"""Simple password-based authentication for the dashboard.

Reads ``DASHBOARD_PASSWORD`` from the environment.  If the variable is empty
or unset, authentication is disabled and all requests pass through.

IMPORTANT: Never log or display PII.
"""

from __future__ import annotations

import os

from nicegui import app, ui
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

DASHBOARD_PASSWORD: str = os.environ.get("DASHBOARD_PASSWORD", "")


def check_password(password: str | None) -> bool:
    """Verify a password against the configured dashboard password.

    Parameters
    ----------
    password:
        The password attempt to check.

    Returns
    -------
    bool
        True if the password matches, or if no password is configured
        (empty string means auth disabled).  False otherwise.
    """
    if not DASHBOARD_PASSWORD:
        # No password configured -- auth disabled, accept empty string
        return password == ""
    if password is None:
        return False
    return password == DASHBOARD_PASSWORD


class AuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that redirects unauthenticated users to /login.

    Bypasses auth for:
    - ``/_nicegui`` internal routes (static assets, websocket)
    - ``/login`` page itself
    - When ``DASHBOARD_PASSWORD`` is empty (auth disabled)
    """

    async def dispatch(self, request: Request, call_next):  # noqa: N802
        """Check authentication before passing request to the next handler."""
        if not DASHBOARD_PASSWORD:
            return await call_next(request)
        if request.url.path.startswith("/_nicegui"):
            return await call_next(request)
        if request.url.path == "/login":
            return await call_next(request)
        if not app.storage.user.get("authenticated", False):
            return RedirectResponse(f"/login?redirect={request.url.path}")
        return await call_next(request)


def login_page() -> None:
    """Render the login page at ``/login``.

    Displays a centered card with a password field and sign-in button.
    On successful authentication, stores the flag in user storage and
    redirects to the originally requested path (or ``/``).
    """

    def try_login(password: str, redirect: str = "/") -> None:
        if check_password(password):
            app.storage.user["authenticated"] = True
            ui.navigate.to(redirect)
        else:
            ui.notify("Invalid password", type="negative")

    with ui.card().classes("absolute-center w-80"):
        ui.label("TheLeadEdge").classes("text-h4 text-center w-full")
        ui.label("Dashboard Login").classes(
            "text-subtitle1 text-center w-full text-grey"
        )
        password_input = ui.input(
            "Password",
            password=True,
            password_toggle_button=True,
        ).classes("w-full")
        ui.button(
            "Sign In",
            on_click=lambda: try_login(password_input.value),
        ).classes("w-full")
