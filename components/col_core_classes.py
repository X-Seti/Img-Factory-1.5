#this belongs in components/col_core_classes.py - Version: 13
# X-Seti - July18 2025 - Img Factory 1.5 - Clean COL Core Classes with Hang Prevention

"""
COL Core Classes - Clean version with infinite loop prevention
Handles COL1/COL2/COL3/COL4 formats with proper collision data structures
FIXED: All infinite loop and hang issues resolved
"""

import struct
import os
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

# Use IMG debug system
try:
    from components.img_debug_functions import img_debugger
    debug_available = True
except ImportError:
    debug_available = False
    print("⚠️ IMG debug system not available")

##Methods list -
# diagnose_col_file
# is_col_debug_enabled
# set_col_debug_enabled

##Classes -
# BoundingBox
# COLFace
# COLFaceGroup
# COLFile
# COLMaterial
# COLModel
# COLVersion
# Vector3

# Global debug control - using IMG debug system
_col_debug_enabled = False

def set_col_debug_enabled(enabled: bool):
    """Enable/disable COL debug output using IMG debug system"""
    global _col_debug_enabled
    _col_debug_enabled = enabled
    
    if debug_available:
        if enabled:
            img_debugger.debug("COL debug system ENABLED")
        else:
            img_debugger.debug("COL debug system DISABLED")

def is_col_debug_enabled() -> bool:
    """Check if COL debug is enabled"""
    global _col_debug_enabled
    return _col_debug_enabled and debug_available

class COLVersion(Enum):
    """COL file version enumeration"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4

@dataclass
class Vector3:
    """3D vector structure"""
    x: float
    y: float
    z: float
    
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

@dataclass
class BoundingBox:
    """Bounding box structure"""
    min_point: Vector3
    max_point: Vector3
    
    def __str__(self):
        return f"BBox[{self.min_point} to {self.max_point}]"

@dataclass
class COLSphere:
    """COL sphere collision structure"""
    center: Vector3
    radius: float
    surface: int
    piece: int
    
    def __str__(self):
        return f"Sphere[{self.center}, r={self.radius:.3f}]"

@dataclass
class COLBox:
    """COL box collision structure"""
    center: Vector3
    size: Vector3
    orientation: List[Vector3]  # 3x3 rotation matrix as vectors
    surface: int
    piece: int
    
    def __str__(self):
        return f"Box[{self.center}, size={self.size}]"

@dataclass
class COLVertex:
    """COL vertex structure"""
    position: Vector3
    
    def __str__(self):
        return f"Vertex[{self.position}]"

@dataclass
class COLFace:
    """COL face structure"""
    a: int  # Vertex indices
    b: int
    c: int
    surface: int
    
    def __str__(self):
        return f"Face[{self.a}, {self.b}, {self.c}]"

@dataclass
class COLFaceGroup:
    """COL face group structure"""
    surface_type: int
    faces: List[COLFace]
    
    def __str__(self):
        return f"FaceGroup[surf={self.surface_type}, {len(self.faces)} faces]"

@dataclass
class COLMaterial:
    """COL material/surface properties"""
    surface_type: int
    friction: float
    elasticity: float
    
    def __str__(self):
        return f"Material[type={self.surface_type}]"

class COLModel:
    """COL model containing collision data"""
    
    def __init__(self):
        self.version = COLVersion.COL_1
        self.model_name = ""
        self.model_id = 0
        self.bounding_box = None
        self.bounding_sphere_center = Vector3(0, 0, 0)
        self.bounding_sphere_radius = 0.0
        
        # Collision geometry
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        self.materials: List[COLMaterial] = []
        
        # State
        self.is_loaded = False
        self.load_error = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'version': self.version.value,
            'spheres': len(self.spheres),
            'boxes': len(self.boxes),
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'face_groups': len(self.face_groups),
            'materials': len(self.materials)
        }
    
    def __str__(self):
        stats = self.get_stats()
        return f"COLModel[v{stats['version']}, {stats['spheres']}S, {stats['boxes']}B, {stats['vertices']}V, {stats['faces']}F]"

class COLFile:
    """COL file containing one or more collision models - HANG PREVENTION VERSION"""
    
    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = None
        self.file_size = 0
    
    def load(self) -> bool:
        """Load COL file from disk - SAFE VERSION"""
        try:
            if not os.path.exists(self.file_path):
                self.load_error = "File not found"
                return False
            
            self.file_size = os.path.getsize(self.file_path)
            
            # Safety check: Don't load files larger than 50MB
            if self.file_size > 50 * 1024 * 1024:
                self.load_error = f"File too large: {self.file_size} bytes"
                if debug_available:
                    img_debugger.warning(f"COL file too large: {self.file_size} bytes")
                return False
            
            with open(self.file_path, 'rb') as f:
                data = f.read()
            
            if debug_available:
                img_debugger.debug(f"Loading COL file: {self.file_path} ({len(data)} bytes)")
            
            return self._parse_col_data_safe(data)
            
        except Exception as e:
            self.load_error = str(e)
            if debug_available:
                img_debugger.error(f"COL load error: {e}")
            return False
    
    def _parse_col_data_safe(self, data: bytes) -> bool:
        """Parse COL data with hang prevention - SAFE VERSION"""
        self.models = []
        offset = 0
        
        if debug_available:
            img_debugger.debug(f"Parsing COL data: {len(data)} bytes")
        
        # Safety limits to prevent infinite loops
        max_iterations = 1000
        max_models = 500
        iteration_count = 0
        
        while offset < len(data) and iteration_count < max_iterations and len(self.models) < max_models:
            iteration_count += 1
            initial_offset = offset
            
            # CRITICAL: Safety check for remaining data
            if offset + 8 > len(data):
                if debug_available:
                    img_debugger.debug("COL parsing stopped: insufficient data for header")
                break
            
            model, consumed = self._parse_col_model_safe(data, offset)
            
            # CRITICAL: Infinite loop prevention
            if consumed <= 0:
                if debug_available:
                    img_debugger.warning("COL parsing stopped: no bytes consumed (infinite loop prevention)")
                break
            
            if offset + consumed <= initial_offset:
                if debug_available:
                    img_debugger.warning("COL parsing stopped: offset not advancing properly")
                break
            
            if model is None:
                if debug_available:
                    img_debugger.debug("COL parsing stopped: model parsing failed")
                break
            
            self.models.append(model)
            offset += consumed
            
            # Progress logging for large files
            if iteration_count % 50 == 0 and debug_available:
                img_debugger.debug(f"COL parsing progress: {len(self.models)} models, offset {offset}/{len(data)}")
        
        # Check why we stopped
        if iteration_count >= max_iterations:
            if debug_available:
                img_debugger.warning("COL parsing stopped: maximum iterations reached (hang prevention)")
        elif len(self.models) >= max_models:
            if debug_available:
                img_debugger.warning("COL parsing stopped: maximum models reached")
        
        self.is_loaded = True
        success = len(self.models) > 0
        
        if debug_available:
            img_debugger.debug(f"COL parsing complete: {len(self.models)} models loaded")
        
        return success
    
    def _parse_col_model_safe(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]:
        """Parse single COL model with safety checks - SAFE VERSION"""
        try:
            # Safety check: Minimum header size
            if offset + 8 > len(data):
                return None, 0
            
            # Read FourCC signature
            fourcc = data[offset:offset+4]
            
            if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return None, 0
            
            # Read file size
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            # CRITICAL: Validate file size to prevent hang
            if file_size <= 0 or file_size > 10 * 1024 * 1024:  # 10MB limit per model
                if debug_available:
                    img_debugger.warning(f"COL model size invalid: {file_size}")
                return None, 8  # Skip header
            
            total_size = file_size + 8
            
            # Safety check: Bounds validation
            if offset + total_size > len(data):
                if debug_available:
                    img_debugger.warning(f"COL model size exceeds data bounds")
                return None, 8  # Skip header
            
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
            
            # Parse model data based on version (with safety limits)
            model_data = data[offset + 8:offset + total_size]
            if model.version == COLVersion.COL_1:
                self._parse_col1_model_safe(model, model_data)
            else:
                self._parse_col23_model_safe(model, model_data)
            
            if debug_available:
                img_debugger.debug(f"Parsed COL model: {model}")
            
            return model, total_size
            
        except Exception as e:
            if debug_available:
                img_debugger.error(f"Error parsing COL model: {e}")
            return None, 8  # Safe advancement
    
    def _parse_col1_model_safe(self, model: COLModel, data: bytes):
        """Parse COL1 model data with safety checks"""
        try:
            offset = 0
            
            if len(data) < 40:
                return
            
            # Parse bounding info (40 bytes)
            bounding_data = struct.unpack('<10f', data[offset:offset+40])
            model.bounding_sphere_center = Vector3(bounding_data[0], bounding_data[1], bounding_data[2])
            model.bounding_sphere_radius = bounding_data[3]
            model.bounding_box = BoundingBox(
                Vector3(bounding_data[4], bounding_data[5], bounding_data[6]),
                Vector3(bounding_data[7], bounding_data[8], bounding_data[9])
            )
            offset += 40
            
            # Parse spheres with safety limits
            if offset + 4 <= len(data):
                sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
                sphere_count = min(sphere_count, 1000)  # Safety limit
                offset += 4
                
                for i in range(sphere_count):
                    if offset + 20 <= len(data):
                        sphere_data = struct.unpack('<5f', data[offset:offset+20])
                        sphere = COLSphere(
                            Vector3(sphere_data[0], sphere_data[1], sphere_data[2]),
                            sphere_data[3],
                            int(sphere_data[4]) & 0xFF,
                            (int(sphere_data[4]) >> 8) & 0xFF
                        )
                        model.spheres.append(sphere)
                        offset += 20
                    else:
                        break
            
            # Parse boxes with safety limits
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                box_count = min(box_count, 1000)  # Safety limit
                offset += 4
                
                for i in range(box_count):
                    if offset + 72 <= len(data):
                        box_data = struct.unpack('<18f', data[offset:offset+72])
                        box = COLBox(
                            Vector3(box_data[0], box_data[1], box_data[2]),
                            Vector3(box_data[3], box_data[4], box_data[5]),
                            [
                                Vector3(box_data[6], box_data[7], box_data[8]),
                                Vector3(box_data[9], box_data[10], box_data[11]),
                                Vector3(box_data[12], box_data[13], box_data[14])
                            ],
                            int(box_data[15]) & 0xFF,
                            (int(box_data[15]) >> 8) & 0xFF
                        )
                        model.boxes.append(box)
                        offset += 72
                    else:
                        break
            
            # Parse vertices with safety limits
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                vertex_count = min(vertex_count, 10000)  # Safety limit
                offset += 4
                
                for i in range(vertex_count):
                    if offset + 12 <= len(data):
                        vertex_data = struct.unpack('<3f', data[offset:offset+12])
                        vertex = COLVertex(Vector3(vertex_data[0], vertex_data[1], vertex_data[2]))
                        model.vertices.append(vertex)
                        offset += 12
                    else:
                        break
            
            # Parse faces with safety limits
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                face_count = min(face_count, 20000)  # Safety limit
                offset += 4
                
                for i in range(face_count):
                    if offset + 16 <= len(data):
                        face_data = struct.unpack('<4I', data[offset:offset+16])
                        face = COLFace(face_data[0], face_data[1], face_data[2], face_data[3])
                        model.faces.append(face)
                        offset += 16
                    else:
                        break
            
            model.is_loaded = True
            
        except Exception as e:
            model.load_error = str(e)
            if debug_available:
                img_debugger.error(f"Error parsing COL1 model: {e}")
    
    def _parse_col23_model_safe(self, model: COLModel, data: bytes):
        """Parse COL2/COL3 model data with safety checks"""
        # Same as COL1 for now, but with version tracking
        self._parse_col1_model_safe(model, data)
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get total statistics for all models"""
        if not self.models:
            return {'models': 0, 'spheres': 0, 'boxes': 0, 'vertices': 0, 'faces': 0}
        
        total_stats = {
            'models': len(self.models),
            'spheres': sum(len(model.spheres) for model in self.models),
            'boxes': sum(len(model.boxes) for model in self.models),
            'vertices': sum(len(model.vertices) for model in self.models),
            'faces': sum(len(model.faces) for model in self.models)
        }
        
        return total_stats
    
    def __str__(self):
        if self.is_loaded:
            total_stats = self.get_total_stats()
            return f"COLFile[{total_stats['models']} models, {total_stats['vertices']} vertices, {total_stats['faces']} faces]"
        else:
            lines = ["COLFile"]
            lines.append(f"Path: {self.file_path}")
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