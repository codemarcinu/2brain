"""
Watchdog observer dla folderu Inbox
"""
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from typing import Callable, Optional
import time
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
        
        self._process_file_safe(file_path)

    def _process_file_safe(self, file_path: Path):
        """Bezpieczne przetwarzanie pliku z logowaniem błędów"""
        try:
            # Ignoruj pliki tymczasowe i ukryte
            if file_path.name.startswith('.') or file_path.suffix == '.tmp':
                return
            
            # Akceptuj tylko .txt i .url
            if file_path.suffix not in ['.txt', '.url']:
                logger.debug("file_ignored", file=file_path.name)
                return
            
            # Poczekaj chwilę na zakończenie zapisu pliku (częsty problem w watchdog)
            time.sleep(0.5)
            
            logger.info("new_file_detected", file=file_path.name)
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
        # Ensure directory exists
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
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
