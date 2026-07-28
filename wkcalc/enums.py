"""Enumerations shared by the domain model and desktop interface."""
from enum import Enum

class BoundaryType(str, Enum):
    KERB_AT_TRAVELLED_EDGE = "kerb_at_travelled_edge"
    KERB_BEYOND_EDGE_LINE = "kerb_beyond_edge_line"
    SEALED_BEYOND_EDGE_LINE = "sealed_beyond_edge_line"
    UNSEALED_BEYOND_EDGE_LINE = "unsealed_beyond_edge_line"
    DESIGNED_EDGE_LINE = "designed_edge_line"
    NO_EDGE_LINE_OR_KERB = "no_edge_line_or_kerb"
    AUTHORITY_DEFINED = "authority_defined"

BOUNDARY_LABELS = {
    BoundaryType.KERB_AT_TRAVELLED_EDGE: "Kerb at travelled-way edge",
    BoundaryType.KERB_BEYOND_EDGE_LINE: "Kerb beyond traffic-edge line",
    BoundaryType.SEALED_BEYOND_EDGE_LINE: "Traffic-edge line with sealed width beyond",
    BoundaryType.UNSEALED_BEYOND_EDGE_LINE: "Traffic-edge line with unsealed width beyond",
    BoundaryType.DESIGNED_EDGE_LINE: "Designed edge line",
    BoundaryType.NO_EDGE_LINE_OR_KERB: "No edge line or kerb",
    BoundaryType.AUTHORITY_DEFINED: "Authority-defined boundary",
}

class SurfaceType(str, Enum):
    SEALED = "sealed"
    UNSEALED = "unsealed"

class AuthorityRule(str, Enum):
    NONE = "none"
    MINIMUM = "minimum"
    OVERRIDE = "override"
