
from decimal import Decimal

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.slab_calculator import (
    calculate_energy_charge,
    prorate_slabs
)


def get_tariff_catalog():
    data = load_all_data()
    return build_tariff_catalog(data)


def test_domestic_50_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        50, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("205.00")


def test_domestic_100_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        100, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("482.50")


def test_domestic_200_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        200, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("1192.50")


def test_domestic_300_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        300, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("2007.50")


def test_domestic_350_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        350, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("2447.50")


def test_zero_consumption():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        0, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("0.00")


def test_negative_consumption():
    tariff = get_tariff_catalog()["TO-2025"]

    try:
        calculate_energy_charge(
            -10, tariff, "DOMESTIC", 30
        )
        assert False
    except ValueError:
        assert True


def test_28_day_period():
    tariff = get_tariff_catalog()["TO-2025"]

    slabs = tariff["slabs"]["DOMESTIC"]
    adjusted = prorate_slabs(slabs, 28)

    assert adjusted[0]["to_unit"] == 50
    assert adjusted[1]["to_unit"] == 100


def test_34_day_period():
    tariff = get_tariff_catalog()["TO-2025"]

    slabs = tariff["slabs"]["DOMESTIC"]
    adjusted = prorate_slabs(slabs, 34)

    assert adjusted[0]["to_unit"] == 57
    assert adjusted[1]["to_unit"] == 113
    assert adjusted[2]["to_unit"] == 227
    assert adjusted[3]["to_unit"] == 340


def test_to_2026_domestic_50_units():
    tariff = get_tariff_catalog()["TO-2026"]

    result = calculate_energy_charge(
        50, tariff, "DOMESTIC", 30
    )

    assert result["energy_charge"] == Decimal("212.50")


def test_industrial_100_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        100, tariff, "INDUSTRIAL_LT", 30
    )

    assert result["energy_charge"] == Decimal("760.00")


def test_commercial_250_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        250, tariff, "COMMERCIAL", 30
    )

    assert result["energy_charge"] == Decimal("2360.00")


def test_agriculture_100_units():
    tariff = get_tariff_catalog()["TO-2025"]

    result = calculate_energy_charge(
        100, tariff, "AGRICULTURE", 30
    )

    assert result["energy_charge"] == Decimal("300.00")
