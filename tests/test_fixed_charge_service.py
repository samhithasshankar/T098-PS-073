
from decimal import Decimal

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.fixed_charge_service import (
    calculate_fixed_and_demand_charges,
)


def get_test_data():
    data = load_all_data()
    tariffs = build_tariff_catalog(data)

    consumer = next(
        item for item in data["consumers"]
        if item["consumer_id"] == "CON-0091"
    )

    return consumer, tariffs["TO-2025"]


def test_commercial_fixed_charge():
    consumer, tariff = get_test_data()

    result = calculate_fixed_and_demand_charges(
        consumer, tariff, Decimal("5.50")
    )

    assert result["fixed_charge"] == Decimal("750.00")


def test_demand_exactly_110_percent_has_no_penalty():
    consumer, tariff = get_test_data()

    result = calculate_fixed_and_demand_charges(
        consumer, tariff, Decimal("5.50")
    )

    assert result["excess_demand_charge"] == Decimal("0.00")
    assert result["excess_demand_flag"] is False


def test_demand_above_110_percent_has_penalty():
    consumer, tariff = get_test_data()

    result = calculate_fixed_and_demand_charges(
        consumer, tariff, Decimal("5.51")
    )

    assert result["excess_demand_flag"] is True
    assert result["excess_demand_kw"] == Decimal("0.51")
    assert result["excess_demand_charge"] == Decimal("153.00")


def test_missing_demand_has_no_excess_charge():
    consumer, tariff = get_test_data()

    result = calculate_fixed_and_demand_charges(
        consumer, tariff, None
    )

    assert result["excess_demand_charge"] == Decimal("0.00")
    assert result["excess_demand_flag"] is False
