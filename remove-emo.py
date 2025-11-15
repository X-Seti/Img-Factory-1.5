python3 << 'EOF'
import os
import glob

emojis = {
    '': '',
    '': '',
    '': '',
    '': '',
    '': ''
}

for filepath in glob.glob('**/*.py', recursive=True):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = content
        for emoji, replacement in emojis.items():
            modified = modified.replace(emoji, replacement)

        if modified != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified)
            print(f"Fixed: {filepath}")
    except Exception as e:
        print(f"Error in {filepath}: {e}")
EOF
