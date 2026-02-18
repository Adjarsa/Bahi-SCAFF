from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

from app.domain.models import Opening, PipelineResult
from app.services.bill_of_materials import BillOfMaterialsService
from app.services.calibration import CalibrationService, KnownMeasurementInput
from app.services.geometry import GeometryReconstructionService
from app.services.image_analysis import ImageAnalysisService
from app.services.perspective import PerspectiveCorrectionService
from app.services.quoting import QuotingService
from app.services.reconstruction3d import Reconstruction3DService
from app.services.scaffolding import ScaffoldingService
from app.services.technical_elevation import TechnicalElevationService


@dataclass
class PipelineInput:
    image_width_px: int
    image_height_px: int
    levels_hint: int
    estimated_story_height_m: float
    terrain_factor: float
    labor_hourly_rate_eur: float
    margin_rate: float
    vat_rate: float
    manual_openings: list[Opening] = field(default_factory=list)
    known_measurement: KnownMeasurementInput | None = None


@dataclass
class PipelineOrchestrator:
    image_analysis: ImageAnalysisService = field(default_factory=ImageAnalysisService)
    perspective: PerspectiveCorrectionService = field(default_factory=PerspectiveCorrectionService)
    calibration: CalibrationService = field(default_factory=CalibrationService)
    geometry: GeometryReconstructionService = field(default_factory=GeometryReconstructionService)
    elevation: TechnicalElevationService = field(default_factory=TechnicalElevationService)
    reconstruction_3d: Reconstruction3DService = field(default_factory=Reconstruction3DService)
    scaffolding: ScaffoldingService = field(default_factory=ScaffoldingService)
    materials: BillOfMaterialsService = field(default_factory=BillOfMaterialsService)
    quoting: QuotingService = field(default_factory=QuotingService)

    def run(self, payload: PipelineInput) -> PipelineResult:
        start = perf_counter()

        features = self.image_analysis.detect(
            image_width_px=payload.image_width_px,
            image_height_px=payload.image_height_px,
            levels_hint=payload.levels_hint,
            manual_openings=payload.manual_openings,
        )
        perspective_result = self.perspective.correct(features)
        calibration_result = self.calibration.calibrate(
            features=features,
            known_measurement=payload.known_measurement,
            estimated_story_height_m=payload.estimated_story_height_m,
        )
        grid = self.geometry.build_grid(features, calibration_result)
        elevation = self.elevation.generate(features, calibration_result, grid)
        mesh = self.reconstruction_3d.reconstruct(features, calibration_result)

        facade_width_m = features.facade_box_px.width / calibration_result.pixels_per_meter
        facade_height_m = features.facade_box_px.height / calibration_result.pixels_per_meter
        plan = self.scaffolding.compute_plan(
            facade_width_m=facade_width_m,
            facade_height_m=facade_height_m,
            terrain_factor=payload.terrain_factor,
        )
        material_lines = self.materials.compute(plan, facade_width_m=facade_width_m)
        quote = self.quoting.compute(
            materials=material_lines,
            facade_area_m2=facade_width_m * facade_height_m,
            labor_hourly_rate_eur=payload.labor_hourly_rate_eur,
            margin_rate=payload.margin_rate,
            vat_rate=payload.vat_rate,
            terrain_factor=payload.terrain_factor,
        )

        runtime_ms = int((perf_counter() - start) * 1000)
        assumptions = [
            "Le mode de detection actuel combine heuristiques et corrections operateur.",
            "Le modele geometrique privilegie la regularite structurelle pour fiabiliser le calepinage.",
            "Les couts unitaires proviennent d'une grille interne parametree.",
        ]

        return PipelineResult(
            features=features,
            perspective=perspective_result,
            calibration=calibration_result,
            grid=grid,
            elevation=elevation,
            mesh=mesh,
            scaffolding=plan,
            material_lines=material_lines,
            quote=quote,
            runtime_ms=runtime_ms,
            assumptions=assumptions,
        )
