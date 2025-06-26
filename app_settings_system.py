# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory App Settings System - Clean Version
Settings management without demo code
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QButtonGroup, QRadioButton, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox,
    QLabel, QPushButton, QComboBox, QCheckBox, QSpinBox,
    QSlider, QGroupBox, QTabWidget, QDialog, QMessageBox,
    QFileDialog, QColorDialog, QFontDialog, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class AppSettings:
    def __init__(self):
        self.settings_file = Path("imgfactory.settings.json")  # Use correct settings file
        self.themes = {}

        # Load themes from JSON files in themes/ folder
        self._load_themes_from_files()

        # Fallback hardcoded themes if no files found
        if not self.themes:
            self._load_default_themes()

        # Default settings
        self.defaults = {
            "theme": "lightgreen",  # Default to lightgreen instead of LCARS
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
            "validate_before_creation": True
        }

        self.current_settings = self.defaults.copy()
        self.load_settings()

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

    def _load_default_themes(self):
        """Load hardcoded fallback themes"""
        print("🔄 Loading default hardcoded themes...")
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
                    "pin_highlight": "#f9e71e",
                    "button_text_color": "#ffffff",  # White text for dark theme
                    "button_text_hover": "#ffffff",
                    "button_text_pressed": "#ffffff"
                }
            },
            "lightgreen": {
                "name": "Light Green Garden",
                "description": "Fresh green theme 🌱",
                "colors": {
                    "bg_primary": "#f0fdf4",
                    "bg_secondary": "#dcfce7",
                    "bg_tertiary": "#bbf7d0",
                    "panel_bg": "#f7fee7",
                    "accent_primary": "#16a34a",
                    "accent_secondary": "#15803d",
                    "text_primary": "#14532d",
                    "text_secondary": "#166534",
                    "text_accent": "#15803d",
                    "button_normal": "#dcfce7",
                    "button_hover": "#bbf7d0",
                    "button_pressed": "#86efac",
                    "border": "#d1d5db",
                    "success": "#16a34a",
                    "warning": "#d97706",
                    "error": "#dc2626",
                    "grid": "#e5e7eb",
                    "pin_default": "#6b7280",
                    "pin_highlight": "#16a34a",
                    "action_import": "#dbeafe",
                    "action_export": "#dcfce7",
                    "action_remove": "#fee2e2",
                    "action_update": "#fef3c7",
                    "action_convert": "#f3e8ff",
                    "panel_entries": "#f0fdf4",
                    "panel_filter": "#fefce8",
                    "toolbar_bg": "#f9fafb",
                    "button_text_color": "#000000",  # Black text for light theme
                    "button_text_hover": "#000000",
                    "button_text_pressed": "#000000"
                }
            }
        }

    # KEEP all your existing methods: get_theme, get_color, save_settings, etc.
    # Just add this method:

    def get_available_themes(self):
        """Get list of available theme names"""
        return list(self.themes.keys())

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

class AppSettings:
    def __init__(self, settings_file="imgfactory.settings.json"):  # Note: .settings not _settings
        self.settings_file = settings_file
        self.defaults = {
            # Theme and appearance
            "theme": "lightgreen",
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

        self.current_settings = self.defaults.copy()
        self.load_settings()

    # ADD: Path remembering methods
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


class AppSettings:
    """Application settings manager with extended theme support"""

    def __init__(self):
        self.settings_file = Path("themer_settings.json")
        self.themes_dir = Path("themes")
        self.themes = self._load_all_themes()
        
        self.default_settings = {
            "theme": "IMG_Factory",
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
            "show_menu_icons": True,
            "show_button_icons": False,
            "show_emoji_in_buttons": False,
            "custom_button_colors": False,
            "button_import_color": "#2196f3",
            "button_export_color": "#4caf50",
            "button_remove_color": "#f44336",
            "button_update_color": "#ff9800",
            "button_convert_color": "#9c27b0",
            "button_default_color": "#0078d4"
        }
        
        self.current_settings = self.load_settings()

    def _load_all_themes(self):
        """Load themes from themes folder and built-in themes"""
        themes = {}
        
        # Load themes from files in themes/ folder
        if self.themes_dir.exists():
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                        theme_name = theme_file.stem
                        themes[theme_name] = theme_data
                except Exception as e:
                    print(f"Error loading theme {theme_file}: {e}")
        
        # Add built-in fallback themes if no files found
        if not themes:
            themes = self._get_builtin_themes()
        
        return themes

    def _get_builtin_themes(self):
        """Get built-in themes as fallback"""
        return {
            "IMG_Factory": {
                "name": "IMG Factory Professional",
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
                    "grid": "#f0f0f0",
                    "pin_default": "#757575",
                    "pin_highlight": "#2196f3",
                    "action_import": "#2196f3",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0"
                }
            },
            "IMG_Factory_Dark": {
                "name": "IMG Factory Dark Mode",
                "description": "Dark version of the IMG Factory theme 🌙📁",
                "category": "🏢 Professional",
                "author": "X-Seti",
                "version": "1.0",
                "colors": {
                    "bg_primary": "#1e1e1e",
                    "bg_secondary": "#2d2d30",
                    "bg_tertiary": "#3e3e42",
                    "panel_bg": "#383838",
                    "accent_primary": "#0078d4",
                    "accent_secondary": "#106ebe",
                    "text_primary": "#ffffff",
                    "text_secondary": "#cccccc",
                    "text_accent": "#0078d4",
                    "button_normal": "#404040",
                    "button_hover": "#505050",
                    "button_pressed": "#606060",
                    "border": "#555555",
                    "success": "#4caf50",
                    "warning": "#ff9800",
                    "error": "#f44336",
                    "grid": "#333333",
                    "pin_default": "#888888",
                    "pin_highlight": "#0078d4",
                    "action_import": "#0078d4",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0"
                }
            },
            "LCARS": {
                "name": "LCARS Interface",
                "description": "Inspired by Star Trek computer interfaces 🖖",
                "category": "🎬 Pop Culture",
                "author": "X-Seti",
                "version": "1.0",
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
                    "pin_highlight": "#f9e71e",
                    "action_import": "#3a86ff",
                    "action_export": "#06ffa5",
                    "action_remove": "#ff006e",
                    "action_update": "#ffb700",
                    "action_convert": "#9d4edd"
                }
            }
        }

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

    def refresh_themes(self):
        """Refresh themes from folder"""
        self.themes = self._load_all_themes()

    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                # Merge with defaults (in case new settings were added)
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return self.default_settings.copy()

    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get_theme_colors(self, theme_name=None):
        """Get colors for specified theme"""
        if theme_name is None:
            theme_name = self.current_settings.get("theme", "IMG_Factory")
        
        return self.themes.get(theme_name, {}).get("colors", {})

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

    def _darken_color(self, hex_color, factor=0.8):
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

    # this belongs in root/App_settings_system.py
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
        self.theme_info_label.setStyleSheet("padding: 8px; background: #f5f5f5; border-radius: 4px;")
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
            ("📂 Open IMG", "import", "Open IMG archive"),
            ("📥 Import Files", "import", "Import files to archive"),
            ("📤 Export Selected", "export", "Export selected entries"),
            ("🗑️ Remove Entry", "remove", "Remove selected entry"),
            ("🔄 Update List", "update", "Refresh entry list"),
            ("🔄 Convert Format", "convert", "Convert file format"),
            ("💾 Save Archive", None, "Save current archive"),
            ("⚙️ Settings", None, "Open settings dialog")
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

        # Enhanced sample data
        sample_data = [
            ["player.dff", "Model", "245 KB", "RW 3.6.0.3", "✅ Ready"],
            ["player.txd", "Texture", "512 KB", "RW 3.6.0.3", "✅ Ready"],
            ["vehicle.col", "Collision", "128 KB", "COL v2", "✅ Ready"],
            ["dance.ifp", "Animation", "1.2 MB", "IFP v1", "🗜️ Compressed"],
            ["mission.scm", "Script", "856 KB", "SCM v3", "🔒 Protected"]
        ]

        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.demo_table.setItem(row, col, item)

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
        self.theme_tab = self._create_theme_tab()
        self.tabs.addTab(self.theme_tab, "🎨 Themes")

        # NEW: Add demo tab
        self.demo_tab = self._create_demo_tab()
        self.tabs.addTab(self.demo_tab, "🎭 Demo")

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
    
    def _create_theme_tab(self):
        """Create theme selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection
        theme_group = QGroupBox("Choose Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_buttons = QButtonGroup()
        
        for theme_name, theme_data in self.app_settings.themes.items():
            radio = QRadioButton(theme_data.get("name", theme_name))
            radio.setToolTip(theme_data.get("description", ""))
            radio.theme_name = theme_name
            self.theme_buttons.addButton(radio)
            theme_layout.addWidget(radio)
        
        layout.addWidget(theme_group)
        layout.addStretch()
        
        return widget
    
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
        # Set theme
        current_theme = self.app_settings.current_settings.get("theme", "IMG_Factory")
        for button in self.theme_buttons.buttons():
            if hasattr(button, 'theme_name') and button.theme_name == current_theme:
                button.setChecked(True)
                break
        
        # Set interface settings
        self.font_family_combo.setCurrentText(self.app_settings.current_settings.get("font_family", "Segoe UI"))
        self.font_size_spin.setValue(self.app_settings.current_settings.get("font_size", 9))
        self.tooltips_check.setChecked(self.app_settings.current_settings.get("show_tooltips", True))
        self.menu_icons_check.setChecked(self.app_settings.current_settings.get("show_menu_icons", True))
        self.button_icons_check.setChecked(self.app_settings.current_settings.get("show_button_icons", False))
    
    def _apply_settings(self):
        """Apply settings permanently including demo theme"""
        new_settings = self._get_dialog_settings()

        # If demo theme is different, use it
        if hasattr(self, 'demo_theme_combo'):
            demo_theme = self.demo_theme_combo.currentText()
            if demo_theme != self.app_settings.current_settings["theme"]:
                new_settings["theme"] = demo_theme

        old_theme = self.app_settings.current_settings["theme"]

        self.app_settings.current_settings.update(new_settings)
        self.app_settings.save_settings()

        if new_settings["theme"] != old_theme:
            self.themeChanged.emit(new_settings["theme"])

        self.settingsChanged.emit()

        QMessageBox.information(self, "Applied", f"Settings applied successfully! 🎨\n\nActive theme: {new_settings['theme']}")

        # Apply interface settings
        self.app_settings.current_settings["font_family"] = self.font_family_combo.currentText()
        self.app_settings.current_settings["font_size"] = self.font_size_spin.value()
        self.app_settings.current_settings["show_tooltips"] = self.tooltips_check.isChecked()
        self.app_settings.current_settings["show_menu_icons"] = self.menu_icons_check.isChecked()
        self.app_settings.current_settings["show_button_icons"] = self.button_icons_check.isChecked()
        
        # Save settings
        self.app_settings.save_settings()
        
        # Emit signals
        self.themeChanged.emit(self.app_settings.current_settings["theme"])
        self.settingsChanged.emit()
    
    def _ok_clicked(self):
        """OK button clicked"""
        self._apply_settings()
        self.accept()
    
    def _reset_to_defaults(self):
        """Reset to default settings"""
        self.app_settings.current_settings = self.app_settings.default_settings.copy()
        self._load_current_settings()


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
