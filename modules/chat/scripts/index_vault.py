"""
Reindeksacja Vault (uruchamiać codziennie przez cron)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from setup_rag import VaultIndexer
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="json", service_name="vault-indexer")
logger = get_logger(__name__)


def main():
    """Reindex vault"""
    logger.info("reindexing_started")

    vault_path = Path("/vault")

    try:
        indexer = VaultIndexer(
            vault_path=vault_path,
            qdrant_url="http://qdrant:6333"
        )

        # Clear old collection
        try:
            indexer.qdrant.delete_collection(indexer.collection_name)
        except Exception:
            pass  # Collection may not exist

        # Reindex
        indexer.run()

        logger.info("reindexing_completed")

    except Exception as e:
        logger.error("reindexing_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
