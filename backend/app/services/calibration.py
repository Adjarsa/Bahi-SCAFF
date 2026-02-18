from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import CalibrationResult, FacadeFeatures


@dataclass
class KnownMeasurementInput:
    pixel_span: float
    meter_span: float


@dataclass
class CalibrationService:
    """Calibration metrique pixels -> metres (auto + manuelle)."""

    def calibrate(
        self,
        features: FacadeFeatures,
        known_measurement: KnownMeasurementInput | None,
        estimated_story_height_m: float,
    ) -> CalibrationResult:
        if known_measurement is not None:
            pixels_per_meter = known_measurement.pixel_span / known_measurement.meter_span
            return CalibrationResult(
                pixels_per_meter=self._clamp_pixels_per_meter(pixels_per_meter),
                method="manual_reference",
                confidence=0.97,
            )

        if features.floor_lines_px:
            facade_top = features.facade_box_px.y_min
            first_floor = features.floor_lines_px[0]
            story_height_px = max(1.0, first_floor - facade_top)
        else:
            story_height_px = max(1.0, features.facade_box_px.height / 3)

        pixels_per_meter = story_height_px / estimated_story_height_m
        confidence = 0.82 if features.openings_px else 0.72
        return CalibrationResult(
            pixels_per_meter=self._clamp_pixels_per_meter(pixels_per_meter),
            method="automatic_inference",
            confidence=confidence,
        )

    @staticmethod
    def _clamp_pixels_per_meter(value: float) -> float:
        return min(500.0, max(2.0, value))
