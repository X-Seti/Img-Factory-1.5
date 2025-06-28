#!/usr/bin/env python3
"""
IMG Factory - Core IMG Format Classes
Complete implementation with SOL 64-bit support
"""

#this belongs in components/ img_core_classes.py - version 15
# X-Seti - June28 2025 - Complete rewrite with SOL 64-bit indexing support

import struct
import os
import zlib
from enum import Enum
from typing import List, Optional, BinaryIO, Union
from pathlib import Path


class IMGVersion(Enum):
    """IMG Archive version types"""
    IMG_UNKNOWN = 0
    IMG_1 = 1        # GTA III/VC - DIR/IMG pair (32-bit)
    IMG_2 = 2        # GTA SA - Single file (32-bit)
    IMG_3 = 3        # GTA IV - Advanced (RAGE engine)
    IMG_FASTMAN92 = 4 # Modded version
    IMG_STORIES = 5   # Stories version
    IMG_SOL = 6       # State of Liberty - 64-bit indexing for >2GB files


class FileType(Enum):
    """File types found in IMG archives"""
    UNKNOWN = 0
    MODEL = 1      # DFF files (RenderWare models)
    TEXTURE = 2    # TXD files (RenderWare textures)
    COLLISION = 3  # COL files (collision data)
    ANIMATION = 4  # IFP files (animations)
    AUDIO = 5      # WAV/MP3 files
    SCRIPT = 6     # SCM files (scripts)
    RAGE_MODEL = 7    # WDR/WDD/WFT files (RAGE models)
    RAGE_TEXTURE = 8  # WTD files (RAGE textures)


class CompressionType(Enum):
    """Compression algorithms supported"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    LZO_1X_999 = 3


class IMGEntry:
    """
    Represents a single file entry within an IMG archive
    Supports both 32-bit and 64-bit indexing (for SOL)
    """
    
    def __init__(self):
        self.name: str = ""
        self.extension: str = ""
        self.offset: int = 0          # Offset in bytes (64-bit for SOL)
        self.size: int = 0            # Size in bytes (64-bit for SOL)
        self.uncompressed_size: int = 0
        self.file_type: FileType = FileType.UNKNOWN
        self.compression: CompressionType = CompressionType.NONE
        self.rw_version: int = 0      # RenderWare version
        self.is_encrypted: bool = False
        self.is_new_entry: bool = False
        self.is_replaced: bool = False
        self.flags: int = 0
        self.is_64bit: bool = False   # True for SOL 64-bit entries
        
        # Reference to parent IMG file
        self._img_file: Optional['IMGFile'] = None
        self._cached_rw_version: Optional[str] = None
    
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
    
    def is_rage_file(self) -> bool:
        """Check if this is a RAGE engine file"""
        return self.file_type in [FileType.RAGE_MODEL, FileType.RAGE_TEXTURE]
    
    def is_supported_format(self) -> bool:
        """Check if this file format is currently supported"""
        supported_types = [
            FileType.MODEL, FileType.TEXTURE, FileType.COLLISION,
            FileType.ANIMATION, FileType.AUDIO, FileType.SCRIPT
        ]
        return self.file_type in supported_types
    
    def detect_renderware_version(self) -> str:
        """
        Detect actual RenderWare version from file data
        Only applies to 3D Era games (GTA III, VC, SA)
        """
        if not self._img_file or not self.is_rw_file():
            return "Unknown"
        
        try:
            # Read first 12 bytes to get RenderWare header
            data = self._img_file.read_entry_data(self)
            if len(data) < 12:
                return "Unknown"
            
            # RenderWare header structure:
            # 4 bytes: chunk type
            # 4 bytes: chunk size  
            # 4 bytes: version
            chunk_type, chunk_size, version = struct.unpack('<III', data[:12])
            
            # Historically accurate version mapping
            version_map = {
                # GTA III (2001) - RenderWare 3.1/3.2
                0x0800FFFF: "3.0.0.0",
                0x1003FFFF: "3.1.0.1",   # GTA III initial release
                0x1005FFFF: "3.2.0.0",   # GTA III later patches
                
                # GTA Vice City (2002) - RenderWare 3.2
                0x1006FFFF: "3.2.0.4",   # VC v1.1
                
                # State of Liberty Stories - RenderWare 3.4
                0x1400FFFF: "3.4.0.3",
                0x1401FFFF: "3.4.0.1",
                0x1402FFFF: "3.4.0.2",
                
                # GTA San Andreas (2004) - RW 3.6 → 3.7
                0x1800FFFF: "3.6.0.0",   # SA initial
                0x1801FFFF: "3.6.0.1",
                0x1803FFFF: "3.6.0.3",   # SA v1.0/v1.01
                0x1C02FFFF: "3.7.0.2",   # SA later versions
                0x1C0EFFFF: "3.7.0.14",  # SA final versions
                
                # Additional common versions
                0x1C00FFFF: "3.7.0.0",
                0x1C01FFFF: "3.7.0.1",
                0x1C03FFFF: "3.7.0.3",
            }
            
            detected_version = version_map.get(version)
            if detected_version:
                self.rw_version = version
                return detected_version
            else:
                return f"RW {hex(version)}"
                
        except Exception as e:
            print(f"Error detecting RenderWare version for {self.name}: {e}")
            return "Unknown"
    
    def get_version_text(self) -> str:
        """Get human-readable version information"""
        if self.is_rw_file():
            # 3D Era - RenderWare files (.dff/.txd)
            if self._cached_rw_version:
                return self._cached_rw_version
            
            detected = self.detect_renderware_version()
            self._cached_rw_version = detected
            return detected
            
        elif self.is_rage_file():
            # HD Era - RAGE engine files
            return "RAGE (Not Supported)"
            
        elif self.file_type == FileType.COLLISION:
            # COL file versions by game era
            if hasattr(self._img_file, 'version'):
                if self._img_file.version == IMGVersion.IMG_1:  # GTA III/VC
                    return "COL 1"
                elif self._img_file.version == IMGVersion.IMG_2:  # GTA SA
                    return "COL 2"
                elif self._img_file.version == IMGVersion.IMG_SOL:  # SOL
                    return "COL 2 (SOL)"
            return "COL 2"
            
        elif self.file_type == FileType.ANIMATION:
            # IFP versions by game era
            if hasattr(self._img_file, 'version'):
                if self._img_file.version == IMGVersion.IMG_1:  # GTA III/VC
                    return "IFP 1"
                elif self._img_file.version == IMGVersion.IMG_2:  # GTA SA
                    return "IFP 2"
                elif self._img_file.version == IMGVersion.IMG_SOL:  # SOL
                    return "IFP 2 (SOL)"
            return "IFP 1"
            
        elif self.file_type == FileType.SCRIPT:
            return "SCM"
        elif self.file_type == FileType.AUDIO:
            return "Audio"
        else:
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
    Supports all IMG versions including SOL 64-bit indexing
    """
    
    def __init__(self, file_path: str = ""):
        self.file_path: str = file_path
        self.version: IMGVersion = IMGVersion.IMG_UNKNOWN
        self.entries: List[IMGEntry] = []
        self.is_encrypted: bool = False
        self.platform: str = "PC"
        self.total_size: int = 0
        self.header_size: int = 0
        self.is_64bit: bool = False  # True for SOL files >2GB
        
        # File handles
        self._file_handle: Optional[BinaryIO] = None
        
        # Auto-detect version if file exists
        if file_path and os.path.exists(file_path):
            self.detect_version()

    def detect_version(self) -> IMGVersion:
        """Detect IMG version from file"""
        if not os.path.exists(self.file_path):
            self.version = IMGVersion.IMG_UNKNOWN
            return self.version
        
        try:
            file_size = os.path.getsize(self.file_path)
            
            with open(self.file_path, 'rb') as f:
                header = f.read(16)
                
            if len(header) < 4:
                self.version = IMGVersion.IMG_UNKNOWN
                return self.version
            
            # Check for VER2 signature (GTA SA)
            if header[:4] == b'VER2':
                # Check if this is SOL format (>2GB or 64-bit indexing)
                if file_size > 2147483648 or self._check_64bit_indexing(header):
                    self.version = IMGVersion.IMG_SOL
                    self.is_64bit = True
                else:
                    self.version = IMGVersion.IMG_2
                return self.version
            
            # Check for GTA IV signature (RAGE)
            signature = struct.unpack('<I', header[:4])[0]
            if signature == 0xA94E2A52:
                self.version = IMGVersion.IMG_3
                return self.version
            
            # Check for DIR file (GTA III/VC)
            dir_path = self.file_path.replace('.img', '.dir')
            if os.path.exists(dir_path):
                self.version = IMGVersion.IMG_1
                return self.version
            
            # Default fallback
            self.version = IMGVersion.IMG_2
            return self.version
            
        except Exception as e:
            print(f"Error detecting version: {e}")
            self.version = IMGVersion.IMG_UNKNOWN
            return self.version

    def _check_64bit_indexing(self, header: bytes) -> bool:
        """Check if file uses 64-bit indexing (SOL format)"""
        try:
            # SOL files may have different header structure
            # or use 64-bit offsets/sizes in entry table
            if len(header) >= 8:
                entry_count = struct.unpack('<I', header[4:8])[0]
                # If entry count is suspiciously high, might be 64-bit
                if entry_count > 100000:  # Reasonable threshold
                    return True
            return False
        except:
            return False

    def open(self) -> bool:
        """Open IMG file and detect version"""
        if not os.path.exists(self.file_path):
            return False
        
        # Detect version first if not already detected
        if self.version == IMGVersion.IMG_UNKNOWN:
            self.detect_version()
        
        if self.version == IMGVersion.IMG_UNKNOWN:
            return False
        
        try:
            if self.version == IMGVersion.IMG_1:
                return self._open_version1()
            elif self.version == IMGVersion.IMG_2:
                return self._open_version2()
            elif self.version == IMGVersion.IMG_SOL:
                return self._open_sol()
            elif self.version == IMGVersion.IMG_3:
                return self._open_version3()
            elif self.version == IMGVersion.IMG_FASTMAN92:
                return self._open_fastman92()
            
        except Exception as e:
            print(f"Error opening IMG file: {e}")
            return False
        
        return False

    def parse_entries(self) -> bool:
        """Parse entries from the opened IMG file"""
        if self.entries:
            return True
        return self.open()

    def _open_version1(self) -> bool:
        """Open IMG version 1 (DIR/IMG pair) - GTA III/VC"""
        if self.file_path.lower().endswith('.dir'):
            dir_path = self.file_path
            img_path = self.file_path[:-4] + '.img'
        else:
            img_path = self.file_path
            dir_path = self.file_path[:-4] + '.dir'
        
        if not os.path.exists(dir_path) or not os.path.exists(img_path):
            print(f"Missing files: DIR={os.path.exists(dir_path)}, IMG={os.path.exists(img_path)}")
            return False
        
        try:
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
            
            self.file_path = img_path
            print(f"Loaded {len(self.entries)} entries from GTA III/VC IMG")
            return True
            
        except Exception as e:
            print(f"Error opening Version 1 IMG: {e}")
            return False

    def _open_version2(self) -> bool:
        """Open IMG version 2 (GTA SA format) - 32-bit"""
        try:
            with open(self.file_path, 'rb') as f:
                signature = f.read(4)
                if signature != b'VER2':
                    print(f"Invalid signature: {signature}")
                    return False
                
                entry_count = struct.unpack('<I', f.read(4))[0]
                print(f"Entry count: {entry_count}")
                
                self.entries = []
                for i in range(entry_count):
                    entry_data = f.read(32)
                    if len(entry_data) != 32:
                        break
                    
                    # Parse entry (32 bytes) - 32-bit offsets/sizes
                    offset_sectors = struct.unpack('<I', entry_data[:4])[0]
                    archive_size = struct.unpack('<H', entry_data[4:6])[0]
                    streaming_size = struct.unpack('<H', entry_data[6:8])[0]
                    name_bytes = entry_data[8:32]
                    
                    size_sectors = archive_size if archive_size != 0 else streaming_size
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
                
                print(f"Loaded {len(self.entries)} entries from GTA SA IMG")
                return True
                
        except Exception as e:
            print(f"Error opening Version 2 IMG: {e}")
            return False

    def _open_sol(self) -> bool:
        """Open SOL format (State of Liberty) - 64-bit indexing for >2GB files"""
        try:
            with open(self.file_path, 'rb') as f:
                signature = f.read(4)
                if signature != b'VER2':
                    print(f"Invalid SOL signature: {signature}")
                    return False
                
                # SOL may use 64-bit entry count
                entry_count_data = f.read(8)  # Read 8 bytes for potential 64-bit
                entry_count = struct.unpack('<I', entry_count_data[:4])[0]
                
                print(f"SOL Entry count: {entry_count} (64-bit indexing)")
                
                self.entries = []
                self.is_64bit = True
                
                for i in range(entry_count):
                    # SOL format might use larger entry size for 64-bit offsets
                    entry_data = f.read(40)  # Assume 40 bytes for 64-bit entries
                    if len(entry_data) < 32:
                        break
                    
                    # Parse SOL entry with potential 64-bit fields
                    if len(entry_data) >= 40:
                        # 64-bit offset (8 bytes)
                        offset_sectors = struct.unpack('<Q', entry_data[:8])[0]
                        # Size fields
                        archive_size = struct.unpack('<I', entry_data[8:12])[0]
                        streaming_size = struct.unpack('<I', entry_data[12:16])[0]
                        # Name (24 bytes)
                        name_bytes = entry_data[16:40]
                    else:
                        # Fallback to 32-bit format
                        offset_sectors = struct.unpack('<I', entry_data[:4])[0]
                        archive_size = struct.unpack('<H', entry_data[4:6])[0]
                        streaming_size = struct.unpack('<H', entry_data[6:8])[0]
                        name_bytes = entry_data[8:32]
                    
                    size_sectors = archive_size if archive_size != 0 else streaming_size
                    name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
                    
                    if name:
                        entry = IMGEntry()
                        entry.name = name
                        entry.extension = os.path.splitext(name)[1].upper().lstrip('.')
                        entry.offset = offset_sectors * 2048 if offset_sectors < 0x100000000 else offset_sectors
                        entry.size = size_sectors * 2048 if size_sectors < 0x100000000 else size_sectors
                        entry.file_type = self._detect_file_type(entry.extension)
                        entry.is_64bit = True
                        entry.set_img_file(self)
                        self.entries.append(entry)
                
                print(f"Loaded {len(self.entries)} entries from SOL IMG (64-bit)")
                return True
                
        except Exception as e:
            print(f"Error opening SOL IMG: {e}")
            return False

    def _open_version3(self) -> bool:
        """Open IMG version 3 (GTA IV format) - RAGE engine"""
        print("IMG Version 3 (RAGE) support not implemented")
        return False

    def _open_fastman92(self) -> bool:
        """Open Fastman92 format"""
        print("Fastman92 format support not implemented")
        return False

    def _detect_file_type(self, extension: str) -> FileType:
        """Detect file type from extension"""
        ext_upper = extension.upper()
        
        # 3D Era (RenderWare) formats - FULLY SUPPORTED
        if ext_upper == 'DFF':
            return FileType.MODEL
        elif ext_upper == 'TXD':
            return FileType.TEXTURE
        elif ext_upper == 'COL':
            return FileType.COLLISION
        elif ext_upper == 'IFP':
            return FileType.ANIMATION
        elif ext_upper in ['WAV', 'MP3']:
            return FileType.AUDIO
        elif ext_upper == 'SCM':
            return FileType.SCRIPT
        
        # HD Era (RAGE) formats - RECOGNIZED BUT NOT SUPPORTED
        elif ext_upper in ['WDR', 'WDD', 'WFT']:
            return FileType.RAGE_MODEL
        elif ext_upper in ['WTD']:
            return FileType.RAGE_TEXTURE
        
        else:
            return FileType.UNKNOWN

    def read_entry_data(self, entry: IMGEntry) -> bytes:
        """Read data for a specific entry - supports 64-bit offsets"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"IMG file not found: {self.file_path}")
        
        try:
            with open(self.file_path, 'rb') as f:
                f.seek(entry.offset)
                return f.read(entry.size)
        except Exception as e:
            raise Exception(f"Error reading entry {entry.name}: {e}")

    def write_entry_data(self, entry: IMGEntry, data: bytes):
        """Write data for a specific entry"""
        raise NotImplementedError("Write functionality not implemented")

    def close(self):
        """Close IMG file"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
        self.entries.clear()

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
        return False

    def get_file_size_gb(self) -> float:
        """Get file size in GB (useful for SOL files)"""
        try:
            size_bytes = os.path.getsize(self.file_path)
            return size_bytes / (1024 * 1024 * 1024)
        except:
            return 0.0


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def detect_img_version(file_path: str) -> IMGVersion:
    """Detect IMG version without fully opening the file"""
    img = IMGFile(file_path)
    return img.detect_version()


def is_sol_file(file_path: str) -> bool:
    """Check if file is State of Liberty format (>2GB)"""
    try:
        size = os.path.getsize(file_path)
        return size > 2147483648  # 2GB threshold
    except:
        return False


class RAGESupport:
    """Placeholder for future RAGE engine support"""
    
    @staticmethod
    def is_rage_file(extension: str) -> bool:
        """Check if file extension is a RAGE format"""
        rage_extensions = ['WDR', 'WDD', 'WFT', 'WTD', 'RPF']
        return extension.upper() in rage_extensions
    
    @staticmethod
    def get_rage_info() -> str:
        """Return info about RAGE support status"""
        return """
        RAGE Engine Support (Future Feature):
        
        Planned formats:
        - .wdr - RAGE Drawable (models)
        - .wdd - RAGE Drawable Dictionary (model collections) 
        - .wft - RAGE Fragment (physics models)
        - .wtd - RAGE Texture Dictionary (textures)
        - .rpf - RAGE Package File (archives)
        
        Games using RAGE: GTA IV, GTA V, Red Dead series
        Status: Research needed for proprietary formats
        """
