from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import CalibrationResult, FacadeFeatures, MeshModel


@dataclass
class Reconstruction3DService:
    """Reconstruction volumique simplifiee et export multi-format."""

    def reconstruct(self, features: FacadeFeatures, calibration: CalibrationResult) -> MeshModel:
        px_to_m = 1.0 / calibration.pixels_per_meter
        box = features.facade_box_px

        width_m = round(box.width * px_to_m, 3)
        height_m = round(box.height * px_to_m, 3)
        depth_m = round(max(0.45, width_m * 0.08), 3)

        opening_count = len(features.openings_px)
        vertex_count = 8 + opening_count * 8
        face_count = 12 + opening_count * 12

        return MeshModel(
            vertex_count=vertex_count,
            face_count=face_count,
            width_m=width_m,
            height_m=height_m,
            depth_m=depth_m,
            export_paths={
                "obj": "exports/facade_model.obj",
                "glb": "exports/facade_model.glb",
                "ifc": "exports/facade_model.ifc",
            },
        )
