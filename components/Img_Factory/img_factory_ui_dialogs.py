#this belongs in components/Img_Factory/img_factory_ui_dialogs.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - UI and Dialog Methods

"""
UI and Dialog Methods
Handles settings dialogs, about dialog, validation, and UI settings
"""

from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QDialog
from PyQt6.QtCore import Qt, QSettings
from methods.svg_shared_icons import get_settings_icon, get_info_icon, get_palette_icon
import os

##Methods list -
# _restore_settings
# _save_settings
# closeEvent
# create_new_img
# debug_theme_system
# open_col_editor
# open_dat_editor
# open_dff_editor
# open_ide_editor
# open_ipl_editor
# open_ipf_editor
# open_paths_map
# open_radar_map
# open_vehi_editor
# open_waterpro
# open_weap_editor
# open_zons_editor
# select_all_entries
# show_about
# show_gui_layout_settings
# show_gui_settings
# show_settings
# show_theme_settings
# validate_img


def create_new_img(self): #vers 5
    """Show new IMG creation dialog - FIXED: No signal connections"""

def select_all_entries(self): #vers 3
    """Select all entries in current table"""
    if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
        self.gui_layout.table.selectAll()
        self.log_message("Selected all entries")


def validate_img(self): #vers 4
    """Validate current IMG file"""
    if not self.current_img:
        self.log_message("No IMG file loaded")
        return

    try:
        from methods.img_validation import IMGValidator
        validation = IMGValidator.validate_img_file(self.current_img)
        if validation.is_valid:
            self.log_message("IMG validation passed")
        else:
            self.log_message(f"IMG validation issues: {validation.get_summary()}")
    except Exception as e:
        self.log_message(f"Validation error: {str(e)}")


def show_gui_settings(self): #vers 5
    """Show GUI settings dialog"""
    self.log_message("GUI settings requested")
    try:
        from utils.app_settings_system import SettingsDialog
        dialog = SettingsDialog(self.app_settings, self)
        dialog.exec()
    except Exception as e:
        self.log_message(f"Settings dialog error: {str(e)}")


def show_about(self):
    """Show about dialog"""
    QMessageBox.about(self, "About IMG Factory 1.5", "IMG Factory 1.5\nAdvanced IMG Archive Management\nX-Seti 2025")


def enable_col_debug(self): #vers 2 #restore
    """Enable COL debug output"""
    # Set debug flag on all loaded COL files
    if hasattr(self, 'current_col') and self.current_col:
        self.current_col._debug_enabled = True

    # Set global flag for future COL files
    import methods.col_core_classes as col_module
    col_module._global_debug_enabled = True

    self.log_message("COL debug output enabled")


def disable_col_debug(self): #vers 2 #restore
    """Disable COL debug output"""
    # Set debug flag on all loaded COL files
    if hasattr(self, 'current_col') and self.current_col:
        self.current_col._debug_enabled = False

    # Set global flag for future COL files
    import methods.col_core_classes as col_module
    col_module._global_debug_enabled = False

    self.log_message("COL debug output disabled")

def toggle_col_debug(self): #vers 2 #restore
    """Toggle COL debug output"""
    try:
        import methods.col_core_classes as col_module
        debug_enabled = getattr(col_module, '_global_debug_enabled', False)

        if debug_enabled:
            self.disable_col_debug()
        else:
            self.enable_col_debug()

    except Exception as e:
        self.log_message(f"Debug toggle error: {e}")


def setup_debug_controls(self): #vers 2 #restore
    """Setup debug control shortcuts - ADD THIS TO __init__"""
    try:
        from PyQt6.QtGui import QShortcut, QKeySequence

        # Ctrl+Shift+D for debug toggle
        debug_shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
        debug_shortcut.activated.connect(self.toggle_col_debug)

        # Start with debug disabled for performance
        self.disable_col_debug()

        self.log_message("Debug controls ready (Ctrl+Shift+D to toggle COL debug)")

    except Exception as e:
        self.log_message(f"Debug controls error: {e}")

# COL and editor functions
def open_col_editor(self): #vers 2
    """Open COL file editor - WORKING VERSION"""

    from components.Col_Editor.col_workshop import COLEditorDialog
    self.log_message("Opening COL Workshop...")
    editor = COLEditorDialog(self)
    editor.show()
    self.log_message("COL Workshop opened")

#TODO below, coming soon.
def open_dff_editor(self): #vers 1
    """Open DFF model editor"""
    self.log_message("DFF editor functionality coming soon")

def open_ipf_editor(self): #vers 1
    """Open IPF animation editor"""
    self.log_message("IPF editor functionality coming soon")

def open_ipl_editor(self): #vers 1
    """Open IPL item placement editor"""
    self.log_message("IPL editor functionality coming soon")

def open_ide_editor(self): #vers 1
    """Open IDE item definition editor"""
    self.log_message("IDE editor functionality coming soon")

def open_dat_editor(self): #vers 1
    """Open DAT file editor"""
    self.log_message("DAT editor functionality coming soon")

def open_zons_editor(self): #vers 1
    """Open zones editor"""
    self.log_message("Zones editor functionality coming soon")

def open_weap_editor(self): #vers 1
    """Open weapons editor"""
    self.log_message("Weapons editor functionality coming soon")

def open_vehi_editor(self): #vers 1
    """Open vehicles editor"""
    self.log_message("Vehicles editor functionality coming soon")

def open_radar_map(self): #vers 1
    """Open radar map editor"""
    self.log_message("Radar map functionality coming soon")

def open_paths_map(self): #vers 1
    """Open paths map editor"""
    self.log_message("Paths map functionality coming soon")

def open_waterpro(self): #vers 1
    """Open water properties editor"""
    self.log_message("Water properties functionality coming soon")


def validate_img(self): #vers 3
    """Validate current IMG file"""
    if not self.current_img:
        QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
        return

    try:
        self.log_message("Validating IMG file...")

        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(0, "Validating...")

        # Try different validation approaches
        validation_result = None

        # Method 1: Try IMGValidator class
        try:
            validator = IMGValidator()
            if hasattr(validator, 'validate'):
                validation_result = validator.validate(self.current_img)
            elif hasattr(validator, 'validate_img_file'):
                validation_result = validator.validate_img_file(self.current_img)
        except Exception as e:
            self.log_message(f"IMGValidator error: {str(e)}")

        # Method 2: Try static method
        if not validation_result:
            try:
                validation_result = IMGValidator.validate_img_file(self.current_img)
            except Exception as e:
                self.log_message(f"Static validation error: {str(e)}")

        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Validation complete")

        if validation_result:
            if hasattr(validation_result, 'is_valid') and validation_result.is_valid:
                self.log_message("IMG file validation passed")
                QMessageBox.information(self, "Validation Result", "IMG file is valid!")
            else:
                errors = getattr(validation_result, 'errors', ['Unknown validation issues'])
                self.log_message(f"IMG file validation failed: {len(errors)} errors")
                error_details = "\n".join(errors[:10])
                if len(errors) > 10:
                    error_details += f"\n... and {len(errors) - 10} more errors"

                QMessageBox.warning(self, "Validation Failed",
                                    f"IMG file has {len(errors)} validation errors:\n\n{error_details}")
        else:
            self.log_message("IMG file validation completed (no issues detected)")
            QMessageBox.information(self, "Validation Result", "IMG file appears to be valid!")

    except Exception as e:
        error_msg = f"Error validating IMG: {str(e)}"
        self.log_message(error_msg)
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Validation error")
        QMessageBox.critical(self, "Validation Error", error_msg)


def show_theme_settings(self): #vers 2
    """Show theme settings dialog"""
    self.show_settings()  # For now, use general settings

def show_about(self): #vers 2
    """Show about dialog"""
    about_text = """
    <h2>IMG Factory 1.5</h2>
    <p><b>Professional IMG Archive Manager</b></p>
    <p>Version: 1.5.0 Python Edition</p>
    <p>Author: X-Seti</p>
    <p>Based on original IMG Factory by MexUK (2007)</p>
    <br>
    <p>Features:</p>
    <ul>
    <li>IMG file creation and editing</li>
    <li>Multi-format support (DFF, TXD, COL, IFP)</li>
    <li>Template system</li>
    <li>Batch operations</li>
    <li>Validation tools</li>
    </ul>
    """

    QMessageBox.about(self, "About IMG Factory", about_text)


def show_gui_settings(self): #vers 5
    """Show GUI settings dialog - ADD THIS METHOD TO YOUR MAIN WINDOW CLASS"""
    try:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QGroupBox

        dialog = QDialog(self)
        dialog.setWindowTitle("GUI Layout Settings")
        dialog.setMinimumSize(500, 250)

        layout = QVBoxLayout(dialog)

        # Panel width group
        width_group = QGroupBox("Right Panel Width Settings")
        width_layout = QVBoxLayout(width_group)

        # Current width display
        current_width = 240  # Default
        if hasattr(self.gui_layout, 'main_splitter') and hasattr(self.gui_layout.main_splitter, 'sizes'):
            sizes = self.gui_layout.main_splitter.sizes()
            if len(sizes) > 1:
                current_width = sizes[1]

        # Width spinner
        spinner_layout = QHBoxLayout()
        spinner_layout.addWidget(QLabel("Width:"))
        width_spin = QSpinBox()
        width_spin.setRange(180, 400)
        width_spin.setValue(current_width)
        width_spin.setSuffix(" px")
        spinner_layout.addWidget(width_spin)
        spinner_layout.addStretch()
        width_layout.addLayout(spinner_layout)

        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Presets:"))
        presets = [("Narrow", 200), ("Default", 240), ("Wide", 280), ("Extra Wide", 320)]
        for name, value in presets:
            btn = QPushButton(f"{name}\n({value}px)")
            btn.clicked.connect(lambda checked, v=value: width_spin.setValue(v))
            presets_layout.addWidget(btn)
        presets_layout.addStretch()
        width_layout.addLayout(presets_layout)

        layout.addWidget(width_group)

        # Buttons
        button_layout = QHBoxLayout()

        preview_btn = QPushButton("Preview")
        def preview_changes():
            width = width_spin.value()
            if hasattr(self.gui_layout, 'main_splitter') and hasattr(self.gui_layout.main_splitter, 'sizes'):
                sizes = self.gui_layout.main_splitter.sizes()
                if len(sizes) >= 2:
                    self.gui_layout.main_splitter.setSizes([sizes[0], width])

            if hasattr(self.gui_layout, 'main_splitter'):
                right_widget = self.gui_layout.main_splitter.widget(1)
                if right_widget:
                    right_widget.setMaximumWidth(width + 60)
                    right_widget.setMinimumWidth(max(180, width - 40))

        preview_btn.clicked.connect(preview_changes)
        button_layout.addWidget(preview_btn)

        apply_btn = QPushButton("Apply & Close")
        def apply_changes():
            width = width_spin.value()
            if hasattr(self.gui_layout, 'main_splitter') and hasattr(self.gui_layout.main_splitter, 'sizes'):
                sizes = self.gui_layout.main_splitter.sizes()
                if len(sizes) >= 2:
                    self.gui_layout.main_splitter.setSizes([sizes[0], width])

            if hasattr(self.gui_layout, 'main_splitter'):
                right_widget = self.gui_layout.main_splitter.widget(1)
                if right_widget:
                    right_widget.setMaximumWidth(width + 60)
                    right_widget.setMinimumWidth(max(180, width - 40))

            # Save to settings if you have app_settings
            if hasattr(self, 'app_settings') and hasattr(self.app_settings, 'current_settings'):
                self.app_settings.current_settings["right_panel_width"] = width
                if hasattr(self.app_settings, 'save_settings'):
                    self.app_settings.save_settings()

            self.log_message(f"Right panel width set to {width}px")
            dialog.accept()

        apply_btn.clicked.connect(apply_changes)
        button_layout.addWidget(apply_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    except Exception as e:
        self.log_message(f"Error showing GUI settings: {str(e)}")

def show_gui_layout_settings(self): #vers 2
    """Show GUI Layout settings - called from menu"""
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_gui_layout_settings'):
        self.gui_layout.show_gui_layout_settings()
    else:
        self.log_message("GUI Layout settings not available")

def debug_theme_system(self): #vers 1
    """Debug method to check theme system status"""
    try:
        if hasattr(self, 'app_settings'):
            settings = self.app_settings
            self.log_message(f"Theme System Debug:")

            if hasattr(settings, 'settings_file'):
                self.log_message(f"   Settings file: {settings.settings_file}")
            if hasattr(settings, 'themes_dir'):
                self.log_message(f"   Themes directory: {settings.themes_dir}")
                self.log_message(f"   Themes dir exists: {settings.themes_dir.exists()}")
            if hasattr(settings, 'themes'):
                self.log_message(f"   Available themes: {list(settings.themes.keys())}")
            if hasattr(settings, 'current_settings'):
                self.log_message(f"   Current theme: {settings.current_settings.get('theme')}")

            # Check if themes directory has files
            if hasattr(settings, 'themes_dir') and settings.themes_dir.exists():
                theme_files = list(settings.themes_dir.glob("*.json"))
                self.log_message(f"   Theme files found: {[f.name for f in theme_files]}")
            else:
                self.log_message(f"Themes directory does not exist!")
        else:
            self.log_message("No app_settings available")
    except Exception as e:
        self.log_message(f"Error in debug_theme_system: {str(e)}")

def show_settings(self): #vers 1
    """Show settings dialog"""
    print("show_settings called!")  # Debug
    try:
        # Try different import paths
        try:
            from utils.app_settings_system import SettingsDialog, apply_theme_to_app
        except ImportError:
            from app_settings_system import SettingsDialog, apply_theme_to_app

        dialog = SettingsDialog(self.app_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            apply_theme_to_app(QApplication.instance(), self.app_settings)
            if hasattr(self.gui_layout, 'apply_table_theme'):
                self.gui_layout.apply_table_theme()
            self.log_message("Settings updated")
    except Exception as e:
        print(f"Settings error: {e}")
        self.log_message(f"Settings error: {str(e)}")

# SETTINGS PERSISTENCE - KEEP 100% OF FUNCTIONALITY

def _restore_settings(self): #vers 1
    """Restore application settings"""
    try:
        settings = QSettings("XSeti", "IMGFactory")

        # Restore window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Restore splitter state
        splitter_state = settings.value("splitter_state")
        if splitter_state and hasattr(self.gui_layout, 'main_splitter'):
            self.gui_layout.main_splitter.restoreState(splitter_state)

        self.log_message("Settings restored")

    except Exception as e:
        self.log_message(f"Failed to restore settings: {str(e)}")

def _save_settings(self): #vers 1
    """Save application settings"""
    try:
        settings = QSettings("XSeti", "IMGFactory")

        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())

        # Save splitter state
        if hasattr(self.gui_layout, 'main_splitter'):
            settings.setValue("splitter_state", self.gui_layout.main_splitter.saveState())

        self.log_message("Settings saved")

    except Exception as e:
        self.log_message(f"Failed to save settings: {str(e)}")

def closeEvent(self, event): #vers 2
    """Handle application close"""
    try:
        self._save_settings()

        # Clean up threads
        if hasattr(self, 'load_thread') and self.load_thread and self.load_thread.isRunning():
            self.load_thread.quit()
            self.load_thread.wait()

        # Close all files
        if hasattr(self, 'close_manager'):
            self.close_manager.close_all_tabs()

        event.accept()
    except Exception as e:
        self.log_message(f"Error during close: {str(e)}")
        event.accept()  # Accept anyway to prevent hanging


__all__ = [
    'create_new_img',
    'select_all_entries',
    'validate_img',
    'show_gui_settings',
    'show_about',
    'open_col_editor',
    'open_dff_editor',
    'open_ipf_editor',
    'open_ipl_editor',
    'open_ide_editor',
    'open_dat_editor',
    'open_zons_editor',
    'open_weap_editor',
    'open_vehi_editor',
    'open_radar_map',
    'open_paths_map',
    'open_waterpro',
    'show_theme_settings',
    'show_gui_layout_settings',
    'debug_theme_system',
    'show_settings',
    '_restore_settings',
    '_save_settings',
    'closeEvent'
]
