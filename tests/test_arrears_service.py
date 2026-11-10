
from datetime import date
from decimal import Decimal

import pytest

from services.arrears_service import (
    calculate_due_date,
    calculate_interest,
    accrue_interest,
    allocate_payment,
    calculate_total_arrears
)


def test_due_date_is_15_days_after_bill_date():
    result = calculate_due_date("2026-04-10")
    assert result == date(2026, 4, 25)


def test_no_interest_on_due_date():
    result = calculate_interest(
        "10000", "2026-04-25", "2026-04-25"
    )
    assert result == Decimal("0.00")


def test_interest_is_calculated_daily():
    result = calculate_interest(
        "10000", "2026-04-25", "2026-05-25"
    )
    assert result == Decimal("150.00")


def test_interest_is_not_compounded():
    debts = [{
        "bill_id": "BL-001",
        "due_date": "2026-04-25",
        "principal": "10000.00"
    }]

    first = accrue_interest(debts, "2026-05-25")
    second = accrue_interest(first, "2026-06-25")

    assert second[0]["principal"] == Decimal("10000.00")
    assert second[0]["interest"] == Decimal("305.00")


def test_payment_clears_interest_before_principal():
    debts = [{
        "bill_id": "BL-001",
        "due_date": "2026-04-25",
        "principal": "10000.00",
        "interest": "150.00",
        "last_interest_date": "2026-05-25"
    }]

    result = allocate_payment(
        debts, "500.00", "2026-05-25"
    )

    updated = result["debts"][0]

    assert updated["interest"] == Decimal("0.00")
    assert updated["principal"] == Decimal("9650.00")
    assert result["unapplied_amount"] == Decimal("0.00")


def test_payment_clears_oldest_principal_first():
    debts = [
        {
            "bill_id": "BL-OLD",
            "due_date": "2026-04-25",
            "principal": "1000.00",
            "interest": "0.00",
            "last_interest_date": "2026-04-25"
        },
        {
            "bill_id": "BL-NEW",
            "due_date": "2026-05-25",
            "principal": "2000.00",
            "interest": "0.00",
            "last_interest_date": "2026-05-25"
        }
    ]

    result = allocate_payment(
        debts, "1500.00", "2026-05-25"
    )

    balances = {
        debt["bill_id"]: debt["principal"]
        for debt in result["debts"]
    }

    assert balances["BL-OLD"] == Decimal("0.00")
    assert balances["BL-NEW"] == Decimal("1515.00")


def test_payment_cannot_be_negative():
    with pytest.raises(ValueError):
        allocate_payment([], "-100", "2026-05-25")


def test_total_arrears_includes_principal_and_interest():
    debts = [
        {
            "bill_id": "BL-001",
            "due_date": "2026-04-25",
            "principal": "1000.00",
            "interest": "50.00"
        },
        {
            "bill_id": "BL-002",
            "due_date": "2026-05-25",
            "principal": "2000.00",
            "interest": "25.00"
        }
    ]

    result = calculate_total_arrears(debts)
    assert result == Decimal("3075.00")
