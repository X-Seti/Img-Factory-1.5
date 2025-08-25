#this belongs in components/img_core_classes.py - Version: 9
# X-Seti - August25 2025 - IMG Factory 1.5 - IMG Core Classes Complete Combined

"""
IMG Core Classes - Complete combined version with all functionality
Merged from img_core_classes.py and img_core_classes_old.py (55KB version)
"""

import os
import struct
import json
import shutil
import tempfile
import math
from enum import Enum
from typing import List, Dict, Optional, Any, Union, BinaryIO, Tuple
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QLineEdit, QGroupBox, QLabel, QHeaderView,
    QAbstractItemView, QListWidget, QListWidgetItem, QSplitter)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# Import existing RW version functions
from core.rw_versions import get_rw_version_name, parse_rw_version, get_model_format_version
from components.img_debug_functions import img_debugger

# Constants
V1_SIGNATURE = b"VER1"
V2_SIGNATURE = b"VER2"
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24

##Methods list -
# add_entry
# add_multiple_entries
# calculate_next_offset
# create_entries_table_panel
# create_img_file
# detect_img_platform
# detect_img_version
# format_file_size
# get_entry
# get_img_platform_info
# get_platform_specific_specs
# has_entry
# import_directory
# import_file
# integrate_filtering
# integrate_fixed_add_entry_methods
# populate_table_with_sample_data
# rebuild
# remove_entry
# sanitize_filename

##Classes -
# CompressionType
# FileType
# FilterPanel
# IMGEntriesTable
# IMGEntry
# IMGFile
# IMGFileInfoPanel
# IMGPlatform
# IMGVersion
# Platform
# RecentFilesManager
# TabFilterWidget
# ValidationResult

class IMGVersion(Enum): #vers 1
    """IMG Archive Version Types"""
    VERSION_1 = 1    # DIR/IMG pair (GTA3, VC)
    VERSION_2 = 2    # Single IMG file (SA)
    UNKNOWN = 0

class IMGPlatform(Enum): #vers 1
    """Platform types for IMG files"""
    PC = "pc"
    PS2 = "ps2" 
    XBOX = "xbox"
    ANDROID = "android"
    IOS = "ios"
    PSP = "psp"
    UNKNOWN = "unknown"

class Platform(Enum): #vers 1
    """Platform enumeration (legacy compatibility)"""
    PC = "PC"
    CONSOLE = "CONSOLE"
    MOBILE = "MOBILE"

class FileType(Enum): #vers 1
    """File types within IMG archives"""
    DFF = "dff"      # Model files
    TXD = "txd"      # Texture dictionary
    COL = "col"      # Collision data
    IPL = "ipl"      # Item placement
    IDE = "ide"      # Item definition
    IFP = "ifp"      # Animation
    SCM = "scm"      # Script
    WAV = "wav"      # Audio
    UNKNOWN = "unknown"

class CompressionType(Enum): #vers 1
    """Compression types"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    UNKNOWN = -1

class ValidationResult: #vers 1
    """Validation result container"""
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, message: str): #vers 1
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str): #vers 1
        self.warnings.append(message)

# Platform detection functions
def detect_img_platform(file_path: str) -> tuple: #vers 1
    """Detect IMG platform from file path and properties"""
    try:
        # Basic filename analysis
        filename = os.path.basename(file_path).lower()
        
        # Platform hints from filename
        if 'android' in filename or 'mobile' in filename:
            return (IMGPlatform.ANDROID, {'method': 'filename'})
        elif 'ps2' in filename or 'playstation' in filename:
            return (IMGPlatform.PS2, {'method': 'filename'})
        elif 'xbox' in filename:
            return (IMGPlatform.XBOX, {'method': 'filename'})
        elif 'psp' in filename:
            return (IMGPlatform.PSP, {'method': 'filename'})
        
        # Default to PC
        return (IMGPlatform.PC, {'method': 'default'})
        
    except Exception:
        return (IMGPlatform.UNKNOWN, {'method': 'error'})

def get_platform_specific_specs(platform: IMGPlatform) -> Dict[str, Any]: #vers 1
    """Get platform-specific specifications"""
    specs = {
        IMGPlatform.PC: {
            'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
            'compression_supported': True,
            'encryption_supported': False,
            'sector_size': 2048
        },
        IMGPlatform.PS2: {
            'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
            'compression_supported': False,
            'encryption_supported': False,
            'sector_size': 2048
        },
        IMGPlatform.XBOX: {
            'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
            'compression_supported': False,
            'encryption_supported': False,
            'sector_size': 2048
        },
        IMGPlatform.ANDROID: {
            'max_file_size': 1 * 1024 * 1024 * 1024,  # 1GB
            'compression_supported': True,
            'encryption_supported': False,
            'sector_size': 2048
        },
        IMGPlatform.PSP: {
            'max_file_size': 512 * 1024 * 1024,  # 512MB
            'compression_supported': False,
            'encryption_supported': False,
            'sector_size': 2048
        }
    }
    return specs.get(platform, specs[IMGPlatform.PC])

def get_img_platform_info(file_path: str) -> Dict[str, Any]: #vers 1
    """Get platform information for IMG file"""
    platform, detection_info = detect_img_platform(file_path)
    return {
        'platform': platform.value,
        'detected_from': 'filename_analysis',
        'supported_features': {
            'compression': platform in [IMGPlatform.PC, IMGPlatform.ANDROID],
            'encryption': False,
            'large_files': platform != IMGPlatform.PSP
        }
    }

class IMGEntry: #vers 4
    """Represents a single file entry within an IMG archive"""
    
    def __init__(self):
        self.name: str = ""
        self.extension: str = ""
        self.offset: int = 0          # Offset in bytes
        self.size: int = 0            # Size in bytes
        self.actual_offset: int = 0   # For new format compatibility
        self.actual_size: int = 0     # For new format compatibility
        self.uncompressed_size: int = 0
        self.file_type: FileType = FileType.UNKNOWN
        self.compression_type: CompressionType = CompressionType.NONE
        self.rw_version: int = 0      # RenderWare version
        self.rw_version_name: str = "" # Human readable version name
        self.is_encrypted: bool = False
        self.is_new_entry: bool = False
        self.is_replaced: bool = False
        self.flags: int = 0
        self.compression_level = 0

        # Internal data cache
        self._cached_data: Optional[bytes] = None
        self._img_file: Optional['IMGFile'] = None
        self._version_detected: bool = False
    
    def set_img_file(self, img_file: 'IMGFile'): #vers 1
        """Set reference to parent IMG file"""
        self._img_file = img_file

    def detect_file_type_and_version(self): #vers 2
        """Detect file type and RW version from file data"""
        try:
            # Extract extension from name
            if '.' in self.name:
                self.extension = self.name.split('.')[-1].lower()
                
                # Set file type based on extension
                if self.extension == 'dff':
                    self.file_type = FileType.DFF
                elif self.extension == 'txd':
                    self.file_type = FileType.TXD
                elif self.extension == 'col':
                    self.file_type = FileType.COL
                elif self.extension == 'ipl':
                    self.file_type = FileType.IPL
                elif self.extension == 'ide':
                    self.file_type = FileType.IDE
                elif self.extension == 'ifp':
                    self.file_type = FileType.IFP
                elif self.extension == 'scm':
                    self.file_type = FileType.SCM
                elif self.extension == 'wav':
                    self.file_type = FileType.WAV

            # Detect RW version for applicable files
            if self.file_type in [FileType.DFF, FileType.TXD] and not self._version_detected:
                self._detect_rw_version_from_data()

        except Exception as e:
            img_debugger.error(f"Error detecting file type for {self.name}: {e}")

    def _detect_rw_version_from_data(self): #vers 1
        """Detect RW version from file header data"""
        try:
            file_data = self._read_header_data(16)  # Read first 16 bytes
            if not file_data or len(file_data) < 8:
                return

            # Try to parse RW version from header
            version_value, version_name = parse_rw_version(file_data)
            if version_value and version_name:
                self.rw_version = version_value
                self.rw_version_name = version_name
                self._version_detected = True
                img_debugger.success(f"Detected RW version {version_name} (0x{version_value:X}) for {self.name}")
            else:
                # Fallback: try reading from different offset
                if len(file_data) >= 8:
                    try:
                        alt_version = struct.unpack('<I', file_data[4:8])[0]
                        if 0x30000 <= alt_version <= 0x40000:  # Valid RW version range
                            self.rw_version = alt_version
                            self.rw_version_name = get_rw_version_name(alt_version)
                            self._version_detected = True
                            img_debugger.success(f"Detected RW version {self.rw_version_name} (alt method) for {self.name}")
                    except:
                        pass

        except Exception as e:
            img_debugger.error(f"Error detecting RW version for {self.name}: {e}")

    def _read_header_data(self, bytes_to_read: int) -> Optional[bytes]: #vers 1
        """Read file header data from IMG file"""
        try:
            if not self._img_file or not self._img_file.file_path:
                return None

            # Determine which file to read from based on IMG version
            if self._img_file.version == IMGVersion.VERSION_1:
                # Read from .img file (companion to .dir)
                img_path = self._img_file.file_path.replace('.dir', '.img')
                if not os.path.exists(img_path):
                    return None
                file_path = img_path
            else:
                # Read from single .img file
                file_path = self._img_file.file_path

            with open(file_path, 'rb') as f:
                f.seek(self.offset)
                return f.read(bytes_to_read)

        except Exception:
            return None

    def get_version_text(self): #vers 1
        """Get version text for display"""
        return self.rw_version_name if self.rw_version_name else "Unknown"

class IMGFile: #vers 5
    """Main IMG archive file handler - COMPLETE with all methods"""
    
    def __init__(self, file_path: str = ""):
        self.file_path: str = file_path
        self.version: IMGVersion = IMGVersion.UNKNOWN
        self.platform: IMGPlatform = IMGPlatform.UNKNOWN
        self.platform_specs: Dict[str, Any] = {}
        self.entries: List[IMGEntry] = []
        self.is_open: bool = False
        self.total_size: int = 0
        self.creation_time: Optional[float] = None
        self.modification_time: Optional[float] = None

        # File handles
        self._img_handle: Optional[BinaryIO] = None
        self._dir_handle: Optional[BinaryIO] = None
    
    def _sanitize_filename(self, filename: str) -> str: #vers 1
        """Sanitize filename to prevent corruption"""
        # Remove any null bytes and truncate to max length
        clean_name = filename.replace('\x00', '').strip()
        if len(clean_name) > MAX_FILENAME_LENGTH - 1:  # Leave space for null terminator
            clean_name = clean_name[:MAX_FILENAME_LENGTH - 1]
        return clean_name

    def create_new(self, output_path: str, version: IMGVersion, **options) -> bool: #vers 2
        """Create new IMG file with specified parameters"""
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
                from core.img_version1 import IMGVersion1Creator
                creator = IMGVersion1Creator()
                success = creator.create_version_1(output_path, initial_size_mb)
                if success:
                    self.entries = creator.entries
                    self.file_path = creator.dir_path  # Store DIR file path for Version 1
                return success
                
            elif version == IMGVersion.VERSION_2:
                # Use Version 2 creator
                from core.img_version2 import IMGVersion2Creator
                creator = IMGVersion2Creator()
                success = creator.create_version_2(output_path, initial_size_mb, compression_enabled)
                if success:
                    self.entries = creator.entries
                    self.is_open = True
                return success
                
            return False

        except Exception as e:
            img_debugger.error(f"Error creating IMG file: {e}")
            return False

    def detect_version(self) -> IMGVersion: #vers 4
        """Detect IMG version and platform from file"""
        try:
            if not os.path.exists(self.file_path):
                return IMGVersion.UNKNOWN

            # Platform detection first
            detected_platform, detection_info = detect_img_platform(self.file_path)
            self.platform = detected_platform
            self.platform_specs = get_platform_specific_specs(detected_platform)

            # Check if it's a .dir file (Version 1)
            if self.file_path.lower().endswith('.dir'):
                img_path = self.file_path[:-4] + '.img'
                if os.path.exists(img_path):
                    self.version = IMGVersion.VERSION_1
                    return IMGVersion.VERSION_1

            # Check if it's a single .img file (Version 2)
            if self.file_path.lower().endswith('.img'):
                try:
                    with open(self.file_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'VER2':
                            self.version = IMGVersion.VERSION_2
                            return IMGVersion.VERSION_2
                        # Could be Version 1 IMG file without DIR
                        self.version = IMGVersion.VERSION_1
                        return IMGVersion.VERSION_1
                except:
                    pass

        except Exception as e:
            img_debugger.error(f"Error detecting IMG version: {e}")

        self.version = IMGVersion.UNKNOWN
        return IMGVersion.UNKNOWN

    def open(self) -> bool: #vers 5
        """Open and parse IMG file"""
        try:
            if not os.path.exists(self.file_path):
                return False

            # Detect version first
            self.detect_version()

            # Load based on version
            if self.version == IMGVersion.VERSION_1:
                success = self._load_version1()
            elif self.version == IMGVersion.VERSION_2:
                success = self._load_version2()
            else:
                return False

            if success:
                self.is_open = True
                # Set IMG file reference for all entries
                for entry in self.entries:
                    entry.set_img_file(self)
                    # DISABLED: Don't auto-detect during file opening to prevent freezing
                    # Detection will be done on-demand when needed for display
                    # entry.detect_file_type_and_version()
                
                img_debugger.success(f"Opened IMG file with {len(self.entries)} entries")
                return True

        except Exception as e:
            img_debugger.error(f"Error opening IMG file: {e}")
            return False

        return False

    def _load_version1(self) -> bool: #vers 1
        """Load Version 1 IMG (DIR/IMG pair)"""
        try:
            dir_path = self.file_path
            img_path = self.file_path[:-4] + '.img'
            
            if not os.path.exists(dir_path) or not os.path.exists(img_path):
                return False

            with open(dir_path, 'rb') as f:
                dir_data = f.read()

            # Parse DIR entries (32 bytes each)
            entry_count = len(dir_data) // 32
            self.entries = []
            
            for i in range(entry_count):
                offset = i * 32
                entry_data = dir_data[offset:offset+32]

                if len(entry_data) < 32:
                    break

                # Parse entry: offset(4), size(4), name(24)
                entry_offset, entry_size = struct.unpack('<II', entry_data[:8])
                entry_name = entry_data[8:32].rstrip(b'\x00').decode('ascii', errors='ignore')

                if entry_name:
                    entry = IMGEntry()
                    entry.name = entry_name
                    entry.offset = entry_offset * SECTOR_SIZE  # Convert sectors to bytes
                    entry.size = entry_size * SECTOR_SIZE
                    entry.actual_offset = entry.offset
                    entry.actual_size = entry.size
                    entry.set_img_file(self)
                    self.entries.append(entry)

            return True

        except Exception as e:
            img_debugger.error(f"Error opening Version 1 IMG: {e}")
            return False

    def _load_version2(self) -> bool: #vers 1
        """Load Version 2 IMG (single file)"""
        try:
            with open(self.file_path, 'rb') as f:
                # Read header
                header = f.read(4)
                if header != V2_SIGNATURE:
                    return False

                entry_count = struct.unpack('<I', f.read(4))[0]

                # Read entries
                self.entries = []
                for i in range(entry_count):
                    # Read entry: offset(4), size(4), name(24)
                    entry_data = f.read(32)
                    if len(entry_data) < 32:
                        break

                    offset_sectors, size_sectors = struct.unpack('<II', entry_data[:8])
                    name_bytes = entry_data[8:32]

                    # Convert values
                    actual_offset = offset_sectors * SECTOR_SIZE
                    actual_size = size_sectors * SECTOR_SIZE

                    # Extract name
                    name_end = name_bytes.find(b'\x00')
                    if name_end != -1:
                        name = name_bytes[:name_end].decode('ascii', errors='ignore')
                    else:
                        name = name_bytes.decode('ascii', errors='ignore').rstrip('\x00')

                    # Create entry
                    entry = IMGEntry()
                    entry.name = name
                    entry.offset = actual_offset
                    entry.size = actual_size
                    entry.actual_offset = actual_offset
                    entry.actual_size = actual_size

                    self.entries.append(entry)

            return True

        except Exception:
            return False

    def read_entry_data(self, entry: IMGEntry) -> bytes: #vers 1
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

    def write_entry_data(self, entry: IMGEntry, data: bytes): #vers 1
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

    def close(self): #vers 1
        """Close IMG file and cleanup resources"""
        if self._img_handle:
            self._img_handle.close()
            self._img_handle = None
        if self._dir_handle:
            self._dir_handle.close()
            self._dir_handle = None
        
        self.is_open = False
        self.entries.clear()

    def add_entry(self, filename: str, data: bytes, auto_save: bool = True) -> bool: #vers 3
        """Add new entry to IMG file - ENHANCED with corruption prevention"""
        try:
            # CRITICAL: Sanitize filename to prevent corruption
            clean_filename = self._sanitize_filename(filename)
            if clean_filename != filename:
                img_debugger.debug(f"Filename sanitized: '{filename}' → '{clean_filename}'")
                filename = clean_filename

            img_debugger.debug(f"add_entry called: {filename} ({len(data)} bytes)")
            img_debugger.debug(f"Current IMG entries before: {len(self.entries)}")

            # Check if entry already exists
            if self.has_entry(filename):
                img_debugger.warning(f"Entry '{filename}' already exists")
                return False

            # Create new entry
            entry = IMGEntry()
            entry.name = filename
            entry.size = len(data)
            entry.actual_size = len(data)
            entry.offset = self.calculate_next_offset()
            entry.actual_offset = entry.offset
            entry._cached_data = data
            entry.is_new_entry = True
            entry.set_img_file(self)

            # Add to entries list
            self.entries.append(entry)
            
            img_debugger.success(f"Added entry: {filename} at offset {entry.offset}")
            return True

        except Exception as e:
            img_debugger.error(f"Failed to add entry {filename}: {e}")
            return False

    def remove_entry(self, name: str) -> bool: #vers 1
        """Remove entry from IMG file"""
        try:
            for i, entry in enumerate(self.entries):
                if entry.name.lower() == name.lower():
                    del self.entries[i]
                    img_debugger.success(f"Removed entry: {name}")
                    return True
            img_debugger.warning(f"Entry '{name}' not found for removal")
            return False
        except Exception as e:
            img_debugger.error(f"Error removing entry {name}: {e}")
            return False

    def has_entry(self, name: str) -> bool: #vers 1
        """Check if entry exists"""
        return any(entry.name.lower() == name.lower() for entry in self.entries)

    def get_entry(self, name: str) -> Optional[IMGEntry]: #vers 1
        """Get entry by name"""
        for entry in self.entries:
            if entry.name.lower() == name.lower():
                return entry
        return None

    def calculate_next_offset(self) -> int: #vers 1
        """Calculate next available offset"""
        if not self.entries:
            return 2048 if self.version == IMGVersion.VERSION_2 else 0
        
        max_offset = 0
        for entry in self.entries:
            end_offset = entry.offset + entry.size
            if end_offset > max_offset:
                max_offset = end_offset
        
        # Align to sector boundary
        return ((max_offset + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE

    def add_multiple_entries(self, entries: List[IMGEntry]) -> int: #vers 1
        """Add multiple entries"""
        try:
            added_count = 0
            for entry in entries:
                if self.has_entry(entry.name):
                    continue
                entry.set_img_file(self)
                self.entries.append(entry)
                added_count += 1
            img_debugger.success(f"Added {added_count} entries")
            return added_count
        except Exception as e:
            img_debugger.error(f"Batch add failed: {e}")
            return 0

    def import_file(self, file_path: str) -> bool: #vers 1
        """Import file into IMG"""
        try:
            filename = os.path.basename(file_path)

            # Read file data
            with open(file_path, 'rb') as f:
                data = f.read()

            # Use add_entry method
            return self.add_entry(filename, data)

        except Exception as e:
            img_debugger.error(f"Failed to import file {file_path}: {e}")
            return False

    def import_directory(self, directory_path: str) -> Tuple[int, int]: #vers 2
        """Import all files from directory"""
        success_count = 0
        error_count = 0
        
        try:
            if not os.path.exists(directory_path):
                img_debugger.error(f"Directory not found: {directory_path}")
                return (0, 1)

            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if self.import_file(file_path):
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        img_debugger.error(f"Error importing {file_path}: {e}")
                        error_count += 1

            img_debugger.success(f"Imported {success_count} files, {error_count} errors")
            return (success_count, error_count)

        except Exception as e:
            img_debugger.error(f"Error importing directory: {e}")
            return (0, 1)

    def rebuild(self) -> bool: #vers 3
        """Rebuild IMG file with current entries"""
        try:
            if self.version == IMGVersion.VERSION_1:
                return self._rebuild_version1()
            elif self.version == IMGVersion.VERSION_2:
                return self._rebuild_version2()
            else:
                img_debugger.error("Unknown IMG version for rebuild")
                return False

        except Exception as e:
            img_debugger.error(f"Error rebuilding IMG file: {e}")
            return False

    def _rebuild_version1(self) -> bool: #vers 1
        """Rebuild Version 1 IMG (DIR/IMG pair)"""
        try:
            dir_path = self.file_path
            img_path = self.file_path[:-4] + '.img'

            # Create backup
            if os.path.exists(dir_path):
                shutil.copy2(dir_path, dir_path + '.bak')
            if os.path.exists(img_path):
                shutil.copy2(img_path, img_path + '.bak')

            # Prepare data for all entries
            entry_data_list = []
            current_offset = 0
            
            for entry in self.entries:
                if entry._cached_data:
                    data = entry._cached_data
                else:
                    # Read existing data
                    data = self.read_entry_data(entry)
                
                entry_data_list.append(data)
                entry.offset = current_offset
                entry.size = len(data)

                # Align to sector boundary
                aligned_size = ((len(data) + 2047) // 2048) * 2048
                current_offset += aligned_size

            # Write DIR file
            with open(dir_path, 'wb') as f:
                for entry in self.entries:
                    # Convert to sectors
                    offset_sectors = entry.offset // 2048
                    size_sectors = ((entry.size + 2047) // 2048)

                    # Pack entry: offset(4), size(4), name(24)
                    entry_data = struct.pack('<II', offset_sectors, size_sectors)
                    name_bytes = entry.name.encode('ascii')[:24].ljust(24, b'\x00')
                    entry_data += name_bytes

                    f.write(entry_data)

            # Write IMG file
            with open(img_path, 'wb') as f:
                for i, data in enumerate(entry_data_list):
                    f.seek(self.entries[i].offset)
                    f.write(data)

                    # Pad to sector boundary
                    current_pos = f.tell()
                    sector_end = ((current_pos + 2047) // 2048) * 2048
                    if current_pos < sector_end:
                        f.write(b'\x00' * (sector_end - current_pos))

            img_debugger.success(f"Rebuilt DIR/IMG pair: {len(self.entries)} entries")
            return True

        except Exception as e:
            img_debugger.error(f"Failed to rebuild Version 1 IMG: {e}")
            return False

    def _rebuild_version2(self) -> bool: #vers 1
        """Rebuild Version 2 IMG (single file)"""
        try:
            # Create backup
            if os.path.exists(self.file_path):
                shutil.copy2(self.file_path, self.file_path + '.bak')

            # Calculate header size
            entry_count = len(self.entries)
            header_size = 8 + (entry_count * 32)  # 8 bytes header + 32 bytes per entry
            header_sectors = ((header_size + SECTOR_SIZE - 1) // SECTOR_SIZE)
            data_start_offset = header_sectors * SECTOR_SIZE

            # Prepare data for all entries
            entry_data_list = []
            current_offset = data_start_offset
            
            for entry in self.entries:
                if entry._cached_data:
                    data = entry._cached_data
                else:
                    # Read existing data
                    data = self.read_entry_data(entry)
                
                entry_data_list.append(data)
                entry.offset = current_offset
                entry.size = len(data)

                # Align to sector boundary
                aligned_size = ((len(data) + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
                current_offset += aligned_size

            # Write IMG file
            with open(self.file_path, 'wb') as f:
                # Write header
                f.write(V2_SIGNATURE)
                f.write(struct.pack('<I', entry_count))

                # Write directory entries
                for entry in self.entries:
                    offset_sectors = entry.offset // SECTOR_SIZE
                    size_sectors = ((entry.size + SECTOR_SIZE - 1) // SECTOR_SIZE)
                    
                    entry_data = struct.pack('<II', offset_sectors, size_sectors)
                    name_bytes = entry.name.encode('ascii')[:24].ljust(24, b'\x00')
                    entry_data += name_bytes
                    
                    f.write(entry_data)

                # Pad header to sector boundary
                current_pos = f.tell()
                if current_pos < data_start_offset:
                    f.write(b'\x00' * (data_start_offset - current_pos))

                # Write file data
                for i, data in enumerate(entry_data_list):
                    f.seek(self.entries[i].offset)
                    f.write(data)

                    # Pad to sector boundary
                    current_pos = f.tell()
                    sector_end = ((current_pos + SECTOR_SIZE - 1) // SECTOR_SIZE) * SECTOR_SIZE
                    if current_pos < sector_end:
                        f.write(b'\x00' * (sector_end - current_pos))

            img_debugger.success(f"Rebuilt Version 2 IMG: {len(self.entries)} entries")
            return True

        except Exception as e:
            img_debugger.error(f"Failed to rebuild Version 2 IMG: {e}")
            return False

    def get_creation_info(self) -> Dict[str, Any]: #vers 1
        """Get information about the IMG file"""
        if not self.file_path or not os.path.exists(self.file_path):
            return {}
        
        stat = os.stat(self.file_path)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'entries': len(self.entries),
            'version': self.version.name if self.version != IMGVersion.UNKNOWN else 'Unknown'
        }

# Fixed methods for integration
def add_entry(self, filename: str, data: bytes, auto_save: bool = True) -> bool: #vers 1
    """Fixed add_entry method for integration"""
    return self.add_entry(filename, data, auto_save)

def calculate_next_offset(self) -> int: #vers 1
    """Fixed calculate_next_offset method for integration"""
    return self.calculate_next_offset()

def remove_entry(self, name: str) -> bool: #vers 1
    """Fixed remove_entry method for integration"""
    return self.remove_entry(name)

def has_entry(self, name: str) -> bool: #vers 1
    """Fixed has_entry method for integration"""
    return self.has_entry(name)

def get_entry(self, name: str) -> Optional[IMGEntry]: #vers 1
    """Fixed get_entry method for integration"""
    return self.get_entry(name)

def add_multiple_entries(self, entries: List[IMGEntry]) -> int: #vers 1
    """Fixed add_multiple_entries method for integration"""
    return self.add_multiple_entries(entries)

def integrate_fixed_add_entry_methods(img_file_class): #vers 1
    """Integrate all fixed methods into IMGFile class"""
    try:
        # Add the fixed methods to the class
        img_file_class.add_entry = add_entry
        img_file_class.calculate_next_offset = calculate_next_offset
        img_file_class.remove_entry = remove_entry
        img_file_class.has_entry = has_entry
        img_file_class.get_entry = get_entry
        img_file_class.add_multiple_entries = add_multiple_entries

        img_debugger.success("Fixed add_entry methods integrated into IMGFile class")
        return True

    except Exception as e:
        img_debugger.error(f"Failed to integrate fixed add_entry methods: {e}")
        return False

# GUI Components
class IMGEntriesTable(QTableWidget): #vers 3
    """Enhanced table widget for IMG entries"""
    entry_selected = pyqtSignal(IMGEntry)
    entry_double_clicked = pyqtSignal(IMGEntry)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        self.entries = []
        self._filter_text = ""
    
    def setup_table(self): #vers 1
        """Setup table structure"""
        headers = ["Name", "Extension", "Size", "Offset", "Type", "RW Version", "Compression", "Status"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Configure table
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # Configure column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Extension
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # RW Version
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Compression
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Status
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_double_clicked)

    def populate_entries(self, entries: List[IMGEntry]): #vers 2
        """Populate table with IMG entries"""
        self.entries = entries
        self.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            name_item = QTableWidgetItem(entry.name)
            if entry.is_new_entry:
                name_item.setBackground(QColor(200, 255, 200))  # Light green
            elif entry.is_replaced:
                name_item.setBackground(QColor(255, 255, 200))  # Light yellow
            self.setItem(row, 0, name_item)
            
            # Extension
            self.setItem(row, 1, QTableWidgetItem(entry.extension.upper()))
            
            # Size
            self.setItem(row, 2, QTableWidgetItem(format_file_size(entry.size)))
            
            # Offset
            self.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:08X}"))
            
            # Type
            self.setItem(row, 4, QTableWidgetItem(entry.file_type.value.upper()))
            
            # RW Version
            self.setItem(row, 5, QTableWidgetItem(entry.get_version_text()))
            
            # Compression
            compression_text = entry.compression_type.name if entry.compression_type != CompressionType.NONE else "None"
            self.setItem(row, 6, QTableWidgetItem(compression_text))
            
            # Status
            status = "New" if entry.is_new_entry else ("Modified" if entry.is_replaced else "OK")
            self.setItem(row, 7, QTableWidgetItem(status))

    def apply_filter(self, filter_text: str): #vers 1
        """Apply filter to table entries"""
        self._filter_text = filter_text.lower()
        
        for row in range(self.rowCount()):
            should_show = True
            if self._filter_text:
                name_item = self.item(row, 0)
                if name_item:
                    should_show = self._filter_text in name_item.text().lower()
            
            self.setRowHidden(row, not should_show)

    def _on_selection_changed(self): #vers 1
        """Handle selection change"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.entries):
            self.entry_selected.emit(self.entries[current_row])

    def _on_double_clicked(self, item): #vers 1
        """Handle double click"""
        if item:
            row = item.row()
            if 0 <= row < len(self.entries):
                self.entry_double_clicked.emit(self.entries[row])

class FilterPanel(QWidget): #vers 2
    """Filter panel for entries"""
    filter_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup filter UI"""
        layout = QVBoxLayout(self)
        
        # File type filter
        type_group = QGroupBox("File Type")
        type_layout = QHBoxLayout(type_group)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['All Files', 'Models (DFF)', 'Textures (TXD)', 'Collision (COL)', 'Animations (IFP)', 'Scripts (SCM)', 'Audio (WAV)'])
        self.type_combo.currentTextChanged.connect(self._on_filter_changed)
        type_layout.addWidget(self.type_combo)
        
        # Search filter
        search_group = QGroupBox("Search")
        search_layout = QHBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search entries...")
        self.search_edit.textChanged.connect(self._on_filter_changed)
        search_layout.addWidget(self.search_edit)
        
        layout.addWidget(type_group)
        layout.addWidget(search_group)

    def _on_filter_changed(self): #vers 1
        """Handle filter change"""
        filter_text = self.search_edit.text()
        self.filter_changed.emit(filter_text)

class IMGFileInfoPanel(QWidget): #vers 1
    """Information panel for IMG file details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel("No IMG file loaded")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

    def update_info(self, img_file: IMGFile): #vers 1
        """Update information display"""
        if not img_file or not img_file.is_open:
            self.info_label.setText("No IMG file loaded")
            return
        
        info = img_file.get_creation_info()
        filename = os.path.basename(img_file.file_path)
        
        info_text = f"""
        <b>File:</b> {filename}<br>
        <b>Version:</b> {info.get('version', 'Unknown')}<br>
        <b>Entries:</b> {info.get('entries', 0)}<br>
        <b>Size:</b> {format_file_size(info.get('size', 0))}<br>
        <b>Platform:</b> {img_file.platform.value.upper()}
        """
        
        self.info_label.setText(info_text.strip())

class TabFilterWidget(QWidget): #vers 1
    """Tab-specific filter widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        layout = QHBoxLayout(self)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['All Files', 'Models (DFF)', 'Textures (TXD)', 'Collision (COL)', 'Animations (IFP)'])
        layout.addWidget(self.filter_combo)

class RecentFilesManager: #vers 1
    """Recent files manager"""
    
    def __init__(self, max_files=10):
        self.max_files = max_files
        self.recent_files = []
        self.settings_file = os.path.join(os.path.expanduser("~"), ".imgfactory_recent.json")
        self.load_recent_files()

    def load_recent_files(self): #vers 1
        """Load recent files from settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.recent_files = json.load(f)
        except Exception:
            self.recent_files = []

    def save_recent_files(self): #vers 1
        """Save recent files to settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.recent_files, f, indent=2)
        except Exception:
            pass

    def add_recent_file(self, file_path: str): #vers 1
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # Keep only max_files
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[:self.max_files]
        
        self.save_recent_files()

# Utility functions
def format_file_size(size_bytes: int) -> str: #vers 2
    """Format file size for display"""
    if size_bytes == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            if unit == 'B':
                return f"{size_bytes:,} {unit}"
            else:
                return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def detect_img_version(file_path: str) -> IMGVersion: #vers 1
    """Detect IMG version from file"""
    img_file = IMGFile(file_path)
    return img_file.detect_version()

def create_img_file(output_path: str, version: IMGVersion, **options) -> bool: #vers 2
    """Create IMG file using appropriate version creator"""
    img = IMGFile()
    return img.create_new(output_path, version, **options)

def create_entries_table_panel(main_window): #vers 4
    """Create the complete entries table panel"""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)

    # IMG file information
    info_group = QGroupBox("📁 IMG File Information")
    info_layout = QVBoxLayout(info_group)

    main_window.file_info_panel = IMGFileInfoPanel()
    info_layout.addWidget(main_window.file_info_panel)

    layout.addWidget(info_group)

    # Filter panel
    filter_group = QGroupBox("🔍 Filter & Search")
    filter_layout = QVBoxLayout(filter_group)

    main_window.filter_panel = FilterPanel()
    filter_layout.addWidget(main_window.filter_panel)

    layout.addWidget(filter_group)

    # Entries table
    entries_group = QGroupBox("📋 Archive Entries")
    entries_layout = QVBoxLayout(entries_group)

    main_window.entries_table = IMGEntriesTable()
    entries_layout.addWidget(main_window.entries_table)

    layout.addWidget(entries_group)

    # Connect filter to table
    main_window.filter_panel.filter_changed.connect(main_window.entries_table.apply_filter)

    # Connect table signals to main window if methods exist
    if hasattr(main_window, 'on_entry_double_clicked'):
        try:
            main_window.entries_table.entry_double_clicked.disconnect()
        except:
            pass
        main_window.entries_table.entry_double_clicked.connect(main_window.on_entry_double_clicked)

    return panel

def integrate_filtering(main_window): #vers 2
    """Integrate filtering functionality into main window"""
    try:
        # Create filter widget if not exists
        if not hasattr(main_window, 'filter_panel'):
            main_window.filter_panel = FilterPanel(main_window)

        # Connect filter widget to table if both exist
        if hasattr(main_window, 'entries_table') and hasattr(main_window.filter_panel, 'filter_changed'):
            main_window.filter_panel.filter_changed.connect(main_window.entries_table.apply_filter)

        img_debugger.success("Filtering system integrated")
        return True
    except Exception as e:
        img_debugger.error(f"Error integrating filtering: {e}")
        return False

def populate_table_with_sample_data(table): #vers 3
    """Populate table with sample data for testing"""
    sample_entries = [
        {"name": "player.dff", "extension": "DFF", "size": 250880, "offset": 0x2000, "version": "RW 3.6"},
        {"name": "player.txd", "extension": "TXD", "size": 524288, "offset": 0x42000, "version": "RW 3.6"},
        {"name": "vehicle.col", "extension": "COL", "size": 131072, "offset": 0x84000, "version": "COL 2"},
        {"name": "dance.ifp", "extension": "IFP", "size": 1258291, "offset": 0xA4000, "version": "IFP 1"},
    ]

    # Convert to mock entry objects
    class MockEntry:
        def __init__(self, data): #vers 1
            self.name = data["name"]
            self.extension = data["extension"]
            self.size = data["size"]
            self.offset = data["offset"]
            self._version = data["version"]
            self.is_new_entry = False
            self.is_replaced = False
            self.compression_type = CompressionType.NONE
            self.file_type = FileType.UNKNOWN

        def get_version_text(self): #vers 1
            return self._version

    mock_entries = [MockEntry(data) for data in sample_entries]
    
    # Use the populate_entries method if it exists
    if hasattr(table, 'populate_entries'):
        table.populate_entries(mock_entries)

# Export classes and functions
__all__ = [
    # Enums
    'IMGVersion', 'FileType', 'CompressionType', 'Platform', 'IMGPlatform',
    
    # Core classes
    'IMGEntry', 'IMGFile', 'ValidationResult',
    
    # GUI components
    'IMGEntriesTable', 'FilterPanel', 'IMGFileInfoPanel', 'TabFilterWidget',
    
    # Utility classes
    'RecentFilesManager',
    
    # Functions
    'create_img_file', 'format_file_size', 'detect_img_version',
    'create_entries_table_panel', 'integrate_filtering', 
    'populate_table_with_sample_data', 'get_img_platform_info',
    
    # Platform functions
    'detect_img_platform', 'get_platform_specific_specs',
    
    # Integration functions
    'integrate_fixed_add_entry_methods',
    'add_entry', 'calculate_next_offset', 'remove_entry', 
    'has_entry', 'get_entry', 'add_multiple_entries'
]