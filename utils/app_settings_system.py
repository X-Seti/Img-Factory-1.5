#!/usr/bin/env python3
# $vers" X-Seti - June26, 2025 - App Factory - Package theme settings"

"""
App Factory - App Settings System - Clean Version
Settings management without demo code
"""

#This goes in root/ app_settings_system.py - version 54

import json
import os
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime  # Fixed: Added QDateTime
from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QButtonGroup, QRadioButton, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox,
    QLabel, QPushButton, QComboBox, QCheckBox, QSpinBox,
    QSlider, QGroupBox, QTabWidget, QDialog, QMessageBox,
    QFileDialog, QColorDialog, QFontDialog, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFontComboBox,
    QScrollArea, QFrame, QLineEdit, QListWidget
)

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot, QRect, QDateTime, QByteArray
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QCursor


# Check for screen capture libraries (for robust color picking)
try:
    import mss
    MSS_AVAILABLE = True
    print("MSS library available - using high-performance screen capture")
except ImportError:
    MSS_AVAILABLE = False
    try:
        from PIL import ImageGrab
        PIL_AVAILABLE = True
        print("MSS not available, using PIL fallback")
    except ImportError:
        PIL_AVAILABLE = False
        print("Neither MSS nor PIL available - using Qt fallback")

class ThemeSaveDialog(QDialog):
    """Dialog for saving themes with complete metadata"""
def _apply_settings(self): #vers 3
    """Apply settings permanently and save to appfactory.settings.json"""
    new_settings = self._get_dialog_settings()
    old_theme = self.app_settings.current_settings["theme"]

    # Update settings
    self.app_settings.current_settings.update(new_settings)

    # Save font settings if modified
    if hasattr(self, 'font_controls'):
        self._save_font_settings()

    # Update modified colors if any
    if hasattr(self, '_modified_colors') and self._modified_colors:
        current_theme = self.app_settings.current_settings["theme"]
        if current_theme in self.app_settings.themes:
            if "colors" not in self.app_settings.themes[current_theme]:
                self.app_settings.themes[current_theme]["colors"] = {}
            self.app_settings.themes[current_theme]["colors"].update(self._modified_colors)

    # Save settings to appfactory.settings.json
    self.app_settings.save_settings()

    # Emit signals
    if new_settings["theme"] != old_theme:
        self.themeChanged.emit(new_settings["theme"])
    self.settingsChanged.emit()

    QMessageBox.information(
        self,
        "Applied",
        f"Settings saved to appfactory.settings.json\n\nActive theme: {new_settings['theme']}"
    )
    def __init__(self, app_settings, current_theme_data, parent=None): #vers 1
        super().__init__(parent)
        self.app_settings = app_settings
        self.current_theme_data = current_theme_data
        self.result_theme_data = None

        self.setWindowTitle("Save Theme - " + App_name)
        self.setMinimumSize(500, 600)
        self.setModal(True)

        self._setup_ui()
        self._detect_theme_type()

    def _setup_ui(self): #vers 1
        """Create the save dialog UI"""
        layout = QVBoxLayout(self)

        # Theme Detection Display
        self.detection_label = QLabel()
        self.detection_label.setStyleSheet("font-weight: bold; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.detection_label)

        # Instructions
        instructions = QLabel("""
        <b>Theme Naming Guidelines:</b><br>
        - Dark themes: Add "_Dark" suffix<br>
        - Light themes: Add "_Light" suffix
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 6px; border-radius: 4px; margin: 4px;")
        layout.addWidget(instructions)

        # Form Group
        form_group = QGroupBox("Theme Information")
        form_layout = QVBoxLayout(form_group)

        grid_layout = QGridLayout()

        # Theme Name
        grid_layout.addWidget(QLabel("Theme Name:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter theme name (e.g., 'Ocean_Dark')")
        self.name_input.textChanged.connect(self._validate_inputs)
        grid_layout.addWidget(self.name_input, 0, 1, 1, 2)

        # Display Name
        grid_layout.addWidget(QLabel("Display Name:"), 2, 0)
        self.display_input = QLineEdit()
        self.display_input.setPlaceholderText("Human-readable name (e.g., 'Ocean Dark Theme')")
        grid_layout.addWidget(self.display_input, 2, 1, 1, 2)

        # Description
        grid_layout.addWidget(QLabel("Description:"), 3, 0)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Brief description of your theme")
        grid_layout.addWidget(self.description_input, 3, 1, 1, 2)

        # Category
        grid_layout.addWidget(QLabel("Category:"), 4, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        categories = [
            "Professional",
            "Dark Themes",
            "Light Themes",
            "Nature",
            "Creative",
            "Gaming",
            "Business",
            "Colorful",
            "High Contrast",
            "Custom"
        ]
        self.category_combo.addItems(categories)
        grid_layout.addWidget(self.category_combo, 4, 1, 1, 2)

        # Author
        grid_layout.addWidget(QLabel("Author:"), 5, 0)
        self.author_input = QLineEdit("X-Seti")
        grid_layout.addWidget(self.author_input, 5, 1, 1, 2)

        # Version
        grid_layout.addWidget(QLabel("Version:"), 6, 0)
        self.version_input = QLineEdit("1.0")
        self.version_input.setMaximumWidth(100)
        grid_layout.addWidget(self.version_input, 6, 1)

        grid_layout.setColumnStretch(0, 0)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)

        form_layout.addLayout(grid_layout)
        layout.addWidget(form_group)

        # Color Summary
        color_group = QGroupBox("Color Summary")
        color_layout = QVBoxLayout(color_group)

        self.color_summary = QLabel()
        self.color_summary.setWordWrap(True)
        color_layout.addWidget(self.color_summary)

        layout.addWidget(color_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.auto_detect_btn = QPushButton("Auto-Detect Theme Type")
        self.auto_detect_btn.clicked.connect(self._detect_theme_type)
        button_layout.addWidget(self.auto_detect_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("Save Theme")
        self.save_btn.clicked.connect(self._save_theme)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        self._populate_current_data()
        self._update_color_summary()

    def _detect_theme_type(self): #vers 1
        """Auto-detect if theme is dark or light based on colors"""
        if not self.current_theme_data or "colors" not in self.current_theme_data:
            return

        colors = self.current_theme_data["colors"]
        bg_primary = colors.get("bg_primary", "#ffffff")

        try:
            hex_color = bg_primary.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)

                brightness = (r * 0.299 + g * 0.587 + b * 0.114)

                if brightness < 128:
                    theme_type = "Dark"
                    self.detection_label.setText("DARK THEME DETECTED")
                    self.detection_label.setStyleSheet(
                        "background: #1A1A1A; color: #FFFFFF; padding: 8px; "
                        "border-radius: 4px; font-weight: bold;"
                    )
                    self.category_combo.setCurrentText("Dark Themes")
                else:
                    theme_type = "Light"
                    self.detection_label.setText("LIGHT THEME DETECTED")
                    self.detection_label.setStyleSheet(
                        "background: #F5F5F5; color: #333333; padding: 8px; "
                        "border-radius: 4px; font-weight: bold;"
                    )
                    self.category_combo.setCurrentText("Light Themes")

                current_name = self.name_input.text()
                if current_name and not current_name.endswith(f"_{theme_type}"):
                    if not current_name.endswith("_Dark") and not current_name.endswith("_Light"):
                        self.name_input.setText(f"{current_name}_{theme_type}")

        except Exception as e:
            self.detection_label.setText("Could not detect theme type")
            print(f"Theme detection error: {e}")

    def _add_suffix(self, suffix): #vers 1
        """Add suffix to theme name"""
        current_name = self.name_input.text()
        if current_name:
            for existing_suffix in ["_Dark", "_Light"]:
                if current_name.endswith(existing_suffix):
                    current_name = current_name[:-len(existing_suffix)]
                    break
            self.name_input.setText(f"{current_name}{suffix}")

    def _populate_current_data(self): #vers 1
        """Populate form with current theme data"""
        if self.current_theme_data:
            self.display_input.setText(self.current_theme_data.get("name", ""))
            self.description_input.setText(self.current_theme_data.get("description", ""))

            category = self.current_theme_data.get("category", "Custom")
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentText(category)

            self.author_input.setText(self.current_theme_data.get("author", "X-Seti"))
            self.version_input.setText(self.current_theme_data.get("version", "1.0"))

    def _update_color_summary(self): #vers 1
        """Update color summary display"""
        if not self.current_theme_data or "colors" not in self.current_theme_data:
            return

        colors = self.current_theme_data["colors"]

        summary_html = f"""
        <b>Primary Colors:</b><br>
        - Background: <span style='background-color: {colors.get('bg_primary', '#fff')};
          padding: 2px 8px; border: 1px solid #ccc;'>{colors.get('bg_primary', '#fff')}</span><br>
        - Accent: <span style='background-color: {colors.get('accent_primary', '#000')};
          color: white; padding: 2px 8px;'>{colors.get('accent_primary', '#000')}</span><br>
        - Text: <span style='background-color: {colors.get('text_primary', '#000')};
          color: white; padding: 2px 8px;'>{colors.get('text_primary', '#000')}</span><br>
        <br>
        <b>Total Colors:</b> {len(colors)} defined
        """

        self.color_summary.setText(summary_html)

    def _validate_inputs(self): #vers 1
        """Validate form inputs"""
        name = self.name_input.text().strip()

        valid = bool(name and len(name) >= 3)

        if valid:
            import re
            valid = bool(re.match(r'^[a-zA-Z0-9_\-\s]+$', name))

        self.save_btn.setEnabled(valid)

        if valid:
            self.save_btn.setText("Save Theme")
            self.save_btn.setStyleSheet("")
        else:
            self.save_btn.setText("Invalid Name")
            self.save_btn.setStyleSheet("background-color: #ffcccb;")

    def _save_theme(self): #vers 1
        """Save the theme with all metadata"""
        theme_name = self.name_input.text().strip()

        self.result_theme_data = {
            "name": self.display_input.text().strip() or theme_name,
            "description": self.description_input.text().strip() or f"Custom theme: {theme_name}",
            "category": self.category_combo.currentText(),
            "author": self.author_input.text().strip() or "X-Seti",
            "version": self.version_input.text().strip() or "1.0",
            "colors": self.current_theme_data.get("colors", {})
        }

        from datetime import datetime
        self.result_theme_data["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        success = self.app_settings.save_theme(theme_name, self.result_theme_data)

        if success:
            QMessageBox.information(
                self, "Theme Saved",
                f"Theme '{theme_name}' saved successfully!\n\n"
                f"Display Name: {self.result_theme_data['name']}\n"
                f"Category: {self.result_theme_data['category']}\n"
                f"Colors: {len(self.result_theme_data['colors'])} defined"
            )
            self.accept()
        else:
            QMessageBox.warning(
                self, "Save Failed",
                f"Failed to save theme '{theme_name}'.\n"
                "Please check file permissions and try again."
            )

    def get_theme_data(self): #vers 1
        """Get the final theme data after dialog closes"""
        return self.result_theme_data


class CustomWindow(QMainWindow): #vers 1
    """Base window class with custom gadgets and corner resize support"""

    def __init__(self, app_name="Application", parent=None): #vers 2
        """Initialize custom window"""
        super().__init__(parent)

        self.app_name = app_name
        self.setWindowTitle(app_name)
        self.setMinimumSize(800, 600)

        # Load app settings
        self.app_settings = AppSettings()

        # Initialize icon provider WITH app_settings
        self.icons = IconProvider(self, self.app_settings)

        # Setup resize handling
        self.resize_margin = 10
        self.resize_direction = None
        self.drag_position = None
        self.initial_geometry = None
        self.setMouseTracking(True)

        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Apply custom gadgets setting
        self._apply_window_mode()

        # Apply theme
        self._apply_theme()


    def _apply_theme(self): #vers 2
        """Apply current theme"""
        stylesheet = self.app_settings.get_stylesheet()
        self.setStyleSheet(stylesheet)

        # Update titlebar icons to match new theme
        self._update_titlebar_icons()


    def _apply_window_mode(self): #vers 1
        """Apply custom window gadgets or system mode"""
        use_custom = self.app_settings.current_settings.get("use_custom_gadgets", False)

        if use_custom:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            if not hasattr(self, 'custom_titlebar'):
                self._create_custom_titlebar()
            else:
                self.custom_titlebar.setVisible(True)
        else:
            self.setWindowFlags(Qt.WindowType.Window)
            if hasattr(self, 'custom_titlebar'):
                self.custom_titlebar.setVisible(False)

        self.show()


    def _create_custom_titlebar(self): #vers 5
        """Create custom title bar with window controls - Simple text-based"""
        self.custom_titlebar = QWidget()
        self.custom_titlebar.setObjectName("customTitleBar")
        self.custom_titlebar.setFixedHeight(40)

        titlebar_layout = QHBoxLayout(self.custom_titlebar)
        titlebar_layout.setContentsMargins(4, 4, 4, 4)
        titlebar_layout.setSpacing(4)

        # Settings button on the left
        settings_btn = QPushButton("Settings")
        settings_btn.setFixedSize(100, 32)
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setToolTip("Settings")
        titlebar_layout.addWidget(settings_btn)

        # App title in center
        titlebar_layout.addStretch()
        title_label = QLabel(self.app_name)
        title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titlebar_layout.addWidget(title_label)
        titlebar_layout.addStretch()

        # Window control buttons - Simple text
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.setStyleSheet("font-size: 16pt; font-weight: bold;")
        minimize_btn.clicked.connect(self.showMinimized)
        minimize_btn.setToolTip("Minimize")
        titlebar_layout.addWidget(minimize_btn)

        maximize_btn = QPushButton("□")
        maximize_btn.setFixedSize(32, 32)
        maximize_btn.setStyleSheet("font-size: 16pt; font-weight: bold;")
        maximize_btn.clicked.connect(self._toggle_maximize)
        maximize_btn.setToolTip("Maximize")
        self.maximize_btn = maximize_btn
        titlebar_layout.addWidget(maximize_btn)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("font-size: 20pt; font-weight: bold;")
        close_btn.clicked.connect(self.close)
        close_btn.setToolTip("Close")
        titlebar_layout.addWidget(close_btn)

        # Add to top of main layout
        self.main_layout.insertWidget(0, self.custom_titlebar)

        # Enable dragging
        self.titlebar_drag_position = None
        self.custom_titlebar.mousePressEvent = self._titlebar_mouse_press
        self.custom_titlebar.mouseMoveEvent = self._titlebar_mouse_move
        self.custom_titlebar.mouseDoubleClickEvent = self._titlebar_double_click


    def _titlebar_mouse_press(self, event): #vers 1
        """Handle mouse press on title bar"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.titlebar_drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def _titlebar_mouse_move(self, event): #vers 1
        """Handle mouse move on title bar - window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.titlebar_drag_position:
            self.move(event.globalPosition().toPoint() - self.titlebar_drag_position)
            event.accept()

    def _titlebar_double_click(self, event): #vers 1
        """Handle double click on title bar - maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()
            event.accept()

    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
            if hasattr(self, 'maximize_btn'):
                self.maximize_btn.setIcon(self.icons.maximize_icon())
                self.maximize_btn.setToolTip("Maximize")
        else:
            self.showMaximized()
            if hasattr(self, 'maximize_btn'):
                self.maximize_btn.setIcon(self.icons.restore_icon())
                self.maximize_btn.setToolTip("Restore")

    def paintEvent(self, event): #vers 1   ➕ Added built-in fallback: Default Green
        """Paint corner resize handles"""
        super().paintEvent(event)

        if not self.app_settings.current_settings.get("enable_corner_resize", True):
            return

        from PyQt6.QtGui import QPainter, QPen, QColor

        painter = QPainter(self)
        pen = QPen(QColor(self.app_settings.get_theme_colors().get('border', '#cccccc')))
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw corner resize indicators
        corner_size = 15

        # Top-left corner
        painter.drawLine(0, corner_size, corner_size, 0)

        # Top-right corner
        painter.drawLine(self.width() - corner_size, 0, self.width(), corner_size)

        # Bottom-left corner
        painter.drawLine(0, self.height() - corner_size, corner_size, self.height())

        # Bottom-right corner
        painter.drawLine(self.width() - corner_size, self.height(),
                        self.width(), self.height() - corner_size)


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


    def _handle_corner_resize(self, global_pos): #vers 1
        """Handle window resizing from any edge or corner"""
        if not self.resize_direction or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        new_geometry = QRect(geometry)

        if "left" in self.resize_direction:
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            if new_width >= min_width:
                new_geometry.setLeft(new_x)

        if "right" in self.resize_direction:
            new_width = geometry.width() + delta.x()
            if new_width >= min_width:
                new_geometry.setWidth(new_width)

        if "top" in self.resize_direction:
            new_y = geometry.y() + delta.y()
            new_height = geometry.height() - delta.y()
            if new_height >= min_height:
                new_geometry.setTop(new_y)

        if "bottom" in self.resize_direction:
            new_height = geometry.height() + delta.y()
            if new_height >= min_height:
                new_geometry.setHeight(new_height)

        self.setGeometry(new_geometry)

    # ===== SETTINGS DIALOG =====

    def open_settings(self): #vers 1
        """Open settings dialog"""
        dialog = SettingsDialog(self.app_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_theme()
            self._apply_window_mode()


class ColorPickerWidget(QWidget):
    """SAFE, simple color picker widget - NO THREADING"""
    colorPicked = pyqtSignal(str)

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setFixedSize(280, 35)
        self.current_color = "#ffffff"
        self.picking_active = False
        self.color_display = None
        self.color_value = None
        self.pick_button = None
        self._setup_ui()

    def _setup_ui(self): #vers 1
        """Setup UI - main horizontal layout"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(2, 2, 2, 2)

        # Color display square
        self.color_display = QLabel()
        self.color_display.setFixedSize(50, 30)
        self.color_display.setStyleSheet("border: 1px solid #999; border-radius: 3px; background-color: #ffffff;")
        main_layout.addWidget(self.color_display)

        # Hex value display
        self.color_value = QLabel("#FFFFFF")
        self.color_value.setFixedWidth(100)
        self.color_value.setFixedHeight(30)
        self.color_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_value.setStyleSheet("""
            font-family: monospace;
            font-size: 20px;
            font-weight: bold;
            color: #000000;
            background-color: #f0f0f0;
            border: 1px solid #999;
            border-radius: 3px;
            padding: 2px;
        """)
        main_layout.addWidget(self.color_value)

        # Pick button
        self.pick_button = QPushButton("Pick")
        self.pick_button.setFixedSize(70, 30)
        self.pick_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(self.pick_button)

        # Initialize display
        self.update_color_display("#ffffff")

    def open_color_dialog(self): #vers 1
        """Open simple Qt color dialog - SAFE"""
        try:
            color = QColorDialog.getColor(QColor(self.current_color), self)
            if color.isValid():
                hex_color = color.name()
                self.current_color = hex_color
                self.update_color_display(hex_color)
                self.colorPicked.emit(hex_color)
                print(f"Color selected: {hex_color}")
        except Exception as e:
            print(f"Color dialog error: {e}")

    def update_color_display(self, hex_color): #vers 1
        """Update the color display safely"""
        try:
            if not hex_color or not isinstance(hex_color, str):
                hex_color = "#ffffff"

            # Ensure valid hex format
            if not hex_color.startswith('#'):
                hex_color = '#' + hex_color
            if len(hex_color) != 7:
                hex_color = "#ffffff"

            self.current_color = hex_color

            # Update color display
            if self.color_display:
                self.color_display.setStyleSheet(
                    f"background-color: {hex_color}; border: 1px solid #999; border-radius: 3px;"
                )

            # Update color value
            if self.color_value:
                self.color_value.setText(hex_color.upper())

        except Exception as e:
            print(f"Display update error: {e}")

    def closeEvent(self, event): #vers 1
        """Clean up when widget is closed"""
        super().closeEvent(event)

    def __del__(self): #vers 1
        """Clean up when object is destroyed"""
        pass


class ScreenCaptureThread(QThread):
    """Background thread for screen capture to avoid blocking UI"""
    colorCaptured = pyqtSignal(str)  # hex color

    def __init__(self, x, y, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.running = True

    def run(self):
        """Capture color at coordinates in background thread"""
        try:
            if MSS_AVAILABLE:
                color = self._capture_with_mss()
            elif PIL_AVAILABLE:
                color = self._capture_with_pil()
            else:
                color = self._capture_with_qt()

            if color and self.running:
                self.colorCaptured.emit(color)
        except Exception as e:
            print(f"Screen capture error: {e}")
            if self.running:
                self.colorCaptured.emit("#ffffff")  # Fallback color

    def _capture_with_mss(self):
        """High-performance capture using MSS library"""
        try:
            with mss.mss() as sct:
                # Capture 1x1 pixel area for maximum efficiency
                monitor = {"top": self.y, "left": self.x, "width": 1, "height": 1}
                screenshot = sct.grab(monitor)

                # MSS returns BGRA, we need RGB
                if len(screenshot.rgb) >= 3:
                    # screenshot.pixel(0, 0) returns (R, G, B) tuple
                    pixel = screenshot.pixel(0, 0)
                    return f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"

        except Exception as e:
            print(f"MSS capture error: {e}")
        return None

    def _capture_with_pil(self):
        """Fallback capture using PIL/Pillow"""
        try:
            # Capture small area around point for efficiency
            bbox = (self.x, self.y, self.x + 1, self.y + 1)
            screenshot = ImageGrab.grab(bbox)
            pixel = screenshot.getpixel((0, 0))

            # Handle both RGB and RGBA
            if isinstance(pixel, tuple) and len(pixel) >= 3:
                return f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"

        except Exception as e:
            print(f"PIL capture error: {e}")
        return None

    def _capture_with_qt(self):
        """Last resort: Qt screen capture"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                pixmap = screen.grabWindow(0, self.x, self.y, 1, 1)
                if not pixmap.isNull():
                    image = pixmap.toImage()
                    if not image.isNull():
                        color = QColor(image.pixel(0, 0))
                        return color.name()
        except Exception as e:
            print(f"Qt capture error: {e}")
        return None

    def stop(self):
        """Stop the capture thread"""
        self.running = False

class XPColorPicker(QWidget): #vers 2
    """XP Display Properties style color picker"""

    colorChanged = pyqtSignal(str, str)  # element_name, hex_color

    def __init__(self, theme_colors, parent=None): #vers 1
        super().__init__(parent)
        self.theme_colors = theme_colors
        self.current_hue = 240
        self.current_sat = 100
        self.current_bri = 25

        # UI element colors mapping
        self.element_colors = {
            'bg_primary': {'name': 'Window Background', 'h': 0, 's': 0, 'b': 100},
            'bg_secondary': {'name': 'Panel Background', 'h': 210, 's': 15, 'b': 98},
            'bg_tertiary': {'name': 'Alternate Background', 'h': 210, 's': 15, 'b': 92},
            'panel_bg': {'name': 'GroupBox Background', 'h': 210, 's': 8, 'b': 95},
            'accent_primary': {'name': 'Primary Accent', 'h': 210, 's': 85, 'b': 53},
            'accent_secondary': {'name': 'Secondary Accent', 'h': 210, 's': 85, 'b': 47},
            'text_primary': {'name': 'Primary Text', 'h': 0, 's': 0, 'b': 13},
            'text_secondary': {'name': 'Secondary Text', 'h': 210, 's': 15, 'b': 35},
            'text_accent': {'name': 'Accent Text', 'h': 210, 's': 85, 'b': 53},
            'button_normal': {'name': 'Button Face', 'h': 210, 's': 40, 'b': 95},
            'button_hover': {'name': 'Button Hover', 'h': 210, 's': 50, 'b': 85},
            'button_pressed': {'name': 'Button Pressed', 'h': 210, 's': 60, 'b': 75},
            'border': {'name': 'Border Color', 'h': 210, 's': 15, 'b': 85},
            'success': {'name': 'Success Color', 'h': 120, 's': 60, 'b': 50},
            'warning': {'name': 'Warning Color', 'h': 35, 's': 100, 'b': 60},
            'error': {'name': 'Error Color', 'h': 4, 's': 90, 'b': 58}
        }

        self._load_theme_colors()
        self._init_ui()

    def _init_ui(self): #vers 2
        """Initialize the XP style UI - FIXED: Removed duplicate global sliders"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Left side - Element list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Element selection
        element_label = QLabel("Select Element:")
        element_label.setFont(QFont("MS Sans Serif", 8, QFont.Weight.Bold))
        left_layout.addWidget(element_label)

        self.element_list = QListWidget()
        self.element_list.setMaximumWidth(160)
        self.element_list.setMaximumHeight(120)
        self.element_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 2px inset #f0f0f0;
                font-family: 'MS Sans Serif';
                font-size: 8pt;
            }
            QListWidget::item {
                padding: 2px 4px;
            }
            QListWidget::item:selected {
                background: #0a246a;
                color: white;
            }
        """)

        for key, data in self.element_colors.items():
            self.element_list.addItem(data['name'])

        self.element_list.setCurrentRow(0)
        self.element_list.currentRowChanged.connect(self._on_element_selected)
        left_layout.addWidget(self.element_list)

        main_layout.addWidget(left_widget)

        # Right side - Color controls
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Color preview
        color_label = QLabel("Color:")
        color_label.setFont(QFont("MS Sans Serif", 8, QFont.Weight.Bold))
        right_layout.addWidget(color_label)

        self.color_preview = QWidget()
        self.color_preview.setFixedSize(60, 30)
        self.color_preview.setStyleSheet("""
            QWidget {
                background: #0a246a;
                border: 2px inset #f0f0f0;
            }
        """)
        right_layout.addWidget(self.color_preview)

        # HSL Sliders - FOR INDIVIDUAL ELEMENT EDITING ONLY
        sliders_frame = QFrame()
        sliders_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        sliders_layout = QVBoxLayout(sliders_frame)
        sliders_layout.setSpacing(3)

        # Hue Slider
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(QLabel("Hue:"))
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(360)
        self.hue_slider.setValue(240)
        self.hue_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hue_slider.setTickInterval(30)
        hue_layout.addWidget(self.hue_slider)
        self.hue_value = QLabel("240")
        self.hue_value.setFixedWidth(40)
        self.hue_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hue_layout.addWidget(self.hue_value)
        sliders_layout.addLayout(hue_layout)

        # Saturation Slider
        sat_layout = QHBoxLayout()
        sat_layout.addWidget(QLabel("Sat:"))
        self.sat_slider = QSlider(Qt.Orientation.Horizontal)
        self.sat_slider.setMinimum(0)
        self.sat_slider.setMaximum(100)
        self.sat_slider.setValue(100)
        self.sat_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sat_slider.setTickInterval(10)
        sat_layout.addWidget(self.sat_slider)
        self.sat_value = QLabel("100")
        self.sat_value.setFixedWidth(40)
        self.sat_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sat_layout.addWidget(self.sat_value)
        sliders_layout.addLayout(sat_layout)

        # Brightness Slider
        bri_layout = QHBoxLayout()
        bri_layout.addWidget(QLabel("Bri:"))
        self.bri_slider = QSlider(Qt.Orientation.Horizontal)
        self.bri_slider.setMinimum(0)
        self.bri_slider.setMaximum(100)
        self.bri_slider.setValue(25)
        self.bri_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.bri_slider.setTickInterval(10)
        bri_layout.addWidget(self.bri_slider)
        self.bri_value = QLabel("25")
        self.bri_value.setFixedWidth(40)
        self.bri_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bri_layout.addWidget(self.bri_value)
        sliders_layout.addLayout(bri_layout)

        right_layout.addWidget(sliders_frame)

        # Connect sliders
        self.hue_slider.valueChanged.connect(self._on_hue_changed)
        self.sat_slider.valueChanged.connect(self._on_sat_changed)
        self.bri_slider.valueChanged.connect(self._on_bri_changed)

        right_layout.addStretch()
        main_layout.addWidget(right_widget)

    def _load_theme_colors(self): #vers 1
        """Load colors from current theme"""
        for element_key in self.element_colors.keys():
            if element_key in self.theme_colors:
                hex_color = self.theme_colors[element_key]
                h, s, l = rgb_to_hsl(hex_color)
                self.element_colors[element_key].update({'h': h, 's': s, 'b': l})

    def _on_element_selected(self, row): #vers 1
        """Handle element selection"""
        if row >= 0:
            element_keys = list(self.element_colors.keys())
            if row < len(element_keys):
                element_key = element_keys[row]
                color_data = self.element_colors[element_key]

                self.current_hue = color_data['h']
                self.current_sat = color_data['s']
                self.current_bri = color_data['b']

                self._update_sliders()
                self._update_color_preview()

    def _update_sliders(self): #vers 1
        """Update slider positions and values"""
        self.hue_slider.blockSignals(True)
        self.sat_slider.blockSignals(True)
        self.bri_slider.blockSignals(True)

        self.hue_slider.setValue(self.current_hue)
        self.sat_slider.setValue(self.current_sat)
        self.bri_slider.setValue(self.current_bri)

        self.hue_value.setText(str(self.current_hue))
        self.sat_value.setText(str(self.current_sat))
        self.bri_value.setText(str(self.current_bri))

        self.hue_slider.blockSignals(False)
        self.sat_slider.blockSignals(False)
        self.bri_slider.blockSignals(False)

    def _update_color_preview(self): #vers 1
        """Update the color preview widget"""
        hex_color = hsl_to_rgb(self.current_hue, self.current_sat, self.current_bri)
        self.color_preview.setStyleSheet(f"""
            QWidget {{
                background: {hex_color};
                border: 2px inset #f0f0f0;
            }}
        """)

        # Emit color change signal
        element_keys = list(self.element_colors.keys())
        current_row = self.element_list.currentRow()
        if current_row >= 0 and current_row < len(element_keys):
            element_key = element_keys[current_row]
            self.colorChanged.emit(element_key, hex_color)

    def _on_hue_changed(self, value): #vers 1
        """Handle hue slider change"""
        self.current_hue = value
        self.hue_value.setText(str(value))
        self._save_current_color()
        self._update_color_preview()

    def _on_sat_changed(self, value): #vers 1
        """Handle saturation slider change"""
        self.current_sat = value
        self.sat_value.setText(str(value))
        self._save_current_color()
        self._update_color_preview()

    def _on_bri_changed(self, value): #vers 1
        """Handle brightness slider change"""
        self.current_bri = value
        self.bri_value.setText(str(value))
        self._save_current_color()
        self._update_color_preview()

    def _save_current_color(self): #vers 1
        """Save current color to selected element"""
        element_keys = list(self.element_colors.keys())
        current_row = self.element_list.currentRow()
        if current_row >= 0 and current_row < len(element_keys):
            element_key = element_keys[current_row]
            self.element_colors[element_key].update({
                'h': self.current_hue,
                's': self.current_sat,
                'b': self.current_bri
            })

    def update_color_display(self, hex_color): #vers 1
        """Update display with picked color"""
        try:
            h, s, l = rgb_to_hsl(hex_color)
            self.current_hue = h
            self.current_sat = s
            self.current_bri = l
            self._update_sliders()
            self._update_color_preview()
            self._save_current_color()
        except Exception as e:
            print(f"Error updating color display: {e}")

    def get_all_colors(self): #vers 1
        """Get all colors as hex values"""
        colors = {}
        for element_key, data in self.element_colors.items():
            colors[element_key] = hsl_to_rgb(data['h'], data['s'], data['b'])
        return colors

class ThemeColorEditor(QWidget): #vers 4
    """Widget for editing individual theme colors with lock protection - FIXED Pick button"""
    colorChanged = pyqtSignal(str, str)  # color_key, hex_color
    lockChanged = pyqtSignal(str, bool)  # color_key, is_locked

    def __init__(self, color_key, color_name, current_value, parent=None): #vers 3
        super().__init__(parent)
        self.color_key = color_key
        self.color_name = color_name
        self.current_value = current_value
        self.is_locked = False
        self._setup_ui()

    def _setup_ui(self): #vers 4
        """Setup the editor UI with lock checkbox - FIXED: Wider Pick button"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Lock checkbox
        self.lock_check = QCheckBox()
        self.lock_check.setFixedWidth(30)
        self.lock_check.setToolTip("Lock to prevent global adjustments")
        self.lock_check.stateChanged.connect(self._on_lock_changed)
        layout.addWidget(self.lock_check)

        # Color name label - FIXED WIDTH for alignment
        name_label = QLabel(self.color_name)
        name_label.setMinimumWidth(150)
        name_label.setMaximumWidth(150)
        layout.addWidget(name_label)

        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 30)
        self.update_preview(self.current_value)
        layout.addWidget(self.color_preview)

        # Color value input - FIXED WIDTH for column alignment
        self.color_input = QLineEdit(self.current_value)
        self.color_input.setMinimumWidth(85)
        self.color_input.setMaximumWidth(85)
        self.color_input.setFont(QFont("monospace", 9))
        self.color_input.textChanged.connect(self.on_color_changed)
        layout.addWidget(self.color_input)

        # Color dialog button - FIXED: Wider for better visibility
        dialog_btn = QPushButton("Pick")
        dialog_btn.setMinimumWidth(80)  # CHANGED from setFixedSize(50, 25)
        dialog_btn.setFixedHeight(30)
        dialog_btn.setToolTip("Open color picker dialog")
        dialog_btn.clicked.connect(self.open_color_dialog)
        layout.addWidget(dialog_btn)

        layout.addStretch()

    def _on_lock_changed(self, state): #vers 1
        """Handle lock state change"""
        self.is_locked = (state == Qt.CheckState.Checked.value)
        self.lockChanged.emit(self.color_key, self.is_locked)

        # Visual feedback - dim when locked
        if self.is_locked:
            self.color_input.setStyleSheet("background-color: #f0f0f0; color: #666;")
            self.lock_check.setToolTip("Locked - Click to unlock")
        else:
            self.color_input.setStyleSheet("")
            self.lock_check.setToolTip("Unlocked - Click to lock")

    def on_color_changed(self, text): #vers 1
        """Handle color input text change"""
        if text.startswith('#') and len(text) == 7:
            self.current_value = text
            self.update_preview(text)
            self.colorChanged.emit(self.color_key, text)

    def open_color_dialog(self): #vers 1
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(self.current_value), self)
        if color.isValid():
            hex_color = color.name()
            self.color_input.setText(hex_color)

    def update_color(self, hex_color): #vers 2
        """Update color from external source - respects lock"""
        # Only update if not locked
        if not self.is_locked:
            self.color_input.setText(hex_color)
            self.current_value = hex_color
            self.update_preview(hex_color)

    def set_locked(self, locked): #vers 1
        """Programmatically set lock state"""
        self.lock_check.setChecked(locked)

    def update_preview(self, hex_color): #vers 1
        """Update the color preview"""
        self.color_preview.setStyleSheet(
            f"background-color: {hex_color}; border: 1px solid #999;"
        )

    def set_color(self, hex_color): #vers 1
        """Set color from external source (like color picker)"""
        self.color_input.setText(hex_color)
        self.current_value = hex_color
        self.update_preview(hex_color)
        self.colorChanged.emit(self.color_key, hex_color)


class DebugActionsHelper: #vers 1
    """Helper class for debug tab actions in SettingsDialog"""

    def __init__(self, settings_dialog): #vers 1
        """Initialize with reference to settings dialog"""
        self.dialog = settings_dialog
        self.main_window = settings_dialog.parent()

    def test_debug_output(self): #vers 1
        """Test debug output - sends test messages to activity log"""
        if hasattr(self.main_window, 'log_message'):
            # Send test messages
            self.main_window.log_message("Debug test message - debug system working!")
            self.main_window.log_message(
                f"[DEBUG-TEST] Debug enabled: {self.dialog.debug_enabled_check.isChecked()}"
            )
            self.main_window.log_message(
                f"[DEBUG-TEST] Debug level: {self.dialog.debug_level_combo.currentText()}"
            )

            # Get enabled categories
            enabled_categories = [
                cat for cat, cb in self.dialog.debug_categories.items()
                if cb.isChecked()
            ]
            self.main_window.log_message(
                f"[DEBUG-TEST] Active categories: {', '.join(enabled_categories)}"
            )

            # Test each category
            for category in enabled_categories:
                self.main_window.log_message(f"[DEBUG-TEST] Testing {category} category")

        else:
            QMessageBox.information(
                self.dialog,
                "Debug Test",
                "Debug test completed!\nCheck the activity log for output."
            )

    def debug_current_img(self): #vers 1
        """Debug current IMG file - analyzes loaded IMG and table state"""
        if not hasattr(self.main_window, 'current_img'):
            self._show_no_img_message()
            return

        if not self.main_window.current_img:
            self._show_no_img_message()
            return

        img = self.main_window.current_img

        # Basic IMG info
        self.main_window.log_message(f"[DEBUG-IMG] Current IMG: {img.file_path}")
        self.main_window.log_message(f"[DEBUG-IMG] Entries: {len(img.entries)}")

        # File type analysis
        file_types = {}
        all_extensions = set()

        for entry in img.entries:
            ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
            file_types[ext] = file_types.get(ext, 0) + 1
            all_extensions.add(ext)

        self.main_window.log_message(f"[DEBUG-IMG] File types found:")
        for ext, count in sorted(file_types.items()):
            self.main_window.log_message(f"[DEBUG-IMG]   {ext}: {count} files")

        self.main_window.log_message(
            f"[DEBUG-IMG] Unique extensions: {sorted(all_extensions)}"
        )

        # Table state analysis
        self._debug_table_state()

        # Memory info
        total_size = sum(entry.size for entry in img.entries)
        self.main_window.log_message(
            f"[DEBUG-IMG] Total size: {self._format_size(total_size)}"
        )

    def _debug_table_state(self): #vers 1
        """Debug table widget state"""
        if not hasattr(self.main_window, 'gui_layout'):
            return

        if not hasattr(self.main_window.gui_layout, 'table'):
            return

        table = self.main_window.gui_layout.table
        table_rows = table.rowCount()

        # Count hidden rows
        hidden_rows = sum(1 for row in range(table_rows) if table.isRowHidden(row))
        visible_rows = table_rows - hidden_rows

        self.main_window.log_message(f"[DEBUG-IMG] Table Analysis:")
        self.main_window.log_message(f"[DEBUG-IMG]   Total rows: {table_rows}")
        self.main_window.log_message(f"[DEBUG-IMG]   Visible rows: {visible_rows}")
        self.main_window.log_message(f"[DEBUG-IMG]   Hidden rows: {hidden_rows}")

        # Selection info
        selected_rows = table.selectedItems()
        selected_count = len(set(item.row() for item in selected_rows))
        self.main_window.log_message(f"[DEBUG-IMG]   Selected rows: {selected_count}")

        # Column info
        column_count = table.columnCount()
        self.main_window.log_message(f"[DEBUG-IMG]   Columns: {column_count}")

        # Header info
        headers = [table.horizontalHeaderItem(i).text() for i in range(column_count)]
        self.main_window.log_message(f"[DEBUG-IMG]   Headers: {', '.join(headers)}")

    def clear_debug_log(self): #vers 1
        """Clear the activity log"""
        if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'log'):
            self.main_window.gui_layout.log.clear()
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Debug log cleared")
        else:
            QMessageBox.information(
                self.dialog,
                "Clear Log",
                "Activity log cleared (if available)."
            )

    # Helper methods

    def _show_no_img_message(self): #vers 1
        """Show no IMG loaded message"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("[DEBUG-IMG] No IMG file currently loaded")
        else:
            QMessageBox.information(
                self.dialog,
                "Debug IMG",
                "No IMG file loaded."
            )

    def _format_size(self, size_bytes): #vers 1
        """Format byte size to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


# Integration function for SettingsDialog
def integrate_debug_actions(settings_dialog): #vers 1
    """Integrate debug actions helper into SettingsDialog"""
    helper = DebugActionsHelper(settings_dialog)

    # Add helper methods to dialog
    settings_dialog._test_debug_output = helper.test_debug_output
    settings_dialog._debug_current_img = helper.debug_current_img
    settings_dialog._clear_debug_log = helper.clear_debug_log

    return helper

class DebugSettings:
    """Debug mode settings and utilities"""

    def __init__(self, app_settings):
        self.app_settings = app_settings
        self.debug_enabled = app_settings.current_settings.get('debug_mode', False)
        self.debug_level = app_settings.current_settings.get('debug_level', 'INFO')
        self.debug_categories = app_settings.current_settings.get('debug_categories', [
            'IMG_LOADING', 'TABLE_POPULATION', 'BUTTON_ACTIONS', 'FILE_OPERATIONS'
        ])

    def is_debug_enabled(self, category='GENERAL'):
        """Check if debug is enabled for specific category"""
        return self.debug_enabled and category in self.debug_categories

    def debug_log(self, message, category='GENERAL', level='INFO'):
        """Log debug message if debug mode is enabled"""
        if self.is_debug_enabled(category):
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
            debug_msg = f"[DEBUG-{category}] [{timestamp}] {message}"

            # Send to main window log if available
            if hasattr(self.app_settings, 'main_window') and hasattr(self.app_settings.main_window, 'log_message'):
                self.app_settings.main_window.log_message(debug_msg)
            else:
                print(debug_msg)

    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_enabled = not self.debug_enabled
        self.app_settings.current_settings['debug_mode'] = self.debug_enabled
        self.app_settings.save_settings()
        return self.debug_enabled

class AppSettings:
    def __init__(self, settings_file="appfactory.settings.json"): #vers 3
        """Initialize application settings with Windows compatibility"""
        current_file_dir = Path(__file__).parent

        # FIXED: Set paths based on where we are - Windows compatible
        if current_file_dir.name == "utils":
            self.themes_dir = current_file_dir.parent / "themes"
            self.settings_file = current_file_dir.parent / settings_file
        else:
            self.themes_dir = current_file_dir / "themes"
            self.settings_file = current_file_dir / settings_file

        # FIXED: Windows-compatible default paths using Path objects
        if os.name == 'nt':  # Windows
            user_home = Path.home()
            desktop = user_home / "Desktop"
            steam_paths = [
                Path("C:/Program Files (x86)/Steam/steamapps/common/"),
                Path("C:/Program Files/Steam/steamapps/common/"),
                user_home / ".steam/steam/steamapps/common/"
            ]
            working_gta = next((str(p) for p in steam_paths if p.exists()), str(desktop / "GTA_VC"))
        else:  # Linux/Mac
            user_home = Path.home()
            desktop = user_home / "Desktop"
            working_gta = str(user_home / ".steam/steam/steamapps/common/")

        # Initialize default settings with Windows-safe paths
        self.default_settings = {
            'debug_mode': False,
            'debug_level': 'INFO',
            'current_theme': 'App_Factory',
            'theme': 'App_Factory',
            "button_display_mode": "both",  # "both", "icons", "text"
            "use_custom_gadgets": False,
            "enable_corner_resize": True,
            "use_svg_icons": True,
            "font_family": "Arial",
            "font_size": 9,
            "show_tooltips": True,
            "show_menu_icons": True,
            "auto_save": True,
            "panel_opacity": 95,
            'debug_categories': ['IMG_LOADING', 'TABLE_POPULATION', 'BUTTON_ACTIONS', 'FILE_OPERATIONS'],
            'working_gta_folder': working_gta,
            'assists_folder': str(desktop / "Assists"),
            'textures_folder': str(desktop / "Textures"),
            'collisions_folder': str(desktop / "Collisions"),
            'generics_folder': str(desktop / "Generics"),
            'water_folder': str(desktop / "Water"),
            'radar_folder': str(desktop / "Radartiles"),
            'gameart_folder': str(desktop / "Gameart"),
            'peds_folder': str(desktop / "Peds"),
            'vehicles_folder': str(desktop / "Vehicles"),
            'weapons_folder': str(desktop / "Weapons"),
            'font_family': 'Segoe UI' if os.name == 'nt' else 'Sans Serif',
            'font_size': 9,
            'show_tooltips': True,
            'show_menu_icons': True,
            'show_button_icons': True,
            'panel_opacity': 95,
            'remember_img_output_path': True,
            'remember_import_path': True,
            'remember_export_path': True,
            'last_img_output_path': '',
            'last_import_path': '',
            'last_export_path': ''
        }

        print(f"Looking for themes in: {self.themes_dir}")
        print(f"Themes directory exists: {self.themes_dir.exists()}")
        if self.themes_dir.exists():
            theme_files = list(self.themes_dir.glob("*.json"))
            print(f"Found {len(theme_files)} theme files")

        self.themes = self._load_all_themes()
        self.current_settings = self._load_settings()

        # GTA Project Directories
        self.working_gta_folder = self.current_settings.get('working_gta_folder', self.default_settings['working_gta_folder'])
        self.assists_folder = self.current_settings.get('assists_folder', self.default_settings['assists_folder'])
        self.textures_folder = self.current_settings.get('textures_folder', self.default_settings['textures_folder'])
        self.collisions_folder = self.current_settings.get('collisions_folder', self.default_settings['collisions_folder'])
        self.generics_folder = self.current_settings.get('generics_folder', self.default_settings['generics_folder'])
        self.water_folder = self.current_settings.get('water_folder', self.default_settings['water_folder'])
        self.radar_folder = self.current_settings.get('radar_folder', self.default_settings['radar_folder'])
        self.gameart_folder = self.current_settings.get('gameart_folder', self.default_settings['gameart_folder'])
        self.peds_folder = self.current_settings.get('peds_folder', self.default_settings['peds_folder'])
        self.vehicles_folder = self.current_settings.get('vehicles_folder', self.default_settings['vehicles_folder'])
        self.weapons_folder = self.current_settings.get('weapons_folder', self.default_settings['weapons_folder'])



    # For creating directories if they don't exist
    def ensure_directories_exist(self):
        """Create all project directories if they don't exist"""
        directories = [
            self.working_gta_folder,
            self.assists_folder,
            self.textures_folder,
            self.collisions_folder,
            self.generics_folder,
            self.water_folder,
            self.radar_folder,
            self.gameart_folder,
            self.peds_folder,
            self.vehicles_folder,
            self.weapons_folder
        ]

        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"Directory ready: {directory}")
            except Exception as e:
                print(f"Could not create directory {directory}: {e}")

    def get(self, key, default=None):
        """Get setting value for core functions compatibility"""
        # Map old 'project_folder' to assists_folder for compatibility
        if key == 'project_folder':
            return getattr(self, 'assists_folder', default)
        return getattr(self, key, default)

    def _load_settings(self): #vers 2
        """Load settings from file - Windows compatible"""
        try:
            if self.settings_file.exists():
                # FIXED: Use explicit encoding for Windows
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                settings = self.default_settings.copy()
                settings.update(loaded_settings)

                theme_name = settings.get("theme")
                if theme_name and theme_name not in self.themes:
                    print(f"Theme '{theme_name}' not found, using default")
                    if self.themes:
                        settings["theme"] = list(self.themes.keys())[0]
                    else:
                        settings["theme"] = "App_Factory"

                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")

        return self.default_settings.copy()


    def _load_all_themes(self): #vers 2
        """Load all theme files from themes directory - Windows compatible"""
        themes = {}
        try:
            if self.themes_dir.exists():
                for theme_file in self.themes_dir.glob("*.json"):
                    try:
                        # FIXED: Use explicit encoding for Windows
                        with open(theme_file, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                            theme_name = theme_file.stem
                            themes[theme_name] = theme_data
                            print(f"  Loaded: {theme_file.name}")
                    except Exception as e:
                        print(f"  Error loading {theme_file.name}: {e}")
            else:
                print(f"Themes directory not found: {self.themes_dir}")
        except Exception as e:
            print(f"Error accessing themes directory: {e}")

        if not themes:
            print("No themes loaded from files, using built-in themes")
            themes = self._get_builtin_themes()
        else:
            print(f"Successfully loaded {len(themes)} themes from files")
            builtin = self._get_builtin_themes()
            for name, data in builtin.items():
                if name not in themes:
                    themes[name] = data
                    print(f"   Added built-in fallback: {name}")

        return themes

    def save_settings(self):
        """Save current settings to file"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)  # ADD THIS LINE
            with open(self.settings_file, 'w', encoding='utf-8') as f:  # ADD encoding='utf-8'
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)  # ADD ensure_ascii=False
        except Exception as e:
            print(f"Could not save settings: {e}")
        # Map old 'project_folder' to assists_folder for compatibility
        if key == 'project_folder':
            return getattr(self, 'assists_folder', default)
        return getattr(self, key, default)

        # Default settings
        self.default_settings = {
            "theme": "lightgreen",
            "name": "lightgreen",
            "font_family": "Segoe UI",
            "font_size": 9,
            "font_weight": "normal",
            "font_style": "normal",
            "panel_font_family": "Segoe UI",
            "panel_font_size": 9,
            "panel_font_weight": "normal",
            "button_font_family": "Segoe UI",
            "button_font_size": 9,
            "button_font_weight": "bold",
            "panel_opacity": 95,
            "show_tooltips": True,
            "auto_save": True,
            "grid_size": 5,
            "snap_to_grid": True,
            "show_grid": True,
            "show_perfboard": True,
            "pin_label_size": 8,
            "zoom_sensitivity": 1.2,
            "max_undo_levels": 50,
            "panel_layout": "left",
            "collapsible_panels": True,
            "remember_window_state": True,
            "voice_commands": False,
            "animations": True,
            "sound_effects": False,
            "lcars_sounds": False,
            # Custom button colors
            "custom_button_colors": False,
            "button_import_color": "#2196f3",
            "button_export_color": "#4caf50",
            "button_remove_color": "#f44336",
            "button_update_color": "#ff9800",
            "button_convert_color": "#9c27b0",
            "button_default_color": "#FFECEE",
            # Icon control settings
            "show_button_icons": False,
            "show_menu_icons": True,
            "show_emoji_in_buttons": False,
            # Path remembering settings (from your existing file)
            "remember_img_output_path": True,
            "last_img_output_path": "/home/x2",
            "remember_import_path": True,
            "last_import_path": "",
            "remember_export_path": True,
            "last_export_path": "",
            "default_img_version": "VER2",
            "default_initial_size_mb": 100,
            "auto_create_directory_structure": False,
            "compression_enabled_by_default": False,
            "remember_dialog_positions": True,
            "show_creation_tips": True,
            "validate_before_creation": True,
             # Debug settings
            "debug_mode": False,
            "debug_level": "INFO",
            "debug_categories": ["IMG_LOADING", "TABLE_POPULATION", "BUTTON_ACTIONS"]
        }
        self.defaults = {
            "theme": "Default Green Theme",
            "name": "Default Green",
            "font_family": "Segoe UI",
            "font_size": 9,
            "panel_opacity": 95,
            "show_tooltips": True,
            "auto_save": True,
            "animations": True,
            "sound_effects": False,
            "lcars_sounds": False,

            # Grid and editor settings
            "grid_size": 5,
            "snap_to_grid": True,
            "show_grid": True,
            "show_perfboard": True,
            "pin_label_size": 8,
            "zoom_sensitivity": 1.2,
            "max_undo_levels": 50,

            # Layout settings
            "panel_layout": "left",
            "collapsible_panels": True,
            "remember_window_state": True,
            "voice_commands": False,

            # NEW: Path remembering settings (from your updated file)
            "remember_img_output_path": True,
            "last_img_output_path": "/home/x2",
            "remember_import_path": True,
            "last_import_path": "",
            "remember_export_path": True,
            "last_export_path": "",

            # NEW: IMG creation preferences (from your updated file)
            "default_img_version": "VER2",
            "default_initial_size_mb": 100,
            "auto_create_directory_structure": False,
            "compression_enabled_by_default": False,

            # NEW: Dialog preferences
            "remember_dialog_positions": True,
            "show_creation_tips": True,
            "validate_before_creation": True
        }

        self.themes = self._load_all_themes()
        self.current_settings = self.load_settings()

    def _get_builtin_themes(self):
        """Essential built-in themes as fallbacks"""
        return {
            "App_Factory": {
                "name": "App Factory Professional",
                "theme": "App Factory Professional",
                "description": "Clean, organized interface inspired by App Factory",
                "category": "Professional",
                "author": "X-Seti",
                "version": "1.0",
                "colors": {
                    "bg_primary": "#ffffff",
                    "bg_secondary": "#f8f9fa",
                    "bg_tertiary": "#e9ecef",
                    "panel_bg": "#f1f3f4",
                    "accent_primary": "#1976d2",
                    "accent_secondary": "#1565c0",
                    "text_primary": "#212529",
                    "text_secondary": "#495057",
                    "text_accent": "#1976d2",
                    "button_normal": "#e3f2fd",
                    "button_hover": "#bbdefb",
                    "button_pressed": "#90caf9",
                    "border": "#dee2e6",
                    "success": "#4caf50",
                    "warning": "#ff9800",
                    "error": "#f44336",
                    "action_import": "#2196f3",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0"
                }
            },
            "Default Green": {
                "theme": "Default Green",
                "name": "Default Green",
                "description": "Clean light green theme",
                "category": "Nature",
                "author": "X-Seti",
                "version": "1.0",
                "colors": {
                    "bg_primary": "#f8fff8",
                    "bg_secondary": "#f0f8f0",
                    "bg_tertiary": "#e8f5e8",
                    "panel_bg": "#f1f8f1",
                    "accent_primary": "#4caf50",
                    "accent_secondary": "#388e3c",
                    "text_primary": "#1b5e20",
                    "text_secondary": "#2e7d32",
                    "text_accent": "#388e3c",
                    "button_normal": "#e8f5e8",
                    "button_hover": "#c8e6c9",
                    "button_pressed": "#a5d6a7",
                    "border": "#a5d6a7",
                    "success": "#4caf50",
                    "warning": "#ff9800",
                    "error": "#f44336",
                    "action_import": "#2196f3",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0"
                }
            }
        }

    def get_last_img_output_path(self) -> str:
        """Get the last used IMG output path"""
        if self.current_settings.get("remember_img_output_path", True):
            return self.current_settings.get("last_img_output_path", "")
        return ""

    def set_last_img_output_path(self, path: str):
        """Set the last used IMG output path"""
        if self.current_settings.get("remember_img_output_path", True):
            self.current_settings["last_img_output_path"] = path
            self.save_settings()

    def get_last_import_path(self) -> str:
        """Get the last used import path"""
        if self.current_settings.get("remember_import_path", True):
            return self.current_settings.get("last_import_path", "")
        return ""

    def set_last_import_path(self, path: str):
        """Set the last used import path"""
        if self.current_settings.get("remember_import_path", True):
            self.current_settings["last_import_path"] = path
            self.save_settings()

    def get_last_export_path(self) -> str:
        """Get the last used export path"""
        if self.current_settings.get("remember_export_path", True):
            return self.current_settings.get("last_export_path", "")
        return ""

    def set_last_export_path(self, path: str):
        """Set the last used export path"""
        if self.current_settings.get("remember_export_path", True):
            self.current_settings["last_export_path"] = path
            self.save_settings()

    def get_default_img_settings(self) -> dict:
        """Get default IMG creation settings"""
        return {
            "version": self.current_settings.get("default_img_version", "VER2"),
            "initial_size_mb": self.current_settings.get("default_initial_size_mb", 100),
            "auto_create_structure": self.current_settings.get("auto_create_directory_structure", False),
            "compression_enabled": self.current_settings.get("compression_enabled_by_default", False)
        }

    def _load_themes_from_files(self):
        """Load themes from JSON files in themes/ directory"""
        themes_dir = Path("themes")
        if not themes_dir.exists():
            print("themes/ directory not found - using hardcoded themes")
            return

        print("Loading themes from files...")
        for theme_file in themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)

                # Use filename without extension as theme key
                theme_key = theme_file.stem
                self.themes[theme_key] = theme_data

                print(f"Loaded: {theme_key} - {theme_data.get('name', 'Unnamed')}")

            except Exception as e:
                print(f"Failed to load {theme_file}: {e}")

        print(f"Total themes loaded: {len(self.themes)}")

    def _get_default_settings(self):
        """Get default settings - FIXED: This method was missing"""
        return {
            "theme": "App_Factory",
            "font_family": "Arial",
            "font_size": 9,
            "show_tooltips": True,
            "auto_save": True,
            "panel_opacity": 95,
            "remember_img_output_path": True,
            "remember_import_path": True,
            "remember_export_path": True,
            "last_img_output_path": "",
            "last_import_path": "",
            "last_export_path": "",
            "default_img_version": "VER2",
            "default_initial_size_mb": 100,
            "auto_create_directory_structure": False,
            "compression_enabled_by_default": False,
            "debug_mode": False,
            "debug_level": "INFO",
            "debug_categories": [
                "IMG_LOADING",
                "TABLE_POPULATION",
                "BUTTON_ACTIONS",
                "FILE_OPERATIONS",
                "COL_LOADING",
                "COL_PARSING",
                "COL_THREADING",
                "COL_DISPLAY",
                "COL_INTEGRATION"
            ],
            "col_debug_enabled": False,
            "search_enabled": True,
            "performance_mode": True
        }

    def _load_all_themes(self):
        """Unified theme loading method"""
        themes = {}

        print(f"Looking for themes in: {self.themes_dir}")

        # Check if themes directory exists
        if self.themes_dir.exists() and self.themes_dir.is_dir():
            print(f"Found themes directory")

            # Load all .json files from themes directory
            theme_files = list(self.themes_dir.glob("*.json"))
            print(f"Found {len(theme_files)} theme files")

            for theme_file in theme_files:
                try:
                    print(f"Loading: {theme_file.name}")
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)

                    # Use filename without extension as theme key
                    theme_name = theme_file.stem
                    themes[theme_name] = theme_data

                    # Show theme info
                    display_name = theme_data.get('name', theme_name)
                    print(f"Loaded: {theme_name} -> '{display_name}'")

                except json.JSONDecodeError as e:
                    print(f"JSON error in {theme_file.name}: {e}")
                except Exception as e:
                    print(f"Error loading {theme_file.name}: {e}")
        else:
            print(f"Themes directory not found: {self.themes_dir}")

        # Add built-in fallback themes if no themes loaded
        if not themes:
            print("No themes loaded from files, using built-in themes")
            themes = self._get_builtin_themes()
        else:
            print(f"Successfully loaded {len(themes)} themes from files")
            # Add a few essential built-in themes as fallbacks
            builtin = self._get_builtin_themes()
            for name, data in builtin.items():
                if name not in themes:
                    themes[name] = data
                    print(f"Added built-in fallback: {name}")

        return themes

    def save_theme_to_file(self, theme_name, theme_data):
        """Save a theme to the themes folder"""
        try:
            # Ensure themes directory exists
            self.themes_dir.mkdir(exist_ok=True)

            theme_file = self.themes_dir / f"{theme_name}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)

            # Update local themes
            self.themes[theme_name] = theme_data
            return True

        except Exception as e:
            print(f"Error saving theme {theme_name}: {e}")
            return False

    def save_theme(self, theme_name: str, theme_data: dict): #vers 2
        """Save a theme to file and immediately reload themes - Windows compatible"""
        try:
            self.themes_dir.mkdir(parents=True, exist_ok=True)

            theme_file = self.themes_dir / f"{theme_name}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)

            print(f"Saved theme: {theme_name} -> {theme_file}")
            self.refresh_themes()

            return True

        except Exception as e:
            print(f"Error saving theme {theme_name}: {e}")
            import traceback
            traceback.print_exc()
            return False


    def refresh_themes(self):
        """Reload themes from disk - HOT RELOAD functionality"""
        print("Refreshing themes from disk...")
        old_count = len(self.themes)
        self.themes = self._load_all_themes()
        new_count = len(self.themes)

        print(f"Theme refresh complete: {old_count} -> {new_count} themes")
        return self.themes

    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # Merge with defaults (in case new settings were added)
                settings = self.default_settings.copy()
                settings.update(loaded_settings)

                # FIXED: Validate theme exists after themes are loaded
                theme_name = settings.get("theme")
                if theme_name and theme_name not in self.themes:
                    print(f"Theme '{theme_name}' not found, using default")
                    # Use first available theme or fallback
                    if self.themes:
                        settings["theme"] = list(self.themes.keys())[0]
                    else:
                        settings["theme"] = "lightgreen"

                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")

        return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to file"""
        try:
            # Ensure parent directory exists
            self.settings_file.parent.mkdir(exist_ok=True)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
            print(f"Settings saved to: {self.settings_file}")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get_theme_info(self, theme_name: str) -> dict:
        """Get detailed info about a specific theme"""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            return {
                "name": theme.get("name", theme_name),
                "description": theme.get("description", "No description"),
                "category": theme.get("category", "Uncategorized"),
                "author": theme.get("author", "Unknown"),
                "version": theme.get("version", "1.0"),
                "color_count": len(theme.get("colors", {}))
            }
        return {}

    def get_theme_colors(self, theme_name=None):
        """Get colors for specified theme"""
        if theme_name is None:
            theme_name = self.current_settings.get("theme", "APP_Factory")

        if theme_name in self.themes:
            return self.themes[theme_name].get("colors", {})
        else:
            print(f"Theme '{theme_name}' not found, using fallback")
            # Try to find any available theme
            if self.themes:
                fallback_name = list(self.themes.keys())[0]
                print(f"Using fallback theme: {fallback_name}")
                return self.themes[fallback_name].get("colors", {})
            else:
                print("No themes available!")
                return {}


    def get_stylesheet(self): #vers 3
        """Generate complete stylesheet for current theme - TXD Workshop style"""
        colors = self.get_theme_colors()
        if not colors:
            return ""

        # Base stylesheet
        stylesheet = f"""
        QMainWindow {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        QDialog {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        QWidget {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        /* Custom Title Bar - Same color as app background */
        QWidget#customTitleBar {{
            background-color: {colors.get('bg_secondary', '#f0f0f0')};
            color: {colors.get('text_primary', '#000000')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-bottom: 2px solid {colors.get('border', '#cccccc')};
        }}

        QWidget#customTitleBar QLabel {{
            background-color: transparent;
            color: {colors.get('text_primary', '#000000')};
        }}

        QWidget#customTitleBar QPushButton {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 3px;
            color: {colors.get('text_primary', '#000000')};
            font-size: 14pt;
            font-weight: bold;
        }}

        QWidget#customTitleBar QPushButton:hover {{
            background-color: {colors.get('button_hover', '#d0d0d0')};
        }}

        QWidget#customTitleBar QPushButton:pressed {{
            background-color: {colors.get('button_pressed', '#c0c0c0')};
        }}

        QWidget#customTitleBar QPushButton:disabled {{
            background-color: {colors.get('bg_secondary', '#f0f0f0')};
            border: 1px solid {colors.get('border', '#cccccc')};
        }}

        QGroupBox {{
            background-color: {colors.get('panel_bg', '#f0f0f0')};
            border: 2px solid {colors.get('border', '#cccccc')};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {colors.get('text_accent', '#15803d')};
        }}

        QPushButton {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 6px 12px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QPushButton:hover {{
            background-color: {colors.get('button_hover', '#d0d0d0')};
        }}

        QPushButton:pressed {{
            background-color: {colors.get('button_pressed', '#c0c0c0')};
        }}

        QTableWidget {{
            background-color: {colors.get('bg_secondary', '#f8f9fa')};
            alternate-background-color: {colors.get('bg_tertiary', '#e9ecef')};
            selection-background-color: {colors.get('accent_primary', '#1976d2')};
            selection-color: white;
            gridline-color: {colors.get('grid', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
        }}

        QTabWidget::pane {{
            border: 1px solid {colors.get('border', '#cccccc')};
            background-color: {colors.get('bg_primary', '#ffffff')};
        }}

        QTabBar::tab {{
            background-color: {colors.get('bg_secondary', '#f0f0f0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            padding: 8px 16px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QTabBar::tab:selected {{
            background-color: {colors.get('accent_primary', '#1976d2')};
            color: white;
        }}

        QTabBar::tab:hover {{
            background-color: {colors.get('button_hover', '#e0e0e0')};
        }}

        QComboBox {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 4px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QSpinBox {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 4px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QCheckBox {{
            color: {colors.get('text_primary', '#000000')};
        }}

        QLabel {{
            color: {colors.get('text_primary', '#000000')};
        }}
        """

        return stylesheet

    def _darken_color(self, hex_color, factor=0.8): #keep
        """Darken a hex color by a factor"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(int(c * factor) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except:
            return hex_color

    def _lighten_color(self, hex_color, factor=1.2):
        """Lighten a hex color by a factor"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            lightened = tuple(min(255, int(c * factor)) for c in rgb)
            return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        except:
            return hex_color

    def get_available_themes(self) -> dict:
        """Get all available themes with refresh option"""
        return self.themes

# ALSO UPDATE your get_theme method to handle missing themes:

    def get_theme(self, theme_name=None):
        """Get theme colors with fallback"""
        if theme_name is None:
            theme_name = self.current_settings["theme"]

        # Handle theme name mismatches (lightyellow_theme -> lightyellow)
        if theme_name.endswith('_theme'):
            theme_name = theme_name[:-6]  # Remove '_theme' suffix

        # Return theme or fallback to first available theme
        if theme_name in self.themes:
            return self.themes[theme_name]
        else:
            print(f"Theme '{theme_name}' not found, using fallback")
            fallback_theme = list(self.themes.keys())[0] if self.themes else "LCARS"
            return self.themes.get(fallback_theme, {"colors": {}})

    def get_theme_data(self, theme_name: str) -> dict:
        """Get complete theme data"""
        if theme_name in self.themes:
            return self.themes[theme_name]
        else:
            print(f"Theme '{theme_name}' not found, using fallback")
            fallback_theme = list(self.themes.keys())[0] if self.themes else "App_Factory"
            return self.themes.get(fallback_theme, {"colors": {}})



class SettingsDialog(QDialog): #vers 15
    """Settings dialog for theme and preference management"""

    themeChanged = pyqtSignal(str)  # theme_name
    settingsChanged = pyqtSignal()


    def __init__(self, app_settings, parent=None): #vers 4
        """Initialize settings dialog"""
        super().__init__(parent)
        self.setWindowTitle("App Factory Settings")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        self.app_settings = app_settings
        self.original_settings = app_settings.current_settings.copy()
        self._modified_colors = {}
        self.color_editors = {}

        # Initialize icon provider
        self.icons = IconProvider(self)

        # Setup resize handling
        self.resize_margin = 10
        self.resize_direction = None
        self.drag_position = None
        self.initial_geometry = None
        self.setMouseTracking(True)

        # Apply window mode (custRom gadgets or system)
        self._apply_dialog_window_mode()


        self._create_ui()
        self._load_current_settings()

    # ===== DEMO TAB FUNCTIONS =====


    def _apply_quick_theme(self, theme_name: str):
        """Apply quick theme with animation effect"""
        self.demo_theme_combo.setCurrentText(theme_name)
        self._apply_demo_theme(theme_name)

        # Animate button click
        sender = self.sender()
        if sender:
            original_text = sender.text()
            sender.setText(f"Applied!")
            QTimer.singleShot(1000, lambda: sender.setText(original_text))


    def _apply_dialog_window_mode(self): #vers 1
        """Apply custom window gadgets to dialog if enabled"""
        use_custom = self.app_settings.current_settings.get("use_custom_gadgets", False)

        if use_custom:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)


    def _random_theme(self):
        """Apply random theme"""
        import random
        themes = list(self.app_settings.themes.keys())
        current = self.demo_theme_combo.currentText()
        themes.remove(current)  # Don't pick the same theme

        random_theme = random.choice(themes)
        self.demo_theme_combo.setCurrentText(random_theme)
        self._apply_demo_theme(random_theme)

        self.demo_log.append(f"Random theme: {random_theme}")


    def _toggle_instant_apply(self, enabled: bool):
        """Enhanced instant apply toggle"""
        if enabled:
            current_theme = self.demo_theme_combo.currentText()
            self._apply_demo_theme(current_theme)
            self.preview_status.setText("Instant apply: ON")
            self.demo_log.append("Instant apply enabled")
        else:
            self.preview_status.setText("Instant apply: OFF")
            self.demo_log.append("Instant apply disabled")


    def _change_preview_scope(self, scope: str):
        """Change preview scope"""
        self.demo_log.append(f"Preview scope: {scope}")
        current_theme = self.demo_theme_combo.currentText()
        self._apply_demo_theme(current_theme)


    def _update_theme_info(self):
        """Update theme information display"""
        current_theme = self.demo_theme_combo.currentText()
        if current_theme in self.app_settings.themes:
            theme_data = self.app_settings.themes[current_theme]

            info_text = f"""
            <b>{theme_data.get('name', current_theme)}</b><br>
            <i>{theme_data.get('description', 'No description available')}</i><br><br>

            <b>Colors:</b><br>
            • Primary: {theme_data['colors'].get('accent_primary', 'N/A')}<br>
            • Background: {theme_data['colors'].get('bg_primary', 'N/A')}<br>
            • Text: {theme_data['colors'].get('text_primary', 'N/A')}<br>

            <b>Category:</b> {theme_data.get('category', 'Standard')}<br>
            <b>Author:</b> {theme_data.get('author', 'Unknown')}
            """

            if hasattr(self, 'theme_info_label'):
                self.theme_info_label.setText(info_text)


    def _update_titlebar_icons(self): #vers 2
        """Update titlebar icons when theme changes"""
        if not hasattr(self, 'custom_titlebar') and not hasattr(self, 'dialog_titlebar'):
            return

        # Clear icon cache and recreate provider
        if hasattr(self, 'icons'):
            self.icons.clear_cache()

        # Force refresh all titlebar button icons
        titlebar = getattr(self, 'custom_titlebar', None) or getattr(self, 'dialog_titlebar', None)
        if titlebar:
            for button in titlebar.findChildren(QPushButton):
                tooltip = button.toolTip()
                if tooltip == "Settings":
                    button.setIcon(self.icons.settings_icon(force_refresh=True))
                elif tooltip == "Minimize":
                    button.setIcon(self.icons.minimize_icon(force_refresh=True))
                elif tooltip == "Maximize":
                    if self.isMaximized():
                        button.setIcon(self.icons.restore_icon(force_refresh=True))
                    else:
                        button.setIcon(self.icons.maximize_icon(force_refresh=True))
                elif tooltip == "Close":
                    button.setIcon(self.icons.close_icon(force_refresh=True))



    def _update_preview_stats(self):
        """Update preview statistics"""
        if hasattr(self, 'stats_labels'):
            current_count = int(self.stats_labels["Preview Changes:"].text()) + 1
            self.stats_labels["Preview Changes:"].setText(str(current_count))
            self.stats_labels["Last Applied:"].setText(self.demo_theme_combo.currentText())


    def _show_full_preview(self):
        """Show full preview window"""
        QMessageBox.information(self, "Full Preview",
            "Full preview window would open here!\n\n"
            "This would show a complete App Factory interface\n"
            "with the selected theme applied.")


    def _preview_theme_instantly(self, theme_name: str):
        """Enhanced instant preview with better feedback"""
        if hasattr(self, 'auto_preview_check') and self.auto_preview_check.isChecked():
            self._apply_demo_theme(theme_name)
            self._update_theme_info()
            self._update_preview_stats()

            # Update status
            self.preview_status.setText(f"Previewing: {theme_name}")
            self.demo_log.append(f"Theme preview: {theme_name}")


    def _apply_demo_theme(self, theme_name: str): #vers 1
        """Apply theme to demo elements"""
        if theme_name not in self.app_settings.themes:
            return

        # Temporarily update settings for preview
        self.app_settings.current_settings["theme"] = theme_name

        # Apply theme stylesheet
        stylesheet = self.app_settings.get_stylesheet()

        # Apply to demo widgets if instant apply enabled
        if hasattr(self, 'instant_apply_check') and self.instant_apply_check.isChecked():
            self.setStyleSheet(stylesheet)
            self.themeChanged.emit(theme_name)

        if hasattr(self, 'demo_log'):
            self.demo_log.append(f"Previewing: {theme_name}")


    def _reset_demo_theme(self): #vers 1
        """Reset to original theme"""
        original = getattr(self, '_original_theme', self.app_settings.current_settings["theme"])
        if hasattr(self, 'demo_theme_combo'):
            self.demo_theme_combo.setCurrentText(original)
        self._apply_demo_theme(original)


    def _create_fonts_tab(self): #vers 2
        """Create fonts settings tab with multiple font type controls"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        info_label = QLabel("Configure fonts for different UI elements. Changes are saved to appfactory.settings.json")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 8px;")
        layout.addWidget(info_label)

        # Scroll area for font groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Font type configurations
        self.font_controls = {}

        font_types = [
            ("default", "Default Font", "General UI text and labels (was Font Family/Size)", "Segoe UI", 9, 8, 24),
            ("title", "Title Font", "Window titles and main headers", "Arial", 14, 10, 32),
            ("panel", "Panel Headers Font", "Group box titles and section headers", "Arial", 10, 8, 18),
            ("button", "Button Font", "All button text", "Arial", 10, 8, 16),
            ("menu", "Menu Font", "Menu bar and menu items", "Segoe UI", 9, 8, 14),
            ("infobar", "Info Bar Font", "Status bar and info display text", "Courier New", 9, 7, 14),
            ("table", "Table/List Font", "Data tables and list views", "Segoe UI", 9, 7, 14),
            ("tooltip", "Tooltip Font", "Hover tooltip text", "Segoe UI", 8, 7, 12)
        ]

        for font_id, title, description, default_family, default_size, min_size, max_size in font_types:
            group = self._create_font_control_group(
                font_id, title, description,
                default_family, default_size,
                min_size, max_size
            )
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Action buttons row
        actions_layout = QHBoxLayout()

        reset_fonts_btn = QPushButton("Reset All Fonts to Defaults")
        reset_fonts_btn.clicked.connect(self._reset_all_fonts)
        actions_layout.addWidget(reset_fonts_btn)

        actions_layout.addStretch()

        preview_btn = QPushButton("Preview Font Changes")
        preview_btn.clicked.connect(self._preview_font_changes)
        actions_layout.addWidget(preview_btn)

        layout.addLayout(actions_layout)

        return tab

    def _create_font_control_group(self, font_id, title, description,
                                default_family, default_size,
                                min_size, max_size): #vers 1
        """Create a font control group for specific font type"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #888; font-style: italic; font-size: 8pt;")
        layout.addWidget(desc_label)

        # Font controls row
        controls_layout = QHBoxLayout()

        # Font family
        controls_layout.addWidget(QLabel("Font:"))
        font_combo = QFontComboBox()

        # Load current font setting from appfactory.settings.json
        current_family = self.app_settings.current_settings.get(
            f'{font_id}_font_family', default_family
        )
        font_combo.setCurrentFont(QFont(current_family))
        font_combo.currentFontChanged.connect(
            lambda f, fid=font_id: self._on_font_changed(fid, 'family', f.family())
        )
        controls_layout.addWidget(font_combo, 1)

        # Font size
        controls_layout.addWidget(QLabel("Size:"))
        size_spin = QSpinBox()
        size_spin.setRange(min_size, max_size)
        current_size = self.app_settings.current_settings.get(
            f'{font_id}_font_size', default_size
        )
        size_spin.setValue(current_size)
        size_spin.setSuffix(" pt")
        size_spin.setFixedWidth(80)
        size_spin.valueChanged.connect(
            lambda v, fid=font_id: self._on_font_changed(fid, 'size', v)
        )
        controls_layout.addWidget(size_spin)

        # Font weight
        controls_layout.addWidget(QLabel("Weight:"))
        weight_combo = QComboBox()
        weight_combo.addItems(["Normal", "Bold", "Light"])
        current_weight = self.app_settings.current_settings.get(
            f'{font_id}_font_weight', 'Normal'
        )
        weight_combo.setCurrentText(current_weight)
        weight_combo.currentTextChanged.connect(
            lambda w, fid=font_id: self._on_font_changed(fid, 'weight', w)
        )
        weight_combo.setFixedWidth(100)
        controls_layout.addWidget(weight_combo)

        layout.addLayout(controls_layout)

        # Store controls for later access
        self.font_controls[font_id] = {
            'family': font_combo,
            'size': size_spin,
            'weight': weight_combo,
            'group': group,
            'default_family': default_family,
            'default_size': default_size
        }

        return group

    def _on_font_changed(self, font_id, property_type, value): #vers 1
        """Handle font property changes - updates current_settings"""
        if property_type == 'family':
            self.app_settings.current_settings[f'{font_id}_font_family'] = value
        elif property_type == 'size':
            self.app_settings.current_settings[f'{font_id}_font_size'] = value
        elif property_type == 'weight':
            self.app_settings.current_settings[f'{font_id}_font_weight'] = value

        # Mark as modified
        if not hasattr(self, '_fonts_modified'):
            self._fonts_modified = True

    def _preview_font_changes(self): #vers 1
        """Preview font changes in dialog"""
        try:
            # Apply default font to see immediate changes
            if 'default' in self.font_controls:
                family = self.font_controls['default']['family'].currentFont().family()
                size = self.font_controls['default']['size'].value()
                weight = self.font_controls['default']['weight'].currentText()

                font = QFont(family, size)
                if weight == "Bold":
                    font.setWeight(QFont.Weight.Bold)
                elif weight == "Light":
                    font.setWeight(QFont.Weight.Light)

                self.setFont(font)

            # Show preview info
            preview_text = "Font Preview Applied!\n\n"
            for font_id, controls in self.font_controls.items():
                family = controls['family'].currentFont().family()
                size = controls['size'].value()
                weight = controls['weight'].currentText()
                preview_text += f"{controls['group'].title()}: {family} {size}pt {weight}\n"

            QMessageBox.information(
                self,
                "Font Preview",
                preview_text + "\nClick 'Apply' to save changes to appfactory.settings.json"
            )
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Could not preview fonts:\n{e}")

    def _reset_all_fonts(self): #vers 1
        """Reset all fonts to their default values"""
        reply = QMessageBox.question(
            self,
            "Reset Fonts",
            "Reset all fonts to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for font_id, controls in self.font_controls.items():
                # Reset to defaults
                default_family = controls['default_family']
                default_size = controls['default_size']

                controls['family'].setCurrentFont(QFont(default_family))
                controls['size'].setValue(default_size)
                controls['weight'].setCurrentText('Normal')

                # Update settings
                self.app_settings.current_settings[f'{font_id}_font_family'] = default_family
                self.app_settings.current_settings[f'{font_id}_font_size'] = default_size
                self.app_settings.current_settings[f'{font_id}_font_weight'] = 'Normal'

            QMessageBox.information(self, "Fonts Reset", "All fonts reset to default values")

    def _load_font_settings(self): #vers 1
        """Load font settings from appfactory.settings.json into controls"""
        font_ids = ['default', 'title', 'panel', 'button', 'menu', 'infobar', 'table', 'tooltip']

        for font_id in font_ids:
            if font_id not in self.font_controls:
                continue

            controls = self.font_controls[font_id]

            # Load family
            family = self.app_settings.current_settings.get(
                f'{font_id}_font_family',
                controls['default_family']
            )
            controls['family'].setCurrentFont(QFont(family))

            # Load size
            size = self.app_settings.current_settings.get(
                f'{font_id}_font_size',
                controls['default_size']
            )
            controls['size'].setValue(size)

            # Load weight
            weight = self.app_settings.current_settings.get(
                f'{font_id}_font_weight',
                'Normal'
            )
            controls['weight'].setCurrentText(weight)

    def _save_font_settings(self): #vers 1
        """Save font settings from controls to app settings and appfactory.settings.json"""
        for font_id, controls in self.font_controls.items():
            family = controls['family'].currentFont().family()
            size = controls['size'].value()
            weight = controls['weight'].currentText()

            self.app_settings.current_settings[f'{font_id}_font_family'] = family
            self.app_settings.current_settings[f'{font_id}_font_size'] = size
            self.app_settings.current_settings[f'{font_id}_font_weight'] = weight

        # Save to appfactory.settings.json
        self.app_settings.save_settings()

    # ===== PICKER FUNCTIONS =====


class SettingsDialog(QDialog): #vers 5
    """Settings dialog for theme and preference management"""

    themeChanged = pyqtSignal(str)  # theme_name
    settingsChanged = pyqtSignal()

    def __init__(self, app_settings, parent=None): #vers 5
        """Initialize settings dialog"""
        super().__init__(parent)

        print(f"Has _update_titlebar_icons: {hasattr(self, '_update_titlebar_icons')}")

        self.setWindowTitle("App Factory Settings")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        self.app_settings = app_settings
        self.original_settings = app_settings.current_settings.copy()
        self._modified_colors = {}
        self.color_editors = {}

        # Initialize icon provider
        self.icons = IconProvider(self)

        # Set default fonts
        from PyQt6.QtGui import QFont
        default_font = QFont("Fira Sans Condensed", 14)
        self.setFont(default_font)
        self.title_font = QFont("Arial", 14)
        self.panel_font = QFont("Arial", 10)
        self.button_font = QFont("Arial", 10)
        self.infobar_font = QFont("Courier New", 9)

        # Setup resize handling
        self.dragging = False
        self.resizing = False
        self.resize_corner = None
        self.resize_margin = 10
        self.resize_direction = None
        self.corner_size = 20
        self.hover_corner = None

        self.drag_position = None
        self.initial_geometry = None
        self.setMouseTracking(True)

        # Apply window mode (custom gadgets or system)
        self._apply_dialog_window_mode()

        self._create_ui()
        self._load_current_settings()

    def _apply_dialog_window_mode(self): #vers 1
        """Apply custom window gadgets to dialog if enabled"""
        use_custom = self.app_settings.current_settings.get("use_custom_gadgets", False)

        if use_custom:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

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


    def resizeEvent(self, event): #vers 2
        '''Keep resize grip in bottom-right corner'''
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - 16, self.height() - 16)


    def mousePressEvent(self, event): #vers 2
        """Handle mouse press for dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on corner
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


    def mouseDoubleClickEvent(self, event): #vers 2
        """Handle double-click on toolbar to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_on_draggable_area(event.pos()):
                self._toggle_maximize()
                event.accept()
            else:
                super().mouseDoubleClickEvent(event)


    def _toggle_maximize(self): #vers 2
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def _is_on_draggable_area(self, pos): #vers 3
        """Check if position is on draggable toolbar area (stretch space, not buttons)"""
        if not hasattr(self, 'toolbar'):
            return False

        toolbar_rect = self.toolbar.geometry()
        if not toolbar_rect.contains(pos):
            return False

        # Get all buttons in toolbar
        buttons_to_check = []

        if hasattr(self, 'info_btn'):
            buttons_to_check.append(self.info_btn)
        if hasattr(self, 'minimize_btn'):
            buttons_to_check.append(self.minimize_btn)
        if hasattr(self, 'maximize_btn'):
            buttons_to_check.append(self.maximize_btn)
        if hasattr(self, 'close_btn'):
            buttons_to_check.append(self.close_btn)
        # Should be enabled on selection:


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


    def _create_ui(self): #vers 7
        """Create the settings dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Store original theme for reset
        self._original_theme = self.app_settings.current_settings.get("theme", "App_Factory")

        # Add custom titlebar if using custom gadgets
        if self.app_settings.current_settings.get("use_custom_gadgets", False):
            self._create_dialog_titlebar()
            layout.addWidget(self.dialog_titlebar)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add tabs
        self.color_picker_tab = self._create_color_picker_tab()
        self.tabs.addTab(self.color_picker_tab, "Colors")

        self.fonts_tab = self._create_fonts_tab()
        self.tabs.addTab(self.fonts_tab, "Fonts")

        self.debug_tab = self._create_debug_tab()
        self.tabs.addTab(self.debug_tab, "Debug")

        self.interface_tab = self._create_interface_tab()
        self.tabs.addTab(self.interface_tab, "Interface")

        content_layout.addWidget(self.tabs)

        # Buttons
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_btn)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        content_layout.addLayout(button_layout)

        layout.addWidget(content_widget)

    def _create_dialog_titlebar(self): #vers 6
        """Create custom title bar for settings dialog - TXD Workshop style"""
        self.dialog_titlebar = QWidget()
        self.dialog_titlebar.setObjectName("customTitleBar")
        self.dialog_titlebar.setFixedHeight(40)

        titlebar_layout = QHBoxLayout(self.dialog_titlebar)
        titlebar_layout.setContentsMargins(4, 4, 4, 4)
        titlebar_layout.setSpacing(4)

        # Settings icon button on the left (decorative)
        settings_icon_btn = QPushButton()
        settings_icon_btn.setIcon(self.icons.settings_icon())
        settings_icon_btn.setFixedSize(32, 32)
        settings_icon_btn.setEnabled(False)  # Just decorative
        titlebar_layout.addWidget(settings_icon_btn)

        # Get parent app name and center title
        titlebar_layout.addStretch()
        app_name = getattr(self.parent(), 'app_name', 'Application') if self.parent() else 'Application'
        title_label = QLabel(f"{app_name} - Settings")
        title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titlebar_layout.addWidget(title_label)
        titlebar_layout.addStretch()

        # Window control buttons on the right
        minimize_btn = QPushButton()
        minimize_btn.setIcon(self.icons.minimize_icon())
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.clicked.connect(self.showMinimized)
        minimize_btn.setToolTip("Minimize")
        titlebar_layout.addWidget(minimize_btn)

        maximize_btn = QPushButton()
        maximize_btn.setIcon(self.icons.maximize_icon())
        maximize_btn.setFixedSize(32, 32)
        maximize_btn.clicked.connect(self._toggle_dialog_maximize)
        maximize_btn.setToolTip("Maximize")
        self.dialog_maximize_btn = maximize_btn
        titlebar_layout.addWidget(maximize_btn)

        close_btn = QPushButton()
        close_btn.setIcon(self.icons.close_icon())
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.reject)
        close_btn.setToolTip("Close")
        titlebar_layout.addWidget(close_btn)

        # Enable dragging
        self.titlebar_drag_position = None
        self.dialog_titlebar.mousePressEvent = self._titlebar_mouse_press
        self.dialog_titlebar.mouseMoveEvent = self._titlebar_mouse_move
        self.dialog_titlebar.mouseDoubleClickEvent = self._titlebar_double_click


    def get_stylesheet(self): #vers 3
        """Generate complete stylesheet for current theme - TXD Workshop style"""
        colors = self.get_theme_colors()
        if not colors:
            return ""

        # Base stylesheet
        stylesheet = f"""
        QMainWindow {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        QDialog {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        QWidget {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        /* Custom Title Bar - Same color as app background */
        QWidget#customTitleBar {{
            background-color: {colors.get('bg_secondary', '#f0f0f0')};
            color: {colors.get('text_primary', '#000000')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-bottom: 2px solid {colors.get('border', '#cccccc')};
        }}

        QWidget#customTitleBar QLabel {{
            background-color: transparent;
            color: {colors.get('text_primary', '#000000')};
        }}

        #QWidget#customTitleBar QPushButton {{
        #    background-color: {colors.get('button_normal', '#e0e0e0')};
        #    border: 1px solid {colors.get('border', '#cccccc')};
        #    border-radius: 3px;
        #    color: {colors.get('text_primary', '#000000')};
        #    font-size: 14pt;
        #    font-weight: bold;
        #}}

        QWidget#customTitleBar QPushButton:hover {{
            background-color: {colors.get('button_hover', '#d0d0d0')};
        }}

        QWidget#customTitleBar QPushButton:pressed {{
            background-color: {colors.get('button_pressed', '#c0c0c0')};
        }}

        QWidget#customTitleBar QPushButton:disabled {{
            background-color: {colors.get('bg_secondary', '#f0f0f0')};
            border: 1px solid {colors.get('border', '#cccccc')};
        }}

        QGroupBox {{
            background-color: {colors.get('panel_bg', '#f0f0f0')};
            border: 2px solid {colors.get('border', '#cccccc')};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {colors.get('text_accent', '#15803d')};
        }}

        QPushButton {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 6px 12px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QPushButton:hover {{
            background-color: {colors.get('button_hover', '#d0d0d0')};
        }}

        QPushButton:pressed {{
            background-color: {colors.get('button_pressed', '#c0c0c0')};
        }}

        QTableWidget {{
            background-color: {colors.get('bg_secondary', '#f8f9fa')};
            alternate-background-color: {colors.get('bg_tertiary', '#e9ecef')};
            selection-background-color: {colors.get('accent_primary', '#1976d2')};
            selection-color: white;
            gridline-color: {colors.get('grid', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
        }}

        QTabWidget::pane {{
            border: 1px solid {colors.get('border', '#cccccc')};
            background-color: {colors.get('bg_primary', '#ffffff')};
        }}

        QTabBar::tab {{
            background-color: {colors.get('bg_secondary', '#f0f0f0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            padding: 8px 16px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QTabBar::tab:selected {{
            background-color: {colors.get('accent_primary', '#1976d2')};
            color: white;
        }}

        QTabBar::tab:hover {{
            background-color: {colors.get('button_hover', '#e0e0e0')};
        }}

        QComboBox {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 4px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QSpinBox {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 4px;
            color: {colors.get('text_primary', '#000000')};
        }}

        QCheckBox {{
            color: {colors.get('text_primary', '#000000')};
        }}

        QLabel {{
            color: {colors.get('text_primary', '#000000')};
        }}
        """

        return stylesheet


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

    def _titlebar_double_click(self, event): #vers 1
        """Handle double click on title bar - maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_dialog_maximize()
            event.accept()

    def _toggle_dialog_maximize(self): #vers 1
        """Toggle dialog maximize state"""
        if self.isMaximized():
            self.showNormal()
            if hasattr(self, 'dialog_maximize_btn'):
                self.dialog_maximize_btn.setIcon(self.icons.maximize_icon())
                self.dialog_maximize_btn.setToolTip("Maximize")
        else:
            self.showMaximized()
            if hasattr(self, 'dialog_maximize_btn'):
                self.dialog_maximize_btn.setIcon(self.icons.restore_icon())
                self.dialog_maximize_btn.setToolTip("Restore")


    def _titlebar_mouse_press(self, event): #vers 1
        """Handle mouse press on title bar"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.titlebar_drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def _titlebar_mouse_move(self, event): #vers 1
        """Handle mouse move on title bar - window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.titlebar_drag_position:
            self.move(event.globalPosition().toPoint() - self.titlebar_drag_position)
            event.accept()

    # ===== CORNER RESIZE METHODS (same as CustomWindow) =====

    def mousePressEvent(self, event): #vers 1
        """Handle mouse press for resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.app_settings.current_settings.get("enable_corner_resize", True):
                self.resize_direction = self._get_resize_direction(event.pos())
                if self.resize_direction:
                    self.drag_position = event.globalPosition().toPoint()
                    self.initial_geometry = self.geometry()
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse move for resizing and cursor updates"""
        if self.app_settings.current_settings.get("enable_corner_resize", True):
            if event.buttons() == Qt.MouseButton.LeftButton and self.resize_direction:
                self._handle_corner_resize(event.globalPosition().toPoint())
                event.accept()
                return
            else:
                direction = self._get_resize_direction(event.pos())
                self._update_cursor(direction)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.resize_direction = None
            self.drag_position = None
            self.initial_geometry = None
        super().mouseReleaseEvent(event)

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

    def _handle_corner_resize(self, global_pos): #vers 2
        """Handle window resizing from any edge or corner"""
        if not self.resize_direction or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        # Create a copy of the geometry
        new_geometry = QRect(geometry.x(), geometry.y(), geometry.width(), geometry.height())

        if "left" in self.resize_direction:
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            if new_width >= min_width:
                new_geometry.setLeft(new_x)

        if "right" in self.resize_direction:
            new_width = geometry.width() + delta.x()
            if new_width >= min_width:
                new_geometry.setWidth(new_width)

        if "top" in self.resize_direction:
            new_y = geometry.y() + delta.y()
            new_height = geometry.height() - delta.y()
            if new_height >= min_height:
                new_geometry.setTop(new_y)

        if "bottom" in self.resize_direction:
            new_height = geometry.height() + delta.y()
            if new_height >= min_height:
                new_geometry.setHeight(new_height)

        self.setGeometry(new_geometry)


    def _create_color_picker_tab(self): #vers 4
        """Create color picker and theme editor tab - FIXED global sliders"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)

        # Left Panel - Color Picker Tools and Global Sliders
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)

        # Screen Color Picker Group
        picker_group = QGroupBox("Color Picker")
        picker_layout = QVBoxLayout(picker_group)

        self.color_picker = ColorPickerWidget()
        picker_layout.addWidget(self.color_picker)

        instructions = QLabel("""
<b>How to use:</b><br>
1. Click 'Pick Color from Screen'<br>
2. Move mouse over any color<br>
3. Left-click to select or "ESC" to cancel<br>
<br>
<i>Picked colors can be applied to theme elements →</i>
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 8px; border-radius: 4px;")
        picker_layout.addWidget(instructions)

        left_layout.addWidget(picker_group)

        # Palette Colors Group
        palette_group = QGroupBox("Quick Colors")
        palette_layout = QGridLayout(palette_group)

        palette_colors = [
            "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF",
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#FF8000", "#8000FF", "#0080FF", "#80FF00", "#FF0080", "#00FF80",
            "#800000", "#008000", "#000080", "#808000", "#800080", "#008080"
        ]

        for i, color in enumerate(palette_colors):
            color_btn = QPushButton()
            color_btn.setFixedSize(25, 25)
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #999;")
            color_btn.setToolTip(color)
            color_btn.clicked.connect(lambda checked, c=color: self._apply_palette_color(c))
            row = i // 6
            col = i % 6
            palette_layout.addWidget(color_btn, row, col)

        left_layout.addWidget(palette_group)

        # GLOBAL THEME SLIDERS - PROPERLY PLACED HERE
        global_sliders_group = QGroupBox("Global Theme Sliders")
        global_sliders_layout = QVBoxLayout(global_sliders_group)

        info_label = QLabel("<b>Adjust ALL colors globally:</b>")
        global_sliders_layout.addWidget(info_label)

        # Global Hue Slider
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(QLabel("Hue:"))
        self.global_hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.global_hue_slider.setMinimum(-180)
        self.global_hue_slider.setMaximum(180)
        self.global_hue_slider.setValue(0)
        hue_layout.addWidget(self.global_hue_slider)
        self.global_hue_value = QLabel("0")
        self.global_hue_value.setFixedWidth(40)
        hue_layout.addWidget(self.global_hue_value)
        global_sliders_layout.addLayout(hue_layout)

        # Global Saturation Slider
        sat_layout = QHBoxLayout()
        sat_layout.addWidget(QLabel("Sat:"))
        self.global_sat_slider = QSlider(Qt.Orientation.Horizontal)
        self.global_sat_slider.setMinimum(-100)
        self.global_sat_slider.setMaximum(100)
        self.global_sat_slider.setValue(0)
        sat_layout.addWidget(self.global_sat_slider)
        self.global_sat_value = QLabel("0")
        self.global_sat_value.setFixedWidth(40)
        sat_layout.addWidget(self.global_sat_value)
        global_sliders_layout.addLayout(sat_layout)

        # Global Brightness Slider
        bri_layout = QHBoxLayout()
        bri_layout.addWidget(QLabel("Bri:"))
        self.global_bri_slider = QSlider(Qt.Orientation.Horizontal)
        self.global_bri_slider.setMinimum(-100)
        self.global_bri_slider.setMaximum(100)
        self.global_bri_slider.setValue(0)
        bri_layout.addWidget(self.global_bri_slider)
        self.global_bri_value = QLabel("0")
        self.global_bri_value.setFixedWidth(40)
        bri_layout.addWidget(self.global_bri_value)
        global_sliders_layout.addLayout(bri_layout)

        # Reset + Lock buttons
        buttons_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_global_sliders)
        buttons_layout.addWidget(reset_btn)

        lock_all_btn = QPushButton("Lock All")
        lock_all_btn.clicked.connect(self._lock_all_colors)
        buttons_layout.addWidget(lock_all_btn)

        unlock_all_btn = QPushButton("Unlock All")
        unlock_all_btn.clicked.connect(self._unlock_all_colors)
        buttons_layout.addWidget(unlock_all_btn)

        global_sliders_layout.addLayout(buttons_layout)
        left_layout.addWidget(global_sliders_group)
        left_layout.addStretch()

        # Right Panel - Theme Selection and Color Editors
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)


        # Theme Selection
        theme_sel_group = QGroupBox("Theme Selection")
        theme_sel_layout = QVBoxLayout(theme_sel_group)

        # Instant apply checkbox
        self.instant_apply_check = QCheckBox("Instant Apply")
        theme_sel_layout.addWidget(self.instant_apply_check)

        self.theme_selector_combo = QComboBox()
        for theme_key, theme_data in self.app_settings.themes.items():
            display_name = theme_data.get("name", theme_key)
            self.theme_selector_combo.addItem(display_name, theme_key)
        self.theme_selector_combo.currentTextChanged.connect(self._on_theme_changed)
        #self.theme_selector_combo.currentTextChanged.connect(self._apply_demo_theme)
        theme_sel_layout.addWidget(self.theme_selector_combo)


        # Theme action buttons
        theme_buttons_layout = QHBoxLayout()

        refresh_themes_btn = QPushButton("Refresh")
        refresh_themes_btn.clicked.connect(self._refresh_themes)
        refresh_themes_btn.setToolTip("Refresh theme list from disk")
        theme_buttons_layout.addWidget(refresh_themes_btn)

        save_theme_btn = QPushButton("Save")
        save_theme_btn.clicked.connect(self._save_current_theme)
        save_theme_btn.setToolTip("Save changes to current theme")
        theme_buttons_layout.addWidget(save_theme_btn)

        save_as_theme_btn = QPushButton("Save As...")
        save_as_theme_btn.clicked.connect(self._save_theme_as)
        save_as_theme_btn.setToolTip("Save as new theme")
        theme_buttons_layout.addWidget(save_as_theme_btn)

        theme_sel_layout.addLayout(theme_buttons_layout)

        right_layout.addWidget(theme_sel_group)

        # Color Editors Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Theme color labels
        self.theme_colors = {
            'bg_primary': 'Window Background',
            'bg_secondary': 'Panel Background',
            'bg_tertiary': 'Alternate Background',
            'panel_bg': 'GroupBox Background',
            'accent_primary': 'Primary Accent',
            'accent_secondary': 'Secondary Accent',
            'text_primary': 'Primary Text',
            'text_secondary': 'Secondary Text',
            'text_accent': 'Accent Text',
            'button_normal': 'Button Face',
            'button_hover': 'Button Hover',
            'button_pressed': 'Button Pressed',
            'border': 'Border Color',
            'success': 'Success Color',
            'warning': 'Warning Color',
            'error': 'Error Color'
        }

        # Create color editors
        self.color_editors = {}
        current_theme = self.app_settings.current_settings.get("theme", "App_Factory")
        if current_theme in self.app_settings.themes:
            colors = self.app_settings.themes[current_theme].get("colors", {})

            for color_key, color_name in self.theme_colors.items():
                current_value = colors.get(color_key, "#ffffff")
                editor = ThemeColorEditor(color_key, color_name, current_value)
                editor.colorChanged.connect(self._on_theme_color_changed)
                editor.lockChanged.connect(lambda key, locked: None)  # Handle lock changes
                self.color_editors[color_key] = editor
                scroll_layout.addWidget(editor)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        right_layout.addWidget(scroll_area)

        # Apply to Element Group
        selection_group = QGroupBox("Apply Picked Color")
        selection_layout = QVBoxLayout(selection_group)

        self.selected_element_combo = QComboBox()
        for color_key, color_name in self.theme_colors.items():
            self.selected_element_combo.addItem(color_name, color_key)
        selection_layout.addWidget(self.selected_element_combo)

        apply_color_btn = QPushButton("Apply Picked Color to Selected Element")
        apply_color_btn.clicked.connect(self._apply_picked_color)
        selection_layout.addWidget(apply_color_btn)

        right_layout.addWidget(selection_group)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        # IMPORTANT: Connect sliders AFTER all widgets are created
        self.global_hue_slider.valueChanged.connect(self._on_global_hue_changed)
        self.global_sat_slider.valueChanged.connect(self._on_global_sat_changed)
        self.global_bri_slider.valueChanged.connect(self._on_global_bri_changed)

        return tab


    def _apply_palette_color(self, color): #vers 1
        """Apply palette color to selected element"""
        selected_data = self.selected_element_combo.currentData()
        if selected_data and selected_data in self.color_editors:
            self.color_editors[selected_data].set_color(color)


    def _create_demo_tab(self) -> QWidget:
        """Create improved demo tab with better layout"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)  # Changed to horizontal for better space usage

        # Left column - Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(300)

        # Theme Selection Group
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout(theme_group)

        # Current theme display
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Active Theme:"))
        self.current_theme_label = QLabel(self.app_settings.current_settings["theme"])
        self.current_theme_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        current_layout.addWidget(self.current_theme_label)
        current_layout.addStretch()
        theme_layout.addLayout(current_layout)

        # Theme selector
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.demo_theme_combo = QComboBox()
        available_themes = list(self.app_settings.themes.keys())
        self.demo_theme_combo.addItems(available_themes)
        refresh_themes_btn = QPushButton("Refresh Themes")
        refresh_themes_btn.setToolTip("Reload themes from themes/ folder")
        refresh_themes_btn.clicked.connect(self.refresh_themes_in_dialog)
        self.demo_theme_combo.setCurrentText(self.app_settings.current_settings["theme"])
        self.demo_theme_combo.currentTextChanged.connect(self._preview_theme_instantly)

        preview_layout.addWidget(self.demo_theme_combo)
        theme_layout.addLayout(preview_layout)

        left_layout.addWidget(theme_group)

        # Real-time Controls Group
        controls_group = QGroupBox("Live Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Instant apply toggle
        self.instant_apply_check = QCheckBox("Apply changes instantly")
        self.instant_apply_check.setChecked(True)
        self.instant_apply_check.toggled.connect(self._toggle_instant_apply)
        controls_layout.addWidget(self.instant_apply_check)

        # Auto-preview toggle
        self.auto_preview_check = QCheckBox("Auto-preview on selection")
        self.auto_preview_check.setChecked(True)
        controls_layout.addWidget(self.auto_preview_check)

        # Preview scope
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(QLabel("Preview Scope:"))
        self.preview_scope_combo = QComboBox()
        self.preview_scope_combo.addItems(["Demo Only", "Dialog Only", "Full Application"])
        self.preview_scope_combo.setCurrentIndex(2)  # Full Application
        self.preview_scope_combo.currentTextChanged.connect(self._change_preview_scope)
        scope_layout.addWidget(self.preview_scope_combo)
        controls_layout.addLayout(scope_layout)

        left_layout.addWidget(controls_group)

        # Quick Themes Group
        quick_group = QGroupBox("🚀 Quick Themes")
        quick_layout = QVBoxLayout(quick_group)

        # Popular themes
        popular_themes = ["LCARS", "App_Factory", "Deep_Purple", "Cyberpunk", "Matrix"]
        for theme_name in popular_themes:
            if theme_name in self.app_settings.themes:
                quick_btn = QPushButton(f" {theme_name}")
                quick_btn.clicked.connect(lambda checked, t=theme_name: self._apply_quick_theme(t))
                quick_btn.setMinimumHeight(35)
                quick_layout.addWidget(quick_btn)

        # Reset and randomize buttons
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_demo_theme)
        random_btn = QPushButton("Random")
        random_btn.clicked.connect(self._random_theme)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(random_btn)
        quick_layout.addLayout(button_layout)

        left_layout.addWidget(quick_group)

        # Theme Info Group
        info_group = QGroupBox("Theme Info")
        info_layout = QVBoxLayout(info_group)

        self.theme_info_label = QLabel()
        self.theme_info_label.setWordWrap(True)
        self.theme_info_label.setMinimumHeight(100)
        #self.theme_info_label.setStyleSheet("padding: 8px;  border-radius: 4px;")
        info_layout.addWidget(self.theme_info_label)

        left_layout.addWidget(info_group)
        left_layout.addStretch()

        main_layout.addWidget(left_widget)

        # Right column - Preview Area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Preview Header
        preview_header = QGroupBox("Live Preview - App Factory Interface")
        header_layout = QHBoxLayout(preview_header)

        self.preview_status = QLabel("Ready for preview")
        self.preview_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        header_layout.addWidget(self.preview_status)
        header_layout.addStretch()

        # Preview controls
        self.full_preview_btn = QPushButton("Full Preview")
        self.full_preview_btn.clicked.connect(self._show_full_preview)
        header_layout.addWidget(self.full_preview_btn)

        right_layout.addWidget(preview_header)

        # Sample App Factory Toolbar
        toolbar_group = QGroupBox("Sample Toolbar")
        toolbar_layout = QGridLayout(toolbar_group)

        self.demo_buttons = []
        toolbar_buttons = [
            ("Open IMG", "import", "Open IMG archive"),
            ("Import Files", "import", "Import files to archive"),
            ("Export Selected", "export", "Export selected entries"),
            ("Remove Entry", "remove", "Remove selected entry"),
            ("Refresh", "update", "Refresh entry list"),
            ("Convert Format", "convert", "Convert file format"),
            ("Save Archive", None, "Save current archive"),
            ("Settings", None, "Open settings dialog")
        ]

        for i, (text, action_type, tooltip) in enumerate(toolbar_buttons):
            btn = QPushButton(text)
            if action_type:
                btn.setProperty("action-type", action_type)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(35)
            self.demo_buttons.append(btn)
            toolbar_layout.addWidget(btn, i // 4, i % 4)

        right_layout.addWidget(toolbar_group)

        # Sample Table
        table_group = QGroupBox("Sample IMG Entries Table")
        table_layout = QVBoxLayout(table_group)

        self.demo_table = QTableWidget(5, 5)
        self.demo_table.setHorizontalHeaderLabels(["Filename", "Type", "Size", "Version", "Status"])
        self.demo_table.setMaximumHeight(180)

        # Auto-resize columns
        self.demo_table.resizeColumnsToContents()
        table_layout.addWidget(self.demo_table)

        right_layout.addWidget(table_group)

        # Sample Log Output
        log_group = QGroupBox("Sample Activity Log")
        log_layout = QVBoxLayout(log_group)

        self.demo_log = QTextEdit()
        self.demo_log.setMaximumHeight(120)
        self.demo_log.setReadOnly(True)

        # Enhanced log content
        initial_log = """App Factory 1.0 - Live Theme Preview
Current IMG: sample_archive.img (150 MB)
Entries loaded: 1,247 files
Active theme: """ + self.app_settings.current_settings["theme"] + """
Live preview mode: ACTIVE
Ready for operations..."""

        self.demo_log.setPlainText(initial_log)
        log_layout.addWidget(self.demo_log)

        right_layout.addWidget(log_group)

        # Preview Statistics
        stats_group = QGroupBox("Preview Statistics")
        stats_layout = QGridLayout(stats_group)

        self.stats_labels = {}
        stats_data = [
            ("Themes Available:", str(len(available_themes))),
            ("Preview Changes:", "0"),
            ("Last Applied:", "None"),
            ("Performance:", "Excellent")
        ]

        for i, (label, value) in enumerate(stats_data):
            stats_layout.addWidget(QLabel(label), i, 0)
            value_label = QLabel(value)
            value_label.setStyleSheet("font-weight: bold; color: #1976D2;")
            self.stats_labels[label] = value_label
            stats_layout.addWidget(value_label, i, 1)

        right_layout.addWidget(stats_group)

        main_layout.addWidget(right_widget)

        # Initialize preview
        self._update_theme_info()
        self._apply_demo_theme(self.app_settings.current_settings["theme"])

        return tab


    def _create_debug_tab(self): #vers 2
        """Create debug settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Debug Mode Group
        debug_group = QGroupBox("🐛 Debug Mode")
        debug_layout = QVBoxLayout(debug_group)

        self.debug_enabled_check = QCheckBox("Enable debug mode")
        self.debug_enabled_check.setChecked(
            self.app_settings.current_settings.get('debug_mode', False)
        )
        debug_layout.addWidget(self.debug_enabled_check)

        # Debug Level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Debug Level:"))
        self.debug_level_combo = QComboBox()
        self.debug_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG", "VERBOSE"])
        self.debug_level_combo.setCurrentText(
            self.app_settings.current_settings.get('debug_level', 'INFO')
        )
        level_layout.addWidget(self.debug_level_combo)
        level_layout.addStretch()
        debug_layout.addLayout(level_layout)

        layout.addWidget(debug_group)

        # Debug Categories
        categories_group = QGroupBox("Debug Categories")
        categories_layout = QGridLayout(categories_group)

        self.debug_categories = {}
        default_categories = [
            ('IMG_LOADING', 'IMG file loading'),
            ('TABLE_POPULATION', 'Table population'),
            ('BUTTON_ACTIONS', 'Button actions'),
            ('FILE_OPERATIONS', 'File operations'),
            ('COL_PARSING', 'COL parsing'),
            ('THEME_SYSTEM', 'Theme system')
        ]

        enabled_cats = self.app_settings.current_settings.get('debug_categories', [])
        for i, (cat_id, cat_name) in enumerate(default_categories):
            checkbox = QCheckBox(cat_name)
            checkbox.setChecked(cat_id in enabled_cats)
            self.debug_categories[cat_id] = checkbox
            row = i // 2
            col = i % 2
            categories_layout.addWidget(checkbox, row, col)

        layout.addWidget(categories_group)

        # Clear log button
        clear_btn = QPushButton("Clear Debug Log")
        clear_btn.clicked.connect(self._clear_debug_log)
        layout.addWidget(clear_btn)

        layout.addStretch()
        return widget


    def _create_fonts_tab(self): #vers 1
        """Create fonts settings tab with multiple font type controls"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        info_label = QLabel("Configure fonts for different UI elements. Changes apply when theme is saved.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 8px;")
        layout.addWidget(info_label)

        # Scroll area for font groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Font type configurations
        self.font_controls = {}

        font_types = [
            ("default", "Default Font", "General UI text", "Segoe UI", 9, 8, 24),
            ("title", "Title Font", "Window titles and main headers", "Arial", 14, 10, 32),
            ("panel", "Panel Headers Font", "Group box titles", "Arial", 10, 8, 18),
            ("button", "Button Font", "All button text", "Arial", 10, 8, 16),
            ("menu", "Menu Font", "Menu bar and menu items", "Segoe UI", 9, 8, 14),
            ("infobar", "Info Bar Font", "Status bar and info text", "Courier New", 9, 7, 14),
            ("table", "Table/List Font", "Data tables and lists", "Segoe UI", 9, 7, 14),
            ("tooltip", "Tooltip Font", "Hover tooltip text", "Segoe UI", 8, 7, 12)
        ]

        for font_id, title, description, default_family, default_size, min_size, max_size in font_types:
            group = self._create_font_control_group(
                font_id, title, description,
                default_family, default_size,
                min_size, max_size
            )
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Preview button
        preview_btn = QPushButton("Preview Font Changes")
        preview_btn.clicked.connect(self._preview_font_changes)
        layout.addWidget(preview_btn)

        return tab


    def _create_font_control_group(self, font_id, title, description,
        default_family, default_size, min_size, max_size): #vers 1
        """Create a font control group for specific font type"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #888; font-style: italic; font-size: 8pt;")
        layout.addWidget(desc_label)

        # Font controls row
        controls_layout = QHBoxLayout()

        # Font family
        controls_layout.addWidget(QLabel("Font:"))
        font_combo = QFontComboBox()

        # Load current font setting
        current_family = self.app_settings.current_settings.get(
            f'{font_id}_font_family', default_family
        )
        font_combo.setCurrentFont(QFont(current_family))
        font_combo.currentFontChanged.connect(
            lambda f, fid=font_id: self._on_font_changed(fid, 'family', f.family())
        )
        controls_layout.addWidget(font_combo, 1)

        # Font size
        controls_layout.addWidget(QLabel("Size:"))
        size_spin = QSpinBox()
        size_spin.setRange(min_size, max_size)
        current_size = self.app_settings.current_settings.get(
            f'{font_id}_font_size', default_size
        )
        size_spin.setValue(current_size)
        size_spin.setSuffix(" pt")
        size_spin.setFixedWidth(80)
        size_spin.valueChanged.connect(
            lambda v, fid=font_id: self._on_font_changed(fid, 'size', v)
        )
        controls_layout.addWidget(size_spin)

        # Font weight
        controls_layout.addWidget(QLabel("Weight:"))
        weight_combo = QComboBox()
        weight_combo.addItems(["Normal", "Bold", "Light"])
        current_weight = self.app_settings.current_settings.get(
            f'{font_id}_font_weight', 'Normal'
        )
        weight_combo.setCurrentText(current_weight)
        weight_combo.currentTextChanged.connect(
            lambda w, fid=font_id: self._on_font_changed(fid, 'weight', w)
        )
        weight_combo.setFixedWidth(100)
        controls_layout.addWidget(weight_combo)

        layout.addLayout(controls_layout)

        # Store controls for later access
        self.font_controls[font_id] = {
            'family': font_combo,
            'size': size_spin,
            'weight': weight_combo,
            'group': group
        }

        return group


    def _on_font_changed(self, font_id, property_type, value): #vers 1
        """Handle font property changes"""
        if property_type == 'family':
            self.app_settings.current_settings[f'{font_id}_font_family'] = value
        elif property_type == 'size':
            self.app_settings.current_settings[f'{font_id}_font_size'] = value
        elif property_type == 'weight':
            self.app_settings.current_settings[f'{font_id}_font_weight'] = value

        # Mark as modified
        if not hasattr(self, '_fonts_modified'):
            self._fonts_modified = True


    def _preview_font_changes(self): #vers 1
        """Preview font changes in dialog"""
        # Apply fonts to current dialog elements
        try:
            # Default font
            if 'default' in self.font_controls:
                family = self.font_controls['default']['family'].currentFont().family()
                size = self.font_controls['default']['size'].value()
                weight = self.font_controls['default']['weight'].currentText()

                font = QFont(family, size)
                if weight == "Bold":
                    font.setWeight(QFont.Weight.Bold)
                elif weight == "Light":
                    font.setWeight(QFont.Weight.Light)

                self.setFont(font)

            QMessageBox.information(
                self,
                "Font Preview",
                "Font changes previewed!\n\nClick 'Apply' to save changes permanently."
            )
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Could not preview fonts:\n{e}")


    def _load_font_settings(self): #vers 1
        """Load font settings into controls"""
        font_ids = ['default', 'title', 'panel', 'button', 'menu', 'infobar', 'table', 'tooltip']

        for font_id in font_ids:
            if font_id not in self.font_controls:
                continue

            controls = self.font_controls[font_id]

            # Load family
            family = self.app_settings.current_settings.get(f'{font_id}_font_family', 'Segoe UI')
            controls['family'].setCurrentFont(QFont(family))

            # Load size
            size = self.app_settings.current_settings.get(f'{font_id}_font_size', 9)
            controls['size'].setValue(size)

            # Load weight
            weight = self.app_settings.current_settings.get(f'{font_id}_font_weight', 'Normal')
            controls['weight'].setCurrentText(weight)


    def _save_font_settings(self): #vers 1
        """Save font settings from controls to app settings"""
        for font_id, controls in self.font_controls.items():
            family = controls['family'].currentFont().family()
            size = controls['size'].value()
            weight = controls['weight'].currentText()

            self.app_settings.current_settings[f'{font_id}_font_family'] = family
            self.app_settings.current_settings[f'{font_id}_font_size'] = size
            self.app_settings.current_settings[f'{font_id}_font_weight'] = weight


    def _create_interface_tab(self): #vers 4
        """Create interface settings tab - UI display options"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Button Display Mode
        button_display_group = QGroupBox("Button Display Mode")
        button_display_layout = QVBoxLayout(button_display_group)

        self.button_display_combo = QComboBox()
        self.button_display_combo.addItems(["Icons + Text", "Icons Only", "Text Only"])

        # Load current setting
        current_mode = self.app_settings.current_settings.get("button_display_mode", "both")
        mode_map = {"both": 0, "icons": 1, "text": 2}
        self.button_display_combo.setCurrentIndex(mode_map.get(current_mode, 0))

        button_display_layout.addWidget(self.button_display_combo)

        hint_label = QLabel("Controls how toolbar buttons are displayed")
        hint_label.setStyleSheet("color: #888; font-style: italic;")
        button_display_layout.addWidget(hint_label)

        layout.addWidget(button_display_group)

        # Window Controls
        window_group = QGroupBox("Window Controls")
        window_layout = QVBoxLayout(window_group)

        self.custom_gadgets_check = QCheckBox("Use custom window gadgets (TXD Workshop style)")
        self.custom_gadgets_check.setChecked(
            self.app_settings.current_settings.get("use_custom_gadgets", False)
        )
        window_layout.addWidget(self.custom_gadgets_check)

        self.corner_resize_check = QCheckBox("Enable corner resize (all 4 corners)")
        self.corner_resize_check.setChecked(
            self.app_settings.current_settings.get("enable_corner_resize", True)
        )
        window_layout.addWidget(self.corner_resize_check)

        gadget_hint = QLabel("Custom gadgets disable system title bar. Corner resize works in both modes.")
        gadget_hint.setStyleSheet("color: #888; font-style: italic;")
        gadget_hint.setWordWrap(True)
        window_layout.addWidget(gadget_hint)

        layout.addWidget(window_group)

        # Interface Options
        interface_group = QGroupBox("Interface Options")
        interface_layout = QVBoxLayout(interface_group)

        self.tooltips_check = QCheckBox("Show tooltips")
        interface_layout.addWidget(self.tooltips_check)

        self.menu_icons_check = QCheckBox("Show menu icons")
        interface_layout.addWidget(self.menu_icons_check)

        self.use_svg_icons_check = QCheckBox("Use SVG icons (never emojis)")
        self.use_svg_icons_check.setChecked(
            self.app_settings.current_settings.get("use_svg_icons", True)
        )
        interface_layout.addWidget(self.use_svg_icons_check)

        layout.addWidget(interface_group)
        layout.addStretch()

        return widget

    # ===== GLOBAL SLIDER HANDLERS =====

    def _on_global_hue_changed(self, value): #vers 2
        """Handle global hue slider change - applies to ALL colors"""
        self.global_hue_value.setText(str(value))
        hue_shift = value
        sat_shift = self.global_sat_slider.value()
        bri_shift = self.global_bri_slider.value()
        self.apply_global_hsb_to_all_colors(hue_shift, sat_shift, bri_shift)

    def _on_global_sat_changed(self, value): #vers 2
        """Handle global saturation slider change - applies to ALL colors"""
        self.global_sat_value.setText(str(value))
        hue_shift = self.global_hue_slider.value()
        sat_shift = value
        bri_shift = self.global_bri_slider.value()
        self.apply_global_hsb_to_all_colors(hue_shift, sat_shift, bri_shift)

    def _on_global_bri_changed(self, value): #vers 2
        """Handle global brightness slider change - applies to ALL colors"""
        self.global_bri_value.setText(str(value))
        hue_shift = self.global_hue_slider.value()
        sat_shift = self.global_sat_slider.value()
        bri_shift = value
        self.apply_global_hsb_to_all_colors(hue_shift, sat_shift, bri_shift)

    def apply_global_hsb_to_all_colors(self, hue_shift, sat_shift, bri_shift): #vers 3
        """Apply HSB adjustments to ALL theme colors globally - respects locks"""
        if not hasattr(self, 'color_editors'):
            return

        if not hasattr(self, 'theme_selector_combo'):
            return

        current_theme = self.theme_selector_combo.currentData()
        if not current_theme:
            return

        original_colors = self.app_settings.get_theme_colors(current_theme)

        # Apply adjustments to each color
        for color_key, original_hex in original_colors.items():
            if color_key not in self.color_editors:
                continue

            editor = self.color_editors[color_key]

            # SKIP if locked
            if editor.is_locked:
                continue

            # Convert to HSL
            h, s, l = rgb_to_hsl(original_hex)

            # Apply shifts
            h = (h + hue_shift) % 360
            s = max(0, min(100, s + sat_shift))
            l = max(0, min(100, l + bri_shift))

            # Convert back to hex
            new_hex = hsl_to_rgb(h, s, l)

            # Update the color editor
            editor.update_color(new_hex)

            # Store modified color
            if not hasattr(self, '_modified_colors'):
                self._modified_colors = {}
            self._modified_colors[color_key] = new_hex

    def _reset_global_sliders(self): #vers 1
        """Reset global HSB sliders to default (0)"""
        self.global_hue_slider.setValue(0)
        self.global_sat_slider.setValue(0)
        self.global_bri_slider.setValue(0)

        current_theme = self.theme_selector_combo.currentData()
        if current_theme:
            original_colors = self.app_settings.get_theme_colors(current_theme)
            self._modified_colors = original_colors.copy()

            for color_key, editor in self.color_editors.items():
                if color_key in original_colors:
                    editor.update_color(original_colors[color_key])

    def _lock_all_colors(self): #vers 1
        """Lock all color editors"""
        if hasattr(self, 'color_editors'):
            for editor in self.color_editors.values():
                editor.set_locked(True)

    def _unlock_all_colors(self): #vers 1
        """Unlock all color editors"""
        if hasattr(self, 'color_editors'):
            for editor in self.color_editors.values():
                editor.set_locked(False)

    # ===== THEME MANAGEMENT =====

    def _on_theme_changed(self, theme_name): #vers 2
        """Handle theme selection change"""
        theme_key = None
        for key, data in self.app_settings.themes.items():
            if data.get("name", key) == theme_name:
                theme_key = key
                break

        if theme_key:
            self._load_theme_colors(theme_key)

            # Apply instantly if checkbox is enabled (copied from _apply_demo_theme)
            if hasattr(self, 'instant_apply_check') and self.instant_apply_check.isChecked():
                # Update settings temporarily
                self.app_settings.current_settings["theme"] = theme_key

                # Get and apply stylesheet
                stylesheet = self.app_settings.get_stylesheet()
                self.setStyleSheet(stylesheet)

                # Emit signal to parent
                self.themeChanged.emit(theme_key)

    def _load_theme_colors(self, theme_key): #vers 1
        """Load colors for selected theme into editors"""
        if theme_key in self.app_settings.themes:
            colors = self.app_settings.themes[theme_key].get("colors", {})

            for color_key, editor in self.color_editors.items():
                color_value = colors.get(color_key, "#ffffff")
                editor.set_color(color_value)

    def _on_theme_color_changed(self, color_key, hex_value): #vers 1
        """Handle individual color changes"""
        if not hasattr(self, '_modified_colors'):
            self._modified_colors = {}
        self._modified_colors[color_key] = hex_value

    def _on_color_changed(self, element_key, hex_color): #vers 1
        """Handle color change from color picker"""
        if not hasattr(self, '_modified_colors'):
            self._modified_colors = self.app_settings.get_theme_colors().copy()
        self._modified_colors[element_key] = hex_color

    def _apply_picked_color(self): #vers 1
        """Apply picked color to selected element"""
        picked_color = self.color_picker.current_color
        selected_data = self.selected_element_combo.currentData()

        if selected_data and picked_color:
            if selected_data in self.color_editors:
                self.color_editors[selected_data].set_color(picked_color)

            if hasattr(self, 'demo_log'):
                element_name = self.selected_element_combo.currentText()
                self.demo_log.append(f"Applied {picked_color} to {element_name}")

    def _refresh_themes(self): #vers 1
        """Refresh themes from disk"""
        current_theme = self.theme_selector_combo.currentData()
        self.app_settings.refresh_themes()

        self.theme_selector_combo.clear()
        for theme_key, theme_data in self.app_settings.themes.items():
            display_name = theme_data.get("name", theme_key)
            self.theme_selector_combo.addItem(display_name, theme_key)

        index = self.theme_selector_combo.findData(current_theme)
        if index >= 0:
            self.theme_selector_combo.setCurrentIndex(index)

    def refresh_themes_in_dialog(self): #vers 1
        """Refresh themes in settings dialog"""
        if hasattr(self, 'demo_theme_combo'):
            current_theme = self.demo_theme_combo.currentText()
            self.app_settings.refresh_themes()

            self.demo_theme_combo.clear()
            for theme_key in self.app_settings.themes.keys():
                self.demo_theme_combo.addItem(theme_key)

            index = self.demo_theme_combo.findText(current_theme)
            if index >= 0:
                self.demo_theme_combo.setCurrentIndex(index)

            if hasattr(self, 'demo_log'):
                self.demo_log.append(f"Refreshed: {len(self.app_settings.themes)} themes")


    # ===== SETTINGS MANAGEMENT =====

    def _load_current_settings(self): #vers 5
        """Load current settings into UI"""
        # Set theme
        if hasattr(self, 'theme_selector_combo'):
            current_theme = self.app_settings.current_settings.get("theme", "App_Factory")
            index = self.theme_selector_combo.findData(current_theme)
            if index >= 0:
                self.theme_selector_combo.setCurrentIndex(index)

       # Backward compatibility: migrate old font_family/font_size to default_font_*
        if 'font_family' in self.app_settings.current_settings and 'default' in self.font_controls:
            old_family = self.app_settings.current_settings.get('font_family', 'Segoe UI')
            old_size = self.app_settings.current_settings.get('font_size', 9)

            if 'default_font_family' not in self.app_settings.current_settings:
                self.app_settings.current_settings['default_font_family'] = old_family
                self.app_settings.current_settings['default_font_size'] = old_size
                self.font_controls['default']['family'].setCurrentFont(QFont(old_family))
                self.font_controls['default']['size'].setValue(old_size)

        # Load font settings
        if hasattr(self, 'font_controls'):
            self._load_font_settings()

        # Set interface settings
        if hasattr(self, 'font_family_combo'):
            self.font_family_combo.setCurrentText(
                self.app_settings.current_settings.get("font_family", "Segoe UI")
            )
        if hasattr(self, 'font_size_spin'):
            self.font_size_spin.setValue(
                self.app_settings.current_settings.get("font_size", 9)
            )
        if hasattr(self, 'tooltips_check'):
            self.tooltips_check.setChecked(
                self.app_settings.current_settings.get("show_tooltips", True)
            )
        if hasattr(self, 'menu_icons_check'):
            self.menu_icons_check.setChecked(
                self.app_settings.current_settings.get("show_menu_icons", True)
            )
        if hasattr(self, 'button_icons_check'):
            self.button_icons_check.setChecked(
                self.app_settings.current_settings.get("show_button_icons", False)
            )

            # Button display mode
        if hasattr(self, 'button_display_combo'):
            current_mode = self.app_settings.current_settings.get("button_display_mode", "both")
            mode_map = {"both": 0, "icons": 1, "text": 2}
            self.button_display_combo.setCurrentIndex(mode_map.get(current_mode, 0))

        # Window controls
        if hasattr(self, 'custom_gadgets_check'):
            self.custom_gadgets_check.setChecked(
                self.app_settings.current_settings.get("use_custom_gadgets", False)
            )
        if hasattr(self, 'corner_resize_check'):
            self.corner_resize_check.setChecked(
                self.app_settings.current_settings.get("enable_corner_resize", True)
            )

        # Interface settings
        if hasattr(self, 'tooltips_check'):
            self.tooltips_check.setChecked(
                self.app_settings.current_settings.get("show_tooltips", True)
            )
        if hasattr(self, 'menu_icons_check'):
            self.menu_icons_check.setChecked(
                self.app_settings.current_settings.get("show_menu_icons", True)
            )
        if hasattr(self, 'use_svg_icons_check'):
            self.use_svg_icons_check.setChecked(
                self.app_settings.current_settings.get("use_svg_icons", True)
            )

    def _get_dialog_settings(self): #vers 2
        """Collect all settings from dialog controls"""
        settings = {}

        # Get theme from demo tab if available
        if hasattr(self, 'demo_theme_combo'):
            settings["theme"] = self.demo_theme_combo.currentText()
        elif hasattr(self, 'theme_selector_combo'):
            theme_data = self.theme_selector_combo.currentData()
            if theme_data:
                settings["theme"] = theme_data
        else:
            settings["theme"] = self.app_settings.current_settings["theme"]

        # Font settings
        if hasattr(self, 'font_family_combo'):
            settings["font_family"] = self.font_family_combo.currentText()
        if hasattr(self, 'font_size_spin'):
            settings["font_size"] = self.font_size_spin.value()

        # Interface settings
        if hasattr(self, 'tooltips_check'):
            settings["show_tooltips"] = self.tooltips_check.isChecked()
        if hasattr(self, 'menu_icons_check'):
            settings["show_menu_icons"] = self.menu_icons_check.isChecked()
        if hasattr(self, 'button_icons_check'):
            settings["show_button_icons"] = self.button_icons_check.isChecked()

        # Button display mode
        if hasattr(self, 'button_display_combo'):
            mode_index = self.button_display_combo.currentIndex()
            mode_map = {0: "both", 1: "icons", 2: "text"}
            settings["button_display_mode"] = mode_map.get(mode_index, "both")

        # Window controls
        if hasattr(self, 'custom_gadgets_check'):
            settings["use_custom_gadgets"] = self.custom_gadgets_check.isChecked()
        if hasattr(self, 'corner_resize_check'):
            settings["enable_corner_resize"] = self.corner_resize_check.isChecked()

        # Interface settings
        if hasattr(self, 'tooltips_check'):
            settings["show_tooltips"] = self.tooltips_check.isChecked()
        if hasattr(self, 'menu_icons_check'):
            settings["show_menu_icons"] = self.menu_icons_check.isChecked()
        if hasattr(self, 'use_svg_icons_check'):
            settings["use_svg_icons"] = self.use_svg_icons_check.isChecked()

        # Debug settings
        if hasattr(self, 'debug_enabled_check'):
            settings["debug_mode"] = self.debug_enabled_check.isChecked()
        if hasattr(self, 'debug_level_combo'):
            settings["debug_level"] = self.debug_level_combo.currentText()
        if hasattr(self, 'debug_categories'):
            enabled_categories = []
            for category, checkbox in self.debug_categories.items():
                if checkbox.isChecked():
                    enabled_categories.append(category)
            settings["debug_categories"] = enabled_categories

        return settings


    def _apply_settings(self): #vers 5
        """Apply settings permanently and save to appfactory.settings.json"""
        new_settings = self._get_dialog_settings()
        old_theme = self.app_settings.current_settings["theme"]
        old_custom_gadgets = self.app_settings.current_settings.get("use_custom_gadgets", False)

        # Update settings
        self.app_settings.current_settings.update(new_settings)

        # Save font settings if modified
        if hasattr(self, 'font_controls'):
            self._save_font_settings()

        # Update modified colors if any
        if hasattr(self, '_modified_colors') and self._modified_colors:
            current_theme = self.app_settings.current_settings["theme"]
            if current_theme in self.app_settings.themes:
                if "colors" not in self.app_settings.themes[current_theme]:
                    self.app_settings.themes[current_theme]["colors"] = {}
                self.app_settings.themes[current_theme]["colors"].update(self._modified_colors)

        # Save settings to appfactory.settings.json
        self.app_settings.save_settings()

        # Apply theme and update icons
        stylesheet = self.app_settings.get_stylesheet()
        self.setStyleSheet(stylesheet)

        # Emit signals
        if new_settings["theme"] != old_theme:
            self.themeChanged.emit(new_settings["theme"])

        # Check if custom gadgets setting changed
        new_custom_gadgets = new_settings.get("use_custom_gadgets", False)
        if old_custom_gadgets != new_custom_gadgets:
            QMessageBox.information(
                self,
                "Restart Required",
                "Window gadget changes will take effect after restarting the application."
            )

        self.settingsChanged.emit()

        QMessageBox.information(
            self,
            "Applied",
            f"Settings saved to appfactory.settings.json\n\nActive theme: {new_settings['theme']}"
        )


    def _reset_to_defaults(self): #vers 1
        """Reset to default settings"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "This will reset all settings to their default values.\n\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.app_settings.current_settings = self.app_settings.default_settings.copy()
            self._load_current_settings()
            QMessageBox.information(self, "Reset", "Settings reset to defaults")

    def _clear_debug_log(self): #vers 1
        """Clear the activity log"""
        if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'log'):
            self.parent().gui_layout.log.clear()
            if hasattr(self.parent(), 'log_message'):
                self.parent().log_message("Debug log cleared")
        else:
            QMessageBox.information(self, "Clear Log", "Activity log cleared (if available).")

    def _ok_clicked(self): #vers 1
        """OK button clicked"""
        self._apply_settings()
        self.accept()

    def _save_current_theme(self): #vers 2
        """Save current theme with modifications"""
        colors = {}
        for color_key, editor in self.color_editors.items():
            colors[color_key] = editor.current_value

        # Update theme
        current_theme = self.theme_selector_combo.currentData()
        if current_theme in self.app_settings.themes:
            self.app_settings.themes[current_theme]["colors"] = colors
            self.app_settings.save_settings()

            QMessageBox.information(
                self,
                "Theme Saved",
                f"Theme '{current_theme}' saved successfully!"
            )

    def _save_theme_as(self): #vers 2
        """Save current theme as a new theme"""
        from PyQt6.QtWidgets import QInputDialog, QFileDialog, QMessageBox
        import json
        import os

        # Ask for new theme name with instructions
        theme_name, ok = QInputDialog.getText(
            self,
            "Save Theme As",
            "Theme Naming Guidelines:\n"
            "• Dark themes: Add _Dark suffix (e.g., Ocean_Dark)\n"
            "• Light themes: Add _Light suffix (e.g., Ocean_Light)\n\n"
            "Enter new theme name:",
            text="My_Custom_Theme"
        )

        if not ok or not theme_name:
            return

        # Create safe filename
        safe_filename = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in theme_name)
        safe_filename = safe_filename.replace(' ', '_').lower()

        # Collect all current colors
        colors = {}
        for color_key, editor in self.color_editors.items():
            colors[color_key] = editor.color_input.text()

        # Create theme data
        theme_data = {
            "name": theme_name,
            "description": f"Custom theme created from {self.theme_selector_combo.currentText()}",
            "category": "Custom",
            "author": "User",
            "version": "1.0",
            "colors": colors
        }

        # Use app_settings themes_dir
        themes_dir = str(self.app_settings.themes_dir)
        os.makedirs(themes_dir, exist_ok=True)

        default_path = os.path.join(themes_dir, f"{safe_filename}.json")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Theme File",
            default_path,
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(theme_data, f, indent=2)

                # Refresh themes
                self._refresh_themes()

                QMessageBox.information(
                    self,
                    "Theme Saved",
                    f"Theme '{theme_name}' saved successfully!\n\nFile: {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save theme:\n{str(e)}"
                )

    def get_contrast_text_color(self, bg_color: str) -> str: #vers 1
        """
        Calculate whether to use black or white text based on background brightness
        Returns '#000000' for light backgrounds, '#ffffff' for dark backgrounds
        """
        # Remove # if present
        if bg_color.startswith('#'):
            bg_color = bg_color[1:]

        # Handle 3-digit hex codes
        if len(bg_color) == 3:
            bg_color = ''.join([c*2 for c in bg_color])

        # Convert to RGB
        try:
            r = int(bg_color[:2], 16)
            g = int(bg_color[2:4], 16)
            b = int(bg_color[4:6], 16)
        except (ValueError, IndexError):
            return '#000000'  # Fallback to black

        # Calculate relative luminance using WCAG formula
        def get_luminance_component(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r_lum = get_luminance_component(r)
        g_lum = get_luminance_component(g)
        b_lum = get_luminance_component(b)

        luminance = 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum

        # Use white text for dark backgrounds (luminance < 0.5)
        # Use black text for light backgrounds (luminance >= 0.5)
        return '#ffffff' if luminance < 0.5 else '#000000'


class IconProvider: #vers 2
    """Provides SVG icons that adapt to theme colors"""

    def __init__(self, parent_widget, app_settings=None):
        """Initialize with parent widget and optional app_settings for theme access"""
        self.parent = parent_widget
        self.app_settings = app_settings or getattr(parent_widget, 'app_settings', None)
        self._icon_cache = {}

    def _get_icon_color(self): #vers 3
        """Get appropriate icon color based on current theme - uses theme text color"""
        if not self.app_settings:
            return '#000000'

        # Use the theme's primary text color for icons
        colors = self.app_settings.get_theme_colors()
        text_color = colors.get('text_primary', '#000000')

        return text_color

    def _svg_to_icon(self, svg_data, size=24, force_refresh=False): #vers 3
        """Convert SVG data to QIcon with theme color support"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray

        # Create cache key
        cache_key = (svg_data, size, self._get_icon_color())

        # Return cached icon if available and not forcing refresh
        if not force_refresh and cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        try:
            icon_color = self._get_icon_color()

            # Replace currentColor with determined color
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', icon_color)
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            icon = QIcon(pixmap)
            self._icon_cache[cache_key] = icon
            return icon
        except Exception as e:
            print(f"Error creating icon: {e}")
            return QIcon()

    def clear_cache(self): #vers 1
        """Clear icon cache to force regeneration with new theme colors"""
        self._icon_cache.clear()

    def restore_icon(self): #vers 1
        """Restore - Two overlapping squares"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="7" y="7" width="10" height="10"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
            <path d="M11 5h6a2 2 0 012 2v6"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def minimize_icon(self): #vers 1
        """Minimize - Horizontal line"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def maximize_icon(self): #vers 1
        """Maximize - Square"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def close_icon(self): #vers 1
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

    # File Operation Icons

    def folder_icon(self): #vers 1
        """Open - Folder icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-7l-2-2H5a2 2 0 00-2 2z"
                stroke="currentColor" stroke-width="2" stroke-linejoin="round" fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def save_icon(self): #vers 1
        """Save - Floppy disk icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M17 21v-8H7v8M7 3v5h8" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def import_icon(self): #vers 1
        """Import - Download arrow"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def export_icon(self): #vers 1
        """Export - Upload arrow"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    # Edit Icons

    def add_icon(self): #vers 1
        """Add - Plus icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="12" y1="5" x2="12" y2="19"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def delete_icon(self): #vers 1
        """Delete - Trash icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def edit_icon(self): #vers 1
        """Edit - Pencil icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M17 3a2.83 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z"
                stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def copy_icon(self): #vers 1
        """Copy icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="9" y="9" width="13" height="13" rx="2"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"
                stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    # View Icons

    def view_icon(self): #vers 1
        """View - Eye icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9
                M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17
                M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5
                C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"
                fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def settings_icon(self): #vers 1
        """Settings - Gear icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
                stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def info_icon(self): #vers 1
        """Info - Circle with i"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 11v6M12 8v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def filter_icon(self): #vers 1
        """Filter - Sliders icon"""
        svg_data = b'''<svg viewBox="0 0 20 20">
            <circle cx="6" cy="4" r="2" fill="currentColor"/>
            <rect x="5" y="8" width="2" height="8" fill="currentColor"/>
            <circle cx="14" cy="12" r="2" fill="currentColor"/>
            <rect x="13" y="4" width="2" height="6" fill="currentColor"/>
            <circle cx="10" cy="8" r="2" fill="currentColor"/>
            <rect x="9" y="12" width="2" height="4" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    # Utility Icons

    def undo_icon(self): #vers 1
        """Undo - Curved arrow"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M3 7v6h6M3 13a9 9 0 1018 0 9 9 0 00-18 0z"
                stroke="currentColor" stroke-width="2" fill="none"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def refresh_icon(self): #vers 1
        """Refresh - Circular arrow"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M16 10A6 6 0 1 1 4 10M4 10l3-3m-3 3l3 3"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round" fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


"""
# In your main window __init__:
from utils.app_settings_system import IconProvider

self.icons = IconProvider(self)

# Then use icons like:
open_btn.setIcon(self.icons.folder_icon())
save_btn.setIcon(self.icons.save_icon())
import_btn.setIcon(self.icons.import_icon())
export_btn.setIcon(self.icons.export_icon())
settings_btn.setIcon(self.icons.settings_icon())
"""

def rgb_to_hsl(hex_color): #vers 1
    """Convert hex color to HSL"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    r, g, b = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6.0

    return int(h * 360), int(s * 100), int(l * 100)


def hsl_to_rgb(h, s, l): #vers 1
    """Convert HSL to hex color"""
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0

    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"




def _create_debug_tab(self):
    """Create debug settings tab"""
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Debug Mode Group
    debug_group = QGroupBox("🐛 Debug Mode")
    debug_layout = QVBoxLayout(debug_group)

    self.debug_enabled_check = QCheckBox("Enable debug mode")
    self.debug_enabled_check.setChecked(self.app_settings.current_settings.get('debug_mode', False))
    self.debug_enabled_check.setToolTip("Enable detailed debug logging throughout the application")
    debug_layout.addWidget(self.debug_enabled_check)

    # Debug Level
    level_layout = QHBoxLayout()
    level_layout.addWidget(QLabel("Debug Level:"))
    self.debug_level_combo = QComboBox()
    self.debug_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG", "VERBOSE"])
    self.debug_level_combo.setCurrentText(self.app_settings.current_settings.get('debug_level', 'INFO'))
    self.debug_level_combo.setToolTip("Set the verbosity level for debug output")
    level_layout.addWidget(self.debug_level_combo)
    level_layout.addStretch()
    debug_layout.addLayout(level_layout)

    layout.addWidget(debug_group)

    # Debug Categories Group
    categories_group = QGroupBox("📋 Debug Categories")
    categories_layout = QGridLayout(categories_group)

    self.debug_categories = {}
    default_categories = [
        ('IMG_LOADING', 'IMG file loading and parsing'),
        ('TABLE_POPULATION', 'Table display and entry population'),
        ('BUTTON_ACTIONS', 'Button clicks and UI actions'),
        ('FILE_OPERATIONS', 'File read/write operations'),
        ('FILTERING', 'Table filtering and search'),
        ('SIGNAL_SYSTEM', 'Unified signal system')
    ]

    enabled_categories = self.app_settings.current_settings.get('debug_categories', [cat[0] for cat in default_categories])

    for i, (category, description) in enumerate(default_categories):
        checkbox = QCheckBox(category.replace('_', ' ').title())
        checkbox.setChecked(category in enabled_categories)
        checkbox.setToolTip(description)
        self.debug_categories[category] = checkbox

        row = i // 2
        col = i % 2
        categories_layout.addWidget(checkbox, row, col)

    layout.addWidget(categories_group)

    # Debug Actions Group
    actions_group = QGroupBox("Debug Actions")
    actions_layout = QVBoxLayout(actions_group)

    # Quick debug buttons
    buttons_layout = QHBoxLayout()

    test_debug_btn = QPushButton("Test Debug")
    test_debug_btn.setToolTip("Send a test debug message")
    test_debug_btn.clicked.connect(self._test_debug_output)
    buttons_layout.addWidget(test_debug_btn)

    debug_img_btn = QPushButton("Debug IMG")
    debug_img_btn.setToolTip("Debug current IMG file (if loaded)")
    debug_img_btn.clicked.connect(self._debug_current_img)
    buttons_layout.addWidget(debug_img_btn)

    clear_log_btn = QPushButton("Clear Log")
    clear_log_btn.setToolTip("Clear the activity log")
    clear_log_btn.clicked.connect(self._clear_debug_log)
    buttons_layout.addWidget(clear_log_btn)

    actions_layout.addLayout(buttons_layout)
    layout.addWidget(actions_group)
    layout.addStretch()

    return widget

def _test_debug_output(self):
    """Test debug output"""
    if hasattr(self.parent(), 'log_message'):
        self.parent().log_message("Debug test message - debug system working!")
        self.parent().log_message(f"[DEBUG-TEST] Debug enabled: {self.debug_enabled_check.isChecked()}")
        self.parent().log_message(f"[DEBUG-TEST] Debug level: {self.debug_level_combo.currentText()}")

        enabled_categories = [cat for cat, cb in self.debug_categories.items() if cb.isChecked()]
        self.parent().log_message(f"[DEBUG-TEST] Active categories: {', '.join(enabled_categories)}")
    else:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Debug Test", "Debug test completed!\nCheck the activity log for output.")

def _debug_current_img(self):
    """Debug current IMG file"""
    if hasattr(self.parent(), 'current_img') and self.parent().current_img:
        img = self.parent().current_img
        self.parent().log_message(f"[DEBUG-IMG] Current IMG: {img.file_path}")
        self.parent().log_message(f"[DEBUG-IMG] Entries: {len(img.entries)}")

        # Count file types
        file_types = {}
        for entry in img.entries:
            ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
            file_types[ext] = file_types.get(ext, 0) + 1

        self.parent().log_message(f"[DEBUG-IMG] File types found:")
        for ext, count in sorted(file_types.items()):
            self.parent().log_message(f"[DEBUG-IMG]   {ext}: {count} files")

        # Check table rows
        if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'table'):
            table = self.parent().gui_layout.table
            table_rows = table.rowCount()
            hidden_rows = sum(1 for row in range(table_rows) if table.isRowHidden(row))
            self.parent().log_message(f"[DEBUG-IMG] Table: {table_rows} rows, {hidden_rows} hidden")

    elif hasattr(self.parent(), 'log_message'):
        self.parent().log_message("[DEBUG-IMG] No IMG file currently loaded")
    else:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Debug IMG", "No IMG file loaded or no debug function available.")

def _clear_debug_log(self):
    """Clear the activity log"""
    if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'log'):
        self.parent().gui_layout.log.clear()
        self.parent().log_message("Debug log cleared")
    else:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Clear Log", "Activity log cleared (if available).")

def apply_theme_to_app(app, app_settings):
    """Apply theme to entire application"""
    stylesheet = app_settings.get_stylesheet()
    app.setStyleSheet(stylesheet)


def hsl_to_rgb(h, s, l): #vers 1
    """Convert HSL to RGB and return hex color"""
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0

    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q

        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    r = int(round(r * 255))
    g = int(round(g * 255))
    b = int(round(b * 255))

    return f"#{r:02x}{g:02x}{b:02x}"

def rgb_to_hsl(hex_color): #vers 1
    """Convert hex color to HSL values"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]

    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
    except (ValueError, IndexError):
        return 0, 0, 50  # Default values

    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val

    # Lightness
    l = (max_val + min_val) / 2.0

    if diff == 0:
        h = s = 0  # achromatic
    else:
        # Saturation
        s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)

        # Hue
        if max_val == r:
            h = (g - b) / diff + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / diff + 2
        elif max_val == b:
            h = (r - g) / diff + 4
        h /= 6

    return int(h * 360), int(s * 100), int(l * 100)


# Clean main function for testing only
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Create settings
    settings = AppSettings()
    
    # Create simple test window
    main_window = QMainWindow()
    main_window.setWindowTitle("App Factory Settings Test")
    main_window.setMinimumSize(400, 300)
    
    # Apply theme
    apply_theme_to_app(app, settings)
    
    # Show settings dialog
    dialog = SettingsDialog(settings, main_window)
    if dialog.exec():
        print("Settings applied")
    
    sys.exit(0)
