"""Unit tests for USPS-standard address normalization.

Tests normalize_address() and make_address_key() for consistent
deduplication across different address formats.

IMPORTANT: These tests use fake addresses only -- never real PII.
"""

from __future__ import annotations

from theleadedge.utils.address import make_address_key, normalize_address


class TestNormalizeAddress:
    """Address normalization tests."""

    def test_normalize_basic_address(self) -> None:
        """Basic address normalizes to uppercase with standard components."""
        result = normalize_address(
            street="123 Main St",
            city="Naples",
            state="FL",
            zip_code="34102",
        )
        assert result == "123 MAIN ST, NAPLES, FL, 34102"

    def test_directional_abbreviation(self) -> None:
        """Full directional words are replaced with USPS abbreviations."""
        result = normalize_address(
            street="456 North Ocean Boulevard",
            city="Cape Coral",
            state="FL",
            zip_code="33904",
        )
        assert "N" in result.split(", ")[0].split()
        assert "NORTH" not in result

    def test_suffix_abbreviation(self) -> None:
        """Full street suffixes are replaced with USPS abbreviations."""
        result = normalize_address(
            street="789 Palm Avenue",
            city="Fort Myers",
            state="FL",
            zip_code="33901",
        )
        assert "AVE" in result
        assert "AVENUE" not in result

    def test_empty_address(self) -> None:
        """Empty street returns empty string."""
        result = normalize_address(street="", city="Naples", zip_code="34102")
        assert result == ""

    def test_normalize_whitespace(self) -> None:
        """Extra whitespace is collapsed to single spaces."""
        result = normalize_address(
            street="123   Main    Street",
            city="Naples",
            state="FL",
            zip_code="34102",
        )
        assert "  " not in result


class TestMakeAddressKey:
    """Address deduplication key tests."""

    def test_make_address_key_strips_unit(self) -> None:
        """Unit/apt numbers are stripped from the deduplication key."""
        key = make_address_key("123 Main St Apt 4B", "34102")
        assert "4B" not in key
        assert "APT" not in key

    def test_same_address_different_format_same_key(self) -> None:
        """Different format representations of the same address produce the same key."""
        key_a = make_address_key("123 North Main Street", "34102")
        key_b = make_address_key("123 N MAIN ST", "34102")
        assert key_a == key_b

    def test_key_is_alphanumeric(self) -> None:
        """Generated key contains only alphanumeric characters."""
        key = make_address_key("123 Palm Dr, #5", "34102")
        assert key.isalnum()
