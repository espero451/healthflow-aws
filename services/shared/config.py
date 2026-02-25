import os

# --- Configuration ----------------------------------------------------

def get_env(name: str, default: str) -> str:
    # Read an environment variable with a fallback.
    return os.getenv(name, default)


EVENT_BUS_NAME = get_env("EVENT_BUS_NAME", "healthflow-bus")
EVENTS_TABLE = get_env("EVENTS_TABLE", "healthflow-events")
USERS_TABLE = get_env("USERS_TABLE", "healthflow-users")
PATIENTS_TABLE = get_env("PATIENTS_TABLE", "healthflow-patients")
OBSERVATIONS_TABLE = get_env("OBSERVATIONS_TABLE", "healthflow-observations")
ALERTS_TABLE = get_env("ALERTS_TABLE", "healthflow-alerts")
JWT_SECRET = get_env("JWT_SECRET", "dev-secret")
ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", "7"))
