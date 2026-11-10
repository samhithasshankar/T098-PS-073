
from decimal import Decimal

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.tod_service import calculate_tod_adjustment


def get_tariff():
    data = load_all_data()
    tariffs = build_tariff_catalog(data)
    return tariffs["TO-2025"]


def test_tod_adjustment_for_eligible_consumer():
    tariff = get_tariff()

    consumer = {
        "meter_type": "TOD",
        "category": "COMMERCIAL",
    }

    result = calculate_tod_adjustment(
        consumer,
        tariff,
        Decimal("1000"),
        Decimal("20"),
        Decimal("30"),
        Decimal("50"),
    )

    assert result["eligible"] is True
    assert result["peak_adjustment"] == Decimal("40.00")
    assert result["offpeak_adjustment"] == Decimal("-30.00")
    assert result["tod_adjustment"] == Decimal("10.00")


def test_normal_meter_gets_no_tod_adjustment():
    tariff = get_tariff()

    consumer = {
        "meter_type": "NORMAL",
        "category": "COMMERCIAL",
    }

    result = calculate_tod_adjustment(
        consumer, tariff, 1000, 20, 30, 50
    )

    assert result["eligible"] is False
    assert result["tod_adjustment"] == Decimal("0.00")


def test_domestic_tod_meter_is_not_eligible():
    tariff = get_tariff()

    consumer = {
        "meter_type": "TOD",
        "category": "DOMESTIC",
    }

    result = calculate_tod_adjustment(
        consumer, tariff, 1000, 20, 30, 50
    )

    assert result["eligible"] is False
    assert result["tod_adjustment"] == Decimal("0.00")


def test_zero_tod_units():
    tariff = get_tariff()

    consumer = {
        "meter_type": "TOD",
        "category": "COMMERCIAL",
    }

    result = calculate_tod_adjustment(
        consumer, tariff, 1000, 0, 0, 0
    )

    assert result["eligible"] is True
    assert result["tod_adjustment"] == Decimal("0.00")


def test_negative_tod_units_are_rejected():
    tariff = get_tariff()

    consumer = {
        "meter_type": "TOD",
        "category": "COMMERCIAL",
    }

    try:
        calculate_tod_adjustment(
            consumer, tariff, 1000, -10, 30, 50
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
