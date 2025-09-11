#this belongs in methods/ img_detection.py - Version: 3
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG Detection UPDATED

"""
IMG Detection - RW Version and Platform Detection UPDATED
Merged with detect_file_type_version.py functions + added new detection from img_core_classes.py
"""

import os
import struct
from typing import Optional, Any, Tuple, Dict
from pathlib import Path

##Methods list -
# detect_entry_file_type_and_version
# detect_rw_version_from_entry_data
# get_file_type_from_extension
# read_entry_data_header
# detect_img_version
# detect_img_platform
# get_img_platform_info
# detect_entry_rw_version
# integrate_detection_functions

def detect_entry_file_type_and_version(entry, img_file=None) -> bool: #vers 3
    """Clean file type and RW version detection - ENHANCED
    
    Args:
        entry: Entry object with .name attribute
        img_file: Parent IMG file for data access (optional)
    
    Returns:
        bool: True if detection succeeded, False if failed
    """
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Must have a name
        if not hasattr(entry, 'name') or not entry.name:
            if img_debugger:
                img_debugger.error("Entry has no name - detection failed")
            return False
        
        # Extract extension from name
        if '.' in entry.name:
            entry.extension = entry.name.split('.')[-1].lower()
        else:
            entry.extension = 'unknown'
        
        # Get file type from extension
        entry.file_type = get_file_type_from_extension(entry.extension)
        
        # For RW files, detect version from data
        if entry.extension in ['dff', 'txd', 'anp', 'ifp']:
            if img_file:
                header_data = read_entry_data_header(entry, img_file, 16)
                if header_data:
                    detect_rw_version_from_entry_data(entry, header_data)
        
        # Enhanced detection for other formats
        if entry.extension == 'col':
            entry.file_type = 'Collision'
        elif entry.extension in ['wav', 'mp3', 'ogg']:
            entry.file_type = 'Audio'
        elif entry.extension in ['bmp', 'png', 'jpg', 'jpeg']:
            entry.file_type = 'Image'
        
        if img_debugger:
            img_debugger.debug(f"Detected: {entry.name} -> {entry.file_type} ({entry.extension})")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Detection failed for {getattr(entry, 'name', 'unknown')}: {e}")
        return False


def detect_rw_version_from_entry_data(entry, header_data: bytes) -> bool: #vers 3
    """Detect RW version from entry header data"""
    try:
        # Import RW version functions
        try:
            from core.rw_versions import parse_rw_version, get_rw_version_name
        except ImportError:
            return False
        
        if len(header_data) < 12:
            return False
        
        # Read RW header structure
        try:
            section_type = struct.unpack('<I', header_data[0:4])[0]
            section_size = struct.unpack('<I', header_data[4:8])[0]
            rw_version = struct.unpack('<I', header_data[8:12])[0]
            
            # Parse RW version
            version_info = parse_rw_version(rw_version)
            if version_info:
                entry.rw_version = rw_version
                entry.rw_version_string = get_rw_version_name(rw_version)
                entry.rw_section_type = section_type
                entry.rw_section_size = section_size
                return True
                
        except struct.error:
            pass
        
        return False
        
    except Exception:
        return False


def get_file_type_from_extension(extension: str) -> str: #vers 3
    """Get file type description from extension"""
    try:
        extension = extension.lower().strip('.')
        
        type_map = {
            'dff': 'Model',
            'txd': 'Texture Dictionary',
            'col': 'Collision',
            'ide': 'Item Definition',
            'ipl': 'Item Placement',
            'dat': 'Data',
            'cfg': 'Configuration',
            'anp': 'Animation Package',
            'ifp': 'Animation',
            'wav': 'Audio Wave',
            'mp3': 'Audio MP3',
            'ogg': 'Audio OGG',
            'bmp': 'Bitmap Image',
            'png': 'PNG Image',
            'jpg': 'JPEG Image',
            'jpeg': 'JPEG Image',
            'tga': 'TGA Image',
            'gif': 'GIF Image',
            'txt': 'Text File',
            'log': 'Log File',
            'xml': 'XML File',
            'json': 'JSON File'
        }
        
        return type_map.get(extension, 'Unknown')
        
    except Exception:
        return 'Unknown'


def read_entry_data_header(entry, img_file=None, num_bytes: int = 16) -> Optional[bytes]: #vers 3
    """Read header bytes from entry data"""
    try:
        # Method 1: Check for cached data
        if hasattr(entry, 'data') and entry.data:
            return entry.data[:num_bytes]
        
        if hasattr(entry, '_cached_data') and entry._cached_data:
            return entry._cached_data[:num_bytes]
        
        # Method 2: Use get_data method if available
        if hasattr(entry, 'get_data'):
            try:
                full_data = entry.get_data()
                if full_data and len(full_data) >= num_bytes:
                    return full_data[:num_bytes]
            except Exception:
                pass
        
        # Method 3: Read directly from IMG file
        if img_file and hasattr(entry, 'offset') and hasattr(entry, 'size'):
            try:
                file_path = getattr(img_file, 'file_path', None)
                if file_path and os.path.exists(file_path):
                    # Handle Version 1 IMG files
                    if hasattr(img_file, 'version'):
                        version_name = getattr(img_file.version, 'name', None) or str(img_file.version)
                        if 'VERSION_1' in version_name and file_path.endswith('.dir'):
                            file_path = file_path[:-4] + '.img'
                    
                    with open(file_path, 'rb') as f:
                        f.seek(entry.offset)
                        return f.read(num_bytes)
            except Exception:
                pass
        
        return None
        
    except Exception:
        return None


def detect_img_version(file_path: str) -> Tuple[int, str]: #vers 3
    """Detect IMG file version from file structure"""
    try:
        if not os.path.exists(file_path):
            return 0, "File not found"
        
        # Check for .dir/.img pair (Version 1)
        if file_path.endswith('.dir'):
            img_path = file_path[:-4] + '.img'
            if os.path.exists(img_path):
                return 1, "Version 1 (DIR/IMG pair)"
        
        # Check single .img file (Version 2)
        if file_path.endswith('.img'):
            try:
                with open(file_path, 'rb') as f:
                    # Read first 8 bytes
                    header = f.read(8)
                    if len(header) >= 4:
                        # Check for VER2 signature
                        if header[:4] == b'VER2':
                            return 2, "Version 2 (Single IMG file)"
                        
                        # If no VER2 signature but it's an .img file, might be Version 1 .img file
                        dir_path = file_path[:-4] + '.dir'
                        if os.path.exists(dir_path):
                            return 1, "Version 1 (DIR/IMG pair)"
                        
                        # Single IMG without DIR might be Version 2 without signature
                        return 2, "Version 2 (Assumed)"
            except Exception:
                pass
        
        return 0, "Unknown format"
        
    except Exception as e:
        return 0, f"Detection error: {e}"


def detect_img_platform(file_path: str) -> str: #vers 3
    """Detect IMG file platform from characteristics"""
    try:
        # Simple heuristics based on file path and name
        file_path_lower = file_path.lower()
        
        # Path-based detection
        if 'ps2' in file_path_lower:
            return 'ps2'
        elif 'xbox' in file_path_lower:
            return 'xbox'
        elif 'pc' in file_path_lower:
            return 'pc'
        
        # Filename-based detection
        filename = os.path.basename(file_path_lower)
        if 'ps2' in filename:
            return 'ps2'
        elif 'xbox' in filename:
            return 'xbox'
        
        # Default to PC if no specific indicators
        return 'pc'
        
    except Exception:
        return 'pc'


def get_img_platform_info(platform: str) -> Dict[str, Any]: #vers 3
    """Get detailed platform information"""
    try:
        platform_info = {
            'pc': {
                'name': 'PC',
                'endianness': 'little',
                'sector_size': 2048,
                'max_filename_length': 24,
                'compression_support': True,
                'alignment': 4
            },
            'ps2': {
                'name': 'PlayStation 2',
                'endianness': 'little',
                'sector_size': 2048,
                'max_filename_length': 24,
                'compression_support': False,
                'alignment': 16
            },
            'xbox': {
                'name': 'Xbox',
                'endianness': 'little',
                'sector_size': 2048,
                'max_filename_length': 24,
                'compression_support': True,
                'alignment': 4
            }
        }
        
        return platform_info.get(platform.lower(), platform_info['pc'])
        
    except Exception:
        return platform_info['pc']


def get_platform_specific_specs(platform: str) -> Dict[str, Any]: #vers 1
    """Get platform specs - from img_core_classes"""
    return get_img_platform_info(platform)


def detect_entry_rw_version(entry, data: bytes = None) -> bool: #vers 3
    """Enhanced RW version detection for entry"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Use provided data or try to get from entry
        header_data = data
        if not header_data:
            if hasattr(entry, 'data') and entry.data:
                header_data = entry.data[:16]
            elif hasattr(entry, '_cached_data') and entry._cached_data:
                header_data = entry._cached_data[:16]
        
        if not header_data or len(header_data) < 12:
            return False
        
        # Detect RW version
        success = detect_rw_version_from_entry_data(entry, header_data)
        
        if success and img_debugger:
            rw_version_string = getattr(entry, 'rw_version_string', 'Unknown')
            img_debugger.debug(f"RW version detected for {entry.name}: {rw_version_string}")
        
        return success
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"RW version detection failed: {e}")
        return False


def integrate_detection_functions(main_window) -> bool: #vers 3
    """Integrate detection functions into main window"""
    try:
        # Add detection functions
        main_window.detect_entry_file_type_and_version = detect_entry_file_type_and_version
        main_window.detect_rw_version_from_entry_data = detect_rw_version_from_entry_data
        main_window.get_file_type_from_extension = get_file_type_from_extension
        main_window.read_entry_data_header = read_entry_data_header
        main_window.detect_img_version = detect_img_version
        main_window.detect_img_platform = detect_img_platform
        main_window.get_img_platform_info = get_img_platform_info
        main_window.detect_entry_rw_version = detect_entry_rw_version
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG detection functions integrated (updated)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Detection integration failed: {e}")
        return False


# Export functions
__all__ = [
    'detect_entry_file_type_and_version',
    'detect_rw_version_from_entry_data', 
    'get_file_type_from_extension',
    'read_entry_data_header',
    'detect_img_version',
    'detect_img_platform',
    'get_img_platform_info',
    'detect_entry_rw_version',
    'integrate_detection_functions'
]
