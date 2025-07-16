#this belongs in components/ img_core_classes.py - Version: 3
# X-Seti - July16 2025 - Img Factory 1.5

"""
IMG Core Classes - Updated to use separate version creators
Removed embedded creation methods, now imports from version-specific files
"""

import struct
import os
import zlib
import hashlib
import json
from enum import Enum
from typing import List, Optional, BinaryIO, Dict, Tuple
from pathlib import Path
from typing import List, Optional, Dict, Any, BinaryIO

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QHeaderView, QAbstractItemView, QComboBox, QLineEdit,
    QPushButton, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction
from enum import Enum

# Import version-specific creators
from components.img_version1 import IMGVersion1Creator, create_version_1_img
from components.img_version2 import IMGVersion2Creator, create_version_2_img


class IMGVersion(Enum):
    """IMG file format versions"""
    UNKNOWN = 0
    VERSION_1 = 1  # GTA3, VC - separate DIR+IMG files
    VERSION_2 = 2  # SA - single IMG file with VER2 header


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
                # Use new Version 1 creator
                from components.img_version1 import IMGVersion1Creator
                creator = IMGVersion1Creator()
                success = creator.create_version_1(output_path, initial_size_mb)
                if success:
                    self.entries = creator.entries
                    self.file_path = creator.dir_path  # Store DIR file path for Version 1
                return success
            elif version == IMGVersion.VERSION_2:
                # Use new Version 2 creator
                from components.img_version2 import IMGVersion2Creator
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

    def open(self) -> bool:
        """Open IMG file for reading"""
        if not os.path.exists(self.file_path):
            return False

        self.version = self.detect_version()
        if self.version == IMGVersion.UNKNOWN:
            return False

        try:
            if self.version == IMGVersion.VERSION_1:
                return self._open_version_1()
            elif self.version == IMGVersion.VERSION_2:
                return self._open_version_2()
            else:
                return False
        except Exception:
            return False

    def detect_version(self) -> IMGVersion:
        """Detect IMG file version from header"""
        if not os.path.exists(self.file_path):
            return IMGVersion.UNKNOWN

        # Check if it's a DIR file (IMG version 1)
        if self.file_path.lower().endswith('.dir'):
            img_path = self.file_path[:-4] + '.img'
            if os.path.exists(img_path):
                return IMGVersion.VERSION_1
            return IMGVersion.UNKNOWN

        # Read header to detect version
        try:
            with open(self.file_path, 'rb') as f:
                header = f.read(4)
                if len(header) < 4:
                    return IMGVersion.UNKNOWN

                # Check for version 2 (VER2 signature)
                if header[:4] == b'VER2':
                    return IMGVersion.VERSION_2

                # Check if corresponding DIR file exists (version 1)
                dir_path = self.file_path[:-4] + '.dir'
                if os.path.exists(dir_path):
                    return IMGVersion.VERSION_1
        except Exception:
            pass

        return IMGVersion.UNKNOWN

    def _open_version_2(self) -> bool:
        """Open IMG version 2 (single file)"""
        try:
            with open(self.file_path, 'rb') as f:
                # Skip VER2 header (4 bytes)
                f.seek(4)
                # Read entry count
                entry_count = struct.unpack('<I', f.read(4))[0]

                for i in range(entry_count):
                    # Read entry: offset(4), size(4), name(24)
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
        except Exception:
            return False

    def _open_version_1(self) -> bool:
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


class IMGEntriesTable(QTableWidget):
    """Enhanced table widget for displaying IMG entries"""

    entries_selected = pyqtSignal(list)
    entry_double_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()
        self.entries = []

    def _setup_table(self): #kept
        """Setup table appearance and headers"""
        headers = ["Name", "Type", "Size", "Offset", "Version", "Compression", "Status"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)

        # Header properties
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 200)  # Name
        header.resizeSection(1, 60)   # Type
        header.resizeSection(2, 80)   # Size
        header.resizeSection(3, 80)   # Offset
        header.resizeSection(4, 100)  # Version
        header.resizeSection(5, 100)  # Compression

        # Enable sorting
        self.setSortingEnabled(True)


    def populate_entries(self, entries: List[IMGEntry]): #kept
        """Populate table with IMG entries"""
        self.entries = entries
        self.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            # Name
            self.setItem(row, 0, QTableWidgetItem(entry.name))

            # Type
            type_text = entry.extension if entry.extension else "UNK"
            self.setItem(row, 1, QTableWidgetItem(type_text))

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

    def get_selected_entries(self) -> List[int]: #kept
        """Get list of selected entry indices"""
        selected_rows = []
        for item in self.selectedItems():
            if item.column() == 0:  # Only process first column
                selected_rows.append(item.row())
        return sorted(set(selected_rows))

    def get_selected_entry_names(self) -> List[str]:
        """Get list of selected entry names for logging"""
        selected_names = []
        selected_rows = self.get_selected_entries()
        for row in selected_rows:
            name_item = self.item(row, 0)
            if name_item:
                selected_names.append(name_item.text())
        return selected_names

    def get_selection_summary(self) -> str:
        """Get a summary of current selection for logging"""
        selected_rows = self.get_selected_entries()
        if not selected_rows:
            return "No entries selected"
        elif len(selected_rows) == 1:
            name_item = self.item(selected_rows[0], 0)
            if name_item:
                return f"Selected: {name_item.text()}"
            return "1 entry selected"
        else:
            return f"{len(selected_rows)} entries selected"

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

    def apply_filter(self, filter_text="", file_type="All Files"): #kept
        """Apply filtering to table entries - FIXED VERSION"""
        if not hasattr(self, 'entries') or not self.entries:
            return

        # Convert filter_text to lowercase for case-insensitive search
        filter_text_lower = filter_text.lower() if filter_text else ""

        for row in range(self.rowCount()):
            show_row = True

            # Get the actual entry for this row
            if row < len(self.entries):
                entry = self.entries[row]

                # Filter by file type
                if file_type != "All Files":
                    entry_type = entry.extension.upper() if entry.extension else "UNK"

                    type_filters = {
                        "Models (DFF)": ["DFF"],
                        "Textures (TXD)": ["TXD"],
                        "Collision (COL)": ["COL"],
                        "Animation (IFP)": ["IFP"],
                        "Audio (WAV)": ["WAV"],
                        "Scripts (SCM)": ["SCM"],
                        "Other": []  # Show everything not in above categories
                    }

                    if file_type in type_filters:
                        allowed_types = type_filters[file_type]
                        if file_type == "Other":
                            # Show files not in any of the main categories
                            all_main_types = ["DFF", "TXD", "COL", "IFP", "WAV", "SCM"]
                            if entry_type in all_main_types:
                                show_row = False
                        elif entry_type not in allowed_types:
                            show_row = False

                # Filter by search text
                if filter_text_lower and show_row:
                    # Search in entry name (case-insensitive)
                    if filter_text_lower not in entry.name.lower():
                        show_row = False

            # Show/hide the row
            self.setRowHidden(row, not show_row)


class FilterPanel(QWidget):
    """Enhanced filter panel with search and file type filtering"""

    filter_changed = pyqtSignal(str, str)  # search_text, file_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup filter panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMaximumWidth(60)

        # File type filter row
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("📂 Type:"))

        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems([
            "All Files",
            "Models (DFF)",
            "Textures (TXD)",
            "Collision (COL)",
            "Animation (IFP)",
            "Audio (WAV)",
            "Scripts (SCM)",
            "Other"
        ])
        filter_layout.addWidget(self.file_type_combo)

        # Recent files button
        self.recent_button = QPushButton("📋 Recent")
        self.recent_button.setMaximumWidth(80)
        filter_layout.addWidget(self.recent_button)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

    def _show_recent_files(self):
        """Show recent files menu"""
        recent_manager = RecentFilesManager()
        recent_files = recent_manager.get_recent_files()

        if not recent_files:
            QMessageBox.information(self, "Recent Files", "No recent files found.")
            return

        menu = QMenu(self)
        for file_path in recent_files:
            file_name = os.path.basename(file_path)
            action = QAction(file_name, self)
            action.setData(file_path)
            action.setToolTip(file_path)
            menu.addAction(action)

        # Show menu at button position
        button_pos = self.recent_button.mapToGlobal(self.recent_button.rect().bottomLeft())
        action = menu.exec(button_pos)

        if action:
            file_path = action.data()
            # Emit signal to parent to open file
            if hasattr(self.parent(), 'open_img_file'):
                self.parent().open_img_file(file_path)


class IMGFileInfoPanel(QWidget):
    """Panel showing IMG file information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup info panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # File info
        self.file_label = QLabel("No IMG file loaded")
        self.file_label.setFont(QFont("", 9, QFont.Weight.Bold))
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

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

def integrate_filtering(main_window, table_widget, filter_widget=None):
    """Integrate filtering functionality - compatibility function"""
    if filter_widget is None:
        filter_widget = FilterPanel(main_window)

    # Connect filter widget to table
    if hasattr(filter_widget, 'filter_changed'):
        filter_widget.filter_changed.connect(table_widget.apply_filter)

    return filter_widget


# Convenience functions for external use
def create_img_file(output_path: str, version: IMGVersion, **options) -> bool:
    """Create IMG file using appropriate version creator"""
    img = IMGFile()
    return img.create_new(output_path, version, **options)


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
    filter_group = QGroupBox("🔍 Filter & S")
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


def detect_img_version(file_path: str) -> IMGVersion:
    """Detect IMG version without fully opening the file"""
    img = IMGFile(file_path)
    return img.detect_version()


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


# Export classes and functions
__all__ = [
    'IMGVersion',
    'FileType', 
    'CompressionType',
    'IMGEntry',
    'IMGFile',
    'ValidationResult',
    'RecentFilesManager',
    'create_img_file'
]
    
