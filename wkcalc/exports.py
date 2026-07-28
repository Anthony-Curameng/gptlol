"""Dependency-free JSON, CSV, and printable HTML exports."""
import csv
import io
import json
from html import escape
from .calculator import WkResult
from .models import CalculationRecord

def record_to_json(record: CalculationRecord, result: WkResult | None = None) -> str:
    data = record.model_dump(mode="json")
    if result is not None:
        data["result"] = result.to_dict()
    return json.dumps(data, indent=2, ensure_ascii=False)

def result_to_csv(record: CalculationRecord, result: WkResult) -> str:
    data = {**record.project.model_dump(), **result.to_dict()}
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=data)
    writer.writeheader()
    writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list, tuple)) else value for key, value in data.items()})
    return output.getvalue()

def result_to_html(record: CalculationRecord, result: WkResult) -> str:
    rows = [("Project", record.project.project), ("Road", record.project.road_name), ("Section", record.project.section)]
    rows += [(key.replace("_", " ").title(), value) for key, value in result.to_dict().items() if key not in {"explanation", "lanes"}]
    table = "".join(f"<tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>" for key, value in rows)
    lane_rows = "".join(
        f"<tr><td>{escape(lane.name)}</td><td>{lane.lane_width_m:.2f} m</td>"
        f"<td>{lane.left_allowance_m:.2f} m</td><td>{lane.right_allowance_m:.2f} m</td>"
        f"<td>{lane.lane_wk_m:.2f} m</td><td>{lane.wk_start_m:.2f}–{lane.wk_end_m:.2f} m</td></tr>"
        for lane in result.lanes
    )
    lane_table = "" if not lane_rows else f"<h2>Per-lane physical Wk</h2><table><tr><th>Lane</th><th>Width</th><th>Left allowance</th><th>Right allowance</th><th>Lane Wk</th><th>Wk interval</th></tr>{lane_rows}</table>"
    notes = "".join(f"<li>{escape(line)}</li>" for line in result.explanation)
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Wk Calculation</title><style>body{{font:11pt Segoe UI,sans-serif;max-width:900px;margin:2rem auto}}th,td{{padding:.5rem;border-bottom:1px solid #ccc;text-align:left}}h1{{color:#17324d}}</style></head><body><h1>Wk Calculation Report</h1><table>{table}</table>{lane_table}<h2>Rule path</h2><p>{escape(result.rule_path)}</p><ul>{notes}</ul></body></html>"
