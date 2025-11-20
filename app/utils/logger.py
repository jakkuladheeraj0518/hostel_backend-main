"""
Logging setup (loguru)
"""
import logging
import sys
from loguru import logger as loguru_logger


def setup_logger():
    """Setup logging with loguru"""
    loguru_logger.remove()
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    loguru_logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG"
    )
    return loguru_logger

