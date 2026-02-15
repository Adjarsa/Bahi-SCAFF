import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { KpiCard } from "../components/KpiCard";
import { DashboardStats } from "../types";

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient
      .getDashboardStats()
      .then(setStats)
      .catch(() => setError("Impossible de charger les statistiques."));
  }, []);

  if (error) {
    return <div className="card">{error}</div>;
  }

  if (!stats) {
    return <div className="card">Chargement du dashboard...</div>;
  }

  return (
    <section className="page-grid">
      <KpiCard title="Projets actifs" value={stats.active_projects} />
      <KpiCard title="Chantiers en cours" value={stats.ongoing_sites} />
      <KpiCard title="Materiel utilise (mois)" value={stats.monthly_material_usage} />
      <KpiCard title="Taux utilisation stock" value={`${stats.stock_utilization_rate}%`} />
      <KpiCard title="Rentabilite estimee" value={`${stats.profitability_estimate.toFixed(2)} EUR`} />
    </section>
  );
}
