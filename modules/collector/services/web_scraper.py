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
            # Używamy requests bo pozwala na lepszą kontrolę timeout i headers
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
            
            # Extract content settings
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not content:
                logger.warning("web_scraping_no_content", url=url)
                # Fallback: sometimes None is returned if extraction fails strictly
                # We could try withFallback=True but let's stick to clean content for now
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
