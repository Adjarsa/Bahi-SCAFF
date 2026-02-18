from __future__ import annotations

import math
from dataclasses import dataclass

from app.domain.models import MaterialLine, ScaffoldingPlan
from app.domain.standards import STANDARDS


@dataclass
class BillOfMaterialsService:
    """Genere un quantitatif detaille exploitable depot/commande."""

    def compute(self, plan: ScaffoldingPlan, facade_width_m: float) -> list[MaterialLine]:
        if not plan.bays:
            return []

        bay_count = len(plan.bays)
        level_count = len(plan.bays[0].levels_m)
        facade_area = facade_width_m * plan.facade_height_m

        uprights = (bay_count + 1) * (level_count + 1) * 2
        platforms = bay_count * level_count
        diagonals = max(2, bay_count * max(1, level_count // 2))
        guardrails = bay_count * level_count * 2
        toe_boards = bay_count * level_count
        anchors = math.ceil(facade_area * STANDARDS.minimum_anchor_density_per_m2)

        return [
            MaterialLine(code="MNT", label="Montants", quantity=uprights, unit="pcs"),
            MaterialLine(code="PLT", label="Plateaux", quantity=platforms, unit="pcs"),
            MaterialLine(code="DIA", label="Diagonales", quantity=diagonals, unit="pcs"),
            MaterialLine(code="GDC", label="Garde-corps", quantity=guardrails, unit="pcs"),
            MaterialLine(code="PLI", label="Plinthes", quantity=toe_boards, unit="pcs"),
            MaterialLine(code="ANC", label="Ancrages", quantity=anchors, unit="pcs"),
        ]
