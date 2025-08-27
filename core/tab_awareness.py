#this belongs in methods/tab_awareness.py - Version: 4
# X-Seti - August16 2025 - IMG Factory 1.5 - Shared Tab Awareness System

"""
Shared Tab Awareness System - Centralized tab detection for all operations
Used by: export, import, remove, dump, split, rebuild functions
Fixes multi-tab confusion bugs where functions can't see current selected tab
FIXED: Proper file detection and reference updates
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

##Methods list - Merged in #vers2
# ensure_current_tab_active
# tab_aware_export_selected
# tab_aware_export_via
# tab_aware_dump_entries
# tab_aware_import_files
# tab_aware_import_via
# tab_aware_remove_selected
# tab_aware_remove_via
# integrate_tab_aware_functions

def ensure_current_tab_active(main_window): #vers 1
    """Ensure current tab references are properly set before any operation"""
    try:
        # Force update current tab references
        if hasattr(main_window, 'ensure_current_tab_references_valid'):
            return main_window.ensure_current_tab_references_valid()
        else:
            # Fallback - manually trigger tab change
            current_index = main_window.main_tab_widget.currentIndex()
            if current_index != -1:
                main_window._on_tab_changed(current_index)
                return True
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error ensuring tab active: {str(e)}")
        return False


def tab_aware_export_selected(main_window): #vers 1
    """Export selected entries with tab validation"""
    try:
        # CRITICAL: Ensure current tab is properly referenced
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        # Verify we have a file loaded
        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File",
                "Please open an IMG or COL file first.")
            return

        # Call original export function
        try:
            from core.export import export_selected_function
            export_selected_function(main_window)
        except ImportError:
            # Fallback to legacy functions
            if hasattr(main_window, 'export_selected_entries'):
                main_window.export_selected_entries()
            else:
                main_window.log_message("❌ Export function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware export error: {str(e)}")


def tab_aware_export_via(main_window): #vers 1
    """Export via IDE with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File",
                "Please open an IMG or COL file first.")
            return

        try:
            from core.export import export_via_function
            export_via_function(main_window)
        except ImportError:
            if hasattr(main_window, 'export_selected_via'):
                main_window.export_selected_via()
            else:
                main_window.log_message("❌ Export via function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware export via error: {str(e)}")


def tab_aware_dump_entries(main_window): #vers 1
    """Dump entries with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File",
                "Please open an IMG or COL file first.")
            return

        try:
            from core.dump import dump_all_function
            dump_all_function(main_window)
        except ImportError:
            if hasattr(main_window, 'dump_entries'):
                main_window.dump_entries()
            else:
                main_window.log_message("❌ Dump function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware dump error: {str(e)}")


def tab_aware_import_files(main_window): #vers 1
    """Import files with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        # Import works with empty tabs too, but we need an IMG file for target
        if not main_window.current_img:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No IMG File",
                "Please open an IMG file first to import into.")
            return

        try:
            from core.importer import import_files_function
            import_files_function(main_window)
        except ImportError:
            if hasattr(main_window, 'import_files'):
                main_window.import_files()
            else:
                main_window.log_message("❌ Import function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware import error: {str(e)}")


def tab_aware_import_via(main_window): #vers 1
    """Import via IDE with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        if not main_window.current_img:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No IMG File",
                "Please open an IMG file first to import into.")
            return

        try:
            from core.importer import import_via_function
            import_via_function(main_window)
        except ImportError:
            if hasattr(main_window, 'import_files_via'):
                main_window.import_files_via()
            else:
                main_window.log_message("❌ Import via function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware import via error: {str(e)}")


def tab_aware_remove_selected(main_window): #vers 1
    """Remove selected entries with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        if not main_window.current_img and not main_window.current_col:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No File",
                "Please open an IMG or COL file first.")
            return

        try:
            from core.remove import remove_selected_function
            remove_selected_function(main_window)
        except ImportError:
            if hasattr(main_window, 'remove_selected'):
                main_window.remove_selected()
            else:
                main_window.log_message("❌ Remove function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware remove error: {str(e)}")


def tab_aware_remove_via(main_window): #vers 1
    """Remove via entries with tab validation"""
    try:
        if not ensure_current_tab_active(main_window):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "Tab Error",
                "Cannot access current tab data. Please try selecting the tab again.")
            return

        if not main_window.current_img:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(main_window, "No IMG File",
                "Please open an IMG file first.")
            return

        try:
            from core.remove import remove_via_entries_function
            remove_via_entries_function(main_window)
        except ImportError:
            if hasattr(main_window, 'remove_via_entries'):
                main_window.remove_via_entries()
            else:
                main_window.log_message("❌ Remove via function not available")

    except Exception as e:
        main_window.log_message(f"❌ Tab-aware remove via error: {str(e)}")


def integrate_tab_aware_functions(main_window): #vers 1
    """Replace existing function mappings with tab-aware versions"""
    try:
        # Replace export functions
        main_window.export_selected = lambda: tab_aware_export_selected(main_window)
        main_window.export_selected_entries = lambda: tab_aware_export_selected(main_window)
        main_window.export_selected_via = lambda: tab_aware_export_via(main_window)
        main_window.export_via = lambda: tab_aware_export_via(main_window)

        # Replace dump functions
        main_window.dump_entries = lambda: tab_aware_dump_entries(main_window)
        main_window.dump_all_entries = lambda: tab_aware_dump_entries(main_window)

        # Replace import functions
        main_window.import_files = lambda: tab_aware_import_files(main_window)
        main_window.import_files_via = lambda: tab_aware_import_via(main_window)
        main_window.import_via = lambda: tab_aware_import_via(main_window)

        # Replace remove functions
        main_window.remove_selected = lambda: tab_aware_remove_selected(main_window)
        main_window.remove_selected_entries = lambda: tab_aware_remove_selected(main_window)
        main_window.remove_via_entries = lambda: tab_aware_remove_via(main_window)
        main_window.remove_via = lambda: tab_aware_remove_via(main_window)

        main_window.log_message("✅ Tab-aware functions integrated - Export/Import will now work with current tab")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error integrating tab-aware functions: {str(e)}")
        return False


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


def get_current_file_from_active_tab(main_window) -> Tuple[Optional[Any], str]: #vers 2
    """Get current file object and type from active tab - FIXED: Better detection
    
    Returns:
        Tuple of (file_object, file_type) where file_type is 'IMG', 'COL', or 'NONE'
    """
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return None, 'NONE'
        
        # FIXED: Check main window references FIRST (most reliable)
        if hasattr(main_window, 'current_img') and main_window.current_img:
            return main_window.current_img, 'IMG'
        
        if hasattr(main_window, 'current_col') and main_window.current_col:
            return main_window.current_col, 'COL'
        
        # Then check open_files
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
    """Get file object and type for specific tab index - FIXED: Proper detection
    
    Args:
        main_window: Main application window
        tab_index: Index of tab to check
        
    Returns:
        Tuple of (file_object, file_type)
    """
    try:
        if not hasattr(main_window, 'main_tab_widget'):
            return None, 'NONE'
        
        if tab_index < 0 or tab_index >= main_window.main_tab_widget.count():
            return None, 'NONE'
        
        # FIXED: Check open_files for loaded file objects
        if hasattr(main_window, 'open_files') and tab_index in main_window.open_files:
            file_info = main_window.open_files[tab_index]
            file_object = file_info.get('file_object')
            file_type = file_info.get('type', 'NONE')
            
            # FIXED: Verify file object is actually loaded
            if file_object:
                # Double-check file type based on object attributes
                if hasattr(file_object, 'entries') and file_object.entries:
                    return file_object, 'IMG'
                elif hasattr(file_object, 'models') and file_object.models:
                    return file_object, 'COL'
                elif file_type in ['IMG', 'COL']:
                    # Trust the stored type even if object seems empty
                    return file_object, file_type
        
        # FIXED: For current tab, check main window references as backup
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


def ensure_tab_references_valid(main_window) -> bool: #vers 2
    """Ensure main_window.current_img/current_col point to active tab's file - FIXED
    
    Returns:
        True if references updated successfully
    """
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            main_window.current_img = None
            main_window.current_col = None
            return False
        
        # FIXED: Get file from open_files and update main window references
        file_object, file_type = get_tab_file_data(main_window, current_index)
        
        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
            main_window.current_col = None
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🔄 Updated current_img from tab {current_index}")
            return True
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
            main_window.current_img = None
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🔄 Updated current_col from tab {current_index}")
            return True
        else:
            # No file in active tab
            main_window.current_img = None
            main_window.current_col = None
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🔄 Cleared file references for empty tab {current_index}")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error updating tab references: {str(e)}")
        return False


def refresh_current_tab_data(main_window) -> bool: #vers 3
    """Force refresh of current tab data and main window references - FIXED
    
    Returns:
        True if refresh successful
    """
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Refreshing tab data for tab {current_index}")
        
        # FIXED: Update references from open_files
        success = ensure_tab_references_valid(main_window)
        
        # FIXED: Update GUI table reference
        if hasattr(main_window, '_find_table_in_tab'):
            current_tab_widget = main_window.main_tab_widget.widget(current_index)
            if current_tab_widget:
                current_table = main_window._find_table_in_tab(current_tab_widget)
                if current_table and hasattr(main_window, 'gui_layout'):
                    main_window.gui_layout.table = current_table
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔄 Tab refresh result: {'Success' if success else 'Failed'}")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error refreshing tab data: {str(e)}")
        return False


def validate_tab_before_operation(main_window, operation_name: str = "operation") -> bool: #vers 3
    """Validate tab state before performing any file operation - FIXED: Better validation
    
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
        
        # FIXED: Force refresh tab references first
        refresh_current_tab_data(main_window)
        
        # Check for loaded files
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Detected file type: {file_type}, File object: {type(file_object).__name__ if file_object else 'None'}")
        
        # Final validation
        if file_type == 'NONE' or not file_object:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ No valid file found. File type: {file_type}, File object: {file_object}")
            
            QMessageBox.warning(main_window, "No File", 
                f"No IMG or COL file detected in current tab. Tab info:\n"
                f"• Current tab: {current_index}\n"
                f"• Total tabs: {total_tabs}\n"
                f"• Detected type: {file_type}\n\n"
                f"Make sure the tab contains a loaded IMG or COL file.")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Tab validation passed for {operation_name} - Tab {current_index}: {file_type}")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Tab validation error for {operation_name}: {str(e)}")
        return False


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
