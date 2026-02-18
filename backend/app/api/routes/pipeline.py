from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path

from app.domain.models import BoundingBox, Opening
from app.schemas.pipeline import (
    MaterialLineOutput,
    PipelineRequest,
    PipelineResponse,
    QuoteOutput,
    ScaffoldingBayOutput,
)
from app.services.calibration import KnownMeasurementInput
from app.services.orchestration import PipelineInput, PipelineOrchestrator
from app.services.technical_elevation import TechnicalElevationService

router = APIRouter(tags=["pipeline"])
orchestrator = PipelineOrchestrator()
elevation_exporter = TechnicalElevationService()


def _map_manual_openings(request: PipelineRequest) -> list[Opening]:
    return [
        Opening(
            kind=opening.kind,
            box=BoundingBox(
                x_min=opening.x_min_px,
                y_min=opening.y_min_px,
                x_max=opening.x_max_px,
                y_max=opening.y_max_px,
            ),
        )
        for opening in request.manual_openings
    ]


@router.post("/pipeline/run", response_model=PipelineResponse)
def run_pipeline(request: PipelineRequest) -> PipelineResponse:
    known_measurement = None
    if request.known_measurement is not None:
        known_measurement = KnownMeasurementInput(
            pixel_span=request.known_measurement.pixel_span,
            meter_span=request.known_measurement.meter_span,
        )

    pipeline_input = PipelineInput(
        image_width_px=request.image_width_px,
        image_height_px=request.image_height_px,
        levels_hint=request.levels_hint,
        estimated_story_height_m=request.estimated_story_height_m,
        terrain_factor=request.terrain_factor,
        labor_hourly_rate_eur=request.labor_hourly_rate_eur,
        margin_rate=request.margin_rate,
        vat_rate=request.vat_rate,
        manual_openings=_map_manual_openings(request),
        known_measurement=known_measurement,
    )

    result = orchestrator.run(pipeline_input)
    facade_width_m = result.features.facade_box_px.width / result.calibration.pixels_per_meter
    facade_height_m = result.features.facade_box_px.height / result.calibration.pixels_per_meter

    bays = [
        ScaffoldingBayOutput(
            bay_index=bay.bay_index,
            x_start_m=bay.x_start_m,
            x_end_m=bay.x_end_m,
            levels_m=bay.levels_m,
            width_m=bay.width_m,
        )
        for bay in result.scaffolding.bays
    ]
    materials = [
        MaterialLineOutput(
            code=line.code,
            label=line.label,
            quantity=line.quantity,
            unit=line.unit,
        )
        for line in result.material_lines
    ]
    quote = result.quote
    if quote is None:
        raise HTTPException(status_code=500, detail="Devis non genere.")

    return PipelineResponse(
        facade_width_m=round(facade_width_m, 3),
        facade_height_m=round(facade_height_m, 3),
        calibration_method=result.calibration.method,
        calibration_confidence=result.calibration.confidence,
        scaffolding_bays=bays,
        compliance_notes=result.scaffolding.compliance_notes + result.features.warnings,
        materials=materials,
        quote=QuoteOutput(
            material_cost_eur=quote.material_cost_eur,
            labor_cost_eur=quote.labor_cost_eur,
            margin_eur=quote.margin_eur,
            vat_eur=quote.vat_eur,
            total_eur=quote.total_eur,
            estimated_hours=quote.estimated_hours,
        ),
        runtime_ms=result.runtime_ms,
        assumptions=result.assumptions,
    )


@router.post("/pipeline/export/{export_format}")
def export_pipeline(
    request: PipelineRequest,
    export_format: str = Path(pattern="^(svg|dxf|pdf|obj|glb|ifc)$"),
) -> dict[str, str]:
    result = orchestrator.run(
        PipelineInput(
            image_width_px=request.image_width_px,
            image_height_px=request.image_height_px,
            levels_hint=request.levels_hint,
            estimated_story_height_m=request.estimated_story_height_m,
            terrain_factor=request.terrain_factor,
            labor_hourly_rate_eur=request.labor_hourly_rate_eur,
            margin_rate=request.margin_rate,
            vat_rate=request.vat_rate,
            manual_openings=_map_manual_openings(request),
            known_measurement=(
                KnownMeasurementInput(
                    pixel_span=request.known_measurement.pixel_span,
                    meter_span=request.known_measurement.meter_span,
                )
                if request.known_measurement
                else None
            ),
        )
    )

    if export_format in {"svg", "dxf", "pdf"}:
        width_m = result.features.facade_box_px.width / result.calibration.pixels_per_meter
        height_m = result.features.facade_box_px.height / result.calibration.pixels_per_meter
        if export_format == "svg":
            content = elevation_exporter.export_svg(result.elevation, width_m=width_m, height_m=height_m)
        elif export_format == "dxf":
            content = elevation_exporter.export_dxf(result.elevation)
        else:
            content = elevation_exporter.export_pdf_stub(result.elevation)
        return {"format": export_format, "content": content}

    mesh_path = result.mesh.export_paths.get(export_format)
    if mesh_path is None:
        raise HTTPException(status_code=400, detail="Format 3D non supporte.")
    return {"format": export_format, "path": mesh_path}
