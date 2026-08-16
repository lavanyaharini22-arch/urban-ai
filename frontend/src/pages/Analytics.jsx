import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";
import api from "../services/api";

export default function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/metrics").then(({ data }) => setMetrics(data)).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h2>Analytics & Model Performance</h2>
        <p>Sensor-only vs. Image-only vs. Multimodal model comparison {metrics && <span className="demo-tag">{metrics.data_mode}</span>}</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {metrics && (
        <>
          <div className="chart-card">
            <h3>Accuracy / Precision / Recall / F1</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics.models}>
                <CartesianGrid stroke="#223047" strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#8ba0c0" fontSize={11} />
                <YAxis stroke="#8ba0c0" fontSize={11} domain={[0, 1]} />
                <Tooltip contentStyle={{ background: "#151d2e", border: "1px solid #223047" }} />
                <Legend />
                <Bar dataKey="accuracy" fill="#3b82f6" />
                <Bar dataKey="precision" fill="#22d3ee" />
                <Bar dataKey="recall" fill="#f59e0b" />
                <Bar dataKey="f1" fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Model Comparison Table</h3>
            <table>
              <thead>
                <tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th></tr>
              </thead>
              <tbody>
                {metrics.models.map((m) => (
                  <tr key={m.name}>
                    <td>{m.name}</td><td>{m.accuracy}</td><td>{m.precision}</td><td>{m.recall}</td><td>{m.f1}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
