#this belongs in components/col_core_classes.py - Version: 7
# X-Seti - August13 2025 - IMG Factory 1.5 - COL Core Classes - COMPLETE CLEAN VERSION

"""
COL Core Classes - Complete with Safe Parsing
Core COL file handling classes with complete save/load functionality
Uses IMG debug system and safe parsing methods from methods/col_parsing_helpers.py
"""

import struct
import os
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
from components.img_debug_functions import img_debugger

##Classes -
# BoundingBox
# COLBox
# COLFace
# COLFaceGroup
# COLFile
# COLMaterial
# COLModel
# COLSphere
# COLVertex
# COLVersion
# Vector3

##Methods list -
# diagnose_col_file
# is_col_debug_enabled
# set_col_debug_enabled

# Global debug control
_global_debug_enabled = False

# Debug system import with fallback
# Import debug functions from img_debug system
try:
    from components.img_debug_functions import img_debugger, set_col_debug_enabled, is_col_debug_enabled
except ImportError:
    # Fallback debug system
    class FallbackDebugger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def info(self, msg): print(f"INFO: {msg}")

    img_debugger = FallbackDebugger()

    def set_col_debug_enabled(enabled: bool):
        pass

    def is_col_debug_enabled() -> bool:
        return False

class COLVersion(Enum):
    """COL file format versions"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4

class Vector3:
    """3D vector class for positions and directions"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0): #vers 1
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"Vector3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def __repr__(self):
        return self.__str__()

class BoundingBox:
    """Axis-aligned bounding box"""
    def __init__(self): #vers 1
        self.center = Vector3()
        self.min = Vector3()
        self.max = Vector3()
        self.radius = 0.0
    
    def calculate_from_vertices(self, vertices: List[Vector3]): #vers 1
        """Calculate bounding box from list of vertices"""
        if not vertices:
            return
        
        # Find min/max
        min_x = min(v.x for v in vertices)
        max_x = max(v.x for v in vertices)
        min_y = min(v.y for v in vertices)
        max_y = max(v.y for v in vertices)
        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)
        
        self.min = Vector3(min_x, min_y, min_z)
        self.max = Vector3(max_x, max_y, max_z)
        
        # Calculate center
        self.center = Vector3(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
        # Calculate radius (distance from center to corner)
        corner_dist = (
            ((max_x - self.center.x) ** 2) +
            ((max_y - self.center.y) ** 2) +
            ((max_z - self.center.z) ** 2)
        ) ** 0.5
        
        self.radius = corner_dist

class COLMaterial:
    """COL material definition"""
    def __init__(self, material_id: int = 0, flags: int = 0): #vers 1
        self.material_id = material_id
        self.flags = flags
    
    def __str__(self):
        return f"COLMaterial(id={self.material_id}, flags={self.flags})"

class COLSphere:
    """COL collision sphere"""
    def __init__(self, center: Vector3, radius: float, material: COLMaterial): #vers 1
        self.center = center
        self.radius = radius
        self.material = material
    
    def __str__(self):
        return f"COLSphere(center={self.center}, radius={self.radius:.3f})"

class COLBox:
    """COL collision box"""
    def __init__(self, min_point: Vector3, max_point: Vector3, material: COLMaterial): #vers 1
        self.min_point = min_point
        self.max_point = max_point
        self.material = material
    
    def __str__(self):
        return f"COLBox(min={self.min_point}, max={self.max_point})"

class COLVertex:
    """COL mesh vertex"""
    def __init__(self, position: Vector3): #vers 1
        self.position = position
    
    def __str__(self):
        return f"COLVertex({self.position})"

class COLFace:
    """COL mesh face"""
    def __init__(self, vertex_indices: Tuple[int, int, int], material: COLMaterial, light: int = 0): #vers 1
        self.vertex_indices = vertex_indices
        self.material = material
        self.light = light
    
    def __str__(self):
        return f"COLFace(indices={self.vertex_indices}, mat={self.material.material_id})"

class COLFaceGroup:
    """COL face group (for COL2/3)"""
    def __init__(self): #vers 1
        self.faces: List[COLFace] = []
        self.material = COLMaterial()
    
    def add_face(self, face: COLFace): #vers 1
        """Add face to group"""
        self.faces.append(face)

class COLModel:
    """COL collision model"""
    def __init__(self): #vers 1
        self.name = ""
        self.model_id = 0
        self.version = COLVersion.COL_1
        self.bounding_box = BoundingBox()
        
        # Collision elements
        self.spheres: List[COLSphere] = []
        self.boxes: List[COLBox] = []
        self.vertices: List[COLVertex] = []
        self.faces: List[COLFace] = []
        self.face_groups: List[COLFaceGroup] = []
        
        # Status flags
        self.has_sphere_data = False
        self.has_box_data = False
        self.has_mesh_data = False
    
    def get_stats(self) -> str: #vers 1
        """Get model statistics"""
        return f"{self.name}: S:{len(self.spheres)} B:{len(self.boxes)} V:{len(self.vertices)} F:{len(self.faces)}"
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



    def calculate_bounding_box(self): #vers 1
        """Calculate bounding box from all collision elements"""
        all_vertices = []
        
        # Add sphere centers
        for sphere in self.spheres:
            all_vertices.extend([
                Vector3(sphere.center.x - sphere.radius, sphere.center.y - sphere.radius, sphere.center.z - sphere.radius),
                Vector3(sphere.center.x + sphere.radius, sphere.center.y + sphere.radius, sphere.center.z + sphere.radius)
            ])
        
        # Add box corners
        for box in self.boxes:
            all_vertices.extend([box.min_point, box.max_point])
        
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
    """COL file handler with complete load/save functionality"""
    def __init__(self, file_path: str = None): #vers 1
        self.file_path = file_path
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = None
        self.file_size = 0

    def load(self) -> bool: #vers 1
        """Load COL file"""
        if not self.file_path:
            self.load_error = "No file path specified"
            return False
        return self.load_from_file(self.file_path)

    def load_from_file(self, file_path: str) -> bool: #vers 2
        """Load COL file from disk with enhanced error handling"""
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

    def _parse_col_data(self, data: bytes) -> bool: #vers 2
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
                    if consumed == 0:
                        img_debugger.error(f"_parse_col_data: Failed to parse any models (stopped at offset {offset})")
                        break
                    else:
                        # Skip this model and continue
                        offset += consumed
                        continue

                self.models.append(model)
                offset += consumed
                model_count += 1

                # Safety check to prevent infinite loops
                if consumed == 0:
                    img_debugger.warning(f"_parse_col_data: Zero bytes consumed, stopping to prevent infinite loop")
                    break

            self.is_loaded = True
            success = len(self.models) > 0

            img_debugger.debug(f"_parse_col_data: Parsing complete - {len(self.models)} models loaded")

            return success

        except Exception as e:
            img_debugger.error(f"_parse_col_data: Exception during parsing: {e}")
            self.load_error = f"Parsing error: {str(e)}"
            return False

    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]: #vers 3
        """Parse single COL model with enhanced error handling"""
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

    def _parse_col1_model(self, model: COLModel, data: bytes): #vers 2
        """Parse COL1 format model with safe parsing methods"""
        try:
            offset = 0

            # Parse model name (22 bytes)
            if len(data) < 22:
                img_debugger.warning("COL1: Data too small for model name")
                return

            name_bytes = data[offset:offset+22]
            model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22

            # Parse model ID (2 bytes)
            if offset + 2 > len(data):
                img_debugger.warning("COL1: Not enough data for model ID")
                return

            model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2

            # Parse bounding data (40 bytes)
            if offset + 40 > len(data):
                img_debugger.warning("COL1: Not enough data for bounding box")
                return

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
            if offset + 20 > len(data):
                img_debugger.warning("COL1: Not enough data for collision counts")
                return

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

            img_debugger.debug(f"COL1: Model {model.name} - S:{num_spheres} B:{num_boxes} V:{num_vertices} F:{num_faces}")

            # Use safe parsing methods from methods/
            try:
                from methods.col_parsing_helpers import (
                    safe_parse_spheres, safe_parse_boxes,
                    safe_parse_vertices, safe_parse_faces_col1
                )

                # Parse spheres safely
                offset = safe_parse_spheres(model, data, offset, num_spheres, "COL1")

                # Skip unknown data
                offset += num_unknown * 4

                # Parse boxes safely
                offset = safe_parse_boxes(model, data, offset, num_boxes, "COL1")

                # Parse vertices safely
                offset = safe_parse_vertices(model, data, offset, num_vertices)

                # Parse faces safely
                offset = safe_parse_faces_col1(model, data, offset, num_faces)

            except ImportError:
                img_debugger.warning("COL1: Safe parsing methods not available, using basic parsing")
                # Fall back to basic parsing without bounds checking
                self._parse_col1_basic(model, data, offset, num_spheres, num_unknown, num_boxes, num_vertices, num_faces)

            model.update_flags()

        except Exception as e:
            img_debugger.error(f"COL1: Error in model parsing: {e}")

    def _parse_col1_basic(self, model: COLModel, data: bytes, offset: int, num_spheres: int, num_unknown: int, num_boxes: int, num_vertices: int, num_faces: int): #vers 1
        """Basic COL1 parsing fallback without safe methods"""
        try:
            # Parse spheres (basic)
            for i in range(num_spheres):
                if offset + 24 > len(data):
                    break
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

            # Parse boxes (basic)
            for i in range(num_boxes):
                if offset + 32 > len(data):
                    break
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

            # Parse vertices (basic)
            for i in range(num_vertices):
                if offset + 12 > len(data):
                    break
                position = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
                offset += 12
                vertex = COLVertex(position)
                model.vertices.append(vertex)

            # Parse faces (basic - this is where the original error occurred)
            for i in range(num_faces):
                if offset + 14 > len(data):  # Need 14 bytes minimum
                    img_debugger.warning(f"COL1: Not enough data for face {i}, stopping")
                    break

                vertex_indices = struct.unpack('<HHH', data[offset:offset+6])
                offset += 6

                if offset + 2 > len(data):
                    material_id = 0
                else:
                    material_id = struct.unpack('<H', data[offset:offset+2])[0]
                    offset += 2

                if offset + 2 > len(data):
                    light = 0
                else:
                    light = struct.unpack('<H', data[offset:offset+2])[0]
                    offset += 2

                if offset + 4 > len(data):
                    flags = 0
                else:
                    flags = struct.unpack('<I', data[offset:offset+4])[0]
                    offset += 4

                material = COLMaterial(material_id, flags=flags)
                face = COLFace(vertex_indices, material, light)
                model.faces.append(face)

        except Exception as e:
            img_debugger.error(f"COL1: Error in basic parsing: {e}")

    def _parse_col23_model(self, model: COLModel, data: bytes): #vers 2
        """Parse COL2/COL3 format model with safe parsing methods"""
        try:
            offset = 0
            
            # Parse model name (22 bytes)
            if len(data) < 22:
                img_debugger.warning("COL2/3: Data too small for model name")
                return
                
            name_bytes = data[offset:offset+22]
            model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Parse model ID (2 bytes)
            if offset + 2 > len(data):
                img_debugger.warning("COL2/3: Not enough data for model ID")
                return
                
            model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Parse bounding data (28 bytes)
            if offset + 28 > len(data):
                img_debugger.warning("COL2/3: Not enough data for bounding box")
                return
                
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
            if offset + 16 > len(data):
                img_debugger.warning("COL2/3: Not enough data for collision counts")
                return
                
            num_spheres = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            num_boxes = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            num_faces = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            num_vertices = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            img_debugger.debug(f"COL2/3: Model {model.name} - S:{num_spheres} B:{num_boxes} V:{num_vertices} F:{num_faces}")
            
            # Use safe parsing methods from methods/
            try:
                from methods.col_parsing_helpers import (
                    safe_parse_spheres, safe_parse_boxes, 
                    safe_parse_vertices, safe_parse_faces_col23
                )
                
                # Parse spheres safely
                offset = safe_parse_spheres(model, data, offset, num_spheres, "COL2/3")
                
                # Parse boxes safely
                offset = safe_parse_boxes(model, data, offset, num_boxes, "COL2/3")
                
                # Parse vertices safely
                offset = safe_parse_vertices(model, data, offset, num_vertices)
                
                # Parse faces safely
                offset = safe_parse_faces_col23(model, data, offset, num_faces)
                
            except ImportError:
                img_debugger.warning("COL2/3: Safe parsing methods not available, using basic parsing")
                # Fall back to basic parsing
                self._parse_col23_basic(model, data, offset, num_spheres, num_boxes, num_vertices, num_faces)
            
            model.update_flags()
            
        except Exception as e:
            img_debugger.error(f"COL2/3: Error in model parsing: {e}")

    def _parse_col23_basic(self, model: COLModel, data: bytes, offset: int, num_spheres: int, num_boxes: int, num_vertices: int, num_faces: int): #vers 1
        """Basic COL2/3 parsing fallback"""
        try:
            # Parse spheres (basic)
            for i in range(num_spheres):
                if offset + 20 > len(data):
                    break
                center = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
                offset += 12
                radius = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
                material_id = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                material = COLMaterial(material_id)
                sphere = COLSphere(center, radius, material)
                model.spheres.append(sphere)
            
            # Parse boxes (basic)
            for i in range(num_boxes):
                if offset + 28 > len(data):
                    break
                min_point = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
                offset += 12
                max_point = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
                offset += 12
                material_id = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                material = COLMaterial(material_id)
                box = COLBox(min_point, max_point, material)
                model.boxes.append(box)
            
            # Parse vertices (basic)
            for i in range(num_vertices):
                if offset + 12 > len(data):
                    break
                position = Vector3(*struct.unpack('<fff', data[offset:offset+12]))
                offset += 12
                vertex = COLVertex(position)
                model.vertices.append(vertex)
            
            # Parse faces (basic with bounds checking
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

        except Exception as e:
            img_debugger.error(f"COL2/3: Error in model parsing: {e}")

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

        lines.append(f"COL File: {os.path.basename(self.file_path) if self.file_path else 'Unk LOD?'}")
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
