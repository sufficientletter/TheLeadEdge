"""Phone number normalization to E.164 format.

Normalizes US phone numbers to the international E.164 standard (+1XXXXXXXXXX)
for consistent storage and deduplication.

IMPORTANT: Phone numbers are PII. Never log raw or normalized phone numbers.
Use only for storage and CRM integration — never in log output.
"""

from __future__ import annotations

import re


def normalize_phone(phone: str | None) -> str | None:
    """Normalize a US phone number to E.164 format (+1XXXXXXXXXX).

    Strips all non-digit characters and validates the result as a
    standard 10-digit US phone number (with or without leading country code).

    Args:
        phone: Raw phone string in any common format, or None.

    Returns:
        E.164 formatted string (e.g., "+12345678901"), or None if the
        input is None, empty, or not a valid US number.
    """
    if not phone:
        return None

    # Extract digits only
    digits = re.sub(r"\D", "", phone)

    # Handle 10-digit US number
    if len(digits) == 10:
        return f"+1{digits}"

    # Handle 11-digit with leading 1
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"

    # Not a standard US number
    return None


def format_phone_display(phone: str | None) -> str:
    """Format an E.164 phone number for human-readable display.

    Args:
        phone: E.164 formatted phone string (e.g., "+12345678901"), or None.

    Returns:
        Formatted string like "(234) 567-8901", or empty string if invalid.
    """
    if not phone:
        return ""

    digits = re.sub(r"\D", "", phone)

    # Strip country code if present
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    return phone
