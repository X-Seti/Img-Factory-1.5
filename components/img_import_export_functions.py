#this belongs in components/ img_import_export_functions.py - Version: 2
# X-Seti - July13 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Import/Export Functions - Complete consolidated functionality
Handles all import/export operations with dialogs and background processing
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
    QGroupBox, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon


# ============================================================================
# IMPORT/EXPORT DIALOGS
# ============================================================================

class ImportOptionsDialog(QDialog):
    """Advanced import options dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Options - IMG Factory 1.5")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.selected_files = []
        self.import_options = {}
        
        self._create_ui()
        self._connect_signals()
    
    def _create_ui(self):
        """Create the UI components"""
        layout = QVBoxLayout(self)
        
        # File selection section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(150)
        file_layout.addWidget(self.file_list)
        
        # File selection buttons
        file_btn_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("Add Files...")
        self.add_files_btn.clicked.connect(self._add_files)
        file_btn_layout.addWidget(self.add_files_btn)
        
        self.add_folder_btn = QPushButton("Add Folder...")
        self.add_folder_btn.clicked.connect(self._add_folder)
        file_btn_layout.addWidget(self.add_folder_btn)
        
        self.remove_files_btn = QPushButton("Remove Selected")
        self.remove_files_btn.clicked.connect(self._remove_selected_files)
        file_btn_layout.addWidget(self.remove_files_btn)
        
        file_btn_layout.addStretch()
        file_layout.addLayout(file_btn_layout)
        layout.addWidget(file_group)
        
        # Import options section
        options_group = QGroupBox("Import Options")
        options_layout = QFormLayout(options_group)
        
        self.overwrite_cb = QCheckBox("Overwrite existing entries")
        options_layout.addRow("Conflicts:", self.overwrite_cb)
        
        self.validate_cb = QCheckBox("Validate file formats")
        self.validate_cb.setChecked(True)
        options_layout.addRow("Validation:", self.validate_cb)
        
        self.organize_cb = QCheckBox("Auto-organize by file type")
        options_layout.addRow("Organization:", self.organize_cb)
        
        layout.addWidget(options_group)
        
        # Progress section
        self.progress_label = QLabel("Ready to import")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_btn = QPushButton("Import Files")
        self.import_btn.clicked.connect(self.accept)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.file_list.itemSelectionChanged.connect(self._update_buttons)
    
    def _add_files(self):
        """Add files to import list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            "",
            "All Files (*);;Models (*.dff);;Textures (*.txd);;Collision (*.col);;Animation (*.ifp);;Audio (*.wav);;Scripts (*.scm)"
        )
        
        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                filename = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                
                item = QListWidgetItem(f"{filename} ({self._format_size(size)})")
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.file_list.addItem(item)
        
        self._update_buttons()
    
    def _add_folder(self):
        """Add folder contents to import list"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Import")
        if folder:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path) and file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    size = os.path.getsize(file_path)
                    
                    item = QListWidgetItem(f"{filename} ({self._format_size(size)})")
                    item.setData(Qt.ItemDataRole.UserRole, file_path)
                    self.file_list.addItem(item)
        
        self._update_buttons()
    
    def _remove_selected_files(self):
        """Remove selected files from list"""
        for item in self.file_list.selectedItems():
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
            self.file_list.takeItem(self.file_list.row(item))
        
        self._update_buttons()
    
    def _update_buttons(self):
        """Update button states"""
        has_files = len(self.selected_files) > 0
        has_selection = len(self.file_list.selectedItems()) > 0
        
        self.import_btn.setEnabled(has_files)
        self.remove_files_btn.setEnabled(has_selection)
        
        # Update progress label
        if has_files:
            self.progress_label.setText(f"Ready to import {len(self.selected_files)} files")
        else:
            self.progress_label.setText("No files selected")
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def get_import_options(self) -> Dict:
        """Get import options"""
        return {
            'files': self.selected_files,
            'overwrite_existing': self.overwrite_cb.isChecked(),
            'validate_files': self.validate_cb.isChecked(),
            'organize_by_type': self.organize_cb.isChecked()
        }


class ExportOptionsDialog(QDialog):
    """Advanced export options dialog"""
    
    def __init__(self, entries: List, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Options - IMG Factory 1.5")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self.entries = entries
        self.export_options = {}
        
        self._create_ui()
        self._connect_signals()
        self._populate_entries()
    
    def _create_ui(self):
        """Create the UI components"""
        layout = QVBoxLayout(self)
        
        # Entry selection section
        entries_group = QGroupBox("Entries to Export")
        entries_layout = QVBoxLayout(entries_group)
        
        # Entry table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(4)
        self.entries_table.setHorizontalHeaderLabels(["Export", "Name", "Type", "Size"])
        
        # Adjust column widths
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        entries_layout.addWidget(self.entries_table)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        selection_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self._select_none)
        selection_layout.addWidget(self.select_none_btn)
        
        self.select_type_combo = QComboBox()
        self.select_type_combo.addItems(["All Types", "DFF", "TXD", "COL", "IFP", "WAV", "SCM"])
        selection_layout.addWidget(self.select_type_combo)
        
        self.select_type_btn = QPushButton("Select Type")
        self.select_type_btn.clicked.connect(self._select_by_type)
        selection_layout.addWidget(self.select_type_btn)
        
        selection_layout.addStretch()
        entries_layout.addLayout(selection_layout)
        layout.addWidget(entries_group)
        
        # Export options section
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout(options_group)
        
        # Output directory
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        output_layout.addWidget(self.output_path_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.browse_btn)
        
        options_layout.addRow("Output Directory:", output_layout)
        
        # Export options
        self.organize_cb = QCheckBox("Organize by file type")
        options_layout.addRow("Organization:", self.organize_cb)
        
        self.create_ide_cb = QCheckBox("Create IDE file list")
        options_layout.addRow("IDE File:", self.create_ide_cb)
        
        self.overwrite_cb = QCheckBox("Overwrite existing files")
        options_layout.addRow("Conflicts:", self.overwrite_cb)
        
        layout.addWidget(options_group)
        
        # Progress section
        self.progress_label = QLabel("Ready to export")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_btn = QPushButton("Export Files")
        self.export_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.export_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.entries_table.itemChanged.connect(self._update_export_count)
    
    def _populate_entries(self):
        """Populate entries table"""
        self.entries_table.setRowCount(len(self.entries))
        
        for row, entry in enumerate(self.entries):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.entries_table.setCellWidget(row, 0, checkbox)
            
            # Name
            name_item = QTableWidgetItem(getattr(entry, 'name', f'Entry {row}'))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 1, name_item)
            
            # Type
            entry_name = getattr(entry, 'name', '')
            file_type = entry_name.split('.')[-1].upper() if '.' in entry_name else 'Unknown'
            type_item = QTableWidgetItem(file_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 2, type_item)
            
            # Size
            size = getattr(entry, 'size', 0)
            size_item = QTableWidgetItem(self._format_size(size))
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 3, size_item)
        
        self._update_export_count()
    
    def _select_all(self):
        """Select all entries"""
        for row in range(self.entries_table.rowCount()):
            checkbox = self.entries_table.cellWidget(row, 0)
            checkbox.setChecked(True)
        self._update_export_count()
    
    def _select_none(self):
        """Deselect all entries"""
        for row in range(self.entries_table.rowCount()):
            checkbox = self.entries_table.cellWidget(row, 0)
            checkbox.setChecked(False)
        self._update_export_count()
    
    def _select_by_type(self):
        """Select entries by file type"""
        selected_type = self.select_type_combo.currentText()
        if selected_type == "All Types":
            self._select_all()
            return
        
        for row in range(self.entries_table.rowCount()):
            type_item = self.entries_table.item(row, 2)
            checkbox = self.entries_table.cellWidget(row, 0)
            
            if type_item and type_item.text() == selected_type:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        
        self._update_export_count()
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if directory:
            self.output_path_edit.setText(directory)
    
    def _update_export_count(self):
        """Update export count label"""
        selected_count = 0
        for row in range(self.entries_table.rowCount()):
            checkbox = self.entries_table.cellWidget(row, 0)
            if checkbox.isChecked():
                selected_count += 1
        
        self.progress_label.setText(f"Ready to export {selected_count} of {len(self.entries)} entries")
        self.export_btn.setEnabled(selected_count > 0 and self.output_path_edit.text().strip() != "")
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def get_selected_entries(self) -> List:
        """Get selected entries for export"""
        selected = []
        for row in range(self.entries_table.rowCount()):
            checkbox = self.entries_table.cellWidget(row, 0)
            if checkbox.isChecked():
                selected.append(self.entries[row])
        return selected
    
    def get_export_options(self) -> Dict:
        """Get export options"""
        return {
            'output_directory': self.output_path_edit.text(),
            'organize_by_type': self.organize_cb.isChecked(),
            'create_ide_file': self.create_ide_cb.isChecked(),
            'overwrite_existing': self.overwrite_cb.isChecked(),
            'selected_entries': self.get_selected_entries()
        }


# ============================================================================
# BACKGROUND PROCESSING THREADS
# ============================================================================

class ImportThread(QThread):
    """Background thread for importing files"""
    
    progress_updated = pyqtSignal(int, str)
    import_completed = pyqtSignal(int, int)  # success_count, error_count
    
    def __init__(self, img_file, import_options):
        super().__init__()
        self.img_file = img_file
        self.import_options = import_options
        self.success_count = 0
        self.error_count = 0
    
    def run(self):
        """Run import process"""
        files = self.import_options.get('files', [])
        overwrite = self.import_options.get('overwrite_existing', False)
        validate = self.import_options.get('validate_files', True)
        
        for i, file_path in enumerate(files):
            try:
                filename = os.path.basename(file_path)
                self.progress_updated.emit(i + 1, f"Importing {filename}...")
                
                # Read file data
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Validate if requested
                if validate and not self._validate_file(file_path, filename):
                    self.error_count += 1
                    continue
                
                # Check for existing entry
                if not overwrite and self._entry_exists(filename):
                    self.error_count += 1
                    continue
                
                # Add entry to IMG
                if hasattr(self.img_file, 'add_entry') and self.img_file.add_entry(filename, file_data):
                    self.success_count += 1
                else:
                    self.error_count += 1
                
            except Exception:
                self.error_count += 1
        
        self.import_completed.emit(self.success_count, self.error_count)
    
    def _validate_file(self, file_path: str, filename: str) -> bool:
        """Basic file validation"""
        try:
            # Check file size
            size = os.path.getsize(file_path)
            if size == 0:
                return False
            
            # Basic extension check
            if '.' in filename:
                ext = filename.split('.')[-1].lower()
                return ext in ['dff', 'txd', 'col', 'ifp', 'wav', 'scm', 'ide', 'ipl', 'dat']
            
            return True
        except Exception:
            return False
    
    def _entry_exists(self, filename: str) -> bool:
        """Check if entry already exists"""
        if hasattr(self.img_file, 'entries'):
            for entry in self.img_file.entries:
                if getattr(entry, 'name', '') == filename:
                    return True
        return False


class ExportThread(QThread):
    """Background thread for exporting files"""
    
    progress_updated = pyqtSignal(int, str)
    export_completed = pyqtSignal(int, int)  # success_count, error_count
    
    def __init__(self, img_file, export_options):
        super().__init__()
        self.img_file = img_file
        self.export_options = export_options
        self.success_count = 0
        self.error_count = 0
    
    def run(self):
        """Run export process"""
        entries = self.export_options.get('selected_entries', [])
        output_dir = self.export_options.get('output_directory', '')
        organize = self.export_options.get('organize_by_type', False)
        create_ide = self.export_options.get('create_ide_file', False)
        overwrite = self.export_options.get('overwrite_existing', False)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        ide_entries = []
        
        for i, entry in enumerate(entries):
            try:
                entry_name = getattr(entry, 'name', f'entry_{i}')
                self.progress_updated.emit(i + 1, f"Exporting {entry_name}...")
                
                # Determine output path
                if organize:
                    file_type = self._get_file_type(entry_name)
                    type_dir = os.path.join(output_dir, file_type.lower())
                    os.makedirs(type_dir, exist_ok=True)
                    output_path = os.path.join(type_dir, entry_name)
                else:
                    output_path = os.path.join(output_dir, entry_name)
                
                # Check if file exists
                if os.path.exists(output_path) and not overwrite:
                    self.error_count += 1
                    continue
                
                # Export the file
                if self._export_entry(entry, output_path):
                    self.success_count += 1
                    
                    # Add to IDE list
                    if create_ide:
                        ide_entries.append({
                            'name': entry_name,
                            'path': os.path.relpath(output_path, output_dir),
                            'size': getattr(entry, 'size', 0)
                        })
                else:
                    self.error_count += 1
                
            except Exception:
                self.error_count += 1
        
        # Create IDE file if requested
        if create_ide and ide_entries:
            self._create_ide_file(output_dir, ide_entries)
        
        self.export_completed.emit(self.success_count, self.error_count)
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename"""
        if '.' in filename:
            ext = filename.split('.')[-1].upper()
            if ext in ['DFF']:
                return 'models'
            elif ext in ['TXD']:
                return 'textures'
            elif ext in ['COL']:
                return 'collision'
            elif ext in ['IFP']:
                return 'animations'
            elif ext in ['WAV', 'OGG']:
                return 'audio'
            elif ext in ['SCM']:
                return 'scripts'
        return 'misc'
    
    def _export_entry(self, entry, output_path: str) -> bool:
        """Export single entry"""
        try:
            # Get entry data
            if hasattr(entry, 'get_data'):
                file_data = entry.get_data()
            elif hasattr(self.img_file, 'get_entry_data'):
                file_data = self.img_file.get_entry_data(entry)
            else:
                return False
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            return True
            
        except Exception:
            return False
    
    def _create_ide_file(self, output_dir: str, ide_entries: List[Dict]):
        """Create IDE file listing exported files"""
        try:
            ide_path = os.path.join(output_dir, 'exported_files.ide')
            with open(ide_path, 'w', encoding='utf-8') as f:
                f.write("# IMG Factory 1.5 - Exported Files List\n")
                f.write(f"# Total files: {len(ide_entries)}\n\n")
                
                for entry in ide_entries:
                    f.write(f"{entry['name']}\t{entry['path']}\t{entry['size']}\n")
                
        except Exception:
            pass  # IDE file creation is optional


# ============================================================================
# MAIN IMPORT/EXPORT FUNCTIONS
# ============================================================================

def import_files_function(main_window):
    """Import files with advanced dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        dialog = ImportOptionsDialog(main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_import_options()
            
            if options['files']:
                _import_files_threaded(main_window, options)
            else:
                QMessageBox.information(main_window, "Import", "No files selected for import.")
                
    except Exception as e:
        main_window.log_message(f"❌ Import error: {str(e)}")


def import_via_function(main_window):
    """Import via IDE file or folder"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        # Ask user what to import
        reply = QMessageBox.question(
            main_window, 
            "Import Via",
            "What would you like to import?\n\n"
            "Yes = Import from IDE file\n"
            "No = Import from folder",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import_from_ide_file(main_window)
        elif reply == QMessageBox.StandardButton.No:
            import_directory_function(main_window)
        
    except Exception as e:
        main_window.log_message(f"❌ Import via error: {str(e)}")


def import_from_ide_file(main_window):
    """Import files listed in IDE file"""
    try:
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File",
            "",
            "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
        )
        
        if not ide_file:
            return
        
        # Parse IDE file
        files_to_import = []
        base_dir = os.path.dirname(ide_file)
        
        with open(ide_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        filename = parts[0]
                        relative_path = parts[1]
                        full_path = os.path.join(base_dir, relative_path)
                        
                        if os.path.exists(full_path):
                            files_to_import.append(full_path)
        
        if files_to_import:
            options = {
                'files': files_to_import,
                'overwrite_existing': False,
                'validate_files': True,
                'organize_by_type': False
            }
            _import_files_threaded(main_window, options)
        else:
            QMessageBox.information(main_window, "IDE Import", "No valid files found in IDE file.")
            
    except Exception as e:
        main_window.log_message(f"❌ IDE import error: {str(e)}")


def import_directory_function(main_window):
    """Import all files from directory"""
    try:
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory to Import")
        if not directory:
            return
        
        # Get all files in directory
        files_to_import = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                files_to_import.append(file_path)
        
        if files_to_import:
            options = {
                'files': files_to_import,
                'overwrite_existing': False,
                'validate_files': True,
                'organize_by_type': False
            }
            _import_files_threaded(main_window, options)
        else:
            QMessageBox.information(main_window, "Directory Import", "No files found in selected directory.")
        
    except Exception as e:
        main_window.log_message(f"❌ Directory import error: {str(e)}")


def export_selected_function(main_window):
    """Export selected entries with advanced dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "Export", "No entries selected for export.")
            return
        
        dialog = ExportOptionsDialog(selected_entries, main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_export_options()
            
            if options['selected_entries'] and options['output_directory']:
                _export_files_threaded(main_window, options)
            else:
                QMessageBox.information(main_window, "Export", "Export cancelled or no output directory specified.")
                
    except Exception as e:
        main_window.log_message(f"❌ Export error: {str(e)}")


def export_via_function(main_window):
    """Export via existing IDE file"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File for Export Matching",
            "",
            "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
        )
        
        if not ide_file:
            return
        
        # Parse IDE file to get list of files to export
        files_to_export = []
        with open(ide_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 1:
                        filename = parts[0].strip()
                        files_to_export.append(filename)
        
        if not files_to_export:
            QMessageBox.information(main_window, "Export Via IDE", "No valid entries found in IDE file.")
            return
        
        # Find matching entries in current IMG
        matching_entries = []
        for entry in main_window.current_img.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name in files_to_export:
                matching_entries.append(entry)
        
        if not matching_entries:
            QMessageBox.information(main_window, "Export Via IDE", "No matching entries found in current IMG file.")
            return
        
        # Get export directory
        output_dir = QFileDialog.getExistingDirectory(main_window, "Select Export Directory")
        if not output_dir:
            return
        
        # Export matching entries
        options = {
            'selected_entries': matching_entries,
            'output_directory': output_dir,
            'organize_by_type': False,
            'create_ide_file': True,
            'overwrite_existing': True
        }
        _export_files_threaded(main_window, options)
        
    except Exception as e:
        main_window.log_message(f"❌ Export via error: {str(e)}")


def quick_export_function(main_window):
    """Quick export - organized by file type"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "Quick Export", "No entries selected for export.")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(main_window, "Select Quick Export Directory")
        if not output_dir:
            return
        
        # Quick export with organization
        options = {
            'selected_entries': selected_entries,
            'output_directory': output_dir,
            'organize_by_type': True,
            'create_ide_file': False,
            'overwrite_existing': True
        }
        _export_files_threaded(main_window, options)
        
    except Exception as e:
        main_window.log_message(f"❌ Quick export error: {str(e)}")


def export_all_function(main_window):
    """Export all entries with advanced dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        all_entries = main_window.current_img.entries if hasattr(main_window.current_img, 'entries') else []
        if not all_entries:
            QMessageBox.information(main_window, "Export All", "No entries found in current IMG file.")
            return
        
        dialog = ExportOptionsDialog(all_entries, main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_export_options()
            
            if options['selected_entries'] and options['output_directory']:
                _export_files_threaded(main_window, options)
            else:
                QMessageBox.information(main_window, "Export All", "Export cancelled or no output directory specified.")
                
    except Exception as e:
        main_window.log_message(f"❌ Export all error: {str(e)}")


def dump_all_function(main_window):
    """Dump all entries - no organization, just extract everything"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        all_entries = main_window.current_img.entries if hasattr(main_window.current_img, 'entries') else []
        if not all_entries:
            QMessageBox.information(main_window, "Dump All", "No entries found in current IMG file.")
            return
        
        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(main_window, "Select Dump Directory")
        if not output_dir:
            return
        
        reply = QMessageBox.question(
            main_window,
            "Dump All Entries",
            f"This will extract all {len(all_entries)} entries to the selected directory.\n\n"
            "Continue with dump operation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Dump all entries without organization
            options = {
                'selected_entries': all_entries,
                'output_directory': output_dir,
                'organize_by_type': False,
                'create_ide_file': True,
                'overwrite_existing': True
            }
            _export_files_threaded(main_window, options)
        
    except Exception as e:
        main_window.log_message(f"❌ Dump all error: {str(e)}")


def remove_selected_function(main_window):
    """Remove selected entries from IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "Remove", "No entries selected for removal.")
            return
        
        reply = QMessageBox.question(
            main_window,
            "Remove Selected Entries",
            f"Are you sure you want to remove {len(selected_entries)} selected entries?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            removed_count = 0
            
            for entry in selected_entries:
                if hasattr(main_window.current_img, 'remove_entry'):
                    if main_window.current_img.remove_entry(entry):
                        removed_count += 1
                elif hasattr(main_window.current_img, 'entries'):
                    try:
                        main_window.current_img.entries.remove(entry)
                        removed_count += 1
                    except ValueError:
                        pass
            
            # Update table
            if hasattr(main_window, 'populate_entries_table'):
                main_window.populate_entries_table()
            
            main_window.log_message(f"✅ Removed {removed_count} entries")
            QMessageBox.information(main_window, "Remove Complete", f"Removed {removed_count} entries from IMG file.")
        
    except Exception as e:
        main_window.log_message(f"❌ Remove error: {str(e)}")


def remove_via_entries_function(main_window):
    """Remove entries via IDE file list"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return
        
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File for Removal List",
            "",
            "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
        )
        
        if not ide_file:
            return
        
        # Parse IDE file
        files_to_remove = []
        with open(ide_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 1:
                        filename = parts[0].strip()
                        files_to_remove.append(filename)
        
        if not files_to_remove:
            QMessageBox.information(main_window, "Remove Via IDE", "No valid entries found in IDE file.")
            return
        
        # Find matching entries
        entries_to_remove = []
        for entry in main_window.current_img.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name in files_to_remove:
                entries_to_remove.append(entry)
        
        if not entries_to_remove:
            QMessageBox.information(main_window, "Remove Via IDE", "No matching entries found in current IMG file.")
            return
        
        reply = QMessageBox.question(
            main_window,
            "Remove Via IDE",
            f"Found {len(entries_to_remove)} matching entries to remove.\n\n"
            "Continue with removal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            removed_count = 0
            
            for entry in entries_to_remove:
                if hasattr(main_window.current_img, 'remove_entry'):
                    if main_window.current_img.remove_entry(entry):
                        removed_count += 1
                elif hasattr(main_window.current_img, 'entries'):
                    try:
                        main_window.current_img.entries.remove(entry)
                        removed_count += 1
                    except ValueError:
                        pass
            
            # Update table
            if hasattr(main_window, 'populate_entries_table'):
                main_window.populate_entries_table()
            
            main_window.log_message(f"✅ Removed {removed_count} entries via IDE")
            QMessageBox.information(main_window, "Remove Complete", f"Removed {removed_count} entries from IMG file.")
        
    except Exception as e:
        main_window.log_message(f"❌ Remove via error: {str(e)}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_selected_entries(main_window):
    """Get currently selected entries from the table"""
    try:
        selected_entries = []
        
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            for row in selected_rows:
                if hasattr(main_window, 'current_img') and main_window.current_img:
                    if hasattr(main_window.current_img, 'entries') and row < len(main_window.current_img.entries):
                        selected_entries.append(main_window.current_img.entries[row])
        
        return selected_entries
        
    except Exception:
        return []


def _import_files_threaded(main_window, import_options):
    """Import files using background thread"""
    try:
        # Create progress dialog
        progress_dialog = QDialog(main_window)
        progress_dialog.setWindowTitle("Importing Files...")
        progress_dialog.setMinimumSize(400, 150)
        progress_dialog.setModal(True)
        
        layout = QVBoxLayout(progress_dialog)
        
        progress_label = QLabel("Preparing import...")
        layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, len(import_options['files']))
        layout.addWidget(progress_bar)
        
        cancel_btn = QPushButton("Cancel")
        layout.addWidget(cancel_btn)
        
        # Create and start import thread
        import_thread = ImportThread(main_window.current_img, import_options)
        
        def update_progress(current, message):
            progress_bar.setValue(current)
            progress_label.setText(message)
        
        def import_finished(success_count, error_count):
            progress_dialog.close()
            
            # Update table
            if hasattr(main_window, 'populate_entries_table'):
                main_window.populate_entries_table()
            
            # Show results
            message = f"Import completed!\n\nSuccessfully imported: {success_count}\nFailed: {error_count}"
            QMessageBox.information(main_window, "Import Complete", message)
            main_window.log_message(f"✅ Import: {success_count} success, {error_count} failed")
        
        def cancel_import():
            if import_thread.isRunning():
                import_thread.terminate()
                import_thread.wait()
            progress_dialog.close()
        
        import_thread.progress_updated.connect(update_progress)
        import_thread.import_completed.connect(import_finished)
        cancel_btn.clicked.connect(cancel_import)
        
        import_thread.start()
        progress_dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Import thread error: {str(e)}")


def _export_files_threaded(main_window, export_options):
    """Export files using background thread"""
    try:
        # Create progress dialog
        progress_dialog = QDialog(main_window)
        progress_dialog.setWindowTitle("Exporting Files...")
        progress_dialog.setMinimumSize(400, 150)
        progress_dialog.setModal(True)
        
        layout = QVBoxLayout(progress_dialog)
        
        progress_label = QLabel("Preparing export...")
        layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, len(export_options['selected_entries']))
        layout.addWidget(progress_bar)
        
        cancel_btn = QPushButton("Cancel")
        layout.addWidget(cancel_btn)
        
        # Create and start export thread
        export_thread = ExportThread(main_window.current_img, export_options)
        
        def update_progress(current, message):
            progress_bar.setValue(current)
            progress_label.setText(message)
        
        def export_finished(success_count, error_count):
            progress_dialog.close()
            
            # Show results
            message = f"Export completed!\n\nSuccessfully exported: {success_count}\nFailed: {error_count}"
            QMessageBox.information(main_window, "Export Complete", message)
            main_window.log_message(f"✅ Export: {success_count} success, {error_count} failed")
        
        def cancel_export():
            if export_thread.isRunning():
                export_thread.terminate()
                export_thread.wait()
            progress_dialog.close()
        
        export_thread.progress_updated.connect(update_progress)
        export_thread.export_completed.connect(export_finished)
        cancel_btn.clicked.connect(cancel_export)
        
        export_thread.start()
        progress_dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Export thread error: {str(e)}")


# ============================================================================
# MENU INTEGRATION
# ============================================================================

def add_import_export_menus(main_window):
    """Add import/export menus to main window"""
    try:
        # Get or create File menu
        if hasattr(main_window, 'menuBar'):
            menubar = main_window.menuBar()
            file_menu = None
            
            # Find existing File menu
            for action in menubar.actions():
                if action.text() == "File":
                    file_menu = action.menu()
                    break
            
            # Create File menu if it doesn't exist
            if not file_menu:
                file_menu = menubar.addMenu("File")
            
            # Add import submenu
            import_menu = file_menu.addMenu("Import")
            
            import_files_action = import_menu.addAction("Import Files...")
            import_files_action.setShortcut("Ctrl+I")
            import_files_action.triggered.connect(lambda: import_files_function(main_window))
            
            import_via_action = import_menu.addAction("Import Via...")
            import_via_action.triggered.connect(lambda: import_via_function(main_window))
            
            # Add export submenu
            export_menu = file_menu.addMenu("Export")
            
            export_selected_action = export_menu.addAction("Export Selected...")
            export_selected_action.setShortcut("Ctrl+E")
            export_selected_action.triggered.connect(lambda: export_selected_function(main_window))
            
            export_via_action = export_menu.addAction("Export Via IDE...")
            export_via_action.triggered.connect(lambda: export_via_function(main_window))
            
            quick_export_action = export_menu.addAction("Quick Export")
            quick_export_action.setShortcut("Ctrl+Shift+E")
            quick_export_action.triggered.connect(lambda: quick_export_function(main_window))
            
            export_all_action = export_menu.addAction("Export All...")
            export_all_action.triggered.connect(lambda: export_all_function(main_window))
            
            export_menu.addSeparator()
            
            dump_all_action = export_menu.addAction("Dump All Entries")
            dump_all_action.triggered.connect(lambda: dump_all_function(main_window))
            
            main_window.log_message("✅ Import/Export menus added")
        
    except Exception as e:
        main_window.log_message(f"❌ Menu creation error: {str(e)}")


# ============================================================================
# MAIN INTEGRATION FUNCTION
# ============================================================================

def integrate_clean_import_export(main_window):
    """Integrate clean import/export functions to main window"""
    try:
        # Replace existing methods with clean versions
        main_window.import_files = lambda: import_files_function(main_window)
        main_window.import_files_via = lambda: import_via_function(main_window)
        main_window.export_selected = lambda: export_selected_function(main_window)
        main_window.export_selected_via = lambda: export_via_function(main_window)
        main_window.quick_export_selected = lambda: quick_export_function(main_window)
        main_window.export_all_entries = lambda: export_all_function(main_window)
        main_window.remove_via_entries = lambda: remove_via_entries_function(main_window)
        main_window.remove_selected = lambda: remove_selected_function(main_window)
        main_window.dump_all_entries = lambda: dump_all_function(main_window)

        # Add convenience method for getting selected entries
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)

        # Add menus
        add_import_export_menus(main_window)

        main_window.log_message("✅ Clean import/export functions integrated")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Integration error: {str(e)}")
        return False


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Dialog classes
    'ImportOptionsDialog',
    'ExportOptionsDialog',
    
    # Thread classes
    'ImportThread',
    'ExportThread',
    
    # Main functions
    'import_files_function',
    'import_via_function',
    'import_from_ide_file',
    'import_directory_function',
    'export_selected_function',
    'export_via_function',
    'export_all_function',
    'quick_export_function',
    'remove_selected_function',
    'remove_via_entries_function',
    'dump_all_function',
    
    # Utility functions
    'get_selected_entries',
    'add_import_export_menus',
    
    # Integration function
    'integrate_clean_import_export'
]