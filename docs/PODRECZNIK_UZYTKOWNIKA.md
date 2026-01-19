# Podręcznik Użytkownika - Obsidian Brain v2

Witaj w Twoim nowym cyfrowym mózgu! 🧠

Ten system pomaga Ci automatycznie zbierać, przetwarzać i wykorzystywać wiedzę, którą znajdujesz w internecie, oraz zarządzać finansami osobistymi.

---

## 🚀 1. Szybki Start

### Włączanie Systemu
Aby uruchomić system (jeśli został zainstalowany):
1. Otwórz terminal w folderze projektu.
2. Wpisz komendę:
   ```bash
   docker compose up -d
   ```
3. Poczekaj chwilę, aż wszystkie serwisy wstaną.

### Sprawdzenie czy działa
- **Dashboard (CLI):** Uruchom w terminalu `python brain.py status`
- **Czat:** [http://localhost:3000](http://localhost:3000)

---

## 📥 2. Zbieranie Wiedzy (Collector)

Najważniejszą funkcją systemu jest automatyczne "czytanie" i notowanie rzeczy za Ciebie.

### Jak dodać treść?
Po prostu wrzuć plik do folderu `00_Inbox` w Twoim Obsidianie.

#### YouTube 🎥
Chcesz notatkę z filmu?
1. Skopiuj link do filmu (np. `https://youtube.com/watch...`).
2. Stwórz plik `.txt` w `00_Inbox` (np. `ciekawy_film.txt`).
3. Wklej link do środka i zapisz.
4. **Gotowe!** Za kilka minut w folderze `YouTube` pojawi się notatka.

#### Artykuły WWW 📰
Znalazłeś ciekawy artykuł?
1. Skopiuj jego adres URL.
2. Stwórz plik `.txt` w `00_Inbox`.
3. Wklej link.
4. **Gotowe!** Notatka pojawi się w folderze `Articles`.

---

## 💰 3. Finanse i Paragony

System automatycznie przetwarza zdjęcia paragonów, wyciągając z nich datę, sklep i kwotę.

### Jak dodać paragon?
Masz dwie opcje:

**Opcja 1: Drag & Drop**
1. Skopiuj zdjęcie paragonu (`.jpg` lub `.png`) do folderu `00_Inbox`.
2. System wykryje plik graficzny i automatycznie go przetworzy.
3. Wynik (plik JSON) zostanie zapisany w `data/receipts_archive`.

**Opcja 2: Brain CLI**
Jeśli masz paragon gdzieś indziej na dysku, użyj komendy:
```bash
python brain.py finance /ścieżka/do/paragonu.jpg
```

System użyje OCR oraz Sztucznej Inteligencji (LLM), aby „przeczytać” Twój paragon i zapisać wydatki. 

> [!TIP]
> **System uczy się Twoich zakupów!** Dzięki funkcji "Async Receipt Pipeline", system zapamiętuje produkty i sklepy. Przy kolejnych zakupach tych samych produktów przetwarzanie będzie błyskawiczne (nawet 5x szybciej), ponieważ system nie będzie musiał pytać Sztucznej Inteligencji o każdy produkt z osobna.

---

## 💬 4. Czat z Twoją Wiedzą (RAG)

Możesz rozmawiać ze swoimi notatkami tak jak z ChatGPT.

1. Wejdź na **[http://localhost:3000](http://localhost:3000)**.
2. Załóż konto (dane są tylko lokalne, nigdzie nie wysyłane).
3. Wybierz model (np. `deepseek-r1:14b` lub `llama3`).
4. Upewnij się w **Ustawieniach**, że pipeline "Obsidian RAG" jest włączony.

### Przykładowe pytania:
- *"Co ostatnio zapisałem na temat uczenia maszynowego?"*
- *"Podsumuj moje notatki o projekcie X"*
- *"Jakie wnioski wyciągnąłem z filmu o Pythonie?"*

AI przeszuka Twoje notatki, znajdzie odpowiednie fragmenty i odpowie na bazie Twojej wiedzy, podając źródła (nazwy plików).

---

## 🗃️ 5. Migracja Danych
Jeśli przenosisz się ze starego systemu, przygotowaliśmy specjalny poradnik migracji.
👉 **[Instrukcja Migracji](MIGRATION_GUIDE.md)**
Znajdziesz tam informacje jak przenieść swoje stare notatki i paragony do nowego systemu.

---

## 🛠️ 6. Rozwiązywanie Problemów

**Nic się nie dzieje po wrzuceniu linku?**
1. Sprawdź, czy Docker działa.
2. Upewnij się, że plik w `00_Inbox` ma rozszerzenie `.txt` i zawiera *tylko* link (bez spacji).
3. Sprawdź logi Collectora: `docker compose logs -f collector`.

**Czat nie widzi nowych notatek?**
System potrzebuje chwili na zaindeksowanie. Możesz wymusić reindeksację komendą w terminalu:
```bash
docker exec brain-chat python /app/scripts/index_vault.py
```

**Błędy przy paragonach?**
Jeśli zdjęcie jest bardzo niewyraźne, OCR może sobie nie poradzić. Spróbuj zrobić zdjęcie z lepszym światłem lub wpisz dane ręcznie.

---

*Miłego korzystania z Twojego Drugiego Mózgu!*
