
"""Arrears ageing report calculations for PS-073."""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")


def to_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def money(value):
    return Decimal(str(value or 0)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def generate_arrears_ageing(debts_by_consumer, as_of_date):
    """
    Generate one ageing row per consumer.

    Age is calculated inclusively from the bill due date.
    Outstanding amount = principal + accrued interest.
    """

    as_of_date = to_date(as_of_date)
    report = []

    for consumer_id in sorted(debts_by_consumer):
        buckets = {
            "bucket_0_30": ZERO,
            "bucket_31_60": ZERO,
            "bucket_61_90": ZERO,
            "bucket_over_90": ZERO,
        }

        for debt in debts_by_consumer[consumer_id]:
            due_date = to_date(debt["due_date"])

            if due_date > as_of_date:
                continue

            outstanding = money(
                money(debt.get("principal", 0))
                + money(debt.get("interest", 0))
            )

            if outstanding <= ZERO:
                continue

            # The due date is counted as day 1.
            overdue_days = (as_of_date - due_date).days + 1

            if overdue_days <= 30:
                bucket = "bucket_0_30"
            elif overdue_days <= 60:
                bucket = "bucket_31_60"
            elif overdue_days <= 90:
                bucket = "bucket_61_90"
            else:
                bucket = "bucket_over_90"

            buckets[bucket] += outstanding

        buckets = {
            key: money(value)
            for key, value in buckets.items()
        }

        total = money(sum(buckets.values(), ZERO))

        report.append({
            "as_of_date": as_of_date.isoformat(),
            "consumer_id": consumer_id,
            **buckets,
            "total": total,
        })

    return report
