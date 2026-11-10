
from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal("0.01")
ZERO = Decimal("0.00")

ELIGIBLE_CATEGORIES = {"COMMERCIAL", "INDUSTRIAL_LT"}


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_tod_adjustment(
    consumer,
    tariff,
    energy_charge,
    tod_peak_kwh,
    tod_offpeak_kwh,
    tod_normal_kwh
):
    """
    BR-05: Calculate Time-of-Day adjustment.

    Peak units receive the tariff peak percentage.
    Off-peak units receive the tariff off-peak percentage.
    Normal units receive no adjustment.

    Only TOD meters in Commercial and Industrial_LT
    categories are eligible.
    """

    zero_result = {
        "tod_adjustment": ZERO,
        "peak_adjustment": ZERO,
        "offpeak_adjustment": ZERO,
        "eligible": False,
    }

    if (
        consumer["meter_type"] != "TOD"
        or consumer["category"] not in ELIGIBLE_CATEGORIES
    ):
        return zero_result

    energy = Decimal(str(energy_charge))
    peak = Decimal(str(tod_peak_kwh))
    offpeak = Decimal(str(tod_offpeak_kwh))
    normal = Decimal(str(tod_normal_kwh))

    if energy < ZERO or min(peak, offpeak, normal) < ZERO:
        raise ValueError("Energy charge and ToD units cannot be negative.")

    total_tod_units = peak + offpeak + normal

    if total_tod_units == ZERO:
        return {
            "tod_adjustment": ZERO,
            "peak_adjustment": ZERO,
            "offpeak_adjustment": ZERO,
            "eligible": True,
        }

    peak_percentage = (
        Decimal(str(tariff["tod_peak_pct"])) / Decimal("100")
    )

    offpeak_percentage = (
        Decimal(str(tariff["tod_offpeak_pct"])) / Decimal("100")
    )

    peak_energy_share = energy * peak / total_tod_units
    offpeak_energy_share = energy * offpeak / total_tod_units

    peak_adjustment = money(
        peak_energy_share * peak_percentage
    )

    offpeak_adjustment = money(
        offpeak_energy_share * offpeak_percentage
    )

    total_adjustment = money(
        peak_adjustment + offpeak_adjustment
    )

    return {
        "tod_adjustment": total_adjustment,
        "peak_adjustment": peak_adjustment,
        "offpeak_adjustment": offpeak_adjustment,
        "eligible": True,
    }
