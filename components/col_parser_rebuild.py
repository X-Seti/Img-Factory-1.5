#this belongs in components/ col_parser_rebuild.py - Version: 1
# X-Seti - July18 2025 - Img Factory 1.5 - Complete COL Parser Rebuild

"""
Complete COL Parser - Rebuilds the missing collision data parsing functionality
Handles COL1, COL2, COL3, and COL4 formats with proper geometry extraction
"""

import struct
import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

## Methods list -
# parse_col_file_complete
# parse_col_model_data
# parse_col1_collision
# parse_col2_collision
# parse_col3_collision
# read_collision_spheres
# read_collision_boxes
# read_collision_mesh
# extract_model_name
# calculate_model_size

##class COLParserComplete: -
#__init__
# parse_file
# parse_model_at_offset
# read_spheres_data
# read_boxes_data
# read_mesh_data
# get_collision_stats


@dataclass
class COLSphere:
    """COL collision sphere"""
    center: Tuple[float, float, float]
    radius: float
    surface: int = 0
    piece: int = 0

@dataclass 
class COLBox:
    """COL collision box"""
    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]
    surface: int = 0
    piece: int = 0

@dataclass
class COLVertex:
    """COL mesh vertex"""
    x: float
    y: float
    z: float

@dataclass
class COLFace:
    """COL mesh face"""
    a: int  # vertex index
    b: int  # vertex index
    c: int  # vertex index
    surface: int = 0

@dataclass
class COLModel:
    """Complete COL model with parsed data"""
    name: str
    version: str
    spheres: List[COLSphere]
    boxes: List[COLBox]
    vertices: List[COLVertex]
    faces: List[COLFace]
    size_bytes: int = 0
    
    def get_collision_stats(self) -> Dict[str, int]:
        """Get collision statistics"""
        return {
            'sphere_count': len(self.spheres),
            'box_count': len(self.boxes),
            'vertex_count': len(self.vertices),
            'face_count': len(self.faces),
            'surface_count': len(self.spheres) + len(self.boxes),
            'total_elements': len(self.spheres) + len(self.boxes) + len(self.faces)
        }


class COLParserComplete:
    """Complete COL file parser with full collision data extraction"""
    
    def __init__(self, debug=False): #vers 1
        self.debug = debug
        self.models: List[COLModel] = []
        self.file_path = ""
        
    def parse_file(self, file_path: str) -> List[COLModel]: #vers 1
        """Parse complete COL file and return all models with collision data"""
        self.file_path = file_path
        self.models = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if self.debug:
                print(f"Parsing COL file: {os.path.basename(file_path)} ({len(data)} bytes)")
            
            # Check if multi-model archive or single model
            if self._is_multi_model_archive(data):
                return self._parse_multi_model_archive(data)
            else:
                return self._parse_single_model_file(data)
                
        except Exception as e:
            if self.debug:
                print(f"Error parsing COL file: {e}")
            return []
    
    def _is_multi_model_archive(self, data: bytes) -> bool: #vers 1
        """Check if this is a multi-model COL archive"""
        if len(data) < 8:
            return False
        
        # Check for archive header patterns
        header = data[:8]
        return (header[:4] == b'COLL' and 
                struct.unpack('<I', header[4:8])[0] > 100)
    
    def _parse_multi_model_archive(self, data: bytes) -> List[COLModel]: #vers 1
        """Parse multi-model COL archive"""
        if len(data) < 8:
            return []
        
        try:
            # Read header
            offset = 0
            signature = data[offset:offset+4]
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            offset += 8
            
            if self.debug:
                print(f"Multi-model archive: {signature}, size: {file_size}")
            
            # Read model table
            model_count = 0
            while offset < len(data):
                # Try to find model signatures
                remaining = data[offset:]
                col_pos = remaining.find(b'COL')
                
                if col_pos == -1:
                    break
                
                model_offset = offset + col_pos
                model = self.parse_model_at_offset(data, model_offset, model_count)
                
                if model:
                    self.models.append(model)
                    model_count += 1
                    offset = model_offset + max(model.size_bytes, 64)
                else:
                    offset = model_offset + 4
                    
                # Safety limit
                if model_count > 200:
                    break
            
            return self.models
            
        except Exception as e:
            if self.debug:
                print(f"Error parsing multi-model archive: {e}")
            return []
    
    def _parse_single_model_file(self, data: bytes) -> List[COLModel]: #vers 1
        """Parse single model COL file"""
        model = self.parse_model_at_offset(data, 0, 0)
        if model:
            self.models.append(model)
        return self.models
    
    def parse_model_at_offset(self, data: bytes, offset: int, model_index: int) -> Optional[COLModel]: #vers 1
        """Parse COL model at specific offset"""
        try:
            if offset + 32 > len(data):
                return None
            
            # Read version signature
            version_sig = data[offset:offset+4]
            version_map = {
                b'COLL': 'COL1',
                b'COL2': 'COL2', 
                b'COL3': 'COL3',
                b'COL4': 'COL4'
            }
            
            version = version_map.get(version_sig, 'COL1')
            
            if self.debug:
                print(f"Model {model_index}: {version} at offset {offset}")
            
            # Parse based on version
            if version == 'COL1':
                return self._parse_col1_model(data, offset, model_index)
            elif version in ['COL2', 'COL3']:
                return self._parse_col23_model(data, offset, model_index, version)
            elif version == 'COL4':
                return self._parse_col4_model(data, offset, model_index)
            else:
                return self._parse_col1_model(data, offset, model_index)  # fallback
                
        except Exception as e:
            if self.debug:
                print(f"Error parsing model at offset {offset}: {e}")
            return None
    
    def _parse_col1_model(self, data: bytes, offset: int, model_index: int) -> Optional[COLModel]: #vers 1
        """Parse COL version 1 model"""
        try:
            start_offset = offset
            
            # Skip signature if present
            if data[offset:offset+4] == b'COLL':
                offset += 4
            
            # Read model size
            if offset + 4 > len(data):
                return None
            model_size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Read model name (22 bytes)
            if offset + 22 > len(data):
                return None
            name_bytes = data[offset:offset+22]
            model_name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            if not model_name:
                model_name = f"model_{model_index}"
            offset += 22
            
            # Read model ID
            if offset + 4 > len(data):
                return None
            model_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Parse collision data
            spheres, boxes, vertices, faces = self._parse_col1_collision_data(data, offset, model_size)
            
            model = COLModel(
                name=model_name,
                version='COL1',
                spheres=spheres,
                boxes=boxes,
                vertices=vertices,
                faces=faces,
                size_bytes=model_size
            )
            
            if self.debug:
                stats = model.get_collision_stats()
                print(f"COL1 {model_name}: {stats}")
            
            return model
            
        except Exception as e:
            if self.debug:
                print(f"Error parsing COL1 model: {e}")
            return None
    
    def _parse_col23_model(self, data: bytes, offset: int, model_index: int, version: str) -> Optional[COLModel]: #vers 1
        """Parse COL version 2/3 model"""
        try:
            start_offset = offset
            
            # Skip signature
            if data[offset:offset+4] in [b'COL2', b'COL3']:
                offset += 4
            
            # Read model size
            if offset + 4 > len(data):
                return None
            model_size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Skip bounding data (40 bytes)
            if offset + 40 > len(data):
                return None
            offset += 40
            
            # Parse collision data
            spheres, boxes, vertices, faces = self._parse_col23_collision_data(data, offset, model_size)
            
            # Try to extract name from data or use default
            model_name = f"model_{model_index}"
            
            model = COLModel(
                name=model_name,
                version=version,
                spheres=spheres,
                boxes=boxes,
                vertices=vertices,
                faces=faces,
                size_bytes=model_size
            )
            
            if self.debug:
                stats = model.get_collision_stats()
                print(f"{version} {model_name}: {stats}")
            
            return model
            
        except Exception as e:
            if self.debug:
                print(f"Error parsing {version} model: {e}")
            return None
    
    def _parse_col4_model(self, data: bytes, offset: int, model_index: int) -> Optional[COLModel]: #vers 1
        """Parse COL version 4 model"""
        # COL4 is similar to COL2/3 but with extended features
        return self._parse_col23_model(data, offset, model_index, 'COL4')
    
    def _parse_col1_collision_data(self, data: bytes, offset: int, model_size: int) -> Tuple[List, List, List, List]: #vers 1
        """Parse COL1 collision data using working logic from old files"""
        spheres = []
        boxes = []
        vertices = []
        faces = []
        
        try:
            # Skip unknown data section if present (from old working code)
            if offset + 4 <= len(data):
                unknown_count = struct.unpack('<I', data[offset:offset+4])[0]
                if 0 <= unknown_count <= 100:  # Sanity check
                    offset += 4 + (unknown_count * 8)  # Skip unknown data
                    if self.debug:
                        print(f"COL1: Skipped {unknown_count} unknown entries")
            
            # Read spheres (from old working logic)
            if offset + 4 <= len(data):
                sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                if 0 <= sphere_count <= 1000:  # Sanity check
                    spheres = self.read_spheres_data(data, offset, sphere_count)
                    offset += sphere_count * 20
                    if self.debug:
                        print(f"COL1: Read {len(spheres)} spheres")
            
            # Read boxes (from old working logic)
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                if 0 <= box_count <= 1000:  # Sanity check
                    boxes = self.read_boxes_data(data, offset, box_count)
                    offset += box_count * 28
                    if self.debug:
                        print(f"COL1: Read {len(boxes)} boxes")
            
            # Read vertices (from old working logic)
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                if 0 <= vertex_count <= 10000:  # Sanity check
                    vertices = self.read_vertices_data(data, offset, vertex_count)
                    offset += vertex_count * 12  # COL1 uses 12 bytes per vertex
                    if self.debug:
                        print(f"COL1: Read {len(vertices)} vertices")
            
            # Read faces (from old working logic)
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                
                if 0 <= face_count <= 10000:  # Sanity check
                    faces = self.read_faces_data(data, offset + 4, face_count)
                    if self.debug:
                        print(f"COL1: Read {len(faces)} faces")
        
        except Exception as e:
            if self.debug:
                print(f"Error parsing COL1 collision data: {e}")
        
        return spheres, boxes, vertices, faces
    
    def _parse_col23_collision_data(self, data: bytes, offset: int, model_size: int) -> Tuple[List, List, List, List]: #vers 1
        """Parse COL2/3 collision data using working logic from old files"""
        spheres = []
        boxes = []
        vertices = []
        faces = []
        
        try:
            # COL2/3 structure: counts first, then data (from old working code)
            if offset + 16 <= len(data):
                sphere_count, box_count, vertex_count, face_count = struct.unpack('<IIII', 
                    data[offset:offset+16])
                offset += 16
                
                if self.debug:
                    print(f"COL2/3 counts: {sphere_count} spheres, {box_count} boxes, {vertex_count} vertices, {face_count} faces")
                
                # Validate counts (from old working sanity checks)
                if (0 <= sphere_count <= 1000 and 0 <= box_count <= 1000 and 
                    0 <= vertex_count <= 10000 and 0 <= face_count <= 10000):
                    
                    # Read spheres (20 bytes each)
                    if sphere_count > 0:
                        spheres = self.read_spheres_data(data, offset, sphere_count)
                        offset += sphere_count * 20
                    
                    # Read boxes (28 bytes each - from old working code)
                    if box_count > 0:
                        boxes = self.read_boxes_data(data, offset, box_count)
                        offset += box_count * 28
                    
                    # Read vertices (6 bytes each for COL2/3 - from old working code)
                    if vertex_count > 0:
                        vertices = self.read_vertices_data(data, offset, vertex_count)
                        offset += vertex_count * 6  # COL2/3 uses 6 bytes per vertex
                    
                    # Read faces (8 bytes each for COL2/3 - from old working code)
                    if face_count > 0:
                        faces = self.read_faces_data(data, offset, face_count)
                        offset += face_count * 8  # COL2/3 uses 8 bytes per face
                    
                    if self.debug:
                        print(f"COL2/3 parsed: {len(spheres)} spheres, {len(boxes)} boxes, {len(vertices)} vertices, {len(faces)} faces")
                else:
                    if self.debug:
                        print(f"COL2/3 counts failed sanity check: {sphere_count}, {box_count}, {vertex_count}, {face_count}")
            
        except Exception as e:
            if self.debug:
                print(f"Error parsing COL2/3 collision data: {e}")
        
        return spheres, boxes, vertices, faces
    
    def read_spheres_data(self, data: bytes, offset: int, count: int) -> List[COLSphere]: #vers 1
        """Read collision spheres from binary data"""
        spheres = []
        try:
            for i in range(count):
                sphere_offset = offset + (i * 20)
                if sphere_offset + 20 <= len(data):
                    # Read sphere data: center (12 bytes) + radius (4 bytes) + surface (4 bytes)
                    sphere_data = struct.unpack('<ffffi', data[sphere_offset:sphere_offset+20])
                    sphere = COLSphere(
                        center=(sphere_data[0], sphere_data[1], sphere_data[2]),
                        radius=sphere_data[3],
                        surface=sphere_data[4]
                    )
                    spheres.append(sphere)
        except Exception as e:
            if self.debug:
                print(f"Error reading spheres: {e}")
        return spheres
    
    def read_boxes_data(self, data: bytes, offset: int, count: int) -> List[COLBox]: #vers 1
        """Read collision boxes from binary data"""
        boxes = []
        try:
            for i in range(count):
                box_offset = offset + (i * 32)
                if box_offset + 32 <= len(data):
                    # Read box data: min (12 bytes) + max (12 bytes) + surface (4 bytes) + piece (4 bytes)
                    box_data = struct.unpack('<ffffffii', data[box_offset:box_offset+32])
                    box = COLBox(
                        min_point=(box_data[0], box_data[1], box_data[2]),
                        max_point=(box_data[3], box_data[4], box_data[5]),
                        surface=box_data[6],
                        piece=box_data[7]
                    )
                    boxes.append(box)
        except Exception as e:
            if self.debug:
                print(f"Error reading boxes: {e}")
        return boxes
    
    def read_vertices_data(self, data: bytes, offset: int, count: int) -> List[COLVertex]: #vers 1
        """Read mesh vertices from binary data"""
        vertices = []
        try:
            for i in range(count):
                vertex_offset = offset + (i * 12)
                if vertex_offset + 12 <= len(data):
                    # Read vertex: x, y, z (12 bytes)
                    x, y, z = struct.unpack('<fff', data[vertex_offset:vertex_offset+12])
                    vertex = COLVertex(x=x, y=y, z=z)
                    vertices.append(vertex)
        except Exception as e:
            if self.debug:
                print(f"Error reading vertices: {e}")
        return vertices
    
    def read_faces_data(self, data: bytes, offset: int, count: int) -> List[COLFace]: #vers 1
        """Read mesh faces from binary data"""
        faces = []
        try:
            for i in range(count):
                face_offset = offset + (i * 16)
                if face_offset + 16 <= len(data):
                    # Read face: vertex indices (12 bytes) + surface (4 bytes)
                    a, b, c, surface = struct.unpack('<IIII', data[face_offset:face_offset+16])
                    face = COLFace(a=a, b=b, c=c, surface=surface)
                    faces.append(face)
        except Exception as e:
            if self.debug:
                print(f"Error reading faces: {e}")
        return faces


# Convenience functions for integration
def parse_col_file_complete(file_path: str, debug: bool = False) -> List[COLModel]: #vers 1
    """Parse complete COL file and return models with collision data"""
    parser = COLParserComplete(debug=debug)
    return parser.parse_file(file_path)


def get_col_model_collision_stats(file_path: str, model_index: int = 0) -> Dict[str, Any]: #vers 1
    """Get collision statistics for specific model"""
    try:
        models = parse_col_file_complete(file_path, debug=False)
        if model_index < len(models):
            return models[model_index].get_collision_stats()
        return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}
    except Exception:
        return {'sphere_count': 0, 'box_count': 0, 'vertex_count': 0, 'face_count': 0}


# Export main classes and functions
__all__ = [
    'COLParserComplete',
    'COLModel', 
    'COLSphere',
    'COLBox',
    'COLVertex', 
    'COLFace',
    'parse_col_file_complete',
    'get_col_model_collision_stats'
]