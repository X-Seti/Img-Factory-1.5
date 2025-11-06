#this belongs in core/impotr.py - Version: 23
# X-Seti - September11 2025 - IMG Factory 1.5 - Import Functions - Clean Production Version

"""
Import Functions - Clean production version with reliable import and proper save detection
"""

import os
import math
import struct
from typing import List, Optional
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox

# Import existing RW detection systems
from core.rw_versions import parse_rw_version, get_rw_version_name, is_valid_rw_version

##Methods list -
# _add_file_to_img
# _create_img_entry
# _detect_rw_version_basic
# _refresh_after_import
# _ask_user_about_saving
# import_files_function
# import_files_with_list
# import_folder_contents
# import_multiple_files_core
# integrate_import_functions

# Constants
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 2
file_type = ""

def _detect_rw_version_basic(file_data: bytes, filename: str) -> tuple: #vers 1
    """Basic RW detection for common file types"""
    try:
        file_ext = filename.split('.')[-1].upper() if '.' in filename else "UNKNOWN"
        
        # Only analyze RW files
        if file_ext not in ['DFF', 'TXD']:
            return None, "Not RenderWare", (file_ext, "Non-RW")
        
        # Quick RW header check
        if len(file_data) < 12:
            return None, "Invalid", (file_ext, "Invalid")
        
        try:
            # Read RW version from header (bytes 8-12)
            version_bytes = file_data[8:12]
            version_value = struct.unpack('<I', version_bytes)[0]
            
            # Quick validation
            if is_valid_rw_version(version_value):
                version_name = get_rw_version_name(version_value)
                return version_value, version_name, (file_ext, version_name)
            else:
                return None, "Unknown", (file_ext, "Unknown")
                
        except Exception:
            return None, "Unknown", (file_ext, "Unknown")
            
    except Exception:
        file_ext = filename.split('.')[-1].upper() if '.' in filename else "UNKNOWN"
        return None, "Error", (file_ext, "Error")

def _create_img_entry(filename: str, file_data: bytes, file_object) -> object: #vers 1
    """Create IMG entry with basic file type detection"""
    try:
        # Try to import IMGEntry class
        try:
            from methods.img_core_classes import IMGEntry
        except ImportError:
            try:
                from components.img_core_classes import IMGEntry
            except ImportError:
                return None
        
        # Create new entry
        new_entry = IMGEntry()
        new_entry.name = filename
        new_entry.data = file_data
        new_entry.size = math.ceil(len(file_data) / SECTOR_SIZE)
        
        # Set version-specific fields
        version = getattr(file_object, 'version', 'V2')
        if version == 'V2':
            new_entry.streaming_size = new_entry.size
        else:
            new_entry.streaming_size = 0
        
        # Calculate offset (will be recalculated during save/rebuild)
        if hasattr(file_object, 'entries') and file_object.entries:
            last_entry = file_object.entries[-1]
            new_entry.offset = last_entry.offset + last_entry.size
        else:
            new_entry.offset = 1 if version == 'V2' else 0
        
        # Mark as new entry
        new_entry.is_new_entry = True
        new_entry.modified = True
        
        # Basic RW detection
        rw_version, rw_version_name, format_info = _detect_rw_version_basic(file_data, filename)
        
        # Set RW data
        new_entry._rw_version = rw_version
        new_entry._rw_version_name = rw_version_name
        new_entry._format_info = format_info
        
        # Set file type property
        if '.' in filename:
            new_entry.type = filename.split('.')[-1].upper()
        else:
            new_entry.type = "UNKNOWN"
        
        return new_entry
        
    except Exception:
        return None

def _add_file_to_img(file_object, file_path: str) -> bool: #vers 1
    """Add file to IMG with proper modification tracking"""
    try:
        if not os.path.exists(file_path):
            return False
        
        filename = os.path.basename(file_path)
        
        # Validate filename length
        if len(filename.encode('ascii', errors='replace')) >= MAX_FILENAME_LENGTH:
            filename = filename[:MAX_FILENAME_LENGTH-1]
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Ensure file_object has entries list
        if not hasattr(file_object, 'entries'):
            file_object.entries = []
        
        # Check for existing entry with same name
        existing_entry = None
        for entry in file_object.entries:
            if hasattr(entry, 'name') and entry.name.lower() == filename.lower():
                existing_entry = entry
                break
        
        if existing_entry:
            # Replace existing entry data
            existing_entry.data = file_data
            existing_entry.size = math.ceil(len(file_data) / SECTOR_SIZE)
            
            version = getattr(file_object, 'version', 'V2')
            if version == 'V2':
                existing_entry.streaming_size = existing_entry.size
            
            # Mark as modified
            existing_entry.is_new_entry = True
            existing_entry.modified = True
            
            # Basic RW detection
            rw_version, rw_version_name, format_info = _detect_rw_version_basic(file_data, filename)
            existing_entry._rw_version = rw_version
            existing_entry._rw_version_name = rw_version_name
            existing_entry._format_info = format_info
        else:
            # Create new entry
            new_entry = _create_img_entry(filename, file_data, file_object)
            
            if not new_entry:
                return False
            
            # Add to entries list
            file_object.entries.append(new_entry)
        
        # Mark file as modified
        file_object.modified = True
        
        return True

    except Exception:
        return False

def _refresh_after_import(main_window): #vers 1
    """Refresh UI after import"""
    try:
        # Refresh main table
        if hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        
        # Refresh file list
        if hasattr(main_window, 'refresh_file_list'):
            main_window.refresh_file_list()
        
        # Update UI for current IMG
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()
        
    except Exception:
        pass

def _ask_user_about_saving(main_window): #vers 1
    """Ask user about saving changes"""
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
                main_window.save_entry()
            elif hasattr(main_window, 'save_img_entry'):
                main_window.save_img_entry()

    except Exception:
        pass

def import_files_function(main_window): #vers 1
    """Import multiple files via file dialog"""

    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

    # File selection dialog
    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(
        main_window,
        "Select files to import", "", "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col);;Audio (*.wav)")

    if not file_paths:
        return False

    # Import files
    imported_count = 0
    failed_count = 0

    for file_path in file_paths:
        if _add_file_to_img(file_object, file_path):
            imported_count += 1
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported: {os.path.basename(file_path)}")
        else:
            failed_count += 1
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Failed: {os.path.basename(file_path)}")

    if imported_count > 0:
        # Refresh UI
        _refresh_after_import(main_window)

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import complete: {imported_count} imported, {failed_count} failed")
            main_window.log_message("IMG marked as modified - use Save Entry to save changes")

        # Ask user about saving
        _ask_user_about_saving(main_window)
        
        return True
    else:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Import failed: No files were imported successfully")
        return False

def import_files_with_list(main_window, file_paths: List[str]) -> bool: #vers 1
    """Import files from provided list"""

    if file_type != 'IMG' or not file_object:
        return False

    if not file_paths:
        return False

    # Import files
    imported_count = 0
    failed_count = 0

    for file_path in file_paths:
        if _add_file_to_img(file_object, file_path):
            imported_count += 1
        else:
            failed_count += 1

    if imported_count > 0:
        # Refresh UI
        _refresh_after_import(main_window)

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import complete: {imported_count} imported, {failed_count} failed")
            main_window.log_message("IMG marked as modified - use Save Entry to save changes")

        # Ask user about saving
        _ask_user_about_saving(main_window)
        
        return True
    else:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Import failed: No files were imported successfully")
        return False

def import_multiple_files_core(main_window, file_paths: List[str]) -> bool: #vers 1
    """Import multiple files with proper modification tracking"""
    return import_files_with_list(main_window, file_paths)

def import_folder_contents(main_window) -> bool: #vers 1
    """Import all files from a folder"""

    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False

    # Folder selection dialog
    folder_path = QFileDialog.getExistingDirectory(
        main_window, "Select folder to import")

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

    return import_files_with_list(main_window, file_paths)

def integrate_import_functions(main_window) -> bool: #vers 1
    """Integrate import functions with main window"""
    # Add import methods to main window
    main_window.import_files_function = lambda: import_files_function(main_window)
    main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
    main_window.import_multiple_files = lambda file_paths: import_multiple_files_core(main_window, file_paths)
    main_window.import_folder_contents = lambda: import_folder_contents(main_window)

    # Add aliases that GUI might use
    main_window.import_files = main_window.import_files_function
    main_window.import_via_dialog = main_window.import_files_function
    main_window.import_folder = main_window.import_folder_contents

    if hasattr(main_window, 'log_message'):
        main_window.log_message("Import functions integrated")
        main_window.log_message("   • File import with modification tracking")
        main_window.log_message("   • Basic RW version detection")
        main_window.log_message("   • Proper save entry detection")

    return True

# Export functions
__all__ = [
    'import_files_function',
    'import_files_with_list',
    'import_multiple_files_core',
    'import_folder_contents',
    'integrate_import_functions'
]
