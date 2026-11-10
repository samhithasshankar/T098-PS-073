
from decimal import Decimal

import pytest

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.reconciliation_service import calculate_faulty_reconciliation


def get_tariff():
    data = load_all_data()
    tariffs = build_tariff_catalog(data)
    return tariffs["TO-2025"]


def test_reconciliation_calculates_each_month_separately():
    tariff = get_tariff()

    estimated_months = [
        {
            "units": 260,
            "tariff": tariff,
            "period_days": 30,
        },
        {
            "units": 260,
            "tariff": tariff,
            "period_days": 30,
        },
    ]

    actual_months = [
        {
            "units": 120,
            "tariff": tariff,
            "period_days": 30,
        },
        {
            "units": 100,
            "tariff": tariff,
            "period_days": 30,
        },
    ]

    result = calculate_faulty_reconciliation(
        "DOMESTIC",
        estimated_months,
        actual_months
    )

    assert len(result["monthly_details"]) == 2

    assert result["monthly_details"][0]["actual_units"] == 120
    assert result["monthly_details"][1]["actual_units"] == 100

    assert result["reconciliation_adjustment"] == (
        result["actual_total"] - result["estimated_total"]
    )


def test_positive_reconciliation():
    tariff = get_tariff()

    estimated = [{
        "units": 100,
        "tariff": tariff,
        "period_days": 30,
    }]

    actual = [{
        "units": 200,
        "tariff": tariff,
        "period_days": 30,
    }]

    result = calculate_faulty_reconciliation(
        "DOMESTIC", estimated, actual
    )

    assert result["reconciliation_adjustment"] > Decimal("0.00")


def test_negative_reconciliation_gives_credit():
    tariff = get_tariff()

    estimated = [{
        "units": 200,
        "tariff": tariff,
        "period_days": 30,
    }]

    actual = [{
        "units": 100,
        "tariff": tariff,
        "period_days": 30,
    }]

    result = calculate_faulty_reconciliation(
        "DOMESTIC", estimated, actual
    )

    assert result["reconciliation_adjustment"] < Decimal("0.00")


def test_mismatched_month_counts_are_rejected():
    tariff = get_tariff()

    estimated = [{
        "units": 100,
        "tariff": tariff,
        "period_days": 30,
    }]

    actual = [
        {
            "units": 100,
            "tariff": tariff,
            "period_days": 30,
        },
        {
            "units": 120,
            "tariff": tariff,
            "period_days": 30,
        },
    ]

    with pytest.raises(ValueError):
        calculate_faulty_reconciliation(
            "DOMESTIC", estimated, actual
        )
