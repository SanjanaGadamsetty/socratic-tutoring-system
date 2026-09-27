"""
Script to remove emojis from all markdown files
"""
import re
import os
from pathlib import Path

def remove_emojis(text):
    """Remove emojis from text"""
    # Emoji pattern
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', text)

def process_file(filepath):
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove emojis
        new_content = remove_emojis(content)

        # Only write if content changed
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    """Main function"""
    project_root = Path(__file__).parent

    # Find all markdown files
    md_files = []
    for pattern in ['*.md', '**/*.md']:
        md_files.extend(project_root.glob(pattern))

    # Exclude node_modules
    md_files = [f for f in md_files if 'node_modules' not in str(f)]

    print(f"Found {len(md_files)} markdown files")
    print()

    updated = 0
    for md_file in md_files:
        if process_file(md_file):
            print(f"Updated: {md_file.relative_to(project_root)}")
            updated += 1

    print()
    print(f"Updated {updated} files")
    print("Done!")

if __name__ == "__main__":
    main()
