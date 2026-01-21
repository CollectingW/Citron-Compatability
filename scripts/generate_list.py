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
            print(f"Note: Starting fresh. Error: {e}")

    # PAGINATION LOGIC: Loop through all pages of issues
    headers = {"Authorization": f"token {token}"}
    all_issues = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues?labels=verified&state=all&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        data = response.json()
        if not data: # No more issues
            break
        all_issues.extend(data)
        page += 1

    # Sort issues by number (ascending) so newest reports overwrite older ones
    all_issues.sort(key=lambda x: x['number'])

    for issue in all_issues:
        title = issue.get("title", "")
        body = issue.get("body", "")
        if not body:
            continue
        
        # Extract Title ID - more flexible regex to handle potential newlines or spaces
        id_match = re.search(r"### Title ID\s+([0-9A-Fa-f]{16})", body, re.IGNORECASE)
        if not id_match:
            # Fallback to checking title for [TID]
            id_match = re.search(r"([0-9A-Fa-f]{16})", title)
            if not id_match:
                print(f"Skipping Issue #{issue['number']}: No valid Title ID found.")
                continue
            
        title_id = id_match.group(1).upper()
        game_name = re.sub(r"\[[0-9A-Fa-f]{16}\]", "", title).strip()

        # Determine status
        status_value = 99 
        body_lower = body.lower()
        for key, value in STATUS_MAP.items():
            # Check for header format or the bolded status format
            status_pattern = rf"### status\s+{re.escape(key)}"
            if re.search(status_pattern, body_lower) or f"status:** {key}" in body_lower:
                status_value = value
                break

        if status_value == 99:
            print(f"Skipping Issue #{issue['number']}: Could not determine Status.")
            continue

        # Update the entry
        compat_data[title_id] = {
            "compatibility": status_value,
            "directory": game_name,
            "releases": [{"id": title_id}]
        }

    # Sort alphabetically by game name
    final_list = sorted(compat_data.values(), key=lambda x: x['directory'].lower())

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated list with {len(final_list)} entries.")

if __name__ == "__main__":
    main()
