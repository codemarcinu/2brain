# Agent 6: Chat Integration

## 🎭 Rola
**MLOps / Integration Engineer**

## 🎯 Cel
Konfiguracja interfejsu czatu (Open Web UI) z dostępem do bazy wiedzy Obsidian przez RAG

## 📖 Kontekst

Open Web UI to gotowy interfejs czatu (wygląda jak ChatGPT). Zadanie:
1. Skonfigurować połączenie z Ollama
2. Podpiąć RAG aby "rozmawiał" z notatkami Obsidian
3. Dodać customowe pipelines dla specjalnych funkcji
4. Udostępnić użytkownikowi pod http://localhost:3000

### Architektura:
```
User → Open Web UI → RAG Pipeline → Qdrant (embeddings) → Ollama → Response
                              ↓
                         Obsidian Vault (source documents)
```

## ✅ Zadania

### 1. Struktura Projektu

```
modules/chat/
├── docker-compose.override.yml   # Konfiguracja Open Web UI
├── setup_rag.py                  # Skrypt indeksujący notatki
├── pipelines/                    # Custom pipelines dla Open Web UI
│   ├── __init__.py
│   └── obsidian_rag.py          # RAG pipeline
├── config/
│   ├── __init__.py
│   └── models.json              # Predefiniowane modele
└── scripts/
    ├── index_vault.py           # Cron job - reindeksacja
    └── backup_chat_history.py  # Backup conversations
```

### 2. Aktualizacja docker-compose.yml

**W głównym `docker-compose.yml` dodaj/zmień:**

```yaml
# Qdrant (Vector Database) - jeśli jeszcze nie ma
qdrant:
  image: qdrant/qdrant:latest
  container_name: brain-qdrant
  ports:
    - "6333:6333"
    - "6334:6334"
  volumes:
    - ./data/qdrant:/qdrant/storage
  environment:
    - QDRANT__SERVICE__HTTP_PORT=6333
    - QDRANT__SERVICE__GRPC_PORT=6334
  networks:
    - brain-network
  restart: unless-stopped

# Open Web UI
open-webui:
  image: ghcr.io/open-webui/open-webui:main
  container_name: brain-chat
  ports:
    - "3000:8080"
  volumes:
    - ./data/open-webui:/app/backend/data
    - ${OBSIDIAN_VAULT_PATH}:/vault:ro
    - ./modules/chat/pipelines:/app/pipelines:ro
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
    - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
    - ENABLE_RAG_WEB_SEARCH=false
    - ENABLE_OLLAMA_API=true
    - RAG_EMBEDDING_MODEL=nomic-embed-text:latest
    - RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE=true
    - CHUNK_SIZE=1000
    - CHUNK_OVERLAP=100
    - RAG_TOP_K=5
    - VECTOR_DB=qdrant
    - QDRANT_URL=http://qdrant:6333
  depends_on:
    ollama:
      condition: service_healthy
    qdrant:
      condition: service_started
  networks:
    - brain-network
  restart: unless-stopped
```

### 3. setup_rag.py (Inicjalne indeksowanie)

```python
"""
Setup RAG - Indeksowanie notatek Obsidian do Qdrant
"""
import os
from pathlib import Path
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.document_loaders import ObsidianLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
import hashlib
from tqdm import tqdm
from shared.logging import setup_logging, get_logger
from shared.config import get_settings

setup_logging(level="INFO", format="console", service_name="rag-setup")
logger = get_logger(__name__)

settings = get_settings()


class VaultIndexer:
    """Indeksowanie Obsidian Vault do Qdrant"""
    
    def __init__(
        self,
        vault_path: Path,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "obsidian_notes"
    ):
        self.vault_path = vault_path
        self.collection_name = collection_name
        
        # Qdrant client
        self.qdrant = QdrantClient(url=qdrant_url)
        
        # Embeddings (Ollama)
        self.embeddings = OllamaEmbeddings(
            base_url=settings.ollama_host,
            model="nomic-embed-text"
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
        
        logger.info(
            "indexer_initialized",
            vault=str(vault_path),
            collection=collection_name
        )
    
    def create_collection(self, vector_size: int = 768):
        """Utwórz kolekcję w Qdrant (jeśli nie istnieje)"""
        try:
            self.qdrant.get_collection(self.collection_name)
            logger.info("collection_exists", name=self.collection_name)
        except:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info("collection_created", name=self.collection_name)
    
    def load_documents(self) -> List[Dict]:
        """Załaduj wszystkie notatki Markdown z Vault"""
        logger.info("loading_documents", path=str(self.vault_path))
        
        documents = []
        
        for md_file in self.vault_path.rglob("*.md"):
            # Skip templates and hidden files
            if md_file.name.startswith('.') or 'templates' in md_file.parts:
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter (basic)
                metadata = {
                    'source': str(md_file.relative_to(self.vault_path)),
                    'title': md_file.stem,
                    'path': str(md_file)
                }
                
                # Extract tags from frontmatter if present
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        content = parts[2]
                        
                        # Simple tag extraction
                        if 'tags:' in frontmatter:
                            tags_section = frontmatter.split('tags:')[1].split('\n')[0]
                            metadata['tags'] = tags_section.strip()
                
                documents.append({
                    'content': content.strip(),
                    'metadata': metadata
                })
                
            except Exception as e:
                logger.warning("file_read_failed", file=str(md_file), error=str(e))
        
        logger.info("documents_loaded", count=len(documents))
        return documents
    
    def index_documents(self, documents: List[Dict]):
        """Podziel dokumenty na chunki i zaindeksuj"""
        logger.info("indexing_started", doc_count=len(documents))
        
        points = []
        point_id = 0
        
        for doc in tqdm(documents, desc="Indexing"):
            # Split into chunks
            chunks = self.text_splitter.split_text(doc['content'])
            
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.embeddings.embed_query(chunk)
                
                # Create point
                payload = {
                    **doc['metadata'],
                    'chunk': chunk,
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks)
                }
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                
                points.append(point)
                point_id += 1
                
                # Batch upsert (co 100 punktów)
                if len(points) >= 100:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    points = []
        
        # Upsert remaining
        if points:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )
        
        logger.info("indexing_completed", total_chunks=point_id)
    
    def run(self):
        """Pełny proces indeksowania"""
        # 1. Create collection
        self.create_collection()
        
        # 2. Load documents
        documents = self.load_documents()
        
        if not documents:
            logger.warning("no_documents_found")
            return
        
        # 3. Index
        self.index_documents(documents)
        
        logger.info("rag_setup_complete")


def main():
    """Main entry point"""
    vault_path = Path(os.getenv('OBSIDIAN_VAULT_PATH', '/vault'))
    
    if not vault_path.exists():
        logger.error("vault_not_found", path=str(vault_path))
        return
    
    indexer = VaultIndexer(vault_path=vault_path)
    indexer.run()


if __name__ == "__main__":
    main()
```

### 4. pipelines/obsidian_rag.py (Custom Pipeline)

```python
"""
Custom RAG Pipeline dla Open Web UI
Wyszukiwanie semantyczne w notatkach Obsidian
"""
from typing import List, Dict, Optional, Generator
from pydantic import BaseModel
from qdrant_client import QdrantClient
from langchain_community.embeddings import OllamaEmbeddings


class Pipeline:
    """
    Open Web UI Pipeline dla RAG w Obsidian
    
    Implementuje interface wymagany przez Open Web UI:
    https://docs.openwebui.com/pipelines/
    """
    
    class Valves(BaseModel):
        """Konfigurowalne parametry (UI w Open Web UI)"""
        QDRANT_URL: str = "http://qdrant:6333"
        COLLECTION_NAME: str = "obsidian_notes"
        TOP_K: int = 5
        SIMILARITY_THRESHOLD: float = 0.7
        OLLAMA_BASE_URL: str = "http://ollama:11434"
        EMBEDDING_MODEL: str = "nomic-embed-text"
    
    def __init__(self):
        self.type = "filter"  # filter, manifold, or function
        self.name = "Obsidian RAG"
        self.valves = self.Valves()
        
        # Initialize clients
        self.qdrant = None
        self.embeddings = None
    
    async def on_startup(self):
        """Called when pipeline starts"""
        self.qdrant = QdrantClient(url=self.valves.QDRANT_URL)
        self.embeddings = OllamaEmbeddings(
            base_url=self.valves.OLLAMA_BASE_URL,
            model=self.valves.EMBEDDING_MODEL
        )
        print(f"Obsidian RAG Pipeline initialized")
    
    async def on_shutdown(self):
        """Called when pipeline stops"""
        pass
    
    def search_vault(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Wyszukaj w Vault
        
        Args:
            query: User query
            top_k: Number of results
        
        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Qdrant
        results = self.qdrant.search(
            collection_name=self.valves.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=self.valves.SIMILARITY_THRESHOLD
        )
        
        # Format results
        contexts = []
        for result in results:
            contexts.append({
                'content': result.payload['chunk'],
                'source': result.payload['source'],
                'title': result.payload['title'],
                'score': result.score
            })
        
        return contexts
    
    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process incoming request (before LLM)
        
        This is where we inject RAG context
        """
        # Get user's last message
        messages = body.get("messages", [])
        if not messages:
            return body
        
        last_message = messages[-1]
        user_query = last_message.get("content", "")
        
        # Search vault
        contexts = self.search_vault(user_query, top_k=self.valves.TOP_K)
        
        if contexts:
            # Build context string
            context_str = "\n\n".join([
                f"[From: {ctx['source']}]\n{ctx['content']}"
                for ctx in contexts
            ])
            
            # Inject context into system message
            system_message = {
                "role": "system",
                "content": f"""You are an AI assistant with access to the user's Obsidian knowledge base.

Use the following context from their notes to answer questions. If the context doesn't contain relevant information, say so and provide a general answer.

CONTEXT FROM OBSIDIAN VAULT:
{context_str}

When referencing information from the notes, mention the source file."""
            }
            
            # Insert system message at the beginning
            body["messages"] = [system_message] + messages
            
            print(f"RAG: Injected {len(contexts)} contexts for query: {user_query[:50]}...")
        
        return body
    
    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process outgoing response (after LLM)
        
        Could be used to add citations or metadata
        """
        return body


# Required for Open Web UI to load the pipeline
def get_pipeline():
    return Pipeline()
```

### 5. scripts/index_vault.py (Cron Job)

```python
"""
Reindeksacja Vault (uruchamiać codziennie przez cron)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from setup_rag import VaultIndexer
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="json", service_name="vault-indexer")
logger = get_logger(__name__)


def main():
    """Reindex vault"""
    logger.info("reindexing_started")
    
    vault_path = Path("/vault")
    
    try:
        indexer = VaultIndexer(
            vault_path=vault_path,
            qdrant_url="http://qdrant:6333"
        )
        
        # Clear old collection
        indexer.qdrant.delete_collection(indexer.collection_name)
        
        # Reindex
        indexer.run()
        
        logger.info("reindexing_completed")
        
    except Exception as e:
        logger.error("reindexing_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 6. requirements.txt (dla setup_rag.py)

```txt
# Vector DB
qdrant-client>=1.7.0

# Embeddings & LangChain
langchain>=0.1.0
langchain-community>=0.0.20
ollama>=0.1.0

# Document processing
markdown>=3.5.0
python-frontmatter>=1.1.0

# Utilities
tqdm>=4.66.0
```

### 7. Skrypt uruchomieniowy scripts/init_chat.sh

```bash
#!/bin/bash
set -e

echo "🚀 Initializing Chat System..."

# 1. Sprawdź czy Ollama ma embedding model
echo "📥 Downloading embedding model..."
docker exec brain-ollama ollama pull nomic-embed-text

# 2. Sprawdź czy Qdrant działa
echo "🔍 Checking Qdrant..."
curl -f http://localhost:6333/ || {
    echo "❌ Qdrant not running!"
    exit 1
}

# 3. Uruchom indeksowanie
echo "📚 Indexing Obsidian Vault..."
cd modules/chat
python setup_rag.py

# 4. Test RAG
echo "🧪 Testing RAG search..."
python -c "
from setup_rag import VaultIndexer
indexer = VaultIndexer('/vault')
results = indexer.qdrant.search(
    collection_name='obsidian_notes',
    query_vector=[0.1] * 768,
    limit=1
)
print(f'✅ RAG working! {len(results)} results found')
"

echo ""
echo "✅ Chat system ready!"
echo "   Open: http://localhost:3000"
echo ""
echo "First-time setup:"
echo "  1. Create account in Open Web UI"
echo "  2. Go to Settings → Models"
echo "  3. Select Ollama model (e.g., deepseek-r1:14b)"
echo "  4. Enable 'Obsidian RAG' pipeline in Settings → Pipelines"
```

### 8. Dokumentacja USER_GUIDE.md

```markdown
# Chat Interface User Guide

## Accessing the Chat

Open your browser and navigate to:
```
http://localhost:3000
```

## First-Time Setup

### 1. Create Account
- Click "Sign Up"
- Enter email and password
- First user becomes admin automatically

### 2. Select Model
- Go to **Settings** (gear icon)
- Navigate to **Models** tab
- Select your preferred model:
  - `deepseek-r1:14b` - Best for reasoning
  - `llama3.2:latest` - Faster, lighter
  - `mistral:latest` - Good balance

### 3. Enable RAG (Obsidian Search)
- Go to **Settings** → **Pipelines**
- Toggle **ON** for "Obsidian RAG"
- Configure parameters:
  - **TOP_K**: 5 (number of notes to retrieve)
  - **SIMILARITY_THRESHOLD**: 0.7 (minimum relevance)

## Using the Chat

### Basic Conversation
Just type your question and press Enter. The AI will respond using the selected model.

### Searching Your Notes
When RAG is enabled, the AI automatically searches your Obsidian vault for relevant context.

**Example queries:**
- "What did I learn about Python decorators?"
- "Summarize my notes on machine learning"
- "Find information about my project X"

The AI will:
1. Search your notes
2. Find relevant chunks
3. Include them in the context
4. Answer based on YOUR knowledge base

### Citations
The AI will mention which notes it used:
> "According to your note 'Python Tips.md'..."

## Tips for Best Results

### 1. Use Specific Queries
❌ "Tell me about AI"
✅ "What are the key points from my AI courses notes?"

### 2. Reference Your Notes
- "What did I write about X?"
- "Based on my notes, how should I..."
- "Find my notes on..."

### 3. Check Sources
Always verify important information by:
- Asking for sources: "Which note did this come from?"
- Opening the mentioned note in Obsidian

## Troubleshooting

### No results from my notes
1. Check if RAG pipeline is enabled
2. Verify vault path in settings
3. Re-run indexing: `docker exec brain-chat python /app/scripts/index_vault.py`

### Slow responses
- Use a smaller model (e.g., `llama3.2` instead of `deepseek-r1`)
- Reduce TOP_K in RAG settings
- Check if GPU is available: `docker exec brain-ollama ollama ps`

### Wrong information
- The AI hallucinates sometimes
- Always cross-reference with original notes
- Use more specific queries

## Advanced Features

### Chat History
All conversations are saved. Access them in the sidebar.

### Export Chat
Right-click conversation → Export → Markdown/JSON

### Multiple Conversations
Create separate chats for different topics:
- Click **+** in sidebar
- Name your conversation

## Maintenance

### Reindex Vault (after adding many notes)
```bash
docker exec brain-chat python /app/scripts/index_vault.py
```

### Backup Chat History
```bash
docker cp brain-chat:/app/backend/data ./backups/chat_$(date +%Y%m%d)
```

## Privacy Note

- All data stays LOCAL
- No external API calls (unless you configure them)
- Your notes never leave your machine
```

## 🎯 Kryteria Sukcesu

```bash
# 1. Uruchom inicjalizację
cd modules/chat
chmod +x scripts/init_chat.sh
./scripts/init_chat.sh

# 2. Sprawdź Open Web UI
open http://localhost:3000

# 3. Test RAG:
# W Open Web UI, zapytaj: "What are my notes about?"
# Expected: Odpowiedź z cytowaniem notatek z Vault

# 4. Sprawdź Qdrant
curl http://localhost:6333/collections/obsidian_notes
# Expected: JSON z info o kolekcji (count > 0)
```

### Checklist:
- [ ] Open Web UI działa na localhost:3000
- [ ] Możliwość stworzenia konta
- [ ] Model Ollama widoczny w Settings
- [ ] RAG pipeline można włączyć
- [ ] Wyszukiwanie w notatkach działa
- [ ] Cytuje źródła (nazwy plików)

## 📦 Pliki Wyjściowe

```
modules/chat/
├── setup_rag.py              ✅
├── requirements.txt          ✅
├── pipelines/
│   └── obsidian_rag.py      ✅
├── scripts/
│   ├── init_chat.sh         ✅
│   └── index_vault.py       ✅
└── USER_GUIDE.md            ✅
```

## 🔗 Zależności

**Wymaga:**
- ✅ Agent 1 (Ollama, Qdrant)
- ✅ Agent 4 (Refinery) - notatki w Vault

---

**Status:** 🟢 Gotowy
**Czas:** ~45 minut
**Następny:** Agent 7 (Migration & Testing)
