# X-Seti - October26 2025 - IMG Factory 1.5 - Simple Tab Validation
# This belongs in methods/simple_tab_validation.py - Version: 1

"""
Simple Tab Validation - Replacement for deleted tab_aware_functions
Provides basic tab validation without complex dependencies
"""

from typing import Optional, Tuple, Any
from PyQt6.QtWidgets import QMessageBox

##Methods list -
# get_current_file_from_active_tab
# get_current_file_type_from_tab
# validate_tab_before_operation

def validate_tab_before_operation(main_window, operation_name: str = "operation") -> bool: #vers 1
    """Simple tab validation - checks if a file is loaded"""
    try:
        # Check if main window has the required attributes
        if not hasattr(main_window, 'main_tab_widget'):
            QMessageBox.warning(main_window, "No Tabs", 
                f"Cannot perform {operation_name}: Tab system not available.")
            return False
        
        # Check if any tab is active
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            QMessageBox.warning(main_window, "No Active Tab", 
                f"Cannot perform {operation_name}: No tab is currently active.")
            return False
        
        # Check if we have a valid file loaded
        has_img = hasattr(main_window, 'current_img') and main_window.current_img is not None
        has_col = hasattr(main_window, 'current_col') and main_window.current_col is not None
        has_txd = hasattr(main_window, 'current_txd') and main_window.current_txd is not None
        
        if not (has_img or has_col or has_txd):
            QMessageBox.warning(main_window, "No File Loaded", 
                f"Cannot perform {operation_name}: No file is currently loaded in the active tab.")
            return False
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Tab validation error: {str(e)}")
        return False


def get_current_file_from_active_tab(main_window) -> Tuple[Optional[Any], str]: #vers 1
    """Get file object and type from current tab
    
    Returns:
        (file_object, file_type) where file_type is 'IMG', 'COL', 'TXD', or 'NONE'
    """
    try:
        # Check IMG first
        if hasattr(main_window, 'current_img') and main_window.current_img:
            return main_window.current_img, 'IMG'
        
        # Check COL
        if hasattr(main_window, 'current_col') and main_window.current_col:
            return main_window.current_col, 'COL'
        
        # Check TXD
        if hasattr(main_window, 'current_txd') and main_window.current_txd:
            return main_window.current_txd, 'TXD'
        
        return None, 'NONE'
        
    except Exception:
        return None, 'NONE'


def get_current_file_type_from_tab(main_window) -> str: #vers 1
    """Get file type from current tab
    
    Returns:
        'IMG', 'COL', 'TXD', or 'NONE'
    """
    _, file_type = get_current_file_from_active_tab(main_window)
    return file_type


__all__ = [
    'validate_tab_before_operation',
    'get_current_file_from_active_tab', 
    'get_current_file_type_from_tab'
]
