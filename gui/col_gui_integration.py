#!/usr/bin/env python3
"""
#this belongs in gui/col_gui_components.py - version 11
X-Seti - June27 2025 - COL GUI Components for Img Factory 1.5
GUI buttons, menus, and styling for COL functionality integration
"""

from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QMenu, QAction, QMenuBar, QMessageBox, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont

class COLActionButton(QPushButton):
    """Specialized button for COL operations with proper theming"""
    
    def __init__(self, text: str, action_type: str = "update", parent=None):
        super().__init__(text, parent)
        
        # Set action type for theme styling
        self.setProperty("action-type", action_type)
        
        # Set COL-specific styling
        self.setMinimumHeight(32)
        self.setMinimumWidth(120)
        
        # Make it bold and prominent
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        
        # Add COL-specific tooltip
        self.setToolTip(f"COL Operation: {text}")

class COLEditorButton(COLActionButton):
    """Main COL Editor button"""
    
    col_editor_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("🔧 COL Editor", "update", parent)
        self.setToolTip("Open COL Editor\nEdit collision files with full 3D visualization")
        
        # Connect to signal
        self.clicked.connect(self.col_editor_requested.emit)
        
        # Make it extra prominent
        self.setMinimumHeight(40)
        self.setMinimumWidth(140)
        
        # Set font size larger
        font = self.font()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)

class COLToolsButtonGroup(QWidget):
    """Group of COL tool buttons"""
    
    col_editor_requested = pyqtSignal()
    col_batch_requested = pyqtSignal()
    col_analyzer_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the button group UI"""
        layout = QVBoxLayout(self)
        
        # COL Tools group
        col_group = QGroupBox("🔧 COL Tools")
        col_layout = QVBoxLayout(col_group)
        
        # Main COL Editor button
        self.col_editor_btn = COLEditorButton()
        col_layout.addWidget(self.col_editor_btn)
        
        # Secondary tools in horizontal layout
        tools_layout = QHBoxLayout()
        
        self.batch_btn = COLActionButton("⚙️ Batch", "convert")
        self.batch_btn.setToolTip("COL Batch Processor\nProcess multiple COL files at once")
        tools_layout.addWidget(self.batch_btn)
        
        self.analyzer_btn = COLActionButton("📊 Analyze", "import")
        self.analyzer_btn.setToolTip("COL Analyzer\nAnalyze COL file structure and quality")
        tools_layout.addWidget(self.analyzer_btn)
        
        col_layout.addLayout(tools_layout)
        
        layout.addWidget(col_group)
    

def integrate_col_gui_into_imgfactory(img_factory_window):
    """
    Integrate COL GUI components into the main IMG Factory window
    """
    try:
        # Add COL menu to menubar
        if hasattr(img_factory_window, 'menuBar'):
            col_menu = COLMenuBuilder.add_col_menu_to_menubar(
                img_factory_window.menuBar(), 
                img_factory_window
            )
            
            # Store reference
            img_factory_window.col_menu = col_menu
        
        # Add COL tools to right panel if it exists
        if hasattr(img_factory_window, '_create_right_panel') or hasattr(img_factory_window, 'right_panel'):
            # Try to add COL tools group to existing right panel
            try:
                # Find the right panel widget
                right_panel = None
                if hasattr(img_factory_window, 'right_panel'):
                    right_panel = img_factory_window.right_panel
                elif hasattr(img_factory_window, 'main_splitter'):
                    # Look for right panel in splitter
                    for i in range(img_factory_window.main_splitter.count()):
                        widget = img_factory_window.main_splitter.widget(i)
                        if widget and i == img_factory_window.main_splitter.count() - 1:  # Last widget
                            right_panel = widget
                            break
                
                if right_panel and hasattr(right_panel, 'layout'):
                    # Create COL tools group
                    col_tools = COLToolsButtonGroup()
                    
                    # Connect signals to main window methods
                    col_tools.col_editor_requested.connect(lambda: COLMenuBuilder._open_col_editor(img_factory_window))
                    col_tools.col_batch_requested.connect(lambda: COLMenuBuilder._open_batch_processor(img_factory_window))
                    col_tools.col_analyzer_requested.connect(lambda: COLMenuBuilder._analyze_col(img_factory_window))
                    
                    # Insert before the stretch (usually last item)
                    layout = right_panel.layout()
                    if layout:
                        # Find stretch item and insert before it
                        count = layout.count()
                        if count > 0:
                            last_item = layout.itemAt(count - 1)
                            if hasattr(last_item, 'spacerItem') and last_item.spacerItem():
                                # Insert before stretch
                                layout.insertWidget(count - 1, col_tools)
                            else:
                                # Just add at the end
                                layout.addWidget(col_tools)
                        else:
                            layout.addWidget(col_tools)
                    
                    # Store reference
                    img_factory_window.col_tools = col_tools
                    
            except Exception as e:
                print(f"Failed to add COL tools to right panel: {e}")
        
        # Add COL status indicator to status bar
        if hasattr(img_factory_window, 'statusBar'):
            col_status = COLStatusIndicator()
            img_factory_window.statusBar().addPermanentWidget(col_status)
            img_factory_window.col_status = col_status
        
        # Log success
        if hasattr(img_factory_window, 'log_message'):
            img_factory_window.log_message("COL GUI components integrated successfully")
        
        return True
        
    except Exception as e:
        print(f"Error integrating COL GUI: {e}")
        if hasattr(img_factory_window, 'log_message'):
            img_factory_window.log_message(f"COL GUI integration error: {str(e)}")
        return False

# Convenience function for easy integration
def setup_col_gui(img_factory_window):
    """
    Easy setup function for COL GUI integration
    Call this from your main IMG Factory window after UI creation
    """
    return integrate_col_gui_into_imgfactory(img_factory_window)
