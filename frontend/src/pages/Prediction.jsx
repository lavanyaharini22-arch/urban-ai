import React, { useState, useRef } from "react";
import api from "../services/api";

const FIELDS = [
  ["temperature", "Temperature (°C)"], ["humidity", "Humidity (%)"],
  ["rainfall", "Rainfall (mm)"], ["pm25", "PM2.5"],
];

export default function Prediction() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [sensors, setSensors] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef();

  const onFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const update = (key) => (e) => setSensors({ ...sensors, [key]: e.target.value });

  const predict = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {};
      Object.entries(sensors).forEach(([k, v]) => { if (v !== "") payload[k] = parseFloat(v); });

      const formData = new FormData();
      formData.append("sensor_json", JSON.stringify(payload));
      if (file) formData.append("file", file);

      const { data } = await api.post("/multimodal-predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Hazard Prediction</h2>
        <p>Combine an image and sensor readings for the full multimodal prediction</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="two-col">
        <div className="chart-card">
          <h3>Inputs</h3>
          <div className="upload-box" onClick={() => inputRef.current.click()} style={{ marginBottom: 14 }}>
            {preview ? <img src={preview} className="preview-img" alt="preview" /> : <p>Click to upload an image (optional)</p>}
            <input ref={inputRef} type="file" accept="image/jpeg,image/png" hidden onChange={onFile} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            {FIELDS.map(([key, label]) => (
              <div className="field" key={key}>
                <label>{label}</label>
                <input type="number" value={sensors[key] || ""} onChange={update(key)} />
              </div>
            ))}
          </div>
          <button className="primary" onClick={predict} disabled={loading}>
            {loading ? "Running Multimodal Model..." : "Predict Hazard"}
          </button>
        </div>

        <div className="chart-card">
          <h3>Result {result && <span className="demo-tag">{result.data_mode}</span>}</h3>
          {!result && <p style={{ color: "#8ba0c0", fontSize: "0.85rem" }}>Prediction output will appear here.</p>}
          {result && (
            <div>
              <div className="card" style={{ marginBottom: 12 }}>
                <div className="label">Predicted Hazard</div>
                <div className="value" style={{ fontSize: "1.2rem" }}>{result.hazard.replace(/_/g, " ")}</div>
              </div>
              <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
                <span className={`risk-badge risk-${result.risk_level}`}>{result.risk_level}</span>
                <span style={{ color: "#8ba0c0", alignSelf: "center" }}>Confidence: {result.confidence}%</span>
              </div>
              {(result.image_contribution != null || result.sensor_contribution != null) && (
                <div className="card" style={{ marginBottom: 12 }}>
                  <div className="label">Contribution Split</div>
                  <div style={{ fontSize: "0.85rem" }}>
                    Image: {result.image_contribution ?? "—"}% &nbsp;|&nbsp; Sensor: {result.sensor_contribution ?? "—"}%
                  </div>
                </div>
              )}
              {result.top_signals?.length > 0 && (
                <div className="card" style={{ marginBottom: 12 }}>
                  <div className="label">Main Signals</div>
                  <ul style={{ paddingLeft: 18, fontSize: "0.85rem" }}>
                    {result.top_signals.map((s) => <li key={s}>{s}</li>)}
                  </ul>
                </div>
              )}
              <div className="card">
                <div className="label">Recommended Action</div>
                <div style={{ fontSize: "0.85rem" }}>{result.recommended_action}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {result && (result.risk_level === "HIGH" || result.risk_level === "CRITICAL") && (
        <div className="chart-card" style={{ borderColor: "#ef4444" }}>
          <h3>⚠️ Early Warning <span className="demo-tag">{result.data_mode}</span></h3>
          <p style={{ fontSize: "0.85rem" }}>
            Elevated {result.hazard.replace(/_/g, " ").toLowerCase()} risk detected. Contributing signals:
          </p>
          <ul style={{ paddingLeft: 18, fontSize: "0.85rem", marginTop: 8 }}>
            {result.top_signals.map((s) => <li key={s}>{s}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
