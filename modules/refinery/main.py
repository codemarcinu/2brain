"""
Refinery Service - Main Entry Point
"""
from shared.messaging import RedisClient
from shared.logging import setup_logging, get_logger
from config import config
from services.llm_processor import LLMProcessor
from services.markdown_generator import MarkdownGenerator
from services.vault_writer import VaultWriter

setup_logging(
    level=config.base.log_level,
    format=config.base.log_format,
    service_name="refinery",
)
logger = get_logger(__name__)


class RefineryService:
    """Main Refinery service"""

    def __init__(self):
        self.redis = RedisClient()
        self.llm = LLMProcessor(
            provider=config.llm_provider,
            model=config.llm_model,
            temperature=config.llm_temperature,
            config=config,
        )
        self.markdown = MarkdownGenerator(config=config)
        self.vault = VaultWriter(config.vault_path, config=config)

        logger.info("refinery_service_initialized")

    def process_task(self, task: dict):
        """
        Process task from queue

        Args:
            task: Dict with task data (YoutubeTask or ArticleTask)
        """
        task_type = task.get("type")
        task_id = task.get("id")

        logger.info("task_processing_started", task_id=task_id, type=task_type)

        try:
            if task_type == "youtube":
                self._process_youtube(task)
            elif task_type == "article":
                self._process_article(task)
            else:
                logger.warning("unknown_task_type", task_id=task_id, type=task_type)
                return

            logger.info("task_completed", task_id=task_id)

        except Exception as e:
            logger.error("task_processing_failed", task_id=task_id, error=str(e))

    def _process_youtube(self, task: dict):
        """Process YouTube task"""
        # 1. LLM processing
        llm_result = self.llm.process_youtube(task)
        if not llm_result:
            raise Exception("LLM processing failed")

        # 2. Generate Markdown
        markdown_content = self.markdown.generate_youtube_note(task, llm_result)

        # 3. Save to Vault
        filepath = self.vault.save_youtube_note(
            markdown_content, task.get("title", "Untitled")
        )

        if not filepath:
            raise Exception("Failed to save note")

    def _process_article(self, task: dict):
        """Process Article task"""
        llm_result = self.llm.process_article(task)
        if not llm_result:
            raise Exception("LLM processing failed")

        markdown_content = self.markdown.generate_article_note(task, llm_result)

        filepath = self.vault.save_article_note(
            markdown_content, task.get("title", "Untitled")
        )

        if not filepath:
            raise Exception("Failed to save note")


def main():
    """Main loop - listen on queue"""
    logger.info("refinery_service_starting")

    service = RefineryService()

    logger.info(
        "refinery_listening",
        queue=config.input_queue,
        llm_provider=config.llm_provider,
        llm_model=config.llm_model,
    )

    try:
        # Listen to Redis queue
        service.redis.listen_to_queue(
            queue_name=config.input_queue, callback=service.process_task
        )
    except KeyboardInterrupt:
        logger.info("refinery_service_shutting_down")


if __name__ == "__main__":
    main()
