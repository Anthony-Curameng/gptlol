from wkcalc import BoundaryType, RoadInput, SideInput, TravelledElement, calculate_travelled_width, calculate_wk


def side(boundary: BoundaryType, **values: float) -> SideInput:
    return SideInput(boundary_type=boundary, **values)


def test_kerbed_road_is_limited_by_kerbs():
    road = RoadInput(
        travelled_width=10,
        left_side=side(BoundaryType.KERB_BEYOND_EDGE_LINE, distance_to_kerb=2),
        right_side=side(BoundaryType.KERB_BEYOND_EDGE_LINE, distance_to_kerb=2),
        kerb_to_kerb_width=13,
    )
    result = calculate_wk(road)
    assert result.unrestricted_wk == 14
    assert result.calculated_wk == 13


def test_three_metre_allowance_each_side():
    road = RoadInput(
        travelled_width=7,
        left_side=side(BoundaryType.DESIGNED_EDGE_LINE),
        right_side=side(BoundaryType.DESIGNED_EDGE_LINE),
    )
    assert calculate_wk(road).calculated_wk == 13


def test_turn_lane_is_included_in_travelled_width():
    elements = [
        TravelledElement(element_type="Through lane", quantity=2, individual_width=3.5),
        TravelledElement(element_type="Turn lane", individual_width=3.2),
        TravelledElement(element_type="Parking", individual_width=2.2, included=False),
    ]
    assert calculate_travelled_width(elements) == 10.2

