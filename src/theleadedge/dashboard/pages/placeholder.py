"""Placeholder pages for remaining dashboard routes.

These stubs register routes with minimal UI.  Each will be replaced
by a full implementation in subsequent Phase 3 batches.

Replaced routes:
- /map       -> map_view.py   (Batch 6)
- /records   -> records.py    (Batch 7)
- /analytics -> analytics.py  (Batch 8)
- /settings  -> settings.py   (Batch 9)
"""

from __future__ import annotations

from nicegui import ui

from theleadedge.dashboard.auth import DASHBOARD_PASSWORD, login_page

if DASHBOARD_PASSWORD:

    @ui.page("/login")
    def page_login() -> None:
        """Login page -- only registered when a password is configured."""
        login_page()
