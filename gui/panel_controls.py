#this belongs in gui/ panel_controls.py - Version: 1
# X-Seti - July12 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory Panel Controls - Consolidated Button Panel System
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


# ============================================================================
# BUTTON DEFINITIONS - Consolidated from buttons.py
# ============================================================================

BUTTON_DEFINITIONS = {
    # IMG Operations
    "open": {"text": "📂 Open", "action_type": "import", "group": "img"},
    "close": {"text": "❌ Close", "action_type": "default", "group": "img"},
    "close_all": {"text": "🗂️ Close All", "action_type": "default", "group": "img"},
    "rebuild": {"text": "🔨 Rebuild", "action_type": "update", "group": "img"},
    "rebuild_as": {"text": "💾 Rebuild As", "action_type": "update", "group": "img"},
    "rebuild_all": {"text": "🔧 Rebuild All", "action_type": "update", "group": "img"},
    "merge": {"text": "🔀 Merge", "action_type": "convert", "group": "img"},
    "split": {"text": "✂️ Split", "action_type": "convert", "group": "img"},
    "convert": {"text": "🔄 Convert", "action_type": "convert", "group": "img"},
    
    # Entry Operations - FIXED: "Refresh" instead of "Update list"
    "import": {"text": "📥 Import", "action_type": "import", "group": "entries"},
    "import_via": {"text": "📁 Import via", "action_type": "import", "group": "entries"},
    "refresh": {"text": "🔄 Refresh", "action_type": "update", "group": "entries"},  # FIXED
    "export": {"text": "📤 Export", "action_type": "export", "group": "entries"},
    "export_via": {"text": "📋 Export via", "action_type": "export", "group": "entries"},
    "quick_export": {"text": "⚡ Quick Export", "action_type": "export", "group": "entries"},
    "remove": {"text": "🗑️ Remove", "action_type": "remove", "group": "entries"},
    "remove_via": {"text": "🚮 Remove via", "action_type": "remove", "group": "entries"},
    "dump": {"text": "📦 Dump", "action_type": "update", "group": "entries"},
    "rename": {"text": "✏️ Rename", "action_type": "default", "group": "entries"},
    "replace": {"text": "🔁 Replace", "action_type": "convert", "group": "entries"},
    
    # Selection Operations
    "select_all": {"text": "☑️ Select All", "action_type": "default", "group": "selection"},
    "select_inverse": {"text": "🔄 Select Inverse", "action_type": "default", "group": "selection"},
    "sort": {"text": "🔢 Sort", "action_type": "default", "group": "selection"},
    
    # Advanced Operations
    "new_img": {"text": "🆕 New", "action_type": "import", "group": "advanced"},
    "validate": {"text": "✅ Validate", "action_type": "update", "group": "advanced"},
    "search": {"text": "🔍 Search", "action_type": "default", "group": "advanced"},
}


# ============================================================================
# MAIN PANEL CREATION FUNCTIONS - From gui_layout.py _create_right_panel_with_pastel_buttons
# ============================================================================

def create_right_panel_with_pastel_buttons(main_window):
    """Create right panel with pastel colored buttons - MATCHES gui_layout.py EXACTLY"""
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(4, 4, 4, 4)
    right_layout.setSpacing(6)

    # IMG Section with pastel colors - MATCHES gui_layout.py
    img_box = QGroupBox("IMG, COL Files")
    img_layout = QGridLayout()
    img_layout.setSpacing(2)
    img_buttons_data = [
        ("New", "new", "document-new", "#EEFAFA", "create_new_img"),
        ("Open", "open", "document-open", "#E3F2FD", "open_img_file"),
        ("Close", "close", "window-close", "#FFF3E0", "close_img_file"),
        ("Close All", "close_all", "edit-clear", "#FFF3E0", "close_all_img"),
        ("Rebuild", "rebuild", "view-refresh", "#E8F5E8", "rebuild_img"),
        ("Rebuild As", "rebuild_as", "document-save-as", "#E8F5E8", "rebuild_img_as"),
        ("Rebuild All", "rebuild_all", "document-save", "#E8F5E8", "rebuild_all_img"),
        ("Merge", "merge", "document-merge", "#F3E5F5", "merge_img"),
        ("Split", "split", "edit-cut", "#F3E5F5", "split_img"),
        ("Convert", "convert", "transform", "#FFF8E1", "convert_img_format"),
    ]
    
    # Create IMG buttons
    for i, (label, action_type, icon, color, method_name) in enumerate(img_buttons_data):
        btn = create_pastel_button(main_window, label, action_type, icon, color, method_name)
        btn.full_text = label
        btn.short_text = get_short_text(label)
        img_layout.addWidget(btn, i // 3, i % 3)
    
    img_box.setLayout(img_layout)
    right_layout.addWidget(img_box)

    # Entries Section with pastel colors - MATCHES gui_layout.py + FIXED "Refresh"
    entries_box = QGroupBox("File Entries")
    entries_layout = QGridLayout()
    entries_layout.setSpacing(2)
    entry_buttons_data = [
        ("Import", "import", "document-import", "#E1F5FE", "import_files"),
        ("Import via", "import_via", "document-import", "#E1F5FE", "import_files_via"),
        ("🔄 Refresh", "update", "view-refresh", "#F9FBE7", "refresh_table"),  # FIXED: Was "Update list"
        ("Export", "export", "document-export", "#E0F2F1", "export_selected"),
        ("Export via", "export_via", "document-export", "#E0F2F1", "export_selected_via"),
        ("Quick Export", "quick_export", "document-export", "#E0F2F1", "quick_export_selected"),
        ("Remove", "remove", "edit-delete", "#FFEBEE", "remove_selected"),
        ("Remove All", "remove_all", "edit-clear", "#FFEBEE", "remove_all_entries"),
        ("Dump", "dump", "document-export", "#E0F2F1", "dump_all_entries"),
        ("Pin selected", "pin", "view-pin", "#FCE4EC", "pin_selected_entries"),
        ("Rename", "rename", "edit", "#FFF8E1", "rename_selected_entry"),
        ("Replace", "replace", "edit-paste", "#FFF8E1", "replace_selected_entry"),
    ]
    
    # Create Entry buttons
    for i, (label, action_type, icon, color, method_name) in enumerate(entry_buttons_data):
        btn = create_pastel_button(main_window, label, action_type, icon, color, method_name)
        btn.full_text = label
        btn.short_text = get_short_text(label)
        entries_layout.addWidget(btn, i // 3, i % 3)
    
    entries_box.setLayout(entries_layout)
    right_layout.addWidget(entries_box)

    # Editing Options Section - EXACT COPY from gui_layout.py
    options_box = QGroupBox("Editing Options")
    options_layout = QGridLayout()
    options_layout.setSpacing(2)
    options_buttons_data = [
        ("Col Edit", "col_edit", "col-edit", "#E3F2FD", "edit_col_file"),
        ("Txd Edit", "txd_edit", "txd-edit", "#F8BBD9", "edit_txd_file"),
        ("Dff Edit", "dff_edit", "dff-edit", "#E1F5FE", "edit_dff_file"),
        ("Ipf Edit", "ipf_edit", "ipf-edit", "#FFF3E0", "edit_ipf_file"),
        ("IDE Edit", "ide_edit", "ide-edit", "#F8BBD9", "edit_ide_file"),
        ("IPL Edit", "ipl_edit", "ipl-edit", "#E1F5FE", "edit_ipl_file"),
        ("Dat Edit", "dat_edit", "dat-edit", "#E3F2FD", "edit_dat_file"),
        ("Zons Cull Ed", "zones_cull", "zones-cull", "#E8F5E8", "edit_zones_cull"),
        ("Weap Edit", "weap_edit", "weap-edit", "#E1F5FE", "edit_weap_file"),
        ("Vehi Edit", "vehi_edit", "vehi-edit", "#E3F2FD", "edit_vehi_file"),
        ("Peds Edit", "peds_edit", "peds-edit", "#F8BBD9", "edit_peds_file"),
        ("Radar Map", "radar_map", "radar-map", "#F8BBD9", "edit_radar_map"),
        ("Paths Map", "paths_map", "paths-map", "#E1F5FE", "edit_paths_map"),
        ("Waterpro", "timecyc", "timecyc", "#E3F2FD", "edit_waterpro"),
        ("Weather", "timecyc", "timecyc", "#E0F2F1", "edit_weather"),
        ("Handling", "handling", "handling", "#E4E3ED", "edit_handling"),
        ("Objects", "ojs_breakble", "ojs-breakble", "#FFE0B2", "edit_objects"),
    ]
    
    # Create Editing Options buttons
    for i, (label, action_type, icon, color, method_name) in enumerate(options_buttons_data):
        btn = create_pastel_button(main_window, label, action_type, icon, color, method_name)
        btn.full_text = label
        btn.short_text = get_short_text(label)
        options_layout.addWidget(btn, i // 3, i % 3)
    
    options_box.setLayout(options_layout)
    right_layout.addWidget(options_box)

    # Filter Section - MATCHES gui_layout.py


    # Add stretch to push everything up
    right_layout.addStretch()

    return right_panel


def create_control_panel(main_window):
    """Create the main control panel - LEGACY FUNCTION"""
    # Use the new right panel function for consistency
    return create_right_panel_with_pastel_buttons(main_window)


def create_img_operations_section(main_window):
    """Create IMG operations button section"""
    group = QGroupBox("📁 IMG Operations")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # First row - New, Open, Close
    row1_layout = QHBoxLayout()
    
    new_btn = create_action_button("🆕 New", "import", main_window, "create_new_img")
    new_btn.setToolTip("Create a new IMG archive")
    row1_layout.addWidget(new_btn)
    
    open_btn = create_action_button("📂 Open", "import", main_window, "open_img_file")
    open_btn.setToolTip("Open an existing IMG archive")
    row1_layout.addWidget(open_btn)
    
    close_btn = create_action_button("❌ Close", None, main_window, "close_img_file")
    close_btn.setToolTip("Close the current IMG archive")
    row1_layout.addWidget(close_btn)
    
    layout.addLayout(row1_layout)
    
    # Second row - Refresh, Rebuild
    row2_layout = QHBoxLayout()
    
    refresh_btn = create_action_button("🔄 Refresh", "update", main_window, "refresh_table")
    refresh_btn.setToolTip("Refresh the entry list")  # FIXED: Uses refresh_table
    row2_layout.addWidget(refresh_btn)
    
    rebuild_btn = create_action_button("🔨 Rebuild", "update", main_window, "rebuild_img")
    rebuild_btn.setToolTip("Rebuild the IMG archive")
    row2_layout.addWidget(rebuild_btn)
    
    layout.addLayout(row2_layout)
    
    return group


def create_entry_operations_section(main_window):
    """Create entry operations button section"""
    group = QGroupBox("📄 Entry Operations")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # First row - Import, Import via
    row1_layout = QHBoxLayout()
    
    import_btn = create_action_button("📥 Import", "import", main_window, "import_files")
    import_btn.setToolTip("Import files into IMG archive")
    row1_layout.addWidget(import_btn)
    
    import_via_btn = create_action_button("📁 Import via", "import", main_window, "import_files_via")
    import_via_btn.setToolTip("Import files with advanced options")
    row1_layout.addWidget(import_via_btn)
    
    layout.addLayout(row1_layout)
    
    # Second row - Export, Export via
    row2_layout = QHBoxLayout()
    
    export_btn = create_action_button("📤 Export", "export", main_window, "export_selected")
    export_btn.setToolTip("Export selected entries")
    row2_layout.addWidget(export_btn)
    
    export_via_btn = create_action_button("📋 Export via", "export", main_window, "export_selected_via")
    export_via_btn.setToolTip("Export with advanced options")
    row2_layout.addWidget(export_via_btn)
    
    layout.addLayout(row2_layout)
    
    # Third row - Quick Export, Remove
    row3_layout = QHBoxLayout()
    
    quick_export_btn = create_action_button("⚡ Quick Export", "export", main_window, "quick_export_selected")
    quick_export_btn.setToolTip("Quick export with default settings")
    row3_layout.addWidget(quick_export_btn)
    
    remove_btn = create_action_button("🗑️ Remove", "remove", main_window, "remove_selected")
    remove_btn.setToolTip("Remove selected entries")
    row3_layout.addWidget(remove_btn)
    
    layout.addLayout(row3_layout)
    
    return group


def create_tools_section(main_window):
    """Create tools section"""
    group = QGroupBox("🔧 Tools")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # First row - Validate, Info
    row1_layout = QHBoxLayout()
    
    validate_btn = create_action_button("✅ Validate", "update", main_window, "validate_img")
    validate_btn.setToolTip("Validate IMG archive integrity")
    row1_layout.addWidget(validate_btn)
    
    info_btn = create_action_button("ℹ️ Info", None, main_window, "show_img_info")
    info_btn.setToolTip("Show IMG archive information")
    row1_layout.addWidget(info_btn)
    
    layout.addLayout(row1_layout)
    
    # Second row - Sort, Find
    row2_layout = QHBoxLayout()
    
    sort_btn = create_action_button("🔢 Sort", None, main_window, "sort_entries")
    sort_btn.setToolTip("Sort entries")
    row2_layout.addWidget(sort_btn)
    
    find_btn = create_action_button("🔍 Find", None, main_window, "show_search_dialog")
    find_btn.setToolTip("Search for entries (Ctrl+F)")
    row2_layout.addWidget(find_btn)
    
    layout.addLayout(row2_layout)
    
    return group


def create_templates_section(main_window):
    """Create templates section"""
    group = QGroupBox("📋 Templates")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # Template manager button
    manager_btn = create_action_button("⚙️ Manage Templates", None, main_window, "manage_templates")
    manager_btn.setToolTip("Open template manager")
    layout.addWidget(manager_btn)
    
    # Quick start wizard button
    wizard_btn = create_action_button("🧙 Quick Start", None, main_window, "show_quick_start_wizard")
    wizard_btn.setToolTip("Open quick start wizard")
    layout.addWidget(wizard_btn)
    
    return group


def create_pastel_button(main_window, label, action_type, icon, bg_color, method_name):
    """Create a button with pastel coloring and connect to method - MATCHES gui_layout.py"""
    btn = QPushButton(label)
    btn.setMaximumHeight(22)
    btn.setMinimumHeight(20)

    # Set icon if provided
    if icon:
        try:
            btn.setIcon(QIcon.fromTheme(icon))
        except:
            pass

    # Apply pastel styling - MATCHES gui_layout.py
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg_color};
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 8pt;
            font-weight: bold;
            color: #333333;
        }}
        QPushButton:hover {{
            background-color: {lighten_color(bg_color, 0.1)};
            border: 1px solid #aaaaaa;
        }}
        QPushButton:pressed {{
            background-color: {darken_color(bg_color, 0.1)};
            border: 1px solid #888888;
        }}
    """)

    # Connect to method if it exists
    if hasattr(main_window, method_name):
        btn.clicked.connect(getattr(main_window, method_name))
    else:
        # Log missing method
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Missing method: {method_name}")
        # Connect to placeholder function
        btn.clicked.connect(lambda: placeholder_function(main_window, method_name))

    return btn


def get_short_text(label):
    """Get short text for button - MATCHES gui_layout.py"""
    short_text_map = {
        "New": "N",
        "Open": "O", 
        "Close": "C",
        "Close All": "CA",
        "Rebuild": "R",
        "Rebuild As": "RA",
        "Rebuild All": "RAL",
        "Merge": "M",
        "Split": "S",
        "Convert": "CV",
        "Import": "I",
        "Import via": "Iv",
        "🔄 Refresh": "Ref",  # FIXED
        "Export": "E",
        "Export via": "Ev",
        "Quick Export": "QE",
        "Remove": "R",
        "Remove All": "RA",
        "Dump": "D",
        "Pin selected": "Pin",
        "Rename": "Ren",
        "Replace": "Rep",
        # Editing Options - EXACT from gui_layout.py
        "Col Edit": "Col",
        "Txd Edit": "Txd",
        "Dff Edit": "Dff",
        "Ipf Edit": "Ipf",
        "IDE Edit": "IDE",
        "IPL Edit": "IPL",
        "Dat Edit": "Dat",
        "Zons Cull Ed": "ZC",
        "Weap Edit": "Weap",
        "Vehi Edit": "Vehi",
        "Peds Edit": "Peds",
        "Radar Map": "RM",
        "Paths Map": "PM",
        "Waterpro": "WP",
        "Weather": "WE",
        "Handling": "HN",
        "Objects": "OB",
    }
    return short_text_map.get(label, label[:3])


def lighten_color(color, factor):
    """Lighten a hex color by factor"""
    try:
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except:
        return color


def darken_color(color, factor):
    """Darken a hex color by factor"""
    try:
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except:
        return color


def placeholder_function(main_window, method_name):
    """Placeholder function for missing methods"""
    if hasattr(main_window, 'log_message'):
        main_window.log_message(f"🚧 {method_name} - Not yet implemented")
    else:
        print(f"🚧 {method_name} - Not yet implemented")


# BUTTON PANEL WITH PRESET MANAGEMENT - From panels.py

class ButtonPanel(QWidget):
    """Panel containing configurable buttons"""
    
    def __init__(self, panel_id: str, title: str, callbacks: Dict[str, Callable] = None, parent=None):
        super().__init__(parent)
        self.panel_id = panel_id
        self.title = title
        self.callbacks = callbacks or {}
        self.buttons: Dict[str, QPushButton] = {}
        
        # Setup layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(3)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        self.main_layout.addWidget(self.title_label)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_widget)
        
        # Apply default buttons based on panel type
        self._create_default_buttons()
    
    def _create_default_buttons(self):
        """Create default buttons based on panel ID"""
        if self.panel_id == "img_ops":
            self._create_img_buttons()
        elif self.panel_id == "entries_ops":
            self._create_entry_buttons()
        elif self.panel_id == "tools":
            self._create_tool_buttons()
    
    def _create_img_buttons(self):
        """Create IMG operation buttons"""
        layout = QGridLayout()
        layout.setSpacing(2)
        
        img_buttons = [
            ("New", "create_new_img"),
            ("Open", "open_img_file"),
            ("Close", "close_img_file"),
            ("Rebuild", "rebuild_img"),
            ("Rebuild As", "rebuild_img_as"),
            ("Merge", "merge_img"),
        ]
        
        for i, (text, method_name) in enumerate(img_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(24)
            if hasattr(self.parent(), method_name):
                btn.clicked.connect(getattr(self.parent(), method_name))
            self.buttons[method_name] = btn
            layout.addWidget(btn, i // 3, i % 3)
        
        self.content_layout.addLayout(layout)
    
    def _create_entry_buttons(self):
        """Create entry operation buttons"""
        layout = QGridLayout()
        layout.setSpacing(2)
        
        entry_buttons = [
            ("Import", "import_files"),
            ("Export", "export_selected"),
            ("Remove", "remove_selected"),
            ("🔄 Refresh", "refresh_table"),  # FIXED
            ("Quick Export", "quick_export_selected"),
            ("Dump", "dump_all_entries"),
        ]
        
        for i, (text, method_name) in enumerate(entry_buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(24)
            if hasattr(self.parent(), method_name):
                btn.clicked.connect(getattr(self.parent(), method_name))
            self.buttons[method_name] = btn
            layout.addWidget(btn, i // 3, i % 3)
        
        self.content_layout.addLayout(layout)
    
    def _create_tool_buttons(self):
        """Create tool buttons"""
        layout = QVBoxLayout()
        layout.setSpacing(2)
        
        tool_buttons = [
            ("🔍 Search", "show_search_dialog"),
            ("✅ Validate", "validate_img"),
            ("ℹ️ Info", "show_img_info"),
            ("🔢 Sort", "sort_entries"),
        ]
        
        for text, method_name in tool_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(24)
            if hasattr(self.parent(), method_name):
                btn.clicked.connect(getattr(self.parent(), method_name))
            self.buttons[method_name] = btn
            layout.addWidget(btn)
        
        self.content_layout.addLayout(layout)
    
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


# ADVANCED BUTTON CLASSES - From gui/buttons.py

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
    'BUTTON_DEFINITIONS',
    
    # Main panel functions (gui_layout.py compatible)
    'create_right_panel_with_pastel_buttons',  # MAIN FUNCTION
    'create_control_panel',  # Legacy compatibility
    
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
