from pydantic import BaseModel


class DashboardStats(BaseModel):
    active_projects: int
    ongoing_sites: int
    monthly_material_usage: int
    stock_utilization_rate: float
    profitability_estimate: float
