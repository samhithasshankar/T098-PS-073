#stores meter readings
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from models.enums import ReadingStatus


@dataclass
class MeterReading:
    consumer_id: str
    reading_date: date
    import_kwh: Decimal
    export_kwh: Decimal = Decimal("0")
    tod_units: dict = field(default_factory=dict)
    status: ReadingStatus = ReadingStatus.NORMAL
    max_demand_kw: Decimal = Decimal("0")
    old_meter_final_kwh: Decimal | None = None
    new_meter_initial_kwh: Decimal | None = None

    def __post_init__(self):
        self.import_kwh = Decimal(str(self.import_kwh))
        self.export_kwh = Decimal(str(self.export_kwh))
        self.max_demand_kw = Decimal(str(self.max_demand_kw))

        self.tod_units = {
            zone: Decimal(str(units))
            for zone, units in self.tod_units.items()
        }

        if self.import_kwh < 0 or self.export_kwh < 0:
            raise ValueError("Meter readings cannot be negative.")

        if self.max_demand_kw < 0:
            raise ValueError("Maximum demand cannot be negative.")

        if not isinstance(self.status, ReadingStatus):
            self.status = ReadingStatus(self.status)

        for zone, units in self.tod_units.items():
            if units < 0:
                raise ValueError(
                    f"Consumption for {zone} cannot be negative."
                )