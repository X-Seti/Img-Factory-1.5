#this belongs in core/ remove.py - Version: 3
# X-Seti - September08 2025 - IMG Factory 1.5 - Remove Functions with Proper Refresh

"""
Remove Functions - Remove entries with comprehensive UI refresh
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# remove_selected_function
# remove_entries_by_name
# remove_multiple_entries
# _remove_entries_direct
# _get_selected_entries_simple
# _get_selected_rows_from_table
# _refresh_after_removal
# integrate_remove_functions

def remove_selected_function(main_window): #vers 3
    """Remove selected entries with proper refresh sequence"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Remove Selected"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Get selected entries
        selected_entries = _get_selected_entries_simple(main_window, file_object)
        
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "No entries selected for removal")
            return False
        
        # Confirm removal
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            f"Remove {len(selected_entries)} selected entries from memory?\n\n"
            f"⚠️ Use 'Save Entry' afterwards to save changes to disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Remove operation cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(selected_entries)} selected entries")
        
        # Remove entries using working method
        success = _remove_entries_direct(file_object, selected_entries, main_window)
        
        if success:
            # Comprehensive refresh after removal
            _refresh_after_removal(main_window)
            
            # Inform user about saving changes
            QMessageBox.information(
                main_window, 
                "Remove Complete", 
                f"Successfully removed {len(selected_entries)} entries from memory.\n\n"
                f"💾 Use the 'Save Entry' button to save changes to disk.\n"
                f"⚠️ Changes will be lost if you reload without saving."
            )
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Removed {len(selected_entries)} entries - use 'Save Entry' to save changes")
        else:
            QMessageBox.critical(main_window, "Remove Failed", 
                "Failed to remove selected entries. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove selected error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove error: {str(e)}")
        return False


def remove_entries_by_name(main_window, entry_names: List[str]) -> bool: #vers 3
    """Remove entries by name programmatically with proper refresh"""
    try:
        if not validate_tab_before_operation(main_window, "Remove Entries by Name"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if not entry_names:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entry_names)} entries by name")
        
        # Find entries to remove
        entries_to_remove = []
        if hasattr(file_object, 'entries'):
            for entry in file_object.entries:
                if entry.name in entry_names:
                    entries_to_remove.append(entry)
        
        if not entries_to_remove:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No matching entries found for removal")
            return False
        
        # Remove entries
        success = _remove_entries_direct(file_object, entries_to_remove, main_window)
        
        if success:
            # Comprehensive refresh after removal
            _refresh_after_removal(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Removed {len(entries_to_remove)} entries by name")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove by name error: {str(e)}")
        return False


def remove_multiple_entries(main_window, entries_to_remove: List) -> bool: #vers 3
    """Remove multiple entries programmatically with proper refresh"""
    try:
        if not validate_tab_before_operation(main_window, "Remove Multiple Entries"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if not entries_to_remove:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries programmatically")
        
        # Remove entries
        success = _remove_entries_direct(file_object, entries_to_remove, main_window)
        
        if success:
            # Comprehensive refresh after removal
            _refresh_after_removal(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Removed {len(entries_to_remove)} entries programmatically")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove multiple error: {str(e)}")
        return False


def _remove_entries_direct(file_object, entries_to_remove: List, main_window) -> bool: #vers 3
    """Remove entries directly from IMG file object"""
    try:
        if not hasattr(file_object, 'entries'):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG file has no entries attribute")
            return False
        
        removed_count = 0
        
        # Method 1: Use IMG file's native remove method if available
        for entry in entries_to_remove:
            entry_name = getattr(entry, 'name', str(entry))
            
            if hasattr(file_object, 'remove_entry') and callable(file_object.remove_entry):
                if file_object.remove_entry(entry_name):
                    removed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"🗑️ Removed: {entry_name}")
                else:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Failed to remove: {entry_name}")
            else:
                # Method 2: Direct removal from entries list
                try:
                    if entry in file_object.entries:
                        file_object.entries.remove(entry)
                        removed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🗑️ Removed: {entry_name}")
                    else:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Entry not found: {entry_name}")
                except Exception as e:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Remove error for {entry_name}: {str(e)}")
        
        # Mark file as modified
        if removed_count > 0:
            if hasattr(file_object, 'modified'):
                file_object.modified = True
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📊 Successfully removed {removed_count}/{len(entries_to_remove)} entries")
        
        return removed_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Direct removal error: {str(e)}")
        return False


def _get_selected_entries_simple(main_window, file_object) -> list: #vers 3
    """Get selected entries using simple working method"""
    try:
        selected_entries = []
        
        # Method 1: Try to get selection from main window
        if hasattr(main_window, 'get_selected_entries'):
            try:
                selected_entries = main_window.get_selected_entries()
                if selected_entries:
                    return selected_entries
            except Exception:
                pass
        
        # Method 2: Try to get selected rows from table
        selected_rows = _get_selected_rows_from_table(main_window)
        if selected_rows and hasattr(file_object, 'entries') and file_object.entries:
            for row in selected_rows:
                if row < len(file_object.entries):
                    selected_entries.append(file_object.entries[row])
        
        return selected_entries
        
    except Exception:
        return []


def _get_selected_rows_from_table(main_window) -> list: #vers 3
    """Get selected row numbers from entries table"""
    try:
        selected_rows = []
        
        # Try different table attributes
        table_attrs = ['entries_table', 'table', 'gui_layout.table']
        
        for attr in table_attrs:
            try:
                if '.' in attr:
                    parts = attr.split('.')
                    table = getattr(main_window, parts[0])
                    for part in parts[1:]:
                        table = getattr(table, part)
                else:
                    table = getattr(main_window, attr)
                
                if table and hasattr(table, 'selectedItems'):
                    selected_items = table.selectedItems()
                    if selected_items:
                        # Get unique row numbers
                        rows = set()
                        for item in selected_items:
                            rows.add(item.row())
                        selected_rows = sorted(list(rows))
                        break
                        
            except AttributeError:
                continue
        
        return selected_rows
        
    except Exception:
        return []


def _refresh_after_removal(main_window): #vers 2
    """Comprehensive refresh after removal - FIXED: No blocking RW detection"""
    try:
        # 1. Skip RW re-parsing to avoid UI freeze - table refresh will show existing RW data
        # Note: RW versions are preserved from when entries were first loaded
        
        # 2. Refresh table with highlights if available
        if hasattr(main_window, 'refresh_table_with_highlights'):
            main_window.refresh_table_with_highlights()
        elif hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        
        # 3. Refresh file list window
        if hasattr(main_window, 'refresh_file_list'):
            main_window.refresh_file_list()
        
        # 4. Update filewindow display via GUI layout
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'refresh_file_list'):
            main_window.gui_layout.refresh_file_list()
        
        # 5. Update UI for current IMG
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()
        
        # 6. Update current tab data
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        
        # 7. Force table repaint
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            main_window.gui_layout.table.viewport().update()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 UI refreshed after removal (RW data preserved)")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error in removal refresh: {str(e)}")


def integrate_remove_functions(main_window) -> bool: #vers 3
    """Integrate remove functions into main window"""
    try:
        # Add remove methods to main window
        main_window.remove_selected_function = lambda: remove_selected_function(main_window)
        main_window.remove_entries_by_name = lambda names: remove_entries_by_name(main_window, names)
        main_window.remove_multiple_entries = lambda entries: remove_multiple_entries(main_window, entries)
        
        # Add aliases that GUI might use
        main_window.remove_selected = main_window.remove_selected_function
        main_window.remove_entries = main_window.remove_entries_by_name
        main_window.remove_multiple = main_window.remove_multiple_entries
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Remove functions integrated")
            main_window.log_message("   • Simple UI refresh after removal")
            main_window.log_message("   • No unnecessary RW detection")
            main_window.log_message("   • Proper filewindow updates")
            main_window.log_message("   • Multiple removal methods available")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'remove_selected_function',
    'remove_entries_by_name',
    'remove_multiple_entries',
    'integrate_remove_functions'
]