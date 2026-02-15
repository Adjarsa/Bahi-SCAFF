from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialRead, MaterialUpdate

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("", response_model=list[MaterialRead])
def list_materials(db: Session = Depends(get_db)) -> list[Material]:
    return db.query(Material).order_by(Material.type.asc(), Material.name.asc()).all()


@router.post("", response_model=MaterialRead)
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)) -> Material:
    material = Material(**payload.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.post("/import", response_model=list[MaterialRead])
def bulk_import_materials(payload: list[MaterialCreate], db: Session = Depends(get_db)) -> list[Material]:
    created: list[Material] = []
    for item in payload:
        material = Material(**item.model_dump())
        db.add(material)
        created.append(material)
    db.commit()
    for item in created:
        db.refresh(item)
    return created


@router.patch("/{material_id}", response_model=MaterialRead)
def update_material(material_id: str, payload: MaterialUpdate, db: Session = Depends(get_db)) -> Material:
    material = db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Materiel introuvable.")
    updates = payload.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(material, key, value)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material
