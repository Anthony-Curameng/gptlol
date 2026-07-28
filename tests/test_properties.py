import pytest
from hypothesis import given,strategies as st
from wkcalc import *
from wkcalc.exports import export_json
finite=st.floats(min_value=0,max_value=100,allow_nan=False,allow_infinity=False)
def side(distance,surface=SurfaceType.SEALED):return SideBoundaryInput(edge_reference=EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE,outer_boundary=OuterBoundaryType.EDGE_OF_SEAL,surface_beyond_edge=surface,distance_from_outer_edge_m=distance)
def road(left,right,segments=()):return RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.DETAILED if segments else WidthInputMode.SIMPLE,simple_internal_width_m=None if segments else 7,segments=segments,left_boundary=left,right_boundary=right)
@given(finite)
def test_unsealed_width_never_increases_wk(width):assert calculate_wk(road(side(width,SurfaceType.UNSEALED),side(0))).final_wk_m==7
@given(st.floats(min_value=0,max_value=3,allow_nan=False,allow_infinity=False),st.floats(min_value=0,max_value=3,allow_nan=False,allow_infinity=False))
def test_increasing_sealed_width_cannot_reduce_wk(a,b):assert calculate_wk(road(side(max(a,b)),side(0))).final_wk_m>=calculate_wk(road(side(min(a,b)),side(0))).final_wk_m
@given(st.floats(min_value=.01,max_value=10,allow_nan=False,allow_infinity=False))
def test_painted_segment_adds_exact_width(width):
    base=(CrossSectionSegment(segment_type=SegmentType.THROUGH_LANE,label="Lane",width_m=3),); painted=base+(CrossSectionSegment(segment_type=SegmentType.INTERNAL_PAINTED_SEPARATION,label="Painted",width_m=width),)
    assert calculate_wk(road(side(0),side(0),painted)).internal_width_m-calculate_wk(road(side(0),side(0),base)).internal_width_m==pytest.approx(width)
@given(st.floats(min_value=.1,max_value=20,allow_nan=False,allow_infinity=False))
def test_json_round_trip_preserves_values(width):
    item=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=width,full_kerb_to_kerb_is_travelled=True,kerb_to_kerb_width_m=width); record=CalculationRecord(road_input=item,result=calculate_wk(item)); assert CalculationRecord.model_validate_json(export_json(record))==record
