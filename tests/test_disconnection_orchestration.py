
from datetime import date, datetime
from decimal import Decimal

import services.command_execution_service as orchestration


def make_debts():
    """Three unpaid bills with total domestic arrears above Rs. 1,000."""
    return [
        {
            "bill_id": "BILL-1",
            "principal": Decimal("400.00"),
            "interest": Decimal("0.00"),
        },
        {
            "bill_id": "BILL-2",
            "principal": Decimal("400.00"),
            "interest": Decimal("0.00"),
        },
        {
            "bill_id": "BILL-3",
            "principal": Decimal("400.00"),
            "interest": Decimal("0.00"),
        },
    ]


def make_data():
    return {
        "consumers": [
            {
                "consumer_id": "CON-TEST-01",
                "category": "DOMESTIC",
                "security_deposit": Decimal("0.00"),
            }
        ],
        "payments": [],
    }


def make_command(command_name, execution_time, arguments=None):
    return {
        "command": command_name,
        "execution_timestamp": execution_time,
        "arguments": arguments or [],
    }


def fake_snapshot(debts):
    return {
        "debts": {"CON-TEST-01": debts},
        "ledger": [],
    }


def test_orchestration_disconnects_exactly_15_days_after_notice(
    monkeypatch,
):
    data = make_data()
    bills = []
    notice_time = datetime(2025, 11, 28, 23, 0)
    later_time = datetime(2025, 12, 28, 23, 0)

    def snapshot(*args, **kwargs):
        return fake_snapshot(make_debts())

    monkeypatch.setattr(
        orchestration,
        "_payment_snapshot",
        snapshot,
    )

    commands = [
        make_command("PRINT_ARREARS_AGEING", notice_time),
        make_command("PRINT_ARREARS_AGEING", later_time),
    ]

    state_rows, _ = orchestration._build_state_events(
        data,
        bills,
        commands,
    )

    notice = next(
        row for row in state_rows
        if row["state"] == "DISCONNECTION_NOTICE"
    )

    disconnection = next(
        row for row in state_rows
        if row["state"] == "DISCONNECTED"
    )

    assert notice["event_date"] == date(2025, 11, 28)
    assert disconnection["event_date"] == date(2025, 12, 13)


def test_payment_clearing_arrears_prevents_disconnection(
    monkeypatch,
):
    data = make_data()
    bills = []
    notice_time = datetime(2025, 11, 28, 23, 0)
    later_time = datetime(2025, 12, 28, 23, 0)

    def snapshot(_bills, _payments, cutoff):
        cutoff = orchestration._timestamp(cutoff)

        # Arrears are unpaid before the disconnection date.
        if cutoff.date() < date(2025, 12, 13):
            return fake_snapshot(make_debts())

        # Payment clears the arrears on the disconnection date.
        return fake_snapshot([])

    monkeypatch.setattr(
        orchestration,
        "_payment_snapshot",
        snapshot,
    )

    commands = [
        make_command("PRINT_ARREARS_AGEING", notice_time),
        make_command("PRINT_ARREARS_AGEING", later_time),
    ]

    state_rows, _ = orchestration._build_state_events(
        data,
        bills,
        commands,
    )

    assert any(
        row["state"] == "DISCONNECTION_NOTICE"
        for row in state_rows
    )

    assert not any(
        row["state"] == "DISCONNECTED"
        for row in state_rows
    )

    assert any(
        row["state"] == "CONNECTED"
        for row in state_rows
    )


def test_disconnected_consumer_can_reconnect_after_full_payment(
    monkeypatch,
):
    data = make_data()
    data["payments"] = [
        {
            "consumer_id": "CON-TEST-01",
            "payment_ts": datetime(2025, 12, 14, 10, 0),
            "amount": Decimal("3000.00"),
        }
    ]

    bills = [
        {
            "consumer_id": "CON-TEST-01",
            "bill_date": date(2025, 11, 1),
            "net_current": Decimal("500.00"),
        }
    ]

    def snapshot(*args, **kwargs):
        return fake_snapshot(make_debts())

    monkeypatch.setattr(
        orchestration,
        "_payment_snapshot",
        snapshot,
    )

    commands = [
        make_command(
            "PRINT_ARREARS_AGEING",
            datetime(2025, 11, 28, 23, 0),
        ),
        make_command(
            "PRINT_ARREARS_AGEING",
            datetime(2025, 12, 28, 23, 0),
        ),
        make_command(
            "RECONNECT",
            datetime(2025, 12, 29, 12, 0),
            ["CON-TEST-01"],
        ),
    ]

    state_rows, reconnect_results = (
        orchestration._build_state_events(
            data,
            bills,
            commands,
        )
    )

    assert any(
        row["state"] == "DISCONNECTED"
        for row in state_rows
    )

    assert reconnect_results["CON-TEST-01"]["state"] == "RECONNECTED"

    assert any(
        row["state"] == "RECONNECTED"
        for row in state_rows
    )


def test_reconnection_is_refused_when_payment_is_insufficient(
    monkeypatch,
):
    data = make_data()
    data["payments"] = [
        {
            "consumer_id": "CON-TEST-01",
            "payment_ts": datetime(2025, 12, 14, 10, 0),
            "amount": Decimal("100.00"),
        }
    ]

    bills = [
        {
            "consumer_id": "CON-TEST-01",
            "bill_date": date(2025, 11, 1),
            "net_current": Decimal("500.00"),
        }
    ]

    def snapshot(*args, **kwargs):
        return fake_snapshot(make_debts())

    monkeypatch.setattr(
        orchestration,
        "_payment_snapshot",
        snapshot,
    )

    commands = [
        make_command(
            "PRINT_ARREARS_AGEING",
            datetime(2025, 11, 28, 23, 0),
        ),
        make_command(
            "PRINT_ARREARS_AGEING",
            datetime(2025, 12, 28, 23, 0),
        ),
        make_command(
            "RECONNECT",
            datetime(2025, 12, 29, 12, 0),
            ["CON-TEST-01"],
        ),
    ]

    state_rows, reconnect_results = (
        orchestration._build_state_events(
            data,
            bills,
            commands,
        )
    )

    assert reconnect_results["CON-TEST-01"]["state"] == "DISCONNECTED"

    assert not any(
        row["state"] == "RECONNECTED"
        for row in state_rows
    )
