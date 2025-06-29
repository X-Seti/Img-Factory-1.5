#this belongs in components/ img_core_classes.py - version 9
# X-Seti - June29 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory - Core IMG Format Classes and Table Components
Clean implementation of IMG file handling and UI table components for Qt6
Consolidated from table_filter.py and table_view.py
"""

import struct
import os
import zlib
import hashlib

from enum import Enum
from typing import List, Optional, BinaryIO, Dict, Tuple
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QHeaderView, QAbstractItemView, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class IMGVersion(Enum):
    """IMG Archive version types"""
    # Primary names (cleaner)
    UNKNOWN = 0
    VERSION_1 = 1        # GTA III/VC - DIR/IMG pair
    VERSION_2 = 2        # GTA SA - Single file
    VERSION_3 = 3        # GTA IV - Advanced
    FASTMAN92 = 4        # Modded version
    STORIES = 5          # Stories version

    # Aliases for backward compatibility
    IMG_UNKNOWN = UNKNOWN
    IMG_1 = VERSION_1
    IMG_2 = VERSION_2
    IMG_3 = VERSION_3
    IMG_FASTMAN92 = FASTMAN92
    IMG_STORIES = STORIES


class Platform(Enum):
    """Platform enumeration"""
    PC = "PC"
    XBOX = "XBOX"
    PS2 = "PS2"
    PSP = "PSP"
    MOBILE = "Mobile"

class FileType(Enum):
    """File types found in IMG archives"""
    UNKNOWN = 0
    MODEL = 1      # DFF files
    TEXTURE = 2    # TXD files
    COLLISION = 3  # COL files
    ANIMATION = 4  # IFP files
    AUDIO = 5      # WAV files
    SCRIPT = 6     # SCM files
    WATER = 7      # Water files
    HANDLING = 8   # Handling files
    PARTICLES = 9  # Particle files

class CompressionType(Enum):
    """Compression algorithm types"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    LZO_1X_999 = 3
    UNKNOWN = 255

class IMGValidationResult:
    """Results from IMG file validation"""
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.corrupt_entries: List[str] = []

    def get_summary(self) -> str:
        """Get validation summary"""
        summary = []
        if self.errors:
            summary.append(f"Errors: {len(self.errors)}")
        if self.warnings:
            summary.append(f"Warnings: {len(self.warnings)}")
        if self.corrupt_entries:
            summary.append(f"Corrupt entries: {len(self.corrupt_entries)}")
        return ", ".join(summary) if summary else "No issues found"


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

class IMGEntry:
    """Represents a single entry in an IMG file"""

    def __init__(self, name: str = "", offset: int = 0, size: int = 0):
        self.name = name
        self.offset = offset  # Offset in bytes
        self.size = size      # Size in bytes
        self.extension = self._extract_extension()

        # Metadata
        self.is_compressed = False
        self.compression_type = CompressionType.NONE
        self.is_encrypted = False
        self.is_new_entry = False
        self.is_replaced = False
        self.file_creation_date = 0
        self.rw_version = 0
        self.raw_version = 0
        self.crc32 = 0
        self.md5_hash = ""

        # Version 3 specific
        self.rage_resource_type = None
        self.flags = 0

        # Fastman92 specific
        self.uncompressed_size = 0
        self.compression_level = 0

        # Internal data cache
        self._cached_data: Optional[bytes] = None
        self._img_file_ref: Optional['IMGFile'] = None

    def _populate_entry_details_after_load(img_file):
        """Call this after loading entries to populate RW versions"""
        for entry in img_file.entries:
            try:
                entry.populate_entry_details()
            except Exception as e:
                print(f"Warning: Could not detect details for {entry.name}: {e}")

    # Enhanced get_version_text with better RW version mapping
    def get_version_text_enhanced(self) -> str:
        """Enhanced version text with better RW version mapping"""
        if self.file_type == FileType.MODEL or self.file_type == FileType.TEXTURE:
            # Enhanced RW version mapping
            rw_versions = {
                0x0800FFFF: "3.0.0.0",
                0x1003FFFF: "3.1.0.1",
                0x1005FFFF: "3.2.0.0",
                0x1400FFFF: "3.4.0.3",
                0x1803FFFF: "3.6.0.3",
                0x1C020037: "3.7.0.2"
            }

            if self.rw_version == 0:
                # Try to detect version if not cached
                self.rw_version = self.detect_rw_version()

            if self.rw_version in rw_versions:
                return rw_versions[self.rw_version]
            elif self.rw_version > 0:
                return f"RW {hex(self.rw_version)}"
            else:
                return "RW Unknown"
        elif self.file_type == FileType.COLLISION:
            return f"COL {self.rw_version}" if self.rw_version > 0 else "COL Unknown"
        elif self.file_type == FileType.ANIMATION:
            return f"IFP {self.rw_version}" if self.rw_version > 0 else "IFP Unknown"
        return "Unknown"


    def _extract_extension(self) -> str:
        """Extract file extension from name"""
        if '.' in self.name:
            return self.name.split('.')[-1].upper()
        return ""

    def get_file_type(self) -> FileType:
        """Get file type based on extension"""
        ext_map = {
            'DFF': FileType.MODEL,
            'TXD': FileType.TEXTURE,
            'COL': FileType.COLLISION,
            'IFP': FileType.ANIMATION,
            'WAV': FileType.AUDIO,
            'SCM': FileType.SCRIPT,
            'CS': FileType.SCRIPT,
            'FXT': FileType.SCRIPT,
        }
        return ext_map.get(self.extension, FileType.UNKNOWN)

    def get_offset_in_sectors(self) -> int:
        """Get offset in 2048-byte sectors"""
        return self.offset // 2048

    def get_size_in_sectors(self) -> int:
        """Get size in 2048-byte sectors (rounded up)"""
        return (self.size + 2047) // 2048

    def get_padded_size(self) -> int:
        """Get padded size (2048-byte aligned)"""
        return self.get_size_in_sectors() * 2048

    def get_data(self) -> bytes:
        """Get entry data from IMG file"""
        if self._cached_data:
            return self._cached_data

        if not self._img_file_ref:
            raise RuntimeError("IMG file reference not set")

        return self._img_file_ref.get_entry_data(self)

    def set_data(self, data: bytes):
        """Set entry data (cache for new/replaced entries)"""
        self._cached_data = data
        self.size = len(data)
        self.is_new_entry = True
        self._calculate_checksums()

    def _calculate_checksums(self):
        """Calculate CRC32 and MD5 for the entry data"""
        if self._cached_data:
            self.crc32 = zlib.crc32(self._cached_data) & 0xffffffff
            self.md5_hash = hashlib.md5(self._cached_data).hexdigest()

    def validate(self) -> IMGValidationResult:
        """Validate entry integrity"""
        result = IMGValidationResult()

        try:
            # Check basic properties
            if not self.name:
                result.errors.append("Entry has no name")
                result.is_valid = False

            if self.size <= 0:
                result.errors.append(f"Entry {self.name} has invalid size: {self.size}")
                result.is_valid = False

            if self.offset < 0:
                result.errors.append(f"Entry {self.name} has invalid offset: {self.offset}")
                result.is_valid = False

            # Try to get data and validate
            if self._img_file_ref:
                try:
                    data = self.get_data()
                    if len(data) != self.size:
                        result.warnings.append(f"Entry {self.name} actual size differs from header")
                except Exception as e:
                    result.errors.append(f"Cannot read data for {self.name}: {str(e)}")
                    result.is_valid = False

        except Exception as e:
            result.errors.append(f"Validation error for {self.name}: {str(e)}")
            result.is_valid = False

        return result

    def get_version_text(self) -> str:
        """Get human-readable version information"""
        if self.get_file_type() == FileType.MODEL or self.get_file_type() == FileType.TEXTURE:
            # RW version mapping (simplified)
            rw_versions = {
                0x0800FFFF: "3.0.0.0",
                0x1003FFFF: "3.1.0.1", 
                0x1005FFFF: "3.2.0.0",
                0x1400FFFF: "3.4.0.3",
                0x1803FFFF: "3.6.0.3"
            }
            return rw_versions.get(self.rw_version, f"RW {hex(self.rw_version)}")
        elif self.get_file_type() == FileType.COLLISION:
            return f"COL {self.rw_version}"
        elif self.get_file_type() == FileType.ANIMATION:
            return f"IFP {self.rw_version}"
        return "Unknown"

def detect_rw_version(self) -> int:
    """Detect RenderWare version from entry data"""
    if not self._img_file or not self.is_rw_file():
        return 0

    try:
        # Read first 12 bytes to get RW header
        data = self.get_data()
        if len(data) < 12:
            return 0

        # Parse RW chunk header: chunk_type, chunk_size, rw_version
        chunk_type, chunk_size, rw_version = struct.unpack('<III', data[:12])

        # Validate it's a proper RW chunk
        if self.file_type == FileType.MODEL and chunk_type not in [0x10, 0x0E]:  # Clump or Atomic
            return 0
        elif self.file_type == FileType.TEXTURE and chunk_type != 0x16:  # Texture Dictionary
            return 0

        return rw_version

    except Exception:
        return 0

def populate_entry_details(self):
    """Populate additional entry details like RW version and file type"""
    # Detect file type from extension
    self.file_type = self._detect_file_type()

    # For RW files, detect version from data
    if self.is_rw_file():
        self.rw_version = self.detect_rw_version()

def _detect_file_type(self) -> FileType:
    """Detect file type from extension"""
    if not self.extension:
        return FileType.UNKNOWN

    ext_upper = self.extension.upper()
    file_type_map = {
        'DFF': FileType.MODEL,
        'TXD': FileType.TEXTURE,
        'COL': FileType.COLLISION,
        'IFP': FileType.ANIMATION,
        'WAV': FileType.AUDIO,
        'SCM': FileType.SCRIPT
    }

    return file_type_map.get(ext_upper, FileType.UNKNOWN)

class IMGFile:
    """Main IMG file handler supporting all versions"""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.version = IMGVersion.UNKNOWN
        self.platform = Platform.PC
        self.entries: List[IMGEntry] = []
        self.is_encrypted = False
        self.encryption_key = b""
        self.total_file_size = 0
        self.header_size = 0
        self.entries_area_size = 0

        # File handles
        self._img_file: Optional[BinaryIO] = None
        self._dir_file: Optional[BinaryIO] = None

        # Modification tracking
        self.is_modified = False
        self.new_entries: List[IMGEntry] = []
        self.removed_entries: List[str] = []

        # Statistics
        self.total_entries = 0
        self.total_size_bytes = 0
        self.fragmentation_percentage = 0.0

        # Compression settings
        self.compression_enabled = False
        self.compression_level = 6

        if file_path:
            self.detect_version()

    def detect_version(self) -> IMGVersion:
        """Detect IMG version from file"""
        if not os.path.exists(self.file_path):
            self.version = IMGVersion.UNKNOWN
            return self.version

        try:
            with open(self.file_path, 'rb') as f:
                header = f.read(16)

            if len(header) < 4:
                self.version = IMGVersion.UNKNOWN
                return self.version

            signature = header[:4]

            # Check for Version 2 (GTA SA)
            if signature == b'VER2':
                self.version = IMGVersion.VERSION_2
                return self.version

            # Check for Fastman92
            if signature == b'VERF':
                self.version = IMGVersion.FASTMAN92
                return self.version

            # Check for Version 3 (GTA IV)
            try:
                sig_uint = struct.unpack('<I', signature)[0]
                if sig_uint == 0xA94E2A52:
                    self.version = IMGVersion.VERSION_3
                    return self.version
            except:
                pass

            # Check for Version 1 (DIR file exists)
            dir_path = self.file_path.replace('.img', '.dir')
            if os.path.exists(dir_path):
                self.version = IMGVersion.VERSION_1
                return self.version

            # Check for Stories format
            if self._detect_stories_format():
                self.version = IMGVersion.STORIES
                return self.version

        except Exception as e:
            print(f"Error detecting IMG version: {e}")

        self.version = IMGVersion.UNKNOWN
        return self.version

    def _detect_stories_format(self) -> bool:
        """Detect if this is a Stories format IMG"""
        try:
            with open(self.file_path, 'rb') as f:
                # Stories format has specific header patterns
                header = f.read(32)
                # Implementation would check for Stories-specific patterns
                return False  # Placeholder
        except:
            return False

    def open(self) -> bool:
        """Open IMG file for reading"""
        try:
            if self.version == IMGVersion.VERSION_1:
                return self._open_version1()
            elif self.version == IMGVersion.VERSION_2:
                return self._open_version2()
            elif self.version == IMGVersion.VERSION_3:
                return self._open_version3()
            elif self.version == IMGVersion.FASTMAN92:
                return self._open_fastman92()
            elif self.version == IMGVersion.STORIES:
                return self._open_stories()
            else:
                print(f"Unsupported IMG version: {self.version}")
                return False
        except Exception as e:
            print(f"Error opening IMG file: {e}")
            return False

    def _open_version1(self) -> bool:
        """Open IMG Version 1 (DIR + IMG pair)"""
        try:
            dir_path = self.file_path.replace('.img', '.dir')
            if not os.path.exists(dir_path):
                return False

            # Open DIR file
            self._dir_file = open(dir_path, 'rb')
            self._img_file = open(self.file_path, 'rb')

            # Read entries from DIR file
            self.entries = []
            while True:
                entry_data = self._dir_file.read(32)  # Each DIR entry is 32 bytes
                if len(entry_data) != 32:
                    break

                # Parse DIR entry
                offset, size = struct.unpack('<II', entry_data[:8])
                name = entry_data[8:32].rstrip(b'\x00').decode('ascii', errors='ignore')

                if name:  # Skip empty entries
                    entry = IMGEntry(name, offset * 2048, size * 2048)
                    entry._img_file_ref = self
                    self.entries.append(entry)

            self.total_entries = len(self.entries)
            return True

        except Exception as e:
            print(f"Error opening Version 1 IMG: {e}")
            return False

    def _open_version2(self) -> bool:
        """Open IMG Version 2 (GTA SA)"""
        try:
            self._img_file = open(self.file_path, 'rb')

            # Read header
            signature = self._img_file.read(4)
            if signature != b'VER2':
                return False

            entry_count = struct.unpack('<I', self._img_file.read(4))[0]

            # Read entries
            self.entries = []
            for i in range(entry_count):
                entry_data = self._img_file.read(32)
                if len(entry_data) != 32:
                    break

                offset, size = struct.unpack('<II', entry_data[:8])
                name = entry_data[8:32].rstrip(b'\x00').decode('ascii', errors='ignore')

                if name:
                    entry = IMGEntry(name, offset * 2048, size * 2048)
                    entry._img_file_ref = self
                    self.entries.append(entry)

            self.total_entries = len(self.entries)
            return True

        except Exception as e:
            print(f"Error opening Version 2 IMG: {e}")
            return False

    def _open_version3(self) -> bool:
        """Open IMG Version 3 (GTA IV)"""
        try:
            self._img_file = open(self.file_path, 'rb')

            # Read and parse Version 3 header
            header = self._img_file.read(32)
            signature, version, entry_count, table_size = struct.unpack('<IIII', header[:16])

            if signature != 0xA94E2A52:
                return False

            # Check for encryption
            if version & 0x80000000:
                self.is_encrypted = True
                # Handle encrypted format
                return self._handle_encrypted_v3()

            # Read entries table
            self.entries = []
            for i in range(entry_count):
                entry_data = self._img_file.read(16)  # V3 entries are 16 bytes
                if len(entry_data) != 16:
                    break

                offset, size, name_offset, flags = struct.unpack('<IIII', entry_data)

                # Read name from string table
                current_pos = self._img_file.tell()
                self._img_file.seek(32 + table_size + name_offset)
                name = self._read_null_terminated_string()
                self._img_file.seek(current_pos)

                if name:
                    entry = IMGEntry(name, offset, size)
                    entry.flags = flags
                    entry._img_file_ref = self
                    self.entries.append(entry)

            self.total_entries = len(self.entries)
            return True

        except Exception as e:
            print(f"Error opening Version 3 IMG: {e}")
            return False

    def _open_fastman92(self) -> bool:
        """Open Fastman92 format"""
        try:
            self._img_file = open(self.file_path, 'rb')

            # Read Fastman92 header
            signature = self._img_file.read(4)
            if signature != b'VERF':
                return False

            version, entry_count = struct.unpack('<II', self._img_file.read(8))

            # Read entries with compression support
            self.entries = []
            for i in range(entry_count):
                entry_data = self._img_file.read(48)  # Fastman92 entries are larger
                if len(entry_data) != 48:
                    break

                offset, size, uncompressed_size, flags = struct.unpack('<IIII', entry_data[:16])
                name = entry_data[16:48].rstrip(b'\x00').decode('ascii', errors='ignore')

                if name:
                    entry = IMGEntry(name, offset, size)
                    entry.uncompressed_size = uncompressed_size
                    entry.flags = flags
                    entry.is_compressed = (flags & 0x1) != 0
                    entry._img_file_ref = self
                    self.entries.append(entry)

            self.total_entries = len(self.entries)
            return True

        except Exception as e:
            print(f"Error opening Fastman92 IMG: {e}")
            return False

    def _open_stories(self) -> bool:
        """Open Stories format"""
        try:
            # Stories format implementation
            # This would require specific Stories format parsing
            print("Stories format not fully implemented yet")
            return False

        except Exception as e:
            print(f"Error opening Stories IMG: {e}")
            return False

    def _handle_encrypted_v3(self) -> bool:
        """Handle encrypted Version 3 format"""
        # Encryption handling would go here
        print("Encrypted V3 format not implemented yet")
        return False

    def _read_null_terminated_string(self) -> str:
        """Read null-terminated string from current position"""
        result = b""
        while True:
            char = self._img_file.read(1)
            if not char or char == b'\x00':
                break
            result += char
        return result.decode('ascii', errors='ignore')

    def get_entry_data(self, entry: IMGEntry) -> bytes:
        """Get data for a specific entry"""
        if entry._cached_data:
            return entry._cached_data

        if not self._img_file:
            raise RuntimeError("IMG file not open")

        try:
            self._img_file.seek(entry.offset)
            data = self._img_file.read(entry.size)

            # Handle compression
            if entry.is_compressed:
                if entry.compression_type == CompressionType.ZLIB:
                    data = zlib.decompress(data)
                elif entry.compression_type == CompressionType.LZ4:
                    # LZ4 decompression would go here
                    pass
                elif entry.compression_type == CompressionType.LZO_1X_999:
                    # LZO decompression would go here
                    pass

            return data

        except Exception as e:
            raise RuntimeError(f"Error reading entry data: {e}")

    def add_entry(self, name: str, data: bytes) -> IMGEntry:
        """Add new entry to IMG"""
        entry = IMGEntry(name, 0, len(data))
        entry.set_data(data)
        entry._img_file_ref = self
        self.entries.append(entry)
        self.new_entries.append(entry)
        self.is_modified = True
        return entry

    def remove_entry(self, entry: IMGEntry) -> bool:
        """Remove entry from IMG"""
        if entry in self.entries:
            self.entries.remove(entry)
            self.removed_entries.append(entry.name)
            self.is_modified = True
            return True
        return False

    def find_entry(self, name: str) -> Optional[IMGEntry]:
        """Find entry by name"""
        name_upper = name.upper()
        for entry in self.entries:
            if entry.name.upper() == name_upper:
                return entry
        return None

    def get_entries_by_type(self, file_type: FileType) -> List[IMGEntry]:
        """Get all entries of specific type"""
        return [entry for entry in self.entries if entry.get_file_type() == file_type]

    def get_entries_by_extension(self, extension: str) -> List[IMGEntry]:
        """Get all entries with specific extension"""
        ext_upper = extension.upper().lstrip('.')
        return [entry for entry in self.entries if entry.extension == ext_upper]

    def validate(self) -> IMGValidationResult:
        """Validate entire IMG file"""
        result = IMGValidationResult()

        try:
            # Validate file exists
            if not os.path.exists(self.file_path):
                result.errors.append("IMG file does not exist")
                result.is_valid = False
                return result

            # Validate version
            if self.version == IMGVersion.UNKNOWN:
                result.errors.append("Unknown IMG version")
                result.is_valid = False

            # Validate each entry
            for entry in self.entries:
                entry_result = entry.validate()
                if not entry_result.is_valid:
                    result.errors.extend(entry_result.errors)
                    result.corrupt_entries.append(entry.name)
                result.warnings.extend(entry_result.warnings)

            # Check for duplicate names
            names = [entry.name.upper() for entry in self.entries]
            duplicates = set([name for name in names if names.count(name) > 1])
            if duplicates:
                result.warnings.extend([f"Duplicate entry: {name}" for name in duplicates])

            # Calculate fragmentation
            self._calculate_fragmentation()
            if self.fragmentation_percentage > 25.0:
                result.warnings.append(f"High fragmentation: {self.fragmentation_percentage:.1f}%")

            result.is_valid = len(result.errors) == 0

        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    def _calculate_fragmentation(self):
        """Calculate fragmentation percentage"""
        if not self.entries:
            self.fragmentation_percentage = 0.0
            return

        # Sort entries by offset
        sorted_entries = sorted(self.entries, key=lambda e: e.offset)

        # Calculate gaps
        total_gaps = 0
        for i in range(len(sorted_entries) - 1):
            current_end = sorted_entries[i].offset + sorted_entries[i].get_padded_size()
            next_start = sorted_entries[i + 1].offset
            if next_start > current_end:
                total_gaps += next_start - current_end

        # Calculate fragmentation percentage
        if self.total_size_bytes > 0:
            self.fragmentation_percentage = (total_gaps / self.total_size_bytes) * 100.0
        else:
            self.fragmentation_percentage = 0.0

    def defragment(self) -> bool:
        """Defragment IMG file by rebuilding without gaps"""
        if not self.is_modified:
            self.is_modified = True  # Force rebuild
        return self.rebuild()

    def rebuild(self, output_path: str = None) -> bool:
        """Rebuild IMG file"""
        if not output_path:
            output_path = self.file_path

        try:
            if self.version == IMGVersion.VERSION_1:
                return self._rebuild_version1(output_path)
            elif self.version == IMGVersion.VERSION_2:
                return self._rebuild_version2(output_path)
            elif self.version == IMGVersion.VERSION_3:
                return self._rebuild_version3(output_path)
            elif self.version == IMGVersion.FASTMAN92:
                return self._rebuild_fastman92(output_path)
            else:
                return False
        except Exception as e:
            print(f"Error rebuilding IMG file: {e}")
            return False

    def _rebuild_version1(self, output_path: str) -> bool:
        """Rebuild IMG Version 1"""
        try:
            dir_path = output_path.replace('.img', '.dir')

            # Create backup if overwriting
            if output_path == self.file_path:
                backup_path = output_path + '.backup'
                if os.path.exists(output_path):
                    os.rename(output_path, backup_path)
                if os.path.exists(dir_path):
                    os.rename(dir_path, dir_path + '.backup')

            # Write IMG file
            with open(output_path, 'wb') as img_file:
                current_offset = 0

                for entry in self.entries:
                    # Align to 2048-byte boundary
                    sector_offset = (current_offset + 2047) // 2048
                    entry.offset = sector_offset * 2048

                    # Seek to position
                    img_file.seek(entry.offset)

                    # Write data
                    data = entry.get_data()
                    img_file.write(data)

                    # Pad to sector boundary
                    padded_size = entry.get_padded_size()
                    if len(data) < padded_size:
                        img_file.write(b'\x00' * (padded_size - len(data)))

            self.is_modified = False
            return True

        except Exception as e:
            print(f"Error rebuilding Version 2: {e}")
            return False


    def _rebuild_version2(self, output_path: str) -> bool:
        """Rebuild IMG Version 2"""
        try:
            # Create backup if overwriting
            if output_path == self.file_path:
                backup_path = output_path + '.backup'
                if os.path.exists(output_path):
                    os.rename(output_path, backup_path)

            with open(output_path, 'wb') as img_file:
                # Write header
                img_file.write(b'VER2')
                img_file.write(struct.pack('<I', len(self.entries)))

                # Calculate entries table size
                entries_table_size = len(self.entries) * 32
                data_start = 8 + entries_table_size

                # Align data start to sector boundary
                data_start = ((data_start + 2047) // 2048) * 2048

                # Write entries table
                current_offset = data_start
                for entry in self.entries:
                    entry.offset = current_offset

                    dir_entry = struct.pack('<II',
                        entry.get_offset_in_sectors(),
                        entry.get_size_in_sectors())
                    dir_entry += entry.name.encode('ascii')[:24].ljust(24, b'\x00')
                    img_file.write(dir_entry)

                    current_offset += entry.get_padded_size()

                # Pad to data start
                current_pos = img_file.tell()
                if current_pos < data_start:
                    img_file.write(b'\x00' * (data_start - current_pos))

                # Write file data
                for entry in self.entries:
                    img_file.seek(entry.offset)
                    data = entry.get_data()
                    img_file.write(data)

                    # Pad to sector boundary
                    padded_size = entry.get_padded_size()
                    if len(data) < padded_size:
                        img_file.write(b'\x00' * (padded_size - len(data)))

            self.is_modified = False
            return True

        except Exception as e:
            print(f"Error rebuilding Version 2: {e}")
            return False

    def _rebuild_version3(self, output_path: str) -> bool:
        """Rebuild IMG Version 3"""
        print("IMG Version 3 rebuilding not yet implemented")
        return False

    def _rebuild_fastman92(self, output_path: str) -> bool:
        """Rebuild Fastman92 format"""
        print("Fastman92 rebuilding not yet implemented")
        return False

    def create_new(self, file_path: str, version: IMGVersion, **kwargs) -> bool:
        """Create new IMG file"""
        self.file_path = file_path
        self.version = version
        self.entries = []
        self.is_modified = True

        # Set default properties based on version
        if version == IMGVersion.VERSION_1:
            # Create empty DIR and IMG files
            dir_path = file_path.replace('.img', '.dir')
            open(file_path, 'wb').close()
            open(dir_path, 'wb').close()
        elif version == IMGVersion.VERSION_2:
            # Create empty Version 2 IMG
            with open(file_path, 'wb') as f:
                f.write(b'VER2')
                f.write(struct.pack('<I', 0))  # Entry count

                # Reserve initial space
                initial_size = kwargs.get('initial_size_mb', 10) * 1024 * 1024
                f.write(b'\x00' * (initial_size - 8))

        return True

    def get_statistics(self) -> Dict:
        """Get IMG file statistics"""
        stats = {
            'version': self.version.name,
            'platform': self.platform.value,
            'total_entries': len(self.entries),
            'total_size_bytes': sum(entry.size for entry in self.entries),
            'total_size_formatted': format_file_size(sum(entry.size for entry in self.entries)),
            'fragmentation_percentage': self.fragmentation_percentage,
            'is_encrypted': self.is_encrypted,
            'is_modified': self.is_modified,
            'compression_enabled': self.compression_enabled,
        }

        # File type breakdown
        type_counts = {}
        for entry in self.entries:
            file_type = entry.get_file_type().name
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        stats['file_types'] = type_counts

        # Extension breakdown
        ext_counts = {}
        for entry in self.entries:
            ext = entry.extension or "Unknown"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
        stats['extensions'] = ext_counts

        return stats

    def export_entry(self, entry: IMGEntry, output_path: str) -> bool:
        """Export single entry to file"""
        try:
            data = entry.get_data()
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            print(f"Error exporting entry {entry.name}: {e}")
            return False

    def export_all_entries(self, output_dir: str, callback=None) -> Tuple[int, int]:
        """Export all entries to directory"""
        os.makedirs(output_dir, exist_ok=True)
        success_count = 0
        error_count = 0

        for i, entry in enumerate(self.entries):
            try:
                if callback:
                    callback(i, len(self.entries), entry.name)

                output_path = os.path.join(output_dir, entry.name)
                if self.export_entry(entry, output_path):
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"Error exporting {entry.name}: {e}")
                error_count += 1

        return success_count, error_count

    def import_file(self, file_path: str, entry_name: str = None) -> Optional[IMGEntry]:
        """Import file into IMG"""
        try:
            if not entry_name:
                entry_name = os.path.basename(file_path)

            with open(file_path, 'rb') as f:
                data = f.read()

            return self.add_entry(entry_name, data)

        except Exception as e:
            print(f"Error importing file {file_path}: {e}")
            return None

    def import_directory(self, directory_path: str, callback=None) -> Tuple[int, int]:
        """Import all files from directory"""
        success_count = 0
        error_count = 0

        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

        for i, filename in enumerate(files):
            try:
                if callback:
                    callback(i, len(files), filename)

                file_path = os.path.join(directory_path, filename)
                if self.import_file(file_path, filename):
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"Error importing {filename}: {e}")
                error_count += 1

        return success_count, error_count

    def replace_entry(self, entry_name: str, new_data: bytes) -> bool:
        """Replace existing entry data"""
        entry = self.find_entry(entry_name)
        if entry:
            entry.set_data(new_data)
            entry.is_replaced = True
            self.is_modified = True
            return True
        return False

    def replace_entry_from_file(self, entry_name: str, file_path: str) -> bool:
        """Replace entry with data from file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return self.replace_entry(entry_name, data)
        except Exception as e:
            print(f"Error replacing entry from file: {e}")
            return False

    def optimize(self) -> bool:
        """Optimize IMG file (defragment and compress if supported)"""
        if self.version == IMGVersion.FASTMAN92 and self.compression_enabled:
            # Apply compression to entries
            for entry in self.entries:
                if not entry.is_compressed and entry.size > 1024:  # Only compress larger files
                    try:
                        data = entry.get_data()
                        compressed_data = zlib.compress(data, self.compression_level)
                        if len(compressed_data) < entry.size:  # Only if actually smaller
                            entry.set_data(compressed_data)
                            entry.is_compressed = True
                            entry.compression_type = CompressionType.ZLIB
                            entry.uncompressed_size = entry.size
                    except Exception as e:
                        print(f"Error compressing entry {entry.name}: {e}")

        # Defragment
        return self.defragment()

    def backup(self, backup_path: str = None) -> bool:
        """Create backup of IMG file"""
        if not backup_path:
            backup_path = self.file_path + '.backup'

        try:
            # Copy main IMG file
            import shutil
            shutil.copy2(self.file_path, backup_path)

            # Copy DIR file if Version 1
            if self.version == IMGVersion.VERSION_1:
                dir_path = self.file_path.replace('.img', '.dir')
                backup_dir_path = backup_path.replace('.img', '.dir')
                if os.path.exists(dir_path):
                    shutil.copy2(dir_path, backup_dir_path)

            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def close(self):
        """Close IMG file and cleanup"""
        if self._img_file:
            self._img_file.close()
            self._img_file = None

        if self._dir_file:
            self._dir_file.close()
            self._dir_file = None

        # Clear cached data to free memory
        for entry in self.entries:
            entry._cached_data = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class IMGEntriesTable(QTableWidget):
    """Custom table widget for IMG entries"""
    
    entries_selected = pyqtSignal(list)  # Emits selected entry indices
    entry_double_clicked = pyqtSignal(int)  # Emits row index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()
        self._connect_signals()
    
    def _setup_table(self):
        """Setup table properties"""
        # Column setup
        columns = ["Name", "Type", "Size", "Offset", "Version", "Compression", "Status"]
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Table properties
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        
        # Column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Compression
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)    # Status
        
        # Set specific column widths
        self.setColumnWidth(1, 80)   # Type
        self.setColumnWidth(2, 100)  # Size
        self.setColumnWidth(3, 100)  # Offset
        self.setColumnWidth(4, 80)   # Version
        self.setColumnWidth(5, 100)  # Compression
        self.setColumnWidth(6, 80)   # Status
    
    def _connect_signals(self):
        """Connect table signals"""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _on_selection_changed(self):
        """Handle selection changes"""
        selected_entries = self.get_selected_entries()
        self.entries_selected.emit(selected_entries)
    
    def _on_item_double_clicked(self, item):
        """Handle double-click events"""
        self.entry_double_clicked.emit(item.row())
    
    def populate_entries(self, entries: List[IMGEntry]):
        """Populate table with IMG entries"""
        self.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.setItem(row, 0, QTableWidgetItem(entry.name))
            
            # Type
            file_type = entry.extension if entry.extension else "Unknown"
            self.setItem(row, 1, QTableWidgetItem(file_type))
            
            # Size
            size_text = format_file_size(entry.size)
            self.setItem(row, 2, QTableWidgetItem(size_text))
            
            # Offset
            offset_text = f"0x{entry.offset:08X}"
            self.setItem(row, 3, QTableWidgetItem(offset_text))
            
            # Version
            version_text = entry.get_version_text()
            self.setItem(row, 4, QTableWidgetItem(version_text))
            
            # Compression
            comp_text = "None" if entry.compression_type == CompressionType.NONE else entry.compression_type.name
            self.setItem(row, 5, QTableWidgetItem(comp_text))
            
            # Status
            status = "Modified" if entry.is_new_entry or entry.is_replaced else "Original"
            self.setItem(row, 6, QTableWidgetItem(status))
    
    def get_selected_entries(self) -> List[int]:
        """Get list of selected entry indices"""
        selected_rows = []
        for item in self.selectedItems():
            if item.column() == 0:  # Only process first column
                selected_rows.append(item.row())
        return sorted(set(selected_rows))
    
    def select_all_entries(self):
        """Select all entries"""
        self.selectAll()
    
    def invert_selection(self):
        """Invert current selection"""
        current_selection = self.get_selected_entries()
        self.clearSelection()
        
        for row in range(self.rowCount()):
            if row not in current_selection:
                self.selectRow(row)
    
    def apply_filter(self, filter_text="", file_type="All Files"):
        """Apply filtering to table entries"""
        for row in range(self.rowCount()):
            show_row = True
            
            # Filter by file type
            if file_type != "All Files":
                type_item = self.item(row, 1)  # Type column
                if type_item:
                    entry_type = type_item.text().upper()
                    if file_type == "Models (DFF)" and entry_type != "DFF":
                        show_row = False
                    elif file_type == "Textures (TXD)" and entry_type != "TXD":
                        show_row = False
                    elif file_type == "Collision (COL)" and entry_type != "COL":
                        show_row = False
                    elif file_type == "Animation (IFP)" and entry_type != "IFP":
                        show_row = False
                    elif file_type == "Audio (WAV)" and entry_type != "WAV":
                        show_row = False
                    elif file_type == "Scripts (SCM)" and entry_type != "SCM":
                        show_row = False
            
            # Filter by search text
            if filter_text and show_row:
                name_item = self.item(row, 0)  # Name column
                if name_item:
                    if filter_text.lower() not in name_item.text().lower():
                        show_row = False
            
            self.setRowHidden(row, not show_row)


class FilterPanel(QWidget):
    """Panel for filtering and searching entries"""
    
    filter_changed = pyqtSignal(str, str)  # search_text, file_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
    
    def _create_ui(self):
        """Create filter panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # File type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Files", "Models (DFF)", "Textures (TXD)", 
            "Collision (COL)", "Animation (IFP)", "Audio (WAV)", "Scripts (SCM)"
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        type_layout.addWidget(self.filter_combo)
        
        layout.addLayout(type_layout)
        
        # Search filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self._on_filter_changed)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
    
    def _on_filter_changed(self):
        """Handle filter changes"""
        search_text = self.search_input.text()
        file_type = self.filter_combo.currentText()
        self.filter_changed.emit(search_text, file_type)


class IMGFileInfoPanel(QWidget):
    """Panel showing IMG file information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
        self._reset_info()
    
    def _create_ui(self):
        """Create the file info panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # File name and basic info
        self.file_label = QLabel("No IMG file loaded")
        self.file_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(self.file_label)
        
        # Statistics
        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)
        
        # Version info
        self.version_label = QLabel("")
        layout.addWidget(self.version_label)
    
    def _reset_info(self):
        """Reset panel to default state"""
        self.file_label.setText("No IMG file loaded")
        self.stats_label.setText("")
        self.version_label.setText("")
    
    def update_info(self, img_file: IMGFile):
        """Update panel with IMG file information"""
        if not img_file:
            self._reset_info()
            return
        
        # File name
        file_name = os.path.basename(img_file.file_path)
        self.file_label.setText(f"File: {file_name}")
        
        # Statistics
        entry_count = len(img_file.entries)
        total_size = sum(entry.size for entry in img_file.entries)
        file_size = format_file_size(total_size)
        self.stats_label.setText(f"Entries: {entry_count} | Size: {file_size}")
        
        # Version
        version_text = f"Version: {img_file.version.name}"
        self.version_label.setText(version_text)


def create_entries_table_panel(main_window):
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
    if hasattr(main_window, 'on_entries_selected'):
        main_window.entries_table.entries_selected.connect(main_window.on_entries_selected)
    
    if hasattr(main_window, 'on_entry_double_clicked'):
        main_window.entries_table.entry_double_clicked.connect(main_window.on_entry_double_clicked)
    
    return panel


def detect_img_version(file_path: str) -> IMGVersion:
    """Detect IMG version without fully opening the file"""
    img = IMGFile(file_path)
    return img.detect_version()


# Utility functions for table management
def populate_table_with_sample_data(table):
    """Populate table with sample data for testing"""
    sample_entries = [
        {"name": "player.dff", "extension": "DFF", "size": 250880, "offset": 0x2000, "version": "RW 3.6"},
        {"name": "player.txd", "extension": "TXD", "size": 524288, "offset": 0x42000, "version": "RW 3.6"},
        {"name": "vehicle.col", "extension": "COL", "size": 131072, "offset": 0x84000, "version": "COL 2"},
        {"name": "dance.ifp", "extension": "IFP", "size": 1258291, "offset": 0xA4000, "version": "IFP 1"},
    ]
    
    # Convert to mock entry objects
    class MockEntry:
        def __init__(self, data):
            self.name = data["name"]
            self.extension = data["extension"] 
            self.size = data["size"]
            self.offset = data["offset"]
            self._version = data["version"]
            self.is_new_entry = False
            self.is_replaced = False
            self.compression_type = CompressionType.NONE
            
        def get_version_text(self):
            return self._version
    
    mock_entries = [MockEntry(data) for data in sample_entries]
    table.populate_entries(mock_entries)


# Missing TabFilterWidget class (simplified version)
class TabFilterWidget(QWidget):
    """Tab-based filter widget - compatibility class"""
    
    filter_changed = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create a simplified version that delegates to FilterPanel
        self.filter_panel = FilterPanel(parent)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.filter_panel)
        
        # Connect signals
        self.filter_panel.filter_changed.connect(self.filter_changed)
    
    def apply_filter(self, filter_text="", file_type="All Files"):
        """Apply filter - compatibility method"""
        self.filter_changed.emit(filter_text, file_type)


def integrate_filtering(main_window, table_widget, filter_widget=None):
    """Integrate filtering functionality - compatibility function"""
    if filter_widget is None:
        filter_widget = FilterPanel(main_window)
    
    # Connect filter widget to table
    if hasattr(filter_widget, 'filter_changed'):
        filter_widget.filter_changed.connect(table_widget.apply_filter)
    
    return filter_widget


# Additional UI Components for compatibility
class IMGTableWidget(QTableWidget):
    """Basic table widget for IMG entries - compatibility class"""
    
    entries_selected = pyqtSignal(list)
    entry_double_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_img: Optional[IMGFile] = None
    
    def populate_entries(self, entries: List[IMGEntry]):
        """Populate table with entries"""
        self.setRowCount(len(entries))
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(["Name", "Type", "Size", "Offset", "Version", "Compression", "Status"])
        
        for row, entry in enumerate(entries):
            self.setItem(row, 0, QTableWidgetItem(entry.name))
            self.setItem(row, 1, QTableWidgetItem(entry.extension))
            self.setItem(row, 2, QTableWidgetItem(format_file_size(entry.size)))
            self.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:08X}"))
            self.setItem(row, 4, QTableWidgetItem(entry.get_version_text()))
            self.setItem(row, 5, QTableWidgetItem("None" if entry.compression_type == CompressionType.NONE else entry.compression_type.name))
            self.setItem(row, 6, QTableWidgetItem("Modified" if entry.is_new_entry or entry.is_replaced else "Original"))
    
    def get_selected_entries(self) -> List[int]:
        """Get selected entry indices"""
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
        return list(selected_rows)
    
    def apply_filter(self, filter_type: str, filter_value: str):
        """Apply filter to entries"""
        for row in range(self.rowCount()):
            show_row = True
            if filter_value and filter_type != "All":
                name_item = self.item(row, 0)
                if name_item and filter_value.lower() not in name_item.text().lower():
                    show_row = False
            self.setRowHidden(row, not show_row)


class IMGFilterWidget(QWidget):
    """Basic filter widget - compatibility class"""

    filter_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["All", "Name", "Type"])
        layout.addWidget(self.filter_type)

        self.filter_value = QLineEdit()
        self.filter_value.setPlaceholderText("Filter...")
        layout.addWidget(self.filter_value)

        self.filter_type.currentTextChanged.connect(self._emit_filter)
        self.filter_value.textChanged.connect(self._emit_filter)

    def _emit_filter(self):
        self.filter_changed.emit(self.filter_type.currentText(), self.filter_value.text())
