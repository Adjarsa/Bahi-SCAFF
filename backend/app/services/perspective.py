from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import FacadeFeatures, PerspectiveResult, Point2D


@dataclass
class PerspectiveCorrectionService:
    """Redressement perspective vers une facade quasi-orthogonale."""

    def correct(self, features: FacadeFeatures) -> PerspectiveResult:
        box = features.facade_box_px
        left_vertical = (Point2D(box.x_min, box.y_min), Point2D(box.x_min, box.y_max))
        right_vertical = (Point2D(box.x_max, box.y_min), Point2D(box.x_max, box.y_max))
        top_horizontal = (Point2D(box.x_min, box.y_min), Point2D(box.x_max, box.y_min))

        skew_ratio = abs(box.width - box.height) / max(box.width, box.height, 1.0)
        orthogonal_score = max(0.7, 1.0 - skew_ratio * 0.2)

        # Matrice homographie simplifiee; dans la version production, elle est
        # issue de la detection des points de fuite et de la minimisation reprojection.
        correction_matrix = (
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        )

        return PerspectiveResult(
            vanishing_lines=[left_vertical, right_vertical, top_horizontal],
            orthogonal_score=orthogonal_score,
            correction_matrix=correction_matrix,
        )
