#this belongs in methods/col_operations.py - Version: 1
# X-Seti - August13 2025 - IMG Factory 1.5 - COL Operations Methods

"""
COL Operations Methods - Shared functions for COL file operations
Used by GUI context menus, COL editor, and other COL functionality
"""

import os
import tempfile
from typing import Optional, Dict, Any, Tuple
from components.img_debug_functions import img_debugger
from components.img_core_classes import format_file_size

##Methods list -
# extract_col_from_img_entry
# get_col_basic_info
# get_col_detailed_analysis
# save_col_to_img_entry
# validate_col_data

def extract_col_from_img_entry(main_window, row: int) -> Optional[Tuple[bytes, str]]: #vers 1
    """Extract COL data from IMG entry and return data + entry name"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            img_debugger.error("No IMG file loaded")
            return None
        
        if row < 0 or row >= len(main_window.current_img.entries):
            img_debugger.error(f"Invalid row index: {row}")
            return None
        
        entry = main_window.current_img.entries[row]
        
        if not entry.name.lower().endswith('.col'):
            img_debugger.error(f"Entry {entry.name} is not a COL file")
            return None
        
        # Extract COL data
        col_data = entry.get_data()
        if not col_data:
            img_debugger.error(f"Failed to extract data from {entry.name}")
            return None
        
        img_debugger.debug(f"Extracted {len(col_data)} bytes from {entry.name}")
        return col_data, entry.name
        
    except Exception as e:
        img_debugger.error(f"Error extracting COL data: {str(e)}")
        return None

def get_col_basic_info(col_data: bytes) -> Dict[str, Any]: #vers 1
    """Get basic information about COL data"""
    try:
        if len(col_data) < 8:
            return {'error': 'COL data too small'}
        
        # Read signature
        signature = col_data[:4]
        
        # Determine version
        version = "Unknown"
        if signature == b'COLL':
            version = "COL1"
        elif signature == b'COL\x02':
            version = "COL2"
        elif signature == b'COL\x03':
            version = "COL3"
        elif signature == b'COL\x04':
            version = "COL4"
        else:
            return {'error': f'Invalid COL signature: {signature}'}
        
        # Count models (basic estimation)
        model_count = 0
        offset = 0
        
        while offset < len(col_data) - 8:
            chunk_sig = col_data[offset:offset+4]
            if chunk_sig in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                model_count += 1
                try:
                    import struct
                    size = struct.unpack('<I', col_data[offset+4:offset+8])[0]
                    offset += size + 8
                except:
                    break
            else:
                break
        
        return {
            'version': version,
            'model_count': max(1, model_count),
            'size': len(col_data),
            'signature': signature
        }
        
    except Exception as e:
        img_debugger.error(f"Error getting COL basic info: {str(e)}")
        return {'error': str(e)}

def get_col_detailed_analysis(col_file_path: str) -> Dict[str, Any]: #vers 1
    """Get detailed analysis of COL file using existing components"""
    try:
        from components.col_core_classes import COLFile
        
        # Load COL file
        col_file = COLFile(col_file_path)
        if not col_file.load():
            return {'error': 'Failed to load COL file'}
        
        analysis = {
            'valid': True,
            'models': [],
            'total_spheres': 0,
            'total_boxes': 0,
            'total_faces': 0,
            'total_vertices': 0
        }
        
        if hasattr(col_file, 'models') and col_file.models:
            for model in col_file.models:
                model_info = {
                    'name': getattr(model, 'name', 'Unknown'),
                    'version': getattr(model, 'version', 'Unknown'),
                    'spheres': len(getattr(model, 'spheres', [])),
                    'boxes': len(getattr(model, 'boxes', [])),
                    'faces': len(getattr(model, 'faces', [])),
                    'vertices': len(getattr(model, 'vertices', []))
                }
                
                analysis['models'].append(model_info)
                analysis['total_spheres'] += model_info['spheres']
                analysis['total_boxes'] += model_info['boxes']
                analysis['total_faces'] += model_info['faces']
                analysis['total_vertices'] += model_info['vertices']
        
        return analysis
        
    except Exception as e:
        img_debugger.error(f"Error getting detailed COL analysis: {str(e)}")
        return {'error': str(e)}

def validate_col_data(col_data: bytes) -> Dict[str, Any]: #vers 1
    """Validate COL data using existing validator"""
    try:
        # Create temporary file for validation
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name
        
        try:
            from components.col_validator import COLValidator
            
            # Validate the data
            result = COLValidator.validate_col_file(temp_path)
            
            return {
                'valid': result.is_valid,
                'errors': result.errors if hasattr(result, 'errors') else [],
                'warnings': result.warnings if hasattr(result, 'warnings') else [],
                'info': result.info if hasattr(result, 'info') else []
            }
            
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except ImportError:
        img_debugger.warning("COL validator not available")
        return {'error': 'COL validator not available'}
    except Exception as e:
        img_debugger.error(f"Error validating COL data: {str(e)}")
        return {'error': str(e)}

def save_col_to_img_entry(main_window, row: int, col_data: bytes) -> bool: #vers 1
    """Save COL data back to IMG entry (for future use)"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            img_debugger.error("No IMG file loaded")
            return False
        
        if row < 0 or row >= len(main_window.current_img.entries):
            img_debugger.error(f"Invalid row index: {row}")
            return False
        
        entry = main_window.current_img.entries[row]
        
        # This would require IMG modification functionality
        # For now, just log the operation
        img_debugger.info(f"Would save {len(col_data)} bytes to {entry.name}")
        
        # TODO: Implement actual IMG entry modification
        # This requires extending the IMG system to support entry replacement
        
        return True
        
    except Exception as e:
        img_debugger.error(f"Error saving COL data: {str(e)}")
        return False

def create_temporary_col_file(col_data: bytes, entry_name: str) -> Optional[str]: #vers 1
    """Create temporary COL file from data"""
    try:
        # Use entry name for temp file if possible
        base_name = os.path.splitext(entry_name)[0] if entry_name else "temp_col"
        
        with tempfile.NamedTemporaryFile(suffix='.col', prefix=f"{base_name}_", delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name
        
        img_debugger.debug(f"Created temporary COL file: {temp_path}")
        return temp_path
        
    except Exception as e:
        img_debugger.error(f"Error creating temporary COL file: {str(e)}")
        return None

def cleanup_temporary_file(file_path: str) -> bool: #vers 1
    """Clean up temporary file safely"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            img_debugger.debug(f"Cleaned up temporary file: {file_path}")
            return True
        return False
    except Exception as e:
        img_debugger.warning(f"Failed to cleanup temporary file {file_path}: {str(e)}")
        return False

# Export functions
__all__ = [
    'extract_col_from_img_entry',
    'get_col_basic_info', 
    'get_col_detailed_analysis',
    'validate_col_data',
    'save_col_to_img_entry',
    'create_temporary_col_file',
    'cleanup_temporary_file'
]