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

## Konfiguracja

Podczas dodawania integracji podajesz:

- `dashboard` - identyfikator dashboardu, np. `default`, `salon`, `tablet`.
- `source` - `static`, `api` albo `unsplash`.
- `static_path` - sciezka do pliku w konfiguracji HA, np. `www/backgrounds/default.jpg`.
- `api_url` - URL endpointu zwracajacego obraz.
- `refresh_minutes` - interwal odswiezania dla zrodla `api`.

### Unsplash

Dla zrodla `unsplash` wymagany jest `unsplash_access_key` z aplikacji utworzonej w Unsplash Developers.
Opcjonalnie mozna ustawic:

- `unsplash_query` - temat zdjec, np. `forest`, `architecture`, `mountains`.
- `unsplash_orientation` - `landscape`, `portrait` albo `squarish`.
- `unsplash_content_filter` - `low` albo `high`.
- `unsplash_width` i `unsplash_height` - rozmiar obrazu.
- `unsplash_quality` - jakosc kompresji.

Wazne: Unsplash wymaga uzywania URL-i obrazow zwracanych przez API. Dlatego dla tego providera integracja zapisuje w encji URL do CDN Unsplash, zamiast kopiowac zdjecie do `/local`.

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
Dla zrodla `unsplash` usluga pobierze nowe losowe zdjecie z konfiguracji Unsplash.

```yaml
service: dihor_background.refresh
data:
  dashboard: salon
  url: https://example.com/background.jpg
```

## Uzycie w dashboardzie

Po odswiezeniu tlo jest dostepne jako statyczny plik Home Assistant:

```text
/local/dihor_backgrounds/salon.jpg
```

Ten URL mozna wykorzystac w motywie, card-mod, custom CSS albo przyszlym komponencie frontendowym.

Dla zrodla `unsplash` aktualny URL obrazu znajduje sie bezposrednio w stanie encji:

```text
dihor_background.salon
```

Encja zawiera tez atrybuty z identyfikatorem zdjecia i autorem.

## Development

Podstawowa walidacja skladni:

```bash
python -m py_compile custom_components/dihor_background/*.py
```
