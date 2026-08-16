import React, { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import api from "../services/api";

const FIELDS = [
  ["temperature", "Temperature (°C)"], ["humidity", "Humidity (%)"],
  ["pm25", "PM2.5"], ["pm10", "PM10"], ["rainfall", "Rainfall (mm)"],
  ["wind_speed", "Wind Speed (km/h)"], ["aqi", "AQI"], ["pressure", "Pressure (hPa)"],
];

export default function SensorFusion() {
  const [form, setForm] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [trend, setTrend] = useState([]);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  useEffect(() => {
    api.get("/sensor-data?points=12").then(({ data }) => setTrend(data.series)).catch(() => {});
  }, []);

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {};
      Object.entries(form).forEach(([k, v]) => { if (v !== "") payload[k] = parseFloat(v); });
      const { data } = await api.post("/sensor-predict", payload);
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
        <h2>Sensor Fusion</h2>
        <p>Enter environmental sensor readings for the Sensor Feature Network</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="two-col">
        <div className="chart-card">
          <h3>Sensor Input</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            {FIELDS.map(([key, label]) => (
              <div className="field" key={key}>
                <label>{label}</label>
                <input type="number" value={form[key] || ""} onChange={update(key)} placeholder="Leave blank if unknown" />
              </div>
            ))}
          </div>
          <button className="primary" onClick={submit} disabled={loading}>
            {loading ? "Running Sensor Network..." : "Compute Sensor Risk"}
          </button>
        </div>

        <div className="chart-card">
          <h3>Sensor Risk {result && <span className="demo-tag">{result.data_mode}</span>}</h3>
          {!result && <p style={{ color: "#8ba0c0", fontSize: "0.85rem" }}>Submit sensor readings to see the risk assessment.</p>}
          {result && (
            <>
              <div className="card" style={{ marginBottom: 12 }}>
                <div className="label">Predicted Condition</div>
                <div className="value" style={{ fontSize: "1.2rem" }}>{result.hazard.replace(/_/g, " ")}</div>
              </div>
              <span className={`risk-badge risk-${result.risk_level}`}>{result.risk_level}</span>
            </>
          )}
        </div>
      </div>

      <div className="chart-card">
        <h3>Sensor Trends</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={trend.map((d, i) => ({ t: `T-${trend.length - i}`, ...d }))}>
            <CartesianGrid stroke="#223047" strokeDasharray="3 3" />
            <XAxis dataKey="t" stroke="#8ba0c0" fontSize={11} />
            <YAxis stroke="#8ba0c0" fontSize={11} />
            <Tooltip contentStyle={{ background: "#151d2e", border: "1px solid #223047" }} />
            <Line type="monotone" dataKey="pm25" stroke="#3b82f6" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="aqi" stroke="#22d3ee" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
