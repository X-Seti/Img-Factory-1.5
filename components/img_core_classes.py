#!/usr/bin/env python3
"""
IMG Factory - Core IMG Format Classes
Clean implementation of IMG file handling for Qt6
"""

import struct
import os
import zlib
from enum import Enum
from typing import List, Optional, BinaryIO
from pathlib import Path


class IMGVersion(Enum):
    """IMG Archive version types"""
    IMG_UNKNOWN = 0
    IMG_1 = 1        # GTA III/VC - DIR/IMG pair
    IMG_2 = 2        # GTA SA - Single file
    IMG_3 = 3        # GTA IV - Advanced
    IMG_FASTMAN92 = 4 # Modded version
    IMG_STORIES = 5   # Stories version


class FileType(Enum):
    """File types found in IMG archives"""
    UNKNOWN = 0
    MODEL = 1      # DFF files
    TEXTURE = 2    # TXD files
    COLLISION = 3  # COL files
    ANIMATION = 4  # IFP files
    AUDIO = 5      # WAV files
    SCRIPT = 6     # SCM files


class CompressionType(Enum):
    """Compression algorithms supported"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    LZO_1X_999 = 3


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
        self.compression: CompressionType = CompressionType.NONE
        self.rw_version: int = 0      # RenderWare version
        self.is_encrypted: bool = False
        self.is_new_entry: bool = False
        self.is_replaced: bool = False
        self.flags: int = 0
        
        # Reference to parent IMG file
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
        return self.compression != CompressionType.NONE
    
    def is_rw_file(self) -> bool:
        """Check if this is a RenderWare file (DFF/TXD)"""
        return self.file_type in [FileType.MODEL, FileType.TEXTURE]
    
    def get_version_text(self) -> str:
        """Get human-readable version information"""
        if self.file_type == FileType.MODEL or self.file_type == FileType.TEXTURE:
            # RW version mapping (simplified)
            rw_versions = {
                0x0800FFFF: "3.0.0.0",
                0x1003FFFF: "3.1.0.1", 
                0x1005FFFF: "3.2.0.0",
                0x1400FFFF: "3.4.0.3",
                0x1803FFFF: "3.6.0.3"
            }
            return rw_versions.get(self.rw_version, f"RW {hex(self.rw_version)}")
        elif self.file_type == FileType.COLLISION:
            return f"COL {self.rw_version}"
        elif self.file_type == FileType.ANIMATION:
            return f"IFP {self.rw_version}"
        return "Unknown"
    
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
    Main IMG archive file handler
    """
    
    def __init__(self, file_path: str = ""):
        self.file_path: str = file_path
        self.version: IMGVersion = IMGVersion.IMG_UNKNOWN
        self.entries: List[IMGEntry] = []
        self.is_encrypted: bool = False
        self.platform: str = "PC"
        
        # File handles
        self._img_handle: Optional[BinaryIO] = None
        self._dir_handle: Optional[BinaryIO] = None
    
    def detect_version(self) -> IMGVersion:
        """Detect IMG file version from header"""
        if not os.path.exists(self.file_path):
            return IMGVersion.IMG_UNKNOWN
        
        # Check if it's a DIR file (IMG version 1)
        if self.file_path.lower().endswith('.dir'):
            img_path = self.file_path[:-4] + '.img'
            if os.path.exists(img_path):
                return IMGVersion.IMG_1
            return IMGVersion.IMG_UNKNOWN
        
        # Read header to detect version
        try:
            with open(self.file_path, 'rb') as f:
                header = f.read(16)
                
                if len(header) < 4:
                    return IMGVersion.IMG_UNKNOWN
                
                # Check for version 2 (VER2 signature)
                if header[:4] == b'VER2':
                    return IMGVersion.IMG_2
                
                # Check for fastman92 version (VERF signature)
                if header[:4] == b'VERF':
                    return IMGVersion.IMG_FASTMAN92
                
                # Check for version 3 (specific magic number)
                if len(header) >= 4:
                    magic = struct.unpack('<I', header[:4])[0]
                    if magic == 0xA94E2A52:
                        return IMGVersion.IMG_3
                
                # Check if corresponding DIR file exists (version 1)
                dir_path = self.file_path[:-4] + '.dir'
                if os.path.exists(dir_path):
                    return IMGVersion.IMG_1
                
        except Exception:
            pass
        
        return IMGVersion.IMG_UNKNOWN
    
    def open(self) -> bool:
        """Open IMG file for reading"""
        if not os.path.exists(self.file_path):
            return False
        
        self.version = self.detect_version()
        if self.version == IMGVersion.IMG_UNKNOWN:
            return False
        
        try:
            if self.version == IMGVersion.IMG_1:
                return self._open_version1()
            elif self.version == IMGVersion.IMG_2:
                return self._open_version2()
            elif self.version == IMGVersion.IMG_3:
                return self._open_version3()
            elif self.version == IMGVersion.IMG_FASTMAN92:
                return self._open_fastman92()
            
        except Exception as e:
            print(f"Error opening IMG file: {e}")
            return False
        
        return False
    
    def _open_version1(self) -> bool:
        """Open IMG version 1 (DIR/IMG pair)"""
        # Determine DIR and IMG paths
        if self.file_path.lower().endswith('.dir'):
            dir_path = self.file_path
            img_path = self.file_path[:-4] + '.img'
        else:
            img_path = self.file_path
            dir_path = self.file_path[:-4] + '.dir'
        
        if not os.path.exists(dir_path) or not os.path.exists(img_path):
            return False
        
        # Open DIR file to read entries
        with open(dir_path, 'rb') as dir_file:
            dir_size = os.path.getsize(dir_path)
            entry_count = dir_size // 32  # Each entry is 32 bytes
            
            self.entries = []
            for i in range(entry_count):
                entry_data = dir_file.read(32)
                if len(entry_data) != 32:
                    break
                
                # Parse DIR entry (32 bytes total)
                offset_sectors, size_sectors = struct.unpack('<II', entry_data[:8])
                name_bytes = entry_data[8:32]
                
                # Extract null-terminated name
                name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
                
                if name:  # Skip empty entries
                    entry = IMGEntry()
                    entry.name = name
                    entry.extension = os.path.splitext(name)[1].upper().lstrip('.')
                    entry.offset = offset_sectors * 2048
                    entry.size = size_sectors * 2048
                    entry.file_type = self._detect_file_type(entry.extension)
                    entry.set_img_file(self)
                    self.entries.append(entry)
        
        # Store IMG path for data reading
        self.file_path = img_path
        return True
    
    def _open_version2(self) -> bool:
        """Open IMG version 2 (GTA SA format)"""
        with open(self.file_path, 'rb') as f:
            # Read header
            signature = f.read(4)
            if signature != b'VER2':
                return False
            
            entry_count = struct.unpack('<I', f.read(4))[0]
            
            self.entries = []
            for i in range(entry_count):
                entry_data = f.read(32)
                if len(entry_data) != 32:
                    break
                
                # Parse entry (32 bytes)
                offset_sectors = struct.unpack('<I', entry_data[:4])[0]
                archive_size = struct.unpack('<H', entry_data[4:6])[0]
                streaming_size = struct.unpack('<H', entry_data[6:8])[0]
                name_bytes = entry_data[8:32]
                
                # Use archive size if available, otherwise streaming size
                size_sectors = archive_size if archive_size != 0 else streaming_size
                
                # Extract name
                name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
                
                if name:
                    entry = IMGEntry()
                    entry.name = name
                    entry.extension = os.path.splitext(name)[1].upper().lstrip('.')
                    entry.offset = offset_sectors * 2048
                    entry.size = size_sectors * 2048
                    entry.file_type = self._detect_file_type(entry.extension)
                    entry.set_img_file(self)
                    self.entries.append(entry)
        
        return True
    
    def _open_version3(self) -> bool:
        """Open IMG version 3 (GTA IV format) - simplified"""
        with open(self.file_path, 'rb') as f:
            # Read header (20 bytes)
            magic = struct.unpack('<I', f.read(4))[0]
            if magic != 0xA94E2A52:
                return False
            
            version = struct.unpack('<I', f.read(4))[0]
            if version != 3:
                return False
            
            entry_count = struct.unpack('<I', f.read(4))[0]
            table_size = struct.unpack('<I', f.read(4))[0]
            entry_size = struct.unpack('<H', f.read(2))[0]
            f.read(2)  # padding
            
            # Read entries (16 bytes each)
            self.entries = []
            for i in range(entry_count):
                entry_data = f.read(16)
                if len(entry_data) != 16:
                    break
                
                # Parse entry
                unknown1 = struct.unpack('<I', entry_data[:4])[0]
                resource_type = struct.unpack('<I', entry_data[4:8])[0]
                offset_sectors = struct.unpack('<I', entry_data[8:12])[0]
                size_info = struct.unpack('<I', entry_data[12:16])[0]
                
                size_sectors = (size_info >> 11) & 0x1FFFFF
                flags = size_info & 0x7FF
                
                entry = IMGEntry()
                entry.offset = offset_sectors * 2048
                entry.size = size_sectors * 2048
                entry.flags = flags
                entry.set_img_file(self)
                self.entries.append(entry)
            
            # Read entry names
            for i, entry in enumerate(self.entries):
                name_bytes = b''
                while True:
                    byte = f.read(1)
                    if not byte or byte == b'\x00':
                        break
                    name_bytes += byte
                
                name = name_bytes.decode('ascii', errors='ignore')
                entry.name = name
                entry.extension = os.path.splitext(name)[1].upper().lstrip('.')
                entry.file_type = self._detect_file_type(entry.extension)
        
        return True
    
    def _open_fastman92(self) -> bool:
        """Open fastman92 IMG format - placeholder"""
        # Complex modded format - not implemented yet
        return False
    
    def _detect_file_type(self, extension: str) -> FileType:
        """Detect file type from extension"""
        ext_map = {
            'DFF': FileType.MODEL,
            'TXD': FileType.TEXTURE,
            'COL': FileType.COLLISION,
            'IFP': FileType.ANIMATION,
            'WAV': FileType.AUDIO,
            'SCM': FileType.SCRIPT,
        }
        return ext_map.get(extension.upper(), FileType.UNKNOWN)
    
    def close(self):
        """Close file handles"""
        if self._img_handle:
            self._img_handle.close()
            self._img_handle = None
        if self._dir_handle:
            self._dir_handle.close()
            self._dir_handle = None
    
    def read_entry_data(self, entry: IMGEntry) -> bytes:
        """Read raw data for an entry"""
        with open(self.file_path, 'rb') as f:
            f.seek(entry.offset)
            data = f.read(entry.size)
            
            # Handle compression if needed
            if entry.is_compressed():
                if entry.compression == CompressionType.ZLIB:
                    try:
                        data = zlib.decompress(data)
                    except:
                        pass  # Return raw data if decompression fails
            
            return data
    
    def write_entry_data(self, entry: IMGEntry, data: bytes):
        """Write data for an entry (placeholder)"""
        # Placeholder - would handle writing data back to IMG file
        entry.size = len(data)
        entry.is_replaced = True
    
    def get_entry_by_name(self, name: str) -> Optional[IMGEntry]:
        """Find entry by name (case-insensitive)"""
        name_upper = name.upper()
        for entry in self.entries:
            if entry.name.upper() == name_upper:
                return entry
        return None
    
    def get_entries_by_extension(self, extension: str) -> List[IMGEntry]:
        """Get all entries with specific extension"""
        ext_upper = extension.upper().lstrip('.')
        return [entry for entry in self.entries if entry.extension == ext_upper]
    
    def add_entry(self, name: str, data: bytes) -> IMGEntry:
        """Add new entry to IMG"""
        entry = IMGEntry()
        entry.name = name
        entry.extension = os.path.splitext(name)[1].upper().lstrip('.')
        entry.size = len(data)
        entry.file_type = self._detect_file_type(entry.extension)
        entry.is_new_entry = True
        entry.set_img_file(self)
        self.entries.append(entry)
        return entry
    
    def remove_entry(self, entry: IMGEntry) -> bool:
        """Remove entry from IMG"""
        if entry in self.entries:
            self.entries.remove(entry)
            return True
        return False
    
    def rebuild(self, output_path: str = None) -> bool:
        """Rebuild IMG file (placeholder)"""
        # Placeholder for rebuild functionality
        return False


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


def detect_img_version(file_path: str) -> IMGVersion:
    """Detect IMG version without fully opening the file"""
    img = IMGFile(file_path)
    return img.detect_version()
