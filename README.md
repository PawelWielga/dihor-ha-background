# Dihor HA Background

Custom integration for Home Assistant installed through HACS.

Integracja ma ulatwic podmiane tel dla dashboardow Home Assistant. Dziala po stronie Home Assistant, dlatego moze:

- skopiowac wskazany statyczny plik do katalogu `www/dihor_backgrounds`,
- pobrac obraz z zewnetrznego API,
- pobrac losowe zdjecie z Unsplash API,
- odswiezac obraz cyklicznie,
- wystawic publiczny URL w formacie `/local/dihor_backgrounds/<dashboard>.jpg`,
- zapisac aktualny URL w encji stanu `dihor_background.<dashboard>`.

## Instalacja przez HACS

1. Dodaj to repozytorium w HACS jako custom repository.
2. Wybierz kategorie `Integration`.
3. Zainstaluj `dihor-ha-background`.
4. Zrestartuj Home Assistant.
5. Dodaj integracje z poziomu `Settings -> Devices & services`.

Jesli po instalacji integracja nie pojawia sie w wyszukiwarce `Devices & services`, upewnij sie, ze masz wersje `v0.1.2` albo nowsza. Wczesniejsza paczka release miala niepoprawna strukture ZIP dla HACS.
Jesli integracja pojawia sie, ale formularz konfiguracji zwraca blad 500, zaktualizuj do `v0.1.4` albo nowszej.

## Konfiguracja

Podczas dodawania integracji podajesz:

- `dashboard` - identyfikator dashboardu, np. `default`, `salon`, `tablet`.
- `source` - `static`, `api` albo `unsplash`.

Po wyborze zrodla integracja pokazuje tylko pola potrzebne dla danego typu tla:

- `static_path` - dla `static`, sciezka do pliku w konfiguracji HA, np. `www/backgrounds/default.jpg`.
- `api_url` - dla `api`, URL endpointu zwracajacego obraz.
- `refresh_minutes` - dla `api` i `unsplash`, interwal odswiezania w minutach.

### Edycja konfiguracji

Po dodaniu integracji mozesz zmienic zrodlo tla, URL API, sciezke pliku statycznego, ustawienia Unsplash i interwal odswiezania z poziomu wpisu integracji:

1. Wejdz w `Settings -> Devices & services`.
2. Otworz `Dihor Dashboard Background`.
3. Przy wybranym wpisie kliknij `Configure`.

Po zapisaniu opcji integracja przeladowuje wpis i od razu uzywa nowych ustawien. Identyfikator `dashboard` pozostaje staly dla danego wpisu.

### Unsplash

Dla zrodla `unsplash` wymagany jest `unsplash_access_key` z aplikacji utworzonej w Unsplash Developers.
Opcjonalnie mozna ustawic:

- `unsplash_query` - temat zdjec, np. `forest`, `architecture`, `mountains`.
- `unsplash_orientation` - `landscape`, `portrait` albo `squarish`.
- `unsplash_content_filter` - `low` albo `high`.
- `unsplash_width` i `unsplash_height` - rozmiar obrazu.
- `unsplash_quality` - jakosc kompresji.

Dla zrodla `unsplash` integracja pobiera losowe zdjecie, zapisuje je lokalnie w `www/dihor_backgrounds` i ustawia encje na staly URL `/local/dihor_backgrounds/<dashboard>.jpg`. Oryginalny URL obrazu z Unsplash jest dostepny w atrybucie `image_url`.

## Uslugi

### `dihor_background.set_static`

Kopiuje statyczny plik do publicznego katalogu integracji.

```yaml
service: dihor_background.set_static
data:
  dashboard: salon
  static_path: www/backgrounds/salon.jpg
```

Wynikowy URL:

```text
/local/dihor_backgrounds/salon.jpg
```

### `dihor_background.refresh`

Pobiera tlo z API. Jesli nie podasz `url`, integracja uzyje URL zapisanego w konfiguracji dashboardu.
Dla zrodla `unsplash` usluga pobierze nowe losowe zdjecie z konfiguracji Unsplash i zapisze je pod stalym lokalnym adresem.

```yaml
service: dihor_background.refresh
data:
  dashboard: salon
  url: https://example.com/background.jpg
```

## Reczne odswiezanie

Dla kazdego wpisu integracji tworzona jest encja przycisku. W selektorze encji
Home Assistant przycisk ma nazwe z dashboardem, np. `Refresh background: salon`.

```text
button.dihor_background_<dashboard>_refresh_background
```

Przyklad dla dashboardu `salon`:

```yaml
type: button
entity: button.dihor_background_salon_refresh_background
name: Nowe tlo
icon: mdi:image-refresh
```

Mozesz tez podpiac bezposrednio usluge pod dowolny przycisk Lovelace:

```yaml
type: button
name: Nowe tlo
icon: mdi:image-refresh
tap_action:
  action: call-service
  service: dihor_background.refresh
  data:
    dashboard: salon
```

## Uzycie w dashboardzie

Po odswiezeniu tlo jest dostepne jako statyczny plik Home Assistant:

```text
/local/dihor_backgrounds/salon.jpg
```

Ten URL trzeba jednorazowo ustawic jako tlo widoku Lovelace. Integracja odswieza plik pod tym samym adresem, dlatego pozniej nie trzeba zmieniac konfiguracji dashboardu przy kazdej zmianie obrazu.

Przyklad dla widoku `salon`:

```yaml
background:
  image: /local/dihor_backgrounds/salon.jpg
  opacity: 100
  size: cover
  alignment: center
  repeat: no-repeat
  attachment: fixed
```

Dla dashboardu o sciezce `/lovelace/debug` i konfiguracji `dashboard: debug` uzyj:

```yaml
background:
  image: /local/dihor_backgrounds/debug.jpg
  opacity: 100
  size: cover
  alignment: center
  repeat: no-repeat
  attachment: fixed
```

Ten URL mozna tez wykorzystac w motywie, card-mod, custom CSS albo przyszlym komponencie frontendowym.

Dla zrodla `unsplash` uzyj tego samego lokalnego URL-a:

```text
/local/dihor_backgrounds/salon.jpg
```

Encja `dihor_background.salon` wskazuje ten lokalny URL i zawiera atrybuty z identyfikatorem zdjecia, autorem, linkiem do Unsplash oraz oryginalnym `image_url`.
