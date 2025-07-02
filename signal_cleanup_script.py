#!/usr/bin/env python3
"""
Signal Cleanup Script for IMG Factory 1.5
Finds and comments out all signal connections to eliminate conflicts
Also detects potential signal conflicts
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

class SignalTracker:
    """Track signal connections to detect conflicts"""
    def __init__(self):
        self.signal_connections = defaultdict(list)  # signal_name -> [(file, line_num, code)]
        self.signal_handlers = defaultdict(list)     # handler_name -> [(file, line_num, code)]
        self.removed_signals = []                    # List of removed signals
        self.classes = defaultdict(list)             # class_name -> [(file, line_num, code)]
        self.functions = defaultdict(list)           # function_name -> [(file, line_num, code)]
        self.methods = defaultdict(list)             # method_name -> [(file, line_num, code)]

def backup_file(file_path):
    """Create backup of file before modifying"""
    backup_path = str(file_path) + ".backup"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backed up: {file_path} -> {backup_path}")

def analyze_signals_in_file(file_path, tracker):
    """Analyze signals in a file before modifying"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_class = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            # Track classes
            class_match = re.search(r'^class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                current_class = class_name
                tracker.classes[class_name].append((str(file_path), line_num, stripped))
            
            # Track functions and methods
            func_match = re.search(r'^(\s*)def\s+(\w+)\s*\(', line)
            if func_match:
                indent, func_name = func_match.groups()
                full_line = stripped
                
                if indent.strip() == '':  # Top-level function
                    tracker.functions[func_name].append((str(file_path), line_num, full_line))
                else:  # Method inside class
                    method_key = f"{current_class}.{func_name}" if current_class else func_name
                    tracker.methods[func_name].append((str(file_path), line_num, full_line, current_class or "Unknown"))
                
            # Look for signal connections
            if '.connect(' in line:
                # Extract signal and handler
                connect_match = re.search(r'(\w+)\.(\w+)\.connect\(([^)]+)\)', line)
                if connect_match:
                    widget, signal, handler = connect_match.groups()
                    signal_name = f"{widget}.{signal}"
                    tracker.signal_connections[signal_name].append((str(file_path), line_num, line.strip()))
                    tracker.signal_handlers[handler].append((str(file_path), line_num, line.strip()))
            
            # Look for signal handler definitions
            handler_match = re.search(r'def (_?on_\w+|_?\w*selection\w*|_?\w*clicked\w*)\(', line)
            if handler_match:
                handler_name = handler_match.group(1)
                tracker.signal_handlers[handler_name].append((str(file_path), line_num, f"def {handler_name}(...)"))
                
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")

def comment_out_signals(file_path, tracker):
    """Comment out signal-related lines in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changes_made = False
        removed_count = 0
        
        # Patterns to find and comment out
        patterns = [
            # Signal connection patterns
            (r'(\s*)(.*\.connect\(.*\))', 'Signal Connection'),
            (r'(\s*)(.*\.itemSelectionChanged\.connect.*)', 'Selection Signal'),
            (r'(\s*)(.*\.itemDoubleClicked\.connect.*)', 'Double-Click Signal'),
            (r'(\s*)(.*\.clicked\.connect.*)', 'Button Click Signal'),
            (r'(\s*)(.*\.timeout\.connect.*)', 'Timer Signal'),
            (r'(\s*)(.*\.triggered\.connect.*)', 'Menu Action Signal'),
            (r'(\s*)(.*\.toggled\.connect.*)', 'Toggle Signal'),
            (r'(\s*)(.*\.valueChanged\.connect.*)', 'Value Changed Signal'),
            (r'(\s*)(.*\.currentTextChanged\.connect.*)', 'Text Changed Signal'),
            (r'(\s*)(.*\.textChanged\.connect.*)', 'Text Changed Signal'),
            
            # Method calls that connect signals
            (r'(\s*)(.*connect_table_signals\(\))', 'Table Signal Method Call'),
            (r'(\s*)(.*connect_signals\(\))', 'Signal Method Call'),
            (r'(\s*)(.*connect_button_signals\(\))', 'Button Signal Method Call'),
        ]
        
        # Function definitions to comment out
        function_patterns = [
            (r'(\s*)(def connect_signals\(self.*?\):)', 'Signal Connect Method'),
            (r'(\s*)(def connect_table_signals\(self.*?\):)', 'Table Signal Connect Method'),
            (r'(\s*)(def connect_button_signals\(self.*?\):)', 'Button Signal Connect Method'),
            (r'(\s*)(def _connect_signals\(self.*?\):)', 'Private Signal Connect Method'),
        ]
        
        lines = content.split('\n')
        modified_lines = []
        in_signal_function = False
        function_indent = 0
        current_function_name = ""
        
        for i, line in enumerate(lines, 1):
            original_line = line
            
            # Check if we're entering a signal function
            for pattern, description in function_patterns:
                match = re.match(pattern, line)
                if match:
                    indent = len(match.group(1))
                    if not line.strip().startswith('#'):
                        line = match.group(1) + "# " + match.group(2)
                        in_signal_function = True
                        function_indent = indent
                        current_function_name = match.group(2)
                        changes_made = True
                        removed_count += 1
                        tracker.removed_signals.append({
                            'file': str(file_path),
                            'line': i,
                            'type': description,
                            'code': match.group(2)
                        })
                        print(f"  📝 {description}: {match.group(2)}")
                    break
            
            # If we're in a signal function, comment out the entire function
            if in_signal_function:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent > function_indent:
                    if not line.strip().startswith('#'):
                        line = line[:current_indent] + "# " + line[current_indent:]
                        changes_made = True
                        if '.connect(' in original_line:
                            removed_count += 1
                            tracker.removed_signals.append({
                                'file': str(file_path),
                                'line': i,
                                'type': 'Function Body Signal',
                                'code': original_line.strip()
                            })
                elif line.strip() and current_indent <= function_indent:
                    in_signal_function = False
            
            # Comment out signal connection lines (if not already in a commented function)
            if not in_signal_function:
                for pattern, description in patterns:
                    match = re.match(pattern, line)
                    if match and not line.strip().startswith('#'):
                        line = match.group(1) + "# " + match.group(2)
                        changes_made = True
                        removed_count += 1
                        tracker.removed_signals.append({
                            'file': str(file_path),
                            'line': i,
                            'type': description,
                            'code': match.group(2).strip()
                        })
                        print(f"  🔌 {description}: {match.group(2).strip()}")
                        break
            
            modified_lines.append(line)
        
        if changes_made:
            # Write the modified content back
            modified_content = '\n'.join(modified_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"✅ Modified: {file_path} ({removed_count} signals removed)")
            return True
        else:
            print(f"➖ No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def detect_conflicts(tracker):
    """Detect potential signal conflicts"""
    print("\n🔍 CONFLICT ANALYSIS")
    print("=" * 50)
    
    conflicts_found = False
    
    # Check for duplicate classes
    print("\n🏗️  DUPLICATE CLASSES:")
    for class_name, definitions in tracker.classes.items():
        if len(definitions) > 1:
            conflicts_found = True
            print(f"\n⚠️  CONFLICT: Class '{class_name}' defined {len(definitions)} times:")
            for file_path, line_num, code in definitions:
                print(f"   📄 {Path(file_path).name}:{line_num} -> {code}")
    
    # Check for duplicate functions (top-level)
    print("\n🔧 DUPLICATE FUNCTIONS:")
    for func_name, definitions in tracker.functions.items():
        if len(definitions) > 1:
            conflicts_found = True
            print(f"\n⚠️  CONFLICT: Function '{func_name}' defined {len(definitions)} times:")
            for file_path, line_num, code in definitions:
                print(f"   📄 {Path(file_path).name}:{line_num} -> {code}")
    
    # Check for duplicate methods (grouped by method name across classes)
    print("\n⚙️  DUPLICATE METHODS:")
    method_conflicts = defaultdict(list)
    for method_name, definitions in tracker.methods.items():
        if len(definitions) > 1:
            # Group by actual method name, not class.method
            for file_path, line_num, code, class_name in definitions:
                method_conflicts[method_name].append((file_path, line_num, code, class_name))
    
    for method_name, definitions in method_conflicts.items():
        if len(definitions) > 1:
            # Check if they're in different classes (which might be OK) or same class (definitely bad)
            classes = set(d[3] for d in definitions)
            if len(classes) == 1:
                conflicts_found = True
                print(f"\n⚠️  CONFLICT: Method '{method_name}' defined {len(definitions)} times in class '{classes.pop()}':")
            else:
                print(f"\n ℹ️  Method '{method_name}' exists in {len(classes)} different classes:")
            
            for file_path, line_num, code, class_name in definitions:
                print(f"   📄 {Path(file_path).name}:{line_num} -> {class_name}.{code}")
    
    # Check for multiple connections to the same signal
    print("\n📡 SIGNAL CONNECTION CONFLICTS:")
    for signal_name, connections in tracker.signal_connections.items():
        if len(connections) > 1:
            conflicts_found = True
            print(f"\n⚠️  CONFLICT: {signal_name} connected {len(connections)} times:")
            for file_path, line_num, code in connections:
                print(f"   📄 {Path(file_path).name}:{line_num} -> {code}")
    
    # Check for duplicate handler names
    print("\n🎯 SIGNAL HANDLER CONFLICTS:")
    for handler_name, handlers in tracker.signal_handlers.items():
        if len(handlers) > 1:
            conflicts_found = True
            print(f"\n⚠️  CONFLICT: Handler '{handler_name}' defined {len(handlers)} times:")
            for file_path, line_num, code in handlers:
                print(f"   📄 {Path(file_path).name}:{line_num} -> {code}")
    
    # Look for common conflict patterns
    print("\n🚨 COMMON CONFLICT PATTERNS:")
    
    # Selection signal conflicts
    selection_signals = [s for s in tracker.signal_connections.keys() if 'selection' in s.lower()]
    if len(selection_signals) > 1:
        conflicts_found = True
        print(f"⚠️  Multiple selection signals found: {selection_signals}")
    
    # Click signal conflicts
    click_signals = [s for s in tracker.signal_connections.keys() if 'click' in s.lower()]
    if len(click_signals) > 3:  # More than 3 might indicate duplicates
        conflicts_found = True
        print(f"⚠️  Many click signals found ({len(click_signals)}): {click_signals[:5]}...")
    
    # Common duplicate method names that cause issues
    problematic_methods = ['_connect_signals', 'on_selection_changed', '_on_selection_changed', 
                          'connect_table_signals', 'connect_signals']
    for method in problematic_methods:
        if method in tracker.methods and len(tracker.methods[method]) > 1:
            conflicts_found = True
            print(f"⚠️  Problematic method '{method}' found in multiple places")
    
    if not conflicts_found:
        print("✅ No obvious conflicts detected")
    
    return conflicts_found

def print_removal_summary(tracker):
    """Print summary of removed signals"""
    print("\n📋 REMOVED SIGNALS SUMMARY")
    print("=" * 50)
    
    if not tracker.removed_signals:
        print("❌ No signals were removed")
        return
    
    # Group by type
    by_type = defaultdict(list)
    for removal in tracker.removed_signals:
        by_type[removal['type']].append(removal)
    
    total_removed = len(tracker.removed_signals)
    print(f"🗑️  Total signals removed: {total_removed}")
    
    for signal_type, removals in by_type.items():
        print(f"\n📝 {signal_type} ({len(removals)} removed):")
        for removal in removals:
            file_name = Path(removal['file']).name
            print(f"   🔹 {file_name}:{removal['line']} -> {removal['code']}")
    
    # Show files affected
    affected_files = set(removal['file'] for removal in tracker.removed_signals)
    print(f"\n📁 Files affected: {len(affected_files)}")
    for file_path in sorted(affected_files):
        file_removals = [r for r in tracker.removed_signals if r['file'] == file_path]
        print(f"   📄 {Path(file_path).name} ({len(file_removals)} signals removed)")

def find_python_files(root_dir):
    """Find all Python files in the project"""
    python_files = []
    root_path = Path(root_dir)
    
    for file_path in root_path.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" not in str(file_path):
            python_files.append(file_path)
    
    return python_files

def main():
    """Main cleanup function"""
    print("🧹 IMG Factory 1.5 - Signal Cleanup Script")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Working directory: {current_dir}")
    
    # Find all Python files
    python_files = find_python_files(current_dir)
    print(f"Found {len(python_files)} Python files")
    
    # Initialize signal tracker
    tracker = SignalTracker()
    
    # First pass: analyze all signals to detect conflicts
    print(f"\n🔍 Analyzing signals in {len(python_files)} files...")
    for file_path in python_files:
        analyze_signals_in_file(file_path, tracker)
    
    # Show conflict analysis
    conflicts_detected = detect_conflicts(tracker)
    
    # Show what will be modified
    print(f"\n📋 PREVIEW: Files that will be modified")
    print("=" * 50)
    
    # Ask for confirmation
    if conflicts_detected:
        print("\n⚠️  CONFLICTS DETECTED! Cleaning up signals is recommended.")
    
    response = input(f"\nDo you want to backup and modify these {len(python_files)} files? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\n📁 Processing files...")
    
    modified_count = 0
    
    for file_path in python_files:
        print(f"\n📄 Processing: {Path(file_path).name}")
        
        # Create backup first
        backup_file(file_path)
        
        # Comment out signals
        if comment_out_signals(file_path, tracker):
            modified_count += 1
    
    # Print detailed summary
    print_removal_summary(tracker)
    
    print(f"\n✅ COMPLETE! Modified {modified_count} files")
    print(f"📊 Total signals removed: {len(tracker.removed_signals)}")
    print("\n📋 Next steps:")
    print("1. Test the application - it should start without crashes")
    print("2. Selection won't work yet (that's expected)")
    print("3. Add back ONE clean signal connection manually")
    print("4. If something breaks, restore from .backup files")
    
    # Show restore command
    print(f"\n🔄 To restore all files from backup:")
    print("find . -name '*.py.backup' -exec sh -c 'mv \"$1\" \"${1%.backup}\"' _ {} \\;")

if __name__ == "__main__":
    main()
