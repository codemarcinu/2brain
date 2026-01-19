# Obsidian Brain v2 🧠

A microservices-based system for automating your Second Brain in Obsidian. Transforms a static note collection into an active, intelligent knowledge base using local AI.

## 🚀 Overview

**Obsidian Brain v2** refactors a monolithic script into a robust, scalable architecture powered by Docker and Local LLMs (Ollama).

**Key Features:**
- **📥 Universal Collector**: Automatically downloads and processes content from YouTube (audio+transcription) and Web Articles.
- **🤖 AI Refinery**: Processes raw content into structured Markdown notes with summaries, tags, and metadata using local LLMs.
- **💰 Finance Tracker**: specialized UI for uploading and digitizing receipts into structured data.
- **💬 AI Chat (RAG)**: Chat with your knowledge base using Open Web UI and vector search (Qdrant).
- **📊 Monitoring**: Real-time dashboard for system health and task queues.

## 🏗️ Architecture

```mermaid
graph LR
    subgraph Input
        I1[00_Inbox / YouTube]
        I2[00_Inbox / Articles]
        I3[Finance UI]
    end

    subgraph Core Services
        C[Collector] -->|Raw Data| Q1[Redis Queue]
        Q1 --> R[Refinery]
        R -->|Markdown| V[Obsidian Vault]
        I3 -->|Receipt Data| DB[PostgreSQL]
    end

    subgraph Intelligence
        R <-->|Inference| O[Ollama (Local LLM)]
        R -->|Embeddings| QD[Qdrant (Vector DB)]
        V -->|Indexing| QD
    end

    subgraph User Interface
        Chat[Open Web UI] <-->|RAG| QD
        Chat <-->|LLM| O
        Dash[Streamlit Dashboard]
    end
```

### Microservices
| Service | Technology | Description |
|---------|------------|-------------|
| **Collector** | Python | Watchdog service for `00_Inbox`. Downloads YT audio/video & scrapes web pages. |
| **Refinery** | Python, LangChain | AI Worker. Summarizes content, extracts tags, generates Markdown. |
| **Finance** | Streamlit | Web UI for receipt processing and expense tracking. |
| **Chat** | Open Web UI | ChatGPT-like interface for chatting with your notes. |
| **Infrastructure** | Redis, Postgres, Qdrant | Message broker, relational DB, and vector store. |

## 🛠️ Installation

### Prerequisites
- **Docker** & **Docker Compose**
- **NVIDIA GPU** (Recommended for local LLMs) or robust CPU
- **Obsidian Vault** existing on disk

### Setup
1. **Clone the repository:**
   ```bash
   git clone <repo-url> obsidian-brain-v2
   cd obsidian-brain-v2
   ```

2. **Initialize the project:**
   ```bash
   # Creates necessary directories and checks environment
   ./scripts/init.sh
   ```

3. **Configure Environment:**
   Copy `.env.example` to `.env` and edit:
   ```bash
   cp .env.example .env
   nano .env
   ```
   *Critical settings:* `OBSIDIAN_VAULT_PATH`, `POSTGRES_PASSWORD`.

4. **Start Services:**
   ```bash
   docker compose up -d
   ```

## 📖 Usage Guide

### 1. Saving Content (Collector)
Simply drop a text file with a URL into your Obsidian Inbox folder (e.g., `00_Inbox`):
- **YouTube**: Create `video_ideas.txt` containing a YouTube link.
- **Articles**: Create `article_research.txt` containing a web URL.
*The Collector will pick it up, process it, and the Refinery will create a new Note in your vault.*

### 2. Expense Tracking (Finance)
1. Open http://localhost:8501
2. Upload a photo of a receipt.
3. Verify the extracted data and click Save.

### 3. Chatting with Notes
1. Open http://localhost:3000
2. Create an account (local only).
3. Select a model (e.g., `deepseek-r1`).
4. Ask questions about your notes!

### 4. Monitoring
1. Run the dashboard:
   ```bash
   streamlit run scripts/monitoring/dashboard.py
   ```
2. Or use the CLI health check:
   ```bash
   python scripts/monitoring/health_check.py
   ```

## 🔧 Operations

### Backups
- **Database**: `./scripts/backup/backup_postgres.sh`
- **Vault**: Your Vault should be backed up separately (e.g., `git`, `Time Machine`).

### Logs
View logs for all services:
```bash
docker compose logs -f
```
View specific service (e.g., Refinery):
```bash
docker compose logs -f refinery
```

## 📂 Project Structure
```
obsidian-brain-v2/
├── docker-compose.yml       # Service orchestration
├── shared/                  # Common Python library (logging, config, messaging)
├── modules/                 # Service source code
│   ├── collector/
│   ├── refinery/
│   ├── finance/
│   └── chat/
├── data/                    # Docker volumes (persistence)
├── scripts/                 # Maintenance & migration scripts
└── docs/                    # Documentation
```

## 📚 Documentation

For more detailed information, please refer to:

- **[User Manual (PL)](docs/PODRECZNIK_UZYTKOWNIKA.md)**: How to use Collector, Finance, and Chat features.
- **[Technical Documentation (PL)](docs/DOKUMENTACJA_TECHNICZNA.md)**: Deep dive into architecture, schemas, and API.
- **[Migration Guide](docs/MIGRATION_GUIDE.md)**: How to upgrade from v1.
- **[Project Status](docs/PROJECT_STATUS.md)**: Current roadmap and completed features.

## 🤝 Contributing
See `docs/PROJECT_STATUS.md` for current progress and roadmap.

---
*Powered by Google Antigravity Agents*
