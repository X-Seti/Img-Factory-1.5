#this belongs in components/ col_debug_control.py - Version: 1
# X-Seti - July10 2025 - IMG Factory 1.5 - COL Debug Control

"""
COL Debug Control System
Provides simple control over COL debug output to improve performance
"""

import os
from typing import Dict, List, Optional, Any


class COLDebugController:
    """Controls COL debug output to improve performance"""
    
    def __init__(self):
        self.debug_enabled = False
        self.debug_categories = set()
        self.performance_mode = True  # Default to performance mode (debug off)
        
    def enable_debug(self, categories: Optional[List[str]] = None):
        """Enable COL debug output for specific categories"""
        self.debug_enabled = True
        self.performance_mode = False
        
        if categories:
            self.debug_categories.update(categories)
        else:
            # Enable all COL categories
            self.debug_categories.update([
                'COL_LOADING',
                'COL_PARSING', 
                'COL_THREADING',
                'COL_DISPLAY',
                'COL_INTEGRATION'
            ])
    
    def disable_debug(self):
        """Disable all COL debug output for performance"""
        self.debug_enabled = False
        self.performance_mode = True
        self.debug_categories.clear()
    
    def is_debug_enabled(self, category: str = None) -> bool:
        """Check if debug is enabled for a category"""
        if not self.debug_enabled or self.performance_mode:
            return False
        
        if category:
            return category in self.debug_categories
        
        return True
    
    def debug_log(self, main_window, message: str, category: str = 'COL_GENERAL', level: str = 'INFO'):
        """Log debug message only if debug is enabled"""
        if not self.is_debug_enabled(category):
            return  # Skip logging for performance
        
        # Only log if debug is specifically enabled
        try:
            prefix = f"[{category}] " if category else ""
            main_window.log_message(f"{prefix}{message}")
        except:
            # Fallback to print if main_window logging fails
            print(f"COL Debug [{category}]: {message}")


# Global debug controller instance
col_debug_controller = COLDebugController()


def disable_col_debug_for_performance():
    """Disable COL debug output to improve loading performance"""
    global col_debug_controller
    col_debug_controller.disable_debug()
    print("✅ COL debug output disabled for better performance")


def enable_col_debug_selective(categories: List[str] = None):
    """Enable COL debug for specific categories only"""
    global col_debug_controller
    col_debug_controller.enable_debug(categories)
    print(f"✅ COL debug enabled for categories: {categories or 'all'}")


def is_col_debug_enabled(category: str = None) -> bool:
    """Check if COL debug is enabled"""
    global col_debug_controller
    return col_debug_controller.is_debug_enabled(category)


def col_debug_log(main_window, message: str, category: str = 'COL_GENERAL', level: str = 'INFO'):
    """Log COL debug message (performance controlled)"""
    global col_debug_controller
    col_debug_controller.debug_log(main_window, message, category, level)


def patch_col_classes_for_performance():
    """Patch COL classes to disable debug output"""
    try:
        # Import and patch col_core_classes
        from components import col_core_classes
        
        # Replace print statements with conditional logging
        original_print = print
        
        def performance_print(*args, **kwargs):
            # Only print if debug is enabled
            if col_debug_controller.is_debug_enabled('COL_PARSING'):
                original_print(*args, **kwargs)
        
        # Patch the col_core_classes module
        if hasattr(col_core_classes, 'print'):
            col_core_classes.print = performance_print
        
        print("✅ COL classes patched for performance")
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch COL classes: {e}")
        return False


def patch_col_parser_for_performance():
    """Patch COL parser to disable verbose output"""
    try:
        from components import col_parser
        
        # Disable debug in COL parser
        if hasattr(col_parser, 'COLParser'):
            original_init = col_parser.COLParser.__init__
            
            def performance_init(self, debug=False):
                # Force debug=False for performance
                original_init(self, debug=False)
            
            col_parser.COLParser.__init__ = performance_init
        
        print("✅ COL parser patched for performance")
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch COL parser: {e}")
        return False


def setup_col_performance_mode(main_window):
    """Setup COL performance mode - disable debug by default"""
    try:
        # Disable debug output
        disable_col_debug_for_performance()
        
        # Patch COL classes
        patch_col_classes_for_performance()
        patch_col_parser_for_performance()
        
        # Add setting to enable debug if needed
        if hasattr(main_window, 'app_settings'):
            # Check if user specifically wants COL debug
            col_debug_enabled = main_window.app_settings.get_setting('col_debug_enabled', False)
            
            if col_debug_enabled:
                enable_col_debug_selective(['COL_LOADING'])  # Only essential category
                main_window.log_message("✅ COL debug enabled (limited)")
            else:
                main_window.log_message("✅ COL performance mode enabled (debug disabled)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL performance setup error: {e}")
        else:
            print(f"❌ COL performance setup error: {e}")
        return False


def create_col_debug_toggle_action(main_window):
    """Create menu action to toggle COL debug"""
    try:
        from PyQt6.QtGui import QAction
        from PyQt6.QtCore import Qt
        
        def toggle_col_debug():
            if col_debug_controller.debug_enabled:
                disable_col_debug_for_performance()
                main_window.log_message("🔇 COL debug disabled for performance")
            else:
                enable_col_debug_selective(['COL_LOADING', 'COL_PARSING'])
                main_window.log_message("🔊 COL debug enabled")
        
        # Create action if main window has menu
        if hasattr(main_window, 'menuBar'):
            action = QAction("Toggle COL Debug", main_window)
            action.setShortcut("Ctrl+Shift+D")
            action.setCheckable(True)
            action.setChecked(col_debug_controller.debug_enabled)
            action.triggered.connect(toggle_col_debug)
            
            # Add to debug menu if it exists
            for menu in main_window.menuBar().findChildren(type(main_window.menuBar().addMenu('temp'))):
                if 'debug' in menu.title().lower():
                    menu.addAction(action)
                    break
            else:
                # Create debug menu
                debug_menu = main_window.menuBar().addMenu("Debug")
                debug_menu.addAction(action)
            
            return action
        
    except Exception as e:
        print(f"❌ Failed to create debug toggle: {e}")
        return None


# Convenience functions for easy integration
def quick_disable_col_debug():
    """Quick function to disable COL debug"""
    disable_col_debug_for_performance()


def quick_enable_col_debug():
    """Quick function to enable essential COL debug"""
    enable_col_debug_selective(['COL_LOADING'])


# Integration function for main window
def integrate_col_debug_control(main_window):
    """Integrate COL debug control into main window"""
    try:
        # Setup performance mode
        setup_col_performance_mode(main_window)
        
        # Create debug toggle
        create_col_debug_toggle_action(main_window)
        
        # Add methods to main window
        main_window.disable_col_debug = quick_disable_col_debug
        main_window.enable_col_debug = quick_enable_col_debug
        main_window.toggle_col_debug = lambda: (
            quick_disable_col_debug() if col_debug_controller.debug_enabled 
            else quick_enable_col_debug()
        )
        
        main_window.log_message("✅ COL debug control integrated")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL debug integration error: {e}")
        else:
            print(f"❌ COL debug integration error: {e}")
        return False
