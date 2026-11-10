
from decimal import Decimal


ZERO = Decimal("0")


def decimal_value(value):
    if value is None or str(value).strip() == "":
        return None

    return Decimal(str(value))


def calculate_normal_consumption(previous_reading, current_reading):
    """
    Calculate consumption from two cumulative NORMAL readings.
    """

    previous = decimal_value(previous_reading)
    current = decimal_value(current_reading)

    if previous is None or current is None:
        raise ValueError("NORMAL readings cannot be empty.")

    consumption = current - previous

    if consumption < ZERO:
        raise ValueError(
            "Current cumulative reading cannot be below previous reading."
        )

    return consumption


def calculate_average_normal_consumption(normal_consumptions):
    """
    Calculate the average of the last three NORMAL billing consumptions.
    """

    if len(normal_consumptions) < 3:
        raise ValueError(
            "Three previous NORMAL billing consumptions are required."
        )

    last_three = [
        decimal_value(value)
        for value in normal_consumptions[-3:]
    ]

    if any(value is None or value < ZERO for value in last_three):
        raise ValueError("NORMAL consumption history is invalid.")

    return sum(last_three, ZERO) / Decimal("3")


def calculate_estimated_consumption(normal_consumptions):
    """
    BR-08: ESTIMATED consumption uses the average
    of the last three NORMAL billing consumptions.
    """

    return calculate_average_normal_consumption(normal_consumptions)


def calculate_faulty_consumption(normal_consumptions):
    """
    BR-08: FAULTY consumption uses the average
    of the last three NORMAL billing consumptions.

    The billing engine must separately skip minimum charge
    for this FAULTY billing period.
    """

    return calculate_average_normal_consumption(normal_consumptions)


def calculate_meter_change_consumption(
    previous_reading,
    old_meter_final,
    new_meter_initial,
    new_meter_reading
):
    """
    BR-08: Calculate consumption across a meter replacement.
    """

    previous = decimal_value(previous_reading)
    old_final = decimal_value(old_meter_final)
    new_initial = decimal_value(new_meter_initial)
    new_current = decimal_value(new_meter_reading)

    values = [previous, old_final, new_initial, new_current]

    if any(value is None for value in values):
        raise ValueError("Meter-change readings cannot be empty.")

    old_meter_units = old_final - previous
    new_meter_units = new_current - new_initial

    if old_meter_units < ZERO or new_meter_units < ZERO:
        raise ValueError("Meter-change readings are inconsistent.")

    return old_meter_units + new_meter_units


def calculate_reading_consumption(
    status,
    previous_reading=None,
    current_reading=None,
    normal_consumptions=None,
    old_meter_final=None,
    new_meter_initial=None
):
    """
    Select the correct consumption calculation based on reading status.
    """

    normal_consumptions = normal_consumptions or []

    if status == "NORMAL":
        return calculate_normal_consumption(
            previous_reading,
            current_reading
        )

    if status == "ESTIMATED":
        return calculate_estimated_consumption(normal_consumptions)

    if status == "FAULTY":
        return calculate_faulty_consumption(normal_consumptions)

    if status == "METER_CHANGE":
        return calculate_meter_change_consumption(
            previous_reading,
            old_meter_final,
            new_meter_initial,
            current_reading
        )

    raise ValueError(f"Unsupported reading status: {status}")
