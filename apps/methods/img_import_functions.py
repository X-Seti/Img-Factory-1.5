#this belongs in methods/img_import_functions.py - Version: 2
# X-Seti - November16 2025 - IMG Factory 1.5 - Consolidated Import Functions

"""
Consolidated Import Functions - All import operations in ONE file
Combines: img_import_export.py + RW detection + core operations
"""

import os
import struct
from typing import List, Optional, Tuple
from PyQt6.QtWidgets import QMessageBox

from apps.core.rw_versions import parse_rw_version, get_rw_version_name, is_valid_rw_version

##Methods list -
# add_file_to_img
# add_multiple_files_to_img
# detect_rw_version_from_data
# mark_entry_as_new
# refresh_after_import
# ask_user_about_saving
# validate_import_file

SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24

def detect_rw_version_from_data(file_data: bytes, filename: str) -> Tuple[Optional[int], str]: #vers 1
    """Detect RW version from file data for new entries"""
    try:
        file_ext = filename.split('.')[-1].upper() if '.' in filename else "UNKNOWN"
        
        # Only analyze RW files (DFF, TXD)
        if file_ext not in ['DFF', 'TXD']:
            return None, "Non-RW"
        
        # Check minimum size
        if len(file_data) < 12:
            return None, "Invalid"
        
        # Read RW version from header (bytes 8-12)
        version_bytes = file_data[8:12]
        version_value = struct.unpack('<I', version_bytes)[0]
        
        # Validate and get name
        if is_valid_rw_version(version_value):
            version_name = get_rw_version_name(version_value)
            return version_value, version_name
        else:
            return None, "Unknown"
            
    except Exception:
        return None, "Error"


def mark_entry_as_new(entry, file_data: bytes, filename: str) -> None: #vers 1
    """Mark entry as new and detect RW version if applicable"""
    try:
        # Mark as new entry
        entry.is_new_entry = True
        entry.modified = True
        
        # Detect RW version for RenderWare files
        rw_version, rw_name = detect_rw_version_from_data(file_data, filename)
        if rw_version:
            entry.rw_version = rw_version
            entry.rw_version_name = rw_name
        else:
            entry.rw_version = None
            entry.rw_version_name = rw_name if rw_name else "N/A"
            
    except Exception:
        # Fail silently, entry is still marked as new
        pass


def add_file_to_img(file_object, file_path: str, main_window=None) -> bool: #vers 2
    """
    Add single file to IMG archive - CORE FUNCTION with RW detection
    Works with both old and new IMG file objects
    """
    try:
        if not os.path.exists(file_path):
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message(f"File not found: {file_path}")
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
                    # Find and mark the newly added entry
                    if hasattr(file_object, 'entries') and file_object.entries:
                        for entry in reversed(file_object.entries):
                            if hasattr(entry, 'name') and entry.name == filename:
                                mark_entry_as_new(entry, file_data, filename)
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
                
                # Mark entry as new
                if success and hasattr(file_object, 'entries') and file_object.entries:
                    for entry in reversed(file_object.entries):
                        if hasattr(entry, 'name') and entry.name == filename:
                            mark_entry_as_new(entry, file_data, filename)
                            break
            except ImportError:
                pass

        # Mark file as modified
        if success and hasattr(file_object, 'modified'):
            file_object.modified = True

        return success

    except Exception as e:
        if main_window and hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error adding file: {str(e)}")
        return False


def add_multiple_files_to_img(file_object, file_paths: List[str], main_window=None) -> int: #vers 2
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
                main_window.log_message(f"Imported: {os.path.basename(file_path)}")
        else:
            failed_count += 1
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message(f"Failed: {os.path.basename(file_path)}")

    return imported_count


def validate_import_file(file_path: str, max_size_mb: Optional[int] = None) -> Tuple[bool, str]: #vers 1
    """Validate a file before importing"""
    try:
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, f"File is empty: {file_path}"
        
        if max_size_mb and file_size > (max_size_mb * 1024 * 1024):
            return False, f"File too large ({file_size / (1024*1024):.1f}MB > {max_size_mb}MB): {file_path}"
        
        # Check filename length
        filename = os.path.basename(file_path)
        if len(filename.encode('ascii', errors='replace')) >= MAX_FILENAME_LENGTH:
            return False, f"Filename too long (>{MAX_FILENAME_LENGTH-1} chars): {filename}"
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)  # Try to read at least 1 byte
        except PermissionError:
            return False, f"Permission denied reading file: {file_path}"
        except Exception as e:
            return False, f"Cannot read file: {file_path} - {str(e)}"
        
        return True, "File is valid for import"
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"


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
    'detect_rw_version_from_data',
    'mark_entry_as_new',
    'refresh_after_import',
    'ask_user_about_saving',
    'validate_import_file'
]
