"""TheLeadEdge storage layer -- ORM tables, repositories, and named queries.

Usage::

    from theleadedge.storage import init_db, get_session
    from theleadedge.storage.repositories import PropertyRepo, LeadRepo
    from theleadedge.storage.queries import get_hot_leads
"""

from .database import (
    Base,
    LeadRow,
    OutreachEventRow,
    PriceHistoryRow,
    PropertyRow,
    ScoreHistoryRow,
    SignalRow,
    SyncLogRow,
    drop_db,
    get_engine,
    get_session,
    get_session_factory,
    init_db,
    reset_engine,
)

__all__ = [
    # Base
    "Base",
    # ORM rows
    "PropertyRow",
    "LeadRow",
    "SignalRow",
    "ScoreHistoryRow",
    "OutreachEventRow",
    "PriceHistoryRow",
    "SyncLogRow",
    # Engine / session
    "get_engine",
    "get_session_factory",
    "get_session",
    "init_db",
    "drop_db",
    "reset_engine",
]
