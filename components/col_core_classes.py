#this belongs in components/ col_core_classes.py - Version: 13
# X-Seti - July11 2025 - Img Factory 1.5
# COL file core classes - CLEAN VERSION with debug control

import struct
import os
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

# Global debug flag - controlled by settings (same as IMG loading)
_global_debug_enabled = False

def set_col_debug_enabled(enabled: bool):
    """Set global COL debug flag"""
    global _global_debug_enabled
    _global_debug_enabled = enabled

def is_col_debug_enabled() -> bool:
    """Check if COL debug is enabled"""
    global _global_debug_enabled
    return _global_debug_enabled

class COLVersion(Enum):
    """COL file format versions"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4

class Vector3:
    """3D vector class"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

class BoundingBox:
    """Bounding box class"""
    def __init__(self):
        self.min = Vector3()
        self.max = Vector3()
        self.center = Vector3()
        self.radius = 0.0
    
    def calculate_from_vertices(self, vertices: List[Vector3]):
        """Calculate bounding box from vertices"""
        if not vertices:
            return
        
        # Find min/max coordinates
        self.min.x = min(v.x for v in vertices)
        self.min.y = min(v.y for v in vertices)
        self.min.z = min(v.z for v in vertices)
        
        self.max.x = max(v.x for v in vertices)
        self.max.y = max(v.y for v in vertices)
        self.max.z = max(v.z for v in vertices)
        
        # Calculate center and radius
        self.center.x = (self.min.x + self.max.x) / 2
        self.center.y = (self.min.y + self.max.y) / 2
        self.center.z = (self.min.z + self.max.z) / 2
        
        # Calculate radius as distance from center to corner
        dx = self.max.x - self.center.x
        dy = self.max.y - self.center.y
        dz = self.max.z - self.center.z
        self.radius = (dx*dx + dy*dy + dz*dz)**0.5

class COLMaterial:
    """COL material definition"""
    def __init__(self):
        self.material_id = 0
        self.flags = 0
        self.brightness = 0
        self.light = 0

class COLSphere:
    """COL sphere collision primitive"""
    def __init__(self):
        self.center = Vector3()
        self.radius = 0.0
        self.material = COLMaterial()

class COLBox:
    """COL box collision primitive"""
    def __init__(self):
        self.min = Vector3()
        self.max = Vector3()
        self.material = COLMaterial()

class COLVertex:
    """COL mesh vertex"""
    def __init__(self):
        self.position = Vector3()

class COLFace:
    """COL mesh face"""
    def __init__(self):
        self.vertex_a = 0
        self.vertex_b = 0
        self.vertex_c = 0
        self.material = COLMaterial()

class COLFaceGroup:
    """COL face group"""
    def __init__(self):
        self.bounding_box = BoundingBox()
        self.start_face = 0
        self.end_face = 0

class COLModel:
    """COL collision model"""
    def __init__(self):
        self.name = ""
        self.model_id = 0
        self.version = COLVersion.COL_1
        self.flags = 0
        
        # Bounding data
        self.bounding_box = BoundingBox()
        
        # Collision primitives
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        
        # Mesh data
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        
        # Status flags
        self.is_loaded = False
        self.has_sphere_data = False
        self.has_box_data = False
        self.has_mesh_data = False
    
    def get_stats(self) -> Dict[str, int]:
        """Get collision statistics"""
        return {
            'spheres': len(self.spheres),
            'boxes': len(self.boxes),
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'face_groups': len(self.face_groups),
            'total_elements': len(self.spheres) + len(self.boxes) + len(self.faces)
        }
    
    def calculate_bounding_box(self):
        """Calculate bounding box from collision data"""
        all_vertices = []
        
        # Add sphere centers and extents
        for sphere in self.spheres:
            all_vertices.extend([
                Vector3(sphere.center.x - sphere.radius, sphere.center.y - sphere.radius, sphere.center.z - sphere.radius),
                Vector3(sphere.center.x + sphere.radius, sphere.center.y + sphere.radius, sphere.center.z + sphere.radius)
            ])
        
        # Add box extents
        for box in self.boxes:
            all_vertices.extend([box.min, box.max])
        
        # Add mesh vertices
        all_vertices.extend([vertex.position for vertex in self.vertices])
        
        # Calculate bounding box
        if all_vertices:
            self.bounding_box.calculate_from_vertices(all_vertices)
    
    def update_flags(self):
        """Update status flags based on available data"""
        self.has_sphere_data = len(self.spheres) > 0
        self.has_box_data = len(self.boxes) > 0
        self.has_mesh_data = len(self.vertices) > 0 and len(self.faces) > 0

class COLFile:
    """COL file handler with debug control"""
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = None
        self.file_size = 0
    

    def load(self) -> bool:
        """Load COL file - MISSING METHOD FIX"""
        if not self.file_path:
            self.load_error = "No file path specified"
            return False

        return self.load_from_file(self.file_path)

    def load_from_file(self, file_path: str) -> bool:
        """Load COL file from disk with debug control"""
        try:
            self.file_path = file_path
            self.load_error = None

            if not os.path.exists(file_path):
                self.load_error = "File not found"
                return False

            with open(file_path, 'rb') as f:
                data = f.read()

            self.file_size = len(data)

            if is_col_debug_enabled():
                print(f"Loading COL file: {os.path.basename(file_path)} ({self.file_size} bytes)")

            return self.load_from_data(data)

        except Exception as e:
            self.load_error = str(e)
            if is_col_debug_enabled():
                print(f"Error loading COL file: {e}")
            return False

    def load_from_data(self, data: bytes) -> bool:
        """Load COL data from bytes with debug control"""
        try:
            self.models.clear()
            self.is_loaded = False
            
            if len(data) < 8:
                self.load_error = "File too small"
                return False
            
            return self._parse_col_data(data)
            
        except Exception as e:
            self.load_error = str(e)
            if is_col_debug_enabled():
                print(f"Error parsing COL data: {e}")
            return False
    
    def _parse_col_data(self, data: bytes) -> bool:
        """Parse COL data - CLEAN with debug control"""
        self.models = []
        offset = 0
        
        # Only log if debug is enabled
        if is_col_debug_enabled():
            print(f"Parsing COL data: {len(data)} bytes")
        
        while offset < len(data):
            model, consumed = self._parse_col_model(data, offset)
            if model is None:
                break
            
            self.models.append(model)
            offset += consumed
            
            # Safety check to prevent infinite loops
            if consumed == 0:
                break
        
        self.is_loaded = True
        success = len(self.models) > 0
        
        # Only log summary if debug enabled
        if is_col_debug_enabled():
            print(f"COL parsing complete: {len(self.models)} models loaded")
        
        return success
    
    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]:
        """Parse single COL model - CLEAN with debug control"""
        try:
            if offset + 8 > len(data):
                return None, 0
            
            # Read FourCC signature
            fourcc = data[offset:offset+4]
            
            if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return None, 0
            
            # Read file size
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = file_size + 8
            
            if offset + total_size > len(data):
                return None, 0
            
            # Create model
            model = COLModel()
            
            # Determine version
            if fourcc == b'COLL':
                model.version = COLVersion.COL_1
            elif fourcc == b'COL\x02':
                model.version = COLVersion.COL_2
            elif fourcc == b'COL\x03':
                model.version = COLVersion.COL_3
            elif fourcc == b'COL\x04':
                model.version = COLVersion.COL_4
            
            # Parse model data based on version
            model_data = data[offset + 8:offset + total_size]
            if model.version == COLVersion.COL_1:
                self._parse_col1_model(model, model_data)
            else:
                self._parse_col23_model(model, model_data)
            
            # Only log if debug enabled
            if is_col_debug_enabled():
                print(f"Parsed COL model: {model.name} (version {model.version.value})")
            
            return model, total_size
            
        except Exception as e:
            if is_col_debug_enabled():
                print(f"Error parsing COL model at offset {offset}: {e}")
            return None, 0
    
    def _parse_col1_model(self, model: COLModel, data: bytes):
        """Parse COL version 1 model - CLEAN with debug control"""
        try:
            if len(data) < 22:
                return
            
            offset = 0
            
            # Read name (22 bytes, null-terminated)
            name_bytes = data[offset:offset+22]
            model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Read model ID (4 bytes)
            if offset + 4 <= len(data):
                model.model_id = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
            
            # Set default name if empty
            if not model.name:
                model.name = f"Model_{model.model_id}"
            
            # Initialize empty collision data for now
            model.spheres = []
            model.boxes = []
            model.vertices = []
            model.faces = []
            
            # Calculate basic bounding box
            model.calculate_bounding_box()
            model.update_flags()
            
            if is_col_debug_enabled():
                print(f"COL1 model parsed: {model.name}")
                
        except Exception as e:
            if is_col_debug_enabled():
                print(f"Error parsing COL1 model: {e}")
    
    def _parse_col23_model(self, model: COLModel, data: bytes):
        """Parse COL version 2/3 model - CLEAN with debug control"""
        try:
            if len(data) < 40:
                if is_col_debug_enabled():
                    print("COL2/3 data too small for header")
                return
            
            offset = 0
            
            # Read bounding sphere (16 bytes)
            center_x, center_y, center_z, radius = struct.unpack('<ffff', data[offset:offset+16])
            model.bounding_box.center = Vector3(center_x, center_y, center_z)
            model.bounding_box.radius = radius
            offset += 16
            
            # Read bounding box (24 bytes)
            min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
            max_x, max_y, max_z = struct.unpack('<fff', data[offset+12:offset+24])
            model.bounding_box.min = Vector3(min_x, min_y, min_z)
            model.bounding_box.max = Vector3(max_x, max_y, max_z)
            offset += 24
            
            # For now, create basic collision data
            model.spheres = []
            model.boxes = []
            model.vertices = []
            model.faces = []
            
            # Set default name
            model.name = f"COL{model.version.value}_Model"
            
            # Update flags
            model.update_flags()
            
            if is_col_debug_enabled():
                print(f"COL2/3 model parsed: {model.name}")
                
        except Exception as e:
            if is_col_debug_enabled():
                print(f"Error parsing COL2/3 model: {e}")
    
    def save_to_file(self, file_path: str) -> bool:
        """Save COL file to disk"""
        try:
            data = self._build_col_data()
            
            with open(file_path, 'wb') as f:
                f.write(data)
            
            if is_col_debug_enabled():
                print(f"COL file saved: {os.path.basename(file_path)} ({len(data)} bytes)")
            
            return True
            
        except Exception as e:
            if is_col_debug_enabled():
                print(f"Error saving COL file: {e}")
            return False
    
    def _build_col_data(self) -> bytes:
        """Build COL file data from models"""
        data = b''
        
        for model in self.models:
            model_data = self._build_col_model(model)
            data += model_data
        
        return data
    
    def _build_col_model(self, model: COLModel) -> bytes:
        """Build data for a single COL model"""
        if model.version == COLVersion.COL_1:
            return self._build_col1_model(model)
        else:
            return self._build_col23_model(model)
    
    def _build_col1_model(self, model: COLModel) -> bytes:
        """Build COL version 1 model data"""
        # Basic COL1 structure
        data = b'COLL'
        
        # Calculate content size
        content_size = 22 + 4  # name + model_id
        data += struct.pack('<I', content_size)
        
        # Write name (22 bytes, padded with nulls)
        name_bytes = model.name.encode('ascii')[:22]
        name_bytes = name_bytes.ljust(22, b'\x00')
        data += name_bytes
        
        # Write model ID
        data += struct.pack('<I', model.model_id)
        
        return data
    
    def _build_col23_model(self, model: COLModel) -> bytes:
        """Build COL version 2/3 model data"""
        # Determine signature
        if model.version == COLVersion.COL_2:
            fourcc = b'COL\x02'
        elif model.version == COLVersion.COL_3:
            fourcc = b'COL\x03'
        else:
            fourcc = b'COL\x04'
        
        data = fourcc
        
        # Calculate content size (simplified)
        content_size = 60  # Basic header
        data += struct.pack('<I', content_size)
        
        # Write bounding sphere
        if model.bounding_box:
            center = model.bounding_box.center
            radius = model.bounding_box.radius
        else:
            center = Vector3()
            radius = 0.0
        
        data += struct.pack('<ffff', center.x, center.y, center.z, radius)
        
        # Write bounding box
        if model.bounding_box:
            min_pt = model.bounding_box.min
            max_pt = model.bounding_box.max
        else:
            min_pt = max_pt = Vector3()
        
        data += struct.pack('<ffffff', min_pt.x, min_pt.y, min_pt.z, max_pt.x, max_pt.y, max_pt.z)
        
        # Pad to required size
        remaining = content_size - (len(data) - 8)
        if remaining > 0:
            data += b'\x00' * remaining
        
        return data
    
    def get_info(self) -> str:
        """Get file information as formatted string"""
        lines = [f"COL File: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}"]
        lines.append(f"Models: {len(self.models)}")
        
        if self.is_loaded:
            total_stats = {'spheres': 0, 'boxes': 0, 'vertices': 0, 'faces': 0, 'total_elements': 0}
            for model in self.models:
                stats = model.get_stats()
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)
            
            lines.append(f"Loaded: Yes")
            lines.append(f"    Elements: {total_stats['total_elements']} total")
            lines.append(f"    Spheres: {total_stats['spheres']}, Boxes: {total_stats['boxes']}")
            lines.append(f"    Mesh: {total_stats['vertices']} vertices, {total_stats['faces']} faces")
        else:
            lines.append(f"Loaded: No")
            if self.load_error:
                lines.append(f"Error: {self.load_error}")
        
        return "\n".join(lines)


def diagnose_col_file(file_path: str) -> dict:
    """Diagnose COL file structure for debugging"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        info = {
            'file_size': len(data),
            'exists': True,
            'readable': True,
        }
        
        if len(data) < 8:
            info['error'] = 'File too small (< 8 bytes)'
            return info
        
        # Check first 8 bytes
        header = data[:8]
        info['header_hex'] = header.hex()
        info['header_ascii'] = header[:4]
        
        # Try to identify COL signature
        signature = data[:4]
        if signature == b'COLL':
            info['detected_version'] = 'COL1'
            info['signature_valid'] = True
        elif signature == b'COL\x02':
            info['detected_version'] = 'COL2'
            info['signature_valid'] = True
        elif signature == b'COL\x03':
            info['detected_version'] = 'COL3'
            info['signature_valid'] = True
        elif signature == b'COL\x04':
            info['detected_version'] = 'COL4'
            info['signature_valid'] = True
        else:
            info['detected_version'] = 'Unknown'
            info['signature_valid'] = False
            info['error'] = f'Invalid signature: {signature}'
        
        # If valid signature, try to read size
        if info['signature_valid']:
            try:
                size = struct.unpack('<I', data[4:8])[0]
                info['declared_size'] = size
                info['total_expected_size'] = size + 8
                info['size_matches'] = (size + 8 == len(data))
            except:
                info['error'] = 'Failed to read size field'
        
        return info
        
    except Exception as e:
        return {
            'exists': os.path.exists(file_path),
            'readable': False,
            'error': str(e)
        }


# Export main classes for import
__all__ = [
    'COLFile', 'COLModel', 'COLVersion', 'COLMaterial',
    'COLSphere', 'COLBox', 'COLVertex', 'COLFace', 'COLFaceGroup',
    'Vector3', 'BoundingBox', 'diagnose_col_file',
    'set_col_debug_enabled', 'is_col_debug_enabled'
]
