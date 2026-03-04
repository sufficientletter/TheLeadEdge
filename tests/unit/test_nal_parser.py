"""Unit tests for the Florida DOR NAL fixed-width file parser.

Tests cover field extraction, type parsing (str, int, float),
edge cases (short lines, empty numerics), whitespace stripping,
and multi-line file parsing.

All test data is synthetic -- no real property data.
"""

from __future__ import annotations

from theleadedge.utils.nal_parser import (
    NalFieldSpec,
    load_nal_field_specs,
    parse_nal_file,
    parse_nal_line,
)

# ---------------------------------------------------------------------------
# Field specs used across tests
# ---------------------------------------------------------------------------

SAMPLE_FIELDS: list[NalFieldSpec] = [
    NalFieldSpec("id", 0, 10),
    NalFieldSpec("name", 10, 30),
    NalFieldSpec("city", 30, 50),
    NalFieldSpec("amount", 50, 60, "float"),
    NalFieldSpec("count", 60, 65, "int"),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestParseNalLineBasic:
    """Tests for basic field extraction from fixed-width lines."""

    def test_parse_nal_line_basic(self) -> None:
        """Fields at known positions should be extracted correctly."""
        # Build a line with known data at exact positions
        # id(0-10), name(10-30), city(30-50), amount(50-60), count(60-65)
        # Each field must be exactly the right width
        id_f = "ABC1234567"              # 10 chars
        name_f = "SYNTHETIC OWNER".ljust(20)  # 20 chars
        city_f = "CAPE CORAL".ljust(20)       # 20 chars
        amount_f = "350000.0".rjust(10)       # 10 chars
        count_f = "42".rjust(5)               # 5 chars
        line = id_f + name_f + city_f + amount_f + count_f

        result = parse_nal_line(line, SAMPLE_FIELDS)

        assert result["id"] == "ABC1234567"
        assert result["name"] == "SYNTHETIC OWNER"
        assert result["city"] == "CAPE CORAL"
        assert result["amount"] == 350000.0
        assert result["count"] == 42

    def test_parse_nal_line_strips_whitespace(self) -> None:
        """String fields should have leading/trailing whitespace stripped."""
        # Heavily padded fields
        id_f = "  ABC     "              # 10 chars
        name_f = "   PADDED NAME".ljust(20)   # 20 chars
        city_f = "   PADDED CITY".ljust(20)   # 20 chars
        amount_f = "100.5".rjust(10)          # 10 chars
        count_f = "1".rjust(5)                # 5 chars
        line = id_f + name_f + city_f + amount_f + count_f

        result = parse_nal_line(line, SAMPLE_FIELDS)

        assert result["id"] == "ABC"
        assert result["name"] == "PADDED NAME"
        assert result["city"] == "PADDED CITY"
        assert result["amount"] == 100.5
        assert result["count"] == 1


class TestParseNalLineNumeric:
    """Tests for numeric field parsing (int and float)."""

    def test_parse_nal_line_numeric_fields(self) -> None:
        """Int and float fields should be parsed to correct Python types."""
        line = (
            "ID12345678"
            + "NAME FIELD HERE".ljust(20)
            + "CITY FIELD HERE".ljust(20)
            + "999999.99".rjust(10)
            + "100".rjust(5)
        )
        result = parse_nal_line(line, SAMPLE_FIELDS)

        assert isinstance(result["amount"], float)
        assert result["amount"] == 999999.99
        assert isinstance(result["count"], int)
        assert result["count"] == 100

    def test_parse_nal_line_empty_numeric(self) -> None:
        """Empty numeric fields should return None, not raise."""
        line = (
            "ID12345678"
            + "SOME NAME HERE".ljust(20)
            + "SOME CITY HERE".ljust(20)
            + " " * 10
            + " " * 5
        )
        result = parse_nal_line(line, SAMPLE_FIELDS)

        assert result["amount"] is None
        assert result["count"] is None

    def test_parse_nal_line_invalid_numeric(self) -> None:
        """Non-numeric content in numeric fields should return None."""
        line = (
            "ID12345678"
            + "SOME NAME HERE".ljust(20)
            + "SOME CITY HERE".ljust(20)
            + "N/A".rjust(10)
            + "N/A".rjust(5)
        )
        result = parse_nal_line(line, SAMPLE_FIELDS)

        assert result["amount"] is None
        assert result["count"] is None


class TestParseNalLineShort:
    """Tests for lines shorter than expected."""

    def test_parse_nal_line_short_line(self) -> None:
        """Line shorter than field end positions should produce None values."""
        # Only 15 chars -- covers id (0-10) but name (10-30) needs more
        line = "SHORT12345ABCDE"
        result = parse_nal_line(line, SAMPLE_FIELDS)

        assert result["id"] == "SHORT12345"
        # name needs 10-30 but line is only 15 chars -- too short → None
        assert result["name"] is None
        # city, amount, count are beyond the line length → None
        assert result["city"] is None
        assert result["amount"] is None
        assert result["count"] is None


class TestParseNalFile:
    """Tests for multi-line NAL file parsing."""

    def test_parse_nal_file_basic(self) -> None:
        """Multiple valid lines should all be parsed."""
        line1 = (
            "PARCEL0001"
            + "OWNER ONE HERE".ljust(20)
            + "CAPE CORAL".ljust(20)
            + "250000.0".rjust(10)
            + "10".rjust(5)
        )
        line2 = (
            "PARCEL0002"
            + "OWNER TWO HERE".ljust(20)
            + "FORT MYERS".ljust(20)
            + "300000.0".rjust(10)
            + "20".rjust(5)
        )
        content = f"{line1}\n{line2}"
        records = parse_nal_file(content, SAMPLE_FIELDS)

        assert len(records) == 2
        assert records[0]["id"] == "PARCEL0001"
        assert records[1]["id"] == "PARCEL0002"
        assert records[0]["amount"] == 250000.0
        assert records[1]["city"] == "FORT MYERS"

    def test_parse_nal_file_skips_short_lines(self) -> None:
        """Lines shorter than minimum field width should be skipped."""
        valid_line = (
            "PARCEL0001"
            + "VALID OWNER".ljust(20)
            + "VALID CITY".ljust(20)
            + "100000.0".rjust(10)
            + "5".rjust(5)
        )
        short_line = "TOO SHORT"
        blank_line = ""

        content = f"{valid_line}\n{short_line}\n{blank_line}\n{valid_line}"
        records = parse_nal_file(content, SAMPLE_FIELDS)

        # Only the two valid-length lines should be parsed
        assert len(records) == 2

    def test_parse_nal_file_empty_content(self) -> None:
        """Empty content should return an empty list."""
        records = parse_nal_file("", SAMPLE_FIELDS)
        assert records == []

    def test_parse_nal_file_empty_fields(self) -> None:
        """Empty field list should return empty dicts for every non-blank line."""
        content = "some data here\nanother line"
        records = parse_nal_file(content, [])
        assert records == [{}, {}]


class TestLoadNalFieldSpecs:
    """Tests for loading field specs from YAML config format."""

    def test_load_from_config(self) -> None:
        """Config section with [start, end, type] lists should produce specs."""
        config_section = {
            "strap": [0, 18, "str"],
            "sale_price": [26, 38, "float"],
            "count": [38, 43, "int"],
        }
        specs = load_nal_field_specs(config_section)

        assert len(specs) == 3

        strap = next(s for s in specs if s.name == "strap")
        assert strap.start == 0
        assert strap.end == 18
        assert strap.field_type == "str"

        price = next(s for s in specs if s.name == "sale_price")
        assert price.start == 26
        assert price.end == 38
        assert price.field_type == "float"

        count = next(s for s in specs if s.name == "count")
        assert count.field_type == "int"

    def test_load_from_config_default_type(self) -> None:
        """Fields with only [start, end] should default to 'str'."""
        config_section = {
            "name": [0, 20],
        }
        specs = load_nal_field_specs(config_section)
        assert len(specs) == 1
        assert specs[0].field_type == "str"
