
from decimal import Decimal
from datetime import date

from services.benefit_service import (
    calculate_bpl_benefit,
    calculate_payment_rebate,
)


def test_bpl_first_50_units_are_free():
    consumer = {"bpl": True}

    result = calculate_bpl_benefit(
        consumer, 80, Decimal("75.00")
    )

    assert result["free_units"] == Decimal("50")
    assert result["units_for_energy_charge"] == Decimal("30")
    assert result["fixed_charge_after_benefit"] == Decimal("0.00")


def test_bpl_fixed_charge_waived_at_100_units():
    consumer = {"bpl": True}

    result = calculate_bpl_benefit(
        consumer, 100, Decimal("75.00")
    )

    assert result["units_for_energy_charge"] == Decimal("50")
    assert result["fixed_charge_after_benefit"] == Decimal("0.00")


def test_bpl_fixed_charge_applies_above_100_units():
    consumer = {"bpl": True}

    result = calculate_bpl_benefit(
        consumer, 120, Decimal("75.00")
    )

    assert result["free_units"] == Decimal("50")
    assert result["units_for_energy_charge"] == Decimal("70")
    assert result["fixed_charge_after_benefit"] == Decimal("75.00")


def test_non_bpl_consumer_gets_no_benefit():
    consumer = {"bpl": False}

    result = calculate_bpl_benefit(
        consumer, 80, Decimal("75.00")
    )

    assert result["free_units"] == Decimal("0")
    assert result["units_for_energy_charge"] == Decimal("80")
    assert result["fixed_charge_after_benefit"] == Decimal("75.00")


def test_online_payment_on_seventh_day():
    result = calculate_payment_rebate(
        date(2026, 4, 10),
        date(2026, 4, 17),
        "ONLINE",
        Decimal("10000.00")
    )

    assert result["prompt_rebate"] == Decimal("100.00")
    assert result["online_rebate"] == Decimal("50.00")
    assert result["total_rebate"] == Decimal("150.00")


def test_counter_payment_gets_only_prompt_rebate():
    result = calculate_payment_rebate(
        date(2026, 4, 10),
        date(2026, 4, 15),
        "COUNTER",
        Decimal("5000.00")
    )

    assert result["prompt_rebate"] == Decimal("50.00")
    assert result["online_rebate"] == Decimal("0.00")


def test_payment_after_seven_days_gets_no_rebate():
    result = calculate_payment_rebate(
        date(2026, 4, 10),
        date(2026, 4, 18),
        "ONLINE",
        Decimal("5000.00")
    )

    assert result["total_rebate"] == Decimal("0.00")


def test_negative_discountable_amount_rejected():
    try:
        calculate_payment_rebate(
            date(2026, 4, 10),
            date(2026, 4, 15),
            "ONLINE",
            Decimal("-100.00")
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
