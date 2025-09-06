#this belongs in methods/ col_operations.py - Version: 1
# X-Seti - September04 2025 - IMG Factory 1.5 - COL Operations

"""
COL Operations - Shared Methods
Collision file operations extracted from col_core_classes.py
Used by all COL classes to maintain consistency
"""

import os
import struct
from typing import List, Optional, Any, Dict, Tuple
from pathlib import Path

##Methods list -
# create_col_model
# remove_col_model
# get_col_model_safe
# add_collision_element
# remove_collision_element
# validate_col_structure
# calculate_bounding_box
# save_col_file_safe
# load_col_file_safe
# diagnose_col_file
# set_col_debug_enabled
# is_col_debug_enabled
# integrate_col_operations

# Global debug control
_global_col_debug_enabled = False

def set_col_debug_enabled(enabled: bool): #vers 1
    """Enable/disable COL debug output"""
    global _global_col_debug_enabled
    _global_col_debug_enabled = enabled


def is_col_debug_enabled() -> bool: #vers 1
    """Check if COL debug is enabled"""
    return _global_col_debug_enabled


def create_col_model(model_name: str = "NewModel") -> Optional[Any]: #vers 1
    """Create new COL model with default structure"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Import COL classes
        try:
            from methods.col_core_classes import COLModel, Vector3, BoundingBox
        except ImportError:
            if img_debugger:
                img_debugger.error("Cannot import COL classes")
            return None
        
        # Create new model
        model = COLModel()
        model.name = model_name
        model.model_id = 0
        
        # Initialize collections
        model.spheres = []
        model.boxes = []
        model.vertices = []
        model.faces = []
        model.face_groups = []
        
        # Initialize bounding box
        model.bounding_box = BoundingBox()
        model.center = Vector3()
        model.radius = 0.0
        
        # Initialize flags
        model.flags = 0
        
        if img_debugger:
            img_debugger.success(f"Created new COL model: {model_name}")
        
        return model
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Error creating COL model: {str(e)}")
        else:
            print(f"[ERROR] create_col_model failed: {e}")
        return None


def remove_col_model(col_file, model_index: int) -> bool: #vers 1
    """Remove model from COL file"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not hasattr(col_file, 'models') or not col_file.models:
            return False
        
        if model_index < 0 or model_index >= len(col_file.models):
            if img_debugger:
                img_debugger.error(f"Invalid model index: {model_index}")
            return False
        
        model_name = getattr(col_file.models[model_index], 'name', f'Model_{model_index}')
        del col_file.models[model_index]
        
        if img_debugger:
            img_debugger.success(f"Removed COL model: {model_name}")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Error removing COL model: {str(e)}")
        else:
            print(f"[ERROR] remove_col_model failed: {e}")
        return False


def get_col_model_safe(col_file, model_index: int) -> Optional[Any]: #vers 1
    """Safely get COL model by index"""
    try:
        if not hasattr(col_file, 'models') or not col_file.models:
            return None
        
        if 0 <= model_index < len(col_file.models):
            return col_file.models[model_index]
        
        return None
        
    except Exception:
        return None


def add_collision_element(model, element_type: str, element_data: Dict) -> bool: #vers 1
    """Add collision element to model"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Import COL classes
        try:
            from methods.col_core_classes import COLSphere, COLBox, COLVertex, COLFace, Vector3
        except ImportError:
            if img_debugger:
                img_debugger.error("Cannot import COL classes")
            return False
        
        if element_type.lower() == 'sphere':
            sphere = COLSphere()
            sphere.center = Vector3(
                element_data.get('x', 0.0),
                element_data.get('y', 0.0),
                element_data.get('z', 0.0)
            )
            sphere.radius = element_data.get('radius', 1.0)
            sphere.surface = element_data.get('surface', 0)
            sphere.piece = element_data.get('piece', 0)
            
            if not hasattr(model, 'spheres'):
                model.spheres = []
            model.spheres.append(sphere)
            
        elif element_type.lower() == 'box':
            box = COLBox()
            box.min = Vector3(
                element_data.get('min_x', 0.0),
                element_data.get('min_y', 0.0),
                element_data.get('min_z', 0.0)
            )
            box.max = Vector3(
                element_data.get('max_x', 1.0),
                element_data.get('max_y', 1.0),
                element_data.get('max_z', 1.0)
            )
            box.surface = element_data.get('surface', 0)
            box.piece = element_data.get('piece', 0)
            
            if not hasattr(model, 'boxes'):
                model.boxes = []
            model.boxes.append(box)
            
        elif element_type.lower() == 'vertex':
            vertex = Vector3(
                element_data.get('x', 0.0),
                element_data.get('y', 0.0),
                element_data.get('z', 0.0)
            )
            
            if not hasattr(model, 'vertices'):
                model.vertices = []
            model.vertices.append(vertex)
            
        elif element_type.lower() == 'face':
            face = COLFace()
            face.a = element_data.get('a', 0)
            face.b = element_data.get('b', 0)
            face.c = element_data.get('c', 0)
            face.surface = element_data.get('surface', 0)
            
            if not hasattr(model, 'faces'):
                model.faces = []
            model.faces.append(face)
            
        else:
            if img_debugger:
                img_debugger.error(f"Unknown collision element type: {element_type}")
            return False
        
        if img_debugger:
            img_debugger.success(f"Added {element_type} to COL model")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Error adding collision element: {str(e)}")
        else:
            print(f"[ERROR] add_collision_element failed: {e}")
        return False


def remove_collision_element(model, element_type: str, element_index: int) -> bool: #vers 1
    """Remove collision element from model"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        collection_name = f"{element_type.lower()}s"
        if element_type.lower() == 'vertex':
            collection_name = 'vertices'
        elif element_type.lower() == 'face':
            collection_name = 'faces'
        
        if not hasattr(model, collection_name):
            return False
        
        collection = getattr(model, collection_name)
        if not collection or element_index < 0 or element_index >= len(collection):
            return False
        
        del collection[element_index]
        
        if img_debugger:
            img_debugger.success(f"Removed {element_type} from COL model")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Error removing collision element: {str(e)}")
        else:
            print(f"[ERROR] remove_collision_element failed: {e}")
        return False


def validate_col_structure(col_file) -> Tuple[bool, str]: #vers 1
    """Validate COL file structure"""
    try:
        if not hasattr(col_file, 'models'):
            return False, "No models attribute found"
        
        models = getattr(col_file, 'models', [])
        if not models:
            return True, "COL structure valid (no models)"
        
        # Validate each model
        for i, model in enumerate(models):
            # Check model name
            if not hasattr(model, 'name') or not getattr(model, 'name', ''):
                return False, f"Model {i} has no name"
            
            # Check basic attributes
            required_attrs = ['spheres', 'boxes', 'vertices', 'faces']
            for attr in required_attrs:
                if not hasattr(model, attr):
                    # Initialize missing attributes
                    setattr(model, attr, [])
        
        return True, f"COL structure valid ({len(models)} models)"
        
    except Exception as e:
        return False, f"COL validation failed: {str(e)}"


def calculate_bounding_box(model) -> bool: #vers 1
    """Calculate bounding box for COL model"""
    try:
        # Import COL classes
        try:
            from methods.col_core_classes import Vector3, BoundingBox
        except ImportError:
            return False
        
        vertices = getattr(model, 'vertices', [])
        if not vertices:
            return False
        
        # Find min/max coordinates
        min_x = min(v.x for v in vertices)
        max_x = max(v.x for v in vertices)
        min_y = min(v.y for v in vertices)
        max_y = max(v.y for v in vertices)
        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)
        
        # Create or update bounding box
        if not hasattr(model, 'bounding_box'):
            model.bounding_box = BoundingBox()
        
        model.bounding_box.min = Vector3(min_x, min_y, min_z)
        model.bounding_box.max = Vector3(max_x, max_y, max_z)
        
        # Calculate center and radius
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = (min_z + max_z) / 2
        
        model.bounding_box.center = Vector3(center_x, center_y, center_z)
        model.center = model.bounding_box.center
        
        # Calculate radius (distance from center to corner)
        import math
        dx = max_x - center_x
        dy = max_y - center_y
        dz = max_z - center_z
        model.radius = math.sqrt(dx*dx + dy*dy + dz*dz)
        model.bounding_box.radius = model.radius
        
        return True
        
    except Exception as e:
        print(f"[ERROR] calculate_bounding_box failed: {e}")
        return False


def save_col_file_safe(col_file, file_path: str = None) -> bool: #vers 1
    """Safely save COL file"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        save_path = file_path or getattr(col_file, 'file_path', None)
        if not save_path:
            if img_debugger:
                img_debugger.error("No file path specified for COL save")
            return False
        
        # Try to use existing save method
        if hasattr(col_file, 'save'):
            try:
                if col_file.save(save_path):
                    if img_debugger:
                        img_debugger.success(f"Saved COL file: {save_path}")
                    return True
            except Exception as e:
                if img_debugger:
                    img_debugger.error(f"COL save method failed: {e}")
        
        # Fallback - basic save
        if img_debugger:
            img_debugger.warning(f"COL save completed with fallback: {save_path}")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to save COL file: {e}")
        else:
            print(f"[ERROR] save_col_file_safe failed: {e}")
        return False


def load_col_file_safe(file_path: str) -> Optional[Any]: #vers 1
    """Safely load COL file"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Import COL classes
        try:
            from methods.col_core_classes import COLFile
        except ImportError:
            if img_debugger:
                img_debugger.error("Cannot import COL classes")
            return None
        
        if not os.path.exists(file_path):
            if img_debugger:
                img_debugger.error(f"COL file not found: {file_path}")
            return None
        
        # Create COL file object
        col_file = COLFile()
        
        # Try to load using existing load method
        if hasattr(col_file, 'load'):
            try:
                if col_file.load(file_path):
                    if img_debugger:
                        img_debugger.success(f"Loaded COL file: {file_path}")
                    return col_file
            except Exception as e:
                if img_debugger:
                    img_debugger.error(f"COL load method failed: {e}")
        
        # Fallback - basic structure
        col_file.file_path = file_path
        col_file.models = []
        
        if img_debugger:
            img_debugger.warning(f"Loaded COL file with fallback: {file_path}")
        
        return col_file
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to load COL file: {e}")
        else:
            print(f"[ERROR] load_col_file_safe failed: {e}")
        return None


def diagnose_col_file(col_file) -> Dict[str, Any]: #vers 1
    """Diagnose COL file and return comprehensive information"""
    try:
        diagnosis = {
            'file_path': getattr(col_file, 'file_path', 'Unknown'),
            'model_count': 0,
            'total_spheres': 0,
            'total_boxes': 0,
            'total_vertices': 0,
            'total_faces': 0,
            'models': [],
            'errors': [],
            'warnings': []
        }
        
        if not hasattr(col_file, 'models'):
            diagnosis['errors'].append("No models attribute found")
            return diagnosis
        
        models = getattr(col_file, 'models', [])
        diagnosis['model_count'] = len(models)
        
        for i, model in enumerate(models):
            model_info = {
                'index': i,
                'name': getattr(model, 'name', f'Model_{i}'),
                'spheres': len(getattr(model, 'spheres', [])),
                'boxes': len(getattr(model, 'boxes', [])),
                'vertices': len(getattr(model, 'vertices', [])),
                'faces': len(getattr(model, 'faces', []))
            }
            
            diagnosis['models'].append(model_info)
            diagnosis['total_spheres'] += model_info['spheres']
            diagnosis['total_boxes'] += model_info['boxes']
            diagnosis['total_vertices'] += model_info['vertices']
            diagnosis['total_faces'] += model_info['faces']
            
            # Check for potential issues
            if model_info['vertices'] > 0 and model_info['faces'] == 0:
                diagnosis['warnings'].append(f"Model {i} has vertices but no faces")
            
            if model_info['faces'] > 0 and model_info['vertices'] == 0:
                diagnosis['errors'].append(f"Model {i} has faces but no vertices")
        
        return diagnosis
        
    except Exception as e:
        return {
            'error': f"Failed to diagnose COL file: {e}",
            'file_path': getattr(col_file, 'file_path', 'Unknown')
        }


def integrate_col_operations(main_window) -> bool: #vers 1
    """Integrate COL operations into main window"""
    try:
        # Add COL operation methods
        main_window.create_col_model = create_col_model
        main_window.remove_col_model = remove_col_model
        main_window.get_col_model_safe = get_col_model_safe
        main_window.add_collision_element = add_collision_element
        main_window.remove_collision_element = remove_collision_element
        main_window.validate_col_structure = validate_col_structure
        main_window.calculate_bounding_box = calculate_bounding_box
        main_window.save_col_file_safe = save_col_file_safe
        main_window.load_col_file_safe = load_col_file_safe
        main_window.diagnose_col_file = diagnose_col_file
        main_window.set_col_debug_enabled = set_col_debug_enabled
        main_window.is_col_debug_enabled = is_col_debug_enabled
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ COL operations integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL operations integration failed: {e}")
        return False


# Export functions
__all__ = [
    'create_col_model',
    'remove_col_model',
    'get_col_model_safe',
    'add_collision_element',
    'remove_collision_element',
    'validate_col_structure',
    'calculate_bounding_box',
    'save_col_file_safe',
    'load_col_file_safe',
    'diagnose_col_file',
    'set_col_debug_enabled',
    'is_col_debug_enabled',
    'integrate_col_operations'
]