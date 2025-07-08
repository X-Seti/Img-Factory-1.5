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
    
    def _is_multi_model_archive(self, data):
        """Check if this is a multi-model COL archive"""
        try:
            # Look for multiple COL signatures
            signature_count = 0
            offset = 0
            
            while offset < len(data) - 4:
                if data[offset:offset+4] in [b'COLL', b'COL2', b'COL3', b'COL4']:
                    signature_count += 1
                    if signature_count > 1:
                        self.log(f"Detected multi-model archive ({signature_count} signatures found)")
                        return True
                    # Skip to avoid counting the same signature multiple times
                    offset += 100
                else:
                    offset += 1
            
            return False
            
        except Exception:
            return False
    
    def _parse_multi_model_archive(self, data):
        """Parse multi-model COL archive with different structure"""
        try:
            self.log("Parsing as multi-model archive...")
            models = []
            
            # Find all COL signatures in the file
            signatures = []
            offset = 0
            
            while offset < len(data) - 4:
                sig = data[offset:offset+4]
                if sig in [b'COLL', b'COL2', b'COL3', b'COL4']:
                    signatures.append(offset)
                    self.log(f"Found {sig} at offset {offset}")
                offset += 1
            
            self.log(f"Found {len(signatures)} model signatures")
            
            # Parse each model starting from its signature
            for i, sig_offset in enumerate(signatures):
                try:
                    self.log(f"\n--- Archive Model {i} at offset {sig_offset} ---")
                    model_info, _ = self.parse_single_model(data, sig_offset, i)
                    
                    if model_info:
                        models.append(model_info)
                        self.log(f"Archive model {i} parsed successfully")
                    else:
                        self.log(f"Failed to parse archive model {i}")
                        
                except Exception as e:
                    self.log(f"Error parsing archive model {i}: {str(e)}")
                    continue
            
            self.log(f"Archive parsing complete: {len(models)} models found")
            return models
            
        except Exception as e:
            self.log(f"Error parsing multi-model archive: {str(e)}")
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
        """Parse collision data counts from model - FIXED VERSION"""
        stats = {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
        
        try:
            original_offset = offset
            self.log(f"Starting collision data parsing at offset {offset}")
            
            # Read sphere count - VALIDATE IT'S REASONABLE
            if offset + 4 <= len(data):
                sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
                
                # SANITY CHECK: Sphere count should be reasonable
                if sphere_count > 50000:  # More than 50k spheres is unrealistic
                    self.log(f"⚠️ Unrealistic sphere count: {sphere_count}, data may be corrupted")
                    # Try to find the actual collision data by scanning ahead
                    return self._scan_for_collision_data(data, original_offset, is_col1)
                
                stats['sphere_count'] = sphere_count
                self.log(f"Spheres: {stats['sphere_count']}")
                offset += 4
                
                # Skip sphere data (20 bytes per sphere)
                sphere_data_size = stats['sphere_count'] * 20
                if offset + sphere_data_size > len(data):
                    self.log(f"⚠️ Not enough data for spheres ({sphere_data_size} bytes needed)")
                    return self._scan_for_collision_data(data, original_offset, is_col1)
                offset += sphere_data_size
            
            # Read box count
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                
                # SANITY CHECK: Box count should be reasonable  
                if box_count > 10000:  # More than 10k boxes is unrealistic
                    self.log(f"⚠️ Unrealistic box count: {box_count}")
                    return stats  # Return what we have so far
                
                stats['box_count'] = box_count
                self.log(f"Boxes: {stats['box_count']}")
                offset += 4
                
                # Skip box data (28 bytes per box)
                box_data_size = stats['box_count'] * 28
                if offset + box_data_size > len(data):
                    self.log(f"⚠️ Not enough data for boxes ({box_data_size} bytes needed)")
                    return stats
                offset += box_data_size
            
            # Read vertex count
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                
                # SANITY CHECK: Vertex count should be reasonable
                if vertex_count > 100000:  # More than 100k vertices is unrealistic for collision
                    self.log(f"⚠️ Unrealistic vertex count: {vertex_count}")
                    return stats  # Return what we have so far
                
                stats['vertex_count'] = vertex_count
                self.log(f"Vertices: {stats['vertex_count']}")
                offset += 4
                
                # Skip vertex data
                vertex_size = 12 if is_col1 else 6
                vertex_data_size = stats['vertex_count'] * vertex_size
                if offset + vertex_data_size > len(data):
                    self.log(f"⚠️ Not enough data for vertices ({vertex_data_size} bytes needed)")
                    return stats
                offset += vertex_data_size
            
            # Read face count
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                
                # SANITY CHECK: Face count should be reasonable
                if face_count > 200000:  # More than 200k faces is unrealistic
                    self.log(f"⚠️ Unrealistic face count: {face_count}")
                    return stats  # Return what we have so far
                
                stats['face_count'] = face_count
                self.log(f"Faces: {stats['face_count']}")
            
        except Exception as e:
            self.log(f"Error reading collision data: {str(e)}")
        
        return stats
    
    def _scan_for_collision_data(self, data, start_offset, is_col1):
        """Scan for reasonable collision data when initial parsing fails"""
        try:
            self.log(f"Scanning for reasonable collision data from offset {start_offset}")
            
            # Try different offsets near the start position
            for test_offset in range(start_offset, min(start_offset + 200, len(data) - 16), 4):
                if test_offset + 16 > len(data):
                    break
                
                # Try reading sphere count at this offset
                try:
                    sphere_count = struct.unpack('<I', data[test_offset:test_offset+4])[0]
                    box_count = struct.unpack('<I', data[test_offset+4:test_offset+8])[0]
                    vertex_count = struct.unpack('<I', data[test_offset+8:test_offset+12])[0]
                    face_count = struct.unpack('<I', data[test_offset+12:test_offset+16])[0]
                    
                    # Check if these look reasonable
                    if (sphere_count < 50000 and box_count < 10000 and 
                        vertex_count < 100000 and face_count < 200000):
                        
                        self.log(f"✅ Found reasonable data at offset {test_offset}")
                        self.log(f"Spheres: {sphere_count}, Boxes: {box_count}, Vertices: {vertex_count}, Faces: {face_count}")
                        
                        return {
                            'sphere_count': sphere_count,
                            'box_count': box_count,
                            'vertex_count': vertex_count,
                            'face_count': face_count
                        }
                
                except:
                    continue
            
            self.log("⚠️ Could not find reasonable collision data")
            return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
            
        except Exception as e:
            self.log(f"Error scanning for collision data: {str(e)}")
            return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
    
    def calculate_model_end_offset(self, data, offset, stats, is_col1):
        """Calculate where this model ends in the file - FIXED VERSION"""
        try:
            original_offset = offset
            
            # If collision data looks corrupted, use declared model size
            total_elements = stats['sphere_count'] + stats['box_count'] + stats['vertex_count'] + stats['face_count']
            
            if total_elements > 500000:  # Unrealistic total
                self.log(f"⚠️ Corrupted collision data detected, using fallback size calculation")
                return original_offset + 800  # Reasonable fallback size
            
            # Calculate actual data size
            end_offset = offset
            
            # Add sphere data size (if reasonable)
            if stats['sphere_count'] < 50000:
                sphere_size = 4 + (stats['sphere_count'] * 20)
                end_offset += sphere_size
                self.log(f"Added spheres: {sphere_size} bytes")
            else:
                self.log("⚠️ Skipping unrealistic sphere data")
                end_offset += 4  # Just the count
            
            # Add box data size (if reasonable)
            if stats['box_count'] < 10000:
                box_size = 4 + (stats['box_count'] * 28)
                end_offset += box_size
                self.log(f"Added boxes: {box_size} bytes")
            else:
                self.log("⚠️ Skipping unrealistic box data")
                end_offset += 4  # Just the count
            
            # Add vertex data size (if reasonable)
            if stats['vertex_count'] < 100000:
                vertex_size = 12 if is_col1 else 6
                vertex_data_size = 4 + (stats['vertex_count'] * vertex_size)
                end_offset += vertex_data_size
                self.log(f"Added vertices: {vertex_data_size} bytes")
            else:
                self.log("⚠️ Skipping unrealistic vertex data")
                end_offset += 4  # Just the count
            
            # Add face data size (if reasonable)
            if stats['face_count'] < 200000:
                face_size = 16 if is_col1 else 8
                face_data_size = 4 + (stats['face_count'] * face_size)
                end_offset += face_data_size
                self.log(f"Added faces: {face_data_size} bytes")
            else:
                self.log("⚠️ Skipping unrealistic face data")
                end_offset += 4  # Just the count
            
            # Ensure we don't go beyond file bounds
            if end_offset > len(data):
                self.log(f"⚠️ Calculated end ({end_offset}) exceeds file size ({len(data)})")
                end_offset = min(original_offset + 1000, len(data))
            
            # Ensure minimum progress
            if end_offset <= original_offset:
                end_offset = original_offset + 100
            
            calculated_size = end_offset - original_offset
            self.log(f"Final model size: {calculated_size} bytes, end offset: {end_offset}")
            
            return end_offset
            
        except Exception as e:
            self.log(f"Error calculating model end: {str(e)}")
            return offset + 800  # Safe fallback
    
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
