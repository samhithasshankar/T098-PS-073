
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
RECONNECTION_FEE = Decimal("250.00")
DOMESTIC_ARREARS_LIMIT = Decimal("1000.00")
OTHER_ARREARS_LIMIT = Decimal("5000.00")
MONEY_PLACES = Decimal("0.01")


def to_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def to_decimal(value):
    return Decimal(str(value))


def round_money(value):
    return to_decimal(value).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP
    )


def get_arrears_threshold(category):
    """Return the applicable disconnection arrears threshold."""
    if category.upper() == "DOMESTIC":
        return DOMESTIC_ARREARS_LIMIT

    return OTHER_ARREARS_LIMIT


def calculate_disconnection_date(notice_date):
    """Disconnection can occur 15 days after the notice date."""
    return to_date(notice_date) + timedelta(days=15)


def is_agriculture_disconnection_restricted(category, check_date):
    """
    Agriculture consumers must not be disconnected
    during June, July, August, September, October or November.
    """
    check_date = to_date(check_date)

    return (
        category.upper() == "AGRICULTURE"
        and check_date.month in (6, 7, 8, 9, 10, 11)
    )


def evaluate_disconnection(
    category,
    consecutive_unpaid_bills,
    total_arrears,
    as_of_date,
    notice_date=None
):
    """
    Evaluate whether a consumer should receive a notice
    or be disconnected.

    Notice conditions:
      - More than two consecutive unpaid bills.
      - Arrears strictly exceed the category threshold.

    Disconnection:
      - At least 15 days have passed after notice.
      - Arrears remain unpaid.
      - Agriculture restriction does not apply.

    Returns a dictionary containing state and reason.
    """
    category = category.upper()
    as_of_date = to_date(as_of_date)
    total_arrears = to_decimal(total_arrears)

    if consecutive_unpaid_bills < 0:
        raise ValueError("Unpaid bill count cannot be negative.")

    if total_arrears < 0:
        raise ValueError("Arrears cannot be negative.")

    if total_arrears == 0:
        return {
            "state": "CONNECTED",
            "reason": "No outstanding arrears.",
            "notice_date": None,
            "disconnection_date": None
        }

    threshold = get_arrears_threshold(category)

    if notice_date is None:
        if (
            consecutive_unpaid_bills > 2
            and total_arrears > threshold
        ):
            return {
                "state": "DISCONNECTION_NOTICE",
                "reason": "Unpaid bill count and arrears exceed the applicable limits.",
                "notice_date": as_of_date,
                "disconnection_date": calculate_disconnection_date(
                    as_of_date
                )
            }

        return {
            "state": "CONNECTED",
            "reason": "Disconnection conditions have not been met.",
            "notice_date": None,
            "disconnection_date": None
        }

    notice_date = to_date(notice_date)
    disconnection_date = calculate_disconnection_date(notice_date)

    if as_of_date < disconnection_date:
        return {
            "state": "DISCONNECTION_NOTICE",
            "reason": "The 15-day notice period has not ended.",
            "notice_date": notice_date,
            "disconnection_date": disconnection_date
        }

    if is_agriculture_disconnection_restricted(
        category,
        as_of_date
    ):
        return {
            "state": "DISCONNECTION_NOTICE",
            "reason": "Agriculture disconnection is restricted from June through November.",
            "notice_date": notice_date,
            "disconnection_date": disconnection_date
        }

    return {
        "state": "DISCONNECTED",
        "reason": "Notice period completed and arrears remain unpaid.",
        "notice_date": notice_date,
        "disconnection_date": disconnection_date
    }


def calculate_reconnection_amount(
    total_arrears,
    security_deposit,
    average_monthly_bill
):
    """
    Calculate the amount required for reconnection:

    Full arrears
    + Rs. 250 reconnection fee
    + security deposit top-up to two months' average bills.
    """
    total_arrears = to_decimal(total_arrears)
    security_deposit = to_decimal(security_deposit)
    average_monthly_bill = to_decimal(average_monthly_bill)

    if (
        total_arrears < 0
        or security_deposit < 0
        or average_monthly_bill < 0
    ):
        raise ValueError("Amounts cannot be negative.")

    required_deposit = average_monthly_bill * 2

    deposit_top_up = max(
        ZERO,
        required_deposit - security_deposit
    )

    return {
        "arrears": round_money(total_arrears),
        "reconnection_fee": RECONNECTION_FEE,
        "deposit_top_up": round_money(deposit_top_up),
        "total_required": round_money(
            total_arrears
            + RECONNECTION_FEE
            + deposit_top_up
        )
    }


def evaluate_reconnection(
    amount_paid,
    total_arrears,
    security_deposit,
    average_monthly_bill
):
    """
    Check whether the consumer has paid the complete
    reconnection amount.

    Returns RECONNECTED only when the full amount is paid.
    """
    amount_paid = to_decimal(amount_paid)

    if amount_paid < 0:
        raise ValueError("Payment cannot be negative.")

    requirement = calculate_reconnection_amount(
        total_arrears,
        security_deposit,
        average_monthly_bill
    )

    if amount_paid >= requirement["total_required"]:
        return {
            "state": "RECONNECTED",
            "required_amount": requirement["total_required"],
            "amount_paid": round_money(amount_paid),
            "shortfall": ZERO
        }

    return {
        "state": "DISCONNECTED",
        "required_amount": requirement["total_required"],
        "amount_paid": round_money(amount_paid),
        "shortfall": round_money(
            requirement["total_required"] - amount_paid
        )
    }
