#this belongs in root /imgfactory.py

#!/usr/bin/env python3
"""
X-Seti - JUNE25 2025 - IMG Factory 1.5 - Main Application Entry Point
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
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap

# Import component
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
from components.img_creator import NewIMGDialog
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
from components.img_manager import IMGFile, IMGVersion, Platform
from components.img_validator import IMGValidator
from app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog
print("Components imported successfully")

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
            self.loading_error.emit(f"Loading error: {str(e)}")


class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.app_settings = settings if hasattr(settings, 'themes') else AppSettings()
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        
        # Core data
        self.current_img: Optional[IMGFile] = None
        self.current_col: Optional = None  # For COL file support
        self.template_manager = IMGTemplateManager()
        
        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None
        
        # Initialize UI
        self._create_ui()
        self._connect_signals()
        self._restore_settings()
        
        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)
        
        # Log startup
        self.log_message("IMG Factory 1.5 initialized")
    
    def _create_ui(self):
        """Create the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Check if advanced UI is enabled, otherwise use fallback
        use_advanced_ui = True
        if hasattr(self.settings, 'current_settings'):
            use_advanced_ui = self.settings.current_settings.get('use_advanced_ui', True)
        elif isinstance(self.settings, dict):
            use_advanced_ui = self.settings.get('use_advanced_ui', True)
        
        if use_advanced_ui:
            self._create_advanced_ui(main_layout)
        else:
            self._create_fallback_ui(main_layout)
    
    def _create_advanced_ui(self, main_layout):
        """Create advanced UI with all features"""
        # Create menu and status bars FIRST
        self._create_menu_bar()
        self._create_status_bar()
        
        # Then create main UI
        self._create_main_ui_with_splitters(main_layout)
    
    def _create_fallback_ui(self, main_layout):
        """Create simplified fallback UI"""
        # Create menu and status bars FIRST
        self._create_menu_bar()
        self._create_status_bar()
        
        # Then create main UI
        self._create_main_ui_with_splitters(main_layout)
    
    def _create_main_ui_with_splitters(self, main_layout):
        """Create the main UI with resizable splitters"""
        
        # Main horizontal splitter (left side vs right side)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Table and Log with vertical splitter
        left_widget = self._create_left_panel()
        
        # Right side: Controls
        right_widget = self._create_right_panel()
        
        # Add widgets to main splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        
        # Set initial sizes (left panel takes 70%, right panel takes 30%)
        self.main_splitter.setSizes([840, 360])
        
        # Set minimum sizes to prevent panels from becoming too small
        self.main_splitter.setChildrenCollapsible(False)
        
        # Style the splitter
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #666666;
                border: 1px solid #444444;
                width: 6px;
                margin: 2px;
                border-radius: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #888888;
            }
            
            QSplitter::handle:pressed {
                background-color: #999999;
            }
        """)
        
        main_layout.addWidget(self.main_splitter)
    
    def _create_left_panel(self):
        """Create the left panel with tabs and log, separated by a vertical splitter"""
        
        # Main container for left panel
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vertical splitter for tabs+content vs log
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section: File type tabs + main content
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(5, 5, 5, 0)
        
        # File type tabs (IMG, COL, Both) 
        self.file_type_tabs = QTabWidget()
        self.file_type_tabs.setMaximumHeight(120)  # Limit tab height to keep info panels small
        
        # IMG tab
        img_tab = self._create_img_tab()
        self.file_type_tabs.addTab(img_tab, "📁 IMG Files")
        
        # COL tab
        col_tab = self._create_col_tab()
        self.file_type_tabs.addTab(col_tab, "🔧 COL Files")
        
        # Both tab
        both_tab = self._create_both_tab()
        self.file_type_tabs.addTab(both_tab, "📦 Both")
        
        top_layout.addWidget(self.file_type_tabs)
        
        # Main content area with table (below the tabs)
        main_content = self._create_main_content_area()
        top_layout.addWidget(main_content)
        
        # Add top section to splitter
        self.left_splitter.addWidget(top_section)
        
        # Log widget (bottom section)
        log_section = QWidget()
        log_layout = QVBoxLayout(log_section)
        log_layout.setContentsMargins(5, 0, 5, 5)
        
        log_label = QLabel("📜 Activity Log")
        log_label.setStyleSheet("font-weight: bold; color: #666;")
        log_layout.addWidget(log_label)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Activity log will appear here...")
        self.log.setMaximumHeight(150)
        self.log.setMinimumHeight(80)
        self.log.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
            }
        """)
        
        log_layout.addWidget(self.log)
        log_section.setLayout(log_layout)
        
        # Add log section to splitter
        self.left_splitter.addWidget(log_section)
        
        # Set initial sizes (main content large, log small)
        self.left_splitter.setSizes([500, 150])
        
        # Style the main vertical splitter
        self.left_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #666666;
                border: 1px solid #444444;
                height: 6px;
                margin: 2px;
                border-radius: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #888888;
            }
            
            QSplitter::handle:pressed {
                background-color: #999999;
            }
        """)
        
        # Add sample data
        self._populate_sample_data()
        
        # Add splitter to main layout
        left_layout.addWidget(self.left_splitter)
        
        return left_container
    
    def _create_img_tab(self) -> QWidget:
        """Create IMG files tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for clean splitter
        
        # Create vertical splitter for info panel vs content
        info_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # IMG file information panel (compact)
        info_group = QGroupBox("📁 IMG File Information")
        info_layout = QHBoxLayout(info_group)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        # File path
        info_layout.addWidget(QLabel("File:"))
        self.file_path_label = QLabel("No file loaded")
        self.file_path_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        info_layout.addWidget(self.file_path_label)
        info_layout.addStretch()
        
        # Version info
        info_layout.addWidget(QLabel("Version:"))
        self.version_label = QLabel("Unknown")
        info_layout.addWidget(self.version_label)
        
        # Entry count
        info_layout.addWidget(QLabel("Entries:"))
        self.entry_count_label = QLabel("0")
        info_layout.addWidget(self.entry_count_label)
        
        # Set fixed height for info panel (about 3 text lines)
        info_group.setMaximumHeight(80)
        info_group.setMinimumHeight(60)
        
        # Add info panel to splitter
        info_splitter.addWidget(info_group)
        
        # Placeholder for main content (will be replaced with actual content)
        content_placeholder = QLabel("Main content area")
        content_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px dashed #ccc;")
        info_splitter.addWidget(content_placeholder)
        
        # Set splitter proportions (info small, content large)
        info_splitter.setSizes([80, 400])
        info_splitter.setCollapsible(0, False)  # Don't allow info panel to collapse
        
        # Style the splitter
        info_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                border: 1px solid #999999;
                height: 4px;
                margin: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #aaaaaa;
            }
            
            QSplitter::handle:pressed {
                background-color: #888888;
            }
        """)
        
        layout.addWidget(info_splitter)
        
        return tab
    
    def _create_col_tab(self) -> QWidget:
        """Create COL files tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create vertical splitter for info panel vs content
        info_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # COL file information panel (compact)
        info_group = QGroupBox("🔧 COL File Information")
        info_layout = QHBoxLayout(info_group)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        # File path
        info_layout.addWidget(QLabel("File:"))
        self.col_file_path_label = QLabel("No COL file loaded")
        self.col_file_path_label.setStyleSheet("font-weight: bold; color: #D32F2F;")
        info_layout.addWidget(self.col_file_path_label)
        info_layout.addStretch()
        
        # Model count
        info_layout.addWidget(QLabel("Models:"))
        self.col_model_count_label = QLabel("0")
        info_layout.addWidget(self.col_model_count_label)
        
        # Set fixed height for info panel
        info_group.setMaximumHeight(80)
        info_group.setMinimumHeight(60)
        
        # Add info panel to splitter
        info_splitter.addWidget(info_group)
        
        # Placeholder for COL content
        col_content_placeholder = QLabel("COL content area")
        col_content_placeholder.setStyleSheet("background-color: #fff5f5; border: 1px dashed #ffcdd2;")
        info_splitter.addWidget(col_content_placeholder)
        
        # Set splitter proportions
        info_splitter.setSizes([80, 400])
        info_splitter.setCollapsible(0, False)
        
        # Style the splitter
        info_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                border: 1px solid #999999;
                height: 4px;
                margin: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #aaaaaa;
            }
        """)
        
        layout.addWidget(info_splitter)
        
        return tab
    
    def _create_both_tab(self) -> QWidget:
        """Create Both files tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create vertical splitter for info panel vs content
        info_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Combined file information panel (compact)
        info_group = QGroupBox("📦 Combined File Operations")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(5, 2, 5, 2)  # Tighter margins
        
        # IMG info row
        img_row = QHBoxLayout()
        img_row.addWidget(QLabel("IMG:"))
        self.both_img_label = QLabel("No IMG file")
        self.both_img_label.setStyleSheet("font-weight: bold;")
        img_row.addWidget(self.both_img_label)
        img_row.addStretch()
        info_layout.addLayout(img_row)
        
        # COL info row
        col_row = QHBoxLayout()
        col_row.addWidget(QLabel("COL:"))
        self.both_col_label = QLabel("No COL file")
        self.both_col_label.setStyleSheet("font-weight: bold;")
        col_row.addWidget(self.both_col_label)
        col_row.addStretch()
        info_layout.addLayout(col_row)
        
        # Set fixed height for info panel (2 rows + padding)
        info_group.setMaximumHeight(85)
        info_group.setMinimumHeight(65)
        
        # Add info panel to splitter
        info_splitter.addWidget(info_group)
        
        # Placeholder for combined content
        both_content_placeholder = QLabel("Combined operations area")
        both_content_placeholder.setStyleSheet("background-color: #f3e5f5; border: 1px dashed #ce93d8;")
        info_splitter.addWidget(both_content_placeholder)
        
        # Set splitter proportions
        info_splitter.setSizes([85, 400])
        info_splitter.setCollapsible(0, False)
        
        # Style the splitter
        info_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                border: 1px solid #999999;
                height: 4px;
                margin: 1px;
            }
            
            QSplitter::handle:hover {
                background-color: #aaaaaa;
            }
        """)
        
        layout.addWidget(info_splitter)
        
        return tab
    
    def _create_main_content_area(self) -> QWidget:
        """Create main content area with table - now integrated into tabs"""
        # This method is no longer needed since content is now in individual tabs
        # But we'll keep it for backward compatibility and put the table here
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the entries table that will be shared across tabs
        self._create_entries_table()
        content_layout.addWidget(self.entries_table)
        
        return content_widget
    
    def _create_entries_table(self):
        """Create the entries table widget"""
        self.entries_table = QTableWidget(0, 6)
        self.entries_table.setHorizontalHeaderLabels([
            "ID", "Type", "Name", "Offset", "Size", "Version"
        ])
        
        # Set table properties
        self.entries_table.verticalHeader().setVisible(False)
        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setShowGrid(True)
        
        # Set column resize modes
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Version
        
        # Apply theme styling
        self._apply_table_theme()
        
        # Set minimum size for table
        self.entries_table.setMinimumSize(400, 200)
        
        # Connect selection changes
        self.entries_table.selectionModel().selectionChanged.connect(self._on_entry_selection_changed)
    
    def _create_right_panel(self):
        """Create the right panel with responsive controls"""
        
        # Container widget for the right panel
        right_widget = QWidget()
        right_widget.setMinimumWidth(250)  # Increased from 150
        right_layout = QVBoxLayout(right_widget)

        # IMG Section with adaptive buttons
        img_box = QGroupBox("IMG Operations")
        img_layout = QGridLayout()
        img_layout.setSpacing(3)  # Tighter spacing
        
        img_buttons = [
            ("New IMG", "import", "document-new", self.create_new_img),
            ("Open IMG", "import", "document-open", self.open_img_file),
            ("Refresh", "update", "view-refresh", self.refresh_table),
            ("Close", None, "window-close", self.close_img_file),
            ("Rebuild", "update", "document-save", self.rebuild_img),
            ("Rebuild As", None, "document-save-as", self.rebuild_img_as),
            ("Rebuild All", None, "document-save", None),
            ("Merge", None, "document-merge", None),
            ("Split", None, "edit-cut", None),
            ("Convert", "convert", "transform", None),
        ]
        
        self.img_buttons = []  # Store button references
        for i, (label, action_type, icon, callback) in enumerate(img_buttons):
            btn = self._create_adaptive_button(label, action_type, icon, callback, bold=True)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entry Operations Section
        entry_box = QGroupBox("Entry Operations")
        entry_layout = QGridLayout()
        entry_layout.setSpacing(3)
        
        entry_buttons = [
            ("Import Files", "import", "go-down", self.import_files),
            ("Export Selected", "export", "go-up", self.export_selected),
            ("Export All", "export", "go-up", self.export_all),
            ("Remove Selected", "remove", "list-remove", self.remove_selected),
            ("Rename", None, "edit", None),
            ("Properties", None, "document-properties", None),
        ]
        
        self.entry_buttons = []
        for i, (label, action_type, icon, callback) in enumerate(entry_buttons):
            btn = self._create_adaptive_button(label, action_type, icon, callback)
            self.entry_buttons.append(btn)
            entry_layout.addWidget(btn, i // 2, i % 2)
        
        entry_box.setLayout(entry_layout)
        right_layout.addWidget(entry_box)

        # COL Operations Section
        col_box = QGroupBox("COL Operations")
        col_layout = QGridLayout()
        col_layout.setSpacing(3)
        
        col_buttons = [
            ("Open COL", "import", "document-open", self.open_col_file),
            ("Export COL", "export", "document-save-as", self.export_col),
            ("Validate", "update", "dialog-ok", None),
            ("Close COL", None, "window-close", self.close_col_file),
        ]
        
        self.col_buttons = []
        for i, (label, action_type, icon, callback) in enumerate(col_buttons):
            btn = self._create_adaptive_button(label, action_type, icon, callback)
            self.col_buttons.append(btn)
            col_layout.addWidget(btn, i // 2, i % 2)
        
        col_box.setLayout(col_layout)
        right_layout.addWidget(col_box)

        # Filter/Search Section
        filter_box = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Types", "DFF Models", "TXD Textures", "COL Collision", "Other"])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)
        
        # Add stretch to push everything to top
        right_layout.addStretch()
        
        return right_widget
    
    def _create_adaptive_button(self, label, action_type=None, icon=None, callback=None, bold=False):
        """Create a themed adaptive button"""
        btn = QPushButton(label)
        
        if action_type:
            btn.setProperty("action-type", action_type)
        
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        
        if bold:
            font = btn.font()
            font.setBold(True)
            btn.setFont(font)
        
        if callback:
            btn.clicked.connect(callback)
        else:
            btn.setEnabled(False)  # Disable buttons without callbacks
        
        return btn
    
    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Legacy method for compatibility"""
        return self._create_adaptive_button(label, action_type, icon, None, bold)
    
    def _create_menu_bar(self):
        """Create the comprehensive menu bar"""
        menubar = self.menuBar()

        # All menu names from the original design
        menu_names = [
            "File", "Edit", "Dat", "IMG", "Model",
            "Texture", "Collision", "Item Definition",
            "Item Placement", "Entry", "Settings", "Help"
        ]

        for name in menu_names:
            menu = menubar.addMenu(name)
            
            if name == "File":
                menu.addAction(QIcon.fromTheme("document-new"), "New IMG...", self.create_new_img)
                menu.addAction(QIcon.fromTheme("document-open"), "Open IMG...", self.open_img_file)
                menu.addAction(QIcon.fromTheme("document-open"), "Open COL...", self.open_col_file)
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("window-close"), "Close", self.close_img_file)
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("application-exit"), "Exit", self.close)
                
            elif name == "Edit":
                menu.addAction(QIcon.fromTheme("edit-undo"), "Undo")
                menu.addAction(QIcon.fromTheme("edit-redo"), "Redo")
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("edit-copy"), "Copy")
                menu.addAction(QIcon.fromTheme("edit-paste"), "Paste")
                
            elif name == "IMG":
                menu.addAction(QIcon.fromTheme("document-save"), "Rebuild", self.rebuild_img)
                menu.addAction(QIcon.fromTheme("document-save-as"), "Rebuild As...", self.rebuild_img_as)
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("document-merge"), "Merge IMG Files")
                menu.addAction(QIcon.fromTheme("edit-cut"), "Split IMG File")
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("dialog-information"), "IMG Properties")
                
            elif name == "Entry":
                menu.addAction(QIcon.fromTheme("go-down"), "Import Files...", self.import_files)
                menu.addAction(QIcon.fromTheme("go-up"), "Export Selected...", self.export_selected)
                menu.addAction(QIcon.fromTheme("go-up"), "Export All...", self.export_all)
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("list-remove"), "Remove Selected", self.remove_selected)
                menu.addAction(QIcon.fromTheme("edit"), "Rename Entry")
                
            elif name == "Settings":
                menu.addAction(QIcon.fromTheme("preferences-other"), "Preferences...", self.show_settings)
                menu.addAction(QIcon.fromTheme("applications-graphics"), "Themes...", self.show_theme_settings)
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("folder"), "Manage Templates...", self.manage_templates)
                
            elif name == "Help":
                menu.addAction(QIcon.fromTheme("help-contents"), "User Guide")
                menu.addAction(QIcon.fromTheme("help-about"), "About IMG Factory", self.show_about)
                
            else:
                # Add placeholder for unimplemented menus
                placeholder = QAction("(Coming Soon)", self)
                placeholder.setEnabled(False)
                menu.addAction(placeholder)
    
    def _create_status_bar(self):
        """Create the status bar with progress indicator"""
        # Use Qt's built-in statusBar() method
        status_bar = self.statusBar()
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        
        self.img_info_label = QLabel("No IMG loaded")
        status_bar.addPermanentWidget(self.img_info_label)
    
    def _apply_table_theme(self):
        """Apply theme styling to the table"""
        if hasattr(self.app_settings, 'current_settings'):
            theme_name = self.app_settings.current_settings.get('theme', 'IMG_Factory')
            
            if theme_name == "LCARS":
                self.entries_table.setStyleSheet("""
                    QTableWidget {
                        gridline-color: #ff9900;
                        background-color: #000000;
                        color: #ff9900;
                        selection-background-color: #333333;
                    }
                    QHeaderView::section {
                        background-color: #ff9900;
                        color: #000000;
                        font-weight: bold;
                    }
                """)
            else:
                self.entries_table.setStyleSheet("""
                    QTableWidget {
                        gridline-color: #dddddd;
                        background-color: #ffffff;
                        alternate-background-color: #f8f9fa;
                        selection-background-color: #e3f2fd;
                    }
                    QHeaderView::section {
                        background-color: #f1f3f4;
                        color: #212529;
                        font-weight: bold;
                        border: 1px solid #dee2e6;
                    }
                """)
    
    def _populate_sample_data(self):
        """Add sample data to demonstrate the interface"""
        sample_entries = [
            ("1", "DFF", "player.dff", "0x00001000", "45.2 KB", "GTA:SA"),
            ("2", "TXD", "player.txd", "0x0000B500", "128.4 KB", "GTA:SA"),
            ("3", "COL", "player.col", "0x00025800", "12.1 KB", "GTA:SA"),
            ("4", "DFF", "vehicle.dff", "0x00028800", "67.8 KB", "GTA:SA"),
            ("5", "TXD", "vehicle.txd", "0x00039200", "256.0 KB", "GTA:SA"),
        ]
        
        self.entries_table.setRowCount(len(sample_entries))
        
        for row, entry_data in enumerate(sample_entries):
            for col, data in enumerate(entry_data):
                item = QTableWidgetItem(str(data))
                self.entries_table.setItem(row, col, item)
        
        # Add sample log entries
        self.log_message("IMG Factory 1.5 loaded")
        self.log_message("Sample data populated for demonstration")
        self.log_message("Ready for file operations")
    
    def _connect_signals(self):
        """Connect internal signals"""
        # Connect tab change signals
        self.file_type_tabs.currentChanged.connect(self._on_tab_changed)
    
    def _restore_settings(self):
        """Restore application settings"""
        settings = QSettings()
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def _on_tab_changed(self, index):
        """Handle tab change events"""
        tab_names = ["IMG", "COL", "Both"]
        if index < len(tab_names):
            self.log_message(f"Switched to {tab_names[index]} view")
    
    def _on_entry_selection_changed(self):
        """Handle entry selection changes"""
        has_selection = len(self.entries_table.selectionModel().selectedRows()) > 0
        has_img = self.current_img is not None
        
        # Enable/disable buttons based on selection
        for btn in self.entry_buttons:
            if btn.text() in ["Export Selected", "Remove Selected"]:
                btn.setEnabled(has_selection and has_img)
    
    def _on_search_changed(self, text):
        """Handle search input changes"""
        # Implement search filtering logic here
        self.log_message(f"Searching for: {text}")
    
    def _on_filter_changed(self, filter_type):
        """Handle filter combo changes"""
        # Implement filtering logic here
        self.log_message(f"Filter changed to: {filter_type}")
    
    # File Operations
    def create_new_img(self):
        """Show new IMG creation dialog"""
        try:
            img_debugger.debug("Starting IMG creation dialog")
            dialog = NewIMGDialog(self, self.app_settings)  # Pass settings here

            # Debug the dialog
            debug_img_creation_process(dialog)

            dialog.img_created.connect(self.load_img_file)
            dialog.img_created.connect(lambda path: self.log_message(f"Created: {os.path.basename(path)}"))
            dialog.exec()

        except Exception as e:
            img_debugger.trace_exception(e)
            raise
    
    def open_img_file(self):
        """Open an IMG file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG File", "", "IMG Files (*.img);;All Files (*)"
        )
        
        if file_path:
            self._load_img_file(file_path)
    
    def open_col_file(self):
        """Open a COL file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self._load_col_file(file_path)
    
    def _load_img_file(self, file_path):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.log_message(f"Loading IMG file: {file_path}")
        self.progress_bar.setVisible(True)
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._on_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_load_error)
        self.load_thread.start()
    
    def _load_col_file(self, file_path):
        """Load COL file"""
        try:
            self.log_message(f"Loading COL file: {file_path}")
            # COL loading logic would go here
            self.current_col = file_path  # Placeholder
            self._update_ui_for_loaded_col()
            self.log_message(f"COL file loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"COL load error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load COL file: {e}")
    
    def _on_load_progress(self, progress, status):
        """Handle load progress updates"""
        self.progress_bar.setValue(progress)
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(status)
    
    def _on_img_loaded(self, img_file):
        """Handle successful IMG file loading"""
        self.current_img = img_file
        self._update_ui_for_loaded_img()
        self.progress_bar.setVisible(False)
        self.log_message(f"IMG file loaded: {len(img_file.entries)} entries")
    
    def _on_load_error(self, error_msg):
        """Handle IMG loading errors"""
        QMessageBox.critical(self, "Loading Error", error_msg)
        self.progress_bar.setVisible(False)
        self.log_message(f"Load error: {error_msg}")
    
    def _update_ui_for_loaded_img(self):
        """Update UI when IMG file is loaded"""
        if not self.current_img:
            return
        
        # Update file info
        self.file_path_label.setText(os.path.basename(self.current_img.file_path))
        self.version_label.setText(str(self.current_img.version))
        self.entry_count_label.setText(str(len(self.current_img.entries)))
        
        # Update both tab info
        self.both_img_label.setText(os.path.basename(self.current_img.file_path))
        
        # Update status bar
        self.img_info_label.setText(f"IMG: {len(self.current_img.entries)} entries")
        
        # Update entries table
        self._populate_entries_table()
        
        # Enable/disable buttons
        self._update_button_states()
    
    def _update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded"""
        if not self.current_col:
            return
        
        # Update COL info
        self.col_file_path_label.setText(os.path.basename(self.current_col))
        self.col_model_count_label.setText("Unknown")  # Would need actual COL parsing
        
        # Update both tab info
        self.both_col_label.setText(os.path.basename(self.current_col))
        
        # Update button states
        self._update_button_states()
    
    def _populate_entries_table(self):
        """Populate the entries table with IMG contents"""
        if not self.current_img:
            return
        
        self.entries_table.setRowCount(len(self.current_img.entries))
        
        for row, entry in enumerate(self.current_img.entries):
            # ID
            id_item = QTableWidgetItem(str(row + 1))
            self.entries_table.setItem(row, 0, id_item)
            
            # Type (based on extension)
            ext = os.path.splitext(entry.name)[1].upper()
            type_item = QTableWidgetItem(ext if ext else "Unknown")
            self.entries_table.setItem(row, 1, type_item)
            
            # Name
            name_item = QTableWidgetItem(entry.name)
            self.entries_table.setItem(row, 2, name_item)
            
            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:08X}")
            self.entries_table.setItem(row, 3, offset_item)
            
            # Size
            size_item = QTableWidgetItem(format_file_size(entry.size))
            self.entries_table.setItem(row, 4, size_item)
            
            # Version
            version_item = QTableWidgetItem("GTA:SA")  # Default for now
            self.entries_table.setItem(row, 5, version_item)
    
    def _update_button_states(self):
        """Update button enabled/disabled states"""
        has_img = self.current_img is not None
        has_col = self.current_col is not None
        has_selection = len(self.entries_table.selectionModel().selectedRows()) > 0
        
        # IMG buttons
        for btn in self.img_buttons:
            if btn.text() in ["Close", "Rebuild", "Rebuild As"]:
                btn.setEnabled(has_img)
        
        # Entry buttons
        for btn in self.entry_buttons:
            if btn.text() in ["Import Files", "Export All"]:
                btn.setEnabled(has_img)
            elif btn.text() in ["Export Selected", "Remove Selected"]:
                btn.setEnabled(has_img and has_selection)
        
        # COL buttons
        for btn in self.col_buttons:
            if btn.text() in ["Export COL", "Close COL"]:
                btn.setEnabled(has_col)
    
    def close_img_file(self):
        """Close the current IMG file"""
        self.current_img = None
        self._clear_img_ui()
        self.log_message("IMG file closed")
    
    def close_col_file(self):
        """Close the current COL file"""
        self.current_col = None
        self._clear_col_ui()
        self.log_message("COL file closed")
    
    def _clear_img_ui(self):
        """Clear IMG-related UI when no IMG is loaded"""
        self.file_path_label.setText("No file loaded")
        self.version_label.setText("Unknown")
        self.entry_count_label.setText("0")
        self.both_img_label.setText("No IMG file")
        self.entries_table.setRowCount(0)
        
        # Update status bar
        self.img_info_label.setText("No IMG loaded")
        
        # Update button states
        self._update_button_states()
    
    def _clear_col_ui(self):
        """Clear COL-related UI when no COL is loaded"""
        self.col_file_path_label.setText("No COL file loaded")
        self.col_model_count_label.setText("0")
        self.both_col_label.setText("No COL file")
        
        # Update button states
        self._update_button_states()
    
    def rebuild_img(self):
        """Rebuild the current IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        
        try:
            self.current_img.rebuild()
            self.log_message("IMG file rebuilt successfully")
            QMessageBox.information(self, "Success", "IMG file rebuilt successfully")
        except Exception as e:
            self.log_message(f"Rebuild error: {e}")
            QMessageBox.critical(self, "Error", f"Rebuild failed: {e}")
    
    def rebuild_img_as(self):
        """Rebuild IMG file with new name"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Rebuild IMG As", "", "IMG Files (*.img);;All Files (*)"
        )
        
        if file_path:
            try:
                self.current_img.rebuild(file_path)
                self.log_message(f"IMG file rebuilt as: {file_path}")
                QMessageBox.information(self, "Success", f"IMG file rebuilt as: {file_path}")
            except Exception as e:
                self.log_message(f"Rebuild error: {e}")
                QMessageBox.critical(self, "Error", f"Rebuild failed: {e}")
    
    def import_files(self):
        """Import files into IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "Import Files", "", "All Files (*)"
        )
        
        if files:
            try:
                for file_path in files:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    filename = os.path.basename(file_path)
                    self.current_img.add_entry(filename, data)
                
                self._update_ui_for_loaded_img()
                self.log_message(f"Imported {len(files)} files")
                QMessageBox.information(self, "Success", f"Imported {len(files)} files")
            except Exception as e:
                self.log_message(f"Import error: {e}")
                QMessageBox.critical(self, "Error", f"Import failed: {e}")
    
    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No entries selected")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Export Directory")
        if export_dir:
            try:
                for index in selected_rows:
                    row = index.row()
                    entry = self.current_img.entries[row]
                    
                    export_path = os.path.join(export_dir, entry.name)
                    with open(export_path, 'wb') as f:
                        f.write(entry.get_data())
                
                self.log_message(f"Exported {len(selected_rows)} entries")
                QMessageBox.information(self, "Success", f"Exported {len(selected_rows)} entries")
            except Exception as e:
                self.log_message(f"Export error: {e}")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Export All Entries")
        if export_dir:
            try:
                for entry in self.current_img.entries:
                    export_path = os.path.join(export_dir, entry.name)
                    with open(export_path, 'wb') as f:
                        f.write(entry.get_data())
                
                self.log_message(f"Exported all {len(self.current_img.entries)} entries")
                QMessageBox.information(self, "Success", f"Exported all {len(self.current_img.entries)} entries")
            except Exception as e:
                self.log_message(f"Export error: {e}")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def export_col(self):
        """Export COL file"""
        if not self.current_col:
            QMessageBox.warning(self, "Warning", "No COL file loaded")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            try:
                # COL export logic would go here
                self.log_message(f"COL file exported: {file_path}")
                QMessageBox.information(self, "Success", f"COL file exported: {file_path}")
            except Exception as e:
                self.log_message(f"COL export error: {e}")
                QMessageBox.critical(self, "Error", f"COL export failed: {e}")
    
    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No entries selected")
            return
        
        reply = QMessageBox.question(
            self, "Confirm", f"Remove {len(selected_rows)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove in reverse order to maintain indices
                for index in sorted(selected_rows, reverse=True):
                    del self.current_img.entries[index.row()]
                
                self._update_ui_for_loaded_img()
                self.log_message(f"Removed {len(selected_rows)} entries")
                QMessageBox.information(self, "Success", f"Removed {len(selected_rows)} entries")
            except Exception as e:
                self.log_message(f"Remove error: {e}")
                QMessageBox.critical(self, "Error", f"Remove failed: {e}")
    
    def refresh_table(self):
        """Refresh the entries table"""
        if self.current_img:
            self._populate_entries_table()
            self.log_message("Table refreshed")
        else:
            self.log_message("No IMG file to refresh")
    
    # Settings and Templates
    def show_settings(self):
        """Show application settings dialog"""
        try:
            dialog = SettingsDialog(self.app_settings, self)
            dialog.settingsChanged.connect(self._on_settings_changed)
            dialog.themeChanged.connect(self._on_theme_changed)
            dialog.exec()
        except Exception as e:
            self.log_message(f"Settings dialog error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open settings: {e}")
    
    def show_theme_settings(self):
        """Show theme settings specifically"""
        try:
            dialog = SettingsDialog(self.app_settings, self)
            dialog.tabs.setCurrentIndex(0)  # Switch to themes tab
            dialog.settingsChanged.connect(self._on_settings_changed)
            dialog.themeChanged.connect(self._on_theme_changed)
            dialog.exec()
        except Exception as e:
            self.log_message(f"Theme settings error: {e}")
    
    def manage_templates(self):
        """Show template manager dialog"""
        try:
            dialog = TemplateManagerDialog(self.template_manager, self)
            dialog.exec()
        except Exception as e:
            self.log_message(f"Template manager error: {e}")
    
    def _on_settings_changed(self):
        """Handle settings changes"""
        self.log_message("Settings updated")
        # Apply new settings
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)
            self._apply_table_theme()
    
    def _on_theme_changed(self, theme_name):
        """Handle theme changes"""
        self.log_message(f"Theme changed to: {theme_name}")
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)
            self._apply_table_theme()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>IMG Factory 1.5</h2>
        <p><b>X-Seti - June 25, 2025</b></p>
        <p>Professional IMG archive management tool for GTA modding</p>
        <p>Credit: MexUK 2007 IMG Factory 1.2</p>
        <p>Enhanced with modern Qt6 interface and advanced features</p>
        <hr>
        <p>Features:</p>
        <ul>
        <li>IMG archive creation and management</li>
        <li>COL file support</li>
        <li>Multiple themes including LCARS</li>
        <li>Template system</li>
        <li>Advanced filtering and search</li>
        </ul>
        """
        QMessageBox.about(self, "About IMG Factory", about_text)
    
    # Utility methods
    def log_message(self, message):
        """Add message to log"""
        timestamp = self._get_timestamp()
        formatted_message = f"[{timestamp}] {message}"
        self.log.append(formatted_message)
        
        # Also update status bar temporarily (use Qt's statusBar() method)
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(message, 3000)  # Show for 3 seconds
    
    def _get_timestamp(self):
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def closeEvent(self, event):
        """Handle application close"""
        # Save settings
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        
        # Close any running threads
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.quit()
            self.load_thread.wait()
        
        self.log_message("IMG Factory closing")
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    app.setOrganizationName("X-Seti")
    
    # Load settings
    try:
        settings = AppSettings()
        apply_theme_to_app(app, settings)
        print(f"✓ Settings loaded successfully - Theme: {settings.current_settings.get('theme', 'Unknown')}")
    except Exception as e:
        print(f"Failed to load AppSettings: {e}")
        # Create minimal settings dict as fallback
        settings = {
            'use_advanced_ui': True,
            'theme': 'IMG_Factory'
        }
    
    # Create main window
    window = IMGFactory(settings)
    window.show()
    
    # Apply any additional themes

    return app.exec()


if __name__ == "__main__":
    main()
