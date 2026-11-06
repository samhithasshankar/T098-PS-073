
from decimal import Decimal, ROUND_HALF_UP
from datetime import date


class Bill:
    def __init__(
        self,
        bill_id,
        consumer_id,
        billing_month,
        previous_reading,
        current_reading,
        fixed_charge=0,
        fac_rate=0,
        electricity_duty_rate=0,
        subsidy=0,
        rebate=0,
        arrears=0,
        late_payment_interest=0,
        peak_units=0,
        off_peak_units=0,
        peak_rate=0,
        off_peak_rate=0,
        imported_units=None,
        exported_units=0,
        banked_units=0,
        other_charges=0
    ):
        self.bill_id = bill_id
        self.consumer_id = consumer_id
        self.billing_month = billing_month

        self.previous_reading = Decimal(str(previous_reading))
        self.current_reading = Decimal(str(current_reading))

        self.fixed_charge = Decimal(str(fixed_charge))
        self.fac_rate = Decimal(str(fac_rate))
        self.electricity_duty_rate = Decimal(str(electricity_duty_rate))

        self.subsidy = Decimal(str(subsidy))
        self.rebate = Decimal(str(rebate))
        self.arrears = Decimal(str(arrears))
        self.late_payment_interest = Decimal(str(late_payment_interest))

        self.peak_units = Decimal(str(peak_units))
        self.off_peak_units = Decimal(str(off_peak_units))
        self.peak_rate = Decimal(str(peak_rate))
        self.off_peak_rate = Decimal(str(off_peak_rate))

        self.imported_units = (
            None if imported_units is None
            else Decimal(str(imported_units))
        )
        self.exported_units = Decimal(str(exported_units))
        self.banked_units = Decimal(str(banked_units))

        self.other_charges = Decimal(str(other_charges))

        self.energy_charge = Decimal("0")
        self.fac_charge = Decimal("0")
        self.duty_charge = Decimal("0")
        self.net_units = Decimal("0")
        self.total_amount = Decimal("0")
        self.bill_status = "UNPAID"

        self.created_date = date.today()

    @staticmethod
    def money(value):
        return Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    @property
    def units_consumed(self):
        return self.current_reading - self.previous_reading

    def calculate_net_units(self):
        if self.imported_units is not None:
            net = self.imported_units - self.exported_units
        else:
            net = self.units_consumed - self.exported_units

        available_units = net + self.banked_units

        self.net_units = max(Decimal("0"), available_units)
        return self.net_units

    def calculate_tod_charge(self):
        peak_charge = self.peak_units * self.peak_rate
        off_peak_charge = self.off_peak_units * self.off_peak_rate

        return self.money(peak_charge + off_peak_charge)

    def calculate_slab_charge(self, slabs):
        """
        slabs format:
        [
            (100, 3.00),
            (200, 5.00),
            (None, 7.00)
        ]

        Slabs are telescopic.
        None represents unlimited units.
        """
        units = self.calculate_net_units()
        remaining_units = units
        previous_limit = Decimal("0")
        total_charge = Decimal("0")

        for limit, rate in slabs:
            rate = Decimal(str(rate))

            if limit is None:
                slab_units = remaining_units
            else:
                limit = Decimal(str(limit))
                slab_units = min(
                    remaining_units,
                    limit - previous_limit
                )

            if slab_units > 0:
                total_charge += slab_units * rate
                remaining_units -= slab_units

            if limit is not None:
                previous_limit = limit

            if remaining_units <= 0:
                break

        self.energy_charge = self.money(total_charge)
        return self.energy_charge

    def calculate_fac(self):
        self.fac_charge = self.money(
            self.net_units * self.fac_rate
        )
        return self.fac_charge

    def calculate_duty(self):
        taxable_amount = (
            self.energy_charge
            + self.fixed_charge
            + self.fac_charge
        )

        self.duty_charge = self.money(
            taxable_amount * self.electricity_duty_rate / 100
        )

        return self.duty_charge

    def generate_bill(self, slabs=None, use_tod=False):
        if self.units_consumed < 0:
            raise ValueError("Current reading cannot be less than previous reading.")

        if self.exported_units < 0 or self.banked_units < 0:
            raise ValueError("Exported and banked units cannot be negative.")

        if use_tod:
            self.net_units = self.calculate_net_units()
            self.energy_charge = self.calculate_tod_charge()
        else:
            if slabs is None:
                raise ValueError("Slab rates are required for slab billing.")

            self.calculate_slab_charge(slabs)

        self.calculate_fac()
        self.calculate_duty()

        gross_amount = (
            self.energy_charge
            + self.fixed_charge
            + self.fac_charge
            + self.duty_charge
            + self.other_charges
        )

        final_amount = (
            gross_amount
            - self.subsidy
            - self.rebate
            + self.arrears
            + self.late_payment_interest
        )

        self.total_amount = self.money(max(Decimal("0"), final_amount))

        return self.total_amount

    def record_payment(self, amount):
        amount = self.money(amount)

        if amount <= 0:
            raise ValueError("Payment amount must be positive.")

        if amount > self.total_amount:
            raise ValueError("Payment cannot exceed the outstanding bill amount.")

        self.total_amount = self.money(self.total_amount - amount)

        if self.total_amount == 0:
            self.bill_status = "PAID"
        else:
            self.bill_status = "PARTIALLY PAID"

        return self.total_amount

    def get_bill_details(self):
        return {
            "bill_id": self.bill_id,
            "consumer_id": self.consumer_id,
            "billing_month": self.billing_month,
            "previous_reading": str(self.previous_reading),
            "current_reading": str(self.current_reading),
            "units_consumed": str(self.units_consumed),
            "net_units": str(self.net_units),
            "energy_charge": str(self.energy_charge),
            "fixed_charge": str(self.fixed_charge),
            "fac_charge": str(self.fac_charge),
            "duty_charge": str(self.duty_charge),
            "subsidy": str(self.subsidy),
            "rebate": str(self.rebate),
            "arrears": str(self.arrears),
            "late_payment_interest": str(self.late_payment_interest),
            "other_charges": str(self.other_charges),
            "total_amount": str(self.total_amount),
            "bill_status": self.bill_status
        }

    def __str__(self):
        return (
            f"Bill ID: {self.bill_id}\n"
            f"Consumer ID: {self.consumer_id}\n"
            f"Billing Month: {self.billing_month}\n"
            f"Units Consumed: {self.units_consumed}\n"
            f"Net Units: {self.net_units}\n"
            f"Total Amount: Rs. {self.total_amount}\n"
            f"Status: {self.bill_status}"
        )
