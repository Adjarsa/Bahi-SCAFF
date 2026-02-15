from pydantic import BaseModel, ConfigDict, Field


class MaterialBase(BaseModel):
    name: str = Field(..., min_length=2)
    type: str
    dimension: str
    weight_kg: float = Field(default=0, ge=0)
    compatibility: str = "universel"
    stock_quantity: int = Field(default=0, ge=0)
    condition: str = "bon"


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    stock_quantity: int | None = Field(default=None, ge=0)
    condition: str | None = None


class MaterialRead(MaterialBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
