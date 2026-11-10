
from decimal import Decimal

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.minimum_charge_service import calculate_minimum_charge


def get_tariffs():
    data = load_all_data()
    return build_tariff_catalog(data)


def test_domestic_minimum_charge():
    tariff = get_tariffs()["TO-2025"]

    result = calculate_minimum_charge(
        "DOMESTIC", tariff, Decimal("0.00"), Decimal("0.00")
    )

    assert result["minimum_charge"] == Decimal("150.00")
    assert result["minimum_charge_adjustment"] == Decimal("150.00")
    assert result["amount_after_minimum"] == Decimal("150.00")


def test_other_category_minimum_charge():
    tariff = get_tariffs()["TO-2025"]

    result = calculate_minimum_charge(
        "COMMERCIAL", tariff, Decimal("0.00"), Decimal("0.00")
    )

    assert result["minimum_charge"] == Decimal("500.00")
    assert result["minimum_charge_adjustment"] == Decimal("500.00")


def test_no_adjustment_when_amount_exceeds_minimum():
    tariff = get_tariffs()["TO-2025"]

    result = calculate_minimum_charge(
        "DOMESTIC", tariff, Decimal("100.00"), Decimal("75.00")
    )

    assert result["minimum_charge_adjustment"] == Decimal("0.00")
    assert result["amount_after_minimum"] == Decimal("175.00")


def test_faulty_month_has_no_minimum_charge():
    tariff = get_tariffs()["TO-2025"]

    result = calculate_minimum_charge(
        "DOMESTIC",
        tariff,
        Decimal("0.00"),
        Decimal("0.00"),
        is_faulty=True
    )

    assert result["minimum_charge_adjustment"] == Decimal("0.00")
    assert result["amount_after_minimum"] == Decimal("0.00")


def test_to_2026_minimum_charge():
    tariff = get_tariffs()["TO-2026"]

    result = calculate_minimum_charge(
        "DOMESTIC", tariff, Decimal("0.00"), Decimal("0.00")
    )

    assert result["minimum_charge"] == Decimal("150.00")
