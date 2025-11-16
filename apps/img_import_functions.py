#this belongs in methods/img_import_functions.py - Version: 1
# X-Seti - November16 2025 - IMG Factory 1.5 - Shared Import Functions

"""
Shared Import Functions - Core import operations used by all import features
Handles actual file addition to IMG archives with proper error handling
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox

##Methods list -
# add_file_to_img
# add_multiple_files_to_img
# refresh_after_import
# ask_user_about_saving

def add_file_to_img(file_object, file_path: str, main_window=None) -> bool: #vers 1
    """
    Add single file to IMG archive - CORE FUNCTION
    Works with both old and new IMG file objects
    """
    try:
        if not os.path.exists(file_path):
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ File not found: {file_path}")
            return False

        filename = os.path.basename(file_path)
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Try multiple methods to add entry
        success = False

        # Method 1: Direct add_entry method
        if hasattr(file_object, 'add_entry') and callable(file_object.add_entry):
            try:
                success = file_object.add_entry(filename, file_data)
                if success:
                    # Mark entry as new
                    if hasattr(file_object, 'entries') and file_object.entries:
                        for entry in reversed(file_object.entries):
                            if hasattr(entry, 'name') and entry.name == filename:
                                entry.is_new_entry = True
                                entry.modified = True
                                break
            except Exception as e:
                if main_window and hasattr(main_window, 'log_message'):
                    main_window.log_message(f"add_entry failed: {str(e)}")
                success = False

        # Method 2: Use img_entry_operations.add_entry_safe
        if not success:
            try:
                from apps.methods.img_entry_operations import add_entry_safe
                success = add_entry_safe(file_object, filename, file_data)
            except ImportError:
                pass

        # Mark file as modified
        if success and hasattr(file_object, 'modified'):
            file_object.modified = True

        return success

    except Exception as e:
        if main_window and hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error adding file: {str(e)}")
        return False


def add_multiple_files_to_img(file_object, file_paths: List[str], main_window=None) -> int: #vers 1
    """
    Add multiple files to IMG archive - CORE BATCH FUNCTION
    Returns count of successfully imported files
    """
    imported_count = 0
    failed_count = 0

    for file_path in file_paths:
        if add_file_to_img(file_object, file_path, main_window):
            imported_count += 1
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Imported: {os.path.basename(file_path)}")
        else:
            failed_count += 1
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Failed: {os.path.basename(file_path)}")

    return imported_count


def refresh_after_import(main_window) -> None: #vers 1
    """Refresh UI after import operation"""
    try:
        # Try multiple refresh methods
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        elif hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        elif hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Warning: Refresh failed: {str(e)}")


def ask_user_about_saving(main_window) -> None: #vers 1
    """Ask user if they want to save after import"""
    try:
        reply = QMessageBox.question(
            main_window,
            "Import Complete",
            "Files have been imported successfully.\n\n"
            "Do you want to save the IMG file now?\n"
            "(You can also use 'Save Entry' later)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Try to save using save entry function
            if hasattr(main_window, 'save_entry'):
                main_window.save_entry()
            elif hasattr(main_window, 'save_img_entry'):
                main_window.save_img_entry()

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Warning: Save dialog failed: {str(e)}")


# Export functions
__all__ = [
    'add_file_to_img',
    'add_multiple_files_to_img',
    'refresh_after_import',
    'ask_user_about_saving'
]
