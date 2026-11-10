
from datetime import date

from utils.data_loader import load_all_data
from services.tariff_service import build_tariff_catalog
from services.tariff_period_service import split_period_by_tariff


def get_tariffs():
    data = load_all_data()
    return build_tariff_catalog(data)


def test_tariff_effective_on_reading_date():
    tariffs = get_tariffs()

    result = split_period_by_tariff(
        period_from=date(2026, 3, 10),
        period_to=date(2026, 4, 10),
        total_units=310,
        tariff_catalog=tariffs,
    )

    assert len(result) == 2

    assert result[0]["tariff_id"] == "TO-2025"
    assert result[0]["days"] == 30

    assert result[1]["tariff_id"] == "TO-2026"
    assert result[1]["days"] == 1

    assert sum(item["units"] for item in result) == 310


def test_period_before_tariff_change():
    tariffs = get_tariffs()

    result = split_period_by_tariff(
        period_from=date(2026, 2, 10),
        period_to=date(2026, 3, 10),
        total_units=200,
        tariff_catalog=tariffs,
    )

    assert len(result) == 1
    assert result[0]["tariff_id"] == "TO-2025"
    assert result[0]["units"] == 200


def test_period_after_tariff_change():
    tariffs = get_tariffs()

    result = split_period_by_tariff(
        period_from=date(2026, 4, 10),
        period_to=date(2026, 5, 10),
        total_units=200,
        tariff_catalog=tariffs,
    )

    assert len(result) == 1
    assert result[0]["tariff_id"] == "TO-2026"
    assert result[0]["units"] == 200


def test_consumption_is_preserved_after_split():
    tariffs = get_tariffs()

    result = split_period_by_tariff(
        period_from=date(2026, 3, 10),
        period_to=date(2026, 4, 10),
        total_units=220,
        tariff_catalog=tariffs,
    )

    assert sum(item["units"] for item in result) == 220


def test_invalid_period_is_rejected():
    tariffs = get_tariffs()

    try:
        split_period_by_tariff(
            period_from=date(2026, 4, 10),
            period_to=date(2026, 3, 10),
            total_units=100,
            tariff_catalog=tariffs,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid period should be rejected.")
