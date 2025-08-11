# $vers" X-Seti - June26, 2025 - Img Factory 1.5 theme settings"

#!/usr/bin/env python3
"""
IMG Factory App Settings System - Clean Version
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
    QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QFrame, QLineEdit
)

from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QCursor

# Check for screen capture libraries (for robust color picking)
try:
    import mss
    MSS_AVAILABLE = True
    print("✅ MSS library available - using high-performance screen capture")
except ImportError:
    MSS_AVAILABLE = False
    try:
        from PIL import ImageGrab
        PIL_AVAILABLE = True
        print("⚠️ MSS not available, using PIL fallback")
    except ImportError:
        PIL_AVAILABLE = False
        print("❌ Neither MSS nor PIL available - using Qt fallback")


class ColorPickerWidget(QWidget):
    """SAFE, simple color picker widget - NO THREADING"""
    colorPicked = pyqtSignal(str)  # Emits hex color

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 70)
        self.current_color = "#ffffff"
        self.picking_active = False
        self.color_display = None
        self.color_value = None
        self.pick_button = None
        self._setup_ui()

    def _setup_ui(self):
        # Main layout with better spacing
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Left side - Color display and value in a frame
        color_frame = QFrame()
        color_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        color_frame.setFixedSize(100, 50)

        color_layout = QVBoxLayout(color_frame)
        color_layout.setContentsMargins(5, 5, 5, 5)
        color_layout.setSpacing(2)

        # Color display
        self.color_display = QLabel()
        self.color_display.setFixedHeight(25)
        self.color_display.setStyleSheet("border: 1px solid #999; border-radius: 3px;")
        color_layout.addWidget(self.color_display)

        # Color value display
        self.color_value = QLabel("#FFFFFF")
        self.color_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_value.setStyleSheet("font-family: monospace; font-size: 9px; font-weight: bold;")
        color_layout.addWidget(self.color_value)

        main_layout.addWidget(color_frame)

        # Middle - Instructions
        info_layout = QVBoxLayout()
        instruction_label = QLabel("Click for Qt\nColor Dialog")
        instruction_label.setStyleSheet("font-size: 10px; color: #666;")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(instruction_label)
        main_layout.addLayout(info_layout)

        # Right side - Pick button
        self.pick_button = QPushButton("🎨 Pick")
        self.pick_button.setFixedSize(60, 50)
        self.pick_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: #E8F5E8;
            }
            QPushButton:hover {
                background-color: #C8E6C9;
            }
            QPushButton:pressed {
                background-color: #A5D6A7;
            }
        """)
        self.pick_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(self.pick_button)

        # Initialize display
        self.update_color_display("#ffffff")

    def open_color_dialog(self):
        """Open simple Qt color dialog - SAFE"""
        try:
            color = QColorDialog.getColor(QColor(self.current_color), self)
            if color.isValid():
                hex_color = color.name()
                self.current_color = hex_color
                self.update_color_display(hex_color)
                self.colorPicked.emit(hex_color)
                print(f"✅ Color selected: {hex_color}")
        except Exception as e:
            print(f"Color dialog error: {e}")

    def update_color_display(self, hex_color):
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
            print(f"❌ Display update error: {e}")

    def closeEvent(self, event):
        """Clean up when widget is closed"""
        super().closeEvent(event)

    def __del__(self):
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

class ThemeColorEditor(QWidget):
    """Widget for editing individual theme colors"""
    colorChanged = pyqtSignal(str, str)  # color_key, hex_value

    def __init__(self, color_key, color_name, current_value, parent=None):
        super().__init__(parent)
        self.color_key = color_key
        self.color_name = color_name
        self.current_value = current_value
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Color name label
        name_label = QLabel(self.color_name)
        name_label.setMinimumWidth(120)
        layout.addWidget(name_label)

        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 20)
        self.update_preview(self.current_value)
        layout.addWidget(self.color_preview)

        # Color value input
        self.color_input = QLineEdit(self.current_value)
        self.color_input.setMaximumWidth(80)
        self.color_input.setFont(QFont("monospace"))
        self.color_input.textChanged.connect(self.on_color_changed)
        layout.addWidget(self.color_input)

        # Color dialog button
        dialog_btn = QPushButton("🎨")
        dialog_btn.setFixedSize(25, 25)
        dialog_btn.clicked.connect(self.open_color_dialog)
        layout.addWidget(dialog_btn)

        layout.addStretch()

    def update_preview(self, hex_color):
        """Update color preview"""
        try:
            self.color_preview.setStyleSheet(
                f"background-color: {hex_color}; border: 1px solid #999; border-radius: 3px;"
            )
        except:
            self.color_preview.setStyleSheet("background-color: #ff0000; border: 1px solid #999;")

    def on_color_changed(self, text):
        """Handle color input change"""
        if text.startswith('#') and len(text) == 7:
            try:
                # Validate hex color
                QColor(text)
                self.current_value = text
                self.update_preview(text)
                self.colorChanged.emit(self.color_key, text)
            except:
                pass

    def open_color_dialog(self):
        """Open Qt color dialog"""
        color = QColorDialog.getColor(QColor(self.current_value), self)
        if color.isValid():
            hex_color = color.name()
            self.color_input.setText(hex_color)
            self.current_value = hex_color
            self.update_preview(hex_color)
            self.colorChanged.emit(self.color_key, hex_color)

    def set_color(self, hex_color):
        """Set color from external source (like color picker)"""
        self.color_input.setText(hex_color)
        self.current_value = hex_color
        self.update_preview(hex_color)
        self.colorChanged.emit(self.color_key, hex_color)

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
    def __init__(self, settings_file="imgfactory.settings.json"):
    #def __init__(self):
        # Get the directory where this file is located
        current_file_dir = Path(__file__).parent
        self.settings_file = settings_file

        # FIXED: Set paths based on where we are
        if current_file_dir.name == "utils":
            # We're in utils/, so themes are in ../themes/
            self.themes_dir = current_file_dir.parent / "themes"
            self.settings_file = current_file_dir.parent / "imgfactory.settings.json"
        else:
            # We're in root, so themes are in ./themes/
            self.themes_dir = current_file_dir / "themes"
            self.settings_file = current_file_dir / "imgfactory.settings.json"

        # Initialize default settings first
        self.default_settings = {
            'debug_mode': False,
            'debug_level': 'INFO',
            'current_theme': 'img_factory',
            'debug_categories': ['IMG_LOADING', 'TABLE_POPULATION', 'BUTTON_ACTIONS', 'FILE_OPERATIONS'],
            'working_gta_folder': os.path.expanduser("~/.steamapps/common/GTA Vice City/"),
            'assists_folder': os.path.expanduser("~/Desktop/Assists/"),
            'textures_folder': os.path.expanduser("~/Desktop/Textures/"),
            'collisions_folder': os.path.expanduser("~/Desktop/Collisions/"),
            'generics_folder': os.path.expanduser("~/Desktop/Generics/"),
            'water_folder': os.path.expanduser("~/Desktop/Water/"),
            'radar_folder': os.path.expanduser("~/Desktop/Radartiles/"),
            'gameart_folder': os.path.expanduser("~/Desktop/Gameart/"),
            'peds_folder': os.path.expanduser("~/Desktop/Peds/"),
            'vehicles_folder': os.path.expanduser("~/Desktop/Vehicles/"),
            'weapons_folder': os.path.expanduser("~/Desktop/Weapons/")
        }

        # Debug: Show what we found
        print(f"🎨 Looking for themes in: {self.themes_dir}")
        print(f"📁 Themes directory exists: {self.themes_dir.exists()}")
        if self.themes_dir.exists():
            theme_files = list(self.themes_dir.glob("*.json"))
            print(f"📄 Found {len(theme_files)} theme files")
            for theme_file in theme_files:
                print(f"  - {theme_file.name}")

        # Load themes first
        self.themes = self._load_all_themes()

        # Fixed: Initialize current_settings
        self.current_settings = self._load_settings()

        # GTA Project Directories - use values from settings
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
                print(f"✅ Directory ready: {directory}")
            except Exception as e:
                print(f"⚠️ Could not create directory {directory}: {e}")

    def get(self, key, default=None):
        """Get setting value for core functions compatibility"""
        # Map old 'project_folder' to assists_folder for compatibility
        if key == 'project_folder':
            return getattr(self, 'assists_folder', default)
        return getattr(self, key, default)

    def _load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_settings = self.default_settings.copy()
                    merged_settings.update(settings)
                    return merged_settings
        except Exception as e:
            print(f"⚠️ Could not load settings: {e}")

        # Return defaults if loading failed
        return self.default_settings.copy()

    def _load_all_themes(self):
        """Load all theme files from themes directory"""
        themes = {}
        try:
            if self.themes_dir.exists():
                for theme_file in self.themes_dir.glob("*.json"):
                    try:
                        with open(theme_file, 'r') as f:
                            theme_data = json.load(f)
                            theme_name = theme_file.stem
                            themes[theme_name] = theme_data
                    except Exception as e:
                        print(f"⚠️ Could not load theme {theme_file.name}: {e}")
        except Exception as e:
            print(f"⚠️ Error loading themes: {e}")

        return themes

    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save settings: {e}")
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
            "button_default_color": "#0078d4",
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
            "IMG_Factory": {
                "name": "IMG Factory Professional",
                "theme": "IMG Factory Professional",
                "description": "Clean, organized interface inspired by IMG Factory 📁",
                "category": "🏢 Professional",
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
                "description": "Clean light green theme 💚",
                "category": "🌿 Nature",
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
            print("⚠️ themes/ directory not found - using hardcoded themes")
            return

        print("🎨 Loading themes from files...")
        for theme_file in themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)

                # Use filename without extension as theme key
                theme_key = theme_file.stem
                self.themes[theme_key] = theme_data

                print(f"  ✅ Loaded: {theme_key} - {theme_data.get('name', 'Unnamed')}")

            except Exception as e:
                print(f"  ❌ Failed to load {theme_file}: {e}")

        print(f"📊 Total themes loaded: {len(self.themes)}")

    def _get_default_settings(self):
        """Get default settings - FIXED: This method was missing"""
        return {
            "theme": "img_factory",
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

        print(f"🔍 Looking for themes in: {self.themes_dir}")

        # Check if themes directory exists
        if self.themes_dir.exists() and self.themes_dir.is_dir():
            print(f"📁 Found themes directory")

            # Load all .json files from themes directory
            theme_files = list(self.themes_dir.glob("*.json"))
            print(f"🎨 Found {len(theme_files)} theme files")

            for theme_file in theme_files:
                try:
                    print(f"   📂 Loading: {theme_file.name}")
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)

                    # Use filename without extension as theme key
                    theme_name = theme_file.stem
                    themes[theme_name] = theme_data

                    # Show theme info
                    display_name = theme_data.get('name', theme_name)
                    print(f"   ✅ Loaded: {theme_name} -> '{display_name}'")

                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON error in {theme_file.name}: {e}")
                except Exception as e:
                    print(f"   ❌ Error loading {theme_file.name}: {e}")
        else:
            print(f"⚠️  Themes directory not found: {self.themes_dir}")

        # Add built-in fallback themes if no themes loaded
        if not themes:
            print("🔄 No themes loaded from files, using built-in themes")
            themes = self._get_builtin_themes()
        else:
            print(f"📊 Successfully loaded {len(themes)} themes from files")
            # Add a few essential built-in themes as fallbacks
            builtin = self._get_builtin_themes()
            for name, data in builtin.items():
                if name not in themes:
                    themes[name] = data
                    print(f"   ➕ Added built-in fallback: {name}")

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

    def save_theme(self, theme_name: str, theme_data: dict) -> bool:
        """Save a theme to file and immediately reload themes"""
        try:
            # Ensure themes directory exists
            self.themes_dir.mkdir(exist_ok=True)

            # Save theme file
            theme_file = self.themes_dir / f"{theme_name}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)

            print(f"💾 Saved theme: {theme_name} -> {theme_file}")

            # IMPORTANT: Immediately reload themes so the new theme is available
            self.refresh_themes()

            return True

        except Exception as e:
            print(f"❌ Error saving theme {theme_name}: {e}")
            return False

    def refresh_themes(self):
        """Reload themes from disk - HOT RELOAD functionality"""
        print("🔄 Refreshing themes from disk...")
        old_count = len(self.themes)
        self.themes = self._load_all_themes()
        new_count = len(self.themes)

        print(f"📊 Theme refresh complete: {old_count} -> {new_count} themes")
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
                    print(f"⚠️  Theme '{theme_name}' not found, using default")
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
            print(f"💾 Settings saved to: {self.settings_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
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
            theme_name = self.current_settings.get("theme", "IMG_Factory")

        if theme_name in self.themes:
            return self.themes[theme_name].get("colors", {})
        else:
            print(f"⚠️  Theme '{theme_name}' not found, using fallback")
            # Try to find any available theme
            if self.themes:
                fallback_name = list(self.themes.keys())[0]
                print(f"   Using fallback theme: {fallback_name}")
                return self.themes[fallback_name].get("colors", {})
            else:
                print("   No themes available!")
                return {}

    def get_stylesheet(self):
        """Generate complete stylesheet for current theme"""
        colors = self.get_theme_colors()
        if not colors:
            return ""

        # Base stylesheet
        stylesheet = f"""
        QMainWindow {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
        }}

        QWidget {{
            background-color: {colors.get('bg_primary', '#ffffff')};
            color: {colors.get('text_primary', '#000000')};
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
            color: {colors.get('text_accent', '#0078d4')};
        }}

        QPushButton {{
            background-color: {colors.get('button_normal', '#e0e0e0')};
            border: 1px solid {colors.get('border', '#cccccc')};
            border-radius: 4px;
            padding: 6px 12px;
            color: {colors.get('text_primary', '#000000')};
            font-weight: {self.current_settings.get('button_font_weight', 'bold')};
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
            gridline-color: {colors.get('border', '#dee2e6')};
        }}

        QMenuBar {{
            background-color: {colors.get('bg_secondary', '#f8f9fa')};
            color: {colors.get('text_primary', '#212529')};
        }}

        QStatusBar {{
            background-color: {colors.get('bg_secondary', '#f8f9fa')};
            color: {colors.get('text_secondary', '#495057')};
            border-top: 1px solid {colors.get('border', '#dee2e6')};
        }}
        """

        # Add action-specific button styling
        action_colors = {
            'import': {
                'normal': colors.get('action_import', '#2196f3'),
                'hover': self._lighten_color(colors.get('action_import', '#2196f3')),
                'pressed': self._darken_color(colors.get('action_import', '#2196f3'))
            },
            'export': {
                'normal': colors.get('action_export', '#4caf50'),
                'hover': self._lighten_color(colors.get('action_export', '#4caf50')),
                'pressed': self._darken_color(colors.get('action_export', '#4caf50'))
            },
            'remove': {
                'normal': colors.get('action_remove', '#f44336'),
                'hover': self._lighten_color(colors.get('action_remove', '#f44336')),
                'pressed': self._darken_color(colors.get('action_remove', '#f44336'))
            },
            'update': {
                'normal': colors.get('action_update', '#ff9800'),
                'hover': self._lighten_color(colors.get('action_update', '#ff9800')),
                'pressed': self._darken_color(colors.get('action_update', '#ff9800'))
            },
            'convert': {
                'normal': colors.get('action_convert', '#9c27b0'),
                'hover': self._lighten_color(colors.get('action_convert', '#9c27b0')),
                'pressed': self._darken_color(colors.get('action_convert', '#9c27b0'))
            }
        }

        for action_type, action_color_set in action_colors.items():
            stylesheet += f"""
            QPushButton[action-type="{action_type}"] {{
                background-color: {action_color_set['normal']};
                color: white;
                border: 1px solid {self._darken_color(action_color_set['normal'])};
            }}
            QPushButton[action-type="{action_type}"]:hover {{
                background-color: {action_color_set['hover']};
            }}
            QPushButton[action-type="{action_type}"]:pressed {{
                background-color: {action_color_set['pressed']};
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
            print(f"⚠️ Theme '{theme_name}' not found, using fallback")
            fallback_theme = list(self.themes.keys())[0] if self.themes else "LCARS"
            return self.themes.get(fallback_theme, {"colors": {}})

    def get_theme_data(self, theme_name: str) -> dict:
        """Get complete theme data"""
        if theme_name in self.themes:
            return self.themes[theme_name]
        else:
            print(f"⚠️ Theme '{theme_name}' not found, using fallback")
            fallback_theme = list(self.themes.keys())[0] if self.themes else "IMG_Factory"
            return self.themes.get(fallback_theme, {"colors": {}})

#
        
class SettingsDialog(QDialog):
    """Settings dialog for theme and preference management"""
    
    themeChanged = pyqtSignal(str)  # theme_name
    settingsChanged = pyqtSignal()
    
    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IMG Factory Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self.app_settings = app_settings
        self.original_settings = app_settings.current_settings.copy()
        
        self._create_ui()
        self._load_current_settings()
    
    def _get_dialog_settings(self) -> dict:
        """Collect all settings from dialog controls"""
        settings = {}

    def refresh_themes_in_dialog(self):
        """Refresh themes in settings dialog"""
        if hasattr(self, 'demo_theme_combo'):
            current_theme = self.demo_theme_combo.currentText()

            # Refresh themes from disk
            self.app_settings.refresh_themes()

            # Update combo box
            self.demo_theme_combo.clear()
            for theme_name, theme_data in self.app_settings.themes.items():
                display_name = theme_data.get("name", theme_name)
                self.demo_theme_combo.addItem(f"{display_name}", theme_name)

            # Try to restore previous selection
            index = self.demo_theme_combo.findData(current_theme)
            if index >= 0:
                self.demo_theme_combo.setCurrentIndex(index)

            if hasattr(self, 'demo_log'):
                self.demo_log.append(f"🔄 Refreshed themes: {len(self.app_settings.themes)} available")


        # Theme settings (if you have theme controls)
        if hasattr(self, 'theme_combo'):
            settings["theme"] = self.theme_combo.currentText()
        elif hasattr(self, 'demo_theme_combo'):
            settings["theme"] = self.demo_theme_combo.currentText()

        # Font settings (if you have font controls)
        if hasattr(self, 'font_family_combo'):
            settings["font_family"] = self.font_family_combo.currentText()
        if hasattr(self, 'font_size_spin'):
            settings["font_size"] = self.font_size_spin.value()

        # Interface settings (if you have these controls)
        if hasattr(self, 'opacity_slider'):
            settings["panel_opacity"] = self.opacity_slider.value()
        if hasattr(self, 'tooltips_check'):
            settings["show_tooltips"] = self.tooltips_check.isChecked()
        if hasattr(self, 'auto_save_check'):
            settings["auto_save"] = self.auto_save_check.isChecked()
        if hasattr(self, 'animations_check'):
            settings["animations"] = self.animations_check.isChecked()

        # Grid settings (if you have these controls)
        if hasattr(self, 'grid_size_spin'):
            settings["grid_size"] = self.grid_size_spin.value()
        if hasattr(self, 'snap_to_grid_check'):
            settings["snap_to_grid"] = self.snap_to_grid_check.isChecked()
        if hasattr(self, 'show_grid_check'):
            settings["show_grid"] = self.show_grid_check.isChecked()

        # Add any other settings you have controls for
        # Example pattern:
        # if hasattr(self, 'your_control_name'):
        #     settings["your_setting_key"] = self.your_control_name.value()  # or .isChecked() or .currentText()

        return settings

    def _get_dialog_settings(self) -> dict:
        """Simple version - collect basic settings"""
        settings = {}

        # Get theme from demo tab if available
        if hasattr(self, 'demo_theme_combo'):
            settings["theme"] = self.demo_theme_combo.currentText()
        else:
            # Keep current theme if no demo tab
            settings["theme"] = self.app_settings.current_settings["theme"]

        # Add any other simple settings here
        return settings


    # REPLACE: Improved Demo tab with better layout and complete functionality

    def get_contrast_text_color(self, bg_color: str) -> str:
        """
        Calculate whether to use black or white text based on background color brightness
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
            # Fallback to black text if color parsing fails
            return '#000000'

        # Calculate relative luminance using WCAG formula
        # https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
        def relative_luminance(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)

        r_rel = relative_luminance(r)
        g_rel = relative_luminance(g)
        b_rel = relative_luminance(b)

        luminance = 0.2126 * r_rel + 0.7152 * g_rel + 0.0722 * b_rel

        # Return white text for dark backgrounds (luminance < 0.5)
        # Return black text for light backgrounds (luminance >= 0.5)
        return '#ffffff' if luminance < 0.5 else '#000000'

    # UPDATE your get_stylesheet() method to use smart text colors:

    def get_stylesheet(self):
        """Generate complete stylesheet for current theme with JSON button text colors"""
        theme = self.get_theme()
        colors = theme["colors"]

        # Use custom button colors if enabled
        if self.current_settings["custom_button_colors"]:
            button_colors = {
                "import": self.current_settings["button_import_color"],
                "export": self.current_settings["button_export_color"],
                "remove": self.current_settings["button_remove_color"],
                "update": self.current_settings["button_update_color"],
                "convert": self.current_settings["button_convert_color"],
                "default": self.current_settings["button_default_color"]
            }
        else:
            button_colors = {
                "import": colors.get("action_import", colors["accent_primary"]),
                "export": colors.get("action_export", colors["success"]),
                "remove": colors.get("action_remove", colors["error"]),
                "update": colors.get("action_update", colors["warning"]),
                "convert": colors.get("action_convert", colors["accent_secondary"]),
                "default": colors["button_normal"]
            }

        # Build font strings
        main_font = f'{self.current_settings["font_family"]}, {self.current_settings["font_size"]}pt'
        panel_font = f'{self.current_settings["panel_font_family"]}, {self.current_settings["panel_font_size"]}pt'
        button_font = f'{self.current_settings["button_font_family"]}, {self.current_settings["button_font_size"]}pt'

        # GET BUTTON TEXT COLORS FROM JSON THEME (this is the key fix!)
        button_text = colors.get("button_text_color", "#000000")        # Use JSON color
        button_text_hover = colors.get("button_text_hover", button_text)  # Use JSON color
        button_text_pressed = colors.get("button_text_pressed", button_text)  # Use JSON color

        # Icon control CSS
        icon_style = ""
        if not self.current_settings.get("show_button_icons", False):
            icon_style = """
            QPushButton {
                qproperty-iconSize: 0px 0px;
            }
            """

        return f"""
            /* Main Window and Widgets */
            QMainWindow {{
                background-color: {colors["bg_primary"]};
                color: {colors["text_primary"]};
                font: {main_font};
            }}

            QWidget {{
                background-color: {colors["bg_primary"]};
                color: {colors["text_primary"]};
                font: {main_font};
            }}

            /* Panels and Group Boxes */
            QGroupBox {{
                background-color: {colors["panel_bg"]};
                border: 2px solid {colors["border"]};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                font: {panel_font};
                font-weight: {self.current_settings["panel_font_weight"]};
                color: {colors["text_accent"]};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {colors["accent_primary"]};
                font-weight: bold;
            }}

            /* FIXED: Default Buttons with JSON text color */
            QPushButton {{
                background-color: {button_colors["default"]};
                border: 2px solid {colors["accent_primary"]};
                border-radius: 6px;
                padding: 8px 16px;
                color: {button_text};  /* USE JSON BUTTON TEXT COLOR */
                font: {button_font};
                font-weight: {self.current_settings["button_font_weight"]};
                min-height: 20px;
            }}

            QPushButton:hover {{
                background-color: {colors["button_hover"]};
                border-color: {colors["accent_secondary"]};
                color: {button_text_hover};  /* USE JSON HOVER TEXT COLOR */
            }}

            QPushButton:pressed {{
                background-color: {colors["button_pressed"]};
                color: {button_text_pressed};  /* USE JSON PRESSED TEXT COLOR */
            }}

            /* FIXED: Action-specific buttons with JSON text colors */
            QPushButton[action-type="import"] {{
                background-color: {button_colors["import"]};
                border-color: {button_colors["import"]};
                color: {button_text};  /* USE JSON TEXT COLOR */
            }}

            QPushButton[action-type="export"] {{
                background-color: {button_colors["export"]};
                border-color: {button_colors["export"]};
                color: {button_text};  /* USE JSON TEXT COLOR */
            }}

            QPushButton[action-type="remove"] {{
                background-color: {button_colors["remove"]};
                border-color: {button_colors["remove"]};
                color: {button_text};  /* USE JSON TEXT COLOR */
            }}

            QPushButton[action-type="update"] {{
                background-color: {button_colors["update"]};
                border-color: {button_colors["update"]};
                color: {button_text};  /* USE JSON TEXT COLOR */
            }}

            QPushButton[action-type="convert"] {{
                background-color: {button_colors["convert"]};
                border-color: {button_colors["convert"]};
                color: {button_text};  /* USE JSON TEXT COLOR */
            }}

            /* Action button hover states */
            QPushButton[action-type="import"]:hover,
            QPushButton[action-type="export"]:hover,
            QPushButton[action-type="remove"]:hover,
            QPushButton[action-type="update"]:hover,
            QPushButton[action-type="convert"]:hover {{
                color: {button_text_hover};  /* USE JSON HOVER TEXT COLOR */
            }}

            /* Action button pressed states */
            QPushButton[action-type="import"]:pressed,
            QPushButton[action-type="export"]:pressed,
            QPushButton[action-type="remove"]:pressed,
            QPushButton[action-type="update"]:pressed,
            QPushButton[action-type="convert"]:pressed {{
                color: {button_text_pressed};  /* USE JSON PRESSED TEXT COLOR */
            }}

            /* Combo Boxes */
            QComboBox {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors["text_primary"]};
                min-height: 20px;
                font: {main_font};
            }}

            QComboBox:hover {{
                border-color: {colors["accent_primary"]};
            }}

            QComboBox QAbstractItemView {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["accent_primary"]};
                selection-background-color: {colors["accent_primary"]};
                color: {colors["text_primary"]};
            }}

            /* Tables */
            QTableWidget {{
                background-color: {colors["bg_secondary"]};
                border: 1px solid {colors["border"]};
                color: {colors["text_primary"]};
                gridline-color: {colors["grid"]};
                font: {main_font};
            }}

            QTableWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {colors["grid"]};
            }}

            QTableWidget::item:selected {{
                background-color: {colors["accent_primary"]};
                color: {colors["bg_primary"]};
            }}

            QHeaderView::section {{
                background-color: {colors["panel_bg"]};
                color: {colors["text_accent"]};
                padding: 6px;
                border: 1px solid {colors["border"]};
                font-weight: bold;
            }}

            /* Text Edit */
            QTextEdit {{
                background-color: {colors["bg_secondary"]};
                border: 1px solid {colors["border"]};
                color: {colors["text_primary"]};
                padding: 4px;
                font: {main_font};
            }}

            /* Line Edit */
            QLineEdit {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors["text_primary"]};
                font: {main_font};
            }}

            QLineEdit:focus {{
                border-color: {colors["accent_primary"]};
            }}

            /* Checkboxes */
            QCheckBox {{
                color: {colors["text_primary"]};
                font: {main_font};
            }}

            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {colors["border"]};
                border-radius: 3px;
                background-color: {colors["bg_secondary"]};
            }}

            QCheckBox::indicator:checked {{
                background-color: {colors["accent_primary"]};
                border-color: {colors["accent_primary"]};
            }}

            /* Icon control */
            {icon_style}
        """

    def _create_demo_tab(self) -> QWidget:
        """Create improved demo tab with better layout"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)  # Changed to horizontal for better space usage

        # Left column - Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(300)

        # Theme Selection Group
        theme_group = QGroupBox("🎨 Theme Selection")
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
        refresh_themes_btn = QPushButton("🔄 Refresh Themes")
        refresh_themes_btn.setToolTip("Reload themes from themes/ folder")
        refresh_themes_btn.clicked.connect(self.refresh_themes_in_dialog)
        self.demo_theme_combo.setCurrentText(self.app_settings.current_settings["theme"])
        self.demo_theme_combo.currentTextChanged.connect(self._preview_theme_instantly)

        preview_layout.addWidget(self.demo_theme_combo)
        theme_layout.addLayout(preview_layout)

        left_layout.addWidget(theme_group)

        # Real-time Controls Group
        controls_group = QGroupBox("⚡ Live Controls")
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
        popular_themes = ["LCARS", "IMG_Factory", "Deep_Purple", "Cyberpunk", "Matrix"]
        for theme_name in popular_themes:
            if theme_name in self.app_settings.themes:
                quick_btn = QPushButton(f"🎭 {theme_name}")
                quick_btn.clicked.connect(lambda checked, t=theme_name: self._apply_quick_theme(t))
                quick_btn.setMinimumHeight(35)
                quick_layout.addWidget(quick_btn)

        # Reset and randomize buttons
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.clicked.connect(self._reset_demo_theme)
        random_btn = QPushButton("🎲 Random")
        random_btn.clicked.connect(self._random_theme)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(random_btn)
        quick_layout.addLayout(button_layout)

        left_layout.addWidget(quick_group)

        # Theme Info Group
        info_group = QGroupBox("ℹ️ Theme Info")
        info_layout = QVBoxLayout(info_group)

        self.theme_info_label = QLabel()
        self.theme_info_label.setWordWrap(True)
        self.theme_info_label.setMinimumHeight(100)
        #self.theme_info_label.setStyleSheet("padding: 8px; background: #f5f5f5; border-radius: 4px;")
        info_layout.addWidget(self.theme_info_label)

        left_layout.addWidget(info_group)
        left_layout.addStretch()

        main_layout.addWidget(left_widget)

        # Right column - Preview Area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Preview Header
        preview_header = QGroupBox("📺 Live Preview - IMG Factory Interface")
        header_layout = QHBoxLayout(preview_header)

        self.preview_status = QLabel("Ready for preview")
        self.preview_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        header_layout.addWidget(self.preview_status)
        header_layout.addStretch()

        # Preview controls
        self.full_preview_btn = QPushButton("🖥️ Full Preview")
        self.full_preview_btn.clicked.connect(self._show_full_preview)
        header_layout.addWidget(self.full_preview_btn)

        right_layout.addWidget(preview_header)

        # Sample IMG Factory Toolbar
        toolbar_group = QGroupBox("🔧 Sample Toolbar")
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
        table_group = QGroupBox("📋 Sample IMG Entries Table")
        table_layout = QVBoxLayout(table_group)

        self.demo_table = QTableWidget(5, 5)
        self.demo_table.setHorizontalHeaderLabels(["Filename", "Type", "Size", "Version", "Status"])
        self.demo_table.setMaximumHeight(180)

        # Auto-resize columns
        self.demo_table.resizeColumnsToContents()
        table_layout.addWidget(self.demo_table)

        right_layout.addWidget(table_group)

        # Sample Log Output
        log_group = QGroupBox("📜 Sample Activity Log")
        log_layout = QVBoxLayout(log_group)

        self.demo_log = QTextEdit()
        self.demo_log.setMaximumHeight(120)
        self.demo_log.setReadOnly(True)

        # Enhanced log content
        initial_log = """🎮 IMG Factory 1.5 - Live Theme Preview
📁 Current IMG: sample_archive.img (150 MB)
📊 Entries loaded: 1,247 files
🎨 Active theme: """ + self.app_settings.current_settings["theme"] + """
⚡ Live preview mode: ACTIVE
📋 Ready for operations..."""

        self.demo_log.setPlainText(initial_log)
        log_layout.addWidget(self.demo_log)

        right_layout.addWidget(log_group)

        # Preview Statistics
        stats_group = QGroupBox("📊 Preview Statistics")
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

    def _preview_theme_instantly(self, theme_name: str):
        """Enhanced instant preview with better feedback"""
        if hasattr(self, 'auto_preview_check') and self.auto_preview_check.isChecked():
            self._apply_demo_theme(theme_name)
            self._update_theme_info()
            self._update_preview_stats()

            # Update status
            self.preview_status.setText(f"Previewing: {theme_name}")
            self.demo_log.append(f"🎨 Theme preview: {theme_name}")

    def _apply_demo_theme(self, theme_name: str):
        """Enhanced theme application with scope control"""
        if theme_name not in self.app_settings.themes:
            return

        # Temporarily update settings
        self.app_settings.current_settings["theme"] = theme_name
        stylesheet = self.app_settings.get_stylesheet()

        scope = getattr(self, 'preview_scope_combo', None)
        scope_text = scope.currentText() if scope else "Demo Only"

        # Apply to demo elements
        for btn in self.demo_buttons:
            btn.setStyleSheet(stylesheet)
        self.demo_table.setStyleSheet(stylesheet)
        self.demo_log.setStyleSheet(stylesheet)

        # Apply based on scope
        if scope_text == "Dialog Only" or scope_text == "Full Application":
            self.setStyleSheet(stylesheet)

        if scope_text == "Full Application":
            self.themeChanged.emit(theme_name)

        # Update current theme label
        if hasattr(self, 'current_theme_label'):
            self.current_theme_label.setText(theme_name)

    def _apply_quick_theme(self, theme_name: str):
        """Apply quick theme with animation effect"""
        self.demo_theme_combo.setCurrentText(theme_name)
        self._apply_demo_theme(theme_name)

        # Animate button click
        sender = self.sender()
        if sender:
            original_text = sender.text()
            sender.setText(f"✨ Applied!")
            QTimer.singleShot(1000, lambda: sender.setText(original_text))

    def _random_theme(self):
        """Apply random theme"""
        import random
        themes = list(self.app_settings.themes.keys())
        current = self.demo_theme_combo.currentText()
        themes.remove(current)  # Don't pick the same theme

        random_theme = random.choice(themes)
        self.demo_theme_combo.setCurrentText(random_theme)
        self._apply_demo_theme(random_theme)

        self.demo_log.append(f"🎲 Random theme: {random_theme}")

    def _toggle_instant_apply(self, enabled: bool):
        """Enhanced instant apply toggle"""
        if enabled:
            current_theme = self.demo_theme_combo.currentText()
            self._apply_demo_theme(current_theme)
            self.preview_status.setText("Instant apply: ON")
            self.demo_log.append("⚡ Instant apply enabled")
        else:
            self.preview_status.setText("Instant apply: OFF")
            self.demo_log.append("⏸️ Instant apply disabled")

    def _change_preview_scope(self, scope: str):
        """Change preview scope"""
        self.demo_log.append(f"🎯 Preview scope: {scope}")
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
            "This would show a complete IMG Factory interface\n"
            "with the selected theme applied.")

    def _reset_demo_theme(self):
        """Enhanced reset with confirmation"""
        original = getattr(self, '_original_theme', self.app_settings.current_settings["theme"])
        self.demo_theme_combo.setCurrentText(original)
        self._apply_demo_theme(original)

        # Reset stats
        if hasattr(self, 'stats_labels'):
            self.stats_labels["Preview Changes:"].setText("0")
            self.stats_labels["Last Applied:"].setText("Reset")

        self.demo_log.append(f"🔄 Reset to original: {original}")
        self.preview_status.setText("Reset to original theme")

    def _preview_theme_instantly(self, theme_name: str):
        """Preview theme in real-time without saving"""
        if hasattr(self, 'instant_apply_check') and self.instant_apply_check.isChecked():
            self._apply_demo_theme(theme_name)
            self.demo_log.append(f"🎨 Previewing theme: {theme_name}")

    def _apply_demo_theme(self, theme_name: str):
        """Apply theme to demo elements only"""
        if theme_name not in self.app_settings.themes:
            return

        # Temporarily update settings for preview
        original_theme = self.app_settings.current_settings["theme"]
        self.app_settings.current_settings["theme"] = theme_name

        # Apply theme to demo elements
        stylesheet = self.app_settings.get_stylesheet()

        # Apply to demo widgets
        for btn in self.demo_buttons:
            btn.setStyleSheet(stylesheet)

        self.demo_table.setStyleSheet(stylesheet)
        self.demo_log.setStyleSheet(stylesheet)

        # Apply to main dialog if instant apply is enabled
        if hasattr(self, 'instant_apply_check') and self.instant_apply_check.isChecked():
            self.setStyleSheet(stylesheet)

        # Emit theme change signal for main app
        self.themeChanged.emit(theme_name)

    def _apply_quick_theme(self, theme_name: str):
        """Apply quick theme selection"""
        self.demo_theme_combo.setCurrentText(theme_name)
        self._apply_demo_theme(theme_name)

    def _toggle_instant_apply(self, enabled: bool):
        """Toggle instant apply mode"""
        if enabled:
            current_theme = self.demo_theme_combo.currentText()
            self._apply_demo_theme(current_theme)
            self.demo_log.append("⚡ Instant apply enabled")
        else:
            self.demo_log.append("⏸️ Instant apply disabled")

    def _reset_demo_theme(self):
        """Reset to original theme"""
        original_theme = getattr(self, '_original_theme', self.app_settings.current_settings["theme"])
        self.demo_theme_combo.setCurrentText(original_theme)
        self._apply_demo_theme(original_theme)
        self.demo_log.append(f"🔄 Reset to original theme: {original_theme}")

    # UPDATE: Add demo tab to your existing _create_ui method
    def _create_ui(self):
        """Create the enhanced settings dialog UI"""
        layout = QVBoxLayout(self)

        # Store original theme for reset
        self._original_theme = self.app_settings.current_settings["theme"]

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Existing tabs...
        # Color picker tab (replaces themes tab)
        self.color_picker_tab = self._create_color_picker_tab()
        self.tabs.addTab(self.color_picker_tab, "🎨 Color Picker")

        # NEW: Add demo tab
        self.demo_tab = self._create_demo_tab()
        self.tabs.addTab(self.demo_tab, "🎭 Demo")

        self.debug_tab = self._create_debug_tab()
        self.tabs.addTab(self.debug_tab, "🐛 Debug")

        # Interface tab
        self.interface_tab = self._create_interface_tab()
        self.tabs.addTab(self.interface_tab, "⚙️ Interface")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("✅ Apply")
        apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_btn)
        
        ok_btn = QPushButton("💾 OK")
        ok_btn.clicked.connect(self._ok_clicked)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
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
        actions_group = QGroupBox("🔧 Debug Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Quick debug buttons
        buttons_layout = QHBoxLayout()

        test_debug_btn = QPushButton("🧪 Test Debug")
        test_debug_btn.setToolTip("Send a test debug message")
        test_debug_btn.clicked.connect(self._test_debug_output)
        buttons_layout.addWidget(test_debug_btn)

        debug_img_btn = QPushButton("📁 Debug IMG")
        debug_img_btn.setToolTip("Debug current IMG file (if loaded)")
        debug_img_btn.clicked.connect(self._debug_current_img)
        buttons_layout.addWidget(debug_img_btn)

        clear_log_btn = QPushButton("🗑️ Clear Log")
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
            self.parent().log_message("🧪 Debug test message - debug system working!")
            self.parent().log_message(f"🐛 [DEBUG-TEST] Debug enabled: {self.debug_enabled_check.isChecked()}")
            self.parent().log_message(f"🐛 [DEBUG-TEST] Debug level: {self.debug_level_combo.currentText()}")

            enabled_categories = [cat for cat, cb in self.debug_categories.items() if cb.isChecked()]
            self.parent().log_message(f"🐛 [DEBUG-TEST] Active categories: {', '.join(enabled_categories)}")
        else:
            QMessageBox.information(self, "Debug Test", "Debug test completed!\nCheck the activity log for output.")

    def _debug_current_img(self):
        """Debug current IMG file"""
        if hasattr(self.parent(), 'current_img') and self.parent().current_img:
            img = self.parent().current_img
            self.parent().log_message(f"🐛 [DEBUG-IMG] Current IMG: {img.file_path}")
            self.parent().log_message(f"🐛 [DEBUG-IMG] Entries: {len(img.entries)}")

            # Count file types
            file_types = {}
            for entry in img.entries:
                ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
                file_types[ext] = file_types.get(ext, 0) + 1

            self.parent().log_message(f"🐛 [DEBUG-IMG] File types found:")
            for ext, count in sorted(file_types.items()):
                self.parent().log_message(f"🐛 [DEBUG-IMG]   {ext}: {count} files")

            # Check table rows
            if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'table'):
                table = self.parent().gui_layout.table
                table_rows = table.rowCount()
                hidden_rows = sum(1 for row in range(table_rows) if table.isRowHidden(row))
                self.parent().log_message(f"🐛 [DEBUG-IMG] Table: {table_rows} rows, {hidden_rows} hidden")

        elif hasattr(self.parent(), 'log_message'):
            self.parent().log_message("🐛 [DEBUG-IMG] No IMG file currently loaded")
        else:
            QMessageBox.information(self, "Debug IMG", "No IMG file loaded or no debug function available.")

    def _clear_debug_log(self):
        """Clear the activity log"""
        if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'log'):
            self.parent().gui_layout.log.clear()
            self.parent().log_message("🗑️ Debug log cleared")
        else:
            QMessageBox.information(self, "Clear Log", "Activity log cleared (if available).")

    # keep


    def _create_color_picker_tab(self):
        """Create color picker and theme editor tab"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)

        # Left Panel - Color Picker Tools
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(300)

        # Screen Color Picker Group
        picker_group = QGroupBox("🎯 Screen Color Picker")
        picker_layout = QVBoxLayout(picker_group)

        self.color_picker = ColorPickerWidget()
        picker_layout.addWidget(self.color_picker)

        # Instructions
        instructions = QLabel("""
    <b>How to use:</b><br>
    1. Click 'Pick Color from Screen'<br>
    2. Move mouse over any color<br>
    3. Left-click to select<br>
    4. Right-click or ESC to cancel<br>
    <br>
    <i>Picked colors can be applied to theme elements →</i>
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 8px; background: #f5f5f5; border-radius: 4px;")
        picker_layout.addWidget(instructions)

        left_layout.addWidget(picker_group)

        # Palette Colors Group
        palette_group = QGroupBox("🎨 Quick Colors")
        palette_layout = QGridLayout(palette_group)

        # Common colors
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
            color_btn.clicked.connect(lambda checked, c=color: self.color_picker.update_color_display(c))

            row = i // 6
            col = i % 6
            palette_layout.addWidget(color_btn, row, col)

        left_layout.addWidget(palette_group)
        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # Right Panel - Theme Color Editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Theme Selection Header
        theme_header = QGroupBox("🎨 Theme Color Editor")
        header_layout = QHBoxLayout(theme_header)

        header_layout.addWidget(QLabel("Current Theme:"))
        self.theme_selector_combo = QComboBox()

        # Populate with available themes
        for theme_name in self.app_settings.themes.keys():
            self.theme_selector_combo.addItem(theme_name)
        self.theme_selector_combo.setCurrentText(self.app_settings.current_settings["theme"])
        self.theme_selector_combo.currentTextChanged.connect(self._load_theme_colors)

        header_layout.addWidget(self.theme_selector_combo)

        save_theme_btn = QPushButton("💾 Save Theme")
        save_theme_btn.clicked.connect(self._save_current_theme)
        header_layout.addWidget(save_theme_btn)

        right_layout.addWidget(theme_header)

        # Scrollable color editor area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Theme color definitions
        self.theme_colors = {
            "bg_primary": "Primary Background",
            "bg_secondary": "Secondary Background",
            "bg_tertiary": "Tertiary Background",
            "panel_bg": "Panel Background",
            "accent_primary": "Primary Accent",
            "accent_secondary": "Secondary Accent",
            "text_primary": "Primary Text",
            "text_secondary": "Secondary Text",
            "text_accent": "Accent Text",
            "button_normal": "Button Normal",
            "button_hover": "Button Hover",
            "button_pressed": "Button Pressed",
            "button_text_color": "Button Text",
            "border": "Borders",
            "success": "Success Color",
            "warning": "Warning Color",
            "error": "Error Color",
            "action_import": "Import Action",
            "action_export": "Export Action",
            "action_remove": "Remove Action",
            "action_update": "Update Action",
            "action_convert": "Convert Action"
        }

        # Create color editors
        self.color_editors = {}
        for color_key, color_name in self.theme_colors.items():
            # Get current color value from theme
            current_value = "#ffffff"  # Default
            current_theme = self.app_settings.current_settings["theme"]
            if current_theme in self.app_settings.themes:
                colors = self.app_settings.themes[current_theme].get("colors", {})
                current_value = colors.get(color_key, "#ffffff")

            editor = ThemeColorEditor(color_key, color_name, current_value)
            editor.colorChanged.connect(self._on_theme_color_changed)
            self.color_editors[color_key] = editor
            scroll_layout.addWidget(editor)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

        # Selected element display
        selection_group = QGroupBox("🎯 Apply Picked Color")
        selection_layout = QVBoxLayout(selection_group)

        self.selected_element_combo = QComboBox()
        for color_key, color_name in self.theme_colors.items():
            self.selected_element_combo.addItem(color_name, color_key)
        selection_layout.addWidget(self.selected_element_combo)

        apply_color_btn = QPushButton("🎨 Apply Picked Color to Selected Element")
        apply_color_btn.clicked.connect(self._apply_picked_color)
        selection_layout.addWidget(apply_color_btn)

        right_layout.addWidget(selection_group)

        main_layout.addWidget(right_panel)

        return tab

    def _load_theme_colors(self, theme_name):
        """Load colors for selected theme into editors"""
        if theme_name in self.app_settings.themes:
            colors = self.app_settings.themes[theme_name].get("colors", {})

            for color_key, editor in self.color_editors.items():
                color_value = colors.get(color_key, "#ffffff")
                editor.set_color(color_value)

    def _on_theme_color_changed(self, color_key, hex_value):
        """Handle individual color changes"""
        # Update the current theme with new color
        current_theme = self.theme_selector_combo.currentText()
        if current_theme in self.app_settings.themes:
            if "colors" not in self.app_settings.themes[current_theme]:
                self.app_settings.themes[current_theme]["colors"] = {}

            self.app_settings.themes[current_theme]["colors"][color_key] = hex_value

            # Apply changes if instant preview is enabled
            if hasattr(self, 'instant_apply_check') and self.instant_apply_check.isChecked():
                self.app_settings.current_settings["theme"] = current_theme
                self.themeChanged.emit(current_theme)

    def _apply_picked_color(self):
        """Apply picked color to selected element"""
        picked_color = self.color_picker.current_color
        selected_data = self.selected_element_combo.currentData()

        if selected_data and picked_color:
            if selected_data in self.color_editors:
                self.color_editors[selected_data].set_color(picked_color)

            # Log the action
            if hasattr(self, 'demo_log'):
                element_name = self.selected_element_combo.currentText()
                self.demo_log.append(f"🎨 Applied {picked_color} to {element_name}")

    def _save_current_theme(self):
        """Save current theme modifications"""
        current_theme = self.theme_selector_combo.currentText()

        # Collect all current colors
        colors = {}
        for color_key, editor in self.color_editors.items():
            colors[color_key] = editor.current_value

        # Update theme data
        if current_theme in self.app_settings.themes:
            self.app_settings.themes[current_theme]["colors"] = colors

            # Save to file
            success = self.app_settings.save_theme(current_theme, self.app_settings.themes[current_theme])

            if success:
                QMessageBox.information(self, "Theme Saved", f"Theme '{current_theme}' saved successfully!")
                if hasattr(self, 'demo_log'):
                    self.demo_log.append(f"💾 Theme '{current_theme}' saved with custom colors")
            else:
                QMessageBox.warning(self, "Save Failed", f"Failed to save theme '{current_theme}'")
        else:
            QMessageBox.warning(self, "No Theme", "No theme selected to save")
    
    def _create_interface_tab(self):
        """Create interface settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QVBoxLayout(font_group)
        
        # Font family
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Segoe UI", "Arial", "Tahoma", "Verdana", "Consolas"])
        font_family_layout.addWidget(self.font_family_combo)
        font_layout.addLayout(font_family_layout)
        
        # Font size
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        font_layout.addLayout(font_size_layout)
        
        layout.addWidget(font_group)
        
        # Interface options
        interface_group = QGroupBox("Interface Options")
        interface_layout = QVBoxLayout(interface_group)
        
        self.tooltips_check = QCheckBox("Show tooltips")
        interface_layout.addWidget(self.tooltips_check)
        
        self.menu_icons_check = QCheckBox("Show menu icons")
        interface_layout.addWidget(self.menu_icons_check)
        
        self.button_icons_check = QCheckBox("Show button icons")
        interface_layout.addWidget(self.button_icons_check)
        
        layout.addWidget(interface_group)
        layout.addStretch()
        
        return widget
    
    def _load_current_settings(self):
        """Load current settings into UI"""
        # Set theme in color picker tab
        if hasattr(self, 'theme_selector_combo'):
            current_theme = self.app_settings.current_settings.get("theme", "IMG_Factory")
            self.theme_selector_combo.setCurrentText(current_theme)
            self._load_theme_colors(current_theme)

        # Set interface settings (keep the rest as is)
        if hasattr(self, 'font_family_combo'):
            self.font_family_combo.setCurrentText(self.app_settings.current_settings.get("font_family", "Segoe UI"))
        if hasattr(self, 'font_size_spin'):
            self.font_size_spin.setValue(self.app_settings.current_settings.get("font_size", 9))
        if hasattr(self, 'tooltips_check'):
            self.tooltips_check.setChecked(self.app_settings.current_settings.get("show_tooltips", True))
        if hasattr(self, 'menu_icons_check'):
            self.menu_icons_check.setChecked(self.app_settings.current_settings.get("show_menu_icons", True))
        if hasattr(self, 'button_icons_check'):
            self.button_icons_check.setChecked(self.app_settings.current_settings.get("show_button_icons", False))

    def _apply_settings(self):
        """Apply settings permanently including demo theme"""
        new_settings = self._get_dialog_settings()

        # If demo theme is different, use it
        if hasattr(self, 'demo_theme_combo'):
            theme_name = self.demo_theme_combo.currentText()
            new_settings["theme"] = theme_name
            self.app_settings.current_settings["theme"] = theme_name
            print(f"🎨\n\nActive theme: {theme_name}")

        old_theme = self.app_settings.current_settings["theme"]

        self.app_settings.current_settings.update(new_settings)
        self.app_settings.save_settings()

        if new_settings["theme"] != old_theme:
            self.themeChanged.emit(new_settings["theme"])

        self.settingsChanged.emit()

        QMessageBox.information(self, "Applied", f"Settings applied successfully! 🎨\n\nActive theme: {new_settings['theme']}")

        # Apply interface settings
        self.app_settings.current_settings['debug_mode'] = self.debug_enabled_check.isChecked()
        self.app_settings.current_settings['debug_level'] = self.debug_level_combo.currentText()

        enabled_categories = []
        for category, checkbox in self.debug_categories.items():
            if checkbox.isChecked():
                enabled_categories.append(category)
        self.app_settings.current_settings['debug_categories'] = enabled_categories
        

        if hasattr(self, 'font_family_combo'):
            self.app_settings.current_settings["font_family"] = self.font_family_combo.currentText()
        if hasattr(self, 'font_size_spin'):
            self.app_settings.current_settings["font_size"] = self.font_size_spin.value()
        if hasattr(self, 'tooltips_check'):
            self.app_settings.current_settings["show_tooltips"] = self.tooltips_check.isChecked()
        if hasattr(self, 'menu_icons_check'):
            self.app_settings.current_settings["show_menu_icons"] = self.menu_icons_check.isChecked()
        if hasattr(self, 'button_icons_check'):
            self.app_settings.current_settings["show_button_icons"] = self.button_icons_check.isChecked()

        # FIXED: Debug settings with safety checks
        if hasattr(self, 'debug_enabled_check'):
            self.app_settings.current_settings['debug_mode'] = self.debug_enabled_check.isChecked()
        if hasattr(self, 'debug_level_combo'):
            self.app_settings.current_settings['debug_level'] = self.debug_level_combo.currentText()
        if hasattr(self, 'debug_categories'):
            enabled_categories = []
            for category, checkbox in self.debug_categories.items():
                if checkbox.isChecked():
                    enabled_categories.append(category)
            self.app_settings.current_settings['debug_categories'] = enabled_categories

        # Save settings
        self.app_settings.save_settings()
        
        # Emit signals
        if hasattr(self, 'themeChanged'):
            self.themeChanged.emit(self.app_settings.current_settings["theme"])
        if hasattr(self, 'settingsChanged'):
            self.settingsChanged.emit()
    
    def _ok_clicked(self):
        """OK button clicked"""
        self._apply_settings()
        self.accept()
    
    def _reset_to_defaults(self):
        """Reset to default settings"""
        self.app_settings.current_settings = self.app_settings.default_settings.copy()
        self._load_current_settings()


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
    actions_group = QGroupBox("🔧 Debug Actions")
    actions_layout = QVBoxLayout(actions_group)

    # Quick debug buttons
    buttons_layout = QHBoxLayout()

    test_debug_btn = QPushButton("🧪 Test Debug")
    test_debug_btn.setToolTip("Send a test debug message")
    test_debug_btn.clicked.connect(self._test_debug_output)
    buttons_layout.addWidget(test_debug_btn)

    debug_img_btn = QPushButton("📁 Debug IMG")
    debug_img_btn.setToolTip("Debug current IMG file (if loaded)")
    debug_img_btn.clicked.connect(self._debug_current_img)
    buttons_layout.addWidget(debug_img_btn)

    clear_log_btn = QPushButton("🗑️ Clear Log")
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
        self.parent().log_message("🧪 Debug test message - debug system working!")
        self.parent().log_message(f"🐛 [DEBUG-TEST] Debug enabled: {self.debug_enabled_check.isChecked()}")
        self.parent().log_message(f"🐛 [DEBUG-TEST] Debug level: {self.debug_level_combo.currentText()}")

        enabled_categories = [cat for cat, cb in self.debug_categories.items() if cb.isChecked()]
        self.parent().log_message(f"🐛 [DEBUG-TEST] Active categories: {', '.join(enabled_categories)}")
    else:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Debug Test", "Debug test completed!\nCheck the activity log for output.")

def _debug_current_img(self):
    """Debug current IMG file"""
    if hasattr(self.parent(), 'current_img') and self.parent().current_img:
        img = self.parent().current_img
        self.parent().log_message(f"🐛 [DEBUG-IMG] Current IMG: {img.file_path}")
        self.parent().log_message(f"🐛 [DEBUG-IMG] Entries: {len(img.entries)}")

        # Count file types
        file_types = {}
        for entry in img.entries:
            ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
            file_types[ext] = file_types.get(ext, 0) + 1

        self.parent().log_message(f"🐛 [DEBUG-IMG] File types found:")
        for ext, count in sorted(file_types.items()):
            self.parent().log_message(f"🐛 [DEBUG-IMG]   {ext}: {count} files")

        # Check table rows
        if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'table'):
            table = self.parent().gui_layout.table
            table_rows = table.rowCount()
            hidden_rows = sum(1 for row in range(table_rows) if table.isRowHidden(row))
            self.parent().log_message(f"🐛 [DEBUG-IMG] Table: {table_rows} rows, {hidden_rows} hidden")

    elif hasattr(self.parent(), 'log_message'):
        self.parent().log_message("🐛 [DEBUG-IMG] No IMG file currently loaded")
    else:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Debug IMG", "No IMG file loaded or no debug function available.")

def _clear_debug_log(self):
    """Clear the activity log"""
    if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'log'):
        self.parent().gui_layout.log.clear()
        self.parent().log_message("🗑️ Debug log cleared")
    else:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Clear Log", "Activity log cleared (if available).")

def apply_theme_to_app(app, app_settings):
    """Apply theme to entire application"""
    stylesheet = app_settings.get_stylesheet()
    app.setStyleSheet(stylesheet)


# Clean main function for testing only
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Create settings
    settings = AppSettings()
    
    # Create simple test window
    main_window = QMainWindow()
    main_window.setWindowTitle("IMG Factory Settings Test")
    main_window.setMinimumSize(400, 300)
    
    # Apply theme
    apply_theme_to_app(app, settings)
    
    # Show settings dialog
    dialog = SettingsDialog(settings, main_window)
    if dialog.exec():
        print("Settings applied")
    
    sys.exit(0)
