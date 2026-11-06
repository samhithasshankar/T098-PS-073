
from models.enums import ConsumerCategory, MeterType
from models.consumer import Consumer
from models.meter import Meter
from models.reading import MeterReading
from models.tariff import Tariff, Slab
from models.ledger import Ledger
from models.bill import Bill

print("Electricity Billing Engine")
print("--------------------------")

# Test existing model imports
print("Consumer categories:", [c.value for c in ConsumerCategory])
print("Meter types:", [m.value for m in MeterType])

print("\nAll model imports successful!")

# Create consumer ledger
print("\n----- LEDGER TEST -----")

ledger = Ledger("L001", "C001")

# Add electricity bill
ledger.add_bill("B001", 1500)

# Record payment
ledger.record_payment("P001", 1000)

# Add delayed payment interest
ledger.add_interest(50)

# Display ledger statement
ledger.print_statement()

print("\nRemaining Balance: Rs.", ledger.get_balance())

print("\nElectricity Billing Engine executed successfully!")
