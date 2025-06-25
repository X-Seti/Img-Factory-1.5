# $vers" X-Seti - June04,2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

import sys
import os
import mimetypes
print("Starting application...")
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QProgressBar, QLabel, QPushButton, QFileDialog,
    QMessageBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenuBar, QMenu, QStatusBar, QSizePolicy
)

print("Tkinter imported successfully")
import tkinter as tk

print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
print("PyQt6.QtGui imported successfully")
from PyQt6.QtGui import QAction, QIcon, QFont, QDragEnterEvent, QDropEvent
print("App Settings System imported successfully")
from App_settings_system import AppSettings, apply_theme_to_app
print("Pastel Theme imported successfully")
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
print("Img Core Classes imported successfully")
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
print("Img Creator imported successfully")
from components.img_creator import NewIMGDialog, GameType, add_new_img_functionality
print("Img Formats imported successfully")
from components.img_formats import GameSpecificIMGDialog, EnhancedIMGCreator
print("Img Template Manager imported successfully")
from components.img_templates import TemplateManagerDialog, IMGTemplateManager
print("Quick Start Wizard imported successfully")
#from components/img_quick_start_wizard import QuickStartWizard

class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit(10)
            img_file = IMGFile(self.file_path)
            
            self.progress.emit(30)
            if not img_file.open():
                self.error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress.emit(100)
            self.finished.emit(img_file)
            
        except Exception as e:
            self.error.emit(f"Error loading IMG file: {str(e)}")

class ExportProgressDialog(QDialog):
    """Progress dialog for export operations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exporting Files...")
        self.setMinimumSize(400, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Progress info
        self.status_label = QLabel("Preparing export...")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Current file label
        self.current_file_label = QLabel("")
        layout.addWidget(self.current_file_label)

        # Log area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setPlaceholderText("Export log...")
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.was_cancelled = False

    def update_progress(self, current, total, filename=""):
        """Update progress display"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_label.setText(f"Exporting {current} of {total} files...")

        if filename:
            self.current_file_label.setText(f"Current: {filename}")

    def add_log(self, message):
        """Add message to log"""
        self.log_text.append(message)

    def set_completed(self):
        """Mark export as completed"""
        self.progress_bar.setValue(100)
        self.status_label.setText("Export completed successfully!")
        self.cancel_button.setText("Close")

class ExportThread(QThread):
    """Background thread for exporting files"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    log_message = pyqtSignal(str)
    finished_signal = pyqtSignal(int, int)  # exported_count, error_count
    error_signal = pyqtSignal(str)

    def __init__(self, img_file, entries, export_dir, options=None):
        super().__init__()
        self.img_file = img_file
        self.entries = entries
        self.export_dir = export_dir
        self.options = options or {}
        self.should_stop = False

    def stop(self):
        """Request thread to stop"""
        self.should_stop = True

    def run(self):
        """Run the export process"""
        exported_count = 0
        error_count = 0
        total_files = len(self.entries)

        try:
            for i, entry in enumerate(self.entries):
                if self.should_stop:
                    break

                try:
                    # Update progress
                    self.progress_updated.emit(i, total_files, entry.name)

                    # Get entry data
                    data = entry.get_data()

                    # Determine output path
                    output_path = os.path.join(self.export_dir, entry.name)

                    # Check for overwrite
                    if os.path.exists(output_path) and not self.options.get('overwrite', True):
                        self.log_message.emit(f"Skipped (exists): {entry.name}")
                        continue

                    # Write file
                    with open(output_path, 'wb') as f:
                        f.write(data)

                    exported_count += 1
                    self.log_message.emit(f"Exported: {entry.name}")

                except Exception as e:
                    error_count += 1
                    self.log_message.emit(f"Error exporting {entry.name}: {str(e)}")

            # Final progress update
            self.progress_updated.emit(total_files, total_files, "")
            self.finished_signal.emit(exported_count, error_count)

        except Exception as e:
            self.error_signal.emit(f"Export failed: {str(e)}")


class ExportOptionsDialog(QDialog):
    """Dialog for export options and file selection"""

    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Options")
        self.setMinimumSize(500, 600)
        self.setModal(True)

        self.entries = entries
        self.selected_entries = []
        self.export_dir = ""

        self._create_ui()

    def _create_ui(self):
        """Create the UI"""
        layout = QVBoxLayout(self)

        # File selection
        file_group = QGroupBox("Select Files to Export")
        file_layout = QVBoxLayout(file_group)

        # Selection buttons
        selection_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        selection_layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self._select_none)
        selection_layout.addWidget(select_none_btn)

        # Filter by type
        filter_combo = QComboBox()
        filter_combo.addItems(["All Types", "Models (DFF)", "Textures (TXD)",
                              "Collision (COL)", "Animation (IFP)", "Audio (WAV)"])
        filter_combo.currentTextChanged.connect(self._filter_files)
        selection_layout.addWidget(filter_combo)

        selection_layout.addStretch()
        file_layout.addLayout(selection_layout)

        # File list
        self.file_list = QListWidget()
        self._populate_file_list()
        file_layout.addWidget(self.file_list)

        layout.addWidget(file_group)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        self.overwrite_check = QCheckBox("Overwrite existing files")
        self.overwrite_check.setChecked(True)
        options_layout.addWidget(self.overwrite_check)

        self.preserve_structure_check = QCheckBox("Preserve folder structure (if applicable)")
        options_layout.addWidget(self.preserve_structure_check)

        layout.addWidget(options_group)

        # Directory selection
        dir_group = QGroupBox("Export Directory")
        dir_layout = QHBoxLayout(dir_group)

        self.dir_label = QLabel("No directory selected")
        dir_layout.addWidget(self.dir_label)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)

        layout.addWidget(dir_group)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        export_btn = QPushButton("Start Export")
        export_btn.clicked.connect(self._start_export)
        export_btn.setDefault(True)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)

    def _populate_file_list(self):
        """Populate the file list with entries"""
        self.file_list.clear()
        for entry in self.entries:
            item = QListWidgetItem(f"{entry.name} ({entry.extension}) - {self._format_size(entry.size)}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)  # Default to checked
            item.entry = entry  # Store reference
            self.file_list.addItem(item)

    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _select_all(self):
        """Select all visible items"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)

    def _select_none(self):
        """Deselect all items"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

    def _filter_files(self, filter_type):
        """Filter files by type"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            entry = item.entry

            show_item = True
            if filter_type != "All Types":
                if filter_type == "Models (DFF)" and entry.extension != "DFF":
                    show_item = False
                elif filter_type == "Textures (TXD)" and entry.extension != "TXD":
                    show_item = False
                elif filter_type == "Collision (COL)" and entry.extension != "COL":
                    show_item = False
                elif filter_type == "Animation (IFP)" and entry.extension != "IFP":
                    show_item = False
                elif filter_type == "Audio (WAV)" and entry.extension != "WAV":
                    show_item = False

            item.setHidden(not show_item)

    def _browse_directory(self):
        """Browse for export directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if directory:
            self.export_dir = directory
            self.dir_label.setText(directory)

    def _start_export(self):
        """Start the export process"""
        # Get selected entries
        self.selected_entries = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_entries.append(item.entry)

        if not self.selected_entries:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one file to export.")
            return

        if not self.export_dir:
            QMessageBox.warning(self, "No Directory", "Please select an export directory.")
            return

        self.accept()

    def get_export_options(self):
        """Get the export options"""
        return {
            'overwrite': self.overwrite_check.isChecked(),
            'preserve_structure': self.preserve_structure_check.isChecked()
        }

class ImportValidationDialog(QDialog):
    """Dialog for validating and reviewing files before import"""

    def __init__(self, file_paths, img_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import File Validation")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        self.file_paths = file_paths
        self.img_file = img_file
        self.validated_files = []

        self._create_ui()
        self._validate_files()

    def _create_ui(self):
        """Create the validation dialog UI"""
        layout = QVBoxLayout(self)

        # Header info
        info_label = QLabel(f"Validating {len(self.file_paths)} files for import...")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(info_label)

        # Validation table
        self.validation_table = QTableWidget(0, 6)
        self.validation_table.setHorizontalHeaderLabels([
            "Import", "Filename", "Size", "Type", "Status", "Notes"
        ])

        # Set column properties
        header = self.validation_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Import checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Filename
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)           # Notes

        self.validation_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.validation_table)

        # Options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)

        self.overwrite_check = QCheckBox("Replace existing files with same name")
        self.overwrite_check.setChecked(False)
        options_layout.addWidget(self.overwrite_check)

        self.auto_rename_check = QCheckBox("Auto-rename conflicting files (append _1, _2, etc.)")
        self.auto_rename_check.setChecked(True)
        options_layout.addWidget(self.auto_rename_check)

        self.validate_formats_check = QCheckBox("Validate file formats (slower but safer)")
        self.validate_formats_check.setChecked(True)
        options_layout.addWidget(self.validate_formats_check)

        layout.addWidget(options_group)

        # Summary
        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)

        # Buttons
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)

        select_valid_btn = QPushButton("Select Valid Only")
        select_valid_btn.clicked.connect(self._select_valid)
        button_layout.addWidget(select_valid_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        import_btn = QPushButton("Import Selected")
        import_btn.clicked.connect(self._start_import)
        import_btn.setDefault(True)
        button_layout.addWidget(import_btn)

        layout.addLayout(button_layout)

    def _validate_files(self):
        """Validate all files and populate table"""
        valid_count = 0
        warning_count = 0
        error_count = 0

        for file_path in self.file_paths:
            try:
                # Get file info
                file_info = self._analyze_file(file_path)

                # Add to table
                row = self.validation_table.rowCount()
                self.validation_table.insertRow(row)

                # Import checkbox
                import_check = QCheckBox()
                import_check.setChecked(file_info['can_import'])
                self.validation_table.setCellWidget(row, 0, import_check)

                # File info
                self.validation_table.setItem(row, 1, QTableWidgetItem(file_info['name']))
                self.validation_table.setItem(row, 2, QTableWidgetItem(file_info['size_text']))
                self.validation_table.setItem(row, 3, QTableWidgetItem(file_info['type']))

                # Status with color coding
                status_item = QTableWidgetItem(file_info['status'])
                if file_info['status'] == "Valid":
                    status_item.setBackground(Qt.GlobalColor.green)
                    valid_count += 1
                elif file_info['status'] == "Warning":
                    status_item.setBackground(Qt.GlobalColor.yellow)
                    warning_count += 1
                else:
                    status_item.setBackground(Qt.GlobalColor.red)
                    error_count += 1

                self.validation_table.setItem(row, 4, status_item)
                self.validation_table.setItem(row, 5, QTableWidgetItem(file_info['notes']))

                # Store file info for import
                file_info['path'] = file_path
                file_info['import_widget'] = import_check
                self.validated_files.append(file_info)

            except Exception as e:
                # Handle file analysis errors
                row = self.validation_table.rowCount()
                self.validation_table.insertRow(row)

                import_check = QCheckBox()
                import_check.setChecked(False)
                self.validation_table.setCellWidget(row, 0, import_check)

                self.validation_table.setItem(row, 1, QTableWidgetItem(os.path.basename(file_path)))
                self.validation_table.setItem(row, 2, QTableWidgetItem("Unknown"))
                self.validation_table.setItem(row, 3, QTableWidgetItem("Unknown"))

                status_item = QTableWidgetItem("Error")
                status_item.setBackground(Qt.GlobalColor.red)
                self.validation_table.setItem(row, 4, status_item)
                self.validation_table.setItem(row, 5, QTableWidgetItem(f"Analysis failed: {str(e)}"))

                error_count += 1

        # Update summary
        total = len(self.file_paths)
        self.summary_label.setText(
            f"Total: {total} files | Valid: {valid_count} | Warnings: {warning_count} | Errors: {error_count}"
        )

    def _analyze_file(self, file_path):
        """Analyze a single file for import"""
        info = {
            'name': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'can_import': True,
            'status': 'Valid',
            'notes': ''
        }

        info['size_text'] = self._format_size(info['size'])

        # Check file extension
        ext = os.path.splitext(file_path)[1].upper().lstrip('.')
        info['type'] = ext if ext else 'Unknown'

        # Validate file type
        known_types = ['DFF', 'TXD', 'COL', 'IFP', 'WAV', 'SCM', 'IPL', 'IDE', 'DAT']
        if ext not in known_types:
            info['status'] = 'Warning'
            info['notes'] = f'Unknown file type (.{ext}). May not be compatible with GTA games.'

        # Check for name conflicts
        if self.img_file:
            existing_entry = self.img_file.get_entry_by_name(info['name'])
            if existing_entry:
                info['status'] = 'Warning'
                info['notes'] = f'File already exists in IMG. Will be replaced or renamed based on options.'

        # Size validation
        if info['size'] == 0:
            info['status'] = 'Error'
            info['notes'] = 'File is empty'
            info['can_import'] = False
        elif info['size'] > 100 * 1024 * 1024:  # 100MB
            info['status'] = 'Warning'
            info['notes'] = 'Large file (>100MB). Import may take time.'

        # Basic file validation (if enabled)
        if self.validate_formats_check.isChecked():
            validation_result = self._validate_file_format(file_path, ext)
            if not validation_result['valid']:
                info['status'] = 'Error'
                info['notes'] = validation_result['reason']
                info['can_import'] = False

        return info

    def _validate_file_format(self, file_path, ext):
        """Basic file format validation"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)

            if ext == 'DFF':
                # RenderWare DFF files start with specific signatures
                if len(header) >= 4:
                    # Check for RW chunk header
                    if header[:4] in [b'\x10\x00\x00\x00', b'\x0E\x00\x00\x00']:
                        return {'valid': True}
                return {'valid': False, 'reason': 'Invalid DFF header'}

            elif ext == 'TXD':
                # RenderWare TXD files
                if len(header) >= 4:
                    if header[:4] in [b'\x16\x00\x00\x00']:
                        return {'valid': True}
                return {'valid': False, 'reason': 'Invalid TXD header'}

            elif ext == 'COL':
                # COL files typically start with 'COL' or version info
                if header[:4] in [b'COL\x01', b'COL\x02', b'COL\x03', b'COL\x04', b'COLL']:
                    return {'valid': True}
                return {'valid': False, 'reason': 'Invalid COL header'}

            # For other types, just check if file is readable
            return {'valid': True}

        except Exception as e:
            return {'valid': False, 'reason': f'Cannot read file: {str(e)}'}

    def _format_size(self, size_bytes):
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _select_all(self):
        """Select all files for import"""
        for file_info in self.validated_files:
            file_info['import_widget'].setChecked(True)

    def _select_valid(self):
        """Select only valid files"""
        for file_info in self.validated_files:
            file_info['import_widget'].setChecked(file_info['can_import'] and file_info['status'] != 'Error')

    def _start_import(self):
        """Start the import process"""
        # Get selected files
        selected_files = []
        for file_info in self.validated_files:
            if file_info['import_widget'].isChecked():
                selected_files.append(file_info)

        if not selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one file to import.")
            return

        self.selected_files = selected_files
        self.accept()

    def get_import_options(self):
        """Get import options"""
        return {
            'overwrite': self.overwrite_check.isChecked(),
            'auto_rename': self.auto_rename_check.isChecked(),
            'validate_formats': self.validate_formats_check.isChecked()
        }

class ImportProgressDialog(QDialog):
    """Progress dialog for import operations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importing Files...")
        self.setMinimumSize(400, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Progress info
        self.status_label = QLabel("Preparing import...")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Current file label
        self.current_file_label = QLabel("")
        layout.addWidget(self.current_file_label)

        # Log area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setPlaceholderText("Import log...")
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.was_cancelled = False

    def update_progress(self, current, total, filename=""):
        """Update progress display"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_label.setText(f"Importing {current} of {total} files...")

        if filename:
            self.current_file_label.setText(f"Current: {filename}")

    def add_log(self, message):
        """Add message to log"""
        self.log_text.append(message)

    def set_completed(self):
        """Mark import as completed"""
        self.progress_bar.setValue(100)
        self.status_label.setText("Import completed successfully!")
        self.cancel_button.setText("Close")

class ImportThread(QThread):
    """Background thread for importing files"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    log_message = pyqtSignal(str)
    finished_signal = pyqtSignal(int, int)  # imported_count, error_count
    error_signal = pyqtSignal(str)

    def __init__(self, img_file, file_infos, options=None):
        super().__init__()
        self.img_file = img_file
        self.file_infos = file_infos
        self.options = options or {}
        self.should_stop = False

    def stop(self):
        """Request thread to stop"""
        self.should_stop = True

    def run(self):
        """Run the import process"""
        imported_count = 0
        error_count = 0
        total_files = len(self.file_infos)

        try:
            for i, file_info in enumerate(self.file_infos):
                if self.should_stop:
                    break

                try:
                    # Update progress
                    self.progress_updated.emit(i, total_files, file_info['name'])

                    # Read file data
                    with open(file_info['path'], 'rb') as f:
                        data = f.read()

                    # Determine final filename
                    final_name = self._get_final_filename(file_info['name'])

                    # Add to IMG
                    entry = self.img_file.add_entry(final_name, data)

                    imported_count += 1
                    self.log_message.emit(f"Imported: {final_name}")

                except Exception as e:
                    error_count += 1
                    self.log_message.emit(f"Error importing {file_info['name']}: {str(e)}")

            # Final progress update
            self.progress_updated.emit(total_files, total_files, "")
            self.finished_signal.emit(imported_count, error_count)

        except Exception as e:
            self.error_signal.emit(f"Import failed: {str(e)}")

    def _get_final_filename(self, original_name):
        """Get final filename handling conflicts"""
        if not self.options.get('auto_rename', False):
            return original_name

        # Check for conflicts and auto-rename
        final_name = original_name
        counter = 1
        name_base, ext = os.path.splitext(original_name)

        while self.img_file.get_entry_by_name(final_name):
            final_name = f"{name_base}_{counter}{ext}"
            counter += 1

        return final_name

class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [Wip]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings
        
        # Current IMG file
        self.current_img: IMGFile = None
        self.load_thread: IMGLoadThread = None

        self._create_menu()
        self._create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout will contain the main horizontal splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self._create_main_ui_with_splitters(main_layout)

    def export_selected_entries(self):
        """Enhanced export with options dialog"""
        if not self.current_img:
            QMessageBox.warning(self, "Export", "No IMG file loaded")
            return

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            # If nothing selected, show all entries
            selected_entries = self.current_img.entries
        else:
            # Use selected entries
            selected_entries = []
            for model_index in selected_rows:
                row = model_index.row()
                if row < len(self.current_img.entries):
                    selected_entries.append(self.current_img.entries[row])

        if not selected_entries:
            QMessageBox.information(self, "Export", "No entries to export")
            return

        # Show export options dialog
        options_dialog = ExportOptionsDialog(selected_entries, self)
        if options_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Get selections and options
        entries_to_export = options_dialog.selected_entries
        export_dir = options_dialog.export_dir
        export_options = options_dialog.get_export_options()

        # Show progress dialog
        progress_dialog = ExportProgressDialog(self)
        progress_dialog.show()

        # Start export thread
        self.export_thread = ExportThread(self.current_img, entries_to_export, export_dir, export_options)
        self.export_thread.progress_updated.connect(progress_dialog.update_progress)
        self.export_thread.log_message.connect(progress_dialog.add_log)
        self.export_thread.log_message.connect(self.log_message)
        self.export_thread.finished_signal.connect(lambda exported, errors: self._export_finished(progress_dialog, exported, errors))
        self.export_thread.error_signal.connect(lambda msg: self._export_error(progress_dialog, msg))

        # Connect cancel button
        progress_dialog.cancel_button.clicked.connect(self.export_thread.stop)

        self.export_thread.start()

        def _export_finished(self, progress_dialog, exported_count, error_count):
            """Handle export completion"""
        progress_dialog.set_completed()

        if error_count == 0:
            message = f"Successfully exported {exported_count} files!"
            QMessageBox.information(self, "Export Complete", message)
        else:
            message = f"Export completed with {error_count} errors.\nSuccessfully exported: {exported_count} files"
            QMessageBox.warning(self, "Export Complete", message)

        self.log_message(f"Export finished: {exported_count} files exported, {error_count} errors")

    def _export_error(self, progress_dialog, error_message):
        """Handle export error"""
        progress_dialog.close()
        QMessageBox.critical(self, "Export Error", error_message)
        self.log_error(error_message)

    def quick_export_selected(self):
        """Quick export without options dialog"""
        if not self.current_img:
            QMessageBox.warning(self, "Quick Export", "No IMG file loaded")
            return

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Quick Export", "No entries selected")
            return

        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return

        # Get selected entries
        selected_entries = []
        for model_index in selected_rows:
            row = model_index.row()
            if row < len(self.current_img.entries):
                selected_entries.append(self.current_img.entries[row])

        # Export directly
        try:
            exported_count = 0
            for entry in selected_entries:
                data = entry.get_data()
                output_path = os.path.join(export_dir, entry.name)

                with open(output_path, 'wb') as f:
                    f.write(data)

                exported_count += 1
                self.log_message(f"Quick exported: {entry.name}")

            QMessageBox.information(self, "Quick Export Complete",
                                f"Successfully exported {exported_count} files to:\n{export_dir}")

        except Exception as e:
            self.log_error(f"Quick export failed: {str(e)}")
            QMessageBox.critical(self, "Quick Export Error", f"Export failed:\n{str(e)}")

    def _clean_button_text(self, text):
        """Remove emoji from button text"""
        if not self.app_settings.current_settings.get("show_emoji_in_buttons", False):
            # Remove common emoji
            emoji_chars = ['📥', '📤', '🗑️', '🔄', '⚙️', '🔍', '💾', '📁', '🖖', '☕', '🍞', '🟣', '✨']
            for emoji in emoji_chars:
                text = text.replace(emoji, '').strip()
        return text

    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Create themed button with icon control"""
        
        # Clean button text if emoji is disabled
        clean_label = self._clean_button_text(label)
        
        btn = QPushButton(clean_label)
        
        if action_type:
            btn.setProperty("action-type", action_type)
        
        # Only add icon if enabled
        if icon and self.app_settings.current_settings.get("show_button_icons", False):
            btn.setIcon(QIcon.fromTheme(icon))
        
        if bold:
            font = btn.font()
            font.setBold(True)
            btn.setFont(font)
        
        return btn

    def _create_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        
        # Only show menu icons if enabled
        show_menu_icons = self.app_settings.current_settings.get("show_menu_icons", True)
        
        open_action = QAction("Open IMG...", self)
        if show_menu_icons:
            open_action.setIcon(QIcon.fromTheme("document-open"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        close_action = QAction("Close IMG", self)
        if show_menu_icons:
            close_action.setIcon(QIcon.fromTheme("window-close"))
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        if show_menu_icons:
            exit_action.setIcon(QIcon.fromTheme("application-exit"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Other menus (keeping original structure)
        menu_names = [
            "Edit", "Dat", "IMG", "Model", "Texture", "Collision", 
            "Item Definition", "Item Placement", "Entry", "Settings", "Help"
        ]

        for name in menu_names:
            menu = menubar.addMenu(name)
            if name == "IMG":
                rebuild_action = QAction("Rebuild", self)
                if show_menu_icons:
                    rebuild_action.setIcon(QIcon.fromTheme("view-refresh"))
                rebuild_action.triggered.connect(self.rebuild_img)
                menu.addAction(rebuild_action)
                
                merge_action = QAction("Merge", self)
                if show_menu_icons:
                    merge_action.setIcon(QIcon.fromTheme("document-merge"))
                menu.addAction(merge_action)
                
                split_action = QAction("Split", self)
                if show_menu_icons:
                    split_action.setIcon(QIcon.fromTheme("edit-cut"))
                menu.addAction(split_action)
                
                menu.addSeparator()
                
                info_action = QAction("IMG Info", self)
                if show_menu_icons:
                    info_action.setIcon(QIcon.fromTheme("dialog-information"))
                info_action.triggered.connect(self.show_img_info)
                menu.addAction(info_action)
            elif name == "Entry":
                export_action = QAction("Export Selected", self)
                if show_menu_icons:
                    export_action.setIcon(QIcon.fromTheme("document-save-as"))
                export_action.triggered.connect(self.export_selected_entries)
                menu.addAction(export_action)
                
                import_action = QAction("Import Files", self)
                if show_menu_icons:
                    import_action.setIcon(QIcon.fromTheme("document-open"))
                import_action.triggered.connect(self.import_files)
                menu.addAction(import_action)
                
                menu.addSeparator()
                
                remove_action = QAction("Remove Selected", self)
                if show_menu_icons:
                    remove_action.setIcon(QIcon.fromTheme("edit-delete"))
                remove_action.triggered.connect(self.remove_selected_entries)
                menu.addAction(remove_action)
            elif name == "Settings":
                prefs_action = QAction("Preferences", self)
                if show_menu_icons:
                    prefs_action.setIcon(QIcon.fromTheme("preferences-other"))
                menu.addAction(prefs_action)
            elif name == "Help":
                about_action = QAction("About", self)
                if show_menu_icons:
                    about_action.setIcon(QIcon.fromTheme("help-about"))
                menu.addAction(about_action)
            else:
                placeholder = QAction("(No items yet)", self)
                placeholder.setEnabled(False)
                menu.addAction(placeholder)

    def _create_status_bar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        
        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status.addPermanentWidget(self.progress_bar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        status.addWidget(self.status_label)
        
        self.img_info_label = QLabel("No IMG loaded")
        status.addPermanentWidget(self.img_info_label)

    def _create_main_ui_with_splitters(self, main_layout):
        """Create the main UI with resizable splitters"""
        
        # Main horizontal splitter (left side vs right side)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Table and Log with vertical splitter
        left_widget = self._create_left_panel()
        
        # Right side: Controls
        right_widget = self._create_right_panel()
        
        # Add widgets to main splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        
        # Set initial sizes (left panel takes 70%, right panel takes 30%)
        self.main_splitter.setSizes([700, 350])
        
        # Set minimum sizes to prevent panels from becoming too small
        self.main_splitter.setChildrenCollapsible(False)
        
        # Style the splitter
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #666666;
                border: 1px solid #444444;
                width: 6px;
                margin: 2px;
                border-radius: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #888888;
            }
            
            QSplitter::handle:pressed {
                background-color: #999999;
            }
        """)
        
        main_layout.addWidget(self.main_splitter)

    def _create_left_panel(self):
        """Create the left panel with IMG info, table and log, separated by a vertical splitter"""
        
        # Main container for left panel
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # IMG file info panel
        info_panel = QGroupBox("IMG File Information")
        info_layout = QHBoxLayout(info_panel)
        
        self.file_path_label = QLabel("No file loaded")
        self.file_path_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(QLabel("File:"))
        info_layout.addWidget(self.file_path_label)
        info_layout.addStretch()
        
        self.version_label = QLabel("Unknown")
        info_layout.addWidget(QLabel("Version:"))
        info_layout.addWidget(self.version_label)
        
        self.entry_count_label = QLabel("0")
        info_layout.addWidget(QLabel("Entries:"))
        info_layout.addWidget(self.entry_count_label)
        
        left_layout.addWidget(info_panel)
        
        # Vertical splitter for table vs log
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Table widget - updated for IMG entries
        self.table = QTableWidget(0, 7)  # Updated to 7 columns
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Version", "Compression", "Status"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self._apply_table_theme()
        
        # Set column widths for IMG entries
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Compression
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status
        
        # Set minimum size for table
        self.table.setMinimumSize(400, 200)
        
        # Log widget
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Operation Log")
        self._apply_log_theme()
        
        # Set minimum size for log
        self.log.setMinimumSize(400, 100)
        
        # Add widgets to left splitter
        self.left_splitter.addWidget(self.table)
        self.left_splitter.addWidget(self.log)
        
        # Set initial sizes (table takes 70%, log takes 30%)
        self.left_splitter.setSizes([400, 200])
        
        # Style the vertical splitter
        self.left_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #666666;
                border: 1px solid #444444;
                height: 6px;
                margin: 2px;
                border-radius: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #888888;
            }
            
            QSplitter::handle:pressed {
                background-color: #999999;
            }
        """)
        
        # Add splitter to main layout
        left_layout.addWidget(self.left_splitter)
        
        # Connect signals and add sample data
        self._connect_signals()
        self._add_sample_data()
        
        return left_container

    def _create_right_panel(self):
        """Create the right panel with responsive controls"""
        
        # Container widget for the right panel
        right_widget = QWidget()
        right_widget.setMinimumWidth(150)  # Reduced minimum width
        right_layout = QVBoxLayout(right_widget)

        # IMG Section with adaptive buttons
        img_box = QGroupBox("IMG Operations")
        img_layout = QGridLayout()
        img_layout.setSpacing(3)  # Tighter spacing
        
        img_buttons = [
            ("New IMG", "import", "document-new", self.create_new_img),
            ("Open IMG", "import", "document-open", self.open_img_file),
            ("Refresh", "update", "view-refresh", self.refresh_table),
            ("Close", None, "window-close", self.close_img_file),
            ("Rebuild", "update", "document-save", self.rebuild_img),
            ("Rebuild As", None, "document-save-as", None),
            ("Rebuild All", None, "document-save", None),
            ("Merge", None, "document-merge", None),
            ("Split", None, "edit-cut", None),
            ("Convert", "convert", "transform", None),
        ]
        
        self.img_buttons = []  # Store button references
        for i, (label, action_type, icon, callback) in enumerate(img_buttons):
            btn = self._create_adaptive_button(label, action_type, icon, callback, bold=True)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entries Section with adaptive buttons
        entries_box = QGroupBox("Entry Operations")
        entries_layout = QGridLayout()
        entries_layout.setSpacing(3)  # Tighter spacing
        
        entry_buttons = [
            ("Import", "import", "edit-copy", self.import_files),
            ("Import via", "import", None, self.quick_import_files),
            ("Update lst", "update", None, self.refresh_table),
            ("Export", "export", None, self.export_selected_entries),
            ("Export via", "export", None, None),
            ("Quick Exp", "export", None, self.quick_export_selected),
            ("Remove", "remove", "edit-delete", self.remove_selected_entries),
            ("Remove via", "remove", None, None),
            ("Dump", "update", None, None),
            ("Rename", "convert", None, None),
            ("Replace", "convert", None, None),
            ("Select All", None, None, None),
            ("Select Inv", None, None, None),
            ("Sort", None, None, None)
        ]
        
        self.entry_buttons = []  # Store button references
        for i, (label, action_type, icon_name, callback) in enumerate(entry_buttons):
            btn = self._create_adaptive_button(label, action_type, icon_name, callback, 
                                             bold="Import" in label or "Export" in label or "Remove" in label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Filter/Search Panel (adapted for narrow panels)
        filter_box = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout()  # Changed to vertical for narrow panels
        
        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Files", "Models (DFF)", "Textures (TXD)", 
                                   "Collision (COL)", "Animation (IFP)", "Audio (WAV)", "Scripts (SCM)"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        # Search input with button
        search_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search...")
        self.filter_input.textChanged.connect(self.apply_filter)
        search_layout.addWidget(self.filter_input)
        
        filter_btn = QPushButton("Find")
        if self.app_settings.current_settings.get("show_button_icons", False):
            filter_btn.setIcon(QIcon.fromTheme("edit-find"))
        filter_btn.setMaximumWidth(50)
        filter_btn.setToolTip("Apply search filter")
        search_layout.addWidget(filter_btn)
        
        filter_layout.addLayout(search_layout)
        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)
        
        # Add stretch to push controls to top
        right_layout.addStretch()

        return right_widget

    def _create_adaptive_button(self, full_text, action_type=None, icon=None, callback=None, bold=False):
        """Create button with adaptive text display and icon control"""
        
        btn = QPushButton()
        
        # Clean text if emoji disabled
        clean_text = self._clean_button_text(full_text)
        
        # Store full text and create short version
        btn.full_text = clean_text
        btn.short_text = self._create_short_text(clean_text)
        btn.setText(clean_text)
        
        if action_type:
            btn.setProperty("action-type", action_type)
        
        # Only add icon if enabled
        if icon and self.app_settings.current_settings.get("show_button_icons", False):
            btn.setIcon(QIcon.fromTheme(icon))
        
        if callback:
            btn.clicked.connect(callback)
        if bold:
            font = btn.font()
            font.setBold(True)
            btn.setFont(font)
        
        # Set size policy and tooltip
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setMinimumHeight(26)
        btn.setToolTip(clean_text)
        
        return btn

    def _create_short_text(self, full_text):
        """Create shortened version of button text"""
        abbreviations = {
            'Open IMG': 'Open',
            'Import': 'Imp',
            'Export': 'Exp', 
            'Remove': 'Rem',
            'Update': 'Upd',
            'Convert': 'Conv',
            'Rebuild': 'Rbld',
            'Quick Exp': 'QExp',
            'Import via': 'Imp>',
            'Export via': 'Exp>',
            'Remove via': 'Rem>',
            'Update lst': 'List',
            'Select All': 'All',
            'Select Inv': 'Inv',
            'Rebuild As': 'RbAs',
            'Rebuild All': 'RbAll',
            'Refresh': 'Ref'
        }
        
        return abbreviations.get(full_text, full_text[:5])

    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)
        
        # Get right panel width
        if hasattr(self, 'main_splitter'):
            sizes = self.main_splitter.sizes()
            if len(sizes) > 1:
                right_panel_width = sizes[1]
                self._adapt_buttons_to_width(right_panel_width)

    def _adapt_buttons_to_width(self, width):
        """Adapt button text based on available width"""
        all_buttons = []
        if hasattr(self, 'img_buttons'):
            all_buttons.extend(self.img_buttons)
        if hasattr(self, 'entry_buttons'):
            all_buttons.extend(self.entry_buttons)
        
        for button in all_buttons:
            if hasattr(button, 'full_text'):
                if width > 280:
                    button.setText(button.full_text)
                elif width > 200:
                    # Medium text - remove some words
                    text = button.full_text.replace(' via', '>').replace(' lst', '')
                    button.setText(text)
                elif width > 150:
                    button.setText(button.short_text)
                else:
                    # Icon only mode
                    button.setText("")

    def _connect_signals(self):
        """Connect signals for table interactions"""
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def _add_sample_data(self):
        """Add sample data to show the interface"""
        sample_entries = [
            ("player.dff", "DFF", "245 KB", "0x2000", "3.6.0.3", "None", "Ready"),
            ("player.txd", "TXD", "512 KB", "0x42000", "3.6.0.3", "None", "Ready"),
            ("vehicle.col", "COL", "128 KB", "0x84000", "COL 2", "None", "Ready"),
            ("dance.ifp", "IFP", "1.2 MB", "0xA4000", "IFP 1", "ZLib", "Ready"),
        ]
        
        self.table.setRowCount(len(sample_entries))
        for row, entry_data in enumerate(sample_entries):
            for col, value in enumerate(entry_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        
        self.log_message("Interface loaded with sample data. Open an IMG file to see real content.")

    def _apply_table_theme(self):
        """Apply theme-aware styling to the table with soft pastel highlights"""
        theme = self.app_settings.get_theme()
        colors = theme["colors"]
        
        # Determine if we're using a dark or light theme
        is_dark_theme = self._is_dark_theme(colors["bg_primary"])
        
        if is_dark_theme:
            # Dark theme colors - soft pastels on dark background
            table_bg = colors["bg_secondary"]
            table_text = colors["text_primary"]
            alternate_bg = self._lighten_color(colors["bg_tertiary"], 0.1)
            selection_bg = self._add_alpha(colors["accent_primary"], 0.3)
            header_bg = colors["panel_bg"]
            header_text = colors["text_accent"]
            grid_color = self._lighten_color(colors["border"], 0.2)
        else:
            # Light theme colors - soft pastels on light background
            table_bg = colors["bg_primary"]
            table_text = colors["text_primary"]
            alternate_bg = self._darken_color(colors["bg_secondary"], 0.05)
            selection_bg = self._add_alpha(colors["accent_primary"], 0.2)
            header_bg = colors["panel_bg"]
            header_text = colors["text_accent"]
            grid_color = colors["border"]
        
        table_style = f"""
            QTableWidget {{
                background-color: {table_bg};
                color: {table_text};
                gridline-color: {grid_color};
                selection-background-color: {selection_bg};
                alternate-background-color: {alternate_bg};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                font-weight: normal;
            }}
            
            QTableWidget::item {{
                padding: 4px 8px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {selection_bg};
                color: {colors["text_primary"]};
            }}
            
            QTableWidget::item:hover {{
                background-color: {self._add_alpha(colors["accent_secondary"], 0.1)};
            }}
            
            QHeaderView::section {{
                background-color: {header_bg};
                color: {header_text};
                padding: 6px 8px;
                border: 1px solid {colors["border"]};
                border-radius: 0px;
                font-weight: bold;
                text-align: left;
            }}
            
            QHeaderView::section:hover {{
                background-color: {self._lighten_color(header_bg, 0.1)};
            }}
        """
        
        self.table.setStyleSheet(table_style)

    def _apply_log_theme(self):
        """Apply theme-aware styling to the log widget"""
        theme = self.app_settings.get_theme()
        colors = theme["colors"]
        
        # Use a slightly different background for the log to distinguish it
        is_dark_theme = self._is_dark_theme(colors["bg_primary"])
        
        if is_dark_theme:
            log_bg = self._darken_color(colors["bg_secondary"], 0.1)
            log_text = colors["text_secondary"]
        else:
            log_bg = self._lighten_color(colors["bg_secondary"], 0.05)
            log_text = colors["text_primary"]
        
        log_style = f"""
            QTextEdit {{
                background-color: {log_bg};
                color: {log_text};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                line-height: 1.2;
            }}
            
            QTextEdit:focus {{
                border-color: {colors["accent_primary"]};
            }}
        """
        
        self.log.setStyleSheet(log_style)

    def _is_dark_theme(self, color_hex):
        """Determine if a color is dark (for theme detection)"""
        # Remove # and convert to RGB
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def _lighten_color(self, color_hex, factor):
        """Lighten a hex color by a factor (0.0 to 1.0)"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, color_hex, factor):
        """Darken a hex color by a factor (0.0 to 1.0)"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _add_alpha(self, color_hex, alpha):
        """Add alpha transparency to a hex color"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"

    def manage_templates(self):
        template_manager = IMGTemplateManager()
        dialog = TemplateManagerDialog(template_manager, self)
        dialog.exec()

    def show_quick_start(self):
        wizard = QuickStartWizard(self)
        wizard.img_created.connect(self.load_img_file)
        wizard.exec()

    def _apply_template(self, template_data):
        """Apply a template to create new IMG"""

        # Validation before creation
        #creator = EnhancedIMGCreator('gtasa')
        #is_valid, errors = creator.validate_creation_params(
        #    filename="new.img",
        #    output_dir="todo",
        #    initial_size_mb=100
        #)

        # Save frequently used configurations
        template_manager = IMGTemplateManager()
        template_manager.save_template("My GTA SA Mod", GameType.GTA_SA, {
            'initial_size_mb': 200,
            'compression': True,
            'create_structure': True
        })
        # Create multiple IMG files at once
        games = ['gta3', 'gtavc', 'gtasa']
        for game in games:
            creator = EnhancedIMGCreator(game)
            creator.create_new_img(f"{game}_custom.img", output_dir)

    def create_new_img(self):
        dialog = NewIMGDialog(self)  # Now uses enhanced version automatically
        dialog.img_created.connect(self.load_img_file)
        dialog.exec()

    def log_message(self, message):
        """Add message to log output"""
        self.log.append(f"[INFO] {message}")
        self.log.ensureCursorVisible()

    def log_error(self, message):
        """Add error message to log output"""
        self.log.append(f"[ERROR] {message}")
        self.log.ensureCursorVisible()

    # IMG File Operations
    def open_img_file(self):
        """Open IMG file dialog and load selected file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open IMG File", 
            "", 
            "IMG Files (*.img *.dir);;All Files (*)"
        )
        
        if file_path:
            self.load_img_file(file_path)

    def load_img_file(self, file_path):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Loading IMG file...")
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress.connect(self.progress_bar.setValue)
        self.load_thread.finished.connect(self.on_img_loaded)
        self.load_thread.error.connect(self.on_img_load_error)
        self.load_thread.start()

    def on_img_loaded(self, img_file):
        """Handle successful IMG file loading"""
        self.current_img = img_file
        self.progress_bar.setVisible(False)
        
        # Update UI
        self.file_path_label.setText(os.path.basename(img_file.file_path))
        self.version_label.setText(f"IMG {img_file.version.value}")
        self.entry_count_label.setText(str(len(img_file.entries)))
        self.img_info_label.setText(f"IMG {img_file.version.value} - {len(img_file.entries)} entries")
        
        # Populate table with real data
        self.populate_table()
        
        self.status_label.setText("IMG file loaded successfully")
        self.log_message(f"Loaded IMG file: {img_file.file_path}")
        self.log_message(f"Version: {img_file.version.name}, Entries: {len(img_file.entries)}")

    def on_img_load_error(self, error_message):
        """Handle IMG file loading error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error loading IMG file")
        self.log_error(error_message)
        
        QMessageBox.critical(self, "Error", f"Failed to load IMG file:\n{error_message}")

    def populate_table(self):
        """Populate table with real IMG entries"""
        if not self.current_img:
            return
        
        entries = self.current_img.entries
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))
            
            # Type
            type_text = entry.extension if entry.extension else "Unknown"
            self.table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # Size
            size_text = format_file_size(entry.size)
            self.table.setItem(row, 2, QTableWidgetItem(size_text))
            
            # Offset
            offset_text = f"0x{entry.offset:X}"
            self.table.setItem(row, 3, QTableWidgetItem(offset_text))
            
            # Version
            version_text = entry.get_version_text()
            self.table.setItem(row, 4, QTableWidgetItem(version_text))
            
            # Compression
            comp_text = "Compressed" if entry.is_compressed() else "None"
            self.table.setItem(row, 5, QTableWidgetItem(comp_text))
            
            # Status
            status_text = "New" if entry.is_new_entry else ("Modified" if entry.is_replaced else "Ready")
            self.table.setItem(row, 6, QTableWidgetItem(status_text))
            
            # Make all items read-only
            for col in range(7):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
            
            # Clear UI and restore sample data
            self._add_sample_data()
            self.file_path_label.setText("No file loaded")
            self.version_label.setText("Unknown")
            self.entry_count_label.setText("0")
            self.img_info_label.setText("No IMG loaded")
            
            self.log_message("IMG file closed")

    def export_selected_entries(self):
        """Enhanced export with options dialog"""
        if not self.current_img:
            QMessageBox.warning(self, "Export", "No IMG file loaded")
            return

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            # If nothing selected, show all entries
            selected_entries = self.current_img.entries
        else:
            # Use selected entries
            selected_entries = []
            for model_index in selected_rows:
                row = model_index.row()
                if row < len(self.current_img.entries):
                    selected_entries.append(self.current_img.entries[row])

        if not selected_entries:
            QMessageBox.information(self, "Export", "No entries to export")
            return

        # Show export options dialog
        options_dialog = ExportOptionsDialog(selected_entries, self)
        if options_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Get selections and options
        entries_to_export = options_dialog.selected_entries
        export_dir = options_dialog.export_dir
        export_options = options_dialog.get_export_options()

        # Show progress dialog
        progress_dialog = ExportProgressDialog(self)
        progress_dialog.show()

        # Start export thread
        self.export_thread = ExportThread(self.current_img, entries_to_export, export_dir, export_options)
        self.export_thread.progress_updated.connect(progress_dialog.update_progress)
        self.export_thread.log_message.connect(progress_dialog.add_log)
        self.export_thread.log_message.connect(self.log_message)
        self.export_thread.finished_signal.connect(lambda exported, errors: self._export_finished(progress_dialog, exported, errors))
        self.export_thread.error_signal.connect(lambda msg: self._export_error(progress_dialog, msg))

        # Connect cancel button
        progress_dialog.cancel_button.clicked.connect(self.export_thread.stop)

        self.export_thread.start()

    def _export_finished(self, progress_dialog, exported_count, error_count):
        """Handle export completion"""
        progress_dialog.set_completed()

        if error_count == 0:
            message = f"Successfully exported {exported_count} files!"
            QMessageBox.information(self, "Export Complete", message)
        else:
            message = f"Export completed with {error_count} errors.\nSuccessfully exported: {exported_count} files"
            QMessageBox.warning(self, "Export Complete", message)

        self.log_message(f"Export finished: {exported_count} files exported, {error_count} errors")

    def _export_error(self, progress_dialog, error_message):
        """Handle export error"""
        progress_dialog.close()
        QMessageBox.critical(self, "Export Error", error_message)
        self.log_error(error_message)

    # Quick export method (bypass options dialog)
    def quick_export_selected(self):
        """Quick export without options dialog"""
        if not self.current_img:
            QMessageBox.warning(self, "Quick Export", "No IMG file loaded")
            return

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Quick Export", "No entries selected")
            return

        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return

        # Get selected entries
        selected_entries = []
        for model_index in selected_rows:
            row = model_index.row()
            if row < len(self.current_img.entries):
                selected_entries.append(self.current_img.entries[row])

        # Export directly
        try:
            exported_count = 0
            for entry in selected_entries:
                data = entry.get_data()
                output_path = os.path.join(export_dir, entry.name)

                with open(output_path, 'wb') as f:
                    f.write(data)

                exported_count += 1
                self.log_message(f"Quick exported: {entry.name}")

            QMessageBox.information(self, "Quick Export Complete",
                                f"Successfully exported {exported_count} files to:\n{export_dir}")

        except Exception as e:
            self.log_error(f"Quick export failed: {str(e)}")
            QMessageBox.critical(self, "Quick Export Error", f"Export failed:\n{str(e)}")

    def apply_filter(self):
        """Apply filter based on combo box and search text"""
        if not self.current_img:
            return
        
        filter_type = self.filter_combo.currentText()
        search_text = self.filter_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Apply type filter
            if filter_type != "All Files":
                type_item = self.table.item(row, 1)
                if type_item:
                    file_type = type_item.text()
                    if filter_type == "Models (DFF)" and file_type != "DFF":
                        show_row = False
                    elif filter_type == "Textures (TXD)" and file_type != "TXD":
                        show_row = False
                    elif filter_type == "Collision (COL)" and file_type != "COL":
                        show_row = False
                    elif filter_type == "Animation (IFP)" and file_type != "IFP":
                        show_row = False
                    elif filter_type == "Audio (WAV)" and file_type != "WAV":
                        show_row = False
                    elif filter_type == "Scripts (SCM)" and file_type != "SCM":
                        show_row = False
            
            # Apply search filter
            if show_row and search_text:
                name_item = self.table.item(row, 0)
                if name_item and search_text not in name_item.text().lower():
                    show_row = False
            
            self.table.setRowHidden(row, not show_row)

    def refresh_table(self):
        """Refresh the table display"""
        if self.current_img:
            self.populate_table()
            self.log_message("Table refreshed")
        else:
            self.log_message("No IMG file loaded to refresh")

    # Event handlers
    def on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = len(self.table.selectionModel().selectedRows())
        if selected_rows > 0:
            self.status_label.setText(f"{selected_rows} entries selected")
        else:
            self.status_label.setText("Ready")

    def on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        row = item.row()
        name_item = self.table.item(row, 0)
        if name_item:
            entry_name = name_item.text()
            self.log_message(f"Double-clicked on entry: {entry_name}")

    # Menu action implementations
    def show_img_info(self):
        """Show detailed IMG file information"""
        if not self.current_img:
            QMessageBox.information(self, "IMG Info", "No IMG file loaded")
            return
        
        info_text = f"""IMG File Information:

File Path: {self.current_img.file_path}
Version: {self.current_img.version.name}
Entry Count: {len(self.current_img.entries)}
Encrypted: {self.current_img.is_encrypted}
Platform: {self.current_img.platform}

File Types:
"""
        
        # Count file types
        type_counts = {}
        for entry in self.current_img.entries:
            ext = entry.extension or "Unknown"
            type_counts[ext] = type_counts.get(ext, 0) + 1
        
        for file_type, count in sorted(type_counts.items()):
            info_text += f"  {file_type}: {count} files\n"
        
        QMessageBox.information(self, "IMG File Information", info_text)

    # Placeholder methods for not-yet-implemented features
    def export_selected_entries(self):
        """Export selected entries to files"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Export", "No entries selected")
            return
        
        if not self.current_img:
            QMessageBox.warning(self, "Export", "No IMG file loaded")
            return
        
        # Get directory to export to
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        try:
            exported_count = 0
            for model_index in selected_rows:
                row = model_index.row()
                if row < len(self.current_img.entries):
                    entry = self.current_img.entries[row]
                    
                    # Get entry data
                    data = entry.get_data()
                    
                    # Write to file
                    output_path = os.path.join(export_dir, entry.name)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    
                    exported_count += 1
                    self.log_message(f"Exported: {entry.name}")
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Successfully exported {exported_count} files to:\n{export_dir}")
            
        except Exception as e:
            self.log_error(f"Export failed: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Export failed:\n{str(e)}")

    def import_files(self):
        """Enhanced import with validation dialog"""
        if not self.current_img:
            QMessageBox.warning(self, "Import", "No IMG file loaded")
            return

        # Get files to import
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            "",
            "All Supported Files (*.dff *.txd *.col *.ifp *.wav *.scm *.ipl *.ide *.dat);;All Files (*)"
        )

        if not file_paths:
            return

        # Show validation dialog
        validation_dialog = ImportValidationDialog(file_paths, self.current_img, self)
        if validation_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Get validated files and options
        selected_files = validation_dialog.selected_files
        import_options = validation_dialog.get_import_options()

        if not selected_files:
            return

        # Show progress dialog
        progress_dialog = ImportProgressDialog(self)
        progress_dialog.show()

        # Start import thread
        self.import_thread = ImportThread(self.current_img, selected_files, import_options)
        self.import_thread.progress_updated.connect(progress_dialog.update_progress)
        self.import_thread.log_message.connect(progress_dialog.add_log)
        self.import_thread.log_message.connect(self.log_message)
        self.import_thread.finished_signal.connect(lambda imported, errors: self._import_finished(progress_dialog, imported, errors))
        self.import_thread.error_signal.connect(lambda msg: self._import_error(progress_dialog, msg))

        # Connect cancel button
        progress_dialog.cancel_button.clicked.connect(self.import_thread.stop)

        self.import_thread.start()

    def _import_finished(self, progress_dialog, imported_count, error_count):
        """Handle import completion"""
        progress_dialog.set_completed()

        # Refresh table to show new entries
        self.populate_table()

        if error_count == 0:
            message = f"Successfully imported {imported_count} files!"
            QMessageBox.information(self, "Import Complete", message)
        else:
            message = f"Import completed with {error_count} errors.\nSuccessfully imported: {imported_count} files"
            QMessageBox.warning(self, "Import Complete", message)

        self.log_message(f"Import finished: {imported_count} files imported, {error_count} errors")

    def _import_error(self, progress_dialog, error_message):
        """Handle import error"""
        progress_dialog.close()
        QMessageBox.critical(self, "Import Error", error_message)
        self.log_error(error_message)

    # Quick import method
    def quick_import_files(self):
        """Quick import without validation dialog"""
        if not self.current_img:
            QMessageBox.warning(self, "Quick Import", "No IMG file loaded")
            return

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Quick Import",
            "",
            "All Files (*)"
        )

        if not file_paths:
            return

        try:
            imported_count = 0
            for file_path in file_paths:
                filename = os.path.basename(file_path)

                with open(file_path, 'rb') as f:
                    data = f.read()

                # Add entry to IMG
                entry = self.current_img.add_entry(filename, data)
                imported_count += 1
                self.log_message(f"Quick imported: {filename}")

            # Refresh table
            self.populate_table()

            QMessageBox.information(self, "Quick Import Complete",
                                f"Successfully imported {imported_count} files")

        except Exception as e:
            self.log_error(f"Quick import failed: {str(e)}")
            QMessageBox.critical(self, "Quick Import Error", f"Import failed:\n{str(e)}")

    def remove_selected_entries(self):
        """Remove selected entries from IMG"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Remove", "No entries selected")
            return
        
        if not self.current_img:
            QMessageBox.warning(self, "Remove", "No IMG file loaded")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Remove {len(selected_rows)} selected entries?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            removed_count = 0
            # Sort rows in descending order to remove from end first
            rows = sorted([idx.row() for idx in selected_rows], reverse=True)
            
            for row in rows:
                if row < len(self.current_img.entries):
                    entry = self.current_img.entries[row]
                    self.current_img.remove_entry(entry)
                    removed_count += 1
                    self.log_message(f"Removed: {entry.name}")
            
            # Refresh table
            self.populate_table()
            
            QMessageBox.information(self, "Remove Complete", 
                                  f"Successfully removed {removed_count} entries")
    except Exception as e:
        self.log_error(f"Remove failed: {str(e)}")
        QMessageBox.critical(self, "Remove Error", f"Remove failed:\n{str(e)}")

    def remove_entries(self):
        try:
            removed_count = 0
            # Your removal logic here
            # removed_count += 1  # increment as you remove items

            QMessageBox.information(self, "Remove Complete",
                                f"Successfully removed {removed_count} entries")


    def rebuild_img(self):
        """Rebuild IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "Rebuild", "No IMG file loaded")
            return
        
        # Get output file path
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Rebuilt IMG", "", "IMG Files (*.img);;All Files (*)"
        )
        
        if not output_path:
            return
        
        try:
            self.log_message("Starting IMG rebuild...")
            self.current_img.rebuild(output_path)
            self.log_message(f"IMG rebuilt successfully: {output_path}")
            
            QMessageBox.information(self, "Rebuild Complete", 
                                  f"IMG file rebuilt successfully:\n{output_path}")
            
        except Exception as e:
            self.log_error(f"Rebuild failed: {str(e)}")
            QMessageBox.critical(self, "Rebuild Error", f"Rebuild failed:\n{str(e)}")

def __init__(self, app_settings):
    super().__init__()
    app = QApplication(sys.argv)
    settings = AppSettings()

    # Apply base theme
    apply_theme_to_app(app, settings)

    # Create window
    window = ImgFactoryDemo(settings)

    # Apply pastel button theme on top
    apply_pastel_theme_to_buttons(app, settings)

    window.show()

    if __name__ == "__main__":
        print("Creating main window...")
        root = tk.Tk()
        print("Root window created")

        # Your app initialization
        app = YourMainAppClass(root)  # Replace with your actual class
        print("App initialized")

        print("Starting mainloop...")
        root.mainloop()

    except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")

    # Add new IMG functionality
    self._add_new_img_support()

def _add_new_img_support(self):
    """Add new IMG creation support"""
    # Add to File menu
    file_menu = self.menuBar().children()[1]  # Assuming File is second menu
    new_action = QAction("🆕 New IMG Archive...", self)
    new_action.setShortcut("Ctrl+N")
    new_action.triggered.connect(self.create_new_img)
    file_menu.insertAction(file_menu.actions()[0], new_action)

    # Add quick access toolbar
    toolbar = self.addToolBar("Quick Actions")

    # New IMG dropdown menu
    new_menu = QMenu("New IMG", self)
    new_menu.addAction("🏙️ GTA III", lambda: self.quick_create("gta3"))
    new_menu.addAction("🌴 GTA VC", lambda: self.quick_create("gtavc"))
    new_menu.addAction("🏜️ GTA SA", lambda: self.quick_create("gtasa"))
    new_menu.addAction("🏫 Bully", lambda: self.quick_create("bully"))
    new_menu.addSeparator()
    new_menu.addAction("⚙️ Custom...", self.create_new_img)

    new_btn = QPushButton("🆕 New IMG")
    new_btn.setMenu(new_menu)
    toolbar.addWidget(new_btn)

def quick_create(self, game_type):
    """Quick create for specific game type"""
    dialog = GameSpecificIMGDialog(self)
    # Pre-select game type
    for button in dialog.game_button_group.buttons():
        if hasattr(button, 'game_type') and button.game_type.value == game_type:
            button.setChecked(True)
            dialog._on_game_type_changed(button)
            break
    dialog.exec()

def create_new_img(self):
    """Show full new IMG creation dialog"""
    dialog = GameSpecificIMGDialog(self)
    dialog.img_created.connect(self.load_img_file)
    dialog.img_created.connect(lambda path: self.log_message(f"Created: {os.path.basename(path)}"))
    dialog.exec()

    self.template_manager = IMGTemplateManager()
    sys.exit(app.exec())
