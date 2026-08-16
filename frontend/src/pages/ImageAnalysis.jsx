import React, { useState, useRef } from "react";
import api from "../services/api";

export default function ImageAnalysis() {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef();

  const onFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    if (!["image/jpeg", "image/png", "image/jpg"].includes(f.type)) {
      setError("Only JPG and PNG images are supported.");
      return;
    }
    setError("");
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  };

  const analyze = async () => {
    if (!file) {
      setError("Please upload an image first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post("/image-predict", formData, {
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
        <h2>Image Analysis</h2>
        <p>Upload a street or CCTV image to run the Vision Transformer branch</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="two-col">
        <div className="chart-card">
          <div className="upload-box" onClick={() => inputRef.current.click()}>
            {preview ? (
              <img src={preview} alt="preview" className="preview-img" />
            ) : (
              <p>Click to upload a JPG or PNG image</p>
            )}
            <input ref={inputRef} type="file" accept="image/jpeg,image/png" hidden onChange={onFile} />
          </div>
          <button className="primary" style={{ marginTop: 14 }} onClick={analyze} disabled={loading}>
            {loading ? "Running Vision Transformer..." : "Analyze Image"}
          </button>
        </div>

        <div className="chart-card">
          <h3>Prediction Result {result && <span className="demo-tag">{result.data_mode}</span>}</h3>
          {!result && <p style={{ color: "#8ba0c0", fontSize: "0.85rem" }}>Results will appear here after analysis.</p>}
          {result && (
            <div>
              <div className="card" style={{ marginBottom: 12 }}>
                <div className="label">Image Condition</div>
                <div className="value" style={{ fontSize: "1.2rem" }}>{result.hazard.replace(/_/g, " ")}</div>
              </div>
              <div className="card" style={{ marginBottom: 12 }}>
                <div className="label">Confidence</div>
                <div className="value">{result.confidence}%</div>
              </div>
              <div className="card">
                <div className="label">Environmental Risk</div>
                <span className={`risk-badge risk-${result.risk_level}`}>{result.risk_level}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
