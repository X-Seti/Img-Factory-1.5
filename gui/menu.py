#this belongs in gui/ menu.py - version 15
#!/usr/bin/env python3
"""
X-Seti - June25 2025 - IMG Factory 1.5
Modular menu system with customizable layouts
"""

from typing import Dict, List, Optional, Callable, Any
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QDialog, QVBoxLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QGroupBox, QLabel, QLineEdit, QComboBox, QMessageBox, QTabWidget,
    QWidget, QSplitter, QTextEdit, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QActionGroup
from gui.panels import PanelManager
from gui.gui_settings import GUISettingsDialog


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

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "action_id": self.action_id,
            "text": self.text,
            "shortcut": self.shortcut,
            "icon": self.icon,
            "checkable": self.checkable,
            "enabled": self.enabled,
            "visible": self.visible,
            "separator_after": self.separator_after
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MenuAction':
        """Create from dictionary"""
        action = cls(
            data["action_id"],
            data["text"],
            data.get("shortcut", ""),
            data.get("icon", "")
        )
        action.checkable = data.get("checkable", False)
        action.enabled = data.get("enabled", True)
        action.visible = data.get("visible", True)
        action.separator_after = data.get("separator_after", False)
        return action

class MenuDefinition:
    """Defines a complete menu structure"""

    def __init__(self):
        # Standard IMG Factory menu structure
        self.menus = {
            "File": [
                MenuAction("new_img", "New IMG", "Ctrl+N", "document-new"),
                MenuAction("open_img", "Open IMG", "Ctrl+O", "document-open"),
                MenuAction("open_multiple", "Open Multiple Files", "Ctrl+Shift+O", "folder-open"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("close_img", "Close", "Ctrl+W", "window-close"),
                MenuAction("close_all", "Close All", "Ctrl+Shift+W"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("recent_files", "Recent Files"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("exit", "Exit", "Ctrl+Q", "application-exit"),
            ],

            "Edit": [
                MenuAction("undo", "Undo", "Ctrl+Z", "edit-undo"),
                MenuAction("redo", "Redo", "Ctrl+Y", "edit-redo"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("cut", "Cut", "Ctrl+X", "edit-cut"),
                MenuAction("copy", "Copy", "Ctrl+C", "edit-copy"),
                MenuAction("paste", "Paste", "Ctrl+V", "edit-paste"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("select_all", "Select All", "Ctrl+A", "edit-select-all"),
                MenuAction("select_inverse", "Select Inverse", "Ctrl+I"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("find", "Find", "Ctrl+F", "edit-find"),
                MenuAction("find_next", "Find Next", "F3"),
            ],

            "Dat": [
                MenuAction("dat_info", "DAT File Information"),
                MenuAction("dat_validate", "Validate DAT"),
                MenuAction("dat_rebuild", "Rebuild DAT"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("dat_extract", "Extract All"),
                MenuAction("dat_create", "Create New DAT"),
            ],

            "IMG": [
                MenuAction("img_info", "IMG Information", "F4"),
                MenuAction("img_validate", "Validate IMG", "F5"),
                MenuAction("img_rebuild", "Rebuild IMG", "F6"),
                MenuAction("img_rebuild_as", "Rebuild As...", "Shift+F6"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("img_merge", "Merge IMG Files"),
                MenuAction("img_split", "Split IMG File"),
                MenuAction("img_convert", "Convert Format"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("img_optimize", "Optimize IMG"),
                MenuAction("img_defrag", "Defragment IMG"),
            ],

            "Model": [
                MenuAction("model_view", "View Model", "F7"),
                MenuAction("model_export", "Export Model"),
                MenuAction("model_import", "Import Model"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("model_convert", "Convert Format"),
                MenuAction("model_validate", "Validate DFF"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("model_batch_export", "Batch Export"),
                MenuAction("model_batch_convert", "Batch Convert"),
            ],

            "Texture": [
                MenuAction("texture_view", "View Texture", "F8"),
                MenuAction("texture_export", "Export Texture"),
                MenuAction("texture_import", "Import Texture"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("texture_convert", "Convert Format"),
                MenuAction("texture_validate", "Validate TXD"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("texture_batch_export", "Batch Export"),
                MenuAction("texture_batch_convert", "Batch Convert"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("texture_palette", "Extract Palette"),
            ],

            "Collision": [
                MenuAction("collision_view", "View Collision", "F9"),
                MenuAction("collision_export", "Export Collision"),
                MenuAction("collision_import", "Import Collision"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("collision_validate", "Validate COL"),
                MenuAction("collision_optimize", "Optimize Collision"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("collision_batch_export", "Batch Export"),
            ],

            "Item Definition": [
                MenuAction("ide_view", "View IDE"),
                MenuAction("ide_edit", "Edit IDE"),
                MenuAction("ide_validate", "Validate IDE"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("ide_export", "Export to Text"),
                MenuAction("ide_import", "Import from Text"),
            ],

            "Item Placement": [
                MenuAction("ipl_view", "View IPL"),
                MenuAction("ipl_edit", "Edit IPL"),
                MenuAction("ipl_validate", "Validate IPL"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("ipl_export", "Export to Text"),
                MenuAction("ipl_import", "Import from Text"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("ipl_map_view", "View on Map"),
            ],

            "Entry": [
                MenuAction("entry_info", "Entry Information", "Alt+Enter"),
                MenuAction("entry_properties", "Properties", "Alt+P"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("entry_import", "Import Files", "Ctrl+I"),
                MenuAction("entry_export", "Export Selected", "Ctrl+E"),
                MenuAction("entry_export_all", "Export All", "Ctrl+Shift+E"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("entry_remove", "Remove Selected", "Delete"),
                MenuAction("entry_rename", "Rename", "F2"),
                MenuAction("entry_replace", "Replace", "Ctrl+R"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("entry_duplicate", "Duplicate"),
                MenuAction("entry_batch_ops", "Batch Operations"),
            ],

            "Settings": [
                MenuAction("preferences", "Preferences", "Ctrl+,"),
                MenuAction("customize_interface", "Customize Interface"),
                MenuAction("customize_buttons", "Customize Buttons"),
                MenuAction("customize_panels", "Customize Panels"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("themes", "Themes"),
                MenuAction("language", "Language"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("reset_layout", "Reset Layout"),
                MenuAction("export_settings", "Export Settings"),
                MenuAction("import_settings", "Import Settings"),
            ],

            "Help": [
                MenuAction("help_contents", "Help Contents", "F1"),
                MenuAction("help_shortcuts", "Keyboard Shortcuts"),
                MenuAction("help_formats", "Supported Formats"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("help_website", "Visit Website"),
                MenuAction("help_report_bug", "Report Bug"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("about", "About IMG Factory"),
            ]
        }

class IMGFactoryMenuBar:
    """Main menu bar for IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
       # self.panel_manager = panel_manager
        self.menu_bar = main_window.menuBar()
        self.callbacks: Dict[str, Callable] = {}
        self.actions: Dict[str, QAction] = {}
        
        self.menu_definition = MenuDefinition()
        self._create_menus()
        
        # Set up default callbacks for GUI settings
        self._setup_default_callbacks()
    
    def _setup_default_callbacks(self):
        """Set up default menu callbacks"""
        default_callbacks = {
            # Settings menu callbacks
            "preferences": self._show_preferences,
            "customize_interface": self._show_gui_settings,
            "customize_buttons": self._show_button_customization,
            "customize_panels": self._show_panel_customization,
            "themes": self._show_theme_settings,
            "language": self._show_language_settings,
            "reset_layout": self._reset_layout,
            "export_settings": self._export_settings,
            "import_settings": self._import_settings,
        }
        
        self.set_callbacks(default_callbacks)
    
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

    def add_panel_menu(self):
        """Add panels menu for tear-off functionality"""
        if not self.panel_manager:
            return

        panels_menu = self.menu_bar.addMenu("Panels")

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

        # Tear off/Dock panels
        tearoff_menu = panels_menu.addMenu("Tear Off")
        dock_menu = panels_menu.addMenu("Dock")

        for panel_id, panel in self.panel_manager.panels.items():
            # Tear off action
            tearoff_action = QAction(f"Tear Off {panel.title}", self.main_window)
            tearoff_action.setEnabled(not panel.is_torn_off)
            tearoff_action.triggered.connect(
                lambda checked, pid=panel_id: self.panel_manager.tear_off_panel(pid)
            )
            tearoff_menu.addAction(tearoff_action)

            # Dock action
            dock_action = QAction(f"Dock {panel.title}", self.main_window)
            dock_action.setEnabled(panel.is_torn_off)
            dock_action.triggered.connect(
                lambda checked, pid=panel_id: self.panel_manager.dock_panel(pid)
            )
            dock_menu.addAction(dock_action)

        panels_menu.addSeparator()

        # Reset layout
        reset_action = QAction("Reset Layout", self.main_window)
        reset_action.triggered.connect(self._reset_panel_layout)
        panels_menu.addAction(reset_action)

        # Save layout
        save_action = QAction("Save Layout", self.main_window)
        save_action.triggered.connect(self._save_panel_layout)
        panels_menu.addAction(save_action)

    def _reset_panel_layout(self):
        """Reset panel layout to default"""
        if self.panel_manager:
            # Dock all panels
            for panel_id in self.panel_manager.panels:
                self.panel_manager.dock_panel(panel_id)

            # Show all panels
            for panel_id in self.panel_manager.panels:
                self.panel_manager.show_panel(panel_id)

            QMessageBox.information(
                self.main_window,
                "Layout Reset",
                "Panel layout has been reset to default."
            )

    def _save_panel_layout(self):
        """Save current panel layout"""
        if self.panel_manager:
            self.panel_manager._save_panel_settings()
            QMessageBox.information(
                self.main_window,
                "Layout Saved",
                "Current panel layout has been saved."
            )


class MenuCustomizationDialog(QDialog):
    """Dialog for customizing menu layout"""

    def __init__(self, menu_bar: IMGFactoryMenuBar, parent=None):
        super().__init__(parent)
        self.menu_bar = menu_bar
        self.setWindowTitle("Customize Menus")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        self._create_ui()
        self._load_current_settings()

    def _create_ui(self):
        """Create customization UI"""
        layout = QVBoxLayout(self)

        # Create tabs
        tab_widget = QTabWidget()

        # Menu Items tab
        items_tab = self._create_items_tab()
        tab_widget.addTab(items_tab, "Menu Items")

        # Shortcuts tab
        shortcuts_tab = self._create_shortcuts_tab()
        tab_widget.addTab(shortcuts_tab, "Keyboard Shortcuts")

        # Toolbar tab
        toolbar_tab = self._create_toolbar_tab()
        tab_widget.addTab(toolbar_tab, "Toolbar")

        layout.addWidget(tab_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

    def _create_items_tab(self) -> QWidget:
        """Create menu items customization tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left side - menu tree
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Menu Structure:"))

        self.menu_tree = QListWidget()
        self._populate_menu_tree()
        left_layout.addWidget(self.menu_tree)

        layout.addLayout(left_layout)

        # Right side - item properties
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Item Properties:"))

        # Properties form
        props_group = QGroupBox("Properties")
        props_layout = QVBoxLayout(props_group)

        # Text
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self.item_text_edit = QLineEdit()
        text_layout.addWidget(self.item_text_edit)
        props_layout.addLayout(text_layout)

        # Shortcut
        shortcut_layout = QHBoxLayout()
        shortcut_layout.addWidget(QLabel("Shortcut:"))
        self.item_shortcut_edit = QLineEdit()
        shortcut_layout.addWidget(self.item_shortcut_edit)
        props_layout.addLayout(shortcut_layout)

        # Checkboxes
        self.item_visible_check = QCheckBox("Visible")
        props_layout.addWidget(self.item_visible_check)

        self.item_enabled_check = QCheckBox("Enabled")
        props_layout.addWidget(self.item_enabled_check)

        self.item_separator_check = QCheckBox("Add separator after")
        props_layout.addWidget(self.item_separator_check)

        right_layout.addWidget(props_group)
        right_layout.addStretch()

        layout.addLayout(right_layout)

        return widget

    def _create_shortcuts_tab(self) -> QWidget:
        """Create keyboard shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Keyboard Shortcuts:"))

        # Shortcuts list
        self.shortcuts_list = QListWidget()
        self._populate_shortcuts_list()
        layout.addWidget(self.shortcuts_list)

        # Edit shortcut
        shortcut_edit_layout = QHBoxLayout()
        shortcut_edit_layout.addWidget(QLabel("New Shortcut:"))

        self.new_shortcut_edit = QLineEdit()
        self.new_shortcut_edit.setPlaceholderText("Press keys or type shortcut...")
        shortcut_edit_layout.addWidget(self.new_shortcut_edit)

        self.assign_shortcut_btn = QPushButton("Assign")
        shortcut_edit_layout.addWidget(self.assign_shortcut_btn)

        layout.addLayout(shortcut_edit_layout)

        return widget

    def _create_toolbar_tab(self) -> QWidget:
        """Create toolbar customization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Toolbar Customization:"))

        # Splitter for available vs current toolbar
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Available actions
        available_widget = QWidget()
        available_layout = QVBoxLayout(available_widget)
        available_layout.addWidget(QLabel("Available Actions:"))

        self.available_actions_list = QListWidget()
        available_layout.addWidget(self.available_actions_list)

        splitter.addWidget(available_widget)

        # Current toolbar
        current_widget = QWidget()
        current_layout = QVBoxLayout(current_widget)
        current_layout.addWidget(QLabel("Current Toolbar:"))

        self.current_toolbar_list = QListWidget()
        current_layout.addWidget(self.current_toolbar_list)

        # Toolbar buttons
        toolbar_buttons = QHBoxLayout()

        self.add_to_toolbar_btn = QPushButton("Add →")
        toolbar_buttons.addWidget(self.add_to_toolbar_btn)

        self.remove_from_toolbar_btn = QPushButton("← Remove")
        toolbar_buttons.addWidget(self.remove_from_toolbar_btn)

        self.move_up_btn = QPushButton("↑ Up")
        toolbar_buttons.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("↓ Down")
        toolbar_buttons.addWidget(self.move_down_btn)

        current_layout.addLayout(toolbar_buttons)

        splitter.addWidget(current_widget)
        layout.addWidget(splitter)

        return widget

    def _populate_menu_tree(self):
        """Populate menu tree with current structure"""
        for menu_name, actions in self.menu_bar.menu_definition.menus.items():
            # Add menu header
            menu_item = QListWidgetItem(f"📁 {menu_name}")
            menu_item.setData(Qt.ItemDataRole.UserRole, {"type": "menu", "name": menu_name})
            self.menu_tree.addItem(menu_item)

            # Add actions
            for action in actions:
                if action.action_id.startswith("separator"):
                    continue

                item_text = f"   • {action.text}"
                if action.shortcut:
                    item_text += f" ({action.shortcut})"

                action_item = QListWidgetItem(item_text)
                action_item.setData(Qt.ItemDataRole.UserRole, {
                    "type": "action",
                    "menu": menu_name,
                    "action": action
                })
                self.menu_tree.addItem(action_item)

    def _populate_shortcuts_list(self):
        """Populate shortcuts list"""
        for action_id, action in self.menu_bar.actions.items():
            if action.shortcut().isEmpty():
                continue

            item_text = f"{action.text()} - {action.shortcut().toString()}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, {"action_id": action_id, "action": action})
            self.shortcuts_list.addItem(item)

    def _load_current_settings(self):
        """Load current menu settings"""
        # This would load any saved customizations
        pass

    def _reset_to_defaults(self):
        """Reset menu to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "This will reset all menu customizations to defaults.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.menu_bar.menu_definition = MenuDefinition()
            self._populate_menu_tree()
            self._populate_shortcuts_list()

    def _apply_changes(self):
        """Apply menu changes"""
        # This would save and apply the customizations
        QMessageBox.information(self, "Applied", "Menu customizations have been applied.")


class ContextMenuManager:
    """Manages context menus for different UI elements"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.context_menus: Dict[str, QMenu] = {}
        self._create_context_menus()

    def _create_context_menus(self):
        """Create standard context menus"""
        # Table context menu
        table_menu = QMenu(self.main_window)

        table_menu.addAction("View Entry", lambda: self._placeholder_action("view_entry"))
        table_menu.addAction("Export Entry", lambda: self._placeholder_action("export_entry"))
        table_menu.addSeparator()
        table_menu.addAction("Remove Entry", lambda: self._placeholder_action("remove_entry"))
        table_menu.addAction("Rename Entry", lambda: self._placeholder_action("rename_entry"))
        table_menu.addSeparator()
        table_menu.addAction("Properties", lambda: self._placeholder_action("entry_properties"))

        self.context_menus["table"] = table_menu

        # Panel context menu
        panel_menu = QMenu(self.main_window)

        panel_menu.addAction("Tear Off Panel", lambda: self._placeholder_action("tear_off"))
        panel_menu.addAction("Customize Panel", lambda: self._placeholder_action("customize_panel"))
        panel_menu.addSeparator()
        panel_menu.addAction("Reset Panel", lambda: self._placeholder_action("reset_panel"))
        panel_menu.addAction("Hide Panel", lambda: self._placeholder_action("hide_panel"))

        self.context_menus["panel"] = panel_menu

    def get_context_menu(self, menu_type: str) -> Optional[QMenu]:
        """Get context menu by type"""
        return self.context_menus.get(menu_type)

    def show_context_menu(self, menu_type: str, position: QPoint):
        """Show context menu at position"""
        menu = self.context_menus.get(menu_type)
        if menu:
            menu.exec(position)

    def _placeholder_action(self, action_name: str):
        """Placeholder for context menu actions"""
        print(f"Context menu action: {action_name}")


    def _show_preferences(self):
        """Show general preferences dialog"""
        try:
            from app_settings_system import SettingsDialog
            dialog = SettingsDialog(self.main_window.app_settings, self.main_window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.main_window.log_message("Preferences updated")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to open preferences: {str(e)}")
    
    def _show_gui_settings(self):
        """Show comprehensive GUI customization dialog"""
        try:
            dialog = GUISettingsDialog(self.main_window.app_settings, self.main_window)
            
            # Connect signals
            dialog.settings_changed.connect(self._apply_gui_changes)
            dialog.theme_changed.connect(self._apply_theme_change)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to open GUI settings: {str(e)}")
    
    def _show_button_customization(self):
        """Show button customization dialog"""
        dialog = ButtonCustomizationDialog(self.main_window)
        dialog.exec()
    
    def _show_panel_customization(self):
        """Show panel customization dialog"""
        dialog = PanelCustomizationDialog(self.main_window)
        dialog.exec()
    
    def _show_theme_settings(self):
        """Show theme-specific settings"""
        dialog = ThemeSettingsDialog(self.main_window.app_settings, self.main_window)
        dialog.exec()
    
    def _show_language_settings(self):
        """Show language settings"""
        QMessageBox.information(
            self.main_window,
            "Language Settings",
            "Language settings coming soon!\n\nCurrently supported: English"
        )
    
    def _reset_layout(self):
        """Reset GUI layout to defaults"""
        reply = QMessageBox.question(
            self.main_window,
            "Reset Layout",
            "This will reset the GUI layout to default settings.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset layout settings
            settings = self.main_window.app_settings.current_settings
            settings["left_panel_width"] = 400
            settings["right_panel_width"] = 300
            settings["table_row_height"] = 25
            settings["widget_spacing"] = 5
            settings["layout_margins"] = 5
            
            self.main_window.app_settings.save_settings()
            self._apply_gui_changes()
            
            QMessageBox.information(
                self.main_window,
                "Layout Reset",
                "GUI layout has been reset to defaults!"
            )
    
    def _create_menus(self):
        """Create all menus"""
        for menu_name, menu_actions in self.menu_definition.menus.items():
            menu = self.menu_bar.addMenu(menu_name)
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
                action.setShortcut(QKeySequence(menu_action.shortcut))

            if menu_action.icon:
                action.setIcon(QIcon.fromTheme(menu_action.icon))

            action.setEnabled(menu_action.enabled)
            action.setCheckable(menu_action.checkable)

            # Store action
            self.actions[menu_action.action_id] = action

            # Add to menu
            menu.addAction(action)

            # Add separator after if needed
            if menu_action.separator_after:
                menu.addSeparator()

    def _populate_menu(self, menu: QMenu, menu_actions: List[MenuAction]):
        """Populate a menu with actions"""
        for menu_action in menu_actions:
            # Handle separators
            if menu_action.action_id.startswith("separator"):
                menu.addSeparator()
                continue

            # Skip invisible actions
            if not menu_action.visible:
                continue

            # Create QAction
            action = QAction(menu_action.text, self.main_window)

            # Set properties
            if menu_action.shortcut:
                action.setShortcut(QKeySequence(menu_action.shortcut))

            if menu_action.icon:
                action.setIcon(QIcon.fromTheme(menu_action.icon))

            action.setEnabled(menu_action.enabled)
            action.setCheckable(menu_action.checkable)

            # Store action for later reference
            self.actions[menu_action.action_id] = action

            # Add to menu
            menu.addAction(action)

            # Add separator after if needed
            if menu_action.separator_after:
                menu.addSeparator()

    def _connect_callbacks(self):
        """Connect actions to callbacks"""
        for action_id, callback in self.callbacks.items():
            if action_id in self.actions:
                self.actions[action_id].triggered.connect(callback)
            else:
                print(f"Warning: No action found for callback '{action_id}'")

    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set menu callbacks"""
        self.callbacks.update(callbacks)
        self._connect_callbacks()

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


    def _export_settings(self):
        """Export settings to file"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json
            import os
            
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export Settings",
                os.path.expanduser("~/IMG_Factory_Settings.json"),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                settings_data = {
                    "version": "1.5",
                    "export_date": str(datetime.now()),
                    "settings": self.main_window.app_settings.current_settings
                }
                
                with open(file_path, 'w') as f:
                    json.dump(settings_data, f, indent=2)
                
                QMessageBox.information(
                    self.main_window,
                    "Export Complete",
                    f"Settings exported successfully to:\n{file_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Export Failed",
                f"Failed to export settings:\n{str(e)}"
            )
    
    def _import_settings(self):
        """Import settings from file"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json
            
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Import Settings",
                os.path.expanduser("~"),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if "settings" in data:
                    # Backup current settings
                    backup = self.main_window.app_settings.current_settings.copy()
                    
                    try:
                        # Apply imported settings
                        self.main_window.app_settings.current_settings.update(data["settings"])
                        self.main_window.app_settings.save_settings()
                        self._apply_gui_changes()
                        
                        QMessageBox.information(
                            self.main_window,
                            "Import Complete",
                            f"Settings imported successfully from:\n{file_path}"
                        )
                        
                    except Exception as e:
                        # Restore backup on error
                        self.main_window.app_settings.current_settings = backup
                        raise e
                else:
                    QMessageBox.warning(
                        self.main_window,
                        "Invalid File",
                        "The selected file doesn't contain valid IMG Factory settings."
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Import Failed",
                f"Failed to import settings:\n{str(e)}"
            )
    
    def _apply_gui_changes(self):
        """Apply GUI changes to the main window"""
        try:
            # Apply theme changes
            from app_settings_system import apply_theme_to_app
            from PyQt6.QtWidgets import QApplication
            
            apply_theme_to_app(QApplication.instance(), self.main_window.app_settings)
            
            # Apply layout changes
            self._apply_layout_changes()
            
            # Apply font changes
            self._apply_font_changes()
            
            # Apply icon changes
            self._apply_icon_changes()
            
            # Log the change
            self.main_window.log_message("GUI settings applied successfully")
            
        except Exception as e:
            self.main_window.log_message(f"Error applying GUI changes: {str(e)}")
    
    def _apply_theme_change(self, theme_code: str):
        """Apply theme change"""
        try:
            from app_settings_system import apply_theme_to_app
            from PyQt6.QtWidgets import QApplication
            
            apply_theme_to_app(QApplication.instance(), self.main_window.app_settings)
            self.main_window.log_message(f"Theme changed to: {theme_code}")
            
        except Exception as e:
            self.main_window.log_message(f"Error applying theme: {str(e)}")
    
    def _apply_layout_changes(self):
        """Apply layout setting changes"""
        settings = self.main_window.app_settings.current_settings
        
        # Apply panel sizes if GUI layout exists
        if hasattr(self.main_window, 'gui_layout'):
            gui_layout = self.main_window.gui_layout
            
            # Set panel widths
            left_width = settings.get("left_panel_width", 400)
            right_width = settings.get("right_panel_width", 300)
            
            if hasattr(gui_layout, 'main_splitter'):
                # Update splitter sizes
                total_width = gui_layout.main_splitter.width()
                center_width = total_width - left_width - right_width
                gui_layout.main_splitter.setSizes([left_width, center_width, right_width])
            
            # Apply table row height
            row_height = settings.get("table_row_height", 25)
            if hasattr(gui_layout, 'table'):
                gui_layout.table.verticalHeader().setDefaultSectionSize(row_height)
    
    def _apply_font_changes(self):
        """Apply font setting changes"""
        settings = self.main_window.app_settings.current_settings
        
        # Apply font scaling
        font_scale = settings.get("font_scale", 100) / 100.0
        
        if font_scale != 1.0:
            # Apply font scaling to application
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            
            current_font = app.font()
            new_size = int(current_font.pointSize() * font_scale)
            current_font.setPointSize(new_size)
            app.setFont(current_font)
    
    def _apply_icon_changes(self):
        """Apply icon setting changes"""
        settings = self.main_window.app_settings.current_settings
        
        # Update menu icons visibility
        show_menu_icons = settings.get("show_menu_icons", True)
        self._update_menu_icons_visibility(show_menu_icons)
        
        # Update icon sizes
        menu_icon_size = settings.get("menu_icon_size", 16)
        self._update_menu_icon_sizes(menu_icon_size)
    
    def _update_menu_icons_visibility(self, show_icons: bool):
        """Update visibility of menu icons"""
        for action in self.actions.values():
            if not show_icons:
                action.setIcon(QIcon())  # Remove icon
            # Note: Re-adding icons would require storing original icon data
    
    def _update_menu_icon_sizes(self, size: int):
        """Update menu icon sizes"""
        # This would require recreating icons at the new size
        # Implementation depends on your icon management system
        pass


# Additional dialog classes for specialized settings:

class ButtonCustomizationDialog(QDialog):
    """Dialog for customizing button appearance and behavior"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔘 Button Customization")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Button style options
        style_group = QGroupBox("Button Style")
        style_layout = QVBoxLayout(style_group)
        
        self.style_group = QButtonGroup()
        
        flat_style = QRadioButton("Flat style")
        raised_style = QRadioButton("Raised style")
        rounded_style = QRadioButton("Rounded corners")
        gradient_style = QRadioButton("Gradient style")
        
        self.style_group.addButton(flat_style, 0)
        self.style_group.addButton(raised_style, 1)
        self.style_group.addButton(rounded_style, 2)
        self.style_group.addButton(gradient_style, 3)
        
        style_layout.addWidget(flat_style)
        style_layout.addWidget(raised_style)
        style_layout.addWidget(rounded_style)
        style_layout.addWidget(gradient_style)
        
        layout.addWidget(style_group)
        
        # Button size options
        size_group = QGroupBox("Button Sizes")
        size_layout = QGridLayout(size_group)
        
        size_layout.addWidget(QLabel("Button Height:"), 0, 0)
        self.button_height_spin = QSpinBox()
        self.button_height_spin.setRange(20, 60)
        self.button_height_spin.setSuffix(" px")
        size_layout.addWidget(self.button_height_spin, 0, 1)
        
        size_layout.addWidget(QLabel("Button Padding:"), 1, 0)
        self.button_padding_spin = QSpinBox()
        self.button_padding_spin.setRange(2, 20)
        self.button_padding_spin.setSuffix(" px")
        size_layout.addWidget(self.button_padding_spin, 1, 1)
        
        layout.addWidget(size_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)


class PanelCustomizationDialog(QDialog):
    """Dialog for customizing panel layout and behavior"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📐 Panel Customization")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Panel visibility
        visibility_group = QGroupBox("Panel Visibility")
        visibility_layout = QVBoxLayout(visibility_group)
        
        self.show_left_panel_check = QCheckBox("Show left panel")
        self.show_right_panel_check = QCheckBox("Show right panel")
        self.show_status_bar_check = QCheckBox("Show status bar")
        self.show_log_panel_check = QCheckBox("Show log panel")
        
        visibility_layout.addWidget(self.show_left_panel_check)
        visibility_layout.addWidget(self.show_right_panel_check)
        visibility_layout.addWidget(self.show_status_bar_check)
        visibility_layout.addWidget(self.show_log_panel_check)
        
        layout.addWidget(visibility_group)
        
        # Panel behavior
        behavior_group = QGroupBox("Panel Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.collapsible_panels_check = QCheckBox("Enable collapsible panels")
        self.remember_panel_state_check = QCheckBox("Remember panel states")
        self.auto_hide_panels_check = QCheckBox("Auto-hide inactive panels")
        
        behavior_layout.addWidget(self.collapsible_panels_check)
        behavior_layout.addWidget(self.remember_panel_state_check)
        behavior_layout.addWidget(self.auto_hide_panels_check)
        
        layout.addWidget(behavior_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)


class ThemeSettingsDialog(QDialog):
    """Dialog for theme-specific customization"""
    
    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self.setWindowTitle("🎨 Theme Settings")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Theme list
        theme_group = QGroupBox("Available Themes")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_list = QListWidget()
        themes = [
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
        ]
        
        for theme in themes:
            self.theme_list.addItem(theme)
        
        theme_layout.addWidget(self.theme_list)
        layout.addWidget(theme_group)
        
        # Theme actions
        action_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self._preview_theme)
        action_layout.addWidget(preview_btn)
        
        import_btn = QPushButton("Import Theme...")
        import_btn.clicked.connect(self._import_theme)
        action_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export Theme...")
        export_btn.clicked.connect(self._export_theme)
        action_layout.addWidget(export_btn)
        
        layout.addLayout(action_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_theme)
        button_layout.addWidget(apply_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _preview_theme(self):
        """Preview selected theme"""
        current_item = self.theme_list.currentItem()
        if current_item:
            QMessageBox.information(self, "Preview", f"Previewing theme: {current_item.text()}")
    
    def _import_theme(self):
        """Import theme from file"""
        QMessageBox.information(self, "Import Theme", "Theme import functionality coming soon!")
    
    def _export_theme(self):
        """Export current theme"""
        QMessageBox.information(self, "Export Theme", "Theme export functionality coming soon!")
    
    def _apply_theme(self):
        """Apply selected theme"""
        current_item = self.theme_list.currentItem()
        if current_item:
            QMessageBox.information(self, "Theme Applied", f"Applied theme: {current_item.text()}")

# Export main classes
__all__ = [
    'MenuAction',
    'MenuDefinition',
    'IMGFactoryMenuBar',
    'MenuCustomizationDialog',
    'ContextMenuManager'
]
