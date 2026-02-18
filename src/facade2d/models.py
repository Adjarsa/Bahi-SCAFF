from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


Point = tuple[float, float]
BBox = tuple[float, float, float, float]


@dataclass
class Opening:
    """Detected opening (window/door) in rectified facade space."""

    id: str
    bbox_px: BBox
    shape: str
    confidence: float
    bbox_m: BBox | None = None


@dataclass
class FacadeMetrics:
    """Facade dimensions and optional physical scale."""

    width_px: float
    height_px: float
    width_m: float | None = None
    height_m: float | None = None
    pixels_per_meter: float | None = None


@dataclass
class FacadeOutput:
    """Full pipeline output payload."""

    metrics: FacadeMetrics
    openings: list[Opening] = field(default_factory=list)
    decorative_bands_px: list[float] = field(default_factory=list)
    floor_levels_px: list[float] = field(default_factory=list)
    vertical_axes_px: list[float] = field(default_factory=list)
    source_image: str | None = None
    rectified_image: str | None = None
    overlay_image: str | None = None
    svg_path: str | None = None
    json_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
