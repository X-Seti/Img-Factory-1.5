#this belongs in root /imgfactory.py

#!/usr/bin/env python3
"""
X-Seti - June25 2025 - IMG Factory 1.5
Main Application with reverted single file open dialog
and new combined multiple file open functionality
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

# Import components with robust error handling
print("Loading IMG Factory components...")

# Core classes - these must work
try:
    from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
    print("✓ IMG Core Classes imported")
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Critical: IMG Core Classes failed: {e}")
    CORE_AVAILABLE = False

# Creator dialog - essential for new IMG creation
try:
    from components.img_creator import NewIMGDialog
    print("✓ IMG Creator imported")
    CREATOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ IMG Creator failed: {e}")
    CREATOR_AVAILABLE = False

# Template system - use what exists
try:
    from components.img_template_manager import IMGTemplateManager, TemplateManagerDialog
    print("✓ IMG Template Manager imported")
    TEMPLATES_AVAILABLE = True
except ImportError:
    try:
        from components.img_templates import IMGTemplateManager, TemplateManagerDialog  
        print("✓ IMG Templates imported")
        TEMPLATES_AVAILABLE = True
    except ImportError as e:
        print(f"⚠ Template system not available: {e}")
        # Create robust dummy classes
        class IMGTemplateManager:
            def __init__(self): 
                print("Using dummy template manager")
            def get_user_templates(self): 
                return []
            def save_template(self, *args): 
                return False
            def delete_template(self, *args):
                return False
            def import_templates(self, *args):
                return {"imported": 0, "skipped": 0, "errors": []}
            def export_templates(self, *args):
                return False
        
        class TemplateManagerDialog:
            def __init__(self, *args): 
                pass
            def exec(self): 
                return 0
        TEMPLATES_AVAILABLE = False

# Validator - now should work with fixed dependencies
try:
    from components.img_validator import IMGValidator
    print("✓ IMG Validator imported")
    VALIDATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠ IMG Validator not available: {e}")
    class IMGValidator:
        @staticmethod
        def validate_img_file(img_file):
            class ValidationResult:
                def __init__(self):
                    self.is_valid = True
                def get_summary(self):
                    return "Validation not available"
                def get_details(self):
                    return "Validation system not loaded"
            return ValidationResult()
    VALIDATOR_AVAILABLE = False

# Combined open dialog
try:
    from components.img_combined_open_dialog import CombinedOpenDialog, show_combined_open_dialog, open_single_img_file
    print("✓ Combined Open Dialog imported")
    COMBINED_DIALOG_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Combined Open Dialog not available: {e}")
    # Create fallback functions
    def show_combined_open_dialog(parent=None):
        from PyQt6.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(
            parent, 
            "Open Files", 
            "", 
            "All Supported (*.img *.col *.txd *.dff);;IMG Files (*.img);;All Files (*)"
        )
        return files, "multiple"
    
    def open_single_img_file(parent=None):
        from PyQt6.QtWidgets import QFileDialog
        file, _ = QFileDialog.getOpenFileName(
            parent, 
            "Open IMG Archive", 
            "", 
            "IMG Files (*.img);;All Files (*)"
        )
        return file
    COMBINED_DIALOG_AVAILABLE = False

# Optional pastel theme
try:
    from gui.pastel_button_theme import apply_pastel_theme_to_buttons
    print("✓ Pastel Theme imported (gui folder)")
    THEME_AVAILABLE = True
except ImportError:
    try:
        from pastel_button_theme import apply_pastel_theme_to_buttons
        print("✓ Pastel Theme imported (root level)")
        THEME_AVAILABLE = True
    except ImportError:
        print("⚠ Pastel theme not available - using default styling")
        def apply_pastel_theme_to_buttons(widget):
            pass
        THEME_AVAILABLE = False

# Check if we can continue
if not CORE_AVAILABLE:
    print("❌ Cannot continue without core IMG classes")
    print("Please ensure components/img_core_classes.py exists")
    sys.exit(1)

print(f"\n🎯 Component Status Summary:")
print(f"   Core Classes: {'✓' if CORE_AVAILABLE else '❌'}")
print(f"   Creator Dialog: {'✓' if CREATOR_AVAILABLE else '❌'}")
print(f"   Templates: {'✓' if TEMPLATES_AVAILABLE else '⚠'}")
print(f"   Validator: {'✓' if VALIDATOR_AVAILABLE else '⚠'}")
print(f"   Combined Dialog: {'✓' if COMBINED_DIALOG_AVAILABLE else '⚠'}")
print(f"   Theme System: {'✓' if THEME_AVAILABLE else '⚠'}")
print("✅ IMG Factory ready to start!\n")


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
            
            # Validate the loaded file
            validation = IMGValidator.validate_img_file(img_file)
            if not validation.is_valid:
                self.loading_error.emit(f"IMG file validation failed: {validation.get_summary()}")
                return
            
            self.progress_updated.emit(100, "Complete")
            self.loading_finished.emit(img_file)
            
        except Exception as e:
            self.loading_error.emit(f"Loading failed: {str(e)}")


class IMGFactoryMain(QMainWindow):
    """Main IMG Factory application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        
        # Application state
        self.current_img: Optional[IMGFile] = None
        self.settings = QSettings("IMGFactory", "ImgFactory15")
        
        # Initialize template manager with error handling
        try:
            self.template_manager = IMGTemplateManager()
        except Exception as e:
            print(f"⚠ Template manager initialization failed: {e}")
            # Create dummy template manager
            class DummyTemplateManager:
                def __init__(self): pass
                def get_user_templates(self): return []
                def save_template(self, *args): return False
            self.template_manager = DummyTemplateManager()
        
        # Threads
        self.load_thread: Optional[IMGLoadThread] = None
        
        self._create_ui()
        self._create_menu()
        self._create_status_bar()
        self._connect_signals()
        self._restore_settings()
        
        # Apply theme
        apply_pastel_theme_to_buttons(self)
    
    def _create_ui(self):
        """Create the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel - File operations
        self._create_left_panel(main_splitter)
        
        # Right splitter for entries and log
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(right_splitter)
        
        # Entries table
        self._create_entries_section(right_splitter)
        
        # Log section
        self._create_log_section(right_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([300, 900])
        right_splitter.setSizes([600, 200])
    
    def _create_left_panel(self, parent):
        """Create left control panel"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        
        # IMG File Operations
        img_group = QGroupBox("IMG Operations")
        img_layout = QVBoxLayout(img_group)
        
        self.new_img_btn = QPushButton("🆕 New IMG")
        self.new_img_btn.clicked.connect(self.create_new_img)
        img_layout.addWidget(self.new_img_btn)
        
        self.open_img_btn = QPushButton("📂 Open IMG")
        self.open_img_btn.clicked.connect(self.open_img_file)
        img_layout.addWidget(self.open_img_btn)
        
        self.open_multiple_btn = QPushButton("📁 Open Multiple Files")
        self.open_multiple_btn.clicked.connect(self.open_multiple_files)
        img_layout.addWidget(self.open_multiple_btn)
        
        self.close_img_btn = QPushButton("✖️ Close IMG")
        self.close_img_btn.clicked.connect(self.close_img_file)
        self.close_img_btn.setEnabled(False)
        img_layout.addWidget(self.close_img_btn)
        
        layout.addWidget(img_group)
        
        # Entry Operations
        entry_group = QGroupBox("Entry Operations")
        entry_layout = QVBoxLayout(entry_group)
        
        self.import_files_btn = QPushButton("⬆️ Import Files")
        self.import_files_btn.clicked.connect(self.import_files)
        self.import_files_btn.setEnabled(False)
        entry_layout.addWidget(self.import_files_btn)
        
        self.export_selected_btn = QPushButton("⬇️ Export Selected")
        self.export_selected_btn.clicked.connect(self.export_selected_entries)
        self.export_selected_btn.setEnabled(False)
        entry_layout.addWidget(self.export_selected_btn)
        
        self.export_all_btn = QPushButton("⬇️ Export All")
        self.export_all_btn.clicked.connect(self.export_all_entries)
        self.export_all_btn.setEnabled(False)
        entry_layout.addWidget(self.export_all_btn)
        
        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected_entries)
        self.remove_btn.setEnabled(False)
        entry_layout.addWidget(self.remove_btn)
        
        layout.addWidget(entry_group)
        
        # Tools
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        self.validate_btn = QPushButton("✅ Validate IMG")
        self.validate_btn.clicked.connect(self.validate_img)
        self.validate_btn.setEnabled(False)
        tools_layout.addWidget(self.validate_btn)
        
        self.rebuild_btn = QPushButton("🔧 Rebuild IMG")
        self.rebuild_btn.clicked.connect(self.rebuild_img)
        self.rebuild_btn.setEnabled(False)
        tools_layout.addWidget(self.rebuild_btn)
        
        layout.addWidget(tools_group)
        
        # IMG Info
        info_group = QGroupBox("IMG Information")
        info_layout = QVBoxLayout(info_group)
        
        self.img_info_label = QLabel("No IMG loaded")
        self.img_info_label.setWordWrap(True)
        info_layout.addWidget(self.img_info_label)
        
        self.entry_count_label = QLabel("Entries: 0")
        info_layout.addWidget(self.entry_count_label)
        
        self.file_size_label = QLabel("Size: 0 B")
        info_layout.addWidget(self.file_size_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        parent.addWidget(left_widget)
    
    def _create_entries_section(self, parent):
        """Create entries table section"""
        entries_widget = QWidget()
        layout = QVBoxLayout(entries_widget)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("📁 IMG Entries")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search entries...")
        self.search_box.textChanged.connect(self._filter_entries)
        header_layout.addWidget(self.search_box)
        
        layout.addLayout(header_layout)
        
        # Entries table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(4)
        self.entries_table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Offset"])
        self.entries_table.horizontalHeader().setStretchLastSection(True)
        self.entries_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)
        layout.addWidget(self.entries_table)
        
        parent.addWidget(entries_widget)
    
    def _create_log_section(self, parent):
        """Create log section"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        
        # Header
        log_header = QLabel("📋 Activity Log")
        log_header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(log_header)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        parent.addWidget(log_widget)
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New IMG", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_img)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open IMG", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        open_multi_action = QAction("Open Multiple Files", self)
        open_multi_action.setShortcut("Ctrl+Shift+O")
        open_multi_action.triggered.connect(self.open_multiple_files)
        file_menu.addAction(open_multi_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("Close IMG", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        import_action = QAction("Import Files", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_files)
        edit_menu.addAction(import_action)
        
        export_selected_action = QAction("Export Selected", self)
        export_selected_action.setShortcut("Ctrl+E")
        export_selected_action.triggered.connect(self.export_selected_entries)
        edit_menu.addAction(export_selected_action)
        
        export_all_action = QAction("Export All", self)
        export_all_action.setShortcut("Ctrl+Shift+E")
        export_all_action.triggered.connect(self.export_all_entries)
        edit_menu.addAction(export_all_action)
        
        edit_menu.addSeparator()
        
        remove_action = QAction("Remove Selected", self)
        remove_action.setShortcut("Delete")
        remove_action.triggered.connect(self.remove_selected_entries)
        edit_menu.addAction(remove_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        validate_action = QAction("Validate IMG", self)
        validate_action.setShortcut("Ctrl+V")
        validate_action.triggered.connect(self.validate_img)
        tools_menu.addAction(validate_action)
        
        rebuild_action = QAction("Rebuild IMG", self)
        rebuild_action.setShortcut("Ctrl+R")
        rebuild_action.triggered.connect(self.rebuild_img)
        tools_menu.addAction(rebuild_action)
        
        tools_menu.addSeparator()
        
        templates_action = QAction("Manage Templates", self)
        templates_action.triggered.connect(self.manage_templates)
        tools_menu.addAction(templates_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        search_action = QAction("Search Entries", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self._focus_search)
        view_menu.addAction(search_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # IMG info
        self.img_status_label = QLabel("No IMG loaded")
        self.status_bar.addPermanentWidget(self.img_status_label)
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.entries_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.entries_table.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _restore_settings(self):
        """Restore application settings"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def _save_settings(self):
        """Save application settings"""
        self.settings.setValue("geometry", self.saveGeometry())
    
    # Event handlers
    def _on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = len(self.entries_table.selectionModel().selectedRows())
        has_selection = selected_rows > 0
        has_img = self.current_img is not None
        
        # Update button states
        self.export_selected_btn.setEnabled(has_selection and has_img)
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
        if name_item and self.current_img:
            entry_name = name_item.text()
            entry = self.current_img.get_entry_by_name(entry_name)
            if entry:
                self.log_message(f"Entry info: {entry.name} ({format_file_size(entry.size)})")
    
    def _filter_entries(self, text):
        """Filter entries table based on search text"""
        for row in range(self.entries_table.rowCount()):
            item = self.entries_table.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower() if text else True
                self.entries_table.setRowHidden(row, not visible)
    
    def _focus_search(self):
        """Focus the search box"""
        self.search_box.setFocus()
        self.search_box.selectAll()
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
<h3>IMG Factory 1.5</h3>
<p>Advanced IMG archive manager for GTA games</p>
<p><b>Features:</b></p>
<ul>
<li>Support for GTA III, Vice City, San Andreas, and IV</li>
<li>Create, edit, and manage IMG archives</li>
<li>Import/export files with validation</li>
<li>Template system for quick archive creation</li>
</ul>
<p><b>Supported Files:</b> IMG, COL, TXD, DFF, IFP, WAV, SCM</p>
<p>X-Seti - June25 2025</p>
        """
        QMessageBox.about(self, "About IMG Factory 1.5", about_text)
    
    # Core functionality
    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(self)
        dialog.template_manager = self.template_manager
        dialog.img_created.connect(self.load_img_file)
        dialog.exec()
    
    def open_img_file(self):
        """Open IMG file dialog - REVERTED TO ORIGINAL SINGLE FILE"""
        file_path = open_single_img_file(self)
        
        if file_path:
            self.load_img_file(file_path)
    
    def open_multiple_files(self):
        """Open multiple files dialog - NEW COMBINED FUNCTIONALITY"""
        files, mode = show_combined_open_dialog(self)
        
        if files:
            if mode == "single" and len(files) == 1:
                # Single IMG file
                self.load_img_file(files[0])
            elif mode == "multiple":
                # Multiple files - handle appropriately
                self._handle_multiple_files(files)
    
    def _handle_multiple_files(self, files: List[str]):
        """Handle opening multiple files"""
        img_files = [f for f in files if f.lower().endswith('.img')]
        other_files = [f for f in files if not f.lower().endswith('.img')]
        
        if img_files:
            # Load the first IMG file
            self.load_img_file(img_files[0])
            
            if len(img_files) > 1:
                self.log_message(f"Note: Only first IMG file loaded. Other IMG files ignored.")
        
        if other_files and self.current_img:
            # Import other files into the loaded IMG
            self.log_message(f"Importing {len(other_files)} additional files...")
            # This would trigger the import process
            # Implementation depends on existing import functionality
        elif other_files:
            self.log_message("Cannot import files - no IMG archive loaded")
    
    def load_img_file(self, file_path: str):
        """Load IMG file"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.log_message(f"Loading IMG file: {os.path.basename(file_path)}")
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.status_label.setText("Loading IMG file...")
        
        # Start loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._update_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_load_error)
        self.load_thread.start()
    
    def _update_load_progress(self, progress: int, status: str):
        """Update loading progress"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        self.current_img = img_file
        
        # Update UI
        self._populate_entries_table()
        self._update_img_info()
        self._update_button_states()
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
        self.log_message(f"Loaded IMG: {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")
    
    def _on_load_error(self, error_message: str):
        """Handle IMG loading error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
        self.log_error(f"Failed to load IMG: {error_message}")
        QMessageBox.critical(self, "Loading Error", f"Failed to load IMG file:\n{error_message}")
    
    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
            
            # Clear UI
            self.entries_table.setRowCount(0)
            self._update_img_info()
            self._update_button_states()
            
            self.log_message("IMG file closed")
    
    def _populate_entries_table(self):
        """Populate entries table"""
        if not self.current_img:
            return
        
        self.entries_table.setRowCount(len(self.current_img.entries))
        
        for row, entry in enumerate(self.current_img.entries):
            # Name
            name_item = QTableWidgetItem(entry.name)
            self.entries_table.setItem(row, 0, name_item)
            
            # Type
            ext = os.path.splitext(entry.name)[1].upper().lstrip('.')
            type_item = QTableWidgetItem(ext or "Unknown")
            self.entries_table.setItem(row, 1, type_item)
            
            # Size
            size_item = QTableWidgetItem(format_file_size(entry.size))
            self.entries_table.setItem(row, 2, size_item)
            
            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:08X}")
            self.entries_table.setItem(row, 3, offset_item)
        
        # Resize columns
        self.entries_table.resizeColumnsToContents()
    
    def _update_img_info(self):
        """Update IMG information display"""
        if self.current_img:
            file_name = os.path.basename(self.current_img.file_path)
            file_size = os.path.getsize(self.current_img.file_path)
            
            self.img_info_label.setText(f"File: {file_name}\nVersion: {self.current_img.version.name}")
            self.entry_count_label.setText(f"Entries: {len(self.current_img.entries)}")
            self.file_size_label.setText(f"Size: {format_file_size(file_size)}")
            self.img_status_label.setText(f"IMG: {file_name}")
        else:
            self.img_info_label.setText("No IMG loaded")
            self.entry_count_label.setText("Entries: 0")
            self.file_size_label.setText("Size: 0 B")
            self.img_status_label.setText("No IMG loaded")
    
    def _update_button_states(self):
        """Update button enabled states"""
        has_img = self.current_img is not None
        
        # IMG operations
        self.close_img_btn.setEnabled(has_img)
        
        # Entry operations
        self.import_files_btn.setEnabled(has_img)
        self.export_all_btn.setEnabled(has_img)
        
        # Tools
        self.validate_btn.setEnabled(has_img)
        self.rebuild_btn.setEnabled(has_img)
    
    # File operations (placeholders for now)
    def import_files(self):
        """Import files into IMG"""
        if not self.current_img:
            return
        
        self.log_message("Import functionality coming soon!")
        QMessageBox.information(self, "Import", "Import functionality will be implemented next")
    
    def export_selected_entries(self):
        """Export selected entries"""
        if not self.current_img:
            return
        
        self.log_message("Export selected functionality coming soon!")
        QMessageBox.information(self, "Export", "Export selected functionality will be implemented next")
    
    def export_all_entries(self):
        """Export all entries"""
        if not self.current_img:
            return
        
        self.log_message("Export all functionality coming soon!")
        QMessageBox.information(self, "Export", "Export all functionality will be implemented next")
    
    def remove_selected_entries(self):
        """Remove selected entries"""
        if not self.current_img:
            return
        
        self.log_message("Remove entries functionality coming soon!")
        QMessageBox.information(self, "Remove", "Remove entries functionality will be implemented next")
    
    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            return
        
        try:
            self.status_label.setText("Validating IMG archive...")
            
            validation = IMGValidator.validate_img_file(self.current_img)
            
            result_text = f"Validation Result: {validation.get_summary()}\n\n"
            result_text += validation.get_details()
            
            if validation.is_valid:
                QMessageBox.information(self, "Validation Result", result_text)
            else:
                QMessageBox.warning(self, "Validation Result", result_text)
            
            self.log_message(f"Validation: {validation.get_summary()}")
            
        except Exception as e:
            self.log_error(f"Validation error: {str(e)}")
        finally:
            self.status_label.setText("Ready")
    
    def rebuild_img(self):
        """Rebuild IMG file"""
        if not self.current_img:
            return
        
        reply = QMessageBox.question(
            self, "Rebuild IMG",
            "This will rebuild the IMG file and may take some time.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_message("Rebuild functionality coming soon!")
            QMessageBox.information(self, "Rebuild", "Rebuild functionality will be implemented next")
    
    def manage_templates(self):
        """Show template manager"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.exec()
    
    # Logging
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = QTimer()
        timestamp.singleShot(0, lambda: self.log_text.append(f"[INFO] {message}"))
    
    def log_error(self, message: str):
        """Add error message to log"""
        timestamp = QTimer()
        timestamp.singleShot(0, lambda: self.log_text.append(f"[ERROR] {message}"))
    
    # Window events
    def closeEvent(self, event):
        """Handle window close"""
        self._save_settings()
        
        if self.current_img:
            self.current_img.close()
        
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("IMG Factory 1.5")
    app.setApplicationVersion("1.5")
    app.setOrganizationName("X-Seti")
    
    # Create and show main window
    window = IMGFactoryMain()
    window.show()
    
    # Log startup
    window.log_message("IMG Factory 1.5 started")
    window.log_message("Ready to work with IMG archives")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
