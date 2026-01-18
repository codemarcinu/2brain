FROM python:3.10-slim

# Metadata
LABEL maintainer="your@email.com"
LABEL description="Collector service for Obsidian Brain"

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    libsndfile1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Stwórz katalog aplikacji
WORKDIR /app

# Skopiuj requirements i zainstaluj zależności Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Zainstaluj shared library (zakładając że jest w parent directory, ale tutaj montujemy ją jako volume lub copy context)
# W docker-compose mamy:
#    - ./shared:/shared:ro
# Więc musimy zainstalować ją z tej lokalizacji. 
# Ale `pip install -e /shared` w Dockerfile zadziała tylko jeśli /shared jest dostępne w build context.
# Zamiast tego zrobimy to w docker-compose command lub założymy, że shared jest kopiowane.
# W naszej strukturze, shared jest obok modules.
# W produkcji najlepiej zbudować wheel shared i go zainstalować, 
# ale dla dev environment zrobimy trick w docker-compose lub założymy dostępność.

# Zmieniamy podejście: Zakładamy, że shared library będzie montowana jako volume w /shared
# więc instalujemy ją w trybie editable przy starcie lub tutaj jeśli kopiujemy context.
# Ale context buildu to ./modules/collector, więc nie mamy dostępu do ../../shared
# Rozwiązanie: W docker-compose context ustawimy na root lub użyjemy mounted volume.
# Zgodnie z planem: "Zainstaluj shared library (zakładając że jest w parent directory)" - to było w planie, ale w dockerfile context jest modules/collector.

# Poprawka: Aby to działało poprawnie w dev, zainstalujemy /shared w CMD lub entrypoint, 
# ALBO (lepiej) w docker-compose.yml dodamy `command: sh -c "pip install -e /shared && python main.py"`
# Jedakże, w planie mieliśmy: `RUN pip install -e /shared`. To zadziała tylko jeśli skopiujemy shared do obrazu.
# Ponieważ shared jest poza contextem (modules/collector), nie możemy go COPY w prosty sposób bez zmiany contextu builda.

# Przyjmijmy, że w `docker-compose.yml` context jest `./modules/collector`, więc nie mamy `shared`.
# W takim razie usuniemy `RUN pip install -e /shared` z Dockerfile i dodamy to do command w docker-compose,
# ponieważ montujemy volume `/shared`.

# Zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

# Uruchom serwis - instalujemy shared przy starcie bo jest montowane jako volume
CMD ["sh", "-c", "pip install -e /shared && python main.py"]
