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

    # Fetch 'verified' issues
    url = f"https://api.github.com/repos/{repo}/issues?labels=verified&state=all&per_page=100"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        issues = response.json()
        
        # IMPORTANT: Sort issues by number (ascending) 
        # This ensures that newer issues overwrite older ones for the same Title ID
        issues.sort(key=lambda x: x['number'])

        for issue in issues:
            title = issue.get("title", "")
            body = issue.get("body", "")
            if not body:
                continue
            
            body_lower = body.lower()
            
            # Extract Title ID
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
                status_pattern = rf"### status\s+{re.escape(key)}"
                if re.search(status_pattern, body_lower) or f"status:** {key}" in body_lower:
                    status_value = value
                    break

            # LOGGING: Check if we are updating or adding
            if title_id in compat_data:
                old_status = compat_data[title_id].get("compatibility")
                if old_status != status_value:
                    print(f"Updating {game_name} ({title_id}): Status {old_status} -> {status_value}")
            else:
                print(f"Adding new game: {game_name} ({title_id})")

            # Update the entry (Overwrites if Title ID exists)
            compat_data[title_id] = {
                "compatibility": status_value,
                "directory": game_name,
                "releases": [{"id": title_id}]
            }

    # Sort alphabetically by game name for a clean JSON file
    final_list = sorted(compat_data.values(), key=lambda x: x['directory'].lower())

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
