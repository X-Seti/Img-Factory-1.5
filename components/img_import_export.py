#this belongs in components/img_import_export.py - Version: 1
# X-Seti - July11 2025 - Img Factory 1.5
# Complete import/export functionality for IMG files

import os
import shutil
import struct
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QCheckBox, QGroupBox,
    QFileDialog, QMessageBox, QProgressDialog, QComboBox,
    QLineEdit, QTextEdit, QTabWidget, QWidget, QGridLayout,
    QTreeWidget, QTreeWidgetItem, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont

# ==============================
# IMPORT/EXPORT DIALOG CLASSES
# ==============================

class ImportOptionsDialog(QDialog):
    """Dialog for import options with IDE file support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Files - Options")
        self.setModal(True)
        self.resize(500, 400)
        
        self.selected_files = []
        self.import_mode = "files"  # "files" or "ide"
        self.replace_existing = False
        self.validate_files = True
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Import mode selection
        mode_group = QGroupBox("Import Mode")
        mode_layout = QVBoxLayout()
        
        self.files_radio = QCheckBox("Import individual files")
        self.files_radio.setChecked(True)
        self.files_radio.toggled.connect(self.on_mode_changed)
        
        self.ide_radio = QCheckBox("Import from IDE file")
        self.ide_radio.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.files_radio)
        mode_layout.addWidget(self.ide_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # File selection area
        self.file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # Buttons for file selection
        file_buttons = QHBoxLayout()
        self.select_files_btn = QPushButton("Select Files...")
        self.select_directory_btn = QPushButton("Select Directory...")
        self.select_ide_btn = QPushButton("Select IDE File...")
        self.select_ide_btn.setEnabled(False)
        
        self.select_files_btn.clicked.connect(self.select_files)
        self.select_directory_btn.clicked.connect(self.select_directory)
        self.select_ide_btn.clicked.connect(self.select_ide_file)
        
        file_buttons.addWidget(self.select_files_btn)
        file_buttons.addWidget(self.select_directory_btn)
        file_buttons.addWidget(self.select_ide_btn)
        file_layout.addLayout(file_buttons)
        
        # File list
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        
        self.file_group.setLayout(file_layout)
        layout.addWidget(self.file_group)
        
        # Options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()
        
        self.replace_check = QCheckBox("Replace existing files")
        self.validate_check = QCheckBox("Validate files before import")
        self.validate_check.setChecked(True)
        
        options_layout.addWidget(self.replace_check)
        options_layout.addWidget(self.validate_check)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import")
        self.cancel_btn = QPushButton("Cancel")
        
        self.import_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.import_btn.setEnabled(False)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def on_mode_changed(self):
        if self.files_radio.isChecked():
            self.import_mode = "files"
            self.select_files_btn.setEnabled(True)
            self.select_directory_btn.setEnabled(True)
            self.select_ide_btn.setEnabled(False)
        else:
            self.import_mode = "ide"
            self.select_files_btn.setEnabled(False)
            self.select_directory_btn.setEnabled(False)
            self.select_ide_btn.setEnabled(True)
    
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Import", "",
            "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
        )
        if files:
            self.selected_files = files
            self.update_file_list()
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            # Get all files from directory
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            self.selected_files = files
            self.update_file_list()
    
    def select_ide_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select IDE File", "", "IDE Files (*.ide);;All Files (*)"
        )
        if file:
            self.selected_files = [file]
            self.update_file_list()
    
    def update_file_list(self):
        self.file_list.clear()
        for file_path in self.selected_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setToolTip(file_path)
            self.file_list.addItem(item)
        
        self.import_btn.setEnabled(len(self.selected_files) > 0)
    
    def get_options(self):
        return {
            'files': self.selected_files,
            'mode': self.import_mode,
            'replace_existing': self.replace_check.isChecked(),
            'validate_files': self.validate_check.isChecked()
        }


class ExportOptionsDialog(QDialog):
    """Dialog for export options"""
    
    def __init__(self, entries=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Files - Options")
        self.setModal(True)
        self.resize(600, 500)
        
        self.entries = entries or []
        self.export_directory = ""
        self.export_mode = "selected"  # "selected", "all", "filtered"
        self.preserve_structure = False
        self.create_ide_file = False
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Export mode selection
        mode_group = QGroupBox("Export Mode")
        mode_layout = QVBoxLayout()
        
        self.selected_radio = QCheckBox("Export selected entries")
        self.selected_radio.setChecked(True)
        
        self.all_radio = QCheckBox("Export all entries")
        self.filtered_radio = QCheckBox("Export filtered entries")
        
        mode_layout.addWidget(self.selected_radio)
        mode_layout.addWidget(self.all_radio)
        mode_layout.addWidget(self.filtered_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Directory selection
        dir_group = QGroupBox("Export Directory")
        dir_layout = QHBoxLayout()
        
        self.dir_label = QLabel("No directory selected")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.browse_btn)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout()
        
        self.preserve_check = QCheckBox("Preserve directory structure")
        self.ide_check = QCheckBox("Create IDE file listing")
        self.overwrite_check = QCheckBox("Overwrite existing files")
        
        options_layout.addWidget(self.preserve_check)
        options_layout.addWidget(self.ide_check)
        options_layout.addWidget(self.overwrite_check)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # File list preview
        preview_group = QGroupBox("Files to Export")
        preview_layout = QVBoxLayout()
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File", "Type", "Size"])
        preview_layout.addWidget(self.file_tree)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Update file list
        self.update_file_preview()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export")
        self.cancel_btn = QPushButton("Cancel")
        
        self.export_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.export_btn.setEnabled(False)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if directory:
            self.export_directory = directory
            self.dir_label.setText(directory)
            self.export_btn.setEnabled(True)
    
    def update_file_preview(self):
        self.file_tree.clear()
        for entry in self.entries:
            item = QTreeWidgetItem([
                getattr(entry, 'name', 'Unknown'),
                getattr(entry, 'extension', '').upper(),
                self._format_size(getattr(entry, 'size', 0))
            ])
            self.file_tree.addItem(item)
    
    def _format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def get_options(self):
        return {
            'directory': self.export_directory,
            'mode': self.export_mode,
            'preserve_structure': self.preserve_check.isChecked(),
            'create_ide_file': self.ide_check.isChecked(),
            'overwrite_existing': self.overwrite_check.isChecked()
        }


# ==============================
# BACKGROUND PROCESSING THREADS
# ==============================

class ImportThread(QThread):
    """Background thread for importing files"""
    
    progress_update = pyqtSignal(int, str)
    file_imported = pyqtSignal(str, bool)
    import_complete = pyqtSignal(int, int)
    import_error = pyqtSignal(str)
    
    def __init__(self, img_file, file_paths, options):
        super().__init__()
        self.img_file = img_file
        self.file_paths = file_paths
        self.options = options
        self.should_cancel = False
    
    def cancel(self):
        self.should_cancel = True
    
    def run(self):
        try:
            imported_count = 0
            error_count = 0
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                if self.should_cancel:
                    break
                
                filename = os.path.basename(file_path)
                progress = int((i + 1) * 100 / total_files)
                self.progress_update.emit(progress, f"Importing {filename}...")
                
                success = self._import_single_file(file_path)
                self.file_imported.emit(filename, success)
                
                if success:
                    imported_count += 1
                else:
                    error_count += 1
                
                # Small delay to prevent UI lockup
                self.msleep(10)
            
            self.import_complete.emit(imported_count, error_count)
            
        except Exception as e:
            self.import_error.emit(f"Import error: {str(e)}")
    
    def _import_single_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            filename = os.path.basename(file_path)
            
            # Check if file already exists
            if self.options.get('replace_existing', False):
                # Remove existing entry if it exists
                for i, entry in enumerate(self.img_file.entries):
                    if getattr(entry, 'name', '') == filename:
                        del self.img_file.entries[i]
                        break
            else:
                # Check for duplicates
                for entry in self.img_file.entries:
                    if getattr(entry, 'name', '') == filename:
                        return False  # Skip duplicate
            
            # Add new entry
            return self.img_file.add_entry(filename, file_data)
            
        except Exception:
            return False


class ExportThread(QThread):
    """Background thread for exporting files"""
    
    progress_update = pyqtSignal(int, str)
    file_exported = pyqtSignal(str, bool)
    export_complete = pyqtSignal(int, int)
    export_error = pyqtSignal(str)
    
    def __init__(self, img_file, entries, export_dir, options):
        super().__init__()
        self.img_file = img_file
        self.entries = entries
        self.export_dir = export_dir
        self.options = options
        self.should_cancel = False
    
    def cancel(self):
        self.should_cancel = True
    
    def run(self):
        try:
            exported_count = 0
            error_count = 0
            total_files = len(self.entries)
            
            # Create export directory
            os.makedirs(self.export_dir, exist_ok=True)
            
            ide_entries = []  # For IDE file creation
            
            for i, entry in enumerate(self.entries):
                if self.should_cancel:
                    break
                
                entry_name = getattr(entry, 'name', f'entry_{i}')
                progress = int((i + 1) * 100 / total_files)
                self.progress_update.emit(progress, f"Exporting {entry_name}...")
                
                success = self._export_single_entry(entry, ide_entries)
                self.file_exported.emit(entry_name, success)
                
                if success:
                    exported_count += 1
                else:
                    error_count += 1
                
                # Small delay to prevent UI lockup
                self.msleep(10)
            
            # Create IDE file if requested
            if self.options.get('create_ide_file', False) and ide_entries:
                self._create_ide_file(ide_entries)
            
            self.export_complete.emit(exported_count, error_count)
            
        except Exception as e:
            self.export_error.emit(f"Export error: {str(e)}")
    
    def _export_single_entry(self, entry, ide_entries):
        try:
            entry_name = getattr(entry, 'name', 'unknown')
            
            # Determine output path
            if self.options.get('preserve_structure', False):
                # Create subdirectories based on file type
                file_ext = os.path.splitext(entry_name)[1].lower()
                if file_ext == '.dff':
                    subdir = 'models'
                elif file_ext == '.txd':
                    subdir = 'textures'
                elif file_ext == '.col':
                    subdir = 'collision'
                else:
                    subdir = 'other'
                
                output_dir = os.path.join(self.export_dir, subdir)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, entry_name)
            else:
                output_path = os.path.join(self.export_dir, entry_name)
            
            # Check if file exists
            if os.path.exists(output_path) and not self.options.get('overwrite_existing', False):
                return False
            
            # Export the file
            if hasattr(self.img_file, 'export_entry'):
                success = self.img_file.export_entry(entry, output_path)
            else:
                # Fallback method
                try:
                    file_data = entry.get_data()
                    with open(output_path, 'wb') as f:
                        f.write(file_data)
                    success = True
                except:
                    success = False
            
            # Add to IDE entries list
            if success and self.options.get('create_ide_file', False):
                ide_entries.append({
                    'name': entry_name,
                    'path': os.path.relpath(output_path, self.export_dir),
                    'size': getattr(entry, 'size', 0)
                })
            
            return success
            
        except Exception:
            return False
    
    def _create_ide_file(self, ide_entries):
        """Create IDE file listing exported files"""
        try:
            ide_path = os.path.join(self.export_dir, 'exported_files.ide')
            with open(ide_path, 'w') as f:
                f.write("# IMG Factory 1.5 - Exported Files List\n")
                f.write(f"# Total files: {len(ide_entries)}\n\n")
                
                for entry in ide_entries:
                    f.write(f"{entry['name']}\t{entry['path']}\t{entry['size']}\n")
                
        except Exception:
            pass  # IDE file creation is optional


# ==============================
# MAIN IMPORT/EXPORT FUNCTIONS
# ==============================

def show_import_dialog(main_window):
    """Show import dialog and handle file import"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        dialog = ImportOptionsDialog(main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_options()
            
            if options['mode'] == 'ide':
                import_from_ide_file(main_window, options['files'][0], options)
            else:
                import_files_threaded(main_window, options['files'], options)
                
    except Exception as e:
        QMessageBox.critical(main_window, "Import Error", f"Failed to show import dialog: {str(e)}")


def show_export_dialog(main_window, selected_entries=None):
    """Show export dialog and handle file export"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Use selected entries or all entries
        if selected_entries is None:
            selected_entries = main_window.current_img.entries
        
        dialog = ExportOptionsDialog(selected_entries, main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_options()
            export_files_threaded(main_window, selected_entries, options['directory'], options)
                
    except Exception as e:
        QMessageBox.critical(main_window, "Export Error", f"Failed to show export dialog: {str(e)}")


def import_files_threaded(main_window, file_paths, options):
    """Import files using background thread"""
    try:
        # Create progress dialog
        progress = QProgressDialog("Importing files...", "Cancel", 0, 100, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Create import thread
        thread = ImportThread(main_window.current_img, file_paths, options)
        
        # Connect signals
        def on_progress(value, text):
            progress.setValue(value)
            progress.setLabelText(text)
            QApplication.processEvents()
        
        def on_file_imported(filename, success):
            status = "✅" if success else "❌"
            main_window.log_message(f"{status} {filename}")
        
        def on_import_complete(imported, errors):
            progress.close()
            main_window.log_message(f"Import complete: {imported} imported, {errors} errors")
            
            # Refresh the table
            if hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            
            QMessageBox.information(main_window, "Import Complete", 
                                  f"Imported {imported} files successfully.\n{errors} files had errors.")
        
        def on_import_error(error_msg):
            progress.close()
            main_window.log_message(f"❌ Import error: {error_msg}")
            QMessageBox.critical(main_window, "Import Error", error_msg)
        
        def on_cancel():
            thread.cancel()
            thread.wait()
            main_window.log_message("Import cancelled by user")
        
        thread.progress_update.connect(on_progress)
        thread.file_imported.connect(on_file_imported)
        thread.import_complete.connect(on_import_complete)
        thread.import_error.connect(on_import_error)
        progress.canceled.connect(on_cancel)
        
        # Start import
        thread.start()
        
    except Exception as e:
        QMessageBox.critical(main_window, "Import Error", f"Failed to start import: {str(e)}")


def export_files_threaded(main_window, entries, export_dir, options):
    """Export files using background thread"""
    try:
        # Create progress dialog
        progress = QProgressDialog("Exporting files...", "Cancel", 0, 100, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Create export thread
        thread = ExportThread(main_window.current_img, entries, export_dir, options)
        
        # Connect signals
        def on_progress(value, text):
            progress.setValue(value)
            progress.setLabelText(text)
            QApplication.processEvents()
        
        def on_file_exported(filename, success):
            status = "✅" if success else "❌"
            main_window.log_message(f"{status} {filename}")
        
        def on_export_complete(exported, errors):
            progress.close()
            main_window.log_message(f"Export complete: {exported} exported, {errors} errors")
            
            QMessageBox.information(main_window, "Export Complete", 
                                  f"Exported {exported} files successfully.\n{errors} files had errors.")
        
        def on_export_error(error_msg):
            progress.close()
            main_window.log_message(f"❌ Export error: {error_msg}")
            QMessageBox.critical(main_window, "Export Error", error_msg)
        
        def on_cancel():
            thread.cancel()
            thread.wait()
            main_window.log_message("Export cancelled by user")
        
        thread.progress_update.connect(on_progress)
        thread.file_exported.connect(on_file_exported)
        thread.export_complete.connect(on_export_complete)
        thread.export_error.connect(on_export_error)
        progress.canceled.connect(on_cancel)
        
        # Start export
        thread.start()
        
    except Exception as e:
        QMessageBox.critical(main_window, "Export Error", f"Failed to start export: {str(e)}")


def import_from_ide_file(main_window, ide_path, options):
    """Import files based on IDE file listing"""
    try:
        with open(ide_path, 'r') as f:
            lines = f.readlines()
        
        base_dir = os.path.dirname(ide_path)
        file_paths = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse IDE line format: filename\tpath\tsize
                parts = line.split('\t')
                if len(parts) >= 2:
                    file_path = os.path.join(base_dir, parts[1])
                    if os.path.exists(file_path):
                        file_paths.append(file_path)
        
        if file_paths:
            import_files_threaded(main_window, file_paths, options)
        else:
            QMessageBox.warning(main_window, "No Files", "No valid files found in IDE file.")
            
    except Exception as e:
        QMessageBox.critical(main_window, "IDE Import Error", f"Failed to import from IDE file: {str(e)}")


def dump_all_entries(main_window):
    """Dump all entries to a folder"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        export_dir = QFileDialog.getExistingDirectory(main_window, "Select Dump Directory")
        if not export_dir:
            return
        
        options = {
            'preserve_structure': True,
            'create_ide_file': True,
            'overwrite_existing': True
        }
        
        export_files_threaded(main_window, main_window.current_img.entries, export_dir, options)
        
    except Exception as e:
        QMessageBox.critical(main_window, "Dump Error", f"Failed to dump entries: {str(e)}")


# ==============================
# INTEGRATION FUNCTIONS
# ==============================

def integrate_import_export_system(main_window):
    """Integrate import/export system into main window"""
    try:
        # Add import/export methods to main window
        main_window.show_import_dialog = lambda: show_import_dialog(main_window)
        main_window.show_export_dialog = lambda: show_export_dialog(main_window)
        main_window.dump_all_entries = lambda: dump_all_entries(main_window)
        
        # Update existing import/export methods
        def import_files():
            show_import_dialog(main_window)
        
        def export_selected():
            selected_entries = get_selected_entries(main_window)
            if selected_entries:
                show_export_dialog(main_window, selected_entries)
            else:
                QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
        
        def export_all():
            show_export_dialog(main_window, main_window.current_img.entries if hasattr(main_window, 'current_img') and main_window.current_img else [])
        
        # Replace existing methods
        main_window.import_files = import_files
        main_window.export_selected = export_selected
        main_window.export_all = export_all
        
        main_window.log_message("✅ Import/Export system integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate import/export system: {str(e)}")
        return False


def get_selected_entries(main_window):
    """Get currently selected entries from the table"""
    try:
        selected_entries = []
        
        if hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            for row in selected_rows:
                if row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])
        
        return selected_entries
        
    except Exception:
        return []


# Export main functions
__all__ = [
    'ImportOptionsDialog', 'ExportOptionsDialog',
    'ImportThread', 'ExportThread',
    'show_import_dialog', 'show_export_dialog',
    'import_files_threaded', 'export_files_threaded',
    'import_from_ide_file', 'dump_all_entries',
    'integrate_import_export_system', 'get_selected_entries'
]