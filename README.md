# Wk Calculator

Wk Calculator is a native, offline Windows desktop application for determining carriageway lighting design width, **Wk**. It uses PySide6 and Pydantic. It opens no browser or local server, contains no telemetry or network calls, and stores calculations only on the local computer.

> Engineering review remains required. The application makes each decision visible through a structured rule trace and never treats internal lane markings as outer traffic-edge lines.

## Critical interpretation

- **Internal painted separation — included within Wk.** Painted centre lines, flush painted medians, painted islands and chevrons lying between the outer traffic edges remain in the internal span.
- **Outer traffic-edge line — not a centre line or lane-divider line.** Only the outermost marked or designed traffic-edge lines define the internal edge-to-edge span.
- A physical median or kerbed island creates divided carriageways. Calculate one carriageway at a time and exclude the physical median.
- Through, turn, parking and bicycle lanes, painted internal separation, and other internal sealed areas are included.
- External sealed width is evaluated independently on each side and is limited to the applicable distance or 3.00 m. Unsealed external width contributes zero.
- A fully travelled kerb-to-kerb road uses that complete width directly and does not request unnecessary edge offsets.
- The calculator produces one Wk for the carriageway. It deliberately does **not** allocate separate Wk values to individual lanes.

## Install for development

Python 3.11, 3.12 or 3.13 is required.

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e ".[dev]"
run-dev.bat
```

The source uses a standard `src` layout. The calculation engine imports no PySide6 code and can be exercised independently.

## Wizard

1. **Road arrangement** — select single, divided-one-side, or mixed/asymmetric and identify any physical median.
2. **Internal cross-section** — use a simple total, full kerb-to-kerb mode, or ordered detailed segments. Template widths remain blank until confirmed.
3. **Left outer boundary** — identify the actual outer travelled edge, surface, physical boundary and distance.
4. **Right outer boundary** — configure independently or deliberately use **Copy left-side settings**.
5. **Authority direction** — disabled by default; an enabled direction requires authority, reference, and width.
6. **Review geometry** — inspect the model-driven diagram and applicable interpretation checklist.
7. **Result** — review arithmetic, rule trace and warnings; save or export PDF, JSON and CSV.

Every page includes a fixed **What does this mean?** panel. Required dimensions start at a visibly incomplete zero state. Next remains unavailable until the page is valid. Starting again or closing with unsaved work requires confirmation.

## Common workflows

### Normal kerbed road

1. Select Single carriageway.
2. Confirm there is no physical median.
3. Select full kerb-to-kerb mode where all sealed width is travelled.
4. Enter kerb-to-kerb width.
5. Review and calculate.

### Painted centre separation

1. Select Single carriageway.
2. Use Detailed cross-section.
3. Add eastbound lane.
4. Add Internal painted separation.
5. Add westbound lane.
6. Define the outer traffic-edge lines.
7. Confirm the painted separation is highlighted as included.
8. Calculate.

### One kerb only

1. Select Mixed/asymmetric.
2. Enter the internal outer-edge-to-outer-edge span.
3. Configure the kerbed side.
4. Configure the unkerbed side separately.
5. Review both side allowances.
6. Calculate.

### Divided road

1. Select One carriageway of a divided road.
2. Enter only the lanes and internal areas belonging to that carriageway.
3. Treat the median kerb as the boundary on the median side.
4. Configure the outer roadside independently.
5. Calculate the opposite carriageway separately where required.

## Local files and recovery

Calculations are saved through a normal Save dialog as `*.wkcalc.json`. The last folder is remembered in the local `settings.json`. Default reports go to `Documents\Wk Calculator\Exports`. Application paths are resolved with `QStandardPaths` under `%LOCALAPPDATA%\ROBRUS\WkCalculator`, containing `settings.json`, `autosave.json`, and `logs\`. A valid calculation is autosaved at review and recovery is offered after abnormal shutdown.

JSON includes the complete input, result, rule trace, schema version, application version and timestamps. CSV is a flat schedule row. PDF is generated natively with PySide6 and includes the diagram and report; no browser or ReportLab is used.

## Test

```bat
py -m pytest
py -m ruff check src tests
py -m mypy src/wkcalc
```

Tests cover the specified core cases, painted/internal segments, mixed boundaries, authority conflicts, validation, persistence, exports, properties, and GUI startup.

## Build for Windows

```bat
py -m pip install -e ".[dev,build]"
build.bat
```

`build.bat` runs all tests before PyInstaller. The checked-in specification creates the recommended onedir distribution:

```text
dist\Wk Calculator\Wk Calculator.exe
```

The packaged application runs without Python installed and functions with the network disconnected.
