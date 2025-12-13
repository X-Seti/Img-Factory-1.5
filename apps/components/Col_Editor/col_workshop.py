#!/usr/bin/env python3
#this belongs in components.Col_Editor.col_workshop.py - Version: 12
# X-Seti - August10 2025 - Converted col editor using gui base template.

"""
components/Col_Editor/col_workshop.py
COL Editor - Main collision editor interface
"""

import os
# Force X11/GLX backend for NVIDIA on Wayland
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QSG_RHI_BACKEND'] = 'opengl'
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '0'  # Use hardware acceleration

import tempfile
import subprocess
import shutil
import struct
import sys
import io
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# Add project root to path for standalone mode
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import PyQt6
from PyQt6.QtWidgets import (QApplication, QSlider, QCheckBox,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QDialog, QFormLayout, QSpinBox,  QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit, QTextEdit, QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QColorDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog, QTabWidget, QDoubleSpinBox, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect, QByteArray
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QPen, QBrush, QColor, QCursor
from PyQt6.QtSvg import QSvgRenderer

# Import project modules AFTER path setup
from apps.debug.debug_functions import img_debugger
from apps.methods.col_core_classes import COLFile, COLModel, COLVersion, Vector3
from depends.svg_icon_factory import SVGIconFactory
#from apps.methods.col_integration import get_col_detailed_analysis, create_temporary_col_file, cleanup_temporary_file
from apps.gui.col_dialogs import show_col_analysis_dialog

# Import COL viewport and preview from depends
try:
    from apps.components.Col_Editor.depends.col_3d_viewport import COL3DViewport
    from apps.components.Col_Editor.depends.col_preview_generator import (
        COLPreviewGenerator, create_col_preview, create_col_thumbnail
    )
    VIEWPORT_AVAILABLE = True
except ImportError:
    VIEWPORT_AVAILABLE = False
    COL3DViewport = None
    print("Warning: COL 3D viewport not available - install PyOpenGL")

# Add root directory to path
App_name = "Col Workshop"
DEBUG_STANDALONE = False

# Use new 3D viewport if available, fallback to text display
if VIEWPORT_AVAILABLE:
    ViewportWidget = COL3DViewport
else:
    ViewportWidget = QLabel  # Fallback text display


# Import AppSettings
try:
    from apps.utils.app_settings_system import AppSettings, SettingsDialog
    APPSETTINGS_AVAILABLE = True
except ImportError:
    APPSETTINGS_AVAILABLE = False
    print("Warning: AppSettings not available")

##class COLModelListWidget: -
# __init__
# on_selection_changed
# populate_models
# set_col_file
# show_context_menu

##class COLPropertiesWidget: -
# __init__
# add_box
# add_sphere
# clear_properties
# export_mesh
# import_mesh
# on_version_changed
# remove_box
# remove_sphere
# set_current_model
# setup_boxes_tab
# setup_mesh_tab
# setup_model_tab
# setup_spheres_tab
# setup_tabs
# update_boxes_table
# update_mesh_info
# update_properties
# update_spheres_table

##class COLWorkshop: -
# __init__
# _apply_always_on_top
# _apply_button_mode
# _apply_window_flags
# _create_info_panel
# _create_left_panel
# _create_preview_controls
# _create_preview_widget
# _create_right_panel
# _create_transform_panel
# _dock_to_main
# _enable_name_edit
# _ensure_depends_structure
# _extract_entry_data
# _generate_thumbnail
# _load_settings
# _on_collision_selected
# _populate_collision_list
# _render_collision_preview
# _save_settings
# _save_surface_name
# _show_col_info
# _toggle_boxes
# _toggle_mesh
# _toggle_spheres
# _undock_from_main
# _update_dock_button_visibility
# load_from_img_archive
# open_col_file
# save_col_file
# show_settings_dialog
# toggle_dock_mode
# update_display

##class ZoomablePreview: -
# __init__
# _update_scaled_pixmap
# fit_to_window
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# pan
# render_collision
# rotate_x
# rotate_y
# rotate_z
# set_model
# setPixmap
# wheelEvent
# zoom_in
# zoom_out

##class COLEditorDialog: -
# __init__
# analyze_file
# closeEvent
# connect_signals
# load_col_file
# on_model_selected
# on_property_changed
# open_file
# save_file
# save_file_as
# setup_ui

##Module-level functions -
# apply_changes
# create_new_model
# delete_model
# export_model
# import_elements
# open_col_editor
# open_workshop
# refresh_model_list
# update_view_options


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
        self.addTab(self.model_tab, "  Model")

        # Spheres tab
        self.spheres_tab = QWidget()
        self.setup_spheres_tab()
        self.addTab(self.spheres_tab, "🔵 Spheres")

        # Boxes tab
        self.boxes_tab = QWidget()
        self.setup_boxes_tab()
        self.addTab(self.boxes_tab, "  Boxes")

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

        self.import_mesh_btn = QPushButton("Import Mesh")
        self.import_mesh_btn.clicked.connect(self.import_mesh)
        mesh_buttons.addWidget(self.import_mesh_btn)

        self.export_mesh_btn = QPushButton("Export Mesh")
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


class COLWorkshop(QWidget): #vers 3
    """COL Workshop - Main window"""

    workshop_closed = pyqtSignal()
    window_closed = pyqtSignal()

    def __init__(self, parent=None, main_window=None): #vers 10
        """initialize_features"""
        if DEBUG_STANDALONE and main_window is None:
            print(App_name + " Initializing ...")

        super().__init__(parent)

        self.main_window = main_window

        self.undo_stack = []
        self.button_display_mode = 'both'
        self.last_save_directory = None

        # Set default fonts
        from PyQt6.QtGui import QFont
        default_font = QFont("Fira Sans Condensed", 14)
        self.setFont(default_font)
        self.title_font = QFont("Arial", 14)
        self.panel_font = QFont("Arial", 10)
        self.button_font = QFont("Arial", 10)
        self.infobar_font = QFont("Courier New", 9)
        self.standalone_mode = (main_window is None)

        # Get app_settings from main_window if available
        if main_window and hasattr(main_window, 'app_settings'):
            self.app_settings = main_window.app_settings
        else:
            self.app_settings = None

        # Preview settings
        self._show_checkerboard = True
        self._show_spheres = True
        self._show_boxes = True
        self._show_mesh = True

        self._checkerboard_size = 16
        self._overlay_opacity = 50
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.background_color = QColor(42, 42, 42)
        self.background_mode = 'solid'
        self.placeholder_text = "No Surface"
        self.setMinimumSize(200, 200)
        preview_widget = False

        # Docking state
        self.is_docked = (main_window is not None)
        self.dock_widget = None
        self.is_overlay = False
        self.overlay_table = None
        self.overlay_tab_index = -1

        self.setWindowTitle(App_name + ": No File")
        self.resize(1400, 800)
        self.use_system_titlebar = False
        self.window_always_on_top = False

        # Window flags
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._initialize_features()

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        if parent:
            parent_pos = parent.pos()
            self.move(parent_pos.x() + 50, parent_pos.y() + 80)

        if self.standalone_mode:
            self._ensure_depends_structure()

        # Setup UI FIRST
        self.setup_ui()

        # Setup hotkeys
        self._setup_hotkeys()

        # Apply theme ONCE at the end
        self._apply_theme()

        if hasattr(self, '_update_dock_button_visibility'):
            self._update_dock_button_visibility()

        if self.main_window and hasattr(self.main_window, 'app_settings'):
            self.update()  # Force widget repaint

        # Enable mouse tracking
        self.setMouseTracking(True)

        if DEBUG_STANDALONE and self.standalone_mode:
            print(App_name + " initialized")


    def setup_ui(self): #vers 7
        """Setup the main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # Tab bar for multiple col files
        self.col_tabs = QTabWidget()
        self.col_tabs.setTabsClosable(True)
        #self.col_tabs.tabCloseRequested.connect(self._close_col_tab)


        # Create initial tab with main content
        initial_tab = QWidget()
        tab_layout = QVBoxLayout(initial_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)


        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create all panels first
        left_panel = self._create_left_panel()
        middle_panel = self._create_middle_panel()
        right_panel = self._create_right_panel()

        # Add panels to splitter based on mode
        if left_panel is not None:  # IMG Factory mode
            main_splitter.addWidget(left_panel)
            main_splitter.addWidget(middle_panel)
            main_splitter.addWidget(right_panel)
            # Set proportions (2:3:5)
            main_splitter.setStretchFactor(0, 2)
            main_splitter.setStretchFactor(1, 3)
            main_splitter.setStretchFactor(2, 5)
        else:  # Standalone mode
            main_splitter.addWidget(middle_panel)
            main_splitter.addWidget(right_panel)
            # Set proportions (1:1)
            main_splitter.setStretchFactor(0, 1)
            main_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(main_splitter)

        # Status indicators if available
        if hasattr(self, '_setup_status_indicators'):
            status_frame = self._setup_status_indicators()
            main_layout.addWidget(status_frame)


    def _enable_name_edit(self, event, is_alpha): #vers 1
        """Enable name editing on click"""
        self.info_name.setReadOnly(False)
        self.info_name.selectAll()
        self.info_name.setFocus()


    def _update_status_indicators(self): #vers 2
        """Update status indicators"""
        if hasattr(self, 'status_collision'):
            self.status_textures.setText(f"collision: {len(self.collision_list)}")

        if hasattr(self, 'status_selected'):
            if self.selected_texture:
                name = self.selected_collision.get('name', 'Unknown')
                self.status_selected.setText(f"Selected: {name}")
            else:
                self.status_selected.setText("Selected: None")

        if hasattr(self, 'status_size'):
            if self.current_txd_data:
                size_kb = len(self.current_col_data) / 1024
                self.status_size.setText(f"COL Size: {size_kb:.1f} KB")
            else:
                self.status_size.setText("COL Size: Unknown")

        if hasattr(self, 'status_modified'):
            if self.windowTitle().endswith("*"):
                self.status_modified.setText("MODIFIED")
                self.status_modified.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.status_modified.setText("")
                self.status_modified.setStyleSheet("")


    def select_col_by_name(self, col_name): #vers 1
        """Select a specific COL model by name in the list"""
        try:
            if not hasattr(self, 'model_list'):
                return False

            # Search through model list for matching name
            for i in range(self.model_list.count()):
                item = self.model_list.item(i)
                item_text = item.text()
                # Extract model name from display text (format: "name (version - stats)")
                if item_text.startswith(col_name):
                    self.model_list.setCurrentRow(i)
                    img_debugger.success(f"Auto-selected COL: {col_name}")
                    return True

            img_debugger.warning(f"COL not found in list: {col_name}")
            return False

        except Exception as e:
            img_debugger.error(f"Error selecting COL by name: {str(e)}")
            return False


# - Panel Creation

    def _create_status_bar(self): #vers 1
        """Create bottom status bar - single line compact"""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        status_bar.setFixedHeight(22)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(15)

        # Left: Ready
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        if hasattr(self, 'status_info'):
            size_kb = len(col_data) / 1024
            tex_count = len(self.collision_list)
            #self.status_col_info.setText(f"Collision: {tex_count} | col: {size_kb:.1f} KB")

        return status_bar


# - Settings Reusable

    def _show_workshop_settings(self): #vers 1
        """Show complete workshop settings dialog"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                                    QTabWidget, QWidget, QGroupBox, QFormLayout,
                                    QSpinBox, QComboBox, QSlider, QLabel, QCheckBox,
                                    QFontComboBox)
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle(App_name + "Settings")
        dialog.setMinimumWidth(650)
        dialog.setMinimumHeight(550)

        layout = QVBoxLayout(dialog)

        # Create tabs
        tabs = QTabWidget()

        # TAB 1: FONTS (FIRST TAB)

        fonts_tab = QWidget()
        fonts_layout = QVBoxLayout(fonts_tab)

        # Default Font
        default_font_group = QGroupBox("Default Font")
        default_font_layout = QHBoxLayout()

        default_font_combo = QFontComboBox()
        default_font_combo.setCurrentFont(self.font())
        default_font_layout.addWidget(default_font_combo)

        default_font_size = QSpinBox()
        default_font_size.setRange(8, 24)
        default_font_size.setValue(self.font().pointSize())
        default_font_size.setSuffix(" pt")
        default_font_size.setFixedWidth(80)
        default_font_layout.addWidget(default_font_size)

        default_font_group.setLayout(default_font_layout)
        fonts_layout.addWidget(default_font_group)

        # Title Font
        title_font_group = QGroupBox("Title Font")
        title_font_layout = QHBoxLayout()

        title_font_combo = QFontComboBox()
        if hasattr(self, 'title_font'):
            title_font_combo.setCurrentFont(self.title_font)
        else:
            title_font_combo.setCurrentFont(QFont("Arial", 14))
        title_font_layout.addWidget(title_font_combo)

        title_font_size = QSpinBox()
        title_font_size.setRange(10, 32)
        title_font_size.setValue(getattr(self, 'title_font', QFont("Arial", 14)).pointSize())
        title_font_size.setSuffix(" pt")
        title_font_size.setFixedWidth(80)
        title_font_layout.addWidget(title_font_size)

        title_font_group.setLayout(title_font_layout)
        fonts_layout.addWidget(title_font_group)

        # Panel Font
        panel_font_group = QGroupBox("Panel Headers Font")
        panel_font_layout = QHBoxLayout()

        panel_font_combo = QFontComboBox()
        if hasattr(self, 'panel_font'):
            panel_font_combo.setCurrentFont(self.panel_font)
        else:
            panel_font_combo.setCurrentFont(QFont("Arial", 10))
        panel_font_layout.addWidget(panel_font_combo)

        panel_font_size = QSpinBox()
        panel_font_size.setRange(8, 18)
        panel_font_size.setValue(getattr(self, 'panel_font', QFont("Arial", 10)).pointSize())
        panel_font_size.setSuffix(" pt")
        panel_font_size.setFixedWidth(80)
        panel_font_layout.addWidget(panel_font_size)

        panel_font_group.setLayout(panel_font_layout)
        fonts_layout.addWidget(panel_font_group)

        # Button Font
        button_font_group = QGroupBox("Button Font")
        button_font_layout = QHBoxLayout()

        button_font_combo = QFontComboBox()
        if hasattr(self, 'button_font'):
            button_font_combo.setCurrentFont(self.button_font)
        else:
            button_font_combo.setCurrentFont(QFont("Arial", 10))
        button_font_layout.addWidget(button_font_combo)

        button_font_size = QSpinBox()
        button_font_size.setRange(8, 16)
        button_font_size.setValue(getattr(self, 'button_font', QFont("Arial", 10)).pointSize())
        button_font_size.setSuffix(" pt")
        button_font_size.setFixedWidth(80)
        button_font_layout.addWidget(button_font_size)

        button_font_group.setLayout(button_font_layout)
        fonts_layout.addWidget(button_font_group)

        # Info Bar Font
        infobar_font_group = QGroupBox("Info Bar Font")
        infobar_font_layout = QHBoxLayout()

        infobar_font_combo = QFontComboBox()
        if hasattr(self, 'infobar_font'):
            infobar_font_combo.setCurrentFont(self.infobar_font)
        else:
            infobar_font_combo.setCurrentFont(QFont("Courier New", 9))
        infobar_font_layout.addWidget(infobar_font_combo)

        infobar_font_size = QSpinBox()
        infobar_font_size.setRange(7, 14)
        infobar_font_size.setValue(getattr(self, 'infobar_font', QFont("Courier New", 9)).pointSize())
        infobar_font_size.setSuffix(" pt")
        infobar_font_size.setFixedWidth(80)
        infobar_font_layout.addWidget(infobar_font_size)

        infobar_font_group.setLayout(infobar_font_layout)
        fonts_layout.addWidget(infobar_font_group)

        fonts_layout.addStretch()
        tabs.addTab(fonts_tab, "Fonts")

        # TAB 2: DISPLAY SETTINGS

        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)

        # Button display mode
        button_group = QGroupBox("Button Display Mode")
        button_layout = QVBoxLayout()

        button_mode_combo = QComboBox()
        button_mode_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])
        current_mode = getattr(self, 'button_display_mode', 'both')
        mode_map = {'both': 0, 'icons': 1, 'text': 2}
        button_mode_combo.setCurrentIndex(mode_map.get(current_mode, 0))
        button_layout.addWidget(button_mode_combo)

        button_hint = QLabel("Changes how toolbar buttons are displayed")
        button_hint.setStyleSheet("color: #888; font-style: italic;")
        button_layout.addWidget(button_hint)

        button_group.setLayout(button_layout)
        display_layout.addWidget(button_group)

        # Table display
        table_group = QGroupBox("Surface List Display")
        table_layout = QVBoxLayout()

        show_thumbnails = QCheckBox("Show Surface types")
        show_thumbnails.setChecked(True)
        table_layout.addWidget(show_thumbnails)

        show_warnings = QCheckBox("Show warning icons for suspicious files")
        show_warnings.setChecked(True)
        show_warnings.setToolTip("Shows surface types")
        table_layout.addWidget(show_warnings)

        table_group.setLayout(table_layout)
        display_layout.addWidget(table_group)

        display_layout.addStretch()
        tabs.addTab(display_tab, "Display")


        # TAB 3: placeholder
        # TAB 4: PERFORMANCE

        perf_tab = QWidget()
        perf_layout = QVBoxLayout(perf_tab)

        perf_group = QGroupBox("Performance Settings")
        perf_form = QFormLayout()

        preview_quality = QComboBox()
        preview_quality.addItems(["Low (Fast)", "Medium", "High (Slow)"])
        preview_quality.setCurrentIndex(1)
        perf_form.addRow("Preview Quality:", preview_quality)

        thumb_size = QSpinBox()
        thumb_size.setRange(32, 128)
        thumb_size.setValue(64)
        thumb_size.setSuffix(" px")
        perf_form.addRow("Thumbnail Size:", thumb_size)

        perf_group.setLayout(perf_form)
        perf_layout.addWidget(perf_group)

        # Caching
        cache_group = QGroupBox("Caching")
        cache_layout = QVBoxLayout()

        enable_cache = QCheckBox("Enable surface preview caching")
        enable_cache.setChecked(True)
        cache_layout.addWidget(enable_cache)

        cache_hint = QLabel("Caching improves performance but uses more memory")
        cache_hint.setStyleSheet("color: #888; font-style: italic;")
        cache_layout.addWidget(cache_hint)

        cache_group.setLayout(cache_layout)
        perf_layout.addWidget(cache_group)

        perf_layout.addStretch()
        tabs.addTab(perf_tab, "Performance")

        # TAB 5: PREVIEW SETTINGS (LAST TAB)

        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        # Zoom Settings
        zoom_group = QGroupBox("Zoom Settings")
        zoom_form = QFormLayout()

        zoom_spin = QSpinBox()
        zoom_spin.setRange(10, 500)
        zoom_spin.setValue(int(getattr(self, 'zoom_level', 1.0) * 100))
        zoom_spin.setSuffix("%")
        zoom_form.addRow("Default Zoom:", zoom_spin)

        zoom_group.setLayout(zoom_form)
        preview_layout.addWidget(zoom_group)

        # Background Settings
        bg_group = QGroupBox("Background Settings")
        bg_layout = QVBoxLayout()

        # Background mode
        bg_mode_layout = QFormLayout()
        bg_mode_combo = QComboBox()
        bg_mode_combo.addItems(["Solid Color", "Checkerboard", "Grid"])
        current_bg_mode = getattr(self, 'background_mode', 'solid')
        mode_idx = {"solid": 0, "checkerboard": 1, "checker": 1, "grid": 2}.get(current_bg_mode, 0)
        bg_mode_combo.setCurrentIndex(mode_idx)
        bg_mode_layout.addRow("Background Mode:", bg_mode_combo)
        bg_layout.addLayout(bg_mode_layout)

        bg_layout.addSpacing(10)

        # Checkerboard size
        cb_label = QLabel("Checkerboard Size:")
        bg_layout.addWidget(cb_label)

        cb_layout = QHBoxLayout()
        cb_slider = QSlider(Qt.Orientation.Horizontal)
        cb_slider.setMinimum(4)
        cb_slider.setMaximum(64)
        cb_slider.setValue(getattr(self, '_checkerboard_size', 16))
        cb_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        cb_slider.setTickInterval(8)
        cb_layout.addWidget(cb_slider)

        cb_spin = QSpinBox()
        cb_spin.setMinimum(4)
        cb_spin.setMaximum(64)
        cb_spin.setValue(getattr(self, '_checkerboard_size', 16))
        cb_spin.setSuffix(" px")
        cb_spin.setFixedWidth(80)
        cb_layout.addWidget(cb_spin)

        bg_layout.addLayout(cb_layout)

        # Connect checkerboard controls
        #cb_slider.valueChanged.connect(cb_spin.setValue)
        #cb_spin.valueChanged.connect(cb_slider.setValue)

        # Hint
        cb_hint = QLabel("Smaller = tighter pattern, larger = bigger squares")
        cb_hint.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        bg_layout.addWidget(cb_hint)

        bg_group.setLayout(bg_layout)
        preview_layout.addWidget(bg_group)

        # Overlay Settings
        overlay_group = QGroupBox("Overlay View Settings")
        overlay_layout = QVBoxLayout()

        overlay_label = QLabel("Overlay Opacity (Wireframe over mesh):")
        overlay_layout.addWidget(overlay_label)

        opacity_layout = QHBoxLayout()
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(100)
        opacity_slider.setValue(getattr(self, '_overlay_opacity', 50))
        opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        opacity_slider.setTickInterval(10)
        opacity_layout.addWidget(opacity_slider)

        opacity_spin = QSpinBox()
        opacity_spin.setMinimum(0)
        opacity_spin.setMaximum(100)
        opacity_spin.setValue(getattr(self, '_overlay_opacity', 50))
        opacity_spin.setSuffix(" %")
        opacity_spin.setFixedWidth(80)
        opacity_layout.addWidget(opacity_spin)

        overlay_layout.addLayout(opacity_layout)

        # Connect opacity controls
        #opacity_slider.valueChanged.connect(opacity_spin.setValue)
        #opacity_spin.valueChanged.connect(opacity_slider.setValue)

        # Hint
        opacity_hint = QLabel("0")
        opacity_hint.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        overlay_layout.addWidget(opacity_hint)

        overlay_group.setLayout(overlay_layout)
        preview_layout.addWidget(overlay_group)

        preview_layout.addStretch()
        tabs.addTab(preview_tab, "Preview")

        # Add tabs to dialog
        layout.addWidget(tabs)

        # BUTTONS

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0078d4;
                color: white;
                padding: 10px 24px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1984d8;
            }
        """)


        def apply_settings():
            # Adjusted for COL Wireframe, Mesh
            self.setFont(QFont(default_font_combo.currentFont().family(),
                            default_font_size.value()))
            self.title_font = QFont(title_font_combo.currentFont().family(),
                                title_font_size.value())
            self.panel_font = QFont(panel_font_combo.currentFont().family(),
                                panel_font_size.value())
            self.button_font = QFont(button_font_combo.currentFont().family(),
                                    button_font_size.value())
            self.infobar_font = QFont(infobar_font_combo.currentFont().family(),
                                    infobar_font_size.value())

            # Apply fonts to UI
            self._apply_title_font()
            self._apply_panel_font()
            self._apply_button_font()
            self._apply_infobar_font()

            mode_map = {0: 'both', 1: 'icons', 2: 'text'}
            self.button_display_mode = mode_map[button_mode_combo.currentIndex()]

            # EXPORT
            self.default_export_format = self.format_combo.currentText()

            # PREVIEW
            self.zoom_level = zoom_spin.value() / 100.0

            bg_modes = ['solid', 'checkerboard', 'grid']
            self.background_mode = bg_modes[bg_mode_combo.currentIndex()]

            self._checkerboard_size = cb_spin.value()
            self._overlay_opacity = opacity_spin.value()

            # Update preview widget
            if hasattr(self, 'preview_widget'):
                if self.background_mode == 'checkerboard':
                    self.preview_widget.set_checkerboard_background()
                    self.preview_widget._checkerboard_size = self._checkerboard_size
                else:
                    self.preview_widget.set_background_color(self.preview_widget.bg_color)

            # Apply button display mode
            if hasattr(self, '_update_all_buttons'):
                self._update_all_buttons()

            # Refresh display

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Workshop settings updated successfully")

        apply_btn.clicked.connect(apply_settings)
        btn_layout.addWidget(apply_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 10px 24px; font-size: 13px;")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Show dialog
        dialog.exec()


    def _apply_window_flags(self): #vers 1
        """Apply window flags based on settings"""
        # Save current geometry
        current_geometry = self.geometry()
        was_visible = self.isVisible()

        if self.use_system_titlebar:
            # Use system window with title bar
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
        else:
            # Use custom frameless window
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Restore geometry and visibility
        self.setGeometry(current_geometry)

        if was_visible:
            self.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            mode = "System title bar" if self.use_system_titlebar else "Custom frameless"
            self.main_window.log_message(f"Window mode: {mode}")


    def _apply_always_on_top(self): #vers 1
        """Apply always on top window flag"""
        current_flags = self.windowFlags()

        if self.window_always_on_top:
            new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
        else:
            new_flags = current_flags & ~Qt.WindowType.WindowStaysOnTopHint

        if new_flags != current_flags:
            # Save state
            current_geometry = self.geometry()
            was_visible = self.isVisible()

            self.setWindowFlags(new_flags)

            self.setGeometry(current_geometry)
            if was_visible:
                self.show()


    def _scan_available_locales(self): #vers 2
        """Scan locale folder and return list of available languages"""
        import os
        import configparser

        locales = []
        locale_path = os.path.join(os.path.dirname(__file__), 'locale')

        if not os.path.exists(locale_path):
            # Easter egg: Amiga Workbench 3.1 style error
            self._show_amiga_locale_error()
            # Return default English
            return [("English", "en", None)]

        try:
            for filename in os.listdir(locale_path):
                if filename.endswith('.lang'):
                    filepath = os.path.join(locale_path, filename)

                    try:
                        config = configparser.ConfigParser()
                        config.read(filepath, encoding='utf-8')

                        if 'Metadata' in config:
                            lang_name = config['Metadata'].get('LanguageName', 'Unknown')
                            lang_code = config['Metadata'].get('LanguageCode', 'unknown')
                            locales.append((lang_name, lang_code, filepath))

                    except Exception as e:
                        if self.main_window and hasattr(self.main_window, 'log_message'):
                            self.main_window.log_message(f"Failed to load locale {filename}: {e}")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Locale scan error: {e}")

        locales.sort(key=lambda x: x[0])

        if not locales:
            locales = [("English", "en", None)]

        return locales


    def _show_amiga_locale_error(self): #vers 2
        """Show Amiga Workbench 3.1 style error dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("Workbench Request")
        dialog.setFixedSize(450, 150)

        # Amiga Workbench styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #aaaaaa;
                border: 2px solid #ffffff;
            }
            QLabel {
                color: #000000;
                background-color: #aaaaaa;
            }
            QPushButton {
                background-color: #8899aa;
                color: #000000;
                border: 2px outset #ffffff;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:pressed {
                border: 2px inset #555555;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Amiga Topaz font style
        amiga_font = QFont("Courier", 10, QFont.Weight.Normal)

        # Error message
        message = QLabel("Workbench 3.1 installer\n\nPlease insert Local disk in any drive")
        message.setFont(amiga_font)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Retry and Cancel buttons (Amiga style)
        retry_btn = QPushButton("Retry")
        retry_btn.setFont(amiga_font)
        retry_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(retry_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(amiga_font)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()


# - Docking functions

    def _update_dock_button_visibility(self): #vers 2
        """Show/hide dock and tearoff buttons based on docked state"""
        if hasattr(self, 'dock_btn'):
            # Hide D button when docked, show when standalone
            self.dock_btn.setVisible(not self.is_docked)

        if hasattr(self, 'tearoff_btn'):
            # T button only visible when docked and not in standalone mode
            self.tearoff_btn.setVisible(self.is_docked and not self.standalone_mode)


    def toggle_dock_mode(self): #vers 2
        """Toggle between docked and standalone mode"""
        if self.is_docked:
            self._undock_from_main()
        else:
            self._dock_to_main()

        self._update_dock_button_visibility()


    def _dock_to_main(self): #vers 9
        """Dock handled by overlay system in imgfactory - IMPROVED"""
        try:
            if hasattr(self, 'is_overlay') and self.is_overlay:
                self.show()
                self.raise_()
                return

            # For proper docking, we need to be called from imgfactory
            # This method should be handled by imgfactory's overlay system
            if self.main_window and hasattr(self.main_window, App_name + '_docked'):
                # If available, use the main window's docking system
                self.main_window.open_col_workshop_docked()
            else:
                # Fallback: just show the window
                self.show()
                self.raise_()

            # Update dock state
            self.is_docked = True
            self._update_dock_button_visibility()

            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} docked to main window")


        except Exception as e:
            img_debugger.error(f"Error docking: {str(e)}")
            self.show()


    def _undock_from_main(self): #vers 4
        """Undock from overlay mode to standalone window - IMPROVED"""
        try:
            if hasattr(self, 'is_overlay') and self.is_overlay:
                # Switch from overlay to normal window
                self.setWindowFlags(Qt.WindowType.Window)
                self.is_overlay = False
                self.overlay_table = None

            # Set proper window flags for standalone mode
            self.setWindowFlags(Qt.WindowType.Window)
            
            # Ensure proper size when undocking
            if hasattr(self, 'original_size'):
                self.resize(self.original_size)
            else:
                self.resize(1000, 700)  # Reasonable default size
                
            self.is_docked = False
            self._update_dock_button_visibility()

            self.show()
            self.raise_()

            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} undocked to standalone")
                
        except Exception as e:
            img_debugger.error(f"Error undocking: {str(e)}")
            # Fallback
            self.setWindowFlags(Qt.WindowType.Window)
            self.show()


    def _apply_button_mode(self, dialog): #vers 1
        """Apply button display mode"""
        mode_index = self.button_mode_combo.currentIndex()
        mode_map = {0: 'both', 1: 'icons', 2: 'text'}

        new_mode = mode_map[mode_index]

        if new_mode != self.button_display_mode:
            self.button_display_mode = new_mode
            self._update_all_buttons()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                mode_names = {0: 'Icons + Text', 1: 'Icons Only', 2: 'Text Only'}
                self.main_window.log_message(f"✨ Button style: {mode_names[mode_index]}")

        dialog.close()


# - Window functionality

    def _initialize_features(self): #vers 3
        """Initialize all features after UI setup"""
        try:
            self._apply_theme()
            self._update_status_indicators()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("All features initialized")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Feature init error: {str(e)}")


    def _is_on_draggable_area(self, pos): #vers 7
        """Check if position is on draggable titlebar area

        Args:
            pos: Position in titlebar coordinates (from eventFilter)

        Returns:
            True if position is on titlebar but not on any button
        """
        if not hasattr(self, 'titlebar'):
            print("[DRAG] No titlebar attribute")
            return False

        # Verify pos is within titlebar bounds
        if not self.titlebar.rect().contains(pos):
            print(f"[DRAG] Position {pos} outside titlebar rect {self.titlebar.rect()}")
            return False

        # Check if clicking on any button - if so, NOT draggable
        for widget in self.titlebar.findChildren(QPushButton):
            if widget.isVisible():
                # Get button geometry in titlebar coordinates
                button_rect = widget.geometry()
                if button_rect.contains(pos):
                    print(f"[DRAG] Clicked on button: {widget.toolTip()}")
                    return False

        # Not on any button = draggable
        print(f"[DRAG] On draggable area at {pos}")
        return True


# - From the fixed gui - move, drag

    def _update_all_buttons(self): #vers 4
        """Update all buttons to match display mode"""
        buttons_to_update = [
            # Toolbar buttons
            ('open_btn', 'Open'),
            ('save_btn', 'Save'),
        ]


    def paintEvent(self, event): #vers 2
        """Paint corner resize triangles"""
        super().paintEvent(event)

        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors
        normal_color = QColor(100, 100, 100, 150)
        hover_color = QColor(150, 150, 255, 200)

        w = self.width()
        h = self.height()
        grip_size = 8  # Make corners visible (8x8px)
        size = self.corner_size

        # Define corner triangles
        corners = {
            'top-left': [(0, 0), (size, 0), (0, size)],
            'top-right': [(w, 0), (w-size, 0), (w, size)],
            'bottom-left': [(0, h), (size, h), (0, h-size)],
            'bottom-right': [(w, h), (w-size, h), (w, h-size)]
        }
        corners2 = {
            "top-left": [(0, grip_size), (0, 0), (grip_size, 0)],
            "top-right": [(w-grip_size, 0), (w, 0), (w, grip_size)],
            "bottom-left": [(0, h-grip_size), (0, h), (grip_size, h)],
            "bottom-right": [(w-grip_size, h), (w, h), (w, h-grip_size)]
        }

        # Get theme colors for corner indicators
        if self.app_settings:
            theme_colors = self._get_theme_colors("default")
            accent_color = QColor(theme_colors.get('accent_primary', '#1976d2'))
            accent_color.setAlpha(180)
        else:
            accent_color = QColor(100, 150, 255, 180)

        hover_color = QColor(accent_color)
        hover_color.setAlpha(255)

        # Draw all corners with hover effect
        for corner_name, points in corners.items():
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()

            # Use hover color if mouse is over this corner
            color = hover_color if self.hover_corner == corner_name else accent_color

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawPath(path)

        painter.end()


    def _get_resize_corner(self, pos): #vers 3
        """Determine which corner is under mouse position"""
        size = self.corner_size; w = self.width(); h = self.height()

        if pos.x() < size and pos.y() < size:
            return "top-left"
        if pos.x() > w - size and pos.y() < size:
            return "top-right"
        if pos.x() < size and pos.y() > h - size:
            return "bottom-left"
        if pos.x() > w - size and pos.y() > h - size:
            return "bottom-right"

        return None


    def mousePressEvent(self, event): #vers 8
        """Handle ALL mouse press - dragging and resizing"""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pos = event.pos()

        # Check corner resize FIRST
        self.resize_corner = self._get_resize_corner(pos)
        if self.resize_corner:
            self.resizing = True
            self.drag_position = event.globalPosition().toPoint()
            self.initial_geometry = self.geometry()
            event.accept()
            return

        # Check if on titlebar
        if hasattr(self, 'titlebar') and self.titlebar.geometry().contains(pos):
            titlebar_pos = self.titlebar.mapFromParent(pos)
            if self._is_on_draggable_area(titlebar_pos):
                self.windowHandle().startSystemMove()
                event.accept()
                return

        super().mousePressEvent(event)


    def mouseMoveEvent(self, event): #vers 4
        """Handle mouse move for resizing and hover effects

        Window dragging is handled by eventFilter to avoid conflicts
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing and self.resize_corner:
                self._handle_corner_resize(event.globalPosition().toPoint())
                event.accept()
                return
        else:
            # Update hover state and cursor
            corner = self._get_resize_corner(event.pos())
            if corner != self.hover_corner:
                self.hover_corner = corner
                self.update()  # Trigger repaint for hover effect
            self._update_cursor(corner)

        # Let parent handle everything else
        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event): #vers 2
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()


    def _handle_corner_resize(self, global_pos): #vers 2
        """Handle window resizing from corners"""
        if not self.resize_corner or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        # Calculate new geometry based on corner
        if self.resize_corner == "top-left":
            new_x = geometry.x() + delta.x()
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.resize_corner == "top-right":
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(geometry.x(), new_y, new_width, new_height)

        elif self.resize_corner == "bottom-left":
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, geometry.y(), new_width, new_height)

        elif self.resize_corner == "bottom-right":
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.resize(new_width, new_height)


    def _get_resize_direction(self, pos): #vers 1
        """Determine resize direction based on mouse position"""
        rect = self.rect()
        margin = self.resize_margin

        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin

        if left and top:
            return "top-left"
        elif right and top:
            return "top-right"
        elif left and bottom:
            return "bottom-left"
        elif right and bottom:
            return "bottom-right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"

        return None


    def _update_cursor(self, direction): #vers 1
        """Update cursor based on resize direction"""
        if direction == "top" or direction == "bottom":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif direction == "left" or direction == "right":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif direction == "top-left" or direction == "bottom-right":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def _handle_resize(self, global_pos): #vers 1
        """Handle window resizing"""
        if not self.resize_direction or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.frameGeometry()

        min_width = 800
        min_height = 600

        # Handle horizontal resizing
        if "left" in self.resize_direction:
            new_width = geometry.width() - delta.x()
            if new_width >= min_width:
                geometry.setLeft(geometry.left() + delta.x())
        elif "right" in self.resize_direction:
            new_width = geometry.width() + delta.x()
            if new_width >= min_width:
                geometry.setRight(geometry.right() + delta.x())

        # Handle vertical resizing
        if "top" in self.resize_direction:
            new_height = geometry.height() - delta.y()
            if new_height >= min_height:
                geometry.setTop(geometry.top() + delta.y())
        elif "bottom" in self.resize_direction:
            new_height = geometry.height() + delta.y()
            if new_height >= min_height:
                geometry.setBottom(geometry.bottom() + delta.y())

        self.setGeometry(geometry)
        self.drag_position = global_pos


    def resizeEvent(self, event): #vers 1
        '''Keep resize grip in bottom-right corner'''
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - 16, self.height() - 16)


    def mouseDoubleClickEvent(self, event): #vers 2
        """Handle double-click - maximize/restore

        Handled here instead of eventFilter for better control
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert to titlebar coordinates if needed
            if hasattr(self, 'titlebar'):
                titlebar_pos = self.titlebar.mapFromParent(event.pos())
                if self._is_on_draggable_area(titlebar_pos):
                    self._toggle_maximize()
                    event.accept()
                    return

        super().mouseDoubleClickEvent(event)

# - Marker 3

    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def closeEvent(self, event): #vers 1
        """Handle close event"""
        self.window_closed.emit()
        event.accept()


# - Panel Setup

    def _create_toolbar(self): #vers 13
        """Create toolbar - FIXED: Hide drag button when docked, ensure buttons visible"""
        self.titlebar = QFrame()
        self.titlebar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.titlebar.setFixedHeight(45)
        self.titlebar.setObjectName("titlebar")

        # Install event filter for drag detection
        self.titlebar.installEventFilter(self)
        self.titlebar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.titlebar.setMouseTracking(True)

        self.layout = QHBoxLayout(self.titlebar)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Get icon color from theme
        icon_color = self._get_icon_color()

        self.toolbar = QFrame()
        self.toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(self.toolbar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setFont(self.button_font)
        self.settings_btn.setIcon(self._create_settings_icon())
        self.settings_btn.setText("Settings")
        self.settings_btn.setIconSize(QSize(20, 20))
        self.settings_btn.clicked.connect(self._show_workshop_settings)
        self.settings_btn.setToolTip("Workshop Settings")
        layout.addWidget(self.settings_btn)

        layout.addStretch()

        # App title in center
        self.title_label = QLabel(App_name)
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        layout.addStretch()
        #layout.addStretch()

        # Only show "Open IMG" button if NOT standalone
        if not self.standalone_mode:
            self.open_img_btn = QPushButton("OpenIMG")
            self.open_img_btn.setFont(self.button_font)
            self.open_img_btn.setIcon(self._create_folder_icon())
            self.open_img_btn.setIconSize(QSize(20, 20))
            self.open_img_btn.clicked.connect(self.open_img_archive)
            layout.addWidget(self.open_img_btn)

        # Open button
        self.open_btn = QPushButton()
        self.open_btn.setFont(self.button_font)
        self.open_btn.setIcon(self._create_open_icon())
        self.open_btn.setText("Open")
        self.open_btn.setIconSize(QSize(20, 20))
        self.open_btn.setShortcut("Ctrl+O")
        if self.button_display_mode == 'icons':
            self.open_btn.setFixedSize(40, 40)
        self.open_btn.setToolTip("Open COL file (Ctrl+O)")
        self.open_btn.clicked.connect(self._open_file)
        layout.addWidget(self.open_btn)

        # Save button
        self.save_btn = QPushButton()
        self.save_btn.setFont(self.button_font)
        self.save_btn.setIcon(self._create_save_icon())
        self.save_btn.setText("Save")
        self.save_btn.setIconSize(QSize(20, 20))
        self.save_btn.setShortcut("Ctrl+S")
        if self.button_display_mode == 'icons':
            self.save_btn.setFixedSize(40, 40)
        self.save_btn.setEnabled(False)  # Enable when modified
        self.save_btn.setToolTip("Save COL file (Ctrl+S)")
        self.save_btn.clicked.connect(self._save_file)
        layout.addWidget(self.save_btn)

        # Save button
        self.saveall_btn = QPushButton()
        self.saveall_btn.setFont(self.button_font)
        self.saveall_btn.setIcon(self._create_saveas_icon())
        self.saveall_btn.setText("Save All")
        self.saveall_btn.setIconSize(QSize(20, 20))
        self.saveall_btn.setShortcut("Ctrl+S")
        if self.button_display_mode == 'icons':
            self.saveall_btn.setFixedSize(40, 40)
        self.saveall_btn.setEnabled(False)  # Enable when modified
        self.saveall_btn.setToolTip("Save COL file (Ctrl+S)")
        #self.saveall_btn.clicked.connect(self._saveall_file)
        #layout.addWidget(self.saveall_btn)

        self.export_all_btn = QPushButton("Extract")
        self.export_all_btn.setFont(self.button_font)
        self.export_all_btn.setIcon(self._create_package_icon())
        self.export_all_btn.setIconSize(QSize(20, 20))
        self.export_all_btn.setToolTip("Export all as col, cst or 3ds files")
        #self.export_all_btn.clicked.connect(self.export_all)
        self.export_all_btn.setEnabled(False)
        layout.addWidget(self.export_all_btn)

        self.undo_btn = QPushButton()
        self.undo_btn.setFont(self.button_font)
        self.undo_btn.setIcon(self._create_undo_icon())
        self.undo_btn.setText("Undo")
        self.undo_btn.setIconSize(QSize(20, 20))
        #self.undo_btn.clicked.connect(self._undo_last_action)
        self.undo_btn.setEnabled(False)
        self.undo_btn.setToolTip("Undo last change")
        layout.addWidget(self.undo_btn)

        # Info button
        self.info_btn = QPushButton("")
        self.info_btn.setText("")  # CHANGED from "Info"
        self.info_btn.setIcon(self._create_info_icon())
        self.info_btn.setMinimumWidth(40)
        self.info_btn.setMaximumWidth(40)
        self.info_btn.setMinimumHeight(30)
        self.info_btn.setToolTip("Information")
        self.info_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        self.info_btn.setIconSize(QSize(20, 20))
        self.info_btn.setFixedWidth(35)
        self.info_btn.clicked.connect(self._show_col_info)
        layout.addWidget(self.info_btn)

        # Properties/Theme button
        self.properties_btn = QPushButton()
        self.properties_btn.setFont(self.button_font)
        self.properties_btn.setIcon(SVGIconFactory.properties_icon(24, icon_color))
        self.properties_btn.setToolTip("Theme")
        self.properties_btn.setFixedSize(35, 35)
        self.properties_btn.clicked.connect(self._show_settings_dialog)
        self.properties_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.properties_btn.customContextMenuRequested.connect(self._show_settings_context_menu)
        layout.addWidget(self.properties_btn)

        # Dock button [D]
        self.dock_btn = QPushButton("D")
        #self.dock_btn.setFont(self.button_font)
        self.dock_btn.setMinimumWidth(40)
        self.dock_btn.setMaximumWidth(40)
        self.dock_btn.setMinimumHeight(30)
        self.dock_btn.setToolTip("Dock")
        self.dock_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        self.dock_btn.clicked.connect(self.toggle_dock_mode)
        layout.addWidget(self.dock_btn)

                # Tear-off button [T] - only in IMG Factory mode
        if not self.standalone_mode:
            self.tearoff_btn = QPushButton("T")
            #self.tearoff_btn.setFont(self.button_font)
            self.tearoff_btn.setMinimumWidth(40)
            self.tearoff_btn.setMaximumWidth(40)
            self.tearoff_btn.setMinimumHeight(30)
            self.tearoff_btn.clicked.connect(self._toggle_tearoff)
            self.tearoff_btn.setToolTip("TXD Workshop - Tearoff window")
            self.tearoff_btn.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    background-color: #4a4a4a;
                    border: 1px solid #5a5a5a;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            layout.addWidget(self.tearoff_btn)

        # Window controls
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(self._create_minimize_icon())
        self.minimize_btn.setIconSize(QSize(20, 20))
        self.minimize_btn.setMinimumWidth(40)
        self.minimize_btn.setMaximumWidth(40)
        self.minimize_btn.setMinimumHeight(30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize Window") # click tab to restore
        layout.addWidget(self.minimize_btn)

        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(self._create_maximize_icon())
        self.maximize_btn.setIconSize(QSize(20, 20))
        self.maximize_btn.setMinimumWidth(40)
        self.maximize_btn.setMaximumWidth(40)
        self.maximize_btn.setMinimumHeight(30)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.maximize_btn.setToolTip("Maximize/Restore Window")
        layout.addWidget(self.maximize_btn)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(self._create_close_icon())
        self.close_btn.setIconSize(QSize(20, 20))
        self.close_btn.setMinimumWidth(40)
        self.close_btn.setMaximumWidth(40)
        self.close_btn.setMinimumHeight(30)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close Window") # closes tab
        layout.addWidget(self.close_btn)

        return self.toolbar


    def _create_transform_panel(self): #vers 11
        """Create transform panel with variable width - no headers"""
        self.transform_panel = QFrame()
        self.transform_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        self.transform_panel.setMinimumWidth(30)
        self.transform_panel.setMaximumWidth(200)
        if self.button_display_mode == 'icons':
            self.transform_panel.setMaximumWidth(40)
            self.transform_panel.setMinimumWidth(40)
            layout.addSpacing(5)

        layout = QVBoxLayout(self.transform_panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Flip Vertical
        self.flip_vert_btn = QPushButton()
        self.flip_vert_btn.setFont(self.button_font)
        self.flip_vert_btn.setIcon(self._create_flip_vert_icon())
        self.flip_vert_btn.setText("Flip Vertical")
        self.flip_vert_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.flip_vert_btn.setFixedSize(40, 40)
        #self.flip_vert_btn.clicked.connect(self._flip_vertical)
        self.flip_vert_btn.setEnabled(False)
        self.flip_vert_btn.setToolTip("Flip col vertically")
        layout.addWidget(self.flip_vert_btn)

        # Flip Horizontal
        self.flip_horz_btn = QPushButton()
        self.flip_horz_btn.setFont(self.button_font)
        self.flip_horz_btn.setIcon(self._create_flip_horz_icon())
        self.flip_horz_btn.setText("Flip Horizontal")
        self.flip_horz_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.flip_horz_btn.setFixedSize(40, 40)
        #self.flip_horz_btn.clicked.connect(self._flip_horizontal)
        self.flip_horz_btn.setEnabled(False)
        self.flip_horz_btn.setToolTip("Flip col horizontally")
        layout.addWidget(self.flip_horz_btn)

        layout.addSpacing(5)

        # Rotate Clockwise
        self.rotate_cw_btn = QPushButton()
        self.rotate_cw_btn.setFont(self.button_font)
        self.rotate_cw_btn.setIcon(self._create_rotate_cw_icon())
        self.rotate_cw_btn.setText("Rotate 90° CW")
        self.rotate_cw_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.rotate_cw_btn.setFixedSize(40, 40)
        #self.rotate_cw_btn.clicked.connect(self._rotate_clockwise)
        self.rotate_cw_btn.setEnabled(False)
        self.rotate_cw_btn.setToolTip("Rotate 90 degrees clockwise")
        layout.addWidget(self.rotate_cw_btn)

        # Rotate Counter-Clockwise
        self.rotate_ccw_btn = QPushButton()
        self.rotate_ccw_btn.setFont(self.button_font)
        self.rotate_ccw_btn.setIcon(self._create_rotate_ccw_icon())
        self.rotate_ccw_btn.setText("Rotate 90° CCW")
        self.rotate_ccw_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.rotate_ccw_btn.setFixedSize(40, 40)
        #self.rotate_ccw_btn.clicked.connect(self._rotate_counterclockwise)
        self.rotate_ccw_btn.setEnabled(False)
        self.rotate_ccw_btn.setToolTip("Rotate 90 degrees counter-clockwise")
        layout.addWidget(self.rotate_ccw_btn)

        layout.addSpacing(5)

        # Analyze button
        self.analyze_btn = QPushButton()
        self.analyze_btn.setFont(self.button_font)
        self.analyze_btn.setIcon(self._create_analyze_icon())
        self.analyze_btn.setText("Analyze")
        self.analyze_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.analyze_btn.setFixedSize(40, 40)
        self.analyze_btn.clicked.connect(self._analyze_collision)
        self.analyze_btn.setEnabled(False)  # Enable when COL loaded
        self.analyze_btn.setToolTip("Analyze collision data")
        layout.addWidget(self.analyze_btn)

        layout.addStretch()

        # Copy
        self.copy_btn = QPushButton()
        self.copy_btn.setFont(self.button_font)
        self.copy_btn.setIcon(self._create_copy_icon())
        self.copy_btn.setText("Copy")
        self.copy_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.copy_btn.setFixedSize(40, 40)
        #self.copy_btn.clicked.connect(self._copy_surface)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setToolTip("Copy col to clipboard")
        layout.addWidget(self.copy_btn)

        # Paste
        self.paste_btn = QPushButton()
        self.paste_btn.setFont(self.button_font)
        self.paste_btn.setIcon(self._create_paste_icon())
        self.paste_btn.setText("Paste")
        self.paste_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.paste_btn.setFixedSize(40, 40)
        #self.paste_btn.clicked.connect(self._paste_surface)
        self.paste_btn.setEnabled(False)
        self.paste_btn.setToolTip("Paste col from clipboard")
        layout.addWidget(self.paste_btn)

        # Create Collision
        self.create_surface_btn = QPushButton()
        self.create_surface_btn.setFont(self.button_font)
        self.create_surface_btn.setIcon(self._create_create_icon())
        self.create_surface_btn.setText("Create")
        self.create_surface_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.create_surface_btn.setFixedSize(40, 40)
        #self.create_surface_btn.clicked.connect(self._create_new_surface_entry)
        self.create_surface_btn.setToolTip("Create new blank Collision")
        layout.addWidget(self.create_surface_btn)

        # Delete collision
        self.delete_surface_btn = QPushButton()
        self.delete_surface_btn.setFont(self.button_font)
        self.delete_surface_btn.setIcon(self._create_delete_icon())
        self.delete_surface_btn.setText("Delete")
        self.delete_surface_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.delete_surface_btn.setFixedSize(40, 40)
        #self.delete_surface_btn.clicked.connect(self._delete_surface)
        self.delete_surface_btn.setEnabled(False)
        self.delete_surface_btn.setToolTip("Remove selected Collision")
        layout.addWidget(self.delete_surface_btn)

        # Duplicate Collision
        self.duplicate_surface_btn = QPushButton()
        self.duplicate_surface_btn.setFont(self.button_font)
        self.duplicate_surface_btn.setIcon(self._create_duplicate_icon())
        self.duplicate_surface_btn.setText("Duplicate")
        self.duplicate_surface_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.duplicate_surface_btn.setFixedSize(40, 40)
        #self.duplicate_surface_btn.clicked.connect(self._duplicate_surface)
        self.duplicate_surface_btn.setEnabled(False)
        self.duplicate_surface_btn.setToolTip("Clone selected Collision")
        layout.addWidget(self.duplicate_surface_btn)

        self.paint_btn = QPushButton()
        self.paint_btn.setFont(self.button_font)
        self.paint_btn.setIcon(self._create_paint_icon())
        self.paint_btn.setText("Paint")
        self.paint_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.paint_btn.setFixedSize(40, 40)
        #self.paint_btn.clicked.connect(self._open_paint_editor)
        self.paint_btn.setEnabled(False)
        self.paint_btn.setToolTip("Paint free hand on surface")
        layout.addWidget(self.paint_btn)

        layout.addSpacing(5)

        # Check col vs DFF
        self.surface_type_btn = QPushButton()
        self.surface_type_btn.setFont(self.button_font)
        self.surface_type_btn.setIcon(self._create_check_icon())
        self.surface_type_btn.setText("Surface type")
        self.surface_type_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.surface_type_btn.setFixedSize(40, 40)
        #self.surface_type_btn.clicked.connect(self._check_col_type)
        self.surface_type_btn.setToolTip("Surface types")
        layout.addWidget(self.surface_type_btn)

        # Check col vs DFF
        self.surface_edit_btn = QPushButton()
        self.surface_edit_btn.setFont(self.button_font)
        self.surface_edit_btn.setIcon(self._create_check_icon())
        self.surface_edit_btn.setText("Surface Edit")
        self.surface_edit_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.surface_edit_btn.setFixedSize(40, 40)
        #self.surface_type_btn.clicked.connect(self._col_edit)
        self.surface_edit_btn.setToolTip("Surface Editor")
        layout.addWidget(self.surface_edit_btn)

        self.build_from_txd_btn = QPushButton()
        self.build_from_txd_btn.setFont(self.button_font)
        self.build_from_txd_btn.setIcon(self._create_build_icon())
        self.build_from_txd_btn.setText("Build col via")
        self.build_from_txd_btn.setIconSize(QSize(20, 20))
        if self.button_display_mode == 'icons':
            self.build_from_txd_btn.setFixedSize(40, 40)
        #self.build_from_dff_btn.clicked.connect(self._build_col_from_dff)
        self.build_from_txd_btn.setToolTip("Create col surface from txd texture names")
        layout.addWidget(self.build_from_txd_btn)

        layout.addSpacing(5)

        layout.addStretch()

        return self.transform_panel


    def _create_left_panel(self): #vers 5
        """Create left panel - COL file list (only in IMG Factory mode)"""
        # In standalone mode, don't create this panel
        if self.standalone_mode:
            self.col_list_widget = None  # Explicitly set to None
            return None

        if not self.main_window:
            # Standalone mode - return None to hide this panel
            return None

        # Only create panel in IMG Factory mode
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("COL Files")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.col_list_widget = QListWidget()
        self.col_list_widget.setAlternatingRowColors(True)
        self.col_list_widget.itemClicked.connect(self._on_col_selected)
        layout.addWidget(self.col_list_widget)
        return panel


    def _create_middle_panel(self): #vers 3
        """Create middle panel with COL models table - matches TXD Workshop layout"""
        panel = QGroupBox("COL Models")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #3a3a3a;
                border-radius: 1px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 20px;
                padding: 0 5px;
                color: #e0e0e0;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setSpacing(5)

        # Model table widget (like TXD Workshop texture_table)
        self.collision_list = QTableWidget()
        self.collision_list.setColumnCount(2)
        self.collision_list.setHorizontalHeaderLabels(["Preview", "Details"])
        self.collision_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.collision_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.collision_list.setAlternatingRowColors(True)
        self.collision_list.itemSelectionChanged.connect(self._on_collision_selected)
        self.collision_list.setIconSize(QSize(64, 64))
        self.collision_list.setColumnWidth(0, 80)  # Thumbnail column
        self.collision_list.horizontalHeader().setStretchLastSection(True)  # Details column stretches
        layout.addWidget(self.collision_list)
        self.collision_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.collision_list.customContextMenuRequested.connect(self._show_collision_context_menu)
        return panel


    def _create_right_panel(self): #vers 10
        """Create right panel with editing controls - compact layout"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)
        has_bumpmap = False
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(5, 5, 5, 5)
        top_layout = QHBoxLayout()

        # Transform panel (left)
        transform_panel = self._create_transform_panel()
        top_layout.addWidget(transform_panel, stretch=1)

        # Preview area (center) - 3D Viewport
        self.preview_widget = COL3DViewport()
        top_layout.addWidget(self.preview_widget, stretch=2)

        # Preview controls (right side, vertical)
        self.preview_controls = self._create_preview_controls()
        top_layout.addWidget(self.preview_controls, stretch=0)
        main_layout.addLayout(top_layout, stretch=1)

        # Information group below
        info_group = QGroupBox("")
        info_group.setFont(self.title_font)
        info_layout = QVBoxLayout(info_group)
        info_group.setMaximumHeight(140)

        # === LINE 1: collision name ===
        name_layout = QHBoxLayout()
        name_label = QLabel("COL Name:")
        name_label.setFont(self.panel_font)
        name_layout.addWidget(name_label)

        self.info_name = QLineEdit()
        self.info_name.setText("Click to edit...")
        self.info_name.setFont(self.panel_font)
        self.info_name.setReadOnly(True)
        self.info_name.setStyleSheet("padding: px; border: 1px solid #3a3a3a;")
        #self.info_name.returnPressed.connect(self._save_surface_name)
        #self.info_name.editingFinished.connect(self._save_surface_name)
        self.info_name.mousePressEvent = lambda e: self._enable_name_edit(e, False)
        name_layout.addWidget(self.info_name, stretch=1)
        info_layout.addLayout(name_layout)

        # === LINES 2 & 3: Adaptive based on display mode ===
        if self.button_display_mode == 'icons':
            # MERGED: Single compact line for icon mode
            merged_line = self._create_merged_icons_line()
            info_layout.addLayout(merged_line)
        else:
            # SEPARATE: Original two-line layout for text/both modes
            # Line 2: Format controls
            format_layout = QHBoxLayout()
            format_layout.setSpacing(5)

            self.format_combo = QComboBox()
            self.format_combo.setFont(self.panel_font)
            self.format_combo.addItems(["COL", "COL2", "COL3", "COL4"])
            #self.format_combo.currentTextChanged.connect(self._change_format)
            self.format_combo.setEnabled(False)
            self.format_combo.setMaximumWidth(100)
            format_layout.addWidget(self.format_combo)

            format_layout.addStretch()

            # Switch button
            self.switch_btn = QPushButton("Mesh")
            self.switch_btn.setFont(self.button_font)
            self.switch_btn.setIcon(self._create_flip_vert_icon())
            self.switch_btn.setIconSize(QSize(20, 20))
            #self.switch_btn.clicked.connect(self.switch_surface_view)
            self.switch_btn.setEnabled(False)
            self.switch_btn.setToolTip("Cycle: Wireframe → Mesh → Painted → Overlay")
            format_layout.addWidget(self.switch_btn)

            # Convert
            self.convert_btn = QPushButton("Convert")
            self.convert_btn.setFont(self.button_font)
            self.convert_btn.setIcon(self._create_convert_icon())
            self.convert_btn.setIconSize(QSize(20, 20))
            self.convert_btn.setToolTip("Convert Collision format")
            #self.convert_btn.clicked.connect(self._convert_surface)
            self.convert_btn.setEnabled(False)
            format_layout.addWidget(self.convert_btn)

            # Line 3: shadow + Bumpmaps
            mipbump_layout = QHBoxLayout()
            mipbump_layout.setSpacing(5)

            self.info_format = QLabel("Shadow Mesh: ")
            self.info_format.setFont(self.panel_font)
            self.info_format.setMinimumWidth(100)
            mipbump_layout.addWidget(self.info_format)

            self.show_shadow_btn = QPushButton("View")
            self.show_shadow_btn.setFont(self.button_font)
            self.show_shadow_btn.setIcon(self._create_view_icon())
            self.show_shadow_btn.setIconSize(QSize(20, 20))
            self.show_shadow_btn.setToolTip("View all levels")
            #self.show_shadow_btn.clicked.connect(self._open_mipmap_manager)
            self.show_shadow_btn.setEnabled(False)
            mipbump_layout.addWidget(self.show_shadow_btn)

            self.create_shadow_btn = QPushButton("Create")
            self.create_shadow_btn.setFont(self.button_font)
            self.create_shadow_btn.setIcon(self._create_add_icon())
            self.create_shadow_btn.setIconSize(QSize(20, 20))
            self.create_shadow_btn.setToolTip("Generate Shadow Mesh")
            #self.create_shadow_btn.clicked.connect(self._create_shadow_dialog)
            self.create_shadow_btn.setEnabled(False)
            mipbump_layout.addWidget(self.create_shadow_btn)

            self.remove_shadow_btn = QPushButton("Remove")
            self.remove_shadow_btn.setFont(self.button_font)
            self.remove_shadow_btn.setIcon(self._create_delete_icon())
            self.remove_shadow_btn.setIconSize(QSize(20, 20))
            self.remove_shadow_btn.setToolTip("Remove Shodow Mesh")
            #self.remove_shadow_btn.clicked.connect(self._remove_shadow)
            self.remove_shadow_btn.setEnabled(False)
            mipbump_layout.addWidget(self.remove_shadow_btn)

            mipbump_layout.addSpacing(30)
            view_layout = QHBoxLayout()

            self.compress_btn = QPushButton("Compress")
            self.compress_btn.setFont(self.button_font)
            self.compress_btn.setIcon(self._create_compress_icon())
            self.compress_btn.setIconSize(QSize(20, 20))
            self.compress_btn.setToolTip("Compress Collision")
            #self.compress_btn.clicked.connect(self._compress_surface)
            self.compress_btn.setEnabled(False)
            format_layout.addWidget(self.compress_btn)

            self.uncompress_btn = QPushButton("Uncompress")
            self.uncompress_btn.setFont(self.button_font)
            self.uncompress_btn.setIcon(self._create_uncompress_icon())
            self.uncompress_btn.setIconSize(QSize(20, 20))
            self.uncompress_btn.setToolTip("Uncompress Collision")
            #self.uncompress_btn.clicked.connect(self._uncompress_surface)
            self.uncompress_btn.setEnabled(False)
            format_layout.addWidget(self.uncompress_btn)

            self.import_btn = QPushButton("Import")
            self.import_btn.setFont(self.button_font)
            self.import_btn.setIcon(self._create_import_icon())
            self.import_btn.setIconSize(QSize(20, 20))
            self.import_btn.setToolTip("Import col, cst, 3ds files")
            #self.import_btn.clicked.connect(self._import_selected)
            self.import_btn.setEnabled(False)
            format_layout.addWidget(self.import_btn)

            self.export_btn = QPushButton("Export")
            self.export_btn.setFont(self.button_font)
            self.export_btn.setIcon(self._create_export_icon())
            self.export_btn.setIconSize(QSize(20, 20))
            self.export_btn.setToolTip("Export col, cst, 3ds files")
            #self.export_btn.clicked.connect(self.export_selected)
            self.export_btn.setEnabled(False)
            format_layout.addWidget(self.export_btn)

            info_layout.addLayout(format_layout)
            info_layout.addLayout(view_layout)
            info_layout.addLayout(mipbump_layout)

        main_layout.addWidget(info_group, stretch=0)
        return panel


    def _create_preview_controls(self): #vers 5
        """Create preview control buttons - vertical layout on right"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_frame.setMaximumWidth(50)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(5)

        # Check if using 3D viewport or 2D preview
        is_3d_viewport = VIEWPORT_AVAILABLE and isinstance(self.preview_widget, COL3DViewport)

        # Zoom In
        zoom_in_btn = QPushButton()
        zoom_in_btn.setIcon(self._create_zoom_in_icon())
        zoom_in_btn.setIconSize(QSize(20, 20))
        zoom_in_btn.setFixedSize(40, 40)
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(self.preview_widget.zoom_in)
        controls_layout.addWidget(zoom_in_btn)

        # Zoom Out
        zoom_out_btn = QPushButton()
        zoom_out_btn.setIcon(self._create_zoom_out_icon())
        zoom_out_btn.setIconSize(QSize(20, 20))
        zoom_out_btn.setFixedSize(40, 40)
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(self.preview_widget.zoom_out)
        controls_layout.addWidget(zoom_out_btn)

        # Reset
        reset_btn = QPushButton()
        reset_btn.setIcon(self._create_reset_icon())
        reset_btn.setIconSize(QSize(20, 20))
        reset_btn.setFixedSize(40, 40)
        reset_btn.setToolTip("Reset View")
        reset_btn.clicked.connect(self.preview_widget.reset_view)
        controls_layout.addWidget(reset_btn)

        # Fit
        fit_btn = QPushButton()
        fit_btn.setIcon(self._create_fit_icon())
        fit_btn.setIconSize(QSize(20, 20))
        fit_btn.setFixedSize(40, 40)
        fit_btn.setToolTip("Fit to Window")
        fit_btn.clicked.connect(self.preview_widget.fit_to_window)
        controls_layout.addWidget(fit_btn)

        controls_layout.addSpacing(10)

        # Pan Up
        pan_up_btn = QPushButton()
        pan_up_btn.setIcon(self._create_arrow_up_icon())
        pan_up_btn.setIconSize(QSize(20, 20))
        pan_up_btn.setFixedSize(40, 40)
        pan_up_btn.setToolTip("Pan Up")
        pan_up_btn.clicked.connect(lambda: self._pan_preview(0, -20))
        controls_layout.addWidget(pan_up_btn)

        # Pan Down
        pan_down_btn = QPushButton()
        pan_down_btn.setIcon(self._create_arrow_down_icon())
        pan_down_btn.setIconSize(QSize(20, 20))
        pan_down_btn.setFixedSize(40, 40)
        pan_down_btn.setToolTip("Pan Down")
        pan_down_btn.clicked.connect(lambda: self._pan_preview(0, 20))
        controls_layout.addWidget(pan_down_btn)

        # Pan Left
        pan_left_btn = QPushButton()
        pan_left_btn.setIcon(self._create_arrow_left_icon())
        pan_left_btn.setIconSize(QSize(20, 20))
        pan_left_btn.setFixedSize(40, 40)
        pan_left_btn.setToolTip("Pan Left")
        pan_left_btn.clicked.connect(lambda: self._pan_preview(-20, 0))
        controls_layout.addWidget(pan_left_btn)

        # Pan Right
        pan_right_btn = QPushButton()
        pan_right_btn.setIcon(self._create_arrow_right_icon())
        pan_right_btn.setIconSize(QSize(20, 20))
        pan_right_btn.setFixedSize(40, 40)
        pan_right_btn.setToolTip("Pan Right")
        pan_right_btn.clicked.connect(lambda: self._pan_preview(20, 0))
        controls_layout.addWidget(pan_right_btn)

        # Color picker
        bg_custom_btn = QPushButton()
        bg_custom_btn.setIcon(self._create_color_picker_icon())
        bg_custom_btn.setIconSize(QSize(20, 20))
        bg_custom_btn.setFixedSize(40, 40)
        bg_custom_btn.setToolTip("Pick Background Color")
        bg_custom_btn.clicked.connect(self._pick_background_color)
        controls_layout.addWidget(bg_custom_btn)

        controls_layout.addSpacing(5)

        # View Spheres toggle
        self.view_spheres_btn = QPushButton()
        self.view_spheres_btn.setIcon(self._create_sphere_icon())
        self.view_spheres_btn.setIconSize(QSize(20, 20))
        self.view_spheres_btn.setFixedSize(40, 40)
        self.view_spheres_btn.setCheckable(True)
        self.view_spheres_btn.setChecked(True)
        self.view_spheres_btn.setToolTip("Toggle Spheres")
        self.view_spheres_btn.clicked.connect(self._toggle_spheres)
        controls_layout.addWidget(self.view_spheres_btn)

        # View Boxes toggle
        self.view_boxes_btn = QPushButton()
        self.view_boxes_btn.setIcon(self._create_box_icon())
        self.view_boxes_btn.setIconSize(QSize(20, 20))
        self.view_boxes_btn.setFixedSize(40, 40)
        self.view_boxes_btn.setCheckable(True)
        self.view_boxes_btn.setChecked(True)
        self.view_boxes_btn.setToolTip("Toggle Boxes")
        self.view_boxes_btn.clicked.connect(self._toggle_boxes)
        controls_layout.addWidget(self.view_boxes_btn)

        # View Mesh toggle
        self.view_mesh_btn = QPushButton()
        self.view_mesh_btn.setIcon(self._create_mesh_icon())
        self.view_mesh_btn.setIconSize(QSize(20, 20))
        self.view_mesh_btn.setFixedSize(40, 40)
        self.view_mesh_btn.setCheckable(True)
        self.view_mesh_btn.setChecked(True)
        self.view_mesh_btn.setToolTip("Toggle Mesh")
        self.view_mesh_btn.clicked.connect(self._toggle_mesh)
        controls_layout.addWidget(self.view_mesh_btn)
        controls_layout.addSpacing(5)

        return controls_frame


    def _update_toolbar_for_docking_state(self): #vers 1
        """Update toolbar visibility based on docking state"""
        # Hide/show drag button based on docking state
        if hasattr(self, 'drag_btn'):
            self.drag_btn.setVisible(not self.is_docked)


# - Rest of the logic for the panels

    def _apply_title_font(self): #vers 1
        """Apply title font to title bar labels"""
        if hasattr(self, 'title_font'):
            # Find all title labels
            for label in self.findChildren(QLabel):
                if label.objectName() == "title_label" or "🗺️" in label.text():
                    label.setFont(self.title_font)


    def _apply_panel_font(self): #vers 1
        """Apply panel font to info panels and labels"""
        if hasattr(self, 'panel_font'):
            # Apply to info labels (Mipmaps, Bumpmaps, status labels)
            for label in self.findChildren(QLabel):
                if any(x in label.text() for x in ["Mipmaps:", "Bumpmaps:", "Status:", "Type:", "Format:"]):
                    label.setFont(self.panel_font)


    def _apply_button_font(self): #vers 1
        """Apply button font to all buttons"""
        if hasattr(self, 'button_font'):
            for button in self.findChildren(QPushButton):
                button.setFont(self.button_font)


    def _apply_infobar_font(self): #vers 1
        """Apply fixed-width font to info bar at bottom"""
        if hasattr(self, 'infobar_font'):
            if hasattr(self, 'info_bar'):
                self.info_bar.setFont(self.infobar_font)


    def _load_img_col_list(self): #vers 2
        """Load COL files from IMG archive"""
        try:
            # Safety check for standalone mode
            if self.standalone_mode or not hasattr(self, 'col_list_widget') or self.col_list_widget is None:
                return

            self.col_list_widget.clear()
            self.col_list = []

            if not self.current_img:
                return

            for entry in self.current_img.entries:
                if entry.name.lower().endswith('.col'):
                    self.col_list.append(entry)
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry)
                    size_kb = entry.size / 1024
                    item.setToolTip(f"{entry.name}\nSize: {size_kb:.1f} KB")
                    self.col_list_widget.addItem(item)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Found {len(self.txd_list)} COL files")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error loading COL list: {str(e)}")


# - Rest of the logic for the panels

    def _pan_preview(self, dx, dy): #vers 2
        """Pan preview by dx, dy pixels - FIXED"""
        if hasattr(self, 'preview_widget') and self.preview_widget:
            self.preview_widget.pan(dx, dy)

    def _pick_background_color(self): #vers 1
        """Open color picker for background"""
        color = QColorDialog.getColor(self.preview_widget.bg_color, self, "Pick Background Color")
        if color.isValid():
            self.preview_widget.set_background_color(color)

    def _set_checkerboard_bg(self): #vers 1
        """Set checkerboard background"""
        # Create checkerboard pattern
        self.preview_widget.setStyleSheet("""
            border: 1px solid #3a3a3a;
            background-image:
                linear-gradient(45deg, #333 25%, transparent 25%),
                linear-gradient(-45deg, #333 25%, transparent 25%),
                linear-gradient(45deg, transparent 75%, #333 75%),
                linear-gradient(-45deg, transparent 75%, #333 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        """)


    def _create_level_card(self, level_data): #vers 2
        """Create modern level card matching mockup"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
            QFrame:hover {
                border-color: #4a6fa5;
                background: #252525;
            }
        """)
        card.setMinimumHeight(140)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Preview thumbnail
        preview_widget = self._create_preview_widget(level_data)
        layout.addWidget(preview_widget)

        # Level info section
        info_section = self._create_info_section(level_data)
        layout.addWidget(info_section, stretch=1)

        # Action buttons
        action_section = self._create_action_section(level_data)
        layout.addWidget(action_section)

        return card

    def _create_preview_widget(self, level_data=None): #vers 5
        """Create preview widget - CollisionPreviewWidget for col_workshop"""
        if level_data is None:
            # Return collision preview widget for main preview area
            preview = CollisionPreviewWidget(self)
            img_debugger.debug(f"Created CollisionPreviewWidget: {type(preview)}")  # ADD THIS
            return preview

        # Original logic with level_data for mipmap/level cards (if needed)
        level_num = level_data.get('level', 0)
        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        rgba_data = level_data.get('rgba_data')
        preview_size = max(45, 120 - (level_num * 15))

        preview = QLabel()
        preview.setFixedSize(preview_size, preview_size)
        preview.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 2px solid #3a3a3a;
                border-radius: 3px;
            }
        """)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if rgba_data and width > 0:
            try:
                image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    scaled_pixmap = pixmap.scaled(
                        preview_size - 10, preview_size - 10,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    preview.setPixmap(scaled_pixmap)
            except:
                preview.setText("No Data")
        else:
            preview.setText("No Data")

        return preview


    def _create_info_section(self, level_data): #vers 1
        """Create info section with stats grid"""
        info_widget = QWidget()
        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with level number and dimensions
        header_layout = QHBoxLayout()

        level_num = level_data.get('level', 0)
        level_badge = QLabel(f"Level {level_num}")
        level_badge.setStyleSheet("""
            QLabel {
                background: #0d47a1;
                color: white;
                padding: 4px 12px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        header_layout.addWidget(level_badge)

        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        dim_label = QLabel(f"{width} x {height}")
        dim_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4a9eff;")
        header_layout.addWidget(dim_label)

        # Main indicator
        if level_num == 0:
            main_badge = QLabel("Main Surface")
            main_badge.setStyleSheet("color: #4caf50; font-size: 12px;")
            header_layout.addWidget(main_badge)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Stats grid
        stats_grid = self._create_stats_grid(level_data)
        layout.addWidget(stats_grid)

        return info_widget


    def _create_stats_grid(self, level_data): #vers 1
        """Create stats grid"""
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)

        fmt = level_data.get('format', self.collision_data.get('format', 'Unknown'))
        size = level_data.get('compressed_size', 0)
        size_kb = size / 1024

        # Format stat
        format_stat = self._create_stat_box("Format:", fmt)
        grid_layout.addWidget(format_stat)

        # Size stat
        size_stat = self._create_stat_box("Size:", f"{size_kb:.1f} KB")
        grid_layout.addWidget(size_stat)
        grid_layout.addWidget(comp_stat)

        # Status stat
        is_modified = level_data.get('level', 0) in self.modified_levels
        status_text = "⚠ Modified" if is_modified else "✓ Valid"
        status_color = "#ff9800" if is_modified else "#4caf50"
        status_stat = self._create_stat_box("Status:", status_text, status_color)
        grid_layout.addWidget(status_stat)

        return grid_widget


    def _create_stat_box(self, label, value, value_color="#e0e0e0"): #vers 1
        """Create individual stat box"""
        stat = QFrame()
        stat.setStyleSheet("""
            QFrame {
                background: #252525;
                border-radius: 3px;
                padding: 6px 10px;
            }
        """)

        layout = QHBoxLayout(stat)
        layout.setContentsMargins(8, 4, 8, 4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(label_widget)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {value_color}; font-weight: bold; font-size: 12px;")
        layout.addWidget(value_widget)

        return stat


    def _create_action_section(self, level_data): #vers 1
        """Create action buttons section"""
        action_widget = QWidget()
        layout = QVBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        level_num = level_data.get('level', 0)

        # Export button
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2e5d2e;
                border: 1px solid #3d7d3d;
                color: white;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #3d7d3d;
            }
        """)
        export_btn.clicked.connect(lambda: self._export_level(level_num))
        layout.addWidget(export_btn)

        # Import button
        import_btn = QPushButton("Import")
        import_btn.setStyleSheet("""
            QPushButton {
                background: #5d3d2e;
                border: 1px solid #7d4d3d;
                color: white;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #7d4d3d;
            }
        """)
        import_btn.clicked.connect(lambda: self._import_level(level_num))
        layout.addWidget(import_btn)

        # Delete button (not for level 0) or Edit button (for level 0)
        if level_num == 0:
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a3a;
                    border: 1px solid #4a4a4a;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #4a4a4a;
                }
            """)
            edit_btn.clicked.connect(self._edit_main_surface)
            layout.addWidget(edit_btn)
        else:
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #5d2e2e;
                    border: 1px solid #7d3d3d;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #7d3d3d;
                }
            """)
            delete_btn.clicked.connect(lambda: self._delete_level(level_num))
            layout.addWidget(delete_btn)

        return action_widget


# - Marker 5

    def _apply_title_font(self): #vers 1
        """Apply title font to title bar labels"""
        if hasattr(self, 'title_font'):
            # Find all title labels
            for label in self.findChildren(QLabel):
                if label.objectName() == "title_label" or "🗺️" in label.text():
                    label.setFont(self.title_font)


    def _apply_panel_font(self): #vers 1
        """Apply panel font to info panels and labels"""
        if hasattr(self, 'panel_font'):
            # Apply to info labels (shadow, Bumpmaps, status labels)
            for label in self.findChildren(QLabel):
                if any(x in label.text() for x in ["shadow:", "Bumpmaps:", "Status:", "Type:", "Format:"]):
                    label.setFont(self.panel_font)


    def _apply_button_font(self): #vers 1
        """Apply button font to all buttons"""
        if hasattr(self, 'button_font'):
            for button in self.findChildren(QPushButton):
                button.setFont(self.button_font)


    def _apply_infobar_font(self): #vers 1
        """Apply fixed-width font to info bar at bottom"""
        if hasattr(self, 'infobar_font'):
            if hasattr(self, 'info_bar'):
                self.info_bar.setFont(self.infobar_font)


    def _toggle_tearoff(self): #vers 2
        """Toggle tear-off state (merge back to IMG Factory) - IMPROVED"""
        try:
            if self.is_docked:
                # Undock from main window
                self._undock_from_main()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"{App_name} torn off from main window")
            else:
                # Dock back to main window
                self._dock_to_main()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"{App_name} docked back to main window")
                    
        except Exception as e:
            img_debugger.error(f"Error toggling tear-off: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Tear-off Error", f"Could not toggle tear-off state:\n{str(e)}")


# - Marker 6

    def _open_settings_dialog(self): #vers 1
        """Open settings dialog and refresh on save"""
        dialog = SettingsDialog(self.mel_settings, self)
        if dialog.exec():
            # Refresh platform list with new ROM path
            self._scan_platforms()
            self.status_label.setText("Settings saved - platforms refreshed")


    def _setup_settings_button(self): #vers 1
        """Setup settings button in UI"""
        settings_btn = QPushButton("âš™ Settings")
        settings_btn.clicked.connect(self._open_settings_dialog)
        settings_btn.setMaximumWidth(120)
        return settings_btn


    def _show_settings_dialog(self): #vers 5
        """Show comprehensive settings dialog with all tabs including hotkeys"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                    QWidget, QLabel, QPushButton, QGroupBox,
                                    QCheckBox, QSpinBox, QFormLayout, QScrollArea,
                                    QKeySequenceEdit, QComboBox, QMessageBox)
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QKeySequence

        dialog = QDialog(self)
        dialog.setWindowTitle(App_name + " Settings")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        layout = QVBoxLayout(dialog)

        # Create tabs
        tabs = QTabWidget()

        # === DISPLAY TAB ===
        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)

        # Thumbnail settings
        thumb_group = QGroupBox("Thumbnail Display")
        thumb_layout = QVBoxLayout()

        thumb_size_layout = QHBoxLayout()
        thumb_size_layout.addWidget(QLabel("Thumbnail size:"))
        thumb_size_spin = QSpinBox()
        thumb_size_spin.setRange(32, 256)
        thumb_size_spin.setValue(self.thumbnail_size if hasattr(self, 'thumbnail_size') else 64)
        thumb_size_spin.setSuffix(" px")
        thumb_size_layout.addWidget(thumb_size_spin)
        thumb_size_layout.addStretch()
        thumb_layout.addLayout(thumb_size_layout)

        thumb_group.setLayout(thumb_layout)
        display_layout.addWidget(thumb_group)

        # Table display settings
        table_group = QGroupBox("Table Display")
        table_layout = QVBoxLayout()

        row_height_layout = QHBoxLayout()
        row_height_layout.addWidget(QLabel("Row height:"))
        row_height_spin = QSpinBox()
        row_height_spin.setRange(50, 200)
        row_height_spin.setValue(getattr(self, 'table_row_height', 100))
        row_height_spin.setSuffix(" px")
        row_height_layout.addWidget(row_height_spin)
        row_height_layout.addStretch()
        table_layout.addLayout(row_height_layout)

        show_grid_check = QCheckBox("Show grid lines")
        show_grid_check.setChecked(getattr(self, 'show_grid_lines', True))
        table_layout.addWidget(show_grid_check)

        table_group.setLayout(table_layout)
        display_layout.addWidget(table_group)

        display_layout.addStretch()
        tabs.addTab(display_tab, "Display")

        # === PREVIEW TAB ===
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        # Preview window settings
        preview_window_group = QGroupBox("Preview Window")
        preview_window_layout = QVBoxLayout()

        show_preview_check = QCheckBox("Show preview window by default")
        show_preview_check.setChecked(getattr(self, 'show_preview_default', True))
        show_preview_check.setToolTip("Automatically open preview when selecting surface")
        preview_window_layout.addWidget(show_preview_check)

        auto_refresh_check = QCheckBox("Auto-refresh preview on selection")
        auto_refresh_check.setChecked(getattr(self, 'auto_refresh_preview', True))
        auto_refresh_check.setToolTip("Update preview immediately when clicking surface")
        preview_window_layout.addWidget(auto_refresh_check)

        preview_window_group.setLayout(preview_window_layout)
        preview_layout.addWidget(preview_window_group)

        # Preview size settings
        preview_size_group = QGroupBox("Preview Size")
        preview_size_layout = QVBoxLayout()

        preview_width_layout = QHBoxLayout()
        preview_width_layout.addWidget(QLabel("Default width:"))
        preview_width_spin = QSpinBox()
        preview_width_spin.setRange(200, 1920)
        preview_width_spin.setValue(getattr(self, 'preview_width', 512))
        preview_width_spin.setSuffix(" px")
        preview_width_layout.addWidget(preview_width_spin)
        preview_width_layout.addStretch()
        preview_size_layout.addLayout(preview_width_layout)

        preview_height_layout = QHBoxLayout()
        preview_height_layout.addWidget(QLabel("Default height:"))
        preview_height_spin = QSpinBox()
        preview_height_spin.setRange(200, 1080)
        preview_height_spin.setValue(getattr(self, 'preview_height', 512))
        preview_height_spin.setSuffix(" px")
        preview_height_layout.addWidget(preview_height_spin)
        preview_height_layout.addStretch()
        preview_size_layout.addLayout(preview_height_layout)

        preview_size_group.setLayout(preview_size_layout)
        preview_layout.addWidget(preview_size_group)

        # Preview background
        preview_bg_group = QGroupBox("Preview Background")
        preview_bg_layout = QVBoxLayout()

        bg_combo = QComboBox()
        bg_combo.addItems(["Black", "White", "Gray", "Custom Color"])
        bg_combo.setCurrentText(getattr(self, 'preview_background', 'Checkerboard'))
        preview_bg_layout.addWidget(bg_combo)

        preview_bg_group.setLayout(preview_bg_layout)
        preview_layout.addWidget(preview_bg_group)

        # Preview zoom
        preview_zoom_group = QGroupBox("Preview Zoom")
        preview_zoom_layout = QVBoxLayout()

        fit_to_window_check = QCheckBox("Fit to window by default")
        fit_to_window_check.setChecked(getattr(self, 'preview_fit_to_window', True))
        preview_zoom_layout.addWidget(fit_to_window_check)

        smooth_zoom_check = QCheckBox("Use smooth scaling")
        smooth_zoom_check.setChecked(getattr(self, 'preview_smooth_scaling', True))
        smooth_zoom_check.setToolTip("Better quality but slower for large model mesh")
        preview_zoom_layout.addWidget(smooth_zoom_check)

        preview_zoom_group.setLayout(preview_zoom_layout)
        preview_layout.addWidget(preview_zoom_group)

        preview_layout.addStretch()
        tabs.addTab(preview_tab, "Preview")

        # === EXPORT TAB ===
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)

        # Export format
        format_group = QGroupBox("Default Collision Export Format")
        format_layout = QVBoxLayout()

        format_combo = QComboBox()
        format_combo.addItems(["COL", "COL2", "COL3", "CST", "3DS"])
        format_combo.setCurrentText(getattr(self, 'default_export_format', 'COL'))
        format_layout.addWidget(format_combo)
        format_hint = QLabel("COL recommended for GTAIII/VC, COL2 for SA")
        format_hint.setStyleSheet("color: #888; font-style: italic;")
        format_layout.addWidget(format_hint)

        format_group.setLayout(format_layout)
        export_layout.addWidget(format_group)

        # Export options
        export_options_group = QGroupBox("Export Options")
        export_options_layout = QVBoxLayout()

        preserve_shadow_check = QCheckBox("Preserve Shadow Mesh when exporting")
        preserve_shadow_check.setChecked(getattr(self, 'export_preserve_shadow', True))
        export_options_layout.addWidget(preserve_shadow_check)

        export_shadowm_check = QCheckBox("Export shadow as separate files")
        export_shadowm_check.setChecked(getattr(self, 'export_shadow_separate', False))
        export_shadowm_check.setToolTip("Save each shadow map as _shadow.col, etc.")
        export_options_layout.addWidget(export_shadowm_check)

        create_subfolders_check = QCheckBox("Create subfolders when exporting all")
        create_subfolders_check.setChecked(getattr(self, 'export_create_subfolders', False))
        create_subfolders_check.setToolTip("Organize exports into folders by col type")
        export_options_layout.addWidget(create_subfolders_check)

        export_options_group.setLayout(export_options_layout)
        export_layout.addWidget(export_options_group)

        # Compatibility note
        compat_label = QLabel(
            "Note: PLACEholder." #TODO
        )
        compat_label.setWordWrap(True)
        compat_label.setStyleSheet("padding: 10px; background-color: #3a3a3a; border-radius: 4px;")
        export_layout.addWidget(compat_label)

        export_layout.addStretch()
        tabs.addTab(export_tab, "Export")

        # === IMPORT TAB ===
        import_tab = QWidget()
        import_layout = QVBoxLayout(import_tab)

        # Import behavior
        import_behavior_group = QGroupBox("Import Behavior")
        import_behavior_layout = QVBoxLayout()

        replace_check = QCheckBox("Replace existing collision with same name")
        replace_check.setChecked(getattr(self, 'import_replace_existing', False))
        import_behavior_layout.addWidget(replace_check)

        auto_format_check = QCheckBox("Automatically select best format")
        auto_format_check.setChecked(getattr(self, 'import_auto_format', True))
        auto_format_check.setToolTip("Choose COL/COL3 based on collision version")
        import_behavior_layout.addWidget(auto_format_check)

        import_behavior_group.setLayout(import_behavior_layout)
        import_layout.addWidget(import_behavior_group)

        # Import format
        import_format_group = QGroupBox("Default Collision Format")
        import_format_layout = QVBoxLayout()

        import_format_combo = QComboBox()
        import_format_combo.addItems(["COL", "COL2", "COL3", "CST", "3DS"])
        import_format_combo.setCurrentText(getattr(self, 'default_import_format', 'COL'))
        import_format_layout.addWidget(import_format_combo)

        format_note = QLabel("COL2/COL3: compression\n, COL type 1 always Uncompressed")
        format_note.setStyleSheet("color: #888; font-style: italic;")
        import_format_layout.addWidget(format_note)

        import_format_group.setLayout(import_format_layout)
        import_layout.addWidget(import_format_group)

        import_layout.addStretch()
        tabs.addTab(import_tab, "Import")

        # === Collision CONSTRAINTS TAB ===
        constraints_tab = QWidget()
        constraints_layout = QVBoxLayout(constraints_tab)

        # Collision naming
        naming_group = QGroupBox("Collision Naming")
        naming_layout = QVBoxLayout()

        name_limit_check = QCheckBox("Enable name length limit")
        name_limit_check.setChecked(getattr(self, 'name_limit_enabled', True))
        name_limit_check.setToolTip("Enforce maximum Collision name length")
        naming_layout.addWidget(name_limit_check)

        char_limit_layout = QHBoxLayout()
        char_limit_layout.addWidget(QLabel("Maximum characters:"))
        char_limit_spin = QSpinBox()
        char_limit_spin.setRange(8, 64)
        char_limit_spin.setValue(getattr(self, 'max_collision_name_length', 32))
        char_limit_spin.setToolTip("RenderWare default is 32 characters")
        char_limit_layout.addWidget(char_limit_spin)
        char_limit_layout.addStretch()
        naming_layout.addLayout(char_limit_layout)

        naming_group.setLayout(naming_layout)
        constraints_layout.addWidget(naming_group)

        # Format support
        format_support_group = QGroupBox("Format Support")
        format_support_layout = QVBoxLayout()

        format_support_group.setLayout(format_support_layout)
        constraints_layout.addWidget(format_support_group)

        constraints_layout.addStretch()
        tabs.addTab(constraints_tab, "Constraints")

        # === KEYBOARD SHORTCUTS TAB ===
        hotkeys_tab = QWidget()
        hotkeys_layout = QVBoxLayout(hotkeys_tab)

        # Add scroll area for hotkeys
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # File Operations Group
        file_group = QGroupBox("File Operations")
        file_form = QFormLayout()

        hotkey_edit_open = QKeySequenceEdit(self.hotkey_open.key() if hasattr(self, 'hotkey_open') else QKeySequence.StandardKey.Open)
        file_form.addRow("Open col:", hotkey_edit_open)

        hotkey_edit_save = QKeySequenceEdit(self.hotkey_save.key() if hasattr(self, 'hotkey_save') else QKeySequence.StandardKey.Save)
        file_form.addRow("Save col:", hotkey_edit_save)

        hotkey_edit_force_save = QKeySequenceEdit(self.hotkey_force_save.key() if hasattr(self, 'hotkey_force_save') else QKeySequence("Alt+Shift+S"))
        force_save_layout = QHBoxLayout()
        force_save_layout.addWidget(hotkey_edit_force_save)
        force_save_hint = QLabel("(Force save even if unmodified)")
        force_save_hint.setStyleSheet("color: #888; font-style: italic;")
        force_save_layout.addWidget(force_save_hint)
        file_form.addRow("Force Save:", force_save_layout)

        hotkey_edit_save_as = QKeySequenceEdit(self.hotkey_save_as.key() if hasattr(self, 'hotkey_save_as') else QKeySequence.StandardKey.SaveAs)
        file_form.addRow("Save As:", hotkey_edit_save_as)

        hotkey_edit_close = QKeySequenceEdit(self.hotkey_close.key() if hasattr(self, 'hotkey_close') else QKeySequence.StandardKey.Close)
        file_form.addRow("Close:", hotkey_edit_close)

        file_group.setLayout(file_form)
        scroll_layout.addWidget(file_group)

        # Edit Operations Group
        edit_group = QGroupBox("Edit Operations")
        edit_form = QFormLayout()

        hotkey_edit_undo = QKeySequenceEdit(self.hotkey_undo.key() if hasattr(self, 'hotkey_undo') else QKeySequence.StandardKey.Undo)
        edit_form.addRow("Undo:", hotkey_edit_undo)

        hotkey_edit_copy = QKeySequenceEdit(self.hotkey_copy.key() if hasattr(self, 'hotkey_copy') else QKeySequence.StandardKey.Copy)
        edit_form.addRow("Copy Collision:", hotkey_edit_copy)

        hotkey_edit_paste = QKeySequenceEdit(self.hotkey_paste.key() if hasattr(self, 'hotkey_paste') else QKeySequence.StandardKey.Paste)
        edit_form.addRow("Paste Collision:", hotkey_edit_paste)

        hotkey_edit_delete = QKeySequenceEdit(self.hotkey_delete.key() if hasattr(self, 'hotkey_delete') else QKeySequence.StandardKey.Delete)
        edit_form.addRow("Delete:", hotkey_edit_delete)

        hotkey_edit_duplicate = QKeySequenceEdit(self.hotkey_duplicate.key() if hasattr(self, 'hotkey_duplicate') else QKeySequence("Ctrl+D"))
        edit_form.addRow("Duplicate:", hotkey_edit_duplicate)

        hotkey_edit_rename = QKeySequenceEdit(self.hotkey_rename.key() if hasattr(self, 'hotkey_rename') else QKeySequence("F2"))
        edit_form.addRow("Rename:", hotkey_edit_rename)

        edit_group.setLayout(edit_form)
        scroll_layout.addWidget(edit_group)

        # Collision Operations Group
        coll_group = QGroupBox("Collision Operations")
        coll_group = QFormLayout()

        hotkey_edit_import = QKeySequenceEdit(self.hotkey_import.key() if hasattr(self, 'hotkey_import') else QKeySequence("Ctrl+I"))
        coll_form.addRow("Import Collision:", hotkey_edit_import)

        hotkey_edit_export = QKeySequenceEdit(self.hotkey_export.key() if hasattr(self, 'hotkey_export') else QKeySequence("Ctrl+E"))
        coll_form.addRow("Export Collision:", hotkey_edit_export)

        hotkey_edit_export_all = QKeySequenceEdit(self.hotkey_export_all.key() if hasattr(self, 'hotkey_export_all') else QKeySequence("Ctrl+Shift+E"))
        coll_form.addRow("Export All:", hotkey_edit_export_all)

        coll_group.setLayout(coll_form)
        scroll_layout.addWidget(coll_group)

        # View Operations Group
        view_group = QGroupBox("View Operations")
        view_form = QFormLayout()

        hotkey_edit_refresh = QKeySequenceEdit(self.hotkey_refresh.key() if hasattr(self, 'hotkey_refresh') else QKeySequence.StandardKey.Refresh)
        view_form.addRow("Refresh:", hotkey_edit_refresh)

        hotkey_edit_properties = QKeySequenceEdit(self.hotkey_properties.key() if hasattr(self, 'hotkey_properties') else QKeySequence("Alt+Return"))
        view_form.addRow("Properties:", hotkey_edit_properties)

        hotkey_edit_find = QKeySequenceEdit(self.hotkey_find.key() if hasattr(self, 'hotkey_find') else QKeySequence.StandardKey.Find)
        view_form.addRow("Find/Search:", hotkey_edit_find)

        hotkey_edit_help = QKeySequenceEdit(self.hotkey_help.key() if hasattr(self, 'hotkey_help') else QKeySequence.StandardKey.HelpContents)
        view_form.addRow("Help:", hotkey_edit_help)

        view_group.setLayout(view_form)
        scroll_layout.addWidget(view_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        hotkeys_layout.addWidget(scroll)

        # Reset to defaults button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_hotkeys_btn = QPushButton("Reset to Plasma6 Defaults")

        def reset_hotkeys():
            reply = QMessageBox.question(dialog, "Reset Hotkeys",
                "Reset all keyboard shortcuts to Plasma6 defaults?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                hotkey_edit_open.setKeySequence(QKeySequence.StandardKey.Open)
                hotkey_edit_save.setKeySequence(QKeySequence.StandardKey.Save)
                hotkey_edit_force_save.setKeySequence(QKeySequence("Alt+Shift+S"))
                hotkey_edit_save_as.setKeySequence(QKeySequence.StandardKey.SaveAs)
                hotkey_edit_close.setKeySequence(QKeySequence.StandardKey.Close)
                hotkey_edit_undo.setKeySequence(QKeySequence.StandardKey.Undo)
                hotkey_edit_copy.setKeySequence(QKeySequence.StandardKey.Copy)
                hotkey_edit_paste.setKeySequence(QKeySequence.StandardKey.Paste)
                hotkey_edit_delete.setKeySequence(QKeySequence.StandardKey.Delete)
                hotkey_edit_duplicate.setKeySequence(QKeySequence("Ctrl+D"))
                hotkey_edit_rename.setKeySequence(QKeySequence("F2"))
                hotkey_edit_import.setKeySequence(QKeySequence("Ctrl+I"))
                hotkey_edit_export.setKeySequence(QKeySequence("Ctrl+E"))
                hotkey_edit_export_all.setKeySequence(QKeySequence("Ctrl+Shift+E"))
                hotkey_edit_refresh.setKeySequence(QKeySequence.StandardKey.Refresh)
                hotkey_edit_properties.setKeySequence(QKeySequence("Alt+Return"))
                hotkey_edit_find.setKeySequence(QKeySequence.StandardKey.Find)
                hotkey_edit_help.setKeySequence(QKeySequence.StandardKey.HelpContents)

        reset_hotkeys_btn.clicked.connect(reset_hotkeys)
        reset_layout.addWidget(reset_hotkeys_btn)
        hotkeys_layout.addLayout(reset_layout)

        tabs.addTab(hotkeys_tab, "Keyboard Shortcuts")

        # Add tabs widget to main layout
        layout.addWidget(tabs)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        def apply_settings(close_dialog=False):
            """Apply all settings"""
            # Apply display settings
            self.thumbnail_size = thumb_size_spin.value()
            self.table_row_height = row_height_spin.value()
            self.show_grid_lines = show_grid_check.isChecked()

            # Apply preview settings
            self.show_preview_default = show_preview_check.isChecked()
            self.auto_refresh_preview = auto_refresh_check.isChecked()
            self.preview_width = preview_width_spin.value()
            self.preview_height = preview_height_spin.value()
            self.preview_background = bg_combo.currentText()
            self.preview_fit_to_window = fit_to_window_check.isChecked()
            self.preview_smooth_scaling = smooth_zoom_check.isChecked()

            # Apply export settings
            self.default_export_format = format_combo.currentText()
            self.export_preserve_alpha = preserve_alpha_check.isChecked()
            self.export_shadow_separate = export_shadow_check.isChecked()
            self.export_create_subfolders = create_subfolders_check.isChecked()

            # Apply import settings
            self.import_auto_name = auto_name_check.isChecked()
            self.import_replace_existing = replace_check.isChecked()
            self.import_auto_format = auto_format_check.isChecked()
            self.default_import_format = import_format_combo.currentText()

            # Apply constraint settings
            self.dimension_limiting_enabled = dimension_check.isChecked()
            self.splash_screen_mode = splash_check.isChecked()
            self.custom_max_dimension = max_dim_spin.value()
            self.name_limit_enabled = name_limit_check.isChecked()
            self.max_surface_name_length = char_limit_spin.value()
            self.iff_import_enabled = iff_check.isChecked()

            # Apply hotkeys
            if hasattr(self, 'hotkey_open'):
                self.hotkey_open.setKey(hotkey_edit_open.keySequence())
            if hasattr(self, 'hotkey_save'):
                self.hotkey_save.setKey(hotkey_edit_save.keySequence())
            if hasattr(self, 'hotkey_force_save'):
                self.hotkey_force_save.setKey(hotkey_edit_force_save.keySequence())
            if hasattr(self, 'hotkey_save_as'):
                self.hotkey_save_as.setKey(hotkey_edit_save_as.keySequence())
            if hasattr(self, 'hotkey_close'):
                self.hotkey_close.setKey(hotkey_edit_close.keySequence())
            if hasattr(self, 'hotkey_undo'):
                self.hotkey_undo.setKey(hotkey_edit_undo.keySequence())
            if hasattr(self, 'hotkey_copy'):
                self.hotkey_copy.setKey(hotkey_edit_copy.keySequence())
            if hasattr(self, 'hotkey_paste'):
                self.hotkey_paste.setKey(hotkey_edit_paste.keySequence())
            if hasattr(self, 'hotkey_delete'):
                self.hotkey_delete.setKey(hotkey_edit_delete.keySequence())
            if hasattr(self, 'hotkey_duplicate'):
                self.hotkey_duplicate.setKey(hotkey_edit_duplicate.keySequence())
            if hasattr(self, 'hotkey_rename'):
                self.hotkey_rename.setKey(hotkey_edit_rename.keySequence())
            if hasattr(self, 'hotkey_import'):
                self.hotkey_import.setKey(hotkey_edit_import.keySequence())
            if hasattr(self, 'hotkey_export'):
                self.hotkey_export.setKey(hotkey_edit_export.keySequence())
            if hasattr(self, 'hotkey_export_all'):
                self.hotkey_export_all.setKey(hotkey_edit_export_all.keySequence())
            if hasattr(self, 'hotkey_refresh'):
                self.hotkey_refresh.setKey(hotkey_edit_refresh.keySequence())
            if hasattr(self, 'hotkey_properties'):
                self.hotkey_properties.setKey(hotkey_edit_properties.keySequence())
            if hasattr(self, 'hotkey_find'):
                self.hotkey_find.setKey(hotkey_edit_find.keySequence())
            if hasattr(self, 'hotkey_help'):
                self.hotkey_help.setKey(hotkey_edit_help.keySequence())

            # Refresh UI with new settings
            if hasattr(self, '_reload_surface_table'):
                self._reload_surface_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Settings applied")

            if close_dialog:
                dialog.accept()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: apply_settings(close_dialog=False))
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(lambda: apply_settings(close_dialog=True))
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _show_settings_context_menu(self, pos): #vers 1
        """Show context menu for Settings button"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        # Move window action
        move_action = menu.addAction("Move Window")
        move_action.triggered.connect(self._enable_move_mode)

        # Maximize window action
        max_action = menu.addAction("Maximize Window")
        max_action.triggered.connect(self._toggle_maximize)

        # Minimize action
        min_action = menu.addAction("Minimize")
        min_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # Upscale Native action
        upscale_action = menu.addAction("Upscale Native")
        upscale_action.setCheckable(True)
        upscale_action.setChecked(False)
        upscale_action.triggered.connect(self._toggle_upscale_native)

        # Shaders action
        shaders_action = menu.addAction("Shaders")
        shaders_action.triggered.connect(self._show_shaders_dialog)

        menu.addSeparator()

        # Icon display mode submenu # TODO icon only system is missing.
        display_menu = menu.addMenu("Platform Display")

        icons_text_action = display_menu.addAction("Icons & Text")
        icons_text_action.setCheckable(True)
        icons_text_action.setChecked(self.icon_display_mode == "icons_and_text")
        icons_text_action.triggered.connect(lambda: self._set_icon_display_mode("icons_and_text"))

        icons_only_action = display_menu.addAction("Icons Only")
        icons_only_action.setCheckable(True)
        icons_only_action.setChecked(self.icon_display_mode == "icons_only")
        icons_only_action.triggered.connect(lambda: self._set_icon_display_mode("icons_only"))

        text_only_action = display_menu.addAction("Text Only")
        text_only_action.setCheckable(True)
        text_only_action.setChecked(self.icon_display_mode == "text_only")
        text_only_action.triggered.connect(lambda: self._set_icon_display_mode("text_only"))

        # Show menu at button position
        menu.exec(self.settings_btn.mapToGlobal(pos))

    def _enable_move_mode(self): #vers 2
        """Enable move window mode using system move"""
        # Use Qt's system move which works on Windows, Linux, etc.
        if hasattr(self.windowHandle(), 'startSystemMove'):
            self.windowHandle().startSystemMove()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Move Window",
                "Drag the titlebar to move the window")

    def _toggle_upscale_native(self): #vers 1
        """Toggle upscale native resolution"""
        # Placeholder for upscale native functionality
        print("Upscale Native toggled")

    def _show_shaders_dialog(self): #vers 1
        """Show shaders configuration dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Shaders",
            "Shader configuration coming soon!\n\nThis will allow you to:\n"
            "- Select shader presets\n"
            "- Configure CRT effects\n"
            "- Adjust visual filters")

    def _show_window_context_menu(self, pos): #vers 1
        """Show context menu for titlebar right-click"""
        from PyQt6.QtWidgets import QMenu


        # Move window action
        move_action = menu.addAction("Move Window")
        move_action.triggered.connect(self._enable_move_mode)

        # Maximize/Restore action
        if self.isMaximized():
            max_action = menu.addAction("Restore Window")
        else:
            max_action = menu.addAction("Maximize Window")
        max_action.triggered.connect(self._toggle_maximize)

        # Minimize action
        min_action = menu.addAction("Minimize")
        min_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # Close action
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)

        # Show menu at global position
        menu.exec(self.mapToGlobal(pos))


    def _get_icon_color(self): #vers 1
        """Get icon color from current theme"""
        if APPSETTINGS_AVAILABLE and self.app_settings:
            colors = self.app_settings.get_theme_colors()
            return colors.get('text_primary', '#ffffff')
        return '#ffffff'


    def _apply_fonts_to_widgets(self): #vers 1
        """Apply fonts from AppSettings to all widgets"""
        if not hasattr(self, 'default_font'):
            return

        print("\n=== Applying Fonts ===")
        print(f"Default font: {self.default_font.family()} {self.default_font.pointSize()}pt")
        print(f"Title font: {self.title_font.family()} {self.title_font.pointSize()}pt")
        print(f"Panel font: {self.panel_font.family()} {self.panel_font.pointSize()}pt")
        print(f"Button font: {self.button_font.family()} {self.button_font.pointSize()}pt")

        # Apply default font to main window
        self.setFont(self.default_font)

        # Apply title font to titlebar
        if hasattr(self, 'title_label'):
            self.title_label.setFont(self.title_font)

        # Apply panel font to lists
        if hasattr(self, 'platform_list'):
            self.platform_list.setFont(self.panel_font)
        if hasattr(self, 'game_list'):
            self.game_list.setFont(self.panel_font)

        # Apply button font to all buttons
        for btn in self.findChildren(QPushButton):
            btn.setFont(self.button_font)

        print("Fonts applied to widgets")
        print("======================\n")


    def _apply_theme(self): #vers 2
        """Apply theme from main window"""
        try:
            if self.main_window and hasattr(self.main_window, 'app_settings'):
                # Get current theme
                theme_name = self.main_window.app_settings.current_settings.get('theme', 'IMG_Factory')
                stylesheet = self.main_window.app_settings.get_stylesheet()

                # Apply to App
                self.setStyleSheet(stylesheet)

                # Force update
                self.update()

                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"theme applied: {theme_name}")
            else:
                # Fallback dark theme
                self.setStyleSheet("""
                    QWidget {
                        background-color: #2b2b2b;
                        color: #e0e0e0;
                    }
                    QListWidget, QTableWidget, QTextEdit {
                        background-color: #1e1e1e;
                        border: 1px solid #3a3a3a;
                    }
                """)
        except Exception as e:
            print(f"Theme application error: {e}")


    def _apply_settings(self, dialog): #vers 5
        """Apply settings from dialog"""
        from PyQt6.QtGui import QFont

        # Store font settings
        self.title_font = QFont(self.title_font_combo.currentFont().family(), self.title_font_size.value())
        self.panel_font = QFont(self.panel_font_combo.currentFont().family(), self.panel_font_size.value())
        self.button_font = QFont(self.button_font_combo.currentFont().family(), self.button_font_size.value())
        self.infobar_font = QFont(self.infobar_font_combo.currentFont().family(), self.infobar_font_size.value())

        # Apply fonts to specific elements
        self._apply_title_font()
        self._apply_panel_font()
        self._apply_button_font()
        self._apply_infobar_font()
        self.default_export_format = format_combo.currentText()

        # Apply button display mode
        mode_map = ["icons", "text", "both"]
        new_mode = mode_map[self.settings_display_combo.currentIndex()]
        if new_mode != self.button_display_mode:
            self.button_display_mode = new_mode
            self._update_all_buttons()

        # Locale setting (would need implementation)
        locale_text = self.settings_locale_combo.currentText()


# - Marker 7

    def _refresh_main_window(self): #vers 1
        """Refresh the main window to show changes"""
        try:
            if self.main_window:
                # Try to refresh the main table
                if hasattr(self.main_window, 'refresh_table'):
                    self.main_window.refresh_table()
                elif hasattr(self.main_window, 'reload_current_file'):
                    self.main_window.reload_current_file()
                elif hasattr(self.main_window, 'update_display'):
                    self.main_window.update_display()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Refresh error: {str(e)}")


#------ Col functions

    def _open_file(self): #vers 1
        """Open file dialog and load COL file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open COL File",
                "",
                "COL Files (*.col);;All Files (*)"
            )

            if file_path:
                self.open_col_file(file_path)

        except Exception as e:
            img_debugger.error(f"Error in open file dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")


    def _save_file(self): #vers 1
        """Save current COL file"""
        try:
            if not self.current_col_file:
                QMessageBox.warning(self, "Save", "No COL file loaded to save")
                return

            if not self.current_file_path:
                # No path yet, do Save As
                self._save_file_as()
                return

            # Save to current path
            if self.current_col_file.save():
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Saved COL: {os.path.basename(self.current_file_path)}")

                QMessageBox.information(self, "Save", f"COL file saved successfully:\n{os.path.basename(self.current_file_path)}")
                img_debugger.success(f"Saved COL file: {self.current_file_path}")
            else:
                error_msg = self.current_col_file.save_error if hasattr(self.current_col_file, 'save_error') else "Unknown error"
                QMessageBox.critical(self, "Save Error", f"Failed to save COL file:\n{error_msg}")
                img_debugger.error(f"Save failed: {error_msg}")

        except Exception as e:
            img_debugger.error(f"Error saving file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")


    def _save_file_as(self): #vers 1
        """Save As dialog"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save COL File As",
                "",
                "COL Files (*.col);;All Files (*)"
            )

            if file_path:
                self.current_file_path = file_path
                self.current_col_file.file_path = file_path
                self._save_file()

        except Exception as e:
            img_debugger.error(f"Error in save as dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")


    def _load_settings(self): #vers 1
        """Load settings from config file"""
        import json

        settings_file = os.path.join(
            os.path.dirname(__file__),
            'col_workshop_settings.json'
        )

        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.save_to_source_location = settings.get('save_to_source_location', True)
                    self.last_save_directory = settings.get('last_save_directory', None)
        except Exception as e:
            print(f"Failed to load settings: {e}")


    def _save_settings(self): #vers 1
        """Save settings to config file"""
        import json

        settings_file = os.path.join(
            os.path.dirname(__file__),
            'col_workshop_settings.json'
        )

        try:
            settings = {
                'save_to_source_location': self.save_to_source_location,
                'last_save_directory': self.last_save_directory
            }

            with open(settings_file, 'w') as f:
                json.dump(settings, indent=2, fp=f)
        except Exception as e:
            print(f"Failed to save settings: {e}")


    def open_col_file(self, file_path): #vers 3
        """Open standalone COL file - supports COL1, COL2, COL3"""
        try:
            from apps.methods.col_core_classes import COLFile

            # Create and load COL file
            col_file = COLFile(file_path)

            if not col_file.load():
                error_msg = col_file.load_error if hasattr(col_file, 'load_error') else "Unknown error"
                QMessageBox.warning(self, "Open Failed", f"Failed to load COL file:\n{error_msg}")
                return False

            # Store loaded file
            self.current_col_file = col_file
            self.current_file_path = file_path

            # Update window title with model count
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            version_str = f"COL ({model_count} models)"
            self.setWindowTitle(f"{App_name} - {os.path.basename(file_path)} - {version_str}")

            # Populate UI
            self._populate_collision_list()  # ADD THIS LINE

            # Select first model by default
            if self.collision_list.rowCount() > 0:
                self.collision_list.selectRow(0)
                self._on_collision_selected()


            # Enable buttons
            if hasattr(self, 'save_btn'):
                self.save_btn.setEnabled(True)
            if hasattr(self, 'analyze_btn'):
                self.analyze_btn.setEnabled(True)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Loaded COL: {os.path.basename(file_path)} ({model_count} models)")

            img_debugger.success(f"Opened COL file: {file_path} with {model_count} models")
            return True

        except Exception as e:
            img_debugger.error(f"Error opening COL file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open COL file:\n{str(e)}")
            return False


    def load_from_img_archive(self, img_path): #vers 1
        """Load COL files from IMG archive"""
        try:
            # TODO: Implement IMG archive COL loading
            # This would extract COL files from the IMG and populate the list

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Loading COL files from IMG: {os.path.basename(img_path)}")

            img_debugger.info(f"IMG archive COL loading - not yet implemented: {img_path}")
            return False

        except Exception as e:
            img_debugger.error(f"Error loading from IMG archive: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load from IMG:\n{str(e)}")
            return False


    def _analyze_collision(self): #vers 1
        """Analyze current COL file"""
        try:
            if not self.current_col_file or not self.current_file_path:
                QMessageBox.warning(self, "Analyze", "No COL file loaded to analyze")
                return

            # Import analysis functions
            from apps.methods.col_operations import get_col_detailed_analysis
            from gui.col_dialogs import show_col_analysis_dialog

            # Get detailed analysis
            analysis_data = get_col_detailed_analysis(self.current_file_path)

            if 'error' in analysis_data:
                QMessageBox.warning(self, "Analysis Error", f"Analysis failed:\n{analysis_data['error']}")
                return

            # Show analysis dialog
            show_col_analysis_dialog(self, analysis_data, os.path.basename(self.current_file_path))

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Analyzed COL: {os.path.basename(self.current_file_path)}")

        except Exception as e:
            img_debugger.error(f"Error analyzing file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to analyze file:\n{str(e)}")


    def _on_col_selected(self, item): #vers 1
        """Handle COL file selection"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                txd_data = self._extract_col_from_img(entry)
                if txd_data:
                    self.current_col_data = col_data
                    self.current_col_name = entry.name
                    self._load_col_files(col_data, entry.name)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error selecting COL: {str(e)}")


    def _extract_col_from_img(self, entry): #vers 2
        """Extract TXD data from IMG entry"""
        try:
            if not self.current_img:
                return None
            return self.current_img.read_entry_data(entry)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Extract error: {str(e)}")
            return None


    def _on_collision_selected(self): #vers 6
        """Handle COL model selection from table"""
        try:
            selected_rows = self.collision_list.selectionModel().selectedRows()
            if not selected_rows:
                img_debugger.debug("No rows selected")
                return

            row = selected_rows[0].row()
            details_item = self.collision_list.item(row, 1)

            if not details_item:
                img_debugger.debug("No details item found")
                return

            model_index = details_item.data(Qt.ItemDataRole.UserRole)
            img_debugger.debug(f"Selected row {row}, model index {model_index}")

            if not self.current_col_file or not hasattr(self.current_col_file, 'models'):
                img_debugger.debug("No COL file or models")
                return

            if model_index is None or model_index < 0 or model_index >= len(self.current_col_file.models):
                img_debugger.debug(f"Invalid model index: {model_index}")
                return

            # Get selected model
            model = self.current_col_file.models[model_index]
            model_name = getattr(model, 'name', f'Model_{model_index}')

            # Update info display
            if hasattr(self, 'info_name'):
                self.info_name.setText(model_name)

            # Update preview widget
            if hasattr(self, 'preview_widget'):
                if VIEWPORT_AVAILABLE and isinstance(self.preview_widget, COL3DViewport):
                    # Use 3D viewport
                    self.preview_widget.set_current_model(model, model_index)
                    img_debugger.success(f"3D viewport updated for {model_name}")
                else:
                    # Use 2D preview fallback
                    width = max(400, self.preview_widget.width())
                    height = max(400, self.preview_widget.height())
                    img_debugger.debug(f"Rendering 2D preview: {width}x{height} for {model_name}")
                    preview_pixmap = self._render_collision_preview(model, width, height)
                    self.preview_widget.setPixmap(preview_pixmap)
                    self.preview_widget.setScaledContents(False)
                    img_debugger.success(f"2D preview updated for {model_name}")
            else:
                img_debugger.warning("No preview_widget attribute found")

        except Exception as e:
            img_debugger.error(f"Error selecting model: {str(e)}")
            import traceback
            traceback.print_exc()


    def _show_collision_context_menu(self, position): #vers 1
        """Show context menu for collision list"""
        item = self.collision_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Get model index
        row = self.collision_list.row(item)
        if row < 0 or not self.current_col_file:
            return

        model = self.current_col_file.models[row]

        # Show Details action
        details_action = menu.addAction("📋 Show Details")
        details_action.triggered.connect(lambda: self._show_model_details(model, row))

        # Copy Info action
        copy_action = menu.addAction("Copy Info to Clipboard")
        copy_action.triggered.connect(lambda: self._copy_model_info(model, row))

        menu.exec(self.collision_list.mapToGlobal(position))


    def _show_model_details(self, model, index): #vers 1
        """Show detailed model information dialog"""
        from PyQt6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Model Details - {model.name}")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        # Create detailed info text
        info_text = f"""Model: {model.name}
    Index: {index}
    Version: {model.version.name if hasattr(model.version, 'name') else model.version}

    Bounding Box:
    Center: ({model.bounding_box.center.x:.3f}, {model.bounding_box.center.y:.3f}, {model.bounding_box.center.z:.3f})
    Min: ({model.bounding_box.min.x:.3f}, {model.bounding_box.min.y:.3f}, {model.bounding_box.min.z:.3f})
    Max: ({model.bounding_box.max.x:.3f}, {model.bounding_box.max.y:.3f}, {model.bounding_box.max.z:.3f})
    Radius: {model.bounding_box.radius:.3f}

    Collision Data:
    Spheres: {len(model.spheres)}
    Boxes: {len(model.boxes)}
    Vertices: {len(model.vertices)}
    Faces: {len(model.faces)}

    """

        # Add first 3 vertices if available
        if len(model.vertices) > 0:
            info_text += "\nVertices:\n"
            for i in range(min(30000, len(model.vertices))):
                v = model.vertices[i]
                info_text += f"  [{i}] ({v.position.x:.3f}, {v.position.y:.3f}, {v.position.z:.3f})\n"

        # Add material info from faces
        if len(model.faces) > 0:
            materials = set()
            for face in model.faces:
                if hasattr(face, 'material'):
                    mat_id = face.material.material_id if hasattr(face.material, 'material_id') else face.material
                    materials.add(mat_id)
            info_text += f"\nUnique Materials: {len(materials)}\n"
            info_text += f"Material IDs: {sorted(materials)}\n"

        text_edit = QTextEdit()
        text_edit.setPlainText(info_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(lambda: self._copy_text_to_clipboard(info_text))
        layout.addWidget(copy_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()


    def _copy_model_info(self, model, index): #vers 1
        """Copy model info to clipboard"""
        info = f"{model.name} | S:{len(model.spheres)} B:{len(model.boxes)} V:{len(model.vertices)} F:{len(model.faces)}"
        self._copy_text_to_clipboard(info)
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Model info copied to clipboard", 2000)


    def _copy_text_to_clipboard(self, text): #vers 1
        """Copy text to system clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


    def _populate_collision_list(self): #vers 4
        """Populate collision table with models - matches TXD Workshop style"""
        try:
            self.collision_list.setRowCount(0)

            if not self.current_col_file or not hasattr(self.current_col_file, 'models'):
                return

            for i, model in enumerate(self.current_col_file.models):
                # Get model info
                name = getattr(model, 'name', f'Model_{i}')
                version = getattr(model, 'version', COLVersion.COL_1)

                # Count collision elements
                spheres = len(getattr(model, 'spheres', []))
                boxes = len(getattr(model, 'boxes', []))
                faces = len(getattr(model, 'faces', []))
                vertices = len(getattr(model, 'vertices', []))

                # Add row
                row = self.collision_list.rowCount()
                self.collision_list.insertRow(row)

                # Create thumbnail item
                thumb_item = QTableWidgetItem()
                thumbnail = self._generate_collision_thumbnail(model, 64, 64)
                thumb_item.setData(Qt.ItemDataRole.DecorationRole, thumbnail)
                thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Create details text
                details = f"Name: {name}\n"
                details += f"Version: {version.name}\n"
                details += f"Spheres: {spheres} | Boxes: {boxes}\n"
                details += f"Faces: {faces} | Vertices: {vertices}"

                details_item = QTableWidgetItem(details)
                details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                details_item.setData(Qt.ItemDataRole.UserRole, i)  # Store model index

                # Set items
                self.collision_list.setItem(row, 0, thumb_item)
                self.collision_list.setItem(row, 1, details_item)

                # Set row height
                self.collision_list.setRowHeight(row, 100)

            img_debugger.debug(f"Populated collision table with {len(self.current_col_file.models)} models")

        except Exception as e:
            img_debugger.error(f"Error populating collision table: {str(e)}")


    def _create_preview_widget(self, level_data=None): #vers 3
        """Create preview widget - large collision preview like TXD Workshop"""
        if level_data is None:
            # Return preview label for collision display
            preview = QLabel()
            preview.setMinimumSize(400, 400)
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview.setStyleSheet("""
                QLabel {
                    background: #0a0a0a;
                    border: 2px solid #3a3a3a;
                    border-radius: 3px;
                    color: #888;
                }
            """)
            preview.setText("Preview Area\n\nSelect a collision model to preview")
            return preview


    def _toggle_spheres(self, checked): #vers 3
        """Toggle sphere visibility"""
        try:
            if hasattr(self, 'viewer_3d'):
                self.viewer_3d.set_view_options(show_spheres=checked)
            img_debugger.debug(f"Spheres visibility: {checked}")
        except Exception as e:
            img_debugger.error(f"Error toggling spheres: {str(e)}")


    def _toggle_boxes(self, checked): #vers 3
        """Toggle box visibility"""
        try:
            if hasattr(self, 'viewer_3d'):
                self.viewer_3d.set_view_options(show_boxes=checked)
            img_debugger.debug(f"Boxes visibility: {checked}")
        except Exception as e:
            img_debugger.error(f"Error toggling boxes: {str(e)}")


    def _toggle_mesh(self, checked): #vers 3
        """Toggle mesh visibility"""
        try:
            if hasattr(self, 'viewer_3d'):
                self.viewer_3d.set_view_options(show_mesh=checked)
            img_debugger.debug(f"Mesh visibility: {checked}")
        except Exception as e:
            img_debugger.error(f"Error toggling mesh: {str(e)}")


# ----- Render functions

    def update_display(self): #vers 2
        """Update 3D viewer display with 2D wireframe rendering"""
        try:
            # Create a pixmap to draw on
            pixmap = QPixmap(self.size())
            pixmap.fill(QColor(30, 30, 30))  # Dark background

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            if not self.current_model:
                # No model loaded
                painter.setPen(QColor(150, 150, 150))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                            "3D Viewer\n\nNo COL model selected")
                painter.end()
                self.setPixmap(pixmap)
                return

            # Get model data
            spheres = getattr(self.current_model, 'spheres', [])
            boxes = getattr(self.current_model, 'boxes', [])
            vertices = getattr(self.current_model, 'vertices', [])
            faces = getattr(self.current_model, 'faces', [])

            # Calculate view bounds and scale
            scale, offset_x, offset_y = self._calculate_view_transform()

            # Draw grid
            self._draw_grid(painter, scale, offset_x, offset_y)

            # Draw collision elements
            if self.show_spheres and spheres:
                self._draw_spheres(painter, spheres, scale, offset_x, offset_y)

            if self.show_boxes and boxes:
                self._draw_boxes(painter, boxes, scale, offset_x, offset_y)

            if self.show_mesh and vertices and faces:
                self._draw_mesh(painter, vertices, faces, scale, offset_x, offset_y)

            # Draw legend
            self._draw_legend(painter)

            painter.end()
            self.setPixmap(pixmap)

        except Exception as e:
            img_debugger.error(f"Error updating 3D viewer: {str(e)}")


    def _generate_collision_thumbnail(self, model, width, height): #vers 2
        """Generate thumbnail preview of collision model"""
        try:
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(40, 40, 40))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Get collision data
            spheres = getattr(model, 'spheres', [])
            boxes = getattr(model, 'boxes', [])
            vertices = getattr(model, 'vertices', [])
            faces = getattr(model, 'faces', [])

            if not spheres and not boxes and not vertices:
                # Empty model
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Empty")
                painter.end()
                return pixmap

            # Calculate bounds and scale for thumbnail
            all_points = []

            for sphere in spheres:
                if hasattr(sphere, 'center'):
                    all_points.append((sphere.center.x, sphere.center.z))

            for box in boxes:
                if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                    all_points.append((box.min_point.x, box.min_point.z))
                    all_points.append((box.max_point.x, box.max_point.z))

            for vertex in vertices:
                if hasattr(vertex, 'position'):
                    all_points.append((vertex.position.x, vertex.position.z))

            if not all_points:
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "No Data")
                painter.end()
                return pixmap

            # Calculate bounds with safety checks
            xs = [p[0] for p in all_points if abs(p[0]) < 10000]
            zs = [p[1] for p in all_points if abs(p[1]) < 10000]

            if not xs or not zs:
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Invalid")
                painter.end()
                return pixmap

            min_x, max_x = min(xs), max(xs)
            min_z, max_z = min(zs), max(zs)

            # Calculate scale to fit in thumbnail
            range_x = max_x - min_x if max_x != min_x else 1
            range_z = max_z - min_z if max_z != min_z else 1

            # Prevent extreme scaling
            if range_x > 10000 or range_z > 10000 or range_x < 0.001 or range_z < 0.001:
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Too Large")
                painter.end()
                return pixmap

            scale = min((width - 20) / range_x, (height - 20) / range_z)

            # Clamp scale to reasonable values
            scale = max(0.1, min(scale, 100))

            offset_x = width / 2 - (min_x + max_x) / 2 * scale
            offset_y = height / 2 - (min_z + max_z) / 2 * scale

            # Helper function to clamp coordinates
            def clamp_coord(val):
                return max(-10000, min(10000, int(val)))

            # Draw spheres
            painter.setPen(QPen(QColor(100, 150, 255), 1))
            painter.setBrush(QBrush(QColor(100, 150, 255, 50)))
            for sphere in spheres[:50]:  # Limit to first 50
                if hasattr(sphere, 'center') and hasattr(sphere, 'radius'):
                    x = clamp_coord(sphere.center.x * scale + offset_x)
                    y = clamp_coord(sphere.center.z * scale + offset_y)
                    r = clamp_coord(sphere.radius * scale)

                    if 0 <= x <= width and 0 <= y <= height and r > 0 and r < 1000:
                        painter.drawEllipse(QPoint(x, y), r, r)

            # Draw boxes
            painter.setPen(QPen(QColor(255, 150, 100), 1))
            painter.setBrush(QBrush(QColor(255, 150, 100, 50)))
            for box in boxes[:50]:  # Limit to first 50
                if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                    x1 = clamp_coord(box.min_point.x * scale + offset_x)
                    y1 = clamp_coord(box.min_point.z * scale + offset_y)
                    x2 = clamp_coord(box.max_point.x * scale + offset_x)
                    y2 = clamp_coord(box.max_point.z * scale + offset_y)

                    w = abs(x2 - x1)
                    h = abs(y2 - y1)

                    if w > 0 and h > 0 and w < 1000 and h < 1000:
                        painter.drawRect(min(x1, x2), min(y1, y2), w, h)

            # Draw mesh wireframe
            if faces and vertices:
                painter.setPen(QPen(QColor(150, 255, 150), 1))
                for face in faces[:50]:  # Limit to first 50 faces
                    if hasattr(face, 'vertex_indices') and len(face.vertex_indices) >= 3:
                        try:
                            idx0 = face.vertex_indices[0]
                            idx1 = face.vertex_indices[1]
                            idx2 = face.vertex_indices[2]

                            if idx0 < len(vertices) and idx1 < len(vertices) and idx2 < len(vertices):
                                v1 = vertices[idx0].position
                                v2 = vertices[idx1].position
                                v3 = vertices[idx2].position

                                x1 = clamp_coord(v1.x * scale + offset_x)
                                y1 = clamp_coord(v1.z * scale + offset_y)
                                x2 = clamp_coord(v2.x * scale + offset_x)
                                y2 = clamp_coord(v2.z * scale + offset_y)
                                x3 = clamp_coord(v3.x * scale + offset_x)
                                y3 = clamp_coord(v3.z * scale + offset_y)

                                painter.drawLine(x1, y1, x2, y2)
                                painter.drawLine(x2, y2, x3, y3)
                                painter.drawLine(x3, y3, x1, y1)
                        except:
                            pass

            painter.end()
            return pixmap

        except Exception as e:
            img_debugger.error(f"Error generating thumbnail: {str(e)}")
            # Return error thumbnail
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(60, 60, 60))
            painter = QPainter(pixmap)
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Error")
            painter.end()
            return pixmap


    def _render_collision_preview(self, model, width, height): #vers 2
        """Render collision model for preview panel - IMPROVED VERSION"""
        try:
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(20, 20, 20))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # Get collision data
            spheres = getattr(model, 'spheres', [])
            boxes = getattr(model, 'boxes', [])
            vertices = getattr(model, 'vertices', [])
            faces = getattr(model, 'faces', [])

            if not spheres and not boxes and not vertices:
                painter.setPen(QColor(150, 150, 150))
                painter.setFont(QFont("Arial", 12))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter,
                            "No Collision Data\n\nModel is empty")
                painter.end()
                return pixmap

            # Calculate bounds from all available collision elements
            all_points = []
            
            # Add sphere centers and radii
            for sphere in spheres:
                if hasattr(sphere, 'center'):
                    all_points.append((sphere.center.x, sphere.center.z))
                    # Add points for the sphere radius to ensure proper scaling
                    if hasattr(sphere, 'radius'):
                        all_points.append((sphere.center.x + sphere.radius, sphere.center.z + sphere.radius))
                        all_points.append((sphere.center.x - sphere.radius, sphere.center.z - sphere.radius))

            # Add box corners
            for box in boxes:
                if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                    all_points.append((box.min_point.x, box.min_point.z))
                    all_points.append((box.max_point.x, box.max_point.z))
                    # Add all 4 corners of the box
                    all_points.append((box.min_point.x, box.max_point.z))
                    all_points.append((box.max_point.x, box.min_point.z))

            # Add vertex positions
            for vertex in vertices:
                if hasattr(vertex, 'position'):
                    all_points.append((vertex.position.x, vertex.position.z))

            if not all_points:
                # Draw empty state
                painter.setPen(QColor(150, 150, 150))
                painter.setFont(QFont("Arial", 12))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter,
                            "No Collision Data\n\nModel is empty")
                painter.end()
                return pixmap

            # Calculate bounds with padding
            xs = [p[0] for p in all_points]
            zs = [p[1] for p in all_points]
            min_x, max_x = min(xs), max(xs)
            min_z, max_z = min(zs), max(zs)

            # Add some padding to prevent elements from touching edges
            padding = max((max_x - min_x) * 0.1, (max_z - min_z) * 0.1, 1.0)
            min_x -= padding
            max_x += padding
            min_z -= padding
            max_z += padding

            range_x = max_x - min_x if max_x != min_x else 1
            range_z = max_z - min_z if max_z != min_z else 1
            
            # Calculate scale with aspect ratio preservation
            scale_x = (width * 0.8) / range_x  # Use 80% of available space
            scale_z = (height * 0.8) / range_z
            scale = min(scale_x, scale_z)  # Use the smaller scale to fit everything
            
            # Calculate center offset
            center_x = width / 2 - (min_x + max_x) / 2 * scale
            center_z = height / 2 - (min_z + max_z) / 2 * scale

            # Draw grid background
            painter.setPen(QPen(QColor(40, 40, 40), 1, Qt.PenStyle.DotLine))
            # Draw grid lines based on the calculated bounds
            grid_step = max(abs(range_x), abs(range_z)) / 20  # 20 grid lines across the range
            if grid_step > 0:
                start_x = int(min_x / grid_step) * grid_step
                start_z = int(min_z / grid_step) * grid_step
                for i in range(-20, 21):
                    grid_x = start_x + i * grid_step
                    grid_z = start_z + i * grid_step
                    screen_x = grid_x * scale + center_x
                    screen_z = grid_z * scale + center_z
                    if 0 <= screen_x <= width:
                        painter.drawLine(int(screen_x), 0, int(screen_x), height)
                    if 0 <= screen_z <= height:
                        painter.drawLine(0, int(screen_z), width, int(screen_z))

            # Draw coordinate system
            painter.setPen(QPen(QColor(80, 80, 80), 2))
            # X axis (red)
            painter.drawLine(width//2 - 20, height//2, width//2 + 20, height//2)
            # Z axis (blue) 
            painter.drawLine(width//2, height//2 - 20, width//2, height//2 + 20)

            # Draw spheres (if enabled)
            if getattr(self, '_show_spheres', True):  # Use proper show_spheres flag
                painter.setPen(QPen(QColor(100, 180, 255), 2))
                painter.setBrush(QBrush(QColor(100, 180, 255, 80)))
                for sphere in spheres:
                    if hasattr(sphere, 'center') and hasattr(sphere, 'radius'):
                        screen_x = sphere.center.x * scale + center_x
                        screen_y = sphere.center.z * scale + center_z
                        screen_radius = sphere.radius * scale
                        # Only draw if sphere is within visible area
                        if (0 <= screen_x <= width and 0 <= screen_y <= height and screen_radius > 0.5):
                            painter.drawEllipse(QPoint(int(screen_x), int(screen_y)), int(screen_radius), int(screen_radius))

            # Draw boxes
            if getattr(self, '_show_boxes', True):  # Use proper show_boxes flag
                painter.setPen(QPen(QColor(255, 180, 100), 2))
                painter.setBrush(QBrush(QColor(255, 180, 100, 80)))
                for box in boxes:
                    if hasattr(box, 'min_point') and hasattr(box, 'max_point'):
                        x1 = box.min_point.x * scale + center_x
                        y1 = box.min_point.z * scale + center_z
                        x2 = box.max_point.x * scale + center_x
                        y2 = box.max_point.z * scale + center_z
                        # Only draw if box is within visible area
                        if (min(x1, x2) <= width and max(x1, x2) >= 0 and 
                            min(y1, y2) <= height and max(y1, y2) >= 0):
                            painter.drawRect(int(min(x1, x2)), int(min(y1, y2)), 
                                           int(abs(x2-x1)), int(abs(y2-y1)))

            # Draw mesh wireframe
            if getattr(self, '_show_mesh', True) and faces and vertices:  # Use proper show_mesh flag
                painter.setPen(QPen(QColor(150, 255, 150), 1))
                for face in faces[:500]:  # Limit faces for performance
                    if hasattr(face, 'vertex_indices') and len(face.vertex_indices) >= 3:
                        try:
                            # Get first 3 vertices of the face
                            if len(face.vertex_indices) >= 3:
                                idx1, idx2, idx3 = face.vertex_indices[0], face.vertex_indices[1], face.vertex_indices[2]
                                if idx1 < len(vertices) and idx2 < len(vertices) and idx3 < len(vertices):
                                    v1 = vertices[idx1].position
                                    v2 = vertices[idx2].position
                                    v3 = vertices[idx3].position

                                    x1 = v1.x * scale + center_x
                                    y1 = v1.z * scale + center_z
                                    x2 = v2.x * scale + center_x
                                    y2 = v2.z * scale + center_z
                                    x3 = v3.x * scale + center_x
                                    y3 = v3.z * scale + center_z

                                    # Only draw if all points are within reasonable bounds
                                    if all(0 <= coord <= max(width, height) for coord in [x1, y1, x2, y2, x3, y3]):
                                        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                                        painter.drawLine(int(x2), int(y2), int(x3), int(y3))
                                        painter.drawLine(int(x3), int(y3), int(x1), int(y1))
                        except (IndexError, AttributeError):
                            continue

            # Draw legend with collision stats
            painter.setPen(QColor(220, 220, 220))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 20, f"Spheres: {len(spheres)}")
            painter.drawText(10, 40, f"Boxes: {len(boxes)}")
            painter.drawText(10, 60, f"Faces: {len(faces)}")
            painter.drawText(10, 80, f"Vertices: {len(vertices)}")

            painter.end()
            return pixmap

        except Exception as e:
            img_debugger.error(f"Error rendering preview: {str(e)}")
            import traceback
            traceback.print_exc()
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(60, 60, 60))
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 100, 100))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"Render Error:\n{str(e)[:50]}...")
            painter.end()
            return pixmap


# ----- Hotkeps

    def keyPressEvent(self, event): #vers 1
        """Handle keyboard shortcuts"""
        from PyQt6.QtCore import Qt

        # D key - Dock/Undock toggle
        if event.key() == Qt.Key.Key_D and not event.modifiers():
            self.toggle_dock_mode()
            event.accept()
            return

        # T key - Tear out (same as undock)
        if event.key() == Qt.Key.Key_T and not event.modifiers():
            if self.is_docked:
                self._undock_from_main()
            event.accept()
            return

        super().keyPressEvent(event)


    def _setup_hotkeys(self): #vers 3
        """Setup Plasma6-style keyboard shortcuts for this application - checks for existing methods"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        from PyQt6.QtCore import Qt

        # === FILE OPERATIONS ===

        # Open col (Ctrl+O)
        self.hotkey_open = QShortcut(QKeySequence.StandardKey.Open, self)
        if hasattr(self, 'open_col_file'):
            self.hotkey_open.activated.connect(self.open_col_file)
        elif hasattr(self, '_open_col_file'):
            self.hotkey_open.activated.connect(self._open_col_file)

        # Save col (Ctrl+S)
        self.hotkey_save = QShortcut(QKeySequence.StandardKey.Save, self)
        if hasattr(self, '_save_col_file'):
            self.hotkey_save.activated.connect(self._save_col_file)
        elif hasattr(self, 'save_col_file'):
            self.hotkey_save.activated.connect(self.save_col_file)

        # Force Save col (Alt+Shift+S)
        self.hotkey_force_save = QShortcut(QKeySequence("Alt+Shift+S"), self)
        if not hasattr(self, '_force_save_col'):
            # Create force save method inline if it doesn't exist
            def force_save():
                if not self.collision_list:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "No Collision", "No Collision to save")
                    return
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("Force save triggered (Alt+Shift+S)")
                # Call save regardless of modified state
                if hasattr(self, '_save_col_file'):
                    self._save_col_file()

            self.hotkey_force_save.activated.connect(force_save)
        else:
            self.hotkey_force_save.activated.connect(self._force_save_col)

        # Save As (Ctrl+Shift+S)
        self.hotkey_save_as = QShortcut(QKeySequence.StandardKey.SaveAs, self)
        if hasattr(self, '_save_as_col_file'):
            self.hotkey_save_as.activated.connect(self._save_as_col_file)
        elif hasattr(self, '_save_col_file'):
            self.hotkey_save_as.activated.connect(self._save_col_file)

        # Close (Ctrl+W)
        self.hotkey_close = QShortcut(QKeySequence.StandardKey.Close, self)
        self.hotkey_close.activated.connect(self.close)

        # === EDIT OPERATIONS ===

        # Undo (Ctrl+Z)
        self.hotkey_undo = QShortcut(QKeySequence.StandardKey.Undo, self)
        if hasattr(self, '_undo_last_action'):
            self.hotkey_undo.activated.connect(self._undo_last_action)
        # else: not implemented yet, no connection

        # Copy (Ctrl+C)
        self.hotkey_copy = QShortcut(QKeySequence.StandardKey.Copy, self)
        if hasattr(self, '_copy_collision'):
            self.hotkey_copy.activated.connect(self._copy_surface)


        # Paste (Ctrl+V)
        self.hotkey_paste = QShortcut(QKeySequence.StandardKey.Paste, self)
        if hasattr(self, '_paste_collision'):
            self.hotkey_paste.activated.connect(self._paste_surface)


        # Delete (Delete)
        self.hotkey_delete = QShortcut(QKeySequence.StandardKey.Delete, self)
        if hasattr(self, '_delete_collision'):
            self.hotkey_delete.activated.connect(self._delete_surface)


        # Duplicate (Ctrl+D)
        self.hotkey_duplicate = QShortcut(QKeySequence("Ctrl+D"), self)
        if hasattr(self, '_duplicate_collision'):
            self.hotkey_duplicate.activated.connect(self._duplicate_surface)


        # Rename (F2)
        self.hotkey_rename = QShortcut(QKeySequence("F2"), self)
        if not hasattr(self, '_rename_collsion_shortcut'):
            # Create rename shortcut method inline
            def rename_shortcut():
                # Focus the name input field if it exists
                if hasattr(self, 'info_name'):
                    self.info_name.setReadOnly(False)
                    self.info_name.selectAll()
                    self.info_name.setFocus()
            self.hotkey_rename.activated.connect(rename_shortcut)
        else:
            self.hotkey_rename.activated.connect(self._rename_shadow_shortcut)

        # === Collision OPERATIONS ===

        # Import Collision (Ctrl+I)
        self.hotkey_import = QShortcut(QKeySequence("Ctrl+I"), self)
        if hasattr(self, '_import_collision'):
            self.hotkey_import.activated.connect(self._import_surface)

        # Export Collision (Ctrl+E)
        self.hotkey_export = QShortcut(QKeySequence("Ctrl+E"), self)
        if hasattr(self, 'export_selected_collision'):
            self.hotkey_export.activated.connect(self.export_selected_surface)

        # Export All (Ctrl+Shift+E)
        self.hotkey_export_all = QShortcut(QKeySequence("Ctrl+Shift+E"), self)
        if hasattr(self, 'export_all_collision'):
            self.hotkey_export_all.activated.connect(self.export_all_surfaces)


        # === VIEW OPERATIONS ===

        # Refresh (F5)d_btn
        self.hotkey_refresh = QShortcut(QKeySequence.StandardKey.Refresh, self)
        if hasattr(self, '_reload_surface_table'):
            self.hotkey_refresh.activated.connect(self._reload_surface_table)
        elif hasattr(self, 'reload_surface_table'):
            self.hotkey_refresh.activated.connect(self.reload_surface_table)
        elif hasattr(self, 'refresh'):
            self.hotkey_refresh.activated.connect(self.refresh)

        # Properties (Alt+Enter)
        self.hotkey_properties = QShortcut(QKeySequence("Alt+Return"), self)
        if hasattr(self, '_show_detailed_info'):
            self.hotkey_properties.activated.connect(self._show_detailed_info)
        elif hasattr(self, '_show_surface_info'):
            self.hotkey_properties.activated.connect(self._show_surface_info)

        # Settings (Ctrl+,)
        self.hotkey_settings = QShortcut(QKeySequence.StandardKey.Preferences, self)
        if hasattr(self, '_show_settings_dialog'):
            self.hotkey_settings.activated.connect(self._show_settings_dialog)
        elif hasattr(self, 'show_settings_dialog'):
            self.hotkey_settings.activated.connect(self.show_settings_dialog)
        elif hasattr(self, '_show_settings_hotkeys'):
            self.hotkey_settings.activated.connect(self._show_settings_hotkeys)

        # === NAVIGATION ===

        # Select All (Ctrl+A) - reserved for future
        self.hotkey_select_all = QShortcut(QKeySequence.StandardKey.SelectAll, self)
        # Not connected - reserved for future multi-select

        # Find (Ctrl+F)
        self.hotkey_find = QShortcut(QKeySequence.StandardKey.Find, self)
        if not hasattr(self, '_focus_search'):
            # Create focus search method inline
            def focus_search():
                if hasattr(self, 'search_input'):
                    self.search_input.setFocus()
                    self.search_input.selectAll()
            self.hotkey_find.activated.connect(focus_search)
        else:
            self.hotkey_find.activated.connect(self._focus_search)

        # === HELP ===

        # Help (F1)
        self.hotkey_help = QShortcut(QKeySequence.StandardKey.HelpContents, self)

        if hasattr(self, 'show_help'):
            self.hotkey_help.activated.connect(self.show_help)

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("Hotkeys initialized (Plasma6 standard)")


    def _reset_hotkeys_to_defaults(self, parent_dialog): #vers 1
        """Reset all hotkeys to Plasma6 defaults"""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtGui import QKeySequence

        reply = QMessageBox.question(parent_dialog, "Reset Hotkeys",
            "Reset all keyboard shortcuts to Plasma6 defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.hotkey_edit_open.setKeySequence(QKeySequence.StandardKey.Open)
            self.hotkey_edit_save.setKeySequence(QKeySequence.StandardKey.Save)
            self.hotkey_edit_force_save.setKeySequence(QKeySequence("Alt+Shift+S"))
            self.hotkey_edit_save_as.setKeySequence(QKeySequence.StandardKey.SaveAs)
            self.hotkey_edit_close.setKeySequence(QKeySequence.StandardKey.Close)
            self.hotkey_edit_undo.setKeySequence(QKeySequence.StandardKey.Undo)
            self.hotkey_edit_copy.setKeySequence(QKeySequence.StandardKey.Copy)
            self.hotkey_edit_paste.setKeySequence(QKeySequence.StandardKey.Paste)
            self.hotkey_edit_delete.setKeySequence(QKeySequence.StandardKey.Delete)
            self.hotkey_edit_duplicate.setKeySequence(QKeySequence("Ctrl+D"))
            self.hotkey_edit_rename.setKeySequence(QKeySequence("F2"))
            self.hotkey_edit_import.setKeySequence(QKeySequence("Ctrl+I"))
            self.hotkey_edit_export.setKeySequence(QKeySequence("Ctrl+E"))
            self.hotkey_edit_export_all.setKeySequence(QKeySequence("Ctrl+Shift+E"))
            self.hotkey_edit_refresh.setKeySequence(QKeySequence.StandardKey.Refresh)
            self.hotkey_edit_properties.setKeySequence(QKeySequence("Alt+Return"))
            self.hotkey_edit_find.setKeySequence(QKeySequence.StandardKey.Find)
            self.hotkey_edit_help.setKeySequence(QKeySequence.StandardKey.HelpContents)


    def _apply_hotkey_settings(self, dialog, close=False): #vers 1
        """Apply hotkey changes"""
        # Update all hotkeys with new sequences
        self.hotkey_open.setKey(self.hotkey_edit_open.keySequence())
        self.hotkey_save.setKey(self.hotkey_edit_save.keySequence())
        self.hotkey_force_save.setKey(self.hotkey_edit_force_save.keySequence())
        self.hotkey_save_as.setKey(self.hotkey_edit_save_as.keySequence())
        self.hotkey_close.setKey(self.hotkey_edit_close.keySequence())
        self.hotkey_undo.setKey(self.hotkey_edit_undo.keySequence())
        self.hotkey_copy.setKey(self.hotkey_edit_copy.keySequence())
        self.hotkey_paste.setKey(self.hotkey_edit_paste.keySequence())
        self.hotkey_delete.setKey(self.hotkey_edit_delete.keySequence())
        self.hotkey_duplicate.setKey(self.hotkey_edit_duplicate.keySequence())
        self.hotkey_rename.setKey(self.hotkey_edit_rename.keySequence())
        self.hotkey_import.setKey(self.hotkey_edit_import.keySequence())
        self.hotkey_export.setKey(self.hotkey_edit_export.keySequence())
        self.hotkey_export_all.setKey(self.hotkey_edit_export_all.keySequence())
        self.hotkey_refresh.setKey(self.hotkey_edit_refresh.keySequence())
        self.hotkey_properties.setKey(self.hotkey_edit_properties.keySequence())
        self.hotkey_find.setKey(self.hotkey_edit_find.keySequence())
        self.hotkey_help.setKey(self.hotkey_edit_help.keySequence())

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("Hotkeys updated")

        # TODO: Save to config file for persistence

        if close:
            dialog.accept()


    def _show_settings_hotkeys(self): #vers 1
        """Show settings dialog with hotkey customization"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                    QWidget, QLabel, QLineEdit, QPushButton,
                                    QGroupBox, QFormLayout, QKeySequenceEdit)
        from PyQt6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle(App_name + " Settings")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)

        layout = QVBoxLayout(dialog)

        # Create tabs
        tabs = QTabWidget()

        # === HOTKEYS TAB ===
        hotkeys_tab = QWidget()
        hotkeys_layout = QVBoxLayout(hotkeys_tab)

        # File Operations Group
        file_group = QGroupBox("File Operations")
        file_form = QFormLayout()

        self.hotkey_edit_open = QKeySequenceEdit(self.hotkey_open.key())
        file_form.addRow("Open col:", self.hotkey_edit_open)

        self.hotkey_edit_save = QKeySequenceEdit(self.hotkey_save.key())
        file_form.addRow("Save col:", self.hotkey_edit_save)

        self.hotkey_edit_force_save = QKeySequenceEdit(self.hotkey_force_save.key())
        force_save_layout = QHBoxLayout()
        force_save_layout.addWidget(self.hotkey_edit_force_save)
        force_save_hint = QLabel("(Force save even if unmodified)")
        force_save_hint.setStyleSheet("color: #888; font-style: italic;")
        force_save_layout.addWidget(force_save_hint)
        file_form.addRow("Force Save:", force_save_layout)

        self.hotkey_edit_save_as = QKeySequenceEdit(self.hotkey_save_as.key())
        file_form.addRow("Save As:", self.hotkey_edit_save_as)

        self.hotkey_edit_close = QKeySequenceEdit(self.hotkey_close.key())
        file_form.addRow("Close:", self.hotkey_edit_close)

        file_group.setLayout(file_form)
        hotkeys_layout.addWidget(file_group)

        # Edit Operations Group
        edit_group = QGroupBox("Edit Operations")
        edit_form = QFormLayout()

        self.hotkey_edit_undo = QKeySequenceEdit(self.hotkey_undo.key())
        edit_form.addRow("Undo:", self.hotkey_edit_undo)

        self.hotkey_edit_copy = QKeySequenceEdit(self.hotkey_copy.key())
        edit_form.addRow("Copy Collision:", self.hotkey_edit_copy)

        self.hotkey_edit_paste = QKeySequenceEdit(self.hotkey_paste.key())
        edit_form.addRow("Paste Collision:", self.hotkey_edit_paste)

        self.hotkey_edit_delete = QKeySequenceEdit(self.hotkey_delete.key())
        edit_form.addRow("Delete:", self.hotkey_edit_delete)

        self.hotkey_edit_duplicate = QKeySequenceEdit(self.hotkey_duplicate.key())
        edit_form.addRow("Duplicate:", self.hotkey_edit_duplicate)

        self.hotkey_edit_rename = QKeySequenceEdit(self.hotkey_rename.key())
        edit_form.addRow("Rename:", self.hotkey_edit_rename)

        edit_group.setLayout(edit_form)
        hotkeys_layout.addWidget(edit_group)

        # Collision Group
        coll_group = QGroupBox("Collision Operations")
        coll_form = QFormLayout()

        self.hotkey_edit_import = QKeySequenceEdit(self.hotkey_import.key())
        coll_form.addRow("Import Collision:", self.hotkey_edit_import)

        self.hotkey_edit_export = QKeySequenceEdit(self.hotkey_export.key())
        coll_form.addRow("Export Collision:", self.hotkey_edit_export)

        self.hotkey_edit_export_all = QKeySequenceEdit(self.hotkey_export_all.key())
        coll_form.addRow("Export All:", self.hotkey_edit_export_all)

        coll_group.setLayout(coll_form)
        hotkeys_layout.addWidget(coll_group)

        # View Operations Group
        view_group = QGroupBox("View Operations")
        view_form = QFormLayout()

        self.hotkey_edit_refresh = QKeySequenceEdit(self.hotkey_refresh.key())
        view_form.addRow("Refresh:", self.hotkey_edit_refresh)

        self.hotkey_edit_properties = QKeySequenceEdit(self.hotkey_properties.key())
        view_form.addRow("Properties:", self.hotkey_edit_properties)

        self.hotkey_edit_find = QKeySequenceEdit(self.hotkey_find.key())
        view_form.addRow("Find/Search:", self.hotkey_edit_find)

        self.hotkey_edit_help = QKeySequenceEdit(self.hotkey_help.key())
        view_form.addRow("Help:", self.hotkey_edit_help)

        view_group.setLayout(view_form)
        hotkeys_layout.addWidget(view_group)

        hotkeys_layout.addStretch()

        # Reset to defaults button
        reset_hotkeys_btn = QPushButton("Reset to Plasma6 Defaults")
        reset_hotkeys_btn.clicked.connect(lambda: self._reset_hotkeys_to_defaults(dialog))
        hotkeys_layout.addWidget(reset_hotkeys_btn)

        tabs.addTab(hotkeys_tab, "Keyboard Shortcuts")

        # === GENERAL TAB (for future settings) ===
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        placeholder_label = QLabel("Additional settings will appear here in future versions.")
        placeholder_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        general_layout.addWidget(placeholder_label)
        general_layout.addStretch()

        tabs.addTab(general_tab, "General")

        layout.addWidget(tabs)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self._apply_hotkey_settings(dialog))
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(lambda: self._apply_hotkey_settings(dialog, close=True))
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _ensure_depends_structure(self): #vers 1
        """Ensure depends/ folder exists in standalone mode with required files"""
        if not self.standalone_mode:
            return

        script_dir = Path(__file__).parent.resolve()
        depends_dir = script_dir / "depends"

        # Create depends folder if it doesn't exist
        if not depends_dir.exists():
            depends_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created depends directory: {depends_dir}")

        # Check for required import modules
        required_modules = [
            'col_core_classes.py',
            'col_dialogs.py',
            'img_debug_functions.py'
        ]

        missing = []
        for module in required_modules:
            module_path = depends_dir / module
            if not module_path.exists():
                missing.append(module)

        if missing:
            print(f"Warning: Missing modules in depends/: {', '.join(missing)}")
            print(f"Copy these from apps.methods. to: {depends_dir}")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f" Missing import modules: {', '.join(missing)}")


    def _show_col_info(self): #vers 4
        """Show TXD Workshop information dialog - About and capabilities"""
        dialog = QDialog(self)
        dialog.setWindowTitle("About COL Workshop")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        # Header
        header = QLabel("COL Workshop for IMG Factory 1.5")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Author info
        author_label = QLabel("Author: X-Seti")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)

        # Version info
        version_label = QLabel("Version: 1.5 - October 2025")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addWidget(QLabel(""))  # Spacer

        # Capabilities section
        capabilities = QTextEdit()
        capabilities.setReadOnly(True)
        capabilities.setMaximumHeight(350)

        info_text = """<b>COL Workshop Capabilities:</b><br><br>

<b>✓ File Operations:</b><br>


<b>✓ Collision Viewing & Editing:</b><br>


<b>✓ Collision Management:</b><br>


<b>✓ Collision Surface Painting:</b><br>


<b>✓ Format Support:</b><br>


<b>✓ Advanced Features:</b><br>"""

        # Add format support dynamically
        formats_available = []

        # Standard formats (always via PIL)

        info_text += "<br>".join(formats_available)
        info_text += "<br><br>"

        # Settings info
        info_text += """<b>✓ Customization:</b><br>
- Adjustable texture name length (8-64 chars)<br>
- Button display modes (Icons/Text/Both)<br>
- Font customization<br>
- Preview zoom and pan offsets<br><br>

<b>Keyboard Shortcuts:</b><br>
- Ctrl+O: Open COL<br>
- Ctrl+S: Save COL<br>
- Ctrl+I: Import Collision col, cst, 3ds<br>
- Ctrl+E: Export Selected col, cst, 3ds<br>
- Ctrl+Z: Undo<br>
- Delete: Remove Collision<br>
- Ctrl+D: Duplicate Collision<br>"""

        capabilities.setHtml(info_text)
        layout.addWidget(capabilities)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setDefault(True)
        layout.addWidget(close_btn)

        dialog.exec()


#class SvgIcons: #vers 1 - Once functions are updated this class will be moved to the bottom
    """SVG icon data to QIcon with theme color support"""


    def _create_bitdepth_icon(self): #vers 3
        """Create bit depth icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M3,5H9V11H3V5M5,7V9H7V7H5M11,7H21V9H11V7M11,15H21V17H11V15M5,20L1.5,16.5L2.91,15.09L5,17.17L9.59,12.59L11,14L5,20Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_resize_icon(self): #vers 2
        """Create resize icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M10,21V19H6.41L10.91,14.5L9.5,13.09L5,17.59V14H3V21H10M14.5,10.91L19,6.41V10H21V3H14V5H17.59L13.09,9.5L14.5,10.91Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_warning_icon_svg(self): #vers 1
        """Create SVG warning icon for table display"""
        svg_data = b"""
        <svg width="16" height="16" viewBox="0 0 16 16">
            <path fill="#FFA500" d="M8 1l7 13H1z"/>
            <text x="8" y="12" font-size="10" fill="black" text-anchor="middle">!</text>
        </svg>
        """
        return QIcon(QPixmap.fromImage(
            QImage.fromData(QByteArray(svg_data))
        ))


    def _create_resize_icon2(self): #vers 1
        """Resize grip icon - diagonal arrows"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 6l-8 8M10 6h4v4M6 14v-4h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_upscale_icon(self): #vers 3
        """Create AI upscale icon - brain/intelligence style"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Brain outline -->
            <path d="M12 3 C8 3 5 6 5 9 C5 10 5.5 11 6 12 C5.5 13 5 14 5 15 C5 18 8 21 12 21 C16 21 19 18 19 15 C19 14 18.5 13 18 12 C18.5 11 19 10 19 9 C19 6 16 3 12 3 Z"
                fill="none" stroke="currentColor" stroke-width="1.5"/>

            <!-- Neural pathways inside -->
            <path d="M9 8 L10 10 M14 8 L13 10 M10 12 L14 12 M9 14 L12 16 M15 14 L12 16"
                stroke="currentColor" stroke-width="1" fill="none"/>

            <!-- Upward indicator -->
            <path d="M19 8 L19 4 M17 6 L19 4 L21 6"
                stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_upscale_icon(self): #vers 3
        """Create AI upscale icon - sparkle/magic AI style"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Large sparkle -->
            <path d="M12 2 L13 8 L12 14 L11 8 Z M8 12 L2 11 L8 10 L14 11 Z"
                fill="currentColor"/>

            <!-- Small sparkles -->
            <circle cx="18" cy="6" r="1.5" fill="currentColor"/>
            <circle cx="6" cy="18" r="1.5" fill="currentColor"/>
            <circle cx="19" cy="16" r="1" fill="currentColor"/>

            <!-- Upward arrow -->
            <path d="M16 20 L20 20 M18 18 L18 22"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_upscale_icon(self): #vers 3
        """Create AI upscale icon - neural network style"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Neural network nodes -->
            <circle cx="6" cy="6" r="2" fill="currentColor"/>
            <circle cx="18" cy="6" r="2" fill="currentColor"/>
            <circle cx="6" cy="18" r="2" fill="currentColor"/>
            <circle cx="18" cy="18" r="2" fill="currentColor"/>
            <circle cx="12" cy="12" r="2.5" fill="currentColor"/>

            <!-- Connecting lines -->
            <path d="M7.5 7.5 L10.5 10.5 M13.5 10.5 L16.5 7.5 M7.5 16.5 L10.5 13.5 M13.5 13.5 L16.5 16.5"
                stroke="currentColor" stroke-width="1.5" fill="none"/>

            <!-- Upward arrow overlay -->
            <path d="M12 3 L12 9 M9 6 L12 3 L15 6"
                stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_manage_icon(self): #vers 1
        """Create manage/settings icon for bumpmap manager"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <!-- Gear/cog icon for management -->
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_paint_icon(self): #vers 1
        """Create paint brush icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M20.71 7.04c.39-.39.39-1.04 0-1.41l-2.34-2.34c-.37-.39-1.02-.39-1.41 0l-1.84 1.83 3.75 3.75M3 17.25V21h3.75L17.81 9.93l-3.75-3.75L3 17.25z"
                fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_compress_icon(self): #vers 2
        """Create compress icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M4,2H20V4H13V10H20V12H4V10H11V4H4V2M4,13H20V15H13V21H20V23H4V21H11V15H4V13Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_build_icon(self): #vers 1
        """Create build/construct icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M22,9 L12,2 L2,9 L12,16 L22,9 Z M12,18 L4,13 L4,19 L12,24 L20,19 L20,13 L12,18 Z"
                fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_uncompress_icon(self): #vers 2
        """Create uncompress icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M11,4V2H13V4H11M13,21V19H11V21H13M4,12V10H20V12H4Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_view_icon(self): #vers 2
        """Create view/eye icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9
                    M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17
                    M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5
                    C17,19.5 21.27,16.39 23,12
                    C21.27,7.61 17,4.5 12,4.5Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_add_icon(self): #vers 2
        """Create add/plus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_delete_icon(self): #vers 2
        """Create delete/minus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H5V11H19V13Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_color_picker_icon(self): #vers 1
        """Color picker icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="2"/>
            <path d="M10 3v4M10 13v4M3 10h4M13 10h4" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_zoom_in_icon(self): #vers 1
        """Zoom in icon (+)"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2"/>
            <path d="M8 5v6M5 8h6" stroke="currentColor" stroke-width="2"/>
            <path d="M13 13l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_zoom_out_icon(self): #vers 1
        """Zoom out icon (-)"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2"/>
            <path d="M5 8h6" stroke="currentColor" stroke-width="2"/>
            <path d="M13 13l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_reset_icon(self): #vers 1
        """Reset/1:1 icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 10A6 6 0 1 1 4 10M4 10l3-3m-3 3l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_fit_icon(self): #vers 1
        """Fit to window icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_arrow_up_icon(self): #vers 1
        """Arrow up"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 3v10M4 7l4-4 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)


    def _create_arrow_down_icon(self): #vers 1
        """Arrow down"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 13V3M12 9l-4 4-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)


    def _create_arrow_left_icon(self): #vers 1
        """Arrow left"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8h10M7 4L3 8l4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)


    def _create_arrow_right_icon(self): #vers 1
        """Arrow right"""
        svg_data = b'''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 8H3M9 12l4-4-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=16)


    def _create_flip_vert_icon(self): #vers 1
        """Create vertical flip SVG icon"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12h18M8 7l-4 5 4 5M16 7l4 5-4 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_flip_horz_icon(self): #vers 1
        """Create horizontal flip SVG icon"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 3v18M7 8l5-4 5 4M7 16l5 4 5-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_rotate_cw_icon(self): #vers 1
        """Create clockwise rotation SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12a9 9 0 11-9-9v6M21 3l-3 6-6-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_rotate_ccw_icon(self): #vers 1
        """Create counter-clockwise rotation SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12a9 9 0 109-9v6M3 3l3 6 6-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_copy_icon(self): #vers 1
        """Create copy SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_paste_icon(self): #vers 1
        """Create paste SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2" stroke="currentColor" stroke-width="2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_edit_icon(self): #vers 1
        """Create edit SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_convert_icon(self): #vers 1
        """Create convert SVG icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12h18M3 12l4-4M3 12l4 4M21 12l-4-4M21 12l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
        </svg>'''

        return self._svg_to_icon(svg_data)


    def _create_undo_icon(self): #vers 2
        """Undo - Curved arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_info_icon(self): #vers 1
        """Info - circle with 'i' icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 11v6M12 8v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_folder_icon(self): #vers 1
        """Open IMG - Folder icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-7l-2-2H5a2 2 0 00-2 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_file_icon(self): #vers 1
        """Open col - File icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_open_icon(self): #vers 1
        """Open - Folder icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v13a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_save_icon(self): #vers 1
        """Save col - Floppy disk icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2"/>
            <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_import_icon(self): #vers 1
        """Import - Download/Import icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_export_icon(self): #vers 1
        """Export - Upload/Export icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_saveas_icon(self): #vers 1
        """Save - Floppy disk icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 21 17 13 7 13 7 21"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 3 7 8 15 8"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_analyze_icon(self): #vers 1
        """Analyze - Bar chart icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="18" y1="20" x2="18" y2="10"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="12" y1="20" x2="12" y2="4"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="6" y1="20" x2="6" y2="14"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_sphere_icon(self): #vers 1
        """Sphere - Circle icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10"
                stroke="currentColor" stroke-width="2"
                fill="none"/>
            <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"
                stroke="currentColor" stroke-width="2"
                fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_box_icon(self): #vers 1
        """Box - Cube icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="22.08" x2="12" y2="12"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_mesh_icon(self): #vers 1
        """Mesh - Grid/wireframe icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="3" y1="9" x2="21" y2="9"
                stroke="currentColor" stroke-width="2"/>
            <line x1="3" y1="15" x2="21" y2="15"
                stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="3" x2="9" y2="21"
                stroke="currentColor" stroke-width="2"/>
            <line x1="15" y1="3" x2="15" y2="21"
                stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_package_icon(self): #vers 1
        """Export All - Package/Box icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" stroke="currentColor" stroke-width="2"/>
            <path d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_properties_icon(self): #vers 1
        """Properties - Info/Details icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 16v-4M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    # CONTEXT MENU ICONS

    def _create_plus_icon(self): #vers 1
        """Create New Entry - Plus icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_document_icon(self): #vers 1
        """Create New col - Document icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_add_icon(self): #vers 1
        """Add/plus icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4v12M4 10h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_trash_icon(self): #vers 1
        """Delete/trash icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5h14M8 5V3h4v2M6 5v11a1 1 0 001 1h6a1 1 0 001-1V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_delete_icon(self): #vers 1
        """Delete/trash icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5h14M8 5V3h4v2M6 5v11a1 1 0 001 1h6a1 1 0 001-1V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_duplicate_icon(self): #vers 1
        """Duplicate/copy icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="6" width="10" height="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M4 4h8v2H6v8H4V4z" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_create_icon(self): #vers 1
        """Create/new icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4v12M4 10h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_filter_icon(self): #vers 1
        """Filter/sliders icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_pencil_icon(self): #vers 1
        """Edit - Pencil icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 3a2.83 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_trash_icon(self): #vers 1
        """Delete - Trash icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_check_icon(self): #vers 2
        """Create check/verify icon - document with checkmark"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
                fill="none" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M9 13l2 2 4-4"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_eye_icon(self): #vers 1
        """View - Eye icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_list_icon(self): #vers 1
        """Properties List - List icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    # WINDOW CONTROL ICONS

    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_maximize_icon(self): #vers 1
        """Maximize - Square"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokea-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_settings_icon(self): #vers 1
        """Settings/gear icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_maximize_icon(self): #vers 1
        """Maximize - Square icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="6" y1="6" x2="18" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="18" y1="6" x2="6" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_add_icon(self): #vers 1
        """Add - Plus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="12" y1="5" x2="12" y2="19"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_delete_icon(self): #vers 1
        """Delete - Trash icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_import_icon(self): #vers 1
        """Import - Download arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_export_icon(self): #vers 1
        """Export - Upload arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_checkerboard_icon(self): #vers 1
        """Create checkerboard pattern icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="5" height="5" fill="currentColor"/>
            <rect x="5" y="5" width="5" height="5" fill="currentColor"/>
            <rect x="10" y="0" width="5" height="5" fill="currentColor"/>
            <rect x="15" y="5" width="5" height="5" fill="currentColor"/>
            <rect x="0" y="10" width="5" height="5" fill="currentColor"/>
            <rect x="5" y="15" width="5" height="5" fill="currentColor"/>
            <rect x="10" y="10" width="5" height="5" fill="currentColor"/>
            <rect x="15" y="15" width="5" height="5" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_undo_icon(self): #vers 2
        """Undo - Curved arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _svg_to_icon(self, svg_data, size=24): #vers 2
        """Convert SVG data to QIcon with theme color support"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray

        try:
            # Get current text color from palette
            text_color = self.palette().color(self.foregroundRole())

            # Replace currentColor with actual color
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', text_color.name())
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except:
            # Fallback to no icon if SVG fails
            return QIcon()



class ZoomablePreview(QLabel): #vers 2
    """Fixed preview widget with zoom and pan"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setMinimumSize(400, 400)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.setStyleSheet("border: 2px solid #3a3a3a; background: #0a0a0a;")
        self.setStyleSheet("border: 1px solid #3a3a3a;")
        self.setMouseTracking(True)

        # Display state
        self.current_model = None
        self.original_pixmap = None
        self.scaled_pixmap = None

        # View controls
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.rotation_x = 45  # X-axis rotation (up/down tilt)
        self.rotation_y = 0   # Y-axis rotation (left/right spin)
        self.rotation_z = 0   # Z-axis rotation (roll)

        # View toggles
        self.show_spheres = True
        self.show_boxes = True
        self.show_mesh = True

        # Mouse interaction
        self.dragging = False
        self.drag_start = QPoint(0, 0)
        self.drag_mode = None  # 'pan' or 'rotate'

        # Background
        self.bg_color = QColor(42, 42, 42)

        self.placeholder_text = "Select a collision model to preview"

        self.background_mode = 'solid'
        self._checkerboard_size = 16


    def setPixmap(self, pixmap): #vers 2
        """Set pixmap and update display"""
        if pixmap and not pixmap.isNull():
            self.original_pixmap = pixmap
            self.placeholder_text = None
            self._update_scaled_pixmap()
        else:
            self.original_pixmap = None
            self.scaled_pixmap = None
            self.placeholder_text = "No texture loaded"

        self.update()  # Trigger repaint


    def set_model(self, model): #vers 1
        """Set collision model to display"""
        self.current_model = model
        self.render_collision()


    def render_collision(self): #vers 2
        """Render the collision model with current view settings"""
        if not self.current_model:
            self.setText(self.placeholder_text)
            self.original_pixmap = None
            self.scaled_pixmap = None
            return

        width = max(400, self.width())
        height = max(400, self.height())

        # Use the parent's render method
        if hasattr(self.parent(), '_render_collision_preview'):
            self.original_pixmap = self.parent()._render_collision_preview(
                self.current_model,
                width,
                height
            )
        else:
            # Fallback - just show text for now
            name = getattr(self.current_model, 'name', 'Unknown')
            self.setText(f"Collision Model: {name}\n\nRendering...")
            return

        self._update_scaled_pixmap()
        self.update()


    def _update_scaled_pixmap(self): #vers
        """Update scaled pixmap based on zoom"""
        if not self.original_pixmap:
            self.scaled_pixmap = None
            return

        scaled_width = int(self.original_pixmap.width() * self.zoom_level)
        scaled_height = int(self.original_pixmap.height() * self.zoom_level)

        self.scaled_pixmap = self.original_pixmap.scaled(
            scaled_width, scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )


    def paintEvent(self, event): #vers 2
        """Paint the preview with background and image"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Draw background
        if self.background_mode == 'checkerboard':
            self._draw_checkerboard(painter)
        else:
            painter.fillRect(self.rect(), self.bg_color)

        # Draw image if available
        if self.scaled_pixmap and not self.scaled_pixmap.isNull():
            # Calculate centered position with pan offset
            x = (self.width() - self.scaled_pixmap.width()) // 2 + self.pan_offset.x()
            y = (self.height() - self.scaled_pixmap.height()) // 2 + self.pan_offset.y()
            painter.drawPixmap(x, y, self.scaled_pixmap)
        elif self.placeholder_text:
            # Draw placeholder text
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.placeholder_text)


    def set_checkerboard_background(self): #vers 1
        """Enable checkerboard background"""
        self.background_mode = 'checkerboard'
        self.update()


    def set_background_color(self, color): #vers 1
        """Set solid background color"""
        self.background_mode = 'solid'
        self.bg_color = color
        self.update()


    def _draw_checkerboard(self, painter): #vers 1
        """Draw checkerboard background pattern"""
        size = self._checkerboard_size
        color1 = QColor(200, 200, 200)
        color2 = QColor(150, 150, 150)

        for y in range(0, self.height(), size):
            for x in range(0, self.width(), size):
                color = color1 if ((x // size) + (y // size)) % 2 == 0 else color2
                painter.fillRect(x, y, size, size, color)


    # Zoom controls
    def zoom_in(self): #vers 1
        """Zoom in"""
        self.zoom_level = min(5.0, self.zoom_level * 1.2)
        self._update_scaled_pixmap()
        self.update()


    def zoom_out(self): #vers 1
        """Zoom out"""
        self.zoom_level = max(0.1, self.zoom_level / 1.2)
        self._update_scaled_pixmap()
        self.update()


    def reset_view(self): #vers 1
        """Reset to default view"""
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.rotation_x = 45
        self.rotation_y = 0
        self.rotation_z = 0
        self.render_collision()


    def fit_to_window(self): #vers 2
        """Fit image to window size"""
        if not self.original_pixmap:
            return

        img_size = self.original_pixmap.size()
        widget_size = self.size()

        zoom_w = widget_size.width() / img_size.width()
        zoom_h = widget_size.height() / img_size.height()

        self.zoom_level = min(zoom_w, zoom_h) * 0.95
        self.pan_offset = QPoint(0, 0)
        self._update_scaled_pixmap()
        self.update()


    def pan(self, dx, dy): #vers 1
        """Pan the view by dx, dy pixels"""
        self.pan_offset += QPoint(dx, dy)
        self.update()


    # Rotation controls
    def rotate_x(self, degrees): #vers 1
        """Rotate around X axis"""
        self.rotation_x = (self.rotation_x + degrees) % 360
        self.render_collision()


    def rotate_y(self, degrees): #vers 1
        """Rotate around Y axis"""
        self.rotation_y = (self.rotation_y + degrees) % 360
        self.render_collision()


    def rotate_z(self, degrees): #vers 1
        """Rotate around Z axis"""
        self.rotation_z = (self.rotation_z + degrees) % 360
        self.render_collision()


    # Mouse events
    def mousePressEvent(self, event): #vers 1
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.drag_mode = 'rotate' if event.modifiers() & Qt.KeyboardModifier.ControlModifier else 'pan'


    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse drag"""
        if self.dragging:
            delta = event.pos() - self.drag_start

            if self.drag_mode == 'rotate':
                # Rotate based on drag
                self.rotate_y(delta.x() * 0.5)
                self.rotate_x(-delta.y() * 0.5)
            else:
                # Pan
                self.pan_offset += delta
                self.update()

            self.drag_start = event.pos()


    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_mode = None


    def wheelEvent(self, event): #vers 1
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()


class COLEditorDialog(QDialog): #vers 3
    """Enhanced COL Editor Dialog"""


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(App_name + " - IMG Factory 1.5")
        self.setModal(False)  # Allow non-modal operation
        self.resize(1000, 700)

        self.current_file = None
        self.current_model = None
        self.file_path = None
        self.is_modified = False

        self.setup_ui()
        self.connect_signals()

        img_debugger.debug(App_name + " dialog created")


    def setup_ui(self): #vers 1
        """Setup editor UI"""
        layout = QVBoxLayout(self)

        # Toolbar
        #self.toolbar = COLToolbar(self)
        #layout.addWidget(self.toolbar)

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

        if VIEWPORT_AVAILABLE:
            self.viewer_3d = COL3DViewport()
            viewer_layout.addWidget(self.viewer_3d)

            # Add 3DS Max style controls at bottom
            controls = self._create_viewport_controls()
            viewer_layout.addWidget(controls)
        else:
            self.viewer_3d = QLabel("3D Viewport unavailable\nInstall: pip install PyOpenGL")
            self.viewer_3d.setAlignment(Qt.AlignmentFlag.AlignCenter)
            viewer_layout.addWidget(self.viewer_3d)

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

            # Import locally when needed
            from apps.methods.col_operations import get_col_detailed_analysis
            from gui.col_dialogs import show_col_analysis_dialog

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


    def _create_viewport_controls(self): #vers 1
        """Create 3D viewport controls - 3DS Max style toolbar at bottom"""
        if not VIEWPORT_AVAILABLE:
            return QWidget()

        controls_widget = QFrame()
        controls_widget.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        controls_widget.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 2px;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #888888;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:checked {
                background-color: #006699;
                border: 1px solid #0088cc;
            }
        """)

        layout = QHBoxLayout(controls_widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        # View mode buttons
        btn_spheres = QPushButton()
        btn_spheres.setIcon(self._create_sphere_icon())
        btn_spheres.setCheckable(True)
        btn_spheres.setChecked(True)
        btn_spheres.setToolTip("Toggle Spheres")
        btn_spheres.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_spheres=checked)
        )

        btn_boxes = QPushButton()
        btn_boxes.setIcon(self._create_box_icon())
        btn_boxes.setCheckable(True)
        btn_boxes.setChecked(True)
        btn_boxes.setToolTip("Toggle Boxes")
        btn_boxes.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_boxes=checked)
        )

        btn_mesh = QPushButton()
        btn_mesh.setIcon(self._create_mesh_icon())
        btn_mesh.setCheckable(True)
        btn_mesh.setChecked(True)
        btn_mesh.setToolTip("Toggle Mesh")
        btn_mesh.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_mesh=checked)
        )

        btn_wireframe = QPushButton()
        btn_wireframe.setIcon(self._create_wireframe_icon())
        btn_wireframe.setCheckable(True)
        btn_wireframe.setChecked(True)
        btn_wireframe.setToolTip("Toggle Wireframe")
        btn_wireframe.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_wireframe=checked)
        )

        btn_bounds = QPushButton()
        btn_bounds.setIcon(self._create_bounds_icon())
        btn_bounds.setCheckable(True)
        btn_bounds.setChecked(True)
        btn_bounds.setToolTip("Toggle Bounding Box")
        btn_bounds.toggled.connect(
            lambda checked: self.viewer_3d.set_view_options(show_bounds=checked)
        )

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setStyleSheet("color: #666666;")

        # Camera controls
        btn_reset = QPushButton()
        btn_reset.setIcon(self._create_reset_view_icon())
        btn_reset.setToolTip("Reset View")
        btn_reset.clicked.connect(self.viewer_3d.reset_view)

        btn_top = QPushButton("T")
        btn_top.setToolTip("Top View")
        btn_top.clicked.connect(lambda: self._set_camera_view('top'))

        btn_front = QPushButton("F")
        btn_front.setToolTip("Front View")
        btn_front.clicked.connect(lambda: self._set_camera_view('front'))

        btn_side = QPushButton("S")
        btn_side.setToolTip("Side View")
        btn_side.clicked.connect(lambda: self._set_camera_view('side'))

        # Add widgets to layout
        layout.addWidget(btn_spheres)
        layout.addWidget(btn_boxes)
        layout.addWidget(btn_mesh)
        layout.addWidget(btn_wireframe)
        layout.addWidget(btn_bounds)
        layout.addWidget(separator1)
        layout.addWidget(btn_reset)
        layout.addWidget(btn_top)
        layout.addWidget(btn_front)
        layout.addWidget(btn_side)
        layout.addStretch()

        return controls_widget


    def _create_sphere_icon(self): #vers 1
        """Sphere collision icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="2" fill="none"/>
            <ellipse cx="10" cy="10" rx="7" ry="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M3 10 Q10 13 17 10" stroke="currentColor" stroke-width="1.5" fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_box_icon(self): #vers 1
        """Box collision icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6 L10 3 L16 6 L16 14 L10 17 L4 14 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M4 6 L10 9 L16 6" stroke="currentColor" stroke-width="2"/>
            <path d="M10 9 L10 17" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_mesh_icon(self): #vers 1
        """Mesh collision icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 10 L10 3 L17 10 L10 17 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M3 10 L17 10 M10 3 L10 17" stroke="currentColor" stroke-width="1.5"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_wireframe_icon(self): #vers 1
        """Wireframe mode icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 5 L15 5 L15 15 L5 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M5 10 L15 10 M10 5 L10 15" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="5" cy="5" r="1.5" fill="currentColor"/>
            <circle cx="15" cy="5" r="1.5" fill="currentColor"/>
            <circle cx="15" cy="15" r="1.5" fill="currentColor"/>
            <circle cx="5" cy="15" r="1.5" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_bounds_icon(self): #vers 1
        """Bounding box icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="3,2"/>
            <path d="M3 3 L7 3 M17 3 L13 3 M3 17 L7 17 M17 17 L13 17 M3 3 L3 7 M3 17 L3 13 M17 3 L17 7 M17 17 L17 13" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_reset_view_icon(self): #vers 1
        """Reset camera view icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 10A6 6 0 1 1 4 10M4 10l3-3m-3 3l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _set_camera_view(self, view_type): #vers 1
        """Set predefined camera view"""
        if not VIEWPORT_AVAILABLE or not hasattr(self, 'viewer_3d'):
            return

        if view_type == 'top':
            self.viewer_3d.rotation_x = 0.0
            self.viewer_3d.rotation_y = 0.0
        elif view_type == 'front':
            self.viewer_3d.rotation_x = 90.0
            self.viewer_3d.rotation_y = 0.0
        elif view_type == 'side':
            self.viewer_3d.rotation_x = 90.0
            self.viewer_3d.rotation_y = 90.0

        self.viewer_3d.update()


    def _svg_to_icon(self, svg_data, size=24): #vers 1
        """Convert SVG to QIcon"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray

        try:
            text_color = self.palette().color(self.foregroundRole())
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', text_color.name())
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except:
            return QIcon()


    def on_property_changed(self, property_name: str, new_value): #vers 2
        """Handle property changes from properties widget"""
        try:
            if not self.current_file or not hasattr(self.current_file, 'models'):
                return

            selected_index = self.model_list.currentRow()
            if selected_index < 0 or selected_index >= len(self.current_file.models):
                return

            current_model = self.current_file.models[selected_index]

            # Update model properties
            if property_name == 'name':
                current_model.name = str(new_value)
                self.model_list.item(selected_index).setText(new_value)
            elif property_name == 'version':
                current_model.version = new_value
            elif property_name == 'material':
                if hasattr(current_model, 'material'):
                    current_model.material = new_value

            # Mark as modified
            self.is_modified = True
            self.status_bar.showMessage(f"Modified: {property_name} changed")

            # Update viewer if needed
            if hasattr(self, 'viewer_3d') and VIEWPORT_AVAILABLE:
                self.viewer_3d.set_current_model(current_model, selected_index)

            img_debugger.debug(f"Property changed: {property_name} = {new_value}")

        except Exception as e:
            img_debugger.error(f"Error handling property change: {str(e)}")
            self.status_bar.showMessage(f"Error: {str(e)}")


        def _create_sphere_icon(self): #vers 1
            """Sphere collision icon"""
            svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="2" fill="none"/>
                <ellipse cx="10" cy="10" rx="7" ry="3" stroke="currentColor" stroke-width="1.5" fill="none"/>
                <path d="M3 10 Q10 13 17 10" stroke="currentColor" stroke-width="1.5" fill="none"/>
            </svg>'''
            return self._svg_to_icon(svg_data, size=20)


        def _create_box_icon(self): #vers 1
            """Box collision icon"""
            svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 6 L10 3 L16 6 L16 14 L10 17 L4 14 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M4 6 L10 9 L16 6" stroke="currentColor" stroke-width="2"/>
                <path d="M10 9 L10 17" stroke="currentColor" stroke-width="2"/>
            </svg>'''
            return self._svg_to_icon(svg_data, size=20)


        def _create_mesh_icon(self): #vers 1
            """Mesh collision icon"""
            svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 10 L10 3 L17 10 L10 17 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M3 10 L17 10 M10 3 L10 17" stroke="currentColor" stroke-width="1.5"/>
            </svg>'''
            return self._svg_to_icon(svg_data, size=20)


        def _create_wireframe_icon(self): #vers 1
            """Wireframe mode icon"""
            svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 5 L15 5 L15 15 L5 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M5 10 L15 10 M10 5 L10 15" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="5" cy="5" r="1.5" fill="currentColor"/>
                <circle cx="15" cy="5" r="1.5" fill="currentColor"/>
                <circle cx="15" cy="15" r="1.5" fill="currentColor"/>
                <circle cx="5" cy="15" r="1.5" fill="currentColor"/>
            </svg>'''
            return self._svg_to_icon(svg_data, size=20)


        def _create_bounds_icon(self): #vers 1
            """Bounding box icon"""
            svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="3,2"/>
                <path d="M3 3 L7 3 M17 3 L13 3 M3 17 L7 17 M17 17 L13 17 M3 3 L3 7 M3 17 L3 13 M17 3 L17 7 M17 17 L17 13" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            </svg>'''
            return self._svg_to_icon(svg_data, size=20)


        def _create_reset_view_icon(self): #vers 1
            """Reset camera view icon"""
            svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 10A6 6 0 1 1 4 10M4 10l3-3m-3 3l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>'''
            return self._svg_to_icon(svg_data, size=20)


        def _set_camera_view(self, view_type): #vers 1
            """Set predefined camera view"""
            if view_type == 'top':
                self.viewer_3d.rotation_x = 0.0
                self.viewer_3d.rotation_y = 0.0
            elif view_type == 'front':
                self.viewer_3d.rotation_x = 90.0
                self.viewer_3d.rotation_y = 0.0
            elif view_type == 'side':
                self.viewer_3d.rotation_x = 90.0
                self.viewer_3d.rotation_y = 90.0

            self.viewer_3d.update()


        def _svg_to_icon(self, svg_data, size=24): #vers 1
            """Convert SVG to QIcon"""
            from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtCore import QByteArray

            try:
                text_color = self.palette().color(self.foregroundRole())
                svg_str = svg_data.decode('utf-8')
                svg_str = svg_str.replace('currentColor', text_color.name())
                svg_data = svg_str.encode('utf-8')

                renderer = QSvgRenderer(QByteArray(svg_data))
                pixmap = QPixmap(size, size)
                pixmap.fill(QColor(0, 0, 0, 0))

                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()

                return QIcon(pixmap)
            except:
                return QIcon()


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


    # Add import/export functionality when docked
    def _add_import_export_functionality(self): #vers 1
        """Add import/export functionality when docked to img factory"""
        try:
            # Only add these when docked to img factory
            if self.main_window and hasattr(self.main_window, 'log_message'):
                # Add import button to toolbar if not already present
                if not hasattr(self, 'import_btn'):
                    # Import button would be added to the toolbar in _create_toolbar
                    pass
                    
                # Add export button to toolbar if not already present
                if not hasattr(self, 'export_btn'):
                    # Export button would be added to the toolbar in _create_toolbar
                    pass
                    
                self.main_window.log_message(f"{App_name} import/export functionality ready")
                
        except Exception as e:
            img_debugger.error(f"Error adding import/export functionality: {str(e)}")


    def _import_col_data(self): #vers 1
        """Import COL data from external source"""
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} import functionality - not yet implemented")
                # TODO: Implement actual import functionality
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Import", "Import functionality coming soon!")
        except Exception as e:
            img_debugger.error(f"Error importing COL data: {str(e)}")


    def _export_col_data(self): #vers 1
        """Export COL data to external source"""
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"{App_name} export functionality - not yet implemented")
                # TODO: Implement actual export functionality
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export", "Export functionality coming soon!")
        except Exception as e:
            img_debugger.error(f"Error exporting COL data: {str(e)}")


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


def update_view_options(viewer: 'COL3DViewport', **options): #vers 1
    """Update 3D viewer options"""
    try:
        viewer.set_view_options(**options)
        img_debugger.debug(f"View options updated: {options}")

        def _ensure_standalone_functionality(self): #vers 1
            """Ensure popped-out windows work independently of img factory"""
            try:
                # When popped out, ensure all necessary functionality is available
                if not self.is_docked or getattr(self, 'is_overlay', False) == False:
                    # Enable all UI elements that might be disabled when docked
                    if hasattr(self, 'toolbar') and self.toolbar:
                        self.toolbar.setEnabled(True)

                    # Ensure all buttons and controls work independently
                    if hasattr(self, 'main_window') and self.main_window is None:
                        # This is truly standalone, enable all features
                        if hasattr(self, 'dock_btn'):
                            self.dock_btn.setText("X")  # Change to close button when standalone
                            self.dock_btn.setToolTip("Close window")

                    # Set proper window flags for standalone operation
                    if not getattr(self, 'is_overlay', False):
                        self.setWindowFlags(Qt.WindowType.Window)

            except Exception as e:
                img_debugger.error(f"Error ensuring standalone functionality: {str(e)}")

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


# --- External AI upscaler integration helper ---
import subprocess
import tempfile
import shutil
import sys


def open_workshop(main_window, img_path=None): #vers 3
    """Open Workshop from main window - works with or without IMG"""
    try:
        workshop = COLWorkshop(main_window, main_window)

        if img_path:
            # Check if it's a col file or IMG file
            if img_path.lower().endswith('.col'):
                # Load standalone col file
                workshop.open_col_file(img_path)
            else:
                # Load from IMG archive
                workshop.load_from_img_archive(img_path)
        else:
            # Open in standalone mode (no IMG loaded)
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message(App_name + " opened in standalone mode")

        workshop.show()
        return workshop
    except Exception as e:
        QMessageBox.critical(main_window, App_name * " Error", f"Failed to open: {str(e)}")
        return None


# Compatibility alias for imports
COLEditorDialog = COLWorkshop  #vers 1

if __name__ == "__main__":
    import sys
    import traceback

    print(App_name + " Starting.")

    try:
        app = QApplication(sys.argv)
        print("QApplication created")

        workshop = COLWorkshop()
        print(App_name + " instance created")

        workshop.setWindowTitle(App_name + " - Standalone")
        workshop.resize(1200, 800)
        workshop.show()
        print("Window shown, entering event loop")
        print(f"Window visible: {workshop.isVisible()}")
        print(f"Window geometry: {workshop.geometry()}")

        sys.exit(app.exec())

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

