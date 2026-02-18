from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import CalibrationResult, FacadeFeatures, StructuralGrid


@dataclass
class GeometryReconstructionService:
    """Reconstruit la grille structurelle facade en metres."""

    def build_grid(self, features: FacadeFeatures, calibration: CalibrationResult) -> StructuralGrid:
        px_to_m = 1.0 / calibration.pixels_per_meter
        box = features.facade_box_px
        width_m = box.width * px_to_m
        height_m = box.height * px_to_m

        x_axes: list[float] = [0.0, width_m]
        y_axes: list[float] = [0.0, height_m]

        for opening in features.openings_px:
            x_axes.append((opening.box.x_min - box.x_min) * px_to_m)
            x_axes.append((opening.box.x_max - box.x_min) * px_to_m)
            y_axes.append((box.y_max - opening.box.y_min) * px_to_m)
            y_axes.append((box.y_max - opening.box.y_max) * px_to_m)

        for floor_line in features.floor_lines_px:
            y_axes.append((box.y_max - floor_line) * px_to_m)

        x_axes_clean = self._unique_sorted(x_axes)
        y_axes_clean = self._unique_sorted(y_axes)
        symmetry_score = self._symmetry_score(x_axes_clean, width_m)

        return StructuralGrid(
            x_axes_m=x_axes_clean,
            y_axes_m=y_axes_clean,
            symmetry_score=symmetry_score,
        )

    @staticmethod
    def _unique_sorted(values: list[float], tolerance: float = 0.02) -> list[float]:
        sorted_values = sorted(max(0.0, v) for v in values)
        unique: list[float] = []
        for value in sorted_values:
            if not unique or abs(value - unique[-1]) > tolerance:
                unique.append(round(value, 3))
        return unique

    @staticmethod
    def _symmetry_score(x_axes: list[float], width_m: float) -> float:
        if width_m <= 0 or len(x_axes) < 2:
            return 0.0
        pair_count = len(x_axes) // 2
        if pair_count == 0:
            return 0.0
        errors = []
        for idx in range(pair_count):
            mirrored_sum = x_axes[idx] + x_axes[-idx - 1]
            errors.append(abs(mirrored_sum - width_m))
        mean_error = sum(errors) / len(errors)
        normalized = mean_error / max(width_m, 0.001)
        return round(max(0.0, 1.0 - normalized), 3)
