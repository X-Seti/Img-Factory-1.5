#this belongs in core/importer.py - Version: 5
# X-Seti - July15 2025 - Img Factory 1.5
# Import functions for IMG Factory

import os
import shutil
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QProgressBar, QMessageBox, QFileDialog, QGroupBox, QGridLayout, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from components.img_core_classes import format_file_size

##Methods list
# import_files
# import_files_function'
# import_via_function'
# import_via_ide_file'
# import_from_folder'
# get_selected_entries'
# integrate_import_functions


def get_selected_entries(main_window): #vers 2
    """Get currently selected entries from the table"""
    try:
        selected_entries = []
        
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            for row in selected_rows:
                if hasattr(main_window, 'current_img') and main_window.current_img and row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])
        
        return selected_entries
        
    except Exception:
        return []


class ImportOptionsDialog(QDialog):
    """Import options dialog"""
    
    def __init__(self, main_window, files, import_type="files"): #vers 1
        super().__init__(main_window)
        self.main_window = main_window
        self.files = files
        self.import_type = import_type
        self.setup_ui()
        
    def setup_ui(self): #vers 2
        self.setWindowTitle(f"Import {self.import_type.title()}")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # File list
        files_group = QGroupBox(f"Files to Import ({len(self.files)})")
        files_layout = QVBoxLayout()
        
        file_list = QTextEdit()
        file_list.setMaximumHeight(150)
        file_list.setPlainText('\n'.join([os.path.basename(f) for f in self.files]))
        file_list.setReadOnly(True)
        files_layout.addWidget(file_list)
        
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()
        
        self.replace_existing = QCheckBox("Replace existing files")
        self.replace_existing.setChecked(True)
        options_layout.addWidget(self.replace_existing)
        
        self.create_backup = QCheckBox("Create backup before import")
        self.create_backup.setChecked(True)
        options_layout.addWidget(self.create_backup)
        
        self.validate_files = QCheckBox("Validate file formats")
        self.validate_files.setChecked(True)
        options_layout.addWidget(self.validate_files)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.start_import)
        button_layout.addWidget(import_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def start_import(self): #vers 2
        """Start the import process"""
        try:
            # Create backup if requested
            if self.create_backup.isChecked():
                self.create_backup_file()
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(self.files))
            
            # Start import thread
            self.import_thread = ImportThread(
                self.main_window,
                self.files,
                self.replace_existing.isChecked(),
                self.validate_files.isChecked()
            )
            self.import_thread.progress.connect(self.progress_bar.setValue)
            self.import_thread.finished.connect(self.import_finished)
            self.import_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to start import: {str(e)}")
    
    def create_backup_file(self): #vers 2
        """Create backup of current IMG file"""
        try:
            if hasattr(self.main_window, 'current_img') and hasattr(self.main_window.current_img, 'file_path'):
                img_path = self.main_window.current_img.file_path
                backup_path = img_path + '.backup'
                shutil.copy2(img_path, backup_path)
                self.main_window.log_message(f"✅ Backup created: {backup_path}")
        except Exception as e:
            self.main_window.log_message(f"❌ Backup failed: {str(e)}")

    def import_finished(self, success, message): #vers 1
        """Handle import completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Import Complete", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Import Failed", message)


class ImportThread(QThread):
    """Background import thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, main_window, files, replace_existing=True, validate_files=True): #vers 1
        super().__init__()
        self.main_window = main_window
        self.files = files
        self.replace_existing = replace_existing
        self.validate_files = validate_files
        
    def run(self): #vers 2
        try:
            imported_count = 0
            failed_count = 0
            
            for i, file_path in enumerate(self.files):
                if self.import_file(file_path):
                    imported_count += 1
                else:
                    failed_count += 1
                
                self.progress.emit(i + 1)
            
            # Refresh table
            if hasattr(self.main_window, 'refresh_table'):
                self.main_window.refresh_table()
            
            if failed_count == 0:
                self.finished.emit(True, f"Successfully imported {imported_count} files.")
            else:
                self.finished.emit(True, f"Imported {imported_count} files. {failed_count} files failed.")
                
        except Exception as e:
            self.finished.emit(False, f"Import error: {str(e)}")
    
    def import_file(self, file_path): #vers 1
        """Import a single file"""
        try:
            filename = os.path.basename(file_path)
            
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Validate file if requested
            if self.validate_files:
                if len(file_data) == 0:
                    return False
            
            # Method 1: Use IMG's add_entry method
            if hasattr(self.main_window.current_img, 'add_entry'):
                try:
                    if self.main_window.current_img.add_entry(filename, file_data):
                        return True
                except Exception:
                    pass
            
            # Method 2: Use IMG's import_file method
            if hasattr(self.main_window.current_img, 'import_file'):
                try:
                    if self.main_window.current_img.import_file(file_path):
                        return True
                except Exception:
                    pass
            
            # Method 3: Create entry directly
            if hasattr(self.main_window.current_img, 'entries'):
                try:
                    # Remove existing entry if replacing
                    if self.replace_existing:
                        self.main_window.current_img.entries = [
                            e for e in self.main_window.current_img.entries 
                            if getattr(e, 'name', '').lower() != filename.lower()
                        ]
                    
                    # Create new entry
                    new_entry = type('Entry', (), {
                        'name': filename,
                        'data': file_data,
                        'size': len(file_data),
                        'get_data': lambda: file_data
                    })()
                    
                    self.main_window.current_img.entries.append(new_entry)
                    return True
                except Exception:
                    pass
            
            return False
            
        except Exception:
            return False


    def import_files(self): #vers 3
        """Import files into current IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Import Files", "",
                "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
            )

            if file_paths:
                self.log_message(f"Importing {len(file_paths)} files...")

                # Show progress - CHECK if method exists first
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Importing files...")

                imported_count = 0
                for i, file_path in enumerate(file_paths):
                    progress = int((i + 1) * 100 / len(file_paths))
                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Importing {os.path.basename(file_path)}")

                    # Check if IMG has import_file method
                    if hasattr(self.current_img, 'import_file'):
                        if self.current_img.import_file(file_path):
                            imported_count += 1
                            self.log_message(f"Imported: {os.path.basename(file_path)}")
                    else:
                        self.log_message(f"❌ IMG import_file method not available")
                        break

                # Refresh table
                if hasattr(self, '_populate_img_table'):
                    self._populate_img_table(self.current_img)
                else:
                    populate_img_table(self.gui_layout.table, self.current_img)

                self.log_message(f"Import complete: {imported_count}/{len(file_paths)} files imported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Import complete")
                if hasattr(self.gui_layout, 'update_img_info'):
                    self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")

                QMessageBox.information(self, "Import Complete",
                                      f"Imported {imported_count} of {len(file_paths)} files")

        except Exception as e:
            error_msg = f"Error importing files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Import error")
            QMessageBox.critical(self, "Import Error", error_msg)


def import_files_function(main_window): #vers 3
    """Import files into IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get files to import
        files, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            "",
            "All Files (*)"
        )
        
        if not files:
            return

        main_window.log_message(f"Import Files: {len(files)} files selected")
        
        # Show import dialog
        dialog = ImportOptionsDialog(main_window, files, "files")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Import error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import failed: {str(e)}")


def import_via_function(main_window): #vers 2
    """Import files via IDE file or folder"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Choice dialog
        reply = QMessageBox.question(
            main_window,
            "Import Via",
            "Import from:\n• Yes = IDE File\n• No = Folder",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        elif reply == QMessageBox.StandardButton.Yes:
            # Import via IDE file
            import_via_ide_file(main_window)
        else:
            # Import from folder
            import_from_folder(main_window)

    except Exception as e:
        main_window.log_message(f"❌ Import via error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via Error", f"Import via failed: {str(e)}")


def import_via_ide_file(main_window): #vers 2
    """Import files listed in IDE file"""
    try:
        # Get IDE file
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File",
            "",
            "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
        )
        
        if not ide_file:
            return

        # Get base folder for files
        base_folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Base Folder for Files"
        )
        
        if not base_folder:
            return

        # Parse IDE file
        files_to_import = []
        try:
            with open(ide_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract filename from IDE line (basic parsing)
                        parts = line.split(',')
                        if len(parts) >= 2:
                            filename = parts[1].strip()
                            file_path = os.path.join(base_folder, filename)
                            if os.path.exists(file_path):
                                files_to_import.append(file_path)
        except Exception as e:
            QMessageBox.critical(main_window, "IDE Parse Error", f"Error parsing IDE file: {str(e)}")
            return

        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", "No valid files found from IDE file.")
            return

        main_window.log_message(f"Import via IDE: {len(files_to_import)} files found")
        
        # Show import dialog
        dialog = ImportOptionsDialog(main_window, files_to_import, "IDE")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via IDE Error", f"Import via IDE failed: {str(e)}")


def import_from_folder(main_window): #vers 2
    """Import all files from a folder"""
    try:
        # Get folder
        folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import"
        )
        
        if not folder:
            return

        # Get all files in folder
        files_to_import = []
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                files_to_import.append(file_path)

        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", "No files found in the selected folder.")
            return

        main_window.log_message(f"Import from folder: {len(files_to_import)} files found")
        
        # Show import dialog
        dialog = ImportOptionsDialog(main_window, files_to_import, "folder")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Import from folder error: {str(e)}")
        QMessageBox.critical(main_window, "Import From Folder Error", f"Import from folder failed: {str(e)}")


def integrate_import_functions(main_window): #vers 2
    """Integrate import functions into main window"""
    try:
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_via_function = lambda: import_via_function(main_window)
        
        # Add aliases for different naming conventions
        main_window.import_files = main_window.import_files_function
        main_window.import_files_via = main_window.import_via_function
        
        main_window.log_message("✅ Import functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate import functions: {str(e)}")
        return False


# Export functions
__all__ = [
    'import_files',
    'import_files_function',
    'import_via_function',
    'import_via_ide_file',
    'import_from_folder',
    'get_selected_entries',
    'integrate_import_functions'
]
