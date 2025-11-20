#this belongs in core/impotr.py - Version: 10
# X-Seti - November16 2025 - IMG Factory 1.5 - Consolidated Import Functions

"""
Import Functions - Single unified import system
Tab-aware - gets file from active tab, not main_window globals
"""

import os
from typing import List
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from apps.methods.tab_system import get_current_file_from_active_tab
from apps.methods.img_import_functions import add_file_to_img, add_multiple_files_to_img, refresh_after_import, ask_user_about_saving

##Methods list -
# import_files_function
# import_files_with_list
# import_folder_contents
# integrate_import_functions

def import_files_function(main_window) -> bool: #vers 10
    """Import multiple files via file dialog - TAB AWARE VERSION"""
    try:
        # Get file object from active tab (NOT from main_window.file_object)
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        # Validate
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

        # Use shared import function
        imported_count = add_multiple_files_to_img(file_object, file_paths, main_window)

        if imported_count > 0:
            # Refresh and notify
            refresh_after_import(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported {imported_count} file(s) successfully")
                main_window.log_message("IMG marked as modified - use Save Entry to save changes")

            # Ask about saving
            ask_user_about_saving(main_window)
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Import failed: No files were imported")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Failed to import files:\n{str(e)}")
        return False


def import_files_with_list(main_window, file_paths: List[str]) -> bool: #vers 6
    """Import files from provided list - TAB AWARE VERSION"""
    try:
        if not file_paths:
            return False

        # Get file object from active tab
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False

        # Use shared import function
        imported_count = add_multiple_files_to_img(file_object, file_paths, main_window)

        if imported_count > 0:
            refresh_after_import(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported {imported_count}/{len(file_paths)} file(s)")
            
            ask_user_about_saving(main_window)
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("No files were imported")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import error: {str(e)}")
        return False


def import_folder_contents(main_window) -> bool: #vers 5
    """Import all files from a folder - TAB AWARE VERSION"""
    try:
        # Get file object from active tab
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False

        # Folder selection dialog
        folder_path = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if not folder_path:
            return False

        # Get all files in folder
        file_paths = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

        if not file_paths:
            QMessageBox.information(main_window, "Empty Folder", "No files found in selected folder")
            return False

        # Import files
        imported_count = add_multiple_files_to_img(file_object, file_paths, main_window)

        if imported_count > 0:
            refresh_after_import(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported {imported_count}/{len(file_paths)} file(s) from folder")
            
            ask_user_about_saving(main_window)
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("No files were imported from folder")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Folder import error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Failed to import folder:\n{str(e)}")
        return False


def integrate_import_functions(main_window) -> bool: #vers 10
    """Integrate import functions with main window - SINGLE INTEGRATION POINT"""
    try:
        # Add import methods to main window
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
        main_window.import_folder_contents = lambda: import_folder_contents(main_window)

        # Add aliases that GUI might use
        main_window.import_files = main_window.import_files_function
        main_window.import_via_dialog = main_window.import_files_function
        main_window.import_folder = main_window.import_folder_contents

        if hasattr(main_window, 'log_message'):
            main_window.log_message("Import functions integrated")
            main_window.log_message("   Tab-aware file import")
            main_window.log_message("   Batch import support")
            main_window.log_message("   Folder import support")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'import_files_function',
    'import_files_with_list',
    'import_folder_contents',
    'integrate_import_functions'
]
