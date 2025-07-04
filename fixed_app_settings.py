#this belongs in utils/app_settings_system.py - version 55
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
        # Get the directory where this file is located
        current_file_dir = Path(__file__).parent

        # FIXED: Set paths based on where we are
        if current_file_dir.name == "utils":
            # We're in utils/, so themes are in ../themes/
            self.themes_dir = current_file_dir.parent / "themes"
            self.settings_file = current_file_dir.parent / "imgfactory.settings.json"
        else:
            # We're in root, so themes are in ./themes/
            self.themes_dir = current_file_dir / "themes"
            self.settings_file = current_file_dir / "imgfactory.settings.json"

        # Debug: Show what we found
        print(f"🎨 Looking for themes in: {self.themes_dir}")
        print(f"📁 Themes directory exists: {self.themes_dir.exists()}")
        if self.themes_dir.exists():
            theme_files = list(self.themes_dir.glob("*.json"))
            print(f"📄 Found {len(theme_files)} theme files")
            for theme_file in theme_files:
                print(f"  - {theme_file.name}")

        # FIXED: Load themes first, then settings
        self.themes = self._load_all_themes()

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
            # Layout settings
            "left_panel_width": 400,
            "right_panel_width": 300,
            "table_row_height": 25,
            "widget_spacing": 5,
            "layout_margins": 5,
            # Window settings
            "remember_window_size": True,
            "remember_window_position": True,
            "maximize_on_startup": False,
            "always_on_top": False,
            # Performance settings
            "smooth_scrolling": True,
            "lazy_loading": True,
            "cache_previews": True,
            # Notifications
            "show_progress_notifications": True,
            "sound_notifications": False,
            "status_bar_updates": True,
            # Visual effects
            "enable_animations": True,
            "enable_shadows": True,
            "enable_transparency": True,
            "rounded_corners": True,
            # Table settings
            "auto_resize_columns": True,
            # Debug settings
            "debug_mode": False,
            "debug_level": "INFO",
            "debug_categories": ["IMG_LOADING", "TABLE_POPULATION", "BUTTON_ACTIONS", "FILE_OPERATIONS"]
        }

        # FIXED: Load settings after themes and defaults are set
        self.current_settings = self.load_settings()

        # Initialize debug settings
        self.debug = DebugSettings(self)

    def _get_builtin_themes(self):
        """Get built-in fallback themes"""
        return {
            "IMG_Factory": {
                "name": "IMG Factory Default",
                "description": "Default IMG Factory theme",
                "category": "Built-in",
                "author": "X-Seti",
                "version": "1.5",
                "colors": {
                    "primary": "#2196f3",
                    "secondary": "#ff9800",
                    "background": "#f5f5f5",
                    "surface": "#ffffff",
                    "text": "#212121",
                    "text_secondary": "#757575",
                    "accent": "#4caf50",
                    "warning": "#ff9800",
                    "error": "#f44336",
                    "success": "#4caf50",
                    "info": "#2196f3"
                }
            },
            "lightgreen": {
                "name": "Light Green",
                "description": "Fresh light green theme",
                "category": "Light",
                "author": "X-Seti",
                "version": "1.5",
                "colors": {
                    "primary": "#4caf50",
                    "secondary": "#8bc34a",
                    "background": "#f1f8e9",
                    "surface": "#ffffff",
                    "text": "#1b5e20",
                    "text_secondary": "#388e3c",
                    "accent": "#cddc39",
                    "warning": "#ff9800",
                    "error": "#f44336",
                    "success": "#4caf50",
                    "info": "#2196f3"
                }
            },
            "LCARS": {
                "name": "LCARS Interface",
                "description": "Star Trek LCARS style interface",
                "category": "Sci-Fi",
                "author": "X-Seti",
                "version": "1.5",
                "colors": {
                    "primary": "#ff9900",
                    "secondary": "#cc99ff",
                    "background": "#000000",
                    "surface": "#333333",
                    "text": "#ff9900",
                    "text_secondary": "#cc99ff",
                    "accent": "#9999ff",
                    "warning": "#ff6600",
                    "error": "#ff3333",
                    "success": "#99ff99",
                    "info": "#99ccff"
                }
            }
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

        # REMOVED: Don't load settings here - they're loaded in __init__

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
            theme_name = self.current_settings.get("theme", "lightgreen")

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

    def get_stylesheet(self, theme_name=None):
        """Generate complete Qt stylesheet from theme"""
        colors = self.get_theme_colors(theme_name)
        
        if not colors:
            return ""

        # Generate comprehensive stylesheet
        stylesheet = f"""
        /* Main Application Styling */
        QMainWindow {{
            background-color: {colors.get('background', '#f5f5f5')};
            color: {colors.get('text', '#212121')};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text', '#212121')};
            border-bottom: 1px solid {colors.get('primary', '#2196f3')};
        }}

        QMenuBar::item {{
            background: transparent;
            padding: 4px 8px;
        }}

        QMenuBar::item:selected {{
            background-color: {colors.get('primary', '#2196f3')};
            color: white;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {colors.get('primary', '#2196f3')};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {self._darken_color(colors.get('primary', '#2196f3'))};
        }}

        QPushButton:pressed {{
            background-color: {self._darken_color(colors.get('primary', '#2196f3'), 0.8)};
        }}

        /* Action-specific button colors */
        QPushButton[action-type="import"] {{
            background-color: {colors.get('info', '#2196f3')};
        }}

        QPushButton[action-type="export"] {{
            background-color: {colors.get('success', '#4caf50')};
        }}

        QPushButton[action-type="remove"] {{
            background-color: {colors.get('error', '#f44336')};
        }}

        QPushButton[action-type="update"] {{
            background-color: {colors.get('warning', '#ff9800')};
        }}

        QPushButton[action-type="convert"] {{
            background-color: {colors.get('secondary', '#ff9800')};
        }}

        /* Tables */
        QTableWidget {{
            background-color: {colors.get('surface', '#ffffff')};
            alternate-background-color: {colors.get('background', '#f5f5f5')};
            color: {colors.get('text', '#212121')};
            gridline-color: {colors.get('text_secondary', '#757575')};
            selection-background-color: {colors.get('primary', '#2196f3')};
            selection-color: white;
        }}

        QHeaderView::section {{
            background-color: {colors.get('primary', '#2196f3')};
            color: white;
            padding: 8px;
            border: 1px solid {self._darken_color(colors.get('primary', '#2196f3'))};
            font-weight: bold;
        }}

        /* Text Edit / Log */
        QTextEdit {{
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text', '#212121')};
            border: 1px solid {colors.get('text_secondary', '#757575')};
            border-radius: 4px;
        }}

        /* Group Boxes */
        QGroupBox {{
            font-weight: bold;
            color: {colors.get('text', '#212121')};
            border: 2px solid {colors.get('primary', '#2196f3')};
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            background-color: {colors.get('background', '#f5f5f5')};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {colors.get('primary', '#2196f3')};
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text', '#212121')};
            border: 1px solid {colors.get('text_secondary', '#757575')};
            border-radius: 4px;
            padding: 4px;
        }}

        QComboBox:hover {{
            border-color: {colors.get('primary', '#2196f3')};
        }}

        /* Labels */
        QLabel {{
            color: {colors.get('text', '#212121')};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text', '#212121')};
            border-top: 1px solid {colors.get('primary', '#2196f3')};
        }}

        /* Dialogs */
        QDialog {{
            background-color: {colors.get('background', '#f5f5f5')};
            color: {colors.get('text', '#212121')};
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {colors.get('background', '#f5f5f5')};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors.get('primary', '#2196f3')};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self._darken_color(colors.get('primary', '#2196f3'))};
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

    def get_available_themes(self) -> dict:
        """Get all available themes with refresh option"""
        return self.themes

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
            fallback_theme = list(self.themes.keys())[0] if self.themes else "lightgreen"
            return self.themes.get(fallback_theme, {"colors": {}})

    def get_theme_data(self, theme_name: str) -> dict:
        """Get complete theme data"""
        if theme_name in self.themes:
            return self.themes[theme_name]
        else:
            print(f"⚠️ Theme '{theme_name}' not found, using fallback")
            fallback_theme = list(self.themes.keys())[0] if self.themes else "lightgreen"
            return self.themes.get(fallback_theme, {"colors": {}})

    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.current_settings = self.default_settings.copy()
        self.save_settings()

    def _clear_debug_log(self):
        """Clear the activity log"""
        if hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'log'):
            self.parent().gui_layout.log.clear()
            self.parent().log_message("🗑️ Debug log cleared")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Clear Log", "Activity log cleared (if available).")

        
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
        """Create the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different settings categories
        tab_widget = QTabWidget()
        
        # Theme tab
        theme_tab = self._create_theme_tab()
        tab_widget.addTab(theme_tab, "🎨 Themes")
        
        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        tab_widget.addTab(appearance_tab, "✨ Appearance")
        
        # Behavior tab
        behavior_tab = self._create_behavior_tab()
        tab_widget.addTab(behavior_tab, "⚙️ Behavior")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # OK/Cancel buttons
        ok_btn = QPushButton("✅ OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_theme_tab(self):
        """Create theme selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection group
        theme_group = QGroupBox("🎨 Theme Selection")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme combo box
        self.theme_combo = QComboBox()
        for theme_name, theme_data in self.app_settings.themes.items():
            display_name = theme_data.get("name", theme_name)
            self.theme_combo.addItem(f"{display_name}", theme_name)
        
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.theme_combo)
        
        # Theme info display
        self.theme_info = QTextEdit()
        self.theme_info.setMaximumHeight(100)
        self.theme_info.setReadOnly(True)
        theme_layout.addWidget(QLabel("Theme Information:"))
        theme_layout.addWidget(self.theme_info)
        
        layout.addWidget(theme_group)
        
        # Refresh themes button
        refresh_btn = QPushButton("🔄 Refresh Themes")
        refresh_btn.clicked.connect(self._refresh_themes)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_appearance_tab(self):
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font settings
        font_group = QGroupBox("🔤 Font Settings")
        font_layout = QGridLayout(font_group)
        
        # Font family
        font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Times New Roman", "Consolas"])
        font_layout.addWidget(self.font_family_combo, 0, 1)
        
        # Font size
        font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
        # Visual effects
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        self.animations_check = QCheckBox("Enable animations")
        self.shadows_check = QCheckBox("Enable shadows")
        self.transparency_check = QCheckBox("Enable transparency")
        self.rounded_corners_check = QCheckBox("Rounded corners")
        
        effects_layout.addWidget(self.animations_check)
        effects_layout.addWidget(self.shadows_check)
        effects_layout.addWidget(self.transparency_check)
        effects_layout.addWidget(self.rounded_corners_check)
        
        layout.addWidget(effects_group)
        layout.addStretch()
        
        return widget
    
    def _create_behavior_tab(self):
        """Create behavior settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Window behavior
        window_group = QGroupBox("🪟 Window Behavior")
        window_layout = QVBoxLayout(window_group)
        
        self.remember_size_check = QCheckBox("Remember window size")
        self.remember_position_check = QCheckBox("Remember window position")
        self.maximize_on_startup_check = QCheckBox("Maximize on startup")
        self.always_on_top_check = QCheckBox("Always on top")
        
        window_layout.addWidget(self.remember_size_check)
        window_layout.addWidget(self.remember_position_check)
        window_layout.addWidget(self.maximize_on_startup_check)
        window_layout.addWidget(self.always_on_top_check)
        
        layout.addWidget(window_group)
        
        # Performance settings
        performance_group = QGroupBox("⚡ Performance")
        performance_layout = QVBoxLayout(performance_group)
        
        self.smooth_scrolling_check = QCheckBox("Enable smooth scrolling")
        self.lazy_loading_check = QCheckBox("Enable lazy loading for large files")
        self.cache_previews_check = QCheckBox("Cache file previews")
        
        performance_layout.addWidget(self.smooth_scrolling_check)
        performance_layout.addWidget(self.lazy_loading_check)
        performance_layout.addWidget(self.cache_previews_check)
        
        layout.addWidget(performance_group)
        
        # Notifications
        notifications_group = QGroupBox("🔔 Notifications")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.show_tooltips_check = QCheckBox("Show tooltips")
        self.show_progress_check = QCheckBox("Show progress notifications")
        self.sound_notifications_check = QCheckBox("Enable sound notifications")
        self.status_bar_updates_check = QCheckBox("Show updates in status bar")
        
        notifications_layout.addWidget(self.show_tooltips_check)
        notifications_layout.addWidget(self.show_progress_check)
        notifications_layout.addWidget(self.sound_notifications_check)
        notifications_layout.addWidget(self.status_bar_updates_check)
        
        layout.addWidget(notifications_group)
        layout.addStretch()
        
        return widget
    
    def _load_current_settings(self):
        """Load current settings into the dialog"""
        settings = self.app_settings.current_settings
        
        # Theme
        theme = settings.get("theme", "lightgreen")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Font settings
        self.font_family_combo.setCurrentText(settings.get("font_family", "Segoe UI"))
        self.font_size_spin.setValue(settings.get("font_size", 9))
        
        # Window behavior
        self.remember_size_check.setChecked(settings.get("remember_window_size", True))
        self.remember_position_check.setChecked(settings.get("remember_window_position", True))
        self.maximize_on_startup_check.setChecked(settings.get("maximize_on_startup", False))
        self.always_on_top_check.setChecked(settings.get("always_on_top", False))
        
        # Performance
        self.smooth_scrolling_check.setChecked(settings.get("smooth_scrolling", True))
        self.lazy_loading_check.setChecked(settings.get("lazy_loading", True))
        self.cache_previews_check.setChecked(settings.get("cache_previews", True))
        
        # Notifications
        self.show_tooltips_check.setChecked(settings.get("show_tooltips", True))
        self.show_progress_check.setChecked(settings.get("show_progress_notifications", True))
        self.sound_notifications_check.setChecked(settings.get("sound_notifications", False))
        self.status_bar_updates_check.setChecked(settings.get("status_bar_updates", True))
        
        # Visual effects
        self.animations_check.setChecked(settings.get("enable_animations", True))
        self.shadows_check.setChecked(settings.get("enable_shadows", True))
        self.transparency_check.setChecked(settings.get("enable_transparency", True))
        self.rounded_corners_check.setChecked(settings.get("rounded_corners", True))
        
        # Update theme info
        self._update_theme_info()
    
    def _on_theme_changed(self):
        """Handle theme change"""
        self._update_theme_info()
        
        # Preview theme immediately
        theme_name = self.theme_combo.currentData()
        if theme_name:
            self.themeChanged.emit(theme_name)
    
    def _update_theme_info(self):
        """Update theme information display"""
        theme_name = self.theme_combo.currentData()
        if theme_name and theme_name in self.app_settings.themes:
            theme_data = self.app_settings.themes[theme_name]
            info_text = f"""
Name: {theme_data.get('name', theme_name)}
Description: {theme_data.get('description', 'No description')}
Author: {theme_data.get('author', 'Unknown')}
Version: {theme_data.get('version', '1.0')}
Category: {theme_data.get('category', 'Uncategorized')}
Colors: {len(theme_data.get('colors', {}))} defined
            """.strip()
            self.theme_info.setText(info_text)
        else:
            self.theme_info.setText("No theme information available")
    
    def _refresh_themes(self):
        """Refresh themes from disk"""
        current_theme = self.theme_combo.currentData()
        
        # Refresh themes
        self.app_settings.refresh_themes()
        
        # Update combo box
        self.theme_combo.clear()
        for theme_name, theme_data in self.app_settings.themes.items():
            display_name = theme_data.get("name", theme_name)
            self.theme_combo.addItem(f"{display_name}", theme_name)
        
        # Try to restore selection
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        QMessageBox.information(self, "Themes Refreshed", 
                              f"Reloaded {len(self.app_settings.themes)} themes from disk")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "This will reset all settings to their default values.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset app settings to defaults
            self.app_settings.reset_to_defaults()
            
            # Reload the dialog with default values
            self._load_current_settings()
            
            QMessageBox.information(
                self,
                "Reset Complete",
                "All settings have been reset to defaults!"
            )
    
    def accept(self):
        """Save settings and close dialog"""
        # Collect all settings
        settings = self.app_settings.current_settings
        
        # Theme
        settings["theme"] = self.theme_combo.currentData()
        
        # Font settings
        settings["font_family"] = self.font_family_combo.currentText()
        settings["font_size"] = self.font_size_spin.value()
        
        # Window behavior
        settings["remember_window_size"] = self.remember_size_check.isChecked()
        settings["remember_window_position"] = self.remember_position_check.isChecked()
        settings["maximize_on_startup"] = self.maximize_on_startup_check.isChecked()
        settings["always_on_top"] = self.always_on_top_check.isChecked()
        
        # Performance
        settings["smooth_scrolling"] = self.smooth_scrolling_check.isChecked()
        settings["lazy_loading"] = self.lazy_loading_check.isChecked()
        settings["cache_previews"] = self.cache_previews_check.isChecked()
        
        # Notifications
        settings["show_tooltips"] = self.show_tooltips_check.isChecked()
        settings["show_progress_notifications"] = self.show_progress_check.isChecked()
        settings["sound_notifications"] = self.sound_notifications_check.isChecked()
        settings["status_bar_updates"] = self.status_bar_updates_check.isChecked()
        
        # Visual effects
        settings["enable_animations"] = self.animations_check.isChecked()
        settings["enable_shadows"] = self.shadows_check.isChecked()
        settings["enable_transparency"] = self.transparency_check.isChecked()
        settings["rounded_corners"] = self.rounded_corners_check.isChecked()
        
        # Save to file
        self.app_settings.save_settings()
        
        # Emit signals
        self.settingsChanged.emit()
        
        super().accept()
    
    def reject(self):
        """Cancel and restore original settings"""
        self.app_settings.current_settings = self.original_settings.copy()
        super().reject()

    def refresh_themes_in_dialog(self):
        """Refresh themes in settings dialog"""
        if hasattr(self, 'theme_combo'):
            current_theme = self.theme_combo.currentData()

            # Refresh themes from disk
            self.app_settings.refresh_themes()

            # Update combo box
            self.theme_combo.clear()
            for theme_name, theme_data in self.app_settings.themes.items():
                display_name = theme_data.get("name", theme_name)
                self.theme_combo.addItem(f"{display_name}", theme_name)

            # Try to restore previous selection
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

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