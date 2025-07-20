#this belongs in components/img_core_classes.py - Version: 6
# X-Seti - July20 2025 - IMG Factory 1.5 - IMG Core Classes - CIRCULAR IMPORT FIXED
# FIXED: Removed circular import with img_platform_detection.py
# PRESERVED: 100% of original functionality - all classes and methods intact

"""
IMG Core Classes - Fixed Circular Import Issue - COMPLETE RESTORATION
Core classes for handling IMG files with proper RW version detection
FIXED: Moved platform detection inline to eliminate circular import
Uses existing functions from core/rw_versions.py and maintains all original functionality
"""

import os
import struct
import json
import shutil
from enum import Enum
from typing import List, Dict, Optional, Any, Union, BinaryIO
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLineEdit, QGroupBox, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt

# Import existing RW version functions - NO CIRCULAR IMPORT
from core.rw_versions import get_rw_version_name, parse_rw_version, get_model_format_version
from components.img_debug_functions import img_debugger

##Methods list -
# create_entries_table_panel
# create_img_file
# detect_img_version
# format_file_size
# get_img_platform_info
# integrate_filtering
# populate_table_with_sample_data

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

class IMGVersion(Enum):
    """IMG Archive Version Types"""
    VERSION_1 = 1    # DIR/IMG pair (GTA3, VC)
    VERSION_2 = 2    # Single IMG file (SA)
    UNKNOWN = 0

class IMGPlatform(Enum):
    """Platform types for IMG files - MOVED HERE TO AVOID CIRCULAR IMPORT"""
    PC = "pc"
    PS2 = "ps2" 
    XBOX = "xbox"
    PSP = "psp"
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"

class FileType(Enum):
    """File types found in IMG archives"""
    DFF = "dff"         # 3D Models
    TXD = "txd"         # Texture Dictionary
    COL = "col"         # Collision Data
    IFP = "ifp"         # Animation Data
    IPL = "ipl"         # Item Placement
    IDE = "ide"         # Item Definition
    DAT = "dat"         # Data files
    SCM = "scm"         # Script files
    UNKNOWN = "unknown"

class Platform(Enum):
    """Platform types for IMG files"""
    PC = 0
    XBOX = 1
    PS2 = 2
    MOBILE = 3

class CompressionType(Enum):
    """Compression types for IMG entries"""
    NONE = 0
    ZLIB = 1
    LZ4 = 2
    CUSTOM = 3

class RecentFilesManager:
    """Manages recently opened IMG files"""
    
    def __init__(self, max_files: int = 10): #vers 1
        self.max_files = max_files
        self.recent_files: List[str] = []
        self.settings_file = "recent_files.json"
        self._load_recent_files()
    
    def _load_recent_files(self): #vers 1
        """Load recent files from settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.recent_files = json.load(f)
        except Exception:
            self.recent_files = []
    
    def _save_recent_files(self): #vers 1
        """Save recent files to settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.recent_files, f)
        except Exception:
            pass
    
    def add_file(self, file_path: str): #vers 1
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[:self.max_files]
        
        self._save_recent_files()
    
    def get_recent_files(self) -> List[str]: #vers 1
        """Get list of recent files, filtering out non-existent ones"""
        existing_files = [f for f in self.recent_files if os.path.exists(f)]
        if len(existing_files) != len(self.recent_files):
            self.recent_files = existing_files
            self._save_recent_files()
        return self.recent_files

class ValidationResult:
    """Results from entry validation"""
    def __init__(self): #vers 1
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, message: str): #vers 1
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str): #vers 1
        self.warnings.append(message)

class IMGEntry:
    """Represents a single file entry within an IMG archive - FIXED WITH RW VERSION DETECTION"""
    
    def __init__(self): #vers 4
        self.name: str = ""
        self.extension: str = ""
        self.offset: int = 0          # Offset in bytes
        self.size: int = 0            # Size in bytes
        self.uncompressed_size: int = 0
        self.file_type: FileType = FileType.UNKNOWN
        self.compression_type: CompressionType = CompressionType.NONE
        self.rw_version: int = 0      # RenderWare version
        self.rw_version_name: str = "" # ADDED: Human readable version name
        self.is_encrypted: bool = False
        self.is_new_entry: bool = False
        self.is_replaced: bool = False
        self.flags: int = 0
        self.compression_level = 0

        # Internal data cache
        self._cached_data: Optional[bytes] = None
        self._img_file: Optional['IMGFile'] = None
        self._version_detected: bool = False # ADDED: Track if version was detected
    
    def set_img_file(self, img_file: 'IMGFile'): #vers 1
        """Set reference to parent IMG file"""
        self._img_file = img_file

    def detect_file_type_and_version(self): #vers 1
        """ADDED: Detect file type and RW version from file data"""
        try:
            # Extract extension from name
            if '.' in self.name:
                self.extension = self.name.split('.')[-1].lower()
                self.file_type = self._get_file_type_from_extension()
            
            # For RenderWare files, detect version from data
            if self.is_renderware_file() and self._img_file and not self._version_detected:
                try:
                    data = self.get_data()
                    if len(data) >= 12:  # Minimum RW header size
                        # Use existing RW version detection function
                        version_info = parse_rw_version(data)
                        if version_info and 'version' in version_info:
                            self.rw_version = version_info['version']
                            self.rw_version_name = get_rw_version_name(self.rw_version)
                            self._version_detected = True
                            
                            if hasattr(img_debugger, 'debug'):
                                img_debugger.debug(f"✅ RW Version detected for {self.name}: {self.rw_version_name}")
                
                except Exception as e:
                    if hasattr(img_debugger, 'warning'):
                        img_debugger.warning(f"Could not detect RW version for {self.name}: {e}")
                    
        except Exception as e:
            if hasattr(img_debugger, 'error'):
                img_debugger.error(f"Error detecting file type/version for {self.name}: {e}")

    def get_version_text(self): #vers 1
        """Get version text for display"""
        if self.rw_version_name:
            return self.rw_version_name
        elif self.rw_version > 0:
            return f"RW {self.rw_version:08X}"
        else:
            return "Unknown"
    
    def _get_file_type_from_extension(self) -> FileType: #vers 1
        """Get file type from extension"""
        ext_lower = self.extension.lower()
        try:
            return FileType(ext_lower)
        except ValueError:
            return FileType.UNKNOWN
    
    def is_renderware_file(self) -> bool: #vers 1
        """Check if file is a RenderWare format"""
        return self.extension.upper() in ['DFF', 'TXD']
    
    def validate(self) -> ValidationResult: #vers 1
        """Validate entry data"""
        result = ValidationResult()
        
        try:
            # Check basic attributes
            if not self.name:
                result.add_error("Entry has no name")
            
            if self.size < 0:
                result.add_error("Entry has negative size")
            
            if self.offset < 0:
                result.add_error("Entry has negative offset")
            
            # Check name validity
            if len(self.name) > 24:
                result.add_warning("Entry name longer than 24 characters")
            
            invalid_chars = set('\x00\xff\xcd')
            if any(char in self.name for char in invalid_chars):
                result.add_error("Entry name contains invalid characters")
            
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
    
    def get_data(self) -> bytes: #vers 1
        """Read entry data from IMG file"""
        if not self._img_file:
            raise ValueError("No IMG file reference set")
        
        return self._img_file.read_entry_data(self)
    
    def set_data(self, data: bytes): #vers 1
        """Write entry data to IMG file"""
        if not self._img_file:
            raise ValueError("No IMG file reference set")
        
        self._img_file.write_entry_data(self, data)

def detect_img_platform_inline(file_path: str) -> IMGPlatform: #vers 1
    """MOVED: Simple platform detection to avoid circular import"""
    try:
        filename = os.path.basename(file_path).lower()
        
        # Simple platform detection based on filename/path
        if any(keyword in filename for keyword in ['ps2', 'playstation']):
            return IMGPlatform.PS2
        elif any(keyword in filename for keyword in ['xbox']):
            return IMGPlatform.XBOX
        elif any(keyword in filename for keyword in ['android', 'mobile']):
            return IMGPlatform.ANDROID
        elif any(keyword in filename for keyword in ['psp', 'stories']):
            return IMGPlatform.PSP
        else:
            return IMGPlatform.PC
            
    except Exception:
        return IMGPlatform.UNKNOWN

def get_img_platform_info(file_path: str) -> Dict[str, Any]: #vers 1
    """Get platform information for IMG file"""
    platform = detect_img_platform_inline(file_path)
    return {
        'platform': platform.value,
        'detected_from': 'filename_analysis',
        'supported_features': {
            'compression': platform in [IMGPlatform.PC, IMGPlatform.ANDROID],
            'encryption': False,
            'large_files': platform != IMGPlatform.PSP
        }
    }

class IMGFile:
    """Main IMG archive file handler - FIXED WITH PLATFORM SUPPORT"""
    
    def __init__(self, file_path: str = ""): #vers 5
        self.file_path: str = file_path
        self.version: IMGVersion = IMGVersion.UNKNOWN
        self.platform: IMGPlatform = IMGPlatform.UNKNOWN  # ADDED: Platform detection
        self.platform_specs: Dict[str, Any] = {}  # ADDED: Platform-specific specs
        self.entries: List[IMGEntry] = []
        self.is_open: bool = False
        self.total_size: int = 0
        self.creation_time: Optional[float] = None
        self.modification_time: Optional[float] = None

        # File handles
        self._img_handle: Optional[BinaryIO] = None
        self._dir_handle: Optional[BinaryIO] = None
    
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
                    self.file_path = creator.file_path
                return success
                
            else:
                print(f"❌ Unsupported IMG version: {version}")
                return False

        except Exception as e:
            print(f"❌ Error creating IMG file: {e}")
            return False

    def detect_version(self) -> IMGVersion: #vers 4
        """Detect IMG version and platform from file"""
        try:
            if not os.path.exists(self.file_path):
                return IMGVersion.UNKNOWN

            # ADDED: Platform detection first - using inline function
            self.platform = detect_img_platform_inline(self.file_path)
            
            if hasattr(img_debugger, 'debug'):
                img_debugger.debug(f"Detected platform: {self.platform.value}")

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
            print(f"[ERROR] Error detecting IMG version: {e}")

        self.version = IMGVersion.UNKNOWN
        return IMGVersion.UNKNOWN

    def open(self) -> bool: #vers 5
        """Open and parse IMG file - FIXED WITH PROPER ENTRY PARSING"""
        try:
            if self.is_open:
                return True

            # Detect version first
            if self.version == IMGVersion.UNKNOWN:
                self.detect_version()

            # Clear existing entries
            self.entries.clear()

            # Open based on version
            success = False
            if self.version == IMGVersion.VERSION_1:
                success = self._open_version_1()
            elif self.version == IMGVersion.VERSION_2:
                success = self._open_version_2()

            if success:
                self.is_open = True
                # ADDED: Detect file types and RW versions for all entries
                for entry in self.entries:
                    entry.detect_file_type_and_version()
                
                if hasattr(img_debugger, 'success'):
                    img_debugger.success(f"Opened {self.file_path} with {len(self.entries)} entries")
                
            return success

        except Exception as e:
            print(f"[ERROR] Error opening IMG file: {e}")
            return False

    def _open_version_2(self) -> bool: #vers 4
        """Open IMG version 2 (single file)"""
        try:
            with open(self.file_path, 'rb') as f:
                header = f.read(8)
                if len(header) < 8:
                    return False

                if header[:4] != b'VER2':
                    return False

                entry_count = struct.unpack('<I', header[4:8])[0]
                
                for i in range(entry_count):
                    entry_data = f.read(32)
                    if len(entry_data) < 32:
                        break

                    entry_offset, entry_size = struct.unpack('<II', entry_data[:8])
                    entry_name = entry_data[8:32].rstrip(b'\x00').decode('ascii', errors='ignore')

                    if entry_name:
                        entry = IMGEntry()
                        entry.name = entry_name
                        entry.offset = entry_offset * 2048  # Convert sectors to bytes
                        entry.size = entry_size * 2048
                        entry.set_img_file(self)
                        self.entries.append(entry)

            return True
        except Exception as e:
            print(f"[ERROR] Error opening Version 2 IMG: {e}")
            return False

    def _open_version_1(self) -> bool: #vers 4
        """Open IMG version 1 (DIR/IMG pair)"""
        dir_path = self.file_path[:-4] + '.dir'
        if not os.path.exists(dir_path):
            return False

        try:
            with open(dir_path, 'rb') as dir_file:
                dir_data = dir_file.read()

            # Parse directory entries (32 bytes each)
            entry_count = len(dir_data) // 32
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
                    entry.offset = entry_offset * 2048  # Convert sectors to bytes
                    entry.size = entry_size * 2048
                    entry.set_img_file(self)
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
        """Close IMG file"""
        self.is_open = False
        self.entries.clear()

    def get_creation_info(self) -> Dict[str, Any]: #vers 1
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
                'platform': self.platform.value,
                'format': f'IMG Version {self.version.value}'
            }
        except Exception:
            return {}

def format_file_size(size_bytes: int) -> str: #vers 1
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def create_img_file(output_path: str, version: IMGVersion, **options) -> bool: #vers 1
    """Create IMG file using appropriate version creator"""
    img = IMGFile()
    return img.create_new(output_path, version, **options)

def detect_img_version(file_path: str) -> IMGVersion: #vers 1
    """Detect IMG version from file path"""
    img = IMGFile(file_path)
    return img.detect_version()

# RESTORED: Complete GUI classes that were missing from the fixed version
class IMGEntriesTable(QTableWidget):
    """Enhanced table widget for IMG entries"""
    entry_double_clicked = pyqtSignal(object)
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(['Name', 'Type', 'Size', 'Offset', 'Version', 'Compression', 'Status'])
        
        # Setup table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Auto-resize columns
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(6):
            header.setSectionResizeMode(i, header.ResizeMode.ResizeToContents)

    def populate_entries(self, entries: List[IMGEntry]): #vers 1
        """Populate table with IMG entries"""
        self.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.setItem(row, 0, QTableWidgetItem(entry.name))
            
            # Type
            self.setItem(row, 1, QTableWidgetItem(entry.extension.upper()))
            
            # Size
            self.setItem(row, 2, QTableWidgetItem(format_file_size(entry.size)))
            
            # Offset
            self.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:08X}"))
            
            # Version
            version_text = entry.get_version_text() if hasattr(entry, 'get_version_text') else "Unknown"
            self.setItem(row, 4, QTableWidgetItem(version_text))
            
            # Compression
            compression_text = entry.compression_type.name if hasattr(entry.compression_type, 'name') else "None"
            self.setItem(row, 5, QTableWidgetItem(compression_text))
            
            # Status
            status = "Modified" if entry.is_replaced else "New" if entry.is_new_entry else "Original"
            self.setItem(row, 6, QTableWidgetItem(status))

    def apply_filter(self, filter_text: str): #vers 1
        """Apply filter to table entries"""
        for row in range(self.rowCount()):
            item = self.item(row, 0)  # Name column
            if item:
                should_show = filter_text.lower() in item.text().lower()
                self.setRowHidden(row, not should_show)

class FilterPanel(QWidget):
    """Filter panel for IMG entries"""
    filter_changed = pyqtSignal(str)
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        layout = QVBoxLayout(self)
        
        # File type filter
        type_group = QGroupBox("File Type Filter")
        type_layout = QHBoxLayout(type_group)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['All', 'DFF', 'TXD', 'COL', 'IFP', 'IPL', 'DAT', 'WAV'])
        self.type_combo.currentTextChanged.connect(self.filter_changed.emit)
        type_layout.addWidget(self.type_combo)
        
        # Search filter
        search_group = QGroupBox("Search")
        search_layout = QHBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search entries...")
        self.search_edit.textChanged.connect(self.filter_changed.emit)
        search_layout.addWidget(self.search_edit)
        
        layout.addWidget(type_group)
        layout.addWidget(search_group)

class IMGFileInfoPanel(QWidget):
    """Information panel for IMG file details"""
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel("No IMG file loaded")
        layout.addWidget(self.info_label)

    def update_info(self, img_file: IMGFile): #vers 1
        """Update panel with IMG file information"""
        if img_file and img_file.file_path:
            info = img_file.get_creation_info()
            text = f"File: {os.path.basename(info.get('path', 'Unknown'))}\n"
            text += f"Size: {info.get('size_mb', 0):.1f} MB\n"
            text += f"Entries: {info.get('entries_count', 0)}\n"
            text += f"Version: {info.get('version', 'Unknown')}\n"
            text += f"Platform: {info.get('platform', 'Unknown')}"
            self.info_label.setText(text)
        else:
            self.info_label.setText("No IMG file loaded")

class TabFilterWidget(QWidget):
    """Tab-specific filter widget"""
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        layout = QHBoxLayout(self)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['All Files', 'Models (DFF)', 'Textures (TXD)', 'Collision (COL)', 'Animations (IFP)'])
        layout.addWidget(self.filter_combo)

def integrate_filtering(main_window): #vers 2
    """Integrate filtering functionality into main window"""
    try:
        # Create filter widget
        filter_widget = FilterPanel(main_window)

        # Connect filter widget to table
        if hasattr(main_window, 'entries_table') and hasattr(filter_widget, 'filter_changed'):
            filter_widget.filter_changed.connect(main_window.entries_table.apply_filter)

        return filter_widget
    except Exception as e:
        if hasattr(img_debugger, 'error'):
            img_debugger.error(f"Error integrating filtering: {e}")
        return None

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
    if hasattr(main_window.filter_panel, 'filter_changed') and hasattr(main_window.entries_table, 'apply_filter'):
        main_window.filter_panel.filter_changed.connect(main_window.entries_table.apply_filter)

    # SIMPLIFIED CONNECTION - Let main app handle its own signals
    # Don't auto-connect anything from here to prevent conflicts

    if hasattr(main_window, 'on_entry_double_clicked'):
        # Only connect double-click since that doesn't cause logging conflicts
        try:
            main_window.entries_table.entry_double_clicked.disconnect()
        except:
            pass
        main_window.entries_table.entry_double_clicked.connect(main_window.on_entry_double_clicked)

    return panel

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

        def get_version_text(self): #vers 1
            return self._version

    mock_entries = [MockEntry(data) for data in sample_entries]
    if hasattr(table, 'populate_entries'):
        table.populate_entries(mock_entries)

# Export classes and functions
__all__ = [
    'IMGVersion',
    'IMGPlatform',
    'FileType', 
    'CompressionType',
    'Platform',
    'IMGEntry',
    'IMGFile',
    'ValidationResult',
    'RecentFilesManager',
    'create_img_file',
    'detect_img_version',
    'format_file_size',
    'get_img_platform_info',
    'IMGEntriesTable',
    'FilterPanel', 
    'IMGFileInfoPanel',
    'TabFilterWidget',
    'integrate_filtering',
    'create_entries_table_panel',
    'populate_table_with_sample_data'
]