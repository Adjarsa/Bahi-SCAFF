from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScaffoldingStandards:
    """Parametres simplifies de conformite R408 / EN12811."""

    max_bay_width_m: float = 3.0
    min_bay_width_m: float = 1.5
    platform_height_step_m: float = 2.0
    guardrail_height_m: float = 1.0
    minimum_anchor_density_per_m2: float = 0.25
    max_ledger_span_m: float = 3.0


STANDARDS = ScaffoldingStandards()
