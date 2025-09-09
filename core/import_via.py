#this belongs in core/import_via.py - Version: 8
# X-Seti - September09 2025 - IMG Factory 1.5 - Import Via Functions with Proper Modification Tracking

"""
Import Via Functions - Import files via IDE/text with proper modification tracking for Save Entry detection
"""

import os
from typing import List, Tuple
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# _add_file_to_img_with_tracking_via
# _ask_user_about_saving_via
# _find_file_in_directory
# _parse_ide_file_for_import
# _parse_text_file_for_import
# _refresh_after_import_via
# import_via_function
# import_via_ide_function
# import_via_text_function
# integrate_import_via_functions

def import_via_function(main_window): #vers 1
    """Import files via file selection dialog"""
    if not validate_tab_before_operation(main_window, "Import Via"):
        return False
    
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        main_window,
        "Select file for import list",
        "",
        "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
    )
    
    if not file_path:
        return False
    
    if file_path.lower().endswith('.ide'):
        return import_via_ide_function_with_path(main_window, file_path)
    else:
        return import_via_text_function_with_path(main_window, file_path)

def import_via_ide_function(main_window): #vers 1
    """Import files using IDE file with models directory selection"""
    if not validate_tab_before_operation(main_window, "Import Via IDE"):
        return False
    
    file_object, file_type = get_current_file_from_active_tab(main_window)
    
    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    # Select IDE file
    file_dialog = QFileDialog()
    ide_path, _ = file_dialog.getOpenFileName(
        main_window,
        "Select IDE file for import",
        "",
        "IDE Files (*.ide);;All Files (*)"
    )
    
    if not ide_path:
        return False
    
    # Select models directory
    models_dir = QFileDialog.getExistingDirectory(
        main_window,
        "Select directory containing DFF/TXD files"
    )
    
    if not models_dir:
        return False
    
    return import_via_ide_function_with_paths(main_window, ide_path, models_dir)

def import_via_ide_function_with_path(main_window, ide_path: str): #vers 1
    """Import files using IDE file path (auto-detect models directory)"""
    models_dir = os.path.dirname(ide_path)  # Use IDE file's directory
    return import_via_ide_function_with_paths(main_window, ide_path, models_dir)

def import_via_ide_function_with_paths(main_window, ide_path: str, models_dir: str): #vers 1
    """Import files using IDE file and models directory with proper modification tracking"""
    if not validate_tab_before_operation(main_window, "Import Via IDE"):
        return False
    
    file_object, file_type = get_current_file_from_active_tab(main_window)
    
    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    if not os.path.exists(ide_path):
        QMessageBox.warning(main_window, "File Not Found", f"IDE file not found: {ide_path}")
        return False
    
    if not os.path.exists(models_dir):
        QMessageBox.warning(main_window, "Directory Not Found", f"Models directory not found: {models_dir}")
        return False
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Importing via IDE: {os.path.basename(ide_path)}")
        main_window.log_message(f"Models directory: {models_dir}")
    
    # Parse IDE file
    model_files, texture_files, missing_files = _parse_ide_file_for_import(ide_path, models_dir)
    
    total_found = len(model_files) + len(texture_files)
    
    if total_found == 0:
        QMessageBox.information(main_window, "No Files Found", "No DFF/TXD files found for IDE entries")
        return False
    
    # Show preview to user
    preview_msg = f"Found {total_found} files to import:\n"
    preview_msg += f"• {len(model_files)} DFF model files\n"
    preview_msg += f"• {len(texture_files)} TXD texture files\n"
    
    if missing_files:
        preview_msg += f"\nMissing {len(missing_files)} files:\n"
        preview_msg += "\n".join(missing_files[:5])  # Show first 5 missing
        if len(missing_files) > 5:
            preview_msg += f"\n... and {len(missing_files) - 5} more"
    
    preview_msg += "\n\nProceed with import?"
    
    reply = QMessageBox.question(
        main_window,
        "Import Via IDE Preview",
        preview_msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )
    
    if reply != QMessageBox.StandardButton.Yes:
        return False
    
    # Import files with proper tracking
    imported_count = 0
    all_files = model_files + texture_files
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        if _add_file_to_img_with_tracking_via(file_object, file_path, filename, main_window):
            imported_count += 1
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported via IDE: {filename}")
    
    if imported_count > 0:
        _refresh_after_import_via(main_window)
        
        QMessageBox.information(
            main_window,
            "Import Via IDE Complete",
            f"Successfully imported {imported_count} files via IDE.\n\n"
            f"Use 'Save Entry' to save changes to disk."
        )
        
        # Ask user about saving
        _ask_user_about_saving_via(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"IDE import complete: {imported_count} files - use Save Entry to save changes")
    
    return imported_count > 0

def import_via_text_function(main_window): #vers 1
    """Import files using text file selection"""
    if not validate_tab_before_operation(main_window, "Import Via Text"):
        return False
    
    file_dialog = QFileDialog()
    text_path, _ = file_dialog.getOpenFileName(
        main_window,
        "Select text file for import",
        "",
        "Text Files (*.txt);;All Files (*)"
    )
    
    if not text_path:
        return False
    
    return import_via_text_function_with_path(main_window, text_path)

def import_via_text_function_with_path(main_window, text_path: str): #vers 1
    """Import files using text file with proper modification tracking"""
    if not validate_tab_before_operation(main_window, "Import Via Text"):
        return False
    
    file_object, file_type = get_current_file_from_active_tab(main_window)
    
    if file_type != 'IMG' or not file_object:
        QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
        return False
    
    if not os.path.exists(text_path):
        QMessageBox.warning(main_window, "File Not Found", f"Text file not found: {text_path}")
        return False
    
    # Select directory containing the files
    files_dir = QFileDialog.getExistingDirectory(
        main_window,
        "Select directory containing the files to import"
    )
    
    if not files_dir:
        return False
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"Importing via text: {os.path.basename(text_path)}")
        main_window.log_message(f"Files directory: {files_dir}")
    
    # Parse text file
    file_paths, missing_files = _parse_text_file_for_import(text_path, files_dir)
    
    if not file_paths:
        QMessageBox.information(main_window, "No Files Found", "No files found for text file entries")
        return False
    
    # Show preview to user
    preview_msg = f"Found {len(file_paths)} files to import from text file.\n"
    
    if missing_files:
        preview_msg += f"\nMissing {len(missing_files)} files:\n"
        preview_msg += "\n".join(missing_files[:5])
        if len(missing_files) > 5:
            preview_msg += f"\n... and {len(missing_files) - 5} more"
    
    preview_msg += "\n\nProceed with import?"
    
    reply = QMessageBox.question(
        main_window,
        "Import Via Text Preview",
        preview_msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )
    
    if reply != QMessageBox.StandardButton.Yes:
        return False
    
    # Import files with proper tracking
    imported_count = 0
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        if _add_file_to_img_with_tracking_via(file_object, file_path, filename, main_window):
            imported_count += 1
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Imported via text: {filename}")
    
    if imported_count > 0:
        _refresh_after_import_via(main_window)
        
        QMessageBox.information(
            main_window,
            "Import Via Text Complete",
            f"Successfully imported {imported_count} files via text file.\n\n"
            f"Use 'Save Entry' to save changes to disk."
        )
        
        # Ask user about saving
        _ask_user_about_saving_via(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Text import complete: {imported_count} files - use Save Entry to save changes")
    
    return imported_count > 0

def _add_file_to_img_with_tracking_via(file_object, file_path: str, filename: str, main_window) -> bool: #vers 1
    """Add file to IMG via with proper modification tracking - FIXES SAVE ENTRY DETECTION"""
    # Read file data
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # Use IMG file's add_entry method if available
    if hasattr(file_object, 'add_entry') and callable(file_object.add_entry):
        success = file_object.add_entry(filename, file_data)
        
        if success:
            # Find the added entry and mark it as new
            if hasattr(file_object, 'entries'):
                for entry in reversed(file_object.entries):  # Check recent entries first
                    if hasattr(entry, 'name') and entry.name == filename:
                        # CRITICAL: Mark as new entry for Save Entry detection
                        entry.is_new_entry = True
                        break
            
            # Mark file as modified
            file_object.modified = True
            
            return True
    
    # Fallback: Use methods from img_entry_operations
    try:
        from methods.img_entry_operations import add_entry_safe
        success = add_entry_safe(file_object, filename, file_data, auto_save=False)
        
        if success:
            # Find the added entry and mark it as new
            if hasattr(file_object, 'entries'):
                for entry in reversed(file_object.entries):
                    if hasattr(entry, 'name') and entry.name == filename:
                        # CRITICAL: Mark as new entry for Save Entry detection
                        entry.is_new_entry = True
                        break
            
            # Mark file as modified
            file_object.modified = True
            
            return True
        
    except ImportError:
        pass
    
    return False

def _parse_ide_file_for_import(ide_path: str, models_dir: str) -> Tuple[List[str], List[str], List[str]]: #vers 1
    """Parse IDE file and find corresponding DFF/TXD files"""
    model_files = []
    texture_files = []
    missing_files = []
    
    model_names = set()
    texture_names = set()
    
    # Parse IDE file
    with open(ide_path, 'r', encoding='utf-8', errors='ignore') as f:
        current_section = None
        
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            
            # Check for section headers
            if line.lower() == 'objs':
                current_section = 'objs'
                continue
            elif line.lower() == 'tobj':
                current_section = 'tobj'
                continue
            elif line.lower() == 'end':
                current_section = None
                continue
            
            # Parse entries in objs and tobj sections
            if current_section in ['objs', 'tobj']:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 3:  # Need at least ID, ModelName, TextureName
                    model_name = parts[1].strip()
                    texture_name = parts[2].strip()
                    
                    # Add model name
                    if model_name and not model_name.isdigit() and model_name != '-1':
                        model_names.add(model_name)
                    
                    # Add texture name
                    if texture_name and not texture_name.isdigit() and texture_name != '-1':
                        texture_names.add(texture_name)
    
    # Find model files (.dff)
    for model_name in model_names:
        dff_path = _find_file_in_directory(models_dir, f"{model_name}.dff")
        if dff_path:
            model_files.append(dff_path)
        else:
            missing_files.append(f"{model_name}.dff")
    
    # Find texture files (.txd)
    for texture_name in texture_names:
        txd_path = _find_file_in_directory(models_dir, f"{texture_name}.txd")
        if txd_path:
            texture_files.append(txd_path)
        else:
            missing_files.append(f"{texture_name}.txd")
    
    return model_files, texture_files, missing_files

def _parse_text_file_for_import(text_path: str, files_dir: str) -> Tuple[List[str], List[str]]: #vers 1
    """Parse text file and find corresponding files"""
    found_files = []
    missing_files = []
    
    with open(text_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                # Smart parsing - extract filename if it's a path
                if '/' in line or '\\' in line:
                    filename = os.path.basename(line)
                else:
                    filename = line
                
                # Find file
                file_path = _find_file_in_directory(files_dir, filename)
                if file_path:
                    found_files.append(file_path)
                else:
                    missing_files.append(filename)
    
    return found_files, missing_files

def _find_file_in_directory(directory: str, filename: str) -> str: #vers 1
    """Find file in directory (case-insensitive)"""
    filename_lower = filename.lower()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() == filename_lower:
                return os.path.join(root, file)
    
    return ""

def _refresh_after_import_via(main_window): #vers 1
    """Refresh UI after import via"""
    # Refresh main table
    if hasattr(main_window, 'refresh_table'):
        main_window.refresh_table()
    
    # Update file list
    if hasattr(main_window, 'refresh_file_list'):
        main_window.refresh_file_list()
    
    # Update GUI layout
    if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'refresh_file_list'):
        main_window.gui_layout.refresh_file_list()
    
    # Update UI state
    if hasattr(main_window, '_update_ui_for_loaded_img'):
        main_window._update_ui_for_loaded_img()
    
    # Update current tab data
    if hasattr(main_window, 'refresh_current_tab_data'):
        main_window.refresh_current_tab_data()
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message("UI refreshed after import via")

def _ask_user_about_saving_via(main_window): #vers 1
    """Ask user about saving changes after import via"""
    # Show info message
    QMessageBox.information(main_window, "Import Via Complete",
        "Files imported to memory successfully!\n\n"
        "Use the 'Save Entry' button to save changes to disk.\n"
        "Changes will be lost if you reload without saving.")

def integrate_import_via_functions(main_window) -> bool: #vers 1
    """Integrate import via functions with proper modification tracking"""
    # Add import via methods to main window
    main_window.import_via_function = lambda: import_via_function(main_window)
    main_window.import_via_ide_function = lambda: import_via_ide_function(main_window)
    main_window.import_via_text_function = lambda: import_via_text_function(main_window)
    
    # Add aliases that GUI might use
    main_window.import_via = main_window.import_via_function
    main_window.import_via_ide = main_window.import_via_ide_function
    main_window.import_via_text = main_window.import_via_text_function
    
    if hasattr(main_window, 'log_message'):
        main_window.log_message("Import via functions integrated with proper modification tracking")
        main_window.log_message("   • Marks imported entries as new for Save Entry detection")
        main_window.log_message("   • Sets modified flag properly")
        main_window.log_message("   • Supports IDE and text file import lists")
        main_window.log_message("   • Smart file finding with case-insensitive search")
    
    return True

# Export functions
__all__ = [
    'import_via_function',
    'import_via_ide_function',
    'import_via_text_function',
    'integrate_import_via_functions'
]