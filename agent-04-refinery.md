# Agent 4: Refinery Service

## 🎭 Rola
**AI/ML Engineer**

## 🎯 Cel
Mikroserwis przetwarzający surowe treści na gotowe notatki Markdown

## 📖 Kontekst

Refinery to "mózg" systemu. Odbiera surowy tekst z kolejki Redis, używa LLM do:
- Generowania podsumowań
- Wyciągania kluczowych punktów
- Sugerowania tagów i linków
- Tworzenia pięknych notatek Markdown

### Przepływ danych:
```
Redis Queue → Refinery → LLM Processing → Obsidian Vault (.md files)
```

**Kluczowa zasada:** Refinery zapisuje gotowe pliki BEZPOŚREDNIO do Obsidian Vault. Obsidian tylko CZYTA, nie steruje.

## ✅ Zadania

### 1. Struktura Projektu

```
modules/refinery/
├── Dockerfile
├── requirements.txt
├── main.py                      # Entry point
├── config.py                    # Konfiguracja
├── services/
│   ├── __init__.py
│   ├── llm_processor.py         # LLM wrapper (Ollama/OpenAI/Gemini)
│   ├── markdown_generator.py   # Jinja2 templates
│   └── vault_writer.py          # Zapis do Obsidian
├── templates/
│   ├── youtube_note.md.jinja2
│   ├── article_note.md.jinja2
│   └── base_note.md.jinja2
├── prompts/
│   ├── youtube_summary.txt
│   └── article_summary.txt
└── tests/
    ├── __init__.py
    └── test_llm_processor.py
```

### 2. Dockerfile

```dockerfile
FROM python:3.10-slim

LABEL maintainer="your@email.com"
LABEL description="Refinery AI service for Obsidian Brain"

WORKDIR /app

# Zainstaluj zależności systemowe (jeśli potrzebne)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod
COPY . .

# Shared library
RUN pip install -e /shared

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check (sprawdź czy Redis dostępny)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

CMD ["python", "main.py"]
```

### 3. requirements.txt

```txt
# LLM Frameworks
langchain>=0.1.0
langchain-community>=0.0.20
langchain-ollama>=0.0.1

# LLM Providers
ollama>=0.1.0
openai>=1.10.0
google-generativeai>=0.3.0

# Templates
jinja2>=3.1.0

# Markdown processing
markdown>=3.5.0
python-frontmatter>=1.1.0

# Utilities
pyyaml>=6.0
```

### 4. config.py

```python
"""
Konfiguracja dla Refinery service
"""
from pathlib import Path
from shared.config import get_settings as get_base_settings


class RefineryConfig:
    """Rozszerzona konfiguracja dla Refinery"""
    
    def __init__(self):
        self.base = get_base_settings()
        
        # Paths
        self.vault_path = Path(self.base.obsidian_vault_path)
        self.templates_path = Path(__file__).parent / "templates"
        self.prompts_path = Path(__file__).parent / "prompts"
        
        # Output folders w Vault
        self.youtube_folder = self.vault_path / "YouTube"
        self.articles_folder = self.vault_path / "Articles"
        self.web_clips_folder = self.vault_path / "Web Clips"
        
        # LLM Settings
        self.llm_provider = "ollama"  # ollama, openai, gemini
        self.llm_model = self.base.ollama_model
        self.llm_temperature = 0.3  # Niższa = bardziej deterministyczne
        self.llm_max_tokens = 2000
        
        # Processing settings
        self.max_content_length = 50000  # Limit dla długich treści
        self.summary_target_words = 300  # Docelowa długość podsumowania
        
        # Redis queues
        self.input_queue = "queue:refinery"
        
        # Ensure folders exist
        for folder in [self.youtube_folder, self.articles_folder, self.web_clips_folder]:
            folder.mkdir(parents=True, exist_ok=True)


config = RefineryConfig()
```

### 5. prompts/youtube_summary.txt

```text
You are a knowledge management assistant. Your task is to create a comprehensive summary of a YouTube video transcript.

## Input
Video Title: {title}
Channel: {channel}
Duration: {duration} seconds
Transcript: {transcript}

## Your Task
Analyze the transcript and provide:

1. **Summary** (2-3 paragraphs): Main message and key takeaways
2. **Key Points** (5-10 bullet points): Most important insights
3. **Tags** (5-8 tags): Relevant topics for categorization
4. **Related Topics** (3-5 topics): Concepts that could be linked to other notes

## Output Format
Return ONLY a valid JSON object (no markdown, no code blocks):
{{
  "summary": "...",
  "key_points": ["...", "..."],
  "tags": ["...", "..."],
  "related_topics": ["...", "..."],
  "main_category": "..."
}}

Be concise, factual, and focus on actionable insights.
```

### 6. prompts/article_summary.txt

```text
You are a knowledge management assistant. Your task is to analyze a web article and extract structured information.

## Input
Title: {title}
Author: {author}
URL: {url}
Content: {content}

## Your Task
Analyze the article and provide:

1. **Summary** (2-3 paragraphs): Main arguments and conclusions
2. **Key Points** (5-10 bullet points): Most important takeaways
3. **Tags** (5-8 tags): Relevant topics
4. **Quotes** (0-3 quotes): Most impactful sentences (if any)
5. **Related Topics** (3-5 topics): Concepts to explore further

## Output Format
Return ONLY a valid JSON object:
{{
  "summary": "...",
  "key_points": ["...", "..."],
  "tags": ["...", "..."],
  "quotes": ["...", "..."],
  "related_topics": ["...", "..."],
  "article_type": "tutorial|analysis|news|opinion|research"
}}

Focus on extracting value, not just restating the article.
```

### 7. services/llm_processor.py

```python
"""
LLM wrapper supporting multiple providers
"""
import json
from typing import Dict, Optional, Literal
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from shared.logging import get_logger
from config import config

logger = get_logger(__name__)

LLMProvider = Literal["ollama", "openai", "gemini"]


class LLMProcessor:
    """Wrapper dla różnych providerów LLM"""
    
    def __init__(
        self,
        provider: LLMProvider = "ollama",
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        self.provider = provider
        self.model = model or config.llm_model
        self.temperature = temperature
        
        # Inicjalizacja providera
        if provider == "ollama":
            self.llm = ChatOllama(
                base_url=config.base.ollama_host,
                model=self.model,
                temperature=temperature,
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                api_key=config.base.openai_api_key,
                model=self.model,
                temperature=temperature,
            )
        elif provider == "gemini":
            # Implementacja dla Gemini
            raise NotImplementedError("Gemini provider not yet implemented")
        
        logger.info(
            "llm_initialized",
            provider=provider,
            model=self.model,
            temperature=temperature
        )
    
    def _load_prompt(self, prompt_name: str) -> str:
        """Załaduj prompt template z pliku"""
        prompt_file = config.prompts_path / f"{prompt_name}.txt"
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """
        Bezpieczne parsowanie odpowiedzi JSON (LLM czasem dodają ``` itd.)
        """
        try:
            # Usuń ewentualne markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith('```'):
                # Find first { and last }
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                if start != -1 and end != 0:
                    cleaned = cleaned[start:end]
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("json_parse_failed", error=str(e), response=response[:200])
            return None
    
    def process_youtube(self, task_data: Dict) -> Optional[Dict]:
        """
        Przetwórz transkrypcję YouTube
        
        Args:
            task_data: Dict z YoutubeTask (title, channel, transcript)
        
        Returns:
            Dict z summary, key_points, tags, etc.
        """
        logger.info("llm_youtube_processing", task_id=task_data.get('id'))
        
        try:
            # Załaduj prompt
            prompt_template = self._load_prompt("youtube_summary")
            
            # Przygotuj dane
            prompt = prompt_template.format(
                title=task_data.get('title', 'Untitled'),
                channel=task_data.get('channel', 'Unknown'),
                duration=task_data.get('duration_seconds', 0),
                transcript=task_data.get('transcript', '')[:config.max_content_length]
            )
            
            # Wywołaj LLM
            response = self.llm.invoke(prompt)
            
            # Parse JSON
            result = self._parse_json_response(response.content)
            
            if result:
                logger.info(
                    "llm_youtube_success",
                    task_id=task_data.get('id'),
                    tags_count=len(result.get('tags', []))
                )
                return result
            else:
                logger.error("llm_youtube_invalid_json", task_id=task_data.get('id'))
                return None
                
        except Exception as e:
            logger.error(
                "llm_youtube_failed",
                task_id=task_data.get('id'),
                error=str(e)
            )
            return None
    
    def process_article(self, task_data: Dict) -> Optional[Dict]:
        """
        Przetwórz artykuł WWW
        
        Args:
            task_data: Dict z ArticleTask (title, content, author)
        
        Returns:
            Dict z summary, key_points, tags, etc.
        """
        logger.info("llm_article_processing", task_id=task_data.get('id'))
        
        try:
            prompt_template = self._load_prompt("article_summary")
            
            prompt = prompt_template.format(
                title=task_data.get('title', 'Untitled'),
                author=task_data.get('author', 'Unknown'),
                url=task_data.get('url', ''),
                content=task_data.get('content', '')[:config.max_content_length]
            )
            
            response = self.llm.invoke(prompt)
            result = self._parse_json_response(response.content)
            
            if result:
                logger.info(
                    "llm_article_success",
                    task_id=task_data.get('id'),
                    article_type=result.get('article_type')
                )
                return result
            else:
                logger.error("llm_article_invalid_json", task_id=task_data.get('id'))
                return None
                
        except Exception as e:
            logger.error(
                "llm_article_failed",
                task_id=task_data.get('id'),
                error=str(e)
            )
            return None
```

### 8. services/markdown_generator.py

```python
"""
Generator notatek Markdown z Jinja2 templates
"""
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from typing import Dict
from shared.logging import get_logger
from config import config

logger = get_logger(__name__)


class MarkdownGenerator:
    """Generator Markdown notes z templates"""
    
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(config.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Custom filters dla Jinja2
        self.env.filters['datetime'] = self._format_datetime
    
    def _format_datetime(self, dt: datetime, format: str = '%Y-%m-%d %H:%M') -> str:
        """Jinja2 filter do formatowania dat"""
        return dt.strftime(format)
    
    def generate_youtube_note(
        self,
        task_data: Dict,
        llm_result: Dict
    ) -> str:
        """
        Wygeneruj notatkę dla YouTube video
        
        Args:
            task_data: Oryginalne dane z YoutubeTask
            llm_result: Wynik przetwarzania LLM
        
        Returns:
            Pełny Markdown z frontmatter
        """
        template = self.env.get_template('youtube_note.md.jinja2')
        
        context = {
            'title': task_data.get('title', 'Untitled'),
            'url': task_data.get('url'),
            'channel': task_data.get('channel'),
            'duration_minutes': (task_data.get('duration_seconds', 0) // 60),
            'created_at': datetime.utcnow(),
            'tags': llm_result.get('tags', []),
            'category': llm_result.get('main_category', 'General'),
            'summary': llm_result.get('summary', ''),
            'key_points': llm_result.get('key_points', []),
            'related_topics': llm_result.get('related_topics', []),
            'transcript': task_data.get('transcript', ''),
        }
        
        return template.render(**context)
    
    def generate_article_note(
        self,
        task_data: Dict,
        llm_result: Dict
    ) -> str:
        """
        Wygeneruj notatkę dla artykułu web
        """
        template = self.env.get_template('article_note.md.jinja2')
        
        context = {
            'title': task_data.get('title', 'Untitled'),
            'url': task_data.get('url'),
            'author': task_data.get('author'),
            'created_at': datetime.utcnow(),
            'tags': llm_result.get('tags', []),
            'article_type': llm_result.get('article_type', 'article'),
            'summary': llm_result.get('summary', ''),
            'key_points': llm_result.get('key_points', []),
            'quotes': llm_result.get('quotes', []),
            'related_topics': llm_result.get('related_topics', []),
            'content': task_data.get('content', ''),
        }
        
        return template.render(**context)
```

### 9. templates/youtube_note.md.jinja2

```jinja2
---
title: "{{ title }}"
created: {{ created_at.strftime('%Y-%m-%d %H:%M') }}
source: {{ url }}
type: youtube
channel: "{{ channel }}"
duration: {{ duration_minutes }}min
tags:
{%- for tag in tags %}
  - {{ tag }}
{%- endfor %}
category: {{ category }}
---

# {{ title }}

**Channel:** [[{{ channel }}]]
**Duration:** {{ duration_minutes }} minutes
**Link:** [Watch on YouTube]({{ url }})

## 📝 Summary

{{ summary }}

## 🔑 Key Points

{% for point in key_points -%}
- {{ point }}
{% endfor %}

## 🔗 Related Topics

{% for topic in related_topics -%}
- [[{{ topic }}]]
{% endfor %}

---

## 📜 Full Transcript

{{ transcript }}
```

### 10. templates/article_note.md.jinja2

```jinja2
---
title: "{{ title }}"
created: {{ created_at.strftime('%Y-%m-%d %H:%M') }}
source: {{ url }}
type: {{ article_type }}
{% if author -%}
author: "{{ author }}"
{% endif -%}
tags:
{%- for tag in tags %}
  - {{ tag }}
{%- endfor %}
---

# {{ title }}

{% if author -%}
**Author:** {{ author }}
{% endif -%}
**Source:** [Read Original]({{ url }})
**Type:** {{ article_type|capitalize }}

## 📝 Summary

{{ summary }}

## 🔑 Key Takeaways

{% for point in key_points -%}
- {{ point }}
{% endfor %}

{% if quotes -%}
## 💬 Notable Quotes

{% for quote in quotes -%}
> {{ quote }}

{% endfor %}
{% endif -%}

## 🔗 Related Topics

{% for topic in related_topics -%}
- [[{{ topic }}]]
{% endfor %}

---

## 📄 Full Content

{{ content }}
```

### 11. services/vault_writer.py

```python
"""
Zapis notatek do Obsidian Vault
"""
from pathlib import Path
from datetime import datetime
from shared.logging import get_logger
from shared.utils import sanitize_filename
from config import config

logger = get_logger(__name__)


class VaultWriter:
    """Writer dla Obsidian Vault"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
    
    def _generate_filename(self, title: str, prefix: str = "") -> str:
        """
        Generuj bezpieczną nazwę pliku
        
        Args:
            title: Tytuł notatki
            prefix: Opcjonalny prefiks (np. data)
        
        Returns:
            Nazwa pliku z .md
        """
        safe_title = sanitize_filename(title, max_length=80)
        
        if prefix:
            return f"{prefix}_{safe_title}.md"
        else:
            return f"{safe_title}.md"
    
    def _ensure_unique_filename(self, folder: Path, filename: str) -> Path:
        """
        Upewnij się że nazwa pliku jest unikalna (dodaj timestamp jeśli konflikt)
        """
        filepath = folder / filename
        
        if not filepath.exists():
            return filepath
        
        # Konflikt - dodaj timestamp
        stem = filepath.stem
        suffix = filepath.suffix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{stem}_{timestamp}{suffix}"
        
        logger.warning(
            "filename_conflict_resolved",
            original=filename,
            new=new_filename
        )
        
        return folder / new_filename
    
    def save_youtube_note(self, content: str, title: str) -> Optional[Path]:
        """
        Zapisz notatkę YouTube do Vault
        
        Args:
            content: Pełny Markdown z frontmatter
            title: Tytuł video
        
        Returns:
            Ścieżka do zapisanego pliku lub None jeśli błąd
        """
        try:
            # Generuj nazwę pliku
            date_prefix = datetime.now().strftime('%Y-%m-%d')
            filename = self._generate_filename(title, prefix=date_prefix)
            
            # Upewnij się że folder istnieje
            config.youtube_folder.mkdir(parents=True, exist_ok=True)
            
            # Unique path
            filepath = self._ensure_unique_filename(
                config.youtube_folder,
                filename
            )
            
            # Zapisz
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(
                "note_saved",
                type="youtube",
                path=str(filepath.relative_to(self.vault_path))
            )
            
            return filepath
            
        except Exception as e:
            logger.error("note_save_failed", type="youtube", error=str(e))
            return None
    
    def save_article_note(self, content: str, title: str) -> Optional[Path]:
        """Zapisz notatkę artykułu"""
        try:
            date_prefix = datetime.now().strftime('%Y-%m-%d')
            filename = self._generate_filename(title, prefix=date_prefix)
            
            config.articles_folder.mkdir(parents=True, exist_ok=True)
            filepath = self._ensure_unique_filename(
                config.articles_folder,
                filename
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(
                "note_saved",
                type="article",
                path=str(filepath.relative_to(self.vault_path))
            )
            
            return filepath
            
        except Exception as e:
            logger.error("note_save_failed", type="article", error=str(e))
            return None
```

### 12. main.py (Entry Point)

```python
"""
Refinery Service - Main Entry Point
"""
from shared.messaging import RedisClient
from shared.logging import setup_logging, get_logger
from config import config
from services.llm_processor import LLMProcessor
from services.markdown_generator import MarkdownGenerator
from services.vault_writer import VaultWriter

setup_logging(
    level=config.base.log_level,
    format=config.base.log_format,
    service_name="refinery"
)
logger = get_logger(__name__)


class RefineryService:
    """Główny serwis Refinery"""
    
    def __init__(self):
        self.redis = RedisClient()
        self.llm = LLMProcessor(
            provider=config.llm_provider,
            model=config.llm_model,
            temperature=config.llm_temperature
        )
        self.markdown = MarkdownGenerator()
        self.vault = VaultWriter(config.vault_path)
        
        logger.info("refinery_service_initialized")
    
    def process_task(self, task: dict):
        """
        Przetwórz zadanie z kolejki
        
        Args:
            task: Dict z task data (YoutubeTask lub ArticleTask)
        """
        task_type = task.get('type')
        task_id = task.get('id')
        
        logger.info("task_processing_started", task_id=task_id, type=task_type)
        
        try:
            if task_type == 'youtube':
                self._process_youtube(task)
            elif task_type == 'article':
                self._process_article(task)
            else:
                logger.warning("unknown_task_type", task_id=task_id, type=task_type)
                return
            
            logger.info("task_completed", task_id=task_id)
            
        except Exception as e:
            logger.error(
                "task_processing_failed",
                task_id=task_id,
                error=str(e)
            )
    
    def _process_youtube(self, task: dict):
        """Przetwórz YouTube task"""
        # 1. LLM processing
        llm_result = self.llm.process_youtube(task)
        if not llm_result:
            raise Exception("LLM processing failed")
        
        # 2. Generate Markdown
        markdown_content = self.markdown.generate_youtube_note(task, llm_result)
        
        # 3. Save to Vault
        filepath = self.vault.save_youtube_note(
            markdown_content,
            task.get('title', 'Untitled')
        )
        
        if not filepath:
            raise Exception("Failed to save note")
    
    def _process_article(self, task: dict):
        """Przetwórz Article task"""
        llm_result = self.llm.process_article(task)
        if not llm_result:
            raise Exception("LLM processing failed")
        
        markdown_content = self.markdown.generate_article_note(task, llm_result)
        
        filepath = self.vault.save_article_note(
            markdown_content,
            task.get('title', 'Untitled')
        )
        
        if not filepath:
            raise Exception("Failed to save note")


def main():
    """Main loop - nasłuchuj na kolejce"""
    logger.info("refinery_service_starting")
    
    service = RefineryService()
    
    logger.info(
        "refinery_listening",
        queue=config.input_queue,
        llm_provider=config.llm_provider,
        llm_model=config.llm_model
    )
    
    try:
        # Listen to Redis queue
        service.redis.listen_to_queue(
            queue_name=config.input_queue,
            callback=service.process_task
        )
    except KeyboardInterrupt:
        logger.info("refinery_service_shutting_down")


if __name__ == "__main__":
    main()
```

### 13. Aktualizacja docker-compose.yml

```yaml
refinery:
  build:
    context: ./modules/refinery
    dockerfile: Dockerfile
  container_name: brain-refinery
  volumes:
    - ${OBSIDIAN_VAULT_PATH}:/vault
    - ./shared:/shared:ro
  environment:
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - REDIS_HOST=redis
    - OLLAMA_HOST=http://ollama:11434
    - OBSIDIAN_VAULT_PATH=/vault
  depends_on:
    redis:
      condition: service_healthy
    ollama:
      condition: service_healthy
  networks:
    - brain-network
  restart: unless-stopped
```

## 🎯 Kryteria Sukcesu

```bash
# 1. Build
docker compose build refinery

# 2. Start
docker compose up -d refinery
docker compose logs -f refinery

# 3. Test end-to-end
# (Collector wysłał zadanie do Redis w poprzednim teście)
# Refinery powinien je automatycznie przetworzyć

# 4. Sprawdź czy notatka została utworzona
ls ${OBSIDIAN_VAULT_PATH}/YouTube/
ls ${OBSIDIAN_VAULT_PATH}/Articles/

# 5. Sprawdź zawartość notatki
cat ${OBSIDIAN_VAULT_PATH}/YouTube/2025-01-18_*.md
# Expected: Poprawny Markdown z frontmatter, summary, key points
```

### Checklist:
- [x] LLM Processor działa z Ollama
- [x] Prompty generują poprawny JSON
- [x] Markdown templates renderują się poprawnie
- [x] Notatki zapisują się w Obsidian Vault
- [x] Błędy LLM nie crashują serwisu (retry/skip)

## 📦 Pliki Wyjściowe

Kompletny mikroserwis `modules/refinery/` ze wszystkimi modułami.

## 🔗 Zależności

**Wymaga:**
- ✅ Agent 1 (Infrastructure) - Redis, Ollama
- ✅ Agent 2 (Shared Library)
- ✅ Agent 3 (Collector) - producent zadań

**Wymagane przez:**
- ✅ Agent 6 (Chat) - używa notatek z Vault

---

**Status:** ✅ Wykonany
**Czas:** ~60 minut
**Następny:** Agent 5 lub 6 (równolegle)
