#this belongs in components/ col_core_classes.py - Version: 2
# X-Seti - July17 2025 - Img Factory 1.5 - COL Core Classes with IMG Debug System

"""
COL Core Classes - Using IMG Debug Framework
Handles COL file structure and operations using the proven IMG debug system
Converted from broken COL debug system to working IMG debug system
"""

import os
import struct
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass

# Import IMG debug system (proven to work)
from components.img_debug_functions import img_debugger, IMGDebugger
from components.unified_debug_functions import debug_trace

## Methods list -
# diagnose_col_file
# get_col_info
# load_col_file_safely
# parse_col_data
# validate_col_structure

##class COLVersion: -
# COL_1
# COL_2
# COL_3
# COL_4

##class COLModel: -
# __init__
# calculate_bounding_box
# get_stats
# update_flags

##class COLFile: -
# __init__
# load
# load_from_file
# load_from_data
# _parse_col_data
# _parse_col_model
# _parse_col1_model
# _parse_col23_model
# get_summary

class COLVersion(Enum):
    """COL file version enumeration"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4


@dataclass
class Vector3:
    """3D vector for collision data"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __iter__(self):
        return iter((self.x, self.y, self.z))


@dataclass
class BoundingBox:
    """Bounding box for collision models"""
    center: Vector3 = None
    min_point: Vector3 = None
    max_point: Vector3 = None
    radius: float = 0.0
    
    def __post_init__(self):
        if self.center is None:
            self.center = Vector3()
        if self.min_point is None:
            self.min_point = Vector3()
        if self.max_point is None:
            self.max_point = Vector3()
    
    def calculate_from_vertices(self, vertices: List[Vector3]):
        """Calculate bounding box from vertex list"""
        if not vertices:
            return
        
        # Find min/max coordinates
        min_x = min(v.x for v in vertices)
        max_x = max(v.x for v in vertices)
        min_y = min(v.y for v in vertices)
        max_y = max(v.y for v in vertices)
        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)
        
        self.min_point = Vector3(min_x, min_y, min_z)
        self.max_point = Vector3(max_x, max_y, max_z)
        self.center = Vector3(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
        # Calculate radius
        dx = max_x - min_x
        dy = max_y - min_y
        dz = max_z - min_z
        self.radius = (dx * dx + dy * dy + dz * dz) ** 0.5 / 2


@dataclass
class COLSphere:
    """COL collision sphere"""
    center: Vector3 = None
    radius: float = 0.0
    material: int = 0
    flags: int = 0
    
    def __post_init__(self):
        if self.center is None:
            self.center = Vector3()


@dataclass
class COLBox:
    """COL collision box"""
    min_point: Vector3 = None
    max_point: Vector3 = None
    material: int = 0
    flags: int = 0
    
    def __post_init__(self):
        if self.min_point is None:
            self.min_point = Vector3()
        if self.max_point is None:
            self.max_point = Vector3()


@dataclass
class COLVertex:
    """COL mesh vertex"""
    position: Vector3 = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = Vector3()


@dataclass
class COLFace:
    """COL mesh face"""
    vertex_indices: Tuple[int, int, int] = (0, 0, 0)
    material: int = 0
    light: int = 0
    flags: int = 0


@dataclass
class COLFaceGroup:
    """COL face group"""
    surface_flags: int = 0
    material: int = 0
    first_face: int = 0
    face_count: int = 0


@dataclass
class COLMaterial:
    """COL material properties"""
    friction: float = 0.7
    elasticity: float = 0.1
    material_id: int = 0


class COLModel:
    """COL collision model using IMG debug system"""
    
    def __init__(self):
        self.name: str = ""
        self.model_id: int = 0
        self.version: COLVersion = COLVersion.COL_1
        
        # Collision data
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        
        # Shadow mesh data (COL3+)
        self.shadow_vertices: List[COLVertex] = []
        self.shadow_faces: List[COLFace] = []
        
        # Bounding data
        self.bounding_box: BoundingBox = BoundingBox()
        
        # Status flags
        self.has_sphere_data: bool = False
        self.has_box_data: bool = False
        self.has_mesh_data: bool = False
        
        img_debugger.debug(f"COL model initialized: {self.name}")
    
    @debug_trace
    def get_stats(self) -> Dict[str, int]: #vers 1
        """Get collision model statistics"""
        stats = {
            'spheres': len(self.spheres),
            'boxes': len(self.boxes),
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'face_groups': len(self.face_groups),
            'shadow_vertices': len(self.shadow_vertices),
            'shadow_faces': len(self.shadow_faces)
        }
        
        img_debugger.debug(f"COL stats for {self.name}: {stats}")
        return stats
    
    def calculate_bounding_box(self): #vers 1
        """Calculate bounding box from collision data"""
        all_vertices = []
        
        # Add sphere centers
        for sphere in self.spheres:
            all_vertices.append(sphere.center)
        
        # Add box corners
        for box in self.boxes:
            all_vertices.extend([box.min_point, box.max_point])
        
        # Add mesh vertices
        all_vertices.extend([vertex.position for vertex in self.vertices])
        
        # Calculate bounding box
        if all_vertices:
            self.bounding_box.calculate_from_vertices(all_vertices)
            img_debugger.debug(f"Bounding box calculated for {self.name}")
    
    def update_flags(self): #vers 1
        """Update status flags based on available data"""
        self.has_sphere_data = len(self.spheres) > 0
        self.has_box_data = len(self.boxes) > 0
        self.has_mesh_data = len(self.vertices) > 0 and len(self.faces) > 0
        
        img_debugger.debug(f"Flags updated for {self.name}: spheres={self.has_sphere_data}, boxes={self.has_box_data}, mesh={self.has_mesh_data}")


class COLFile:
    """COL file handler using IMG debug system"""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = None
        self.file_size = 0
        
        img_debugger.debug(f"COL file initialized: {file_path}")
    
    @debug_trace
    def load(self) -> bool: #vers 1
        """Load COL file - Main entry point"""
        if not self.file_path:
            self.load_error = "No file path specified"
            img_debugger.error(f"COL load failed: {self.load_error}")
            return False
        
        return self.load_from_file(self.file_path)
    
    @debug_trace
    def load_from_file(self, file_path: str) -> bool: #vers 1
        """Load COL file from disk using IMG debug system"""
        try:
            self.file_path = file_path
            self.load_error = None
            
            img_debugger.debug(f"Loading COL file: {file_path}")
            
            if not os.path.exists(file_path):
                self.load_error = "File not found"
                img_debugger.error(f"COL file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self.file_size = len(data)
            img_debugger.info(f"COL file read: {os.path.basename(file_path)} ({self.file_size} bytes)")
            
            return self.load_from_data(data)
            
        except Exception as e:
            self.load_error = str(e)
            img_debugger.error(f"Error loading COL file: {e}")
            return False
    
    @debug_trace
    def load_from_data(self, data: bytes) -> bool: #vers 1
        """Load COL data from bytes using IMG debug system"""
        try:
            self.models.clear()
            self.is_loaded = False
            
            if len(data) < 8:
                self.load_error = "File too small"
                img_debugger.error("COL data too small (<8 bytes)")
                return False
            
            success = self._parse_col_data(data)
            if success:
                self.is_loaded = True
                img_debugger.success(f"COL data loaded successfully: {len(self.models)} models")
            
            return success
            
        except Exception as e:
            self.load_error = str(e)
            img_debugger.error(f"Error parsing COL data: {e}")
            return False
    
    def _parse_col_data(self, data: bytes) -> bool: #vers 1
        """Parse COL data using IMG debug system"""
        self.models = []
        offset = 0
        
        img_debugger.debug(f"Parsing COL data: {len(data)} bytes")
        
        while offset < len(data):
            model, consumed = self._parse_col_model(data, offset)
            if model is None:
                break
            
            self.models.append(model)
            offset += consumed
            
            # Safety check to prevent infinite loops
            if consumed == 0:
                img_debugger.warning("COL parsing stopped: no bytes consumed")
                break
        
        success = len(self.models) > 0
        img_debugger.debug(f"COL parsing complete: {len(self.models)} models loaded")
        
        return success
    
    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]: #vers 1
        """Parse single COL model using IMG debug system"""
        try:
            if offset + 8 > len(data):
                img_debugger.debug("COL model parsing stopped: insufficient data for header")
                return None, 0
            
            # Read FourCC signature
            fourcc = data[offset:offset+4]
            
            if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                img_debugger.debug(f"COL model parsing stopped: invalid signature {fourcc}")
                return None, 0
            
            # Read file size
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = file_size + 8
            
            if offset + total_size > len(data):
                img_debugger.warning(f"COL model size mismatch: expected {total_size}, available {len(data) - offset}")
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
            
            img_debugger.debug(f"COL model parsed: {model.name} (version {model.version.value})")
            
            return model, total_size
            
        except Exception as e:
            img_debugger.error(f"Error parsing COL model at offset {offset}: {e}")
            return None, 0
    
    def _parse_col1_model(self, model: COLModel, data: bytes): #vers 1
        """Parse COL version 1 model using IMG debug system"""
        try:
            if len(data) < 22:
                img_debugger.warning("COL1 data too small for header")
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
            
            img_debugger.debug(f"COL1 model parsed: {model.name}")
            
        except Exception as e:
            img_debugger.error(f"Error parsing COL1 model: {e}")
    
    def _parse_col23_model(self, model: COLModel, data: bytes): #vers 1
        """Parse COL version 2/3 model using IMG debug system"""
        try:
            if len(data) < 40:
                img_debugger.warning("COL2/3 data too small for header")
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
            model.bounding_box.min_point = Vector3(min_x, min_y, min_z)
            model.bounding_box.max_point = Vector3(max_x, max_y, max_z)
            offset += 24
            
            # For now, initialize empty collision data
            # TODO: Add detailed COL2/3 parsing
            model.spheres = []
            model.boxes = []
            model.vertices = []
            model.faces = []
            
            # Set default name
            model.name = f"COL{model.version.value}_Model"
            
            model.update_flags()
            
            img_debugger.debug(f"COL{model.version.value} model parsed: {model.name}")
            
        except Exception as e:
            img_debugger.error(f"Error parsing COL{model.version.value} model: {e}")
    
    def get_summary(self) -> str: #vers 1
        """Get file summary using IMG debug system"""
        lines = []
        lines.append(f"COL File: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}")
        lines.append(f"File Size: {self.file_size} bytes")
        lines.append(f"Models: {len(self.models)}")
        
        if self.is_loaded and self.models:
            lines.append(f"Loaded: Yes")
            
            # Calculate total statistics
            total_stats = {'spheres': 0, 'boxes': 0, 'vertices': 0, 'faces': 0}
            for model in self.models:
                stats = model.get_stats()
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)
            
            lines.append(f"Total Collision: {total_stats['spheres']} spheres, {total_stats['boxes']} boxes")
            lines.append(f"Total Mesh: {total_stats['vertices']} vertices, {total_stats['faces']} faces")
        else:
            lines.append(f"Loaded: No")
            if self.load_error:
                lines.append(f"Error: {self.load_error}")
        
        summary = "\n".join(lines)
        img_debugger.debug(f"COL summary generated: {len(lines)} lines")
        return summary


# Utility functions using IMG debug system
@debug_trace
def diagnose_col_file(file_path: str) -> dict: #vers 1
    """Diagnose COL file structure using IMG debug system"""
    img_debugger.debug(f"Diagnosing COL file: {file_path}")
    
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
            img_debugger.warning(f"COL file too small: {len(data)} bytes")
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
        
        img_debugger.info(f"COL diagnosis complete: {info['detected_version']}")
        return info
        
    except Exception as e:
        error_info = {
            'exists': os.path.exists(file_path),
            'readable': False,
            'error': str(e)
        }
        img_debugger.error(f"COL diagnosis failed: {e}")
        return error_info


# Legacy compatibility - remove broken debug system
def get_col_info(col_file: COLFile) -> str: #vers 1
    """Get COL file information using IMG debug system"""
    return col_file.get_summary()


# Export main classes and functions
__all__ = [
    'COLFile', 'COLModel', 'COLVersion', 'COLMaterial',
    'COLSphere', 'COLBox', 'COLVertex', 'COLFace', 'COLFaceGroup',
    'Vector3', 'BoundingBox', 'diagnose_col_file', 'get_col_info'
]
