## Szkolenie "Bezpieczeństwo Front-Endu Aplikacji Webowych"

### Wprowadzenie
Ostatnie szkolenie w ramach Sekurak Akademii 25.
- Uczestnicy: Kamil Jarciński, gość i prowadzący.
- Temat: bezpieczeństwo front-endu aplikacji webowych.
  
### Plan Szkolenia
1. Zrozumienie podatności XSS (Cross-Site Scripting).
2. Omówienie skutków ataków XSS.
3. Techniki obrony przed XSS.

### Czym jest XSS?
- Luka w zabezpieczeniach pozwalająca na wstrzyknięcie kodu JavaScript, który jest wykonywany w przeglądarkach użytkowników.
- Występuje w kontekście domeny aplikacji.

### Analiza Przykładu
Aplikacja przyjmująca dane wejściowe:
- Wprowadzane imię pogrubione poprzez kod HTML.
- Wykorzystanie narzędzi deweloperskich do analizy osadzania danych.

#### Identyfikacja Potencjalnych Ataków
1. Zlokalizowanie miejsca w kodzie HTML, gdzie dane są osadzane.
2. Analiza kontekstu (SYNC), w którym te dane zostaną wstrzyknięte.
3. Ustalanie potencjalnych payloadów (ataku) w zależności od kontekstu.

### Testy Wstrzykiwania
- Przykład wstrzyknięcia HTML: pierwsza próba osadzenia tagu HTML, co potwierdziło podatność na HTML Injection.
- Próba wstrzyknięcia tagu `<script>` z założeniem, że wykona się w kontekście przeglądarki. W różnych aplikacjach, kod JavaScript między tagami `<script>` nie wykonuje się, ponieważ osadzany jest w kontekście nieaktywnego skryptowania.

### Problemy Wykonania
- Tag `<script>` osadzony, lecz nie wykonał się z powodu specyficznego zachowania metody `innerHTML` w JavaScript.
  
### Wnioski
Zidentyfikowanie podatności XSS wymaga:
- Analiza treningowa w środowisku przeglądarki.
- Znalezienie potencjalnych mechanizmów obronnych w aplikacji.

### 📝 Actions
TODO: Przeanalizować implementacje zabezpieczeń dla podatności XSS.  
TODO: Przygotować dokumentację o zastosowaniu odpowiednich technik obronnych.  
  
### 📅 Calendar
TERMIN: Kiedy odbywa się kolejne szkolenie z zakresu bezpieczeństwa aplikacji?  

## 🧠 Flashcards
#flashcard Czym jest XSS? :: Luka w zabezpieczeniach, która pozwala na wstrzyknięcie kodu JavaScript.  
#flashcard Jakie są skutki ataków XSS? :: Możliwość przejęcia sesji użytkownika, kradzież danych.  
#flashcard Jakie są metody obrony przed XSS? :: Walidacja inputów, użycie szablonów, konteksty danych.

## XSS Injection Techniques

### Overview
Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts into content from otherwise trusted web applications. This document discusses various techniques of XSS injection and browser behaviors that can affect their execution.

### Browser Behavior and XSS
1. **XSS Execution Contexts**: 
    - XSS can behave differently depending on whether it's executed through a browser or a testing tool like Burp Suite (BERTAP).
    - Browsers apply mechanisms such as URL encoding that may prevent certain payloads from executing correctly.

2. **Variation Across Browsers**: 
    - Different browsers may handle XSS payloads differently. 
    - A payload that works in Firefox may not work in Chrome or vice versa due to variations in their rendering engines and security policies.

### Injection Methods
#### Using `<img>` Tag
- The `<img>` tag can be used for crafting XSS payloads by exploiting the `onerror` event.

```html
<img src="non-existent-image" onerror="alert('XSS executed');">
```

- This will trigger the alert if the image fails to load.

#### Script Tags in HTML
- If data resides between HTML tags, direct script injection is possible. For instance:

```html
<script>alert('XSS');</script>
```

#### Attribute-Based XSS
1. **Escaping Attributes**: When XSS data is injected into an HTML attribute, it may be necessary to escape out of the attribute context.
  
```html
<div title="string'"><script>alert('XSS')</script></div>
```

- The injected quote may lead to an execution context switch.

2. **Polyglots**: Creating a polyglot payload can help bypass restrictions across multiple contexts.

```html
<img src="invalid" onerror="alert(1);"><div title='test" <script>alert(2)</script>'>
```

### CSS and HTML Manipulations
- CSS manipulations can also trigger events to ensure the JavaScript executes when expected.

```html
<div style="background-color:red;" onmouseover="alert(3);">Hover me!</div>
```

### JavaScript String Injection
- Injecting within JavaScript strings can pose challenges, especially concerning string termination.

```javascript
let str = "Some data"; // Closing quote can be triggered
// By injecting a closing quote and then a new script tag
str = "Some data"; <script>alert('XSS');</script>
```

### Dealing with Escaping
- Be aware that some applications escape certain characters (e.g., backslashes).
- Explore if the escape character itself is escaped; if not, it may allow for injection.

```javascript
let safeData = "Data with escape \\"; // Would be escaped
```

### Summary
Multiple techniques can be employed to exploit XSS vulnerabilities based on how the input is rendered and the security measures taken by the browser or application developers. Understanding the context and behavior of the browser is crucial in successfully executing XSS attacks.

## 📝 Actions
TODO: Document variations of XSS payloads and test against different browsers.
TODO: Create examples of polyglot payloads for XSS demonstrations.
TODO: Explore and list possible defenses against XSS vulnerabilities.

## 🧠 Flashcards
#flashcard What is XSS? :: A vulnerability that allows attackers to inject malicious scripts into trusted web applications.
#flashcard What does the `onerror` event do in an `<img>` tag? :: It executes JavaScript when the image fails to load.
#flashcard What is a polyglot payload? :: A payload that works across multiple contexts to evade XSS filtering.
#flashcard How can CSS be used in XSS? :: CSS can trigger events that execute JavaScript when styling is applied.

## XSS - Techniki Wstrzykiwania JavaScript

### Wprowadzenie
XSS (Cross-Site Scripting) to technika ataku, która umożliwia wstrzykiwanie złośliwego kodu JavaScript do aplikacji webowych. Znajomość sposobów wstrzykiwania kodu oraz zależności od kontekstu, w którym dane są osadzane, jest kluczowa dla przeprowadzenia efektywnego ataku.

### Mechanizm Ataku
Atak XSS opiera się na umiejscowieniu złośliwego skryptu pomiędzy znacznikami `<script>`. W sytuacji, gdy przeglądarka interpretuje kod, może to prowadzić do różnych działań, takich jak wywołanie alertów czy modyfikowanie DOM.

### Payloady i Ograniczenia
Nie istnieje uniwersalny payload, który działałby wszędzie. Zwykle różne ograniczenia w aplikacjach mogą uniemożliwiać jego skuteczność. Efektywne wstrzykiwanie kodu często wymaga zrozumienia kontekstu aplikacji oraz specyfiki kodowania danych.

### Techniki Ominięcia Ochrony
1. **Komentarze Liniowe**: Wstrzyknięcie `//` w kodzie JavaScript, aby zignorować błędy składniowe.
2. **Protokół JavaScript**: Użycie atrybutu href z prefiksem `javascript:` umożliwia wykonanie skryptu po kliknięciu linku.

### Zabezpieczenia w Kodzie JavaScript
Przy osadzaniu danych w aplikacji, istotne jest odpowiednie kodowanie:
- Użycie kodowania Unicode lub hex dla znaków specjalnych.
- Zakodowanie atrybutów, które mogą prowadzić do wykonania złośliwego kodu.

### Analiza Wkładu
Podczas analizy ataków XSS, poprzez inspekcję źródła strony, można znaleźć miejsca, gdzie dane są osadzane. Należy zwracać uwagę na sposób kodowania i rejestrowania tych danych.

## 📝 Actions
TODO: Zbadać możliwości osadzenia payloadów w różnych kontekstach aplikacji.
TODO: Przeanalizować dokumentację przeglądarek dotycząca zachowania skryptów JavaScript.
TODO: Przygotować i przetestować różne payloady z XSS Cheatsheet.

## 📅 Calendar
SPOTKANIE: Przeprowadzenie warsztatów na temat ochrony przed XSS w dniu 2023-11-15. [Synced](https://www.google.com/calendar/event?eid=MWpkbjM1Z2hkM2ttbHBpb3J1Y2Nhb2wxYTQgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co oznacza XSS? :: Cross-Site Scripting
#flashcard Jakie są techniki wstrzykiwania XSS? :: Komentarze liniowe, protokół JavaScript
#flashcard Co to jest payload? :: Kod wstrzykiwany w ataku XSS
#flashcard Jak ją opisać w kontekście bezpieczeństwa? :: Wymaga znania kontekstu i zabiegów programistycznych w aplikacji.

## Analiza Ataku XSS na WordPress

### Wprowadzenie
Ten dokument omawia techniki ataku typu Cross-Site Scripting (XSS) przy użyciu WordPressa jako przykładu, koncentrując się na możliwościach, jakie stwarza nieodpowiednie przetwarzanie danych przez aplikację. 

### Architektura Ataku
Atak rozpoczyna się od przesłania przez atakującego linka zawierającego payload, który zostaje wykonany w przeglądarce administratora. Kluczowe aspekty obejmują:

- **Same Origin Policy**: Przeglądarka blokuje dostęp do danych z innych domen przez kod JavaScript, co jednak można obejść odpowiednio skonstruowanym payloadem.
  
- **Dowiedzenie się o Twojej ofierze**: Atakujący określa podatności systemu (np. pluginy), aby wstrzyknąć kod.

### Mechanizm Działania
1. **Przesłanie linku**: Atakujący publikuj komentarz z linkiem do payloadu na stronie, co jest sposobem na dotarcie do administratora.
   
2. **Wykonanie Payloadu**: Po kliknięciu w link i wczytaniu strony, kod JavaScript zostaje wykonany. W tym etapie możliwe jest:
   - Zarejestrowanie nowego użytkownika.
   - Odczytanie tokena CSRF oraz innych poufnych danych.

3. **Kod JavaScript**: Payload zawiera mechanizm, który wywołuje funkcję odpowiedzialną za dodanie nowego użytkownika za pomocą żądania HTTP POST. 

### Przykład Kodowania Payloadu
```javascript
const payload = '<img src=x onerror="alert(document.cookie)">';
```
- **iframe**: Tworzenie iframe z zasobem, który umożliwia osadzenie kodu JavaScript w kontekście strony ofiary.

### Problemy Związane z Mieszaną Treścią
W przypadku korzystania z HTTP w połączeniu z HTTPS, przeglądarka blokuje niezaufane zasoby. Dlatego ważne, aby atakujący wykorzystywał właściwy protokół. 

### Wnioski
- Atak XSS może być przeprowadzony poprzez kliknięcie w niezaufany link lub zasób.
- Istotna jest analiza struktury wtyczek i możliwości, jakie one dają.
- Użycie odpowiednich metod może skutkować kradzieżą danych, w tym tokenów CSRF.

## 📝 Actions
TODO: Przeanalizować istniejący system zabezpieczeń pod kątem podatności XSS.  
TODO: Wprowadzić zabezpieczenia przeciw XSS w formularzach WordPressa.  
TODO: Umożliwić monitorowanie podejrzanej aktywności admina.

## 📅 Calendar
TERMIN: Zorganizować szkolenie dla zespołu na temat ochrony przed atakami XSS.   [Synced](https://www.google.com/calendar/event?eid=ODVjajRlZnRtcmd0MDNqM2h2dTE1MXZ0MW8gbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Jakie są zasady działania Same Origin Policy? :: Cod JavaScript nie ma dostępu do danych z innych domen.  
#flashcard Co pozwala na wstrzyknięcie kodu JavaScript w kontekście ofiary? :: Wykorzystanie iframe lub nieodpowiednio zabezpieczonych parametrów.  
#flashcard Jakie są skutki xss dla admina WordPressa? :: Możliwość przejęcia konta, kradzieży danych sesji.  

## XSS i jego skutki

Cross-Site Scripting (XSS) to jedna z najpopularniejszych podatności w aplikacjach webowych, która umożliwia atakującemu wykonywanie złośliwego kodu JavaScript w kontekście przeglądarki ofiary. Zastosowane techniki exploitacji XSS różnią się w zależności od konkretnego scenariusza.

### Skutki XSS

XSS może prowadzić do wielu poważnych konsekwencji:
- Odczyt danych: Atakujący może uzyskać dostęp do informacji, które są dostępne dla ofiary, takich jak ciasteczka sesyjne.
- Wykonanie akcji: Atakujący może przeprowadzać akcje w imieniu ofiary, takie jak rejestracja nowych użytkowników.
- Wstrzykiwanie żądań: Dzięki XSS atakujący może wydawać polecenia do wewnętrznej sieci, atakując inne usługi w LANie ofiary.
- Złośliwe oprogramowanie: Możliwość wykorzystania przestarzałych przeglądarek do przejęcia kontroli nad systemem operacyjnym.

### Odpowiedzi na pytania o XSS

1. W przypadku otwarcia złośliwego kodu HTML w aplikacjach desktopowych, takich jak Outlook, zagrożenie jest mniejsze, ponieważ brakuje odpowiedniego silnika JavaScript. Natomiast wersje przeglądarkowe są narażone na ataki XSS.
2. Odnosząc się do trybu prywatnego przeglądarki, atak XSS nie zadziała, jeśli ofiara nie posiada odpowiednich ciasteczek sesyjnych.
3. WAFy mogą być obejdżone przy użyciu znaków takich jak `%0C`, jednak skuteczność wymaga analizy konkretnego rozwiązania.

## Dobre praktyki zabezpieczeń przed XSS

### Sanityzacja danych

Sanityzacja to kluczowy proces, który pomaga eliminować potencjalnie niebezpieczne dane wejściowe. Należy stosować odpowiednie techniki sanityzacji w zależności od kontekstu, w jakim dane są używane.

### Enkodowanie danych

Odpowiednie enkodowanie danych jest niezbędne, aby zabezpieczyć aplikacje przed XSS:
- W kontekście HTML: Należy stosować encję dla znaków takich jak `&`, `<`, `>`, `'`, `"` w zależności od ich kontekstu.
- W kontekście JavaScript: Należy używać `JSON.stringify()` i pamiętać o kodowaniu specjalnych znaków.

### Ograniczanie dostępu do danych

Należy unikać przekazywania danych pochodzących od użytkownika do zdarzeń JavaScriptowych (np. `onError`, `onMouseOver`) oraz do metod manipulujących DOM-em, takich jak `document.write`.

### Używanie frameworków

Frameworki i silniki szablonów, takie jak React, mogą znacznie podnieść poziom bezpieczeństwa. Zaleca się korzystanie z mechanizmów takich jak `dangerouslySetInnerHTML` z rozwagą, aby nie wyłączyć zabezpieczeń.

## 📝 Actions
TODO: Przeprowadzić audyt aplikacji pod kątem podatności XSS.  
TODO: Implementować encodowanie danych w odpowiednich kontekstach.  
TODO: Opracować protokoły sanityzacji danych wejściowych.  

## 🧠 Flashcards
#flashcard Co to jest XSS? :: Cross-Site Scripting, podatność umożliwiająca wykonywanie złośliwego kodu w przeglądarkach.  
#flashcard Jakie są skutki ataku XSS? :: Odczyt danych, wykonanie akcji w imieniu ofiary, wstrzykiwanie żądań do LAN.  
#flashcard Co to jest sanityzacja? :: Proces usuwania potencjalnie niebezpiecznych danych pochodzących od użytkowników.  
#flashcard Jakich metod unikać w kontekście XSS? :: `eval`, `setTimeout`, `setInterval` dla danych pochodzących od użytkowników.

## Techniki ataków XSS w kontekście Reacta

### Renderowanie Markdown na HTML
Markdown może być przetwarzany na HTML za pomocą bibliotek, które konwertują tekst w formacie Markdown na odpowiedni HTML. Użycie `dangerouslySetInnerHTML` w React umożliwia wstrzyknięcie HTML do DOM, jednak wiąże się z ryzykiem wystąpienia ataku XSS, jeśli źródło danych nie jest odpowiednio zabezpieczone.

### Przykład ataku XSS
Gdy użytkownik ma możliwość zmiany zawartości w Markdown, może to prowadzić do wstrzyknięcia złośliwego kodu JavaScript:

```javascript
const markdownContent = "[Kliknij tutaj](javascript:alert('XSS'))";
const htmlContent = marked(markdownContent); // Zmienna htmlContent zawiera wstrzyknięty kod
```

### Problemy z sanitizacją
Starsze wersje Reacta mogły mieć luki bezpieczeństwa, umożliwiające ataki XSS przez osadzanie niesanitarnych linków. W takich przypadkach silnik Reacta mógł nie zabezpieczać nawet przed niepoprawnie zakodowanym linkiem (np. wstrzyknięcie: `javascript:alert('XSS')`).

### Custom Prompts i manipulation
Użytkownicy mogą mieć dostęp do parametrów obiektów, co prowadzi do sytuacji, gdzie mogą wstrzykiwać złośliwe skrypty poprzez odpowiednie atrybuty HTML, np.:

```javascript
const props = {
  test: "<img src=x onerror=alert('XSS') />"
};
```

### Praca z iFrame
Przypisanie niebezpiecznego kodu do atrybutów `src` w tagu `iFrame` może umożliwić atak XSS, więc nie należy pozwalać na osadzanie niezaufanych danych w takim kontekście.

### Protokół Data
Protokół `data:` może być użyty do osadzenia złośliwego kodu, co również prowadzi do ataków XSS:

```html
<iframe src="data:text/html,<script>alert('XSS')</script>"></iframe>
```

## 📝 Actions
TODO: Zidentyfikować miejsca w kodzie, gdzie użyto `dangerouslySetInnerHTML` i wprowadzić odpowiednie zabezpieczenia.
TODO: Sprawdzić wszystkie powiązane komponenty, które dopuszczają wstrzyknięcia przez propsy.

## 📅 Calendar
SPOTKANIE: Omówienie bezpieczeństwa w aplikacjach React - 15.11.2023  [Synced](https://www.google.com/calendar/event?eid=Z3Z1OWkzdDl1cDQ3aTg4cnByaXNjOTZsdDQgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Czym jest `dangerouslySetInnerHTML`? :: Metodą Reacta, która pozwala na osadzenie HTML bez sanitizacji.
#flashcard Jak można wykonać atak XSS w React? :: Przez wstrzyknięcie złośliwego skryptu w `innerHTML` lub przez niesanitizowane propsy.

## Bezpieczeństwo w aplikacjach webowych

### Wprowadzenie do SafeHatML
SafeHatML to silnik stworzony przez Google, bazujący na pakiecie Go. Jego głównym celem jest ochrona przed atakami XSS oraz eliminacja typowych błędów programistycznych, jak np. przypisywanie danych użytkownika do atrybutu `src` tagu `script`, co może prowadzić do poważnych luk w zabezpieczeniach. SafeHatML blokuje taką kompilację, co sprawia, że jest to polecane rozwiązanie w kontekście bezpieczeństwa aplikacji.

### Typy ataków XSS
Należy pamiętać, że istnieją różne klasy ataków XSS, w tym:
- **Down-based XSS** - ataki, które zależą od błędów w kodzie JavaScript. Żaden silnik szablonów nie jest w stanie ochronić przed tego typu atakami.

### Technologie związane z zabezpieczeniami
Wprowadzenie mechanizmów SAST (Static Application Security Testing) i DAST (Dynamic Application Security Testing) jest kluczowe dla zapewnienia wysokiej jakości kodu. Szkolenie programistów w zakresie bezpiecznego kodowania oraz regularne skanowanie aplikacji pozwala na wczesne wykrywanie potencjalnych luk w zabezpieczeniach.

### Zastosowanie dodatków przeglądarkowych
Choć istnieją różne wtyczki do przeglądarek, które mogą pomóc w identyfikacji podatności, takie jak RetireJS, ich stosowanie powinno być ograniczone do minimum. Zachowanie minimalizmu w dodatkach przeglądarkowych zmniejsza ryzyko ataków związanych z zainfekowanymi wtyczkami.

### Aktualizacje i zarządzanie wersjami
Zarządzanie wersjami bibliotek JavaScript jest kluczowe. Należy dostosowywać aplikacje do najnowszych wydań, aby uniknąć znanych podatności. Wykorzystanie aktualizowanych paczek zmniejsza ryzyko wystąpienia problemów związanych z przestarzałym oprogramowaniem.

## 📝 Actions
- TODO: Wdrożyć SafeHatML w bieżących projektach.
- TODO: Szkolenie programistów w zakresie SAST i DAST.
- TODO: Ograniczyć użycie dodatków przeglądarkowych do minimum.
- TODO: Regularnie aktualizować biblioteki JavaScript w projekcie.

## 📅 Calendar
- SPOTKANIE: 21 stycznia - rozpoczęcie semestru Akademii 26. [Synced](https://www.google.com/calendar/event?eid=OGg5aHF1ZDBkc2dqcWQ2amdnZmVnZmYzYzAgbWFyY2luLnVib2dpQG0)
- TERMIN: Jutro, 19:00 - szkolenie o narzędziach AI. [Synced](https://www.google.com/calendar/event?eid=ZHIyMjRwN3RqMnRlZHBmMWZpb3BuYmRqMmMgbWFyY2luLnVib2dpQG0)

## 🧠 Flashcards
#flashcard Co to jest SafeHatML? :: Silnik stworzony przez Google do ochrony przed atakami XSS.
#flashcard Jakie są główne typy ataków XSS? :: Down-based XSS i inne formy XSS.
#flashcard Jakie techniki należy stosować do zapewnienia bezpieczeństwa kodu? :: SAST, DAST i szkolenia programistów.
#flashcard Dlaczego warto korzystać z aktualizowanych bibliotek? :: Aby uniknąć znanych podatności i problemów związanych z przestarzałym oprogramowaniem.