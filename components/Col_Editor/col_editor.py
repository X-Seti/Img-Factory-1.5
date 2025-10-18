#!/usr/bin/env python3

#this belongs in components.Col_Editor.col_editor.py - Version: 6
# X-Seti - August13 2025 - IMG Factory 1.5 - Enhanced COL Editor
# Enhanced version with better integration and 3D viewer improvements

"""
Enhanced COL Editor - Collision file editor with improved 3D visualization
Provides complete COL editing capabilities with model viewer and property editor
ENHANCED: Better integration with IMG Factory systems and improved UI
"""

import os
import sys
import tempfile
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
    QGroupBox, QCheckBox, QTextEdit, QFileDialog, QMessageBox,
    QStatusBar, QMenuBar, QToolBar, QComboBox, QSlider, QFormLayout,
    QTableWidget, QTableWidgetItem, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon

# Add project root to path for standalone execution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Now import everything without try/except
try:
    # When running from main app
    from debug.img_debug_functions import img_debugger
    from methods.col_core_classes import COLFile, COLModel, COLVersion, Vector3
except ImportError:
    # When running standalone
    from img_debug_functions import img_debugger
    from col_core_classes import COLFile, COLModel, COLVersion, Vector3

# These should work now with project root in path
from methods.col_operations import get_col_detailed_analysis, create_temporary_col_file, cleanup_temporary_file
from gui.col_dialogs import show_col_analysis_dialog

##Methods list -
# apply_changes
# create_new_model
# delete_model
# export_model
# import_elements
# load_col_file
# on_element_selected
# on_model_selected
# open_col_editor
# refresh_model_list
# save_col_file
# update_view_options

##Classes -
# COLEditorDialog
# COLModelListWidget  
# COLPropertiesWidget
# COLViewer3D
# COLToolbar

class COLViewer3D(QLabel): #vers 2
    """Enhanced 3D viewer widget for COL models"""
    
    model_selected = pyqtSignal(int)  # Model index selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #555555;
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        
        # View options
        self.show_spheres = True
        self.show_boxes = True
        self.show_mesh = True
        self.show_wireframe = False
        self.show_bounds = True
        
        self.current_model = None
        self.current_file = None
        self.selected_model_index = -1
        
        self.update_display()
    
    def set_current_file(self, col_file: COLFile): #vers 1
        """Set current COL file for display"""
        self.current_file = col_file
        self.selected_model_index = -1
        self.current_model = None
        self.update_display()
    
    def set_current_model(self, model: COLModel, model_index: int = -1): #vers 2
        """Set current model for display"""
        self.current_model = model
        self.selected_model_index = model_index
        self.update_display()
        
        if model:
            img_debugger.debug(f"3D Viewer showing model: {model.name}")
    
    def set_view_options(self, show_spheres=None, show_boxes=None, show_mesh=None, show_wireframe=None, show_bounds=None): #vers 1
        """Update view options"""
        if show_spheres is not None:
            self.show_spheres = show_spheres
        if show_boxes is not None:
            self.show_boxes = show_boxes
        if show_mesh is not None:
            self.show_mesh = show_mesh
        if show_wireframe is not None:
            self.show_wireframe = show_wireframe
        if show_bounds is not None:
            self.show_bounds = show_bounds
        
        self.update_display()
    
    def update_display(self): #vers 1
        """Update 3D viewer display"""
        try:
            if not self.current_file and not self.current_model:
                self.setText("3D Viewer\n\nNo COL file loaded\nUse File > Open to load a COL file")
                return
            
            if self.current_file and not self.current_model:
                # Show file overview
                model_count = len(self.current_file.models) if hasattr(self.current_file, 'models') else 0
                display_text = "3D Viewer - File Overview\n\n"
                display_text += f"COL File: {os.path.basename(getattr(self.current_file, 'file_path', 'Unknown'))}\n"
                display_text += f"Models: {model_count}\n\n"
                
                if model_count > 0 and hasattr(self.current_file, 'models'):
                    display_text += "Models (click to select):\n"
                    for i, model in enumerate(self.current_file.models[:10]):  # Show first 10
                        indicator = "→ " if i == self.selected_model_index else "  "
                        display_text += f"{indicator}{i+1}: {getattr(model, 'name', f'Model_{i}')}\n"
                    
                    if model_count > 10:
                        display_text += f"  ... and {model_count - 10} more models\n"
                
                display_text += "\nView Options:\n"
                display_text += f"Spheres: {'✅' if self.show_spheres else '❌'}\n"
                display_text += f"Boxes: {'✅' if self.show_boxes else '❌'}\n"
                display_text += f"Mesh: {'✅' if self.show_mesh else '❌'}\n"
                display_text += f"Wireframe: {'✅' if self.show_wireframe else '❌'}\n"
                display_text += f"Bounds: {'✅' if self.show_bounds else '❌'}\n"
                
                self.setText(display_text)
                return
            
            if self.current_model:
                # Show model details
                display_text = "3D Viewer - Model View\n\n"
                display_text += f"Model: {getattr(self.current_model, 'name', 'Unknown')}\n"
                display_text += f"Version: {getattr(self.current_model, 'version', 'Unknown')}\n\n"
                
                # Collision elements
                spheres = getattr(self.current_model, 'spheres', [])
                boxes = getattr(self.current_model, 'boxes', [])
                faces = getattr(self.current_model, 'faces', [])
                vertices = getattr(self.current_model, 'vertices', [])
                
                display_text += "Collision Elements:\n"
                display_text += f"Spheres: {len(spheres)} {'(shown)' if self.show_spheres else '(hidden)'}\n"
                display_text += f"Boxes: {len(boxes)} {'(shown)' if self.show_boxes else '(hidden)'}\n"
                display_text += f"Faces: {len(faces)} {'(shown)' if self.show_mesh else '(hidden)'}\n"
                display_text += f"Vertices: {len(vertices)}\n\n"
                
                # Bounding box info
                if hasattr(self.current_model, 'bounding_box') and self.current_model.bounding_box:
                    bbox = self.current_model.bounding_box
                    display_text += "Bounding Box:\n"
                    if hasattr(bbox, 'center'):
                        display_text += f"Center: ({bbox.center.x:.2f}, {bbox.center.y:.2f}, {bbox.center.z:.2f})\n"
                    if hasattr(bbox, 'radius'):
                        display_text += f"Radius: {bbox.radius:.2f}\n"
                
                display_text += "\n[Future: OpenGL 3D visualization will be displayed here]"
                self.setText(display_text)
            
        except Exception as e:
            self.setText(f"3D Viewer Error:\n\n{str(e)}")
            img_debugger.error(f"Error updating 3D viewer display: {str(e)}")
    
    def mousePressEvent(self, event): #vers 1
        """Handle mouse clicks for model selection"""
        if event.button() == Qt.MouseButton.LeftButton and self.current_file:
            # Simple model selection - in future this would be 3D picking
            if hasattr(self.current_file, 'models') and self.current_file.models:
                # Cycle through models for now
                current_index = self.selected_model_index
                next_index = (current_index + 1) % len(self.current_file.models)
                
                self.selected_model_index = next_index
                self.current_model = self.current_file.models[next_index]
                self.update_display()
                self.model_selected.emit(next_index)
        
        super().mousePressEvent(event)

class COLPropertiesWidget(QTabWidget): #vers 2
    """Enhanced properties editor widget for COL elements"""
    
    property_changed = pyqtSignal(str, object)  # property_name, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_model = None
        
        self.setup_tabs()
    
    def setup_tabs(self): #vers 1
        """Setup property tabs"""
        # Model properties tab
        self.model_tab = QWidget()
        self.setup_model_tab()
        self.addTab(self.model_tab, "📄 Model")
        
        # Spheres tab
        self.spheres_tab = QWidget()
        self.setup_spheres_tab()
        self.addTab(self.spheres_tab, "🔵 Spheres")
        
        # Boxes tab
        self.boxes_tab = QWidget()
        self.setup_boxes_tab()
        self.addTab(self.boxes_tab, "📦 Boxes")
        
        # Mesh tab
        self.mesh_tab = QWidget()
        self.setup_mesh_tab()
        self.addTab(self.mesh_tab, "🌐 Mesh")
    
    def setup_model_tab(self): #vers 1
        """Setup model properties tab"""
        layout = QVBoxLayout(self.model_tab)
        
        # Model info group
        info_group = QGroupBox("Model Information")
        info_layout = QFormLayout(info_group)
        
        self.model_name_edit = QLineEdit()
        self.model_name_edit.textChanged.connect(lambda text: self.property_changed.emit('name', text))
        info_layout.addRow("Name:", self.model_name_edit)
        
        self.model_version_combo = QComboBox()
        for version in COLVersion:
            self.model_version_combo.addItem(f"COL{version.value}", version)
        self.model_version_combo.currentIndexChanged.connect(self.on_version_changed)
        info_layout.addRow("Version:", self.model_version_combo)
        
        self.model_id_spin = QSpinBox()
        self.model_id_spin.setRange(0, 65535)
        self.model_id_spin.valueChanged.connect(lambda value: self.property_changed.emit('model_id', value))
        info_layout.addRow("Model ID:", self.model_id_spin)
        
        layout.addWidget(info_group)
        
        # Bounding box group
        bbox_group = QGroupBox("Bounding Box")
        bbox_layout = QFormLayout(bbox_group)
        
        # Center coordinates
        center_layout = QHBoxLayout()
        self.center_x_spin = QDoubleSpinBox()
        self.center_x_spin.setRange(-999999, 999999)
        self.center_x_spin.setDecimals(3)
        center_layout.addWidget(self.center_x_spin)
        
        self.center_y_spin = QDoubleSpinBox()
        self.center_y_spin.setRange(-999999, 999999)
        self.center_y_spin.setDecimals(3)
        center_layout.addWidget(self.center_y_spin)
        
        self.center_z_spin = QDoubleSpinBox()
        self.center_z_spin.setRange(-999999, 999999)
        self.center_z_spin.setDecimals(3)
        center_layout.addWidget(self.center_z_spin)
        
        bbox_layout.addRow("Center (X,Y,Z):", center_layout)
        
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(0, 999999)
        self.radius_spin.setDecimals(3)
        bbox_layout.addRow("Radius:", self.radius_spin)
        
        layout.addWidget(bbox_group)
        layout.addStretch()
    
    def setup_spheres_tab(self): #vers 1
        """Setup spheres tab"""
        layout = QVBoxLayout(self.spheres_tab)
        
        # Spheres table
        self.spheres_table = QTableWidget()
        self.spheres_table.setColumnCount(5)
        self.spheres_table.setHorizontalHeaderLabels([
            "Center X", "Center Y", "Center Z", "Radius", "Material"
        ])
        layout.addWidget(self.spheres_table)
        
        # Spheres buttons
        spheres_buttons = QHBoxLayout()
        
        self.add_sphere_btn = QPushButton("➕ Add Sphere")
        self.add_sphere_btn.clicked.connect(self.add_sphere)
        spheres_buttons.addWidget(self.add_sphere_btn)
        
        self.remove_sphere_btn = QPushButton("➖ Remove Sphere")
        self.remove_sphere_btn.clicked.connect(self.remove_sphere)
        spheres_buttons.addWidget(self.remove_sphere_btn)
        
        spheres_buttons.addStretch()
        layout.addLayout(spheres_buttons)
    
    def setup_boxes_tab(self): #vers 1
        """Setup boxes tab"""
        layout = QVBoxLayout(self.boxes_tab)
        
        # Boxes table
        self.boxes_table = QTableWidget()
        self.boxes_table.setColumnCount(7)
        self.boxes_table.setHorizontalHeaderLabels([
            "Min X", "Min Y", "Min Z", "Max X", "Max Y", "Max Z", "Material"
        ])
        layout.addWidget(self.boxes_table)
        
        # Boxes buttons
        boxes_buttons = QHBoxLayout()
        
        self.add_box_btn = QPushButton("➕ Add Box")
        self.add_box_btn.clicked.connect(self.add_box)
        boxes_buttons.addWidget(self.add_box_btn)
        
        self.remove_box_btn = QPushButton("➖ Remove Box")
        self.remove_box_btn.clicked.connect(self.remove_box)
        boxes_buttons.addWidget(self.remove_box_btn)
        
        boxes_buttons.addStretch()
        layout.addLayout(boxes_buttons)
    
    def setup_mesh_tab(self): #vers 1
        """Setup mesh tab"""
        layout = QVBoxLayout(self.mesh_tab)
        
        # Mesh info
        info_layout = QFormLayout()
        
        self.vertices_count_label = QLabel("0")
        info_layout.addRow("Vertices:", self.vertices_count_label)
        
        self.faces_count_label = QLabel("0")
        info_layout.addRow("Faces:", self.faces_count_label)
        
        layout.addLayout(info_layout)
        
        # Mesh buttons
        mesh_buttons = QHBoxLayout()
        
        self.import_mesh_btn = QPushButton("📥 Import Mesh")
        self.import_mesh_btn.clicked.connect(self.import_mesh)
        mesh_buttons.addWidget(self.import_mesh_btn)
        
        self.export_mesh_btn = QPushButton("📤 Export Mesh")
        self.export_mesh_btn.clicked.connect(self.export_mesh)
        mesh_buttons.addWidget(self.export_mesh_btn)
        
        mesh_buttons.addStretch()
        layout.addLayout(mesh_buttons)
        
        layout.addStretch()
    
    def set_current_model(self, model: COLModel): #vers 1
        """Set current model for editing"""
        self.current_model = model
        self.update_properties()
    
    def update_properties(self): #vers 1
        """Update property displays"""
        if not self.current_model:
            self.clear_properties()
            return
        
        try:
            # Update model properties
            if hasattr(self.current_model, 'name'):
                self.model_name_edit.setText(self.current_model.name)
            
            if hasattr(self.current_model, 'version'):
                version_index = list(COLVersion).index(self.current_model.version)
                self.model_version_combo.setCurrentIndex(version_index)
            
            if hasattr(self.current_model, 'model_id'):
                self.model_id_spin.setValue(self.current_model.model_id)
            
            # Update bounding box
            if hasattr(self.current_model, 'bounding_box') and self.current_model.bounding_box:
                bbox = self.current_model.bounding_box
                if hasattr(bbox, 'center'):
                    self.center_x_spin.setValue(bbox.center.x)
                    self.center_y_spin.setValue(bbox.center.y)
                    self.center_z_spin.setValue(bbox.center.z)
                if hasattr(bbox, 'radius'):
                    self.radius_spin.setValue(bbox.radius)
            
            # Update spheres table
            self.update_spheres_table()
            
            # Update boxes table
            self.update_boxes_table()
            
            # Update mesh info
            self.update_mesh_info()
            
        except Exception as e:
            img_debugger.error(f"Error updating properties: {str(e)}")
    
    def clear_properties(self): #vers 1
        """Clear all property displays"""
        self.model_name_edit.clear()
        self.model_version_combo.setCurrentIndex(0)
        self.model_id_spin.setValue(0)
        self.center_x_spin.setValue(0)
        self.center_y_spin.setValue(0)
        self.center_z_spin.setValue(0)
        self.radius_spin.setValue(0)
        self.spheres_table.setRowCount(0)
        self.boxes_table.setRowCount(0)
        self.vertices_count_label.setText("0")
        self.faces_count_label.setText("0")
    
    def update_spheres_table(self): #vers 1
        """Update spheres table"""
        if not hasattr(self.current_model, 'spheres'):
            self.spheres_table.setRowCount(0)
            return
        
        spheres = self.current_model.spheres
        self.spheres_table.setRowCount(len(spheres))
        
        for i, sphere in enumerate(spheres):
            if hasattr(sphere, 'center'):
                self.spheres_table.setItem(i, 0, QTableWidgetItem(f"{sphere.center.x:.3f}"))
                self.spheres_table.setItem(i, 1, QTableWidgetItem(f"{sphere.center.y:.3f}"))
                self.spheres_table.setItem(i, 2, QTableWidgetItem(f"{sphere.center.z:.3f}"))
            if hasattr(sphere, 'radius'):
                self.spheres_table.setItem(i, 3, QTableWidgetItem(f"{sphere.radius:.3f}"))
            if hasattr(sphere, 'material'):
                self.spheres_table.setItem(i, 4, QTableWidgetItem(str(sphere.material)))
    
    def update_boxes_table(self): #vers 1
        """Update boxes table"""
        if not hasattr(self.current_model, 'boxes'):
            self.boxes_table.setRowCount(0)
            return
        
        boxes = self.current_model.boxes
        self.boxes_table.setRowCount(len(boxes))
        
        for i, box in enumerate(boxes):
            if hasattr(box, 'min_point'):
                self.boxes_table.setItem(i, 0, QTableWidgetItem(f"{box.min_point.x:.3f}"))
                self.boxes_table.setItem(i, 1, QTableWidgetItem(f"{box.min_point.y:.3f}"))
                self.boxes_table.setItem(i, 2, QTableWidgetItem(f"{box.min_point.z:.3f}"))
            if hasattr(box, 'max_point'):
                self.boxes_table.setItem(i, 3, QTableWidgetItem(f"{box.max_point.x:.3f}"))
                self.boxes_table.setItem(i, 4, QTableWidgetItem(f"{box.max_point.y:.3f}"))
                self.boxes_table.setItem(i, 5, QTableWidgetItem(f"{box.max_point.z:.3f}"))
            if hasattr(box, 'material'):
                self.boxes_table.setItem(i, 6, QTableWidgetItem(str(box.material)))
    
    def update_mesh_info(self): #vers 1
        """Update mesh information"""
        if not self.current_model:
            return
        
        vertices_count = len(getattr(self.current_model, 'vertices', []))
        faces_count = len(getattr(self.current_model, 'faces', []))
        
        self.vertices_count_label.setText(str(vertices_count))
        self.faces_count_label.setText(str(faces_count))
    
    def on_version_changed(self): #vers 1
        """Handle version change"""
        if self.current_model:
            new_version = self.model_version_combo.currentData()
            self.property_changed.emit('version', new_version)
    
    def add_sphere(self): #vers 1
        """Add new sphere"""
        img_debugger.info("Add sphere - not yet implemented")
    
    def remove_sphere(self): #vers 1
        """Remove selected sphere"""
        img_debugger.info("Remove sphere - not yet implemented")
    
    def add_box(self): #vers 1
        """Add new box"""
        img_debugger.info("Add box - not yet implemented")
    
    def remove_box(self): #vers 1
        """Remove selected box"""
        img_debugger.info("Remove box - not yet implemented")
    
    def import_mesh(self): #vers 1
        """Import mesh from file"""
        img_debugger.info("Import mesh - not yet implemented")
    
    def export_mesh(self): #vers 1
        """Export mesh to file"""
        img_debugger.info("Export mesh - not yet implemented")

class COLModelListWidget(QListWidget): #vers 1
    """Enhanced model list widget"""
    
    model_selected = pyqtSignal(int)  # Model index
    model_context_menu = pyqtSignal(int, object)  # Model index, position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect selection
        self.currentRowChanged.connect(self.on_selection_changed)
    
    def set_col_file(self, col_file: COLFile): #vers 1
        """Set COL file and populate list"""
        self.current_file = col_file
        self.populate_models()
    
    def populate_models(self): #vers 1
        """Populate model list"""
        self.clear()
        
        if not self.current_file or not hasattr(self.current_file, 'models'):
            return
        
        for i, model in enumerate(self.current_file.models):
            name = getattr(model, 'name', f'Model_{i}')
            version = getattr(model, 'version', COLVersion.COL_1)
            
            # Count collision elements
            spheres = len(getattr(model, 'spheres', []))
            boxes = len(getattr(model, 'boxes', []))
            faces = len(getattr(model, 'faces', []))
            
            item_text = f"{name} ({version.name} - S:{spheres} B:{boxes} F:{faces})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store model index
            self.addItem(item)
    
    def on_selection_changed(self, row): #vers 1
        """Handle selection change"""
        if row >= 0:
            self.model_selected.emit(row)
    
    def show_context_menu(self, position): #vers 1
        """Show context menu"""
        item = self.itemAt(position)
        if item:
            model_index = item.data(Qt.ItemDataRole.UserRole)
            self.model_context_menu.emit(model_index, self.mapToGlobal(position))

class COLToolbar(QToolBar): #vers 1
    """COL editor toolbar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        
        self.setup_actions()
    
    def setup_actions(self): #vers 1
        """Setup toolbar actions"""
        # File actions
        self.open_action = QAction("📂 Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.addAction(self.open_action)
        
        self.save_action = QAction("💾 Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.addAction(self.save_action)
        
        self.addSeparator()
        
        # View actions
        self.view_spheres_action = QAction("🔵 Spheres", self)
        self.view_spheres_action.setCheckable(True)
        self.view_spheres_action.setChecked(True)
        self.addAction(self.view_spheres_action)
        
        self.view_boxes_action = QAction("📦 Boxes", self)
        self.view_boxes_action.setCheckable(True)
        self.view_boxes_action.setChecked(True)
        self.addAction(self.view_boxes_action)
        
        self.view_mesh_action = QAction("🌐 Mesh", self)
        self.view_mesh_action.setCheckable(True)
        self.view_mesh_action.setChecked(True)
        self.addAction(self.view_mesh_action)
        
        self.addSeparator()
        
        # Analysis action
        self.analyze_action = QAction("📊 Analyze", self)
        self.addAction(self.analyze_action)

class COLEditorDialog(QDialog): #vers 3
    """Enhanced COL Editor Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Editor - IMG Factory 1.5")
        self.setModal(False)  # Allow non-modal operation
        self.resize(1000, 700)
        
        self.current_file = None
        self.current_model = None
        self.file_path = None
        self.is_modified = False
        
        self.setup_ui()
        self.connect_signals()
        
        img_debugger.debug("COL Editor dialog created")
    
    def setup_ui(self): #vers 1
        """Setup editor UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        self.toolbar = COLToolbar(self)
        layout.addWidget(self.toolbar)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel - Model list and properties
        left_panel = QSplitter(Qt.Orientation.Vertical)
        left_panel.setFixedWidth(350)
        
        # Model list
        models_group = QGroupBox("Models")
        models_layout = QVBoxLayout(models_group)
        
        self.model_list = COLModelListWidget()
        models_layout.addWidget(self.model_list)
        
        left_panel.addWidget(models_group)
        
        # Properties
        properties_group = QGroupBox("Properties")
        properties_layout = QVBoxLayout(properties_group)
        
        self.properties_widget = COLPropertiesWidget()
        properties_layout.addWidget(self.properties_widget)
        
        left_panel.addWidget(properties_group)
        
        # Set left panel sizes
        left_panel.setSizes([200, 400])
        
        main_splitter.addWidget(left_panel)
        
        # Right panel - 3D viewer
        viewer_group = QGroupBox("3D Viewer")
        viewer_layout = QVBoxLayout(viewer_group)
        
        self.viewer_3d = COLViewer3D()
        viewer_layout.addWidget(self.viewer_3d)
        
        main_splitter.addWidget(viewer_group)
        
        # Set main splitter sizes
        main_splitter.setSizes([350, 650])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        layout.addWidget(self.status_bar)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def connect_signals(self): #vers 1
        """Connect UI signals"""
        # Toolbar actions
        self.toolbar.open_action.triggered.connect(self.open_file)
        self.toolbar.save_action.triggered.connect(self.save_file)
        self.toolbar.analyze_action.triggered.connect(self.analyze_file)
        
        # View options
        self.toolbar.view_spheres_action.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_spheres=checked)
        )
        self.toolbar.view_boxes_action.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_boxes=checked)
        )
        self.toolbar.view_mesh_action.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_mesh=checked)
        )
        
        # Model selection
        self.model_list.model_selected.connect(self.on_model_selected)
        self.viewer_3d.model_selected.connect(self.on_model_selected)
        
        # Properties changes
        self.properties_widget.property_changed.connect(self.on_property_changed)
    
    def load_col_file(self, file_path: str) -> bool: #vers 2
        """Load COL file - ENHANCED VERSION"""
        try:
            self.file_path = file_path
            self.status_bar.showMessage("Loading COL file...")
            self.progress_bar.setVisible(True)
            
            # Load the file
            self.current_file = COLFile(file_path)
            
            if not self.current_file.load():
                error_msg = getattr(self.current_file, 'load_error', 'Unknown error')
                QMessageBox.critical(self, "Load Error", f"Failed to load COL file:\n{error_msg}")
                self.progress_bar.setVisible(False)
                self.status_bar.showMessage("Ready")
                return False
            
            # Update UI
            self.model_list.set_col_file(self.current_file)
            self.viewer_3d.set_current_file(self.current_file)
            
            # Select first model if available
            if hasattr(self.current_file, 'models') and self.current_file.models:
                self.model_list.setCurrentRow(0)
            
            model_count = len(getattr(self.current_file, 'models', []))
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)} ({model_count} models)")
            self.progress_bar.setVisible(False)
            
            self.setWindowTitle(f"COL Editor - {os.path.basename(file_path)}")
            self.is_modified = False
            
            img_debugger.success(f"COL file loaded: {file_path}")
            return True
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready")
            error_msg = f"Error loading COL file: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            img_debugger.error(error_msg)
            return False
    
    def open_file(self): #vers 1
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_file(file_path)
    
    def save_file(self): #vers 1
        """Save current file"""
        if not self.current_file:
            QMessageBox.warning(self, "Save", "No file loaded to save")
            return
        
        if not self.file_path:
            self.save_file_as()
            return
        
        try:
            self.status_bar.showMessage("Saving COL file...")
            
            # TODO: Implement actual saving
            # For now, just show a message
            QMessageBox.information(self, "Save", 
                "COL file saving will be implemented in a future version.\n"
                "Currently the editor is in view-only mode.")
            
            self.status_bar.showMessage("Ready")
            
        except Exception as e:
            error_msg = f"Error saving COL file: {str(e)}"
            QMessageBox.critical(self, "Save Error", error_msg)
            img_debugger.error(error_msg)
    
    def save_file_as(self): #vers 1
        """Save file as dialog"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.file_path = file_path
            self.save_file()
    
    def analyze_file(self): #vers 1
        """Analyze current COL file"""
        if not self.current_file or not self.file_path:
            QMessageBox.warning(self, "Analyze", "No file loaded to analyze")
            return
        
        try:
            self.status_bar.showMessage("Analyzing COL file...")
            
            # Get detailed analysis
            analysis_data = get_col_detailed_analysis(self.file_path)
            
            if 'error' in analysis_data:
                QMessageBox.warning(self, "Analysis Error", f"Analysis failed: {analysis_data['error']}")
                return
            
            # Show analysis dialog
            show_col_analysis_dialog(self, analysis_data, os.path.basename(self.file_path))
            
            self.status_bar.showMessage("Ready")
            
        except Exception as e:
            error_msg = f"Error analyzing COL file: {str(e)}"
            QMessageBox.critical(self, "Analysis Error", error_msg)
            img_debugger.error(error_msg)
    
    def on_model_selected(self, model_index: int): #vers 1
        """Handle model selection"""
        try:
            if not self.current_file or not hasattr(self.current_file, 'models'):
                return
            
            if model_index < 0 or model_index >= len(self.current_file.models):
                return
            
            # Update current model
            self.current_model = self.current_file.models[model_index]
            
            # Update viewer
            self.viewer_3d.set_current_model(self.current_model, model_index)
            
            # Update properties
            self.properties_widget.set_current_model(self.current_model)
            
            # Update list selection if needed
            if self.model_list.currentRow() != model_index:
                self.model_list.setCurrentRow(model_index)
            
            model_name = getattr(self.current_model, 'name', f'Model_{model_index}')
            self.status_bar.showMessage(f"Selected: {model_name}")
            
            img_debugger.debug(f"Model selected: {model_name} (index {model_index})")
            
        except Exception as e:
            img_debugger.error(f"Error selecting model: {str(e)}")
    
    def on_property_changed(self, property_name: str, new_value): #vers 1
        """Handle property change"""
        try:
            if not self.current_model:
                return
            
            # Apply property change
            if property_name == 'name':
                self.current_model.name = new_value
            elif property_name == 'version':
                self.current_model.version = new_value
            elif property_name == 'model_id':
                self.current_model.model_id = new_value
            
            # Mark as modified
            self.is_modified = True
            self.setWindowTitle(f"COL Editor - {os.path.basename(self.file_path or 'Untitled')} *")
            
            # Update displays
            self.model_list.populate_models()
            self.viewer_3d.update_display()
            
            img_debugger.debug(f"Property changed: {property_name} = {new_value}")
            
        except Exception as e:
            img_debugger.error(f"Error changing property: {str(e)}")
    
    def closeEvent(self, event): #vers 1
        """Handle close event"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "The file has unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        
        img_debugger.debug("COL Editor dialog closed")

# Convenience functions
def open_col_editor(parent=None, file_path: str = None) -> COLEditorDialog: #vers 2
    """Open COL editor dialog - ENHANCED VERSION"""
    try:
        editor = COLEditorDialog(parent)
        
        if file_path:
            if editor.load_col_file(file_path):
                img_debugger.success(f"COL editor opened with file: {file_path}")
            else:
                img_debugger.error(f"Failed to load file in COL editor: {file_path}")
        
        editor.show()
        return editor
        
    except Exception as e:
        img_debugger.error(f"Error opening COL editor: {str(e)}")
        if parent:
            QMessageBox.critical(parent, "COL Editor Error", f"Failed to open COL editor:\n{str(e)}")
        return None

def create_new_model(model_name: str = "New Model") -> COLModel: #vers 1
    """Create new COL model"""
    try:
        model = COLModel()
        model.name = model_name
        model.version = COLVersion.COL_2  # Default to COL2
        model.spheres = []
        model.boxes = []
        model.vertices = []
        model.faces = []
        
        # Initialize bounding box
        if hasattr(model, 'calculate_bounding_box'):
            model.calculate_bounding_box()
        
        img_debugger.debug(f"Created new COL model: {model_name}")
        return model
        
    except Exception as e:
        img_debugger.error(f"Error creating new COL model: {str(e)}")
        return None

def delete_model(col_file: COLFile, model_index: int) -> bool: #vers 1
    """Delete model from COL file"""
    try:
        if not hasattr(col_file, 'models') or not col_file.models:
            return False
        
        if model_index < 0 or model_index >= len(col_file.models):
            return False
        
        model_name = getattr(col_file.models[model_index], 'name', f'Model_{model_index}')
        del col_file.models[model_index]
        
        img_debugger.debug(f"Deleted COL model: {model_name}")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error deleting COL model: {str(e)}")
        return False

def export_model(model: COLModel, file_path: str) -> bool: #vers 1
    """Export single model to file"""
    try:
        # TODO: Implement model export
        img_debugger.info(f"Model export to {file_path} - not yet implemented")
        return False
        
    except Exception as e:
        img_debugger.error(f"Error exporting model: {str(e)}")
        return False

def import_elements(model: COLModel, file_path: str) -> bool: #vers 1
    """Import collision elements from file"""
    try:
        # TODO: Implement element import
        img_debugger.info(f"Element import from {file_path} - not yet implemented")
        return False
        
    except Exception as e:
        img_debugger.error(f"Error importing elements: {str(e)}")
        return False

def refresh_model_list(list_widget: COLModelListWidget, col_file: COLFile): #vers 1
    """Refresh model list widget"""
    try:
        list_widget.set_col_file(col_file)
        img_debugger.debug("Model list refreshed")
        
    except Exception as e:
        img_debugger.error(f"Error refreshing model list: {str(e)}")

def update_view_options(viewer: COLViewer3D, **options): #vers 1
    """Update 3D viewer options"""
    try:
        viewer.set_view_options(**options)
        img_debugger.debug(f"View options updated: {options}")
        
    except Exception as e:
        img_debugger.error(f"Error updating view options: {str(e)}")

def apply_changes(editor: COLEditorDialog) -> bool: #vers 1
    """Apply all pending changes"""
    try:
        # TODO: Implement change application
        img_debugger.info("Apply changes - not yet implemented")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error applying changes: {str(e)}")
        return False

# Export classes and functions
__all__ = [
    'COLEditorDialog',
    'COLViewer3D',
    'COLPropertiesWidget', 
    'COLModelListWidget',
    'COLToolbar',
    'open_col_editor',
    'create_new_model',
    'delete_model',
    'export_model',
    'import_elements',
    'refresh_model_list',
    'update_view_options',
    'apply_changes'
]
