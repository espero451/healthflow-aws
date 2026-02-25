const API_BASE = import.meta.env.VITE_API_BASE_URL;

async function request(path, options = {}) {
  if (!API_BASE) {
    throw new Error("Missing VITE_API_BASE_URL");
  }
  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

export async function login(username, password, role) {
  return request("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role })
  });
}

export async function submitObservation(token, patientId, score) {
  return request("/observations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ patient_id: patientId, score })
  });
}
