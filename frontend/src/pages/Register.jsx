import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm_password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const passwordStrength = () => {
    const p = form.password;
    if (!p) return "";
    let score = 0;
    if (p.length >= 8) score++;
    if (/[A-Z]/.test(p)) score++;
    if (/[a-z]/.test(p)) score++;
    if (/\d/.test(p)) score++;
    if (/[^A-Za-z0-9]/.test(p)) score++;
    return ["Very weak", "Weak", "Fair", "Good", "Strong", "Very strong"][score];
  };

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!form.name || !form.email || !form.password || !form.confirm_password) {
      setError("Please fill in all fields.");
      return;
    }
    if (form.password !== form.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/register", form);
      setSuccess("Registration successful! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create your account</h1>
        <p className="subtitle">Urban Environmental Intelligence Platform</p>

        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}

        <form onSubmit={submit}>
          <div className="field">
            <label>Full Name</label>
            <input type="text" value={form.name} onChange={update("name")} placeholder="Jane Doe" />
          </div>
          <div className="field">
            <label>Email</label>
            <input type="email" value={form.email} onChange={update("email")} placeholder="jane@example.com" />
          </div>
          <div className="field">
            <label>Password {form.password && <span style={{ color: "#8ba0c0" }}>— {passwordStrength()}</span>}</label>
            <input type="password" value={form.password} onChange={update("password")} placeholder="At least 8 characters" />
          </div>
          <div className="field">
            <label>Confirm Password</label>
            <input type="password" value={form.confirm_password} onChange={update("confirm_password")} placeholder="Re-enter password" />
          </div>
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <div className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </div>
      </div>
    </div>
  );
}
