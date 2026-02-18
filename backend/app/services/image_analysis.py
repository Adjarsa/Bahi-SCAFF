from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import BoundingBox, FacadeFeatures, Opening


@dataclass
class ImageAnalysisService:
    """Detection facade robuste avec fallback deterministe.

    Le moteur reel IA (OpenCV + PyTorch) pourra remplacer les heuristiques
    sans changer les contrats de sortie.
    """

    def detect(
        self,
        image_width_px: int,
        image_height_px: int,
        levels_hint: int,
        manual_openings: list[Opening],
    ) -> FacadeFeatures:
        x_margin = image_width_px * 0.08
        y_margin = image_height_px * 0.08
        facade_box = BoundingBox(
            x_min=x_margin,
            y_min=y_margin,
            x_max=image_width_px - x_margin,
            y_max=image_height_px - y_margin,
        )

        floor_lines = self._build_floor_lines(facade_box, levels_hint)
        openings = manual_openings or self._build_default_openings(facade_box, levels_hint)
        warnings = self._quality_warnings(image_width_px, image_height_px, openings)

        confidence = 0.82
        if manual_openings:
            confidence = 0.95
        elif warnings:
            confidence = 0.75

        return FacadeFeatures(
            facade_box_px=facade_box,
            openings_px=openings,
            floor_lines_px=floor_lines,
            roof_line_px=facade_box.y_min,
            confidence=confidence,
            warnings=warnings,
        )

    @staticmethod
    def _build_floor_lines(facade_box: BoundingBox, levels_hint: int) -> list[float]:
        story_count = max(levels_hint, 1)
        story_height = facade_box.height / story_count
        return [facade_box.y_min + i * story_height for i in range(1, story_count)]

    @staticmethod
    def _build_default_openings(facade_box: BoundingBox, levels_hint: int) -> list[Opening]:
        openings: list[Opening] = []
        levels = max(levels_hint, 1)
        story_height = facade_box.height / levels
        opening_width = facade_box.width * 0.14
        opening_height = story_height * 0.45
        spacing = facade_box.width / 4

        for floor_idx in range(levels):
            y_center = facade_box.y_min + story_height * floor_idx + story_height * 0.45
            for col in range(1, 4):
                x_center = facade_box.x_min + spacing * col - spacing * 0.5
                box = BoundingBox(
                    x_min=x_center - opening_width / 2,
                    y_min=y_center - opening_height / 2,
                    x_max=x_center + opening_width / 2,
                    y_max=y_center + opening_height / 2,
                )
                openings.append(Opening(kind="window", box=box))

        door_width = facade_box.width * 0.16
        door_height = story_height * 0.7
        door_center_x = facade_box.x_min + facade_box.width * 0.15
        door_center_y = facade_box.y_max - door_height / 2
        openings.append(
            Opening(
                kind="door",
                box=BoundingBox(
                    x_min=door_center_x - door_width / 2,
                    y_min=door_center_y - door_height / 2,
                    x_max=door_center_x + door_width / 2,
                    y_max=door_center_y + door_height / 2,
                ),
            )
        )

        return openings

    @staticmethod
    def _quality_warnings(image_width_px: int, image_height_px: int, openings: list[Opening]) -> list[str]:
        warnings: list[str] = []
        if image_width_px < 1200 or image_height_px < 800:
            warnings.append("Resolution image limitee, valider les cotes critiques.")
        if not openings:
            warnings.append("Aucune ouverture detectee, calibration auto moins fiable.")
        return warnings
