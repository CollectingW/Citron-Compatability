import os
import requests
import json
import re

# Mapping human words to the emulator's ID system
STATUS_MAP = {
    "perfect": 0,
    "playable": 1,
    "ingame": 3,
    "intro": 4,
    "wontboot": 5
}

def main():
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")
    
    # Fetch all issues with the 'verified' label
    url = f"https://api.github.com/repos/{repo}/issues?labels=verified&state=all"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    issues = response.json()

    compat_data = {}

    for issue in issues:
        title = issue.get("title", "")
        body = issue.get("body", "").lower()
        
        # Regex to find Title ID in brackets [01006A800016E000]
        id_match = re.search(r"\[([0-9A-Fa-f]{16})\]", title)
        if not id_match:
            continue
            
        title_id = id_match.group(1).upper()
        game_name = title.split("]", 1)[1].strip() if "]" in title else "Unknown Game"

        # Determine status from body
        status_value = 99
        # Look for the bolded Status line
        for key, value in STATUS_MAP.items():
            if f"**status:** {key}" in body:
                status_value = value
                break

        # Add to structure
        compat_data[title_id] = {
            "compatibility": status_value,
            "directory": game_name,
            "releases": [{"id": title_id}]
        }

    # Convert back to the list format the emulator expects
    final_list = list(compat_data.values())

    with open("compatibility_list.json", "w") as f:
        json.dump(final_list, f, indent=2)

if __name__ == "__main__":
    main()
