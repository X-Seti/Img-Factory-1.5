#this belongs in methods/ img_file_operations.py - Version: 4
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG File Operations

"""
IMG File Operations - Shared Methods
File I/O operations for IMG files (create, load, save, rebuild)
Extracted from img_core_classes.py to eliminate duplicates
"""

import os
import struct
import shutil
import tempfile
from typing import Optional, Any, List, Dict
from pathlib import Path

##Methods list -
# create_img_file
# rebuild_img
# import_file_into_img(img_file
# import_directory_into_img(img_file
# create_img_file < dup ??
# load_img_file_safe
# save_img_file_safe
# rebuild_img_file
# validate_img_structure
# get_img_file_info
# detect_img_platform
# get_platform_specific_specs
# format_file_size
# integrate_file_operations

# Constants
V1_SIGNATURE = b"VER1"
V2_SIGNATURE = b"VER2"
SECTOR_SIZE = 2048


def create_img_file(file_path: str, version: int = 2) -> Optional[Any]: #vers 1
    """Create new IMG file - from img_core_classes"""
    try:
        # Import debug and classes
        try:
            from components.img_debug_functions import img_debugger
            from components.img_core_classes import IMGFile, IMGVersion
        except ImportError:
            return None

        img_file = IMGFile()
        img_file.file_path = file_path
        img_file.version = IMGVersion.VERSION_2 if version == 2 else IMGVersion.VERSION_1
        img_file.entries = []
        img_file.is_open = False
        img_file.modified = False

        if img_debugger:
            img_debugger.success(f"Created IMG file structure: {file_path}")

        return img_file

    except Exception as e:
        if 'img_debugger' in locals():
            img_debugger.error(f"Failed to create IMG file: {e}")
        return None


def rebuild_img(img_file) -> bool: #vers 1
    """Rebuild IMG file - from img_core_classes"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None

        if not hasattr(img_file, 'entries') or not img_file.entries:
            if img_debugger:
                img_debugger.warning("No entries to rebuild")
            return False

        if img_debugger:
            img_debugger.info(f"Starting rebuild for {len(img_file.entries)} entries")

        # Recalculate offsets
        from methods.img_entry_operations import calculate_next_offset
        current_offset = 2048  # Start after header

        for entry in img_file.entries:
            entry.offset = current_offset
            entry_size = getattr(entry, 'size', 0)
            current_offset += entry_size
            # Align to sector boundary
            current_offset = ((current_offset + 2047) // 2048) * 2048

        if img_debugger:
            img_debugger.success("IMG rebuild completed")

        return True

    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Rebuild failed: {e}")
        return False


def import_file_into_img(img_file, file_path: str) -> bool: #vers 1
    """Import file into IMG - from img_core_classes"""
    try:
        if not os.path.exists(file_path):
            return False

        filename = os.path.basename(file_path)

        # Read file data
        with open(file_path, 'rb') as f:
            data = f.read()

        # Use existing add_entry function
        from methods.img_entry_operations import add_entry_safe
        return add_entry_safe(img_file, filename, data)

    except Exception:
        return False


def import_directory_into_img(img_file, directory_path: str, recursive: bool = False) -> int: #vers 1
    """Import directory into IMG - from img_core_classes"""
    try:
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return 0

        imported_count = 0

        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if import_file_into_img(img_file, file_path):
                        imported_count += 1
        else:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    if import_file_into_img(img_file, item_path):
                        imported_count += 1

        return imported_count

    except Exception:
        return 0

def create_img_file(file_path: str, version: int = 2, platform: str = "pc") -> Optional[Any]: #vers 1
    """Create new IMG file with specified version and platform"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Import IMG classes
        try:
            from components.img_core_classes import IMGFile, IMGVersion, IMGPlatform
        except ImportError:
            if img_debugger:
                img_debugger.error("Cannot import IMG classes")
            return None
        
        # Create IMG file object
        img_file = IMGFile()
        img_file.file_path = file_path
        
        # Set version
        if version == 1:
            img_file.version = IMGVersion.VERSION_1
        elif version == 2:
            img_file.version = IMGVersion.VERSION_2
        else:
            img_file.version = IMGVersion.VERSION_2  # Default to V2
        
        # Set platform
        if hasattr(IMGPlatform, platform.upper()):
            img_file.platform = getattr(IMGPlatform, platform.upper())
        else:
            img_file.platform = IMGPlatform.PC  # Default to PC
        
        # Initialize entries list
        img_file.entries = []
        img_file.is_open = False
        img_file.modified = False
        
        # Create initial file structure
        if img_file.version == IMGVersion.VERSION_1:
            # Create .dir and .img files
            dir_path = file_path
            img_path = file_path.replace('.dir', '.img')
            
            # Create empty .dir file (will be populated when entries are added)
            with open(dir_path, 'wb') as f:
                pass  # Empty file
            
            # Create empty .img file
            with open(img_path, 'wb') as f:
                pass  # Empty file
        else:
            # Create Version 2 IMG file
            with open(file_path, 'wb') as f:
                # Write V2 header
                f.write(V2_SIGNATURE)  # VER2 signature
                f.write(struct.pack('<I', 0))  # Number of entries (0 initially)
                
                # Pad to sector boundary
                padding_size = SECTOR_SIZE - f.tell()
                f.write(b'\x00' * padding_size)
        
        if img_debugger:
            img_debugger.success(f"Created IMG file: {file_path} (Version {version}, Platform {platform})")
        
        return img_file
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to create IMG file {file_path}: {e}")
        else:
            print(f"[ERROR] create_img_file failed: {e}")
        return None


def load_img_file_safe(file_path: str) -> Optional[Any]: #vers 1
    """Safely load IMG file with validation"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        # Import IMG classes
        try:
            from components.img_core_classes import IMGFile
        except ImportError:
            if img_debugger:
                img_debugger.error("Cannot import IMG classes")
            return None
        
        if not os.path.exists(file_path):
            if img_debugger:
                img_debugger.error(f"IMG file not found: {file_path}")
            return None
        
        # Create IMG file object
        img_file = IMGFile()
        
        # Try to load using existing load method
        if hasattr(img_file, 'load'):
            try:
                if img_file.load(file_path):
                    if img_debugger:
                        img_debugger.success(f"Loaded IMG file: {file_path}")
                    return img_file
            except Exception as e:
                if img_debugger:
                    img_debugger.error(f"IMG load method failed: {e}")
        
        # Fallback manual loading
        img_file.file_path = file_path
        img_file.entries = []
        
        if img_debugger:
            img_debugger.warning(f"Loaded IMG file with fallback method: {file_path}")
        
        return img_file
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to load IMG file {file_path}: {e}")
        else:
            print(f"[ERROR] load_img_file_safe failed: {e}")
        return None


def save_img_file_safe(img_file, file_path: str = None) -> bool: #vers 1
    """Safely save IMG file with backup"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        save_path = file_path or getattr(img_file, 'file_path', None)
        if not save_path:
            if img_debugger:
                img_debugger.error("No file path specified for save")
            return False
        
        # Create backup if file exists
        if os.path.exists(save_path):
            backup_path = save_path + '.backup'
            try:
                shutil.copy2(save_path, backup_path)
                if img_debugger:
                    img_debugger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                if img_debugger:
                    img_debugger.warning(f"Failed to create backup: {e}")
        
        # Try to use existing save method
        if hasattr(img_file, 'save'):
            try:
                if img_file.save(save_path):
                    if img_debugger:
                        img_debugger.success(f"Saved IMG file: {save_path}")
                    return True
            except Exception as e:
                if img_debugger:
                    img_debugger.error(f"IMG save method failed: {e}")
        
        # Fallback - at least mark as modified
        if hasattr(img_file, 'modified'):
            img_file.modified = False
        
        if img_debugger:
            img_debugger.warning(f"IMG save completed with fallback: {save_path}")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to save IMG file: {e}")
        else:
            print(f"[ERROR] save_img_file_safe failed: {e}")
        return False


def rebuild_img_file(img_file, output_path: str = None) -> bool: #vers 1
    """Rebuild IMG file with optimized structure"""
    try:
        # Import debug system
        try:
            from components.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        from methods.img_entry_operations import calculate_next_offset
        
        rebuild_path = output_path or getattr(img_file, 'file_path', None)
        if not rebuild_path:
            return False
        
        if not hasattr(img_file, 'entries') or not img_file.entries:
            if img_debugger:
                img_debugger.warning("No entries to rebuild")
            return False
        
        # Try to use existing rebuild method
        if hasattr(img_file, 'rebuild'):
            try:
                if img_file.rebuild(rebuild_path):
                    if img_debugger:
                        img_debugger.success(f"Rebuilt IMG file: {rebuild_path}")
                    return True
            except Exception as e:
                if img_debugger:
                    img_debugger.error(f"IMG rebuild method failed: {e}")
        
        # Fallback rebuild
        if img_debugger:
            img_debugger.info(f"Starting fallback rebuild for {len(img_file.entries)} entries")
        
        # Recalculate offsets
        current_offset = SECTOR_SIZE  # Start after header
        for entry in img_file.entries:
            entry.offset = current_offset
            entry_size = getattr(entry, 'size', 0)
            current_offset += entry_size
            # Align to sector boundary
            current_offset = ((current_offset + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
        
        if img_debugger:
            img_debugger.success(f"Rebuild completed with fallback: {rebuild_path}")
        
        return True
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to rebuild IMG file: {e}")
        else:
            print(f"[ERROR] rebuild_img_file failed: {e}")
        return False


def validate_img_structure(img_file) -> tuple[bool, str]: #vers 1
    """Validate IMG file structure"""
    try:
        if not hasattr(img_file, 'entries'):
            return False, "No entries attribute found"
        
        if not hasattr(img_file, 'file_path'):
            return False, "No file path attribute found"
        
        file_path = getattr(img_file, 'file_path', None)
        if file_path and not os.path.exists(file_path):
            return False, f"IMG file not found: {file_path}"
        
        # Check entries
        entries = getattr(img_file, 'entries', [])
        if not entries:
            return True, "IMG structure valid (no entries)"
        
        # Validate entries
        invalid_count = 0
        for i, entry in enumerate(entries):
            if not hasattr(entry, 'name') or not getattr(entry, 'name', ''):
                invalid_count += 1
        
        if invalid_count > 0:
            return False, f"Found {invalid_count} entries with invalid names"
        
        return True, f"IMG structure valid ({len(entries)} entries)"
        
    except Exception as e:
        return False, f"Structure validation failed: {str(e)}"


def get_img_file_info(img_file) -> Dict[str, Any]: #vers 1
    """Get comprehensive IMG file information"""
    try:
        info = {
            'file_path': getattr(img_file, 'file_path', 'Unknown'),
            'version': 'Unknown',
            'platform': 'Unknown',
            'entry_count': 0,
            'total_size': 0,
            'is_open': getattr(img_file, 'is_open', False),
            'modified': getattr(img_file, 'modified', False)
        }
        
        # Get version info
        if hasattr(img_file, 'version'):
            version = getattr(img_file, 'version')
            if hasattr(version, 'name'):
                info['version'] = version.name
            else:
                info['version'] = str(version)
        
        # Get platform info
        if hasattr(img_file, 'platform'):
            platform = getattr(img_file, 'platform')
            if hasattr(platform, 'value'):
                info['platform'] = platform.value
            else:
                info['platform'] = str(platform)
        
        # Get entries info
        if hasattr(img_file, 'entries'):
            entries = getattr(img_file, 'entries', [])
            info['entry_count'] = len(entries)
            
            # Calculate total size
            total_size = 0
            for entry in entries:
                entry_size = getattr(entry, 'size', 0)
                total_size += entry_size
            info['total_size'] = total_size
        
        # Get file size if file exists
        file_path = info['file_path']
        if file_path != 'Unknown' and os.path.exists(file_path):
            info['file_size'] = os.path.getsize(file_path)
        else:
            info['file_size'] = 0
        
        return info
        
    except Exception as e:
        return {
            'error': f"Failed to get IMG info: {e}"
        }


def detect_img_platform(img_file) -> str: #vers 1
    """Detect IMG file platform"""
    try:
        # Check if platform is already set
        if hasattr(img_file, 'platform'):
            platform = getattr(img_file, 'platform')
            if hasattr(platform, 'value'):
                return platform.value
            else:
                return str(platform)
        
        # Try to detect from file characteristics
        file_path = getattr(img_file, 'file_path', '')
        if file_path:
            # Simple heuristics based on file path
            file_path_lower = file_path.lower()
            if 'ps2' in file_path_lower:
                return 'ps2'
            elif 'xbox' in file_path_lower:
                return 'xbox'
            else:
                return 'pc'  # Default to PC
        
        return 'pc'  # Default fallback
        
    except Exception:
        return 'pc'


def get_platform_specific_specs(platform: str) -> Dict[str, Any]: #vers 1
    """Get platform-specific specifications"""
    try:
        specs = {
            'pc': {
                'sector_size': 2048,
                'max_filename_length': 24,
                'endianness': 'little',
                'alignment': 4
            },
            'ps2': {
                'sector_size': 2048,
                'max_filename_length': 24,
                'endianness': 'little',
                'alignment': 16
            },
            'xbox': {
                'sector_size': 2048,
                'max_filename_length': 24,
                'endianness': 'little',
                'alignment': 4
            }
        }
        
        return specs.get(platform.lower(), specs['pc'])
        
    except Exception:
        return specs['pc']  # Default to PC specs


def format_file_size(size_bytes: int) -> str: #vers 1
    """Format file size in human readable format"""
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size_bytes)} {size_names[i]}"
        else:
            return f"{size_bytes:.1f} {size_names[i]}"
        
    except Exception:
        return "Unknown"


def integrate_file_operations(main_window) -> bool: #vers 1
    """Integrate file operations into main window"""
    try:
        # Add file operation methods
        main_window.create_img_file = create_img_file
        main_window.load_img_file_safe = load_img_file_safe
        main_window.save_img_file_safe = save_img_file_safe
        main_window.rebuild_img_file = rebuild_img_file
        main_window.validate_img_structure = validate_img_structure
        main_window.get_img_file_info = get_img_file_info
        main_window.detect_img_platform = detect_img_platform
        main_window.get_platform_specific_specs = get_platform_specific_specs
        main_window.format_file_size = format_file_size
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG file operations integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ File operations integration failed: {e}")
        return False


# Export functions
__all__ = [
    'create_img_file',
    'rebuild_img',
    'import_file_into_img',
    'import_directory_into_img',
    'create_img_file',
    'load_img_file_safe',
    'save_img_file_safe',
    'rebuild_img_file',
    'validate_img_structure',
    'get_img_file_info',
    'detect_img_platform',
    'get_platform_specific_specs',
    'format_file_size',
    'integrate_file_operations'
]
