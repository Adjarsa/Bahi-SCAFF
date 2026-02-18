from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class KnownMeasurement(BaseModel):
    pixel_span: float = Field(gt=0)
    meter_span: float = Field(gt=0)


class OpeningInput(BaseModel):
    kind: str = Field(default="window")
    x_min_px: float = Field(ge=0)
    y_min_px: float = Field(ge=0)
    x_max_px: float = Field(gt=0)
    y_max_px: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_extents(self) -> "OpeningInput":
        if self.x_max_px <= self.x_min_px:
            raise ValueError("x_max_px doit etre > x_min_px")
        if self.y_max_px <= self.y_min_px:
            raise ValueError("y_max_px doit etre > y_min_px")
        return self


class PipelineRequest(BaseModel):
    image_width_px: int = Field(gt=0)
    image_height_px: int = Field(gt=0)
    levels_hint: int = Field(default=3, ge=1, le=50)
    known_measurement: KnownMeasurement | None = None
    manual_openings: list[OpeningInput] = Field(default_factory=list)
    estimated_story_height_m: float = Field(default=3.0, gt=2.0, le=6.0)
    terrain_factor: float = Field(default=1.0, gt=0.5, le=2.0)
    labor_hourly_rate_eur: float = Field(default=55.0, gt=0)
    margin_rate: float = Field(default=0.15, ge=0.0, le=1.0)
    vat_rate: float = Field(default=0.2, ge=0.0, le=1.0)


class ScaffoldingBayOutput(BaseModel):
    bay_index: int
    x_start_m: float
    x_end_m: float
    levels_m: list[float]
    width_m: float


class MaterialLineOutput(BaseModel):
    code: str
    label: str
    quantity: int
    unit: str


class QuoteOutput(BaseModel):
    material_cost_eur: float
    labor_cost_eur: float
    margin_eur: float
    vat_eur: float
    total_eur: float
    estimated_hours: float


class PipelineResponse(BaseModel):
    facade_width_m: float
    facade_height_m: float
    calibration_method: str
    calibration_confidence: float
    scaffolding_bays: list[ScaffoldingBayOutput]
    compliance_notes: list[str]
    materials: list[MaterialLineOutput]
    quote: QuoteOutput
    runtime_ms: int
    assumptions: list[str]


class ExportRequest(BaseModel):
    format: str = Field(pattern="^(svg|dxf|pdf|obj|glb|ifc)$")
