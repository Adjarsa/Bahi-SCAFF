from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, Form, UploadFile
import uvicorn

from facade2d.parsing import parse_corners, parse_reference
from facade2d.pipeline import Facade2DPipeline, PipelineConfig


app = FastAPI(
    title="Facade2D API",
    description="Professional 2D facade generation from smartphone photos.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/process")
async def process_facade(
    image: UploadFile = File(...),
    corners: str | None = Form(default=None),
    reference: str | None = Form(default=None),
    auto_corners: bool = Form(default=True),
    output_dir: str | None = Form(default=None),
    include_svg: bool = Form(default=True),
) -> dict:
    parsed_corners = parse_corners(corners)
    parsed_reference = parse_reference(reference)

    with TemporaryDirectory(prefix="facade2d_") as tmp_dir:
        extension = Path(image.filename or "input.jpg").suffix or ".jpg"
        input_path = Path(tmp_dir) / f"source{extension}"
        input_path.write_bytes(await image.read())

        final_output = Path(output_dir) if output_dir else Path(tmp_dir) / "output"
        pipeline = Facade2DPipeline(PipelineConfig(auto_detect_corners=auto_corners))
        result = pipeline.process(
            image_path=str(input_path),
            output_dir=str(final_output),
            corners=parsed_corners,
            reference=parsed_reference,
        )
        payload = result.to_dict()
        if include_svg and result.svg_path:
            payload["svg"] = Path(result.svg_path).read_text(encoding="utf-8")
        return payload


def run() -> None:
    uvicorn.run("facade2d.api:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
