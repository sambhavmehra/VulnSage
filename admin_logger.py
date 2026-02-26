"""
Admin Logging & Panel
Tracks user registrations, logins, and all activity.
Admin users can view all logs from the dashboard.
"""

import json
import os
from datetime import datetime

LOGS_FILE = "admin_logs.json"


def _load_logs() -> dict:
    """Load all logs from file."""
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"registrations": [], "logins": [], "activity": []}


def _save_logs(logs: dict):
    """Save logs to file."""
    try:
        with open(LOGS_FILE, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not save logs: {e}")


def log_registration(username: str, name: str):
    """Log a new user registration."""
    logs = _load_logs()
    logs["registrations"].append({
        "username": username,
        "name": name,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    _save_logs(logs)


def log_login(username: str, role: str, success: bool):
    """Log a login attempt."""
    logs = _load_logs()
    logs["logins"].append({
        "username": username,
        "role": role,
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    # Keep last 500 login entries
    logs["logins"] = logs["logins"][-500:]
    _save_logs(logs)


def log_activity(username: str, action: str):
    """Log a user activity."""
    logs = _load_logs()
    logs["activity"].append({
        "username": username,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    # Keep last 1000 activity entries
    logs["activity"] = logs["activity"][-1000:]
    _save_logs(logs)


def get_all_logs() -> dict:
    """Get all logs for admin viewing."""
    return _load_logs()


def get_registered_users_count() -> int:
    logs = _load_logs()
    return len(logs["registrations"])


def get_total_logins() -> int:
    logs = _load_logs()
    return len([l for l in logs["logins"] if l["success"]])


def get_failed_logins() -> int:
    logs = _load_logs()
    return len([l for l in logs["logins"] if not l["success"]])
