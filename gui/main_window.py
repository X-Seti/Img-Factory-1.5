#this belongs in gui/ main_window.py - version 54
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory Main Window - GUI Layout Management
Main window setup and layout orchestration
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QButtonGroup
)
from PyQt6.QtCore import Qt

# Import our GUI modules
from .status_bar import create_status_bar
from .control_panels import create_control_panel
from .log_panel import create_log_panel


class IMGFactoryMainWindow(QMainWindow):
    """
    Main IMG Factory window - handles layout and orchestration only
    Business logic is handled by separate components
    """
    
    def __init__(self, app_settings=None):
        super().__init__()
        self.app_settings = app_settings
        
        # Initialize window properties
        self._setup_window()
        
        # Create UI components
        self._create_main_layout()
        
        # Setup menu and status bars
        self._setup_menu_and_status()
    
    def _setup_window(self):
        """Setup basic window properties"""
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def _create_main_layout(self):
        """Create the main window layout with splitters"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main horizontal splitter (content | controls)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - IMG content and log
        left_panel = self._create_left_panel()
        self.main_splitter.addWidget(left_panel)
        
        # Right panel - Control buttons
        right_panel = create_control_panel(self)
        self.main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (70% left, 30% right)
        self.main_splitter.setSizes([840, 360])
        
        # Configure splitter
        self._style_splitter()
        
        main_layout.addWidget(self.main_splitter)
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with IMG content"""
        # Container widget
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vertical splitter for table and log
        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Entries table panel (includes IMG file info)
        table_panel = create_entries_table_panel(self)
        self.content_splitter.addWidget(table_panel)
        
        # Log panel
        log_panel = create_log_panel(self)
        self.content_splitter.addWidget(log_panel)
        
        # Set proportions (75% table, 25% log)
        self.content_splitter.setSizes([600, 200])
        
        left_layout.addWidget(self.content_splitter)
        
        return left_container
    
    def _style_splitter(self):
        """Apply styling to splitters"""
        # Get current theme colors for splitter styling
        if hasattr(self, 'app_settings') and self.app_settings:
            colors = self.app_settings.get_theme_colors()
            bg_color = colors.get('bg_secondary', '#f8f9fa')
            border_color = colors.get('border', '#dee2e6')
            hover_color = colors.get('bg_tertiary', '#e9ecef')
            pressed_color = colors.get('accent_primary', '#1976d2')
        else:
            # Fallback colors for light theme
            bg_color = '#f8f9fa'
            border_color = '#dee2e6'
            hover_color = '#e9ecef'
            pressed_color = '#1976d2'
        
        splitter_style = f"""
            QSplitter::handle {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                width: 6px;
                margin: 2px;
                border-radius: 3px;
            }}
            
            QSplitter::handle:hover {{
                background-color: {hover_color};
                border-color: {pressed_color};
            }}
            
            QSplitter::handle:pressed {{
                background-color: {pressed_color};
                border-color: {pressed_color};
            }}
        """
        
        self.main_splitter.setStyleSheet(splitter_style)
        self.content_splitter.setStyleSheet(splitter_style)
        
        # Prevent panels from collapsing completely
        self.main_splitter.setChildrenCollapsible(False)
        self.content_splitter.setChildrenCollapsible(False)
    
    def _setup_menu_and_status(self):
        """Setup menu bar and status bar"""
        # Create menu bar
        create_menu_bar(self)
        
        # Create status bar
        create_status_bar(self)
    
    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Create themed button - bridge method for compatibility"""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QIcon
        
        btn = QPushButton(label)
        
        if action_type:
            btn.setProperty("action-type", action_type)
        
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        
        if bold:
            font = btn.font()
            font.setBold(True)
            btn.setFont(font)
        
        return btn
    
    # Drag and drop support
    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop events"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        img_files = [f for f in files if f.lower().endswith('.img')]
        
        if img_files:
            # Signal to load the first IMG file
            if hasattr(self, 'load_img_file'):
                self.load_img_file(img_files[0])
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state if settings available
        if self.app_settings and hasattr(self.app_settings, 'save_window_state'):
            self.app_settings.save_window_state(self)
        
        # Accept the close event
        event.accept()


# Factory function for backward compatibility
def create_main_window(app_settings=None):
    """Create and return main window instance"""
    return IMGFactoryMainWindow(app_settings)
