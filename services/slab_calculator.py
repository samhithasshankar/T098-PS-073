from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from models.tariff import Slab


@dataclass
class SlabBreakdown:
    units: Decimal
    rate: Decimal
    amount: Decimal


def prorate_slab_limits(slabs: list[Slab], days: int) -> list[Slab]:
    """
    Adjust slab limits when the billing period is outside
    the standard 28-33 day range.

    Formula:
        Adjusted limit = Original limit * days / 30
    """

    if days <= 0:
        raise ValueError("Billing days must be positive.")

    if 28 <= days <= 33:
        return slabs

    adjusted_slabs = []

    for slab in slabs:
        if slab.upper_limit is None:
            adjusted_slabs.append(Slab(None, slab.rate))
        else:
            adjusted_limit = (
                slab.upper_limit * Decimal(days) / Decimal("30")
            ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

            adjusted_slabs.append(
                Slab(adjusted_limit, slab.rate)
            )

    return adjusted_slabs


def calculate_slab_breakdown(
    consumption: Decimal,
    slabs: list[Slab],
    days: int = 30
) -> list[SlabBreakdown]:

    consumption = Decimal(str(consumption))

    if consumption < 0:
        raise ValueError("Consumption cannot be negative.")

    if not slabs:
        raise ValueError("At least one slab is required.")

    adjusted_slabs = prorate_slab_limits(slabs, days)

    previous_limit = Decimal("0")
    remaining_units = consumption
    breakdown = []

    for slab in adjusted_slabs:

        if remaining_units <= 0:
            break

        if slab.upper_limit is None:
            available_units = remaining_units
        else:
            available_units = (
                slab.upper_limit - previous_limit
            )

            if available_units <= 0:
                raise ValueError("Invalid slab limits.")

        units_in_slab = min(
            remaining_units,
            available_units
        )

        amount = units_in_slab * slab.rate

        breakdown.append(
            SlabBreakdown(
                units=units_in_slab,
                rate=slab.rate,
                amount=amount
            )
        )

        remaining_units -= units_in_slab

        if slab.upper_limit is not None:
            previous_limit = slab.upper_limit

    if remaining_units > 0:
        raise ValueError(
            "Tariff slabs do not cover the complete consumption."
        )

    return breakdown


def calculate_energy_charge(
    consumption: Decimal,
    slabs: list[Slab],
    days: int = 30
) -> Decimal:

    breakdown = calculate_slab_breakdown(
        consumption,
        slabs,
        days
    )

    total = sum(
        (item.amount for item in breakdown),
        Decimal("0")
    )

    return total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )