"""
Konfiguracja dla Refinery service
"""
from pathlib import Path
from shared.config import get_settings as get_base_settings


class RefineryConfig:
    """Rozszerzona konfiguracja dla Refinery"""

    def __init__(self):
        self.base = get_base_settings()

        # Paths
        self.vault_path = Path(self.base.obsidian_vault_path)
        self.templates_path = Path(__file__).parent / "templates"
        self.prompts_path = Path(__file__).parent / "prompts"

        # Output folders w Vault
        self.youtube_folder = self.vault_path / "YouTube"
        self.articles_folder = self.vault_path / "Articles"
        self.web_clips_folder = self.vault_path / "Web Clips"

        # LLM Settings
        self.llm_provider = "ollama"  # ollama, openai, gemini
        self.llm_model = self.base.ollama_model
        self.llm_temperature = 0.3  # Lower = more deterministic
        self.llm_max_tokens = 2000

        # Processing settings
        self.max_content_length = 50000  # Limit for long content
        self.summary_target_words = 300  # Target summary length

        # Redis queues
        self.input_queue = "queue:refinery"

        # Ensure folders exist
        for folder in [self.youtube_folder, self.articles_folder, self.web_clips_folder]:
            folder.mkdir(parents=True, exist_ok=True)


config = RefineryConfig()
