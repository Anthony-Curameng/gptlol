"""Public GUI-independent API for Wk Calculator."""
from .constants import APPLICATION_VERSION
from .enums import AuthorityRule, EdgeReferenceType, OuterBoundaryType, RoadArrangement, SegmentType, SurfaceType, WidthInputMode
from .models import CalculationRecord, CrossSectionSegment, RoadInput, SegmentResult, SideBoundaryInput, WkResult
__all__ = ["APPLICATION_VERSION", "AuthorityRule", "CalculationRecord", "CrossSectionSegment", "EdgeReferenceType", "OuterBoundaryType", "RoadArrangement", "RoadInput", "SegmentResult", "SegmentType", "SideBoundaryInput", "SurfaceType", "WidthInputMode", "WkResult"]
from .calculator import calculate_internal_width, calculate_side_allowance, calculate_wk
__all__ += ["calculate_internal_width", "calculate_side_allowance", "calculate_wk"]
