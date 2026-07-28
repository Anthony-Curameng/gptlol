"""Public API for the GUI-independent Wk calculation layer."""
from .calculator import LaneResult, SideResult, WkResult, calculate_side_allowance, calculate_travelled_width, calculate_wk
from .enums import AuthorityRule, BoundaryType, SurfaceType
from .models import CalculationRecord, ProjectDetails, RoadInput, SideInput, TravelledElement
__all__ = ["AuthorityRule", "BoundaryType", "CalculationRecord", "LaneResult", "ProjectDetails", "RoadInput", "SideInput", "SideResult", "SurfaceType", "TravelledElement", "WkResult", "calculate_side_allowance", "calculate_travelled_width", "calculate_wk"]
