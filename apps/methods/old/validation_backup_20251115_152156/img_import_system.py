#this belongs in core/impotr.py - Version: 18
# X-Seti - September11 2025 - IMG Factory 1.5 - Import Functions - DEBUG VERSION

"""
Import Functions - DEBUG version to identify failure points
"""

import os
from typing import List, Optional
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox

##Methods list -
# _debug_log
# _add_file_to_img_direct
# _refresh_after_import
# _ask_user_about_saving
# import_files_function
# import_files_with_list
# import_folder_contents
# import_multiple_files_core
# integrate_import_functions

def _debug_log(main_window, message): #vers 1
    """Debug logging helper"""
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"[DEBUG] {message}")
    print(f"[DEBUG] {message}")

def _add_file_to_img_direct(file_object, file_path: str, main_window) -> bool: #vers 1
    """Add file directly to IMG with debug logging"""
    try:
        _debug_log(main_window, f"Starting direct file add: {file_path}")
        
        if not os.path.exists(file_path):
            _debug_log(main_window, f"File does not exist: {file_path}")
            return False
        
        filename = os.path.basename(file_path)
        _debug_log(main_window, f"Filename: {filename}")
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        _debug_log(main_window, f"Read {len(file_data)} bytes from file")
        
        # Check if file_object has add_entry method
        if hasattr(file_object, 'add_entry') and callable(file_object.add_entry):
            _debug_log(main_window, "Using file_object.add_entry method")
            success = file_object.add_entry(filename, file_data)
            _debug_log(main_window, f"add_entry returned: {success}")
            
            if success:
                # Find the added entry and mark it as new
                if hasattr(file_object, 'entries'):
                    _debug_log(main_window, f"Total entries after add: {len(file_object.entries)}")
                    for entry in reversed(file_object.entries):  # Check recent entries first
                        if hasattr(entry, 'name') and entry.name == filename:
                            _debug_log(main_window, f"Found added entry: {entry.name}")
                            # Mark as new entry for Save Entry detection
                            entry.is_new_entry = True
                            entry.modified = True
                            _debug_log(main_window, "Marked entry as new/modified")
                            break
                
                # Mark file as modified
                file_object.modified = True
                _debug_log(main_window, "Marked IMG as modified")
                return True
            else:
                _debug_log(main_window, "add_entry method failed")
                return False
        else:
            _debug_log(main_window, "file_object does not have add_entry method")
            
            # Try using entry operations from methods
            try:
                from apps.methods.img_entry_operations import add_entry_safe
                _debug_log(main_window, "Using add_entry_safe from apps.methods.)
                success = add_entry_safe(file_object, filename, file_data)
                _debug_log(main_window, f"add_entry_safe returned: {success}")
                
                if success:
                    file_object.modified = True
                    _debug_log(main_window, "Marked IMG as modified via add_entry_safe")
                
                return success
                
            except ImportError as e:
                _debug_log(main_window, f"Cannot import add_entry_safe: {e}")
                return False

    except Exception as e:
        _debug_log(main_window, f"Exception in _add_file_to_img_direct: {str(e)}")
        return False

def import_files_function(main_window): #vers 4
    """Import multiple files via file dialog - DEBUG VERSION"""
    _debug_log(main_window, "Starting import_files_function")
    
    if not validate_tab_before_operation(main_window, "Import Files"):
        _debug_log(main_window, "Tab validation failed")
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)
    _debug_log(main_window, f"Got file_object: {file_object}, file_type: {file_type}")

    if file_type != 'IMG' or not file_object:
        _debug_log(main_window, "No IMG file or wrong file type")
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

    # File selection dialog
    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(
        main_window,
        "Select files to import",
        "",
        "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col);;Audio (*.wav)"
    )

    if not file_paths:
        _debug_log(main_window, "No files selected")
        return False

    _debug_log(main_window, f"Selected {len(file_paths)} files: {file_paths}")

    # Import files using direct method
    imported_count = 0
    failed_count = 0

    for file_path in file_paths:
        _debug_log(main_window, f"Processing file: {file_path}")
        
        if _add_file_to_img_direct(file_object, file_path, main_window):
            imported_count += 1
            _debug_log(main_window, f"Successfully imported: {os.path.basename(file_path)}")
        else:
            failed_count += 1
            _debug_log(main_window, f"Failed to import: {os.path.basename(file_path)}")

    _debug_log(main_window, f"Import summary: {imported_count} success, {failed_count} failed")

    if imported_count > 0:
        # Refresh after import
        _refresh_after_import(main_window)

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import complete: {imported_count} imported, {failed_count} failed")
            main_window.log_message("IMG marked as modified - use Save Entry to save changes")

        # Ask user about saving
        _ask_user_about_saving(main_window)
        
        return True
    else:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import failed: No files were imported successfully")
        return False

def import_files_with_list(main_window, file_paths: List[str]) -> bool: #vers 3
    """Import files from provided list - DEBUG VERSION"""
    _debug_log(main_window, f"Starting import_files_with_list with {len(file_paths)} files")
    
    if not validate_tab_before_operation(main_window, "Import Files List"):
        _debug_log(main_window, "Tab validation failed")
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)
    _debug_log(main_window, f"Got file_object: {file_object}, file_type: {file_type}")

    if file_type != 'IMG' or not file_object:
        _debug_log(main_window, "No IMG file or wrong file type")
        return False

    if not file_paths:
        _debug_log(main_window, "No files provided")
        return False

    # Import files using direct method
    imported_count = 0
    failed_count = 0

    for file_path in file_paths:
        _debug_log(main_window, f"Processing file: {file_path}")
        
        if _add_file_to_img_direct(file_object, file_path, main_window):
            imported_count += 1
            _debug_log(main_window, f"Successfully imported: {os.path.basename(file_path)}")
        else:
            failed_count += 1
            _debug_log(main_window, f"Failed to import: {os.path.basename(file_path)}")

    _debug_log(main_window, f"Import summary: {imported_count} success, {failed_count} failed")

    if imported_count > 0:
        # Refresh after import
        _refresh_after_import(main_window)

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import complete: {imported_count} imported, {failed_count} failed")
            main_window.log_message("IMG marked as modified - use Save Entry to save changes")

        # Ask user about saving
        _ask_user_about_saving(main_window)
        
        return True
    else:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import failed: No files were imported successfully")
        return False

def import_multiple_files_core(main_window, file_paths: List[str]) -> bool: #vers 4
    """Import multiple files with proper modification tracking - DEBUG VERSION"""
    return import_files_with_list(main_window, file_paths)

def import_folder_contents(main_window) -> bool: #vers 4
    """Import all files from a folder - DEBUG VERSION"""
    _debug_log(main_window, "Starting import_folder_contents")
    
    if not validate_tab_before_operation(main_window, "Import Folder"):
        _debug_log(main_window, "Tab validation failed")
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)

    if file_type != 'IMG' or not file_object:
        _debug_log(main_window, "No IMG file or wrong file type")
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

    # Folder selection dialog
    folder_path = QFileDialog.getExistingDirectory(
        main_window,
        "Select folder to import"
    )

    if not folder_path:
        _debug_log(main_window, "No folder selected")
        return False

    _debug_log(main_window, f"Selected folder: {folder_path}")

    # Get all files from folder
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    _debug_log(main_window, f"Found {len(file_paths)} files in folder")

    if not file_paths:
        QMessageBox.information(main_window, "Empty Folder", "No files found in selected folder")
        return False

    return import_files_with_list(main_window, file_paths)

def _ask_user_about_saving(main_window): #vers 4
    """Ask user about saving with better messaging"""
    try:
        reply = QMessageBox.question(
            main_window,
            "Save Changes?",
            "Files have been imported successfully.\n\n"
            "Do you want to save the IMG file now?\n"
            "(You can also use 'Save Entry' later)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Try to save using save entry function
            if hasattr(main_window, 'save_entry'):
                _debug_log(main_window, "Calling main_window.save_entry()")
                main_window.save_entry()
            elif hasattr(main_window, 'save_img_entry'):
                _debug_log(main_window, "Calling main_window.save_img_entry()")
                main_window.save_img_entry()
            else:
                _debug_log(main_window, "No save function available")
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("Save Entry function not available - use menu")

    except Exception as e:
        _debug_log(main_window, f"Save dialog error: {str(e)}")

def _refresh_after_import(main_window): #vers 4
    """Refresh UI after import with comprehensive updates"""
    _debug_log(main_window, "Starting UI refresh")
    
    # Refresh main table
    if hasattr(main_window, 'refresh_table'):
        _debug_log(main_window, "Calling refresh_table")
        main_window.refresh_table()
    
    # Refresh file list window
    if hasattr(main_window, 'refresh_file_list'):
        _debug_log(main_window, "Calling refresh_file_list")
        main_window.refresh_file_list()
    
    # Update GUI layout
    if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'refresh_file_list'):
        _debug_log(main_window, "Calling gui_layout.refresh_file_list")
        main_window.gui_layout.refresh_file_list()
    
    # Update UI for current IMG
    if hasattr(main_window, '_update_ui_for_loaded_img'):
        _debug_log(main_window, "Calling _update_ui_for_loaded_img")
        main_window._update_ui_for_loaded_img()
    
    # Update current tab data
    if hasattr(main_window, 'refresh_current_tab_data'):
        _debug_log(main_window, "Calling refresh_current_tab_data")
        main_window.refresh_current_tab_data()
    
    # Update highlights for new entries
    if hasattr(main_window, 'refresh_table_with_highlights'):
        _debug_log(main_window, "Calling refresh_table_with_highlights")
        main_window.refresh_table_with_highlights()
    
    _debug_log(main_window, "UI refresh completed")

def integrate_import_functions(main_window) -> bool: #vers 4
    """Integrate import functions with main window - DEBUG VERSION"""
    _debug_log(main_window, "Starting integration of import functions")
    
    # Add import methods to main window
    main_window.import_files_function = lambda: import_files_function(main_window)
    main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
    main_window.import_multiple_files = lambda file_paths: import_multiple_files_core(main_window, file_paths)
    main_window.import_folder_contents = lambda: import_folder_contents(main_window)

    # Add aliases that GUI might use
    main_window.import_files = main_window.import_files_function
    main_window.import_via_dialog = main_window.import_files_function
    main_window.import_folder = main_window.import_folder_contents

    _debug_log(main_window, "Import functions integrated")

    if hasattr(main_window, 'log_message'):
        main_window.log_message("Import functions integrated - DEBUG VERSION")
        main_window.log_message("   • Direct file addition with debug logging")
        main_window.log_message("   • Comprehensive error tracking")
        main_window.log_message("   • Step-by-step import process logging")

    return True

# Export functions
__all__ = [
    'import_files_function',
    'import_files_with_list',
    'import_multiple_files_core',
    'import_folder_contents',
    'integrate_import_functions'
]
