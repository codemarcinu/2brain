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
                # yt-dlp może dodać extension w zależności od kodeka, ale wymuszamy format
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
