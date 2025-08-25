#this belongs in methods/detect_file_type_version.py - Version: 2
# X-Seti - August25 2025 - IMG Factory 1.5 - File Type and Version Detection - NO FALLBACKS

"""
File Type and Version Detection - CLEAN VERSION
Works or fails cleanly - no fallback code
"""

from typing import Optional, Any
from core.rw_versions import parse_rw_version, get_rw_version_name
from components.img_debug_functions import img_debugger

##Methods list -
# detect_entry_file_type_and_version
# detect_rw_version_from_entry_data
# get_file_type_from_extension
# integrate_detection_functions
# read_entry_data_header

def detect_entry_file_type_and_version(entry, img_file=None) -> bool: #vers 2
    """Clean file type and RW version detection - NO FALLBACKS
    
    Args:
        entry: Entry object with .name attribute
        img_file: Parent IMG file for data access (optional)
    
    Returns:
        bool: True if detection succeeded, False if failed
    """
    try:
        # Must have a name
        if not hasattr(entry, 'name') or not entry.name:
            img_debugger.error("Entry has no name - detection failed")
            return False
        
        # Extract extension from name
        if '.' in entry.name:
            entry.extension = entry.name.split('.')[-1].upper()
            # Clean extension (letters only)
            entry.extension = ''.join(c for c in entry.extension if c.isalpha())
        else:
            entry.extension = "UNKNOWN"
        
        # Set file type based on extension
        entry.file_type = get_file_type_from_extension(entry.extension)
        
        # For RenderWare files, detect version
        if entry.extension in ['DFF', 'TXD']:
            return detect_rw_version_from_entry_data(entry, img_file)
        else:
            # Non-RW files - set defaults and succeed
            entry.rw_version = 0
            entry.rw_version_name = "N/A"
            return True
            
    except Exception as e:
        img_debugger.error(f"Error detecting file type for {entry.name}: {e}")
        return False

def get_file_type_from_extension(extension: str) -> str: #vers 1
    """Get file type from extension - simple mapping"""
    ext_lower = extension.lower()
    
    type_mapping = {
        'dff': 'MODEL',
        'txd': 'TEXTURE', 
        'col': 'COLLISION',
        'ifp': 'ANIMATION',
        'ipl': 'PLACEMENT',
        'ide': 'DEFINITION',
        'dat': 'DATA',
        'wav': 'AUDIO',
        'scm': 'SCRIPT'
    }
    
    return type_mapping.get(ext_lower, 'UNKNOWN')

def detect_rw_version_from_entry_data(entry, img_file) -> bool: #vers 1
    """Detect RW version from entry data - SINGLE METHOD ONLY
    
    Args:
        entry: Entry object with offset/size
        img_file: IMG file to read from
    
    Returns:
        bool: True if version detected, False if failed
    """
    try:
        # Initialize RW attributes
        entry.rw_version = 0
        entry.rw_version_name = "Unknown"
        
        # Must have img_file to read data
        if not img_file:
            img_debugger.debug(f"No IMG file provided for RW detection: {entry.name}")
            return False
        
        # Must have valid offset and size
        if not hasattr(entry, 'offset') or not hasattr(entry, 'size'):
            img_debugger.debug(f"Entry missing offset/size for RW detection: {entry.name}")
            return False
        
        if entry.offset <= 0 or entry.size < 12:
            img_debugger.debug(f"Invalid offset/size for RW detection: {entry.name}")
            return False
        
        # Read first 12 bytes from file
        header_data = read_entry_data_header(entry, img_file, 12)
        if not header_data or len(header_data) < 12:
            img_debugger.debug(f"Failed to read header data: {entry.name}")
            return False
        
        # Parse RW version from bytes 8-12
        version_bytes = header_data[8:12]
        version_value, version_name = parse_rw_version(version_bytes)
        
        if version_value > 0 and version_name:
            entry.rw_version = version_value
            entry.rw_version_name = version_name
            img_debugger.debug(f"RW version detected: {entry.name} -> {version_name}")
            return True
        else:
            img_debugger.debug(f"No valid RW version found: {entry.name}")
            return False
            
    except Exception as e:
        img_debugger.error(f"RW version detection failed for {entry.name}: {e}")
        return False

def read_entry_data_header(entry, img_file, num_bytes: int) -> Optional[bytes]: #vers 1
    """Read header bytes from entry - SINGLE CLEAN METHOD
    
    Args:
        entry: Entry with offset attribute
        img_file: IMG file with read_entry_data method or file_path
        num_bytes: Number of bytes to read
    
    Returns:
        bytes: Header data or None if failed
    """
    try:
        # Method 1: Use img_file.read_entry_data if available
        if hasattr(img_file, 'read_entry_data'):
            full_data = img_file.read_entry_data(entry)
            if full_data and len(full_data) >= num_bytes:
                return full_data[:num_bytes]
        
        # Method 2: Read directly from file path
        if hasattr(img_file, 'file_path') and img_file.file_path:
            file_path = img_file.file_path
            
            # For Version 1 IMG, read from .img file
            if hasattr(img_file, 'version') and hasattr(img_file.version, 'name'):
                if img_file.version.name == 'VERSION_1' and file_path.endswith('.dir'):
                    file_path = file_path[:-4] + '.img'
            
            with open(file_path, 'rb') as f:
                f.seek(entry.offset)
                return f.read(num_bytes)
        
        # If we get here, we failed
        return None
        
    except Exception as e:
        img_debugger.error(f"Failed to read header data: {e}")
        return None

def integrate_detection_functions(main_window): #vers 1
    """Integrate detection functions into main window"""
    try:
        # Add clean detection functions
        main_window.detect_entry_file_type_and_version = detect_entry_file_type_and_version
        main_window.detect_rw_version_from_entry_data = detect_rw_version_from_entry_data
        main_window.get_file_type_from_extension = get_file_type_from_extension
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Clean file type detection integrated")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Detection integration failed: {e}")
        return False

# Export only the clean functions
__all__ = [
    'detect_entry_file_type_and_version',
    'detect_rw_version_from_entry_data', 
    'get_file_type_from_extension',
    'read_entry_data_header',
    'integrate_detection_functions'
]
