#!/usr/bin/env python3
"""
#this belongs in components/col_editor.py - version 5
X-Seti - June27 2025 - COL Editor for Img Factory 1.5
Complete COL editing functionality based on Steve's COL Editor II
"""

import sys
import os
import math
from typing import List, Optional, Tuple, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QTextEdit, QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QGroupBox, QTabWidget, QStatusBar, QMenuBar, QMenu,
    QHeaderView, QAbstractItemView, QMessageBox, QFileDialog, QProgressBar,
    QSlider, QFrame, QListWidget, QListWidgetItem, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QFont, QPainter, QPen, QBrush, QColor

try:
    from PyQt6.QtOpenGL import QOpenGLWidget
except ImportError:
    # OpenGL not available - use regular widget as fallback
    from PyQt6.QtWidgets import QWidget as QOpenGLWidget
    print("Warning: PyQt6 OpenGL not available - COL 3D features disabled")

from col_core_classes import (
    COLFile, COLModel, COLSphere, COLBox, COLVertex, COLFace, COLFaceGroup,
    COLVersion, COLMaterial, Vector3, BoundingBox
)

class COLModelTreeWidget(QTreeWidget):
    """Tree widget for displaying COL models and their elements"""
    
    model_selected = pyqtSignal(COLModel)
    element_selected = pyqtSignal(str, int)  # element_type, index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Name", "Type", "Count", "Version"])
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self._on_item_clicked)
        
        self.col_file: Optional[COLFile] = None
        self.current_model: Optional[COLModel] = None
    
    def load_col_file(self, col_file: COLFile):
        """Load COL file into tree view"""
        self.col_file = col_file
        self.clear()
        
        if not col_file or not col_file.models:
            return
        
        for i, model in enumerate(col_file.models):
            self._add_model_item(model, i)
        
        self.expandAll()
    
    def _add_model_item(self, model: COLModel, model_index: int):
        """Add a COL model to the tree"""
        # Main model item
        model_item = QTreeWidgetItem(self)
        model_item.setText(0, model.name or f"Model_{model_index}")
        model_item.setText(1, "COL Model")
        model_item.setText(2, str(model.get_stats()["total_elements"]))
        model_item.setText(3, f"Version {model.version.value}")
        model_item.setData(0, Qt.ItemDataRole.UserRole, ("model", model_index))
        
        # Add collision elements as children
        if model.spheres:
            spheres_item = QTreeWidgetItem(model_item)
            spheres_item.setText(0, "Spheres")
            spheres_item.setText(1, "Collision Spheres")
            spheres_item.setText(2, str(len(model.spheres)))
            spheres_item.setData(0, Qt.ItemDataRole.UserRole, ("spheres", model_index))
            
            for i, sphere in enumerate(model.spheres):
                sphere_item = QTreeWidgetItem(spheres_item)
                sphere_item.setText(0, f"Sphere {i}")
                sphere_item.setText(1, f"R={sphere.radius:.2f}")
                sphere_item.setText(2, f"Mat={sphere.surface.material}")
                sphere_item.setData(0, Qt.ItemDataRole.UserRole, ("sphere", model_index, i))
        
        if model.boxes:
            boxes_item = QTreeWidgetItem(model_item)
            boxes_item.setText(0, "Boxes")
            boxes_item.setText(1, "Collision Boxes")
            boxes_item.setText(2, str(len(model.boxes)))
            boxes_item.setData(0, Qt.ItemDataRole.UserRole, ("boxes", model_index))
            
            for i, box in enumerate(model.boxes):
                box_item = QTreeWidgetItem(boxes_item)
                box_item.setText(0, f"Box {i}")
                size = box.max - box.min
                box_item.setText(1, f"{size.x:.1f}x{size.y:.1f}x{size.z:.1f}")
                box_item.setText(2, f"Mat={box.surface.material}")
                box_item.setData(0, Qt.ItemDataRole.UserRole, ("box", model_index, i))
        
        if model.faces:
            mesh_item = QTreeWidgetItem(model_item)
            mesh_item.setText(0, "Mesh")
            mesh_item.setText(1, "Collision Mesh")
            mesh_item.setText(2, f"{len(model.faces)} faces")
            mesh_item.setData(0, Qt.ItemDataRole.UserRole, ("mesh", model_index))
            
            # Vertices
            vertices_item = QTreeWidgetItem(mesh_item)
            vertices_item.setText(0, "Vertices")
            vertices_item.setText(1, "Mesh Vertices")
            vertices_item.setText(2, str(len(model.vertices)))
            vertices_item.setData(0, Qt.ItemDataRole.UserRole, ("vertices", model_index))
            
            # Faces
            faces_item = QTreeWidgetItem(mesh_item)
            faces_item.setText(0, "Faces")
            faces_item.setText(1, "Mesh Faces")
            faces_item.setText(2, str(len(model.faces)))
            faces_item.setData(0, Qt.ItemDataRole.UserRole, ("faces", model_index))
        
        if model.face_groups:
            groups_item = QTreeWidgetItem(model_item)
            groups_item.setText(0, "Face Groups")
            groups_item.setText(1, "Optimization Groups")
            groups_item.setText(2, str(len(model.face_groups)))
            groups_item.setData(0, Qt.ItemDataRole.UserRole, ("face_groups", model_index))
        
        if model.shadow_faces:
            shadow_item = QTreeWidgetItem(model_item)
            shadow_item.setText(0, "Shadow Mesh")
            shadow_item.setText(1, "Shadow Casting")
            shadow_item.setText(2, f"{len(model.shadow_faces)} faces")
            shadow_item.setData(0, Qt.ItemDataRole.UserRole, ("shadow", model_index))
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item selection"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data[0] == "model":
            model_index = data[1]
            if self.col_file and 0 <= model_index < len(self.col_file.models):
                self.current_model = self.col_file.models[model_index]
                self.model_selected.emit(self.current_model)
        else:
            # Element selected
            element_type = data[0]
            model_index = data[1]
            element_index = data[2] if len(data) > 2 else -1
            self.element_selected.emit(element_type, element_index)

class COLPropertiesWidget(QWidget):
    """Properties panel for editing COL elements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_model: Optional[COLModel] = None
        self.current_element_type: str = ""
        self.current_element_index: int = -1
    
    def setup_ui(self):
        """Setup the properties UI"""
        layout = QVBoxLayout(self)
        
        # Model properties group
        self.model_group = QGroupBox("Model Properties")
        model_layout = QFormLayout(self.model_group)
        
        self.name_edit = QLineEdit()
        self.model_id_spin = QSpinBox()
        self.model_id_spin.setRange(0, 65535)
        self.version_combo = QComboBox()
        self.version_combo.addItems(["Version 1", "Version 2", "Version 3"])
        
        model_layout.addRow("Name:", self.name_edit)
        model_layout.addRow("Model ID:", self.model_id_spin)
        model_layout.addRow("Version:", self.version_combo)
        
        layout.addWidget(self.model_group)
        
        # Element properties group
        self.element_group = QGroupBox("Element Properties")
        self.element_layout = QFormLayout(self.element_group)
        layout.addWidget(self.element_group)
        
        # Statistics group
        self.stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(self.stats_group)
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        layout.addWidget(self.stats_group)
        
        layout.addStretch()
    
    def set_model(self, model: COLModel):
        """Set current model to edit"""
        self.current_model = model
        if not model:
            return
        
        # Update model properties
        self.name_edit.setText(model.name)
        self.model_id_spin.setValue(model.model_id)
        self.version_combo.setCurrentIndex(model.version.value - 1)
        
        # Update statistics
        stats = model.get_stats()
        stats_text = []
        for key, value in stats.items():
            stats_text.append(f"{key.replace('_', ' ').title()}: {value}")
        self.stats_text.setText("\n".join(stats_text))
    
    def set_element(self, element_type: str, element_index: int):
        """Set current element to edit"""
        self.current_element_type = element_type
        self.current_element_index = element_index
        
        # Clear previous element properties
        for i in reversed(range(self.element_layout.count())):
            child = self.element_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        if not self.current_model:
            return
        
        # Add element-specific properties
        if element_type == "sphere" and element_index >= 0:
            self._setup_sphere_properties(element_index)
        elif element_type == "box" and element_index >= 0:
            self._setup_box_properties(element_index)
        elif element_type == "face" and element_index >= 0:
            self._setup_face_properties(element_index)
    
    def _setup_sphere_properties(self, index: int):
        """Setup properties for sphere editing"""
        if index >= len(self.current_model.spheres):
            return
        
        sphere = self.current_model.spheres[index]
        
        # Center position
        self.sphere_x_spin = QDoubleSpinBox()
        self.sphere_x_spin.setRange(-1000, 1000)
        self.sphere_x_spin.setValue(sphere.center.x)
        self.sphere_x_spin.setDecimals(3)
        
        self.sphere_y_spin = QDoubleSpinBox()
        self.sphere_y_spin.setRange(-1000, 1000)
        self.sphere_y_spin.setValue(sphere.center.y)
        self.sphere_y_spin.setDecimals(3)
        
        self.sphere_z_spin = QDoubleSpinBox()
        self.sphere_z_spin.setRange(-1000, 1000)
        self.sphere_z_spin.setValue(sphere.center.z)
        self.sphere_z_spin.setDecimals(3)
        
        # Radius
        self.sphere_radius_spin = QDoubleSpinBox()
        self.sphere_radius_spin.setRange(0.1, 1000)
        self.sphere_radius_spin.setValue(sphere.radius)
        self.sphere_radius_spin.setDecimals(3)
        
        # Material
        self.sphere_material_combo = QComboBox()
        self.sphere_material_combo.addItems([f"{mat.name} ({mat.value})" for mat in COLMaterial])
        self.sphere_material_combo.setCurrentIndex(sphere.surface.material)
        
        # Add to layout
        self.element_layout.addRow("Center X:", self.sphere_x_spin)
        self.element_layout.addRow("Center Y:", self.sphere_y_spin)
        self.element_layout.addRow("Center Z:", self.sphere_z_spin)
        self.element_layout.addRow("Radius:", self.sphere_radius_spin)
        self.element_layout.addRow("Material:", self.sphere_material_combo)
    
    def _setup_box_properties(self, index: int):
        """Setup properties for box editing"""
        if index >= len(self.current_model.boxes):
            return
        
        box = self.current_model.boxes[index]
        
        # Min coordinates
        self.box_min_x_spin = QDoubleSpinBox()
        self.box_min_x_spin.setRange(-1000, 1000)
        self.box_min_x_spin.setValue(box.min.x)
        self.box_min_x_spin.setDecimals(3)
        
        self.box_min_y_spin = QDoubleSpinBox()
        self.box_min_y_spin.setRange(-1000, 1000)
        self.box_min_y_spin.setValue(box.min.y)
        self.box_min_y_spin.setDecimals(3)
        
        self.box_min_z_spin = QDoubleSpinBox()
        self.box_min_z_spin.setRange(-1000, 1000)
        self.box_min_z_spin.setValue(box.min.z)
        self.box_min_z_spin.setDecimals(3)
        
        # Max coordinates
        self.box_max_x_spin = QDoubleSpinBox()
        self.box_max_x_spin.setRange(-1000, 1000)
        self.box_max_x_spin.setValue(box.max.x)
        self.box_max_x_spin.setDecimals(3)
        
        self.box_max_y_spin = QDoubleSpinBox()
        self.box_max_y_spin.setRange(-1000, 1000)
        self.box_max_y_spin.setValue(box.max.y)
        self.box_max_y_spin.setDecimals(3)
        
        self.box_max_z_spin = QDoubleSpinBox()
        self.box_max_z_spin.setRange(-1000, 1000)
        self.box_max_z_spin.setValue(box.max.z)
        self.box_max_z_spin.setDecimals(3)
        
        # Material
        self.box_material_combo = QComboBox()
        self.box_material_combo.addItems([f"{mat.name} ({mat.value})" for mat in COLMaterial])
        self.box_material_combo.setCurrentIndex(box.surface.material)
        
        # Add to layout
        self.element_layout.addRow("Min X:", self.box_min_x_spin)
        self.element_layout.addRow("Min Y:", self.box_min_y_spin)
        self.element_layout.addRow("Min Z:", self.box_min_z_spin)
        self.element_layout.addRow("Max X:", self.box_max_x_spin)
        self.element_layout.addRow("Max Y:", self.box_max_y_spin)
        self.element_layout.addRow("Max Z:", self.box_max_z_spin)
        self.element_layout.addRow("Material:", self.box_material_combo)
    
    def _setup_face_properties(self, index: int):
        """Setup properties for face editing"""
        if index >= len(self.current_model.faces):
            return
        
        face = self.current_model.faces[index]
        
        # Vertex indices
        self.face_a_spin = QSpinBox()
        self.face_a_spin.setRange(0, len(self.current_model.vertices) - 1)
        self.face_a_spin.setValue(face.a)
        
        self.face_b_spin = QSpinBox()
        self.face_b_spin.setRange(0, len(self.current_model.vertices) - 1)
        self.face_b_spin.setValue(face.b)
        
        self.face_c_spin = QSpinBox()
        self.face_c_spin.setRange(0, len(self.current_model.vertices) - 1)
        self.face_c_spin.setValue(face.c)
        
        # Material
        self.face_material_combo = QComboBox()
        self.face_material_combo.addItems([f"{mat.name} ({mat.value})" for mat in COLMaterial])
        self.face_material_combo.setCurrentIndex(face.material)
        
        # Light value
        self.face_light_spin = QSpinBox()
        self.face_light_spin.setRange(0, 255)
        self.face_light_spin.setValue(face.light)
        
        # Add to layout
        self.element_layout.addRow("Vertex A:", self.face_a_spin)
        self.element_layout.addRow("Vertex B:", self.face_b_spin)
        self.element_layout.addRow("Vertex C:", self.face_c_spin)
        self.element_layout.addRow("Material:", self.face_material_combo)
        self.element_layout.addRow("Light:", self.face_light_spin)

class COLViewer3D(QOpenGLWidget):
    """3D viewer for COL files - simplified version"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.col_file: Optional[COLFile] = None
        self.current_model: Optional[COLModel] = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = 1.0
        self.show_spheres = True
        self.show_boxes = True
        self.show_mesh = True
        self.show_wireframe = False
        
        # Mouse handling
        self.last_mouse_pos = None
        self.mouse_buttons = Qt.MouseButton.NoButton
    
    def set_col_file(self, col_file: COLFile):
        """Set COL file to display"""
        self.col_file = col_file
        self.update()
    
    def set_current_model(self, model: COLModel):
        """Set current model to display"""
        self.current_model = model
        self.update()
    
    def paintGL(self):
        """Paint the 3D view - simplified implementation"""
        # This would normally use OpenGL for 3D rendering
        # For now, just display a placeholder
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        if not self.current_model:
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                           "No collision model selected")
            return
        
        # Draw simplified representation
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(10, 20, f"Model: {self.current_model.name}")
        
        stats = self.current_model.get_stats()
        y_pos = 40
        for key, value in stats.items():
            if value > 0:
                painter.drawText(10, y_pos, f"{key}: {value}")
                y_pos += 20
        
        # Draw basic wireframe representation
        if self.show_mesh and self.current_model.vertices:
            painter.setPen(QPen(QColor(0, 255, 0), 1))
            # Simplified 2D projection of 3D vertices
            center_x = self.width() // 2
            center_y = self.height() // 2
            scale = 50 * self.zoom
            
            # Draw vertices as points
            for vertex in self.current_model.vertices:
                x = center_x + int(vertex.position.x * scale)
                y = center_y + int(vertex.position.y * scale)
                painter.drawEllipse(x - 2, y - 2, 4, 4)
        
        # Draw spheres
        if self.show_spheres and self.current_model.spheres:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            center_x = self.width() // 2
            center_y = self.height() // 2
            scale = 50 * self.zoom
            
            for sphere in self.current_model.spheres:
                x = center_x + int(sphere.center.x * scale)
                y = center_y + int(sphere.center.y * scale)
                radius = int(sphere.radius * scale)
                painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
        
        # Draw boxes
        if self.show_boxes and self.current_model.boxes:
            painter.setPen(QPen(QColor(0, 0, 255), 2))
            center_x = self.width() // 2
            center_y = self.height() // 2
            scale = 50 * self.zoom
            
            for box in self.current_model.boxes:
                x1 = center_x + int(box.min.x * scale)
                y1 = center_y + int(box.min.y * scale)
                x2 = center_x + int(box.max.x * scale)
                y2 = center_y + int(box.max.y * scale)
                painter.drawRect(x1, y1, x2 - x1, y2 - y1)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.last_mouse_pos = event.position()
        self.mouse_buttons = event.buttons()
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement"""
        if self.last_mouse_pos is None:
            return
        
        dx = event.position().x() - self.last_mouse_pos.x()
        dy = event.position().y() - self.last_mouse_pos.y()
        
        if self.mouse_buttons & Qt.MouseButton.LeftButton:
            # Rotate
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
            self.update()
        elif self.mouse_buttons & Qt.MouseButton.RightButton:
            # Zoom
            self.zoom *= (1.0 + dy * 0.01)
            self.zoom = max(0.1, min(10.0, self.zoom))
            self.update()
        
        self.last_mouse_pos = event.position()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.last_mouse_pos = None
        self.mouse_buttons = Qt.MouseButton.NoButton

class COLEditorDialog(QDialog):
    """Main COL editor dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Editor - Img Factory 1.5")
        self.setMinimumSize(1200, 800)
        self.col_file: Optional[COLFile] = None
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("📂 Open COL")
        self.save_btn = QPushButton("💾 Save COL")
        self.export_btn = QPushButton("📤 Export")
        self.import_btn = QPushButton("📥 Import")
        
        toolbar_layout.addWidget(self.open_btn)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addSeparator()
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.import_btn)
        toolbar_layout.addStretch()
        
        # View options
        self.show_spheres_cb = QCheckBox("Spheres")
        self.show_spheres_cb.setChecked(True)
        self.show_boxes_cb = QCheckBox("Boxes")
        self.show_boxes_cb.setChecked(True)
        self.show_mesh_cb = QCheckBox("Mesh")
        self.show_mesh_cb.setChecked(True)
        self.wireframe_cb = QCheckBox("Wireframe")
        
        toolbar_layout.addWidget(QLabel("Show:"))
        toolbar_layout.addWidget(self.show_spheres_cb)
        toolbar_layout.addWidget(self.show_boxes_cb)
        toolbar_layout.addWidget(self.show_mesh_cb)
        toolbar_layout.addWidget(self.wireframe_cb)
        
        layout.addLayout(toolbar_layout)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - model tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Models:"))
        
        self.model_tree = COLModelTreeWidget()
        left_layout.addWidget(self.model_tree)
        
        left_panel.setMaximumWidth(300)
        main_splitter.addWidget(left_panel)
        
        # Center panel - 3D view
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.addWidget(QLabel("3D View:"))
        
        self.viewer_3d = COLViewer3D()
        center_layout.addWidget(self.viewer_3d)
        
        main_splitter.addWidget(center_panel)
        
        # Right panel - properties
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.properties_widget = COLPropertiesWidget()
        right_layout.addWidget(self.properties_widget)
        
        right_panel.setMaximumWidth(350)
        main_splitter.addWidget(right_panel)
        
        # Set splitter sizes
        main_splitter.setSizes([300, 600, 350])
        layout.addWidget(main_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def connect_signals(self):
        """Connect UI signals"""
        self.open_btn.clicked.connect(self.open_col_file)
        self.save_btn.clicked.connect(self.save_col_file)
        self.export_btn.clicked.connect(self.export_elements)
        self.import_btn.clicked.connect(self.import_elements)
        
        self.model_tree.model_selected.connect(self.on_model_selected)
        self.model_tree.element_selected.connect(self.on_element_selected)
        
        self.show_spheres_cb.toggled.connect(self.update_view_options)
        self.show_boxes_cb.toggled.connect(self.update_view_options)
        self.show_mesh_cb.toggled.connect(self.update_view_options)
        self.wireframe_cb.toggled.connect(self.update_view_options)
    
    def open_col_file(self):
        """Open COL file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_file(file_path)
    
    def load_col_file(self, file_path: str):
        """Load COL file"""
        try:
            self.col_file = COLFile(file_path)
            if self.col_file.load():
                self.model_tree.load_col_file(self.col_file)
                self.viewer_3d.set_col_file(self.col_file)
                self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)} - {len(self.col_file.models)} models")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load COL file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading COL file: {str(e)}")
    
    def save_col_file(self):
        """Save COL file"""
        if not self.col_file:
            return
        
        try:
            if self.col_file.save():
                self.status_bar.showMessage("COL file saved successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to save COL file")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving COL file: {str(e)}")
    
    def export_elements(self):
        """Export collision elements"""
        QMessageBox.information(self, "Export", "Export functionality coming soon!")
    
    def import_elements(self):
        """Import collision elements"""
        QMessageBox.information(self, "Import", "Import functionality coming soon!")
    
    def on_model_selected(self, model: COLModel):
        """Handle model selection"""
        self.properties_widget.set_model(model)
        self.viewer_3d.set_current_model(model)
        self.status_bar.showMessage(f"Selected model: {model.name}")
    
    def on_element_selected(self, element_type: str, element_index: int):
        """Handle element selection"""
        self.properties_widget.set_element(element_type, element_index)
        self.status_bar.showMessage(f"Selected {element_type} #{element_index}")
    
    def update_view_options(self):
        """Update 3D view options"""
        self.viewer_3d.show_spheres = self.show_spheres_cb.isChecked()
        self.viewer_3d.show_boxes = self.show_boxes_cb.isChecked()
        self.viewer_3d.show_mesh = self.show_mesh_cb.isChecked()
        self.viewer_3d.show_wireframe = self.wireframe_cb.isChecked()
        self.viewer_3d.update()

# Convenience function for integration with main IMG Factory
def open_col_editor(parent=None, col_file_path: str = None):
    """Open COL editor dialog"""
    editor = COLEditorDialog(parent)
    
    if col_file_path:
        editor.load_col_file(col_file_path)
    
    return editor.exec()
