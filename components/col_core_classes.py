#!/usr/bin/env python3
"""
#this belongs in components/col_core_classes.py - version 10
X-Seti - June27 2025 - COL Core Classes for Img Factory 1.5
Handles collision file parsing and manipulation for GTA III, VC, SA
Based on Steve's COL Editor II functionality
"""

import struct
import os
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import math

class COLVersion(Enum):
    """COL file version enumeration"""
    COL_1 = 1    # GTA III, VC
    COL_2 = 2    # GTA SA PS2
    COL_3 = 3    # GTA SA PC/Xbox
    COL_4 = 4    # GTA SA (rare)
    UNKNOWN = 0

class COLMaterial(Enum):
    """Collision material types"""
    DEFAULT = 0
    TARMAC = 1
    TARMACCRACKED = 2
    RUMBLESTRIP = 3
    CONCRETE = 4
    CONCRETE_DUSTY = 5
    METAL = 6
    WOOD = 7
    GRAVEL = 8
    WATER = 9
    GLASS = 10
    SAND = 11
    PAVEMENT = 12
    CARDBOARD = 13
    CARPET = 14
    TILE = 15
    HEDGE = 16
    CONTAINER = 17

@dataclass
class Vector3:
    """3D Vector class"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector3(self.x / mag, self.y / mag, self.z / mag)
        return Vector3(0, 0, 0)

@dataclass
class BoundingBox:
    """Bounding box structure"""
    min: Vector3
    max: Vector3
    center: Vector3
    radius: float

@dataclass
class COLSurface:
    """Surface properties for collision elements"""
    material: int = 0
    flag: int = 0
    brightness: int = 0
    light: int = 0

@dataclass
class COLSphere:
    """Collision sphere"""
    center: Vector3
    radius: float
    surface: COLSurface

@dataclass
class COLBox:
    """Collision box (axis-aligned)"""
    min: Vector3
    max: Vector3
    surface: COLSurface

@dataclass
class COLVertex:
    """Collision mesh vertex"""
    position: Vector3

@dataclass
class COLFace:
    """Collision mesh face (triangle)"""
    a: int  # vertex index
    b: int  # vertex index
    c: int  # vertex index
    material: int = 0
    light: int = 0
    surface: Optional[COLSurface] = None

@dataclass
class COLFaceGroup:
    """Face group for optimization (COL2/3 only)"""
    min: Vector3
    max: Vector3
    start_face: int
    end_face: int

class COLModel:
    """Individual collision model within a COL file"""
    
    def __init__(self):
        self.name: str = ""
        self.model_id: int = 0
        self.version: COLVersion = COLVersion.COL_1
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
        
        # Flags
        self.flags: int = 0
        self.has_spheres: bool = False
        self.has_boxes: bool = False
        self.has_mesh: bool = False
        self.has_face_groups: bool = False
        self.has_shadow_mesh: bool = False
    
    def calculate_bounding_box(self):
        """Calculate bounding box from all collision elements"""
        if not self.vertices and not self.spheres and not self.boxes:
            self.bounding_box = BoundingBox(
                Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(0, 0, 0), 0
            )
            return
        
        # Initialize with extreme values
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        
        # Check mesh vertices
        for vertex in self.vertices:
            min_x = min(min_x, vertex.position.x)
            min_y = min(min_y, vertex.position.y)
            min_z = min(min_z, vertex.position.z)
            max_x = max(max_x, vertex.position.x)
            max_y = max(max_y, vertex.position.y)
            max_z = max(max_z, vertex.position.z)
        
        # Check spheres
        for sphere in self.spheres:
            min_x = min(min_x, sphere.center.x - sphere.radius)
            min_y = min(min_y, sphere.center.y - sphere.radius)
            min_z = min(min_z, sphere.center.z - sphere.radius)
            max_x = max(max_x, sphere.center.x + sphere.radius)
            max_y = max(max_y, sphere.center.y + sphere.radius)
            max_z = max(max_z, sphere.center.z + sphere.radius)
        
        # Check boxes
        for box in self.boxes:
            min_x = min(min_x, box.min.x)
            min_y = min(min_y, box.min.y)
            min_z = min(min_z, box.min.z)
            max_x = max(max_x, box.max.x)
            max_y = max(max_y, box.max.y)
            max_z = max(max_z, box.max.z)
        
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
    
    def load(self) -> bool:
        """Load COL file from disk"""
        if not os.path.exists(self.file_path):
            return False
        
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
            
            return self._parse_col_data(data)
        
        except Exception as e:
            print(f"Error loading COL file: {e}")
            return False
    
    def save(self, output_path: str = None) -> bool:
        """Save COL file to disk"""
        if not output_path:
            output_path = self.file_path
        
        try:
            data = self._build_col_data()
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
        
        except Exception as e:
            print(f"Error saving COL file: {e}")
            return False
    
    def _parse_col_data(self, data: bytes) -> bool:
        """Parse COL file data"""
        self.models = []
        offset = 0
        
        while offset < len(data):
            model, consumed = self._parse_col_model(data, offset)
            if model is None:
                break
            
            self.models.append(model)
            offset += consumed
        
        self.is_loaded = True
        return len(self.models) > 0
    
    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]:
        """Parse a single COL model from data"""
        if offset + 8 > len(data):
            return None, 0
        
        # Read FourCC
        fourcc = data[offset:offset+4]
        if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
            return None, 0
        
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
        
        # Read file size
        file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
        total_size = file_size + 8
        
        if offset + total_size > len(data):
            return None, 0
        
        # Parse based on version
        if model.version == COLVersion.COL_1:
            self._parse_col1_model(model, data, offset + 8, file_size)
        else:
            self._parse_col23_model(model, data, offset + 8, file_size)
        
        return model, total_size
    
    def _parse_col1_model(self, model: COLModel, data: bytes, start_offset: int, size: int):
        """Parse COL version 1 model"""
        offset = start_offset
        
        # Read name (22 bytes)
        name_bytes = data[offset:offset+22]
        model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
        offset += 22
        
        # Read model ID
        model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        
        # Read bounding box (40 bytes)
        bb_data = struct.unpack('<12f', data[offset:offset+48])
        model.bounding_box = BoundingBox(
            Vector3(bb_data[0], bb_data[1], bb_data[2]),  # min
            Vector3(bb_data[3], bb_data[4], bb_data[5]),  # max
            Vector3(bb_data[6], bb_data[7], bb_data[8]),  # center
            bb_data[9]  # radius
        )
        offset += 48
        
        # Read collision elements
        # Spheres
        sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        for _ in range(sphere_count):
            radius = struct.unpack('<f', data[offset:offset+4])[0]
            center = Vector3(*struct.unpack('<3f', data[offset+4:offset+16]))
            surface = COLSurface(*struct.unpack('<4B', data[offset+16:offset+20]))
            model.spheres.append(COLSphere(center, radius, surface))
            offset += 20
        
        # Skip unknown section
        unknown_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4 + (unknown_count * 4)  # Skip unknown data
        
        # Boxes
        box_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        for _ in range(box_count):
            min_vec = Vector3(*struct.unpack('<3f', data[offset:offset+12]))
            max_vec = Vector3(*struct.unpack('<3f', data[offset+12:offset+24]))
            surface = COLSurface(*struct.unpack('<4B', data[offset+24:offset+28]))
            model.boxes.append(COLBox(min_vec, max_vec, surface))
            offset += 28
        
        # Vertices
        vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        for _ in range(vertex_count):
            pos = Vector3(*struct.unpack('<3f', data[offset:offset+12]))
            model.vertices.append(COLVertex(pos))
            offset += 12
        
        # Faces
        face_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        for _ in range(face_count):
            a, b, c = struct.unpack('<3I', data[offset:offset+12])
            surface = COLSurface(*struct.unpack('<4B', data[offset+12:offset+16]))
            face = COLFace(a, b, c, surface.material, surface.light, surface)
            model.faces.append(face)
            offset += 16
        
        model.update_flags()
    
    def _parse_col23_model(self, model: COLModel, data: bytes, start_offset: int, size: int):
        """Parse COL version 2/3 model"""
        offset = start_offset
        
        # Read name (22 bytes)
        name_bytes = data[offset:offset+22]
        model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
        offset += 22
        
        # Read model ID
        model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        
        # Read bounding box (40 bytes) - different order than COL1
        bb_data = struct.unpack('<10f', data[offset:offset+40])
        model.bounding_box = BoundingBox(
            Vector3(bb_data[0], bb_data[1], bb_data[2]),  # min
            Vector3(bb_data[3], bb_data[4], bb_data[5]),  # max
            Vector3(bb_data[6], bb_data[7], bb_data[8]),  # center
            bb_data[9]  # radius
        )
        offset += 40
        
        # Read counts and offsets
        sphere_count = struct.unpack('<H', data[offset:offset+2])[0]
        box_count = struct.unpack('<H', data[offset+2:offset+4])[0]
        face_count = struct.unpack('<H', data[offset+4:offset+6])[0]
        line_count = struct.unpack('<B', data[offset+6:offset+7])[0]
        # Skip padding byte
        offset += 8
        
        # Read flags
        model.flags = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Read offsets
        sphere_offset = struct.unpack('<I', data[offset:offset+4])[0] if sphere_count > 0 else 0
        box_offset = struct.unpack('<I', data[offset+4:offset+8])[0] if box_count > 0 else 0
        line_offset = struct.unpack('<I', data[offset+8:offset+12])[0] if line_count > 0 else 0
        vertex_offset = struct.unpack('<I', data[offset+12:offset+16])[0] if face_count > 0 else 0
        face_offset = struct.unpack('<I', data[offset+16:offset+20])[0] if face_count > 0 else 0
        # Skip triangle planes offset
        offset += 24
        
        # COL3 specific offsets
        shadow_face_count = 0
        shadow_vertex_offset = 0
        shadow_face_offset = 0
        
        if model.version == COLVersion.COL_3:
            shadow_face_count = struct.unpack('<I', data[offset:offset+4])[0]
            shadow_vertex_offset = struct.unpack('<I', data[offset+4:offset+8])[0]
            shadow_face_offset = struct.unpack('<I', data[offset+8:offset+12])[0]
            offset += 12
        
        # Parse collision elements using offsets
        base_offset = start_offset + 4  # Relative to after FourCC
        
        # Spheres
        if sphere_count > 0:
            sphere_data_offset = base_offset + sphere_offset
            for i in range(sphere_count):
                center = Vector3(*struct.unpack('<3f', data[sphere_data_offset:sphere_data_offset+12]))
                radius = struct.unpack('<f', data[sphere_data_offset+12:sphere_data_offset+16])[0]
                surface = COLSurface(*struct.unpack('<4B', data[sphere_data_offset+16:sphere_data_offset+20]))
                model.spheres.append(COLSphere(center, radius, surface))
                sphere_data_offset += 20
        
        # Boxes
        if box_count > 0:
            box_data_offset = base_offset + box_offset
            for i in range(box_count):
                min_vec = Vector3(*struct.unpack('<3f', data[box_data_offset:box_data_offset+12]))
                max_vec = Vector3(*struct.unpack('<3f', data[box_data_offset+12:box_data_offset+24]))
                surface = COLSurface(*struct.unpack('<4B', data[box_data_offset+24:box_data_offset+28]))
                model.boxes.append(COLBox(min_vec, max_vec, surface))
                box_data_offset += 28
        
        # Vertices (compressed format)
        if face_count > 0 and vertex_offset > 0:
            vertex_data_offset = base_offset + vertex_offset
            # We need to determine vertex count by scanning faces
            max_vertex_index = 0
            
            # First pass: find max vertex index from faces
            if face_count > 0:
                face_data_offset = base_offset + face_offset
                for i in range(face_count):
                    a, b, c = struct.unpack('<3H', data[face_data_offset:face_data_offset+6])
                    max_vertex_index = max(max_vertex_index, a, b, c)
                    face_data_offset += 8  # 6 bytes for indices + 2 bytes for material/light
            
            # Read vertices
            for i in range(max_vertex_index + 1):
                # COL2/3 uses compressed int16 coordinates
                x, y, z = struct.unpack('<3h', data[vertex_data_offset:vertex_data_offset+6])
                pos = Vector3(x / 128.0, y / 128.0, z / 128.0)
                model.vertices.append(COLVertex(pos))
                vertex_data_offset += 6
        
        # Faces
        if face_count > 0:
            face_data_offset = base_offset + face_offset
            for i in range(face_count):
                a, b, c = struct.unpack('<3H', data[face_data_offset:face_data_offset+6])
                material, light = struct.unpack('<2B', data[face_data_offset+6:face_data_offset+8])
                face = COLFace(a, b, c, material, light)
                model.faces.append(face)
                face_data_offset += 8
        
        # Shadow mesh (COL3 only)
        if model.version == COLVersion.COL_3 and shadow_face_count > 0:
            # Parse shadow vertices and faces (similar to regular mesh)
            pass  # TODO: Implement shadow mesh parsing
    
    def _build_col_data(self) -> bytes:
        """Build COL file data from models"""
        data = b''
        
        for model in self.models:
            model_data = self._build_col_model(model)
            data += model_data
        
        return data
    
    def _build_col_model(self, model: COLModel) -> bytes:
        """Build data for a single COL model"""
        # This is a simplified version - full implementation would be more complex
        if model.version == COLVersion.COL_1:
            return self._build_col1_model(model)
        else:
            return self._build_col23_model(model)
    
    def _build_col1_model(self, model: COLModel) -> bytes:
        """Build COL version 1 model data"""
        # Simplified implementation
        data = b'COLL'
        # TODO: Implement full COL1 building
        return data
    
    def _build_col23_model(self, model: COLModel) -> bytes:
        """Build COL version 2/3 model data"""
        # Simplified implementation
        fourcc = b'COL\x02' if model.version == COLVersion.COL_2 else b'COL\x03'
        data = fourcc
        # TODO: Implement full COL2/3 building
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
