#!/usr/bin/env python3
"""
X-Seti - June05, 2023 - button panel with responsive layout and tooltips
"""

#This goes in gui/ button_panel.py - version 4

from PyQt6.QtWidgets import (QGroupBox, QGridLayout, QPushButton, QVBoxLayout, ScrollArea, QWidget, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class ResponsiveButtonPanel(QWidget):
    """Button panel that adapts to width changes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons_data = []
        self.button_widgets = []
        self.current_columns = 3
        
    def create_responsive_button_section(self, title, buttons_data, parent_layout):
        """Create a responsive button section that adapts to width"""
        
        # Store button data for recreation
        section_data = {
            'title': title,
            'buttons': buttons_data,
            'group_box': None,
            'layout': None
        }
        
        # Create group box
        group_box = QGroupBox(title)
        layout = QGridLayout()
        layout.setSpacing(4)  # Tighter spacing
        
        # Create buttons with adaptive sizing
        buttons = []
        for i, (label, action_type, icon, callback) in enumerate(buttons_data):
            btn = QPushButton()
            
            # Set properties
            if action_type:
                btn.setProperty("action-type", action_type)
            if icon:
                btn.setIcon(QIcon.fromTheme(icon))
            
            # Adaptive text handling
            self._setup_adaptive_button(btn, label, callback)
            buttons.append(btn)
            
            # Add to layout
            row, col = divmod(i, self.current_columns)
            layout.addWidget(btn, row, col)
        
        section_data['group_box'] = group_box
        section_data['layout'] = layout
        section_data['buttons'] = buttons
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)
        
        return section_data
    
    def _setup_adaptive_button(self, button, full_text, callback):
        """Setup button with adaptive text and tooltip"""
        button.full_text = full_text
        button.short_text = self._create_short_text(full_text)
        
        # Set initial text
        button.setText(full_text)
        button.setToolTip(f"{full_text}")
        
        # Set size policy
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setMinimumHeight(28)
        
        # Connect callback
        
        # Store reference
        self.button_widgets.append(button)
    
    def _create_short_text(self, full_text):
        """Create shortened version of button text"""
        # Create abbreviations for common terms
        abbreviations = {
            'Import': 'Imp',
            'Export': 'Exp', 
            'Remove': 'Rem',
            'Update': 'Upd',
            'Convert': 'Conv',
            'Rebuild': 'Rbld',
            'Quick Exp': 'QExp',
            'Import via': 'Imp>',
            'Export via': 'Exp>',
            'Remove via': 'Rem>',
            'Update lst': 'Upd',
            'Select All': 'All',
            'Select Inv': 'Inv',
            'Rebuild As': 'RbAs',
            'Rebuild All': 'RbAll'
        }
        
        return abbreviations.get(full_text, full_text[:4])
    
    def resizeEvent(self, event):
        """Handle resize events to adapt button layout"""
        super().resizeEvent(event)
        self._adapt_to_width(event.size().width())
    
    def _adapt_to_width(self, width):
        """Adapt button display based on available width"""
        if not self.button_widgets:
            return
            
        # Determine display mode based on width
        if width > 280:
            # Full text mode
            for button in self.button_widgets:
                button.setText(button.full_text)
        elif width > 200:
            # Medium text mode - remove some words
            for button in self.button_widgets:
                text = button.full_text
                if len(text) > 8:
                    # Remove common words
                    text = text.replace(' via', '>')
                    text = text.replace(' lst', '')
                    text = text.replace(' All', '')
                button.setText(text)
        elif width > 150:
            # Short text mode
            for button in self.button_widgets:
                button.setText(button.short_text)
        else:
            # Icon only mode
            for button in self.button_widgets:
                button.setText("")
                # Ensure tooltip is visible
                if not button.toolTip():
                    button.setToolTip(button.full_text)


def create_enhanced_right_panel(parent):
    """Create enhanced right panel with responsive buttons"""
    
    # Container widget for the right panel
    right_widget = QWidget()
    right_widget.setMinimumWidth(150)  # Reduced from 250
    right_layout = QVBoxLayout(right_widget)
    
    # Create responsive panel
    responsive_panel = ResponsiveButtonPanel()
    
    # IMG Operations with enhanced layout
    img_buttons_data = [
        ("Open IMG/COL", "import", "document-open", parent.open_img_file),
        ("Refresh", "update", "view-refresh", parent.refresh_table),
        ("Close", None, "window-close", parent.close_img_file),
        ("Rebuild", "update", "document-save", parent.rebuild_img),
        ("Rebuild As", None, "document-save-as", None),
        ("Rebuild All", None, "document-save", None),
        ("Merge", None, "document-merge", None),
        ("Split", None, "edit-cut", None),
        ("Convert", "convert", "transform", None),
    ]
    
    img_section = responsive_panel.create_responsive_button_section(
        "IMG Operations", img_buttons_data, right_layout
    )
    
    # Entry Operations
    entry_buttons_data = [
        ("Import", "import", "edit-copy", parent.import_files),
        ("Import via", "import", None, None),
        ("Update lst", "update", None, parent.refresh_table),
        ("Export", "export", None, parent.export_selected_entries),
        ("Export via", "export", None, None),
        ("Quick Exp", "export", None, None),
        ("Remove", "remove", "edit-delete", parent.remove_selected_entries),
        ("Remove via", "remove", None, None),
        ("Dump", "update", None, None),
        ("Rename", "convert", None, None),
        ("Replace", "convert", None, None),
        ("Select All", None, None, None),
        ("Select Inv", None, None, None),
        ("Sort", None, None, None)
    ]
    
    entry_section = responsive_panel.create_responsive_button_section(
        "Entry Operations", entry_buttons_data, right_layout
    )
    
    # Filter/Search Panel (unchanged but enhanced)
    from PyQt6.QtWidgets import QComboBox, QLineEdit, QHBoxLayout
    
    filter_box = QGroupBox("Filter & Search")
    filter_layout = QVBoxLayout()  # Changed to vertical for narrow panels
    
    # Filter combo
    parent.filter_combo = QComboBox()
    parent.filter_combo.addItems(["All Files", "Models (DFF)", "Textures (TXD)", 
                                 "Collision (COL)", "Animation (IFP)", "Audio (WAV)", "Scripts (SCM)"])

    filter_layout.addWidget(parent.filter_combo)
    
    # Search box with button
    search_layout = QHBoxLayout()
    parent.filter_input = QLineEdit()
    parent.filter_input.setPlaceholderText("Search...")

    search_layout.addWidget(parent.filter_input)
    
    filter_btn = QPushButton("🔍")
    filter_btn.setIcon(QIcon.fromTheme("edit-find"))
    filter_btn.setMaximumWidth(30)
    filter_btn.setToolTip("Apply search filter")
    search_layout.addWidget(filter_btn)
    
    filter_layout.addLayout(search_layout)
    filter_box.setLayout(filter_layout)
    right_layout.addWidget(filter_box)
    
    # Add stretch to push controls to top
    right_layout.addStretch()
    
    return right_widget


# Alternative approach: Collapsible sections for very narrow panels
class CollapsibleButtonGroup(QGroupBox):
    """Button group that can collapse when space is limited"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.is_collapsed = False
        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.content_widget)
        
        # Make title clickable
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self.toggle_collapse)
    
    def toggle_collapse(self, checked):
        """Toggle the collapsed state"""
        self.content_widget.setVisible(checked)
        self.is_collapsed = not checked
    
    def set_content_layout(self, layout):
        """Set the layout for the content widget"""
        self.content_widget.setLayout(layout)


# Enhanced button creation with better theming
def create_themed_button(label, action_type=None, icon=None, bold=False, parent=None):
    """Create a properly themed button with enhanced features"""
    btn = QPushButton(label)
    
    if action_type:
        btn.setProperty("action-type", action_type)
    
    if icon:
        btn.setIcon(QIcon.fromTheme(icon))
    
    if bold:
        font = btn.font()
        font.setBold(True)
        btn.setFont(font)
    
    # Enhanced size policy
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    btn.setMinimumHeight(26)
    
    # Better tooltip
    if label and not btn.toolTip():
        btn.setToolTip(f"{label}")
    
    return btn
