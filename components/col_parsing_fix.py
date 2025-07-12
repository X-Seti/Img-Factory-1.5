#this belongs in components/ col_parsing_functions.py - Version: 4
# X-Seti - July12 2025 - COL Parsing Functions - FIXED DEBUG CONTROL

"""
COL Parsing Functions - CLEAN VERSION with proper debug control
Unified debug system that respects global COL debug settings
"""

import os
import struct
from typing import List, Dict, Tuple, Optional

# Import global debug control
from components.col_core_classes import is_col_debug_enabled


class COLParser:
    """Enhanced COL parser with proper debug control"""
    
    def __init__(self, debug=None):
        # Use global debug setting if not specified
        if debug is None:
            self.debug = is_col_debug_enabled()
        else:
            self.debug = debug
        
        self.log_messages = []
    
    def log(self, message):
        """Log debug message only if global debug is enabled"""
        # Always check global debug setting
        if is_col_debug_enabled():
            print(f"🔍 COLParser: {message}")
        self.log_messages.append(message)
    
    def set_debug(self, enabled):
        """Update debug setting - now syncs with global setting"""
        self.debug = enabled
        # Also update global setting to keep them in sync
        from components.col_core_classes import set_col_debug_enabled
        set_col_debug_enabled(enabled)
    
    def parse_col_file_structure(self, file_path):
        """Parse complete COL file and return structure info for all models"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.log(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")
            
            # CRITICAL FIX: First check if this is a multi-model COL archive
            if self._is_multi_model_archive(data):
                return self._parse_multi_model_archive(data)
            
            # Single model parsing (original approach)
            models = []
            offset = 0
            model_index = 0
            
            while offset < len(data):
                self.log(f"\n--- Model {model_index} at offset {offset} ---")
                
                # Check if we have enough data for a model
                if offset + 32 > len(data):
                    self.log(f"Not enough data for model header (need 32, have {len(data) - offset})")
                    break
                
                # Parse this model
                model_info, new_offset = self.parse_single_model(data, offset, model_index)
                
                if model_info is None:
                    self.log(f"Failed to parse model {model_index}, stopping")
                    break
                
                models.append(model_info)
                
                # Check if we advanced
                if new_offset <= offset:
                    self.log(f"Offset didn't advance (was {offset}, now {new_offset}), stopping")
                    break
                
                offset = new_offset
                model_index += 1
                
                self.log(f"Model {model_index - 1} parsed successfully, next offset: {offset}")
                
                # Safety check - don't parse more than 200 models
                if model_index > 200:
                    self.log("Safety limit reached (200 models), stopping")
                    break
            
            self.log(f"\nParsing complete: {len(models)} models found")
            return models
            
        except Exception as e:
            self.log(f"Error parsing COL file: {str(e)}")
            return []
    
    def parse_single_model(self, data, offset, model_index):
        """Parse single COL model at given offset"""
        try:
            if offset + 8 > len(data):
                self.log(f"Not enough data for signature at offset {offset}")
                return None, offset
            
            # Read signature
            signature = data[offset:offset+4]
            
            self.log(f"Found {signature} at offset {offset}")
            
            if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                self.log(f"Invalid signature: {signature}")
                # Try to find next valid signature
                next_offset = self._find_next_signature(data, offset + 1)
                if next_offset > 0:
                    return None, next_offset
                else:
                    return None, len(data)  # End of data
            
            # Read file size
            try:
                file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
                self.log(f"Model size: {file_size} bytes")
            except struct.error:
                self.log("Failed to read file size")
                return None, offset + 8
            
            # Validate size
            total_size = file_size + 8
            if offset + total_size > len(data):
                self.log(f"Model extends beyond file (needs {total_size}, available {len(data) - offset})")
                return None, len(data)  # Skip to end
            
            # Extract model data
            model_data = data[offset + 8:offset + total_size]
            
            # Parse based on version
            if signature == b'COLL':
                model_info = self._parse_col1_info(model_data, model_index)
            else:
                model_info = self._parse_col23_info(model_data, model_index, signature)
            
            if model_info:
                model_info['file_offset'] = offset
                model_info['file_size'] = file_size
                model_info['total_size'] = total_size
                model_info['version'] = signature.decode('ascii', errors='ignore')
            
            return model_info, offset + total_size
            
        except Exception as e:
            self.log(f"Error parsing model at offset {offset}: {str(e)}")
            return None, offset + 64  # Skip ahead to try next model
    
    def _find_next_signature(self, data, start_offset):
        """Find next valid COL signature in data"""
        signatures = [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']
        
        for i in range(start_offset, len(data) - 4):
            for sig in signatures:
                if data[i:i+4] == sig:
                    self.log(f"Found next signature {sig} at offset {i}")
                    return i
        
        return -1  # No signature found
    
    def _is_multi_model_archive(self, data):
        """Check if this is a multi-model COL archive"""
        if len(data) < 32:
            return False
        
        # Look for multiple signatures
        signature_count = 0
        offset = 0
        
        while offset < len(data) - 8:
            signature = data[offset:offset+4]
            if signature in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                signature_count += 1
                if signature_count > 1:
                    self.log("Detected multi-model COL archive")
                    return True
                
                # Skip past this model
                try:
                    file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
                    offset += file_size + 8
                except:
                    break
            else:
                offset += 1
        
        return False
    
    def _parse_multi_model_archive(self, data):
        """Parse multi-model COL archive"""
        self.log("Parsing as multi-model archive")
        models = []
        offset = 0
        model_index = 0
        
        while offset < len(data) - 8:
            signature = data[offset:offset+4]
            
            if signature in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                model_info, new_offset = self.parse_single_model(data, offset, model_index)
                
                if model_info:
                    models.append(model_info)
                    model_index += 1
                
                if new_offset <= offset:
                    break
                offset = new_offset
            else:
                offset += 1
        
        return models
    
    def _parse_col1_info(self, data, model_index):
        """Parse COL version 1 model info"""
        try:
            if len(data) < 40:
                return None
            
            offset = 0
            
            # Name (22 bytes)
            name_bytes = data[offset:offset+22]
            name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Model ID (4 bytes)
            model_id = struct.unpack('<I', data[offset:offset+4])[0] if len(data) >= offset + 4 else 0
            offset += 4
            
            if not name:
                name = f"COL1_Model_{model_id or model_index}"
            
            return {
                'name': name,
                'model_id': model_id,
                'type': 'COL1',
                'sphere_count': 0,  # COL1 doesn't have detailed counts
                'box_count': 0,
                'vertex_count': 0,
                'face_count': 0,
                'total_elements': 1,
                'estimated_size': len(data)
            }
            
        except Exception as e:
            self.log(f"Error parsing COL1 info: {str(e)}")
            return None
    
    def _parse_col23_info(self, data, model_index, signature):
        """Parse COL version 2/3 model info"""
        try:
            if len(data) < 60:
                return None
            
            offset = 0
            
            # Skip bounding sphere (16 bytes)
            offset += 16
            
            # Skip bounding box (24 bytes)  
            offset += 24
            
            # Read counts
            if offset + 16 <= len(data):
                num_spheres, num_boxes, num_vertices, num_faces = struct.unpack('<IIII', data[offset:offset+16])
                offset += 16
            else:
                num_spheres = num_boxes = num_vertices = num_faces = 0
            
            # Try to find name in the data
            name = f"COL_{signature.decode('ascii', errors='ignore')}_Model_{model_index}"
            
            total_elements = num_spheres + num_boxes + num_faces
            
            return {
                'name': name,
                'model_id': model_index,
                'type': signature.decode('ascii', errors='ignore'),
                'sphere_count': num_spheres,
                'box_count': num_boxes,
                'vertex_count': num_vertices,
                'face_count': num_faces,
                'total_elements': total_elements,
                'estimated_size': len(data)
            }
            
        except Exception as e:
            self.log(f"Error parsing COL2/3 info: {str(e)}")
            return None
    
    def _calculate_model_end_offset(self, data, start_offset, declared_size):
        """Calculate where this model ends"""
        try:
            return start_offset + declared_size + 8
        except Exception as e:
            self.log(f"Error calculating model end: {str(e)}")
            return start_offset + 800  # Safe fallback
    
    def get_model_stats_by_index(self, file_path, model_index):
        """Get statistics for a specific model by index"""
        models = self.parse_col_file_structure(file_path)
        
        if model_index < len(models):
            return models[model_index]
        else:
            self.log(f"Model index {model_index} not found (only {len(models)} models)")
            return {
                'sphere_count': 0,
                'box_count': 0,
                'vertex_count': 0,
                'face_count': 0,
                'total_elements': 0,
                'estimated_size': 64
            }
    
    def format_collision_types(self, stats):
        """Format collision types string from stats"""
        types = []
        if stats.get('sphere_count', 0) > 0:
            types.append(f"Spheres({stats['sphere_count']})")
        if stats.get('box_count', 0) > 0:
            types.append(f"Boxes({stats['box_count']})")
        if stats.get('face_count', 0) > 0:
            types.append(f"Mesh({stats['face_count']})")
        
        return ", ".join(types) if types else "None"
    
    def get_debug_log(self):
        """Get debug log messages"""
        return self.log_messages
    
    def clear_debug_log(self):
        """Clear debug log"""
        self.log_messages = []

# Convenience functions that respect global debug setting
def parse_col_file_with_debug(file_path, debug=None):
    """Parse COL file and return model statistics with optional debug output"""
    if debug is None:
        debug = is_col_debug_enabled()
    
    parser = COLParser(debug=debug)
    models = parser.parse_col_file_structure(file_path)
    
    # Only show debug log if global debug is enabled
    if is_col_debug_enabled() and debug:
        print("\n=== COL Parser Debug Log ===")
        for msg in parser.get_debug_log():
            print(msg)
        print("=== End Debug Log ===\n")
    
    return models

def get_model_collision_stats(file_path, model_index, debug=None):
    """Get collision statistics for a specific model"""
    if debug is None:
        debug = is_col_debug_enabled()
    
    parser = COLParser(debug=debug)
    return parser.get_model_stats_by_index(file_path, model_index)

def format_model_collision_types(stats):
    """Format collision types string"""
    parser = COLParser(debug=False)  # Never debug for formatting
    return parser.format_collision_types(stats)


# Export main classes and functions
__all__ = [
    'COLParser',
    'parse_col_file_with_debug',
    'get_model_collision_stats', 
    'format_model_collision_types'
]
