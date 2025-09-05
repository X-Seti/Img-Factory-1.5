#this belongs in components/ img_core_classes.py - Version: 10
# X-Seti - September04 2025 - IMG Factory 1.5 - IMG Core Classes CLEAN - Methods Moved

"""
IMG Core Classes - CLEAN VERSION
All shared methods moved to methods/ directory - NO DUPLICATES
Classes import methods from methods/ to avoid code duplication
"""

import os
import struct
from enum import Enum
from typing import List, Dict, Optional, Any, Union, BinaryIO
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QLineEdit, QGroupBox, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt

# Import shared methods from existing methods/ files
from methods.img_entry_operations import (
    add_entry_safe, remove_entry_safe, get_entry_safe, has_entry_safe,
    calculate_next_offset, sanitize_filename, validate_entry_data
)
from methods.img_operations_shared import (
    validate_img_structure, get_entry_data_safely
)
from methods.detect_file_type_version import (
    detect_entry_file_type_and_version, get_file_type_from_extension
)

# Import existing RW version functions
from core.rw_versions import get_rw_version_name, parse_rw_version, get_model_format_version
from components.img_debug_functions import img_debugger

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

##Methods list - NOW IN methods/ -
# Entry operations: add_entry_safe, remove_entry_safe, get_entry_safe, etc. -> methods/img_entry_operations.py
# File operations: create_img_file, rebuild_img, import_file_into_img, etc. -> methods/img_file_operations.py  
# Detection: detect_img_version, detect_img_platform, etc. -> methods/img_detection.py
# Utils: format_file_size, populate_table_with_sample_data -> methods/img_utils.py
# Validation: validate_img_structure, get_entry_data_safely -> methods/img_operations_shared.py

# Constants
V1_SIGNATURE = b"VER1"
V2_SIGNATURE = b"VER2"
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24

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
    UNKNOWN = "unknown"

class CompressionType(Enum): #vers 1
    """Compression types for entries"""
    NONE = 0
    ZLIB = 1
    UNKNOWN = -1

class FileType(Enum): #vers 1
    """File type classifications"""
    MODEL = "model"
    TEXTURE = "texture"
    COLLISION = "collision"
    ANIMATION = "animation"
    AUDIO = "audio"
    DATA = "data"
    UNKNOWN = "unknown"

class Platform(Enum): #vers 1
    """Game platform enum"""
    GTA3_PC = "gta3_pc"
    GTAVC_PC = "gtavc_pc"
    GTASA_PC = "gtasa_pc"
    GTA3_PS2 = "gta3_ps2"
    GTAVC_PS2 = "gtavc_ps2"
    GTASA_PS2 = "gtasa_ps2"
    UNKNOWN = "unknown"

class IMGEntry: #vers 1
    """Individual entry within IMG archive"""
    
    def __init__(self): #vers 1
        self.name = ""
        self.offset = 0
        self.size = 0
        self.actual_offset = 0
        self.actual_size = 0
        self.compression = CompressionType.NONE
        self.file_type = FileType.UNKNOWN
        self.extension = ""
        
        # RW data attributes
        self.rw_version = 0
        self.rw_version_string = ""
        self.rw_section_type = 0
        self.rw_section_size = 0
        
        # Data storage
        self.data = None
        self._cached_data = None
        self.is_new_entry = False
        self.is_modified = False
        
        # Parent IMG reference
        self.img_file = None
    
    def set_img_file(self, img_file): #vers 1
        """Set parent IMG file reference"""
        self.img_file = img_file
    
    def get_data(self) -> Optional[bytes]: #vers 1
        """Get entry data using shared method"""
        return get_entry_data_safely(self, self.img_file)
    
    def set_data(self, data: bytes): #vers 1
        """Set entry data"""
        self._cached_data = data
        self.size = len(data) if data else 0
        self.actual_size = self.size
        self.is_modified = True
    
    def detect_file_type(self): #vers 1
        """Detect file type using shared method"""
        try:
            detect_entry_file_type_and_version(self, self.img_file)
        except Exception:
            pass
    
    def __str__(self):
        return f"IMGEntry(name='{self.name}', size={self.size}, offset={self.offset})"
    
    def __repr__(self):
        return self.__str__()


class IMGFile: #vers 1
    """IMG Archive File Handler - Uses shared methods"""
    
    def __init__(self): #vers 1
        self.file_path = ""
        self.version = IMGVersion.UNKNOWN
        self.platform = IMGPlatform.UNKNOWN
        self.entries = []
        self.is_open = False
        self.modified = False
        
        # File handles
        self._img_handle = None
        self._dir_handle = None
        
        # Metadata
        self.total_size = 0
        self.header_size = 0
        self.creation_time = None
        self.modification_time = None
    
    def add_entry(self, filename: str, data: bytes, auto_save: bool = False) -> bool: #vers 1
        """Add entry using shared method"""
        return add_entry_safe(self, filename, data, auto_save)
    
    def remove_entry(self, filename: str) -> bool: #vers 1
        """Remove entry using shared method"""
        return remove_entry_safe(self, filename)
    
    def get_entry(self, filename: str) -> Optional[IMGEntry]: #vers 1
        """Get entry using shared method"""
        return get_entry_safe(self, filename)
    
    def has_entry(self, filename: str) -> bool: #vers 1
        """Check if entry exists using shared method"""
        return has_entry_safe(self, filename)
    
    def calculate_next_offset(self) -> int: #vers 1
        """Calculate next offset using shared method"""
        return calculate_next_offset(self)
    
    def validate_structure(self) -> tuple[bool, str]: #vers 1
        """Validate structure using shared method"""
        return validate_img_structure(self)
    
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
    
    def __str__(self):
        return f"IMGFile(path='{self.file_path}', version={self.version}, entries={len(self.entries)})"
    
    def __repr__(self):
        return self.__str__()


class RecentFilesManager: #vers 1
    """Manager for recent files list"""
    
    def __init__(self, max_files: int = 10): #vers 1
        self.max_files = max_files
        self.recent_files = []
    
    def add_file(self, file_path: str): #vers 1
        """Add file to recent files list"""
        try:
            # Remove if already in list
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            
            # Add to beginning
            self.recent_files.insert(0, file_path)
            
            # Trim to max size
            if len(self.recent_files) > self.max_files:
                self.recent_files = self.recent_files[:self.max_files]
        except Exception:
            pass
    
    def get_recent_files(self) -> List[str]: #vers 1
        """Get list of recent files"""
        # Filter out non-existent files
        existing_files = [f for f in self.recent_files if os.path.exists(f)]
        self.recent_files = existing_files
        return existing_files.copy()
    
    def clear(self): #vers 1
        """Clear recent files list"""
        self.recent_files.clear()


# GUI Classes (UI-specific, kept here)

class IMGEntriesTable(QTableWidget): #vers 1
    """Custom table widget for IMG entries"""
    
    entry_selected = pyqtSignal(str)  # Entry name
    entries_selected = pyqtSignal(list)  # List of entry names
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.img_file = None
        self.setup_table()
    
    def setup_table(self): #vers 1
        """Setup table structure"""
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "Name", "Size", "Type", "RW Version", "Offset", "Status"
        ])
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
    
    def set_img_file(self, img_file: IMGFile): #vers 1
        """Set IMG file and populate table"""
        self.img_file = img_file
        self.populate_entries()
    
    def populate_entries(self): #vers 1
        """Populate table with entries from IMG file"""
        if not self.img_file or not hasattr(self.img_file, 'entries'):
            self.setRowCount(0)
            return
        
        entries = self.img_file.entries
        self.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.setItem(row, 0, QTableWidgetItem(getattr(entry, 'name', '')))
            
            # Size - use shared format function
            try:
                from methods.img_utils import format_file_size
                size_str = format_file_size(getattr(entry, 'size', 0))
            except ImportError:
                size = getattr(entry, 'size', 0)
                size_str = f"{size} B"
            self.setItem(row, 1, QTableWidgetItem(size_str))
            
            # Type
            file_type = getattr(entry, 'file_type', FileType.UNKNOWN)
            if hasattr(file_type, 'value'):
                type_str = file_type.value
            else:
                type_str = str(file_type)
            self.setItem(row, 2, QTableWidgetItem(type_str))
            
            # RW Version
            rw_version = getattr(entry, 'rw_version_string', '')
            self.setItem(row, 3, QTableWidgetItem(rw_version))
            
            # Offset
            offset = getattr(entry, 'offset', 0)
            self.setItem(row, 4, QTableWidgetItem(f"0x{offset:08X}"))
            
            # Status
            status = "Modified" if getattr(entry, 'is_modified', False) else "Original"
            self.setItem(row, 5, QTableWidgetItem(status))
    
    def _on_selection_changed(self): #vers 1
        """Handle selection change"""
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
        
        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            name_item = self.item(row, 0)
            if name_item:
                self.entry_selected.emit(name_item.text())
        
        # Emit list of selected entries
        selected_names = []
        for row in selected_rows:
            name_item = self.item(row, 0)
            if name_item:
                selected_names.append(name_item.text())
        
        self.entries_selected.emit(selected_names)
    
    def get_selected_entries(self) -> List[str]: #vers 1
        """Get list of selected entry names"""
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
        
        selected_names = []
        for row in selected_rows:
            name_item = self.item(row, 0)
            if name_item:
                selected_names.append(name_item.text())
        
        return selected_names


class FilterPanel(QWidget): #vers 1
    """Panel for filtering entries"""
    
    filter_changed = pyqtSignal(str, str)  # filter_type, filter_value
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup filter UI"""
        layout = QHBoxLayout(self)
        
        # Filter type combo
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems([
            "All", "Name", "Type", "Extension", "Size", "RW Version"
        ])
        layout.addWidget(QLabel("Filter:"))
        layout.addWidget(self.filter_type_combo)
        
        # Filter value input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter value...")
        layout.addWidget(self.filter_input)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_filter)
        layout.addWidget(clear_btn)
        
        # Connect signals
        self.filter_type_combo.currentTextChanged.connect(self._emit_filter_changed)
        self.filter_input.textChanged.connect(self._emit_filter_changed)
    
    def _emit_filter_changed(self): #vers 1
        """Emit filter changed signal"""
        filter_type = self.filter_type_combo.currentText()
        filter_value = self.filter_input.text()
        self.filter_changed.emit(filter_type, filter_value)
    
    def clear_filter(self): #vers 1
        """Clear filter"""
        self.filter_type_combo.setCurrentText("All")
        self.filter_input.clear()


class IMGFileInfoPanel(QWidget): #vers 1
    """Panel showing IMG file information"""
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup info panel UI"""
        layout = QVBoxLayout(self)
        
        # Info group
        info_group = QGroupBox("IMG File Information")
        info_layout = QVBoxLayout(info_group)
        
        self.info_labels = {}
        info_fields = [
            ("File Path", "file_path"),
            ("Version", "version"),
            ("Platform", "platform"),
            ("Entry Count", "entry_count"),
            ("File Size", "file_size"),
            ("Total Data Size", "total_data_size"),
            ("Status", "status")
        ]
        
        for label_text, field_name in info_fields:
            label = QLabel(f"{label_text}: -")
            self.info_labels[field_name] = label
            info_layout.addWidget(label)
        
        layout.addWidget(info_group)
        layout.addStretch()
    
    def update_info(self, img_file: IMGFile): #vers 1
        """Update info panel with IMG file data"""
        try:
            if not img_file:
                self.clear_info()
                return
            
            # Basic info
            self.info_labels["file_path"].setText(f"File Path: {img_file.file_path}")
            self.info_labels["version"].setText(f"Version: {img_file.version.name if hasattr(img_file.version, 'name') else img_file.version}")
            self.info_labels["platform"].setText(f"Platform: {img_file.platform.value if hasattr(img_file.platform, 'value') else img_file.platform}")
            self.info_labels["entry_count"].setText(f"Entry Count: {len(img_file.entries)}")
            
            # File size
            if img_file.file_path and os.path.exists(img_file.file_path):
                file_size = os.path.getsize(img_file.file_path)
                try:
                    from methods.img_utils import format_file_size
                    file_size_str = format_file_size(file_size)
                except ImportError:
                    file_size_str = f"{file_size} B"
                self.info_labels["file_size"].setText(f"File Size: {file_size_str}")
            else:
                self.info_labels["file_size"].setText("File Size: -")
            
            # Total data size
            total_size = sum(getattr(entry, 'size', 0) for entry in img_file.entries)
            try:
                from methods.img_utils import format_file_size
                total_size_str = format_file_size(total_size)
            except ImportError:
                total_size_str = f"{total_size} B"
            self.info_labels["total_data_size"].setText(f"Total Data Size: {total_size_str}")
            
            # Status
            if img_file.modified:
                status = "Open (Modified)"
            elif img_file.is_open:
                status = "Open"
            else:
                status = "Closed"
            self.info_labels["status"].setText(f"Status: {status}")
            
        except Exception as e:
            img_debugger.error(f"Failed to update info panel: {e}")
            self.clear_info()
    
    def clear_info(self): #vers 1
        """Clear info panel"""
        for label in self.info_labels.values():
            text = label.text()
            if ": " in text:
                prefix = text.split(": ")[0]
                label.setText(f"{prefix}: -")


class TabFilterWidget(QWidget): #vers 1
    """Widget for tab-specific filtering"""
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self): #vers 1
        """Setup tab filter UI"""
        layout = QHBoxLayout(self)
        
        # Quick filter buttons
        filter_types = ["All", "DFF", "TXD", "COL", "Audio"]
        
        for filter_name in filter_types:
            btn = QPushButton(filter_name)
            btn.setCheckable(True)
            if filter_name == "All":
                btn.setChecked(True)
            layout.addWidget(btn)


# Integration functions (UI-specific)

def create_entries_table_panel(parent=None) -> IMGEntriesTable: #vers 1
    """Create entries table panel"""
    return IMGEntriesTable(parent)

def integrate_filtering(main_window): #vers 1
    """Integrate filtering functionality"""
    try:
        # Add filter panel to main window
        if hasattr(main_window, 'gui_layout'):
            filter_panel = FilterPanel()
            main_window.filter_panel = filter_panel
            
            # Connect filter signals
            filter_panel.filter_changed.connect(
                lambda filter_type, filter_value: main_window.apply_entry_filter(filter_type, filter_value)
            )
        
        main_window.log_message("✅ Entry filtering integrated")
        return True
    except Exception as e:
        main_window.log_message(f"❌ Filter integration failed: {e}")
        return False

# Helper functions that use shared methods

def format_file_size(size_bytes: int) -> str: #vers 1
    """Format file size - wrapper for shared method"""
    try:
        from methods.img_utils import format_file_size as shared_format_file_size
        return shared_format_file_size(size_bytes)
    except ImportError:
        # Fallback implementation
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size_bytes)} {size_names[i]}"
        else:
            return f"{size_bytes:.1f} {size_names[i]}"

def populate_table_with_sample_data(table: IMGEntriesTable): #vers 1
    """Populate table with sample data"""
    try:
        # Create sample IMG file
        sample_img = IMGFile()
        sample_img.entries = []
        
        # Add sample entries
        sample_entries = [
            ("player.dff", 50000, "Model"),
            ("player.txd", 25000, "Texture"),
            ("weapon.dff", 30000, "Model"),
            ("collision.col", 15000, "Collision")
        ]
        
        for name, size, file_type in sample_entries:
            entry = IMGEntry()
            entry.name = name
            entry.size = size
            entry.file_type = file_type
            entry.extension = name.split('.')[-1] if '.' in name else ''
            sample_img.entries.append(entry)
        
        table.set_img_file(sample_img)
        
    except Exception as e:
        img_debugger.error(f"Failed to populate sample data: {e}")


# Export all classes and functions
__all__ = [
    # Enums
    'IMGVersion', 'IMGPlatform', 'CompressionType', 'FileType', 'Platform',
    # Core classes
    'IMGEntry', 'IMGFile', 'RecentFilesManager',
    # GUI classes
    'IMGEntriesTable', 'FilterPanel', 'IMGFileInfoPanel', 'TabFilterWidget',
    # Functions
    'create_entries_table_panel', 'integrate_filtering', 'populate_table_with_sample_data',
    'format_file_size'
]