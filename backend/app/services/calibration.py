import math

from fastapi import HTTPException

from app.schemas.project import CalibrationRequest, CalibrationResult


def calibrate_facade(request: CalibrationRequest, facade_data: dict) -> CalibrationResult:
    method = request.method.lower().strip()
    if method not in {"manual", "automatic", "lidar"}:
        raise HTTPException(status_code=400, detail="Methode de calibration invalide.")

    if method == "manual":
        if request.reference_distance_m is None or request.point_a is None or request.point_b is None:
            raise HTTPException(status_code=400, detail="Calibration manuelle incomplete.")
        dx = request.point_b[0] - request.point_a[0]
        dy = request.point_b[1] - request.point_a[1]
        pixel_distance = math.hypot(dx, dy)
        if pixel_distance <= 1e-6:
            raise HTTPException(status_code=400, detail="Distance pixels invalide.")
        scale = request.reference_distance_m / pixel_distance
        confidence = 0.92
    elif method == "automatic":
        width_m = float(facade_data.get("width_m", 12.0))
        synthetic_px_width = max(1000.0, width_m * 220.0)
        scale = width_m / synthetic_px_width
        confidence = 0.68
    else:  # lidar
        width_m = float(facade_data.get("width_m", 12.0))
        synthetic_px_width = max(1000.0, width_m * 240.0)
        scale = width_m / synthetic_px_width
        confidence = 0.97

    return CalibrationResult(
        method=method,
        scale_m_per_px=round(scale, 6),
        confidence=confidence,
        requires_confirmation=confidence < 0.7,
    )
