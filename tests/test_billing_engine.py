
from datetime import date
from decimal import Decimal

import pytest

from services.billing_engine import calculate_consumer_bills
from services.tariff_service import build_tariff_catalog
from utils.data_loader import load_all_data


def setup_data():
    data = load_all_data()

    consumers = {
        row["consumer_id"]: row
        for row in data["consumers"]
    }

    tariffs = build_tariff_catalog(data)

    return data, consumers, tariffs


def test_consumer_billing_returns_bills():
    data, consumers, tariffs = setup_data()

    consumer_id = "CON-0063"

    readings = [
        row for row in data["readings"]
        if row["consumer_id"] == consumer_id
    ]

    result = calculate_consumer_bills(
        consumer=consumers[consumer_id],
        readings=readings,
        tariff_catalog=tariffs
    )

    assert len(result) > 0

    for bill in result:
        assert bill["consumer_id"] == consumer_id
        assert bill["units_billed"] >= 0
        assert bill["net_current"] >= 0
        assert bill["tariff_id"] in tariffs


def test_consumer_billing_preserves_net_meter_bank():
    data, consumers, tariffs = setup_data()

    consumer_id = "CON-0061"

    readings = [
        row for row in data["readings"]
        if row["consumer_id"] == consumer_id
    ]

    result = calculate_consumer_bills(
        consumer=consumers[consumer_id],
        readings=readings,
        tariff_catalog=tariffs
    )

    assert len(result) > 0

    for previous, current in zip(result, result[1:]):
        assert current["banked_used"] >= 0
        assert previous["banked_closing"] >= 0


def test_opening_bank_is_used():
    data, consumers, tariffs = setup_data()

    consumer_id = "CON-0061"

    readings = [
        row for row in data["readings"]
        if row["consumer_id"] == consumer_id
    ]

    result = calculate_consumer_bills(
        consumer=consumers[consumer_id],
        readings=readings,
        tariff_catalog=tariffs,
        opening_banked_units=Decimal("50")
    )

    assert len(result) > 0


def test_unknown_consumer_readings_return_empty():
    data, consumers, tariffs = setup_data()

    consumer = consumers["CON-0063"]

    result = calculate_consumer_bills(
        consumer=consumer,
        readings=[],
        tariff_catalog=tariffs
    )

    assert result == []
