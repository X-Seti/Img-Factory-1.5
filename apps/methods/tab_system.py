#this belongs in methods/tab_system.py - Version: 1
# X-Seti - November10 2025 - IMG Factory 1.5 - Unified Tab System

"""
Unified Tab System - Handles all tab creation and management
Ensures every file (IMG, COL, TXD) gets its own preserved tab
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout

##Methods list -
# create_tab
# get_tab_info
# is_tab_empty
# setup_tab_tracking
# switch_to_tab
# update_tab_info

def create_tab(main_window, file_path: str = None, file_type: str = 'NONE', file_object: Any = None) -> int: #vers 1
    """
    Create new tab or reuse empty tab - ALWAYS PRESERVES EXISTING TABS
    
    Args:
        main_window: Main window instance
        file_path: Path to file being loaded
        file_type: 'IMG', 'COL', 'TXD', or 'NONE'
        file_object: Loaded file object (IMGFile, COLFile, etc)
    
    Returns:
        int: Index of created/reused tab
    """
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty and can be reused
        if current_index >= 0 and is_tab_empty(main_window, current_index):
            main_window.log_message(f"Reusing empty tab {current_index} for {file_type}")
            tab_index = current_index
        else:
            # Current tab has content - CREATE NEW TAB
            main_window.log_message(f"Creating NEW tab for {file_type}")
            
            # Create new tab widget
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create GUI layout for this tab (table, splitters, etc)
            if hasattr(main_window, 'gui_layout'):
                main_window.gui_layout.create_main_ui_with_splitters(tab_layout)
            
            # Add new tab
            tab_index = main_window.main_tab_widget.addTab(tab_widget, "Loading...")
            
            # Switch to new tab
            main_window.main_tab_widget.setCurrentIndex(tab_index)
        
        # Setup tab tracking info
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}
        
        # Get clean file name for tab label
        if file_path:
            file_name = os.path.basename(file_path)
            # Remove extension for cleaner display
            file_name_clean = file_name[:-4] if '.' in file_name else file_name
        else:
            file_name_clean = "No File"
        
        # Get SVG icon based on file type
        tab_icon = None
        if file_type == 'IMG':
            from apps.methods.svg_shared_icons import get_img_file_icon
            tab_icon = get_img_file_icon()
            tab_name = file_name_clean
        elif file_type == 'COL':
            from apps.methods.svg_shared_icons import get_col_file_icon
            tab_icon = get_col_file_icon()
            tab_name = file_name_clean
        elif file_type == 'TXD':
            from apps.methods.svg_shared_icons import get_txd_file_icon
            tab_icon = get_txd_file_icon()
            tab_name = file_name_clean
        else:
            tab_name = file_name_clean
        
        # Set tab icon if available
        if tab_icon:
            main_window.main_tab_widget.setTabIcon(tab_index, tab_icon)
        
        # Store tab info in open_files tracking
        main_window.open_files[tab_index] = {
            'type': file_type,
            'file_path': file_path,
            'file_object': file_object,
            'tab_name': tab_name
        }
        
        # Update tab display name
        main_window.main_tab_widget.setTabText(tab_index, tab_name)
        
        main_window.log_message(f"✅ Tab {tab_index} created: {tab_name}")
        return tab_index
        
    except Exception as e:
        main_window.log_message(f"❌ Error creating tab: {str(e)}")
        import traceback
        traceback.print_exc()
        return -1


def is_tab_empty(main_window, tab_index: int) -> bool: #vers 1
    """
    Check if tab is empty and can be reused
    
    Returns:
        bool: True if tab has no file loaded
    """
    try:
        # Check open_files tracking
        if hasattr(main_window, 'open_files'):
            if tab_index in main_window.open_files:
                tab_info = main_window.open_files[tab_index]
                
                # Tab is empty if:
                # - type is 'NONE'
                # - no file_path
                # - no file_object
                if tab_info.get('type') == 'NONE':
                    return True
                if not tab_info.get('file_path'):
                    return True
                if not tab_info.get('file_object'):
                    return True
                
                return False
        
        # No tracking info - check tab name
        tab_name = main_window.main_tab_widget.tabText(tab_index)
        if tab_name in ["No File", "Loading...", ""]:
            return True
        
        return False
        
    except Exception as e:
        main_window.log_message(f"Error checking if tab empty: {str(e)}")
        return False


def update_tab_info(main_window, tab_index: int, file_object: Any = None, status: str = None) -> bool: #vers 1
    """
    Update tab information after file is loaded
    
    Args:
        tab_index: Index of tab to update
        file_object: Loaded file object to store
        status: Optional status message
    
    Returns:
        bool: Success
    """
    try:
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}
        
        if tab_index not in main_window.open_files:
            main_window.log_message(f"⚠️ Tab {tab_index} not in tracking")
            return False
        
        # Update file object
        if file_object:
            main_window.open_files[tab_index]['file_object'] = file_object
            main_window.log_message(f"✅ Tab {tab_index} file object updated")
        
        # Update status if provided
        if status:
            main_window.log_message(f"Tab {tab_index}: {status}")
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating tab info: {str(e)}")
        return False


def get_tab_info(main_window, tab_index: int = None) -> Optional[Dict[str, Any]]: #vers 1
    """
    Get information about a specific tab
    
    Args:
        tab_index: Index of tab (None = current tab)
    
    Returns:
        dict: Tab info or None
    """
    try:
        if tab_index is None:
            tab_index = main_window.main_tab_widget.currentIndex()
        
        if not hasattr(main_window, 'open_files'):
            return None
        
        return main_window.open_files.get(tab_index)
        
    except Exception as e:
        main_window.log_message(f"Error getting tab info: {str(e)}")
        return None


def switch_to_tab(main_window, tab_index: int) -> bool: #vers 1
    """
    Switch to specific tab and load its file references
    
    Args:
        tab_index: Index of tab to switch to
    
    Returns:
        bool: Success
    """
    try:
        if tab_index < 0 or tab_index >= main_window.main_tab_widget.count():
            return False
        
        # Get tab info
        tab_info = get_tab_info(main_window, tab_index)
        if not tab_info:
            main_window.log_message(f"No info for tab {tab_index}")
            return False
        
        # Update current file references
        file_type = tab_info.get('type', 'NONE')
        file_object = tab_info.get('file_object')
        
        # Clear all current references first
        main_window.current_img = None
        if hasattr(main_window, 'current_col'):
            main_window.current_col = None
        if hasattr(main_window, 'current_txd'):
            main_window.current_txd = None
        
        # Set appropriate reference based on file type
        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
        elif file_type == 'TXD' and file_object:
            main_window.current_txd = file_object
        
        # Switch tab
        main_window.main_tab_widget.setCurrentIndex(tab_index)
        
        main_window.log_message(f"✅ Switched to tab {tab_index}: {tab_info.get('tab_name', 'Unknown')}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error switching to tab: {str(e)}")
        return False


def setup_tab_tracking(main_window) -> bool: #vers 1
    """
    Initialize tab tracking system on main window
    
    Returns:
        bool: Success
    """
    try:
        # Initialize tracking dict if not exists
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}
            main_window.log_message("✅ Tab tracking initialized")
        
        # Connect tab change signal to update references
        main_window.main_tab_widget.currentChanged.connect(
            lambda idx: _on_tab_changed(main_window, idx)
        )
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up tab tracking: {str(e)}")
        return False


def _on_tab_changed(main_window, new_index: int): #vers 1
    """
    Internal handler when tab changes - updates current file references
    
    Args:
        new_index: Index of newly selected tab
    """
    try:
        if new_index < 0:
            return
        
        # Get tab info
        tab_info = get_tab_info(main_window, new_index)
        if not tab_info:
            return
        
        # Update current file references based on tab type
        file_type = tab_info.get('type', 'NONE')
        file_object = tab_info.get('file_object')
        
        # Clear all references first
        main_window.current_img = None
        if hasattr(main_window, 'current_col'):
            main_window.current_col = None
        if hasattr(main_window, 'current_txd'):
            main_window.current_txd = None
        
        # Set appropriate reference
        if file_type == 'IMG' and file_object:
            main_window.current_img = file_object
            main_window.log_message(f"Switched to IMG: {tab_info.get('tab_name')}")
        elif file_type == 'COL' and file_object:
            main_window.current_col = file_object
            main_window.log_message(f"Switched to COL: {tab_info.get('tab_name')}")
        elif file_type == 'TXD' and file_object:
            main_window.current_txd = file_object
            main_window.log_message(f"Switched to TXD: {tab_info.get('tab_name')}")
        
        # Update UI for current file
        if hasattr(main_window, '_update_ui_for_current_file'):
            main_window._update_ui_for_current_file()
        
    except Exception as e:
        main_window.log_message(f"❌ Error in tab change handler: {str(e)}")


# Export all functions
__all__ = [
    'create_tab',
    'is_tab_empty',
    'update_tab_info',
    'get_tab_info',
    'switch_to_tab',
    'setup_tab_tracking'
]
