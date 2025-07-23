#this belongs in components/col_loader.py - Version: 8
# X-Seti - July23 2025 - IMG Factory 1.5 - COL Loading System with IMG Debug System
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
COL Loading System - Main COL file loading functions
Ported from old-ignore-folder with IMG debug system integration
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

# Import IMG debug system (ONLY debug change)
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile

##Methods list -
# create_table_item
# load_col_file_object
# load_col_file_safely
# populate_col_table
# setup_col_table_structure
# update_col_info_bar
# validate_col_file

def load_col_file_safely(main_window, file_path: str) -> bool: #vers 8
    """Load COL file safely with proper validation and tab management"""
    try:
        img_debugger.debug(f"Loading COL: {os.path.basename(file_path)}")
        
        # Use threaded loader for better UX
        from components.col_threaded_loader import load_col_file_threaded
        loader = load_col_file_threaded(main_window, file_path)
        
        # Return True if loader started successfully
        return loader is not None
        
    except Exception as e:
        img_debugger.error(f"Error in COL loading: {str(e)}")
        return False

def load_col_file_object(main_window, file_path: str) -> Optional[COLFile]: #vers 8
    """Load COL file and return COL object directly"""
    try:
        if not validate_col_file(main_window, file_path):
            return None
        
        col_file = COLFile(file_path)
        
        if col_file.load_from_file(file_path):
            if col_file.load_error:
                error_details = col_file.load_error
                img_debugger.error(f"COL file load error: {error_details}")
                main_window.log_message(f"❌ Failed to load COL file: {error_details}")
                return None
            
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            img_debugger.success(f"COL file loaded: {model_count} models")
            return col_file
            
        except Exception as e:
            img_debugger.error(f"Error loading COL file: {str(e)}")
            return None

def validate_col_file(main_window, file_path: str) -> bool: #vers 8
    """Validate COL file before loading"""
    try:
        if not os.path.exists(file_path):
            img_debugger.error(f"COL file not found: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            img_debugger.error(f"Cannot read COL file: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size < 32:
            img_debugger.error(f"COL file too small ({file_size} bytes)")
            return False
        
        # Check COL signature
        try:
            with open(file_path, 'rb') as f:
                signature = f.read(4)
                if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                    img_debugger.error(f"Invalid COL signature: {signature}")
                    return False
        except Exception as e:
            img_debugger.error(f"Error reading COL signature: {str(e)}")
            return False
        
        img_debugger.debug(f"COL file validation passed: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error validating COL file: {str(e)}")
        return False

def setup_col_table_structure(main_window) -> bool: #vers 8
    """Setup table structure for COL data"""
    try:
        # Try to use methods version first
        try:
            from methods.populate_col_table import setup_col_table_structure as methods_setup_structure
            return methods_setup_structure(main_window)
        except ImportError:
            img_debugger.warning("methods.populate_col_table not available, using fallback")
        
        # Fallback implementation
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("GUI layout or table not found")
            return False
        
        table = main_window.gui_layout.table
        
        # COL-specific columns
        col_headers = ["Model Name", "Type", "Version", "Size", "Spheres", "Boxes", "Faces", "Info"]
        table.setColumnCount(len(col_headers))
        table.setHorizontalHeaderLabels(col_headers)
        
        # Set column widths
        table.setColumnWidth(0, 200)  # Model Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 80)   # Version
        table.setColumnWidth(3, 100)  # Size
        table.setColumnWidth(4, 80)   # Spheres
        table.setColumnWidth(5, 80)   # Boxes
        table.setColumnWidth(6, 80)   # Faces
        table.setColumnWidth(7, 150)  # Info
        
        img_debugger.debug("COL table structure setup complete")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error setting up COL table structure: {str(e)}")
        return False

def populate_col_table(main_window, col_file: Any) -> bool: #vers 8
    """Populate table with COL data"""
    try:
        # Try to use methods version first
        try:
            from methods.populate_col_table import populate_table_with_col_data_debug
            return populate_table_with_col_data_debug(main_window, col_file)
        except ImportError:
            img_debugger.warning("methods.populate_col_table not available, using fallback")
        
        # Fallback implementation
        if not col_file or not hasattr(col_file, 'models'):
            img_debugger.error("Invalid COL file for table population")
            return False
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("GUI layout or table not found")
            return False
        
        table = main_window.gui_layout.table
        table.setRowCount(len(col_file.models))
        
        for row, model in enumerate(col_file.models):
            # Model Name
            name_item = create_table_item(model.name or f"Model_{row+1}")
            table.setItem(row, 0, name_item)
            
            # Type
            type_item = create_table_item("COL")
            table.setItem(row, 1, type_item)
            
            # Version
            version_item = create_table_item(str(getattr(model, 'col_version', 1)))
            table.setItem(row, 2, version_item)
            
            # Size (estimate)
            size_item = create_table_item("N/A")
            table.setItem(row, 3, size_item)
            
            # Stats
            stats = model.get_total_stats()
            table.setItem(row, 4, create_table_item(str(stats['spheres'])))
            table.setItem(row, 5, create_table_item(str(stats['boxes'])))
            table.setItem(row, 6, create_table_item(str(stats['faces'])))
            
            # Info
            info_text = f"V{model.col_version} Model"
            table.setItem(row, 7, create_table_item(info_text))
        
        img_debugger.success(f"COL table populated with {len(col_file.models)} models")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error populating COL table: {str(e)}")
        return False

def create_table_item(text: str) -> QTableWidgetItem: #vers 8
    """Create a table widget item with proper formatting"""
    item = QTableWidgetItem(str(text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

def update_col_info_bar(main_window, col_file: Any, file_path: str): #vers 8
    """Update info bar with COL file information"""
    try:
        # Try to use GUI version first
        try:
            from gui.gui_infobar import update_col_info_bar_enhanced
            update_col_info_bar_enhanced(main_window, col_file, file_path)
            return
        except ImportError:
            img_debugger.warning("gui.gui_infobar not available, using fallback")
        
        # Fallback info bar update
        if hasattr(main_window, 'status_bar') and hasattr(main_window.status_bar, 'showMessage'):
            file_name = os.path.basename(file_path)
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            message = f"COL: {file_name} - {model_count} models"
            main_window.status_bar.showMessage(message)
            
        img_debugger.debug(f"COL info bar updated: {os.path.basename(file_path)}")
        
    except Exception as e:
        img_debugger.error(f"Error updating COL info bar: {str(e)}")
