#this belongs in core/ impotr.py - Version: 1
# X-Seti - August24 2025 - IMG Factory 1.5 - Import Function Integration

import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system (this works!)
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# import_files_function
# import_multiple_files
# import_folder_contents
# _import_using_img_editor_core
# _convert_img_to_archive
# _create_import_progress_dialog
# _get_import_file_list
# integrate_import_functions

def import_files_function(main_window): #vers 1
    """Import files using IMG_Editor core - TAB AWARE"""
    try:
        # Use same tab validation as rebuild.py
        if not validate_tab_before_operation(main_window, "Import Files"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Choose files to import
        file_paths, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            "",
            "All Files (*.*)"
        )
        
        if not file_paths:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Import cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📥 Importing {len(file_paths)} files")
        
        # Use IMG_Editor core for import
        success = _import_using_img_editor_core(file_object, file_paths, main_window)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Import Complete", 
                f"Successfully imported {len(file_paths)} files")
        else:
            QMessageBox.critical(main_window, "Import Failed", 
                "Failed to import files. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import files error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import error: {str(e)}")
        return False


def import_multiple_files(main_window, file_paths: List[str]) -> bool: #vers 1
    """Import multiple files programmatically"""
    try:
        if not validate_tab_before_operation(main_window, "Import Multiple Files"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if not file_paths:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📥 Importing {len(file_paths)} files programmatically")
        
        return _import_using_img_editor_core(file_object, file_paths, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import multiple error: {str(e)}")
        return False


def import_folder_contents(main_window): #vers 1
    """Import entire folder contents using IMG_Editor core"""
    try:
        # Use same tab validation
        if not validate_tab_before_operation(main_window, "Import Folder"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Choose folder to import
        folder_path = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Import folder cancelled by user")
            return False
        
        # Get list of files in folder
        file_paths = _get_import_file_list(folder_path)
        
        if not file_paths:
            QMessageBox.information(main_window, "No Files", "No files found in selected folder")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📥 Importing folder contents: {len(file_paths)} files from {folder_path}")
        
        # Use IMG_Editor core for import
        success = _import_using_img_editor_core(file_object, file_paths, main_window)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Import Complete", 
                f"Successfully imported {len(file_paths)} files from folder")
        else:
            QMessageBox.critical(main_window, "Import Failed", 
                "Failed to import folder contents. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import folder error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import error: {str(e)}")
        return False


def _import_using_img_editor_core(file_object, file_paths: List[str], main_window) -> bool: #vers 1
    """CORE FUNCTION: Import using working IMG_Editor Import_Export class"""
    try:
        # Import the working IMG_Editor core classes
        try:
            from IMG_Editor.core.Core import IMGArchive, IMGEntry
            from IMG_Editor.core.Import_Export import Import_Export
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG_Editor core not available - cannot import")
            return False
        
        # Convert to IMG_Editor archive format if needed
        img_archive = _convert_img_to_archive(file_object, main_window)
        if not img_archive:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to convert IMG to archive format")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Using IMG_Editor Import_Export.import_file")
        
        # Create progress dialog
        progress_dialog = _create_import_progress_dialog(main_window, len(file_paths))
        
        imported_count = 0
        failed_count = 0
        
        try:
            for i, file_path in enumerate(file_paths):
                # Update progress
                progress_dialog.setValue(i)
                file_name = os.path.basename(file_path)
                progress_dialog.setLabelText(f"Importing: {file_name}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("Import cancelled by user")
                    break
                
                # Use IMG_Editor Import_Export.import_file
                try:
                    imported_entry = Import_Export.import_file(img_archive, file_path, file_name)
                    
                    if imported_entry:
                        imported_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"✅ Imported: {file_name}")
                    else:
                        failed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Failed to import: {file_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Import error for {file_name}: {str(e)}")
            
        finally:
            progress_dialog.close()
        
        # Report results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Import complete: {imported_count} success, {failed_count} failed")
        
        # If successful imports, need to save/rebuild IMG
        if imported_count > 0:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("💾 Import successful - remember to rebuild IMG to save changes")
        
        return imported_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core import error: {str(e)}")
        return False


def _convert_img_to_archive(file_object, main_window) -> Optional[object]: #vers 1
    """Convert IMG file object to IMG_Editor IMGArchive format"""
    try:
        from IMG_Editor.core.Core import IMGArchive, IMGEntry
        
        # If already IMG_Editor format, return as-is
        if isinstance(file_object, IMGArchive):
            return file_object
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Converting IMG to IMG_Editor archive format for import")
        
        # Load IMG file using IMG_Editor
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No valid file path found")
            return None
        
        # Create and load IMG_Editor archive
        archive = IMGArchive()
        if not archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to load IMG file with IMG_Editor")
            return None
        
        if hasattr(main_window, 'log_message'):
            entry_count = len(archive.entries) if archive.entries else 0
            main_window.log_message(f"✅ Loaded IMG with {entry_count} entries for import")
        
        return archive
        
    except ImportError:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ IMG_Editor core not available")
        return None
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Archive conversion error: {str(e)}")
        return None


def _create_import_progress_dialog(main_window, total_files) -> QProgressDialog: #vers 1
    """Create progress dialog for import operation"""
    try:
        progress_dialog = QProgressDialog(
            "Preparing import...",
            "Cancel",
            0,
            total_files,
            main_window
        )
        
        progress_dialog.setWindowTitle("Importing Files")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        return progress_dialog
        
    except Exception:
        # Fallback: create minimal progress dialog
        progress_dialog = QProgressDialog(main_window)
        progress_dialog.setRange(0, total_files)
        return progress_dialog


def _get_import_file_list(folder_path: str) -> List[str]: #vers 1
    """Get list of files to import from folder"""
    try:
        file_paths = []
        folder = Path(folder_path)
        
        for file_path in folder.iterdir():
            if file_path.is_file():
                file_paths.append(str(file_path))
        
        # Sort for consistent import order
        file_paths.sort()
        
        return file_paths
        
    except Exception:
        return []


def integrate_import_functions(main_window) -> bool: #vers 1
    """Integrate IMG_Editor core import functions - NEW"""
    try:
        # Main import functions with IMG_Editor core
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_multiple_files = lambda file_paths: import_multiple_files(main_window, file_paths)
        main_window.import_folder_contents = lambda: import_folder_contents(main_window)
        
        # Add aliases that GUI might use
        main_window.import_files = main_window.import_files_function
        main_window.import_via_dialog = main_window.import_files_function
        main_window.import_folder = main_window.import_folder_contents
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG_Editor core import functions integrated with TAB AWARENESS")
            main_window.log_message("   • Uses Import_Export.import_file for reliable import")
            main_window.log_message("   • Supports file selection, multiple files, and folder import")
            main_window.log_message("   • Remember to rebuild IMG after import to save changes")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import integration failed: {str(e)}")
        return False


# Export only the essential functions
__all__ = [
    'import_files_function',
    'import_multiple_files',
    'import_folder_contents',
    'integrate_import_functions'
]
