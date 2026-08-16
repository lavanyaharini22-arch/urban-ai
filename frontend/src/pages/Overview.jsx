import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import api from "../services/api";

export default function Overview() {
  const [series, setSeries] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/sensor-data?scenario=random&points=24")
      .then(({ data }) => setSeries(data.series))
      .catch((err) => setError(err.message));
  }, []);

  const latest = series[series.length - 1] || {};
  const chartData = series.map((d, i) => ({ t: `T-${series.length - i}`, ...d }));

  return (
    <div>
      <div className="page-header">
        <h2>Overview</h2>
        <p>Real-time snapshot of urban environmental conditions <span className="demo-tag">DEMO DATA</span></p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="kpi-grid">
        <Kpi label="Current Hazard Level" value="LOW" />
        <Kpi label="Air Quality Index" value={latest.aqi ?? "--"} />
        <Kpi label="Temperature" value={latest.temperature ? `${latest.temperature}°C` : "--"} />
        <Kpi label="Humidity" value={latest.humidity ? `${latest.humidity}%` : "--"} />
        <Kpi label="Rainfall" value={latest.rainfall ? `${latest.rainfall} mm` : "--"} />
        <Kpi label="Active Sensors" value="12" />
        <Kpi label="Model Confidence" value="91.2%" />
      </div>

      <div className="two-col">
        <div className="chart-card">
          <h3>AQI Over Time</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="#223047" strokeDasharray="3 3" />
              <XAxis dataKey="t" stroke="#8ba0c0" fontSize={11} />
              <YAxis stroke="#8ba0c0" fontSize={11} />
              <Tooltip contentStyle={{ background: "#151d2e", border: "1px solid #223047" }} />
              <Line type="monotone" dataKey="aqi" stroke="#22d3ee" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Temperature & Humidity</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="#223047" strokeDasharray="3 3" />
              <XAxis dataKey="t" stroke="#8ba0c0" fontSize={11} />
              <YAxis stroke="#8ba0c0" fontSize={11} />
              <Tooltip contentStyle={{ background: "#151d2e", border: "1px solid #223047" }} />
              <Line type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="humidity" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card">
        <h3>Rainfall Trend</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid stroke="#223047" strokeDasharray="3 3" />
            <XAxis dataKey="t" stroke="#8ba0c0" fontSize={11} />
            <YAxis stroke="#8ba0c0" fontSize={11} />
            <Tooltip contentStyle={{ background: "#151d2e", border: "1px solid #223047" }} />
            <Line type="monotone" dataKey="rainfall" stroke="#60a5fa" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Kpi({ label, value }) {
  return (
    <div className="card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}
