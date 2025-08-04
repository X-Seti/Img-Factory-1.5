#this belongs in core/close.py - Version: 9
# X-Seti - July31 2025 - IMG Factory 1.5 - Close and Tab Management Functions

"""
IMG Factory Close Functions
Handles all close, tab management, and cleanup operations
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout


##Class IMGCloseManager -
# __init__
# close_current_file
# close_all_tabs
# close_tab
# create_new_tab
# _clear_current_tab
# _clear_all_tables_in_tab
# _reindex_open_files

def close_all_img(main_window): #vers 3
    """Close all IMG files - Wrapper for close_all_tabs"""
    try:
        if hasattr(main_window, 'close_manager') and main_window.close_manager:
            main_window.close_manager.close_all_tabs()
        else:
            main_window.log_message("❌ Close manager not available")
    except Exception as e:
        main_window.log_message(f"❌ Error in close_all_img: {str(e)}")

def close_img_file(main_window): #vers 6
    """Close current file (IMG or COL) - FIXED: No recursive calls"""
    try:
        if hasattr(main_window, 'close_manager') and main_window.close_manager:
            main_window.close_manager.close_current_file()
        else:
            main_window.log_message("❌ Close manager not available")
    except Exception as e:
        main_window.log_message(f"❌ Error in close_img_file: {str(e)}")

def setup_close_manager(main_window): #vers 3
    """Setup close manager for main window"""
    main_window.close_manager = IMGCloseManager(main_window)

    # Connect tab close signal to our manager
    main_window.main_tab_widget.tabCloseRequested.connect(main_window.close_manager.close_tab)

    return main_window.close_manager

def install_close_functions(main_window): #vers 3
    """Install close functions as methods on main window"""
    close_manager = setup_close_manager(main_window)

    # Install methods on main window
    main_window.close_img_file = lambda: close_img_file(main_window)
    main_window.close_all_img = lambda: close_all_img(main_window)
    main_window.close_all_tabs = close_manager.close_all_tabs
    main_window._close_tab = close_manager.close_tab
    main_window._clear_current_tab = close_manager._clear_current_tab
    main_window._create_new_tab = close_manager.create_new_tab
    main_window._reindex_open_files = close_manager._reindex_open_files

    main_window.log_message("✅ Close functions installed")

    return close_manager

class IMGCloseManager:
    """Manages all close operations and tab cleanup for IMG Factory"""
    
    def __init__(self, main_window): #vers 1
        """Initialize with reference to main window"""
        self.main_window = main_window
        self.log_message = main_window.log_message

    def close_current_file(self): #vers 2
        """Close current file (IMG or COL) - FIXED: Remove tab or clear it"""
        try:
            current_index = self.main_window.main_tab_widget.currentIndex()

            # If we have multiple tabs, remove this tab completely
            if self.main_window.main_tab_widget.count() > 1:
                self.close_tab(current_index)
            else:
                # Only one tab left, just clear it
                self._clear_current_tab()

        except Exception as e:
            self.log_message(f"❌ Error closing file: {str(e)}")

    def close_all_tabs(self): #vers 3
        """Close all tabs - Handle both IMG and COL"""
        try:
            tab_count = self.main_window.main_tab_widget.count()
            self.log_message(f"🗂️ Closing all {tab_count} tabs")

            # Close from highest index to lowest to avoid index shifting issues
            for i in range(tab_count - 1, -1, -1):
                if self.main_window.main_tab_widget.count() > 1:
                    self.close_tab(i)
                else:
                    # Last tab - just clear it
                    self._clear_current_tab()
                    break

            # Ensure we have at least one empty tab
            if self.main_window.main_tab_widget.count() == 0:
                self.create_new_tab()

            # CRITICAL FIX: Clear the file window display
            self.main_window.current_img = None
            if hasattr(self.main_window, 'current_col'):
                self.main_window.current_col = None
            self.main_window._update_ui_for_no_img()

            self.log_message("✅ All tabs closed")

        except Exception as e:
            self.log_message(f"❌ Error closing all tabs: {str(e)}")

    def close_tab(self, index): #vers 4
        """Close tab at index - Handle both IMG and COL"""
        if self.main_window.main_tab_widget.count() <= 1:
            # Don't close the last tab, just clear it
            self._clear_current_tab()
            return

        try:
            # Get file info before removal for logging
            file_info = self.main_window.open_files.get(index, {})
            file_path = file_info.get('file_path', 'Unknown file')
            file_type = file_info.get('type', 'Unknown')

            # Clear table data in this tab before removing
            tab_widget = self.main_window.main_tab_widget.widget(index)
            if tab_widget:
                self._clear_all_tables_in_tab(tab_widget)

            # Remove from open files
            if index in self.main_window.open_files:
                del self.main_window.open_files[index]
                self.log_message(f"🗂️ Closing tab {index}: {file_type} - {os.path.basename(file_path)}")

            # Remove tab
            self.main_window.main_tab_widget.removeTab(index)

            # Reindex remaining open files
            self._reindex_open_files(index)

            self.log_message(f"✅ Tab {index} closed")

        except Exception as e:
            self.log_message(f"❌ Error closing tab {index}: {str(e)}")

    def create_new_tab(self): #vers 2
        """Create a new empty tab with proper GUI components"""
        try:
            new_tab = QWidget()
            new_layout = QVBoxLayout(new_tab)
            new_layout.setContentsMargins(0, 0, 0, 0)

            # CRITICAL FIX: Create GUI components for the new tab
            self.main_window.gui_layout.create_main_ui_with_splitters(new_layout)

            # Add the tab
            new_index = self.main_window.main_tab_widget.addTab(new_tab, "📁 No File")
            self.main_window.main_tab_widget.setCurrentIndex(new_index)

            self.log_message(f"✅ Created new tab {new_index} with GUI components")
            return new_index

        except Exception as e:
            self.log_message(f"❌ Error creating new tab: {str(e)}")
            return None

    def _clear_current_tab(self): #vers 1
        """Clear current tab contents"""
        try:
            current_index = self.main_window.main_tab_widget.currentIndex()
            
            # Clear file data
            self.main_window.current_img = None
            if hasattr(self.main_window, 'current_col'):
                self.main_window.current_col = None

            # Remove from open files
            if hasattr(self.main_window, 'open_files') and current_index in self.main_window.open_files:
                del self.main_window.open_files[current_index]

            # Reset tab name
            self.main_window.main_tab_widget.setTabText(current_index, "📁 No File")
            
            # Update UI
            self.main_window._update_ui_for_no_img()
            
            self.log_message("✅ Current tab cleared")

        except Exception as e:
            self.log_message(f"❌ Error clearing current tab: {str(e)}")

    def _clear_all_tables_in_tab(self, tab_widget): #vers 1
        """Clear all table data in a tab widget"""
        try:
            from PyQt6.QtWidgets import QTableWidget
            
            # Find all QTableWidget instances in this tab
            tables = tab_widget.findChildren(QTableWidget)
            for table in tables:
                table.clear()
                table.setRowCount(0)
                
        except Exception as e:
            self.log_message(f"❌ Error clearing tables: {str(e)}")

    def _reindex_open_files(self, removed_index): #vers 1
        """Reindex open_files after tab removal"""
        try:
            if not hasattr(self.main_window, 'open_files'):
                return
                
            new_open_files = {}
            for old_index, file_info in self.main_window.open_files.items():
                if old_index > removed_index:
                    # Shift index down by 1
                    new_index = old_index - 1
                    new_open_files[new_index] = file_info
                elif old_index < removed_index:
                    # Keep same index
                    new_open_files[old_index] = file_info
                # Skip the removed index
            
            self.main_window.open_files = new_open_files
            
        except Exception as e:
            self.log_message(f"❌ Error reindexing files: {str(e)}")

__all__ = [
    'IMGCloseManager',
    'close_img_file',
    'close_all_img',
    'setup_close_manager',
    'install_close_functions'
]
