#!/usr/bin/env python3
"""
#this belongs in gui/ menu_system.py - version 15
X-Seti - June28 2025 - IMG Factory 1.5
Unified Menu System - Single source for all menu functionality
Combines function-based and class-based approaches for maximum flexibility
"""

from typing import Dict, List, Optional, Callable, Any
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QButtonGroup, QDialog, QVBoxLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QGroupBox, QLabel, QLineEdit, QComboBox, QMessageBox, QTabWidget,
    QWidget, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QActionGroup


class MenuAction:
    """Represents a menu action with all properties"""

    def __init__(self, action_id: str, text: str, shortcut: str = "",
                 icon: str = "", callback: Callable = None, checkable: bool = False,
                 status_tip: str = "", separator_after: bool = False):  # Add this parameter
        self.action_id = action_id
        self.text = text
        self.shortcut = shortcut
        self.icon = icon
        self.callback = callback
        self.checkable = checkable
        self.enabled = True
        self.visible = True
        self.separator_after = separator_after  # Add this line
        self.status_tip = status_tip


class MenuDefinition:
    """Complete IMG Factory menu structure definition"""
    
    def __init__(self):
        self.menus = self._create_standard_menus()
    
    def _create_standard_menus(self) -> Dict[str, List[MenuAction]]:
        """Create the standard IMG Factory menu structure"""
        return {
            "File": [
                MenuAction("new_img", "&New IMG Archive...", "Ctrl+N", "document-new", 
                          status_tip="Create a new IMG archive"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("open_img", "&Open IMG Archive...", "Ctrl+O", "document-open",
                          status_tip="Open an existing IMG archive"),
                MenuAction("open_recent", "Open &Recent", submenu=True),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("close_img", "&Close IMG", "Ctrl+W", "window-close",
                          status_tip="Close the current IMG archive"),
                MenuAction("close_all", "Close &All", "Ctrl+Shift+W",
                          status_tip="Close all open IMG archives"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("save", "&Save", "Ctrl+S", "document-save",
                          status_tip="Save changes to the current IMG"),
                MenuAction("save_as", "Save &As...", "Ctrl+Shift+S", "document-save-as",
                          status_tip="Save IMG with a new name"),
                MenuAction("separator4", "", separator_after=True),
                MenuAction("exit", "E&xit", "Ctrl+Q", "application-exit",
                          status_tip="Exit IMG Factory")
            ],
            
            "Edit": [
                MenuAction("undo", "&Undo", "Ctrl+Z", "edit-undo",
                          status_tip="Undo the last action"),
                MenuAction("redo", "&Redo", "Ctrl+Y", "edit-redo",
                          status_tip="Redo the last undone action"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("cut", "Cu&t", "Ctrl+X", "edit-cut",
                          status_tip="Cut selected entries"),
                MenuAction("copy", "&Copy", "Ctrl+C", "edit-copy",
                          status_tip="Copy selected entries"),
                MenuAction("paste", "&Paste", "Ctrl+V", "edit-paste",
                          status_tip="Paste entries from clipboard"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("select_all", "Select &All", "Ctrl+A", "edit-select-all",
                          status_tip="Select all entries"),
                MenuAction("select_none", "Select &None", "Ctrl+D",
                          status_tip="Deselect all entries"),
                MenuAction("invert_selection", "&Invert Selection", "Ctrl+I",
                          status_tip="Invert current selection")
            ],
            
            "IMG": [
                MenuAction("rebuild", "&Rebuild", "F5", "view-refresh",
                          status_tip="Rebuild the current IMG archive"),
                MenuAction("rebuild_as", "Rebuild &As...", "Shift+F5", "document-save-as",
                          status_tip="Rebuild IMG archive with new name"),
                MenuAction("rebuild_all", "Rebuild A&ll", "Ctrl+F5",
                          status_tip="Rebuild all IMG files in directory"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("merge", "&Merge IMG...", "", "document-merge",
                          status_tip="Merge another IMG into current"),
                MenuAction("split", "&Split IMG...", "", "document-split",
                          status_tip="Split IMG into multiple files"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("convert", "&Convert Format...", "", "document-convert",
                          status_tip="Convert IMG to different version"),
                MenuAction("compress", "Com&press", "", "archive-compress",
                          status_tip="Compress IMG archive"),
                MenuAction("decompress", "&Decompress", "", "archive-extract",
                          status_tip="Decompress IMG archive"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("info", "IMG &Information", "Alt+Enter", "document-properties",
                          status_tip="Show IMG file information"),
                MenuAction("validate", "&Validate", "F9", "tools-check-spelling",
                          status_tip="Validate IMG archive integrity")
            ],
            
            "Entry": [
                MenuAction("import_files", "&Import Files...", "Ctrl+I", "document-import",
                          status_tip="Import files into IMG archive"),
                MenuAction("import_folder", "Import &Folder...", "Ctrl+Shift+I", "folder-import",
                          status_tip="Import entire folder into IMG"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("export_selected", "&Export Selected...", "Ctrl+E", "document-export",
                          status_tip="Export selected entries"),
                MenuAction("export_all", "Export &All...", "Ctrl+Shift+E", "document-export-all",
                          status_tip="Export all entries"),
                MenuAction("quick_export", "&Quick Export", "Ctrl+Q", "document-quick-export",
                          status_tip="Quick export to last used folder"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("remove", "&Remove", "Delete", "edit-delete",
                          status_tip="Remove selected entries"),
                MenuAction("remove_all", "Remove A&ll", "Ctrl+Delete",
                          status_tip="Remove all entries"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("rename", "Re&name...", "F2", "edit-rename",
                          status_tip="Rename selected entry"),
                MenuAction("replace", "Re&place...", "Ctrl+H", "edit-replace",
                          status_tip="Replace selected entry with new file"),
                MenuAction("duplicate", "&Duplicate", "Ctrl+D", "edit-duplicate",
                          status_tip="Duplicate selected entry"),
                MenuAction("separator4", "", separator_after=True),
                MenuAction("properties", "&Properties", "Alt+Enter", "document-properties",
                          status_tip="Show entry properties")
            ],
            
            "Tools": [
                MenuAction("validate_img", "&Validate Archive", "F9", "tools-check-spelling",
                          status_tip="Validate IMG archive for errors"),
                MenuAction("repair", "&Repair Archive", "", "tools-repair",
                          status_tip="Attempt to repair corrupted IMG"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("template_manager", "&Template Manager...", "", "folder-templates",
                          status_tip="Manage IMG creation templates"),
                MenuAction("batch_processor", "&Batch Processor...", "", "application-batch",
                          status_tip="Process multiple IMG files"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("img_converter", "IMG &Converter...", "", "document-convert",
                          status_tip="Convert between IMG versions"),
                MenuAction("txd_converter", "&TXD Converter...", "", "image-convert",
                          status_tip="Convert TXD texture files"),
                MenuAction("col_editor", "&COL Editor...", "", "shape-editor",
                          status_tip="Edit collision files"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("quick_wizard", "&Quick Start Wizard...", "F1", "tools-wizard",
                          status_tip="Quick start wizard for new users")
            ],
            
            "View": [
                MenuAction("toolbar", "&Toolbar", "", checkable=True,
                          status_tip="Show/hide toolbar"),
                MenuAction("statusbar", "&Status Bar", "", checkable=True,
                          status_tip="Show/hide status bar"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("file_info", "&File Information", "F3", checkable=True,
                          status_tip="Show/hide file information panel"),
                MenuAction("log_panel", "&Activity Log", "F4", checkable=True,
                          status_tip="Show/hide activity log panel"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("refresh", "&Refresh", "F5", "view-refresh",
                          status_tip="Refresh current view"),
                MenuAction("zoom_in", "Zoom &In", "Ctrl+=", "zoom-in",
                          status_tip="Increase interface size"),
                MenuAction("zoom_out", "Zoom &Out", "Ctrl+-", "zoom-out",
                          status_tip="Decrease interface size"),
                MenuAction("zoom_reset", "&Reset Zoom", "Ctrl+0", "zoom-original",
                          status_tip="Reset interface to normal size"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("fullscreen", "&Full Screen", "F11", "view-fullscreen",
                          status_tip="Toggle full screen mode")
            ],
            
            "Settings": [
                MenuAction("preferences", "&Preferences...", "Ctrl+,", "configure",
                          status_tip="Open application preferences"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("customize_interface", "&Customize Interface...", "", "configure-desktop",
                          status_tip="Customize interface layout"),
                MenuAction("customize_toolbar", "Customize &Toolbar...", "", "configure-toolbars",
                          status_tip="Customize toolbar buttons"),
                MenuAction("customize_menus", "Customize &Menus...", "", "configure-shortcuts",
                          status_tip="Customize menu layout and shortcuts"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("themes", "&Themes...", "", "preferences-desktop-theme",
                          status_tip="Change application theme"),
                MenuAction("language", "&Language...", "", "preferences-desktop-locale",
                          status_tip="Change interface language"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("reset_layout", "&Reset Layout", "", "configure-reset",
                          status_tip="Reset interface to default layout"),
                MenuAction("export_settings", "&Export Settings...", "", "document-export",
                          status_tip="Export current settings"),
                MenuAction("import_settings", "&Import Settings...", "", "document-import",
                          status_tip="Import settings from file")
            ],
            
            "Help": [
                MenuAction("help_contents", "&Help Contents", "F1", "help-contents",
                          status_tip="Open help documentation"),
                MenuAction("quick_start", "&Quick Start Guide", "", "help-guide",
                          status_tip="Open quick start guide"),
                MenuAction("keyboard_shortcuts", "&Keyboard Shortcuts", "", "help-keyboard",
                          status_tip="Show keyboard shortcuts"),
                MenuAction("supported_formats", "&Supported Formats", "", "help-formats",
                          status_tip="Show supported file formats"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("check_updates", "Check for &Updates...", "", "system-software-update",
                          status_tip="Check for application updates"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("website", "Visit &Website", "", "internet-web-browser",
                          status_tip="Visit the IMG Factory website"),
                MenuAction("report_bug", "&Report Bug...", "", "tools-report-bug",
                          status_tip="Report a bug or issue"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("about", "&About IMG Factory", "", "help-about",
                          status_tip="About IMG Factory")
            ]
        }


class IMGFactoryMenuSystem:
    """Unified menu system for IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()
        self.menu_definition = MenuDefinition()
        self.actions: Dict[str, QAction] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.context_menus: Dict[str, QMenu] = {}
        
        # Settings
        self.show_icons = True
        self.show_tooltips = True
        
        # Load settings
        self._load_settings()
        
        # Create menus
        self._create_all_menus()
        self._create_context_menus()
    
    def _load_settings(self):
        """Load menu display settings"""
        if hasattr(self.main_window, 'app_settings') and self.main_window.app_settings:
            settings = self.main_window.app_settings.current_settings
            self.show_icons = settings.get("show_menu_icons", True)
            self.show_tooltips = settings.get("show_menu_tooltips", True)
    
    def _create_all_menus(self):
        """Create all menus from definition"""
        for menu_name, menu_actions in self.menu_definition.menus.items():
            menu = self.menu_bar.addMenu(f"&{menu_name}")
            self._populate_menu(menu, menu_actions)
    
    def _populate_menu(self, menu: QMenu, menu_actions: List[MenuAction]):
        """Populate a menu with actions"""
        for menu_action in menu_actions:
            if menu_action.action_id.startswith("separator"):
                if menu_action.separator_after:
                    menu.addSeparator()
                continue
            
            if not menu_action.visible:
                continue
            
            # Create QAction
            action = QAction(menu_action.text, self.main_window)
            
            # Set properties
            if menu_action.shortcut:
                if menu_action.shortcut.startswith("Ctrl+") or menu_action.shortcut.startswith("F"):
                    action.setShortcut(QKeySequence(menu_action.shortcut))
                else:
                    action.setShortcut(menu_action.shortcut)
            
            if menu_action.icon and self.show_icons:
                action.setIcon(QIcon.fromTheme(menu_action.icon))
            
            if menu_action.status_tip and self.show_tooltips:
                action.setStatusTip(menu_action.status_tip)
                action.setToolTip(menu_action.status_tip)
            
            action.setCheckable(menu_action.checkable)
            action.setEnabled(menu_action.enabled)
            
            # Store action reference
            self.actions[menu_action.action_id] = action
            
            # Connect callback if available
            if menu_action.callback:
                action.triggered.connect(menu_action.callback)
            elif menu_action.action_id in self.callbacks:
                action.triggered.connect(self.callbacks[menu_action.action_id])
            else:
                # Connect to main window method if it exists
                method_name = menu_action.action_id
                if hasattr(self.main_window, method_name):
                    action.triggered.connect(getattr(self.main_window, method_name))
                else:
                    # Default handler
                    action.triggered.connect(lambda checked, aid=menu_action.action_id: self._default_action_handler(aid))
            
            # Add to menu
            menu.addAction(action)
            
            # Add separator after if specified
            if menu_action.separator_after:
                menu.addSeparator()
    
    def _create_context_menus(self):
        """Create context menus for different UI elements"""
        # Table context menu
        table_menu = QMenu(self.main_window)
        table_actions = [
            MenuAction("view_entry", "View Entry", "Enter", "document-view"),
            MenuAction("separator1", "", separator_after=True),
            MenuAction("export_entry", "Export Entry", "Ctrl+E", "document-export"),
            MenuAction("replace_entry", "Replace Entry", "Ctrl+H", "edit-replace"),
            MenuAction("separator2", "", separator_after=True),
            MenuAction("remove_entry", "Remove Entry", "Delete", "edit-delete"),
            MenuAction("rename_entry", "Rename Entry", "F2", "edit-rename"),
            MenuAction("separator3", "", separator_after=True),
            MenuAction("entry_properties", "Properties", "Alt+Enter", "document-properties")
        ]
        self._populate_menu(table_menu, table_actions)
        self.context_menus["table"] = table_menu
        
        # Panel context menu
        panel_menu = QMenu(self.main_window)
        panel_actions = [
            MenuAction("dock_panel", "Dock Panel", "", "dock-panel"),
            MenuAction("float_panel", "Float Panel", "", "float-panel"),
            MenuAction("separator1", "", separator_after=True),
            MenuAction("hide_panel", "Hide Panel", "", "hide-panel"),
            MenuAction("separator2", "", separator_after=True),
            MenuAction("customize_panel", "Customize Panel", "", "configure-panel")
        ]
        self._populate_menu(panel_menu, panel_actions)
        self.context_menus["panel"] = panel_menu
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set callbacks for menu actions"""
        self.callbacks.update(callbacks)
        
        # Update existing actions
        for action_id, callback in callbacks.items():
            if action_id in self.actions:
                action = self.actions[action_id]
                # Disconnect any existing connections
                action.triggered.disconnect()
                # Connect new callback
                action.triggered.connect(callback)
    
    def get_action(self, action_id: str) -> Optional[QAction]:
        """Get action by ID"""
        return self.actions.get(action_id)
    
    def enable_action(self, action_id: str, enabled: bool = True):
        """Enable/disable action"""
        if action_id in self.actions:
            self.actions[action_id].setEnabled(enabled)
    
    def set_action_checked(self, action_id: str, checked: bool):
        """Set action checked state"""
        if action_id in self.actions:
            action = self.actions[action_id]
            if action.isCheckable():
                action.setChecked(checked)
    
    def show_context_menu(self, menu_type: str, position: QPoint):
        """Show context menu at position"""
        if menu_type in self.context_menus:
            self.context_menus[menu_type].exec(position)
    
    def get_context_menu(self, menu_type: str) -> Optional[QMenu]:
        """Get context menu by type"""
        return self.context_menus.get(menu_type)
    
    def _default_action_handler(self, action_id: str):
        """Default handler for unconnected actions"""
        print(f"Menu action triggered: {action_id}")
        # Log to main window if available
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Menu action: {action_id}")


# Convenience function for creating menu system
def create_menu_system(main_window):
    """Create unified menu system (simplified)"""
    # Just use the existing working create_menu_bar function
    # But call it directly without recursion
    menubar = main_window.menuBar()

    # Get settings for icon display
    show_icons = True
    if hasattr(main_window, 'app_settings') and main_window.app_settings:
        show_icons = main_window.app_settings.current_settings.get("show_menu_icons", True)

    # Create basic menus manually for now
    file_menu = menubar.addMenu("&File")
    edit_menu = menubar.addMenu("&Edit")
    img_menu = menubar.addMenu("&IMG")
    entry_menu = menubar.addMenu("&Entry")
    tools_menu = menubar.addMenu("&Tools")
    view_menu = menubar.addMenu("&View")
    settings_menu = menubar.addMenu("&Settings")
    help_menu = menubar.addMenu("&Help")

    return menubar


# Legacy compatibility function
def create_menu_bar(main_window):
    """Legacy function for backward compatibility"""
    return create_menu_system(main_window)


# Export main classes
__all__ = [
    'MenuAction',
    'MenuDefinition',
    'IMGFactoryMenuSystem',
    'create_menu_system',
    'create_menu_bar',  # Legacy compatibility
    'register_global_shortcuts'  # Add this to exports
]

def register_global_shortcuts(main_window):
    """Register global keyboard shortcuts"""
    from PyQt6.QtGui import QShortcut, QKeySequence  # Move import inside function

    shortcuts = [
        ("Ctrl+F", "show_search_dialog"),
        ("Ctrl+G", "toggle_grid_display"),
        ("F1", "show_help"),
        ("F11", "toggle_fullscreen"),
        ("Escape", "cancel_operation"),
    ]

    for shortcut, method_name in shortcuts:
        if hasattr(main_window, method_name):
            action = QAction(main_window)
            action.setShortcut(shortcut)
            action.triggered.connect(getattr(main_window, method_name))
            main_window.addAction(action)

