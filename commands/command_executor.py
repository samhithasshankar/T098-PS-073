
"""Ordered command execution for the PS-073 billing engine."""

from datetime import date, datetime


SUPPORTED_COMMANDS = {
    "RECONNECT",
    "PRINT_ARREARS_AGEING",
    "PRINT_BILL",
    "PRINT_LEDGER",
}


def _as_datetime(value):
    """Normalize date/datetime values to datetime."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    return datetime.fromisoformat(str(value).strip())


def execute_commands(
    commands,
    handlers,
    process_events_before=None,
):
    """Execute parsed commands strictly in file order."""

    if not isinstance(commands, list):
        raise TypeError("commands must be a list.")

    if not isinstance(handlers, dict):
        raise TypeError("handlers must be a dictionary.")

    results = []

    for command_record in commands:
        command_name = str(
            command_record.get("command", "")
        ).upper()

        arguments = command_record.get("arguments", [])
        execution_timestamp = command_record.get(
            "execution_timestamp"
        )

        if command_name not in SUPPORTED_COMMANDS:
            raise ValueError(
                f"Unsupported command: {command_name}"
            )

        if execution_timestamp is None:
            raise ValueError(
                f"Command at line "
                f"{command_record.get('line_number')} "
                "has no execution timestamp."
            )

        if command_name not in handlers:
            raise ValueError(
                f"No handler registered for command: "
                f"{command_name}"
            )

        execution_timestamp = _as_datetime(
            execution_timestamp
        )

        # Apply input events strictly earlier than this command.
        if process_events_before is not None:
            process_events_before(execution_timestamp)

        result = handlers[command_name](
            arguments,
            execution_timestamp,
        )

        results.append({
            "line_number": command_record.get("line_number"),
            "command": command_name,
            "arguments": list(arguments),
            "execution_timestamp": execution_timestamp,
            "result": result,
        })

    return results
