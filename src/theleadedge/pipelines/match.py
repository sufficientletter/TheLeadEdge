"""Address matching pipeline for resolving source records to properties.

Implements a cascading match strategy:
1. Parcel ID exact match (confidence 1.0)
2. Normalized address exact match (confidence 0.95)
3. Address key match (confidence 0.85)
4. Fuzzy match via rapidfuzz (confidence = 0.70 * ratio)

Fuzzy matching requires exact ZIP code match to prevent false positives.

IMPORTANT: Never log full addresses (PII). Use only match_method and
confidence values in log messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog
from rapidfuzz import fuzz

from theleadedge.storage.repositories import PropertyRepo
from theleadedge.utils.address import make_address_key, normalize_address

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from theleadedge.models.source_record import SourceRecord
    from theleadedge.storage.database import PropertyRow

logger = structlog.get_logger()


@dataclass
class MatchResult:
    """Outcome of an address-matching attempt.

    Attributes
    ----------
    property_id:
        Database ID of the matched property, or ``None`` if no match.
    method:
        Name of the cascade step that matched (``"parcel_id"``,
        ``"address_normalized"``, ``"address_key"``, ``"fuzzy"``,
        or ``"none"``).
    confidence:
        Match confidence from 0.0 (no match) to 1.0 (exact parcel hit).
    property_row:
        The matched ``PropertyRow`` ORM instance, or ``None``.
    """

    property_id: int | None
    method: str
    confidence: float
    property_row: PropertyRow | None


class RecordMapper:
    """Cascading address matcher that resolves SourceRecords to PropertyRows.

    The cascade tries four strategies in order and returns the first
    successful match:

    1. **Parcel ID** -- exact match on county parcel number (confidence 1.0)
    2. **Normalized address** -- full USPS-normalized address equality (0.95)
    3. **Address key** -- alphanumeric-only key ignoring units (0.85)
    4. **Fuzzy** -- rapidfuzz ratio on normalized addresses within the
       same ZIP code, accepted only when ratio >= 85 (0.70 * ratio/100)
    """

    # Minimum rapidfuzz ratio to accept a fuzzy match
    FUZZY_MIN_RATIO: float = 85.0
    # Fuzzy confidence is scaled by this factor
    FUZZY_CONFIDENCE_FACTOR: float = 0.70

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._prop_repo = PropertyRepo(session)
        self.log = logger.bind(component="record_mapper")

    async def match(self, record: SourceRecord) -> MatchResult:
        """Run the cascading match against the properties table.

        Parameters
        ----------
        record:
            The source record to resolve.

        Returns
        -------
        MatchResult
            The best match found, or a ``method="none"`` result if
            no property could be resolved.
        """
        # Step 1: Parcel ID exact match
        if record.parcel_id:
            result = await self._match_by_parcel_id(record.parcel_id)
            if result is not None:
                self.log.info(
                    "match_found",
                    method="parcel_id",
                    confidence=result.confidence,
                )
                return result

        # Step 2: Normalized address exact match
        if record.street_address:
            result = await self._match_by_normalized_address(
                record.street_address,
                record.city or "",
                record.state,
                record.zip_code or "",
            )
            if result is not None:
                self.log.info(
                    "match_found",
                    method="address_normalized",
                    confidence=result.confidence,
                )
                return result

        # Step 3: Address key match
        if record.street_address and record.zip_code:
            result = await self._match_by_address_key(
                record.street_address,
                record.zip_code,
            )
            if result is not None:
                self.log.info(
                    "match_found",
                    method="address_key",
                    confidence=result.confidence,
                )
                return result

        # Step 4: Fuzzy match
        if record.street_address and record.zip_code:
            result = await self._match_by_fuzzy(
                record.street_address,
                record.zip_code,
            )
            if result is not None:
                self.log.info(
                    "match_found",
                    method="fuzzy",
                    confidence=result.confidence,
                )
                return result

        # No match
        self.log.debug("no_match_found")
        return MatchResult(
            property_id=None,
            method="none",
            confidence=0.0,
            property_row=None,
        )

    async def _match_by_parcel_id(self, parcel_id: str) -> MatchResult | None:
        """Exact match on county parcel ID (confidence 1.0)."""
        row = await self._prop_repo.get_by_parcel_id(parcel_id)
        if row is None:
            return None
        return MatchResult(
            property_id=row.id,
            method="parcel_id",
            confidence=1.0,
            property_row=row,
        )

    async def _match_by_normalized_address(
        self,
        street: str,
        city: str,
        state: str,
        zip_code: str,
    ) -> MatchResult | None:
        """Exact match on USPS-normalized full address (confidence 0.95)."""
        normalized = normalize_address(street, city, state, zip_code)
        if not normalized:
            return None
        row = await self._prop_repo.get_by_address_key(normalized)
        if row is None:
            return None
        return MatchResult(
            property_id=row.id,
            method="address_normalized",
            confidence=0.95,
            property_row=row,
        )

    async def _match_by_address_key(
        self,
        street: str,
        zip_code: str,
    ) -> MatchResult | None:
        """Match on alphanumeric address key, ignoring units (confidence 0.85)."""
        key = make_address_key(street, zip_code)
        if not key:
            return None

        # Query all properties in this ZIP and compare address keys
        candidates = await self._prop_repo.get_by_zip_code(zip_code)
        for prop in candidates:
            if prop.address_normalized is None:
                continue
            candidate_key = make_address_key(prop.address, prop.zip_code)
            if candidate_key == key:
                return MatchResult(
                    property_id=prop.id,
                    method="address_key",
                    confidence=0.85,
                    property_row=prop,
                )
        return None

    async def _match_by_fuzzy(
        self,
        street: str,
        zip_code: str,
    ) -> MatchResult | None:
        """Fuzzy match on normalized addresses within the same ZIP code.

        Only accepts matches with a rapidfuzz ratio >= 85.
        Confidence = 0.70 * (ratio / 100).
        """
        normalized_input = normalize_address(street, zip_code=zip_code)
        if not normalized_input:
            return None

        candidates = await self._prop_repo.get_by_zip_code(zip_code)
        if not candidates:
            return None

        best_row: PropertyRow | None = None
        best_ratio: float = 0.0

        for prop in candidates:
            if prop.address_normalized is None:
                continue
            ratio = fuzz.ratio(normalized_input, prop.address_normalized)
            if ratio > best_ratio:
                best_ratio = ratio
                best_row = prop

        if best_row is not None and best_ratio >= self.FUZZY_MIN_RATIO:
            confidence = self.FUZZY_CONFIDENCE_FACTOR * (best_ratio / 100.0)
            return MatchResult(
                property_id=best_row.id,
                method="fuzzy",
                confidence=round(confidence, 4),
                property_row=best_row,
            )

        return None
