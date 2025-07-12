#this belongs in gui/ panels.py - Version: 5

#!/usr/bin/env python3
"""
X-Seti - June28 2025 - IMG Factory 1.5
Tear-off panels system for flexible GUI layout
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QSplitter, QFrame, QLabel, QPushButton, QComboBox, QCheckBox,
    QSpinBox, QDialog, QListWidget, QListWidgetItem, QMessageBox,
    QApplication, QMenu, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QTimer
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QCursor, QIcon, QAction

from gui.buttons import (
    DraggableButton, ButtonFactory, ButtonPresetManager,
    ButtonCustomizationDialog, ButtonPreset
)


class TearOffPanel(QFrame):
    """Panel that can be torn off from main window"""
    
    panel_closed = pyqtSignal(str)  # panel_id
    panel_moved = pyqtSignal(str, QPoint)  # panel_id, position
    panel_resized = pyqtSignal(str, tuple)  # panel_id, (width, height)
    
    def __init__(self, panel_id: str, title: str, parent=None):
        super().__init__(parent)
        self.panel_id = panel_id
        self.title = title
        self.is_torn_off = False
        self.original_parent = parent
        self.original_layout_position = None
        
        # Setup frame
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setMinimumSize(200, 100)
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(3)
        
        # Title bar
        self._create_title_bar()
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_widget)
        
        # Drag handling
        self.drag_start_position = QPoint()
        self.setAcceptDrops(True)
    
    def _create_title_bar(self):
        """Create title bar with controls"""
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(24)
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
            }
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 2, 2, 2)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Customize button
        self.customize_btn = QPushButton("⚙")
        self.customize_btn.setFixedSize(16, 16)
        self.customize_btn.setToolTip("Customize panel")
        self.customize_btn.clicked.connect(self._show_customize_menu)
        title_layout.addWidget(self.customize_btn)
        
        # Tear off button
        self.tear_off_btn = QPushButton("📌" if not self.is_torn_off else "🔗")
        self.tear_off_btn.setFixedSize(16, 16)
        self.tear_off_btn.setToolTip("Tear off panel")
        self.tear_off_btn.clicked.connect(self.toggle_tear_off)
        title_layout.addWidget(self.tear_off_btn)
        
        # Close button (only when torn off)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setToolTip("Close panel")
        self.close_btn.clicked.connect(self._close_panel)
        self.close_btn.setVisible(False)
        title_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(self.title_bar)
    
    def _show_customize_menu(self):
        """Show customization menu"""
        menu = QMenu(self)
        
        # Change preset
        preset_menu = menu.addMenu("Change Preset")
        if hasattr(self, 'preset_manager'):
            for preset_name in self.preset_manager.get_preset_names():
                action = preset_menu.addAction(preset_name)
                action.triggered.connect(lambda checked, name=preset_name: self.apply_preset(name))
        
        # Customize layout
        customize_action = menu.addAction("Customize Layout...")
        customize_action.triggered.connect(self._show_customization_dialog)
        
        menu.addSeparator()
        
        # Reset to default
        reset_action = menu.addAction("Reset to Default")
        reset_action.triggered.connect(self.reset_to_default)
        
        menu.exec(QCursor.pos())
    
    def _show_customization_dialog(self):
        """Show customization dialog"""
        if hasattr(self, 'preset_manager'):
            dialog = ButtonCustomizationDialog(self.preset_manager, self)
            dialog.preset_changed.connect(self.apply_preset)
            dialog.exec()
    
    def toggle_tear_off(self):
        """Toggle tear off state"""
        if self.is_torn_off:
            self.dock_panel()
        else:
            self.tear_off_panel()
    
    def tear_off_panel(self):
        """Tear off panel to separate window"""
        if self.is_torn_off:
            return
        
        # Store original position
        self.original_parent = self.parent()
        self.original_layout_position = self._get_layout_position()
        
        # Remove from parent layout
        if self.parent():
            layout = self.parent().layout()
            if layout:
                layout.removeWidget(self)
        
        # Make it a top-level window
        self.setParent(None)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(f"IMG Factory - {self.title}")
        
        # Update UI
        self.is_torn_off = True
        self.tear_off_btn.setText("🔗")
        self.tear_off_btn.setToolTip("Dock panel")
        self.close_btn.setVisible(True)
        
        # Show as window
        self.show()
        self.raise_()
        
        # Position near cursor
        cursor_pos = QCursor.pos()
        self.move(cursor_pos.x() - 50, cursor_pos.y() - 50)
    
    def dock_panel(self):
        """Dock panel back to main window"""
        if not self.is_torn_off or not self.original_parent:
            return
        
        # Hide window
        self.hide()
        
        # Restore to original parent
        self.setParent(self.original_parent)
        self.setWindowFlags(Qt.WindowType.Widget)
        
        # Add back to layout
        if self.original_layout_position:
            self._restore_layout_position()
        
        # Update UI
        self.is_torn_off = False
        self.tear_off_btn.setText("📌")
        self.tear_off_btn.setToolTip("Tear off panel")
        self.close_btn.setVisible(False)
        
        # Show in parent
        self.show()
    
    def _close_panel(self):
        """Close panel (only when torn off)"""
        if self.is_torn_off:
            self.hide()
            self.panel_closed.emit(self.panel_id)
    
    def _get_layout_position(self) -> Optional[Dict]:
        """Get current position in parent layout"""
        if not self.parent():
            return None
        
        layout = self.parent().layout()
        if not layout:
            return None
        
        # For grid layout
        if isinstance(layout, QGridLayout):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() == self:
                    row, col, rowspan, colspan = layout.getItemPosition(i)
                    return {
                        "type": "grid",
                        "row": row,
                        "col": col,
                        "rowspan": rowspan,
                        "colspan": colspan
                    }
        
        # For other layouts
        elif hasattr(layout, 'indexOf'):
            index = layout.indexOf(self)
            if index >= 0:
                return {
                    "type": "linear",
                    "index": index
                }
        
        return None
    
    def _restore_layout_position(self):
        """Restore position in parent layout"""
        if not self.original_parent or not self.original_layout_position:
            return
        
        layout = self.original_parent.layout()
        if not layout:
            return
        
        pos_info = self.original_layout_position
        
        if pos_info["type"] == "grid" and isinstance(layout, QGridLayout):
            layout.addWidget(self, pos_info["row"], pos_info["col"], 
                           pos_info["rowspan"], pos_info["colspan"])
        elif pos_info["type"] == "linear":
            layout.insertWidget(pos_info["index"], self)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Only start drag from title bar
            title_bar_rect = self.title_bar.geometry()
            if title_bar_rect.contains(event.position().toPoint()):
                self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if self.drag_start_position.isNull():
            return
        
        # Only allow dragging from title bar
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        # If not torn off, tear off on drag
        if not self.is_torn_off:
            self.tear_off_panel()


class ButtonPanel(TearOffPanel):
    """Panel containing draggable buttons"""
    
    def __init__(self, panel_id: str, title: str, preset_manager: ButtonPresetManager, 
                 callbacks: Dict[str, Callable] = None, parent=None):
        super().__init__(panel_id, title, parent)
        self.preset_manager = preset_manager
        self.callbacks = callbacks or {}
        self.buttons: Dict[str, DraggableButton] = {}
        
        # Apply default preset
        self.apply_current_preset()
    
    def apply_preset(self, preset_name: str):
        """Apply a button preset"""
        preset = self.preset_manager.get_preset(preset_name)
        if not preset:
            return
        
        # Clear existing buttons
        self.clear_buttons()
        
        # Update title if preset has group name
        if preset.group_name:
            self.title_label.setText(preset.group_name)
        
        # Create layout based on preset
        if preset.layout_type == "grid":
            layout = QGridLayout()
            layout.setSpacing(preset.spacing)
            
            row, col = 0, 0
            for button_config in preset.button_configs:
                if not button_config.get("visible", True):
                    continue
                
                button = self._create_button_from_config(button_config)
                if button:
                    layout.addWidget(button, row, col)
                    self.buttons[button_config["id"]] = button
                    
                    col += 1
                    if col >= preset.grid_columns:
                        col = 0
                        row += 1
        
        else:  # vertical or horizontal
            if preset.layout_type == "vertical":
                layout = QVBoxLayout()
            else:
                layout = QHBoxLayout()
            
            layout.setSpacing(preset.spacing)
            
            for button_config in preset.button_configs:
                if not button_config.get("visible", True):
                    continue
                
                button = self._create_button_from_config(button_config)
                if button:
                    layout.addWidget(button)
                    self.buttons[button_config["id"]] = button
        
        # Set layout
        self._clear_content_layout()
        self.content_layout.addLayout(layout)
        
        # Update preset manager
        self.preset_manager.set_current_preset(preset_name)
    
    def apply_current_preset(self):
        """Apply currently selected preset"""
        current_preset = self.preset_manager.get_current_preset()
        if current_preset:
            self.apply_preset(current_preset.name)
    
    def reset_to_default(self):
        """Reset to default preset"""
        self.apply_preset("IMG Operations")
    
    def _create_button_from_config(self, config: Dict) -> Optional[DraggableButton]:
        """Create button from configuration"""
        try:
            button = ButtonFactory.create_button(config["id"], self.callbacks)
            button.setEnabled(config.get("enabled", True))
            
            # Override text if specified in config
            if "text" in config and config["text"] != button.text():
                button.setText(config["text"])
            
            return button
        except Exception as e:
            print(f"Error creating button {config.get('id', 'unknown')}: {e}")
            return None
    
    def clear_buttons(self):
        """Clear all buttons from panel"""
        self.buttons.clear()
        self._clear_content_layout()
    
    def _clear_content_layout(self):
        """Clear content layout"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
    
    def _clear_layout(self, layout):
        """Recursively clear layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())


class FilterSearchPanel(TearOffPanel):
    """Panel for filter and search controls"""
    
    filter_changed = pyqtSignal(str, str)  # filter_type, value
    search_requested = pyqtSignal(str)     # search_text
    
    def __init__(self, parent=None):
        super().__init__("filter_search", "Filter & Search", parent)
        self._create_filter_controls()
    
    def _create_filter_controls(self):
        """Create filter and search controls"""
        # Type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "DFF", "TXD", "COL", "IFP", "WAV", "SCM"])
        self.type_filter.currentTextChanged.connect(
            lambda text: self.filter_changed.emit("type", text)
        )
        type_layout.addWidget(self.type_filter)
        
        self.content_layout.addLayout(type_layout)
        
        # Version filter
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        
        self.version_filter = QComboBox()
        self.version_filter.addItems(["All Versions"])
        self.version_filter.currentTextChanged.connect(
            lambda text: self.filter_changed.emit("version", text)
        )
        version_layout.addWidget(self.version_filter)
        
        self.content_layout.addLayout(version_layout)
        
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
        
        self.content_layout.addLayout(search_layout)
        
        # Hit Tabs checkbox
        self.hit_tabs_check = QCheckBox("Hit Tabs")
        self.content_layout.addWidget(self.hit_tabs_check)
        
        self.content_layout.addStretch()
    
    def _do_search(self):
        """Perform search"""
        text = self.search_box.text().strip()
        self.search_requested.emit(text)


class PanelManager:
    """Manages all panels and their layouts"""
    
    def __init__(self, main_window, preset_manager: ButtonPresetManager):
        self.main_window = main_window
        self.preset_manager = preset_manager
        self.panels: Dict[str, TearOffPanel] = {}
        self.panel_settings_path = Path.home() / ".imgfactory" / "panel_layout.json"
        
        self._load_panel_settings()
    
    def create_default_panels(self, callbacks: Dict[str, Callable]) -> Dict[str, TearOffPanel]:
        """Create default panels"""
        panels = {}
        
        # IMG Operations Panel
        img_panel = ButtonPanel("img_ops", "IMG Operations", self.preset_manager, callbacks)
        panels["img_ops"] = img_panel
        
        # Entries Operations Panel  
        entries_panel = ButtonPanel("entries_ops", "Entries Operations", self.preset_manager, callbacks)
        # Set to entries preset
        entries_panel.apply_preset("Entries Operations")
        panels["entries_ops"] = entries_panel
        
        # Filter & Search Panel
        filter_panel = FilterSearchPanel()
        panels["filter_search"] = filter_panel
        
        # Store panels
        self.panels.update(panels)
        
        # Connect signals
        for panel in panels.values():
            panel.panel_closed.connect(self._on_panel_closed)
            panel.panel_moved.connect(self._on_panel_moved)
            panel.panel_resized.connect(self._on_panel_resized)
        
        return panels
    
    def get_panel(self, panel_id: str) -> Optional[TearOffPanel]:
        """Get panel by ID"""
        return self.panels.get(panel_id)
    
    def show_panel(self, panel_id: str):
        """Show a panel (create if needed)"""
        panel = self.panels.get(panel_id)
        if panel:
            if panel.is_torn_off:
                panel.show()
                panel.raise_()
            else:
                panel.setVisible(True)
    
    def hide_panel(self, panel_id: str):
        """Hide a panel"""
        panel = self.panels.get(panel_id)
        if panel:
            panel.setVisible(False)
    
    def tear_off_panel(self, panel_id: str):
        """Tear off a panel"""
        panel = self.panels.get(panel_id)
        if panel and not panel.is_torn_off:
            panel.tear_off_panel()
    
    def dock_panel(self, panel_id: str):
        """Dock a panel"""
        panel = self.panels.get(panel_id)
        if panel and panel.is_torn_off:
            panel.dock_panel()
    
    def _on_panel_closed(self, panel_id: str):
        """Handle panel closed"""
        # For now, just hide it
        self.hide_panel(panel_id)
    
    def _on_panel_moved(self, panel_id: str, position: QPoint):
        """Handle panel moved"""
        self._save_panel_settings()
    
    def _on_panel_resized(self, panel_id: str, size: tuple):
        """Handle panel resized"""
        self._save_panel_settings()
    
    def _load_panel_settings(self):
        """Load panel settings"""
        try:
            if self.panel_settings_path.exists():
                with open(self.panel_settings_path, 'r') as f:
                    self.panel_settings = json.load(f)
            else:
                self.panel_settings = {}
        except Exception as e:
            print(f"Error loading panel settings: {e}")
            self.panel_settings = {}
    
    def _save_panel_settings(self):
        """Save panel settings"""
        try:
            self.panel_settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Collect current panel states
            settings = {}
            for panel_id, panel in self.panels.items():
                settings[panel_id] = {
                    "is_torn_off": panel.is_torn_off,
                    "visible": panel.isVisible(),
                    "geometry": {
                        "x": panel.x(),
                        "y": panel.y(), 
                        "width": panel.width(),
                        "height": panel.height()
                    }
                }
            
            with open(self.panel_settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving panel settings: {e}")
    
    def restore_panel_layout(self):
        """Restore saved panel layout"""
        for panel_id, settings in self.panel_settings.items():
            panel = self.panels.get(panel_id)
            if not panel:
                continue
            
            # Restore visibility
            panel.setVisible(settings.get("visible", True))
            
            # Restore tear-off state
            if settings.get("is_torn_off", False):
                panel.tear_off_panel()
                
                # Restore geometry
                geom = settings.get("geometry", {})
                if geom:
                    panel.setGeometry(
                        geom.get("x", 100),
                        geom.get("y", 100),
                        geom.get("width", 200),
                        geom.get("height", 150)
                    )


# Export main classes
__all__ = [
    'TearOffPanel',
    'ButtonPanel', 
    'FilterSearchPanel',
    'PanelManager'
]
