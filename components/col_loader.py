#this belongs in components/col_loader.py - Version: 4
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Loading System Fixed
# Fixed import issues - uses correct function names from ported files

"""
COL Loading System - Fixed imports
Uses correct function names from ported COL files
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

# Import IMG debug system
from components.img_debug_functions import img_debugger

##Methods list -
# create_table_item
# load_col_file_safely
# load_col_file_object
# populate_col_table
# setup_col_tab
# setup_col_table_structure
# update_col_info_bar
# validate_col_file

def load_col_file_safely(main_window, file_path: str) -> bool: #vers 4
    """Load COL file safely with proper validation and tab management"""
    try:
        main_window.log_message(f"🔧 Loading COL: {os.path.basename(file_path)}")
        
        # Use our ported COL parsing functions
        from components.col_parsing_functions import load_col_file_safely as parse_load_col
        return parse_load_col(main_window, file_path)
        
    except Exception as e:
        main_window.log_message(f"❌ Error in COL loading: {str(e)}")
        return False

def validate_col_file(main_window, file_path: str) -> bool: #vers 4
    """Validate COL file before loading"""
    try:
        from components.col_validator import validate_col_file as validator
        return validator(main_window, file_path)
        
    except ImportError:
        # Fallback validation
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
        
        # Check COL signature
        try:
            with open(file_path, 'rb') as f:
                signature = f.read(4)
                if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                    main_window.log_message(f"❌ Invalid COL signature: {signature}")
                    return False
        except Exception as e:
            main_window.log_message(f"❌ COL validation error: {str(e)}")
            return False
        
        return True

def setup_col_tab(main_window, file_path: str) -> Optional[int]: #vers 4
    """Setup or reuse tab for COL file"""
    try:
        from methods.populate_col_table import setup_col_tab as methods_setup_tab
        return methods_setup_tab(main_window, file_path)
        
    except ImportError:
        # Fallback implementation
        try:
            file_name = os.path.basename(file_path)
            file_name_clean = file_name[:-4] if file_name.lower().endswith('.col') else file_name
            
            # Simple tab setup
            if not hasattr(main_window, 'open_files'):
                main_window.open_files = {}
            
            current_index = 0
            main_window.open_files[current_index] = {
                'file_path': file_path,
                'type': 'COL',
                'tab_name': f"🛡️ {file_name_clean}",
                'file_object': None
            }
            
            # Update window title
            main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
            
            return current_index
            
        except Exception as e:
            main_window.log_message(f"❌ Error setting up COL tab: {str(e)}")
            return None

def load_col_file_object(main_window, file_path: str) -> Optional[Any]: #vers 4
    """Load COL file object"""
    try:
        from methods.populate_col_table import load_col_file_object as methods_load_object
        return methods_load_object(main_window, file_path)
        
    except ImportError:
        # Fallback implementation using core classes
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
            
        except Exception as e:
            main_window.log_message(f"❌ Error loading COL file: {str(e)}")
            return None

def setup_col_table_structure(main_window) -> bool: #vers 4
    """Setup table structure for COL data"""
    try:
        from methods.populate_col_table import setup_col_table_structure as methods_setup_structure
        return methods_setup_structure(main_window)
        
    except ImportError:
        # Fallback implementation
        try:
            if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
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
            
            return True
            
        except Exception as e:
            main_window.log_message(f"❌ Error setting up COL table structure: {str(e)}")
            return False

def populate_col_table(main_window, col_file: Any) -> bool: #vers 4
    """Populate table with COL data"""
    try:
        from methods.populate_col_table import populate_table_with_col_data_debug
        return populate_table_with_col_data_debug(main_window, col_file)
        
    except ImportError:
        # Fallback implementation
        try:
            if not col_file or not hasattr(col_file, 'models') or not col_file.models:
                main_window.log_message("❌ No COL models to display")
                return False
            
            if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
                main_window.log_message("❌ No table widget available")
                return False
            
            table = main_window.gui_layout.table
            models = col_file.models
            
            # Set row count
            table.setRowCount(len(models))
            
            # Populate each model
            for row, model in enumerate(models):
                # Model Name
                model_name = getattr(model, 'name', f"Model_{row+1}")
                table.setItem(row, 0, create_table_item(model_name))
                
                # Type
                table.setItem(row, 1, create_table_item("COL"))
                
                # Version
                version = getattr(model, 'version', None)
                version_text = f"v{version.value}" if version else "Unknown"
                table.setItem(row, 2, create_table_item(version_text))
                
                # Size
                table.setItem(row, 3, create_table_item("Unknown"))
                
                # Spheres
                sphere_count = len(getattr(model, 'spheres', []))
                table.setItem(row, 4, create_table_item(str(sphere_count)))
                
                # Boxes
                box_count = len(getattr(model, 'boxes', []))
                table.setItem(row, 5, create_table_item(str(box_count)))
                
                # Faces
                face_count = len(getattr(model, 'faces', []))
                table.setItem(row, 6, create_table_item(str(face_count)))
                
                # Info
                info_parts = []
                if sphere_count > 0:
                    info_parts.append("Spheres")
                if box_count > 0:
                    info_parts.append("Boxes")
                if face_count > 0:
                    info_parts.append("Mesh")
                
                info_text = ", ".join(info_parts) if info_parts else "Basic COL"
                table.setItem(row, 7, create_table_item(info_text))
            
            # Enable sorting
            table.setSortingEnabled(True)
            
            main_window.log_message(f"✅ COL table populated with {len(models)} models")
            return True
            
        except Exception as e:
            main_window.log_message(f"❌ Error populating COL table: {str(e)}")
            return False

def update_col_info_bar(main_window, col_file: Any, file_path: str) -> bool: #vers 4
    """Update info bar with COL file information"""
    try:
        from gui.gui_infobar import update_col_info_bar_enhanced
        update_col_info_bar_enhanced(main_window, col_file, file_path)
        return True
        
    except ImportError:
        # Fallback implementation
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            
            # Update window title
            main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
            
            # Update info labels if they exist
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'info_panel'):
                info_panel = main_window.gui_layout.info_panel
                if hasattr(info_panel, 'update_info'):
                    info_panel.update_info(f"COL: {model_count} models", file_size)
            
            main_window.log_message(f"✅ COL info updated: {file_name} ({model_count} models)")
            return True
            
        except Exception as e:
            main_window.log_message(f"❌ Error updating COL info bar: {str(e)}")
            return False

def create_table_item(text: str) -> QTableWidgetItem: #vers 4
    """Create a table widget item with text"""
    item = QTableWidgetItem(str(text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
    return item

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