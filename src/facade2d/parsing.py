from __future__ import annotations


def parse_corners(text: str | None) -> list[tuple[float, float]] | None:
    """
    Parse corners from:
      "x1,y1 x2,y2 x3,y3 x4,y4"
    """
    if not text:
        return None
    points: list[tuple[float, float]] = []
    for chunk in text.split():
        x_str, y_str = chunk.split(",", maxsplit=1)
        points.append((float(x_str), float(y_str)))
    if len(points) != 4:
        raise ValueError("Exactly 4 corner points are required.")
    return points


def parse_reference(text: str | None) -> tuple[tuple[float, float], tuple[float, float], float] | None:
    """
    Parse metric reference from:
      "x1,y1,x2,y2,length_m"
    """
    if not text:
        return None
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 5:
        raise ValueError("Reference must be x1,y1,x2,y2,length_m.")
    x1, y1, x2, y2, length_m = (float(part) for part in parts)
    return (x1, y1), (x2, y2), length_m
