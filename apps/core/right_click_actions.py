# X-Seti - December 2025 - IMG Factory 1.5 - Complete Right-Click Actions
# Combined: Basic copying + Advanced file operations + Extraction functionality
# Version: 5

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

def copy_selected_text_from_cell(main_window, row: int, col: int): #vers 1
    """Copy selected text from current cell to clipboard"""
    try:
        table = main_window.gui_layout.table
        item = table.item(row, col)
        
        if item:
            # Get the QTableWidgetItem
            cell_widget = table.cellWidget(row, col) if table.cellWidget(row, col) else None
            
            if cell_widget and hasattr(cell_widget, 'selectedText') and callable(getattr(cell_widget, 'selectedText')):
                # If there's a custom widget with selected text
                selected_text = cell_widget.selectedText()
            else:
                # For standard QTableWidgetItem, we need to handle text selection differently
                # Since standard QTableWidgetItem doesn't support partial text selection,
                # we'll just copy the full text of the cell
                selected_text = item.text()
                
                # However, if the user wants to copy only selected text, they would need
                # to select the text in an editable context. For read-only tables,
                # we'll just copy the whole cell content
                main_window.log_message(f"Note: Full cell content copied. Partial text selection not supported in read-only table.")
            
            if selected_text:
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(selected_text)
                main_window.log_message(f"Copied selected text: '{selected_text[:50]}{'...' if len(selected_text) > 50 else ''}'")
            else:
                # If no specific text was selected, copy the full cell content
                full_text = item.text()
                QApplication.clipboard().setText(full_text)
                main_window.log_message(f"Copied full cell content: '{full_text[:50]}{'...' if len(full_text) > 50 else ''}'")
        else:
            main_window.log_message("No data in selected cell")
            
    except Exception as e:
        main_window.log_message(f"Copy selected text error: {str(e)}")

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


def get_selected_entry_info(main_window, row): #vers 1
    """Get information about selected entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return None
        
        if row < 0 or row >= len(main_window.current_img.entries):
            return None
        
        entry = main_window.current_img.entries[row]
        return {
            'entry': entry,
            'name': entry.name,
            'is_col': entry.name.lower().endswith('.col'),
            'is_dff': entry.name.lower().endswith('.dff'),
            'is_txd': entry.name.lower().endswith('.txd'),
            'size': entry.size,
            'offset': entry.offset
        }
    except Exception as e:
        main_window.log_message(f"❌ Error getting entry info: {str(e)}")
        return None


def edit_col_from_img_entry(main_window, row): #vers 2
    """Edit COL file from IMG entry - WORKING VERSION"""
    try:
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info or not entry_info['is_col']:
            main_window.log_message("❌ Selected entry is not a COL file")
            return False
        
        entry = entry_info['entry']
        main_window.log_message(f"🔧 Opening COL editor for: {entry.name}")
        
        # Use methods from col_operations
        from apps.methods.col_operations import extract_col_from_img_entry, create_temporary_col_file, cleanup_temporary_file
        
        # Extract COL data
        extraction_result = extract_col_from_img_entry(main_window, row)
        if not extraction_result:
            main_window.log_message("❌ Failed to extract COL data")
            return False
        
        col_data, entry_name = extraction_result
        
        # Create temporary COL file
        temp_path = create_temporary_col_file(col_data, entry_name)
        if not temp_path:
            main_window.log_message("❌ Failed to create temporary COL file")
            return False
        
        try:
            # Import and open COL editor
            from apps.components.Col_Editor.col_editor import COLEditorDialog
            
            editor = COLEditorDialog(main_window)
            
            # Load the temporary COL file
            if editor.load_col_file(temp_path):
                editor.setWindowTitle(f"COL Editor - {entry.name}")
                editor.show()  # Use show() instead of exec() for non-modal
                main_window.log_message(f"✅ COL editor opened for: {entry.name}")
                return True
            else:
                main_window.log_message("❌ Failed to load COL file in editor")
                return False
                
        finally:
            # Clean up temporary file
            cleanup_temporary_file(temp_path)
        
    except ImportError:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(main_window, "COL Editor", 
            "COL editor component not available. Please check components.Col_Editor.col_editor.py")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error editing COL file: {str(e)}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Error", f"Failed to edit COL file: {str(e)}")
        return False


def view_col_collision(main_window, row): #vers 2
    """View COL collision - WORKING VERSION"""
    try:
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info or not entry_info['is_col']:
            main_window.log_message("❌ Selected entry is not a COL file")
            return False
        
        entry = entry_info['entry']
        main_window.log_message(f"🔍 Viewing COL collision for: {entry.name}")
        
        # Use methods from col_operations
        from apps.methods.col_operations import extract_col_from_img_entry, get_col_basic_info
        
        # Extract COL data
        extraction_result = extract_col_from_img_entry(main_window, row)
        if not extraction_result:
            main_window.log_message("❌ Failed to extract COL data")
            return False
        
        col_data, entry_name = extraction_result
        
        # Get basic info
        basic_info = get_col_basic_info(col_data)
        
        if 'error' in basic_info:
            main_window.log_message(f"❌ COL analysis error: {basic_info['error']}")
            return False
        
        # Build info display
        from apps.methods.img_core_classes import format_file_size
        info_text = f"COL File: {entry.name}\\n"
        info_text += f"Size: {format_file_size(len(col_data))}\\n"
        info_text += f"Version: {basic_info.get('version', 'Unknown')}\\n"
        info_text += f"Models: {basic_info.get('model_count', 0)}\\n"
        info_text += f"Signature: {basic_info.get('signature', b'Unknown')}\\n"
        
        # Show info dialog
        from apps.gui.col_dialogs import show_col_info_dialog
        show_col_info_dialog(main_window, info_text, f"COL Collision Info - {entry.name}")
        
        main_window.log_message(f"✅ COL collision viewed for: {entry.name}")
        return True
        
    except ImportError:
        main_window.log_message("❌ COL operations not available")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error viewing COL collision: {str(e)}")
        return False


def analyze_col_from_img_entry(main_window, row): #vers 2
    """Analyze COL file from IMG entry - WORKING VERSION"""
    try:
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info or not entry_info['is_col']:
            main_window.log_message("❌ Selected entry is not a COL file")
            return False
        
        entry = entry_info['entry']
        main_window.log_message(f"🔍 Analyzing COL file: {entry.name}")
        
        # Use methods from col_operations
        from apps.methods.col_operations import extract_col_from_img_entry, validate_col_data, create_temporary_col_file, cleanup_temporary_file, get_col_detailed_analysis
        
        # Extract COL data
        extraction_result = extract_col_from_img_entry(main_window, row)
        if not extraction_result:
            main_window.log_message("❌ Failed to extract COL data")
            return False
        
        col_data, entry_name = extraction_result
        
        # Validate COL data
        validation_result = validate_col_data(col_data)
        
        # Get detailed analysis if possible
        temp_path = create_temporary_col_file(col_data, entry_name)
        analysis_data = {}
        
        if temp_path:
            try:
                detailed_analysis = get_col_detailed_analysis(temp_path)
                if 'error' not in detailed_analysis:
                    analysis_data.update(detailed_analysis)
            finally:
                cleanup_temporary_file(temp_path)
        
        # Combine validation and analysis data
        final_analysis = {
            'size': len(col_data),
            **analysis_data,
            **validation_result
        }
        
        # Show analysis dialog
        from apps.gui.col_dialogs import show_col_analysis_dialog
        show_col_analysis_dialog(main_window, final_analysis, entry.name)
        
        main_window.log_message(f"✅ COL analysis completed for: {entry.name}")
        return True
        
    except ImportError:
        main_window.log_message("❌ COL analysis components not available")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error analyzing COL file: {str(e)}")
        return False


def edit_col_collision(main_window, row): #vers 2
    """Edit COL collision - WORKING VERSION (alias for edit_col_from_img_entry)"""
    return edit_col_from_img_entry(main_window, row)


def edit_dff_model(main_window, row): #vers 1
    """Edit DFF model"""
    main_window.log_message(f"✏️ Edit DFF model from row {row} - not yet implemented")


def edit_txd_textures(main_window, row): #vers 1
    """Edit TXD textures"""
    main_window.log_message(f"🎨 Edit TXD textures from row {row} - not yet implemented")


def view_dff_model(main_window, row): #vers 1
    """View DFF model"""
    main_window.log_message(f"👁️ View DFF model from row {row} - not yet implemented")


def view_txd_textures(main_window, row): #vers 1
    """View TXD textures"""
    main_window.log_message(f"View TXD textures from row {row} - not yet implemented")


def replace_selected_entry(main_window, row): #vers 1
    """Replace selected entry"""
    main_window.log_message(f"🔄 Replace entry from row {row} - not yet implemented")


def show_entry_properties(main_window, row): #vers 1
    """Show entry properties"""
    entry_info = get_selected_entry_info(main_window, row)
    if entry_info:
        from apps.methods.img_core_classes import format_file_size
        props_text = f"Entry Properties:\\n\\n"
        props_text += f"Name: {entry_info['name']}\\n"
        props_text += f"Size: {format_file_size(entry_info['size'])}\\n"
        props_text += f"Offset: 0x{entry_info['offset']:08X}\\n"
        props_text += f"Type: {'COL' if entry_info['is_col'] else 'DFF' if entry_info['is_dff'] else 'TXD' if entry_info['is_txd'] else 'Other'}\\n"
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(main_window, "Entry Properties", props_text)
        main_window.log_message(f"📋 Properties shown for: {entry_info['name']}")
    else:
        main_window.log_message(f"❌ Unable to get properties for row {row}")


def enhanced_context_menu_event(main_window, event): #vers 2
    """Enhanced context menu with working COL functions"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return

        table = main_window.gui_layout.table
        # Get the item at the position where the right-click occurred
        item = table.itemAt(event.pos())
        if not item:
            return

        row = item.row()
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info:
            return

        # Create context menu
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(table)
        
        # Add file-type specific actions
        if entry_info['is_col']:
            # COL file actions
            from PyQt6.QtGui import QAction
            view_action = QAction("🔍 View Collision", table)
            view_action.triggered.connect(lambda: view_col_collision(main_window, row))
            menu.addAction(view_action)
            
            edit_action = QAction("🔧 Edit COL File", table)
            edit_action.triggered.connect(lambda: edit_col_from_img_entry(main_window, row))
            menu.addAction(edit_action)
            
            analyze_action = QAction("📊 Analyze COL", table)
            analyze_action.triggered.connect(lambda: analyze_col_from_img_entry(main_window, row))
            menu.addAction(analyze_action)
            
            menu.addSeparator()
            
        elif entry_info['is_dff']:
            # DFF model actions
            from PyQt6.QtGui import QAction
            view_action = QAction("👁️ View Model", table)
            view_action.triggered.connect(lambda: view_dff_model(main_window, row))
            menu.addAction(view_action)
            
            edit_action = QAction("✏️ Edit Model", table)
            edit_action.triggered.connect(lambda: edit_dff_model(main_window, row))
            menu.addAction(edit_action)
            
            menu.addSeparator()
            
        elif entry_info['is_txd']:
            # TXD texture actions
            from PyQt6.QtGui import QAction
            view_action = QAction("View Textures", table)
            view_action.triggered.connect(lambda: view_txd_textures(main_window, row))
            menu.addAction(view_action)
            
            edit_action = QAction("🎨 Edit Textures", table)
            edit_action.triggered.connect(lambda: edit_txd_textures(main_window, row))
            menu.addAction(edit_action)
            
            menu.addSeparator()
        
        # Common actions
        from PyQt6.QtGui import QAction
        props_action = QAction("📋 Properties", table)
        props_action.triggered.connect(lambda: show_entry_properties(main_window, row))
        menu.addAction(props_action)
        
        replace_action = QAction("🔄 Replace Entry", table)
        replace_action.triggered.connect(lambda: replace_selected_entry(main_window, row))
        menu.addAction(replace_action)
        
        # Show menu at the global position of the event
        menu.exec(event.globalPos())

    except Exception as e:
        main_window.log_message(f"❌ Error showing context menu: {str(e)}")


def move_file(main_window, row, entry_info):
    """
    Move selected file to a new location
    """
    try:
        # Get current entry
        entry = entry_info['entry']
        current_name = entry.name
        
        # Show dialog to select destination
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        dest_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Destination Directory",
            ""
        )
        
        if dest_dir:
            # For IMG entries, we can't actually move files since they're inside the IMG
            # Instead, we can rename to change the path-like structure
            QMessageBox.information(main_window, "Move Operation", 
                                  f"Moving '{current_name}' to '{dest_dir}'\\n\\n"
                                  f"Note: In IMG files, entries are virtual and cannot be moved to different directories.\\n"
                                  f"You can rename the entry to reflect a new path structure if needed.")
            
    except Exception as e:
        main_window.log_message(f"❌ Error moving file: {str(e)}")


def move_selected_file(main_window):
    """
    Move selected file (when no specific row selected)
    """
    try:
        # Get selected items from table
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_items = table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
                entry_info = get_entry_info(main_window, row)
                if entry_info:
                    move_file(main_window, row, entry_info)
    except Exception as e:
        main_window.log_message(f"❌ Error moving selected file: {str(e)}")


def analyze_file(main_window, row, entry_info):
    """
    Analyze selected file
    """
    try:
        entry = entry_info['entry']
        name = entry.name
        
        # Determine file type and perform appropriate analysis
        if entry_info['is_col']:
            # Use existing COL analysis functionality
            analyze_col_from_img_entry(main_window, row)
        elif entry_info['is_dff']:
            # DFF analysis
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "DFF Analysis", 
                                  f"DFF Analysis for: {name}\\n\\n"
                                  f"Size: {entry.size} bytes\\n"
                                  f"Offset: 0x{entry.offset:08X}\\n"
                                  f"Type: DFF Model File")
        elif entry_info['is_txd']:
            # TXD analysis
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "TXD Analysis", 
                                  f"TXD Analysis for: {name}\\n\\n"
                                  f"Size: {entry.size} bytes\\n"
                                  f"Offset: 0x{entry.offset:08X}\\n"
                                  f"Type: Texture Dictionary File")
        else:
            # Generic analysis
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "File Analysis", 
                                  f"Analysis for: {name}\\n\\n"
                                  f"Size: {entry.size} bytes\\n"
                                  f"Offset: 0x{entry.offset:08X}\\n"
                                  f"Type: Generic IMG Entry")
        
    except Exception as e:
        main_window.log_message(f"❌ Error analyzing file: {str(e)}")


def analyze_selected_file(main_window):
    """
    Analyze selected file (when no specific row selected)
    """
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_items = table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
                entry_info = get_entry_info(main_window, row)
                if entry_info:
                    analyze_file(main_window, row, entry_info)
    except Exception as e:
        main_window.log_message(f"❌ Error analyzing selected file: {str(e)}")


def show_hex_editor(main_window, row, entry_info):
    """
    Show hex editor for selected file
    """
    try:
        # Import the hex editor module
        from apps.components.Hex_Editor import show_hex_editor_for_entry
        
        # Use the new hex editor implementation
        show_hex_editor_for_entry(main_window, row, entry_info)
        
    except Exception as e:
        main_window.log_message(f"❌ Error showing hex editor: {str(e)}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Error", f"Could not open hex editor:\\n{str(e)}")


def show_hex_editor_selected(main_window):
    """
    Show hex editor for selected file (when no specific row selected)
    """
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_items = table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
                entry_info = get_entry_info(main_window, row)
                if entry_info:
                    show_hex_editor(main_window, row, entry_info)
    except Exception as e:
        main_window.log_message(f"❌ Error showing hex editor for selected: {str(e)}")


def copy_entry_name(main_window, row):
    """
    Copy entry name to clipboard
    """
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                from PyQt6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(entry.name)
                main_window.log_message(f"📋 Copied name: {entry.name}")
    except Exception as e:
        main_window.log_message(f"❌ Error copying entry name: {str(e)}")


def copy_entry_info(main_window, row):
    """
    Copy entry info to clipboard
    """
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                info_text = f"Name: {entry.name}\\nSize: {entry.size}\\nOffset: 0x{entry.offset:08X}"
                from PyQt6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(info_text)
                main_window.log_message(f"📋 Copied info for: {entry.name}")
    except Exception as e:
        main_window.log_message(f"❌ Error copying entry info: {str(e)}")


def get_entry_info(main_window, row):
    """
    Get entry information for a given row
    """
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                return {
                    'entry': entry,
                    'name': entry.name,
                    'is_col': entry.name.lower().endswith('.col'),
                    'is_dff': entry.name.lower().endswith('.dff'),
                    'is_txd': entry.name.lower().endswith('.txd'),
                    'size': entry.size,
                    'offset': entry.offset
                }
        return None
    except Exception:
        return None


def set_game_path(main_window):
    """
    Set game path with support for custom paths including Linux paths
    """
    try:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os
        
        # Get current path if it exists
        current_path = getattr(main_window, 'game_root', None)
        if not current_path or current_path == "C:/":
            # Default to home directory instead of C:/
            current_path = os.path.expanduser("~")
        
        # Open directory dialog without restricting to Windows paths
        folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Game Root Directory (Supports Windows and Linux paths)",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            # Validate that it's a game directory by checking for common game files
            game_files = [
                "gta3.exe", "gta_vc.exe", "gta_sa.exe", "gtasol.exe", "solcore.exe",
                "gta3.dat", "gta_vc.dat", "gta_sa.dat", "gta_sol.dat", "SOL/gta_sol.dat",
                "default.ide", "Data/default.dat", "models/", "textures/", "data/"
            ]
            
            # Check if the folder contains game-related files/directories
            is_game_dir = False
            for item in os.listdir(folder):
                item_lower = item.lower()
                if any(game_file.split('/')[0] in item_lower for game_file in game_files if '/' not in game_file) or \
                   any(game_file in item_lower for game_file in game_files if '/' not in game_file):
                    is_game_dir = True
                    break
            
            # Also check subdirectories
            if not is_game_dir:
                for root, dirs, files in os.walk(folder):
                    for d in dirs:
                        if d.lower() in ['models', 'textures', 'data', 'sfx', 'audio']:
                            is_game_dir = True
                            break
                    if is_game_dir:
                        break
            
            main_window.game_root = folder
            main_window.log_message(f"Game path set: {folder}")
            
            # Update directory tree if it exists
            if hasattr(main_window, 'directory_tree'):
                main_window.directory_tree.game_root = folder
                main_window.directory_tree.current_root = folder
                if hasattr(main_window.directory_tree, 'path_label'):
                    main_window.directory_tree.path_label.setText(folder)
                # Auto-populate the tree
                if hasattr(main_window.directory_tree, 'populate_tree'):
                    main_window.directory_tree.populate_tree(folder)
                    main_window.log_message("Directory tree auto-populated")
            
            # Save settings
            if hasattr(main_window, 'save_settings'):
                main_window.save_settings()
            else:
                # Create a simple save settings if not available
                try:
                    from PyQt6.QtCore import QSettings
                    settings = QSettings("IMG_Factory", "IMG_Factory_Settings")
                    settings.setValue("game_root", folder)
                except:
                    pass
            
            # Show success message
            QMessageBox.information(
                main_window,
                "Game Path Set",
                f"Game path configured:\n{folder}\n\nDirectory tree will now show game files.\nSwitch to the 'Directory Tree' tab to browse."
            )
        else:
            main_window.log_message("Game path selection cancelled")
            
    except Exception as e:
        main_window.log_message(f"Error setting game path: {str(e)}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            main_window,
            "Error Setting Game Path",
            f"An error occurred while setting the game path:\n\n{str(e)}"
        )


def show_dff_texture_list_from_selection(main_window):
    """
    Show DFF texture list for currently selected entry
    """
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_items = table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
                entry_info = get_entry_info(main_window, row)
                if entry_info and entry_info['is_dff']:
                    show_dff_texture_list(main_window, row, entry_info)
                else:
                    # Check if it's a DFF file in the IMG that we need to extract and parse
                    if entry_info and entry_info['name'].lower().endswith('.dff'):
                        show_dff_texture_list_from_img_dff(main_window, row, entry_info)
                    else:
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.information(main_window, "DFF Texture List", 
                                              "Please select a DFF file to view texture list")
    except Exception as e:
        main_window.log_message(f"❌ Error showing DFF texture list from selection: {str(e)}")


def show_dff_texture_list_from_img_dff(main_window, row, entry_info):
    """
    Extract and show DFF texture list from DFF files in IMG
    """
    try:
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        from PyQt6.QtCore import QThread, pyqtSignal
        import tempfile
        import os
        
        # Get the DFF data from the IMG entry
        if hasattr(main_window, 'current_img') and main_window.current_img:
            entry = main_window.current_img.entries[row]
            dff_data = entry.get_data() if hasattr(entry, 'get_data') else None
            
            if dff_data:
                # Create a temporary file to extract the DFF
                with tempfile.NamedTemporaryFile(delete=False, suffix='.dff', mode='wb') as temp_file:
                    temp_file.write(dff_data)
                    temp_dff_path = temp_file.name
                
                try:
                    # Parse the DFF file for texture information
                    textures = parse_dff_textures_from_data(temp_dff_path)
                    
                    # Create dialog to show texture list
                    dialog = QDialog(main_window)
                    dialog.setWindowTitle(f"Textures in {entry.name}")
                    dialog.resize(500, 400)
                    
                    layout = QVBoxLayout(dialog)
                    
                    # Create text area for texture list
                    text_area = QTextEdit()
                    text_area.setReadOnly(True)
                    
                    if textures:
                        texture_list = "\n".join([f"  • {tex}" for tex in textures])
                        text_content = f"Textures found in {entry.name}:\n\n{texture_list}"
                    else:
                        text_content = f"No textures found in {entry.name}"
                    
                    text_area.setPlainText(text_content)
                    layout.addWidget(text_area)
                    
                    # Close button
                    close_btn = QPushButton("Close")
                    close_btn.clicked.connect(dialog.close)
                    layout.addWidget(close_btn)
                    
                    dialog.exec()
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_dff_path):
                        os.remove(temp_dff_path)
            else:
                QMessageBox.warning(main_window, "DFF Texture List", 
                                  f"Could not extract data from {entry.name}")
    except Exception as e:
        main_window.log_message(f"❌ Error showing DFF texture list from IMG: {str(e)}")


def parse_dff_textures_from_data(dff_path):
    """
    Parse a DFF file to extract texture names
    """
    try:
        textures = []
        
        # This is a simplified implementation - in a real application,
        # you'd need a proper DFF parser
        with open(dff_path, 'rb') as f:
            data = f.read()
            
        # Look for texture-related patterns in the DFF data
        import re
        
        # Search for potential texture names in the binary data
        # DFF files often contain texture names in certain sections
        text_data = data.decode('ascii', errors='ignore')
        
        # Look for potential texture names (alphanumeric with underscores, hyphens, dots)
        # Common patterns in DFF files for texture names
        potential_textures = re.findall(r'[A-Za-z0-9_\-]{3,20}\.(?:txd|png|jpg|bmp|dxt|tga)', text_data, re.IGNORECASE)
        
        # Also look for names without extensions that might be texture names
        # Look for names that could be texture names (avoiding too many false positives)
        potential_names = re.findall(r'[A-Za-z][A-Za-z0-9_\-]{3,19}(?=\.)', text_data)
        
        # Combine and deduplicate
        all_matches = list(set(potential_textures + potential_names))
        
        # Filter for likely texture names
        for name in all_matches:
            # Check if it contains common texture-related terms
            if any(tex in name.lower() for tex in ['tex', 'texture', 'material', 'diffuse', 'specular', 'normal', 'bump']):
                textures.append(name)
            # Check if it's a common texture naming pattern (not too generic)
            elif len(name) > 3 and len(name) < 20 and not any(c.isdigit() for c in name[:2]):  # Avoid names starting with numbers
                # Additional check: avoid common non-texture words
                if not any(common_word in name.lower() for common_word in ['object', 'model', 'geometry', 'data', 'file', 'name']):
                    textures.append(name)
        
        # Return unique textures, removing duplicates
        unique_textures = list(set(textures))
        
        # Sort for consistent output
        unique_textures.sort()
        
        return unique_textures
        
    except Exception as e:
        print(f"Error parsing DFF textures: {str(e)}")
        return []


def show_dff_model_viewer_from_selection(main_window):
    """
    Show DFF model viewer for currently selected entry
    """
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_items = table.selectedItems()
            if selected_items:
                row = selected_items[0].row()
                entry_info = get_entry_info(main_window, row)
                if entry_info and entry_info['is_dff']:
                    show_dff_model_viewer(main_window, row, entry_info)
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(main_window, "DFF Model Viewer", 
                                          "Please select a DFF file to view in model viewer")
    except Exception as e:
        main_window.log_message(f"❌ Error showing DFF model viewer from selection: {str(e)}")


def handle_double_click_rename(main_window, row, col):
    """
    Handle double-click rename functionality
    """
    try:
        # Only allow renaming when clicking on the name column (usually column 0)
        if col == 0:  # Assuming name column is first column
            if hasattr(main_window, 'current_img') and main_window.current_img:
                if 0 <= row < len(main_window.current_img.entries):
                    # Get the current entry
                    entry = main_window.current_img.entries[row]
                    current_name = entry.name
                    
                    # Show input dialog for new name
                    from PyQt6.QtWidgets import QInputDialog, QMessageBox
                    new_name, ok = QInputDialog.getText(
                        main_window,
                        "Rename File",
                        f"Enter new name for '{current_name}':",
                        text=current_name
                    )
                    
                    if ok and new_name and new_name != current_name:
                        # Validate the new name
                        if validate_new_name(main_window, new_name):
                            # Check for duplicates
                            if not check_duplicate_name(main_window, new_name, entry):
                                # Perform the rename
                                entry.name = new_name
                                
                                # Update the table display
                                if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                                    table = main_window.gui_layout.table
                                    table.item(row, 0).setText(new_name)

                                # Mark as modified
                                if hasattr(main_window.current_img, 'modified'):
                                    main_window.current_img.modified = True

                                main_window.log_message(f"✅ Renamed '{current_name}' to '{new_name}'")
                                QMessageBox.information(main_window, "Rename Successful", 
                                                      f"Successfully renamed to '{new_name}'")
                            else:
                                QMessageBox.warning(main_window, "Duplicate Name", 
                                                  f"An entry named '{new_name}' already exists")
                        else:
                            QMessageBox.warning(main_window, "Invalid Name", 
                                              "The name provided is invalid")
        else:
            # For other columns, we might want to handle different actions
            main_window.log_message(f"Double-clicked on row {row}, column {col}")
            
    except Exception as e:
        main_window.log_message(f"❌ Error handling double-click rename: {str(e)}")


def validate_new_name(main_window, new_name):
    """
    Validate new name for file entry
    """
    try:
        # Check for empty name
        if not new_name or not new_name.strip():
            return False
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in new_name for char in invalid_chars):
            return False
        
        # Check length (typically IMG entries have 24 char limit)
        if len(new_name) > 24:
            return False
        
        return True
    except Exception:
        return False


def check_duplicate_name(main_window, new_name, current_entry):
    """
    Check if new name would create duplicate
    """
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            for entry in main_window.current_img.entries:
                if entry != current_entry and getattr(entry, 'name', '') == new_name:
                    return True
        return False
    except Exception:
        return True  # Return True on error to be safe


def show_main_context_menu(main_window, position):
    """
    Show context menu for the main window/active tab
    """
    try:
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(main_window)
        
        # Add file operations that were requested
        add_requested_file_operations(main_window, menu)
        
        # Add common operations
        add_common_operations(main_window, menu)
        
        # Show the menu
        menu.exec(main_window.mapToGlobal(position))
        
    except Exception as e:
        main_window.log_message(f"❌ Error showing main context menu: {str(e)}")


def show_table_context_menu(main_window, position):
    """
    Show context menu for the table
    """
    try:
        table = main_window.gui_layout.table
        from PyQt6.QtWidgets import QTableWidgetItem
        item = table.itemAt(position)
        
        if not item:
            # Show generic menu if no item clicked
            show_main_context_menu(main_window, position)
            return
        
        row = item.row()
        menu = QMenu(table)
        
        # Add file operations that were requested
        add_requested_file_operations(main_window, menu, row)
        
        # Add common operations
        add_common_operations(main_window, menu, row)
        
        # Show the menu
        menu.exec(table.mapToGlobal(position))
        
    except Exception as e:
        main_window.log_message(f"❌ Error showing table context menu: {str(e)}")


def add_requested_file_operations(main_window, menu, row=None):
    """
    Add the requested file operations to context menu
    """
    try:
        # Get entry info if row is specified
        entry_info = None
        if row is not None and hasattr(main_window, 'current_img') and main_window.current_img:
            if 0 <= row < len(main_window.current_img.entries):
                entry = main_window.current_img.entries[row]
                entry_info = {
                    'entry': entry,
                    'name': entry.name,
                    'is_col': entry.name.lower().endswith('.col'),
                    'is_dff': entry.name.lower().endswith('.dff'),
                    'is_txd': entry.name.lower().endswith('.txd'),
                    'path': getattr(entry, 'full_path', '') if hasattr(entry, 'full_path') else ''
                }
        
        # Rename action
        from PyQt6.QtGui import QAction
        rename_action = QAction("Rename", menu)
        if row is not None:
            rename_action.triggered.connect(lambda: handle_double_click_rename(main_window, row, 0))
        else:
            rename_action.triggered.connect(main_window.rename_selected)
        menu.addAction(rename_action)
        
        # Move action
        move_action = QAction("Move", menu)
        if row is not None and entry_info:
            move_action.triggered.connect(lambda: move_file(main_window, row, entry_info))
        else:
            move_action.triggered.connect(lambda: move_selected_file(main_window))
        menu.addAction(move_action)
        
        # Analyze file action
        analyze_action = QAction("Analyze File", menu)
        if row is not None and entry_info:
            analyze_action.triggered.connect(lambda: analyze_file(main_window, row, entry_info))
        else:
            analyze_action.triggered.connect(lambda: analyze_selected_file(main_window))
        menu.addAction(analyze_action)
        
        # Show hex editor action
        hex_action = QAction("Show Hex Editor", menu)
        if row is not None and entry_info:
            hex_action.triggered.connect(lambda: show_hex_editor(main_window, row, entry_info))
        else:
            hex_action.triggered.connect(lambda: show_hex_editor_selected(main_window))
        menu.addAction(hex_action)
        
        # Show texture list for DFF (if DFF file)
        if entry_info and entry_info['is_dff']:
            texture_action = QAction("Show Texture List for DFF", menu)
            texture_action.triggered.connect(lambda: show_dff_texture_list(main_window, row, entry_info))
            menu.addAction(texture_action)
        
        # Show DFF model in viewer (if DFF file)
        if entry_info and entry_info['is_dff']:
            model_action = QAction("Show DFF Model in Viewer", menu)
            model_action.triggered.connect(lambda: show_dff_model_viewer(main_window, row, entry_info))
            menu.addAction(model_action)
        
        menu.addSeparator()
        
    except Exception as e:
        main_window.log_message(f"❌ Error adding requested file operations: {str(e)}")


def add_common_operations(main_window, menu, row=None):
    """
    Add common operations to context menu
    """
    try:
        # Export action
        if hasattr(main_window, 'export_selected'):
            from PyQt6.QtGui import QAction
            export_action = QAction("Export", menu)
            export_action.triggered.connect(main_window.export_selected)
            menu.addAction(export_action)
        
        # Remove action
        if hasattr(main_window, 'remove_selected'):
            remove_action = QAction("Remove", menu)
            remove_action.triggered.connect(main_window.remove_selected)
            menu.addAction(remove_action)
        
        # Copy operations
        copy_submenu = menu.addMenu("Copy")
        
        copy_name_action = QAction("Copy Name", menu)
        if row is not None:
            copy_name_action.triggered.connect(lambda: copy_entry_name(main_window, row))
        copy_submenu.addAction(copy_name_action)
        
        copy_info_action = QAction("Copy Info", menu)
        if row is not None:
            copy_info_action.triggered.connect(lambda: copy_entry_info(main_window, row))
        copy_submenu.addAction(copy_info_action)
        
    except Exception as e:
        main_window.log_message(f"❌ Error adding common operations: {str(e)}")


def fix_menu_system_and_functionality(main_window):
    """
    Comprehensive fix for menu system and functionality
    """
    try:
        # Fix the rename functionality to work from both right-click and double-click
        fix_rename_functionality(main_window)
        
        # Implement context menu for active tab
        implement_tab_context_menu(main_window)
        
        # Add requested file operations to main window
        add_file_operations_to_main_window(main_window)
        
        # Set up proper double-click rename functionality
        setup_double_click_rename(main_window)
        
        main_window.log_message("✅ Comprehensive menu system and functionality fix applied")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error applying comprehensive fix: {str(e)}")
        return False


def add_file_operations_to_main_window(main_window):
    """
    Add the requested file operations as methods to the main window
    """
    try:
        # Add move_selected_file method
        main_window.move_selected_file = lambda: move_selected_file(main_window)
        
        # Add analyze_selected_file method
        main_window.analyze_selected_file = lambda: analyze_selected_file(main_window)
        
        # Add show_hex_editor_selected method
        main_window.show_hex_editor_selected = lambda: show_hex_editor_selected(main_window)
        
        # Add show_dff_texture_list method (as a general method that handles current selection)
        main_window.show_dff_texture_list = lambda: show_dff_texture_list_from_selection(main_window)
        
        # Add show_dff_model_viewer method (as a general method that handles current selection)
        main_window.show_dff_model_viewer = lambda: show_dff_model_viewer_from_selection(main_window)
        
        # Add set_game_path method
        main_window.set_game_path = lambda: set_game_path(main_window)
        
        main_window.log_message("✅ File operations added to main window")
        
    except Exception as e:
        main_window.log_message(f"❌ Error adding file operations: {str(e)}")


def fix_rename_functionality(main_window):
    """
    Fix rename functionality to work from both right-click and double-click
    """
    try:
        # Ensure rename_selected function is properly connected
        if not hasattr(main_window, 'rename_selected'):
            from apps.core.imgcol_rename import integrate_imgcol_rename_functions
            integrate_imgcol_rename_functions(main_window)
        
        # Connect double-click event to table for rename
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            # Connect double-click to rename function
            table.cellDoubleClicked.connect(lambda row, col: handle_double_click_rename(main_window, row, col))
        
        main_window.log_message("✅ Rename functionality fixed")
        
    except Exception as e:
        main_window.log_message(f"❌ Error fixing rename functionality: {str(e)}")


def implement_tab_context_menu(main_window):
    """
    Implement context menu for active tab with file operations
    This integrates with the existing context menu system to avoid conflicts
    """
    try:
        # Add context menu to the main window
        from PyQt6.QtCore import Qt
        main_window.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_window.customContextMenuRequested.connect(lambda pos: show_main_context_menu(main_window, pos))
        
        # For the table, we need to integrate with the existing context menu system
        # rather than replacing it to avoid conflicts with the existing setup
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            
            # Instead of replacing the context menu policy, we'll enhance the existing one
            # by making sure our features are available through the existing system
            
            # The existing setup_table_context_menu should already handle the basic context menu
            # We'll enhance it by making sure our operations are available
            
            # Store a reference to our enhanced functionality
            table._enhanced_context_menu = True
        
        main_window.log_message("✅ Tab context menu enhanced with additional operations")
        
    except Exception as e:
        main_window.log_message(f"❌ Error implementing tab context menu: {str(e)}")


def setup_double_click_rename(main_window):
    """
    Setup double-click rename functionality
    """
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            
            # Store original double-click handler if it exists
            if hasattr(table, '_original_double_click_handler'):
                return  # Already set up
            
            # Connect double-click event
            table.cellDoubleClicked.connect(lambda row, col: handle_double_click_rename(main_window, row, col))
            
            # Mark as set up
            table._original_double_click_handler = True
            
            main_window.log_message("✅ Double-click rename functionality set up")
            
    except Exception as e:
        main_window.log_message(f"❌ Error setting up double-click rename: {str(e)}")


# Export main functions
__all__ = [
    'setup_table_context_menu',
    'show_advanced_context_menu', 
    'copy_table_cell',
    'copy_table_row',
    'copy_table_column_data',
    'copy_table_selection',
    'copy_selected_text_from_cell',
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
    'show_dff_model_viewer',
    'get_selected_entry_info',
    'edit_col_from_img_entry',
    'view_col_collision',
    'analyze_col_from_img_entry',
    'edit_col_collision',
    'edit_dff_model',
    'edit_txd_textures',
    'view_dff_model',
    'view_txd_textures',
    'replace_selected_entry',
    'show_entry_properties',
    'enhanced_context_menu_event',
    'move_file',
    'move_selected_file',
    'analyze_file',
    'analyze_selected_file',
    'show_hex_editor',
    'show_hex_editor_selected',
    'copy_entry_name',
    'copy_entry_info',
    'get_entry_info',
    'set_game_path',
    'show_dff_texture_list_from_selection',
    'show_dff_texture_list_from_img_dff',
    'parse_dff_textures_from_data',
    'show_dff_model_viewer_from_selection',
    'handle_double_click_rename',
    'validate_new_name',
    'check_duplicate_name',
    'show_main_context_menu',
    'show_table_context_menu',
    'add_requested_file_operations',
    'add_common_operations',
    'fix_menu_system_and_functionality',
    'add_file_operations_to_main_window',
    'fix_rename_functionality',
    'implement_tab_context_menu',
    'setup_double_click_rename'
]
