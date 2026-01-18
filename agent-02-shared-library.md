# Agent 2: Shared Library

## 🎭 Rola
**Backend Library Developer**

## 🎯 Cel
Stworzenie wspólnej biblioteki Python używanej przez wszystkie mikroserwisy

## 📖 Kontekst

Mikroserwisy (Collector, Refinery, Finance) potrzebują współdzielonego kodu:
- **Komunikacja** - jednolity sposób wysyłania zadań przez Redis
- **Typy danych** - wspólne modele Pydantic dla wszystkich serwisów
- **Konfiguracja** - centralne zarządzanie zmiennymi środowiskowymi
- **Logowanie** - strukturalne logi w formacie JSON

Tworzymy pakiet Python instalowany przez `pip install -e ./shared`, który będzie importowany w każdym mikroserwisie.

## ✅ Zadania

### 1. Stwórz Strukturę Pakietu

```
shared/
├── setup.py                 # Definicja pakietu
├── requirements.txt         # Zależności
├── README.md               # Dokumentacja biblioteki
├── tests/                  # Testy jednostkowe
│   ├── __init__.py
│   ├── test_messaging.py
│   ├── test_types.py
│   └── test_config.py
└── shared/                 # Główny pakiet
    ├── __init__.py
    ├── messaging.py        # Redis client
    ├── types.py           # Pydantic models
    ├── config.py          # Environment config
    ├── logging.py         # Structured logging
    └── utils.py           # Helper functions
```

### 2. Plik `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name="obsidian-brain-shared",
    version="2.0.0",
    description="Shared library for Obsidian Brain microservices",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "structlog>=24.0.0",
    ],
    python_requires=">=3.10",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
)
```

### 3. Plik `requirements.txt`

```txt
redis>=5.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
structlog>=24.0.0
```

### 4. Moduł `shared/__init__.py`

```python
"""
Obsidian Brain Shared Library
Wspólny kod dla wszystkich mikroserwisów
"""

__version__ = "2.0.0"

from .messaging import RedisClient, TaskQueue
from .types import (
    ArticleTask,
    YoutubeTask,
    ReceiptTask,
    ProcessedNote,
    TaskStatus,
)
from .config import Settings, get_settings
from .logging import setup_logging, get_logger

__all__ = [
    "RedisClient",
    "TaskQueue",
    "ArticleTask",
    "YoutubeTask",
    "ReceiptTask",
    "ProcessedNote",
    "TaskStatus",
    "Settings",
    "get_settings",
    "setup_logging",
    "get_logger",
]
```

### 5. Moduł `shared/messaging.py` (Klient Redis)

```python
"""
Redis messaging dla komunikacji między serwisami
"""
import json
import redis
from typing import Callable, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class RedisClient:
    """
    Wrapper na Redis do zarządzania kolejkami zadań
    """
    
    def __init__(
        self,
        host: str = "redis",
        port: int = 6379,
        db: int = 0,
        decode_responses: bool = True
    ):
        """
        Args:
            host: Redis host
            port: Redis port
            db: Database number
            decode_responses: Czy dekodować odpowiedzi jako string
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        logger.info("redis_connected", host=host, port=port, db=db)
    
    def ping(self) -> bool:
        """Sprawdź czy Redis odpowiada"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            logger.error("redis_connection_failed")
            return False
    
    def publish_task(
        self,
        queue_name: str,
        payload: dict,
        priority: int = 0
    ) -> bool:
        """
        Wyślij zadanie do kolejki
        
        Args:
            queue_name: Nazwa kolejki (np. 'queue:refinery')
            payload: Dane zadania (dict)
            priority: Priorytet (wyższy = ważniejsze)
        
        Returns:
            True jeśli sukces
        """
        try:
            # Dodaj metadata
            task = {
                **payload,
                "metadata": {
                    "enqueued_at": datetime.utcnow().isoformat(),
                    "priority": priority,
                }
            }
            
            # LPUSH dodaje na początek listy (FIFO z RPOP)
            self.client.lpush(queue_name, json.dumps(task))
            
            logger.info(
                "task_published",
                queue=queue_name,
                task_id=payload.get("id"),
                priority=priority
            )
            return True
            
        except Exception as e:
            logger.error(
                "task_publish_failed",
                queue=queue_name,
                error=str(e)
            )
            return False
    
    def listen_to_queue(
        self,
        queue_name: str,
        callback: Callable[[dict], None],
        timeout: int = 0
    ) -> None:
        """
        Nasłuchuj na kolejce i wywołuj callback dla każdego zadania
        
        Args:
            queue_name: Nazwa kolejki
            callback: Funkcja przetwarzająca zadanie callback(task_data)
            timeout: Timeout w sekundach (0 = blokujące czekanie)
        
        Przykład:
            def process_task(task):
                print(f"Processing: {task}")
            
            client.listen_to_queue("queue:refinery", process_task)
        """
        logger.info("queue_listener_started", queue=queue_name)
        
        while True:
            try:
                # BRPOP - blokujące pobranie z końca listy
                result = self.client.brpop(queue_name, timeout=timeout or 0)
                
                if result:
                    _, task_json = result
                    task = json.loads(task_json)
                    
                    logger.info(
                        "task_received",
                        queue=queue_name,
                        task_id=task.get("id")
                    )
                    
                    # Wywołaj callback
                    callback(task)
                    
            except json.JSONDecodeError as e:
                logger.error("task_json_decode_error", error=str(e))
            except KeyboardInterrupt:
                logger.info("queue_listener_stopped", queue=queue_name)
                break
            except Exception as e:
                logger.error(
                    "queue_listener_error",
                    queue=queue_name,
                    error=str(e)
                )
    
    def get_queue_length(self, queue_name: str) -> int:
        """Ile zadań w kolejce"""
        return self.client.llen(queue_name)
    
    def clear_queue(self, queue_name: str) -> bool:
        """Wyczyść wszystkie zadania z kolejki"""
        try:
            self.client.delete(queue_name)
            logger.warning("queue_cleared", queue=queue_name)
            return True
        except Exception as e:
            logger.error("queue_clear_failed", queue=queue_name, error=str(e))
            return False


class TaskQueue:
    """
    Wysokopoziomowy wrapper - uproszczone API dla standardowych operacji
    """
    
    # Standardowe nazwy kolejek
    COLLECTOR_QUEUE = "queue:collector"
    REFINERY_QUEUE = "queue:refinery"
    FINANCE_QUEUE = "queue:finance"
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
    
    def send_to_refinery(self, task: dict) -> bool:
        """Wyślij zadanie do przetworzenia przez AI"""
        return self.redis.publish_task(self.REFINERY_QUEUE, task)
    
    def send_to_finance(self, task: dict) -> bool:
        """Wyślij paragon do weryfikacji"""
        return self.redis.publish_task(self.FINANCE_QUEUE, task)
    
    def get_stats(self) -> dict:
        """Statystyki wszystkich kolejek"""
        return {
            "collector": self.redis.get_queue_length(self.COLLECTOR_QUEUE),
            "refinery": self.redis.get_queue_length(self.REFINERY_QUEUE),
            "finance": self.redis.get_queue_length(self.FINANCE_QUEUE),
        }
```

### 6. Moduł `shared/types.py` (Modele Pydantic)

```python
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
```

### 7. Moduł `shared/config.py` (Konfiguracja)

```python
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
```

### 8. Moduł `shared/logging.py` (Strukturalne logowanie)

```python
"""
Strukturalne logowanie dla wszystkich serwisów
"""
import structlog
import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format: str = "json",
    service_name: Optional[str] = None
) -> None:
    """
    Konfiguracja structlog dla całego serwisu
    
    Args:
        level: DEBUG, INFO, WARNING, ERROR
        format: 'json' lub 'console'
        service_name: Nazwa serwisu (np. 'collector')
    """
    
    # Procesory wspólne dla wszystkich formatów
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if service_name:
        shared_processors.append(
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            )
        )
    
    # Wybór formatu
    if format == "json":
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:  # console
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    # Konfiguracja structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Konfiguracja standardowego loggera
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Dodaj service_name do kontekstu
    if service_name:
        structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Pobierz logger dla modułu
    
    Args:
        name: Nazwa loggera (domyślnie __name__ wywołującego)
    """
    return structlog.get_logger(name)
```

### 9. Moduł `shared/utils.py` (Pomocnicze funkcje)

```python
"""
Narzędzia pomocnicze używane w wielu miejscach
"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_task_id(prefix: str = "task") -> str:
    """
    Generuj unikalny ID zadania
    
    Args:
        prefix: Prefiks (np. 'yt', 'art', 'rec')
    
    Returns:
        ID w formacie: prefix_YYYYMMDD_HHMMSS_hash
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_hash = hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_hash}"


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """
    Przekształć tekst na bezpieczną nazwę pliku
    
    Args:
        text: Oryginalny tekst
        max_length: Maksymalna długość nazwy
    
    Returns:
        Bezpieczna nazwa pliku
    """
    # Usuń niebezpieczne znaki
    safe = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
    # Zamień spacje na podkreślenia
    safe = safe.replace(' ', '_')
    # Ogranicz długość
    return safe[:max_length].strip('_')


def ensure_path_exists(path: Path) -> Path:
    """
    Upewnij się że katalog istnieje (utwórz jeśli nie)
    
    Args:
        path: Ścieżka do katalogu
    
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def calculate_file_hash(file_path: Path) -> str:
    """
    Oblicz MD5 hash pliku (do deduplikacji)
    
    Args:
        file_path: Ścieżka do pliku
    
    Returns:
        MD5 hash jako hex string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
```

### 10. Testy `tests/test_messaging.py`

```python
"""
Testy dla modułu messaging
"""
import pytest
from shared.messaging import RedisClient, TaskQueue
from shared.types import ArticleTask


@pytest.fixture
def redis_client():
    """Fixture z klientem Redis (wymaga działającego Redis)"""
    client = RedisClient(host="localhost")
    yield client
    # Cleanup
    client.clear_queue("test_queue")


def test_redis_connection(redis_client):
    """Test połączenia z Redis"""
    assert redis_client.ping() is True


def test_publish_task(redis_client):
    """Test publikacji zadania"""
    task = {"id": "test_001", "type": "test", "data": "hello"}
    result = redis_client.publish_task("test_queue", task)
    assert result is True
    assert redis_client.get_queue_length("test_queue") == 1


def test_listen_to_queue(redis_client):
    """Test nasłuchiwania na kolejce"""
    received_tasks = []
    
    def callback(task):
        received_tasks.append(task)
    
    # Wyślij zadanie
    task = {"id": "test_002", "data": "test"}
    redis_client.publish_task("test_queue", task)
    
    # Nasłuchuj (timeout aby nie czekać w nieskończoność)
    result = redis_client.client.brpop("test_queue", timeout=1)
    assert result is not None


def test_task_queue_wrapper():
    """Test wysokopoziomowego API"""
    queue = TaskQueue()
    
    task = ArticleTask(
        id="art_001",
        url="https://example.com",
        content="Test content"
    )
    
    result = queue.send_to_refinery(task.model_dump())
    assert result is True
```

### 11. Plik `README.md` dla biblioteki

```markdown
# Obsidian Brain Shared Library

Wspólna biblioteka Python dla wszystkich mikroserwisów systemu Obsidian Brain v2.

## Instalacja

```bash
# W głównym katalogu projektu
cd shared
pip install -e .

# Lub z poziomu mikroserwisu
pip install -e ../shared
```

## Użycie

### Messaging (Redis)

```python
from shared.messaging import RedisClient, TaskQueue
from shared.types import YoutubeTask

# Niskopoziomowy client
client = RedisClient(host="redis", port=6379)
client.publish_task("queue:refinery", {"id": "001", "type": "youtube"})

# Wysokopoziomowy wrapper
queue = TaskQueue()
task = YoutubeTask(
    id="yt_001",
    url="https://youtube.com/watch?v=xyz",
    transcript="Full transcript..."
)
queue.send_to_refinery(task.model_dump())
```

### Typy Danych

```python
from shared.types import ArticleTask, ProcessedNote

# Walidacja danych
task = ArticleTask(
    id="art_001",
    url="https://example.com/article",
    content="Article text...",
    title="Example Article"
)

# Export do JSON
json_data = task.model_dump_json()
```

### Konfiguracja

```python
from shared.config import get_settings

settings = get_settings()
print(settings.redis_host)  # redis
print(settings.postgres_url)  # postgresql://brain:pass@postgres/db
```

### Logowanie

```python
from shared.logging import setup_logging, get_logger

# W main.py serwisu
setup_logging(level="INFO", format="json", service_name="collector")

# W modułach
logger = get_logger(__name__)
logger.info("task_started", task_id="001", status="processing")
logger.error("task_failed", task_id="001", error="Connection timeout")
```

## Testy

```bash
# Zainstaluj zależności dev
pip install -e ".[dev]"

# Uruchom testy (wymaga działającego Redis)
pytest tests/ -v

# Coverage
pytest tests/ --cov=shared --cov-report=html
```

## Dodawanie Nowych Typów

1. Dodaj model Pydantic w `types.py`
2. Zaktualizuj `__init__.py` (dodaj do `__all__`)
3. Dodaj testy w `tests/test_types.py`
4. Zaktualizuj dokumentację

## Changelog

### v2.0.0 (2025-01-18)
- Inicjalna wersja dla architektury mikroserwisowej
- Redis messaging
- Pydantic models
- Structured logging
```

## 🎯 Kryteria Sukcesu

### Walidacja po wykonaniu:

```bash
# 1. Instalacja pakietu działa
cd shared
pip install -e .
# Expected: Successfully installed obsidian-brain-shared

# 2. Import działa
python -c "from shared.messaging import RedisClient; print('OK')"
# Expected: OK

# 3. Połączenie z Redis działa
python -c "from shared.messaging import RedisClient; c = RedisClient(); print(c.ping())"
# Expected: True

# 4. Testy przechodzą
pytest tests/ -v
# Expected: All tests passed

# 5. Typy działają
python -c "from shared.types import ArticleTask; t = ArticleTask(id='test', url='https://example.com', content='test'); print(t.model_dump_json())"
# Expected: Valid JSON output
```

### Checklist końcowy:

- [x] Struktura katalogów zgodna z zadaniem
- [x] `pip install -e ./shared` działa bez błędów
- [x] Wszystkie moduły importują się poprawnie
- [x] RedisClient łączy się z Redis z Agenta 1
- [x] Testy jednostkowe przechodzą
- [x] Dokumentacja README.md kompletna
- [x] Pydantic models walidują dane poprawnie

## 📦 Pliki Wyjściowe

```
shared/
├── setup.py                ✅
├── requirements.txt        ✅
├── README.md              ✅
├── tests/
│   ├── __init__.py        ✅
│   ├── test_messaging.py  ✅
│   ├── test_types.py      ✅
│   └── test_config.py     ✅
└── shared/
    ├── __init__.py        ✅
    ├── messaging.py       ✅
    ├── types.py          ✅
    ├── config.py         ✅
    ├── logging.py        ✅
    └── utils.py          ✅
```

## 🔗 Zależności

**Wymaga:**
- ✅ Agent 1 (Infrastructure) - działający Redis

**Wymagane przez:**
- ✅ Agent 3 (Collector) - używa messaging, types
- ✅ Agent 4 (Refinery) - używa messaging, types, logging
- ✅ Agent 5 (Finance) - używa types, config, logging

## 💡 Wskazówki dla Google Antigravity

### Testowanie podczas rozwoju:

```bash
# Terminal 1 - Redis (z Agenta 1)
docker compose up redis

# Terminal 2 - Python REPL do testów
cd shared
python
>>> from shared.messaging import RedisClient
>>> c = RedisClient()
>>> c.publish_task("test", {"hello": "world"})
```

### Możliwe problemy:

**Redis niedostępny:**
- Sprawdź czy Agent 1 uruchomił kontenery
- Zmień host na `localhost` jeśli testujesz poza Dockerem

**Import errors:**
- Upewnij się że `pip install -e .` zostało uruchomione
- Sprawdź czy jesteś w virtualenv

**Pydantic validation errors:**
- Sprawdź przykłady w `json_schema_extra`
- Użyj `model_validate()` zamiast `__init__` dla debugowania

---

**Status:** 🟢 Gotowy do uruchomienia
**Czas wykonania:** ~30 minut
**Następny agent:** Agent 3, 4, lub 5 (można równolegle)
