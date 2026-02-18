from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import cv2
import numpy as np

from facade2d.pipeline import Facade2DPipeline, PipelineConfig


class TestFacade2DPipelineSynthetic(unittest.TestCase):
    def _build_synthetic_source(self) -> tuple[np.ndarray, list[tuple[float, float]], tuple[tuple[float, float], tuple[float, float], float]]:
        rect_h, rect_w = 700, 360
        rectified = np.full((rect_h, rect_w, 3), 230, dtype=np.uint8)

        # Main facade contour
        cv2.rectangle(rectified, (8, 8), (rect_w - 8, rect_h - 8), (180, 180, 180), 4)

        # Decorative belt
        cv2.line(rectified, (0, 500), (rect_w - 1, 500), (150, 150, 150), 5)

        # 6 windows + 1 door
        windows = [
            (60, 80, 80, 110),
            (220, 80, 80, 110),
            (60, 230, 80, 110),
            (220, 230, 80, 110),
            (60, 380, 80, 110),
            (220, 380, 80, 110),
            (140, 520, 90, 150),  # door
        ]
        for x, y, w, h in windows:
            cv2.rectangle(rectified, (x, y), (x + w, y + h), (45, 45, 45), -1)

        src_h, src_w = 820, 560
        src = np.full((src_h, src_w, 3), 235, dtype=np.uint8)
        src_pts = np.array(
            [[0, 0], [rect_w - 1, 0], [rect_w - 1, rect_h - 1], [0, rect_h - 1]],
            dtype=np.float32,
        )
        dst_pts = np.array(
            [[90, 40], [430, 20], [510, 790], [35, 800]],
            dtype=np.float32,
        )
        perspective = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(rectified, perspective, (src_w, src_h), dst=src, borderMode=cv2.BORDER_TRANSPARENT)

        # Reference segment: door width = 1.00 m (known measure)
        door_left_rect = np.array([[[140.0, 660.0]]], dtype=np.float32)
        door_right_rect = np.array([[[230.0, 660.0]]], dtype=np.float32)
        door_left_src = cv2.perspectiveTransform(door_left_rect, perspective).reshape(2)
        door_right_src = cv2.perspectiveTransform(door_right_rect, perspective).reshape(2)
        reference = (
            (float(door_left_src[0]), float(door_left_src[1])),
            (float(door_right_src[0]), float(door_right_src[1])),
            1.0,
        )
        corners = [(float(x), float(y)) for x, y in dst_pts.tolist()]
        return warped, corners, reference

    def test_process_preserves_openings_and_scale(self) -> None:
        source, corners, reference = self._build_synthetic_source()

        with TemporaryDirectory(prefix="facade2d_test_") as tmp_dir:
            input_path = Path(tmp_dir) / "source.jpg"
            output_dir = Path(tmp_dir) / "out"
            cv2.imwrite(str(input_path), source)

            pipeline = Facade2DPipeline(PipelineConfig(auto_detect_corners=False))
            result = pipeline.process(
                image_path=str(input_path),
                output_dir=str(output_dir),
                corners=corners,
                reference=reference,
            )

            self.assertGreaterEqual(len(result.openings), 7)
            self.assertLessEqual(len(result.openings), 10)
            self.assertIsNotNone(result.metrics.pixels_per_meter)
            self.assertGreater(result.metrics.pixels_per_meter or 0.0, 40.0)

            self.assertTrue(Path(result.rectified_image or "").exists())
            self.assertTrue(Path(result.overlay_image or "").exists())
            self.assertTrue(Path(result.svg_path or "").exists())
            self.assertTrue(Path(result.json_path or "").exists())


if __name__ == "__main__":
    unittest.main()
