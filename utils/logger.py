"""
Logging utilities for Trading-AI.

Provides a configured logger factory function so modules can obtain
consistent loggers throughout the application.
"""
from __future__ import annotations

import logging
import sys
from logging import Logger
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> Logger:
    """Create and return a configured logger.

    Args:
        name: Logger name (usually __name__ of calling module).
        level: Logging level (default logging.INFO).

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        # Already configured
        logger.setLevel(level)
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    return logger
