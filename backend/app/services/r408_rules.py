from dataclasses import dataclass

from app.schemas.generation import GenerationWarning, ScaffoldGenerationRequest


@dataclass(frozen=True)
class R408Thresholds:
    max_height_without_anchor_m: float = 4.0
    max_anchor_horizontal_spacing_m: float = 6.0
    max_anchor_vertical_spacing_m: float = 4.0
    max_bay_width_load_class_5_6_m: float = 2.57


def evaluate_r408_warnings(
    *,
    facade_width_m: float,
    facade_height_m: float,
    levels: int,
    bay_layout_m: list[float],
    anchors_count: int,
    req: ScaffoldGenerationRequest,
) -> list[GenerationWarning]:
    thresholds = R408Thresholds()
    warnings: list[GenerationWarning] = []

    required_anchor_lines_x = max(1, int(facade_width_m // thresholds.max_anchor_horizontal_spacing_m) + 1)
    required_anchor_lines_y = max(1, int(facade_height_m // thresholds.max_anchor_vertical_spacing_m) + 1)
    required_anchors = required_anchor_lines_x * required_anchor_lines_y

    if facade_height_m > thresholds.max_height_without_anchor_m and anchors_count < required_anchors:
        warnings.append(
            GenerationWarning(
                code="R408_ANCHORAGE_INSUFFISANT",
                severity="critical",
                message=(
                    "Nombre d'ancrages insuffisant pour la hauteur du montage "
                    f"({anchors_count} / requis >= {required_anchors})."
                ),
            )
        )

    if req.load_class >= 5 and any(width > thresholds.max_bay_width_load_class_5_6_m for width in bay_layout_m):
        warnings.append(
            GenerationWarning(
                code="R408_TRAVEE_CHARGE",
                severity="warning",
                message="Classe de charge elevee: largeur de travee a reduire pour limiter les efforts.",
            )
        )

    if req.access_mode not in {"trappe", "echelle", "escalier"}:
        warnings.append(
            GenerationWarning(
                code="R408_ACCES_INVALIDE",
                severity="critical",
                message="Mode d'acces non reconnu. Utiliser trappe, echelle ou escalier.",
            )
        )

    if levels > 1 and req.access_mode == "echelle" and not req.has_stair_tower:
        warnings.append(
            GenerationWarning(
                code="R408_ACCES_SECU",
                severity="warning",
                message="Acces echelle sur plusieurs niveaux: privilegier une tour escalier securisee.",
            )
        )

    if not req.has_pedestrian_protection:
        warnings.append(
            GenerationWarning(
                code="R408_PROTECTION_PIETON",
                severity="info",
                message="Protection pieton non activee. Verifier le contexte chantier.",
            )
        )

    return warnings
