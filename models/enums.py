#defines the allowed consumer categories, meter types, reading statuses and ToD zones.
from enum import Enum


class ConsumerCategory(str, Enum):
    DOMESTIC = "DOMESTIC"
    COMMERCIAL = "COMMERCIAL"
    INDUSTRIAL_LT = "INDUSTRIAL_LT"
    AGRICULTURE = "AGRICULTURE"


class MeterType(str, Enum):
    NORMAL = "NORMAL"
    TOD = "TOD"
    NET = "NET"


class ReadingStatus(str, Enum):
    NORMAL = "NORMAL"
    ESTIMATED = "ESTIMATED"
    FAULTY = "FAULTY"
    METER_CHANGE = "METER_CHANGE"


class TODZone(str, Enum):
    PEAK = "PEAK"
    OFF_PEAK = "OFF_PEAK"
    NORMAL = "NORMAL"