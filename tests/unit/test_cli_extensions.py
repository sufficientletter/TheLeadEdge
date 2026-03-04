"""Tests for Phase 2 CLI extensions in main.py.

Verifies that all expected subcommands are registered in the argument
parser and that arguments are parsed correctly.

These tests validate parser configuration only -- they do not invoke
actual pipeline logic.
"""

from __future__ import annotations

from theleadedge.main import build_parser

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_parser_has_all_commands() -> None:
    """build_parser() should register all 12 CLI subcommands."""
    import argparse

    parser = build_parser()
    # Extract the subparsers action to get registered choices
    subparsers_actions = [
        action
        for action in parser._subparsers._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    assert len(subparsers_actions) == 1
    choices = set(subparsers_actions[0].choices.keys())

    expected = {
        "import",
        "score",
        "briefing",
        "run",
        "download-redfin",
        "enrich",
        "import-public-records",
        "scheduler",
        "health",
        "data-health",
        "match-records",
        "download-pa",
    }
    assert choices == expected


def test_health_command_exists() -> None:
    """The 'health' subcommand should be accepted by the parser."""
    parser = build_parser()
    args = parser.parse_args(["health"])
    assert args.command == "health"


def test_download_pa_command_exists() -> None:
    """The 'download-pa' subcommand should be accepted by the parser."""
    parser = build_parser()
    args = parser.parse_args(["download-pa"])
    assert args.command == "download-pa"


def test_enrich_tier_argument() -> None:
    """The enrich command should parse --tier correctly."""
    parser = build_parser()

    # Default
    args = parser.parse_args(["enrich"])
    assert args.tier == "S,A"

    # Custom
    args = parser.parse_args(["enrich", "--tier", "S,A,B"])
    assert args.tier == "S,A,B"


def test_scheduler_command_exists() -> None:
    """The 'scheduler' subcommand should be accepted by the parser."""
    parser = build_parser()
    args = parser.parse_args(["scheduler"])
    assert args.command == "scheduler"


def test_data_health_command_exists() -> None:
    """The 'data-health' subcommand should be accepted by the parser."""
    parser = build_parser()
    args = parser.parse_args(["data-health"])
    assert args.command == "data-health"


def test_match_records_command_exists() -> None:
    """The 'match-records' subcommand should be accepted by the parser."""
    parser = build_parser()
    args = parser.parse_args(["match-records"])
    assert args.command == "match-records"
