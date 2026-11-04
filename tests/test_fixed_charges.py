from decimal import Decimal

import pytest

from models.enums import ConsumerCategory
from services.fixed_charge_service import calculate_fixed_charge


def test_domestic_fixed_charge():
    result = calculate_fixed_charge(
        ConsumerCategory.DOMESTIC,
        Decimal("5")
    )

    assert result.total_charge == Decimal("375.00")


def test_commercial_fixed_charge():
    result = calculate_fixed_charge(
        ConsumerCategory.COMMERCIAL,
        Decimal("5")
    )

    assert result.total_charge == Decimal("750.00")


def test_industrial_fixed_charge():
    result = calculate_fixed_charge(
        ConsumerCategory.INDUSTRIAL_LT,
        Decimal("5")
    )

    assert result.total_charge == Decimal("1250.00")


def test_agriculture_fixed_charge():
    result = calculate_fixed_charge(
        ConsumerCategory.AGRICULTURE,
        Decimal("5")
    )

    assert result.total_charge == Decimal("0.00")


def test_exactly_ten_percent_excess_no_penalty():
    result = calculate_fixed_charge(
        ConsumerCategory.DOMESTIC,
        Decimal("5"),
        Decimal("5.5")
    )

    assert result.excess_load_penalty == Decimal("0.00")
    assert result.load_regularisation_required is False


def test_more_than_ten_percent_excess():
    result = calculate_fixed_charge(
        ConsumerCategory.DOMESTIC,
        Decimal("5"),
        Decimal("6")
    )

    assert result.base_charge == Decimal("375.00")
    assert result.excess_load_penalty == Decimal("150.00")
    assert result.total_charge == Decimal("525.00")
    assert result.load_regularisation_required is True


def test_bpl_fixed_charge_exemption():
    result = calculate_fixed_charge(
        ConsumerCategory.DOMESTIC,
        Decimal("5"),
        is_bpl=True,
        consumption=Decimal("100")
    )

    assert result.total_charge == Decimal("0.00")


def test_bpl_above_100_units():
    result = calculate_fixed_charge(
        ConsumerCategory.DOMESTIC,
        Decimal("5"),
        is_bpl=True,
        consumption=Decimal("101")
    )

    assert result.total_charge == Decimal("375.00")


def test_negative_load_rejected():
    with pytest.raises(ValueError):
        calculate_fixed_charge(
            ConsumerCategory.DOMESTIC,
            Decimal("-5")
        )