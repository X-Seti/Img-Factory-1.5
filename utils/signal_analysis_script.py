#!/usr/bin/env python3
"""
#this belongs in root /signal_analysis_script.py - Version: 1
# X-Seti - JULY03 2025 - Signal Analysis Script for Img Factory 1.5
# Find and analyze all signal-related functions to identify conflicts
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict, Counter
import argparse

class SignalAnalyzer:
    """Analyze signal patterns in Python files"""
    
    def __init__(self):
        self.signal_connections = defaultdict(list)  # signal_name -> [(file, line_num, code)]
        self.signal_handlers = defaultdict(list)     # handler_name -> [(file, line_num, code)]
        self.signal_methods = defaultdict(list)      # method_name -> [(file, line_num, code)]
        self.button_connections = defaultdict(list)  # button -> [(file, line_num, code)]
        self.classes_with_signals = defaultdict(list) # class_name -> signal_methods
        self.files_analyzed = []
        self.conflicts_found = []

    def analyze_file(self, file_path):
        """Analyze a single Python file for signal patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.files_analyzed.append(str(file_path))
            current_class = None
            current_function = None
            
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip comments and empty lines
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Track current class
                class_match = re.search(r'^class\s+(\w+)', stripped)
                if class_match:
                    current_class = class_match.group(1)
                    continue
                
                # Track current function/method
                func_match = re.search(r'^(\s*)def\s+(\w+)\s*\(', line)
                if func_match:
                    indent, func_name = func_match.groups()
                    current_function = func_name
                    
                    # Check for signal-related method names
                    if self._is_signal_method(func_name):
                        method_info = {
                            'file': str(file_path),
                            'line': line_num,
                            'class': current_class,
                            'method': func_name,
                            'code': stripped,
                            'indent': len(indent)
                        }
                        self.signal_methods[func_name].append(method_info)
                        
                        if current_class:
                            self.classes_with_signals[current_class].append(func_name)
                    continue
                
                # Look for signal connections
                if '.connect(' in line:
                    self._analyze_signal_connection(file_path, line_num, line, current_class, current_function)
                
                # Look for button connections specifically
                if 'clicked.connect(' in line:
                    self._analyze_button_connection(file_path, line_num, line, current_class)
                
                # Look for table signal connections
                if any(signal in line for signal in ['itemSelectionChanged', 'itemDoubleClicked', 'selectionChanged']):
                    self._analyze_table_signal(file_path, line_num, line, current_class)
        
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")

    def _is_signal_method(self, method_name):
        """Check if method name indicates signal handling"""
        signal_patterns = [
            r'^_?connect_.*signals?$',
            r'^_?on_.*$',
            r'^_?.*_changed$',
            r'^_?.*_clicked$',
            r'^_?.*selection.*$',
            r'^_?handle_.*$',
            r'^_?.*_signal.*$'
        ]
        
        for pattern in signal_patterns:
            if re.match(pattern, method_name, re.IGNORECASE):
                return True
        return False

    def _analyze_signal_connection(self, file_path, line_num, line, current_class, current_function):
        """Analyze a signal connection line"""
        # Extract signal pattern
        connect_patterns = [
            r'(\w+)\.(\w+)\.connect\(([^)]+)\)',  # widget.signal.connect(handler)
            r'(\w+)\.connect\(([^)]+)\)',         # signal.connect(handler)
        ]
        
        for pattern in connect_patterns:
            match = re.search(pattern, line.strip())
            if match:
                if len(match.groups()) == 3:
                    widget, signal, handler = match.groups()
                    signal_name = f"{widget}.{signal}"
                else:
                    signal, handler = match.groups()
                    signal_name = signal
                
                connection_info = {
                    'file': str(file_path),
                    'line': line_num,
                    'class': current_class,
                    'function': current_function,
                    'signal': signal_name,
                    'handler': handler.strip(),
                    'code': line.strip()
                }
                
                self.signal_connections[signal_name].append(connection_info)
                break

    def _analyze_button_connection(self, file_path, line_num, line, current_class):
        """Analyze button click connections"""
        button_match = re.search(r'(\w+)\.clicked\.connect\(([^)]+)\)', line.strip())
        if button_match:
            button, handler = button_match.groups()
            
            connection_info = {
                'file': str(file_path),
                'line': line_num,
                'class': current_class,
                'button': button,
                'handler': handler.strip(),
                'code': line.strip()
            }
            
            self.button_connections[button].append(connection_info)

    def _analyze_table_signal(self, file_path, line_num, line, current_class):
        """Analyze table-specific signal connections"""
        table_signals = ['itemSelectionChanged', 'itemDoubleClicked', 'selectionChanged']
        
        for signal in table_signals:
            if signal in line and '.connect(' in line:
                signal_info = {
                    'file': str(file_path),
                    'line': line_num,
                    'class': current_class,
                    'signal_type': signal,
                    'code': line.strip()
                }
                
                self.signal_handlers[f"table_{signal}"].append(signal_info)

    def detect_conflicts(self):
        """Detect signal conflicts and duplicates"""
        conflicts = []
        
        # 1. Check for duplicate signal method names
        for method_name, occurrences in self.signal_methods.items():
            if len(occurrences) > 1:
                conflicts.append({
                    'type': 'Duplicate Signal Method',
                    'method': method_name,
                    'count': len(occurrences),
                    'locations': occurrences
                })
        
        # 2. Check for multiple connections to same signal
        for signal_name, connections in self.signal_connections.items():
            if len(connections) > 1:
                conflicts.append({
                    'type': 'Multiple Signal Connections',
                    'signal': signal_name,
                    'count': len(connections),
                    'locations': connections
                })
        
        # 3. Check for classes with multiple signal handling methods
        for class_name, methods in self.classes_with_signals.items():
            if len(methods) > 3:  # More than 3 signal methods might indicate problems
                conflicts.append({
                    'type': 'Class with Many Signal Methods',
                    'class': class_name,
                    'methods': methods,
                    'count': len(methods)
                })
        
        self.conflicts_found = conflicts
        return conflicts

    def print_analysis_report(self):
        """Print comprehensive analysis report"""
        print("🔍 SIGNAL ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n📁 Files analyzed: {len(self.files_analyzed)}")
        print(f"📊 Signal methods found: {len(self.signal_methods)}")
        print(f"🔗 Signal connections found: {len(self.signal_connections)}")
        print(f"🖱️  Button connections found: {len(self.button_connections)}")
        
        # Print signal methods by frequency
        print(f"\n📋 SIGNAL METHODS FOUND:")
        method_counts = Counter(method for method in self.signal_methods.keys())
        for method, count in method_counts.most_common():
            status = "⚠️  DUPLICATE" if count > 1 else "✅ UNIQUE"
            print(f"  {status} {method} ({count} occurrence{'s' if count > 1 else ''})")
            
            # Show locations for duplicates
            if count > 1:
                for occurrence in self.signal_methods[method]:
                    file_name = Path(occurrence['file']).name
                    class_info = f" in {occurrence['class']}" if occurrence['class'] else ""
                    print(f"    📄 {file_name}:{occurrence['line']}{class_info}")
        
        # Print signal connections
        print(f"\n🔗 SIGNAL CONNECTIONS:")
        for signal_name, connections in self.signal_connections.items():
            status = "⚠️  MULTIPLE" if len(connections) > 1 else "✅ SINGLE"
            print(f"  {status} {signal_name} ({len(connections)} connection{'s' if len(connections) > 1 else ''})")
            
            if len(connections) > 1:
                for conn in connections:
                    file_name = Path(conn['file']).name
                    class_info = f" in {conn['class']}" if conn['class'] else ""
                    print(f"    📄 {file_name}:{conn['line']}{class_info} -> {conn['handler']}")
        
        # Print conflicts summary
        conflicts = self.detect_conflicts()
        print(f"\n🚨 CONFLICTS DETECTED: {len(conflicts)}")
        
        for conflict in conflicts:
            print(f"\n⚠️  {conflict['type']}:")
            if conflict['type'] == 'Duplicate Signal Method':
                print(f"   Method: {conflict['method']} ({conflict['count']} times)")
                for location in conflict['locations']:
                    file_name = Path(location['file']).name
                    class_info = f" in {location['class']}" if location['class'] else ""
                    print(f"   📄 {file_name}:{location['line']}{class_info}")
            
            elif conflict['type'] == 'Multiple Signal Connections':
                print(f"   Signal: {conflict['signal']} ({conflict['count']} connections)")
                for location in conflict['locations']:
                    file_name = Path(location['file']).name
                    print(f"   📄 {file_name}:{location['line']} -> {location['handler']}")
            
            elif conflict['type'] == 'Class with Many Signal Methods':
                print(f"   Class: {conflict['class']} ({conflict['count']} signal methods)")
                print(f"   Methods: {', '.join(conflict['methods'])}")

    def get_files_to_clean(self):
        """Get list of files that need signal cleanup"""
        files_with_conflicts = set()
        
        # Files with duplicate signal methods
        for method_name, occurrences in self.signal_methods.items():
            if len(occurrences) > 1:
                for occurrence in occurrences:
                    files_with_conflicts.add(occurrence['file'])
        
        # Files with multiple signal connections
        for signal_name, connections in self.signal_connections.items():
            if len(connections) > 1:
                for connection in connections:
                    files_with_conflicts.add(connection['file'])
        
        return sorted(files_with_conflicts)

    def generate_cleanup_recommendations(self):
        """Generate specific cleanup recommendations"""
        print(f"\n💡 CLEANUP RECOMMENDATIONS:")
        print("=" * 60)
        
        files_to_clean = self.get_files_to_clean()
        
        print(f"📁 Files needing cleanup: {len(files_to_clean)}")
        for file_path in files_to_clean:
            file_name = Path(file_path).name
            print(f"  📄 {file_name}")
        
        # Specific recommendations based on analysis
        print(f"\n🔧 SPECIFIC ACTIONS NEEDED:")
        
        # Check for common problematic methods
        problematic_methods = ['_connect_signals', 'connect_signals', '_on_selection_changed', 'on_selection_changed']
        for method in problematic_methods:
            if method in self.signal_methods and len(self.signal_methods[method]) > 1:
                print(f"  ⚠️  Remove duplicate '{method}' methods")
                print(f"     Keep only the one in the unified signal handler")
        
        # Check for table signal duplicates
        table_signals = [key for key in self.signal_connections.keys() if 'selection' in key.lower() or 'click' in key.lower()]
        if len(table_signals) > 2:
            print(f"  ⚠️  Consolidate table signal connections")
            print(f"     Use unified signal handler instead of {len(table_signals)} separate connections")
        
        # Check for button signal consolidation
        if len(self.button_connections) > 10:
            print(f"  ⚠️  Consolidate button signal connections")
            print(f"     Found {len(self.button_connections)} button connections - consider grouping")
        
        print(f"\n✅ RECOMMENDED SOLUTION:")
        print(f"  1. Run signal cleanup script to comment out conflicting signals")
        print(f"  2. Use only the unified signal handler from components/unified_signal_handler.py")
        print(f"  3. Replace all manual signal connections with unified connect_table_signals()")
        print(f"  4. Test application to ensure signals work correctly")


def find_python_files(root_dir):
    """Find all Python files in the project"""
    python_files = []
    root_path = Path(root_dir)
    
    # Skip certain directories
    skip_dirs = {'__pycache__', '.git', 'venv', 'env', 'backup_*'}
    
    for file_path in root_path.rglob("*.py"):
        # Skip files in skip_dirs
        if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
            continue
        python_files.append(file_path)
    
    return python_files


def main():
    """Main analysis function"""
    parser = argparse.ArgumentParser(description="Analyze signal patterns in IMG Factory 1.5")
    parser.add_argument('--cleanup', action='store_true', help='Generate cleanup script')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
    args = parser.parse_args()
    
    print("🔍 IMG Factory 1.5 - Signal Pattern Analysis")
    print("=" * 60)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Working directory: {current_dir}")
    
    # Find all Python files
    python_files = find_python_files(current_dir)
    print(f"Found {len(python_files)} Python files to analyze")
    
    # Initialize analyzer
    analyzer = SignalAnalyzer()
    
    # Analyze all files
    print(f"\n🔍 Analyzing files...")
    for file_path in python_files:
        print(f"  📄 {file_path.name}")
        analyzer.analyze_file(file_path)
    
    # Generate report
    analyzer.print_analysis_report()
    
    # Generate recommendations
    analyzer.generate_cleanup_recommendations()
    
    # Offer to generate cleanup script
    if args.cleanup or input(f"\n❓ Generate cleanup script? (y/N): ").lower() == 'y':
        generate_cleanup_script(analyzer)


def generate_cleanup_script(analyzer):
    """Generate a cleanup script based on analysis"""
    cleanup_script = '''#!/usr/bin/env python3
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
'''
    
    # Add specific patterns based on conflicts found
    for method_name, occurrences in analyzer.signal_methods.items():
        if len(occurrences) > 1:
            cleanup_script += f'            r"(\\s*)(.*{method_name}.*\\.connect.*)",\n'
    
    cleanup_script += '''        ]
        
        # Comment out conflicting patterns
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            for pattern in patterns_to_comment:
                if re.search(pattern, line) and not line.strip().startswith('#'):
                    lines[i] = re.sub(r'^(\\s*)', r'\\1# SIGNAL_CLEANUP: ', line)
                    changes_made = True
        
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\\n'.join(lines))
            print(f"✓ Cleaned: {file_path}")
            return True
        
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
    
    return False

def main():
    """Main cleanup function"""
    files_to_clean = [
'''
    
    # Add files that need cleaning
    files_to_clean = analyzer.get_files_to_clean()
    for file_path in files_to_clean:
        cleanup_script += f'        "{file_path}",\n'
    
    cleanup_script += '''    ]
    
    print(f"🧹 Cleaning {len(files_to_clean)} files...")
    
    for file_path in files_to_clean:
        backup_file(file_path)
        clean_signals_in_file(file_path)
    
    print("✅ Cleanup complete!")
    print("Next: Use unified signal handler for all connections")

if __name__ == "__main__":
    main()
'''
    
    # Write cleanup script
    cleanup_path = Path("generated_signal_cleanup.py")
    with open(cleanup_path, 'w', encoding='utf-8') as f:
        f.write(cleanup_script)
    
    print(f"\n✅ Generated cleanup script: {cleanup_path}")
    print(f"Run with: python {cleanup_path}")


if __name__ == "__main__":
    main()