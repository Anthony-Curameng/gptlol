import pytest
from pydantic import ValidationError
from wkcalc import *
from wkcalc.validation import InputValidationError,validate_road_input

def boundary():return SideBoundaryInput(edge_reference=EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE,outer_boundary=OuterBoundaryType.KERB,surface_beyond_edge=SurfaceType.SEALED,distance_from_outer_edge_m=0)
def test_missing_boundary_distance_is_rejected():
    with pytest.raises(ValidationError):SideBoundaryInput(edge_reference=EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE,outer_boundary=OuterBoundaryType.KERB,surface_beyond_edge=SurfaceType.SEALED)
def test_physical_total_less_than_internal_is_rejected():
    road=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=10,kerb_to_kerb_width_m=9,left_boundary=boundary(),right_boundary=boundary())
    with pytest.raises(InputValidationError,match="cannot be less"):validate_road_input(road)
def test_physical_median_forces_divided_mode():
    road=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=8,left_boundary=boundary(),right_boundary=boundary(),physical_median_present=True)
    with pytest.raises(InputValidationError,match="physical median"):validate_road_input(road)
def test_authority_reference_is_required():
    road=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=8,left_boundary=boundary(),right_boundary=boundary(),authority_rule=AuthorityRule.MINIMUM,authority_width_m=9)
    with pytest.raises(InputValidationError,match="reference"):validate_road_input(road)
def test_physical_median_is_not_a_segment_type():assert "physical_median" not in {item.value for item in SegmentType}
def test_centre_line_is_not_an_edge_reference():assert "centre" not in " ".join(item.value for item in EdgeReferenceType)
