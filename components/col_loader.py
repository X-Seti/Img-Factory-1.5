#this belongs in core/ loadcol.py - Version: 3
# X-Seti - July18 2025 - Img Factory 1.5 - COL Loading System Fixed

"""
COL Loading System - Fixed table structure conflicts
Ensures COL files use proper 6-column table structure
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

## Methods list -
# load_col_file_safely
# validate_col_file
# setup_col_tab
# load_col_file_object
# populate_col_table
# update_col_info_bar
# create_table_item


def load_col_file_safely(main_window, file_path: str) -> bool: #vers 3
    """Load COL file safely with proper validation and tab management"""
    try:
        main_window.log_message(f"🔧 Loading COL: {os.path.basename(file_path)}")
        
        # Step 1: Validate file
        if not validate_col_file(main_window, file_path):
            return False
        
        # Step 2: Setup tab
        tab_index = setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False
        
        # Step 3: Load COL file object
        col_file = load_col_file_object(main_window, file_path)
        if col_file is None:
            return False
        
        # Step 4: Setup table structure (6 columns for COL)
        setup_col_table_structure(main_window)
        
        # Step 5: Populate table with COL data
        populate_col_table(main_window, col_file)
        
        # Step 6: Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file
        
        # Step 7: Update info bar
        update_col_info_bar(main_window, col_file, file_path)
        
        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False


def validate_col_file(main_window, file_path: str) -> bool: #vers 3
    """Validate COL file before loading"""
    try:
        if not os.path.exists(file_path):
            main_window.log_message(f"❌ COL file not found: {file_path}")
            return False

        if not os.access(file_path, os.R_OK):
            main_window.log_message(f"❌ Cannot read COL file: {file_path}")
            return False

        file_size = os.path.getsize(file_path)
        if file_size < 32:
            main_window.log_message(f"❌ COL file too small ({file_size} bytes)")
            return False

        return True
        
    except Exception as e:
        main_window.log_message(f"❌ COL validation error: {str(e)}")
        return False


def setup_col_tab(main_window, file_path: str) -> Optional[int]: #vers 3
    """Setup or reuse tab for COL file"""
    try:
        file_name = os.path.basename(file_path)
        
        # Check if file already open
        for tab_index, file_info in main_window.open_files.items():
            if file_info.get('file_path') == file_path:
                main_window.main_tab_widget.setCurrentIndex(tab_index)
                main_window.log_message(f"📂 Switched to existing tab: {file_name}")
                return tab_index
        
        # Create new tab
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty (no file loaded)
        if (current_index == 0 and 
            len(main_window.open_files) == 0 and 
            main_window.main_tab_widget.tabText(0) == "📁 No File"):
            
            # Use existing empty tab
            main_window.main_tab_widget.setTabText(0, f"📋 {file_name}")
            main_window.open_files[0] = {
                'file_path': file_path,
                'type': 'COL',
                'tab_name': f"📋 {file_name}"
            }
            return 0
        else:
            # Create new tab
            from PyQt6.QtWidgets import QWidget, QVBoxLayout
            
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add main UI to tab
            main_window.gui_layout.create_main_ui_with_splitters(tab_layout)
            
            # Add tab
            new_index = main_window.main_tab_widget.addTab(tab_widget, f"📋 {file_name}")
            main_window.main_tab_widget.setCurrentIndex(new_index)
            
            # Store file info
            main_window.open_files[new_index] = {
                'file_path': file_path,
                'type': 'COL',
                'tab_name': f"📋 {file_name}"
            }
            
            return new_index
            
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def load_col_file_object(main_window, file_path: str) -> Optional[Any]: #vers 3
    """Load COL file object"""
    try:
        from components.col_core_classes import COLFile
        
        main_window.log_message("📖 Loading COL file data...")
        col_file = COLFile(file_path)
        
        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            main_window.log_message(f"❌ Failed to load COL file: {error_details}")
            return None
        
        model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
        main_window.log_message(f"✅ COL file loaded: {model_count} models")
        return col_file
        
    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None


def update_col_info_bar(main_window, col_file: Any, file_path: str) -> None: #vers 3
    """Update info bar with COL file information"""
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
        
        # Update window title
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
        
        # Update info labels if they exist
        if hasattr(main_window, 'file_path_label'):
            main_window.file_path_label.setText(file_path)
        
        if hasattr(main_window, 'version_label'):
            main_window.version_label.setText("COL")
        
        if hasattr(main_window, 'entry_count_label'):
            main_window.entry_count_label.setText(str(model_count))
        
        # Update status bar
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            size_text = f"{file_size // 1024}KB" if file_size >= 1024 else f"{file_size}B"
            main_window.gui_layout.show_progress(-1, f"COL: {model_count} models ({size_text})")
        
        main_window.log_message(f"✅ COL info bar updated: {file_name}")
        
    except Exception as e:
        main_window.log_message(f"❌ Error updating COL info bar: {str(e)}")


# Export functions
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
