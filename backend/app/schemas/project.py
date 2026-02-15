from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FacadeDetection(BaseModel):
    width_m: float = Field(default=12.0, gt=0)
    height_m: float = Field(default=10.0, gt=0)
    levels: list[float] = Field(default_factory=lambda: [3.0, 6.0, 9.0])
    openings: list[dict[str, Any]] = Field(default_factory=list)
    balconies: list[dict[str, Any]] = Field(default_factory=list)
    obstacles: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)


class CalibrationRequest(BaseModel):
    method: str = Field(description="manual | automatic | lidar")
    reference_distance_m: float | None = Field(default=None, gt=0)
    point_a: tuple[float, float] | None = None
    point_b: tuple[float, float] | None = None


class CalibrationResult(BaseModel):
    method: str
    scale_m_per_px: float = Field(gt=0)
    confidence: float = Field(ge=0, le=1)
    requires_confirmation: bool = False


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    description: str | None = None
    status: str | None = None


class ProjectRead(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    facade_data: dict[str, Any]
    calibration_data: dict[str, Any]
    generation_result: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
