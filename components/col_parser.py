#this belongs in components/ col_parser.py - Version: 1
# X-Seti - July08 2025 - Complete COL Parser with Debug Mode for IMG Factory 1.5

"""
COL Parser - Complete collision file parsing with debugging
Handles all COL format versions (COL1/COL2/COL3/COL4) with detailed logging
"""

import struct
import os
from typing import Dict, List, Tuple, Optional

class COLParser:
    """Complete COL file parser with debugging support"""
    
    def __init__(self, debug=True):
        self.debug = debug
        self.log_messages = []
    
    def log(self, message):
        """Log debug message"""
        if self.debug:
            print(f"🔍 COLParser: {message}")
        self.log_messages.append(message)
    
    def parse_col_file_structure(self, file_path):
        """Parse complete COL file and return structure info for all models"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.log(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")
            
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
            
            self.log(f"\nParsing complete: {len(models)} models found")
            return models
            
        except Exception as e:
            self.log(f"Error parsing COL file: {str(e)}")
            return []
    
    def parse_single_model(self, data, offset, model_index):
        """Parse a single COL model and return info + new offset"""
        try:
            start_offset = offset
            
            # Read signature
            if offset + 4 > len(data):
                return None, offset
            
            signature = data[offset:offset+4]
            self.log(f"Signature: {signature}")
            
            # Validate signature
            if signature not in [b'COLL', b'COL2', b'COL3', b'COL4']:
                self.log(f"Invalid signature: {signature}")
                return None, offset
            
            offset += 4
            
            # Read file size
            if offset + 4 > len(data):
                return None, offset
            
            file_size = struct.unpack('<I', data[offset:offset+4])[0]
            self.log(f"Declared size: {file_size}")
            offset += 4
            
            # Read model name (22 bytes)
            if offset + 22 > len(data):
                return None, offset
            
            name_bytes = data[offset:offset+22]
            model_name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            self.log(f"Model name: '{model_name}'")
            offset += 22
            
            # Read model ID (2 bytes)
            if offset + 2 > len(data):
                return None, offset
            
            model_id = struct.unpack('<H', data[offset:offset+2])[0]
            self.log(f"Model ID: {model_id}")
            offset += 2
            
            # Determine version
            version_str = signature.decode('ascii', errors='ignore')
            is_col1 = (version_str == 'COLL')
            self.log(f"Version: {version_str} (COL1: {is_col1})")
            
            # Skip bounding data
            bounds_size = 40 if is_col1 else 28
            if offset + bounds_size > len(data):
                return None, offset
            
            self.log(f"Skipping {bounds_size} bytes of bounding data")
            offset += bounds_size
            
            # Skip unknown data for COL1
            if is_col1:
                if offset + 4 <= len(data):
                    unknown_count = struct.unpack('<I', data[offset:offset+4])[0]
                    self.log(f"COL1 unknown data: {unknown_count} entries")
                    offset += 4 + (unknown_count * 8)
            
            # Parse collision data
            collision_stats = self.parse_collision_data(data, offset, is_col1)
            
            # Calculate model end offset
            model_end = self.calculate_model_end_offset(data, offset, collision_stats, is_col1)
            
            # Build model info
            model_info = {
                'index': model_index,
                'name': model_name or f"Model_{model_index + 1}",
                'signature': version_str,
                'model_id': model_id,
                'is_col1': is_col1,
                'sphere_count': collision_stats['sphere_count'],
                'box_count': collision_stats['box_count'],
                'vertex_count': collision_stats['vertex_count'],
                'face_count': collision_stats['face_count'],
                'total_elements': collision_stats['sphere_count'] + collision_stats['box_count'] + collision_stats['face_count'],
                'estimated_size': model_end - start_offset,
                'start_offset': start_offset,
                'end_offset': model_end
            }
            
            self.log(f"Model stats: {collision_stats}")
            self.log(f"Model size: {model_info['estimated_size']} bytes")
            
            return model_info, model_end
            
        except Exception as e:
            self.log(f"Error parsing single model: {str(e)}")
            return None, offset
    
    def parse_collision_data(self, data, offset, is_col1):
        """Parse collision data counts from model"""
        stats = {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
        
        try:
            # Read sphere count
            if offset + 4 <= len(data):
                stats['sphere_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                self.log(f"Spheres: {stats['sphere_count']}")
                offset += 4
                offset += stats['sphere_count'] * 20  # Skip sphere data
            
            # Read box count
            if offset + 4 <= len(data):
                stats['box_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                self.log(f"Boxes: {stats['box_count']}")
                offset += 4
                offset += stats['box_count'] * 28  # Skip box data
            
            # Read vertex count
            if offset + 4 <= len(data):
                stats['vertex_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                self.log(f"Vertices: {stats['vertex_count']}")
                offset += 4
                vertex_size = 12 if is_col1 else 6
                offset += stats['vertex_count'] * vertex_size
            
            # Read face count
            if offset + 4 <= len(data):
                stats['face_count'] = struct.unpack('<I', data[offset:offset+4])[0]
                self.log(f"Faces: {stats['face_count']}")
            
        except Exception as e:
            self.log(f"Error reading collision data: {str(e)}")
        
        return stats
    
    def calculate_model_end_offset(self, data, offset, stats, is_col1):
        """Calculate where this model ends in the file"""
        try:
            # Start from collision data offset
            end_offset = offset
            
            # Skip remaining collision data
            # Spheres already skipped in parse_collision_data
            # Boxes already skipped in parse_collision_data
            # Vertices already skipped in parse_collision_data
            
            # Skip faces
            face_size = 16 if is_col1 else 8
            end_offset += 4 + (stats['face_count'] * face_size)
            
            # For COL2/3, skip additional data
            if not is_col1:
                # Skip face groups (if present)
                if end_offset + 4 <= len(data):
                    try:
                        face_group_count = struct.unpack('<I', data[end_offset:end_offset+4])[0]
                        if face_group_count < 1000:  # Sanity check
                            self.log(f"Face groups: {face_group_count}")
                            end_offset += 4 + (face_group_count * 28)
                    except:
                        pass
                
                # Skip shadow mesh (COL3)
                if end_offset + 8 <= len(data):
                    try:
                        shadow_vertex_count = struct.unpack('<I', data[end_offset:end_offset+4])[0]
                        if 0 < shadow_vertex_count < 10000:  # Sanity check
                            self.log(f"Shadow vertices: {shadow_vertex_count}")
                            end_offset += 4 + (shadow_vertex_count * 6)
                            
                            if end_offset + 4 <= len(data):
                                shadow_face_count = struct.unpack('<I', data[end_offset:end_offset+4])[0]
                                if 0 < shadow_face_count < 10000:  # Sanity check
                                    self.log(f"Shadow faces: {shadow_face_count}")
                                    end_offset += 4 + (shadow_face_count * 8)
                    except:
                        pass
            
            # Align to 4-byte boundary (common in binary formats)
            while end_offset % 4 != 0 and end_offset < len(data):
                end_offset += 1
            
            return end_offset
            
        except Exception as e:
            self.log(f"Error calculating model end: {str(e)}")
            return offset + 100  # Fallback
    
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

# Convenience functions
def parse_col_file_with_debug(file_path, debug=True):
    """Parse COL file and return model statistics with debug output"""
    parser = COLParser(debug=debug)
    models = parser.parse_col_file_structure(file_path)
    
    if debug:
        print("\n=== COL Parser Debug Log ===")
        for msg in parser.get_debug_log():
            print(msg)
        print("=== End Debug Log ===\n")
    
    return models

def get_model_collision_stats(file_path, model_index, debug=False):
    """Get collision statistics for a specific model"""
    parser = COLParser(debug=debug)
    return parser.get_model_stats_by_index(file_path, model_index)

def format_model_collision_types(stats):
    """Format collision types string"""
    parser = COLParser(debug=False)
    return parser.format_collision_types(stats)
