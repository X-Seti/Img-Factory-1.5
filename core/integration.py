#this belongs in core/integration.py - Version: 1
# X-Seti - July15 2025 - Img Factory 1.5
# Master integration for all core IMG Factory functions

def integrate_complete_core_system(main_window):
    """
    Master integration function - integrates all core functionality
    Replaces all the scattered patch files with one clean integration
    """
    try:
        main_window.log_message("🔧 Starting core system integration...")
        
        # 1. Integrate core utilities
        from core.utils import integrate_core_functions
        if not integrate_core_functions(main_window):
            return False
        
        # 2. Integrate import functions
        from core.import_funcs import integrate_import_functions
        if not integrate_import_functions(main_window):
            return False
        
        # 3. Integrate export functions
        from core.export import integrate_export_functions
        if not integrate_export_functions(main_window):
            return False
        
        # 4. Integrate remove functions
        from core.remove import integrate_remove_functions
        if not integrate_remove_functions(main_window):
            return False
        
        # 5. Integrate dump functions
        from core.dump import integrate_dump_functions
        if not integrate_dump_functions(main_window):
            return False
        
        # 6. Integrate menu functions
        from core.menus import integrate_menu_functions
        if not integrate_menu_functions(main_window):
            return False
        
        # 7. Integrate core class
        from core.importer import integrate_import_functions
        from core.exporter import integrate_export_functions
        from core.remove import integrate_remove_functions

        
        # 8. Add convenience methods
        main_window.refresh_table = lambda: main_window.get_selected_entries() or main_window.log_message("🔄 Refresh requested")
        main_window.validate_img = lambda: main_window.validate_img_file()
        main_window.show_img_info = lambda: main_window.log_message(f"📊 IMG Info: {main_window.get_img_info()}")
        
        # 9. Fix button method aliases for GUI compatibility
        add_button_method_aliases(main_window)
        
        main_window.log_message("✅ Core system integration complete!")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Core integration failed: {str(e)}")
        return False


def add_button_method_aliases(main_window):
    """Add method aliases for GUI button compatibility"""
    try:
        # Import button methods
        main_window.import_files_function = main_window.import_files
        main_window.import_via_function = main_window.import_files_via
        main_window.import_directory_function = main_window.import_directory
        
        # Export button methods
        main_window.export_selected_function = main_window.export_selected
        main_window.export_via_function = main_window.export_selected_via
        main_window.quick_export_function = main_window.quick_export_selected
        main_window.export_all_function = main_window.export_all_entries
        
        # Remove button methods
        main_window.remove_selected_function = main_window.remove_selected
        main_window.remove_via_entries_function = main_window.remove_via_entries
        
        # Dump button methods
        main_window.dump_all_function = main_window.dump_all_entries
        main_window.dump_all_entries_function = main_window.dump_all_entries
        
        # Legacy compatibility - old naming conventions
        main_window.import_files_threaded = main_window.import_files
        main_window.export_files_threaded = main_window.export_selected
        main_window.dump_entries = main_window.dump_all_entries
        
        main_window.log_message("✅ Button method aliases added")
        
    except Exception as e:
        main_window.log_message(f"❌ Button alias integration failed: {str(e)}")


# Export functions
__all__ = [
    'integrate_complete_core_system',
    'add_button_method_aliases'
]
