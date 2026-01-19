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
- **Dashboard:** [http://localhost:8501](http://localhost:8501) (Zakładka "Overview")
- **Czat:** [http://localhost:3000](http://localhost:3000)

---

## 📥 2. Zbieranie Wiedzy (Collector)

Najważniejszą funkcją systemu jest automatyczne "czytanie" i notowanie rzeczy za Ciebie.

### Jak dodać treść?
Po prostu wrzuć plik tekstowy z linkiem do folderu `00_Inbox` w Twoim Obsidianie.

#### YouTube 🎥
Chcesz notatkę z filmu?
1. Skopiuj link do filmu (np. `https://youtube.com/watch...`).
2. Stwórz plik w `00_Inbox` (nazwa dowolna, np. `ciekawy_film.txt`).
3. Wklej link do środka i zapisz.
4. **Gotowe!** Za kilka minut w folderze `YouTube` pojawi się notatka z podsumowaniem, kluczowymi punktami i pełną transkrypcją.

#### Artykuły WWW 📰
Znalazłeś ciekawy artykuł?
1. Skopiuj jego adres URL.
2. Stwórz plik w `00_Inbox` (np. `artykul_ai.txt`).
3. Wklej link.
4. **Gotowe!** System pobierze treść, usunie reklamy i stworzy notatkę w folderze `Articles`.

> **Wskazówka:** System automatycznie usuwa plik z linkiem z `00_Inbox` po poprawnym przetworzeniu.

---

## 💰 3. Finanse i Paragony

System posiada dedykowaną aplikację do cyfryzacji paragonów.

1. Wejdź na **[http://localhost:8501](http://localhost:8501)**.
2. Wybierz z menu po lewej **"📤 Upload & Verify"**.
3. **Wrzuć zdjęcie paragonu** (drag & drop).
4. Poczekaj chwileczkę - AI odczyta dane: Sklep, Datę, Kwotę i Listę zakupów.
5. **Sprawdź dane** w formularzu. Czasem AI myli "8" z "B", więc rzuć okiem.
6. Kliknij **"✅ Save to Database"**.

Twoje wydatki są teraz bezpieczne w bazie danych SQL i widoczne w zakładce **"📊 Expenses Dashboard"** pod postacią wykresów.

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

## 🛠️ 5. Rozwiązywanie Problemów

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
