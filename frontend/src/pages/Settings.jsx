import React, { useOutletContext } from "react";
import { useAuth } from "../context/AuthContext.jsx";

export default function Settings() {
  const { auth } = useAuth();
  const { status } = useOutletContext() || {};

  return (
    <div>
      <div className="page-header">
        <h2>Settings</h2>
        <p>Account and system information</p>
      </div>

      <div className="two-col">
        <div className="chart-card">
          <h3>Account</h3>
          <p style={{ fontSize: "0.85rem", marginBottom: 6 }}><strong>Name:</strong> {auth?.name}</p>
          <p style={{ fontSize: "0.85rem" }}><strong>Email:</strong> {auth?.email}</p>
        </div>

        <div className="chart-card">
          <h3>System Status</h3>
          <p style={{ fontSize: "0.85rem", marginBottom: 6 }}><strong>Data Mode:</strong> {status?.data_mode || "..."}</p>
          <p style={{ fontSize: "0.85rem", marginBottom: 6 }}><strong>Vision Backbone:</strong> {status?.vision_backbone || "..."}</p>
          <p style={{ fontSize: "0.85rem", marginBottom: 6 }}><strong>Device:</strong> {status?.device || "..."}</p>
          <p style={{ fontSize: "0.85rem" }}><strong>CUDA Available:</strong> {status?.cuda_available ? "Yes" : "No"}</p>
        </div>
      </div>
    </div>
  );
}
