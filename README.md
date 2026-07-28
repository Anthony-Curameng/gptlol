# Wk Calculator

A local, browser-based tool for calculating carriageway **Wk** from travelled-way width, independent left/right boundary conditions, and physical width limits. The deterministic calculation engine is separate from the Streamlit interface, making its rules straightforward to test and reuse.

> **Engineering notice:** This tool records transparent calculation inputs and outcomes; it does not replace the governing standard or authority approval. Confirm the applicable rule set and units before using an output for design.

## Features

- Six-step guided workflow for road arrangement, travelled elements, independent boundaries, limits, and results.
- Simple total-width mode or detailed lane/area schedule.
- Maximum 3 m side allowances, with kerb, sealed-edge, unsealed-edge, designed-line, and authority boundary rules.
- Impossible-geometry rejection and categorised warnings.
- Responsive, printable SVG cross-section.
- JSON, CSV, and standalone HTML report downloads.
- Pure Python rule engine with example and property-based tests.

## Run locally

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e '.[test]'
streamlit run app.py
```


## Calculation rules

Each side contributes between 0 and 3 m:

| Boundary | Allowance |
| --- | --- |
| Kerb at travelled edge | 0 m |
| Kerb beyond edge line | Distance to kerb, capped at 3 m |
| Sealed edge | Available sealed width, capped at 3 m |
| Unsealed edge | 0 m |
| Designed edge line | 3 m |
| Authority-defined boundary | Supplied allowance, capped at 3 m |

The unrestricted result is the travelled width plus both side allowances. The final calculated Wk is capped by the lowest supplied kerb-to-kerb or sealed-width limit. An authority Wk is displayed separately rather than silently replacing the calculated result.

## Test

```bash
pytest
```

Tests cover matched and asymmetric roads, travelled-element inclusion, validation failures, width caps, and Hypothesis invariants.

## Project layout

```text
app.py                     Streamlit workflow
wkcalc/models.py           Pydantic input/output contracts
wkcalc/rules.py            Pure deterministic calculations
wkcalc/validation.py       Cross-field geometry checks
wkcalc/explanations.py     Plain-language rule explanations
wkcalc/diagrams.py         Dependency-free SVG rendering
wkcalc/exports.py          JSON, CSV, and HTML generation
tests/                     Explicit and property-based tests
data/authority_overrides.json  Starter authority configuration
```
