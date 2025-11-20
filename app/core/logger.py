"""Simple logger setup for the application."""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


def setup_logger(name: str = "app") -> logging.Logger:
    """Configure and return a logger for the application.

    - Writes rotating file logs to `logs/app.log`.
    - Also emits to console (stderr).
    - Respects `settings.DEBUG` for log level.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid adding handlers multiple times in interactive / reload environments
    if logger.handlers:
        return logger

    # Ensure logs directory exists
    logs_dir = Path("logs")
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If we can't create logs dir, fall back to console-only logging
        pass

    # File handler (rotating)
    try:
        file_handler = RotatingFileHandler(
            filename=str(logs_dir / "app.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception:
        # ignore file handler errors
        pass

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Do not propagate to root logger to avoid duplicate messages
    logger.propagate = False

    return logger
