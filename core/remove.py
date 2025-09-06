#this belongs in core/ remove.py - Version: 4
# X-Seti - September06 2025 - IMG Factory 1.5 - Remove Functions

"""
Remove Functions - Uses same pattern as fixed import functions
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QMessageBox, QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

try:
    from components.img_integration import IMGArchive, IMGEntry, Import_Export
    IMG_INTEGRATION_AVAILABLE = True
except ImportError:
    IMG_INTEGRATION_AVAILABLE = False

##Methods list -
# remove_selected_function
# remove_entries_by_name
# remove_multiple_entries
# _remove_entries
# _get_selected_entries_safe
# _create_remove_progress_dialog
# _convert_to_imgfactory_object
# integrate_remove_functions

def remove_selected_function(main_window): #vers 2
    """Remove selected entries"""
    try:
        # Use same tab validation as import functions
        if not validate_tab_before_operation(main_window, "Remove Selected"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Get selected entries
        selected_entries = _get_selected_entries_safe(main_window, file_object)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "No entries selected for removal")
            return False
        
        # Confirm removal
        entry_names = [getattr(entry, 'name', 'Unknown') for entry in selected_entries]
        entry_list = '\n'.join(entry_names[:10])  # Show first 10
        if len(entry_names) > 10:
            entry_list += f"\n... and {len(entry_names) - 10} more"
        
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            f"Remove {len(selected_entries)} selected entries?\n\n{entry_list}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Remove operation cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(selected_entries)} selected entries")
        
        success = _remove_entries(file_object, selected_entries, main_window)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Remove Complete", 
                f"Successfully removed {len(selected_entries)} entries")
        else:
            QMessageBox.critical(main_window, "Remove Failed", 
                "Failed to remove selected entries. Check debug log for details.")
                
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove selected error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove failed: {str(e)}")
        return False


def remove_entries_by_name(main_window, entry_names: List[str]) -> bool: #vers 2
    """Remove entries by name list"""
    try:
        if not validate_tab_before_operation(main_window, "Remove Entries"):
            return False
            
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Current tab does not contain an IMG file")
            return False
        
        # Find entries to remove
        entries_to_remove = []
        if hasattr(file_object, 'entries'):
            for entry in file_object.entries:
                entry_name = getattr(entry, 'name', '')
                if entry_name in entry_names:
                    entries_to_remove.append(entry)
        
        if not entries_to_remove:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ No matching entries found for removal")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries by name")
        
        return _remove_entries(file_object, entries_to_remove, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove by name error: {str(e)}")
        return False


def remove_multiple_entries(main_window, entries: List) -> bool: #vers 2  
    """Remove multiple entries"""
    try:
        if not validate_tab_before_operation(main_window, "Remove Multiple"):
            return False
            
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
            
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries)} multiple entries")
            
        return _remove_entries(file_object, entries, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove multiple error: {str(e)}")
        return False


def _remove_entries(file_object, entries_to_remove: List, main_window) -> bool: #vers 2
    """Remove entries"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG core not available for removal")
            return False
        
        # Convert to IMG archive format (same as import)
        img_archive = _convert_img_to_archive(file_object, main_window)
        if not img_archive:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Could not convert to IMG archive format")
            return False
        
        # Create progress dialog (same as import)
        progress_dialog = _create_remove_progress_dialog(main_window, len(entries_to_remove))
        progress_dialog.show()
        QApplication.processEvents()
        
        removed_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(entries_to_remove):
                if progress_dialog.wasCanceled():
                    break
                
                entry_name = getattr(entry, 'name', f'Entry_{i}')
                progress_dialog.setLabelText(f"Removing: {entry_name}")
                progress_dialog.setValue(i)
                QApplication.processEvents()
                
                # Find entry in IMG archive
                img_archedit_entry = None
                for archive_entry in img_archive.entries:
                    if getattr(archive_entry, 'name', '') == entry_name:
                        img_archedit_entry = archive_entry
                        break
                
                if not img_archedit_entry:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ Entry not found in archive: {entry_name}")
                    failed_count += 1
                    continue
                
                # Remove entry from archive
                try:
                    img_archive.entries.remove(img_archedit_entry)
                    removed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ Removed: {entry_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Remove error for {entry_name}: {str(e)}")
            
        finally:
            progress_dialog.close()
        
        # Report results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Removal complete: {removed_count} success, {failed_count} failed")
            if removed_count > 0:
                main_window.log_message("💾 Remember to rebuild IMG to save changes")
        
        return removed_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG archive removal error: {str(e)}")
        return False


def _get_selected_entries_safe(main_window, file_object) -> list: #vers 2
    """Safely get selected entries from main window"""
    try:
        selected_entries = []
        
        # Method 1: Use main window's get_selected_entries
        if hasattr(main_window, 'get_selected_entries'):
            try:
                selected_entries = main_window.get_selected_entries()
                if selected_entries:
                    return selected_entries
            except Exception:
                pass
        
        # Method 2: Check if there's a table widget
        if hasattr(main_window, 'entries_table'):
            try:
                table = main_window.entries_table
                selected_rows = set()
                
                for item in table.selectedItems():
                    selected_rows.add(item.row())
                
                if selected_rows and hasattr(file_object, 'entries'):
                    for row in selected_rows:
                        if row < len(file_object.entries):
                            selected_entries.append(file_object.entries[row])
                
                if selected_entries:
                    return selected_entries
                    
            except Exception:
                pass
        
        return []
        
    except Exception:
        return []


def _create_remove_progress_dialog(main_window, total_entries) -> QProgressDialog: #vers 2
    """Create progress dialog for remove operation"""
    try:
        progress_dialog = QProgressDialog(
            "Preparing removal...",
            "Cancel",
            0,
            total_entries,
            main_window
        )
        progress_dialog.setWindowTitle("Removing Entries")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(500)
        progress_dialog.setValue(0)
        
        return progress_dialog
        
    except Exception:
        # Fallback to basic dialog
        from PyQt6.QtWidgets import QProgressDialog
        return QProgressDialog("Removing entries...", "Cancel", 0, total_entries, main_window)


def _convert_img_to_archive(file_object, main_window): #vers 2
    """Convert file object to IMG archive format"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            return None
        
        # If already IMG format, return as-is
        if isinstance(file_object, IMGArchive):
            return file_object
        
        # Load IMG file
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Create and load IMG archive
        archive = IMGArchive()
        if archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                entry_count = len(archive.entries) if archive.entries else 0
                main_window.log_message(f"✅ Converted to IMG archive format: {entry_count} entries")
            return archive
        
        return None
        
    except Exception:
        return None


def integrate_remove_functions(main_window) -> bool: #vers 2
    """Integrate remove functions into main window"""
    try:
        # Main remove functions with IMG
        main_window.remove_selected_function = lambda: remove_selected_function(main_window)
        main_window.remove_entries_by_name = lambda entry_names: remove_entries_by_name(main_window, entry_names)
        main_window.remove_multiple_entries = lambda entries: remove_multiple_entries(main_window, entries)
        
        # Add aliases that GUI might use
        main_window.remove_selected = main_window.remove_selected_function
        main_window.remove_selected_entries = main_window.remove_selected_function
        main_window.delete_selected = main_window.remove_selected_function
        main_window.remove_entries = main_window.remove_multiple_entries
        
        if hasattr(main_window, 'log_message'):
            integration_msg = "✅ Remove functions integrated with tab awareness + imgfactory methods"
            main_window.log_message(integration_msg)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove integration failed: {str(e)}")
        return False


# Export only the essential functions
__all__ = [
    'remove_selected_function',
    'remove_entries_by_name', 
    'remove_multiple_entries',
    'integrate_remove_functions'
]
