#this belongs in gui/ panel_controls.py - Version: 3
# X-Seti - July13 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
Panel Controls - Utility Functions Only
Cleaned version with NO duplicate button creation - gui_layout.py is the master
Contains only utility functions for styling, colors, and button state management
"""

from typing import Dict, Callable, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon


# ============================================================================
# COLOR UTILITY FUNCTIONS - Keep these, they're used by gui_layout.py
# ============================================================================

def lighten_color(color: str, factor: float = 0.1) -> str:
    """Lighten a hex color by a factor"""
    try:
        if not color.startswith('#') or len(color) != 7:
            return color
        
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except:
        return color


def darken_color(color: str, factor: float = 0.1) -> str:
    """Darken a hex color by a factor"""
    try:
        if not color.startswith('#') or len(color) != 7:
            return color
        
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except:
        return color


def get_short_text(text: str) -> str:
    """Get shortened text for buttons"""
    short_mapping = {
        "Import Via": "Import>",
        "Export Via": "Export>", 
        "Quick Export": "QuickExp",
        "Export All": "ExpAll",
        "Dump All": "Dump",
        "🔄 Refresh": "🔄",
        "🔍 Search": "🔍",
        "ℹ️ Info": "ℹ️",
        "🔢 Sort": "🔢",
        "☑️ Select All": "☑️",
        "Rebuild As": "RebuildAs",
        "Close All": "CloseAll",
        "Rebuild All": "RebuildAll",
    }
    return short_mapping.get(text, text[:6])


# ============================================================================
# BUTTON STYLING UTILITIES - Keep these, they're useful
# ============================================================================

def create_pastel_button(main_window, label: str, action_type: str, icon: str, bg_color: str, method_name: str):
    """
    Create a pastel button with styling - UTILITY FUNCTION ONLY
    This is called by gui_layout.py (the master) - does NOT create duplicate buttons
    """
    btn = QPushButton(label)
    btn.setMaximumHeight(22)
    btn.setMinimumHeight(20)

    # Set icon if provided
    if icon:
        try:
            btn.setIcon(QIcon.fromTheme(icon))
        except:
            pass

    # Apply pastel styling
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg_color};
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 8pt;
            font-weight: normal;
        }}
        QPushButton:hover {{
            background-color: {lighten_color(bg_color)};
            border: 1px solid #aaaaaa;
        }}
        QPushButton:pressed {{
            background-color: {darken_color(bg_color)};
            border: 1px solid #999999;
        }}
        QPushButton:disabled {{
            background-color: #f5f5f5;
            color: #999999;
            border: 1px solid #dddddd;
        }}
    """)

    # Connect to method if it exists
    if hasattr(main_window, method_name):
        btn.clicked.connect(getattr(main_window, method_name))
    else:
        # Placeholder for missing methods
        btn.clicked.connect(lambda: placeholder_function(main_window, method_name))

    return btn


def placeholder_function(main_window, method_name: str):
    """Placeholder function for missing methods"""
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"🚧 {method_name} - Not yet implemented")
    else:
        print(f"🚧 {method_name} - Not yet implemented")


# ============================================================================
# BUTTON STATE MANAGEMENT - Keep these utilities
# ============================================================================

def update_button_states(main_window, img_loaded: bool = False, entries_selected: bool = False):
    """Update button enabled/disabled states based on context"""
    try:
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
        
        # Update IMG-dependent buttons
        for attr_name in img_dependent_buttons:
            if hasattr(main_window, attr_name):
                button = getattr(main_window, attr_name)
                if hasattr(button, 'setEnabled'):
                    button.setEnabled(img_loaded)
        
        # Update selection-dependent buttons  
        for attr_name in selection_dependent_buttons:
            if hasattr(main_window, attr_name):
                button = getattr(main_window, attr_name)
                if hasattr(button, 'setEnabled'):
                    button.setEnabled(img_loaded and entries_selected)
                    
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Button state update error: {str(e)}")


def set_button_icon_mode(panel, show_icons: bool = True):
    """Toggle between icon and text mode for buttons"""
    try:
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
    except Exception as e:
        print(f"Icon mode error: {e}")


def apply_button_theme_properties(button, action_type: str):
    """Apply theme properties to a button"""
    try:
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
    except Exception as e:
        print(f"Theme property error: {e}")


# ============================================================================
# SIMPLE PANEL UTILITIES - Keep for compatibility
# ============================================================================

class FilterSearchPanel(QWidget):
    """Simple filter and search panel"""
    
    filter_changed = pyqtSignal(str, str)  # filter_type, value
    search_requested = pyqtSignal(str)     # search_text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("filter_search")
        self.setWindowTitle("Filter & Search")
        self._create_filter_controls()
    
    def _create_filter_controls(self):
        """Create filter and search controls"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        # Type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "DFF", "TXD", "COL", "IFP", "WAV", "SCM"])
        self.type_filter.currentTextChanged.connect(
            lambda text: self.filter_changed.emit("type", text)
        )
        type_layout.addWidget(self.type_filter)
        layout.addLayout(type_layout)
        
        # Search
        search_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.returnPressed.connect(self._do_search)
        search_layout.addWidget(self.search_box)
        
        self.find_btn = QPushButton("Find")
        self.find_btn.setMaximumWidth(50)
        self.find_btn.clicked.connect(self._do_search)
        search_layout.addWidget(self.find_btn)
        layout.addLayout(search_layout)
        
        layout.addStretch()
    
    def _do_search(self):
        """Perform search"""
        text = self.search_box.text().strip()
        self.search_requested.emit(text)


class ButtonPreset:
    """Button layout preset configuration"""

class ButtonPanel:
    """Panel containing configurable buttons"""

class ButtonPresetManager:
    """Manages button presets and customization"""

class FilterSearchPanel:
    """Simple filter and search panel"""

# ADVANCED BUTTON CLASSES - From gui/buttons.py

class DraggableButton:
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

# LEGACY COMPATIBILITY FUNCTIONS - REMOVED DUPLICATES

def create_control_panel(main_window):
    """
    LEGACY FUNCTION - NO LONGER CREATES PANELS
    gui_layout.py is now the master for all panel creation
    This is kept only for compatibility - returns None
    """
    if hasattr(main_window, 'log_message'):
        main_window.log_message("ℹ️ create_control_panel redirected to gui_layout.py")
    return None


def create_right_panel_with_pastel_buttons(main_window):
    """
    LEGACY FUNCTION - NO LONGER CREATES PANELS  
    gui_layout.py is now the master for all panel creation
    This is kept only for compatibility - returns None
    """
    if hasattr(main_window, 'log_message'):
        main_window.log_message("ℹ️ create_right_panel_with_pastel_buttons redirected to gui_layout.py")
    return None


# ============================================================================
# EXPORTS - UTILITIES ONLY, NO DUPLICATE CREATORS
# ============================================================================

__all__ = [
    # Color utilities
    'lighten_color',
    'darken_color', 
    'get_short_text',
    
    # Button styling utilities
    'create_pastel_button',  # Utility function used by gui_layout.py
    'placeholder_function',
    'apply_button_theme_properties',
    'set_button_icon_mode',
    
    # State management
    'update_button_states',
    
    # Simple panels
    'FilterSearchPanel',
    
    # Legacy compatibility (return None - redirect to gui_layout.py)
    'create_control_panel',
    'create_right_panel_with_pastel_buttons',
]
