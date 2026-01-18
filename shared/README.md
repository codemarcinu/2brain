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
```

### Konfiguracja

```python
from shared.config import get_settings

settings = get_settings()
print(settings.redis_host)
print(settings.postgres_url)
```

### Logowanie

```python
from shared.logging import setup_logging, get_logger

setup_logging(service_name="my_service")
logger = get_logger()

logger.info("service_started", port=8000)
```
