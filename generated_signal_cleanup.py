#!/usr/bin/env python3
"""
Generated Signal Cleanup Script for IMG Factory 1.5
This script comments out conflicting signal connections
"""

import re
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create backup of file"""
    backup_path = str(file_path) + ".backup"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backed up: {file_path}")

def clean_signals_in_file(file_path):
    """Clean signal connections in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Patterns to comment out
        patterns_to_comment = [
            r"(\s*)(.*connect_signals.*\.connect.*)",
            r"(\s*)(.*_connect_signals.*\.connect.*)",
            r"(\s*)(.*connect_table_signals.*\.connect.*)",
            r"(\s*)(.*disconnect_table_signals.*\.connect.*)",
            r"(\s*)(.*get_selection_count.*\.connect.*)",
        ]
        
        # Comment out conflicting patterns
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for pattern in patterns_to_comment:
                if re.search(pattern, line) and not line.strip().startswith('#'):
                    lines[i] = re.sub(r'^(\s*)', r'\1# SIGNAL_CLEANUP: ', line)
                    changes_made = True
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"✓ Cleaned: {file_path}")
            return True
        
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
    
    return False

def main():
    """Main cleanup function"""
    files_to_clean = [
        "/home/x2/Documents/GitHub/Img Factory 1.5/app_settings_system.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/col_editor.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/col_integration.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/col_utilities.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/img_combined_open_dialog.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/img_core_classes.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/img_creator.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/img_formats.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/img_templates.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/components/unified_signal_handler.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/button_panel.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/buttons.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/col_gui_integration.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/control_panels.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/dialogs.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/gui_layout.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/gui_settings.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/log_panel.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/menu.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/gui/panels.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/imgfactory.py",
        "/home/x2/Documents/GitHub/Img Factory 1.5/main_col_integration.py",
    ]
    
    print(f"🧹 Cleaning {len(files_to_clean)} files...")
    
    for file_path in files_to_clean:
        backup_file(file_path)
        clean_signals_in_file(file_path)
    
    print("✅ Cleanup complete!")
    print("Next: Use unified signal handler for all connections")

if __name__ == "__main__":
    main()
