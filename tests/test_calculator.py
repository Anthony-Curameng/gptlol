import pytest

from wkcalc import AuthorityRule, BoundaryType, RoadInput, SideInput, SurfaceType, TravelledElement, calculate_side_allowance, calculate_travelled_width, calculate_wk

def test_asymmetric_kerb_and_designed_edge_are_calculated_independently():
    road=RoadInput(travelled_width_m=10,left=SideInput(boundary_type=BoundaryType.KERB_BEYOND_EDGE_LINE,distance_to_kerb_m=1.8,surface=SurfaceType.SEALED),right=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),kerb_to_kerb_width_m=14.2)
    result=calculate_wk(road)
    assert result.left.allowance_m==1.8; assert result.right.allowance_m==3; assert result.unrestricted_wk_m==14.8; assert result.final_wk_m==14.2
    assert "kerb-to-kerb width" in result.rule_path

def test_unsealed_area_does_not_add_to_wk():
    side=SideInput(boundary_type=BoundaryType.UNSEALED_BEYOND_EDGE_LINE,width_beyond_edge_m=20)
    assert calculate_side_allowance(side).allowance_m==0

def test_unsealed_surface_before_kerb_does_not_add_to_wk():
    side=SideInput(boundary_type=BoundaryType.KERB_BEYOND_EDGE_LINE,distance_to_kerb_m=2,surface=SurfaceType.UNSEALED)
    assert calculate_side_allowance(side).allowance_m==0

def test_element_based_width_includes_turn_and_bicycle_lanes():
    elements=[TravelledElement(element_type="Through",quantity=2,individual_width=3.5),TravelledElement(element_type="Turn",individual_width=3),TravelledElement(element_type="Bicycle",individual_width=1.5)]
    assert calculate_travelled_width(elements)==11.5

def test_authority_override_is_explicit_final_step():
    road=RoadInput(travelled_width_m=7,left=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),right=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),authority_rule=AuthorityRule.OVERRIDE,authority_width_m=11)
    result=calculate_wk(road)
    assert result.calculated_wk_m==13; assert result.final_wk_m==11; assert result.authority_rule==AuthorityRule.OVERRIDE

def test_unequal_lanes_receive_separate_wk_results():
    elements=[
        TravelledElement(element_type="Left through lane",individual_width=3),
        TravelledElement(element_type="Right through lane",individual_width=4),
    ]
    road=RoadInput(
        travelled_width_m=7,
        left=SideInput(boundary_type=BoundaryType.KERB_BEYOND_EDGE_LINE,distance_to_kerb_m=2,surface=SurfaceType.SEALED),
        right=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),
        total_sealed_width_m=10,
    )
    result=calculate_wk(road,elements)
    assert [lane.lane_width_m for lane in result.lanes]==[3,4]
    assert result.lanes[0].lane_wk_m==pytest.approx(4.2)
    assert result.lanes[1].lane_wk_m==pytest.approx(5.8)
    assert sum(lane.lane_wk_m for lane in result.lanes)==pytest.approx(result.calculated_wk_m)

def test_lane_schedule_must_match_travelled_width():
    road=RoadInput(travelled_width_m=7,left=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),right=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE))
    with pytest.raises(ValueError,match="lane widths must equal"):
        calculate_wk(road,[TravelledElement(element_type="Lane",individual_width=3.5)])
