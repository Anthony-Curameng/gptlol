"""Single deterministic Wk engine. This module has no GUI dependencies."""
from dataclasses import dataclass
from .constants import MAX_STANDARD_SIDE_ALLOWANCE_M
from .enums import AuthorityRule, EdgeReferenceType, OuterBoundaryType, SegmentType, SurfaceType, WidthInputMode
from .models import RoadInput, SegmentResult, SideBoundaryInput, WkResult
from .validation import AuthorityGeometryConflict, validate_road_input

@dataclass(frozen=True)
class SideDecision:
    allowance_m: float
    reason: str
    trace: str
    warning: str | None = None

def calculate_internal_width(road: RoadInput) -> tuple[float, tuple[SegmentResult, ...]]:
    if road.full_kerb_to_kerb_is_travelled:
        return road.kerb_to_kerb_width_m or 0.0, ()
    if road.width_mode == WidthInputMode.SIMPLE:
        return road.simple_internal_width_m or 0.0, ()
    results = tuple(
        SegmentResult(segment_type=s.segment_type, label=s.label, quantity=s.quantity, individual_width_m=s.width_m, total_width_m=s.total_width_m, inclusion_reason=("Included internal painted separation between the outer traffic-edge lines." if s.is_internal_painted_area else "Included internal sealed cross-section element."))
        for s in road.segments
    )
    return sum(item.total_width_m for item in results), results

def calculate_side_allowance(side: SideBoundaryInput, side_name: str = "Side") -> SideDecision:
    if side.edge_reference == EdgeReferenceType.KERB_IS_OUTER_TRAVELLED_EDGE:
        return SideDecision(0.0, "kerb at outer travelled edge", f"{side_name}: the kerb is the outer travelled edge, so 0.00 m was added.")
    if side.surface_beyond_edge == SurfaceType.UNSEALED:
        return SideDecision(0.0, "unsealed area excluded", f"{side_name}: the area outside the outer traffic-edge line is unsealed, so 0.00 m was added.")
    if side.outer_boundary == OuterBoundaryType.AUTHORITY_DEFINED:
        value = side.authority_allowance_m or 0.0
        warning = f"{side_name} authority-defined allowance exceeds the standard 3.00 m cap; authority review required." if value > MAX_STANDARD_SIDE_ALLOWANCE_M else None
        return SideDecision(value, "authority-defined side allowance", f"{side_name}: the authority-defined allowance of {value:.2f} m was used without silent clamping.", warning)
    value = min(side.distance_from_outer_edge_m, MAX_STANDARD_SIDE_ALLOWANCE_M)
    feature = "kerb" if side.outer_boundary == OuterBoundaryType.KERB else "edge of seal"
    reason = f"distance to {feature}" if side.distance_from_outer_edge_m <= MAX_STANDARD_SIDE_ALLOWANCE_M else "standard 3.00 m maximum"
    return SideDecision(value, reason, f"{side_name}: {side.distance_from_outer_edge_m:.2f} m of sealed pavement extends to the {feature}; {value:.2f} m was added ({reason}).")

def _available_sealed_width(road: RoadInput, internal: float, physical: float) -> float:
    if road.kerb_to_kerb_width_m is not None: return road.kerb_to_kerb_width_m
    available = internal
    for side in (road.left_boundary, road.right_boundary):
        if side is not None and side.surface_beyond_edge == SurfaceType.SEALED: available += side.distance_from_outer_edge_m
    return max(physical, available)

def calculate_wk(road: RoadInput) -> WkResult:
    validate_road_input(road)
    internal, segments = calculate_internal_width(road)
    warnings: list[str] = []
    trace: list[str] = [f"The internal span is {internal:.2f} m."]
    for segment in road.segments:
        if segment.segment_type == SegmentType.INTERNAL_PAINTED_SEPARATION:
            trace.append(f"The {segment.total_width_m:.2f} m {segment.label} is included because it lies between the outer traffic-edge lines.")
            if segment.total_width_m > 3.0: warnings.append("Unusually large internal painted separation; confirm it is not a physical median.")
    if road.full_kerb_to_kerb_is_travelled:
        left = SideDecision(0.0, "not applicable in full kerb-to-kerb mode", "Left: no edge offset is required in fully travelled kerb-to-kerb mode.")
        right = SideDecision(0.0, "not applicable in full kerb-to-kerb mode", "Right: no edge offset is required in fully travelled kerb-to-kerb mode.")
        unrestricted = physical = internal
        physical_reason = "Complete sealed kerb-to-kerb width is travelled."
        trace.append(f"The complete sealed kerb-to-kerb width is travelled, so physical Wk is {physical:.2f} m.")
    else:
        left = calculate_side_allowance(road.left_boundary, "Left")  # type: ignore[arg-type]
        right = calculate_side_allowance(road.right_boundary, "Right")  # type: ignore[arg-type]
        trace.extend((left.trace, right.trace)); unrestricted = internal + left.allowance_m + right.allowance_m
        physical, physical_reason = unrestricted, None
        if road.kerb_to_kerb_width_m is not None and road.kerb_to_kerb_width_m < unrestricted:
            physical = road.kerb_to_kerb_width_m; physical_reason = "Explicit kerb-to-kerb geometry verification capped Wk."
            trace.append(f"The explicitly supplied {physical:.2f} m kerb-to-kerb total capped the unrestricted {unrestricted:.2f} m Wk.")
        else: trace.append(f"Physical Wk = {internal:.2f} + {left.allowance_m:.2f} + {right.allowance_m:.2f} = {physical:.2f} m.")
    for decision in (left, right):
        if decision.warning: warnings.append(decision.warning)
    boundaries = (road.left_boundary, road.right_boundary)
    if road.kerb_to_kerb_width_m is not None and not road.full_kerb_to_kerb_is_travelled: warnings.append("Kerb-to-kerb total was supplied as an explicit geometry verification value.")
    if any(s and s.edge_reference == EdgeReferenceType.DESIGNED_OUTER_TRAFFIC_EDGE_LINE for s in boundaries): warnings.append("Width is based on a designed outer traffic edge that is not physically marked.")
    if boundaries and all(s and s.edge_reference != EdgeReferenceType.MARKED_OUTER_TRAFFIC_EDGE_LINE for s in boundaries): warnings.append("No marked outer traffic-edge lines are used.")
    final, authority_reason = physical, None
    if road.authority_rule != AuthorityRule.NONE:
        available = _available_sealed_width(road, internal, physical)
        if (road.authority_width_m or 0) > available:
            raise AuthorityGeometryConflict(f"Authority width {road.authority_width_m:.2f} m exceeds the available sealed geometry {available:.2f} m; review the geometry or authority direction.")
        if road.authority_rule == AuthorityRule.FINAL_OVERRIDE:
            final = road.authority_width_m or physical; authority_reason = f"Final Wk overridden by {road.authority_name}: {road.authority_reference}."; warnings.append("Authority final override applied.")
        else:
            final = max(physical, road.authority_width_m or physical); authority_reason = f"Authority minimum from {road.authority_name} applied where greater: {road.authority_reference}."
        trace.append(f"{authority_reason} Final Wk is {final:.2f} m.")
    else: trace.append(f"No authority adjustment applies; final Wk is {final:.2f} m.")
    return WkResult(internal_width_m=internal,left_allowance_m=left.allowance_m,right_allowance_m=right.allowance_m,unrestricted_wk_m=unrestricted,physical_wk_m=physical,final_wk_m=final,left_limiting_reason=left.reason,right_limiting_reason=right.reason,physical_limiting_reason=physical_reason,authority_adjustment_reason=authority_reason,included_segments=segments,rule_trace=tuple(trace),warnings=tuple(warnings))
