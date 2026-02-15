from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_materials
from app.db.session import engine


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)
    seed_materials(db)
