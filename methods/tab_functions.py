#this belongs in methods/tab_functions.py - Version: 1
# X-Seti - September25 2025 - IMG Factory 1.5 - Tab System

"""
Tab System - Each tab stores its own data
No reindexing, no dictionary confusion
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget
from typing import Optional, Tuple, Any

##Methods list -
# create_tab
# get_tab_data
# get_tab_table
# update_references
# close_tab
# clear_tab
# switch_tab
# setup_tab_system
# migrate_tabs

def create_tab(main_window, file_path=None, file_type=None, file_object=None): #vers 1
    """Create tab - stores ALL data on tab widget itself"""
    try:
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create GUI components for this tab
        main_window.gui_layout.create_main_ui_with_splitters(tab_layout)
        
        # Get table widget for this tab and store reference
        from PyQt6.QtWidgets import QTableWidget
        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            tab_widget.table_ref = tables[0]
        else:
            main_window.log_message("⚠️ No table found in new tab")
            tab_widget.table_ref = None
        
        # Store ALL file data on tab widget
        tab_widget.file_path = file_path
        tab_widget.file_type = file_type or 'NONE'
        tab_widget.file_object = file_object
        tab_widget.tab_ready = True
        
        # Determine tab name
        if file_path:
            import os
            file_name = os.path.basename(file_path)
            if file_name.lower().endswith('.img'):
                file_name = file_name[:-4]
                icon = "📁"
            elif file_name.lower().endswith('.col'):
                file_name = file_name[:-4]
                icon = "🛡️"
            else:
                icon = "📄"
            tab_name = f"{icon} {file_name}"
        else:
            tab_name = "📁 No File"
        
        tab_widget.tab_name = tab_name
        
        # Add tab
        new_index = main_window.main_tab_widget.addTab(tab_widget, tab_name)
        main_window.main_tab_widget.setCurrentIndex(new_index)
        
        main_window.log_message(f"✅ Tab created: {tab_name}")
        return new_index
        
    except Exception as e:
        main_window.log_message(f"❌ Error creating tab: {str(e)}")
        return None


def get_tab_data(tab_widget) -> Tuple[Optional[Any], str, Optional[Any]]: #vers 1
    """Get file data from tab widget - NO external lookups
    
    Returns:
        (file_object, file_type, table_widget)
    """
    try:
        if not tab_widget:
            return None, 'NONE', None
        
        # Get data stored on tab
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
        
        # Find and store reference
        from PyQt6.QtWidgets import QTableWidget
        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            tab_widget.table_ref = tables[0]
            return tables[0]
        
        return None
        
    except Exception as e:
        return None


def update_references(main_window, tab_index): #vers 1
    """Update main window references to current tab's data"""
    try:
        if tab_index == -1:
            # No tabs
            main_window.current_img = None
            main_window.current_col = None
            if hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table = None
            return True
        
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return False
        
        # Get data from tab
        file_object, file_type, table = get_tab_data(tab_widget)
        
        # Update gui_layout.table reference
        if table:
            main_window.gui_layout.table = table
        
        # Update current file references
        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
            main_window.current_col = None
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
            main_window.current_img = None
        else:
            # Empty tab
            main_window.current_img = None
            main_window.current_col = None
        
        main_window.log_message(f"🎯 References updated to tab {tab_index} ({file_type})")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating references: {str(e)}")
        return False


def close_tab(main_window, tab_index): #vers 1
    """Close tab - NO reindexing needed"""
    try:
        tab_count = main_window.main_tab_widget.count()
        
        if tab_count <= 1:
            # Last tab - just clear it
            clear_tab(main_window, 0)
            return
        
        # Get info before closing
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        tab_name = getattr(tab_widget, 'tab_name', 'Unknown')
        
        # Simply remove the tab
        main_window.main_tab_widget.removeTab(tab_index)
        
        main_window.log_message(f"✅ Closed tab: {tab_name}")
        
        # Update references to current tab
        current_index = main_window.main_tab_widget.currentIndex()
        update_references(main_window, current_index)
        
    except Exception as e:
        main_window.log_message(f"❌ Error closing tab: {str(e)}")


def clear_tab(main_window, tab_index): #vers 1
    """Clear tab contents - leave empty tab"""
    try:
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return
        
        # Clear file data
        tab_widget.file_object = None
        tab_widget.file_type = 'NONE'
        tab_widget.file_path = None
        tab_widget.tab_name = "📁 No File"
        
        # Clear table
        if hasattr(tab_widget, 'table_ref') and tab_widget.table_ref:
            tab_widget.table_ref.setRowCount(0)
        
        # Update tab name
        main_window.main_tab_widget.setTabText(tab_index, "📁 No File")
        
        # Update main window references
        if tab_index == main_window.main_tab_widget.currentIndex():
            main_window.current_img = None
            main_window.current_col = None
            main_window._update_ui_for_no_img()
        
        main_window.log_message("✅ Tab cleared")
        
    except Exception as e:
        main_window.log_message(f"❌ Error clearing tab: {str(e)}")


def switch_tab(main_window, tab_index): #vers 1
    """Handle tab switching - updates references only"""
    try:
        if tab_index == -1:
            main_window.current_img = None
            main_window.current_col = None
            if hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table = None
            return
        
        main_window.log_message(f"🔄 Switching to tab: {tab_index}")
        
        # Simply update main window references
        update_references(main_window, tab_index)
        
    except Exception as e:
        main_window.log_message(f"❌ Error switching tab: {str(e)}")


def setup_tab_system(main_window): #vers 1
    """Setup tab system - remove old handlers"""
    try:
        main_window.log_message("🚀 Setting up tab system...")
        
        # Disconnect old handlers
        try:
            main_window.main_tab_widget.currentChanged.disconnect()
            main_window.main_tab_widget.tabCloseRequested.disconnect()
        except:
            pass  # No handlers to disconnect
        
        # Connect new handlers
        main_window.main_tab_widget.currentChanged.connect(
            lambda index: switch_tab(main_window, index)
        )
        main_window.main_tab_widget.tabCloseRequested.connect(
            lambda index: close_tab(main_window, index)
        )
        
        # Install methods on main window
        main_window.create_tab = lambda fp=None, ft=None, fo=None: create_tab(main_window, fp, ft, fo)
        main_window.close_tab = lambda idx: close_tab(main_window, idx)
        main_window.clear_tab = lambda idx: clear_tab(main_window, idx)
        main_window.update_references = lambda idx: update_references(main_window, idx)
        
        main_window.log_message("✅ Tab system active")
        main_window.log_message("   • No reindexing")
        main_window.log_message("   • Each tab stores own data")
        main_window.log_message("   • Unlimited tabs supported")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up tabs: {str(e)}")
        return False


def migrate_tabs(main_window): #vers 1
    """Migrate existing tabs from old system"""
    try:
        tab_count = main_window.main_tab_widget.count()
        main_window.log_message(f"🔄 Migrating {tab_count} tabs...")
        
        migrated = 0
        
        for i in range(tab_count):
            tab_widget = main_window.main_tab_widget.widget(i)
            if not tab_widget:
                continue
            
            # Get data from old open_files if available
            if hasattr(main_window, 'open_files') and i in main_window.open_files:
                file_info = main_window.open_files[i]
                
                # Store on tab widget
                tab_widget.file_path = file_info.get('file_path')
                tab_widget.file_object = file_info.get('file_object')
                tab_widget.file_type = file_info.get('type', 'NONE')
                tab_widget.tab_name = file_info.get('tab_name', 'Unknown')
            else:
                # Empty tab
                tab_widget.file_path = None
                tab_widget.file_object = None
                tab_widget.file_type = 'NONE'
                tab_widget.tab_name = main_window.main_tab_widget.tabText(i)
            
            # Get and store table reference
            table = get_tab_table(tab_widget)
            if table:
                tab_widget.table_ref = table
            
            tab_widget.tab_ready = True
            migrated += 1
        
        # Disable old open_files system
        if hasattr(main_window, 'open_files'):
            main_window.open_files_backup = main_window.open_files.copy()
            main_window.open_files = {}  # Clear it
            main_window.log_message("🗑️ Old open_files disabled")
        
        main_window.log_message(f"✅ Migrated {migrated}/{tab_count} tabs")
        
        # Update current tab references
        current_index = main_window.main_tab_widget.currentIndex()
        update_references(main_window, current_index)
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Migration error: {str(e)}")
        return False


__all__ = [
    'create_tab',
    'get_tab_data',
    'get_tab_table',
    'update_references',
    'close_tab',
    'clear_tab',
    'switch_tab',
    'setup_tab_system',
    'migrate_tabs'
]
