import { useEffect, useRef, type ReactElement } from "react";
import type { PipelineRequest, PipelineResponse } from "../types";

interface FacadeCanvasProps {
  request: PipelineRequest;
  response: PipelineResponse | null;
}

export function FacadeCanvas({ request, response }: FacadeCanvasProps): ReactElement {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#f5f7fa";
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = "#173b6b";
    ctx.lineWidth = 2;
    ctx.strokeRect(40, 20, width - 80, height - 40);

    ctx.fillStyle = "#173b6b";
    ctx.font = "12px sans-serif";
    ctx.fillText(`Image: ${request.image_width_px}x${request.image_height_px}px`, 48, 38);

    if (!response) {
      ctx.fillStyle = "#5f6b7a";
      ctx.fillText("Lancer le calcul pour afficher l'echafaudage.", 48, 58);
      return;
    }

    const facadeWidthM = response.facade_width_m;
    const facadeHeightM = response.facade_height_m;
    const innerWidth = width - 100;
    const innerHeight = height - 80;
    const xOrigin = 50;
    const yBottom = height - 30;
    const scale = Math.min(innerWidth / facadeWidthM, innerHeight / facadeHeightM);

    ctx.strokeStyle = "#0f9d58";
    ctx.lineWidth = 1.5;
    for (const bay of response.scaffolding_bays) {
      const x = xOrigin + bay.x_start_m * scale;
      const bayWidth = bay.width_m * scale;
      const bayHeight = facadeHeightM * scale;
      const y = yBottom - bayHeight;
      ctx.strokeRect(x, y, bayWidth, bayHeight);

      ctx.fillStyle = "#1f2a36";
      ctx.fillText(`T${bay.bay_index}`, x + 4, y - 6);
      for (const level of bay.levels_m) {
        const yLevel = yBottom - level * scale;
        ctx.beginPath();
        ctx.moveTo(x, yLevel);
        ctx.lineTo(x + bayWidth, yLevel);
        ctx.strokeStyle = "#4a90e2";
        ctx.stroke();
      }
    }

    ctx.fillStyle = "#1f2a36";
    ctx.fillText(`Facade: ${facadeWidthM.toFixed(2)}m x ${facadeHeightM.toFixed(2)}m`, 50, height - 8);
  }, [request, response]);

  return <canvas ref={canvasRef} width={640} height={360} className="facade-canvas" />;
}
