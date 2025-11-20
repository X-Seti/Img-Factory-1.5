#this belongs in core/impotr.py - Version: 14
# X-Seti - November19 2025 - IMG Factory 1.5 - Consolidated Import Functions
"""
Import Functions - Single unified import system
Tab-aware - gets file from active tab, not main_window globals
"""

import os
from typing import List
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QCheckBox, QVBoxLayout, QWidget
from apps.methods.tab_system import get_current_file_from_active_tab
from apps.methods.img_import_functions import add_file_to_img, add_multiple_files_to_img, refresh_after_import
# Import setting for save preference
from apps.utils.app_settings_system import AppSettings

##Methods list -
# import_files_function
# import_files_with_list
# import_folder_contents
# integrate_import_functions
# _ask_user_about_saving_once

def import_files_function(main_window) -> bool: #vers 11
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

        # Use shared import function - NO auto-save
        success_list, failed_list = add_multiple_files_to_img(file_object, file_paths, main_window)
        imported_count = len(success_list)
        if imported_count > 0:
            # ✅ Mark entries as new for highlighting
            for entry in file_object.entries:
                if not hasattr(entry, 'is_new_entry'):
                    for fp in file_paths:
                        if os.path.basename(fp) == entry.name:
                            entry.is_new_entry = True
                            break
            # Refresh and notify
            refresh_after_import(main_window)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported {imported_count} file(s) successfully")
                main_window.log_message("IMG marked as modified - use Save Entry to save changes")
            # ✅ Ask about saving - only once per session unless user resets
            _ask_user_about_saving_once(main_window)
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

def import_files_with_list(main_window, file_paths: List[str]) -> bool: #vers 7
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
        success_list, failed_list = add_multiple_files_to_img(file_object, file_paths, main_window)
        imported_count = len(success_list)
        if imported_count > 0:
            # ✅ Mark entries as new for highlighting
            for entry in file_object.entries:
                if not hasattr(entry, 'is_new_entry'):
                    for fp in file_paths:
                        if os.path.basename(fp) == entry.name:
                            entry.is_new_entry = True
                            break
            refresh_after_import(main_window)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported {imported_count}/{len(file_paths)} file(s)")
            _ask_user_about_saving_once(main_window)
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("No files were imported")
            return False
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import error: {str(e)}")
        return False

def import_folder_contents(main_window) -> bool: #vers 6
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
        success_list, failed_list = add_multiple_files_to_img(file_object, file_paths, main_window)
        imported_count = len(success_list)
        if imported_count > 0:
            # ✅ Mark entries as new
            for entry in file_object.entries:
                if not hasattr(entry, 'is_new_entry'):
                    for fp in file_paths:
                        if os.path.basename(fp) == entry.name:
                            entry.is_new_entry = True
                            break
            refresh_after_import(main_window)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported {imported_count}/{len(file_paths)} file(s) from folder")
            _ask_user_about_saving_once(main_window)
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

def _ask_user_about_saving_once(main_window) -> None: #vers 2
    """Ask user if they want to save after import, with 'Don't ask again' option"""
    try:
        # Check if user has disabled prompts
        should_ask = getattr(main_window.settings, 'current_settings', {}).get('ask_save_after_import', True)
        if not should_ask:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Auto-save prompt disabled. Save manually with 'Save Entry'.")
            return

        # Create custom dialog with checkbox
        dialog = QMessageBox(main_window)
        dialog.setWindowTitle("Import Complete")
        dialog.setText("Files have been imported successfully.")
        dialog.setInformativeText("Do you want to save the IMG file now?\n(You can also use 'Save Entry' later)")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.Yes)

        # Add "Don't ask again" checkbox
        checkbox = QCheckBox("Don't ask me again")
        checkbox.setChecked(False)

        # Insert checkbox into dialog layout
        layout = dialog.layout()
        if layout:
            # Find the button box and insert above it
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget():
                    widget = item.widget()
                    if "buttonbox" in widget.objectName().lower():
                        # Create a container for the checkbox
                        checkbox_container = QWidget()
                        checkbox_layout = QVBoxLayout(checkbox_container)
                        checkbox_layout.addWidget(checkbox)
                        layout.insertWidget(i, checkbox_container)
                        break

        reply = dialog.exec()

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(main_window, 'save_entry'):
                main_window.save_entry()
            elif hasattr(main_window, 'save_img_entry'):
                main_window.save_img_entry()

        # Handle checkbox state
        if checkbox.isChecked():
            # Update setting
            if hasattr(main_window, 'settings'):
                main_window.settings.current_settings['ask_save_after_import'] = False
                main_window.settings.save_settings()
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("Save prompt disabled. Use 'Save Entry' to save manually.")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Warning: Save dialog failed: {str(e)}")

def integrate_import_functions(main_window) -> bool: #vers 11
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
            main_window.log_message("   ✅ No auto-save crashes")
            main_window.log_message("   ✅ Save prompt with 'Don't ask again' option")
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
