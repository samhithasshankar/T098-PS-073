
from decimal import Decimal, ROUND_HALF_UP


ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def units(value):
    return Decimal(str(value))


def calculate_net_metering(
    consumer,
    tariff,
    import_units,
    export_units,
    opening_banked_units=0,
    bill_date=None
):
    """
    BR-07: Net-metering calculation.

    Eligible NET consumers:
    - Current exports offset current imports.
    - Excess exports are added to the bank.
    - Previously banked units offset remaining net imports.
    - Remaining banked units are settled in March.

    Ineligible NET consumers:
    - Solar capacity greater than sanctioned load.
    - Billed on gross import units.
    - Exports and banked units are ignored.
    """

    imported = units(import_units)
    exported = units(export_units)
    opening_bank = units(opening_banked_units)

    if min(imported, exported, opening_bank) < ZERO:
        raise ValueError("Import, export and banked units cannot be negative.")

    if consumer["meter_type"] != "NET":
        return {
            "eligible": False,
            "units_billed": imported,
            "banked_used": ZERO,
            "banked_closing": ZERO,
            "settlement_credit": ZERO,
            "settled_units": ZERO,
            "flag": None,
        }

    solar_capacity = units(consumer["solar_capacity_kw"])
    sanctioned_load = units(consumer["sanctioned_load_kw"])

    if solar_capacity > sanctioned_load:
        return {
            "eligible": False,
            "units_billed": imported,
            "banked_used": ZERO,
            "banked_closing": ZERO,
            "settlement_credit": ZERO,
            "settled_units": ZERO,
            "flag": "INELIGIBLE_NET",
        }

    net_units = imported - exported

    if net_units < ZERO:
        current_banked_units = opening_bank + abs(net_units)
        units_to_bill = ZERO
        banked_used = ZERO
    else:
        banked_used = min(opening_bank, net_units)
        units_to_bill = net_units - banked_used
        current_banked_units = opening_bank - banked_used

    settled_units = ZERO
    settlement_credit = ZERO

    if bill_date is not None and bill_date.month == 3:
        settled_units = current_banked_units

        settlement_rate = units(tariff["net_settlement_rate"])

        settlement_credit = money(
            settled_units * settlement_rate
        )

        current_banked_units = ZERO

    return {
        "eligible": True,
        "units_billed": units_to_bill,
        "banked_used": banked_used,
        "banked_closing": current_banked_units,
        "settlement_credit": settlement_credit,
        "settled_units": settled_units,
        "flag": None,
    }
