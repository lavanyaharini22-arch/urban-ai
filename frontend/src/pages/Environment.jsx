import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import api from "../services/api";

const STATUS_LEVELS = ["NORMAL", "LOW RISK", "MODERATE RISK", "HIGH RISK", "CRITICAL"];

export default function Environment() {
  const [series, setSeries] = useState([]);
  const [scenario, setScenario] = useState("random");

  useEffect(() => {
    api.get(`/sensor-data?scenario=${scenario}&points=12`)
      .then(({ data }) => setSeries(data.series))
      .catch(() => setSeries([]));
  }, [scenario]);

  const latest = series[series.length - 1] || {};
  const statusIndex = latest.rainfall > 40 ? 3 : latest.aqi > 200 ? 3 : latest.rainfall > 15 ? 2 : 0;

  return (
    <div>
      <div className="page-header">
        <h2>Environmental Monitoring</h2>
        <p>Live sensor snapshot across monitored conditions <span className="demo-tag">DEMO DATA</span></p>
      </div>

      <div className="field" style={{ maxWidth: 260 }}>
        <label>Scenario</label>
        <select value={scenario} onChange={(e) => setScenario(e.target.value)}
          style={{ width: "100%", padding: 10, background: "#151d2e", color: "#e6ecf5", border: "1px solid #223047", borderRadius: 8 }}>
          <option value="random">Random</option>
          <option value="normal">Normal Conditions</option>
          <option value="flood">Flood Risk</option>
          <option value="pollution">Air Pollution</option>
        </select>
      </div>

      <div className="card" style={{ margin: "16px 0" }}>
        <div className="label">Current Environmental Status</div>
        <div className={`risk-badge risk-${STATUS_LEVELS[statusIndex].split(" ")[0]}`}>
          {STATUS_LEVELS[statusIndex]}
        </div>
      </div>

      <div className="chart-card">
        <h3>PM2.5 / PM10 Levels</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={series.map((d, i) => ({ t: `T-${series.length - i}`, ...d }))}>
            <CartesianGrid stroke="#223047" strokeDasharray="3 3" />
            <XAxis dataKey="t" stroke="#8ba0c0" fontSize={11} />
            <YAxis stroke="#8ba0c0" fontSize={11} />
            <Tooltip contentStyle={{ background: "#151d2e", border: "1px solid #223047" }} />
            <Bar dataKey="pm25" fill="#3b82f6" />
            <Bar dataKey="pm10" fill="#22d3ee" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
