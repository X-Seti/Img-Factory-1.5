#this belongs in core/close.py - Version: 10
# X-Seti - September25 2025 - IMG Factory 1.5 - Close and Tab Management Functions

"""
IMG Factory Close Functions
Handles all close, tab management, and cleanup operations
Uses new tab system - NO reindexing
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout

##Class IMGCloseManager -
# __init__
# close_current_file
# close_all_tabs
# close_tab
# _clear_current_tab
# _clear_all_tables_in_tab

##Functions -
# close_all_img
# close_img_file
# setup_close_manager
# install_close_functions

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
    """Close current file (IMG or COL)"""
    try:
        if hasattr(main_window, 'close_manager') and main_window.close_manager:
            main_window.close_manager.close_current_file()
        else:
            main_window.log_message("❌ Close manager not available")
    except Exception as e:
        main_window.log_message(f"❌ Error in close_img_file: {str(e)}")

def setup_close_manager(main_window): #vers 4
    """Setup close manager for main window - Uses new tab system"""
    main_window.close_manager = IMGCloseManager(main_window)

    # NOTE: Tab close signal now handled by new tab system (tab_functions.py)
    # This is kept for backwards compatibility with other close operations

    return main_window.close_manager

def install_close_functions(main_window): #vers 4
    """Install close functions as methods on main window"""
    close_manager = setup_close_manager(main_window)

    # Install methods on main window
    main_window.close_img_file = lambda: close_img_file(main_window)
    main_window.close_all_img = lambda: close_all_img(main_window)
    main_window.close_all_tabs = close_manager.close_all_tabs
    main_window._clear_current_tab = close_manager._clear_current_tab

    main_window.log_message("✅ Close functions installed")

    return close_manager

class IMGCloseManager:
    """Manages all close operations and tab cleanup for IMG Factory"""

    def __init__(self, main_window): #vers 1
        """Initialize with reference to main window"""
        self.main_window = main_window
        self.log_message = main_window.log_message

    def close_current_file(self): #vers 3
        """Close current file (IMG or COL)"""
        try:
            current_index = self.main_window.main_tab_widget.currentIndex()

            # If we have multiple tabs, use new tab system to close
            if self.main_window.main_tab_widget.count() > 1:
                # Use new tab system close function
                if hasattr(self.main_window, 'close_tab'):
                    self.main_window.close_tab(current_index)
                else:
                    # Fallback - direct close
                    self.close_tab(current_index)
            else:
                # Only one tab left, just clear it
                self._clear_current_tab()

        except Exception as e:
            self.log_message(f"❌ Error closing file: {str(e)}")

    def close_all_tabs(self): #vers 4
        """Close all tabs - Handle both IMG and COL"""
        try:
            tab_count = self.main_window.main_tab_widget.count()
            self.log_message(f"🗂️ Closing all {tab_count} tabs")

            # Close from highest index to lowest
            for i in range(tab_count - 1, -1, -1):
                if self.main_window.main_tab_widget.count() > 1:
                    # Use new tab system if available
                    if hasattr(self.main_window, 'close_tab'):
                        self.main_window.close_tab(i)
                    else:
                        self.close_tab(i)
                else:
                    # Last tab - just clear it
                    self._clear_current_tab()
                    break

            # Ensure we have at least one empty tab
            if self.main_window.main_tab_widget.count() == 0:
                if hasattr(self.main_window, 'create_tab'):
                    self.main_window.create_tab()
                else:
                    self.log_message("⚠️ No tab creation method available")

            # Clear references
            self.main_window.current_img = None
            if hasattr(self.main_window, 'current_col'):
                self.main_window.current_col = None
            self.main_window._update_ui_for_no_img()

            self.log_message("✅ All tabs closed")

        except Exception as e:
            self.log_message(f"❌ Error closing all tabs: {str(e)}")

    def close_tab(self, index): #vers 5
        """Close tab at index - Simplified for new tab system"""
        if self.main_window.main_tab_widget.count() <= 1:
            # Don't close the last tab, just clear it
            self._clear_current_tab()
            return

        try:
            # Get tab widget for logging
            tab_widget = self.main_window.main_tab_widget.widget(index)
            tab_name = self.main_window.main_tab_widget.tabText(index)

            # Clear table data in this tab
            if tab_widget:
                self._clear_all_tables_in_tab(tab_widget)

            # Remove tab - new system handles the rest
            self.main_window.main_tab_widget.removeTab(index)

            self.log_message(f"✅ Closed tab: {tab_name}")

            # Update references using new tab system
            if hasattr(self.main_window, 'update_references'):
                current_index = self.main_window.main_tab_widget.currentIndex()
                self.main_window.update_references(current_index)

        except Exception as e:
            self.log_message(f"❌ Error closing tab {index}: {str(e)}")

    def _clear_current_tab(self): #vers 2
        """Clear current tab contents"""
        try:
            current_index = self.main_window.main_tab_widget.currentIndex()

            # Use new tab system clear if available
            if hasattr(self.main_window, 'clear_tab'):
                self.main_window.clear_tab(current_index)
                return

            # Fallback - manual clear
            tab_widget = self.main_window.main_tab_widget.widget(current_index)
            if tab_widget:
                # Clear file data on tab
                tab_widget.file_object = None
                tab_widget.file_type = 'NONE'
                tab_widget.file_path = None

            # Clear main window references
            self.main_window.current_img = None
            if hasattr(self.main_window, 'current_col'):
                self.main_window.current_col = None

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


__all__ = [
    'IMGCloseManager',
    'close_img_file',
    'close_all_img',
    'setup_close_manager',
    'install_close_functions'
]
