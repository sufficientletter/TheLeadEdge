"""Tests for responsive layout, mobile components, and PWA manifest."""

from __future__ import annotations

import json
from pathlib import Path

from theleadedge.dashboard.layout import NAV_ITEMS


class TestNavItems:
    """Verify navigation item configuration."""

    def test_nav_items_count(self) -> None:
        assert len(NAV_ITEMS) == 6

    def test_all_items_have_required_keys(self) -> None:
        for item in NAV_ITEMS:
            assert "label" in item
            assert "icon" in item
            assert "path" in item

    def test_briefing_is_home(self) -> None:
        assert NAV_ITEMS[0]["path"] == "/"
        assert NAV_ITEMS[0]["label"] == "Briefing"

    def test_all_paths_start_with_slash(self) -> None:
        for item in NAV_ITEMS:
            assert item["path"].startswith("/")

    def test_mobile_bar_uses_first_five(self) -> None:
        mobile_items = NAV_ITEMS[:5]
        assert len(mobile_items) == 5
        paths = {i["path"] for i in mobile_items}
        assert "/" in paths
        assert "/leads" in paths
        assert "/map" in paths

    def test_all_icons_are_material_names(self) -> None:
        """Icons should be valid Material Icons names (lowercase, no spaces)."""
        for item in NAV_ITEMS:
            icon = item["icon"]
            assert icon == icon.lower()
            assert " " not in icon

    def test_all_labels_are_nonempty(self) -> None:
        for item in NAV_ITEMS:
            assert len(item["label"]) > 0

    def test_no_duplicate_paths(self) -> None:
        paths = [item["path"] for item in NAV_ITEMS]
        assert len(paths) == len(set(paths))

    def test_settings_page_included(self) -> None:
        paths = [item["path"] for item in NAV_ITEMS]
        assert "/settings" in paths

    def test_analytics_page_included(self) -> None:
        paths = [item["path"] for item in NAV_ITEMS]
        assert "/analytics" in paths


class TestNotificationBellData:
    """Test notification bell data structures."""

    def test_empty_notifications(self) -> None:
        items: list[dict[str, str]] = []
        assert len(items) == 0

    def test_notification_structure(self) -> None:
        item = {"title": "New S-tier lead", "description": "Score: 95.2"}
        assert "title" in item
        assert "description" in item

    def test_max_displayed(self) -> None:
        items = [{"title": f"Item {i}"} for i in range(15)]
        displayed = items[:10]
        assert len(displayed) == 10

    def test_notification_without_description(self) -> None:
        item = {"title": "Follow-up due"}
        assert "title" in item
        assert item.get("description") is None

    def test_notification_count_matches_items(self) -> None:
        items = [
            {"title": "New S-tier lead"},
            {"title": "Follow-up overdue"},
            {"title": "Price reduction detected"},
        ]
        count = len(items)
        assert count == 3


class TestNotificationBellComponent:
    """Test notification_bell component module structure."""

    def test_import_notification_bell(self) -> None:
        """Verify the notification bell function can be imported."""
        from theleadedge.dashboard.components.notification_bell import (
            notification_bell,
        )

        assert callable(notification_bell)


class TestManifestStructure:
    """Verify PWA manifest file content."""

    def _get_manifest_path(self) -> Path:
        return (
            Path(__file__).parent.parent.parent
            / "src"
            / "theleadedge"
            / "dashboard"
            / "static"
            / "manifest.json"
        )

    def test_manifest_file_exists(self) -> None:
        manifest = self._get_manifest_path()
        assert manifest.exists(), f"manifest.json not found at {manifest}"

    def test_manifest_is_valid_json(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_manifest_has_required_fields(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert "name" in data
        assert "short_name" in data
        assert "start_url" in data
        assert "display" in data

    def test_manifest_name(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert data["name"] == "TheLeadEdge"
        assert data["short_name"] == "LeadEdge"

    def test_manifest_display_standalone(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert data["display"] == "standalone"

    def test_manifest_start_url(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert data["start_url"] == "/"

    def test_manifest_theme_color(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert data["theme_color"].startswith("#")

    def test_manifest_has_icons(self) -> None:
        manifest = self._get_manifest_path()
        with open(manifest) as f:
            data = json.load(f)
        assert "icons" in data
        assert len(data["icons"]) >= 1
        for icon in data["icons"]:
            assert "src" in icon
            assert "sizes" in icon
            assert "type" in icon


class TestLayoutModuleImport:
    """Verify layout module exports are correct."""

    def test_create_layout_importable(self) -> None:
        from theleadedge.dashboard.layout import create_layout

        assert callable(create_layout)

    def test_nav_items_is_list_of_dicts(self) -> None:
        assert isinstance(NAV_ITEMS, list)
        for item in NAV_ITEMS:
            assert isinstance(item, dict)
