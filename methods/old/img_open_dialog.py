#this belongs in components/ img_open_functions_dialog.py - version 16

#!/usr/bin/env python3
"""
X-Seti - June25 2025 - IMG Factory 1.5
Combined Open Dialog for IMG, COL, TXD files
Supports multiple file selection and validation
"""

import os
from typing import List, Dict, Optional, Set, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QGroupBox, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit, QSplitter,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap


class FileValidationThread(QThread):
    """Thread for validating files in background"""
    
    file_validated = pyqtSignal(str, dict)  # file_path, validation_info
    validation_complete = pyqtSignal()
    
    def __init__(self, file_paths: List[str]):
        super().__init__()
        self.file_paths = file_paths
        self.validation_results = {}
    
    def run(self):
        """Validate files"""
        for file_path in self.file_paths:
            validation_info = self._validate_file(file_path)
            self.validation_results[file_path] = validation_info
            self.file_validated.emit(file_path, validation_info)
        
        self.validation_complete.emit()
    
    def _validate_file(self, file_path: str) -> Dict:
        """Validate individual file"""
        info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': 0,
            'type': 'Unknown',
            'valid': False,
            'status': 'Checking...',
            'notes': '',
            'can_open': False
        }
        
        try:
            if not os.path.exists(file_path):
                info['status'] = 'Error'
                info['notes'] = 'File not found'
                return info
            
            # Get file info
            info['size'] = os.path.getsize(file_path)
            ext = os.path.splitext(file_path)[1].lower()
            
            # Determine file type and validation
            if ext == '.img':
                info['type'] = 'IMG Archive'
                info['valid'] = self._validate_img_file(file_path)
                info['can_open'] = info['valid']
            elif ext == '.col':
                info['type'] = 'Collision Data'
                info['valid'] = self._validate_col_file(file_path)
                info['can_open'] = info['valid']
            elif ext == '.txd':
                info['type'] = 'Texture Dictionary'
                info['valid'] = self._validate_txd_file(file_path)
                info['can_open'] = info['valid']
            elif ext == '.dff':
                info['type'] = 'Model Data'
                info['valid'] = self._validate_dff_file(file_path)
                info['can_open'] = info['valid']
            else:
                info['type'] = f'{ext.upper()} File'
                info['valid'] = True  # Allow unknown types
                info['can_open'] = True
            
            # Set status
            if info['valid']:
                info['status'] = 'Valid'
                info['notes'] = f"{info['type']} - {self._format_size(info['size'])}"
            else:
                info['status'] = 'Invalid'
                info['notes'] = f"Invalid {info['type']} format"
            
        except Exception as e:
            info['status'] = 'Error'
            info['notes'] = f"Validation failed: {str(e)}"
        
        return info
    
    def _validate_img_file(self, file_path: str) -> bool:
        """Validate IMG file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if len(header) >= 4:
                    # Check for IMG Version 2 header
                    if header[:4] == b'VER2':
                        return True
                    # Check for Version 1 (look for corresponding DIR file)
                    dir_path = file_path.replace('.img', '.dir')
                    if os.path.exists(dir_path):
                        return True
            return False
        except Exception:
            return False
    
    def _validate_col_file(self, file_path: str) -> bool:
        """Validate COL file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if len(header) >= 4:
                    # Check for COL signatures
                    if header[:4] in [b'COL\x01', b'COL\x02', b'COL\x03', b'COL\x04', b'COLL']:
                        return True
            return False
        except Exception:
            return False
    
    def _validate_txd_file(self, file_path: str) -> bool:
        """Validate TXD file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if len(header) >= 4:
                    # Check for RenderWare TXD signature
                    if header[:4] == b'\x16\x00\x00\x00':
                        return True
            return False
        except Exception:
            return False
    
    def _validate_dff_file(self, file_path: str) -> bool:
        """Validate DFF file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if len(header) >= 4:
                    # Check for RenderWare DFF signatures
                    if header[:4] in [b'\x10\x00\x00\x00', b'\x0E\x00\x00\x00']:
                        return True
            return False
        except Exception:
            return False
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class CombinedOpenDialog(QDialog):
    """Combined dialog for opening IMG, COL, TXD files"""
    
    files_selected = pyqtSignal(list, str)  # file_paths, open_mode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Files - IMG Factory 1.5")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        self.selected_files = []
        self.validation_thread = None
        self.file_info = {}
        
        self._create_ui()
        self._connect_signals()
    
    def _create_ui(self):
        """Create the UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🗂️ Open Files")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin: 10px;")
        layout.addWidget(header)
        
        # Mode selection
        mode_group = QGroupBox("Open Mode")
        mode_layout = QHBoxLayout(mode_group)
        
        self.mode_group = QButtonGroup()
        
        self.single_mode = QRadioButton("Single File (IMG only)")
        self.single_mode.setChecked(True)
        self.mode_group.addButton(self.single_mode, 0)
        mode_layout.addWidget(self.single_mode)
        
        self.multi_mode = QRadioButton("Multiple Files (IMG, COL, TXD, DFF)")
        self.mode_group.addButton(self.multi_mode, 1)
        mode_layout.addWidget(self.multi_mode)
        
        layout.addWidget(mode_group)
        
        # File browser section
        browser_group = QGroupBox("File Selection")
        browser_layout = QVBoxLayout(browser_group)
        
        # Browse buttons
        browse_layout = QHBoxLayout()
        
        self.browse_single_btn = QPushButton("📁 Browse for IMG File")
        self.browse_single_btn.clicked.connect(self._browse_single_file)
        browse_layout.addWidget(self.browse_single_btn)
        
        self.browse_multi_btn = QPushButton("📁 Browse for Multiple Files")
        self.browse_multi_btn.clicked.connect(self._browse_multiple_files)
        self.browse_multi_btn.setEnabled(False)
        browse_layout.addWidget(self.browse_multi_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self._clear_files)
        browse_layout.addWidget(self.clear_btn)
        
        browser_layout.addLayout(browse_layout)
        
        # File list/table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(5)
        self.file_table.setHorizontalHeaderLabels(["Filename", "Type", "Size", "Status", "Notes"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.setAlternatingRowColors(True)
        browser_layout.addWidget(self.file_table)
        
        layout.addWidget(browser_group)
        
        # Validation section
        validation_group = QGroupBox("Validation")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validation_progress = QProgressBar()
        self.validation_progress.setVisible(False)
        validation_layout.addWidget(self.validation_progress)
        
        self.validation_status = QLabel("Ready to select files")
        validation_layout.addWidget(self.validation_status)
        
        layout.addWidget(validation_group)
        
        # Button section
        button_layout = QHBoxLayout()
        
        self.help_btn = QPushButton("❓ Help")
        self.help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(self.help_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("✖️ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.open_btn = QPushButton("✅ Open")
        self.open_btn.clicked.connect(self._open_files)
        self.open_btn.setEnabled(False)
        button_layout.addWidget(self.open_btn)
        
        layout.addLayout(button_layout)
    
    def _on_mode_changed(self, button):
        """Handle mode change"""
        is_multi = button == self.multi_mode
        
        self.browse_single_btn.setEnabled(not is_multi)
        self.browse_multi_btn.setEnabled(is_multi)
        
        # Clear current selection when switching modes
        self._clear_files()
    
    def _browse_single_file(self):
        """Browse for single IMG file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open IMG Archive",
            "",
            "IMG Archives (*.img);;All Files (*)"
        )
        
        if file_path:
            self.selected_files = [file_path]
            self._validate_files()
    
    def _browse_multiple_files(self):
        """Browse for multiple files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Open",
            "",
            "All Supported (*.img *.col *.txd *.dff);;IMG Archives (*.img);;Collision Files (*.col);;Texture Files (*.txd);;Model Files (*.dff);;All Files (*)"
        )
        
        if file_paths:
            self.selected_files = file_paths
            self._validate_files()
    
    def _clear_files(self):
        """Clear selected files"""
        self.selected_files = []
        self.file_info = {}
        self.file_table.setRowCount(0)
        self.validation_status.setText("Ready to select files")
        self.open_btn.setEnabled(False)
    
    def _validate_files(self):
        """Start file validation"""
        if not self.selected_files:
            return
        
        self.validation_progress.setVisible(True)
        self.validation_progress.setRange(0, len(self.selected_files))
        self.validation_progress.setValue(0)
        self.validation_status.setText("Validating files...")
        
        # Start validation thread
        self.validation_thread = FileValidationThread(self.selected_files)
        self.validation_thread.file_validated.connect(self._on_file_validated)
        self.validation_thread.validation_complete.connect(self._on_validation_complete)
        self.validation_thread.start()
    
    def _on_file_validated(self, file_path: str, info: Dict):
        """Handle individual file validation"""
        self.file_info[file_path] = info
        
        # Update progress
        current = len(self.file_info)
        self.validation_progress.setValue(current)
        self.validation_status.setText(f"Validated {current}/{len(self.selected_files)} files")
        
        # Update table
        self._update_file_table()
    
    def _on_validation_complete(self):
        """Handle validation completion"""
        self.validation_progress.setVisible(False)
        
        valid_count = sum(1 for info in self.file_info.values() if info['can_open'])
        total_count = len(self.file_info)
        
        self.validation_status.setText(f"Validation complete: {valid_count}/{total_count} files can be opened")
        self.open_btn.setEnabled(valid_count > 0)
    
    def _update_file_table(self):
        """Update file table with validation results"""
        self.file_table.setRowCount(len(self.file_info))
        
        for row, (file_path, info) in enumerate(self.file_info.items()):
            # Filename
            filename_item = QTableWidgetItem(info['name'])
            if info['can_open']:
                filename_item.setIcon(QIcon("✅"))
            else:
                filename_item.setIcon(QIcon("❌"))
            self.file_table.setItem(row, 0, filename_item)
            
            # Type
            type_item = QTableWidgetItem(info['type'])
            self.file_table.setItem(row, 1, type_item)
            
            # Size
            size_text = self._format_size(info['size']) if info['size'] > 0 else "Unknown"
            size_item = QTableWidgetItem(size_text)
            self.file_table.setItem(row, 2, size_item)
            
            # Status
            status_item = QTableWidgetItem(info['status'])
            if info['status'] == 'Valid':
                status_item.setBackground(QColor(200, 255, 200))
            elif info['status'] == 'Error':
                status_item.setBackground(QColor(255, 200, 200))
            else:
                status_item.setBackground(QColor(255, 255, 200))
            self.file_table.setItem(row, 3, status_item)
            
            # Notes
            notes_item = QTableWidgetItem(info['notes'])
            self.file_table.setItem(row, 4, notes_item)
        
        # Resize columns
        self.file_table.resizeColumnsToContents()
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def _open_files(self):
        """Open selected files"""
        # Get files that can be opened
        valid_files = [path for path, info in self.file_info.items() if info['can_open']]
        
        if not valid_files:
            QMessageBox.warning(self, "No Valid Files", "No files can be opened.")
            return
        
        # Determine mode
        mode = "single" if self.single_mode.isChecked() else "multiple"
        
        # Emit signal with files and mode
        self.files_selected.emit(valid_files, mode)
        self.accept()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
<h3>Combined Open Dialog - IMG Factory 1.5</h3>

<h4>Open Modes:</h4>
<ul>
<li><b>Single File:</b> Open one IMG archive file</li>
<li><b>Multiple Files:</b> Open multiple IMG, COL, TXD, DFF files</li>
</ul>

<h4>Supported File Types:</h4>
<ul>
<li><b>IMG:</b> GTA archive files (Version 1 and 2)</li>
<li><b>COL:</b> Collision data files</li>
<li><b>TXD:</b> Texture dictionary files</li>
<li><b>DFF:</b> 3D model files</li>
</ul>

<h4>Validation:</h4>
<p>Files are automatically validated to ensure they can be opened correctly.</p>
<p>✅ = Valid file, ❌ = Invalid or corrupted file</p>

<h4>Usage:</h4>
<ol>
<li>Select open mode (single or multiple)</li>
<li>Browse for files</li>
<li>Wait for validation to complete</li>
<li>Click Open to proceed</li>
</ol>
        """
        
        QMessageBox.information(self, "Help", help_text)


# Integration function for main application
def show_combined_open_dialog(parent=None) -> Tuple[List[str], str]:
    """Show combined open dialog and return selected files and mode"""
    dialog = CombinedOpenDialog(parent)
    
    selected_files = []
    mode = "single"
    
    def on_files_selected(files, open_mode):
        nonlocal selected_files, mode
        selected_files = files
        mode = open_mode
    
    dialog.files_selected.connect(on_files_selected)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return selected_files, mode
    
    return [], ""


# Utility function to revert to original single IMG open
def open_single_img_file(parent=None) -> str:
    """Original single IMG file open dialog"""
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Open IMG Archive",
        "",
        "IMG Archives (*.img);;All Files (*)"
    )
    return file_path


if __name__ == "__main__":
    # Test the dialog
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    files, mode = show_combined_open_dialog()
    print(f"Selected files: {files}")
    print(f"Mode: {mode}")
    
    sys.exit()
