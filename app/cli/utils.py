"""Utilities used by the app.cli package."""

from __future__ import annotations
from pathlib import Path

import click


def ensure_folder(path: Path) -> Path:
    """Ensure that a directory exists, creating parents if needed.

    Args:
        path: The directory path to ensure exists.

    Returns:
        The original Path object.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_numeric_cedula(name: str) -> bool:
    """Check whether the patient identifier contains only digits.

    Args:
        name: The patient identifier string to validate.

    Returns:
        True if the identifier is numeric, otherwise False.
    """
    return name.isdigit()


def echo_error(message: str) -> None:
    """Print an error message to the console in red.

    Args:
        message: The error message to display.
    """
    click.secho(message, fg="red", bold=True, color=True)


def echo_warning(message: str) -> None:
    """Print a warning message to the console in yellow.

    Args:
        message: The warning message to display.
    """
    click.secho(message, fg="yellow", color=True)


def echo_info(message: str) -> None:
    """Print an informational message to the console in blue.

    Args:
        message: The information message to display.
    """
    click.secho(message, fg="bright_blue", color=True)


def echo_success(message: str) -> None:
    """Print a success message to the console in green.

    Args:
        message: The success message to display.
    """
    click.secho(message, fg="green", bold=True, color=True)
