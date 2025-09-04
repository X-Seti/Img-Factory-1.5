#this belongs in core/ impotr.py - Version: 13
# X-Seti - September04 2025 - IMG Factory 1.5 - Clean Import Functions

import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# import_files_function
# import_multiple_files
# import_folder_contents
# _import_files_to_img
# _get_files_from_folder
# _ask_rebuild_after_import
# integrate_import_functions

def import_files_function(main_window): #vers 13
    """Import files via file dialog"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Import Files"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # File dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            "",
            "All Supported Files (*.dff *.txd *.col *.ipl *.ide *.dat *.cfg);;All Files (*.*)"
        )
        
        if not file_paths:
            return False
        
        # Import files
        success = _import_files_to_img(file_object, file_paths, main_window)
        
        if success:
            # Ask to rebuild
            _ask_rebuild_after_import(main_window, len(file_paths))
        
        return success
        
    except Exception as e:
        QMessageBox.critical(main_window, "Import Error", f"Import error: {str(e)}")
        return False


def import_multiple_files(main_window, file_paths: List[str]) -> bool: #vers 13
    """Import multiple files programmatically (for drag-drop)"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Import Multiple Files"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if not file_paths:
            return False
        
        # Import files
        success = _import_files_to_img(file_object, file_paths, main_window)
        
        if success:
            # Ask to rebuild
            _ask_rebuild_after_import(main_window, len(file_paths))
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import multiple error: {str(e)}")
        return False


def import_folder_contents(main_window): #vers 13
    """Import entire folder contents"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Import Folder"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Folder dialog
        folder_path = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            return False
        
        # Get files from folder
        file_paths = _get_files_from_folder(folder_path)
        
        if not file_paths:
            QMessageBox.information(main_window, "No Files", "No supported files found in folder")
            return False
        
        # Import files
        success = _import_files_to_img(file_object, file_paths, main_window)
        
        if success:
            # Ask to rebuild
            _ask_rebuild_after_import(main_window, len(file_paths))
        
        return success
        
    except Exception as e:
        QMessageBox.critical(main_window, "Import Error", f"Import folder error: {str(e)}")
        return False


def _import_files_to_img(file_object, file_paths: List[str], main_window) -> bool: #vers 13
    """Import files using existing add_entry method"""
    try:
        # Check if file object has add_entry method
        if not hasattr(file_object, 'add_entry'):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ File object has no add_entry method")
            return False
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Importing files...", "Cancel", 0, len(file_paths), main_window)
        progress_dialog.setWindowTitle("Importing Files")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setValue(0)
        progress_dialog.show()
        
        imported_count = 0
        failed_count = 0
        
        try:
            for i, file_path in enumerate(file_paths):
                # Update progress
                progress_dialog.setValue(i)
                file_name = os.path.basename(file_path)
                progress_dialog.setLabelText(f"Importing: {file_name}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    break
                
                try:
                    # Read file data
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Use existing add_entry method (auto_save=False for batch)
                    if hasattr(file_object, 'add_entry'):
                        success = file_object.add_entry(file_name, file_data, auto_save=False)
                    else:
                        success = file_object.add_entry(file_name, file_data)
                    
                    if success:
                        imported_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"✅ Imported: {file_name}")
                    else:
                        failed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Failed to import: {file_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Import error for {file_name}: {str(e)}")
        
        finally:
            progress_dialog.close()
        
        # Report results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Import complete: {imported_count} success, {failed_count} failed")
        
        return imported_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import files error: {str(e)}")
        return False


def _get_files_from_folder(folder_path: str) -> List[str]: #vers 13
    """Get supported files from folder"""
    try:
        supported_extensions = {'.dff', '.txd', '.col', '.ipl', '.ide', '.dat', '.cfg'}
        file_paths = []
        
        folder = Path(folder_path)
        
        for file_path in folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in supported_extensions:
                    file_paths.append(str(file_path))
        
        # Sort for consistent import order
        file_paths.sort()
        
        return file_paths
        
    except Exception:
        return []


def _ask_rebuild_after_import(main_window, imported_count: int): #vers 13
    """Ask user if they want to rebuild IMG after import"""
    try:
        reply = QMessageBox.question(
            main_window,
            "Import Complete",
            f"Successfully imported {imported_count} files to memory.\n\n"
            f"Do you want to rebuild the IMG file now to save changes to disk?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Trigger rebuild function
            if hasattr(main_window, 'rebuild_img_function'):
                main_window.rebuild_img_function()
            elif hasattr(main_window, 'rebuild_function'):
                main_window.rebuild_function()
            else:
                QMessageBox.information(main_window, "Rebuild", 
                    "Rebuild function not available. Use the Rebuild button to save changes.")
        else:
            QMessageBox.information(main_window, "Import Note",
                "Files imported to memory. Use 'Rebuild' or 'Save Entry' to save changes to disk.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Ask rebuild error: {str(e)}")


def integrate_import_functions(main_window) -> bool: #vers 13
    """Integrate clean import functions into main window"""
    try:
        # Add import methods to main window
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_multiple_files = lambda file_paths: import_multiple_files(main_window, file_paths)
        main_window.import_folder_contents = lambda: import_folder_contents(main_window)
        
        # Add aliases that GUI might use
        main_window.import_files = main_window.import_files_function
        main_window.import_via_dialog = main_window.import_files_function
        main_window.import_folder = main_window.import_folder_contents
        
        # Integrate save_entry function if available
        if SAVE_ENTRY_AVAILABLE:
            integrate_save_entry_function(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Clean import functions integrated")
            main_window.log_message("   • Uses existing add_entry method")
            main_window.log_message("   • Handles duplicate files (Replace/Rename/Cancel)")
            main_window.log_message("   • Supports drag-and-drop integration")
            main_window.log_message("   • Tells user to press 'Save Entry' button after import")
            if SAVE_ENTRY_AVAILABLE:
                main_window.log_message("   • Save Entry function integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'import_files_function',
    'import_multiple_files',
    'import_folder_contents',
    'integrate_import_functions'
]