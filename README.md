# Project Spacing Board

A small local-first desktop utility for project design notes. It stores your board as plain JSON so you can keep the data file inside any project folder.

## Features

- Four default columns: **Road Name**, **Category**, **Arrangement**, and **Spacing**
- Add or remove columns as your project notes evolve
- Add or remove rows for multiple design references
- Open existing JSON files and save updated JSON files anywhere on disk
- Toggle **Pin to front** to keep the window above others using Electron's always-on-top support
- Runs entirely locally with no backend

## Getting started

```bash
npm install
npm start
```

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
