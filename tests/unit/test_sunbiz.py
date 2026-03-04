"""Unit tests for the Sunbiz LLC data connector.

Tests cover pipe-delimited parsing, cross-referencing LLC entities to
property owners, dissolved entity flagging, and out-of-state agent
detection.

All test data is synthetic -- no real entities or PII.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from theleadedge.sources.sunbiz import SunbizConnector, _normalize_name

# ---------------------------------------------------------------------------
# Sample pipe-delimited data
# ---------------------------------------------------------------------------

def _pipe(*fields: str) -> str:
    return "|".join(fields)


SAMPLE_PIPE_DATA = "\n".join([
    _pipe(
        "P12345678", "SUNSHINE PROPERTIES LLC", "01/15/2020",
        "ACTIVE", "FL", "JOHN DOE", "123 AGENT ST", "NAPLES",
        "FL", "456 MAIN ST", "NAPLES", "FL", "34102",
    ),
    _pipe(
        "P23456789", "COASTAL INVESTMENTS INC", "03/22/2018",
        "DISSOLVED", "FL", "JANE SMITH", "789 OAK AVE", "MIAMI",
        "FL", "321 PALM DR", "FORT MYERS", "FL", "33901",
    ),
    _pipe(
        "P34567890", "NORTHERN REALTY LLC", "07/10/2021",
        "ACTIVE", "NY", "BOB JONES", "555 WALL ST", "NEW YORK",
        "NY", "100 BEACH RD", "CAPE CORAL", "FL", "33904",
    ),
    _pipe(
        "P45678901", "EMPTY SHELL LLC", "11/01/2019",
        "ADMIN DISSOLVED", "FL", "ALICE WONDER", "222 ELM ST",
        "TAMPA", "FL", "333 VINE ST", "NAPLES", "FL", "34103",
    ),
    _pipe(
        "P56789012", "GULF ACCESS HOLDINGS LLC", "06/15/2022",
        "ACTIVE", "FL", "CHARLIE BROWN", "444 PINE LN",
        "FORT MYERS", "FL", "555 GULF DR", "BONITA SPRINGS",
        "FL", "34134",
    ),
]) + "\n"

_HEADER_FIELDS = (
    "DOCUMENT NUMBER", "ENTITY NAME", "FILING DATE", "STATUS",
    "STATE", "REG AGENT NAME", "REG AGENT ADDRESS",
    "REG AGENT CITY", "REG AGENT STATE", "PRINCIPAL ADDRESS",
    "PRINCIPAL CITY", "PRINCIPAL STATE", "PRINCIPAL ZIP",
)
SAMPLE_PIPE_WITH_HEADER = "\n".join([
    _pipe(*_HEADER_FIELDS),
    _pipe(
        "P12345678", "SUNSHINE PROPERTIES LLC", "01/15/2020",
        "ACTIVE", "FL", "JOHN DOE", "123 AGENT ST", "NAPLES",
        "FL", "456 MAIN ST", "NAPLES", "FL", "34102",
    ),
]) + "\n"

SAMPLE_PIPE_SHORT_LINES = """\
P99999999|MINIMAL ENTITY
P88888888|ANOTHER ENTITY|05/01/2023|ACTIVE
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def download_dir(tmp_path: Path) -> Path:
    """Create a temporary download directory."""
    d = tmp_path / "sunbiz_downloads"
    d.mkdir()
    return d


@pytest.fixture
def connector(download_dir: Path) -> SunbizConnector:
    """Create a SunbizConnector with no SFTP credentials (local mode)."""
    return SunbizConnector(download_dir=download_dir)


@pytest.fixture
def sample_file(download_dir: Path) -> Path:
    """Write sample pipe-delimited data to a file."""
    path = download_dir / "corp_data.txt"
    path.write_text(SAMPLE_PIPE_DATA, encoding="utf-8")
    return path


@pytest.fixture
def sample_file_with_header(download_dir: Path) -> Path:
    """Write sample data with a header row."""
    path = download_dir / "corp_header.txt"
    path.write_text(SAMPLE_PIPE_WITH_HEADER, encoding="utf-8")
    return path


@pytest.fixture
def sample_file_short(download_dir: Path) -> Path:
    """Write sample data with short/partial lines."""
    path = download_dir / "corp_short.txt"
    path.write_text(SAMPLE_PIPE_SHORT_LINES, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Test: transform parses pipe-delimited
# ---------------------------------------------------------------------------


class TestTransform:
    """Tests for the transform method parsing pipe-delimited files."""

    def test_transform_parses_pipe_delimited(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Valid pipe-delimited file produces entity dicts with expected fields."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        assert len(entities) == 5

        first = entities[0]
        assert first["document_number"] == "P12345678"
        assert first["entity_name"] == "SUNSHINE PROPERTIES LLC"
        assert first["status"] == "ACTIVE"
        assert first["state"] == "FL"
        assert first["principal_city"] == "NAPLES"
        assert first["principal_state"] == "FL"
        assert first["principal_zip"] == "34102"
        assert first["is_dissolved"] is False
        assert first["is_out_of_state_agent"] is False

    def test_transform_skips_header_row(
        self, connector: SunbizConnector, sample_file_with_header: Path
    ) -> None:
        """Header row with 'DOCUMENT NUMBER' is skipped."""
        raw_records = [{"file_path": sample_file_with_header}]
        entities = connector.transform(raw_records)

        # Should have 1 entity (header skipped)
        assert len(entities) == 1
        assert entities[0]["document_number"] == "P12345678"

    def test_transform_handles_short_lines(
        self, connector: SunbizConnector, sample_file_short: Path
    ) -> None:
        """Short lines with fewer fields are parsed with empty defaults."""
        raw_records = [{"file_path": sample_file_short}]
        entities = connector.transform(raw_records)

        assert len(entities) == 2
        # Short line: only document_number and entity_name
        assert entities[0]["document_number"] == "P99999999"
        assert entities[0]["entity_name"] == "MINIMAL ENTITY"
        assert entities[0]["status"] == ""
        assert entities[0]["is_dissolved"] is False

    def test_transform_missing_file(
        self, connector: SunbizConnector, download_dir: Path
    ) -> None:
        """Missing file produces no entities (with warning logged)."""
        raw_records = [{"file_path": download_dir / "nonexistent.txt"}]
        entities = connector.transform(raw_records)
        assert len(entities) == 0

    def test_transform_empty_input(
        self, connector: SunbizConnector
    ) -> None:
        """Empty input produces no entities."""
        entities = connector.transform([])
        assert len(entities) == 0


# ---------------------------------------------------------------------------
# Test: dissolved entity flagging
# ---------------------------------------------------------------------------


class TestDissolvedFlagging:
    """Tests for dissolved/inactive LLC detection."""

    def test_dissolved_status_flagged(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Entities with DISSOLVED status are flagged."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        # P23456789 has status DISSOLVED
        dissolved = [e for e in entities if e["document_number"] == "P23456789"]
        assert len(dissolved) == 1
        assert dissolved[0]["is_dissolved"] is True
        assert dissolved[0]["status"] == "DISSOLVED"

    def test_admin_dissolved_flagged(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Entities with ADMIN DISSOLVED status are flagged."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        admin_dissolved = [
            e for e in entities if e["document_number"] == "P45678901"
        ]
        assert len(admin_dissolved) == 1
        assert admin_dissolved[0]["is_dissolved"] is True

    def test_active_not_flagged_dissolved(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Active entities are not flagged as dissolved."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        active = [e for e in entities if e["document_number"] == "P12345678"]
        assert len(active) == 1
        assert active[0]["is_dissolved"] is False


# ---------------------------------------------------------------------------
# Test: out-of-state registered agent
# ---------------------------------------------------------------------------


class TestOutOfStateAgent:
    """Tests for out-of-state registered agent detection."""

    def test_out_of_state_agent_flagged(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Entity with NY registered agent state is flagged as out-of-state."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        ny_agent = [
            e for e in entities if e["document_number"] == "P34567890"
        ]
        assert len(ny_agent) == 1
        assert ny_agent[0]["is_out_of_state_agent"] is True
        assert ny_agent[0]["registered_agent_state"] == "NY"

    def test_fl_agent_not_flagged(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Entity with FL registered agent state is not flagged."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        fl_agent = [
            e for e in entities if e["document_number"] == "P12345678"
        ]
        assert len(fl_agent) == 1
        assert fl_agent[0]["is_out_of_state_agent"] is False


# ---------------------------------------------------------------------------
# Test: cross-reference matching
# ---------------------------------------------------------------------------


class TestCrossReference:
    """Tests for cross-referencing entities to property owners."""

    def test_cross_reference_matches(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """LLC name that matches owner_name_raw produces a match."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        # Simulate property owners with LLC names
        property_owner_names = [
            (101, "SUNSHINE PROPERTIES LLC"),
            (102, "COASTAL INVESTMENTS INC"),
            (103, "Some Other Person"),
        ]

        matches = connector.cross_reference(entities, property_owner_names)

        assert len(matches) == 2
        matched_prop_ids = {m["property_id"] for m in matches}
        assert 101 in matched_prop_ids
        assert 102 in matched_prop_ids
        assert 103 not in matched_prop_ids

    def test_cross_reference_normalized_matching(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Cross-reference ignores LLC/INC suffixes and punctuation."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        # Owner name without the suffix should still match
        property_owner_names = [
            (201, "Sunshine Properties"),  # Mixed case, no LLC
        ]

        matches = connector.cross_reference(entities, property_owner_names)
        assert len(matches) == 1
        assert matches[0]["property_id"] == 201

    def test_cross_reference_no_matches(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """No matches when owner names do not correspond to any entity."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        property_owner_names = [
            (301, "Completely Unrelated Name"),
            (302, "Another Random Owner"),
        ]

        matches = connector.cross_reference(entities, property_owner_names)
        assert len(matches) == 0

    def test_cross_reference_empty_owners(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Empty owner list produces no matches."""
        raw_records = [{"file_path": sample_file}]
        entities = connector.transform(raw_records)

        matches = connector.cross_reference(entities, [])
        assert len(matches) == 0

    def test_cross_reference_empty_entities(
        self, connector: SunbizConnector
    ) -> None:
        """Empty entity list produces no matches."""
        property_owner_names = [(401, "Some Owner LLC")]
        matches = connector.cross_reference([], property_owner_names)
        assert len(matches) == 0


# ---------------------------------------------------------------------------
# Test: health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Tests for the health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_healthy_local(
        self, download_dir: Path
    ) -> None:
        """Local mode health check returns True when directory exists."""
        connector = SunbizConnector(download_dir=download_dir)
        result = await connector.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_missing_dir(
        self, tmp_path: Path
    ) -> None:
        """Health check returns False when directory does not exist."""
        missing_dir = tmp_path / "does_not_exist"
        connector = SunbizConnector(download_dir=missing_dir)
        result = await connector.health_check()
        assert result is False


# ---------------------------------------------------------------------------
# Test: name normalization helper
# ---------------------------------------------------------------------------


class TestNormalizeName:
    """Tests for the _normalize_name helper function."""

    def test_strips_llc_suffix(self) -> None:
        assert _normalize_name("SUNSHINE PROPERTIES LLC") == "SUNSHINE PROPERTIES"

    def test_strips_inc_suffix(self) -> None:
        assert _normalize_name("COASTAL INVESTMENTS INC") == "COASTAL INVESTMENTS"

    def test_case_insensitive(self) -> None:
        assert _normalize_name("sunshine properties llc") == "SUNSHINE PROPERTIES"

    def test_strips_punctuation(self) -> None:
        assert _normalize_name("O'BRIEN'S, LLC") == "OBRIENS"

    def test_collapses_whitespace(self) -> None:
        assert _normalize_name("  MULTIPLE   SPACES   LLC  ") == "MULTIPLE SPACES"

    def test_empty_string(self) -> None:
        assert _normalize_name("") == ""

    def test_strips_trust_suffix(self) -> None:
        assert _normalize_name("SMITH FAMILY TRUST") == "SMITH FAMILY"


# ---------------------------------------------------------------------------
# Test: fetch (local file scan)
# ---------------------------------------------------------------------------


class TestFetch:
    """Tests for the fetch method in local/HTTP fallback mode."""

    @pytest.mark.asyncio
    async def test_fetch_finds_txt_files(
        self, connector: SunbizConnector, sample_file: Path
    ) -> None:
        """Fetch scans download directory and finds .txt files."""
        results = await connector.fetch()
        assert len(results) == 1
        assert results[0]["file_path"] == sample_file

    @pytest.mark.asyncio
    async def test_fetch_empty_dir(
        self, connector: SunbizConnector
    ) -> None:
        """Fetch returns empty list for empty directory."""
        results = await connector.fetch()
        assert len(results) == 0
