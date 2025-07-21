#this belongs in methods/populate_col_table.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Table Population Methods
# Table population methods for COL files using IMG debug system

"""
COL Table Population Methods
Handles populating the main table widget with COL file data
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

# Import IMG debug system and COL classes
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile, COLModel

##Methods list -
# load_col_file_object
# load_col_file_safely
# populate_table_with_col_data_debug
# setup_col_tab
# setup_col_tab_integration
# setup_col_table_structure

def setup_col_table_structure(main_window): #vers 1
    """Setup table structure for COL data display"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("No table widget available for COL setup")
            return False
        
        table = main_window.gui_layout.table
        
        # Setup COL-specific columns
        col_headers = ["Model Name", "Type", "Version", "Size", "Spheres", "Boxes", "Faces", "Info"]
        table.setColumnCount(len(col_headers))
        table.setHorizontalHeaderLabels(col_headers)
        
        # Adjust column widths for COL data
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
        img_debugger.error(f"Error setting up COL table structure: {e}")
        return False

def populate_table_with_col_data_debug(main_window, col_file: COLFile): #vers 1
    """Populate table with COL file data using IMG debug system"""
    try:
        if not col_file or not col_file.models:
            img_debugger.warning("No COL data to populate")
            return False
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("No table widget available")
            return False
        
        table = main_window.gui_layout.table
        models = col_file.models
        
        img_debugger.debug(f"Populating table with {len(models)} COL models")
        
        # Setup table structure first
        setup_col_table_structure(main_window)
        
        # Set row count
        table.setRowCount(len(models))
        
        # Populate each model
        for row, model in enumerate(models):
            # Model Name (Column 0)
            model_name = model.name or f"Model_{row+1}"
            table.setItem(row, 0, QTableWidgetItem(model_name))
            
            # Type (Column 1)
            table.setItem(row, 1, QTableWidgetItem("COL"))
            
            # Version (Column 2)
            version_text = f"v{model.version.value}"
            table.setItem(row, 2, QTableWidgetItem(version_text))
            
            # Size (Column 3) - Estimate based on data
            sphere_count = len(model.spheres)
            box_count = len(model.boxes)
            vertex_count = len(model.vertices)
            face_count = len(model.faces)
            
            estimated_size = (sphere_count * 20) + (box_count * 32) + (vertex_count * 12) + (face_count * 20)
            size_text = f"{estimated_size:,} bytes" if estimated_size > 0 else "Unknown"
            table.setItem(row, 3, QTableWidgetItem(size_text))
            
            # Spheres (Column 4)
            table.setItem(row, 4, QTableWidgetItem(str(sphere_count)))
            
            # Boxes (Column 5)
            table.setItem(row, 5, QTableWidgetItem(str(box_count)))
            
            # Faces (Column 6)
            table.setItem(row, 6, QTableWidgetItem(str(face_count)))
            
            # Info (Column 7)
            info_parts = []
            if model.has_sphere_data:
                info_parts.append("Spheres")
            if model.has_box_data:
                info_parts.append("Boxes")
            if model.has_mesh_data:
                info_parts.append("Mesh")
            
            info_text = ", ".join(info_parts) if info_parts else "Basic COL"
            table.setItem(row, 7, QTableWidgetItem(info_text))
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        img_debugger.success(f"COL table populated with {len(models)} models")
        return True
        
    except Exception as e:
        img_debugger.error(f"Error populating COL table: {e}")
        return False

def load_col_file_object(main_window, file_path: str) -> Optional[COLFile]: #vers 1
    """Load COL file object using IMG debug system"""
    try:
        from components.col_validator import validate_col_file
        
        # Validate file first
        if not validate_col_file(main_window, file_path):
            return None
        
        img_debugger.debug(f"Loading COL file object: {os.path.basename(file_path)}")
        
        # Create and load COL file
        col_file = COLFile(file_path)
        
        if col_file.load():
            img_debugger.success(f"COL file loaded: {len(col_file.models)} models")
            return col_file
        else:
            error_msg = col_file.load_error or "Unknown loading error"
            img_debugger.error(f"COL file loading failed: {error_msg}")
            return None
            
    except Exception as e:
        img_debugger.error(f"Error loading COL file object: {e}")
        return None

def load_col_file_safely(main_window, file_path: str) -> bool: #vers 1
    """Load COL file safely with full error handling using IMG debug system"""
    try:
        img_debugger.debug(f"Starting safe COL file load: {os.path.basename(file_path)}")
        
        # Validate file first
        from components.col_validator import validate_col_file
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
        setup_col_table_structure(main_window)
        
        # Populate table with COL data
        populate_table_with_col_data_debug(main_window, col_file)
        
        # Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file
        
        # Update info bar
        from gui.gui_infobar import update_col_info_bar_enhanced
        update_col_info_bar_enhanced(main_window, col_file, file_path)
        
        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False

def setup_col_tab(main_window, file_path: str) -> Optional[int]: #vers 1
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

def setup_col_tab_integration(main_window): #vers 1
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)

        # Add styling reset method
        from core.tables_structure import reset_table_styling
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)

        main_window.log_message("✅ COL tab integration ready")
        return True

    except Exception as e:
        main_window.log_message(f"❌ COL tab integration failed: {str(e)}")
        return False