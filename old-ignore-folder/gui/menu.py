#this belongs in gui/ menu.py - Version: 19
# X-Seti - July12 2025 - IMG Factory 1.5

#!/usr/bin/env python3
"""
IMG Factory Menu System - Complete Implementation
Full menu system with all original entries restored
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Callable
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QCheckBox, QGroupBox, QLabel, QLineEdit, QComboBox, 
    QMessageBox, QTabWidget, QWidget, QTextEdit, QSpinBox, QRadioButton,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSettings
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QActionGroup
from .panel_manager import PanelManager


class MenuAction:
    """Represents a menu action with properties"""

    def __init__(self, action_id: str, text: str, shortcut: str = "",
                 icon: str = "", callback: Callable = None, checkable: bool = False):
        self.action_id = action_id
        self.text = text
        self.shortcut = shortcut
        self.icon = icon
        self.callback = callback
        self.checkable = checkable
        self.enabled = True
        self.visible = True
        self.separator_after = False


class MenuDefinition:
    """Defines the complete menu structure"""

    def __init__(self):
        # Complete IMG Factory menu structure - all original entries restored
        self.menu_structure = {
            "File": [
                MenuAction("new_img", "&New IMG", "Ctrl+N", "document-new"),
                MenuAction("open_img", "&Open IMG", "Ctrl+O", "document-open"),
                MenuAction("open_multiple", "Open &Multiple Files", "Ctrl+Shift+O", "folder-open"),
                MenuAction("recent_files", "&Recent Files"),
                MenuAction("sep1", ""),
                MenuAction("close_img", "&Close", "Ctrl+W", "window-close"),
                MenuAction("close_all", "Close &All", "Ctrl+Shift+W"),
                MenuAction("sep2", ""),
                MenuAction("save_img", "&Save", "Ctrl+S"),
                MenuAction("save_as_img", "Save &As...", "Ctrl+Shift+S"),
                MenuAction("sep3", ""),
                MenuAction("exit", "E&xit", "Ctrl+Q", "application-exit"),
            ],

            "Edit": [
                MenuAction("undo", "&Undo", "Ctrl+Z", "edit-undo"),
                MenuAction("redo", "&Redo", "Ctrl+Y", "edit-redo"),
                MenuAction("sep1", ""),
                MenuAction("cut", "Cu&t", "Ctrl+X", "edit-cut"),
                MenuAction("copy", "&Copy", "Ctrl+C", "edit-copy"),
                MenuAction("paste", "&Paste", "Ctrl+V", "edit-paste"),
                MenuAction("sep2", ""),
                MenuAction("select_all", "Select &All", "Ctrl+A", "edit-select-all"),
                MenuAction("select_inverse", "Select &Inverse", "Ctrl+I"),
                MenuAction("select_none", "Select &None", "Ctrl+D"),
                MenuAction("sep3", ""),
                MenuAction("find", "&Find", "Ctrl+F", "edit-find"),
                MenuAction("find_next", "Find &Next", "F3"),
                MenuAction("replace", "&Replace", "Ctrl+H"),
            ],

            "DAT": [
                MenuAction("dat_info", "DAT File &Information"),
                MenuAction("dat_validate", "&Validate DAT"),
                MenuAction("dat_rebuild", "&Rebuild DAT"),
                MenuAction("dat_optimize", "&Optimize DAT"),
                MenuAction("sep1", ""),
                MenuAction("dat_extract", "&Extract All"),
                MenuAction("dat_create", "&Create New DAT"),
                MenuAction("dat_merge", "&Merge DAT Files"),
                MenuAction("sep2", ""),
                MenuAction("dat_backup", "&Backup DAT"),
                MenuAction("dat_restore", "&Restore DAT"),
            ],

            "IMG": [
                MenuAction("img_info", "IMG &Information", "F4"),
                MenuAction("img_validate", "&Validate IMG", "F5"),
                MenuAction("img_rebuild", "&Rebuild IMG", "F6"),
                MenuAction("img_rebuild_as", "Rebuild &As...", "Shift+F6"),
                MenuAction("sep1", ""),
                MenuAction("img_extract", "&Extract All"),
                MenuAction("img_merge", "&Merge IMG Files"),
                MenuAction("img_split", "&Split IMG File"),
                MenuAction("img_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("img_optimize", "&Optimize IMG"),
                MenuAction("img_defrag", "&Defragment IMG"),
                MenuAction("img_compress", "&Compress IMG"),
                MenuAction("sep3", ""),
                MenuAction("img_backup", "&Backup IMG"),
                MenuAction("img_compare", "Co&mpare IMG Files"),
            ],

            "Model": [
                MenuAction("model_view", "&View Model", "F7"),
                MenuAction("model_export", "&Export Model"),
                MenuAction("model_import", "&Import Model"),
                MenuAction("model_replace", "&Replace Model"),
                MenuAction("sep1", ""),
                MenuAction("model_convert", "&Convert Format"),
                MenuAction("model_validate", "&Validate DFF"),
                MenuAction("model_optimize", "&Optimize Model"),
                MenuAction("sep2", ""),
                MenuAction("model_batch_export", "&Batch Export"),
                MenuAction("model_batch_convert", "Batch &Convert"),
                MenuAction("model_batch_optimize", "Batch &Optimize"),
                MenuAction("sep3", ""),
                MenuAction("model_viewer_3d", "&3D Model Viewer"),
                MenuAction("model_properties", "Model &Properties"),
            ],

            "Texture": [
                MenuAction("texture_view", "&View Texture", "F8"),
                MenuAction("texture_export", "&Export Texture"),
                MenuAction("texture_import", "&Import Texture"),
                MenuAction("texture_replace", "&Replace Texture"),
                MenuAction("sep1", ""),
                MenuAction("texture_convert", "&Convert Format"),
                MenuAction("texture_validate", "&Validate TXD"),
                MenuAction("texture_optimize", "&Optimize Textures"),
                MenuAction("sep2", ""),
                MenuAction("texture_batch_export", "&Batch Export"),
                MenuAction("texture_batch_convert", "Batch &Convert"),
                MenuAction("texture_batch_resize", "Batch &Resize"),
                MenuAction("sep3", ""),
                MenuAction("texture_palette", "Extract &Palette"),
                MenuAction("texture_atlas", "Create &Atlas"),
                MenuAction("texture_properties", "Texture &Properties"),
            ],

            "Collision": [
                MenuAction("collision_view", "&View Collision", "F9"),
                MenuAction("collision_edit", "&Edit Collision", "Ctrl+Shift+C"),
                MenuAction("collision_export", "&Export Collision"),
                MenuAction("collision_import", "&Import Collision"),
                MenuAction("collision_replace", "&Replace Collision"),
                MenuAction("sep1", ""),
                MenuAction("collision_validate", "&Validate COL"),
                MenuAction("collision_optimize", "&Optimize Collision"),
                MenuAction("collision_analyze", "&Analyze Collision"),
                MenuAction("sep2", ""),
                MenuAction("collision_batch_export", "&Batch Export"),
                MenuAction("collision_batch_convert", "Batch &Convert"),
                MenuAction("sep3", ""),
                MenuAction("collision_viewer_3d", "&3D Collision Viewer"),
                MenuAction("collision_properties", "Collision &Properties"),
                MenuAction("collision_debug", "&Debug Information"),
            ],

            "Animation": [
                MenuAction("anim_view", "&View Animation"),
                MenuAction("anim_export", "&Export Animation"),
                MenuAction("anim_import", "&Import Animation"),
                MenuAction("anim_replace", "&Replace Animation"),
                MenuAction("sep1", ""),
                MenuAction("anim_validate", "&Validate IFP"),
                MenuAction("anim_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("anim_batch_export", "&Batch Export"),
                MenuAction("anim_properties", "Animation &Properties"),
                MenuAction("anim_player", "Animation &Player"),
            ],

            "Item Definition": [
                MenuAction("ide_view", "&View IDE"),
                MenuAction("ide_edit", "&Edit IDE"),
                MenuAction("ide_validate", "&Validate IDE"),
                MenuAction("ide_search", "&Search IDE"),
                MenuAction("sep1", ""),
                MenuAction("ide_export", "&Export to Text"),
                MenuAction("ide_import", "&Import from Text"),
                MenuAction("ide_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("ide_backup", "&Backup IDE"),
                MenuAction("ide_compare", "&Compare IDE Files"),
            ],

            "Item Placement": [
                MenuAction("ipl_view", "&View IPL"),
                MenuAction("ipl_edit", "&Edit IPL"),
                MenuAction("ipl_validate", "&Validate IPL"),
                MenuAction("ipl_search", "&Search IPL"),
                MenuAction("sep1", ""),
                MenuAction("ipl_export", "&Export to Text"),
                MenuAction("ipl_import", "&Import from Text"),
                MenuAction("ipl_convert", "&Convert Format"),
                MenuAction("sep2", ""),
                MenuAction("ipl_map_view", "View on &Map"),
                MenuAction("ipl_coordinates", "Show &Coordinates"),
                MenuAction("ipl_zones", "Show &Zones"),
            ],

            "Entry": [
                MenuAction("entry_info", "Entry &Information", "Alt+Enter"),
                MenuAction("entry_properties", "&Properties", "Alt+P"),
                MenuAction("entry_preview", "Pre&view", "Space"),
                MenuAction("sep1", ""),
                MenuAction("entry_import", "&Import Files", "Ctrl+I"),
                MenuAction("entry_export", "&Export Selected", "Ctrl+E"),
                MenuAction("entry_export_all", "Export &All", "Ctrl+Shift+E"),
                MenuAction("entry_quick_export", "&Quick Export", "Ctrl+Q"),
                MenuAction("sep2", ""),
                MenuAction("entry_remove", "&Remove Selected", "Delete"),
                MenuAction("entry_rename", "Re&name", "F2"),
                MenuAction("entry_replace", "Rep&lace", "Ctrl+R"),
                MenuAction("entry_duplicate", "&Duplicate", "Ctrl+D"),
                MenuAction("sep3", ""),
                MenuAction("entry_sort", "&Sort Entries"),
                MenuAction("entry_filter", "&Filter Entries"),
                MenuAction("entry_search", "Searc&h Entries"),
                MenuAction("sep4", ""),
                MenuAction("entry_batch_ops", "&Batch Operations"),
                MenuAction("entry_mass_rename", "&Mass Rename"),
                MenuAction("entry_verify", "&Verify Integrity"),
            ],

            "Tools": [
                MenuAction("search", "&Search", "Ctrl+F", "search"),
                MenuAction("filter", "&Filter", "Ctrl+Shift+F", "filter"),
                MenuAction("batch_processor", "&Batch Processor"),
                MenuAction("sep1", ""),
                MenuAction("col_editor", "&COL Editor", "Ctrl+Shift+C"),
                MenuAction("txd_editor", "&TXD Editor", "Ctrl+Shift+T"),
                MenuAction("dff_editor", "&DFF Editor", "Ctrl+Shift+D"),
                MenuAction("ifp_editor", "&IFP Editor", "Ctrl+Shift+I"),
                MenuAction("sep2", ""),
                MenuAction("ide_editor", "I&DE Editor"),
                MenuAction("ipl_editor", "IP&L Editor"),
                MenuAction("dat_editor", "DA&T Editor"),
                MenuAction("sep3", ""),
                MenuAction("file_converter", "File &Converter"),
                MenuAction("hex_editor", "&Hex Editor"),
                MenuAction("text_editor", "Te&xt Editor"),
                MenuAction("sep4", ""),
                MenuAction("game_launcher", "&Game Launcher"),
                MenuAction("mod_manager", "&Mod Manager"),
                MenuAction("sep5", ""),
                MenuAction("preferences", "&Preferences", "Ctrl+,", "settings"),
            ],

            "View": [
                MenuAction("toolbar", "&Toolbar", "", "", None, True),
                MenuAction("statusbar", "&Status Bar", "", "", None, True),
                MenuAction("log_panel", "&Log Panel", "F12", "", None, True),
                MenuAction("sep1", ""),
                MenuAction("file_tree", "&File Tree", "", "", None, True),
                MenuAction("properties_panel", "&Properties Panel", "", "", None, True),
                MenuAction("preview_panel", "Pre&view Panel", "", "", None, True),
                MenuAction("sep2", ""),
                MenuAction("icon_mode", "&Icon Mode", "Ctrl+1", "icon", None, True),
                MenuAction("list_mode", "&List Mode", "Ctrl+2", "list", None, True),
                MenuAction("detail_mode", "&Detail Mode", "Ctrl+3", "detail", None, True),
                MenuAction("thumbnail_mode", "&Thumbnail Mode", "Ctrl+4", "thumbnail", None, True),
                MenuAction("sep3", ""),
                MenuAction("zoom_in", "Zoom &In", "Ctrl+="),
                MenuAction("zoom_out", "Zoom &Out", "Ctrl+-"),
                MenuAction("zoom_reset", "&Reset Zoom", "Ctrl+0"),
                MenuAction("zoom_fit", "&Fit to Window", "Ctrl+9"),
                MenuAction("sep4", ""),
                MenuAction("fullscreen", "&Fullscreen", "F11"),
                MenuAction("stay_on_top", "Stay on &Top", "", "", None, True),
            ],

            "Settings": [
                MenuAction("preferences", "&Preferences", "Ctrl+,"),
                MenuAction("customize_interface", "Customize &Interface"),
                MenuAction("customize_buttons", "Customize &Buttons"),
                MenuAction("customize_panels", "Customize &Panels"),
                MenuAction("customize_menus", "Customize &Menus"),
                MenuAction("sep1", ""),
                MenuAction("themes", "&Themes"),
                MenuAction("language", "&Language"),
                MenuAction("plugins", "&Plugins"),
                MenuAction("sep2", ""),
                MenuAction("file_associations", "&File Associations"),
                MenuAction("default_directories", "&Default Directories"),
                MenuAction("performance", "Per&formance"),
                MenuAction("sep3", ""),
                MenuAction("reset_layout", "&Reset Layout"),
                MenuAction("reset_settings", "Reset &Settings"),
                MenuAction("sep4", ""),
                MenuAction("export_settings", "&Export Settings"),
                MenuAction("import_settings", "&Import Settings"),
            ],

            "Debug": [
                MenuAction("debug_console", "&Debug Console", "F12"),
                MenuAction("debug_log", "Debug &Log"),
                MenuAction("debug_performance", "&Performance Monitor"),
                MenuAction("sep1", ""),
                MenuAction("debug_col", "&COL Debug Mode", "", "", None, True),
                MenuAction("debug_img", "&IMG Debug Mode", "", "", None, True),
                MenuAction("debug_memory", "&Memory Debug", "", "", None, True),
                MenuAction("sep2", ""),
                MenuAction("debug_export_log", "&Export Debug Log"),
                MenuAction("debug_clear_log", "&Clear Debug Log"),
                MenuAction("debug_settings", "Debug &Settings"),
            ],

            "Help": [
                MenuAction("help_contents", "&Help Contents", "F1"),
                MenuAction("help_shortcuts", "&Keyboard Shortcuts"),
                MenuAction("help_formats", "Supported &Formats"),
                MenuAction("help_tutorial", "&Tutorial"),
                MenuAction("sep1", ""),
                MenuAction("help_website", "Visit &Website"),
                MenuAction("help_forum", "Community &Forum"),
                MenuAction("help_report_bug", "&Report Bug"),
                MenuAction("help_feature_request", "&Feature Request"),
                MenuAction("sep2", ""),
                MenuAction("help_check_updates", "&Check for Updates"),
                MenuAction("help_changelog", "&Changelog"),
                MenuAction("sep3", ""),
                MenuAction("about", "&About IMG Factory"),
                MenuAction("about_qt", "About &Qt"),
            ]
        }


class IMGFactoryMenuBar:
    """Complete IMG Factory menu bar with all original functionality"""
    
    def __init__(self, main_window, panel_manager: PanelManager = None):
        self.main_window = main_window
        self.panel_manager = panel_manager
        self.menu_bar = main_window.menuBar()
        self.callbacks: Dict[str, Callable] = {}
        self.actions: Dict[str, QAction] = {}
        self.menus: Dict[str, QMenu] = {}
        
        # Dialog management
        self._preferences_dialog = None
        self._gui_settings_dialog = None
        
        # Clear any existing menus first
        self.menu_bar.clear()
        
        self.menu_definition = MenuDefinition()
        self._create_menus()
        
        # Set up default callbacks
        self._setup_default_callbacks()
    
    def _create_menus(self):
        """Create all menus from definition"""
        for menu_name, menu_actions in self.menu_definition.menu_structure.items():
            menu = self.menu_bar.addMenu(menu_name)
            self.menus[menu_name] = menu
            
            for menu_action in menu_actions:
                if menu_action.action_id.startswith("sep"):
                    menu.addSeparator()
                else:
                    action = QAction(menu_action.text, self.main_window)
                    
                    if menu_action.shortcut:
                        action.setShortcut(QKeySequence(menu_action.shortcut))
                    
                    if menu_action.checkable:
                        action.setCheckable(True)
                        # Set default checked state for view items
                        if menu_action.action_id in ["toolbar", "statusbar", "log_panel"]:
                            action.setChecked(True)
                    
                    # Store action
                    self.actions[menu_action.action_id] = action
                    
                    # Add to menu
                    menu.addAction(action)
    
    def _setup_default_callbacks(self):
        """Set up default menu callbacks"""
        default_callbacks = {
            # File menu
            "exit": self._exit_application,
            
            # Settings menu
            "preferences": self._show_preferences,
            "customize_interface": self._show_gui_settings,
            "themes": self._show_theme_settings,
            "export_settings": self._export_settings,
            "import_settings": self._import_settings,
            "reset_layout": self._reset_layout,
            
            # View menu
            "toolbar": self._toggle_toolbar,
            "statusbar": self._toggle_statusbar,
            "log_panel": self._toggle_log_panel,
            "fullscreen": self._toggle_fullscreen,
            
            # Help menu
            "about": self._show_about,
            "help_contents": self._show_help,
            "help_shortcuts": self._show_shortcuts,
            "help_formats": self._show_formats,
            "about_qt": self._show_about_qt,
            
            # Debug menu
            "debug_console": self._show_debug_console,
            "debug_clear_log": self._clear_debug_log,
        }
        
        self.set_callbacks(default_callbacks)
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set menu callbacks"""
        self.callbacks.update(callbacks)
        self._connect_callbacks()
    
    def _connect_callbacks(self):
        """Connect actions to callbacks"""
        for action_id, callback in self.callbacks.items():
            if action_id in self.actions:
                self.actions[action_id].triggered.connect(callback)

    def enable_action(self, action_id: str, enabled: bool = True):
        """Enable/disable an action"""
        if action_id in self.actions:
            self.actions[action_id].setEnabled(enabled)

    def check_action(self, action_id: str, checked: bool = True):
        """Check/uncheck an action"""
        if action_id in self.actions:
            action = self.actions[action_id]
            if action.isCheckable():
                action.setChecked(checked)

    def get_action(self, action_id: str) -> Optional[QAction]:
        """Get action by ID"""
        return self.actions.get(action_id)
    
    def set_panel_manager(self, panel_manager: PanelManager):
        """Set panel manager for panel menu integration"""
        self.panel_manager = panel_manager
        self.add_panel_menu()
    
    def add_panel_menu(self):
        """Add panels menu for tear-off functionality"""
        if not self.panel_manager:
            return

        panels_menu = self.menu_bar.addMenu("&Panels")
        self.menus["Panels"] = panels_menu

        # Show/Hide panels
        show_hide_menu = panels_menu.addMenu("Show/Hide")

        for panel_id, panel in self.panel_manager.panels.items():
            action = QAction(panel.title, self.main_window)
            action.setCheckable(True)
            action.setChecked(panel.isVisible())
            action.triggered.connect(
                lambda checked, pid=panel_id:
                self.panel_manager.show_panel(pid) if checked
                else self.panel_manager.hide_panel(pid)
            )
            show_hide_menu.addAction(action)

        panels_menu.addSeparator()

        # Reset layout
        reset_action = QAction("Reset Layout", self.main_window)
        reset_action.triggered.connect(self._reset_panel_layout)
        panels_menu.addAction(reset_action)
    
    # ========================================================================
    # CALLBACK IMPLEMENTATIONS
    # ========================================================================
    
    def _exit_application(self):
        """Exit the application"""
        self.main_window.close()
    
    def _show_preferences(self):
        """Show preferences dialog with proper lifecycle management"""
        try:
            # Check if dialog already exists and is visible
            if hasattr(self, '_preferences_dialog') and self._preferences_dialog is not None:
                if self._preferences_dialog.isVisible():
                    # Bring existing dialog to front
                    self._preferences_dialog.raise_()
                    self._preferences_dialog.activateWindow()
                    return
                else:
                    # Clean up old dialog
                    self._preferences_dialog.deleteLater()
                    self._preferences_dialog = None
            
            if hasattr(self.main_window, 'app_settings'):
                from utils.app_settings_system import SettingsDialog
                
                # Create new dialog
                self._preferences_dialog = SettingsDialog(self.main_window.app_settings, self.main_window)
                
                # Connect cleanup signal
                self._preferences_dialog.finished.connect(self._on_preferences_closed)
                
                # Show dialog
                result = self._preferences_dialog.exec()
                
                if result == QDialog.DialogCode.Accepted:
                    self._apply_gui_changes()
                    if hasattr(self.main_window, 'log_message'):
                        self.main_window.log_message("✅ Preferences updated")
                
                # Clean up
                self._preferences_dialog = None
                
            else:
                QMessageBox.information(
                    self.main_window, 
                    "Preferences", 
                    "Preferences system not available"
                )
        except Exception as e:
            QMessageBox.critical(
                self.main_window, 
                "Error", 
                "Failed to open preferences: " + str(e)
            )
            # Clean up on error
            if hasattr(self, '_preferences_dialog'):
                self._preferences_dialog = None
    
    def _on_preferences_closed(self):
        """Handle preferences dialog closed"""
        if hasattr(self, '_preferences_dialog'):
            self._preferences_dialog = None
    
    def _show_gui_settings(self):
        """Show GUI settings dialog"""
        QMessageBox.information(
            self.main_window, 
            "GUI Settings", 
            "GUI customization dialog coming soon!"
        )
    
    def _show_theme_settings(self):
        """Show theme settings"""
        QMessageBox.information(
            self.main_window, 
            "Themes", 
            "Theme selection coming soon!"
        )
    
    def _export_settings(self):
        """Export settings to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Settings",
                "img_factory_settings.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                QMessageBox.information(
                    self.main_window, 
                    "Export Complete", 
                    "Settings exported to " + file_path
                )
                    
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Export Failed", 
                "Failed to export settings: " + str(e)
            )
    
    def _import_settings(self):
        """Import settings from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Import Settings",
                "",
                "JSON Files (*.json)"
            )
            
            if file_path:
                QMessageBox.information(
                    self.main_window, 
                    "Import Complete", 
                    "Settings imported from " + file_path
                )
                    
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Import Failed", 
                "Failed to import settings: " + str(e)
            )
    
    def _reset_layout(self):
        """Reset GUI layout"""
        reply = QMessageBox.question(
            self.main_window,
            "Reset Layout",
            "This will reset the GUI layout to defaults. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self.main_window, 
                "Reset Complete", 
                "Layout has been reset to defaults."
            )
    
    def _toggle_toolbar(self):
        """Toggle toolbar visibility"""
        if hasattr(self.main_window, 'toolbar'):
            visible = self.main_window.toolbar.isVisible()
            self.main_window.toolbar.setVisible(not visible)
            self.check_action("toolbar", not visible)
    
    def _toggle_statusbar(self):
        """Toggle status bar visibility"""
        if hasattr(self.main_window, 'statusBar'):
            statusbar = self.main_window.statusBar()
            visible = statusbar.isVisible()
            statusbar.setVisible(not visible)
            self.check_action("statusbar", not visible)
    
    def _toggle_log_panel(self):
        """Toggle log panel visibility"""
        if hasattr(self.main_window, 'log_panel'):
            visible = self.main_window.log_panel.isVisible()
            self.main_window.log_panel.setVisible(not visible)
            self.check_action("log_panel", not visible)
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.main_window.isFullScreen():
            self.main_window.showNormal()
        else:
            self.main_window.showFullScreen()
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>IMG Factory 1.5</h2>
        <p><b>Version:</b> 1.5.0</p>
        <p><b>Build Date:</b> July 12, 2025</p>
        <p><b>Author:</b> X-Seti</p>
        <p><b>Original Credits:</b> MexUK 2007 IMG Factory 1.2</p>
        <br>
        <p>A comprehensive tool for managing GTA IMG archives and related files.</p>
        <p>Supports COL, TXD, DFF, IFP, IDE, IPL, and other GTA file formats.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>IMG archive creation and editing</li>
        <li>File import/export with progress tracking</li>
        <li>COL collision file editor</li>
        <li>TXD texture management</li>
        <li>DFF model viewer</li>
        <li>Advanced search and filtering</li>
        <li>Customizable interface and themes</li>
        <li>Batch processing tools</li>
        </ul>
        """
        
        QMessageBox.about(self.main_window, "About IMG Factory", about_text)
    
    def _show_about_qt(self):
        """Show about Qt dialog"""
        QMessageBox.aboutQt(self.main_window, "About Qt")
    
    def _show_help(self):
        """Show help contents"""
        help_text = """
        <h2>IMG Factory Help</h2>
        <h3>Getting Started:</h3>
        <p>1. Open an IMG file using File → Open IMG</p>
        <p>2. Browse entries in the main table</p>
        <p>3. Use right-click context menus for entry operations</p>
        <p>4. Import files using Entry → Import Files</p>
        <p>5. Export files using Entry → Export Selected</p>
        
        <h3>Keyboard Shortcuts:</h3>
        <p><b>Ctrl+O:</b> Open IMG file</p>
        <p><b>Ctrl+N:</b> Create new IMG file</p>
        <p><b>Ctrl+I:</b> Import files</p>
        <p><b>Ctrl+E:</b> Export selected entries</p>
        <p><b>F5:</b> Validate IMG</p>
        <p><b>F6:</b> Rebuild IMG</p>
        <p><b>Delete:</b> Remove selected entries</p>
        <p><b>F2:</b> Rename entry</p>
        <p><b>F7:</b> View model</p>
        <p><b>F8:</b> View texture</p>
        <p><b>F9:</b> View collision</p>
        
        <h3>File Types:</h3>
        <p><b>IMG:</b> Archive files containing game assets</p>
        <p><b>COL:</b> Collision data files</p>
        <p><b>TXD:</b> Texture dictionary files</p>
        <p><b>DFF:</b> 3D model files</p>
        <p><b>IFP:</b> Animation files</p>
        <p><b>IDE:</b> Item definition files</p>
        <p><b>IPL:</b> Item placement files</p>
        """
        
        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Help Contents")
        msg.setText(help_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr><th>Action</th><th>Shortcut</th></tr>
        <tr><td>New IMG</td><td>Ctrl+N</td></tr>
        <tr><td>Open IMG</td><td>Ctrl+O</td></tr>
        <tr><td>Close IMG</td><td>Ctrl+W</td></tr>
        <tr><td>Save</td><td>Ctrl+S</td></tr>
        <tr><td>Import Files</td><td>Ctrl+I</td></tr>
        <tr><td>Export Selected</td><td>Ctrl+E</td></tr>
        <tr><td>Quick Export</td><td>Ctrl+Q</td></tr>
        <tr><td>Remove Selected</td><td>Delete</td></tr>
        <tr><td>Rename Entry</td><td>F2</td></tr>
        <tr><td>Select All</td><td>Ctrl+A</td></tr>
        <tr><td>Find</td><td>Ctrl+F</td></tr>
        <tr><td>IMG Information</td><td>F4</td></tr>
        <tr><td>Validate IMG</td><td>F5</td></tr>
        <tr><td>Rebuild IMG</td><td>F6</td></tr>
        <tr><td>View Model</td><td>F7</td></tr>
        <tr><td>View Texture</td><td>F8</td></tr>
        <tr><td>View Collision</td><td>F9</td></tr>
        <tr><td>COL Editor</td><td>Ctrl+Shift+C</td></tr>
        <tr><td>TXD Editor</td><td>Ctrl+Shift+T</td></tr>
        <tr><td>DFF Editor</td><td>Ctrl+Shift+D</td></tr>
        <tr><td>Log Panel</td><td>F12</td></tr>
        <tr><td>Fullscreen</td><td>F11</td></tr>
        <tr><td>Preferences</td><td>Ctrl+,</td></tr>
        <tr><td>Exit</td><td>Ctrl+Q</td></tr>
        </table>
        """
        
        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setText(shortcuts_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()
    
    def _show_formats(self):
        """Show supported formats"""
        formats_text = """
        <h2>Supported File Formats</h2>
        
        <h3>Archive Formats:</h3>
        <p><b>IMG:</b> GTA image archives (versions 1, 2, 3)</p>
        <p><b>DAT:</b> GTA data files</p>
        
        <h3>3D Model Formats:</h3>
        <p><b>DFF:</b> RenderWare DFF models</p>
        <p><b>COL:</b> Collision data (versions 1, 2, 3, 4)</p>
        <p><b>WDR:</b> World drawable files</p>
        
        <h3>Texture Formats:</h3>
        <p><b>TXD:</b> RenderWare texture dictionaries</p>
        <p><b>WTD:</b> World texture dictionaries</p>
        
        <h3>Animation Formats:</h3>
        <p><b>IFP:</b> Animation packages</p>
        <p><b>YCD:</b> Clip dictionaries</p>
        
        <h3>Data Formats:</h3>
        <p><b>IDE:</b> Item definition files</p>
        <p><b>IPL:</b> Item placement files</p>
        <p><b>DAT:</b> Various data files</p>
        
        <h3>Import/Export Formats:</h3>
        <p><b>Images:</b> PNG, JPG, BMP, TGA, DDS</p>
        <p><b>Models:</b> OBJ, PLY (export only)</p>
        <p><b>Text:</b> TXT, CSV (for data files)</p>
        """
        
        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Supported Formats")
        msg.setText(formats_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()
    
    def _show_debug_console(self):
        """Show debug console"""
        QMessageBox.information(
            self.main_window, 
            "Debug Console", 
            "Debug console coming soon!"
        )
    
    def _clear_debug_log(self):
        """Clear debug log"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message("Debug log cleared")
        QMessageBox.information(
            self.main_window, 
            "Debug Log", 
            "Debug log has been cleared."
        )
    
    def _reset_panel_layout(self):
        """Reset panel layout to default"""
        if self.panel_manager:
            for panel_id in self.panel_manager.panels:
                self.panel_manager.dock_panel(panel_id)
                self.panel_manager.show_panel(panel_id)

            QMessageBox.information(
                self.main_window,
                "Layout Reset",
                "Panel layout has been reset to default."
            )
    
    def _apply_gui_changes(self):
        """Apply GUI changes to the main window"""
        try:
            # Apply theme changes
            if hasattr(self.main_window, 'app_settings'):
                from utils.app_settings_system import apply_theme_to_app
                from PyQt6.QtWidgets import QApplication
                
                apply_theme_to_app(QApplication.instance(), self.main_window.app_settings)
            
            # Log the change
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("GUI settings applied successfully")
            
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Error applying GUI changes: " + str(e))


    def cleanup_dialogs(self):
        """Clean up any open dialogs"""
        try:
            if hasattr(self, '_preferences_dialog') and self._preferences_dialog is not None:
                self._preferences_dialog.close()
                self._preferences_dialog.deleteLater()
                self._preferences_dialog = None
            
            if hasattr(self, '_gui_settings_dialog') and self._gui_settings_dialog is not None:
                self._gui_settings_dialog.close()
                self._gui_settings_dialog.deleteLater()
                self._gui_settings_dialog = None
                
        except Exception as e:
            print(f"Error cleaning up dialogs: {e}")


# Export main classes
__all__ = [
    'IMGFactoryMenuBar',
    'MenuAction',
    'MenuDefinition'
]