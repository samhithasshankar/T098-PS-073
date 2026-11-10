
from decimal import Decimal, ROUND_HALF_UP

from services.benefit_service import calculate_bpl_benefit
from services.fixed_charge_service import calculate_fixed_and_demand_charges
from services.minimum_charge_service import calculate_minimum_charge
from services.net_metering_service import calculate_net_metering
from services.slab_calculator import calculate_slab_breakdown
from services.tax_service import calculate_fac_and_duty
from services.tod_service import calculate_tod_adjustment


ZERO = Decimal("0")
MONEY_ZERO = Decimal("0.00")
TWO_PLACES = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP
    )


def units(value, field_name):
    result = Decimal(str(value))

    if result < ZERO:
        raise ValueError(f"{field_name} cannot be negative.")

    if result != result.to_integral_value():
        raise ValueError(
            f"{field_name} must be a whole number of kWh."
        )

    return result


def calculate_period_bill(
    consumer,
    tariff,
    period_days,
    import_units,
    export_units=0,
    opening_banked_units=0,
    bill_date=None,
    max_demand_kw=None,
    tod_peak_kwh=0,
    tod_offpeak_kwh=0,
    tod_normal_kwh=0,
    is_faulty=False,
):
    """
    Calculate charges for one billing period.

    Inputs must contain period consumption values, not cumulative
    meter register readings.

    Reading processing, payments, arrears, tariff changes within
    a period and long-period splitting are handled separately.
    """

    if not isinstance(period_days, int) or period_days <= 0:
        raise ValueError("period_days must be a positive integer.")

    category = consumer["category"]

    imported = units(import_units, "import_units")
    exported = units(export_units, "export_units")
    peak = units(tod_peak_kwh, "tod_peak_kwh")
    offpeak = units(tod_offpeak_kwh, "tod_offpeak_kwh")
    normal = units(tod_normal_kwh, "tod_normal_kwh")

    # 1. Net metering and banked units
    net_result = calculate_net_metering(
        consumer=consumer,
        tariff=tariff,
        import_units=imported,
        export_units=exported,
        opening_banked_units=opening_banked_units,
        bill_date=bill_date,
    )

    billed_units_decimal = net_result["units_billed"]
    billed_units = int(billed_units_decimal)

    # 2. Fixed charge and excess demand
    fixed_result = calculate_fixed_and_demand_charges(
        consumer,
        tariff,
        max_demand_kw=max_demand_kw,
    )

    # 3. BPL benefit
    bpl_value = consumer.get("bpl", False)

    is_bpl = (
        bpl_value is True
        or str(bpl_value).strip().lower() == "true"
    )

    benefit_consumer = {
        **consumer,
        "bpl": is_bpl
    }

    bpl_result = calculate_bpl_benefit(
        benefit_consumer,
        billed_units_decimal,
        fixed_result["fixed_charge"],
    )

    energy_units = int(
        bpl_result["units_for_energy_charge"]
    )

    fixed_charge = bpl_result["fixed_charge_after_benefit"]

    # 4. Slab energy calculation
    slab_result = calculate_slab_breakdown(
        energy_units,
        tariff["slabs"][category],
        period_days=period_days,
    )

    energy_charge = slab_result["energy_charge"]

    # 5. Time-of-Day adjustment
    tod_result = calculate_tod_adjustment(
        consumer=consumer,
        tariff=tariff,
        energy_charge=energy_charge,
        tod_peak_kwh=peak,
        tod_offpeak_kwh=offpeak,
        tod_normal_kwh=normal,
    )

    adjusted_energy = money(
        energy_charge + tod_result["tod_adjustment"]
    )

    # 6. Minimum charge
    minimum_result = calculate_minimum_charge(
        category=category,
        tariff=tariff,
        energy_charge=adjusted_energy,
        fixed_charge=fixed_charge,
        is_faulty=is_faulty,
    )

    # 7. FAC and duty
    tax_result = calculate_fac_and_duty(
        category=category,
        tariff=tariff,
        units_billed=billed_units_decimal,
        energy_charge=adjusted_energy,
        fixed_charge=fixed_charge,
    )

    # 8. Agriculture subsidy
    subsidy = MONEY_ZERO

    if category == "AGRICULTURE":
        pump_hp = Decimal(
            str(consumer.get("pump_hp") or 0)
        )

        hp_limit = Decimal(
            str(tariff["agri_subsidy_hp_limit"])
        )

        if pump_hp <= hp_limit:
            subsidy = money(energy_charge)

    minimum_adjustment = (
        minimum_result["minimum_charge_adjustment"]
    )

    excess_demand_charge = (
        fixed_result["excess_demand_charge"]
    )

    settlement_credit = net_result["settlement_credit"]

    # 9. Final current bill amount
    net_current = money(
        adjusted_energy
        + fixed_charge
        + excess_demand_charge
        + tax_result["fac"]
        + tax_result["duty"]
        + minimum_adjustment
        - subsidy
        - settlement_credit
    )

    net_current = max(MONEY_ZERO, net_current)

    # 10. Billing flags
    flags = set()

    if net_result["flag"]:
        flags.add(net_result["flag"])

    if fixed_result["excess_demand_flag"]:
        flags.add("LOAD_REGULARISATION")

    if minimum_adjustment > ZERO:
        flags.add("MINIMUM_APPLIED")

    if is_faulty:
        flags.add("FAULTY_AVERAGE")

    return {
        "units_imported": int(imported),
        "units_exported": int(exported),
        "units_billed": billed_units,
        "energy_units": energy_units,
        "banked_used": net_result["banked_used"],
        "banked_closing": net_result["banked_closing"],
        "settled_units": net_result["settled_units"],
        "settlement_credit": settlement_credit,
        "energy_charge": energy_charge,
        "tod_adjustment": tod_result["tod_adjustment"],
        "fixed_charge": fixed_charge,
        "excess_demand_charge": excess_demand_charge,
        "fac": tax_result["fac"],
        "duty": tax_result["duty"],
        "subsidy": subsidy,
        "minimum_charge_adjustment": minimum_adjustment,
        "reconciliation_adjustment": MONEY_ZERO,
        "net_current": net_current,
        "slab_breakdown": slab_result["slab_breakdown"],
        "flags": sorted(flags),
        "details": {
            "net_metering": net_result,
            "bpl": bpl_result,
            "fixed_and_demand": fixed_result,
            "tod": tod_result,
            "minimum_charge": minimum_result,
            "tax": tax_result,
        },
    }
