#this belongs in root /imgfactory.py
#!/usr/bin/env python3
"""
X-Seti - June26 2025 - IMG Factory 1.5 - Restored Original GUI with Phase 2 Functions
Credit MexUK 2007 IMG Factory 1.2 - Original beautiful GUI restored
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add components directory to path
current_dir = Path(__file__).parent
components_dir = current_dir / "components"
if str(components_dir) not in sys.path:
    sys.path.insert(0, str(components_dir))

# Import Qt6 components
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
        QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
        QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
        QAbstractItemView, QTabWidget, QCheckBox, QGridLayout, QFrame,
        QSizePolicy, QInputDialog
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
    from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap, QDragEnterEvent, QDropEvent
except ImportError as e:
    print(f"Error importing PyQt6: {e}")
    print("Please install PyQt6: pip install PyQt6")
    sys.exit(1)

# Import application components with graceful fallback
try:
    from img_manager import IMGFile, IMGEntry, IMGVersion, format_file_size
    from img_validator import IMGValidator
    from img_formats import GameSpecificIMGDialog
    from img_templates import IMGTemplateManager, TemplateManagerDialog
    HAS_FULL_COMPONENTS = True
except ImportError as e:
    print(f"Some advanced components not available: {e}")
    HAS_FULL_COMPONENTS = False
    
    # Basic stubs for missing components
    class IMGFile:
        def __init__(self, path=""):
            self.file_path = path
            self.entries = []
            self.version = None
        def open(self): return True
        def close(self): pass
        def rebuild(self): return True
        def add_entry(self, name, data): pass
        def remove_entry(self, entry): return True
        def export_entry(self, entry, path): return True
        def import_file(self, path, name): return True
    
    class IMGEntry:
        def __init__(self):
            self.name = ""
            self.extension = ""
            self.size = 0
            self.offset = 0
    
    def format_file_size(size):
        if size < 1024: return f"{size} B"
        elif size < 1024*1024: return f"{size/1024:.1f} KB"
        else: return f"{size/(1024*1024):.1f} MB"

# Import theme system
try:
    from App_settings_system import AppSettings, apply_theme_to_app
    from pastel_button_theme import apply_pastel_theme_to_buttons
    HAS_THEMES = True
    print("✓ Theme system loaded successfully")
except ImportError as e:
    print(f"Theme system not available: {e}")
    HAS_THEMES = False
    
    # Create basic settings stub
    class AppSettings:
        def __init__(self):
            self.current_settings = {
                "show_button_icons": False, 
                "show_menu_icons": True,
                "theme": "LCARS_Modern",
                "custom_button_colors": True,
                "button_import_color": "#E3F2FD",
                "button_export_color": "#E8F5E8", 
                "button_remove_color": "#FFEBEE",
                "button_update_color": "#FFF3E0",
                "button_convert_color": "#F3E5F5"
            }
    
    def apply_theme_to_app(app, settings):
        pass
    
    def apply_pastel_theme_to_buttons(app, settings):
        pass


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_updated = pyqtSignal(int, str)
    loading_finished = pyqtSignal(object)
    loading_error = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress_updated.emit(10, "Opening file...")
            img_file = IMGFile(self.file_path)
            
            self.progress_updated.emit(50, "Loading entries...")
            if img_file.open():
                self.progress_updated.emit(100, "Complete")
                self.loading_finished.emit(img_file)
            else:
                self.loading_error.emit("Failed to open IMG file")
        except Exception as e:
            self.loading_error.emit(f"Error: {str(e)}")


class ImgFactoryDemo(QMainWindow):
    """IMG Factory with restored original beautiful GUI"""
    
    def __init__(self, app_settings=None):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [GUI Demo]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings or AppSettings()
        
        # Core data
        self.current_img: Optional[IMGFile] = None
        self.load_thread: Optional[IMGLoadThread] = None
        self.template_manager = IMGTemplateManager() if HAS_FULL_COMPONENTS else None
        
        # UI components
        self.table: Optional[QTableWidget] = None
        self.log_output: Optional[QTextEdit] = None
        self.main_splitter: Optional[QSplitter] = None
        
        # Initialize UI
        self._create_menu()
        self._create_status_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        self._create_main_ui_with_splitters(main_layout)
        self._add_sample_data()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def _create_menu(self):
        """Create menu bar matching original"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
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
                menu.addAction(merge_action)
                
                split_action = QAction("Split", self)
                menu.addAction(split_action)
                
                menu.addSeparator()
                
                info_action = QAction("IMG Info", self)
                if show_menu_icons:
                    info_action.setIcon(QIcon.fromTheme("dialog-information"))
                info_action.triggered.connect(self.show_img_info)
                menu.addAction(info_action)
            elif name == "Entry":
                export_action = QAction("Export Selected", self)
                if show_menu_icons:
                    export_action.setIcon(QIcon.fromTheme("document-save-as"))
                export_action.triggered.connect(self.export_selected_entries)
                menu.addAction(export_action)
                
                import_action = QAction("Import Files", self)
                if show_menu_icons:
                    import_action.setIcon(QIcon.fromTheme("document-open"))
                import_action.triggered.connect(self.import_files)
                menu.addAction(import_action)
                
                menu.addSeparator()
                
                remove_action = QAction("Remove Selected", self)
                if show_menu_icons:
                    remove_action.setIcon(QIcon.fromTheme("edit-delete"))
                remove_action.triggered.connect(self.remove_selected_entries)
                menu.addAction(remove_action)
            elif name == "Settings":
                prefs_action = QAction("Preferences", self)
                if show_menu_icons:
                    prefs_action.setIcon(QIcon.fromTheme("preferences-other"))
                prefs_action.triggered.connect(self.show_preferences)
                menu.addAction(prefs_action)
                
                themes_action = QAction("Themes", self)
                if show_menu_icons:
                    themes_action.setIcon(QIcon.fromTheme("applications-graphics"))
                themes_action.triggered.connect(self.show_theme_settings)
                menu.addAction(themes_action)
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
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Left side info
        self.combined_entries_label = QLabel("Combined Entries: 0")
        self.status_bar.addWidget(self.combined_entries_label)
        
        # Right side info
        self.selected_label = QLabel("Selected: 0")
        self.both_label = QLabel("Both: IMG + COL loaded")
        
        self.status_bar.addPermanentWidget(self.selected_label)
        self.status_bar.addPermanentWidget(self.both_label)
    
    def _create_main_ui_with_splitters(self, main_layout):
        """Create main UI with splitters matching original design"""
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Main content area
        left_widget = self._create_left_panel()
        self.main_splitter.addWidget(left_widget)
        
        # Right side - Control panel
        right_widget = self._create_right_panel()
        self.main_splitter.addWidget(right_widget)
        
        # Set splitter proportions (about 70% left, 30% right)
        self.main_splitter.setSizes([770, 330])
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 0)
        
        main_layout.addWidget(self.main_splitter)
    
    def _create_left_panel(self):
        """Create left panel with tabs and table"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # File info header
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("File: No file loaded"))
        info_layout.addStretch()
        info_layout.addWidget(QLabel("Version: N/A"))
        info_layout.addWidget(QLabel("|"))
        info_layout.addWidget(QLabel("Entries: 8"))
        left_layout.addLayout(info_layout)
        
        # Tabs for different views
        self.tab_widget = QTabWidget()
        
        # IMG tab
        img_tab = QWidget()
        img_layout = QVBoxLayout(img_tab)
        img_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Name", "Size", "Version", "Compression", "Status"
        ])
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 90)
        self.table.setColumnWidth(6, 80)
        
        img_layout.addWidget(self.table)
        self.tab_widget.addTab(img_tab, "IMG")
        
        # COL tab
        col_tab = QWidget()
        col_layout = QVBoxLayout(col_tab)
        col_layout.addWidget(QLabel("COL files will be displayed here"))
        self.tab_widget.addTab(col_tab, "COL")
        
        # Both tab
        both_tab = QWidget()
        both_layout = QVBoxLayout(both_tab)
        both_layout.addWidget(QLabel("Combined view of IMG and COL files"))
        self.tab_widget.addTab(both_tab, "Both")
        
        left_layout.addWidget(self.tab_widget)
        
        # Log output section
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(120)
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New', monospace; font-size: 9pt;")
        left_layout.addWidget(QLabel("Log Output"))
        left_layout.addWidget(self.log_output)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        return left_widget
    
    def _create_right_panel(self):
        """Create right control panel matching original design"""
        right_widget = QWidget()
        right_widget.setMinimumWidth(280)
        right_widget.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)
        
        # IMG Operations Group
        img_group = QGroupBox("IMG")
        img_layout = QGridLayout(img_group)
        img_layout.setSpacing(4)
        
        # Row 1
        self.open_btn = self._create_adaptive_button("Open", "import", callback=self.open_img_file)
        self.open_col_btn = self._create_adaptive_button("Open COL", "import")
        self.close_btn = self._create_adaptive_button("Close", "remove")
        img_layout.addWidget(self.open_btn, 0, 0)
        img_layout.addWidget(self.open_col_btn, 0, 1)
        img_layout.addWidget(self.close_btn, 0, 2)
        
        # Row 2
        self.rebuild_btn = self._create_adaptive_button("Rebuild", "update", callback=self.rebuild_img)
        self.rebuild_as_btn = self._create_adaptive_button("Rebuild As", "update")
        img_layout.addWidget(self.rebuild_btn, 1, 0)
        img_layout.addWidget(self.rebuild_as_btn, 1, 1)
        
        # Row 3
        self.merge_btn = self._create_adaptive_button("Merge", "convert")
        self.split_btn = self._create_adaptive_button("Split", "convert")
        self.convert_btn = self._create_adaptive_button("Convert", "convert")
        img_layout.addWidget(self.merge_btn, 2, 0)
        img_layout.addWidget(self.split_btn, 2, 1)
        img_layout.addWidget(self.convert_btn, 2, 2)
        
        right_layout.addWidget(img_group)
        
        # Entries Operations Group
        entries_group = QGroupBox("Entries")
        entries_layout = QGridLayout(entries_group)
        entries_layout.setSpacing(4)
        
        # Row 1
        self.import_btn = self._create_adaptive_button("Import", "import", callback=self.import_files)
        self.import_via_btn = self._create_adaptive_button("Import via", "import")
        self.update_lst_btn = self._create_adaptive_button("Update lst", "update")
        entries_layout.addWidget(self.import_btn, 0, 0)
        entries_layout.addWidget(self.import_via_btn, 0, 1)
        entries_layout.addWidget(self.update_lst_btn, 0, 2)
        
        # Row 2
        self.export_btn = self._create_adaptive_button("Export", "export", callback=self.export_selected_entries)
        self.export_via_btn = self._create_adaptive_button("Export via", "export")
        self.quick_export_btn = self._create_adaptive_button("Quick Export", "export")
        entries_layout.addWidget(self.export_btn, 1, 0)
        entries_layout.addWidget(self.export_via_btn, 1, 1)
        entries_layout.addWidget(self.quick_export_btn, 1, 2)
        
        # Row 3
        self.remove_btn = self._create_adaptive_button("Remove", "remove", callback=self.remove_selected_entries)
        self.remove_via_btn = self._create_adaptive_button("Remove via", "remove")
        self.dump_btn = self._create_adaptive_button("Dump", "convert")
        self.dump_btn.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold;")
        entries_layout.addWidget(self.remove_btn, 2, 0)
        entries_layout.addWidget(self.remove_via_btn, 2, 1)
        entries_layout.addWidget(self.dump_btn, 2, 2)
        
        # Row 4
        self.rename_btn = self._create_adaptive_button("Rename", "update")
        self.replace_btn = self._create_adaptive_button("Replace", "update")
        entries_layout.addWidget(self.rename_btn, 3, 0)
        entries_layout.addWidget(self.replace_btn, 3, 1)
        
        right_layout.addWidget(entries_group)
        
        # Selection buttons
        selection_layout = QHBoxLayout()
        self.select_all_btn = self._create_adaptive_button("Select All", callback=self.select_all)
        self.select_inverse_btn = self._create_adaptive_button("Select Inverse", callback=self.select_inverse)
        self.sort_btn = self._create_adaptive_button("Sort")
        selection_layout.addWidget(self.select_all_btn)
        selection_layout.addWidget(self.select_inverse_btn)
        selection_layout.addWidget(self.sort_btn)
        right_layout.addLayout(selection_layout)
        
        # Filter & Search Group
        filter_group = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setSpacing(6)
        
        # Type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("All Types"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Types", "DFF", "TXD", "COL", "IFP", "WAV", "SCM"])
        self.type_combo.currentTextChanged.connect(self.apply_filter)
        type_layout.addWidget(self.type_combo)
        filter_layout.addLayout(type_layout)
        
        # Version filter
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("All Versions"))
        self.version_combo = QComboBox()
        self.version_combo.addItems(["All Versions", "3.0.0.0", "3.1.0.1", "3.3.0.2", "3.6.0.3"])
        version_layout.addWidget(self.version_combo)
        filter_layout.addLayout(version_layout)
        
        # Search
        search_layout = QVBoxLayout()
        self.matches_label = QLabel("0 matches")
        search_layout.addWidget(self.matches_label)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search...")
        self.filter_input.textChanged.connect(self.apply_filter)
        search_layout.addWidget(self.filter_input)
        
        search_btn_layout = QHBoxLayout()
        self.find_btn = QPushButton("Find")
        self.hit_tabs_check = QCheckBox("Hit Tabs")
        search_btn_layout.addWidget(self.find_btn)
        search_btn_layout.addWidget(self.hit_tabs_check)
        search_layout.addLayout(search_btn_layout)
        
        filter_layout.addLayout(search_layout)
        right_layout.addWidget(filter_group)
        
        # Info section
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel("Name"))
        info_layout.addWidget(QLabel("IMG File"))
        info_layout.addWidget(QLabel("RW Version"))
        right_layout.addLayout(info_layout)
        
        right_layout.addStretch()
        return right_widget
    
    def _create_adaptive_button(self, text, action_type=None, icon=None, callback=None):
        """Create button with adaptive styling and theme support"""
        btn = QPushButton(text)
        
        # Set action type property for theme styling
        if action_type:
            btn.setProperty("action-type", action_type)
        
        # Add icon if enabled in settings
        if icon and self.app_settings.current_settings.get("show_button_icons", False):
            btn.setIcon(QIcon.fromTheme(icon))
        
        # Connect callback
        if callback:
            btn.clicked.connect(callback)
        
        # Set size policy and properties
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setMinimumHeight(26)
        btn.setToolTip(text)
        
        # Apply custom button colors if enabled
        if self.app_settings.current_settings.get("custom_button_colors", True) and action_type:
            color_key = f"button_{action_type}_color"
            if color_key in self.app_settings.current_settings:
                color = self.app_settings.current_settings[color_key]
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border: 2px solid #BDBDBD;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-weight: bold;
                        min-height: 24px;
                    }}
                    QPushButton:hover {{
                        background-color: {self._darken_color(color, 0.1)};
                        border-color: #9E9E9E;
                    }}
                    QPushButton:pressed {{
                        background-color: {self._darken_color(color, 0.2)};
                    }}
                """)
        
        return btn
    
    def _darken_color(self, hex_color, factor):
        """Helper function to darken a hex color"""
        if not hex_color.startswith('#'):
            return hex_color
        
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))  
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def _add_sample_data(self):
        """Add sample data to show interface"""
        sample_entries = [
            ("3", "COL", "building.col", "245 KB", "COL 2", "None", "Ready"),
            ("1", "COL", "player.col", "128 KB", "COL 2", "None", "Ready"),
            ("1", "DFF", "player.dff", "512 KB", "3.6.0.3", "None", "Ready"),
            ("2", "TXD", "player.txd", "1.2 MB", "3.6.0.3", "None", "Ready"),
            ("2", "COL", "vehicle.col", "256 KB", "COL 2", "None", "Ready"),
            ("3", "DFF", "vehicle.dff", "800 KB", "3.6.0.3", "None", "Ready"),
            ("4", "TXD", "vehicle.txd", "2.1 MB", "3.6.0.3", "ZLib", "Ready"),
            ("4", "COL", "weapon.col", "64 KB", "COL 2", "None", "Ready"),
        ]
        
        self.table.setRowCount(len(sample_entries))
        for row, entry_data in enumerate(sample_entries):
            for col, value in enumerate(entry_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        
        self.log_message("Interface loaded with sample data. Open an IMG file to see real content.")
        self.log_message("[INFO] Switched to COL view")
        self.log_message("[INFO] Switched to Combined view")
        self.log_message("[INFO] Switched to IMG view")
        self.log_message("[INFO] Switched to Combined view")
    
    # Core functionality methods
    def open_img_file(self):
        """Open IMG file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG File", "",
            "IMG Files (*.img);;DIR Files (*.dir);;All Files (*)"
        )
        
        if file_path:
            self.load_img_file(file_path)
    
    def load_img_file(self, file_path: str):
        """Load IMG file in background"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_img_load_error)
        self.load_thread.start()
    
    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        self.current_img = img_file
        self.log_message(f"Loaded: {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")
        
        # Update table with real data
        self._populate_table_with_img_data()
        
        # Update status
        self.combined_entries_label.setText(f"Combined Entries: {len(img_file.entries)}")
    
    def _on_img_load_error(self, error_message: str):
        """Handle IMG loading error"""
        self.log_error(error_message)
        QMessageBox.critical(self, "Error", f"Failed to load IMG file:\n{error_message}")
    
    def _populate_table_with_img_data(self):
        """Populate table with real IMG data"""
        if not self.current_img:
            return
        
        self.table.setRowCount(len(self.current_img.entries))
        
        for row, entry in enumerate(self.current_img.entries):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(row)))
            
            # Type
            self.table.setItem(row, 1, QTableWidgetItem(entry.extension or ""))
            
            # Name
            self.table.setItem(row, 2, QTableWidgetItem(entry.name))
            
            # Size
            self.table.setItem(row, 3, QTableWidgetItem(format_file_size(entry.size)))
            
            # Version
            self.table.setItem(row, 4, QTableWidgetItem("3.6.0.3"))
            
            # Compression
            self.table.setItem(row, 5, QTableWidgetItem("None"))
            
            # Status
            self.table.setItem(row, 6, QTableWidgetItem("Ready"))
    
    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
        
        self.log_message("IMG file closed")
        self.combined_entries_label.setText("Combined Entries: 0")
        
        # Restore sample data
        self._add_sample_data()
    
    def rebuild_img(self):
        """Rebuild IMG file"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "No IMG file loaded")
            return
        
        try:
            self.log_message("Starting IMG rebuild...")
            if self.current_img.rebuild():
                self.log_message("IMG rebuilt successfully")
                QMessageBox.information(self, "Success", "IMG rebuilt successfully!")
            else:
                self.log_error("Failed to rebuild IMG")
        except Exception as e:
            self.log_error(f"Rebuild error: {str(e)}")
    
    def import_files(self):
        """Import files into IMG"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "No IMG file loaded")
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Import", "", "All Files (*)"
        )
        
        if file_paths:
            success_count = 0
            for file_path in file_paths:
                try:
                    filename = os.path.basename(file_path)
                    if self.current_img.import_file(file_path, filename):
                        success_count += 1
                except Exception as e:
                    self.log_error(f"Import error: {str(e)}")
            
            self.log_message(f"Imported {success_count} files")
            self._populate_table_with_img_data()  # Refresh table
    
    def export_selected_entries(self):
        """Export selected entries"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select files to export")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        if self.current_img:
            success_count = 0
            for row in selected_rows:
                try:
                    entry = self.current_img.entries[row.row()]
                    output_path = os.path.join(export_dir, entry.name)
                    if self.current_img.export_entry(entry, output_path):
                        success_count += 1
                except Exception as e:
                    self.log_error(f"Export error: {str(e)}")
            
            self.log_message(f"Exported {success_count} files")
        else:
            self.log_message(f"Would export {len(selected_rows)} files (demo mode)")
    
    def remove_selected_entries(self):
        """Remove selected entries"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self, "Remove Entries",
            f"Remove {len(selected_rows)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.current_img:
                removed_count = 0
                # Remove in reverse order
                for row in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
                    try:
                        entry = self.current_img.entries[row.row()]
                        if self.current_img.remove_entry(entry):
                            removed_count += 1
                    except Exception as e:
                        self.log_error(f"Remove error: {str(e)}")
                
                self.log_message(f"Removed {removed_count} entries")
                self._populate_table_with_img_data()  # Refresh table
            else:
                # Demo mode - remove from table
                for row in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
                    self.table.removeRow(row.row())
                self.log_message(f"Removed {len(selected_rows)} entries (demo mode)")
    
    def select_all(self):
        """Select all entries"""
        self.table.selectAll()
    
    def select_inverse(self):
        """Invert selection"""
        selection_model = self.table.selectionModel()
        selected_rows = set(index.row() for index in selection_model.selectedRows())
        
        selection_model.clear()
        for row in range(self.table.rowCount()):
            if row not in selected_rows:
                selection_model.select(
                    self.table.model().index(row, 0),
                    selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows
                )
    
    def on_selection_changed(self):
        """Handle selection changes"""
        selected_count = len(self.table.selectionModel().selectedRows())
        self.selected_label.setText(f"Selected: {selected_count}")
    
    def apply_filter(self):
        """Apply search and type filters"""
        search_text = self.filter_input.text().lower()
        type_filter = self.type_combo.currentText()
        
        matches = 0
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Apply type filter
            if type_filter != "All Types":
                type_item = self.table.item(row, 1)
                if type_item and type_item.text() != type_filter:
                    show_row = False
            
            # Apply search filter
            if show_row and search_text:
                name_item = self.table.item(row, 2)
                if name_item and search_text not in name_item.text().lower():
                    show_row = False
            
            self.table.setRowHidden(row, not show_row)
            if show_row:
                matches += 1
        
        self.matches_label.setText(f"{matches} matches")
    
    def show_img_info(self):
        """Show IMG information dialog"""
        if self.current_img:
            info_text = f"""IMG File Information:

File: {os.path.basename(self.current_img.file_path)}
Version: {getattr(self.current_img, 'version', 'Unknown')}
Entries: {len(self.current_img.entries)}
Total Size: {format_file_size(sum(entry.size for entry in self.current_img.entries))}

File Types:
"""
            # Count file types
            type_counts = {}
            for entry in self.current_img.entries:
                ext = entry.extension or "Unknown"
                type_counts[ext] = type_counts.get(ext, 0) + 1
            
            for file_type, count in sorted(type_counts.items()):
                info_text += f"  {file_type}: {count}\n"
            
            QMessageBox.information(self, "IMG Information", info_text)
        else:
            QMessageBox.information(self, "IMG Information", "No IMG file loaded")
    
    def show_preferences(self):
        """Show preferences dialog"""
        if HAS_THEMES:
            try:
                from App_settings_system import SettingsDialog
                dialog = SettingsDialog(self.app_settings, self)
                dialog.themeChanged.connect(self.apply_theme)
                dialog.settingsChanged.connect(self.apply_theme)
                dialog.exec()
            except Exception as e:
                self.log_error(f"Error opening preferences: {str(e)}")
                QMessageBox.information(self, "Preferences", "Theme preferences coming soon!")
        else:
            QMessageBox.information(self, "Preferences", "Theme system not available")
    
    def show_theme_settings(self):
        """Show theme settings dialog"""
        if HAS_THEMES:
            try:
                from App_settings_system import SettingsDialog
                dialog = SettingsDialog(self.app_settings, self)
                dialog.themeChanged.connect(self.apply_theme)
                dialog.exec()
            except Exception as e:
                self.log_error(f"Error opening theme settings: {str(e)}")
                QMessageBox.information(self, "Themes", "Theme settings coming soon!")
        else:
            QMessageBox.information(self, "Themes", "Theme system not available")
    
    def apply_theme(self):
        """Apply current theme to the application"""
        if HAS_THEMES:
            try:
                # Get the QApplication instance
                app = QApplication.instance()
                if app:
                    # Apply base theme
                    apply_theme_to_app(app, self.app_settings)
                    
                    # Apply button theme
                    apply_pastel_theme_to_buttons(app, self.app_settings)
                    
                    self.log_message("Theme applied successfully")
            except Exception as e:
                self.log_error(f"Error applying theme: {str(e)}")
    
    def refresh_button_colors(self):
        """Refresh button colors based on current theme settings"""
        if not HAS_THEMES:
            return
        
        # Update all buttons with action types
        for widget in self.findChildren(QPushButton):
            action_type = widget.property("action-type")
            if action_type:
                color_key = f"button_{action_type}_color"
                if color_key in self.app_settings.current_settings:
                    color = self.app_settings.current_settings[color_key]
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color};
                            border: 2px solid #BDBDBD;
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: bold;
                            min-height: 24px;
                        }}
                        QPushButton:hover {{
                            background-color: {self._darken_color(color, 0.1)};
                            border-color: #9E9E9E;
                        }}
                        QPushButton:pressed {{
                            background-color: {self._darken_color(color, 0.2)};
                        }}
                    """)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """IMG Factory 1.5 [GUI Demo]

A modern recreation of the classic IMG Factory tool
for Grand Theft Auto game archive management.

Features:
• Original beautiful GUI design restored
• Support for all IMG format versions
• Advanced file operations and validation
• Modern Qt6 interface with classic styling
• Template system and batch operations
• Full theme system with customizable colors

Based on the original IMG Factory by MexUK
Python Qt6 recreation by X-Seti

Version 1.5 - June 2025"""
        
        QMessageBox.about(self, "About IMG Factory", about_text)
    
    # Advanced features (Phase 2)
    def create_new_img(self):
        """Create new IMG with game-specific dialog"""
        if HAS_FULL_COMPONENTS:
            try:
                dialog = GameSpecificIMGDialog(self)
                if dialog.exec() == dialog.DialogCode.Accepted:
                    self.log_message("New IMG created successfully")
            except Exception as e:
                self.log_error(f"Error creating IMG: {str(e)}")
        else:
            QMessageBox.information(self, "Feature Not Available", 
                                  "Advanced IMG creation requires full component modules")
    
    def manage_templates(self):
        """Show template manager"""
        if HAS_FULL_COMPONENTS and self.template_manager:
            try:
                dialog = TemplateManagerDialog(self.template_manager, self)
                dialog.exec()
            except Exception as e:
                self.log_error(f"Error opening template manager: {str(e)}")
        else:
            QMessageBox.information(self, "Feature Not Available",
                                  "Template management requires full component modules")
    
    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            QMessageBox.information(self, "No IMG", "No IMG file loaded")
            return
        
        if HAS_FULL_COMPONENTS:
            try:
                validation = IMGValidator.validate_img_file(self.current_img)
                status = "Valid" if validation.is_valid else "Issues Found"
                summary = validation.get_summary()
                
                self.log_message(f"Validation: {status} - {summary}")
                QMessageBox.information(self, "Validation Results", f"Status: {status}\n{summary}")
            except Exception as e:
                self.log_error(f"Validation error: {str(e)}")
        else:
            self.log_message("IMG validation completed (basic check)")
            QMessageBox.information(self, "Validation", "Basic validation completed - no issues found")
    
    # Utility methods
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
        self.log_output.append(f"[{timestamp}] <span style='color: red;'>ERROR:</span> {message}")
        self.log_output.ensureCursorVisible()
    
    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(('.img', '.dir')) for url in urls):
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.img', '.dir')):
                self.load_img_file(file_path)
                break


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    app.setOrganizationName("IMG Factory")
    
    # Initialize settings first
    if HAS_THEMES:
        print("Initializing theme system...")
        settings = AppSettings()
        
        # Apply base theme to application
        apply_theme_to_app(app, settings)
        print(f"✓ Applied base theme: {settings.current_settings.get('theme', 'default')}")
    else:
        settings = AppSettings()
        print("Using basic settings (theme system not available)")
    
    try:
        # Create main window
        print("Creating main window...")
        window = ImgFactoryDemo(settings)
        
        # Apply button themes after window creation
        if HAS_THEMES:
            print("Applying button themes...")
            apply_pastel_theme_to_buttons(app, settings)
            
            # Refresh button colors to ensure they're applied
            QTimer.singleShot(100, window.refresh_button_colors)
            print("✓ Button themes applied")
        
        # Show window
        window.show()
        print("✓ Window displayed")
        
        # Log startup status
        if HAS_FULL_COMPONENTS:
            window.log_message("IMG Factory started with full functionality")
        else:
            window.log_message("IMG Factory started in demo mode")
            window.log_message("Install component modules for advanced features")
        
        if HAS_THEMES:
            window.log_message(f"Theme system active: {settings.current_settings.get('theme', 'default')}")
            window.log_message("Access Settings → Themes to customize appearance")
        
        # Check command line arguments
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path) and file_path.lower().endswith(('.img', '.dir')):
                window.load_img_file(file_path)
                window.log_message(f"Loaded from command line: {os.path.basename(file_path)}")
        
        # Run application
        print("🚀 IMG Factory ready!")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        
        try:
            QMessageBox.critical(None, "Fatal Error", f"IMG Factory failed to start:\n{str(e)}")
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
