"""Pure deterministic calculation layer; contains no GUI dependencies."""
from dataclasses import asdict, dataclass
from collections.abc import Iterable
from .enums import AuthorityRule, BoundaryType, SurfaceType
from .models import RoadInput, SideInput, TravelledElement
from .validation import validate_road

@dataclass(frozen=True)
class SideResult:
    allowance_m: float
    limiting_feature: str


@dataclass(frozen=True)
class LaneResult:
    """The Wk zone assigned to one lane, ordered from left to right."""

    lane_number: int
    name: str
    lane_width_m: float
    left_allowance_m: float
    right_allowance_m: float
    lane_wk_m: float
    wk_start_m: float
    wk_end_m: float


@dataclass(frozen=True)
class WkResult:
    travelled_width_m: float
    left: SideResult
    right: SideResult
    unrestricted_wk_m: float
    physical_limit_m: float | None
    calculated_wk_m: float
    final_wk_m: float
    authority_width_m: float | None
    authority_rule: AuthorityRule
    rule_path: str
    explanation: tuple[str, ...]
    lanes: tuple[LaneResult, ...] = ()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["authority_rule"] = self.authority_rule.value
        return data

def calculate_travelled_width(elements: Iterable[TravelledElement]) -> float:
    return sum(element.total_width for element in elements)


def _expanded_lanes(elements: Iterable[TravelledElement]) -> list[tuple[str, float]]:
    """Expand quantities into ordered, individually calculated lanes."""
    lanes: list[tuple[str, float]] = []
    for element in elements:
        if not element.included:
            continue
        for item in range(1, element.quantity + 1):
            suffix = f" {item}" if element.quantity > 1 else ""
            lanes.append((f"{element.element_type}{suffix}", element.individual_width))
    return lanes


def _calculate_lanes(
    elements: Iterable[TravelledElement],
    travelled_width_m: float,
    left_allowance_m: float,
    right_allowance_m: float,
    calculated_wk_m: float,
) -> tuple[LaneResult, ...]:
    """Allocate physical Wk to ordered lanes without hiding a limit convention.

    A physical cap can reduce the two outside allowances. The reduction is shared
    pro-rata between the requested left and right allowances; interior lane widths
    are never changed. Only the first and last lanes receive outside allowance.
    """
    lanes = _expanded_lanes(elements)
    if not lanes:
        return ()
    element_total = sum(width for _, width in lanes)
    if abs(element_total - travelled_width_m) > 1e-6:
        raise ValueError(
            "Included lane widths must equal the travelled-way width before "
            "per-lane Wk can be calculated."
        )

    available_allowance = max(0.0, calculated_wk_m - travelled_width_m)
    requested_allowance = left_allowance_m + right_allowance_m
    factor = min(1.0, available_allowance / requested_allowance) if requested_allowance else 0.0
    effective_left = left_allowance_m * factor
    effective_right = right_allowance_m * factor

    results: list[LaneResult] = []
    cursor = 0.0
    for index, (name, width) in enumerate(lanes, start=1):
        lane_left = effective_left if index == 1 else 0.0
        lane_right = effective_right if index == len(lanes) else 0.0
        lane_wk = lane_left + width + lane_right
        results.append(
            LaneResult(
                lane_number=index,
                name=name,
                lane_width_m=width,
                left_allowance_m=lane_left,
                right_allowance_m=lane_right,
                lane_wk_m=lane_wk,
                wk_start_m=cursor,
                wk_end_m=cursor + lane_wk,
            )
        )
        cursor += lane_wk
    return tuple(results)

def calculate_side_allowance(side: SideInput, maximum_m: float = 3.0) -> SideResult:
    boundary = side.boundary_type
    if boundary == BoundaryType.KERB_AT_TRAVELLED_EDGE:
        return SideResult(0.0, "kerb at travelled-way edge")
    if boundary == BoundaryType.KERB_BEYOND_EDGE_LINE:
        if side.surface == SurfaceType.UNSEALED:
            return SideResult(0.0, "unsealed surface between edge line and kerb")
        value = min(side.distance_to_kerb_m or 0.0, maximum_m)
        return SideResult(value, "kerb distance" if value < maximum_m else "maximum side allowance")
    if boundary == BoundaryType.SEALED_BEYOND_EDGE_LINE:
        value = min(side.width_beyond_edge_m or 0.0, maximum_m)
        return SideResult(value, "available sealed width" if value < maximum_m else "maximum side allowance")
    if boundary in {BoundaryType.UNSEALED_BEYOND_EDGE_LINE, BoundaryType.NO_EDGE_LINE_OR_KERB}:
        return SideResult(0.0, "unsealed or undefined travelled-way edge")
    if boundary == BoundaryType.AUTHORITY_DEFINED:
        value = min(side.authority_allowance_m or 0.0, maximum_m)
        return SideResult(value, "authority-defined boundary allowance")
    return SideResult(maximum_m, "maximum side allowance from designed edge line")

def calculate_wk(
    road_input: RoadInput,
    travelled_elements: Iterable[TravelledElement] = (),
) -> WkResult:
    validate_road(road_input)
    left = calculate_side_allowance(road_input.left, road_input.maximum_side_allowance_m)
    right = calculate_side_allowance(road_input.right, road_input.maximum_side_allowance_m)
    unrestricted = road_input.travelled_width_m + left.allowance_m + right.allowance_m
    named_limits = [(name, width) for name, width in (("kerb-to-kerb width", road_input.kerb_to_kerb_width_m), ("total sealed width", road_input.total_sealed_width_m)) if width is not None]
    physical_limit = min((width for _, width in named_limits), default=None)
    calculated = min(unrestricted, physical_limit) if physical_limit is not None else unrestricted
    final, authority_text = calculated, "no authority adjustment"
    if road_input.authority_rule == AuthorityRule.MINIMUM:
        final = max(calculated, road_input.authority_width_m or calculated)
        authority_text = "authority minimum applied"
    elif road_input.authority_rule == AuthorityRule.OVERRIDE:
        final = road_input.authority_width_m or calculated
        authority_text = "authority override applied"
    active = [name for name, width in named_limits if width == physical_limit and width < unrestricted]
    physical_text = ", ".join(active) if active else "no physical cap"
    rule_path = f"side allowances → unrestricted Wk → {physical_text} → {authority_text}"
    explanation = (
        f"Left allowance is {left.allowance_m:.2f} m, limited by {left.limiting_feature}.",
        f"Right allowance is {right.allowance_m:.2f} m, limited by {right.limiting_feature}.",
        f"Unrestricted Wk is {road_input.travelled_width_m:.2f} + {left.allowance_m:.2f} + {right.allowance_m:.2f} = {unrestricted:.2f} m.",
        f"The physical-width calculation gives {calculated:.2f} m ({physical_text}).",
        f"The final Wk is {final:.2f} m ({authority_text}).",
    )
    lanes = _calculate_lanes(
        travelled_elements,
        road_input.travelled_width_m,
        left.allowance_m,
        right.allowance_m,
        calculated,
    )
    return WkResult(
        road_input.travelled_width_m,
        left,
        right,
        unrestricted,
        physical_limit,
        calculated,
        final,
        road_input.authority_width_m,
        road_input.authority_rule,
        rule_path,
        explanation,
        lanes,
    )
