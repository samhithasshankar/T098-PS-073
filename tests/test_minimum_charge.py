from decimal import Decimal

from models.enums import ConsumerCategory, ReadingStatus
from services.minimum_charge_service import calculate_minimum_bill


def test_domestic_minimum_charge():
    result = calculate_minimum_bill(
        ConsumerCategory.DOMESTIC,
        Decimal("100"),
        Decimal("30")
    )

    assert result == Decimal("150.00")


def test_domestic_above_minimum():
    result = calculate_minimum_bill(
        ConsumerCategory.DOMESTIC,
        Decimal("200"),
        Decimal("75")
    )

    assert result == Decimal("275.00")


def test_commercial_minimum_charge():
    result = calculate_minimum_bill(
        ConsumerCategory.COMMERCIAL,
        Decimal("300"),
        Decimal("100")
    )

    assert result == Decimal("500.00")


def test_industrial_minimum_charge():
    result = calculate_minimum_bill(
        ConsumerCategory.INDUSTRIAL_LT,
        Decimal("200"),
        Decimal("100")
    )

    assert result == Decimal("500.00")


def test_faulty_month_no_minimum():
    result = calculate_minimum_bill(
        ConsumerCategory.DOMESTIC,
        Decimal("100"),
        Decimal("30"),
        ReadingStatus.FAULTY
    )

    assert result == Decimal("130.00")


def test_agriculture_minimum_charge():
    result = calculate_minimum_bill(
        ConsumerCategory.AGRICULTURE,
        Decimal("100"),
        Decimal("0")
    )

    assert result == Decimal("500.00")