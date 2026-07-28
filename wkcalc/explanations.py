"""Human-readable descriptions of calculation decisions."""

from .models import BoundaryType, CalculationResult, RoadInput, SideInput


def _side_explanation(label: str, side: SideInput, allowance: float) -> str:
    if side.boundary_type == BoundaryType.KERB_AT_TRAVELLED_EDGE:
        reason = "the kerb is at the travelled-way edge"
    elif side.boundary_type == BoundaryType.KERB_BEYOND_EDGE_LINE:
        reason = "the distance to the kerb"
    elif side.boundary_type == BoundaryType.SEALED_EDGE:
        reason = "the available sealed width"
    elif side.boundary_type == BoundaryType.UNSEALED_EDGE:
        reason = "unsealed area is excluded"
    elif side.boundary_type == BoundaryType.AUTHORITY_OVERRIDE:
        reason = "the authority-defined allowance"
    else:
        reason = "the maximum 3.00 m designed-edge allowance"
    return f"The {label} side used {allowance:.2f} m because {reason}."


def explain_result(road: RoadInput, result: CalculationResult) -> list[str]:
    lines = [
        _side_explanation("left", road.left_side, result.left_allowance),
        _side_explanation("right", road.right_side, result.right_allowance),
    ]
    if result.limiting_width is not None and result.calculated_wk < result.unrestricted_wk:
        if road.kerb_to_kerb_width == result.limiting_width:
            label = "kerb-to-kerb width"
        else:
            label = "total sealed width"
        lines.append(f"The resulting width was limited by the {result.limiting_width:.2f} m {label}.")
    else:
        lines.append("No supplied physical width reduced the unrestricted Wk.")
    return lines
