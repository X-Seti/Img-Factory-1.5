#this belongs in methods/detect_file_type_and_version.py - Version: 1
# X-Seti - July31 2025 - IMG Factory 1.5 - Universal File Type and Version Detection

"""
Universal File Type and Version Detection
Moved from IMGEntry class to be reusable by all entry types
Used by: IMG loading, split IMG creation, table population, validation
"""

from typing import Optional, Tuple, Any
from core.rw_versions import get_rw_version_name, parse_rw_version
from components.img_debug_functions import img_debugger

##Methods list -
# detect_entry_file_type_and_version
# detect_rw_version_from_data
# get_file_type_from_extension
# integrate_detection_functions

def detect_entry_file_type_and_version(entry, img_file=None) -> bool: #vers 1
    """Universal file type and RW version detection for any entry object
    
    Args:
        entry: Entry object with .name attribute (and optionally offset, size)
        img_file: Parent IMG file for data access (optional)
    
    Returns:
        bool: True if detection succeeded
    """
    try:
        # Extract extension from name
        if hasattr(entry, 'name') and '.' in entry.name:
            entry.extension = entry.name.split('.')[-1].upper()
            entry.extension = ''.join(c for c in entry.extension if c.isalpha())
        else:
            entry.extension = "NO_EXT"
        
        # Set file type based on extension
        entry.file_type = get_file_type_from_extension(entry.extension)
        
        # Detect RW version for RenderWare files
        if entry.extension in ['DFF', 'TXD']:
            detect_rw_version_from_data(entry, img_file)
        else:
            # Non-RW files
            entry.rw_version = 0
            entry.rw_version_name = "N/A"
            
        return True
        
    except Exception as e:
        img_debugger.error(f"Error detecting file type for {getattr(entry, 'name', 'unknown')}: {e}")
        return False

def get_file_type_from_extension(extension: str) -> str: #vers 1
    """Get file type from extension"""
    ext_lower = extension.lower()
    
    type_mapping = {
        'dff': 'DFF',
        'txd': 'TXD', 
        'col': 'COL',
        'ifp': 'IFP',
        'ipl': 'IPL',
        'dat': 'DAT',
        'wav': 'WAV',
        'scm': 'SCM',
        'ide': 'IDE',
        'img': 'IMG',
        'dir': 'DIR'
    }
    
    return type_mapping.get(ext_lower, 'UNKNOWN')

def detect_rw_version_from_data(entry, img_file=None) -> bool: #vers 1
    """Detect RenderWare version from file data
    
    Args:
        entry: Entry object 
        img_file: Parent IMG file for data access
    
    Returns:
        bool: True if version detected successfully
    """
    try:
        # Initialize RW version attributes if not present
        if not hasattr(entry, 'rw_version'):
            entry.rw_version = 0
        if not hasattr(entry, 'rw_version_name'):
            entry.rw_version_name = "Unknown"
        if not hasattr(entry, '_version_detected'):
            entry._version_detected = False
        
        # Skip if already detected
        if entry._version_detected:
            return True
        
        # Try to get file data using multiple methods
        file_data = None
        
        # Method 1: Cached data
        if hasattr(entry, '_cached_data') and entry._cached_data:
            file_data = entry._cached_data
        
        # Method 2: get_data method
        elif hasattr(entry, 'get_data'):
            try:
                file_data = entry.get_data()
            except:
                pass
        
        # Method 3: Read from IMG file
        elif img_file and hasattr(img_file, 'read_entry_data'):
            try:
                file_data = img_file.read_entry_data(entry)
            except:
                pass
        
        # Method 4: Read header directly if we have offset/size
        elif img_file and hasattr(entry, 'offset') and hasattr(entry, 'size'):
            try:
                file_data = _read_entry_header_data(entry, img_file, 12)
            except:
                pass
        
        if not file_data or len(file_data) < 12:
            img_debugger.debug(f"No data available for RW version detection: {entry.name}")
            return False
        
        # Parse RW version from header (bytes 8-12 contain version)
        try:
            version_bytes = file_data[8:12]
            version_value, version_name = parse_rw_version(version_bytes)
            
            if version_value > 0:
                entry.rw_version = version_value
                entry.rw_version_name = version_name
                entry._version_detected = True
                
                img_debugger.debug(f"✅ RW Version detected for {entry.name}: {version_name}")
                return True
            else:
                entry.rw_version_name = "Unknown"
                img_debugger.debug(f"⚠️ Unknown RW version for {entry.name}")
                
        except Exception as e:
            img_debugger.debug(f"RW version parsing failed for {entry.name}: {e}")
        
        return False
        
    except Exception as e:
        img_debugger.error(f"Error detecting RW version for {getattr(entry, 'name', 'unknown')}: {e}")
        return False

def _read_entry_header_data(entry, img_file, header_size: int = 12) -> Optional[bytes]: #vers 1
    """Read header data from entry using IMG file"""
    try:
        if not hasattr(img_file, 'file_path') or not img_file.file_path:
            return None
        
        # Determine file path based on IMG version
        if hasattr(img_file, 'version') and img_file.version == 1:
            # Version 1: Read from .img file
            img_path = img_file.file_path.replace('.dir', '.img')
        else:
            # Version 2: Read from single .img file
            img_path = img_file.file_path
        
        # Read header data
        with open(img_path, 'rb') as f:
            f.seek(entry.offset)
            return f.read(min(header_size, entry.size))
            
    except Exception as e:
        img_debugger.debug(f"Error reading header data for {entry.name}: {e}")
        return None

def create_enhanced_entry(name: str, offset: int, size: int, file_data: bytes = None, img_file=None) -> Any: #vers 1
    """Create an enhanced entry object with all detection methods
    
    Used by split IMG creation to create entries compatible with table population
    """
    # Create basic entry object
    entry = type('EnhancedEntry', (), {
        'name': name,
        'offset': offset, 
        'size': size,
        'extension': '',
        'file_type': 'UNKNOWN',
        'rw_version': 0,
        'rw_version_name': 'N/A',
        '_cached_data': file_data,
        '_version_detected': False
    })()
    
    # Add detection method to entry
    entry.detect_file_type_and_version = lambda: detect_entry_file_type_and_version(entry, img_file)
    
    # Add data access methods
    if file_data:
        entry.get_data = lambda: file_data
        entry.read_data = lambda: file_data
    
    # Run initial detection
    detect_entry_file_type_and_version(entry, img_file)
    
    return entry

def integrate_detection_functions(main_window): #vers 1
    """Integrate detection functions into main window for easy access"""
    try:
        # Add detection functions to main window
        main_window.detect_entry_file_type_and_version = detect_entry_file_type_and_version
        main_window.detect_rw_version_from_data = detect_rw_version_from_data
        main_window.get_file_type_from_extension = get_file_type_from_extension
        main_window.create_enhanced_entry = create_enhanced_entry
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ File type detection functions integrated")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error integrating detection functions: {str(e)}")
        return False

__all__ = [
    'detect_entry_file_type_and_version',
    'detect_rw_version_from_data', 
    'get_file_type_from_extension',
    'create_enhanced_entry',
    'integrate_detection_functions'
]