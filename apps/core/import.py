#this belongs in core/import.py - Version: 1
# X-Seti - November22 2025 - IMG Factory 1.5 - Core Import System

"""
Core Import System - Complete import functionality for IMG Factory 1.5
Handles all import operations with comprehensive validation, preview, and error handling
"""

import os
import struct
import math
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox

##Methods list -
# import_files_dialog
# import_files_with_list
# import_files_with_validation
# import_preview_dialog
# get_current_file_from_active_tab
# _get_import_preview_info
# _validate_import_files
# _show_import_preview
# _perform_import_operation
# _refresh_after_import
# integrate_import_system

def get_current_file_from_active_tab(main_window) -> Tuple[Optional[Any], Optional[str]]:
    """Get current file object and type from active tab - STANDARD FUNCTION"""
    try:
        # Try to get from tab system
        if hasattr(main_window, 'get_current_file_from_active_tab'):
            return main_window.get_current_file_from_active_tab()
        
        # Fallback to direct attributes
        file_object = getattr(main_window, 'file_object', None)
        file_type = getattr(main_window, 'file_type', None)
        
        return file_object, file_type
    except Exception:
        return None, None

def import_files_dialog(main_window) -> bool: #vers 1
    """Main import dialog for selecting files to import"""
    try:
        # Get current file context
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'IMG':
            QMessageBox.warning(main_window, "Import Error", "No IMG file is currently loaded")
            return False
        
        # Open file selection dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            "",
            "All Files (*.*);;DFF Files (*.dff);;TXD Files (*.txd);;COL Files (*.col);;DAT Files (*.dat);;IDE Files (*.ide)"
        )
        
        if not file_paths:
            return False
        
        # Show import preview
        return import_files_with_validation(main_window, file_paths)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import dialog error: {str(e)}")
        return False

def import_files_with_list(main_window, file_paths: List[str]) -> bool: #vers 1
    """Import files from a provided list - FOR USE BY import_via and other systems"""
    try:
        # Get current file context
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'IMG':
            QMessageBox.warning(main_window, "Import Error", "No IMG file is currently loaded")
            return False
        
        if not file_paths:
            return False
        
        # Validate files before import
        return import_files_with_validation(main_window, file_paths)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import with list error: {str(e)}")
        return False

def import_files_with_validation(main_window, file_paths: List[str]) -> bool: #vers 1
    """Validate and import files with preview"""
    try:
        # Get current file context
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'IMG':
            return False
        
        # Get preview information
        preview_info = _get_import_preview_info(file_object, file_paths)
        
        # Show preview dialog
        if _show_import_preview(main_window, preview_info, file_paths):
            # Perform import
            return _perform_import_operation(main_window, file_paths)
        else:
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import with validation error: {str(e)}")
        return False

def _get_import_preview_info(img_archive, file_paths: List[str]) -> Dict[str, Any]: #vers 1
    """Get preview information for import operation"""
    preview = {
        'total_files': len(file_paths),
        'valid_files': 0,
        'invalid_files': 0,
        'duplicate_files': 0,
        'total_size': 0,
        'sectors_needed': 0,
        'files': []
    }
    
    # Get existing entries for duplicate checking
    existing_entries = set()
    if hasattr(img_archive, 'entries') and img_archive.entries:
        for entry in img_archive.entries:
            if hasattr(entry, 'name'):
                existing_entries.add(entry.name.lower())
    
    for file_path in file_paths:
        is_valid, error_msg = _validate_import_file(file_path)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        file_info = {
            'path': file_path,
            'name': filename,
            'size': file_size,
            'valid': is_valid,
            'error': error_msg,
            'is_duplicate': filename.lower() in existing_entries
        }
        
        preview['files'].append(file_info)
        
        if is_valid:
            preview['valid_files'] += 1
            preview['total_size'] += file_size
        else:
            preview['invalid_files'] += 1
            
        if file_info['is_duplicate']:
            preview['duplicate_files'] += 1
    
    # Calculate sectors needed
    if preview['total_size'] > 0:
        preview['sectors_needed'] = math.ceil(preview['total_size'] / 2048)
    else:
        preview['sectors_needed'] = 0
    
    return preview

def _validate_import_file(file_path: str) -> Tuple[bool, str]: #vers 1
    """Validate a single file for import"""
    try:
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        # Check filename length (IMG standard)
        filename = os.path.basename(file_path)
        if len(filename) > 24:
            return False, f"Filename too long (max 24 chars): {filename}"
        
        # Check file size (reasonable limit)
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, f"File is empty: {filename}"
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            return False, f"File not readable: {str(e)}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def _show_import_preview(main_window, preview_info: Dict, file_paths: List[str]) -> bool: #vers 1
    """Show import preview dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Import Preview")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Preview information
        info_text = f"""
Import Summary:
- Total files: {preview_info['total_files']}
- Valid files: {preview_info['valid_files']}
- Invalid files: {preview_info['invalid_files']}
- Duplicate files: {preview_info['duplicate_files']}
- Total size: {preview_info['total_size']:,} bytes ({preview_info['total_size'] / 1024 / 1024:.2f} MB)
- Sectors needed: {preview_info['sectors_needed']}

Do you want to proceed with the import?
        """
        
        info_label = QLabel(info_text)
        layout.addWidget(info_label)
        
        # Show problematic files if any
        problematic_files = []
        for file_info in preview_info['files']:
            if not file_info['valid'] or file_info['is_duplicate']:
                status = "INVALID" if not file_info['valid'] else "DUPLICATE"
                problematic_files.append(f"{status}: {file_info['name']} - {file_info['error']}")
        
        if problematic_files:
            problem_label = QLabel("Problematic files:")
            layout.addWidget(problem_label)
            
            problem_list = QLabel("\n".join(problematic_files))
            problem_list.setWordWrap(True)
            layout.addWidget(problem_list)
        
        # Options
        overwrite_duplicates = QCheckBox("Overwrite duplicate files")
        layout.addWidget(overwrite_duplicates)
        
        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(import_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        # Show dialog
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return True
        else:
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import preview error: {str(e)}")
        return False

def _perform_import_operation(main_window, file_paths: List[str]) -> bool: #vers 1
    """Perform the actual import operation"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'IMG':
            return False
        
        success_count = 0
        fail_count = 0
        success_files = []
        fail_files = []
        
        for file_path in file_paths:
            try:
                is_valid, error_msg = _validate_import_file(file_path)
                if not is_valid:
                    fail_files.append((file_path, error_msg))
                    fail_count += 1
                    continue
                
                # Read file data
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Get entry name (basename)
                entry_name = os.path.basename(file_path)
                
                # Add to archive
                if hasattr(file_object, 'add_entry') and callable(getattr(file_object, 'add_entry')):
                    success = file_object.add_entry(entry_name, file_data)
                else:
                    # Fallback to add_entry_safe from methods
                    try:
                        from apps.methods.img_entry_operations import add_entry_safe
                        success = add_entry_safe(file_object, entry_name, file_data)
                    except:
                        success = False
                
                if success:
                    success_files.append(file_path)
                    success_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"Imported: {entry_name}")
                else:
                    fail_files.append((file_path, "Failed to add to archive"))
                    fail_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"Failed to import: {entry_name}")
                        
            except Exception as e:
                fail_files.append((file_path, str(e)))
                fail_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Error importing {file_path}: {str(e)}")
        
        # Log results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import completed: {success_count} success, {fail_count} failed")
            if success_count > 0:
                main_window.log_message(f"Successfully imported: {', '.join(os.path.basename(f) for f in success_files[:5])}{'...' if len(success_files) > 5 else ''}")
            if fail_count > 0:
                main_window.log_message(f"Failed imports: {len(fail_files)} files")
        
        # Refresh UI
        _refresh_after_import(main_window)
        
        # Show summary
        if hasattr(main_window, 'log_message'):
            if fail_count == 0:
                main_window.log_message(f"✅ Successfully imported {success_count} files")
            else:
                main_window.log_message(f"⚠️ Import completed: {success_count} success, {fail_count} failed")
        
        return success_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import operation error: {str(e)}")
        return False

def _refresh_after_import(main_window) -> None: #vers 1
    """Refresh UI after import operation"""
    try:
        # Try multiple refresh methods in order of preference
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        elif hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        elif hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
        elif hasattr(main_window, 'update_table_display'):
            main_window.update_table_display()
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Warning: Refresh after import failed: {str(e)}")

def integrate_import_system(main_window) -> bool: #vers 1
    """Integrate import system into main window"""
    try:
        # Add main import functions
        main_window.import_files_dialog = lambda: import_files_dialog(main_window)
        main_window.import_files_with_list = lambda file_paths: import_files_with_list(main_window, file_paths)
        main_window.import_files_with_validation = lambda file_paths: import_files_with_validation(main_window, file_paths)
        
        # Add aliases that GUI might use
        main_window.import_files = main_window.import_files_dialog
        main_window.import_multiple = main_window.import_files_with_list
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Core import system integrated")
            main_window.log_message("   • File import dialog")
            main_window.log_message("   • Import with validation")
            main_window.log_message("   • Import preview with statistics")
            main_window.log_message("   • Duplicate detection")
            main_window.log_message("   • Error handling and logging")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import system integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'import_files_dialog',
    'import_files_with_list', 
    'import_files_with_validation',
    'integrate_import_system',
    'get_current_file_from_active_tab'
]