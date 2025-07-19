#this belongs in methods/populate_col_table.py - Version: 5
# X-Seti - July18 2025 - Img Factory 1.5 - Updated COL Table Population

"""
COL Table Population Methods - UPDATED VERSION
Consolidated and updated table population functions using working parser
Integrates with fixed COL parsing system
"""

import os
from typing import Optional, Any, Dict
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

##Methods list -
# create_table_item
# format_collision_display  
# format_file_size
# populate_col_table
# setup_col_table_structure

def create_table_item(text: str, data=None) -> QTableWidgetItem: #vers 5
    """Create standardized table widget item with optional data"""
    item = QTableWidgetItem(str(text))
    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
    if data is not None:
        item.setData(Qt.ItemDataRole.UserRole, data)
    return item

def format_collision_display(model_info: Dict[str, Any]) -> str: #vers 5
    """Format collision types for table display"""
    if not isinstance(model_info, dict):
        return "Unknown"
    
    collision_types = model_info.get('collision_types', [])
    if not collision_types:
        return "No collision"
    
    return ", ".join(collision_types)

def setup_col_table_structure(main_window) -> bool: #vers 5
    """Setup table structure for COL data (7 columns)"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return False

        table = main_window.gui_layout.table
        
        # Configure table for COL data (7 columns)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Set column widths
        table.setColumnWidth(0, 60)   # Model
        table.setColumnWidth(1, 80)   # Type  
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 80)   # Surfaces
        table.setColumnWidth(4, 80)   # Vertices
        table.setColumnWidth(5, 120)  # Collision
        table.setColumnWidth(6, 80)   # Status

        # Apply scoped COL table styling
        table.setObjectName("col_table")
        col_table_style = """
            QTableWidget#col_table {
                background-color: #F8F9FA;
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget#col_table::item {
                padding: 6px;
                border: none;
            }
            QTableWidget#col_table::item:alternate {
                background-color: #F5F5F5;
            }
            QTableWidget#col_table::item:hover {
                background-color: #E3F2FD;
            }
            QTableWidget#col_table::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """

        # Apply table styling
        table.setStyleSheet(col_table_style)

        # Apply header styling
        header = table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #BBDEFB;
                color: #1976D2;
                font-weight: bold;
                border: 1px solid #90CAF9;
                padding: 6px;
            }
            QHeaderView::section:hover {
                background-color: #90CAF9;
            }
        """)

        # Clear existing data
        table.setRowCount(0)

        main_window.log_message("🔧 COL table structure configured")
        return True

    except Exception as e:
        main_window.log_message(f"⚠️ Error setting up COL table structure: {str(e)}")
        return False

def populate_col_table(main_window, col_file: Any) -> bool: #vers 5
    """Populate table with COL data using working parser - UPDATED VERSION"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return False

        table = main_window.gui_layout.table

        # Setup table structure first
        if not setup_col_table_structure(main_window):
            return False

        # Use the working parser from fixed files
        try:
            from components.col_parsing_functions import COLParser, format_model_collision_types

            main_window.log_message("🔧 Using working COL parser for real collision data")
            
            # Create parser instance
            parser = COLParser(debug=True)
            parsed_models = parser.parse_col_file_structure(col_file.file_path)

            if not parsed_models:
                main_window.log_message("⚠️ Parser found no models")
                table.setRowCount(0)
                return True

            # Set row count
            table.setRowCount(len(parsed_models))
            main_window.log_message(f"🔧 Populating table with {len(parsed_models)} COL models")

            # Populate rows with real parsed collision data
            for i, model_info in enumerate(parsed_models):
                try:
                    # Model index
                    table.setItem(i, 0, create_table_item(str(i)))
                    
                    # Type (COL version)
                    version = model_info.get('version', 1)
                    version_str = f"COL{version}"
                    table.setItem(i, 1, create_table_item(version_str))
                    
                    # Size (collision object count)
                    total_objects = (model_info.get('spheres', 0) + 
                                   model_info.get('boxes', 0) + 
                                   model_info.get('vertices', 0))
                    size_str = f"{total_objects} objects"
                    table.setItem(i, 2, create_table_item(size_str))
                    
                    # Surfaces (face count)
                    faces = model_info.get('faces', 0)
                    table.setItem(i, 3, create_table_item(str(faces)))
                    
                    # Vertices
                    vertices = model_info.get('vertices', 0)
                    table.setItem(i, 4, create_table_item(str(vertices)))
                    
                    # Collision types
                    collision_display = format_model_collision_types(model_info)
                    table.setItem(i, 5, create_table_item(collision_display))
                    
                    # Status
                    status = "✅ Loaded"
                    table.setItem(i, 6, create_table_item(status))
                    
                except Exception as e:
                    main_window.log_message(f"⚠️ Error populating row {i}: {str(e)}")
                    # Fill with error data
                    table.setItem(i, 0, create_table_item(str(i)))
                    table.setItem(i, 1, create_table_item("ERROR"))
                    table.setItem(i, 2, create_table_item("0 objects"))
                    table.setItem(i, 3, create_table_item("0"))
                    table.setItem(i, 4, create_table_item("0"))
                    table.setItem(i, 5, create_table_item("Parse Error"))
                    table.setItem(i, 6, create_table_item("❌ Error"))

            main_window.log_message(f"✅ COL table populated with real data: {len(parsed_models)} models")
            return True

        except ImportError as e:
            main_window.log_message(f"❌ Working COL parser not available: {str(e)}")
            # Fallback to basic COL file data
            return _populate_col_table_fallback(main_window, col_file)

    except Exception as e:
        main_window.log_message(f"❌ Error populating COL table: {str(e)}")
        return False

def _populate_col_table_fallback(main_window, col_file) -> bool: #vers 5
    """Fallback COL table population when parser unavailable"""
    try:
        table = main_window.gui_layout.table
        main_window.log_message("⚠️ Using fallback COL table population")

        if not hasattr(col_file, 'models') or not col_file.models:
            table.setRowCount(0)
            return True

        table.setRowCount(len(col_file.models))
        
        for i, model in enumerate(col_file.models):
            try:
                # Basic model info
                table.setItem(i, 0, create_table_item(str(i)))
                table.setItem(i, 1, create_table_item("COL"))
                table.setItem(i, 2, create_table_item("Unknown"))
                table.setItem(i, 3, create_table_item("0"))
                table.setItem(i, 4, create_table_item("0"))
                table.setItem(i, 5, create_table_item("Parser unavailable"))
                table.setItem(i, 6, create_table_item("⚠ Limited"))
                
            except Exception as e:
                main_window.log_message(f"⚠️ Error in fallback row {i}: {str(e)}")

        main_window.log_message(f"⚠️ COL table populated with fallback data: {len(col_file.models)} models")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Fallback population failed: {str(e)}")
        return False

def populate_col_table_enhanced(main_window, col_file: Any) -> bool: #vers 5
    """Enhanced COL table population with detailed statistics and advanced formatting"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            main_window.log_message("⚠️ Main table not available")
            return False

        table = main_window.gui_layout.table
        main_window.log_message("🔧 Using enhanced COL table population")

        # Setup enhanced table structure 
        if not setup_col_table_structure(main_window):
            return False

        # Try to use COLDisplayManager for advanced features
        try:
            from components.col_display import COLDisplayManager
            
            main_window.log_message("🎨 Using COLDisplayManager for enhanced display")
            display_manager = COLDisplayManager(main_window)
            success = display_manager.populate_col_table(col_file)
            
            if success:
                main_window.log_message("✅ Enhanced COL table populated successfully")
                return True
            else:
                main_window.log_message("⚠️ COLDisplayManager failed, falling back to standard population")
                
        except ImportError:
            main_window.log_message("⚠️ COLDisplayManager not available, using enhanced standard population")

        # Enhanced standard population (fallback)
        return _populate_col_table_enhanced_standard(main_window, col_file)

    except Exception as e:
        main_window.log_message(f"❌ Enhanced COL table population failed: {str(e)}")
        # Final fallback to basic population
        return populate_col_table(main_window, col_file)

def _populate_col_table_enhanced_standard(main_window, col_file) -> bool: #vers 5
    """Enhanced standard population without COLDisplayManager dependency"""
    try:
        table = main_window.gui_layout.table

        # Use the working parser for enhanced data
        try:
            from components.col_parsing_functions import COLParser, format_model_collision_types

            parser = COLParser(debug=True)
            parsed_models = parser.parse_col_file_structure(col_file.file_path)

            if not parsed_models:
                main_window.log_message("⚠️ Parser found no models")
                table.setRowCount(0)
                return True

            table.setRowCount(len(parsed_models))
            main_window.log_message(f"🎨 Enhanced population: {len(parsed_models)} models")

            # Enhanced population with better formatting
            for i, model_info in enumerate(parsed_models):
                try:
                    # Enhanced model name with index
                    model_name = f"Model_{i+1}"
                    if hasattr(col_file, 'models') and i < len(col_file.models):
                        model = col_file.models[i]
                        if hasattr(model, 'name') and model.name:
                            model_name = model.name
                    
                    table.setItem(i, 0, create_table_item(model_name))
                    
                    # Enhanced type with detailed version
                    version = model_info.get('version', 1)
                    version_str = f"COL{version}"
                    if version == 1:
                        version_str += " (Legacy)"
                    elif version >= 3:
                        version_str += " (Modern)"
                    table.setItem(i, 1, create_table_item(version_str))
                    
                    # Enhanced size calculation
                    spheres = model_info.get('spheres', 0)
                    boxes = model_info.get('boxes', 0) 
                    vertices = model_info.get('vertices', 0)
                    total_objects = spheres + boxes + vertices
                    
                    if total_objects > 0:
                        size_str = f"{total_objects} obj"
                        if spheres > 0 and boxes > 0 and vertices > 0:
                            size_str += " (Mixed)"
                        elif vertices > 0:
                            size_str += " (Mesh)"
                        else:
                            size_str += " (Simple)"
                    else:
                        size_str = "No collision"
                    table.setItem(i, 2, create_table_item(size_str))
                    
                    # Enhanced surface count
                    faces = model_info.get('faces', 0)
                    surface_str = str(faces) if faces > 0 else "None"
                    table.setItem(i, 3, create_table_item(surface_str))
                    
                    # Enhanced vertex count with detail
                    vertex_str = str(vertices) if vertices > 0 else "None"
                    if vertices > 1000:
                        vertex_str += " (Complex)"
                    elif vertices > 100:
                        vertex_str += " (Detailed)"
                    table.setItem(i, 4, create_table_item(vertex_str))
                    
                    # Enhanced collision types display
                    collision_display = format_model_collision_types(model_info)
                    if not collision_display or collision_display == "No collision":
                        collision_display = "❌ None"
                    else:
                        collision_display = f"✅ {collision_display}"
                    table.setItem(i, 5, create_table_item(collision_display))
                    
                    # Enhanced status with more detail
                    if total_objects > 0:
                        if vertices > 0:
                            status = "🎯 Mesh Ready"
                        else:
                            status = "🔘 Primitive"
                    else:
                        status = "⚠️ Empty"
                    table.setItem(i, 6, create_table_item(status))
                    
                except Exception as e:
                    main_window.log_message(f"⚠️ Error in enhanced row {i}: {str(e)}")
                    # Enhanced error display
                    table.setItem(i, 0, create_table_item(f"Model_{i+1}"))
                    table.setItem(i, 1, create_table_item("❌ ERROR"))
                    table.setItem(i, 2, create_table_item("Unknown"))
                    table.setItem(i, 3, create_table_item("?"))
                    table.setItem(i, 4, create_table_item("?"))
                    table.setItem(i, 5, create_table_item("❌ Parse Error"))
                    table.setItem(i, 6, create_table_item("💥 Failed"))

            main_window.log_message(f"✅ Enhanced COL table populated: {len(parsed_models)} models")
            return True

        except ImportError as e:
            main_window.log_message(f"❌ Enhanced parser not available: {str(e)}")
            return _populate_col_table_fallback(main_window, col_file)

    except Exception as e:
        main_window.log_message(f"❌ Enhanced standard population failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'populate_col_table',
    'populate_col_table_enhanced',  # Added enhanced version
    'setup_col_table_structure', 
    'create_table_item',
    'format_file_size',
    'format_collision_display'
]
