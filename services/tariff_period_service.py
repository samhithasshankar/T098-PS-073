
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from services.tariff_service import get_tariff_for_date


def round_units(value):
    """Round units to the nearest whole number."""
    return int(
        Decimal(str(value)).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


def split_period_by_tariff(
    period_from,
    period_to,
    total_units,
    tariff_catalog
):
    """
    Split a billing period when a tariff order becomes effective.

    The period is treated as:
        (period_from, period_to]

    This means the reading date is included in the billing period.
    A tariff effective on the reading date applies to that date.
    """

    # Convert datetime values to date values.
    # This prevents comparisons between datetime and date objects.
    if isinstance(period_from, datetime):
        period_from = period_from.date()

    if isinstance(period_to, datetime):
        period_to = period_to.date()

    if not isinstance(period_from, date):
        raise TypeError("period_from must be a date or datetime")

    if not isinstance(period_to, date):
        raise TypeError("period_to must be a date or datetime")

    if period_to <= period_from:
        raise ValueError("period_to must be after period_from")

    if Decimal(str(total_units)) < 0:
        raise ValueError("total_units cannot be negative")

    total_days = (period_to - period_from).days

    effective_dates = sorted({
        tariff["effective_date"]
        for tariff in tariff_catalog.values()
        if period_from < tariff["effective_date"] <= period_to
    })

    segments = []
    cursor = period_from

    # Split the period at each tariff effective date.
    for effective_date in effective_dates:
        old_segment_end = effective_date - timedelta(days=1)

        if old_segment_end > cursor:
            days = (old_segment_end - cursor).days

            tariff_date = cursor + timedelta(days=1)
            tariff = get_tariff_for_date(
                tariff_catalog,
                tariff_date
            )

            segments.append({
                "period_from": cursor,
                "period_to": old_segment_end,
                "days": days,
                "tariff": tariff,
                "tariff_id": tariff["tariff_id"]
            })

        # The next segment starts from the day before the
        # effective date so that the effective date is included.
        cursor = old_segment_end

    # Add the final segment.
    if period_to > cursor:
        days = (period_to - cursor).days

        tariff_date = cursor + timedelta(days=1)
        tariff = get_tariff_for_date(
            tariff_catalog,
            tariff_date
        )

        segments.append({
            "period_from": cursor,
            "period_to": period_to,
            "days": days,
            "tariff": tariff,
            "tariff_id": tariff["tariff_id"]
        })

    # Allocate consumption according to the number of days.
    allocated_units = 0

    for index, segment in enumerate(segments):
        if index == len(segments) - 1:
            units = int(total_units) - allocated_units
        else:
            units = round_units(
                Decimal(str(total_units))
                * Decimal(segment["days"])
                / Decimal(total_days)
            )

            allocated_units += units

        segment["units"] = units

    # Validate that the split preserves the original period.
    if sum(segment["days"] for segment in segments) != total_days:
        raise ValueError("Tariff period day allocation is incorrect")

    if sum(segment["units"] for segment in segments) != int(total_units):
        raise ValueError("Tariff period unit allocation is incorrect")

    return segments
