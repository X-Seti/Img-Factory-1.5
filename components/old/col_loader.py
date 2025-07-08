#this belongs in components/ col_loader.py - Version: 1
# X-Seti - July08 2025 - Bridge between new parser and existing COL classes

from typing import List, Optional
from components.col_parser import COLParser, ParsedModel
from components.col_core_classes import (
    COLFile, COLModel, COLSphere, COLBox, COLVertex, COLFace, COLFaceGroup,
    Vector3, BoundingBox, COLMaterial, COLVersion
)

class COLLoader:
    """Bridge between the new COL parser and existing COL classes"""
    
    def __init__(self):
        self.parser = COLParser()
    
    def load_col_file(self, file_path: str) -> Optional[COLFile]:
        """Load COL file using the new parser and convert to COL classes"""
        try:
            # Parse with new parser
            parsed_models = self.parser.parse_col_file(file_path)
            if not parsed_models:
                return None
            
            # Create COL file
            col_file = COLFile(file_path)
            
            # Convert each parsed model
            for parsed_model in parsed_models:
                col_model = self._convert_parsed_model(parsed_model)
                if col_model:
                    col_file.models.append(col_model)
            
            col_file.is_loaded = True
            print(f"✅ COL file loaded: {len(col_file.models)} models")
            return col_file
            
        except Exception as e:
            print(f"❌ Error loading COL file: {e}")
            return None
    
    def _convert_parsed_model(self, parsed: ParsedModel) -> Optional[COLModel]:
        """Convert ParsedModel to COLModel"""
        try:
            model = COLModel()
            model.name = parsed.name
            model.model_id = parsed.model_id
            model.version = self._get_col_version(parsed.version)
            model.flags = parsed.flags
            
            # Convert bounding box
            model.bounding_box = BoundingBox(
                Vector3(*parsed.bounding_min),
                Vector3(*parsed.bounding_max),
                Vector3(*parsed.bounding_center),
                parsed.bounding_radius
            )
            
            # Convert spheres
            model.spheres = []
            for sphere_data in parsed.spheres:
                center = Vector3(sphere_data.center_x, sphere_data.center_y, sphere_data.center_z)
                material = COLMaterial(sphere_data.material)
                sphere = COLSphere(center, sphere_data.radius, material)
                model.spheres.append(sphere)
            
            # Convert boxes
            model.boxes = []
            for box_data in parsed.boxes:
                min_point = Vector3(box_data.min_x, box_data.min_y, box_data.min_z)
                max_point = Vector3(box_data.max_x, box_data.max_y, box_data.max_z)
                material = COLMaterial(box_data.material)
                box = COLBox(min_point, max_point, material)
                model.boxes.append(box)
            
            # Convert vertices
            model.vertices = []
            for vertex_data in parsed.vertices:
                position = Vector3(vertex_data.x, vertex_data.y, vertex_data.z)
                vertex = COLVertex(position)
                model.vertices.append(vertex)
            
            # Convert faces
            model.faces = []
            for face_data in parsed.faces:
                material = COLMaterial(face_data.material)
                face = COLFace(face_data.vertex_a, face_data.vertex_b, face_data.vertex_c, material, face_data.light)
                model.faces.append(face)
            
            # Convert face groups
            model.face_groups = []
            for group_data in parsed.face_groups:
                face_group = COLFaceGroup(group_data.start_face, group_data.end_face)
                model.face_groups.append(face_group)
            
            # Convert shadow vertices
            model.shadow_vertices = []
            for vertex_data in parsed.shadow_vertices:
                position = Vector3(vertex_data.x, vertex_data.y, vertex_data.z)
                vertex = COLVertex(position)
                model.shadow_vertices.append(vertex)
            
            # Convert shadow faces
            model.shadow_faces = []
            for face_data in parsed.shadow_faces:
                material = COLMaterial(face_data.material)
                face = COLFace(face_data.vertex_a, face_data.vertex_b, face_data.vertex_c, material, face_data.light)
                model.shadow_faces.append(face)
            
            print(f"✅ Converted '{model.name}': S:{len(model.spheres)} B:{len(model.boxes)} V:{len(model.vertices)} F:{len(model.faces)}")
            return model
            
        except Exception as e:
            print(f"❌ Error converting parsed model: {e}")
            return None
    
    def _get_col_version(self, version_num: int) -> COLVersion:
        """Convert version number to COLVersion enum"""
        if version_num == 1:
            return COLVersion.COL_1
        elif version_num == 2:
            return COLVersion.COL_2
        elif version_num == 3:
            return COLVersion.COL_3
        elif version_num == 4:
            return COLVersion.COL_4
        else:
            return COLVersion.COL_1

class COLFixedLoader:
    """Fixed COL loader that replaces the broken parsing"""
    
    @staticmethod
    def load_col_file_fixed(file_path: str) -> Optional[COLFile]:
        """Load COL file with complete collision data parsing"""
        loader = COLLoader()
        return loader.load_col_file(file_path)
    
    @staticmethod
    def patch_existing_col_classes():
        """Monkey patch existing COL classes to use fixed loader"""
        # Replace the load method in COLFile
        original_load = COLFile.load
        
        def fixed_load(self) -> bool:
            """Fixed load method that uses complete parsing"""
            try:
                loader = COLLoader()
                fixed_col = loader.load_col_file(self.file_path)
                
                if fixed_col:
                    # Copy the models to this instance
                    self.models = fixed_col.models
                    self.is_loaded = True
                    print(f"🔧 FIXED: Loaded {len(self.models)} models with complete collision data")
                    return True
                else:
                    print(f"❌ FIXED: Failed to load COL file")
                    return False
                    
            except Exception as e:
                print(f"❌ FIXED: Error in fixed loader: {e}")
                # Fallback to original method
                return original_load(self)
        
        # Apply the patch
        COLFile.load = fixed_load
        print("🔧 Applied COL loader patch")

# Auto-apply the patch when imported
COLFixedLoader.patch_existing_col_classes()