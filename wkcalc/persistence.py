"""Local-only calculation persistence under the user's Documents directory."""
import json
import re
from pathlib import Path
from .models import CalculationRecord

APP_FOLDER = "Wk Calculator"

def application_data_dir(documents: Path | None = None) -> Path:
    root = documents or (Path.home() / "Documents")
    folder = root / APP_FOLDER
    for child in (folder, folder / "calculations", folder / "exports"):
        child.mkdir(parents=True, exist_ok=True)
    settings = folder / "settings.json"
    if not settings.exists():
        settings.write_text("{}\n", encoding="utf-8")
    return folder

def safe_filename(value: str, fallback: str = "wk-calculation") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    return cleaned or fallback

def save_record(record: CalculationRecord, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.model_dump_json(indent=2), encoding="utf-8")

def load_record(path: Path) -> CalculationRecord:
    return CalculationRecord.model_validate_json(path.read_text(encoding="utf-8"))

def load_authority_rules(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
