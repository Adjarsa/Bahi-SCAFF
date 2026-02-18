from __future__ import annotations

from dataclasses import dataclass

from app.domain.models import MaterialLine, QuoteSummary


@dataclass
class QuotingService:
    """Calcul financier chantier: materiel, MO, marge, TVA."""

    unit_prices_eur: dict[str, float] | None = None

    def __post_init__(self) -> None:
        if self.unit_prices_eur is None:
            self.unit_prices_eur = {
                "MNT": 22.0,
                "PLT": 18.0,
                "DIA": 19.0,
                "GDC": 9.5,
                "PLI": 4.5,
                "ANC": 14.0,
            }

    def compute(
        self,
        materials: list[MaterialLine],
        facade_area_m2: float,
        labor_hourly_rate_eur: float,
        margin_rate: float,
        vat_rate: float,
        terrain_factor: float,
    ) -> QuoteSummary:
        material_cost = 0.0
        for line in materials:
            unit_price = self.unit_prices_eur.get(line.code, 0.0)
            material_cost += unit_price * line.quantity

        estimated_hours = max(4.0, facade_area_m2 / 12.0) * terrain_factor
        labor_cost = estimated_hours * labor_hourly_rate_eur

        subtotal = material_cost + labor_cost
        margin = subtotal * margin_rate
        before_vat = subtotal + margin
        vat = before_vat * vat_rate
        total = before_vat + vat

        return QuoteSummary(
            material_cost_eur=round(material_cost, 2),
            labor_cost_eur=round(labor_cost, 2),
            margin_eur=round(margin, 2),
            vat_eur=round(vat, 2),
            total_eur=round(total, 2),
            estimated_hours=round(estimated_hours, 2),
        )
