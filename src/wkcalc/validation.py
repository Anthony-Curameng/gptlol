"""Cross-field validation performed before any result is produced."""
from .enums import AuthorityRule, RoadArrangement, WidthInputMode
from .models import RoadInput

class InputValidationError(ValueError): pass
class AuthorityGeometryConflict(InputValidationError): pass

def validate_road_input(road: RoadInput) -> None:
    if road.physical_median_present and road.arrangement != RoadArrangement.DIVIDED_CARRIAGEWAY_ONE_SIDE:
        raise InputValidationError("A physical median requires calculation of one carriageway of a divided road.")
    if road.full_kerb_to_kerb_is_travelled:
        if road.kerb_to_kerb_width_m is None:
            raise InputValidationError("Enter the fully travelled kerb-to-kerb width.")
    elif road.width_mode == WidthInputMode.SIMPLE:
        if road.simple_internal_width_m is None:
            raise InputValidationError("Enter the outer-edge-to-outer-edge internal width.")
        if road.segments:
            raise InputValidationError("Segments must be empty in simple width mode.")
    elif not road.segments:
        raise InputValidationError("Add at least one internal cross-section segment.")
    if not road.full_kerb_to_kerb_is_travelled and (road.left_boundary is None or road.right_boundary is None):
        raise InputValidationError("Configure both outer boundaries independently.")
    internal = road.kerb_to_kerb_width_m if road.full_kerb_to_kerb_is_travelled else (road.simple_internal_width_m if road.width_mode == WidthInputMode.SIMPLE else sum(segment.total_width_m for segment in road.segments))
    if road.kerb_to_kerb_width_m is not None and internal is not None and road.kerb_to_kerb_width_m < internal:
        raise InputValidationError("The physical total cannot be less than the internal width.")
    if road.authority_rule == AuthorityRule.NONE:
        if road.authority_width_m is not None or road.authority_name.strip() or road.authority_reference.strip():
            raise InputValidationError("Authority fields must be blank when no adjustment is selected.")
    elif road.authority_width_m is None or not road.authority_name.strip() or not road.authority_reference.strip():
        raise InputValidationError("Authority name, reference, and width are all required.")
