"use client";
// DocuSign-style "Adopt Your Signature": one dialog captures both signature and initials,
// either by picking a typed style or drawing. Returns transparent PNG data URLs.
import { useEffect, useRef, useState } from "react";

const FONTS = ["Dancing Script", "Great Vibes", "Homemade Apple", "Caveat"];

export const initialsOf = (name = "") =>
  name.split(/\s+/).filter(Boolean).map((p) => p[0].toUpperCase()).join("").slice(0, 4);

/**
 * @param {{defaultName?: string, actionLabel?: string, onDone: (r:{signature:string, initials:string, name:string}) => void|Promise<void>, onCancel: () => void}} props
 */
export default function SignaturePad({ defaultName = "", actionLabel = "Adopt and Sign", onDone, onCancel }) {
  const [name, setName] = useState(defaultName);
  const [ini, setIni] = useState(initialsOf(defaultName));
  const [mode, setMode] = useState("style");
  const [font, setFont] = useState(FONTS[0]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const sigCanvas = useRef(null);
  const iniCanvas = useRef(null);

  useEffect(() => {
    if (mode === "draw") [sigCanvas.current, iniCanvas.current].forEach(prepCanvas);
  }, [mode]);

  const adopt = async () => {
    setErr("");
    try {
      let signature, initials;
      if (mode === "style") {
        if (!name.trim()) throw new Error("Enter your full name");
        if (!ini.trim()) throw new Error("Enter your initials");
        await document.fonts.load(`64px "${font}"`).catch(() => {});
        signature = textToPng(name.trim(), font);
        initials = textToPng(ini.trim(), font);
      } else {
        if (!sigCanvas.current._ink) throw new Error("Draw your signature");
        if (!iniCanvas.current._ink) throw new Error("Draw your initials");
        signature = trim(sigCanvas.current);
        initials = trim(iniCanvas.current);
      }
      setBusy(true);
      await onDone({ signature, initials, name: name.trim() });
    } catch (e) {
      setErr(e.message || String(e));
      setBusy(false);
    }
  };

  return (
    <div className="modal-bg" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Adopt your signature">
        <div className="mhead">
          <h3>Adopt Your Signature</h3>
          <p>Confirm your name, initials and signature.</p>
        </div>
        <div className="mbody">
          <div className="row" style={{ alignItems: "flex-end" }}>
            <div style={{ flex: 3, minWidth: 200 }}>
              <label>Full name *</label>
              <input value={name} autoFocus onChange={(e) => { setName(e.target.value); setIni(initialsOf(e.target.value)); }} />
            </div>
            <div style={{ flex: 1, minWidth: 90 }}>
              <label>Initials *</label>
              <input value={ini} maxLength={5} onChange={(e) => setIni(e.target.value)} />
            </div>
          </div>

          <div className="tabs" style={{ marginTop: 16 }}>
            <button className={mode === "style" ? "on" : ""} onClick={() => setMode("style")}>Select style</button>
            <button className={mode === "draw" ? "on" : ""} onClick={() => setMode("draw")}>Draw</button>
          </div>

          {mode === "style" ? (
            <div className="style-list">
              {FONTS.map((f) => (
                <button key={f} type="button" className={`style-opt ${font === f ? "on" : ""}`} onClick={() => setFont(f)}>
                  <input type="radio" readOnly checked={font === f} />
                  <span className="sig" style={{ fontFamily: `"${f}", cursive` }}>{name || "Your Name"}</span>
                  <span className="ini" style={{ fontFamily: `"${f}", cursive` }}>{ini || "YN"}</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="draw-grid">
              <div>
                <label>Draw your signature</label>
                <DrawBox canvasRef={sigCanvas} />
              </div>
              <div>
                <label>Draw your initials</label>
                <DrawBox canvasRef={iniCanvas} />
              </div>
            </div>
          )}
          <p className="legal">
            By selecting Adopt and Sign, I agree that the signature and initials will be the electronic representation of my signature and
            initials for all purposes when I use them on documents, just the same as a pen-and-paper signature.
          </p>
          {err && <div className="error">{err}</div>}
        </div>
        <div className="mfoot">
          <button className="btn ghost" onClick={onCancel}>Cancel</button>
          <button className="btn yellow" disabled={busy} onClick={adopt}>{busy ? "Saving…" : actionLabel}</button>
        </div>
      </div>
    </div>
  );
}

function DrawBox({ canvasRef }) {
  const drawing = useRef(false);
  const pos = (e) => {
    const r = canvasRef.current.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  };
  return (
    <>
      <canvas
        ref={canvasRef}
        className="sig-canvas"
        onPointerDown={(e) => {
          drawing.current = true;
          canvasRef.current.setPointerCapture(e.pointerId);
          const ctx = canvasRef.current.getContext("2d");
          ctx.beginPath();
          ctx.moveTo(...pos(e));
        }}
        onPointerMove={(e) => {
          if (!drawing.current) return;
          const ctx = canvasRef.current.getContext("2d");
          ctx.lineTo(...pos(e));
          ctx.stroke();
          canvasRef.current._ink = true;
        }}
        onPointerUp={() => (drawing.current = false)}
      />
      <button type="button" className="link small" onClick={() => prepCanvas(canvasRef.current)}>Clear</button>
    </>
  );
}

function prepCanvas(c) {
  if (!c) return;
  const dpr = window.devicePixelRatio || 1;
  c.width = c.clientWidth * dpr;
  c.height = c.clientHeight * dpr;
  const ctx = c.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.lineWidth = 2.4;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = "#111a40";
  c._ink = false;
}

function textToPng(text, font) {
  const c = document.createElement("canvas");
  const ctx = c.getContext("2d");
  ctx.font = `64px "${font}", cursive`;
  c.width = Math.ceil(ctx.measureText(text).width) + 40;
  c.height = 120;
  ctx.font = `64px "${font}", cursive`;
  ctx.fillStyle = "#111a40";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 20, 62);
  return trim(c);
}

/** Crop transparent margins and return a PNG data URL. */
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
