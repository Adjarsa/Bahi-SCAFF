from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.project import Project
from app.services.export_service import (
    export_conformity_report,
    export_delivery_note,
    export_quantitative_excel,
    export_technical_pdf,
)

router = APIRouter(prefix="/projects", tags=["exports"])


def _project_and_generation(project_id: str, db: Session) -> tuple[dict, dict]:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    generation = project.generation_result or {}
    if not generation:
        raise HTTPException(status_code=400, detail="Generation requise avant export.")
    project_data = {"id": project.id, "name": project.name}
    return project_data, generation


@router.get("/{project_id}/exports/pdf")
def export_pdf(project_id: str, db: Session = Depends(get_db)) -> FileResponse:
    project, generation = _project_and_generation(project_id, db)
    path = export_technical_pdf(project, generation)
    return FileResponse(path, filename="plan-technique.pdf", media_type="application/pdf")


@router.get("/{project_id}/exports/excel")
def export_excel(project_id: str, db: Session = Depends(get_db)) -> FileResponse:
    project, generation = _project_and_generation(project_id, db)
    path = export_quantitative_excel(project, generation)
    return FileResponse(
        path,
        filename="quantitatif.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/{project_id}/exports/bon-sortie")
def export_bon_sortie(project_id: str, db: Session = Depends(get_db)) -> FileResponse:
    project, generation = _project_and_generation(project_id, db)
    path = export_delivery_note(project, generation)
    return FileResponse(path, filename="bon-sortie.csv", media_type="text/csv")


@router.get("/{project_id}/exports/conformite")
def export_conformity(project_id: str, db: Session = Depends(get_db)) -> FileResponse:
    project, generation = _project_and_generation(project_id, db)
    path = export_conformity_report(project, generation)
    return FileResponse(path, filename="rapport-conformite.pdf", media_type="application/pdf")
