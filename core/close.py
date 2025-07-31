#this belongs in core/ close.py - Version: 1
# X-Seti - July06 2025 - Img Factory 1.5 - Close and Tab Management Functions

#!/usr/bin/env python3
"""
IMG Factory Close Functions
Handles all close, tab management, and cleanup operations
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from core.close_func import install_close_functions, setup_close_manager

def close_all_img(self): #vers 2
    """Close all IMG files - Wrapper for close_all_tabs"""
    try:
        if hasattr(self, 'close_manager') and self.close_manager:
            self.close_manager.close_all_tabs()
        else:
            self.log_message("❌ Close manager not available")
    except Exception as e:
        self.log_message(f"❌ Error in close_all_img: {str(e)}")


def close_img_file(self): #vers 5
    """Close current file (IMG or COL) - UPDATED for both file types"""
    current_index = self.main_window.main_tab_widget.currentIndex()

    # Clear the current file data
    old_img = self.main_window.current_img
    old_col = self.main_window.current_col
    self.main_window.current_img = None
    self.main_window.current_col = None

    # Remove from open_files if exsts
    if current_index in self.main_window.open_files:
        file_info = self.main_window.open_files[current_index]
        file_path = file_info.get('file_path', 'Unknown file')
        file_type = file_info.get('type', 'Unknown')
        self.log_message(f"🗂️ Closing {file_type}: {os.path.basename(file_path)}")
        del self.main_window.open_files[current_index]

    # Reset tab name to "No File"
    self.main_window.main_tab_widget.setTabText(current_index, "📁 No File")
    # Update UI for no file stat
    self.main_window._update_ui_for_no_img()

    # Log what was closed
    if old_img:
        self.log_message("✅ IMG file closed")
    elif old_col:
        self.log_message("✅ COL file closed")
    else:
        self.log_message("✅ Tab cleared")


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

__all__ = [
    'close_img_file',
    'close_all_img'
]
