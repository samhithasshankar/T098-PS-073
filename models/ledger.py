
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime


class Ledger:
    def __init__(self, ledger_id, consumer_id):
        self.ledger_id = ledger_id
        self.consumer_id = consumer_id

        self.total_debit = Decimal("0.00")
        self.total_credit = Decimal("0.00")
        self.outstanding_balance = Decimal("0.00")

        self.transactions = []

    @staticmethod
    def money(amount):
        return Decimal(str(amount)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    def add_bill(self, bill_id, amount, description="Electricity Bill"):
        amount = self.money(amount)

        if amount <= 0:
            raise ValueError("Bill amount must be positive.")

        self.total_debit += amount
        self.outstanding_balance += amount

        self.transactions.append({
            "transaction_id": len(self.transactions) + 1,
            "date": datetime.now().isoformat(timespec="seconds"),
            "type": "DEBIT",
            "reference_id": bill_id,
            "description": description,
            "amount": amount,
            "balance": self.outstanding_balance
        })

        return self.outstanding_balance

    def record_payment(self, payment_id, amount,
                       description="Electricity Bill Payment"):
        amount = self.money(amount)

        if amount <= 0:
            raise ValueError("Payment amount must be positive.")

        if amount > self.outstanding_balance:
            raise ValueError("Payment exceeds outstanding balance.")

        self.total_credit += amount
        self.outstanding_balance -= amount

        self.transactions.append({
            "transaction_id": len(self.transactions) + 1,
            "date": datetime.now().isoformat(timespec="seconds"),
            "type": "CREDIT",
            "reference_id": payment_id,
            "description": description,
            "amount": amount,
            "balance": self.outstanding_balance
        })

        return self.outstanding_balance

    def add_interest(self, interest_amount):
        interest_amount = self.money(interest_amount)

        if interest_amount < 0:
            raise ValueError("Interest cannot be negative.")

        if interest_amount == 0:
            return self.outstanding_balance

        self.total_debit += interest_amount
        self.outstanding_balance += interest_amount

        self.transactions.append({
            "transaction_id": len(self.transactions) + 1,
            "date": datetime.now().isoformat(timespec="seconds"),
            "type": "DEBIT",
            "reference_id": "INTEREST",
            "description": "Delayed Payment Interest",
            "amount": interest_amount,
            "balance": self.outstanding_balance
        })

        return self.outstanding_balance

    def add_adjustment(self, amount, description):
        amount = self.money(amount)

        if amount == 0:
            raise ValueError("Adjustment cannot be zero.")

        if amount > 0:
            self.total_debit += amount
            self.outstanding_balance += amount
            transaction_type = "DEBIT"
        else:
            amount = abs(amount)

            if amount > self.outstanding_balance:
                raise ValueError("Adjustment exceeds outstanding balance.")

            self.total_credit += amount
            self.outstanding_balance -= amount
            transaction_type = "CREDIT"

        self.transactions.append({
            "transaction_id": len(self.transactions) + 1,
            "date": datetime.now().isoformat(timespec="seconds"),
            "type": transaction_type,
            "reference_id": "ADJUSTMENT",
            "description": description,
            "amount": amount,
            "balance": self.outstanding_balance
        })

        return self.outstanding_balance

    def get_balance(self):
        return self.money(self.outstanding_balance)

    def get_transaction_history(self):
        return self.transactions.copy()

    def get_statement(self):
        return {
            "ledger_id": self.ledger_id,
            "consumer_id": self.consumer_id,
            "total_debit": str(self.total_debit),
            "total_credit": str(self.total_credit),
            "outstanding_balance": str(self.outstanding_balance),
            "transaction_count": len(self.transactions)
        }

    def print_statement(self):
        print("\n========== CONSUMER LEDGER ==========")
        print("Ledger ID:", self.ledger_id)
        print("Consumer ID:", self.consumer_id)
        print("Total Debit: Rs.", self.total_debit)
        print("Total Credit: Rs.", self.total_credit)
        print("Outstanding: Rs.", self.outstanding_balance)

        print("\n--------- TRANSACTION HISTORY ---------")

        for transaction in self.transactions:
            print("--------------------------------------")
            print("Transaction ID:", transaction["transaction_id"])
            print("Date:", transaction["date"])
            print("Type:", transaction["type"])
            print("Reference:", transaction["reference_id"])
            print("Description:", transaction["description"])
            print("Amount: Rs.", transaction["amount"])
            print("Balance: Rs.", transaction["balance"])

        print("======================================")

    def __str__(self):
        return (
            f"Ledger ID: {self.ledger_id}\n"
            f"Consumer ID: {self.consumer_id}\n"
            f"Total Debit: Rs. {self.total_debit}\n"
            f"Total Credit: Rs. {self.total_credit}\n"
            f"Outstanding Balance: Rs. {self.outstanding_balance}"
        )
