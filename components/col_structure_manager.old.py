#this belongs in components/ col_structure_manager.py - Version: 1
# X-Seti - July08 2025 - COL Structure Management for IMG Factory 1.5

"""
COL Structure Manager
Handles COL file structure parsing, validation and data management
"""

import struct
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class COLHeader:
    """COL file header structure"""
    signature: str
    file_size: int
    model_name: str
    model_id: int
    version: int

@dataclass
class COLBounds:
    """COL bounding data structure"""
    radius: float
    center: Tuple[float, float, float]
    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]

@dataclass
class COLSphere:
    """COL collision sphere structure"""
    center: Tuple[float, float, float]
    radius: float
    material: int
    flags: int = 0

@dataclass
class COLBox:
    """COL collision box structure"""
    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]
    material: int
    flags: int = 0

@dataclass
class COLVertex:
    """COL mesh vertex structure"""
    position: Tuple[float, float, float]

@dataclass
class COLFace:
    """COL mesh face structure"""
    vertex_indices: Tuple[int, int, int]
    material: int
    light: int = 0
    flags: int = 0

@dataclass
class COLModelStructure:
    """Complete COL model structure"""
    header: COLHeader
    bounds: COLBounds
    spheres: List[COLSphere]
    boxes: List[COLBox]
    vertices: List[COLVertex]
    faces: List[COLFace]
    face_groups: List = None
    shadow_vertices: List[COLVertex] = None
    shadow_faces: List[COLFace] = None

class COLStructureManager:
    """Manages COL file structure parsing and validation"""
    
    def __init__(self):
        self.debug = True
        
    def parse_col_header(self, data: bytes, offset: int = 0) -> Tuple[COLHeader, int]:
        """Parse COL file header and return header + new offset"""
        try:
            if len(data) < offset + 32:
                raise ValueError("Data too short for COL header")
            
            # Read signature (4 bytes)
            signature = data[offset:offset+4].decode('ascii', errors='ignore')
            offset += 4
            
            # Read file size (4 bytes)
            file_size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Read model name (22 bytes, null-terminated)
            name_bytes = data[offset:offset+22]
            model_name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
            offset += 22
            
            # Read model ID (2 bytes)
            model_id = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Determine version from signature
            version = 1
            if signature.startswith('COL'):
                version_char = signature[3] if len(signature) > 3 else '1'
                if version_char.isdigit():
                    version = int(version_char)
            
            header = COLHeader(
                signature=signature,
                file_size=file_size,
                model_name=model_name,
                model_id=model_id,
                version=version
            )
            
            if self.debug:
                print(f"🔍 COL Header: {signature} v{version}, Model: '{model_name}', Size: {file_size}")
            
            return header, offset
            
        except Exception as e:
            raise ValueError(f"Error parsing COL header: {str(e)}")
    
    def parse_col_bounds(self, data: bytes, offset: int, version: int) -> Tuple[COLBounds, int]:
        """Parse COL bounding data based on version"""
        try:
            if version == 1:
                # COL1: radius + center + min + max (40 bytes)
                if len(data) < offset + 40:
                    raise ValueError("Data too short for COL1 bounds")
                
                radius = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
                center = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                min_point = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                max_point = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                
            else:
                # COL2/3: min + max + center + radius (28 bytes)
                if len(data) < offset + 28:
                    raise ValueError(f"Data too short for COL{version} bounds")
                
                min_point = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                max_point = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                center = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                radius = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
            
            bounds = COLBounds(
                radius=radius,
                center=center,
                min_point=min_point,
                max_point=max_point
            )
            
            if self.debug:
                print(f"🔍 Bounds: Center{center}, Radius:{radius:.2f}")
            
            return bounds, offset
            
        except Exception as e:
            raise ValueError(f"Error parsing COL bounds: {str(e)}")
    
    def parse_col_spheres(self, data: bytes, offset: int, version: int) -> Tuple[List[COLSphere], int]:
        """Parse COL collision spheres"""
        try:
            # Read sphere count
            if len(data) < offset + 4:
                return [], offset
            
            sphere_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            spheres = []
            sphere_size = 20 if version == 1 else 20  # Same for all versions
            
            for i in range(sphere_count):
                if len(data) < offset + sphere_size:
                    break
                
                # Read sphere data
                radius = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
                center = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                
                # Read surface/material data (4 bytes)
                surface_data = struct.unpack('<I', data[offset:offset+4])[0]
                material = surface_data & 0xFF  # Extract material from surface data
                flags = (surface_data >> 8) & 0xFFFFFF
                offset += 4
                
                sphere = COLSphere(
                    center=center,
                    radius=radius,
                    material=material,
                    flags=flags
                )
                spheres.append(sphere)
            
            if self.debug and sphere_count > 0:
                print(f"🔍 Parsed {len(spheres)} spheres")
            
            return spheres, offset
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error parsing spheres: {str(e)}")
            return [], offset
    
    def parse_col_boxes(self, data: bytes, offset: int, version: int) -> Tuple[List[COLBox], int]:
        """Parse COL collision boxes"""
        try:
            # Read box count
            if len(data) < offset + 4:
                return [], offset
            
            box_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            boxes = []
            box_size = 28  # Box size is consistent across versions
            
            for i in range(box_count):
                if len(data) < offset + box_size:
                    break
                
                # Read box data
                min_point = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                max_point = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                
                # Read surface/material data (4 bytes)
                surface_data = struct.unpack('<I', data[offset:offset+4])[0]
                material = surface_data & 0xFF
                flags = (surface_data >> 8) & 0xFFFFFF
                offset += 4
                
                box = COLBox(
                    min_point=min_point,
                    max_point=max_point,
                    material=material,
                    flags=flags
                )
                boxes.append(box)
            
            if self.debug and box_count > 0:
                print(f"🔍 Parsed {len(boxes)} boxes")
            
            return boxes, offset
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error parsing boxes: {str(e)}")
            return [], offset
    
    def parse_col_vertices(self, data: bytes, offset: int, version: int) -> Tuple[List[COLVertex], int]:
        """Parse COL mesh vertices"""
        try:
            # Read vertex count
            if len(data) < offset + 4:
                return [], offset
            
            vertex_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            vertices = []
            vertex_size = 12 if version == 1 else 6  # COL1: 12 bytes, COL2/3: 6 bytes
            
            for i in range(vertex_count):
                if len(data) < offset + vertex_size:
                    break
                
                if version == 1:
                    # COL1: float[3] (12 bytes)
                    position = struct.unpack('<fff', data[offset:offset+12])
                    offset += 12
                else:
                    # COL2/3: int16[3] (6 bytes) - needs scaling
                    x, y, z = struct.unpack('<hhh', data[offset:offset+6])
                    position = (x / 128.0, y / 128.0, z / 128.0)  # Scale factor
                    offset += 6
                
                vertex = COLVertex(position=position)
                vertices.append(vertex)
            
            if self.debug and vertex_count > 0:
                print(f"🔍 Parsed {len(vertices)} vertices")
            
            return vertices, offset
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error parsing vertices: {str(e)}")
            return [], offset
    
    def parse_col_faces(self, data: bytes, offset: int, version: int) -> Tuple[List[COLFace], int]:
        """Parse COL mesh faces"""
        try:
            # Read face count
            if len(data) < offset + 4:
                return [], offset
            
            face_count = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            faces = []
            face_size = 16 if version == 1 else 8  # COL1: 16 bytes, COL2/3: 8 bytes
            
            for i in range(face_count):
                if len(data) < offset + face_size:
                    break
                
                if version == 1:
                    # COL1: uint32[3] + surface (16 bytes)
                    a, b, c = struct.unpack('<III', data[offset:offset+12])
                    offset += 12
                    surface_data = struct.unpack('<I', data[offset:offset+4])[0]
                    offset += 4
                else:
                    # COL2/3: uint16[3] + material + light (8 bytes)
                    a, b, c = struct.unpack('<HHH', data[offset:offset+6])
                    offset += 6
                    material = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 1
                    light = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 1
                    surface_data = (material | (light << 8))
                
                material = surface_data & 0xFF
                light = (surface_data >> 8) & 0xFF
                flags = (surface_data >> 16) & 0xFFFF
                
                face = COLFace(
                    vertex_indices=(a, b, c),
                    material=material,
                    light=light,
                    flags=flags
                )
                faces.append(face)
            
            if self.debug and face_count > 0:
                print(f"🔍 Parsed {len(faces)} faces")
            
            return faces, offset
            
        except Exception as e:
            if self.debug:
                print(f"⚠️ Error parsing faces: {str(e)}")
            return [], offset
    
    def parse_complete_model(self, data: bytes, offset: int = 0) -> Tuple[COLModelStructure, int]:
        """Parse complete COL model structure"""
        try:
            original_offset = offset
            
            # Parse header
            header, offset = self.parse_col_header(data, offset)
            
            # Parse bounds
            bounds, offset = self.parse_col_bounds(data, offset, header.version)
            
            # Skip unknown data section if present (COL1)
            if header.version == 1 and offset + 4 <= len(data):
                unknown_count = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4 + (unknown_count * 8)  # Skip unknown data
            
            # Parse collision data
            spheres, offset = self.parse_col_spheres(data, offset, header.version)
            boxes, offset = self.parse_col_boxes(data, offset, header.version)
            vertices, offset = self.parse_col_vertices(data, offset, header.version)
            faces, offset = self.parse_col_faces(data, offset, header.version)
            
            # TODO: Parse face groups and shadow mesh for COL2/3
            
            model = COLModelStructure(
                header=header,
                bounds=bounds,
                spheres=spheres,
                boxes=boxes,
                vertices=vertices,
                faces=faces
            )
            
            model_size = offset - original_offset
            if self.debug:
                print(f"✅ Parsed complete model: {model_size} bytes")
            
            return model, offset
            
        except Exception as e:
            raise ValueError(f"Error parsing COL model: {str(e)}")
    
    def validate_model_structure(self, model: COLModelStructure) -> Dict[str, any]:
        """Validate COL model structure and return analysis"""
        try:
            validation = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'statistics': {}
            }
            
            # Check header
            if not model.header.signature.startswith('COL'):
                validation['errors'].append("Invalid COL signature")
                validation['valid'] = False
            
            # Check bounds
            if model.bounds.radius <= 0:
                validation['warnings'].append("Zero or negative bounding radius")
            
            # Check collision data
            total_elements = len(model.spheres) + len(model.boxes) + len(model.faces)
            if total_elements == 0:
                validation['warnings'].append("No collision geometry found")
            
            # Validate face indices
            vertex_count = len(model.vertices)
            for i, face in enumerate(model.faces):
                for j, vertex_index in enumerate(face.vertex_indices):
                    if vertex_index >= vertex_count:
                        validation['errors'].append(f"Face {i} vertex {j} index {vertex_index} out of range")
                        validation['valid'] = False
            
            # Generate statistics
            validation['statistics'] = {
                'sphere_count': len(model.spheres),
                'box_count': len(model.boxes),
                'vertex_count': len(model.vertices),
                'face_count': len(model.faces),
                'total_collision_elements': total_elements,
                'estimated_size': self._estimate_model_size(model)
            }
            
            return validation
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'statistics': {}
            }
    
    def _estimate_model_size(self, model: COLModelStructure) -> int:
        """Estimate model size in bytes"""
        size = 32  # Header size
        size += 40 if model.header.version == 1 else 28  # Bounds size
        size += len(model.spheres) * 20  # Sphere data
        size += len(model.boxes) * 28  # Box data
        size += len(model.vertices) * (12 if model.header.version == 1 else 6)  # Vertex data
        size += len(model.faces) * (16 if model.header.version == 1 else 8)  # Face data
        return size
    
    def get_model_statistics(self, model: COLModelStructure) -> Dict[str, any]:
        """Get detailed model statistics"""
        try:
            stats = {
                'name': model.header.model_name,
                'version': model.header.version,
                'model_id': model.header.model_id,
                'collision_elements': {
                    'spheres': len(model.spheres),
                    'boxes': len(model.boxes),
                    'mesh_faces': len(model.faces)
                },
                'geometry': {
                    'vertices': len(model.vertices),
                    'faces': len(model.faces)
                },
                'bounds': {
                    'center': model.bounds.center,
                    'radius': model.bounds.radius,
                    'min': model.bounds.min_point,
                    'max': model.bounds.max_point
                },
                'estimated_size': self._estimate_model_size(model)
            }
            
            # Calculate total collision elements
            stats['total_elements'] = (
                stats['collision_elements']['spheres'] + 
                stats['collision_elements']['boxes'] + 
                stats['collision_elements']['mesh_faces']
            )
            
            # Generate collision types string
            types = []
            if stats['collision_elements']['spheres'] > 0:
                types.append(f"Spheres({stats['collision_elements']['spheres']})")
            if stats['collision_elements']['boxes'] > 0:
                types.append(f"Boxes({stats['collision_elements']['boxes']})")
            if stats['collision_elements']['mesh_faces'] > 0:
                types.append(f"Mesh({stats['collision_elements']['mesh_faces']})")
            
            stats['collision_types'] = ", ".join(types) if types else "None"
            
            return stats
            
        except Exception as e:
            return {
                'name': 'Unknown',
                'version': 0,
                'model_id': 0,
                'collision_elements': {'spheres': 0, 'boxes': 0, 'mesh_faces': 0},
                'geometry': {'vertices': 0, 'faces': 0},
                'bounds': {'center': (0,0,0), 'radius': 0, 'min': (0,0,0), 'max': (0,0,0)},
                'total_elements': 0,
                'collision_types': 'Error',
                'estimated_size': 0,
                'error': str(e)
            }