"""
Collector Service - Main Entry Point
"""
import time
import signal
import sys
import json
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
    


    def process_receipt(self, file_path: Path):
        """Przetwórz paragon/fakturę (obraz/PDF)"""
        logger.info("receipt_processing_started", file=file_path.name)
        
        # Przygotuj payload dla Finance Service
        # Finance oczekuje: { "id": "...", "file_path": "/inbox/..." }
        
        # Uwaga: file_path musi być ścieżką widoczną w kontenerze Finance.
        # Oba kontenery mają mapowanie wolumenu na /inbox.
        # Zakładamy, że file_path jest absolutną ścieżką w kontenerze Collector (/inbox/...)
        
        task_payload = {
            "id": generate_task_id("fin"),
            "file_path": str(file_path),
            "timestamp": time.time()
        }
        
        # Wyślij bezpośrednio do Redis (kolejka queue:finance)
        # TaskQueue w shared lib domyślnie obsługuje tylko queue:refinery w metodzie send_to_refinery
        # więc użyjemy surowego klienta redis z self.queue.redis
        
        try:
            self.queue.redis.rpush("queue:finance", json.dumps(task_payload))
            logger.info("finance_task_sent", file=file_path.name)
        except Exception as e:
            logger.error("finance_task_send_failed", file=file_path.name, error=str(e))
            
    def process_file(self, file_path: Path):
        """
        Przetwórz plik z linkiem lub obraz
        """
        try:
            # 1. Sprawdź czy to obraz/PDF (Paragon)
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.pdf']:
                self.process_receipt(file_path)
                return

            # 2. Jeśli tekstowy, odczytaj URL
            with open(file_path, 'r', encoding='utf-8') as f:
                url = f.read().strip()
            
            # Basic validation
            if not url or not url.startswith('http'):
                logger.warning("invalid_url_in_file", file=file_path.name, content=url[:50] if url else "empty")
                return
            
            logger.info("processing_url", url=url, source_file=file_path.name)
            
            # Routing: YouTube vs WWW
            if self.is_youtube_url(url):
                self.process_youtube(url)
            else:
                self.process_article(url)
            
            # Usuń plik po przetworzeniu (dla linków)
            # Dla obrazów (paragonów) też możemy usunąć, bo Finance sobie poradzi?
            # NIE - Finance potrzebuje pliku! Finance go usunie lub zarchiwizuje.
            # Więc usuwamy TYLKO pliki tekstowe z linkami.
            try:
                file_path.unlink()
                logger.info("source_file_deleted", file=file_path.name)
            except OSError as e:
                logger.error("failed_to_delete_file", file=file_path.name, error=str(e))
            
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
        
        try:
            # 3. Transkrypcja
            transcript = self.transcriber.transcribe(
                audio_file,
                language=config.whisper_language
            )
            
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
            
            success = self.queue.send_to_refinery(task.model_dump(mode='json'))
            
            if success:
                logger.info(
                    "youtube_task_sent",
                    task_id=task.id,
                    title=task.title
                )
            else:
                logger.error("youtube_task_send_failed", task_id=task.id)
                
        finally:
            # Cleanup audio file always
            if audio_file and audio_file.exists():
                audio_file.unlink()
    
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
        
        success = self.queue.send_to_refinery(task.model_dump(mode='json'))
        
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
    
    try:
        # Inicjalizacja serwisu
        service = CollectorService()
        
        # Uruchom watchdog
        watcher = InboxWatcher(
            inbox_path=config.inbox_path,
            callback=service.process_file
        )
        watcher.start()
        
        logger.info("collector_service_ready", inbox_path=str(config.inbox_path))
        logger.info("inbox_watcher_path_set", resolved_inbox_path=str(config.inbox_path))
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            logger.info("shutdown_signal_received")
            watcher.stop()
            sys.exit(0)
            
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.critical("collector_service_crashed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
