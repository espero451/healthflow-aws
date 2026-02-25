import { test, expect } from "@playwright/test";

test("API flow emits alerts", async ({ request }) => {
  const apiBase = process.env.API_BASE_URL;
  test.skip(!apiBase, "Missing API_BASE_URL");

  const patientLogin = await request.post(`${apiBase}/login`, {
    data: { username: "patient1", password: "demo", role: "patient" }
  });
  expect(patientLogin.ok()).toBeTruthy();
  const patientBody = await patientLogin.json();
  const patientToken = patientBody.token;

  await request.post(`${apiBase}/observations`, {
    data: { patient_id: patientBody.patient_id, score: 9 },
    headers: { Authorization: `Bearer ${patientToken}` }
  });

  const clinicianLogin = await request.post(`${apiBase}/login`, {
    data: { username: "clinician1", password: "demo", role: "clinician" }
  });
  expect(clinicianLogin.ok()).toBeTruthy();
  const clinicianBody = await clinicianLogin.json();

  const alerts = await request.get(`${apiBase}/alerts`, {
    headers: { Authorization: `Bearer ${clinicianBody.token}` }
  });
  expect(alerts.ok()).toBeTruthy();
  const alertBody = await alerts.json();
  expect(Array.isArray(alertBody.alerts)).toBeTruthy();
});
