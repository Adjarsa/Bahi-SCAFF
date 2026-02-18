import type { ChangeEvent } from "react";
import type { PipelineRequest } from "../types";

interface MeasurementPanelProps {
  request: PipelineRequest;
  onChange: (next: PipelineRequest) => void;
  onRun: () => void;
  loading: boolean;
}

export function MeasurementPanel({
  request,
  onChange,
  onRun,
  loading
}: MeasurementPanelProps): JSX.Element {
  function updateNumericField(
    key: keyof PipelineRequest,
    event: ChangeEvent<HTMLInputElement>
  ): void {
    const value = Number(event.target.value);
    if (Number.isNaN(value)) {
      return;
    }
    onChange({ ...request, [key]: value });
  }

  function toggleKnownMeasurement(enabled: boolean): void {
    if (!enabled) {
      const next = { ...request };
      delete next.known_measurement;
      onChange(next);
      return;
    }
    onChange({
      ...request,
      known_measurement: { pixel_span: 300, meter_span: 1.5 }
    });
  }

  return (
    <section className="panel">
      <h2>Parametres facade</h2>
      <div className="grid">
        <label>
          Largeur image (px)
          <input
            type="number"
            value={request.image_width_px}
            onChange={(event) => updateNumericField("image_width_px", event)}
          />
        </label>
        <label>
          Hauteur image (px)
          <input
            type="number"
            value={request.image_height_px}
            onChange={(event) => updateNumericField("image_height_px", event)}
          />
        </label>
        <label>
          Nombre d'etages
          <input
            type="number"
            value={request.levels_hint}
            onChange={(event) => updateNumericField("levels_hint", event)}
          />
        </label>
        <label>
          Hauteur etage estimee (m)
          <input
            type="number"
            step="0.1"
            value={request.estimated_story_height_m}
            onChange={(event) => updateNumericField("estimated_story_height_m", event)}
          />
        </label>
        <label>
          Facteur terrain
          <input
            type="number"
            step="0.1"
            value={request.terrain_factor}
            onChange={(event) => updateNumericField("terrain_factor", event)}
          />
        </label>
        <label>
          Taux horaire MO (EUR)
          <input
            type="number"
            value={request.labor_hourly_rate_eur}
            onChange={(event) => updateNumericField("labor_hourly_rate_eur", event)}
          />
        </label>
        <label>
          Marge
          <input
            type="number"
            step="0.01"
            value={request.margin_rate}
            onChange={(event) => updateNumericField("margin_rate", event)}
          />
        </label>
        <label>
          TVA
          <input
            type="number"
            step="0.01"
            value={request.vat_rate}
            onChange={(event) => updateNumericField("vat_rate", event)}
          />
        </label>
      </div>

      <label className="checkbox">
        <input
          type="checkbox"
          checked={Boolean(request.known_measurement)}
          onChange={(event) => toggleKnownMeasurement(event.target.checked)}
        />
        Calibration manuelle
      </label>

      {request.known_measurement ? (
        <div className="grid">
          <label>
            Portee connue (px)
            <input
              type="number"
              value={request.known_measurement.pixel_span}
              onChange={(event) =>
                onChange({
                  ...request,
                  known_measurement: {
                    ...request.known_measurement!,
                    pixel_span: Number(event.target.value)
                  }
                })
              }
            />
          </label>
          <label>
            Portee connue (m)
            <input
              type="number"
              step="0.01"
              value={request.known_measurement.meter_span}
              onChange={(event) =>
                onChange({
                  ...request,
                  known_measurement: {
                    ...request.known_measurement!,
                    meter_span: Number(event.target.value)
                  }
                })
              }
            />
          </label>
        </div>
      ) : null}

      <button onClick={onRun} disabled={loading}>
        {loading ? "Calcul en cours..." : "Generer facade + echafaudage"}
      </button>
    </section>
  );
}
