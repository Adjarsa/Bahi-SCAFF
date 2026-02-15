export interface Project {
  id: string;
  name: string;
  description?: string | null;
  status: string;
  facade_data: Record<string, unknown>;
  calibration_data: Record<string, unknown>;
  generation_result: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Material {
  id: string;
  name: string;
  type: string;
  dimension: string;
  weight_kg: number;
  compatibility: string;
  stock_quantity: number;
  condition: string;
}

export interface DashboardStats {
  active_projects: number;
  ongoing_sites: number;
  monthly_material_usage: number;
  stock_utilization_rate: number;
  profitability_estimate: number;
}

export interface GenerationRequest {
  scaffold_type: string;
  bay_width_m: number;
  level_height_m: number;
  upright_spacing_m: number;
  number_of_levels?: number;
  load_class: number;
  has_stair_tower: boolean;
  access_mode: string;
  has_consoles: boolean;
  has_nets: boolean;
  has_pedestrian_protection: boolean;
  optimize_stock: boolean;
  available_module_widths_m: number[];
}

export interface GenerationLine {
  type: string;
  quantity: number;
  unit_weight_kg: number;
  total_weight_kg: number;
  in_stock: number;
  shortage: number;
}

export interface GenerationWarning {
  code: string;
  severity: string;
  message: string;
}

export interface GenerationResponse {
  facade_width_m: number;
  facade_height_m: number;
  levels: number;
  bay_layout_m: number[];
  quantities: GenerationLine[];
  total_weight_kg: number;
  total_volume_m3: number;
  stock_sufficient: boolean;
  warnings: GenerationWarning[];
  confidence: number;
  requires_confirmation: boolean;
}
