#this belongs in gui/ main_window.py - Version: 55
# X-Seti - July12 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory Main Window - Clean Implementation
Main window setup and layout management
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QApplication, QMenuBar, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

# Import consolidated GUI components
try:
    from .panel_controls import (
        create_right_panel_with_pastel_buttons,
        create_control_panel,
        PanelManager
    )
    from .tear_off import TearOffPanelManager, setup_tear_off_system
    from .log_panel import create_log_panel, setup_logging_for_main_window
    from .status_bar import create_status_bar
except ImportError as e:
    print(f"Import error in main_window: {e}")
    # Fallback - create minimal stubs
    def create_right_panel_with_pastel_buttons(main_window):
        return QWidget()
    def create_control_panel(main_window):
        return QWidget()
    def create_log_panel(main_window):
        return QWidget()
    def create_status_bar(main_window):
        return QStatusBar()
    class PanelManager:
        def __init__(self, main_window): pass
    class TearOffPanelManager:
        def __init__(self, main_window): pass


class IMGFactoryMainWindow(QMainWindow):
    """
    Clean IMG Factory main window implementation
    Handles layout and basic window management
    """
    
    # Signals for communication
    file_opened = pyqtSignal(str)  # file_path
    file_closed = pyqtSignal()
    selection_changed = pyqtSignal(int)  # selection_count
    
    def __init__(self, app_settings=None):
        super().__init__()
        self.app_settings = app_settings
        
        # Initialize core attributes
        self.current_img = None
        self.current_col = None
        self.open_files = {}
        
        # GUI components
        self.gui_layout = None
        self.panel_manager = None
        self.tearoff_manager = None
        self.log_panel = None
        self.status_bar = None
        
        # Setup window
        self._setup_window()
        self._create_layout()
        self._setup_logging()
        self._setup_status_bar()
        
        # Show initial status
        self.show_status("Ready")
        self.log_message("IMG Factory 1.5 initialized")
    
    def _setup_window(self):
        """Setup basic window properties"""
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create menu bar
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """Create basic menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Open action
        open_action = QAction('Open IMG/COL...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        # New action
        new_action = QAction('New IMG...', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.create_new_img)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Close action
        close_action = QAction('Close', self)
        close_action.setShortcut('Ctrl+W')
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Refresh action
        refresh_action = QAction('Refresh', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_table)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_layout(self):
        """Create the main window layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # Create main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - content area (table, log, etc.)
        left_panel = self._create_left_panel()
        
        # Right side - control buttons
        try:
            right_panel = create_right_panel_with_pastel_buttons(self)
        except Exception as e:
            print(f"Error creating right panel: {e}")
            right_panel = QWidget()  # Fallback
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (left panel gets most space)
        main_splitter.setSizes([1000, 280])
        
        # Constrain right panel size
        right_panel.setMaximumWidth(300)
        right_panel.setMinimumWidth(250)
        
        # Add splitter to main layout
        main_layout.addWidget(main_splitter)
        
        # Store references
        self.main_splitter = main_splitter
        self.right_panel = right_panel
        self.left_panel = left_panel
    
    def _create_left_panel(self):
        """Create the left panel with table and log"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        # Create vertical splitter for table and log
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top area - table/content area
        table_area = self._create_table_area()
        
        # Bottom area - log panel
        try:
            log_panel = create_log_panel(self)
            self.log_panel = log_panel
        except Exception as e:
            print(f"Error creating log panel: {e}")
            log_panel = QWidget()  # Fallback
        
        # Add to splitter
        left_splitter.addWidget(table_area)
        left_splitter.addWidget(log_panel)
        
        # Set proportions (table gets most space)
        left_splitter.setSizes([600, 200])
        
        # Add to layout
        left_layout.addWidget(left_splitter)
        
        return left_widget
    
    def _create_table_area(self):
        """Create the main table/content area"""
        # For now, create a simple placeholder
        # This will be replaced with actual table implementation
        from PyQt6.QtWidgets import QLabel
        
        placeholder = QLabel("Main Content Area\n\nTable will be displayed here")
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 20px;
                font-size: 14px;
                color: #666;
            }
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return placeholder
    
    def _setup_logging(self):
        """Setup logging system"""
        try:
            setup_logging_for_main_window(self)
        except Exception as e:
            print(f"Error setting up logging: {e}")
            # Add basic log_message method as fallback
            self._log_messages = []
            
    def _setup_status_bar(self):
        """Setup status bar"""
        try:
            status_bar = create_status_bar(self)
            self.setStatusBar(status_bar)
            self.status_bar = status_bar
        except Exception as e:
            print(f"Error creating status bar: {e}")
            # Fallback to basic status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
    
    def _setup_panel_system(self):
        """Setup panel management system"""
        try:
            # Create panel manager
            self.panel_manager = PanelManager(self)
            
            # Setup tear-off system
            self.tearoff_manager = setup_tear_off_system(self)
            
            self.log_message("✅ Panel system initialized")
            
        except Exception as e:
            print(f"Error setting up panel system: {e}")
            self.log_message(f"⚠️ Panel system error: {str(e)}")
    
    # ========================================================================
    # CORE METHODS - These will be connected to by other components
    # ========================================================================
    
    def log_message(self, message: str):
        """Log a message - fallback implementation"""
        if hasattr(self, '_log_messages'):
            self._log_messages.append(message)
            print(f"LOG: {message}")
        else:
            print(f"LOG: {message}")
    
    def show_status(self, message: str):
        """Show status message"""
        if self.status_bar:
            self.status_bar.showMessage(message)
        else:
            print(f"STATUS: {message}")
    
    def open_img_file(self):
        """Open IMG/COL file - placeholder"""
        self.log_message("🔧 Open IMG File - Not yet implemented")
        self.show_status("Open file functionality not yet implemented")
    
    def create_new_img(self):
        """Create new IMG file - placeholder"""
        self.log_message("🔧 Create New IMG - Not yet implemented")
        self.show_status("Create new IMG functionality not yet implemented")
    
    def close_img_file(self):
        """Close current file - placeholder"""
        self.log_message("🔧 Close IMG File - Not yet implemented")
        self.show_status("Close file functionality not yet implemented")
    
    def refresh_table(self):
        """Refresh table - placeholder"""
        self.log_message("🔄 Refresh Table - Not yet implemented")
        self.show_status("Refresh functionality not yet implemented")
    
    def import_files(self):
        """Import files - placeholder"""
        self.log_message("📥 Import Files - Not yet implemented")
        self.show_status("Import functionality not yet implemented")
    
    def export_selected(self):
        """Export selected entries - placeholder"""
        self.log_message("📤 Export Selected - Not yet implemented")
        self.show_status("Export functionality not yet implemented")
    
    def export_selected_via(self):
        """Export via dialog - placeholder"""
        self.log_message("📋 Export Via - Not yet implemented")
        self.show_status("Export via functionality not yet implemented")
    
    def quick_export_selected(self):
        """Quick export - placeholder"""
        self.log_message("⚡ Quick Export - Not yet implemented")
        self.show_status("Quick export functionality not yet implemented")
    
    def remove_selected(self):
        """Remove selected entries - placeholder"""
        self.log_message("🗑️ Remove Selected - Not yet implemented")
        self.show_status("Remove functionality not yet implemented")
    
    def rebuild_img(self):
        """Rebuild IMG - placeholder"""
        self.log_message("🔨 Rebuild IMG - Not yet implemented")
        self.show_status("Rebuild functionality not yet implemented")
    
    def rebuild_img_as(self):
        """Rebuild IMG as - placeholder"""
        self.log_message("💾 Rebuild IMG As - Not yet implemented")
        self.show_status("Rebuild as functionality not yet implemented")
    
    def validate_img(self):
        """Validate IMG - placeholder"""
        self.log_message("✅ Validate IMG - Not yet implemented")
        self.show_status("Validate functionality not yet implemented")
    
    def show_search_dialog(self):
        """Show search dialog - placeholder"""
        self.log_message("🔍 Search Dialog - Not yet implemented")
        self.show_status("Search functionality not yet implemented")
    
    def show_img_info(self):
        """Show IMG info - placeholder"""
        self.log_message("ℹ️ IMG Info - Not yet implemented")
        self.show_status("Info functionality not yet implemented")
    
    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About IMG Factory 1.5", 
                         "IMG Factory 1.5\n\nA tool for managing IMG archives\n\nCredit: MexUK 2007 Img Factory 1.2\nUpdated by X-Seti 2025")
    
    def merge_img(self):
        """Merge IMG files - placeholder"""
        self.log_message("🔀 Merge IMG - Not yet implemented")
    
    def split_img(self):
        """Split IMG file - placeholder"""
        self.log_message("✂️ Split IMG - Not yet implemented")
    
    def convert_img_format(self):
        """Convert IMG format - placeholder"""
        self.log_message("🔄 Convert IMG Format - Not yet implemented")
    
    def manage_templates(self):
        """Manage templates - placeholder"""
        self.log_message("📋 Manage Templates - Not yet implemented")
    
    def show_quick_start_wizard(self):
        """Show quick start wizard - placeholder"""
        self.log_message("🧙 Quick Start Wizard - Not yet implemented")
    
    # ========================================================================
    # WINDOW EVENTS
    # ========================================================================
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.log_message("Closing IMG Factory...")
        event.accept()
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.log_message(f"Files dropped: {files}")
            # TODO: Handle dropped files
        event.accept()


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_main_window(app_settings=None):
    """Create and return a new main window instance"""
    return IMGFactoryMainWindow(app_settings)


def create_minimal_main_window():
    """Create a minimal main window for testing"""
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    window = IMGFactoryMainWindow()
    return window, app


# ============================================================================
# MAIN ENTRY POINT FOR TESTING
# ============================================================================

if __name__ == "__main__":
    window, app = create_minimal_main_window()
    window.show()
    sys.exit(app.exec())


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'IMGFactoryMainWindow',
    'create_main_window',
    'create_minimal_main_window'
]