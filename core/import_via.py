#this belongs in core/ import_via.py - Version: 14
# X-Seti - September08 2025 - IMG Factory 1.5 - Import Via Functions with RW Detection

"""
Import Via Functions - Import via IDE/text files with RW version detection
"""

import os
from pathlib import Path
from typing import List, Optional, Set
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# import_via_function
# import_via_ide_function
# import_via_text_function
# _import_files_via_ide
# _import_files_via_text
# _parse_text_file_list
# _find_files_for_import
# _parse_imported_files_for_rw
# _track_imported_files_with_highlighting
# _refresh_after_import_via
# integrate_import_via_functions

def import_via_function(main_window): #vers 14
    """Import via dialog - choose IDE or text file"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Import Via"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Ask user what type of import
        reply = QMessageBox.question(
            main_window,
            "Import Via",
            "Choose import method:\n\n"
            "• Yes = Import via IDE file\n"
            "• No = Import via text file list\n"
            "• Cancel = Cancel import",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            return import_via_ide_function(main_window)
        elif reply == QMessageBox.StandardButton.No:
            return import_via_text_function(main_window)
        else:
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via Error", f"Import via error: {str(e)}")
        return False


def import_via_ide_function(main_window) -> bool: #vers 14
    """Import files based on IDE definitions with RW detection"""
    try:
        # File dialog for IDE file
        ide_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File",
            "",
            "IDE Files (*.ide);;All Files (*.*)"
        )
        
        if not ide_path:
            return False
        
        # Ask for base directory where files are located
        base_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Base Directory (where model files are located)",
            ""
        )
        
        if not base_dir:
            return False
        
        # Import files via IDE
        success = _import_files_via_ide(main_window, ide_path, base_dir)
        
        if success:
            QMessageBox.information(main_window, "Import Via Complete",
                "Files imported via IDE successfully!\n\n"
                "💾 Use the 'Save Entry' button to save changes to disk.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        return False


def import_via_text_function(main_window) -> bool: #vers 14
    """Import files from text file list with RW detection"""
    try:
        # File dialog for text file
        text_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select Text File List",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not text_path:
            return False
        
        # Ask for base directory where files are located
        base_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Base Directory (where files are located)",
            ""
        )
        
        if not base_dir:
            return False
        
        # Import files via text list
        success = _import_files_via_text(main_window, text_path, base_dir)
        
        if success:
            QMessageBox.information(main_window, "Import Via Complete",
                "Files imported via text list successfully!\n\n"
                "💾 Use the 'Save Entry' button to save changes to disk.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via text error: {str(e)}")
        return False


def _import_files_via_ide(main_window, ide_path: str, base_dir: str) -> bool: #vers 14
    """Import files based on IDE definitions with RW detection"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        # Parse IDE file
        try:
            from methods.ide_parser_functions import parse_ide_file
            ide_parser = parse_ide_file(ide_path)
            if ide_parser:
                ide_models = ide_parser.models
            else:
                ide_models = None
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IDE parser not available")
            return False
        
        if not ide_models:
            QMessageBox.information(main_window, "No Models", "No model definitions found in IDE file")
            return False
        
        # Track existing files before import
        existing_files = set()
        if hasattr(file_object, 'entries'):
            existing_files = {entry.name for entry in file_object.entries}
        
        # Find files to import based on IDE models
        files_to_import = _find_files_for_import(ide_models, base_dir)
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", 
                "No files found matching IDE definitions in the specified directory")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Found {len(files_to_import)} files from IDE definitions")
        
        # Import the files
        imported_count = 0
        imported_filenames = []
        
        # Create progress dialog
        progress = QProgressDialog("Importing via IDE...", "Cancel", 0, len(files_to_import), main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        for i, file_path in enumerate(files_to_import):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Importing {os.path.basename(file_path)}...")
            QApplication.processEvents()
            
            try:
                # Read file data
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                filename = os.path.basename(file_path)
                
                # Use existing add_entry method
                if hasattr(file_object, 'add_entry'):
                    success = file_object.add_entry(filename, file_data, auto_save=False)
                    if success:
                        imported_count += 1
                        imported_filenames.append(filename)
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"📁 Imported via IDE: {filename}")
                
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to import {os.path.basename(file_path)}: {str(e)}")
        
        progress.setValue(len(files_to_import))
        progress.close()
        
        if imported_count > 0:
            # Parse imported files for RW versions
            _parse_imported_files_for_rw(main_window, file_object, imported_filenames)
            
            # Track files for highlighting
            _track_imported_files_with_highlighting(main_window, file_object, imported_filenames, existing_files)
            
            # Refresh after import
            _refresh_after_import_via(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Successfully imported {imported_count} files via IDE")
            
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No files were imported via IDE")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        return False


def _import_files_via_text(main_window, text_path: str, base_dir: str) -> bool: #vers 14
    """Import files from text file list with RW detection"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        # Parse text file for file list
        file_list = _parse_text_file_list(text_path)
        
        if not file_list:
            QMessageBox.information(main_window, "No Files", "No valid file names found in text file")
            return False
        
        # Track existing files before import
        existing_files = set()
        if hasattr(file_object, 'entries'):
            existing_files = {entry.name for entry in file_object.entries}
        
        # Find actual files in base directory
        files_to_import = []
        for filename in file_list:
            file_path = os.path.join(base_dir, filename)
            if os.path.exists(file_path):
                files_to_import.append(file_path)
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚠️ File not found: {filename}")
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", 
                "No files from text list found in the specified directory")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Found {len(files_to_import)} files from text list")
        
        # Import the files
        imported_count = 0
        imported_filenames = []
        
        # Create progress dialog
        progress = QProgressDialog("Importing via text list...", "Cancel", 0, len(files_to_import), main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        for i, file_path in enumerate(files_to_import):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Importing {os.path.basename(file_path)}...")
            QApplication.processEvents()
            
            try:
                # Read file data
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                filename = os.path.basename(file_path)
                
                # Use existing add_entry method
                if hasattr(file_object, 'add_entry'):
                    success = file_object.add_entry(filename, file_data, auto_save=False)
                    if success:
                        imported_count += 1
                        imported_filenames.append(filename)
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"📁 Imported via text: {filename}")
                
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to import {os.path.basename(file_path)}: {str(e)}")
        
        progress.setValue(len(files_to_import))
        progress.close()
        
        if imported_count > 0:
            # Parse imported files for RW versions
            _parse_imported_files_for_rw(main_window, file_object, imported_filenames)
            
            # Track files for highlighting
            _track_imported_files_with_highlighting(main_window, file_object, imported_filenames, existing_files)
            
            # Refresh after import
            _refresh_after_import_via(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Successfully imported {imported_count} files via text list")
            
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No files were imported via text list")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via text error: {str(e)}")
        return False


def _parse_text_file_list(text_path: str) -> List[str]: #vers 14
    """Parse text file for list of filenames"""
    try:
        file_list = []
        
        with open(text_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    # Smart parsing - extract filename if it's a path
                    if '/' in line or '\\' in line:
                        filename = os.path.basename(line)
                    else:
                        filename = line
                    
                    # Validate filename
                    if filename and '.' in filename:
                        file_list.append(filename)
        
        return file_list
        
    except Exception:
        return []


def _find_files_for_import(ide_models: dict, base_dir: str) -> List[str]: #vers 14
    """Find files to import based on IDE model definitions"""
    try:
        files_to_import = []
        
        for model_id, model_data in ide_models.items():
            # Look for DFF and TXD files for each model
            model_name = model_data.get('name', model_id)
            
            # Common file patterns for GTA models
            potential_files = [
                f"{model_name}.dff",
                f"{model_name}.txd",
                f"{model_name}.col"
            ]
            
            for filename in potential_files:
                file_path = os.path.join(base_dir, filename)
                if os.path.exists(file_path):
                    files_to_import.append(file_path)
        
        return files_to_import
        
    except Exception:
        return []


def _parse_imported_files_for_rw(main_window, img_file, imported_filenames: List[str]): #vers 1
    """Parse imported files for RW versions - NEW FUNCTION"""
    try:
        if not hasattr(img_file, 'entries'):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Parsing {len(imported_filenames)} imported files for RW versions...")
        
        # Find imported entries and parse for RW
        parsed_count = 0
        for entry in img_file.entries:
            if entry.name in imported_filenames:
                try:
                    # Use existing RW detection method
                    if hasattr(entry, 'detect_file_type_and_version'):
                        entry.detect_file_type_and_version()
                        parsed_count += 1
                except Exception as e:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ RW parse error for {entry.name}: {str(e)}")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Parsed RW versions for {parsed_count} imported files")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ RW parsing error: {str(e)}")


def _track_imported_files_with_highlighting(main_window, img_file, imported_filenames: List[str], existing_files: set): #vers 1
    """Track imported files for highlighting with duplicate detection - NEW FUNCTION"""
    try:
        # Categorize files as new or replaced
        new_files = []
        replaced_files = []
        
        for filename in imported_filenames:
            if filename in existing_files:
                replaced_files.append(filename)  # File already existed
            else:
                new_files.append(filename)       # Truly new file
        
        # Track with highlighting system if available
        try:
            if not hasattr(main_window, '_import_highlight_manager'):
                from methods.import_highlight_system import integrate_import_highlighting
                integrate_import_highlighting(main_window)
            
            if hasattr(main_window, '_import_highlight_manager'):
                highlight_manager = main_window._import_highlight_manager
                highlight_manager.track_multiple_files(new_files, replaced_files)
                
                # Log the breakdown
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"📊 Import via breakdown: {len(new_files)} new, {len(replaced_files)} replaced")
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ Highlighting system not available")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Highlighting tracking error: {str(e)}")


def _refresh_after_import_via(main_window): #vers 2
    """Update table after import via - Simple refresh without heavy RW detection"""
    try:
        # Update table to show current entries including newly imported ones
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            
            # Get current IMG file
            if hasattr(main_window, 'current_img') and main_window.current_img:
                img_file = main_window.current_img
                
                if hasattr(img_file, 'entries'):
                    # Clear table and repopulate with basic info
                    table.setRowCount(len(img_file.entries))
                    
                    # Get highlight manager for new/replaced files
                    highlight_manager = getattr(main_window, '_import_highlight_manager', None)
                    
                    # Simple population without heavy RW detection
                    for row, entry in enumerate(img_file.entries):
                        # Name column (with highlighting if available)
                        name_item = QTableWidgetItem(entry.name)
                        if highlight_manager:
                            is_highlighted, is_replaced = highlight_manager.is_file_highlighted(entry.name)
                            if is_highlighted:
                                if is_replaced:
                                    name_item.setBackground(QBrush(QColor(255, 255, 200)))  # Yellow for replaced
                                else:
                                    name_item.setBackground(QBrush(QColor(200, 255, 200)))  # Green for new
                        table.setItem(row, 0, name_item)
                        
                        # Type column (from extension only)
                        file_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else 'Unknown'
                        type_item = QTableWidgetItem(file_ext)
                        table.setItem(row, 1, type_item)
                        
                        # Offset column
                        offset_text = f"0x{getattr(entry, 'offset', 0):08X}"
                        offset_item = QTableWidgetItem(offset_text)
                        table.setItem(row, 2, offset_item)
                        
                        # Size column
                        size = getattr(entry, 'size', 0)
                        size_item = QTableWidgetItem(str(size))
                        table.setItem(row, 3, size_item)
                        
                        # RW Version column (use detected data if available)
                        if table.columnCount() > 5:
                            rw_version = getattr(entry, 'rw_version_name', 'Unknown')
                            rw_item = QTableWidgetItem(rw_version)
                            table.setItem(row, 5, rw_item)
                    
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"🔄 Table updated: {len(img_file.entries)} entries (with highlighting)")
        
        # Update file list window
        if hasattr(main_window, 'refresh_file_list'):
            main_window.refresh_file_list()
        
        # Update UI for loaded IMG
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error updating table after import via: {str(e)}")


def integrate_import_via_functions(main_window) -> bool: #vers 14
    """Integrate import via functions into main window"""
    try:
        # Add import via methods to main window
        main_window.import_via_function = lambda: import_via_function(main_window)
        main_window.import_via_ide_function = lambda: import_via_ide_function(main_window)
        main_window.import_via_text_function = lambda: import_via_text_function(main_window)
        
        # Add aliases that GUI might use
        main_window.import_via = main_window.import_via_function
        main_window.import_via_ide = main_window.import_via_ide_function
        main_window.import_via_text = main_window.import_via_text_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Import Via functions integrated")
            main_window.log_message("   • IDE file import support")
            main_window.log_message("   • Text file list import support")
            main_window.log_message("   • RW version detection for imported files")
            main_window.log_message("   • Smart highlighting (new vs replaced)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import Via integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'import_via_function',
    'import_via_ide_function', 
    'import_via_text_function',
    'integrate_import_via_functions'
]