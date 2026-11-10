
from datetime import date
from decimal import Decimal

from services.billing_service import calculate_period_bill
from services.tariff_service import build_tariff_catalog
from utils.data_loader import load_all_data


def setup_data():
    data = load_all_data()

    consumers = {
        row["consumer_id"]: row
        for row in data["consumers"]
    }

    tariffs = build_tariff_catalog(data)

    return consumers, tariffs


def test_domestic_50_unit_bill():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0063"],
        tariffs["TO-2025"],
        period_days=30,
        import_units=50,
        bill_date=date(2025, 9, 3),
    )

    assert result["units_billed"] == 50
    assert result["energy_charge"] == Decimal("205.00")
    assert result["fixed_charge"] == Decimal("150.00")
    assert result["fac"] == Decimal("17.50")
    assert result["duty"] == Decimal("22.35")
    assert result["net_current"] == Decimal("394.85")


def test_net_metering_excess_export():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0061"],
        tariffs["TO-2026"],
        period_days=30,
        import_units=220,
        export_units=310,
        opening_banked_units=0,
        bill_date=date(2026, 5, 3),
    )

    assert result["units_billed"] == 0
    assert result["banked_closing"] == Decimal("90")
    assert result["energy_charge"] == Decimal("0.00")
    assert result["fac"] == Decimal("0.00")


def test_net_metering_uses_opening_bank():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0061"],
        tariffs["TO-2026"],
        period_days=31,
        import_units=400,
        export_units=280,
        opening_banked_units=90,
        bill_date=date(2026, 6, 3),
    )

    assert result["units_billed"] == 30
    assert result["banked_used"] == Decimal("90")
    assert result["banked_closing"] == Decimal("0")


def test_ineligible_net_meter():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0068"],
        tariffs["TO-2025"],
        period_days=30,
        import_units=100,
        export_units=120,
        bill_date=date(2025, 9, 3),
    )

    assert result["units_billed"] == 100
    assert "INELIGIBLE_NET" in result["flags"]


def test_exact_ten_percent_demand_excess():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0091"],
        tariffs["TO-2025"],
        period_days=30,
        import_units=100,
        max_demand_kw=Decimal("5.50"),
        bill_date=date(2025, 9, 10),
    )

    assert result["excess_demand_charge"] == Decimal("0.00")
    assert "LOAD_REGULARISATION" not in result["flags"]


def test_demand_above_ten_percent():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0091"],
        tariffs["TO-2025"],
        period_days=30,
        import_units=100,
        max_demand_kw=Decimal("5.51"),
        bill_date=date(2025, 10, 10),
    )

    assert result["excess_demand_charge"] == Decimal("153.00")
    assert "LOAD_REGULARISATION" in result["flags"]


def test_false_bpl_value_does_not_activate_benefit():
    consumers, tariffs = setup_data()

    result = calculate_period_bill(
        consumers["CON-0063"],
        tariffs["TO-2025"],
        period_days=30,
        import_units=80,
        bill_date=date(2025, 9, 3),
    )

    assert result["energy_units"] == 80
    assert result["subsidy"] == Decimal("0.00")
