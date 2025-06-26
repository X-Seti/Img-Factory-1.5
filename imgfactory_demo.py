#this belongs in root /Imgfactory_Demo.py

# $vers" X-Seti - June26,2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

import sys
import os
import mimetypes
print("Starting application...")
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QProgressBar, QLabel, QPushButton, QFileDialog,
    QMessageBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenuBar, QMenu, QStatusBar, QSizePolicy
)

print("Tkinter imported successfully")
import tkinter as tk

print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
print("PyQt6.QtGui imported successfully")
from PyQt6.QtGui import QAction, QIcon, QFont, QDragEnterEvent, QDropEvent
print("App Settings System imported successfully")
from app_settings_system import AppSettings, apply_theme_to_app
print("Img Core Classes imported successfully")
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
print("Img Creator imported successfully")
from components.img_creator import NewIMGDialog, GameType, add_new_img_functionality
print("Img Formats imported successfully")
from components.img_formats import GameSpecificIMGDialog, EnhancedIMGCreator
print("Img Template Manager imported successfully")
from components.img_templates import TemplateManagerDialog, IMGTemplateManager
from components.img_manager import IMGFile, IMGVersion, Platform
print("Quick Start Wizard imported successfully")
#from components.img_quick_start_wizard import QuickStartWizard

class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit(10)
            img_file = IMGFile(self.file_path)
            
            self.progress.emit(30)
            if not img_file.open():
                self.error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress.emit(100)
            self.finished.emit(img_file)
            
        except Exception as e:
            self.error.emit(f"Error loading IMG file: {str(e)}")

class ExportProgressDialog(QDialog):
    """Progress dialog for export operations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exporting Files...")
        self.setMinimumSize(400, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Progress info
        self.status_label = QLabel("Preparing export...")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        layout.addWidget(self.cancel_btn)

class ExportThread(QThread):
    """Background thread for exporting files"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    export_finished = pyqtSignal(int, int)        # success_count, error_count
    export_error = pyqtSignal(str)                # error message
    
    def __init__(self, img_file: IMGFile, entries: list, export_dir: str):
        super().__init__()
        self.img_file = img_file
        self.entries = entries
        self.export_dir = export_dir
        self.should_stop = False
    
    def stop_export(self):
        self.should_stop = True
    
    def run(self):
        success_count = 0
        error_count = 0
        total_files = len(self.entries)
        
        try:
            for i, entry in enumerate(self.entries):
                if self.should_stop:
                    break
                
                try:
                    self.progress_updated.emit(i, total_files, entry.name)
                    
                    # Get entry data
                    data = entry.get_data()
                    
                    # Write to file
                    output_path = os.path.join(self.export_dir, entry.name)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Export error for {entry.name}: {e}")
            
            self.progress_updated.emit(total_files, total_files, "Complete")
            self.export_finished.emit(success_count, error_count)
            
        except Exception as e:
            self.export_error.emit(f"Export failed: {str(e)}")

class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [Demo]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings
        
        # Current IMG file
        self.current_img: IMGFile = None
        self.load_thread: IMGLoadThread = None
        self.export_thread: ExportThread = None

        self._create_menu()
        self._create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout will contain the main horizontal splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self._create_main_ui_with_splitters(main_layout)
        
        # Apply theme
        self._apply_table_theme()
        
        # Add new IMG functionality
        self._add_new_img_support()

    def _create_menu(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # New IMG submenu
        new_menu = file_menu.addMenu("New IMG")
        
        new_gta3_action = QAction("GTA III IMG", self)
        new_gta3_action.triggered.connect(lambda: self.quick_create_img(GameType.GTA_III))
        new_menu.addAction(new_gta3_action)
        
        new_gtavc_action = QAction("GTA Vice City IMG", self)
        new_gtavc_action.triggered.connect(lambda: self.quick_create_img(GameType.GTA_VC))
        new_menu.addAction(new_gtavc_action)
        
        new_gtasa_action = QAction("GTA San Andreas IMG", self)
        new_gtasa_action.triggered.connect(lambda: self.quick_create_img(GameType.GTA_SA))
        new_menu.addAction(new_gtasa_action)
        
        new_bully_action = QAction("Bully IMG", self)
        new_bully_action.triggered.connect(lambda: self.quick_create_img(GameType.BULLY))
        new_menu.addAction(new_bully_action)
        
        file_menu.addSeparator()
        
        open_action = QAction("Open IMG", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        templates_action = QAction("Manage Templates", self)
        templates_action.triggered.connect(self.manage_templates)
        tools_menu.addAction(templates_action)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

    def _create_status_bar(self):
        """Create status bar with progress"""
        self.status_bar = self.statusBar()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _create_main_ui_with_splitters(self, main_layout):
        """Create main UI using QSplitter for flexible layout"""
        
        # Main horizontal splitter (left: content, right: controls)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Content area (IMG info + table + log)
        left_widget = self._create_left_content_area()
        main_splitter.addWidget(left_widget)
        
        # Right side: Control panels
        right_widget = self._create_right_control_panels()
        main_splitter.addWidget(right_widget)
        
        # Set proportional sizes (left 70%, right 30%)
        main_splitter.setSizes([770, 330])
        
        main_layout.addWidget(main_splitter)

    def _create_left_content_area(self):
        """Create left content area with IMG info, table, and log"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # IMG file info panel
        info_group = QGroupBox("IMG File Information")
        info_layout = QHBoxLayout(info_group)
        
        self.file_path_label = QLabel("No file loaded")
        self.version_label = QLabel("Unknown")
        self.entry_count_label = QLabel("0 entries")
        self.img_info_label = QLabel("No IMG loaded - Open an IMG file to see real content.")
        
        info_layout.addWidget(QLabel("File:"))
        info_layout.addWidget(self.file_path_label)
        info_layout.addStretch()
        info_layout.addWidget(self.version_label)
        info_layout.addWidget(self.entry_count_label)
        
        left_layout.addWidget(info_group)
        
        # Vertical splitter for table and log
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Main table area
        table_widget = self._create_table_area()
        content_splitter.addWidget(table_widget)
        
        # Log area
        log_widget = self._create_log_area()
        content_splitter.addWidget(log_widget)
        
        # Set vertical proportions (table 75%, log 25%)
        content_splitter.setSizes([450, 150])
        
        left_layout.addWidget(content_splitter)
        
        return left_widget

    def _create_table_area(self):
        """Create the main entries table"""
        table_group = QGroupBox("IMG Entries")
        table_layout = QVBoxLayout(table_group)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Name', 'Type', 'Size', 'Offset', 'Version', 'Compression', 'Status'
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Compression
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        table_layout.addWidget(self.table)
        
        # Add sample data initially
        self._add_sample_data()
        
        return table_group

    def _create_log_area(self):
        """Create log output area"""
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        
        self.log = QTextEdit()
        self.log.setMaximumHeight(120)
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 9))
        
        log_layout.addWidget(self.log)
        
        # Initial log message
        self.log_message("IMG Factory 1.5 ready - Open an IMG file to get started")
        
        return log_group

    def _create_right_control_panels(self):
        """Create right side control panels"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # IMG Operations panel
        img_ops_group = QGroupBox("IMG Operations")
        img_ops_layout = QGridLayout(img_ops_group)
        
        self.open_btn = QPushButton("Open IMG")
        self.open_btn.clicked.connect(self.open_img_file)
        img_ops_layout.addWidget(self.open_btn, 0, 0)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close_img_file)
        img_ops_layout.addWidget(self.close_btn, 0, 1)
        
        self.new_img_btn = QPushButton("New IMG")
        self.new_img_btn.clicked.connect(self.create_new_img)
        img_ops_layout.addWidget(self.new_img_btn, 1, 0)
        
        self.rebuild_btn = QPushButton("Rebuild")
        self.rebuild_btn.clicked.connect(self.rebuild_img)
        img_ops_layout.addWidget(self.rebuild_btn, 1, 1)
        
        right_layout.addWidget(img_ops_group)
        
        # Entry Operations panel
        entry_ops_group = QGroupBox("Entry Operations")
        entry_ops_layout = QGridLayout(entry_ops_group)
        
        self.import_btn = QPushButton("Import Files")
        self.import_btn.clicked.connect(self.import_files)
        entry_ops_layout.addWidget(self.import_btn, 0, 0)
        
        self.export_selected_btn = QPushButton("Export Selected")
        self.export_selected_btn.clicked.connect(self.export_selected_entries)
        entry_ops_layout.addWidget(self.export_selected_btn, 0, 1)
        
        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.clicked.connect(self.export_all_entries)
        entry_ops_layout.addWidget(self.export_all_btn, 1, 0)
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_entries)
        entry_ops_layout.addWidget(self.remove_btn, 1, 1)
        
        right_layout.addWidget(entry_ops_group)
        
        # Filter & Search panel
        filter_group = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout(filter_group)
        
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setPlaceholderText("Search entries...")
        filter_layout.addWidget(self.search_input)
        
        # Filter buttons
        filter_btn_layout = QHBoxLayout()
        
        self.filter_all_btn = QPushButton("All")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        filter_btn_layout.addWidget(self.filter_all_btn)
        
        self.filter_dff_btn = QPushButton("DFF")
        self.filter_dff_btn.setCheckable(True)
        filter_btn_layout.addWidget(self.filter_dff_btn)
        
        self.filter_txd_btn = QPushButton("TXD")
        self.filter_txd_btn.setCheckable(True)  
        filter_btn_layout.addWidget(self.filter_txd_btn)
        
        filter_layout.addLayout(filter_btn_layout)
        
        right_layout.addWidget(filter_group)
        
        # Spacer to push everything up
        right_layout.addStretch()
        
        return right_widget

    def _add_sample_data(self):
        """Add sample data to demonstrate table layout"""
        self.table.setRowCount(5)
        
        sample_data = [
            ("admiral.dff", "DFF", "1.2 MB", "0x1000", "RW 3.6.0.3", "None", "Ready"),
            ("admiral.txd", "TXD", "512 KB", "0x1500", "RW 3.6.0.3", "None", "Ready"),
            ("banshee.dff", "DFF", "980 KB", "0x2000", "RW 3.6.0.3", "None", "Ready"),
            ("banshee.txd", "TXD", "256 KB", "0x2400", "RW 3.6.0.3", "None", "Ready"),
            ("cheetah.dff", "DFF", "1.1 MB", "0x2800", "RW 3.6.0.3", "None", "Ready")
        ]
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

    def _apply_table_theme(self):
        """Apply theme-aware styling to the table with soft pastel highlights"""
        theme = self.app_settings.get_theme()
        colors = theme["colors"]
        
        # Determine if we're using a dark or light theme
        is_dark_theme = self._is_dark_theme(colors["bg_primary"])
        
        if is_dark_theme:
            # Dark theme colors - soft pastels on dark background
            table_bg = colors["bg_secondary"]
            table_text = colors["text_primary"]
            alternate_bg = self._lighten_color(colors["bg_tertiary"], 0.1)
            selection_bg = self._add_alpha(colors["accent_primary"], 0.3)
            header_bg = colors["panel_bg"]
            header_text = colors["text_accent"]
            grid_color = self._lighten_color(colors["border"], 0.2)
        else:
            # Light theme colors - soft pastels on light background
            table_bg = colors["bg_primary"]
            table_text = colors["text_primary"]
            alternate_bg = self._darken_color(colors["bg_secondary"], 0.05)
            selection_bg = self._add_alpha(colors["accent_primary"], 0.2)
            header_bg = colors["panel_bg"]
            header_text = colors["text_accent"]
            grid_color = colors["border"]
        
        table_style = f"""
            QTableWidget {{
                background-color: {table_bg};
                color: {table_text};
                gridline-color: {grid_color};
                selection-background-color: {selection_bg};
                alternate-background-color: {alternate_bg};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                font-weight: normal;
            }}
            
            QTableWidget::item {{
                padding: 4px 8px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {selection_bg};
                color: {colors["text_primary"]};
            }}
            
            QTableWidget::item:hover {{
                background-color: {self._add_alpha(colors["accent_secondary"], 0.1)};
            }}
            
            QHeaderView::section {{
                background-color: {header_bg};
                color: {header_text};
                padding: 6px 8px;
                border: 1px solid {colors["border"]};
                font-weight: bold;
            }}
        """
        
        self.table.setStyleSheet(table_style)

    def _is_dark_theme(self, bg_color):
        """Determine if theme is dark based on background color"""
        # Simple check - if background is darker than mid-gray, it's dark
        if bg_color.startswith("#"):
            hex_color = bg_color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            brightness = (r + g + b) / 3
            return brightness < 128
        return False

    def _lighten_color(self, hex_color, factor):
        """Lighten a hex color by a factor (0-1)"""
        if not hex_color.startswith("#"):
            return hex_color
        
        hex_color = hex_color[1:]
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16) 
        b = int(hex_color[4:6], 16)
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color, factor):
        """Darken a hex color by a factor (0-1)"""
        if not hex_color.startswith("#"):
            return hex_color
        
        hex_color = hex_color[1:]
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _add_alpha(self, hex_color, alpha):
        """Add alpha transparency to a hex color"""
        # For stylesheet purposes, just return the color
        # In real implementation, you'd convert to rgba
        return hex_color

    def log_message(self, message):
        """Add message to log output"""
        self.log.append(f"[INFO] {message}")
        self.log.ensureCursorVisible()

    def log_error(self, message):
        """Add error message to log output"""
        self.log.append(f"[ERROR] {message}")
        self.log.ensureCursorVisible()

    # IMG File Operations
    def open_img_file(self):
        """Open IMG file dialog and load selected file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open IMG File", 
            "", 
            "IMG Files (*.img *.dir);;All Files (*)"
        )
        
        if file_path:
            self.load_img_file(file_path)

    def load_img_file(self, file_path):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Loading IMG file...")
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress.connect(self.progress_bar.setValue)
        self.load_thread.finished.connect(self.on_img_loaded)
        self.load_thread.error.connect(self.on_img_load_error)
        self.load_thread.start()

    def on_img_loaded(self, img_file):
        """Handle successful IMG file loading"""
        self.current_img = img_file
        self.progress_bar.setVisible(False)
        
        # Update UI
        self.file_path_label.setText(os.path.basename(img_file.file_path))
        self.version_label.setText(f"IMG {img_file.version.value}")
        self.entry_count_label.setText(str(len(img_file.entries)))
        self.img_info_label.setText(f"IMG {img_file.version.value} - {len(img_file.entries)} entries")
        
        # Populate table with real data
        self.populate_table()
        
        self.status_label.setText("IMG file loaded successfully")
        self.log_message(f"Loaded IMG file: {img_file.file_path}")
        self.log_message(f"Version: {img_file.version.name}, Entries: {len(img_file.entries)}")

    def on_img_load_error(self, error_message):
        """Handle IMG file loading error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error loading IMG file")
        self.log_error(error_message)
        
        QMessageBox.critical(self, "Error", f"Failed to load IMG file:\n{error_message}")

    def populate_table(self):
        """Populate table with real IMG entries"""
        if not self.current_img:
            return
        
        entries = self.current_img.entries
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))
            
            # Type
            type_text = entry.extension if entry.extension else "Unknown"
            self.table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # Size
            size_text = format_file_size(entry.size)
            self.table.setItem(row, 2, QTableWidgetItem(size_text))
            
            # Offset
            offset_text = f"0x{entry.offset:X}"
            self.table.setItem(row, 3, QTableWidgetItem(offset_text))
            
            # Version
            version_text = entry.get_version_text()
            self.table.setItem(row, 4, QTableWidgetItem(version_text))
            
            # Compression
            comp_text = "Compressed" if entry.is_compressed() else "None"
            self.table.setItem(row, 5, QTableWidgetItem(comp_text))
            
            # Status
            status_text = "New" if entry.is_new_entry else ("Modified" if entry.is_replaced else "Ready")
            self.table.setItem(row, 6, QTableWidgetItem(status_text))
            
            # Make all items read-only
            for col in range(7):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
            
            # Clear UI and restore sample data
            self._add_sample_data()
            self.file_path_label.setText("No file loaded")
            self.version_label.setText("Unknown")
            self.entry_count_label.setText("0 entries")
            self.img_info_label.setText("No IMG loaded")
            
            self.log_message("IMG file closed")

    def export_selected_entries(self):
        """Export selected entries to files"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Export", "No entries selected")
            return
        
        if not self.current_img:
            QMessageBox.warning(self, "Export", "No IMG file loaded")
            return
        
        # Get directory to export to
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        # Get entries to export
        entries_to_export = []
        for model_index in selected_rows:
            row = model_index.row()
            if row < len(self.current_img.entries):
                entries_to_export.append(self.current_img.entries[row])
        
        if not entries_to_export:
            return
        
        # Start export in background thread
        self.progress_bar.setVisible(True)
        self.status_label.setText("Exporting files...")
        
        self.export_thread = ExportThread(self.current_img, entries_to_export, export_dir)
        self.export_thread.progress_updated.connect(self._update_export_progress)
        self.export_thread.export_finished.connect(self._on_export_finished)
        self.export_thread.export_error.connect(self._on_export_error)
        self.export_thread.start()
    
    def export_all_entries(self):
        """Export all entries to files"""
        if not self.current_img:
            QMessageBox.warning(self, "Export", "No IMG file loaded")
            return
        
        if not self.current_img.entries:
            QMessageBox.information(self, "Export", "No entries to export")
            return
        
        # Get directory to export to
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        # Start export in background thread
        self.progress_bar.setVisible(True)
        self.status_label.setText("Exporting all files...")
        
        self.export_thread = ExportThread(self.current_img, self.current_img.entries, export_dir)
        self.export_thread.progress_updated.connect(self._update_export_progress)
        self.export_thread.export_finished.connect(self._on_export_finished)
        self.export_thread.export_error.connect(self._on_export_error)
        self.export_thread.start()
    
    def _update_export_progress(self, current, total, filename):
        """Update export progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Exporting {current}/{total}: {filename}")
    
    def _on_export_finished(self, success_count, error_count):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
        if error_count == 0:
            message = f"Successfully exported {success_count} files!"
            QMessageBox.information(self, "Export Complete", message)
            self.log_message(f"Export completed: {success_count} files")
        else:
            message = f"Export completed with {error_count} errors.\nSuccessfully exported: {success_count} files"
            QMessageBox.warning(self, "Export Complete", message)
            self.log_message(f"Export completed: {success_count} files, {error_count} errors")
    
    def _on_export_error(self, error_message):
        """Handle export error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        self.log_error(f"Export failed: {error_message}")
        QMessageBox.critical(self, "Export Error", f"Export failed:\n{error_message}")

    def import_files(self):
        """Import files into current IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Import", "No IMG file loaded")
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            "",
            "All Supported (*.dff *.txd *.col *.ifp *.wav *.scm);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col);;IFP Animations (*.ifp);;All Files (*)"
        )
        
        if not file_paths:
            return
        
        try:
            imported_count = 0
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                
                # Read file data
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Add to IMG
                self.current_img.add_entry(filename, data)
                imported_count += 1
                self.log_message(f"Imported: {filename}")
            
            # Refresh table
            self.populate_table()
            self.entry_count_label.setText(str(len(self.current_img.entries)))
            
            QMessageBox.information(self, "Import Complete", 
                                  f"Successfully imported {imported_count} files")
            
        except Exception as e:
            self.log_error(f"Import failed: {str(e)}")
            QMessageBox.critical(self, "Import Error", f"Import failed:\n{str(e)}")

    def remove_entries(self):
        """Remove selected entries from IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Remove", "No IMG file loaded")
            return
        
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Remove", "No entries selected")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal",
                                   f"Remove {len(selected_rows)} selected entries?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            removed_count = 0
            # Sort rows in descending order to remove from end first
            rows = sorted([idx.row() for idx in selected_rows], reverse=True)
            
            for row in rows:
                if row < len(self.current_img.entries):
                    entry = self.current_img.entries[row]
                    self.current_img.remove_entry(entry)
                    removed_count += 1
                    self.log_message(f"Removed: {entry.name}")
            
            # Refresh table
            self.populate_table()
            self.entry_count_label.setText(str(len(self.current_img.entries)))
            
            QMessageBox.information(self, "Remove Complete", 
                                  f"Successfully removed {removed_count} entries")
                                  
        except Exception as e:
            self.log_error(f"Remove failed: {str(e)}")
            QMessageBox.critical(self, "Remove Error", f"Remove failed:\n{str(e)}")

    def rebuild_img(self):
        """Rebuild IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "Rebuild", "No IMG file loaded")
            return
        
        # Get output file path
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Rebuilt IMG", "", "IMG Files (*.img);;All Files (*)"
        )
        
        if not output_path:
            return
        
        try:
            self.log_message("Starting IMG rebuild...")
            self.current_img.rebuild(output_path)
            self.log_message(f"IMG rebuilt successfully: {output_path}")
            
            QMessageBox.information(self, "Rebuild Complete", 
                                  f"IMG file rebuilt successfully:\n{output_path}")
            
        except Exception as e:
            self.log_error(f"Rebuild failed: {str(e)}")
            QMessageBox.critical(self, "Rebuild Error", f"Rebuild failed:\n{str(e)}")

    # New IMG Creation Methods
    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(self)
        dialog.img_created.connect(self.load_img_file)
        dialog.img_created.connect(lambda path: self.log_message(f"Created: {os.path.basename(path)}"))
        dialog.exec()
    
    def quick_create_img(self, game_type):
        """Quick create IMG for specific game type"""
        dialog = NewIMGDialog(self)
        
        # Pre-select game type if available
        if hasattr(dialog, 'game_type_combo'):
            for i in range(dialog.game_type_combo.count()):
                if dialog.game_type_combo.itemData(i) == game_type:
                    dialog.game_type_combo.setCurrentIndex(i)
                    break
        
        dialog.img_created.connect(self.load_img_file)
        dialog.img_created.connect(lambda path: self.log_message(f"Created {game_type.name} IMG: {os.path.basename(path)}"))
        dialog.exec()
    
    def manage_templates(self):
        """Show template manager dialog"""
        try:
            template_manager = IMGTemplateManager()
            dialog = TemplateManagerDialog(template_manager, self)
            dialog.exec()
        except Exception as e:
            self.log_error(f"Template manager error: {str(e)}")
            QMessageBox.critical(self, "Template Manager Error", f"Failed to open template manager:\n{str(e)}")
    
    def show_settings(self):
        """Show application settings dialog"""
        try:
            from App_settings_system import SettingsDialog
            dialog = SettingsDialog(self.app_settings, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Apply new settings
                apply_theme_to_app(QApplication.instance(), self.app_settings)
                self._apply_table_theme()
                self.log_message("Settings updated")
        except Exception as e:
            self.log_error(f"Settings error: {str(e)}")
            QMessageBox.critical(self, "Settings Error", f"Failed to open settings:\n{str(e)}")

    def _add_new_img_support(self):
        """Add new IMG creation support"""
        # This method enables the new IMG functionality
        self.log_message("New IMG creation functionality enabled")

def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("IMG Factory")
        app.setApplicationVersion("1.5")
        app.setOrganizationName("X-Seti")
        
        # Initialize settings
        settings = AppSettings()
        
        # Apply base theme
        apply_theme_to_app(app, settings)
        
        # Create main window
        window = ImgFactoryDemo(settings)
        
        # Show window
        window.show()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path) and file_path.lower().endswith(('.img', '.dir')):
                window.load_img_file(file_path)
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
