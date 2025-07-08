#this belongs in components/ col_parser.py - Version: 2
# X-Seti - July08 2025 - Complete COL Format Parser for IMG Factory 1.5

import struct
import os
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

@dataclass
class ParsedSphere:
    """Parsed collision sphere data"""
    center_x: float
    center_y: float 
    center_z: float
    radius: float
    material: int
    flags: int = 0

@dataclass  
class ParsedBox:
    """Parsed collision box data"""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    material: int
    flags: int = 0

@dataclass
class ParsedVertex:
    """Parsed collision vertex"""
    x: float
    y: float
    z: float

@dataclass
class ParsedFace:
    """Parsed collision face (triangle)"""
    vertex_a: int
    vertex_b: int
    vertex_c: int
    material: int
    light: int = 0
    flags: int = 0

@dataclass
class ParsedFaceGroup:
    """Face group for COL2/3"""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    start_face: int
    end_face: int

@dataclass
class ParsedModel:
    """Complete parsed COL model data"""
    name: str
    model_id: int
    spheres: List[ParsedSphere]
    boxes: List[ParsedBox] 
    vertices: List[ParsedVertex]
    faces: List[ParsedFace]
    face_groups: List[ParsedFaceGroup]
    shadow_vertices: List[ParsedVertex]
    shadow_faces: List[ParsedFace]
    version: int = 1
    flags: int = 0
    bounding_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounding_radius: float = 0.0
    bounding_min: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounding_max: Tuple[float, float, float] = (0.0, 0.0, 0.0)

class COLParser:
    """Complete COL format parser based on GTAMods wiki specification"""
    
    def __init__(self):
        self.debug = True
        
    def parse_col_file(self, file_path: str) -> List[ParsedModel]:
        """Parse complete COL file and return all models with full collision data"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if self.debug:
                print(f"🔍 Parsing COL file: {len(data)} bytes")
            
            models = []
            offset = 0
            
            while offset < len(data):
                model, model_size = self._parse_model(data, offset)
                if model is None or model_size == 0:
                    break
                
                models.append(model)
                offset += model_size
                
                if self.debug:
                    print(f"✅ Parsed model '{model.name}' - S:{len(model.spheres)} B:{len(model.boxes)} V:{len(model.vertices)} F:{len(model.faces)}")
            
            print(f"🎯 COL parsing complete: {len(models)} models")
            return models
            
        except Exception as e:
            print(f"❌ Error parsing COL file: {e}")
            return []
    
    def _parse_model(self, data: bytes, offset: int) -> Tuple[Optional[ParsedModel], int]:
        """Parse a single COL model from data"""
        try:
            if offset + 8 > len(data):
                return None, 0
            
            # Read header
            signature = data[offset:offset+4]
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = file_size + 8
            
            if offset + total_size > len(data):
                print(f"❌ Model extends beyond file: need {offset + total_size}, have {len(data)}")
                return None, 0
            
            # Determine version
            version = self._get_version_from_signature(signature)
            
            if self.debug:
                print(f"🔍 Model signature: {signature}, version: {version}, size: {total_size}")
            
            # Parse based on version
            model_data = data[offset + 8:offset + total_size]
            
            if version == 1:
                model = self._parse_col1_model(model_data)
            else:
                model = self._parse_col23_model(model_data, version)
            
            if model:
                model.version = version
                
            return model, total_size
            
        except Exception as e:
            print(f"❌ Error parsing model at offset {offset}: {e}")
            return None, 0
    
    def _get_version_from_signature(self, signature: bytes) -> int:
        """Determine COL version from signature"""
        if signature == b'COLL':
            return 1
        elif signature == b'COL\x02':
            return 2
        elif signature == b'COL\x03':
            return 3
        elif signature == b'COL\x04':
            return 4
        else:
            return 1  # Default fallback
    
    def _parse_col1_model(self, data: bytes) -> Optional[ParsedModel]:
        """Parse COL version 1 model (GTA III/VC format)"""
        try:
            offset = 0
            
            # Read name (22 bytes)
            if len(data) < 22:
                raise Exception("COL1 data too short for name")
            
            name_bytes = data[offset:offset+22]
            name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Read model ID (2 bytes)
            model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Read bounding data (40 bytes for COL1 TBounds)
            if offset + 40 > len(data):
                raise Exception("COL1 data too short for bounding data")
            
            # COL1 TBounds: radius + center + min + max
            radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            center_x, center_y, center_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            max_x, max_y, max_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            
            if self.debug:
                print(f"🔍 COL1 Model: '{name}' ID:{model_id} Radius:{radius}")
            
            # Read collision data counts
            sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Parse spheres
            spheres = []
            for i in range(sphere_count):
                if offset + 20 > len(data):
                    break
                # COL1 sphere: radius + center + surface
                s_radius = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
                s_center_x, s_center_y, s_center_z = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                s_material = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 4  # Skip remaining surface data
                
                sphere = ParsedSphere(s_center_x, s_center_y, s_center_z, s_radius, s_material)
                spheres.append(sphere)
            
            # Skip unknown data section (4 bytes count + data)
            if offset + 4 <= len(data):
                unknown_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (unknown_count * 8)  # Skip unknown data
            
            # Read box count and boxes
            boxes = []
            if offset + 4 <= len(data):
                box_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                for i in range(box_count):
                    if offset + 28 > len(data):
                        break
                    # COL1 box: min + max + surface
                    b_min_x, b_min_y, b_min_z = struct.unpack('<fff', data[offset:offset+12])
                    offset += 12
                    b_max_x, b_max_y, b_max_z = struct.unpack('<fff', data[offset:offset+12])
                    offset += 12
                    b_material = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 4  # Skip remaining surface data
                    
                    box = ParsedBox(b_min_x, b_min_y, b_min_z, b_max_x, b_max_y, b_max_z, b_material)
                    boxes.append(box)
            
            # Read vertex count and vertices
            vertices = []
            if offset + 4 <= len(data):
                vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                for i in range(vertex_count):
                    if offset + 12 > len(data):
                        break
                    v_x, v_y, v_z = struct.unpack('<fff', data[offset:offset+12])
                    offset += 12
                    
                    vertex = ParsedVertex(v_x, v_y, v_z)
                    vertices.append(vertex)
            
            # Read face count and faces
            faces = []
            if offset + 4 <= len(data):
                face_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                for i in range(face_count):
                    if offset + 16 > len(data):
                        break
                    # COL1 face: a, b, c + surface
                    f_a, f_b, f_c = struct.unpack('<III', data[offset:offset+12])
                    offset += 12
                    f_material = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 4  # Skip remaining surface data
                    
                    face = ParsedFace(f_a, f_b, f_c, f_material)
                    faces.append(face)
            
            model = ParsedModel(
                name=name,
                model_id=model_id,
                spheres=spheres,
                boxes=boxes,
                vertices=vertices,
                faces=faces,
                face_groups=[],
                shadow_vertices=[],
                shadow_faces=[],
                version=1,
                flags=0,
                bounding_center=(center_x, center_y, center_z),
                bounding_radius=radius,
                bounding_min=(min_x, min_y, min_z),
                bounding_max=(max_x, max_y, max_z)
            )
            
            return model
            
        except Exception as e:
            print(f"❌ Error parsing COL1 model: {e}")
            return None
    
    def _parse_col23_model(self, data: bytes, version: int) -> Optional[ParsedModel]:
        """Parse COL version 2/3 model (GTA SA format)"""
        try:
            offset = 0
            
            # Read name (22 bytes)
            name_bytes = data[offset:offset+22]
            name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Read model ID (2 bytes)
            model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Read bounding data (COL2/3 TBounds: min + max + center + radius)
            min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            max_x, max_y, max_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            center_x, center_y, center_z = struct.unpack('<fff', data[offset:offset+12])
            offset += 12
            radius = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            
            # Read counts and offsets
            sphere_count = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            box_count = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            face_count = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            line_count = struct.unpack('<B', data[offset:offset+1])[0]
            offset += 1
            padding = struct.unpack('<B', data[offset:offset+1])[0]
            offset += 1
            
            flags = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Read all offsets
            sphere_offset = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            box_offset = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            line_offset = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            vertex_offset = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            face_offset = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            plane_offset = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Version 3 specific offsets
            shadow_face_count = 0
            shadow_vertex_offset = 0
            shadow_face_offset = 0
            if version >= 3:
                shadow_face_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                shadow_vertex_offset = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                shadow_face_offset = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
            
            if self.debug:
                print(f"🔍 COL{version} Model: '{name}' S:{sphere_count} B:{box_count} F:{face_count}")
            
            # Parse spheres
            spheres = []
            if sphere_count > 0 and sphere_offset > 0:
                data_offset = sphere_offset
                for i in range(sphere_count):
                    if data_offset + 16 > len(data):
                        break
                    # COL2/3 sphere: center + radius + surface
                    s_center_x, s_center_y, s_center_z = struct.unpack('<fff', data[data_offset:data_offset+12])
                    data_offset += 12
                    s_radius = struct.unpack('<f', data[data_offset:data_offset+4])[0]
                    data_offset += 4
                    s_material = struct.unpack('<B', data[data_offset:data_offset+1])[0]
                    data_offset += 4  # Skip remaining surface data
                    
                    sphere = ParsedSphere(s_center_x, s_center_y, s_center_z, s_radius, s_material)
                    spheres.append(sphere)
            
            # Parse boxes
            boxes = []
            if box_count > 0 and box_offset > 0:
                data_offset = box_offset
                for i in range(box_count):
                    if data_offset + 28 > len(data):
                        break
                    # COL2/3 box: min + max + surface
                    b_min_x, b_min_y, b_min_z = struct.unpack('<fff', data[data_offset:data_offset+12])
                    data_offset += 12
                    b_max_x, b_max_y, b_max_z = struct.unpack('<fff', data[data_offset:data_offset+12])
                    data_offset += 12
                    b_material = struct.unpack('<B', data[data_offset:data_offset+1])[0]
                    data_offset += 4  # Skip remaining surface data
                    
                    box = ParsedBox(b_min_x, b_min_y, b_min_z, b_max_x, b_max_y, b_max_z, b_material)
                    boxes.append(box)
            
            # Parse vertices (compressed format)
            vertices = []
            if vertex_offset > 0:
                # Calculate vertex count from face data
                vertex_count = 0
                if face_count > 0 and face_offset > 0:
                    # Scan faces to find max vertex index
                    temp_offset = face_offset
                    for i in range(face_count):
                        if temp_offset + 4 > len(data):
                            break
                        f_a, f_b, f_c = struct.unpack('<HHH', data[temp_offset:temp_offset+6])
                        vertex_count = max(vertex_count, f_a + 1, f_b + 1, f_c + 1)
                        temp_offset += 8  # Face is 8 bytes in COL2/3
                
                # Parse compressed vertices
                data_offset = vertex_offset
                for i in range(vertex_count):
                    if data_offset + 6 > len(data):
                        break
                    # COL2/3 vertex: compressed int16[3] / 128.0
                    v_x_raw, v_y_raw, v_z_raw = struct.unpack('<hhh', data[data_offset:data_offset+6])
                    data_offset += 6
                    
                    v_x = v_x_raw / 128.0
                    v_y = v_y_raw / 128.0
                    v_z = v_z_raw / 128.0
                    
                    vertex = ParsedVertex(v_x, v_y, v_z)
                    vertices.append(vertex)
            
            # Parse faces
            faces = []
            if face_count > 0 and face_offset > 0:
                data_offset = face_offset
                for i in range(face_count):
                    if data_offset + 8 > len(data):
                        break
                    # COL2/3 face: a, b, c (uint16) + material + light
                    f_a, f_b, f_c = struct.unpack('<HHH', data[data_offset:data_offset+6])
                    data_offset += 6
                    f_material = struct.unpack('<B', data[data_offset:data_offset+1])[0]
                    data_offset += 1
                    f_light = struct.unpack('<B', data[data_offset:data_offset+1])[0]
                    data_offset += 1
                    
                    face = ParsedFace(f_a, f_b, f_c, f_material, f_light)
                    faces.append(face)
            
            # Parse face groups (if present)
            face_groups = []
            if flags & 8 and face_count > 0:  # Has face groups flag
                # Face groups are located before faces
                group_offset = face_offset - 4
                if group_offset >= 0:
                    group_count = struct.unpack('<I', data[group_offset:group_offset+4])[0]
                    group_offset -= group_count * 28
                    
                    for i in range(group_count):
                        if group_offset + 28 > len(data):
                            break
                        g_min_x, g_min_y, g_min_z = struct.unpack('<fff', data[group_offset:group_offset+12])
                        group_offset += 12
                        g_max_x, g_max_y, g_max_z = struct.unpack('<fff', data[group_offset:group_offset+12])
                        group_offset += 12
                        g_start, g_end = struct.unpack('<HH', data[group_offset:group_offset+4])
                        group_offset += 4
                        
                        group = ParsedFaceGroup(g_min_x, g_min_y, g_min_z, g_max_x, g_max_y, g_max_z, g_start, g_end)
                        face_groups.append(group)
            
            # Parse shadow mesh (COL3 only)
            shadow_vertices = []
            shadow_faces = []
            if version >= 3 and shadow_face_count > 0:
                # Parse shadow vertices (same format as regular vertices)
                if shadow_vertex_offset > 0:
                    # Calculate shadow vertex count from shadow faces
                    shadow_vertex_count = 0
                    if shadow_face_offset > 0:
                        temp_offset = shadow_face_offset
                        for i in range(shadow_face_count):
                            if temp_offset + 6 > len(data):
                                break
                            f_a, f_b, f_c = struct.unpack('<HHH', data[temp_offset:temp_offset+6])
                            shadow_vertex_count = max(shadow_vertex_count, f_a + 1, f_b + 1, f_c + 1)
                            temp_offset += 8
                    
                    data_offset = shadow_vertex_offset
                    for i in range(shadow_vertex_count):
                        if data_offset + 6 > len(data):
                            break
                        v_x_raw, v_y_raw, v_z_raw = struct.unpack('<hhh', data[data_offset:data_offset+6])
                        data_offset += 6
                        
                        v_x = v_x_raw / 128.0
                        v_y = v_y_raw / 128.0
                        v_z = v_z_raw / 128.0
                        
                        vertex = ParsedVertex(v_x, v_y, v_z)
                        shadow_vertices.append(vertex)
                
                # Parse shadow faces
                if shadow_face_offset > 0:
                    data_offset = shadow_face_offset
                    for i in range(shadow_face_count):
                        if data_offset + 8 > len(data):
                            break
                        f_a, f_b, f_c = struct.unpack('<HHH', data[data_offset:data_offset+6])
                        data_offset += 6
                        f_material = struct.unpack('<B', data[data_offset:data_offset+1])[0]
                        data_offset += 1
                        f_light = struct.unpack('<B', data[data_offset:data_offset+1])[0]
                        data_offset += 1
                        
                        face = ParsedFace(f_a, f_b, f_c, f_material, f_light)
                        shadow_faces.append(face)
            
            model = ParsedModel(
                name=name,
                model_id=model_id,
                spheres=spheres,
                boxes=boxes,
                vertices=vertices,
                faces=faces,
                face_groups=face_groups,
                shadow_vertices=shadow_vertices,
                shadow_faces=shadow_faces,
                version=version,
                flags=flags,
                bounding_center=(center_x, center_y, center_z),
                bounding_radius=radius,
                bounding_min=(min_x, min_y, min_z),
                bounding_max=(max_x, max_y, max_z)
            )
            
            return model
            
        except Exception as e:
            print(f"❌ Error parsing COL{version} model: {e}")
            return None

# Test function
def test_col_parser():
    """Test the COL parser with a sample file"""
    parser = COLParser()
    
    # Test with a real COL file if available
    test_file = "test.col"
    if os.path.exists(test_file):
        models = parser.parse_col_file(test_file)
        print(f"Parsed {len(models)} models from {test_file}")
        for i, model in enumerate(models):
            print(f"Model {i}: {model.name} - {len(model.spheres)}S {len(model.boxes)}B {len(model.faces)}F")
    else:
        print("No test file available")

if __name__ == "__main__":
    test_col_parser()