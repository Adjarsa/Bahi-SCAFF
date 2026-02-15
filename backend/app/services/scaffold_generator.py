import math
from collections import defaultdict
from statistics import mean

from sqlalchemy.orm import Session

from app.models.material import Material
from app.schemas.generation import (
    GenerationWarning,
    MaterialLine,
    ScaffoldGenerationRequest,
    ScaffoldGenerationResponse,
)
from app.services.r408_rules import evaluate_r408_warnings


def _best_bay_layout(total_width_m: float, module_widths_m: list[float]) -> list[float]:
    width_cm = int(round(total_width_m * 100))
    modules_cm = sorted({int(round(m * 100)) for m in module_widths_m if m > 0})
    if not modules_cm:
        modules_cm = [307]

    max_sum = width_cm + max(modules_cm) * 4
    dp: list[list[int] | None] = [None] * (max_sum + 1)
    dp[0] = []

    for current in range(max_sum + 1):
        if dp[current] is None:
            continue
        for module in modules_cm:
            nxt = current + module
            if nxt > max_sum:
                continue
            candidate = dp[current] + [module]
            current_best = dp[nxt]
            if current_best is None or len(candidate) < len(current_best):
                dp[nxt] = candidate

    best_sum = None
    best_combo: list[int] | None = None
    for tested_sum in range(width_cm, max_sum + 1):
        combo = dp[tested_sum]
        if combo is None:
            continue
        if best_sum is None:
            best_sum = tested_sum
            best_combo = combo
            continue
        overflow = tested_sum - width_cm
        best_overflow = best_sum - width_cm
        if overflow < best_overflow or (overflow == best_overflow and len(combo) < len(best_combo or [])):
            best_sum = tested_sum
            best_combo = combo

    if not best_combo:
        count = max(1, math.ceil(total_width_m / 3.07))
        return [round(total_width_m / count, 2)] * count
    return [round(value / 100, 2) for value in best_combo]


def _material_catalog_by_type(db: Session) -> dict[str, dict[str, float]]:
    materials = db.query(Material).all()
    stock_by_type: dict[str, int] = defaultdict(int)
    weight_by_type: dict[str, list[float]] = defaultdict(list)

    for material in materials:
        stock_by_type[material.type] += material.stock_quantity
        weight_by_type[material.type].append(material.weight_kg)

    catalog: dict[str, dict[str, float]] = {}
    for material_type, quantity in stock_by_type.items():
        catalog[material_type] = {
            "stock": quantity,
            "unit_weight_kg": round(mean(weight_by_type[material_type]), 2) if weight_by_type[material_type] else 0.0,
        }
    return catalog


def generate_scaffold_plan(
    *,
    db: Session,
    facade_width_m: float,
    facade_height_m: float,
    calibration_confidence: float,
    req: ScaffoldGenerationRequest,
) -> ScaffoldGenerationResponse:
    bay_layout = _best_bay_layout(facade_width_m, req.available_module_widths_m)
    bays = len(bay_layout)
    levels = req.number_of_levels or max(1, math.ceil(facade_height_m / req.level_height_m))

    anchors_count = max(4, (math.ceil(facade_width_m / 6.0) + 1) * max(1, math.ceil(facade_height_m / 4.0)))

    quantities = {
        "montants": (bays + 1) * 2 * levels,
        "plateaux": bays * levels,
        "moises": bays * (levels + 1) * 2,
        "diagonales": max(2, math.ceil(bays / 3) * levels),
        "garde_corps": bays * levels * 2,
        "plinthes": bays * levels * 2,
        "verins": (bays + 1) * 2,
        "ancrages": anchors_count,
        "echelles": max(1, math.ceil(levels / 2)),
        "planchers": bays * levels,
        "lisses": bays * levels * 2,
        "consoles": math.ceil(bays / 2) if req.has_consoles else 0,
        "filets": bays * levels if req.has_nets else 0,
        "protections_pietons": bays if req.has_pedestrian_protection else 0,
        "escaliers": 1 if req.has_stair_tower else 0,
    }

    catalog = _material_catalog_by_type(db)
    lines: list[MaterialLine] = []
    warnings: list[GenerationWarning] = []
    total_weight = 0.0
    stock_sufficient = True

    for material_type, qty in quantities.items():
        if qty <= 0:
            continue
        meta = catalog.get(material_type, {"stock": 0, "unit_weight_kg": 0.0})
        stock = int(meta["stock"])
        unit_weight = float(meta["unit_weight_kg"])
        shortage = max(0, qty - stock)
        if shortage > 0:
            stock_sufficient = False
            warnings.append(
                GenerationWarning(
                    code="STOCK_INSUFFISANT",
                    severity="warning",
                    message=f"Stock insuffisant pour {material_type}: manque {shortage} piece(s).",
                )
            )
        line_weight = qty * unit_weight
        total_weight += line_weight
        lines.append(
            MaterialLine(
                type=material_type,
                quantity=qty,
                unit_weight_kg=round(unit_weight, 2),
                total_weight_kg=round(line_weight, 2),
                in_stock=stock,
                shortage=shortage,
            )
        )

    warnings.extend(
        evaluate_r408_warnings(
            facade_width_m=facade_width_m,
            facade_height_m=facade_height_m,
            levels=levels,
            bay_layout_m=bay_layout,
            anchors_count=anchors_count,
            req=req,
        )
    )

    highest_severity = {warning.severity for warning in warnings}
    requires_confirmation = "critical" in highest_severity or calibration_confidence < 0.6
    confidence = max(0.2, min(0.99, round((0.65 if warnings else 0.85) * calibration_confidence + 0.15, 2)))
    total_volume = round(total_weight / 160.0, 2) if total_weight > 0 else 0.0

    return ScaffoldGenerationResponse(
        facade_width_m=facade_width_m,
        facade_height_m=facade_height_m,
        levels=levels,
        bay_layout_m=bay_layout,
        quantities=lines,
        total_weight_kg=round(total_weight, 2),
        total_volume_m3=total_volume,
        stock_sufficient=stock_sufficient,
        warnings=warnings,
        confidence=confidence,
        requires_confirmation=requires_confirmation,
    )
