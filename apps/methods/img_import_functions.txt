#this belongs in methods/ img_import_functions.py - Version: 1
# X-Seti - November16 2025 - IMG Factory 1.5 - IMG Import Functions

"""
IMG Import Functions - Handles importing files into IMG archives
Ported from img_import_export.py modern system
Provides file import, batch import, folder import, and validation
"""

import os
import struct
import math
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from apps.methods.img_entry_operations import add_entry_safe, add_multiple_entries

##Methods list -
# add_file_to_img
# add_multiple_files_to_img
# refresh_after_import
# ask_user_about_saving
# import_file
# import_multiple_files
# import_folder
# validate_import_file
# get_import_preview
# integrate_img_import_functions

# Constants
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24

def add_file_to_img(file_object, file_path: str, main_window=None) -> bool: #vers 1
    """Add single file to IMG archive - CORE FUNCTION
    
    This is a wrapper around import_file for compatibility with existing code
    
    Args:
        file_object: IMG archive object
        file_path: Path to file to import
        main_window: Optional main window for logging
        
    Returns:
        True if import successful, False otherwise
    """
    try:
        return import_file(file_object, file_path)
    except Exception as e:
        if main_window and hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error adding file: {str(e)}")
        return False


def add_multiple_files_to_img(file_object, file_paths: List[str], main_window=None) -> Tuple[List, List]: #vers 1
    """Add multiple files to IMG archive - CORE FUNCTION
    
    This is a wrapper around import_multiple_files for compatibility with existing code
    
    Args:
        file_object: IMG archive object
        file_paths: List of file paths to import
        main_window: Optional main window for logging
        
    Returns:
        Tuple of (success_list, failed_list)
    """
    try:
        return import_multiple_files(file_object, file_paths)
    except Exception as e:
        if main_window and hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error adding multiple files: {str(e)}")
        return [], file_paths


def import_file(img_archive, file_path: str, entry_name: Optional[str] = None) -> bool: #vers 1
    """Import a file into an IMG archive
    
    Args:
        img_archive: IMG archive object
        file_path: Path to file to import
        entry_name: Optional custom entry name (default: filename)
        
    Returns:
        True if import successful, False otherwise
    """
    try:
        # Import debug system
        try:
            from apps.debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not os.path.exists(file_path):
            if img_debugger:
                img_debugger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine entry name
        if not entry_name:
            entry_name = os.path.basename(file_path)
        
        if img_debugger:
            img_debugger.debug(f"Importing file: {file_path} as {entry_name}")
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        if img_debugger:
            img_debugger.debug(f"Read {len(file_data)} bytes from {file_path}")
        
        # Use the add_entry method from the archive or fallback to add_entry_safe
        if hasattr(img_archive, 'add_entry') and callable(img_archive.add_entry):
            success = img_archive.add_entry(entry_name, file_data)
        else:
            success = add_entry_safe(img_archive, entry_name, file_data)
        
        if success:
            if img_debugger:
                img_debugger.success(f"Successfully imported: {entry_name}")
            return True
        else:
            if img_debugger:
                img_debugger.error(f"Failed to add entry to archive: {entry_name}")
            return False
                
    except Exception as e:
        try:
            from apps.debug.img_debug_functions import img_debugger
            img_debugger.error(f"Failed to import file {file_path}: {str(e)}")
        except:
            print(f"[ERROR] import_file failed: {e}")
        return False


def import_multiple_files(img_archive, file_paths: List[str], entry_names: Optional[List[str]] = None) -> Tuple[List, List]: #vers 1
    """Import multiple files into an IMG archive
    
    Args:
        img_archive: IMG archive object
        file_paths: List of file paths to import
        entry_names: Optional list of custom entry names
        
    Returns:
        Tuple of (success_list, failed_list)
    """
    try:
        # Import debug system
        try:
            from apps.debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not file_paths:
            return [], []
        
        # Validate entry names if provided
        if entry_names and len(entry_names) != len(file_paths):
            raise ValueError("Entry names list must match file paths list length")
        
        success_list = []
        failed_list = []
        
        for i, file_path in enumerate(file_paths):
            entry_name = entry_names[i] if entry_names else None
            
            if import_file(img_archive, file_path, entry_name):
                success_list.append(file_path)
            else:
                failed_list.append(file_path)
        
        if img_debugger:
            img_debugger.info(f"Batch import: {len(success_list)} success, {len(failed_list)} failed")
        
        return success_list, failed_list
        
    except Exception as e:
        try:
            from apps.debug.img_debug_functions import img_debugger
            img_debugger.error(f"Failed to import multiple files: {str(e)}")
        except:
            print(f"[ERROR] import_multiple_files failed: {e}")
        return [], file_paths


def import_folder(img_archive, folder_path: str, recursive: bool = False, 
                  filter_extensions: Optional[List[str]] = None) -> Tuple[List, List]: #vers 1
    """Import all files from a folder into an IMG archive
    
    Args:
        img_archive: IMG archive object
        folder_path: Path to folder to import from
        recursive: Whether to recurse into subdirectories
        filter_extensions: Optional list of file extensions to filter (e.g., ['.dff', '.txd'])
        
    Returns:
        Tuple of (success_list, failed_list)
    """
    try:
        # Import debug system
        try:
            from apps.debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not os.path.exists(folder_path):
            if img_debugger:
                img_debugger.error(f"Folder not found: {folder_path}")
            return [], []
        
        if not os.path.isdir(folder_path):
            if img_debugger:
                img_debugger.error(f"Path is not a folder: {folder_path}")
            return [], []
        
        # Collect files
        file_paths = []
        
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Apply filter if provided
                    if filter_extensions:
                        ext = os.path.splitext(file)[1].lower()
                        if ext not in [e.lower() for e in filter_extensions]:
                            continue
                    
                    file_paths.append(file_path)
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                
                if not os.path.isfile(file_path):
                    continue
                
                # Apply filter if provided
                if filter_extensions:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in [e.lower() for e in filter_extensions]:
                        continue
                
                file_paths.append(file_path)
        
        if img_debugger:
            img_debugger.debug(f"Found {len(file_paths)} files to import from {folder_path}")
        
        # Import all collected files
        return import_multiple_files(img_archive, file_paths)
        
    except Exception as e:
        try:
            from apps.debug.img_debug_functions import img_debugger
            img_debugger.error(f"Failed to import folder {folder_path}: {str(e)}")
        except:
            print(f"[ERROR] import_folder failed: {e}")
        return [], []


def validate_import_file(file_path: str, max_size_mb: Optional[int] = None) -> Tuple[bool, str]: #vers 1
    """Validate a file before importing
    
    Args:
        file_path: Path to file to validate
        max_size_mb: Optional maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Check if it's a file
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        # Check filename length
        filename = os.path.basename(file_path)
        if len(filename) > MAX_FILENAME_LENGTH:
            return False, f"Filename too long (max {MAX_FILENAME_LENGTH} chars): {filename}"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        
        if max_size_mb:
            max_size_bytes = max_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                return False, f"File too large (max {max_size_mb}MB): {file_size / 1024 / 1024:.2f}MB"
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            return False, f"File not readable: {str(e)}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_import_preview(img_archive, file_paths: List[str]) -> Dict[str, any]: #vers 1
    """Get preview information for importing files
    
    Args:
        img_archive: IMG archive object
        file_paths: List of file paths to preview
        
    Returns:
        Dictionary with preview information
    """
    try:
        preview = {
            'total_files': len(file_paths),
            'valid_files': 0,
            'invalid_files': 0,
            'total_size': 0,
            'files': []
        }
        
        for file_path in file_paths:
            is_valid, error_msg = validate_import_file(file_path)
            
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'valid': is_valid,
                'error': error_msg
            }
            
            preview['files'].append(file_info)
            
            if is_valid:
                preview['valid_files'] += 1
                preview['total_size'] += file_info['size']
            else:
                preview['invalid_files'] += 1
        
        # Calculate sectors needed
        if preview['total_size'] > 0:
            preview['sectors_needed'] = math.ceil(preview['total_size'] / SECTOR_SIZE)
        else:
            preview['sectors_needed'] = 0
        
        return preview
        
    except Exception as e:
        return {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'total_size': 0,
            'sectors_needed': 0,
            'files': [],
            'error': str(e)
        }


def refresh_after_import(main_window) -> None: #vers 1
    """Refresh UI after import operation
    
    Args:
        main_window: Main application window
    """
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
    """Ask user if they want to save after import
    
    Args:
        main_window: Main application window
    """
    try:
        from PyQt6.QtWidgets import QMessageBox
        
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


def integrate_img_import_functions(main_window) -> bool: #vers 1
    """Integrate IMG import functions into main window
    
    Args:
        main_window: Main application window
        
    Returns:
        True if integration successful
    """
    try:
        # Add import methods to main window
        main_window.import_file = lambda img_archive, file_path, entry_name=None: import_file(img_archive, file_path, entry_name)
        main_window.import_multiple_files = lambda img_archive, file_paths, entry_names=None: import_multiple_files(img_archive, file_paths, entry_names)
        main_window.import_folder = lambda img_archive, folder_path, recursive=False, filter_extensions=None: import_folder(img_archive, folder_path, recursive, filter_extensions)
        main_window.validate_import_file = lambda file_path, max_size_mb=None: validate_import_file(file_path, max_size_mb)
        main_window.get_import_preview = lambda img_archive, file_paths: get_import_preview(img_archive, file_paths)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("IMG import functions integrated")
            main_window.log_message("   • Single file import")
            main_window.log_message("   • Batch file import")
            main_window.log_message("   • Folder import with filtering")
            main_window.log_message("   • Import validation and preview")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"IMG import integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'add_file_to_img',
    'add_multiple_files_to_img',
    'refresh_after_import',
    'ask_user_about_saving',
    'import_file',
    'import_multiple_files',
    'import_folder',
    'validate_import_file',
    'get_import_preview',
    'integrate_img_import_functions'
]
