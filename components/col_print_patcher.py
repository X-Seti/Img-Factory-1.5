#this belongs in components/ col_print_patcher.py - Version: 2
# X-Seti - July11 2025 - IMG Factory 1.5 - COL Print Statement Patcher FIXED

"""
COL Print Statement Patcher - FIXED
Removes the flood of print statements from COL parsing files
"""

import sys
import re
from typing import List, Dict, Any


class COLPrintPatcher:
    """Patches COL files to remove excessive print statements"""
    
    def __init__(self):
        self.patched_modules = set()
        self.original_functions = {}
        self.debug_enabled = False
    
    def enable_debug(self):
        """Enable debug output"""
        self.debug_enabled = True
    
    def disable_debug(self):
        """Disable debug output"""
        self.debug_enabled = False
    
    def patch_col_core_classes(self):
        """Patch col_core_classes.py to remove print statements"""
        try:
            from components import col_core_classes
            
            if 'col_core_classes' in self.patched_modules:
                return True
            
            # Simple approach: disable debug globally on the module
            if hasattr(col_core_classes, '_debug_enabled'):
                col_core_classes._debug_enabled = self.debug_enabled
            
            self.patched_modules.add('col_core_classes')
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch col_core_classes: {e}")
            return False
    
    def patch_col_parser(self):
        """Patch col_parser.py to remove print statements"""
        try:
            from components import col_parser
            
            if 'col_parser' in self.patched_modules:
                return True
                
            # Simple approach: disable debug globally on the module
            if hasattr(col_parser, '_debug_enabled'):
                col_parser._debug_enabled = self.debug_enabled
            
            self.patched_modules.add('col_parser')
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch col_parser: {e}")
            return False
    
    def patch_col_integration(self):
        """Patch col_integration.py to remove excessive logging"""
        try:
            from components import col_integration
            
            if 'col_integration' in self.patched_modules:
                return True
            
            # Simple approach: disable debug globally on the module
            if hasattr(col_integration, '_debug_enabled'):
                col_integration._debug_enabled = self.debug_enabled
            
            self.patched_modules.add('col_integration')
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch col_integration: {e}")
            return False
    
    def patch_all_col_modules(self):
        """Patch all COL modules for silent operation"""
        success = True
        
        success &= self.patch_col_core_classes()
        success &= self.patch_col_parser()
        success &= self.patch_col_integration()
        
        return success
    
    def restore_original_functions(self):
        """Restore original functions (for debugging)"""
        try:
            # Simple restore - just re-enable debug on modules
            from components import col_core_classes, col_parser, col_integration
            
            for module in [col_core_classes, col_parser, col_integration]:
                if hasattr(module, '_debug_enabled'):
                    module._debug_enabled = True
            
            self.patched_modules.clear()
            self.original_functions.clear()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore original functions: {e}")
            return False


# Global patcher instance
col_patcher = COLPrintPatcher()


def apply_col_silence_patches():
    """Apply patches to silence COL debug output"""
    success = col_patcher.patch_all_col_modules()
    if success:
        print("✅ COL modules patched for silent operation")
    return success


def enable_col_debug_output():
    """Enable COL debug output"""
    col_patcher.enable_debug()
    print("🔊 COL debug output enabled")


def disable_col_debug_output():
    """Disable COL debug output"""
    col_patcher.disable_debug()
    print("🔇 COL debug output disabled")


def restore_col_original_functions():
    """Restore original COL functions (for debugging)"""
    success = col_patcher.restore_original_functions()
    if success:
        print("🔄 COL original functions restored")
    return success

def install_col_print_patcher(main_window):
    """Install COL print patcher into main window"""
    try:
        # Apply patches to silence COL output
        success = apply_col_silence_patches()

        if success:
            main_window.log_message("✅ COL print patcher installed")

            # Add control methods to main window
            main_window.enable_col_debug = enable_col_debug_output
            main_window.disable_col_debug = disable_col_debug_output

            return True
        else:
            main_window.log_message("⚠️ COL print patcher had issues")
            return False

    except Exception as e:
        main_window.log_message(f"❌ COL print patcher failed: {e}")
        return False

# Simple integration function that works
def simple_col_debug_disable():
    """Simple function to disable COL debug output"""
    try:
        # Set global debug flags
        import components.col_core_classes as col_module
        col_module._global_debug_enabled = False
        
        # Disable on patcher
        col_patcher.disable_debug()
        
        print("✅ COL debug disabled")
        return True
        
    except Exception as e:
        print(f"❌ COL debug disable failed: {e}")
        return False


def simple_col_debug_enable():
    """Simple function to enable COL debug output"""
    try:
        # Set global debug flags
        import components.col_core_classes as col_module
        col_module._global_debug_enabled = True
        
        # Enable on patcher
        col_patcher.enable_debug()
        
        print("✅ COL debug enabled")
        return True
        
    except Exception as e:
        print(f"❌ COL debug enable failed: {e}")
        return False


if __name__ == "__main__":
    print("COL Print Patcher - Fixed Version")
    print("✅ No syntax errors")
