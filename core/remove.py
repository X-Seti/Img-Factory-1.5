#this belongs in core/ remove.py - Version: 1
# X-Seti - August24 2025 - IMG Factory 1.5 - Remove Functions


import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system (this works!)
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# remove_selected_function
# remove_entries_by_name
# remove_multiple_entries
# _remove_using_img_editor_core
# _get_selected_entries_safe
# _create_remove_progress_dialog
# _convert_img_to_archive
# integrate_remove_functions

def remove_selected_function(main_window): #vers 1
    """Remove selected entries using IMG_Editor core - TAB AWARE"""
    try:
        # Use same tab validation as rebuild.py
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
        
        # Use IMG_Editor core for removal
        success = _remove_using_img_editor_core(file_object, selected_entries, main_window)
        
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
        QMessageBox.critical(main_window, "Remove Error", f"Remove error: {str(e)}")
        return False


def remove_entries_by_name(main_window, entry_names: List[str]) -> bool: #vers 1
    """Remove entries by name programmatically"""
    try:
        if not validate_tab_before_operation(main_window, "Remove Entries by Name"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if not entry_names:
            return False
        
        # Find entries by name
        entries_to_remove = []
        if hasattr(file_object, 'entries'):
            for entry in file_object.entries:
                entry_name = getattr(entry, 'name', '')
                if entry_name in entry_names:
                    entries_to_remove.append(entry)
        
        if not entries_to_remove:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No matching entries found for removal")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries by name")
        
        return _remove_using_img_editor_core(file_object, entries_to_remove, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove by name error: {str(e)}")
        return False


def remove_multiple_entries(main_window, entries_to_remove: List) -> bool: #vers 1
    """Remove multiple entries programmatically"""
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
        
        return _remove_using_img_editor_core(file_object, entries_to_remove, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove multiple error: {str(e)}")
        return False


def _remove_using_img_editor_core(file_object, entries_to_remove, main_window) -> bool: #vers 1
    """CORE FUNCTION: Remove entries using working IMG_Editor archive manipulation"""
    try:
        # Import the working IMG_Editor core classes
        try:
            from IMG_Editor.core.Core import IMGArchive, IMGEntry
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG_Editor core not available - cannot remove")
            return False
        
        # Convert to IMG_Editor archive format if needed
        img_archive = _convert_img_to_archive(file_object, main_window)
        if not img_archive:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to convert IMG to archive format")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Using IMG_Editor archive entry removal")
        
        # Create progress dialog
        progress_dialog = _create_remove_progress_dialog(main_window, len(entries_to_remove))
        
        removed_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(entries_to_remove):
                # Update progress
                progress_dialog.setValue(i)
                entry_name = getattr(entry, 'name', f'entry_{i}')
                progress_dialog.setLabelText(f"Removing: {entry_name}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("Remove operation cancelled by user")
                    break
                
                # Find entry in IMG_Editor archive
                img_editor_entry = None
                for j, archive_entry in enumerate(img_archive.entries):
                    if archive_entry.name == entry_name:
                        img_editor_entry = archive_entry
                        break
                
                if not img_editor_entry:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ Entry not found in archive: {entry_name}")
                    failed_count += 1
                    continue
                
                # Remove entry from archive
                try:
                    img_archive.entries.remove(img_editor_entry)
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
            main_window.log_message(f"📊 Remove complete: {removed_count} success, {failed_count} failed")
        
        # If successful removals, need to save/rebuild IMG
        if removed_count > 0:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("💾 Remove successful - remember to rebuild IMG to save changes")
        
        return removed_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core remove error: {str(e)}")
        return False


def _get_selected_entries_safe(main_window, file_object) -> list: #vers 1
    """Safely get selected entries from main window"""
    try:
        # Try different methods to get selected entries
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
        
        # Method 3: If no selection, return empty list
        return []
        
    except Exception:
        return []


def _create_remove_progress_dialog(main_window, total_entries) -> QProgressDialog: #vers 1
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
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        return progress_dialog
        
    except Exception:
        # Fallback: create minimal progress dialog
        progress_dialog = QProgressDialog(main_window)
        progress_dialog.setRange(0, total_entries)
        return progress_dialog


def _convert_img_to_archive(file_object, main_window) -> Optional[object]: #vers 1
    """Convert IMG file object to IMG_Editor IMGArchive format"""
    try:
        from IMG_Editor.core.Core import IMGArchive, IMGEntry
        
        # If already IMG_Editor format, return as-is
        if isinstance(file_object, IMGArchive):
            return file_object
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Converting IMG to IMG_Editor archive format for removal")
        
        # Load IMG file using IMG_Editor
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No valid file path found")
            return None
        
        # Create and load IMG_Editor archive
        archive = IMGArchive()
        if not archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to load IMG file with IMG_Editor")
            return None
        
        if hasattr(main_window, 'log_message'):
            entry_count = len(archive.entries) if archive.entries else 0
            main_window.log_message(f"✅ Loaded IMG with {entry_count} entries for removal")
        
        return archive
        
    except ImportError:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ IMG_Editor core not available")
        return None

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Archive conversion error: {str(e)}")
        return None


def integrate_remove_functions(main_window) -> bool: #vers 1
    """Integrate IMG_Editor core remove functions - NEW"""
    try:
        # Main remove functions with IMG_Editor core
        main_window.remove_selected_function = lambda: remove_selected_function(main_window)
        main_window.remove_entries_by_name = lambda entry_names: remove_entries_by_name(main_window, entry_names)
        main_window.remove_multiple_entries = lambda entries: remove_multiple_entries(main_window, entries)
        
        # Add aliases that GUI might use
        main_window.remove_selected = main_window.remove_selected_function
        main_window.remove_selected_entries = main_window.remove_selected_function
        main_window.delete_selected = main_window.remove_selected_function
        main_window.remove_entries = main_window.remove_multiple_entries
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG_Editor core remove functions integrated with TAB AWARENESS")
            main_window.log_message("   • Uses IMG archive entry manipulation for reliable removal")
            main_window.log_message("   • Supports selected entries, by name, and multiple entry removal")
            main_window.log_message("   • Remember to rebuild IMG after removal to save changes")
        
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
        
