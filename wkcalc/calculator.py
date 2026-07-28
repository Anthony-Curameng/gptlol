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

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["authority_rule"] = self.authority_rule.value
        return data

def calculate_travelled_width(elements: Iterable[TravelledElement]) -> float:
    return sum(element.total_width for element in elements)

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

def calculate_wk(road_input: RoadInput) -> WkResult:
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
    return WkResult(road_input.travelled_width_m, left, right, unrestricted, physical_limit, calculated, final, road_input.authority_width_m, road_input.authority_rule, rule_path, explanation)
