
from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_minimum_charge(
    category,
    tariff,
    energy_charge,
    fixed_charge,
    is_faulty=False
):
    """
    BR-04: Apply the category minimum charge when
    energy charge + fixed charge is below the minimum.

    No minimum charge adjustment is applied in a FAULTY month.
    """

    energy = money(energy_charge)
    fixed = money(fixed_charge)

    if energy < ZERO or fixed < ZERO:
        raise ValueError("Energy and fixed charges cannot be negative.")

    amount_before_minimum = money(energy + fixed)

    if is_faulty:
        return {
            "amount_before_minimum": amount_before_minimum,
            "minimum_charge": ZERO,
            "minimum_charge_adjustment": ZERO,
            "amount_after_minimum": amount_before_minimum,
        }

    minimum_field = (
        "min_charge_domestic"
        if category == "DOMESTIC"
        else "min_charge_others"
    )

    minimum_charge = money(tariff[minimum_field])

    adjustment = max(
        ZERO,
        money(minimum_charge - amount_before_minimum)
    )

    return {
        "amount_before_minimum": amount_before_minimum,
        "minimum_charge": minimum_charge,
        "minimum_charge_adjustment": adjustment,
        "amount_after_minimum": money(
            amount_before_minimum + adjustment
        ),
    }
