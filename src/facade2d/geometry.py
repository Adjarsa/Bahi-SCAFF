from __future__ import annotations

import math

import cv2
import numpy as np


def order_points(points: np.ndarray) -> np.ndarray:
    """Order 4 points as top-left, top-right, bottom-right, bottom-left."""
    pts = np.asarray(points, dtype=np.float32)
    if pts.shape != (4, 2):
        raise ValueError("Exactly 4 points are required.")

    sums = pts.sum(axis=1)
    diffs = np.diff(pts, axis=1).flatten()

    top_left = pts[np.argmin(sums)]
    bottom_right = pts[np.argmax(sums)]
    top_right = pts[np.argmin(diffs)]
    bottom_left = pts[np.argmax(diffs)]
    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)


def auto_detect_facade_corners(image: np.ndarray) -> np.ndarray:
    """Detect the dominant quadrilateral likely representing the facade."""
    if image is None or image.size == 0:
        raise ValueError("Invalid input image.")

    height, width = image.shape[:2]
    image_area = float(height * width)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 60, 180)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < image_area * 0.15:
            continue
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:
            return order_points(approx.reshape(4, 2))

    return np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype=np.float32,
    )


def rectify_facade(image: np.ndarray, corners: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Apply perspective warp to obtain a fronto-parallel facade image."""
    ordered = order_points(corners)
    tl, tr, br, bl = ordered

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(round(width_a)), int(round(width_b)))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(round(height_a)), int(round(height_b)))

    max_width = max(1, max_width)
    max_height = max(1, max_height)

    destination = np.array(
        [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
        dtype=np.float32,
    )
    homography = cv2.getPerspectiveTransform(ordered, destination)
    rectified = cv2.warpPerspective(image, homography, (max_width, max_height))
    return rectified, homography


def transform_points(points: list[tuple[float, float]], homography: np.ndarray) -> list[tuple[float, float]]:
    """Project points using homography."""
    pts = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    transformed = cv2.perspectiveTransform(pts, homography).reshape(-1, 2)
    return [(float(p[0]), float(p[1])) for p in transformed]


def pixels_per_meter(p1: tuple[float, float], p2: tuple[float, float], real_length_m: float) -> float:
    """Compute pixels/meter from a known-length segment."""
    if real_length_m <= 0:
        raise ValueError("Real length must be > 0.")
    px_distance = math.dist(p1, p2)
    if px_distance <= 0:
        raise ValueError("Reference points must be distinct.")
    return px_distance / real_length_m
