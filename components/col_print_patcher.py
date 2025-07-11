#this belongs in components/ col_print_patcher.py - Version: 1
# X-Seti - July10 2025 - IMG Factory 1.5 - COL Print Statement Patcher

"""
COL Print Statement Patcher
Removes the flood of print statements from COL parsing files
"""

import sys
import re
from typing import List, Dict, Any


class COLPrintPatcher:
    """Patches COL files to remove excessive print statements"""
    
    def __init__(self):
        self.patched_modules = set()
        self.original_functions = {}
        self.debug_enabled = False
    
    def enable_debug(self):
        """Enable debug output"""
        self.debug_enabled = True
    
    def disable_debug(self):
        """Disable debug output"""
        self.debug_enabled = False
    
    def patch_col_core_classes(self):
        """Patch col_core_classes.py to remove print statements"""
        try:
            from components import col_core_classes
            
            if 'col_core_classes' in self.patched_modules:
                return True
            
            # Patch COLFile._parse_col_data method
            if hasattr(col_core_classes.COLFile, '_parse_col_data'):
                original_method = col_core_classes.COLFile._parse_col_data
                self.original_functions['COLFile._parse_col_data'] = original_method
                
                def silent_parse_col_data(self, data):
                    """Parse COL data without printing"""
                    self.models = []
                    offset = 0
                    
                    # Only log if debug is enabled
                    if self.debug_enabled:
                        print(f"Parsing COL data: {len(data)} bytes")
                    
                    while offset < len(data):
                        model, consumed = self._parse_col_model(data, offset)
                        if model is None:
                            break
                        
                        self.models.append(model)
                        offset += consumed
                        
                        # Safety check to prevent infinite loops
                        if consumed == 0:
                            break
                    
                    self.is_loaded = True
                    success = len(self.models) > 0
                    
                    # Only log summary if debug enabled
                    if self.debug_enabled:
                        print(f"COL parsing complete: {len(self.models)} models loaded")
                    
                    return success
                
                col_core_classes.COLFile._parse_col_data = silent_parse_col_data
            
            # Patch COLFile._parse_col_model method
            if hasattr(col_core_classes.COLFile, '_parse_col_model'):
                original_method = col_core_classes.COLFile._parse_col_model
                self.original_functions['COLFile._parse_col_model'] = original_method
                
                def silent_parse_col_model(self, data, offset):
                    """Parse single COL model without printing"""
                    try:
                        if offset + 8 > len(data):
                            return None, 0
                        
                        # Read FourCC signature
                        fourcc = data[offset:offset+4]
                        
                        if fourcc not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                            return None, 0
                        
                        # Read file size
                        import struct
                        file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
                        total_size = file_size + 8
                        
                        if offset + total_size > len(data):
                            return None, 0
                        
                        # Create model
                        from components.col_core_classes import COLModel, COLVersion
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
                        
                        # Parse model data based on version
                        model_data = data[offset + 8:offset + total_size]
                        if model.version == COLVersion.COL_1:
                            self._parse_col1_model(model, model_data)
                        else:
                            self._parse_col23_model(model, model_data)
                        
                        return model, total_size
                        
                    except Exception as e:
                        if self.debug_enabled:
                            print(f"Error parsing COL model at offset {offset}: {e}")
                        return None, 0
                
                col_core_classes.COLFile._parse_col_model = silent_parse_col_model
            
            # Patch COLFile._parse_col1_model method
            if hasattr(col_core_classes.COLFile, '_parse_col1_model'):
                original_method = col_core_classes.COLFile._parse_col1_model
                self.original_functions['COLFile._parse_col1_model'] = original_method
                
                def silent_parse_col1_model(self, model, data):
                    """Parse COL1 model without printing"""
                    try:
                        if len(data) < 22:
                            return
                        
                        import struct
                        offset = 0
                        
                        # Read name (22 bytes, null-terminated)
                        name_bytes = data[offset:offset+22]
                        model.name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
                        offset += 22
                        
                        # Read model ID (4 bytes)
                        if offset + 4 <= len(data):
                            model.model_id = struct.unpack('<I', data[offset:offset+4])[0]
                            offset += 4
                        
                        # Initialize empty collision data for now
                        model.spheres = []
                        model.boxes = []
                        model.vertices = []
                        model.faces = []
                        
                        # Calculate basic bounding box
                        model.calculate_bounding_box()
                        model.update_flags()
                        
                    except Exception as e:
                        if self.debug_enabled:
                            print(f"Error parsing COL1 model: {e}")
                
                col_core_classes.COLFile._parse_col1_model = silent_parse_col1_model
            
            # Patch COLFile._parse_col23_model method
            if hasattr(col_core_classes.COLFile, '_parse_col23_model'):
                original_method = col_core_classes.COLFile._parse_col23_model
                self.original_functions['COLFile._parse_col23_model'] = original_method
                
                def silent_parse_col23_model(self, model, data):
                    """Parse COL2/3 model without printing"""
                    try:
                        if len(data) < 40:
                            return
                        
                        import struct
                        offset = 0
                        
                        # Read bounding sphere (16 bytes)
                        center_x, center_y, center_z, radius = struct.unpack('<ffff', data[offset:offset+16])
                        offset += 16
                        
                        # Read bounding box (24 bytes)
                        min_x, min_y, min_z = struct.unpack('<fff', data[offset:offset+12])
                        max_x, max_y, max_z = struct.unpack('<fff', data[offset+12:offset+24])
                        offset += 24
                        
                        # Set model properties
                        from components.col_core_classes import Vector3, BoundingBox
                        model.bounding_box = BoundingBox()
                        model.bounding_box.min = Vector3(min_x, min_y, min_z)
                        model.bounding_box.max = Vector3(max_x, max_y, max_z)
                        model.bounding_box.center = Vector3(center_x, center_y, center_z)
                        model.bounding_box.radius = radius
                        
                        # Initialize collision data arrays
                        model.spheres = []
                        model.boxes = []
                        model.vertices = []
                        model.faces = []
                        
                        # Set a default name
                        model.name = f"COL{model.version.value}_Model"
                        
                        # Update flags
                        model.update_flags()
                        
                    except Exception as e:
                        if self.debug_enabled:
                            print(f"Error parsing COL2/3 model: {e}")
                
                col_core_classes.COLFile._parse_col23_model = silent_parse_col23_model
            
            self.patched_modules.add('col_core_classes')
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch col_core_classes: {e}")
            return False
    
    def patch_col_parser(self):
        """Patch col_parser.py to remove print statements"""
        try:
            from components import col_parser
            
            if 'col_parser' in self.patched_modules:
                return True
            
            # Patch COLParser.log method
            if hasattr(col_parser, 'COLParser'):
                original_init = col_parser.COLParser.__init__
                self.original_functions['COLParser.__init__'] = original_init
                
                def silent_init(self, debug=False):
                    """Initialize COL parser with debug control"""
                    self.debug = self.debug_enabled  # Use our debug setting
                    self.log_messages = []
                
                def silent_log(self, message):
                    """Silent log method"""
                    if self.debug_enabled:
                        print(f"🔍 COLParser: {message}")
                    self.log_messages.append(message)
                
                col_parser.COLParser.__init__ = silent_init
                col_parser.COLParser.log = silent_log
            
            self.patched_modules.add('col_parser')
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch col_parser: {e}")
            return False
    
    def patch_col_integration(self):
        """Patch col_integration.py to remove excessive logging"""
        try:
            from components import col_integration
            
            if 'col_integration' in self.patched_modules:
                return True
            
            # Patch any excessive logging in col_integration
            # This would be module-specific based on actual content
            
            self.patched_modules.add('col_integration')
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch col_integration: {e}")
            return False
    
    def patch_all_col_modules(self):
        """Patch all COL modules for silent operation"""
        success = True
        
        success &= self.patch_col_core_classes()
        success &= self.patch_col_parser()
        success &= self.patch_col_integration()
        
        return success
    
    def restore_original_functions(self):
        """Restore original functions (for debugging)"""
        try:
            # Restore col_core_classes
            if 'col_core_classes' in self.patched_modules:
                from components import col_core_classes
                
                for func_name, original_func in self.original_functions.items():
                    if func_name.startswith('COLFile.'):
                        method_name = func_name.split('.')[1]
                        setattr(col_core_classes.COLFile, method_name, original_func)
            
            # Restore col_parser
            if 'col_parser' in self.patched_modules:
                from components import col_parser
                
                if 'COLParser.__init__' in self.original_functions:
                    col_parser.COLParser.__init__ = self.original_functions['COLParser.__init__']
            
            self.patched_modules.clear()
            self.original_functions.clear()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore original functions: {e}")
            return False


# Global patcher instance
col_patcher = COLPrintPatcher()


def apply_col_silence_patches():
    """Apply patches to silence COL debug output"""
    success = col_patcher.patch_all_col_modules()
    if success:
        print("✅ COL modules patched for silent operation")
    return success


def enable_col_debug_output():
    """Enable COL debug output"""
    col_patcher.enable_debug()
    print("🔊 COL debug output enabled")


def disable_col_debug_output():
    """Disable COL debug output"""
    col_patcher.disable_debug()
    print("🔇 COL debug output disabled")


def restore_col_original_functions():
    """Restore original COL functions (for debugging)"""
    success = col_patcher.restore_original_functions()
    if success:
        print("🔄 COL original functions restored")
    return success


def install_col_print_