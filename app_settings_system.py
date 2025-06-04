#!/usr/bin/env python3
"""
X-Seti - June02,2025 - Application Settings System with LCARS Theme Support
Complete settings management with Star Trek LCARS theme for our purple-loving, tea-drinking user! 🖖☕🟣
"""

import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QWidget, QGroupBox, QComboBox, QLabel, QPushButton,
                           QSlider, QCheckBox, QSpinBox, QColorDialog, QMessageBox,
                           QGridLayout, QButtonGroup, QRadioButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QColor, QPalette, QFont


class AppSettings:
    """Application settings manager with theme support"""
    
    def __init__(self):
        self.settings_file = Path("chip_editor_settings.json")
        self.themes = {
            "LCARS": {
                "name": "LCARS (Star Trek)",
                "description": "Inspired by Enterprise computer interfaces 🖖",
                "colors": {
                    "bg_primary": "#1a1a2e",      # Deep space blue
                    "bg_secondary": "#16213e",     # Panel dark blue  
                    "bg_tertiary": "#0f3460",      # Darker panel blue
                    "panel_bg": "#2d2d44",         # Control panel background
                    "accent_primary": "#ff6600",   # LCARS orange
                    "accent_secondary": "#9d4edd", # LCARS purple (for you!)
                    "text_primary": "#e0e1dd",     # Light gray text
                    "text_secondary": "#c9ada7",   # Muted text
                    "text_accent": "#f2cc8f",      # Yellow highlights
                    "button_normal": "#3a86ff",    # Blue buttons
                    "button_hover": "#4895ff",     # Lighter blue hover
                    "button_pressed": "#2563eb",   # Darker blue pressed
                    "border": "#577590",           # Subtle borders
                    "success": "#06ffa5",          # LCARS green
                    "warning": "#ffb700",          # LCARS amber
                    "error": "#ff006e",            # LCARS red
                    "grid": "#403d58",             # Grid lines
                    "pin_default": "#c0c0c0",      # Default pin color
                    "pin_highlight": "#f9e71e"     # Pin highlight
                }
            },
            
            "Tea_and_Toast": {
                "name": "Tea & Toast Morning",
                "description": "Warm browns and purples for cozy mornings ☕🍞",
                "colors": {
                    "bg_primary": "#2d1b20",       # Dark tea brown
                    "bg_secondary": "#3d2b30",     # Medium brown
                    "bg_tertiary": "#4a3540",      # Lighter brown
                    "panel_bg": "#5d4e75",         # Purple-brown panels
                    "accent_primary": "#8b5a83",   # Tea purple
                    "accent_secondary": "#d4a574", # Toast golden
                    "text_primary": "#f4e4c1",     # Cream text
                    "text_secondary": "#e6d7b0",   # Light brown text
                    "text_accent": "#f2b705",      # Golden accent
                    "button_normal": "#7b68ee",    # Medium purple
                    "button_hover": "#9370db",     # Light purple
                    "button_pressed": "#6a4c93",   # Dark purple
                    "border": "#8b7355",           # Toast crust brown
                    "success": "#90c695",          # Mint green
                    "warning": "#f4a261",          # Honey
                    "error": "#e76f51",            # Tea spill red
                    "grid": "#5a4a5a",             # Subtle grid
                    "pin_default": "#d4a574",      # Toast colored pins
                    "pin_highlight": "#f2cc8f"     # Butter yellow
                }
            },
            
            "Deep_Purple": {
                "name": "Deep Purple Space",
                "description": "Rich purples with cosmic blues 🟣✨",
                "colors": {
                    "bg_primary": "#1a0d26",       # Deep purple space
                    "bg_secondary": "#2d1b3d",     # Medium purple
                    "bg_tertiary": "#3d2850",      # Lighter purple
                    "panel_bg": "#4a3366",         # Purple panels
                    "accent_primary": "#8e44ad",   # Bright purple
                    "accent_secondary": "#3498db", # Cosmic blue
                    "text_primary": "#f8f9fa",     # Pure white text
                    "text_secondary": "#e9ecef",   # Light gray
                    "text_accent": "#bb86fc",      # Purple accent
                    "button_normal": "#6f42c1",    # Purple buttons
                    "button_hover": "#7952cc",     # Lighter purple
                    "button_pressed": "#5a32a3",   # Dark purple
                    "border": "#6c5ce7",           # Purple borders
                    "success": "#00b894",          # Teal success
                    "warning": "#fdcb6e",          # Golden warning
                    "error": "#e84393",            # Pink error
                    "grid": "#4a3366",             # Purple grid
                    "pin_default": "#a29bfe",      # Light purple pins
                    "pin_highlight": "#fd79a8"     # Pink highlight
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
                    "bg_primary": "#ffffff",           # Pure white main background
                    "bg_secondary": "#f8f9fa",        # Very light gray panels
                    "bg_tertiary": "#e9ecef",         # Light gray sections
                    "panel_bg": "#f1f3f4",            # Panel backgrounds
                    "accent_primary": "#1976d2",      # Professional blue
                    "accent_secondary": "#1565c0",    # Darker blue
                    "text_primary": "#212529",        # Dark gray text
                    "text_secondary": "#495057",      # Medium gray text
                    "text_accent": "#1976d2",         # Blue accent text
                    "button_normal": "#e3f2fd",       # Light blue buttons
                    "button_hover": "#bbdefb",        # Medium blue hover
                    "button_pressed": "#90caf9",      # Darker blue pressed
                    "border": "#dee2e6",              # Light gray borders
                    "success": "#4caf50",             # Green for success/export
                    "warning": "#ff9800",             # Orange for warnings
                    "error": "#f44336",               # Red for errors/remove
                    "grid": "#f0f0f0",                # Very light grid
                    "pin_default": "#757575",         # Gray pins
                    "pin_highlight": "#2196f3",       # Blue highlight
                    
                    # IMG Factory specific colors
                    "action_import": "#2196f3",       # Blue for import actions
                    "action_export": "#4caf50",       # Green for export actions
                    "action_remove": "#f44336",       # Red for remove actions
                    "action_update": "#ff9800",       # Orange for update actions
                    "action_convert": "#9c27b0",      # Purple for convert actions
                    "panel_entries": "#e8f5e8",       # Light green for entries panel
                    "panel_filter": "#fff3e0",        # Light orange for filter panel
                    "toolbar_bg": "#fafafa"           # Toolbar background
                }
            }
        }
        
        # Default settings
        self.defaults = {
            "theme": "LCARS",
            "font_family": "Segoe UI",
            "font_size": 9,
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
            "panel_layout": "left",  # left, right, floating
            "collapsible_panels": True,
            "remember_window_state": True,
            "voice_commands": False,  # For future "Computer, show components"
            "animations": True,
            "sound_effects": False,
            "lcars_sounds": False     # Authentic Star Trek sounds
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
                    # Merge with defaults to handle new settings
                    for key, value in loaded.items():
                        if key in self.defaults:
                            self.current_settings[key] = value
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.current_settings = self.defaults.copy()
        self.save_settings()
    
    def get_stylesheet(self):
        """Generate complete stylesheet for current theme"""
        theme = self.get_theme()
        colors = theme["colors"]
        
        return f"""
            /* Main Window and Widgets */
            QMainWindow {{
                background-color: {colors["bg_primary"]};
                color: {colors["text_primary"]};
            }}
            
            QWidget {{
                background-color: {colors["bg_primary"]};
                color: {colors["text_primary"]};
                font-family: {self.current_settings["font_family"]};
                font-size: {self.current_settings["font_size"]}pt;
            }}
            
            /* Panels and Group Boxes */
            QGroupBox {{
                background-color: {colors["panel_bg"]};
                border: 2px solid {colors["border"]};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                font-weight: bold;
                color: {colors["text_accent"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {colors["accent_primary"]};
                font-weight: bold;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {colors["button_normal"]};
                border: 2px solid {colors["accent_primary"]};
                border-radius: 6px;
                padding: 8px 16px;
                color: {colors["text_primary"]};
                font-weight: bold;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {colors["button_hover"]};
                border-color: {colors["accent_secondary"]};
            }}
            
            QPushButton:pressed {{
                background-color: {colors["button_pressed"]};
            }}
            
            QPushButton:disabled {{
                background-color: {colors["bg_tertiary"]};
                color: {colors["text_secondary"]};
                border-color: {colors["border"]};
            }}
            
            /* Combo Boxes */
            QComboBox {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                padding: 4px 8px;
                color: {colors["text_primary"]};
                min-height: 20px;
            }}
            
            QComboBox:hover {{
                border-color: {colors["accent_primary"]};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors["text_primary"]};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["accent_primary"]};
                selection-background-color: {colors["accent_primary"]};
                color: {colors["text_primary"]};
            }}
            
            /* Spin Boxes */
            QSpinBox {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                padding: 4px;
                color: {colors["text_primary"]};
            }}
            
            QSpinBox:hover {{
                border-color: {colors["accent_primary"]};
            }}
            
            /* Check Boxes and Radio Buttons */
            QCheckBox {{
                color: {colors["text_primary"]};
                spacing: 8px;
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
            
            QRadioButton {{
                color: {colors["text_primary"]};
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {colors["border"]};
                border-radius: 8px;
                background-color: {colors["bg_secondary"]};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {colors["accent_primary"]};
                border-color: {colors["accent_primary"]};
            }}
            
            /* Sliders */
            QSlider::groove:horizontal {{
                border: 1px solid {colors["border"]};
                height: 6px;
                background: {colors["bg_tertiary"]};
                border-radius: 3px;
            }}
            
            QSlider::handle:horizontal {{
                background: {colors["accent_primary"]};
                border: 2px solid {colors["accent_secondary"]};
                width: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {colors["accent_secondary"]};
            }}
            
            /* Labels */
            QLabel {{
                color: {colors["text_primary"]};
                background: transparent;
            }}
            
            /* Tab Widget */
            QTabWidget::pane {{
                border: 2px solid {colors["border"]};
                background-color: {colors["bg_secondary"]};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {colors["bg_tertiary"]};
                border: 2px solid {colors["border"]};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                color: {colors["text_secondary"]};
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors["accent_primary"]};
                color: {colors["text_primary"]};
                border-color: {colors["accent_primary"]};
            }}
            
            QTabBar::tab:hover {{
                background-color: {colors["button_hover"]};
                color: {colors["text_primary"]};
            }}
            
            /* Tool Bar */
            QToolBar {{
                background-color: {colors["panel_bg"]};
                border: none;
                spacing: 4px;
                padding: 4px;
            }}
            
            QToolBar QLabel {{
                background-color: {colors["bg_tertiary"]};
                border: 1px solid {colors["border"]};
                border-radius: 3px;
                padding: 4px 8px;
                color: {colors["text_accent"]};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {colors["panel_bg"]};
                border-top: 2px solid {colors["border"]};
                color: {colors["text_primary"]};
            }}
            
            /* Graphics View */
            QGraphicsView {{
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                background-color: {colors["bg_primary"]};
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background-color: {colors["bg_tertiary"]};
                width: 16px;
                border: none;
                border-radius: 8px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors["accent_primary"]};
                border-radius: 8px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors["accent_secondary"]};
            }}
            
            /* Line Edits */
            QLineEdit {{
                background-color: {colors["bg_secondary"]};
                border: 2px solid {colors["border"]};
                border-radius: 4px;
                padding: 6px;
                color: {colors["text_primary"]};
            }}
            
            QLineEdit:focus {{
                border-color: {colors["accent_primary"]};
            }}
            
            /* Special LCARS styling for theme */
            {"" if self.current_settings["theme"] != "LCARS" else f'''
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
            '''}
            
            /* IMG Factory Professional styling */
            {"" if self.current_settings["theme"] != "IMG_Factory" else f'''
            /* IMG Factory specific button styling */
            QPushButton[action-type="import"] {{
                background-color: {colors["action_import"]};
                color: white;
                border: 1px solid {colors["action_import"]};
            }}
            
            QPushButton[action-type="export"] {{
                background-color: {colors["action_export"]};
                color: white;
                border: 1px solid {colors["action_export"]};
            }}
            
            QPushButton[action-type="remove"] {{
                background-color: {colors["action_remove"]};
                color: white;
                border: 1px solid {colors["action_remove"]};
            }}
            
            QPushButton[action-type="update"] {{
                background-color: {colors["action_update"]};
                color: white;
                border: 1px solid {colors["action_update"]};
            }}
            
            QPushButton[action-type="convert"] {{
                background-color: {colors["action_convert"]};
                color: white;
                border: 1px solid {colors["action_convert"]};
            }}
            
            /* Clean rectangular buttons */
            QPushButton {{
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: normal;
                min-height: 22px;
            }}
            
            /* Panel styling like IMG Factory */
            QGroupBox {{
                background-color: {colors["panel_bg"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                margin-top: 0.5em;
                padding-top: 8px;
                font-weight: normal;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: {colors["text_primary"]};
                font-weight: normal;
                font-size: 11px;
            }}
            
            /* Toolbar styling */
            QToolBar {{
                background-color: {colors["toolbar_bg"]};
                border: none;
                spacing: 2px;
                padding: 2px;
            }}
            
            /* Menu bar */
            QMenuBar {{
                background-color: {colors["bg_primary"]};
                border-bottom: 1px solid {colors["border"]};
                color: {colors["text_primary"]};
            }}
            
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors["button_hover"]};
            }}
            
            /* Table/List styling */
            QTreeWidget, QListWidget, QTableWidget {{
                background-color: {colors["bg_primary"]};
                border: 1px solid {colors["border"]};
                gridline-color: {colors["border"]};
                selection-background-color: {colors["button_hover"]};
            }}
            
            QHeaderView::section {{
                background-color: {colors["bg_secondary"]};
                padding: 4px;
                border: 1px solid {colors["border"]};
                font-weight: normal;
            }}
            '''}
        """


class SettingsDialog(QDialog):
    """Settings dialog with tabs for different categories"""
    
    settingsChanged = pyqtSignal()
    themeChanged = pyqtSignal(str)
    
    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.setWindowTitle("Chip Editor Settings - Live Long and Prosper 🖖")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self._create_ui()
        self._load_current_settings()
        
    def _create_ui(self):
        """Create the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Theme tab
        self.theme_tab = self._create_theme_tab()
        self.tabs.addTab(self.theme_tab, "🎨 Themes")
        
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
        """Create theme selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection
        theme_group = QGroupBox("Choose Your Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_buttons = QButtonGroup()
        
        for theme_name, theme_data in self.app_settings.themes.items():
            radio = QRadioButton(theme_data["name"])
            radio.setToolTip(theme_data["description"])
            radio.theme_name = theme_name
            self.theme_buttons.addButton(radio)
            theme_layout.addWidget(radio)
            
            # Add description
            desc_label = QLabel(f"   {theme_data['description']}")
            desc_label.setStyleSheet("color: #888; font-style: italic;")
            theme_layout.addWidget(desc_label)
        
        layout.addWidget(theme_group)
        
        # Theme preview
        preview_group = QGroupBox("Theme Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.theme_preview = QLabel("Select a theme to see preview")
        self.theme_preview.setMinimumHeight(100)
        self.theme_preview.setStyleSheet("""
            border: 2px solid #666;
            border-radius: 8px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a2e, stop:1 #16213e);
            color: #e0e1dd;
            font-size: 14px;
        """)
        preview_layout.addWidget(self.theme_preview)
        
        layout.addWidget(preview_group)
        
        # Connect theme selection
        self.theme_buttons.buttonClicked.connect(self._theme_selected)
        
        layout.addStretch()
        return widget
    
    def _create_interface_tab(self):
        """Create interface settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QGridLayout(font_group)
        
        font_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Consolas", "Ubuntu"])
        font_layout.addWidget(self.font_combo, 0, 1)
        
        font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
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
        
        # Update preview
        colors = theme["colors"]
        preview_style = f"""
            border: 2px solid {colors["border"]};
            border-radius: 8px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors["bg_primary"]}, stop:1 {colors["bg_secondary"]});
            color: {colors["text_primary"]};
            font-size: 14px;
        """
        
        self.theme_preview.setStyleSheet(preview_style)
        self.theme_preview.setText(f"""
Theme: {theme["name"]}

{theme["description"]}

Primary: {colors["text_primary"]}
Accent: {colors["accent_primary"]}
Background: {colors["bg_primary"]}

"Make it so!" - Captain Picard
        """)
    
    def _load_current_settings(self):
        """Load current settings into dialog controls"""
        settings = self.app_settings.current_settings
        
        # Theme tab
        for button in self.theme_buttons.buttons():
            if button.theme_name == settings["theme"]:
                button.setChecked(True)
                self._theme_selected(button)
                break
        
        # Interface tab
        self.font_combo.setCurrentText(settings["font_family"])
        self.font_size_spin.setValue(settings["font_size"])
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
            self, "Export Settings", "chip_editor_settings.json",
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