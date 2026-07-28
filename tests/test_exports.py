import csv,io,json
from wkcalc import *
from wkcalc.exports import export_csv, export_json, report_html

def record():
    road=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=8,full_kerb_to_kerb_is_travelled=True,kerb_to_kerb_width_m=8,project_name="Example")
    return CalculationRecord(road_input=road,result=calculate_wk(road))
def test_json_contains_complete_record():
    data=json.loads(export_json(record())); assert data["schema_version"]==1; assert data["road_input"]["project_name"]=="Example"; assert data["result"]["rule_trace"]
def test_csv_is_flat_schedule(): assert csv.DictReader(io.StringIO(export_csv(record()))).__next__()["final_wk_m"]=="8.0"
def test_html_is_printable_and_escaped(): assert "Wk Calculation Report" in report_html(record())
