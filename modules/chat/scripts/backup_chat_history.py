"""
Backup Open Web UI chat history
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="json", service_name="chat-backup")
logger = get_logger(__name__)


def main():
    """Backup chat history"""
    source_path = Path("/app/backend/data")
    backup_dir = Path(os.getenv("BACKUP_PATH", "/backups"))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"chat_backup_{timestamp}"

    try:
        if not source_path.exists():
            logger.error("source_not_found", path=str(source_path))
            return

        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_path, backup_path)

        logger.info(
            "backup_completed",
            source=str(source_path),
            destination=str(backup_path)
        )

    except Exception as e:
        logger.error("backup_failed", error=str(e))


if __name__ == "__main__":
    main()
