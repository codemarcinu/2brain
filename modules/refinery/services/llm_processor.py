"""
LLM wrapper supporting multiple providers
"""
import json
from typing import Dict, Optional, Literal
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from shared.logging import get_logger

logger = get_logger(__name__)

LLMProvider = Literal["ollama", "openai", "gemini"]


class LLMProcessor:
    """Wrapper for different LLM providers"""

    def __init__(
        self,
        provider: LLMProvider = "ollama",
        model: Optional[str] = None,
        temperature: float = 0.3,
        config=None,
    ):
        # Import config here to avoid circular imports
        if config is None:
            from config import config as default_config
            config = default_config

        self.provider = provider
        self.model = model or config.llm_model
        self.temperature = temperature
        self.config = config

        # Initialize provider
        if provider == "ollama":
            self.llm = ChatOllama(
                base_url=config.base.ollama_host,
                model=self.model,
                temperature=temperature,
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                api_key=config.base.openai_api_key,
                model=self.model,
                temperature=temperature,
            )
        elif provider == "gemini":
            # Implementation for Gemini
            raise NotImplementedError("Gemini provider not yet implemented")

        logger.info(
            "llm_initialized",
            provider=provider,
            model=self.model,
            temperature=temperature,
        )

    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt template from file"""
        prompt_file = self.config.prompts_path / f"{prompt_name}.txt"
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """
        Safe parsing of JSON response (LLM sometimes adds ``` etc.)
        """
        try:
            # Remove potential markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith("```"):
                # Find first { and last }
                start = cleaned.find("{")
                end = cleaned.rfind("}") + 1
                if start != -1 and end != 0:
                    cleaned = cleaned[start:end]

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("json_parse_failed", error=str(e), response=response[:200])
            return None

    def process_youtube(self, task_data: Dict) -> Optional[Dict]:
        """
        Process YouTube transcript

        Args:
            task_data: Dict with YoutubeTask (title, channel, transcript)

        Returns:
            Dict with summary, key_points, tags, etc.
        """
        logger.info("llm_youtube_processing", task_id=task_data.get("id"))

        try:
            # Load prompt
            prompt_template = self._load_prompt("youtube_summary")

            # Prepare data
            prompt = prompt_template.format(
                title=task_data.get("title", "Untitled"),
                channel=task_data.get("channel", "Unknown"),
                duration=task_data.get("duration_seconds", 0),
                transcript=task_data.get("transcript", "")[
                    : self.config.max_content_length
                ],
            )

            # Call LLM
            response = self.llm.invoke(prompt)

            # Parse JSON
            result = self._parse_json_response(response.content)

            if result:
                logger.info(
                    "llm_youtube_success",
                    task_id=task_data.get("id"),
                    tags_count=len(result.get("tags", [])),
                )
                return result
            else:
                logger.error("llm_youtube_invalid_json", task_id=task_data.get("id"))
                return None

        except Exception as e:
            logger.error(
                "llm_youtube_failed", task_id=task_data.get("id"), error=str(e)
            )
            return None

    def process_article(self, task_data: Dict) -> Optional[Dict]:
        """
        Process web article

        Args:
            task_data: Dict with ArticleTask (title, content, author)

        Returns:
            Dict with summary, key_points, tags, etc.
        """
        logger.info("llm_article_processing", task_id=task_data.get("id"))

        try:
            prompt_template = self._load_prompt("article_summary")

            prompt = prompt_template.format(
                title=task_data.get("title", "Untitled"),
                author=task_data.get("author", "Unknown"),
                url=task_data.get("url", ""),
                content=task_data.get("content", "")[: self.config.max_content_length],
            )

            response = self.llm.invoke(prompt)
            result = self._parse_json_response(response.content)

            if result:
                logger.info(
                    "llm_article_success",
                    task_id=task_data.get("id"),
                    article_type=result.get("article_type"),
                )
                return result
            else:
                logger.error("llm_article_invalid_json", task_id=task_data.get("id"))
                return None

        except Exception as e:
            logger.error(
                "llm_article_failed", task_id=task_data.get("id"), error=str(e)
            )
            return None
