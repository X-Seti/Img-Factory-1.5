#this belongs in core/right_click_actions.py - Version: 2
# X-Seti - July21 2025 - Img Factory 1.5 - Table Right-Click Actions - FIXED

"""
Right-Click Actions - Table context menu and clipboard operations
Provides comprehensive right-click functionality for table data copying
FIXED: Works with both real QWidget and DummyMainWindow objects
"""

import os
from typing import Optional, List, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMenu, QTableWidget, QWidget
from PyQt6.QtGui import QAction

##Methods list -
# copy_table_cell
# copy_table_column_data
# copy_table_row
# copy_table_selection
# copy_filename_only
# copy_file_summary
# integrate_right_click_actions
# setup_table_context_menu
# show_table_context_menu

def setup_table_context_menu(main_window): #vers 2
    """Setup right-click context menu for the main table - FIXED"""
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            table.customContextMenuRequested.connect(lambda pos: show_table_context_menu(main_window, pos))
            main_window.log_message("✅ Table right-click context menu enabled")
            return True
        else:
            main_window.log_message("⚠️ Table not available for context menu setup")
            return False
    except Exception as e:
        main_window.log_message(f"❌ Error setting up context menu: {str(e)}")
        return False

def show_table_context_menu(main_window, position): #vers 2
    """Show context menu for table right-click - FIXED for DummyMainWindow"""
    try:
        table = main_window.gui_layout.table
        item = table.itemAt(position)
        
        if not item:
            return

        # FIXED: Choose proper parent for QMenu
        # Check if main_window is a proper QWidget
        menu_parent = table  # Default to table as parent
        if isinstance(main_window, QWidget):
            menu_parent = main_window
        
        # Create context menu with proper parent
        menu = QMenu(menu_parent)
        
        # Get selected data info
        row = item.row()
        col = item.column()
        
        # Get column header name
        header_item = table.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col}"
        
        # Get cell data
        cell_data = item.text() if item else ""
        
        # Copy Cell action
        copy_cell_action = QAction(f"📋 Copy Cell ({column_name})", menu_parent)
        copy_cell_action.triggered.connect(lambda: copy_table_cell(main_window, row, col))
        menu.addAction(copy_cell_action)
        
        # Copy Row action
        copy_row_action = QAction("📄 Copy Row", menu_parent)
        copy_row_action.triggered.connect(lambda: copy_table_row(main_window, row))
        menu.addAction(copy_row_action)
        
        # Copy Column action
        copy_column_action = QAction(f"📊 Copy Column ({column_name})", menu_parent)
        copy_column_action.triggered.connect(lambda: copy_table_column_data(main_window, col))
        menu.addAction(copy_column_action)
        
        menu.addSeparator()
        
        # Copy Selection action
        selected_items = table.selectedItems()
        if len(selected_items) > 1:
            copy_selection_action = QAction(f"🔗 Copy Selection ({len(selected_items)} items)", menu_parent)
            copy_selection_action.triggered.connect(lambda: copy_table_selection(main_window))
            menu.addAction(copy_selection_action)
            menu.addSeparator()
        
        # Copy filename only (for first column)
        if col == 0:
            copy_filename_action = QAction("📁 Copy Filename Only", menu_parent)
            copy_filename_action.triggered.connect(lambda: copy_filename_only(main_window, row))
            menu.addAction(copy_filename_action)
        
        # Copy file summary
        copy_summary_action = QAction("📋 Copy File Summary", menu_parent)
        copy_summary_action.triggered.connect(lambda: copy_file_summary(main_window, row))
        menu.addAction(copy_summary_action)
        
        # Show menu at cursor position
        menu.exec(table.mapToGlobal(position))
        
    except Exception as e:
        main_window.log_message(f"❌ Context menu error: {str(e)}")

def copy_table_cell(main_window, row: int, col: int): #vers 1
    """Copy single table cell to clipboard"""
    try:
        table = main_window.gui_layout.table
        item = table.item(row, col)
        
        if item:
            text = item.text()
            QApplication.clipboard().setText(text)
            
            # Get column name for feedback
            header_item = table.horizontalHeaderItem(col)
            column_name = header_item.text() if header_item else f"Column {col}"
            
            main_window.log_message(f"📋 Copied {column_name}: '{text}'")
        else:
            main_window.log_message("⚠️ No data in selected cell")
            
    except Exception as e:
        main_window.log_message(f"❌ Copy cell error: {str(e)}")

def copy_table_row(main_window, row: int): #vers 1
    """Copy entire table row to clipboard (tab-separated)"""
    try:
        table = main_window.gui_layout.table
        
        # Get all data from row
        row_data = []
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append("")
        
        # Join with tabs
        text = "\t".join(row_data)
        QApplication.clipboard().setText(text)
        
        filename = row_data[0] if row_data else "Unknown"
        main_window.log_message(f"📄 Copied row: {filename}")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy row error: {str(e)}")

def copy_table_column_data(main_window, col: int): #vers 1
    """Copy entire column data to clipboard (newline-separated)"""
    try:
        table = main_window.gui_layout.table
        
        # Get column header
        header_item = table.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col}"
        
        # Get all data from column
        column_data = [column_name]  # Start with header
        for row in range(table.rowCount()):
            item = table.item(row, col)
            if item:
                column_data.append(item.text())
            else:
                column_data.append("")
        
        # Join with newlines
        text = "\n".join(column_data)
        QApplication.clipboard().setText(text)
        
        main_window.log_message(f"📊 Copied column '{column_name}': {table.rowCount()} entries")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy column error: {str(e)}")

def copy_table_selection(main_window): #vers 1
    """Copy selected table items to clipboard"""
    try:
        table = main_window.gui_layout.table
        selected_items = table.selectedItems()
        
        if not selected_items:
            main_window.log_message("⚠️ No items selected")
            return
        
        # Group by rows
        rows_data = {}
        for item in selected_items:
            row = item.row()
            col = item.column()
            if row not in rows_data:
                rows_data[row] = {}
            rows_data[row][col] = item.text()
        
        # Format as table
        lines = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            # Create ordered list of values by column
            ordered_values = []
            for col in sorted(row_data.keys()):
                ordered_values.append(row_data[col])
            lines.append("\t".join(ordered_values))
        
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
        
        main_window.log_message(f"🔗 Copied selection: {len(selected_items)} items from {len(rows_data)} rows")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy selection error: {str(e)}")

def copy_filename_only(main_window, row: int): #vers 1
    """Copy filename without extension from first column"""
    try:
        table = main_window.gui_layout.table
        item = table.item(row, 0)  # First column
        
        if item:
            full_name = item.text()
            # Remove extension
            if '.' in full_name:
                filename_only = '.'.join(full_name.split('.')[:-1])
            else:
                filename_only = full_name
                
            QApplication.clipboard().setText(filename_only)
            main_window.log_message(f"📋 Copied filename: '{filename_only}'")
        else:
            main_window.log_message("⚠️ No filename found")
            
    except Exception as e:
        main_window.log_message(f"❌ Copy filename error: {str(e)}")

def copy_file_summary(main_window, row: int): #vers 1
    """Copy formatted file information summary"""
    try:
        table = main_window.gui_layout.table
        
        # Get all column headers
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
            else:
                headers.append(f"Column_{col}")
        
        # Get row data
        row_data = []
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append("N/A")
        
        # Create formatted summary
        summary_lines = ["=== File Information ==="]
        for i, (header, data) in enumerate(zip(headers, row_data)):
            summary_lines.append(f"{header}: {data}")
        
        text = "\n".join(summary_lines)
        QApplication.clipboard().setText(text)
        
        filename = row_data[0] if row_data else "Unknown"
        main_window.log_message(f"📄 Copied file summary for: {filename}")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy summary error: {str(e)}")

def integrate_right_click_actions(main_window): #vers 2
    """Main integration function - call this from imgfactory.py - FIXED"""
    try:
        success = setup_table_context_menu(main_window)
        if success:
            main_window.log_message("✅ Right-click actions integrated successfully")
            
            # Add convenience method to main window
            main_window.setup_table_right_click = lambda: setup_table_context_menu(main_window)
            
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Right-click integration error: {str(e)}")
        return False

# Export main functions
__all__ = [
    'setup_table_context_menu',
    'show_table_context_menu', 
    'copy_table_cell',
    'copy_table_row',
    'copy_table_column_data',
    'copy_table_selection',
    'copy_filename_only',
    'copy_file_summary',
    'integrate_right_click_actions'
]