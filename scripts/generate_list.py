import os
import requests
import json
import re

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
                    if entry.get("releases"):
                        tid = entry["releases"][0]["id"].upper()
                        compat_data[tid] = entry
        except Exception as e:
            print(f"Note: Could not parse existing list, starting fresh. Error: {e}")

    # Fetch 'verified' issues from GitHub
    url = f"https://api.github.com/repos/{repo}/issues?labels=verified&state=all"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        issues = response.json()
        for issue in issues:
            title = issue.get("title", "")
            body = issue.get("body", "")
            if not body:
                continue
            
            body_lower = body.lower()
            
            id_match = re.search(r"### Title ID\s+([0-9A-Fa-f]{16})", body)
            
            if not id_match:
                id_match = re.search(r"\[([0-9A-Fa-f]{16})\]", title)
                if not id_match:
                    continue
                
            title_id = id_match.group(1).upper()

            game_name = re.sub(r"\[[0-9A-Fa-f]{16}\]", "", title).strip()

            # Determine status
            status_value = 99 
            for key, value in STATUS_MAP.items():
                # Regex looks for "### Status" followed by any amount of space/newlines, 
                # then the specific status word.
                status_pattern = rf"### status\s+{re.escape(key)}"
                if re.search(status_pattern, body_lower):
                    status_value = value
                    break
                
                # Legacy check for manual issues
                if f"status:** {key}" in body_lower:
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
