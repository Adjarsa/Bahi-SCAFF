from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import (
    BoundingBox,
    CalibrationResult,
    FacadeFeatures,
    Point2D,
    StructuralGrid,
    TechnicalElevation,
)


@dataclass
class TechnicalElevationService:
    """Produit l'elevation technique 2D exploitable chantier."""

    def generate(
        self,
        features: FacadeFeatures,
        calibration: CalibrationResult,
        grid: StructuralGrid,
    ) -> TechnicalElevation:
        px_to_m = 1.0 / calibration.pixels_per_meter
        box = features.facade_box_px
        width_m = box.width * px_to_m
        height_m = box.height * px_to_m

        segments = [
            (Point2D(0.0, 0.0), Point2D(width_m, 0.0)),
            (Point2D(width_m, 0.0), Point2D(width_m, height_m)),
            (Point2D(width_m, height_m), Point2D(0.0, height_m)),
            (Point2D(0.0, height_m), Point2D(0.0, 0.0)),
        ]
        for y in grid.y_axes_m:
            if 0 < y < height_m:
                segments.append((Point2D(0.0, y), Point2D(width_m, y)))
        for x in grid.x_axes_m:
            if 0 < x < width_m:
                segments.append((Point2D(x, 0.0), Point2D(x, height_m)))

        opening_boxes = [self._convert_opening(opening.box, box, px_to_m) for opening in features.openings_px]
        meta = {
            "export_svg": "available",
            "export_dxf": "available",
            "export_pdf": "available",
        }
        return TechnicalElevation(
            polyline_segments_m=segments,
            opening_boxes_m=opening_boxes,
            meta=meta,
        )

    @staticmethod
    def _convert_opening(box_px: BoundingBox, facade_box_px: BoundingBox, px_to_m: float) -> BoundingBox:
        return BoundingBox(
            x_min=(box_px.x_min - facade_box_px.x_min) * px_to_m,
            y_min=(facade_box_px.y_max - box_px.y_max) * px_to_m,
            x_max=(box_px.x_max - facade_box_px.x_min) * px_to_m,
            y_max=(facade_box_px.y_max - box_px.y_min) * px_to_m,
        )

    def export_svg(self, elevation: TechnicalElevation, width_m: float, height_m: float) -> str:
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_m:.3f} {height_m:.3f}">'
        ]
        for segment in elevation.polyline_segments_m:
            lines.append(
                (
                    f'<line x1="{segment[0].x:.3f}" y1="{height_m - segment[0].y:.3f}" '
                    f'x2="{segment[1].x:.3f}" y2="{height_m - segment[1].y:.3f}" '
                    'stroke="black" stroke-width="0.01"/>'
                )
            )
        for opening in elevation.opening_boxes_m:
            lines.append(
                (
                    f'<rect x="{opening.x_min:.3f}" y="{height_m - opening.y_max:.3f}" '
                    f'width="{opening.width:.3f}" height="{opening.height:.3f}" '
                    'fill="none" stroke="blue" stroke-width="0.01"/>'
                )
            )
        lines.append("</svg>")
        return "".join(lines)

    @staticmethod
    def export_dxf(elevation: TechnicalElevation) -> str:
        output = ["0", "SECTION", "2", "ENTITIES"]
        for segment in elevation.polyline_segments_m:
            output.extend(
                [
                    "0",
                    "LINE",
                    "8",
                    "ELEVATION",
                    "10",
                    f"{segment[0].x:.3f}",
                    "20",
                    f"{segment[0].y:.3f}",
                    "11",
                    f"{segment[1].x:.3f}",
                    "21",
                    f"{segment[1].y:.3f}",
                ]
            )
        output.extend(["0", "ENDSEC", "0", "EOF"])
        return "\n".join(output)

    @staticmethod
    def export_pdf_stub(elevation: TechnicalElevation) -> str:
        return (
            "PDF_TECHNIQUE_STUB\n"
            f"segments={len(elevation.polyline_segments_m)}\n"
            f"openings={len(elevation.opening_boxes_m)}"
        )
