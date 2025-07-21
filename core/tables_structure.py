#this belongs in core/tables_structure.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - Table Structure Functions
# Table styling and structure management functions using IMG debug system

"""
Table Structure Functions - Table management and styling
Provides table styling reset, structure setup, and management functions
"""

from typing import Optional
from PyQt6.QtWidgets import QTableWidget, QHeaderView
from PyQt6.QtCore import Qt

# Import IMG debug system
from components.img_debug_functions import img_debugger

##Methods list -
# reset_table_styling
# setup_table_for_col_data
# setup_table_for_img_data
# setup_table_structure

def reset_table_styling(main_window): #vers 1
    """Completely reset table styling to default using IMG debug system"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.warning("No table widget available for styling reset")
            return False

        table = main_window.gui_layout.table
        header = table.horizontalHeader()

        # Clear all styling
        table.setStyleSheet("")
        header.setStyleSheet("")
        table.setObjectName("")

        # Reset to basic alternating colors
        table.setAlternatingRowColors(True)

        # Reset selection behavior
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        # Reset header properties
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)

        main_window.log_message("🔧 Table styling completely reset")
        img_debugger.debug("Table styling reset to default")
        return True

    except Exception as e:
        error_msg = f"Error resetting table styling: {str(e)}"
        main_window.log_message(f"⚠️ {error_msg}")
        img_debugger.error(error_msg)
        return False

def setup_table_structure(main_window, file_type: str = "IMG"): #vers 1
    """Setup table structure based on file type using IMG debug system"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("No table widget available for structure setup")
            return False
        
        table = main_window.gui_layout.table
        
        if file_type.upper() == "COL":
            return setup_table_for_col_data(table)
        else:
            return setup_table_for_img_data(table)
        
    except Exception as e:
        img_debugger.error(f"Error setting up table structure: {e}")
        return False

def setup_table_for_img_data(table: QTableWidget) -> bool: #vers 1
    """Setup table structure for IMG file data"""
    try:
        # IMG file columns
        img_headers = ["Name", "Type", "Size", "Offset", "RW Version", "Info"]
        table.setColumnCount(len(img_headers))
        table.setHorizontalHeaderLabels(img_headers)
        
        # Set column widths for IMG data
        table.setColumnWidth(0, 200)  # Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 100)  # Offset
        table.setColumnWidth(4, 120)  # RW Version
        table.setColumnWidth(5, 150)  # Info
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        img_debugger.debug("Table structure setup for IMG data")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error setting up IMG table structure: {e}")
        return False

def setup_table_for_col_data(table: QTableWidget) -> bool: #vers 1
    """Setup table structure for COL file data"""
    try:
        # COL file columns
        col_headers = ["Model Name", "Type", "Version", "Size", "Spheres", "Boxes", "Faces", "Info"]
        table.setColumnCount(len(col_headers))
        table.setHorizontalHeaderLabels(col_headers)
        
        # Set column widths for COL data
        table.setColumnWidth(0, 200)  # Model Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 80)   # Version
        table.setColumnWidth(3, 100)  # Size
        table.setColumnWidth(4, 80)   # Spheres
        table.setColumnWidth(5, 80)   # Boxes
        table.setColumnWidth(6, 80)   # Faces
        table.setColumnWidth(7, 150)  # Info
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        img_debugger.debug("Table structure setup for COL data")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error setting up COL table structure: {e}")
        return False

def apply_table_theme(main_window, theme_name: str = "default"): #vers 1
    """Apply specific theme to table using IMG debug system"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.warning("No table widget available for theme application")
            return False

        table = main_window.gui_layout.table
        
        if theme_name == "dark":
            # Dark theme styling
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    gridline-color: #555555;
                    selection-background-color: #0078d4;
                }
                QTableWidget::item:alternate {
                    background-color: #333333;
                }
                QHeaderView::section {
                    background-color: #404040;
                    color: #ffffff;
                    padding: 4px;
                    border: 1px solid #555555;
                }
            """)
        elif theme_name == "light":
            # Light theme styling
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    gridline-color: #d0d0d0;
                    selection-background-color: #0078d4;
                }
                QTableWidget::item:alternate {
                    background-color: #f5f5f5;
                }
                QHeaderView::section {
                    background-color: #e0e0e0;
                    color: #000000;
                    padding: 4px;
                    border: 1px solid #d0d0d0;
                }
            """)
        else:
            # Default system theme
            reset_table_styling(main_window)
            return True
        
        img_debugger.debug(f"Applied '{theme_name}' theme to table")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error applying table theme: {e}")
        return False

def optimize_table_performance(table: QTableWidget, row_count: int = 0) -> bool: #vers 1
    """Optimize table performance for large datasets"""
    try:
        if row_count > 1000:
            # Disable sorting during population for performance
            table.setSortingEnabled(False)
            
            # Set uniform row heights for performance
            table.setUniformRowHeights(True)
            
            # Reduce update frequency
            table.setUpdatesEnabled(False)
            
            img_debugger.debug(f"Table performance optimized for {row_count} rows")
        else:
            # Enable normal features for smaller datasets
            table.setSortingEnabled(True)
            table.setUniformRowHeights(False)
            table.setUpdatesEnabled(True)
            
            img_debugger.debug(f"Table configured for normal operation ({row_count} rows)")
        
        return True
        
    except Exception as e:
        img_debugger.error(f"Error optimizing table performance: {e}")
        return False

def finalize_table_setup(table: QTableWidget) -> bool: #vers 1
    """Finalize table setup after data population"""
    try:
        # Re-enable updates and sorting
        table.setUpdatesEnabled(True)
        table.setSortingEnabled(True)
        
        # Resize columns to content if reasonable
        if table.rowCount() < 1000:  # Only for smaller datasets
            table.resizeColumnsToContents()
        
        # Ensure first column is visible
        if table.columnCount() > 0:
            table.scrollToItem(table.item(0, 0) if table.rowCount() > 0 else None)
        
        img_debugger.debug("Table setup finalized")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error finalizing table setup: {e}")
        return False