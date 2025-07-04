        main_layout.addWidget(right_widget)

        # Initialize preview
        self._update_theme_info()
        self._apply_demo_theme(self.app_settings.current_settings["theme"])

        return tab

    def _create_debug_tab(self):
        """Create debug settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Debug mode group
        debug_group = QGroupBox("🐛 Debug Settings")
        debug_layout = QVBoxLayout(debug_group)
        
        # Debug mode toggle
        self.debug_enabled_check = QCheckBox("Enable debug mode")
        debug_layout.addWidget(self.debug_enabled_check)
        
        # Debug level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Debug Level:"))
        self.debug_level_combo = QComboBox()
        self.debug_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        level_layout.addWidget(self.debug_level_combo)
        level_layout.addStretch()
        debug_layout.addLayout(level_layout)
        
        # Debug categories
        categories_label = QLabel("Debug Categories:")
        debug_layout.addWidget(categories_label)
        
        self.debug_categories = {}
        categories = ["IMG_LOADING", "TABLE_POPULATION", "BUTTON_ACTIONS", "FILE_OPERATIONS", "THEME_SYSTEM"]
        
        for category in categories:
            check = QCheckBox(category)
            self.debug_categories[category] = check
            debug_layout.addWidget(check)
        
        layout.addWidget(debug_group)
        
        # Debug tools group
        tools_group = QGroupBox("🔧 Debug Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Clear log button
        clear_log_btn = QPushButton("🗑️ Clear Debug Log")
        clear_log_btn.clicked.connect(self._clear_debug_log)
        tools_layout.addWidget(clear_log_btn)
        
        # Export debug info
        export_debug_btn = QPushButton("📄 Export Debug Info")
        export_debug_btn.clicked.connect(self._export_debug_info)
        tools_layout.addWidget(export_debug_btn)
        
        layout.addWidget(tools_group)
        layout.addStretch()
        
        return tab

    def _create_interface_tab(self):
        """Create interface settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Font group
        font_group = QGroupBox("🔤 Font Settings")
        font_layout = QVBoxLayout(font_group)
        
        # Font family
        family_layout = QHBoxLayout()
        family_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Times New Roman", "Consolas"])
        family_layout.addWidget(self.font_family_combo)
        family_layout.addStretch()
        font_layout.addLayout(family_layout)
        
        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        size_layout.addWidget(self.font_size_spin)
        size_layout.addStretch()
        font_layout.addLayout(size_layout)
        
        layout.addWidget(font_group)
        
        # Interface options
        interface_group = QGroupBox("⚙️ Interface Options")
        interface_layout = QVBoxLayout(interface_group)
        
        self.tooltips_check = QCheckBox("Show tooltips")
        interface_layout.addWidget(self.tooltips_check)
        
        self.menu_icons_check = QCheckBox("Show menu icons")
        interface_layout.addWidget(self.menu_icons_check)
        
        self.button_icons_check = QCheckBox("Show button icons")
        interface_layout.addWidget(self.button_icons_check)
        
        layout.addWidget(interface_group)
        layout.addStretch()
        
        return tab

    def _load_current_settings(self):
        """Load current settings into UI"""
        # Set theme
        current_theme = self.app_settings.current_settings.get("theme", "lightgreen")
        for button in self.theme_buttons.buttons():
            if hasattr(button, 'theme_name') and button.theme_name == current_theme:
                button.setChecked(True)
                break
        
        # Set demo theme combo
        if hasattr(self, 'demo_theme_combo'):
            self.demo_theme_combo.setCurrentText(current_theme)
        
        # Set interface settings
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
        
        # Set debug settings
        if hasattr(self, 'debug_enabled_check'):
            self.debug_enabled_check.setChecked(self.app_settings.current_settings.get("debug_mode", False))
        if hasattr(self, 'debug_level_combo'):
            self.debug_level_combo.setCurrentText(self.app_settings.current_settings.get("debug_level", "INFO"))
        if hasattr(self, 'debug_categories'):
            enabled_categories = self.app_settings.current_settings.get("debug_categories", [])
            for category, checkbox in self.debug_categories.items():
                checkbox.setChecked(category in enabled_categories)

    def _on_theme_selected(self, button):
        """Handle theme selection"""
        theme_name = button.theme_name
        
        # Update theme info
        self._update_theme_info_for_theme(theme_name)
        
        # Update demo if available
        if hasattr(self, 'demo_theme_combo'):
            self.demo_theme_combo.setCurrentText(theme_name)
            self._apply_demo_theme(theme_name)

    def _update_theme_info_for_theme(self, theme_name):
        """Update theme information display"""
        if theme_name in self.app_settings.themes:
            theme_data = self.app_settings.themes[theme_name]
            info_text = f"""
            <b>{theme_data.get('name', theme_name)}</b><br>
            <i>{theme_data.get('description', 'No description available')}</i><br><br>
            <b>Author:</b> {theme_data.get('author', 'Unknown')}<br>
            <b>Version:</b> {theme_data.get('version', '1.0')}<br>
            <b>Category:</b> {theme_data.get('category', 'Standard')}<br>
            <b>Colors:</b> {len(theme_data.get('colors', {}))} defined
            """
            self.theme_info_label.setText(info_text)

    def _preview_theme_instantly(self, theme_name: str):
        """Preview theme in real-time without saving"""
        if hasattr(self, 'auto_preview_check') and self.auto_preview_check.isChecked():
            self._apply_demo_theme(theme_name)
            self._update_theme_info_for_theme(theme_name)
            self._update_preview_stats()
            
            # Update status
            if hasattr(self, 'preview_status'):
                self.preview_status.setText(f"Previewing: {theme_name}")
            if hasattr(self, 'demo_log'):
                self.demo_log.append(f"🎨 Theme preview: {theme_name}")

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
        if hasattr(self, 'demo_buttons'):
            for btn in self.demo_buttons:
                btn.setStyleSheet(stylesheet)

        if hasattr(self, 'demo_table'):
            self.demo_table.setStyleSheet(stylesheet)
        if hasattr(self, 'demo_log'):
            self.demo_log.setStyleSheet(stylesheet)

        # Apply to main dialog if instant apply is enabled
        if hasattr(self, 'instant_apply_check') and self.instant_apply_check.isChecked():
            self.setStyleSheet(stylesheet)

        # Emit theme change signal for main app
        scope = getattr(self, 'preview_scope_combo', None)
        scope_text = scope.currentText() if scope else "Full Application"
        
        if scope_text == "Full Application":
            self.themeChanged.emit(theme_name)

        # Update current theme label
        if hasattr(self, 'current_theme_label'):
            self.current_theme_label.setText(f"Current: {theme_name}")

    def _apply_quick_theme(self, theme_name: str):
        """Apply quick theme selection"""
        if hasattr(self, 'demo_theme_combo'):
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
        if hasattr(self, 'demo_theme_combo'):
            current = self.demo_theme_combo.currentText()
            if current in themes:
                themes.remove(current)  # Don't pick the same theme

        if themes:
            random_theme = random.choice(themes)
            if hasattr(self, 'demo_theme_combo'):
                self.demo_theme_combo.setCurrentText(random_theme)
            self._apply_demo_theme(random_theme)

            if hasattr(self, 'demo_log'):
                self.demo_log.append(f"🎲 Random theme: {random_theme}")

    def _toggle_instant_apply(self, enabled: bool):
        """Toggle instant apply mode"""
        if enabled:
            if hasattr(self, 'demo_theme_combo'):
                current_theme = self.demo_theme_combo.currentText()
                self._apply_demo_theme(current_theme)
            if hasattr(self, 'demo_log'):
                self.demo_log.append("⚡ Instant apply enabled")
        else:
            if hasattr(self, 'demo_log'):
                self.demo_log.append("⏸️ Instant apply disabled")

    def _change_preview_scope(self, scope: str):
        """Change preview scope"""
        if hasattr(self, 'demo_log'):
            self.demo_log.append(f"🎯 Preview scope: {scope}")
        if hasattr(self, 'demo_theme_combo'):
            current_theme = self.demo_theme_combo.currentText()
            self._apply_demo_theme(current_theme)

    def _update_theme_info(self):
        """Update theme information display"""
        if hasattr(self, 'demo_theme_combo'):
            current_theme = self.demo_theme_combo.currentText()
            self._update_theme_info_for_theme(current_theme)

    def _update_preview_stats(self):
        """Update preview statistics"""
        if hasattr(self, 'stats_labels'):
            try:
                current_count = int(self.stats_labels["Preview Changes:"].text()) + 1
                self.stats_labels["Preview Changes:"].setText(str(current_count))
                if hasattr(self, 'demo_theme_combo'):
                    self.stats_labels["Last Applied:"].setText(self.demo_theme_combo.currentText())
            except (ValueError, KeyError):
                pass

    def _reset_demo_theme(self):
        """Reset to original theme"""
        original_theme = getattr(self, '_original_theme', self.app_settings.current_settings["theme"])
        if hasattr(self, 'demo_theme_combo'):
            self.demo_theme_combo.setCurrentText(original_theme)
        self._apply_demo_theme(original_theme)
        
        # Reset stats
        if hasattr(self, 'stats_labels'):
            try:
                self.stats_labels["Preview Changes:"].setText("0")
                self.stats_labels["Last Applied:"].setText("Reset")
            except KeyError:
                pass

        if hasattr(self, 'demo_log'):
            self.demo_log.append(f"🔄 Reset to original: {original_theme}")
        if hasattr(self, 'preview_status'):
            self.preview_status.setText("Reset to original theme")

    def _clear_debug_log(self):
        """Clear debug log"""
        if hasattr(self, 'demo_log'):
            self.demo_log.clear()
            self.demo_log.append("🗑️ Debug log cleared")

    def _export_debug_info(self):
        """Export debug information"""
        debug_info = {
            "settings": self.app_settings.current_settings,
            "themes": list(self.app_settings.themes.keys()),
            "debug_enabled": self.app_settings.current_settings.get("debug_mode", False),
            "debug_level": self.app_settings.current_settings.get("debug_level", "INFO"),
            "debug_categories": self.app_settings.current_settings.get("debug_categories", [])
        }
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Debug Info", "debug_info.json", "JSON Files (*.json)"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(debug_info, f, indent=2)
                QMessageBox.information(self, "Export Complete", f"Debug info exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export debug info: {str(e)}")

    def _get_dialog_settings(self) -> dict:
        """Collect all settings from dialog controls"""
        settings = {}

        # Theme settings
        if hasattr(self, 'demo_theme_combo'):
            settings["theme"] = self.demo_theme_combo.currentText()
        elif hasattr(self, 'theme_buttons'):
            for button in self.theme_buttons.buttons():
                if button.isChecked():
                    settings["theme"] = button.theme_name
                    break

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

        # Debug settings
        if hasattr(self, 'debug_enabled_check'):
            settings['debug_mode'] = self.debug_enabled_check.isChecked()
        if hasattr(self, 'debug_level_combo'):
            settings['debug_level'] = self.debug_level_combo.currentText()
        if hasattr(self, 'debug_categories'):
            enabled_categories = []
            for category, checkbox in self.debug_categories.items():
                if checkbox.isChecked():
                    enabled_categories.append(category)
            settings['debug_categories'] = enabled_categories

        return settings

    def _apply_settings(self):
        """Apply settings permanently"""
        new_settings = self._get_dialog_settings()
        
        # Update app settings
        old_theme = self.app_settings.current_settings.get("theme", "lightgreen")
        self.app_settings.current_settings.update(new_settings)
        self.app_settings.save_settings()
        
        # Emit signals if theme changed
        if new_settings.get("theme") != old_theme:
            self.themeChanged.emit(new_settings.get("theme", old_theme))
        
        self.settingsChanged.emit()
        
        QMessageBox.information(self, "Applied", "Settings applied successfully!")
        self.accept()

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
                self.demo_theme_combo.addItem(display_name, theme_name)

            # Try to restore previous selection
            index = self.demo_theme_combo.findData(current_theme)
            if index >= 0:
                self.demo_theme_combo.setCurrentIndex(index)

            if hasattr(self, 'demo_log'):
                self.demo_log.append(f"🔄 Refreshed themes: {len(self.app_settings.themes)} available")

    def accept(self):
        """Save settings and close dialog"""
        self._apply_settings()

    def reject(self):
        """Cancel and restore original settings"""
        self.app_settings.current_settings = self.original_settings.copy()
        super().reject()


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
    
    sys.exit(0)#this belongs in utils/app_settings_system.py - version 55
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory App Settings System - Complete Version
All functionality preserved, only initialization order fixed
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QButtonGroup, QRadioButton, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox,
    QSlider, QGroupBox, QTabWidget, QDialog, QMessageBox,
    QFileDialog, QColorDialog, QFontDialog, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer
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
            "debug_categories": ["IMG_LOADING", "TABLE_POPULATION", "BUTTON_ACTIONS", "FILE_OPERATIONS"],
            # Path memory
            "remember_img_output_path": True,
            "remember_import_path": True,
            "remember_export_path": True,
            "last_img_output_path": "",
            "last_import_path": "",
            "last_export_path": "",
            # IMG defaults
            "default_img_version": "VER2",
            "default_initial_size_mb": 100,
            "auto_create_directory_structure": False,
            "compression_enabled_by_default": False,
            # Interface
            "show_menu_icons": True,
            "show_button_icons": False
        }

        # FIXED: Load themes first, then settings
        self.themes = self._load_all_themes()
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
                    "info": "#2196f3",
                    "accent_primary": "#2196f3",
                    "accent_secondary": "#ff9800",
                    "bg_primary": "#f5f5f5",
                    "bg_secondary": "#ffffff",
                    "text_primary": "#212121",
                    "text_secondary": "#757575",
                    "button_normal": "#2196f3",
                    "button_hover": "#1976d2",
                    "button_pressed": "#0d47a1",
                    "border": "#e0e0e0",
                    "action_import": "#2196f3",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0"
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
                    "info": "#2196f3",
                    "accent_primary": "#4caf50",
                    "accent_secondary": "#8bc34a",
                    "bg_primary": "#f1f8e9",
                    "bg_secondary": "#ffffff",
                    "text_primary": "#1b5e20",
                    "text_secondary": "#388e3c",
                    "button_normal": "#4caf50",
                    "button_hover": "#66bb6a",
                    "button_pressed": "#388e3c",
                    "border": "#c8e6c9",
                    "action_import": "#2196f3",
                    "action_export": "#4caf50",
                    "action_remove": "#f44336",
                    "action_update": "#ff9800",
                    "action_convert": "#9c27b0"
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
                    "info": "#99ccff",
                    "accent_primary": "#ff9900",
                    "accent_secondary": "#cc99ff",
                    "bg_primary": "#000000",
                    "bg_secondary": "#333333",
                    "text_primary": "#ff9900",
                    "text_secondary": "#cc99ff",
                    "button_normal": "#ff9900",
                    "button_hover": "#ffaa00",
                    "button_pressed": "#cc7700",
                    "border": "#666666",
                    "action_import": "#99ccff",
                    "action_export": "#99ff99",
                    "action_remove": "#ff3333",
                    "action_update": "#ff9900",
                    "action_convert": "#cc99ff"
                }
            }
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

    def _clear_debug_log(self):
        """Clear the activity log"""
        if hasattr(self, 'parent') and hasattr(self.parent(), 'gui_layout') and hasattr(self.parent().gui_layout, 'log'):
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
        """Create the enhanced settings dialog UI"""
        layout = QVBoxLayout(self)

        # Store original theme for reset
        self._original_theme = self.app_settings.current_settings["theme"]

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create all tabs
        self.theme_tab = self._create_theme_tab()
        self.tabs.addTab(self.theme_tab, "🎨 Themes")

        self.demo_tab = self._create_demo_tab()
        self.tabs.addTab(self.demo_tab, "🎭 Demo")

        self.debug_tab = self._create_debug_tab()
        self.tabs.addTab(self.debug_tab, "🐛 Debug")

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
        
        ok_btn = QPushButton("✅ Apply")
        ok_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)

    def _create_theme_tab(self):
        """Create theme selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme selection
        theme_group = QGroupBox("🎨 Theme Selection")
        theme_layout = QVBoxLayout(theme_group)
        
        # Create radio buttons for each theme
        self.theme_buttons = QButtonGroup()
        
        for theme_name, theme_data in self.app_settings.themes.items():
            radio = QRadioButton(theme_data.get("name", theme_name))
            radio.theme_name = theme_name
            self.theme_buttons.addButton(radio)
            theme_layout.addWidget(radio)
        
        layout.addWidget(theme_group)
        
        # Theme info display
        info_group = QGroupBox("ℹ️ Theme Information")
        info_layout = QVBoxLayout(info_group)
        
        self.theme_info_label = QLabel("Select a theme to view information")
        self.theme_info_label.setWordWrap(True)
        info_layout.addWidget(self.theme_info_label)
        
        layout.addWidget(info_group)
        
        # Connect signals
        self.theme_buttons.buttonClicked.connect(self._on_theme_selected)
        
        return tab

    def _create_demo_tab(self):
        """Create demo tab with live preview"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)
        
        # Left side - Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Theme Preview Group
        theme_group = QGroupBox("🎨 Theme Preview")
        theme_layout = QVBoxLayout(theme_group)
        
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Theme:"))
        self.demo_theme_combo = QComboBox()
        
        # Populate with themes
        for theme_name, theme_data in self.app_settings.themes.items():
            display_name = theme_data.get("name", theme_name)
            self.demo_theme_combo.addItem(display_name, theme_name)
        
        refresh_themes_btn = QPushButton("🔄")
        refresh_themes_btn.setToolTip("Refresh themes from disk")
        refresh_themes_btn.clicked.connect(self.refresh_themes_in_dialog)
        preview_layout.addWidget(self.demo_theme_combo)
        preview_layout.addWidget(refresh_themes_btn)
        
        self.demo_theme_combo.currentTextChanged.connect(self._preview_theme_instantly)
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
        popular_themes = ["LCARS", "lightgreen", "IMG_Factory"]
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
        button_layout.addWidget(reset_btn)
        
        random_btn = QPushButton("🎲 Random")
        random_btn.clicked.connect(self._random_theme)
        button_layout.addWidget(random_btn)
        
        quick_layout.addLayout(button_layout)
        left_layout.addWidget(quick_group)

        main_layout.addWidget(left_widget)
        
        # Right side - Demo elements
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Demo elements group
        demo_group = QGroupBox("🎭 Preview Elements")
        demo_layout = QVBoxLayout(demo_group)
        
        # Demo buttons
        self.demo_buttons = []
        button_layout = QHBoxLayout()
        
        demo_button_configs = [
            ("📥 Import", "import"),
            ("📤 Export", "export"),
            ("🗑️ Remove", "remove"),
            ("🔄 Update", "update"),
            ("🔄 Convert", "convert")
        ]
        
        for text, action_type in demo_button_configs:
            btn = QPushButton(text)
            btn.setProperty("action-type", action_type)
            btn.setMinimumHeight(35)
            self.demo_buttons.append(btn)
            button_layout.addWidget(btn)
        
        demo_layout.addLayout(button_layout)
        
        # Demo table
        self.demo_table = QTableWidget(3, 3)
        self.demo_table.setHorizontalHeaderLabels(["File", "Type", "Size"])
        self.demo_table.setMaximumHeight(120)
        
        # Add sample data
        sample_data = [
            ["file1.txt", "Text", "1.2 KB"],
            ["image.png", "Image", "45.6 KB"],
            ["data.bin", "Binary", "2.3 MB"]
        ]
        
        for row, (file, type_, size) in enumerate(sample_data):
            self.demo_table.setItem(row, 0, QTableWidgetItem(file))
            self.demo_table.setItem(row, 1, QTableWidgetItem(type_))
            self.demo_table.setItem(row, 2, QTableWidgetItem(size))
        
        demo_layout.addWidget(self.demo_table)
        
        # Demo log
        self.demo_log = QTextEdit()
        self.demo_log.setMaximumHeight(100)
        self.demo_log.setReadOnly(True)
        self.demo_log.append("🎨 Theme preview initialized")
        demo_layout.addWidget(self.demo_log)
        
        right_layout.addWidget(demo_group)
        
        # Preview status
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        
        self.preview_status = QLabel("Ready for preview")
        self.current_theme_label = QLabel(f"Current: {self.app_settings.current_settings['theme']}")
        status_layout.addWidget(self.preview_status)
        status_layout.addWidget(self.current_theme_label)
        
        # Stats
        self.stats_labels = {}
        stats_data = [
            ("Preview Changes:", "0"),
            ("Last Applied:", "None"),
            ("Themes Available:", str(len(self.app_settings.themes)))
        ]
        
        for i, (label, value) in enumerate(stats_data):
            label_widget = QLabel(label)
            value_label = QLabel(value)
            status_layout.addWidget(label_widget)
            status_layout.addWidget(value_label)
            self.stats_labels[label] = value_label

        right_layout.addWidget(status_group)
        
        main_layout.addWidget(right_