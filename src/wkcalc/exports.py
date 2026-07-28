"""Complete JSON, flat schedule CSV, HTML, and native Qt PDF exports."""
import csv, io
from html import escape
from pathlib import Path
from .models import CalculationRecord

def export_json(record: CalculationRecord) -> str: return record.model_dump_json(indent=2)
def export_csv(record: CalculationRecord) -> str:
    road,result=record.road_input,record.result
    row={"schema_version":record.schema_version,"application_version":record.application_version,"created_at":record.created_at.isoformat(),"project_name":road.project_name,"road_name":road.road_name,"section_reference":road.section_reference,"arrangement":road.arrangement.value,"internal_width_m":result.internal_width_m,"left_allowance_m":result.left_allowance_m,"right_allowance_m":result.right_allowance_m,"unrestricted_wk_m":result.unrestricted_wk_m,"physical_wk_m":result.physical_wk_m,"authority_rule":road.authority_rule.value,"authority_width_m":road.authority_width_m,"final_wk_m":result.final_wk_m,"warnings":" | ".join(result.warnings),"rule_trace":" | ".join(result.rule_trace)}
    output=io.StringIO(newline=""); writer=csv.DictWriter(output,fieldnames=row); writer.writeheader(); writer.writerow(row); return output.getvalue()
def report_html(record: CalculationRecord) -> str:
    road,result=record.road_input,record.result
    segments="".join(f"<tr><td>{escape(s.label)}</td><td>{escape(s.segment_type.value)}</td><td>{s.quantity}</td><td>{s.individual_width_m:.2f}</td><td>{s.total_width_m:.2f}</td></tr>" for s in result.included_segments) or "<tr><td colspan='5'>Simple width mode</td></tr>"
    values=(("Internal width",result.internal_width_m),("Left allowance",result.left_allowance_m),("Right allowance",result.right_allowance_m),("Unrestricted Wk",result.unrestricted_wk_m),("Physical Wk",result.physical_wk_m),("Final Wk",result.final_wk_m))
    calculations="".join(f"<tr><th>{label}</th><td>{value:.2f} m</td></tr>" for label,value in values); trace="".join(f"<li>{escape(line)}</li>" for line in result.rule_trace); warnings="".join(f"<li>{escape(line)}</li>" for line in result.warnings) or "<li>None</li>"
    return f"<!doctype html><html><head><meta charset='utf-8'><style>body{{font:10pt 'Segoe UI';color:#17212b}}table{{border-collapse:collapse;width:100%}}th,td{{padding:6px;border-bottom:1px solid #bbb;text-align:left}}h1,h2{{color:#17324d}}</style></head><body><h1>Wk Calculation Report</h1><p><b>Project:</b> {escape(road.project_name)}<br><b>Road:</b> {escape(road.road_name)}<br><b>Section:</b> {escape(road.section_reference)}<br><b>Created:</b> {record.created_at.isoformat()}<br><b>Application:</b> {record.application_version}</p><h2>Entered cross-section</h2><table><tr><th>Segment</th><th>Type</th><th>Qty</th><th>Width (m)</th><th>Total (m)</th></tr>{segments}</table><h2>Calculated values</h2><table>{calculations}</table><h2>Authority</h2><p>{escape(road.authority_name)} — {escape(road.authority_reference)}</p><h2>Rule trace</h2><ol>{trace}</ol><h2>Warnings</h2><ul>{warnings}</ul></body></html>"
def export_pdf(record: CalculationRecord,path: Path,diagram=None) -> None:
    from PySide6.QtCore import QMarginsF
    from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument
    writer=QPdfWriter(str(path)); writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4)); writer.setPageMargins(QMarginsF(15,15,15,15),QPageLayout.Unit.Millimeter)
    if diagram is None:
        document=QTextDocument(); document.setHtml(report_html(record)); document.print_(writer); return
    from PySide6.QtGui import QPainter
    from PySide6.QtCore import QRectF,Qt
    painter=QPainter(writer); page=writer.pageLayout().paintRectPixels(writer.resolution()); pixmap=diagram.grab().scaled(page.width(),int(page.height()*.42),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation); painter.drawPixmap(0,0,pixmap); painter.drawText(QRectF(0,pixmap.height()+20,page.width(),100),"Cross-section diagram — entered dimensions govern."); writer.newPage(); document=QTextDocument(); document.setHtml(report_html(record)); document.setPageSize(page.size()); document.drawContents(painter,QRectF(page)); painter.end()
