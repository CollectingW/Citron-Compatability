import os
import requests
import json
import re

# Mapping human words from the C++ Dialog to the emulator's ID system
STATUS_MAP = {
    "perfect": 0,
    "playable": 1,
    "ingame": 3,
    "intro/menu": 4,
    "won't boot": 5
}

def main():
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    file_path = "compatibility_list.json"
    
    compat_data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_list = json.load(f)
                for entry in existing_list:
                    # Use the first release ID as the key
                    if entry.get("releases"):
                        tid = entry["releases"][0]["id"].upper()
                        compat_data[tid] = entry
        except Exception as e:
            print(f"Note: Could not parse existing list, starting fresh. Error: {e}")

    # --- 2. Fetch 'verified' issues from GitHub ---
    url = f"https://api.github.com/repos/{repo}/issues?labels=verified&state=all"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        issues = response.json()
        for issue in issues:
            title = issue.get("title", "")
            body = issue.get("body", "").lower()
            
            # Extract Title ID [0100...]
            id_match = re.search(r"\[([0-9A-Fa-f]{16})\]", title)
            if not id_match:
                continue
                
            title_id = id_match.group(1).upper()
            game_name = title.split("]", 1)[1].strip() if "]" in title else "Unknown Game"

            # Determine status
            status_value = 99 
            for key, value in STATUS_MAP.items():
                if f"status:** {key}" in body:
                    status_value = value
                    break

            # Add or update the entry
            compat_data[title_id] = {
                "compatibility": status_value,
                "directory": game_name,
                "releases": [{"id": title_id}]
            }

    # Sort alphabetically by game name
    final_list = sorted(compat_data.values(), key=lambda x: x['directory'].lower())

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
