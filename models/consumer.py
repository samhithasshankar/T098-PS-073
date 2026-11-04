#representation of a consumer in the system
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from models.enums import ConsumerCategory, MeterType


@dataclass
class Consumer:
    consumer_id: str
    name: str
    category: ConsumerCategory
    sanctioned_load_kw: Decimal
    connection_date: date
    meter_type: MeterType
    solar_capacity_kw: Decimal = Decimal("0")
    is_bpl: bool = False
    security_deposit: Decimal = Decimal("0")

    def __post_init__(self):
        self.sanctioned_load_kw = Decimal(
            str(self.sanctioned_load_kw)
        )

        self.solar_capacity_kw = Decimal(
            str(self.solar_capacity_kw)
        )

        self.security_deposit = Decimal(
            str(self.security_deposit)
        )

        if not self.consumer_id.strip():
            raise ValueError("Consumer ID cannot be empty.")

        if not self.name.strip():
            raise ValueError("Consumer name cannot be empty.")

        if self.sanctioned_load_kw <= 0:
            raise ValueError("Sanctioned load must be positive.")

        if self.solar_capacity_kw < 0:
            raise ValueError("Solar capacity cannot be negative.")

        if self.security_deposit < 0:
            raise ValueError("Security deposit cannot be negative.")

        if not isinstance(self.category, ConsumerCategory):
            self.category = ConsumerCategory(self.category)

        if not isinstance(self.meter_type, MeterType):
            self.meter_type = MeterType(self.meter_type)