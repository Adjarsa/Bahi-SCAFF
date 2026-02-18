from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from facade2d.detection import (
    DetectionConfig,
    cluster_positions,
    detect_decorative_bands,
    detect_openings,
)
from facade2d.geometry import (
    auto_detect_facade_corners,
    pixels_per_meter,
    rectify_facade,
    transform_points,
)
from facade2d.models import FacadeMetrics, FacadeOutput
from facade2d.rendering import draw_overlay, render_svg


@dataclass
class PipelineConfig:
    auto_detect_corners: bool = True
    detection: DetectionConfig = field(default_factory=DetectionConfig)


class Facade2DPipeline:
    """End-to-end facade extraction pipeline."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

    def process(
        self,
        image_path: str,
        output_dir: str,
        corners: list[tuple[float, float]] | None = None,
        reference: tuple[tuple[float, float], tuple[float, float], float] | None = None,
    ) -> FacadeOutput:
        source = cv2.imread(image_path)
        if source is None:
            raise FileNotFoundError(f"Unable to read image: {image_path}")

        src_h, src_w = source.shape[:2]
        if corners is not None:
            corners_np = np.array(corners, dtype=np.float32)
        elif self.config.auto_detect_corners:
            corners_np = auto_detect_facade_corners(source)
        else:
            corners_np = np.array(
                [[0, 0], [src_w - 1, 0], [src_w - 1, src_h - 1], [0, src_h - 1]],
                dtype=np.float32,
            )

        rectified, homography = rectify_facade(source, corners_np)
        rect_h, rect_w = rectified.shape[:2]

        ppm: float | None = None
        if reference is not None:
            p1_src, p2_src, length_m = reference
            p1_rect, p2_rect = transform_points([p1_src, p2_src], homography)
            ppm = pixels_per_meter(p1_rect, p2_rect, length_m)

        openings = detect_openings(rectified, self.config.detection)
        if ppm is not None:
            for opening in openings:
                opening.bbox_m = tuple(float(value / ppm) for value in opening.bbox_px)

        decorative_bands = detect_decorative_bands(rectified)

        centers_y = [opening.bbox_px[1] + opening.bbox_px[3] / 2 for opening in openings]
        centers_x = [opening.bbox_px[0] + opening.bbox_px[2] / 2 for opening in openings]
        floor_levels = cluster_positions(centers_y, tolerance=max(12.0, rect_h * 0.06))
        vertical_axes = cluster_positions(centers_x, tolerance=max(10.0, rect_w * 0.05))

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        rectified_path = output_path / "rectified.png"
        overlay_path = output_path / "overlay.png"
        svg_path = output_path / "facade_2d.svg"
        json_path = output_path / "facade_2d.json"

        cv2.imwrite(str(rectified_path), rectified)
        overlay = draw_overlay(rectified, openings, decorative_bands)
        cv2.imwrite(str(overlay_path), overlay)
        render_svg(rect_w, rect_h, openings, decorative_bands, str(svg_path), pixels_per_meter=ppm)

        metrics = FacadeMetrics(
            width_px=float(rect_w),
            height_px=float(rect_h),
            width_m=(rect_w / ppm) if ppm is not None else None,
            height_m=(rect_h / ppm) if ppm is not None else None,
            pixels_per_meter=ppm,
        )

        result = FacadeOutput(
            metrics=metrics,
            openings=openings,
            decorative_bands_px=[float(value) for value in decorative_bands],
            floor_levels_px=[float(value) for value in floor_levels],
            vertical_axes_px=[float(value) for value in vertical_axes],
            source_image=str(Path(image_path)),
            rectified_image=str(rectified_path),
            overlay_image=str(overlay_path),
            svg_path=str(svg_path),
            json_path=str(json_path),
        )

        json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
        return result
