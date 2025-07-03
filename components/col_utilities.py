#!/usr/bin/env python3
"""
#this belongs in components/col_utilities.py - version 6
X-Seti - June27 2025 - COL Utilities for Img Factory 1.5
Batch processing, optimization, and conversion utilities for COL files
"""

import os
import sys
import json
import math
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QFileDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QTabWidget, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from col_core_classes import (
    COLFile, COLModel, COLSphere, COLBox, COLVertex, COLFace,
    COLVersion, Vector3, BoundingBox
)

class COLBatchProcessor(QThread):
    """Background thread for batch processing COL files"""
    
    progress = pyqtSignal(int, str)  # progress, status
    file_processed = pyqtSignal(str, bool, str)  # file_path, success, message
    finished_all = pyqtSignal(int, int)  # total_files, successful_files
    
    def __init__(self, file_paths: List[str], operations: Dict[str, Any]):
        super().__init__()
        self.file_paths = file_paths
        self.operations = operations
        self.should_cancel = False
    
    def cancel(self):
        """Cancel the batch operation"""
        self.should_cancel = True
    
    def run(self):
        """Run batch processing"""
        total_files = len(self.file_paths)
        successful_files = 0
        
        for i, file_path in enumerate(self.file_paths):
            if self.should_cancel:
                break
            
            # Update progress
            progress = int((i / total_files) * 100)
            file_name = os.path.basename(file_path)
            self.progress.emit(progress, f"Processing {file_name}...")
            
            try:
                success, message = self.process_single_file(file_path)
                if success:
                    successful_files += 1
                
                self.file_processed.emit(file_path, success, message)
                
            except Exception as e:
                self.file_processed.emit(file_path, False, f"Error: {str(e)}")
        
        self.progress.emit(100, "Batch processing complete")
        self.finished_all.emit(total_files, successful_files)
    
    def process_single_file(self, file_path: str) -> Tuple[bool, str]:
        """Process a single COL file"""
        try:
            # Load COL file
            col_file = COLFile(file_path)
            if not col_file.load():
                return False, "Failed to load COL file"
            
            original_stats = col_file.get_total_stats()
            modified = False
            
            # Apply operations
            for model in col_file.models:
                if self.operations.get('optimize_geometry', False):
                    if self.optimize_model_geometry(model):
                        modified = True
                
                if self.operations.get('remove_duplicate_vertices', False):
                    if self.remove_duplicate_vertices(model):
                        modified = True
                
                if self.operations.get('convert_version', False):
                    target_version = self.operations.get('target_version', COLVersion.COL_3)
                    if self.convert_model_version(model, target_version):
                        modified = True
                
                if self.operations.get('calculate_face_groups', False):
                    if self.calculate_face_groups(model):
                        modified = True
                
                if self.operations.get('fix_materials', False):
                    if self.fix_material_assignments(model):
                        modified = True
            
            # Save if modified
            if modified:
                output_path = file_path
                if self.operations.get('backup_original', True):
                    backup_path = file_path + '.backup'
                    import shutil
                    shutil.copy2(file_path, backup_path)
                
                if self.operations.get('output_directory'):
                    output_path = os.path.join(
                        self.operations['output_directory'],
                        os.path.basename(file_path)
                    )
                
                if not col_file.save(output_path):
                    return False, "Failed to save processed file"
            
            new_stats = col_file.get_total_stats()
            
            # Generate report
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
    
    def optimize_model_geometry(self, model: COLModel) -> bool:
        """Optimize model geometry"""
        modified = False
        
        # Remove zero-area faces
        original_face_count = len(model.faces)
        model.faces = [face for face in model.faces if self.is_valid_face(model, face)]
        if len(model.faces) != original_face_count:
            modified = True
        
        # Remove unused vertices
        if self.remove_unused_vertices(model):
            modified = True
        
        # Merge nearby vertices
        if self.merge_nearby_vertices(model):
            modified = True
        
        return modified
    
    def is_valid_face(self, model: COLModel, face: COLFace) -> bool:
        """Check if face is valid (has non-zero area)"""
        if (face.a >= len(model.vertices) or 
            face.b >= len(model.vertices) or 
            face.c >= len(model.vertices)):
            return False
        
        v1 = model.vertices[face.a].position
        v2 = model.vertices[face.b].position
        v3 = model.vertices[face.c].position
        
        # Calculate face area using cross product
        edge1 = v2 - v1
        edge2 = v3 - v1
        
        # Cross product magnitude
        cross_x = edge1.y * edge2.z - edge1.z * edge2.y
        cross_y = edge1.z * edge2.x - edge1.x * edge2.z
        cross_z = edge1.x * edge2.y - edge1.y * edge2.x
        
        area = 0.5 * math.sqrt(cross_x*cross_x + cross_y*cross_y + cross_z*cross_z)
        
        return area > 0.001  # Minimum area threshold
    
    def remove_duplicate_vertices(self, model: COLModel) -> bool:
        """Remove duplicate vertices and update face indices"""
        if not model.vertices:
            return False
        
        # Find duplicates
        vertex_map = {}  # position -> first_index
        index_map = {}   # old_index -> new_index
        new_vertices = []
        
        for i, vertex in enumerate(model.vertices):
            if i in processed:
                continue
            
            group = [i]
            processed.add(i)
            
            # Find nearby vertices
            for j, other_vertex in enumerate(model.vertices):
                if j in processed:
                    continue
                
                distance = (vertex.position - other_vertex.position).magnitude()
                if distance < threshold:
                    group.append(j)
                    processed.add(j)
            
            vertex_groups.append(group)
        
        # Merge groups if any contain multiple vertices
        if len(vertex_groups) < len(model.vertices):
            new_vertices = []
            index_map = {}
            
            for group in vertex_groups:
                # Use first vertex as representative
                representative_idx = group[0]
                new_index = len(new_vertices)
                new_vertices.append(model.vertices[representative_idx])
                
                # Map all group members to the new index
                for old_idx in group:
                    index_map[old_idx] = new_index
            
            # Update faces
            for face in model.faces:
                face.a = index_map[face.a]
                face.b = index_map[face.b]
                face.c = index_map[face.c]
            
            model.vertices = new_vertices
            return True
        
        return False
    
    def convert_model_version(self, model: COLModel, target_version: COLVersion) -> bool:
        """Convert model to target version"""
        if model.version == target_version:
            return False
        
        # Version-specific conversions
        if target_version == COLVersion.COL_1:
            # Converting to COL1 - remove features not supported
            model.face_groups = []
            model.shadow_vertices = []
            model.shadow_faces = []
            
            # Convert compressed vertices back to full precision
            for vertex in model.vertices:
                # No conversion needed - already in full precision
                pass
        
        elif target_version in [COLVersion.COL_2, COLVersion.COL_3]:
            # Converting to COL2/3 - compress vertices
            for vertex in model.vertices:
                # Clamp to COL2/3 limits (-256 to +256)
                vertex.position.x = max(-255.99, min(255.99, vertex.position.x))
                vertex.position.y = max(-255.99, min(255.99, vertex.position.y))
                vertex.position.z = max(-255.99, min(255.99, vertex.position.z))
            
            # Generate face groups if converting to COL3
            if target_version == COLVersion.COL_3:
                self.calculate_face_groups(model)
        
        model.version = target_version
        model.update_flags()
        return True
    
    def calculate_face_groups(self, model: COLModel) -> bool:
        """Calculate face groups for optimization"""
        if not model.faces or len(model.faces) < 80:
            # Face groups only needed for large meshes
            return False
        
        # Simple spatial grouping algorithm
        model.face_groups = []
        faces_per_group = min(50, max(10, len(model.faces) // 20))
        
        for i in range(0, len(model.faces), faces_per_group):
            end_idx = min(i + faces_per_group, len(model.faces))
            
            # Calculate bounding box for this group
            min_x = min_y = min_z = float('inf')
            max_x = max_y = max_z = float('-inf')
            
            for face_idx in range(i, end_idx):
                face = model.faces[face_idx]
                
                # Check all vertices of this face
                for vertex_idx in [face.a, face.b, face.c]:
                    if vertex_idx < len(model.vertices):
                        pos = model.vertices[vertex_idx].position
                        min_x = min(min_x, pos.x)
                        min_y = min(min_y, pos.y)
                        min_z = min(min_z, pos.z)
                        max_x = max(max_x, pos.x)
                        max_y = max(max_y, pos.y)
                        max_z = max(max_z, pos.z)
            
            # Create face group
            from col_core_classes import COLFaceGroup
            face_group = COLFaceGroup(
                min=Vector3(min_x, min_y, min_z),
                max=Vector3(max_x, max_y, max_z),
                start_face=i,
                end_face=end_idx - 1
            )
            model.face_groups.append(face_group)
        
        return True
    
    def fix_material_assignments(self, model: COLModel) -> bool:
        """Fix invalid material assignments"""
        modified = False
        
        # Fix face materials
        for face in model.faces:
            if face.material > 17:  # Max material ID
                face.material = 0  # Default material
                modified = True
        
        # Fix sphere materials
        for sphere in model.spheres:
            if sphere.surface.material > 17:
                sphere.surface.material = 0
                modified = True
        
        # Fix box materials
        for box in model.boxes:
            if box.surface.material > 17:
                box.surface.material = 0
                modified = True
        
        return modified

class COLBatchDialog(QDialog):
    """Dialog for batch processing COL files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Batch Processor")
        self.setMinimumSize(800, 600)
        self.file_paths: List[str] = []
        self.processor: Optional[COLBatchProcessor] = None
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the batch dialog UI"""
        layout = QVBoxLayout(self)
        
        # File selection
        file_group = QGroupBox("Files")
        file_layout = QVBoxLayout(file_group)
        
        file_buttons_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("📁 Add Files")
        self.add_folder_btn = QPushButton("📂 Add Folder")
        self.clear_files_btn = QPushButton("🗑️ Clear")
        
        file_buttons_layout.addWidget(self.add_files_btn)
        file_buttons_layout.addWidget(self.add_folder_btn)
        file_buttons_layout.addWidget(self.clear_files_btn)
        file_buttons_layout.addStretch()
        
        file_layout.addLayout(file_buttons_layout)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["File", "Status", "Message"])
        self.files_table.horizontalHeader().setStretchLastSection(True)
        file_layout.addWidget(self.files_table)
        
        layout.addWidget(file_group)
        
        # Operations
        ops_group = QGroupBox("Operations")
        ops_layout = QGridLayout(ops_group)
        
        self.optimize_cb = QCheckBox("Optimize Geometry")
        self.optimize_cb.setChecked(True)
        self.remove_duplicates_cb = QCheckBox("Remove Duplicate Vertices")
        self.remove_duplicates_cb.setChecked(True)
        self.convert_version_cb = QCheckBox("Convert Version")
        self.version_combo = QComboBox()
        self.version_combo.addItems(["Version 1", "Version 2", "Version 3"])
        self.version_combo.setCurrentIndex(2)  # Default to COL3
        
        self.face_groups_cb = QCheckBox("Calculate Face Groups")
        self.face_groups_cb.setChecked(True)
        self.fix_materials_cb = QCheckBox("Fix Material Assignments")
        self.fix_materials_cb.setChecked(True)
        
        ops_layout.addWidget(self.optimize_cb, 0, 0)
        ops_layout.addWidget(self.remove_duplicates_cb, 0, 1)
        ops_layout.addWidget(self.convert_version_cb, 1, 0)
        ops_layout.addWidget(self.version_combo, 1, 1)
        ops_layout.addWidget(self.face_groups_cb, 2, 0)
        ops_layout.addWidget(self.fix_materials_cb, 2, 1)
        
        layout.addWidget(ops_group)
        
        # Output options
        output_group = QGroupBox("Output Options")
        output_layout = QFormLayout(output_group)
        
        self.backup_cb = QCheckBox("Backup Original Files")
        self.backup_cb.setChecked(True)
        
        self.output_dir_cb = QCheckBox("Use Output Directory")
        self.output_dir_edit = QLineEdit()
        self.output_dir_btn = QPushButton("📁 Browse")
        
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.output_dir_btn)
        
        output_layout.addRow(self.backup_cb)
        output_layout.addRow(self.output_dir_cb)
        output_layout.addRow("Output Directory:", output_dir_layout)
        
        layout.addWidget(output_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Processing")
        self.start_btn.setProperty("action-type", "export")
        self.cancel_btn = QPushButton("⏹️ Cancel")
        self.cancel_btn.setProperty("action-type", "remove")
        self.cancel_btn.setEnabled(False)
        self.close_btn = QPushButton("❌ Close")
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
    
    def add_files(self):
        """Add COL files to the list"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select COL Files", "", "COL Files (*.col);;All Files (*)"
        )
        
        if files:
            for file_path in files:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
            
            self.update_files_table()
    
    def add_folder(self):
        """Add all COL files from a folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder:
            for file_path in Path(folder).rglob("*.col"):
                file_path_str = str(file_path)
                if file_path_str not in self.file_paths:
                    self.file_paths.append(file_path_str)
            
            self.update_files_table()
    
    def clear_files(self):
        """Clear file list"""
        self.file_paths = []
        self.update_files_table()
    
    def update_files_table(self):
        """Update the files table"""
        self.files_table.setRowCount(len(self.file_paths))
        
        for row, file_path in enumerate(self.file_paths):
            file_name = os.path.basename(file_path)
            
            name_item = QTableWidgetItem(file_name)
            name_item.setToolTip(file_path)
            status_item = QTableWidgetItem("Ready")
            message_item = QTableWidgetItem("")
            
            self.files_table.setItem(row, 0, name_item)
            self.files_table.setItem(row, 1, status_item)
            self.files_table.setItem(row, 2, message_item)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_dir_edit.setText(folder)
    
    def start_processing(self):
        """Start batch processing"""
        if not self.file_paths:
            QMessageBox.warning(self, "No Files", "Please add some COL files to process.")
            return
        
        # Prepare operations
        operations = {
            'optimize_geometry': self.optimize_cb.isChecked(),
            'remove_duplicate_vertices': self.remove_duplicates_cb.isChecked(),
            'convert_version': self.convert_version_cb.isChecked(),
            'target_version': [COLVersion.COL_1, COLVersion.COL_2, COLVersion.COL_3][self.version_combo.currentIndex()],
            'calculate_face_groups': self.face_groups_cb.isChecked(),
            'fix_materials': self.fix_materials_cb.isChecked(),
            'backup_original': self.backup_cb.isChecked(),
            'output_directory': self.output_dir_edit.text() if self.output_dir_cb.isChecked() else None
        }
        
        # Create output directory if needed
        if operations['output_directory']:
            os.makedirs(operations['output_directory'], exist_ok=True)
        
        # Start processing thread
        self.processor = COLBatchProcessor(self.file_paths, operations)
        self.processor.progress.connect(self.on_progress)
        self.processor.file_processed.connect(self.on_file_processed)
        self.processor.finished_all.connect(self.on_finished)
        
        self.processor.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")
    
    def cancel_processing(self):
        """Cancel batch processing"""
        if self.processor:
            self.processor.cancel()
            self.status_label.setText("Cancelling...")
    
    def on_progress(self, value: int, status: str):
        """Update progress"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def on_file_processed(self, file_path: str, success: bool, message: str):
        """Update file status"""
        try:
            row = self.file_paths.index(file_path)
            status = "Success" if success else "Failed"
            
            self.files_table.setItem(row, 1, QTableWidgetItem(status))
            self.files_table.setItem(row, 2, QTableWidgetItem(message))
            
            # Color code the row
            if success:
                color = Qt.GlobalColor.green
            else:
                color = Qt.GlobalColor.red
            
            for col in range(3):
                item = self.files_table.item(row, col)
                if item:
                    item.setBackground(color)
        
        except ValueError:
            pass  # File not in list
    
    def on_finished(self, total_files: int, successful_files: int):
        """Processing finished"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        
        status = f"Complete: {successful_files}/{total_files} files processed successfully"
        self.status_label.setText(status)
        
        # Show completion message
        QMessageBox.information(
            self, "Batch Processing Complete",
            f"Processing finished!\n\n"
            f"Total files: {total_files}\n"
            f"Successful: {successful_files}\n"
            f"Failed: {total_files - successful_files}"
        )

class COLAnalyzer:
    """Utility class for analyzing COL files"""
    
    @staticmethod
    def analyze_col_file(col_file: COLFile) -> Dict[str, Any]:
        """Analyze a COL file and return detailed statistics"""
        analysis = {
            'file_info': {
                'path': col_file.file_path,
                'model_count': len(col_file.models),
                'file_size': 0
            },
            'models': [],
            'totals': col_file.get_total_stats(),
            'issues': []
        }
        
        # Get file size
        if col_file.file_path and os.path.exists(col_file.file_path):
            analysis['file_info']['file_size'] = os.path.getsize(col_file.file_path)
        
        # Analyze each model
        for i, model in enumerate(col_file.models):
            model_analysis = COLAnalyzer.analyze_col_model(model, i)
            analysis['models'].append(model_analysis)
            analysis['issues'].extend(model_analysis['issues'])
        
        return analysis
    
    @staticmethod
    def analyze_col_model(model: COLModel, model_index: int) -> Dict[str, Any]:
        """Analyze a single COL model"""
        analysis = {
            'index': model_index,
            'name': model.name,
            'version': model.version,
            'stats': model.get_stats(),
            'bounding_box': None,
            'issues': [],
            'quality_score': 0
        }
        
        # Bounding box analysis
        if model.bounding_box:
            bb = model.bounding_box
            analysis['bounding_box'] = {
                'min': (bb.min.x, bb.min.y, bb.min.z),
                'max': (bb.max.x, bb.max.y, bb.max.z),
                'center': (bb.center.x, bb.center.y, bb.center.z),
                'radius': bb.radius,
                'volume': (bb.max.x - bb.min.x) * (bb.max.y - bb.min.y) * (bb.max.z - bb.min.z)
            }
        
        # Check for issues
        issues = []
        
        # Check for empty model
        if not model.spheres and not model.boxes and not model.faces:
            issues.append("Model is empty (no collision geometry)")
        
        # Check for invalid face indices
        for i, face in enumerate(model.faces):
            max_vertex = len(model.vertices) - 1
            if face.a > max_vertex or face.b > max_vertex or face.c > max_vertex:
                issues.append(f"Face {i} has invalid vertex indices")
        
        # Check for degenerate faces
        degenerate_faces = 0
        for face in model.faces:
            if face.a == face.b or face.b == face.c or face.a == face.c:
                degenerate_faces += 1
        
        if degenerate_faces > 0:
            issues.append(f"{degenerate_faces} degenerate faces found")
        
        # Check for invalid materials
        invalid_materials = 0
        for face in model.faces:
            if face.material > 17:
                invalid_materials += 1
        
        if invalid_materials > 0:
            issues.append(f"{invalid_materials} faces with invalid materials")
        
        # Check version compatibility
        if model.version == COLVersion.COL_1 and model.face_groups:
            issues.append("COL1 model has face groups (not supported)")
        
        if model.version != COLVersion.COL_3 and model.shadow_faces:
            issues.append("Non-COL3 model has shadow mesh (not supported)")
        
        # Check vertex limits for COL2/3
        if model.version in [COLVersion.COL_2, COLVersion.COL_3]:
            out_of_bounds_vertices = 0
            for vertex in model.vertices:
                if (abs(vertex.position.x) > 255.99 or 
                    abs(vertex.position.y) > 255.99 or 
                    abs(vertex.position.z) > 255.99):
                    out_of_bounds_vertices += 1
            
            if out_of_bounds_vertices > 0:
                issues.append(f"{out_of_bounds_vertices} vertices exceed COL2/3 bounds")
        
        analysis['issues'] = issues
        
        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= len(issues) * 10  # Penalty for each issue
        quality_score -= degenerate_faces * 2  # Extra penalty for degenerate faces
        quality_score = max(0, quality_score)
        
        analysis['quality_score'] = quality_score
        
        return analysis
    
    @staticmethod
    def generate_report(analysis: Dict[str, Any]) -> str:
        """Generate a text report from analysis"""
        report = []
        
        # File info
        info = analysis['file_info']
        report.append("COL FILE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"File: {os.path.basename(info['path'])}")
        report.append(f"Size: {info['file_size']} bytes")
        report.append(f"Models: {info['model_count']}")
        report.append("")
        
        # Totals
        totals = analysis['totals']
        report.append("TOTAL STATISTICS")
        report.append("-" * 20)
        for key, value in totals.items():
            if value > 0:
                report.append(f"{key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Model details
        report.append("MODEL DETAILS")
        report.append("-" * 20)
        for model_analysis in analysis['models']:
            name = model_analysis['name'] or f"Model {model_analysis['index']}"
            report.append(f"{name} (Version {model_analysis['version'].value})")
            report.append(f"  Quality Score: {model_analysis['quality_score']}/100")
            
            stats = model_analysis['stats']
            if stats['total_elements'] > 0:
                report.append(f"  Elements: {stats['spheres']} spheres, {stats['boxes']} boxes, {stats['faces']} faces")
            
            if model_analysis['issues']:
                report.append("  Issues:")
                for issue in model_analysis['issues']:
                    report.append(f"    - {issue}")
            
            report.append("")
        
        # Overall issues
        if analysis['issues']:
            report.append("ISSUES SUMMARY")
            report.append("-" * 20)
            for issue in analysis['issues']:
                report.append(f"- {issue}")
        
        return "\n".join(report)

def open_col_batch_processor(parent=None):
    """Open COL batch processor dialog"""
    dialog = COLBatchDialog(parent)
    return dialog.exec()

def analyze_col_file_dialog(parent=None):
    """Open COL file for analysis"""
    file_path, _ = QFileDialog.getOpenFileName(
        parent, "Analyze COL File", "", "COL Files (*.col);;All Files (*)"
    )
    
    if file_path:
        try:
            col_file = COLFile(file_path)
            if col_file.load():
                analysis = COLAnalyzer.analyze_col_file(col_file)
                report = COLAnalyzer.generate_report(analysis)
                
                # Show report dialog
                dialog = QDialog(parent)
                dialog.setWindowTitle(f"COL Analysis - {os.path.basename(file_path)}")
                dialog.setMinimumSize(600, 400)
                
                layout = QVBoxLayout(dialog)
                
                text_edit = QTextEdit()
                text_edit.setPlainText(report)
                text_edit.setReadOnly(True)
                text_edit.setFont(QFont("Courier", 9))
                layout.addWidget(text_edit)
                
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.close)
                layout.addWidget(close_btn)
                
                dialog.exec()
            else:
                QMessageBox.warning(parent, "Error", f"Failed to load COL file: {file_path}")
        
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error analyzing COL file: {str(e)}")

if __name__ == "__main__":
    # Test the batch processor
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    dialog = COLBatchDialog()
    dialog.show()
    
    sys.exit(app.exec()):
            pos_key = (round(vertex.position.x, 6), 
                      round(vertex.position.y, 6), 
                      round(vertex.position.z, 6))
            
            if pos_key in vertex_map:
                # Duplicate found
                index_map[i] = vertex_map[pos_key]
            else:
                # New vertex
                vertex_map[pos_key] = len(new_vertices)
                index_map[i] = len(new_vertices)
                new_vertices.append(vertex)
        
        # Update faces if vertices were removed
        if len(new_vertices) < len(model.vertices):
            for face in model.faces:
                face.a = index_map[face.a]
                face.b = index_map[face.b]
                face.c = index_map[face.c]
            
            model.vertices = new_vertices
            return True
        
        return False
    
    def remove_unused_vertices(self, model: COLModel) -> bool:
        """Remove vertices not used by any face"""
        if not model.faces:
            return False
        
        # Find used vertices
        used_vertices = set()
        for face in model.faces:
            used_vertices.add(face.a)
            used_vertices.add(face.b)
            used_vertices.add(face.c)
        
        # Create mapping from old to new indices
        old_vertices = model.vertices
        new_vertices = []
        index_map = {}
        
        for old_index in sorted(used_vertices):
            if old_index < len(old_vertices):
                index_map[old_index] = len(new_vertices)
                new_vertices.append(old_vertices[old_index])
        
        # Update faces if vertices were removed
        if len(new_vertices) < len(old_vertices):
            for face in model.faces:
                face.a = index_map.get(face.a, 0)
                face.b = index_map.get(face.b, 0)
                face.c = index_map.get(face.c, 0)
            
            model.vertices = new_vertices
            return True
        
        return False
    
    def merge_nearby_vertices(self, model: COLModel, threshold: float = 0.01) -> bool:
        """Merge vertices that are very close together"""
        if not model.vertices:
            return False
        
        # Find vertices to merge
        vertex_groups = []
        processed = set()
        
        for i, vertex in enumerate(model.vertices
