
"""Application orchestration for the PS-073 command file."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from commands.command_processor import parse_command_file
from reports.csv_report_service import write_all_reports
from services.arrears_ageing_service import generate_arrears_ageing
from services.billing_engine import calculate_consumer_bills
from services.disconnection_service import (
    evaluate_disconnection,
    evaluate_reconnection,
)
from services.payment_processing_service import process_payments
from services.tariff_service import build_tariff_catalog

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _timestamp(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    return datetime.fromisoformat(str(value).strip())


def _money(value):
    return Decimal(str(value or 0)).quantize(
        CENT, rounding=ROUND_HALF_UP
    )


def _prepare_bills(data):
    """Calculate bills and their slab rows for every consumer."""
    tariff_catalog = build_tariff_catalog(data)
    readings_by_consumer = defaultdict(list)

    for reading in data["readings"]:
        readings_by_consumer[reading["consumer_id"]].append(reading)

    all_bills = []

    for consumer in data["consumers"]:
        all_bills.extend(
            calculate_consumer_bills(
                consumer=consumer,
                readings=readings_by_consumer[
                    consumer["consumer_id"]
                ],
                tariff_catalog=tariff_catalog,
            )
        )

    all_bills.sort(
        key=lambda row: (
            _date(row["bill_date"]),
            row["consumer_id"],
        )
    )

    counts = defaultdict(int)
    slab_rows = []

    for bill in all_bills:
        bill_date = _date(bill["bill_date"])
        key = (bill["consumer_id"], bill_date)
        counts[key] += 1
        suffix = counts[key]

        bill["bill_id"] = (
            f"BL-{bill['consumer_id']}-{bill_date:%Y%m%d}"
            if suffix == 1
            else (
                f"BL-{bill['consumer_id']}-"
                f"{bill_date:%Y%m%d}-{suffix}"
            )
        )

        bill["bill_date"] = bill_date
        bill["due_date"] = bill_date + timedelta(days=15)
        bill["tariff_ids"] = (
            bill.get("tariff_ids")
            or bill.get("tariff_id", "")
        )
        bill["arrears"] = ZERO
        bill["interest"] = ZERO
        bill["total_due"] = _money(
            bill.get("net_current", 0)
        )

        for slab in bill.get("slab_breakdown", []):
            slab_rows.append({
                "bill_id": bill["bill_id"],
                "tariff_id": slab.get(
                    "tariff_id",
                    bill.get("tariff_id", ""),
                ),
                "slab_no": slab["slab_no"],
                "units": slab["units"],
                "rate_per_unit": slab["rate_per_unit"],
                "amount": slab["amount"],
            })

    return all_bills, slab_rows


def _payment_snapshot(bills, payments, cutoff):
    """Return payment/debt state using only events through cutoff."""
    cutoff = _timestamp(cutoff)

    eligible_bills = [
        bill
        for bill in bills
        if datetime.combine(
            _date(bill["bill_date"]), time.min
        ) <= cutoff
    ]

    eligible_payments = [
        payment
        for payment in payments
        if _timestamp(payment["payment_ts"]) <= cutoff
    ]

    return process_payments(
        eligible_bills,
        eligible_payments,
        as_of_date=cutoff.date(),
    )


def _outstanding(debts):
    return sum(
        (
            _money(debt.get("principal", 0))
            + _money(debt.get("interest", 0))
            for debt in debts
        ),
        ZERO,
    )


def _consecutive_unpaid(debts):
    count = 0

    for debt in reversed(debts):
        if _money(debt.get("principal", 0)) > ZERO:
            count += 1
        else:
            break

    return count


def _build_state_events(data, bills, commands):
    """Evaluate connection state at each command timestamp."""
    consumers = {
        row["consumer_id"]: row
        for row in data["consumers"]
    }

    states = {
        consumer_id: "CONNECTED"
        for consumer_id in consumers
    }

    notice_dates = {}
    disconnected_dates = {}
    state_rows = []
    reconnect_results = {}

    for command in commands:
        execution_time = _timestamp(
            command["execution_timestamp"]
        )

        snapshot = _payment_snapshot(
            bills,
            data["payments"],
            execution_time,
        )

        for consumer_id, consumer in consumers.items():

            # Do not issue another notice or disconnection
            # event for a consumer already disconnected.
            if states[consumer_id] == "DISCONNECTED":
                continue

            debts = snapshot["debts"].get(consumer_id, [])
            arrears = _outstanding(debts)

            evaluation = evaluate_disconnection(
                category=consumer["category"],
                consecutive_unpaid_bills=_consecutive_unpaid(
                    debts
                ),
                total_arrears=arrears,
                as_of_date=execution_time.date(),
                notice_date=notice_dates.get(consumer_id),
            )

            new_state = evaluation["state"]

            if new_state != states[consumer_id]:
                state_rows.append({
                    "consumer_id": consumer_id,
                    "event_date": execution_time.date(),
                    "state": new_state,
                    "reason": evaluation["reason"],
                })

                states[consumer_id] = new_state

                if new_state == "DISCONNECTION_NOTICE":
                    notice_dates[consumer_id] = (
                        evaluation["notice_date"]
                    )

                elif new_state == "DISCONNECTED":
                    disconnected_dates[consumer_id] = (
                        execution_time.date()
                    )

                elif new_state == "CONNECTED":
                    notice_dates.pop(consumer_id, None)
                    disconnected_dates.pop(consumer_id, None)

        if command["command"] == "RECONNECT":
            consumer_id = command["arguments"][0]
            consumer = consumers[consumer_id]
            debts = snapshot["debts"].get(consumer_id, [])
            arrears = _outstanding(debts)

            prior_bills = [
                bill
                for bill in bills
                if bill["consumer_id"] == consumer_id
                and _date(bill["bill_date"])
                <= execution_time.date()
            ]

            average_bill = (
                sum(
                    (
                        _money(bill.get("net_current", 0))
                        for bill in prior_bills
                    ),
                    ZERO,
                ) / Decimal(len(prior_bills))
                if prior_bills
                else ZERO
            )

            disconnected_on = disconnected_dates.get(
                consumer_id
            )

            payments_after_disconnect = [
                payment
                for payment in data["payments"]
                if payment["consumer_id"] == consumer_id
                and _timestamp(payment["payment_ts"])
                <= execution_time
                and disconnected_on is not None
                and _timestamp(
                    payment["payment_ts"]
                ).date() >= disconnected_on
            ]

            amount_paid = sum(
                (
                    _money(payment["amount"])
                    for payment in payments_after_disconnect
                ),
                ZERO,
            )

            if states[consumer_id] != "DISCONNECTED":
                reconnect_results[consumer_id] = {
                    "state": "REFUSED",
                    "reason": (
                        "Consumer is not in DISCONNECTED state."
                    ),
                }

            else:
                result = evaluate_reconnection(
                    amount_paid=amount_paid,
                    total_arrears=arrears,
                    security_deposit=consumer.get(
                        "security_deposit", 0
                    ),
                    average_monthly_bill=average_bill,
                )

                if result["state"] == "RECONNECTED":
                    states[consumer_id] = "RECONNECTED"

                    state_rows.append({
                        "consumer_id": consumer_id,
                        "event_date": execution_time.date(),
                        "state": "RECONNECTED",
                        "reason": (
                            "Required arrears, reconnection fee "
                            "and deposit top-up paid."
                        ),
                    })

                if amount_paid <= ZERO:
                    result = {
                        "state": "REFUSED",
                        "reason": (
                            "No qualifying payment was recorded "
                            "before the reconnect request."
                        ),
                        "required_amount": result[
                            "required_amount"
                        ],
                        "amount_paid": result["amount_paid"],
                        "shortfall": result["shortfall"],
                    }

                reconnect_results[consumer_id] = result

    state_rows.sort(
        key=lambda row: (
            row["event_date"],
            row["consumer_id"],
        )
    )

    return state_rows, reconnect_results


def execute_project(data, command_file=None, output_dir=None):
    """Execute commands and write the five required reports."""

    if command_file:
        commands = parse_command_file(command_file)
    else:
        from utils.data_loader import DATA_DIR
        commands = parse_command_file(
            DATA_DIR / "commands.txt"
        )

    bills, slab_rows = _prepare_bills(data)
    payments = data["payments"]

    printed_ageing = []
    printed_ledger = []
    command_results = []

    for command in commands:
        name = command["command"]
        args = command["arguments"]

        execution_time = _timestamp(
            command["execution_timestamp"]
        )

        if name == "PRINT_ARREARS_AGEING":
            as_of = _date(args[0])
            cutoff = datetime.combine(as_of, time.max)

            snapshot = _payment_snapshot(
                bills,
                payments,
                cutoff,
            )

            rows = generate_arrears_ageing(
                snapshot["debts"],
                as_of,
            )

            printed_ageing.extend(rows)

            command_results.append({
                "command": name,
                "count": len(rows),
            })

        elif name == "PRINT_BILL":
            consumer_id, month = args

            matches = [
                bill
                for bill in bills
                if bill["consumer_id"] == consumer_id
                and _date(
                    bill["bill_date"]
                ).strftime("%Y-%m") == month
                and _date(
                    bill["bill_date"]
                ) <= execution_time.date()
            ]

            command_results.append({
                "command": name,
                "count": len(matches),
            })

        elif name == "PRINT_LEDGER":
            consumer_id, report_date = args
            cutoff_date = _date(report_date)

            cutoff = min(
                datetime.combine(cutoff_date, time.max),
                execution_time,
            )

            snapshot = _payment_snapshot(
                bills,
                payments,
                cutoff,
            )

            rows = [
                row
                for row in snapshot["ledger"]
                if row["consumer_id"] == consumer_id
                and _timestamp(row["entry_ts"]) <= cutoff
            ]

            printed_ledger.extend(rows)

            command_results.append({
                "command": name,
                "count": len(rows),
            })

        elif name == "RECONNECT":
            command_results.append({
                "command": name,
                "consumer_id": args[0],
            })

    state_rows, reconnect_results = _build_state_events(
        data,
        bills,
        commands,
    )

    for result in command_results:
        if result["command"] == "RECONNECT":
            reconnect = reconnect_results.get(
                result["consumer_id"],
                {
                    "state": "REFUSED",
                    "reason": (
                        "Reconnection conditions were not met."
                    ),
                },
            )

            result.update(reconnect)

    final_cutoff = max(
        (
            _timestamp(command["execution_timestamp"])
            for command in commands
        ),
        default=datetime.max,
    )

    final_snapshot = _payment_snapshot(
        bills,
        payments,
        final_cutoff,
    )

    debt_lookup = {
        debt["bill_id"]: debt
        for debts in final_snapshot["debts"].values()
        for debt in debts
    }

    for bill in bills:
        debt = debt_lookup.get(bill["bill_id"])

        if debt:
            bill["arrears"] = _money(
                debt.get("principal", 0)
            )

            bill["interest"] = _money(
                debt.get("interest", 0)
            )

            bill["total_due"] = _money(
                debt.get("principal", 0)
                + debt.get("interest", 0)
            )

    reports = {
        "bills.csv": bills,
        "bill_slabs.csv": slab_rows,
        "ledger.csv": printed_ledger,
        "consumer_state.csv": state_rows,
        "arrears_ageing.csv": printed_ageing,
    }

    written = write_all_reports(
        reports,
        output_dir=output_dir,
    )

    return {
        "commands_executed": len(commands),
        "command_results": command_results,
        "bills_calculated": len(bills),
        "reports": written,
        "ledger_entries": len(printed_ledger),
    }
