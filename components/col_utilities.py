#this belongs in components/col_utilities.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Utilities
# COL file utilities and operations using IMG debug system

"""
COL Utilities - COL file operations and dialogs
Provides batch processing, analysis, and utility functions for COL files
"""

import os
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel,
    QGroupBox, QCheckBox, QSpinBox, QLineEdit, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt

# Import IMG debug system and COL classes
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile, COLModel, COLVersion

##Methods list -
# analyze_col_file_dialog
# analyze_col_from_img_entry
# analyze_col_model
# edit_col_from_img_entry
# export_col_to_img
# load_col_from_img_entry
# open_col_batch_proc_dialog
# open_col_batch_processor
# open_col_editor

##Classes -
# COLBatchProcessor

class COLBatchProcessor(QDialog):
    """COL batch processing dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Batch Processor")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup batch processor UI"""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel("COL Batch Processor - Process multiple COL files")
        layout.addWidget(info_label)
        
        # File list
        files_group = QGroupBox("COL Files")
        files_layout = QVBoxLayout(files_group)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["File", "Size", "Status"])
        files_layout.addWidget(self.files_table)
        
        # File buttons
        file_buttons = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_files)
        file_buttons.addWidget(add_files_btn)
        
        remove_files_btn = QPushButton("Remove Selected")
        remove_files_btn.clicked.connect(self.remove_files)
        file_buttons.addWidget(remove_files_btn)
        
        clear_files_btn = QPushButton("Clear All")
        clear_files_btn.clicked.connect(self.clear_files)
        file_buttons.addWidget(clear_files_btn)
        
        file_buttons.addStretch()
        files_layout.addLayout(file_buttons)
        layout.addWidget(files_group)
        
        # Operations group
        ops_group = QGroupBox("Operations")
        ops_layout = QVBoxLayout(ops_group)
        
        self.validate_check = QCheckBox("Validate COL files")
        self.validate_check.setChecked(True)
        ops_layout.addWidget(self.validate_check)
        
        self.analyze_check = QCheckBox("Analyze structure")
        ops_layout.addWidget(self.analyze_check)
        
        self.convert_check = QCheckBox("Convert version")
        ops_layout.addWidget(self.convert_check)
        
        layout.addWidget(ops_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        start_btn = QPushButton("Start Processing")
        start_btn.clicked.connect(self.start_processing)
        button_layout.addWidget(start_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def add_files(self): #vers 1
        """Add COL files to batch list"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select COL Files", "", "COL Files (*.col);;All Files (*)"
        )
        
        for file_path in files:
            self.add_file_to_table(file_path)
    
    def add_file_to_table(self, file_path: str): #vers 1
        """Add file to the table"""
        row = self.files_table.rowCount()
        self.files_table.insertRow(row)
        
        # File name
        file_name = os.path.basename(file_path)
        self.files_table.setItem(row, 0, QTableWidgetItem(file_name))
        
        # File size
        try:
            size = os.path.getsize(file_path)
            size_text = f"{size:,} bytes"
        except:
            size_text = "Unknown"
        self.files_table.setItem(row, 1, QTableWidgetItem(size_text))
        
        # Status
        self.files_table.setItem(row, 2, QTableWidgetItem("Ready"))
        
        # Store full path in item data
        item = self.files_table.item(row, 0)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
    
    def remove_files(self): #vers 1
        """Remove selected files"""
        selected_rows = set()
        for item in self.files_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in sorted(selected_rows, reverse=True):
            self.files_table.removeRow(row)
    
    def clear_files(self): #vers 1
        """Clear all files"""
        self.files_table.setRowCount(0)
    
    def start_processing(self): #vers 1
        """Start batch processing"""
        row_count = self.files_table.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "No Files", "Please add COL files to process.")
            return
        
        img_debugger.debug(f"Starting COL batch processing of {row_count} files")
        
        for row in range(row_count):
            item = self.files_table.item(row, 0)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            
            # Update progress
            progress = int((row / row_count) * 100)
            self.progress_bar.setValue(progress)
            
            # Update status
            self.files_table.setItem(row, 2, QTableWidgetItem("Processing..."))
            
            # Process file
            success = self.process_file(file_path)
            
            # Update status
            status = "Complete" if success else "Failed"
            self.files_table.setItem(row, 2, QTableWidgetItem(status))
        
        self.progress_bar.setValue(100)
        img_debugger.success("COL batch processing complete")
        QMessageBox.information(self, "Complete", "Batch processing finished.")
    
    def process_file(self, file_path: str) -> bool: #vers 1
        """Process individual COL file"""
        try:
            if self.validate_check.isChecked():
                from components.col_validator import validate_col_file
                if not validate_col_file(None, file_path):
                    return False
            
            if self.analyze_check.isChecked():
                col_file = COLFile(file_path)
                if not col_file.load():
                    return False
                
                # Perform analysis
                analyze_col_model(col_file.models[0] if col_file.models else None)
            
            return True
            
        except Exception as e:
            img_debugger.error(f"Error processing {file_path}: {e}")
            return False

def open_col_batch_proc_dialog(main_window) -> bool: #vers 1
    """Open COL batch processor dialog"""
    try:
        img_debugger.debug("Opening COL batch processor")
        
        processor = COLBatchProcessor(main_window)
        result = processor.exec()
        
        if result:
            img_debugger.success("COL batch processor completed")
        else:
            img_debugger.debug("COL batch processor cancelled")
        
        return result == QDialog.DialogCode.Accepted
        
    except Exception as e:
        img_debugger.error(f"Error opening COL batch processor: {e}")
        return False

def open_col_batch_processor(main_window): #vers 1
    """Open COL batch processor"""
    try:
        processor = COLBatchProcessor(main_window)
        processor.exec()
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open batch processor: {str(e)}")

def open_col_editor(main_window): #vers 1
    """Open COL editor"""
    try:
        # Try to open COL editor if available
        try:
            from components.col_editor import COLEditorDialog
            editor = COLEditorDialog(main_window)
            editor.exec()
        except ImportError:
            QMessageBox.information(main_window, "COL Editor", 
                "COL editor will be available in a future version.")
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open COL editor: {str(e)}")

def analyze_col_file_dialog(main_window): #vers 1
    """Analyze COL file with file dialog"""
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            main_window, "Select COL File to Analyze", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            img_debugger.debug(f"Analyzing COL file: {os.path.basename(file_path)}")
            
            col_file = COLFile(file_path)
            if col_file.load():
                analysis = []
                analysis.append(f"COL File Analysis: {os.path.basename(file_path)}")
                analysis.append(f"File Size: {col_file.file_size:,} bytes")
                analysis.append(f"Models: {len(col_file.models)}")
                analysis.append("")
                
                for i, model in enumerate(col_file.models):
                    analysis.extend(analyze_col_model(model))
                    if i < len(col_file.models) - 1:
                        analysis.append("")
                
                # Show analysis dialog
                dialog = QDialog(main_window)
                dialog.setWindowTitle("COL Analysis")
                dialog.resize(600, 400)
                
                layout = QVBoxLayout(dialog)
                
                text_edit = QTextEdit()
                text_edit.setPlainText("\n".join(analysis))
                text_edit.setReadOnly(True)
                layout.addWidget(text_edit)
                
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.close)
                layout.addWidget(close_btn)
                
                dialog.exec()
            else:
                QMessageBox.critical(main_window, "Error", f"Failed to load COL file: {col_file.load_error}")
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL file: {str(e)}")

def analyze_col_model(model: Optional[COLModel]) -> List[str]: #vers 1
    """Analyze COL model and return analysis text"""
    if not model:
        return ["No model data available"]
    
    analysis = []
    analysis.append(f"Model: {model.name}")
    analysis.append(f"Version: COL {model.version.value}")
    analysis.append(f"Model ID: {model.model_id}")
    analysis.append(f"Spheres: {len(model.spheres)}")
    analysis.append(f"Boxes: {len(model.boxes)}")
    analysis.append(f"Vertices: {len(model.vertices)}")
    analysis.append(f"Faces: {len(model.faces)}")
    
    # Bounding box info
    if model.bounding_box:
        bbox = model.bounding_box
        analysis.append(f"Bounding Box:")
        analysis.append(f"  Center: ({bbox.center.x:.2f}, {bbox.center.y:.2f}, {bbox.center.z:.2f})")
        analysis.append(f"  Radius: {bbox.radius:.2f}")
    
    return analysis

def edit_col_from_img_entry(main_window, row): #vers 1
    """Edit COL file from IMG entry"""
    try:
        # Get entry from row
        if hasattr(main_window, 'current_img') and main_window.current_img:
            entries = main_window.current_img.entries
            if row < len(entries):
                entry = entries[row]
                # Implementation for editing COL from IMG entry
                main_window.log_message(f"COL editing from IMG entry will be implemented")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to edit COL: {str(e)}")

def analyze_col_from_img_entry(main_window, row): #vers 1
    """Analyze COL file from IMG entry"""
    try:
        # Get entry from row
        if hasattr(main_window, 'current_img') and main_window.current_img:
            entries = main_window.current_img.entries
            if row < len(entries):
                entry = entries[row]
                # Implementation for analyzing COL from IMG entry
                main_window.log_message(f"COL analysis from IMG entry will be implemented")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL: {str(e)}")

def load_col_from_img_entry(main_window, entry): #vers 1
    """Load COL file from IMG entry"""
    try:
        # Implementation for loading COL from IMG entry
        img_debugger.debug(f"Loading COL from IMG entry: {entry.name}")
        return True
        
    except Exception as e:
        img_debugger.error(f"Failed to load COL from IMG entry: {e}")
        return False

def export_col_to_img(main_window, col_file, img_file): #vers 1
    """Export COL file to IMG"""
    try:
        # Implementation for exporting COL to IMG
        img_debugger.debug(f"Exporting COL to IMG")
        return True
        
    except Exception as e:
        img_debugger.error(f"Failed to export COL to IMG: {e}")
        return False