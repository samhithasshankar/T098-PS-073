from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from models.enums import ConsumerCategory


@dataclass
class FixedChargeBreakdown:
    base_charge: Decimal
    excess_load_penalty: Decimal
    total_charge: Decimal
    load_regularisation_required: bool


FIXED_RATES = {
    ConsumerCategory.DOMESTIC: Decimal("75"),
    ConsumerCategory.COMMERCIAL: Decimal("150"),
    ConsumerCategory.INDUSTRIAL_LT: Decimal("250"),
    ConsumerCategory.AGRICULTURE: Decimal("0"),
}


def money(value: Decimal) -> Decimal:
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def calculate_fixed_charge(
    category: ConsumerCategory,
    sanctioned_load_kw: Decimal,
    max_demand_kw: Decimal = Decimal("0"),
    is_bpl: bool = False,
    consumption: Decimal = Decimal("0")
) -> FixedChargeBreakdown:

    sanctioned_load_kw = Decimal(str(sanctioned_load_kw))
    max_demand_kw = Decimal(str(max_demand_kw))
    consumption = Decimal(str(consumption))

    if sanctioned_load_kw <= 0:
        raise ValueError("Sanctioned load must be positive.")

    if max_demand_kw < 0 or consumption < 0:
        raise ValueError("Demand and consumption cannot be negative.")

    if not isinstance(category, ConsumerCategory):
        category = ConsumerCategory(category)

    rate = FIXED_RATES[category]

    # BPL consumers using 100 units or less
    # receive a fixed-charge exemption.
    if is_bpl and consumption <= Decimal("100"):
        return FixedChargeBreakdown(
            base_charge=Decimal("0.00"),
            excess_load_penalty=Decimal("0.00"),
            total_charge=Decimal("0.00"),
            load_regularisation_required=False
        )

    base_charge = sanctioned_load_kw * rate

    # Penalty only when demand exceeds sanctioned load by
    # MORE THAN 10%, not exactly 10%.
    threshold = sanctioned_load_kw * Decimal("1.10")

    excess_penalty = Decimal("0")
    regularisation_required = False

    if max_demand_kw > threshold:
        excess_kw = max_demand_kw - sanctioned_load_kw

        excess_penalty = (
            excess_kw * rate * Decimal("2")
        )

        regularisation_required = True

    base_charge = money(base_charge)
    excess_penalty = money(excess_penalty)

    return FixedChargeBreakdown(
        base_charge=base_charge,
        excess_load_penalty=excess_penalty,
        total_charge=money(base_charge + excess_penalty),
        load_regularisation_required=regularisation_required
    )