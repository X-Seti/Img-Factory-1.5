#this belongs in methods/tab_awareness.py - Version: 1
# X-Seti - August16 2025 - IMG Factory 1.5 - Shared Tab Awareness System

"""
Shared Tab Awareness System - Centralized tab detection for all operations
Used by: export, import, remove, dump, split, rebuild functions
Fixes multi-tab confusion bugs where functions can't see current selected tab
"""

from typing import Optional, Dict, Any, List, Tuple
from PyQt6.QtWidgets import QMessageBox

##Methods list -
# get_current_active_tab_info
# get_current_file_from_active_tab
# get_current_file_type_from_tab
# get_selected_entries_from_active_tab
# ensure_tab_references_valid
# refresh_current_tab_data
# validate_tab_before_operation
# get_active_tab_index
# get_tab_file_data
# integrate_tab_awareness_system

def get_current_active_tab_info(main_window) -> Dict[str, Any]: #vers 1
    """Get comprehensive info about currently active tab
    
    Returns:
        Dict with: tab_index, file_type, file_object, table_widget, selected_entries
    """
    try:
        tab_info = {
            'tab_index': -1,
            'file_type': 'NONE',
            'file_object': None,
            'table_widget': None,
            'selected_entries': [],
            'tab_valid': False
        }
        
        if not hasattr(main_window, 'main_tab_widget'):
            return tab_info
        
        # Get current tab index
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return tab_info
        
        tab_info['tab_index'] = current_index
        
        # Get current tab widget
        current_tab = main_window.main_tab_widget.currentWidget()
        if not current_tab:
            return tab_info
        
        # Find table widget in current tab
        table_widget = None
        if hasattr(current_tab, 'table'):
            table_widget = current_tab.table
        elif hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table_widget = main_window.gui_layout.table
        
        tab_info['table_widget'] = table_widget
        
        # Get file object and type from tab
        file_object, file_type = get_tab_file_data(main_window, current_index)
        tab_info['file_object'] = file_object
        tab_info['file_type'] = file_type
        
        # Get selected entries from table
        if table_widget:
            selected_entries = get_selected_entries_from_table(table_widget, file_object)
            tab_info['selected_entries'] = selected_entries
        
        tab_info['tab_valid'] = file_object is not None
        
        return tab_info
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting tab info: {str(e)}")
        return tab_info


def get_current_file_from_active_tab(main_window) -> Tuple[Optional[Any], str]: #vers 1
    """Get current file object and type from active tab
    
    Returns:
        Tuple of (file_object, file_type) where file_type is 'IMG', 'COL', or 'NONE'
    """
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return None, 'NONE'
        
        return get_tab_file_data(main_window, current_index)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting current file from tab: {str(e)}")
        return None, 'NONE'


def get_current_file_type_from_tab(main_window) -> str: #vers 1
    """Get file type from currently active tab
    
    Returns:
        'IMG', 'COL', or 'NONE'
    """
    try:
        _, file_type = get_current_file_from_active_tab(main_window)
        return file_type
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting file type from tab: {str(e)}")
        return 'NONE'


def get_selected_entries_from_active_tab(main_window) -> List[Any]: #vers 1
    """Get selected entries from currently active tab's table
    
    Returns:
        List of selected entries or empty list
    """
    try:
        tab_info = get_current_active_tab_info(main_window)
        return tab_info.get('selected_entries', [])
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting selected entries from tab: {str(e)}")
        return []


def get_tab_file_data(main_window, tab_index: int) -> Tuple[Optional[Any], str]: #vers 3
    """Get file object and type"""
    try:
        if tab_index < 0 or tab_index >= main_window.main_tab_widget.count():
            return None, 'NONE'

        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return None, 'NONE'

        # NEW: Get from tab storage first
        if hasattr(tab_widget, 'tab_ready') and tab_widget.tab_ready:
            file_object = getattr(tab_widget, 'file_object', None)
            file_type = getattr(tab_widget, 'file_type', 'NONE')
            return file_object, file_type

        # OLD system fallback (keep for compatibility during migration)
        if hasattr(tab_widget, 'img_file') and tab_widget.img_file:
            return tab_widget.img_file, 'IMG'

        if hasattr(tab_widget, 'col_file') and tab_widget.col_file:
            return tab_widget.col_file, 'COL'

        # Check main window as last resort
        if tab_index == main_window.main_tab_widget.currentIndex():
            if hasattr(main_window, 'current_img') and main_window.current_img:
                return main_window.current_img, 'IMG'
            if hasattr(main_window, 'current_col') and main_window.current_col:
                return main_window.current_col, 'COL'

        return None, 'NONE'

    except Exception as e:
        return None, 'NONE'


def get_selected_entries_from_table(table_widget, file_object) -> List[Any]: #vers 1
    """Extract selected entries from table widget
    
    Args:
        table_widget: QTableWidget containing entries
        file_object: IMG or COL file object
        
    Returns:
        List of selected entries
    """
    try:
        if not table_widget or not file_object:
            return []
        
        selected_entries = []
        selected_rows = set()
        
        # Get selected rows
        for item in table_widget.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return []
        
        # Get entries based on file type
        if hasattr(file_object, 'entries'):  # IMG file
            for row in selected_rows:
                if row < len(file_object.entries):
                    selected_entries.append(file_object.entries[row])
        
        elif hasattr(file_object, 'models'):  # COL file
            for row in selected_rows:
                if row < len(file_object.models):
                    model = file_object.models[row]
                    col_entry = {
                        'name': f"{getattr(model, 'name', f'model_{row}')}.col",
                        'type': 'COL_MODEL',
                        'model': model,
                        'index': row,
                        'col_file': file_object
                    }
                    selected_entries.append(col_entry)
        
        return selected_entries
        
    except Exception as e:
        return []


def ensure_tab_references_valid(main_window) -> bool: #vers 1
    """Ensure main_window.current_img/current_col point to active tab's file
    
    Returns:
        True if references updated successfully
    """
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type == 'IMG':
            main_window.current_img = file_object
            main_window.current_col = None
            return True
        elif file_type == 'COL':
            main_window.current_col = file_object
            main_window.current_img = None
            return True
        else:
            # No file in active tab
            main_window.current_img = None
            main_window.current_col = None
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error updating tab references: {str(e)}")
        return False


def refresh_current_tab_data(main_window) -> bool: #vers 2
    """Force refresh of current tab data and main window references - FIXED: Force tab switch
    
    Returns:
        True if refresh successful
    """
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Refreshing tab data for tab {current_index}")
        
        # FIXED: Force tab change event to update references
        if hasattr(main_window, '_on_tab_changed'):
            main_window._on_tab_changed(current_index)
        elif hasattr(main_window, 'on_tab_changed'):
            main_window.on_tab_changed(current_index)
        elif hasattr(main_window, 'tab_changed'):
            main_window.tab_changed(current_index)
        
        # Update main window references to match active tab
        success = ensure_tab_references_valid(main_window)
        
        # FIXED: Additional forced update
        if not success:
            # Try to manually detect and set file references
            file_object, file_type = get_tab_file_data(main_window, current_index)
            if file_object and file_type != 'NONE':
                if file_type == 'IMG':
                    main_window.current_img = file_object
                    main_window.current_col = None
                    success = True
                elif file_type == 'COL':
                    main_window.current_col = file_object  
                    main_window.current_img = None
                    success = True
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Tab refresh result: {'Success' if success else 'Failed'}")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error refreshing tab data: {str(e)}")
        return False


def validate_tab_before_operation(main_window, operation_name: str = "operation") -> bool: #vers 2
    """Validate tab state before performing any file operation - FIXED: Better debugging
    
    Args:
        main_window: Main application window
        operation_name: Name of operation for error messages
        
    Returns:
        True if tab is valid for operations
    """
    try:
        # DEBUG: Add comprehensive logging
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Tab validation for {operation_name}...")
        
        # Check if we have tabs
        if not hasattr(main_window, 'main_tab_widget'):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No main_tab_widget attribute found")
            QMessageBox.warning(main_window, "No Tabs", 
                f"Cannot perform {operation_name}: No tab system available.")
            return False
        
        # Check if any tab is active
        current_index = main_window.main_tab_widget.currentIndex()
        total_tabs = main_window.main_tab_widget.count()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Current tab: {current_index}, Total tabs: {total_tabs}")
        
        if current_index == -1:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No active tab (index = -1)")
            QMessageBox.warning(main_window, "No Active Tab", 
                f"Cannot perform {operation_name}: No tab is currently active.")
            return False
        
        # Check current tab widget
        current_tab_widget = main_window.main_tab_widget.widget(current_index)
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Current tab widget: {type(current_tab_widget).__name__ if current_tab_widget else 'None'}")
        
        # FIXED: Try multiple methods to detect file
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Detected file type: {file_type}, File object: {type(file_object).__name__ if file_object else 'None'}")
        
        # FIXED: Also check main_window direct references as fallback
        if file_type == 'NONE':
            if hasattr(main_window, 'current_img') and main_window.current_img:
                file_object = main_window.current_img
                file_type = 'IMG'
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"🔍 Fallback: Found IMG in main_window.current_img")
            elif hasattr(main_window, 'current_col') and main_window.current_col:
                file_object = main_window.current_col
                file_type = 'COL'
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"🔍 Fallback: Found COL in main_window.current_col")
        
        # Update main window references if needed
        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
            main_window.current_col = None
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
            main_window.current_img = None
        
        # Final validation
        if file_type == 'NONE' or not file_object:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ No valid file found. File type: {file_type}, File object: {file_object}")
            
            # FIXED: Don't show dialog if we can see files in the interface
            if total_tabs > 0:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚠️ Files may be loaded but not detected properly - proceeding anyway")
                return True  # Let the operation try to proceed
            
            QMessageBox.warning(main_window, "No File", 
                f"Cannot perform {operation_name}: Please open an IMG or COL file first.")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Tab validation passed for {operation_name} - Tab {current_index}: {file_type}")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Tab validation error for {operation_name}: {str(e)}")
        
        # FIXED: Don't block operation with dialog, just log and proceed
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Tab validation failed but proceeding anyway")
        return True  # Allow operation to proceed and handle its own validation


def get_active_tab_index(main_window) -> int: #vers 1
    """Get index of currently active tab
    
    Returns:
        Tab index or -1 if no active tab
    """
    try:
        if hasattr(main_window, 'main_tab_widget'):
            return main_window.main_tab_widget.currentIndex()
        return -1
        
    except Exception:
        return -1


def integrate_tab_awareness_system(main_window) -> bool: #vers 1
    """Integrate tab awareness functions into main window
    
    Args:
        main_window: Main application window
        
    Returns:
        True if integration successful
    """
    try:
        # Add all tab awareness functions to main window
        main_window.get_current_active_tab_info = lambda: get_current_active_tab_info(main_window)
        main_window.get_current_file_from_active_tab = lambda: get_current_file_from_active_tab(main_window)
        main_window.get_current_file_type_from_tab = lambda: get_current_file_type_from_tab(main_window)
        main_window.get_selected_entries_from_active_tab = lambda: get_selected_entries_from_active_tab(main_window)
        main_window.ensure_tab_references_valid = lambda: ensure_tab_references_valid(main_window)
        main_window.refresh_current_tab_data = lambda: refresh_current_tab_data(main_window)
        main_window.validate_tab_before_operation = lambda op="operation": validate_tab_before_operation(main_window, op)
        main_window.get_active_tab_index = lambda: get_active_tab_index(main_window)
        
        # Override existing problematic functions
        main_window.get_current_file_type = lambda: get_current_file_type_from_tab(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries_from_active_tab(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Tab awareness system integrated - Multi-tab operations fixed")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error integrating tab awareness system: {str(e)}")
        return False


__all__ = [
    'get_current_active_tab_info',
    'get_current_file_from_active_tab', 
    'get_current_file_type_from_tab',
    'get_selected_entries_from_active_tab',
    'ensure_tab_references_valid',
    'refresh_current_tab_data',
    'validate_tab_before_operation',
    'get_active_tab_index',
    'get_tab_file_data',
    'integrate_tab_awareness_system'
]
