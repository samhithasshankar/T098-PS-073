
from datetime import datetime
from decimal import Decimal

import pytest

from services.rebate_service import (
    calculate_online_rebate,
    calculate_payment_rebates,
    calculate_prompt_rebate,
)


def test_prompt_rebate_within_seven_days():
    rebate = calculate_prompt_rebate(
        Decimal("5000"),
        "2026-04-10",
        "2026-04-15 12:00:00",
    )

    assert rebate == Decimal("50.00")


def test_prompt_rebate_on_seventh_day_at_1159_pm():
    rebate = calculate_prompt_rebate(
        Decimal("5000"),
        "2026-04-10",
        "2026-04-17 23:59:00",
    )

    assert rebate == Decimal("50.00")


def test_prompt_rebate_not_allowed_after_seven_days():
    rebate = calculate_prompt_rebate(
        Decimal("5000"),
        "2026-04-10",
        "2026-04-18 00:00:00",
    )

    assert rebate == Decimal("0.00")


def test_prompt_rebate_not_allowed_before_bill_date():
    rebate = calculate_prompt_rebate(
        Decimal("5000"),
        "2026-04-10",
        "2026-04-09 12:00:00",
    )

    assert rebate == Decimal("0.00")


def test_prompt_rebate_is_capped_at_100():
    rebate = calculate_prompt_rebate(
        Decimal("20000"),
        "2026-04-10",
        "2026-04-17 23:59:00",
    )

    assert rebate == Decimal("100.00")


def test_online_rebate_is_half_percent():
    rebate = calculate_online_rebate(
        Decimal("5000"),
        "ONLINE",
    )

    assert rebate == Decimal("25.00")


def test_online_rebate_is_capped_at_50():
    rebate = calculate_online_rebate(
        Decimal("20000"),
        "ONLINE",
    )

    assert rebate == Decimal("50.00")


def test_counter_payment_does_not_get_online_rebate():
    rebate = calculate_online_rebate(
        Decimal("5000"),
        "COUNTER",
    )

    assert rebate == Decimal("0.00")


def test_combined_rebates_are_returned_separately():
    result = calculate_payment_rebates(
        eligible_amount=Decimal("5000"),
        bill_date="2026-04-10",
        payment_ts="2026-04-17 23:59:00",
        mode="ONLINE",
    )

    assert result["prompt_rebate"] == Decimal("50.00")
    assert result["online_rebate"] == Decimal("25.00")
    assert result["total_rebate"] == Decimal("75.00")


def test_invalid_payment_mode_is_rejected():
    with pytest.raises(ValueError):
        calculate_online_rebate(
            Decimal("5000"),
            "CHEQUE",
        )


def test_negative_eligible_amount_is_rejected():
    with pytest.raises(ValueError):
        calculate_prompt_rebate(
            Decimal("-100"),
            "2026-04-10",
            "2026-04-12 12:00:00",
        )


def test_datetime_objects_are_supported():
    rebate = calculate_prompt_rebate(
        Decimal("1000"),
        datetime(2026, 4, 10),
        datetime(2026, 4, 17, 23, 59),
    )

    assert rebate == Decimal("10.00")
