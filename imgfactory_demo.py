#this belongs in root /Imgfactory_Demo.py
# $vers" X-Seti - June25,2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

import sys
import os
import mimetypes
print("Starting IMG Factory 1.5...")

# Cache cleanup and conflict resolution
try:
    from img_cache_manager import auto_cleanup
    cache_mgr = auto_cleanup()
    print("✅ Cache cleanup completed")
except ImportError:
    print("⚠️  Cache manager not available, continuing without cleanup")
except Exception as e:
    print(f"⚠️  Cache cleanup failed: {e}, continuing...")

from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QProgressBar, QLabel, QPushButton, QFileDialog,
    QMessageBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenuBar, QMenu, QStatusBar, QSizePolicy, QInputDialog,
    QFrame, QButtonGroup, QRadioButton, QSpacerItem, QLineEdit, QTabWidget
)

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont, QDragEnterEvent, QDropEvent, QPalette, QColor

# Application settings with error handling
try:
    from App_settings_system import AppSettings, apply_theme_to_app
    print("✅ App Settings imported successfully")
except ImportError as e:
    print(f"⚠️  App Settings not available: {e}")
    class AppSettings:
        def __init__(self):
            self.current_settings = {"theme": "professional"}
    def apply_theme_to_app(app, settings):
        pass

# Core classes with priority handling
try:
    from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
    print("✅ Core Classes imported successfully")
except ImportError as e:
    print(f"⚠️  Core Classes import failed: {e}")
    # Create minimal dummy classes
    class IMGFile:
        def __init__(self, path=""):
            self.file_path = path
            self.entries = []
            self.version = None
        def open(self): return False
        def close(self): pass
    
    class IMGEntry:
        def __init__(self):
            self.name = ""
            self.size = 0
            self.offset = 0
        def get_type(self): return "Unknown"
    
    class IMGVersion:
        IMG_1 = 1
        IMG_2 = 2
        IMG_3 = 3
    
    def format_file_size(size): return f"{size} bytes"

# Creator classes with conflict resolution
try:
    from components.img_creator import NewIMGDialog, GameType, add_new_img_functionality
    print("✅ IMG Creator imported successfully")
except ImportError as e:
    print(f"⚠️  IMG Creator import failed: {e}")
    class NewIMGDialog:
        def __init__(self, parent=None): pass
        def exec(self): return 0
        def get_creation_settings(self): return {}
    
    class GameType:
        @classmethod
        def get_all_types(cls): return []
    
    def add_new_img_functionality(window): pass


class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [GUI Demo]")
        self.setGeometry(100, 100, 1200, 800)
        self.app_settings = app_settings

        # Initialize attributes
        self.current_img = None
        self.current_col = None
        self.load_thread = None
        
        # Data storage for different file types
        self.img_entries = []
        self.col_entries = []
        self.combined_entries = []

        # Apply professional styling
        self._setup_styling()
        
        self._create_menu()
        self._create_status_bar()

        # Create main interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self._create_enhanced_ui(main_layout)

        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Load sample data for demo
        self._populate_sample_data()

    def _setup_styling(self):
        """Setup modern professional styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #ddd;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 6px;
                gridline-color: #e0e0e0;
                selection-background-color: #2196f3;
                alternate-background-color: #f9f9f9;
            }
            
            QTableWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            
            QTableWidget QHeaderView::section {
                background-color: #f1f3f4;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                padding: 8px;
                font-weight: bold;
                color: #555;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin: 8px 0px;
                padding-top: 10px;
                background-color: #fafafa;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                background-color: #fafafa;
                color: #1976d2;
            }
            
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                min-height: 14px;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #2196f3;
            }
            
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            
            QPushButton[action-type="import"] {
                background-color: #e3f2fd;
                border-color: #2196f3;
                color: #1976d2;
            }
            
            QPushButton[action-type="export"] {
                background-color: #e8f5e8;
                border-color: #4caf50;
                color: #2e7d32;
            }
            
            QPushButton[action-type="remove"] {
                background-color: #ffebee;
                border-color: #f44336;
                color: #c62828;
            }
            
            QPushButton[action-type="update"] {
                background-color: #fff3e0;
                border-color: #ff9800;
                color: #ef6c00;
            }
            
            QPushButton[action-type="convert"] {
                background-color: #f3e5f5;
                border-color: #9c27b0;
                color: #7b1fa2;
            }
            
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
            
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }
            
            QComboBox:hover {
                border-color: #2196f3;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
            }
            
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f0f0f0;
                text-align: center;
            }
            
            QTabWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 0px;
                padding: 0px;
            }
            
            QTabWidget::tab-bar {
                left: 5px;
            }
            
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-bottom: none;
                border-radius: 4px 4px 0px 0px;
                padding: 6px 12px;
                margin-right: 2px;
                min-width: 60px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-color: #2196f3;
                color: #2196f3;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background-color: #2196f3;
                border-radius: 3px;
            }
        """)

    def _create_enhanced_ui(self, main_layout):
        """Create enhanced UI layout similar to original but modern"""
        
        # Left side - File info and table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # File info header
        self._create_file_info_header(left_layout)
        
        # Main table
        self._create_main_table(left_layout)
        
        # Log output at bottom
        self._create_log_section(left_layout)
        
        # Right side - Control panels (like original)
        right_panel = self._create_right_control_panel()
        
        # Add to main layout with splitter for resizable panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_panel)
        self.main_splitter.setSizes([800, 400])  # 2:1 ratio like original
        
        # Make splitter handle more visible
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ddd;
                width: 4px;
                margin: 2px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #2196f3;
            }
        """)
        
        main_layout.addWidget(self.main_splitter)

    def _create_file_info_header(self, layout):
        """Create file information header"""
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_frame.setMaximumHeight(60)
        
        info_layout = QHBoxLayout(info_frame)
        
        # File info labels
        self.file_label = QLabel("File: No file loaded")
        self.file_label.setStyleSheet("font-weight: bold; color: #333;")
        
        self.version_label = QLabel("Version: N/A")
        self.version_label.setStyleSheet("color: #666;")
        
        self.entries_label = QLabel("Entries: 0")
        self.entries_label.setStyleSheet("color: #666;")
        
        # Add to layout
        info_layout.addWidget(self.file_label)
        info_layout.addStretch()
        info_layout.addWidget(self.version_label)
        info_layout.addWidget(QLabel("|"))
        info_layout.addWidget(self.entries_label)
        
        layout.addWidget(info_frame)

    def _create_main_table(self, layout):
        """Create main file table with tabs"""
        # Create vertical splitter for table and log
        self.table_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create tab widget for different file types
        self.file_tabs = QTabWidget()
        
        # IMG Tab
        self.img_table = self._create_table_widget()
        self.file_tabs.addTab(self.img_table, "📁 IMG")
        
        # COL Tab  
        self.col_table = self._create_table_widget()
        self.file_tabs.addTab(self.col_table, "🏗️ COL")
        
        # Combined Tab
        self.combined_table = self._create_table_widget()
        self.file_tabs.addTab(self.combined_table, "🔗 Both")
        
        # Set the current active table (for compatibility)
        self.table = self.img_table
        
        # Connect tab change signal
        self.file_tabs.currentChanged.connect(self._on_tab_changed)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Add tabs and progress to splitter
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addWidget(self.file_tabs)
        table_layout.addWidget(self.progress_bar)
        
        self.table_splitter.addWidget(table_container)
        
        # We'll add the log section to this splitter later
        layout.addWidget(self.table_splitter)
    
    def _create_table_widget(self):
        """Create a table widget with standard configuration"""
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Offset", "Size", "Version"])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        
        # Configure column sizing
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Version
        
        return table
    
    def _on_tab_changed(self, index):
        """Handle tab change"""
        # Update the active table reference
        if index == 0:  # IMG tab
            self.table = self.img_table
            self.log_message("Switched to IMG view")
        elif index == 1:  # COL tab
            self.table = self.col_table
            self.log_message("Switched to COL view")
        elif index == 2:  # Combined tab
            self.table = self.combined_table
            self.log_message("Switched to Combined view")
        
        # Update status
        self._update_status_for_current_tab()

    def _create_log_section(self, layout):
        """Create log output section"""
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        
        self.log = QTextEdit()
        self.log.setMinimumHeight(80)
        self.log.setMaximumHeight(200)
        self.log.setReadOnly(True)
        
        log_layout.addWidget(self.log)
        
        # Add log to the table splitter instead of main layout
        self.table_splitter.addWidget(log_group)
        self.table_splitter.setSizes([500, 150])  # Table gets more space than log
        
        # Style the vertical splitter
        self.table_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ddd;
                height: 4px;
                margin: 2px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #2196f3;
            }
        """)

    def _create_right_control_panel(self):
        """Create right control panel similar to original IMG Factory"""
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # IMG Operations (like original top section)
        img_group = QGroupBox("IMG")
        img_layout = QVBoxLayout(img_group)
        
        # Row 1
        row1 = QHBoxLayout()
        open_btn = self._create_styled_button("Open", "import")
        open_btn.clicked.connect(self.open_img_file)
        open_col_btn = self._create_styled_button("Open COL", "import")
        open_col_btn.clicked.connect(self.open_col_file)
        close_btn = self._create_styled_button("Close", "remove")
        close_btn.clicked.connect(self.close_file)
        row1.addWidget(open_btn)
        row1.addWidget(open_col_btn)
        row1.addWidget(close_btn)
        
        # Row 2
        row2 = QHBoxLayout()
        rebuild_btn = self._create_styled_button("Rebuild", "update")
        rebuild_btn.clicked.connect(self.rebuild_img)
        rebuild_as_btn = self._create_styled_button("Rebuild As", "update")
        rebuild_as_btn.clicked.connect(self.rebuild_img_as)
        row2.addWidget(rebuild_btn)
        row2.addWidget(rebuild_as_btn)
        
        # Row 3
        row3 = QHBoxLayout()
        merge_btn = self._create_styled_button("Merge", "convert")
        split_btn = self._create_styled_button("Split", "convert")
        convert_btn = self._create_styled_button("Convert", "convert")
        row3.addWidget(merge_btn)
        row3.addWidget(split_btn)
        row3.addWidget(convert_btn)
        
        img_layout.addLayout(row1)
        img_layout.addLayout(row2)
        img_layout.addLayout(row3)
        
        # Entries Operations
        entries_group = QGroupBox("Entries")
        entries_layout = QVBoxLayout(entries_group)
        
        # Import/Export row
        ie_row = QHBoxLayout()
        import_btn = self._create_styled_button("Import", "import")
        import_btn.clicked.connect(self.import_files)
        import_via_btn = self._create_styled_button("Import via", "import")
        update_list_btn = self._create_styled_button("Update list", "update")
        ie_row.addWidget(import_btn)
        ie_row.addWidget(import_via_btn)
        ie_row.addWidget(update_list_btn)
        
        # Export row
        export_row = QHBoxLayout()
        export_btn = self._create_styled_button("Export", "export")
        export_btn.clicked.connect(self.export_selected)
        export_via_btn = self._create_styled_button("Export via", "export")
        quick_export_btn = self._create_styled_button("Quick Export", "export")
        export_row.addWidget(export_btn)
        export_row.addWidget(export_via_btn)
        export_row.addWidget(quick_export_btn)
        
        # Remove/Replace row
        rr_row = QHBoxLayout()
        remove_btn = self._create_styled_button("Remove", "remove")
        remove_btn.clicked.connect(self.remove_selected)
        remove_via_btn = self._create_styled_button("Remove via", "remove")
        dump_btn = self._create_styled_button("Dump", "update")
        rr_row.addWidget(remove_btn)
        rr_row.addWidget(remove_via_btn)
        rr_row.addWidget(dump_btn)
        
        # Rename/Replace row
        rename_row = QHBoxLayout()
        rename_btn = self._create_styled_button("Rename", "convert")
        replace_btn = self._create_styled_button("Replace", "update")
        rename_row.addWidget(rename_btn)
        rename_row.addWidget(replace_btn)
        
        entries_layout.addLayout(ie_row)
        entries_layout.addLayout(export_row)
        entries_layout.addLayout(rr_row)
        entries_layout.addLayout(rename_row)
        
        # Selection tools
        select_row = QHBoxLayout()
        select_all_btn = self._create_styled_button("Select All", "convert")
        select_all_btn.clicked.connect(self.select_all_entries)
        select_inv_btn = self._create_styled_button("Select Inverse", "convert")
        sort_btn = self._create_styled_button("Sort", "convert")
        select_row.addWidget(select_all_btn)
        select_row.addWidget(select_inv_btn)
        select_row.addWidget(sort_btn)
        
        entries_layout.addLayout(select_row)
        
        # Filter & Search section
        filter_group = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout(filter_group)
        
        # Filter dropdowns
        filter_row1 = QHBoxLayout()
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "DFF", "TXD", "COL", "WAV", "SCM"])
        self.version_filter = QComboBox()
        self.version_filter.addItems(["All Versions", "GTA III", "GTA VC", "GTA SA", "GTA IV"])
        filter_row1.addWidget(self.type_filter)
        filter_row1.addWidget(self.version_filter)
        
        # Search
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        find_btn = self._create_styled_button("Find", "convert")
        find_btn.clicked.connect(self.search_entries)
        search_row.addWidget(self.search_input)
        search_row.addWidget(find_btn)
        
        # Match options
        options_row = QHBoxLayout()
        self.hit_tabs_check = QCheckBox("Hit Tabs")
        options_row.addWidget(self.hit_tabs_check)
        options_row.addStretch()
        
        filter_layout.addLayout(filter_row1)
        filter_layout.addLayout(search_row)
        filter_layout.addLayout(options_row)
        
        # Info panel
        info_group = QGroupBox("Info")
        info_layout = QVBoxLayout(info_group)
        
        info_table = QTableWidget(0, 3)
        info_table.setHorizontalHeaderLabels(["Name", "IMG File", "RW Ver"])
        info_table.setMaximumHeight(100)
        info_layout.addWidget(info_table)
        
        # Add all groups to right panel
        right_layout.addWidget(img_group)
        right_layout.addWidget(entries_group)
        right_layout.addWidget(filter_group)
        right_layout.addWidget(info_group)
        right_layout.addStretch()
        
        return right_widget

    def _create_styled_button(self, text, action_type=None):
        """Create a styled button with action type"""
        btn = QPushButton(text)
        if action_type:
            btn.setProperty("action-type", action_type)
        btn.setMaximumHeight(28)
        btn.setMinimumWidth(80)
        return btn

    def _create_menu(self):
        """Create application menu bar matching original"""
        menubar = self.menuBar()
        
        # Replicate original menu structure
        menu_structure = {
            "File": ["New IMG", "Open", "Close", "-", "Exit"],
            "Edit": ["Undo", "Redo", "-", "Cut", "Copy", "Paste"],
            "Dat": ["Load DAT", "Save DAT"],
            "IMG": ["Rebuild", "Rebuild As", "Merge", "Split", "Convert"],
            "Model": ["View", "Extract", "Replace"],
            "Texture": ["View", "Extract", "Replace"],
            "Collision": ["View", "Extract"],
            "Item Definition": ["View", "Edit"],
            "Item Placement": ["View", "Edit"],
            "Entry": ["Import", "Export", "Remove", "Rename"],
            "Settings": ["Preferences", "Templates"],
            "Help": ["About", "Help Topics"]
        }
        
        for menu_name, items in menu_structure.items():
            menu = menubar.addMenu(menu_name)
            
            for item in items:
                if item == "-":
                    menu.addSeparator()
                else:
                    action = QAction(item, self)
                    
                    # Connect key actions
                    if item == "Open":
                        action.setShortcut("Ctrl+O")
                        action.triggered.connect(self.open_img_file)
                    elif item == "Exit":
                        action.triggered.connect(self.close)
                    elif item == "New IMG":
                        action.setShortcut("Ctrl+N")
                        action.triggered.connect(self.create_new_img)
                    elif item == "About":
                        action.triggered.connect(self.show_about)
                    
                    menu.addAction(action)

    def _create_status_bar(self):
        """Create status bar"""
        status = QStatusBar()
        
        # Add status sections like original
        self.entries_status = QLabel("Entries: 0")
        self.selected_status = QLabel("Selected: 0")
        self.img_status = QLabel("IMG: (no tabs open)")
        
        status.addWidget(self.entries_status)
        status.addPermanentWidget(self.selected_status)
        status.addPermanentWidget(self.img_status)
        
        status.showMessage("Ready")
        self.setStatusBar(status)

    def _populate_sample_data(self):
        """Add sample data to demonstrate the interface"""
        # Sample IMG data
        img_data = [
            (1, "DFF", "player.dff", "0x1000", "245 KB", "GTA SA"),
            (2, "TXD", "player.txd", "0x2000", "1.2 MB", "GTA SA"),
            (3, "DFF", "vehicle.dff", "0x4000", "512 KB", "GTA SA"),
            (4, "TXD", "vehicle.txd", "0x5000", "2.1 MB", "GTA SA"),
        ]
        
        # Sample COL data
        col_data = [
            (1, "COL", "player.col", "0x3000", "45 KB", "GTA SA"),
            (2, "COL", "vehicle.col", "0x6000", "78 KB", "GTA SA"),
            (3, "COL", "building.col", "0x7000", "234 KB", "GTA SA"),
            (4, "COL", "weapon.col", "0x8000", "12 KB", "GTA SA"),
        ]
        
        # Combined data
        combined_data = img_data + col_data
        combined_data.sort(key=lambda x: x[2])  # Sort by name
        
        # Populate IMG table
        self._populate_table(self.img_table, img_data)
        
        # Populate COL table
        self._populate_table(self.col_table, col_data)
        
        # Populate Combined table
        self._populate_table(self.combined_table, combined_data)
        
        # Store data
        self.img_entries = img_data
        self.col_entries = col_data
        self.combined_entries = combined_data
        
        # Update status
        self._update_status_for_current_tab()
    
    def _populate_table(self, table, data):
        """Populate a specific table with data"""
        table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # Color-code by type
                if col == 1:  # Type column
                    if value == "DFF":
                        item.setBackground(QColor("#e3f2fd"))
                    elif value == "TXD":
                        item.setBackground(QColor("#e8f5e8"))
                    elif value == "COL":
                        item.setBackground(QColor("#fff3e0"))
                
                table.setItem(row, col, item)
    
    def _update_status_for_current_tab(self):
        """Update status based on current tab"""
        current_index = self.file_tabs.currentIndex()
        
        if current_index == 0:  # IMG tab
            count = len(self.img_entries)
            self.entries_status.setText(f"IMG Entries: {count}")
            self.entries_label.setText(f"Entries: {count}")
            self.img_status.setText("IMG: Sample IMG loaded")
        elif current_index == 1:  # COL tab
            count = len(self.col_entries)
            self.entries_status.setText(f"COL Entries: {count}")
            self.entries_label.setText(f"Entries: {count}")
            self.img_status.setText("COL: Sample COL loaded")
        elif current_index == 2:  # Combined tab
            count = len(self.combined_entries)
            self.entries_status.setText(f"Combined Entries: {count}")
            self.entries_label.setText(f"Entries: {count}")
            self.img_status.setText("Both: IMG + COL loaded")

    # File operations
    def open_img_file(self):
        """Open IMG file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG File", "", 
            "IMG Files (*.img);;All Files (*)"
        )
        if file_path:
            self.log_message(f"Loading IMG file: {file_path}")
            # Switch to IMG tab
            self.file_tabs.setCurrentIndex(0)
            # TODO: Implement actual IMG loading
    
    def open_col_file(self):
        """Open COL file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", 
            "COL Files (*.col);;All Files (*)"
        )
        if file_path:
            self.log_message(f"Loading COL file: {file_path}")
            # Switch to COL tab
            self.file_tabs.setCurrentIndex(1)
            # TODO: Implement actual COL loading

    def close_file(self):
        """Close current file based on active tab"""
        current_index = self.file_tabs.currentIndex()
        
        if current_index == 0:  # IMG tab
            self.log_message("Closed IMG file")
            self.img_table.setRowCount(0)
            self.img_entries = []
        elif current_index == 1:  # COL tab
            self.log_message("Closed COL file")
            self.col_table.setRowCount(0)
            self.col_entries = []
        elif current_index == 2:  # Combined tab
            self.log_message("Closed all files")
            self.combined_table.setRowCount(0)
            self.img_table.setRowCount(0)
            self.col_table.setRowCount(0)
            self.img_entries = []
            self.col_entries = []
            self.combined_entries = []
        
        self._update_status_for_current_tab()

    def close_img_file(self):
        """Legacy method - redirects to close_file"""
        self.close_file()

    def create_new_img(self):
        self.log_message("New IMG creation requested")

    def rebuild_img(self):
        self.log_message("Rebuild IMG requested")

    def rebuild_img_as(self):
        self.log_message("Rebuild IMG As requested")

    def import_files(self):
        self.log_message("Import files requested")

    def export_selected(self):
        self.log_message("Export selected requested")

    def remove_selected(self):
        self.log_message("Remove selected requested")

    def select_all_entries(self):
        self.table.selectAll()
        selected = self.table.rowCount()
        self.selected_status.setText(f"Selected: {selected}")
        self.log_message(f"Selected all {selected} entries")

    def search_entries(self):
        search_text = self.search_input.text()
        if search_text:
            self.log_message(f"Searching for: {search_text}")

    def show_about(self):
        QMessageBox.about(self, "About IMG Factory 1.5",
                         "IMG Factory 1.5\n\nA modern tool for managing GTA IMG archive files.\n\nOriginal by MexUK (2007)\nEnhanced by X-Seti (2025)")

    def log_message(self, message):
        """Add message to log output"""
        self.log.append(f"[INFO] {message}")
        self.log.ensureCursorVisible()

    def log_error(self, message):
        """Add error message to log output"""
        self.log.append(f"[ERROR] {message}")
        self.log.ensureCursorVisible()

    # Drag and drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.img'):
                    self.log_message(f"Dropped IMG file: {file_path}")
                    break

def cleanup_on_exit():
    """Cleanup function called on application exit"""
    try:
        print("🧹 Cleaning up on exit...")
        import gc
        collected = gc.collect()
        print(f"  ✓ Collected {collected} objects")
    except Exception as e:
        print(f"⚠️  Exit cleanup error: {e}")

def main():
    """Main application entry point with cleanup integration"""
    try:
        app = QApplication(sys.argv)
        
        # Register cleanup function
        import atexit
        atexit.register(cleanup_on_exit)
        
        # Initialize settings
        settings = AppSettings()

        # Apply theme
        apply_theme_to_app(app, settings)

        # Create window
        print("🏗️  Creating main window...")
        window = ImgFactoryDemo(settings)

        # Show window
        window.show()
        
        print("🎮 IMG Factory 1.5 started successfully!")
        return app.exec()
        
    except Exception as e:
        print(f"💥 Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
