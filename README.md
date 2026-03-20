# Project Spacing Board

A small local-first **Python** desktop utility for project design notes. It stores your board as plain JSON so you can keep the data file inside any project folder, and it can be packaged into a standalone Windows `.exe`.

## Features

- Four default columns: **Road Name**, **Category**, **Arrangement**, and **Spacing**
- Add or remove columns as your project notes evolve
- Add or remove rows for multiple design references
- Open existing JSON files and save updated JSON files anywhere on disk
- Toggle **Pin to front** to keep the window above others
- Generate support files directly into a chosen project folder
- Runs entirely locally with no backend and no Node/Electron runtime
- Packages cleanly as a Windows executable with PyInstaller

## Run locally

```bash
python app.py
```

## Package for Windows

Install the build dependency and create the executable:

```bash
python -m pip install -r requirements-build.txt
python build_windows.py
```

The packaged executable is written to:

- `release/ProjectSpacingBoard.exe`

## Build from GitHub Actions

A workflow is included at `.github/workflows/build-windows.yml`.

It:

- runs on pushes to `main`
- runs manually with **workflow_dispatch**
- installs PyInstaller
- builds the Windows `.exe`
- uploads the generated executable as an artifact

## Support files

Use **Generate Support Files** inside the app to create these in any folder:

- `<board-title>.json` with the current board data
- `project-spacing-board.README.txt` with a quick reference for the generated files

## JSON shape

```json
{
  "title": "Project Spacing Board",
  "columns": ["Road Name", "Category", "Arrangement", "Spacing"],
  "rows": [
    {
      "id": "example-row",
      "values": {
        "Road Name": "Marketing Site",
        "Category": "Desktop",
        "Arrangement": "Hero / Cards / Footer",
        "Spacing": "8 / 16 / 24 / 48"
      }
    }
  ]
}
```
