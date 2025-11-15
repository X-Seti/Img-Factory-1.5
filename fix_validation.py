#!/usr/bin/env python3
#this belongs in root /fix_validation.py - Version: 1
# X-Seti - November15 2025 - IMG Factory 1.5 - Auto-fix file validation

"""
Automated Fix Script - Replace hardcoded IMG checks with universal validation
More reliable than sed for multi-line Python code
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# Files to fix
FILES_TO_FIX = [
    "apps/core/core.py",
    "apps/core/dump.py",
    "apps/core/export_via.py",
    "apps/core/rebuild.py",
    "apps/core/remove.py",
    "apps/core/remove_via.py",
    "apps/core/rw_analysis_trigger.py",
    "apps/core/imgcol_convert.py",
    "apps/core/imgcol_rename.py",
    "apps/core/imgcol_replace.py",
    "apps/core/impotr.py",
    "apps/core/rename.py",
    "apps/core/save_entry.py",
    "apps/methods/img_import_system.py"
]

# Import statement to add
IMPORT_LINE = "from apps.methods.file_validation import validate_img_file, validate_any_file, get_selected_entries_for_operation\n"

# Pattern to match the old validation code
OLD_PATTERN = re.compile(
    r'(\s+)if not hasattr\(main_window, [\'"]current_img[\'"]\) or not main_window\.current_img:\s*\n'
    r'\s+QMessageBox\.warning\(main_window, [\'"]No IMG File[\'"], [\'"]Current tab does not contain an IMG file[\'"].*?\)\s*\n'
    r'\s+return False',
    re.MULTILINE
)

# Replacement code
NEW_VALIDATION = """{indent}# FIXED: Use universal validation
{indent}success, img_file = validate_img_file(main_window, "{operation}")
{indent}if not success:
{indent}    return False"""


def backup_files(files, backup_dir):
    """Create backups of all files"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    backed_up = []
    
    for file_path in files:
        if os.path.exists(file_path):
            backup_path = backup_dir / os.path.basename(file_path)
            shutil.copy2(file_path, backup_path)
            backed_up.append(file_path)
    
    return backed_up


def add_import_if_needed(content, file_path):
    """Add import statement if not already present"""
    if 'from apps.methods.file_validation import' in content:
        return content, False
    
    # Find the last import line
    lines = content.split('\n')
    last_import_idx = -1
    
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            last_import_idx = i
    
    if last_import_idx >= 0:
        # Insert after last import
        lines.insert(last_import_idx + 1, IMPORT_LINE.rstrip())
        return '\n'.join(lines), True
    else:
        # No imports found, add after docstring
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and i > 0:
                # Find closing docstring
                for j in range(i+1, len(lines)):
                    if '"""' in lines[j]:
                        lines.insert(j + 1, '\n' + IMPORT_LINE.rstrip())
                        return '\n'.join(lines), True
        
        # Fallback - add at top after shebang/comment
        lines.insert(0, IMPORT_LINE.rstrip())
        return '\n'.join(lines), True


def extract_operation_name(file_path, func_context):
    """Try to extract operation name from function name or context"""
    # Try to find function name
    func_match = re.search(r'def (\w+)\(', func_context)
    if func_match:
        func_name = func_match.group(1)
        # Convert function name to readable operation name
        # e.g., export_selected_function -> Export Selected
        name = func_name.replace('_function', '').replace('_', ' ').title()
        return name
    
    return "Operation"


def fix_validation_checks(content, file_path):
    """Replace old validation with new validation"""
    changes = 0
    
    def replacer(match):
        nonlocal changes
        changes += 1
        
        indent = match.group(1)
        # Get surrounding context to determine operation name
        start_pos = max(0, match.start() - 500)
        context = content[start_pos:match.start()]
        operation_name = extract_operation_name(file_path, context)
        
        return NEW_VALIDATION.format(indent=indent, operation=operation_name)
    
    new_content = OLD_PATTERN.sub(replacer, content)
    return new_content, changes


def replace_current_img_references(content):
    """Replace main_window.current_img with img_file (except in validation)"""
    changes = 0
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip lines that are part of validation check
        if 'hasattr(main_window' in line or 'validate_img_file' in line:
            new_lines.append(line)
            continue
        
        # Replace current_img with img_file
        if 'main_window.current_img' in line:
            new_line = line.replace('main_window.current_img', 'img_file')
            if new_line != line:
                changes += 1
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines), changes


def fix_file(file_path):
    """Fix a single file"""
    print(f"  📝 Fixing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"    ⚠️  File not found, skipping")
        return 0
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    content = original_content
    total_changes = 0
    
    # Step 1: Add import
    content, import_added = add_import_if_needed(content, file_path)
    if import_added:
        print(f"    + Added import statement")
        total_changes += 1
    
    # Step 2: Fix validation checks
    content, validation_changes = fix_validation_checks(content, file_path)
    if validation_changes > 0:
        print(f"    ✓ Replaced {validation_changes} validation check(s)")
        total_changes += validation_changes
    
    # Step 3: Replace current_img references
    content, ref_changes = replace_current_img_references(content)
    if ref_changes > 0:
        print(f"    ✓ Updated {ref_changes} current_img reference(s)")
        total_changes += ref_changes
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"    ✅ Applied {total_changes} change(s)")
    else:
        print(f"    ℹ️  No changes needed")
    
    print()
    return total_changes


def main():
    print("🔧 IMG Factory 1.5 - Fixing file validation checks")
    print("=" * 60)
    print()
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("apps/methods/old") / f"validation_backup_{timestamp}"
    
    print(f"📦 Creating backups in {backup_dir}")
    backed_up = backup_files(FILES_TO_FIX, backup_dir)
    print(f"  ✓ Backed up {len(backed_up)} file(s)")
    print()
    
    # Fix files
    print("🔄 Applying fixes...")
    print()
    
    total_changes = 0
    for file_path in FILES_TO_FIX:
        changes = fix_file(file_path)
        total_changes += changes
    
    print("=" * 60)
    print("✅ Validation fixes complete!")
    print(f"   Total changes: {total_changes}")
    print(f"   Backups in: {backup_dir}")
    print()
    print("⚠️  IMPORTANT: Manual review required!")
    print("   1. Check operation names are correct")
    print("   2. Verify all img_file references work")
    print("   3. Test each fixed function")
    print("   4. Some functions may need get_selected_entries_for_operation()")
    print()
    print("🔍 To review changes:")
    print(f"   diff -r {backup_dir} apps/core/")
    print(f"   diff {backup_dir}/img_import_system.py apps/methods/img_import_system.py")
    print()
    print("📝 Files that may need manual fixes:")
    print("   - Functions that need selected entries")
    print("   - Functions that work with COL files too")
    print("   - export_via.py (needs validate_any_file)")
    print()


if __name__ == '__main__':
    main()
