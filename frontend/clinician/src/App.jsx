import { useEffect, useState } from "react";

import { fetchAlerts, login } from "./api.js";

export default function App() {
  const [token, setToken] = useState("");
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("Login to view alerts.");
  const [error, setError] = useState("");

  function formatTimestamp(value) {
    if (!value) {
      return "";
    }
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }
    const formatter = new Intl.DateTimeFormat("en-GB", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
    return formatter.format(parsed).replace(",", "");
  }

  async function handleLogin(event) {
    event.preventDefault();
    setError("");
    try {
      const result = await login(loginForm.username, loginForm.password, "clinician");
      setToken(result.token);
      setStatus("Connected. Monitoring alerts...");
    } catch (err) {
      setError(err.message);
    }
  }

  async function refreshAlerts() {
    if (!token) {
      return;
    }
    try {
      const result = await fetchAlerts(token);
      setAlerts(result.alerts || []);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    if (!token) {
      return undefined;
    }
    refreshAlerts();
    const interval = setInterval(refreshAlerts, 5000);
    return () => clearInterval(interval);
  }, [token]);

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">HealthFlow AWS Clinician</p>
        <h1>Alert dashboard</h1>
        <p className="subtitle">Real-time alerts refresh every five seconds.</p>
      </header>

      {!token ? (
        <form className="card" onSubmit={handleLogin}>
          <h2>Login</h2>
          <label>
            Username
            <input
              value={loginForm.username}
              onChange={(event) =>
                setLoginForm({ ...loginForm, username: event.target.value })
              }
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={loginForm.password}
              onChange={(event) =>
                setLoginForm({ ...loginForm, password: event.target.value })
              }
              required
            />
          </label>
          <button type="submit">Access dashboard</button>
        </form>
      ) : (
        <section className="card">
          <div className="card-header">
            <h2>Active alerts</h2>
            {status ? <div className="toast info">{status}</div> : null}
            {error ? <div className="toast error">{error}</div> : null}
            <button type="button" className="ghost" onClick={refreshAlerts}>
              Refresh
            </button>
          </div>
          <div className="table">
            <div className="row head">
              <span>Patient</span>
              <span>Score</span>
              <span>Message</span>
              <span>Created</span>
            </div>
            {alerts.length === 0 ? (
              <div className="row empty">No alerts yet.</div>
            ) : (
              alerts.map((alert) => (
                <div key={alert.alert_id} className="row">
                  <span>{alert.patient_login || "-"}</span>
                  <span>{alert.score}</span>
                  <span>{alert.message}</span>
                  <span>{formatTimestamp(alert.created_at)}</span>
                </div>
              ))
            )}
          </div>
        </section>
      )}

    </div>
  );
}
