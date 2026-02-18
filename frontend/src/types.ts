export interface KnownMeasurement {
  pixel_span: number;
  meter_span: number;
}

export interface OpeningInput {
  kind: string;
  x_min_px: number;
  y_min_px: number;
  x_max_px: number;
  y_max_px: number;
}

export interface PipelineRequest {
  image_width_px: number;
  image_height_px: number;
  levels_hint: number;
  known_measurement?: KnownMeasurement;
  manual_openings: OpeningInput[];
  estimated_story_height_m: number;
  terrain_factor: number;
  labor_hourly_rate_eur: number;
  margin_rate: number;
  vat_rate: number;
}

export interface ScaffoldingBay {
  bay_index: number;
  x_start_m: number;
  x_end_m: number;
  levels_m: number[];
  width_m: number;
}

export interface MaterialLine {
  code: string;
  label: string;
  quantity: number;
  unit: string;
}

export interface QuoteOutput {
  material_cost_eur: number;
  labor_cost_eur: number;
  margin_eur: number;
  vat_eur: number;
  total_eur: number;
  estimated_hours: number;
}

export interface PipelineResponse {
  facade_width_m: number;
  facade_height_m: number;
  calibration_method: string;
  calibration_confidence: number;
  scaffolding_bays: ScaffoldingBay[];
  compliance_notes: string[];
  materials: MaterialLine[];
  quote: QuoteOutput;
  runtime_ms: number;
  assumptions: string[];
}
