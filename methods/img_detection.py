#this belongs in methods/ img_detection.py - Version: 1
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG Detection Functions

"""
IMG Detection Functions - RW Version Detection
Centralized RW version detection for all IMG entry types
Uses existing core/rw_versions.py functions
"""

import struct
from typing import Optional, Tuple

##Methods list -
# detect_entry_rw_version
# detect_rw_version_from_data
# parse_rw_header
# get_rw_version_name
# is_renderware_file
# detect_file_type_from_extension
# integrate_detection_functions

def detect_entry_rw_version(entry, data: bytes) -> bool: #vers 1
    """Detect RW version for an entry from file data"""
    try:
        # Initialize RW properties
        if hasattr(entry, '_rw_version'):
            entry._rw_version = None
        if hasattr(entry, '_rw_version_name'):
            entry._rw_version_name = "Unknown"
        if hasattr(entry, 'rw_version'):
            entry.rw_version = 0
        if hasattr(entry, 'rw_version_name'):
            entry.rw_version_name = "Unknown"
        
        # Check if it's a RenderWare file
        file_ext = getattr(entry, 'name', '').lower()
        if not file_ext.endswith(('.dff', '.txd')):
            # Not a RenderWare file
            if hasattr(entry, '_rw_version_name'):
                entry._rw_version_name = "Not RenderWare"
            if hasattr(entry, 'rw_version_name'):
                entry.rw_version_name = "Not RenderWare"
            return True
        
        # Try to detect RW version from data
        version_value, version_name = detect_rw_version_from_data(data)
        
        if version_value > 0:
            # Set RW version properties
            if hasattr(entry, '_rw_version'):
                entry._rw_version = version_value
            if hasattr(entry, '_rw_version_name'):
                entry._rw_version_name = version_name
            if hasattr(entry, 'rw_version'):
                entry.rw_version = version_value
            if hasattr(entry, 'rw_version_name'):
                entry.rw_version_name = version_name
            
            return True
        else:
            # Failed to detect
            if hasattr(entry, '_rw_version_name'):
                entry._rw_version_name = "RW File"
            if hasattr(entry, 'rw_version_name'):
                entry.rw_version_name = "RW File"
            return False
        
    except Exception as e:
        # Error during detection
        if hasattr(entry, '_rw_version_name'):
            entry._rw_version_name = f"Error: {str(e)}"
        if hasattr(entry, 'rw_version_name'):
            entry.rw_version_name = f"Error: {str(e)}"
        return False


def detect_rw_version_from_data(data: bytes) -> Tuple[int, str]: #vers 1
    """Detect RW version from raw file data"""
    try:
        if len(data) < 12:
            return 0, "Too small"
        
        # Try to import existing RW detection functions
        try:
            from core.rw_versions import parse_rw_version, get_rw_version_name, is_valid_rw_version
            
            # RW version is usually at offset 8-12
            version_bytes = data[8:12]
            version_value, version_name = parse_rw_version(version_bytes)
            
            if version_value > 0 and is_valid_rw_version(version_value):
                return version_value, version_name
            
        except ImportError:
            pass
        
        # Fallback manual detection
        version_value, version_name = parse_rw_header(data)
        if version_value > 0:
            return version_value, version_name
        
        return 0, "Unknown"
        
    except Exception as e:
        return 0, f"Error: {str(e)}"


def parse_rw_header(data: bytes) -> Tuple[int, str]: #vers 1
    """Manual RW header parsing fallback"""
    try:
        if len(data) < 12:
            return 0, "Too small"
        
        # RenderWare files start with section header
        # Bytes 0-4: Section type
        # Bytes 4-8: Section size
        # Bytes 8-12: RW version
        
        section_type = struct.unpack('<I', data[0:4])[0]
        section_size = struct.unpack('<I', data[4:8])[0]
        rw_version = struct.unpack('<I', data[8:12])[0]
        
        # Validate section type (common RW sections)
        valid_sections = [0x0001, 0x000E, 0x0010, 0x0014, 0x0015, 0x0016, 0x001A]
        
        if section_type in valid_sections and section_size > 0:
            # Convert version to readable format
            version_name = get_rw_version_name(rw_version)
            return rw_version, version_name
        
        return 0, "Invalid RW header"
        
    except Exception as e:
        return 0, f"Parse error: {str(e)}"


def get_rw_version_name(version_value: int) -> str: #vers 1
    """Convert RW version value to human readable name"""
    try:
        # Try to use existing function
        try:
            from core.rw_versions import get_rw_version_name as core_get_version
            return core_get_version(version_value)
        except ImportError:
            pass
        
        # Fallback version mapping
        version_map = {
            0x30000: "3.0.0.0",
            0x31001: "3.1.0.1 GTA III",
            0x32000: "3.2.0.0", 
            0x33002: "3.3.0.2 GTA VC (PC)",
            0x34001: "3.4.0.1",
            0x34003: "3.4.0.3",
            0x35000: "3.5.0.0",
            0x35002: "3.5.0.2",
            0x36003: "3.6.0.3 GTA SA (PC)",
            0x37002: "3.7.0.2"
        }
        
        if version_value in version_map:
            return version_map[version_value]
        
        # Try to format as version number
        if version_value > 0:
            major = (version_value >> 16) & 0xFF
            minor = (version_value >> 8) & 0xFF
            patch1 = (version_value >> 4) & 0xF
            patch2 = version_value & 0xF
            return f"{major}.{minor}.{patch1}.{patch2}"
        
        return "Unknown"
        
    except Exception:
        return "Unknown"


def is_renderware_file(filename: str) -> bool: #vers 1
    """Check if file is a RenderWare file by extension"""
    try:
        if not filename:
            return False
        
        filename_lower = filename.lower()
        rw_extensions = ['.dff', '.txd']
        
        return any(filename_lower.endswith(ext) for ext in rw_extensions)
        
    except Exception:
        return False


def detect_file_type_from_extension(filename: str) -> str: #vers 1
    """Detect file type from extension"""
    try:
        if not filename or '.' not in filename:
            return "UNKNOWN"
        
        ext = filename.split('.')[-1].upper()
        
        # Clean extension (letters only)
        ext = ''.join(c for c in ext if c.isalpha())
        
        # Common IMG file types
        type_map = {
            'DFF': 'MODEL',
            'TXD': 'TEXTURE',
            'COL': 'COLLISION', 
            'IFP': 'ANIMATION',
            'IPL': 'PLACEMENT',
            'IDE': 'DEFINITION',
            'DAT': 'DATA',
            'WAV': 'AUDIO',
            'SCM': 'SCRIPT'
        }
        
        return type_map.get(ext, ext)
        
    except Exception:
        return "UNKNOWN"


def integrate_detection_functions(main_window) -> bool: #vers 1
    """Integrate detection functions into main window"""
    try:
        # Add detection methods
        main_window.detect_entry_rw_version = detect_entry_rw_version
        main_window.detect_rw_version_from_data = detect_rw_version_from_data
        main_window.is_renderware_file = is_renderware_file
        main_window.detect_file_type_from_extension = detect_file_type_from_extension
        main_window.get_rw_version_name = get_rw_version_name
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ RW detection functions integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Detection integration failed: {e}")
        return False


# Export functions
__all__ = [
    'detect_entry_rw_version',
    'detect_rw_version_from_data',
    'parse_rw_header',
    'get_rw_version_name',
    'is_renderware_file',
    'detect_file_type_from_extension',
    'integrate_detection_functions'
]