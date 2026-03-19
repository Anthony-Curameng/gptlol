# Project Spacing Board

A small local-first desktop utility for project design notes. It stores your board as plain JSON so you can keep the data file inside any project folder.

## Features

- Four default columns: **Road Name**, **Category**, **Arrangement**, and **Spacing**
- Add or remove columns as your project notes evolve
- Add or remove rows for multiple design references
- Open existing JSON files and save updated JSON files anywhere on disk
- Toggle **Pin to front** to keep the window above others using Electron's always-on-top support
- Runs entirely locally with no backend
- Can be packaged for Windows as both an installer and a portable `.exe`

## Getting started

```bash
npm install
npm start
```

## Package for Windows

This repo is now configured with `electron-builder` for Windows packaging.

### Build locally on Windows

```bash
npm install
npm run dist:win
```

Build artifacts are written to the `release/` folder:

- `Project Spacing Board-<version>-x64.exe` for the NSIS installer
- `Project Spacing Board-<version>-x64-portable.exe` for the portable build

### Build from GitHub Actions

A workflow is included at `.github/workflows/build-windows.yml`.

It can:

- run on pushes to `main`
- run manually with **workflow_dispatch**
- upload the generated Windows installer and portable executable as build artifacts

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
