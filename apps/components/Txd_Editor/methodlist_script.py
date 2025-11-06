#!/usr/bin/env python3
"""
methodlist.py - Extract all class and method headers from Python files
X-Seti - October10 2025

Usage:
    python3 methodlist.py > list.txt
    python3 methodlist.py components/Txd_Editor/txd_workshop.py > txd_methods.txt
    python3 methodlist.py --dir components/ > all_components.txt
"""

import os
import sys
import re
from pathlib import Path


def extract_classes_and_methods(file_path):
    """
    Extract all class definitions and method signatures from a Python file
    
    Returns:
        dict: {
            'file': str,
            'classes': [
                {
                    'name': str,
                    'line': int,
                    'version': str,
                    'methods': [
                        {'name': str, 'line': int, 'version': str, 'signature': str}
                    ]
                }
            ],
            'functions': [  # Module-level functions
                {'name': str, 'line': int, 'version': str, 'signature': str}
            ]
        }
    """
    result = {
        'file': str(file_path),
        'classes': [],
        'functions': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return result
    
    current_class = None
    
    for line_num, line in enumerate(lines, 1):
        # Match class definitions
        class_match = re.match(r'^class\s+(\w+).*?:\s*(?:#vers\s*(\d+))?', line)
        if class_match:
            class_name = class_match.group(1)
            version = class_match.group(2) or '?'
            current_class = {
                'name': class_name,
                'line': line_num,
                'version': version,
                'signature': line.strip(),
                'methods': []
            }
            result['classes'].append(current_class)
            continue
        
        # Match method/function definitions
        func_match = re.match(r'^(\s*)def\s+(\w+)\s*\((.*?)\).*?:\s*(?:#vers\s*(\d+))?', line)
        if func_match:
            indent = func_match.group(1)
            func_name = func_match.group(2)
            params = func_match.group(3)
            version = func_match.group(4) or '?'
            
            func_info = {
                'name': func_name,
                'line': line_num,
                'version': version,
                'signature': line.strip(),
                'params': params
            }
            
            # Determine if it's a method (indented) or module function
            if indent and current_class:
                current_class['methods'].append(func_info)
            elif not indent:
                result['functions'].append(func_info)
    
    return result


def format_output(data, show_line_numbers=True, show_versions=True):
    """Format extracted data as readable text"""
    output = []
    
    file_name = os.path.basename(data['file'])
    output.append("=" * 80)
    output.append(f"FILE: {file_name}")
    output.append(f"PATH: {data['file']}")
    output.append("=" * 80)
    output.append("")
    
    # Module-level functions
    if data['functions']:
        output.append("## MODULE-LEVEL FUNCTIONS")
        output.append("-" * 80)
        for func in sorted(data['functions'], key=lambda x: x['name']):
            line_info = f" (line {func['line']})" if show_line_numbers else ""
            vers_info = f" #vers {func['version']}" if show_versions else ""
            output.append(f"def {func['name']}({func['params']}){vers_info}{line_info}")
        output.append("")
    
    # Classes and their methods
    if data['classes']:
        output.append("## CLASSES")
        output.append("-" * 80)
        
        for cls in sorted(data['classes'], key=lambda x: x['name']):
            line_info = f" (line {cls['line']})" if show_line_numbers else ""
            vers_info = f" #vers {cls['version']}" if show_versions else ""
            
            output.append(f"\nclass {cls['name']}{vers_info}{line_info}")
            
            if cls['methods']:
                output.append("  Methods:")
                for method in sorted(cls['methods'], key=lambda x: x['name']):
                    method_line = f" (line {method['line']})" if show_line_numbers else ""
                    method_vers = f" #vers {method['version']}" if show_versions else ""
                    output.append(f"    • {method['name']}({method['params']}){method_vers}{method_line}")
            else:
                output.append("  (no methods)")
        output.append("")
    
    # Summary
    total_classes = len(data['classes'])
    total_methods = sum(len(cls['methods']) for cls in data['classes'])
    total_functions = len(data['functions'])
    
    output.append("=" * 80)
    output.append("SUMMARY")
    output.append("-" * 80)
    output.append(f"Classes:          {total_classes}")
    output.append(f"Methods:          {total_methods}")
    output.append(f"Module Functions: {total_functions}")
    output.append(f"Total:            {total_classes + total_methods + total_functions}")
    output.append("=" * 80)
    
    return "\n".join(output)


def scan_directory(directory, pattern="*.py", recursive=True):
    """Scan directory for Python files"""
    path = Path(directory)
    
    if recursive:
        files = list(path.rglob(pattern))
    else:
        files = list(path.glob(pattern))
    
    return sorted(files)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract class and method headers from Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file
  python3 methodlist.py txd_workshop.py > methods.txt
  
  # Directory (recursive)
  python3 methodlist.py --dir components/ > all_methods.txt
  
  # Current directory
  python3 methodlist.py --dir . > project_methods.txt
  
  # Without line numbers
  python3 methodlist.py --no-lines txd_workshop.py
  
  # Without version tags
  python3 methodlist.py --no-versions txd_workshop.py
        """
    )
    
    parser.add_argument('file', nargs='?', help='Python file to analyze')
    parser.add_argument('--dir', '-d', help='Directory to scan (recursive)')
    parser.add_argument('--pattern', '-p', default='*.py', help='File pattern (default: *.py)')
    parser.add_argument('--no-lines', action='store_true', help='Hide line numbers')
    parser.add_argument('--no-versions', action='store_true', help='Hide version tags')
    parser.add_argument('--no-recursive', action='store_true', help='Disable recursive scan')
    
    args = parser.parse_args()
    
    show_lines = not args.no_lines
    show_versions = not args.no_versions
    
    files_to_process = []
    
    if args.dir:
        # Scan directory
        files_to_process = scan_directory(
            args.dir, 
            args.pattern, 
            recursive=not args.no_recursive
        )
        if not files_to_process:
            print(f"No Python files found in {args.dir}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        # Single file
        files_to_process = [Path(args.file)]
    else:
        # Default: current directory
        files_to_process = scan_directory('.', args.pattern)
        if not files_to_process:
            print("No Python files found in current directory", file=sys.stderr)
            sys.exit(1)
    
    # Process all files
    all_results = []
    for file_path in files_to_process:
        if not file_path.exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            continue
        
        data = extract_classes_and_methods(file_path)
        all_results.append(data)
    
    # Output results
    for i, data in enumerate(all_results):
        if i > 0:
            print("\n\n")  # Separator between files
        print(format_output(data, show_lines, show_versions))
    
    # Grand total if multiple files
    if len(all_results) > 1:
        total_classes = sum(len(d['classes']) for d in all_results)
        total_methods = sum(sum(len(c['methods']) for c in d['classes']) for d in all_results)
        total_functions = sum(len(d['functions']) for d in all_results)
        
        print("\n")
        print("=" * 80)
        print("GRAND TOTAL")
        print("-" * 80)
        print(f"Files:            {len(all_results)}")
        print(f"Classes:          {total_classes}")
        print(f"Methods:          {total_methods}")
        print(f"Module Functions: {total_functions}")
        print(f"Total:            {total_classes + total_methods + total_functions}")
        print("=" * 80)


if __name__ == '__main__':
    main()
