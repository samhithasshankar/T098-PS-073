
from datetime import date, datetime, time
from decimal import Decimal, ROUND_HALF_UP

from services.arrears_service import (
    allocate_payment,
    calculate_due_date,
    calculate_total_arrears,
    accrue_interest,
)


ZERO = Decimal("0.00")
MONEY_PLACES = Decimal("0.01")


def to_decimal(value):
    """Convert a value safely into Decimal."""
    return Decimal(str(value or 0))


def round_money(value):
    """Round money to two decimal places."""
    return to_decimal(value).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP
    )


def to_date(value):
    """Convert a date, datetime or ISO date string into date."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(str(value)[:10])


def to_datetime(value):
    """Convert a date, datetime or timestamp string into datetime."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    value = str(value).strip()

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d")


def format_money(value):
    """Return a two-decimal-place money string."""
    return str(round_money(value))


def get_bill_amount(bill):
    """
    Obtain the current bill principal.

    net_current is used because total_due may also contain
    previous arrears and interest.
    """
    if "net_current" in bill:
        amount = to_decimal(bill["net_current"])
    elif "bill_amount" in bill:
        amount = to_decimal(bill["bill_amount"])
    else:
        raise ValueError(
            f"Bill {bill.get('bill_id')} has no net_current amount."
        )

    if amount < 0:
        raise ValueError("Bill amount cannot be negative.")

    return round_money(amount)


def add_ledger_entry(
    ledger,
    balances,
    consumer_id,
    entry_ts,
    entry_type,
    reference,
    debit=ZERO,
    credit=ZERO
):
    """Add a transaction and update the consumer's running balance."""
    debit = round_money(debit)
    credit = round_money(credit)

    if debit < 0 or credit < 0:
        raise ValueError("Ledger debit and credit cannot be negative.")

    if debit > 0 and credit > 0:
        raise ValueError(
            "A ledger entry cannot contain both debit and credit."
        )

    balance = round_money(
        balances.get(consumer_id, ZERO) + debit - credit
    )

    balances[consumer_id] = balance

    ledger.append({
        "consumer_id": consumer_id,
        "entry_ts": entry_ts.isoformat(sep=" "),
        "entry_type": entry_type,
        "reference": reference,
        "debit": format_money(debit),
        "credit": format_money(credit),
        "balance": format_money(balance)
    })


def process_payments(
    bills,
    payments,
    as_of_date=None
):
    """
    Process bills and payments chronologically.

    Bill requirements:
        bill_id
        consumer_id
        bill_date
        net_current

    Optional bill field:
        due_date

    Payment requirements:
        payment_id
        consumer_id
        payment_ts
        amount
        mode

    Processing rules:
        1. Bills are added on their bill dates.
        2. Interest is accrued after the due date.
        3. Interest is calculated on outstanding principal only.
        4. Payments clear interest before principal.
        5. Oldest outstanding bills are paid first.
        6. Excess payments remain as consumer credit.
        7. All ledger entries are maintained chronologically.

    Returns:
        debts
        ledger
        balances
        unapplied_credits
        payment_results
    """

    events = []

    # Prepare bill events.
    for bill in bills:
        required_fields = [
            "bill_id",
            "consumer_id",
            "bill_date"
        ]

        for field in required_fields:
            if field not in bill:
                raise ValueError(
                    f"Bill is missing required field: {field}"
                )

        bill_date = to_date(bill["bill_date"])

        due_date = (
            to_date(bill["due_date"])
            if bill.get("due_date")
            else calculate_due_date(bill_date)
        )

        amount = get_bill_amount(bill)

        events.append({
            "event_type": "BILL",
            "event_ts": datetime.combine(bill_date, time.min),
            "bill": bill,
            "amount": amount,
            "due_date": due_date
        })

    # Prepare payment events.
    for payment in payments:
        required_fields = [
            "payment_id",
            "consumer_id",
            "payment_ts",
            "amount",
            "mode"
        ]

        for field in required_fields:
            if field not in payment:
                raise ValueError(
                    f"Payment is missing required field: {field}"
                )

        payment_ts = to_datetime(payment["payment_ts"])
        amount = round_money(payment["amount"])

        if amount <= 0:
            raise ValueError(
                f"Payment {payment['payment_id']} must be positive."
            )

        mode = str(payment["mode"]).strip().upper()

        if mode not in ("ONLINE", "COUNTER"):
            raise ValueError(
                f"Invalid payment mode for {payment['payment_id']}: {mode}"
            )

        events.append({
            "event_type": "PAYMENT",
            "event_ts": payment_ts,
            "payment": payment,
            "amount": amount
        })

    # Bills are processed before payments when they share a date.
    events.sort(
        key=lambda event: (
            event["event_ts"],
            0 if event["event_type"] == "BILL" else 1,
            (
                event["bill"]["bill_id"]
                if event["event_type"] == "BILL"
                else event["payment"]["payment_id"]
            )
        )
    )

    debts_by_consumer = {}
    ledger = []
    balances = {}
    unapplied_credits = {}
    payment_results = {}

    def accrue_consumer_interest(consumer_id, event_date):
        """Accrue interest and record the additional amount."""
        debts = debts_by_consumer.get(consumer_id, [])

        if not debts:
            return

        before = {
            debt["bill_id"]: to_decimal(
                debt.get("interest", ZERO)
            )
            for debt in debts
        }

        updated = accrue_interest(debts, event_date)

        debts_by_consumer[consumer_id] = updated

        for debt in updated:
            old_interest = before.get(
                debt["bill_id"],
                ZERO
            )

            new_interest = to_decimal(
                debt.get("interest", ZERO)
            )

            additional_interest = round_money(
                new_interest - old_interest
            )

            if additional_interest > 0:
                add_ledger_entry(
                    ledger=ledger,
                    balances=balances,
                    consumer_id=consumer_id,
                    entry_ts=datetime.combine(
                        event_date,
                        time.min
                    ),
                    entry_type="INTEREST",
                    reference=debt["bill_id"],
                    debit=additional_interest
                )

    # Process every event in chronological order.
    for event in events:

        event_type = event["event_type"]
        event_ts = event["event_ts"]

        if event_type == "BILL":

            bill = event["bill"]
            consumer_id = bill["consumer_id"]
            amount = event["amount"]

            debt = {
                "bill_id": bill["bill_id"],
                "due_date": event["due_date"],
                "principal": amount,
                "interest": ZERO,
                "last_interest_date": event["due_date"]
            }

            debts_by_consumer.setdefault(
                consumer_id,
                []
            ).append(debt)

            # Record the complete bill debit.
            add_ledger_entry(
                ledger=ledger,
                balances=balances,
                consumer_id=consumer_id,
                entry_ts=event_ts,
                entry_type="BILL",
                reference=bill["bill_id"],
                debit=amount
            )

            # Use any earlier excess payment as consumer credit.
            available_credit = unapplied_credits.get(
                consumer_id,
                ZERO
            )

            if available_credit > 0:
                result = allocate_payment(
                    debts_by_consumer[consumer_id],
                    available_credit,
                    event_ts.date()
                )

                debts_by_consumer[consumer_id] = result["debts"]

                unapplied_credits[consumer_id] = (
                    result["unapplied_amount"]
                )

        else:

            payment = event["payment"]
            consumer_id = payment["consumer_id"]
            payment_id = payment["payment_id"]
            payment_amount = event["amount"]
            payment_date = event_ts.date()

            debts = debts_by_consumer.get(
                consumer_id,
                []
            )

            # Record any interest accrued up to this payment date.
            accrue_consumer_interest(
                consumer_id,
                payment_date
            )

            # Apply the payment to interest and then principal.
            result = allocate_payment(
                debts_by_consumer.get(consumer_id, []),
                payment_amount,
                payment_date
            )

            debts_by_consumer[consumer_id] = result["debts"]

            # Carry forward any amount not needed to clear debts.
            old_credit = unapplied_credits.get(
                consumer_id,
                ZERO
            )

            unapplied_credits[consumer_id] = round_money(
                old_credit + result["unapplied_amount"]
            )

            # Record the full amount actually received.
            add_ledger_entry(
                ledger=ledger,
                balances=balances,
                consumer_id=consumer_id,
                entry_ts=event_ts,
                entry_type="PAYMENT",
                reference=payment_id,
                credit=payment_amount
            )

            payment_results[payment_id] = {
                "consumer_id": consumer_id,
                "payment_amount": payment_amount,
                "mode": payment["mode"],
                "allocations": result["allocations"],
                "unapplied_amount": result["unapplied_amount"]
            }

    # Accrue interest up to the requested reporting date.
    if as_of_date is not None:
        reporting_date = to_date(as_of_date)

        for consumer_id in sorted(debts_by_consumer):
            accrue_consumer_interest(
                consumer_id,
                reporting_date
            )

    # Calculate outstanding arrears.
    arrears_by_consumer = {}

    for consumer_id, debts in debts_by_consumer.items():
        arrears_by_consumer[consumer_id] = (
            calculate_total_arrears(debts)
        )

    # Return a consistent ledger order.
    ledger.sort(
        key=lambda row: (
            row["entry_ts"],
            row["consumer_id"],
            row["entry_type"],
            row["reference"]
        )
    )

    return {
        "debts": debts_by_consumer,
        "ledger": ledger,
        "balances": balances,
        "unapplied_credits": unapplied_credits,
        "arrears_by_consumer": arrears_by_consumer,
        "payment_results": payment_results
    }
