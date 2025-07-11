#this belongs in components/ img_integration_patch.py - Version: 1
# X-Seti - July10 2025 - IMG Factory 1.5 - Integration Patch

"""
Integration Patch for IMG Factory 1.5
Fixes search functionality and disables COL debug for better performance
"""

def apply_search_and_performance_fixes(main_window):
    """Apply both search fix and COL performance improvements"""
    try:
        # Apply search fix
        from components.img_search_function import IMGSearchManager, install_search_manager
        
        search_success = install_search_manager(main_window)
        dialog_success = fix_search_dialog(main_window)
        
        if search_success:
            main_window.log_message("✅ Search functionality fixed")
        else:
            main_window.log_message("⚠️ Search fix had issues - check search input locations")
        
        if dialog_success:
            main_window.log_message("✅ Search dialog fixed")
        
        # Apply COL performance fix
        from components.col_debug_control import integrate_col_debug_control
        
        perf_success = integrate_col_debug_control(main_window)
        
        if perf_success:
            main_window.log_message("✅ COL debug disabled for better performance")
        else:
            main_window.log_message("⚠️ COL performance fix had issues")
        
        # Add convenient methods to main window
        main_window.fix_search = lambda: install_search_manager(main_window)
        main_window.toggle_col_debug = lambda: main_window.toggle_col_debug()
        
        overall_success = search_success and perf_success
        
        if overall_success:
            main_window.log_message("🎯 Integration patch applied successfully!")
            main_window.log_message("📝 Search box now works with live filtering")
            main_window.log_message("🚀 COL loading is faster (debug disabled)")
            main_window.log_message("⌨️ Use Ctrl+Shift+D to toggle COL debug if needed")
        
        return overall_success
        
    except Exception as e:
        main_window.log_message(f"❌ Integration patch error: {e}")
        return False


def add_to_imgfactory_startup(main_window):
    """Add this to imgfactory.py startup sequence"""
    """
    To integrate this fix, add this line to imgfactory.py in the __init__ method:
    
    # After GUI setup, before final logging
    from components.integration_patch import apply_search_and_performance_fixes
    apply_search_and_performance_fixes(self)
    """
    apply_search_and_performance_fixes(main_window)
