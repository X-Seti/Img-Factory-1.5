#this belongs in core/robust_tab_system.py - Version: 2
# X-Seti - August10 2025 - IMG Factory 1.5 - FIXED ROBUST TAB DATA SYSTEM

"""
FIXED ROBUST TAB DATA PRESERVATION SYSTEM
Handles N tabs correctly - preserves data by widget position, not file object
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget

##Methods list -
# create_tab_with_persistent_data
# get_tab_table_widget
# preserve_all_tab_data_by_position
# restore_all_tab_data_by_position
# update_tab_manager_references
# validate_tab_data_integrity
# _reindex_open_files_robust_fixed
# patch_close_manager_for_robust_tabs

def create_tab_with_persistent_data(main_window, tab_name="📁 No File"): #vers 1
    """Create new tab with persistent data storage and dedicated table widget"""
    try:
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create GUI components for this tab - EACH TAB GETS ITS OWN
        main_window.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Get the table widget that was just created for THIS tab
        tab_table = get_tab_table_widget(tab_widget)
        
        if tab_table:
            # Store table reference with the tab widget for direct access
            tab_widget.tab_table_widget = tab_table
            tab_widget.tab_data_preserved = True
            
            main_window.log_message(f"✅ Tab created with dedicated table widget")
        else:
            main_window.log_message(f"⚠️ Tab created but no table widget found")

        # Add tab to main widget
        new_index = main_window.main_tab_widget.addTab(tab_widget, tab_name)
        main_window.main_tab_widget.setCurrentIndex(new_index)

        return new_index

    except Exception as e:
        main_window.log_message(f"❌ Error creating persistent tab: {str(e)}")
        return None


def get_tab_table_widget(tab_widget): #vers 1
    """Get the table widget for a specific tab - DIRECT REFERENCE"""
    try:
        from PyQt6.QtWidgets import QTableWidget
        
        # Check if tab already has stored table reference
        if hasattr(tab_widget, 'tab_table_widget'):
            return tab_widget.tab_table_widget
        
        # Find table widget in this tab
        tables = tab_widget.findChildren(QTableWidget)
        if tables:
            # Store reference for future use
            tab_widget.tab_table_widget = tables[0]
            return tables[0]
        
        return None
        
    except Exception as e:
        print(f"Error getting tab table widget: {str(e)}")
        return None


def preserve_all_tab_data_by_position(main_window, removed_tab_index): #vers 1
    """FIXED: Preserve ALL tab data by WIDGET POSITION before removal"""
    try:
        tab_count = main_window.main_tab_widget.count()
        preserved_data = {}
        
        main_window.log_message(f"💾 Preserving data for {tab_count} tabs before removing tab {removed_tab_index}")
        
        # Preserve data for ALL tabs by their CURRENT widget position
        for widget_position in range(tab_count):
            if widget_position == removed_tab_index:
                main_window.log_message(f"⏭️ Skipping tab {widget_position} (being removed)")
                continue
                
            tab_widget = main_window.main_tab_widget.widget(widget_position)
            if not tab_widget:
                continue
                
            table = get_tab_table_widget(tab_widget)
            if not table:
                continue
                
            # Store table data by WIDGET POSITION, not file index
            table_data = {
                'row_count': table.rowCount(),
                'column_count': table.columnCount(),
                'headers': [table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else f"Col{i}" 
                           for i in range(table.columnCount())],
                'data': []
            }
            
            # Preserve all cell data
            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                table_data['data'].append(row_data)
            
            # Key insight: Store by WIDGET POSITION
            preserved_data[widget_position] = table_data
            
            file_name = "Unknown"
            if widget_position in main_window.open_files:
                file_info = main_window.open_files[widget_position]
                file_name = file_info.get('file_path', 'Unknown')
                
            main_window.log_message(f"💾 Preserved tab {widget_position}: {table_data['row_count']} rows ({file_name})")
        
        # Store preserved data globally, not in file objects
        main_window._preserved_tab_data = preserved_data
        
        return preserved_data
        
    except Exception as e:
        main_window.log_message(f"❌ Error preserving tab data: {str(e)}")
        return {}


def restore_all_tab_data_by_position(main_window): #vers 1
    """FIXED: Restore ALL tab data to correct WIDGET POSITIONS after reindexing"""
    try:
        if not hasattr(main_window, '_preserved_tab_data'):
            main_window.log_message("ℹ️ No preserved data to restore")
            return True
            
        preserved_data = main_window._preserved_tab_data
        tab_count = main_window.main_tab_widget.count()
        
        main_window.log_message(f"🔄 Restoring data to {tab_count} tabs from {len(preserved_data)} preserved datasets")
        
        # Map preserved data to new widget positions
        preserved_positions = sorted(preserved_data.keys())
        new_widget_position = 0
        
        for old_widget_position in preserved_positions:
            if new_widget_position >= tab_count:
                break  # No more tabs to restore to
                
            table_data = preserved_data[old_widget_position]
            
            # Get the tab widget at the NEW position
            tab_widget = main_window.main_tab_widget.widget(new_widget_position)
            if not tab_widget:
                main_window.log_message(f"⚠️ No tab widget at position {new_widget_position}")
                new_widget_position += 1
                continue
                
            table = get_tab_table_widget(tab_widget)
            if not table:
                main_window.log_message(f"⚠️ No table widget at position {new_widget_position}")
                new_widget_position += 1
                continue
            
            # Restore table structure and data
            table.setRowCount(table_data['row_count'])
            table.setColumnCount(table_data['column_count'])
            table.setHorizontalHeaderLabels(table_data['headers'])
            
            # Restore all cell data
            from PyQt6.QtWidgets import QTableWidgetItem
            for row, row_data in enumerate(table_data['data']):
                for col, cell_text in enumerate(row_data):
                    if cell_text:  # Only set non-empty cells
                        table.setItem(row, col, QTableWidgetItem(cell_text))
            
            file_name = "Unknown"
            if new_widget_position in main_window.open_files:
                file_info = main_window.open_files[new_widget_position]
                file_name = file_info.get('file_path', 'Unknown')
                
            main_window.log_message(f"🔄 Restored to tab {new_widget_position}: {table_data['row_count']} rows ({file_name})")
            new_widget_position += 1
        
        # Clean up preserved data
        del main_window._preserved_tab_data
        main_window.log_message("✅ All tab data restored and cleanup complete")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error restoring tab data: {str(e)}")
        return False


def update_tab_manager_references(main_window, current_tab_index): #vers 1
    """Update main window references to point to current tab's widgets"""
    try:
        if current_tab_index == -1:
            return False
            
        current_tab_widget = main_window.main_tab_widget.widget(current_tab_index)
        if not current_tab_widget:
            return False
        
        # Get THIS tab's table widget
        current_table = get_tab_table_widget(current_tab_widget)
        if current_table:
            # Update gui_layout reference to point to CURRENT tab's table
            main_window.gui_layout.table = current_table
            main_window.log_message(f"🎯 GUI references updated to tab {current_tab_index}")
            return True
        else:
            main_window.log_message(f"⚠️ No table widget found in tab {current_tab_index}")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Error updating tab references: {str(e)}")
        return False


def validate_tab_data_integrity(main_window): #vers 1
    """Validate that all tabs have their data intact"""
    try:
        tab_count = main_window.main_tab_widget.count()
        file_count = len(main_window.open_files)
        
        main_window.log_message(f"🔍 Validating {tab_count} tabs, {file_count} files tracked")
        
        integrity_issues = []
        
        for i in range(tab_count):
            tab_widget = main_window.main_tab_widget.widget(i)
            if not tab_widget:
                integrity_issues.append(f"Tab {i}: Widget missing")
                continue
                
            # Check if tab has table widget
            table = get_tab_table_widget(tab_widget)
            if not table:
                integrity_issues.append(f"Tab {i}: No table widget")
                continue
                
            # Check if tab has file data
            if i in main_window.open_files:
                file_info = main_window.open_files[i]
                file_path = file_info.get('file_path', 'Unknown')
                row_count = table.rowCount()
                
                if row_count == 0 and file_info.get('file_object'):
                    integrity_issues.append(f"Tab {i}: File loaded but table empty ({file_path})")
                else:
                    main_window.log_message(f"✅ Tab {i}: {row_count} rows ({file_path})")
            else:
                # Empty tab - should have 0 rows
                if table.rowCount() > 0:
                    integrity_issues.append(f"Tab {i}: Empty tab but has {table.rowCount()} rows")
                
        if integrity_issues:
            main_window.log_message(f"⚠️ Integrity issues found:")
            for issue in integrity_issues:
                main_window.log_message(f"   {issue}")
            return False
        else:
            main_window.log_message(f"✅ All tabs have data integrity")
            return True
            
    except Exception as e:
        main_window.log_message(f"❌ Error validating tab integrity: {str(e)}")
        return False


def _reindex_open_files_robust_fixed(close_manager, removed_index): #vers 2
    """FIXED: Robust reindexing that handles N tabs correctly"""
    try:
        if not hasattr(close_manager.main_window, 'open_files'):
            return
            
        close_manager.log_message(f"🔄 FIXED robust reindexing: removing tab {removed_index}")
        
        # STEP 1: Preserve ALL tab data by widget position BEFORE any changes
        preserve_all_tab_data_by_position(close_manager.main_window, removed_index)
        
        # STEP 2: Reindex open_files dictionary (same logic as before)
        new_open_files = {}
        sorted_items = sorted(close_manager.main_window.open_files.items())
        
        new_index = 0
        for old_index, file_info in sorted_items:
            if old_index == removed_index:
                close_manager.log_message(f"⏭️ Skipping removed tab {old_index}: {file_info.get('file_path', 'Unknown')}")
                continue
                
            new_open_files[new_index] = file_info
            close_manager.log_message(f"📁 Tab {old_index} → Tab {new_index}: {file_info.get('tab_name', 'Unknown')}")
            new_index += 1
        
        close_manager.main_window.open_files = new_open_files
        
        # STEP 3: Restore ALL tab data to correct widget positions
        restore_all_tab_data_by_position(close_manager.main_window)
        
        close_manager.log_message("✅ FIXED robust reindexing complete")
        
        # STEP 4: Update current tab references
        current_index = close_manager.main_window.main_tab_widget.currentIndex()
        if hasattr(close_manager.main_window, 'update_tab_manager_references'):
            close_manager.main_window.update_tab_manager_references(current_index)
        
    except Exception as e:
        close_manager.log_message(f"❌ Error in fixed robust reindexing: {str(e)}")


def patch_close_manager_for_robust_tabs(main_window): #vers 2
    """Patch existing close manager to use FIXED robust tab system"""
    try:
        if hasattr(main_window, 'close_manager'):
            # Replace the reindex method with FIXED robust version
            original_reindex = main_window.close_manager._reindex_open_files
            
            def fixed_robust_reindex_wrapper(removed_index):
                return _reindex_open_files_robust_fixed(main_window.close_manager, removed_index)
            
            main_window.close_manager._reindex_open_files = fixed_robust_reindex_wrapper
            main_window.log_message("✅ Close manager patched with FIXED robust tabs")
            return True
        else:
            main_window.log_message("❌ No close manager found to patch")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Error patching close manager: {str(e)}")
        return False


# INTEGRATION FUNCTIONS

def install_robust_tab_system(main_window): #vers 2
    """Install FIXED robust tab system methods on main window"""
    try:
        # Install methods
        main_window.create_tab_with_persistent_data = lambda tab_name="📁 No File": create_tab_with_persistent_data(main_window, tab_name)
        main_window.preserve_all_tab_data_by_position = lambda removed_index: preserve_all_tab_data_by_position(main_window, removed_index)
        main_window.restore_all_tab_data_by_position = lambda: restore_all_tab_data_by_position(main_window)
        main_window.update_tab_manager_references = lambda tab_index: update_tab_manager_references(main_window, tab_index)
        main_window.validate_tab_data_integrity = lambda: validate_tab_data_integrity(main_window)
        
        main_window.log_message("✅ FIXED robust tab system installed")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error installing robust tab system: {str(e)}")
        return False


__all__ = [
    'create_tab_with_persistent_data',
    'get_tab_table_widget', 
    'preserve_all_tab_data_by_position',
    'restore_all_tab_data_by_position',
    'update_tab_manager_references',
    'validate_tab_data_integrity',
    'install_robust_tab_system',
    'patch_close_manager_for_robust_tabs',
    '_reindex_open_files_robust_fixed'
]