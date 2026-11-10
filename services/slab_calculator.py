
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0")
TWO_PLACES = Decimal("0.01")


def round_units(value):
    """Round slab limits to the nearest whole unit."""
    return int(
        Decimal(value).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


def round_money(value):
    """Round money to two decimal places."""
    return Decimal(value).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def prorate_slabs(slabs, period_days):
    """
    Keep original slab limits for 28-33 day periods.

    For other periods, multiply slab limits by days/30
    and round to the nearest whole unit.
    """

    if period_days <= 0:
        raise ValueError("Billing period must be positive.")

    if not slabs:
        raise ValueError("No tariff slabs supplied.")

    if 28 <= period_days <= 33:
        return [slab.copy() for slab in slabs]

    factor = Decimal(period_days) / Decimal("30")

    adjusted_slabs = []
    previous_upper = 0

    for index, slab in enumerate(slabs):

        adjusted = slab.copy()

        adjusted["from_unit"] = (
            0 if index == 0 else previous_upper + 1
        )

        if slab["to_unit"] is None:
            adjusted["to_unit"] = None

        else:
            adjusted_upper = round_units(
                Decimal(slab["to_unit"]) * factor
            )

            if adjusted_upper <= previous_upper:
                raise ValueError(
                    "Invalid slab limits after proration."
                )

            adjusted["to_unit"] = adjusted_upper
            previous_upper = adjusted_upper

        adjusted_slabs.append(adjusted)

    return adjusted_slabs


def calculate_slab_breakdown(
    units,
    slabs,
    period_days=30
):
    """
    Calculate progressive slab charges.

    Important:
    The first slab 0-50 represents 50 units,
    not 51 units.

    Each subsequent slab capacity is calculated
    using the difference between consecutive upper
    limits.
    """

    units = int(units)

    if units < 0:
        raise ValueError("Consumption cannot be negative.")

    if not slabs:
        raise ValueError("No tariff slabs supplied.")

    adjusted_slabs = prorate_slabs(
        slabs,
        period_days
    )

    remaining_units = units
    previous_upper = 0

    breakdown = []
    total_charge = ZERO

    for slab in adjusted_slabs:

        if remaining_units == 0:
            break

        upper = slab["to_unit"]

        rate = Decimal(
            str(slab["rate_per_unit"])
        )

        if upper is None:
            slab_units = remaining_units

        else:
            # 0-50 means 50 units.
            # 51-100 means another 50 units.
            slab_capacity = upper - previous_upper

            slab_units = min(
                remaining_units,
                slab_capacity
            )

        if slab_units <= 0:
            continue

        amount = round_money(
            Decimal(slab_units) * rate
        )

        breakdown.append({
            "slab_no": slab["slab_no"],
            "units": slab_units,
            "rate_per_unit": rate,
            "amount": amount
        })

        total_charge += amount
        remaining_units -= slab_units

        if upper is not None:
            previous_upper = upper

    if remaining_units > 0:
        raise ValueError(
            "Tariff slabs do not cover the supplied consumption."
        )

    return {
        "units": units,
        "period_days": period_days,
        "slab_breakdown": breakdown,
        "energy_charge": round_money(total_charge)
    }


def calculate_energy_charge(
    units,
    tariff,
    category,
    period_days=30
):
    """Calculate energy charges using the loaded tariff."""

    if category not in tariff["slabs"]:
        raise ValueError(
            f"No slabs for {category} "
            f"in tariff {tariff['tariff_id']}"
        )

    return calculate_slab_breakdown(
        units,
        tariff["slabs"][category],
        period_days
    )
