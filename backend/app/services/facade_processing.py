from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.schemas.project import FacadeDetection

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".pdf", ".dwg"}


async def save_facade_files(project_id: str, files: list[UploadFile]) -> list[str]:
    settings = get_settings()
    upload_root = Path(settings.upload_dir) / project_id
    upload_root.mkdir(parents=True, exist_ok=True)

    saved_paths: list[str] = []
    for uploaded in files:
        suffix = Path(uploaded.filename or "").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Format non supporte: {suffix}")
        if not uploaded.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant.")
        destination = upload_root / uploaded.filename
        content = await uploaded.read()
        destination.write_bytes(content)
        saved_paths.append(str(destination))
    return saved_paths


def _detect_from_image(path: Path) -> tuple[float, float]:
    try:
        with Image.open(path) as img:
            width_px, height_px = img.size
    except UnidentifiedImageError:
        return 12.0, 10.0
    # Estimation conservative en attente de calibration.
    width_m = max(6.0, round(width_px / 220.0, 2))
    height_m = max(5.0, round(height_px / 210.0, 2))
    return width_m, height_m


def detect_facade_features(paths: list[str]) -> dict[str, Any]:
    if not paths:
        return FacadeDetection().model_dump()

    first = Path(paths[0])
    if first.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic"}:
        width_m, height_m = _detect_from_image(first)
        confidence = 0.62
    else:
        width_m, height_m = 12.0, 10.0
        confidence = 0.45

    levels = []
    current = 3.0
    while current < height_m:
        levels.append(round(current, 2))
        current += 3.0

    openings = [
        {"type": "porte", "x_m": round(width_m * 0.1, 2), "y_m": 0.0, "width_m": 1.0, "height_m": 2.1},
        {"type": "fenetre", "x_m": round(width_m * 0.55, 2), "y_m": 1.2, "width_m": 1.4, "height_m": 1.2},
    ]
    balconies = [{"x_m": round(width_m * 0.35, 2), "y_m": 3.2, "width_m": 2.5, "depth_m": 1.2}]
    obstacles = [{"type": "lampadaire", "x_m": round(width_m * 0.05, 2), "distance_facade_m": 1.2}]

    return FacadeDetection(
        width_m=width_m,
        height_m=height_m,
        levels=levels,
        openings=openings,
        balconies=balconies,
        obstacles=obstacles,
        confidence=confidence,
    ).model_dump()
