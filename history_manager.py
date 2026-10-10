import json
from datetime import datetime


HISTORY_FILE = "history.json"

def save_entry(transcript: str, response: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "transcript": transcript,
        "response": response
    }
    data = load_history()
    data.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []