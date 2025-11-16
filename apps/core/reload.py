#this belongs in core/reload.py - Version: 9
# X-Seti - November16 2025 - IMG Factory 1.5 - Reload Functions - TAB AWARE

"""
Reload Functions - TAB-AWARE VERSION
Gets file from active tab, not main_window.current_img
"""

import os
from PyQt6.QtWidgets import QMessageBox

from apps.methods.tab_system import get_current_file_from_active_tab

##Methods list -
# reload_current_file
# integrate_reload_functions

def reload_current_file(main_window) -> bool: #vers 9
    """Reload file in current tab - TAB AWARE VERSION"""
    try:
        # Get file from active tab
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object:
            QMessageBox.warning(main_window, "No File", "No file is currently loaded in this tab")
            return False
        
        # Get file path
        if not hasattr(file_object, 'file_path'):
            QMessageBox.warning(main_window, "No File Path", "Current file has no file path")
            return False
        
        file_path = file_object.file_path
        if not os.path.exists(file_path):
            QMessageBox.warning(main_window, "File Not Found", f"File not found: {file_path}")
            return False
        
        filename = os.path.basename(file_path)
        
        # Ask for confirmation
        reply = QMessageBox.question(
            main_window,
            "Reload File",
            f"Reload {filename}?\n\nThis will discard any unsaved changes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Reload cancelled by user")
            return False
        
        # Reload based on type
        if file_type == 'IMG':
            return _reload_img_in_tab(main_window, file_path)
        elif file_type == 'COL':
            return _reload_col_in_tab(main_window, file_path)
        else:
            QMessageBox.warning(main_window, "Unsupported Type", f"Cannot reload {file_type} files")
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Reload error: {str(e)}")
        QMessageBox.critical(main_window, "Reload Error", f"Failed to reload file:\n{str(e)}")
        return False


def _reload_img_in_tab(main_window, file_path: str) -> bool: #vers 1
    """Reload IMG file in current tab"""
    try:
        filename = os.path.basename(file_path)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Reloading IMG: {filename}")
        
        # Load new IMG instance
        from apps.methods.img_core_classes import IMGFile
        new_img = IMGFile(file_path)
        
        if not new_img.open():
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Failed to reload IMG: {filename}")
            return False
        
        # Update current tab's file object
        current_index = main_window.main_tab_widget.currentIndex()
        if hasattr(main_window, 'open_files') and current_index in main_window.open_files:
            main_window.open_files[current_index]['file_object'] = new_img
        
        # Update main_window reference (for compatibility)
        main_window.current_img = new_img
        
        # Refresh UI
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        elif hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        
        entry_count = len(new_img.entries) if new_img.entries else 0
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"IMG reloaded: {filename} ({entry_count} entries)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"IMG reload error: {str(e)}")
        return False


def _reload_col_in_tab(main_window, file_path: str) -> bool: #vers 1
    """Reload COL file in current tab"""
    try:
        filename = os.path.basename(file_path)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Reloading COL: {filename}")
        
        # Load new COL instance
        from apps.methods.col_core_classes import COLFile
        new_col = COLFile(file_path)
        
        if not new_col.load():
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Failed to reload COL: {filename}")
            return False
        
        # Update current tab's file object
        current_index = main_window.main_tab_widget.currentIndex()
        if hasattr(main_window, 'open_files') and current_index in main_window.open_files:
            main_window.open_files[current_index]['file_object'] = new_col
        
        # Update main_window reference (for compatibility)
        main_window.current_col = new_col
        
        # Refresh UI
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        elif hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        
        model_count = len(new_col.models) if hasattr(new_col, 'models') and new_col.models else 0
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL reloaded: {filename} ({model_count} models)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL reload error: {str(e)}")
        return False


def integrate_reload_functions(main_window) -> bool: #vers 9
    """Integrate reload functions - TAB AWARE"""
    try:
        # Add reload methods
        main_window.reload_current_file = lambda: reload_current_file(main_window)
        
        # Add aliases
        main_window.reload_file = main_window.reload_current_file
        main_window.reload_table = main_window.reload_current_file
        main_window.refresh_current_file = main_window.reload_current_file
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Reload functions integrated (tab-aware)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Reload integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'reload_current_file',
    'integrate_reload_functions'
]
