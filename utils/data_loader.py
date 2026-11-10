
import csv
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal, InvalidOperation


# Project data directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def read_csv(filename):
    """
    Read a CSV file and return its rows as dictionaries.
    """
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required input file not found: {file_path}"
        )

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        return list(reader)


def read_commands():
    """
    Read commands in their original file order.
    Ignore blank lines and comments.
    """
    file_path = DATA_DIR / "commands.txt"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required input file not found: {file_path}"
        )

    commands = []

    with file_path.open(
        mode="r",
        encoding="utf-8-sig"
    ) as file:

        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split("|")

            commands.append({
                "line_number": line_number,
                "command": parts[0].strip(),
                "arguments": [
                    part.strip() for part in parts[1:]
                ]
            })

    return commands


def to_decimal(value, field_name="value"):
    """
    Safely convert a CSV value to Decimal.
    Empty values are treated as zero only when requested.
    """
    if value is None or str(value).strip() == "":
        return Decimal("0")

    try:
        return Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError(
            f"Invalid decimal in {field_name}: {value}"
        )


def to_optional_decimal(value, field_name="value"):
    """
    Convert a value to Decimal or return None if empty.
    """
    if value is None or str(value).strip() == "":
        return None

    return to_decimal(value, field_name)


def to_integer(value, field_name="value"):
    """
    Convert a CSV value to integer.
    """
    if value is None or str(value).strip() == "":
        return None

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Invalid integer in {field_name}: {value}"
        )


def to_date(value):
    """
    Convert YYYY-MM-DD into a date object.
    """
    return datetime.strptime(
        value.strip(), "%Y-%m-%d"
    ).date()


def to_timestamp(value):
    """
    Convert YYYY-MM-DD HH:MM:SS into a datetime object.
    """
    return datetime.strptime(
        value.strip(), "%Y-%m-%d %H:%M:%S"
    )


def to_boolean(value):
    """
    Convert the supplied true/false values.
    """
    normalized = str(value).strip().lower()

    if normalized == "true":
        return True

    if normalized == "false":
        return False

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


def load_all_data():
    """
    Load every official input file.

    No sample records are generated or modified.
    """

    data = {
        "consumers": read_csv("consumers.csv"),
        "tariff_orders": read_csv("tariff_orders.csv"),
        "tariff_slabs": read_csv("tariff_slabs.csv"),
        "readings": read_csv("readings.csv"),
        "payments": read_csv("payments.csv"),
        "commands": read_commands()
    }

    validate_input_data(data)

    return data


def validate_input_data(data):
    """
    Basic structural and reference validation.
    """

    required_files = [
        "consumers",
        "tariff_orders",
        "tariff_slabs",
        "readings",
        "payments",
        "commands"
    ]

    for name in required_files:
        if name not in data:
            raise ValueError(
                f"Missing input collection: {name}"
            )

    consumers = data["consumers"]
    tariff_orders = data["tariff_orders"]
    tariff_slabs = data["tariff_slabs"]
    readings = data["readings"]
    payments = data["payments"]

    if not consumers:
        raise ValueError("No consumers found.")

    if not tariff_orders:
        raise ValueError("No tariff orders found.")

    if not readings:
        raise ValueError("No meter readings found.")

    if not payments:
        raise ValueError("No payment records found.")

    consumer_ids = {
        row["consumer_id"] for row in consumers
    }

    tariff_ids = {
        row["tariff_id"] for row in tariff_orders
    }

    for row in readings:
        if row["consumer_id"] not in consumer_ids:
            raise ValueError(
                f"Unknown consumer in reading: "
                f"{row['consumer_id']}"
            )

    for row in payments:
        if row["consumer_id"] not in consumer_ids:
            raise ValueError(
                f"Unknown consumer in payment: "
                f"{row['consumer_id']}"
            )

    for row in tariff_slabs:
        if row["tariff_id"] not in tariff_ids:
            raise ValueError(
                f"Unknown tariff in slab: "
                f"{row['tariff_id']}"
            )

    print("Input data validation successful.")


def print_data_summary(data):
    """
    Display the number of records loaded from each file.
    """

    print("\nELECTRICITY BILLING ENGINE")
    print("--------------------------")

    print(
        f"Consumers       : {len(data['consumers'])}"
    )
    print(
        f"Tariff orders   : {len(data['tariff_orders'])}"
    )
    print(
        f"Tariff slabs    : {len(data['tariff_slabs'])}"
    )
    print(
        f"Meter readings  : {len(data['readings'])}"
    )
    print(
        f"Payments        : {len(data['payments'])}"
    )
    print(
        f"Commands        : {len(data['commands'])}"
    )

    print("--------------------------")
    print("All official input files loaded successfully.")
