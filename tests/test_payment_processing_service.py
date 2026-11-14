
from decimal import Decimal

from services.payment_processing_service import process_payments


def make_bill(bill_id, consumer_id, bill_date, amount):
    return {
        "bill_id": bill_id,
        "consumer_id": consumer_id,
        "bill_date": bill_date,
        "net_current": str(amount),
    }


def make_payment(payment_id, consumer_id, payment_date, amount, mode="COUNTER"):
    return {
        "payment_id": payment_id,
        "consumer_id": consumer_id,
        "payment_ts": f"{payment_date} 12:00:00",
        "amount": str(amount),
        "mode": mode,
    }


def get_all_debts(result):
    debts = result["debts"]

    if isinstance(debts, list):
        return debts

    if isinstance(debts, dict):
        all_debts = []

        for value in debts.values():
            if isinstance(value, list):
                all_debts.extend(value)
            elif isinstance(value, dict):
                if "bill_id" in value:
                    all_debts.append(value)
                else:
                    all_debts.extend(
                        item for item in value.values()
                        if isinstance(item, dict) and "bill_id" in item
                    )

        return all_debts

    return []


def get_debt(result, bill_id):
    return next(
        debt for debt in get_all_debts(result)
        if debt["bill_id"] == bill_id
    )


def test_bill_without_payment_creates_outstanding_debt():
    bills = [
        make_bill("BILL-001", "CON-0001", "2026-01-01", 1000)
    ]

    result = process_payments(bills, [])

    debt = get_debt(result, "BILL-001")

    assert Decimal(str(debt["principal"])) == Decimal("1000")
    assert Decimal(str(debt["interest"])) == Decimal("0")


def test_payment_before_due_date_reduces_principal():
    bills = [
        make_bill("BILL-001", "CON-0001", "2026-01-01", 1000)
    ]

    payments = [
        make_payment("PAY-001", "CON-0001", "2026-01-10", 400)
    ]

    result = process_payments(bills, payments)

    debt = get_debt(result, "BILL-001")

    assert Decimal(str(debt["principal"])) == Decimal("600")
    assert Decimal(str(debt["interest"])) == Decimal("0")


def test_payment_after_due_date_pays_interest_before_principal():
    bills = [
        make_bill("BILL-001", "CON-0001", "2026-01-01", 1000)
    ]

    payments = [
        make_payment("PAY-001", "CON-0001", "2026-01-20", 10)
    ]

    result = process_payments(bills, payments)

    debt = get_debt(result, "BILL-001")

    assert Decimal(str(debt["interest"])) == Decimal("0")
    assert Decimal(str(debt["principal"])) < Decimal("1000")


def test_payment_is_allocated_to_oldest_bill_first():
    bills = [
        make_bill("BILL-001", "CON-0001", "2026-01-01", 100),
        make_bill("BILL-002", "CON-0001", "2026-02-01", 100),
    ]

    payments = [
        make_payment("PAY-001", "CON-0001", "2026-02-10", 100)
    ]

    result = process_payments(bills, payments)

    oldest_debt = get_debt(result, "BILL-001")
    newer_debt = get_debt(result, "BILL-002")

    # Oldest bill accrued Rs. 1.25 interest.
    # The payment clears interest first, then reduces principal.
    assert Decimal(str(oldest_debt["interest"])) == Decimal("0")
    assert Decimal(str(oldest_debt["principal"])) == Decimal("1.25")

    # The newer bill must remain untouched.
    assert Decimal(str(newer_debt["principal"])) == Decimal("100")


def test_excess_payment_is_carried_forward_as_credit():
    bills = [
        make_bill("BILL-001", "CON-0001", "2026-01-01", 100)
    ]

    payments = [
        make_payment("PAY-001", "CON-0001", "2026-01-10", 150)
    ]

    result = process_payments(bills, payments)

    debt = get_debt(result, "BILL-001")

    assert Decimal(str(debt["principal"])) == Decimal("0")
    assert Decimal(str(debt["interest"])) == Decimal("0")
    assert result["unapplied_credits"]


def test_ledger_contains_bill_and_payment_entries():
    bills = [
        make_bill("BILL-001", "CON-0001", "2026-01-01", 1000)
    ]

    payments = [
        make_payment("PAY-001", "CON-0001", "2026-01-10", 400)
    ]

    result = process_payments(bills, payments)

    entry_types = [
        entry["entry_type"]
        for entry in result["ledger"]
    ]

    assert "BILL" in entry_types
    assert "PAYMENT" in entry_types
