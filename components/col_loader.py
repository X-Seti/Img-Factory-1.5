#this belongs in components/col_loader.py - Version: 4
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Loading System Fixed

"""
COL Loading System - Fixed table structure conflicts
Ensures COL files use proper table structure with IMG debug integration
FIXED: Complete missing functions with existing method calls only
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

# Import existing functions - NO NEW FUNCTIONS CREATED
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile
from components.col_validator import validate_col_file
from methods.populate_col_table import populate_col_table, setup_col_table_structure, create_table_item
from core.tables_structure import reset_table_styling

## Methods list -
# load_col_file_safely
# validate_col_file
# setup_col_tab
# load_col_file_object
# populate_col_table
# update_col_info_bar
# create_table_item

def load_col_file_safely(main_window, file_path: str) -> bool: #vers 4
    """Load COL file safely with proper validation and tab management - FIXED"""
    try:
        main_window.log_message(f"🔧 Loading COL: {os.path.basename(file_path)}")
        
        # Step 1: Validate file - USE EXISTING FUNCTION
        if not validate_col_file(main_window, file_path):
            return False
        
        # Step 2: Setup tab - USE EXISTING FUNCTION
        tab_index = setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False
        
        # Step 3: Load COL file object - USE EXISTING FUNCTION
        col_file = load_col_file_object(main_window, file_path)
        if col_file is None:
            return False
        
        # Step 4: Setup table structure - USE EXISTING FUNCTION
        setup_col_table_structure(main_window)
        
        # Step 5: Populate table with COL data - USE EXISTING FUNCTION
        if not populate_col_table(main_window, col_file):
            main_window.log_message("❌ Failed to populate COL table")
            return False
        
        # Step 6: Update main window state
        main_window.current_col = col_file
        if hasattr(main_window, 'open_files') and tab_index in main_window.open_files:
            main_window.open_files[tab_index]['file_object'] = col_file
        
        # Step 7: Update info bar - USE EXISTING FUNCTION
        update_col_info_bar(main_window, col_file, file_path)
        
        # Step 8: Reset table styling - USE EXISTING FUNCTION
        reset_table_styling(main_window)
        
        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False


def setup_col_tab(main_window, file_path: str) -> Optional[int]: #vers 2
    """Setup COL tab in main window - FIXED"""
    try:
        filename = os.path.basename(file_path)
        
        # Check if file is already open
        if hasattr(main_window, 'open_files'):
            for tab_index, file_info in main_window.open_files.items():
                if file_info.get('file_path') == file_path:
                    main_window.main_tab_widget.setCurrentIndex(tab_index)
                    return tab_index
        
        # Get current tab or create new one
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty
        if current_index not in main_window.open_files:
            # Use current empty tab
            tab_index = current_index
        else:
            # Create new tab
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
            tab_index = main_window.main_tab_widget.currentIndex()
        
        # Store COL file info
        tab_name = f"🔧 {filename[:-4] if filename.lower().endswith('.col') else filename}"
        main_window.open_files[tab_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }
        
        # Update tab name
        main_window.main_tab_widget.setTabText(tab_index, tab_name)
        
        return tab_index
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def load_col_file_object(main_window, file_path: str) -> Optional[COLFile]: #vers 2
    """Load COL file object using existing COL core classes - FIXED"""
    try:
        # Create COL file object - USE EXISTING COLFile CLASS
        col_file = COLFile(file_path)
        
        # Load the file - USE EXISTING load() METHOD
        if col_file.load():
            main_window.log_message(f"✅ COL object loaded: {len(col_file.models)} models")
            return col_file
        else:
            error_msg = col_file.load_error or "Unknown loading error"
            main_window.log_message(f"❌ Failed to load COL file: {error_msg}")
            return None
            
    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None


def update_col_info_bar(main_window, col_file: Any, file_path: str) -> None: #vers 3
    """Update info bar with COL file information - FIXED"""
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
        
        # Update window title
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
        
        # Update status bar if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            size_text = f"{file_size // 1024}KB" if file_size >= 1024 else f"{file_size}B"
            main_window.gui_layout.show_progress(-1, f"COL: {model_count} models ({size_text})")
        
        # Update info display if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'update_img_info'):
            main_window.gui_layout.update_img_info(f"COL: {file_name}")
        
        main_window.log_message(f"✅ COL info bar updated: {file_name}")
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating COL info bar: {str(e)}")


# Export functions - KEEP EXISTING INTERFACE
__all__ = [
    'load_col_file_safely',
    'validate_col_file', 
    'setup_col_tab',
    'load_col_file_object',
    'populate_col_table',
    'update_col_info_bar',
    'setup_col_table_structure',
    'create_table_item'
]