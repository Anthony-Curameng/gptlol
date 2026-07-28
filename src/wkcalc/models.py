"""The single validated domain model used by calculation, UI, and exports."""
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .constants import APPLICATION_VERSION, RULE_REFERENCE, SCHEMA_VERSION
from .enums import AuthorityRule, EdgeReferenceType, OuterBoundaryType, RoadArrangement, SegmentType, SurfaceType, WidthInputMode

class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

class CrossSectionSegment(DomainModel):
    segment_type: SegmentType
    label: str = Field(min_length=1, max_length=100)
    width_m: float = Field(gt=0)
    quantity: int = Field(default=1, ge=1)
    notes: str = ""
    @property
    def total_width_m(self) -> float: return self.width_m * self.quantity
    @property
    def is_vehicle_area(self) -> bool: return self.segment_type in {SegmentType.THROUGH_LANE, SegmentType.TURN_LANE, SegmentType.PARKING_LANE, SegmentType.BICYCLE_LANE}
    @property
    def is_internal_painted_area(self) -> bool: return self.segment_type == SegmentType.INTERNAL_PAINTED_SEPARATION
    @property
    def is_included_in_base_span(self) -> bool: return True

class SideBoundaryInput(DomainModel):
    edge_reference: EdgeReferenceType
    outer_boundary: OuterBoundaryType
    surface_beyond_edge: SurfaceType
    distance_from_outer_edge_m: float = Field(ge=0)
    authority_allowance_m: float | None = Field(default=None, ge=0)
    @model_validator(mode="after")
    def consistent_boundary(self):
        if self.edge_reference == EdgeReferenceType.KERB_IS_OUTER_TRAVELLED_EDGE and (self.outer_boundary != OuterBoundaryType.KERB or self.distance_from_outer_edge_m != 0):
            raise ValueError("A kerb at the travelled edge must use a kerb boundary at zero distance.")
        if self.outer_boundary == OuterBoundaryType.AUTHORITY_DEFINED and self.authority_allowance_m is None:
            raise ValueError("An authority-defined side allowance is required.")
        return self

class RoadInput(DomainModel):
    arrangement: RoadArrangement
    width_mode: WidthInputMode
    simple_internal_width_m: float | None = Field(default=None, gt=0)
    segments: tuple[CrossSectionSegment, ...] = ()
    full_kerb_to_kerb_is_travelled: bool = False
    kerb_to_kerb_width_m: float | None = Field(default=None, gt=0)
    left_boundary: SideBoundaryInput | None = None
    right_boundary: SideBoundaryInput | None = None
    authority_rule: AuthorityRule = AuthorityRule.NONE
    authority_width_m: float | None = Field(default=None, gt=0)
    authority_name: str = ""
    authority_reference: str = ""
    project_name: str = ""
    road_name: str = ""
    section_reference: str = ""
    calculation_notes: str = ""
    physical_median_present: bool = False

class SegmentResult(DomainModel):
    segment_type: SegmentType
    label: str
    quantity: int
    individual_width_m: float
    total_width_m: float
    inclusion_reason: str

class WkResult(DomainModel):
    internal_width_m: float
    left_allowance_m: float
    right_allowance_m: float
    unrestricted_wk_m: float
    physical_wk_m: float
    final_wk_m: float
    left_limiting_reason: str
    right_limiting_reason: str
    physical_limiting_reason: str | None = None
    authority_adjustment_reason: str | None = None
    included_segments: tuple[SegmentResult, ...] = ()
    rule_trace: tuple[str, ...]
    warnings: tuple[str, ...] = ()

class CalculationRecord(DomainModel):
    schema_version: int = SCHEMA_VERSION
    application_version: str = APPLICATION_VERSION
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rule_reference: str = RULE_REFERENCE
    road_input: RoadInput
    result: WkResult
