import React, { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import api from "../services/api";

const NAV_ITEMS = [
  { to: "/dashboard", label: "🏠 Overview", end: true },
  { to: "/dashboard/environment", label: "🌍 Environmental Monitoring" },
  { to: "/dashboard/image-analysis", label: "📷 Image Analysis" },
  { to: "/dashboard/sensor-fusion", label: "📡 Sensor Fusion" },
  { to: "/dashboard/prediction", label: "🔮 Hazard Prediction" },
  { to: "/dashboard/analytics", label: "📊 Analytics" },
  { to: "/dashboard/explainability", label: "🧠 Explainable AI" },
  { to: "/dashboard/settings", label: "⚙️ Settings" },
];

export default function DashboardLayout() {
  const { auth, logout } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);

  useEffect(() => {
    api.get("/model/status").then(({ data }) => setStatus(data)).catch(() => setStatus(null));
  }, []);

  const handleLogout = async () => {
    try {
      await api.post("/logout");
    } catch {
      // ignore network errors on logout
    }
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">🌐 Urban Hazard AI</div>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}
              className={({ isActive }) => (isActive ? "active" : "")}>
              {item.label}
            </NavLink>
          ))}
          <button className="logout-btn" onClick={handleLogout}>🚪 Logout</button>
        </nav>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="title">Urban Environmental Intelligence</div>
          <div className="status-group">
            <span>{auth?.name}</span>
            <span className="pill ok">System Online</span>
            <span className={`pill ${status?.data_mode === "REAL" ? "ok" : "warn"}`}>
              Model: {status?.data_mode || "..."}
            </span>
            <span className="pill ok">{status?.device?.toUpperCase() || "CPU"}</span>
          </div>
        </header>
        <main className="content">
          <Outlet context={{ status }} />
        </main>
      </div>
    </div>
  );
}
