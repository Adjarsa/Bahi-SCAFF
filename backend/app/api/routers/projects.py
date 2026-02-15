from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.project import Project
from app.schemas.project import (
    CalibrationRequest,
    CalibrationResult,
    FacadeDetection,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from app.services.calibration import calibrate_facade
from app.services.facade_processing import detect_facade_features, save_facade_files

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")

    updates = payload.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(project, key, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/facade/import", response_model=FacadeDetection)
async def import_facade_files(
    project_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> FacadeDetection:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")

    saved_paths = await save_facade_files(project_id, files)
    detection = detect_facade_features(saved_paths)
    project.facade_data = {"files": saved_paths, "detection": detection}
    db.add(project)
    db.commit()
    db.refresh(project)
    return FacadeDetection(**detection)


@router.post("/{project_id}/calibration", response_model=CalibrationResult)
def calibrate_project_facade(
    project_id: str,
    payload: CalibrationRequest,
    db: Session = Depends(get_db),
) -> CalibrationResult:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    detection = (project.facade_data or {}).get("detection", {})
    result = calibrate_facade(payload, detection)
    project.calibration_data = result.model_dump()
    db.add(project)
    db.commit()
    return result
