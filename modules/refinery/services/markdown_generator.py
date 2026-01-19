"""
Generator notatek Markdown z Jinja2 templates
"""
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import Dict
from shared.logging import get_logger

logger = get_logger(__name__)


class MarkdownGenerator:
    """Generator Markdown notes using templates"""

    def __init__(self, config=None):
        # Import config here to avoid circular imports
        if config is None:
            from config import config as default_config
            config = default_config

        self.config = config
        self.env = Environment(
            loader=FileSystemLoader(str(config.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Custom filters for Jinja2
        self.env.filters["datetime"] = self._format_datetime

    def _format_datetime(self, dt: datetime, format: str = "%Y-%m-%d %H:%M") -> str:
        """Jinja2 filter for formatting dates"""
        return dt.strftime(format)

    def generate_youtube_note(self, task_data: Dict, llm_result: Dict) -> str:
        """
        Generate note for YouTube video

        Args:
            task_data: Original data from YoutubeTask
            llm_result: Result from LLM processing

        Returns:
            Full Markdown with frontmatter
        """
        template = self.env.get_template("youtube_note.md.jinja2")

        context = {
            "title": task_data.get("title", "Untitled"),
            "url": task_data.get("url"),
            "channel": task_data.get("channel"),
            "duration_minutes": (task_data.get("duration_seconds", 0) // 60),
            "created_at": datetime.utcnow(),
            "tags": llm_result.get("tags", []),
            "category": llm_result.get("main_category", "General"),
            "summary": llm_result.get("summary", ""),
            "key_points": llm_result.get("key_points", []),
            "related_topics": llm_result.get("related_topics", []),
            "transcript": task_data.get("transcript", ""),
        }

        return template.render(**context)

    def generate_article_note(self, task_data: Dict, llm_result: Dict) -> str:
        """
        Generate note for web article
        """
        template = self.env.get_template("article_note.md.jinja2")

        context = {
            "title": task_data.get("title", "Untitled"),
            "url": task_data.get("url"),
            "author": task_data.get("author"),
            "created_at": datetime.utcnow(),
            "tags": llm_result.get("tags", []),
            "article_type": llm_result.get("article_type", "article"),
            "summary": llm_result.get("summary", ""),
            "key_points": llm_result.get("key_points", []),
            "quotes": llm_result.get("quotes", []),
            "related_topics": llm_result.get("related_topics", []),
            "content": task_data.get("content", ""),
        }

        return template.render(**context)
