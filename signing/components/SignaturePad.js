"use client";
// Modal to draw or type a signature/initials. Returns a transparent PNG data URL.
import { useEffect, useRef, useState } from "react";

const FONTS = ["Dancing Script", "Great Vibes", "Caveat"];

export default function SignaturePad({ kind = "signature", defaultName = "", onDone, onCancel }) {
  const [mode, setMode] = useState("type");
  const [text, setText] = useState(kind === "initials" ? initialsOf(defaultName) : defaultName);
  const [font, setFont] = useState(FONTS[0]);
  const canvasRef = useRef(null);
  const drawing = useRef(false);
  const hasInk = useRef(false);

  useEffect(() => {
    if (mode !== "draw") return;
    const c = canvasRef.current;
    const dpr = window.devicePixelRatio || 1;
    c.width = c.clientWidth * dpr;
    c.height = c.clientHeight * dpr;
    const ctx = c.getContext("2d");
    ctx.scale(dpr, dpr);
    ctx.lineWidth = 2.4;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#111a40";
    hasInk.current = false;
  }, [mode]);

  const pos = (e) => {
    const r = canvasRef.current.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  };
  const down = (e) => {
    drawing.current = true;
    canvasRef.current.setPointerCapture(e.pointerId);
    const ctx = canvasRef.current.getContext("2d");
    ctx.beginPath();
    ctx.moveTo(...pos(e));
  };
  const move = (e) => {
    if (!drawing.current) return;
    const ctx = canvasRef.current.getContext("2d");
    ctx.lineTo(...pos(e));
    ctx.stroke();
    hasInk.current = true;
  };
  const clear = () => {
    const c = canvasRef.current;
    c.getContext("2d").clearRect(0, 0, c.width, c.height);
    hasInk.current = false;
  };

  const done = async () => {
    if (mode === "draw") {
      if (!hasInk.current) return;
      onDone(trim(canvasRef.current));
    } else {
      if (!text.trim()) return;
      await document.fonts.load(`64px "${font}"`);
      const c = document.createElement("canvas");
      const ctx = c.getContext("2d");
      ctx.font = `64px "${font}"`;
      const w = Math.ceil(ctx.measureText(text).width) + 40;
      c.width = w;
      c.height = 110;
      ctx.font = `64px "${font}"`;
      ctx.fillStyle = "#111a40";
      ctx.textBaseline = "middle";
      ctx.fillText(text, 20, 58);
      onDone(trim(c));
    }
  };

  return (
    <div className="modal-bg" onClick={onCancel}>
      <div className="modal light" onClick={(e) => e.stopPropagation()}>
        <h3>{kind === "initials" ? "Your initials" : "Your signature"}</h3>
        <div className="tabs">
          <button className={mode === "type" ? "on" : ""} onClick={() => setMode("type")}>Type</button>
          <button className={mode === "draw" ? "on" : ""} onClick={() => setMode("draw")}>Draw</button>
        </div>
        {mode === "type" ? (
          <>
            <input autoFocus value={text} onChange={(e) => setText(e.target.value)} placeholder={kind === "initials" ? "Initials" : "Full name"} />
            <div className="font-choices">
              {FONTS.map((f) => (
                <button key={f} className={font === f ? "on" : ""} style={{ fontFamily: `"${f}", cursive` }} onClick={() => setFont(f)}>
                  {text || "Signature"}
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            <canvas ref={canvasRef} className="sig-canvas" onPointerDown={down} onPointerMove={move} onPointerUp={() => (drawing.current = false)} />
            <button className="link" onClick={clear}>Clear</button>
          </>
        )}
        <div className="row end">
          <button className="btn ghost" onClick={onCancel}>Cancel</button>
          <button className="btn" onClick={done}>Adopt {kind}</button>
        </div>
      </div>
    </div>
  );
}

function initialsOf(name) {
  return name.split(/\s+/).filter(Boolean).map((p) => p[0].toUpperCase()).join("");
}

/** Crop transparent margins from a canvas and return a PNG data URL. */
function trim(canvas) {
  const ctx = canvas.getContext("2d");
  const { width, height } = canvas;
  const data = ctx.getImageData(0, 0, width, height).data;
  let minX = width, minY = height, maxX = -1, maxY = -1;
  for (let y = 0; y < height; y++)
    for (let x = 0; x < width; x++)
      if (data[(y * width + x) * 4 + 3] > 10) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
  if (maxX < 0) return canvas.toDataURL("image/png");
  const pad = 6;
  minX = Math.max(0, minX - pad);
  minY = Math.max(0, minY - pad);
  maxX = Math.min(width - 1, maxX + pad);
  maxY = Math.min(height - 1, maxY + pad);
  const out = document.createElement("canvas");
  out.width = maxX - minX + 1;
  out.height = maxY - minY + 1;
  out.getContext("2d").drawImage(canvas, minX, minY, out.width, out.height, 0, 0, out.width, out.height);
  return out.toDataURL("image/png");
}
