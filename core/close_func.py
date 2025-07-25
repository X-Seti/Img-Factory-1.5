#this belongs in components/ img_close_functions.py - Version: 1
# X-Seti - July06 2025 - Img Factory 1.5 - Close and Tab Management Functions

#!/usr/bin/env python3
"""
IMG Factory Close Functions
Handles all close, tab management, and cleanup operations
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class IMGCloseManager:
    """Manages all close operations and tab cleanup for IMG Factory"""
    
    def __init__(self, main_window): #vers 1
        """Initialize with reference to main window"""
        self.main_window = main_window
        self.log_message = main_window.log_message

    def _close_img_file(self): #vers 5
        """Close current file (IMG or COL) - UPDATED for both file types"""
        current_index = self.main_window.main_tab_widget.currentIndex()

        # Clear the current file data
        old_img = self.main_window.current_img
        old_col = self.main_window.current_col
        self.main_window.current_img = None
        self.main_window.current_col = None

        # Remove from open_files if exists
        if current_index in self.main_window.open_files:
            file_info = self.main_window.open_files[current_index]
            file_path = file_info.get('file_path', 'Unknown file')
            file_type = file_info.get('type', 'Unknown')
            self.log_message(f"🗂️ Closing {file_type}: {os.path.basename(file_path)}")
            del self.main_window.open_files[current_index]

        # Reset tab name to "No File"
        self.main_window.main_tab_widget.setTabText(current_index, "📁 No File")

        # Update UI for no file state
        self.main_window._update_ui_for_no_img()

        # Log what was closed
        if old_img:
            self.log_message("✅ IMG file closed")
        elif old_col:
            self.log_message("✅ COL file closed")
        else:
            self.log_message("✅ Tab cleared")

    def close_img_file(self): #vers 5
        """Close current IMG/COL file - DIRECT implementation if close_manager fails"""
        try:
            # Try to use close manager first
            if hasattr(self, 'close_manager') and self.close_manager:
                self.close_manager.close_img_file()
                return
        except Exception as e:
            self.log_message(f"❌ Close manager error: {str(e)}")

        # Fallback: Direct implementation
        try:
            current_index = self.main_tab_widget.currentIndex()

            # Log what we're closing
            if hasattr(self, 'current_img') and self.current_img:
                file_path = getattr(self.current_img, 'file_path', 'Unknown IMG')
                self.log_message(f"🗂️ Closing IMG: {os.path.basename(file_path)}")
          #  elif hasattr(self, 'current_col') and self.current_col:
          #      file_path = getattr(self.current_col, 'file_path', 'Unknown #=-COL')
          #      self.log_message(f"🗂️ Closing COL: {os.path.basename(file_path)}")
            else:
                self.log_message("🗂️ Closing current tab")

            # Clear the current file data
            self.current_img = None
            #self.current_col = None

            # Remove from open_files if exists
            if hasattr(self, 'open_files') and current_index in self.open_files:
                del self.open_files[current_index]

            # Reset tab name to "No File"
            if hasattr(self, 'main_tab_widget'):
                self.main_tab_widget.setTabText(current_index, "📁 No File")

            # Update UI for no file state
            self._update_ui_for_no_img()

            self.log_message("✅ File closed successfully")

        except Exception as e:
            error_msg = f"Error closing file: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            # Don't show error dialog, just log it


    def close_all_img(self): #vers 2
        """Close all IMG files - Wrapper for close_all_tabs"""
        try:
            if hasattr(self, 'close_manager') and self.close_manager:
                self.close_manager.close_all_tabs()
            else:
                self.log_message("❌ Close manager not available")
        except Exception as e:
            self.log_message(f"❌ Error in close_all_img: {str(e)}")


    def close_all_tabs(self): #vers 2
        """Close all tabs - UPDATED to handle both IMG and COL"""
        try:
            tab_count = self.main_window.main_tab_widget.count()
            self.log_message(f"🗂️ Closing all {tab_count} tabs")

            # Close from highest index to lowest to avoid index shifting issues
            for i in range(tab_count - 1, -1, -1):
                if self.main_window.main_tab_widget.count() > 1:
                    # Use the working close_tab function
                    self.close_tab(i)
                else:
                    # Last tab - just clear it
                    self._clear_current_tab()
                    break

            # Ensure we have at least one empty tab
            if self.main_window.main_tab_widget.count() == 0:
                self.create_new_tab()

            self.log_message("✅ All tabs closed")

        except Exception as e:
            self.log_message(f"❌ Error closing all tabs: {str(e)}")


    def close_tab(self, index): #vers 4
        """Close tab at index - UPDATED for both IMG and COL"""
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

            # Update open_files dict indices
            self._reindex_open_files()

            # Update current file references based on new current tab
            current_index = self.main_window.main_tab_widget.currentIndex()
            if current_index in self.main_window.open_files:
                file_info = self.main_window.open_files[current_index]
                if file_info['type'] == 'IMG':
                    self.main_window.current_img = file_info['file_object']
                    self.main_window.current_col = None
                elif file_info['type'] == 'COL':
                    self.main_window.current_col = file_info['file_object']
                    self.main_window.current_img = None
            else:
                self.main_window.current_img = None
                self.main_window.current_col = None

            # Update UI for current state
            if hasattr(self.main_window, '_update_ui_for_current_file'):
                self.main_window._update_ui_for_current_file()

        except Exception as e:
            self.log_message(f"❌ Error closing tab {index}: {str(e)}")

    def _clear_current_tab(self): #vers 4
        """Clear current tab - UPDATED for both IMG and COL"""
        current_index = self.main_window.main_tab_widget.currentIndex()

        # Clear table data in current tab
        tab_widget = self.main_window.main_tab_widget.widget(current_index)
        if tab_widget:
            self._clear_all_tables_in_tab(tab_widget)

        # Remove from open_files
        if current_index in self.main_window.open_files:
            file_info = self.main_window.open_files[current_index]
            file_type = file_info.get('type', 'Unknown')
            self.log_message(f"🗂️ Clearing {file_type} from current tab")
            del self.main_window.open_files[current_index]

        # Reset tab name properly
        self.main_window.main_tab_widget.setTabText(current_index, "📁 No File")

        # Clear current file references
        self.main_window.current_img = None
        self.main_window.current_col = None

        # Update UI for no file state
        self.main_window._update_ui_for_no_img()

        self.log_message("🗂️ Tab cleared")


    def _clear_all_tables_in_tab(self, tab_widget): #vers 3
        """Clear ALL table widgets found in a tab (deep search)"""
        try:
            tables_cleared = 0
            
            # Deep recursive search for ALL QTableWidget instances
            def find_and_clear_all_tables(widget):
                nonlocal tables_cleared
                
                # Check if this widget is a QTableWidget
                if hasattr(widget, 'setRowCount') and hasattr(widget, 'columnCount'):
                    if 'QTableWidget' in str(type(widget)):
                        widget.setRowCount(0)
                        tables_cleared += 1
                        return
                
                # Search ALL children recursively
                if hasattr(widget, 'children'):
                    for child in widget.children():
                        if hasattr(child, 'setParent'):  # Is a widget
                            find_and_clear_all_tables(child)
                
                # Also check layout items if it's a layout
                if hasattr(widget, 'count') and hasattr(widget, 'itemAt'):
                    for i in range(widget.count()):
                        item = widget.itemAt(i)
                        if item and item.widget():
                            find_and_clear_all_tables(item.widget())
            
            find_and_clear_all_tables(tab_widget)
            
            if tables_cleared > 0:
                self.log_message(f"🗂️ Cleared {tables_cleared} table(s) in tab")
            else:
                self.log_message(f"⚠️ No tables found to clear in tab")
                
        except Exception as e:
            self.log_message(f"❌ Error clearing tables in tab: {str(e)}")


    def _reindex_open_files(self): #vers 4
        """Reindex open_files dict after tab removal"""
        new_open_files = {}
        for i in range(self.main_window.main_tab_widget.count()):
            # Find matching file in old dict
            for old_index, file_info in self.main_window.open_files.items():
                if self.main_window.main_tab_widget.tabText(i) == file_info.get('tab_name', ''):
                    new_open_files[i] = file_info
                    break
        self.main_window.open_files = new_open_files


    def create_new_tab(self): #vers 4
        """Create new empty tab - FIXED: Use correct method"""
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Use the same method as _create_initial_tab
        self.main_window.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Add tab
        self.main_window.main_tab_widget.addTab(tab_widget, "📁 No File")
        self.main_window.main_tab_widget.setCurrentIndex(self.main_window.main_tab_widget.count() - 1)


    def get_open_file_count(self): #vers 1
        """Get count of open files"""
        return len(self.main_window.open_files)

    def get_tab_count(self): #vers 1
        """Get total tab count"""
        return self.main_window.main_tab_widget.count()

    def is_any_file_open(self): #vers 1
        """Check if any files are currently open"""
        return len(self.main_window.open_files) > 0

    def get_current_tab_file_info(self): #vers 1
        """Get file info for current tab"""
        current_index = self.main_window.main_tab_widget.currentIndex()
        return self.main_window.open_files.get(current_index, None)


# Convenience functions for integration with main window
def setup_close_manager(main_window): #vers 2
    """Setup close manager for main window"""
    main_window.close_manager = IMGCloseManager(main_window)
    
    # Connect tab close signal to our manager
    main_window.main_tab_widget.tabCloseRequested.connect(main_window.close_manager.close_tab)
    
    return main_window.close_manager


def install_close_functions(main_window): #vers 2
    """Install close functions as methods on main window for backward compatibility"""
    close_manager = setup_close_manager(main_window)
    
    # Install methods on main window
    main_window.close_img_file = close_manager.close_img_file
    main_window.close_all_tabs = close_manager.close_all_tabs
    main_window._close_tab = close_manager.close_tab
    main_window._clear_current_tab = close_manager._clear_current_tab
    main_window._create_new_tab = close_manager.create_new_tab
    main_window._reindex_open_files = close_manager._reindex_open_files
    
    main_window.log_message("✅ Close functions installed from components/img_close_functions.py")
    
    return close_manager
