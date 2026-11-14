
import pytest

from commands.command_executor import execute_commands


def test_commands_execute_in_file_order():
    calls = []

    commands = [
        {
            "line_number": 1,
            "command": "PRINT_BILL",
            "arguments": ["CON-0001", "2026-01"],
            "execution_timestamp": "2026-01-31 23:00:00",
        },
        {
            "line_number": 2,
            "command": "PRINT_LEDGER",
            "arguments": ["CON-0001", "2026-01-31"],
            "execution_timestamp": "2026-01-31 23:30:00",
        },
    ]

    handlers = {
        "PRINT_BILL": lambda args, ts: calls.append("bill"),
        "PRINT_LEDGER": lambda args, ts: calls.append("ledger"),
    }

    execute_commands(commands, handlers)

    assert calls == ["bill", "ledger"]


def test_events_are_processed_before_each_command():
    calls = []

    commands = [{
        "line_number": 1,
        "command": "PRINT_BILL",
        "arguments": ["CON-0001", "2026-01"],
        "execution_timestamp": "2026-01-31 23:00:00",
    }]

    execute_commands(
        commands,
        {"PRINT_BILL": lambda args, ts: "done"},
        process_events_before=lambda ts: calls.append(ts),
    )

    assert len(calls) == 1


def test_unsupported_command_is_rejected():
    commands = [{
        "line_number": 1,
        "command": "INVALID",
        "arguments": [],
        "execution_timestamp": "2026-01-31 23:00:00",
    }]

    with pytest.raises(ValueError, match="Unsupported command"):
        execute_commands(commands, {})


def test_missing_handler_is_rejected():
    commands = [{
        "line_number": 1,
        "command": "PRINT_BILL",
        "arguments": [],
        "execution_timestamp": "2026-01-31 23:00:00",
    }]

    with pytest.raises(ValueError, match="No handler registered"):
        execute_commands(commands, {})
