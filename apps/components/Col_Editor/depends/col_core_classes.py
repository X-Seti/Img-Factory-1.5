#this belongs in apps/components/Col_Editor/depends/col_core_classes.py - Version: 3
# X-Seti - December13 2025 - IMG Factory 1.5 - COL Core Classes CLEAN

"""
COL Core Classes - Clean version with integrated fixes
- Garbage face count detection/correction
- No fallback/basic method duplicates
- Clear parsing flow
- Proper error handling
"""

import struct
import os
from enum import Enum
from typing import List, Tuple, Optional
from apps.debug.debug_functions import img_debugger

##Methods list -
# calculate_bounding_box
# get_info
# get_stats
# load_from_file
# update_flags
# _build_col1_model
# _build_col23_model
# _calculate_face_count
# _parse_col1_model
# _parse_col23_model
# _parse_col_data
# _parse_col_model

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

# ===== DATA STRUCTURES =====

class Vector3:
    """3D vector"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0): #vers 1
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


class BoundingBox:
    """Bounding box"""
    def __init__(self): #vers 1
        self.min = Vector3(-1.0, -1.0, -1.0)
        self.max = Vector3(1.0, 1.0, 1.0)
        self.center = Vector3(0.0, 0.0, 0.0)
        self.radius = 1.0


class COLVersion(Enum):
    """COL format versions"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4


class COLMaterial:
    """COL material/surface"""
    def __init__(self, material_id: int = 0, flags: int = 0): #vers 1
        self.material_id = material_id
        self.flags = flags


class COLSphere:
    """COL collision sphere"""
    def __init__(self, center: Vector3, radius: float, material: COLMaterial): #vers 1
        self.center = center
        self.radius = radius
        self.material = material


class COLBox:
    """COL collision box"""
    def __init__(self, min_point: Vector3, max_point: Vector3, material: COLMaterial): #vers 1
        self.min_point = min_point
        self.max_point = max_point
        self.material = material


class COLVertex:
    """COL mesh vertex"""
    def __init__(self, position: Vector3): #vers 1
        self.position = position


class COLFace:
    """COL mesh face (triangle)"""
    def __init__(self, vertex_indices: Tuple[int, int, int], material: COLMaterial, light: int): #vers 1
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
        
        # Debug flag
        self.calculated_face_count = False
    
    def get_stats(self) -> str: #vers 1
        """Get model statistics"""
        return f"{self.name}: S:{len(self.spheres)} B:{len(self.boxes)} V:{len(self.vertices)} F:{len(self.faces)}"
    
    def update_flags(self): #vers 1
        """Update status flags"""
        self.has_sphere_data = len(self.spheres) > 0
        self.has_box_data = len(self.boxes) > 0
        self.has_mesh_data = len(self.vertices) > 0 and len(self.faces) > 0
    
    def calculate_bounding_box(self): #vers 1
        """Calculate bounding box from collision elements"""
        all_vertices = []
        
        # Add sphere centers
        for sphere in self.spheres:
            all_vertices.extend([
                Vector3(sphere.center.x - sphere.radius, sphere.center.y - sphere.radius, sphere.center.z - sphere.radius),
                Vector3(sphere.center.x + sphere.radius, sphere.center.y + sphere.radius, sphere.center.z + sphere.radius)
            ])
        
        # Add box vertices
        for box in self.boxes:
            all_vertices.extend([box.min_point, box.max_point])
        
        # Add mesh vertices
        for vertex in self.vertices:
            all_vertices.append(vertex.position)
        
        if not all_vertices:
            return
        
        # Calculate bounds
        min_x = min(v.x for v in all_vertices)
        min_y = min(v.y for v in all_vertices)
        min_z = min(v.z for v in all_vertices)
        max_x = max(v.x for v in all_vertices)
        max_y = max(v.y for v in all_vertices)
        max_z = max(v.z for v in all_vertices)
        
        self.bounding_box.min = Vector3(min_x, min_y, min_z)
        self.bounding_box.max = Vector3(max_x, max_y, max_z)
        self.bounding_box.center = Vector3(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
        # Calculate radius
        dx = max_x - min_x
        dy = max_y - min_y
        dz = max_z - min_z
        self.bounding_box.radius = (dx*dx + dy*dy + dz*dz) ** 0.5 / 2


class COLFile:
    """COL file container"""
    
    def __init__(self): #vers 1
        self.file_path = ""
        self.models: List[COLModel] = []
        self.is_loaded = False
        self.load_error = ""
    
    def load_from_file(self, file_path: str) -> bool: #vers 1
        """Load COL file from disk"""
        try:
            self.file_path = file_path
            self.models = []
            self.is_loaded = False
            self.load_error = ""
            
            if not os.path.exists(file_path):
                self.load_error = f"File not found: {file_path}"
                return False
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if len(data) < 8:
                self.load_error = "File too small"
                return False
            
            return self._parse_col_data(data)
            
        except Exception as e:
            self.load_error = f"Load error: {str(e)}"
            img_debugger.error(f"COL load error: {e}")
            return False
    
    def _parse_col_data(self, data: bytes) -> bool: #vers 1
        """Parse COL file data"""
        try:
            offset = 0
            model_count = 0
            
            while offset < len(data):
                model, consumed = self._parse_col_model(data, offset)
                
                if model is None:
                    break
                
                self.models.append(model)
                offset += consumed
                model_count += 1
                
                # Safety check
                if consumed == 0:
                    img_debugger.warning("Zero bytes consumed, stopping")
                    break
            
            self.is_loaded = len(self.models) > 0
            img_debugger.success(f"Loaded {len(self.models)} COL models")
            
            return self.is_loaded
            
        except Exception as e:
            self.load_error = f"Parse error: {str(e)}"
            img_debugger.error(f"COL parse error: {e}")
            return False
    
    def _parse_col_model(self, data: bytes, offset: int) -> Tuple[Optional[COLModel], int]: #vers 1
        """Parse single COL model"""
        try:
            if offset + 8 > len(data):
                return None, 0
            
            # Read signature
            fourcc = data[offset:offset+4]
            
            if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return None, 0
            
            # Read file size
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = file_size + 8
            
            if offset + total_size > len(data):
                img_debugger.warning(f"Model extends beyond data")
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
            
            # Extract model data
            model_data = data[offset + 8:offset + total_size]
            
            # Parse based on version
            if model.version == COLVersion.COL_1:
                self._parse_col1_model(model, model_data)
            else:
                self._parse_col23_model(model, model_data)
            
            return model, total_size
            
        except Exception as e:
            img_debugger.error(f"Model parse error: {e}")
            return None, 0
    
    def _parse_col1_model(self, model: COLModel, data: bytes): #vers 2
        """Parse COL1 model with garbage face count fix"""
        try:
            offset = 0
            
            # Parse model name (22 bytes)
            if len(data) < 22:
                return
            
            name_bytes = data[offset:offset+22]
            model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Parse model ID (2 bytes)
            model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Parse bounding box (40 bytes)
            model.bounding_box.radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            
            cx, cy, cz = struct.unpack('<fff', data[offset:offset+12])
            model.bounding_box.center = Vector3(cx, cy, cz)
            offset += 12
            
            min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
            model.bounding_box.min = Vector3(min_x, min_y, min_z)
            offset += 12
            
            max_x, max_y, max_z = struct.unpack('<fff', data[offset:offset+12])
            model.bounding_box.max = Vector3(max_x, max_y, max_z)
            offset += 12
            
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
            
            # CRITICAL FIX: Check for garbage face count
            num_faces = self._calculate_face_count(data, offset, num_spheres, num_unknown, 
                                                   num_boxes, num_vertices, num_faces, is_col1=True)
            
            # Import safe parsing helpers
            try:
                from apps.methods.col_parsing_helpers import (
                    safe_parse_spheres, safe_parse_boxes,
                    safe_parse_vertices, safe_parse_faces_col1
                )
                
                # Parse spheres
                offset = safe_parse_spheres(model, data, offset, num_spheres, "COL1")
                
                # Skip unknown data
                offset += num_unknown * 4
                
                # Parse boxes
                offset = safe_parse_boxes(model, data, offset, num_boxes, "COL1")
                
                # Parse vertices
                offset = safe_parse_vertices(model, data, offset, num_vertices)
                
                # Parse faces (with corrected count)
                offset = safe_parse_faces_col1(model, data, offset, num_faces)
                
            except ImportError:
                img_debugger.error("COL1: Safe parsing helpers not available")
                return
            
            model.update_flags()
            
        except Exception as e:
            img_debugger.error(f"COL1 parse error: {e}")
    
    def _parse_col23_model(self, model: COLModel, data: bytes): #vers 2
        """Parse COL2/COL3 model"""
        try:
            offset = 0
            
            # Parse model name (22 bytes)
            if len(data) < 22:
                return
            
            name_bytes = data[offset:offset+22]
            model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Parse model ID (2 bytes)
            model.model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Parse bounding box (28 bytes for COL2/3)
            min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
            model.bounding_box.min = Vector3(min_x, min_y, min_z)
            offset += 12
            
            max_x, max_y, max_z = struct.unpack('<fff', data[offset:offset+12])
            model.bounding_box.max = Vector3(max_x, max_y, max_z)
            offset += 12
            
            cx, cy, cz = struct.unpack('<fff', data[offset:offset+12])
            model.bounding_box.center = Vector3(cx, cy, cz)
            offset += 12
            
            model.bounding_box.radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            
            # Parse counts (16 bytes) - COL2/3 order: spheres, boxes, faces, vertices
            num_spheres = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            num_boxes = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            num_faces = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            num_vertices = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Import safe parsing helpers
            try:
                from apps.methods.col_parsing_helpers import (
                    safe_parse_spheres, safe_parse_boxes,
                    safe_parse_vertices, safe_parse_faces_col23
                )
                
                # Parse spheres
                offset = safe_parse_spheres(model, data, offset, num_spheres, "COL2/3")
                
                # Parse boxes
                offset = safe_parse_boxes(model, data, offset, num_boxes, "COL2/3")
                
                # Parse vertices
                offset = safe_parse_vertices(model, data, offset, num_vertices)
                
                # Parse faces
                offset = safe_parse_faces_col23(model, data, offset, num_faces)
                
            except ImportError:
                img_debugger.error("COL2/3: Safe parsing helpers not available")
                return
            
            model.update_flags()
            
        except Exception as e:
            img_debugger.error(f"COL2/3 parse error: {e}")
    
    def _calculate_face_count(self, data: bytes, offset: int, num_spheres: int, 
                             num_unknown: int, num_boxes: int, num_vertices: int, 
                             num_faces: int, is_col1: bool = True) -> int: #vers 1
        """
        Calculate actual face count from file size
        Fixes garbage face count issues (like 3.2 billion faces)
        """
        try:
            # Calculate bytes used by known data
            SPHERE_SIZE = 24  # center(12) + radius(4) + material(4) + flags(4)
            BOX_SIZE = 32     # min(12) + max(12) + material(4) + flags(4)
            VERTEX_SIZE = 12  # position(12)
            FACE_SIZE_COL1 = 16  # indices(6) + mat(2) + light(2) + flags(4) + padding(2)
            FACE_SIZE_COL23 = 12 # indices(6) + mat(2) + light(2) + padding(2)
            
            data_used = (num_spheres * SPHERE_SIZE) + \
                       (num_unknown * 4) + \
                       (num_boxes * BOX_SIZE) + \
                       (num_vertices * VERTEX_SIZE)
            
            # Calculate remaining bytes
            offset_after_verts = offset + data_used
            remaining_bytes = len(data) - offset_after_verts
            
            # Calculate face count from remaining bytes
            face_size = FACE_SIZE_COL1 if is_col1 else FACE_SIZE_COL23
            calculated_faces = remaining_bytes // face_size
            
            # Sanity check: Is stored face count garbage?
            MAX_REASONABLE_FACES = 1000000  # 1 million faces
            
            if num_faces > MAX_REASONABLE_FACES or num_faces > calculated_faces * 10:
                img_debugger.warning(f"⚠️  Garbage face count detected: {num_faces}")
                img_debugger.warning(f"    Correcting to calculated value: {calculated_faces}")
                img_debugger.warning(f"    (Remaining bytes: {remaining_bytes} / Face size: {face_size})")
                return calculated_faces
            
            # Face count seems reasonable
            return num_faces
            
        except Exception as e:
            img_debugger.error(f"Face count calculation error: {e}")
            return num_faces  # Return original if calculation fails
    
    def get_info(self) -> str: #vers 1
        """Get file information"""
        lines = []
        lines.append(f"COL File: {os.path.basename(self.file_path) if self.file_path else 'Unknown'}")
        lines.append(f"Models: {len(self.models)}")
        
        for i, model in enumerate(self.models):
            lines.append(f"\nModel {i}: {model.get_stats()}")
        
        return "\n".join(lines)
    
    def _build_col1_model(self, model: COLModel) -> bytes: #vers 1
        """Build COL1 format binary data"""
        data = b''
        model_content = b''
        
        # Model name (22 bytes)
        name_bytes = model.name.encode('ascii')[:21].ljust(22, b'\x00')
        model_content += name_bytes
        
        # Model ID (2 bytes)
        model_content += struct.pack('<H', model.model_id)
        
        # Bounding box (40 bytes)
        model_content += struct.pack('<f', model.bounding_box.radius)
        model_content += struct.pack('<fff', model.bounding_box.center.x, model.bounding_box.center.y, model.bounding_box.center.z)
        model_content += struct.pack('<fff', model.bounding_box.min.x, model.bounding_box.min.y, model.bounding_box.min.z)
        model_content += struct.pack('<fff', model.bounding_box.max.x, model.bounding_box.max.y, model.bounding_box.max.z)
        
        # Counts (20 bytes)
        model_content += struct.pack('<I', len(model.spheres))
        model_content += struct.pack('<I', 0)  # unknown
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
        data += b'COLL'
        data += struct.pack('<I', len(model_content))
        data += model_content
        
        return data
    
    def _build_col23_model(self, model: COLModel) -> bytes: #vers 1
        """Build COL2/COL3 format binary data"""
        data = b''
        model_content = b''
        
        # Model name (22 bytes)
        name_bytes = model.name.encode('ascii')[:21].ljust(22, b'\x00')
        model_content += name_bytes
        
        # Model ID (2 bytes)
        model_content += struct.pack('<H', model.model_id)
        
        # Bounding box (28 bytes)
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
        
        # Build header
        if model.version == COLVersion.COL_2:
            data += b'COL\x02'
        elif model.version == COLVersion.COL_3:
            data += b'COL\x03'
        else:
            data += b'COL\x04'
        
        data += struct.pack('<I', len(model_content))
        data += model_content
        
        return data


# Export classes
__all__ = [
    'Vector3', 'BoundingBox', 'COLVersion', 'COLMaterial',
    'COLSphere', 'COLBox', 'COLVertex', 'COLFace', 'COLFaceGroup',
    'COLModel', 'COLFile'
]
