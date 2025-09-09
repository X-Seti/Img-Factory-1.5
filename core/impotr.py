#this belongs in core/ impotr.py - Version: 14
# X-Seti - September08 2025 - IMG Factory 1.5 - Import Functions with RW Detection

"""
Import Functions - Clean import with RW version detection and highlighting
"""

import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# import_files_function
# import_multiple_files
# import_folder_contents
# _import_files_to_img
# _get_files_from_folder
# _parse_imported_files_for_rw
# _track_imported_files_with_highlighting
# _ask_rebuild_after_import
# integrate_import_functions

def import_files_function(main_window): #vers 14
    """Import files via file dialog with RW detection"""
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
        
        # Import the files
        success = import_multiple_files(main_window, file_paths)
        
        if success:
            _ask_rebuild_after_import(main_window)
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import error: {str(e)}")
        return False


def import_multiple_files(main_window, file_paths: List[str]) -> bool: #vers 14
    """Import multiple files with RW detection and highlighting"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Importing {len(file_paths)} files...")
        
        # Track existing files before import for highlighting
        existing_files = set()
        if hasattr(file_object, 'entries'):
            existing_files = {entry.name for entry in file_object.entries}
        
        # Import files to IMG
        imported_count = _import_files_to_img(main_window, file_object, file_paths)
        
        if imported_count > 0:
            # Get list of imported filenames
            imported_filenames = [os.path.basename(path) for path in file_paths[:imported_count]]
            
            # Parse imported files for RW versions
            _parse_imported_files_for_rw(main_window, file_object, imported_filenames)
            
            # Track files for highlighting with duplicate detection
            _track_imported_files_with_highlighting(main_window, file_object, imported_filenames, existing_files)
            
            # Refresh table with highlights and RW data
            _refresh_after_import(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Successfully imported {imported_count} files")
            
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No files were imported")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import multiple error: {str(e)}")
        return False


def import_folder_contents(main_window) -> bool: #vers 14
    """Import all files from a folder with RW detection"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Import Folder"):
            return False
        
        folder_path = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import",
            ""
        )
        
        if not folder_path:
            return False
        
        # Get files from folder
        file_paths = _get_files_from_folder(folder_path)
        
        if not file_paths:
            QMessageBox.information(main_window, "No Files", "No supported files found in selected folder")
            return False
        
        # Import the files
        success = import_multiple_files(main_window, file_paths)
        
        if success:
            _ask_rebuild_after_import(main_window)
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import folder error: {str(e)}")
        return False


def _import_files_to_img(main_window, img_file, file_paths: List[str]) -> int: #vers 14
    """Import files to IMG using existing add_entry method"""
    try:
        imported_count = 0
        
        # Create progress dialog
        progress = QProgressDialog("Importing files...", "Cancel", 0, len(file_paths), main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        for i, file_path in enumerate(file_paths):
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
                
                # Use existing add_entry method (no auto-save for batch)
                if hasattr(img_file, 'add_entry'):
                    success = img_file.add_entry(filename, file_data, auto_save=False)
                    if success:
                        imported_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"📁 Imported: {filename}")
                else:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("❌ IMG file doesn't support add_entry method")
                    break
                
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to import {os.path.basename(file_path)}: {str(e)}")
        
        progress.setValue(len(file_paths))
        progress.close()
        
        return imported_count
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import to IMG error: {str(e)}")
        return 0


def _get_files_from_folder(folder_path: str) -> List[str]: #vers 14
    """Get supported files from folder"""
    try:
        supported_extensions = {'.dff', '.txd', '.col', '.ipl', '.ide', '.dat', '.cfg'}
        file_paths = []
        
        for file_path in Path(folder_path).iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                file_paths.append(str(file_path))
        
        return sorted(file_paths)
        
    except Exception:
        return []


def _parse_imported_files_for_rw(main_window, img_file, imported_filenames: List[str]): #vers 2
    """Parse imported files for RW versions - FIXED: Non-blocking"""
    try:
        if not hasattr(img_file, 'entries'):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Parsing {len(imported_filenames)} imported files for RW versions...")
        
        # Only parse imported files, not all entries (to avoid UI freeze)
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
                    main_window.log_message(f"📊 Import breakdown: {len(new_files)} new, {len(replaced_files)} replaced")
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ Highlighting system not available")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Highlighting tracking error: {str(e)}")


def _refresh_after_import(main_window): #vers 2
    """Update table after import - Simple refresh without heavy RW detection"""
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
            main_window.log_message(f"⚠️ Error updating table after import: {str(e)}")


def _ask_rebuild_after_import(main_window): #vers 14
    """Ask user about rebuilding after import"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("💾 Files imported to memory. Use 'Save Entry' to save changes to disk.")
        
        # Show info message
        QMessageBox.information(main_window, "Import Complete",
            "Files imported to memory successfully!\n\n"
            "💾 Use the 'Save Entry' button to save changes to disk.\n"
            "⚠️ Changes will be lost if you reload without saving.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Ask rebuild error: {str(e)}")


def integrate_import_functions(main_window) -> bool: #vers 14
    """Integrate import functions into main window"""
    try:
        # Add import methods to main window
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_multiple_files = lambda file_paths: import_multiple_files(main_window, file_paths)
        main_window.import_folder_contents = lambda: import_folder_contents(main_window)
        
        # Add aliases that GUI might use
        main_window.import_files = main_window.import_files_function
        main_window.import_via_dialog = main_window.import_files_function
        main_window.import_folder = main_window.import_folder_contents
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Import functions integrated")
            main_window.log_message("   • RW version detection for imported files")
            main_window.log_message("   • Smart highlighting (new vs replaced)")
            main_window.log_message("   • Comprehensive table refresh")
            main_window.log_message("   • Uses existing add_entry method")
        
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