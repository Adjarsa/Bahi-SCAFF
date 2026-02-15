import { FormEvent, useEffect, useMemo, useState } from "react";
import { apiClient } from "../api/client";
import { ThreeScaffoldView } from "../components/ThreeScaffoldView";
import { GenerationRequest, GenerationResponse, Project } from "../types";

const defaultRequest: GenerationRequest = {
  scaffold_type: "facade",
  bay_width_m: 3,
  level_height_m: 2,
  upright_spacing_m: 3,
  number_of_levels: 4,
  load_class: 3,
  has_stair_tower: false,
  access_mode: "trappe",
  has_consoles: false,
  has_nets: true,
  has_pedestrian_protection: true,
  optimize_stock: true,
  available_module_widths_m: [0.73, 1.09, 1.57, 2.07, 2.57, 3.07],
};

export function GenerationPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState("");
  const [form, setForm] = useState<GenerationRequest>(defaultRequest);
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    apiClient
      .listProjects()
      .then((rows) => {
        setProjects(rows);
        if (rows.length > 0) {
          setProjectId(rows[0].id);
        }
      })
      .catch(() => setMessage("Impossible de recuperer la liste de projets."));
  }, []);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectId) {
      setMessage("Selectionnez un projet.");
      return;
    }
    try {
      const data = await apiClient.generateScaffold(projectId, form);
      setResult(data);
      setMessage("Generation terminee.");
    } catch {
      setMessage("Generation impossible. Verifiez vos donnees.");
    }
  };

  const canExport = useMemo(() => Boolean(projectId && result), [projectId, result]);

  return (
    <section className="page-stack">
      <article className="card">
        <h2>Generation echafaudage</h2>
        <form className="form-grid two-cols" onSubmit={onSubmit}>
          <label>
            Projet
            <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
              {projects.map((project) => (
                <option value={project.id} key={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Type echafaudage
            <input
              value={form.scaffold_type}
              onChange={(e) => setForm({ ...form, scaffold_type: e.target.value })}
            />
          </label>
          <label>
            Largeur traves (m)
            <input
              type="number"
              step="0.1"
              value={form.bay_width_m}
              onChange={(e) => setForm({ ...form, bay_width_m: Number(e.target.value) })}
            />
          </label>
          <label>
            Hauteur niveau (m)
            <input
              type="number"
              step="0.1"
              value={form.level_height_m}
              onChange={(e) => setForm({ ...form, level_height_m: Number(e.target.value) })}
            />
          </label>
          <label>
            Nombre niveaux
            <input
              type="number"
              value={form.number_of_levels}
              onChange={(e) => setForm({ ...form, number_of_levels: Number(e.target.value) })}
            />
          </label>
          <label>
            Classe charge
            <input
              type="number"
              min="1"
              max="6"
              value={form.load_class}
              onChange={(e) => setForm({ ...form, load_class: Number(e.target.value) })}
            />
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.has_stair_tower}
              onChange={(e) => setForm({ ...form, has_stair_tower: e.target.checked })}
            />
            Presence escalier
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.has_consoles}
              onChange={(e) => setForm({ ...form, has_consoles: e.target.checked })}
            />
            Consoles
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.has_nets}
              onChange={(e) => setForm({ ...form, has_nets: e.target.checked })}
            />
            Baches / filets
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.has_pedestrian_protection}
              onChange={(e) => setForm({ ...form, has_pedestrian_protection: e.target.checked })}
            />
            Protection pietons
          </label>
          <button type="submit">Lancer la generation</button>
        </form>
        {message ? <p>{message}</p> : null}
      </article>

      {result ? (
        <>
          <article className="card">
            <h2>Resultat generation</h2>
            <p>
              Facade: {result.facade_width_m}m x {result.facade_height_m}m | Niveaux: {result.levels} | Confiance:{" "}
              {(result.confidence * 100).toFixed(0)}%
            </p>
            <p>
              Stock suffisant: <strong>{result.stock_sufficient ? "Oui" : "Non"}</strong> | Poids total:{" "}
              {result.total_weight_kg} kg | Volume camion: {result.total_volume_m3} m3
            </p>
            {canExport ? (
              <div className="exports">
                <a href={apiClient.exportUrl(projectId, "pdf")} target="_blank" rel="noreferrer">
                  Export PDF technique
                </a>
                <a href={apiClient.exportUrl(projectId, "excel")} target="_blank" rel="noreferrer">
                  Export Excel quantitatif
                </a>
                <a href={apiClient.exportUrl(projectId, "bon-sortie")} target="_blank" rel="noreferrer">
                  Bon sortie depot
                </a>
                <a href={apiClient.exportUrl(projectId, "conformite")} target="_blank" rel="noreferrer">
                  Rapport conformite
                </a>
              </div>
            ) : null}
          </article>

          <article className="card">
            <h2>Visualisation 3D</h2>
            <ThreeScaffoldView bayLayout={result.bay_layout_m} levels={result.levels} />
          </article>

          <article className="card">
            <h2>Quantitatif materiel</h2>
            <table>
              <thead>
                <tr>
                  <th>Piece</th>
                  <th>Quantite</th>
                  <th>Stock</th>
                  <th>Manque</th>
                  <th>Poids total (kg)</th>
                </tr>
              </thead>
              <tbody>
                {result.quantities.map((line) => (
                  <tr key={line.type}>
                    <td>{line.type}</td>
                    <td>{line.quantity}</td>
                    <td>{line.in_stock}</td>
                    <td>{line.shortage}</td>
                    <td>{line.total_weight_kg}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <article className="card">
            <h2>Avertissements securite</h2>
            {result.warnings.length === 0 ? (
              <p>Aucun avertissement.</p>
            ) : (
              <ul>
                {result.warnings.map((warning) => (
                  <li key={`${warning.code}-${warning.message}`}>
                    <strong>[{warning.severity.toUpperCase()}]</strong> {warning.code} - {warning.message}
                  </li>
                ))}
              </ul>
            )}
          </article>
        </>
      ) : null}
    </section>
  );
}
