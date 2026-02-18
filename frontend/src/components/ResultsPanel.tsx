import type { PipelineResponse } from "../types";

interface ResultsPanelProps {
  response: PipelineResponse | null;
  error: string | null;
  onExport: (format: "svg" | "dxf" | "pdf" | "obj" | "glb" | "ifc") => void;
}

export function ResultsPanel({ response, error, onExport }: ResultsPanelProps): JSX.Element {
  return (
    <section className="panel">
      <h2>Resultats techniques</h2>

      <div className="export-actions">
        <button onClick={() => onExport("svg")}>Export SVG</button>
        <button onClick={() => onExport("dxf")}>Export DXF</button>
        <button onClick={() => onExport("pdf")}>Export PDF</button>
        <button onClick={() => onExport("obj")}>Export OBJ</button>
        <button onClick={() => onExport("glb")}>Export GLB</button>
        <button onClick={() => onExport("ifc")}>Export IFC</button>
      </div>

      {error ? <p className="error">{error}</p> : null}

      {!response ? (
        <p>Aucun calcul lance.</p>
      ) : (
        <>
          <div className="kpis">
            <div>
              <strong>Facade</strong>
              <p>
                {response.facade_width_m.toFixed(2)}m x {response.facade_height_m.toFixed(2)}m
              </p>
            </div>
            <div>
              <strong>Calibration</strong>
              <p>
                {response.calibration_method} ({(response.calibration_confidence * 100).toFixed(0)}%)
              </p>
            </div>
            <div>
              <strong>Runtime</strong>
              <p>{response.runtime_ms} ms</p>
            </div>
          </div>

          <h3>Travees echafaudage</h3>
          <ul>
            {response.scaffolding_bays.map((bay) => (
              <li key={bay.bay_index}>
                T{bay.bay_index}: {bay.width_m.toFixed(2)}m ({bay.levels_m.length} niveaux)
              </li>
            ))}
          </ul>

          <h3>Quantitatif materiel</h3>
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Designation</th>
                <th>Quantite</th>
                <th>Unite</th>
              </tr>
            </thead>
            <tbody>
              {response.materials.map((line) => (
                <tr key={line.code}>
                  <td>{line.code}</td>
                  <td>{line.label}</td>
                  <td>{line.quantity}</td>
                  <td>{line.unit}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3>Devis</h3>
          <ul>
            <li>Materiel: {response.quote.material_cost_eur.toFixed(2)} EUR</li>
            <li>Main-d'oeuvre: {response.quote.labor_cost_eur.toFixed(2)} EUR</li>
            <li>Marge: {response.quote.margin_eur.toFixed(2)} EUR</li>
            <li>TVA: {response.quote.vat_eur.toFixed(2)} EUR</li>
            <li>
              <strong>Total: {response.quote.total_eur.toFixed(2)} EUR</strong>
            </li>
          </ul>

          <h3>Conformite et hypotheses</h3>
          <ul>
            {response.compliance_notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
            {response.assumptions.map((assumption) => (
              <li key={assumption}>{assumption}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
