/**
 * OverlayCanvas — AI anatomy overlays drawn on the surgeon camera.
 *
 * A <canvas> element positioned absolutely on top of the expanded surgeon camera.
 * Draws colour-coded structure outlines with floating labels.
 */

import { useRef, useEffect } from "react";
import { useDirector, type OverlayItem } from "@/lib/director";

const OVERLAY_COLOURS: Record<string, { stroke: string; fill: string; dash?: number[] }> = {
  artery: { stroke: "rgba(255, 59, 74, 0.7)", fill: "rgba(255, 59, 74, 0.12)" },
  vein:   { stroke: "rgba(61, 139, 255, 0.7)", fill: "rgba(61, 139, 255, 0.12)" },
  nerve:  { stroke: "rgba(255, 200, 50, 0.8)", fill: "rgba(255, 200, 50, 0.08)", dash: [6, 4] },
  duct:   { stroke: "rgba(34, 197, 94, 0.7)", fill: "rgba(34, 197, 94, 0.12)" },
  marma:  { stroke: "rgba(255, 159, 28, 0.6)", fill: "rgba(255, 159, 28, 0.15)" },
};

const LABEL_BG = "rgba(10, 10, 15, 0.75)";

export function OverlayCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlays = useDirector((s) => s.overlays);
  const overlayItems = useDirector((s) => s.overlayItems);
  const frameRef = useRef(0);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let running = true;

    const draw = () => {
      if (!running) return;
      timeRef.current += 0.016; // ~60fps

      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
      }
      const w = canvas.width;
      const h = canvas.height;

      ctx.clearRect(0, 0, w, h);

      // Filter items by active overlay types
      const activeItems = overlayItems.filter((item) => {
        if (item.type === "artery" && !overlays.arteries) return false;
        if (item.type === "vein" && !overlays.veins) return false;
        if (item.type === "nerve" && !overlays.nerves) return false;
        if (item.type === "duct" && !overlays.ducts) return false;
        if (item.type === "marma" && !overlays.marma) return false;
        return true;
      });

      for (const item of activeItems) {
        const [x1, y1, x2, y2] = item.bbox;
        const px1 = x1 * w, py1 = y1 * h, px2 = x2 * w, py2 = y2 * h;
        const bw = px2 - px1, bh = py2 - py1;
        const colours = OVERLAY_COLOURS[item.type] || OVERLAY_COLOURS.artery;

        ctx.save();

        // Marma: pulsing filled circle
        if (item.type === "marma") {
          const cx = (px1 + px2) / 2;
          const cy = (py1 + py2) / 2;
          const radius = Math.max(bw, bh) / 2;
          const pulse = 1 + 0.15 * Math.sin(timeRef.current * 3);

          // Concentric rings
          for (let ring = 3; ring >= 1; ring--) {
            ctx.beginPath();
            ctx.arc(cx, cy, radius * pulse * (1 + ring * 0.3), 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(255, 159, 28, ${0.1 / ring})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }

          ctx.beginPath();
          ctx.arc(cx, cy, radius * pulse, 0, Math.PI * 2);
          ctx.fillStyle = colours.fill;
          ctx.fill();
          ctx.strokeStyle = colours.stroke;
          ctx.lineWidth = 2;
          ctx.stroke();
        } else {
          // Rectangle outline for arteries/veins/nerves/ducts
          if (colours.dash) ctx.setLineDash(colours.dash);
          ctx.strokeStyle = colours.stroke;
          ctx.lineWidth = 2;

          // Pulse effect for arteries
          if (item.type === "artery") {
            const pulse = 1 + 0.1 * Math.sin(timeRef.current * 5);
            ctx.lineWidth = 2 * pulse;
          }

          ctx.strokeRect(px1, py1, bw, bh);
          ctx.fillStyle = colours.fill;
          ctx.fillRect(px1, py1, bw, bh);
        }

        // Label with glassmorphic background
        const labelText = `${item.label} (${Math.round(item.confidence * 100)}%)`;
        ctx.font = "12px Inter, sans-serif";
        const textMetrics = ctx.measureText(labelText);
        const labelW = textMetrics.width + 16;
        const labelH = 22;
        const labelX = px1;
        const labelY = py1 - labelH - 4;

        ctx.fillStyle = LABEL_BG;
        ctx.beginPath();
        ctx.roundRect(labelX, labelY, labelW, labelH, 4);
        ctx.fill();

        ctx.fillStyle = colours.stroke;
        ctx.fillText(labelText, labelX + 8, labelY + 15);

        ctx.restore();
      }

      // Legend panel (bottom-left)
      const activeTypes = [...new Set(activeItems.map((i) => i.type))];
      if (activeTypes.length > 0) {
        const legendY = h - 20 - activeTypes.length * 20;
        ctx.fillStyle = LABEL_BG;
        ctx.beginPath();
        ctx.roundRect(12, legendY, 120, activeTypes.length * 20 + 10, 6);
        ctx.fill();

        activeTypes.forEach((type, i) => {
          const y = legendY + 18 + i * 20;
          const colour = OVERLAY_COLOURS[type]?.stroke || "#fff";
          ctx.fillStyle = colour;
          ctx.beginPath();
          ctx.arc(26, y - 4, 4, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = "#e0e0e0";
          ctx.font = "11px Inter, sans-serif";
          ctx.fillText(type.charAt(0).toUpperCase() + type.slice(1) + "s", 36, y);
        });
      }

      frameRef.current = requestAnimationFrame(draw);
    };

    frameRef.current = requestAnimationFrame(draw);
    return () => {
      running = false;
      cancelAnimationFrame(frameRef.current);
    };
  }, [overlays, overlayItems]);

  const hasActiveOverlay = Object.values(overlays).some(Boolean);
  if (!hasActiveOverlay || overlayItems.length === 0) return null;

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 z-10 pointer-events-none"
      style={{ width: "100%", height: "100%" }}
    />
  );
}

export default OverlayCanvas;
