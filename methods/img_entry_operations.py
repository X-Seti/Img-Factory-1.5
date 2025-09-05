#this belongs in methods/ img_entry_operations.py - Version: 4
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG Entry Operations UPDATED

"""
IMG Entry Operations - Shared Methods UPDATED
Entry management operations for IMG files (add, remove, get, validate)
Merged functions from img_core_classes.py to eliminate duplicates
"""

import os
import struct
from typing import List, Optional, Any, Tuple
from pathlib import Path

##Methods list -
# add_multiple_entries_batch(img_file
# add_entry_safe
# remove_entry_safe  
# get_entry_safe
# has_entry_safe
# get_entry_by_index_safe
# calculate_next_offset
# validate_entry_data
# sanitize_filename
# create_img_entry
# add_multiple_entries
# import_file_to_img
# import_directory_to_img
# integrate_entry_operations

# Constants from img_core_classes
MAX_FILENAME_LENGTH = 24
SECTOR_SIZE = 2048

def add_multiple_entries_batch(img_file, file_data_pairs: List[tuple], auto_save: bool = True) -> int: #vers 1
    """Add multiple entries efficiently - BATCH METHOD from img_core_classes"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None

        added_count = 0

        if img_debugger:
            img_debugger.debug(f"Adding {len(file_data_pairs)} entries in batch mode...")

        for filename, data in file_data_pairs:
            # Add without auto-save for efficiency
            if add_entry_safe(img_file, filename, data, auto_save=False):
                added_count += 1
            else:
                if img_debugger:
                    img_debugger.warning(f"Failed to add {filename} in batch")

        # Save once at the end if requested
        if auto_save and added_count > 0:
            if img_debugger:
                img_debugger.debug(f"Batch save: {added_count} entries added")
            # Note: save functionality would need to be implemented separately

        if img_debugger:
            img_debugger.success(f"Batch add complete: {added_count}/{len(file_data_pairs)} entries added")

        return added_count

    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Batch add failed: {e}")
        return 0


def add_entry_safe(img_file, filename: str, data: bytes, auto_save: bool = False) -> bool: #vers 2
    """Safely add entry to IMG file with enhanced validation"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if img_debugger:
            img_debugger.debug(f"add_entry called: {filename} ({len(data)} bytes)")
            img_debugger.debug(f"Current IMG entries before: {len(getattr(img_file, 'entries', []))}")
        
        # Validate inputs
        if not filename or not data:
            return False
        
        # Sanitize filename
        clean_filename = sanitize_filename(filename)
        if clean_filename != filename and img_debugger:
            img_debugger.debug(f"Filename sanitized: '{filename}' → '{clean_filename}'")
        
        # Check for duplicates
        if has_entry_safe(img_file, clean_filename):
            if img_debugger:
                img_debugger.warning(f"Entry '{clean_filename}' already exists")
            return False
        
        # Create new entry
        entry = create_img_entry(clean_filename, data, img_file)
        if not entry:
            return False
        
        # Detect RW version for DFF/TXD files
        if clean_filename.lower().endswith(('.dff', '.txd')):
            try:
                from methods.detect_file_type_version import detect_rw_version_from_entry_data
                detect_rw_version_from_entry_data(entry, data[:16] if len(data) >= 16 else data)
            except ImportError:
                pass
        
        # Add to entries list
        if not hasattr(img_file, 'entries'):
            img_file.entries = []
        
        img_file.entries.append(entry)
        
        # Mark as modified
        if hasattr(img_file, 'modified'):
            img_file.modified = True
        
        if img_debugger:
            img_debugger.success(f"Added entry: {clean_filename} at offset {entry.offset}")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to add entry {filename}: {e}")
        else:
            print(f"[ERROR] add_entry_safe failed: {e}")
        return False


def remove_entry_safe(img_file, filename: str) -> bool: #vers 2
    """Safely remove entry from IMG file"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return False
        
        # Find and remove entry
        for i, entry in enumerate(img_file.entries):
            entry_name = getattr(entry, 'name', '')
            if entry_name.lower() == filename.lower():
                del img_file.entries[i]
                
                # Mark as modified
                if hasattr(img_file, 'modified'):
                    img_file.modified = True
                
                if img_debugger:
                    img_debugger.success(f"Removed entry: {filename}")
                return True
        
        if img_debugger:
            img_debugger.warning(f"Entry '{filename}' not found for removal")
        return False
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Error removing entry {filename}: {e}")
        else:
            print(f"[ERROR] remove_entry_safe failed: {e}")
        return False


def get_entry_safe(img_file, filename: str) -> Optional[Any]: #vers 2
    """Safely get entry by name"""
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


def has_entry_safe(img_file, filename: str) -> bool: #vers 2
    """Safely check if entry exists"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return False
        
        for entry in img_file.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name.lower() == filename.lower():
                return True
        
        return False
        
    except Exception:
        return False


def get_entry_by_index_safe(img_file, index: int) -> Optional[Any]: #vers 2
    """Safely get entry by index"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            return None
        
        if 0 <= index < len(img_file.entries):
            return img_file.entries[index]
        
        return None
        
    except Exception:
        return None


def calculate_next_offset(img_file) -> int: #vers 2
    """Calculate next available offset for new entry"""
    try:
        if not hasattr(img_file, 'entries') or not img_file.entries:
            # Check IMG version to determine starting offset
            if hasattr(img_file, 'version'):
                version_name = getattr(img_file.version, 'name', None) or str(img_file.version)
                if 'VERSION_2' in version_name or '2' in str(version_name):
                    return SECTOR_SIZE  # 2048 for V2
            return 0  # 0 for V1
        
        # Find the highest end offset
        max_offset = 0
        for entry in img_file.entries:
            entry_offset = getattr(entry, 'offset', 0)
            entry_size = getattr(entry, 'size', 0)
            end_offset = entry_offset + entry_size
            if end_offset > max_offset:
                max_offset = end_offset
        
        # Align to sector boundary
        return ((max_offset + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
        
    except Exception:
        return SECTOR_SIZE  # Safe fallback


def validate_entry_data(filename: str, data: bytes) -> Tuple[bool, str]: #vers 2
    """Validate entry filename and data"""
    try:
        # Check filename
        if not filename or len(filename.strip()) == 0:
            return False, "Filename cannot be empty"
        
        if len(filename) > MAX_FILENAME_LENGTH:
            return False, f"Filename too long (max {MAX_FILENAME_LENGTH} chars)"
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*\\/\r\n\t'
        if any(char in filename for char in invalid_chars):
            return False, f"Invalid characters in filename: {invalid_chars}"
        
        # Check data
        if not data:
            return False, "Data cannot be empty"
        
        if len(data) == 0:
            return False, "Data size is zero"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Validation error: {e}"


def sanitize_filename(filename: str) -> str: #vers 2
    """Sanitize filename for IMG entry"""
    try:
        if not filename:
            return "unknown"
        
        # Remove invalid characters
        invalid_chars = '<>:"|?*\\/\r\n\t'
        clean_name = ''.join(c for c in filename if c not in invalid_chars)
        
        # Trim to max length
        if len(clean_name) > MAX_FILENAME_LENGTH:
            name_part, ext_part = os.path.splitext(clean_name)
            if len(ext_part) > 0:
                max_name_len = MAX_FILENAME_LENGTH - len(ext_part)
                clean_name = name_part[:max_name_len] + ext_part
            else:
                clean_name = clean_name[:MAX_FILENAME_LENGTH]
        
        # Ensure not empty
        if not clean_name or clean_name.isspace():
            clean_name = "unknown"
        
        return clean_name
        
    except Exception:
        return "unknown"


def create_img_entry(filename: str, data: bytes, img_file) -> Optional[Any]: #vers 2
    """Create new IMG entry object with multiple fallbacks"""
    try:
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
                    self.actual_size = 0
                    self.actual_offset = 0
                    self.data = None
                    self.is_new_entry = True
                    self._cached_data = None
                
                def set_img_file(self, img_file):
                    self.img_file = img_file
            
            entry = SimpleIMGEntry()
        
        # Set entry properties
        entry.name = filename
        entry.size = len(data)
        entry.actual_size = len(data)
        entry.offset = calculate_next_offset(img_file)
        entry.actual_offset = entry.offset
        entry.is_new_entry = True
        
        # Store data
        if hasattr(entry, '_cached_data'):
            entry._cached_data = data
        elif hasattr(entry, 'data'):
            entry.data = data
        else:
            # Add data attribute manually
            entry.data = data
        
        # Set IMG file reference if method exists
        if hasattr(entry, 'set_img_file'):
            entry.set_img_file(img_file)
        
        return entry
        
    except Exception as e:
        print(f"[ERROR] create_img_entry failed: {e}")
        return None


def add_multiple_entries(img_file, entries: List[Any]) -> int: #vers 2
    """Add multiple entries to IMG file"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        added_count = 0
        
        if not hasattr(img_file, 'entries'):
            img_file.entries = []
        
        for entry in entries:
            entry_name = getattr(entry, 'name', '')
            if not entry_name:
                continue
            
            # Skip duplicates
            if has_entry_safe(img_file, entry_name):
                continue
            
            # Set IMG file reference
            if hasattr(entry, 'set_img_file'):
                entry.set_img_file(img_file)
            
            img_file.entries.append(entry)
            added_count += 1
        
        # Mark as modified
        if hasattr(img_file, 'modified'):
            img_file.modified = True
        
        if img_debugger:
            img_debugger.success(f"Added {added_count} entries")
        
        return added_count
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Batch add failed: {e}")
        else:
            print(f"[ERROR] add_multiple_entries failed: {e}")
        return 0


def import_file_to_img(img_file, file_path: str) -> bool: #vers 2
    """Import single file into IMG"""
    try:
        if not os.path.exists(file_path):
            return False
        
        filename = os.path.basename(file_path)
        
        # Read file data
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Use add_entry_safe method
        return add_entry_safe(img_file, filename, data)
        
    except Exception as e:
        print(f"[ERROR] import_file_to_img failed: {e}")
        return False


def import_directory_to_img(img_file, directory_path: str, recursive: bool = False) -> int: #vers 2
    """Import directory contents into IMG"""
    try:
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return 0
        
        imported_count = 0
        
        # Get file list
        if recursive:
            file_list = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_list.append(os.path.join(root, file))
        else:
            file_list = [
                os.path.join(directory_path, f)
                for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f))
            ]
        
        # Import each file
        for file_path in file_list:
            if import_file_to_img(img_file, file_path):
                imported_count += 1
        
        return imported_count
        
    except Exception as e:
        print(f"[ERROR] import_directory_to_img failed: {e}")
        return 0


def integrate_entry_operations(main_window) -> bool: #vers 2
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
        main_window.add_multiple_entries = lambda img_file, entries: add_multiple_entries(img_file, entries)
        main_window.import_file_to_img = lambda img_file, file_path: import_file_to_img(img_file, file_path)
        main_window.import_directory_to_img = lambda img_file, directory_path, recursive=False: import_directory_to_img(img_file, directory_path, recursive)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG entry operations integrated (updated)")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Entry operations integration failed: {e}")
        return False


# Export functions
__all__ = [
    'add_multiple_entries_batch',
    'add_entry_safe',
    'remove_entry_safe', 
    'get_entry_safe',
    'has_entry_safe',
    'get_entry_by_index_safe',
    'calculate_next_offset',
    'validate_entry_data',
    'sanitize_filename',
    'create_img_entry',
    'add_multiple_entries',
    'import_file_to_img',
    'import_directory_to_img',
    'integrate_entry_operations'
]
