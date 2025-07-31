#this belongs in methods/populate_col_table.py - Version: 3
# X-Seti - July23 2025 - IMG Factory 1.5 - COL Table Population Methods
# Ported from old working version

"""
COL Table Population Methods - Ported from working old version
Handles populating the main table widget with COL file data
Uses IMG debug system instead of old COL debug calls
"""

import os
from typing import Optional, Any
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

# Import IMG debug system and COL classes
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile, COLModel

##Methods list -
# load_col_file_object
# load_col_file_safely
# populate_col_table_enhanced
# populate_table_with_col_data_debug
# reset_table_styling
# setup_col_tab
# setup_col_tab_integration
# setup_col_table_structure
# update_col_info_bar_enhanced
# validate_col_file

def validate_col_file(main_window, file_path): #vers 1
    """Validate COL file before loading"""
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
    
    return True

def setup_col_tab(main_window, file_path): #vers 1
    """Setup or reuse tab for COL file"""
    try:
        current_index = main_window.main_tab_widget.currentIndex()
        
        # Check if current tab is empty
        if not hasattr(main_window, 'open_files') or current_index not in main_window.open_files:
            img_debugger.debug("Using current tab for COL file")
        else:
            img_debugger.debug("Creating new tab for COL file")
            if hasattr(main_window, 'close_manager'):
                main_window.close_manager.create_new_tab()
                current_index = main_window.main_tab_widget.currentIndex()
            else:
                img_debugger.warning("Close manager not available")
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
        img_debugger.error(f"Error setting up COL tab: {str(e)}")
        return None

def load_col_file_object(main_window, file_path): #vers 1
    """Load COL file object"""
    try:
        from components.col_core_classes import COLFile
        
        img_debugger.debug(f"Loading COL file: {os.path.basename(file_path)}")
        
        # Create COL file object
        col_file = COLFile(file_path)
        
        # Load the file
        if col_file.load():
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            img_debugger.success(f"COL file loaded: {model_count} models")
            return col_file
        else:
            error_details = col_file.load_error if hasattr(col_file, 'load_error') else "Unknown error"
            img_debugger.error(f"Failed to load COL file: {error_details}")
            return None
        
    except Exception as e:
        img_debugger.error(f"Error loading COL file: {str(e)}")
        return None

def setup_col_table_structure(main_window): #vers 1
    """Setup table structure for COL data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("No table widget available")
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

def _populate_col_table_enhanced(main_window, col_file): #vers 1
    """Populate table using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.populate_col_table(col_file)
        img_debugger.success("Enhanced COL table populated")
        
    except Exception as e:
        img_debugger.error(f"Enhanced table population failed: {str(e)}")
        raise

def _update_col_info_bar_enhanced(main_window, col_file, file_path): #vers 1
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        img_debugger.success("Enhanced info bar updated")
        
    except Exception as e:
        img_debugger.error(f"Enhanced info bar update failed: {str(e)}")
        raise

def reset_table_styling(main_window): #vers 1
    """Completely reset table styling to default"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return

        table = main_window.gui_layout.table
        header = table.horizontalHeader()

        # Clear all styling
        table.setStyleSheet("")
        header.setStyleSheet("")
        table.setObjectName("")

        # Reset to basic alternating colors
        table.setAlternatingRowColors(True)

        img_debugger.debug("Table styling completely reset")

    except Exception as e:
        img_debugger.warning(f"Error resetting table styling: {str(e)}")

def setup_col_tab_integration(main_window): #vers 1
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)

        # Add styling reset method
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)

        img_debugger.success("COL tab integration ready")
        return True

    except Exception as e:
        img_debugger.error(f"COL tab integration failed: {str(e)}")
        return False

def populate_table_with_col_data_debug(main_window, col_file): #vers 1
    """Populate table with COL file data using IMG debug system"""
    try:
        if not col_file or not hasattr(col_file, 'models') or not col_file.models:
            img_debugger.warning("No COL data to populate")
            return False
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("No table widget available")
            return False
        
        table = main_window.gui_layout.table
        models = col_file.models
        
        img_debugger.debug(f"Populating table with {len(models)} COL models")
        
        # Setup table structure first
        _setup_col_table_structure(main_window)
        
        # Set row count
        table.setRowCount(len(models))
        
        # Populate each model
        for row, model in enumerate(models):
            # Model Name (Column 0)
            model_name = model.name if hasattr(model, 'name') and model.name else f"Model_{row+1}"
            table.setItem(row, 0, QTableWidgetItem(model_name))
            
            # Type (Column 1)
            table.setItem(row, 1, QTableWidgetItem("COL"))
            
            # Version (Column 2)
            if hasattr(model, 'version') and hasattr(model.version, 'value'):
                version_text = f"v{model.version.value}"
            else:
                version_text = "Unknown"
            table.setItem(row, 2, QTableWidgetItem(version_text))
            
            # Size (Column 3) - Estimate based on data
            sphere_count = len(model.spheres) if hasattr(model, 'spheres') else 0
            box_count = len(model.boxes) if hasattr(model, 'boxes') else 0
            vertex_count = len(model.vertices) if hasattr(model, 'vertices') else 0
            face_count = len(model.faces) if hasattr(model, 'faces') else 0
            
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
            if hasattr(model, 'has_sphere_data') and model.has_sphere_data:
                info_parts.append("Spheres")
            if hasattr(model, 'has_box_data') and model.has_box_data:
                info_parts.append("Boxes")
            if hasattr(model, 'has_mesh_data') and model.has_mesh_data:
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

def populate_col_table_enhanced(main_window, col_file): #vers 1
    """Populate table using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.populate_col_table(col_file)
        img_debugger.success("Enhanced COL table populated")
        
    except Exception as e:
        img_debugger.error(f"Enhanced table population failed: {str(e)}")
        raise

def update_col_info_bar_enhanced(main_window, col_file, file_path): #vers 1
    """Update info bar using enhanced display manager"""
    try:
        from components.col_display import COLDisplayManager
        
        display_manager = COLDisplayManager(main_window)
        display_manager.update_col_info_bar(col_file, file_path)
        img_debugger.success("Enhanced info bar updated")
        
    except Exception as e:
        img_debugger.error(f"Enhanced info bar update failed: {str(e)}")
        raise


def setup_col_table_structure(main_window): #vers 1
    """Setup table structure for COL data"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("Table widget not found")
            return False

        table = main_window.gui_layout.table

        # COL-specific columns
        col_headers = ["Model Name", "Type", "Version", "Size", "Spheres", "Boxes", "Vertices", "Faces"]
        table.setColumnCount(len(col_headers))
        table.setHorizontalHeaderLabels(col_headers)

        # Set column widths for better display
        table.setColumnWidth(0, 200)  # Model Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 80)   # Version
        table.setColumnWidth(3, 100)  # Size
        table.setColumnWidth(4, 80)   # Spheres
        table.setColumnWidth(5, 80)   # Boxes
        table.setColumnWidth(6, 80)   # Vertices
        table.setColumnWidth(7, 80)   # Faces

        # Enable sorting
        table.setSortingEnabled(True)

        img_debugger.debug("COL table structure setup complete")
        return True

    except Exception as e:
        img_debugger.error(f"Error setting up COL table structure: {str(e)}")
        return False

def populate_table_with_col_data_debug(main_window, col_file): #vers 1
    """Populate table with COL data with debug output"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("Table widget not found")
            return False

        table = main_window.gui_layout.table

        if not col_file or not hasattr(col_file, 'models'):
            img_debugger.warning("No COL models to display")
            table.setRowCount(0)
            return False

        models = col_file.models
        img_debugger.debug(f"Populating table with {len(models)} COL models")

        # Set row count
        table.setRowCount(len(models))

        for row, model in enumerate(models):
            try:
                # Model Name
                model_name = getattr(model, 'name', f'Model_{row+1}')
                table.setItem(row, 0, QTableWidgetItem(str(model_name)))

                # Type
                table.setItem(row, 1, QTableWidgetItem("COL"))

                # Version
                version = getattr(model, 'version', 'Unknown')
                if hasattr(version, 'value'):
                    version_text = f"COL{version.value}"
                else:
                    version_text = str(version)
                table.setItem(row, 2, QTableWidgetItem(version_text))

                # Size (approximate)
                size_text = "~"
                if hasattr(model, 'get_stats'):
                    stats = model.get_stats()
                    # Estimate size based on object counts
                    estimated_size = (stats.get('vertices', 0) * 12 +
                                    stats.get('faces', 0) * 16 +
                                    stats.get('spheres', 0) * 20 +
                                    stats.get('boxes', 0) * 32)
                    if estimated_size > 1024:
                        size_text = f"~{estimated_size//1024}KB"
                    else:
                        size_text = f"~{estimated_size}B"
                table.setItem(row, 3, QTableWidgetItem(size_text))

                # Spheres
                spheres_count = len(getattr(model, 'spheres', []))
                table.setItem(row, 4, QTableWidgetItem(str(spheres_count)))

                # Boxes
                boxes_count = len(getattr(model, 'boxes', []))
                table.setItem(row, 5, QTableWidgetItem(str(boxes_count)))

                # Vertices
                vertices_count = len(getattr(model, 'vertices', []))
                table.setItem(row, 6, QTableWidgetItem(str(vertices_count)))

                # Faces
                faces_count = len(getattr(model, 'faces', []))
                table.setItem(row, 7, QTableWidgetItem(str(faces_count)))

            except Exception as e:
                img_debugger.error(f"Error populating row {row}: {str(e)}")
                # Fill with error data
                table.setItem(row, 0, QTableWidgetItem(f"Error_Model_{row}"))
                for col in range(1, 8):
                    table.setItem(row, col, QTableWidgetItem("Error"))

        img_debugger.success(f"COL table populated with {len(models)} models")
        return True

    except Exception as e:
        img_debugger.error(f"Error populating COL table: {str(e)}")
        return False


def load_col_file_safely(main_window, file_path): #vers 1
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
        setup_col_table_structure(main_window)

        # Populate table with COL data (try enhanced first, fallback to debug version)
        try:
            populate_col_table_enhanced(main_window, col_file)
        except Exception as e:
            img_debugger.warning(f"Enhanced table population failed: {str(e)}, using fallback")
            populate_table_with_col_data_debug(main_window, col_file)

        # Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file

        # Update info bar (try enhanced first, fallback to basic)
        try:
            update_col_info_bar_enhanced(main_window, col_file, file_path)
        except Exception as e:
            img_debugger.warning(f"Enhanced info bar update failed: {str(e)}")
            # If enhanced fails, we continue without it

        img_debugger.success(f"COL file loaded: {os.path.basename(file_path)}")
        return True

    except Exception as e:
        img_debugger.error(f"Error loading COL file: {str(e)}")
        return False
