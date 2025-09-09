#this belongs in core/ save_entry.py - Version: 3
# X-Seti - September08 2025 - IMG Factory 1.5 - Save Entry Function Final

"""
Save Entry Function - Handles saving memory data to IMG file with comprehensive refresh
Uses existing rebuild_current_img_native function with proper UI updates
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QMessageBox

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# save_img_entry
# _check_for_changes
# _clear_modification_flags
# _refresh_everything_after_save
# integrate_save_entry_function

def save_img_entry(main_window): #vers 3
    """Save IMG entry changes by rebuilding the IMG file with comprehensive refresh"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Save Entry"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Check if there are changes to save
        has_changes = _check_for_changes(file_object, main_window)
        
        if not has_changes:
            QMessageBox.information(main_window, "No Changes", "No changes detected. IMG file is up to date.")
            return True
        
        # Ask user to confirm save
        reply = QMessageBox.question(
            main_window,
            "Save Changes",
            "This will rebuild the IMG file to save all changes to disk.\n\n"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # Use existing rebuild function
        from core.rebuild import rebuild_current_img_native
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"💾 Saving changes to: {os.path.basename(file_object.file_path)}")
        
        success = rebuild_current_img_native(main_window)
        
        if success:
            # Clear modification flags after successful save
            _clear_modification_flags(file_object, main_window)
            
            # Comprehensive refresh after save
            _refresh_everything_after_save(main_window)
            
            QMessageBox.information(main_window, "Save Complete", 
                "IMG file saved successfully!\n\nAll changes have been written to disk.")
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ IMG file saved - memory data written to disk")
        else:
            QMessageBox.critical(main_window, "Save Failed", "Failed to save IMG file changes")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Save entry error: {str(e)}")
        QMessageBox.critical(main_window, "Save Error", f"Save error: {str(e)}")
        return False


def _check_for_changes(file_object, main_window) -> bool: #vers 3
    """Check if IMG file has unsaved changes"""
    try:
        # Method 1: Check modified flag
        if hasattr(file_object, 'modified') and file_object.modified:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("💾 Changes detected: IMG marked as modified")
            return True
        
        # Method 2: Check for new entries
        if hasattr(file_object, 'entries'):
            new_count = 0
            modified_count = 0
            for entry in file_object.entries:
                if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                    new_count += 1
                if hasattr(entry, 'modified') and entry.modified:
                    modified_count += 1
            
            if new_count > 0 or modified_count > 0:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"💾 Changes detected: {new_count} new, {modified_count} modified entries")
                return True
        
        # Method 3: Check deleted entries
        if hasattr(file_object, 'deleted_entries') and file_object.deleted_entries:
            deleted_count = len(file_object.deleted_entries)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"💾 Changes detected: {deleted_count} deleted entries")
            return True
        
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Check changes error: {str(e)}")
        return False


def _clear_modification_flags(file_object, main_window): #vers 3
    """Clear modification flags after successful save"""
    try:
        # Clear file modified flag
        if hasattr(file_object, 'modified'):
            file_object.modified = False
        
        # Clear entry modification flags
        if hasattr(file_object, 'entries'):
            for entry in file_object.entries:
                if hasattr(entry, 'is_new_entry'):
                    entry.is_new_entry = False
                if hasattr(entry, 'modified'):
                    entry.modified = False
        
        # Clear deleted entries list
        if hasattr(file_object, 'deleted_entries'):
            file_object.deleted_entries.clear()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🧹 Cleared modification flags")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error clearing flags: {str(e)}")


def _refresh_everything_after_save(main_window): #vers 2
    """Comprehensive refresh after successful save - FIXED: No blocking RW detection"""
    try:
        # 1. Skip RW re-parsing to avoid UI freeze - rebuild already has fresh data
        # Note: rebuild_current_img_native already handles RW detection properly
        
        # 2. Refresh main table with updated data
        if hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
            if hasattr(main_window, 'log_message'):
                main_window.log_message("🔄 Table refreshed")
        
        # 3. Refresh file list window  
        if hasattr(main_window, 'refresh_file_list'):
            main_window.refresh_file_list()
            if hasattr(main_window, 'log_message'):
                main_window.log_message("🔄 File list refreshed")
        
        # 4. Update filewindow display via GUI layout
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'refresh_file_list'):
            main_window.gui_layout.refresh_file_list()
        
        # 5. Update UI state for loaded IMG
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()
        
        # 6. Update current tab data
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        
        # 7. Clear import highlights (file saved, no longer "imported")
        if hasattr(main_window, '_import_highlight_manager'):
            main_window._import_highlight_manager.clear_highlights()
            if hasattr(main_window, 'log_message'):
                main_window.log_message("🧹 Cleared import highlights")
        
        # 8. Force table repaint to show all updates
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            main_window.gui_layout.table.viewport().update()
        
        # 9. Update file info display if available
        if hasattr(main_window, 'update_file_info'):
            main_window.update_file_info()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 All UI components refreshed after save")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error in comprehensive refresh: {str(e)}")


def integrate_save_entry_function(main_window) -> bool: #vers 4
    """Integrate save entry function into main window - WORKING VERSION"""
    try:
        # Add save_img_entry method to main window with multiple aliases
        main_window.save_img_entry = lambda: save_img_entry(main_window)
        main_window.save_entry = lambda: save_img_entry(main_window)
        main_window.save_img_changes = lambda: save_img_entry(main_window)
        main_window.save_memory_to_disk = lambda: save_img_entry(main_window)
        
        # Add more aliases that GUI might use
        main_window.save_img_entry_function = lambda: save_img_entry(main_window)
        main_window.save_changes = lambda: save_img_entry(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Save Entry function integrated")
            main_window.log_message("   • Uses rebuild_current_img_native")
            main_window.log_message("   • Always allows saving current memory state")
            main_window.log_message("   • Multiple function aliases available")
            main_window.log_message("   • Simple UI refresh after save")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Save Entry integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'save_img_entry',
    'integrate_save_entry_function'
]
