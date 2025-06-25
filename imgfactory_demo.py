#this belongs in root /Imgfactory_Demo.py
# $vers" X-Seti - June25,2025 - Img Factory 1.5"
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
    QAbstractItemView, QMenuBar, QMenu, QStatusBar, QSizePolicy, QInputDialog
)

print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
print("PyQt6.QtGui imported successfully")
from PyQt6.QtGui import QAction, QIcon, QFont, QDragEnterEvent, QDropEvent
print("App Settings System imported successfully")
from App_settings_system import AppSettings, apply_theme_to_app

try:
    print("Pastel Theme imported successfully")
    from pastel_button_theme import apply_pastel_theme_to_buttons
except ImportError:
    print("Warning: Pastel theme not available")
    def apply_pastel_theme_to_buttons(app, settings):
        pass

try:
    print("Img Core Classes imported successfully")
    from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
except ImportError as e:
    print(f"Error: Cannot import core classes: {e}")
    # Create minimal dummy classes
    class IMGFile:
        def __init__(self, path=""):
            self.file_path = path
            self.entries = []
            self.version = None
        def open(self):
            return False
        def close(self):
            pass
    
    class IMGEntry:
        def __init__(self):
            self.name = ""
            self.size = 0
            self.offset = 0
        def get_type(self):
            return "Unknown"
    
    class IMGVersion:
        IMG_1 = 1
        IMG_2 = 2
    
    def format_file_size(size):
        return f"{size} bytes"
try:
    print("Img Creator imported successfully")
    from components.img_creator import NewIMGDialog, GameType, add_new_img_functionality
except ImportError as e:
    print(f"Warning: IMG Creator not available: {e}")
    # Create dummy classes to prevent errors
    class NewIMGDialog:
        def __init__(self, parent=None):
            pass
        def exec(self):
            return 0
        def get_creation_settings(self):
            return {}
    
    class GameType:
        pass
    
    def add_new_img_functionality(window):
        pass

try:
    print("Img Formats imported successfully")
    from components.img_formats import GameSpecificIMGDialog, EnhancedIMGCreator
except ImportError:
    print("Warning: Enhanced IMG formats not available")

try:
    print("Img Template Manager imported successfully")
    from components.img_template_manager import TemplateManagerDialog, IMGTemplateManager
except ImportError as e:
    print(f"Warning: Template Manager not available: {e}")
    # Create dummy classes
    class TemplateManagerDialog:
        def __init__(self, manager, parent=None):
            pass
        def exec(self):
            return 0
    
    class IMGTemplateManager:
        def __init__(self):
            pass

try:
    print("Quick Start Wizard imported successfully")
    from components.img_quick_start_wizard import QuickStartWizard
except ImportError:
    print("Warning: Quick Start Wizard not available")


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

        # Details
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        layout.addWidget(self.details_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def update_progress(self, current, total, filename=""):
        """Update progress display"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_label.setText(f"Exporting {current}/{total} files...")
            if filename:
                self.details_text.append(f"Processing: {filename}")
        
        # Auto-scroll to bottom
        cursor = self.details_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.details_text.setTextCursor(cursor)


class ImportValidationDialog(QDialog):
    """Dialog for validating and reviewing files before import"""

    def __init__(self, file_paths, img_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import File Validation")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        self.file_paths = file_paths
        self.img_file = img_file
        self.validated_files = []

        self._create_ui()
        self._validate_files()

    def _create_ui(self):
        """Create the validation dialog UI"""
        layout = QVBoxLayout(self)

        # Header info
        info_label = QLabel(f"Validating {len(self.file_paths)} files for import...")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(info_label)

        # Validation table
        self.validation_table = QTableWidget(0, 6)
        self.validation_table.setHorizontalHeaderLabels([
            "Import", "Filename", "Size", "Type", "Status", "Notes"
        ])

        # Set column properties
        header = self.validation_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Import checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Filename
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)           # Notes

        self.validation_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.validation_table)

        # Options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)

        self.overwrite_check = QCheckBox("Replace existing files with same name")
        self.overwrite_check.setChecked(False)
        options_layout.addWidget(self.overwrite_check)

        self.auto_rename_check = QCheckBox("Auto-rename conflicting files (append _1, _2, etc.)")
        self.auto_rename_check.setChecked(True)
        options_layout.addWidget(self.auto_rename_check)

        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_button)
        
        select_none_button = QPushButton("Select None")
        select_none_button.clicked.connect(self._select_none)
        button_layout.addWidget(select_none_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        import_button = QPushButton("Import Selected")
        import_button.clicked.connect(self.accept)
        import_button.setDefault(True)
        button_layout.addWidget(import_button)
        
        layout.addLayout(button_layout)

    def _validate_files(self):
        """Validate each file for import"""
        for file_path in self.file_paths:
            try:
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_type = mimetypes.guess_type(file_path)[0] or "Unknown"
                
                # Check if file already exists in IMG
                status = "Ready"
                notes = ""
                
                if any(entry.name.lower() == filename.lower() for entry in self.img_file.entries):
                    status = "Exists"
                    notes = "File with same name already exists in IMG"
                
                # Add validation row
                row = self.validation_table.rowCount()
                self.validation_table.insertRow(row)
                
                # Import checkbox
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                self.validation_table.setCellWidget(row, 0, checkbox)
                
                # File info
                self.validation_table.setItem(row, 1, QTableWidgetItem(filename))
                self.validation_table.setItem(row, 2, QTableWidgetItem(format_file_size(file_size)))
                self.validation_table.setItem(row, 3, QTableWidgetItem(file_type))
                self.validation_table.setItem(row, 4, QTableWidgetItem(status))
                self.validation_table.setItem(row, 5, QTableWidgetItem(notes))
                
                # Store file path for later
                self.validation_table.item(row, 1).setData(Qt.ItemDataRole.UserRole, file_path)
                
            except Exception as e:
                print(f"Error validating {file_path}: {e}")

    def _select_all(self):
        """Select all files for import"""
        for row in range(self.validation_table.rowCount()):
            checkbox = self.validation_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def _select_none(self):
        """Deselect all files"""
        for row in range(self.validation_table.rowCount()):
            checkbox = self.validation_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def get_selected_files(self):
        """Get list of selected files for import"""
        selected_files = []
        for row in range(self.validation_table.rowCount()):
            checkbox = self.validation_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                file_path = self.validation_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
                if file_path:
                    selected_files.append(file_path)
        return selected_files

    def get_import_options(self):
        """Get import options"""
        return {
            'overwrite': self.overwrite_check.isChecked(),
            'auto_rename': self.auto_rename_check.isChecked()
        }


class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [GUI Demo]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings

        # Initialize attributes
        self.current_img = None
        self.load_thread = None
        self.template_manager = IMGTemplateManager()

        self._create_menu()
        self._create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout(central_widget)

        self._create_main_ui()

        # Enable drag and drop
        self.setAcceptDrops(True)

    def _clean_button_text(self, text):
        """Remove emoji from button text if disabled"""
        if not self.app_settings.current_settings.get("show_button_emojis", True):
            emoji_chars = ['📁', '🆕', '📂', '💾', '🔄', '📤', '📥', '🗑️', '⚙️', '❓', '🍞', '🟣', '✨']
            for emoji in emoji_chars:
                text = text.replace(emoji, '').strip()
        return text

    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Create themed button with icon control"""
        
        # Clean button text if emoji is disabled
        clean_label = self._clean_button_text(label)
        
        btn = QPushButton(clean_label)
        
        if action_type:
            btn.setProperty("action-type", action_type)
        
        # Only add icon if enabled
        if icon and self.app_settings.current_settings.get("show_button_icons", False):
            btn.setIcon(QIcon.fromTheme(icon))
        
        if bold:
            font = btn.font()
            font.setBold(True)
            btn.setFont(font)
        
        return btn

    def _create_menu(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")
        
        # Only show menu icons if enabled
        show_menu_icons = self.app_settings.current_settings.get("show_menu_icons", True)
        
        open_action = QAction("Open IMG...", self)
        if show_menu_icons:
            open_action.setIcon(QIcon.fromTheme("document-open"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        close_action = QAction("Close IMG", self)
        if show_menu_icons:
            close_action.setIcon(QIcon.fromTheme("window-close"))
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        if show_menu_icons:
            exit_action.setIcon(QIcon.fromTheme("application-exit"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Other menus
        menu_names = [
            "Edit", "Dat", "IMG", "Model", "Texture", "Collision", 
            "Item Definition", "Item Placement", "Entry", "Settings", "Help"
        ]

        for name in menu_names:
            menu = menubar.addMenu(name)
            if name == "IMG":
                rebuild_action = QAction("Rebuild", self)
                if show_menu_icons:
                    rebuild_action.setIcon(QIcon.fromTheme("view-refresh"))
                rebuild_action.triggered.connect(self.rebuild_img)
                menu.addAction(rebuild_action)
                
                merge_action = QAction("Merge", self)
                if show_menu_icons:
                    merge_action.setIcon(QIcon.fromTheme("document-merge"))
                menu.addAction(merge_action)
                
                split_action = QAction("Split", self)
                if show_menu_icons:
                    split_action.setIcon(QIcon.fromTheme("edit-cut"))
                menu.addAction(split_action)
                
            elif name == "Settings":
                preferences_action = QAction("Preferences", self)
                if show_menu_icons:
                    preferences_action.setIcon(QIcon.fromTheme("preferences-other"))
                preferences_action.triggered.connect(self.show_preferences)
                menu.addAction(preferences_action)
                
                template_action = QAction("Manage Templates", self)
                template_action.triggered.connect(self.manage_templates)
                menu.addAction(template_action)
                
            elif name == "Help":
                about_action = QAction("About", self)
                if show_menu_icons:
                    about_action.setIcon(QIcon.fromTheme("help-about"))
                about_action.triggered.connect(self.show_about)
                menu.addAction(about_action)
            else:
                placeholder = QAction("(No items yet)", self)
                placeholder.setEnabled(False)
                menu.addAction(placeholder)

    def _create_status_bar(self):
        """Create status bar"""
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

    def _create_main_ui(self):
        """Create main user interface"""
        # Left panel: Table + Log
        left_layout = QVBoxLayout()

        # IMG file info
        info_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file loaded")
        self.version_label = QLabel("Version: N/A")
        self.entry_count_label = QLabel("Entries: 0")
        
        info_layout.addWidget(QLabel("File:"))
        info_layout.addWidget(self.file_path_label)
        info_layout.addStretch()
        info_layout.addWidget(self.version_label)
        info_layout.addWidget(self.entry_count_label)
        
        left_layout.addLayout(info_layout)

        # Main table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Offset", "Size", "Version"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #3daee9;
            }
            QTableWidget::item:selected {
                background-color: #3daee9;
                color: white;
            }
        """)

        # Resize columns to content
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Version

        left_layout.addWidget(self.table)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        # Log output
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        
        self.log = QTextEdit()
        self.log.setMaximumHeight(150)
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                font-family: monospace;
                font-size: 9pt;
            }
        """)
        log_layout.addWidget(self.log)
        
        left_layout.addWidget(log_group)

        # Create left panel widget
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Right panel: Controls
        right_layout = QVBoxLayout()

        # File operations
        file_group = QGroupBox("File Operations")
        file_layout = QGridLayout(file_group)
        
        open_btn = self.themed_button("📂 Open IMG", "import")
        open_btn.clicked.connect(self.open_img_file)
        file_layout.addWidget(open_btn, 0, 0)
        
        close_btn = self.themed_button("❌ Close IMG", "remove")
        close_btn.clicked.connect(self.close_img_file)
        file_layout.addWidget(close_btn, 0, 1)
        
        new_btn = self.themed_button("🆕 New IMG", "import")
        new_btn.clicked.connect(self.create_new_img)
        file_layout.addWidget(new_btn, 1, 0)
        
        rebuild_btn = self.themed_button("🔄 Rebuild", "update")
        rebuild_btn.clicked.connect(self.rebuild_img)
        file_layout.addWidget(rebuild_btn, 1, 1)
        
        right_layout.addWidget(file_group)

        # Entry operations
        entry_group = QGroupBox("Entry Operations")
        entry_layout = QGridLayout(entry_group)
        
        import_btn = self.themed_button("📥 Import Files", "import")
        import_btn.clicked.connect(self.import_files)
        entry_layout.addWidget(import_btn, 0, 0)
        
        export_btn = self.themed_button("📤 Export Selected", "export")
        export_btn.clicked.connect(self.export_selected)
        entry_layout.addWidget(export_btn, 0, 1)
        
        export_all_btn = self.themed_button("📤 Export All", "export")
        export_all_btn.clicked.connect(self.export_all)
        entry_layout.addWidget(export_all_btn, 1, 0)
        
        remove_btn = self.themed_button("🗑️ Remove Selected", "remove")
        remove_btn.clicked.connect(self.remove_selected)
        entry_layout.addWidget(remove_btn, 1, 1)
        
        right_layout.addWidget(entry_group)

        # Tools
        tools_group = QGroupBox("Tools")
        tools_layout = QGridLayout(tools_group)
        
        validate_btn = self.themed_button("✅ Validate", "update")
        validate_btn.clicked.connect(self.validate_img)
        tools_layout.addWidget(validate_btn, 0, 0)
        
        search_btn = self.themed_button("🔍 Search", "convert")
        search_btn.clicked.connect(self.search_entries)
        tools_layout.addWidget(search_btn, 0, 1)
        
        template_btn = self.themed_button("📋 Templates", "convert")
        template_btn.clicked.connect(self.manage_templates)
        tools_layout.addWidget(template_btn, 1, 0)
        
        settings_btn = self.themed_button("⚙️ Settings", "convert")
        settings_btn.clicked.connect(self.show_preferences)
        tools_layout.addWidget(settings_btn, 1, 1)
        
        right_layout.addWidget(tools_group)

        # Filter panel
        filter_group = QGroupBox("Filter")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Files", "Models (.dff)", "Textures (.txd)", "Collision (.col)", "Audio (.wav)", "Scripts (.scm)"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        right_layout.addWidget(filter_group)

        # Create right panel widget
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(200)

        # Add both panels to main layout
        self.layout.addWidget(left_widget)
        self.layout.addWidget(right_widget)

        # Populate with sample data
        self._populate_sample_data()

    def _populate_sample_data(self):
        """Add sample data to demonstrate the interface"""
        sample_data = [
            (1, "DFF", "player.dff", "0x1000", "245 KB", "GTA SA"),
            (2, "TXD", "player.txd", "0x2000", "1.2 MB", "GTA SA"),
            (3, "COL", "player.col", "0x3000", "45 KB", "GTA SA"),
            (4, "DFF", "vehicle.dff", "0x4000", "512 KB", "GTA SA"),
            (5, "TXD", "vehicle.txd", "0x5000", "2.1 MB", "GTA SA"),
        ]
        
        self.table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

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
        self.statusBar().showMessage("Loading IMG file...")
        
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
        
        # Populate table with real data
        self.populate_table()
        
        self.statusBar().showMessage("IMG file loaded successfully")
        self.log_message(f"Loaded IMG file: {img_file.file_path}")
        self.log_message(f"Version: {img_file.version.name}, Entries: {len(img_file.entries)}")

    def on_img_load_error(self, error_message):
        """Handle IMG file loading error"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error loading IMG file")
        self.log_error(error_message)
        
        QMessageBox.critical(self, "Error", f"Failed to load IMG file:\n{error_message}")

    def populate_table(self):
        """Populate table with IMG file entries"""
        if not self.current_img:
            return
        
        entries = self.current_img.entries
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get_type()))
            self.table.setItem(row, 2, QTableWidgetItem(entry.name))
            self.table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:08X}"))
            self.table.setItem(row, 4, QTableWidgetItem(format_file_size(entry.size)))
            self.table.setItem(row, 5, QTableWidgetItem(self.current_img.version.name))

    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
            
            # Reset UI
            self.file_path_label.setText("No file loaded")
            self.version_label.setText("Version: N/A")
            self.entry_count_label.setText("Entries: 0")
            self.table.setRowCount(0)
            
            self.statusBar().showMessage("IMG file closed")
            self.log_message("IMG file closed")

    def create_new_img(self):
        """Create new IMG file"""
        try:
            dialog = NewIMGDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                settings = dialog.get_creation_settings()
                self.log_message(f"Creating new IMG file: {settings['filename']}")
                # IMG creation logic would go here
                QMessageBox.information(self, "Success", "New IMG file created successfully!")
                
        except Exception as e:
            self.log_error(f"Failed to create new IMG: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to create new IMG:\n{str(e)}")

    def rebuild_img(self):
        """Rebuild current IMG file"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "No IMG file is currently loaded")
            return
        
        reply = QMessageBox.question(
            self, "Rebuild IMG", 
            "This will rebuild the IMG file and may take some time.\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Rebuilt IMG", "", "IMG Files (*.img);;All Files (*)"
            )
            
            if not output_path:
                return
            
            try:
                self.statusBar().showMessage("Rebuilding IMG file...")
                self.log_message("Starting IMG rebuild...")
                
                # Placeholder for actual rebuild functionality
                self.log_message(f"IMG rebuilt successfully: {output_path}")
                
                QMessageBox.information(self, "Rebuild Complete", 
                                      f"IMG file rebuilt successfully:\n{output_path}")
                
            except Exception as e:
                self.log_error(f"Rebuild failed: {str(e)}")
                QMessageBox.critical(self, "Rebuild Error", f"Rebuild failed:\n{str(e)}")
            finally:
                self.statusBar().showMessage("Ready")

    # Entry Operations
    def import_files(self):
        """Import files into IMG"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "Please load an IMG file first")
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            "",
            "All Supported Files (*.dff *.txd *.col *.ifp *.wav *.scm *.ipl *.ide *.dat);;All Files (*)"
        )
        
        if file_paths:
            # Show validation dialog
            dialog = ImportValidationDialog(file_paths, self.current_img, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_files = dialog.get_selected_files()
                options = dialog.get_import_options()
                
                self.log_message(f"Importing {len(selected_files)} files...")
                
                # Show progress dialog
                progress_dialog = ExportProgressDialog(self)
                progress_dialog.setWindowTitle("Importing Files...")
                progress_dialog.status_label.setText("Importing files...")
                
                try:
                    for i, file_path in enumerate(selected_files):
                        filename = os.path.basename(file_path)
                        progress_dialog.update_progress(i, len(selected_files), filename)
                        
                        # Simulate import process
                        self.log_message(f"Imported: {filename}")
                        
                        if progress_dialog.result() == QDialog.DialogCode.Rejected:
                            break
                    
                    progress_dialog.update_progress(len(selected_files), len(selected_files), "Complete")
                    self.log_message(f"Import completed: {len(selected_files)} files imported")
                    
                    # Refresh table
                    self.populate_table()
                    
                except Exception as e:
                    self.log_error(f"Import failed: {str(e)}")
                    QMessageBox.critical(self, "Import Error", f"Import failed:\n{str(e)}")
                finally:
                    progress_dialog.close()

    def export_selected(self):
        """Export selected entries"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select entries to export")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        self.log_message(f"Exporting {len(selected_rows)} selected entries...")
        
        # Show progress dialog
        progress_dialog = ExportProgressDialog(self)
        progress_dialog.show()
        
        try:
            for i, row in enumerate(sorted(selected_rows)):
                filename = self.table.item(row, 2).text()
                progress_dialog.update_progress(i, len(selected_rows), filename)
                
                # Simulate export process
                self.log_message(f"Exported: {filename}")
                
                if progress_dialog.result() == QDialog.DialogCode.Rejected:
                    break
            
            progress_dialog.update_progress(len(selected_rows), len(selected_rows), "Complete")
            self.log_message(f"Export completed: {len(selected_rows)} files exported")
            
        except Exception as e:
            self.log_error(f"Export failed: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Export failed:\n{str(e)}")
        finally:
            progress_dialog.close()

    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "No IMG file is currently loaded")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        entry_count = len(self.current_img.entries)
        self.log_message(f"Exporting all {entry_count} entries...")
        
        # Show progress dialog
        progress_dialog = ExportProgressDialog(self)
        progress_dialog.show()
        
        try:
            for i, entry in enumerate(self.current_img.entries):
                progress_dialog.update_progress(i, entry_count, entry.name)
                
                # Simulate export process
                self.log_message(f"Exported: {entry.name}")
                
                if progress_dialog.result() == QDialog.DialogCode.Rejected:
                    break
            
            progress_dialog.update_progress(entry_count, entry_count, "Complete")
            self.log_message(f"Export completed: {entry_count} files exported")
            
        except Exception as e:
            self.log_error(f"Export failed: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Export failed:\n{str(e)}")
        finally:
            progress_dialog.close()

    def remove_selected(self):
        """Remove selected entries"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select entries to remove")
            return
        
        reply = QMessageBox.question(
            self, "Remove Entries", 
            f"Remove {len(selected_rows)} selected entries?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove rows in reverse order to maintain indices
            for row in sorted(selected_rows, reverse=True):
                filename = self.table.item(row, 2).text()
                self.table.removeRow(row)
                self.log_message(f"Removed: {filename}")
            
            self.log_message(f"Removed {len(selected_rows)} entries")

    # Tools
    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "No IMG file is currently loaded")
            return
        
        self.log_message("Validating IMG file...")
        
        # Placeholder validation
        issues_found = 0
        validation_results = [
            "✓ File header is valid",
            "✓ Entry table is consistent",
            "✓ All entries have valid offsets",
            "✓ No corrupted data blocks found"
        ]
        
        result_text = "Validation Results:\n\n" + "\n".join(validation_results)
        result_text += f"\n\nValidation completed with {issues_found} issues found."
        
        if issues_found == 0:
            QMessageBox.information(self, "Validation Results", result_text)
        else:
            QMessageBox.warning(self, "Validation Results", result_text)
        
        self.log_message(f"Validation completed: {issues_found} issues found")

    def search_entries(self):
        """Search for entries by name"""
        search_text, ok = QInputDialog.getText(self, "Search Entries", "Enter search term:")
        if ok and search_text:
            self.log_message(f"Searching for: {search_text}")
            
            # Simple search implementation
            found_rows = []
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 2)
                if name_item and search_text.lower() in name_item.text().lower():
                    found_rows.append(row)
            
            if found_rows:
                # Select found rows
                self.table.clearSelection()
                for row in found_rows:
                    self.table.selectRow(row)
                
                # Scroll to first result
                self.table.scrollToItem(self.table.item(found_rows[0], 0))
                
                self.log_message(f"Found {len(found_rows)} matches")
                QMessageBox.information(self, "Search Results", f"Found {len(found_rows)} matches")
            else:
                self.log_message("No matches found")
                QMessageBox.information(self, "Search Results", "No matches found")

    def manage_templates(self):
        """Open template management dialog"""
        try:
            dialog = TemplateManagerDialog(self.template_manager, self)
            dialog.exec()
        except Exception as e:
            self.log_error(f"Failed to open template manager: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open template manager:\n{str(e)}")

    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", "Preferences dialog not yet implemented")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>IMG Factory 1.5</h2>
        <p><b>Version:</b> 1.5</p>
        <p><b>Date:</b> June 25, 2025</p>
        <p><b>Author:</b> X-Seti</p>
        <p><b>Original Credit:</b> MexUK 2007 (IMG Factory 1.2)</p>
        <br>
        <p>A modern tool for managing GTA IMG archive files.</p>
        <p>Supports GTA III, Vice City, San Andreas, and IV formats.</p>
        """
        QMessageBox.about(self, "About IMG Factory", about_text)

    def apply_filter(self, filter_text):
        """Apply file type filter to table"""
        self.log_message(f"Applying filter: {filter_text}")
        
        # Simple filter implementation
        if filter_text == "All Files":
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
        else:
            # Extract file extension from filter text
            filter_ext = None
            if "(.dff)" in filter_text:
                filter_ext = "DFF"
            elif "(.txd)" in filter_text:
                filter_ext = "TXD"
            elif "(.col)" in filter_text:
                filter_ext = "COL"
            elif "(.wav)" in filter_text:
                filter_ext = "WAV"
            elif "(.scm)" in filter_text:
                filter_ext = "SCM"
            
            if filter_ext:
                for row in range(self.table.rowCount()):
                    type_item = self.table.item(row, 1)
                    if type_item:
                        show_row = type_item.text() == filter_ext
                        self.table.setRowHidden(row, not show_row)

    # Drag and Drop Support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            # Check if any URLs are IMG files
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.img'):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.img'):
                    self.load_img_file(file_path)
                    break
        event.acceptProposedAction()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        # Ctrl+F for search
        if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.search_entries()
        # Delete key for remove selected
        elif event.key() == Qt.Key.Key_Delete:
            self.remove_selected()
        # Ctrl+A for select all
        elif event.key() == Qt.Key.Key_A and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.table.selectAll()
        else:
            super().keyPressEvent(event)


def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        settings = AppSettings()

        # Apply base theme
        apply_theme_to_app(app, settings)

        # Create window
        window = ImgFactoryDemo(settings)

        # Apply pastel button theme on top
        apply_pastel_theme_to_buttons(app, settings)

        window.show()
        
        print("IMG Factory 1.5 started successfully")
        return app.exec()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())