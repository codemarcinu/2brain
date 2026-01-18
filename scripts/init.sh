#!/bin/bash
set -e

echo "🚀 Inicjalizacja Obsidian Brain v2..."

# Sprawdź czy Docker działa
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker nie działa. Uruchom Docker Desktop."
    exit 1
fi

# Sprawdź czy nvidia-docker jest dostępny (dla GPU)
if ! docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    echo "⚠️  NVIDIA GPU niedostępne. Ollama będzie wolniejszy."
    echo "   Kontynuować bez GPU? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Skopiuj .env.example jeśli .env nie istnieje
if [ ! -f .env ]; then
    echo "📝 Tworzę plik .env z przykładowej konfiguracji..."
    cp .env.example .env
    echo "⚠️  WAŻNE: Edytuj plik .env i ustaw właściwe ścieżki!"
    echo "   - OBSIDIAN_VAULT_PATH"
    echo "   - INBOX_PATH"
fi

# Stwórz katalogi danych
echo "📁 Tworzę katalogi danych..."
mkdir -p data/{redis,postgres,qdrant,ollama,open-webui}

# Uruchom infrastrukturę
echo "🐳 Uruchamiam kontenery Docker..."
docker compose up -d redis postgres qdrant ollama

# Czekaj aż serwisy będą gotowe
echo "⏳ Czekam na gotowość serwisów..."
sleep 10

# Sprawdź status
echo "🔍 Sprawdzam status serwisów..."
docker compose ps

# Pobierz model do Ollama
echo "🤖 Pobieram model AI do Ollama (może to chwilę potrwać)..."
docker exec brain-ollama ollama pull deepseek-r1:14b

echo ""
echo "✅ Infrastruktura gotowa!"
echo ""
echo "Dostępne serwisy:"
echo "  - Redis:        localhost:6379"
echo "  - PostgreSQL:   localhost:5432"
echo "  - Qdrant:       localhost:6333"
echo "  - Ollama:       localhost:11434"
echo ""
echo "Następne kroki:"
echo "  1. Edytuj plik .env (ustaw ścieżki)"
echo "  2. Uruchom Agent 2 (Shared Library)"
echo "  3. docker compose logs -f  (aby obserwować logi)"
