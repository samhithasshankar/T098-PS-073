
import csv

from reports.csv_report_service import write_report, REPORT_COLUMNS


def test_arrears_ageing_csv_has_official_columns(tmp_path):
    rows = [
        {
            "as_of_date": "2026-10-28",
            "consumer_id": "CON-0001",
            "bucket_0_30": "100.00",
            "bucket_31_60": "0.00",
            "bucket_61_90": "0.00",
            "bucket_over_90": "0.00",
            "total": "100.00",
        }
    ]

    path = write_report(
        "arrears_ageing.csv",
        rows,
        output_dir=tmp_path,
    )

    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        result = list(reader)

    assert reader.fieldnames == REPORT_COLUMNS["arrears_ageing.csv"]
    assert len(result) == 1
    assert result[0]["consumer_id"] == "CON-0001"
    assert result[0]["total"] == "100.00"


def test_report_writer_creates_header_for_empty_report(tmp_path):
    path = write_report(
        "arrears_ageing.csv",
        [],
        output_dir=tmp_path,
    )

    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        assert next(reader) == REPORT_COLUMNS["arrears_ageing.csv"]
        assert list(reader) == []


def test_report_writer_rejects_unknown_filename(tmp_path):
    try:
        write_report("unknown.csv", [], output_dir=tmp_path)
    except ValueError as error:
        assert "Unsupported report filename" in str(error)
    else:
        raise AssertionError("Expected ValueError")
