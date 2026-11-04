from decimal import Decimal, ROUND_HALF_UP

from models.enums import ConsumerCategory, ReadingStatus


MINIMUM_CHARGES = {
    ConsumerCategory.DOMESTIC: Decimal("150"),
    ConsumerCategory.COMMERCIAL: Decimal("500"),
    ConsumerCategory.INDUSTRIAL_LT: Decimal("500"),
    ConsumerCategory.AGRICULTURE: Decimal("500"),
}


def calculate_minimum_bill(
    category: ConsumerCategory,
    energy_charge: Decimal,
    fixed_charge: Decimal,
    reading_status: ReadingStatus = ReadingStatus.NORMAL
) -> Decimal:

    energy_charge = Decimal(str(energy_charge))
    fixed_charge = Decimal(str(fixed_charge))

    if energy_charge < 0 or fixed_charge < 0:
        raise ValueError("Charges cannot be negative.")

    if not isinstance(category, ConsumerCategory):
        category = ConsumerCategory(category)

    if not isinstance(reading_status, ReadingStatus):
        reading_status = ReadingStatus(reading_status)

    subtotal = energy_charge + fixed_charge

    # Minimum charge is not applicable in faulty months.
    if reading_status == ReadingStatus.FAULTY:
        return subtotal.quantize(Decimal("0.01"))

    minimum = MINIMUM_CHARGES[category]

    final_amount = max(subtotal, minimum)

    return final_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )