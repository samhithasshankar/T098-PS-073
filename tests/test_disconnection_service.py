
from datetime import date
from decimal import Decimal

import pytest

from services.disconnection_service import (
    calculate_disconnection_date,
    is_agriculture_disconnection_restricted,
    evaluate_disconnection,
    calculate_reconnection_amount,
    evaluate_reconnection
)


def test_disconnection_date_is_15_days_after_notice():
    result = calculate_disconnection_date("2026-06-01")
    assert result == date(2026, 6, 16)


def test_domestic_notice_requires_more_than_two_unpaid_bills():
    result = evaluate_disconnection(
        "DOMESTIC", 2, "1500", "2026-06-01"
    )
    assert result["state"] == "CONNECTED"


def test_domestic_notice_issued_after_three_unpaid_bills():
    result = evaluate_disconnection(
        "DOMESTIC", 3, "1001", "2026-06-01"
    )
    assert result["state"] == "DISCONNECTION_NOTICE"


def test_arrears_must_exceed_domestic_threshold():
    result = evaluate_disconnection(
        "DOMESTIC", 3, "1000", "2026-06-01"
    )
    assert result["state"] == "CONNECTED"


def test_other_category_uses_5000_threshold():
    result = evaluate_disconnection(
        "COMMERCIAL", 3, "5000", "2026-06-01"
    )
    assert result["state"] == "CONNECTED"


def test_disconnect_after_notice_period():
    result = evaluate_disconnection(
        "DOMESTIC",
        3,
        "1500",
        "2026-06-20",
        notice_date="2026-06-01"
    )
    assert result["state"] == "DISCONNECTED"


def test_no_disconnection_before_notice_period_ends():
    result = evaluate_disconnection(
        "DOMESTIC",
        3,
        "1500",
        "2026-06-15",
        notice_date="2026-06-01"
    )
    assert result["state"] == "DISCONNECTION_NOTICE"


def test_agriculture_restricted_from_june_through_november():
    for month in range(6, 12):
        check_date = date(2026, month, 20)

        assert is_agriculture_disconnection_restricted(
            "AGRICULTURE", check_date
        )


def test_agriculture_can_be_disconnected_outside_restricted_months():
    assert not is_agriculture_disconnection_restricted(
        "AGRICULTURE", "2026-12-20"
    )


def test_reconnection_amount_includes_deposit_top_up():
    result = calculate_reconnection_amount(
        total_arrears="5000",
        security_deposit="1000",
        average_monthly_bill="1500"
    )

    assert result["arrears"] == Decimal("5000.00")
    assert result["reconnection_fee"] == Decimal("250.00")
    assert result["deposit_top_up"] == Decimal("2000.00")
    assert result["total_required"] == Decimal("7250.00")


def test_no_deposit_top_up_when_deposit_is_sufficient():
    result = calculate_reconnection_amount(
        total_arrears="1000",
        security_deposit="4000",
        average_monthly_bill="1500"
    )

    assert result["deposit_top_up"] == Decimal("0.00")
    assert result["total_required"] == Decimal("1250.00")


def test_reconnection_refused_when_payment_is_incomplete():
    result = evaluate_reconnection(
        amount_paid="7000",
        total_arrears="5000",
        security_deposit="1000",
        average_monthly_bill="1500"
    )

    assert result["state"] == "DISCONNECTED"
    assert result["shortfall"] == Decimal("250.00")


def test_reconnection_allowed_after_full_payment():
    result = evaluate_reconnection(
        amount_paid="7250",
        total_arrears="5000",
        security_deposit="1000",
        average_monthly_bill="1500"
    )

    assert result["state"] == "RECONNECTED"
    assert result["shortfall"] == Decimal("0.00")


def test_negative_reconnection_payment_rejected():
    with pytest.raises(ValueError):
        evaluate_reconnection(
            "-100",
            "5000",
            "1000",
            "1500"
        )
