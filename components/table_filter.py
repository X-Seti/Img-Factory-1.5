#this belongs in components/table_view_filter_fix.py - Version: 1
# X-Seti - June28 2025 - Fixed Tab Filtering and RenderWare Version Detection

import struct
from PyQt6.QtWidgets import QTableWidget, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

class IMGEntriesTable(QTableWidget):
    """Enhanced table with proper tab filtering and version detection"""
    
    entries_selected = pyqtSignal(list)
    entry_double_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_entries = []
        self.current_tab_filter = "Both"
        self.current_search_filter = ""
        self._setup_table()
    
    def _setup_table(self):
        """Setup table configuration"""
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "#", "Filename", "Type", "Size", "Offset", "Version", "Status"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 40)   # ID
        self.setColumnWidth(1, 200)  # Filename
        self.setColumnWidth(2, 80)   # Type
        self.setColumnWidth(3, 100)  # Size
        self.setColumnWidth(4, 100)  # Offset
        self.setColumnWidth(5, 120)  # Version
        self.setColumnWidth(6, 80)   # Status
    
    def populate_entries(self, entries, img_file=None):
        """Populate table with entries and detect versions"""
        self.current_entries = entries
        self.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # ID
            self.setItem(row, 0, self._create_readonly_item(str(row + 1)))
            
            # Filename
            self.setItem(row, 1, self._create_readonly_item(entry.name))
            
            # Type (extension)
            file_type = entry.name.split('.')[-1].upper() if '.' in entry.name else "Unknown"
            self.setItem(row, 2, self._create_readonly_item(file_type))
            
            # Size
            size_text = self._format_file_size(entry.size)
            self.setItem(row, 3, self._create_readonly_item(size_text))
            
            # Offset
            self.setItem(row, 4, self._create_readonly_item(f"0x{entry.offset:X}"))
            
            # Version - Enhanced detection
            version = self._detect_version(entry, img_file)
            self.setItem(row, 5, self._create_readonly_item(version))
            
            # Status
            self.setItem(row, 6, self._create_readonly_item("Ready"))
        
        # Apply current filters
        self._apply_all_filters()
    
    def _detect_version(self, entry, img_file):
        """Detect proper RenderWare or file version"""
        if not img_file:
            return "Unknown"
        
        try:
            file_type = entry.name.split('.')[-1].upper() if '.' in entry.name else ""
            
            # Try to read file data for RenderWare files
            if file_type in ['DFF', 'TXD']:
                try:
                    data = img_file.read_entry_data(entry)
                    if len(data) >= 12:
                        # Read RenderWare header
                        chunk_type, chunk_size, rw_version = struct.unpack('<III', data[:12])
                        return self._format_rw_version(rw_version)
                except:
                    pass
            
            # Use IMG version as fallback with better detection
            if hasattr(img_file, 'version'):
                img_version = img_file.version.name if hasattr(img_file.version, 'name') else str(img_file.version)
                
                if img_version == 'IMG_1':
                    if file_type in ['DFF', 'TXD']:
                        return "RW 3.6.0.3"  # GTA III/VC common version
                    elif file_type == 'COL':
                        return "COL 2"
                    elif file_type == 'IFP':
                        return "IFP 1"
                    else:
                        return "GTA III/VC"
                elif img_version == 'IMG_2':
                    if file_type in ['DFF', 'TXD']:
                        return "RW 3.7.0.2"  # GTA SA common version
                    elif file_type == 'COL':
                        return "COL 3"
                    else:
                        return "GTA SA"
                elif img_version == 'IMG_3':
                    return "GTA IV"
                else:
                    return img_version
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    def _format_rw_version(self, version):
        """Format RenderWare version to readable string"""
        version_map = {
            0x30000: "3.0.0.0",  # Alpha/beta GTA III
            0x31000: "3.1.0.0",  # GTA III (PS2)
            0x31001: "3.1.0.1",  # GTA III (PC)
            0x33002: "3.3.0.2",  # GTA VC (PS2)
            0x33003: "3.4.0.3",  # GTA VC (PC, XBOX)

            0x34003: "3.4.0.4",  # GTA SOL (PC mod)
            0x34003: "3.4.0.5",  # GTA VC (Amdroid)
            0x35000: "3.5.0.0",  # unsued
            0x36003: "3.6.0.3",  # GTA SA (PS2, PC, Xbox)
            0x1803FFFF: "3.6.0.3", # Trilogy GTA
            0x1805FFFF: "3.7.0.2", # unused
        }
        
        if version in version_map:
            return f"RW {version_map[version]}"
        elif version >= 0x30000 and version <= 0x3FFFF:
            major = (version >> 16) & 0xFF
            minor = (version >> 8) & 0xFF
            build = version & 0xFF
            return f"RW {major}.{minor}.{build}"
        else:
            return f"RW 0x{version:X}"
    
    def set_tab_filter(self, tab_name):
        """Set current tab filter"""
        self.current_tab_filter = tab_name
        self._apply_all_filters()
    
    def set_search_filter(self, search_text):
        """Set search filter"""
        self.current_search_filter = search_text.lower()
        self._apply_all_filters()
    
    def _apply_all_filters(self):
        """Apply both tab and search filters"""
        for row in range(self.rowCount()):
            show_row = True
            
            # Apply tab filter
            if self.current_tab_filter != "Both":
                type_item = self.item(row, 2)
                if type_item:
                    file_type = type_item.text()
                    
                    if self.current_tab_filter == "DFF" and file_type != "DFF":
                        show_row = False
                    elif self.current_tab_filter == "COL" and file_type != "COL":
                        show_row = False
                    elif self.current_tab_filter == "TXD" and file_type != "TXD":
                        show_row = False
                    elif self.current_tab_filter == "Other" and file_type in ["DFF", "COL", "TXD"]:
                        show_row = False
            
            # Apply search filter
            if show_row and self.current_search_filter:
                filename_item = self.item(row, 1)
                if filename_item:
                    if self.current_search_filter not in filename_item.text().lower():
                        show_row = False
            
            self.setRowHidden(row, not show_row)
    
    def _create_readonly_item(self, text):
        """Create a read-only table item"""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt
        
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

class TabFilterWidget(QWidget):
    """Widget that handles tab filtering"""
    
    tab_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_tabs()
    
    def _setup_tabs(self):
        """Setup tab widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        
        # Add tabs
        tabs = ["DFF", "COL", "Both", "TXD", "Other"]
        for tab_name in tabs:
            tab = QWidget()
            self.tab_widget.addTab(tab, tab_name)
        
        # Set "Both" as default
        self.tab_widget.setCurrentIndex(2)
        
        # Connect signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.tab_widget)
    
    def _on_tab_changed(self, index):
        """Handle tab change"""
        tab_name = self.tab_widget.tabText(index)
        self.tab_changed.emit(tab_name)
    
    def set_current_tab(self, tab_name):
        """Set current tab by name"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                self.tab_widget.setCurrentIndex(i)
                break


def integrate_filtering(main_window):
    """Integrate filtering into main window"""
    
    # Replace existing table with enhanced version
    if hasattr(main_window, 'entries_table'):
        old_table = main_window.entries_table
        parent = old_table.parent()
        layout = parent.layout()
        
        # Remove old table
        layout.removeWidget(old_table)
        old_table.deleteLater()
        
        # Create new enhanced table
        main_window.entries_table = IMGEntriesTable()
        layout.addWidget(main_window.entries_table)
    
    # Connect tab filtering if tab widget exists
    if hasattr(main_window, 'tab_widget'):
        main_window.tab_widget.currentChanged.connect(
            lambda index: main_window.entries_table.set_tab_filter(
                main_window.tab_widget.tabText(index)
            )
        )
    
    # Connect search filtering
    if hasattr(main_window, 'search_input'):
        main_window.search_input.textChanged.connect(
            main_window.entries_table.set_search_filter
        )
    elif hasattr(main_window, 'filter_input'):
        main_window.filter_input.textChanged.connect(
            main_window.entries_table.set_search_filter
        )
