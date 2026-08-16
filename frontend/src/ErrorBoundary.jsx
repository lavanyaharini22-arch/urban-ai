import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error("Dashboard render error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
          background: "#0a0e17", color: "#e6ecf5", fontFamily: "system-ui, sans-serif", padding: 24,
        }}>
          <div style={{ maxWidth: 520, textAlign: "center" }}>
            <h2 style={{ marginBottom: 12 }}>Something went wrong</h2>
            <p style={{ color: "#8ba0c0", fontSize: "0.9rem", marginBottom: 16 }}>
              A component failed to render. Check the browser console (F12) for the exact
              error, and confirm the backend is running at <code>http://localhost:8000</code>.
            </p>
            <pre style={{
              textAlign: "left", background: "#151d2e", border: "1px solid #223047",
              borderRadius: 8, padding: 12, fontSize: "0.78rem", overflowX: "auto",
            }}>
              {String(this.state.error?.message || this.state.error)}
            </pre>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: 16, padding: "10px 18px", background: "#3b82f6", color: "#04101f",
                border: "none", borderRadius: 8, fontWeight: 600, cursor: "pointer",
              }}
            >
              Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
