import pytest
from pydantic import ValidationError

from wkcalc import BoundaryType, RoadInput, SideInput, calculate_side_allowance, calculate_wk
from wkcalc.validation import GeometryError


def test_boundary_specific_distance_is_required():
    with pytest.raises(GeometryError, match="incomplete input"):
        calculate_side_allowance(SideInput(boundary_type=BoundaryType.KERB_BEYOND_EDGE_LINE))


def test_impossible_kerb_geometry_is_rejected():
    road = RoadInput(
        travelled_width=12,
        left_side=SideInput(boundary_type=BoundaryType.KERB_AT_TRAVELLED_EDGE),
        right_side=SideInput(boundary_type=BoundaryType.KERB_AT_TRAVELLED_EDGE),
        kerb_to_kerb_width=10,
    )
    with pytest.raises(GeometryError, match="cannot be less"):
        calculate_wk(road)


def test_negative_input_is_rejected_by_pydantic():
    with pytest.raises(ValidationError):
        SideInput(boundary_type=BoundaryType.SEALED_EDGE, sealed_width_available=-1)


def test_unsealed_width_is_not_added():
    side = SideInput(boundary_type=BoundaryType.UNSEALED_EDGE, sealed_width_available=50)
    assert calculate_side_allowance(side) == 0

