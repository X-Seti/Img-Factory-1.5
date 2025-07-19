#this belongs in components/col_display.py - Version: 2
# X-Seti - July17 2025 - IMG Factory 1.5 - COL Display Management
# IMG Debug Treatment + Integrated Table Population Functions

"""
COL Display Management
Complete COL file display and table population using IMG debug system
INTEGRATED: Table population functions moved here from other files
"""

import os
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Import COL classes and IMG debug system
from components.col_core_classes import COLFile, COLModel
from components.col_debug_functions import col_debug_log, is_col_debug_enabled
from components.img_debug_functions import img_debugger

print(f"[DEBUG] gui.col_display calling: with args={Path}")
##Methods list -
# create_table_item
# format_collision_types
# get_enhanced_model_stats
# populate_col_table
# populate_col_table_enhanced
# populate_col_table_img_format
# setup_col_table_structure
# update_col_info_bar_enhanced

##Classes -
# COLDisplayManager

def create_table_item(text: str, data=None) -> QTableWidgetItem: #vers 1
    """Create standardized table widget item"""
    item = QTableWidgetItem(str(text))
    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
    if data is not None:
        item.setData(Qt.ItemDataRole.UserRole, data)
    return item

def format_collision_types(stats: Dict[str, Any]) -> str: #vers 1
    """Format collision types for display"""
    types = []
    
    if stats.get('sphere_count', 0) > 0:
        types.append(f"S:{stats['sphere_count']}")
    if stats.get('box_count', 0) > 0:
        types.append(f"B:{stats['box_count']}")
    if stats.get('face_count', 0) > 0:
        types.append(f"M:{stats['face_count']}")
    
    return ", ".join(types) if types else "None"

def get_enhanced_model_stats(model: COLModel, col_file: COLFile, model_index: int) -> Dict[str, Any]: #vers 1
    """Get enhanced model statistics using IMG debug system"""
    try:
        col_debug_log(None, f"Getting stats for model {model_index}", 'COL_DISPLAY')
        
        stats = {
            'sphere_count': 0,
            'box_count': 0,
            'vertex_count': 0,
            'face_count': 0,
            'total_elements': 0,
            'estimated_size': 64,
            'collision_types': 'None'
        }
        
        # Get basic collision data
        if hasattr(model, 'spheres') and model.spheres:
            stats['sphere_count'] = len(model.spheres)
        
        if hasattr(model, 'boxes') and model.boxes:
            stats['box_count'] = len(model.boxes)
            
        if hasattr(model, 'vertices') and model.vertices:
            stats['vertex_count'] = len(model.vertices)
            
        if hasattr(model, 'faces') and model.faces:
            stats['face_count'] = len(model.faces)
        
        # Calculate total collision elements
        stats['total_elements'] = stats['sphere_count'] + stats['box_count'] + stats['face_count']
        
        # Estimate size in bytes
        size = stats['sphere_count'] * 20  # Sphere data
        size += stats['box_count'] * 48   # Box data
        size += stats['vertex_count'] * 12  # Vertex data
        size += stats['face_count'] * 12    # Face data
        stats['estimated_size'] = max(size, 64)
        
        # Format collision types
        stats['collision_types'] = format_collision_types(stats)
        
        if is_col_debug_enabled():
            img_debugger.debug(f"Model {model_index} stats: {stats}")
        
        return stats
        
    except Exception as e:
        col_debug_log(None, f"Error getting model stats: {e}", 'COL_DISPLAY', 'ERROR')
        return stats

def setup_col_table_structure(main_window) -> bool: #vers 1
    """Setup table structure for COL data display - MOVED from core/loadcol.py"""
    try:
        col_debug_log(main_window, "Setting up COL table structure", 'COL_DISPLAY')
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            col_debug_log(main_window, "Main table not available", 'COL_DISPLAY', 'ERROR')
            return False

        table = main_window.gui_layout.table

        # Configure table for COL data (7 columns for enhanced display)
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
        ])

        # Set column widths optimized for COL data
        table.setColumnWidth(0, 120)  # Model name
        table.setColumnWidth(1, 80)   # Type (COL1/2/3/4)
        table.setColumnWidth(2, 100)  # Size
        table.setColumnWidth(3, 100)  # Surface count
        table.setColumnWidth(4, 100)  # Vertex count
        table.setColumnWidth(5, 150)  # Collision types
        table.setColumnWidth(6, 80)   # Status

        # Apply COL-specific styling
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #f0f8ff;
                alternate-background-color: #e6f3ff;
                selection-background-color: #4169e1;
                gridline-color: #b0c4de;
            }
            QHeaderView::section {
                background-color: #1e3a8a;
                color: white;
                font-weight: bold;
                border: 1px solid #1e40af;
                padding: 6px;
            }
        """)
        
        col_debug_log(main_window, "COL table structure configured successfully", 'COL_DISPLAY', 'SUCCESS')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error setting up COL table structure: {str(e)}", 'COL_DISPLAY', 'ERROR')
        return False

def populate_col_table(main_window, col_file: COLFile) -> bool: #vers 1
    """Basic COL table population - MOVED from core/loadcol.py"""
    try:
        col_debug_log(main_window, "Populating COL table with basic data", 'COL_DISPLAY')
        
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            col_debug_log(main_window, "Main table not available", 'COL_DISPLAY', 'ERROR')
            return False
        
        table = main_window.gui_layout.table
        
        if not hasattr(col_file, 'models') or not col_file.models:
            col_debug_log(main_window, "No COL models to display", 'COL_DISPLAY', 'WARNING')
            table.setRowCount(0)
            return True
        
        # Set row count
        table.setRowCount(len(col_file.models))
        col_debug_log(main_window, f"Displaying {len(col_file.models)} COL models", 'COL_DISPLAY')
        
        # Populate rows with basic data
        for i, model in enumerate(col_file.models):
            try:
                # Model name
                model_name = getattr(model, 'name', f'Model_{i+1}')
                table.setItem(i, 0, create_table_item(model_name))
                
                # Model type
                version = getattr(model, 'version', None)
                if version and hasattr(version, 'value'):
                    model_type = f"COL{version.value}"
                else:
                    model_type = "COL"
                table.setItem(i, 1, create_table_item(model_type))
                
                # Basic collision data counts
                sphere_count = len(getattr(model, 'spheres', []))
                box_count = len(getattr(model, 'boxes', []))
                triangle_count = len(getattr(model, 'faces', []))
                
                # Size estimate
                size_estimate = (sphere_count * 20) + (box_count * 48) + (triangle_count * 36)
                table.setItem(i, 2, create_table_item(format_file_size(max(size_estimate, 64))))
                
                # Surface count (total collision elements)
                surface_count = sphere_count + box_count + triangle_count
                table.setItem(i, 3, create_table_item(str(surface_count)))
                
                # Vertex count
                vertex_count = len(getattr(model, 'vertices', []))
                table.setItem(i, 4, create_table_item(str(vertex_count)))
                
                # Collision types
                collision_types = format_collision_types({
                    'sphere_count': sphere_count,
                    'box_count': box_count,
                    'face_count': triangle_count
                })
                table.setItem(i, 5, create_table_item(collision_types))
                
                # Status
                status = "✅ Loaded" if surface_count > 0 else "⚠️ Empty"
                table.setItem(i, 6, create_table_item(status))
                
            except Exception as e:
                col_debug_log(main_window, f"Error populating model {i}: {str(e)}", 'COL_DISPLAY', 'ERROR')
                # Fill with placeholder data
                for col in range(7):
                    table.setItem(i, col, create_table_item("Error" if col == 0 else "?"))
        
        col_debug_log(main_window, "COL table populated successfully", 'COL_DISPLAY', 'SUCCESS')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error populating COL table: {str(e)}", 'COL_DISPLAY', 'ERROR')
        return False

def populate_col_table_enhanced(main_window, col_file: COLFile) -> bool: #vers 1
    """Enhanced COL table population with detailed statistics"""
    try:
        col_debug_log(main_window, "Populating COL table with enhanced data", 'COL_DISPLAY')
        
        # Use display manager for enhanced population
        display_manager = COLDisplayManager(main_window)
        return display_manager.populate_col_table(col_file)
        
    except Exception as e:
        col_debug_log(main_window, f"Enhanced COL table population failed: {str(e)}", 'COL_DISPLAY', 'ERROR')
        # Fallback to basic population
        return populate_col_table(main_window, col_file)

def populate_col_table_img_format(main_window, col_file: COLFile) -> bool: #vers 1
    """Populate COL table using IMG-style formatting - MOVED from core/tables_structure.py"""
    try:
        col_debug_log(main_window, "Populating COL table with IMG-style formatting", 'COL_DISPLAY')
        
        # Setup table structure first
        if not setup_col_table_structure(main_window):
            return False
        
        # Use enhanced population for IMG-style display
        return populate_col_table_enhanced(main_window, col_file)
        
    except Exception as e:
        col_debug_log(main_window, f"IMG-format COL population failed: {str(e)}", 'COL_DISPLAY', 'ERROR')
        return False

def update_col_info_bar_enhanced(main_window, col_file: COLFile, file_path: str) -> bool: #vers 1
    """Update info bar with enhanced COL data - MOVED from gui/gui_infobar.py"""
    try:
        col_debug_log(main_window, "Updating COL info bar with enhanced data", 'COL_DISPLAY')
        
        gui_layout = main_window.gui_layout
        
        # Update file count
        if hasattr(gui_layout, 'file_count_label'):
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            gui_layout.file_count_label.setText(f"Models: {model_count}")
        
        # Update file size
        if hasattr(gui_layout, 'file_size_label'):
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            size_str = format_file_size(file_size)
            gui_layout.file_size_label.setText(f"Size: {size_str}")
        
        # Update format version
        if hasattr(gui_layout, 'format_version_label'):
            version = getattr(col_file, 'version', 'Unknown')
            gui_layout.format_version_label.setText(f"Format: COL v{version}")
        
        # Calculate total collision elements
        total_elements = 0
        if hasattr(col_file, 'models'):
            for model in col_file.models:
                stats = get_enhanced_model_stats(model, col_file, 0)
                total_elements += stats.get('total_elements', 0)
        
        # Update additional info if available
        if hasattr(gui_layout, 'additional_info_label'):
            gui_layout.additional_info_label.setText(f"Collision Elements: {total_elements}")
        
        col_debug_log(main_window, "COL info bar updated successfully", 'COL_DISPLAY', 'SUCCESS')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error updating COL info bar: {str(e)}", 'COL_DISPLAY', 'ERROR')
        return False

class COLDisplayManager:
    """Enhanced COL display management with IMG debug integration"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        col_debug_log(main_window, "COL Display Manager initialized", 'COL_DISPLAY')
    
    def populate_col_table(self, col_file: COLFile) -> bool:
        """Enhanced table population with detailed model analysis"""
        try:
            col_debug_log(self.main_window, "Enhanced COL table population starting", 'COL_DISPLAY')
            
            if not hasattr(self.main_window, 'gui_layout') or not hasattr(self.main_window.gui_layout, 'table'):
                col_debug_log(self.main_window, "Main table not available for enhanced display", 'COL_DISPLAY', 'ERROR')
                return False
            
            table = self.main_window.gui_layout.table
            
            if not hasattr(col_file, 'models') or not col_file.models:
                col_debug_log(self.main_window, "No COL models available for enhanced display", 'COL_DISPLAY', 'WARNING')
                table.setRowCount(0)
                return True
            
            # Setup enhanced table structure
            table.setRowCount(len(col_file.models))
            
            # Populate with enhanced data
            for row, model in enumerate(col_file.models):
                try:
                    # Get enhanced statistics
                    stats = get_enhanced_model_stats(model, col_file, row)
                    
                    # Model name with enhanced formatting
                    model_name = getattr(model, 'name', f'Model_{row+1}')
                    table.setItem(row, 0, create_table_item(model_name, model))
                    
                    # Model type with version info
                    version = getattr(model, 'version', None)
                    if version and hasattr(version, 'value'):
                        model_type = f"COL{version.value}"
                    else:
                        model_type = "Collision"
                    table.setItem(row, 1, create_table_item(model_type))
                    
                    # Enhanced size calculation
                    model_size = stats.get('estimated_size', 64)
                    size_str = format_file_size(model_size)
                    table.setItem(row, 2, create_table_item(size_str))
                    
                    # Surface count (total collision elements)
                    surface_count = stats.get('total_elements', 0)
                    table.setItem(row, 3, create_table_item(str(surface_count)))
                    
                    # Vertex count
                    vertex_count = stats.get('vertex_count', 0)
                    table.setItem(row, 4, create_table_item(str(vertex_count)))
                    
                    # Enhanced collision types
                    collision_types = stats.get('collision_types', 'None')
                    table.setItem(row, 5, create_table_item(collision_types))
                    
                    # Enhanced status
                    if surface_count > 100:
                        status = "🔥 Complex"
                    elif surface_count > 10:
                        status = "✅ Normal"
                    elif surface_count > 0:
                        status = "⚡ Simple"
                    else:
                        status = "⚠️ Empty"
                    table.setItem(row, 6, create_table_item(status))
                    
                    if is_col_debug_enabled():
                        col_debug_log(self.main_window, f"Enhanced row {row}: {model_name} - {surface_count} elements", 'COL_DISPLAY')
                    
                except Exception as e:
                    col_debug_log(self.main_window, f"Error in enhanced population for model {row}: {str(e)}", 'COL_DISPLAY', 'ERROR')
                    # Fill with error indicators
                    for col in range(7):
                        table.setItem(row, col, create_table_item("Error" if col == 0 else "?"))
            
            col_debug_log(self.main_window, "Enhanced COL table population completed successfully", 'COL_DISPLAY', 'SUCCESS')
            return True
            
        except Exception as e:
            col_debug_log(self.main_window, f"Enhanced COL table population failed: {str(e)}", 'COL_DISPLAY', 'ERROR')
            return False
    
    def update_col_info_bar(self, col_file: COLFile, file_path: str) -> bool:
        """Update info bar with enhanced COL statistics"""
        return update_col_info_bar_enhanced(self.main_window, col_file, file_path)

# Export main functions
__all__ = [
    'COLDisplayManager',
    'create_table_item',
    'format_collision_types',
    'get_enhanced_model_stats',
    'populate_col_table',
    'populate_col_table_enhanced',
    'populate_col_table_img_format',
    'setup_col_table_structure',
    'update_col_info_bar_enhanced'
]
