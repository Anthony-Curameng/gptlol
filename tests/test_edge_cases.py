import pytest

from wkcalc import BoundaryType, RoadInput, SideInput, calculate_side_allowance, calculate_wk

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st


@given(st.floats(min_value=0, max_value=1_000, allow_nan=False, allow_infinity=False))
def test_side_allowance_never_exceeds_three(width):
    side = SideInput(boundary_type=BoundaryType.SEALED_EDGE, sealed_width_available=width)
    assert 0 <= calculate_side_allowance(side) <= 3


@given(
    st.floats(min_value=0.01, max_value=100, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
)
def test_increasing_unsealed_width_does_not_increase_wk(travelled, unsealed):
    road = RoadInput(
        travelled_width=travelled,
        left_side=SideInput(boundary_type=BoundaryType.UNSEALED_EDGE, sealed_width_available=unsealed),
        right_side=SideInput(boundary_type=BoundaryType.UNSEALED_EDGE),
    )
    assert calculate_wk(road).calculated_wk == travelled


@given(
    st.floats(min_value=0.01, max_value=100, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0, max_value=20, allow_nan=False, allow_infinity=False),
)
def test_wk_never_exceeds_limits(travelled, extra):
    limit = travelled + extra
    road = RoadInput(
        travelled_width=travelled,
        left_side=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),
        right_side=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),
        kerb_to_kerb_width=limit,
        total_sealed_width=limit + 1,
    )
    result = calculate_wk(road)
    assert 0 <= result.calculated_wk <= limit

