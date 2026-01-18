---
title: Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 2_transkrypcja
created: "2026-01-16 10:08"
summary: Notatka dokumentuje sesję szkoleniową poświęconą narzędziom OSINT oraz ich zastosowaniu w bezpieczeństwie cyfrowym, z naciskiem na praktyczne umiejętności i techniki.
type: refined
tags:
  - osint
  - cybersec
  - tools
  - metadata
  - dora
  - do-weryfikacji
suggested_category: Review
status: do-weryfikacji
---

# Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 2_transkrypcja

> [!abstract] Podsumowanie
> Notatka dokumentuje sesję szkoleniową poświęconą narzędziom OSINT oraz ich zastosowaniu w bezpieczeństwie cyfrowym, z naciskiem na praktyczne umiejętności i techniki.

## 📝 Treść

---
title: Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 2_transkrypcja
created: "2026-01-16 09:42"
summary: Szkolenie koncentruje się na narzędziach OSINT, logistyce spotkań oraz edukacji w zakresie cyberbezpieczeństwa, z elementami interakcji i dyskusji.
type: transcript
tags:
  - calendar
  - compliance
  - compliance/dora
  - compliance/nis2
  - compliance/rodo
  - cybersec
  - cybersec/blue-team
  - cybersec/osint
  - productivity
  - tech
  - tech/python
  - todo
  - source/drive_import
status: do-weryfikacji
source_file: Drive_0824_Narzędziownik OSINT 2.0 Reloaded - sesja 2_transkrypcja.txt
---

# Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 2_transkrypcja

> [!abstract] Podsumowanie
> Szkolenie koncentruje się na narzędziach OSINT, logistyce spotkań oraz edukacji w zakresie cyberbezpieczeństwa, z elementami interakcji i dyskusji.

## 📝 Treść

## Szkolenie Narzędziownik OSINT Edycja 2.0

### Wprowadzenie
Witamy uczestników na szkoleniu Narzędziownik OSINT edycja 2.0. Uczestnicy mieli możliwość wcześniejszych spotkań, a szkolenie koncentruje się na technikach zbierania informacji z wykorzystaniem narzędzi OSINT. Szkolenie ma na celu rozwój umiejętności w zakresie bezpieczeństwa cyfrowego.

### Prezentacja Trenera
Trener z ponad 16-letnim doświadczeniem w cyberbezpieczeństwie, przedstawia siebie oraz możliwości kontaktu przez e-mail oraz LinkedIn. Uczestnicy są zachęcani do zadawania pytań w każdym momencie.

### Agenda Szkolenia
1. Narzędzia
2. Techniki poszukiwania informacji
3. Bezpieczeństwo operacji

### Logistyka Spotkań
Szkolenia będą trwały około trzech godzin z dwoma przerwami. Pytania mogą być zadawane w dowolnym momencie z oznaczeniem „Q”.

### Tematy Szkolenia
- Zasady rekonesansu ofensywnego
- Techniki poszukiwania informacji o firmach i osobach
- Użycie narzędzi takich jak Google Hack Database (Dorki)

### Bezpieczeństwo i Zasady
Uczestnicy są instruowani, aby:
- Unikać logowania się w oczywistych miejscach (np. dom)
- Użyć VPN lub Tor w celu anonimowości
- Nie ograniczać się do Google

### Dorki i Techniki Wyszukiwania
Uczestnicy poznają techniki wyszukiwania na podstawie operatorów w Google, takich jak `site` do poszukiwania informacji o konkretnej domenie. Wprowadzono również operator `intitle` do wyszukiwania plików oraz `OR` w kontekście wyszukiwania specyficznych terminów. Dodatkowo omawia się wykorzystanie LinkedIn w celach zbierania danych o pracownikach firmy.

### Wyciek Danych i Przykłady
Przykłady z życia pokazują potencjalne luki bezpieczeństwa, jak np. dostęp do plików ze wrażliwymi informacjami, które mogą być nieświadomie udostępnione.

### API i Zabezpieczenia
Zwrócono uwagę na możliwość nieautoryzowanego dostępu do API, które nie są odpowiednio zabezpieczone oraz znaczenie odpowiedniej konfiguracji serwerów FTP.

### Narzędzia i Techniki
Uczestnicy poznają narzędzia takie jak CRTSH, które pomagają zbierać informacje o certyfikatach SSL oraz Google Docs, które mogą zawierać dane wrażliwe.

## 📝 Actions
TODO: Przeprowadzić ćwiczenia na trzecim spotkaniu, aby utrwalić zdobytą wiedzę.  
TODO: Zaoferować uczestnikom dostęp do dodatkowych zasobów i serwerów Discord.

## 📅 Calendar
TERMIN: 13. - następne spotkanie dotyczące narzędzi związanych ze sztuczną inteligencją i bezpieczeństwem operacyjnym.  [Synced](https://www.google.com/calendar/event?eid=aW40cjNpZG00OHQ0bzRyaWk2b3RydTQ0amcgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Czym jest OSINT? :: OSINT (Open Source Intelligence) to zbieranie informacji ze źródeł ogólnodostępnych.  
#flashcard Jakie techniki wykorzystuje OSINT? :: Używa operatorów wyszukiwania, narzędzi do analizy danych, informacji dostępnych w sieci.  
#flashcard Jakie są zasady bezpiecznego poszukiwania danych? :: Unikać logowania w publicznych sieciach, korzystać z VPN oraz Tor.

## Metadane w plikach

Metadane to dodatkowe informacje o plikach, które mogą być cenne dla analizy danych i bezpieczeństwa. Oto kluczowe zagadnienia dotyczące metadanych oraz ich zastosowanie w różnych kontekstach.

### Definicja metadanych
Metadane to dane o danych, które opisują dodatkowe właściwości plików, normalnie niewidoczne dla użytkowników. Przykłady obejmują informacje dotyczące:
- Geolokalizacji zdjęć.
- Autora dokumentów tekstowych.
- Technicznych detali zdjęć (aparat, przesłona, ogniskowa).

### Rodzaje metadanych
Istnieją trzy główne standardy metadanych:
1. **IPTC (International Press Telecommunications Council)**
   - Zawiera dane redakcyjne, takie jak autorstwo i prawa autorskie.
  
2. **EXIF (Exchangeable Image File Format)**
   - Opracowany przez Josha Meissnera, definiuje metadane dla zdjęć, obejmujące ustawienia aparatu i geolokalizację. Umożliwia de facto rozszerzalne metadane w formacie XML.
  
3. **XMP (Extensible Metadata Platform)**
   - Opracowany przez Adobe, przechowuje metadane w systemie XML RDF, umożliwiając integrację z EXIF i IPTC oraz dodawanie własnych pól zgodnych z Dublin Core.

### Aspekty bezpieczeństwa (DORA, NIS2, RODO)
Z perspektywy ochrony danych osobowych, metadane mogą zawierać informacje, które podlegają regulacjom, takim jak RODO. Konieczne jest ich odpowiednie zarządzanie, zwłaszcza w kontekście przesyłania i przechowywania plików. Od 2019 roku wiele platform usuwa metadane podczas przesyłania plików, co wpływa na integralność i dane osobowe charakteryzujące zdjęcia czy dokumenty.

### Walidacja i zarządzanie metadanymi
Zaleca się korzystanie z narzędzi takich jak **ExifTool** do analizy i modyfikacji metadanych, co pozwala na śledzenie zmian oraz wykonywanie audytów.

```bash
exiftool -A -U -G1 filename
```

### Użycie metadanych w informatyce śledczej
W kontekście informatyki śledczej znajomość i umiejętność analizowania metadanych pozwala na określenie czy dane zostały zmienione (EXIF tampering) oraz ich pochodzenie, co jest kluczowe w procesach dowodowych.

## 📝 Actions
TODO: Monitorować zmiany w regulacjach dotyczących zarządzania metadanymi.
TODO: Przeszkolić zespół w zakresie wykorzystania metadanych w procesach analizy danych.
TODO: Zastosować ExifTool w projektach analitycznych do walidacji metadanych.

## 🧠 Flashcards
#flashcard Co to są metadane? :: Dane o danych, które dostarczają dodatkowych informacji o pliku.
#flashcard Jakie są podstawowe rodzaje metadanych? :: IPTC, EXIF, XMP.
#flashcard Jakie narzędzie służy do zarządzania metadanymi? :: ExifTool.

## 🖼️ Analiza Plików Obrazów i Metadanych

### Rozmiar i Suma Kontrolna
Podczas analizy plików obrazów, takich jak PNG, istotne jest zbadanie ich rozmiaru przed i po przetworzeniu oraz sprawdzenie sumy kontrolnej.

### Metadane Obrazu
ExifTool może pomóc w wykrywaniu problemów z plikami. Nawet gdy plik jest otwierany przez system, mogą występować informacje o uszkodzeniach. 

#### Przykład Pliku Obraz.png
W pliku `obraz.png` dane są związane z formatem PNG, w tym rozdzielczość. 

### Steganografia
Steganografia to technika zabezpieczania danych w innych obiektach, na przykład w obrazach. Można zapisać tajny komunikat w pliku z obrazem, który nie wpływa na jego wyświetlanie.

### Wykorzystanie ExifTool
W przypadku modyfikacji plików obrazów, ExifTool może dostarczyć istotnych informacji, takich jak lokalizacja wykonania zdjęcia.

### OSINT i Weryfikacja Metadanych
W OSINT ważne jest zweryfikowanie metadanych, takich jak lokalizacja, która może być myląca. Należy bacznie zweryfikować te dane.

### Oczyszczanie Metadanych
Aby wyczyścić wszystkie metadane pliku, można użyć ExifTool z parametrem `-all=`, co sprawi, że plik nie będzie zawierał żadnych metadanych. 

### Zabezpieczenie Metadanych
W przypadku przeprowadzania śledztwa, zaleca się usunięcie metadanych oraz wykorzystanie opcji `-overwrite_original`, aby zabezpieczyć plik. 

### Rekodowanie Binarne
Można zastosować proces binarnego rekodowania, aby nadal uzyskać dane pliku, ale bez tagów. Użycie ExifTool z parametrem `-tagsFromFile @` pozwala na skopiowanie obrazu bez tagów metadanych.

## 📝 Actions
TODO: Użyj ExifTool do analizy plików obrazów w celu uzyskania metadanych.  
TODO: Zastosuj steganografię do ukrycia komunikatu w pliku obrazowym.  
TODO: Wyczyść metadane z obrazów przed ich publikacją dla bezpieczeństwa informacji.  

## 🧠 Flashcards
#flashcard Co to jest steganografia? :: Technika zabezpieczania danych w innych obiektach, np. w obrazach.  
#flashcard Jakie informacje można uzyskać z ExifTool? :: Data wykonania zdjęcia, lokalizacja, program do edycji.  
#flashcard Co robi parametr -all= w ExifTool? :: Usuwa wszystkie metadane z pliku.  
#flashcard Jak można zabezpieczyć metadane pliku? :: Używając ExifTool z parametrem -overwrite_original i -all=.  

## ExifTool i Metadane

### Wprowadzenie
ExifTool to narzędzie, które umożliwia odczyt i zapis metadanych w plikach multimedialnych. Posiada wiele funkcji pomocnych w analizie i śledztwie cyfrowym.

### Użycie ExifTool

#### Skopiowanie Obrazu
Aby skopiować obraz z zachowaniem tagów, można użyć parametru `tags from file`. Dodanie znaku `@` informuje ExifTool, że ma skopiować obraz bez dodatkowych tagów.

```bash
exiftool -tagsfromfile @ -overwrite_original -all UN3.png
```

#### Analiza Metadanych
Wynik wykonania powyższego polecenia wskazuje, że plik `UN3.png` nie zawiera żadnych tagów. Znalezione dane pochodzą jedynie z systemu plików.

### Znaczenie Metadanych
Metadane są kluczowe w kontekście śledztw, ponieważ wiele informacji można uzyskać z plików pochodzących z portali społecznościowych, takich jak Instagram czy TikTok. Wykorzystanie metadanych w śledztwie może dostarczyć istotnych dowodów.

#### Narzędzia do Wykorzystywania Metadanych
Oprócz ExifTool, dostępnych jest wiele innych narzędzi. Przykładem jest FOCA (Fingerprinting Organizations with Collected Archives).

### Instalacja FOCA

#### Pobieranie
FOCA można pobrać z oficjalnego repozytorium na GitHubie, jednak wymaga zainstalowania bazy SQL Express dla systemu Windows.

```bash
# Aby zainstalować bazę SQL Express
# 1. Pobierz instalator z oficjalnej strony Microsoftu
# 2. Zainstaluj, akceptując domyślne ustawienia
```

#### Praca z FOCA
FOCA przeprowadza analizę w dwóch krokach: 
1. Enumeracja subdomen.
2. Weryfikacja plików przy użyciu znanych dorków.

### Ustawienia i Ograniczenia
Podczas korzystania z narzędzi warto pamiętać o limitach wyszukiwarek, które mogą blokować dalsze zapytania. W przypadku Google i Binga, FOCA może wykonać więcej zapytań w porównaniu do DuckDuckGo.

## 📝 Actions
TODO: Wykonać testowe polecenie ExifTool na pliku graficznym.  
TODO: Pobierz i zainstaluj FOCA, upewniając się, że SQL Express jest zainstalowany.  
TODO: Zbadaj metadane dostępne w plikach graficznych uzyskanych z różnych źródeł.

## 📅 Calendar
TERMIN: Zbadaj metadane plików przed następnych spotkaniem, aby podzielić się wynikami.   [Synced](https://www.google.com/calendar/event?eid=Y3M3bm9tbThpZDVmOTk5bWtyc2sya25sOG8gbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jaką funkcję pełni ExifTool? :: Odczytuje i zapisuje metadane w plikach multimedialnych.  
#flashcard Jak działa proces FOCA? :: Enumeracja subdomen, następnie weryfikacja plików.  
#flashcard Co należy zainstalować, aby używać FOCA na Windowsie? :: SQL Express.

## 🌐 Narzędzia OSINT i Reverse IP

### Wprowadzenie
Narzędzia do Open Source Intelligence (OSINT) są kluczowe w analizie bezpieczeństwa. W tym kontekście szczególną uwagę należy zwrócić na techniki takie jak Reverse IP i enumeracja domen. 

### Narzędzia do OSINT
Poniżej przedstawione są narzędzia, które będą omawiane w trakcie szkolenia:

1. **The Harvester**
2. **SpiderFoot**
3. **FOCA**
4. **Ferox**
5. **Buster**
6. **Fuf**

Każde z wymienionych narzędzi ma swoje specyfikacje, predyspozycje i zastosowanie, zwłaszcza w kontekście zbierania informacji oraz analizy serwerów.

### Techniki DNS i Reverse IP
Reverse IP umożliwia identyfikację wielu domen hostowanych na tym samym adresie IP. W przypadku, gdy np. ambasada Chin dzieli ten sam adres IP z innymi domenami, technika ta może ujawnić szereg powiązań. DNS pozwala na przywiązanie wielu rekordów do jednego adresu, co zwiększa zakres badanych danych.

### OSINT i jego implikacje w bezpieczeństwie
Ważne jest zrozumienie, jakie konsekwencje dla bezpieczeństwa mogą mieć działania OSINT. Każda interakcja z serwerami (np. rozpoznanie technologii) może być rejestrowana w logach, co może ujawniać nasze działania administracji serweru.

## 📝 Actions
TODO: Wprowadzić nadzór nad bezpieczeństwem narzędzi online wykorzystywanych do analizy danych.  
TODO: Przeanalizować politykę prywatności narzędzi OSINT.  
TODO: Udokumentować wykorzystanie technik Reverse IP w kontekście analizy bezpieczeństwa.  

## 📅 Calendar
SPOTKANIE: Mega Secura Cooking Party - 20 października.   [Synced](https://www.google.com/calendar/event?eid=NmQ2MGQ3bm0za3RidTM2ZTBtNDdkYm41MmsgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest Reverse IP? :: Technika identyfikacji wielu domen hostowanych na tym samym adresie IP.  
#flashcard Jakie narzędzia do OSINT są wymienione? :: The Harvester, SpiderFoot, FOCA, Ferox, Buster, Fuf.  
#flashcard Dlaczego technika Reverse IP jest istotna? :: Umożliwia zrozumienie powiązań między różnymi domenami i potencjalnymi zagrożeniami.  

## Recon NG: Praca z Narzędziem

### Dashboard

1. Użycie komendy `dashboard` pokazuje aktualny brak aktywności w systemie, co jest normalne, gdyż nie uruchomiono jeszcze żadnych procesów.

### Wyszukiwanie Dodatków

2. Komenda `marketplace search` pozwala na przeglądanie dostępnych pluginów do Recon NG, które umożliwiają zbieranie dodatkowych informacji z. OSINT. Potencjalne informacje mogą obejmować:
   - Dane teleadresowe związane z firmą.
   - Adresy email.
   - Informacje o certyfikatach.

3. Zainstalowane moduły są oznaczone jako "zainstalowany" i mogą wymagać klucza API. Przykład: plugin z portalu Shodan wymaga rejestracji i wygenerowania klucza.

### Moduły Rozpoznawania

4. Sugerowany moduł do instalacji to `modules load Recon.Domains.Contacts`, który przechwytuje dane kontaktowe administratorów.

5. Aby ustawić parametr źródła, użyj komendy:
   ```bash
   Options Set Source apple.com
   ```

6. Komenda `Run` pozwala na szybkie zebranie danych kontaktowych, potencjalnie w kilka sekund.

### Informacje Publiczne

7. Uwaga: Zbierane dane są publicznie dostępne na stronie arin.net, co oszczędza czas.

### Zakres Danych

8. Przykładowe dane, jakie mogą być wyciągane przez Recon NG, to:
   - Domeny
   - Informacje o firmie
   - Bloki sieciowe
   - Lokalizacje
   - Datosy kontaktowe (29 zebranych)
   - Potencjalne wycieki

### Maltego: Narzędzie do OSINT

#### Licencja

9. Narzędzie Maltego wymaga wykupienia licencji, aby z niego korzystać komercyjnie. Licencja podstawowa (Basic) pozwala na ograniczone możliwości.

10. Koszt licencji profesjonalnej wynosi 6000 euro rocznie.

#### Działanie

11. Po uruchomieniu Maltego wymagane jest logowanie przez przeglądarkę. Wszelkie aktualizacje pluginów powinny być regularnie przeprowadzane.

12. W Maltego dostępne są różne transformaty, które można instalować podobnie jak pluginy w Recon NG.

### Tryb Stealth

13. Maltego ma różne tryby odpytywania, w tym tryb stealth, który ukrywa zapytania, co zwiększa prywatność w procesie wyszukiwania.

## 📝 Actions
TODO: Zainstalować moduł Recon.Domains.Contacts w narzędziu Recon NG.  
TODO: Skonfigurować parametry źródła w Recon NG dla konkretnej domeny.  
TODO: Wykupić odpowiednią licencję dla Maltego do użytku komercyjnego.  
TODO: Regularnie aktualizować pluginy w Maltego.

## 🧠 Flashcards
#flashcard Jakie informacje można zbierać za pomocą Recon NG? :: Dane teleadresowe, adresy email, informacje o certyfikatach.  
#flashcard Co jest wymagane do używania narzędzia Maltego? :: Wykupiona licencja.  
#flashcard Jakie mają zastosowanie transformaty w Maltego? :: Umożliwiają pozyskiwanie informacji z różnych źródeł przy użyciu pluginów.  
#flashcard Czym jest tryb stealth w Maltego? :: Tryb, który ukrywa zapytania do stron internetowych, zwiększając prywatność.

## Maltego i SpiderFoot - Wprowadzenie do Narzędzi OSINT

### Funkcjonalności Maltego

Maltego to zaawansowane narzędzie do analizy danych OSINT (Open Source Intelligence). Możliwości tego narzędzia obejmują:

- Odpytywanie stron internetowych w trybie normalnym oraz trybie stealth.
- Ukrywanie aktywności poprzez losowe parametry, takie jak user agent przeglądarki.

Przykład użycia:
1. Wprowadzenie domeny (np. sekurak.pl) do analizy.
2. Uruchomienie transformacji, takich jak ekstrakcja adresów e-mail.

### Monitorowanie Kredytów

Wersja darmowa Maltego umożliwia użytkownikowi korzystanie z ograniczonej liczby kredytów:
- Skonsumowane: 0
- Pozostałe: 200
- Kredyty są aktualizowane co miesiąc.

Warto pilnować limitów, aby narzędzie działało bez zakłóceń.

### Wyszukiwanie Osób

Możliwości wyszukiwania w Maltego:
- Rozpoczęcie od wysokiego poziomu (np. osoba: John Doe) i modyfikacja na Tomka Turbę.
- Próbować namierzyć adres e-mail Tomka Turby.

### Dodatkowe Funkcjonalności

- Dodawanie nowych właściwości i notatek do obiektów.
- Tworzenie powiązań między różnymi obiektami.
- Modyfikacja błędnie ocenionych obiektów.

### Wizualizacja Danych

Maltego umożliwia sortowanie danych w różnych wizualizacjach (gwiazda, siatka, struktura pływająca). Umożliwia to lepsze zrozumienie zgromadzonych informacji.

### Eksportowanie Danych

Maltego oferuje możliwość eksportu danych do różnych formatów:
- Raporty z analityką.
- Grafy i tabele.

---

### SpiderFoot - Automatyzacja Skanowania

SpiderFoot to narzędzie do automatycznego skanowania, które wykonuje wiele funkcji osintowych. Kluczowe cechy obejmują:

- Obsługuje wiele celów: domeny, adresy IP, numery telefonów, itp.
- Wymaga podstawowego klucza API do niektórych operacji.

### Uruchamianie SpiderFoot

Aby uruchomić SpiderFoot:
1. Klonowanie repozytorium z GitHub:
   ```bash
   git clone https://github.com/smicallef/spiderfoot.git
   ```
2. Instalacja wymaganych bibliotek:
   ```bash
   pip install -r requirements.txt
   ```
3. Uruchomienie narzędzia na porcie 5001:
   ```bash
   python spiderfoot.py -p 0.0.0.0:5001
   ```

### Przykłady Funkcjonalności

SpiderFoot pozwala na skanowanie:
- Nazwy domen (np. sekurak.pl)
- Imion i nazwisk (np. Tomasz Turba)
- Adresów kryptowalutowych

### Zabezpieczenia i Ryzyka

Podczas używania SpiderFoot w internecie, brakuje opcji logowania, co może prowadzić do nieautoryzowanego użycia. Użytkownicy powinni stosować skanowanie pasywne, aby nie wysyłać ruchu do celów.

---

## 📝 Actions
TODO: Monitorować kredyty w Maltego aby uniknąć przestojów.  
TODO: Przeprowadzić analizę danych przy użyciu funkcji SpiderFoot.

## 📅 Calendar
TERMIN: Regularne monitorowanie i aktualizacja raportów w Maltego co miesiąc. [Synced](https://www.google.com/calendar/event?eid=M2ZkMmNkaGp0bzd0ZmFpb2Ftc2JwZTUxajQgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest Maltego? :: Narzędzie do analizy danych OSINT.  
#flashcard Jakie są tryby działania Maltego? :: Normalny i stealth.  
#flashcard Co to jest SpiderFoot? :: Narzędzie do automatycznego skanowania OSINT.  
#flashcard Jak zainstalować SpiderFoot? :: Skorzystać z repozytorium GitHub i zainstalować wymagane biblioteki.

## Dokumentacja dotycząca tworzenia i zarządzania serwerami w chmurze

### Wprowadzenie
W niniejszym dokumencie opisano proces tworzenia i zarządzania serwerami w chmurze, ze szczególnym uwzględnieniem aspektów związanych z bezpieczeństwem oraz automatyzacją zadań.

### Tworzenie serwera w chmurze
Aby utworzyć serwer, należy skorzystać z portalu do zarządzania serwerami. Proces obejmuje następujące kroki:

1. **Logowanie do portalu** – Użytkownik loguje się do swojego konta.
2. **Wybór typu serwera** – Użytkownik określa typ serwera. Na przykład, wybiera serwer z systemem operacyjnym Linux, w tym konkretnej wersji Ubuntu (np. 22.04).
3. **Konfiguracja zasobów** – Użytkownik ustala konfigurację, w tym region (np. Niemcy), ilość pamięci RAM (np. 8 GB), procesorów (np. 4), a także przestrzeń dyskową (np. 160 GB) i transfer danych (np. 5 TB).
4. **Nazwa i hasło** – Użytkownik nadaje nazwę dla serwera i ustala hasło administratora.
5. **Dodanie kluczy** – Opcjonalne dodanie kluczy SSH dla bezpiecznego dostępu.
6. **Potwierdzenie i utworzenie serwera** – Po zakończeniu konfiguracji użytkownik klika przycisk "Utwórz".

Przykładowa komenda logowania przez SSH:
```bash
ssh user@ip_address
```

### Monitorowanie stanu serwera
Po utworzeniu serwera jego status powinien zmienić się na "ready". Monitorowanie odbywa się za pomocą odświeżania strony, co pozwala na obserwację aktualnych zasobów i stanu działania serwera.

### Integracja z narzędziami analitycznymi
Użytkownik może użyć narzędzia takiego jak SpiderFoot, aby zbierać dane dotyczące bezpieczeństwa i analizy incydentów. 

1. **Zbieranie informacji** – Uruchom skanowanie, aby zbierać dane na temat domen, adresów e-mail itp.
2. **Analiza wyników** – Po zakończeniu skanu użytkownik może przeglądać zebrane dane oraz generować wizualizacje.

### Automatyzacja zadań
Możliwość automatyzacji zadań dzięki użyciu programów takich jak Maltego, które pozwalają na stworzenie maszyn (agentów) do automatyzacji procesów śledczych.

#### Przykład tworzenia maszyny
1. **Utworzenie nowej maszyny** – Użytkownik określa cel automatyzacji (np. śledzenie figuranta).
2. **Wybór transformacji** – Wybierany jest rodzaj przetwarzanych danych, jak np. adresy IP lub adresy e-mail.
3. **Planowanie uruchomienia** – Użytkownik ustala harmonogram uruchamiania, np. co 30 sekund za pomocą opcji "timer machine".

### Aspekty compliance
Podczas korzystania z powyższych narzędzi należy być świadomym regulacji prawnych, takich jak:
- **RODO** – W kontekście przetwarzania danych osobowych.
- **DORA** – Ochrona danych w odniesieniu do infrastruktury krytycznej.
- **NIS2** – Zasady ochrony bezpieczeństwa sieci i systemów informacyjnych.

## 📝 Actions
TODO: Zalogować się do portalu i utworzyć testowy serwer.
TODO: Skonfigurować skanowanie za pomocą SpiderFoot.
TODO: Utworzyć maszynę w Maltego do monitorowania zmian na określonym adresie e-mail.

## 📅 Calendar
TERMIN: Ustalić datę przetestowania działania serwera w chmurze. [Synced](https://www.google.com/calendar/event?eid=bzkxNGxycjBoYWp1MnNpbzkxdWk3MTQ5MDQgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie są podstawowe kroki do utworzenia serwera w chmurze? :: Logowanie, wybór serwera, konfiguracja zasobów, nazwa i hasło, dodanie kluczy, utworzenie serwera.
#flashcard Jakie regulacje należy uwzględnić przy przetwarzaniu danych osobowych? :: RODO, DORA, NIS2.

## Analiza Wyszukiwania i Wykorzystania Danych

### Portale i Narzędzia
W kontekście dostępu do danych, warto zauważyć istnienie portalu [bezpiecznedanegow.pl](http://bezpiecznedanegow.pl), który wymaga logowania oraz profilu zaufanego, co ogranicza łatwość przejścia. Alternatywne źródła, takie jak forum BridgeForums, mogą być pomocne w pozyskiwaniu informacji.

### Zawartość Wycieku Danych
Sam wyciek najczęściej występuje w formie niezabezpieczonego pliku tekstowego. Zawiera on krytyczne dane osobowe, takie jak:

- Numer PESEL
- E-mail
- Imię i nazwisko
- Adres

### Wyszukiwanie Obrazem
Obecnie dominującymi narzędziami w wyszukiwaniu obrazem są Google Lens oraz Yandex Lens. Google Lens oferuje możliwość:

- Wyszukiwania na podstawie obrazów
- Zaznaczania fragmentów obrazu

### Wykorzystanie Języka Arabskiego w Obrazach
Przykłady wyszukiwania obrazów arabskich, jak wskazano, pokazują możliwości tłumaczenia tekstów bezpośrednio z obrazów, co wzmacnia funkcjonalność narzędzi.

### Wyszukiwarki i Bezpieczeństwo
W przypadku użycia wyszukiwarek, takich jak Yandex, konieczne jest zachowanie ostrożności i zabezpieczenie się przez VPN, zwłaszcza w kontekście działalności w służbach. Należy również być świadomym potencjalnych zagrożeń związanych z wyszukiwanymi danymi.

### Narzędzia do Wyszukiwania Obrazków
Wśród dostępnych narzędzi znajduje się również TinEye oraz PimEyes, które oferują funkcjonalności umożliwiające precyzyjne dopasowanie wizualne wizerunków, co jest istotne w pracy operacyjnej.

### Monitorowanie Warunków Atmosferycznych
Platformy takie jak Windy oraz dane.imgw.pl są kluczowe dla uzyskania informacji o warunkach pogodowych i meteorologicznych.

## 📝 Actions
TODO: Zbadać możliwości integracji z portalem bezpiecznedanegow.pl.  
TODO: Dokonać analizy potencjalnych źródeł wycieków danych.  
TODO: Zastosować zasadę ostrożności podczas korzystania z Yandex Lens.  
TODO: Użyć PimEyes w celach analizy wizerunków w kontekście operacyjnym.  

## 📅 Calendar
TERMIN: Sprawdzenie dostępności danych z platformy danych.imgw.pl do 2023-11-01.   [Synced](https://www.google.com/calendar/event?eid=cW8xNzZvNjM0ZWc0ZnE0Y3BubWJvbzdnb3MgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest Reverse Image Search? :: Narzędzie do wyszukiwania dopasowań obrazów.  
#flashcard Jakie dane osobowe mogą być wycieki? :: PESEL, e-mail, imię, nazwisko, adres.  
#flashcard Jak zabezpieczyć się korzystając z Yandex? :: Użyć VPN oraz sprawdzonych serwerów.  

## Analiza danych dotyczących pojazdów

### Proces analizy zdjęć
Analiza zdjęć umożliwia oceny pojazdów w kontekście istniejących danych katalogowych. Obrazy można wykorzystać do pomiarów, które potwierdzają autentyczność przedstawionych pojazdów.

#### Narzędzia do pomiarów
Do wykonywania pomiarów wykorzystuje się narzędzie PhotoMeasure, które pozwala na:
- Dokonywanie pomiarów bazowych,
- Rotację obrazów zgodnie z wymogami pomiarów.

### Poszukiwanie informacji o pojazdach
Szeroka gama portali umożliwia access do publikowanych informacji o pojazdach. Kluczowe to:
- **Historia Pojazdu** - umożliwia przeszukiwanie rejestrów.
- **Ubezpieczeniowy Fundusz Gwarancyjny** - dostęp do informacji dotyczących szkód.

#### Portal Bezpieczneautobus.gov.pl
- Wprowadzenie numeru rejestracyjnego pozwala na uzyskanie szczegółowych informacji, takich jak:
  - Status badań technicznych,
  - Aktualność polisy OC.

### Gromadzenie danych
Portale, takie jak Vindecoders oraz inne systemy, umożliwiają dostęp do informacji o właścicielach pojazdów oraz ich historii rejestracji.

---

## 📝 Actions
TODO: Przeanalizować zdjęcia pojazdów za pomocą PhotoMeasure.  
TODO: Zbadać historię pojazdów w portalu historiapojazdu.gov.pl.  
TODO: Sprawdzić status badań pojazdu na bezpieczneautobus.gov.pl.  

## 📅 Calendar
SPOTKANIE: Mega Securac Hacking Party, 21:30.   [Synced](https://www.google.com/calendar/event?eid=bW1qNWRocHI0MmVnNTRqMHV1ODIyb3Jvc28gbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie narzędzie jest wykorzystywane do pomiarów na zdjęciach? :: PhotoMeasure  
#flashcard Jakie informacje można uzyskać z portalu Bezpieczneautobus.gov.pl? :: Status badań technicznych i polisy OC.  
#flashcard Co robi portal Vindecoders? :: Umożliwia dostęp do informacji o właścicielach pojazdów.

## 📡 Analiza danych z otwartych źródeł

### Weryfikacja płatności i rejestr VAT
W kontekście przetwarzania danych, istotne jest, aby numery rachunków bankowych były weryfikowane zgodnie z białą listą podatników VAT. Każdy przelew powinien być sprawdzany, aby zapewnić, że środki będą przesyłane na właściwy numer. 

### Narzędzia OSINT
Dostępne narzędzia OSINT, takie jak platforma alleo.com, pozwalają na analizę powiązań między spółkami. Umożliwia to lepsze zrozumienie struktury działalności zależnej oraz związanych z nią ryzyk.

### Portal RAR
Portal RAR (repozytorium akt rejestrowych) dostępny na stronie rar.ms.gov.pl stanowi cenne źródło informacji o dokumentach firmowych. Użytkownik ma dostęp do:
- Dokumentów notarialnych
- Pełnomocników
- Wewnątrzfirmowych postanowień
- Protokółów niezgodności

Dostęp do bardziej wrażliwych danych wymaga autoryzacji sądowej, co wymusza przestrzeganie przepisów związanych z ochroną danych osobowych (RODO).

### Rejestry edukacyjne i nieruchomości
Zawierają one obszerną bazę informacji:
- Rejestr szkół
- Ewidencja uczelni
- Przegląd nieruchomości

W kontekście wymagania DORA, kluczowe jest zabezpieczenie tych danych, aby zminimalizować ryzyko ich udostępnienia osobom trzecim.

### Mapy i geolokalizacja
Geolokalizacja umożliwia analizę danych miejscowych. Serwis Open Street Maps oraz portale takie jak Bellingcat pomagają identyfikować i wizualizować konkretne lokalizacje na podstawie dostępnych zdjęć i opisów.

### Wydarzenia
## 📅 Calendar
TERMIN: Wprowadzenie do narzędzi OSINT i geolokalizacji – 15 listopada 2023 [Synced](https://www.google.com/calendar/event?eid=M3BkdTlmNGticDJ1OWwwaDRubDZha2l1OTggbWFyY2luLnVib2dpQG0)

## 📝 Actions
TODO: Zainstalować i przetestować narzędzia OSINT.
TODO: Przygotować raport z analizy danych dotyczących lokalizacji i powiązań.
TODO: Opracować procedury weryfikacji płatności z wykorzystaniem białej listy podatników VAT.

## 🧠 Flashcards
#flashcard Co to jest portal RAR? :: Repozytorium akt rejestrowych, źródło informacji o dokumentach firmowych.
#flashcard Co zapewnia weryfikacja białej listy podatników VAT? :: Pewność, że płatności są wysyłane na właściwe numery rachunków bankowych.
#flashcard Jakie informacje zawiera rejestr edukacyjny? :: Informacje o szkołach, uczelniach publicznych i ewidencji uczelni niepublicznych.

## 📅 Calendar
SPOTKANIE: 13 października o godzinie 19.00 [Synced](https://www.google.com/calendar/event?eid=cWlhanNtMGZrb3NzMWpjYTA2MWxlMmo0MzggbWFyY2luLnVib2dpQG0)

## 👁️ Geoinformacja i Wykorzystanie Map
Dzięki nowoczesnym technologiom możliwe jest zbieranie informacji o lokalizacjach poprzez analizę map oraz mediów społecznościowych. Umożliwia to szybką identyfikację zdarzeń, takich jak pożary czy inne sytuacje kryzysowe.

### 🗺️ Zastosowanie Map
W przypadku nagłych sytuacji, takich jak pożar chemikaliów w Wólce Kosowskiej, obecność ludzi nagrywających zdarzenie na różnych platformach społecznościowych, takich jak YouTube, Snapchat czy TikTok, służy jako potwierdzenie tego wydarzenia.

### 🌐 Portale Mapowe
Portal Geohack jest jednym z najlepszych źródeł do uzyskiwania informacji o różnych mapach. Oferuje dostęp do map globalnych oraz regionalnych, w tym zdjęć satelitarnych i informacji geograficznych.

### 🎥 Mapy z Dostępem do Kamer
Dostęp do kamer przez internet stanowi dodatkową warstwę informacji. Jednakże, takie dane powinny być traktowane ostrożnie, aby nie naruszyć prywatności osób.

## 🔍 Rekonesans Techniczny
Rekonesans techniczny związany jest z zastosowaniem sztucznej inteligencji w analizie danych. W kolejnych sekcjach zostaną przedstawione nowoczesne narzędzia oraz techniki analizy OSINT.

## 📝 Actions
TODO: Przeanalizować dostępność portalu Geohack w kontekście lokalnych informacji mapowych.  
TODO: Zidentyfikować źródła, które mogą potwierdzić informacje o pożarach za pomocą mediów społecznościowych.  
TODO: Ustalić zasady dotyczące użycia kamer w kontekście ochrony prywatności.

## 🧠 Flashcards
#flashcard Jakie portale mapowe są najlepsze do szybkiego uzyskiwania informacji? :: Geohack, Targeo, eMapi.  
#flashcard Co oferuje Geohack? :: Dostęp do różnych map oraz zdjęć satelitarnych.  
#flashcard Jakie dane mogą potwierdzać wydarzenia w lokalizacjach? :: Filmiki i posty użytkowników w mediach społecznościowych.  

## Dokumentacja Zapisów Szkoleniowych

### Temat: Śledztwa i Narzędzia OSINT

Podczas szkolenia omawiano różne aspekty związane z narzędziami OSINT oraz wyzwaniami, które stają przed analitykami podczas prowadzenia śledztw. 

#### Geospy
Jest narzędzie nazwane Geospy, które wykorzystuje sztuczną inteligencję w celu automatyzacji analizy danych geolokalizacyjnych. Zostanie ono przedstawione na najbliższym szkoleniu.

#### Wiarygodność Map Baidu
Zagadniono kwestię wiarygodności map Baidu. Pojawiły się wątpliwości dotyczące tego, na ile można polegać na tych mapach w kontekście prowadzonych badań. Ostatecznie uznano, że chociaż brak jest absolutnej pewności, należy przyjąć, że są one wiarygodne do pewnego stopnia.

#### OSINT i Dane Historyczne
Podniesiono pytania dotyczące danych historycznych, takich jak właściciele filmów publikowanych w przeszłości. Wskazano, że dostęp do takich danych, na przykład poprzez archiwum internetu, nadal mieści się w ramach OSINT.

#### Podatność Związana z Numerem VIN
Omówiono podatności związane z numerem VIN, zwłaszcza w kontekście systemu infotainment w pojazdach marki Honda. Zidentyfikowano, że numer VIN może być wykorzystywany do szyfrowania komunikacji, co wprowadza dodatkowe ryzyko.

#### Narzędzia Maltego
Poruszono temat narzędzi Maltego i strategii unikania banowania na wersji darmowej. Zauważono, że wystarczy zarejestrować się raz na wersję basic, aby mieć stały dostęp.

### Podsumowanie
Szkolenie zakończono podsumowaniem, podkreślając znaczenie omawianych tematów. Zwrócono uwagę na dostępność nagrania ze szkolenia oraz zaproszono uczestników na kolejne wydarzenia.

## 📅 Calendar
TERMIN: Wspólne szkolenie na temat Geospy - data do ustalenia. [Synced](https://www.google.com/calendar/event?eid=dmc5djc0ZWc4MTQ1YmJxcms0dDY1amFocmsgbWFyY2luLnVib2dpQG0)

## 📝 Actions
TODO: Przygotować materiały do prezentacji Geospy na następne szkolenie.  
TODO: Zbadać wiarygodność map Baidu w kontekście zastosowań OSINT.  
TODO: Przeanalizować dostęp do danych historycznych w archiwum internetu.  
TODO: Zidentyfikować inne podatności związane z numerem VIN w systemach infotainment.  
TODO: Opracować strategię korzystania z wersji darmowej Maltego, aby uniknąć blokad.  

## 🧠 Flashcards
#flashcard Co to jest Geospy? :: Narzędzie wykorzystujące AI do analizy danych geolokalizacyjnych.  
#flashcard Jaką wątpliwość podniesiono w kontekście map Baidu? :: Wiarygodność i możliwość polegania na tych mapach.  
#flashcard Jakie dane mogą zostać uznane za OSINT? :: Dane historyczne z archiwum internetu.  
#flashcard Czego dotyczy podatność z numerem VIN? :: Szyfrowania komunikacji w systemie infotainment w Hondzie.  
#flashcard Jak uniknąć banowania w Maltego? :: Rejestracja w wersji basic i regularne logowanie.

## Powiązane notatki

- [[000_MOC_Cybersec]]
- [[000_MOC_Compliance]]
- [[Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 1_transkrypcja]]
