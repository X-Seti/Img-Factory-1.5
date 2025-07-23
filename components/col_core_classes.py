#this belongs in components/col_core_classes.py - Version: 2
# X-Seti - July23 2025 - IMG Factory 1.5 - COL Core Classes - Complete Port
# Ported from col_core_classes.py-old with 100% functionality preservation
# ONLY debug system changed from old COL debug to img_debugger

"""
COL Core Classes - COMPLETE PORT
Core COL file handling classes with complete save/load functionality
Uses IMG debug system throughout - preserves 100% original functionality
Includes ALL missing classes: COLMaterial, COLFaceGroup, Vector3, etc.
"""

import os
import struct
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

# Import IMG debug system - NO fallback code
from components.img_debug_functions import img_debugger

##Functions list -
# _build_col1_model
# _build_col23_model
# _build_col_data
# _build_col_model
# _parse_col1_model
# _parse_col23_model
# _parse_col_data
# _parse_col_model
# calculate_bounding_box
# calculate_from_vertices
# diagnose_col_file
# get_info
# get_stats
# is_col_debug_enabled
# load
# load_from_data
# load_from_file
# save_to_file
# set_col_debug_enabled
# update_flags

##Classes list -
# BoundingBox
# COLFace
# COLFaceGroup
# COLFile
# COLMaterial
# COLModel
# COLSphere
# COLBox
# COLVertex
# COLVersion (Enum)
# Vector3

# Global debug state
_col_debug_enabled = False

def set_col_debug_enabled(enabled: bool): #vers 1
    """Enable or disable COL debug output"""
    global _col_debug_enabled
    _col_debug_enabled = enabled
    img_debugger.debug(f"COL debug {'enabled' if enabled else 'disabled'}")

def is_col_debug_enabled() -> bool: #vers 1
    """Check if COL debug is enabled"""
    return _col_debug_enabled

class COLVersion(Enum):
    """COL file version enumeration"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4

@dataclass
class Vector3:
    """3D vector class"""
    x: float
    y: float
    z: float
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self) -> str:
        return f"Vector3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

class BoundingBox:
    """3D bounding box class"""
    
    def __init__(self):
        self.min = Vector3(float('inf'), float('inf'), float('inf'))
        self.max = Vector3(float('-inf'), float('-inf'), float('-inf'))
        self.center = Vector3()
        self.radius = 0.0
    
    def calculate_from_vertices(self, vertices: List[Tuple[float, float, float]]): #vers 1
        """Calculate bounding box from vertex list"""
        if not vertices:
            return
        
        # Find min/max bounds
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        min_z = min(v[2] for v in vertices)
        max_z = max(v[2] for v in vertices)
        
        self.min = Vector3(min_x, min_y, min_z)
        self.max = Vector3(max_x, max_y, max_z)
        
        # Calculate center
        self.center = Vector3(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
        # Calculate radius
        import math
        self.radius = math.sqrt(
            (max_x - min_x) ** 2 +
            (max_y - min_y) ** 2 +
            (max_z - min_z) ** 2
        ) / 2

@dataclass
class COLMaterial:
    """COL material properties"""
    material_id: int
    friction: float = 1.0
    elasticity: float = 0.1
    flags: int = 0

@dataclass
class COLSphere:
    """COL collision sphere"""
    center: Vector3
    radius: float
    material: COLMaterial
    
    def __init__(self, center: Vector3 = None, radius: float = 1.0, material: COLMaterial = None):
        self.center = center or Vector3()
        self.radius = radius
        self.material = material or COLMaterial(0)

@dataclass
class COLBox:
    """COL collision box"""
    min_point: Vector3
    max_point: Vector3
    material: COLMaterial
    
    def __init__(self, min_point: Vector3 = None, max_point: Vector3 = None, material: COLMaterial = None):
        self.min_point = min_point or Vector3()
        self.max_point = max_point or Vector3()
        self.material = material or COLMaterial(0)

@dataclass
class COLVertex:
    """COL mesh vertex"""
    position: Vector3
    
    def __init__(self, position: Vector3 = None):
        self.position = position or Vector3()

@dataclass
class COLFace:
    """COL mesh face"""
    vertex_indices: Tuple[int, int, int]
    material: COLMaterial
    light: int = 255
    
    def __init__(self, vertex_indices: Tuple[int, int, int] = (0, 0, 0), material: COLMaterial = None, light: int = 255):
        self.vertex_indices = vertex_indices
        self.material = material or COLMaterial(0)
        self.light = light

@dataclass
class COLFaceGroup:
    """COL face group for material organization"""
    faces: List[COLFace]
    material: COLMaterial
    
    def __init__(self, material: COLMaterial = None):
        self.faces = []
        self.material = material or COLMaterial(0)

class COLModel:
    """COL collision model"""
    
    def __init__(self):
        self.name = ""
        self.model_id = 0
        self.version = COLVersion.COL_2
        
        # Collision geometry
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        
        # Shadow mesh (optional)
        self.shadow_vertices: List[COLVertex] = []
        self.shadow_faces: List[COLFace] = []
        
        # Bounding data
        self.bounding_box = BoundingBox()
        
        # Status flags
        self.has_sphere_data = False
        self.has_box_data = False
        self.has_mesh_data = False
    
    def calculate_bounding_box(self): #vers 1
        """Calculate bounding box from collision data"""
        all_vertices = []
        
        # Add sphere bounds
        for sphere in self.spheres:
            center = sphere.center
            radius = sphere.radius
            all_vertices.extend([
                (center.x - radius, center.y - radius, center.z - radius),
                (center.x + radius, center.y + radius, center.z + radius)
            ])
        
        # Add box bounds
        for box in self.boxes:
            all_vertices.extend([
                (box.min_point.x, box.min_point.y, box.min_point.z),
                (box.max_point.x, box.max_point.y, box.max_point.z)
            ])
        
        # Add mesh vertices
        for vertex in self.vertices:
            pos = vertex.position
            all_vertices.append((pos.x, pos.y, pos.z))
        
        # Calculate bounding box
        if all_vertices:
            self.bounding_box.calculate_from_vertices(all_vertices)
    
    def update_flags(self): #vers 1
        """Update status flags based on available data"""
        self.has_sphere_data = len(self.spheres) > 0
        self.has_box_data = len(self.boxes) > 0
        self.has_mesh_data = len(self.vertices) > 0 and len(self.faces) > 0
    
    def get_stats(self) -> Dict[str, int]: #vers 1
        """Get comprehensive model statistics"""
        return {
            'version': self.version.value,
            'spheres': len(self.spheres),
            'boxes': len(self.boxes),
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'face_groups': len(self.face_groups),
            'shadow_vertices': len(self.shadow_vertices),
            'shadow_faces': len(self.shadow_faces),
            'total_collision_objects': len(self.spheres) + len(self.boxes)
        }

class COLFile:
    """COL file handler with complete functionality"""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = None
        self.file_size = 0
    

    def load(self) -> bool: #vers 2
        """Load COL file - make sure load_error is set"""
        if not self.file_path:
            self.load_error = "No file path specified"
            return False

        return self.load_from_file(self.file_path)
    

    def load_from_file(self, file_path: str) -> bool: #vers 2
        """Load COL file from disk with proper error handling"""
        try:
            self.file_path = file_path
            self.load_error = None  # Clear any previous error

            if not os.path.exists(file_path):
                self.load_error = f"File not found: {file_path}"
                return False

            with open(file_path, 'rb') as f:
                data = f.read()

            self.file_size = len(data)

            if is_col_debug_enabled():
                img_debugger.debug(f"Loading COL file: {os.path.basename(file_path)} ({self.file_size} bytes)")

            return self.load_from_data(data)

        except Exception as e:
            self.load_error = f"File read error: {str(e)}"
            if is_col_debug_enabled():
                img_debugger.error(f"Error loading COL file: {e}")
            return False


    def load_from_data(self, data: bytes) -> bool: #vers 2
        """Load COL data from bytes with proper error handling"""
        try:
            self.models.clear()
            self.is_loaded = False
            self.load_error = None  # Clear any previous error

            if len(data) < 8:
                self.load_error = "File too small (less than 8 bytes)"
                return False

            # Check signature first
            signature = data[:4]
            if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                self.load_error = f"Invalid COL signature: {signature}"
                return False

            success = self._parse_col_data(data)

            if success:
                self.is_loaded = True
                if len(self.models) == 0:
                    self.load_error = "File parsed but no models found"
                    return False
            else:
                if not self.load_error:  # If no specific error was set
                    self.load_error = "Failed to parse COL data"

            return success

        except Exception as e:
            self.load_error = f"Data parsing error: {str(e)}"
            if is_col_debug_enabled():
                img_debugger.error(f"Error parsing COL data: {e}")
            return False


    def _parse_col_data(self, data: bytes) -> bool:
        """Parse COL data with enhanced debugging"""
        try:
            self.models = []
            offset = 0

            img_debugger.debug(f"_parse_col_data: Starting with {len(data)} bytes")

            model_count = 0
            while offset < len(data):
                img_debugger.debug(f"_parse_col_data: Parsing model {model_count} at offset {offset}")

                model, consumed = self._parse_col_model(data, offset)

                if model is None:
                    img_debugger.debug(f"_parse_col_data: Model parsing returned None, consumed: {consumed}")
                    if consumed == 0:  # No progress made
                        if len(self.models) == 0:
                            self.load_error = f"Failed to parse any models (stopped at offset {offset})"
                            img_debugger.error(f"_parse_col_data: {self.load_error}")
                            return False
                        else:
                            img_debugger.debug(f"_parse_col_data: Got {len(self.models)} models, stopping here")
                            break
                    break

                self.models.append(model)
                offset += consumed
                model_count += 1

                img_debugger.debug(f"_parse_col_data: Model {model_count-1} parsed successfully, new offset: {offset}")

                # Safety check to prevent infinite loops
                if consumed == 0:
                    img_debugger.warning("_parse_col_data: No bytes consumed, breaking to prevent infinite loop")
                    break

                # Safety limit
                if model_count > 1000:
                    img_debugger.warning("_parse_col_data: Safety limit reached (1000 models)")
                    break

            success = len(self.models) > 0

            img_debugger.debug(f"_parse_col_data: Parsing complete - {len(self.models)} models loaded, success: {success}")

            return success

        except Exception as e:
            self.load_error = f"Model parsing error: {str(e)}"
            img_debugger.error(f"_parse_col_data: Exception: {e}")
            import traceback
            img_debugger.error(f"_parse_col_data: Traceback: {traceback.format_exc()}")
            return False


    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]: #vers 3

        try:
            img_debugger.debug(f"_parse_col_model: Starting at offset {offset}, data length {len(data)}")

            if offset + 8 > len(data):
                img_debugger.debug(f"_parse_col_model: Not enough data for header (need 8, have {len(data) - offset})")
                return None, 0

            # Read FourCC signature
            fourcc = data[offset:offset+4]
            img_debugger.debug(f"_parse_col_model: Read FourCC: {fourcc}")

            if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                img_debugger.debug(f"_parse_col_model: Invalid FourCC signature: {fourcc}")
                return None, 0

            # Read file size
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = file_size + 8

            img_debugger.debug(f"_parse_col_model: File size from header: {file_size}, total size: {total_size}")

            if offset + total_size > len(data):
                img_debugger.warning(f"_parse_col_model: Model size extends beyond data: need {total_size}, have {len(data) - offset}")
                return None, 0

            # Create model
            model = COLModel()

            # Determine version
            if fourcc == b'COLL':
                model.version = COLVersion.COL_1
                img_debugger.debug("_parse_col_model: Detected COL1 format")
            elif fourcc == b'COL\x02':
                model.version = COLVersion.COL_2
                img_debugger.debug("_parse_col_model: Detected COL2 format")
            elif fourcc == b'COL\x03':
                model.version = COLVersion.COL_3
                img_debugger.debug("_parse_col_model: Detected COL3 format")
            elif fourcc == b'COL\x04':
                model.version = COLVersion.COL_4
                img_debugger.debug("_parse_col_model: Detected COL4 format")

            # Parse model data based on version
            model_data = data[offset + 8:offset + total_size]
            img_debugger.debug(f"_parse_col_model: Extracted model data: {len(model_data)} bytes")

            try:
                if model.version == COLVersion.COL_1:
                    img_debugger.debug("_parse_col_model: Calling _parse_col1_model")
                    self._parse_col1_model(model, model_data)
                else:
                    img_debugger.debug("_parse_col_model: Calling _parse_col23_model")
                    self._parse_col23_model(model, model_data)
            except Exception as e:
                img_debugger.error(f"_parse_col_model: Failed to parse model data: {e}")
                import traceback
                img_debugger.error(f"_parse_col_model: Traceback: {traceback.format_exc()}")
                return None, 0

            # Validate the model was parsed correctly
            if hasattr(model, 'get_stats'):
                stats = model.get_stats()
                img_debugger.debug(f"_parse_col_model: Model parsed successfully - {stats}")
            else:
                img_debugger.debug("_parse_col_model: Model parsed (no stats available)")

            return model, total_size

        except Exception as e:
            img_debugger.error(f"_parse_col_model: Exception in method: {e}")
            import traceback
            img_debugger.error(f"_parse_col_model: Traceback: {traceback.format_exc()}")
            return None, 0
    """

    def _parse_col_model(self, data: bytes, offset: int):
        #SIMPLE TEST VERSION - Replace with real version once this works
        img_debugger.debug("=== _parse_col_model: TEST VERSION CALLED ===")
        img_debugger.debug(f"=== offset: {offset}, data length: {len(data)} ===")

        if offset + 8 > len(data):
            img_debugger.debug("=== Not enough data for header ===")
            return None, 0

        fourcc = data[offset:offset+4]
        img_debugger.debug(f"=== FourCC: {fourcc} ===")

        if fourcc == b'COLL':
            img_debugger.debug("=== Valid COLL signature found ===")
            # For now, just return a minimal success to test
            from components.col_core_classes import COLModel, COLVersion
            model = COLModel()
            model.version = COLVersion.COL_1
            model.name = "test_model"
            return model, 100  # Return some consumed bytes
        else:
            img_debugger.debug(f"=== Invalid signature: {fourcc} ===")
            return None, 0

    """

    def _parse_col1_model(self, model: COLModel, data: bytes): #vers 1
        """Parse COL1 format model"""
        offset = 0
        
        # Parse model name (22 bytes)
        name_bytes = data[offset:offset+22]
        model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
        offset += 22
        
        # Parse model ID (2 bytes)
        model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        
        # Parse bounding data (40 bytes)
        bounding_radius = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        bounding_center = struct.unpack('<fff', data[offset:offset+12])
        offset += 12
        bounding_min = struct.unpack('<fff', data[offset:offset+12])
        offset += 12
        bounding_max = struct.unpack('<fff', data[offset:offset+12])
        offset += 12
        
        # Set bounding box
        model.bounding_box.center = Vector3(*bounding_center)
        model.bounding_box.min = Vector3(*bounding_min)
        model.bounding_box.max = Vector3(*bounding_max)
        model.bounding_box.radius = bounding_radius
        
        # Parse counts (20 bytes)
        num_spheres = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_unknown = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_boxes = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_vertices = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_faces = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Parse spheres
        for i in range(num_spheres):
            center = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            material_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            flags = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            material = COLMaterial(material_id, flags=flags)
            sphere = COLSphere(center, radius, material)
            model.spheres.append(sphere)
        
        # Skip unknown data
        offset += num_unknown * 4
        
        # Parse boxes
        for i in range(num_boxes):
            min_point = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            max_point = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            material_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            flags = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            material = COLMaterial(material_id, flags=flags)
            box = COLBox(min_point, max_point, material)
            model.boxes.append(box)
        
        # Parse vertices
        for i in range(num_vertices):
            position = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            vertex = COLVertex(position)
            model.vertices.append(vertex)
        
        # Parse faces
        for i in range(num_faces):
            vertex_indices = struct.unpack('<HHH', data[offset:offset+6])
            offset += 6
            material_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            light = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            flags = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            material = COLMaterial(material_id, flags=flags)
            face = COLFace(vertex_indices, material, light)
            model.faces.append(face)
        
        model.update_flags()
    
    def _parse_col23_model(self, model: COLModel, data: bytes): #vers 1
        """Parse COL2/COL3 format model"""
        offset = 0
        
        # Parse model name (22 bytes)
        name_bytes = data[offset:offset+22]
        model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
        offset += 22
        
        # Parse model ID (2 bytes)
        model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        
        # Parse bounding data (28 bytes)
        bounding_min = struct.unpack('<fff', data[offset:offset+12])
        offset += 12
        bounding_max = struct.unpack('<fff', data[offset:offset+12])
        offset += 12
        bounding_center = struct.unpack('<fff', data[offset:offset+12])
        offset += 12
        bounding_radius = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Set bounding box
        model.bounding_box.center = Vector3(*bounding_center)
        model.bounding_box.min = Vector3(*bounding_min)
        model.bounding_box.max = Vector3(*bounding_max)
        model.bounding_box.radius = bounding_radius
        
        # Parse counts (16 bytes)
        num_spheres = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_boxes = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_faces = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        num_vertices = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Parse spheres
        for i in range(num_spheres):
            center = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            material_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            material = COLMaterial(material_id)
            sphere = COLSphere(center, radius, material)
            model.spheres.append(sphere)
        
        # Parse boxes
        for i in range(num_boxes):
            min_point = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            max_point = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            material_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            material = COLMaterial(material_id)
            box = COLBox(min_point, max_point, material)
            model.boxes.append(box)
        
        # Parse vertices
        for i in range(num_vertices):
            position = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
            offset += 12
            vertex = COLVertex(position)
            model.vertices.append(vertex)
        
        # Parse faces
        for i in range(num_faces):
            vertex_indices = struct.unpack('<HHH', data[offset:offset+6])
            offset += 6
            material_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            light = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            offset += 2  # Skip padding
            
            material = COLMaterial(material_id)
            face = COLFace(vertex_indices, material, light)
            model.faces.append(face)
        
        model.update_flags()
    
    def save_to_file(self, file_path: str = None) -> bool: #vers 1
        """Save COL file to disk"""
        try:
            if file_path:
                self.file_path = file_path
            
            if not self.file_path:
                self.load_error = "No file path specified"
                return False
            
            # Build COL data
            col_data = self._build_col_data()
            
            # Write to file
            with open(self.file_path, 'wb') as f:
                f.write(col_data)
            
            if is_col_debug_enabled():
                img_debugger.success(f"COL file saved: {self.file_path} ({len(col_data)} bytes)")
            
            return True
            
        except Exception as e:
            self.load_error = str(e)
            if is_col_debug_enabled():
                img_debugger.error(f"Error saving COL file: {e}")
            return False
    
    def _build_col_data(self) -> bytes: #vers 1
        """Build COL file data from models"""
        data = b''
        
        for model in self.models:
            model_data = self._build_col_model(model)
            data += model_data
        
        return data
    
    def _build_col_model(self, model: COLModel) -> bytes: #vers 1
        """Build single COL model data"""
        if model.version == COLVersion.COL_1:
            return self._build_col1_model(model)
        else:
            return self._build_col23_model(model)
    
    def _build_col1_model(self, model: COLModel) -> bytes: #vers 1
        """Build COL1 format model data"""
        data = b''
        
        # Build model data first to calculate size
        model_content = b''
        
        # Model name (22 bytes)
        name_bytes = model.name.encode('ascii')[:21].ljust(22, b'\x00')
        model_content += name_bytes
        
        # Model ID (2 bytes)
        model_content += struct.pack('<H', model.model_id)
        
        # Bounding data (40 bytes)
        model_content += struct.pack('<f', model.bounding_box.radius)
        model_content += struct.pack('<fff', model.bounding_box.center.x, model.bounding_box.center.y, model.bounding_box.center.z)
        model_content += struct.pack('<fff', model.bounding_box.min.x, model.bounding_box.min.y, model.bounding_box.min.z)
        model_content += struct.pack('<fff', model.bounding_box.max.x, model.bounding_box.max.y, model.bounding_box.max.z)
        
        # Counts (20 bytes)
        model_content += struct.pack('<I', len(model.spheres))
        model_content += struct.pack('<I', 0)  # Unknown count
        model_content += struct.pack('<I', len(model.boxes))
        model_content += struct.pack('<I', len(model.vertices))
        model_content += struct.pack('<I', len(model.faces))
        
        # Spheres
        for sphere in model.spheres:
            model_content += struct.pack('<fff', sphere.center.x, sphere.center.y, sphere.center.z)
            model_content += struct.pack('<f', sphere.radius)
            model_content += struct.pack('<I', sphere.material.material_id)
            model_content += struct.pack('<I', sphere.material.flags)
        
        # Boxes
        for box in model.boxes:
            model_content += struct.pack('<fff', box.min_point.x, box.min_point.y, box.min_point.z)
            model_content += struct.pack('<fff', box.max_point.x, box.max_point.y, box.max_point.z)
            model_content += struct.pack('<I', box.material.material_id)
            model_content += struct.pack('<I', box.material.flags)
        
        # Vertices
        for vertex in model.vertices:
            model_content += struct.pack('<fff', vertex.position.x, vertex.position.y, vertex.position.z)
        
        # Faces
        for face in model.faces:
            model_content += struct.pack('<HHH', *face.vertex_indices)
            model_content += struct.pack('<H', face.material.material_id)
            model_content += struct.pack('<H', face.light)
            model_content += struct.pack('<I', face.material.flags)
        
        # Build header
        data += b'COLL'  # Signature
        data += struct.pack('<I', len(model_content))  # File size
        data += model_content
        
        return data
    
    def _build_col23_model(self, model: COLModel) -> bytes: #vers 1
        """Build COL2/COL3 format model data"""
        data = b''
        
        # Build model data first to calculate size
        model_content = b''
        
        # Model name (22 bytes)
        name_bytes = model.name.encode('ascii')[:21].ljust(22, b'\x00')
        model_content += name_bytes
        
        # Model ID (2 bytes)
        model_content += struct.pack('<H', model.model_id)
        
        # Bounding data (28 bytes)
        model_content += struct.pack('<fff', model.bounding_box.min.x, model.bounding_box.min.y, model.bounding_box.min.z)
        model_content += struct.pack('<fff', model.bounding_box.max.x, model.bounding_box.max.y, model.bounding_box.max.z)
        model_content += struct.pack('<fff', model.bounding_box.center.x, model.bounding_box.center.y, model.bounding_box.center.z)
        model_content += struct.pack('<f', model.bounding_box.radius)
        
        # Counts (16 bytes)
        model_content += struct.pack('<I', len(model.spheres))
        model_content += struct.pack('<I', len(model.boxes))
        model_content += struct.pack('<I', len(model.faces))
        model_content += struct.pack('<I', len(model.vertices))
        
        # Spheres
        for sphere in model.spheres:
            model_content += struct.pack('<fff', sphere.center.x, sphere.center.y, sphere.center.z)
            model_content += struct.pack('<f', sphere.radius)
            model_content += struct.pack('<I', sphere.material.material_id)
        
        # Boxes
        for box in model.boxes:
            model_content += struct.pack('<fff', box.min_point.x, box.min_point.y, box.min_point.z)
            model_content += struct.pack('<fff', box.max_point.x, box.max_point.y, box.max_point.z)
            model_content += struct.pack('<I', box.material.material_id)
        
        # Vertices
        for vertex in model.vertices:
            model_content += struct.pack('<fff', vertex.position.x, vertex.position.y, vertex.position.z)
        
        # Faces
        for face in model.faces:
            model_content += struct.pack('<HHH', *face.vertex_indices)
            model_content += struct.pack('<H', face.material.material_id)
            model_content += struct.pack('<H', face.light)
            model_content += struct.pack('<H', 0)  # Padding
        
        # Build header with appropriate signature
        if model.version == COLVersion.COL_2:
            data += b'COL\x02'
        elif model.version == COLVersion.COL_3:
            data += b'COL\x03'
        else:
            data += b'COL\x04'
        
        data += struct.pack('<I', len(model_content))  # File size
        data += model_content
        
        return data
    
    def get_info(self) -> str: #vers 1
        """Get comprehensive file information"""
        lines = []
        
        lines.append(f"COL File: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}")
        lines.append(f"File Size: {self.file_size:,} bytes")
        lines.append(f"Models: {len(self.models)}")
        
        if self.is_loaded:
            total_stats = {
                'spheres': sum(len(m.spheres) for m in self.models),
                'boxes': sum(len(m.boxes) for m in self.models),
                'vertices': sum(len(m.vertices) for m in self.models),
                'faces': sum(len(m.faces) for m in self.models)
            }
            
            lines.append(f"Total Objects: {total_stats['spheres']} spheres, {total_stats['boxes']} boxes")
            lines.append(f"Total Geometry: {total_stats['vertices']} vertices, {total_stats['faces']} faces")
        else:
            lines.append(f"Loaded: No")
            if self.load_error:
                lines.append(f"Error: {self.load_error}")
        
        return "\n".join(lines)

def diagnose_col_file(file_path: str) -> dict: #vers 1
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
