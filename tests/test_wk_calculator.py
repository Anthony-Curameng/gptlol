import pytest
from wkcalc import *
from wkcalc.validation import AuthorityGeometryConflict, InputValidationError

def boundary(distance=0,surface=SurfaceType.SEALED,outer=OuterBoundaryType.KERB): return SideBoundaryInput(edge_reference=EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE,outer_boundary=outer,surface_beyond_edge=surface,distance_from_outer_edge_m=distance)
def road(width=7,left=None,right=None,**kw): return RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.SIMPLE,simple_internal_width_m=width,left_boundary=left or boundary(0),right_boundary=right or boundary(0),**kw)

def test_full_kerb_to_kerb(): assert calculate_wk(road(8,full_kerb_to_kerb_is_travelled=True,kerb_to_kerb_width_m=8,left_boundary=None,right_boundary=None)).final_wk_m==8
def test_two_metres_each_side(): assert calculate_wk(road(left=boundary(2),right=boundary(2))).final_wk_m==11
def test_five_metres_each_side_caps_at_three(): assert calculate_wk(road(left=boundary(5),right=boundary(5))).final_wk_m==13
def test_mixed_edges(): assert calculate_wk(road(left=boundary(1.5),right=boundary(2.5,outer=OuterBoundaryType.EDGE_OF_SEAL))).final_wk_m==11
def test_one_sealed_one_unsealed(): assert calculate_wk(road(left=boundary(2),right=boundary(9,SurfaceType.UNSEALED))).final_wk_m==9

def test_painted_separation_and_turn_lane_are_included():
    segments=(CrossSectionSegment(segment_type=SegmentType.THROUGH_LANE,label="Eastbound",width_m=3.5),CrossSectionSegment(segment_type=SegmentType.INTERNAL_PAINTED_SEPARATION,label="Painted centre separation",width_m=1.2),CrossSectionSegment(segment_type=SegmentType.TURN_LANE,label="Turn lane",width_m=3),CrossSectionSegment(segment_type=SegmentType.THROUGH_LANE,label="Westbound",width_m=3.5))
    item=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.DETAILED,segments=segments,left_boundary=boundary(),right_boundary=boundary())
    result=calculate_wk(item); assert result.internal_width_m==11.2; assert any("included" in line for line in result.rule_trace)

@pytest.mark.parametrize("kind",[SegmentType.PARKING_LANE,SegmentType.BICYCLE_LANE])
def test_parking_and_bicycle_lanes_are_included(kind):
    segment=CrossSectionSegment(segment_type=kind,label=kind.value,width_m=2)
    item=RoadInput(arrangement=RoadArrangement.SINGLE_CARRIAGEWAY,width_mode=WidthInputMode.DETAILED,segments=(segment,),left_boundary=boundary(),right_boundary=boundary())
    assert calculate_wk(item).internal_width_m==2

def test_designed_outer_edge_is_accepted_with_warning():
    designed=SideBoundaryInput(edge_reference=EdgeReferenceType.DESIGNED_OUTER_TRAFFIC_EDGE_LINE,outer_boundary=OuterBoundaryType.EDGE_OF_SEAL,surface_beyond_edge=SurfaceType.SEALED,distance_from_outer_edge_m=2)
    result=calculate_wk(road(left=designed));assert result.left_allowance_m==2;assert any("designed" in warning for warning in result.warnings)

def test_authority_side_allowance_over_three_is_not_silently_clamped():
    directed=SideBoundaryInput(edge_reference=EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE,outer_boundary=OuterBoundaryType.AUTHORITY_DEFINED,surface_beyond_edge=SurfaceType.SEALED,distance_from_outer_edge_m=0,authority_allowance_m=4)
    result=calculate_wk(road(left=directed));assert result.left_allowance_m==4;assert any("exceeds" in warning for warning in result.warnings)

def test_authority_override_and_minimum():
    reference=dict(authority_name="Authority",authority_reference="Document 1")
    assert calculate_wk(road(left=boundary(2),right=boundary(2),authority_rule=AuthorityRule.FINAL_OVERRIDE,authority_width_m=10,**reference)).final_wk_m==10
    assert calculate_wk(road(left=boundary(5),right=boundary(5),authority_rule=AuthorityRule.MINIMUM,authority_width_m=15,**reference)).final_wk_m==15

def test_authority_cannot_exceed_available_seal():
    with pytest.raises(AuthorityGeometryConflict): calculate_wk(road(authority_rule=AuthorityRule.MINIMUM,authority_width_m=20,authority_name="A",authority_reference="R"))
