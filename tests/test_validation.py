import pytest
from pydantic import ValidationError
from wkcalc import AuthorityRule, BoundaryType, RoadInput, SideInput, calculate_wk
from wkcalc.validation import GeometryError
from wkcalc.models import CalculationRecord, ProjectDetails
from wkcalc.persistence import application_data_dir, load_record, save_record

def plain_side(): return SideInput(boundary_type=BoundaryType.KERB_AT_TRAVELLED_EDGE)

def test_kerb_distance_and_surface_are_required():
    with pytest.raises(ValidationError,match="distance to kerb"):
        SideInput(boundary_type=BoundaryType.KERB_BEYOND_EDGE_LINE)

def test_impossible_physical_width_is_rejected():
    road=RoadInput(travelled_width_m=12,left=plain_side(),right=plain_side(),kerb_to_kerb_width_m=10)
    with pytest.raises(GeometryError,match="cannot be less"):
        calculate_wk(road)

def test_authority_rule_requires_width():
    road=RoadInput(travelled_width_m=8,left=plain_side(),right=plain_side(),authority_rule=AuthorityRule.MINIMUM)
    with pytest.raises(GeometryError,match="authority width"):
        calculate_wk(road)

def test_side_maximum_cannot_exceed_three():
    with pytest.raises(ValidationError):
        RoadInput(travelled_width_m=8,left=plain_side(),right=plain_side(),maximum_side_allowance_m=3.1)

def test_calculation_record_round_trip_stays_local(tmp_path):
    road=RoadInput(travelled_width_m=8,left=plain_side(),right=plain_side())
    record=CalculationRecord(project=ProjectDetails(project="Local project"),road=road); path=tmp_path/"calculations"/"record.json"
    save_record(record,path)
    assert load_record(path)==record
    assert application_data_dir(tmp_path).parent==tmp_path
