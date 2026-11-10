
from decimal import Decimal

import pytest

from services.reading_service import (
    calculate_normal_consumption,
    calculate_average_normal_consumption,
    calculate_estimated_consumption,
    calculate_faulty_consumption,
    calculate_meter_change_consumption,
    calculate_reading_consumption,
)


def test_normal_consumption():
    result = calculate_normal_consumption(1000, 1120)

    assert result == Decimal("120")


def test_normal_reading_cannot_decrease():
    with pytest.raises(ValueError):
        calculate_normal_consumption(1200, 1100)


def test_average_of_last_three_normal_consumptions():
    result = calculate_average_normal_consumption(
        [100, 200, 300, 400]
    )

    assert result == Decimal("300")


def test_estimated_consumption():
    result = calculate_estimated_consumption(
        [240, 260, 280]
    )

    assert result == Decimal("260")


def test_faulty_consumption():
    result = calculate_faulty_consumption(
        [240, 260, 280]
    )

    assert result == Decimal("260")


def test_three_normal_readings_are_required():
    with pytest.raises(ValueError):
        calculate_estimated_consumption([240, 260])


def test_meter_change_consumption():
    result = calculate_meter_change_consumption(
        previous_reading=1000,
        old_meter_final=1120,
        new_meter_initial=50,
        new_meter_reading=150
    )

    assert result == Decimal("220")


def test_meter_change_rejects_inconsistent_readings():
    with pytest.raises(ValueError):
        calculate_meter_change_consumption(
            previous_reading=1000,
            old_meter_final=900,
            new_meter_initial=50,
            new_meter_reading=150
        )


def test_reading_status_dispatch():
    result = calculate_reading_consumption(
        status="NORMAL",
        previous_reading=1000,
        current_reading=1150
    )

    assert result == Decimal("150")


def test_unknown_reading_status():
    with pytest.raises(ValueError):
        calculate_reading_consumption(status="UNKNOWN")
