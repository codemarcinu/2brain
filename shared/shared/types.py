"""
Wspólne typy danych dla wszystkich serwisów
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Status przetwarzania zadania"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseTask(BaseModel):
    """Bazowa klasa dla wszystkich zadań"""
    id: str = Field(..., description="Unikalny identyfikator zadania")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: TaskStatus = TaskStatus.PENDING
    
    class Config:
        use_enum_values = True


class ArticleTask(BaseTask):
    """Zadanie przetworzenia artykułu web"""
    type: Literal["article"] = "article"
    url: HttpUrl
    title: Optional[str] = None
    content: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "art_20250118_001",
                "type": "article",
                "url": "https://example.com/article",
                "title": "AI Trends 2025",
                "content": "Full article text...",
                "author": "John Doe",
            }
        }


class YoutubeTask(BaseTask):
    """Zadanie przetworzenia video YouTube"""
    type: Literal["youtube"] = "youtube"
    url: HttpUrl
    title: Optional[str] = None
    channel: Optional[str] = None
    transcript: str
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "yt_20250118_001",
                "type": "youtube",
                "url": "https://youtube.com/watch?v=xyz",
                "title": "ML Tutorial",
                "channel": "Tech Channel",
                "transcript": "Full transcript...",
                "duration_seconds": 1800,
            }
        }


class ReceiptTask(BaseTask):
    """Zadanie przetworzenia paragonu"""
    type: Literal["receipt"] = "receipt"
    image_path: str
    shop_name: Optional[str] = None
    purchase_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    items: List[Dict[str, Any]] = Field(default_factory=list)
    ocr_raw_text: Optional[str] = None
    verified: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rec_20250118_001",
                "type": "receipt",
                "image_path": "/inbox/receipt_001.jpg",
                "shop_name": "Biedronka",
                "purchase_date": "2025-01-18T10:30:00",
                "total_amount": 45.67,
                "items": [
                    {"name": "Mleko", "price": 3.99, "quantity": 2},
                    {"name": "Chleb", "price": 2.50, "quantity": 1},
                ],
            }
        }


class ProcessedNote(BaseModel):
    """Wygenerowana notatka Markdown"""
    id: str
    title: str
    content: str  # Pełny Markdown
    tags: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)  # Linki do innych notatek
    source_url: Optional[str] = None
    source_type: Literal["youtube", "article", "manual"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    vault_path: str  # Gdzie zapisać w Obsidian
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "note_20250118_001",
                "title": "AI Trends 2025",
                "content": "# AI Trends 2025\n\n## Summary\n...",
                "tags": ["AI", "trends", "2025"],
                "links": ["Machine Learning", "Neural Networks"],
                "source_url": "https://example.com/article",
                "source_type": "article",
                "vault_path": "Articles/2025-01/AI_Trends.md",
            }
        }


class ErrorResponse(BaseModel):
    """Standardowa odpowiedź błędu"""
    error: str
    details: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
