#this belongs in core/remove_via.py - Version: 7
# X-Seti - September09 2025 - IMG Factory 1.5 - Remove Via Functions with Proper Modification Tracking

"""
Remove Via Functions - Remove entries via IDE/text files with proper modification tracking
"""

import os
from typing import List
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from apps.methods.file_validation import validate_img_file, validate_any_file, get_selected_entries_for_operation
from apps.methods.imgcol_exists import set_context

##Methods list -
# _parse_ide_file_for_removal
# _parse_text_file_list
# _refresh_after_removal_via
# _remove_entries_via_with_tracking
# integrate_remove_via_functions
# remove_via_function
# remove_via_ide_function
# remove_via_text_function

def remove_via_function(main_window, file_object, file_type): #vers 1
    """Remove entries via file selection dialog"""
    
    set_context(main_window)
    # File selection dialog - remove via should work with both img and col files.

    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        main_window,
        "Select file for removal list",
        "",
        "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
    )
    
    if not file_path:
        return False
    
    if file_path.lower().endswith('.ide'):
        return remove_via_ide_function_with_path(main_window, file_path)
    else:
        return remove_via_text_function_with_path(main_window, file_path)

def remove_via_ide_function(main_window): #vers 1
    """Remove entries using IDE file selection"""
    
    file_dialog = QFileDialog()
    ide_path, _ = file_dialog.getOpenFileName(
        main_window,
        "Select IDE file for removal",
        "",
        "IDE Files (*.ide);;All Files (*)"
    )
    
    if not ide_path:
        return False
    
    return remove_via_ide_function_with_path(main_window, ide_path)

def remove_via_ide_function_with_path(main_window, ide_path: str): #vers 1
    """Remove entries using specific IDE file path with proper modification tracking"""
    
    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    if not os.path.exists(ide_path):
        QMessageBox.warning(main_window, "File Not Found", f"IDE file not found: {ide_path}")
        return False
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Removing entries via IDE: {os.path.basename(ide_path)}")
    
    # Parse IDE file for entry names
    entry_names_to_remove = _parse_ide_file_for_removal(ide_path)
    
    if not entry_names_to_remove:
        QMessageBox.information(main_window, "No Entries", "No valid entries found in IDE file for removal")
        return False
    
    # Find matching entries
    entries_to_remove = []
    for entry_name in entry_names_to_remove:
        for entry in file_object.entries:
            if hasattr(entry, 'name') and entry.name.lower() == entry_name.lower():
                entries_to_remove.append(entry)
                break
    
    if not entries_to_remove:
        QMessageBox.information(main_window, "No Matches", "No matching entries found in IMG file")
        return False
    
    # Confirm removal
    reply = QMessageBox.question(
        main_window,
        "Confirm IDE Removal",
        f"Remove {len(entries_to_remove)} entries found in IDE file?\n\n"
        f"Use 'Save Entry' afterwards to save changes to disk.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    
    if reply != QMessageBox.StandardButton.Yes:
        return False
    
    # Remove entries with proper tracking
    success = _remove_entries_via_with_tracking(file_object, entries_to_remove, main_window)
    
    if success:
        _refresh_after_removal_via(main_window)
        
        QMessageBox.information(
            main_window,
            "Remove Via IDE Complete",
            f"Successfully removed {len(entries_to_remove)} entries via IDE file.\n\n"
            f"Use 'Save Entry' to save changes to disk."
        )
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Removed {len(entries_to_remove)} entries via IDE - use Save Entry to save changes")
    
    return success

def remove_via_text_function(main_window): #vers 1
    """Remove entries using text file selection"""
    
    file_dialog = QFileDialog()
    text_path, _ = file_dialog.getOpenFileName(
        main_window,
        "Select text file for removal",
        "",
        "Text Files (*.txt);;All Files (*)"
    )
    
    if not text_path:
        return False
    
    return remove_via_text_function_with_path(main_window, text_path)

def remove_via_text_function_with_path(main_window, text_path: str): #vers 1
    """Remove entries using specific text file path with proper modification tracking"""
    
    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    if not os.path.exists(text_path):
        QMessageBox.warning(main_window, "File Not Found", f"Text file not found: {text_path}")
        return False
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Removing entries via text: {os.path.basename(text_path)}")
    
    # Parse text file for entry names
    entry_names_to_remove = _parse_text_file_list(text_path)
    
    if not entry_names_to_remove:
        QMessageBox.information(main_window, "No Entries", "No valid entries found in text file for removal")
        return False
    
    # Find matching entries
    entries_to_remove = []
    for entry_name in entry_names_to_remove:
        for entry in file_object.entries:
            if hasattr(entry, 'name') and entry.name.lower() == entry_name.lower():
                entries_to_remove.append(entry)
                break
    
    if not entries_to_remove:
        QMessageBox.information(main_window, "No Matches", "No matching entries found in IMG file")
        return False
    
    # Confirm removal
    reply = QMessageBox.question(
        main_window,
        "Confirm Text Removal",
        f"Remove {len(entries_to_remove)} entries found in text file?\n\n"
        f"Use 'Save Entry' afterwards to save changes to disk.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    
    if reply != QMessageBox.StandardButton.Yes:
        return False
    
    # Remove entries with proper tracking
    success = _remove_entries_via_with_tracking(file_object, entries_to_remove, main_window)
    
    if success:
        _refresh_after_removal_via(main_window)
        
        QMessageBox.information(
            main_window,
            "Remove Via Text Complete",
            f"Successfully removed {len(entries_to_remove)} entries via text file.\n\n"
            f"Use 'Save Entry' to save changes to disk."
        )
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Removed {len(entries_to_remove)} entries via text - use Save Entry to save changes")
    
    return success

def _remove_entries_via_with_tracking(file_object, entries_to_remove: List, main_window) -> bool: #vers 1
    """Remove entries via with proper modification tracking - FIXES SAVE ENTRY DETECTION"""
    if not hasattr(file_object, 'entries'):
        return False
    
    # Initialize deleted_entries tracking if not exists
    if not hasattr(file_object, 'deleted_entries'):
        file_object.deleted_entries = []
    
    removed_count = 0
    
    for entry in entries_to_remove:
        if entry in file_object.entries:
            # Remove from current entries list
            file_object.entries.remove(entry)
            
            # CRITICAL: Track the deletion for Save Entry detection
            file_object.deleted_entries.append(entry)
            
            removed_count += 1
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Removed via: {entry.name}")
    
    # Mark file as modified
    if removed_count > 0:
        file_object.modified = True
    
    return removed_count > 0

def _parse_ide_file_for_removal(ide_path: str) -> List[str]: #vers 1
    """Parse IDE file to extract model and texture names for removal"""
    entry_names = []
    
    with open(ide_path, 'r', encoding='utf-8', errors='ignore') as f:
        current_section = None
        
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            
            # Check for section headers
            if line.lower() == 'objs':
                current_section = 'objs'
                continue
            elif line.lower() == 'tobj':
                current_section = 'tobj'
                continue
            elif line.lower() == 'end':
                current_section = None
                continue
            
            # Parse entries in objs and tobj sections
            if current_section in ['objs', 'tobj']:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 3:  # Need at least ID, ModelName, TextureName
                    model_name = parts[1].strip()
                    texture_name = parts[2].strip()
                    
                    # Add model name (.dff)
                    if model_name and not model_name.isdigit() and model_name != '-1':
                        if not model_name.lower().endswith('.dff'):
                            model_name += '.dff'
                        entry_names.append(model_name)
                    
                    # Add texture name (.txd)
                    if texture_name and not texture_name.isdigit() and texture_name != '-1':
                        if not texture_name.lower().endswith('.txd'):
                            texture_name += '.txd'
                        entry_names.append(texture_name)
    
    return list(set(entry_names))  # Remove duplicates

def _parse_text_file_list(text_path: str) -> List[str]: #vers 1
    """Parse text file for list of filenames"""
    file_list = []
    
    with open(text_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                # Smart parsing - extract filename if it's a path
                if '/' in line or '\\' in line:
                    filename = os.path.basename(line)
                else:
                    filename = line
                
                # Validate filename
                if filename and '.' in filename:
                    file_list.append(filename)
    
    return file_list

def _refresh_after_removal_via(main_window): #vers 1
    """Refresh UI after removal via"""
    # Refresh main table
    if hasattr(main_window, 'refresh_table'):
        main_window.refresh_table()
    
    # Refresh file list window
    if hasattr(main_window, 'refresh_file_list'):
        main_window.refresh_file_list()
    
    # Update GUI layout
    if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'refresh_file_list'):
        main_window.gui_layout.refresh_file_list()
    
    # Update UI for current IMG
    if hasattr(main_window, '_update_ui_for_loaded_img'):
        main_window._update_ui_for_loaded_img()
    
    # Update current tab data
    if hasattr(main_window, 'refresh_current_tab_data'):
        main_window.refresh_current_tab_data()
    
    # Clear any stale highlights (removed files should not be highlighted)
    if hasattr(main_window, '_import_highlight_manager'):
        if hasattr(main_window, 'refresh_table_with_highlights'):
            main_window.refresh_table_with_highlights()
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message("UI refreshed after removal via")

def integrate_remove_via_functions(main_window) -> bool: #vers 3
    """Integrate remove via functions with proper modification tracking"""
    global file_object, file_type
    file_object = getattr(main_window, 'file_object', None)
    file_type = getattr(main_window, 'file_type', None)

    # Add remove via methods to main window
    main_window.remove_via_function = lambda: remove_via_function(main_window)
    main_window.remove_via_ide_function = lambda: remove_via_ide_function(main_window)
    main_window.remove_via_text_function = lambda: remove_via_text_function(main_window)
    
    # Add aliases that GUI might use
    main_window.remove_via = main_window.remove_via_function
    main_window.remove_via_ide = main_window.remove_via_ide_function
    main_window.remove_via_text = main_window.remove_via_text_function
    main_window.remove_via_entries = main_window.remove_via_function
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message("Remove via functions integrated with proper modification tracking")
        main_window.log_message("   • Tracks deleted entries for Save Entry detection")
        main_window.log_message("   • Supports IDE and text file removal lists")
        main_window.log_message("   • Sets modified flag properly")
    
    return True

# Export functions
__all__ = [
    'remove_via_function',
    'remove_via_ide_function',
    'remove_via_text_function',
    'integrate_remove_via_functions'
]
