#this belongs in gui/ panel_controls.py - Version: 5
# X-Seti - July12 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory Panel Controls - Button Panel customization
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, 
    QComboBox, QLineEdit, QLabel, QSizePolicy, QButtonGroup,
    QListWidget, QListWidgetItem, QSpinBox, QCheckBox, QDialog,
    QFormLayout, QTabWidget, QScrollArea, QFrame
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field

class DraggableButton(QPushButton):
    """Advanced button with drag-and-drop functionality"""
    
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
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if ((event.pos() - self.drag_start_position).manhattanLength() < 
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
    """Button layout preset configuration"""

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
    
    @classmethod
    def create_button(cls, button_id: str, callbacks: Dict[str, Callable] = None) -> DraggableButton:
        """Create a button by ID"""
        if button_id not in BUTTON_DEFINITIONS:
            raise ValueError(f"Unknown button ID: {button_id}")
        
        definition = BUTTON_DEFINITIONS[button_id]
        button = DraggableButton(
            definition["text"],
            button_id,
            definition["action_type"]
        )
        
        # Set callback if provided
        if callbacks and button_id in callbacks:
            button.set_callback(callbacks[button_id])
        
        return button


class ButtonPresetManager:
    """Manages button presets and customization"""
    
    def __init__(self, settings_path: str = None):
        if settings_path is None:
            from pathlib import Path
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
                import json
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                
                for preset_data in data.get("presets", []):
                    preset = ButtonPreset.from_dict(preset_data)
                    self.presets[preset.name] = preset
                
                self.current_preset_name = data.get("current_preset", "IMG Operations")
            
            # Always ensure default presets exist
            self._create_default_presets()
            
        except Exception as e:
            print(f"Error loading button presets: {e}")
            self._create_default_presets()
    
    def _create_default_presets(self):
        """Create default presets"""
        if "IMG Operations" not in self.presets:
            img_preset = ButtonPreset("IMG Operations", "Standard IMG file operations")
            img_preset.group_name = "IMG"
            img_preset.grid_columns = 3
            for button_id in ["open", "close", "rebuild", "merge", "split"]:
                if button_id in BUTTON_DEFINITIONS:
                    definition = BUTTON_DEFINITIONS[button_id]
                    img_preset.add_button(button_id, definition["text"], definition["action_type"])
            self.presets[img_preset.name] = img_preset
    
    def _save_presets(self):
        """Save presets to file"""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            import json
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
    
    def get_preset_names(self) -> List[str]:
        """Get list of preset names"""
        return list(self.presets.keys())

def set_button_icon_mode(panel, show_icons=True):
    """Toggle between icon and text mode for buttons"""
    for child in panel.findChildren(QPushButton):
        if show_icons and hasattr(child, '_original_text'):
            # Show icons only
            child.setText("")
            if hasattr(child, '_icon'):
                child.setIcon(child._icon)
        else:
            # Show text (store original text if not stored)
            if not hasattr(child, '_original_text'):
                child._original_text = child.text()
            if hasattr(child, '_original_text'):
                child.setText(child._original_text)


def apply_button_theme_properties(button, action_type):
    """Apply theme properties to a button"""
    if action_type:
        button.setProperty("action-type", action_type)
    
    # Set size policy and minimum size
    button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    button.setMinimumHeight(28)
    
    # Add hover effects through stylesheet
    button.setStyleSheet(button.styleSheet() + """
        QPushButton {
            font-size: 9pt;
            padding: 4px 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        QPushButton:pressed {
            background-color: rgba(0, 0, 0, 0.1);
        }
    """)


def update_button_states(main_window, img_loaded=False, entries_selected=False):
    """Update button enabled/disabled states based on context"""
    # IMG operation buttons
    img_dependent_buttons = [
        'close_img_file', 'refresh_table', 'rebuild_img', 'rebuild_img_as',
        'merge_img', 'split_img', 'convert_img_format', 'validate_img',
        'show_img_info', 'import_files', 'export_all_entries'
    ]
    
    # Entry operation buttons (require selection)
    selection_dependent_buttons = [
        'export_selected', 'export_selected_via', 'quick_export_selected',
        'remove_selected', 'rename_entry', 'replace_entry'
    ]
    
    # Update button states
    for attr_name in img_dependent_buttons:
        if hasattr(main_window, attr_name):
            button = getattr(main_window, attr_name)
            if hasattr(button, 'setEnabled'):
                button.setEnabled(img_loaded)
    
    for attr_name in selection_dependent_buttons:
        if hasattr(main_window, attr_name):
            button = getattr(main_window, attr_name)
            if hasattr(button, 'setEnabled'):
                button.setEnabled(img_loaded and entries_selected)


# ============================================================================
# MAIN INTEGRATION FUNCTION
# ============================================================================

def setup_consolidated_panel_controls(main_window):
    """Setup consolidated panel controls system"""
    try:
        # Create panel manager
        panel_manager = PanelManager(main_window)
        main_window.panel_manager = panel_manager
        
        # Create main control panel
        control_panel = create_control_panel(main_window)
        main_window.control_panel = control_panel
        
        # Log success
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Consolidated panel controls setup complete")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error setting up panel controls: {str(e)}")
        return False


# ============================================================================
# EXPORTS - Complete list including all button system components
# ============================================================================

__all__ = [
    # Button definitions
    
    # Main panel functions (gui_layout.py compatible)
    
    # Panel section functions
    'create_img_operations_section',
    'create_entry_operations_section', 
    'create_tools_section',
    'create_templates_section',
    
    # Button creation functions
    'create_pastel_button',
    'get_short_text',
    'lighten_color',
    'darken_color',
    'placeholder_function',
    
    # Advanced button system (from buttons.py)
    'DraggableButton',
    'ButtonPreset',
    'ButtonFactory',
    'ButtonPresetManager',
    
    # Panel classes (from panels.py)
    'ButtonPanel',
    'PanelManager',
    
    # Utility functions (from control_panels.py)
    'set_button_icon_mode',
    'apply_button_theme_properties',
    'update_button_states',
    
    # Integration function
    'setup_consolidated_panel_controls'
]
