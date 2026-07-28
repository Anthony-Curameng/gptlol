"""Cross-field geometry checks and actionable validation messages."""
from .enums import AuthorityRule
from .models import RoadInput

class GeometryError(ValueError):
    """Raised when dimensions describe impossible or incomplete geometry."""

def validate_road(road: RoadInput) -> None:
    for label, limit in (("Kerb-to-kerb width", road.kerb_to_kerb_width_m), ("Total sealed width", road.total_sealed_width_m)):
        if limit is not None and limit < road.travelled_width_m:
            raise GeometryError(f"[invalid geometry] {label} ({limit:.2f} m) cannot be less than travelled width ({road.travelled_width_m:.2f} m).")
    if road.authority_rule != AuthorityRule.NONE and road.authority_width_m is None:
        raise GeometryError("[incomplete input] An authority width is required for the selected authority rule.")
    if road.authority_rule == AuthorityRule.NONE and road.authority_width_m is not None:
        raise GeometryError("[invalid input] Select an authority minimum or override before entering its width.")
