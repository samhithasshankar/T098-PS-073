from models.enums import ConsumerCategory, MeterType
from models.consumer import Consumer
from models.meter import Meter
from models.reading import MeterReading
from models.tariff import Tariff, Slab

print("Electricity Billing Engine")
print("--------------------------")
print("Consumer categories:", [c.value for c in ConsumerCategory])
print("Meter types:", [m.value for m in MeterType])
print("All model imports successful!")