
from decimal import Decimal, ROUND_HALF_UP

from services.slab_calculator import calculate_energy_charge


TWO_PLACES = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_faulty_reconciliation(
    category,
    estimated_months,
    actual_months
):
    """
    Recalculate estimated versus actual energy charges
    separately for every affected billing month.

    Each month must contain:
    {
        "units": consumption units,
        "tariff": applicable tariff dictionary,
        "period_days": billing period days
    }

    A negative reconciliation adjustment is a credit.
    """

    if not estimated_months or not actual_months:
        raise ValueError("Both estimated and actual months are required.")

    if len(estimated_months) != len(actual_months):
        raise ValueError(
            "Estimated and actual month counts must match."
        )

    estimated_total = Decimal("0.00")
    actual_total = Decimal("0.00")
    monthly_details = []

    for index, (estimated, actual) in enumerate(
        zip(estimated_months, actual_months),
        start=1
    ):
        estimated_result = calculate_energy_charge(
            estimated["units"],
            estimated["tariff"],
            category,
            estimated["period_days"]
        )

        actual_result = calculate_energy_charge(
            actual["units"],
            actual["tariff"],
            category,
            actual["period_days"]
        )

        estimated_charge = money(
            estimated_result["energy_charge"]
        )

        actual_charge = money(
            actual_result["energy_charge"]
        )

        difference = money(
            actual_charge - estimated_charge
        )

        estimated_total += estimated_charge
        actual_total += actual_charge

        monthly_details.append({
            "month_number": index,
            "estimated_units": estimated["units"],
            "actual_units": actual["units"],
            "estimated_energy_charge": estimated_charge,
            "actual_energy_charge": actual_charge,
            "reconciliation_adjustment": difference,
        })

    adjustment = money(actual_total - estimated_total)

    return {
        "estimated_total": money(estimated_total),
        "actual_total": money(actual_total),
        "reconciliation_adjustment": adjustment,
        "monthly_details": monthly_details,
    }
