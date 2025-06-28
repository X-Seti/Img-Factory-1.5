#this belongs in gui/ gui_settings.py - version 1
# $vers" X-Seti - June28 2025 - IMG Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

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
    QListWidgetItem, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon


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
    
    def _create_ui(self):
        """Create the settings UI with tabs"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.tab_widget.addTab(self._create_appearance_tab(), "🎨 Appearance")
        self.tab_widget.addTab(self._create_layout_tab(), "📐 Layout")
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
        """Create layout settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Panel sizes
        panel_group = QGroupBox("📏 Panel Sizes")
        panel_layout = QGridLayout(panel_group)
        
        # Left panel width
        panel_layout.addWidget(QLabel("Left Panel Width:"), 0, 0)
        self.left_panel_spin = QSpinBox()
        self.left_panel_spin.setRange(200, 800)
        self.left_panel_spin.setSuffix(" px")
        panel_layout.addWidget(self.left_panel_spin, 0, 1)
        
        # Right panel width
        panel_layout.addWidget(QLabel("Right Panel Width:"), 1, 0)
        self.right_panel_spin = QSpinBox()
        self.right_panel_spin.setRange(180, 600)
        self.right_panel_spin.setSuffix(" px")
        panel_layout.addWidget(self.right_panel_spin, 1, 1)
        
        # Table row height
        panel_layout.addWidget(QLabel("Table Row Height:"), 2, 0)
        self.row_height_spin = QSpinBox()
        self.row_height_spin.setRange(20, 60)
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
        self.widget_spacing_spin.setSuffix(" px")
        spacing_layout.addWidget(self.widget_spacing_spin, 0, 1)
        
        # Layout margins
        spacing_layout.addWidget(QLabel("Layout Margins:"), 1, 0)
        self.layout_margins_spin = QSpinBox()
        self.layout_margins_spin.setRange(0, 30)
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
        
        # Appearance
        theme = settings.get("theme", "img_factory")
        self.theme_combo.setCurrentText(self._theme_code_to_name(theme))
        
        # Layout
        self.left_panel_spin.setValue(settings.get("left_panel_width", 400))
        self.right_panel_spin.setValue(settings.get("right_panel_width", 300))
        self.row_height_spin.setValue(settings.get("table_row_height", 25))
        self.widget_spacing_spin.setValue(settings.get("widget_spacing", 5))
        self.layout_margins_spin.setValue(settings.get("layout_margins", 5))
        
        # Window behavior
        self.remember_size_check.setChecked(settings.get("remember_window_size", True))
        self.remember_position_check.setChecked(settings.get("remember_window_position", True))
        self.maximize_on_startup_check.setChecked(settings.get("maximize_on_startup", False))
        self.always_on_top_check.setChecked(settings.get("always_on_top", False))
        
        # Fonts
        self.font_scale_slider.setValue(int(settings.get("font_scale", 100)))
        self._update_font_scale_label()
        self.antialiasing_check.setChecked(settings.get("font_antialiasing", True))
        self.bold_headers_check.setChecked(settings.get("bold_table_headers", True))
        self.monospace_numbers_check.setChecked(settings.get("monospace_numbers", False))
        
        # Icons
        self.show_menu_icons_check.setChecked(settings.get("show_menu_icons", True))
        self.show_toolbar_icons_check.setChecked(settings.get("show_toolbar_icons", True))
        self.show_button_icons_check.setChecked(settings.get("show_button_icons", True))
        self.show_file_type_icons_check.setChecked(settings.get("show_file_type_icons", True))
        
        # Icon sizes
        self.menu_icon_size_combo.setCurrentText(f"{settings.get('menu_icon_size', 16)}px")
        self.toolbar_icon_size_combo.setCurrentText(f"{settings.get('toolbar_icon_size', 24)}px")
        self.button_icon_size_combo.setCurrentText(f"{settings.get('button_icon_size', 16)}px")
        
        # Icon style
        icon_style = settings.get("icon_style", 0)
        self.icon_style_group.button(icon_style).setChecked(True)
        
        # Behavior
        self.double_click_open_check.setChecked(settings.get("double_click_open", True))
        self.single_click_select_check.setChecked(settings.get("single_click_select", False))
        self.hover_preview_check.setChecked(settings.get("hover_preview", True))
        self.auto_resize_columns_check.setChecked(settings.get("auto_resize_columns", True))
        
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
        self.transparency_check.setChecked(settings.get("enable_transparency", False))
        self.rounded_corners_check.setChecked(settings.get("rounded_corners", True))
    
    def _update_font_scale_label(self):
        """Update font scale percentage label"""
        value = self.font_scale_slider.value()
        self.font_scale_label.setText(f"{value}%")
    
    def _choose_color(self, color_type: str):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, f"Choose {color_type.title()} Color")
        if color.isValid():
            # Store the color (you'd implement this based on your settings system)
            pass
    
    def _choose_font(self, font_type: str):
        """Open font picker dialog"""
        current_font = QFont()
        font, ok = QFontDialog.getFont(current_font, self, f"Choose {font_type.title()} Font")
        if ok:
            # Store the font (you'd implement this based on your settings system)
            pass
    
    def _theme_code_to_name(self, code: str) -> str:
        """Convert theme code to display name"""
        theme_map = {
            "img_factory": "IMG Factory Default",
            "dark": "Dark Theme",
            "light_professional": "Light Professional",
            "gta_san_andreas": "GTA San Andreas",
            "gta_vice_city": "GTA Vice City",
            "lcars": "LCARS (Star Trek)",
            "cyberpunk_2077": "Cyberpunk 2077",
            "matrix": "Matrix",
            "synthwave": "Synthwave",
            "amiga_workbench": "Amiga Workbench"
        }
        return theme_map.get(code, "IMG Factory Default")
    
    def _theme_name_to_code(self, name: str) -> str:
        """Convert display name to theme code"""
        name_map = {
            "IMG Factory Default": "img_factory",
            "Dark Theme": "dark",
            "Light Professional": "light_professional",
            "GTA San Andreas": "gta_san_andreas",
            "GTA Vice City": "gta_vice_city",
            "LCARS (Star Trek)": "lcars",
            "Cyberpunk 2077": "cyberpunk_2077",
            "Matrix": "matrix",
            "Synthwave": "synthwave",
            "Amiga Workbench": "amiga_workbench"
        }
        return name_map.get(name, "img_factory")
    
    def _apply_settings(self):
        """Apply settings without closing dialog"""
        self._save_settings()
        self.settings_changed.emit()
        QMessageBox.information(self, "Settings Applied", "GUI settings have been applied successfully!")
    
    def _save_and_close(self):
        """Save settings and close dialog"""
        self._save_settings()
        self.settings_changed.emit()
        self.accept()
    
    def _save_settings(self):
        """Save all settings to app_settings"""
        settings = self.app_settings.current_settings
        
        # Appearance
        theme_code = self._theme_name_to_code(self.theme_combo.currentText())
        if settings.get("theme") != theme_code:
            settings["theme"] = theme_code
            self.theme_changed.emit(theme_code)
        
        # Layout
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
        
        # Fonts
        settings["font_scale"] = self.font_scale_slider.value()
        settings["font_antialiasing"] = self.antialiasing_check.isChecked()
        settings["bold_table_headers"] = self.bold_headers_check.isChecked()
        settings["monospace_numbers"] = self.monospace_numbers_check.isChecked()
        
        # Icons
        settings["show_menu_icons"] = self.show_menu_icons_check.isChecked()
        settings["show_toolbar_icons"] = self.show_toolbar_icons_check.isChecked()
        settings["show_button_icons"] = self.show_button_icons_check.isChecked()
        settings["show_file_type_icons"] = self.show_file_type_icons_check.isChecked()
        
        # Icon sizes (extract number from "16px" format)
        settings["menu_icon_size"] = int(self.menu_icon_size_combo.currentText().replace("px", ""))
        settings["toolbar_icon_size"] = int(self.toolbar_icon_size_combo.currentText().replace("px", ""))
        settings["button_icon_size"] = int(self.button_icon_size_combo.currentText().replace("px", ""))
        
        # Icon style
        settings["icon_style"] = self.icon_style_group.checkedId()
        
        # Behavior
        settings["double_click_open"] = self.double_click_open_check.isChecked()
        settings["single_click_select"] = self.single_click_select_check.isChecked()
        settings["hover_preview"] = self.hover_preview_check.isChecked()
        settings["auto_resize_columns"] = self.auto_resize_columns_check.isChecked()
        
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
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "This will reset all GUI settings to their default values.\n\nContinue?",
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
                "All GUI settings have been reset to defaults!"
            )
            