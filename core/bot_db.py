import json
import os
import tempfile
import threading
import time
from typing import Dict, Any

DB_FILE = "bots_db.json"
TELEMETRY_FILE = "telemetry.json"
db_lock = threading.Lock()

ASYNC_RESULTS: Dict[str, str] = {}


def load_data(file_path: str, default_val: Any) -> Any:
    with db_lock:
        if not os.path.exists(file_path): return default_val
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default_val


def save_data(file_path: str, data: Any):
    with db_lock:
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(file_path)) or '.')
        with os.fdopen(fd, 'w', encoding="utf-8") as f: json.dump(data, f, indent=4)
        os.replace(tmp_path, file_path)


def save_bot(target_id: str, webhook_url: str, secret_key: str, metadata: dict = None):
    bots = load_data(DB_FILE, {})
    bots[target_id] = {
        "webhook_url": webhook_url,
        "secret_key": secret_key,
        "metadata": metadata or {},
        "last_seen": time.time()
    }
    save_data(DB_FILE, bots)


def load_bots() -> Dict[str, Dict[str, Any]]:
    return load_data(DB_FILE, {})


def remove_bot(target_id: str):
    bots = load_data(DB_FILE, {})
    if target_id in bots:
        del bots[target_id]
        save_data(DB_FILE, bots)


def log_telemetry(ip: str, user_agent: str):
    data = load_data(TELEMETRY_FILE, {"hits": [], "total_views": 0, "decay_score": 100.0})
    data["total_views"] += 1
    data["hits"].append({"ip": ip, "ua": user_agent, "ts": time.time()})

    if len(data["hits"]) > 1000: data["hits"] = data["hits"][-1000:]

    bots_count = len(load_bots())
    if data["total_views"] > 0:
        raw_rate = (bots_count / data["total_views"]) * 100
        data["decay_score"] = (data["decay_score"] * 0.9) + (raw_rate * 0.1)

    save_data(TELEMETRY_FILE, data)


def get_telemetry_stats() -> dict:
    return load_data(TELEMETRY_FILE, {"hits": [], "total_views": 0, "decay_score": 0.0})
