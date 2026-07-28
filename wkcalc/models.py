"""Validated, serialisable inputs for Wk calculations."""
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .enums import AuthorityRule, BoundaryType, SurfaceType

class SideInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    boundary_type: BoundaryType
    distance_to_kerb_m: float | None = Field(default=None, ge=0)
    width_beyond_edge_m: float | None = Field(default=None, ge=0)
    surface: SurfaceType | None = None
    authority_allowance_m: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def required_measurement(self) -> "SideInput":
        if self.boundary_type == BoundaryType.KERB_BEYOND_EDGE_LINE:
            if self.distance_to_kerb_m is None:
                raise ValueError("distance to kerb is required")
            if self.surface is None:
                raise ValueError("surface between edge line and kerb is required")
        if self.boundary_type in {BoundaryType.SEALED_BEYOND_EDGE_LINE, BoundaryType.UNSEALED_BEYOND_EDGE_LINE} and self.width_beyond_edge_m is None:
            raise ValueError("width beyond the traffic-edge line is required")
        if self.boundary_type == BoundaryType.AUTHORITY_DEFINED and self.authority_allowance_m is None:
            raise ValueError("authority-defined side allowance is required")
        return self

class TravelledElement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    element_type: str = Field(min_length=1, max_length=80)
    quantity: int = Field(default=1, ge=1)
    individual_width: float = Field(gt=0)
    included: bool = True
    notes: str = ""

    @property
    def total_width(self) -> float:
        return self.quantity * self.individual_width if self.included else 0.0

class RoadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    travelled_width_m: float = Field(gt=0)
    left: SideInput
    right: SideInput
    kerb_to_kerb_width_m: float | None = Field(default=None, gt=0)
    total_sealed_width_m: float | None = Field(default=None, gt=0)
    authority_width_m: float | None = Field(default=None, gt=0)
    authority_rule: AuthorityRule = AuthorityRule.NONE
    maximum_side_allowance_m: float = Field(default=3.0, gt=0, le=3.0)

class ProjectDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project: str = ""
    road_name: str = ""
    section: str = ""
    road_authority: str = ""
    calculation_reference: str = ""

class CalculationRecord(BaseModel):
    schema_version: int = 1
    project: ProjectDetails = Field(default_factory=ProjectDetails)
    road: RoadInput
    travelled_elements: list[TravelledElement] = Field(default_factory=list)
