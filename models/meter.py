#representation of a meter in the system
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from models.enums import MeterType


@dataclass
class Meter:
    meter_id: str
    consumer_id: str
    meter_type: MeterType
    installed_on: date
    solar_capacity_kw: Decimal = Decimal("0")

    def __post_init__(self):
        self.solar_capacity_kw = Decimal(
            str(self.solar_capacity_kw)
        )

        if not self.meter_id.strip():
            raise ValueError("Meter ID cannot be empty.")

        if not self.consumer_id.strip():
            raise ValueError("Consumer ID cannot be empty.")

        if not isinstance(self.meter_type, MeterType):
            self.meter_type = MeterType(self.meter_type)

        if self.solar_capacity_kw < 0:
            raise ValueError("Solar capacity cannot be negative.")