"""
Konfiguracja Finance Service
"""
from pathlib import Path
from shared.config import get_settings as get_base_settings


class FinanceConfig:
    """Rozszerzona konfiguracja dla Finance"""

    def __init__(self):
        self.base = get_base_settings()

        # Paths
        self.receipts_folder = Path("/inbox/receipts")  # Mounted volume
        self.temp_uploads = Path("/tmp/finance_uploads")

        # OCR Settings
        self.ocr_language = "pol+eng"  # Tesseract language
        self.ocr_dpi = 300  # Target DPI for preprocessing

        # LLM Settings (DeepSeek dla structured parsing)
        self.llm_api_key = self.base.deepseek_api_key or self.base.openai_api_key
        self.llm_model = "deepseek-chat"  # lub gpt-4o-mini
        self.llm_base_url = "https://api.deepseek.com"  # lub OpenAI

        # Database
        self.database_url = self.base.postgres_url

        # Obsidian integration (optional)
        self.vault_path = Path(self.base.obsidian_vault_path)
        self.expenses_note_path = self.vault_path / "Finance" / "Monthly Expenses"

        # UI Settings
        self.page_title = "Obsidian Brain - Finance Manager"
        self.page_icon = "💰"

        # Ensure paths exist
        self.receipts_folder.mkdir(parents=True, exist_ok=True)
        self.temp_uploads.mkdir(parents=True, exist_ok=True)
        self.expenses_note_path.parent.mkdir(parents=True, exist_ok=True)


config = FinanceConfig()
