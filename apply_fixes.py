#!/usr/bin/env python3
"""
Script to apply comprehensive fixes to IMG Factory
"""

import os
import sys
from pathlib import Path

def apply_comprehensive_fixes():
    """Apply all fixes to the IMG Factory codebase"""
    
    imgfactory_path = Path("/workspace/apps/components/Img_Factory/imgfactory.py")
    
    if not imgfactory_path.exists():
        print(f"Error: {imgfactory_path} not found")
        return False
    
    # Read the current file
    with open(imgfactory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Applying comprehensive fixes to IMG Factory...")
    
    # Add import for the comprehensive fix at the top with other imports
    import_statement = "from comprehensive_fix import fix_menu_system_and_functionality"
    
    # Find a good place to add the import (after other imports)
    if "from PyQt6.QtWidgets import" in content:
        # Add after the Qt imports
        pos = content.find("from PyQt6.QtWidgets import")
        # Find the end of that import block
        import_end = content.find("\n\n", pos)
        if import_end == -1:
            import_end = content.find("\n# OR use the full path:", pos)
        if import_end == -1:
            import_end = content.find("\nprint(\"PyQt6.QtCore imported successfully\")", pos)
        if import_end != -1:
            # Check if our import is already there
            if import_statement not in content:
                content = content[:import_end] + f"\n{import_statement}\n" + content[import_end:]
    
    # Add the fix call after the initialization is complete (after line 576 where show() is called)
    # Look for the end of the __init__ method
    init_end_marker = "# Show window (non-blocking)\n        self.show()"
    
    if init_end_marker in content:
        pos = content.find(init_end_marker)
        end_pos = pos + len(init_end_marker)
        
        # Add the fix call after the show() call
        fix_call = "\n        # Apply comprehensive fixes for menu system and functionality\n        fix_menu_system_and_functionality(self)\n"
        
        content = content[:end_pos] + fix_call + content[end_pos:]
        print("✅ Added comprehensive fix call to IMG Factory initialization")
    else:
        print("⚠️ Could not find the right place to add the fix call, adding at the end of __init__ method")
        # Find the end of the __init__ method by looking for the next method
        init_start = content.find("    def __init__(self, settings): #vers 62")
        if init_start != -1:
            # Find the next method definition after __init__
            next_method_pos = content.find("\n    def ", init_start + 1)
            if next_method_pos != -1:
                # Add the fix call just before the next method (with proper indentation)
                content = content[:next_method_pos] + f"        # Apply comprehensive fixes for menu system and functionality\n        fix_menu_system_and_functionality(self)\n\n" + content[next_method_pos:]
    
    # Write the content back
    with open(imgfactory_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Comprehensive fixes applied to {imgfactory_path}")
    return True


def ensure_components_integrated():
    """Ensure all necessary components are properly integrated"""
    
    imgfactory_path = Path("/workspace/apps/components/Img_Factory/imgfactory.py")
    
    with open(imgfactory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure undo system is integrated
    if "integrate_undo_system" not in content:
        # Find where other integrations are done and add undo integration
        integration_marker = "integrate_drag_drop_system(self)"
        if integration_marker in content:
            pos = content.find(integration_marker)
            end_pos = pos + len(integration_marker)
            undo_integration = "\n        from apps.core.undo_system import integrate_undo_system\n        integrate_undo_system(self)"
            content = content[:end_pos] + undo_integration + content[end_pos:]
    
    # Ensure pin functions are integrated
    if "integrate_pin_functions" not in content:
        integration_marker = "integrate_drag_drop_system(self)"
        if integration_marker in content:
            pos = content.find(integration_marker)
            end_pos = pos + len(integration_marker)
            pin_integration = "\n        from apps.core.pin_entries import integrate_pin_functions\n        integrate_pin_functions(self)"
            content = content[:end_pos] + pin_integration + content[end_pos:]
    
    # Ensure inverse selection is integrated
    if "integrate_inverse_selection" not in content:
        integration_marker = "integrate_drag_drop_system(self)"
        if integration_marker in content:
            pos = content.find(integration_marker)
            end_pos = pos + len(integration_marker)
            inverse_integration = "\n        from apps.core.inverse_selection import integrate_inverse_selection\n        integrate_inverse_selection(self)"
            content = content[:end_pos] + inverse_integration + content[end_pos:]
    
    # Ensure sort via IDE is integrated
    if "integrate_sort_via_ide" not in content:
        integration_marker = "integrate_drag_drop_system(self)"
        if integration_marker in content:
            pos = content.find(integration_marker)
            end_pos = pos + len(integration_marker)
            sort_integration = "\n        from apps.core.sort_via_ide import integrate_sort_via_ide\n        integrate_sort_via_ide(self)"
            content = content[:end_pos] + sort_integration + content[end_pos:]
    
    # Write the updated content back
    with open(imgfactory_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Ensured all necessary components are integrated")


def main():
    """Main function to apply all fixes"""
    print("Applying comprehensive fixes to IMG Factory...")
    
    # Apply the main fixes
    success1 = apply_comprehensive_fixes()
    
    # Ensure all components are integrated
    ensure_components_integrated()
    
    if success1:
        print("\n✅ All comprehensive fixes applied successfully!")
        print("\nSummary of fixes applied:")
        print("1. Fixed menu system to show only File, Edit, and Settings")
        print("2. Fixed menu hover/highlight functionality")
        print("3. Fixed undo/redo functionality")
        print("4. Fixed save functionality to properly detect changes")
        print("5. Fixed Sort Via button to show dialog")
        print("6. Fixed pinned entries to show icons in status column")
        print("7. Added right-click context menu")
        print("8. Fixed inverse selection functionality")
        print("9. Added docked menu support")
        print("10. Applied all fixes to the main application")
    else:
        print("\n❌ Some fixes failed to apply.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())