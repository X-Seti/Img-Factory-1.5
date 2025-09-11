#this belongs in core/independent_tab_system.py - Version: 1
# X-Seti - August10 2025 - IMG Factory 1.5 - Self-contained tabs

"""
Each tab is completely self-contained. Removing tabs doesn't affect others.
Scales to unlimited tabs with zero memory overhead.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget

##Methods list -
# create_independent_tab
# get_tab_table_direct
# make_tab_completely_independent  
# update_current_tab_reference_only
# close_tab_without_reindexing
# setup_independent_tab_system

def create_independent_tab(main_window, file_path=None, file_object=None, file_type=None): #vers 1
    """Create completely independent tab - no shared references"""
    try:
        # Create unique tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create dedicated GUI components for THIS tab only
        main_window.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Get this tab's table widget and make it independent
        tab_table = get_tab_table_direct(tab_widget)
        if tab_table:
            # Store everything directly on the tab widget - NO EXTERNAL REFERENCES
            tab_widget.dedicated_table = tab_table
            tab_widget.file_path = file_path
            tab_widget.file_object = file_object 
            tab_widget.file_type = file_type
            tab_widget.is_independent = True
            
            # Set tab name
            if file_path:
                file_name = file_path.split('/')[-1].split('\\')[-1]  # Handle both / and \
                if file_name.lower().endswith(('.img', '.col')):
                    file_name = file_name[:-4]
                icon = "📁" if file_type == "IMG" else "🛡️" if file_type == "COL" else "📄"
                tab_name = f"{icon} {file_name}"
            else:
                tab_name = "📁 No File"
                
            tab_widget.tab_name = tab_name
        else:
            main_window.log_message("⚠️ Could not create table widget for independent tab")
            return None

        # Add tab WITHOUT updating open_files tracking
        tab_index = main_window.main_tab_widget.addTab(tab_widget, tab_name)
        main_window.main_tab_widget.setCurrentIndex(tab_index)
        
        main_window.log_message(f"✅ Independent tab created: {tab_name}")
        return tab_index

    except Exception as e:
        main_window.log_message(f"❌ Error creating independent tab: {str(e)}")
        return None


def get_tab_table_direct(tab_widget): #vers 1
    """Get table widget directly from tab - no external lookups"""
    try:
        from PyQt6.QtWidgets import QTableWidget
        
        # Check for stored reference first
        if hasattr(tab_widget, 'dedicated_table'):
            return tab_widget.dedicated_table
        
        # Find table in this tab widget
        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            tab_widget.dedicated_table = tables[0]
            return tables[0]
        
        return None
        
    except Exception as e:
        return None


def make_tab_completely_independent(main_window, tab_index): #vers 1
    """Make existing tab completely independent - migrate from old system"""
    try:
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        if not tab_widget:
            return False
            
        # Get file info from old system if it exists
        file_info = main_window.open_files.get(tab_index, {})
        
        # Store everything directly on tab widget
        tab_widget.file_path = file_info.get('file_path')
        tab_widget.file_object = file_info.get('file_object')
        tab_widget.file_type = file_info.get('type', 'Unknown')
        tab_widget.tab_name = file_info.get('tab_name', 'Unknown')
        
        # Get table widget and store reference
        table = get_tab_table_direct(tab_widget)
        if table:
            tab_widget.dedicated_table = table
            tab_widget.is_independent = True
            
            main_window.log_message(f"✅ Tab {tab_index} made independent")
            return True
        else:
            main_window.log_message(f"⚠️ Could not make tab {tab_index} independent - no table")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Error making tab independent: {str(e)}")
        return False


def update_current_tab_reference_only(main_window, tab_index): #vers 1
    """Update ONLY current tab reference - don't touch other tabs"""
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
            
        # Update gui_layout.table to point to THIS tab's table only
        if hasattr(tab_widget, 'dedicated_table'):
            main_window.gui_layout.table = tab_widget.dedicated_table
        else:
            # Fallback - find table in this tab
            table = get_tab_table_direct(tab_widget)
            if table:
                main_window.gui_layout.table = table
            
        # Update current file references
        if hasattr(tab_widget, 'file_object') and tab_widget.file_object:
            if hasattr(tab_widget, 'file_type'):
                if tab_widget.file_type == 'IMG':
                    main_window.current_img = tab_widget.file_object
                    main_window.current_col = None
                elif tab_widget.file_type == 'COL':
                    main_window.current_col = tab_widget.file_object  
                    main_window.current_img = None
        else:
            # Empty tab
            main_window.current_img = None
            main_window.current_col = None
            
        main_window.log_message(f"🎯 Current tab reference updated to: {tab_index}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating current tab reference: {str(e)}")
        return False


def close_tab_without_reindexing(main_window, tab_index): #vers 1
    """Close tab without affecting any other tabs - NO REINDEXING"""
    try:
        tab_count = main_window.main_tab_widget.count()
        
        if tab_count <= 1:
            # Last tab - just clear it
            tab_widget = main_window.main_tab_widget.widget(0)
            if tab_widget:
                # Clear tab data
                tab_widget.file_path = None
                tab_widget.file_object = None
                tab_widget.file_type = None
                tab_widget.tab_name = "📁 No File"
                
                # Clear table
                if hasattr(tab_widget, 'dedicated_table'):
                    tab_widget.dedicated_table.setRowCount(0)
                    
                # Update tab name
                main_window.main_tab_widget.setTabText(0, "📁 No File")
                
            main_window.log_message("✅ Last tab cleared")
            return True
            
        # Get tab info before removal
        tab_widget = main_window.main_tab_widget.widget(tab_index)
        tab_name = "Unknown"
        if tab_widget and hasattr(tab_widget, 'tab_name'):
            tab_name = tab_widget.tab_name
            
        # Remove tab widget - this is ALL we need to do
        main_window.main_tab_widget.removeTab(tab_index)
        
        # Update current tab reference if needed
        current_index = main_window.main_tab_widget.currentIndex()
        update_current_tab_reference_only(main_window, current_index)
        
        main_window.log_message(f"✅ Independent tab closed: {tab_name}")
        main_window.log_message(f"📊 Remaining tabs: {main_window.main_tab_widget.count()}")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error closing independent tab: {str(e)}")
        return False


def setup_independent_tab_system(main_window): #vers 1
    """Setup completely independent tab system"""
    try:
        # Install methods on main window
        main_window.create_independent_tab = lambda file_path=None, file_object=None, file_type=None: create_independent_tab(main_window, file_path, file_object, file_type)
        main_window.make_tab_completely_independent = lambda tab_index: make_tab_completely_independent(main_window, tab_index)
        main_window.update_current_tab_reference_only = lambda tab_index: update_current_tab_reference_only(main_window, tab_index)
        main_window.close_tab_without_reindexing = lambda tab_index: close_tab_without_reindexing(main_window, tab_index)
        
        # Replace tab change handler with independent version
        main_window.main_tab_widget.currentChanged.disconnect()  # Remove old handler
        main_window.main_tab_widget.currentChanged.connect(lambda index: update_current_tab_reference_only(main_window, index))
        
        # Replace close handler with independent version  
        main_window.main_tab_widget.tabCloseRequested.disconnect()  # Remove old handler
        main_window.main_tab_widget.tabCloseRequested.connect(lambda index: close_tab_without_reindexing(main_window, index))
        
        main_window.log_message("✅ Independent tab system active")
        main_window.log_message("🚀 Scales to unlimited tabs with zero overhead")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up independent tab system: {str(e)}")
        return False


def migrate_existing_tabs_to_independent(main_window): #vers 1
    """Migrate existing tabs from old system to independent system"""
    try:
        tab_count = main_window.main_tab_widget.count()
        migrated_count = 0
        
        main_window.log_message(f"🔄 Migrating {tab_count} existing tabs to independent system")
        
        for i in range(tab_count):
            if make_tab_completely_independent(main_window, i):
                migrated_count += 1
                
        # Clear old open_files tracking - no longer needed
        main_window.open_files = {}
        
        main_window.log_message(f"✅ Migrated {migrated_count}/{tab_count} tabs to independent system")
        main_window.log_message("🗑️ Old file tracking system disabled")
        
        return migrated_count == tab_count
        
    except Exception as e:
        main_window.log_message(f"❌ Error migrating tabs: {str(e)}")
        return False


__all__ = [
    'create_independent_tab',
    'get_tab_table_direct',
    'make_tab_completely_independent',
    'update_current_tab_reference_only', 
    'close_tab_without_reindexing',
    'setup_independent_tab_system',
    'migrate_existing_tabs_to_independent'
]
