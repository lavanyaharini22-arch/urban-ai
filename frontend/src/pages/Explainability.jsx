import React, { useOutletContext } from "react";

export default function Explainability() {
  const { status } = useOutletContext() || {};

  return (
    <div>
      <div className="page-header">
        <h2>Explainable AI</h2>
        <p>Understand why the model produced its predictions</p>
      </div>

      <div className="two-col">
        <div className="chart-card">
          <h3>Image Explanation</h3>
          <p style={{ fontSize: "0.85rem", color: "#8ba0c0", marginBottom: 10 }}>
            The vision branch ({status?.vision_backbone === "pretrained" ? "pretrained ViT-B/16" : "demo ViT"})
            exposes a per-patch saliency map showing which regions of the image most influenced the prediction.
            Run an analysis on the Image Analysis page to generate this for a specific image.
          </p>
        </div>

        <div className="chart-card">
          <h3>Sensor Feature Importance</h3>
          <p style={{ fontSize: "0.85rem", color: "#8ba0c0", marginBottom: 10 }}>
            Computed via permutation: each sensor feature is neutralized to its population mean and the
            resulting shift in predicted probability is measured. Larger shifts indicate greater influence
            on that specific prediction.
          </p>
          <div className="card">
            <div className="label">Example — Top Contributing Sensor Features</div>
            <ol style={{ paddingLeft: 18, fontSize: "0.85rem", marginTop: 8 }}>
              <li>Rainfall</li>
              <li>PM2.5</li>
              <li>Humidity</li>
              <li>Temperature</li>
            </ol>
          </div>
        </div>
      </div>

      <div className="chart-card" style={{ borderColor: "#f59e0b" }}>
        <p style={{ fontSize: "0.82rem" }}>
          These are model-derived interpretability signals, not causal explanations. They describe what the
          model attended to for a given input — not a guaranteed real-world cause of the predicted hazard.
        </p>
      </div>
    </div>
  );
}
