#this belongs in debug.unified_debug_functions.py - Version: 6
# X-Seti - July17 2025 - IMG Factory 1.5
# Unified Debug Integration - CLEAN VERSION using IMG debug system

"""
Unified Debug Integration - Clean version using IMG debug system
REMOVED CONFLICTS: All COL debug functions now use col_debug_functions.py with IMG debug system
"""

from PyQt6.QtWidgets import QLabel, QMessageBox
from PyQt6.QtGui import QAction, QShortcut, QKeySequence
from PyQt6.QtCore import QTimer

##Methods list -
# add_status_indicators
# apply_all_fixes_and_improvements
# create_debug_menu
# fix_search_dialog
# install_debug_control_system
# install_search_manager
# integrate_all_improvements
# setup_debug_convenience_methods

def debug_trace(func): #vers 1
    """Simple debug decorator to trace function calls."""
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] Calling: {func.__name__} with args={args} kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[DEBUG] Finished: {func.__name__}")
        return result
    return wrapper

def apply_all_fixes_and_improvements(main_window): #vers 1
    """Apply all fixes and improvements to IMG Factory - CLEAN VERSION using IMG debug"""
    try:
        main_window.log_message("🔧 Applying comprehensive fixes...")
        
        # 1. Fix search functionality - simplified approach
        search_manager_success = install_search_manager(main_window)
        search_dialog_success = fix_search_dialog(main_window)
        
        if search_manager_success:
            main_window.log_message("✅ Search manager installed - live search now works")
        
        if search_dialog_success:
            main_window.log_message("✅ Search dialog functionality fixed")
        
        # 2. Install debug control system - simplified
        debug_system_success = install_debug_control_system(main_window)
        
        if debug_system_success:
            main_window.log_message("✅ Debug control system installed")
        
        # 3. COL debug control - NOW USES col_debug_functions.py
        col_debug_success = setup_img_debug_system_integration(main_window)
        
        if col_debug_success:
            main_window.log_message("✅ IMG debug system integrated for COL operations")
        
        # 4. Add convenience methods to main window
        setup_debug_convenience_methods(main_window)
        
        # 5. Create comprehensive debug menu
        create_debug_menu(main_window)
        
        # 6. Show summary of what was fixed
        overall_success = search_manager_success and debug_system_success and col_debug_success
        
        if overall_success:
            main_window.log_message("=" * 50)
            main_window.log_message("🎯 ALL FIXES APPLIED SUCCESSFULLY!")
            main_window.log_message("📖 Check Debug menu for all options")
        
        return overall_success
        
    except Exception as e:
        main_window.log_message(f"❌ Integration error: {e}")
        return False

def setup_img_debug_system_integration(main_window): #vers 1
    """Setup IMG debug system for COL operations - REPLACES old COL debug"""
    try:
        # Use the new col_debug_functions.py which uses IMG debug system
        from debug.col_debug_functions import integrate_col_debug_with_main_window
        
        success = integrate_col_debug_with_main_window(main_window)
        
        if success:
            main_window.log_message("✅ COL operations now use IMG debug system")
        else:
            main_window.log_message("⚠️ COL debug integration had issues")
        
        return success
        
    except Exception as e:
        main_window.log_message(f"IMG debug integration error: {e}")
        return False

def install_search_manager(main_window): #vers 1
    """Install search manager - simplified approach"""
    try:
        # Try to install from core search system
        from core.guisearch import install_search_system
        
        success = install_search_system(main_window)
        
        if success:
            main_window.log_message("✅ Search system installed")
        else:
            main_window.log_message("⚠️ Search system installation issues")
        
        return success
        
    except ImportError:
        main_window.log_message("⚠️ Search system not available")
        return False
    except Exception as e:
        main_window.log_message(f"Search installation error: {e}")
        return False

def fix_search_dialog(main_window): #vers 1
    """Fix search dialog functionality"""
    try:
        # Add search dialog method if missing
        if not hasattr(main_window, 'show_search_dialog'):
            def show_search_dialog():
                """Simple search dialog"""
                try:
                    from core.dialogs import show_search_dialog as core_search
                    core_search(main_window)
                except ImportError:
                    QMessageBox.information(main_window, "Search", 
                        "Use Ctrl+F for quick search in the entries table")
            
            main_window.show_search_dialog = show_search_dialog
        
        return True
        
    except Exception as e:
        main_window.log_message(f"Search dialog error: {e}")
        return False

def install_debug_control_system(main_window): #vers 1
    """Install debug control system - CLEAN VERSION"""
    try:
        # Add missing method to main window
        def show_debug_settings():
            """Simple debug settings dialog"""
            try:
                # Try to show proper debug settings if available
                from utils.app_settings_system import SettingsDialog
                if hasattr(main_window, 'app_settings'):
                    dialog = SettingsDialog(main_window.app_settings, main_window)
                    dialog.exec()
                else:
                    QMessageBox.information(main_window, "Debug Settings", 
                        "Debug settings: Use Ctrl+Shift+D to toggle COL debug")
            except ImportError:
                QMessageBox.information(main_window, "Debug Settings", 
                    "Debug settings: Use Ctrl+Shift+D to toggle COL debug")
        
        main_window.show_debug_settings = show_debug_settings
        
        return True
        
    except Exception as e:
        main_window.log_message(f"Debug control error: {e}")
        return False

def setup_debug_convenience_methods(main_window): #vers 1
    """Add convenience debug methods to main window"""
    try:
        # Add debug info method
        def show_debug_info():
            """Show debug information"""
            try:
                from debug.img_debug_functions import img_debugger
                from debug.col_debug_functions import is_col_debug_enabled
                
                info = f"IMG Debug: {'Enabled' if img_debugger.debug_enabled else 'Disabled'}\n"
                info += f"COL Debug: {'Enabled' if is_col_debug_enabled() else 'Disabled'}\n"
                info += f"Debug Log: {img_debugger.log_file}\n"
                info += f"Error Count: {img_debugger.error_count}\n"
                info += f"Warning Count: {img_debugger.warning_count}"
                
                QMessageBox.information(main_window, "Debug Information", info)
                
            except Exception as e:
                QMessageBox.critical(main_window, "Debug Error", f"Error getting debug info: {e}")
        
        main_window.show_debug_info = show_debug_info
        
        # Add debug log viewer
        def view_debug_log():
            """View debug log file"""
            try:
                from debug.img_debug_functions import img_debugger
                import os
                
                if os.path.exists(img_debugger.log_file):
                    os.system(f"xdg-open {img_debugger.log_file}")  # Linux
                else:
                    QMessageBox.information(main_window, "Debug Log", "No debug log file found")
                    
            except Exception as e:
                QMessageBox.critical(main_window, "Debug Error", f"Error opening debug log: {e}")
        
        main_window.view_debug_log = view_debug_log
        
        return True
        
    except Exception as e:
        main_window.log_message(f"Debug convenience methods error: {e}")
        return False

def create_debug_menu(main_window): #vers 1
    """Create comprehensive debug menu"""
    try:
        menu_bar = main_window.menuBar()
        
        # Find or create Debug menu
        debug_menu = None
        for action in menu_bar.actions():
            if "debug" in action.text().lower():
                debug_menu = action.menu()
                break
        
        if not debug_menu:
            debug_menu = menu_bar.addMenu("🔧 Debug")
        
        # Clear existing debug actions
        debug_menu.clear()
        
        # IMG Debug controls
        img_debug_menu = debug_menu.addMenu("📁 IMG Debug")
        
        img_enable_action = img_debug_menu.addAction("Enable IMG Debug")
        img_enable_action.triggered.connect(lambda: setattr(__import__('debug.img_debug_functions').img_debug_functions.img_debugger, 'debug_enabled', True))
        
        img_disable_action = img_debug_menu.addAction("Disable IMG Debug")
        img_disable_action.triggered.connect(lambda: setattr(__import__('debug.img_debug_functions').img_debug_functions.img_debugger, 'debug_enabled', False))
        
        # COL Debug controls (using IMG debug system)
        col_debug_menu = debug_menu.addMenu("🛡️ COL Debug")
        
        col_enable_action = col_debug_menu.addAction("Enable COL Debug")
        col_enable_action.triggered.connect(lambda: main_window.enable_col_debug() if hasattr(main_window, 'enable_col_debug') else None)
        
        col_disable_action = col_debug_menu.addAction("Disable COL Debug")
        col_disable_action.triggered.connect(lambda: main_window.disable_col_debug() if hasattr(main_window, 'disable_col_debug') else None)
        
        col_toggle_action = col_debug_menu.addAction("Toggle COL Debug")
        col_toggle_action.triggered.connect(lambda: main_window.toggle_col_debug() if hasattr(main_window, 'toggle_col_debug') else None)
        col_toggle_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        
        debug_menu.addSeparator()
        
        # Debug information
        debug_info_action = debug_menu.addAction("📊 Debug Information")
        debug_info_action.triggered.connect(lambda: main_window.show_debug_info() if hasattr(main_window, 'show_debug_info') else None)
        
        # Debug log
        debug_log_action = debug_menu.addAction("📋 View Debug Log")
        debug_log_action.triggered.connect(lambda: main_window.view_debug_log() if hasattr(main_window, 'view_debug_log') else None)
        
        debug_menu.addSeparator()
        
        # Debug settings
        debug_settings_action = debug_menu.addAction("⚙️ Debug Settings")
        debug_settings_action.triggered.connect(lambda: main_window.show_debug_settings() if hasattr(main_window, 'show_debug_settings') else None)
        
        main_window.log_message("✅ Debug menu created")
        return True
        
    except Exception as e:
        main_window.log_message(f"Debug menu error: {e}")
        return False

def add_status_indicators(main_window): #vers 1
    """Add debug status indicators to status bar"""
    try:
        # Create debug status label
        debug_status_label = QLabel("🎛️ Debug Ready")
        debug_status_label.setToolTip("Debug system status")
        
        def update_debug_status():
            """Update debug status display"""
            try:
                from debug.img_debug_functions import img_debugger
                from debug.col_debug_functions import is_col_debug_enabled
                
                img_debug = img_debugger.debug_enabled
                col_debug = is_col_debug_enabled()
                
                if img_debug and col_debug:
                    debug_status_label.setText("🔴 IMG+COL Debug")
                    debug_status_label.setStyleSheet("color: red; font-weight: bold;")
                elif img_debug:
                    debug_status_label.setText("🟡 IMG Debug")
                    debug_status_label.setStyleSheet("color: orange; font-weight: bold;")
                elif col_debug:
                    debug_status_label.setText("🟢 COL Debug")
                    debug_status_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    debug_status_label.setText("🎛️ Debug Ready")
                    debug_status_label.setStyleSheet("color: blue;")
            except:
                debug_status_label.setText("🎛️ Debug Ready")
                debug_status_label.setStyleSheet("color: blue;")
        
        update_debug_status()
        
        # Add to status bar
        main_window.statusBar().addPermanentWidget(debug_status_label)
        
        # Update periodically
        timer = QTimer()
        timer.timeout.connect(update_debug_status)
        timer.start(5000)  # Update every 5 seconds
        
        main_window.log_message("✅ Debug status indicators added")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Status indicators error: {e}")
        return False

def integrate_all_improvements(main_window): #vers 1
    """Main function to integrate all improvements - call this from imgfactory.py"""
    try:
        # Apply core fixes
        core_success = apply_all_fixes_and_improvements(main_window)
        
        # Add additional UI improvements
        add_status_indicators(main_window)
        
        if core_success:
            main_window.log_message("🎉 IMG Factory 1.5 - All improvements integrated successfully!")
            main_window.log_message("📖 Check Debug menu for all options")
        
        return core_success
        
    except Exception as e:
        main_window.log_message(f"❌ Integration error: {e}")
        return False

# Export main functions - REMOVED CONFLICTING COL DEBUG FUNCTIONS
__all__ = [
    'apply_all_fixes_and_improvements',
    'integrate_all_improvements', 
    'install_search_manager',
    'fix_search_dialog',
    'install_debug_control_system',
    'setup_img_debug_system_integration',
    'create_debug_menu',
    'add_status_indicators',
    'setup_debug_convenience_methods'
]
