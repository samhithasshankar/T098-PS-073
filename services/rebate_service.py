
from datetime import date, datetime, time
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
MONEY_PLACES = Decimal("0.01")

PROMPT_REBATE_RATE = Decimal("0.01")
PROMPT_REBATE_CAP = Decimal("100.00")

ONLINE_REBATE_RATE = Decimal("0.005")
ONLINE_REBATE_CAP = Decimal("50.00")

PROMPT_REBATE_DAYS = 7


def to_decimal(value):
    """Convert a value to Decimal safely."""
    return Decimal(str(value or 0))


def round_money(value):
    """Round a monetary value to two decimal places."""
    return to_decimal(value).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def to_date(value):
    """Convert a date, datetime or ISO date string into date."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(str(value).strip()[:10])


def to_datetime(value):
    """Convert a date, datetime or ISO timestamp into datetime."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    value = str(value).strip()

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.combine(
            date.fromisoformat(value[:10]),
            time.min,
        )


def calculate_prompt_rebate(eligible_amount, bill_date, payment_ts):
    """
    Calculate the prompt-payment rebate.

    The payment qualifies when it is made from the bill date
    through the seventh calendar day after the bill date,
    inclusive.

    The caller must supply the eligible amount. This function
    does not decide whether that amount means the original bill
    amount or the amount actually paid.
    """
    eligible_amount = round_money(eligible_amount)
    bill_date = to_date(bill_date)
    payment_ts = to_datetime(payment_ts)

    if eligible_amount < ZERO:
        raise ValueError("Eligible amount cannot be negative.")

    payment_date = payment_ts.date()
    days_after_bill = (payment_date - bill_date).days

    if not 0 <= days_after_bill <= PROMPT_REBATE_DAYS:
        return ZERO

    rebate = eligible_amount * PROMPT_REBATE_RATE

    return min(
        round_money(rebate),
        PROMPT_REBATE_CAP,
    )


def calculate_online_rebate(eligible_amount, mode):
    """
    Calculate the additional online-payment rebate.

    The caller must supply the eligible amount used as the
    calculation base.
    """
    eligible_amount = round_money(eligible_amount)
    mode = str(mode).strip().upper()

    if eligible_amount < ZERO:
        raise ValueError("Eligible amount cannot be negative.")

    if mode not in ("ONLINE", "COUNTER"):
        raise ValueError(f"Invalid payment mode: {mode}")

    if mode != "ONLINE":
        return ZERO

    rebate = eligible_amount * ONLINE_REBATE_RATE

    return min(
        round_money(rebate),
        ONLINE_REBATE_CAP,
    )


def calculate_payment_rebates(
    eligible_amount,
    bill_date,
    payment_ts,
    mode,
):
    """
    Calculate prompt and online rebates separately.

    Returns:
        {
            "prompt_rebate": Decimal,
            "online_rebate": Decimal,
            "total_rebate": Decimal
        }

    The same eligible_amount is used as the base for both
    rebate calculations. The caller is responsible for
    supplying the correct base under the confirmed billing rule.
    """
    prompt_rebate = calculate_prompt_rebate(
        eligible_amount,
        bill_date,
        payment_ts,
    )

    online_rebate = calculate_online_rebate(
        eligible_amount,
        mode,
    )

    total_rebate = round_money(
        prompt_rebate + online_rebate
    )

    return {
        "prompt_rebate": prompt_rebate,
        "online_rebate": online_rebate,
        "total_rebate": total_rebate,
    }
