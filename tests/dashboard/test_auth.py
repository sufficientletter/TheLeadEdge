"""Tests for dashboard auth module.

Tests the check_password function in isolation, without requiring
a running NiceGUI server.
"""

from __future__ import annotations

from theleadedge.dashboard import auth


class TestCheckPassword:
    """Verify password checking logic."""

    def test_correct_password(self) -> None:
        original = auth.DASHBOARD_PASSWORD
        try:
            auth.DASHBOARD_PASSWORD = "secret123"
            assert auth.check_password("secret123") is True
        finally:
            auth.DASHBOARD_PASSWORD = original

    def test_wrong_password(self) -> None:
        original = auth.DASHBOARD_PASSWORD
        try:
            auth.DASHBOARD_PASSWORD = "secret123"
            assert auth.check_password("wrong") is False
        finally:
            auth.DASHBOARD_PASSWORD = original

    def test_empty_password_means_no_auth(self) -> None:
        original = auth.DASHBOARD_PASSWORD
        try:
            auth.DASHBOARD_PASSWORD = ""
            assert auth.check_password("") is True
        finally:
            auth.DASHBOARD_PASSWORD = original

    def test_none_password(self) -> None:
        original = auth.DASHBOARD_PASSWORD
        try:
            auth.DASHBOARD_PASSWORD = "secret"
            assert auth.check_password(None) is False
        finally:
            auth.DASHBOARD_PASSWORD = original

    def test_empty_config_rejects_nonempty_input(self) -> None:
        """When no password is configured, only empty string passes."""
        original = auth.DASHBOARD_PASSWORD
        try:
            auth.DASHBOARD_PASSWORD = ""
            assert auth.check_password("anything") is False
        finally:
            auth.DASHBOARD_PASSWORD = original

    def test_password_is_case_sensitive(self) -> None:
        original = auth.DASHBOARD_PASSWORD
        try:
            auth.DASHBOARD_PASSWORD = "Secret"
            assert auth.check_password("secret") is False
            assert auth.check_password("Secret") is True
        finally:
            auth.DASHBOARD_PASSWORD = original
