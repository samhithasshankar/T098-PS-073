
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP


MONTHLY_INTEREST_RATE = Decimal("0.015")
DAYS_IN_MONTH = Decimal("30")
ZERO = Decimal("0.00")
MONEY_PLACES = Decimal("0.01")


def to_date(value):
    """Convert a date string or date object into a date object."""
    if isinstance(value, date):
        return value

    return date.fromisoformat(value)


def to_decimal(value):
    """Safely convert a value into Decimal."""
    return Decimal(str(value))


def round_money(value):
    """Round money to two decimal places."""
    return to_decimal(value).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_due_date(bill_date):
    """The bill is due 15 days after its bill date."""
    bill_date = to_date(bill_date)
    return bill_date + timedelta(days=15)


def calculate_interest(principal, due_date, as_of_date):
    """
    Calculate simple interest at 1.5% per month.

    Interest starts after the due date.
    Interest is calculated daily using a 30-day month.
    Interest is calculated only on principal.
    """
    principal = to_decimal(principal)
    due_date = to_date(due_date)
    as_of_date = to_date(as_of_date)

    if principal < 0:
        raise ValueError("Principal cannot be negative.")

    if as_of_date <= due_date or principal == 0:
        return ZERO

    overdue_days = (as_of_date - due_date).days

    interest = (
        principal
        * MONTHLY_INTEREST_RATE
        * Decimal(overdue_days)
        / DAYS_IN_MONTH
    )

    return round_money(interest)


def accrue_interest(debts, as_of_date):
    """
    Accrue interest on outstanding principal.

    Each debt must contain:
        bill_id
        due_date
        principal

    Optional fields:
        interest
        last_interest_date

    Returns a new list without modifying the original list.
    """
    as_of_date = to_date(as_of_date)
    updated_debts = deepcopy(debts)

    for debt in updated_debts:
        due_date = to_date(debt["due_date"])
        principal = to_decimal(debt["principal"])
        existing_interest = to_decimal(
            debt.get("interest", ZERO)
        )

        last_interest_date = to_date(
            debt.get("last_interest_date", due_date)
        )

        if principal < 0 or existing_interest < 0:
            raise ValueError(
                "Principal and interest cannot be negative."
            )

        interest_start = max(last_interest_date, due_date)

        if as_of_date > interest_start and principal > 0:
            overdue_days = (
                as_of_date - interest_start
            ).days

            additional_interest = (
                principal
                * MONTHLY_INTEREST_RATE
                * Decimal(overdue_days)
                / DAYS_IN_MONTH
            )

            existing_interest += round_money(
                additional_interest
            )

        debt["principal"] = round_money(principal)
        debt["interest"] = round_money(existing_interest)
        debt["due_date"] = due_date
        debt["last_interest_date"] = max(
            last_interest_date,
            as_of_date
        )

    return updated_debts


def allocate_payment(debts, payment_amount, payment_date):
    """
    Apply a payment in this order:
      1. Accrued interest, oldest bill first.
      2. Outstanding principal, oldest bill first.

    Returns:
      updated_debts
      allocations
      unapplied_amount
    """
    payment_amount = to_decimal(payment_amount)
    payment_date = to_date(payment_date)

    if payment_amount < 0:
        raise ValueError("Payment amount cannot be negative.")

    payment_amount = round_money(payment_amount)

    updated_debts = accrue_interest(debts, payment_date)

    # Oldest bill first.
    updated_debts.sort(
        key=lambda debt: (
            to_date(debt["due_date"]),
            debt["bill_id"]
        )
    )

    remaining_payment = payment_amount
    allocations = []

    # First clear interest.
    for debt in updated_debts:
        if remaining_payment <= 0:
            break

        outstanding_interest = to_decimal(
            debt.get("interest", ZERO)
        )

        amount_paid = min(
            remaining_payment,
            outstanding_interest
        )

        amount_paid = round_money(amount_paid)

        debt["interest"] = round_money(
            outstanding_interest - amount_paid
        )

        remaining_payment = round_money(
            remaining_payment - amount_paid
        )

        if amount_paid > 0:
            allocations.append({
                "bill_id": debt["bill_id"],
                "entry_type": "INTEREST",
                "amount": amount_paid
            })

    # Then clear principal.
    for debt in updated_debts:
        if remaining_payment <= 0:
            break

        outstanding_principal = to_decimal(
            debt["principal"]
        )

        amount_paid = min(
            remaining_payment,
            outstanding_principal
        )

        amount_paid = round_money(amount_paid)

        debt["principal"] = round_money(
            outstanding_principal - amount_paid
        )

        remaining_payment = round_money(
            remaining_payment - amount_paid
        )

        if amount_paid > 0:
            allocations.append({
                "bill_id": debt["bill_id"],
                "entry_type": "PRINCIPAL",
                "amount": amount_paid
            })

    return {
        "debts": updated_debts,
        "allocations": allocations,
        "unapplied_amount": round_money(remaining_payment)
    }


def calculate_total_arrears(debts):
    """Return total outstanding principal plus interest."""
    total = ZERO

    for debt in debts:
        total += (
            to_decimal(debt["principal"])
            + to_decimal(debt.get("interest", ZERO))
        )

    return round_money(total)
