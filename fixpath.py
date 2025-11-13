#!/usr/bin/env python3
"""
X-Seti - November13 2025 - IMG Factory 1.5 - Import Path Correction Tool
#this belongs in root /fix_imports.py - Version: 1
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix import paths in a single file""" #vers 1
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes = []

        # Patterns to fix - imports that should have apps. prefix
        patterns = [
            (r'^from methods\.', 'from apps.methods.'),
            (r'^from core\.', 'from apps.core.'),
            (r'^from gui\.', 'from apps.gui.'),
            (r'^from utils\.', 'from apps.utils.'),
            (r'^from components\.', 'from apps.components.'),
            (r'^from debug\.', 'from apps.debug.'),
        ]

        for pattern, replacement in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                changes.append(f"  Fixed: {pattern} -> {replacement}")

        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes

        return None

    except Exception as e:
        print(f"ERROR reading {filepath}: {e}")
        return None

def scan_and_fix_all():
    """Scan all Python files and fix imports""" #vers 1
    root = Path(__file__).parent / 'apps'

    if not root.exists():
        print(f"ERROR: {root} does not exist!")
        return

    print("=" * 60)
    print("IMG Factory 1.5 - Import Path Correction Tool")
    print("=" * 60)
    print(f"Scanning: {root}\n")

    total_files = 0
    fixed_files = 0

    for py_file in root.rglob('*.py'):
        total_files += 1
        changes = fix_imports_in_file(py_file)

        if changes:
            fixed_files += 1
            print(f"✓ FIXED: {py_file.relative_to(root.parent)}")
            for change in changes:
                print(change)
            print()

    print("=" * 60)
    print(f"Scanned: {total_files} files")
    print(f"Fixed: {fixed_files} files")
    print("=" * 60)

if __name__ == "__main__":
    scan_and_fix_all()
