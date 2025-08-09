import json
import os

def generate_policy(cookies):
    # Path to cookie_db.json (1 level above current directory)
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cookie_db.json"))

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"cookie_db.json not found at: {db_path}")

    # Load and normalize the cookie database (keys to lowercase)
    with open(db_path, "r", encoding="utf-8") as f:
        raw_db = json.load(f)
        cookie_db = {k.lower(): v for k, v in raw_db.items()}

    policy = []
    for cookie in cookies:
        if "error" in cookie.get("name", "").lower():
            return [cookie]  # Return error for frontend to display

        # Normalize the cookie name
        cookie_name = cookie['name'].strip().lower()

        # Lookup from the database
        info = cookie_db.get(cookie_name, {
            "category": "Unclassified",
            "description": "No description available.",
            "duration": "Unknown",
            "type": "N/A",
            "function": "N/A",
            "ownership": "N/A",
            "risk_category": "N/A"
        })

        # Optional logging of unknown cookies for improvement
        if cookie_name not in cookie_db:
            print(f"[WARNING] Unclassified cookie detected: {cookie_name}")


        # Append structured info to the policy list
        policy.append({
            "name": cookie.get("name", "N/A"),
            "domain": cookie.get("domain", "N/A"),
            "category": info.get("category", "Unclassified"),
            "description": info.get("description", "No description available."),
            "duration": info.get("duration", "Unknown"),
            "type": info.get("type", "N/A"),
            "function": info.get("function", "N/A"),
            "ownership": info.get("ownership", "N/A"),
            "risk_category": info.get("risk_category", "N/A")
        })

    return policy
