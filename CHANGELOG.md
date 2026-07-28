# Changelog

## 1.0.0 — 2026-07-28

- Consolidated the prototype into one `src/wkcalc` package, one enum module, one validated road model, and one Wk result model.
- Added the offline seven-step PySide6 wizard, ordered segment editor, model-driven cross-section diagram, authority validation, autosave recovery, and local exports.
- Explicitly included internal painted separation within Wk, distinguished outer traffic-edge lines, excluded physical medians and unsealed external areas, and removed per-lane Wk allocation.
- Added JSON, CSV, native PDF, `.wkcalc.json` persistence, Windows development/build scripts, and core/property/GUI tests.
