#this belongs in components/Img_Factory/img_factory_tab_system.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - Tab System Methods

"""
Tab System Methods
Handles tab creation, switching, tracking, and management
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QTableWidget
from PyQt6.QtCore import Qt

##Methods list -
# _create_initial_tab
# _create_ui
# _find_table_in_tab
# _log_current_tab_state
# _reindex_open_files_robust
# _update_info_bar_for_current_file
# ensure_current_tab_references_valid
# setup_robust_tab_system

def _create_ui(self): #vers 11
    """Create the main user interface - WITH TABS FIXED"""
    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    # Main layout
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(5, 5, 5, 5)

    # Create main tab widget for file handling
    self.main_tab_widget = QTabWidget()
    self.main_tab_widget.setTabsClosable(True)
    self.main_tab_widget.setMovable(True)

    # Initialize open files tracking (for migration)
    if not hasattr(self, 'open_files'):
        self.open_files = {}

    # Create initial empty tab
    self._create_initial_tab()

    # Setup close manager BEFORE tab system
    self.close_manager = install_close_functions(self)

    # Setup NEW tab system
    #setup_tab_system(self)

    # Migrate existing tabs if any
    if self.open_files:
        migrate_tabs(self)

    # Add tab widget to main layout
    main_layout.addWidget(self.main_tab_widget)

    # Create GUI layout system (single instance)
    self.gui_layout.create_status_bar()
    self.gui_layout.apply_table_theme()

    # Setup unified signal system
    self.setup_unified_signals()


def _create_initial_tab(self): #vers 4
    #./components/img_close_functions.py: - def _create_initial_tab[self]
    """Create initial empty tab"""
    # Create tab widget
    tab_widget = QWidget()
    tab_layout = QVBoxLayout(tab_widget)
    tab_layout.setContentsMargins(0, 0, 0, 0)

    # Create GUI layout for this tab
    self.gui_layout.create_main_ui_with_splitters(tab_layout)

    # Add tab with "No file" label
    self.main_tab_widget.addTab(tab_widget, "No File")


def _find_table_in_tab(self, tab_widget): #vers 1
    """Find the table widget in a specific tab - HELPER METHOD"""
    try:
        if not tab_widget:
            return None

        # Method 1: Check for dedicated_table attribute (robust system)
        if hasattr(tab_widget, 'dedicated_table'):
            return tab_widget.dedicated_table

        # Method 2: Search recursively through widget hierarchy
        from PyQt6.QtWidgets import QTableWidget

        def find_table_recursive(widget):
            if isinstance(widget, QTableWidget):
                return widget
            for child in widget.findChildren(QTableWidget):
                return child  # Return first table found
            return None

        table = find_table_recursive(tab_widget)
        if table:
            return table

        # Method 3: Check standard locations
        if hasattr(tab_widget, 'table'):
            return tab_widget.table

        return None

    except Exception as e:
        self.log_message(f"Error finding table in tab: {str(e)}")
        return None


def _log_current_tab_state(self, tab_index): #vers 1
    """Log current tab state for debugging export issues - HELPER METHOD"""
    try:
        # Log file state
        if self.current_img:
            entry_count = len(self.current_img.entries) if self.current_img.entries else 0
            self.log_message(f"State: IMG with {entry_count} entries")
        elif self.current_col:
            if hasattr(self.current_col, 'models'):
                model_count = len(self.current_col.models) if self.current_col.models else 0
                self.log_message(f"State: COL with {model_count} models")
            else:
                self.log_message(f"State: COL file loaded")
        else:
            self.log_message(f"State: No file loaded")

        # Log table state
        if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
            table = self.gui_layout.table
            row_count = table.rowCount() if table else 0
            self.log_message(f"Table: {row_count} rows in gui_layout.table")
        else:
            self.log_message(f"Table: No table reference in gui_layout")

    except Exception as e:
        self.log_message(f"Error logging tab state: {str(e)}")


def ensure_current_tab_references_valid(self): #vers 1
    """Ensure current tab references are valid before export operations - PUBLIC METHOD"""
    try:
        current_index = self.main_tab_widget.currentIndex()
        if current_index == -1:
            return False

        # Force update tab references
        self._on_tab_changed(current_index)

        # Verify we have valid references
        has_valid_file = self.current_img is not None or self.current_col is not None
        has_valid_table = hasattr(self.gui_layout, 'table') and self.gui_layout.table is not None

        if has_valid_file and has_valid_table:
            self.log_message(f"Tab references validated for export operations")
            return True
        else:
            self.log_message(f"Invalid tab references - File: {has_valid_file}, Table: {has_valid_table}")
            return False

    except Exception as e:
        self.log_message(f"Error validating tab references: {str(e)}")
        return False


def _update_info_bar_for_current_file(self): #vers 1
    """Update info bar based on current file type"""
    try:
        if self.current_img:
            # Update for IMG file
            entry_count = len(self.current_img.entries) if self.current_img.entries else 0
            file_path = getattr(self.current_img, 'file_path', 'Unknown')

            if hasattr(self.gui_layout, 'info_label') and self.gui_layout.info_label:
                self.gui_layout.info_label.setText(f"IMG: {os.path.basename(file_path)} | {entry_count} entries")

        elif self.current_col:
            # Update for COL file
            model_count = len(self.current_col.models) if hasattr(self.current_col, 'models') and self.current_col.models else 0
            file_path = getattr(self.current_col, 'file_path', 'Unknown')

            if hasattr(self.gui_layout, 'info_label') and self.gui_layout.info_label:
                self.gui_layout.info_label.setText(f"COL: {os.path.basename(file_path)} | {model_count} models")

    except Exception as e:
        self.log_message(f"Error updating info bar: {str(e)}")


def setup_robust_tab_system(self): #vers 1
    """Setup robust tab system during initialization"""
    try:
        # Import and install robust tab system
        from core.robust_tab_system import install_robust_tab_system

        if install_robust_tab_system(self):
            self.log_message("Robust tab system ready")

            # Run initial integrity check
            if hasattr(self, 'validate_tab_data_integrity'):
                self.validate_tab_data_integrity()

            return True
        else:
            self.log_message("Failed to setup robust tab system")
            return False

    except ImportError:
        self.log_message("⚠Robust tab system not available - using basic system")
        return False
    except Exception as e:
        self.log_message(f"Error setting up robust tab system: {str(e)}")
        return False


__all__ = [
    '_create_ui',
    '_create_initial_tab',
    '_find_table_in_tab',
    '_log_current_tab_state',
    'ensure_current_tab_references_valid',
    '_update_info_bar_for_current_file',
    'setup_robust_tab_system',
    '_reindex_open_files_robust'
]
