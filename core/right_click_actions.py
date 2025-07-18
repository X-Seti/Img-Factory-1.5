#this belongs in core/right_click_actions.py - Version: 1
# X-Seti - July18 2025 - Img Factory 1.5 - Table Right-Click Actions

"""
Right-Click Actions - Table context menu and clipboard operations
Provides comprehensive right-click functionality for table data copying
"""

import os
from typing import Optional, List, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMenu, QTableWidget
from PyQt6.QtGui import QAction

##Methods list -
# copy_table_cell
# copy_table_column_data
# copy_table_row
# copy_table_selection
# setup_table_context_menu
# show_table_context_menu

def setup_table_context_menu(main_window): #vers 1
    """Setup right-click context menu for the main table"""
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

def show_table_context_menu(main_window, position): #vers 1
    """Show context menu for table right-click"""
    try:
        table = main_window.gui_layout.table
        item = table.itemAt(position)
        
        if not item:
            return

        # Create context menu
        menu = QMenu(main_window)
        
        # Get selected data info
        row = item.row()
        col = item.column()
        
        # Get column header name
        header_item = table.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column_{col}"
        
        # Copy single cell
        copy_cell_action = QAction("📋 Copy Cell Value", main_window)
        copy_cell_action.triggered.connect(lambda: copy_table_cell(main_window, row, col))
        menu.addAction(copy_cell_action)
        
        # Copy entire row
        copy_row_action = QAction("📋 Copy Entire Row", main_window)
        copy_row_action.triggered.connect(lambda: copy_table_row(main_window, row))
        menu.addAction(copy_row_action)
        
        menu.addSeparator()
        
        # Copy column header + data
        copy_with_header_action = QAction(f"📋 Copy '{column_name}' Value", main_window)
        copy_with_header_action.triggered.connect(lambda: copy_table_column_data(main_window, row, col))
        menu.addAction(copy_with_header_action)
        
        # Copy selection if multiple cells selected
        selected_ranges = table.selectedRanges()
        if selected_ranges and len(selected_ranges) > 0:
            menu.addSeparator()
            copy_selection_action = QAction("📋 Copy Selection", main_window)
            copy_selection_action.triggered.connect(lambda: copy_table_selection(main_window))
            menu.addAction(copy_selection_action)
        
        # Additional useful actions
        menu.addSeparator()
        
        # Copy filename only (for first column)
        if col == 0:  # Name column
            copy_filename_action = QAction("📋 Copy Filename Only", main_window)
            copy_filename_action.triggered.connect(lambda: copy_filename_only(main_window, row))
            menu.addAction(copy_filename_action)
        
        # Copy file info summary
        copy_summary_action = QAction("📄 Copy File Info Summary", main_window)
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
            main_window.log_message(f"📋 Copied cell: '{text}'")
        else:
            main_window.log_message("⚠️ No data in selected cell")
    except Exception as e:
        main_window.log_message(f"❌ Copy cell error: {str(e)}")

def copy_table_row(main_window, row: int): #vers 1
    """Copy entire table row to clipboard (tab-separated)"""
    try:
        table = main_window.gui_layout.table
        row_data = []
        
        # Get all column data for the row
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append("")
        
        # Tab-separated for easy pasting into spreadsheets
        text = "\t".join(row_data)
        QApplication.clipboard().setText(text)
        
        # Show filename in log message
        filename = row_data[0] if row_data else "Unknown"
        main_window.log_message(f"📋 Copied row for: {filename}")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy row error: {str(e)}")

def copy_table_column_data(main_window, row: int, col: int): #vers 1
    """Copy column header + data to clipboard"""
    try:
        table = main_window.gui_layout.table
        
        # Get header name
        header_item = table.horizontalHeaderItem(col)
        header = header_item.text() if header_item else f"Column_{col}"
        
        # Get cell data
        item = table.item(row, col)
        data = item.text() if item else ""
        
        # Format as "Header: Value"
        text = f"{header}: {data}"
        QApplication.clipboard().setText(text)
        main_window.log_message(f"📋 Copied: {text}")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy column data error: {str(e)}")

def copy_table_selection(main_window): #vers 1
    """Copy selected table cells to clipboard"""
    try:
        table = main_window.gui_layout.table
        selected_ranges = table.selectedRanges()
        
        if not selected_ranges:
            main_window.log_message("⚠️ No cells selected")
            return
            
        # Get all selected text
        all_text = []
        
        for selection_range in selected_ranges:
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                row_data = []
                for col in range(selection_range.leftColumn(), selection_range.rightColumn() + 1):
                    item = table.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                all_text.append("\t".join(row_data))
        
        # Join rows with newlines
        text = "\n".join(all_text)
        QApplication.clipboard().setText(text)
        main_window.log_message(f"📋 Copied {len(all_text)} rows to clipboard")
        
    except Exception as e:
        main_window.log_message(f"❌ Copy selection error: {str(e)}")

def copy_filename_only(main_window, row: int): #vers 1
    """Copy just the filename without extension"""
    try:
        table = main_window.gui_layout.table
        item = table.item(row, 0)  # Name column
        
        if item:
            full_name = item.text()
            # Remove extension if present
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

def integrate_right_click_actions(main_window): #vers 1
    """Main integration function - call this from imgfactory.py"""
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