"""Pure deterministic Wk calculation rules."""

from collections.abc import Iterable

from .models import BoundaryType, CalculationResult, RoadInput, SideInput, TravelledElement
from .validation import validate_road, validate_side

MAX_SIDE_ALLOWANCE = 3.0


def calculate_side_allowance(side: SideInput) -> float:
    validate_side(side)
    if side.boundary_type in {BoundaryType.KERB_AT_TRAVELLED_EDGE, BoundaryType.UNSEALED_EDGE}:
        return 0.0
    if side.boundary_type == BoundaryType.KERB_BEYOND_EDGE_LINE:
        return min(side.distance_to_kerb or 0.0, MAX_SIDE_ALLOWANCE)
    if side.boundary_type == BoundaryType.SEALED_EDGE:
        return min(side.sealed_width_available or 0.0, MAX_SIDE_ALLOWANCE)
    if side.boundary_type == BoundaryType.AUTHORITY_OVERRIDE:
        return min(side.authority_allowance or 0.0, MAX_SIDE_ALLOWANCE)
    return MAX_SIDE_ALLOWANCE


def calculate_travelled_width(elements: Iterable[TravelledElement]) -> float:
    return sum(element.total_width for element in elements)


def calculate_wk(road: RoadInput) -> CalculationResult:
    validate_road(road)
    left = calculate_side_allowance(road.left_side)
    right = calculate_side_allowance(road.right_side)
    unrestricted = road.travelled_width + left + right
    limits = [width for width in (road.kerb_to_kerb_width, road.total_sealed_width) if width is not None]
    limiting_width = min(limits) if limits else None
    calculated = min(unrestricted, limiting_width) if limiting_width is not None else unrestricted

    warnings: list[str] = []
    if road.authority_wk is not None:
        warnings.append("[authority review required] An authority-defined Wk is supplied; confirm which value governs.")
    if road.sealed_areas_are_travelled:
        warnings.append("[unusual but permitted geometry] Sealed areas are marked as intended travelled way.")

    boundary_names = {road.left_side.boundary_type.value, road.right_side.boundary_type.value}
    rule = "Asymmetric boundary allowances" if len(boundary_names) > 1 else "Matched boundary allowances"
    if limiting_width is not None and limiting_width < unrestricted:
        rule += ", limited by available width"

    return CalculationResult(
        travelled_width=road.travelled_width,
        left_allowance=left,
        right_allowance=right,
        unrestricted_wk=unrestricted,
        limiting_width=limiting_width,
        calculated_wk=calculated,
        rule_applied=rule,
        warnings=warnings,
        authority_wk=road.authority_wk,
    )
