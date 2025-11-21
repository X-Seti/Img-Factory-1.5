#this belongs in core/impotr.py - Version: 16
# X-Seti - November21 2025 - IMG Factory 1.5 - CLEAN IMPORT SYSTEM
"""
IMPORT SYSTEM
"""
import os
from typing import List
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from apps.methods.tab_system import get_current_file_from_active_tab
from apps.methods.img_import_functions import add_multiple_files_to_img, refresh_after_import
from apps.methods.rw_versions import parse_rw_version, get_rw_version_name

def import_files_function(main_window) -> bool:
    """Import multiple files via dialog - CLEAN, NO FALLBACKS"""
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
            # Mark as new entries and store data for RW detection
            for entry in file_object.entries:
                if not hasattr(entry, 'is_new_entry') and hasattr(entry, 'name'):
                    for fp in success_list:
                        if os.path.basename(fp) == entry.name:
                            entry.is_new_entry = True
                            # Read and store data for RW version detection during Save Entry
                            if not hasattr(entry, 'data') or not entry.data:
                                try:
                                    with open(fp, 'rb') as f:
                                        entry.data = f.read()
                                    # Parse RW version immediately for table display
                                    if entry.name.lower().endswith(('.dff', '.txd')):
                                        version_val, version_name = parse_rw_version(entry.data[8:12] if len(entry.data) >= 12 else b'\x00\x00\x00\x00')
                                        if version_val > 0:
                                            entry.rw_version = version_val
                                            entry.rw_version_name = version_name
                                        else:
                                            entry.rw_version_name = "RW File"
                                    else:
                                        entry.rw_version_name = "Unknown"
                                except Exception as e:
                                    if hasattr(main_window, 'log_message'):
                                        main_window.log_message(f"Failed to read data for {entry.name}: {str(e)}")
                                    entry.rw_version_name = "Unknown"
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
    """Import from provided list - CLEAN, NO FALLBACKS"""
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
                    if os.path.basename(fp) == entry.name:
                        entry.is_new_entry = True
                        if not hasattr(entry, 'data') or not entry.data:
                            try:
                                with open(fp, 'rb') as f:
                                    entry.data = f.read()
                                if entry.name.lower().endswith(('.dff', '.txd')):
                                    version_val, version_name = parse_rw_version(entry.data[8:12] if len(entry.data) >= 12 else b'\x00\x00\x00\x00')
                                    if version_val > 0:
                                        entry.rw_version = version_val
                                        entry.rw_version_name = version_name
                                    else:
                                        entry.rw_version_name = "RW File"
                                else:
                                    entry.rw_version_name = "Unknown"
                            except Exception as e:
                                if hasattr(main_window, 'log_message'):
                                    main_window.log_message(f"Failed to read data for {entry.name}: {str(e)}")
                                entry.rw_version_name = "Unknown"
                        break
        refresh_after_import(main_window)
        return True
    return False

def import_folder_contents(main_window) -> bool:
    """Import folder contents - CLEAN, NO FALLBACKS"""
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
                    if os.path.basename(fp) == entry.name:
                        entry.is_new_entry = True
                        if not hasattr(entry, 'data') or not entry.data:
                            try:
                                with open(fp, 'rb') as f:
                                    entry.data = f.read()
                                if entry.name.lower().endswith(('.dff', '.txd')):
                                    version_val, version_name = parse_rw_version(entry.data[8:12] if len(entry.data) >= 12 else b'\x00\x00\x00\x00')
                                    if version_val > 0:
                                        entry.rw_version = version_val
                                        entry.rw_version_name = version_name
                                    else:
                                        entry.rw_version_name = "RW File"
                                else:
                                    entry.rw_version_name = "Unknown"
                            except Exception as e:
                                if hasattr(main_window, 'log_message'):
                                    main_window.log_message(f"Failed to read data for {entry.name}: {str(e)}")
                                entry.rw_version_name = "Unknown"
                        break
        refresh_after_import(main_window)
        return True
    return False

def integrate_import_functions(main_window) -> bool:
    """Integrate clean import functions"""
    try:
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
        main_window.import_folder_contents = lambda: import_folder_contents(main_window)
        main_window.import_files = main_window.import_files_function
        main_window.import_folder = main_window.import_folder_contents

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ CLEAN import system integrated")
            main_window.log_message("   • No auto-save crashes")
            main_window.log_message("   • Mark new entries for Save Entry")
            main_window.log_message("   • RW version detection for table display")
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
