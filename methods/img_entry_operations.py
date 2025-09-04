#this belongs in methods/ img_entry_operations.py - Version: 1
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG Entry Operations

"""
IMG Entry Operations - Shared Methods
Entry management operations for IMG files (add, remove, get, validate)
Used by all IMG classes to maintain consistency
"""

import os
from typing import List, Optional, Any
from methods.img_detection import detect_entry_rw_version

##Methods list -
# add_entry_safe
# remove_entry_safe
# get_entry_safe
# has_entry_safe
# get_entry_by_index_safe
# calculate_next_offset
# validate_entry_data
# sanitize_filename
# create_img_entry
# integrate_entry_operations

def add_entry_safe(img_file, filename: str, data: bytes, auto_save: bool = False) -> bool: #vers 1
    """Safely add entry to IMG file with RW detection"""
    try:
        # Validate inputs
        if not filename or not data:
            return False
        
        # Sanitize filename
        clean_filename = sanitize_filename(filename)
        
        # Check for duplicates
        if has_entry_safe(img_file, clean_filename):
            # Handle duplicate - could expand this with dialog later
            return False
        
        # Create new entry
        entry = create_img_entry(clean_filename, data, img_file)
        if not entry:
            return False
        
        # Detect RW version for DFF/TXD files
        if clean_filename.lower().endswith(('.dff', '.txd')):
            detect_entry_rw_version(entry, data)
        
        # Add to entries list
        if not hasattr(img_file, 'entries'):
            img_file.entries = []
        
        img_file.entries.append(entry)
        
        # Mark as modified
        if hasattr(img_file, 'modified'):
            img_file.modified = True
        
        return True
        
    except Exception as e:
        print(f"[ERROR] add_entry_safe failed: {e}")
        return False


def remove_entry_safe(img_file, filename: str) -> bool: #vers 1
    """Safely remove entry from IMG file"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return False
        
        # Find and remove entry
        for i, entry in enumerate(img_file.entries):
            entry_name = getattr(entry, 'name', '')
            if entry_name.lower() == filename.lower():
                removed_entry = img_file.entries.pop(i)
                
                # Mark as modified
                if hasattr(img_file, 'modified'):
                    img_file.modified = True
                
                # Add to deleted entries list
                if hasattr(img_file, 'deleted_entries'):
                    img_file.deleted_entries.append(removed_entry)
                
                return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] remove_entry_safe failed: {e}")
        return False


def get_entry_safe(img_file, filename: str) -> Optional[Any]: #vers 1
    """Safely get entry by filename"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return None
        
        for entry in img_file.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name.lower() == filename.lower():
                return entry
        
        return None
        
    except Exception:
        return None


def has_entry_safe(img_file, filename: str) -> bool: #vers 1
    """Safely check if entry exists"""
    try:
        return get_entry_safe(img_file, filename) is not None
    except Exception:
        return False


def get_entry_by_index_safe(img_file, index: int) -> Optional[Any]: #vers 1
    """Safely get entry by index"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return None
        
        if 0 <= index < len(img_file.entries):
            return img_file.entries[index]
        
        return None
        
    except Exception:
        return None


def calculate_next_offset(img_file) -> int: #vers 1
    """Calculate next available offset for new entry"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            # First entry
            if hasattr(img_file, 'version'):
                if hasattr(img_file.version, 'name') and img_file.version.name == 'VERSION_1':
                    return 0
                else:
                    return 2048  # V2 reserve space for directory
            return 0
        
        # Find max offset + size
        max_end = 0
        for entry in img_file.entries:
            entry_offset = getattr(entry, 'offset', 0)
            entry_size = getattr(entry, 'size', 0)
            entry_end = entry_offset + entry_size
            
            if entry_end > max_end:
                max_end = entry_end
        
        # Align to sector boundary (2048 bytes)
        return ((max_end + 2047) // 2048) * 2048
        
    except Exception as e:
        print(f"[ERROR] calculate_next_offset failed: {e}")
        return 0


def validate_entry_data(filename: str, data: bytes) -> tuple[bool, str]: #vers 1
    """Validate entry data before adding"""
    try:
        # Check filename
        if not filename or len(filename.strip()) == 0:
            return False, "Empty filename"
        
        if len(filename) > 24:
            return False, "Filename too long (max 24 characters)"
        
        # Check data
        if not data or len(data) == 0:
            return False, "Empty file data"
        
        if len(data) > 100 * 1024 * 1024:  # 100MB limit
            return False, "File too large (max 100MB)"
        
        # Check filename characters
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            return False, f"Invalid characters in filename: {invalid_chars}"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Validation error: {e}"


def sanitize_filename(filename: str) -> str: #vers 1
    """Sanitize filename for IMG entry"""
    try:
        if not filename:
            return "unknown"
        
        # Remove invalid characters
        invalid_chars = '<>:"|?*\\/\r\n\t'
        clean_name = ''.join(c for c in filename if c not in invalid_chars)
        
        # Trim to max length
        if len(clean_name) > 24:
            name_part, ext_part = os.path.splitext(clean_name)
            if len(ext_part) > 0:
                max_name_len = 24 - len(ext_part)
                clean_name = name_part[:max_name_len] + ext_part
            else:
                clean_name = clean_name[:24]
        
        # Ensure not empty
        if not clean_name or clean_name.isspace():
            clean_name = "unknown"
        
        return clean_name
        
    except Exception:
        return "unknown"


def create_img_entry(filename: str, data: bytes, img_file) -> Optional[Any]: #vers 1
    """Create new IMG entry object"""
    try:
        # Import IMG entry class - try multiple locations
        entry = None
        
        # Try components/img_core_classes.py
        try:
            from components.img_core_classes import IMGEntry
            entry = IMGEntry()
        except ImportError:
            pass
        
        # Try Core.py (IMG_Editor reference)
        if not entry:
            try:
                from Core import IMGEntry
                entry = IMGEntry()
            except ImportError:
                pass
        
        # Fallback - create simple object
        if not entry:
            class SimpleIMGEntry:
                def __init__(self):
                    self.name = ""
                    self.size = 0
                    self.offset = 0
                    self.data = None
                    self.is_new_entry = True
            
            entry = SimpleIMGEntry()
        
        # Set entry properties
        entry.name = filename
        entry.size = len(data)
        entry.offset = calculate_next_offset(img_file)
        entry.is_new_entry = True
        
        # Store data
        if hasattr(entry, 'data'):
            entry.data = data
        elif hasattr(entry, '_cached_data'):
            entry._cached_data = data
        
        # Set IMG file reference if method exists
        if hasattr(entry, 'set_img_file'):
            entry.set_img_file(img_file)
        
        return entry
        
    except Exception as e:
        print(f"[ERROR] create_img_entry failed: {e}")
        return None


def integrate_entry_operations(main_window) -> bool: #vers 1
    """Integrate entry operations into main window"""
    try:
        # Add entry operation methods
        main_window.add_entry_safe = lambda img_file, filename, data, auto_save=False: add_entry_safe(img_file, filename, data, auto_save)
        main_window.remove_entry_safe = lambda img_file, filename: remove_entry_safe(img_file, filename)
        main_window.get_entry_safe = lambda img_file, filename: get_entry_safe(img_file, filename)
        main_window.has_entry_safe = lambda img_file, filename: has_entry_safe(img_file, filename)
        main_window.calculate_next_offset = lambda img_file: calculate_next_offset(img_file)
        main_window.sanitize_filename = sanitize_filename
        main_window.validate_entry_data = validate_entry_data
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG entry operations integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Entry operations integration failed: {e}")
        return False


# Export functions
__all__ = [
    'add_entry_safe',
    'remove_entry_safe', 
    'get_entry_safe',
    'has_entry_safe',
    'get_entry_by_index_safe',
    'calculate_next_offset',
    'validate_entry_data',
    'sanitize_filename',
    'create_img_entry',
    'integrate_entry_operations'
]