"""Formatting helpers for desktop result displays and reports."""
from .calculator import WkResult

def result_summary(result: WkResult) -> list[tuple[str, str]]:
    rows = [
        ("Travelled-way width", f"{result.travelled_width_m:.2f} m"),
        ("Left-side allowance", f"{result.left.allowance_m:.2f} m"),
        ("Right-side allowance", f"{result.right.allowance_m:.2f} m"),
        ("Unrestricted Wk", f"{result.unrestricted_wk_m:.2f} m"),
    ]
    if result.physical_limit_m is not None:
        rows.append(("Physical width limit", f"{result.physical_limit_m:.2f} m"))
    rows.append(("Final Wk", f"{result.final_wk_m:.2f} m"))
    return rows
