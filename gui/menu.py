#this belongs in gui/ menu.py - version 14

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
    
    def __init__(self, main_window, panel_manager: PanelManager = None):
        self.main_window = main_window
        self.panel_manager = panel_manager
        self.menu_bar = main_window.menuBar()
        self.callbacks: Dict[str, Callable] = {}
        self.actions: Dict[str, QAction] = {}
        
        self.menu_definition = MenuDefinition()
        self._create_menus()
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """Set menu callbacks"""
        self.callbacks.update(callbacks)
        self._connect_callbacks()
    
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


# Export main classes
__all__ = [
    'MenuAction',
    'MenuDefinition',
    'IMGFactoryMenuBar',
    'MenuCustomizationDialog',
    'ContextMenuManager'
]
