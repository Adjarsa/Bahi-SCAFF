from __future__ import annotations

import math
from dataclasses import dataclass

from app.domain.models import ScaffoldingBay, ScaffoldingPlan
from app.domain.standards import STANDARDS


@dataclass
class ScaffoldingService:
    """Dimensionnement d'echafaudage conforme aux regles internes."""

    def compute_plan(
        self,
        facade_width_m: float,
        facade_height_m: float,
        terrain_factor: float,
    ) -> ScaffoldingPlan:
        bay_count = max(1, math.ceil(facade_width_m / STANDARDS.max_bay_width_m))
        while bay_count > 1 and (facade_width_m / bay_count) < STANDARDS.min_bay_width_m:
            bay_count -= 1

        bay_width = facade_width_m / bay_count
        levels = self._build_levels(facade_height_m)

        bays: list[ScaffoldingBay] = []
        for idx in range(bay_count):
            start_x = round(idx * bay_width, 3)
            end_x = round((idx + 1) * bay_width, 3)
            bays.append(
                ScaffoldingBay(
                    bay_index=idx + 1,
                    x_start_m=start_x,
                    x_end_m=end_x,
                    levels_m=levels,
                )
            )

        notes = self._compliance_notes(
            bay_width=bay_width,
            facade_width_m=facade_width_m,
            facade_height_m=facade_height_m,
            terrain_factor=terrain_factor,
        )
        return ScaffoldingPlan(
            bays=bays,
            facade_height_m=facade_height_m,
            compliance_notes=notes,
        )

    @staticmethod
    def _build_levels(facade_height_m: float) -> list[float]:
        raw_count = max(1, math.ceil(facade_height_m / STANDARDS.platform_height_step_m))
        levels = []
        for idx in range(raw_count):
            level = min(facade_height_m, (idx + 1) * STANDARDS.platform_height_step_m)
            levels.append(round(level, 3))
        if levels and levels[-1] != round(facade_height_m, 3):
            levels[-1] = round(facade_height_m, 3)
        return levels

    @staticmethod
    def _compliance_notes(
        bay_width: float,
        facade_width_m: float,
        facade_height_m: float,
        terrain_factor: float,
    ) -> list[str]:
        notes = ["Verification regles R408/EN12811 effectuee (niveau pre-dimensionnement)."]
        if bay_width > STANDARDS.max_bay_width_m:
            notes.append("Largeur de travee au-dessus du seuil EN12811.")
        if bay_width < STANDARDS.min_bay_width_m:
            notes.append("Largeur de travee inferieure au minimum operatoire.")
        if terrain_factor > 1.3:
            notes.append("Terrain complexe: renfort d'ancrages recommande.")

        facade_area = facade_width_m * facade_height_m
        recommended_anchors = math.ceil(facade_area * STANDARDS.minimum_anchor_density_per_m2)
        notes.append(f"Ancrages minimum recommandes: {recommended_anchors}.")
        return notes
