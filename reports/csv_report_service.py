
"""CSV output helpers for the PS-073 billing engine."""

import csv
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

REPORT_COLUMNS = {
    "bills.csv": [
        "bill_id", "consumer_id", "bill_date", "period_from", "period_to",
        "days", "tariff_ids", "units_billed", "banked_used",
        "banked_closing", "energy_charge", "tod_adjustment",
        "fixed_charge", "excess_demand_charge", "fac", "duty",
        "subsidy", "minimum_charge_adjustment",
        "reconciliation_adjustment", "net_current", "arrears",
        "interest", "total_due", "due_date", "flags",
    ],
    "bill_slabs.csv": [
        "bill_id", "tariff_id", "slab_no", "units", "rate_per_unit", "amount",
    ],
    "ledger.csv": [
        "consumer_id", "entry_ts", "entry_type", "reference",
        "debit", "credit", "balance",
    ],
    "consumer_state.csv": [
        "consumer_id", "event_date", "state", "reason",
    ],
    "arrears_ageing.csv": [
        "as_of_date", "consumer_id", "bucket_0_30", "bucket_31_60",
        "bucket_61_90", "bucket_over_90", "total",
    ],
}


def _serialize(value):
    """Convert supported values into CSV-safe strings."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def write_report(filename, rows, output_dir=None):
    """Write rows using the official output column order."""
    if filename not in REPORT_COLUMNS:
        raise ValueError(f"Unsupported report filename: {filename}")

    columns = REPORT_COLUMNS[filename]
    destination_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / filename

    with destination.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="ignore",
            restval="",
        )
        writer.writeheader()

        for row in rows:
            writer.writerow({
                column: _serialize(row.get(column))
                for column in columns
            })

    return destination


def write_all_reports(reports, output_dir=None):
    """Write each supplied report using its official CSV schema."""
    written = {}

    for filename, rows in reports.items():
        written[filename] = write_report(
            filename,
            rows,
            output_dir=output_dir,
        )

    return written
