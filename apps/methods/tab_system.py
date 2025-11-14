#this belongs in methods/tab_system.py - Version: 5
# X-Seti - November14 2025 - IMG Factory 1.5 - Complete Tab System

"""
Complete Tab System - Consolidated from tab_functions, tab_aware_functions, tab_validation
Handles tab creation, management, validation, and awareness
Supports IMG, COL, and TXD files
FIXED: Always creates new tabs, never overwrites existing tabs
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QMessageBox
from typing import Optional, Tuple, Any, Dict, List

##Methods list -
# clear_tab
# close_tab
# create_tab
# ensure_tab_references_valid
# get_active_tab_index
# get_current_active_tab_info
# get_current_file_from_active_tab
# get_current_file_type_from_tab
# get_selected_entries_from_active_tab
# get_selected_entries_from_table
# get_tab_data
# get_tab_file_data
# get_tab_table
# integrate_tab_system
# migrate_tabs
# refresh_current_tab_data
# setup_tab_system
# switch_tab
# update_references
# validate_tab_before_operation


def create_tab(main_window, file_path=None, file_type=None, file_object=None): #vers 5
    """
    Create NEW tab - ALWAYS creates a new tab, never overwrites existing tabs
    Stores ALL data on tab widget itself
    
    Args:
        main_window: Main window instance
        file_path: Path to file being loaded
        file_type: 'IMG', 'COL', 'TXD', or 'NONE'
        file_object: Loaded file object
    
    Returns:
        int: Index of newly created tab
    """
    try:
        # ALWAYS create new tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create NEW GUI components for this tab
        main_window.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Get the NEW table widget created for THIS tab
        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            tab_widget.table_ref = tables[-1]
        else:
            main_window.log_message("No table found in new tab")
            tab_widget.table_ref = None

        # Store file data directly on tab widget
        tab_widget.file_path = file_path
        tab_widget.file_type = file_type or 'NONE'
        tab_widget.file_object = file_object
        tab_widget.tab_ready = True

        # Generate tab name with icon
        if file_path:
            import os
            file_name = os.path.basename(file_path)

            if file_name.lower().endswith('.img'):
                file_name = file_name[:-4]
                try:
                    from apps.methods.svg_shared_icons import get_img_file_icon
                    icon = get_img_file_icon()
                    has_icon = True
                except:
                    icon = None
                    has_icon = False
            elif file_name.lower().endswith('.col'):
                file_name = file_name[:-4]
                try:
                    from apps.methods.svg_shared_icons import get_col_file_icon
                    icon = get_col_file_icon()
                    has_icon = True
                except:
                    icon = None
                    has_icon = False
            elif file_name.lower().endswith('.txd'):
                file_name = file_name[:-4]
                try:
                    from apps.methods.svg_shared_icons import get_txd_file_icon
                    icon = get_txd_file_icon()
                    has_icon = True
                except:
                    icon = None
                    has_icon = False
            else:
                icon = None
                has_icon = False

            tab_name = file_name
        else:
            tab_name = "No File"
            icon = None
            has_icon = False

        tab_widget.tab_name = tab_name

        # Add new tab - ALWAYS adds, never reuses
        new_index = main_window.main_tab_widget.addTab(tab_widget, tab_name)
        
        # Set icon if available
        if has_icon and icon:
            main_window.main_tab_widget.setTabIcon(new_index, icon)
        
        # Set tab text
        main_window.main_tab_widget.setTabText(new_index, tab_name)
        
        # Switch to new tab
        main_window.main_tab_widget.setCurrentIndex(new_index)

        main_window.log_message(f"Tab {new_index} created: {tab_name}")
        return new_index

    except Exception as e:
        main_window.log_message(f"Error creating tab: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_tab_data(tab_widget) -> Tuple[Optional[Any], str, Optional[Any]]: #vers 1
    """Get file data from tab widget - Returns (file_object, file_type, table_widget)"""
    try:
        if not tab_widget:
            return None, 'NONE', None

        file_object = getattr(tab_widget, 'file_object', None)
        file_type = getattr(tab_widget, 'file_type', 'NONE')
        table = getattr(tab_widget, 'table_ref', None)

        return file_object, file_type, table

    except Exception as e:
        return None, 'NONE', None


def get_tab_table(tab_widget): #vers 1
    """Get table widget from tab"""
    try:
        if hasattr(tab_widget, 'table_ref'):
            return tab_widget.table_ref

        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            tab_widget.table_ref = tables[-1]
            return tables[-1]

        return None

    except Exception as e:
        return None


def update_references(main_window, tab_index): #vers 3
    """Update main window references to current tab's data"""
    try:
        if tab_index == -1:
            main_window.current_img = None
            main_window.current_col = None
            main_window.current_txd = None
            if hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table = None
            return True

        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return False

        file_object, file_type, table = get_tab_data(tab_widget)

        if table:
            main_window.gui_layout.table = table

        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
            main_window.current_col = None
            main_window.current_txd = None
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
            main_window.current_img = None
            main_window.current_txd = None
        elif file_type == 'TXD' and file_object:
            main_window.current_txd = file_object
            main_window.current_img = None
            main_window.current_col = None
        else:
            main_window.current_img = None
            main_window.current_col = None
            main_window.current_txd = None

        main_window.log_message(f"References updated to tab {tab_index} ({file_type})")
        return True

    except Exception as e:
        main_window.log_message(f"Error updating references: {str(e)}")
        return False


def close_tab(main_window, tab_index): #vers 2
    """Close tab - currentChanged signal handles switching"""
    try:
        tab_count = main_window.main_tab_widget.count()

        if tab_count <= 1:
            clear_tab(main_window, 0)
            return

        tab_widget = main_window.main_tab_widget.widget(tab_index)
        tab_name = getattr(tab_widget, 'tab_name', 'Unknown')

        main_window.main_tab_widget.removeTab(tab_index)
        main_window.log_message(f"Closed tab: {tab_name}")

    except Exception as e:
        main_window.log_message(f"Error closing tab: {str(e)}")


def clear_tab(main_window, tab_index): #vers 2
    """Clear tab contents without removing tab"""
    try:
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return

        tab_widget.file_object = None
        tab_widget.file_type = 'NONE'
        tab_widget.file_path = None
        tab_widget.tab_name = "No File"

        if hasattr(tab_widget, 'table_ref') and tab_widget.table_ref:
            tab_widget.table_ref.setRowCount(0)

        main_window.main_tab_widget.setTabText(tab_index, "No File")

        if tab_index == main_window.main_tab_widget.currentIndex():
            main_window.current_img = None
            main_window.current_col = None
            main_window.current_txd = None
            main_window._update_ui_for_no_img()

        main_window.log_message("Tab cleared")

    except Exception as e:
        main_window.log_message(f"Error clearing tab: {str(e)}")


def switch_tab(main_window, tab_index): #vers 5
    """Handle tab switching - updates ALL TXD Workshops"""
    try:
        if tab_index == -1:
            main_window.current_img = None
            main_window.current_col = None
            main_window.current_txd = None
            if hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table = None
            return

        main_window.log_message(f"Switching to tab: {tab_index}")
        update_references(main_window, tab_index)

        # Update ALL open TXD Workshops
        if hasattr(main_window, 'txd_workshops'):
            tab_widget = main_window.main_tab_widget.widget(tab_index)
            file_path = getattr(tab_widget, 'file_path', None)

            if file_path:
                for workshop in main_window.txd_workshops:
                    if workshop and workshop.isVisible():
                        if file_path.lower().endswith('.txd'):
                            workshop.open_txd_file(file_path)
                        elif file_path.lower().endswith('.img'):
                            workshop.load_from_img_archive(file_path)

    except Exception as e:
        main_window.log_message(f"Error switching tab: {str(e)}")


def setup_tab_system(main_window): #vers 3
    """Setup tab system - connect signals and register methods"""
    try:
        main_window.log_message("Setting up tab system...")

        # Disconnect any existing signals
        try:
            main_window.main_tab_widget.currentChanged.disconnect()
            main_window.main_tab_widget.tabCloseRequested.disconnect()
        except:
            pass

        # Connect tab signals
        main_window.main_tab_widget.currentChanged.connect(
            lambda index: switch_tab(main_window, index)
        )
        main_window.main_tab_widget.tabCloseRequested.connect(
            lambda index: close_tab(main_window, index)
        )

        # Register methods on main window
        main_window.create_tab = lambda fp=None, ft=None, fo=None: create_tab(main_window, fp, ft, fo)
        main_window.close_tab = lambda idx: close_tab(main_window, idx)
        main_window.clear_tab = lambda idx: clear_tab(main_window, idx)
        main_window.update_references = lambda idx: update_references(main_window, idx)

        main_window.log_message("Tab system active")
        main_window.log_message("  Always creates new tabs")
        main_window.log_message("  Supports IMG, COL, TXD")

        return True

    except Exception as e:
        main_window.log_message(f"Error setting up tabs: {str(e)}")
        return False


def migrate_tabs(main_window): #vers 2
    """Migrate existing tabs from old system"""
    try:
        tab_count = main_window.main_tab_widget.count()
        main_window.log_message(f"Migrating {tab_count} tabs...")

        migrated = 0

        for i in range(tab_count):
            tab_widget = main_window.main_tab_widget.widget(i)
            if not tab_widget:
                continue

            if hasattr(main_window, 'open_files') and i in main_window.open_files:
                file_info = main_window.open_files[i]

                tab_widget.file_path = file_info.get('file_path')
                tab_widget.file_object = file_info.get('file_object')
                tab_widget.file_type = file_info.get('type', 'NONE')
                tab_widget.tab_name = file_info.get('tab_name', 'Unknown')
            else:
                tab_widget.file_path = None
                tab_widget.file_object = None
                tab_widget.file_type = 'NONE'
                tab_widget.tab_name = main_window.main_tab_widget.tabText(i)

            table = get_tab_table(tab_widget)
            if table:
                tab_widget.table_ref = table

            tab_widget.tab_ready = True
            migrated += 1

        if hasattr(main_window, 'open_files'):
            main_window.open_files_backup = main_window.open_files.copy()
            main_window.open_files = {}
            main_window.log_message("Old open_files disabled")

        main_window.log_message(f"Migrated {migrated}/{tab_count} tabs")

        current_index = main_window.main_tab_widget.currentIndex()
        update_references(main_window, current_index)

        return True

    except Exception as e:
        main_window.log_message(f"Migration error: {str(e)}")
        return False


def get_current_active_tab_info(main_window) -> Dict[str, Any]: #vers 1
    """Get comprehensive info about currently active tab"""
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
        
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return tab_info
        
        tab_info['tab_index'] = current_index
        
        current_tab = main_window.main_tab_widget.currentWidget()
        if not current_tab:
            return tab_info
        
        table_widget = None
        if hasattr(current_tab, 'table'):
            table_widget = current_tab.table
        elif hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table_widget = main_window.gui_layout.table
        
        tab_info['table_widget'] = table_widget
        
        file_object, file_type = get_tab_file_data(main_window, current_index)
        tab_info['file_object'] = file_object
        tab_info['file_type'] = file_type
        
        if table_widget:
            selected_entries = get_selected_entries_from_table(table_widget, file_object)
            tab_info['selected_entries'] = selected_entries
        
        tab_info['tab_valid'] = file_object is not None
        
        return tab_info
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error getting tab info: {str(e)}")
        return tab_info


def get_current_file_from_active_tab(main_window) -> Tuple[Optional[Any], str]: #vers 1
    """Get current file object and type from active tab"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return None, 'NONE'
        
        return get_tab_file_data(main_window, current_index)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error getting current file from tab: {str(e)}")
        return None, 'NONE'


def get_current_file_type_from_tab(main_window) -> str: #vers 1
    """Get file type from currently active tab"""
    try:
        _, file_type = get_current_file_from_active_tab(main_window)
        return file_type
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error getting file type from tab: {str(e)}")
        return 'NONE'


def get_selected_entries_from_active_tab(main_window) -> List[Any]: #vers 1
    """Get selected entries from currently active tab's table"""
    try:
        tab_info = get_current_active_tab_info(main_window)
        return tab_info.get('selected_entries', [])
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error getting selected entries from tab: {str(e)}")
        return []


def get_tab_file_data(main_window, tab_index: int) -> Tuple[Optional[Any], str]: #vers 3
    """Get file object and type from specific tab"""
    try:
        if tab_index < 0 or tab_index >= main_window.main_tab_widget.count():
            return None, 'NONE'

        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return None, 'NONE'

        if hasattr(tab_widget, 'tab_ready') and tab_widget.tab_ready:
            file_object = getattr(tab_widget, 'file_object', None)
            file_type = getattr(tab_widget, 'file_type', 'NONE')
            return file_object, file_type

        if hasattr(tab_widget, 'img_file') and tab_widget.img_file:
            return tab_widget.img_file, 'IMG'

        if hasattr(tab_widget, 'col_file') and tab_widget.col_file:
            return tab_widget.col_file, 'COL'

        if tab_index == main_window.main_tab_widget.currentIndex():
            if hasattr(main_window, 'current_img') and main_window.current_img:
                return main_window.current_img, 'IMG'
            if hasattr(main_window, 'current_col') and main_window.current_col:
                return main_window.current_col, 'COL'
            if hasattr(main_window, 'current_txd') and main_window.current_txd:
                return main_window.current_txd, 'TXD'

        return None, 'NONE'

    except Exception as e:
        return None, 'NONE'


def get_selected_entries_from_table(table_widget, file_object) -> List[Any]: #vers 1
    """Extract selected entries from table widget"""
    try:
        if not table_widget or not file_object:
            return []
        
        selected_entries = []
        selected_rows = set()
        
        for item in table_widget.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return []
        
        if hasattr(file_object, 'entries'):
            for row in selected_rows:
                if row < len(file_object.entries):
                    selected_entries.append(file_object.entries[row])
        
        elif hasattr(file_object, 'models'):
            for row in selected_rows:
                if row < len(file_object.models):
                    selected_entries.append(file_object.models[row])
        
        return selected_entries
        
    except Exception as e:
        return []


def ensure_tab_references_valid(main_window) -> bool: #vers 1
    """Ensure main window references match current active tab"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return False
        
        file_object, file_type = get_tab_file_data(main_window, current_index)
        
        if not file_object or file_type == 'NONE':
            return False
        
        if file_type == 'IMG':
            main_window.current_img = file_object
            main_window.current_col = None
            main_window.current_txd = None
        elif file_type == 'COL':
            main_window.current_col = file_object
            main_window.current_img = None
            main_window.current_txd = None
        elif file_type == 'TXD':
            main_window.current_txd = file_object
            main_window.current_img = None
            main_window.current_col = None
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error ensuring tab references: {str(e)}")
        return False


def refresh_current_tab_data(main_window) -> bool: #vers 1
    """Force refresh of current tab's data and references"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Refreshing tab data for tab {current_index}")
        
        success = ensure_tab_references_valid(main_window)
        
        if not success:
            file_object, file_type = get_tab_file_data(main_window, current_index)
            if file_object and file_type != 'NONE':
                if file_type == 'IMG':
                    main_window.current_img = file_object
                    main_window.current_col = None
                    main_window.current_txd = None
                    success = True
                elif file_type == 'COL':
                    main_window.current_col = file_object  
                    main_window.current_img = None
                    main_window.current_txd = None
                    success = True
                elif file_type == 'TXD':
                    main_window.current_txd = file_object
                    main_window.current_img = None
                    main_window.current_col = None
                    success = True
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Tab refresh result: {'Success' if success else 'Failed'}")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error refreshing tab data: {str(e)}")
        return False


def validate_tab_before_operation(main_window, operation_name: str = "operation") -> bool: #vers 2
    """Validate tab state before performing any file operation"""
    try:
        if not hasattr(main_window, 'main_tab_widget'):
            QMessageBox.warning(main_window, "No Tabs", 
                f"Cannot perform {operation_name}: No tab system available.")
            return False
        
        current_index = main_window.main_tab_widget.currentIndex()
        
        if current_index == -1:
            QMessageBox.warning(main_window, "No Active Tab", 
                f"Cannot perform {operation_name}: No tab is currently active.")
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type == 'NONE':
            if hasattr(main_window, 'current_img') and main_window.current_img:
                file_object = main_window.current_img
                file_type = 'IMG'
            elif hasattr(main_window, 'current_col') and main_window.current_col:
                file_object = main_window.current_col
                file_type = 'COL'
            elif hasattr(main_window, 'current_txd') and main_window.current_txd:
                file_object = main_window.current_txd
                file_type = 'TXD'
        
        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
            main_window.current_col = None
            main_window.current_txd = None
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
            main_window.current_img = None
            main_window.current_txd = None
        elif file_type == 'TXD' and file_object:
            main_window.current_txd = file_object
            main_window.current_img = None
            main_window.current_col = None
        
        if file_type == 'NONE' or not file_object:
            QMessageBox.warning(main_window, "No File", 
                f"Cannot perform {operation_name}: Please open an IMG, COL, or TXD file first.")
            return False
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Tab validation error for {operation_name}: {str(e)}")
        return False


def get_active_tab_index(main_window) -> int: #vers 1
    """Get index of currently active tab"""
    try:
        if hasattr(main_window, 'main_tab_widget'):
            return main_window.main_tab_widget.currentIndex()
        return -1
        
    except Exception:
        return -1


def integrate_tab_system(main_window) -> bool: #vers 1
    """Integrate complete tab system into main window"""
    try:
        setup_tab_system(main_window)
        
        main_window.get_current_active_tab_info = lambda: get_current_active_tab_info(main_window)
        main_window.get_current_file_from_active_tab = lambda: get_current_file_from_active_tab(main_window)
        main_window.get_current_file_type_from_tab = lambda: get_current_file_type_from_tab(main_window)
        main_window.get_selected_entries_from_active_tab = lambda: get_selected_entries_from_active_tab(main_window)
        main_window.ensure_tab_references_valid = lambda: ensure_tab_references_valid(main_window)
        main_window.refresh_current_tab_data = lambda: refresh_current_tab_data(main_window)
        main_window.validate_tab_before_operation = lambda op="operation": validate_tab_before_operation(main_window, op)
        main_window.get_active_tab_index = lambda: get_active_tab_index(main_window)
        
        main_window.get_current_file_type = lambda: get_current_file_type_from_tab(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries_from_active_tab(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Complete tab system integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error integrating tab system: {str(e)}")
        return False


__all__ = [
    'clear_tab',
    'close_tab',
    'create_tab',
    'ensure_tab_references_valid',
    'get_active_tab_index',
    'get_current_active_tab_info',
    'get_current_file_from_active_tab', 
    'get_current_file_type_from_tab',
    'get_selected_entries_from_active_tab',
    'get_selected_entries_from_table',
    'get_tab_data',
    'get_tab_file_data',
    'get_tab_table',
    'integrate_tab_system',
    'migrate_tabs',
    'refresh_current_tab_data',
    'setup_tab_system',
    'switch_tab',
    'update_references',
    'validate_tab_before_operation'
]
