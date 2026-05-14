# AGENTS.md

Podstawowe zasady pracy agentow w repozytorium `dihor-ha-background`.

## Kontekst projektu

- Projekt: `dihor-ha-background`.
- Cel: custom integration dla Home Assistant instalowana przez HACS.
- Funkcja: zarzadzanie tlami dashboardow przez statyczny plik albo API z odswiezaniem.
- Glowny katalog integracji: `custom_components/dihor_background`.
- Manifest HACS: `hacs.json`.

## Zasady pracy

- Komunikacja z uzytkownikiem: polski.
- Wprowadzaj male, czytelne zmiany.
- Nie cofaj zmian uzytkownika bez wyraznej zgody.
- Nie zakladaj, ze to Supervisor add-on. To integracja HACS.
- Pliki publiczne zapisuj pod `www/dihor_backgrounds`, zeby byly dostepne jako `/local/dihor_backgrounds/...`.
- Przy zmianie konfiguracji, uslug albo zachowania aktualizuj `README.md`.
- Przy dodaniu/zmianie uslug aktualizuj `custom_components/dihor_background/services.yaml`.

## Struktura

- `custom_components/dihor_background/manifest.json` - manifest integracji HA.
- `custom_components/dihor_background/__init__.py` - setup, uslugi i odswiezanie.
- `custom_components/dihor_background/config_flow.py` - konfiguracja przez UI.
- `custom_components/dihor_background/const.py` - stale.
- `custom_components/dihor_background/services.yaml` - opisy uslug.
- `hacs.json` - konfiguracja HACS.
- `.github/workflows/validate.yml` - walidacja HACS i Hassfest.

## Weryfikacja

Po zmianach w Pythonie uruchom:

```bash
python -m py_compile custom_components/dihor_background/*.py
```

Jesli zmiana dotyczy tylko dokumentacji, wystarczy sprawdzenie diffa.
