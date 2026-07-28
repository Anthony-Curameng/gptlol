from hypothesis import given, strategies as st
from wkcalc import BoundaryType, RoadInput, SideInput, calculate_side_allowance, calculate_wk

finite=st.floats(min_value=.01,max_value=1000,allow_nan=False,allow_infinity=False)
@given(finite)
def test_side_allowance_is_bounded(width):
    side=SideInput(boundary_type=BoundaryType.SEALED_BEYOND_EDGE_LINE,width_beyond_edge_m=width)
    assert 0 <= calculate_side_allowance(side).allowance_m <= 3

@given(finite,st.floats(min_value=0,max_value=1000,allow_nan=False,allow_infinity=False))
def test_unsealed_width_never_changes_wk(travelled,unsealed):
    road=RoadInput(travelled_width_m=travelled,left=SideInput(boundary_type=BoundaryType.UNSEALED_BEYOND_EDGE_LINE,width_beyond_edge_m=unsealed),right=SideInput(boundary_type=BoundaryType.NO_EDGE_LINE_OR_KERB))
    assert calculate_wk(road).final_wk_m==travelled

@given(finite,st.floats(min_value=0,max_value=50,allow_nan=False,allow_infinity=False))
def test_physical_limit_is_never_exceeded(travelled,extra):
    limit=travelled+extra
    road=RoadInput(travelled_width_m=travelled,left=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),right=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),total_sealed_width_m=limit)
    assert calculate_wk(road).calculated_wk_m <= limit
