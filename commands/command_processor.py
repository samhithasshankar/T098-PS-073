
"""
Command parser for the PS-073 electricity billing engine.

Commands are preserved in file order.
Empty arguments are allowed because the official README
defines them as "not supplied".
"""

import re
from datetime import datetime


MONTH_END_PATTERN = re.compile(
    r"^#\s*---\s*month-end\s+"
    r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*---$"
)

COMMAND_ARGUMENTS = {
    "RECONNECT": 2,
    "PRINT_ARREARS_AGEING": 1,
    "PRINT_BILL": 2,
    "PRINT_LEDGER": 2,
}


def parse_command_lines(lines):
    """Parse commands while preserving order and empty arguments."""

    parsed_commands = []
    current_execution_timestamp = None

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line:
            continue

        month_end_match = MONTH_END_PATTERN.match(line)

        if month_end_match:
            current_execution_timestamp = datetime.strptime(
                month_end_match.group(1),
                "%Y-%m-%d %H:%M:%S"
            )
            continue

        if line.startswith("#"):
            continue

        parts = [part.strip() for part in line.split("|")]
        command_name = parts[0].upper()
        arguments = parts[1:]

        if command_name not in COMMAND_ARGUMENTS:
            raise ValueError(
                f"Unknown command '{command_name}' "
                f"at line {line_number}."
            )

        expected_count = COMMAND_ARGUMENTS[command_name]

        if len(arguments) != expected_count:
            raise ValueError(
                f"{command_name} at line {line_number} "
                f"requires {expected_count} arguments; "
                f"received {len(arguments)}."
            )

        if command_name == "RECONNECT" and arguments[1]:
            try:
                execution_timestamp = datetime.strptime(
                    arguments[1],
                    "%Y-%m-%d %H:%M:%S"
                )
            except ValueError as error:
                raise ValueError(
                    f"Invalid RECONNECT timestamp at line "
                    f"{line_number}: {arguments[1]}"
                ) from error
        else:
            execution_timestamp = current_execution_timestamp

        if execution_timestamp is None:
            raise ValueError(
                f"No execution timestamp is defined before "
                f"command at line {line_number}."
            )

        parsed_commands.append({
            "line_number": line_number,
            "command": command_name,
            "arguments": arguments,
            "execution_timestamp": execution_timestamp,
        })

    return parsed_commands


def parse_command_file(file_path):
    """Read and parse a commands.txt file."""

    with open(file_path, "r", encoding="utf-8-sig") as file:
        return parse_command_lines(file.readlines())
