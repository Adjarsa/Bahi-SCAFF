from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from facade2d.models import Opening


@dataclass
class DetectionConfig:
    min_area_ratio: float = 0.001
    max_area_ratio: float = 0.20
    min_aspect_ratio: float = 0.18
    max_aspect_ratio: float = 4.5
    min_solidity: float = 0.45
    min_contrast: float = 0.08
    dark_percentile: float = 20.0
    nms_iou_threshold: float = 0.35


def _iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2, ay2 = ax1 + aw, ay1 + ah
    bx2, by2 = bx1 + bw, by1 + bh

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    union = aw * ah + bw * bh - inter
    if union <= 0:
        return 0.0
    return inter / union


def _nms(openings: list[Opening], iou_threshold: float) -> list[Opening]:
    sorted_openings = sorted(openings, key=lambda item: item.confidence, reverse=True)
    kept: list[Opening] = []
    for candidate in sorted_openings:
        if all(_iou(candidate.bbox_px, current.bbox_px) < iou_threshold for current in kept):
            kept.append(candidate)
    return kept


def _shape_from_contour(contour: np.ndarray) -> str:
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
    return "arched" if len(approx) >= 6 else "rectangular"


def _remove_border_connected_components(mask: np.ndarray) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1:
        return mask

    height, width = mask.shape[:2]
    cleaned = np.zeros_like(mask)
    for label in range(1, num_labels):
        x, y, w, h, _ = stats[label]
        touches_border = x <= 0 or y <= 0 or (x + w) >= width or (y + h) >= height
        if touches_border:
            continue
        cleaned[labels == label] = 255
    return cleaned


def _contrast_score(gray: np.ndarray, bbox: tuple[int, int, int, int]) -> float:
    x, y, w, h = bbox
    inner = gray[y : y + h, x : x + w]
    if inner.size == 0:
        return 0.0

    pad = max(2, int(round(min(w, h) * 0.12)))
    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(gray.shape[1], x + w + pad)
    y1 = min(gray.shape[0], y + h + pad)
    if x1 <= x0 or y1 <= y0:
        return 0.0

    ring_mask = np.ones((y1 - y0, x1 - x0), dtype=bool)
    ring_mask[(y - y0) : (y - y0 + h), (x - x0) : (x - x0 + w)] = False
    ring_region = gray[y0:y1, x0:x1][ring_mask]
    if ring_region.size == 0:
        return 0.0

    inner_mean = float(np.mean(inner))
    ring_mean = float(np.mean(ring_region))
    return max(0.0, (ring_mean - inner_mean) / 255.0)


def cluster_positions(values: list[float], tolerance: float) -> list[float]:
    """Cluster 1D coordinates with fixed tolerance."""
    if not values:
        return []

    ordered = sorted(values)
    groups: list[list[float]] = [[ordered[0]]]
    for value in ordered[1:]:
        if abs(value - groups[-1][-1]) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])

    return [float(np.mean(group)) for group in groups]


def detect_openings(rectified_image: np.ndarray, cfg: DetectionConfig | None = None) -> list[Opening]:
    """Detect facade openings while preserving count and position."""
    config = cfg or DetectionConfig()
    height, width = rectified_image.shape[:2]
    image_area = float(height * width)

    gray = cv2.cvtColor(rectified_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    normalized = cv2.equalizeHist(gray)

    adaptive = cv2.adaptiveThreshold(
        normalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,
        7,
    )
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    dark_threshold = float(np.percentile(gray, config.dark_percentile))
    _, dark = cv2.threshold(gray, dark_threshold, 255, cv2.THRESH_BINARY_INV)

    raw_masks = [adaptive, otsu, dark]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5))
    contours: list[np.ndarray] = []
    for raw_mask in raw_masks:
        mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        mask = _remove_border_connected_components(mask)
        found, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours.extend(found)

    candidates: list[Opening] = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        rect_area = float(w * h)
        if rect_area <= 0:
            continue

        if w < width * 0.015 or h < height * 0.04:
            continue
        if w > width * 0.70 or h > height * 0.80:
            continue

        area_ratio = rect_area / image_area
        if area_ratio < config.min_area_ratio or area_ratio > config.max_area_ratio:
            continue

        aspect = float(w) / float(h)
        if aspect < config.min_aspect_ratio or aspect > config.max_aspect_ratio:
            continue

        solidity = area / rect_area
        if solidity < config.min_solidity:
            continue

        contrast = _contrast_score(gray, (x, y, w, h))
        if contrast < config.min_contrast:
            continue

        shape = _shape_from_contour(contour)
        confidence = min(
            0.99,
            0.25 + (solidity * 0.35) + (contrast * 0.35) + (min(area_ratio / 0.03, 1.0) * 0.05),
        )
        candidates.append(
            Opening(
                id=f"opening_{len(candidates) + 1}",
                bbox_px=(float(x), float(y), float(w), float(h)),
                shape=shape,
                confidence=float(confidence),
            )
        )

    filtered = _nms(candidates, config.nms_iou_threshold)
    filtered.sort(key=lambda item: (item.bbox_px[1], item.bbox_px[0]))
    for index, opening in enumerate(filtered, start=1):
        opening.id = f"opening_{index}"
    return filtered


def detect_decorative_bands(rectified_image: np.ndarray) -> list[float]:
    """Detect horizontal decorative bands using texture peaks and edge coverage."""
    gray = cv2.cvtColor(rectified_image, cv2.COLOR_BGR2GRAY)
    height, _ = gray.shape

    laplacian = cv2.Laplacian(gray, cv2.CV_32F)
    texture_energy = np.mean(np.abs(laplacian), axis=1)
    smoothed = cv2.GaussianBlur(texture_energy.reshape(-1, 1), (1, 21), 0).reshape(-1)

    threshold = float(np.mean(smoothed) + np.std(smoothed))
    raw_candidates = np.where(smoothed > threshold)[0].tolist()
    if not raw_candidates:
        return []

    clusters = cluster_positions([float(v) for v in raw_candidates], tolerance=8.0)
    edges = cv2.Canny(gray, 60, 180)
    bands: list[float] = []
    for y_pos in clusters:
        y = int(round(y_pos))
        y0, y1 = max(0, y - 2), min(height, y + 3)
        if y1 <= y0:
            continue
        strip = edges[y0:y1, :]
        if strip.size == 0:
            continue
        horizontal_coverage = float(np.mean(np.any(strip > 0, axis=0)))
        if horizontal_coverage > 0.45:
            bands.append(float(y_pos))

    return bands
