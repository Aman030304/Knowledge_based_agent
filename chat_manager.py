import os
import json
import uuid
from datetime import datetime

CHATS_DIR = "chats"

def _ensure_chats_dir():
    """Ensures the chats directory exists."""
    if not os.path.exists(CHATS_DIR):
        os.makedirs(CHATS_DIR)

def save_chat(chat_id, name, messages):
    """Saves a chat to a JSON file."""
    _ensure_chats_dir()
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    
    chat_data = {
        "id": chat_id,
        "name": name,
        "updated_at": datetime.now().isoformat(),
        "messages": messages
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=4, ensure_ascii=False)

def load_chat(chat_id):
    """Loads a chat from a JSON file."""
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_chats():
    """Lists all available chats, sorted by last update."""
    _ensure_chats_dir()
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(CHATS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chat_data = json.load(f)
                    chats.append({
                        "id": chat_data.get("id"),
                        "name": chat_data.get("name", "Untitled Chat"),
                        "updated_at": chat_data.get("updated_at", "")
                    })
            except Exception:
                continue
    
    # Sort by updated_at descending
    chats.sort(key=lambda x: x["updated_at"], reverse=True)
    return chats

def delete_chat(chat_id):
    """Deletes a chat file."""
    file_path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def rename_chat(chat_id, new_name):
    """Renames a chat."""
    chat_data = load_chat(chat_id)
    if chat_data:
        chat_data["name"] = new_name
        save_chat(chat_id, new_name, chat_data["messages"])
        return True
    return False

def create_new_chat():
    """Creates a new chat ID and initial structure."""
    chat_id = str(uuid.uuid4())
    save_chat(chat_id, "New Chat", [])
    return chat_id
