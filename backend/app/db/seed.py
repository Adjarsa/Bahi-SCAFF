from sqlalchemy.orm import Session

from app.models.material import Material

DEFAULT_MATERIALS: list[dict] = [
    {"name": "Montant 2m", "type": "montants", "dimension": "2.00m", "weight_kg": 12.5, "stock_quantity": 200},
    {"name": "Montant 3m", "type": "montants", "dimension": "3.00m", "weight_kg": 18.0, "stock_quantity": 80},
    {"name": "Plateau 3m", "type": "plateaux", "dimension": "3.00m", "weight_kg": 21.0, "stock_quantity": 150},
    {"name": "Plateau 2m", "type": "plateaux", "dimension": "2.00m", "weight_kg": 16.0, "stock_quantity": 120},
    {"name": "Moise 3m", "type": "moises", "dimension": "3.00m", "weight_kg": 11.0, "stock_quantity": 220},
    {"name": "Diagonale 3m", "type": "diagonales", "dimension": "3.00m", "weight_kg": 8.5, "stock_quantity": 140},
    {"name": "Garde-corps 3m", "type": "garde_corps", "dimension": "3.00m", "weight_kg": 7.2, "stock_quantity": 180},
    {"name": "Plinthe 3m", "type": "plinthes", "dimension": "3.00m", "weight_kg": 4.8, "stock_quantity": 180},
    {"name": "Verin reglable", "type": "verins", "dimension": "0.60m", "weight_kg": 5.5, "stock_quantity": 260},
    {"name": "Ancrage", "type": "ancrages", "dimension": "standard", "weight_kg": 1.2, "stock_quantity": 500},
]


def seed_materials(db: Session) -> None:
    existing = db.query(Material).count()
    if existing > 0:
        return
    for material in DEFAULT_MATERIALS:
        db.add(Material(**material))
    db.commit()
