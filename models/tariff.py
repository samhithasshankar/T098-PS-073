#This represents tariff orders and slab rates.
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from models.enums import ConsumerCategory


@dataclass
class Slab:
    upper_limit: Decimal | None
    rate: Decimal

    def __post_init__(self):
        if self.upper_limit is not None:
            self.upper_limit = Decimal(str(self.upper_limit))

        self.rate = Decimal(str(self.rate))

        if self.upper_limit is not None and self.upper_limit <= 0:
            raise ValueError("Slab limit must be positive.")

        if self.rate < 0:
            raise ValueError("Slab rate cannot be negative.")


@dataclass
class Tariff:
    tariff_id: str
    effective_from: date

    slabs: dict = field(default_factory=dict)
    fixed_charge_per_kw: dict = field(default_factory=dict)
    fac_per_unit: Decimal = Decimal("0.35")
    duty_percent: dict = field(default_factory=dict)
    minimum_charge: dict = field(default_factory=dict)

    def __post_init__(self):
        self.fac_per_unit = Decimal(str(self.fac_per_unit))

        if self.fac_per_unit < 0:
            raise ValueError("FAC cannot be negative.")

        self.slabs = {
            ConsumerCategory(category): [
                slab if isinstance(slab, Slab)
                else Slab(*slab)
                for slab in slab_list
            ]
            for category, slab_list in self.slabs.items()
        }

        self.fixed_charge_per_kw = {
            ConsumerCategory(category): Decimal(str(amount))
            for category, amount in self.fixed_charge_per_kw.items()
        }

        self.duty_percent = {
            ConsumerCategory(category): Decimal(str(rate))
            for category, rate in self.duty_percent.items()
        }

        self.minimum_charge = {
            ConsumerCategory(category): Decimal(str(amount))
            for category, amount in self.minimum_charge.items()
        }

        for category, slabs in self.slabs.items():
            if not slabs:
                raise ValueError(
                    f"No tariff slabs configured for {category.value}"
                )

            for index, slab in enumerate(slabs):
                if index > 0:
                    previous = slabs[index - 1]

                    if previous.upper_limit is None:
                        raise ValueError(
                            "An unlimited slab must be the final slab."
                        )

                    if (
                        slab.upper_limit is not None
                        and slab.upper_limit <= previous.upper_limit
                    ):
                        raise ValueError(
                            "Tariff slab limits must be increasing."
                        )

            if slabs[-1].upper_limit is not None:
                raise ValueError(
                    "The final tariff slab must have no upper limit."
                )