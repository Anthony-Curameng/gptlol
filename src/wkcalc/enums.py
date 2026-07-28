"""All domain enumerations; enums are not redeclared elsewhere."""
from enum import Enum

class RoadArrangement(str, Enum):
    SINGLE_CARRIAGEWAY = "single_carriageway"
    DIVIDED_CARRIAGEWAY_ONE_SIDE = "divided_carriageway_one_side"
    MIXED_OR_ASYMMETRIC = "mixed_or_asymmetric"

class WidthInputMode(str, Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"

class SegmentType(str, Enum):
    THROUGH_LANE = "through_lane"
    TURN_LANE = "turn_lane"
    PARKING_LANE = "parking_lane"
    BICYCLE_LANE = "bicycle_lane"
    INTERNAL_PAINTED_SEPARATION = "internal_painted_separation"
    OTHER_INTERNAL_SEALED = "other_internal_sealed"

class EdgeReferenceType(str, Enum):
    MARKED_OUTER_TRAFFIC_EDGE_LINE = "marked_outer_traffic_edge_line"
    DESIGNED_OUTER_TRAFFIC_EDGE_LINE = "designed_outer_traffic_edge_line"
    KERB_IS_OUTER_TRAVELLED_EDGE = "kerb_is_outer_travelled_edge"

class OuterBoundaryType(str, Enum):
    KERB = "kerb"
    EDGE_OF_SEAL = "edge_of_seal"
    AUTHORITY_DEFINED = "authority_defined"

class SurfaceType(str, Enum):
    SEALED = "sealed"
    UNSEALED = "unsealed"

class AuthorityRule(str, Enum):
    NONE = "none"
    FINAL_OVERRIDE = "final_override"
    MINIMUM = "minimum"
