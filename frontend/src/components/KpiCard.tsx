interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
}

export function KpiCard({ title, value, subtitle }: KpiCardProps) {
  return (
    <article className="card">
      <h3>{title}</h3>
      <p className="kpi-value">{value}</p>
      {subtitle ? <p className="kpi-subtitle">{subtitle}</p> : null}
    </article>
  );
}
