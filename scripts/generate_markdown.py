import json

def generate_markdown_table(data):
    """Generates a Markdown table from the compatibility list data."""
    
    rating_map = {
        0: "Perfect",
        1: "Playable",
        3: "Ingame",
        4: "Intro/Menu",
        5: "Won't Boot"
    }

    # Create the table header
    table = "| Game Name | Title ID | Status |\n"
    table += "|---|---|---|\n"
    
    # Populate the table rows
    for item in data:
        game_name = item.get('directory', 'N/A')
        
        # Safely get the release ID
        try:
            release_id = item['releases'][0]['id']
        except (IndexError, KeyError):
            release_id = 'N/A'
            
        # Get the compatibility status string, with a fallback for unknown numbers
        status_num = item.get('compatibility', -1)
        status_str = rating_map.get(status_num, "Unknown")
        
        table += f"| {game_name} | {release_id} | {status_str} |\n"
        
    return table

def main():
    """Reads the JSON file and writes the Markdown file."""
    try:
        with open('compatibility_list.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: compatibility_list.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from compatibility_list.json.")
        return

    # Build the full Markdown content
    markdown_content = "# Citron Compatibility List\n\n"
    markdown_content += "This list is automatically generated from user reports and is updated in real-time.\n\n"
    markdown_content += generate_markdown_table(data) # The data is already sorted by your generate_list.py

    with open('COMPATIBILITY.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("Successfully generated COMPATIBILITY.md")

if __name__ == "__main__":
    main()
