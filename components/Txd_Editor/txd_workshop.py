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
from PyQt6.QtWidgets import (QApplication,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QDialog, QFormLayout,
    QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit, QTextEdit,
    QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QColorDialog,
    QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QPen, QColor

try:
    # Try main app path first
    from methods.txd_versions import (
        detect_txd_version, get_platform_name, get_game_from_version,
        get_version_capabilities, get_platform_capabilities,
        is_mipmap_supported, is_bumpmap_supported,
        validate_txd_format, TXDPlatform, detect_platform_from_data
    )
except ImportError:
    # Fallback to standalone depends folder
    from depends.txd_versions import (
        detect_txd_version, get_platform_name, get_game_from_version,
        get_version_capabilities, get_platform_capabilities,
        is_mipmap_supported, is_bumpmap_supported,
        validate_txd_format, TXDPlatform, detect_platform_from_data
    )


##Methods list -
# _compress_to_dxt1
# _compress_to_dxt3
# _compress_to_dxt5
# _create_blank_texture
# _create_empty_txd_data
# _create_export_icon
# _create_file_icon
# _create_flip_horiz_icon
# _create_flip_vert_icon
# _create_folder_icon
# _create_import_icon
# _create_info_icon
# _create_left_panel
# _create_middle_panel
# _create_new_texture_entry
# _create_new_txd
# _create_package_icon
# _create_properties_icon
# _create_right_panel
# _create_save_icon
# _create_thumbnail
# _create_toolbar
# _create_undo_icon
# _decode_bumpmap
# _decompress_dxt1
# _decompress_dxt3
# _decompress_dxt5
# _decompress_uncompressed
# _delete_texture
# _detect_txd_info
# _encode_bumpmap
# _export_bumpmap
# _extract_alpha_channel
# _extract_txd_from_img
# _export_alpha_only
# _get_format_description
# _get_resize_direction
# _handle_resize
# _import_bumpmap
# _is_on_draggable_area
# _load_img_txd_list
# _load_txd_textures
# _mark_as_modified
# _on_texture_selected
# _on_txd_selected
# _parse_single_texture
# _rebuild_txd_data
# _reload_texture_table
# _save_as_new_txd
# _save_as_txd_file
# _save_texture_png
# _save_to_img
# _save_undo_state
# _show_detailed_info
# _show_texture_context_menu
# _toggle_maximize
# _undo_last_action
# _update_cursor
# _update_texture_info
# _view_bumpmap
# export_all_textures
# export_selected_texture
# flip_texture
# import_texture
# load_from_img_archive
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
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


    def __init__(self, parent=None, main_window=None): #vers 7
        super().__init__(parent)
        self.main_window = main_window
        self.current_img = None
        self.current_txd_data = None
        self.current_txd_name = None
        self.txd_list = []
        self.texture_list = []
        self.selected_texture = None
        self.undo_stack = []
        self.button_display_mode = 'both'

        # TXD version tracking variables
        self.txd_version_id = 0
        self.txd_device_id = 0
        self.txd_version_str = "Unknown"
        self.txd_platform_name = "Unknown"
        self.txd_game = "Unknown"
        self.txd_capabilities = {}

        # Detect standalone mode
        self.standalone_mode = (main_window is None)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # NEW: Docking state
        self.is_docked = False
        self.dock_widget = None

        self.setWindowTitle("TXD Workshop: No File")
        self.resize(1400, 800)
        self._initialize_features()

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None  # Changed from resize_direction
        self.corner_size = 20  # Size of corner resize areas
        self.hover_corner = None  # Track which corner is hovered

        if parent:
            parent_pos = parent.pos()
            self.move(parent_pos.x() + 50, parent_pos.y() + 80)

        self.setup_ui()
        self._apply_theme()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)


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


    def _show_workshop_settings(self): #vers 1
        """Show workshop settings dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Workshop Settings")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Appearance group
        appearance_group = QGroupBox("Button Appearance")
        appearance_layout = QVBoxLayout(appearance_group)

        # Button display mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Button Style:"))

        self.button_mode_combo = QComboBox()
        self.button_mode_combo.addItems([
            "Icons + Text",
            "Icons Only",
            "Text Only"
        ])

        # Set current mode
        mode_map = {'both': 0, 'icons': 1, 'text': 2}
        self.button_mode_combo.setCurrentIndex(mode_map.get(self.button_display_mode, 0))

        mode_layout.addWidget(self.button_mode_combo)
        appearance_layout.addLayout(mode_layout)

        layout.addWidget(appearance_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: self._apply_button_mode(dialog))
        button_layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec()

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

    def toggle_dock_mode(self): #vers 1
        """Toggle between docked and standalone mode"""
        if self.is_docked:
            self._undock_from_main()
        else:
            self._dock_to_main()

    def _dock_to_main(self): #vers 1
        """Dock TXD Workshop into IMG Factory as a tab"""
        if not self.main_window:
            print("No main window available for docking")
            return

        # Check if main window has tab system
        if not hasattr(self.main_window, 'content_tabs'):
            print("Main window does not support tabs")
            return

        # Create dock widget if it doesn't exist
        if not self.dock_widget:
            from PyQt6.QtWidgets import QWidget, QVBoxLayout
            self.dock_widget = QWidget()
            layout = QVBoxLayout(self.dock_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self)

        # Add as new tab
        tab_index = self.main_window.content_tabs.addTab(
            self.dock_widget,
            "TXD Workshop"
        )
        self.main_window.content_tabs.setCurrentIndex(tab_index)

        self.is_docked = True

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("TXD Workshop docked")

    def _undock_from_main(self): #vers 1
        """Undock TXD Workshop into standalone window"""
        if not self.main_window or not self.dock_widget:
            return

        # Remove from tabs
        if hasattr(self.main_window, 'content_tabs'):
            for i in range(self.main_window.content_tabs.count()):
                if self.main_window.content_tabs.widget(i) == self.dock_widget:
                    self.main_window.content_tabs.removeTab(i)
                    break

        # Remove from dock widget
        self.setParent(None)

        # Show as standalone window
        self.setWindowTitle("TXD Workshop - Standalone")
        self.resize(1200, 800)
        self.show()

        self.is_docked = False

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("TXD Workshop undocked")


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


    def _update_all_buttons(self): #vers 2
        """Update all buttons to match display mode"""
        buttons_to_update = [
            # Toolbar buttons
            ('open_img_btn', 'Open IMG'),
            ('open_txd_btn', 'Open TXD'),
            ('save_txd_btn', 'Save TXD'),
            ('import_btn', 'Import'),
            ('export_btn', 'Export'),
            ('export_all_btn', 'Export All'),
            ('flip_btn', 'Switch'),
            ('props_btn', 'Properties'),
            ('info_btn', 'Info'),
            # Transform buttons
            ('flip_vert_btn', 'Flip V'),
            ('flip_horz_btn', 'Flip H'),
            ('rotate_cw_btn', 'Rotate CW'),
            ('rotate_ccw_btn', 'Rotate CCW'),
            ('copy_btn', 'Copy'),
            ('paste_btn', 'Paste'),
            ('edit_btn', 'Edit'),
            ('convert_btn', 'Convert'),
            # Manage buttons
            ('create_texture_btn', 'Create'),
            ('delete_texture_btn', 'Delete'),
            ('duplicate_texture_btn', 'Clone'),
            # Effects buttons
            ('filters_btn', 'Filters'),
            ('paint_btn', 'Paint'),
            # Format/Size buttons
            ('bitdepth_btn', 'Bit Depth'),
            ('resize_btn', 'Resize'),
            ('upscale_btn', 'Upscale'),
            ('compress_btn', 'Compress'),
            ('uncompress_btn', 'Uncompress'),
            # Mipmap buttons
            ('show_mipmaps_btn', 'View'),
            ('create_mipmaps_btn', 'Create'),
            ('remove_mipmaps_btn', 'Remove'),
            # Bumpmap buttons
            ('view_bumpmap_btn', 'View'),
            ('export_bumpmap_btn', 'Export'),
            ('import_bumpmap_btn', 'Import'),
        ]

        # Adjust transform panel width based on mode
        if hasattr(self, 'transform_panel'):
            if self.button_display_mode == 'icons':
                self.transform_panel.setMaximumWidth(50)
            else:
                self.transform_panel.setMaximumWidth(200)

        for btn_name, btn_text in buttons_to_update:
            if hasattr(self, btn_name):
                button = getattr(self, btn_name)
                self._apply_button_mode_to_button(button, btn_text)


    def _apply_button_mode_to_button(self, button, text): #vers 3
        """Apply display mode to a single button with proper spacing"""
        # Store original icon if not already stored
        if not hasattr(button, '_original_icon'):
            button._original_icon = button.icon()

        if self.button_display_mode == 'icons':
            # Icons only - hide text, compact size
            button.setText("")
            if not button._original_icon.isNull():
                button.setIcon(button._original_icon)
                button.setIconSize(QSize(20, 20))
            button.setMinimumWidth(32)
            button.setMaximumWidth(32)

        elif self.button_display_mode == 'text':
            # Text only - show text, hide icon, auto-size
            button.setText(text)
            button.setIcon(QIcon())
            button.setMinimumWidth(60)  # Minimum for text readability
            button.setMaximumWidth(16777215)  # No max limit

        elif self.button_display_mode == 'both':
            # Icons + Text - show both, normal size
            button.setText(text)
            if not button._original_icon.isNull():
                button.setIcon(button._original_icon)
                button.setIconSize(QSize(16, 16))
            button.setMinimumWidth(80)
            button.setMaximumWidth(16777215)


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


    def _detect_txd_info(self, txd_data: bytes) -> bool: #vers 1
        """
        Detect and store TXD version and platform information
        Called when loading any TXD file
        """
        try:
            # Validate format first
            is_valid, message = validate_txd_format(txd_data)

            if not is_valid:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"TXD Validation: {message}")
                return False

            # Detect version info
            self.txd_version_id, self.txd_device_id, self.txd_version_str = detect_txd_version(txd_data)

            # Get platform and game info
            self.txd_platform_name = get_platform_name(self.txd_device_id)
            self.txd_game = get_game_from_version(self.txd_version_id, self.txd_device_id)

            # Get capabilities
            self.txd_capabilities = get_version_capabilities(self.txd_version_id)

            # Log detection
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"TXD: {self.txd_version_str} | "
                    f"Platform: {self.txd_platform_name} | "
                    f"Game: {self.txd_game}"
                )

            return True

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Version detection error: {str(e)}")
            return False


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
        size = self.corner_size

        # Define corner triangles
        corners = {
            'top-left': [(0, 0), (size, 0), (0, size)],
            'top-right': [(w, 0), (w-size, 0), (w, size)],
            'bottom-left': [(0, h), (size, h), (0, h-size)],
            'bottom-right': [(w, h), (w-size, h), (w, h-size)]
        }

        for corner_name, points in corners.items():
            # Choose color based on hover state
            if self.hover_corner == corner_name:
                painter.setBrush(QBrush(hover_color))
                painter.setPen(QPen(hover_color.darker(120), 1))
            else:
                painter.setBrush(QBrush(normal_color))
                painter.setPen(QPen(normal_color.darker(120), 1))

            # Draw triangle
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()

            painter.drawPath(path)

        painter.end()


    def _get_resize_corner(self, pos): #vers 2
        """Determine which corner is under mouse position"""
        size = self.corner_size
        w = self.width()
        h = self.height()

        # Top-left corner
        if pos.x() < size and pos.y() < size:
            return "top-left"

        # Top-right corner
        if pos.x() > w - size and pos.y() < size:
            return "top-right"

        # Bottom-left corner
        if pos.x() < size and pos.y() > h - size:
            return "bottom-left"

        # Bottom-right corner
        if pos.x() > w - size and pos.y() > h - size:
            return "bottom-right"

        return None


    def mousePressEvent(self, event): #vers 2
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on resize corner
            self.resize_corner = self._get_resize_corner(event.pos())

            if self.resize_corner:
                self.resizing = True
                self.drag_position = event.globalPosition().toPoint()
                self.initial_geometry = self.geometry()
            else:
                # Check if clicking on toolbar for dragging
                if self._is_on_draggable_area(event.pos()):
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

            event.accept()


    def mouseMoveEvent(self, event): #vers 2
        """Handle mouse move for dragging, resizing, and hover effects"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing and self.resize_corner:
                self._handle_corner_resize(event.globalPosition().toPoint())
            elif self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # Update hover state and cursor
            corner = self._get_resize_corner(event.pos())
            if corner != self.hover_corner:
                self.hover_corner = corner
                self.update()  # Trigger repaint for hover effect
            self._update_cursor(corner)


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
            # Move top-left corner
            new_x = geometry.x() + delta.x()
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.resize_corner == "top-right":
            # Move top-right corner
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(geometry.x(), new_y, new_width, new_height)

        elif self.resize_corner == "bottom-left":
            # Move bottom-left corner
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, geometry.y(), new_width, new_height)

        elif self.resize_corner == "bottom-right":
            # Move bottom-right corner
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.resize(new_width, new_height)


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

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(self._create_settings_icon())
        self.settings_btn.setText("Settings")
        self.settings_btn.setIconSize(QSize(20, 20))
        self.settings_btn.clicked.connect(self._show_workshop_settings)
        self.settings_btn.setToolTip("Workshop Settings")
        layout.addWidget(self.settings_btn)

        layout.addStretch()

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
        self.dock_btn = QPushButton("D")
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


    def _create_mipmaps_dialog(self): #vers 1
        """Open dialog to create mipmaps with depth selection"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout
        import math

        # Calculate possible mipmap levels
        width = self.selected_texture.get('width', 256)
        height = self.selected_texture.get('height', 256)
        max_dimension = max(width, height)

        # Calculate how many levels possible (down to 1x1)
        max_levels = int(math.log2(max_dimension)) + 1

        # Create selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Mipmaps")
        dialog.setModal(True)
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)

        # Header info
        header = QLabel(f"Texture: {self.selected_texture['name']}\n"
                    f"Size: {width}x{height}\n\n"
                    f"Select minimum mipmap size:")
        header.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Slider with level preview
        slider_layout = QVBoxLayout()

        mipmap_slider = QSlider(Qt.Orientation.Horizontal)
        mipmap_slider.setMinimum(0)  # Down to 1x1
        mipmap_slider.setMaximum(max_levels - 1)
        mipmap_slider.setValue(max(0, max_levels - 6))  # Default to ~32x32
        mipmap_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        mipmap_slider.setTickInterval(1)

        # Preview label showing dimensions at each level
        mipmap_preview = QLabel()
        mipmap_preview.setStyleSheet("font-size: 14px; padding: 10px; "
                                    "background: #2a2a2a; border-radius: 3px;")
        mipmap_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def update_preview(value):
            # Calculate dimensions at this level
            levels_from_top = max_levels - 1 - value
            min_w = max(1, width >> levels_from_top)
            min_h = max(1, height >> levels_from_top)
            num_levels = max_levels - value

            preview_text = f"Minimum Size: {min_w}x{min_h}\n"
            preview_text += f"Total Levels: {num_levels}\n\n"
            preview_text += f"Levels: {width}x{height}"

            # Show a few intermediate levels
            current_w, current_h = width, height
            shown = 1
            for i in range(1, num_levels):
                current_w = max(1, current_w // 2)
                current_h = max(1, current_h // 2)
                if shown < 4 or i == num_levels - 1:  # Show first 3 and last
                    preview_text += f" → {current_w}x{current_h}"
                    shown += 1
                elif shown == 4:
                    preview_text += " → ..."
                    shown += 1

            mipmap_preview.setText(preview_text)

        mipmap_slider.valueChanged.connect(update_preview)
        update_preview(mipmap_slider.value())

        slider_layout.addWidget(QLabel("More Levels ←  →  Fewer Levels"))
        slider_layout.addWidget(mipmap_slider)
        slider_layout.addWidget(mipmap_preview)

        layout.addLayout(slider_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        def do_generate():
            slider_value = mipmap_slider.value()
            num_levels = max_levels - slider_value
            dialog.accept()

            # Generate mipmaps
            if hasattr(self, '_auto_generate_mipmaps_to_level'):
                self._auto_generate_mipmaps_to_level(num_levels)
            else:
                self._auto_generate_mipmaps()

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(do_generate)
        button_layout.addWidget(generate_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _remove_mipmaps(self): #vers 1
        """Remove all mipmap levels except Level 0"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        mipmap_levels = self.selected_texture.get('mipmap_levels', [])
        if len(mipmap_levels) <= 1:
            QMessageBox.information(self, "No Mipmaps",
                                "This texture has no mipmap levels to remove")
            return

        reply = QMessageBox.question(
            self, "Remove Mipmaps",
            f"Remove all mipmap levels from '{self.selected_texture['name']}'?\n\n"
            f"This will keep only Level 0 (main texture).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Keep only level 0
            level_0 = next((l for l in mipmap_levels if l.get('level') == 0), None)

            if level_0:
                self.selected_texture['mipmap_levels'] = [level_0]
                self.selected_texture['mipmaps'] = 1
            else:
                # No level 0 found, create it from main texture data
                self.selected_texture['mipmap_levels'] = [{
                    'level': 0,
                    'width': self.selected_texture['width'],
                    'height': self.selected_texture['height'],
                    'rgba_data': self.selected_texture['rgba_data'],
                    'compressed_data': None,
                    'compressed_size': len(self.selected_texture.get('rgba_data', b''))
                }]
                self.selected_texture['mipmaps'] = 1

            # Update display
            self._save_undo_state("Remove mipmaps")
            self._update_texture_info(self.selected_texture)
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Removed mipmaps from: {self.selected_texture['name']}")


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


    def _create_right_panel(self): #vers 8
        """Create right panel with editing controls - compact 3-line layout"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)

        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(5, 5, 5, 5)

        top_layout = QHBoxLayout()

        # Transform panel (left)
        transform_panel = self._create_transform_panel()
        top_layout.addWidget(transform_panel, stretch=1)

        # Preview area (center)
        self.preview_widget = ZoomablePreview(self)
        top_layout.addWidget(self.preview_widget, stretch=2)

        # Preview controls (right side, vertical)
        preview_controls = self._create_preview_controls()
        top_layout.addWidget(preview_controls)

        main_layout.addLayout(top_layout)

        # Information group below - COMPACT VERSION
        info_group = QGroupBox("")
        info_layout = QVBoxLayout(info_group)

        # === LINE 1: Texture name and alpha name ===
        name_layout = QHBoxLayout()

        name_label = QLabel("Name:")
        name_label.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(name_label)

        self.info_name = QLineEdit()
        self.info_name.setPlaceholderText("Click to edit...")
        self.info_name.setReadOnly(True)
        self.info_name.setStyleSheet("padding: 5px; border: 1px solid #3a3a3a;")
        self.info_name.returnPressed.connect(self._save_texture_name)
        self.info_name.editingFinished.connect(self._save_texture_name)
        self.info_name.mousePressEvent = lambda e: self._enable_name_edit(e, False)
        name_layout.addWidget(self.info_name, stretch=1)

        self.alpha_label = QLabel("Alpha:")
        self.alpha_label.setStyleSheet("font-weight: bold; color: red; margin-left: 10px;")
        self.alpha_label.setVisible(False)
        name_layout.addWidget(self.alpha_label)

        self.info_alpha_name = QLineEdit()
        self.info_alpha_name.setPlaceholderText("Click to edit...")
        self.info_alpha_name.setReadOnly(True)
        self.info_alpha_name.setStyleSheet("color: red; padding: 5px; border: 1px solid #3a3a3a;")
        self.info_alpha_name.returnPressed.connect(self._save_alpha_name)
        self.info_alpha_name.editingFinished.connect(self._save_alpha_name)
        self.info_alpha_name.mousePressEvent = lambda e: self._enable_name_edit(e, True)
        self.info_alpha_name.setVisible(False)
        name_layout.addWidget(self.info_alpha_name, stretch=1)

        info_layout.addLayout(name_layout)

        # === LINE 2: Size + Format + Bit Depth + Buttons (MERGED) ===
        size_format_layout = QHBoxLayout()
        size_format_layout.setSpacing(5)

        # Size label
        self.info_size = QLabel("Size: -")
        self.info_size.setMinimumWidth(100)
        size_format_layout.addWidget(self.info_size)

        # Format label
        self.format_status_label = QLabel("Format: -")
        self.format_status_label.setMinimumWidth(90)
        size_format_layout.addWidget(self.format_status_label)

        size_format_layout.addStretch()

        # Format dropdown
        self.format_combo = QComboBox()
        self.format_combo.addItems(["DXT1", "DXT3", "DXT5", "ARGB8888", "ARGB1555", "ARGB4444", "RGB888", "RGB565"])
        self.format_combo.currentTextChanged.connect(self._change_format)
        self.format_combo.setEnabled(False)
        self.format_combo.setMaximumWidth(100)
        size_format_layout.addWidget(self.format_combo)

        # Bit depth indicator (read-only display)
        self.info_bitdepth = QLabel("[32bit]")
        self.info_bitdepth.setStyleSheet("font-weight: bold; padding: 3px 8px; border: 1px solid #3a3a3a;")
        self.info_bitdepth.setMinimumWidth(50)
        size_format_layout.addWidget(self.info_bitdepth)

        # Buttons with TEXT AND ICONS (FIXED)
        self.bitdepth_btn = QPushButton("Bit Depth")
        self.bitdepth_btn.setIcon(self._create_bitdepth_icon())
        self.bitdepth_btn.setIconSize(QSize(16, 16))
        self.bitdepth_btn.setToolTip("Change bit depth")
        self.bitdepth_btn.clicked.connect(self._change_bit_depth)
        self.bitdepth_btn.setEnabled(False)
        print(f"Created bitdepth icon: {not self.bitdepth_btn.icon().isNull()}")  # ADD THIS

        size_format_layout.addWidget(self.bitdepth_btn)

        self.resize_btn = QPushButton("Resize")
        self.resize_btn.setIcon(self._create_resize_icon())
        self.resize_btn.setIconSize(QSize(16, 16))
        self.resize_btn.setToolTip("Resize texture")
        self.resize_btn.clicked.connect(self._resize_texture)
        self.resize_btn.setEnabled(False)
        print(f"Created resize icon: {not self.resize_btn.icon().isNull()}")  # ADD THIS
        size_format_layout.addWidget(self.resize_btn)

        self.upscale_btn = QPushButton("AI Upscale")
        self.upscale_btn.setIcon(self._create_upscale_icon())
        self.upscale_btn.setIconSize(QSize(16, 16))
        self.upscale_btn.setToolTip("AI upscale texture")
        self.upscale_btn.clicked.connect(self._upscale_texture)
        self.upscale_btn.setEnabled(False)
        size_format_layout.addWidget(self.upscale_btn)

        self.compress_btn = QPushButton("Compress")
        self.compress_btn.setIcon(self._create_compress_icon())
        self.compress_btn.setIconSize(QSize(16, 16))
        self.compress_btn.setToolTip("Compress texture")
        self.compress_btn.clicked.connect(self._compress_texture)
        self.compress_btn.setEnabled(False)
        size_format_layout.addWidget(self.compress_btn)

        self.uncompress_btn = QPushButton("Uncompress")
        self.uncompress_btn.setIcon(self._create_uncompress_icon())
        self.uncompress_btn.setIconSize(QSize(16, 16))
        self.uncompress_btn.setToolTip("Uncompress texture")
        self.uncompress_btn.clicked.connect(self._uncompress_texture)
        self.uncompress_btn.setEnabled(False)
        size_format_layout.addWidget(self.uncompress_btn)

        info_layout.addLayout(size_format_layout)

        # === LINE 3: Mipmaps + Bumpmaps (MERGED) ===

        mipbump_layout = QHBoxLayout()
        mipbump_layout.setSpacing(5)  # Consistent spacing

        # Mipmaps section
        self.info_format = QLabel("Mipmaps: None")
        self.info_format.setMinimumWidth(100)
        self.info_format.setStyleSheet("font-weight: bold;")
        mipbump_layout.addWidget(self.info_format)

        # Mipmap buttons - ensure they have icons
        self.show_mipmaps_btn = QPushButton("View")
        self.show_mipmaps_btn.setIcon(self._create_view_icon())
        self.show_mipmaps_btn.setIconSize(QSize(16, 16))
        self.show_mipmaps_btn.setToolTip("View all mipmap levels")
        self.show_mipmaps_btn.clicked.connect(self._open_mipmap_manager)
        self.show_mipmaps_btn.setEnabled(False)
        mipbump_layout.addWidget(self.show_mipmaps_btn)

        self.create_mipmaps_btn = QPushButton("Create")
        self.create_mipmaps_btn.setIcon(self._create_add_icon())
        self.create_mipmaps_btn.setIconSize(QSize(16, 16))
        self.create_mipmaps_btn.setToolTip("Generate mipmaps")
        self.create_mipmaps_btn.clicked.connect(self._create_mipmaps_dialog)
        self.create_mipmaps_btn.setEnabled(False)
        mipbump_layout.addWidget(self.create_mipmaps_btn)

        self.remove_mipmaps_btn = QPushButton("Remove")
        self.remove_mipmaps_btn.setIcon(self._create_delete_icon())
        self.remove_mipmaps_btn.setIconSize(QSize(16, 16))
        self.remove_mipmaps_btn.setToolTip("Remove all mipmaps")
        self.remove_mipmaps_btn.clicked.connect(self._remove_mipmaps)
        self.remove_mipmaps_btn.setEnabled(False)
        mipbump_layout.addWidget(self.remove_mipmaps_btn)

        mipbump_layout.addSpacing(30)  # Spacer between sections

        # Bumpmaps section
        self.info_format_b = QLabel("Bumpmaps: No data")
        self.info_format_b.setMinimumWidth(120)
        self.info_format_b.setStyleSheet("font-weight: bold; color: #757575;")
        mipbump_layout.addWidget(self.info_format_b)

        # Bumpmap buttons - ensure they have icons
        self.view_bumpmap_btn = QPushButton("View")
        self.view_bumpmap_btn.setIcon(self._create_view_icon())
        self.view_bumpmap_btn.setIconSize(QSize(16, 16))
        self.view_bumpmap_btn.setToolTip("View bumpmap channel")
        self.view_bumpmap_btn.clicked.connect(self._view_bumpmap)
        self.view_bumpmap_btn.setEnabled(False)
        mipbump_layout.addWidget(self.view_bumpmap_btn)

        self.export_bumpmap_btn = QPushButton("Export")
        self.export_bumpmap_btn.setIcon(self._create_export_icon())
        self.export_bumpmap_btn.setIconSize(QSize(16, 16))
        self.export_bumpmap_btn.setToolTip("Export bumpmap as PNG")
        self.export_bumpmap_btn.clicked.connect(self._export_bumpmap)
        self.export_bumpmap_btn.setEnabled(False)
        mipbump_layout.addWidget(self.export_bumpmap_btn)

        self.import_bumpmap_btn = QPushButton("Import")
        self.import_bumpmap_btn.setIcon(self._create_import_icon())
        self.import_bumpmap_btn.setIconSize(QSize(16, 16))
        self.import_bumpmap_btn.setToolTip("Import bumpmap from image")
        self.import_bumpmap_btn.clicked.connect(self._import_bumpmap)
        self.import_bumpmap_btn.setEnabled(False)
        mipbump_layout.addWidget(self.import_bumpmap_btn)

        mipbump_layout.addStretch()

        info_layout.addLayout(mipbump_layout)

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


    def _has_bumpmap_data(self, texture_data: dict) -> bool: #vers 1
        """Check if texture has bumpmap data"""
        try:
            # Check explicit flag
            if texture_data.get('has_bumpmap', False):
                return True

            # Check for bumpmap data key
            if 'bumpmap_data' in texture_data and texture_data['bumpmap_data']:
                return True

            # Check raster format flags
            flags = texture_data.get('raster_format_flags', 0)
            if flags & 0x10:  # Environment map bit
                return True

            return False

        except Exception:
            return False


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


    def _auto_generate_mipmaps_to_level(self, num_levels): #vers 1
        """Generate mipmaps down to specified level count"""
        if not self.selected_texture:
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

            # Generate levels down to specified depth
            current_width = width // 2
            current_height = height // 2
            level_num = 1

            while level_num < num_levels and current_width >= 1 and current_height >= 1:
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

            actual_levels = len(self.selected_texture['mipmap_levels'])
            min_dim = min(current_width * 2, currentQFormLayout_height * 2)
            QMessageBox.information(self, "Success",
                f"Generated {actual_levels} mipmap levels\n"
                f"From {width}x{height} down to {min_dim}x{min_dim}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mipmaps: {str(e)}")


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


    def _enable_name_edit(self, event, is_alpha): #vers 1
        """Enable name editing on click"""
        if is_alpha:
            self.info_alpha_name.setReadOnly(False)
            self.info_alpha_name.selectAll()
            self.info_alpha_name.setFocus()
        else:
            self.info_name.setReadOnly(False)
            self.info_name.selectAll()
            self.info_name.setFocus()


    def _save_texture_name(self): #vers 1
        """Save edited texture name"""
        if not self.selected_texture:
            return

        new_name = self.info_name.text().strip()
        if new_name and new_name != self.selected_texture.get('name', ''):
            old_name = self.selected_texture.get('name', '')
            self.selected_texture['name'] = new_name
            self._save_undo_state(f"Rename texture: {old_name} → {new_name}")
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✏️ Renamed: {old_name} → {new_name}")

        self.info_name.setReadOnly(True)


    def _save_alpha_name(self): #vers 1
        """Save edited alpha name"""
        if not self.selected_texture or not self.selected_texture.get('has_alpha'):
            return

        new_alpha_name = self.info_alpha_name.text().strip()
        if new_alpha_name and new_alpha_name != self.selected_texture.get('alpha_name', ''):
            old_name = self.selected_texture.get('alpha_name', '')
            self.selected_texture['alpha_name'] = new_alpha_name
            self._save_undo_state(f"Rename alpha: {old_name} → {new_alpha_name}")
            self._reload_texture_table()
            self._mark_as_modified()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✏️ Alpha renamed: {old_name} → {new_alpha_name}")

        self.info_alpha_name.setReadOnly(True)


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


    def _create_preview_controls(self): #vers 2
        """Create preview control buttons - vertical layout on right"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_frame.setMaximumWidth(50)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(5)

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
        pan_up_btn.setIconSize(QSize(16, 16))
        pan_up_btn.setFixedSize(40, 40)
        pan_up_btn.setToolTip("Pan Up")
        pan_up_btn.clicked.connect(lambda: self._pan_preview(0, -20))
        controls_layout.addWidget(pan_up_btn)

        # Pan Down
        pan_down_btn = QPushButton()
        pan_down_btn.setIcon(self._create_arrow_down_icon())
        pan_down_btn.setIconSize(QSize(16, 16))
        pan_down_btn.setFixedSize(40, 40)
        pan_down_btn.setToolTip("Pan Down")
        pan_down_btn.clicked.connect(lambda: self._pan_preview(0, 20))
        controls_layout.addWidget(pan_down_btn)

        # Pan Left
        pan_left_btn = QPushButton()
        pan_left_btn.setIcon(self._create_arrow_left_icon())
        pan_left_btn.setIconSize(QSize(16, 16))
        pan_left_btn.setFixedSize(40, 40)
        pan_left_btn.setToolTip("Pan Left")
        pan_left_btn.clicked.connect(lambda: self._pan_preview(-20, 0))
        controls_layout.addWidget(pan_left_btn)

        # Pan Right
        pan_right_btn = QPushButton()
        pan_right_btn.setIcon(self._create_arrow_right_icon())
        pan_right_btn.setIconSize(QSize(16, 16))
        pan_right_btn.setFixedSize(40, 40)
        pan_right_btn.setToolTip("Pan Right")
        pan_right_btn.clicked.connect(lambda: self._pan_preview(20, 0))
        controls_layout.addWidget(pan_right_btn)

        controls_layout.addSpacing(10)

        # Background colors
        bg_black_btn = QPushButton()
        bg_black_btn.setFixedSize(40, 40)
        bg_black_btn.setStyleSheet("background-color: black; border: 1px solid #555;")
        bg_black_btn.setToolTip("Black Background")
        bg_black_btn.clicked.connect(lambda: self.preview_widget.set_background_color(QColor(0, 0, 0)))
        controls_layout.addWidget(bg_black_btn)

        bg_gray_btn = QPushButton()
        bg_gray_btn.setFixedSize(40, 40)
        bg_gray_btn.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
        bg_gray_btn.setToolTip("Gray Background")
        bg_gray_btn.clicked.connect(lambda: self.preview_widget.set_background_color(QColor(42, 42, 42)))
        controls_layout.addWidget(bg_gray_btn)

        bg_white_btn = QPushButton()
        bg_white_btn.setFixedSize(40, 40)
        bg_white_btn.setStyleSheet("background-color: white; border: 1px solid #555;")
        bg_white_btn.setToolTip("White Background")
        bg_white_btn.clicked.connect(lambda: self.preview_widget.set_background_color(QColor(255, 255, 255)))
        controls_layout.addWidget(bg_white_btn)

        bg_custom_btn = QPushButton()
        bg_custom_btn.setIcon(self._create_color_picker_icon())
        bg_custom_btn.setIconSize(QSize(20, 20))
        bg_custom_btn.setFixedSize(40, 40)
        bg_custom_btn.setToolTip("Pick Color")
        bg_custom_btn.clicked.connect(self._pick_background_color)
        controls_layout.addWidget(bg_custom_btn)

        controls_layout.addStretch()

        return controls_frame


    def _pan_preview(self, dx, dy): #vers 2
        """Pan preview by delta"""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.pan_offset = QPoint(
                self.preview_widget.pan_offset.x() + dx,
                self.preview_widget.pan_offset.y() + dy
            )
            self.preview_widget.update_display()


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


    def _apply_theme(self): #vers 1
        """Apply theme from main window"""
        try:
            if self.main_window and hasattr(self.main_window, 'app_settings'):
                from depends.txd_workshop_theme import apply_theme_to_workshop, connect_workshop_to_theme_system
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


    def _on_texture_selected(self): #vers 6
        """Handle texture selection - UNIFIED VERSION"""
        try:
            row = self.texture_table.currentRow()

            # Invalid selection - disable everything
            if row < 0 or row >= len(self.texture_list):
                self.selected_texture = None
                self.export_btn.setEnabled(False)

                # Disable all optional buttons
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
                if hasattr(self, 'bitdepth_btn'):
                    self.bitdepth_btn.setEnabled(False)

                # Disable mipmap buttons
                if hasattr(self, 'create_mipmaps_btn'):
                    self.create_mipmaps_btn.setEnabled(False)
                if hasattr(self, 'remove_mipmaps_btn'):
                    self.remove_mipmaps_btn.setEnabled(False)
                if hasattr(self, 'show_mipmaps_btn'):
                    self.show_mipmaps_btn.setEnabled(False)

                # Disable bumpmap buttons
                if hasattr(self, 'view_bumpmap_btn'):
                    self.view_bumpmap_btn.setEnabled(False)
                if hasattr(self, 'export_bumpmap_btn'):
                    self.export_bumpmap_btn.setEnabled(False)
                if hasattr(self, 'import_bumpmap_btn'):
                    self.import_bumpmap_btn.setEnabled(False)

                # Disable transform buttons
                if hasattr(self, 'flip_vert_btn'):
                    self.flip_vert_btn.setEnabled(False)
                if hasattr(self, 'flip_horz_btn'):
                    self.flip_horz_btn.setEnabled(False)
                if hasattr(self, 'rotate_cw_btn'):
                    self.rotate_cw_btn.setEnabled(False)
                if hasattr(self, 'rotate_ccw_btn'):
                    self.rotate_ccw_btn.setEnabled(False)

                return

            # Valid selection - get texture data
            self.selected_texture = self.texture_list[row]

            # Check mipmap state
            mipmap_levels = self.selected_texture.get('mipmap_levels', [])
            num_levels = len(mipmap_levels)
            has_mipmaps = num_levels > 1

            # Check bumpmap state
            has_bumpmap = self._has_bumpmap_data(self.selected_texture) if hasattr(self, '_has_bumpmap_data') else False
            can_support_bumpmap = is_bumpmap_supported(self.txd_version_id, self.txd_device_id) if self.txd_version_id else False

            # Update display FIRST (this should show the texture preview)
            self._update_texture_info(self.selected_texture)

            # Debug log
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"Selected: {self.selected_texture.get('name')} | "
                    f"Levels: {num_levels} | Mipmaps: {has_mipmaps} | Bumpmap: {has_bumpmap}"
                )

            # Enable basic buttons
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
            if hasattr(self, 'bitdepth_btn'):
                self.bitdepth_btn.setEnabled(True)

            # Flip button - enable only if has alpha
            if hasattr(self, 'flip_btn'):
                has_alpha = self.selected_texture.get('has_alpha', False)
                self.flip_btn.setEnabled(has_alpha)

            # Mipmap buttons
            if hasattr(self, 'create_mipmaps_btn'):
                self.create_mipmaps_btn.setEnabled(not has_mipmaps)
            if hasattr(self, 'remove_mipmaps_btn'):
                self.remove_mipmaps_btn.setEnabled(has_mipmaps)
            if hasattr(self, 'show_mipmaps_btn'):
                self.show_mipmaps_btn.setEnabled(has_mipmaps)

            # Bumpmap buttons
            if hasattr(self, 'view_bumpmap_btn'):
                self.view_bumpmap_btn.setEnabled(has_bumpmap)
            if hasattr(self, 'export_bumpmap_btn'):
                self.export_bumpmap_btn.setEnabled(has_bumpmap)
            if hasattr(self, 'import_bumpmap_btn'):
                self.import_bumpmap_btn.setEnabled(can_support_bumpmap)

            # Transform buttons
            if hasattr(self, 'flip_vert_btn'):
                self.flip_vert_btn.setEnabled(True)
            if hasattr(self, 'flip_horz_btn'):
                self.flip_horz_btn.setEnabled(True)
            if hasattr(self, 'rotate_cw_btn'):
                self.rotate_cw_btn.setEnabled(True)
            if hasattr(self, 'rotate_ccw_btn'):
                self.rotate_ccw_btn.setEnabled(True)

            # Additional buttons
            if hasattr(self, 'copy_btn'):
                self.copy_btn.setEnabled(True)
            if hasattr(self, 'paste_btn'):
                self.paste_btn.setEnabled(True)
            if hasattr(self, 'edit_btn'):
                self.edit_btn.setEnabled(True)
            if hasattr(self, 'convert_btn'):
                self.convert_btn.setEnabled(True)
            if hasattr(self, 'paint_btn'):
                self.paint_btn.setEnabled(True)
            if hasattr(self, 'filters_btn'):
                self.filters_btn.setEnabled(True)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Selection error: {str(e)}")
                import traceback
                self.main_window.log_message(traceback.format_exc())


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


    def _load_txd_textures(self, txd_data, txd_name): #vers 12
        """Load textures from TXD data - display with mipmap info"""
        try:
            import struct

            self.texture_table.setRowCount(0)
            self.texture_list = []
            textures = []
            offset = 12
            if self.txd_version_id == 0:
                self._detect_txd_info(txd_data)

            self.current_txd_data = txd_data
            self.current_txd_name = txd_name

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


    def _upscale_texture_advanced(self): #vers 1
        """Advanced AI upscale with options dialog"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QCheckBox, QPushButton

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("AI Upscale Options")
        dialog.setModal(True)
        dialog.resize(450, 400)

        layout = QVBoxLayout(dialog)

        # Current texture info
        width = self.selected_texture.get('width', 0)
        height = self.selected_texture.get('height', 0)

        header = QLabel(f"Current Size: {width}x{height}")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(header)

        # Scale factor
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale Factor:"))
        scale_combo = QComboBox()
        scale_combo.addItems(["2x", "3x", "4x", "6x", "8x"])
        scale_combo.setCurrentIndex(0)
        scale_layout.addWidget(scale_combo)
        layout.addLayout(scale_layout)

        # Preview size label
        preview_label = QLabel(f"Result: {width*2}x{height*2}")
        preview_label.setStyleSheet("color: #4a9eff; font-weight: bold; padding: 5px;")

        def update_preview(index):
            factor = [2, 3, 4, 6, 8][index]
            new_w = width * factor
            new_h = height * factor
            size_mb = (new_w * new_h * 4) / (1024 * 1024)
            preview_label.setText(f"Result: {new_w}x{new_h} (~{size_mb:.1f} MB)")

        scale_combo.currentIndexChanged.connect(update_preview)
        layout.addWidget(preview_label)

        layout.addSpacing(10)

        # Method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        method_combo = QComboBox()
        method_combo.addItems(["Smooth (Bilinear)", "Sharp (Bicubic)", "Lanczos", "Nearest Neighbor"])
        method_combo.setCurrentIndex(1)
        method_layout.addWidget(method_combo)
        layout.addLayout(method_layout)

        # Sharpness slider
        sharp_layout = QVBoxLayout()
        sharp_layout.addWidget(QLabel("Sharpness:"))
        sharp_slider = QSlider(Qt.Orientation.Horizontal)
        sharp_slider.setMinimum(0)
        sharp_slider.setMaximum(100)
        sharp_slider.setValue(50)
        sharp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        sharp_slider.setTickInterval(25)
        sharp_layout.addWidget(sharp_slider)

        sharp_value_label = QLabel("50%")
        sharp_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sharp_slider.valueChanged.connect(lambda v: sharp_value_label.setText(f"{v}%"))
        sharp_layout.addWidget(sharp_value_label)
        layout.addLayout(sharp_layout)

        layout.addSpacing(10)

        # Options
        denoise_check = QCheckBox("Denoise (reduce noise)")
        denoise_check.setChecked(False)
        layout.addWidget(denoise_check)

        enhance_check = QCheckBox("Enhance edges")
        enhance_check.setChecked(True)
        layout.addWidget(enhance_check)

        preserve_alpha_check = QCheckBox("Preserve alpha channel")
        preserve_alpha_check.setChecked(True)
        layout.addWidget(preserve_alpha_check)

        layout.addSpacing(10)

        # Warning for large sizes
        warning_label = QLabel("⚠️ Large upscales may take time and increase file size significantly")
        warning_label.setStyleSheet("color: #ff9800; font-size: 11px; padding: 5px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        def do_upscale():
            factor = [2, 3, 4, 6, 8][scale_combo.currentIndex()]
            method = method_combo.currentIndex()
            sharpness = sharp_slider.value()
            denoise = denoise_check.isChecked()
            enhance = enhance_check.isChecked()
            preserve_alpha = preserve_alpha_check.isChecked()

            dialog.accept()

            # Apply upscale (placeholder for now)
            QMessageBox.information(self, "Upscaling",
                f"Upscaling {factor}x with method {method_combo.currentText()}\n"
                f"Sharpness: {sharpness}%\n"
                f"Denoise: {denoise}\n"
                f"Enhance: {enhance}\n\n"
                f"Advanced upscaling will be implemented soon!")

        upscale_btn = QPushButton("Upscale")
        upscale_btn.clicked.connect(do_upscale)
        button_layout.addWidget(upscale_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


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


    def _rebuild_txd_data(self): #vers 2
        """Rebuild TXD data with modified texture names and properties"""
        try:
            if not self.current_txd_data:
                return None

            # NEW: Preserve original version header
            if len(self.current_txd_data) < 28:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("Cannot rebuild: insufficient header data")
                return None

            # Read original header to preserve version
            original_header = self.current_txd_data[:28]

            # Extract version info if not already detected
            if self.txd_version_id == 0:
                self._detect_txd_info(self.current_txd_data)

            # Log rebuild info
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"Rebuilding TXD with version: {self.txd_version_str}"
                )

            # Import struct for header manipulation
            import struct

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Rebuilding TXD...")

            # If we have original data, update it in place
            if self.current_txd_data and len(self.current_txd_data) > 100:
                original_data = bytearray(self.current_txd_data)

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Rebuilt: {len(original_data)} bytes")

                return bytes(original_data)

            # No original data? Use serializer as fallback docked
            if self.texture_list:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Using serializer...")

                from methods.txd_serializer import serialize_txd_file
                return serialize_txd_file(self.texture_list)

            return None

            # No original data? Use serializer as fallback standalone
            if self.texture_list:
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Using serializer...")

                from depends.txd_serializer import serialize_txd_file
                return serialize_txd_file(self.texture_list)

            return None

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


    def _get_format_description(self) -> str: #vers 1
        """Get human-readable format description for UI display"""
        desc_parts = []

        if self.txd_capabilities:
            # Bit depths
            if self.txd_capabilities.get('bit_depths'):
                depths = ', '.join(str(d) for d in self.txd_capabilities['bit_depths'])
                desc_parts.append(f"{depths}-bit")

            # Features
            features = []
            if self.txd_capabilities.get('mipmaps'):
                features.append("Mipmaps")
            if self.txd_capabilities.get('bumpmaps'):
                features.append("Bumpmaps")
            if self.txd_capabilities.get('dxt_compression'):
                features.append("DXT")
            if self.txd_capabilities.get('palette'):
                features.append("Palette")
            if self.txd_capabilities.get('swizzled'):
                features.append("Swizzled")

            if features:
                desc_parts.append(', '.join(features))

        return ' | '.join(desc_parts) if desc_parts else "Standard format"


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


    def save_txd_file(self): #vers 6
        """Save TXD with preserved version information"""
        if not self.current_txd_data:
            QMessageBox.warning(self, "No Data", "No TXD file loaded")
            return

        try:
            # Check if loaded from IMG
            if self.current_img and self.current_txd_name:
                reply = QMessageBox.question(
                    self, "Save Location",
                    "Save back to IMG archive or as new TXD file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Yes
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self._save_to_img()
                elif reply == QMessageBox.StandardButton.No:
                    self._save_as_txd_file()
            else:
                # Save as standalone TXD file
                self._save_as_txd_file()

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save: {str(e)}")
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Save error: {str(e)}")


    def _save_to_img(self): #vers 1
        """Save TXD back to IMG archive"""
        if not self.current_txd_name:
            QMessageBox.warning(self, "No TXD", "No TXD file loaded from IMG")
            return

        try:
            # Rebuild TXD data
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Update entry in IMG
            if hasattr(self.current_img, 'replace_entry'):
                self.current_img.replace_entry(self.current_txd_name, modified_txd_data)

                # Mark IMG as modified in main window
                if self.main_window and hasattr(self.main_window, '_mark_as_modified'):
                    self.main_window._mark_as_modified()

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"✅ Saved TXD to IMG: {self.current_txd_name}")

                QMessageBox.information(self, "Success",
                    f"TXD saved to IMG archive\n\n"
                    f"Remember to save the IMG file to write changes to disk!")

                # Clear modified state
                self.save_txd_btn.setEnabled(False)
                self.save_txd_btn.setStyleSheet("")
                title = self.windowTitle().replace("*", "")
                self.setWindowTitle(title)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save to IMG: {str(e)}")

    def _save_as_txd_file(self): #vers 1
        """Save as standalone TXD file"""
        # Get save path
        if self.current_txd_name:
            default_name = self.current_txd_name
        else:
            default_name = "untitled.txd"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save TXD File", default_name,
            "TXD Files (*.txd);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Rebuild TXD data
            modified_txd_data = self._rebuild_txd_data()

            if not modified_txd_data:
                QMessageBox.critical(self, "Error", "Failed to rebuild TXD data")
                return

            # Write to file
            with open(file_path, 'wb') as f:
                f.write(modified_txd_data)

            self.current_txd_name = os.path.basename(file_path)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Saved TXD file: {file_path}")

            QMessageBox.information(self, "Success", f"TXD saved successfully!\n\n{file_path}")

            # Clear modified state
            self.save_txd_btn.setEnabled(False)
            self.save_txd_btn.setStyleSheet("")
            self.setWindowTitle(f"TXD Workshop: {self.current_txd_name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TXD: {str(e)}")


    def _create_new_txd_data(self): #vers 2
        """Create new TXD structure from scratch"""
        import struct

        try:
            # Basic RenderWare TXD header
            # Type, Size, Version
            header = struct.pack('<III', 0x16, 0, 0x1803FFFF)

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"   Created basic TXD header: {len(header)} bytes")

            return header

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"   ❌ Create TXD error: {str(e)}")
            return None


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


    def _convert_texture(self): #vers 3
        """Convert texture format with GTA III 8-bit support"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection", "Please select a texture first")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Convert Texture Format")
        dialog.setModal(True)
        dialog.resize(400, 350)

        layout = QVBoxLayout(dialog)

        # Current format
        current_format = self.selected_texture.get('format', 'Unknown')
        current_depth = self.selected_texture.get('depth', 32)
        current_label = QLabel(f"Current: {current_format} ({current_depth}bit)")
        current_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 10px;")
        layout.addWidget(current_label)

        # Format selection
        format_group = QGroupBox("Convert To")
        format_layout = QVBoxLayout(format_group)

        format_combo = QComboBox()
        format_combo.addItems([
            "DXT1 (No Alpha, 6:1 compression) - 32bit",
            "DXT3 (Sharp Alpha, 4:1 compression) - 32bit",
            "DXT5 (Smooth Alpha, 4:1 compression) - 32bit",
            "ARGB8888 (32-bit Uncompressed)",
            "RGB888 (24-bit No Alpha)",
            "ARGB1555 (16-bit with Alpha)",
            "RGB565 (16-bit No Alpha)",
            "PAL8 (8-bit Indexed - GTA III)"
        ])
        format_layout.addWidget(format_combo)

        # Info label
        info_label = QLabel()
        info_label.setStyleSheet("color: #ff9800; font-size: 10px; padding: 5px;")
        info_label.setWordWrap(True)

        def update_info(index):
            if index == 7:  # PAL8
                info_label.setText("⚠️ 8-bit indexed format (GTA III). Limited to 256 colors with palette.")
            else:
                info_label.setText("Note: Converting between compressed formats may result in quality loss.")

        format_combo.currentIndexChanged.connect(update_info)
        update_info(0)

        format_layout.addWidget(info_label)
        layout.addWidget(format_group)

        # Size estimate
        width = self.selected_texture.get('width', 0)
        height = self.selected_texture.get('height', 0)

        size_group = QGroupBox("Size Estimate")
        size_layout = QVBoxLayout(size_group)

        size_label = QLabel(f"Texture: {width}x{height}")
        size_layout.addWidget(size_label)

        def update_size_estimate(index):
            format_map = [
                ('DXT1', 32), ('DXT3', 32), ('DXT5', 32),
                ('ARGB8888', 32), ('RGB888', 24),
                ('ARGB1555', 16), ('RGB565', 16),
                ('PAL8', 8)
            ]
            selected_format, bit_depth = format_map[index]

            # Calculate estimated size
            pixel_count = width * height
            if 'DXT1' in selected_format:
                estimated = pixel_count // 2
            elif 'DXT' in selected_format:
                estimated = pixel_count
            elif 'PAL8' in selected_format:
                estimated = pixel_count + 1024  # 256 color palette (256 * 4 bytes)
            elif 'ARGB8888' in selected_format:
                estimated = pixel_count * 4
            elif 'RGB888' in selected_format:
                estimated = pixel_count * 3
            else:  # 16-bit formats
                estimated = pixel_count * 2

            size_kb = estimated / 1024
            estimate_label.setText(f"Estimated: {size_kb:.1f} KB ({bit_depth}bit)")

        estimate_label = QLabel("Select format above")
        size_layout.addWidget(estimate_label)

        format_combo.currentIndexChanged.connect(update_size_estimate)
        update_size_estimate(0)

        layout.addWidget(size_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        def do_convert():
            format_map = [
                ('DXT1', 32), ('DXT3', 32), ('DXT5', 32),
                ('ARGB8888', 32), ('RGB888', 24),
                ('ARGB1555', 16), ('RGB565', 16),
                ('PAL8', 8)
            ]
            selected_format, bit_depth = format_map[format_combo.currentIndex()]

            # Save undo state
            self._save_undo_state(f"Convert: {current_format} → {selected_format}")

            # Update texture format and bit depth
            self.selected_texture['format'] = selected_format
            self.selected_texture['depth'] = bit_depth

            # Mark as modified
            self._mark_as_modified()
            self._update_texture_info(self.selected_texture)
            self._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"✅ Converted: {current_format} → {selected_format} ({bit_depth}bit)")

            dialog.accept()

            if selected_format == 'PAL8':
                QMessageBox.information(self, "Format Converted",
                    f"Texture converted to 8-bit indexed format\n\n"
                    "Note: Color palette will be generated when saving.\n"
                    "Best for GTA III textures with limited colors.")
            else:
                QMessageBox.information(self, "Format Converted",
                    f"Texture format: {selected_format} ({bit_depth}bit)\n\n"
                    "Compression will be applied when saving TXD file.")

        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(do_convert)
        button_layout.addWidget(convert_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _create_transform_panel(self): #vers 8
        """Create transform panel with variable width - no headers"""
        self.transform_panel = QFrame()
        self.transform_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        self.transform_panel.setMinimumWidth(50)
        self.transform_panel.setMaximumWidth(200)

        layout = QVBoxLayout(self.transform_panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Flip Vertical
        self.flip_vert_btn = QPushButton()
        self.flip_vert_btn.setIcon(self._create_flip_vert_icon())
        self.flip_vert_btn.setText("Flip Vertical")
        self.flip_vert_btn.setIconSize(QSize(20, 20))
        self.flip_vert_btn.clicked.connect(self._flip_vertical)
        self.flip_vert_btn.setEnabled(False)
        self.flip_vert_btn.setToolTip("Flip texture vertically")
        layout.addWidget(self.flip_vert_btn)

        # Flip Horizontal
        self.flip_horz_btn = QPushButton()
        self.flip_horz_btn.setIcon(self._create_flip_horz_icon())
        self.flip_horz_btn.setText("Flip Horizontal")
        self.flip_horz_btn.setIconSize(QSize(20, 20))
        self.flip_horz_btn.clicked.connect(self._flip_horizontal)
        self.flip_horz_btn.setEnabled(False)
        self.flip_horz_btn.setToolTip("Flip texture horizontally")
        layout.addWidget(self.flip_horz_btn)

        layout.addSpacing(5)

        # Rotate Clockwise
        self.rotate_cw_btn = QPushButton()
        self.rotate_cw_btn.setIcon(self._create_rotate_cw_icon())
        self.rotate_cw_btn.setText("Rotate 90° CW")
        self.rotate_cw_btn.setIconSize(QSize(20, 20))
        self.rotate_cw_btn.clicked.connect(self._rotate_clockwise)
        self.rotate_cw_btn.setEnabled(False)
        self.rotate_cw_btn.setToolTip("Rotate 90 degrees clockwise")
        layout.addWidget(self.rotate_cw_btn)

        # Rotate Counter-Clockwise
        self.rotate_ccw_btn = QPushButton()
        self.rotate_ccw_btn.setIcon(self._create_rotate_ccw_icon())
        self.rotate_ccw_btn.setText("Rotate 90° CCW")
        self.rotate_ccw_btn.setIconSize(QSize(20, 20))
        self.rotate_ccw_btn.clicked.connect(self._rotate_counterclockwise)
        self.rotate_ccw_btn.setEnabled(False)
        self.rotate_ccw_btn.setToolTip("Rotate 90 degrees counter-clockwise")
        layout.addWidget(self.rotate_ccw_btn)

        layout.addSpacing(5)

        # Copy
        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(self._create_copy_icon())
        self.copy_btn.setText("Copy")
        self.copy_btn.setIconSize(QSize(20, 20))
        self.copy_btn.clicked.connect(self._copy_texture)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setToolTip("Copy texture to clipboard")
        layout.addWidget(self.copy_btn)

        # Paste
        self.paste_btn = QPushButton()
        self.paste_btn.setIcon(self._create_paste_icon())
        self.paste_btn.setText("Paste")
        self.paste_btn.setIconSize(QSize(20, 20))
        self.paste_btn.clicked.connect(self._paste_texture)
        self.paste_btn.setEnabled(False)
        self.paste_btn.setToolTip("Paste texture from clipboard")
        layout.addWidget(self.paste_btn)

        # Edit
        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(self._create_edit_icon())
        self.edit_btn.setText("Edit")
        self.edit_btn.setIconSize(QSize(20, 20))
        self.edit_btn.clicked.connect(self._edit_texture)
        self.edit_btn.setEnabled(False)
        self.edit_btn.setToolTip("Edit texture in external editor")
        layout.addWidget(self.edit_btn)

        # Convert
        self.convert_btn = QPushButton()
        self.convert_btn.setIcon(self._create_convert_icon())
        self.convert_btn.setText("Convert")
        self.convert_btn.setIconSize(QSize(20, 20))
        self.convert_btn.clicked.connect(self._convert_texture)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setToolTip("Convert texture format")
        layout.addWidget(self.convert_btn)

        layout.addSpacing(5)

        # Create Texture
        self.create_texture_btn = QPushButton()
        self.create_texture_btn.setIcon(self._create_create_icon())
        self.create_texture_btn.setText("Create")
        self.create_texture_btn.setIconSize(QSize(20, 20))
        self.create_texture_btn.clicked.connect(self._create_new_texture_entry)
        self.create_texture_btn.setToolTip("Create new blank texture")
        layout.addWidget(self.create_texture_btn)

        # Delete Texture
        self.delete_texture_btn = QPushButton()
        self.delete_texture_btn.setIcon(self._create_delete_icon())
        self.delete_texture_btn.setText("Delete")
        self.delete_texture_btn.setIconSize(QSize(20, 20))
        self.delete_texture_btn.clicked.connect(self._delete_texture)
        self.delete_texture_btn.setEnabled(False)
        self.delete_texture_btn.setToolTip("Remove selected texture")
        layout.addWidget(self.delete_texture_btn)

        # Duplicate Texture
        self.duplicate_texture_btn = QPushButton()
        self.duplicate_texture_btn.setIcon(self._create_duplicate_icon())
        self.duplicate_texture_btn.setText("Duplicate")
        self.duplicate_texture_btn.setIconSize(QSize(20, 20))
        self.duplicate_texture_btn.clicked.connect(self._duplicate_texture)
        self.duplicate_texture_btn.setEnabled(False)
        self.duplicate_texture_btn.setToolTip("Clone selected texture")
        layout.addWidget(self.duplicate_texture_btn)

        layout.addSpacing(5)

        # Filters
        self.filters_btn = QPushButton()
        self.filters_btn.setIcon(self._create_filter_icon())
        self.filters_btn.setText("Filters")
        self.filters_btn.setIconSize(QSize(20, 20))
        self.filters_btn.clicked.connect(self._open_filters_dialog)
        self.filters_btn.setEnabled(False)
        self.filters_btn.setToolTip("Brightness, Contrast, Saturation")
        layout.addWidget(self.filters_btn)

        layout.addStretch()

        return self.transform_panel


    def _add_new_texture(self): #vers 1
        """Import new texture to TXD"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Texture", "",
            "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
        )

        if file_path:
            QMessageBox.information(self, "Import Texture",
                f"Import texture functionality:\n{os.path.basename(file_path)}\n\n"
                "Will create new texture entry in TXD")


    def _duplicate_texture(self): #vers 1
        """Duplicate selected texture"""
        if not self.selected_texture:
            return

        import copy
        new_texture = copy.deepcopy(self.selected_texture)
        new_texture['name'] = f"{new_texture['name']}_copy"
        if new_texture.get('has_alpha'):
            new_texture['alpha_name'] = f"{new_texture.get('alpha_name', '')}_copy"

        self.texture_list.append(new_texture)
        self._save_undo_state("Duplicate texture")
        self._reload_texture_table()
        self._mark_as_modified()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📋 Duplicated: {self.selected_texture['name']}")


    def _edit_texture(self): #vers 1
        """Edit texture in external editor"""
        if not self.selected_texture:
            return

        QMessageBox.information(self, "Edit Texture",
            "External texture editor coming soon!\n\n"
            "This will allow editing textures in an external image editor.")


    def _open_paint_editor(self): #vers 1
        """Open simple paint editor"""
        if not self.selected_texture:
            return

        QMessageBox.information(self, "Paint Editor",
            "Simple pixel paint editor coming soon!\n\n"
            "Features:\n"
            "- Draw pixels\n"
            "- Color picker\n"
            "- Brush sizes\n"
            "- Undo/Redo")


    def _open_filters_dialog(self): #vers 1
        """Open filters dialog"""
        if not self.selected_texture:
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Image Filters")
        dialog.setModal(True)
        dialog.resize(400, 400)

        layout = QVBoxLayout(dialog)

        # Brightness
        layout.addWidget(QLabel("Brightness:"))
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setMinimum(-100)
        brightness_slider.setMaximum(100)
        brightness_slider.setValue(0)
        layout.addWidget(brightness_slider)

        # Contrast
        layout.addWidget(QLabel("Contrast:"))
        contrast_slider = QSlider(Qt.Orientation.Horizontal)
        contrast_slider.setMinimum(-100)
        contrast_slider.setMaximum(100)
        contrast_slider.setValue(0)
        layout.addWidget(contrast_slider)

        # Saturation
        layout.addWidget(QLabel("Saturation:"))
        saturation_slider = QSlider(Qt.Orientation.Horizontal)
        saturation_slider.setMinimum(-100)
        saturation_slider.setMaximum(100)
        saturation_slider.setValue(0)
        layout.addWidget(saturation_slider)

        # Hue
        layout.addWidget(QLabel("Hue Shift:"))
        hue_slider = QSlider(Qt.Orientation.Horizontal)
        hue_slider.setMinimum(0)
        hue_slider.setMaximum(360)
        hue_slider.setValue(0)
        layout.addWidget(hue_slider)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(lambda: QMessageBox.information(
            dialog, "Apply Filters", "Filter application coming soon!"))
        button_layout.addWidget(apply_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda: [
            brightness_slider.setValue(0),
            contrast_slider.setValue(0),
            saturation_slider.setValue(0),
            hue_slider.setValue(0)
        ])
        button_layout.addWidget(reset_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _update_texture_info(self, texture): #vers 6
        """Update texture information display"""
        if not texture:
            self.info_name.setText("")
            self.info_alpha_name.setText("")
            self.info_alpha_name.setVisible(False)
            if hasattr(self, 'alpha_label'):
                self.alpha_label.setVisible(False)
            if hasattr(self, 'preview_widget'):
                self.preview_widget.setText("No texture selected")
            return

        # Set ONLY the name - no extra formatting
        name = texture.get('name', 'Unknown')
        self.info_name.setText(name)

        # Set alpha name if has alpha
        has_alpha = texture.get('has_alpha', False)
        if has_alpha:
            alpha_name = texture.get('alpha_name', name + 'a')
            self.info_alpha_name.setText(alpha_name)
            self.info_alpha_name.setVisible(True)
            if hasattr(self, 'alpha_label'):
                self.alpha_label.setVisible(True)
        else:
            self.info_alpha_name.setText("")
            self.info_alpha_name.setVisible(False)
            if hasattr(self, 'alpha_label'):
                self.alpha_label.setVisible(False)

        # Update size info
        width = texture.get('width', 0)
        height = texture.get('height', 0)
        if hasattr(self, 'info_size'):
            self.info_size.setText(f"Size: {width}x{height}")

        # Update format
        fmt = texture.get('format', 'Unknown')
        if hasattr(self, 'format_status_label'):
            self.format_status_label.setText(f"Format: {fmt}")

        # Update bit depth
        depth = texture.get('depth', 32)
        if hasattr(self, 'info_bitdepth'):
            self.info_bitdepth.setText(f"[{depth}bit]")

        # Update mipmap info
        mipmap_levels = texture.get('mipmap_levels', [])
        num_mipmaps = len(mipmap_levels)
        if hasattr(self, 'info_format'):
            if num_mipmaps > 1:
                self.info_format.setText(f"Mipmaps: {num_mipmaps} levels")
            else:
                self.info_format.setText("Mipmaps: None")

        # Bumpmap detection (FIXED - using 'texture' not 'texture_data')
        has_bumpmap = False
        bumpmap_info = "No data"

        # Check if this version supports bumpmaps
        if is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
            # Check for bumpmap format bits
            if 'raster_format_flags' in texture:
                flags = texture.get('raster_format_flags', 0)
                if flags & 0x10:  # Bit 4 indicates environment/bumpmap
                    has_bumpmap = True
                    bumpmap_info = "Bumpmap present"

            # Also check for explicit bumpmap data
            if 'bumpmap_data' in texture or texture.get('has_bumpmap', False):
                has_bumpmap = True
                bumpmap_info = "Bumpmap present"
        else:
            bumpmap_info = f"Not supported ({self.txd_game})"

        # Update bumpmap UI
        if hasattr(self, 'bumpmap_label'):
            self.bumpmap_label.setText(bumpmap_info)

        if hasattr(self, 'info_format_b'):
            if has_bumpmap:
                self.info_format_b.setStyleSheet("font-weight: bold; color: #4CAF50;")  # Green
            else:
                self.info_format_b.setStyleSheet("font-weight: bold; color: #757575;")  # Gray

        # Bumpmap buttons handled in _on_texture_selected()

        # Update preview with new widget
        rgba_data = texture.get('rgba_data')
        if rgba_data and width > 0 and hasattr(self, 'preview_widget'):
            try:
                image = QImage(rgba_data, width, height, width * 4, QImage.Format.Format_RGBA8888)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    self.preview_widget.set_image(pixmap)
                else:
                    self.preview_widget.setText("Invalid image data")
            except Exception as e:
                self.preview_widget.setText(f"Preview error: {str(e)}")
                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Preview error: {str(e)}")
        elif hasattr(self, 'preview_widget'):
            self.preview_widget.setText("No preview available")


    def _view_bumpmap(self): #vers 1
        """Display bumpmap in preview window"""
        if not self.selected_texture:
            return

        try:
            texture_data = self.selected_texture

            # Extract bumpmap channel
            # Bumpmaps are typically stored as additional texture data
            # This is a simplified implementation

            if 'bumpmap_data' in texture_data:
                bumpmap_image = self._decode_bumpmap(texture_data['bumpmap_data'])

                # Display in preview
                pixmap = QPixmap.fromImage(bumpmap_image)
                self.texture_preview.setPixmap(
                    pixmap.scaled(self.texture_preview.size(),
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
                )

                if self.main_window and hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("Displaying bumpmap channel")
            else:
                QMessageBox.information(self, "No Bumpmap",
                    "Bumpmap data not found in texture")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to view bumpmap: {str(e)}")


    def _export_bumpmap(self): #vers 1
        """Export bumpmap as separate image file"""
        if not self.selected_texture:
            return

        try:
            texture_data = self.selected_texture
            texture_name = texture_data.get('name', 'texture')

            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Bumpmap",
                f"{texture_name}_bumpmap.png",
                "PNG Images (*.png);;All Files (*)"
            )

            if not file_path:
                return

            # Extract and save bumpmap
            if 'bumpmap_data' in texture_data:
                bumpmap_image = self._decode_bumpmap(texture_data['bumpmap_data'])

                if bumpmap_image.save(file_path):
                    QMessageBox.information(self, "Success",
                        f"Bumpmap exported to:\n{file_path}")

                    if self.main_window and hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message(f"Exported bumpmap: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save bumpmap")
            else:
                QMessageBox.information(self, "No Bumpmap",
                    "No bumpmap data found in texture")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


    def _import_bumpmap(self): #vers 1
        """Import bumpmap from image file"""
        if not self.selected_texture:
            QMessageBox.warning(self, "No Selection",
                "Please select a texture to add bumpmap to")
            return

        # Check if version supports bumpmaps
        if not is_bumpmap_supported(self.txd_version_id, self.txd_device_id):
            QMessageBox.warning(self, "Not Supported",
                f"Bumpmaps not supported for {self.txd_game}\n"
                f"Only San Andreas and State of Liberty support bumpmaps")
            return

        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Bumpmap",
                "",
                "Image Files (*.png *.jpg *.bmp *.tga);;All Files (*)"
            )

            if not file_path:
                return

            # Load bumpmap image
            bumpmap_image = QImage(file_path)

            if bumpmap_image.isNull():
                QMessageBox.warning(self, "Error", "Failed to load bumpmap image")
                return

            # Encode bumpmap data
            bumpmap_data = self._encode_bumpmap(bumpmap_image)

            # Add to texture data
            self.selected_texture['bumpmap_data'] = bumpmap_data
            self.selected_texture['has_bumpmap'] = True

            # Mark as modified
            self._mark_as_modified()

            # Update UI
            self._update_texture_info(self.selected_texture)

            QMessageBox.information(self, "Success",
                "Bumpmap imported successfully")

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"Imported bumpmap from: {os.path.basename(file_path)}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {str(e)}")


    def _decode_bumpmap(self, bumpmap_data: bytes) -> QImage: #vers 1
        """Decode bumpmap data to QImage"""
        try:
            # Bumpmaps are typically stored as grayscale or normal maps
            # This is a simplified decoder

            # Assume 8-bit grayscale for now
            width = self.selected_texture.get('width', 256)
            height = self.selected_texture.get('height', 256)

            # Create grayscale image
            image = QImage(width, height, QImage.Format.Format_Grayscale8)

            # Copy data
            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    if idx < len(bumpmap_data):
                        value = bumpmap_data[idx]
                        image.setPixel(x, y, value)

            return image

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Bumpmap decode error: {str(e)}")
            return QImage()

    def _encode_bumpmap(self, image: QImage) -> bytes: #vers 1
        """Encode QImage to bumpmap data"""
        try:
            # Convert to grayscale if not already
            if image.format() != QImage.Format.Format_Grayscale8:
                image = image.convertToFormat(QImage.Format.Format_Grayscale8)

            # Extract pixel data
            width = image.width()
            height = image.height()
            bumpmap_data = bytearray(width * height)

            for y in range(height):
                for x in range(width):
                    pixel = image.pixel(x, y)
                    # Extract grayscale value
                    gray = pixel & 0xFF
                    bumpmap_data[y * width + x] = gray

            return bytes(bumpmap_data)

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Bumpmap encode error: {str(e)}")
            return b''


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


    def open_txd_file(self, file_path=None): #vers 3
        """Open standalone TXD file with version detection"""
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Open TXD File", "",
                    "TXD Files (*.txd);;All Files (*)"
                )

            if file_path:
                with open(file_path, 'rb') as f:
                    txd_data = f.read()

                # Detect version info FIRST
                if not self._detect_txd_info(txd_data):
                    QMessageBox.warning(self, "Invalid TXD",
                        "Could not detect valid TXD format")
                    return

                # Load textures
                self._load_txd_textures(txd_data, os.path.basename(file_path))

                # Update window title with version info
                self.setWindowTitle(
                    f"TXD Workshop: {os.path.basename(file_path)} "
                    f"[{self.txd_version_str}]"
                )

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


    def show_properties(self): #vers 2
        """Show TXD properties including version and platform information"""
        if not self.current_txd_name:
            QMessageBox.information(self, "No TXD", "No TXD file loaded")
            return

        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("TXD Properties")
            dialog.setMinimumWidth(500)

            layout = QFormLayout(dialog)

            # Basic info
            layout.addRow("TXD Name:", QLabel(self.current_txd_name))
            layout.addRow("Texture Count:", QLabel(str(len(self.texture_list))))

            # NEW: Version information
            layout.addRow("", QLabel(""))  # Spacer
            layout.addRow("RenderWare Version:", QLabel(self.txd_version_str))
            layout.addRow("Platform:", QLabel(self.txd_platform_name))
            layout.addRow("Game:", QLabel(self.txd_game))
            layout.addRow("Format:", QLabel(self._get_format_description()))

            # NEW: Capabilities
            if self.txd_capabilities:
                layout.addRow("", QLabel(""))  # Spacer
                caps_label = QLabel("<b>Capabilities:</b>")
                layout.addRow(caps_label)

                if self.txd_capabilities.get('mipmaps'):
                    layout.addRow("  Mipmaps:", QLabel("Supported"))
                if self.txd_capabilities.get('bumpmaps'):
                    layout.addRow("  Bumpmaps:", QLabel("Supported"))
                if self.txd_capabilities.get('dxt_compression'):
                    layout.addRow("  DXT Compression:", QLabel("Supported"))
                if self.txd_capabilities.get('palette'):
                    layout.addRow("  Palette:", QLabel("Supported"))
                if self.txd_capabilities.get('swizzled'):
                    layout.addRow("  Swizzled:", QLabel("Yes (Console)"))

            # File size info
            if self.current_txd_data:
                size_kb = len(self.current_txd_data) / 1024
                layout.addRow("", QLabel(""))  # Spacer
                layout.addRow("File Size:", QLabel(f"{size_kb:.2f} KB"))

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addRow("", close_btn)

            dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not show properties: {str(e)}")


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

    def _create_upscale_icon(self): #vers 2
        """Create upscale icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M7,15L12,10L17,15H7Z"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_compress_icon(self): #vers 2
        """Create compress icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path fill="currentColor"
                d="M4,2H20V4H13V10H20V12H4V10H11V4H4V2M4,13H20V15H13V21H20V23H4V21H11V15H4V13Z"/>
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

    def _create_settings_icon(self): #vers 1
        """Settings/gear icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
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



class MipmapManagerWindow(QWidget): #vers 2
    """Mipmap Manager - Modern card-based design matching mockup"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data
        self.main_window = main_window
        self.modified_levels = {}  # Track modified levels

        texture_name = texture_data.get('name', 'Unknown')
        width = texture_data.get('width', 0)
        height = texture_data.get('height', 0)
        fmt = texture_data.get('format', 'Unknown')

        self.setWindowTitle(f"Mipmap Manager - {texture_name}")
        self.resize(900, 700)

        # Frameless window with custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setup_ui()

        # Enable dragging
        self.dragging = False
        self.drag_position = None


    def setup_ui(self): #vers 2
        """Setup modern UI matching mockup"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)

        # Toolbar with Apply/Close buttons
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #2b2b2b;
                border: none;
            }
        """)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(15)

        # Create level cards
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        for level_data in mipmap_levels:
            card = self._create_level_card(level_data)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Bottom status bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar)


    def _create_title_bar(self): #vers 1
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        title_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        title_bar.setFixedHeight(40)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Title text
        texture_name = self.texture_data.get('name', 'Unknown')
        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)
        fmt = self.texture_data.get('format', 'Unknown')

        title_label = QLabel(f"Mipmap Manager - {texture_name} ({width}x{height}, {fmt})")
        title_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        layout.addWidget(title_label)

        layout.addStretch()

        # Drag handle
        drag_btn = QPushButton("☰")
        drag_btn.setFixedSize(30, 30)
        drag_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #e0e0e0;
            }
        """)
        drag_btn.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(drag_btn)

        return title_bar


    def _create_toolbar(self): #vers 2
        """Create toolbar with action buttons AND Apply/Close"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background: #252525;
                border-bottom: 1px solid #3a3a3a;
            }
            QPushButton {
                background: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 8px 16px;
                border-radius: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        toolbar.setFixedHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Left side - Action buttons
        autogen_btn = QPushButton("🔄 Auto-Generate")
        autogen_btn.setToolTip("Generate all mipmap levels")
        autogen_btn.clicked.connect(self._auto_generate_mipmaps)
        layout.addWidget(autogen_btn)

        export_all_btn = QPushButton("📤 Export All")
        export_all_btn.setToolTip("Export all levels as PNG")
        export_all_btn.clicked.connect(self._export_all_levels)
        layout.addWidget(export_all_btn)

        import_all_btn = QPushButton("📥 Import All")
        import_all_btn.setToolTip("Import levels from PNG files")
        import_all_btn.clicked.connect(self._import_all_levels)
        layout.addWidget(import_all_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setToolTip("Remove all mipmap levels except Level 0")
        clear_btn.clicked.connect(self._clear_all_levels)
        layout.addWidget(clear_btn)

        layout.addStretch()

        # Right side - Apply/Close buttons
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0d47a1;
                border-color: #1976d2;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #1976d2;
            }
        """)
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return toolbar


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


    def _create_preview_widget(self, level_data): #vers 1
        """Create preview thumbnail with checkerboard"""
        level_num = level_data.get('level', 0)
        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        rgba_data = level_data.get('rgba_data')

        # Scale preview size based on level
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
                preview.setText("🖼️")
        else:
            preview.setText("🖼️")

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

        # Main texture indicator
        if level_num == 0:
            main_badge = QLabel("● Main Texture")
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

        fmt = level_data.get('format', self.texture_data.get('format', 'Unknown'))
        size = level_data.get('compressed_size', 0)
        size_kb = size / 1024

        # Format stat
        format_stat = self._create_stat_box("Format:", fmt)
        grid_layout.addWidget(format_stat)

        # Size stat
        size_stat = self._create_stat_box("Size:", f"{size_kb:.1f} KB")
        grid_layout.addWidget(size_stat)

        # Compression stat
        if 'DXT' in fmt:
            ratio = "4:1" if 'DXT5' in fmt or 'DXT3' in fmt else "6:1"
            comp_stat = self._create_stat_box("Compression:", ratio)
        else:
            comp_stat = self._create_stat_box("Compression:", "None")
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
        export_btn = QPushButton("📤 Export")
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
        import_btn = QPushButton("📥 Import")
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
            edit_btn = QPushButton("✏️ Edit")
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
            edit_btn.clicked.connect(self._edit_main_texture)
            layout.addWidget(edit_btn)
        else:
            delete_btn = QPushButton("🗑️ Delete")
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


    def _create_bottom_bar(self): #vers 1
        """Create bottom status bar"""
        bottom_bar = QFrame()
        bottom_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        bottom_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-top: 1px solid #3a3a3a;
            }
        """)
        bottom_bar.setFixedHeight(45)

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Left side - Stats
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        num_levels = len(mipmap_levels)
        total_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        total_size_kb = total_size / 1024

        stats_label = QLabel(f"Total Levels: {num_levels} | Total Size: {total_size_kb:.1f} KB")
        stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(stats_label)

        # Modified badge if there are changes
        if self.modified_levels:
            modified_badge = QLabel("● Modified")
            modified_badge.setStyleSheet("""
                QLabel {
                    background: #ff6b35;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-left: 10px;
                }
            """)
            layout.addWidget(modified_badge)

        layout.addStretch()

        return bottom_bar


    def mousePressEvent(self, event): #vers 1
        """Enable window dragging from title bar"""
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 40:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()


    def mouseMoveEvent(self, event): #vers 1
        """Handle window dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


    def mouseReleaseEvent(self, event): #vers 1
        """Stop dragging"""
        self.dragging = False


    def _auto_generate_mipmaps(self): #vers 1
        """Auto-generate all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("🔄 Auto-generating mipmaps...")
        # Call parent's generate method
        if hasattr(self.parent_workshop, '_auto_generate_mipmaps'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data
            self.parent_workshop._auto_generate_mipmaps()
            self.parent_workshop.selected_texture = old_selection
            # Refresh window
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _export_all_levels(self): #vers 1
        """Export all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📤 Exporting all mipmap levels...")

        from PyQt6.QtWidgets import QFileDialog
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        # Export logic here
        QMessageBox.information(self, "Export", "Mipmap export functionality coming soon!")


    def _import_all_levels(self): #vers 1
        """Import mipmap levels from files"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📥 Importing mipmap levels...")
        QMessageBox.information(self, "Import", "Mipmap import functionality coming soon!")


    def _clear_all_levels(self): #vers 1
        """Clear all mipmap levels except Level 0"""
        reply = QMessageBox.question(
            self, "Clear Mipmaps",
            "Remove all mipmap levels except Level 0?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if 'mipmap_levels' in self.texture_data:
                # Keep only level 0
                level_0 = next((l for l in self.texture_data['mipmap_levels'] if l.get('level') == 0), None)
                if level_0:
                    self.texture_data['mipmap_levels'] = [level_0]
                    self.texture_data['mipmaps'] = 1
                    self.close()
                    new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
                    new_window.show()


    def _export_level(self, level_num): #vers 1
        """Export single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📤 Exporting Level {level_num}...")


    def _import_level(self, level_num): #vers 1
        """Import single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📥 Importing Level {level_num}...")
        self.modified_levels[level_num] = True


    def _delete_level(self, level_num): #vers 1
        """Delete mipmap level"""
        reply = QMessageBox.question(
            self, "Delete Level",
            f"Delete Level {level_num}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.texture_data['mipmap_levels'] = [
                l for l in self.texture_data.get('mipmap_levels', [])
                if l.get('level') != level_num
            ]
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _edit_main_texture(self): #vers 1
        """Edit main texture"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("✏️ Editing main texture...")


    def _apply_changes(self): #vers 1
        """Apply all changes and close"""
        if self.modified_levels:
            # Update parent workshop
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            if hasattr(self.parent_workshop, '_reload_texture_table'):
                self.parent_workshop._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Mipmap changes applied")

        self.close()


class MipmapManagerWindow(QWidget): #vers 2
    """Mipmap Manager - Modern card-based design matching mockup"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data
        self.main_window = main_window
        self.modified_levels = {}  # Track modified levels

        texture_name = texture_data.get('name', 'Unknown')
        width = texture_data.get('width', 0)
        height = texture_data.get('height', 0)
        fmt = texture_data.get('format', 'Unknown')

        self.setWindowTitle(f"Mipmap Manager - {texture_name}")
        self.resize(1080, 700)  # 20% wider (900 * 1.2 = 1080)

        # Frameless window with custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        self.setup_ui()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)


    def setup_ui(self): #vers 2
        """Setup modern UI matching mockup"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)

        # Toolbar with Apply/Close buttons
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #2b2b2b;
                border: none;
            }
        """)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(15)

        # Create level cards
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        for level_data in mipmap_levels:
            card = self._create_level_card(level_data)
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Bottom status bar
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar)


    def _create_title_bar(self): #vers 1
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        title_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-bottom: 1px solid #3a3a3a;
            }
        """)
        title_bar.setFixedHeight(40)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Title text
        texture_name = self.texture_data.get('name', 'Unknown')
        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)
        fmt = self.texture_data.get('format', 'Unknown')

        title_label = QLabel(f"Mipmap Manager - {texture_name} ({width}x{height}, {fmt})")
        title_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        layout.addWidget(title_label)

        layout.addStretch()

        # Drag handle
        drag_btn = QPushButton("☰")
        drag_btn.setFixedSize(30, 30)
        drag_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #e0e0e0;
            }
        """)
        drag_btn.setCursor(Qt.CursorShape.SizeAllCursor)
        layout.addWidget(drag_btn)

        return title_bar


    def _create_toolbar(self): #vers 2
        """Create toolbar with action buttons AND Apply/Close"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background: #252525;
                border-bottom: 1px solid #3a3a3a;
            }
            QPushButton {
                background: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                padding: 8px 16px;
                border-radius: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        toolbar.setFixedHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Left side - Action buttons
        autogen_btn = QPushButton("🔄 Auto-Generate")
        autogen_btn.setToolTip("Generate all mipmap levels")
        autogen_btn.clicked.connect(self._auto_generate_mipmaps)
        layout.addWidget(autogen_btn)

        export_all_btn = QPushButton("📤 Export All")
        export_all_btn.setToolTip("Export all levels as PNG")
        export_all_btn.clicked.connect(self._export_all_levels)
        layout.addWidget(export_all_btn)

        import_all_btn = QPushButton("📥 Import All")
        import_all_btn.setToolTip("Import levels from PNG files")
        import_all_btn.clicked.connect(self._import_all_levels)
        layout.addWidget(import_all_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setToolTip("Remove all mipmap levels except Level 0")
        clear_btn.clicked.connect(self._clear_all_levels)
        layout.addWidget(clear_btn)

        layout.addStretch()

        # Right side - Apply/Close buttons
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #0d47a1;
                border-color: #1976d2;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #1976d2;
            }
        """)
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return toolbar


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


    def _create_preview_widget(self, level_data): #vers 1
        """Create preview thumbnail with checkerboard"""
        level_num = level_data.get('level', 0)
        width = level_data.get('width', 0)
        height = level_data.get('height', 0)
        rgba_data = level_data.get('rgba_data')

        # Scale preview size based on level
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
                preview.setText("🖼️")
        else:
            preview.setText("🖼️")

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

        # Main texture indicator
        if level_num == 0:
            main_badge = QLabel("● Main Texture")
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

        fmt = level_data.get('format', self.texture_data.get('format', 'Unknown'))
        size = level_data.get('compressed_size', 0)
        size_kb = size / 1024

        # Format stat
        format_stat = self._create_stat_box("Format:", fmt)
        grid_layout.addWidget(format_stat)

        # Size stat
        size_stat = self._create_stat_box("Size:", f"{size_kb:.1f} KB")
        grid_layout.addWidget(size_stat)

        # Compression stat
        if 'DXT' in fmt:
            ratio = "4:1" if 'DXT5' in fmt or 'DXT3' in fmt else "6:1"
            comp_stat = self._create_stat_box("Compression:", ratio)
        else:
            comp_stat = self._create_stat_box("Compression:", "None")
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
        export_btn = QPushButton("📤 Export")
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
        import_btn = QPushButton("📥 Import")
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
            edit_btn = QPushButton("✏️ Edit")
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
            edit_btn.clicked.connect(self._edit_main_texture)
            layout.addWidget(edit_btn)
        else:
            delete_btn = QPushButton("🗑️ Delete")
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


    def _create_bottom_bar(self): #vers 1
        """Create bottom status bar"""
        bottom_bar = QFrame()
        bottom_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        bottom_bar.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border-top: 1px solid #3a3a3a;
            }
        """)
        bottom_bar.setFixedHeight(45)

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        # Left side - Stats
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        num_levels = len(mipmap_levels)
        total_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        total_size_kb = total_size / 1024

        stats_label = QLabel(f"Total Levels: {num_levels} | Total Size: {total_size_kb:.1f} KB")
        stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(stats_label)

        # Modified badge if there are changes
        if self.modified_levels:
            modified_badge = QLabel("● Modified")
            modified_badge.setStyleSheet("""
                QLabel {
                    background: #ff6b35;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-left: 10px;
                }
            """)
            layout.addWidget(modified_badge)

        layout.addStretch()

        return bottom_bar


    def mousePressEvent(self, event): #vers 1
        """Enable window dragging from title bar"""
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 40:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event): #vers 1
        """Handle window dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


    def mouseReleaseEvent(self, event): #vers 1
        """Stop dragging"""
        self.dragging = False


    def _auto_generate_mipmaps(self): #vers 1
        """Auto-generate all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("🔄 Auto-generating mipmaps...")
        # Call parent's generate method
        if hasattr(self.parent_workshop, '_auto_generate_mipmaps'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.texture_data
            self.parent_workshop._auto_generate_mipmaps()
            self.parent_workshop.selected_texture = old_selection
            # Refresh window
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _export_all_levels(self): #vers 1
        """Export all mipmap levels"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📤 Exporting all mipmap levels...")

        from PyQt6.QtWidgets import QFileDialog
        output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not output_dir:
            return

        # Export logic here
        QMessageBox.information(self, "Export", "Mipmap export functionality coming soon!")


    def _import_all_levels(self): #vers 1
        """Import mipmap levels from files"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("📥 Importing mipmap levels...")
        QMessageBox.information(self, "Import", "Mipmap import functionality coming soon!")


    def _clear_all_levels(self): #vers 1
        """Clear all mipmap levels except Level 0"""
        reply = QMessageBox.question(
            self, "Clear Mipmaps",
            "Remove all mipmap levels except Level 0?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if 'mipmap_levels' in self.texture_data:
                # Keep only level 0
                level_0 = next((l for l in self.texture_data['mipmap_levels'] if l.get('level') == 0), None)
                if level_0:
                    self.texture_data['mipmap_levels'] = [level_0]
                    self.texture_data['mipmaps'] = 1
                    self.close()
                    new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
                    new_window.show()


    def _export_level(self, level_num): #vers 1
        """Export single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📤 Exporting Level {level_num}...")


    def _import_level(self, level_num): #vers 1
        """Import single mipmap level"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📥 Importing Level {level_num}...")
        self.modified_levels[level_num] = True


    def _delete_level(self, level_num): #vers 1
        """Delete mipmap level"""
        reply = QMessageBox.question(
            self, "Delete Level",
            f"Delete Level {level_num}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.texture_data['mipmap_levels'] = [
                l for l in self.texture_data.get('mipmap_levels', [])
                if l.get('level') != level_num
            ]
            self.close()
            new_window = MipmapManagerWindow(self.parent_workshop, self.texture_data, self.main_window)
            new_window.show()


    def _edit_main_texture(self): #vers 1
        """Edit main texture"""
        if self.main_window and hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("✏️ Editing main texture...")


    def _apply_changes(self): #vers 1
        """Apply all changes and close"""
        if self.modified_levels:
            # Update parent workshop
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            if hasattr(self.parent_workshop, '_reload_texture_table'):
                self.parent_workshop._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Mipmap changes applied")

        self.close()


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


class TexturePropertiesDialog(QDialog): #vers 1
    """Complete texture properties dialog with all settings"""

    def __init__(self, parent, texture_data, main_window=None):
        super().__init__(parent)
        self.parent_workshop = parent
        self.texture_data = texture_data.copy()  # Work on copy
        self.original_texture = texture_data
        self.main_window = main_window
        self.changes_made = False

        self.setWindowTitle(f"Properties: {texture_data.get('name', 'Unknown')}")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "Settings")


    def setup_ui(self): #vers 1
        """Setup properties dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with texture name
        header = QLabel(f"Texture: {self.texture_data.get('name', 'Unknown')}")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Tabs for different property sections
        tabs = QTabWidget()

        # Tab 1: Basic Info
        basic_tab = self._create_basic_tab()
        tabs.addTab(basic_tab, "Basic")

        # Tab 2: Format Settings
        format_tab = self._create_format_tab()
        tabs.addTab(format_tab, "Format")

        # Tab 3: Mipmap Info
        mipmap_tab = self._create_mipmap_tab()
        tabs.addTab(mipmap_tab, "Mipmaps")

        # Tab 4: Advanced
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_changes)
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._ok_clicked)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)


    def _create_settings_tab(self): #vers 2
        """Create settings/appearance tab with button mode"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Workshop Appearance group
        workshop_group = QGroupBox("Workshop Appearance")
        workshop_layout = QFormLayout(workshop_group)

        # Button display mode
        button_mode_combo = QComboBox()
        button_mode_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])

        # Set current mode
        if hasattr(self.parent_workshop, 'button_display_mode'):
            mode_map = {'both': 0, 'icons': 1, 'text': 2}
            current_index = mode_map.get(self.parent_workshop.button_display_mode, 0)
            button_mode_combo.setCurrentIndex(current_index)

        # Connect to update
        button_mode_combo.currentIndexChanged.connect(
            lambda idx: self._change_workshop_button_mode(idx)
        )

        workshop_layout.addRow("Button Style:", button_mode_combo)

        layout.addWidget(workshop_group)

        # ... rest of settings tab ...

        layout.addStretch()
        return tab


    def _change_workshop_button_mode(self, index): #vers 1
        """Change button display mode from properties"""
        if not hasattr(self, 'parent_workshop'):
            return

        mode_map = {0: 'both', 1: 'icons', 2: 'text'}
        new_mode = mode_map[index]

        self.parent_workshop.button_display_mode = new_mode
        self.parent_workshop._update_all_buttons()


    def _create_basic_tab(self): #vers 1
        """Create basic info tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Names group
        names_group = QGroupBox("Names")
        names_layout = QFormLayout(names_group)

        self.name_edit = QLineEdit(self.texture_data.get('name', ''))
        self.name_edit.setMaxLength(32)
        names_layout.addRow("Texture Name:", self.name_edit)

        # Alpha name (if has alpha)
        if self.texture_data.get('has_alpha', False):
            alpha_name = self.texture_data.get('alpha_name', self.texture_data.get('name', '') + 'a')
            self.alpha_name_edit = QLineEdit(alpha_name)
            self.alpha_name_edit.setMaxLength(32)
            names_layout.addRow("Alpha Name:", self.alpha_name_edit)
        else:
            self.alpha_name_edit = None

        layout.addWidget(names_group)

        # Dimensions group
        dim_group = QGroupBox("Dimensions")
        dim_layout = QFormLayout(dim_group)

        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)

        dim_label = QLabel(f"{width} x {height} pixels")
        dim_label.setStyleSheet("font-weight: bold;")
        dim_layout.addRow("Size:", dim_label)

        # Calculate memory size
        uncompressed_size = width * height * 4  # RGBA
        size_kb = uncompressed_size / 1024
        size_mb = size_kb / 1024

        if size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.2f} KB"

        size_label = QLabel(f"{size_str} (uncompressed)")
        dim_layout.addRow("Memory:", size_label)

        # Aspect ratio
        if width > 0 and height > 0:
            from math import gcd
            divisor = gcd(width, height)
            aspect_w = width // divisor
            aspect_h = height // divisor
            aspect_label = QLabel(f"{aspect_w}:{aspect_h}")
            dim_layout.addRow("Aspect Ratio:", aspect_label)

        layout.addWidget(dim_group)

        # Color info group
        color_group = QGroupBox("Color Information")
        color_layout = QFormLayout(color_group)

        depth = self.texture_data.get('depth', 32)
        color_layout.addRow("Bit Depth:", QLabel(f"{depth} bit"))

        has_alpha = self.texture_data.get('has_alpha', False)
        alpha_status = QLabel("Yes" if has_alpha else "No")
        alpha_status.setStyleSheet("color: red; font-weight: bold;" if has_alpha else "")
        color_layout.addRow("Alpha Channel:", alpha_status)

        layout.addWidget(color_group)

        layout.addStretch()
        return tab


    def _create_settings_tab(self): #vers 1
        """Create settings/appearance tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Appearance group
        appearance_group = QGroupBox("Workshop Appearance")
        appearance_layout = QFormLayout(appearance_group)

        # Theme selector
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark Theme", "Light Theme", "Green Theme", "Blue Theme", "Custom"])
        appearance_layout.addRow("Theme:", theme_combo)

        # Button style
        button_style_combo = QComboBox()
        button_style_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])
        appearance_layout.addRow("Button Style:", button_style_combo)

        # Icon size
        icon_size_combo = QComboBox()
        icon_size_combo.addItems(["Small (16px)", "Medium (20px)", "Large (24px)"])
        icon_size_combo.setCurrentIndex(1)
        appearance_layout.addRow("Icon Size:", icon_size_combo)

        # Layout
        layout_combo = QComboBox()
        layout_combo.addItems(["Compact", "Normal", "Spacious"])
        layout_combo.setCurrentIndex(1)
        appearance_layout.addRow("Layout:", layout_combo)

        layout.addWidget(appearance_group)

        # Preview options
        preview_group = QGroupBox("Preview Settings")
        preview_layout = QFormLayout(preview_group)

        # Thumbnail size
        thumb_size_combo = QComboBox()
        thumb_size_combo.addItems(["Small (64px)", "Medium (80px)", "Large (120px)"])
        thumb_size_combo.setCurrentIndex(1)
        preview_layout.addRow("Thumbnail Size:", thumb_size_combo)

        # Preview background
        bg_combo = QComboBox()
        bg_combo.addItems(["Checkerboard", "Black", "White", "Gray"])
        preview_layout.addRow("Preview Background:", bg_combo)

        layout.addWidget(preview_group)

        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)

        font_size_combo = QComboBox()
        font_size_combo.addItems(["Small", "Medium", "Large"])
        font_size_combo.setCurrentIndex(1)
        font_layout.addRow("Font Size:", font_size_combo)

        layout.addWidget(font_group)

        layout.addStretch()

        # Note
        note = QLabel("Note: Some settings require restart to take full effect")
        note.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(note)

        return tab


    def _create_format_tab(self): #vers 1
        """Create format settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Current format group
        format_group = QGroupBox("Texture Format")
        format_layout = QFormLayout(format_group)

        current_format = self.texture_data.get('format', 'Unknown')
        format_label = QLabel(current_format)
        format_label.setStyleSheet("font-weight: bold;")
        format_layout.addRow("Current Format:", format_label)

        # Compression status
        is_compressed = 'DXT' in current_format
        compress_label = QLabel("Compressed" if is_compressed else "Uncompressed")
        compress_label.setStyleSheet("color: green;" if is_compressed else "color: orange;")
        format_layout.addRow("Status:", compress_label)

        # Show compression ratio if compressed
        if is_compressed:
            width = self.texture_data.get('width', 0)
            height = self.texture_data.get('height', 0)
            uncompressed = width * height * 4

            rgba_data = self.texture_data.get('rgba_data', b'')
            compressed = len(rgba_data) if rgba_data else 0

            if uncompressed > 0 and compressed > 0:
                ratio = uncompressed / compressed
                ratio_label = QLabel(f"{ratio:.1f}:1")
                format_layout.addRow("Compression Ratio:", ratio_label)

        layout.addWidget(format_group)

        # Format conversion group
        convert_group = QGroupBox("Format Conversion")
        convert_layout = QVBoxLayout(convert_group)

        convert_layout.addWidget(QLabel("Select target format:"))

        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "DXT1 (No Alpha, 6:1)",
            "DXT3 (Sharp Alpha, 4:1)",
            "DXT5 (Smooth Alpha, 4:1)",
            "ARGB8888 (Uncompressed)",
            "RGB888 (Uncompressed, No Alpha)"
        ])

        # Set current selection
        format_map = {
            'DXT1': 0, 'DXT3': 1, 'DXT5': 2,
            'ARGB8888': 3, 'RGB888': 4
        }
        current_idx = format_map.get(current_format, 0)
        self.format_combo.setCurrentIndex(current_idx)

        convert_layout.addWidget(self.format_combo)

        convert_note = QLabel(
            "Note: Format conversion will be applied when you click Apply or OK.\n"
            "DXT formats reduce file size but may lose quality."
        )
        convert_note.setStyleSheet("color: #888; font-size: 10px;")
        convert_note.setWordWrap(True)
        convert_layout.addWidget(convert_note)

        layout.addWidget(convert_group)

        layout.addStretch()
        return tab


    def _create_mipmap_tab(self): #vers 1
        """Create mipmap info tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Mipmap status group
        status_group = QGroupBox("Mipmap Status")
        status_layout = QFormLayout(status_group)

        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        num_mipmaps = len(mipmap_levels)

        status_layout.addRow("Levels:", QLabel(str(num_mipmaps)))

        if num_mipmaps > 0:
            # Show level details
            details = QTextEdit()
            details.setReadOnly(True)
            details.setMaximumHeight(200)

            details_text = ""
            for level in mipmap_levels:
                level_num = level.get('level', 0)
                w = level.get('width', 0)
                h = level.get('height', 0)
                size = level.get('compressed_size', 0)
                size_kb = size / 1024

                details_text += f"Level {level_num}: {w}x{h} ({size_kb:.1f} KB)\n"

            details.setText(details_text)
            status_layout.addRow("Details:", details)
        else:
            no_mipmap_label = QLabel("No mipmaps generated")
            no_mipmap_label.setStyleSheet("color: orange;")
            status_layout.addRow("Status:", no_mipmap_label)

        layout.addWidget(status_group)

        # Mipmap actions group
        actions_group = QGroupBox("Mipmap Actions")
        actions_layout = QVBoxLayout(actions_group)

        generate_btn = QPushButton("Generate Mipmaps")
        generate_btn.clicked.connect(self._generate_mipmaps)
        actions_layout.addWidget(generate_btn)

        if num_mipmaps > 0:
            view_btn = QPushButton("View All Levels")
            view_btn.clicked.connect(self._view_mipmaps)
            actions_layout.addWidget(view_btn)

            export_btn = QPushButton("Export All Levels")
            export_btn.clicked.connect(self._export_mipmaps)
            actions_layout.addWidget(export_btn)

        layout.addWidget(actions_group)

        layout.addStretch()
        return tab


    def _create_advanced_tab(self): #vers 1
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Technical info group
        tech_group = QGroupBox("Technical Information")
        tech_layout = QFormLayout(tech_group)

        # RenderWare version
        rw_version = self.texture_data.get('rw_version', 'Unknown')
        tech_layout.addRow("RW Version:", QLabel(str(rw_version)))

        # Platform
        platform = self.texture_data.get('platform', 'PC')
        tech_layout.addRow("Platform:", QLabel(platform))

        # Texture flags
        flags = self.texture_data.get('flags', 0)
        tech_layout.addRow("Flags:", QLabel(f"0x{flags:04X}"))

        layout.addWidget(tech_group)

        # Memory stats group
        mem_group = QGroupBox("Memory Statistics")
        mem_layout = QFormLayout(mem_group)

        width = self.texture_data.get('width', 0)
        height = self.texture_data.get('height', 0)

        # Uncompressed size
        uncompressed = width * height * 4
        mem_layout.addRow("Uncompressed:", QLabel(f"{uncompressed:,} bytes"))

        # Current size
        rgba_data = self.texture_data.get('rgba_data', b'')
        current_size = len(rgba_data) if rgba_data else 0
        mem_layout.addRow("Current:", QLabel(f"{current_size:,} bytes"))

        # With mipmaps
        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        total_mipmap_size = sum(level.get('compressed_size', 0) for level in mipmap_levels)
        mem_layout.addRow("With Mipmaps:", QLabel(f"{total_mipmap_size:,} bytes"))

        layout.addWidget(mem_group)

        layout.addStretch()
        return tab


    def _apply_changes(self): #vers 1
        """Apply changes to texture"""
        # Update name
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.original_texture.get('name', ''):
            self.original_texture['name'] = new_name
            self.changes_made = True

        # Update alpha name if exists
        if self.alpha_name_edit:
            new_alpha_name = self.alpha_name_edit.text().strip()
            if new_alpha_name and new_alpha_name != self.original_texture.get('alpha_name', ''):
                self.original_texture['alpha_name'] = new_alpha_name
                self.changes_made = True

        # Update format if changed
        format_map = ['DXT1', 'DXT3', 'DXT5', 'ARGB8888', 'RGB888']
        new_format = format_map[self.format_combo.currentIndex()]

        if new_format != self.original_texture.get('format', ''):
            # Mark for format conversion
            self.original_texture['target_format'] = new_format
            self.changes_made = True

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"ℹ️ Format change queued: {new_format}")

        if self.changes_made:
            # Notify parent workshop
            if hasattr(self.parent_workshop, '_mark_as_modified'):
                self.parent_workshop._mark_as_modified()

            if hasattr(self.parent_workshop, '_reload_texture_table'):
                self.parent_workshop._reload_texture_table()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("✅ Properties updated")


    def _ok_clicked(self): #vers 1
        """Apply changes and close"""
        self._apply_changes()
        self.accept()


    def _generate_mipmaps(self): #vers 2
        """Generate mipmaps with user-selected depth"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout

        # Calculate possible mipmap levels
        width = self.texture_data.get('width', 256)
        height = self.texture_data.get('height', 256)
        max_dimension = max(width, height)

        # Calculate how many levels possible (down to 1x1)
        import math
        max_levels = int(math.log2(max_dimension)) + 1

        # Create selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Mipmaps")
        dialog.setModal(True)
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)

        # Header info
        header = QLabel(f"Texture Size: {width}x{height}\nSelect minimum mipmap size:")
        header.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Slider with level preview
        slider_layout = QVBoxLayout()

        self.mipmap_slider = QSlider(Qt.Orientation.Horizontal)
        self.mipmap_slider.setMinimum(0)  # Down to 1x1
        self.mipmap_slider.setMaximum(max_levels - 1)
        self.mipmap_slider.setValue(max_levels - 6)  # Default to ~32x32
        self.mipmap_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.mipmap_slider.setTickInterval(1)

        # Preview label showing dimensions at each level
        self.mipmap_preview = QLabel()
        self.mipmap_preview.setStyleSheet("font-size: 14px; padding: 10px; background: #2a2a2a; border-radius: 3px;")
        self.mipmap_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)


        def update_preview(value):
            # Calculate dimensions at this level
            levels_from_top = max_levels - 1 - value
            min_w = max(1, width >> levels_from_top)
            min_h = max(1, height >> levels_from_top)
            num_levels = max_levels - value

            preview_text = f"Minimum Size: {min_w}x{min_h}\n"
            preview_text += f"Total Levels: {num_levels}\n\n"
            preview_text += f"Levels: {width}x{height}"

            # Show a few intermediate levels
            current_w, current_h = width, height
            shown = 1
            for i in range(1, num_levels):
                current_w = max(1, current_w // 2)
                current_h = max(1, current_h // 2)
                if shown < 4 or i == num_levels - 1:  # Show first 3 and last
                    preview_text += f" → {current_w}x{current_h}"
                    shown += 1
                elif shown == 4:
                    preview_text += " → ..."
                    shown += 1

            self.mipmap_preview.setText(preview_text)

        self.mipmap_slider.valueChanged.connect(update_preview)
        update_preview(self.mipmap_slider.value())

        slider_layout.addWidget(QLabel("More Levels ←  →  Fewer Levels"))
        slider_layout.addWidget(self.mipmap_slider)
        slider_layout.addWidget(self.mipmap_preview)

        layout.addLayout(slider_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(lambda: self._do_generate_mipmaps(dialog, max_levels))
        button_layout.addWidget(generate_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()


    def _do_generate_mipmaps(self, dialog, max_levels): #vers 1
        """Actually generate the mipmaps with selected depth"""
        slider_value = self.mipmap_slider.value()
        num_levels = max_levels - slider_value

        dialog.accept()

        if hasattr(self.parent_workshop, '_auto_generate_mipmaps_to_level'):
            # Use enhanced version with level control
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.original_texture

            self.parent_workshop._auto_generate_mipmaps_to_level(num_levels)

            self.parent_workshop.selected_texture = old_selection
        elif hasattr(self.parent_workshop, '_auto_generate_mipmaps'):
            # Fallback to basic version
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.original_texture

            self.parent_workshop._auto_generate_mipmaps()

            self.parent_workshop.selected_texture = old_selection

        # Refresh dialog
        self.close()
        new_dialog = TexturePropertiesDialog(self.parent_workshop, self.original_texture, self.main_window)
        new_dialog.exec()


    def _view_mipmaps(self): #vers 1
        """Open mipmap manager"""
        if hasattr(self.parent_workshop, '_open_mipmap_manager'):
            old_selection = self.parent_workshop.selected_texture
            self.parent_workshop.selected_texture = self.original_texture

            self.parent_workshop._open_mipmap_manager()

            self.parent_workshop.selected_texture = old_selection


    def _export_mipmaps(self): #vers 1
        """Export all mipmap levels"""
        from PyQt6.QtWidgets import QFileDialog
        import os

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        mipmap_levels = self.texture_data.get('mipmap_levels', [])
        name = self.texture_data.get('name', 'texture')

        exported = 0
        for level in mipmap_levels:
            level_num = level.get('level', 0)
            rgba_data = level.get('rgba_data')
            width = level.get('width', 0)
            height = level.get('height', 0)

            if rgba_data and width > 0:
                file_path = os.path.join(output_dir, f"{name}_level{level_num}.png")
                if hasattr(self.parent_workshop, '_save_texture_png'):
                    self.parent_workshop._save_texture_png(rgba_data, width, height, file_path)
                    exported += 1

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Export Complete", f"Exported {exported} mipmap levels")


class ZoomablePreview(QLabel): #vers 1
    """Custom preview widget with zoom and pan"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.original_pixmap = None
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.dragging = False
        self.drag_start = QPoint(0, 0)
        self.bg_color = QColor(42, 42, 42)  # Default dark gray

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("border: 1px solid #3a3a3a;")

        # Enable mouse tracking for pan
        self.setMouseTracking(True)


    def set_image(self, pixmap): #vers 1
        """Set image and reset view"""
        self.original_pixmap = pixmap
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()


    def update_display(self): #vers 2
        """Update displayed image with zoom and pan"""
        if not self.original_pixmap:
            self.clear()
            return

        # Calculate zoomed size
        scaled_size = self.original_pixmap.size() * self.zoom_level
        zoomed_pixmap = self.original_pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Apply pan offset
        if self.pan_offset.x() != 0 or self.pan_offset.y() != 0:
            # Create a new pixmap with offset applied
            result = QPixmap(self.size())
            result.fill(self.bg_color)

            painter = QPainter(result)
            # Center the image and apply offset
            x = (self.width() - zoomed_pixmap.width()) // 2 + self.pan_offset.x()
            y = (self.height() - zoomed_pixmap.height()) // 2 + self.pan_offset.y()
            painter.drawPixmap(x, y, zoomed_pixmap)
            painter.end()

            self.setPixmap(result)
        else:
            self.setPixmap(zoomed_pixmap)


    def zoom_in(self): #vers 1
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 10.0)  # Max 10x zoom
        self.update_display()


    def zoom_out(self): #vers 1
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)  # Min 0.1x zoom
        self.update_display()


    def reset_view(self): #vers 1
        """Reset zoom and pan"""
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()


    def fit_to_window(self): #vers 1
        """Fit image to window"""
        if not self.original_pixmap:
            return

        # Calculate zoom to fit
        img_size = self.original_pixmap.size()
        widget_size = self.size()

        zoom_w = widget_size.width() / img_size.width()
        zoom_h = widget_size.height() / img_size.height()

        self.zoom_level = min(zoom_w, zoom_h) * 0.95  # 95% to add padding
        self.pan_offset = QPoint(0, 0)
        self.update_display()


    def set_background_color(self, color): #vers 1
        """Set background color"""
        self.bg_color = color
        self.setStyleSheet(f"border: 1px solid #3a3a3a; background-color: {color.name()};")


    def mousePressEvent(self, event): #vers 1
        """Start pan drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)


    def mouseMoveEvent(self, event): #vers 1
        """Handle pan drag"""
        if self.dragging:
            delta = event.pos() - self.drag_start
            self.pan_offset += delta
            self.drag_start = event.pos()
            # Pan handled by offset, update if needed


    def mouseReleaseEvent(self, event): #vers 1
        """End pan drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def wheelEvent(self, event): #vers 1
        """Mouse wheel zoom"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()



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

if __name__ == "__main__":
    import sys
    import traceback

    print("Starting TXD Workshop...")

    try:
        app = QApplication(sys.argv)
        print("QApplication created")

        workshop = TXDWorkshop()
        print("TXDWorkshop instance created")

        workshop.setWindowTitle("TXD Workshop - Standalone")
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
