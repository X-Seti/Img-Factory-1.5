#!/usr/bin/env python3
"""
IMG Factory Main Application
Clean Qt6-based implementation of IMG Factory with modular architecture
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon

# Import our modular components
from img_manager import IMGFile, IMGVersion, IMGEntry, format_file_size, detect_img_version
from img_creator import NewIMGDialog, add_new_img_functionality
from img_templates import IMGTemplateManager, TemplateManagerDialog


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path: str):
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


class ExportThread(QThread):
    """Background thread for exporting files"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished_signal = pyqtSignal(int, int)  # exported_count, error_count
    error_signal = pyqtSignal(str)
    
    def __init__(self, img_file: IMGFile, entries: List[IMGEntry], export_dir: str):
        super().__init__()
        self.img_file = img_file
        self.entries = entries
        self.export_dir = export_dir
        self.should_stop = False
    
    def stop(self):
        self.should_stop = True
    
    def run(self):
        exported_count = 0
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
                    
                    exported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Export error for {entry.name}: {e}")
            
            self.progress_updated.emit(total_files, total_files, "")
            self.finished_signal.emit(exported_count, error_count)
            
        except Exception as e:
            self.error_signal.emit(f"Export failed: {str(e)}")


class ImportThread(QThread):
    """Background thread for importing files"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished_signal = pyqtSignal(int, int)  # imported_count, error_count
    error_signal = pyqtSignal(str)
    
    def __init__(self, img_file: IMGFile, file_paths: List[str]):
        super().__init__()
        self.img_file = img_file
        self.file_paths = file_paths
        self.should_stop = False
    
    def stop(self):
        self.should_stop = True
    
    def run(self):
        imported_count = 0
        error_count = 0
        total_files = len(self.file_paths)
        
        try:
            for i, file_path in enumerate(self.file_paths):
                if self.should_stop:
                    break
                
                try:
                    filename = os.path.basename(file_path)
                    self.progress_updated.emit(i, total_files, filename)
                    
                    # Read file data
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    
                    # Add to IMG
                    self.img_file.add_entry(filename, data)
                    imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Import error for {file_path}: {e}")
            
            self.progress_updated.emit(total_files, total_files, "")
            self.finished_signal.emit(imported_count, error_count)
            
        except Exception as e:
            self.error_signal.emit(f"Import failed: {str(e)}")


class IMGFactoryMain(QMainWindow):
    """Main IMG Factory application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMG Factory 2.0 - Python Edition")
        self.setGeometry(100, 100, 1200, 800)
        
        # Core data
        self.current_img: Optional[IMGFile] = None
        self.template_manager = IMGTemplateManager()
        
        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None
        self.export_thread: Optional[ExportThread] = None
        self.import_thread: Optional[ImportThread] = None
        
        self._create_ui()
        self._connect_signals()
        self._load_sample_data()
    
    def _create_ui(self):
        """Create the main user interface"""
        # Central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main splitter (left content | right controls)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - IMG content and log
        left_panel = self._create_left_panel()
        self.main_splitter.addWidget(left_panel)
        
        # Right panel - Controls
        right_panel = self._create_right_panel()
        self.main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (70% left, 30% right)
        self.main_splitter.setSizes([840, 360])
        
        main_layout.addWidget(self.main_splitter)
        
        # Create menu bar and status bar
        self._create_menu_bar()
        self._create_status_bar()
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with IMG info, table, and log"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # IMG file info
        info_group = QGroupBox("📁 IMG File Information")
        info_layout = QHBoxLayout(info_group)
        
        self.file_path_label = QLabel("No file loaded")
        self.file_path_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(QLabel("File:"))
        info_layout.addWidget(self.file_path_label)
        info_layout.addStretch()
        
        self.version_label = QLabel("Unknown")
        info_layout.addWidget(QLabel("Version:"))
        info_layout.addWidget(self.version_label)
        
        self.entry_count_label = QLabel("0")
        info_layout.addWidget(QLabel("Entries:"))
        info_layout.addWidget(self.entry_count_label)
        
        layout.addWidget(info_group)
        
        # Vertical splitter for table and log
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Entries table
        self.entries_table = QTableWidget(0, 7)
        self.entries_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Version", "Compression", "Status"
        ])
        self.entries_table.verticalHeader().setVisible(False)
        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        
        # Configure column widths
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Compression
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status
        
        content_splitter.addWidget(self.entries_table)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setPlaceholderText("Application log will appear here...")
        self.log_output.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
            }
        """)
        
        content_splitter.addWidget(self.log_output)
        
        # Set splitter proportions (80% table, 20% log)
        content_splitter.setSizes([400, 100])
        
        layout.addWidget(content_splitter)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with controls"""
        panel = QWidget()
        panel.setMinimumWidth(200)
        layout = QVBoxLayout(panel)
        
        # IMG Operations
        img_group = QGroupBox("🎮 IMG Operations")
        img_layout = QVBoxLayout(img_group)
        
        self.new_img_btn = QPushButton("🆕 New IMG")
        self.new_img_btn.clicked.connect(self.create_new_img)
        img_layout.addWidget(self.new_img_btn)
        
        self.open_img_btn = QPushButton("📂 Open IMG")
        self.open_img_btn.clicked.connect(self.open_img_file)
        img_layout.addWidget(self.open_img_btn)
        
        self.close_img_btn = QPushButton("❌ Close")
        self.close_img_btn.clicked.connect(self.close_img_file)
        self.close_img_btn.setEnabled(False)
        img_layout.addWidget(self.close_img_btn)
        
        img_layout.addWidget(QLabel("---"))
        
        self.rebuild_btn = QPushButton("🔄 Rebuild")
        self.rebuild_btn.clicked.connect(self.rebuild_img)
        self.rebuild_btn.setEnabled(False)
        img_layout.addWidget(self.rebuild_btn)
        
        self.rebuild_as_btn = QPushButton("💾 Rebuild As...")
        self.rebuild_as_btn.clicked.connect(self.rebuild_img_as)
        self.rebuild_as_btn.setEnabled(False)
        img_layout.addWidget(self.rebuild_as_btn)
        
        layout.addWidget(img_group)
        
        # Entry Operations
        entry_group = QGroupBox("📦 Entry Operations")
        entry_layout = QVBoxLayout(entry_group)
        
        self.import_btn = QPushButton("📥 Import Files")
        self.import_btn.clicked.connect(self.import_files)
        self.import_btn.setEnabled(False)
        entry_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export Selected")
        self.export_btn.clicked.connect(self.export_selected)
        self.export_btn.setEnabled(False)
        entry_layout.addWidget(self.export_btn)
        
        self.export_all_btn = QPushButton("📤 Export All")
        self.export_all_btn.clicked.connect(self.export_all)
        self.export_all_btn.setEnabled(False)
        entry_layout.addWidget(self.export_all_btn)
        
        entry_layout.addWidget(QLabel("---"))
        
        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.remove_btn.setEnabled(False)
        entry_layout.addWidget(self.remove_btn)
        
        layout.addWidget(entry_group)
        
        # Filter & Search
        filter_group = QGroupBox("🔍 Filter & Search")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Files", "Models (DFF)", "Textures (TXD)", 
            "Collision (COL)", "Animation (IFP)", "Audio (WAV)", "Scripts (SCM)"
        ])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.search_input)
        
        layout.addWidget(filter_group)
        
        # Templates
        template_group = QGroupBox("📋 Templates")
        template_layout = QVBoxLayout(template_group)
        
        self.manage_templates_btn = QPushButton("⚙️ Manage Templates")
        self.manage_templates_btn.clicked.connect(self.manage_templates)
        template_layout.addWidget(self.manage_templates_btn)
        
        layout.addWidget(template_group)
        
        layout.addStretch()
        
        return panel
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("🆕 New IMG...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_img)
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Open IMG...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        close_action = QAction("❌ Close IMG", self)
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # IMG Menu
        img_menu = menubar.addMenu("IMG")
        
        rebuild_action = QAction("🔄 Rebuild", self)
        rebuild_action.triggered.connect(self.rebuild_img)
        img_menu.addAction(rebuild_action)
        
        rebuild_as_action = QAction("💾 Rebuild As...", self)
        rebuild_as_action.triggered.connect(self.rebuild_img_as)
        img_menu.addAction(rebuild_as_action)
        
        img_menu.addSeparator()
        
        info_action = QAction("ℹ️ IMG Info", self)
        info_action.triggered.connect(self.show_img_info)
        img_menu.addAction(info_action)
        
        # Entry Menu
        entry_menu = menubar.addMenu("Entry")
        
        import_action = QAction("📥 Import Files...", self)
        import_action.triggered.connect(self.import_files)
        entry_menu.addAction(import_action)
        
        export_selected_action = QAction("📤 Export Selected...", self)
        export_selected_action.triggered.connect(self.export_selected)
        entry_menu.addAction(export_selected_action)
        
        export_all_action = QAction("📤 Export All...", self)
        export_all_action.triggered.connect(self.export_all)
        entry_menu.addAction(export_all_action)
        
        entry_menu.addSeparator()
        
        remove_action = QAction("🗑️ Remove Selected", self)
        remove_action.triggered.connect(self.remove_selected)
        entry_menu.addAction(remove_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        
        templates_action = QAction("📋 Manage Templates...", self)
        templates_action.triggered.connect(self.manage_templates)
        tools_menu.addAction(templates_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Main status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # IMG info label
        self.img_status_label = QLabel("No IMG loaded")
        self.status_bar.addPermanentWidget(self.img_status_label)
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.entries_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.entries_table.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _load_sample_data(self):
        """Load sample data to show interface"""
        sample_entries = [
            ("player.dff", "DFF", "245 KB", "0x2000", "RW 3.6", "None", "Ready"),
            ("player.txd", "TXD", "512 KB", "0x42000", "RW 3.6", "None", "Ready"),
            ("vehicle.col", "COL", "128 KB", "0x84000", "COL 2", "None", "Ready"),
            ("dance.ifp", "IFP", "1.2 MB", "0xA4000", "IFP 1", "ZLib", "Ready"),
        ]
        
        self.entries_table.setRowCount(len(sample_entries))
        for row, entry_data in enumerate(sample_entries):
            for col, value in enumerate(entry_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.entries_table.setItem(row, col, item)
        
        self.log_message("IMG Factory 2.0 Python Edition initialized")
        self.log_message("Sample data loaded. Open an IMG file to see real content.")
    
    def _on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = len(self.entries_table.selectionModel().selectedRows())
        has_selection = selected_rows > 0
        has_img = self.current_img is not None
        
        # Update button states
        self.export_btn.setEnabled(has_selection and has_img)
        self.remove_btn.setEnabled(has_selection and has_img)
        
        # Update status
        if selected_rows > 0:
            self.status_label.setText(f"{selected_rows} entries selected")
        else:
            self.status_label.setText("Ready")
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        row = item.row()
        name_item = self.entries_table.item(row, 0)
        if name_item:
            entry_name = name_item.text()
            self.log_message(f"Double-clicked entry: {entry_name}")
    
    def apply_filter(self):
        """Apply filter and search to entries table"""
        if not self.current_img:
            return
        
        filter_type = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        for row in range(self.entries_table.rowCount()):
            show_row = True
            
            # Apply type filter
            if filter_type != "All Files":
                type_item = self.entries_table.item(row, 1)
                if type_item:
                    file_type = type_item.text()
                    if filter_type == "Models (DFF)" and file_type != "DFF":
                        show_row = False
                    elif filter_type == "Textures (TXD)" and file_type != "TXD":
                        show_row = False
                    elif filter_type == "Collision (COL)" and file_type != "COL":
                        show_row = False
                    elif filter_type == "Animation (IFP)" and file_type != "IFP":
                        show_row = False
                    elif filter_type == "Audio (WAV)" and file_type != "WAV":
                        show_row = False
                    elif filter_type == "Scripts (SCM)" and file_type != "SCM":
                        show_row = False
            
            # Apply search filter
            if show_row and search_text:
                name_item = self.entries_table.item(row, 0)
                if name_item and search_text not in name_item.text().lower():
                    show_row = False
            
            self.entries_table.setRowHidden(row, not show_row)
    
    def log_message(self, message: str):
        """Add message to log output"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        self.log_output.ensureCursorVisible()
    
    def log_error(self, message: str):
        """Add error message to log output"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] ERROR: {message}")
        self.log_output.ensureCursorVisible()
    
    def show_progress(self, visible: bool = True):
        """Show or hide progress bar"""
        self.progress_bar.setVisible(visible)
        if not visible:
            self.progress_bar.setValue(0)
    
    def update_progress(self, value: int):
        """Update progress bar value"""
        self.progress_bar.setValue(value)
    
    # IMG File Operations
    def create_new_img(self):
        """Create new IMG file"""
        dialog = NewIMGDialog(self)
        dialog.template_manager = self.template_manager
        dialog.img_created.connect(self.load_img_file)
        dialog.img_created.connect(lambda path: self.log_message(f"Created IMG: {os.path.basename(path)}"))
        dialog.exec()
    
    def open_img_file(self):
        """Open IMG file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open IMG File",
            "",
            "IMG Files (*.img *.dir);;All Files (*)"
        )
        
        if file_path:
            self.load_img_file(file_path)
    
    def load_img_file(self, file_path: str):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.show_progress(True)
        self.status_label.setText("Loading IMG file...")
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress.connect(self.update_progress)
        self.load_thread.finished.connect(self._on_img_loaded)
        self.load_thread.error.connect(self._on_img_load_error)
        self.load_thread.start()
    
    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG file loading"""
        self.current_img = img_file
        self.show_progress(False)
        
        # Update UI
        self.file_path_label.setText(os.path.basename(img_file.file_path))
        self.version_label.setText(f"IMG {img_file.version.value}")
        self.entry_count_label.setText(str(len(img_file.entries)))
        self.img_status_label.setText(f"IMG {img_file.version.value} - {len(img_file.entries)} entries")
        
        # Enable/disable buttons
        self.close_img_btn.setEnabled(True)
        self.rebuild_btn.setEnabled(True)
        self.rebuild_as_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_all_btn.setEnabled(True)
        
        # Populate table
        self._populate_entries_table()
        
        self.status_label.setText("IMG file loaded successfully")
        self.log_message(f"Loaded: {img_file.file_path}")
        self.log_message(f"Version: {img_file.version.name}, Entries: {len(img_file.entries)}")
    
    def _on_img_load_error(self, error_message: str):
        """Handle IMG file loading error"""
        self.show_progress(False)
        self.status_label.setText("Error loading IMG file")
        self.log_error(error_message)
        
        QMessageBox.critical(self, "Error", f"Failed to load IMG file:\n{error_message}")
    
    def _populate_entries_table(self):
        """Populate entries table with real IMG data"""
        if not self.current_img:
            return
        
        entries = self.current_img.entries
        self.entries_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.entries_table.setItem(row, 0, QTableWidgetItem(entry.name))
            
            # Type
            type_text = entry.extension if entry.extension else "Unknown"
            self.entries_table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # Size
            size_text = format_file_size(entry.size)
            self.entries_table.setItem(row, 2, QTableWidgetItem(size_text))
            
            # Offset
            offset_text = f"0x{entry.offset:X}"
            self.entries_table.setItem(row, 3, QTableWidgetItem(offset_text))
            
            # Version
            version_text = entry.get_version_text()
            self.entries_table.setItem(row, 4, QTableWidgetItem(version_text))
            
            # Compression
            comp_text = "Compressed" if entry.is_compressed else "None"
            self.entries_table.setItem(row, 5, QTableWidgetItem(comp_text))
            
            # Status
            if entry.is_new_entry:
                status_text = "New"
            elif entry.is_replaced:
                status_text = "Modified"
            else:
                status_text = "Ready"
            self.entries_table.setItem(row, 6, QTableWidgetItem(status_text))
            
            # Make all items read-only
            for col in range(7):
                item = self.entries_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        # Reset filters
        self.filter_combo.setCurrentIndex(0)
        self.search_input.clear()
    
    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
            
            # Update UI
            self._load_sample_data()
            self.file_path_label.setText("No file loaded")
            self.version_label.setText("Unknown")
            self.entry_count_label.setText("0")
            self.img_status_label.setText("No IMG loaded")
            
            # Disable buttons
            self.close_img_btn.setEnabled(False)
            self.rebuild_btn.setEnabled(False)
            self.rebuild_as_btn.setEnabled(False)
            self.import_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.export_all_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            
            self.log_message("IMG file closed")
    
    def rebuild_img(self):
        """Rebuild current IMG file"""
        if not self.current_img:
            return
        
        try:
            self.status_label.setText("Rebuilding IMG file...")
            if self.current_img.rebuild():
                self.log_message("IMG file rebuilt successfully")
                QMessageBox.information(self, "Success", "IMG file rebuilt successfully!")
            else:
                self.log_error("Failed to rebuild IMG file")
                QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
        except Exception as e:
            self.log_error(f"Rebuild error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Rebuild failed:\n{str(e)}")
        finally:
            self.status_label.setText("Ready")
    
    def rebuild_img_as(self):
        """Rebuild IMG file to new location"""
        if not self.current_img:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Rebuilt IMG As", "", "IMG Files (*.img);;All Files (*)"
        )
        
        if output_path:
            try:
                self.status_label.setText("Rebuilding IMG file...")
                if self.current_img.rebuild(output_path):
                    self.log_message(f"IMG rebuilt as: {output_path}")
                    QMessageBox.information(self, "Success", f"IMG file rebuilt as:\n{output_path}")
                else:
                    self.log_error("Failed to rebuild IMG file")
                    QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
            except Exception as e:
                self.log_error(f"Rebuild error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Rebuild failed:\n{str(e)}")
            finally:
                self.status_label.setText("Ready")
    
    # Entry Operations
    def import_files(self):
        """Import files into IMG"""
        if not self.current_img:
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            "",
            "All Supported Files (*.dff *.txd *.col *.ifp *.wav *.scm *.ipl *.ide *.dat);;All Files (*)"
        )
        
        if file_paths:
            self.show_progress(True)
            self.status_label.setText("Importing files...")
            
            self.import_thread = ImportThread(self.current_img, file_paths)
            self.import_thread.progress_updated.connect(self._update_import_progress)
            self.import_thread.finished_signal.connect(self._on_import_finished)
            self.import_thread.error_signal.connect(self._on_import_error)
            self.import_thread.start()
    
    def _update_import_progress(self, current: int, total: int, filename: str):
        """Update import progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.update_progress(progress)
            self.status_label.setText(f"Importing {current}/{total}: {filename}")
    
    def _on_import_finished(self, imported_count: int, error_count: int):
        """Handle import completion"""
        self.show_progress(False)
        self.status_label.setText("Ready")
        
        # Refresh table
        self._populate_entries_table()
        self.entry_count_label.setText(str(len(self.current_img.entries)))
        
        if error_count == 0:
            message = f"Successfully imported {imported_count} files!"
            QMessageBox.information(self, "Import Complete", message)
            self.log_message(f"Import completed: {imported_count} files")
        else:
            message = f"Import completed with {error_count} errors.\nSuccessfully imported: {imported_count} files"
            QMessageBox.warning(self, "Import Complete", message)
            self.log_message(f"Import completed: {imported_count} files, {error_count} errors")
    
    def _on_import_error(self, error_message: str):
        """Handle import error"""
        self.show_progress(False)
        self.status_label.setText("Ready")
        self.log_error(f"Import failed: {error_message}")
        QMessageBox.critical(self, "Import Error", f"Import failed:\n{error_message}")
    
    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            return
        
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Export", "No entries selected")
            return
        
        self._export_entries([row.row() for row in selected_rows])
    
    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            return
        
        entry_count = len(self.current_img.entries)
        self._export_entries(list(range(entry_count)))
    
    def _export_entries(self, row_indices: List[int]):
        """Export entries by row indices"""
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        # Get entries to export
        entries_to_export = []
        for row in row_indices:
            if row < len(self.current_img.entries):
                entries_to_export.append(self.current_img.entries[row])
        
        if not entries_to_export:
            return
        
        self.show_progress(True)
        self.status_label.setText("Exporting files...")
        
        self.export_thread = ExportThread(self.current_img, entries_to_export, export_dir)
        self.export_thread.progress_updated.connect(self._update_export_progress)
        self.export_thread.finished_signal.connect(self._on_export_finished)
        self.export_thread.error_signal.connect(self._on_export_error)
        self.export_thread.start()
    
    def _update_export_progress(self, current: int, total: int, filename: str):
        """Update export progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.update_progress(progress)
            self.status_label.setText(f"Exporting {current}/{total}: {filename}")
    
    def _on_export_finished(self, exported_count: int, error_count: int):
        """Handle export completion"""
        self.show_progress(False)
        self.status_label.setText("Ready")
        
        if error_count == 0:
            message = f"Successfully exported {exported_count} files!"
            QMessageBox.information(self, "Export Complete", message)
            self.log_message(f"Export completed: {exported_count} files")
        else:
            message = f"Export completed with {error_count} errors.\nSuccessfully exported: {exported_count} files"
            QMessageBox.warning(self, "Export Complete", message)
            self.log_message(f"Export completed: {exported_count} files, {error_count} errors")
    
    def _on_export_error(self, error_message: str):
        """Handle export error"""
        self.show_progress(False)
        self.status_label.setText("Ready")
        self.log_error(f"Export failed: {error_message}")
        QMessageBox.critical(self, "Export Error", f"Export failed:\n{error_message}")
    
    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            return
        
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Remove", "No entries selected")
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Remove {len(selected_rows)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            removed_count = 0
            # Sort rows in descending order to remove from end first
            rows = sorted([idx.row() for idx in selected_rows], reverse=True)
            
            for row in rows:
                if row < len(self.current_img.entries):
                    entry = self.current_img.entries[row]
                    if self.current_img.remove_entry(entry):
                        removed_count += 1
                        self.log_message(f"Removed: {entry.name}")
            
            # Refresh table
            self._populate_entries_table()
            self.entry_count_label.setText(str(len(self.current_img.entries)))
            
            QMessageBox.information(self, "Remove Complete", f"Successfully removed {removed_count} entries")
            
        except Exception as e:
            self.log_error(f"Remove failed: {str(e)}")
            QMessageBox.critical(self, "Remove Error", f"Remove failed:\n{str(e)}")
    
    # Tools
    def manage_templates(self):
        """Show template manager dialog"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.exec()
    
    def show_img_info(self):
        """Show detailed IMG file information"""
        if not self.current_img:
            QMessageBox.information(self, "IMG Info", "No IMG file loaded")
            return
        
        info_text = f"""IMG File Information:

File Path: {self.current_img.file_path}
Version: {self.current_img.version.name}
Platform: {self.current_img.platform.value}
Entry Count: {len(self.current_img.entries)}
Encrypted: {self.current_img.is_encrypted}

File Types:
"""
        
        # Count file types
        type_counts = {}
        for entry in self.current_img.entries:
            ext = entry.extension or "Unknown"
            type_counts[ext] = type_counts.get(ext, 0) + 1
        
        for file_type, count in sorted(type_counts.items()):
            info_text += f"  {file_type}: {count} files\n"
        
        QMessageBox.information(self, "IMG File Information", info_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>IMG Factory 2.0 - Python Edition</h2>
<p>A modern, cross-platform IMG archive manager for GTA and related games.</p>

<p><b>Features:</b></p>
<ul>
<li>Support for IMG versions 1, 2, 3, and Fastman92</li>
<li>Template system for quick IMG creation</li>
<li>Import/Export functionality</li>
<li>Background processing</li>
<li>Cross-platform compatibility</li>
</ul>

<p><b>Supported Games:</b></p>
<ul>
<li>Grand Theft Auto III</li>
<li>Grand Theft Auto Vice City</li>
<li>Grand Theft Auto San Andreas</li>
<li>Grand Theft Auto IV</li>
<li>Bully</li>
</ul>

<p>Based on the original IMG Factory by MexUK<br>
Python edition by X-Seti</p>
        """
        
        QMessageBox.about(self, "About IMG Factory", about_text)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("IMG Factory")
    
    # Apply modern style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = IMGFactoryMain()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
