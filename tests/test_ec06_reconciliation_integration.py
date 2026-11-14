
from decimal import Decimal

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.billing_engine import calculate_consumer_bills


def test_ec06_reconciliation_is_applied_in_production_billing():
    data = load_all_data()

    consumer = next(
        item for item in data["consumers"]
        if item["consumer_id"] == "CON-0077"
    )

    readings = [
        item for item in data["readings"]
        if item["consumer_id"] == "CON-0077"
    ]

    bills = calculate_consumer_bills(
        consumer,
        readings,
        build_tariff_catalog(data),
    )

    reconciled = {
        bill["reading_id"]: bill
        for bill in bills
        if bill["reading_id"] in {"RD-00493", "RD-00595"}
    }

    faulty = reconciled["RD-00493"]
    following = reconciled["RD-00595"]

    assert faulty["units_imported"] == 120
    assert following["units_imported"] == 100

    assert faulty["energy_charge"] == Decimal("624.50")
    assert following["energy_charge"] == Decimal("482.50")

    assert faulty["fac"] == Decimal("42.00")
    assert following["fac"] == Decimal("35.00")

    assert faulty["duty"] == Decimal("48.99")
    assert following["duty"] == Decimal("40.05")

    assert faulty["net_current"] == Decimal("865.49")
    assert following["net_current"] == Decimal("707.55")

    assert faulty["minimum_charge_adjustment"] == Decimal("0.00")

    assert "FAULTY_AVERAGE" in faulty["flags"]
    assert "RECONCILED" in faulty["flags"]
    assert "RECONCILED" in following["flags"]

    assert "RECONCILIATION_PENDING" not in faulty["flags"]
    assert "RECONCILIATION_PENDING" not in following["flags"]

    assert (
        faulty["units_imported"] + following["units_imported"]
    ) == 220
