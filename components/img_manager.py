#!/usr/bin/env python3
"""
IMG Manager - Core IMG file handling and management
Based on the C++ IMG Factory codebase structure
"""

import os
import struct
import time
from typing import List, Dict, Optional, Union, BinaryIO
from enum import Enum
from pathlib import Path


class IMGVersion(Enum):
    """IMG file version enumeration"""
    UNKNOWN = 0
    VERSION_1 = 1  # GTA III/VC (DIR + IMG files)
    VERSION_2 = 2  # GTA SA (single IMG file with header)
    VERSION_3 = 3  # GTA IV (encrypted/unencrypted)
    FASTMAN92 = 4  # Fastman92's extended format
    STORIES = 5    # GTA Stories format


class CompressionType(Enum):
    """Compression algorithm types"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    LZO_1X_999 = 3
    UNKNOWN = 255


class Platform(Enum):
    """Platform enumeration"""
    PC = "PC"
    XBOX = "XBOX"
    PS2 = "PS2"
    PSP = "PSP"
    MOBILE = "Mobile"


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
        
        # Version 3 specific
        self.rage_resource_type = None
        self.flags = 0
        
        # Fastman92 specific
        self.uncompressed_size = 0
        self.compression_level = 0
        
        # Internal data cache
        self._cached_data: Optional[bytes] = None
        self._img_file_ref: Optional['IMGFile'] = None
    
    def _extract_extension(self) -> str:
        """Extract file extension from name"""
        if '.' in self.name:
            return self.name.split('.')[-1].upper()
        return ""
    
    def get_sectors_offset(self) -> int:
        """Get offset in sectors (1 sector = 2048 bytes)"""
        return self.offset // 2048
    
    def get_sectors_size(self) -> int:
        """Get size in sectors"""
        return (self.size + 2047) // 2048  # Round up
    
    def get_padded_size(self) -> int:
        """Get size padded to sector boundary"""
        return self.get_sectors_size() * 2048
    
    def get_version_text(self) -> str:
        """Get human-readable version information"""
        if self.extension in ['DFF', 'TXD']:
            return f"RW {self.rw_version}" if self.rw_version else "RW Unknown"
        elif self.extension == 'COL':
            return f"COL {self.raw_version}" if self.raw_version else "COL Unknown"
        elif self.extension == 'IFP':
            return f"IFP {self.raw_version}" if self.raw_version else "IFP Unknown"
        return "Unknown"
    
    def get_data(self) -> bytes:
        """Get entry data (decompressed if necessary)"""
        if self._cached_data is not None:
            return self._cached_data
        
        if self._img_file_ref is None:
            raise RuntimeError("No IMG file reference available")
        
        return self._img_file_ref._read_entry_data(self)
    
    def set_data(self, data: bytes):
        """Set entry data (will be compressed if needed)"""
        self._cached_data = data
        self.size = len(data)
        if self._img_file_ref:
            self._img_file_ref._write_entry_data(self, data)
    
    def can_be_read(self) -> bool:
        """Check if entry can be read successfully"""
        if self.is_encrypted and self.compression_type == CompressionType.UNKNOWN:
            return False
        if self.is_compressed and self.compression_type == CompressionType.UNKNOWN:
            return False
        return True


class IMGFile:
    """Main IMG file manager"""
    
    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.version = IMGVersion.UNKNOWN
        self.platform = Platform.PC
        self.is_encrypted = False
        self.encryption_type = 0
        self.game_type = 0
        self.sub_version = 0
        
        self.entries: List[IMGEntry] = []
        self._file_handle: Optional[BinaryIO] = None
        self._is_modified = False
        
        # Version-specific data
        self._undecrypted_position_offset = 0  # For IMG3 encrypted files
        
    def open(self) -> bool:
        """Open and parse IMG file"""
        if not os.path.exists(self.file_path):
            return False
        
        try:
            self._file_handle = open(self.file_path, 'rb')
            self.version = self._detect_version()
            
            if self.version == IMGVersion.UNKNOWN:
                return False
            
            return self._parse_file()
            
        except Exception as e:
            print(f"Error opening IMG file: {e}")
            if self._file_handle:
                self._file_handle.close()
                self._file_handle = None
            return False
    
    def close(self):
        """Close IMG file"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def create_new(self, file_path: str, version: IMGVersion = IMGVersion.VERSION_2) -> bool:
        """Create a new empty IMG file"""
        try:
            self.file_path = file_path
            self.version = version
            self.entries = []
            self._is_modified = True
            
            # Create initial file structure
            if version == IMGVersion.VERSION_1:
                # Create DIR file
                dir_path = file_path.replace('.img', '.dir')
                with open(dir_path, 'wb') as f:
                    pass  # Empty DIR file
                # Create empty IMG file
                with open(file_path, 'wb') as f:
                    pass  # Empty IMG file
            else:
                # Create IMG file with appropriate header
                with open(file_path, 'wb') as f:
                    self._write_header(f)
            
            return True
            
        except Exception as e:
            print(f"Error creating IMG file: {e}")
            return False
    
    def add_entry(self, name: str, data: bytes) -> IMGEntry:
        """Add new entry to IMG file"""
        entry = IMGEntry(name, 0, len(data))
        entry._img_file_ref = self
        entry._cached_data = data
        entry.is_new_entry = True
        
        self.entries.append(entry)
        self._is_modified = True
        
        return entry
    
    def remove_entry(self, entry: IMGEntry) -> bool:
        """Remove entry from IMG file"""
        try:
            self.entries.remove(entry)
            self._is_modified = True
            return True
        except ValueError:
            return False
    
    def get_entry_by_name(self, name: str) -> Optional[IMGEntry]:
        """Find entry by name (case insensitive)"""
        name_upper = name.upper()
        for entry in self.entries:
            if entry.name.upper() == name_upper:
                return entry
        return None
    
    def rebuild(self, output_path: str = None) -> bool:
        """Rebuild IMG file, optionally to a new location"""
        if output_path is None:
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
                raise ValueError(f"Unsupported IMG version: {self.version}")
                
        except Exception as e:
            print(f"Error rebuilding IMG file: {e}")
            return False
    
    def _detect_version(self) -> IMGVersion:
        """Detect IMG file version from header"""
        if not self._file_handle:
            return IMGVersion.UNKNOWN
        
        self._file_handle.seek(0)
        
        # Check file extension first
        if self.file_path.lower().endswith('.dir'):
            return IMGVersion.VERSION_1
        
        # Read first 16 bytes for analysis
        header = self._file_handle.read(16)
        if len(header) < 4:
            # Check for DIR file
            dir_path = self.file_path.replace('.img', '.dir')
            if os.path.exists(dir_path):
                return IMGVersion.VERSION_1
            return IMGVersion.UNKNOWN
        
        # Check various signatures
        signature = header[:4]
        
        if signature == b'VER2':
            return IMGVersion.VERSION_2
        elif signature == b'VERF':
            return IMGVersion.FASTMAN92
        elif struct.unpack('<I', signature)[0] == 0xA94E2A52:
            return IMGVersion.VERSION_3
        else:
            # Try to decrypt for IMG3 encrypted
            try:
                decrypted = self._decrypt_img3_header(header)
                if len(decrypted) >= 4:
                    if struct.unpack('<I', decrypted[:4])[0] == 0xA94E2A52:
                        self.is_encrypted = True
                        return IMGVersion.VERSION_3
            except:
                pass
            
            # Check for DIR file as fallback
            dir_path = self.file_path.replace('.img', '.dir')
            if os.path.exists(dir_path):
                return IMGVersion.VERSION_1
        
        return IMGVersion.UNKNOWN
    
    def _parse_file(self) -> bool:
        """Parse IMG file based on detected version"""
        if self.version == IMGVersion.VERSION_1:
            return self._parse_version1()
        elif self.version == IMGVersion.VERSION_2:
            return self._parse_version2()
        elif self.version == IMGVersion.VERSION_3:
            return self._parse_version3()
        elif self.version == IMGVersion.FASTMAN92:
            return self._parse_fastman92()
        else:
            return False
    
    def _parse_version1(self) -> bool:
        """Parse IMG Version 1 (GTA III/VC)"""
        dir_path = self.file_path.replace('.img', '.dir')
        if not os.path.exists(dir_path):
            return False
        
        try:
            with open(dir_path, 'rb') as dir_file:
                dir_size = os.path.getsize(dir_path)
                entry_count = dir_size // 32
                
                for i in range(entry_count):
                    entry_data = dir_file.read(32)
                    if len(entry_data) != 32:
                        break
                    
                    # Parse DIR entry (32 bytes: offset, size, name)
                    offset_sectors, size_sectors = struct.unpack('<II', entry_data[:8])
                    name_bytes = entry_data[8:32]
                    name = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
                    
                    entry = IMGEntry(name, offset_sectors * 2048, size_sectors * 2048)
                    entry._img_file_ref = self
                    self.entries.append(entry)
            
            return True
            
        except Exception as e:
            print(f"Error parsing IMG Version 1: {e}")
            return False
    
    def _parse_version2(self) -> bool:
        """Parse IMG Version 2 (GTA SA)"""
        try:
            self._file_handle.seek(0)
            
            # Read header (8 bytes: VER2 + entry count)
            header = self._file_handle.read(8)
            if len(header) != 8 or header[:4] != b'VER2':
                return False
            
            entry_count = struct.unpack('<I', header[4:8])[0]
            
            # Read entry table
            for i in range(entry_count):
                entry_data = self._file_handle.read(32)
                if len(entry_data) != 32:
                    break
                
                # Parse entry (32 bytes: offset, archive_size, streaming_size, name)
                offset_sectors, archive_size, streaming_size = struct.unpack('<III', entry_data[:12])
                name_bytes = entry_data[12:32]
                name = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
                
                # Use archive_size if available, otherwise streaming_size
                size_sectors = archive_size if archive_size != 0 else streaming_size
                
                entry = IMGEntry(name, offset_sectors * 2048, size_sectors * 2048)
                entry._img_file_ref = self
                self.entries.append(entry)
            
            return True
            
        except Exception as e:
            print(f"Error parsing IMG Version 2: {e}")
            return False
    
    def _parse_version3(self) -> bool:
        """Parse IMG Version 3 (GTA IV)"""
        try:
            self._file_handle.seek(0)
            
            if self.is_encrypted:
                return self._parse_version3_encrypted()
            else:
                return self._parse_version3_unencrypted()
                
        except Exception as e:
            print(f"Error parsing IMG Version 3: {e}")
            return False
    
    def _parse_version3_unencrypted(self) -> bool:
        """Parse unencrypted IMG Version 3"""
        # Read header (20 bytes)
        header = self._file_handle.read(20)
        if len(header) != 20:
            return False
        
        signature, version, entry_count, table_size, table_entry_size = struct.unpack('<IIIII', header)
        if signature != 0xA94E2A52 or version != 3:
            return False
        
        # Read entry table
        for i in range(entry_count):
            entry_data = self._file_handle.read(16)
            if len(entry_data) != 16:
                break
            
            # Parse entry (16 bytes: unknown, resource_type, offset, size_info)
            unknown, resource_type, offset_sectors, size_info = struct.unpack('<IIII', entry_data)
            
            # Extract size from size_info
            size_sectors = (size_info >> 11) & 0x1FFFFF
            flags = size_info & 0x7FF
            
            # Create entry (name will be read separately)
            entry = IMGEntry("", offset_sectors * 2048, size_sectors * 2048)
            entry._img_file_ref = self
            entry.flags = flags
            entry.rage_resource_type = resource_type
            self.entries.append(entry)
        
        # Read entry names
        for entry in self.entries:
            name_bytes = b""
            while True:
                byte = self._file_handle.read(1)
                if not byte or byte == b'\x00':
                    break
                name_bytes += byte
            entry.name = name_bytes.decode('ascii', errors='ignore')
            entry.extension = entry._extract_extension()
        
        return True
    
    def _parse_version3_encrypted(self) -> bool:
        """Parse encrypted IMG Version 3"""
        # This would require implementing the encryption/decryption
        # For now, return False as not implemented
        print("Encrypted IMG Version 3 not yet implemented")
        return False
    
    def _parse_fastman92(self) -> bool:
        """Parse Fastman92 format"""
        try:
            self._file_handle.seek(0)
            
            # Read first header (20 bytes: VERF + flags + author)
            header1 = self._file_handle.read(20)
            if len(header1) != 20 or header1[:4] != b'VERF':
                return False
            
            archive_flags = struct.unpack('<I', header1[4:8])[0]
            author = header1[8:20].rstrip(b'\x00').decode('ascii', errors='ignore')
            
            # Extract flags
            self.sub_version = archive_flags & 15
            self.encryption_type = (archive_flags >> 4) & 15
            self.game_type = (archive_flags >> 8) & 7
            self.is_encrypted = self.encryption_type != 0
            
            if self.is_encrypted:
                print("Encrypted Fastman92 format not supported")
                return False
            
            # Read second header (12 bytes: check + entry_count + reserved)
            header2 = self._file_handle.read(12)
            if len(header2) != 12:
                return False
            
            check, entry_count = struct.unpack('<II', header2[:8])
            if check != 1:
                return False
            
            # Read entries (64 bytes each)
            for i in range(entry_count):
                entry_data = self._file_handle.read(64)
                if len(entry_data) != 64:
                    break
                
                # Parse entry
                offset_sectors, uncompressed_sectors, padding1, compressed_sectors, padding2, flags = struct.unpack('<IHHHI', entry_data[:16])
                name_bytes = entry_data[16:56]
                name = name_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
                
                entry = IMGEntry(name, offset_sectors * 2048, compressed_sectors * 2048)
                entry._img_file_ref = self
                entry.uncompressed_size = uncompressed_sectors * 2048
                
                # Check compression
                compression_id = flags & 15
                if compression_id == 1:
                    entry.is_compressed = True
                    entry.compression_type = CompressionType.ZLIB
                elif compression_id == 2:
                    entry.is_compressed = True
                    entry.compression_type = CompressionType.LZ4
                
                self.entries.append(entry)
            
            return True
            
        except Exception as e:
            print(f"Error parsing Fastman92 format: {e}")
            return False
    
    def _read_entry_data(self, entry: IMGEntry) -> bytes:
        """Read and potentially decompress entry data"""
        if not self._file_handle:
            raise RuntimeError("IMG file not open")
        
        self._file_handle.seek(entry.offset)
        data = self._file_handle.read(entry.size)
        
        if entry.is_compressed:
            return self._decompress_data(data, entry.compression_type, entry.uncompressed_size)
        
        return data
    
    def _write_entry_data(self, entry: IMGEntry, data: bytes):
        """Write and potentially compress entry data"""
        # For now, just cache the data
        # Actual writing would happen during rebuild
        entry._cached_data = data
        entry.size = len(data)
        self._is_modified = True
    
    def _decompress_data(self, data: bytes, compression_type: CompressionType, uncompressed_size: int) -> bytes:
        """Decompress data based on compression type"""
        try:
            if compression_type == CompressionType.ZLIB:
                import zlib
                return zlib.decompress(data)
            elif compression_type == CompressionType.LZ4:
                try:
                    import lz4.frame
                    return lz4.frame.decompress(data)
                except ImportError:
                    print("LZ4 library not available")
                    return data
            elif compression_type == CompressionType.LZO_1X_999:
                # LZO decompression would need external library
                print("LZO decompression not implemented")
                return data
            else:
                return data
        except Exception as e:
            print(f"Decompression error: {e}")
            return data
    
    def _compress_data(self, data: bytes, compression_type: CompressionType, level: int = 6) -> bytes:
        """Compress data based on compression type"""
        try:
            if compression_type == CompressionType.ZLIB:
                import zlib
                return zlib.compress(data, level)
            elif compression_type == CompressionType.LZ4:
                try:
                    import lz4.frame
                    return lz4.frame.compress(data)
                except ImportError:
                    print("LZ4 library not available")
                    return data
            else:
                return data
        except Exception as e:
            print(f"Compression error: {e}")
            return data
    
    def _decrypt_img3_header(self, data: bytes) -> bytes:
        """Decrypt IMG3 header (placeholder implementation)"""
        # This would require the actual decryption algorithm
        # For now, return empty bytes
        return b""
    
    def _write_header(self, file_handle: BinaryIO):
        """Write appropriate header for IMG version"""
        if self.version == IMGVersion.VERSION_2:
            file_handle.write(b'VER2')
            file_handle.write(struct.pack('<I', 0))  # Entry count (will be updated)
        elif self.version == IMGVersion.VERSION_3:
            file_handle.write(struct.pack('<IIIII', 0xA94E2A52, 3, 0, 0, 16))
        # Version 1 doesn't need a header in the IMG file itself
    
    def _rebuild_version1(self, output_path: str) -> bool:
        """Rebuild IMG Version 1"""
        try:
            dir_path = output_path.replace('.img', '.dir')
            
            # Calculate new offsets
            current_offset = 0
            for entry in self.entries:
                entry.offset = current_offset
                current_offset += entry.get_padded_size()
            
            # Write DIR file
            with open(dir_path, 'wb') as dir_file:
                for entry in self.entries:
                    dir_file.write(struct.pack('<II', entry.get_sectors_offset(), entry.get_sectors_size()))
                    name_bytes = entry.name.encode('ascii')[:24].ljust(24, b'\x00')
                    dir_file.write(name_bytes)
            
            # Write IMG file
            with open(output_path, 'wb') as img_file:
                for entry in self.entries:
                    data = entry.get_data()
                    padded_size = entry.get_padded_size()
                    img_file.write(data.ljust(padded_size, b'\x00'))
            
            return True
            
        except Exception as e:
            print(f"Error rebuilding Version 1: {e}")
            return False
    
    def _rebuild_version2(self, output_path: str) -> bool:
        """Rebuild IMG Version 2"""
        try:
            # Calculate header size and body start
            header_size = 8 + (len(self.entries) * 32)
            body_start = ((header_size + 2047) // 2048) * 2048  # Align to sector
            
            # Calculate new offsets
            current_offset = body_start
            for entry in self.entries:
                entry.offset = current_offset
                current_offset += entry.get_padded_size()
            
            with open(output_path, 'wb') as img_file:
                # Write header
                img_file.write(b'VER2')
                img_file.write(struct.pack('<I', len(self.entries)))
                
                # Write entry table
                for entry in self.entries:
                    img_file.write(struct.pack('<III', entry.get_sectors_offset(), entry.get_sectors_size(), entry.get_sectors_size()))
                    name_bytes = entry.name.encode('ascii')[:20].ljust(20, b'\x00')
                    img_file.write(name_bytes)
                
                # Pad to sector boundary
                current_pos = img_file.tell()
                if current_pos < body_start:
                    img_file.write(b'\x00' * (body_start - current_pos))
                
                # Write entry data
                for entry in self.entries:
                    data = entry.get_data()
                    padded_size = entry.get_padded_size()
                    img_file.write(data.ljust(padded_size, b'\x00'))
            
            return True
            
        except Exception as e:
            print(f"Error rebuilding Version 2: {e}")
            return False
    
    def _rebuild_version3(self, output_path: str) -> bool:
        """Rebuild IMG Version 3"""
        # This would be more complex due to the different structure
        # For now, return False as not implemented
        print("IMG Version 3 rebuilding not yet implemented")
        return False
    
    def _rebuild_fastman92(self, output_path: str) -> bool:
        """Rebuild Fastman92 format"""
        # This would require implementing the full Fastman92 format writing
        # For now, return False as not implemented
        print("Fastman92 rebuilding not yet implemented")
        return False


# Utility functions
def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def detect_img_version(file_path: str) -> IMGVersion:
    """Detect IMG version without fully opening the file"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            
        if len(header) < 4:
            return IMGVersion.UNKNOWN
        
        signature = header[:4]
        
        if signature == b'VER2':
            return IMGVersion.VERSION_2
        elif signature == b'VERF':
            return IMGVersion.FASTMAN92
        elif struct.unpack('<I', signature)[0] == 0xA94E2A52:
            return IMGVersion.VERSION_3
        else:
            # Check for DIR file
            dir_path = file_path.replace('.img', '.dir')
            if os.path.exists(dir_path):
                return IMGVersion.VERSION_1
                
    except Exception:
        pass
    
    return IMGVersion.UNKNOWN


# Example usage and testing
if __name__ == "__main__":
    # Test basic functionality
    img = IMGFile()
    
    # Test creating new IMG
    print("Testing IMG creation...")
    if img.create_new("test.img", IMGVersion.VERSION_2):
        print("✓ Created new IMG file")
        
        # Add test entry
        test_data = b"Hello, IMG Factory!"
        entry = img.add_entry("test.txt", test_data)
        print(f"✓ Added entry: {entry.name}")
        
        # Test rebuild
        if img.rebuild():
            print("✓ Rebuilt IMG file")
        
        img.close()
        
        # Clean up
        if os.path.exists("test.img"):
            os.remove("test.img")
    
    print("IMG Manager tests completed!")
