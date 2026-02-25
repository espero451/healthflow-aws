import { datetimeField, model, numberField, stringField } from "./framework.js";

export const Patient = model("Patient", {
  patient_id: stringField(),
  patient_login: stringField(),
  email: stringField({ required: false }),
  created_at: datetimeField()
});

export const Observation = model("Observation", {
  observation_id: stringField(),
  patient_id: stringField(),
  patient_login: stringField(),
  score: numberField(),
  created_at: datetimeField()
});

export const Alert = model("Alert", {
  alert_id: stringField(),
  patient_id: stringField(),
  patient_login: stringField(),
  score: numberField(),
  message: stringField(),
  created_at: datetimeField()
});

export const models = [Patient, Observation, Alert];
