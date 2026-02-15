from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.project import GenerationRun, Project
from app.schemas.generation import ScaffoldGenerationRequest, ScaffoldGenerationResponse
from app.services.scaffold_generator import generate_scaffold_plan

router = APIRouter(prefix="/projects", tags=["generation"])


@router.post("/{project_id}/generate", response_model=ScaffoldGenerationResponse)
def generate_for_project(
    project_id: str,
    payload: ScaffoldGenerationRequest,
    db: Session = Depends(get_db),
) -> ScaffoldGenerationResponse:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")

    detection = (project.facade_data or {}).get("detection", {})
    facade_width = float(detection.get("width_m", 12.0))
    facade_height = float(detection.get("height_m", 10.0))
    calibration_confidence = float((project.calibration_data or {}).get("confidence", 0.5))

    result = generate_scaffold_plan(
        db=db,
        facade_width_m=facade_width,
        facade_height_m=facade_height,
        calibration_confidence=calibration_confidence,
        req=payload,
    )

    result_data = result.model_dump()
    run = GenerationRun(project_id=project.id, parameters=payload.model_dump(), result=result_data)
    project.generation_result = result_data
    project.status = "planned"
    db.add(run)
    db.add(project)
    db.commit()
    return result


@router.get("/{project_id}/quantitatif")
def get_quantitatif(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    if not project.generation_result:
        raise HTTPException(status_code=400, detail="Aucune generation disponible pour ce projet.")
    generation = project.generation_result
    return {
        "project_id": project.id,
        "quantities": generation.get("quantities", []),
        "total_weight_kg": generation.get("total_weight_kg", 0),
        "total_volume_m3": generation.get("total_volume_m3", 0),
        "stock_sufficient": generation.get("stock_sufficient", False),
    }


@router.get("/{project_id}/conformity")
def get_conformity(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    generation = project.generation_result or {}
    return {
        "project_id": project.id,
        "confidence": generation.get("confidence", 0),
        "requires_confirmation": generation.get("requires_confirmation", True),
        "warnings": generation.get("warnings", []),
    }
