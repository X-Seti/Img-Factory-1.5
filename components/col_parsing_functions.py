#this belongs in components/col_parsing_functions.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Parsing Functions
# Complete COL parsing functions with safe parsing and IMG debug system

"""
COL Parsing Functions - Safe COL file parsing
Provides safe collision file parsing with debug control and error handling
"""

import struct
import os
from typing import Dict, List, Tuple, Optional
from components.img_debug_functions import img_debugger
from components.col_core_classes import is_col_debug_enabled

##Methods list -
# load_col_file_safely
# reset_table_styling
# safe_parse_col_file_structure
# safe_parse_single_model
# setup_col_tab_integration

def load_col_file_safely(main_window, file_path): #vers 1
    """Load COL file safely with proper tab management"""
    try:
        # Import required functions
        from components.col_validator import validate_col_file
        from methods.populate_col_table import setup_col_tab, load_col_file_object, setup_col_table_structure, populate_table_with_col_data_debug
        from gui.gui_infobar import update_col_info_bar_enhanced
        
        # Validate file
        if not validate_col_file(main_window, file_path):
            return False

        # Setup tab
        tab_index = setup_col_tab(main_window, file_path)
        if tab_index is None:
            return False

        # Load COL file
        col_file = load_col_file_object(main_window, file_path)
        if col_file is None:
            return False

        # Setup table structure for COL data
        setup_col_table_structure(main_window)

        # Populate table with COL data
        populate_table_with_col_data_debug(main_window, col_file)

        # Update main window state
        main_window.current_col = col_file
        main_window.open_files[tab_index]['file_object'] = col_file

        # Update info bar
        update_col_info_bar_enhanced(main_window, col_file, file_path)

        main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error loading COL file: {str(e)}")
        return False

def reset_table_styling(main_window): #vers 1
    """Reset table styling to default - moved to core/tables_structure.py"""
    try:
        from core.tables_structure import reset_table_styling
        reset_table_styling(main_window)
        
    except ImportError:
        # Fallback implementation
        try:
            if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
                return

            table = main_window.gui_layout.table
            header = table.horizontalHeader()

            # Clear all styling
            table.setStyleSheet("")
            header.setStyleSheet("")
            table.setObjectName("")

            # Reset to basic alternating colors
            table.setAlternatingRowColors(True)

            main_window.log_message("🔧 Table styling completely reset")

        except Exception as e:
            main_window.log_message(f"⚠️ Error resetting table styling: {str(e)}")
    
    except Exception as e:
        main_window.log_message(f"⚠️ Error resetting table styling: {str(e)}")

def setup_col_tab_integration(main_window): #vers 1
    """Setup COL tab integration with main window"""
    try:
        # Add COL loading method to main window
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)

        # Add styling reset method
        main_window._reset_table_styling = lambda: reset_table_styling(main_window)

        main_window.log_message("✅ COL tab integration ready")
        return True

    except Exception as e:
        main_window.log_message(f"❌ COL tab integration failed: {str(e)}")
        return False

# Safe parsing functions from old working code
def safe_parse_col_file_structure(main_window, file_path: str) -> Optional[dict]: #vers 1
    """Safely parse COL file structure without full loading"""
    try:
        if not os.path.exists(file_path):
            img_debugger.error(f"COL file not found: {file_path}")
            return None
        
        with open(file_path, 'rb') as f:
            data = f.read(32)  # Read first 32 bytes for header
        
        if len(data) < 8:
            img_debugger.error("COL file too small for header")
            return None
        
        # Check signature
        signature = data[:4]
        if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
            img_debugger.error(f"Invalid COL signature: {signature}")
            return None
        
        # Read file size
        file_size = struct.unpack('<I', data[4:8])[0]
        
        # Determine version
        version = 1
        if signature == b'COL\x02':
            version = 2
        elif signature == b'COL\x03':
            version = 3
        elif signature == b'COL\x04':
            version = 4
        
        structure_info = {
            'version': version,
            'signature': signature.decode('ascii', errors='ignore'),
            'file_size': file_size,
            'actual_size': os.path.getsize(file_path),
            'models': 1,  # Conservative estimate
            'format': f'COL Version {version}'
        }
        
        if is_col_debug_enabled():
            img_debugger.debug(f"COL structure parsed: {structure_info}")
        
        return structure_info
        
    except Exception as e:
        img_debugger.error(f"Error parsing COL structure: {e}")
        return None

def safe_parse_single_model(main_window, data: bytes, offset: int = 0) -> Tuple[Optional[dict], int]: #vers 1
    """Safely parse single COL model without crashing"""
    try:
        if offset + 8 > len(data):
            return None, offset
        
        # Read header safely
        signature = data[offset:offset+4]
        if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
            return None, offset + 4  # Skip invalid signature
        
        # Read size safely
        try:
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
        except struct.error:
            return None, offset + 8
        
        total_size = min(file_size + 8, len(data) - offset)  # Prevent overflow
        
        # Determine version
        version = 1
        if signature == b'COL\x02':
            version = 2
        elif signature == b'COL\x03':
            version = 3
        elif signature == b'COL\x04':
            version = 4
        
        # Extract name if possible (safe)
        model_name = "Unknown"
        try:
            if version == 1 and offset + 30 <= len(data):
                name_start = offset + 8
                name_data = data[name_start:name_start+22]
                model_name = name_data.split(b'\x00')[0].decode('ascii', errors='ignore')
            elif version > 1 and offset + 48 <= len(data):
                # Skip bounding data (40 bytes) then read name
                name_start = offset + 48
                if name_start + 22 <= len(data):
                    name_data = data[name_start:name_start+22]
                    model_name = name_data.split(b'\x00')[0].decode('ascii', errors='ignore')
        except:
            model_name = f"Model_v{version}"
        
        if not model_name or len(model_name.strip()) == 0:
            model_name = f"Model_v{version}_{offset}"
        
        model_info = {
            'name': model_name,
            'version': version,
            'signature': signature.decode('ascii', errors='ignore'),
            'size': file_size,
            'offset': offset,
            'formats': [f'COL Version {version}'],
            'collision_types': ['Basic COL (safe mode)']  # Simple fallback
        }

        if is_col_debug_enabled():
            img_debugger.debug(f"Model {offset} parsed safely (size: {file_size})")

        # Return with safe offset advancement
        return model_info, offset + total_size

    except Exception as e:
        img_debugger.error(f"Error parsing single model: {str(e)}")
        return None, offset + 8  # Safe advancement

# COL Parser Class - WORKING VERSION FROM OLD FILES
class COLParser:
    """Complete COL file parser with working collision data extraction - Updated to use IMG debug"""
    
    def __init__(self, debug=None): #vers 1
        """Initialize COL parser with IMG debug control"""
        debug_available = True
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            debug_available = False
            
        self.debug = debug if debug is not None else debug_available
        self.log_messages = []
    
    def log(self, message): #vers 1
        """Log debug message using IMG debug system"""
        if self.debug:
            try:
                img_debugger.debug(f"COLParser: {message}")
            except:
                print(f"COLParser: {message}")  # Fallback
        self.log_messages.append(message)
    
    def set_debug(self, enabled: bool): #vers 1
        """Enable/disable debug output"""
        self.debug = enabled
        if enabled:
            self.log("COL parser debug enabled")
        else:
            self.log("COL parser debug disabled")
    
    def parse_col_file_structure(self, file_path: str) -> Optional[dict]: #vers 1
        """Parse COL file structure safely"""
        try:
            self.log(f"Parsing COL structure: {os.path.basename(file_path)}")
            
            if not os.path.exists(file_path):
                self.log(f"File not found: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path)
            if file_size < 8:
                self.log(f"File too small: {file_size} bytes")
                return None
            
            with open(file_path, 'rb') as f:
                # Read header
                signature = f.read(4)
                if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                    self.log(f"Invalid signature: {signature}")
                    return None
                
                # Determine version
                version = 1
                if signature == b'COL\x02':
                    version = 2
                elif signature == b'COL\x03':
                    version = 3
                elif signature == b'COL\x04':
                    version = 4
                
                # Read size
                size_data = f.read(4)
                if len(size_data) < 4:
                    return None
                
                model_size = struct.unpack('<I', size_data)[0]
                
                structure = {
                    'version': version,
                    'signature': signature.decode('ascii', errors='ignore'),
                    'model_size': model_size,
                    'file_size': file_size,
                    'valid': True
                }
                
                self.log(f"COL structure parsed: version {version}, size {model_size}")
                return structure
                
        except Exception as e:
            self.log(f"Error parsing COL structure: {e}")
            return None
    
    def parse_single_model(self, data: bytes, offset: int = 0) -> Tuple[Optional[dict], int]: #vers 1
        """Parse single COL model from data"""
        try:
            if offset + 8 > len(data):
                return None, offset
            
            # Read signature
            signature = data[offset:offset+4]
            if signature not in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return None, offset + 1  # Skip 1 byte and continue
            
            # Read size
            model_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            total_size = model_size + 8
            
            if offset + total_size > len(data):
                self.log(f"Model size exceeds data length: {total_size} > {len(data) - offset}")
                return None, len(data)  # Skip to end
            
            # Determine version
            version = 1
            if signature == b'COL\x02':
                version = 2
            elif signature == b'COL\x03':
                version = 3
            elif signature == b'COL\x04':
                version = 4
            
            model_info = {
                'version': version,
                'signature': signature.decode('ascii', errors='ignore'),
                'size': model_size,
                'offset': offset,
                'data': data[offset:offset+total_size]
            }
            
            # Extract model name based on version
            try:
                if version == 1:
                    # COL1: name at offset 8, 22 bytes
                    name_start = offset + 8
                    if name_start + 22 <= len(data):
                        name_data = data[name_start:name_start+22]
                        model_info['name'] = name_data.split(b'\x00')[0].decode('ascii', errors='ignore')
                else:
                    # COL2/3/4: skip bounding data (40 bytes), then name
                    name_start = offset + 48
                    if name_start + 22 <= len(data):
                        name_data = data[name_start:name_start+22]
                        model_info['name'] = name_data.split(b'\x00')[0].decode('ascii', errors='ignore')
                
                if not model_info.get('name'):
                    model_info['name'] = f"Model_{version}_{offset}"
                    
            except Exception as e:
                model_info['name'] = f"Model_{version}_{offset}"
                self.log(f"Error extracting model name: {e}")
            
            self.log(f"Parsed model: {model_info['name']} (v{version})")
            return model_info, offset + total_size
            
        except Exception as e:
            self.log(f"Error parsing model at offset {offset}: {e}")
            return None, offset + 8  # Skip 8 bytes and continue
    
    def _is_multi_model_archive(self, data: bytes) -> bool: #vers 1
        """Check if data contains multiple COL models"""
        try:
            model_count = 0
            offset = 0
            
            while offset < len(data) - 8:
                signature = data[offset:offset+4]
                if signature in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                    model_count += 1
                    if model_count > 1:
                        return True
                    
                    # Skip this model
                    try:
                        model_size = struct.unpack('<I', data[offset+4:offset+8])[0]
                        offset += model_size + 8
                    except:
                        break
                else:
                    offset += 1
            
            return model_count > 1
            
        except Exception as e:
            self.log(f"Error checking multi-model archive: {e}")
            return False