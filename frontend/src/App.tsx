import { useState } from "react";
import { FacadeCanvas } from "./components/FacadeCanvas";
import { MeasurementPanel } from "./components/MeasurementPanel";
import { ResultsPanel } from "./components/ResultsPanel";
import { exportPipeline, runPipeline } from "./services/api";
import type { PipelineRequest, PipelineResponse } from "./types";

const initialRequest: PipelineRequest = {
  image_width_px: 2400,
  image_height_px: 1600,
  levels_hint: 4,
  manual_openings: [],
  estimated_story_height_m: 3,
  terrain_factor: 1,
  labor_hourly_rate_eur: 55,
  margin_rate: 0.15,
  vat_rate: 0.2
};

function downloadTextFile(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export default function App(): JSX.Element {
  const [request, setRequest] = useState<PipelineRequest>(initialRequest);
  const [response, setResponse] = useState<PipelineResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const result = await runPipeline(request);
      setResponse(result);
    } catch (runError) {
      setError((runError as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport(format: "svg" | "dxf" | "pdf" | "obj" | "glb" | "ifc"): Promise<void> {
    setError(null);
    try {
      const result = await exportPipeline(request, format);
      if (result.content) {
        downloadTextFile(`facade_export.${format}`, result.content);
      } else if (result.path) {
        window.alert(`Modele ${format.toUpperCase()} disponible: ${result.path}`);
      }
    } catch (exportError) {
      setError((exportError as Error).message);
    }
  }

  return (
    <main className="app-layout">
      <header>
        <h1>Bahi-SCAFF - Console technique interne</h1>
        <p>Generation facade, echafaudage, quantitatif et devis chantier.</p>
      </header>
      <section className="workspace">
        <MeasurementPanel request={request} onChange={setRequest} onRun={handleRun} loading={loading} />
        <div className="canvas-stack">
          <FacadeCanvas request={request} response={response} />
          <ResultsPanel response={response} error={error} onExport={handleExport} />
        </div>
      </section>
    </main>
  );
}
