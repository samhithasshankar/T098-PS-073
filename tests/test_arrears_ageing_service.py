
from services.arrears_ageing_service import generate_arrears_ageing


def test_ageing_places_debt_in_correct_bucket():
    debts = {
        "CON-0001": [
            {
                "bill_id": "BL-001",
                "due_date": "2026-10-01",
                "principal": "1000",
                "interest": "50",
            }
        ]
    }

    result = generate_arrears_ageing(debts, "2026-10-20")

    assert len(result) == 1
    assert result[0]["bucket_0_30"] == 1050
    assert result[0]["total"] == 1050


def test_ageing_excludes_bills_not_yet_due():
    debts = {
        "CON-0001": [
            {
                "bill_id": "BL-001",
                "due_date": "2026-10-25",
                "principal": "1000",
                "interest": "0",
            }
        ]
    }

    result = generate_arrears_ageing(debts, "2026-10-20")

    assert result[0]["total"] == 0


def test_ageing_uses_all_four_buckets():
    debts = {
        "CON-0001": [
            {
                "bill_id": "BL-001",
                "due_date": "2026-10-20",
                "principal": "100",
                "interest": "0",
            },
            {
                "bill_id": "BL-002",
                "due_date": "2026-09-20",
                "principal": "200",
                "interest": "0",
            },
            {
                "bill_id": "BL-003",
                "due_date": "2026-08-20",
                "principal": "300",
                "interest": "0",
            },
            {
                "bill_id": "BL-004",
                "due_date": "2026-07-20",
                "principal": "400",
                "interest": "0",
            },
        ]
    }

    result = generate_arrears_ageing(debts, "2026-10-20")[0]

    assert result["bucket_0_30"] == 100
    assert result["bucket_31_60"] == 200
    assert result["bucket_61_90"] == 300
    assert result["bucket_over_90"] == 400
    assert result["total"] == 1000


def test_ageing_returns_zero_for_empty_consumer_debts():
    result = generate_arrears_ageing(
        {"CON-0001": []},
        "2026-10-20",
    )

    assert result[0]["total"] == 0
