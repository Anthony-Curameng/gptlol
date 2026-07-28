"""Versioned local persistence and autosave lifecycle."""
from datetime import datetime, timezone
import json
from pathlib import Path
from .models import CalculationRecord

def application_data_dir(base: Path | None = None) -> Path:
    if base is None:
        from PySide6.QtCore import QStandardPaths
        application_path = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
        root = application_path.parent / "WkCalculator"
    else:
        root = base / "ROBRUS" / "WkCalculator" if base.name != "WkCalculator" else base
    (root / "logs").mkdir(parents=True, exist_ok=True)
    settings = root / "settings.json"
    if not settings.exists(): settings.write_text("{}\n",encoding="utf-8")
    return root

def default_exports_dir(base: Path | None = None) -> Path:
    if base is None:
        from PySide6.QtCore import QStandardPaths
        base = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))
    folder=base/"Wk Calculator"/"Exports"; folder.mkdir(parents=True,exist_ok=True); return folder

def last_used_folder(default: Path, base: Path | None = None) -> Path:
    settings_path = application_data_dir(base) / "settings.json"
    try:
        value = json.loads(settings_path.read_text(encoding="utf-8")).get("last_used_folder")
    except (OSError, json.JSONDecodeError):
        value = None
    return Path(value) if value else default

def remember_last_folder(folder: Path, base: Path | None = None) -> None:
    settings_path = application_data_dir(base) / "settings.json"
    settings_path.write_text(json.dumps({"last_used_folder": str(folder)}, indent=2) + "\n", encoding="utf-8")

def save_record(record: CalculationRecord,path: Path) -> CalculationRecord:
    updated=record.model_copy(update={"modified_at":datetime.now(timezone.utc)})
    path.parent.mkdir(parents=True,exist_ok=True); temporary=path.with_suffix(path.suffix+".tmp"); temporary.write_text(updated.model_dump_json(indent=2),encoding="utf-8"); temporary.replace(path); return updated

def load_record(path: Path) -> CalculationRecord: return CalculationRecord.model_validate_json(path.read_text(encoding="utf-8"))
def autosave_path(base: Path | None=None) -> Path: return application_data_dir(base)/"autosave.json"
def write_autosave(record: CalculationRecord,base: Path | None=None) -> CalculationRecord: return save_record(record,autosave_path(base))
def recover_autosave(base: Path | None=None) -> CalculationRecord | None:
    path=autosave_path(base); return load_record(path) if path.exists() else None
def clear_autosave(base: Path | None=None) -> None: autosave_path(base).unlink(missing_ok=True)
