#this belongs in core/ loadcol.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - COL Loading Functions

"""
COL Loading Functions
Handles loading COL files with proper validation and tab management
"""

import os


def load_col_file_safely(main_window, file_path):
    """Load COL file safely with proper tab management"""
    try:
        # Validate file
        if not validate_col_file(main_window, file_path):
            return False
        
        # Setup tab
        tab_index = setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False
        
        # Load COL file
        col_file = load_col_file_object(main_window, file_path)
        if col_file is None:
            return False
        
        # Setup table structure for COL data
        from core.tables_structure import setup_col_table_structure
        setup_col_table_structure(main_window)
        
        # Populate table with enhanced COL data
        from core.tables_structure import populate_col_table_enhanced
        populate_col_table_enhanced(main_window, col_file)
        
        # Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file
        
        # Update info bar with enhanced data
        update_col_info_bar_enhanced(main_window, col_file, file_path)
        
        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False


def load_col_file_object(main_window, file_path):
    """Load COL file object"""
    try:
        from components.col_core_classes import COLFile
        
        main_window.log_message("📖 Loading COL file data...")
        col_file = COLFile(file_path)
        
        if not col_file.load():
            error_details = getattr(col_file, 'load_error', 'Unknown loading error')
            main_window.log_message(f"❌ Failed to load COL file: {error_details}")
            return None
        
        return col_file
        
    except ImportError as e:
        main_window.log_message(f"❌ COL core classes not available: {str(e)}")
        return None
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return None


def validate_col_file(main_window, file_path):
    """Validate COL file before loading"""
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


def setup_col_tab(main_window, file_path):
    """Setup or reuse tab for COL file"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty
        if not hasattr(main_window, 'open_files') or current_index not in main_window.open_files:
            main_window.log_message("Using current tab for COL file")
        else:
            main_window.log_message("Creating new tab for COL file")
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
                current_index = main_window.main_tab_widget.currentIndex()
            else:
                main_window.log_message("⚠️ Close manager not available")
                return None
        
        # Setup tab info
        file_name = os.path.basename(file_path)
        file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
        tab_name = f"🛡️ {file_name_clean}"
        
        # Store tab info
        if not hasattr(main_window, 'open_files'):
            main_window.open_files = {}
        
        main_window.open_files[current_index] = {
            'type': 'COL',
            'file_path': file_path,
            'file_object': None,
            'tab_name': tab_name
        }
        
        # Update tab name
        main_window.main_tab_widget.setTabText(current_index, tab_name)
        
        return current_index
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
        return None


def update_col_info_bar_enhanced(main_window, col_file, file_path):
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        main_window.log_message("✅ Enhanced info bar updated")
        
    except Exception as e:
        main_window.log_message(f"❌ Enhanced info bar update failed: {str(e)}")
        raise


# Export functions
__all__ = [
    'load_col_file_safely',
    'load_col_file_object',
    'validate_col_file',
    'setup_col_tab',
    'update_col_info_bar_enhanced'
]