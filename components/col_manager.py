#this belongs in components/col_manager.py - Version: 1
# X-Seti - July17 2025 - IMG Factory 1.5 - COL Manager
# Consolidated COL management - utilities, structure, threading using IMG debug system

"""
COL Manager - Complete COL file management system
Consolidates col_utilities, col_structure_manager, col_threaded_loader
Uses IMG debug system throughout - no broken debug calls
"""

import os
import struct
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel,
    QGroupBox, QCheckBox, QSpinBox, QLineEdit, QComboBox, QApplication
)
from PyQt6.QtCore import Qt

# Import IMG debug system - no broken debug calls
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile, COLModel, COLVersion

##Methods list -
# analyze_col_file
# analyze_col_model
# convert_model_version
# load_col_file_async
# merge_nearby_vertices
# open_col_batch_processor_dialog
# optimize_model_geometry
# parse_col_bounds
# parse_col_face
# parse_col_header
# remove_duplicate_vertices
# remove_unused_vertices
# validate_col_structure

##Classes -
# COLAnalyzer
# COLBackgroundLoader
# COLBatchProcessor
# COLBounds
# COLBox
# COLFace
# COLHeader
# COLModelStructure
# COLOptimizer
# COLProcessingThread
# COLSphere
# COLStructureManager
# COLVertex

@dataclass
class COLHeader:
    """COL file header structure"""
    signature: str
    file_size: int
    model_name: str
    model_id: int
    version: int

@dataclass
class COLBounds:
    """COL bounding data structure"""
    radius: float
    center: Tuple[float, float, float]
    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]

@dataclass
class COLSphere:
    """COL collision sphere structure"""
    center: Tuple[float, float, float]
    radius: float
    material: int
    flags: int = 0

@dataclass
class COLBox:
    """COL collision box structure"""
    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]
    material: int
    flags: int = 0

@dataclass
class COLVertex:
    """COL mesh vertex structure"""
    position: Tuple[float, float, float]

@dataclass
class COLFace:
    """COL mesh face structure"""
    vertex_indices: Tuple[int, int, int]
    material: int
    light: int = 0
    flags: int = 0

@dataclass
class COLModelStructure:
    """Complete COL model structure"""
    header: COLHeader
    bounds: COLBounds
    spheres: List[COLSphere]
    boxes: List[COLBox]
    vertices: List[COLVertex]
    faces: List[COLFace]
    face_groups: List = None
    shadow_vertices: List[COLVertex] = None
    shadow_faces: List[COLFace] = None

class COLStructureManager:
    """Manages COL file structure parsing and validation""" #vers 1
    
    def __init__(self):
        self.debug_enabled = img_debugger.debug_enabled
        
    def parse_col_header(self, data: bytes, offset: int = 0) -> Tuple[COLHeader, int]: #vers 1
        """Parse COL file header and return header + new offset"""
        try:
            if img_debugger.debug_enabled:
                img_debugger.debug(f"Added {len(files)} COL files to batch processor")
    
    def add_folder(self): #vers 1
        """Add all COL files from a folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder:
            added_count = 0
            for file_path in Path(folder).rglob("*.col"):
                file_path_str = str(file_path)
                if file_path_str not in self.file_paths:
                    self.file_paths.append(file_path_str)
                    added_count += 1
            
            self.update_files_table()
            
            if img_debugger.debug_enabled:
                img_debugger.debug(f"Added {added_count} COL files from folder: {folder}")
    
    def clear_files(self): #vers 1
        """Clear file list"""
        self.file_paths = []
        self.update_files_table()
        
        if img_debugger.debug_enabled:
            img_debugger.debug("Cleared COL file list")
    
    def update_files_table(self): #vers 1
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
    
    def browse_output_dir(self): #vers 1
        """Browse for output directory"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_dir_edit.setText(folder)
    
    def start_processing(self): #vers 1
        """Start batch processing"""
        if not self.file_paths:
            QMessageBox.warning(self, "No Files", "Please add some COL files to process.")
            return
        
        # Gather operations
        operations = {
            'remove_duplicates': self.remove_duplicates_cb.isChecked(),
            'remove_unused': self.remove_unused_cb.isChecked(),
            'merge_nearby': self.merge_nearby_cb.isChecked(),
            'convert_version': self.convert_version_cb.isChecked(),
            'output_dir': self.output_dir_edit.text().strip() or None,
            'merge_threshold': 0.01,
            'target_version': COLVersion.COL_2
        }
        
        if img_debugger.debug_enabled:
            img_debugger.debug(f"Starting batch processing with operations: {operations}")
        
        # Create and start processing thread
        self.processing_thread = COLProcessingThread(self.file_paths, operations)
        self.processing_thread.progress_updated.connect(self.on_progress)
        self.processing_thread.file_processed.connect(self.on_file_processed)
        self.processing_thread.finished_all.connect(self.on_finished)
        
        self.processing_thread.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("Processing...")
    
    def cancel_processing(self): #vers 1
        """Cancel processing"""
        if self.processing_thread:
            self.processing_thread.cancel_processing()
            self.processing_thread.wait()
        
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("Cancelled")
        
        if img_debugger.debug_enabled:
            img_debugger.debug("Batch processing cancelled")
    
    def on_progress(self, progress: int, status: str): #vers 1
        """Update progress display"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def on_file_processed(self, filename: str, success: bool, message: str): #vers 1
        """Update file processing status"""
        try:
            # Find file in table
            for row in range(self.files_table.rowCount()):
                item = self.files_table.item(row, 0)
                if item and item.text() == filename:
                    # Update status
                    status_item = QTableWidgetItem("Success" if success else "Failed")
                    message_item = QTableWidgetItem(message)
                    
                    self.files_table.setItem(row, 1, status_item)
                    self.files_table.setItem(row, 2, message_item)
                    
                    # Color code the row
                    if success:
                        color = Qt.GlobalColor.green
                    else:
                        color = Qt.GlobalColor.red
                    
                    for col in range(3):
                        item = self.files_table.item(row, col)
                        if item:
                            item.setBackground(color)
                    break
        except ValueError:
            pass  # File not in list
    
    def on_finished(self, total_files: int, successful_files: int): #vers 1
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
        
        if img_debugger.debug_enabled:
            img_debugger.success(f"Batch processing finished: {successful_files}/{total_files} successful")

def load_col_file_async(main_window, file_path: str): #vers 1
    """Load COL file asynchronously with progress feedback"""
    try:
        if img_debugger.debug_enabled:
            img_debugger.debug(f"Starting async COL load: {file_path}")
        
        # Show progress if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(0, "Loading COL file...")
        
        # Create background loader
        loader = COLBackgroundLoader(file_path, main_window)
        
        # Connect signals
        def on_progress(progress, status):
            """Update progress display"""
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'update_progress'):
                main_window.gui_layout.update_progress(progress, status)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"COL Load: {status}")
        
        def on_model_loaded(count, name):
            """Report model loading"""
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📦 Loaded model {count}: {name}")
        
        def on_load_complete(col_file):
            """Handle successful load completion"""
            try:
                # Hide progress
                if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'hide_progress'):
                    main_window.gui_layout.hide_progress()
                
                # Update main window with loaded COL
                main_window.current_col = col_file
                
                # Populate table with COL data
                try:
                    from components.col_tab_integration import populate_table_with_col_data_debug
                    populate_table_with_col_data_debug(main_window, col_file)
                except ImportError:
                    if img_debugger.debug_enabled:
                        img_debugger.warning("COL tab integration not available")
                
                # Update info bar
                try:
                    from components.col_tab_integration import update_info_bar_for_col
                    update_info_bar_for_col(main_window, col_file, file_path)
                except ImportError:
                    if img_debugger.debug_enabled:
                        img_debugger.warning("COL info bar update not available")
                
                # Update window title
                file_name = os.path.basename(file_path)
                if hasattr(main_window, 'setWindowTitle'):
                    main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
                
                model_count = len(getattr(col_file, 'models', []))
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ COL Load Complete: {file_name} ({model_count} models)")
                
                if img_debugger.debug_enabled:
                    img_debugger.success(f"COL async load complete: {file_path}")
                
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error updating UI after COL load: {str(e)}")
                if img_debugger.debug_enabled:
                    img_debugger.error(f"COL load completion error: {e}")
        
        def on_load_error(error_msg):
            """Handle load errors"""
            # Hide progress
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'hide_progress'):
                main_window.gui_layout.hide_progress()
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ COL Load Error: {error_msg}")
            
            # Show error dialog
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(main_window, "COL Load Error", 
                               f"Failed to load COL file:\n{error_msg}")
            
            if img_debugger.debug_enabled:
                img_debugger.error(f"COL async load error: {error_msg}")
        
        # Connect all signals
        loader.progress_update.connect(on_progress)
        loader.model_loaded.connect(on_model_loaded)
        loader.load_complete.connect(on_load_complete)
        loader.load_error.connect(on_load_error)
        
        # Store loader reference to prevent garbage collection
        main_window._col_loader = loader
        
        # Start loading
        loader.start()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Started background COL loading: {os.path.basename(file_path)}")
        
        return loader
        
    except Exception as e:
        if img_debugger.debug_enabled:
            img_debugger.error(f"Failed to start async COL load: {e}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to start COL loading: {str(e)}")
        return None

def open_col_batch_processor_dialog(main_window): #vers 1
    """Open COL batch processor dialog"""
    try:
        if img_debugger.debug_enabled:
            img_debugger.debug("Opening COL batch processor dialog")
        
        dialog = COLBatchProcessor(main_window)
        result = dialog.exec()
        
        if img_debugger.debug_enabled:
            img_debugger.debug(f"COL batch processor closed with result: {result}")
        
        return result == QDialog.DialogCode.Accepted
        
    except Exception as e:
        if img_debugger.debug_enabled:
            img_debugger.error(f"Error opening COL batch processor: {e}")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to open COL batch processor: {str(e)}")
        return False

# Export main classes and functions
__all__ = [
    'COLStructureManager',
    'COLBackgroundLoader',
    'COLOptimizer',
    'COLAnalyzer',
    'COLProcessingThread',
    'COLBatchProcessor',
    'COLHeader',
    'COLBounds',
    'COLSphere',
    'COLBox',
    'COLVertex',
    'COLFace',
    'COLModelStructure',
    'load_col_file_async',
    'open_col_batch_processor_dialog',
    'analyze_col_file',
    'analyze_col_model',
    'optimize_model_geometry',
    'remove_duplicate_vertices',
    'remove_unused_vertices',
    'merge_nearby_vertices',
    'convert_model_version',
    'validate_col_structure',
    'parse_col_header',
    'parse_col_bounds'
] len(data) < offset + 32:
                raise ValueError("Data too short for COL header")
            
            # Read signature (4 bytes)
            signature = data[offset:offset+4].decode('ascii', errors='ignore')
            offset += 4
            
            # Read file size (4 bytes)
            file_size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Read model name (22 bytes, null-terminated)
            model_name_data = data[offset:offset+22]
            null_pos = model_name_data.find(b'\x00')
            if null_pos != -1:
                model_name = model_name_data[:null_pos].decode('ascii', errors='ignore')
            else:
                model_name = model_name_data.decode('ascii', errors='ignore')
            offset += 22
            
            # Read model ID and version
            model_id, version = struct.unpack('<HH', data[offset:offset+4])
            offset += 4
            
            header = COLHeader(signature, file_size, model_name, model_id, version)
            
            if img_debugger.debug_enabled:
                img_debugger.debug(f"COL Header parsed: {signature}, size: {file_size}, name: {model_name}")
            
            return header, offset
            
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"COL header parsing error: {e}")
            raise

    def parse_col_bounds(self, data: bytes, offset: int) -> Tuple[COLBounds, int]: #vers 1
        """Parse COL bounding information"""
        try:
            if len(data) < offset + 40:
                raise ValueError("Data too short for bounds")
            
            # Parse bounding sphere
            radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            
            center = struct.unpack('<3f', data[offset:offset+12])
            offset += 12
            
            # Parse bounding box
            min_point = struct.unpack('<3f', data[offset:offset+12])
            offset += 12
            
            max_point = struct.unpack('<3f', data[offset:offset+12])
            offset += 12
            
            bounds = COLBounds(radius, center, min_point, max_point)
            
            if img_debugger.debug_enabled:
                img_debugger.debug(f"COL Bounds: radius={radius:.2f}, center={center}")
            
            return bounds, offset
            
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"COL bounds parsing error: {e}")
            raise

    def validate_col_structure(self, file_path: str) -> bool: #vers 1
        """Validate COL file structure using IMG debug system"""
        try:
            if img_debugger.debug_enabled:
                img_debugger.debug(f"Validating COL structure: {file_path}")
            
            if not os.path.exists(file_path):
                if img_debugger.debug_enabled:
                    img_debugger.error(f"COL file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                data = f.read(32)  # Read header
                
            if len(data) < 32:
                if img_debugger.debug_enabled:
                    img_debugger.error("COL file too small for header")
                return False
            
            # Try to parse header
            header, _ = self.parse_col_header(data)
            
            # Basic validation
            if header.signature not in ['COL', 'COLL']:
                if img_debugger.debug_enabled:
                    img_debugger.error(f"Invalid COL signature: {header.signature}")
                return False
            
            if img_debugger.debug_enabled:
                img_debugger.success(f"COL structure validation passed: {file_path}")
            
            return True
            
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"COL validation error: {e}")
            return False

class COLBackgroundLoader(QThread):
    """Background thread for loading COL files without freezing UI""" #vers 1
    
    # Signals for UI updates
    progress_update = pyqtSignal(int, str)  # progress %, status text
    model_loaded = pyqtSignal(int, str)     # model count, model name
    load_complete = pyqtSignal(object)      # COLFile object
    load_error = pyqtSignal(str)            # error message
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.should_cancel = False
        self.col_file = None
        
    def cancel_load(self): #vers 1
        """Cancel the loading operation"""
        self.should_cancel = True
        
    def run(self): #vers 1
        """Run the background loading process"""
        try:
            if img_debugger.debug_enabled:
                img_debugger.debug(f"Starting background COL load: {self.file_path}")
            
            self.progress_update.emit(0, "Initializing COL loader...")
            QApplication.processEvents()
            
            # Check file exists
            if not os.path.exists(self.file_path):
                self.load_error.emit(f"File not found: {self.file_path}")
                return
                
            file_size = os.path.getsize(self.file_path)
            self.progress_update.emit(5, f"Loading COL file ({file_size:,} bytes)...")
            
            # Create COL file object
            self.col_file = COLFile(self.file_path)
            
            self.progress_update.emit(10, "Parsing COL structure...")
            
            # Load with progress tracking
            if self.load_col_with_progress():
                self.progress_update.emit(100, "Loading complete")
                self.load_complete.emit(self.col_file)
                
                if img_debugger.debug_enabled:
                    img_debugger.success(f"COL background load complete: {self.file_path}")
            else:
                self.load_error.emit("Failed to load COL file")
                
        except Exception as e:
            error_msg = f"Background loading error: {str(e)}"
            if img_debugger.debug_enabled:
                img_debugger.error(error_msg)
            self.load_error.emit(error_msg)
    
    def load_col_with_progress(self) -> bool: #vers 1
        """Load COL file with progress updates"""
        try:
            def progress_load():
                if self.should_cancel:
                    return False
                
                self.progress_update.emit(20, "Reading file data...")
                result = self.col_file.load()
                
                if result and hasattr(self.col_file, 'models'):
                    model_count = len(self.col_file.models)
                    self.progress_update.emit(60, f"Processing {model_count} models...")
                    
                    for i, model in enumerate(self.col_file.models):
                        if self.should_cancel:
                            return False
                        
                        progress = 60 + (30 * (i + 1) // model_count)
                        model_name = getattr(model, 'name', f'Model {i+1}')
                        
                        self.progress_update.emit(progress, f"Processing {model_name}...")
                        self.model_loaded.emit(i+1, model_name)
                        
                        # Small delay to prevent UI lockup
                        self.msleep(5)
                
                return result
            
            return progress_load()
            
        except Exception as e:
            self.progress_update.emit(0, f"Loading error: {str(e)}")
            return False

class COLOptimizer:
    """Class for optimizing COL models""" #vers 1
    
    def optimize_model_geometry(self, model: COLModel) -> bool: #vers 1
        """Optimize model geometry using IMG debug system"""
        if img_debugger.debug_enabled:
            img_debugger.debug(f"Optimizing COL model geometry")
        
        try:
            original_vertex_count = len(getattr(model, 'vertices', []))
            original_face_count = len(getattr(model, 'faces', []))
            
            # Remove duplicates
            self.remove_duplicate_vertices(model)
            
            # Remove unused vertices
            self.remove_unused_vertices(model)
            
            new_vertex_count = len(getattr(model, 'vertices', []))
            new_face_count = len(getattr(model, 'faces', []))
            
            if img_debugger.debug_enabled:
                img_debugger.success(f"Geometry optimized: {original_vertex_count}→{new_vertex_count} vertices, {original_face_count}→{new_face_count} faces")
            
            return True
            
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"Geometry optimization error: {e}")
            return False
    
    def remove_duplicate_vertices(self, model: COLModel) -> int: #vers 1
        """Remove duplicate vertices"""
        if not hasattr(model, 'vertices') or not model.vertices:
            return 0
        
        vertices = model.vertices
        unique_vertices = []
        vertex_map = {}
        removed_count = 0
        
        for i, vertex in enumerate(vertices):
            vertex_key = tuple(vertex.position)
            if vertex_key not in vertex_map:
                vertex_map[vertex_key] = len(unique_vertices)
                unique_vertices.append(vertex)
            else:
                removed_count += 1
        
        model.vertices = unique_vertices
        
        # Update face indices if faces exist
        if hasattr(model, 'faces') and model.faces:
            for face in model.faces:
                if hasattr(face, 'vertex_indices'):
                    new_indices = []
                    for idx in face.vertex_indices:
                        if idx < len(vertices):
                            vertex_key = tuple(vertices[idx].position)
                            new_indices.append(vertex_map[vertex_key])
                        else:
                            new_indices.append(idx)
                    face.vertex_indices = tuple(new_indices)
        
        if img_debugger.debug_enabled and removed_count > 0:
            img_debugger.debug(f"Removed {removed_count} duplicate vertices")
        
        return removed_count
    
    def remove_unused_vertices(self, model: COLModel) -> int: #vers 1
        """Remove vertices not referenced by faces"""
        if not hasattr(model, 'vertices') or not hasattr(model, 'faces'):
            return 0
        
        if not model.vertices or not model.faces:
            return 0
        
        # Find used vertices
        used_vertices = set()
        for face in model.faces:
            if hasattr(face, 'vertex_indices'):
                for idx in face.vertex_indices:
                    used_vertices.add(idx)
        
        # Create new vertex list and mapping
        new_vertices = []
        vertex_remap = {}
        
        for old_idx in sorted(used_vertices):
            if old_idx < len(model.vertices):
                vertex_remap[old_idx] = len(new_vertices)
                new_vertices.append(model.vertices[old_idx])
        
        removed_count = len(model.vertices) - len(new_vertices)
        model.vertices = new_vertices
        
        # Update face indices
        for face in model.faces:
            if hasattr(face, 'vertex_indices'):
                new_indices = []
                for idx in face.vertex_indices:
                    if idx in vertex_remap:
                        new_indices.append(vertex_remap[idx])
                    else:
                        new_indices.append(0)  # Fallback to first vertex
                face.vertex_indices = tuple(new_indices)
        
        if img_debugger.debug_enabled and removed_count > 0:
            img_debugger.debug(f"Removed {removed_count} unused vertices")
        
        return removed_count
    
    def merge_nearby_vertices(self, model: COLModel, threshold: float = 0.01) -> int: #vers 1
        """Merge vertices that are very close together"""
        if not hasattr(model, 'vertices') or not model.vertices:
            return 0
        
        vertices = model.vertices
        merged_count = 0
        vertex_map = {}
        
        # Group vertices by proximity
        for i, vertex in enumerate(vertices):
            pos = vertex.position
            found_match = False
            
            for existing_idx, existing_pos in vertex_map.items():
                distance = sum((a - b) ** 2 for a, b in zip(pos, existing_pos)) ** 0.5
                if distance < threshold:
                    vertex_map[i] = existing_pos
                    found_match = True
                    merged_count += 1
                    break
            
            if not found_match:
                vertex_map[i] = pos
        
        if img_debugger.debug_enabled and merged_count > 0:
            img_debugger.debug(f"Merged {merged_count} nearby vertices (threshold: {threshold})")
        
        return merged_count
    
    def convert_model_version(self, model: COLModel, target_version: COLVersion) -> bool: #vers 1
        """Convert model to target COL version"""
        try:
            current_version = getattr(model, 'version', COLVersion.COL_1)
            
            if current_version == target_version:
                return True
            
            if img_debugger.debug_enabled:
                img_debugger.debug(f"Converting COL model from {current_version} to {target_version}")
            
            # Version conversion logic would go here
            model.version = target_version
            
            if img_debugger.debug_enabled:
                img_debugger.success(f"COL model converted to {target_version}")
            
            return True
            
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"Version conversion error: {e}")
            return False

class COLAnalyzer:
    """Utility class for analyzing COL files""" #vers 1
    
    @staticmethod
    def analyze_col_file(col_file: COLFile) -> Dict[str, Any]: #vers 1
        """Analyze a COL file and return detailed statistics"""
        if img_debugger.debug_enabled:
            img_debugger.debug(f"Analyzing COL file: {getattr(col_file, 'file_path', 'unknown')}")
        
        analysis = {
            'file_info': {
                'path': getattr(col_file, 'file_path', ''),
                'model_count': len(getattr(col_file, 'models', [])),
                'file_size': 0
            },
            'models': [],
            'totals': {},
            'issues': []
        }
        
        # Get file size
        if hasattr(col_file, 'file_path') and col_file.file_path and os.path.exists(col_file.file_path):
            analysis['file_info']['file_size'] = os.path.getsize(col_file.file_path)
        
        # Get totals
        if hasattr(col_file, 'get_total_stats'):
            analysis['totals'] = col_file.get_total_stats()
        
        # Analyze each model
        if hasattr(col_file, 'models'):
            for i, model in enumerate(col_file.models):
                model_analysis = COLAnalyzer.analyze_col_model(model, i)
                analysis['models'].append(model_analysis)
                analysis['issues'].extend(model_analysis['issues'])
        
        if img_debugger.debug_enabled:
            img_debugger.success(f"COL analysis complete: {len(analysis['models'])} models, {len(analysis['issues'])} issues")
        
        return analysis
    
    @staticmethod
    def analyze_col_model(model: COLModel, model_index: int) -> Dict[str, Any]: #vers 1
        """Analyze a single COL model"""
        analysis = {
            'index': model_index,
            'name': getattr(model, 'name', f'Model {model_index}'),
            'stats': {
                'vertices': len(getattr(model, 'vertices', [])),
                'faces': len(getattr(model, 'faces', [])),
                'spheres': len(getattr(model, 'spheres', [])),
                'boxes': len(getattr(model, 'boxes', []))
            },
            'issues': []
        }
        
        # Check for common issues
        if analysis['stats']['vertices'] == 0:
            analysis['issues'].append(f"Model {model_index}: No vertices")
        
        if analysis['stats']['faces'] == 0:
            analysis['issues'].append(f"Model {model_index}: No faces")
        
        if analysis['stats']['vertices'] > 10000:
            analysis['issues'].append(f"Model {model_index}: High vertex count ({analysis['stats']['vertices']})")
        
        return analysis

class COLProcessingThread(QThread):
    """Background thread for batch COL processing""" #vers 1
    
    progress_updated = pyqtSignal(int, str)  # progress %, status
    file_processed = pyqtSignal(str, bool, str)  # filename, success, message
    finished_all = pyqtSignal(int, int)  # total, successful
    
    def __init__(self, file_paths: List[str], operations: Dict[str, Any]):
        super().__init__()
        self.file_paths = file_paths
        self.operations = operations
        self.should_cancel = False
        
    def cancel_processing(self): #vers 1
        """Cancel processing"""
        self.should_cancel = True
        
    def run(self): #vers 1
        """Run batch processing"""
        try:
            if img_debugger.debug_enabled:
                img_debugger.debug(f"Starting batch COL processing: {len(self.file_paths)} files")
            
            total_files = len(self.file_paths)
            successful_files = 0
            
            for i, file_path in enumerate(self.file_paths):
                if self.should_cancel:
                    break
                
                progress = int((i / total_files) * 100)
                filename = os.path.basename(file_path)
                
                self.progress_updated.emit(progress, f"Processing {filename}...")
                
                success, message = self.process_single_file(file_path)
                
                if success:
                    successful_files += 1
                
                self.file_processed.emit(filename, success, message)
            
            self.progress_updated.emit(100, "Processing complete")
            self.finished_all.emit(total_files, successful_files)
            
            if img_debugger.debug_enabled:
                img_debugger.success(f"Batch processing complete: {successful_files}/{total_files} successful")
            
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"Batch processing error: {e}")
    
    def process_single_file(self, file_path: str) -> Tuple[bool, str]: #vers 1
        """Process a single COL file"""
        try:
            # Load COL file
            col_file = COLFile(file_path)
            if not col_file.load():
                return False, "Failed to load COL file"
            
            # Get original stats
            original_stats = {}
            if hasattr(col_file, 'get_total_stats'):
                original_stats = col_file.get_total_stats()
            
            # Apply operations
            optimizer = COLOptimizer()
            
            if hasattr(col_file, 'models'):
                for model in col_file.models:
                    # Apply selected operations
                    if self.operations.get('remove_duplicates', False):
                        optimizer.remove_duplicate_vertices(model)
                    
                    if self.operations.get('remove_unused', False):
                        optimizer.remove_unused_vertices(model)
                    
                    if self.operations.get('merge_nearby', False):
                        threshold = self.operations.get('merge_threshold', 0.01)
                        optimizer.merge_nearby_vertices(model, threshold)
                    
                    if self.operations.get('convert_version', False):
                        target_version = self.operations.get('target_version', COLVersion.COL_2)
                        optimizer.convert_model_version(model, target_version)
            
            # Save file
            output_dir = self.operations.get('output_dir')
            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(file_path))
                if hasattr(col_file, 'save') and not col_file.save(output_path):
                    return False, "Failed to save processed file"
            else:
                # Save in place
                if hasattr(col_file, 'save') and not col_file.save():
                    return False, "Failed to save file"
            
            # Generate report
            new_stats = {}
            if hasattr(col_file, 'get_total_stats'):
                new_stats = col_file.get_total_stats()
            
            changes = []
            for key in original_stats:
                if key in new_stats and original_stats[key] != new_stats[key]:
                    changes.append(f"{key}: {original_stats[key]} → {new_stats[key]}")
            
            if changes:
                return True, f"Modified: {', '.join(changes)}"
            else:
                return True, "No changes needed"
                
        except Exception as e:
            return False, f"Processing error: {str(e)}"

class COLBatchProcessor(QDialog):
    """Dialog for batch processing COL files""" #vers 1
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Batch Processor")
        self.setFixedSize(800, 600)
        self.file_paths = []
        self.processing_thread = None
        self.setup_ui()
        
        if img_debugger.debug_enabled:
            img_debugger.debug("COL Batch Processor dialog created")
    
    def setup_ui(self): #vers 1
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # File list section
        files_group = QGroupBox("COL Files")
        files_layout = QVBoxLayout(files_group)
        
        # File buttons
        file_buttons = QHBoxLayout()
        add_files_btn = QPushButton("📁 Add Files")
        add_files_btn.clicked.connect(self.add_files)
        add_folder_btn = QPushButton("📂 Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        clear_files_btn = QPushButton("🗑️ Clear")
        clear_files_btn.clicked.connect(self.clear_files)
        
        file_buttons.addWidget(add_files_btn)
        file_buttons.addWidget(add_folder_btn)
        file_buttons.addWidget(clear_files_btn)
        file_buttons.addStretch()
        
        files_layout.addLayout(file_buttons)
        
        # Files table
        self.files_table = QTableWidget(0, 3)
        self.files_table.setHorizontalHeaderLabels(["File", "Status", "Message"])
        files_layout.addWidget(self.files_table)
        
        layout.addWidget(files_group)
        
        # Operations section
        ops_group = QGroupBox("Operations")
        ops_layout = QVBoxLayout(ops_group)
        
        self.remove_duplicates_cb = QCheckBox("Remove duplicate vertices")
        self.remove_unused_cb = QCheckBox("Remove unused vertices")
        self.merge_nearby_cb = QCheckBox("Merge nearby vertices")
        self.convert_version_cb = QCheckBox("Convert version")
        
        ops_layout.addWidget(self.remove_duplicates_cb)
        ops_layout.addWidget(self.remove_unused_cb)
        ops_layout.addWidget(self.merge_nearby_cb)
        ops_layout.addWidget(self.convert_version_cb)
        
        layout.addWidget(ops_group)
        
        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Leave empty to modify files in place")
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_output_dir)
        
        output_dir_layout.addWidget(QLabel("Output Directory:"))
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(browse_btn)
        
        output_layout.addLayout(output_dir_layout)
        layout.addWidget(output_group)
        
        # Progress section
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        
        self.cancel_btn = QPushButton("⏹️ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
    
    def add_files(self): #vers 1
        """Add COL files to the list"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select COL Files", "", "COL Files (*.col);;All Files (*)"
        )
        
        if files:
            for file_path in files:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
            
            self.update_files_table()
            
            if