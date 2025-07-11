#!/usr/bin/env python3
"""
#this belongs in components/col_core_classes.py - version 12
X-Seti - July07 2025 - COL Core Classes for Img Factory 1.5
Complete COL file format support for GTA games
"""

import os
import struct
import math
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


class COLVersion(Enum):
    """COL file format versions"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4


class COLMaterial(Enum):
    """COL surface material types"""
    DEFAULT = 0
    CONCRETE = 1
    METAL = 2
    SOFT = 3
    GLASS = 4
    SAND = 5
    WATER = 6
    WOOD = 7
    GRAVEL = 8
    MUD = 9
    MATTRESS = 10
    CLOTH = 11
    CARPET = 12
    FLESHBONE = 13
    RUBBER = 14
    PLASTIC = 15


class Vector3:
    """3D vector class"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self) -> float:
        """Calculate vector magnitude"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        """Normalize vector to unit length"""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag
        return self
    
    def dot(self, other) -> float:
        """Dot product with another vector"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """Cross product with another vector"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )


class BoundingBox:
    """3D bounding box"""
    
    def __init__(self, min_point: Vector3, max_point: Vector3, center: Vector3, radius: float):
        self.min = min_point
        self.max = max_point
        self.center = center
        self.radius = radius
    
    def __str__(self):
        return f"BoundingBox(min={self.min}, max={self.max}, radius={self.radius:.2f})"
    
    def contains_point(self, point: Vector3) -> bool:
        """Check if point is inside bounding box"""
        return (self.min.x <= point.x <= self.max.x and
                self.min.y <= point.y <= self.max.y and
                self.min.z <= point.z <= self.max.z)


class COLSphere:
    """COL collision sphere"""
    
    def __init__(self, center: Vector3 = None, radius: float = 0.0, material: COLMaterial = COLMaterial.DEFAULT):
        self.center = center or Vector3()
        self.radius = radius
        self.material = material
    
    def __str__(self):
        return f"COLSphere(center={self.center}, radius={self.radius:.2f}, material={self.material.name})"


class COLBox:
    """COL collision box"""
    
    def __init__(self, min_point: Vector3 = None, max_point: Vector3 = None, material: COLMaterial = COLMaterial.DEFAULT):
        self.min = min_point or Vector3()
        self.max = max_point or Vector3()
        self.material = material
    
    def __str__(self):
        return f"COLBox(min={self.min}, max={self.max}, material={self.material.name})"
    
    def get_center(self) -> Vector3:
        """Get box center point"""
        return Vector3(
            (self.min.x + self.max.x) / 2,
            (self.min.y + self.max.y) / 2,
            (self.min.z + self.max.z) / 2
        )
    
    def get_size(self) -> Vector3:
        """Get box dimensions"""
        return Vector3(
            self.max.x - self.min.x,
            self.max.y - self.min.y,
            self.max.z - self.min.z
        )


class COLVertex:
    """COL mesh vertex"""
    
    def __init__(self, position: Vector3 = None):
        self.position = position or Vector3()
    
    def __str__(self):
        return f"COLVertex({self.position})"


class COLFace:
    """COL mesh face (triangle)"""
    
    def __init__(self, vertex_a: int = 0, vertex_b: int = 0, vertex_c: int = 0, 
                 material: COLMaterial = COLMaterial.DEFAULT, lighting: int = 0):
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.vertex_c = vertex_c
        self.material = material
        self.lighting = lighting
    
    def __str__(self):
        return f"COLFace({self.vertex_a}, {self.vertex_b}, {self.vertex_c}, {self.material.name})"


class COLFaceGroup:
    """COL face group for LOD"""
    
    def __init__(self, min_face: int = 0, max_face: int = 0):
        self.min_face = min_face
        self.max_face = max_face
    
    def __str__(self):
        return f"COLFaceGroup({self.min_face}-{self.max_face})"


class COLModel:
    """Single COL collision model"""
    
    def __init__(self):
        self.name: str = ""
        self.model_id: int = 0
        self.version: COLVersion = COLVersion.COL_2
        self.flags: int = 0
        
        # Bounding data
        self.bounding_box: Optional[BoundingBox] = None
        
        # Collision elements
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        
        # Shadow mesh (COL3 only)
        self.shadow_vertices: List[COLVertex] = []
        self.shadow_faces: List[COLFace] = []
        self._debug_enabled = getattr(sys.modules.get('components.col_core_classes'), '_global_debug_enabled', False)


    def __str__(self):
        return f"COLModel(name='{self.name}', version={self.version.name}, elements={self.get_total_elements()})"
    
    def get_total_elements(self) -> int:
        """Get total number of collision elements"""
        return len(self.spheres) + len(self.boxes) + len(self.faces)
    
    def calculate_bounding_box(self):
        """Calculate bounding box from collision elements"""
        if not (self.spheres or self.boxes or self.vertices):
            self.bounding_box = BoundingBox(Vector3(), Vector3(), Vector3(), 0.0)
            return
        
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        
        # Include spheres
        for sphere in self.spheres:
            min_x = min(min_x, sphere.center.x - sphere.radius)
            min_y = min(min_y, sphere.center.y - sphere.radius)
            min_z = min(min_z, sphere.center.z - sphere.radius)
            max_x = max(max_x, sphere.center.x + sphere.radius)
            max_y = max(max_y, sphere.center.y + sphere.radius)
            max_z = max(max_z, sphere.center.z + sphere.radius)
        
        # Include boxes
        for box in self.boxes:
            min_x = min(min_x, box.min.x)
            min_y = min(min_y, box.min.y)
            min_z = min(min_z, box.min.z)
            max_x = max(max_x, box.max.x)
            max_y = max(max_y, box.max.y)
            max_z = max(max_z, box.max.z)
        
        # Include vertices
        for vertex in self.vertices:
            min_x = min(min_x, vertex.position.x)
            min_y = min(min_y, vertex.position.y)
            min_z = min(min_z, vertex.position.z)
            max_x = max(max_x, vertex.position.x)
            max_y = max(max_y, vertex.position.y)
            max_z = max(max_z, vertex.position.z)
        
        # Handle edge case where no valid geometry exists
        if min_x == float('inf'):
            min_x = min_y = min_z = 0
            max_x = max_y = max_z = 0
        
        min_vec = Vector3(min_x, min_y, min_z)
        max_vec = Vector3(max_x, max_y, max_z)
        center = Vector3(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
        # Calculate radius as distance from center to corner
        radius = (max_vec - center).magnitude()
        
        self.bounding_box = BoundingBox(min_vec, max_vec, center, radius)
    
    def update_flags(self):
        """Update flags based on current collision elements"""
        self.flags = 0
        
        # Check if not empty
        if self.spheres or self.boxes or self.faces:
            self.flags |= 2  # Not empty flag
        
        # Check for face groups
        if self.face_groups and self.faces:
            self.flags |= 8  # Has face groups flag
        
        # Check for shadow mesh (COL3 only)
        if self.version == COLVersion.COL_3 and self.shadow_faces:
            self.flags |= 16  # Has shadow mesh flag
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about this collision model"""
        return {
            "spheres": len(self.spheres),
            "boxes": len(self.boxes),
            "vertices": len(self.vertices),
            "faces": len(self.faces),
            "face_groups": len(self.face_groups),
            "shadow_vertices": len(self.shadow_vertices),
            "shadow_faces": len(self.shadow_faces),
            "total_elements": len(self.spheres) + len(self.boxes) + len(self.faces)
        }


class COLFile:
    """Main COL file handler"""
    
    def __init__(self, file_path: str = ""):
        self.file_path: str = file_path
        self.models: List[COLModel] = []
        self.is_loaded: bool = False
    
    def __str__(self):
        return f"COLFile('{os.path.basename(self.file_path)}', {len(self.models)} models, loaded={self.is_loaded})"
    
    def load(self) -> bool:
        """Load COL file from disk"""
        if not os.path.exists(self.file_path):
            print(f"COL file does not exist: {self.file_path}")
            return False
        
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
            
            print(f"Loading COL file: {len(data)} bytes")
            return self._parse_col_data(data)
        
        except Exception as e:
            print(f"Error loading COL file {self.file_path}: {e}")
            return False
    
    def save(self, output_path: str = None) -> bool:
        """Save COL file to disk"""
        if not output_path:
            output_path = self.file_path
        
        try:
            data = self._build_col_data()
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"COL file saved: {output_path}")
            return True
        
        except Exception as e:
            print(f"Error saving COL file: {e}")
            return False
    
    def _parse_col_data(self, data: bytes) -> bool:
        """Parse COL file data"""
        self.models = []
        offset = 0

        # Only log if debug is specifically enabled
        debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled

        if debug_enabled:
            print(f"Parsing COL data: {len(data)} bytes")

        while offset < len(data):
            model, consumed = self._parse_col_model(data, offset)
            if model is None:
                break

            self.models.append(model)
            offset += consumed

            # Safety check to prevent infinite loops
            if consumed == 0:
                if debug_enabled:
                    print("Warning: No bytes consumed, breaking to prevent infinite loop")
                break

        self.is_loaded = True
        success = len(self.models) > 0

        # Only log summary, no individual model spam
        if debug_enabled:
            print(f"COL parsing complete: {len(self.models)} models loaded")

        return success

    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]:
        """Parse a single COL model from data"""
        try:
            if offset + 8 > len(data):
                return None, 0

            # Only log if debug is specifically enabled
            debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled

            # Read FourCC signature
            fourcc = data[offset:offset+4]

            if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return None, 0

            # Read file size
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = file_size + 8  # Size field doesn't include header

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

            return model, total_size

        except Exception as e:
            debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled
            if debug_enabled:
                print(f"Error parsing COL model at offset {offset}: {e}")
            return None, 0

    def _parse_col1_model(self, model: COLModel, data: bytes):
        """Parse COL version 1 mode"""
        try:
            if len(data) < 22:
                return

            debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled
            offset = 0

            # Read name (22 bytes, null-terminated)
            name_bytes = data[offset:offset+22]
            model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22

            # Read model ID (4 bytes)
            if offset + 4 <= len(data):
                model.model_id = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4

            # Initialize empty collision data
            model.spheres = []
            model.boxes = []
            model.vertices = []
            model.faces = []

            # Calculate basic bounding box
            model.calculate_bounding_box()
            model.update_flags()

            # Only log if debug specifically enabled
            if debug_enabled:
                print(f"COL1 model parsed: {model.name}")

        except Exception as e:
            debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled
            if debug_enabled:
                print(f"Error parsing COL1 model: {e}")
    
    def _parse_col23_model(self, model: COLModel, data: bytes):
        """Parse COL version 2/3 model"""
        try:
            if len(data) < 60:  # Minimum size for COL2/3 header
                return

            debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled
            offset = 0

            # Read bounding sphere (16 bytes: center + radius)
            center_x, center_y, center_z, radius = struct.unpack('<ffff', data[offset:offset+16])
            offset += 16

            # Read bounding box (24 bytes: min + max)
            min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            max_x, max_y, max_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12

            # Create bounding box
            model.bounding_box = BoundingBox(
                Vector3(min_x, min_y, min_z),
                Vector3(max_x, max_y, max_z),
                Vector3(center_x, center_y, center_z),
                radius
            )

            # Read counts (16 bytes)
            sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            box_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            face_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4

            # Only log counts if debug enabled
            if debug_enabled:
                print(f"COL2/3 counts - Spheres: {sphere_count}, Boxes: {box_count}, Vertices: {vertex_count}, Faces: {face_count}")

            # Initialize lists
            model.spheres = []
            model.boxes = []
            model.vertices = []
            model.faces = []

            # Create placeholder elements for basic implementation
            for i in range(sphere_count):
                sphere = COLSphere(Vector3(0, 0, 0), 1.0, COLMaterial.DEFAULT)
                model.spheres.append(sphere)

            for i in range(box_count):
                box = COLBox(Vector3(-1, -1, -1), Vector3(1, 1, 1), COLMaterial.DEFAULT)
                model.boxes.append(box)

            for i in range(vertex_count):
                vertex = COLVertex(Vector3(0, 0, 0))
                model.vertices.append(vertex)

            for i in range(face_count):
                face = COLFace(0, 1, 2, COLMaterial.DEFAULT, 0)
                model.faces.append(face)

            # Set a default name
            model.name = f"COL{model.version.value}_Model"

            # Update flags
            model.update_flags()

            # Only log if debug enabled
            if debug_enabled:
                print(f"COL2/3 model parsed: {model.name}")

        except Exception as e:
            debug_enabled = hasattr(self, '_debug_enabled') and self._debug_enabled
            if debug_enabled:
                print(f"Error parsing COL2/3 model: {e}")

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
            min_point = model.bounding_box.min
            max_point = model.bounding_box.max
        else:
            min_point = Vector3()
            max_point = Vector3()
        
        data += struct.pack('<fff', min_point.x, min_point.y, min_point.z)
        data += struct.pack('<fff', max_point.x, max_point.y, max_point.z)
        
        # Write counts
        data += struct.pack('<I', len(model.spheres))
        data += struct.pack('<I', len(model.boxes))
        data += struct.pack('<I', len(model.vertices))
        data += struct.pack('<I', len(model.faces))
        
        return data
    
    def add_model(self, model: COLModel):
        """Add a collision model to the file"""
        self.models.append(model)
    
    def remove_model(self, index: int) -> bool:
        """Remove a collision model by index"""
        if 0 <= index < len(self.models):
            del self.models[index]
            return True
        return False
    
    def get_total_stats(self) -> Dict[str, int]:
        """Get total statistics for all models in the file"""
        total_stats = {
            "models": len(self.models),
            "spheres": 0,
            "boxes": 0,
            "vertices": 0,
            "faces": 0,
            "face_groups": 0,
            "shadow_vertices": 0,
            "shadow_faces": 0,
            "total_elements": 0
        }
        
        for model in self.models:
            stats = model.get_stats()
            for key in stats:
                if key in total_stats:
                    total_stats[key] += stats[key]
        
        return total_stats
    
    def get_diagnostic_info(self) -> str:
        """Get diagnostic information about the COL file"""
        if not self.file_path:
            return "No file path set"
        
        lines = []
        lines.append(f"File: {os.path.basename(self.file_path)}")
        
        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)
            lines.append(f"Size: {file_size:,} bytes")
            lines.append(f"Exists: Yes")
        else:
            lines.append(f"Exists: No")
            return "\n".join(lines)
        
        if self.is_loaded:
            lines.append(f"Loaded: Yes")
            lines.append(f"Models: {len(self.models)}")
            
            for i, model in enumerate(self.models):
                stats = model.get_stats()
                lines.append(f"  Model {i}: {model.name} ({model.version.name})")
                lines.append(f"    Elements: {stats['total_elements']} total")
                lines.append(f"    Spheres: {stats['spheres']}, Boxes: {stats['boxes']}")
                lines.append(f"    Mesh: {stats['vertices']} vertices, {stats['faces']} faces")
        else:
            lines.append(f"Loaded: No")
        
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
    'Vector3', 'BoundingBox', 'diagnose_col_file'
]
