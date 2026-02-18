from __future__ import annotations

import argparse
import json
import sys

from facade2d.parsing import parse_corners, parse_reference
from facade2d.pipeline import Facade2DPipeline, PipelineConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="facade2d",
        description="Generate 2D architectural facades from smartphone photos.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    process_cmd = subparsers.add_parser("process", help="Process one facade photo.")
    process_cmd.add_argument("--input", required=True, help="Path to source image.")
    process_cmd.add_argument("--output", required=True, help="Output directory.")
    process_cmd.add_argument(
        "--corners",
        default=None,
        help='4 facade corners in source image: "x1,y1 x2,y2 x3,y3 x4,y4".',
    )
    process_cmd.add_argument(
        "--reference",
        default=None,
        help='Known metric segment in source image: "x1,y1,x2,y2,length_m".',
    )
    process_cmd.add_argument(
        "--no-auto-corners",
        action="store_true",
        help="Disable automatic corner detection when --corners is missing.",
    )
    return parser


def run_process(args: argparse.Namespace) -> int:
    corners = parse_corners(args.corners)
    reference = parse_reference(args.reference)
    pipeline = Facade2DPipeline(
        PipelineConfig(
            auto_detect_corners=not args.no_auto_corners,
        )
    )
    result = pipeline.process(
        image_path=args.input,
        output_dir=args.output,
        corners=corners,
        reference=reference,
    )
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "process":
            return run_process(args)
        parser.error(f"Unknown command: {args.command}")
    except Exception as exc:  # pragma: no cover - top-level CLI guard
        print(f"[facade2d] error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
