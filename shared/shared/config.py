"""
Centralna konfiguracja dla wszystkich serwisów
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Konfiguracja z zmiennych środowiskowych
    """
    
    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    # PostgreSQL
    postgres_user: str = "brain"
    postgres_password: str = "changeme"
    postgres_db: str = "obsidian_brain"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    
    # Ollama
    ollama_host: str = "http://ollama:11434"
    ollama_model: str = "deepseek-r1:14b"
    
    # WebUI
    webui_secret_key: str = "changeme"
    
    # API Keys (opcjonalne)
    openai_api_key: str = ""
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    
    # Paths
    obsidian_vault_path: str = "/vault"
    inbox_path: str = "/inbox"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json | console
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def postgres_url(self) -> str:
        """Database URL for SQLAlchemy"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Singleton settings (cache)
    """
    return Settings()
