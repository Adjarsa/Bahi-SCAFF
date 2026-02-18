from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float


@dataclass(frozen=True)
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return max(0.0, self.x_max - self.x_min)

    @property
    def height(self) -> float:
        return max(0.0, self.y_max - self.y_min)

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True)
class Opening:
    kind: str
    box: BoundingBox


@dataclass(frozen=True)
class FacadeFeatures:
    facade_box_px: BoundingBox
    openings_px: list[Opening] = field(default_factory=list)
    floor_lines_px: list[float] = field(default_factory=list)
    roof_line_px: float = 0.0
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PerspectiveResult:
    vanishing_lines: list[tuple[Point2D, Point2D]] = field(default_factory=list)
    orthogonal_score: float = 1.0
    correction_matrix: tuple[tuple[float, float, float], ...] = (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    )


@dataclass(frozen=True)
class CalibrationResult:
    pixels_per_meter: float
    method: str
    confidence: float


@dataclass(frozen=True)
class StructuralGrid:
    x_axes_m: list[float] = field(default_factory=list)
    y_axes_m: list[float] = field(default_factory=list)
    symmetry_score: float = 0.0


@dataclass(frozen=True)
class TechnicalElevation:
    polyline_segments_m: list[tuple[Point2D, Point2D]] = field(default_factory=list)
    opening_boxes_m: list[BoundingBox] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MeshModel:
    vertex_count: int
    face_count: int
    width_m: float
    height_m: float
    depth_m: float
    export_paths: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ScaffoldingBay:
    bay_index: int
    x_start_m: float
    x_end_m: float
    levels_m: list[float] = field(default_factory=list)

    @property
    def width_m(self) -> float:
        return max(0.0, self.x_end_m - self.x_start_m)


@dataclass(frozen=True)
class ScaffoldingPlan:
    bays: list[ScaffoldingBay] = field(default_factory=list)
    facade_height_m: float = 0.0
    compliance_notes: list[str] = field(default_factory=list)

    @property
    def bay_count(self) -> int:
        return len(self.bays)


@dataclass(frozen=True)
class MaterialLine:
    code: str
    label: str
    quantity: int
    unit: str


@dataclass(frozen=True)
class QuoteSummary:
    material_cost_eur: float
    labor_cost_eur: float
    margin_eur: float
    vat_eur: float
    total_eur: float
    estimated_hours: float


@dataclass(frozen=True)
class PipelineResult:
    features: FacadeFeatures
    perspective: PerspectiveResult
    calibration: CalibrationResult
    grid: StructuralGrid
    elevation: TechnicalElevation
    mesh: MeshModel
    scaffolding: ScaffoldingPlan
    material_lines: list[MaterialLine] = field(default_factory=list)
    quote: QuoteSummary | None = None
    runtime_ms: int = 0
    assumptions: list[str] = field(default_factory=list)
