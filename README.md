# Obsidian Brain v2 🧠

A microservices-based system for automating your Second Brain in Obsidian. Transforms a static note collection into an active, intelligent knowledge base using local AI.

## 🚀 Overview

**Obsidian Brain v2** refactors a monolithic script into a robust, scalable architecture powered by Docker and Local LLMs (Ollama).

**Key Features:**
- **📥 Universal Collector**: Automatically downloads and processes content from YouTube, Articles, and **Receipts**.
- **🤖 AI Refinery**: Processes raw content into structured Markdown notes.
- **💰 Finance Tracker**: Automated receipt OCR and data extraction (Headless).
- **💬 AI Chat (RAG)**: Chat with your knowledge base using Open Web UI.
- **🧠 Brain CLI**: Terminal Dashboard for status monitoring and management.

## 🏗️ Architecture

```mermaid
graph LR
    subgraph Input
        I1[00_Inbox / YouTube]
        I2[00_Inbox / Articles]
        I3[00_Inbox / Receipts]
    end

    subgraph Core Services
        C[Collector] -->|Raw Data| Q1[Redis Queue]
        Q1 --> R[Refinery]
        Q1 --> F[Finance]
        R -->|Markdown| V[Obsidian Vault]
        F -->|JSON| Archive[Data Archive]
    end

    subgraph Intelligence
        R <-->|Inference| O[Ollama (Local LLM)]
        F <-->|Extraction| O
        R -->|Embeddings| QD[Qdrant (Vector DB)]
    end

    subgraph User Interface
        Chat[Open Web UI] <-->|RAG| QD
        CLI[Brain CLI] -->|Monitor| Q1
    end
```

### Microservices
| Service | Technology | Description |
|---------|------------|-------------|
| **Collector** | Python | Watchdog service. Routes links vs images (receipts). |
| **Refinery** | Python, LangChain | AI Worker for content processing. |
| **Finance** | Python (Headless) | Receipt OCR and LLM extraction service. |
| **Chat** | Open Web UI | ChatGPT-like interface for chatting with your notes. |
| **CLI** | Python, Rich | Terminal UI for status and management. |

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

4. **Install CLI dependencies:**
   ```bash
   pip install -r requirements-cli.txt
   ```

5. **Start Services:**
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
To process a receipt, you can either:
- **Drag & Drop**: Copy an image (`.jpg`, `.png`) to the `data/inbox` folder.
- **CLI**: Use the helper command:
  ```bash
  python brain.py finance /path/to/receipt.jpg
  ```
The system will OCR the receipt and save structured data to `data/receipts_archive`.

### 3. Chatting with Notes
1. Open http://localhost:3000
2. Create an account (local only).
3. Select a model (e.g., `deepseek-r1`).
4. Ask questions about your notes!

### 4. Monitoring (CLI)
View the system status dashboard:
```bash
python brain.py status
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
