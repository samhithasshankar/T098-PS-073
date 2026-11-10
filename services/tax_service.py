
from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_fac_and_duty(
    category,
    tariff,
    units_billed,
    energy_charge,
    fixed_charge
):
    """
    BR-06:
    FAC = tariff FAC rate x billed units.

    Electricity duty:
    Domestic uses duty_pct_domestic.
    All other categories use duty_pct_others.

    Duty is calculated on:
    energy charge + fixed charge + FAC.
    """

    billed_units = Decimal(str(units_billed))
    energy = money(energy_charge)
    fixed = money(fixed_charge)

    if billed_units < ZERO:
        raise ValueError("Billed units cannot be negative.")

    if energy < ZERO or fixed < ZERO:
        raise ValueError("Energy and fixed charges cannot be negative.")

    fac_rate = Decimal(str(tariff["fac_per_unit"]))

    fac = money(billed_units * fac_rate)

    duty_field = (
        "duty_pct_domestic"
        if category == "DOMESTIC"
        else "duty_pct_others"
    )

    duty_percentage = (
        Decimal(str(tariff[duty_field])) / Decimal("100")
    )

    duty_base = money(energy + fixed + fac)
    duty = money(duty_base * duty_percentage)

    return {
        "fac": fac,
        "duty_base": duty_base,
        "duty": duty,
    }
