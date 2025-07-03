#this belongs in gui/ control_panels.py - version 11
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory Control Panels - Right-side Control Button Panels
Handles the control button sections and action panels
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, 
    QComboBox, QLineEdit, QLabel, QSizePolicy
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


def create_control_panel(main_window):
    """Create the main control panel with all button sections"""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(10)
    
    # IMG Operations section
    img_section = create_img_operations_section(main_window)
    layout.addWidget(img_section)
    
    # Entry Operations section  
    entry_section = create_entry_operations_section(main_window)
    layout.addWidget(entry_section)
    
    # Tools section
    tools_section = create_tools_section(main_window)
    layout.addWidget(tools_section)
    
    # Templates section
    templates_section = create_templates_section(main_window)
    layout.addWidget(templates_section)
    
    # Add stretch to push controls to top
    layout.addStretch()
    
    return panel


def create_img_operations_section(main_window):
    """Create IMG operations button section"""
    group = QGroupBox("IMG Operations")
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
    refresh_btn.setToolTip("Refresh the entry list")
    row2_layout.addWidget(refresh_btn)
    
    rebuild_btn = create_action_button("🔨 Rebuild", "update", main_window, "rebuild_img")
    rebuild_btn.setToolTip("Rebuild the IMG archive")
    row2_layout.addWidget(rebuild_btn)
    
    layout.addLayout(row2_layout)
    
    # Third row - Rebuild As, Merge
    row3_layout = QHBoxLayout()
    
    rebuild_as_btn = create_action_button("💾 Rebuild As", "update", main_window, "rebuild_img_as")
    rebuild_as_btn.setToolTip("Rebuild the IMG archive with a new name")
    row3_layout.addWidget(rebuild_as_btn)
    
    merge_btn = create_action_button("🔗 Merge", "convert", main_window, "merge_img")
    merge_btn.setToolTip("Merge another IMG archive into this one")
    row3_layout.addWidget(merge_btn)
    
    layout.addLayout(row3_layout)
    
    # Fourth row - Split, Convert
    row4_layout = QHBoxLayout()
    
    split_btn = create_action_button("✂️ Split", "convert", main_window, "split_img")
    split_btn.setToolTip("Split the IMG archive into multiple files")
    row4_layout.addWidget(split_btn)
    
    convert_btn = create_action_button("🔄 Convert", "convert", main_window, "convert_img_format")
    convert_btn.setToolTip("Convert IMG to different format/version")
    row4_layout.addWidget(convert_btn)
    
    layout.addLayout(row4_layout)
    
    return group


def create_entry_operations_section(main_window):
    """Create entry operations button section"""
    group = QGroupBox("Entry Operations")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # First row - Import, Import via
    row1_layout = QHBoxLayout()
    
    import_btn = create_action_button("📥 Import", "import", main_window, "import_files")
    import_btn.setToolTip("Import files into the IMG archive")
    row1_layout.addWidget(import_btn)
    
    import_via_btn = create_action_button("📥 Import via", "import", main_window, "import_files_advanced")
    import_via_btn.setToolTip("Import files with advanced options")
    row1_layout.addWidget(import_via_btn)
    
    layout.addLayout(row1_layout)
    
    # Second row - Export, Export via
    row2_layout = QHBoxLayout()
    
    export_btn = create_action_button("📤 Export", "export", main_window, "export_selected_entries")
    export_btn.setToolTip("Export selected entries")
    row2_layout.addWidget(export_btn)
    
    export_via_btn = create_action_button("📤 Export via", "export", main_window, "export_selected_advanced")
    export_via_btn.setToolTip("Export selected entries with advanced options")
    row2_layout.addWidget(export_via_btn)
    
    layout.addLayout(row2_layout)
    
    # Third row - Quick Export, Export All
    row3_layout = QHBoxLayout()
    
    quick_export_btn = create_action_button("⚡ Quick Exp", "export", main_window, "quick_export")
    quick_export_btn.setToolTip("Quick export to default location")
    row3_layout.addWidget(quick_export_btn)
    
    export_all_btn = create_action_button("📤 Export All", "export", main_window, "export_all_entries")
    export_all_btn.setToolTip("Export all entries")
    row3_layout.addWidget(export_all_btn)
    
    layout.addLayout(row3_layout)
    
    # Fourth row - Remove, Remove via
    row4_layout = QHBoxLayout()
    
    remove_btn = create_action_button("🗑️ Remove", "remove", main_window, "remove_selected_entries")
    remove_btn.setToolTip("Remove selected entries")
    row4_layout.addWidget(remove_btn)
    
    remove_via_btn = create_action_button("🗑️ Remove via", "remove", main_window, "remove_entries_advanced")
    remove_via_btn.setToolTip("Remove entries with advanced options")
    row4_layout.addWidget(remove_via_btn)
    
    layout.addLayout(row4_layout)
    
    # Fifth row - Rename, Replace
    row5_layout = QHBoxLayout()
    
    rename_btn = create_action_button("✏️ Rename", "convert", main_window, "rename_entry")
    rename_btn.setToolTip("Rename selected entry")
    row5_layout.addWidget(rename_btn)
    
    replace_btn = create_action_button("↔️ Replace", "convert", main_window, "replace_entry")
    replace_btn.setToolTip("Replace selected entry with new file")
    row5_layout.addWidget(replace_btn)
    
    layout.addLayout(row5_layout)
    
    # Sixth row - Select operations
    row6_layout = QHBoxLayout()
    
    select_all_btn = create_action_button("📋 Select All", None, main_window, "select_all_entries")
    select_all_btn.setToolTip("Select all entries")
    row6_layout.addWidget(select_all_btn)
    
    select_inv_btn = create_action_button("🔄 Select Inv", None, main_window, "invert_selection")
    select_inv_btn.setToolTip("Invert current selection")
    row6_layout.addWidget(select_inv_btn)
    
    layout.addLayout(row6_layout)
    
    return group


def create_tools_section(main_window):
    """Create tools section"""
    group = QGroupBox("Tools")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # First row - Validate, Info
    row1_layout = QHBoxLayout()
    
    validate_btn = create_action_button("✅ Validate", "update", main_window, "validate_img")
    validate_btn.setToolTip("Validate the IMG archive")
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


def create_action_button(text, action_type, main_window, method_name):
    """Create a themed action button"""
    # Try to use main window's themed_button method if available
    if hasattr(main_window, 'themed_button'):
        btn = main_window.themed_button(text, action_type)
    else:
        btn = QPushButton(text)
        if action_type:
            btn.setProperty("action-type", action_type)
    
    # Set size policy
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    btn.setMinimumHeight(28)
    
    return btn


def create_responsive_button_section(title, buttons_data, parent_layout):
    """Create a responsive button section that adapts to width"""
    group = QGroupBox(title)
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # Calculate buttons per row based on available width
    buttons_per_row = 2  # Default for narrow panels
    
    # Create button rows
    current_row = None
    for i, (text, action_type, icon, callback) in enumerate(buttons_data):
        if i % buttons_per_row == 0:
            current_row = QHBoxLayout()
            layout.addLayout(current_row)
        
        btn = QPushButton(text)
        if action_type:
            btn.setProperty("action-type", action_type)
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setMinimumHeight(26)
        
        
        current_row.addWidget(btn)
    
    # Fill last row if needed
    if current_row and (len(buttons_data) % buttons_per_row != 0):
        remaining = buttons_per_row - (len(buttons_data) % buttons_per_row)
        for _ in range(remaining):
            current_row.addStretch()
    
    parent_layout.addWidget(group)
    return group


def create_compact_control_panel(main_window):
    """Create a compact version of the control panel for narrow windows"""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(3, 3, 3, 3)
    layout.setSpacing(5)
    
    # Essential IMG operations
    essential_img_data = [
        ("🆕 New", "import", "document-new", getattr(main_window, 'create_new_img', None)),
        ("📂 Open", "import", "document-open", getattr(main_window, 'open_img_file', None)),
        ("🔨 Rebuild", "update", "document-save", getattr(main_window, 'rebuild_img', None)),
        ("❌ Close", None, "window-close", getattr(main_window, 'close_img_file', None)),
    ]
    
    create_responsive_button_section("IMG", essential_img_data, layout)
    
    # Essential entry operations
    essential_entry_data = [
        ("📥 Import", "import", "edit-copy", getattr(main_window, 'import_files', None)),
        ("📤 Export", "export", "edit-paste", getattr(main_window, 'export_selected_entries', None)),
        ("🗑️ Remove", "remove", "edit-delete", getattr(main_window, 'remove_selected_entries', None)),
        ("🔍 Find", None, "edit-find", getattr(main_window, 'show_search_dialog', None)),
    ]
    
    create_responsive_button_section("Entry", essential_entry_data, layout)
    
    # Add stretch
    layout.addStretch()
    
    return panel


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
        'export_selected_entries', 'remove_selected_entries', 
        'rename_entry', 'replace_entry'
    ]
    
    # Update IMG-dependent buttons
    for attr_name in img_dependent_buttons:
        if hasattr(main_window, attr_name):
            widget = getattr(main_window, attr_name, None)
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(img_loaded)
    
    # Update selection-dependent buttons  
    for attr_name in selection_dependent_buttons:
        if hasattr(main_window, attr_name):
            widget = getattr(main_window, attr_name, None)
            if hasattr(widget, 'setEnabled'):
                widget.setEnabled(img_loaded and entries_selected)


class CollapsibleButtonGroup(QGroupBox):
    """A button group that can be collapsed to save space"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self._on_toggle)
        
        self.content_widget = QWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.content_widget)
        
        self._original_height = None
    
    def _on_toggle(self, checked):
        """Handle collapse/expand toggle"""
        if not checked:
            # Collapsing - store current height
            self._original_height = self.height()
            
        self.content_widget.setVisible(checked)
        
        if checked and self._original_height:
            # Expanding - restore height
            self.resize(self.width(), self._original_height)
    
    def set_content_layout(self, layout):
        """Set the layout for the collapsible content"""
        self.content_widget.setLayout(layout)


def create_collapsible_control_panel(main_window):
    """Create control panel with collapsible sections"""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)
    
    # IMG Operations (collapsible)
    img_group = CollapsibleButtonGroup("IMG Operations")
    img_layout = QVBoxLayout()
    
    # Add IMG operation buttons to collapsible layout
    img_buttons = [
        ("🆕 New", "create_new_img"),
        ("📂 Open", "open_img_file"), 
        ("🔨 Rebuild", "rebuild_img"),
        ("❌ Close", "close_img_file"),
    ]
    
    for text, method in img_buttons:
        btn = create_action_button(text, "import" if "New" in text or "Open" in text else "update", 
                                  main_window, method)
        img_layout.addWidget(btn)
    
    img_group.set_content_layout(img_layout)
    layout.addWidget(img_group)
    
    # Entry Operations (collapsible)
    entry_group = CollapsibleButtonGroup("Entry Operations")
    entry_layout = QVBoxLayout()
    
    entry_buttons = [
        ("📥 Import", "import_files"),
        ("📤 Export", "export_selected_entries"),
        ("🗑️ Remove", "remove_selected_entries"),
    ]
    
    for text, method in entry_buttons:
        action_type = "import" if "Import" in text else "export" if "Export" in text else "remove"
        btn = create_action_button(text, action_type, main_window, method)
        entry_layout.addWidget(btn)
    
    entry_group.set_content_layout(entry_layout)
    layout.addWidget(entry_group)
    
    # Tools (always visible, compact)
    tools_group = QGroupBox("Tools")
    tools_layout = QHBoxLayout(tools_group)
    
    validate_btn = create_action_button("✅", None, main_window, "validate_img")
    validate_btn.setToolTip("Validate")
    validate_btn.setMaximumWidth(40)
    tools_layout.addWidget(validate_btn)
    
    find_btn = create_action_button("🔍", None, main_window, "show_search_dialog")
    find_btn.setToolTip("Find (Ctrl+F)")
    find_btn.setMaximumWidth(40)
    tools_layout.addWidget(find_btn)
    
    info_btn = create_action_button("ℹ️", None, main_window, "show_img_info")
    info_btn.setToolTip("Info")
    info_btn.setMaximumWidth(40)
    tools_layout.addWidget(info_btn)
    
    layout.addWidget(tools_group)
    
    # Add stretch
    layout.addStretch()
    
    return panel


# Canvas display settings for grid and colors
def create_canvas_settings_panel(main_window):
    """Create canvas display settings panel"""
    group = QGroupBox("🎨 Canvas Display")
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    
    # Grid settings
    grid_layout = QHBoxLayout()
    grid_layout.addWidget(QLabel("Grid:"))
    
    grid_combo = QComboBox()
    grid_combo.addItems(["Hidden", "Dotted Line", "Solid Line", "Dashed Line"])
    grid_combo.setCurrentText("Dotted Line")
    if hasattr(main_window, 'on_grid_style_changed'):
        grid_combo.currentTextChanged.connect(main_window.on_grid_style_changed)
    grid_layout.addWidget(grid_combo)
    
    layout.addLayout(grid_layout)
    
    # Color settings
    colors_layout = QVBoxLayout()
    
    # Background color
    bg_layout = QHBoxLayout()
    bg_layout.addWidget(QLabel("Background:"))
    bg_btn = QPushButton("🎨")
    bg_btn.setToolTip("Choose background color")
    bg_btn.setMaximumWidth(40)
    if hasattr(main_window, 'choose_background_color'):

    bg_layout.addWidget(bg_btn)
    bg_layout.addStretch()
    colors_layout.addLayout(bg_layout)
    
    # Grid color
    grid_color_layout = QHBoxLayout()
    grid_color_layout.addWidget(QLabel("Grid:"))
    grid_color_btn = QPushButton("🎨")
    grid_color_btn.setToolTip("Choose grid color")
    grid_color_btn.setMaximumWidth(40)

    grid_color_layout.addWidget(grid_color_btn)
    grid_color_layout.addStretch()
    colors_layout.addLayout(grid_color_layout)
    
    layout.addLayout(colors_layout)
    
    return group


# Utility functions for button management
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


# Integration with responsive button panel system
def integrate_with_responsive_system(main_window, panel):
    """Integrate control panel with existing responsive button system"""
    # Import the existing responsive system if available
    try:
        from .responsive_button_panel import create_responsive_right_panel
        # Use existing system if it exists
        return create_responsive_right_panel(main_window)
    except ImportError:
        # Fall back to our implementation
        return panel
