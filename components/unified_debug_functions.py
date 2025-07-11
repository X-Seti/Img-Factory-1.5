#this belongs in components/ unified_debug_functions.py - Version: 1
# X-Seti - July10 2025 - IMG Factory 1.5 - Unified Debug Integration

"""
Unified Debug Integration
Combines search fix, COL debug control, and performance improvements
"""

def apply_all_fixes_and_improvements(main_window):
    """Apply all fixes and improvements to IMG Factory"""
    try:
        main_window.log_message("🔧 Applying comprehensive fixes...")
        
        # 1. Fix search functionality
        from components.img_search_fix import install_search_manager, fix_search_dialog
        
        search_manager_success = install_search_manager(main_window)
        search_dialog_success = fix_search_dialog(main_window)
        
        if search_manager_success:
            main_window.log_message("✅ Search manager installed - live search now works")
        
        if search_dialog_success:
            main_window.log_message("✅ Search dialog functionality fixed")
        
        # 2. Install comprehensive debug control system
        from components.debug_control_system import install_debug_control_system
        
        debug_system_success = install_debug_control_system(main_window)
        
        if debug_system_success:
            main_window.log_message("✅ Debug control system installed")
        
        # 3. Patch COL files to stop print spam
        from components.col_print_patcher import install_col_print_patcher
        
        col_patcher_success = install_col_print_patcher(main_window)
        
        if col_patcher_success:
            main_window.log_message("✅ COL print spam eliminated")
        
        # 4. Add convenience methods to main window
        def show_debug_settings():
            """Show comprehensive debug settings dialog"""
            from components.debug_control_system import DebugControlDialog
            dialog = DebugControlDialog(main_window)
            dialog.exec()
        
        def quick_performance_mode():
            """Quick switch to performance mode"""
            from components.debug_control_system import debug_controller
            debug_controller.quick_preset_off()
            main_window.log_message("🚀 Performance mode activated - all debug disabled")
        
        def quick_minimal_debug():
            """Quick switch to minimal debug mode"""
            from components.debug_control_system import debug_controller
            debug_controller.quick_preset_errors_only()
            main_window.log_message("⚠️ Minimal debug mode - errors only")
        
        def quick_col_debug():
            """Quick switch to COL debug mode"""
            from components.debug_control_system import debug_controller
            debug_controller.quick_preset_col_minimal()
            main_window.log_message("📁 COL debug mode - minimal COL logging")
        
        # Add methods to main window
        main_window.show_debug_settings = show_debug_settings
        main_window.performance_mode = quick_performance_mode
        main_window.minimal_debug_mode = quick_minimal_debug
        main_window.col_debug_mode = quick_col_debug
        
        # 5. Create comprehensive debug menu
        create_debug_menu(main_window)
        
        # 6. Show summary of what was fixed
        overall_success = search_manager_success and debug_system_success and col_patcher_success
        
        if overall_success:
            main_window.log_message("=" * 50)
            main_window.log_message("🎯 ALL FIXES APPLIED SUCCESSFULLY!")
            main_window.log_message("📝 Search box now works with live filtering")
            main_window.log_message("🚀 COL loading is much faster (debug disabled)")
            main_window.log_message("🎛️ Debug control available via Ctrl+Shift+D")
            main_window.log_message("⌨️ COL debug toggle: Ctrl+Alt+C")
            main_window.log_message("🔍 Search shortcuts: F3 (next), Shift+F3 (prev)")
            main_window.log_message("=" * 50)
        else:
            main_window.log_message("⚠️ Some fixes had issues - check logs above")
        
        return overall_success
        
    except Exception as e:
        main_window.log_message(f"❌ Unified integration error: {e}")
        return False


def create_debug_menu(main_window):
    """Create comprehensive debug menu"""
    try:
        if not hasattr(main_window, 'menuBar'):
            return
        
        # Find or create Debug menu
        debug_menu = None
        for menu in main_window.menuBar().findChildren(type(main_window.menuBar().addMenu('temp'))):
            if 'debug' in menu.title().lower():
                debug_menu = menu
                break
        
        if not debug_menu:
            debug_menu = main_window.menuBar().addMenu("Debug")
        
        # Clear existing debug menu items to avoid duplicates
        debug_menu.clear()
        
        from PyQt6.QtGui import QAction
        from PyQt6.QtCore import QKeySequence
        
        # Debug Control Settings
        settings_action = QAction("🎛️ Debug Control Settings...", main_window)
        settings_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        settings_action.triggered.connect(main_window.show_debug_settings)
        debug_menu.addAction(settings_action)
        
        debug_menu.addSeparator()
        
        # Quick Mode Actions
        performance_action = QAction("🚀 Performance Mode (All Debug Off)", main_window)
        performance_action.triggered.connect(main_window.performance_mode)
        debug_menu.addAction(performance_action)
        
        minimal_action = QAction("⚠️ Minimal Debug (Errors Only)", main_window)
        minimal_action.triggered.connect(main_window.minimal_debug_mode)
        debug_menu.addAction(minimal_action)
        
        col_action = QAction("📁 COL Debug Mode", main_window)
        col_action.triggered.connect(main_window.col_debug_mode)
        debug_menu.addAction(col_action)
        
        debug_menu.addSeparator()
        
        # COL Debug Toggle
        col_toggle_action = QAction("🔇/🔊 Toggle COL Debug", main_window)
        col_toggle_action.setShortcut(QKeySequence("Ctrl+Alt+C"))
        col_toggle_action.setCheckable(True)
        col_toggle_action.triggered.connect(main_window.enable_col_debug)
        debug_menu.addAction(col_toggle_action)
        
        debug_menu.addSeparator()
        
        # Search Functions
        search_action = QAction("🔍 Test Search Function", main_window)
        search_action.triggered.connect(lambda: main_window.show_search_dialog() if hasattr(main_window, 'show_search_dialog') else None)
        debug_menu.addAction(search_action)
        
        main_window.log_message("✅ Debug menu created")
        
    except Exception as e:
        main_window.log_message(f"❌ Debug menu creation error: {e}")


def add_status_indicators(main_window):
    """Add debug status indicators to status bar"""
    try:
        if not hasattr(main_window, 'statusBar'):
            return
        
        from PyQt6.QtWidgets import QLabel
        from components.debug_control_system import debug_controller
        
        # Create debug status label
        debug_status_label = QLabel()
        
        def update_debug_status():
            if debug_controller.performance_mode:
                debug_status_label.setText("🚀 Performance Mode")
                debug_status_label.setStyleSheet("color: green; font-weight: bold;")
            elif debug_controller.debug_level.value <= 1:
                debug_status_label.setText("⚠️ Minimal Debug")
                debug_status_label.setStyleSheet("color: orange;")
            else:
                debug_status_label.setText("🔍 Full Debug")
                debug_status_label.setStyleSheet("color: red;")
        
        update_debug_status()
        
        # Add to status bar
        main_window.statusBar().addPermanentWidget(debug_status_label)
        
        # Update periodically
        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(update_debug_status)
        timer.start(5000)  # Update every 5 seconds
        
        main_window.log_message("✅ Debug status indicators added")
        
    except Exception as e:
        main_window.log_message(f"❌ Status indicators error: {e}")


def create_debug_keyboard_shortcuts(main_window):
    """Create keyboard shortcuts for debug functions"""
    try:
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # F12 - Quick performance mode toggle
        def toggle_performance():
            from components.debug_control_system import debug_controller
            if debug_controller.performance_mode:
                main_window.minimal_debug_mode()
            else:
                main_window.performance_mode()
        
        perf_shortcut = QShortcut(QKeySequence("F12"), main_window)
        perf_shortcut.activated.connect(toggle_performance)
        
        # Ctrl+F12 - Show debug settings
        debug_shortcut = QShortcut(QKeySequence("Ctrl+F12"), main_window)
        debug_shortcut.activated.connect(main_window.show_debug_settings)
        
        main_window.log_message("✅ Debug keyboard shortcuts created")
        main_window.log_message("⌨️ F12: Toggle performance mode")
        main_window.log_message("⌨️ Ctrl+F12: Debug settings")
        
    except Exception as e:
        main_window.log_message(f"❌ Keyboard shortcuts error: {e}")


# Main integration function for imgfactory.py
def integrate_all_improvements(main_window):
    """Main function to integrate all improvements - call this from imgfactory.py"""
    try:
        # Apply core fixes
        core_success = apply_all_fixes_and_improvements(main_window)
        
        # Add additional UI improvements
        add_status_indicators(main_window)
        create_debug_keyboard_shortcuts(main_window)
        
        if core_success:
            main_window.log_message("🎉 IMG Factory 1.5 - All improvements integrated successfully!")
            main_window.log_message("📖 Check Debug menu for all options")
        
        return core_success
        
    except Exception as e:
        main_window.log_message(f"❌ Integration error: {e}")
        return False


"""
TO INTEGRATE INTO IMGFACTORY.PY:
==================================

Add this single line in imgfactory.py __init__ method, after GUI setup:

    # Apply all fixes and improvements
    from components.unified_debug_integration import integrate_all_improvements
    integrate_all_improvements(self)

This will:
✅ Fix the broken search box
✅ Silence COL debug spam  
✅ Add comprehensive debug controls
✅ Create debug menu with shortcuts
✅ Add status indicators
✅ Provide performance/debug mode toggles
"""
