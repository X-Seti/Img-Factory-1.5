#!/usr/bin/env python3
#this belongs in components/Txd_Editor/ txd_workshop.py - Version: 3
# X-Seti - September26 2025 - Img Factory 1.5 - TXD Workshop

"""
TXD Workshop - Main texture editing window for IMG Factory
Displays TXD files from IMG archives with texture preview and editing capabilities
"""

import os
import tempfile
import subprocess
import shutil
import struct
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit,
    QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage

##Methods list -
# _get_resize_direction
# _handle_resize
# _is_on_draggable_area
# _toggle_maximize
# _update_cursor
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# _create_blank_texture
# _create_empty_txd_data
# _create_left_panel
# _create_middle_panel
# _create_new_texture_entry
# _create_new_txd
# _create_right_panel
# _create_thumbnail
# _create_toolbar
# _decompress_dxt1
# _decompress_dxt3
# _decompress_dxt5
# _decompress_uncompressed
# _delete_texture
# _extract_alpha_channel
# _extract_txd_from_img
# _export_alpha_only
# _load_img_txd_list
# _load_txd_textures
# _mark_as_modified
# _on_texture_selected
# _on_txd_selected
# _parse_single_texture
# _reload_texture_table
# _save_texture_png
# _save_undo_state
# _show_texture_context_menu
# _undo_last_action
# _update_texture_info
# export_all_textures
# export_selected_texture
# flip_texture
# import_texture
# load_from_img_archive
# open_img_archive
# open_txd_file
# save_txd_file
# setup_ui
# show_properties

##class TXDWorkshop: -
# __init__
# closeEvent

class TXDWorkshop(QWidget): #vers 3
    """TXD Workshop - Main texture editing window"""

    workshop_closed = pyqtSignal()

    def __init__(self, parent=None, main_window=None): #vers 5
        super().__init__(parent)
        self.main_window = main_window
        self.current_img = None
        self.current_txd_data = None
        self.current_txd_name = None
        self.txd_list = []
        self.texture_list = []
        self.selected_texture = None
        self.undo_stack = []

        # Detect standalone mode
        self.standalone_mode = (main_window is None)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setWindowTitle("TXD Workshop: No File")
        self.resize(1400, 800)
        self._initialize_features()
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_direction = None
        self.resize_margin = 10

        if parent:
            parent_pos = parent.pos()
            self.move(parent_pos.x() + 50, parent_pos.y() + 80)

        self.setup_ui()

        from PyQt6.QtWidgets import QSizeGrip
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        self.size_grip.move(self.width() - 16, self.height() - 16)
        self.size_grip.raise_()
        self._apply_theme()

    def setup_ui(self): #vers 6
        """Setup the main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

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

        # Connect signals AFTER texture_table is created
        self._connect_texture_table_signals()

        # Status indicators if available
        if hasattr(self, '_setup_status_indicators'):
            status_frame = self._setup_status_indicators()
            main_layout.addWidget(status_frame)

    def _initialize_features(self): #vers 1
        """Initialize all features after UI setup"""
        try:
            self._apply_theme()
            self._update_status_indicators()

            if hasattr(self, 'format_filter'):
                self.format_filter.setCurrentIndex(0)
            if hasattr(self, 'size_filter'):
                self.size_filter.setCurrentIndex(0)
            if hasattr(self, 'alpha_filter'):
                self.alpha_filter.setCurrentIndex(0)

            self._clear_texture_search()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("TXD Workshop features initialized")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"features init error: {str(e)}")


    def mousePressEvent(self, event): #vers 1
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on resize edge
            self.resize_direction = self._get_resize_direction(event.pos())

            if self.resize_direction:
                self.resizing = True
                self.drag_position = event.globalPosition().toPoint()
            else:
                # Check if clicking on toolbar for dragging
                if self._is_on_draggable_area(event.pos()):
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

            event.accept()


    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse move for dragging and resizing"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing and self.resize_direction:
                self._handle_resize(event.globalPosition().toPoint())
            elif self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # Update cursor based on position
            resize_dir = self._get_resize_direction(event.pos())
            self._update_cursor(resize_dir)


    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_direction = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()

    def resizeEvent(self, event): #vers 1
        '''Keep resize grip in bottom-right corner'''
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - 16, self.height() - 16)

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


    def mouseDoubleClickEvent(self, event): #vers 1
        """Handle double-click on toolbar to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_on_draggable_area(event.pos()):
                self._toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)

    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def _enable_txd_features_after_load(self): #vers 1
        """Enable TXD features after successful texture load"""
        if self.texture_list:
            self.save_txd_btn.setEnabled(False)
            self.import_btn.setEnabled(True)
            self.export_all_btn.setEnabled(True)

            if hasattr(self, 'new_texture_btn'):
                self.new_texture_btn.setEnabled(True)
            if hasattr(self, 'stats_btn'):
                self.stats_btn.setEnabled(True)

            self._update_status_indicators()

    def _is_on_draggable_area(self, pos): #vers 3
        """Check if position is on draggable toolbar area (stretch space, not buttons)"""
        if not hasattr(self, 'toolbar'):
            return False

        toolbar_rect = self.toolbar.geometry()
        if not toolbar_rect.contains(pos):
            return False

        # Get all buttons in toolbar
        buttons_to_check = []

        if hasattr(self, 'open_img_btn'):
            buttons_to_check.append(self.open_img_btn)
        if hasattr(self, 'open_txd_btn'):
            buttons_to_check.append(self.open_txd_btn)
        if hasattr(self, 'save_txd_btn'):
            buttons_to_check.append(self.save_txd_btn)
        if hasattr(self, 'import_btn'):
            buttons_to_check.append(self.import_btn)
        if hasattr(self, 'export_btn'):
            buttons_to_check.append(self.export_btn)
        if hasattr(self, 'export_all_btn'):
            buttons_to_check.append(self.export_all_btn)
        if hasattr(self, 'flip_btn'):
            buttons_to_check.append(self.flip_btn)
        if hasattr(self, 'props_btn'):
            buttons_to_check.append(self.props_btn)
        if hasattr(self, 'info_btn'):
            buttons_to_check.append(self.info_btn)
        if hasattr(self, 'minimize_btn'):
            buttons_to_check.append(self.minimize_btn)
        if hasattr(self, 'maximize_btn'):
            buttons_to_check.append(self.maximize_btn)
        if hasattr(self, 'close_btn'):
            buttons_to_check.append(self.close_btn)

        if not hasattr(self, 'drag_btn'):
            return False

        # Convert to toolbar coordinates
        toolbar_local_pos = self.toolbar.mapFrom(self, pos)

        # Check if clicking on drag button
        return self.drag_btn.geometry().contains(toolbar_local_pos)

        # Check if position is NOT on any button (i.e., on stretch area)
        for btn in buttons_to_check:
            btn_global_rect = btn.geometry()
            btn_rect = btn_global_rect.translated(toolbar_rect.topLeft())
            if btn_rect.contains(pos):
                return False  # On a button, not draggable

        return True  # On empty stretch area, draggable


    def _create_resize_icon(self): #vers 1
        """Resize grip icon - diagonal arrows"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 6l-8 8M10 6h4v4M6 14v-4h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _setup_status_indicators(self): #vers 4
        """Setup status indicators with visible resize button"""
        self.status_frame = QFrame()
        self.status_layout = QHBoxLayout(self.status_frame)
        self.status_layout.setContentsMargins(5, 2, 5, 2)

        self.status_textures = QLabel("Textures: 0")
        self.status_layout.addWidget(self.status_textures)

        self.status_selected = QLabel("Selected: None")
        self.status_layout.addWidget(self.status_selected)

        self.status_size = QLabel("TXD Size: Unknown")
        self.status_layout.addWidget(self.status_size)

        self.status_layout.addStretch()

        self.status_modified = QLabel("")
        self.status_layout.addWidget(self.status_modified)

        # Add visible resize button with icon
        self.resize_grip_btn = QPushButton()
        self.resize_grip_btn.setIcon(self._create_resize_icon())
        self.resize_grip_btn.setIconSize(QSize(16, 16))
        self.resize_grip_btn.setFixedSize(20, 20)
        self.resize_grip_btn.setToolTip("Drag to resize window")
        self.resize_grip_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        # Make it act like a resize grip
        self.resize_grip_btn.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.status_layout.addWidget(self.resize_grip_btn)

        return self.status_frame

    def _create_toolbar(self): #vers 9
        """Create toolbar with drag and tear-off buttons"""
        self.toolbar = QFrame()
        self.toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(self.toolbar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Only show "Open IMG" button if NOT standalone
        if not self.standalone_mode:
            self.open_img_btn = QPushButton("Open IMG")
            self.open_img_btn.setIcon(self._create_folder_icon())
            self.open_img_btn.setIconSize(QSize(20, 20))
            self.open_img_btn.clicked.connect(self.open_img_archive)
            layout.addWidget(self.open_img_btn)

        self.open_txd_btn = QPushButton("Open TXD")
        self.open_txd_btn.setIcon(self._create_file_icon())
        self.open_txd_btn.setIconSize(QSize(20, 20))
        self.open_txd_btn.clicked.connect(self.open_txd_file)
        layout.addWidget(self.open_txd_btn)

        self.save_txd_btn = QPushButton("Save TXD")
        self.save_txd_btn.setIcon(self._create_save_icon())
        self.save_txd_btn.setIconSize(QSize(20, 20))
        self.save_txd_btn.clicked.connect(self.save_txd_file)
        self.save_txd_btn.setEnabled(False)
        layout.addWidget(self.save_txd_btn)

        layout.addSpacing(10)

        self.import_btn = QPushButton("Import")
        self.import_btn.setIcon(self._create_import_icon())
        self.import_btn.setIconSize(QSize(20, 20))
        self.import_btn.clicked.connect(self.import_texture)
        self.import_btn.setEnabled(False)
        layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.setIcon(self._create_export_icon())
        self.export_btn.setIconSize(QSize(20, 20))
        self.export_btn.clicked.connect(self.export_selected_texture)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)

        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.setIcon(self._create_package_icon())
        self.export_all_btn.setIconSize(QSize(20, 20))
        self.export_all_btn.clicked.connect(self.export_all_textures)
        self.export_all_btn.setEnabled(False)
        layout.addWidget(self.export_all_btn)

        layout.addSpacing(10)

        self.flip_btn = QPushButton("Switch")
        self.flip_btn.setIcon(self._create_flip_vert_icon())
        self.flip_btn.setIconSize(QSize(20, 20))
        self.flip_btn.clicked.connect(self.flip_texture)
        self.flip_btn.setEnabled(False)
        layout.addWidget(self.flip_btn)

        self.props_btn = QPushButton("Properties")
        self.props_btn.setIcon(self._create_properties_icon())
        self.props_btn.setIconSize(QSize(20, 20))
        self.props_btn.clicked.connect(self.show_properties)
        self.props_btn.setEnabled(False)
        layout.addWidget(self.props_btn)

        self.info_btn = QPushButton("Info")
        self.info_btn.setIcon(self._create_info_icon())
        self.info_btn.setIconSize(QSize(20, 20))
        self.info_btn.clicked.connect(self._show_detailed_info)
        self.info_btn.setEnabled(False)
        layout.addWidget(self.info_btn)

        layout.addStretch()

        # Drag button [D]
        self.drag_btn = QPushButton("D")
        self.drag_btn.setMinimumWidth(40)
        self.drag_btn.setMaximumWidth(40)
        self.drag_btn.setMinimumHeight(30)
        self.drag_btn.setToolTip("Drag to move window")
        self.drag_btn.setStyleSheet("""
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
        self.drag_btn.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(self.drag_btn)

        # Tear-off button [T] - only in IMG Factory mode
        if not self.standalone_mode:
            self.tearoff_btn = QPushButton("T")
            self.tearoff_btn.setMinimumWidth(40)
            self.tearoff_btn.setMaximumWidth(40)
            self.tearoff_btn.setMinimumHeight(30)
            self.tearoff_btn.clicked.connect(self._toggle_tearoff)
            self.tearoff_btn.setToolTip("Merge back to IMG Factory window")
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
        self.minimize_btn.setIconSize(QSize(16, 16))
        self.minimize_btn.setMinimumWidth(40)
        self.minimize_btn.setMaximumWidth(40)
        self.minimize_btn.setMinimumHeight(30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize Window")
        layout.addWidget(self.minimize_btn)

        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(self._create_maximize_icon())
        self.maximize_btn.setIconSize(QSize(16, 16))
        self.maximize_btn.setMinimumWidth(40)
        self.maximize_btn.setMaximumWidth(40)
        self.maximize_btn.setMinimumHeight(30)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.maximize_btn.setToolTip("Maximize/Restore Window")
        layout.addWidget(self.maximize_btn)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(self._create_close_icon())
        self.close_btn.setIconSize(QSize(16, 16))
        self.close_btn.setMinimumWidth(40)
        self.close_btn.setMaximumWidth(40)
        self.close_btn.setMinimumHeight(30)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close Window")
        layout.addWidget(self.close_btn)

        return self.toolbar

    def _toggle_tearoff(self): #vers 1
        """Toggle tear-off state (merge back to IMG Factory)"""
        QMessageBox.information(self, "Tear-off",
            "Merge back to IMG Factory functionality coming soon!\n\n"
            "This will dock the TXD Workshop back into the main window.")



    def _on_texture_table_double_click(self, item): #vers 1
        """Handle double-click on texture table - open mipmap manager"""
        try:
            row = item.row()

            # Get texture for this row
            if row < 0 or row >= len(self.texture_list):
                return

            texture = self.texture_list[row]

            # Check if texture has mipmaps
            mipmap_levels = texture.get('mipmap_levels', [])
            if len(mipmap_levels) > 1:
                # Has mipmaps - open mipmap manager
                self.selected_texture = texture
                self._open_mipmap_manager()
            else:
                # No mipmaps - just select the texture
                self.selected_texture = texture
                self._update_texture_info(texture)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Double-click error: {str(e)}")


    def _create_right_panel(self): #vers 5
        """Create right panel with editing controls - aligned button layout"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)

        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Sub-layout to place transform panel and preview side by side
        top_layout = QHBoxLayout()

        # Transform panel (left in the sub-layout)
        transform_panel = self._create_transform_panel()
        top_layout.addWidget(transform_panel, stretch=1)

        # Preview area (right in the sub-layout)
        self.preview_label = QLabel("No texture selected")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setMinimumWidth(400)
        self.preview_label.setStyleSheet("border: 1px solid #3a3a3a; background-color: #1e1e1e;")
        top_layout.addWidget(self.preview_label, stretch=2)

        # Add the top horizontal layout to the main vertical layout
        main_layout.addLayout(top_layout)

        # Information group
        info_group = QGroupBox("Texture Information")
        info_layout = QVBoxLayout(info_group)

        # Row 1: Texture name and alpha name (full width, no buttons)
        name_layout = QHBoxLayout()

        self.info_name = QLabel("Name: -")
        self.info_name.setStyleSheet("font-weight: bold; padding: 5px; border: 1px solid #3a3a3a;")
        self.info_name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.info_name.customContextMenuRequested.connect(lambda pos: self._show_name_context_menu(pos, alpha=False))
        name_layout.addWidget(self.info_name, stretch=1)

        self.info_alpha_name = QLabel("Alpha: -")
        self.info_alpha_name.setStyleSheet("color: red; font-weight: bold; padding: 5px; border: 1px solid #3a3a3a;")
        self.info_alpha_name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.info_alpha_name.customContextMenuRequested.connect(lambda pos: self._show_name_context_menu(pos, alpha=True))
        self.info_alpha_name.setVisible(False)
        name_layout.addWidget(self.info_alpha_name, stretch=1)

        info_layout.addLayout(name_layout)
        info_layout.addSpacing(5)

        # Row 2: Size label (left) + buttons (right, aligned)
        size_layout = QHBoxLayout()
        self.info_size = QLabel("Size: -")
        self.info_size.setMinimumWidth(120)
        size_layout.addWidget(self.info_size)

        size_layout.addStretch()

        self.bitdepth_btn = QPushButton("Bit Depth")
        self.bitdepth_btn.clicked.connect(self._change_bit_depth)
        self.bitdepth_btn.setEnabled(False)
        size_layout.addWidget(self.bitdepth_btn)

        self.resize_btn = QPushButton("Resize")
        self.resize_btn.clicked.connect(self._resize_texture)
        self.resize_btn.setEnabled(False)
        size_layout.addWidget(self.resize_btn)

        self.upscale_btn = QPushButton("AI Upscale")
        self.upscale_btn.clicked.connect(self._upscale_texture)
        self.upscale_btn.setEnabled(False)
        size_layout.addWidget(self.upscale_btn)

        info_layout.addLayout(size_layout)

        # Row 3: Format label (left) + dropdown, buttons, and bit depth indicator (right, aligned)
        format_layout = QHBoxLayout()

        self.format_status_label = QLabel("Format: -")
        self.format_status_label.setMinimumWidth(120)
        format_layout.addWidget(self.format_status_label)

        format_layout.addStretch()

        self.format_combo = QComboBox()
        self.format_combo.addItems(["DXT1", "DXT3", "DXT5", "ARGB8888", "ARGB1555", "ARGB4444", "RGB888", "RGB565"])
        self.format_combo.currentTextChanged.connect(self._change_format)
        self.format_combo.setEnabled(False)
        format_layout.addWidget(self.format_combo)

        self.compress_btn = QPushButton("Compress")
        self.compress_btn.clicked.connect(self._compress_texture)
        self.compress_btn.setEnabled(False)
        format_layout.addWidget(self.compress_btn)

        self.uncompress_btn = QPushButton("Uncompress")
        self.uncompress_btn.clicked.connect(self._uncompress_texture)
        self.uncompress_btn.setEnabled(False)
        format_layout.addWidget(self.uncompress_btn)

        # Bit depth indicator (read-only display)
        self.info_bitdepth = QLabel("[32bit]")
        self.info_bitdepth.setStyleSheet("font-weight: bold; padding: 5px; border: 1px solid #3a3a3a;")
        format_layout.addWidget(self.info_bitdepth)

        info_layout.addLayout(format_layout)

        # Row 4: Mipmaps label (left) + button (right, aligned)
        mipmap_layout = QHBoxLayout()
        self.info_format = QLabel("Mipmaps:")
        self.info_format.setMinimumWidth(120)
        mipmap_layout.addWidget(self.info_format)

        mipmap_layout.addStretch()

        self.show_mipmaps_btn = QPushButton("View Mipmaps")
        self.show_mipmaps_btn.clicked.connect(self._open_mipmap_manager)
        self.show_mipmaps_btn.setEnabled(False)
        self.show_mipmaps_btn.setToolTip("View all mipmap levels")
        mipmap_layout.addWidget(self.show_mipmaps_btn)

        info_layout.addLayout(mipmap_layout)

        main_layout.addWidget(info_group)
        return panel

    def _change_bit_depth(self): #vers 1
        """Change texture bit depth"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QInputDialog

        current_depth = self.selected_texture.get('depth', 32)

        bit_depths = ["32bit (RGBA)", "24bit (RGB)", "16bit (ARGB1555)", "16bit (ARGB4444)", "16bit (RGB565)", "8bit (Indexed)"]
        depth_values = [32, 24, 16, 16, 16, 8]

        # Find current selection
        try:
            current_index = depth_values.index(current_depth)
        except:
            current_index = 0

        choice, ok = QInputDialog.getItem(
            self,
            "Change Bit Depth",
            f"Current: {current_depth}bit\n\nSelect new bit depth:",
            bit_depths,
            current_index,
            False
        )

        if ok:
            new_depth = depth_values[bit_depths.index(choice)]

            if new_depth != current_depth:
                self._save_undo_state("Change bit depth")
                self.selected_texture['depth'] = new_depth

                self._update_texture_info(self.selected_texture)
                self._update_table_display()
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Bit depth changed: {current_depth}bit → {new_depth}bit")

    def _mipmap_io_menu(self): #vers 1
        """Show export/import menu for mipmaps"""
        if not self.selected_texture:
            return

        menu = QMenu(self)
        export_action = menu.addAction("📤 Export All Levels")
        export_action.triggered.connect(self._export_all_levels)

        import_action = menu.addAction("📥 Import All Levels")
        import_action.triggered.connect(self._import_all_levels)

        menu.exec(self.mipmap_io_btn.mapToGlobal(self.mipmap_io_btn.rect().bottomLeft()))


    def _update_editing_controls(self): #vers 2
        """Update editing control states based on selection"""
        has_selection = self.selected_texture is not None

        # Basic controls
        if hasattr(self, 'resize_btn'):
            self.resize_btn.setEnabled(has_selection)
        if hasattr(self, 'upscale_btn'):
            self.upscale_btn.setEnabled(has_selection)
        if hasattr(self, 'format_combo'):
            self.format_combo.setEnabled(has_selection)

        if has_selection:
            # Compress button - always enabled (can compress or change DXT format)
            if hasattr(self, 'compress_btn'):
                self.compress_btn.setEnabled(True)

            # Uncompress button - only enabled if currently DXT format
            if hasattr(self, 'uncompress_btn'):
                current_format = self.selected_texture.get('format', 'Unknown')
                self.uncompress_btn.setEnabled('DXT' in current_format)
        else:
            # No selection - disable both
            if hasattr(self, 'compress_btn'):
                self.compress_btn.setEnabled(False)
            if hasattr(self, 'uncompress_btn'):
                self.uncompress_btn.setEnabled(False)


    def _batch_export_dialog(self): #vers 1
        """Show batch export options dialog"""
        if not self.texture_list:
            QMessageBox.warning(self, "No Textures", "No textures to export")
            return

        # Create custom dialog
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Batch Export Options")
        dialog.setText(f"Export {len(self.texture_list)} textures:")

        normal_btn = dialog.addButton("Normal Only", QMessageBox.ButtonRole.AcceptRole)
        alpha_btn = dialog.addButton("Alpha Only", QMessageBox.ButtonRole.AcceptRole)
        both_btn = dialog.addButton("Both Separate", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        dialog.exec()
        clicked = dialog.clickedButton()

        if clicked == cancel_btn:
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        try:
            exported = 0
            for texture in self.texture_list:
                name = texture.get('name', f'texture_{exported}')
                rgba_data = texture.get('rgba_data')
                width = texture.get('width', 0)
                height = texture.get('height', 0)

                if rgba_data and width > 0:
                    if clicked == normal_btn or clicked == both_btn:
                        file_path = os.path.join(output_dir, f"{name}.png")
                        self._save_texture_png(rgba_data, width, height, file_path)
                        exported += 1

                    if clicked == alpha_btn or clicked == both_btn:
                        alpha_data = self._extract_alpha_channel(rgba_data)
                        alpha_path = os.path.join(output_dir, f"{name}_alpha.png")
                        self._save_texture_png(alpha_data, width, height, alpha_path)
                        if clicked == alpha_btn:
                            exported += 1

            QMessageBox.information(self, "Success", f"Exported {exported} files successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Batch export failed: {str(e)}")

    def _show_detailed_info(self): #vers 1
        """Show detailed texture information"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        tex = self.selected_texture

        # Build detailed info
        info = f"=== Texture Details ===\n"
        info += f"Name: {tex.get('name', 'Unknown')}\n"
        info += f"Dimensions: {tex.get('width', 0)}x{tex.get('height', 0)}\n"
        info += f"Format: {tex.get('format', 'Unknown')}\n"
        info += f"Has Alpha: {'Yes' if tex.get('has_alpha', False) else 'No'}\n"

        if tex.get('alpha_name'):
            info += f"Alpha Name: {tex.get('alpha_name')}\n"

        if tex.get('rgba_data'):
            data_size = len(tex['rgba_data'])
            info += f"Raw Data Size: {data_size:,} bytes ({data_size/1024:.1f} KB)\n"

            # Calculate memory usage
            pixels = tex.get('width', 0) * tex.get('height', 0)
            if pixels > 0:
                info += f"Pixel Count: {pixels:,}\n"
                info += f"Bytes per Pixel: {data_size/pixels:.1f}\n"

        # Estimated compressed size
        est_dxt1 = (tex.get('width', 0) * tex.get('height', 0)) // 2
        est_dxt5 = tex.get('width', 0) * tex.get('height', 0)
        info += f"\n=== Estimated Compressed Sizes ===\n"
        info += f"DXT1: {est_dxt1:,} bytes\n"
        info += f"DXT5: {est_dxt5:,} bytes\n"

        QMessageBox.information(self, "Detailed Texture Information", info)


    def _update_status_indicators(self): #vers 1
        """Update status indicators"""
        if hasattr(self, 'status_textures'):
            self.status_textures.setText(f"Textures: {len(self.texture_list)}")

        if hasattr(self, 'status_selected'):
            if self.selected_texture:
                name = self.selected_texture.get('name', 'Unknown')
                self.status_selected.setText(f"Selected: {name}")
            else:
                self.status_selected.setText("Selected: None")

        if hasattr(self, 'status_size'):
            if self.current_txd_data:
                size_kb = len(self.current_txd_data) / 1024
                self.status_size.setText(f"TXD Size: {size_kb:.1f} KB")
            else:
                self.status_size.setText("TXD Size: Unknown")

        if hasattr(self, 'status_modified'):
            if self.windowTitle().endswith("*"):
                self.status_modified.setText("MODIFIED")
                self.status_modified.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.status_modified.setText("")
                self.status_modified.setStyleSheet("")


    def _import_normal_texture(self): #vers 1
        """Import normal texture (RGB/RGBA)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Normal Texture", "",
            "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
        )

        if not file_path:
            return

        try:
            from PyQt6.QtGui import QImage

            # Load image
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.critical(self, "Error", "Failed to load image")
                return

            # Convert to RGBA8888
            img = img.convertToFormat(QImage.Format.Format_RGBA8888)

            # Get image data
            width = img.width()
            height = img.height()
            ptr = img.bits()
            ptr.setsize(img.sizeInBytes())
            rgba_data = bytes(ptr)

            # Check if image has alpha
            has_alpha = False
            for i in range(3, len(rgba_data), 4):
                if rgba_data[i] < 255:
                    has_alpha = True
                    break

            # Update texture
            self._save_undo_state("Import normal texture")
            self.selected_texture['width'] = width
            self.selected_texture['height'] = height
            self.selected_texture['rgba_data'] = rgba_data
            self.selected_texture['has_alpha'] = has_alpha

            # Update alpha name if texture now has alpha
            if has_alpha and 'alpha_name' not in self.selected_texture:
                self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                alpha_msg = "with alpha" if has_alpha else "no alpha"
                self.main_window.log_message(f"✅ Imported normal texture: {width}x{height} ({alpha_msg})")

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")


    def _import_alpha_texture(self): #vers 2
        """Import alpha channel - creates alpha if doesn't exist"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Alpha Channel", "",
            "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
        )

        if not file_path:
            return

        try:
            from PyQt6.QtGui import QImage

            # Load alpha image
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.critical(self, "Error", "Failed to load image")
                return

            # Get current texture dimensions
            tex_width = self.selected_texture.get('width', 0)
            tex_height = self.selected_texture.get('height', 0)

            # If no texture data exists, create blank texture with alpha
            if not self.selected_texture.get('rgba_data') or tex_width == 0 or tex_height == 0:
                # Use alpha image dimensions
                tex_width = img.width()
                tex_height = img.height()

                # Create blank RGB texture (gray)
                blank_rgba = bytearray()
                for _ in range(tex_width * tex_height):
                    blank_rgba.extend([128, 128, 128, 255])  # Gray with full alpha

                self.selected_texture['width'] = tex_width
                self.selected_texture['height'] = tex_height
                self.selected_texture['rgba_data'] = bytes(blank_rgba)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"ℹ️ Created blank texture {tex_width}x{tex_height} for alpha import")

            # Check dimensions match
            if img.width() != tex_width or img.height() != tex_height:
                reply = QMessageBox.question(
                    self, "Size Mismatch",
                    f"Alpha image is {img.width()}x{img.height()}, texture is {tex_width}x{tex_height}. Resize alpha?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    img = img.scaled(tex_width, tex_height, Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
                else:
                    return

            # Convert to grayscale
            img = img.convertToFormat(QImage.Format.Format_Grayscale8)

            # Get alpha data
            ptr = img.bits()
            ptr.setsize(img.sizeInBytes())
            alpha_data = bytes(ptr)

            # Apply alpha to existing texture
            self._save_undo_state("Import alpha channel")

            rgba_data = bytearray(self.selected_texture['rgba_data'])

            # If current texture has no alpha (all 255), we're adding it
            has_existing_alpha = any(rgba_data[i] < 255 for i in range(3, len(rgba_data), 4))

            for i, alpha_val in enumerate(alpha_data):
                if i * 4 + 3 < len(rgba_data):
                    rgba_data[i * 4 + 3] = alpha_val  # Set alpha channel

            self.selected_texture['rgba_data'] = bytes(rgba_data)
            self.selected_texture['has_alpha'] = True

            # Add alpha name if not present
            if 'alpha_name' not in self.selected_texture:
                self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

            # Update format to support alpha if currently non-alpha format
            current_format = self.selected_texture.get('format', 'DXT1')
            if current_format in ['DXT1', 'RGB888', 'RGB565']:
                # Switch to alpha-capable format
                if 'DXT' in current_format:
                    self.selected_texture['format'] = 'DXT5'
                    format_msg = " (format changed to DXT5)"
                else:
                    self.selected_texture['format'] = 'ARGB8888'
                    format_msg = " (format changed to ARGB8888)"
            else:
                format_msg = ""

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                action = "Added" if not has_existing_alpha else "Replaced"
                self.main_window.log_message(f"✅ {action} alpha channel from: {os.path.basename(file_path)}{format_msg}")

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import alpha: {str(e)}")


    def _on_texture_selected(self): #vers 3
        """Handle texture selection with full feature support"""
        try:
            row = self.texture_table.currentRow()
            if row < 0 or row >= len(self.texture_list):
                self.selected_texture = None

                self.export_btn.setEnabled(False)

                # Update flip button based on alpha existence
                if hasattr(self, 'flip_btn'):
                    has_alpha = self.selected_texture.get('has_alpha', False)
                    self.flip_btn.setEnabled(has_alpha)
                    if has_alpha:
                        self.flip_btn.setText("Alpha")
                        self.flip_btn.setToolTip("Toggle between normal and alpha view")
                    else:
                        self.flip_btn.setText("Flip")
                        self.flip_btn.setToolTip("This texture has no alpha channel")

                if hasattr(self, 'props_btn'):
                    self.props_btn.setEnabled(False)
                if hasattr(self, 'duplicate_btn'):
                    self.duplicate_btn.setEnabled(False)
                if hasattr(self, 'remove_btn'):
                    self.remove_btn.setEnabled(False)

                self._update_editing_controls()
                self._update_status_indicators()
                return

            self.selected_texture = self.texture_list[row]
            self._update_texture_info(self.selected_texture)

            self.export_btn.setEnabled(True)
            if hasattr(self, 'flip_btn'):
                self.flip_btn.setEnabled(True)
            if hasattr(self, 'props_btn'):
                self.props_btn.setEnabled(True)
            if hasattr(self, 'duplicate_btn'):
                self.duplicate_btn.setEnabled(True)
            if hasattr(self, 'remove_btn'):
                self.remove_btn.setEnabled(True)

            # Enable transform buttons
            if hasattr(self, 'flip_vert_btn'):
                self.flip_vert_btn.setEnabled(True)
            if hasattr(self, 'flip_horz_btn'):
                self.flip_horz_btn.setEnabled(True)
            if hasattr(self, 'rotate_cw_btn'):
                self.rotate_cw_btn.setEnabled(True)
            if hasattr(self, 'rotate_ccw_btn'):
                self.rotate_ccw_btn.setEnabled(True)
            if hasattr(self, 'copy_btn'):
                self.copy_btn.setEnabled(True)
            if hasattr(self, 'paste_btn'):
                self.paste_btn.setEnabled(True)
            if hasattr(self, 'edit_btn'):
                self.edit_btn.setEnabled(True)
            if hasattr(self, 'convert_btn'):
                self.convert_btn.setEnabled(True)
            # Enable mipmap buttons if texture selected
            if hasattr(self, 'generate_mipmaps_btn'):
                self.generate_mipmaps_btn.setEnabled(True)
            if hasattr(self, 'show_mipmaps_btn'):
                has_mipmaps = len(self.selected_texture.get('mipmap_levels', [])) > 1
                self.show_mipmaps_btn.setEnabled(has_mipmaps)
            if hasattr(self, 'mipmap_io_btn'):
                self.mipmap_io_btn.setEnabled(True)

            self._update_editing_controls()
            self._update_status_indicators()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Selection error: {str(e)}")


    def _apply_theme(self): #vers 1
        """Apply theme from main window"""
        try:
            if self.main_window and hasattr(self.main_window, 'app_settings'):
                from components.Txd_Editor.txd_workshop_theme import apply_theme_to_workshop, connect_workshop_to_theme_system
                apply_theme_to_workshop(self, self.main_window)
                connect_workshop_to_theme_system(self, self.main_window)
        except:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #e0e0e0; }
                QListWidget { background-color: #1e1e1e; border: 1px solid #3a3a3a; }
                QListWidget::item:selected { background-color: #0d47a1; }
                QPushButton { background-color: #3a3a3a; border: 1px solid #4a4a4a; padding: 5px 15px; border-radius: 3px; }
                QPushButton:hover { background-color: #4a4a4a; }
            """)



    def _create_left_panel(self): #vers 5
        """Create left panel - TXD file list (only in IMG Factory mode)"""
        # In standalone mode, don't create this panel
        if self.standalone_mode:
            self.txd_list_widget = None  # Explicitly set to None
            return None

        # Only create panel in IMG Factory mode
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("TXD Files")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.txd_list_widget = QListWidget()
        self.txd_list_widget.setAlternatingRowColors(True)
        self.txd_list_widget.itemClicked.connect(self._on_txd_selected)
        layout.addWidget(self.txd_list_widget)

        return panel

    def _load_img_txd_list(self): #vers 2
        """Load TXD files from IMG archive"""
        try:
            # Safety check for standalone mode
            if self.standalone_mode or not hasattr(self, 'txd_list_widget') or self.txd_list_widget is None:
                return

            self.txd_list_widget.clear()
            self.txd_list = []

            if not self.current_img:
                return

            for entry in self.current_img.entries:
                if entry.name.lower().endswith('.txd'):
                    self.txd_list.append(entry)
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry)
                    size_kb = entry.size / 1024
                    item.setToolTip(f"{entry.name}\nSize: {size_kb:.1f} KB")
                    self.txd_list_widget.addItem(item)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Found {len(self.txd_list)} TXD files")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error loading TXD list: {str(e)}")


    def _create_middle_panel(self): #vers 3
        """Create middle panel - Texture list with context menu"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("Textures")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        self.texture_table = QTableWidget()
        self.texture_table.setColumnCount(2)
        self.texture_table.setHorizontalHeaderLabels(["Preview", "Details"])
        self.texture_table.horizontalHeader().setStretchLastSection(True)
        self.texture_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.texture_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.texture_table.setAlternatingRowColors(True)
        self.texture_table.itemSelectionChanged.connect(self._on_texture_selected)
        self.texture_table.setIconSize(QSize(64, 64))
        self.texture_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.texture_table.customContextMenuRequested.connect(self._show_texture_context_menu)
        layout.addWidget(self.texture_table)

        return panel


    def _create_blank_texture(self, width, height, with_alpha=False): #vers 2
        """Create blank RGBA texture data with optional alpha"""
        if with_alpha:
            # Gray with transparent alpha (128)
            return bytes([128, 128, 128, 128] * (width * height))
        else:
            # Gray with full opaque alpha (255)
            return bytes([128, 128, 128, 255] * (width * height))


    def _create_empty_txd_data(self): #vers 1
        """Create minimal empty TXD structure"""
        import struct
        # RenderWare TXD header (simplified)
        header = struct.pack('<III', 0x16, 0, 0x1803FFFF)  # Type, Size, Version
        return header

    def _create_new_texture_entry(self): #vers 2
        """Create a new texture entry in current TXD with optional alpha channel"""
        if not self.current_txd_data:
            QMessageBox.warning(self, "No TXD", "Please load or create a TXD file first")
            return

        name, ok = QInputDialog.getText(self, "New Texture Entry", "Enter texture name:")
        if not ok or not name:
            return

        # Ask if user wants alpha channel
        reply = QMessageBox.question(
            self, "Alpha Channel",
            "Create texture with alpha channel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        create_with_alpha = (reply == QMessageBox.StandardButton.Yes)

        # Create basic texture entry
        new_texture = {
            'name': name,
            'width': 256,
            'height': 256,
            'format': 'DXT5' if create_with_alpha else 'DXT1',
            'has_alpha': create_with_alpha,
            'mipmaps': 1,
            'rgba_data': self._create_blank_texture(256, 256, create_with_alpha)
        }

        # Add alpha name if creating with alpha
        if create_with_alpha:
            new_texture['alpha_name'] = name + 'a'

        self.texture_list.append(new_texture)
        self._save_undo_state("Create texture entry")
        self._reload_texture_table()
        self._mark_as_modified()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            alpha_msg = "with alpha" if create_with_alpha else "no alpha"
            self.main_window.log_message(f"✅ Created texture entry: {name} ({alpha_msg})")



    def _create_new_txd(self): #vers 1
        """Create a new empty TXD file"""
        name, ok = QInputDialog.getText(self, "New TXD", "Enter TXD filename (without .txd):")
        if ok and name:
            if not name.lower().endswith('.txd'):
                name += '.txd'

            # Create minimal TXD structure
            self.current_txd_name = name
            self.current_txd_data = self._create_empty_txd_data()
            self.texture_list = []
            self.texture_table.setRowCount(0)

            self.setWindowTitle(f"TXD Workshop: {name}")
            self.save_txd_btn.setEnabled(True)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Created new TXD: {name}")


    def _delete_texture(self): #vers 1
        """Delete selected texture from TXD"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to delete")
            return

        reply = QMessageBox.question(
            self, "Delete Texture",
            f"Delete texture '{self.selected_texture['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._save_undo_state("Delete texture")
            self.texture_list.remove(self.selected_texture)
            self.selected_texture = None
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Texture deleted")

    def _mark_as_modified(self): #vers 1
        """Mark the TXD as modified and enable save button"""
        self.save_txd_btn.setEnabled(True)
        self.save_txd_btn.setStyleSheet("background-color: #ff6b35; font-weight: bold;")
        current_title = self.windowTitle()
        if not current_title.endswith("*"):
            self.setWindowTitle(current_title + "*")

    def _open_mipmap_manager(self): #vers 1
        """Open Mipmap Manager window for selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        mipmap_levels = self.selected_texture.get('mipmap_levels', [])
        if not mipmap_levels:
            QMessageBox.information(self, "No Mipmaps", "This texture has no mipmap levels")
            return

        # Create and show Mipmap Manager window
        manager = MipmapManagerWindow(self, self.selected_texture, self.main_window)
        manager.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"🔍 Opened Mipmap Manager for: {self.selected_texture['name']}")

    def _connect_texture_table_signals(self): #vers 1
        """Connect texture table signals for mipmap manager"""
        # Double-click to open mipmap manager
        self.texture_table.itemDoubleClicked.connect(self._on_texture_table_double_click)


    def _on_texture_selected(self): #vers 4
        """Handle texture selection - read-only, no modifications"""
        try:
            row = self.texture_table.currentRow()

            # Invalid selection
            if row < 0 or row >= len(self.texture_list):
                self.selected_texture = None
                self.export_btn.setEnabled(False)

                if hasattr(self, 'flip_btn'):
                    self.flip_btn.setEnabled(False)
                if hasattr(self, 'props_btn'):
                    self.props_btn.setEnabled(False)
                if hasattr(self, 'duplicate_btn'):
                    self.duplicate_btn.setEnabled(False)
                if hasattr(self, 'remove_btn'):
                    self.remove_btn.setEnabled(False)
                if hasattr(self, 'resize_btn'):
                    self.resize_btn.setEnabled(False)
                if hasattr(self, 'upscale_btn'):
                    self.upscale_btn.setEnabled(False)
                if hasattr(self, 'format_combo'):
                    self.format_combo.setEnabled(False)
                if hasattr(self, 'compress_btn'):
                    self.compress_btn.setEnabled(False)
                if hasattr(self, 'uncompress_btn'):
                    self.uncompress_btn.setEnabled(False)
                if hasattr(self, 'show_mipmaps_btn'):
                    self.show_mipmaps_btn.setEnabled(False)

                self._update_editing_controls()
                self._update_status_indicators()
                return

            # Valid selection - set selected texture
            self.selected_texture = self.texture_list[row]

            # Update display (read-only)
            self._update_texture_info(self.selected_texture)

            # Enable buttons based on selection
            self.export_btn.setEnabled(True)

            if hasattr(self, 'props_btn'):
                self.props_btn.setEnabled(True)
            if hasattr(self, 'duplicate_btn'):
                self.duplicate_btn.setEnabled(True)
            if hasattr(self, 'remove_btn'):
                self.remove_btn.setEnabled(True)
            if hasattr(self, 'resize_btn'):
                self.resize_btn.setEnabled(True)
            if hasattr(self, 'upscale_btn'):
                self.upscale_btn.setEnabled(True)
            if hasattr(self, 'format_combo'):
                self.format_combo.setEnabled(True)
            if hasattr(self, 'compress_btn'):
                self.compress_btn.setEnabled(True)
            if hasattr(self, 'uncompress_btn'):
                self.uncompress_btn.setEnabled(True)

            # Flip button - enable only if has alpha
            if hasattr(self, 'flip_btn'):
                has_alpha = self.selected_texture.get('has_alpha', False)
                self.flip_btn.setEnabled(has_alpha)
                if has_alpha:
                    self.flip_btn.setText("Switch")
                    self.flip_btn.setToolTip("Toggle between normal and alpha view")
                else:
                    self.flip_btn.setText("Switch")
                    self.flip_btn.setToolTip("No alpha channel to view")

            # Mipmap button - enable only if has mipmaps
            if hasattr(self, 'show_mipmaps_btn'):
                has_mipmaps = len(self.selected_texture.get('mipmap_levels', [])) > 1
                self.show_mipmaps_btn.setEnabled(has_mipmaps)

            # Enable transform buttons if they exist
            if hasattr(self, 'flip_vert_btn'):
                self.flip_vert_btn.setEnabled(True)
            if hasattr(self, 'flip_horz_btn'):
                self.flip_horz_btn.setEnabled(True)
            if hasattr(self, 'rotate_cw_btn'):
                self.rotate_cw_btn.setEnabled(True)
            if hasattr(self, 'rotate_ccw_btn'):
                self.rotate_ccw_btn.setEnabled(True)
            if hasattr(self, 'copy_btn'):
                self.copy_btn.setEnabled(True)
            if hasattr(self, 'paste_btn'):
                self.paste_btn.setEnabled(True)
            if hasattr(self, 'edit_btn'):
                self.edit_btn.setEnabled(True)
            if hasattr(self, 'convert_btn'):
                self.convert_btn.setEnabled(True)

            self._update_editing_controls()
            self._update_status_indicators()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Selection error: {str(e)}")

    def _reload_texture_table(self): #vers 2
        """Reload texture table display with mipmap info"""
        self.texture_table.setRowCount(0)

        for tex in self.texture_list:
            row = self.texture_table.rowCount()
            self.texture_table.insertRow(row)

            thumb_item = QTableWidgetItem()
            if tex.get('rgba_data') and tex['width'] > 0:
                pixmap = self._create_thumbnail(tex['rgba_data'], tex['width'], tex['height'])
                if pixmap:
                    thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
                else:
                    thumb_item.setText("🖼️")
            else:
                thumb_item.setText("🖼️")

            # Build details with mipmap info
            depth = tex.get('depth', 32)
            details = f"Name: {tex['name']} - {depth}bit\n"

            if tex.get('has_alpha', False):
                alpha_name = tex.get('alpha_name', tex['name'] + 'a')
                details += f"Alpha: {alpha_name}\n"
            else:
                details += "\n"

            if tex['width'] > 0:
                details += f"Size: {tex['width']}x{tex['height']} | Format: {tex['format']}\n"
            else:
                details += f"Format: {tex['format']}\n"

            # Mipmap info
            mipmap_levels = tex.get('mipmap_levels', [])
            num_mipmaps = len(mipmap_levels)

            if num_mipmaps > 0:
                is_compressed = 'DXT' in tex['format']
                compress_status = "compressed" if is_compressed else "uncompressed"
                details += f"📊 {num_mipmaps} mipmap levels ({compress_status}) - Click to view"
            else:
                details += "📊 No mipmaps"

            thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            details_item = QTableWidgetItem(details)
            details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.texture_table.setItem(row, 0, thumb_item)
            self.texture_table.setItem(row, 1, details_item)

        for row in range(self.texture_table.rowCount()):
            self.texture_table.setRowHeight(row, 100)
        self.texture_table.setColumnWidth(0, 80)


    def _save_undo_state(self, action_name): #vers 1
        """Save current state to undo stack"""
        import copy
        state = {
            'action': action_name,
            'texture_list': copy.deepcopy(self.texture_list)
        }
        self.undo_stack.append(state)

        # Limit undo stack to 10 items
        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)


    def _undo_last_action(self): #vers 1
        """Undo the last action"""
        if not self.undo_stack:
            QMessageBox.information(self, "Undo", "Nothing to undo")
            return

        previous_state = self.undo_stack.pop()
        self.texture_list = previous_state['texture_list']
        self._reload_texture_table()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"↶ Undo: {previous_state['action']}")

    def _auto_generate_mipmaps(self): #vers 1
        """Auto-generate all mipmap levels from main texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get main texture (level 0)
        main_rgba = self.selected_texture.get('rgba_data')
        if not main_rgba:
            QMessageBox.warning(self, "No Data", "Texture has no image data")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']

            # Convert to QImage
            source_image = QImage(main_rgba, width, height, width * 4, QImage.Format.Format_RGBA8888)

            if source_image.isNull():
                QMessageBox.warning(self, "Error", "Failed to create source image")
                return

            # Clear existing mipmap levels except level 0
            if 'mipmap_levels' not in self.selected_texture:
                self.selected_texture['mipmap_levels'] = []

            # Keep level 0 if it exists
            level_0 = None
            for level in self.selected_texture['mipmap_levels']:
                if level['level'] == 0:
                    level_0 = level
                    break

            # Start fresh
            self.selected_texture['mipmap_levels'] = []

            # Add level 0
            if level_0:
                self.selected_texture['mipmap_levels'].append(level_0)
            else:
                self.selected_texture['mipmap_levels'].append({
                    'level': 0,
                    'width': width,
                    'height': height,
                    'rgba_data': main_rgba,
                    'compressed_data': None,
                    'compressed_size': len(main_rgba)
                })

            # Generate remaining levels
            current_width = width // 2
            current_height = height // 2
            level_num = 1

            while current_width >= 1 and current_height >= 1:
                # Scale down
                scaled_image = source_image.scaled(
                    current_width, current_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                if scaled_image.isNull():
                    break

                # Convert to RGBA
                scaled_image = scaled_image.convertToFormat(QImage.Format.Format_RGBA8888)
                ptr = scaled_image.bits()
                ptr.setsize(scaled_image.sizeInBytes())
                rgba_data = bytes(ptr)

                # Add mipmap level
                mipmap_level = {
                    'level': level_num,
                    'width': current_width,
                    'height': current_height,
                    'rgba_data': rgba_data,
                    'compressed_data': None,
                    'compressed_size': len(rgba_data)
                }
                self.selected_texture['mipmap_levels'].append(mipmap_level)

                # Next level
                current_width = max(1, current_width // 2)
                current_height = max(1, current_height // 2)
                level_num += 1

            # Update mipmap count
            self.selected_texture['mipmaps'] = len(self.selected_texture['mipmap_levels'])

            # Update display
            self._update_texture_info(self.selected_texture)
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Generated {level_num} mipmap levels")

            QMessageBox.information(self, "Success",
                f"Generated {level_num} mipmap levels\n"
                f"From {width}x{height} down to {current_width*2}x{current_height*2}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mipmaps: {str(e)}")

    def _show_texture_context_menu(self, position): #vers 2
        """Show context menu for texture operations - simplified"""
        if not self.selected_texture:
            return

        has_alpha = self.selected_texture.get('has_alpha', False)

        menu = QMenu(self)

        # Import submenu
        import_menu = menu.addMenu(self._create_import_icon(), "Import")

        import_normal_action = import_menu.addAction("Import Texture")
        import_normal_action.triggered.connect(self._import_normal_texture)

        if has_alpha:
            import_alpha_action = import_menu.addAction("Import Alpha Channel")
            import_alpha_action.triggered.connect(self._import_alpha_texture)

        # Export submenu
        export_menu = menu.addMenu(self._create_export_icon(), "Export")

        export_texture_action = export_menu.addAction("Export Texture")
        export_texture_action.triggered.connect(self.export_selected_texture)

        if has_alpha:
            export_alpha_action = export_menu.addAction("Export Alpha Channel")
            export_alpha_action.triggered.connect(self._export_alpha_only)

        menu.addSeparator()

        # Delete texture
        delete_action = menu.addAction(self._create_trash_icon(), "Delete Texture")
        delete_action.triggered.connect(self._delete_texture)

        menu.exec(self.texture_table.viewport().mapToGlobal(position))

    def load_from_img_archive(self, img_path): #vers 1
        """Load TXD list from IMG archive"""
        try:
            if self.main_window and hasattr(self.main_window, 'current_img'):
                self.current_img = self.main_window.current_img
            else:
                from methods.img_core_classes import IMGFile
                self.current_img = IMGFile(img_path)
                self.current_img.open()

            img_name = os.path.basename(img_path)
            self.setWindowTitle(f"TXD Workshop: {img_name}")
            self._load_img_txd_list()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ TXD Workshop loaded: {img_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load IMG: {str(e)}")

    def _load_img_txd_list(self): #vers 1
        """Load TXD files from IMG archive"""
        try:
            self.txd_list_widget.clear()
            self.txd_list = []

            if not self.current_img:
                return

            for entry in self.current_img.entries:
                if entry.name.lower().endswith('.txd'):
                    self.txd_list.append(entry)
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, entry)
                    size_kb = entry.size / 1024
                    item.setToolTip(f"{entry.name}\nSize: {size_kb:.1f} KB")
                    self.txd_list_widget.addItem(item)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"📋 Found {len(self.txd_list)} TXD files")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error loading TXD list: {str(e)}")

    def _on_txd_selected(self, item): #vers 1
        """Handle TXD file selection"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                txd_data = self._extract_txd_from_img(entry)
                if txd_data:
                    self.current_txd_data = txd_data
                    self.current_txd_name = entry.name
                    self._load_txd_textures(txd_data, entry.name)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error selecting TXD: {str(e)}")

    def _extract_txd_from_img(self, entry): #vers 2
        """Extract TXD data from IMG entry"""
        try:
            if not self.current_img:
                return None
            return self.current_img.read_entry_data(entry)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Extract error: {str(e)}")
            return None

    def _load_txd_textures(self, txd_data, txd_name): #vers 11
        """Load textures from TXD data - display with mipmap info"""
        try:
            import struct

            self.texture_table.setRowCount(0)
            self.texture_list = []
            textures = []
            offset = 12

            # Get texture count
            texture_count = 0
            if offset + 12 < len(txd_data):
                try:
                    st, ss, sv = struct.unpack('<III', txd_data[offset:offset+12])
                    offset += 12
                    if ss >= 4:
                        texture_count = struct.unpack('<I', txd_data[offset:offset+4])[0]
                        offset += ss
                except:
                    pass

            # Parse each texture
            if 0 < texture_count < 500:
                for i in range(texture_count):
                    if offset + 12 > len(txd_data):
                        break
                    try:
                        stype, ssize, sver = struct.unpack('<III', txd_data[offset:offset+12])
                        if stype == 0x15:  # Texture Native
                            tex = self._parse_single_texture(txd_data, offset, i)
                            if tex:
                                textures.append(tex)
                        offset += 12 + ssize
                    except:
                        offset += 1000
                        continue

            if not textures:
                textures = [{'name': 'No textures', 'width': 0, 'height': 0, 'has_alpha': False,
                            'format': 'Unknown', 'mipmaps': 0, 'rgba_data': None, 'mipmap_levels': []}]

            # Populate table with mipmap info
            for tex in textures:
                self.texture_list.append(tex)
                row = self.texture_table.rowCount()
                self.texture_table.insertRow(row)

                thumb_item = QTableWidgetItem()
                if tex.get('rgba_data') and tex['width'] > 0:
                    pixmap = self._create_thumbnail(tex['rgba_data'], tex['width'], tex['height'])
                    if pixmap:
                        thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
                    else:
                        thumb_item.setText("🖼️")
                else:
                    thumb_item.setText("🖼️")

                # Build details text with mipmap info
                depth = tex.get('depth', 32)
                details = f"Name: {tex['name']} - {depth}bit\n"

                # Alpha name line
                if tex.get('has_alpha', False):
                    alpha_name = tex.get('alpha_name', tex['name'] + 'a')
                    details += f"Alpha: {alpha_name}\n"
                else:
                    details += "\n"  # Empty line for spacing

                # Size and format line
                if tex['width'] > 0:
                    details += f"Size: {tex['width']}x{tex['height']} | Format: {tex['format']}\n"
                else:
                    details += f"Format: {tex['format']}\n"

                # Mipmap info line - CLICKABLE
                mipmap_levels = tex.get('mipmap_levels', [])
                num_mipmaps = len(mipmap_levels)

                if num_mipmaps > 0:
                    # Check if compressed
                    is_compressed = 'DXT' in tex['format']
                    compress_status = "compressed" if is_compressed else "uncompressed"
                    details += f"📊 {num_mipmaps} mipmap levels ({compress_status}) - Click to view"
                else:
                    details += "📊 No mipmaps"

                # Make items non-editable
                thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                details_item = QTableWidgetItem(details)
                details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.texture_table.setItem(row, 0, thumb_item)
                self.texture_table.setItem(row, 1, details_item)

            for row in range(self.texture_table.rowCount()):
                self.texture_table.setRowHeight(row, 100)  # Increased height for mipmap line
            self.texture_table.setColumnWidth(0, 80)

            self.save_txd_btn.setEnabled(False)
            self.import_btn.setEnabled(True)
            self.export_all_btn.setEnabled(True)
            self._initialize_features()
            self._enable_txd_features_after_load()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Loaded {len(textures)} textures from {txd_name}")
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error: {str(e)}")

    def _upscale_texture(self): #vers 2
        """AI upscale selected texture with size management"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get scale factor
        factor, ok = QInputDialog.getInt(self, "AI Upscale", "Scale factor:", value=2, min=2, max=8)
        if not ok:
            return

        current_width = self.selected_texture.get('width', 256)
        current_height = self.selected_texture.get('height', 256)

        new_width = current_width * factor
        new_height = current_height * factor

        # Calculate memory and file size impact
        old_size_mb = (current_width * current_height * 4) / (1024 * 1024)
        new_size_mb = (new_width * new_height * 4) / (1024 * 1024)

        if new_size_mb > 16:  # Warn for textures over 16MB uncompressed
            reply = QMessageBox.question(self, "Large Upscale",
                                    f"Upscaling {factor}x will create a {new_width}x{new_height} texture "
                                    f"(~{new_size_mb:.1f}MB uncompressed). "
                                    f"This will significantly increase TXD size. Continue?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Perform the upscale
        if self._perform_ai_upscale(factor):
            self.selected_texture['width'] = new_width
            self.selected_texture['height'] = new_height

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscaled texture {factor}x to {new_width}x{new_height}")
        else:
            QMessageBox.critical(self, "Error", "AI upscale failed")

    def _perform_ai_upscale(self, factor): #vers 1
        """Perform AI upscaling on texture data"""
        try:
            if not self.selected_texture.get('rgba_data'):
                return False

            # For now, use basic upscaling (could be with actual AI upscaling libraries)
            return self._resize_texture_data(
                self.selected_texture['width'] * factor,
                self.selected_texture['height'] * factor
            )

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"AI upscale error: {str(e)}")
            return False

    def export_selected_texture(self): #vers 2
        """Export selected texture with channel options"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            name = self.selected_texture.get('name', 'texture')

            # Ask user what to export
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Export Options")
            dialog.setText(f"Export {name} as:")

            normal_btn = dialog.addButton("Normal (RGBA)", QMessageBox.ButtonRole.AcceptRole)
            alpha_btn = dialog.addButton("Alpha Channel Only", QMessageBox.ButtonRole.AcceptRole)
            both_btn = dialog.addButton("Both Separately", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

            dialog.exec()
            clicked = dialog.clickedButton()

            if clicked == cancel_btn:
                return

            # Get save location
            default_name = f"{name}.png"
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Texture", default_name,
                                                    "PNG Files (*.png);;All Files (*)")

            if not file_path:
                return

            rgba_data = self.selected_texture.get('rgba_data')
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if not rgba_data or width <= 0:
                QMessageBox.critical(self, "Error", "Cannot export this texture")
                return

            if clicked == normal_btn:
                self._save_texture_png(rgba_data, width, height, file_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported: {file_path}")

            elif clicked == alpha_btn:
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, file_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported alpha: {file_path}")

            elif clicked == both_btn:
                # Save normal
                self._save_texture_png(rgba_data, width, height, file_path)
                # Save alpha
                alpha_path = file_path.replace('.png', '_alpha.png')
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, alpha_path)
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Exported both: {file_path} and {alpha_path}")

            QMessageBox.information(self, "Success", "Texture exported successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def export_all_textures(self): #vers 1
        """Export all textures in current TXD"""
        if not self.texture_list:
            QMessageBox.warning(self, "No Textures", "No textures to export")
            return

        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        try:
            exported = 0
            for texture in self.texture_list:
                name = texture.get('name', f'texture_{exported}')
                rgba_data = texture.get('rgba_data')
                width = texture.get('width', 0)
                height = texture.get('height', 0)

                if rgba_data and width > 0:
                    file_path = os.path.join(output_dir, f"{name}.png")
                    self._save_texture_png(rgba_data, width, height, file_path)
                    exported += 1

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Exported {exported} textures to {output_dir}")

            QMessageBox.information(self, "Success", f"Exported {exported} textures successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def _extract_alpha_channel(self, rgba_data): #vers 1
        """Extract alpha channel as grayscale RGBA"""
        alpha_data = bytearray()
        for i in range(0, len(rgba_data), 4):
            a = rgba_data[i+3]
            alpha_data.extend([a, a, a, 255])
        return bytes(alpha_data)

    def _save_texture_png(self, rgba_data, width, height, file_path): #vers 1
        """Save RGBA data as PNG"""
        image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
        if not image.save(file_path):
            raise Exception("Failed to save PNG")

    def _export_alpha_only(self): #vers 1
        """Export only alpha channel"""
        if not self.selected_texture:
            return

        name = self.selected_texture.get('name', 'texture')
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Alpha Channel", f"{name}_alpha.png",
                                                "PNG Files (*.png)")
        if file_path:
            rgba_data = self.selected_texture.get('rgba_data')
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if rgba_data:
                alpha_data = self._extract_alpha_channel(rgba_data)
                self._save_texture_png(alpha_data, width, height, file_path)
                QMessageBox.information(self, "Success", "Alpha channel exported!")


    def _change_format(self, format_name): #vers 2
        """Change texture format - only set has_alpha if alpha data exists"""
        if not self.selected_texture:
            return

        old_format = self.selected_texture.get('format', 'Unknown')
        self.selected_texture['format'] = format_name

        # Check if texture actually has alpha data
        has_actual_alpha = False
        rgba_data = self.selected_texture.get('rgba_data')

        if rgba_data:
            # Check if any alpha values are not 255 (fully opaque)
            width = self.selected_texture.get('width', 0)
            height = self.selected_texture.get('height', 0)

            if width > 0 and height > 0:
                # Sample alpha channel - check every pixel's alpha value
                for i in range(3, len(rgba_data), 4):  # Every 4th byte is alpha
                    if rgba_data[i] < 255:  # Found non-opaque pixel
                        has_actual_alpha = True
                        break

        # Update alpha flag based on format AND actual alpha data
        if format_name in ['DXT3', 'DXT5', 'ARGB8888', 'ARGB1555', 'ARGB4444']:
            # Only set has_alpha if texture actually contains alpha data
            self.selected_texture['has_alpha'] = has_actual_alpha

            # If format supports alpha but texture doesn't have it, warn user
            if not has_actual_alpha:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"⚠️ {format_name} supports alpha, but texture has no alpha data")

        elif format_name in ['DXT1', 'RGB888', 'RGB565']:
            # These formats don't support alpha
            self.selected_texture['has_alpha'] = False

            # Remove alpha_name if switching to non-alpha format
            if 'alpha_name' in self.selected_texture:
                del self.selected_texture['alpha_name']

        self._update_texture_info(self.selected_texture)
        self._update_table_display()
        self._mark_as_modified()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            alpha_status = "with alpha" if self.selected_texture['has_alpha'] else "no alpha"
            self.main_window.log_message(f"Format changed: {old_format} -> {format_name} ({alpha_status})")


    def _compress_texture(self): #vers 3
        """Compress selected texture to DXT format"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_format = self.selected_texture.get('format', 'ARGB8888')

        if 'DXT' in current_format:
            # Already compressed - offer to change DXT version
            from PyQt6.QtWidgets import QInputDialog

            dxt_formats = ["DXT1", "DXT3", "DXT5"]
            new_format, ok = QInputDialog.getItem(
                self,
                "Change DXT Format",
                f"Current format: {current_format}\n\nSelect target DXT format:",
                dxt_formats,
                0,
                False
            )

            if ok and new_format != current_format:
                self._save_undo_state("Change DXT format")
                self.selected_texture['format'] = new_format

                # Update has_alpha based on format
                if new_format == 'DXT1':
                    # DXT1 can have 1-bit alpha, keep existing alpha state
                    pass
                elif new_format in ['DXT3', 'DXT5']:
                    # DXT3/DXT5 have alpha
                    if not self.selected_texture.get('has_alpha'):
                        self.selected_texture['has_alpha'] = True
                        if 'alpha_name' not in self.selected_texture:
                            self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

                # Update dropdown
                if hasattr(self, 'format_combo'):
                    index = self.format_combo.findText(new_format)
                    if index >= 0:
                        self.format_combo.setCurrentIndex(index)

                self._update_texture_info(self.selected_texture)
                self._update_table_display()
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Changed format: {current_format} → {new_format}")

            return

        # Not compressed - compress to DXT
        if not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Data", "Texture has no image data to compress")
            return

        try:
            # Let user choose DXT format
            from PyQt6.QtWidgets import QInputDialog

            has_alpha = self.selected_texture.get('has_alpha', False)

            if has_alpha:
                dxt_formats = ["DXT3", "DXT5", "DXT1"]
                default_format = "DXT5"
                message = "Texture has alpha channel.\n\nRecommended: DXT5 (best quality)\nAlternative: DXT3 (simpler alpha)\nDXT1: 1-bit alpha only"
            else:
                dxt_formats = ["DXT1", "DXT3", "DXT5"]
                default_format = "DXT1"
                message = "Texture has no alpha channel.\n\nRecommended: DXT1 (smallest size)"

            target_format, ok = QInputDialog.getItem(
                self,
                "Compress Texture",
                f"Current format: {current_format}\n\n{message}\n\nSelect DXT format:",
                dxt_formats,
                dxt_formats.index(default_format),
                False
            )

            if not ok:
                return

            # Save undo state
            self._save_undo_state("Compress texture")
            self.selected_texture['format'] = target_format

            # Update has_alpha if compressing to DXT3/DXT5
            if target_format in ['DXT3', 'DXT5'] and not has_alpha:
                self.selected_texture['has_alpha'] = True
                self.selected_texture['alpha_name'] = self.selected_texture['name'] + 'a'

            # Update dropdown
            if hasattr(self, 'format_combo'):
                index = self.format_combo.findText(target_format)
                if index >= 0:
                    self.format_combo.setCurrentIndex(index)

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Compressed: {current_format} → {target_format}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compress: {str(e)}")


    def _uncompress_texture(self): #vers 3
        """Uncompress selected texture from DXT to ARGB8888"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_format = self.selected_texture.get('format', 'ARGB8888')

        if 'DXT' not in current_format:
            QMessageBox.information(self, "Not Compressed", "Texture is not in DXT format")
            return

        try:
            reply = QMessageBox.question(
                self,
                "Uncompress Texture",
                f"Uncompress to ARGB8888?\n\n"
                f"Current: {current_format}\n"
                f"Target: ARGB8888\n\n"
                f"This will convert the texture to uncompressed format.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            if self.selected_texture.get('rgba_data'):
                self._save_undo_state("Uncompress texture")
                self.selected_texture['format'] = 'ARGB8888'

                # Update dropdown to show ARGB8888
                if hasattr(self, 'format_combo'):
                    index = self.format_combo.findText('ARGB8888')
                    if index >= 0:
                        self.format_combo.setCurrentIndex(index)

                self._update_texture_info(self.selected_texture)
                self._update_table_display()
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Uncompressed: {current_format} → ARGB8888")
            else:
                QMessageBox.warning(self, "No Data", "Texture has no decompressed data available")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to uncompress: {str(e)}")

    def _show_name_context_menu(self, position, alpha=False): #vers 1
        """Show context menu for renaming texture or alpha name"""
        if not self.selected_texture:
            return

        # Don't show alpha context menu if no alpha channel
        if alpha and not self.selected_texture.get('has_alpha', False):
            return

        menu = QMenu(self)

        if alpha:
            rename_action = menu.addAction("Rename Alpha")
            rename_action.triggered.connect(lambda: self._rename_texture(alpha=True))
        else:
            rename_action = menu.addAction("Rename Texture")
            rename_action.triggered.connect(lambda: self._rename_texture(alpha=False))

        # Show menu at the cursor position
        menu.exec(self.sender().mapToGlobal(position))

    def _calculate_new_txd_size(self): #vers 1
        """Calculate estimated new TXD size including actual texture data"""
        estimated_size = 1024  # Header overhead

        for texture in self.texture_list:
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            fmt = texture.get('format', 'DXT1')
            has_data = texture.get('rgba_data') is not None

            if has_data:
                # Use actual data size if available
                rgba_size = len(texture['rgba_data'])

                # Estimate compressed size based on format
                if 'DXT1' in fmt:
                    estimated_size += rgba_size // 8  # DXT1 compression
                elif 'DXT5' in fmt:
                    estimated_size += rgba_size // 4  # DXT5 compression
                else:
                    estimated_size += rgba_size  # Uncompressed
            else:
                # Fallback to dimension-based estimation
                if 'DXT1' in fmt:
                    estimated_size += (width * height) // 2
                elif 'DXT5' in fmt:
                    estimated_size += width * height
                else:
                    estimated_size += width * height * 4

            estimated_size += 200  # Header per texture

        return estimated_size

    def _rebuild_txd_data(self): #vers 1
        """Rebuild TXD data with modified texture names and properties"""
        try:
            import struct

            if not self.current_txd_data or not self.texture_list:
                return None

            # Start with original TXD data
            original_data = bytearray(self.current_txd_data)

            # Parse and update texture names and properties
            offset = 12

            # Skip to texture count
            if offset + 12 < len(original_data):
                st, ss, sv = struct.unpack('<III', original_data[offset:offset+12])
                offset += 12
                if ss >= 4:
                    texture_count = struct.unpack('<I', original_data[offset:offset+4])[0]
                    offset += ss

                    # Update each texture's data in the binary
                    texture_index = 0
                    for i in range(texture_count):
                        if offset + 12 > len(original_data) or texture_index >= len(self.texture_list):
                            break

                        stype, ssize, sver = struct.unpack('<III', original_data[offset:offset+12])
                        if stype == 0x15:  # Texture Native
                            # Update texture properties in binary data
                            self._update_texture_in_data(original_data, offset, self.texture_list[texture_index])
                            texture_index += 1

                        offset += 12 + ssize

            return bytes(original_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuild error: {str(e)}")
            return None

    def _update_texture_in_data(self, data, offset, texture_info): #vers 1
        """Update texture properties in the binary TXD data"""
        try:
            import struct

            # Navigate to the texture data location
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', data[struct_offset:struct_offset+12])

            if struct_type == 0x01:  # Struct section
                name_pos = struct_offset + 12 + 8  # Skip header and platform info

                # Update texture name (32 bytes)
                new_name = texture_info.get('name', 'texture')[:31]
                name_bytes = new_name.encode('ascii')[:31].ljust(32, b'\x00')
                data[name_pos:name_pos+32] = name_bytes

                # Update alpha/mask name if it exists (next 32 bytes)
                if texture_info.get('has_alpha', False) and texture_info.get('alpha_name'):
                    alpha_name = texture_info.get('alpha_name', '')[:31]
                    alpha_bytes = alpha_name.encode('ascii')[:31].ljust(32, b'\x00')
                    data[name_pos+32:name_pos+64] = alpha_bytes

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Name update error: {str(e)}")

    def _update_img_with_txd(self, modified_txd_data): #vers 3
        """Update IMG archive using IMG Factory's save system"""
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Starting IMG update via IMG Factory save system...")

            # Check prerequisites
            if not self.current_img:
                raise Exception("No current IMG file loaded")

            if not self.current_txd_name:
                raise Exception("No current TXD name available")

            # Find and update the TXD entry
            txd_entry = None
            for entry in self.current_img.entries:
                if entry.name == self.current_txd_name:
                    txd_entry = entry
                    break

            if not txd_entry:
                raise Exception(f"TXD entry '{self.current_txd_name}' not found in IMG")

            # Update the entry data
            old_size = txd_entry.size
            txd_entry.data = modified_txd_data
            txd_entry.size = len(modified_txd_data)

            # Mark IMG as modified
            if hasattr(self.current_img, 'modified'):
                self.current_img.modified = True

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"TXD entry updated in memory: {old_size} -> {len(modified_txd_data)} bytes")

            # Use IMG Factory's save system - try multiple methods in order of preference
            save_successful = False

            # Method 1: save_img_entry (most likely to work)
            if hasattr(self.main_window, 'save_img_entry'):
                try:
                    self.main_window.save_img_entry()
                    save_successful = True
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("Successfully used main_window.save_img_entry()")
                except Exception as e:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"save_img_entry failed: {str(e)}")

            # Method 2: save_entry (alias)
            if not save_successful and hasattr(self.main_window, 'save_entry'):
                try:
                    self.main_window.save_entry()
                    save_successful = True
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("Successfully used main_window.save_entry()")
                except Exception as e:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"save_entry failed: {str(e)}")

            # Method 3: Direct core save_entry import
            if not save_successful:
                try:
                    from core.save_entry import save_img_entry
                    save_img_entry(self.main_window)
                    save_successful = True
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("Successfully used core.save_entry.save_img_entry()")
                except ImportError:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("core.save_entry module not available")
                except Exception as e:
                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"core.save_entry failed: {str(e)}")

            if save_successful:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("IMG saved successfully using IMG Factory save system")
                return True
            else:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("Warning: All save methods failed - changes remain in memory only")
                return False

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG update error: {str(e)}")
            return False

    def _resize_texture(self): #vers 1
        """Resize selected texture with size validation"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Get current dimensions
        current_width = self.selected_texture.get('width', 256)
        current_height = self.selected_texture.get('height', 256)

        # Get new dimensions from user
        w, ok1 = QInputDialog.getInt(
            self, "Resize Texture", "New width:",
            value=current_width, min=1, max=4096
        )
        if not ok1:
            return

        h, ok2 = QInputDialog.getInt(
            self, "Resize Texture", "New height:",
            value=current_height, min=1, max=4096
        )
        if not ok2:
            return

        # Calculate size impact
        old_pixels = current_width * current_height
        new_pixels = w * h
        size_multiplier = new_pixels / old_pixels if old_pixels > 0 else 1

        # Warn for large size increases
        if size_multiplier > 4:
            reply = QMessageBox.question(
                self, "Large Resize",
                f"Resizing to {w}x{h} will increase texture size by {size_multiplier:.1f}x. "
                f"This may require IMG rebuilding. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Update texture dimensions
        self.selected_texture['width'] = w
        self.selected_texture['height'] = h

        # If we have RGBA data, resize it
        if self.selected_texture.get('rgba_data'):
            self._resize_texture_data(w, h)

        # Update display
        self._update_texture_info(self.selected_texture)
        self._update_table_display()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Resized texture to {w}x{h}")

    def _resize_texture_data(self, new_width, new_height): #vers 1
        """Resize the actual texture image data using QImage"""
        try:
            if not self.selected_texture.get('rgba_data'):
                return False

            # Convert current RGBA data to QImage
            rgba_data = self.selected_texture['rgba_data']
            old_width = self.selected_texture['width']
            old_height = self.selected_texture['height']

            qimg = QImage(rgba_data, old_width, old_height, old_width * 4, QImage.Format.Format_RGBA8888)

            # Resize image with high quality
            resized_img = qimg.scaled(new_width, new_height,
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)

            # Convert back to RGBA data
            resized_img = resized_img.convertToFormat(QImage.Format.Format_RGBA8888)

            # Get raw bytes from QImage
            ptr = resized_img.bits()
            ptr.setsize(resized_img.sizeInBytes())
            new_rgba_data = bytes(ptr)

            # Update texture data
            self.selected_texture['rgba_data'] = new_rgba_data
            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Resize data error: {str(e)}")
            return False

    def _update_table_display(self): #vers 2
        """Update the middle panel table display after edits"""
        if not self.selected_texture:
            return

        row = self.texture_table.currentRow()
        if row < 0 or row >= len(self.texture_list):
            return

        tex = self.selected_texture

        # Rebuild details text with compression status
        details = f"Name: {tex['name']}\n"

        # Add alpha name if texture has alpha
        if tex.get('has_alpha', False):
            alpha_name = tex.get('alpha_name', tex['name'] + 'a')
            details += f"Alpha: {alpha_name}\n"

        if tex['width'] > 0:
            details += f"Size: {tex['width']}x{tex['height']}\n"

        # Show format with compression status
        fmt = tex['format']
        if 'DXT' in fmt:
            details += f"Format: {fmt} (Compressed)\n"
        else:
            details += f"Format: {fmt} (Uncompressed)\n"

        details += f"Alpha: {'Yes' if tex.get('has_alpha', False) else 'No'}"

        # Update the table item
        details_item = self.texture_table.item(row, 1)
        if details_item:
            details_item.setText(details)

    def _parse_single_texture(self, txd_data, offset, index): #vers 16
        """Parse single texture with ALL mipmap levels"""
        import struct

        tex = {
            'name': f'texture_{index}',
            'width': 0,
            'height': 0,
            'has_alpha': False,
            'format': 'Unknown',
            'mipmaps': 1,
            'rgba_data': None,
            'mipmap_levels': []  # Store all mipmap levels
        }

        try:
            # TextureNative structure
            parent_type, parent_size, parent_version = struct.unpack('<III', txd_data[offset:offset+12])

            if parent_type != 0x15:
                return tex

            # Struct section
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', txd_data[struct_offset:struct_offset+12])

            if struct_type != 0x01:
                return tex

            pos = struct_offset + 12

            # Read 88-byte header
            platform_id, filter_mode, uv_addressing = struct.unpack('<I2B', txd_data[pos:pos+6])[:3]
            pos += 8  # Skip padding

            name_bytes = txd_data[pos:pos+32]
            tex['name'] = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore') or f'texture_{index}'
            pos += 32

            mask_bytes = txd_data[pos:pos+32]
            alpha_name = mask_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
            if alpha_name:
                tex['alpha_name'] = alpha_name
                tex['has_alpha'] = True  # If alpha_name exists, has_alpha is True
            pos += 32

            raster_format_flags, d3d_format, width, height, depth, num_levels, raster_type = struct.unpack('<IIHHBBB', txd_data[pos:pos+15])
            tex['width'] = width
            tex['height'] = height
            tex['depth'] = depth
            tex['mipmaps'] = num_levels
            pos += 15

            platform_prop = struct.unpack('<B', txd_data[pos:pos+1])[0]
            pos += 1

            # Format detection - only set has_alpha if not already set by alpha_name
            if platform_id == 8:  # D3D8
                if platform_prop == 1:
                    tex['format'] = 'DXT1'
                elif platform_prop == 3:
                    tex['format'] = 'DXT3'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif platform_prop == 5:
                    tex['format'] = 'DXT5'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif d3d_format == 21:  # ARGB8888
                    tex['format'] = 'ARGB8888'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif d3d_format == 22:  # RGB888
                    tex['format'] = 'RGB888'
                    # RGB888 can still have alpha channel if alpha_name exists
                elif d3d_format == 25:  # ARGB1555
                    tex['format'] = 'ARGB1555'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif d3d_format == 26:  # ARGB4444
                    tex['format'] = 'ARGB4444'
                    if not tex.get('has_alpha'):
                        tex['has_alpha'] = True
                elif d3d_format == 23:  # RGB565
                    tex['format'] = 'RGB565'
                    # RGB565 can still have alpha channel if alpha_name exists

            # Skip palette if present
            palette_type = (raster_format_flags >> 13) & 0b11
            if palette_type == 1:  # 8-bit palette
                pos += 1024
            elif palette_type > 1:  # 4-bit palette
                if depth == 4:
                    pos += 64
                else:
                    pos += 128

            # Parse ALL mipmap levels
            current_width = width
            current_height = height

            for level in range(num_levels):
                if pos + 4 >= len(txd_data):
                    break

                # Read size-prefixed pixel data for this level
                pixels_len = struct.unpack('<I', txd_data[pos:pos+4])[0]
                pos += 4

                if pos + pixels_len > len(txd_data):
                    break

                dxt_data = txd_data[pos:pos + pixels_len]
                pos += pixels_len

                # Decompress this mipmap level
                rgba_data = None
                if 'DXT1' in tex['format']:
                    rgba_data = self._decompress_dxt1(dxt_data, current_width, current_height)
                elif 'DXT3' in tex['format']:
                    rgba_data = self._decompress_dxt3(dxt_data, current_width, current_height)
                elif 'DXT5' in tex['format']:
                    rgba_data = self._decompress_dxt5(dxt_data, current_width, current_height)

                # Store this mipmap level
                mipmap_level = {
                    'level': level,
                    'width': current_width,
                    'height': current_height,
                    'rgba_data': rgba_data,
                    'compressed_data': dxt_data,
                    'compressed_size': pixels_len
                }
                tex['mipmap_levels'].append(mipmap_level)

                # Set main texture data to level 0
                if level == 0:
                    tex['rgba_data'] = rgba_data

                # Calculate next mipmap dimensions (half size, minimum 1)
                current_width = max(1, current_width // 2)
                current_height = max(1, current_height // 2)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    status = "✅" if rgba_data else "❌"
                    self.main_window.log_message(
                        f"{status} Level {level}: {mipmap_level['width']}x{mipmap_level['height']} ({pixels_len} bytes)"
                    )

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"ERROR parsing texture: {str(e)}")

        return tex

    def _decompress_dxt1(self, dxt_data, width, height): #vers 1
        """DXT1 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 8
                    if block_offset + 8 > len(dxt_data):
                        break

                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset:block_offset+4])
                    indices = struct.unpack('<I', dxt_data[block_offset+4:block_offset+8])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b, 255))

                    if c0 > c1:
                        colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3, 255))
                        colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3, 255))
                    else:
                        colors.append(((colors[0][0]+colors[1][0])//2, (colors[0][1]+colors[1][1])//2, (colors[0][2]+colors[1][2])//2, 255))
                        colors.append((0, 0, 0, 0))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                index = (indices >> ((py*4+px)*2)) & 0x03
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+4] = colors[index]
            return bytes(rgba)
        except:
            return None

    def _decompress_dxt3(self, dxt_data, width, height): #vers 1
        """DXT3 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 16
                    if block_offset + 16 > len(dxt_data):
                        break

                    alpha_data = struct.unpack('<Q', dxt_data[block_offset:block_offset+8])[0]
                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset+8:block_offset+12])
                    indices = struct.unpack('<I', dxt_data[block_offset+12:block_offset+16])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b))

                    colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3))
                    colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                color_index = (indices >> ((py*4+px)*2)) & 0x03
                                alpha_index = py*4 + px
                                alpha = ((alpha_data >> (alpha_index*4)) & 0x0F) * 17
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+3] = colors[color_index]
                                rgba[pixel_offset+3] = alpha
            return bytes(rgba)
        except:
            return None

    def _decompress_dxt5(self, dxt_data, width, height): #vers 1
        """DXT5 decompression"""
        try:
            import struct
            rgba = bytearray(width * height * 4)
            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    block_offset = (by * blocks_x + bx) * 16
                    if block_offset + 16 > len(dxt_data):
                        break

                    a0 = dxt_data[block_offset]
                    a1 = dxt_data[block_offset + 1]
                    alpha_indices = struct.unpack('<Q', dxt_data[block_offset:block_offset+8])[0] >> 16
                    alpha_palette = [a0, a1]
                    if a0 > a1:
                        for i in range(1, 7):
                            alpha_palette.append(((7-i)*a0+i*a1)//7)
                    else:
                        for i in range(1, 5):
                            alpha_palette.append(((5-i)*a0+i*a1)//5)
                        alpha_palette.extend([0, 255])

                    c0, c1 = struct.unpack('<HH', dxt_data[block_offset+8:block_offset+12])
                    indices = struct.unpack('<I', dxt_data[block_offset+12:block_offset+16])[0]

                    colors = []
                    for c in [c0, c1]:
                        r = ((c >> 11) & 0x1F) << 3
                        g = ((c >> 5) & 0x3F) << 2
                        b = (c & 0x1F) << 3
                        colors.append((r, g, b))

                    colors.append(((2*colors[0][0]+colors[1][0])//3, (2*colors[0][1]+colors[1][1])//3, (2*colors[0][2]+colors[1][2])//3))
                    colors.append(((colors[0][0]+2*colors[1][0])//3, (colors[0][1]+2*colors[1][1])//3, (colors[0][2]+2*colors[1][2])//3))

                    for py in range(4):
                        for px in range(4):
                            if (bx*4+px < width) and (by*4+py < height):
                                color_index = (indices >> ((py*4+px)*2)) & 0x03
                                alpha_index = (alpha_indices >> ((py*4+px)*3)) & 0x07
                                pixel_offset = ((by*4+py)*width+(bx*4+px))*4
                                rgba[pixel_offset:pixel_offset+3] = colors[color_index]
                                rgba[pixel_offset+3] = alpha_palette[alpha_index]
            return bytes(rgba)
        except:
            return None

    def _decompress_uncompressed(self, data, width, height, format_type): #vers 1
        """Decompress uncompressed formats"""
        try:
            import struct
            rgba = bytearray(width * height * 4)

            if 'ARGB8888' in format_type or 'ARGB32' in format_type:
                for i in range(width * height):
                    if i*4+4 <= len(data):
                        b,g,r,a = struct.unpack('BBBB', data[i*4:i*4+4])
                        rgba[i*4:i*4+4] = [r,g,b,a]

            elif 'RGB565' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        r = ((pixel >> 11) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x3F) << 2
                        b = (pixel & 0x1F) << 3
                        rgba[i*4:i*4+4] = [r,g,b,255]

            elif 'ARGB1555' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        a = 255 if (pixel & 0x8000) else 0
                        r = ((pixel >> 10) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x1F) << 3
                        b = (pixel & 0x1F) << 3
                        rgba[i*4:i*4+4] = [r,g,b,a]

            elif 'ARGB4444' in format_type:
                for i in range(width * height):
                    if i*2+2 <= len(data):
                        pixel = struct.unpack('<H', data[i*2:i*2+2])[0]
                        a = ((pixel >> 12) & 0x0F) * 17
                        r = ((pixel >> 8) & 0x0F) * 17
                        g = ((pixel >> 4) & 0x0F) * 17
                        b = (pixel & 0x0F) * 17
                        rgba[i*4:i*4+4] = [r,g,b,a]

            elif 'LUM8' in format_type or 'L8' in format_type:
                for i in range(width * height):
                    if i < len(data):
                        lum = data[i]
                        rgba[i*4:i*4+4] = [lum,lum,lum,255]

            return bytes(rgba)
        except:
            return None

    def _create_thumbnail(self, rgba_data, width, height): #vers 1
        """Create thumbnail from RGBA data"""
        try:
            if not rgba_data or width <= 0 or height <= 0:
                return None

            image = QImage(rgba_data, width, height, width*4, QImage.Format.Format_RGBA8888)
            if image.isNull():
                return None

            pixmap = QPixmap.fromImage(image)
            return pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        except:
            return None


    def _create_transform_panel(self): #vers 2
        """Create transform and edit controls panel with SVG icons"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(150)
        panel.setMaximumWidth(200)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        header = QLabel("Transform")
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header)

        # Flip operations with SVG icons
        self.flip_vert_btn = QPushButton()
        self.flip_vert_btn.setIcon(self._create_flip_vert_icon())
        self.flip_vert_btn.setText("Flip Vertical")
        self.flip_vert_btn.clicked.connect(self._flip_vertical)
        self.flip_vert_btn.setEnabled(False)
        self.flip_vert_btn.setToolTip("Flip texture vertically")
        self.flip_vert_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.flip_vert_btn)

        self.flip_horz_btn = QPushButton()
        self.flip_horz_btn.setIcon(self._create_flip_horz_icon())
        self.flip_horz_btn.setText("Flip Horizontal")
        self.flip_horz_btn.clicked.connect(self._flip_horizontal)
        self.flip_horz_btn.setEnabled(False)
        self.flip_horz_btn.setToolTip("Flip texture horizontally")
        self.flip_horz_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.flip_horz_btn)

        layout.addSpacing(5)

        # Rotate operations with SVG icons
        self.rotate_cw_btn = QPushButton()
        self.rotate_cw_btn.setIcon(self._create_rotate_cw_icon())
        self.rotate_cw_btn.setText("Rotate 90° CW")
        self.rotate_cw_btn.clicked.connect(self._rotate_clockwise)
        self.rotate_cw_btn.setEnabled(False)
        self.rotate_cw_btn.setToolTip("Rotate 90 degrees clockwise")
        self.rotate_cw_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.rotate_cw_btn)

        self.rotate_ccw_btn = QPushButton()
        self.rotate_ccw_btn.setIcon(self._create_rotate_ccw_icon())
        self.rotate_ccw_btn.setText("Rotate 90° CCW")
        self.rotate_ccw_btn.clicked.connect(self._rotate_counterclockwise)
        self.rotate_ccw_btn.setEnabled(False)
        self.rotate_ccw_btn.setToolTip("Rotate 90 degrees counter-clockwise")
        self.rotate_ccw_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.rotate_ccw_btn)

        layout.addSpacing(10)

        # Edit operations with SVG icons
        edit_header = QLabel("Edit")
        edit_header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(edit_header)

        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(self._create_copy_icon())
        self.copy_btn.setText("Copy")
        self.copy_btn.clicked.connect(self._copy_texture)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setToolTip("Copy texture to clipboard")
        self.copy_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.copy_btn)

        self.paste_btn = QPushButton()
        self.paste_btn.setIcon(self._create_paste_icon())
        self.paste_btn.setText("Paste")
        self.paste_btn.clicked.connect(self._paste_texture)
        self.paste_btn.setEnabled(False)
        self.paste_btn.setToolTip("Paste texture from clipboard")
        self.paste_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.paste_btn)

        layout.addSpacing(5)

        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(self._create_edit_icon())
        self.edit_btn.setText("Edit")
        self.edit_btn.clicked.connect(self._edit_texture_external)
        self.edit_btn.setEnabled(False)
        self.edit_btn.setToolTip("Edit in external editor (coming soon)")
        self.edit_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.edit_btn)

        self.convert_btn = QPushButton()
        self.convert_btn.setIcon(self._create_convert_icon())
        self.convert_btn.setText("Convert")
        self.convert_btn.clicked.connect(self._convert_texture_format)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setToolTip("Convert format (coming soon)")
        self.convert_btn.setIconSize(QSize(20, 20))
        layout.addWidget(self.convert_btn)

        layout.addStretch()

        return panel


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
        """Open TXD - File icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_save_icon(self): #vers 1
        """Save TXD - Floppy disk icon"""
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
        """Create New TXD - Document icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2"/>
            <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_undo_icon(self): #vers 1
        """Undo - Curved arrow icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


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
            <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data)


    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data)




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

    def _update_texture_info(self, texture): #vers 8
        """Update texture information display with compression status"""
        try:
            name = texture.get('name', 'Unknown')
            width = texture.get('width', 0)
            height = texture.get('height', 0)
            has_alpha = texture.get('has_alpha', False)
            fmt = texture.get('format', 'Unknown')
            depth = texture.get('depth', 32)

            # Line 1: Name and bit depth
            self.info_name.setText(f"Name: {name} - {depth}bit")

            # Line 2: Alpha name (if exists)
            if has_alpha:
                alpha_name = texture.get('alpha_name', name + 'a')
                self.info_alpha_name.setText(f"Alpha: {alpha_name}")
                self.info_alpha_name.setVisible(True)
            else:
                self.info_alpha_name.setText("Alpha: -")
                self.info_alpha_name.setVisible(False)

            # Line 3: Size
            self.info_size.setText(f"Size: {width}x{height}" if width > 0 else "Size: Unknown")

            # Line 4: Format with compression status
            if 'DXT' in fmt:
                compression_status = "Compressed"
            else:
                compression_status = "Uncompressed"

            if hasattr(self, 'format_status_label'):
                self.format_status_label.setText(f"Format: {fmt} ({compression_status})")

            # Update bit depth indicator
            if hasattr(self, 'info_bitdepth'):
                self.info_bitdepth.setText(f"[{depth}bit]")

            # Line 5: Mipmaps info
            num_mipmaps = len(texture.get('mipmap_levels', []))
            if num_mipmaps > 1:
                self.info_format.setText(f"Mipmaps: {num_mipmaps} levels")
            elif num_mipmaps == 1:
                self.info_format.setText(f"Mipmaps: 1 level (no mipmaps)")
            else:
                self.info_format.setText(f"Mipmaps: None")

            # Update preview image
            rgba_data = texture.get('rgba_data')
            if rgba_data and width > 0 and height > 0:
                try:
                    # Create QImage from RGBA data
                    qimg = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

                    # Scale to fit preview area (max 400x400)
                    scaled = qimg.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                    # Convert to pixmap and display
                    pixmap = QPixmap.fromImage(scaled)
                    self.preview_label.setPixmap(pixmap)
                    self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                except Exception as e:
                    self.preview_label.setText(f"Preview error: {str(e)}")
            else:
                self.preview_label.setText("No preview available")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Update info error: {str(e)}")

    def _extract_alpha_for_display(self, rgba_data): #vers 1
        """Extract alpha channel as grayscale for display"""
        alpha_display = bytearray()
        for i in range(3, len(rgba_data), 4):
            a = rgba_data[i]
            alpha_display.extend([a, a, a, 255])  # Grayscale with full opacity
        return bytes(alpha_display)


    def _flip_vertical(self): #vers 2
        """Flip texture vertically"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = bytearray(self.selected_texture['rgba_data'])

            # Flip vertically - swap rows
            flipped = bytearray(len(rgba_data))
            for y in range(height):
                for x in range(width):
                    src_idx = (y * width + x) * 4
                    dst_idx = ((height - 1 - y) * width + x) * 4
                    flipped[dst_idx:dst_idx+4] = rgba_data[src_idx:src_idx+4]

            self._save_undo_state("Flip vertical")
            self.selected_texture['rgba_data'] = bytes(flipped)
            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Flipped texture vertically")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")


    def _flip_horizontal(self): #vers 1
        """Flip texture horizontally"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = bytearray(self.selected_texture['rgba_data'])

            # Flip horizontally - swap columns
            flipped = bytearray(len(rgba_data))
            for y in range(height):
                for x in range(width):
                    src_idx = (y * width + x) * 4
                    dst_idx = (y * width + (width - 1 - x)) * 4
                    flipped[dst_idx:dst_idx+4] = rgba_data[src_idx:src_idx+4]

            self._save_undo_state("Flip horizontal")
            self.selected_texture['rgba_data'] = bytes(flipped)
            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Flipped texture horizontally")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to flip: {str(e)}")


    def _rotate_clockwise(self): #vers 1
        """Rotate texture 90 degrees clockwise"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = self.selected_texture['rgba_data']

            # Use QImage for rotation
            from PyQt6.QtGui import QImage, QTransform
            img = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

            transform = QTransform().rotate(90)
            rotated = img.transformed(transform)

            # Get rotated data
            ptr = rotated.bits()
            ptr.setsize(rotated.sizeInBytes())
            rotated_data = bytes(ptr)

            self._save_undo_state("Rotate 90° CW")
            self.selected_texture['rgba_data'] = rotated_data
            self.selected_texture['width'] = rotated.width()
            self.selected_texture['height'] = rotated.height()

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Rotated 90° CW: now {rotated.width()}x{rotated.height()}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate: {str(e)}")


    def _rotate_counterclockwise(self): #vers 1
        """Rotate texture 90 degrees counter-clockwise"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = self.selected_texture['rgba_data']

            # Use QImage for rotation
            from PyQt6.QtGui import QImage, QTransform
            img = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

            transform = QTransform().rotate(-90)
            rotated = img.transformed(transform)

            # Get rotated data
            ptr = rotated.bits()
            ptr.setsize(rotated.sizeInBytes())
            rotated_data = bytes(ptr)

            self._save_undo_state("Rotate 90° CCW")
            self.selected_texture['rgba_data'] = rotated_data
            self.selected_texture['width'] = rotated.width()
            self.selected_texture['height'] = rotated.height()

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Rotated 90° CCW: now {rotated.width()}x{rotated.height()}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate: {str(e)}")


    def _copy_texture(self): #vers 1
        """Copy texture to clipboard"""
        if not self.selected_texture or not self.selected_texture.get('rgba_data'):
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            from PyQt6.QtGui import QImage, QClipboard
            from PyQt6.QtWidgets import QApplication

            width = self.selected_texture['width']
            height = self.selected_texture['height']
            rgba_data = self.selected_texture['rgba_data']

            img = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

            clipboard = QApplication.clipboard()
            clipboard.setImage(img)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Copied texture to clipboard: {self.selected_texture['name']}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {str(e)}")


    def _paste_texture(self): #vers 1
        """Paste texture from clipboard"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        try:
            from PyQt6.QtGui import QClipboard
            from PyQt6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            img = clipboard.image()

            if img.isNull():
                QMessageBox.warning(self, "No Image", "No image in clipboard")
                return

            # Convert to RGBA8888
            img = img.convertToFormat(QImage.Format.Format_RGBA8888)

            width = img.width()
            height = img.height()
            ptr = img.bits()
            ptr.setsize(img.sizeInBytes())
            rgba_data = bytes(ptr)

            self._save_undo_state("Paste texture")
            self.selected_texture['width'] = width
            self.selected_texture['height'] = height
            self.selected_texture['rgba_data'] = rgba_data

            self._update_texture_info(self.selected_texture)
            self._update_table_display()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Pasted texture from clipboard: {width}x{height}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to paste: {str(e)}")


    def _edit_texture_external(self): #vers 1
        """Edit texture in external editor (placeholder)"""
        QMessageBox.information(self, "Coming Soon",
            "External editor integration will be added soon!\n\n"
            "Will support:\n"
            "• Open in GIMP/Photoshop\n"
            "• Auto-reload on save\n"
            "• Custom editor paths")


    def _convert_texture_format(self): #vers 1
        """Convert texture format (placeholder)"""
        QMessageBox.information(self, "Coming Soon",
            "Format conversion tools will be added soon!\n\n"
            "Will support:\n"
            "• Batch DXT compression\n"
            "• Color depth conversion\n"
            "• Palette generation")


    def flip_texture(self): #vers 2
        """Flip between normal and alpha channel view (only if alpha exists)"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        # Check if texture has alpha
        if not self.selected_texture.get('has_alpha', False):
            QMessageBox.information(self, "No Alpha",
                "This texture has no alpha channel to view.\n\n"
                "Use 'Import → Import Alpha Channel' to add one.")
            return

        # Toggle alpha view flag
        if not hasattr(self, '_show_alpha'):
            self._show_alpha = False

        self._show_alpha = not self._show_alpha
        self._update_texture_info(self.selected_texture)

        mode = "Alpha Channel" if self._show_alpha else "Normal View"

        # Update flip button text if it exists
        if hasattr(self, 'flip_btn'):
            self.flip_btn.setText("🔄 Normal" if self._show_alpha else "🔄 Alpha")

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Switched to {mode}")


    def save_txd_file(self): #vers 3
        """Save TXD file with debugging"""
        if not self.texture_list or not self.current_txd_name:
            QMessageBox.warning(self, "No TXD", "No TXD file loaded to save")
            return

        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Starting TXD rebuild...")

            # Check prerequisites
            if not self.current_txd_data:
                raise Exception("No current TXD data available")

            if not self.texture_list:
                raise Exception("No texture list available")

            # Try to rebuild
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                raise Exception("_rebuild_txd_data returned None or empty data")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuild successful: {len(modified_txd_data)} bytes")

            # Rest of save logic...
            QMessageBox.information(self, "Debug", f"Rebuild successful: {len(modified_txd_data)} bytes")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"TXD rebuild failed: {str(e)}")
            QMessageBox.critical(self, "Debug Error", f"TXD rebuild failed: {str(e)}")


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

    def _rename_texture(self, alpha=False): #vers 2
        """Rename texture or alpha name and mark as modified"""
        from PyQt6.QtWidgets import QInputDialog

        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        current_name = self.selected_texture.get('name', 'texture')

        if alpha:
            if not self.selected_texture.get('has_alpha', False):
                QMessageBox.information(self, "No Alpha", "This texture does not have an alpha channel")
                return

            alpha_name = self.selected_texture.get('alpha_name', current_name + 'a')
            new_name, ok = QInputDialog.getText(self, "Rename Alpha", "Enter alpha name:", text=alpha_name)
            if ok and new_name and new_name != alpha_name:
                self.selected_texture['alpha_name'] = new_name
                self.info_alpha_name.setText(f"Alpha: {new_name}")
                self._update_table_display()
                self._mark_as_modified()  # Mark as modified
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Alpha renamed to: {new_name}")
        else:
            new_name, ok = QInputDialog.getText(self, "Rename Texture", "Enter texture name:", text=current_name)
            if ok and new_name and new_name != current_name:
                self.selected_texture['name'] = new_name
                self.info_name.setText(f"Name: {new_name}")
                self._update_table_display()
                self._mark_as_modified()  # Mark as modified
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Texture renamed: {current_name} -> {new_name}")

    def _update_texture_name_in_data(self, data, offset, texture_info): #vers 1
        """Update texture name in the binary TXD data"""
        try:
            import struct

            # Navigate to the texture name location (offset + 12 for section header + 8 for platform info + name at pos 32)
            struct_offset = offset + 12
            struct_type, struct_size, struct_version = struct.unpack('<III', data[struct_offset:struct_offset+12])

            if struct_type == 0x01:  # Struct section
                name_pos = struct_offset + 12 + 8  # Skip header and platform info

                # Update texture name (32 bytes)
                new_name = texture_info.get('name', 'texture')[:31]  # Max 31 chars + null terminator
                name_bytes = new_name.encode('ascii')[:31].ljust(32, b'\x00')
                data[name_pos:name_pos+32] = name_bytes

                # Update alpha/mask name if it exists (next 32 bytes)
                if texture_info.get('has_alpha', False) and texture_info.get('alpha_name'):
                    alpha_name = texture_info.get('alpha_name', '')[:31]
                    alpha_bytes = alpha_name.encode('ascii')[:31].ljust(32, b'\x00')
                    data[name_pos+32:name_pos+64] = alpha_bytes

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Name update error: {str(e)}")

        # Update window title to show unsaved changes
        current_title = self.windowTitle()
        if not current_title.endswith("*"):
            self.setWindowTitle(current_title + "*")

    def _rebuild_txd_with_size_management(self): #vers 1
        """Rebuild TXD data with support for large texture replacements"""
        try:
            import struct

            if not self.current_txd_data or not self.texture_list:
                return None

            # Calculate new TXD size requirements
            estimated_size = self._calculate_new_txd_size()
            original_size = len(self.current_txd_data)

            if estimated_size > original_size * 3:  # More than 3x size increase
                reply = QMessageBox.question(self, "Large Texture Replacement",
                                        f"New TXD will be ~{estimated_size/1024/1024:.1f}MB "
                                        f"(was {original_size/1024/1024:.1f}MB). "
                                        f"This may require IMG rebuilding. Continue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return None

            # Build new TXD from scratch rather than modifying existing
            return self._build_new_txd_structure()

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"TXD rebuild error: {str(e)}")
            return None

    def _requires_img_rebuild(self, new_txd_data): #vers 1
        """Check if IMG needs full rebuild due to size changes"""
        if not self.current_txd_data:
            return True

        size_ratio = len(new_txd_data) / len(self.current_txd_data)
        return size_ratio > 2.0  # Rebuild if more than 2x size increase

    def _update_img_with_large_txd(self, modified_txd_data): #vers 1
        """Handle IMG update with potentially large TXD replacements"""
        try:
            if self._requires_img_rebuild(modified_txd_data):
                return self._rebuild_img_with_new_txd(modified_txd_data)
            else:
                return self._update_img_in_place(modified_txd_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG update error: {str(e)}")
            return False

    def _rebuild_img_with_new_txd(self, new_txd_data): #vers 1
        """Rebuild entire IMG file to accommodate large TXD"""
        try:
            # This would require integration with your IMG rebuilding system
            if self.main_window and hasattr(self.main_window, 'rebuild_current_img'):
                # Update TXD data first
                for entry in self.current_img.entries:
                    if entry.name == self.current_txd_name:
                        entry.data = new_txd_data
                        entry.size = len(new_txd_data)
                        break

                # Trigger full IMG rebuild
                result = self.main_window.rebuild_current_img()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"IMG rebuilt due to large TXD size change")

                return result
            else:
                # Fallback: save to new file
                return self._save_as_new_img(new_txd_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"IMG rebuild error: {str(e)}")
            return False

    def _save_as_new_img(self, new_txd_data): #vers 1
        """Save as new IMG file when rebuild is needed"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save IMG with Large Textures",
                self.current_img.file_path.replace('.img', '_hd.img'),
                "IMG Files (*.img);;All Files (*)"
            )

            if file_path:
                # Update TXD data
                for entry in self.current_img.entries:
                    if entry.name == self.current_txd_name:
                        entry.data = new_txd_data
                        entry.size = len(new_txd_data)
                        break

                # Save as new file
                self.current_img.save_as(file_path)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Saved as new IMG: {file_path}")

                return True

            return False

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Save as new error: {str(e)}")
            return False

    def open_img_archive(self): #vers 1
        """Open IMG archive and load TXD file list"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open IMG Archive", "", "IMG Files (*.img);;All Files (*)")
            if file_path:
                self.load_from_img_archive(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open IMG: {str(e)}")


    def open_txd_file(self, file_path=None): #vers 2
        """Open standalone TXD file"""
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(self, "Open TXD File", "", "TXD Files (*.txd);;All Files (*)")

            if file_path:
                with open(file_path, 'rb') as f:
                    txd_data = f.read()
                self._load_txd_textures(txd_data, os.path.basename(file_path))
                self.setWindowTitle(f"TXD Workshop: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open TXD: {str(e)}")

    def import_texture(self): #vers 1
        """Import texture to replace selected"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to replace")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Import Texture", "",
                                                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)")
        if file_path:
            QMessageBox.information(self, "Coming Soon", "Import functionality will be added soon!")

    def show_properties(self): #vers 1
        """Show detailed texture properties"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        QMessageBox.information(self, "Coming Soon", "Properties dialog will be added soon!")

    def _create_texture_filters(self): #vers 1
        """Create texture filtering options"""
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)

        # Format filter
        format_filter_layout = QHBoxLayout()
        format_filter_layout.addWidget(QLabel("Format:"))

        self.format_filter = QComboBox()
        self.format_filter.addItems(["All", "DXT1", "DXT3", "DXT5", "ARGB8888", "RGB888"])
        self.format_filter.currentTextChanged.connect(self._apply_texture_filters)
        format_filter_layout.addWidget(self.format_filter)

        filter_layout.addLayout(format_filter_layout)

        # Size filter
        size_filter_layout = QHBoxLayout()
        size_filter_layout.addWidget(QLabel("Size:"))

        self.size_filter = QComboBox()
        self.size_filter.addItems(["All", "Small (≤256)", "Medium (512-1024)", "Large (≥2048)"])
        self.size_filter.currentTextChanged.connect(self._apply_texture_filters)
        size_filter_layout.addWidget(self.size_filter)

        filter_layout.addLayout(size_filter_layout)

        # Alpha filter
        self.alpha_filter = QComboBox()
        self.alpha_filter.addItems(["All", "With Alpha", "No Alpha"])
        self.alpha_filter.currentTextChanged.connect(self._apply_texture_filters)
        filter_layout.addWidget(self.alpha_filter)

        return filter_group

    def _apply_texture_filters(self): #vers 1
        """Apply texture filters to table"""
        if not hasattr(self, 'texture_table') or not self.texture_list:
            return

        format_filter = self.format_filter.currentText() if hasattr(self, 'format_filter') else "All"
        size_filter = self.size_filter.currentText() if hasattr(self, 'size_filter') else "All"
        alpha_filter = self.alpha_filter.currentText() if hasattr(self, 'alpha_filter') else "All"

        for row in range(self.texture_table.rowCount()):
            if row < len(self.texture_list):
                texture = self.texture_list[row]
                show_row = True

                # Format filter
                if format_filter != "All":
                    tex_format = texture.get('format', 'Unknown')
                    if format_filter not in tex_format:
                        show_row = False

                # Size filter
                if size_filter != "All" and show_row:
                    width = texture.get('width', 0)
                    height = texture.get('height', 0)
                    max_dim = max(width, height)

                    if size_filter == "Small (≤256)" and max_dim > 256:
                        show_row = False
                    elif size_filter == "Medium (512-1024)" and (max_dim < 512 or max_dim > 1024):
                        show_row = False
                    elif size_filter == "Large (≥2048)" and max_dim < 2048:
                        show_row = False

                # Alpha filter
                if alpha_filter != "All" and show_row:
                    has_alpha = texture.get('has_alpha', False)
                    if alpha_filter == "With Alpha" and not has_alpha:
                        show_row = False
                    elif alpha_filter == "No Alpha" and has_alpha:
                        show_row = False

                self.texture_table.setRowHidden(row, not show_row)

    def _create_texture_search(self): #vers 1
        """Create texture search functionality"""
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Search:"))

        from PyQt6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter texture name...")
        self.search_input.textChanged.connect(self._perform_texture_search)
        search_layout.addWidget(self.search_input)

        clear_search_btn = QPushButton("Clear")
        clear_search_btn.clicked.connect(self._clear_texture_search)
        search_layout.addWidget(clear_search_btn)

        return search_layout

    def _perform_texture_search(self, search_text): #vers 1
        """Perform texture search"""
        if not hasattr(self, 'texture_table') or not self.texture_list:
            return

        search_text = search_text.lower().strip()

        for row in range(self.texture_table.rowCount()):
            if row < len(self.texture_list):
                texture = self.texture_list[row]
                texture_name = texture.get('name', '').lower()

                # Show row if search text is in texture name or if search is empty
                show_row = not search_text or search_text in texture_name
                self.texture_table.setRowHidden(row, not show_row)

    def _clear_texture_search(self): #vers 1
        """Clear texture search"""
        if hasattr(self, 'search_input'):
            self.search_input.clear()

        # Show all rows
        if hasattr(self, 'texture_table'):
            for row in range(self.texture_table.rowCount()):
                self.texture_table.setRowHidden(row, False)

    def _duplicate_texture(self): #vers 1
        """Duplicate selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to duplicate")
            return

        try:
            # Create duplicate
            original = self.selected_texture
            duplicate = original.copy()

            # Generate unique name
            base_name = original.get('name', 'texture')
            counter = 1
            new_name = f"{base_name}_copy"

            # Check for existing names
            existing_names = [t.get('name', '') for t in self.texture_list]
            while new_name in existing_names:
                counter += 1
                new_name = f"{base_name}_copy{counter}"

            duplicate['name'] = new_name

            # Add to texture list
            self.texture_list.append(duplicate)

            # Update table
            self._add_texture_to_table(duplicate)

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Duplicated texture: {base_name} -> {new_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to duplicate texture: {str(e)}")

    def _remove_texture(self): #vers 1
        """Remove selected texture"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture to remove")
            return

        texture_name = self.selected_texture.get('name', 'texture')

        reply = QMessageBox.question(self, "Remove Texture",
                                   f"Remove texture '{texture_name}'?\nThis cannot be undone.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Find and remove from list
            current_row = self.texture_table.currentRow()
            if 0 <= current_row < len(self.texture_list):
                self.texture_list.pop(current_row)
                self.texture_table.removeRow(current_row)

                # Clear selection
                self.selected_texture = None
                self._update_editing_controls()

                # Mark as modified
                self._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Removed texture: {texture_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove texture: {str(e)}")

    def _create_new_texture(self): #vers 1
        """Create new blank texture"""
        from PyQt6.QtWidgets import QInputDialog

        # Get texture name
        name, ok = QInputDialog.getText(self, "New Texture", "Enter texture name:")
        if not ok or not name:
            return

        # Check for duplicate names
        existing_names = [t.get('name', '') for t in self.texture_list]
        if name in existing_names:
            QMessageBox.warning(self, "Duplicate Name", f"Texture name '{name}' already exists")
            return

        # Get dimensions
        width, ok = QInputDialog.getInt(self, "New Texture", "Width:", value=256, min=4, max=4096)
        if not ok:
            return

        height, ok = QInputDialog.getInt(self, "New Texture", "Height:", value=256, min=4, max=4096)
        if not ok:
            return

        try:
            # Create blank RGBA data (transparent)
            rgba_data = bytearray(width * height * 4)
            for i in range(0, len(rgba_data), 4):
                rgba_data[i:i+4] = [0, 0, 0, 0]  # Transparent black

            # Create texture
            new_texture = {
                'name': name,
                'width': width,
                'height': height,
                'format': 'ARGB8888',
                'has_alpha': True,
                'rgba_data': bytes(rgba_data),
                'mipmaps': 1
            }

            # Add to list
            self.texture_list.append(new_texture)
            self._add_texture_to_table(new_texture)

            # Mark as modified
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Created new texture: {name} ({width}x{height})")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create texture: {str(e)}")

    def _texture_statistics(self): #vers 1
        """Show texture statistics"""
        if not self.texture_list:
            QMessageBox.information(self, "Statistics", "No textures loaded")
            return

        # Calculate statistics
        total_textures = len(self.texture_list)
        total_size = 0
        format_counts = {}
        alpha_count = 0
        size_distribution = {"Small (≤256)": 0, "Medium (512-1024)": 0, "Large (≥2048)": 0}

        for texture in self.texture_list:
            # Size calculation
            if texture.get('rgba_data'):
                total_size += len(texture['rgba_data'])

            # Format count
            fmt = texture.get('format', 'Unknown')
            format_counts[fmt] = format_counts.get(fmt, 0) + 1

            # Alpha count
            if texture.get('has_alpha', False):
                alpha_count += 1

            # Size distribution
            max_dim = max(texture.get('width', 0), texture.get('height', 0))
            if max_dim <= 256:
                size_distribution["Small (≤256)"] += 1
            elif max_dim <= 1024:
                size_distribution["Medium (512-1024)"] += 1
            else:
                size_distribution["Large (≥2048)"] += 1

        # Build statistics text
        stats = f"=== TXD Statistics ===\n"
        stats += f"Total Textures: {total_textures}\n"
        stats += f"Total Data Size: {total_size:,} bytes ({total_size/1024:.1f} KB)\n"
        stats += f"Textures with Alpha: {alpha_count} ({alpha_count/total_textures*100:.1f}%)\n\n"

        stats += "=== Format Distribution ===\n"
        for fmt, count in sorted(format_counts.items()):
            percentage = count / total_textures * 100
            stats += f"{fmt}: {count} ({percentage:.1f}%)\n"

        stats += "\n=== Size Distribution ===\n"
        for size_cat, count in size_distribution.items():
            percentage = count / total_textures * 100
            stats += f"{size_cat}: {count} ({percentage:.1f}%)\n"

        QMessageBox.information(self, "TXD Statistics", stats)

    def _add_texture_to_table(self, texture): #vers 2
        """Add a texture to the table with compression status"""
        row = self.texture_table.rowCount()
        self.texture_table.insertRow(row)

        # Create thumbnail
        thumb_item = QTableWidgetItem()
        rgba_data = texture.get('rgba_data')
        width = texture.get('width', 0)
        height = texture.get('height', 0)

        if rgba_data and width > 0:
            pixmap = self._create_thumbnail(rgba_data, width, height)
            if pixmap:
                thumb_item.setData(Qt.ItemDataRole.DecorationRole, pixmap)
            else:
                thumb_item.setText("🖼️")
        else:
            thumb_item.setText("🖼️")

        # Create details with compression status
        details = f"Name: {texture['name']}\n"
        if texture.get('has_alpha', False):
            alpha_name = texture.get('alpha_name', texture['name'] + 'a')
            details += f"Alpha: {alpha_name}\n"
        if width > 0:
            details += f"Size: {width}x{height}\n"

        # Show format with compression status
        fmt = texture['format']
        if 'DXT' in fmt:
            details += f"Format: {fmt} (Compressed)\n"
        else:
            details += f"Format: {fmt} (Uncompressed)\n"

        details += f"Alpha: {'Yes' if texture.get('has_alpha', False) else 'No'}"

        details_item = QTableWidgetItem(details)

        # Make items non-editable
        thumb_item.setFlags(thumb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.texture_table.setItem(row, 0, thumb_item)
        self.texture_table.setItem(row, 1, details_item)
        self.texture_table.setRowHeight(row, 80)


class MipmapManagerWindow(QWidget): #vers 1
    """Mipmap Manager - View and edit all mipmap levels"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data
        self.main_window = main_window
        self.modified_levels = {}  # Track modified levels

        self.setWindowTitle(f"Mipmap Manager - {texture_data['name']}")
        self.resize(900, 700)
        self.setup_ui()

    def setup_ui(self): #vers 1
        """Setup Mipmap Manager UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header info
        header = QLabel(f"Texture: {self.texture_data['name']} | Format: {self.texture_data['format']}")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scrollable mipmap grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        grid_widget = QWidget()
        self.grid_layout = QVBoxLayout(grid_widget)
        self.grid_layout.setSpacing(10)

        # Create level cards
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        for level_data in mipmap_levels:
            card = self._create_level_card(level_data)
            self.grid_layout.addWidget(card)

        self.grid_layout.addStretch()
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)


    def _create_toolbar(self): #vers 1
        """Create toolbar with mipmap operations"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        # Auto-generate button
        autogen_btn = QPushButton("🔄 Auto-Generate")
        autogen_btn.setToolTip("Generate all mipmap levels from main texture")
        autogen_btn.clicked.connect(self._auto_generate_mipmaps)
        layout.addWidget(autogen_btn)

        # Export all button
        export_all_btn = QPushButton("📤 Export All")
        export_all_btn.setToolTip("Export all mipmap levels as PNG files")
        export_all_btn.clicked.connect(self._export_all_levels)
        layout.addWidget(export_all_btn)

        # Import all button
        import_all_btn = QPushButton("📥 Import All")
        import_all_btn.setToolTip("Import mipmap levels from PNG files")
        import_all_btn.clicked.connect(self._import_all_levels)
        layout.addWidget(import_all_btn)

        layout.addStretch()

        # Apply button
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.setToolTip("Apply all changes to texture")
        apply_btn.clicked.connect(self._apply_changes)
        apply_btn.setStyleSheet("font-weight: bold; padding: 8px 16px;")
        layout.addWidget(apply_btn)

        return toolbar

    def _create_level_card(self, level_data): #vers 1
        """Create card for single mipmap level"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setMinimumHeight(150)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)

        # Preview thumbnail
        preview_label = QLabel()
        preview_label.setFixedSize(128, 128)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("border: 1px solid #3a3a3a; background-color: #1e1e1e;")

        rgba_data = level_data.get('rgba_data')
        if rgba_data:
            width = level_data['width']
            height = level_data['height']
            image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
                preview_label.setPixmap(scaled)
        else:
            preview_label.setText("No Data")

        layout.addWidget(preview_label)

        # Info section
        info_layout = QVBoxLayout()

        level_label = QLabel(f"Level {level_data['level']}")
        level_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        info_layout.addWidget(level_label)

        size_label = QLabel(f"Size: {level_data['width']}x{level_data['height']}")
        info_layout.addWidget(size_label)

        compressed_size = level_data.get('compressed_size', 0)
        size_kb = compressed_size / 1024 if compressed_size > 0 else 0
        size_info = QLabel(f"Compressed: {size_kb:.2f} KB")
        info_layout.addWidget(size_info)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Buttons section
        button_layout = QVBoxLayout()

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(lambda: self._export_level(level_data))
        button_layout.addWidget(export_btn)

        import_btn = QPushButton("Import")
        import_btn.clicked.connect(lambda: self._import_level(level_data))
        button_layout.addWidget(import_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return card


    def _auto_generate_mipmaps(self): #vers 2
        """Auto-generate all mipmap levels from main texture"""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtGui import QImage

        # Ask user for source
        reply = QMessageBox.question(
            self, "Auto-Generate Mipmaps",
            "Generate mipmaps from:\n\nYes = Normal RGB\nNo = Alpha Channel\n\nChoose source:",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        use_alpha = (reply == QMessageBox.StandardButton.No)

        # Get main texture (level 0)
        main_level = None
        for level in self.texture_data.get('mipmap_levels', []):
            if level['level'] == 0:
                main_level = level
                break

        if not main_level or not main_level.get('rgba_data'):
            QMessageBox.warning(self, "Error", "Main texture data not available")
            return

        # Check if alpha channel exists
        if use_alpha and not self.texture_data.get('has_alpha', False):
            QMessageBox.warning(self, "No Alpha", "This texture has no alpha channel")
            return

        try:
            # Generate mipmaps
            source_width = main_level['width']
            source_height = main_level['height']
            source_data = main_level['rgba_data']

            # Convert to QImage for downscaling
            if use_alpha:
                # Extract alpha as grayscale
                alpha_data = bytearray()
                for i in range(3, len(source_data), 4):
                    a = source_data[i]
                    alpha_data.extend([a, a, a, 255])
                source_image = QImage(bytes(alpha_data), source_width, source_height,
                                    source_width * 4, QImage.Format.Format_RGBA8888)
            else:
                # Use normal RGB
                source_image = QImage(source_data, source_width, source_height,
                                    source_width * 4, QImage.Format.Format_RGBA8888)

            if source_image.isNull():
                QMessageBox.warning(self, "Error", "Failed to create source image")
                return

            # Generate each level
            current_width = source_width // 2
            current_height = source_height // 2
            level_num = 1
            generated_count = 0

            while current_width >= 1 and current_height >= 1:
                # Scale down image
                scaled_image = source_image.scaled(
                    current_width, current_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                if scaled_image.isNull():
                    break

                # Convert to RGBA bytes
                scaled_image = scaled_image.convertToFormat(QImage.Format.Format_RGBA8888)
                rgba_data = scaled_image.bits().asarray(current_width * current_height * 4)

                # Find or create level entry
                level_data = None
                for level in self.texture_data.get('mipmap_levels', []):
                    if level['level'] == level_num:
                        level_data = level
                        break

                if level_data:
                    # Update existing level
                    level_data['rgba_data'] = bytes(rgba_data)
                    level_data['width'] = current_width
                    level_data['height'] = current_height
                    self.modified_levels[level_num] = level_data
                else:
                    # Create new level
                    new_level = {
                        'level': level_num,
                        'width': current_width,
                        'height': current_height,
                        'rgba_data': bytes(rgba_data),
                        'compressed_data': None,
                        'compressed_size': 0
                    }
                    self.texture_data['mipmap_levels'].append(new_level)
                    self.modified_levels[level_num] = new_level

                generated_count += 1
                level_num += 1
                current_width //= 2
                current_height //= 2

            # Refresh UI
            self._refresh_level_cards()

            source_type = "Alpha" if use_alpha else "RGB"
            QMessageBox.information(
                self, "Success",
                f"Generated {generated_count} mipmap levels from {source_type}\n\nClick 'Apply Changes' to save"
            )

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Generated {generated_count} mipmaps from {source_type}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mipmaps: {str(e)}")
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Mipmap generation error: {str(e)}")


    def _refresh_level_cards(self): #vers 1
        """Refresh all level cards in UI"""
        # Clear existing cards
        while self.grid_layout.count() > 1:  # Keep stretch
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate cards
        mipmap_levels = sorted(self.texture_data.get('mipmap_levels', []), key=lambda x: x['level'])
        for level_data in mipmap_levels:
            card = self._create_level_card(level_data)
            self.grid_layout.insertWidget(self.grid_layout.count() - 1, card)


    def _export_level(self, level_data): #vers 2
        """Export single mipmap level as PNG"""
        try:
            rgba_data = level_data.get('rgba_data')
            if not rgba_data:
                QMessageBox.warning(self, "No Data", "This mipmap level has no data to export")
                return

            # Default filename
            texture_name = self.texture_data['name']
            level_num = level_data['level']
            width = level_data['width']
            height = level_data['height']
            default_name = f"{texture_name}_{width}x{height}_level{level_num}.png"

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Mipmap Level",
                default_name,
                "PNG Files (*.png);;All Files (*)"
            )

            if not file_path:
                return

            # Convert to QImage and save
            image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

            if image.isNull():
                QMessageBox.warning(self, "Error", "Failed to create image")
                return

            if image.save(file_path, "PNG"):
                QMessageBox.information(self, "Success", f"Exported level {level_num} to:\n{file_path}")
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Exported mipmap level {level_num}: {width}x{height}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save PNG file")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


    def _export_all_levels(self): #vers 2
        """Export all mipmap levels as separate PNG files"""
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if not folder:
            return

        try:
            texture_name = self.texture_data['name']
            mipmap_levels = self.texture_data.get('mipmap_levels', [])

            if not mipmap_levels:
                QMessageBox.warning(self, "No Mipmaps", "No mipmap levels to export")
                return

            exported_count = 0
            failed_count = 0

            for level_data in mipmap_levels:
                rgba_data = level_data.get('rgba_data')
                if not rgba_data:
                    failed_count += 1
                    continue

                level_num = level_data['level']
                width = level_data['width']
                height = level_data['height']

                # Create filename
                filename = f"{texture_name}_{width}x{height}_level{level_num}.png"
                file_path = os.path.join(folder, filename)

                # Convert and save
                image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)

                if not image.isNull() and image.save(file_path, "PNG"):
                    exported_count += 1
                else:
                    failed_count += 1

            # Show results
            message = f"Exported {exported_count} mipmap levels"
            if failed_count > 0:
                message += f"\n{failed_count} levels failed to export"

            QMessageBox.information(self, "Export Complete", message)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Exported {exported_count} mipmap levels to: {folder}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export all failed: {str(e)}")


    def _import_level(self, level_data): #vers 2
        """Import single mipmap level from PNG"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Mipmap Level",
                "",
                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
            )

            if not file_path:
                return

            # Load image
            image = QImage(file_path)
            if image.isNull():
                QMessageBox.warning(self, "Error", "Failed to load image file")
                return

            # Convert to RGBA8888
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)

            imported_width = image.width()
            imported_height = image.height()
            expected_width = level_data['width']
            expected_height = level_data['height']

            # Warn if size mismatch
            if imported_width != expected_width or imported_height != expected_height:
                reply = QMessageBox.question(
                    self, "Size Mismatch",
                    f"Imported image size: {imported_width}x{imported_height}\n"
                    f"Expected size: {expected_width}x{expected_height}\n\n"
                    f"Resize image to fit?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    image = image.scaled(
                        expected_width, expected_height,
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                else:
                    return

            # Convert to bytes
            rgba_data = image.bits().asarray(image.width() * image.height() * 4)

            # Update level data
            level_data['rgba_data'] = bytes(rgba_data)
            level_data['width'] = image.width()
            level_data['height'] = image.height()
            level_data['compressed_data'] = None  # Needs recompression

            # Track as modified
            self.modified_levels[level_data['level']] = level_data

            # Refresh UI
            self._refresh_level_cards()

            QMessageBox.information(
                self, "Success",
                f"Imported level {level_data['level']}\n\nClick 'Apply Changes' to save"
            )

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"✅ Imported mipmap level {level_data['level']}: {image.width()}x{image.height()}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {str(e)}")


    def _import_all_levels(self): #vers 2
        """Import mipmap levels from PNG files"""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Import Mipmap Levels",
                "",
                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
            )

            if not files:
                return

            # Try to match files to levels by size
            mipmap_levels = self.texture_data.get('mipmap_levels', [])
            imported_count = 0
            failed_count = 0

            for file_path in files:
                image = QImage(file_path)
                if image.isNull():
                    failed_count += 1
                    continue

                # Convert to RGBA8888
                image = image.convertToFormat(QImage.Format.Format_RGBA8888)
                width = image.width()
                height = image.height()

                # Find matching level by size
                matched_level = None
                for level in mipmap_levels:
                    if level['width'] == width and level['height'] == height:
                        matched_level = level
                        break

                if not matched_level:
                    # Try to find by filename pattern (e.g., texture_512x512_level0.png)
                    filename = os.path.basename(file_path)
                    for level in mipmap_levels:
                        if f"{level['width']}x{level['height']}" in filename:
                            matched_level = level
                            break

                if matched_level:
                    # Import to matched level
                    rgba_data = image.bits().asarray(width * height * 4)
                    matched_level['rgba_data'] = bytes(rgba_data)
                    matched_level['compressed_data'] = None
                    self.modified_levels[matched_level['level']] = matched_level
                    imported_count += 1
                else:
                    failed_count += 1

            # Refresh UI
            if imported_count > 0:
                self._refresh_level_cards()

            # Show results
            message = f"Imported {imported_count} mipmap levels"
            if failed_count > 0:
                message += f"\n{failed_count} files could not be matched to mipmap levels"
            message += "\n\nClick 'Apply Changes' to save"

            QMessageBox.information(self, "Import Complete", message)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Imported {imported_count} mipmap levels")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import all failed: {str(e)}")

    def _apply_changes(self): #vers 2
        """Apply all changes back to parent texture"""
        if not self.modified_levels:
            QMessageBox.information(self, "No Changes", "No changes to apply")
            return

        try:
            # Confirm apply
            reply = QMessageBox.question(
                self, "Apply Changes",
                f"Apply {len(self.modified_levels)} modified mipmap level(s)?\n\n"
                f"This will update the texture in memory.\n"
                f"You must save the TXD to make changes permanent.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Update texture data with modified levels
            for level_num, modified_level in self.modified_levels.items():
                # Find the level in texture data
                for i, level in enumerate(self.texture_data['mipmap_levels']):
                    if level['level'] == level_num:
                        # Update the level
                        self.texture_data['mipmap_levels'][i] = modified_level
                        break

            # Update main texture if level 0 was modified
            if 0 in self.modified_levels:
                self.texture_data['rgba_data'] = self.modified_levels[0]['rgba_data']

            # Recompress modified levels if format is DXT
            if 'DXT' in self.texture_data['format']:
                self._recompress_modified_levels()

            # Update parent workshop
            if self.parent_workshop:
                # Find texture in parent's texture_list and update it
                for i, tex in enumerate(self.parent_workshop.texture_list):
                    if tex['name'] == self.texture_data['name']:
                        self.parent_workshop.texture_list[i] = self.texture_data
                        break

                # Reload texture table to show changes
                self.parent_workshop._reload_texture_table()

                # Mark as modified
                self.parent_workshop._mark_as_modified()

            # Clear modified tracking
            self.modified_levels.clear()

            QMessageBox.information(
                self, "Success",
                f"Changes applied successfully!\n\n"
                f"Don't forget to save the TXD file."
            )

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Applied mipmap changes to: {self.texture_data['name']}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply changes: {str(e)}")
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Apply changes error: {str(e)}")


    def _recompress_modified_levels(self): #vers 1
        """Recompress modified mipmap levels to DXT format"""
        try:
            format_type = self.texture_data['format']

            for level_num, level_data in self.modified_levels.items():
                rgba_data = level_data.get('rgba_data')
                if not rgba_data:
                    continue

                width = level_data['width']
                height = level_data['height']

                # Compress based on format
                if 'DXT1' in format_type:
                    compressed_data = self._compress_to_dxt1(rgba_data, width, height)
                elif 'DXT3' in format_type:
                    compressed_data = self._compress_to_dxt3(rgba_data, width, height)
                elif 'DXT5' in format_type:
                    compressed_data = self._compress_to_dxt5(rgba_data, width, height)
                else:
                    compressed_data = rgba_data  # Uncompressed

                if compressed_data:
                    level_data['compressed_data'] = compressed_data
                    level_data['compressed_size'] = len(compressed_data)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Recompressed {len(self.modified_levels)} modified levels")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ Recompression warning: {str(e)}")


    # --- DXT1 and DXT5 encoders (pure Python) ---

    def _compress_to_dxt1(self, rgba_data, width, height): #vers 2
        """Compress RGBA data to DXT1 format"""
        try:
            # Use helper function
            return _encode_dxt1(rgba_data, width, height)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ DXT1 compression error: {str(e)}")
            return None


    def _compress_to_dxt3(self, rgba_data, width, height): #vers 2
        """Compress RGBA data to DXT3 format"""
        try:
            # DXT3 uses DXT1 color + explicit alpha
            import struct

            blocks_x = (width + 3) // 4
            blocks_y = (height + 3) // 4
            dxt3_data = bytearray()

            for by in range(blocks_y):
                for bx in range(blocks_x):
                    # Extract 4x4 block
                    block_alpha = bytearray()

                    for py in range(4):
                        for px in range(4):
                            x = bx * 4 + px
                            y = by * 4 + py

                            if x < width and y < height:
                                idx = (y * width + x) * 4
                                alpha = rgba_data[idx + 3]
                            else:
                                alpha = 255

                            block_alpha.append(alpha)

                    # Encode explicit alpha (4-bit per pixel)
                    alpha_block = 0
                    for i in range(16):
                        alpha_4bit = block_alpha[i] >> 4  # Convert 8-bit to 4-bit
                        alpha_block |= (alpha_4bit << (i * 4))

                    # Pack alpha block (8 bytes)
                    dxt3_data.extend(struct.pack('<Q', alpha_block))

                    # Add DXT1 color block (would need to encode, using placeholder)
                    dxt3_data.extend(b'\x00' * 8)  # Placeholder for color block

            return bytes(dxt3_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ DXT3 compression error: {str(e)}")
            return None


    def _compress_to_dxt5(self, rgba_data, width, height): #vers 2
        """Compress RGBA data to DXT5 format"""
        try:
            # Use helper function
            return _encode_dxt5(rgba_data, width, height)
        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"⚠️ DXT5 compression error: {str(e)}")
            return None


# Footer functions

def _rgb_to_565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def _565_to_rgb(c):
    r = ((c >> 11) & 0x1F) << 3
    g = ((c >> 5) & 0x3F) << 2
    b = (c & 0x1F) << 3
    return r, g, b


def _best_color_index(palette, r, g, b):
    best = 0
    best_dist = None
    for i, (pr, pg, pb) in enumerate(palette):
        dr = pr - r
        dg = pg - g
        db = pb - b
        dist = dr*dr + dg*dg + db*db
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = i
    return best


def _encode_dxt1(rgba_bytes, width, height):
    """Encode raw RGBA bytes (RGBA8888) into DXT1 bytes.
    Simple block-wise encoder: select endpoints by luminance heuristic and assign indices.
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    out = bytearray()

    for by in range(blocks_y):
        for bx in range(blocks_x):
            pixels = []
            for py in range(4):
                for px in range(4):
                    x = bx*4 + px
                    y = by*4 + py
                    if x < width and y < height:
                        idx = (y*width + x)*4
                        r = rgba_bytes[idx]
                        g = rgba_bytes[idx+1]
                        b = rgba_bytes[idx+2]
                    else:
                        r = g = b = 0
                    pixels.append((r,g,b))

            lum = [0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2] for p in pixels]
            max_i = lum.index(max(lum))
            min_i = lum.index(min(lum))
            c0_rgb = pixels[max_i]
            c1_rgb = pixels[min_i]

            c0_565 = _rgb_to_565(*c0_rgb)
            c1_565 = _rgb_to_565(*c1_rgb)

            pr0 = _565_to_rgb(c0_565)
            pr1 = _565_to_rgb(c1_565)
            palette = [pr0, pr1]
            if c0_565 > c1_565:
                palette.append(((2*pr0[0]+pr1[0])//3, (2*pr0[1]+pr1[1])//3, (2*pr0[2]+pr1[2])//3))
                palette.append(((pr0[0]+2*pr1[0])//3, (pr0[1]+2*pr1[1])//3, (pr0[2]+2*pr1[2])//3))
            else:
                palette.append(((pr0[0]+pr1[0])//2, (pr0[1]+pr1[1])//2, (pr0[2]+pr1[2])//2))
                palette.append((0,0,0))

            indices = 0
            bit_pos = 0
            for (r,g,b) in pixels:
                idx = _best_color_index(palette, r, g, b)
                indices |= (idx & 0x3) << bit_pos
                bit_pos += 2

            out.extend(struct.pack('<HHI', c0_565, c1_565, indices))

    return bytes(out)


def _encode_alpha_block(alpha_bytes):
    """Encode 4x4 alpha block for DXT5.
    alpha_bytes: list of 16 alpha values (0-255)
    Returns 8 bytes: a0, a1, and 48-bit index stream (little-endian packed 3 bits per pixel)
    """
    a0 = max(alpha_bytes)
    a1 = min(alpha_bytes)

    # Build alpha palette
    alpha_palette = [a0, a1]
    if a0 > a1:
        for i in range(1, 6):
            alpha_palette.append((( (6 - i) * a0 + i * a1 ) // 6))
    else:
        for i in range(1, 4):
            alpha_palette.append((( (4 - i) * a0 + i * a1 ) // 4))
        alpha_palette.extend([0, 255])

    # For each pixel, find best index (0..7)
    indices = 0
    bit_pos = 0
    for a in alpha_bytes:
        # find closest
        best_i = 0
        best_dist = None
        for i, av in enumerate(alpha_palette):
            dist = (av - a) * (av - a)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_i = i
        indices |= (best_i & 0x7) << bit_pos
        bit_pos += 3

    # pack into 6 bytes little endian
    idx_bytes = indices.to_bytes(6, 'little')
    return bytes([a0, a1]) + idx_bytes


def _encode_dxt5(rgba_bytes, width, height):
    """Encode raw RGBA8888 bytes into DXT5 bytes.
    DXT5 block = 8 bytes alpha block + 8 bytes color block (same as DXT1 color block)
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    out = bytearray()

    for by in range(blocks_y):
        for bx in range(blocks_x):
            alpha_vals = []
            pixels_rgb = []
            for py in range(4):
                for px in range(4):
                    x = bx*4 + px
                    y = by*4 + py
                    if x < width and y < height:
                        idx = (y*width + x)*4
                        r = rgba_bytes[idx]
                        g = rgba_bytes[idx+1]
                        b = rgba_bytes[idx+2]
                        a = rgba_bytes[idx+3]
                    else:
                        r = g = b = a = 0
                    pixels_rgb.append((r,g,b))
                    alpha_vals.append(a)

            # alpha block
            alpha_block = _encode_alpha_block(alpha_vals)

            # color block same as DXT1
            lum = [0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2] for p in pixels_rgb]
            max_i = lum.index(max(lum))
            min_i = lum.index(min(lum))
            c0_rgb = pixels_rgb[max_i]
            c1_rgb = pixels_rgb[min_i]
            c0_565 = _rgb_to_565(*c0_rgb)
            c1_565 = _rgb_to_565(*c1_rgb)
            pr0 = _565_to_rgb(c0_565)
            pr1 = _565_to_rgb(c1_565)
            palette = [pr0, pr1]
            if c0_565 > c1_565:
                palette.append(((2*pr0[0]+pr1[0])//3, (2*pr0[1]+pr1[1])//3, (2*pr0[2]+pr1[2])//3))
                palette.append(((pr0[0]+2*pr1[0])//3, (pr0[1]+2*pr1[1])//3, (pr0[2]+2*pr1[2])//3))
            else:
                palette.append(((pr0[0]+pr1[0])//2, (pr0[1]+pr1[1])//2, (pr0[2]+pr1[2])//2))
                palette.append((0,0,0))

            indices = 0
            bit_pos = 0
            for (r,g,b) in pixels_rgb:
                idx = _best_color_index(palette, r, g, b)
                indices |= (idx & 0x3) << bit_pos
                bit_pos += 2

            color_bytes = struct.pack('<HHI', c0_565, c1_565, indices)

            out.extend(alpha_block)
            out.extend(color_bytes)

    return bytes(out)

# --- External AI upscaler integration helper ---
import subprocess
import tempfile
import shutil
import sys


def _call_external_upscaler(self, qimg, factor, command): #vers 1
    """Call external AI upscaler tool"""
    if not command:
        return None

    tmp_dir = tempfile.mkdtemp(prefix='txd_upscale_')
    input_path = os.path.join(tmp_dir, 'input.png')
    output_path = os.path.join(tmp_dir, 'output.png')

    try:
        # Save input image
        qimg.save(input_path)

        # Try common command patterns
        command_patterns = [
            [command, '-i', input_path, '-o', output_path, '-s', str(factor)],
            [command, input_path, output_path, str(factor)],
            [command, input_path, output_path],
            [command, '--input', input_path, '--output', output_path, '--scale', str(factor)]
        ]

        for cmd_args in command_patterns:
            try:
                result = subprocess.run(cmd_args, check=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        timeout=300)  # 5 minute timeout

                if os.path.exists(output_path):
                    result_img = QImage(output_path)
                    if not result_img.isNull():
                        return result_img.convertToFormat(QImage.Format.Format_RGBA8888)

            except subprocess.TimeoutExpired:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("External upscaler timed out")
                break
            except Exception:
                continue

        return None

    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass


def open_txd_workshop(main_window, img_path=None): #vers 3
    """Open TXD Workshop from main window - works with or without IMG"""
    try:
        workshop = TXDWorkshop(main_window, main_window)

        if img_path:
            # Check if it's a TXD file or IMG file
            if img_path.lower().endswith('.txd'):
                # Load standalone TXD file
                workshop.open_txd_file(img_path)
            else:
                # Load from IMG archive
                workshop.load_from_img_archive(img_path)
        else:
            # Open in standalone mode (no IMG loaded)
            if main_window and hasattr(main_window, 'log_message'):
                main_window.log_message("TXD Workshop opened in standalone mode")

        workshop.show()
        return workshop
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open TXD Workshop: {str(e)}")
        return None

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    workshop = TXDWorkshop(None, None)
    workshop.show()
    sys.exit(app.exec())
