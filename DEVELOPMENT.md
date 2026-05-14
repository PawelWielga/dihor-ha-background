# Development

Notatki techniczne dla osob rozwijajacych integracje `dihor-ha-background`.

## Struktura projektu

- `custom_components/dihor_background/manifest.json` - manifest integracji Home Assistant.
- `custom_components/dihor_background/__init__.py` - setup integracji, uslugi i odswiezanie tla.
- `custom_components/dihor_background/config_flow.py` - konfiguracja przez UI.
- `custom_components/dihor_background/const.py` - stale.
- `custom_components/dihor_background/services.yaml` - opisy uslug Home Assistant.
- `hacs.json` - konfiguracja HACS.
- `.github/workflows/validate.yml` - walidacja HACS i Hassfest.

## Walidacja lokalna

Po zmianach w Pythonie uruchom:

```bash
python -m py_compile custom_components/dihor_background/*.py
```

W PowerShell wildcard nie zawsze jest przekazywany do Pythona. Wtedy uzyj:

```powershell
python -m py_compile (Get-ChildItem custom_components/dihor_background -Filter *.py | ForEach-Object { $_.FullName })
```

Jesli zmiana dotyczy tylko dokumentacji, wystarczy sprawdzenie diffa.
