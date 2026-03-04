"""NiceGUI dashboard application for TheLeadEdge.

Entry point for the web dashboard.  Call ``run_dashboard()`` to start
the NiceGUI server, or ``create_app()`` to configure without running
(useful for testing).

IMPORTANT: Never log or display PII.
"""

from __future__ import annotations

import structlog
from nicegui import app, ui

from theleadedge.config import Settings
from theleadedge.storage.database import get_engine, init_db

logger = structlog.get_logger()


def create_app(settings: Settings | None = None) -> None:
    """Configure the NiceGUI application.

    Registers startup hooks, middleware, static files, and imports
    all page routes.  Must be called before ``ui.run()``.

    Parameters
    ----------
    settings:
        Application settings.  If None, loads from environment / .env.
    """
    from pathlib import Path

    if settings is None:
        settings = Settings()

    # Store settings in app storage for access by pages
    app.storage.general["settings"] = settings

    async def startup() -> None:
        """Initialize database on app startup."""
        engine = get_engine(settings.database_url)
        await init_db(engine)
        logger.info("dashboard_db_initialized")

    app.on_startup(startup)

    # Register auth middleware (only if password is set)
    from theleadedge.dashboard.auth import DASHBOARD_PASSWORD, AuthMiddleware

    if DASHBOARD_PASSWORD:
        app.add_middleware(AuthMiddleware)

    # Register static files for PWA manifest and assets
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.add_static_files("/static", str(static_dir))

    # Import pages to register routes
    import theleadedge.dashboard.pages.analytics  # noqa: F401
    import theleadedge.dashboard.pages.briefing  # noqa: F401
    import theleadedge.dashboard.pages.lead_detail  # noqa: F401
    import theleadedge.dashboard.pages.leads  # noqa: F401
    import theleadedge.dashboard.pages.map_view  # noqa: F401
    import theleadedge.dashboard.pages.placeholder  # noqa: F401
    import theleadedge.dashboard.pages.records  # noqa: F401
    import theleadedge.dashboard.pages.settings  # noqa: F401


def run_dashboard(
    host: str = "0.0.0.0",
    port: int = 8080,
    reload: bool = False,
    settings: Settings | None = None,
) -> None:
    """Create and run the dashboard.

    Parameters
    ----------
    host:
        Network interface to bind to.
    port:
        TCP port number.
    reload:
        Enable NiceGUI auto-reload for development.
    settings:
        Application settings.  If None, loads from environment / .env.
    """
    create_app(settings)
    ui.run(
        host=host,
        port=port,
        title="TheLeadEdge",
        favicon="\U0001f3e0",
        reload=reload,
        storage_secret="theleadedge-dashboard-secret",
    )
