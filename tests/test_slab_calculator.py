from decimal import Decimal

import pytest

from models.tariff import Slab
from services.slab_calculator import (
    calculate_energy_charge,
    calculate_slab_breakdown
)


DOMESTIC_SLABS = [
    Slab(Decimal("50"), Decimal("4.10")),
    Slab(Decimal("100"), Decimal("5.55")),
    Slab(Decimal("200"), Decimal("7.10")),
    Slab(Decimal("300"), Decimal("8.15")),
    Slab(None, Decimal("8.80"))
]


def test_250_units():
    result = calculate_energy_charge(
        Decimal("250"), DOMESTIC_SLABS
    )

    assert result == Decimal("1600.00")


def test_exactly_50_units():
    result = calculate_energy_charge(
        Decimal("50"), DOMESTIC_SLABS
    )

    assert result == Decimal("205.00")


def test_exactly_100_units():
    result = calculate_energy_charge(
        Decimal("100"), DOMESTIC_SLABS
    )

    assert result == Decimal("482.50")


def test_exactly_200_units():
    result = calculate_energy_charge(
        Decimal("200"), DOMESTIC_SLABS
    )

    assert result == Decimal("1192.50")


def test_exactly_300_units():
    result = calculate_energy_charge(
        Decimal("300"), DOMESTIC_SLABS
    )

    assert result == Decimal("2007.50")


def test_above_300_units():
    result = calculate_energy_charge(
        Decimal("350"), DOMESTIC_SLABS
    )

    assert result == Decimal("2447.50")


def test_zero_consumption():
    result = calculate_energy_charge(
        Decimal("0"), DOMESTIC_SLABS
    )

    assert result == Decimal("0.00")


def test_negative_consumption():
    with pytest.raises(ValueError):
        calculate_energy_charge(
            Decimal("-10"), DOMESTIC_SLABS
        )


def test_34_day_proration():
    result = calculate_slab_breakdown(
        Decimal("57"), DOMESTIC_SLABS, days=34
    )

    # 50 * 34 / 30 = 56.67, rounded to 57 units.
    assert result[0].units == Decimal("57")
    assert result[0].amount == Decimal("233.70")


def test_28_day_period_no_proration():
    result = calculate_slab_breakdown(
        Decimal("50"), DOMESTIC_SLABS, days=28
    )

    assert result[0].units == Decimal("50")
    assert result[0].amount == Decimal("205.00")


def test_33_day_period_no_proration():
    result = calculate_slab_breakdown(
        Decimal("50"), DOMESTIC_SLABS, days=33
    )

    assert result[0].units == Decimal("50")


def test_single_flat_tariff():
    flat_slab = [
        Slab(None, Decimal("9.20"))
    ]

    result = calculate_energy_charge(
        Decimal("150"), flat_slab
    )

    assert result == Decimal("1380.00")