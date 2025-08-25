#this belongs in components/img_core_classes.py - Version: 6
# X-Seti - August24 2025 - IMG Factory 1.5 - Ported IMG_Editor Core Classes


import os
import struct
import math
from typing import Optional, List, Dict, Any


# Constants from IMG_Editor
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24
V1_SIGNATURE = b'VER2'  # DIR file signature
V2_SIGNATURE = b'VER2'  # IMG file signature

class IMGEntry:
    """IMG entry representing a file within an archive"""

    def __init__(self):
        self.name: str = ""
        self.actual_offset: int = 0
        self.actual_size: int = 0
        self.data: Optional[bytes] = None
        self.is_new_entry: bool = False
        self.is_modified: bool = False

    def get_data(self, archive=None) -> Optional[bytes]:
        """Get entry data - from memory or file"""
        try:
            if self.data is not None:
                return self.data

            if archive and hasattr(archive, 'file_path') and archive.file_path:
                # Read from file
                with open(archive.file_path, 'rb') as f:
                    f.seek(self.actual_offset)
                    self.data = f.read(self.actual_size)
                    return self.data

            return None
        except Exception:
            return None

    def set_data(self, data: bytes):
        """Set entry data"""
        self.data = data
        self.actual_size = len(data) if data else 0
        self.is_modified = True


class IMGArchive:
    """IMG archive handler - ported from working IMG_Editor"""

    def __init__(self):
        self.file_path: str = ""
        self.version: str = "V2"  # V1 or V2
        self.entries: List[IMGEntry] = []
        self.is_modified: bool = False

    def load_from_file(self, file_path: str) -> bool:
        """Load IMG archive from file"""
        try:
            self.file_path = file_path

            # Detect version
            if file_path.lower().endswith('.dir'):
                self.version = 'V1'
                return self._load_version1()
            else:
                self.version = 'V2'
                return self._load_version2()
        except Exception:
            return False

    def _load_version1(self) -> bool:
        """Load Version 1 IMG (DIR/IMG pair)"""
        try:
            dir_path = self.file_path
            img_path = self.file_path.replace('.dir', '.img')

            if not os.path.exists(dir_path) or not os.path.exists(img_path):
                return False

            # Read DIR file
            with open(dir_path, 'rb') as f:
                entries_data = f.read()

            # Parse entries (32 bytes each)
            entry_count = len(entries_data) // 32
            self.entries = []

            for i in range(entry_count):
                offset = i * 32
                entry_data = entries_data[offset:offset + 32]

                if len(entry_data) < 32:
                    break

                # Unpack entry: offset(4), size(4), name(24)
                offset_sectors, size_sectors = struct.unpack('<II', entry_data[:8])
                name_bytes = entry_data[8:32]

                # Convert to actual values
                actual_offset = offset_sectors * SECTOR_SIZE
                actual_size = size_sectors * SECTOR_SIZE

                # Extract name
                name_end = name_bytes.find(b'\\x00')
                if name_end != -1:
                    name = name_bytes[:name_end].decode('ascii', errors='ignore')
                else:
                    name = name_bytes.decode('ascii', errors='ignore').rstrip('\\x00')

                # Create entry
                entry = IMGEntry()
                entry.name = name
                entry.actual_offset = actual_offset
                entry.actual_size = actual_size

                self.entries.append(entry)

            return True

        except Exception:
            return False

    def _load_version2(self) -> bool:
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
                    name_end = name_bytes.find(b'\\x00')
                    if name_end != -1:
                        name = name_bytes[:name_end].decode('ascii', errors='ignore')
                    else:
                        name = name_bytes.decode('ascii', errors='ignore').rstrip('\\x00')

                    # Create entry
                    entry = IMGEntry()
                    entry.name = name
                    entry.actual_offset = actual_offset
                    entry.actual_size = actual_size

                    self.entries.append(entry)

            return True

        except Exception:
            return False

    def add_entry(self, entry_name: str, data: bytes) -> bool:
        """Add or update entry in archive"""
        try:
            # Check if entry already exists
            existing_entry = self.get_entry_by_name(entry_name)

            if existing_entry:
                # Update existing entry
                existing_entry.set_data(data)
            else:
                # Create new entry
                new_entry = IMGEntry()
                new_entry.name = entry_name
                new_entry.set_data(data)
                new_entry.is_new_entry = True

                self.entries.append(new_entry)

            self.is_modified = True
            return True

        except Exception:
            return False

    def get_entry_by_name(self, entry_name: str) -> Optional[IMGEntry]:
        """Find entry by name"""
        try:
            for entry in self.entries:
                if entry.name == entry_name:
                    return entry
            return None
        except Exception:
            return None

    def remove_entry(self, entry_name: str) -> bool:
        """Remove entry by name"""
        try:
            entry = self.get_entry_by_name(entry_name)
            if entry:
                self.entries.remove(entry)
                self.is_modified = True
                return True
            return False
        except Exception:
            return False
