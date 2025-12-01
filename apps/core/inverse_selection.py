#this belongs in core/inverse_selection.py - Version: 1
# X-Seti - December01 2025 - IMG Factory 1.5 - Inverse Selection Function

"""
Inverse Selection Function - Inverts the current selection in the table
"""

from PyQt6.QtWidgets import QMessageBox
from apps.methods.tab_system import get_current_file_from_active_tab, validate_tab_before_operation

##Methods list -
# inverse_selection
# integrate_inverse_selection

def inverse_selection(main_window):
    """Invert the current selection in the table"""
    try:
        # Validate tab and get file object
        if not validate_tab_before_operation(main_window, "Inverse Selection"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            QMessageBox.warning(main_window, "No Table", "Table not available")
            return False
        
        table = main_window.gui_layout.table
        
        # Get all selected items
        current_selected_items = table.selectedItems()
        current_selected_rows = set(item.row() for item in current_selected_items)
        
        # Get total number of rows
        total_rows = table.rowCount()
        
        # Clear current selection
        table.clearSelection()
        
        # Select all rows that were NOT selected before
        for row in range(total_rows):
            if row not in current_selected_rows:
                table.selectRow(row)
        
        # Count new selection
        new_selected_items = table.selectedItems()
        main_window.log_message(f"Inversed selection: {len(new_selected_items)} entries now selected")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Inverse selection error: {str(e)}")
        QMessageBox.critical(main_window, "Inverse Selection Error", f"Inverse selection failed: {str(e)}")
        return False


def integrate_inverse_selection(main_window) -> bool:
    """Integrate inverse selection function into main window"""
    try:
        main_window.inverse_selection = lambda: inverse_selection(main_window)
        main_window.invert_selection = lambda: inverse_selection(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Inverse selection function integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Failed to integrate inverse selection: {str(e)}")
        return False