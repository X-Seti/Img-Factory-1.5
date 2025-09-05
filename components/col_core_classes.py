#this belongs in components/ col_core_classes.py - Version: 8
# X-Seti - September04 2025 - IMG Factory 1.5 - COL Core Classes CLEAN - Methods Moved

"""
COL Core Classes - CLEAN VERSION
All shared methods moved to methods/col_operations.py - NO DUPLICATES
Classes import methods from methods/ to avoid code duplication
"""

import struct
import os
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

# Import shared methods from existing methods/ files
from methods.col_operations import (
    extract_col_from_img_entry, get_col_basic_info, get_col_detailed_analysis,
    validate_col_data, save_col_to_img_entry, create_temporary_col_file,
    cleanup_temporary_file
)

# Import debug functions
try:
    from components.img_debug_functions import img_debugger
except ImportError:
    # Fallback debug system
    class FallbackDebugger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    
    img_debugger = FallbackDebugger()

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

##Methods list - NOW IN methods/col_operations.py -
# extract_col_from_img_entry, get_col_basic_info, get_col_detailed_analysis
# validate_col_data, save_col_to_img_entry, create_temporary_col_file
# cleanup_temporary_file, diagnose_col_file_structure, set_col_debug_enabled, is_col_debug_enabled

class COLVersion(Enum): #vers 1
    """COL file format versions"""
    COL_1 = 1
    COL_2 = 2
    COL_3 = 3
    COL_4 = 4

class Vector3: #vers 1
    """3D vector class for positions and directions"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0): 
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"Vector3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def __repr__(self):
        return self.__str__()
    
    def length(self) -> float: #vers 1
        """Calculate vector length"""
        import math
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self): #vers 1
        """Normalize vector to unit length"""
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length
            self.z /= length
    
    def dot(self, other: 'Vector3') -> float: #vers 1
        """Calculate dot product with another vector"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vector3') -> 'Vector3': #vers 1
        """Calculate cross product with another vector"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

class BoundingBox: #vers 1
    """Axis-aligned bounding box"""
    def __init__(self): 
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
        
        # Set bounds
        self.min = Vector3(min_x, min_y, min_z)
        self.max = Vector3(max_x, max_y, max_z)
        
        # Calculate center
        self.center = Vector3(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        )
        
        # Calculate radius (distance from center to corner)
        import math
        dx = max_x - self.center.x
        dy = max_y - self.center.y
        dz = max_z - self.center.z
        self.radius = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def contains_point(self, point: Vector3) -> bool: #vers 1
        """Check if point is inside bounding box"""
        return (self.min.x <= point.x <= self.max.x and
                self.min.y <= point.y <= self.max.y and
                self.min.z <= point.z <= self.max.z)

class COLSphere: #vers 1
    """Collision sphere"""
    def __init__(self):
        self.center = Vector3()
        self.radius = 0.0
        self.surface = 0  # Surface material type
        self.piece = 0    # Piece ID
    
    def __str__(self):
        return f"COLSphere(center={self.center}, radius={self.radius:.3f})"

class COLBox: #vers 1
    """Collision box"""
    def __init__(self):
        self.min = Vector3()
        self.max = Vector3()
        self.surface = 0  # Surface material type
        self.piece = 0    # Piece ID
    
    def __str__(self):
        return f"COLBox(min={self.min}, max={self.max})"
    
    def get_center(self) -> Vector3: #vers 1
        """Get center point of box"""
        return Vector3(
            (self.min.x + self.max.x) / 2,
            (self.min.y + self.max.y) / 2,
            (self.min.z + self.max.z) / 2
        )
    
    def get_size(self) -> Vector3: #vers 1
        """Get size dimensions of box"""
        return Vector3(
            self.max.x - self.min.x,
            self.max.y - self.min.y,
            self.max.z - self.min.z
        )

class COLVertex: #vers 1
    """Collision mesh vertex"""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.position = Vector3(x, y, z)
    
    def __str__(self):
        return f"COLVertex({self.position})"

class COLFace: #vers 1
    """Collision mesh face"""
    def __init__(self):
        self.a = 0  # Vertex index A
        self.b = 0  # Vertex index B  
        self.c = 0  # Vertex index C
        self.surface = 0  # Surface material type
    
    def __str__(self):
        return f"COLFace(a={self.a}, b={self.b}, c={self.c}, surface={self.surface})"
    
    def get_normal(self, vertices: List[Vector3]) -> Vector3: #vers 1
        """Calculate face normal from vertices"""
        if len(vertices) <= max(self.a, self.b, self.c):
            return Vector3()
        
        v1 = vertices[self.a]
        v2 = vertices[self.b]
        v3 = vertices[self.c]
        
        # Calculate two edge vectors
        edge1 = Vector3(v2.x - v1.x, v2.y - v1.y, v2.z - v1.z)
        edge2 = Vector3(v3.x - v1.x, v3.y - v1.y, v3.z - v1.z)
        
        # Calculate cross product for normal
        normal = edge1.cross(edge2)
        normal.normalize()
        
        return normal

class COLFaceGroup: #vers 1
    """Group of collision faces with shared material"""
    def __init__(self):
        self.surface = 0  # Surface material type
        self.faces = []   # List of face indices
    
    def __str__(self):
        return f"COLFaceGroup(surface={self.surface}, faces={len(self.faces)})"

class COLMaterial: #vers 1
    """Collision surface material"""
    def __init__(self):
        self.friction = 1.0
        self.elasticity = 0.0
        self.flags = 0
        self.name = ""
    
    def __str__(self):
        return f"COLMaterial(name='{self.name}', friction={self.friction:.2f})"

class COLModel: #vers 1
    """Single collision model within COL file"""
    def __init__(self):
        self.name = ""
        self.model_id = 0
        
        # Geometry collections
        self.spheres = []     # List[COLSphere]
        self.boxes = []       # List[COLBox]
        self.vertices = []    # List[Vector3]
        self.faces = []       # List[COLFace]
        self.face_groups = [] # List[COLFaceGroup]
        
        # Bounding info
        self.bounding_box = BoundingBox()
        self.center = Vector3()
        self.radius = 0.0
        
        # Properties
        self.flags = 0
        self.has_face_groups = False
        self.has_shadow_mesh = False
    
    def calculate_bounding_box(self): #vers 1
        """Calculate bounding box from all vertices"""
        if self.vertices:
            self.bounding_box.calculate_from_vertices(self.vertices)
            self.center = self.bounding_box.center
            self.radius = self.bounding_box.radius
    
    def add_sphere(self, center: Vector3, radius: float, surface: int = 0, piece: int = 0): #vers 1
        """Add collision sphere"""
        sphere = COLSphere()
        sphere.center = center
        sphere.radius = radius
        sphere.surface = surface
        sphere.piece = piece
        self.spheres.append(sphere)
    
    def add_box(self, min_pos: Vector3, max_pos: Vector3, surface: int = 0, piece: int = 0): #vers 1
        """Add collision box"""
        box = COLBox()
        box.min = min_pos
        box.max = max_pos
        box.surface = surface
        box.piece = piece
        self.boxes.append(box)
    
    def add_vertex(self, position: Vector3) -> int: #vers 1
        """Add vertex and return its index"""
        self.vertices.append(position)
        return len(self.vertices) - 1
    
    def add_face(self, a: int, b: int, c: int, surface: int = 0): #vers 1
        """Add collision face"""
        face = COLFace()
        face.a = a
        face.b = b
        face.c = c
        face.surface = surface
        self.faces.append(face)
    
    def get_element_count(self) -> Dict[str, int]: #vers 1
        """Get count of all collision elements"""
        return {
            'spheres': len(self.spheres),
            'boxes': len(self.boxes),
            'vertices': len(self.vertices),
            'faces': len(self.faces),
            'face_groups': len(self.face_groups)
        }
    
    def __str__(self):
        counts = self.get_element_count()
        return f"COLModel(name='{self.name}', elements={sum(counts.values())})"

class COLFile: #vers 1
    """COL file container - Uses shared methods"""
    def __init__(self):
        self.file_path = ""
        self.version = COLVersion.COL_1
        self.models = []  # List[COLModel]
        self.materials = []  # List[COLMaterial]
        
        # File properties
        self.is_loaded = False
        self.modified = False
        self.file_size = 0
    
    def add_model(self, name: str = "NewModel") -> COLModel: #vers 1
        """Add new model to COL file"""
        model = COLModel()
        model.name = name or f"Model_{len(self.models)}"
        model.model_id = len(self.models)
        self.models.append(model)
        self.modified = True
        return model
    
    def remove_model(self, index: int) -> bool: #vers 1
        """Remove model by index"""
        try:
            if 0 <= index < len(self.models):
                del self.models[index]
                self.modified = True
                return True
            return False
        except Exception:
            return False
    
    def get_model(self, index: int) -> Optional[COLModel]: #vers 1
        """Get model by index"""
        try:
            if 0 <= index < len(self.models):
                return self.models[index]
            return None
        except Exception:
            return None
    
    def find_model_by_name(self, name: str) -> Optional[COLModel]: #vers 1
        """Find model by name"""
        for model in self.models:
            if model.name.lower() == name.lower():
                return model
        return None
    
    def get_total_element_count(self) -> Dict[str, int]: #vers 1
        """Get total count of all elements across all models"""
        totals = {
            'models': len(self.models),
            'spheres': 0,
            'boxes': 0,
            'vertices': 0,
            'faces': 0,
            'face_groups': 0
        }
        
        for model in self.models:
            counts = model.get_element_count()
            for key in ['spheres', 'boxes', 'vertices', 'faces', 'face_groups']:
                totals[key] += counts[key]
        
        return totals
    
    def validate_structure(self) -> Tuple[bool, List[str]]: #vers 1
        """Validate COL file structure using shared method"""
        try:
            result = validate_col_data(self.file_path if hasattr(self, 'file_path') else '')
            # Convert shared method result to expected format
            if isinstance(result, dict):
                if 'error' in result:
                    return False, [result['error']]
                else:
                    return True, []
            return True, []
        except Exception as e:
            return False, [f"Validation failed: {str(e)}"]
    
    def get_file_info(self) -> Dict[str, Any]: #vers 1
        """Get comprehensive file information using shared method"""
        try:
            if self.file_path:
                return get_col_basic_info(self.file_path)
            else:
                # Return basic structure info
                totals = self.get_total_element_count()
                return {
                    'file_path': 'New COL File',
                    'version': self.version.name if hasattr(self.version, 'name') else str(self.version),
                    'model_count': totals['models'],
                    'total_elements': sum(v for k, v in totals.items() if k != 'models'),
                    'file_size': self.file_size,
                    'status': 'Modified' if self.modified else 'Saved'
                }
        except Exception as e:
            return {'error': f"Failed to get file info: {str(e)}"}
    
    def extract_from_img_entry(self, main_window, row: int) -> bool: #vers 1
        """Extract COL data from IMG entry using shared method"""
        try:
            result = extract_col_from_img_entry(main_window, row)
            if result:
                col_data, entry_name = result
                # Process the extracted data
                self.file_path = entry_name
                self.file_size = len(col_data)
                self.is_loaded = True
                return True
            return False
        except Exception:
            return False
    
    def save_to_img_entry(self, main_window, row: int, col_data: bytes) -> bool: #vers 1
        """Save COL data to IMG entry using shared method"""
        return save_col_to_img_entry(main_window, row, col_data)
    
    def create_temporary_file(self, col_data: bytes, entry_name: str) -> Optional[str]: #vers 1
        """Create temporary COL file using shared method"""
        return create_temporary_col_file(col_data, entry_name)
    
    def cleanup_temporary_file(self, file_path: str) -> bool: #vers 1
        """Cleanup temporary file using shared method"""
        return cleanup_temporary_file(file_path)
    
    def __str__(self):
        totals = self.get_total_element_count()
        return f"COLFile(path='{self.file_path}', models={totals['models']}, elements={sum(v for k, v in totals.items() if k != 'models')})"


# Global debug control functions (use shared methods)

def diagnose_col_file(col_file: COLFile) -> Dict[str, Any]: #vers 1
    """Diagnose COL file using shared method"""
    try:
        from methods.col_operations import diagnose_col_file_structure
        return diagnose_col_file_structure(col_file)
    except ImportError:
        # Fallback implementation
        return {
            'error': 'Shared diagnose function not available',
            'file_path': getattr(col_file, 'file_path', 'Unknown')
        }

def set_col_debug_enabled(enabled: bool): #vers 1
    """Enable/disable COL debug using shared method"""
    try:
        from methods.col_operations import set_col_debug_enabled as shared_set_debug
        shared_set_debug(enabled)
    except ImportError:
        # Fallback - just log
        img_debugger.info(f"COL debug {'enabled' if enabled else 'disabled'}")

def is_col_debug_enabled() -> bool: #vers 1
    """Check if COL debug enabled using shared method"""
    try:
        from methods.col_operations import is_col_debug_enabled as shared_is_debug
        return shared_is_debug()
    except ImportError:
        return False

# Export all classes and functions
__all__ = [
    # Enums
    'COLVersion',
    # Basic classes
    'Vector3', 'BoundingBox',
    # Collision element classes
    'COLSphere', 'COLBox', 'COLVertex', 'COLFace', 'COLFaceGroup', 'COLMaterial',
    # Main classes
    'COLModel', 'COLFile',
    # Functions
    'diagnose_col_file', 'set_col_debug_enabled', 'is_col_debug_enabled'
]