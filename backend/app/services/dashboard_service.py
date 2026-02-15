from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.project import Project
from app.schemas.dashboard import DashboardStats


def compute_dashboard_stats(db: Session) -> DashboardStats:
    projects = db.query(Project).all()
    materials = db.query(Material).all()

    active_projects = sum(1 for project in projects if project.status not in {"archived", "done"})
    ongoing_sites = sum(1 for project in projects if project.status in {"in_progress", "planned"})

    monthly_material_usage = 0
    required_total = 0
    for project in projects:
        result = project.generation_result or {}
        for line in result.get("quantities", []):
            monthly_material_usage += int(line.get("quantity", 0))
            required_total += int(line.get("quantity", 0))

    total_stock = sum(material.stock_quantity for material in materials)
    stock_utilization_rate = round((required_total / total_stock) * 100.0, 2) if total_stock else 0.0

    profitability_estimate = round((monthly_material_usage * 4.5) - (monthly_material_usage * 1.8), 2)

    return DashboardStats(
        active_projects=active_projects,
        ongoing_sites=ongoing_sites,
        monthly_material_usage=monthly_material_usage,
        stock_utilization_rate=stock_utilization_rate,
        profitability_estimate=profitability_estimate,
    )
