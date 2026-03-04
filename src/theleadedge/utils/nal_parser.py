"""Florida DOR NAL (Name-Address-Legal) fixed-width file parser.

Lee County (and other FL counties) distribute property assessment data
in the Florida Department of Revenue standard NAL format -- fixed-width
text files where each field occupies a defined column range.

The NAL file contains multiple record types, each with its own layout.
This parser handles the primary record types needed for property
assessment data extraction.

Reference: Florida DOR Data Sharing Program
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NalFieldSpec:
    """Defines a single field's position within a NAL record line.

    Attributes:
        name: Internal field name.
        start: 0-based start column (inclusive).
        end: 0-based end column (exclusive).
        field_type: One of ``"str"``, ``"int"``, ``"float"``.
    """

    name: str
    start: int
    end: int
    field_type: str = "str"


def parse_nal_line(
    line: str,
    fields: list[NalFieldSpec],
) -> dict[str, str | int | float | None]:
    """Extract fields from a fixed-width NAL record line.

    Args:
        line: Raw text line from NAL file.
        fields: List of field specifications defining column positions.

    Returns:
        Dict mapping field names to extracted values.  Strings are stripped.
        Numeric fields return ``None`` if the raw value is empty or
        non-numeric.
    """
    result: dict[str, str | int | float | None] = {}
    for spec in fields:
        raw = line[spec.start : spec.end].strip() if len(line) >= spec.end else ""
        if not raw:
            result[spec.name] = None
            continue
        if spec.field_type == "int":
            try:
                result[spec.name] = int(raw)
            except ValueError:
                result[spec.name] = None
        elif spec.field_type == "float":
            try:
                result[spec.name] = float(raw)
            except ValueError:
                result[spec.name] = None
        else:
            result[spec.name] = raw
    return result


def parse_nal_file(
    content: str,
    fields: list[NalFieldSpec],
) -> list[dict[str, str | int | float | None]]:
    """Parse all lines of a NAL file.

    Skips blank lines and lines shorter than the minimum field width
    required by the field specifications.

    Args:
        content: Full text content of a NAL file.
        fields: Field specifications for the record layout.

    Returns:
        List of parsed records (one dict per valid line).
    """
    min_width = max(f.end for f in fields) if fields else 0
    records: list[dict[str, str | int | float | None]] = []
    for line in content.splitlines():
        if len(line) < min_width:
            continue
        records.append(parse_nal_line(line, fields))
    return records


def load_nal_field_specs(
    config_section: dict[str, list],
) -> list[NalFieldSpec]:
    """Build NalFieldSpec list from a YAML config section.

    Each entry in the config section maps a field name to a list of
    ``[start, end, type]``.

    Args:
        config_section: Dict from pa_fields.yaml (e.g. ``lee.nal_fields``).

    Returns:
        List of ``NalFieldSpec`` instances.
    """
    specs: list[NalFieldSpec] = []
    for name, positions in config_section.items():
        start = positions[0]
        end = positions[1]
        field_type = positions[2] if len(positions) > 2 else "str"
        specs.append(
            NalFieldSpec(name=name, start=start, end=end, field_type=field_type)
        )
    return specs
