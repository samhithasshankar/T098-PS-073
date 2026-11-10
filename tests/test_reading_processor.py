
from utils.data_loader import load_all_data
from services.reading_processor import process_all_readings


def get_processed_readings():
    data = load_all_data()
    return process_all_readings(data["readings"])


def find_reading(processed, reading_id):
    return next(
        item for item in processed
        if item["reading_id"] == reading_id
    )


def test_opening_readings_are_not_billed():
    data = load_all_data()

    processed = process_all_readings(data["readings"])

    assert len(processed) == 1399


def test_domestic_exact_slab_boundary_consumption():
    processed = get_processed_readings()

    expected = {
        "RD-00301": 50,
        "RD-00401": 100,
        "RD-00501": 200,
        "RD-00600": 300,
    }

    for reading_id, expected_units in expected.items():
        result = find_reading(processed, reading_id)

        assert result["consumption_units"] == expected_units


def test_28_day_period():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00654")

    assert result["period_days"] == 28
    assert result["consumption_units"] == 180


def test_34_day_period():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00781")

    assert result["period_days"] == 34
    assert result["consumption_units"] == 240


def test_long_period_is_split():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00698")

    assert result["period_days"] == 62
    assert result["consumption_units"] == 410
    assert len(result["segments"]) == 2

    assert result["segments"][0]["days"] == 30
    assert result["segments"][1]["days"] == 32

    assert (
        result["segments"][0]["units"]
        + result["segments"][1]["units"]
        == 410
    )


def test_faulty_reading_uses_last_three_normal_bills():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00493")

    assert result["status"] == "FAULTY"
    assert result["consumption_units"] == 260
    assert result["is_faulty"] is True


def test_normal_after_faulty_marks_reconciliation():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00595")

    assert result["consumption_units"] == 220
    assert result["reconciliation_required"] is True
    assert result["reconciliation_actual_units"] == 220


def test_meter_change_consumption():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00622")

    assert result["status"] == "METER_CHANGE"
    assert result["consumption_units"] == 557


def test_normal_reading_max_demand_is_retained():
    processed = get_processed_readings()

    result = find_reading(processed, "RD-00827")

    assert str(result["max_demand_kw"]) == "5.50"
