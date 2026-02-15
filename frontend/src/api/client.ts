import axios from "axios";
import {
  DashboardStats,
  GenerationRequest,
  GenerationResponse,
  Material,
  Project,
} from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
});

export const apiClient = {
  async getDashboardStats(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>("/dashboard/stats");
    return data;
  },
  async listProjects(): Promise<Project[]> {
    const { data } = await api.get<Project[]>("/projects");
    return data;
  },
  async createProject(payload: { name: string; description?: string }): Promise<Project> {
    const { data } = await api.post<Project>("/projects", payload);
    return data;
  },
  async listMaterials(): Promise<Material[]> {
    const { data } = await api.get<Material[]>("/materials");
    return data;
  },
  async createMaterial(payload: Omit<Material, "id">): Promise<Material> {
    const { data } = await api.post<Material>("/materials", payload);
    return data;
  },
  async generateScaffold(projectId: string, payload: GenerationRequest): Promise<GenerationResponse> {
    const { data } = await api.post<GenerationResponse>(`/projects/${projectId}/generate`, payload);
    return data;
  },
  exportUrl(projectId: string, kind: "pdf" | "excel" | "bon-sortie" | "conformite"): string {
    return `${api.defaults.baseURL}/projects/${projectId}/exports/${kind}`;
  },
};
