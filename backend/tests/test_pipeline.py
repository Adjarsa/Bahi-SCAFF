from app.domain.models import BoundingBox, Opening
from app.services.calibration import KnownMeasurementInput
from app.services.orchestration import PipelineInput, PipelineOrchestrator


def test_pipeline_produces_materials_and_quote() -> None:
    orchestrator = PipelineOrchestrator()
    payload = PipelineInput(
        image_width_px=2400,
        image_height_px=1600,
        levels_hint=4,
        estimated_story_height_m=3.0,
        terrain_factor=1.1,
        labor_hourly_rate_eur=58.0,
        margin_rate=0.18,
        vat_rate=0.2,
        known_measurement=KnownMeasurementInput(pixel_span=600.0, meter_span=3.0),
        manual_openings=[
            Opening(
                kind="window",
                box=BoundingBox(
                    x_min=700,
                    y_min=500,
                    x_max=920,
                    y_max=760,
                ),
            )
        ],
    )

    result = orchestrator.run(payload)

    assert result.calibration.method == "manual_reference"
    assert result.scaffolding.bay_count >= 1
    assert result.material_lines
    assert result.quote is not None
    assert result.quote.total_eur > result.quote.material_cost_eur
