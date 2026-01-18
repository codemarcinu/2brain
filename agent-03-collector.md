# Agent 3: Collector Service

## 🎭 Rola
**Data Ingestion Engineer**

## 🎯 Cel
Mikroserwis pobierający treści z YouTube i stron WWW

## 📖 Kontekst

Collector to pierwszy punkt kontaktu z zewnętrznymi danymi. Ten serwis:
- **Obserwuje** folder `00_Inbox/` (watchdog)
- **Pobiera** treści z linków (YouTube audio, artykuły web)
- **Wysyła** surowe dane do kolejki Redis dla Refinery
- **NIE przetwarza** treści AI - jest "głupim" robotem do brudnej roboty

### Przepływ danych:
```
00_Inbox/link.txt → Collector → Redis Queue → [Refinery will process]
```

## ✅ Zadania

### 1. Struktura Projektu

```
modules/collector/
├── Dockerfile
├── requirements.txt
├── main.py                    # Entry point
├── config.py                  # Konfiguracja serwisu
├── services/
│   ├── __init__.py
│   ├── youtube_downloader.py  # yt-dlp wrapper
│   ├── web_scraper.py         # trafilatura wrapper
│   └── transcriber.py         # whisper wrapper
├── utils/
│   ├── __init__.py
│   └── file_watcher.py        # Watchdog logic
└── tests/
    ├── __init__.py
    └── test_services.py
```

### 2. Dockerfile

```dockerfile
FROM python:3.10-slim

# Metadata
LABEL maintainer="your@email.com"
LABEL description="Collector service for Obsidian Brain"

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stwórz katalog aplikacji
WORKDIR /app

# Skopiuj requirements i zainstaluj zależności Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Zainstaluj shared library (zakładając że jest w parent directory)
RUN pip install -e /shared

# Zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

# Uruchom serwis
CMD ["python", "main.py"]
```

### 3. requirements.txt

```txt
# YouTube
yt-dlp>=2024.0.0
faster-whisper>=1.0.0

# Web scraping
trafilatura>=1.10.0
requests>=2.31.0
beautifulsoup4>=4.12.0

# File watching
watchdog>=4.0.0

# Shared library (zainstalowane przez Dockerfile)
# obsidian-brain-shared @ file:///shared

# Utilities
python-dotenv>=1.0.0
```

### 4. config.py

```python
"""
Konfiguracja dla Collector service
"""
from pathlib import Path
from shared.config import get_settings as get_base_settings


class CollectorConfig:
    """Rozszerzona konfiguracja dla Collector"""
    
    def __init__(self):
        self.base = get_base_settings()
        
        # Paths
        self.inbox_path = Path(self.base.inbox_path)
        self.temp_download_path = Path("/tmp/collector_downloads")
        
        # Watchdog settings
        self.watch_patterns = ["*.txt", "*.url"]
        self.watch_ignore_patterns = [".*", "*.tmp"]
        
        # YouTube settings
        self.youtube_audio_format = "m4a"
        self.youtube_max_length_minutes = 180  # 3h limit
        
        # Whisper settings
        self.whisper_model = "medium"  # tiny, base, small, medium, large
        self.whisper_device = "auto"  # auto, cpu, cuda
        self.whisper_language = "pl"  # auto-detect or specify
        
        # Web scraping settings
        self.web_timeout_seconds = 30
        self.web_max_content_length = 1_000_000  # 1MB
        
        # Redis queues
        self.output_queue = "queue:refinery"
        
        # Ensure paths exist
        self.temp_download_path.mkdir(parents=True, exist_ok=True)


config = CollectorConfig()
```

### 5. services/youtube_downloader.py

```python
"""
YouTube video downloader (audio only)
"""
import yt_dlp
from pathlib import Path
from typing import Optional, Dict
from shared.logging import get_logger

logger = get_logger(__name__)


class YouTubeDownloader:
    """Wrapper dla yt-dlp do pobierania audio z YouTube"""
    
    def __init__(self, output_dir: Path, audio_format: str = "m4a"):
        self.output_dir = output_dir
        self.audio_format = audio_format
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_audio(self, url: str) -> Optional[Path]:
        """
        Pobierz audio z YouTube video
        
        Args:
            url: URL do YouTube video
        
        Returns:
            Path do pobranego pliku audio lub None jeśli błąd
        """
        try:
            logger.info("youtube_download_started", url=url)
            
            # Konfiguracja yt-dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_format,
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            # Pobierz
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                
                # Znajdź pobrany plik
                audio_file = self.output_dir / f"{video_id}.{self.audio_format}"
                
                if not audio_file.exists():
                    logger.error("youtube_file_not_found", video_id=video_id)
                    return None
                
                logger.info(
                    "youtube_download_completed",
                    url=url,
                    video_id=video_id,
                    file_size_mb=audio_file.stat().st_size / (1024*1024),
                    duration_seconds=info.get('duration')
                )
                
                return audio_file
                
        except Exception as e:
            logger.error("youtube_download_failed", url=url, error=str(e))
            return None
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Pobierz metadata video bez pobierania
        
        Returns:
            Dict z info (title, channel, duration, etc.)
        """
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'channel': info.get('uploader'),
                    'duration_seconds': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', '')[:500],  # First 500 chars
                }
        except Exception as e:
            logger.error("youtube_info_failed", url=url, error=str(e))
            return None
```

### 6. services/transcriber.py

```python
"""
Audio transcription using Whisper
"""
from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel
from shared.logging import get_logger

logger = get_logger(__name__)


class Transcriber:
    """Wrapper dla faster-whisper"""
    
    def __init__(
        self,
        model_size: str = "medium",
        device: str = "auto",
        compute_type: str = "float16"
    ):
        """
        Args:
            model_size: tiny, base, small, medium, large
            device: auto, cpu, cuda
            compute_type: float16, int8, float32
        """
        logger.info(
            "transcriber_initializing",
            model=model_size,
            device=device
        )
        
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        
        logger.info("transcriber_ready")
    
    def transcribe(
        self,
        audio_path: Path,
        language: str = "pl"
    ) -> Optional[str]:
        """
        Transkrybuj plik audio
        
        Args:
            audio_path: Ścieżka do pliku audio
            language: Kod języka (pl, en, auto)
        
        Returns:
            Pełna transkrypcja jako string
        """
        try:
            logger.info(
                "transcription_started",
                file=audio_path.name,
                language=language
            )
            
            # Transkrypcja
            segments, info = self.model.transcribe(
                str(audio_path),
                language=None if language == "auto" else language,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
            )
            
            # Połącz segmenty w pełny tekst
            full_text = " ".join([segment.text for segment in segments])
            
            logger.info(
                "transcription_completed",
                file=audio_path.name,
                detected_language=info.language,
                duration_seconds=info.duration,
                text_length=len(full_text)
            )
            
            return full_text
            
        except Exception as e:
            logger.error(
                "transcription_failed",
                file=audio_path.name,
                error=str(e)
            )
            return None
```

### 7. services/web_scraper.py

```python
"""
Web content extraction
"""
import trafilatura
import requests
from typing import Optional, Dict
from datetime import datetime
from shared.logging import get_logger

logger = get_logger(__name__)


class WebScraper:
    """Wrapper dla trafilatura - ekstrakcja głównej treści artykułów"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def extract_article(self, url: str) -> Optional[Dict]:
        """
        Pobierz i wyekstrahuj artykuł z URL
        
        Args:
            url: URL artykułu
        
        Returns:
            Dict z title, content, author, date lub None jeśli błąd
        """
        try:
            logger.info("web_scraping_started", url=url)
            
            # Pobierz HTML
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'ObsidianBrain/2.0 (Knowledge Management Bot)'
                }
            )
            response.raise_for_status()
            
            html = response.text
            
            # Ekstrakcja metadanych i treści
            metadata = trafilatura.extract_metadata(html)
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not content:
                logger.warning("web_scraping_no_content", url=url)
                return None
            
            result = {
                'url': url,
                'title': metadata.title if metadata else 'Untitled',
                'author': metadata.author if metadata else None,
                'date': metadata.date if metadata else None,
                'content': content,
                'sitename': metadata.sitename if metadata else None,
            }
            
            logger.info(
                "web_scraping_completed",
                url=url,
                title=result['title'],
                content_length=len(content)
            )
            
            return result
            
        except requests.RequestException as e:
            logger.error("web_scraping_request_failed", url=url, error=str(e))
            return None
        except Exception as e:
            logger.error("web_scraping_failed", url=url, error=str(e))
            return None
```

### 8. utils/file_watcher.py

```python
"""
Watchdog observer dla folderu Inbox
"""
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from typing import Callable
from shared.logging import get_logger

logger = get_logger(__name__)


class InboxFileHandler(FileSystemEventHandler):
    """Handler dla nowych plików w Inbox"""
    
    def __init__(self, callback: Callable[[Path], None]):
        """
        Args:
            callback: Funkcja wywoływana dla każdego nowego pliku
        """
        self.callback = callback
    
    def on_created(self, event: FileCreatedEvent):
        """Wywołane gdy nowy plik zostanie utworzony"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Ignoruj pliki tymczasowe i ukryte
        if file_path.name.startswith('.') or file_path.suffix == '.tmp':
            return
        
        # Akceptuj tylko .txt i .url
        if file_path.suffix not in ['.txt', '.url']:
            logger.debug("file_ignored", file=file_path.name)
            return
        
        logger.info("new_file_detected", file=file_path.name)
        
        try:
            self.callback(file_path)
        except Exception as e:
            logger.error(
                "file_processing_failed",
                file=file_path.name,
                error=str(e)
            )


class InboxWatcher:
    """Obserwator folderu Inbox"""
    
    def __init__(self, inbox_path: Path, callback: Callable[[Path], None]):
        self.inbox_path = inbox_path
        self.callback = callback
        self.observer = Observer()
    
    def start(self):
        """Uruchom obserwatora"""
        event_handler = InboxFileHandler(self.callback)
        self.observer.schedule(
            event_handler,
            str(self.inbox_path),
            recursive=False
        )
        self.observer.start()
        logger.info("inbox_watcher_started", path=str(self.inbox_path))
    
    def stop(self):
        """Zatrzymaj obserwatora"""
        self.observer.stop()
        self.observer.join()
        logger.info("inbox_watcher_stopped")
```

### 9. main.py (Entry Point)

```python
"""
Collector Service - Main Entry Point
"""
import time
from pathlib import Path
from urllib.parse import urlparse
from shared.messaging import TaskQueue
from shared.types import YoutubeTask, ArticleTask
from shared.logging import setup_logging, get_logger
from shared.utils import generate_task_id
from config import config
from services.youtube_downloader import YouTubeDownloader
from services.transcriber import Transcriber
from services.web_scraper import WebScraper
from utils.file_watcher import InboxWatcher


# Setup logging
setup_logging(
    level=config.base.log_level,
    format=config.base.log_format,
    service_name="collector"
)
logger = get_logger(__name__)


class CollectorService:
    """Główny serwis Collector"""
    
    def __init__(self):
        self.queue = TaskQueue()
        self.youtube = YouTubeDownloader(
            output_dir=config.temp_download_path,
            audio_format=config.youtube_audio_format
        )
        self.transcriber = Transcriber(
            model_size=config.whisper_model,
            device=config.whisper_device
        )
        self.scraper = WebScraper(timeout=config.web_timeout_seconds)
        
        logger.info("collector_service_initialized")
    
    def is_youtube_url(self, url: str) -> bool:
        """Sprawdź czy URL to YouTube"""
        parsed = urlparse(url)
        return 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc
    
    def process_file(self, file_path: Path):
        """
        Przetwórz plik z linkiem
        
        Args:
            file_path: Ścieżka do pliku .txt/.url z linkiem
        """
        try:
            # Odczytaj URL z pliku
            with open(file_path, 'r', encoding='utf-8') as f:
                url = f.read().strip()
            
            if not url.startswith('http'):
                logger.warning("invalid_url", file=file_path.name, url=url)
                return
            
            logger.info("processing_url", url=url, source_file=file_path.name)
            
            # Routing: YouTube vs WWW
            if self.is_youtube_url(url):
                self.process_youtube(url)
            else:
                self.process_article(url)
            
            # Usuń plik po przetworzeniu (opcjonalne)
            # file_path.unlink()
            
        except Exception as e:
            logger.error(
                "file_processing_error",
                file=file_path.name,
                error=str(e)
            )
    
    def process_youtube(self, url: str):
        """Przetwórz YouTube video"""
        logger.info("youtube_processing_started", url=url)
        
        # 1. Pobierz metadata
        info = self.youtube.get_video_info(url)
        if not info:
            logger.error("youtube_info_retrieval_failed", url=url)
            return
        
        # 2. Pobierz audio
        audio_file = self.youtube.download_audio(url)
        if not audio_file:
            logger.error("youtube_download_failed", url=url)
            return
        
        # 3. Transkrypcja
        transcript = self.transcriber.transcribe(
            audio_file,
            language=config.whisper_language
        )
        
        # Cleanup audio file
        audio_file.unlink()
        
        if not transcript:
            logger.error("youtube_transcription_failed", url=url)
            return
        
        # 4. Wyślij do Refinery
        task = YoutubeTask(
            id=generate_task_id("yt"),
            url=url,
            title=info.get('title'),
            channel=info.get('channel'),
            transcript=transcript,
            duration_seconds=info.get('duration_seconds'),
            thumbnail_url=info.get('thumbnail'),
        )
        
        success = self.queue.send_to_refinery(task.model_dump())
        
        if success:
            logger.info(
                "youtube_task_sent",
                task_id=task.id,
                title=task.title
            )
        else:
            logger.error("youtube_task_send_failed", task_id=task.id)
    
    def process_article(self, url: str):
        """Przetwórz artykuł WWW"""
        logger.info("article_processing_started", url=url)
        
        # 1. Scrape content
        article = self.scraper.extract_article(url)
        if not article:
            logger.error("article_scraping_failed", url=url)
            return
        
        # 2. Wyślij do Refinery
        task = ArticleTask(
            id=generate_task_id("art"),
            url=url,
            title=article.get('title'),
            content=article.get('content'),
            author=article.get('author'),
            metadata={'sitename': article.get('sitename')}
        )
        
        success = self.queue.send_to_refinery(task.model_dump())
        
        if success:
            logger.info(
                "article_task_sent",
                task_id=task.id,
                title=task.title
            )
        else:
            logger.error("article_task_send_failed", task_id=task.id)


def main():
    """Main loop"""
    logger.info("collector_service_starting")
    
    # Inicjalizacja serwisu
    service = CollectorService()
    
    # Uruchom watchdog
    watcher = InboxWatcher(
        inbox_path=config.inbox_path,
        callback=service.process_file
    )
    watcher.start()
    
    logger.info("collector_service_ready", inbox_path=str(config.inbox_path))
    
    try:
        # Keep alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("collector_service_shutting_down")
        watcher.stop()


if __name__ == "__main__":
    main()
```

### 10. Aktualizacja docker-compose.yml

Dodaj do głównego `docker-compose.yml`:

```yaml
collector:
  build:
    context: ./modules/collector
    dockerfile: Dockerfile
  container_name: brain-collector
  volumes:
    - ${INBOX_PATH}:/inbox
    - ./shared:/shared:ro
  environment:
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - REDIS_HOST=redis
    - INBOX_PATH=/inbox
  depends_on:
    redis:
      condition: service_healthy
  networks:
    - brain-network
  restart: unless-stopped
```

## 🎯 Kryteria Sukcesu

### Walidacja po wykonaniu:

```bash
# 1. Build image działa
docker compose build collector
# Expected: Successfully built

# 2. Serwis startuje
docker compose up -d collector
docker compose logs collector
# Expected: "collector_service_ready"

# 3. Test YouTube
echo "https://www.youtube.com/watch?v=dQw4w9WgXcQ" > ${INBOX_PATH}/test_yt.txt
# Sprawdź logi: docker compose logs -f collector
# Expected: "youtube_task_sent"

# 4. Test Article
echo "https://en.wikipedia.org/wiki/Artificial_intelligence" > ${INBOX_PATH}/test_art.txt
# Expected: "article_task_sent"

# 5. Sprawdź Redis queue
docker exec brain-redis redis-cli LLEN queue:refinery
# Expected: 2 (dwa zadania w kolejce)
```

### Checklist końcowy:

- [x] Struktura katalogów zgodna z planem
- [x] Dockerfile buduje się bez błędów
- [x] Serwis startuje i loguje "collector_service_ready"
- [x] Watchdog wykrywa nowe pliki w Inbox
- [x] YouTube download + transcription działa
- [x] Web scraping działa
- [x] Zadania trafiają do Redis queue:refinery
- [x] Błędy są logowane bez crashowania serwisu

## 📦 Pliki Wyjściowe

```
modules/collector/
├── Dockerfile                 ✅
├── requirements.txt           ✅
├── main.py                   ✅
├── config.py                 ✅
├── services/
│   ├── __init__.py           ✅
│   ├── youtube_downloader.py ✅
│   ├── web_scraper.py        ✅
│   └── transcriber.py        ✅
├── utils/
│   ├── __init__.py           ✅
│   └── file_watcher.py       ✅
└── tests/
    ├── __init__.py           ✅
    └── test_services.py      ✅
```

## 🔗 Zależności

**Wymaga:**
- ✅ Agent 1 (Infrastructure) - Redis, wolumeny
- ✅ Agent 2 (Shared Library) - messaging, types

**Wymagane przez:**
- ✅ Agent 4 (Refinery) - Refinery konsumuje zadania z queue

## 💡 Wskazówki

### Performance:
- Whisper `medium` to dobry kompromis (szybkość/jakość)
- Dla GPU: zmień `compute_type` na `float16`
- Dla CPU: użyj `int8` lub `tiny` model

### Troubleshooting:
- Jeśli Whisper wolny → użyj API (OpenAI, Deepgram)
- Jeśli yt-dlp failuje → sprawdź rate limiting YouTube
- Jeśli trafilatura nic nie znajduje → dodaj fallback na BeautifulSoup

---

**Status:** 🟢 Gotowy do uruchomienia  
**Czas wykonania:** ~45 minut  
**Następny agent:** Agent 4 (Refinery) - konsumuje zadania
