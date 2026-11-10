
from decimal import Decimal
from datetime import date

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.net_metering_service import calculate_net_metering


def get_data():
    data = load_all_data()
    tariffs = build_tariff_catalog(data)

    consumers = {
        item["consumer_id"]: item
        for item in data["consumers"]
    }

    return consumers, tariffs


def test_excess_export_is_banked():
    consumers, tariffs = get_data()

    consumer = consumers["CON-0061"]

    result = calculate_net_metering(
        consumer,
        tariffs["TO-2026"],
        220,
        310,
        0,
        date(2026, 5, 3)
    )

    assert result["eligible"] is True
    assert result["units_billed"] == Decimal("0")
    assert result["banked_used"] == Decimal("0")
    assert result["banked_closing"] == Decimal("90")


def test_banked_units_are_used_before_billing():
    consumers, tariffs = get_data()

    consumer = consumers["CON-0061"]

    result = calculate_net_metering(
        consumer,
        tariffs["TO-2026"],
        400,
        280,
        90,
        date(2026, 6, 3)
    )

    assert result["units_billed"] == Decimal("30")
    assert result["banked_used"] == Decimal("90")
    assert result["banked_closing"] == Decimal("0")


def test_solar_capacity_equal_to_load_is_eligible():
    consumers, tariffs = get_data()

    consumer = consumers["CON-0049"]

    result = calculate_net_metering(
        consumer,
        tariffs["TO-2025"],
        100,
        120
    )

    assert result["eligible"] is True
    assert result["flag"] is None
    assert result["banked_closing"] == Decimal("20")


def test_solar_capacity_above_load_is_ineligible():
    consumers, tariffs = get_data()

    consumer = consumers["CON-0068"]

    result = calculate_net_metering(
        consumer,
        tariffs["TO-2025"],
        100,
        120
    )

    assert result["eligible"] is False
    assert result["flag"] == "INELIGIBLE_NET"
    assert result["units_billed"] == Decimal("100")
    assert result["banked_closing"] == Decimal("0")


def test_march_annual_settlement():
    consumers, tariffs = get_data()

    consumer = consumers["CON-0061"]

    result = calculate_net_metering(
        consumer,
        tariffs["TO-2025"],
        100,
        100,
        25,
        date(2026, 3, 31)
    )

    assert result["settled_units"] == Decimal("25")
    assert result["settlement_credit"] == Decimal("75.00")
    assert result["banked_closing"] == Decimal("0")


def test_negative_units_are_rejected():
    consumers, tariffs = get_data()

    consumer = consumers["CON-0061"]

    try:
        calculate_net_metering(
            consumer,
            tariffs["TO-2025"],
            -10,
            0
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
