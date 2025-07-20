#this belongs in components/ img_core_classes.py - Version: 3
# X-Seti - July16 2025 - Img Factory 1.5

"""
IMG Core Classes - Updated to use separate version creators
Removed embedded creation methods, now imports from version-specific files
"""

import os
import struct
import json
from typing import List, Optional, Dict, Any, BinaryIO
from pathlib import Path
from enum import Enum

# Import version-specific creators
from components.img_version1 import IMGVersion1Creator, create_version_1_img
from components.img_version2 import IMGVersion2Creator, create_version_2_img


class IMGVersion(Enum):
    """IMG file format versions"""
    UNKNOWN = 0
    VERSION_1 = 1  # GTA3, VC - separate DIR+IMG files
    VERSION_2 = 2  # SA, IV - single IMG file with VER2 header


class FileType(Enum):
    """File types found in IMG archives"""
    UNKNOWN = 0
    MODEL = 1      # .dff
    TEXTURE = 2    # .txd
    COLLISION = 3  # .col
    ANIMATION = 4  # .ifp
    AUDIO = 5      # .wav
    SCRIPT = 6     # .scm
    DATA = 7       # .dat, .cfg
    PLACEMENT = 8  # .ipl
    DEFINITION = 9 # .ide
    OTHER = 10


class CompressionType(Enum):
    """Compression types for IMG entries"""
    NONE = 0
    ZLIB = 1
    LZO_1X_1 = 2
    LZO_1X_999 = 3


class RecentFilesManager:
    """Manages recent files list for file dialogs"""
    
    def __init__(self, max_files=10):
        self.max_files = max_files
        self.recent_files = []
        self.settings_file = "recent_files.json"
        self._load_recent_files()
    
    def _load_recent_files(self):
        """Load recent files from settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.recent_files = data.get('recent_files', [])
        except Exception:
            self.recent_files = []
    
    def _save_recent_files(self):
        """Save recent files to settings"""
        try:
            data = {'recent_files': self.recent_files}
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def add_file(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # Keep only max_files entries
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[:self.max_files]
        
        self._save_recent_files()
    
    def get_recent_files(self):
        """Get list of recent files"""
        # Filter out files that no longer exist
        existing_files = [f for f in self.recent_files if os.path.exists(f)]
        if len(existing_files) != len(self.recent_files):
            self.recent_files = existing_files
            self._save_recent_files()
        return self.recent_files


class ValidationResult:
    """Results from entry validation"""
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)


class IMGEntry:
    """
    Represents a single file entry within an IMG archive
    """
    
    def __init__(self):
        self.name: str = ""
        self.extension: str = ""
        self.offset: int = 0          # Offset in bytes
        self.size: int = 0            # Size in bytes
        self.uncompressed_size: int = 0
        self.file_type: FileType = FileType.UNKNOWN
        self.compression_type: CompressionType = CompressionType.NONE
        self.rw_version: int = 0      # RenderWare version
        self.is_encrypted: bool = False
        self.is_new_entry: bool = False
        self.is_replaced: bool = False
        self.flags: int = 0
        self.compression_level = 0

        # Internal data cache
        self._cached_data: Optional[bytes] = None
        self._img_file: Optional['IMGFile'] = None
    
    def set_img_file(self, img_file: 'IMGFile'):
        """Set reference to parent IMG file"""
        self._img_file = img_file
    
    def get_offset_in_sectors(self) -> int:
        """Get offset in 2048-byte sectors"""
        return self.offset // 2048
    
    def get_size_in_sectors(self) -> int:
        """Get size in 2048-byte sectors (rounded up)"""
        return (self.size + 2047) // 2048
    
    def get_padded_size(self) -> int:
        """Get size padded to sector boundary"""
        return self.get_size_in_sectors() * 2048
    
    def is_compressed(self) -> bool:
        """Check if entry is compressed"""
        return self.compression_type != CompressionType.NONE
    
    def is_rw_file(self) -> bool:
        """Check if this is a RenderWare file (DFF/TXD)"""
        return self.file_type in [FileType.MODEL, FileType.TEXTURE]
    
    def get_file_type(self) -> FileType:
        """Get file type based on extension"""
        if not self.extension:
            return FileType.UNKNOWN
        
        ext = self.extension.lower()
        type_map = {
            'dff': FileType.MODEL,
            'txd': FileType.TEXTURE,
            'col': FileType.COLLISION,
            'ifp': FileType.ANIMATION,
            'wav': FileType.AUDIO,
            'scm': FileType.SCRIPT,
            'dat': FileType.DATA,
            'cfg': FileType.DATA,
            'ipl': FileType.PLACEMENT,
            'ide': FileType.DEFINITION
        }
        return type_map.get(ext, FileType.OTHER)
    
    def validate(self) -> ValidationResult:
        """Validate entry data"""
        result = ValidationResult()
        
        try:
            # Check name
            if not self.name or len(self.name.strip()) == 0:
                result.add_error("Entry name is empty")
            elif len(self.name) > 24:
                result.add_error("Entry name exceeds 24 characters")
            
            # Check size
            if self.size < 0:
                result.add_error("Entry size is negative")
            elif self.size == 0:
                result.add_warning("Entry size is zero")
            
            # Check offset
            if self.offset < 0:
                result.add_error("Entry offset is negative")
            
            # Validate compression
            if self.compression_type != CompressionType.NONE:
                if self.uncompressed_size <= 0:
                    result.add_error("Compressed entry has invalid uncompressed size")
                elif self.uncompressed_size <= self.size:
                    result.add_warning("Compressed entry may not be properly compressed")
            
            # Validate data if available
            if self._img_file:
                try:
                    data = self.get_data()
                    if len(data) != self.size:
                        result.add_warning(f"Entry {self.name} actual size differs from header")
                except Exception as e:
                    result.add_error(f"Cannot read data for {self.name}: {str(e)}")

        except Exception as e:
            result.add_error(f"Validation error for {self.name}: {str(e)}")

        return result
    
    def get_data(self) -> bytes:
        """Read entry data from IMG file"""
        if not self._img_file:
            raise ValueError("No IMG file reference set")
        
        return self._img_file.read_entry_data(self)
    
    def set_data(self, data: bytes):
        """Write entry data to IMG file"""
        if not self._img_file:
            raise ValueError("No IMG file reference set")
        
        self._img_file.write_entry_data(self, data)


class IMGFile:
    """
    Main IMG archive file handler - Updated to use version-specific creators
    """
    
    def __init__(self, file_path: str = ""):
        self.file_path: str = file_path
        self.version: IMGVersion = IMGVersion.UNKNOWN
        self.entries: List[IMGEntry] = []
        self.is_encrypted: bool = False
        self.platform: str = "PC"
        
        # File handles
        self._img_handle: Optional[BinaryIO] = None
        self._dir_handle: Optional[BinaryIO] = None
    
    def create_new(self, output_path: str, version: IMGVersion, **options) -> bool:
        """Create new IMG file with specified parameters - FIXED"""
        try:
            self.file_path = output_path
            self.version = version
            self.entries = []

            # Extract creation options
            initial_size_mb = options.get('initial_size_mb', 50)
            compression_enabled = options.get('compression_enabled', False)
            game_preset = options.get('game_preset', None)

            if version == IMGVersion.VERSION_1:
                # Use Version 1 creator
                creator = IMGVersion1Creator()
                success = creator.create_version_1(output_path, initial_size_mb)
                if success:
                    self.entries = creator.entries
                    self.file_path = creator.dir_path  # Store DIR file path for Version 1
                return success
                
            elif version == IMGVersion.VERSION_2:
                # Use Version 2 creator - FIXED METHOD CALL
                creator = IMGVersion2Creator()
                success = creator.create_version_2(output_path, initial_size_mb, compression_enabled)
                if success:
                    self.entries = creator.entries
                    self.file_path = creator.file_path
                return success
                
            else:
                print(f"❌ Unsupported IMG version: {version}")
                return False

        except Exception as e:
            print(f"❌ Error creating IMG file: {e}")
            return False

    def read_entry_data(self, entry: IMGEntry) -> bytes:
        """Read data for a specific entry"""
        try:
            if self.version == IMGVersion.VERSION_1:
                # Read from .img file
                img_path = self.file_path.replace('.dir', '.img')
                with open(img_path, 'rb') as f:
                    f.seek(entry.offset)
                    return f.read(entry.size)
            else:
                # Read from single .img file
                with open(self.file_path, 'rb') as f:
                    f.seek(entry.offset)
                    return f.read(entry.size)
        except Exception as e:
            raise RuntimeError(f"Failed to read entry data: {e}")

    def write_entry_data(self, entry: IMGEntry, data: bytes):
        """Write data for a specific entry"""
        try:
            if self.version == IMGVersion.VERSION_1:
                # Write to .img file
                img_path = self.file_path.replace('.dir', '.img')
                with open(img_path, 'r+b') as f:
                    f.seek(entry.offset)
                    f.write(data)
            else:
                # Write to single .img file
                with open(self.file_path, 'r+b') as f:
                    f.seek(entry.offset)
                    f.write(data)
        except Exception as e:
            raise RuntimeError(f"Failed to write entry data: {e}")

    def get_creation_info(self) -> Dict[str, Any]:
        """Get information about the IMG file"""
        if not self.file_path or not os.path.exists(self.file_path):
            return {}
        
        try:
            file_size = os.path.getsize(self.file_path)
            return {
                'path': self.file_path,
                'size_bytes': file_size,
                'size_mb': file_size / (1024 * 1024),
                'entries_count': len(self.entries),
                'version': self.version.name,
                'format': f'IMG Version {self.version.value}'
            }
        except Exception:
            return {}


# Convenience functions for external use
def create_img_file(output_path: str, version: IMGVersion, **options) -> bool:
    """Create IMG file using appropriate version creator"""
    img = IMGFile()
    return img.create_new(output_path, version, **options)


class Platform(Enum):
    """Platform types for IMG files"""
    PC = 0
    XBOX = 1
    PS2 = 2
    MOBILE = 3


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# Placeholder classes for compatibility with imgfactory.py imports
class IMGEntriesTable:
    """Placeholder for IMG entries table"""
    pass

class FilterPanel:
    """Placeholder for filter panel"""
    pass

class IMGFileInfoPanel:
    """Placeholder for IMG file info panel"""
    pass

class TabFilterWidget:
    """Placeholder for tab filter widget"""
    pass


def integrate_filtering(main_window):
    """Placeholder for filtering integration"""
    pass

def create_entries_table_panel(main_window):
    """Placeholder for entries table panel creation"""
    pass


# Export classes and functions
__all__ = [
    'IMGVersion',
    'FileType', 
    'CompressionType',
    'Platform',
    'IMGEntry',
    'IMGFile',
    'ValidationResult',
    'RecentFilesManager',
    'create_img_file',
    'format_file_size',
    'IMGEntriesTable',
    'FilterPanel', 
    'IMGFileInfoPanel',
    'TabFilterWidget',
    'integrate_filtering',
    'create_entries_table_panel'
]
    