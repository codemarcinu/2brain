# Agent 1: Infrastructure Setup

## 🎭 Rola
**DevOps Infrastructure Engineer**

## 🎯 Cel
Zbudowanie podstawowej infrastruktury containerowej dla systemu mikroserwisów

## 📖 Kontekst

Refaktoryzujemy monolityczną aplikację Python do architektury mikroserwisowej. Potrzebujemy bazowej infrastruktury:
- **Kolejka zadań** (Redis) - komunikacja między serwisami
- **Baza danych** (PostgreSQL) - trwałe dane finansowe
- **Serwer AI** (Ollama) - lokalne modele LLM
- **Interfejs czatu** (Open Web UI) - frontend dla użytkownika

System będzie działał lokalnie w Docker, z możliwością późniejszego wdrożenia na serwer.

## ✅ Zadania

### 1. Stwórz Strukturę Katalogów

```bash
mkdir -p obsidian-brain-v2/{modules/{collector,refinery,finance,chat},shared,data/{redis,postgres,qdrant,ollama},scripts}
cd obsidian-brain-v2
```

Struktura powinna wyglądać tak:
```
obsidian-brain-v2/
├── modules/
│   ├── collector/
│   ├── refinery/
│   ├── finance/
│   └── chat/
├── shared/
├── data/
│   ├── redis/
│   ├── postgres/
│   ├── qdrant/
│   └── ollama/
└── scripts/
```

### 2. Przygotuj Plik `docker-compose.yml`

Stwórz plik z następującymi serwisami:

#### Redis (Kolejka Zadań)
```yaml
redis:
  image: redis:7-alpine
  container_name: brain-redis
  ports:
    - "6379:6379"
  volumes:
    - ./data/redis:/data
  command: redis-server --appendonly yes
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - brain-network
  restart: unless-stopped
```

#### PostgreSQL (Baza Danych)
```yaml
postgres:
  image: postgres:16-alpine
  container_name: brain-postgres
  environment:
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
  ports:
    - "5432:5432"
  volumes:
    - ./data/postgres:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - brain-network
  restart: unless-stopped
```

#### Ollama (Serwer AI)
```yaml
ollama:
  image: ollama/ollama:latest
  container_name: brain-ollama
  ports:
    - "11434:11434"
  volumes:
    - ./data/ollama:/root/.ollama
  environment:
    - OLLAMA_HOST=0.0.0.0
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
  healthcheck:
    test: ["CMD", "ollama", "list"]
    interval: 30s
    timeout: 10s
    retries: 3
  networks:
    - brain-network
  restart: unless-stopped
```

#### Qdrant (Baza Wektorowa)
```yaml
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
```

#### Open Web UI (Interfejs Czatu)
```yaml
open-webui:
  image: ghcr.io/open-webui/open-webui:main
  container_name: brain-chat
  ports:
    - "3000:8080"
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
    - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
    - ENABLE_RAG_WEB_SEARCH=true
  volumes:
    - ./data/open-webui:/app/backend/data
  depends_on:
    ollama:
      condition: service_healthy
  networks:
    - brain-network
  restart: unless-stopped
```

#### Sieć
```yaml
networks:
  brain-network:
    driver: bridge
    name: brain-network
```

### 3. Stwórz Plik `.env.example`

```env
# PostgreSQL Configuration
POSTGRES_USER=brain
POSTGRES_PASSWORD=changeme_in_production
POSTGRES_DB=obsidian_brain

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Ollama Configuration
OLLAMA_HOST=ollama:11434
OLLAMA_MODEL=deepseek-r1:14b

# Open Web UI
WEBUI_SECRET_KEY=generate_random_secret_here

# API Keys (opcjonalne - dla zewnętrznych serwisów)
OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=

# Paths
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
INBOX_PATH=/path/to/00_Inbox
```

### 4. Stwórz Plik `.gitignore`

```gitignore
# Environment
.env

# Data volumes
data/redis/*
data/postgres/*
data/qdrant/*
data/ollama/*
data/open-webui/*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary
tmp/
temp/
```

### 5. Stwórz Skrypt Pomocniczy `scripts/init.sh`

```bash
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
```

### 6. Stwórz Plik `README-infrastructure.md`

```markdown
# Infrastruktura - Obsidian Brain v2

## Architektura

System składa się z 5 głównych serwisów:

1. **Redis** - Kolejka zadań (port 6379)
2. **PostgreSQL** - Baza danych (port 5432)
3. **Qdrant** - Baza wektorowa dla RAG (port 6333)
4. **Ollama** - Serwer modeli AI (port 11434)
5. **Open Web UI** - Interfejs czatu (port 3000)

## Wymagania

### Minimalne
- Docker 24.0+
- Docker Compose 2.20+
- 16GB RAM
- 50GB wolnego miejsca

### Zalecane
- NVIDIA GPU (dla Ollama)
- nvidia-docker runtime
- 32GB RAM
- 100GB SSD

## Instalacja

### 1. Przygotowanie
```bash
# Sklonuj/utwórz projekt
mkdir obsidian-brain-v2
cd obsidian-brain-v2

# Uruchom skrypt inicjalizacyjny
chmod +x scripts/init.sh
./scripts/init.sh
```

### 2. Konfiguracja
Edytuj plik `.env`:
```bash
nano .env
```

Ustaw co najmniej:
- `OBSIDIAN_VAULT_PATH` - ścieżka do Twojego Vault
- `INBOX_PATH` - folder 00_Inbox
- `POSTGRES_PASSWORD` - zmień hasło!

### 3. Uruchomienie
```bash
# Uruchom wszystkie serwisy
docker compose up -d

# Sprawdź status
docker compose ps

# Obserwuj logi
docker compose logs -f
```

## Zarządzanie

### Podstawowe Komendy

```bash
# Uruchom wszystko
docker compose up -d

# Zatrzymaj wszystko
docker compose down

# Restart konkretnego serwisu
docker compose restart ollama

# Logi konkretnego serwisu
docker compose logs -f redis

# Wejdź do kontenera
docker exec -it brain-redis redis-cli
docker exec -it brain-postgres psql -U brain -d obsidian_brain
```

### Monitorowanie

**Redis Queue:**
```bash
docker exec -it brain-redis redis-cli
127.0.0.1:6379> LLEN queue:refinery
127.0.0.1:6379> LRANGE queue:refinery 0 -1
```

**PostgreSQL:**
```bash
docker exec -it brain-postgres psql -U brain -d obsidian_brain
# SELECT * FROM expenses LIMIT 10;
```

**Ollama Models:**
```bash
docker exec brain-ollama ollama list
docker exec brain-ollama ollama run deepseek-r1:14b "Hello"
```

## Troubleshooting

### Problem: Ollama nie startuje (GPU)
**Rozwiązanie:**
```bash
# Sprawdź czy GPU jest widoczne
nvidia-smi

# Sprawdź nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi

# Jeśli brak GPU, usuń sekcję deploy w docker-compose.yml
```

### Problem: PostgreSQL nie przyjmuje połączeń
**Rozwiązanie:**
```bash
# Sprawdź logi
docker compose logs postgres

# Sprawdź czy port jest zajęty
lsof -i :5432

# Restart z czystymi danymi (UWAGA: usuwa dane!)
docker compose down
rm -rf data/postgres/*
docker compose up -d postgres
```

### Problem: Redis brak pamięci
**Rozwiązanie:**
```bash
# Sprawdź użycie pamięci
docker exec brain-redis redis-cli INFO memory

# Wyczyść kolejki
docker exec brain-redis redis-cli FLUSHDB
```

### Problem: Brak miejsca na dysku
**Rozwiązanie:**
```bash
# Sprawdź wielkość wolumenów
du -sh data/*

# Wyczyść nieużywane obrazy
docker system prune -a

# Wyczyść stare modele Ollama
docker exec brain-ollama rm -rf /root/.ollama/models/old_models
```

## Backup i Restore

### Backup PostgreSQL
```bash
docker exec brain-postgres pg_dump -U brain obsidian_brain > backup_$(date +%Y%m%d).sql
```

### Restore PostgreSQL
```bash
docker exec -i brain-postgres psql -U brain obsidian_brain < backup_20250118.sql
```

### Backup Redis
```bash
docker exec brain-redis redis-cli SAVE
cp data/redis/dump.rdb backup_redis_$(date +%Y%m%d).rdb
```

## Bezpieczeństwo

### Produkcja
Jeśli planujesz wystawić na sieć:

1. **Zmień hasła:**
   - PostgreSQL: `POSTGRES_PASSWORD`
   - Web UI: `WEBUI_SECRET_KEY`

2. **Firewall:**
   ```bash
   # Zablokuj porty na zewnątrz (tylko localhost)
   sudo ufw deny 6379  # Redis
   sudo ufw deny 5432  # PostgreSQL
   ```

3. **HTTPS:**
   - Dodaj reverse proxy (nginx/traefik)
   - Certyfikaty SSL (Let's Encrypt)

## Performance Tuning

### Ollama (GPU)
```yaml
# W docker-compose.yml dodaj:
environment:
  - OLLAMA_NUM_GPU=1
  - OLLAMA_MAX_LOADED_MODELS=2
```

### PostgreSQL
```yaml
# W docker-compose.yml dodaj:
command:
  - postgres
  - -c
  - shared_buffers=256MB
  - -c
  - max_connections=100
```

### Redis
```yaml
# W docker-compose.yml zmień:
command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## Następne Kroki

✅ Infrastruktura gotowa
⏭️ Przejdź do **Agent 2: Shared Library**
```

## 🎯 Kryteria Sukcesu

### Walidacja po wykonaniu:

```bash
# 1. Wszystkie kontenery działają
docker compose ps
# Expected: All services "Up" and "healthy"

# 2. Redis odpowiada
docker exec brain-redis redis-cli ping
# Expected: PONG

# 3. PostgreSQL przyjmuje połączenia
docker exec brain-postgres pg_isready -U brain
# Expected: accepting connections

# 4. Ollama ma pobrany model
docker exec brain-ollama ollama list
# Expected: deepseek-r1:14b

# 5. Qdrant działa
curl http://localhost:6333/
# Expected: {"title":"qdrant - vector search engine",...}
```

### Checklist końcowy:

- [ ] Wszystkie 5 kontenerów działa (docker compose ps)
- [ ] Plik .env utworzony i skonfigurowany
- [ ] Katalogi data/* utworzone
- [ ] Redis PING zwraca PONG
- [ ] PostgreSQL akceptuje połączenia
- [ ] Ollama ma pobrany model deepseek-r1:14b
- [ ] Qdrant API odpowiada na localhost:6333
- [ ] Dokumentacja README-infrastructure.md kompletna

## 📦 Pliki Wyjściowe

Po zakończeniu pracy tego agenta powinny istnieć:

```
obsidian-brain-v2/
├── docker-compose.yml       ✅ Główna orkiestracja
├── .env                     ✅ Konfiguracja (z .env.example)
├── .gitignore              ✅ Wykluczenia z Git
├── README-infrastructure.md ✅ Dokumentacja
├── scripts/
│   └── init.sh             ✅ Skrypt inicjalizacyjny
├── modules/                 ✅ Puste katalogi gotowe na kod
│   ├── collector/
│   ├── refinery/
│   ├── finance/
│   └── chat/
├── shared/                  ✅ Pusty katalog (dla Agenta 2)
└── data/                    ✅ Katalogi dla wolumenów
    ├── redis/
    ├── postgres/
    ├── qdrant/
    ├── ollama/
    └── open-webui/
```

## 🔗 Zależności

**Wymaga:**
- ❌ Brak (pierwszy agent)

**Wymagane przez:**
- ✅ Agent 2 (Shared Library) - potrzebuje działającego Redis
- ✅ Agent 3-7 (Wszystkie serwisy aplikacyjne)

## 💡 Wskazówki dla Google Antigravity

### Jak ustawić agenta:

1. **Workspace:** Utwórz nowy folder `obsidian-brain-v2`
2. **Execution Mode:** Sequential (krok po kroku)
3. **Validation:** Uruchom `./scripts/init.sh` po wygenerowaniu plików
4. **Output Check:** Sprawdź czy `docker compose ps` pokazuje wszystkie serwisy

### Możliwe problemy:

**NVIDIA GPU niedostępne:**
- Agent może zasugerować usunięcie sekcji `deploy.resources` z `docker-compose.yml`
- System będzie wolniejszy ale działający

**Porty zajęte:**
- Zmień porty w `docker-compose.yml` (np. 6379→6380)
- Zaktualizuj `.env` odpowiednio

**Brak miejsca na dysku:**
- Agent powinien ostrzec jeśli < 50GB wolnego
- Zasugerować czyszczenie `docker system prune -a`

---

**Status:** 🟢 Gotowy do uruchomienia
**Czas wykonania:** ~15-30 minut (w zależności od pobierania modelu Ollama)
**Następny agent:** Agent 2 - Shared Library
