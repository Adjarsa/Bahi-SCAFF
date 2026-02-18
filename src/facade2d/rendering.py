from __future__ import annotations

from pathlib import Path

import cv2

from facade2d.models import Opening


def _format_value(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def render_svg(
    width_px: int,
    height_px: int,
    openings: list[Opening],
    decorative_bands_px: list[float],
    output_path: str,
    pixels_per_meter: float | None = None,
) -> None:
    """Render a clean 2D vector elevation."""
    width_m = (width_px / pixels_per_meter) if pixels_per_meter else None
    height_m = (height_px / pixels_per_meter) if pixels_per_meter else None

    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" '
        f'width="{width_px}" height="{height_px}">'
    )
    lines.append('  <defs>')
    lines.append('    <style>')
    lines.append("      .outline { fill: none; stroke: #1c1c1c; stroke-width: 2; }")
    lines.append("      .opening { fill: #d9e4f5; stroke: #2b3d5e; stroke-width: 1.5; }")
    lines.append("      .band { stroke: #a14722; stroke-width: 1.3; fill: none; }")
    lines.append("      .dim { stroke: #7a7a7a; stroke-width: 1; fill: none; }")
    lines.append("      .txt { fill: #333; font-family: Arial, sans-serif; font-size: 12px; }")
    lines.append("    </style>")
    lines.append("  </defs>")
    lines.append('  <rect class="outline" x="1" y="1" width="{0}" height="{1}"/>'.format(width_px - 2, height_px - 2))

    for band_y in decorative_bands_px:
        y = _format_value(band_y)
        lines.append(f'  <line class="band" x1="0" y1="{y}" x2="{width_px}" y2="{y}"/>')

    for opening in openings:
        x, y, w, h = opening.bbox_px
        if opening.shape == "arched":
            x1 = _format_value(x)
            y1 = _format_value(y + h)
            x2 = _format_value(x + w)
            top = _format_value(y + h * 0.35)
            arc_r = _format_value(w / 2)
            lines.append(
                "  <path class=\"opening\" "
                f"d=\"M{x1},{y1} L{x1},{top} A{arc_r},{arc_r} 0 0 1 {x2},{top} L{x2},{y1} Z\"/>"
            )
        else:
            lines.append(
                "  <rect class=\"opening\" "
                f"x=\"{_format_value(x)}\" y=\"{_format_value(y)}\" "
                f"width=\"{_format_value(w)}\" height=\"{_format_value(h)}\"/>"
            )

    if width_m is not None and height_m is not None:
        lines.append(f'  <line class="dim" x1="0" y1="{height_px + 15}" x2="{width_px}" y2="{height_px + 15}"/>')
        lines.append(f'  <line class="dim" x1="{width_px + 15}" y1="0" x2="{width_px + 15}" y2="{height_px}"/>')
        lines.append(
            f'  <text class="txt" x="{width_px / 2}" y="{height_px + 32}" text-anchor="middle">'
            f"{_format_value(width_m)} m</text>"
        )
        lines.append(
            f'  <text class="txt" x="{width_px + 26}" y="{height_px / 2}" '
            'transform="rotate(90 {0} {1})">'.format(width_px + 26, height_px / 2)
            + f"{_format_value(height_m)} m</text>"
        )

    lines.append("</svg>")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def draw_overlay(image: np.ndarray, openings: list[Opening], decorative_bands_px: list[float]) -> np.ndarray:
    """Draw detection overlay for QA checks."""
    overlay = image.copy()
    for opening in openings:
        x, y, w, h = opening.bbox_px
        x0, y0, x1, y1 = int(x), int(y), int(x + w), int(y + h)
        cv2.rectangle(overlay, (x0, y0), (x1, y1), (43, 61, 94), 2)
        cv2.putText(
            overlay,
            opening.id,
            (x0, max(12, y0 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (24, 24, 24),
            1,
            cv2.LINE_AA,
        )

    for band_y in decorative_bands_px:
        y = int(round(band_y))
        cv2.line(overlay, (0, y), (overlay.shape[1] - 1, y), (34, 84, 201), 1, cv2.LINE_AA)
    return overlay
