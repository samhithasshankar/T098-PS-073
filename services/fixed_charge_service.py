
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")

FIXED_CHARGE_FIELDS = {
    "DOMESTIC": "fixed_domestic_per_kw",
    "COMMERCIAL": "fixed_commercial_per_kw",
    "INDUSTRIAL_LT": "fixed_industrial_per_kw",
}


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_fixed_and_demand_charges(consumer, tariff, max_demand_kw=None):
    """
    Calculate the regular fixed charge and any excess-demand charge.

    BR-03:
    - Fixed charge = sanctioned load x category fixed rate.
    - Excess demand applies only when demand is MORE than 110%
      of sanctioned load.
    - Excess demand charge = excess kW x 2 x fixed rate.
    """

    category = consumer["category"]
    sanctioned_load = Decimal(str(consumer["sanctioned_load_kw"]))

    if sanctioned_load < 0:
        raise ValueError("Sanctioned load cannot be negative.")

    if category == "AGRICULTURE":
        return {
            "fixed_charge": ZERO,
            "excess_demand_charge": ZERO,
            "excess_demand_flag": False,
            "excess_demand_kw": Decimal("0.00"),
        }

    field = FIXED_CHARGE_FIELDS.get(category)

    if field is None:
        raise ValueError(f"Unsupported consumer category: {category}")

    fixed_rate = Decimal(str(tariff[field]))

    fixed_charge = money(sanctioned_load * fixed_rate)

    excess_demand_charge = ZERO
    excess_demand_flag = False
    excess_demand_kw = Decimal("0.00")

    if max_demand_kw is not None:
        demand = Decimal(str(max_demand_kw))

        if demand < 0:
            raise ValueError("Maximum demand cannot be negative.")

        threshold = sanctioned_load * Decimal("1.10")

        if demand > threshold:
            excess_demand_kw = demand - sanctioned_load

            excess_demand_charge = money(
                excess_demand_kw * fixed_rate * Decimal("2")
            )

            excess_demand_flag = True

    return {
        "fixed_charge": fixed_charge,
        "excess_demand_charge": excess_demand_charge,
        "excess_demand_flag": excess_demand_flag,
        "excess_demand_kw": money(excess_demand_kw),
    }
