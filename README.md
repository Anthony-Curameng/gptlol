# Wk Calculator

A **native Windows desktop application** for calculating carriageway Wk from travelled-way composition, independent side conditions, and physical or authority limits. It uses PySide6 widgets and starts no browser, web server, cloud service, or network listener. Calculation files and exports stay on the local machine.

> **Engineering notice:** Confirm the governing standard and authority requirements before issuing a design. The calculator exposes its rule path; it does not replace engineering review.

## Desktop workflow

The `QWizard` interface guides the user through seven pages:

1. optional project, road, section, authority, and calculation-reference details;
2. direct travelled-way width or an editable schedule of lanes and travelled areas;
3. independent left-side boundary details;
4. independent right-side boundary details;
5. kerb-to-kerb, total sealed width, maximum side allowance, and authority limits;
6. a local `QGraphicsScene` cross-section review; and
7. result, exact rule path, print, and local JSON/CSV/HTML exports.

Boundary choices include kerbs at or beyond the travelled edge, sealed or unsealed areas beyond a traffic-edge line, designed edge lines, no defined edge, and authority-defined boundaries. Conditional controls collect only relevant measurements.

## Install and run for development

Python 3.11 or newer is required. In Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python main.py
```

No localhost address is opened. Closing the desktop window exits the application.

## Local files

The application creates these folders on first export:

```text
Documents\Wk Calculator\
├── calculations\
├── exports\
└── settings.json
```

JSON calculation records are Pydantic-validated when loaded. Filenames are sanitised before use. `data/authority_rules.json` provides versioned defaults and can be extended with reviewed authority configurations. SQLite is deliberately not used until searchable history is required.

## Calculation behavior

Each side is evaluated independently and capped by the configured maximum, which cannot exceed 3 m. Unsealed or undefined areas contribute zero. The engine then:

1. adds travelled width and both side allowances;
2. caps that unrestricted Wk by the lowest applicable kerb-to-kerb or total sealed width;
3. applies an explicitly selected authority minimum or override; and
4. returns immutable `SideResult` and `WkResult` records, explanations, and the exact rule path.

The calculation and persistence layers import no PySide6 code and can be tested without the desktop interface.

## Test

```powershell
python -m pytest
```

Tests cover asymmetric roads, surface effects, lane summation, authority rules, impossible geometry, required conditional values, and Hypothesis invariants.

## Build a Windows executable

Install the build extra, then use the checked-in specification:

```powershell
python -m pip install -e ".[build]"
pyinstaller --clean wk-calculator.spec
```

The result is `dist\Wk Calculator.exe`, built with `console=False`. For a faster-starting directory package instead, use:

```powershell
pyinstaller --noconsole --onedir --name "Wk Calculator" --add-data "data\authority_rules.json;data" main.py
```

PyInstaller bundles Python and the installed PySide6 runtime. The packaged program remains a local desktop application and requires no Python installation on the target computer.

## Structure

```text
main.py                     Native process entry point
wkcalc/enums.py             Domain enumerations and display labels
wkcalc/models.py            Pydantic input and record models
wkcalc/calculator.py        Pure deterministic calculation engine
wkcalc/validation.py        Cross-field geometry validation
wkcalc/explanations.py      Result display formatting
wkcalc/persistence.py       Documents-folder JSON persistence
wkcalc/exports.py           JSON, CSV, and printable HTML reports
ui/wizard.py                Seven-page QWizard composition
ui/*_page.py                Individual desktop workflow pages
ui/cross_section.py         QGraphicsScene cross-section
wk-calculator.spec          Windows PyInstaller definition
tests/                      Explicit and property-based tests
data/authority_rules.json   Versioned local authority defaults
```
