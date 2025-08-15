#this belongs in core/tab_aware_functions.py - Version: 1
# X-Seti - August16 2025 - IMG Factory 1.5 - Tab-Aware Export Function Wrapper

"""
Tab-Aware Function Wrapper - Ensures export/import functions work with current tab
Fixes issue where functions can't see current selected tab in multi-tab environment
"""

##Methods list -
# ensure_current_tab_active
# tab_aware_export_selected
# tab_aware_export_via
# tab_aware_dump_entries
# tab_aware_import_files
# tab_aware_import_via
# tab_aware_remove_selected
# tab_aware_remove_via
# integrate_tab_aware_functions

def ensure_current_tab_active(main_window): #vers 1
    """Ensure current tab references are properly set before any operation"""
    try:
        # Force update current tab references
        if hasattr(main_window, 'ensure_current_tab_references_valid'):
            return main_window.ensure_current_tab_references_valid()
        else:
            # Fallback - manually trigger tab change
            current_index = main_window.main_tab_widget.currentIndex()
            if current_index != -1:
                main_window._on_tab_changed(current_index)
                return True
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error ensuring tab active: {str(e)}")
        return False


def tab_aware_export_selected(main_window): #vers 1
    """Export selected entries with tab validation"""
    try:
        # CRITICAL: Ensure current tab is properly referenced
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        # Verify we have a file loaded
        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File", 
                "Please open an IMG or COL file first.")
            return
            
        # Call original export function
        try:
            from core.export import export_selected_function
            export_selected_function(main_window)
        except ImportError:
            # Fallback to legacy functions
            if hasattr(main_window, 'export_selected_entries'):
                main_window.export_selected_entries()
            else:
                main_window.log_message("❌ Export function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware export error: {str(e)}")


def tab_aware_export_via(main_window): #vers 1
    """Export via IDE with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File", 
                "Please open an IMG or COL file first.")
            return
            
        try:
            from core.export import export_via_function
            export_via_function(main_window)
        except ImportError:
            if hasattr(main_window, 'export_selected_via'):
                main_window.export_selected_via()
            else:
                main_window.log_message("❌ Export via function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware export via error: {str(e)}")


def tab_aware_dump_entries(main_window): #vers 1
    """Dump entries with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File", 
                "Please open an IMG or COL file first.")
            return
            
        try:
            from core.dump import dump_all_function
            dump_all_function(main_window)
        except ImportError:
            if hasattr(main_window, 'dump_entries'):
                main_window.dump_entries()
            else:
                main_window.log_message("❌ Dump function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware dump error: {str(e)}")


def tab_aware_import_files(main_window): #vers 1
    """Import files with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        # Import works with empty tabs too, but we need an IMG file for target
        if not main_window.current_img:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No IMG File", 
                "Please open an IMG file first to import into.")
            return
            
        try:
            from core.importer import import_files_function
            import_files_function(main_window)
        except ImportError:
            if hasattr(main_window, 'import_files'):
                main_window.import_files()
            else:
                main_window.log_message("❌ Import function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware import error: {str(e)}")


def tab_aware_import_via(main_window): #vers 1
    """Import via IDE with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        if not main_window.current_img:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No IMG File", 
                "Please open an IMG file first to import into.")
            return
            
        try:
            from core.importer import import_via_function
            import_via_function(main_window)
        except ImportError:
            if hasattr(main_window, 'import_files_via'):
                main_window.import_files_via()
            else:
                main_window.log_message("❌ Import via function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware import via error: {str(e)}")


def tab_aware_remove_selected(main_window): #vers 1
    """Remove selected entries with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File", 
                "Please open an IMG or COL file first.")
            return
            
        try:
            from core.remove import remove_selected_function
            remove_selected_function(main_window)
        except ImportError:
            if hasattr(main_window, 'remove_selected'):
                main_window.remove_selected()
            else:
                main_window.log_message("❌ Remove function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware remove error: {str(e)}")


def tab_aware_remove_via(main_window): #vers 1
    """Remove via entries with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error", 
                "Cannot access current tab data. Please try selecting the tab again.")
            return
            
        if not main_window.current_img:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No IMG File", 
                "Please open an IMG file first.")
            return
            
        try:
            from core.remove import remove_via_entries_function
            remove_via_entries_function(main_window)
        except ImportError:
            if hasattr(main_window, 'remove_via_entries'):
                main_window.remove_via_entries()
            else:
                main_window.log_message("❌ Remove via function not available")
                
    except Exception as e:
        main_window.log_message(f"❌ Tab-aware remove via error: {str(e)}")


def integrate_tab_aware_functions(main_window): #vers 1
    """Replace existing function mappings with tab-aware versions"""
    try:
        # Replace export functions
        main_window.export_selected = lambda: tab_aware_export_selected(main_window)
        main_window.export_selected_entries = lambda: tab_aware_export_selected(main_window)
        main_window.export_selected_via = lambda: tab_aware_export_via(main_window)
        main_window.export_via = lambda: tab_aware_export_via(main_window)
        
        # Replace dump functions
        main_window.dump_entries = lambda: tab_aware_dump_entries(main_window)
        main_window.dump_all_entries = lambda: tab_aware_dump_entries(main_window)
        
        # Replace import functions
        main_window.import_files = lambda: tab_aware_import_files(main_window)
        main_window.import_files_via = lambda: tab_aware_import_via(main_window)
        main_window.import_via = lambda: tab_aware_import_via(main_window)
        
        # Replace remove functions  
        main_window.remove_selected = lambda: tab_aware_remove_selected(main_window)
        main_window.remove_selected_entries = lambda: tab_aware_remove_selected(main_window)
        main_window.remove_via_entries = lambda: tab_aware_remove_via(main_window)
        main_window.remove_via = lambda: tab_aware_remove_via(main_window)
        
        main_window.log_message("✅ Tab-aware functions integrated - Export/Import will now work with current tab")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error integrating tab-aware functions: {str(e)}")
        return False