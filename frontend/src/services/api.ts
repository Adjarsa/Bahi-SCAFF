import type { PipelineRequest, PipelineResponse } from "../types";

const API_BASE = (import.meta as ImportMeta & { env: Record<string, string | undefined> }).env
  .VITE_API_BASE ?? "http://localhost:8000/api/v1";

export async function runPipeline(payload: PipelineRequest): Promise<PipelineResponse> {
  const response = await fetch(`${API_BASE}/pipeline/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Erreur API (${response.status})`);
  }
  return (await response.json()) as PipelineResponse;
}

export async function exportPipeline(
  payload: PipelineRequest,
  format: "svg" | "dxf" | "pdf" | "obj" | "glb" | "ifc"
): Promise<Record<string, string>> {
  const response = await fetch(`${API_BASE}/pipeline/export/${format}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`Export ${format} indisponible`);
  }
  return (await response.json()) as Record<string, string>;
}
