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
