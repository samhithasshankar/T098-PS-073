
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from services.reading_service import (
    calculate_normal_consumption,
    calculate_estimated_consumption,
    calculate_faulty_consumption,
    calculate_meter_change_consumption,
)


ZERO = Decimal("0")
WHOLE_UNIT = Decimal("1")


def parse_timestamp(value):
    return datetime.strptime(
        value.strip(),
        "%Y-%m-%d %H:%M:%S"
    )


def optional_decimal(value):
    if value is None or str(value).strip() == "":
        return None

    return Decimal(str(value).strip())


def round_units(value):
    return int(
        Decimal(value).quantize(
            WHOLE_UNIT,
            rounding=ROUND_HALF_UP
        )
    )


def split_long_period(
    period_from,
    period_to,
    consumption
):
    """
    BR-01: Split a period longer than 45 days
    into a 30-day bill and the remaining bill.

    Consumption is apportioned by days.
    Any rounding remainder is assigned to the
    second period so total units are preserved.
    """

    total_days = (period_to.date() - period_from.date()).days

    if total_days <= 45:
        return [{
            "period_from": period_from,
            "period_to": period_to,
            "days": total_days,
            "units": int(consumption),
            "bill_date": period_to.date(),
        }]

    first_end = period_from + timedelta(days=30)

    first_units = round_units(
        Decimal(consumption)
        * Decimal("30")
        / Decimal(total_days)
    )

    second_units = int(consumption) - first_units

    return [
        {
            "period_from": period_from,
            "period_to": first_end,
            "days": 30,
            "units": first_units,
            "bill_date": first_end.date(),
        },
        {
            "period_from": first_end,
            "period_to": period_to,
            "days": total_days - 30,
            "units": second_units,
            "bill_date": period_to.date(),
        },
    ]


def process_consumer_readings(readings):
    """
    Process one consumer's readings chronologically.

    The first reading is an opening register reading,
    not a bill.

    Cumulative registers are retained across ESTIMATED
    and FAULTY records so the next NORMAL reading can
    capture actual consumption across that interval.
    """

    if not readings:
        return []

    ordered = sorted(
        readings,
        key=lambda row: parse_timestamp(row["reading_ts"])
    )

    results = []

    previous_timestamp = None
    last_import_register = None
    last_export_register = None

    normal_history = []
    pending_faulty = []

    for row in ordered:
        timestamp = parse_timestamp(row["reading_ts"])
        status = row["status"].strip().upper()

        current_import = optional_decimal(
            row.get("kwh_import")
        )

        current_export = optional_decimal(
            row.get("kwh_export")
        )

        # The first record establishes opening registers.
        if previous_timestamp is None:
            previous_timestamp = timestamp

            if current_import is not None:
                last_import_register = current_import

            if current_export is not None:
                last_export_register = current_export

            continue

        period_days = (
            timestamp.date() - previous_timestamp.date()
        ).days

        if period_days <= 0:
            raise ValueError(
                f"Invalid reading date for {row['reading_id']}: "
                "reading dates must increase."
            )

        consumption = ZERO
        export_units = ZERO
        is_faulty = False
        is_estimated = False
        reconciliation_required = False
        reconciliation_actual_units = None

        if status == "NORMAL":
            if current_import is None:
                raise ValueError(
                    f"NORMAL reading {row['reading_id']} "
                    "has no import register."
                )

            if last_import_register is None:
                raise ValueError(
                    f"No previous import register for "
                    f"{row['reading_id']}."
                )

            consumption = calculate_normal_consumption(
                last_import_register,
                current_import
            )

            # Export is also a cumulative register for NET meters.
            if current_export is not None:
                if last_export_register is None:
                    raise ValueError(
                        f"No previous export register for "
                        f"{row['reading_id']}."
                    )

                export_units = (
                    current_export - last_export_register
                )

                if export_units < ZERO:
                    raise ValueError(
                        f"Export register decreased for "
                        f"{row['reading_id']}."
                    )

                last_export_register = current_export

            last_import_register = current_import

            if pending_faulty:
                reconciliation_required = True
                reconciliation_actual_units = consumption

                pending_faulty = []

            normal_history.append(consumption)

        elif status == "ESTIMATED":
            consumption = calculate_estimated_consumption(
                normal_history
            )

            is_estimated = True

        elif status == "FAULTY":
            consumption = calculate_faulty_consumption(
                normal_history
            )

            is_faulty = True

            pending_faulty.append({
                "reading_id": row["reading_id"],
                "estimated_units": consumption,
                "period_days": period_days,
                "period_from": previous_timestamp,
                "period_to": timestamp,
            })

        elif status == "METER_CHANGE":
            if (
                last_import_register is None
                or current_import is None
            ):
                raise ValueError(
                    f"Missing import register for "
                    f"meter change {row['reading_id']}."
                )

            consumption = calculate_meter_change_consumption(
                previous_reading=last_import_register,
                old_meter_final=row.get("old_meter_final"),
                new_meter_initial=row.get("new_meter_initial"),
                new_meter_reading=current_import,
            )

            last_import_register = current_import

        else:
            raise ValueError(
                f"Unsupported reading status {status} "
                f"for {row['reading_id']}."
            )

        if consumption < ZERO:
            raise ValueError(
                f"Negative consumption for {row['reading_id']}."
            )

        # Keep the original interval separate from split bill periods.
        segments = split_long_period(
            previous_timestamp,
            timestamp,
            consumption
        )

        flags = []

        if is_estimated:
            flags.append("ESTIMATED")

        if is_faulty:
            flags.append("FAULTY_AVERAGE")

        if len(segments) > 1:
            flags.append("SPLIT_BILL")

        if reconciliation_required:
            flags.append("RECONCILIATION_PENDING")

        result = {
            "reading_id": row["reading_id"],
            "consumer_id": row["consumer_id"],
            "status": status,
            "reading_ts": timestamp,
            "period_from": previous_timestamp,
            "period_to": timestamp,
            "period_days": period_days,
            "consumption_units": int(consumption),
            "export_units": int(export_units),
            "tod_peak_kwh": optional_decimal(
                row.get("tod_peak_kwh")
            ),
            "tod_offpeak_kwh": optional_decimal(
                row.get("tod_offpeak_kwh")
            ),
            "tod_normal_kwh": optional_decimal(
                row.get("tod_normal_kwh")
            ),
            "max_demand_kw": optional_decimal(
                row.get("max_demand_kw")
            ),
            "is_estimated": is_estimated,
            "is_faulty": is_faulty,
            "reconciliation_required": reconciliation_required,
            "reconciliation_actual_units": (
                int(reconciliation_actual_units)
                if reconciliation_actual_units is not None
                else None
            ),
            "pending_faulty_periods": list(pending_faulty),
            "segments": segments,
            "flags": flags,
        }

        results.append(result)
        previous_timestamp = timestamp

    return results


def process_all_readings(readings):
    """
    Process all consumers' readings.

    Returns a list of billable reading-period records
    sorted by bill date and consumer ID.
    """

    grouped = {}

    for row in readings:
        consumer_id = row["consumer_id"]

        grouped.setdefault(
            consumer_id,
            []
        ).append(row)

    all_results = []

    for consumer_id, consumer_readings in grouped.items():
        all_results.extend(
            process_consumer_readings(consumer_readings)
        )

    all_results.sort(
        key=lambda item: (
            item["reading_ts"],
            item["consumer_id"]
        )
    )

    return all_results
