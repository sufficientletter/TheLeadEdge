"""Structured logging configuration for TheLeadEdge.

Uses structlog with stdlib integration so that all Python loggers
(including third-party libraries) flow through the same pipeline.

Usage:
    from theleadedge.utils.logging import setup_logging, get_logger

    setup_logging(log_level="INFO", json_output=False)
    logger = get_logger(__name__)
    logger.info("pipeline started", source="mls_csv", record_count=42)

IMPORTANT: Never log PII (client names, phone numbers, email addresses,
home addresses). Sanitize all data before passing to log calls.
"""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(log_level: str = "DEBUG", json_output: bool = False) -> None:
    """Configure structlog for the application.

    Args:
        log_level: Root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_output: If True, emit JSON lines (for production).
                     If False, emit colored console output (for development).
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # Quiet noisy third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a configured structlog logger.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        A bound structlog logger instance.
    """
    return structlog.get_logger(name)
