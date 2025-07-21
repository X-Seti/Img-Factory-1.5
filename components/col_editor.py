#this belongs in components/col_editor.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Editor
# Complete COL file editor with 3D visualization using IMG debug system

"""
COL Editor - Collision file editor with 3D visualization
Provides complete COL editing capabilities with model viewer and property editor
"""

import os
from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
    QGroupBox, QCheckBox, QTextEdit, QFileDialog, QMessageBox,
    QStatusBar, QMenuBar, QToolBar, QComboBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFont

# Import IMG debug system and COL classes
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile, COLModel, COLVersion, Vector3

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

class COLViewer3D(QLabel):
    """3D viewer widget for COL models (placeholder)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("border: 1px solid gray; background-color: #2a2a2a;")
        self.setText("3D Viewer\n(Coming Soon)")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # View options
        self.show_spheres = True
        self.show_boxes = True
        self.show_mesh = True
        self.show_wireframe = False
        
        self.current_model = None
    
    def set_current_model(self, model: COLModel): #vers 1
        """Set current model for display"""
        self.current_model = model
        if model:
            info = f"3D Viewer\nModel: {model.name}\n"
            info += f"Spheres: {len(model.spheres)}\n"
            info += f"Boxes: {len(model.boxes)}\n"
            info += f"Faces: {len(model.faces)}"
            self.setText(info)
            img_debugger.debug(f"3D Viewer showing model: {model.name}")
        else:
            self.setText("3D Viewer\n(No Model)")

class COLPropertiesWidget(QWidget):
    """Properties editor widget for COL elements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_model = None
        self.current_element = None
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup properties UI"""
        layout = QVBoxLayout(self)
        
        # Model properties group
        model_group = QGroupBox("Model Properties")
        model_layout = QVBoxLayout(model_group)
        
        # Model name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_property_changed)
        name_layout.addWidget(self.name_edit)
        model_layout.addLayout(name_layout)
        
        # Model ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Model ID:"))
        self.id_spin = QSpinBox()
        self.id_spin.setRange(0, 999999)
        self.id_spin.valueChanged.connect(self.on_property_changed)
        id_layout.addWidget(self.id_spin)
        model_layout.addLayout(id_layout)
        
        # Version
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self.version_combo = QComboBox()
        self.version_combo.addItems(["COL 1", "COL 2", "COL 3", "COL 4"])
        self.version_combo.currentTextChanged.connect(self.on_property_changed)
        version_layout.addWidget(self.version_combo)
        model_layout.addLayout(version_layout)
        
        layout.addWidget(model_group)
        
        # Element properties group
        element_group = QGroupBox("Element Properties")
        element_layout = QVBoxLayout(element_group)
        
        self.element_props_widget = QTextEdit()
        self.element_props_widget.setMaximumHeight(150)
        self.element_props_widget.setPlainText("Select an element to view properties")
        element_layout.addWidget(self.element_props_widget)
        
        layout.addWidget(element_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
    
    def set_model(self, model: COLModel): #vers 1
        """Set current model"""
        self.current_model = model
        if model:
            self.name_edit.setText(model.name)
            self.id_spin.setValue(model.model_id)
            self.version_combo.setCurrentText(f"COL {model.version.value}")
            
            # Update statistics
            stats = f"Spheres: {len(model.spheres)}\n"
            stats += f"Boxes: {len(model.boxes)}\n"
            stats += f"Vertices: {len(model.vertices)}\n"
            stats += f"Faces: {len(model.faces)}"
            self.stats_text.setPlainText(stats)
        else:
            self.clear_properties()
    
    def set_element(self, element_type: str, element_index: int): #vers 1
        """Set current element for editing"""
        if not self.current_model:
            return
        
        props = f"Element Type: {element_type}\nIndex: {element_index}\n\n"
        
        try:
            if element_type == "sphere" and element_index < len(self.current_model.spheres):
                sphere = self.current_model.spheres[element_index]
                props += f"Center: ({sphere.center.x:.2f}, {sphere.center.y:.2f}, {sphere.center.z:.2f})\n"
                props += f"Radius: {sphere.radius:.2f}\n"
                props += f"Surface: {sphere.surface}\n"
                props += f"Piece: {sphere.piece}"
            elif element_type == "box" and element_index < len(self.current_model.boxes):
                box = self.current_model.boxes[element_index]
                props += f"Min: ({box.min.x:.2f}, {box.min.y:.2f}, {box.min.z:.2f})\n"
                props += f"Max: ({box.max.x:.2f}, {box.max.y:.2f}, {box.max.z:.2f})\n"
                props += f"Surface: {box.surface}\n"
                props += f"Piece: {box.piece}"
            elif element_type == "face" and element_index < len(self.current_model.faces):
                face = self.current_model.faces[element_index]
                props += f"Vertices: {face.a}, {face.b}, {face.c}\n"
                props += f"Surface: {face.surface}\n"
                props += f"Piece: {face.piece}"
            
        except Exception as e:
            props += f"Error reading element properties: {e}"
        
        self.element_props_widget.setPlainText(props)
        self.current_element = (element_type, element_index)
    
    def clear_properties(self): #vers 1
        """Clear all properties"""
        self.name_edit.clear()
        self.id_spin.setValue(0)
        self.version_combo.setCurrentIndex(0)
        self.element_props_widget.clear()
        self.stats_text.clear()
        self.current_model = None
        self.current_element = None
    
    def on_property_changed(self): #vers 1
        """Handle property changes"""
        if self.current_model:
            # Update model properties
            self.current_model.name = self.name_edit.text()
            self.current_model.model_id = self.id_spin.value()
            
            version_text = self.version_combo.currentText()
            if "1" in version_text:
                self.current_model.version = COLVersion.COL_1
            elif "2" in version_text:
                self.current_model.version = COLVersion.COL_2
            elif "3" in version_text:
                self.current_model.version = COLVersion.COL_3
            elif "4" in version_text:
                self.current_model.version = COLVersion.COL_4

class COLModelListWidget(QWidget):
    """Widget for displaying and managing COL models"""
    
    model_selected = pyqtSignal(object)  # COLModel
    element_selected = pyqtSignal(str, int)  # element_type, index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.col_file = None
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup model list UI"""
        layout = QVBoxLayout(self)
        
        # Models list
        models_label = QLabel("Models")
        layout.addWidget(models_label)
        
        self.models_list = QListWidget()
        self.models_list.currentRowChanged.connect(self.on_model_selected)
        layout.addWidget(self.models_list)
        
        # Elements tree
        elements_label = QLabel("Elements")
        layout.addWidget(elements_label)
        
        self.elements_tree = QTreeWidget()
        self.elements_tree.setHeaderLabel("Collision Elements")
        self.elements_tree.itemClicked.connect(self.on_element_clicked)
        layout.addWidget(self.elements_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_model_btn = QPushButton("Add Model")
        add_model_btn.clicked.connect(self.add_model)
        button_layout.addWidget(add_model_btn)
        
        delete_model_btn = QPushButton("Delete Model")
        delete_model_btn.clicked.connect(self.delete_model)
        button_layout.addWidget(delete_model_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def set_col_file(self, col_file: COLFile): #vers 1
        """Set COL file to display"""
        self.col_file = col_file
        self.refresh_model_list()
    
    def refresh_model_list(self): #vers 1
        """Refresh the model list display"""
        self.models_list.clear()
        self.elements_tree.clear()
        
        if not self.col_file or not self.col_file.models:
            return
        
        for i, model in enumerate(self.col_file.models):
            item_text = f"{model.name} (v{model.version.value})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.models_list.addItem(item)
        
        # Select first model by default
        if self.models_list.count() > 0:
            self.models_list.setCurrentRow(0)
    
    def on_model_selected(self, row: int): #vers 1
        """Handle model selection"""
        if row < 0 or not self.col_file or row >= len(self.col_file.models):
            return
        
        model = self.col_file.models[row]
        self.model_selected.emit(model)
        self.populate_elements_tree(model)
    
    def populate_elements_tree(self, model: COLModel): #vers 1
        """Populate elements tree for model"""
        self.elements_tree.clear()
        
        # Spheres
        if model.spheres:
            spheres_item = QTreeWidgetItem(["Spheres"])
            for i, sphere in enumerate(model.spheres):
                sphere_item = QTreeWidgetItem([f"Sphere {i}"])
                sphere_item.setData(0, Qt.ItemDataRole.UserRole, ("sphere", i))
                spheres_item.addChild(sphere_item)
            self.elements_tree.addTopLevelItem(spheres_item)
        
        # Boxes
        if model.boxes:
            boxes_item = QTreeWidgetItem(["Boxes"])
            for i, box in enumerate(model.boxes):
                box_item = QTreeWidgetItem([f"Box {i}"])
                box_item.setData(0, Qt.ItemDataRole.UserRole, ("box", i))
                boxes_item.addChild(box_item)
            self.elements_tree.addTopLevelItem(boxes_item)
        
        # Faces
        if model.faces:
            faces_item = QTreeWidgetItem(["Faces"])
            for i, face in enumerate(model.faces):
                face_item = QTreeWidgetItem([f"Face {i}"])
                face_item.setData(0, Qt.ItemDataRole.UserRole, ("face", i))
                faces_item.addChild(face_item)
            self.elements_tree.addTopLevelItem(faces_item)
        
        # Expand all items
        self.elements_tree.expandAll()
    
    def on_element_clicked(self, item: QTreeWidgetItem, column: int): #vers 1
        """Handle element click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            element_type, index = data
            self.element_selected.emit(element_type, index)
    
    def add_model(self): #vers 1
        """Add new model"""
        if self.col_file:
            from components.col_core_classes import COLModel
            new_model = COLModel()
            new_model.name = f"Model_{len(self.col_file.models) + 1}"
            new_model.model_id = len(self.col_file.models)
            self.col_file.models.append(new_model)
            self.refresh_model_list()
            img_debugger.debug(f"Added new COL model: {new_model.name}")
    
    def delete_model(self): #vers 1
        """Delete selected model"""
        current_row = self.models_list.currentRow()
        if current_row >= 0 and self.col_file and current_row < len(self.col_file.models):
            model_name = self.col_file.models[current_row].name
            del self.col_file.models[current_row]
            self.refresh_model_list()
            img_debugger.debug(f"Deleted COL model: {model_name}")

class COLEditorDialog(QDialog):
    """Main COL editor dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("COL Editor")
        self.setModal(True)
        self.resize(1200, 800)
        
        self.col_file = None
        self.file_path = None
        self.is_modified = False
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self): #vers 1
        """Setup editor UI"""
        layout = QVBoxLayout(self)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - model list
        self.model_list_widget = COLModelListWidget()
        main_splitter.addWidget(self.model_list_widget)
        
        # Center panel - 3D viewer
        viewer_group = QGroupBox("3D Viewer")
        viewer_layout = QVBoxLayout(viewer_group)
        
        # View options
        options_layout = QHBoxLayout()
        self.show_spheres_cb = QCheckBox("Spheres")
        self.show_spheres_cb.setChecked(True)
        options_layout.addWidget(self.show_spheres_cb)
        
        self.show_boxes_cb = QCheckBox("Boxes")
        self.show_boxes_cb.setChecked(True)
        options_layout.addWidget(self.show_boxes_cb)
        
        self.show_mesh_cb = QCheckBox("Mesh")
        self.show_mesh_cb.setChecked(True)
        options_layout.addWidget(self.show_mesh_cb)
        
        self.wireframe_cb = QCheckBox("Wireframe")
        options_layout.addWidget(self.wireframe_cb)
        
        options_layout.addStretch()
        viewer_layout.addLayout(options_layout)
        
        # 3D viewer
        self.viewer_3d = COLViewer3D()
        viewer_layout.addWidget(self.viewer_3d)
        
        main_splitter.addWidget(viewer_group)
        
        # Right panel - properties
        self.properties_widget = COLPropertiesWidget()
        main_splitter.addWidget(self.properties_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([250, 500, 300])
        
        layout.addWidget(main_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self): #vers 1
        """Create menu bar"""
        # Note: In a dialog, we create our own menu bar
        self.menu_bar = QMenuBar(self)
        
        # File menu
        file_menu = self.menu_bar.addMenu("File")
        
        open_action = QAction("Open COL...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_col_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_col_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_col_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Model...", self)
        export_action.triggered.connect(self.export_model)
        file_menu.addAction(export_action)
        
        import_action = QAction("Import Elements...", self)
        import_action.triggered.connect(self.import_elements)
        file_menu.addAction(import_action)
    
    def create_toolbar(self): #vers 1
        """Create toolbar"""
        self.toolbar = QToolBar(self)
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_col_file)
        self.toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_col_file)
        self.toolbar.addWidget(save_btn)
        
        self.toolbar.addSeparator()
        
        new_model_btn = QPushButton("New Model")
        new_model_btn.clicked.connect(self.create_new_model)
        self.toolbar.addWidget(new_model_btn)
    
    def setup_connections(self): #vers 1
        """Setup signal connections"""
        self.model_list_widget.model_selected.connect(self.on_model_selected)
        self.model_list_widget.element_selected.connect(self.on_element_selected)
        
        # View options
        self.show_spheres_cb.toggled.connect(self.update_view_options)
        self.show_boxes_cb.toggled.connect(self.update_view_options)
        self.show_mesh_cb.toggled.connect(self.update_view_options)
        self.wireframe_cb.toggled.connect(self.update_view_options)
    
    def load_col_file(self, file_path: str = None): #vers 1
        """Load COL file"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
            )
        
        if file_path and os.path.exists(file_path):
            try:
                self.col_file = COLFile(file_path)
                if self.col_file.load():
                    self.file_path = file_path
                    self.model_list_widget.set_col_file(self.col_file)
                    self.setWindowTitle(f"COL Editor - {os.path.basename(file_path)}")
                    self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
                    self.is_modified = False
                    img_debugger.success(f"COL file loaded in editor: {file_path}")
                    return True
                else:
                    error_msg = self.col_file.load_error or "Unknown error"
                    QMessageBox.critical(self, "Load Error", f"Failed to load COL file:\n{error_msg}")
                    img_debugger.error(f"Failed to load COL in editor: {error_msg}")
                    return False
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading COL file:\n{str(e)}")
                img_debugger.error(f"Exception loading COL in editor: {e}")
                return False
        
        return False
    
    def open_col_file(self): #vers 1
        """Open COL file dialog"""
        self.load_col_file()
    
    def save_col_file(self): #vers 1
        """Save current COL file"""
        if self.file_path and self.col_file:
            # COL file saving not yet implemented
            QMessageBox.information(self, "Save", "COL file saving will be implemented soon.")
            self.status_bar.showMessage("Save functionality coming soon")
        else:
            self.save_col_file_as()
    
    def save_col_file_as(self): #vers 1
        """Save COL file with new name"""
        if not self.col_file:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(self, "Save As", "COL file saving will be implemented soon.")
    
    def create_new_model(self): #vers 1
        """Create new COL model"""
        if not self.col_file:
            # Create new COL file
            self.col_file = COLFile()
            self.col_file.models = []
            self.model_list_widget.set_col_file(self.col_file)
        
        self.model_list_widget.add_model()
        self.is_modified = True
    
    def delete_model(self): #vers 1
        """Delete selected model"""
        self.model_list_widget.delete_model()
        self.is_modified = True
    
    def export_model(self): #vers 1
        """Export current model"""
        QMessageBox.information(self, "Export", "Model export functionality coming soon!")
    
    def import_elements(self): #vers 1
        """Import collision elements"""
        QMessageBox.information(self, "Import", "Import functionality coming soon!")
    
    def on_model_selected(self, model: COLModel): #vers 1
        """Handle model selection"""
        self.properties_widget.set_model(model)
        self.viewer_3d.set_current_model(model)
        self.status_bar.showMessage(f"Selected model: {model.name}")
    
    def on_element_selected(self, element_type: str, element_index: int): #vers 1
        """Handle element selection"""
        self.properties_widget.set_element(element_type, element_index)
        self.status_bar.showMessage(f"Selected {element_type} #{element_index}")
    
    def update_view_options(self): #vers 1
        """Update 3D view options"""
        self.viewer_3d.show_spheres = self.show_spheres_cb.isChecked()
        self.viewer_3d.show_boxes = self.show_boxes_cb.isChecked()
        self.viewer_3d.show_mesh = self.show_mesh_cb.isChecked()
        self.viewer_3d.show_wireframe = self.wireframe_cb.isChecked()
    
    def apply_changes(self): #vers 1
        """Apply all pending changes"""
        if self.col_file:
            # Recalculate bounding boxes and update flags
            for model in self.col_file.models:
                model.calculate_bounding_box()
                model.update_flags()
            
            self.is_modified = True
            self.status_bar.showMessage("Changes applied")
            img_debugger.debug("COL editor changes applied")

# Convenience function for integration with main IMG Factory
def open_col_editor(parent=None, col_file_path: str = None): #vers 1
    """Open COL editor dialog"""
    try:
        img_debugger.debug("Opening COL editor dialog")
        
        editor = COLEditorDialog(parent)
        
        if col_file_path:
            editor.load_col_file(col_file_path)
        
        result = editor.exec()
        
        if result:
            img_debugger.success("COL editor completed successfully")
        else:
            img_debugger.debug("COL editor cancelled")
        
        return result == QDialog.DialogCode.Accepted
        
    except Exception as e:
        img_debugger.error(f"Error opening COL editor: {e}")
        if parent:
            QMessageBox.critical(parent, "Error", f"Failed to open COL editor:\n{str(e)}")
        return False