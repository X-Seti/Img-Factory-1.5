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


class COLDisplayManager:
    """Enhanced COL display management with IMG debug integration"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        col_debug_log(main_window, "COL Display Manager initialized", 'COL_DISPLAY')

    def update_col_info_bar(self, col_file: COLFile, file_path: str) -> bool:
        """Update info bar with enhanced COL statistics"""
        return update_col_info_bar_enhanced(self.main_window, col_file, file_path)

# Export main functions
__all__ = [
    'COLDisplayManager',
    'create_table_item',
    'format_collision_types',
    'get_enhanced_model_stats'
]
