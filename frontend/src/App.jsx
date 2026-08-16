import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext.jsx";

import Register from "./pages/Register.jsx";
import Login from "./pages/Login.jsx";
import DashboardLayout from "./pages/DashboardLayout.jsx";
import Overview from "./pages/Overview.jsx";
import Environment from "./pages/Environment.jsx";
import ImageAnalysis from "./pages/ImageAnalysis.jsx";
import SensorFusion from "./pages/SensorFusion.jsx";
import Prediction from "./pages/Prediction.jsx";
import Analytics from "./pages/Analytics.jsx";
import Explainability from "./pages/Explainability.jsx";
import Settings from "./pages/Settings.jsx";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/register" replace />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Overview />} />
        <Route path="environment" element={<Environment />} />
        <Route path="image-analysis" element={<ImageAnalysis />} />
        <Route path="sensor-fusion" element={<SensorFusion />} />
        <Route path="prediction" element={<Prediction />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="explainability" element={<Explainability />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/register" replace />} />
    </Routes>
  );
}
