#this belongs in core/ import_via.py - Version: 1
# X-Seti - August24 2025 - IMG Factory 1.5 - Import Via Functions

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox, QFileDialog, 
    QMessageBox, QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt

# Use EXACT same methods and dialogs as export_via.py
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab
from methods.ide_parser import IDEParser
from gui.ide_dialog import show_ide_dialog

# IMG_Editor core integration support
try:
    from components.img_integration import IMGArchive, IMGEntry, Import_Export
    IMG_INTEGRATION_AVAILABLE = True
except ImportError:
    IMG_INTEGRATION_AVAILABLE = False

##Methods list -
# import_via_function
# _import_img_via_ide
# _import_via_folder
# _import_via_textfile
# _show_import_destination_dialog
# _find_files_for_import
# _import_with_img_core
# _convert_to_img_archive
# integrate_import_via_functions

def import_via_function(main_window): #vers 1
    """Main import via function using EXACT same dialogs as export_via.py"""
    try:
        # EXACT same tab awareness validation as export_via.py
        if not validate_tab_before_operation(main_window, "Import Via"):
            return
        
        # Get current file type (same as export_via.py)
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG':
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first for import operations")
            return
        
        # Show import method selection dialog
        import_choice = _show_import_method_dialog(main_window)
        
        if import_choice == 'ide':
            _import_img_via_ide(main_window)
        elif import_choice == 'folder':
            _import_via_folder(main_window)
        elif import_choice == 'textfile':
            _import_via_textfile(main_window)
        else:
            return  # User cancelled
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via Error", f"Import via failed: {str(e)}")


def _import_img_via_ide(main_window): #vers 1
    """Import IMG files via IDE definitions using EXACT same dialog as export_via.py"""
    try:
        # EXACT same tab validation as export_via.py
        if not validate_tab_before_operation(main_window, "Import IMG via IDE"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # EXACT same IDE dialog as export_via.py (100% identical)
        if hasattr(main_window, 'log_message'):
            main_window.log_message("📥 Starting IMG Import Via IDE...")
        
        try:
            ide_parser = show_ide_dialog(main_window, "import")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error",
                               "IDE dialog system not available.\nPlease ensure all components are installed.")
            return
        
        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("IDE import cancelled by user")
            return
        
        # EXACT same IDE models extraction as export_via.py
        ide_models = getattr(ide_parser, 'models', {})
        if not ide_models:
            QMessageBox.information(main_window, "No IDE Entries", "No model entries found in IDE file")
            return
        
        # Show source folder selection dialog
        source_folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Source Folder Containing Files to Import",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not source_folder:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Import via IDE cancelled - no source folder selected")
            return
        
        # Find files to import based on IDE definitions
        files_to_import, files_found, files_missing = _find_files_for_import(source_folder, ide_models, main_window)
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", 
                f"No matching files found in:\n{source_folder}\n\nLooked for files matching IDE definitions")
            return
        
        # Show import confirmation dialog
        if not _show_import_confirmation_dialog(main_window, files_to_import, files_missing):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📥 Importing {len(files_to_import)} files based on IDE definitions")
        
        # Import files with IMG_Editor core support
        success = _import_with_img_core(main_window, file_object, files_to_import)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Import Complete", 
                f"Successfully imported {len(files_to_import)} files via IDE definitions!")
        else:
            QMessageBox.critical(main_window, "Import Failed", 
                "Failed to import files. Check debug log for details.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via IDE Error", f"Import via IDE failed: {str(e)}")


def _import_via_folder(main_window): #vers 1
    """Import entire folder contents"""
    try:
        # Validate current tab
        if not validate_tab_before_operation(main_window, "Import Folder"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # Choose source folder
        source_folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import All Files From",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not source_folder:
            return
        
        # Get all files from folder
        files_to_import = []
        folder_path = Path(source_folder)
        
        for file_path in folder_path.iterdir():
            if file_path.is_file():
                files_to_import.append(str(file_path))
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files", "No files found in selected folder")
            return
        
        # Show confirmation
        reply = QMessageBox.question(
            main_window,
            "Confirm Folder Import",
            f"Import all {len(files_to_import)} files from:\n{source_folder}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📁 Importing entire folder: {len(files_to_import)} files")
        
        # Import with IMG_Editor core
        success = _import_with_img_core(main_window, file_object, files_to_import)
        
        if success:
            # Refresh current tab
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Import Complete", 
                f"Successfully imported {len(files_to_import)} files from folder!")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import folder error: {str(e)}")
        QMessageBox.critical(main_window, "Import Folder Error", f"Import folder failed: {str(e)}")


def _import_via_textfile(main_window): #vers 1
    """Import files listed in text file"""
    try:
        # Validate current tab
        if not validate_tab_before_operation(main_window, "Import via Text File"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # Choose text file
        text_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select Text File with File List",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not text_file:
            return
        
        # Choose source directory
        source_folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Source Folder Containing Files Listed in Text File",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not source_folder:
            return
        
        # Parse text file
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                file_lines = f.readlines()
            
            files_to_find = []
            for line in file_lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip comments
                    files_to_find.append(line)
            
            if not files_to_find:
                QMessageBox.information(main_window, "No Files Listed", "No valid file names found in text file")
                return
                
        except Exception as e:
            QMessageBox.critical(main_window, "File Read Error", f"Error reading text file: {str(e)}")
            return
        
        # Find actual files
        files_to_import = []
        files_missing = []
        
        for file_name in files_to_find:
            file_path = os.path.join(source_folder, file_name)
            if os.path.exists(file_path):
                files_to_import.append(file_path)
            else:
                files_missing.append(file_name)
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", 
                f"No files from the text list were found in:\n{source_folder}")
            return
        
        # Show confirmation
        if not _show_import_confirmation_dialog(main_window, files_to_import, files_missing):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📄 Importing {len(files_to_import)} files from text list")
        
        # Import with IMG_Editor core
        success = _import_with_img_core(main_window, file_object, files_to_import)
        
        if success:
            # Refresh current tab
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Import Complete", 
                f"Successfully imported {len(files_to_import)} files from text list!")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import via text file error: {str(e)}")
        QMessageBox.critical(main_window, "Import via Text File Error", f"Import via text file failed: {str(e)}")


def _show_import_method_dialog(main_window) -> Optional[str]: #vers 1
    """Show import method selection dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Import Method")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header = QLabel("Select Import Method:")
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 15px;")
        layout.addWidget(header)
        
        # Method buttons
        ide_btn = QPushButton("📋 Import via IDE File")
        ide_btn.setToolTip("Import files based on IDE definitions")
        ide_btn.setMinimumHeight(40)
        
        folder_btn = QPushButton("📁 Import Entire Folder")
        folder_btn.setToolTip("Import all files from a selected folder")
        folder_btn.setMinimumHeight(40)
        
        textfile_btn = QPushButton("📄 Import via Text File List")
        textfile_btn.setToolTip("Import files listed in a text file")
        textfile_btn.setMinimumHeight(40)
        
        layout.addWidget(ide_btn)
        layout.addWidget(folder_btn)
        layout.addWidget(textfile_btn)
        
        layout.addWidget(QLabel())  # Spacer
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        layout.addWidget(cancel_btn)
        
        # Results
        choice = None
        
        def choose_ide():
            nonlocal choice
            choice = 'ide'
            dialog.accept()
        
        def choose_folder():
            nonlocal choice
            choice = 'folder'
            dialog.accept()
        
        def choose_textfile():
            nonlocal choice
            choice = 'textfile'
            dialog.accept()
        
        ide_btn.clicked.connect(choose_ide)
        folder_btn.clicked.connect(choose_folder)
        textfile_btn.clicked.connect(choose_textfile)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return choice
        
        return None
        
    except Exception:
        return None


def _find_files_for_import(source_folder: str, ide_models: Dict, main_window) -> Tuple[List[str], List[str], List[str]]: #vers 1
    """Find files to import based on IDE definitions - EXACT same format as export_via.py"""
    try:
        files_to_import = []
        files_found = []
        files_missing = []
        
        # Extract filenames from IDE models dictionary (EXACT methods/ide_parser.py format)
        files_to_find = []
        for model_id, model_data in ide_models.items():
            model_name = model_data.get('name', '')
            if model_name:
                files_to_find.extend([
                    f"{model_name}.dff",
                    f"{model_data.get('txd', model_name)}.txd"
                ])

        # Find actual files in source folder
        for file_to_find in files_to_find:
            file_path = os.path.join(source_folder, file_to_find)
            
            if os.path.exists(file_path):
                files_to_import.append(file_path)
                files_found.append(file_to_find)
            else:
                files_missing.append(file_to_find)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Found {len(files_found)} files, {len(files_missing)} missing from IDE definitions")
        
        return files_to_import, files_found, files_missing
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error finding files for import: {str(e)}")
        return [], [], []


def _show_import_confirmation_dialog(main_window, files_to_import: List[str], files_missing: List[str]) -> bool: #vers 1
    """Show import confirmation dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Confirm Import")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_text = f"Import {len(files_to_import)} files?"
        if files_missing:
            header_text += f" ({len(files_missing)} files not found)"
        
        header = QLabel(header_text)
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # File list
        file_list = QTextEdit()
        file_list.setReadOnly(True)
        file_list.setMaximumHeight(200)
        
        file_text = "Files to import:\n"
        for file_path in files_to_import[:20]:  # Show first 20
            file_name = os.path.basename(file_path)
            file_text += f"✅ {file_name}\n"
        
        if len(files_to_import) > 20:
            file_text += f"... and {len(files_to_import) - 20} more files\n"
        
        if files_missing:
            file_text += f"\nMissing files:\n"
            for missing_file in files_missing[:10]:  # Show first 10
                file_text += f"❌ {missing_file}\n"
            if len(files_missing) > 10:
                file_text += f"... and {len(files_missing) - 10} more missing\n"
        
        file_list.setPlainText(file_text)
        layout.addWidget(file_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Files")
        import_btn.setDefault(True)
        cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        import_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        return dialog.exec() == QDialog.DialogCode.Accepted
        
    except Exception:
        return False


def _import_with_img_core(main_window, file_object, files_to_import: List[str]) -> bool: #vers 1
    """Import files using IMG_Editor core for reliability"""
    try:
        # Convert to IMG_Editor archive if available
        if IMG_INTEGRATION_AVAILABLE:
            img_archive = _convert_to_img_archive(file_object, main_window)
            if img_archive:
                return _import_with_img_archive(main_window, img_archive, files_to_import)
        
        # Fallback to basic import
        return _import_with_basic_method(main_window, file_object, files_to_import)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Import with core error: {str(e)}")
        return False


def _import_with_img_archive(main_window, img_archive, files_to_import: List[str]) -> bool: #vers 1
    """Import using IMG_Editor archive"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Using IMG_Editor core for reliable import")
        
        # Create progress dialog - NO THREADING to avoid crashes
        progress_dialog = QProgressDialog(
            "Preparing import...",
            "Cancel",
            0,
            len(files_to_import),
            main_window
        )
        progress_dialog.setWindowTitle("Importing Files")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        imported_count = 0
        failed_count = 0
        
        try:
            for i, file_path in enumerate(files_to_import):
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
            if imported_count > 0:
                main_window.log_message("💾 Remember to rebuild IMG to save changes")
        
        return imported_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG archive import error: {str(e)}")
        return False


def _import_with_basic_method(main_window, file_object, files_to_import: List[str]) -> bool: #vers 1
    """Fallback import method"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("⚠️ Using fallback import method")
        
        # Use the existing import method from core/import.py
        try:
            from core.impotr import import_multiple_files
            return import_multiple_files(main_window, files_to_import)
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No import method available")
            return False
        
    except Exception:
        return False


def _convert_to_img_archive(file_object, main_window):
    """Convert file object to IMG_Editor archive format"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            return None
        
        # If already IMG_Editor format, return as-is
        if isinstance(file_object, IMGArchive):
            return file_object
        
        # Load IMG file using IMG_Editor
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Create and load IMG_Editor archive
        archive = IMGArchive()
        if archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                entry_count = len(archive.entries) if archive.entries else 0
                main_window.log_message(f"✅ Converted to IMG archive format: {entry_count} entries")
            return archive
        
        return None
        
    except Exception:
        return None


def integrate_import_via_functions(main_window) -> bool: #vers 1
    """Integrate import via functions into main window"""
    try:
        # Add main import via function
        main_window.import_via_function = lambda: import_via_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.import_via = main_window.import_via_function
        main_window.import_files_via = main_window.import_via_function
        main_window.import_via_ide = main_window.import_via_function
        main_window.import_via_dialog = main_window.import_via_function
        
        if hasattr(main_window, 'log_message'):
            integration_msg = "✅ Import via functions integrated with tab awareness"
            if IMG_INTEGRATION_AVAILABLE:
                integration_msg += " + IMG_Editor core"
            main_window.log_message(integration_msg)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate import via functions: {str(e)}")
        return False


# Export functions
__all__ = [
    'import_via_function',
    'integrate_import_via_functions'
]
