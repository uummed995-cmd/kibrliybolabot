import json
import os
from datetime import datetime
from config import DB_FILE

def _load():
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _save(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get(key, default=None):
    data = _load()
    return data.get(key, default)

def set(key, value):
    data = _load()
    data[key] = value
    _save(data)

def get_setting(key, default=None):
    settings = get("settings", {})
    return settings.get(key, default)

def set_setting(key, value):
    data = _load()
    if "settings" not in data:
        data["settings"] = {}
    data["settings"][key] = value
    _save(data)

def get_bot_lang():
    return get_setting("bot_lang", "uz")

def set_bot_lang(lang):
    set_setting("bot_lang", lang)

def get_user(user_id):
    users = get("users", {})
    return users.get(str(user_id), {})

def set_user(user_id, user_data):
    data = _load()
    if "users" not in data:
        data["users"] = {}
    data["users"][str(user_id)] = user_data
    _save(data)

def get_warns(user_id, chat_id):
    warns = get("warns", {})
    return warns.get(f"{chat_id}_{user_id}", 0)

def add_warn(user_id, chat_id):
    data = _load()
    if "warns" not in data:
        data["warns"] = {}
    key = f"{chat_id}_{user_id}"
    data["warns"][key] = data["warns"].get(key, 0) + 1
    _save(data)
    return data["warns"][key]

def reset_warns(user_id, chat_id):
    data = _load()
    if "warns" not in data:
        data["warns"] = {}
    key = f"{chat_id}_{user_id}"
    data["warns"][key] = 0
    _save(data)

def get_user_score(user_id):
    scores = get("scores", {})
    return scores.get(str(user_id), 0)

def add_user_score(user_id, points):
    data = _load()
    if "scores" not in data:
        data["scores"] = {}
    data["scores"][str(user_id)] = data["scores"].get(str(user_id), 0) + points
    _save(data)

def get_last_bonus(user_id):
    bonuses = get("last_bonus", {})
    return bonuses.get(str(user_id))

def set_last_bonus(user_id):
    data = _load()
    if "last_bonus" not in data:
        data["last_bonus"] = {}
    data["last_bonus"][str(user_id)] = datetime.now().isoformat()
    _save(data)

def get_tickets():
    return get("tickets", {})

def create_ticket(ticket_id, user_id, username, text, time_str):
    data = _load()
    if "tickets" not in data:
        data["tickets"] = {}
    data["tickets"][str(ticket_id)] = {
        "user_id": user_id,
        "username": username,
        "text": text,
        "time": time_str,
        "status": "open",
        "messages": []
    }
    _save(data)

def close_ticket(ticket_id):
    data = _load()
    if "tickets" in data and str(ticket_id) in data["tickets"]:
        data["tickets"][str(ticket_id)]["status"] = "closed"
        _save(data)

def get_ticket(ticket_id):
    tickets = get("tickets", {})
    return tickets.get(str(ticket_id))

def get_mandatory_channels():
    return get_setting("mandatory_channels", [])

def set_mandatory_channels(channels):
    set_setting("mandatory_channels", channels)

def get_group_id():
    return get_setting("group_id")

def set_group_id(group_id):
    set_setting("group_id", group_id)

def get_group_admins():
    return get_setting("group_admins", [])

def set_group_admins(admins):
    set_setting("group_admins", admins)

def get_banned_users():
    return get("banned_users", [])

def ban_user(user_id):
    data = _load()
    if "banned_users" not in data:
        data["banned_users"] = []
    if user_id not in data["banned_users"]:
        data["banned_users"].append(user_id)
    _save(data)

def unban_user(user_id):
    data = _load()
    if "banned_users" in data and user_id in data["banned_users"]:
        data["banned_users"].remove(user_id)
    _save(data)

def get_stats():
    return get("stats", {"total_users": 0, "total_messages": 0, "total_games": 0})

def increment_stat(key):
    data = _load()
    if "stats" not in data:
        data["stats"] = {"total_users": 0, "total_messages": 0, "total_games": 0}
    data["stats"][key] = data["stats"].get(key, 0) + 1
    _save(data)

def register_user(user_id, username, full_name):
    data = _load()
    if "users" not in data:
        data["users"] = {}
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "joined": datetime.now().isoformat(),
            "score": 0
        }
        if "stats" not in data:
            data["stats"] = {"total_users": 0}
        data["stats"]["total_users"] = data["stats"].get("total_users", 0) + 1
    _save(data)

def get_all_users():
    return get("users", {})
