"""
Zapis notatek do Obsidian Vault
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from shared.logging import get_logger
from shared.utils import sanitize_filename

logger = get_logger(__name__)


class VaultWriter:
    """Writer for Obsidian Vault"""

    def __init__(self, vault_path: Path, config=None):
        self.vault_path = vault_path

        # Import config here to avoid circular imports
        if config is None:
            from config import config as default_config
            config = default_config

        self.config = config

    def _generate_filename(self, title: str, prefix: str = "") -> str:
        """
        Generate safe filename

        Args:
            title: Note title
            prefix: Optional prefix (e.g., date)

        Returns:
            Filename with .md extension
        """
        safe_title = sanitize_filename(title, max_length=80)

        if prefix:
            return f"{prefix}_{safe_title}.md"
        else:
            return f"{safe_title}.md"

    def _ensure_unique_filename(self, folder: Path, filename: str) -> Path:
        """
        Ensure filename is unique (add timestamp if conflict)
        """
        filepath = folder / filename

        if not filepath.exists():
            return filepath

        # Conflict - add timestamp
        stem = filepath.stem
        suffix = filepath.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{stem}_{timestamp}{suffix}"

        logger.warning(
            "filename_conflict_resolved", original=filename, new=new_filename
        )

        return folder / new_filename

    def save_youtube_note(self, content: str, title: str) -> Optional[Path]:
        """
        Save YouTube note to Vault

        Args:
            content: Full Markdown with frontmatter
            title: Video title

        Returns:
            Path to saved file or None if error
        """
        try:
            # Generate filename
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            filename = self._generate_filename(title, prefix=date_prefix)

            # Ensure folder exists
            self.config.youtube_folder.mkdir(parents=True, exist_ok=True)

            # Unique path
            filepath = self._ensure_unique_filename(self.config.youtube_folder, filename)

            # Save
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(
                "note_saved",
                type="youtube",
                path=str(filepath.relative_to(self.vault_path)),
            )

            return filepath

        except Exception as e:
            logger.error("note_save_failed", type="youtube", error=str(e))
            return None

    def save_article_note(self, content: str, title: str) -> Optional[Path]:
        """Save article note"""
        try:
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            filename = self._generate_filename(title, prefix=date_prefix)

            self.config.articles_folder.mkdir(parents=True, exist_ok=True)
            filepath = self._ensure_unique_filename(
                self.config.articles_folder, filename
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(
                "note_saved",
                type="article",
                path=str(filepath.relative_to(self.vault_path)),
            )

            return filepath

        except Exception as e:
            logger.error("note_save_failed", type="article", error=str(e))
            return None
