"""Structured logging configuration."""
from __future__ import annotations
import logging
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from app.config import settings

def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or "trading-ai")
    if not logger.handlers:
        console = Console(stderr=True)
        handler = RichHandler(console=console, rich_tracebacks=True, tracebacks_show_locals=True)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        logger.propagate = False
    return logger
