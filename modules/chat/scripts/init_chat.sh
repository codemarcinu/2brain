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
results = indexer.qdrant.query_points(
    collection_name='obsidian_notes',
    query=[0.1] * 768,
    limit=1
).points
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
