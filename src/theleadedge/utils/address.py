"""USPS-standard address normalization for deduplication.

Normalizes street addresses to a canonical form using USPS abbreviations
so that "123 North Main Street" and "123 N MAIN ST" produce the same key.

Used by the ingestion pipeline to deduplicate properties across MLS exports
and public record sources.

IMPORTANT: This module processes address strings. Never log full addresses
(they are PII). Use only the generated keys for logging/debugging.
"""

from __future__ import annotations

import re

# USPS standard directional abbreviations (Publication 28)
DIRECTIONALS: dict[str, str] = {
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
    "NORTHEAST": "NE",
    "NORTHWEST": "NW",
    "SOUTHEAST": "SE",
    "SOUTHWEST": "SW",
}

# USPS standard street suffix abbreviations (Publication 28)
SUFFIXES: dict[str, str] = {
    "AVENUE": "AVE",
    "BOULEVARD": "BLVD",
    "CIRCLE": "CIR",
    "COURT": "CT",
    "DRIVE": "DR",
    "HIGHWAY": "HWY",
    "LANE": "LN",
    "PARKWAY": "PKWY",
    "PLACE": "PL",
    "ROAD": "RD",
    "STREET": "ST",
    "TERRACE": "TER",
    "TRAIL": "TRL",
    "WAY": "WAY",
}

# Already-abbreviated forms map to themselves for uniform lookup
_SUFFIX_ABBREVS: dict[str, str] = {v: v for v in SUFFIXES.values()}
_ALL_SUFFIXES: dict[str, str] = {**SUFFIXES, **_SUFFIX_ABBREVS}


def normalize_address(
    street: str,
    city: str = "",
    state: str = "FL",
    zip_code: str = "",
) -> str:
    """Normalize a street address to USPS standard format.

    Uppercases everything, replaces directionals and suffixes with standard
    abbreviations, and normalizes unit/apartment designators.

    Args:
        street: Street address line (e.g., "123 North Main Street").
        city: City name (optional).
        state: State abbreviation (default "FL").
        zip_code: 5-digit ZIP code (optional).

    Returns:
        Normalized address string with components joined by ", ".
        Returns empty string if street is empty.
    """
    if not street:
        return ""

    # Uppercase everything
    street = street.upper().strip()
    city = city.upper().strip()
    state = state.upper().strip()
    zip_code = zip_code.strip()

    # Normalize whitespace
    street = re.sub(r"\s+", " ", street)

    # Replace directionals and suffixes
    words = street.split()
    normalized: list[str] = []
    for word in words:
        clean = word.strip(".,")
        if clean in DIRECTIONALS:
            normalized.append(DIRECTIONALS[clean])
        elif clean in _ALL_SUFFIXES:
            normalized.append(_ALL_SUFFIXES[clean])
        else:
            normalized.append(clean)

    street = " ".join(normalized)

    # Normalize unit/apt variations to # format
    street = re.sub(r"\b(APT|APARTMENT|UNIT|STE|SUITE)\s*#?\s*", "# ", street)

    # Build full address
    parts = [street]
    if city:
        parts.append(city)
    if state:
        parts.append(state)
    if zip_code:
        parts.append(zip_code)

    return ", ".join(parts)


def make_address_key(street: str, zip_code: str) -> str:
    """Create a deduplication key from address components.

    Strips unit numbers and removes all non-alphanumeric characters to
    produce a compact key suitable for exact-match deduplication.

    Args:
        street: Street address line.
        zip_code: 5-digit ZIP code.

    Returns:
        Alphanumeric-only uppercase key (e.g., "123NMAINST34102").
    """
    key = normalize_address(street, zip_code=zip_code)
    # Remove unit numbers for dedup matching
    key = re.sub(r"\s*#\s*\S+", "", key)
    # Remove all non-alphanumeric
    key = re.sub(r"[^A-Z0-9]", "", key)
    return key
