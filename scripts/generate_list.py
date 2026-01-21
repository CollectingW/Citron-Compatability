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
    
    # We fetch ALL issues that have the 'verified' label
    url = f"https://api.github.com/repos/{repo}/issues?labels=verified&state=all"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return

    issues = response.json()
    compat_data = {}

    for issue in issues:
        title = issue.get("title", "")
        body = issue.get("body", "").lower()
        
        # 1. Extract Title ID from brackets
        id_match = re.search(r"\[([0-9A-Fa-f]{16})\]", title)
        if not id_match:
            continue
            
        title_id = id_match.group(1).upper()
        
        # 2. Extract Game Name
        game_name = title.split("]", 1)[1].strip() if "]" in title else "Unknown Game"

        # 3. Determine status by looking for "**Status:** Word" in the body
        status_value = 99 # Default: Not Tested
        for key, value in STATUS_MAP.items():
            if f"status:** {key}" in body:
                status_value = value
                break

        # 4. Add to the dictionary
        compat_data[title_id] = {
            "compatibility": status_value,
            "directory": game_name,
            "releases": [{"id": title_id}]
        }

    # Convert dictionary to a list and sort by name
    final_list = sorted(compat_data.values(), key=lambda x: x['directory'])

    with open("compatibility_list.json", "w") as f:
        json.dump(final_list, f, indent=2)

if __name__ == "__main__":
    main()
