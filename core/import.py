#this belongs in core/impotr.py - Version: 16
# X-Seti - September11 2025 - IMG Factory 1.5 - Import Functions - Fixed Argument Error & Save Issue

"""
Import Functions - FIXED: Function argument error and IMG save failure
"""

import os
from typing import List, Optional
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# _add_file_to_img_with_tracking
# _ask_user_about_saving
# _refresh_after_import
# import_files_function
# import_files_with_list
# import_folder_contents
# import_multiple_files
# integrate_import_functions

def import_files_function(main_window): #vers 2
    """Import multiple files via file dialog with proper modification tracking"""
    if not validate_tab_before_operation(main_window, "Import Files"):
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)

    if file_type != 'IMG' or not file_object:
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
        return False

    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Importing {len(file_paths)} files")

    # Import files with proper tracking
    success = import_multiple_files(main_window, file_paths)

    if success:
        # Ask user about saving
        _ask_user_about_saving(main_window)

    return success

def import_files_with_list(main_window, file_paths: List[str]) -> bool: #vers 1
    """Import files from provided list - NEW FUNCTION for import_via compatibility"""
    if not validate_tab_before_operation(main_window, "Import Files List"):
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)

    if file_type != 'IMG' or not file_object:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ No IMG file loaded")
        return False

    if not file_paths:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ No files provided")
        return False

    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Importing {len(file_paths)} files from list")

    # Import files with proper tracking
    success = import_multiple_files(main_window, file_paths)

    if success:
        # Ask user about saving
        _ask_user_about_saving(main_window)

    return success

def import_multiple_files(main_window, file_paths: List[str]) -> bool: #vers 2
    """Import multiple files with proper modification tracking - FIXED SAVE ISSUE"""
    if not validate_tab_before_operation(main_window, "Import Multiple Files"):
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)

    if file_type != 'IMG' or not file_object:
        return False

    if not file_paths:
        return False

    imported_count = 0
    failed_count = 0

    for file_path in file_paths:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)

            # Add file with proper tracking
            if _add_file_to_img_with_tracking(file_object, file_path, filename, main_window):
                imported_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Imported: {filename}")
            else:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to import: {filename}")
        else:
            failed_count += 1
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ File not found: {file_path}")

    if imported_count > 0:
        # CRITICAL: Mark IMG as modified for proper save detection
        file_object.modified = True
        
        # Refresh after import
        _refresh_after_import(main_window)

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Import complete: {imported_count} imported, {failed_count} failed")
            main_window.log_message(f"💾 IMG marked as modified - use Save Entry to save changes")

    return imported_count > 0

def import_folder_contents(main_window) -> bool: #vers 2
    """Import all files from a folder with proper modification tracking"""
    if not validate_tab_before_operation(main_window, "Import Folder"):
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)

    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

    # Folder selection dialog
    folder_path = QFileDialog.getExistingDirectory(
        main_window,
        "Select folder to import"
    )

    if not folder_path:
        return False

    # Get all files from folder
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    if not file_paths:
        QMessageBox.information(main_window, "Empty Folder", "No files found in selected folder")
        return False

    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Importing folder contents: {len(file_paths)} files")

    # Import files with proper tracking
    success = import_multiple_files(main_window, file_paths)

    if success:
        # Ask user about saving
        _ask_user_about_saving(main_window)

    return success

def _add_file_to_img_with_tracking(file_object, file_path: str, filename: str, main_window) -> bool: #vers 2
    """Add file to IMG with proper modification tracking - FIXES SAVE ENTRY DETECTION"""
    try:
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Use IMG file's add_entry method if available
        if hasattr(file_object, 'add_entry') and callable(file_object.add_entry):
            success = file_object.add_entry(filename, file_data)

            if success:
                # Find the added entry and mark it as new
                if hasattr(file_object, 'entries'):
                    for entry in reversed(file_object.entries):  # Check recent entries first
                        if hasattr(entry, 'name') and entry.name == filename:
                            # CRITICAL: Mark as new entry for Save Entry detection
                            entry.is_new_entry = True
                            entry.modified = True
                            break

                # CRITICAL: Mark file as modified for proper save detection
                file_object.modified = True

                return True

        # Fallback: Use methods from img_entry_operations
        try:
            from methods.img_entry_operations import add_entry_safe
            success = add_entry_safe(file_object, filename, file_data, auto_save=False)
            
            if success:
                # CRITICAL: Mark file as modified 
                file_object.modified = True
                
                # Mark new entry
                if hasattr(file_object, 'entries'):
                    for entry in reversed(file_object.entries):
                        if hasattr(entry, 'name') and entry.name == filename:
                            entry.is_new_entry = True
                            entry.modified = True
                            break
            
            return success

        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Cannot import entry operations for {filename}")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error adding {filename}: {str(e)}")
        return False

def _ask_user_about_saving(main_window): #vers 2
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
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("💾 Saving IMG file...")
                main_window.save_entry()
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("⚠️ Save Entry function not available - use menu")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Save dialog error: {str(e)}")

def _refresh_after_import(main_window): #vers 2
    """Refresh UI after import with comprehensive updates"""
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
    
    # Update highlights for new entries
    if hasattr(main_window, 'refresh_table_with_highlights'):
        main_window.refresh_table_with_highlights()
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message("🔄 UI refreshed after import")

def integrate_import_functions(main_window) -> bool: #vers 2
    """Integrate import functions with proper modification tracking - FIXED ARGUMENTS"""
    # Add import methods to main window
    main_window.import_files_function = lambda: import_files_function(main_window)
    main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
    main_window.import_multiple_files = lambda file_paths: import_multiple_files(main_window, file_paths)
    main_window.import_folder_contents = lambda: import_folder_contents(main_window)

    # Add aliases that GUI might use
    main_window.import_files = main_window.import_files_function
    main_window.import_via_dialog = main_window.import_files_function
    main_window.import_folder = main_window.import_folder_contents

    if hasattr(main_window, 'log_message'):
        main_window.log_message("✅ Import functions integrated - FIXED argument errors")
        main_window.log_message("   • Added import_files_with_list for import_via compatibility")
        main_window.log_message("   • Fixed save entry detection")
        main_window.log_message("   • Marks imported entries as new")
        main_window.log_message("   • Sets modified flag properly")

    return True

# Export functions
__all__ = [
    'import_files_function',
    'import_files_with_list',
    'import_multiple_files',
    'import_folder_contents',
    'integrate_import_functions'
]