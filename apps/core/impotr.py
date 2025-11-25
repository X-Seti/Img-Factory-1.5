#this belongs in core/import.py - Version: 19
# X-Seti - November25 2025 - IMG Factory 1.5 - NEW IMPORT SYSTEM - FIXED
"""
NEW IMPORT SYSTEM - Ground Up Rebuild - FIXED VERSION
"""
import os
import re
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from apps.methods.tab_system import get_current_file_from_active_tab
from apps.methods.img_import_functions import add_multiple_files_to_img, refresh_after_import
from apps.methods.rw_versions import parse_rw_version, get_rw_version_name


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove problematic characters"""
    # Remove invalid characters and replace with underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32 and ord(c) != 127)
    return sanitized


def detect_file_type(filename: str) -> str:
    """Detect file type based on extension"""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.dff']:
        return 'MODEL'
    elif ext in ['.txd']:
        return 'TEXTURE'
    elif ext in ['.col']:
        return 'COLLISION'
    elif ext in ['.wav', '.mp3', '.ogg']:
        return 'AUDIO'
    elif ext in ['.dat', '.txt']:
        return 'TEXT'
    else:
        return 'UNKNOWN'


def detect_rw_version(file_path: str) -> tuple[int, str]:
    """Detect RenderWare version from file data"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        if len(data) >= 12:
            version_val, version_name = parse_rw_version(data[8:12])
            if version_val > 0:
                return version_val, version_name
        return 0, "Unknown"
    except Exception:
        return 0, "Unknown"


def import_files_function(main_window) -> bool:
    """Import multiple files via dialog - NEW SYSTEM"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Active tab must contain an IMG file")
            return False

        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window, "Select files to import", "",
            "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col);;Audio (*.wav)"
        )
        if not file_paths:
            return False

        # Import WITHOUT auto-save
        success_list, failed_list = add_multiple_files_to_img(file_object, file_paths, main_window)
        imported_count = len(success_list)

        if imported_count > 0:
            # Mark as new entries and store data for proper metadata
            for entry in file_object.entries:
                if not hasattr(entry, 'is_new_entry') and hasattr(entry, 'name'):
                    for fp in success_list:
                        if sanitize_filename(os.path.basename(fp)) == sanitize_filename(entry.name):
                            entry.is_new_entry = True
                            # Read and store data for metadata
                            if not hasattr(entry, 'data') or not entry.data:
                                try:
                                    with open(fp, 'rb') as f:
                                        entry.data = f.read()
                                    # Set file type
                                    entry.file_type = detect_file_type(entry.name)
                                    # Parse RW version for table display
                                    if entry.name.lower().endswith(('.dff', '.txd')):
                                        version_val, version_name = detect_rw_version(fp)
                                        entry.rw_version = version_val
                                        entry.rw_version_name = version_name
                                    else:
                                        entry.rw_version_name = "N/A"
                                except Exception as e:
                                    if hasattr(main_window, 'log_message'):
                                        main_window.log_message(f"Failed to read data for {entry.name}: {str(e)}")
                                    entry.rw_version_name = "Error"
                            break

            refresh_after_import(main_window)
            main_window.log_message(f"Imported {imported_count} file(s) - use Save Entry to save changes")
            return True
        else:
            main_window.log_message("Import failed: No files were imported")
            return False

    except Exception as e:
        main_window.log_message(f"Import error: {str(e)}")
        return False


def import_files_with_list(main_window, file_paths: List[str]) -> bool:
    """Import from provided list - NEW SYSTEM"""
    if not file_paths:
        return False

    file_object, file_type = get_current_file_from_active_tab(main_window)
    if file_type != 'IMG' or not file_object:
        return False

    success_list, failed_list = add_multiple_files_to_img(file_object, file_paths, main_window)
    if success_list:
        # Mark as new entries and store data
        for entry in file_object.entries:
            if not hasattr(entry, 'is_new_entry') and hasattr(entry, 'name'):
                for fp in success_list:
                    if sanitize_filename(os.path.basename(fp)) == sanitize_filename(entry.name):
                        entry.is_new_entry = True
                        if not hasattr(entry, 'data') or not entry.data:
                            try:
                                with open(fp, 'rb') as f:
                                    entry.data = f.read()
                                # Set file type
                                entry.file_type = detect_file_type(entry.name)
                                # Parse RW version
                                if entry.name.lower().endswith(('.dff', '.txd')):
                                    version_val, version_name = detect_rw_version(fp)
                                    entry.rw_version = version_val
                                    entry.rw_version_name = version_name
                                else:
                                    entry.rw_version_name = "N/A"
                            except Exception as e:
                                if hasattr(main_window, 'log_message'):
                                    main_window.log_message(f"Failed to read data for {entry.name}: {str(e)}")
                                entry.rw_version_name = "Error"
                        break
        refresh_after_import(main_window)
        return True
    return False


def import_folder_contents(main_window) -> bool:
    """Import folder contents - NEW SYSTEM"""
    file_object, file_type = get_current_file_from_active_tab(main_window)
    if file_type != 'IMG' or not file_object:
        return False

    folder_path = QFileDialog.getExistingDirectory(main_window, "Select Folder to Import")
    if not folder_path:
        return False

    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))

    if not file_paths:
        return False

    success_list, failed_list = add_multiple_files_to_img(file_object, file_paths, main_window)
    if success_list:
        # Mark as new entries and store data
        for entry in file_object.entries:
            if not hasattr(entry, 'is_new_entry') and hasattr(entry, 'name'):
                for fp in success_list:
                    if sanitize_filename(os.path.basename(fp)) == sanitize_filename(entry.name):
                        entry.is_new_entry = True
                        if not hasattr(entry, 'data') or not entry.data:
                            try:
                                with open(fp, 'rb') as f:
                                    entry.data = f.read()
                                # Set file type
                                entry.file_type = detect_file_type(entry.name)
                                # Parse RW version
                                if entry.name.lower().endswith(('.dff', '.txd')):
                                    version_val, version_name = detect_rw_version(fp)
                                    entry.rw_version = version_val
                                    entry.rw_version_name = version_name
                                else:
                                    entry.rw_version_name = "N/A"
                            except Exception as e:
                                if hasattr(main_window, 'log_message'):
                                    main_window.log_message(f"Failed to read data for {entry.name}: {str(e)}")
                                entry.rw_version_name = "Error"
                        break
        refresh_after_import(main_window)
        return True
    return False


def integrate_import_functions(main_window) -> bool:
    """Integrate NEW import functions"""
    try:
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
        main_window.import_folder_contents = lambda: import_folder_contents(main_window)
        main_window.import_files = main_window.import_files_function
        main_window.import_folder = main_window.import_folder_contents

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ NEW import system integrated")
            main_window.log_message("   • No auto-save crashes")
            main_window.log_message("   • Proper metadata detection")
            main_window.log_message("   • Filename sanitization")
            main_window.log_message("   • File type detection")
            main_window.log_message("   • RW version detection")
            main_window.log_message("   • Tab-aware only")
        return True
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import integration failed: {str(e)}")
        return False


__all__ = [
    'import_files_function',
    'import_files_with_list',
    'import_folder_contents',
    'integrate_import_functions'
]