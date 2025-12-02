#this belongs in core/right_click_actions.py - Version: 4
# X-Seti - August07 2025 - IMG Factory 1.5 - Complete Right-Click Actions
# Combined: Basic copying + Advanced file operations + Extraction functionality

"""
Complete Right-Click Actions - Unified context menu system
Combines basic clipboard operations with advanced file-specific actions
"""

import os
import tempfile
from typing import Optional, List, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMenu, QTableWidget, QWidget, QMessageBox
from PyQt6.QtGui import QAction

##Methods list -
# analyze_col_from_table
# copy_file_summary
# copy_filename_only
# copy_table_cell
# copy_table_column_data
# copy_table_row
# copy_table_selection
# edit_col_from_table
# edit_ide_file
# get_selected_entries_for_extraction
# integrate_right_click_actions
# setup_table_context_menu
# show_advanced_context_menu
# show_dff_info
# view_ide_definitions
# view_txd_textures

def setup_table_context_menu(main_window): #vers 3
    """Setup comprehensive right-click context menu for the main table"""
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            table.customContextMenuRequested.connect(lambda pos: show_advanced_context_menu(main_window, pos))
            main_window.log_message("Advanced table right-click context menu enabled")
            return True
        else:
            main_window.log_message("Table not available for context menu setup")
            return False
    except Exception as e:
        main_window.log_message(f"Error setting up context menu: {str(e)}")
        return False

def show_advanced_context_menu(main_window, position): #vers 3
    """Show comprehensive context menu with file-type specific actions"""
    try:
        table = main_window.gui_layout.table
        item = table.itemAt(position)

        if not item:
            return

        # Choose proper parent for QMenu
        menu_parent = table
        if isinstance(main_window, QWidget):
            menu_parent = main_window

        # Create context menu
        menu = QMenu(menu_parent)

        # Get selected data info
        row = item.row()
        col = item.column()

        # Get column header and cell data
        header_item = table.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col}"
        cell_data = item.text() if item else ""

        # Get entry info for file-type specific actions
        entry_name = ""
        entry_type = ""
        # Use tab-aware approach if available
        if hasattr(main_window, 'get_current_file_from_active_tab'):
            file_object, file_type = main_window.get_current_file_from_active_tab()
            if file_type == 'IMG' and file_object and hasattr(file_object, 'entries'):
                if 0 <= row < len(file_object.entries):
                    entry = file_object.entries[row]
                    entry_name = entry.name
                    entry_type = entry.name.split('.')[-1].upper() if '.' in entry.name else ""
        else:
            # Fallback to old method
            if hasattr(main_window, 'current_img') and main_window.current_img:
                if 0 <= row < len(main_window.current_img.entries):
                    entry = main_window.current_img.entries[row]
                    entry_name = entry.name
                    entry_type = entry.name.split('.')[-1].upper() if '.' in entry.name else ""

        # FILE-TYPE SPECIFIC ACTIONS (Advanced functionality)
        if entry_type:
            if entry_type == 'COL':
                # COL file specific actions
                edit_col_action = QAction("Edit COL File", menu_parent)
                edit_col_action.triggered.connect(lambda: edit_col_from_table(main_window, row))
                menu.addAction(edit_col_action)

                analyze_col_action = QAction("Analyze COL File", menu_parent)
                analyze_col_action.triggered.connect(lambda: analyze_col_from_table(main_window, row))
                menu.addAction(analyze_col_action)

            elif entry_type == 'IDE':
                # IDE file specific actions
                view_ide_action = QAction("View IDE Definitions", menu_parent)
                view_ide_action.triggered.connect(lambda: view_ide_definitions(main_window, row))
                menu.addAction(view_ide_action)

                edit_ide_action = QAction("Edit IDE File", menu_parent)
                edit_ide_action.triggered.connect(lambda: edit_ide_file(main_window, row))
                menu.addAction(edit_ide_action)

            elif entry_type == 'DFF':
                # DFF model specific actions
                dff_info_action = QAction("DFF Model Info", menu_parent)
                dff_info_action.triggered.connect(lambda: show_dff_info(main_window, row))
                menu.addAction(dff_info_action)

            elif entry_type == 'TXD':
                # TXD texture specific actions
                txd_view_action = QAction("View TXD Textures", menu_parent)
                txd_view_action.triggered.connect(lambda: view_txd_textures(main_window, row))
                menu.addAction(txd_view_action)

            menu.addSeparator()

        # EXTRACTION ACTIONS (if extraction system is available)
        if hasattr(main_window, 'extract_selected_files'):
            selected_entries = get_selected_entries_for_extraction(main_window)
            if selected_entries:
                extract_selected_action = QAction("Extract Selected", menu_parent)
                extract_selected_action.triggered.connect(main_window.extract_selected_files)
                menu.addAction(extract_selected_action)

            if hasattr(main_window, 'extract_all_files'):
                extract_all_action = QAction("Extract All", menu_parent)
                extract_all_action.triggered.connect(main_window.extract_all_files)
                menu.addAction(extract_all_action)

            # Quick extract submenu
            if entry_type in ['IDE', 'COL', 'DFF', 'TXD']:
                quick_extract_action = QAction(f"Quick Extract {entry_type} Files", menu_parent)
                if entry_type == 'IDE' and hasattr(main_window, 'quick_extract_ide_files'):
                    quick_extract_action.triggered.connect(main_window.quick_extract_ide_files)
                elif entry_type == 'COL' and hasattr(main_window, 'quick_extract_col_files'):
                    quick_extract_action.triggered.connect(main_window.quick_extract_col_files)
                elif entry_type == 'DFF' and hasattr(main_window, 'quick_extract_dff_files'):
                    quick_extract_action.triggered.connect(main_window.quick_extract_dff_files)
                elif entry_type == 'TXD' and hasattr(main_window, 'quick_extract_txd_files'):
                    quick_extract_action.triggered.connect(main_window.quick_extract_txd_files)
                menu.addAction(quick_extract_action)

            menu.addSeparator()

        # STANDARD IMG OPERATIONS
        if hasattr(main_window, 'export_selected'):
            export_action = QAction("Export", menu_parent)
            export_action.triggered.connect(main_window.export_selected)
            menu.addAction(export_action)

        if hasattr(main_window, 'remove_selected'):
            selected_items = table.selectedItems()
            if selected_items:
                remove_action = QAction("Remove", menu_parent)
                remove_action.triggered.connect(main_window.remove_selected)
                menu.addAction(remove_action)

        # RENAME OPERATION
        if hasattr(main_window, 'rename_selected'):
            selected_items = table.selectedItems()
            if selected_items:
                rename_action = QAction("Rename", menu_parent)
                rename_action.triggered.connect(main_window.rename_selected)
                menu.addAction(rename_action)

        # MOVE OPERATION
        if hasattr(main_window, 'move_selected_file'):
            selected_items = table.selectedItems()
            if selected_items:
                move_action = QAction("Move", menu_parent)
                move_action.triggered.connect(main_window.move_selected_file)
                menu.addAction(move_action)

        # ANALYZE FILE OPERATION
        if hasattr(main_window, 'analyze_selected_file'):
            selected_items = table.selectedItems()
            if selected_items:
                analyze_action = QAction("Analyze File", menu_parent)
                analyze_action.triggered.connect(main_window.analyze_selected_file)
                menu.addAction(analyze_action)

        # HEX EDITOR OPERATION
        if hasattr(main_window, 'show_hex_editor_selected'):
            selected_items = table.selectedItems()
            if selected_items:
                hex_action = QAction("Show Hex Editor", menu_parent)
                hex_action.triggered.connect(main_window.show_hex_editor_selected)
                menu.addAction(hex_action)

        # SPECIAL OPERATIONS FOR DFF FILES
        if entry_type == 'DFF':
            # Show texture list for DFF
            texture_action = QAction("Show Texture List for DFF", menu_parent)
            texture_action.triggered.connect(lambda: show_dff_texture_list(main_window, row))
            menu.addAction(texture_action)

            # Show DFF model in viewer
            model_action = QAction("Show DFF Model in Viewer", menu_parent)
            model_action.triggered.connect(lambda: show_dff_model_viewer(main_window, row))
            menu.addAction(model_action)

        # PIN OPERATIONS
        if hasattr(main_window, 'toggle_pinned_entries'):
            selected_items = table.selectedItems()
            if selected_items:
                pin_action = QAction("Toggle Pin", menu_parent)
                pin_action.triggered.connect(main_window.toggle_pinned_entries)
                menu.addAction(pin_action)

        # UNDO/REDO OPERATIONS
        if hasattr(main_window, 'undo'):
            undo_action = QAction("Undo", menu_parent)
            undo_action.triggered.connect(main_window.undo)
            menu.addAction(undo_action)

        if hasattr(main_window, 'redo'):
            redo_action = QAction("Redo", menu_parent)
            redo_action.triggered.connect(main_window.redo)
            menu.addAction(redo_action)

        menu.addSeparator()

        # CLIPBOARD OPERATIONS (Basic functionality)
        copy_cell_action = QAction(f"Copy Cell ({column_name})", menu_parent)
        copy_cell_action.triggered.connect(lambda: copy_table_cell(main_window, row, col))
        menu.addAction(copy_cell_action)

        copy_row_action = QAction("Copy Row", menu_parent)
        copy_row_action.triggered.connect(lambda: copy_table_row(main_window, row))
        menu.addAction(copy_row_action)

        copy_column_action = QAction(f"Copy Column ({column_name})", menu_parent)
        copy_column_action.triggered.connect(lambda: copy_table_column_data(main_window, col))
        menu.addAction(copy_column_action)

        # Copy Selection action (if multiple items selected)
        selected_items = table.selectedItems()
        if len(selected_items) > 1:
            copy_selection_action = QAction(f"Copy Selection ({len(selected_items)} items)", menu_parent)
            copy_selection_action.triggered.connect(lambda: copy_table_selection(main_window))
            menu.addAction(copy_selection_action)
        
        # Copy selected text from current cell (if text is selected)
        copy_selected_text_action = QAction("Copy Selected Text", menu_parent)
        copy_selected_text_action.triggered.connect(lambda: copy_selected_text_from_cell(main_window, row, col))
        menu.addAction(copy_selected_text_action)

        # Copy filename only (for first column)
        if col == 0:
            copy_filename_action = QAction("Copy Filename Only", menu_parent)
            copy_filename_action.triggered.connect(lambda: copy_filename_only(main_window, row))
            menu.addAction(copy_filename_action)

        # Copy file summary
        copy_summary_action = QAction("Copy File Summary", menu_parent)
        copy_summary_action.triggered.connect(lambda: copy_file_summary(main_window, row))
        menu.addAction(copy_summary_action)

        # Show menu at cursor position
        menu.exec(table.mapToGlobal(position))

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error showing context menu: {str(e)}")

# CLIPBOARD OPERATIONS
def copy_table_cell(main_window, row: int, col: int): #vers 1
    """Copy single table cell to clipboard"""
    try:
        table = main_window.gui_layout.table
        item = table.item(row, col)
        
        if item:
            text = item.text()
            QApplication.clipboard().setText(text)
            
            header_item = table.horizontalHeaderItem(col)
            column_name = header_item.text() if header_item else f"Column {col}"
            main_window.log_message(f"Copied {column_name}: '{text}'")
        else:
            main_window.log_message("No data in selected cell")
            
    except Exception as e:
        main_window.log_message(f"Copy cell error: {str(e)}")

def copy_table_row(main_window, row: int): #vers 1
    """Copy entire table row to clipboard"""
    try:
        table = main_window.gui_layout.table
        
        row_data = []
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                row_data.append(item.text())
            else:
                row_data.append("")
        
        text = "\t".join(row_data)
        QApplication.clipboard().setText(text)
        
        filename = row_data[0] if row_data else f"Row {row}"
        main_window.log_message(f"Copied row: {filename}")
        
    except Exception as e:
        main_window.log_message(f"Copy row error: {str(e)}")

def copy_table_column_data(main_window, col: int): #vers 1
    """Copy entire column data to clipboard"""
    try:
        table = main_window.gui_layout.table
        
        header_item = table.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col}"
        
        column_data = []
        for row in range(table.rowCount()):
            item = table.item(row, col)
            if item:
                column_data.append(item.text())
            else:
                column_data.append("")
        
        text = "\n".join(column_data)
        QApplication.clipboard().setText(text)
        
        main_window.log_message(f"Copied column '{column_name}': {table.rowCount()} entries")
        
    except Exception as e:
        main_window.log_message(f"Copy column error: {str(e)}")

def copy_table_selection(main_window): #vers 1
    """Copy selected table items to clipboard"""
    try:
        table = main_window.gui_layout.table
        selected_items = table.selectedItems()
        
        if not selected_items:
            main_window.log_message("No items selected")
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
            ordered_values = []
            for col in sorted(row_data.keys()):
                ordered_values.append(row_data[col])
            lines.append("\t".join(ordered_values))
        
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
        
        main_window.log_message(f"Copied selection: {len(selected_items)} items from {len(rows_data)} rows")
        
    except Exception as e:
        main_window.log_message(f"Copy selection error: {str(e)}")

def copy_filename_only(main_window, row: int): #vers 1
    """Copy filename without extension from first column"""
    try:
        table = main_window.gui_layout.table
        item = table.item(row, 0)
        
        if item:
            full_name = item.text()
            if '.' in full_name:
                filename_only = '.'.join(full_name.split('.')[:-1])
            else:
                filename_only = full_name
                
            QApplication.clipboard().setText(filename_only)
            main_window.log_message(f"Copied filename: '{filename_only}'")
        else:
            main_window.log_message("No filename found")
            
    except Exception as e:
        main_window.log_message(f"Copy filename error: {str(e)}")

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
        main_window.log_message(f"Copied file summary for: {filename}")
        
    except Exception as e:
        main_window.log_message(f"Copy summary error: {str(e)}")

# FILE-TYPE SPECIFIC ACTIONS
def edit_col_from_table(main_window, row: int): #vers 1
    """Edit COL file from table row"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                
                # Check if COL editor is available
                if hasattr(main_window, 'open_col_editor'):
                    main_window.open_col_editor(entry)
                else:
                    main_window.log_message("COL editor not available")
    except Exception as e:
        main_window.log_message(f"COL edit error: {str(e)}")

def analyze_col_from_table(main_window, row: int): #vers 1
    """Analyze COL file from table row"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                
                # Check if COL analyzer is available
                if hasattr(main_window, 'analyze_col_file'):
                    main_window.analyze_col_file(entry)
                else:
                    main_window.log_message("COL analyzer not available")
    except Exception as e:
        main_window.log_message(f"COL analysis error: {str(e)}")

def edit_ide_file(main_window, row: int): #vers 1
    """Edit IDE file from table row"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                
                # Check if IDE editor is available
                if hasattr(main_window, 'open_ide_editor'):
                    main_window.open_ide_editor(entry)
                else:
                    main_window.log_message("IDE editor not available")
    except Exception as e:
        main_window.log_message(f"IDE edit error: {str(e)}")

def view_ide_definitions(main_window, row: int): #vers 1
    """View IDE definitions from table row"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                
                # Check if IDE viewer is available
                if hasattr(main_window, 'view_ide_definitions'):
                    main_window.view_ide_definitions(entry)
                else:
                    main_window.log_message("IDE viewer not available")
    except Exception as e:
        main_window.log_message(f"IDE view error: {str(e)}")

def show_dff_info(main_window, row: int): #vers 1
    """Show DFF model information"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                
                # Check if DFF info viewer is available
                if hasattr(main_window, 'show_dff_info'):
                    main_window.show_dff_info(entry)
                else:
                    main_window.log_message("DFF info viewer not available")
    except Exception as e:
        main_window.log_message(f"DFF info error: {str(e)}")

def view_txd_textures(main_window, row: int): #vers 1
    """View TXD textures from table row"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                
                # Check if TXD viewer is available
                if hasattr(main_window, 'view_txd_textures'):
                    main_window.view_txd_textures(entry)
                else:
                    main_window.log_message("TXD viewer not available")
    except Exception as e:
        main_window.log_message(f"TXD view error: {str(e)}")

# EXTRACTION SUPPORT
def get_selected_entries_for_extraction(main_window) -> List: #vers 1
    """Get currently selected entries for extraction"""
    try:
        entries = []
        
        if not hasattr(main_window.gui_layout, 'table') or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return entries
        
        table = main_window.gui_layout.table
        
        # Get selected rows
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())
        
        # Get corresponding entries
        for row in selected_rows:
            if row < len(main_window.current_img.entries):
                entries.append(main_window.current_img.entries[row])
        
        return entries
        
    except Exception as e:
        main_window.log_message(f"Error getting selected entries: {str(e)}")
        return []

def integrate_right_click_actions(main_window): #vers 3
    """Main integration function - call this from imgfactory.py"""
    try:
        success = setup_table_context_menu(main_window)
        if success:
            main_window.log_message("Complete right-click actions integrated successfully")
            
            # Add convenience method to main window
            main_window.setup_table_right_click = lambda: setup_table_context_menu(main_window)
            
        return success
        
    except Exception as e:
        main_window.log_message(f"Right-click integration error: {str(e)}")
        return False

# Additional functions needed for context menu
def show_dff_texture_list(main_window, row):
    """Show texture list for DFF file - needed for context menu"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                entry_info = {
                    'name': entry.name,
                    'is_dff': entry.name.lower().endswith('.dff'),
                    'size': entry.size,
                    'offset': entry.offset
                }
                
                if entry_info['is_dff']:
                    # Import from comprehensive fix if available
                    try:
                        from apps.components.Img_Factory.comprehensive_fix import show_dff_texture_list as dff_texture_func
                        dff_texture_func(main_window, row, entry_info)
                    except ImportError:
                        # Fallback implementation
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.information(main_window, "DFF Texture List", 
                                              f"Texture List for DFF: {entry.name}\n\n"
                                              f"Note: DFF texture extraction and listing functionality would be implemented here.\n"
                                              f"This would parse the DFF file and show all referenced textures.")
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(main_window, "DFF Texture List", 
                                      "Selected file is not a DFF file")
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error showing DFF texture list: {str(e)}")


def show_dff_model_viewer(main_window, row):
    """Show DFF model in viewer - needed for context menu"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                entry_info = {
                    'name': entry.name,
                    'is_dff': entry.name.lower().endswith('.dff'),
                    'size': entry.size,
                    'offset': entry.offset
                }
                
                if entry_info['is_dff']:
                    # Import from comprehensive fix if available
                    try:
                        from apps.components.Img_Factory.comprehensive_fix import show_dff_model_viewer as dff_viewer_func
                        dff_viewer_func(main_window, row, entry_info)
                    except ImportError:
                        # Fallback implementation
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.information(main_window, "DFF Model Viewer", 
                                              f"DFF Model Viewer for: {entry.name}\n\n"
                                              f"Note: 3D model viewer functionality would be implemented here.\n"
                                              f"This would load and display the DFF model in a 3D viewport.")
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(main_window, "DFF Model Viewer", 
                                      "Selected file is not a DFF file")
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error showing DFF model viewer: {str(e)}")


# Export main functions
__all__ = [
    'setup_table_context_menu',
    'show_advanced_context_menu', 
    'copy_table_cell',
    'copy_table_row',
    'copy_table_column_data',
    'copy_table_selection',
    'copy_filename_only',
    'copy_file_summary',
    'edit_col_from_table',
    'analyze_col_from_table',
    'edit_ide_file',
    'view_ide_definitions',
    'show_dff_info',
    'view_txd_textures',
    'get_selected_entries_for_extraction',
    'integrate_right_click_actions',
    'show_dff_texture_list',
    'show_dff_model_viewer'
]
