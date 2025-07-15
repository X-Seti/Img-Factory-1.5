#this belongs in core/import.py - Version: 1
# X-Seti - July15 2025 - Img Factory 1.5
# Import functions for IMG Factory

import os
import shutil
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QProgressBar, QMessageBox, QFileDialog, QGroupBox, QGridLayout, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont


class ImportOptionsDialog(QDialog):
    """Import options dialog"""
    
    def __init__(self, main_window, files_to_import, import_type="files"):
        super().__init__(main_window)
        self.main_window = main_window
        self.files_to_import = files_to_import
        self.import_type = import_type
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"Import {self.import_type.title()}")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()
        
        self.replace_existing = QCheckBox("Replace existing entries")
        self.replace_existing.setChecked(True)
        options_layout.addWidget(self.replace_existing)
        
        self.validate_files = QCheckBox("Validate files before import")
        self.validate_files.setChecked(True)
        options_layout.addWidget(self.validate_files)
        
        self.create_backup = QCheckBox("Create backup before import")
        self.create_backup.setChecked(False)
        options_layout.addWidget(self.create_backup)
        
        self.create_log = QCheckBox("Create import log file")
        self.create_log.setChecked(False)
        options_layout.addWidget(self.create_log)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # File count info
        info_label = QLabel(f"Files to import: {len(self.files_to_import)}")
        layout.addWidget(info_label)
        
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
        
    def start_import(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.files_to_import))
        
        # Start import thread
        self.import_thread = ImportThread(
            self.main_window,
            self.files_to_import,
            self.replace_existing.isChecked(),
            self.validate_files.isChecked(),
            self.create_backup.isChecked(),
            self.create_log.isChecked()
        )
        
        self.import_thread.progress.connect(self.progress_bar.setValue)
        self.import_thread.finished.connect(self.import_finished)
        self.import_thread.start()
        
    def import_finished(self, success, message):
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
    
    def __init__(self, main_window, files_to_import, replace_existing, validate_files, create_backup, create_log):
        super().__init__()
        self.main_window = main_window
        self.files_to_import = files_to_import
        self.replace_existing = replace_existing
        self.validate_files = validate_files
        self.create_backup = create_backup
        self.create_log = create_log
        
    def run(self):
        try:
            imported_count = 0
            log_entries = []
            
            # Create backup if requested
            if self.create_backup:
                self.create_img_backup()
            
            for i, file_path in enumerate(self.files_to_import):
                filename = os.path.basename(file_path)
                
                # Validate file if requested
                if self.validate_files:
                    if not self.validate_file(file_path):
                        log_entries.append(f"Skipped: {filename} (validation failed)")
                        continue
                
                # Check if entry already exists
                if not self.replace_existing:
                    if self.entry_exists(filename):
                        log_entries.append(f"Skipped: {filename} (already exists)")
                        continue
                
                # Import file
                imported = self.import_file(file_path)
                
                if imported:
                    imported_count += 1
                    log_entries.append(f"Imported: {filename}")
                else:
                    log_entries.append(f"Failed: {filename}")
                
                self.progress.emit(i + 1)
            
            # Create log file if requested
            if self.create_log:
                log_path = os.path.join(os.path.dirname(self.files_to_import[0]), 'import_log.txt')
                with open(log_path, 'w') as f:
                    f.write('\n'.join(log_entries))
            
            # Update UI
            if hasattr(self.main_window, '_update_ui_for_loaded_img'):
                self.main_window._update_ui_for_loaded_img()
            
            self.finished.emit(True, f"Imported {imported_count}/{len(self.files_to_import)} files successfully.")
            
        except Exception as e:
            self.finished.emit(False, f"Import error: {str(e)}")
    
    def create_img_backup(self):
        """Create backup of current IMG file"""
        try:
            if hasattr(self.main_window, 'current_img') and hasattr(self.main_window.current_img, 'file_path'):
                img_path = self.main_window.current_img.file_path
                backup_path = img_path + '.backup'
                shutil.copy2(img_path, backup_path)
        except Exception:
            pass
    
    def validate_file(self, file_path):
        """Validate file before import"""
        try:
            # Basic validation - file exists and is readable
            if not os.path.exists(file_path):
                return False
            
            if os.path.getsize(file_path) == 0:
                return False
            
            # Try to read file
            with open(file_path, 'rb') as f:
                f.read(10)  # Read first 10 bytes
            
            return True
            
        except Exception:
            return False
    
    def entry_exists(self, filename):
        """Check if entry already exists in IMG"""
        try:
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                for entry in self.main_window.current_img.entries:
                    entry_name = getattr(entry, 'name', '')
                    if entry_name.lower() == filename.lower():
                        return True
            return False
        except Exception:
            return False
    
    def import_file(self, file_path):
        """Import a single file"""
        try:
            filename = os.path.basename(file_path)
            
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
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
                    # Create new entry (this depends on your IMG class structure)
                    new_entry = type('Entry', (), {
                        'name': filename,
                        'data': file_data,
                        'size': len(file_data),
                        'get_data': lambda: file_data
                    })()
                    
                    # Remove existing entry if replacing
                    if self.replace_existing:
                        self.main_window.current_img.entries = [
                            e for e in self.main_window.current_img.entries 
                            if getattr(e, 'name', '').lower() != filename.lower()
                        ]
                    
                    self.main_window.current_img.entries.append(new_entry)
                    return True
                except Exception:
                    pass
            
            return False
            
        except Exception:
            return False


def import_files_function(main_window):
    """Import selected files"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get files to import
        files, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select files to import",
            "",
            "All Files (*)"
        )

        if not files:
            return

        main_window.log_message(f"📥 Import Via IDE: {ide_file}")

        # Parse IDE file to get filenames
        files_to_import = []
        try:
            with open(ide_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue

                    # Extract filename from IDE line
                    parts = line.split(',')
                    if parts:
                        filename = parts[0].strip().strip('"\'')
                        if filename:
                            # Look for file in assets folder
                            file_path = os.path.join(assets_folder, filename)
                            if os.path.exists(file_path):
                                files_to_import.append(file_path)
                            else:
                                main_window.log_message(f"⚠️ Not found: {filename}")

        except Exception as e:
            main_window.log_message(f"❌ Error reading IDE file: {str(e)}")
            QMessageBox.critical(main_window, "IDE Parse Error", f"Could not parse IDE file:\n{str(e)}")
            return

        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", "No files from IDE found in assets folder.")
            return

        main_window.log_message(f"📋 Found {len(files_to_import)} files to import")

        # Show import dialog
        dialog = ImportOptionsDialog(main_window, files_to_import, "IDE")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Import Via error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via Error", f"Import Via failed: {str(e)}")


def import_directory_function(main_window):
    """Import all files from a directory"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get directory
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory to Import")
        if not directory:
            return

        # Get all files in directory
        files_to_import = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                files_to_import.append(os.path.join(root, file))

        if not files_to_import:
            QMessageBox.information(main_window, "No Files", "No files found in directory.")
            return

        main_window.log_message(f"📥 Import Directory: {directory} ({len(files_to_import)} files)")

        # Show import dialog
        dialog = ImportOptionsDialog(main_window, files_to_import, "directory")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Import Directory error: {str(e)}")
        QMessageBox.critical(main_window, "Import Directory Error", f"Import Directory failed: {str(e)}")


def import_from_ide_file(main_window, ide_file_path, assets_folder):
    """Import files based on IDE file - utility function"""
    try:
        files_to_import = []
        
        with open(ide_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('//'):
                    continue

                # Extract filename from IDE line
                parts = line.split(',')
                if parts:
                    filename = parts[0].strip().strip('"\'')
                    if filename:
                        file_path = os.path.join(assets_folder, filename)
                        if os.path.exists(file_path):
                            files_to_import.append(file_path)

        return files_to_import

    except Exception as e:
        main_window.log_message(f"❌ Error parsing IDE file: {str(e)}")
        return []


def validate_import_files(files_to_import):
    """Validate files before import"""
    valid_files = []
    
    for file_path in files_to_import:
        try:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Try to read file
                with open(file_path, 'rb') as f:
                    f.read(10)  # Read first 10 bytes
                valid_files.append(file_path)
        except Exception:
            continue
    
    return valid_files


def create_backup_before_import(main_window):
    """Create backup of current IMG file before import"""
    try:
        if hasattr(main_window, 'current_img') and hasattr(main_window.current_img, 'file_path'):
            img_path = main_window.current_img.file_path
            backup_path = img_path + '.backup'
            shutil.copy2(img_path, backup_path)
            main_window.log_message(f"✅ Backup created: {backup_path}")
            return True
    except Exception as e:
        main_window.log_message(f"❌ Backup failed: {str(e)}")
        return False


def get_import_statistics(main_window):
    """Get import statistics"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            total_entries = len(main_window.current_img.entries)
            
            # Count by file type
            type_counts = {}
            for entry in main_window.current_img.entries:
                entry_name = getattr(entry, 'name', '')
                ext = os.path.splitext(entry_name)[1].lower()
                type_counts[ext] = type_counts.get(ext, 0) + 1
            
            return {
                'total_entries': total_entries,
                'type_counts': type_counts
            }
    except Exception:
        pass
    
    return {'total_entries': 0, 'type_counts': {}}


def integrate_import_functions(main_window):
    """Integrate import functions into main window"""
    try:
        main_window.import_files = lambda: import_files_function(main_window)
        main_window.import_files_via = lambda: import_via_function(main_window)
        main_window.import_directory = lambda: import_directory_function(main_window)
        
        # Add aliases
        main_window.import_files_function = main_window.import_files
        main_window.import_via_function = main_window.import_files_via
        main_window.import_directory_function = main_window.import_directory
        
        # Add utility functions
        main_window.import_from_ide_file = lambda ide_file, assets_folder: import_from_ide_file(main_window, ide_file, assets_folder)
        main_window.validate_import_files = validate_import_files
        main_window.create_backup_before_import = lambda: create_backup_before_import(main_window)
        main_window.get_import_statistics = lambda: get_import_statistics(main_window)
        
        main_window.log_message("✅ Import functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate import functions: {str(e)}")
        return False


# Export functions
__all__ = [
    'import_files_function',
    'import_via_function',
    'import_directory_function',
    'import_from_ide_file',
    'validate_import_files',
    'create_backup_before_import',
    'get_import_statistics',
    'integrate_import_functions'
]Import Files: {len(files)} files selected")

        # Show import dialog
        dialog = ImportOptionsDialog(main_window, files, "files")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Import error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import failed: {str(e)}")


def import_via_function(main_window):
    """Import models and textures from IDE file assets folder"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get IDE file
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE file",
            "",
            "IDE Files (*.ide);;All Files (*)"
        )

        if not ide_file:
            return

        # Get assets folder
        assets_folder = QFileDialog.getExistingDirectory(main_window, "Select Assets Folder")
        if not assets_folder:
            return

        main_window.log_message(f"📥 