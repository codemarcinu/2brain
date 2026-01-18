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
