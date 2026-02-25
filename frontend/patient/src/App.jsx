import { useState } from "react";

import { login, submitObservation } from "./api.js";

export default function App() {
  const [token, setToken] = useState("");
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [patientId, setPatientId] = useState("");
  const [score, setScore] = useState(5);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const result = await login(loginForm.username, loginForm.password, "patient");
      setToken(result.token);
      setPatientId(result.patient_id || "");
      setMessage(result.new_user ? "Account created." : "Logged in.");
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleObservation(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await submitObservation(token, patientId, score);
      setMessage("Observation submitted.");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">HealthFlow AWS Patient</p>
        <h1>Daily symptom check-in</h1>
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
          <button type="submit">Sign in</button>
        </form>
      ) : (
        <form className="card" onSubmit={handleObservation}>
          <h2>Submit symptom score</h2>
          <label>
            Score (1-10)
            <input
              type="number"
              min="1"
              max="10"
              value={score}
              onChange={(event) => setScore(Number(event.target.value))}
              required
            />
          </label>
          <button type="submit" disabled={!patientId}>
            Submit score
          </button>
          {patientId ? <p className="hint">Patient ID: {patientId}</p> : null}
        </form>
      )}

      {message ? <div className="toast success">{message}</div> : null}
      {error ? <div className="toast error">{error}</div> : null}
    </div>
  );
}
