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
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QGroupBox, QLabel, QPushButton, QComboBox, QCheckBox,
    QSpinBox, QSlider, QLineEdit, QTextEdit, QButtonGroup,
    QRadioButton, QScrollArea, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


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
    
    def _create_ui(self):
        """Create settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Theme tab
        self.theme_tab = self._create_theme_tab()
        self.tabs.addTab(self.theme_tab, "🎨 Theme")
        
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
        """Apply current settings"""
        # Get selected theme
        for button in self.theme_buttons.buttons():
            if button.isChecked():
                self.app_settings.current_settings["theme"] = button.theme_name
                break
        
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