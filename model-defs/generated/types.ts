// Generated types

export type Patient = {
  patient_id: string;
  patient_login: string;
  email?: string;
  created_at: string;
};

export type Observation = {
  observation_id: string;
  patient_id: string;
  patient_login: string;
  score: number;
  created_at: string;
};

export type Alert = {
  alert_id: string;
  patient_id: string;
  patient_login: string;
  score: number;
  message: string;
  created_at: string;
};
