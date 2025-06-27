#!/usr/bin/env python3
"""
#this belongs in root /imgfactory.py
IMG Factory 2.0 - Main Application Entry Point - FIXED IMPORTS
Clean Qt6-based implementation for IMG archive management
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap

# Import components
try:
    from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
    from components.img_creator import NewIMGDialog
    from components.img_templates import IMGTemplateManager, TemplateManagerDialog
    print("Core components imported successfully")
    
    # Try to import App Settings System
    try:
        from App_settings_system import AppSettings, apply_theme_to_app
        print("App Settings System imported successfully")
    except ImportError:
        print("App Settings System not found - using defaults")
        AppSettings = None
        apply_theme_to_app = None
    
    # Try to import pastel theme
    try:
        from gui.pastel_button_theme import apply_pastel_theme_to_buttons
        print("Pastel Theme imported successfully")
    except ImportError:
        print("Pastel Theme not found - using default styling")
        apply_pastel_theme_to_buttons = None
    
    # Try to import COL GUI components
    try:
        from gui.col_gui_components import setup_col_gui
        print("COL GUI components imported successfully")
    except ImportError:
        print("COL GUI components not found - COL buttons disabled")
        setup_col_gui = None
    
    # Try to import validator
    try:
        from components.img_validator import IMGValidator
        print("IMG Validator imported successfully")
    except ImportError:
        print("IMG Validator not found - validation disabled")
        IMGValidator = None
        
except ImportError as e:
    print(f"Failed to import core components: {e}")
    print("Make sure all component files are in the components/ directory")
    sys.exit(1)


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_updated = pyqtSignal(int, str)  # progress, status
    loading_finished = pyqtSignal(object)    # IMGFile object
    loading_error = pyqtSignal(str)          # error message
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress_updated.emit(10, "Opening file...")
            
            # Create IMG file instance
            img_file = IMGFile(self.file_path)
            
            self.progress_updated.emit(30, "Detecting format...")
            
            # Open and parse file
            if not img_file.open():
                self.loading_error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress_updated.emit(80, "Loading entries...")
            
            # Validate the loaded file if validator available
            if IMGValidator:
                validation = IMGValidator.validate_img_file(img_file)
                if not validation.is_valid:
                    self.loading_error.emit(f"IMG file validation failed: {validation.get_summary()}")
                    return
            
            self.progress_updated.emit(100, "Loading complete")
            self.loading_finished.emit(img_file)
            
        except Exception as e:
            self.loading_error.emit(f"Error loading IMG file: {str(e)}")


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
        try:
            exported_count = 0
            error_count = 0
            total = len(self.entries)
            
            for i, entry in enumerate(self.entries):
                if self.should_stop:
                    break
                
                try:
                    self.progress_updated.emit(i + 1, total, entry.name)
                    
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
        try:
            imported_count = 0
            error_count = 0
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                if self.should_stop:
                    break
                
                try:
                    filename = os.path.basename(file_path)
                    self.progress_updated.emit(i + 1, total_files, filename)
                    
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
        self.template_manager = IMGTemplateManager() if 'IMGTemplateManager' in globals() else None
        
        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None
        self.export_thread: Optional[ExportThread] = None
        self.import_thread: Optional[ImportThread] = None
        
        self._create_ui()
        self._connect_signals()
    
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
        """Create left panel with IMG content and log"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # IMG entries table
        entries_group = QGroupBox("📁 IMG Entries")
        entries_layout = QVBoxLayout(entries_group)
        
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(5)
        self.entries_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Compressed"
        ])
        
        # Configure table
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)
        
        entries_layout.addWidget(self.entries_table)
        layout.addWidget(entries_group)
        
        # Log area
        log_group = QGroupBox("📋 Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # IMG Operations
        img_group = QGroupBox("📁 IMG Operations")
        img_layout = QVBoxLayout(img_group)
        
        self.open_btn = QPushButton("📂 Open IMG")
        self.open_btn.clicked.connect(self.open_img)
        img_layout.addWidget(self.open_btn)
        
        self.new_btn = QPushButton("🆕 New IMG")
        self.new_btn.clicked.connect(self.new_img)
        img_layout.addWidget(self.new_btn)
        
        self.save_btn = QPushButton("💾 Save IMG")
        self.save_btn.clicked.connect(self.save_img)
        self.save_btn.setEnabled(False)
        img_layout.addWidget(self.save_btn)
        
        self.close_btn = QPushButton("❌ Close IMG")
        self.close_btn.clicked.connect(self.close_img)
        self.close_btn.setEnabled(False)
        img_layout.addWidget(self.close_btn)
        
        layout.addWidget(img_group)
        
        # Entry Operations
        entry_group = QGroupBox("📄 Entry Operations")
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
        
        # Templates (if available)
        if self.template_manager:
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
        
        open_action = QAction("Open IMG...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img)
        file_menu.addAction(open_action)
        
        new_action = QAction("New IMG...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_img)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save IMG", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_img)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        
        import_action = QAction("Import Files...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_files)
        edit_menu.addAction(import_action)
        
        export_action = QAction("Export Selected...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_selected)
        edit_menu.addAction(export_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.entries_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def log_message(self, message: str):
        """Add message to activity log"""
        self.log_text.append(f"[{QTimer().remainingTime()}] {message}")
        # Ensure log doesn't get too long
        if self.log_text.document().blockCount() > 1000:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
    
    def on_selection_changed(self):
        """Handle entry selection change"""
        has_selection = len(self.entries_table.selectedItems()) > 0
        has_img = self.current_img is not None
        
        self.export_btn.setEnabled(has_selection and has_img)
        self.remove_btn.setEnabled(has_selection and has_img)
    
    def open_img(self):
        """Open IMG file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG File", "", "IMG Files (*.img);;All Files (*)"
        )
        
        if file_path:
            self.load_img_file(file_path)
    
    def load_img_file(self, file_path: str):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.log_message(f"Loading IMG file: {os.path.basename(file_path)}")
        self.status_bar.showMessage("Loading IMG file...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        
        # Create and start loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self.on_load_progress)
        self.load_thread.loading_finished.connect(self.on_img_loaded)
        self.load_thread.loading_error.connect(self.on_load_error)
        self.load_thread.start()
    
    def on_load_progress(self, progress: int, status: str):
        """Handle loading progress"""
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(status)
    
    def on_img_loaded(self, img_file: IMGFile):
        """Handle IMG file loaded"""
        self.current_img = img_file
        self.populate_entries_table()
        
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Loaded: {os.path.basename(img_file.file_path)} - {len(img_file.entries)} entries")
        self.log_message(f"Successfully loaded {len(img_file.entries)} entries")
        
        # Enable controls
        self.save_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_all_btn.setEnabled(True)
    
    def on_load_error(self, error_msg: str):
        """Handle loading error"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Ready")
        
        QMessageBox.critical(self, "Loading Error", error_msg)
        self.log_message(f"Loading error: {error_msg}")
    
    def populate_entries_table(self):
        """Populate entries table with current IMG data"""
        if not self.current_img:
            self.entries_table.setRowCount(0)
            return
        
        entries = self.current_img.entries
        self.entries_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            name_item = QTableWidgetItem(entry.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 0, name_item)
            
            # Type (based on extension) 
            ext = entry.extension.upper() if entry.extension else "Unknown"
            type_item = QTableWidgetItem(ext)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 1, type_item)
            
            # Size
            size_item = QTableWidgetItem(format_file_size(entry.size))
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 2, size_item)
            
            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:08X}")
            offset_item.setFlags(offset_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 3, offset_item)
            
            # Compressed
            compressed_item = QTableWidgetItem("Yes" if entry.is_compressed() else "No")
            compressed_item.setFlags(compressed_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.entries_table.setItem(row, 4, compressed_item)
    
    def new_img(self):
        """Create new IMG file"""
        if 'NewIMGDialog' in globals():
            dialog = NewIMGDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.log_message("Created new IMG file")
        else:
            QMessageBox.information(self, "New IMG", "New IMG creation not available - missing component")
    
    def save_img(self):
        """Save current IMG file"""
        if not self.current_img:
            return
        
        try:
            if self.current_img.save():
                self.log_message("IMG file saved successfully")
                self.status_bar.showMessage("IMG file saved", 2000)
            else:
                QMessageBox.warning(self, "Save Error", "Failed to save IMG file")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving IMG file: {str(e)}")
    
    def close_img(self):
        """Close current IMG file"""
        self.current_img = None
        self.entries_table.setRowCount(0)
        
        # Disable controls
        self.save_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.export_all_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        
        self.status_bar.showMessage("Ready")
        self.log_message("IMG file closed")
    
    def import_files(self):
        """Import files into current IMG"""
        if not self.current_img:
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "Import Files", "", "All Files (*)"
        )
        
        if files:
            self.log_message(f"Importing {len(files)} files...")
            # Start import thread
            self.import_thread = ImportThread(self.current_img, files)
            self.import_thread.progress_updated.connect(self.on_import_progress)
            self.import_thread.finished_signal.connect(self.on_import_finished)
            self.import_thread.error_signal.connect(self.on_import_error)
            self.import_thread.start()
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(files))
    
    def on_import_progress(self, current: int, total: int, filename: str):
        """Handle import progress"""
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Importing {filename}...")
    
    def on_import_finished(self, imported_count: int, error_count: int):
        """Handle import finished"""
        self.progress_bar.setVisible(False)
        self.populate_entries_table()
        
        message = f"Import complete: {imported_count} files imported"
        if error_count > 0:
            message += f", {error_count} errors"
        
        self.status_bar.showMessage(message, 3000)
        self.log_message(message)
    
    def on_import_error(self, error_msg: str):
        """Handle import error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Import Error", error_msg)
        self.log_message(f"Import error: {error_msg}")
    
    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            return
        
        selected_rows = set()
        for item in self.entries_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select entries to export")
            return
        
        selected_entries = [self.current_img.entries[row] for row in selected_rows]
        self.export_entries(selected_entries)
    
    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            return
        
        self.export_entries(self.current_img.entries)
    
    def export_entries(self, entries: List[IMGEntry]):
        """Export list of entries"""
        export_dir = QFileDialog.getExistingDirectory(self, "Export Directory")
        if not export_dir:
            return
        
        self.log_message(f"Exporting {len(entries)} entries...")
        
        # Start export thread
        self.export_thread = ExportThread(self.current_img, entries, export_dir)
        self.export_thread.progress_updated.connect(self.on_export_progress)
        self.export_thread.finished_signal.connect(self.on_export_finished)
        self.export_thread.error_signal.connect(self.on_export_error)
        self.export_thread.start()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(entries))
    
    def on_export_progress(self, current: int, total: int, filename: str):
        """Handle export progress"""
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Exporting {filename}...")
    
    def on_export_finished(self, exported_count: int, error_count: int):
        """Handle export finished"""
        self.progress_bar.setVisible(False)
        
        message = f"Export complete: {exported_count} files exported"
        if error_count > 0:
            message += f", {error_count} errors"
        
        self.status_bar.showMessage(message, 3000)
        self.log_message(message)
    
    def on_export_error(self, error_msg: str):
        """Handle export error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Export Error", error_msg)
        self.log_message(f"Export error: {error_msg}")
    
    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            return
        
        selected_rows = set()
        for item in self.entries_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self, "Remove Entries",
            f"Remove {len(selected_rows)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove entries (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.current_img.entries):
                    removed_entry = self.current_img.entries.pop(row)
                    self.log_message(f"Removed entry: {removed_entry.name}")
            
            self.populate_entries_table()
            self.status_bar.showMessage(f"Removed {len(selected_rows)} entries", 2000)
    
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
                    elif filter_type == "Audio (WAV)" and file_type not in ["WAV", "MP3"]:
                        show_row = False
                    elif filter_type == "Scripts (SCM)" and file_type not in ["SCM", "CS"]:
                        show_row = False
            
            # Apply search filter
            if show_row and search_text:
                name_item = self.entries_table.item(row, 0)
                if name_item and search_text not in name_item.text().lower():
                    show_row = False
            
            self.entries_table.setRowHidden(row, not show_row)
    
    def manage_templates(self):
        """Show template manager dialog"""
        if self.template_manager and 'TemplateManagerDialog' in globals():
            dialog = TemplateManagerDialog(self.template_manager, self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Templates", "Template manager not available")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>IMG Factory 2.0</h2>
<p>Modern IMG archive manager for GTA and related games</p>

<h3>Features:</h3>
<ul>
<li>Support for IMG versions 1 and 2</li>
<li>Import and export files</li>
<li>Background processing</li>
<li>File filtering and search</li>
<li>Template system</li>
</ul>

<h3>Supported Games:</h3>
<ul>
<li>GTA III</li>
<li>GTA Vice City</li>
<li>GTA San Andreas</li>
<li>GTA Liberty City Stories</li>
<li>GTA Vice City Stories</li>
<li>Bully (Canis Canem Edit)</li>
</ul>

<p><b>Version:</b> 2.0<br>
<b>Build:</b> Python/PyQt6</p>
        """
        
        QMessageBox.about(self, "About IMG Factory", about_text)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("X-Seti")
    
    # Apply theme if available
    if apply_theme_to_app:
        try:
            # Create dummy settings if AppSettings not available
            if AppSettings:
                settings = AppSettings()
                apply_theme_to_app(app, settings)
            else:
                app.setStyleSheet("""
                    QMainWindow {
                        background-color: #f0f0f0;
                    }
                    QGroupBox {
                        font-weight: bold;
                        border: 2px solid #cccccc;
                        border-radius: 5px;
                        margin-top: 1ex;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 5px 0 5px;
                    }
                    QPushButton {
                        background-color: #e1e1e1;
                        border: 2px solid #999999;
                        border-radius: 6px;
                        padding: 6px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                    QPushButton:pressed {
                        background-color: #c0c0c0;
                    }
                    QPushButton:disabled {
                        background-color: #f0f0f0;
                        color: #999999;
                    }
                """)
        except Exception as e:
            print(f"Failed to apply theme: {e}")
    
    # Apply button theme if available
    if apply_pastel_theme_to_buttons:
        try:
            apply_pastel_theme_to_buttons(app, None)
        except Exception as e:
            print(f"Failed to apply button theme: {e}")
    
    # Create and show main window
    window = IMGFactoryMain()
    window.show()
    
    # Add welcome message
    window.log_message("IMG Factory 2.0 started successfully")
    window.log_message("Ready to load IMG files")
    
    # Try to integrate COL functionality
    try:
        from imgfactory_col_integration import setup_col_integration
        if setup_col_integration(window):
            window.log_message("COL functionality integrated successfully")
        else:
            window.log_message("COL integration failed - functionality disabled")
    except ImportError:
        window.log_message("COL components not found - COL functionality disabled")
    except Exception as e:
        window.log_message(f"COL integration error: {str(e)}")
    
    # Try to integrate COL GUI components
    try:
        if setup_col_gui:
            if setup_col_gui(window):
                window.log_message("COL GUI components integrated successfully")
            else:
                window.log_message("COL GUI integration failed")
        else:
            window.log_message("COL GUI components not available")
    except Exception as e:
        window.log_message(f"COL GUI integration error: {str(e)}")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())