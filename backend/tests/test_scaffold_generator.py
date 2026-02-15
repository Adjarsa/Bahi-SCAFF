from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.material import Material
from app.schemas.generation import ScaffoldGenerationRequest
from app.services.scaffold_generator import _best_bay_layout, generate_scaffold_plan


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    maker = sessionmaker(bind=engine)
    db = maker()
    db.add_all(
        [
            Material(name="Montant", type="montants", dimension="2m", weight_kg=12.0, stock_quantity=300),
            Material(name="Plateau", type="plateaux", dimension="3m", weight_kg=22.0, stock_quantity=300),
            Material(name="Moise", type="moises", dimension="3m", weight_kg=11.0, stock_quantity=300),
            Material(name="Ancrage", type="ancrages", dimension="std", weight_kg=1.0, stock_quantity=300),
        ]
    )
    db.commit()
    return db


def test_best_bay_layout_covers_width() -> None:
    layout = _best_bay_layout(14.2, [0.73, 1.09, 1.57, 2.07, 2.57, 3.07])
    assert sum(layout) >= 14.2
    assert all(width > 0 for width in layout)


def test_generation_response_includes_quantities_and_warnings() -> None:
    db = _session()
    req = ScaffoldGenerationRequest(load_class=5, bay_width_m=3.0, level_height_m=2.0)
    response = generate_scaffold_plan(
        db=db,
        facade_width_m=18.0,
        facade_height_m=12.0,
        calibration_confidence=0.95,
        req=req,
    )
    assert response.levels >= 1
    assert len(response.quantities) > 0
    assert response.total_weight_kg >= 0
    assert any(item.code.startswith("R408") for item in response.warnings)
