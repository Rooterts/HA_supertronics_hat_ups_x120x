"""Standalone validation helpers."""

from __future__ import annotations


def validate_thresholds(stop_value: int, resume_value: int) -> dict[str, str]:
    """Ensure hysteresis thresholds are valid."""
    errors: dict[str, str] = {}
    if resume_value >= stop_value:
        errors["base"] = "resume_must_be_lower"
    return errors
