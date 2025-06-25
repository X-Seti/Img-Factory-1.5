#!/usr/bin/env python3
"""
X-Seti - June02,2025 - App Settings System with Extended Themes
"""

import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QWidget, QGroupBox, QComboBox, QLabel, QPushButton,
                           QSlider, QCheckBox, QSpinBox, QColorDialog, QMessageBox,
                           QGridLayout, QButtonGroup, QRadioButton, QFrame, QFontDialog,
                           QLineEdit, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QColor, QPalette, QFont


class AppSettings:
    """ application settings manager with extended theme support"""
    
    def __init__(self):
        self.settings_file = Path("themer_settings.json")
        self.themes = {
            "LCARS": {
                "name": "LCARS (Star Trek)",
                "description": "Inspired by Enterprise computer interfaces 🖖",
                "colors": {
                    "bg_primary": "#1a1a2e",
                    "bg_secondary": "#16213e", 
                    "bg_tertiary": "#0f3460",
                    "panel_bg": "#2d2d44",
                    "accent_primary": "#ff6600",
                    "accent_secondary": "#9d4edd",
                    "text_primary": "#e0e1dd",
                    "text_secondary": "#c9ada7",
                    "text_accent": "#f2cc8f",
                    "button_normal": "#3a86ff",
                    "button_hover": "#4895ff",
                    "button_pressed": "#2563eb",
                    "border": "#577590",
                    "success": "#06ffa5",
                    "warning": "#ffb700",
                    "error": "#ff006e",
                    "grid": "#403d58",
                    "pin_default": "#c0c0c0",
                    "pin_highlight": "#f9e71e"
                }
            },
            
            "Tea_and_Toast": {
                "name": "Tea & Toast Morning",
                "description": "Warm browns and purples for cozy mornings ☕🍞",
                "colors": {
                    "bg_primary": "#2d1b20",
                    "bg_secondary": "#3d2b30",
                    "bg_tertiary": "#4a3540",
                    "panel_bg": "#5d4e75",
                    "accent_primary": "#8b5a83",
                    "accent_secondary": "#d4a574",
                    "text_primary": "#f4e4c1",
                    "text_secondary": "#e6d7b0",
                    "text_accent": "#f2b705",
                    "button_normal": "#7b68ee",
                    "button_hover": "#9370db",
                    "button_pressed": "#6a4c93",
                    "border": "#8b7355",
                    "success": "#90c695",
                    "warning": "#f4a261",
                    "error": "#e76f51",
                    "grid": "#5a4a5a",
                    "pin_default": "#d4a574",
                    "pin_highlight": "#f2cc8f"
                }
            },
            
            "Deep_Purple": {
                "name": "Deep Purple Space",
                "description": "Rich purples with cosmic blues 🟣✨",
                "colors": {
                    "bg_primary": "#1a0d26",
                    "bg_secondary": "#2d1b3d",
                    "bg_tertiary": "#3d2850",
                    "panel_bg": "#4a3366",
                    "accent_primary": "#8e44ad",
                    "accent_secondary": "#3498db",
                    "text_primary": "#f8f9fa",
                    "text_secondary": "#e9ecef",
                    "text_accent": "#bb86fc",
                    "button_normal": "#6f42c1",
                    "button_hover": "#7952cc",
                    "button_pressed": "#5a32a3",
                    "border": "#6c5ce7",
                    "success": "#00b894",
                    "warning": "#fdcb6e",
                    "error": "#e84393",
                    "grid": "#4a3366",
                    "pin_default": "#a29bfe",
                    "pin_highlight": "#fd79a8"
                }
            },
            
            "Matrix": {
                "name": "Matrix Digital Rain",
                "description": "Follow the white rabbit... 🐰💊",
                "colors": {
                    "bg_primary": "#000000",
                    "bg_secondary": "#001100",
                    "bg_tertiary": "#002200",
                    "panel_bg": "#0d1f0d",
                    "accent_primary": "#00ff00",
                    "accent_secondary": "#00cc00",
                    "text_primary": "#00ff00",
                    "text_secondary": "#00cc00",
                    "text_accent": "#33ff33",
                    "button_normal": "#003300",
                    "button_hover": "#004400",
                    "button_pressed": "#002200",
                    "border": "#00aa00",
                    "success": "#00ff00",
                    "warning": "#ffff00",
                    "error": "#ff0000",
                    "grid": "#002200",
                    "pin_default": "#00cc00",
                    "pin_highlight": "#00ffff"
                }
            },
            
            "Borg": {
                "name": "Borg Collective",
                "description": "Resistance is futile. You will be assimilated. 🤖",
                "colors": {
                    "bg_primary": "#0a0a0a",
                    "bg_secondary": "#1a1a1a",
                    "bg_tertiary": "#2a2a2a",
                    "panel_bg": "#1f1f1f",
                    "accent_primary": "#00ff00",
                    "accent_secondary": "#ff0000",
                    "text_primary": "#c0c0c0",
                    "text_secondary": "#a0a0a0",
                    "text_accent": "#00ff00",
                    "button_normal": "#333333",
                    "button_hover": "#404040",
                    "button_pressed": "#202020",
                    "border": "#666666",
                    "success": "#00ff00",
                    "warning": "#ffff00",
                    "error": "#ff0000",
                    "grid": "#333333",
                    "pin_default": "#808080",
                    "pin_highlight": "#00ff00"
                }
            },
            
            "Klingon": {
                "name": "Klingon Empire",
                "description": "Qapla'! Today is a good day to code! ⚔️",
                "colors": {
                    "bg_primary": "#1a0000",
                    "bg_secondary": "#2a0a0a",
                    "bg_tertiary": "#3a1010",
                    "panel_bg": "#2a1a1a",
                    "accent_primary": "#ff0000",
                    "accent_secondary": "#cc0000",
                    "text_primary": "#ffdddd",
                    "text_secondary": "#ccbbbb",
                    "text_accent": "#ff6666",
                    "button_normal": "#4a0000",
                    "button_hover": "#660000",
                    "button_pressed": "#330000",
                    "border": "#aa3333",
                    "success": "#ffaa00",
                    "warning": "#ff6600",
                    "error": "#ff0000",
                    "grid": "#441111",
                    "pin_default": "#aa4444",
                    "pin_highlight": "#ffaa00"
                }
            },
            
            "Dominion": {
                "name": "The Dominion",
                "description": "Order through submission. Victory is life! 👁️",
                "colors": {
                    "bg_primary": "#1a1a0a",
                    "bg_secondary": "#2a2a1a",
                    "bg_tertiary": "#3a3a2a",
                    "panel_bg": "#2a2a1f",
                    "accent_primary": "#ccaa00",
                    "accent_secondary": "#aa8800",
                    "text_primary": "#ffffcc",
                    "text_secondary": "#ddddaa",
                    "text_accent": "#ffcc44",
                    "button_normal": "#4a4a00",
                    "button_hover": "#666600",
                    "button_pressed": "#333300",
                    "border": "#888855",
                    "success": "#88cc00",
                    "warning": "#ff8800",
                    "error": "#cc4400",
                    "grid": "#444433",
                    "pin_default": "#aaaa55",
                    "pin_highlight": "#ffcc00"
                }
            },
            
            "Knight_Rider": {
                "name": "Knight Rider KITT",
                "description": "A shadowy flight into the dangerous world of... coding! 🚗",
                "colors": {
                    "bg_primary": "#000000",
                    "bg_secondary": "#111111",
                    "bg_tertiary": "#222222",
                    "panel_bg": "#1a1a1a",
                    "accent_primary": "#ff0000",
                    "accent_secondary": "#cc0000",
                    "text_primary": "#ff4444",
                    "text_secondary": "#cc3333",
                    "text_accent": "#ff6666",
                    "button_normal": "#330000",
                    "button_hover": "#550000",
                    "button_pressed": "#220000",
                    "border": "#666666",
                    "success": "#00ff00",
                    "warning": "#ffaa00",
                    "error": "#ff0000",
                    "grid": "#333333",
                    "pin_default": "#aa3333",
                    "pin_highlight": "#ff0000"
                }
            },
            
            "Amiga_MUI": {
                "name": "Amiga MUI (Magic User Interface)",
                "description": "The classic Amiga look with 3D beveled buttons! 💾",
                "colors": {
                    "bg_primary": "#c0c0c0",
                    "bg_secondary": "#b0b0b0",
                    "bg_tertiary": "#a0a0a0",
                    "panel_bg": "#c8c8c8",
                    "accent_primary": "#0066cc",
                    "accent_secondary": "#004499",
                    "text_primary": "#000000",
                    "text_secondary": "#333333",
                    "text_accent": "#0066cc",
                    "button_normal": "#d0d0d0",
                    "button_hover": "#e0e0e0",
                    "button_pressed": "#b0b0b0",
                    "border": "#808080",
                    "success": "#008800",
                    "warning": "#cc6600",
                    "error": "#cc0000",
                    "grid": "#aaaaaa",
                    "pin_default": "#666666",
                    "pin_highlight": "#0066cc"
                }
            },
            
            "Classic_Dark": {
                "name": "Classic Dark",
                "description": "Professional dark theme with blue accents",
                "colors": {
                    "bg_primary": "#2b2b2b",
                    "bg_secondary": "#3c3c3c",
                    "bg_tertiary": "#4d4d4d",
                    "panel_bg": "#383838",
                    "accent_primary": "#0078d4",
                    "accent_secondary": "#106ebe",
                    "text_primary": "#ffffff",
                    "text_secondary": "#cccccc",
                    "text_accent": "#569cd6",
                    "button_normal": "#0e639c",
                    "button_hover": "#1177bb",
                    "button_pressed": "#094771",
                    "border": "#555555",
                    "success": "#4ec9b0",
                    "warning": "#ffd700",
                    "error": "#f14c4c",
                    "grid": "#444444",
                    "pin_default": "#c0c0c0",
                    "pin_highlight": "#ffd700"
                }
            },
            
            "Light_Professional": {
                "name": "Light Professional",
                "description": "Clean light theme for daytime work",
                "colors": {
                    "bg_primary": "#ffffff",
                    "bg_secondary": "#f5f5f5",
                    "bg_tertiary": "#e0e0e0",
                    "panel_bg": "#f0f0f0",
                    "accent_primary": "#0066cc",
                    "accent_secondary": "#0052a3",
                    "text_primary": "#000000",
                    "text_secondary": "#333333",
                    "text_accent": "#0066cc",
                    "button_normal": "#0078d4",
                    "button_hover": "#106ebe",
                    "button_pressed": "#005a9e",
                    "border": "#cccccc",
                    "success": "#107c10",
                    "warning": "#ff8c00",
                    "error": "#d13438",
                    "grid": "#dddddd",
                    "pin_default": "#666666",
                    "pin_highlight": "#ff8c00"
                }
            },
            
            "IMG_Factory": {
                "name": "IMG Factory Professional",
                "description": "Clean, organized interface inspired by IMG Factory 📁",
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
                    "grid": "#f0f0f0",
                    "pin_default": "#757575",
                    "pin_highlight": "#2196f3",
                    "action_import": "#2196f3",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0",
                    "panel_entries": "#e8f5e8",
                    "panel_filter": "#fff3e0",
                    "toolbar_bg": "#fafafa"
                }
            }
        }
        
        #  default settings
        self.defaults = {
            "theme": "LCARS",
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
            "button_default_color": "#0078d4"
        }
        
        self.current_settings = self.defaults.copy()
        self.load_settings()
    
    def get_theme(self, theme_name=None):
        """Get theme colors"""
        if theme_name is None:
            theme_name = self.current_settings["theme"]
        return self.themes.get(theme_name, self.themes["LCARS"])
    
    def get_color(self, color_name, theme_name=None):
        """Get specific color from current theme"""
        theme = self.get_theme(theme_name)
        return theme["colors"].get(color_name, "#ffffff")
    
    def get_qcolor(self, color_name, theme_name=None):
        """Get QColor object for specific color"""
        hex_color = self.get_color(color_name, theme_name)
        return QColor(hex_color)
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    for key, value in loaded.items():
                        if key in self.defaults:
                            self.current_settings[key] = value
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.current_settings = self.defaults.copy()
        self.save_settings()
    
    def get_font(self, font_type="default"):
        """Get QFont object for specific font type"""
        if font_type == "panel":
            family = self.current_settings["panel_font_family"]
            size = self.current_settings["panel_font_size"]
            weight = self.current_settings["panel_font_weight"]
        elif font_type == "button":
            family = self.current_settings["button_font_family"]
            size = self.current_settings["button_font_size"]
            weight = self.current_settings["button_font_weight"]
        else:
            family = self.current_settings["font_family"]
            size = self.current_settings["font_size"]
            weight = self.current_settings["font_weight"]
        
        font = QFont(family, size)
        if weight == "bold":
            font.setBold(True)
        elif weight == "light":
            font.setWeight(QFont.Weight.Light)
        
        return font
    
    def get_stylesheet(self):
        """Generate complete stylesheet for current theme"""
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
            
            /* Default Buttons */
            QPushButton {{
                background-color: {button_colors["default"]};
                border: 2px solid {colors["accent_primary"]};
                border-radius: 6px;
                padding: 8px 16px;
                color: {colors["text_primary"]};
                font: {button_font};
                font-weight: {self.current_settings["button_font_weight"]};
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {colors["button_hover"]};
                border-color: {colors["accent_secondary"]};
            }}
            
            QPushButton:pressed {{
                background-color: {colors["button_pressed"]};
            }}
            
            /* Action-specific button styling */
            QPushButton[action-type="import"] {{
                background-color: {button_colors["import"]};
                border-color: {button_colors["import"]};
                color: white;
            }}
            
            QPushButton[action-type="export"] {{
                background-color: {button_colors["export"]};
                border-color: {button_colors["export"]};
                color: white;
            }}
            
            QPushButton[action-type="remove"] {{
                background-color: {button_colors["remove"]};
                border-color: {button_colors["remove"]};
                color: white;
            }}
            
            QPushButton[action-type="update"] {{
                background-color: {button_colors["update"]};
                border-color: {button_colors["update"]};
                color: white;
            }}
            
            QPushButton[action-type="convert"] {{
                background-color: {button_colors["convert"]};
                border-color: {button_colors["convert"]};
                color: white;
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
            
            /* Line Edits */
            QLineEdit {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                padding: 6px;
                color: {colors["text_primary"]};
                font: {main_font};
            }}
            
            QLineEdit:focus {{
                border-color: {colors["accent_primary"]};
            }}
            
            /* Check Boxes and Radio Buttons */
            QCheckBox {{
                color: {colors["text_primary"]};
                spacing: 8px;
                font: {main_font};
            }}
            
            QRadioButton {{
                color: {colors["text_primary"]};
                spacing: 8px;
                font: {main_font};
            }}
            
            /* Labels */
            QLabel {{
                color: {colors["text_primary"]};
                background: transparent;
                font: {main_font};
            }}
            
            /* Special theme-specific styling */
            {"" if self.current_settings["theme"] not in ["LCARS", "Matrix", "Borg", "Knight_Rider", "Amiga_MUI"] else self._get_special_theme_styles(colors)}
        """
    
    def _get_special_theme_styles(self, colors):
        """Get special styling for specific themes"""
        theme = self.current_settings["theme"]
        
        if theme == "LCARS":
            return f'''
            QPushButton {{
                border-top-left-radius: 15px;
                border-bottom-right-radius: 15px;
                border-top-right-radius: 3px;
                border-bottom-left-radius: 3px;
            }}
            
            QGroupBox {{
                border-top-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }}
            '''
        
        elif theme == "Matrix":
            return f'''
            QWidget {{
                font-family: "Courier New", monospace;
            }}
            
            QPushButton {{
                border: 1px solid {colors["accent_primary"]};
                border-radius: 2px;
                text-transform: uppercase;
            }}
            
            QPushButton:hover {{
                text-shadow: 0 0 5px {colors["accent_primary"]};
            }}
            '''
        
        elif theme == "Borg":
            return f'''
            QPushButton {{
                border: 2px solid {colors["border"]};
                border-radius: 0px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            QGroupBox {{
                border-radius: 0px;
                border: 2px solid {colors["border"]};
            }}
            '''
        
        elif theme == "Knight_Rider":
            return f'''
            QPushButton {{
                border: 2px solid {colors["accent_primary"]};
                border-radius: 4px;
                text-transform: uppercase;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                box-shadow: 0 0 10px {colors["accent_primary"]};
            }}
            '''
        
        elif theme == "Amiga_MUI":
            return f'''
            QPushButton {{
                border: 2px outset {colors["border"]};
                border-radius: 2px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["button_hover"]}, stop:1 {colors["button_normal"]});
            }}
            
            QPushButton:pressed {{
                border: 2px inset {colors["border"]};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["button_normal"]}, stop:1 {colors["button_hover"]});
            }}
            
            QGroupBox {{
                border: 2px inset {colors["border"]};
                border-radius: 2px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors["panel_bg"]}, stop:1 {colors["bg_secondary"]});
            }}
            '''

class SettingsDialog(QDialog):
    """ settings dialog with font controls and button customization"""
    
    settingsChanged = pyqtSignal()
    themeChanged = pyqtSignal(str)
    
    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.setWindowTitle("App Editor Settings - Live Long and Prosper 🖖")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self._create_ui()
        self._load_current_settings()
        
    def _create_ui(self):
        """Create the enhanced settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Theme tab
        self.theme_tab = self._create_theme_tab()
        self.tabs.addTab(self.theme_tab, "🎨 Themes")
        
        # Font tab (new)
        self.font_tab = self._create_font_tab()
        self.tabs.addTab(self.font_tab, "🔤 Fonts")
        
        # Button colors tab (new)
        self.button_tab = self._create_button_tab()
        self.tabs.addTab(self.button_tab, "🎨 Button Colors")
        
        # Interface tab
        self.interface_tab = self._create_interface_tab()
        self.tabs.addTab(self.interface_tab, "⚙️ Interface")
        
        # Editor tab
        self.editor_tab = self._create_editor_tab()
        self.tabs.addTab(self.editor_tab, "✏️ Editor")
        
        # Advanced tab
        self.advanced_tab = self._create_advanced_tab()
        self.tabs.addTab(self.advanced_tab, "🚀 Advanced")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self._preview_settings)
        button_layout.addWidget(preview_btn)
        
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
    
    def _create_theme_tab(self):
        """Create enhanced theme selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area for themes
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Theme selection
        theme_group = QGroupBox("Choose Your Universe 🌌")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_buttons = QButtonGroup()
        
        # Group themes by category
        theme_categories = {
            "🖖 Star Trek Universe": ["LCARS", "Borg", "Klingon", "Dominion"],
            "☕ Personal Favorites": ["Tea_and_Toast", "Deep_Purple"],
            "🎬 Pop Culture": ["Matrix", "Knight_Rider"],
            "💻 Computer Classics": ["Amiga_MUI"],
            "🏢 Professional": ["Classic_Dark", "Light_Professional", "IMG_Factory"]
        }
        
        for category, theme_names in theme_categories.items():
            cat_label = QLabel(category)
            cat_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #666; margin-top: 10px;")
            theme_layout.addWidget(cat_label)
            
            for theme_name in theme_names:
                if theme_name in self.app_settings.themes:
                    theme_data = self.app_settings.themes[theme_name]
                    radio = QRadioButton(theme_data["name"])
                    radio.setToolTip(theme_data["description"])
                    radio.theme_name = theme_name
                    self.theme_buttons.addButton(radio)
                    theme_layout.addWidget(radio)
                    
                    # Add description
                    desc_label = QLabel(f"   {theme_data['description']}")
                    desc_label.setStyleSheet("color: #888; font-style: italic; margin-left: 20px;")
                    theme_layout.addWidget(desc_label)
        
        scroll_layout.addWidget(theme_group)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Theme preview
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.theme_preview = QLabel("Select a theme to see preview")
        self.theme_preview.setMinimumHeight(120)
        self.theme_preview.setStyleSheet("""
            border: 2px solid #666;
            border-radius: 8px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a2e, stop:1 #16213e);
            color: #e0e1dd;
            font-size: 12px;
        """)
        preview_layout.addWidget(self.theme_preview)
        
        layout.addWidget(preview_group)
        
        # Connect theme selection
        self.theme_buttons.buttonClicked.connect(self._theme_selected)
        
        return widget
    
    def _create_font_tab(self):
        """Create font customization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Main application font
        main_font_group = QGroupBox("Main Application Font")
        main_font_layout = QGridLayout(main_font_group)
        
        main_font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Consolas", "Ubuntu", "Roboto", "Open Sans"])
        main_font_layout.addWidget(self.font_combo, 0, 1)
        
        main_font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        main_font_layout.addWidget(self.font_size_spin, 1, 1)
        
        main_font_layout.addWidget(QLabel("Font Weight:"), 2, 0)
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.addItems(["normal", "bold", "light"])
        main_font_layout.addWidget(self.font_weight_combo, 2, 1)
        
        font_preview_btn = QPushButton("🔤 Choose Font...")
        font_preview_btn.clicked.connect(self._choose_main_font)
        main_font_layout.addWidget(font_preview_btn, 3, 0, 1, 2)
        
        layout.addWidget(main_font_group)
        
        # Panel font
        panel_font_group = QGroupBox("Panel Text Font")
        panel_font_layout = QGridLayout(panel_font_group)
        
        panel_font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.panel_font_combo = QComboBox()
        self.panel_font_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Consolas", "Ubuntu", "Roboto", "Open Sans"])
        panel_font_layout.addWidget(self.panel_font_combo, 0, 1)
        
        panel_font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.panel_font_size_spin = QSpinBox()
        self.panel_font_size_spin.setRange(8, 16)
        panel_font_layout.addWidget(self.panel_font_size_spin, 1, 1)
        
        panel_font_layout.addWidget(QLabel("Font Weight:"), 2, 0)
        self.panel_font_weight_combo = QComboBox()
        self.panel_font_weight_combo.addItems(["normal", "bold", "light"])
        panel_font_layout.addWidget(self.panel_font_weight_combo, 2, 1)
        
        panel_font_preview_btn = QPushButton("🔤 Choose Panel Font...")
        panel_font_preview_btn.clicked.connect(self._choose_panel_font)
        panel_font_layout.addWidget(panel_font_preview_btn, 3, 0, 1, 2)
        
        layout.addWidget(panel_font_group)
        
        # Button font
        button_font_group = QGroupBox("Button Text Font")
        button_font_layout = QGridLayout(button_font_group)
        
        button_font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.button_font_combo = QComboBox()
        self.button_font_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Consolas", "Ubuntu", "Roboto", "Open Sans"])
        button_font_layout.addWidget(self.button_font_combo, 0, 1)
        
        button_font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.button_font_size_spin = QSpinBox()
        self.button_font_size_spin.setRange(8, 16)
        button_font_layout.addWidget(self.button_font_size_spin, 1, 1)
        
        button_font_layout.addWidget(QLabel("Font Weight:"), 2, 0)
        self.button_font_weight_combo = QComboBox()
        self.button_font_weight_combo.addItems(["normal", "bold", "light"])
        button_font_layout.addWidget(self.button_font_weight_combo, 2, 1)
        
        button_font_preview_btn = QPushButton("🔤 Choose Button Font...")
        button_font_preview_btn.clicked.connect(self._choose_button_font)
        button_font_layout.addWidget(button_font_preview_btn, 3, 0, 1, 2)
        
        layout.addWidget(button_font_group)
        
        # Font preview
        preview_group = QGroupBox("Font Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.font_preview_label = QLabel("The quick brown fox jumps over the lazy dog.\n1234567890 !@#$%^&*()")
        self.font_preview_label.setStyleSheet("""
            border: 1px solid #ccc;
            padding: 10px;
            background: white;
            color: black;
            min-height: 40px;
        """)
        preview_layout.addWidget(self.font_preview_label)
        
        layout.addWidget(preview_group)
        
        # Connect font changes
        self.font_combo.currentTextChanged.connect(self._update_font_preview)
        self.font_size_spin.valueChanged.connect(self._update_font_preview)
        self.font_weight_combo.currentTextChanged.connect(self._update_font_preview)
        
        layout.addStretch()
        return widget
    
    def _create_button_tab(self):
        """Create button color customization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Custom colors toggle
        custom_group = QGroupBox("Custom Button Colors")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_button_colors_check = QCheckBox("Enable custom button colors")
        self.custom_button_colors_check.setToolTip("Override theme button colors with custom ones")
        self.custom_button_colors_check.toggled.connect(self._toggle_custom_colors)
        custom_layout.addWidget(self.custom_button_colors_check)
        
        layout.addWidget(custom_group)
        
        # Color selection
        self.colors_group = QGroupBox("Button Action Colors")
        colors_layout = QGridLayout(self.colors_group)
        
        # Create color buttons
        self.color_buttons = {}
        color_types = [
            ("import", "📥 Import Actions", "#2196f3"),
            ("export", "📤 Export Actions", "#4caf50"),
            ("remove", "🗑️ Remove Actions", "#f44336"),
            ("update", "🔄 Update Actions", "#ff9800"),
            ("convert", "🔄 Convert Actions", "#9c27b0"),
            ("default", "⚙️ Default Buttons", "#0078d4")
        ]
        
        for i, (action_type, label, default_color) in enumerate(color_types):
            colors_layout.addWidget(QLabel(label), i, 0)
            
            color_btn = QPushButton("")
            color_btn.setMinimumSize(60, 30)
            color_btn.setStyleSheet(f"background-color: {default_color}; border: 2px solid #333;")
            color_btn.action_type = action_type
            color_btn.clicked.connect(lambda checked, btn=color_btn: self._choose_button_color(btn))
            colors_layout.addWidget(color_btn, i, 1)
            
            reset_btn = QPushButton("Reset")
            reset_btn.clicked.connect(lambda checked, btn=color_btn, default=default_color: self._reset_button_color(btn, default))
            colors_layout.addWidget(reset_btn, i, 2)
            
            self.color_buttons[action_type] = color_btn
        
        layout.addWidget(self.colors_group)
        
        # Button preview
        preview_group = QGroupBox("Button Preview")
        preview_layout = QHBoxLayout(preview_group)
        
        # Create sample buttons
        sample_buttons = [
            ("📥 Import", "import"),
            ("📤 Export", "export"),
            ("🗑️ Remove", "remove"),
            ("🔄 Update", "update"),
            ("🔄 Convert", "convert"),
            ("⚙️ Default", "default")
        ]
        
        self.preview_buttons = {}
        for text, action_type in sample_buttons:
            btn = QPushButton(text)
            btn.setProperty("action-type", action_type)
            btn.setMinimumHeight(35)
            preview_layout.addWidget(btn)
            self.preview_buttons[action_type] = btn
        
        layout.addWidget(preview_group)
        
        # Initially disable custom colors
        self.colors_group.setEnabled(False)
        
        layout.addStretch()
        return widget
    
    def _create_interface_tab(self):
        """Create interface settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Panel settings
        panel_group = QGroupBox("Panel Layout")
        panel_layout = QVBoxLayout(panel_group)
        
        self.collapsible_check = QCheckBox("Collapsible panel sections")
        panel_layout.addWidget(self.collapsible_check)
        
        self.tooltips_check = QCheckBox("Show tooltips")
        panel_layout.addWidget(self.tooltips_check)
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Panel Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(95)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("95%")
        opacity_layout.addWidget(self.opacity_label)
        panel_layout.addLayout(opacity_layout)
        
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        layout.addWidget(panel_group)
        
        # Animation settings
        anim_group = QGroupBox("Visual Effects")
        anim_layout = QVBoxLayout(anim_group)
        
        self.animations_check = QCheckBox("Enable animations")
        anim_layout.addWidget(self.animations_check)
        
        self.sound_check = QCheckBox("Sound effects")
        anim_layout.addWidget(self.sound_check)
        
        self.lcars_sounds_check = QCheckBox("LCARS computer sounds 🖖")
        self.lcars_sounds_check.setToolTip("Authentic Star Trek computer sounds")
        anim_layout.addWidget(self.lcars_sounds_check)
        
        layout.addWidget(anim_group)
        
        layout.addStretch()
        return widget
    
    def _create_editor_tab(self):
        """Create editor settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grid settings
        grid_group = QGroupBox("Grid & Snapping")
        grid_layout = QGridLayout(grid_group)
        
        self.show_grid_check = QCheckBox("Show grid")
        grid_layout.addWidget(self.show_grid_check, 0, 0, 1, 2)
        
        self.show_perfboard_check = QCheckBox("Show perfboard pattern")
        grid_layout.addWidget(self.show_perfboard_check, 1, 0, 1, 2)
        
        self.snap_check = QCheckBox("Snap to grid")
        grid_layout.addWidget(self.snap_check, 2, 0, 1, 2)
        
        grid_layout.addWidget(QLabel("Grid Size:"), 3, 0)
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(1, 20)
        grid_layout.addWidget(self.grid_size_spin, 3, 1)
        
        layout.addWidget(grid_group)
        
        # Pin settings
        pin_group = QGroupBox("Pin Labels")
        pin_layout = QGridLayout(pin_group)
        
        pin_layout.addWidget(QLabel("Pin Label Size:"), 0, 0)
        self.pin_size_spin = QSpinBox()
        self.pin_size_spin.setRange(6, 16)
        pin_layout.addWidget(self.pin_size_spin, 0, 1)
        
        layout.addWidget(pin_group)
        
        # Zoom settings
        zoom_group = QGroupBox("Zoom & Navigation")
        zoom_layout = QGridLayout(zoom_group)
        
        zoom_layout.addWidget(QLabel("Zoom Sensitivity:"), 0, 0)
        self.zoom_sensitivity_spin = QSpinBox()
        self.zoom_sensitivity_spin.setRange(110, 150)
        self.zoom_sensitivity_spin.setSuffix("%")
        zoom_layout.addWidget(self.zoom_sensitivity_spin, 0, 1)
        
        layout.addWidget(zoom_group)
        
        layout.addStretch()
        return widget
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QGridLayout(perf_group)
        
        self.auto_save_check = QCheckBox("Auto-save changes")
        perf_layout.addWidget(self.auto_save_check, 0, 0, 1, 2)
        
        self.remember_state_check = QCheckBox("Remember window state")
        perf_layout.addWidget(self.remember_state_check, 1, 0, 1, 2)
        
        perf_layout.addWidget(QLabel("Max Undo Levels:"), 2, 0)
        self.undo_levels_spin = QSpinBox()
        self.undo_levels_spin.setRange(10, 200)
        perf_layout.addWidget(self.undo_levels_spin, 2, 1)
        
        layout.addWidget(perf_group)
        
        # Future features
        future_group = QGroupBox("Future Features (Coming Soon)")
        future_layout = QVBoxLayout(future_group)
        
        self.voice_commands_check = QCheckBox("Voice commands (\"Computer, show components\")")
        self.voice_commands_check.setEnabled(False)
        self.voice_commands_check.setToolTip("Star Trek-style voice control - Coming in v3.0!")
        future_layout.addWidget(self.voice_commands_check)
        
        layout.addWidget(future_group)
        
        # Export/Import settings
        export_group = QGroupBox("Settings Management")
        export_layout = QHBoxLayout(export_group)
        
        export_btn = QPushButton("📤 Export Settings")
        export_btn.clicked.connect(self._export_settings)
        export_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 Import Settings")
        import_btn.clicked.connect(self._import_settings)
        export_layout.addWidget(import_btn)
        
        layout.addWidget(export_group)
        
        layout.addStretch()
        return widget
    
    def _theme_selected(self, button):
        """Handle theme selection"""
        theme_name = button.theme_name
        theme = self.app_settings.themes[theme_name]
        
        # Update preview with theme-specific styling
        colors = theme["colors"]
        
        # Special preview text based on theme
        preview_texts = {
            "LCARS": "🖖 LCARS Interface Active\n\nWelcome to the Enterprise computer system.\nMake it so!\n\nStatus: Operational\nUser: Captain Picard",
            "Tea_and_Toast": "☕ Good morning!\n\nTime for tea and toast while coding.\nWarm browns and purples create\na cozy coding atmosphere.\n\nPerfect for early morning sessions! 🍞",
            "Deep_Purple": "🟣 Deep Purple Space\n\nRich purples with cosmic blues.\nPerfect for your favorite color!\n\nLet the purple guide your creativity. ✨",
            "Matrix": "🐰 Welcome to the Matrix\n\nThere is no spoon.\nChoose: Red pill or blue pill?\n\nFollow the white rabbit...\nWake up, Neo.",
            "Borg": "🤖 RESISTANCE IS FUTILE\n\nYOU WILL BE ASSIMILATED.\nWe are the Borg.\n\nYour biological and technological\ndistinctiveness will be added to our own.",
            "Klingon": "⚔️ Qapla'!\n\nToday is a good day to code!\nHonor and glory to the Empire!\n\nKahless guide your development!",
            "Dominion": "👁️ Victory is life.\n\nOrder through submission.\nThe Dominion brings peace\nthrough control.\n\nObey the Founders.",
            "Knight_Rider": "🚗 KITT Online\n\nMichael, I'm scanning for bugs\nin your code.\n\nA shadowy flight into the\ndangerous world of development.",
            "Amiga_MUI": "💾 Amiga Workbench\n\nMagic User Interface active.\nClassic 3D beveled look.\n\nBringing back the 90s\ncomputing experience!",
        }
        
        preview_text = preview_texts.get(theme_name, f"""
Theme: {theme["name"]}

{theme["description"]}

Experience the unique styling
of this theme!
        """)
        
        preview_style = f"""
            border: 2px solid {colors["border"]};
            border-radius: 8px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors["bg_primary"]}, stop:1 {colors["bg_secondary"]});
            color: {colors["text_primary"]};
            font-size: 12px;
            font-weight: bold;
        """
        
        self.theme_preview.setStyleSheet(preview_style)
        self.theme_preview.setText(preview_text)
    
    def _choose_main_font(self):
        """Open font dialog for main font"""
        current_font = QFont(
            self.font_combo.currentText(),
            self.font_size_spin.value()
        )
        if self.font_weight_combo.currentText() == "bold":
            current_font.setBold(True)
        
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.font_combo.setCurrentText(font.family())
            self.font_size_spin.setValue(font.pointSize())
            self.font_weight_combo.setCurrentText("bold" if font.bold() else "normal")
            self._update_font_preview()
    
    def _choose_panel_font(self):
        """Open font dialog for panel font"""
        current_font = QFont(
            self.panel_font_combo.currentText(),
            self.panel_font_size_spin.value()
        )
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.panel_font_combo.setCurrentText(font.family())
            self.panel_font_size_spin.setValue(font.pointSize())
            self.panel_font_weight_combo.setCurrentText("bold" if font.bold() else "normal")
    
    def _choose_button_font(self):
        """Open font dialog for button font"""
        current_font = QFont(
            self.button_font_combo.currentText(),
            self.button_font_size_spin.value()
        )
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.button_font_combo.setCurrentText(font.family())
            self.button_font_size_spin.setValue(font.pointSize())
            self.button_font_weight_combo.setCurrentText("bold" if font.bold() else "normal")
    
    def _update_font_preview(self):
        """Update font preview"""
        font_family = self.font_combo.currentText()
        font_size = self.font_size_spin.value()
        font_weight = self.font_weight_combo.currentText()
        
        weight_str = "bold" if font_weight == "bold" else "normal"
        
        self.font_preview_label.setStyleSheet(f"""
            border: 1px solid #ccc;
            padding: 10px;
            background: white;
            color: black;
            min-height: 40px;
            font-family: {font_family};
            font-size: {font_size}pt;
            font-weight: {weight_str};
        """)
    
    def _toggle_custom_colors(self, enabled):
        """Toggle custom button colors"""
        self.colors_group.setEnabled(enabled)
        if enabled:
            self._update_preview_buttons()
    
    def _choose_button_color(self, button):
        """Open color dialog for button"""
        current_color = button.palette().button().color()
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #333;")
            self._update_preview_buttons()
    
    def _reset_button_color(self, button, default_color):
        """Reset button color to default"""
        button.setStyleSheet(f"background-color: {default_color}; border: 2px solid #333;")
        self._update_preview_buttons()
    
    def _update_preview_buttons(self):
        """Update preview button colors"""
        if self.custom_button_colors_check.isChecked():
            for action_type, color_btn in self.color_buttons.items():
                if action_type in self.preview_buttons:
                    # Extract color from style
                    style = color_btn.styleSheet()
                    color_match = style.split("background-color: ")[1].split(";")[0]
                    self.preview_buttons[action_type].setStyleSheet(
                        f"background-color: {color_match}; color: white; font-weight: bold; padding: 5px;"
                    )
    
    def _load_current_settings(self):
        """Load current settings into dialog controls"""
        settings = self.app_settings.current_settings
        
        # Theme tab
        for button in self.theme_buttons.buttons():
            if button.theme_name == settings["theme"]:
                button.setChecked(True)
                self._theme_selected(button)
                break
        
        # Font tab
        self.font_combo.setCurrentText(settings["font_family"])
        self.font_size_spin.setValue(settings["font_size"])
        self.font_weight_combo.setCurrentText(settings["font_weight"])
        self.panel_font_combo.setCurrentText(settings["panel_font_family"])
        self.panel_font_size_spin.setValue(settings["panel_font_size"])
        self.panel_font_weight_combo.setCurrentText(settings["panel_font_weight"])
        self.button_font_combo.setCurrentText(settings["button_font_family"])
        self.button_font_size_spin.setValue(settings["button_font_size"])
        self.button_font_weight_combo.setCurrentText(settings["button_font_weight"])
        self._update_font_preview()
        
        # Button colors tab
        self.custom_button_colors_check.setChecked(settings["custom_button_colors"])
        self._toggle_custom_colors(settings["custom_button_colors"])
        
        # Set button colors
        color_settings = {
            "import": settings["button_import_color"],
            "export": settings["button_export_color"],
            "remove": settings["button_remove_color"],
            "update": settings["button_update_color"],
            "convert": settings["button_convert_color"],
            "default": settings["button_default_color"]
        }
        
        for action_type, color in color_settings.items():
            if action_type in self.color_buttons:
                self.color_buttons[action_type].setStyleSheet(
                    f"background-color: {color}; border: 2px solid #333;"
                )
        
        # Interface tab
        self.collapsible_check.setChecked(settings["collapsible_panels"])
        self.tooltips_check.setChecked(settings["show_tooltips"])
        self.opacity_slider.setValue(settings["panel_opacity"])
        self.opacity_label.setText(f"{settings['panel_opacity']}%")
        self.animations_check.setChecked(settings["animations"])
        self.sound_check.setChecked(settings["sound_effects"])
        self.lcars_sounds_check.setChecked(settings["lcars_sounds"])
        
          # Editor tab
        self.show_grid_check.setChecked(settings["show_grid"])
        self.show_perfboard_check.setChecked(settings["show_perfboard"])
        self.snap_check.setChecked(settings["snap_to_grid"])
        self.grid_size_spin.setValue(settings["grid_size"])
        self.pin_size_spin.setValue(settings["pin_label_size"])
        zoom_percent = int(settings["zoom_sensitivity"] * 100)
        self.zoom_sensitivity_spin.setValue(zoom_percent)

        # Advanced tab
        self.auto_save_check.setChecked(settings["auto_save"])
        self.remember_state_check.setChecked(settings["remember_window_state"])
        self.undo_levels_spin.setValue(settings["max_undo_levels"])
        self.voice_commands_check.setChecked(settings["voice_commands"])


    def _get_dialog_settings(self):
        """Get settings from dialog controls"""
        selected_theme = None
        for button in self.theme_buttons.buttons():
            if button.isChecked():
                selected_theme = button.theme_name
                break

        return {
            "theme": selected_theme or "LCARS",
            "font_family": self.font_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "panel_opacity": self.opacity_slider.value(),
            "show_tooltips": self.tooltips_check.isChecked(),
            "auto_save": self.auto_save_check.isChecked(),
            "grid_size": self.grid_size_spin.value(),
            "snap_to_grid": self.snap_check.isChecked(),
            "show_grid": self.show_grid_check.isChecked(),
            "show_perfboard": self.show_perfboard_check.isChecked(),
            "pin_label_size": self.pin_size_spin.value(),
            "zoom_sensitivity": self.zoom_sensitivity_spin.value() / 100.0,
            "max_undo_levels": self.undo_levels_spin.value(),
            "collapsible_panels": self.collapsible_check.isChecked(),
            "remember_window_state": self.remember_state_check.isChecked(),
            "voice_commands": self.voice_commands_check.isChecked(),
            "animations": self.animations_check.isChecked(),
            "sound_effects": self.sound_check.isChecked(),
            "lcars_sounds": self.lcars_sounds_check.isChecked()
        }

    def _preview_settings(self):
        """Preview settings without applying permanently"""
        new_settings = self._get_dialog_settings()
        old_theme = self.app_settings.current_settings["theme"]

        # Temporarily apply settings
        self.app_settings.current_settings.update(new_settings)

        # Emit theme change signal
        if new_settings["theme"] != old_theme:
            self.themeChanged.emit(new_settings["theme"])

        self.settingsChanged.emit()

        # Show preview message
        QMessageBox.information(self, "Preview",
            f"Preview applied!\n\n"
            f"Theme: {self.app_settings.themes[new_settings['theme']]['name']}\n"
            f"Font: {new_settings['font_family']} {new_settings['font_size']}pt\n"
            f"Grid: {'On' if new_settings['show_grid'] else 'Off'}\n\n"
            f"Click OK to make permanent, or Cancel to revert.")

    def _apply_settings(self):
        """Apply settings permanently"""
        new_settings = self._get_dialog_settings()
        old_theme = self.app_settings.current_settings["theme"]

        self.app_settings.current_settings.update(new_settings)
        self.app_settings.save_settings()

        if new_settings["theme"] != old_theme:
            self.themeChanged.emit(new_settings["theme"])

        self.settingsChanged.emit()

        QMessageBox.information(self, "Applied",
            "Settings applied successfully! 🖖\n\n"
            "Live long and prosper with your new theme!")

    def _ok_clicked(self):
        """Handle OK button - apply and close"""
        self._apply_settings()
        self.accept()

    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\n\n"
            "This will change your theme back to LCARS and reset all preferences.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.app_settings.reset_to_defaults()
            self._load_current_settings()
            self.themeChanged.emit("LCARS")
            self.settingsChanged.emit()

            QMessageBox.information(self, "Reset Complete",
                "Settings reset to defaults.\n\n"
                "Welcome back to the LCARS interface! 🖖")

    def _export_settings(self):
        """Export settings to file"""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "themer_settings.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.app_settings.current_settings, f, indent=2)
                QMessageBox.information(self, "Export Successful",
                    f"Settings exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed",
                    f"Failed to export settings:\n{str(e)}")

    def _import_settings(self):
        """Import settings from file"""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "",
            "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    imported_settings = json.load(f)

                # Validate imported settings
                valid_keys = set(self.app_settings.defaults.keys())
                imported_keys = set(imported_settings.keys())

                if not imported_keys.issubset(valid_keys):
                    QMessageBox.warning(self, "Invalid Settings",
                        "The imported file contains invalid settings.")
                    return

                # Apply imported settings
                self.app_settings.current_settings.update(imported_settings)
                self.app_settings.save_settings()
                self._load_current_settings()

                self.themeChanged.emit(self.app_settings.current_settings["theme"])
                self.settingsChanged.emit()

                QMessageBox.information(self, "Import Successful",
                    f"Settings imported from:\n{filename}")

            except Exception as e:
                QMessageBox.critical(self, "Import Failed",
                    f"Failed to import settings:\n{str(e)}")

def apply_theme_to_app(app, app_settings):
    """Apply theme to entire application"""
    stylesheet = app_settings.get_stylesheet()
    app.setStyleSheet(stylesheet)


# Example usage and integration
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    # Create settings
    settings = AppSettings()

    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("Settings Demo - Star Trek LCARS Theme 🖖")
    main_window.setMinimumSize(800, 600)

    # Create central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # Add some demo widgets
    from PyQt6.QtWidgets import QGroupBox, QPushButton, QComboBox, QCheckBox, QSlider

    # IMG Factory style demo
    img_factory_group = QGroupBox("IMG Factory Style Demo 📁")
    img_factory_layout = QVBoxLayout(img_factory_group)

    # Entries section (like IMG Factory)
    entries_layout = QHBoxLayout()

    import_btn = QPushButton("📥 Import")
    import_btn.setProperty("action-type", "import")
    entries_layout.addWidget(import_btn)

    import_via_btn = QPushButton("📥 Import via")
    import_via_btn.setProperty("action-type", "import")
    entries_layout.addWidget(import_via_btn)

    update_btn = QPushButton("🔄 Update list")
    update_btn.setProperty("action-type", "update")
    entries_layout.addWidget(update_btn)

    img_factory_layout.addLayout(entries_layout)

    # Export section
    export_layout = QHBoxLayout()

    export_btn = QPushButton("📤 Export")
    export_btn.setProperty("action-type", "export")
    export_layout.addWidget(export_btn)

    export_via_btn = QPushButton("📤 Export via")
    export_via_btn.setProperty("action-type", "export")
    export_layout.addWidget(export_via_btn)

    quick_export_btn = QPushButton("⚡ Quick Export")
    quick_export_btn.setProperty("action-type", "export")
    export_layout.addWidget(quick_export_btn)

    img_factory_layout.addLayout(export_layout)

    # Remove/Actions section
    actions_layout = QHBoxLayout()

    remove_btn = QPushButton("🗑️ Remove")
    remove_btn.setProperty("action-type", "remove")
    actions_layout.addWidget(remove_btn)

    remove_via_btn = QPushButton("🗑️ Remove via")
    remove_via_btn.setProperty("action-type", "remove")
    actions_layout.addWidget(remove_via_btn)

    dump_btn = QPushButton("💾 Dump")
    dump_btn.setProperty("action-type", "update")
    actions_layout.addWidget(dump_btn)

    img_factory_layout.addLayout(actions_layout)

    # Convert section
    convert_layout = QHBoxLayout()

    convert_btn = QPushButton("🔄 Convert")
    convert_btn.setProperty("action-type", "convert")
    convert_layout.addWidget(convert_btn)

    replace_btn = QPushButton("↔️ Replace")
    replace_btn.setProperty("action-type", "convert")
    convert_layout.addWidget(replace_btn)

    convert_layout.addStretch()

    img_factory_layout.addLayout(convert_layout)

    layout.addWidget(img_factory_group)

    # Original demo (for other themes)
    demo_group = QGroupBox("Star Trek Demo - Tea & Toast Approved ☕🍞")
    demo_layout = QVBoxLayout(demo_group)

    demo_layout.addWidget(QPushButton("🖖 Make It So!"))
    demo_layout.addWidget(QPushButton("☕ Earl Grey, Hot"))
    demo_layout.addWidget(QPushButton("🟣 Engage Purple Mode"))

    combo = QComboBox()
    combo.addItems(["Starfleet", "Romulan", "Klingon", "Borg"])
    demo_layout.addWidget(combo)

    demo_layout.addWidget(QCheckBox("🌟 Enable Warp Drive"))
    demo_layout.addWidget(QCheckBox("☕ Auto-serve Tea"))

    demo_layout.addWidget(QSlider(Qt.Orientation.Horizontal))

    layout.addWidget(demo_group)

    # Settings button
    settings_btn = QPushButton("⚙️ Open Settings")
    layout.addWidget(settings_btn)

    def open_settings():
        dialog = SettingsDialog(settings, main_window)
        dialog.themeChanged.connect(lambda: apply_theme_to_app(app, settings))
        dialog.settingsChanged.connect(lambda: apply_theme_to_app(app, settings))
        dialog.exec()

    settings_btn.clicked.connect(open_settings)

    # Apply initial theme
    apply_theme_to_app(app, settings)

    main_window.show()

    print("🖖 Live Long and Prosper! LCARS Theme System Active")
    print("☕ Tea and Toast mode available")
    print("🟣 Deep Purple themes included")
    print("⚙️ Click settings to customize your experience")

    sys.exit(app.exec())
