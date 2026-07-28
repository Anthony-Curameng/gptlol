from hypothesis import given, strategies as st
from wkcalc import EdgeReferenceType, OuterBoundaryType, SideBoundaryInput, SurfaceType, calculate_side_allowance

def side(distance=0, surface=SurfaceType.SEALED, boundary=OuterBoundaryType.KERB, edge=EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE):
    return SideBoundaryInput(edge_reference=edge,outer_boundary=boundary,surface_beyond_edge=surface,distance_from_outer_edge_m=distance)

def test_kerb_at_travelled_edge_is_zero(): assert calculate_side_allowance(side(edge=EdgeReferenceType.KERB_IS_OUTER_TRAVELLED_EDGE)).allowance_m==0

def test_sealed_distance_is_capped_at_three(): assert calculate_side_allowance(side(5)).allowance_m==3

def test_unsealed_width_is_excluded(): assert calculate_side_allowance(side(100,SurfaceType.UNSEALED)).allowance_m==0

@given(st.floats(min_value=0,max_value=1000,allow_nan=False,allow_infinity=False))
def test_standard_allowance_is_bounded(distance): assert 0 <= calculate_side_allowance(side(distance)).allowance_m <= 3
