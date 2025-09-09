#this belongs in core/import.py - Version: 15
# X-Seti - September09 2025 - IMG Factory 1.5 - Import Functions with Proper Modification Tracking

"""
Import Functions - Import files with proper modification tracking for Save Entry detection
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
# import_folder_contents
# import_multiple_files
# integrate_import_functions

def import_files_function(main_window): #vers 1
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

def import_multiple_files(main_window, file_paths: List[str]) -> bool: #vers 1
    """Import multiple files with proper modification tracking"""
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