"""Dependency-free result exports."""

import csv
import io
import json
from html import escape

from .models import CalculationResult


def result_to_json(result: CalculationResult) -> str:
    return json.dumps(result.model_dump(mode="json"), indent=2)


def result_to_csv(result: CalculationResult) -> str:
    output = io.StringIO()
    data = result.model_dump(mode="json")
    writer = csv.DictWriter(output, fieldnames=data.keys())
    writer.writeheader()
    writer.writerow({key: json.dumps(value) if isinstance(value, list) else value for key, value in data.items()})
    return output.getvalue()


def result_to_html(result: CalculationResult, title: str = "Wk Calculation Report") -> str:
    rows = "".join(
        f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td>{escape(str(value))}</td></tr>"
        for key, value in result.model_dump(mode="json").items()
    )
    return f"<!doctype html><html><head><title>{escape(title)}</title><style>body{{font-family:sans-serif;max-width:800px;margin:auto}}th,td{{padding:.5rem;border-bottom:1px solid #ddd;text-align:left}}</style></head><body><h1>{escape(title)}</h1><table>{rows}</table></body></html>"
