"""
Obsidian Brain Shared Library
Wspólny kod dla wszystkich mikroserwisów
"""

__version__ = "2.0.0"

from .messaging import RedisClient, TaskQueue
from .types import (
    ArticleTask,
    YoutubeTask,
    ReceiptTask,
    ProcessedNote,
    TaskStatus,
)
from .config import Settings, get_settings
from .logging import setup_logging, get_logger

__all__ = [
    "RedisClient",
    "TaskQueue",
    "ArticleTask",
    "YoutubeTask",
    "ReceiptTask",
    "ProcessedNote",
    "TaskStatus",
    "Settings",
    "get_settings",
    "setup_logging",
    "get_logger",
]
