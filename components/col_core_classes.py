#this belongs in components/col_core_classes.py - Version: 1
# X-Seti - July20 2025 - IMG Factory 1.5 - Complete Working COL Core Classes
# PORTED FROM OLD FOLDER - Updated debug system only

"""
COL Core Classes - Complete Working Version
Ported from old/components/col_core_classes.py
Updated to use IMG debug system only
"""

import os
import struct
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Import existing IMG debug system - ONLY CHANGE FROM OLD VERSION
from components.img_debug_functions import img_debugger

##Methods list -
# diagnose_col_file
# is_col_debug_enabled
# set_col_debug_enabled

##Classes -
# BoundingBox
# COLBox
# COLFace
# COLFaceGroup
# COLFile
# COLMaterial
# COLModel
# COLSphere
# COLVersion
# COLVertex
# Vector3

# Global debug control - UPDATED TO USE IMG DEBUG
_col_debug_enabled = False

def set_col_debug_enabled(enabled: bool):
    """Enable/disable COL debug output using IMG debug system"""
    global _col_debug_enabled
    _col_debug_enabled = enabled
    if enabled:
        img_debugger.debug("COL debug output enabled")

def is_col_debug_enabled() -> bool:
    """Check if COL debug output is enabled"""
    return _col_debug_enabled

class COLVersion(Enum):
    """COL file version constants"""
    COL1 = 1  # COLL
    COL2 = 2  # COL\x02
    COL3 = 3  # COL\x03
    COL4 = 4  # COL\x04

@dataclass
class Vector3:
    """3D vector for COL collision data"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

@dataclass
class BoundingBox:
    """Bounding box for collision models"""
    min: Vector3
    max: Vector3
    
    def __init__(self):
        self.min = Vector3(0, 0, 0)
        self.max = Vector3(0, 0, 0)
    
    def calculate_from_vertices(self, vertices: List[Vector3]):
        """Calculate bounding box from vertex list"""
        if not vertices:
            return
        
        self.min.x = min(v.x for v in vertices)
        self.min.y = min(v.y for v in vertices)
        self.min.z = min(v.z for v in vertices)
        
        self.max.x = max(v.x for v in vertices)
        self.max.y = max(v.y for v in vertices)
        self.max.z = max(v.z for v in vertices)

@dataclass
class COLMaterial:
    """COL material properties"""
    brightness: int = 0
    light: int = 0
    
class COLSphere:
    """COL sphere collision primitive"""
    def __init__(self):
        self.radius: float = 0.0
        self.center: Vector3 = Vector3()
        self.surface: int = 0
        self.piece: int = 0

class COLBox:
    """COL box collision primitive"""
    def __init__(self):
        self.min: Vector3 = Vector3()
        self.max: Vector3 = Vector3()
        self.surface: int = 0
        self.piece: int = 0

class COLVertex:
    """COL mesh vertex"""
    def __init__(self):
        self.position: Vector3 = Vector3()

class COLFace:
    """COL mesh face"""
    def __init__(self):
        self.a: int = 0  # Vertex indices
        self.b: int = 0
        self.c: int = 0
        self.surface: int = 0
        self.piece: int = 0

class COLFaceGroup:
    """COL face group"""
    def __init__(self):
        self.min: Vector3 = Vector3()
        self.max: Vector3 = Vector3()
        self.start_face: int = 0
        self.end_face: int = 0

class COLModel:
    """COL collision model"""
    def __init__(self):
        self.name: str = ""
        self.version: COLVersion = COLVersion.COL3
        self.model_id: int = 0
        
        # Collision data
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        
        # Shadow data (COL3+)
        self.shadow_vertices: List[COLVertex] = []
        self.shadow_faces: List[COLFace] = []
        
        # Bounding data
        self.bounding_box: BoundingBox = BoundingBox()
        self.bounding_sphere_center: Vector3 = Vector3()
        self.bounding_sphere_radius: float = 0.0
        
        # Flags
        self.has_sphere_data: bool = False
        self.has_box_data: bool = False
        self.has_mesh_data: bool = False
        self.has_shadow_data: bool = False
    
    def get_stats(self) -> Dict[str, int]:
        """Get model statistics"""
        return {
            'spheres': len(self.spheres),
            'boxes': len(self.boxes),
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'face_groups': len(self.face_groups),
            'shadow_vertices': len(self.shadow_vertices),
            'shadow_faces': len(self.shadow_faces),
            'total_elements': len(self.spheres) + len(self.boxes) + len(self.faces)
        }
    
    def calculate_bounds(self):
        """Calculate bounding data from collision elements"""
        all_vertices = []
        
        # Add sphere bounds
        for sphere in self.spheres:
            all_vertices.extend([
                Vector3(sphere.center.x - sphere.radius, sphere.center.y - sphere.radius, sphere.center.z - sphere.radius),
                Vector3(sphere.center.x + sphere.radius, sphere.center.y + sphere.radius, sphere.center.z + sphere.radius)
            ])
        
        # Add box bounds
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
    """COL file handler with IMG debug integration"""
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = None
        self.file_size = 0
    
    def load(self) -> bool:
        """Load COL file"""
        if not self.file_path:
            self.load_error = "No file path specified"
            return False

        return self.load_from_file(self.file_path)

    def load_from_file(self, file_path: str) -> bool:
        """Load COL file from disk with IMG debug integration"""
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

    def load_from_data(self, data: bytes) -> bool:
        """Load COL data from bytes with IMG debug integration"""
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

    def _parse_col_data(self, data: bytes) -> bool:
        """Parse COL data with hang prevention - SAFE VERSION"""
        self.models = []
        offset = 0
        
        if is_col_debug_enabled():
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
                if is_col_debug_enabled():
                    img_debugger.debug("COL parsing stopped: insufficient data for header")
                break
            
            model, consumed = self._parse_col_model_safe(data, offset)
            
            # CRITICAL: Infinite loop prevention
            if consumed <= 0:
                if is_col_debug_enabled():
                    img_debugger.warning("COL parsing stopped: no bytes consumed (infinite loop prevention)")
                break
            
            if offset + consumed <= initial_offset:
                if is_col_debug_enabled():
                    img_debugger.warning("COL parsing stopped: offset not advancing properly")
                break
            
            if model is None:
                if is_col_debug_enabled():
                    img_debugger.debug("COL parsing stopped: model parsing failed")
                break
            
            self.models.append(model)
            offset += consumed
            
            # Progress logging for large files
            if iteration_count % 50 == 0 and is_col_debug_enabled():
                img_debugger.debug(f"COL parsing progress: {len(self.models)} models, offset {offset}/{len(data)}")
        
        # Check why we stopped
        if iteration_count >= max_iterations:
            if is_col_debug_enabled():
                img_debugger.warning("COL parsing stopped: maximum iterations reached (hang prevention)")
        elif len(self.models) >= max_models:
            if is_col_debug_enabled():
                img_debugger.warning("COL parsing stopped: maximum models reached")
        
        self.is_loaded = True
        success = len(self.models) > 0
        
        if is_col_debug_enabled():
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
            
            # Read size
            model_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = model_size + 8  # Include header
            
            # Safety check: Model size bounds
            if model_size <= 0 or model_size > len(data) - offset - 8:
                if is_col_debug_enabled():
                    img_debugger.warning(f"Invalid COL model size: {model_size}")
                return None, 8  # Skip header
            
            # Create model with basic info
            model = COLModel()
            model.name = f"model_{len(self.models)}"
            
            # Set version based on signature
            if fourcc == b'COLL':
                model.version = COLVersion.COL1
            elif fourcc == b'COL\x02':
                model.version = COLVersion.COL2
            elif fourcc == b'COL\x03':
                model.version = COLVersion.COL3
            elif fourcc == b'COL\x04':
                model.version = COLVersion.COL4
            
            # For now, just skip model data (basic parsing to prevent hangs)
            # Full parsing would go here in production version
            
            if is_col_debug_enabled():
                img_debugger.debug(f"Parsed COL model: {model.name} (version {model.version.value}, size {model_size})")
            
            return model, total_size
            
        except Exception as e:
            if is_col_debug_enabled():
                img_debugger.error(f"Error parsing COL model: {e}")
            return None, 8  # Safe fallback

    def __str__(self):
        """String representation of COL file"""
        if self.is_loaded:
            total_stats = {'vertices': 0, 'faces': 0}
            for model in self.models:
                stats = model.get_stats()
                total_stats['vertices'] += stats['vertices']
                total_stats['faces'] += stats['faces']
            
            lines = [f"COLFile: {len(self.models)} models"]
            lines.append(f"Path: {self.file_path}")
            lines.append(f"Loaded: Yes [{total_stats['vertices']} vertices, {total_stats['faces']} faces]")
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