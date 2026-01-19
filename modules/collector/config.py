"""
Konfiguracja dla Collector service
"""
from pathlib import Path
import os
import sys

# Dodaj shared do path jeśli jeszcze nie zainstalowane (dla lokalnego dev bez instalacji)
# sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from shared.config import get_settings as get_base_settings


class CollectorConfig:
    """Rozszerzona konfiguracja dla Collector"""
    
    def __init__(self):
        self.base = get_base_settings()
        
        # Paths
        self.inbox_path = Path(os.getenv("INBOX_PATH", self.base.inbox_path))
        self.temp_download_path = Path("/tmp/collector_downloads")
        
        # Watchdog settings
        self.watch_patterns = ["*.txt", "*.url"]
        self.watch_ignore_patterns = [".*", "*.tmp"]
        
        # YouTube settings
        self.youtube_audio_format = "m4a"
        self.youtube_max_length_minutes = 180  # 3h limit
        
        # Whisper settings
        self.whisper_model = "medium"  # tiny, base, small, medium, large
        self.whisper_device = "cpu"  # auto, cpu, cuda
        self.whisper_language = "auto"  # auto-detect or specify
        
        # Web scraping settings
        self.web_timeout_seconds = 30
        self.web_max_content_length = 1_000_000  # 1MB
        
        # Redis queues
        self.output_queue = "queue:refinery"
        
        # Ensure paths exist
        try:
            self.temp_download_path.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Może wystąpić problem z uprawnieniami w niektórych środowiskach, ale w dockerze /tmp powinno być ok
            pass


config = CollectorConfig()
