#this belongs in gui/ table_view.py - version 7
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory Table View - IMG Entries Table and File Information
Handles the main entries table and IMG file information display
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QHeaderView, QAbstractItemView, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


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
        columns = ["ID", "Type", "Name", "Offset", "Size", "Version", "Compression", "Status"]
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Version
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Compression
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Status
        
        # Set specific column widths
        self.setColumnWidth(0, 60)   # ID
        self.setColumnWidth(1, 80)   # Type
        self.setColumnWidth(3, 100)  # Offset
        self.setColumnWidth(4, 100)  # Size
        self.setColumnWidth(5, 100)  # Version
        self.setColumnWidth(6, 100)  # Compression
        self.setColumnWidth(7, 80)   # Status
        
        # Table styling
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f5f5f5;
                selection-background-color: #3daee9;
                selection-color: white;
            }
            
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #3daee9;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #c0c0c0;
                font-weight: bold;
            }
        """)
    
    def _connect_signals(self):
        """Connect table signals"""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _on_selection_changed(self):
        """Handle selection changes"""
        selected_rows = []
        for item in self.selectedItems():
            if item.column() == 0:  # Only process first column to avoid duplicates
                selected_rows.append(item.row())
        
        self.entries_selected.emit(selected_rows)
    
    def _on_item_double_clicked(self, item):
        """Handle double-click events"""
        self.entry_double_clicked.emit(item.row())
    
    def populate_entries(self, entries):
        """Populate table with IMG entries"""
        self.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # ID
            id_item = QTableWidgetItem(str(row + 1))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, id_item)
            
            # Type (file extension)
            type_item = QTableWidgetItem(entry.extension or "Unknown")
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, type_item)
            
            # Name
            name_item = QTableWidgetItem(entry.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, name_item)
            
            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:X}")
            offset_item.setFlags(offset_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 3, offset_item)
            
            # Size
            size_text = self._format_file_size(entry.size)
            size_item = QTableWidgetItem(size_text)
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 4, size_item)
            
            # Version
            version_item = QTableWidgetItem(entry.get_version_text())
            version_item.setFlags(version_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 5, version_item)
            
            # Compression
            compression_text = entry.compression.name if hasattr(entry, 'compression') else "None"
            compression_item = QTableWidgetItem(compression_text)
            compression_item.setFlags(compression_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 6, compression_item)
            
            # Status
            status_text = "Modified" if getattr(entry, 'is_modified', False) else "Ready"
            status_item = QTableWidgetItem(status_text)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 7, status_item)
    
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
    
    def get_selected_entries(self):
        """Get indices of selected entries"""
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
                name_item = self.item(row, 2)  # Name column
                if name_item:
                    if filter_text.lower() not in name_item.text().lower():
                        show_row = False
            
            self.setRowHidden(row, not show_row)


class IMGFileInfoPanel(QWidget):
    """Panel showing IMG file information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
        self._reset_info()
    
    def _create_ui(self):
        """Create the file info UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # File path
        layout.addWidget(QLabel("File:"))
        self.file_path_label = QLabel("No file loaded")
        self.file_path_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        layout.addWidget(self.file_path_label)
        
        layout.addStretch()
        
        # Version
        layout.addWidget(QLabel("Version:"))
        self.version_label = QLabel("Unknown")
        layout.addWidget(self.version_label)
        
        # Entry count
        layout.addWidget(QLabel("Entries:"))
        self.entry_count_label = QLabel("0")
        layout.addWidget(self.entry_count_label)
        
        # File size
        layout.addWidget(QLabel("Size:"))
        self.file_size_label = QLabel("0 B")
        layout.addWidget(self.file_size_label)
    
    def _reset_info(self):
        """Reset all info to default state"""
        self.file_path_label.setText("No file loaded")
        self.file_path_label.setStyleSheet("color: #666666;")
        self.version_label.setText("Unknown")
        self.entry_count_label.setText("0")
        self.file_size_label.setText("0 B")
    
    def update_info(self, img_file):
        """Update info panel with IMG file data"""
        if img_file:
            # File path
            import os
            filename = os.path.basename(img_file.file_path)
            self.file_path_label.setText(filename)
            self.file_path_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
            
            # Version
            self.version_label.setText(img_file.version.name if hasattr(img_file, 'version') else "Unknown")
            
            # Entry count
            entry_count = len(img_file.entries) if hasattr(img_file, 'entries') else 0
            self.entry_count_label.setText(str(entry_count))
            
            # File size
            try:
                file_size = os.path.getsize(img_file.file_path)
                self.file_size_label.setText(self._format_file_size(file_size))
            except:
                self.file_size_label.setText("Unknown")
        else:
            self._reset_info()
    
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
            self.is_modified = False
            
        def get_version_text(self):
            return self._version
    
    mock_entries = [MockEntry(data) for data in sample_entries]
    table.populate_entries(mock_entries)
