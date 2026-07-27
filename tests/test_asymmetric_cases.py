from wkcalc import BoundaryType, RoadInput, SideInput, calculate_wk


def test_kerb_left_unsealed_right():
    road = RoadInput(
        travelled_width=8,
        left_side=SideInput(boundary_type=BoundaryType.KERB_BEYOND_EDGE_LINE, distance_to_kerb=1.5),
        right_side=SideInput(boundary_type=BoundaryType.UNSEALED_EDGE, sealed_width_available=99),
    )
    result = calculate_wk(road)
    assert result.left_allowance == 1.5
    assert result.right_allowance == 0
    assert result.calculated_wk == 9.5
    assert result.rule_applied.startswith("Asymmetric")


def test_authority_value_is_reported_but_not_silently_substituted():
    road = RoadInput(
        travelled_width=8,
        left_side=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),
        right_side=SideInput(boundary_type=BoundaryType.DESIGNED_EDGE_LINE),
        authority_wk=11,
    )
    result = calculate_wk(road)
    assert result.calculated_wk == 14
    assert result.authority_wk == 11
    assert "authority review required" in result.warnings[0]

