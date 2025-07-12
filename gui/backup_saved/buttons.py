#this belongs in gui/ buttons.py - Version: 15

#!/usr/bin/env python3
"""
X-Seti - June28 2025 - IMG Factory 1.5
Modular button system with customizable layouts and tear-off functionality
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QMenu, QDialog, QListWidget, QListWidgetItem,
    QCheckBox, QSpinBox, QLabel, QComboBox, QMessageBox, QFileDialog,
    QApplication, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QCursor, QAction


class DraggableButton(QPushButton):
    """Button that can be dragged and rearranged"""
    
    button_moved = pyqtSignal(str, QPoint)  # button_id, new_position
    
    def __init__(self, text: str, button_id: str, action_type: str = "default"):
        super().__init__(text)
        self.button_id = button_id
        self.action_type = action_type
        self.callback = None
        self.is_enabled_by_default = True
        
        # Make buttons smaller
        self.setMaximumHeight(24)
        self.setMinimumHeight(20)
        self.setMaximumWidth(80)
        self.setMinimumWidth(60)
        
        # Set properties for theming
        self.setProperty("action-type", action_type)
        self.setProperty("button-id", button_id)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.drag_start_position = QPoint()
    
    def set_callback(self, callback: Callable):
        """Set button callback"""
        self.callback = callback
        if callback:
            self.clicked.connect(callback)
    
    def mousePressEvent(self, event):
        """Handle mouse press for drag start"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        # Create drag
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.button_id)
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.render(painter)
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.drag_start_position)
        
        # Execute drag
        drop_action = drag.exec(Qt.DropAction.MoveAction)


class ButtonPreset:
    """Represents a button layout preset"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.button_configs: List[Dict] = []
        self.layout_type = "grid"  # grid, vertical, horizontal
        self.grid_columns = 3
        self.spacing = 2
        self.group_name = ""
    
    def add_button(self, button_id: str, text: str, action_type: str, 
                   position: tuple = None, enabled: bool = True):
        """Add button configuration"""
        config = {
            "id": button_id,
            "text": text,
            "action_type": action_type,
            "position": position,
            "enabled": enabled,
            "visible": True
        }
        self.button_configs.append(config)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            "name": self.name,
            "description": self.description,
            "button_configs": self.button_configs,
            "layout_type": self.layout_type,
            "grid_columns": self.grid_columns,
            "spacing": self.spacing,
            "group_name": self.group_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ButtonPreset':
        """Create from dictionary"""
        preset = cls(data["name"], data.get("description", ""))
        preset.button_configs = data.get("button_configs", [])
        preset.layout_type = data.get("layout_type", "grid")
        preset.grid_columns = data.get("grid_columns", 3)
        preset.spacing = data.get("spacing", 2)
        preset.group_name = data.get("group_name", "")
        return preset


class ButtonFactory:
    """Factory for creating standard IMG Factory buttons"""
    
    # Standard button definitions
    BUTTON_DEFINITIONS = {
        # IMG Operations
        "open": {"text": "Open", "action_type": "import", "group": "img"},
        "close": {"text": "Close", "action_type": "default", "group": "img"},
        "close_all": {"text": "Close All", "action_type": "default", "group": "img"},
        "rebuild": {"text": "Rebuild", "action_type": "update", "group": "img"},
        "rebuild_as": {"text": "Rebuild As", "action_type": "update", "group": "img"},
        "rebuild_all": {"text": "Rebuild All", "action_type": "update", "group": "img"},
        "merge": {"text": "Merge", "action_type": "convert", "group": "img"},
        "split": {"text": "Split", "action_type": "convert", "group": "img"},
        "convert": {"text": "Convert", "action_type": "convert", "group": "img"},
        
        # Entry Operations
        "import": {"text": "Import", "action_type": "import", "group": "entries"},
        "import_via": {"text": "Import via", "action_type": "import", "group": "entries"},
        "update_list": {"text": "Update list", "action_type": "update", "group": "entries"},
        "export": {"text": "Export", "action_type": "export", "group": "entries"},
        "export_via": {"text": "Export via", "action_type": "export", "group": "entries"},
        "quick_export": {"text": "Quick Export", "action_type": "export", "group": "entries"},
        "remove": {"text": "Remove", "action_type": "remove", "group": "entries"},
        "remove_via": {"text": "Remove via", "action_type": "remove", "group": "entries"},
        "dump": {"text": "Dump", "action_type": "update", "group": "entries"},
        "rename": {"text": "Rename", "action_type": "default", "group": "entries"},
        "replace": {"text": "Replace", "action_type": "convert", "group": "entries"},
        
        # Selection Operations
        "select_all": {"text": "Select All", "action_type": "default", "group": "selection"},
        "select_inverse": {"text": "Select Inverse", "action_type": "default", "group": "selection"},
        "sort": {"text": "Sort", "action_type": "default", "group": "selection"},
        
        # Advanced Operations
        "open_multiple": {"text": "📁 Multiple", "action_type": "import", "group": "advanced"},
        "new_img": {"text": "🆕 New", "action_type": "import", "group": "advanced"},
    }
    
    @classmethod
    def create_button(cls, button_id: str, callbacks: Dict[str, Callable] = None) -> DraggableButton:
        """Create a button by ID"""
        if button_id not in cls.BUTTON_DEFINITIONS:
            raise ValueError(f"Unknown button ID: {button_id}")
        
        definition = cls.BUTTON_DEFINITIONS[button_id]
        button = DraggableButton(
            definition["text"],
            button_id,
            definition["action_type"]
        )
        
        # Set callback if provided
        if callbacks and button_id in callbacks:
            button.set_callback(callbacks[button_id])
        
        return button
    
    @classmethod
    def get_default_presets(cls) -> List[ButtonPreset]:
        """Get default button presets"""
        presets = []
        
        # IMG Operations Preset
        img_preset = ButtonPreset("IMG Operations", "Standard IMG file operations")
        img_preset.group_name = "IMG"
        img_preset.grid_columns = 3
        for button_id in ["open", "close", "close_all", "rebuild", "rebuild_as", 
                         "rebuild_all", "merge", "split", "convert"]:
            definition = cls.BUTTON_DEFINITIONS[button_id]
            img_preset.add_button(button_id, definition["text"], definition["action_type"])
        presets.append(img_preset)
        
        # Entries Operations Preset
        entries_preset = ButtonPreset("Entries Operations", "File entry management")
        entries_preset.group_name = "Entries"
        entries_preset.grid_columns = 3
        for button_id in ["import", "import_via", "update_list", "export", "export_via",
                         "quick_export", "remove", "remove_via", "dump", "rename", 
                         "replace", "select_all", "select_inverse", "sort"]:
            definition = cls.BUTTON_DEFINITIONS[button_id]
            entries_preset.add_button(button_id, definition["text"], definition["action_type"])
        presets.append(entries_preset)
        
        # Compact Preset
        compact_preset = ButtonPreset("Compact", "Essential buttons only")
        compact_preset.group_name = "Essential"
        compact_preset.grid_columns = 2
        for button_id in ["open", "close", "import", "export", "rebuild", "new_img"]:
            definition = cls.BUTTON_DEFINITIONS[button_id]
            compact_preset.add_button(button_id, definition["text"], definition["action_type"])
        presets.append(compact_preset)
        
        return presets


class ButtonPresetManager:
    """Manages button presets and customization"""
    
    def __init__(self, settings_path: str = None):
        if settings_path is None:
            self.settings_path = Path.home() / ".imgfactory" / "button_presets.json"
        else:
            self.settings_path = Path(settings_path)
        
        self.presets: Dict[str, ButtonPreset] = {}
        self.current_preset_name = "IMG Operations"
        self._load_presets()
    
    def _load_presets(self):
        """Load presets from file"""
        try:
            if self.settings_path.exists():
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                
                for preset_data in data.get("presets", []):
                    preset = ButtonPreset.from_dict(preset_data)
                    self.presets[preset.name] = preset
                
                self.current_preset_name = data.get("current_preset", "IMG Operations")
            
            # Always ensure default presets exist
            default_presets = ButtonFactory.get_default_presets()
            for preset in default_presets:
                if preset.name not in self.presets:
                    self.presets[preset.name] = preset
            
        except Exception as e:
            print(f"Error loading button presets: {e}")
            # Load defaults
            for preset in ButtonFactory.get_default_presets():
                self.presets[preset.name] = preset
    
    def _save_presets(self):
        """Save presets to file"""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "current_preset": self.current_preset_name,
                "presets": [preset.to_dict() for preset in self.presets.values()]
            }
            
            with open(self.settings_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"Error saving button presets: {e}")
    
    def get_preset(self, name: str) -> Optional[ButtonPreset]:
        """Get preset by name"""
        return self.presets.get(name)
    
    def get_current_preset(self) -> Optional[ButtonPreset]:
        """Get currently active preset"""
        return self.presets.get(self.current_preset_name)
    
    def set_current_preset(self, name: str):
        """Set current preset"""
        if name in self.presets:
            self.current_preset_name = name
            self._save_presets()
    
    def save_preset(self, preset: ButtonPreset):
        """Save a preset"""
        self.presets[preset.name] = preset
        self._save_presets()
    
    def delete_preset(self, name: str) -> bool:
        """Delete a preset"""
        if name in self.presets and name not in ["IMG Operations", "Entries Operations", "Compact"]:
            del self.presets[name]
            if self.current_preset_name == name:
                self.current_preset_name = "IMG Operations"
            self._save_presets()
            return True
        return False
    
    def get_preset_names(self) -> List[str]:
        """Get list of preset names"""
        return list(self.presets.keys())


class ButtonCustomizationDialog(QDialog):
    """Dialog for customizing button layouts"""
    
    preset_changed = pyqtSignal(str)  # preset_name
    
    def __init__(self, preset_manager: ButtonPresetManager, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.setWindowTitle("Customize Button Layout")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self._create_ui()
        self._load_current_preset()
    
    def _create_ui(self):
        """Create the customization UI"""
        layout = QVBoxLayout(self)
        
        # Preset selection
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.preset_manager.get_preset_names())
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        
        self.save_preset_btn = QPushButton("Save As...")
        self.save_preset_btn.clicked.connect(self._save_preset)
        preset_layout.addWidget(self.save_preset_btn)
        
        self.delete_preset_btn = QPushButton("Delete")
        self.delete_preset_btn.clicked.connect(self._delete_preset)
        preset_layout.addWidget(self.delete_preset_btn)
        
        layout.addLayout(preset_layout)
        
        # Available buttons
        available_group = QGroupBox("Available Buttons")
        available_layout = QVBoxLayout(available_group)
        
        self.available_list = QListWidget()
        self._populate_available_buttons()
        available_layout.addWidget(self.available_list)
        
        layout.addWidget(available_group)
        
        # Layout settings
        settings_group = QGroupBox("Layout Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        settings_layout.addWidget(QLabel("Columns:"))
        self.columns_spin = QSpinBox()
        self.columns_spin.setRange(1, 6)
        self.columns_spin.setValue(3)
        settings_layout.addWidget(self.columns_spin)
        
        settings_layout.addWidget(QLabel("Spacing:"))
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 10)
        self.spacing_spin.setValue(2)
        settings_layout.addWidget(self.spacing_spin)
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_available_buttons(self):
        """Populate available buttons list"""
        for button_id, definition in ButtonFactory.BUTTON_DEFINITIONS.items():
            item = QListWidgetItem(f"{definition['text']} ({button_id})")
            item.setData(Qt.ItemDataRole.UserRole, button_id)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.available_list.addItem(item)
    
    def _load_current_preset(self):
        """Load current preset into UI"""
        current_preset = self.preset_manager.get_current_preset()
        if current_preset:
            self.preset_combo.setCurrentText(current_preset.name)
            self.columns_spin.setValue(current_preset.grid_columns)
            self.spacing_spin.setValue(current_preset.spacing)
            
            # Update checkboxes
            enabled_buttons = {config["id"] for config in current_preset.button_configs}
            for i in range(self.available_list.count()):
                item = self.available_list.item(i)
                button_id = item.data(Qt.ItemDataRole.UserRole)
                if button_id in enabled_buttons:
                    item.setCheckState(Qt.CheckState.Checked)
    
    def _on_preset_changed(self, preset_name: str):
        """Handle preset change"""
        preset = self.preset_manager.get_preset(preset_name)
        if preset:
            self.columns_spin.setValue(preset.grid_columns)
            self.spacing_spin.setValue(preset.spacing)
            
            # Update checkboxes
            enabled_buttons = {config["id"] for config in preset.button_configs}
            for i in range(self.available_list.count()):
                item = self.available_list.item(i)
                button_id = item.data(Qt.ItemDataRole.UserRole)
                item.setCheckState(
                    Qt.CheckState.Checked if button_id in enabled_buttons 
                    else Qt.CheckState.Unchecked
                )
    
    def _save_preset(self):
        """Save current configuration as new preset"""
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            preset = self._create_preset_from_ui(name)
            self.preset_manager.save_preset(preset)
            
            # Update combo box
            self.preset_combo.clear()
            self.preset_combo.addItems(self.preset_manager.get_preset_names())
            self.preset_combo.setCurrentText(name)
    
    def _delete_preset(self):
        """Delete current preset"""
        current_name = self.preset_combo.currentText()
        if self.preset_manager.delete_preset(current_name):
            self.preset_combo.clear()
            self.preset_combo.addItems(self.preset_manager.get_preset_names())
            QMessageBox.information(self, "Success", f"Preset '{current_name}' deleted.")
        else:
            QMessageBox.warning(self, "Error", "Cannot delete default preset.")
    
    def _create_preset_from_ui(self, name: str) -> ButtonPreset:
        """Create preset from UI settings"""
        preset = ButtonPreset(name)
        preset.grid_columns = self.columns_spin.value()
        preset.spacing = self.spacing_spin.value()
        
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                button_id = item.data(Qt.ItemDataRole.UserRole)
                definition = ButtonFactory.BUTTON_DEFINITIONS[button_id]
                preset.add_button(button_id, definition["text"], definition["action_type"])
        
        return preset
    
    def _apply_changes(self):
        """Apply changes to current preset"""
        current_name = self.preset_combo.currentText()
        preset = self._create_preset_from_ui(current_name)
        preset.name = current_name
        
        self.preset_manager.save_preset(preset)
        self.preset_manager.set_current_preset(current_name)
        self.preset_changed.emit(current_name)


# Export main classes
__all__ = [
    'DraggableButton',
    'ButtonPreset', 
    'ButtonFactory',
    'ButtonPresetManager',
    'ButtonCustomizationDialog'
]
