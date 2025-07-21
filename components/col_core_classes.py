#this belongs in components/col_core_classes.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Core Classes
# Core COL file classes and structures with IMG debug system integration

"""
COL Core Classes - Complete COL file handling
Provides COL file parsing, model management, and collision data structures
"""

import os
import struct
import time
from typing import List, Optional, Tuple, Any, Dict
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

# Import IMG debug system
from components.img_debug_functions import img_debugger

##Methods list -
# calculate_bounding_box
# get_raw_data
# load
# load_from_data
# load_from_file
# update_flags

##Classes -
# COLFile
# COLModel
# COLVersion
# Vector3
# BoundingBox
# COLSphere
# COLBox  
# COLVertex
# COLFace

# Global debug state for COL operations
_col_debug_enabled = False

def set_col_debug_enabled(enabled: bool):
    """Enable/disable COL debug output using IMG debug system"""
    global _col_debug_enabled
    _col_debug_enabled = enabled
    
    if enabled:
        img_debugger.debug("🛡️ COL debug system ENABLED")
    else:
        img_debugger.debug("🛡️ COL debug system DISABLED for performance")

def is_col_debug_enabled() -> bool:
    """Check if COL debug is enabled"""
    global _col_debug_enabled
    return _col_debug_enabled and img_debugger.debug_enabled

class COLVersion(Enum):
    """COL file version constants"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4

@dataclass
class Vector3:
    """3D vector for positions and directions"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

@dataclass
class BoundingBox:
    """Bounding box for collision models"""
    min: Vector3
    max: Vector3
    center: Vector3
    radius: float = 0.0
    
    def __init__(self):
        self.min = Vector3()
        self.max = Vector3()
        self.center = Vector3()
        self.radius = 0.0
    
    def calculate_from_vertices(self, vertices: List[Vector3]): #vers 1
        """Calculate bounding box from vertex list"""
        if not vertices:
            return
        
        self.min.x = min(v.x for v in vertices)
        self.min.y = min(v.y for v in vertices)
        self.min.z = min(v.z for v in vertices)
        
        self.max.x = max(v.x for v in vertices)
        self.max.y = max(v.y for v in vertices)
        self.max.z = max(v.z for v in vertices)
        
        # Calculate center
        self.center.x = (self.min.x + self.max.x) / 2
        self.center.y = (self.min.y + self.max.y) / 2
        self.center.z = (self.min.z + self.max.z) / 2
        
        # Calculate radius
        dx = self.max.x - self.min.x
        dy = self.max.y - self.min.y
        dz = self.max.z - self.min.z
        self.radius = (dx * dx + dy * dy + dz * dz) ** 0.5 / 2

@dataclass
class COLSphere:
    """Collision sphere data"""
    center: Vector3
    radius: float
    surface: int = 0
    piece: int = 0

@dataclass
class COLBox:
    """Collision box data"""
    min: Vector3
    max: Vector3
    surface: int = 0
    piece: int = 0

@dataclass
class COLVertex:
    """Collision mesh vertex"""
    position: Vector3

@dataclass
class COLFace:
    """Collision mesh face"""
    a: int  # Vertex indices
    b: int
    c: int
    surface: int = 0
    piece: int = 0

class COLModel:
    """COL collision model with debug control"""
    def __init__(self):
        self.name = ""
        self.model_id = 0
        self.version = COLVersion.COL_1
        self.bounding_box = BoundingBox()
        
        # Collision data
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        
        # Status flags
        self.has_sphere_data = False
        self.has_box_data = False
        self.has_mesh_data = False
    
    def calculate_bounding_box(self): #vers 1
        """Calculate bounding box from all collision data"""
        all_vertices = []
        
        # Add sphere positions
        all_vertices.extend([sphere.center for sphere in self.spheres])
        
        # Add box corners
        for box in self.boxes:
            all_vertices.extend([box.min, box.max])
        
        # Add mesh vertices
        all_vertices.extend([vertex.position for vertex in self.vertices])
        
        # Calculate bounding box
        if all_vertices:
            self.bounding_box.calculate_from_vertices(all_vertices)
    
    def update_flags(self): #vers 1
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
    
    def load(self) -> bool: #vers 1
        """Load COL file - MISSING METHOD FIX"""
        if not self.file_path:
            self.load_error = "No file path specified"
            return False

        return self.load_from_file(self.file_path)

    def load_from_file(self, file_path: str) -> bool: #vers 1
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
                img_debugger.debug(f"Loading COL file: {os.path.basename(file_path)} ({self.file_size} bytes)")

            return self.load_from_data(data)

        except Exception as e:
            self.load_error = str(e)
            if is_col_debug_enabled():
                img_debugger.error(f"Error loading COL file: {e}")
            return False

    def load_from_data(self, data: bytes) -> bool: #vers 1
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
                img_debugger.error(f"Error parsing COL data: {e}")
            return False
    
    def _parse_col_data(self, data: bytes) -> bool: #vers 1
        """Parse COL data - CLEAN with debug control"""
        self.models = []
        offset = 0
        
        # Only log if debug is enabled
        if is_col_debug_enabled():
            img_debugger.debug(f"Parsing COL data: {len(data)} bytes")
        
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
            img_debugger.success(f"COL parsing complete: {len(self.models)} models loaded")
        
        return success
    
    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]: #vers 1
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
                img_debugger.debug(f"Parsed COL model: {model.name} (version {model.version.value})")
            
            return model, total_size
            
        except Exception as e:
            if is_col_debug_enabled():
                img_debugger.error(f"Error parsing COL model at offset {offset}: {e}")
            return None, 0
    
    def _parse_col1_model(self, model: COLModel, data: bytes): #vers 1
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
                img_debugger.debug(f"COL1 model parsed: {model.name}")
                
        except Exception as e:
            if is_col_debug_enabled():
                img_debugger.error(f"Error parsing COL1 model: {e}")
    
    def _parse_col23_model(self, model: COLModel, data: bytes): #vers 1
        """Parse COL version 2/3 model - CLEAN with debug control"""
        try:
            if len(data) < 40:
                if is_col_debug_enabled():
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
            model.bounding_box.min = Vector3(min_x, min_y, min_z)
            model.bounding_box.max = Vector3(max_x, max_y, max_z)
            offset += 24
            
            # Read name (22 bytes, null-terminated) if available
            if offset + 22 <= len(data):
                name_bytes = data[offset:offset+22]
                model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
                offset += 22
            
            # Set default name if empty
            if not model.name:
                model.name = f"Model_{int(time.time())}"
            
            # Initialize empty collision data for now
            model.spheres = []
            model.boxes = []
            model.vertices = []
            model.faces = []
            
            # Calculate bounding box
            model.calculate_bounding_box()
            model.update_flags()
            
            if is_col_debug_enabled():
                img_debugger.debug(f"COL2/3 model parsed: {model.name}")
                
        except Exception as e:
            if is_col_debug_enabled():
                img_debugger.error(f"Error parsing COL2/3 model: {e}")

    def get_raw_data(self) -> Optional[bytes]: #vers 1
        """Get raw COL file data for export"""
        # Placeholder - would need to implement COL file writing
        if is_col_debug_enabled():
            img_debugger.warning("COL file writing not yet implemented")
        return None
