#this belongs in components/ col_display.py - Version: 1
# X-Seti - July08 2025 - COL Display Functions for IMG Factory 1.5

"""
COL Display Manager
Handles displaying COL data in IMG Factory table with accurate statistics
"""

import os
import struct
from PyQt6.QtWidgets import QTableWidgetItem

class COLDisplayManager:
    """Manages COL data display in IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def populate_col_table(self, col_file):
        """Populate table with COL models using enhanced statistics"""
        try:
            if not hasattr(self.main_window, 'gui_layout') or not hasattr(self.main_window.gui_layout, 'table'):
                self.main_window.log_message("⚠️ Main table not available")
                return
            
            table = self.main_window.gui_layout.table
            
            # Configure table for COL data (7 columns)
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "Model", "Type", "Size", "Surfaces", "Vertices", "Collision", "Status"
            ])
            
            # Clear existing data
            table.setRowCount(0)
            
            if not hasattr(col_file, 'models') or not col_file.models:
                self.main_window.log_message("⚠️ No models found in COL file")
                return
            
            table.setRowCount(len(col_file.models))
            self.main_window.log_message(f"🔧 Populating table with {len(col_file.models)} COL models")
            
            for row, model in enumerate(col_file.models):
                # Get enhanced model statistics
                stats = self._get_enhanced_model_stats(model, col_file, row)
                
                # Model name/index
                model_name = getattr(model, 'name', f"Model_{row+1}")
                if not model_name or model_name.strip() == "":
                    model_name = f"Model_{row+1}"
                table.setItem(row, 0, QTableWidgetItem(str(model_name)))
                
                # Model type - show COL version
                version = getattr(model, 'version', None)
                if version and hasattr(version, 'name'):
                    model_type = f"COL {version.name.replace('COL_', '')}"
                else:
                    model_type = "Collision"
                table.setItem(row, 1, QTableWidgetItem(model_type))
                
                # Calculate model size
                model_size = stats.get('estimated_size', 64)
                size_str = self._format_file_size(model_size)
                table.setItem(row, 2, QTableWidgetItem(size_str))
                
                # Surface count (total collision elements)
                surface_count = stats.get('total_elements', 0)
                table.setItem(row, 3, QTableWidgetItem(str(surface_count)))
                
                # Vertex count
                vertex_count = stats.get('vertex_count', 0)
                table.setItem(row, 4, QTableWidgetItem(str(vertex_count)))
                
                # Collision types
                collision_types = stats.get('collision_types', 'None')
                table.setItem(row, 5, QTableWidgetItem(collision_types))
                
                # Status
                status = "✅ Loaded" if stats.get('total_elements', 0) > 0 else "⚠️ Empty"
                table.setItem(row, 6, QTableWidgetItem(status))
            
            self.main_window.log_message("✅ COL table populated with enhanced data")
            
        except Exception as e:
            self.main_window.log_message(f"⚠️ Error populating COL table: {str(e)}")
    
    def _get_enhanced_model_stats(self, model, col_file, model_index):
        """Get enhanced model statistics using centralized parser"""
        try:
            # Try using the centralized COL parser first
            try:
                from components.col_parsing_functions import get_model_collision_stats, format_model_collision_types
                
                # Get stats from centralized parser with debug
                stats = get_model_collision_stats(col_file.file_path, model_index, debug=True)
                
                # Add collision types formatting
                stats['collision_types'] = format_model_collision_types(stats)
                
                self.main_window.log_message(f"📊 Model {model_index}: Enhanced stats from parser")
                return stats
                
            except ImportError:
                self.main_window.log_message("⚠️ Centralized COL parser not available")
                
            # Fallback to basic stats from model attributes
            stats = {
                'sphere_count': getattr(model, 'num_spheres', 0),
                'box_count': getattr(model, 'num_boxes', 0),
                'vertex_count': getattr(model, 'num_vertices', 0),
                'face_count': getattr(model, 'num_faces', 0)
            }
            
            # If stats are all zeros, try direct binary reading
            if all(v == 0 for v in stats.values()) and hasattr(col_file, 'file_path'):
                self.main_window.log_message(f"🔍 Model {model_index}: Using direct binary reading")
                stats = self._read_model_collision_stats_direct(col_file.file_path, model_index, model)
            
            # Calculate totals and types
            stats['total_elements'] = stats['sphere_count'] + stats['box_count'] + stats['face_count']
            
            # Generate collision types string
            types = []
            if stats['sphere_count'] > 0:
                types.append(f"Spheres({stats['sphere_count']})")
            if stats['box_count'] > 0:
                types.append(f"Boxes({stats['box_count']})")
            if stats['face_count'] > 0:
                types.append(f"Mesh({stats['face_count']})")
            
            stats['collision_types'] = ", ".join(types) if types else "None"
            
            # Estimate size
            stats['estimated_size'] = self._estimate_model_size(stats)
            
            return stats
            
        except Exception as e:
            self.main_window.log_message(f"⚠️ Error getting model stats: {str(e)}")
            return {
                'sphere_count': 0,
                'box_count': 0,
                'vertex_count': 0,
                'face_count': 0,
                'total_elements': 0,
                'collision_types': 'Error',
                'estimated_size': 64
            }
    
    def _read_model_collision_stats_direct(self, file_path, model_index, model):
        """Direct binary reading as fallback (legacy method)"""
        try:
            self.main_window.log_message(f"🔍 Direct reading model {model_index} from {os.path.basename(file_path)}")
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Simple approach: try to find model by signature pattern
            offset = 0
            current_model = 0
            
            while offset < len(data) and current_model <= model_index:
                # Look for COL signature
                sig_pos = data.find(b'COL', offset)
                if sig_pos == -1:
                    break
                
                # Validate it's a proper signature
                if sig_pos + 4 <= len(data):
                    full_sig = data[sig_pos:sig_pos+4]
                    if full_sig in [b'COLL', b'COL2', b'COL3', b'COL4']:
                        
                        if current_model == model_index:
                            # Found our target model
                            stats = self._extract_collision_stats_at_offset(data, sig_pos)
                            self.main_window.log_message(f"📊 Direct stats for model {model_index}: {stats}")
                            return stats
                        
                        current_model += 1
                        offset = sig_pos + 4
                    else:
                        offset = sig_pos + 1
                else:
                    break
            
            self.main_window.log_message(f"⚠️ Could not find model {model_index} in file")
            return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
            
        except Exception as e:
            self.main_window.log_message(f"⚠️ Direct reading error: {str(e)}")
            return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
    
    def _extract_collision_stats_at_offset(self, data, sig_offset):
        """Extract collision stats starting from signature offset"""
        try:
            offset = sig_offset
            
            # Read signature to determine version
            signature = data[offset:offset+4]
            is_col1 = (signature == b'COLL')
            offset += 4
            
            # Skip file size, name, ID, bounds
            offset += 4 + 22 + 2  # size + name + id
            offset += 40 if is_col1 else 28  # bounds
            
            # Skip unknown data for COL1
            if is_col1 and offset + 4 <= len(data):
                unknown_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (unknown_count * 8)
            
            # Read collision counts
            stats = {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
            
            # Spheres
            if offset + 4 <= len(data):
                stats['sphere_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (stats['sphere_count'] * 20)
            
            # Boxes
            if offset + 4 <= len(data):
                stats['box_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (stats['box_count'] * 28)
            
            # Vertices
            if offset + 4 <= len(data):
                stats['vertex_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                vertex_size = 12 if is_col1 else 6
                offset += 4 + (stats['vertex_count'] * vertex_size)
            
            # Faces
            if offset + 4 <= len(data):
                stats['face_count'] = struct.unpack('<I', data[offset:offset+4])[0]
            
            return stats
            
        except Exception as e:
            return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
    
    def _skip_model_collision_data(self, data, offset, is_col1):
        """Skip a model's collision data and return new offset"""
        try:
            # Skip spheres
            if offset + 4 <= len(data):
                sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (sphere_count * 20)
            
            # Skip boxes  
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (box_count * 28)
            
            # Skip vertices
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                vertex_size = 12 if is_col1 else 6
                offset += 4 + (vertex_count * vertex_size)
            
            # Skip faces
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                face_size = 16 if is_col1 else 8
                offset += 4 + (face_count * face_size)
            
            # Skip face groups for COL2/3 (if present)
            if not is_col1 and offset + 4 <= len(data):
                face_group_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (face_group_count * 28)  # Face group size
            
            # Skip shadow mesh for COL3 (if present)
            if not is_col1 and offset + 4 <= len(data):
                # Try to detect shadow mesh by checking remaining data
                remaining = len(data) - offset
                if remaining > 8:  # Enough for shadow vertex/face counts
                    shadow_vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                    if shadow_vertex_count < 10000:  # Sanity check
                        offset += 4 + (shadow_vertex_count * 6)  # Shadow vertices
                        if offset + 4 <= len(data):
                            shadow_face_count = struct.unpack('<I', data[offset:offset+4])[0]
                            if shadow_face_count < 10000:  # Sanity check
                                offset += 4 + (shadow_face_count * 8)  # Shadow faces
            
            return offset
            
        except Exception:
            return offset
    
    def _estimate_model_size(self, stats):
        """Estimate model size in bytes from statistics"""
        size = 64  # Base model overhead
        size += stats['sphere_count'] * 20  # Sphere data
        size += stats['box_count'] * 28  # Box data  
        size += stats['vertex_count'] * 12  # Vertex data (average)
        size += stats['face_count'] * 12  # Face data (average)
        return max(size, 64)
    
    def _format_file_size(self, size_bytes):
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"
    
    def update_col_info_bar(self, col_file, file_path):
        """Update info bar with COL file information"""
        try:
            gui_layout = self.main_window.gui_layout
            
            # Update file count
            if hasattr(gui_layout, 'file_count_label'):
                model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
                gui_layout.file_count_label.setText(f"Models: {model_count}")
            
            # Update file size
            if hasattr(gui_layout, 'file_size_label'):
                file_size = os.path.getsize(file_path)
                size_str = self._format_file_size(file_size)
                gui_layout.file_size_label.setText(f"Size: {size_str}")
            
            # Update format version
            if hasattr(gui_layout, 'format_version_label'):
                version = getattr(col_file, 'version', 'Unknown')
                gui_layout.format_version_label.setText(f"Format: COL v{version}")
            
            self.main_window.log_message("✅ Info bar updated for COL file")
            
        except Exception as e:
            self.main_window.log_message(f"⚠️ Error updating info bar: {str(e)}")

# Standalone functions for use without class
def populate_col_table_with_enhanced_data(main_window, col_file):
    """Standalone function to populate COL table with enhanced data"""
    display_manager = COLDisplayManager(main_window)
    display_manager.populate_col_table(col_file)

def update_col_info_bar_enhanced(main_window, col_file, file_path):
    """Standalone function to update info bar with enhanced COL data"""
    display_manager = COLDisplayManager(main_window)
    display_manager.update_col_info_bar(col_file, file_path)
