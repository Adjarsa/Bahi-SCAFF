import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension: Mapped[str] = mapped_column(String(100), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    compatibility: Mapped[str] = mapped_column(Text, default="universel")
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    condition: Mapped[str] = mapped_column(String(50), default="bon")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
