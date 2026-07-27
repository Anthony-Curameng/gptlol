"""Cross-field validation that cannot be expressed by numeric field constraints."""

from .models import BoundaryType, RoadInput, SideInput


class GeometryError(ValueError):
    """Raised when supplied dimensions describe impossible geometry."""


def validate_side(side: SideInput, label: str = "Side") -> None:
    requirements = {
        BoundaryType.KERB_BEYOND_EDGE_LINE: ("distance_to_kerb", side.distance_to_kerb),
        BoundaryType.SEALED_EDGE: ("sealed_width_available", side.sealed_width_available),
        BoundaryType.AUTHORITY_OVERRIDE: ("authority_allowance", side.authority_allowance),
    }
    if side.boundary_type in requirements:
        field, value = requirements[side.boundary_type]
        if value is None:
            raise GeometryError(f"[incomplete input] {label}: {field} is required for this boundary.")


def validate_road(road: RoadInput) -> None:
    validate_side(road.left_side, "Left side")
    validate_side(road.right_side, "Right side")
    for label, limit in (
        ("Kerb-to-kerb width", road.kerb_to_kerb_width),
        ("Total sealed width", road.total_sealed_width),
    ):
        if limit is not None and limit < road.travelled_width:
            raise GeometryError(
                f"[invalid input] {label} ({limit:.2f} m) cannot be less than travelled width "
                f"({road.travelled_width:.2f} m)."
            )

