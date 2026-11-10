
from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_bpl_benefit(consumer, total_units, fixed_charge):
    """
    BR-09:
    BPL consumers receive their first 50 units free.

    If total consumption is 100 units or less,
    fixed charge is also waived.
    """

    units = Decimal(str(total_units))
    fixed = money(fixed_charge)

    if units < 0:
        raise ValueError("Consumption cannot be negative.")

    if fixed < ZERO:
        raise ValueError("Fixed charge cannot be negative.")

    if not consumer["bpl"]:
        return {
            "free_units": Decimal("0"),
            "units_for_energy_charge": units,
            "fixed_charge_after_benefit": fixed,
        }

    free_units = min(units, Decimal("50"))
    billable_units = units - free_units

    if units <= Decimal("100"):
        fixed_after_benefit = ZERO
    else:
        fixed_after_benefit = fixed

    return {
        "free_units": free_units,
        "units_for_energy_charge": billable_units,
        "fixed_charge_after_benefit": fixed_after_benefit,
    }


def calculate_payment_rebate(
    bill_date,
    payment_date,
    payment_mode,
    discountable_amount
):
    """
    BR-09:
    Prompt-payment rebate:
    1% within seven days, capped at Rs 100.

    Additional ONLINE rebate:
    0.5%, capped at Rs 50.

    discountable_amount is the eligible bill amount supplied
    by the billing/ledger integration.
    """

    amount = money(discountable_amount)

    if amount < ZERO:
        raise ValueError("Discountable amount cannot be negative.")

    if payment_mode not in {"ONLINE", "COUNTER"}:
        raise ValueError("Unsupported payment mode.")

    days_after_bill = (payment_date - bill_date).days

    prompt_rebate = ZERO
    online_rebate = ZERO

    if 0 <= days_after_bill <= 7:
        prompt_rebate = min(
            money(amount * Decimal("0.01")),
            Decimal("100.00")
        )

        if payment_mode == "ONLINE":
            online_rebate = min(
                money(amount * Decimal("0.005")),
                Decimal("50.00")
            )

    return {
        "prompt_rebate": prompt_rebate,
        "online_rebate": online_rebate,
        "total_rebate": money(prompt_rebate + online_rebate),
    }
