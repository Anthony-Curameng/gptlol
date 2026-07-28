"""Validated input and output models for the calculation engine."""

from enum import Enum

from pydantic import BaseModel, Field


class BoundaryType(str, Enum):
    KERB_AT_TRAVELLED_EDGE = "kerb_at_travelled_edge"
    KERB_BEYOND_EDGE_LINE = "kerb_beyond_edge_line"
    SEALED_EDGE = "sealed_edge"
    UNSEALED_EDGE = "unsealed_edge"
    DESIGNED_EDGE_LINE = "designed_edge_line"
    AUTHORITY_OVERRIDE = "authority_override"


class SideInput(BaseModel):
    boundary_type: BoundaryType
    distance_to_kerb: float | None = Field(default=None, ge=0)
    sealed_width_available: float | None = Field(default=None, ge=0)
    authority_allowance: float | None = Field(default=None, ge=0)


class TravelledElement(BaseModel):
    element_type: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    individual_width: float = Field(gt=0)
    included: bool = True
    notes: str = ""

    @property
    def total_width(self) -> float:
        return self.quantity * self.individual_width if self.included else 0.0


class RoadInput(BaseModel):
    travelled_width: float = Field(gt=0)
    left_side: SideInput
    right_side: SideInput
    kerb_to_kerb_width: float | None = Field(default=None, gt=0)
    total_sealed_width: float | None = Field(default=None, gt=0)
    authority_wk: float | None = Field(default=None, gt=0)
    sealed_areas_are_travelled: bool = False


class CalculationResult(BaseModel):
    travelled_width: float
    left_allowance: float
    right_allowance: float
    unrestricted_wk: float
    limiting_width: float | None
    calculated_wk: float
    rule_applied: str
    warnings: list[str] = Field(default_factory=list)
    authority_wk: float | None = None

