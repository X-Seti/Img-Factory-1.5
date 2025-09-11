#this belongs in methods.col_utilities.py - Version: 9
# X-Seti - July23 2025 - IMG Factory 1.5 - COL Utilities with IMG Debug System
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
COL Utilities - Utility functions and batch processing for COL files
Ported from old-ignore-folder
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QProgressBar, QLabel, QFileDialog, QMessageBox, QCheckBox,
    QSpinBox, QLineEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Import IMG debug system (ONLY debug change)
from debug.img_debug_functions import img_debugger
from methods.col_core_classes import COLFile, COLModel

##Methods list -
# add_files
# add_file_to_table
# browse_output_dir
# clear_files
# merge_nearby_vertices
# optimize_model_geometry
# process_file
# process_single_file
# remove_duplicate_vertices
# remove_files
# remove_unused_vertices
# start_processing

##Classes -
# COLBatchProcessor
# COLBatchWorker
# COLOptimizer

class COLBatchProcessor(QDialog):
    """Dialog for batch processing COL files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Batch Processor")
        self.setModal(True)
        self.resize(800, 600)
        
        self.file_paths: List[str] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup batch processor UI"""
        layout = QVBoxLayout(self)
        
        # File list
        files_group = QGroupBox("COL Files")
        files_layout = QVBoxLayout(files_group)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["File Name", "Size", "Status"])
        self.files_table.setColumnWidth(0, 300)
        self.files_table.setColumnWidth(1, 100)
        self.files_table.setColumnWidth(2, 100)
        files_layout.addWidget(self.files_table)
        
        # File buttons
        file_buttons = QHBoxLayout()
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self.add_files)
        self.remove_files_btn = QPushButton("Remove Selected")
        self.remove_files_btn.clicked.connect(self.remove_files)
        self.clear_files_btn = QPushButton("Clear All")
        self.clear_files_btn.clicked.connect(self.clear_files)
        
        file_buttons.addWidget(self.add_files_btn)
        file_buttons.addWidget(self.remove_files_btn)
        file_buttons.addWidget(self.clear_files_btn)
        file_buttons.addStretch()
        files_layout.addLayout(file_buttons)
        
        layout.addWidget(files_group)
        
        # Operations
        operations_group = QGroupBox("Operations")
        operations_layout = QFormLayout(operations_group)
        
        self.remove_duplicates_cb = QCheckBox("Remove duplicate vertices")
        self.remove_unused_cb = QCheckBox("Remove unused vertices")
        self.merge_nearby_cb = QCheckBox("Merge nearby vertices")
        self.merge_threshold_spin = QSpinBox()
        self.merge_threshold_spin.setRange(1, 100)
        self.merge_threshold_spin.setValue(1)
        self.merge_threshold_spin.setSuffix(" units")
        
        operations_layout.addRow(self.remove_duplicates_cb)
        operations_layout.addRow(self.remove_unused_cb)
        operations_layout.addRow(self.merge_nearby_cb, self.merge_threshold_spin)
        
        # Output directory
        self.output_dir_edit = QLineEdit()
        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.browse_output_btn)
        operations_layout.addRow("Output Directory:", output_layout)
        
        layout.addWidget(operations_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
    
    def add_files(self): #vers 9
        """Add COL files to batch list"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select COL Files", "", "COL Files (*.col);;All Files (*)"
        )
        
        for file_path in files:
            self.add_file_to_table(file_path)
    
    def add_file_to_table(self, file_path: str): #vers 9
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
    
    def remove_files(self): #vers 9
        """Remove selected files"""
        selected_rows = set()
        for item in self.files_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in sorted(selected_rows, reverse=True):
            self.files_table.removeRow(row)
    
    def clear_files(self): #vers 9
        """Clear all files"""
        self.files_table.setRowCount(0)
    
    def browse_output_dir(self): #vers 9
        """Browse for output directory"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_dir_edit.setText(folder)
    
    def start_processing(self): #vers 9
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


    def open_col_batch_processor_dialog(main_window): #vers 1
        """Open batch processor dialog - wrapper function"""
        try:
            from components.col_manager import open_col_batch_proc_dialog
            return open_col_batch_proc_dialog(main_window)
        except Exception as e:
            img_debugger.error(f"Failed to open batch processor: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "COL Batch Processor",
                                "COL Batch Processor is not yet available.")

    def analyze_col_file_dialog(main_window): #vers 1
        """Open COL analysis dialog"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "COL Analyzer",
                                "COL file analysis feature is coming soon!")
            img_debugger.debug("COL analyzer placeholder shown")
        except Exception as e:
            img_debugger.error(f"COL analyzer error: {e}")

    def open_col_editor_dialog(main_window): #vers 1
        """Open COL editor dialog"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "COL Editor",
                                "COL editor feature is coming soon!")
            img_debugger.debug("COL editor placeholder shown")
        except Exception as e:
            img_debugger.error(f"COL editor error: {e}")


    def open_col_batch_processor(main_window): #vers 1
        """Open COL batch processor dialog"""
        try:
            from components.col_manager import open_col_batch_proc_dialog
            open_col_batch_proc_dialog(main_window)
        except ImportError:
            # Fallback implementation
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "COL Batch Processor",
                                "COL Batch Processor is not yet available.\n"
                                "This feature is coming soon!")
            img_debugger.debug("COL batch processor placeholder shown")


    def process_file(self, file_path: str) -> bool: #vers 9
        """Process a single COL file"""
        try:
            # Load COL file
            col_file = COLFile(file_path)
            if not col_file.load_from_file(file_path):
                img_debugger.error(f"Failed to load COL file: {file_path}")
                return False
            
            # Apply operations
            optimizer = COLOptimizer()
            
            for model in col_file.models:
                if self.remove_duplicates_cb.isChecked():
                    optimizer.remove_duplicate_vertices(model)
                
                if self.remove_unused_cb.isChecked():
                    optimizer.remove_unused_vertices(model)
                
                if self.merge_nearby_cb.isChecked():
                    threshold = self.merge_threshold_spin.value() / 100.0
                    optimizer.merge_nearby_vertices(model, threshold)
            
            # Save file
            output_dir = self.output_dir_edit.text()
            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(file_path))
                # Save would go here - not implemented in basic version
                img_debugger.debug(f"Would save to: {output_path}")
            
            return True
            
        except Exception as e:
            img_debugger.error(f"Error processing COL file {file_path}: {str(e)}")
            return False


class COLBatchWorker(QThread):
    """Worker thread for batch COL processing"""
    
    progress_update = pyqtSignal(int, str)  # progress, status
    file_processed = pyqtSignal(str, bool, str)  # file_path, success, message
    finished_all = pyqtSignal(int, int)  # total_files, successful_files
    
    def __init__(self, file_paths: List[str], operations: Dict[str, Any]):
        super().__init__()
        self.file_paths = file_paths
        self.operations = operations
        self.should_stop = False
    
    def stop(self):
        """Stop processing"""
        self.should_stop = True
    
    def run(self):
        """Process all files"""
        total_files = len(self.file_paths)
        successful_files = 0
        
        img_debugger.debug(f"Starting batch processing of {total_files} COL files")
        
        for i, file_path in enumerate(self.file_paths):
            if self.should_stop:
                break
            
            progress = int((i / total_files) * 100)
            file_name = os.path.basename(file_path)
            self.progress_update.emit(progress, f"Processing {file_name}...")
            
            success, message = self.process_single_file(file_path)
            self.file_processed.emit(file_path, success, message)
            
            if success:
                successful_files += 1
        
        self.progress_update.emit(100, "Processing complete")
        self.finished_all.emit(total_files, successful_files)
    
    def process_single_file(self, file_path: str) -> Tuple[bool, str]: #vers 9
        """Process a single COL file"""
        try:
            # Load COL file
            col_file = COLFile(file_path)
            if not col_file.load_from_file(file_path):
                return False, "Failed to load COL file"
            
            # Get original stats
            original_stats = col_file.get_total_stats()
            
            # Apply operations
            optimizer = COLOptimizer()
            
            for model in col_file.models:
                # Apply selected operations
                if self.operations.get('remove_duplicates', False):
                    optimizer.remove_duplicate_vertices(model)
                
                if self.operations.get('remove_unused', False):
                    optimizer.remove_unused_vertices(model)
                
                if self.operations.get('merge_nearby', False):
                    threshold = self.operations.get('merge_threshold', 0.01)
                    optimizer.merge_nearby_vertices(model, threshold)
            
            # Save if output directory specified
            output_dir = self.operations.get('output_dir')
            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(file_path))
                # Save would go here - not implemented in basic version
                img_debugger.debug(f"Would save to: {output_path}")
            
            # Generate report
            new_stats = col_file.get_total_stats()
            changes = []
            for key in original_stats:
                if original_stats[key] != new_stats[key]:
                    changes.append(f"{key}: {original_stats[key]} → {new_stats[key]}")
            
            if changes:
                return True, f"Modified: {', '.join(changes)}"
            else:
                return True, "No changes needed"
                
        except Exception as e:
            return False, f"Processing error: {str(e)}"


class COLOptimizer:
    """Class for optimizing COL models"""
    
    def optimize_model_geometry(self, model: COLModel) -> bool: #vers 9
        """Optimize model geometry"""
        try:
            original_stats = model.get_total_stats()
            
            # Apply optimizations
            self.remove_duplicate_vertices(model)
            self.remove_unused_vertices(model)
            
            # Update model
            model.update_flags()
            model.update_bounding_box()
            
            new_stats = model.get_total_stats()
            
            # Check if changes were made
            changes_made = any(original_stats[key] != new_stats[key] for key in original_stats)
            
            if changes_made:
                img_debugger.debug(f"Model optimized: {original_stats} → {new_stats}")
            
            return changes_made
            
        except Exception as e:
            img_debugger.error(f"Error optimizing model: {str(e)}")
            return False
    
    def remove_duplicate_vertices(self, model: COLModel): #vers 9
        """Remove duplicate vertices from model"""
        try:
            if not model.vertices:
                return
            
            unique_vertices = []
            vertex_map = {}
            
            for i, vertex in enumerate(model.vertices):
                pos_key = vertex.position
                if pos_key not in vertex_map:
                    vertex_map[pos_key] = len(unique_vertices)
                    unique_vertices.append(vertex)
            
            # Update faces to use new vertex indices
            for face in model.faces:
                new_indices = []
                for old_index in face.vertex_indices:
                    if old_index < len(model.vertices):
                        old_pos = model.vertices[old_index].position
                        new_index = vertex_map.get(old_pos, old_index)
                        new_indices.append(new_index)
                    else:
                        new_indices.append(old_index)
                face.vertex_indices = tuple(new_indices)
            
            removed_count = len(model.vertices) - len(unique_vertices)
            model.vertices = unique_vertices
            
            if removed_count > 0:
                img_debugger.debug(f"Removed {removed_count} duplicate vertices")
                
        except Exception as e:
            img_debugger.error(f"Error removing duplicate vertices: {str(e)}")
    
    def remove_unused_vertices(self, model: COLModel): #vers 9
        """Remove unused vertices from model"""
        try:
            if not model.vertices or not model.faces:
                return
            
            # Find used vertex indices
            used_indices = set()
            for face in model.faces:
                used_indices.update(face.vertex_indices)
            
            # Create mapping from old to new indices
            vertex_map = {}
            new_vertices = []
            
            for old_index in sorted(used_indices):
                if old_index < len(model.vertices):
                    vertex_map[old_index] = len(new_vertices)
                    new_vertices.append(model.vertices[old_index])
            
            # Update faces
            for face in model.faces:
                new_indices = []
                for old_index in face.vertex_indices:
                    new_index = vertex_map.get(old_index, 0)
                    new_indices.append(new_index)
                face.vertex_indices = tuple(new_indices)
            
            removed_count = len(model.vertices) - len(new_vertices)
            model.vertices = new_vertices
            
            if removed_count > 0:
                img_debugger.debug(f"Removed {removed_count} unused vertices")
                
        except Exception as e:
            img_debugger.error(f"Error removing unused vertices: {str(e)}")
    
    def merge_nearby_vertices(self, model: COLModel, threshold: float = 0.01): #vers 9
        """Merge vertices that are very close together"""
        try:
            if not model.vertices or threshold <= 0:
                return
            
            merged_count = 0
            vertex_map = {}
            new_vertices = []
            
            for i, vertex in enumerate(model.vertices):
                merged = False
                
                # Check against existing vertices
                for j, existing_vertex in enumerate(new_vertices):
                    # Calculate distance
                    dx = vertex.position[0] - existing_vertex.position[0]
                    dy = vertex.position[1] - existing_vertex.position[1]
                    dz = vertex.position[2] - existing_vertex.position[2]
                    distance = (dx*dx + dy*dy + dz*dz) ** 0.5
                    
                    if distance < threshold:
                        vertex_map[i] = j
                        merged = True
                        merged_count += 1
                        break
                
                if not merged:
                    vertex_map[i] = len(new_vertices)
                    new_vertices.append(vertex)
            
            # Update faces
            for face in model.faces:
                new_indices = []
                for old_index in face.vertex_indices:
                    new_index = vertex_map.get(old_index, old_index)
                    new_indices.append(new_index)
                face.vertex_indices = tuple(new_indices)
            
            model.vertices = new_vertices
            
            if merged_count > 0:
                img_debugger.debug(f"Merged {merged_count} nearby vertices")
                
        except Exception as e:
            img_debugger.error(f"Error merging nearby vertices: {str(e)}")
