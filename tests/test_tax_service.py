
from decimal import Decimal

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.tax_service import calculate_fac_and_duty


def get_tariff(tariff_id="TO-2025"):
    data = load_all_data()
    tariffs = build_tariff_catalog(data)
    return tariffs[tariff_id]


def test_domestic_fac_and_duty():
    tariff = get_tariff()

    result = calculate_fac_and_duty(
        "DOMESTIC",
        tariff,
        100,
        Decimal("500.00"),
        Decimal("75.00")
    )

    assert result["fac"] == Decimal("35.00")
    assert result["duty_base"] == Decimal("610.00")
    assert result["duty"] == Decimal("36.60")


def test_commercial_duty_percentage():
    tariff = get_tariff()

    result = calculate_fac_and_duty(
        "COMMERCIAL",
        tariff,
        100,
        Decimal("500.00"),
        Decimal("150.00")
    )

    assert result["fac"] == Decimal("35.00")
    assert result["duty_base"] == Decimal("685.00")
    assert result["duty"] == Decimal("61.65")


def test_to_2026_fac_rate():
    tariff = get_tariff("TO-2026")

    result = calculate_fac_and_duty(
        "DOMESTIC",
        tariff,
        100,
        Decimal("500.00"),
        Decimal("80.00")
    )

    assert result["fac"] == Decimal("40.00")
    assert result["duty_base"] == Decimal("620.00")
    assert result["duty"] == Decimal("37.20")


def test_zero_billed_units():
    tariff = get_tariff()

    result = calculate_fac_and_duty(
        "DOMESTIC",
        tariff,
        0,
        Decimal("0.00"),
        Decimal("0.00")
    )

    assert result["fac"] == Decimal("0.00")
    assert result["duty"] == Decimal("0.00")


def test_negative_billed_units_rejected():
    tariff = get_tariff()

    try:
        calculate_fac_and_duty(
            "DOMESTIC",
            tariff,
            -10,
            Decimal("0.00"),
            Decimal("0.00")
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
