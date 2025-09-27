#this belongs in methods/tab_functions.py - Version: 3
# X-Seti - September27 2025 - IMG Factory 1.5 - Tab System with TXD Support

"""
Tab System - Each tab stores its own data
Supports IMG, COL, and TXD files - NO reindexing
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget
from typing import Optional, Tuple, Any

##Methods list -
# clear_tab
# close_tab
# create_tab
# get_tab_data
# get_tab_table
# migrate_tabs
# setup_tab_system
# switch_tab
# update_references


def create_tab(main_window, file_path=None, file_type=None, file_object=None): #vers 4
    """Create tab - stores ALL data on tab widget itself"""
    try:
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # CRITICAL: Create NEW GUI components for this tab
        # Don't reuse existing widgets
        main_window.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Get the NEW table widget created for THIS tab
        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            # Make sure we get the LAST table (newest one created)
            tab_widget.table_ref = tables[-1]  # Changed from [0] to [-1]
        else:
            main_window.log_message("No table found in new tab")
            tab_widget.table_ref = None

        tab_widget.file_path = file_path
        tab_widget.file_type = file_type or 'NONE'
        tab_widget.file_object = file_object
        tab_widget.tab_ready = True

        if file_path:
            import os
            file_name = os.path.basename(file_path)

            if file_name.lower().endswith('.img'):
                file_name = file_name[:-4]
                icon = "📦"
            elif file_name.lower().endswith('.col'):
                file_name = file_name[:-4]
                icon = "🛡️"
            elif file_name.lower().endswith('.txd'):
                file_name = file_name[:-4]
                icon = "🖼️"
            else:
                icon = "📄"

            tab_name = f"{icon} {file_name}"
        else:
            tab_name = "📂 No File"

        tab_widget.tab_name = tab_name

        # Add tab and immediately set its text to ensure it's correct
        new_index = main_window.main_tab_widget.addTab(tab_widget, tab_name)
        main_window.main_tab_widget.setTabText(new_index, tab_name)  # Force set name
        main_window.main_tab_widget.setCurrentIndex(new_index)

        main_window.log_message(f"Tab created at index {new_index}: {tab_name}")
        return new_index

    except Exception as e:
        main_window.log_message(f"Error creating tab: {str(e)}")
        return None

def get_tab_data(tab_widget) -> Tuple[Optional[Any], str, Optional[Any]]: #vers 1
    """Get file data from tab widget

    Returns:
        (file_object, file_type, table_widget)
    """
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
    """Close tab - Let currentChanged signal handle switching"""
    try:
        tab_count = main_window.main_tab_widget.count()

        if tab_count <= 1:
            clear_tab(main_window, 0)
            return

        tab_widget = main_window.main_tab_widget.widget(tab_index)
        tab_name = getattr(tab_widget, 'tab_name', 'Unknown')

        main_window.main_tab_widget.removeTab(tab_index)
        main_window.log_message(f"Closed tab: {tab_name}")

        # Signal will trigger switch_tab automatically

    except Exception as e:
        main_window.log_message(f"Error closing tab: {str(e)}")


def clear_tab(main_window, tab_index): #vers 2
    """Clear tab contents"""
    try:
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return

        tab_widget.file_object = None
        tab_widget.file_type = 'NONE'
        tab_widget.file_path = None
        tab_widget.tab_name = "📂 No File"

        if hasattr(tab_widget, 'table_ref') and tab_widget.table_ref:
            tab_widget.table_ref.setRowCount(0)

        main_window.main_tab_widget.setTabText(tab_index, "📂 No File")

        if tab_index == main_window.main_tab_widget.currentIndex():
            main_window.current_img = None
            main_window.current_col = None
            main_window.current_txd = None
            main_window._update_ui_for_no_img()

        main_window.log_message("Tab cleared")

    except Exception as e:
        main_window.log_message(f"Error clearing tab: {str(e)}")


def switch_tab(main_window, tab_index): #vers 4
    """Handle tab switching - updates references AND TXD Workshop"""
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

        # DEBUG: Check if workshop exists
        if hasattr(main_window, 'txd_workshop'):
            main_window.log_message(f"TXD Workshop found: {main_window.txd_workshop}")

            if main_window.txd_workshop and main_window.txd_workshop.isVisible():
                tab_widget = main_window.main_tab_widget.widget(tab_index)
                file_path = getattr(tab_widget, 'file_path', None)

                main_window.log_message(f"Tab file path: {file_path}")

                if file_path:
                    if file_path.lower().endswith('.txd'):
                        main_window.log_message("Loading TXD in workshop")
                        main_window.txd_workshop.open_txd_file(file_path)
                    elif file_path.lower().endswith('.img'):
                        main_window.log_message("Loading IMG in workshop")
                        main_window.txd_workshop.load_from_img_archive(file_path)
        else:
            main_window.log_message("No txd_workshop attribute found")

    except Exception as e:
        main_window.log_message(f"Error switching tab: {str(e)}")


def setup_tab_system(main_window): #vers 3
    """Setup tab system - connect signals"""
    try:
        main_window.log_message("Setting up tab system...")

        try:
            main_window.main_tab_widget.currentChanged.disconnect()
            main_window.main_tab_widget.tabCloseRequested.disconnect()
        except:
            pass

        main_window.main_tab_widget.currentChanged.connect(
            lambda index: switch_tab(main_window, index)
        )
        main_window.main_tab_widget.tabCloseRequested.connect(
            lambda index: close_tab(main_window, index)
        )

        main_window.create_tab = lambda fp=None, ft=None, fo=None: create_tab(main_window, fp, ft, fo)
        main_window.close_tab = lambda idx: close_tab(main_window, idx)
        main_window.clear_tab = lambda idx: clear_tab(main_window, idx)
        main_window.update_references = lambda idx: update_references(main_window, idx)

        main_window.log_message("Tab system active")
        main_window.log_message("  No reindexing")
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


__all__ = [
    'clear_tab',
    'close_tab',
    'create_tab',
    'get_tab_data',
    'get_tab_table',
    'migrate_tabs',
    'setup_tab_system',
    'switch_tab',
    'update_references'
]
