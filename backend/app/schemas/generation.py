from pydantic import BaseModel, Field


class ScaffoldGenerationRequest(BaseModel):
    scaffold_type: str = "facade"
    bay_width_m: float = Field(default=3.0, gt=0)
    level_height_m: float = Field(default=2.0, gt=0)
    upright_spacing_m: float = Field(default=3.0, gt=0)
    number_of_levels: int | None = Field(default=None, ge=1)
    load_class: int = Field(default=3, ge=1, le=6)
    has_stair_tower: bool = False
    access_mode: str = "trappe"
    has_consoles: bool = False
    has_nets: bool = False
    has_pedestrian_protection: bool = False
    optimize_stock: bool = True
    available_module_widths_m: list[float] = Field(default_factory=lambda: [0.73, 1.09, 1.57, 2.07, 2.57, 3.07])


class MaterialLine(BaseModel):
    type: str
    quantity: int
    unit_weight_kg: float
    total_weight_kg: float
    in_stock: int
    shortage: int


class GenerationWarning(BaseModel):
    code: str
    severity: str
    message: str


class ScaffoldGenerationResponse(BaseModel):
    facade_width_m: float
    facade_height_m: float
    levels: int
    bay_layout_m: list[float]
    quantities: list[MaterialLine]
    total_weight_kg: float
    total_volume_m3: float
    stock_sufficient: bool
    warnings: list[GenerationWarning]
    confidence: float = Field(ge=0, le=1)
    requires_confirmation: bool = False
