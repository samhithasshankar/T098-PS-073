
from datetime import datetime
from decimal import Decimal, InvalidOperation


def decimal_value(value, field_name):
    """Convert a supplied CSV value into Decimal."""

    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(
            f"Invalid value for {field_name}: {value}"
        )


def build_tariff_catalog(data):
    """
    Build tariff orders and category-wise slabs
    using the official CSV data.
    """

    tariff_catalog = {}

    # Load tariff orders
    for row in data["tariff_orders"]:

        tariff_id = row["tariff_id"]

        if tariff_id in tariff_catalog:
            raise ValueError(
                f"Duplicate tariff ID: {tariff_id}"
            )

        tariff_catalog[tariff_id] = {
            "tariff_id": tariff_id,
            "effective_date": datetime.strptime(
                row["effective_date"], "%Y-%m-%d"
            ).date(),

            "fac_per_unit": decimal_value(
                row["fac_per_unit"], "fac_per_unit"
            ),

            "duty_pct_domestic": decimal_value(
                row["duty_pct_domestic"],
                "duty_pct_domestic"
            ),

            "duty_pct_others": decimal_value(
                row["duty_pct_others"],
                "duty_pct_others"
            ),

            "fixed_domestic_per_kw": decimal_value(
                row["fixed_domestic_per_kw"],
                "fixed_domestic_per_kw"
            ),

            "fixed_commercial_per_kw": decimal_value(
                row["fixed_commercial_per_kw"],
                "fixed_commercial_per_kw"
            ),

            "fixed_industrial_per_kw": decimal_value(
                row["fixed_industrial_per_kw"],
                "fixed_industrial_per_kw"
            ),

            "min_charge_domestic": decimal_value(
                row["min_charge_domestic"],
                "min_charge_domestic"
            ),

            "min_charge_others": decimal_value(
                row["min_charge_others"],
                "min_charge_others"
            ),

            "tod_peak_pct": decimal_value(
                row["tod_peak_pct"], "tod_peak_pct"
            ),

            "tod_offpeak_pct": decimal_value(
                row["tod_offpeak_pct"], "tod_offpeak_pct"
            ),

            "net_settlement_rate": decimal_value(
                row["net_settlement_rate"],
                "net_settlement_rate"
            ),

            "agri_subsidy_hp_limit": int(
                row["agri_subsidy_hp_limit"]
            ),

            "slabs": {}
        }

    if not tariff_catalog:
        raise ValueError("No tariff orders found.")

    # Load category-wise tariff slabs
    for row in data["tariff_slabs"]:

        tariff_id = row["tariff_id"]
        category = row["category"]

        if tariff_id not in tariff_catalog:
            raise ValueError(
                f"Unknown tariff ID in slabs: {tariff_id}"
            )

        slab = {
            "slab_no": int(row["slab_no"]),
            "from_unit": int(row["from_unit"]),
            "to_unit": (
                int(row["to_unit"])
                if row["to_unit"].strip()
                else None
            ),
            "rate_per_unit": decimal_value(
                row["rate_per_unit"], "rate_per_unit"
            )
        }

        category_slabs = (
            tariff_catalog[tariff_id]["slabs"]
            .setdefault(category, [])
        )

        category_slabs.append(slab)

    # Sort and validate slab sequences
    for tariff_id, tariff in tariff_catalog.items():

        for category, slabs in tariff["slabs"].items():

            slabs.sort(key=lambda item: item["slab_no"])

            if not slabs:
                raise ValueError(
                    f"No slabs for {tariff_id} / {category}"
                )

            expected_slab_no = 1

            for index, slab in enumerate(slabs):

                if slab["slab_no"] != expected_slab_no:
                    raise ValueError(
                        f"Invalid slab numbering for "
                        f"{tariff_id} / {category}"
                    )

                if slab["from_unit"] < 0:
                    raise ValueError(
                        f"Negative slab start for "
                        f"{tariff_id} / {category}"
                    )

                if slab["rate_per_unit"] < 0:
                    raise ValueError(
                        f"Negative slab rate for "
                        f"{tariff_id} / {category}"
                    )

                if index == 0 and slab["from_unit"] != 0:
                    raise ValueError(
                        f"First slab must start at zero for "
                        f"{tariff_id} / {category}"
                    )

                if index > 0:
                    previous = slabs[index - 1]

                    if previous["to_unit"] is None:
                        raise ValueError(
                            f"Unlimited slab must be last for "
                            f"{tariff_id} / {category}"
                        )

                    if slab["from_unit"] != (
                        previous["to_unit"] + 1
                    ):
                        raise ValueError(
                            f"Gap or overlap in slabs for "
                            f"{tariff_id} / {category}"
                        )

                expected_slab_no += 1

            if slabs[-1]["to_unit"] is not None:
                raise ValueError(
                    f"Last slab must have an empty upper limit "
                    f"for {tariff_id} / {category}"
                )

    # Check tariff effective dates
    ordered_tariffs = sorted(
        tariff_catalog.values(),
        key=lambda item: item["effective_date"]
    )

    for index in range(1, len(ordered_tariffs)):
        if (
            ordered_tariffs[index]["effective_date"]
            <= ordered_tariffs[index - 1]["effective_date"]
        ):
            raise ValueError(
                "Tariff effective dates must be unique "
                "and in increasing order."
            )

    return tariff_catalog


def get_tariff_for_date(tariff_catalog, billing_date):
    """
    Return the tariff effective on the supplied date.

    The effective date is inclusive:
    a tariff applies from 00:00 on its effective date.
    """

    applicable = [
        tariff
        for tariff in tariff_catalog.values()
        if tariff["effective_date"] <= billing_date
    ]

    if not applicable:
        raise ValueError(
            f"No tariff is effective on {billing_date}"
        )

    return max(
        applicable,
        key=lambda item: item["effective_date"]
    )


def get_category_slabs(tariff, category):
    """Return the slabs for the requested consumer category."""

    if category not in tariff["slabs"]:
        raise ValueError(
            f"No slabs found for category {category} "
            f"in tariff {tariff['tariff_id']}"
        )

    return tariff["slabs"][category]


def print_tariff_summary(tariff_catalog):
    """Display tariff orders and their slab categories."""

    print("\nTARIFF CATALOG")
    print("--------------")

    for tariff_id in sorted(
        tariff_catalog,
        key=lambda item: tariff_catalog[item]["effective_date"]
    ):

        tariff = tariff_catalog[tariff_id]

        print(f"\nTariff: {tariff_id}")
        print(
            f"Effective from: {tariff['effective_date']}"
        )
        print(
            f"FAC per unit: Rs {tariff['fac_per_unit']}"
        )

        for category, slabs in tariff["slabs"].items():

            print(f"\n  {category}")

            for slab in slabs:
                upper = (
                    slab["to_unit"]
                    if slab["to_unit"] is not None
                    else "Unlimited"
                )

                print(
                    f"    Slab {slab['slab_no']}: "
                    f"{slab['from_unit']} - {upper} "
                    f"units @ Rs {slab['rate_per_unit']}"
                )

    print("\nTariff catalog loaded successfully.")
