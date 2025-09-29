#this belongs in gui/ gui_settings.py - version 2
# X-Seti - July05 2025 - IMG Factory 1.5 - Complete GUI Settings with Tab Height Controls
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory GUI Settings Dialog
Comprehensive GUI customization options
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QSpinBox, QCheckBox, QComboBox, 
    QPushButton, QSlider, QColorDialog, QFontDialog,
    QMessageBox, QGridLayout, QFrame, QButtonGroup,
    QRadioButton, QLineEdit, QTextEdit, QListWidget,
    QListWidgetItem, QSplitter, QScrollArea, QFormLayout
)
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
import os

print(f"[DEBUG] gui_settings calling: with args={Path}")

class GUISettingsDialog(QDialog):
    """Comprehensive GUI Settings Dialog"""
    
    settings_changed = pyqtSignal()
    theme_changed = pyqtSignal(str)
    
    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.setWindowTitle("🖥️ GUI Settings - IMG Factory 1.5")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        self._create_ui()
        self._load_current_settings()
        #integrate_settings_menu(self)
        #integrate_color_ui_system(self)

    def _safe_load_icon(self, icon_name):
        """Safely load icon with fallback - ADDED TO FIX QIcon.fromTheme issues"""
        try:
            # Try theme icon first
            theme_icon = QIcon.fromTheme(icon_name)
            if theme_icon and not theme_icon.isNull():
                return theme_icon
        except Exception:
            pass
        
        # Try local icon paths
        try:
            icon_paths = [
                f"icons/{icon_name}.png",
                f"gui/icons/{icon_name}.png",
                f"resources/icons/{icon_name}.png"
            ]
            
            for path in icon_paths:
                if os.path.exists(path):
                    local_icon = QIcon(path)
                    if local_icon and not local_icon.isNull():
                        return local_icon
        except Exception:
            pass
        
        # Return empty icon as fallback
        return QIcon()
    
    def _create_ui(self):
        """Create the settings UI with tabs"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.tab_widget.addTab(self._create_appearance_tab(), "🎨 Appearance")
        self.tab_widget.addTab(self._create_layout_tab(), "📐 Layout")
        self.tab_widget.addTab(self._create_tabs_tab(), "📑 Tabs")
        self.tab_widget.addTab(self._create_fonts_tab(), "🔤 Fonts")
        self.tab_widget.addTab(self._create_icons_tab(), "🖼️ Icons")
        self.tab_widget.addTab(self._create_behavior_tab(), "⚙️ Behavior")
        
        layout.addWidget(self.tab_widget)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        # Reset to defaults
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Cancel
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Apply
        apply_btn = QPushButton("✓ Apply")
        apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_btn)
        
        # OK
        ok_btn = QPushButton("✓ OK")
        ok_btn.clicked.connect(self._save_and_close)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection
        theme_group = QGroupBox("🎨 Theme Selection")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "IMG Factory Default",
            "Dark Theme", 
            "Light Professional",
            "GTA San Andreas",
            "GTA Vice City",
            "LCARS (Star Trek)",
            "Cyberpunk 2077",
            "Matrix",
            "Synthwave",
            "Amiga Workbench"
        ])
        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Color customization
        color_group = QGroupBox("🌈 Color Customization")
        color_layout = QGridLayout(color_group)
        
        # Background color
        color_layout.addWidget(QLabel("Background Color:"), 0, 0)
        self.bg_color_btn = QPushButton("Choose Color...")
        self.bg_color_btn.clicked.connect(lambda: self._choose_color('background'))
        color_layout.addWidget(self.bg_color_btn, 0, 1)
        
        # Text color
        color_layout.addWidget(QLabel("Text Color:"), 1, 0)
        self.text_color_btn = QPushButton("Choose Color...")
        self.text_color_btn.clicked.connect(lambda: self._choose_color('text'))
        color_layout.addWidget(self.text_color_btn, 1, 1)
        
        # Accent color
        color_layout.addWidget(QLabel("Accent Color:"), 2, 0)
        self.accent_color_btn = QPushButton("Choose Color...")
        self.accent_color_btn.clicked.connect(lambda: self._choose_color('accent'))
        color_layout.addWidget(self.accent_color_btn, 2, 1)
        
        layout.addWidget(color_group)
        
        # Visual effects
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        self.animations_check = QCheckBox("Enable animations")
        self.shadows_check = QCheckBox("Enable shadows")
        self.transparency_check = QCheckBox("Enable transparency effects")
        self.rounded_corners_check = QCheckBox("Rounded corners")
        
        effects_layout.addWidget(self.animations_check)
        effects_layout.addWidget(self.shadows_check)
        effects_layout.addWidget(self.transparency_check)
        effects_layout.addWidget(self.rounded_corners_check)
        
        layout.addWidget(effects_group)
        layout.addStretch()
        
        return widget
    
    def _create_layout_tab(self) -> QWidget:
        """Create layout settings tab - REVERTED to original without tab settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Panel sizes
        panel_group = QGroupBox("📏 Panel Sizes")
        panel_layout = QGridLayout(panel_group)
        
        # Left panel width
        panel_layout.addWidget(QLabel("Left Panel Width:"), 0, 0)
        self.left_panel_spin = QSpinBox()
        self.left_panel_spin.setRange(200, 800)
        self.left_panel_spin.setValue(600)
        self.left_panel_spin.setSuffix(" px")
        panel_layout.addWidget(self.left_panel_spin, 0, 1)
        
        # Right panel width
        panel_layout.addWidget(QLabel("Right Panel Width:"), 1, 0)
        self.right_panel_spin = QSpinBox()
        self.right_panel_spin.setRange(180, 600)
        self.right_panel_spin.setValue(280)
        self.right_panel_spin.setSuffix(" px")
        panel_layout.addWidget(self.right_panel_spin, 1, 1)
        
        # Table row height
        panel_layout.addWidget(QLabel("Table Row Height:"), 2, 0)
        self.row_height_spin = QSpinBox()
        self.row_height_spin.setRange(20, 60)
        self.row_height_spin.setValue(25)
        self.row_height_spin.setSuffix(" px")
        panel_layout.addWidget(self.row_height_spin, 2, 1)
        
        layout.addWidget(panel_group)
        
        # Spacing and margins
        spacing_group = QGroupBox("📐 Spacing & Margins")
        spacing_layout = QGridLayout(spacing_group)
        
        # Widget spacing
        spacing_layout.addWidget(QLabel("Widget Spacing:"), 0, 0)
        self.widget_spacing_spin = QSpinBox()
        self.widget_spacing_spin.setRange(2, 20)
        self.widget_spacing_spin.setValue(5)
        self.widget_spacing_spin.setSuffix(" px")
        spacing_layout.addWidget(self.widget_spacing_spin, 0, 1)
        
        # Layout margins
        spacing_layout.addWidget(QLabel("Layout Margins:"), 1, 0)
        self.layout_margins_spin = QSpinBox()
        self.layout_margins_spin.setRange(0, 30)
        self.layout_margins_spin.setValue(5)
        self.layout_margins_spin.setSuffix(" px")
        spacing_layout.addWidget(self.layout_margins_spin, 1, 1)
        
        layout.addWidget(spacing_group)
        
        # Window behavior
        window_group = QGroupBox("🪟 Window Behavior")
        window_layout = QVBoxLayout(window_group)
        
        self.remember_size_check = QCheckBox("Remember window size")
        self.remember_position_check = QCheckBox("Remember window position")
        self.maximize_on_startup_check = QCheckBox("Maximize on startup")
        self.always_on_top_check = QCheckBox("Keep window always on top")
        
        window_layout.addWidget(self.remember_size_check)
        window_layout.addWidget(self.remember_position_check)
        window_layout.addWidget(self.maximize_on_startup_check)
        window_layout.addWidget(self.always_on_top_check)
        
        layout.addWidget(window_group)
        layout.addStretch()
        
        return widget
    
    def _create_tabs_tab(self) -> QWidget:
        """Create dedicated tabs settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tab Settings Group - DEDICATED TAB
        tab_group = QGroupBox("📑 Tab Configuration")
        tab_layout = QGridLayout(tab_group)
        
        # Main tab height
        tab_layout.addWidget(QLabel("Main Tab Height:"), 0, 0)
        self.main_tab_height_spin = QSpinBox()
        self.main_tab_height_spin.setRange(20, 60)
        self.main_tab_height_spin.setValue(35)
        self.main_tab_height_spin.setSuffix(" px")
        self.main_tab_height_spin.setToolTip("Height of the main IMG/COL/TXD tabs")
        tab_layout.addWidget(self.main_tab_height_spin, 0, 1)
        
        # Individual tab height
        tab_layout.addWidget(QLabel("Individual Tab Height:"), 1, 0)
        self.individual_tab_height_spin = QSpinBox()
        self.individual_tab_height_spin.setRange(16, 30)
        self.individual_tab_height_spin.setValue(24)
        self.individual_tab_height_spin.setSuffix(" px")
        self.individual_tab_height_spin.setToolTip("Height of individual tab buttons")
        tab_layout.addWidget(self.individual_tab_height_spin, 1, 1)
        
        # Tab font size
        tab_layout.addWidget(QLabel("Tab Font Size:"), 2, 0)
        self.tab_font_size_spin = QSpinBox()
        self.tab_font_size_spin.setRange(7, 14)
        self.tab_font_size_spin.setValue(9)
        self.tab_font_size_spin.setSuffix(" pt")
        self.tab_font_size_spin.setToolTip("Font size for tab text")
        tab_layout.addWidget(self.tab_font_size_spin, 2, 1)
        
        # Tab padding
        tab_layout.addWidget(QLabel("Tab Padding:"), 3, 0)
        self.tab_padding_spin = QSpinBox()
        self.tab_padding_spin.setRange(2, 12)
        self.tab_padding_spin.setValue(4)
        self.tab_padding_spin.setSuffix(" px")
        self.tab_padding_spin.setToolTip("Padding inside tab buttons")
        tab_layout.addWidget(self.tab_padding_spin, 3, 1)
        
        # Tab container height
        tab_layout.addWidget(QLabel("Tab Container Height:"), 4, 0)
        self.tab_container_height_spin = QSpinBox()
        self.tab_container_height_spin.setRange(30, 80)
        self.tab_container_height_spin.setValue(30)
        self.tab_container_height_spin.setSuffix(" px")
        self.tab_container_height_spin.setToolTip("Total height of the tab container section")
        tab_layout.addWidget(self.tab_container_height_spin, 4, 1)
        
        layout.addWidget(tab_group)
        
        # Tab Style Presets
        style_group = QGroupBox("🎨 Tab Style Presets")
        style_layout = QVBoxLayout(style_group)
        
        # Style selector
        style_selector_layout = QHBoxLayout()
        style_selector_layout.addWidget(QLabel("Quick Style:"))
        self.tab_style_combo = QComboBox()
        self.tab_style_combo.addItems(["Compact", "Standard", "Large"])
        self.tab_style_combo.setCurrentText("Compact")
        self.tab_style_combo.setToolTip("Preset tab size configurations")
        style_selector_layout.addWidget(self.tab_style_combo)
        style_selector_layout.addStretch()
        
        style_layout.addLayout(style_selector_layout)
        
        # Style descriptions
        style_descriptions = QTextEdit()
        style_descriptions.setMaximumHeight(80)
        style_descriptions.setReadOnly(True)
        style_descriptions.setPlainText(
            "• Compact: Space-saving tabs (35px height, 9pt font)\n"
            "• Standard: Balanced appearance (45px height, 10pt font)\n"
            "• Large: Accessibility-friendly (55px height, 11pt font)"
        )
        style_layout.addWidget(style_descriptions)
        
        layout.addWidget(style_group)
        
        # Preview and Actions
        actions_group = QGroupBox("🛠️ Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Preview button
        preview_btn = QPushButton("👀 Preview Tab Changes")
        preview_btn.clicked.connect(self._preview_tab_changes)
        preview_btn.setMinimumHeight(35)
        actions_layout.addWidget(preview_btn)
        
        # Reset to defaults button
        reset_tabs_btn = QPushButton("🔄 Reset Tab Settings to Defaults")
        reset_tabs_btn.clicked.connect(self._reset_tab_settings)
        reset_tabs_btn.setMinimumHeight(35)
        actions_layout.addWidget(reset_tabs_btn)
        
        layout.addWidget(actions_group)
        
        # Connect tab style combo to update spinboxes
        self.tab_style_combo.currentTextChanged.connect(self._apply_tab_style_preset)
        
        layout.addStretch()
        
        return widget
    
    def _create_fonts_tab(self) -> QWidget:
        """Create fonts settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font categories
        font_group = QGroupBox("🔤 Font Settings")
        font_layout = QGridLayout(font_group)
        
        # Main interface font
        font_layout.addWidget(QLabel("Main Interface Font:"), 0, 0)
        self.main_font_btn = QPushButton("Select Font...")
        self.main_font_btn.clicked.connect(lambda: self._choose_font('main'))
        font_layout.addWidget(self.main_font_btn, 0, 1)
        
        # Table font
        font_layout.addWidget(QLabel("Table Font:"), 1, 0)
        self.table_font_btn = QPushButton("Select Font...")
        self.table_font_btn.clicked.connect(lambda: self._choose_font('table'))
        font_layout.addWidget(self.table_font_btn, 1, 1)
        
        # Menu font
        font_layout.addWidget(QLabel("Menu Font:"), 2, 0)
        self.menu_font_btn = QPushButton("Select Font...")
        self.menu_font_btn.clicked.connect(lambda: self._choose_font('menu'))
        font_layout.addWidget(self.menu_font_btn, 2, 1)
        
        layout.addWidget(font_group)
        
        # Font size scaling
        size_group = QGroupBox("📏 Font Size Scaling")
        size_layout = QVBoxLayout(size_group)
        
        size_layout.addWidget(QLabel("Global Font Size Scale:"))
        self.font_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_scale_slider.setRange(75, 150)
        self.font_scale_slider.setValue(100)
        self.font_scale_slider.valueChanged.connect(self._update_font_scale_label)
        
        self.font_scale_label = QLabel("100%")
        self.font_scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("75%"))
        scale_layout.addWidget(self.font_scale_slider)
        scale_layout.addWidget(QLabel("150%"))
        
        size_layout.addLayout(scale_layout)
        size_layout.addWidget(self.font_scale_label)
        
        layout.addWidget(size_group)
        
        # Text options
        text_group = QGroupBox("📝 Text Options")
        text_layout = QVBoxLayout(text_group)
        
        self.antialiasing_check = QCheckBox("Enable font antialiasing")
        self.bold_headers_check = QCheckBox("Bold table headers")
        self.monospace_numbers_check = QCheckBox("Use monospace for numbers")
        
        text_layout.addWidget(self.antialiasing_check)
        text_layout.addWidget(self.bold_headers_check)
        text_layout.addWidget(self.monospace_numbers_check)
        
        layout.addWidget(text_group)
        layout.addStretch()
        
        return widget
    
    def _create_icons_tab(self) -> QWidget:
        """Create icons settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Icon display
        display_group = QGroupBox("🖼️ Icon Display")
        display_layout = QVBoxLayout(display_group)
        
        self.show_menu_icons_check = QCheckBox("Show icons in menus")
        self.show_toolbar_icons_check = QCheckBox("Show toolbar icons")
        self.show_button_icons_check = QCheckBox("Show icons on buttons")
        self.show_file_type_icons_check = QCheckBox("Show file type icons in table")
        
        display_layout.addWidget(self.show_menu_icons_check)
        display_layout.addWidget(self.show_toolbar_icons_check)
        display_layout.addWidget(self.show_button_icons_check)
        display_layout.addWidget(self.show_file_type_icons_check)
        
        layout.addWidget(display_group)
        
        # Icon size
        size_group = QGroupBox("📏 Icon Sizes")
        size_layout = QGridLayout(size_group)
        
        # Menu icon size
        size_layout.addWidget(QLabel("Menu Icon Size:"), 0, 0)
        self.menu_icon_size_combo = QComboBox()
        self.menu_icon_size_combo.addItems(["16px", "20px", "24px", "32px"])
        size_layout.addWidget(self.menu_icon_size_combo, 0, 1)
        
        # Toolbar icon size
        size_layout.addWidget(QLabel("Toolbar Icon Size:"), 1, 0)
        self.toolbar_icon_size_combo = QComboBox()
        self.toolbar_icon_size_combo.addItems(["16px", "20px", "24px", "32px", "48px"])
        size_layout.addWidget(self.toolbar_icon_size_combo, 1, 1)
        
        # Button icon size
        size_layout.addWidget(QLabel("Button Icon Size:"), 2, 0)
        self.button_icon_size_combo = QComboBox()
        self.button_icon_size_combo.addItems(["16px", "20px", "24px", "32px"])
        size_layout.addWidget(self.button_icon_size_combo, 2, 1)
        
        layout.addWidget(size_group)
        
        # Icon style
        style_group = QGroupBox("🎨 Icon Style")
        style_layout = QVBoxLayout(style_group)
        
        self.icon_style_group = QButtonGroup()
        
        style_auto = QRadioButton("Automatic (match theme)")
        style_mono = QRadioButton("Monochrome")
        style_color = QRadioButton("Full color")
        style_outline = QRadioButton("Outline style")
        
        self.icon_style_group.addButton(style_auto, 0)
        self.icon_style_group.addButton(style_mono, 1)
        self.icon_style_group.addButton(style_color, 2)
        self.icon_style_group.addButton(style_outline, 3)
        
        style_layout.addWidget(style_auto)
        style_layout.addWidget(style_mono)
        style_layout.addWidget(style_color)
        style_layout.addWidget(style_outline)
        
        layout.addWidget(style_group)
        layout.addStretch()
        
        return widget
    
    def _create_behavior_tab(self) -> QWidget:
        """Create behavior settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Interface behavior
        interface_group = QGroupBox("🖱️ Interface Behavior")
        interface_layout = QVBoxLayout(interface_group)
        
        self.double_click_open_check = QCheckBox("Double-click to open files")
        self.single_click_select_check = QCheckBox("Single-click to select")
        self.hover_preview_check = QCheckBox("Show preview on hover")
        self.auto_resize_columns_check = QCheckBox("Auto-resize table columns")
        
        interface_layout.addWidget(self.double_click_open_check)
        interface_layout.addWidget(self.single_click_select_check)
        interface_layout.addWidget(self.hover_preview_check)
        interface_layout.addWidget(self.auto_resize_columns_check)
        
        layout.addWidget(interface_group)
        
        # Performance
        performance_group = QGroupBox("⚡ Performance")
        performance_layout = QVBoxLayout(performance_group)
        
        self.lazy_loading_check = QCheckBox("Enable lazy loading for large files")
        self.cache_thumbnails_check = QCheckBox("Cache file thumbnails")
        self.preload_common_files_check = QCheckBox("Preload common file types")
        
        performance_layout.addWidget(self.lazy_loading_check)
        performance_layout.addWidget(self.cache_thumbnails_check)
        performance_layout.addWidget(self.preload_common_files_check)
        
        layout.addWidget(performance_group)
        
        # Notifications
        notifications_group = QGroupBox("🔔 Notifications")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.show_notifications_check = QCheckBox("Show system notifications")
        self.sound_notifications_check = QCheckBox("Play sound for notifications")
        self.progress_notifications_check = QCheckBox("Show progress notifications")
        
        notifications_layout.addWidget(self.show_notifications_check)
        notifications_layout.addWidget(self.sound_notifications_check)
        notifications_layout.addWidget(self.progress_notifications_check)
        
        layout.addWidget(notifications_group)
        layout.addStretch()
        
        return widget
    
    def _save_and_close(self):
        """Save settings and close dialog"""
        self._save_settings()
        self.settings_changed.emit()
        self.accept()
    
    def _create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab with button display options"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Existing theme section...

        # Button Display Mode Section - NEW
        button_group = QGroupBox("🖲️ Button Display Mode")
        button_layout = QVBoxLayout(button_group)

        # Button display mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Button Style:"))

        self.button_mode_combo = QComboBox()
        self.button_mode_combo.addItems([
            "Text Only",
            "Icons Only",
            "Icons with Text"
        ])
        self.button_mode_combo.setCurrentText("Text Only")  # Default
        self.button_mode_combo.currentTextChanged.connect(self._on_button_mode_changed)
        mode_layout.addWidget(self.button_mode_combo)
        mode_layout.addStretch()

        button_layout.addLayout(mode_layout)

        # Preview section
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))

        # Create sample buttons to show the different modes
        self.preview_text_btn = QPushButton("Export")
        self.preview_text_btn.setMaximumWidth(60)

        self.preview_icon_btn = QPushButton()
        self.preview_icon_btn.setIcon(QIcon.fromTheme("document-export"))
        self.preview_icon_btn.setMaximumWidth(40)
        self.preview_icon_btn.setToolTip("Export")

        self.preview_both_btn = QPushButton("Export")
        self.preview_both_btn.setIcon(QIcon.fromTheme("document-export"))
        self.preview_both_btn.setMaximumWidth(80)

        preview_layout.addWidget(self.preview_text_btn)
        preview_layout.addWidget(self.preview_icon_btn)
        preview_layout.addWidget(self.preview_both_btn)
        preview_layout.addStretch()

        button_layout.addLayout(preview_layout)

        # Help text
        help_label = QLabel("Text Only: No icons, faster performance\n"
                        "Icons Only: Desktop-style icons with tooltips\n"
                        "Icons with Text: Icons with text labels")
        help_label.setStyleSheet("color: #666; font-size: 8pt; font-style: italic;")
        button_layout.addWidget(help_label)

        layout.addWidget(button_group)

        # Existing color and effects sections...

        return widget

    def _on_button_mode_changed(self, mode_text):
        """Handle button mode change in settings"""
        # Update preview buttons
        if mode_text == "Text Only":
            self.preview_text_btn.setVisible(True)
            self.preview_icon_btn.setVisible(False)
            self.preview_both_btn.setVisible(False)
        elif mode_text == "Icons Only":
            self.preview_text_btn.setVisible(False)
            self.preview_icon_btn.setVisible(True)
            self.preview_both_btn.setVisible(False)
        elif mode_text == "Icons with Text":
            self.preview_text_btn.setVisible(False)
            self.preview_icon_btn.setVisible(False)
            self.preview_both_btn.setVisible(True)

    def _apply_button_mode_to_main_window(self):
        """Apply button mode to main window immediately"""
        try:
            main_window = self.parent()

            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'backend'):
                mode_text = self.button_mode_combo.currentText()

                if mode_text == "Text Only":
                    mode = "text_only"
                elif mode_text == "Icons Only":
                    mode = "icons_only"
                elif mode_text == "Icons with Text":
                    mode = "icons_with_text"
                else:
                    mode = "text_only"

                main_window.gui_layout.backend.set_button_display_mode(mode)
                main_window.log_message(f"✅ Button display mode: {mode_text}")

        except Exception as e:
            print(f"Error applying button mode: {e}")


    def _update_font_scale_label(self):
        """Update font scale percentage label"""
        value = self.font_scale_slider.value()
        self.font_scale_label.setText(f"{value}%")
    
    def _choose_color(self, color_type: str):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, f"Choose {color_type.title()} Color")
        if color.isValid():
            # Store the color (implement based on your color management system)
            color_name = color.name()
            if color_type == 'background':
                self.bg_color_btn.setStyleSheet(f"background-color: {color_name};")
            elif color_type == 'text':
                self.text_color_btn.setStyleSheet(f"background-color: {color_name};")
            elif color_type == 'accent':
                self.accent_color_btn.setStyleSheet(f"background-color: {color_name};")
    
    def _choose_font(self, font_type: str):
        """Open font picker dialog"""
        current_font = QFont()
        font, ok = QFontDialog.getFont(current_font, self, f"Choose {font_type.title()} Font")
        if ok:
            # Update button text to show selected font
            font_info = f"{font.family()} {font.pointSize()}pt"
            if font_type == 'main':
                self.main_font_btn.setText(font_info)
            elif font_type == 'table':
                self.table_font_btn.setText(font_info)
            elif font_type == 'menu':
                self.menu_font_btn.setText(font_info)
    

    def _save_settings(self):
        """Save all settings to app_settings - CLEAN VERSION"""
        try:
            settings = self.app_settings.current_settings

            # Button display mode - NEW
            mode_text = self.button_mode_combo.currentText()
            if mode_text == "Text Only":
                settings["button_display_mode"] = "text_only"
            elif mode_text == "Icons Only":
                settings["button_display_mode"] = "icons_only"
            elif mode_text == "Icons with Text":
                settings["button_display_mode"] = "icons_with_text"
            else:
                settings["button_display_mode"] = "text_only"  # Default fallback

            # Tab settings
            settings["main_tab_height"] = self.main_tab_height_spin.value()
            settings["individual_tab_height"] = self.individual_tab_height_spin.value()
            settings["tab_font_size"] = self.tab_font_size_spin.value()
            settings["tab_padding"] = self.tab_padding_spin.value()
            settings["tab_container_height"] = self.tab_container_height_spin.value()
            settings["tab_style"] = self.tab_style_combo.currentText()

            # Theme settings
            theme_code = self._theme_name_to_code(self.theme_combo.currentText())
            if settings.get("theme") != theme_code:
                settings["theme"] = theme_code
                self.theme_changed.emit(theme_code)

            # Visual effects
            settings["enable_animations"] = self.animations_check.isChecked()
            settings["enable_shadows"] = self.shadows_check.isChecked()
            settings["enable_transparency"] = self.transparency_check.isChecked()
            settings["rounded_corners"] = self.rounded_corners_check.isChecked()

            # Layout settings
            settings["left_panel_width"] = self.left_panel_spin.value()
            settings["right_panel_width"] = self.right_panel_spin.value()
            settings["table_row_height"] = self.row_height_spin.value()
            settings["widget_spacing"] = self.widget_spacing_spin.value()
            settings["layout_margins"] = self.layout_margins_spin.value()

            # Window behavior
            settings["remember_window_size"] = self.remember_size_check.isChecked()
            settings["remember_window_position"] = self.remember_position_check.isChecked()
            settings["maximize_on_startup"] = self.maximize_on_startup_check.isChecked()
            settings["always_on_top"] = self.always_on_top_check.isChecked()

            # Font settings
            settings["font_scale"] = self.font_scale_slider.value()
            settings["enable_antialiasing"] = self.antialiasing_check.isChecked()

            # Performance settings
            settings["lazy_loading"] = self.lazy_loading_check.isChecked()
            settings["cache_thumbnails"] = self.cache_thumbnails_check.isChecked()
            settings["preload_common_files"] = self.preload_common_files_check.isChecked()

            # Notification settings
            settings["show_notifications"] = self.show_notifications_check.isChecked()
            settings["sound_notifications"] = self.sound_notifications_check.isChecked()
            settings["progress_notifications"] = self.progress_notifications_check.isChecked()

            # Apply settings to main window immediately
            self._apply_settings_to_main_window()

            # Save to file
            self.app_settings.save_settings()

            # Emit signals
            self.settings_changed.emit()

            if hasattr(self.app_settings, 'log_message'):
                self.app_settings.log_message("✅ Settings saved successfully")

        except Exception as e:
            error_msg = f"Error saving settings: {str(e)}"
            if hasattr(self.app_settings, 'log_message'):
                self.app_settings.log_message(f"❌ {error_msg}")
            print(error_msg)  # Fallback logging


    def _load_current_settings(self):
        """Load current settings into controls - CLEAN VERSION"""
        try:
            settings = self.app_settings.current_settings

            # Button display mode - NEW
            button_mode = settings.get("button_display_mode", "text_only")
            if button_mode == "text_only":
                self.button_mode_combo.setCurrentText("Text Only")
            elif button_mode == "icons_only":
                self.button_mode_combo.setCurrentText("Icons Only")
            elif button_mode == "icons_with_text":
                self.button_mode_combo.setCurrentText("Icons with Text")
            else:
                self.button_mode_combo.setCurrentText("Text Only")  # Default fallback

            # Update preview based on loaded setting
            self._on_button_mode_changed(self.button_mode_combo.currentText())

            # Tab settings
            self.main_tab_height_spin.setValue(settings.get("main_tab_height", 35))
            self.individual_tab_height_spin.setValue(settings.get("individual_tab_height", 24))
            self.tab_font_size_spin.setValue(settings.get("tab_font_size", 9))
            self.tab_padding_spin.setValue(settings.get("tab_padding", 4))
            self.tab_container_height_spin.setValue(settings.get("tab_container_height", 40))

            # Tab style combo
            tab_style = settings.get("tab_style", "Compact")
            self.tab_style_combo.setCurrentText(tab_style)

            # Theme
            theme_code = settings.get("theme", "img_factory")
            theme_name = self._theme_code_to_name(theme_code)
            self.theme_combo.setCurrentText(theme_name)

            # Visual effects
            self.animations_check.setChecked(settings.get("enable_animations", True))
            self.shadows_check.setChecked(settings.get("enable_shadows", True))
            self.transparency_check.setChecked(settings.get("enable_transparency", False))
            self.rounded_corners_check.setChecked(settings.get("rounded_corners", True))

            # Layout
            self.left_panel_spin.setValue(settings.get("left_panel_width", 600))
            self.right_panel_spin.setValue(settings.get("right_panel_width", 280))
            self.row_height_spin.setValue(settings.get("table_row_height", 25))
            self.widget_spacing_spin.setValue(settings.get("widget_spacing", 5))
            self.layout_margins_spin.setValue(settings.get("layout_margins", 5))

            # Window behavior
            self.remember_size_check.setChecked(settings.get("remember_window_size", True))
            self.remember_position_check.setChecked(settings.get("remember_window_position", True))
            self.maximize_on_startup_check.setChecked(settings.get("maximize_on_startup", False))
            self.always_on_top_check.setChecked(settings.get("always_on_top", False))

            # Font settings
            self.font_scale_slider.setValue(settings.get("font_scale", 100))
            self.antialiasing_check.setChecked(settings.get("enable_antialiasing", True))

            # Performance settings
            self.lazy_loading_check.setChecked(settings.get("lazy_loading", False))
            self.cache_thumbnails_check.setChecked(settings.get("cache_thumbnails", True))
            self.preload_common_files_check.setChecked(settings.get("preload_common_files", False))

            # Notification settings
            self.show_notifications_check.setChecked(settings.get("show_notifications", True))
            self.sound_notifications_check.setChecked(settings.get("sound_notifications", False))
            self.progress_notifications_check.setChecked(settings.get("progress_notifications", True))

        except Exception as e:
            error_msg = f"Error loading settings: {str(e)}"
            print(error_msg)  # Fallback logging

            # Set defaults if loading fails
            self._set_default_values()


    def _apply_settings_to_main_window(self):
        """Apply all settings to main window immediately - CLEAN VERSION"""
        try:
            main_window = self.parent()

            if not main_window:
                return

            # Apply button display mode
            self._apply_button_mode_to_main_window()

            # Apply tab settings
            self._apply_tab_settings_to_main_window()

            # Apply layout settings
            if hasattr(main_window, 'gui_layout'):
                gui_layout = main_window.gui_layout

                # Update splitter sizes if available
                if hasattr(gui_layout, 'main_splitter'):
                    left_width = self.left_panel_spin.value()
                    right_width = self.right_panel_spin.value()
                    gui_layout.main_splitter.setSizes([left_width, right_width])

                # Update table row height
                if hasattr(gui_layout, 'table') and gui_layout.table:
                    row_height = self.row_height_spin.value()
                    gui_layout.table.verticalHeader().setDefaultSectionSize(row_height)

            # Apply window behavior
            if self.remember_size_check.isChecked():
                # Window size will be remembered on close
                pass

            if self.always_on_top_check.isChecked():
                main_window.setWindowFlags(main_window.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
                main_window.show()
            else:
                main_window.setWindowFlags(main_window.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
                main_window.show()

            # Log success
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ Settings applied to main window")

        except Exception as e:
            error_msg = f"Error applying settings to main window: {str(e)}"
            print(error_msg)


    def _set_default_values(self):
        """Set default values for all controls - HELPER METHOD"""
        try:
            # Button display mode
            self.button_mode_combo.setCurrentText("Text Only")
            self._on_button_mode_changed("Text Only")

            # Tab settings
            self.main_tab_height_spin.setValue(35)
            self.individual_tab_height_spin.setValue(24)
            self.tab_font_size_spin.setValue(9)
            self.tab_padding_spin.setValue(4)
            self.tab_container_height_spin.setValue(40)
            self.tab_style_combo.setCurrentText("Compact")

            # Theme
            self.theme_combo.setCurrentText("IMG Factory Default")

            # Visual effects
            self.animations_check.setChecked(True)
            self.shadows_check.setChecked(True)
            self.transparency_check.setChecked(False)
            self.rounded_corners_check.setChecked(True)

            # Layout
            self.left_panel_spin.setValue(600)
            self.right_panel_spin.setValue(280)
            self.row_height_spin.setValue(25)
            self.widget_spacing_spin.setValue(5)
            self.layout_margins_spin.setValue(5)

            # Window behavior
            self.remember_size_check.setChecked(True)
            self.remember_position_check.setChecked(True)
            self.maximize_on_startup_check.setChecked(False)
            self.always_on_top_check.setChecked(False)

            # Font settings
            self.font_scale_slider.setValue(100)
            self.antialiasing_check.setChecked(True)

            # Performance settings
            self.lazy_loading_check.setChecked(False)
            self.cache_thumbnails_check.setChecked(True)
            self.preload_common_files_check.setChecked(False)

            # Notification settings
            self.show_notifications_check.setChecked(True)
            self.sound_notifications_check.setChecked(False)
            self.progress_notifications_check.setChecked(True)

        except Exception as e:
            print(f"Error setting default values: {str(e)}")

    def _theme_code_to_name(self, code: str) -> str:
        """Convert theme code to display name - CONSOLIDATED VERSION"""
        theme_map = {
            "img_factory": "IMG Factory Default",
            "dark": "Dark Theme",
            "light": "Light Mode",
            "light_professional": "Light Professional",
            "high_contrast": "High Contrast",
            "gta_san_andreas": "GTA San Andreas",
            "gta_vice_city": "GTA Vice City",
            "lcars": "LCARS (Star Trek)",
            "cyberpunk_2077": "Cyberpunk 2077",
            "matrix": "Matrix",
            "synthwave": "Synthwave",
            "amiga_workbench": "Amiga Workbench",
            "custom": "Custom"
        }
        return theme_map.get(code, "IMG Factory Default")

    def _theme_name_to_code(self, name: str) -> str:
        """Convert display name to theme code - CONSOLIDATED VERSION"""
        name_map = {
            "IMG Factory Default": "img_factory",
            "Dark Theme": "dark",
            "Light Mode": "light",
            "Light Professional": "light_professional",
            "High Contrast": "high_contrast",
            "GTA San Andreas": "gta_san_andreas",
            "GTA Vice City": "gta_vice_city",
            "LCARS (Star Trek)": "lcars",
            "Cyberpunk 2077": "cyberpunk_2077",
            "Matrix": "matrix",
            "Synthwave": "synthwave",
            "Amiga Workbench": "amiga_workbench",
            "Custom": "custom"
        }
        return name_map.get(name, "img_factory")

    def get_available_themes(self) -> list:
        """Get list of all available theme display names"""
        return [
            "IMG Factory Default",
            "Dark Theme",
            "Light Mode",
            "Light Professional",
            "High Contrast",
            "GTA San Andreas",
            "GTA Vice City",
            "LCARS (Star Trek)",
            "Cyberpunk 2077",
            "Matrix",
            "Synthwave",
            "Amiga Workbench",
            "Custom"
        ]

    def get_theme_description(self, theme_code: str) -> str:
        """Get description for theme code"""
        descriptions = {
            "img_factory": "Classic IMG Factory interface with pastel colors",
            "dark": "Dark theme for reduced eye strain",
            "light": "Clean light theme for maximum readability",
            "light_professional": "Professional light theme for business use",
            "high_contrast": "High contrast theme for accessibility",
            "gta_san_andreas": "Inspired by GTA San Andreas color scheme",
            "gta_vice_city": "Retro 80s Vice City inspired theme",
            "lcars": "Star Trek LCARS computer interface style",
            "cyberpunk_2077": "Futuristic cyberpunk aesthetic",
            "matrix": "Green-on-black Matrix code style",
            "synthwave": "Neon synthwave retro aesthetic",
            "amiga_workbench": "Classic Amiga Workbench interface",
            "custom": "User customized theme"
        }
        return descriptions.get(theme_code, "No description available")

    def is_dark_theme(self, theme_code: str) -> bool:
        """Check if theme is a dark theme"""
        dark_themes = {
            "dark", "cyberpunk_2077", "matrix", "synthwave"
        }
        return theme_code in dark_themes

    def get_theme_preview_colors(self, theme_code: str) -> dict:
        """Get preview colors for theme"""
        theme_colors = {
            "img_factory": {
                "background": "#f5f5f5",
                "text": "#333333",
                "accent": "#2196f3",
                "button": "#e3f2fd"
            },
            "dark": {
                "background": "#2b2b2b",
                "text": "#ffffff",
                "accent": "#bb86fc",
                "button": "#3c3c3c"
            },
            "light": {
                "background": "#ffffff",
                "text": "#000000",
                "accent": "#FFEFEE",
                "button": "#f0f0f0"
            },
            "light_professional": {
                "background": "#fafafa",
                "text": "#333333",
                "accent": "#1976d2",
                "button": "#e8eaf6"
            },
            "high_contrast": {
                "background": "#000000",
                "text": "#ffffff",
                "accent": "#ffff00",
                "button": "#ffffff"
            },
            "gta_san_andreas": {
                "background": "#2d1810",
                "text": "#f4e4bc",
                "accent": "#ff6b35",
                "button": "#4a2c17"
            },
            "gta_vice_city": {
                "background": "#1a0d26",
                "text": "#ff69b4",
                "accent": "#00ffff",
                "button": "#4d1a4d"
            },
            "lcars": {
                "background": "#000000",
                "text": "#ff9900",
                "accent": "#9999ff",
                "button": "#333366"
            },
            "cyberpunk_2077": {
                "background": "#0f0f0f",
                "text": "#00ffff",
                "accent": "#ff003c",
                "button": "#1a1a2e"
            },
            "matrix": {
                "background": "#000000",
                "text": "#00ff00",
                "accent": "#00aa00",
                "button": "#003300"
            },
            "synthwave": {
                "background": "#2d1b69",
                "text": "#ff006e",
                "accent": "#06ffa5",
                "button": "#4d2d8a"
            },
            "amiga_workbench": {
                "background": "#c0c0c0",
                "text": "#000000",
                "accent": "#0000aa",
                "button": "#dddddd"
            },
            "custom": {
                "background": "#f5f5f5",
                "text": "#333333",
                "accent": "#2196f3",
                "button": "#e3f2fd"
            }
        }
        return theme_colors.get(theme_code, theme_colors["img_factory"])


    def _apply_settings(self):
        """Apply settings without closing dialog"""
        self._save_settings()
        self.settings_changed.emit()
        QMessageBox.information(self, "Settings Applied", "GUI settings have been applied successfully!")
    
    def _reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self, "Reset to Defaults",
            "This will reset all GUI settings to their default values.\n\nAre you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset tab settings
            self.main_tab_height_spin.setValue(35)
            self.individual_tab_height_spin.setValue(24)
            self.tab_font_size_spin.setValue(9)
            self.tab_padding_spin.setValue(4)
            self.tab_container_height_spin.setValue(40)
            self.tab_style_combo.setCurrentText("Compact")
            
            # Reset theme
            self.theme_combo.setCurrentText("IMG Factory Default")
            
            # Reset visual effects
            self.animations_check.setChecked(True)
            self.shadows_check.setChecked(True)
            self.transparency_check.setChecked(False)
            self.rounded_corners_check.setChecked(True)
            
            # Reset layout
            self.left_panel_spin.setValue(600)
            self.right_panel_spin.setValue(280)
            self.row_height_spin.setValue(25)
            self.widget_spacing_spin.setValue(5)
            self.layout_margins_spin.setValue(5)
            
            # Reset window behavior
            self.remember_size_check.setChecked(True)
            self.remember_position_check.setChecked(True)
            self.maximize_on_startup_check.setChecked(False)
            self.always_on_top_check.setChecked(False)
            
            # Reset fonts
            self.font_scale_slider.setValue(100)
            self.antialiasing_check.setChecked(True)
            self.bold_headers_check.setChecked(True)
            self.monospace_numbers_check.setChecked(False)
            
            # Reset icons
            self.show_menu_icons_check.setChecked(True)
            self.show_toolbar_icons_check.setChecked(True)
            self.show_button_icons_check.setChecked(True)
            self.show_file_type_icons_check.setChecked(True)
            
            self.menu_icon_size_combo.setCurrentText("16px")
            self.toolbar_icon_size_combo.setCurrentText("24px")
            self.button_icon_size_combo.setCurrentText("16px")
            
            self.icon_style_group.button(0).setChecked(True)
            
            # Reset behavior
            self.double_click_open_check.setChecked(True)
            self.single_click_select_check.setChecked(False)
            self.hover_preview_check.setChecked(True)
            self.auto_resize_columns_check.setChecked(True)
            
            # Reset performance
            self.lazy_loading_check.setChecked(True)
            self.cache_thumbnails_check.setChecked(True)
            self.preload_common_files_check.setChecked(False)
            
            # Reset notifications
            self.show_notifications_check.setChecked(True)
            self.sound_notifications_check.setChecked(False)
            self.progress_notifications_check.setChecked(True)
            
            # Reset font buttons
            self.main_font_btn.setText("Select Font...")
            self.table_font_btn.setText("Select Font...")
            self.menu_font_btn.setText("Select Font...")
            
            # Reset color buttons
            self.bg_color_btn.setStyleSheet("")
            self.text_color_btn.setStyleSheet("")
            self.accent_color_btn.setStyleSheet("")
            
            # Update font scale label
            self._update_font_scale_label()
            
            QMessageBox.information(self, "Reset Complete", "All settings have been reset to default values.")

    def _reset_tab_settings(self):
        """Reset only tab settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Tab Settings",
            "This will reset all tab settings to their default values.\n\nAre you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset tab settings only
            self.main_tab_height_spin.setValue(35)
            self.individual_tab_height_spin.setValue(24)
            self.tab_font_size_spin.setValue(9)
            self.tab_padding_spin.setValue(4)
            self.tab_container_height_spin.setValue(40)
            self.tab_style_combo.setCurrentText("Compact")
            
            QMessageBox.information(self, "Reset Complete", "Tab settings have been reset to default values.")

    def create_settings_menu(main_window):
        """Example of adding file window color option to settings menu"""

        # If you have a QMenuBar
        if hasattr(main_window, 'menuBar'):
            settings_menu = main_window.menuBar().addMenu("⚙️ Settings")

            # Add file window color option
            color_action = settings_menu.addAction("🎨 File Window Colors")
            color_action.triggered.connect(main_window.show_file_window_color_selector)

            # Add separator
            settings_menu.addSeparator()

            # Quick theme submenu
            theme_submenu = settings_menu.addMenu("🌈 Quick Themes")

            # Add popular themes as quick actions
            quick_themes = [
                ("Light Pink", "🌸"),
                ("Dark Blue", "🌙"),
                ("Green", "🟢"),
                ("Black & Red", "⚫"),
                ("Purple", "🟣"),
                ("Orange", "🟠")
            ]

            for theme_name, emoji in quick_themes:
                action = theme_submenu.addAction(f"{emoji} {theme_name}")
                action.triggered.connect(lambda checked, theme=theme_name: main_window.apply_file_window_theme(theme))

            # Add separator and other settings
            settings_menu.addSeparator()

            # Other settings can go here
            general_action = settings_menu.addAction("⚙️ General Settings")
            # general_action.triggered.connect(main_window.show_general_settings)

            return settings_menu

        # Alternative: If you have a settings dialog
        elif hasattr(main_window, 'settings_dialog'):
            return add_color_options_to_dialog(main_window.settings_dialog)

        return None


    def add_color_options_to_dialog(settings_dialog):
        """Add color options to an existing settings dialog"""
        from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

        # Create appearance group
        appearance_group = QGroupBox("🎨 Appearance")
        appearance_layout = QVBoxLayout(appearance_group)

        # Current theme display
        current_theme_label = QLabel("Current File Window Theme:")
        current_theme_display = QLabel("Light Pink")  # This should be updated with actual current theme
        current_theme_display.setStyleSheet("font-weight: bold; color: #EC4899; padding: 5px;")

        appearance_layout.addWidget(current_theme_label)
        appearance_layout.addWidget(current_theme_display)

        # Theme selection button
        theme_button_layout = QHBoxLayout()

        select_theme_btn = QPushButton("🎨 Choose File Window Colors")
        select_theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #EC4899;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #BE185D;
            }
        """)

        # This would need to be connected to the main window's method
        # select_theme_btn.clicked.connect(main_window.show_file_window_color_selector)

        theme_button_layout.addWidget(select_theme_btn)
        theme_button_layout.addStretch()

        appearance_layout.addLayout(theme_button_layout)

        # Quick theme buttons
        quick_themes_label = QLabel("Quick Themes:")
        appearance_layout.addWidget(quick_themes_label)

        quick_buttons_layout = QHBoxLayout()

        quick_themes = [
            ("🌸", "Light Pink", "#F472B6"),
            ("🌙", "Dark Blue", "#3B82F6"),
            ("🟢", "Green", "#22C55E"),
            ("⚫", "Black & Red", "#F87171")
        ]

        for emoji, theme_name, color in quick_themes:
            btn = QPushButton(f"{emoji}")
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid #999;
                    border-radius: 20px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    border: 3px solid #333;
                }}
            """)
            btn.setToolTip(theme_name)
            # btn.clicked.connect(lambda checked, theme=theme_name: main_window.apply_file_window_theme(theme))
            quick_buttons_layout.addWidget(btn)

        quick_buttons_layout.addStretch()
        appearance_layout.addLayout(quick_buttons_layout)

        # Add to settings dialog (this depends on your dialog structure)
        # settings_dialog.layout().addWidget(appearance_group)

        return appearance_group


    def integrate_settings_menu(main_window):
        """Complete integration of color settings into main window"""
        try:
            # First integrate the color UI system
            from methods.colour_ui_for_loaded_img import integrate_color_ui_system
            integrate_color_ui_system(main_window)

            # Create or update settings menu
            settings_menu = create_settings_menu(main_window)

            # Add toolbar button for quick access (optional)
            if hasattr(main_window, 'toolbar'):
                color_toolbar_action = main_window.toolbar.addAction("🎨")
                color_toolbar_action.setToolTip("Change File Window Colors")
                color_toolbar_action.triggered.connect(main_window.show_file_window_color_selector)

            # Add status bar indicator (optional)
            if hasattr(main_window, 'statusBar'):
                current_theme = getattr(main_window, '_current_file_window_theme', 'Light Pink')
                theme_indicator = f"Theme: {current_theme}"
                main_window.statusBar().addPermanentWidget(QLabel(theme_indicator))

            if hasattr(main_window, 'log_message'):
                main_window.log_message("🎨 Settings menu with color options integrated")

            return True

        except Exception as e:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Error integrating settings menu: {str(e)}")
            return False


    def _apply_tab_style_preset(self, style_name):
        """Apply preset tab style configurations"""
        if style_name == "Compact":
            self.main_tab_height_spin.setValue(35)
            self.individual_tab_height_spin.setValue(24)
            self.tab_font_size_spin.setValue(9)
            self.tab_padding_spin.setValue(4)
            self.tab_container_height_spin.setValue(40)
        elif style_name == "Standard":
            self.main_tab_height_spin.setValue(45)
            self.individual_tab_height_spin.setValue(28)
            self.tab_font_size_spin.setValue(10)
            self.tab_padding_spin.setValue(6)
            self.tab_container_height_spin.setValue(50)
        elif style_name == "Large":
            self.main_tab_height_spin.setValue(55)
            self.individual_tab_height_spin.setValue(32)
            self.tab_font_size_spin.setValue(11)
            self.tab_padding_spin.setValue(8)
            self.tab_container_height_spin.setValue(60)

    def _preview_tab_changes(self):
        """Preview tab height changes in real-time"""
        if hasattr(self.parent(), 'gui_layout'):
            # Apply changes to the main window tabs
            self._apply_tab_settings_to_main_window()
            
            # Show preview message
            QMessageBox.information(self, "Preview Applied", 
                                   "Tab height changes have been applied as preview.\n"
                                   "Click 'Apply' to save permanently or 'Cancel' to revert.")

    def _apply_tab_settings_to_main_window(self):
        """Apply tab settings to main window - FIXED"""
        try:
            main_window = self.parent()
            
            # Check if main window has gui_layout
            if not hasattr(main_window, 'gui_layout'):
                return
                
            # Get current values
            main_height = self.main_tab_height_spin.value()
            tab_height = self.individual_tab_height_spin.value()
            font_size = self.tab_font_size_spin.value()
            padding = self.tab_padding_spin.value()
            container_height = self.tab_container_height_spin.value()
            
            # Method 1: Try to call the method if it exists
            if hasattr(main_window.gui_layout, '_apply_dynamic_tab_styling'):
                main_window.gui_layout._apply_dynamic_tab_styling(
                    main_height, tab_height, font_size, padding, container_height
                )
            else:
                # Method 2: Apply styling directly if method doesn't exist
                self._apply_tab_styling_directly(main_window, main_height, tab_height, font_size, padding, container_height)
                
        except Exception as e:
            # Show error but don't crash
            QMessageBox.warning(self, "Tab Settings", f"Could not apply tab settings: {str(e)}")

    def _apply_tab_styling_directly(self, main_window, main_height, tab_height, font_size, padding, container_height):
        """Apply tab styling directly when method doesn't exist"""
        try:
            # Look for main type tabs in the GUI layout
            if hasattr(main_window, 'gui_layout'):
                gui_layout = main_window.gui_layout
                
                # Try to find main tabs
                main_tabs = None
                if hasattr(gui_layout, 'main_type_tabs'):
                    main_tabs = gui_layout.main_type_tabs
                elif hasattr(gui_layout, 'main_tab_widget'):
                    main_tabs = gui_layout.main_tab_widget
                
                if main_tabs:
                    # Apply styling directly
                    main_tabs.setMaximumHeight(main_height)
                    main_tabs.setStyleSheet(f"""
                        QTabWidget::pane {{ 
                            border: 1px solid #cccccc;
                            border-radius: 3px;
                            background-color: #ffffff;
                            margin-top: 0px;
                        }}
                        QTabBar {{
                            qproperty-drawBase: 0;
                        }}
                        QTabBar::tab {{
                            background-color: #f0f0f0;
                            border: 1px solid #cccccc;
                            border-bottom: none;
                            padding: {padding}px 8px;
                            margin-right: 2px;
                            border-radius: 3px 3px 0px 0px;
                            min-width: 80px;
                            max-height: {tab_height}px;
                            font-size: {font_size}pt;
                        }}
                        QTabBar::tab:selected {{
                            background-color: #ffffff;
                            border-bottom: 1px solid #ffffff;
                            color: #000000;
                            font-weight: bold;
                        }}
                        QTabBar::tab:hover {{
                            background-color: #e8e8e8;
                        }}
                        QTabBar::tab:!selected {{
                            margin-top: 2px;
                        }}
                    """)

                    # Update container height if possible
                    if main_tabs.parent():
                        main_tabs.parent().setMaximumHeight(container_height)

                    # Log success
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"Tab styling applied: {main_height}px height, {font_size}pt font")

        except Exception as e:
            # Silent fail for direct styling
            pass
            font_size = self.tab_font_size_spin.value()
            padding = self.tab_padding_spin.value()
            container_height = self.tab_container_height_spin.value()

            # Apply to main tabs
            main_window.gui_layout._apply_dynamic_tab_styling(
            main_height, tab_height, font_size, padding, container_height
            )

        except Exception as e:
            print(f"Error applying tab settings: {e}")


# Integration method for gui_layout.py
def _apply_dynamic_tab_styling(self, main_height, tab_height, font_size, padding, container_height):
    """Apply dynamic tab styling - called from settings"""
    if hasattr(self, 'main_type_tabs'):
        # Update tab widget height
        self.main_type_tabs.setMaximumHeight(main_height)

        # Update styling
        self.main_type_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #ffffff;
                margin-top: 0px;
            }}
            QTabBar {{
                qproperty-drawBase: 0;
            }}
            QTabBar::tab {{
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                padding: {padding}px 8px;
                margin-right: 2px;
                border-radius: 3px 3px 0px 0px;
                min-width: 80px;
                max-height: {tab_height}px;
                font-size: {font_size}pt;
            }}
            QTabBar::tab:selected {{
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
                color: #000000;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: #e8e8e8;
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """)

        # Update container height
        if hasattr(self, 'main_type_tabs') and self.main_type_tabs.parent():
            self.main_type_tabs.parent().setMaximumHeight(container_height)

        # Update splitter proportions to account for new tab height
        if hasattr(self, 'left_vertical_splitter'):
            current_sizes = self.left_vertical_splitter.sizes()
            if len(current_sizes) >= 3:
                # Adjust middle section based on tab height change
                new_sizes = [container_height, current_sizes[1], current_sizes[2]]
                self.left_vertical_splitter.setSizes(new_sizes)

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Tab styling updated: {main_height}px height, {font_size}pt font")
