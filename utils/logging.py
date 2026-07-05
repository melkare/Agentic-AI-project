"""Logging helpers for the project."""

from __future__ import annotations

import logging
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_exception(logger: logging.Logger, exc: Exception, context: str) -> None:
    """Record an exception with context."""

    logger.exception("%s: %s", context, exc)
