#this belongs in gui/ gui_layout.py - Version: 14
# X-Seti - JULY03 2025 - Img Factory 1.5 - GUI Layout Module - Fixed Button Connections

#adjectments, Refrash button renamed from update-list, Reload button.
#first button block needs adjucting.
#_get_short_text moved to gui_backend.py

import re
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QMenuBar, QStatusBar, QProgressBar, QTabWidget, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QIcon, QShortcut, QKeySequence
from core.gui_search import ASearchDialog, SearchManager
from typing import Optional, Dict, Any, List

class IMGFactoryGUILayout:
    """Handles the complete GUI layout for IMG Factory 1.5"""
    
    def __init__(self, main_window):
        """Initialize GUI layout with tab settings support"""
        self.main_window = main_window
        self.table = None
        self.log = None
        self.main_splitter = None
        self.img_buttons = []       #_create_right_panel_with_pastel_buttons
        self.entry_buttons = []     #_create_right_panel_with_pastel_buttons
        self.options_buttons = []
        #_create_right_panel_with_pastel_buttons

        # Status bar components
        self.status_bar = None
        self.status_label = None
        self.progress_bar = None    #show_progres
        self.img_info_label = None

        # Tab-related components
        self.main_type_tabs = None
        self.tab_widget = None
        self.left_vertical_splitter = None

        # Fix button mappings and connections
        self.add_button_methods()

        # Initialize tab settings and button icons after a short delay
        # This ensures the main window is fully initialized
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._delayed_initialization)
    
    def _delayed_initialization(self):
        """Perform delayed initialization after main window is ready"""
        try:
            # Load tab settings from app settings
            self.load_tab_settings_from_app_settings()

            # Enable button icons based on settings
            #self.enable_button_icons()

        except Exception as e:
            # Don't crash on initialization issues
            if hasattr(self.main_window, 'app_settings'):
                self.load_tab_settings_from_app_settings(self.main_window.app_settings)

    def apply_settings_changes(self, settings):
        """Apply settings changes to the GUI layout"""
        try:
            # Apply tab settings if they exist
            if any(key.startswith('tab_') or key in ['main_tab_height', 'individual_tab_height', 'tab_font_size', 'tab_padding', 'tab_container_height'] for key in settings.keys()):
                main_height = settings.get("main_tab_height", 35)
                tab_height = settings.get("individual_tab_height", 24)
                font_size = settings.get("tab_font_size", 9)
                padding = settings.get("tab_padding", 4)
                container_height = settings.get("tab_container_height", 40)

                self._apply_dynamic_tab_styling(
                    main_height, tab_height, font_size, padding, container_height
                )

            # Apply button icon settings
            if 'show_button_icons' in settings:
                self._update_button_icons_state(settings['show_button_icons'])

            # Apply other GUI settings as needed
            if 'table_row_height' in settings:
                self._update_table_row_height(settings['table_row_height'])

            if 'widget_spacing' in settings:
                self._update_widget_spacing(settings['widget_spacing'])

        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Error applying settings changes: {str(e)}")

    def _update_table_row_height(self, height):
        """Update table row height"""
        try:
            if hasattr(self, 'table') and self.table:
                self.table.verticalHeader().setDefaultSectionSize(height)
        except Exception:
            pass

    def _update_widget_spacing(self, spacing):
        """Update widget spacing"""
        try:
            if hasattr(self, 'main_splitter') and self.main_splitter:
                # Update splitter spacing
                self.main_splitter.setHandleWidth(max(4, spacing))
        except Exception:
            pass

    def create_main_ui_with_splitters(self, main_layout):
        """Create the main UI with correct 3-section layout"""
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - vertical layout with 3 sections
        left_panel = self._create_left_three_section_panel()
        
        # Right side - control buttons with pastel colors
        right_panel = self._create_right_panel_with_pastel_buttons()
        
        # Add panels to splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_panel)
        
        # FIXED: Set splitter proportions and force constraints
        self.main_splitter.setSizes([1000, 280])  # Fixed right panel to 280px
        
        # FIXED: Add size constraints to force the right panel width
        right_panel.setMaximumWidth(280)  # Fixed at 280px
        right_panel.setMinimumWidth(280)  # Fixed at 280px
        
        # Style the main horizontal splitter handle with theme colors
        theme_colors = self._get_theme_colors("default")
        splitter_bg = theme_colors.get('splitter_color_background', 'default')
        splitter_shine = theme_colors.get('splitter_color_shine', 'default')
        splitter_shadow = theme_colors.get('splitter_color_shadow', 'default')
        
        self.main_splitter.setStyleSheet(f"""
            QSplitter::handle:horizontal {{
                background-color: #{splitter_bg};
                border: 1px solid #{splitter_shine};
                border-left: 1px solid #{splitter_shadow};
                width: 8px;
                margin: 2px 1px;
                border-radius: 3px;
            }}
            
            QSplitter::handle:horizontal:hover {{
                background-color: #{splitter_shine};
                border-color: #{splitter_shadow};
            }}
            
            QSplitter::handle:horizontal:pressed {{
                background-color: #{splitter_shadow};
            }}
        """)
        
        # Prevent panels from collapsing completely
        self.main_splitter.setCollapsible(0, False)  # Left panel
        self.main_splitter.setCollapsible(1, False)  # Right panel
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)
    
    def _create_left_three_section_panel(self):
        """Create left panel with 3 sections: Main Tabs, File Window, Status Window - UPDATED HEIGHTS"""
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(3, 3, 3, 3)
        left_layout.setSpacing(0)  # No spacing - splitter handles this

        # Create vertical splitter for the 3 sections
        self.left_vertical_splitter = QSplitter(Qt.Orientation.Vertical)

        # 1. TOP: Main Tabs (IMG, COL, TXD) - COMPACT HEIGHT
        #main_tabs = self._create_main_tabs_section()
        #self.left_vertical_splitter.addWidget(main_tabs)

        # 2. MIDDLE: File Window (table with sub-tabs)
        file_window = self._create_file_window()
        self.left_vertical_splitter.addWidget(file_window)

        # 3. BOTTOM: Status Window (log and status)
        status_window = self._create_status_window()
        self.left_vertical_splitter.addWidget(status_window)

        # Set section proportions: MainTabs(40px), File(720px), Status(200px)
        # Total height ~960px, tabs take minimal space
        self.left_vertical_splitter.setSizes([ 760, 200])

        # Prevent sections from collapsing completely
        self.left_vertical_splitter.setCollapsible(1, False)  # File window
        self.left_vertical_splitter.setCollapsible(2, False)  # Status window

        # Apply theme styling to vertical splitter
        self._apply_vertical_splitter_theme()

        left_layout.addWidget(self.left_vertical_splitter)

        return left_container

    def update_main_tab_info(self, file_type, file_path=None, stats=None):
        """Update main tab info - called from main window"""
        if hasattr(self, 'gui_layout'):
            self.gui_layout.update_ultra_compact_file_info(file_type, file_path, stats)

    def load_tab_settings_from_app_settings(self, app_settings):
        """Load tab settings from app settings - MISSING METHOD FIX"""
        try:
            if hasattr(app_settings, 'current_settings'):
                # Load tab-related settings
                tab_height = app_settings.current_settings.get('main_tab_height', 20)
                tab_style = app_settings.current_settings.get('tab_style', 'Compact')

                # Apply tab settings if main_tab_widget exists
                if hasattr(self, 'main_tab_widget'):
                    # Apply basic tab styling
                    self.main_tab_widget.setStyleSheet(f"""
                    QTabWidget::tab-bar {{
                        height: {tab_height}px;
                    }}
                    """)

            return True

        except Exception as e:
            print(f"Error loading tab settings: {e}")
            return False

    def _create_ultra_compact_file_status(self, file_type):
        """Create ultra compact file status widget - single line"""
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(3, 1, 3, 1)  # Minimal margins
        status_layout.setSpacing(8)

        # Combined file info in one line
        file_info_label = QLabel(f"No {file_type} file loaded")
        file_info_label.setStyleSheet("color: #666; font-size: 8pt;")
        status_layout.addWidget(file_info_label)

        # Store references for updates
        if file_type == "IMG":
            self.img_combined_label = file_info_label
        elif file_type == "COL":
            self.col_combined_label = file_info_label
        elif file_type == "TXD":
            self.txd_combined_label = file_info_label

        # Add stretch to push everything left
        status_layout.addStretch()

        # Quick action button (optional)
        action_btn = QPushButton("...")
        action_btn.setMaximumSize(16, 16)
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 2px;
                font-size: 7pt;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        action_btn.clicked.connect(lambda: self._show_file_actions(file_type))
        status_layout.addWidget(action_btn)

        status_widget.setMaximumHeight(20)  # Ultra compact height

        return status_widget

    def _show_file_actions(self, file_type):
        """Show quick actions for file type"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self.main_window)

        if file_type == "IMG":
            menu.addAction("📂 Open IMG File", self.main_window.open_img_file)
            menu.addAction("📋 File Info", lambda: self._show_file_info_popup(file_type))
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                menu.addAction("✅ Validate IMG", self.main_window.validate_img)
        elif file_type == "COL":
            menu.addAction("📂 Open COL File", self.main_window.open_col_file)
            menu.addAction("📋 File Info", lambda: self._show_file_info_popup(file_type))
        elif file_type == "TXD":
            menu.addAction("📂 Open TXD File", lambda: self._open_txd_file())
            menu.addAction("📋 File Info", lambda: self._show_file_info_popup(file_type))

        # Show menu at button position
        button = self.main_window.sender()
        if button:
            menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def _show_show_file_actions(self, file_type):
        """Show file info popup for current file"""
        if file_type == "IMG" and hasattr(self.main_window, 'current_img') and self.main_window.current_img:
            self._show_detailed_file_info(file_type, self.main_window.current_img.file_path, self.main_window.current_img)
        elif file_type == "COL" and hasattr(self.main_window, 'current_col') and self.main_window.current_col:
            self._show_detailed_file_info(file_type, self.main_window.current_col.get('file_path', ''), self.main_window.current_col)
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self.main_window, f"{file_type} Info", f"No {file_type} file currently loaded")

    def update_ultra_compact_file_info(self, file_type, file_path=None, stats=None):
        """Update ultra compact file info display"""
        if file_type == "IMG":
            if hasattr(self, 'img_combined_label'):
                if file_path:
                    name = os.path.basename(file_path)
                    count = stats.get('entries', 0) if stats else 0
                    self.img_combined_label.setText(f"{name} ({count} entries)")
                else:
                    self.img_combined_label.setText("No IMG file loaded")

        elif file_type == "COL":
            if hasattr(self, 'col_combined_label'):
                if file_path:
                    name = os.path.basename(file_path)
                    count = stats.get('models', 0) if stats else 0
                    self.col_combined_label.setText(f"{name} ({count} models)")
                else:
                    self.col_combined_label.setText("No COL file loaded")

        elif file_type == "TXD":
            if hasattr(self, 'txd_combined_label'):
                if file_path:
                    name = os.path.basename(file_path)
                    count = stats.get('textures', 0) if stats else 0
                    self.txd_combined_label.setText(f"{name} ({count} textures)")
                else:
                    self.txd_combined_label.setText("No TXD file loaded")


    def _create_compact_file_status(self, file_type):
        """Create compact file status widget for a specific file type"""
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(5, 2, 5, 2)
        status_layout.setSpacing(10)

        # File name
        file_label = QLabel(f"{file_type} File:")
        file_label.setStyleSheet("font-weight: bold; color: #333;")
        status_layout.addWidget(file_label)

        file_name_label = QLabel("No file loaded")
        file_name_label.setStyleSheet("color: #666;")
        status_layout.addWidget(file_name_label)

        # Store references for updates
        if file_type == "IMG":
            self.img_file_name_label = file_name_label
        elif file_type == "COL":
            self.col_file_name_label = file_name_label
        elif file_type == "TXD":
            self.txd_file_name_label = file_name_label

        # Add stretch to push everything left
        status_layout.addStretch()

        # Quick stats
        stats_label = QLabel("Items: 0")
        stats_label.setStyleSheet("color: #666; font-size: 9pt;")
        status_layout.addWidget(stats_label)

        # Store reference for updates
        if file_type == "IMG":
            self.img_stats_label = stats_label
        elif file_type == "COL":
            self.col_stats_label = stats_label
        elif file_type == "TXD":
            self.txd_stats_label = stats_label

        return status_widget

    def _on_main_tab_changed(self, index):
        """Handle main tab change between IMG/COL/TXD"""
        tab_names = ["IMG", "COL", "TXD"]
        if 0 <= index < len(tab_names):
            current_type = tab_names[index]
            self.main_window.log_message(f"Switched to {current_type} mode")

            # Update the file window based on current type
            self._update_file_window_for_type(current_type)

            # Emit signal for main window to handle
            if hasattr(self.main_window, 'on_main_file_type_changed'):
                self.main_window.on_main_file_type_changed(current_type)

    def _update_file_window_for_type(self, file_type):
        """Update file window content based on selected type"""
        if file_type == "IMG":
            # Show IMG-specific table columns
            self._configure_table_for_img()
        elif file_type == "COL":
            # Show COL-specific table columns
            self._configure_table_for_col()
        elif file_type == "TXD":
            # Show TXD-specific table columns
            self._configure_table_for_txd()

    def _configure_table_for_img(self):
        """Configure table for IMG file display"""
        if hasattr(self, 'table'):
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                "Name", "Extension", "Size", "Hash", "Version", "Compression", "Status"
            ])

    def _configure_table_for_col(self):
        """Configure table for COL file display"""
        if hasattr(self, 'table'):
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "Model", "Type", "Surfaces", "Vertices", "Collision", "Status"
            ])

    def _configure_table_for_txd(self):
        """Configure table for TXD file display"""
        if hasattr(self, 'table'):
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "Texture", "Format", "Width", "Height", "Mipmaps", "Status"
            ])

    def update_file_info_for_type(self, file_type, file_path=None, stats=None):
        """Update file info for specific type"""
        if file_type == "IMG":
            if hasattr(self, 'img_file_name_label'):
                name = os.path.basename(file_path) if file_path else "No file loaded"
                self.img_file_name_label.setText(name)
            if hasattr(self, 'img_stats_label') and stats:
                self.img_stats_label.setText(f"Items: {stats.get('entries', 0)}")

        elif file_type == "COL":
            if hasattr(self, 'col_file_name_label'):
                name = os.path.basename(file_path) if file_path else "No file loaded"
                self.col_file_name_label.setText(name)
            if hasattr(self, 'col_stats_label') and stats:
                self.col_stats_label.setText(f"Models: {stats.get('models', 0)}")

        elif file_type == "TXD":
            if hasattr(self, 'txd_file_name_label'):
                name = os.path.basename(file_path) if file_path else "No file loaded"
                self.txd_file_name_label.setText(name)
            if hasattr(self, 'txd_stats_label') and stats:
                self.txd_stats_label.setText(f"Textures: {stats.get('textures', 0)}")


    def _create_information_bar(self):
        """Create information bar with file details"""
        info_bar = QWidget()
        info_layout = QVBoxLayout(info_bar)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(3)
        
        # Title
        title_label = QLabel("IMG Archive Information")
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #333;")
        info_layout.addWidget(title_label)
        
        # File details in horizontal layout
        details_layout = QHBoxLayout()
        
        # File name
        self.file_name_label = QLabel("File: No file loaded")
        details_layout.addWidget(self.file_name_label)
        
        # Separator
        sep1 = QLabel(" | ")
        sep1.setStyleSheet("color: #666;")
        details_layout.addWidget(sep1)
        
        # Entry count
        self.entry_count_label = QLabel("Entries: 0")
        details_layout.addWidget(self.entry_count_label)
        
        # Separator
        sep2 = QLabel(" | ")
        sep2.setStyleSheet("color: #666;")
        details_layout.addWidget(sep2)
        
        # File size
        self.file_size_label = QLabel("Size: 0 bytes")
        details_layout.addWidget(self.file_size_label)
        
        # Separator
        sep3 = QLabel(" | ")
        sep3.setStyleSheet("color: #666;")
        details_layout.addWidget(sep3)
        
        # Format version
        self.format_version_label = QLabel("Format: Unknown")
        details_layout.addWidget(self.format_version_label)
        
        # Stretch to push everything left
        details_layout.addStretch()
        
        info_layout.addLayout(details_layout)
        
        # Apply theme styling
        self._apply_info_bar_theme_styling(info_bar)
        
        return info_bar
    
    def _create_file_window(self):
        """Create file window with tabs for different views"""
        file_window = QWidget()
        file_layout = QVBoxLayout(file_window)
        file_layout.setContentsMargins(5, 5, 5, 5)
        file_layout.setSpacing(3)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: File Entries (main table)
        entries_tab = QWidget()
        entries_layout = QVBoxLayout(entries_tab)
        entries_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Extension", "Size", "Hash", "Version", "Compression", "Status"
        ])
        
        # Table configuration
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSortingEnabled(True)
        
        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Extension
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Hash
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Compression
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status
        
        # Apply theme styling to table
        self._apply_table_theme_styling()
        
        entries_layout.addWidget(self.table)
        self.tab_widget.addTab(entries_tab, "📁 File Entries")
        
        # Tab 2: Directory Tree (future enhancement)
        tree_tab = QWidget()
        tree_layout = QVBoxLayout(tree_tab)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        tree_placeholder = QLabel("Directory tree view will be implemented here")
        tree_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tree_placeholder.setStyleSheet("color: #666; font-style: italic;")
        tree_layout.addWidget(tree_placeholder)
        
        self.tab_widget.addTab(tree_tab, "🌳 Directory Tree")
        
        # Tab 3: Search Results (future enhancement)
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_placeholder = QLabel("Search results will be displayed here")
        search_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_placeholder.setStyleSheet("color: #666; font-style: italic;")
        search_layout.addWidget(search_placeholder)

        self.tab_widget.addTab(search_tab, "🔍 Search Results")

        file_layout.addWidget(self.tab_widget)

        return file_window
    
    def _create_status_window(self):
        """Create status window with log and status indicators"""
        status_window = QWidget()
        status_layout = QVBoxLayout(status_window)
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.setSpacing(3)
        
        # Title with status indicators
        title_layout = QHBoxLayout()
        
        title_label = QLabel("Activity Log")
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #333;")
        title_layout.addWidget(title_label)
        
        # Status indicators
        title_layout.addStretch()
        
        # Progress indicator (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setVisible(False)
        title_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 8pt;
                color: #2e7d32;
            }
        """)
        title_layout.addWidget(self.status_label)
        
        status_layout.addLayout(title_layout)
     
        # Log with scrollbars
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Activity log will appear here...")
        
        # Enable scrollbars for log
        self.log.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.log.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Apply theme styling to log
        self._apply_log_theme_styling()
        
        status_layout.addWidget(self.log)
        
        return status_window
    
    def add_button_methods(main_window): # we keep this version
        """Add any missing button method names that GUI might be calling"""
        try:
            # Import the functions we need
            from components.img_import_export_functions import (
                import_files_function, import_via_function, export_selected_function,
                export_via_function, quick_export_function, export_all_function,
                remove_selected_function, remove_via_entries_function, dump_all_function  # ADD THIS
            )

            # Add all possible method names that buttons might call
            method_mappings = {
                # Import methods
                'import_files': lambda: import_files_function(main_window),
                'import_files_via': lambda: import_via_function(main_window),
                'import_files_advanced': lambda: import_via_function(main_window),

                # Export methods
                'export_selected': lambda: export_selected_function(main_window),
                'export_selected_via': lambda: export_via_function(main_window),
                'export_selected_advanced': lambda: export_via_function(main_window),
                'export_selected_entries': lambda: export_selected_function(main_window),
                'quick_export_selected': lambda: quick_export_function(main_window),
                'quick_export': lambda: quick_export_function(main_window),
                'export_all_entries': lambda: export_all_function(main_window),
                'export_all': lambda: export_all_function(main_window),

                # Remove methods
                'remove_selected': lambda: remove_selected_function(main_window),
                'remove_selected_entries': lambda: remove_selected_function(main_window),
                'remove_all_entries': lambda: remove_selected_function(main_window),
                'remove_via_entries': lambda: remove_via_entries_function(main_window),  # ADD THIS LINE

                # Other methods
                'dump_entries': lambda: dump_all_function(main_window),
                'dump_all_entries': lambda: dump_all_function(main_window),
                'refresh_table': main_window.refresh_table if hasattr(main_window, 'refresh_table') else lambda: main_window.log_message("Refresh requested"),
                'reload_table': main_window.refresh_table if hasattr(main_window, 'reload_table') else lambda: main_window.log_message("reload requested"),
            }
            # Add all method names to main_window
            for method_name, method_func in method_mappings.items():
                setattr(main_window, method_name, method_func)

            main_window.log_message(f"✅ Added {len(method_mappings)} button method mappings")
            return True

        except Exception as e:
            main_window.log_message(f"❌ Error adding button methods: {str(e)}")
            return False

    def _create_right_panel_with_pastel_buttons(self):
        """Create right panel with pastel colored buttons - FIXED BUTTON CONNECTIONS"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(6)

        # IMG Section with pastel colors
        img_box = QGroupBox("IMG, COL Files")
        img_layout = QGridLayout()
        img_layout.setSpacing(2)
        img_buttons_data = [
            ("Create Img", "new", "document-new", "#EEFAFA", "create_new_img"),
            ("Open", "open", "document-open", "#E3F2FD", "open_img_file"),
            ("Reload", "reload", "document-reload", "#F9FBE7", "reload_table"),
            ("     ", "space", "placeholder", "#FEFEFE", "useless_button"),
            ("Close", "close", "window-close", "#FFF3E0", "close_img_file"),
            ("Close All", "close_all", "edit-clear", "#FFF3E0", "close_all_img"),
            ("Rebuild", "rebuild", "view-rebuild", "#E8F5E8", "rebuild_img"),
            ("Rebuild As", "rebuild_as", "document-save-as", "#E8F5E8", "rebuild_img_as"),
            ("Rebuild All", "rebuild_all", "document-save", "#E8F5E8", "rebuild_all_img"),
            ("Merge", "merge", "document-merge", "#F3E5F5", "merge_img"),
            ("Split via", "split", "edit-cut", "#F3E5F5", "split_img"),
            ("Convert", "convert", "transform", "#FFF8E1", "convert_img_format"),
        ]
        
        for i, (label, action_type, icon, color, method_name) in enumerate(img_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entries Section with pastel colors
        entries_box = QGroupBox("File Entries")
        entries_layout = QGridLayout()
        entries_layout.setSpacing(2)
        entry_buttons_data = [
            ("Import", "import", "document-import", "#E1F5FE", "import_files"),
            ("Import via", "import_via", "document-import", "#E1F5FE", "import_files_via"),
            ("Refresh", "update", "view-refresh", "#F9FBE7", "refresh_table"),
            ("Export", "export", "document-export", "#E8F5E8", "export_selected"),
            ("Export via", "export_via", "document-export", "#E8F5E8", "export_selected_via"),
            ("Quick Exp", "quick_export", "document-send", "#E8F5E8", "quick_export_selected"),
            ("Remove", "remove", "edit-delete", "#FFEBEE", "remove_selected"),
            ("Remove via", "remove_via", "document-remvia", "#FFEBEE", "remove_via_entries"),
            ("Dump", "dump", "document-dump", "#F3E5F5", "dump_entries"),
            ("Rename", "rename", "edit-rename", "#FFF8E1", "rename_selected"),
            ("Replace", "replace", "edit-copy", "#FFF8E1", "replace_selected"),
            ("Select All", "select_all", "edit-select-all", "#F1F8E9", "select_all_entries"),
            ("Inverse", "sel_inverse", "edit-select", "#F1F8E9", "select_inverse"),
            ("Sort via", "sort", "view-sort", "#F1F8E9", "sort_entries"),
            ("Pin selected", "pin_selected", "pin", "#E8EAF6", "pin_selected_entries"),
        ]
        
        for i, (label, action_type, icon, color, method_name) in enumerate(entry_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Options Section with pastel colors
        options_box = QGroupBox("Editing Options")
        options_layout = QGridLayout()
        options_layout.setSpacing(2)
        options_buttons_data = [
            ("Col Edit", "col_edit", "col-edit", "#E3F2FD", "edit_col_file"),
            ("Txd Edit", "txd_edit", "txd-edit", "#F8BBD9", "edit_txd_file"),
            ("Dff Edit", "dff_edit", "dff-edit", "#E1F5FE", "edit_dff_file"),
            ("Ipf Edit", "ipf_edit", "ipf-edit", "#FFF3E0", "edit_ipf_file"),
            ("IDE Edit", "ide_edit", "ide-edit", "#F8BBD9", "edit_ide_file"),
            ("IPL Edit", "ipl_edit", "ipl-edit", "#E1F5FE", "edit_ipl_file"),
            ("Dat Edit", "dat_edit", "dat-edit", "#E3F2FD", "edit_dat_file"),
            ("Zons Cull Ed", "zones_cull", "zones-cull", "#E8F5E8", "edit_zones_cull"),
            ("Weap Edit", "weap_edit", "weap-edit", "#E1F5FE", "edit_weap_file"),
            ("Vehi Edit", "vehi_edit", "vehi-edit", "#E3F2FD", "edit_vehi_file"),
            ("Peds Edit", "peds_edit", "peds-edit", "#F8BBD9", "edit_peds_file"),
            ("Radar Map", "radar_map", "radar-map", "#F8BBD9", "edit_radar_map"),
            ("Paths Map", "paths_map", "paths-map", "#E1F5FE", "edit_paths_map"),
            ("Waterpro", "timecyc", "timecyc", "#E3F2FD", "edit_waterpro"),
            ("Weather", "timecyc", "timecyc", "#E0F2F1", "edit_weather"),
            ("Handling", "handling", "handling", "#E4E3ED", "edit_handling"),
            ("Objects", "ojs_breakble", "ojs-breakble", "#FFE0B2", "edit_objects"),
            ("SCM code", "scm_code", "scm-code", "#FFD0BD", "editscm"),
            ("GXT font", "gxt_font", "gxt-font", "#CFD0BD", "editgxt"),
            ("Menu Edit", "menu_font", "menu-font", "#AFD0BD", "editmenu"),
        ]
        
        for i, (label, action_type, icon, color, method_name) in enumerate(options_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color, method_name)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.options_buttons.append(btn)
            options_layout.addWidget(btn, i // 3, i % 3)
        
        options_box.setLayout(options_layout)
        right_layout.addWidget(options_box)

        # Filter Section
        filter_box = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(4)

        # Filter controls
        filter_controls = QHBoxLayout()
        filter_combo = QComboBox()
        filter_combo.addItems(["All Files", "DFF Models", "TXD Textures", "COL Collision", "IFP Animations"])
        filter_controls.addWidget(QLabel("Type:"))
        filter_controls.addWidget(filter_combo)
        filter_layout.addLayout(filter_controls)

        search_controls = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search filename...")
        search_controls.addWidget(QLabel("Search:"))
        search_controls.addWidget(search_input)
        filter_layout.addLayout(search_controls)

        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)

        # Add stretch to push everything up
        right_layout.addStretch()

        return right_panel
    
    def _create_pastel_button(self, label, action_type, icon, bg_color, method_name):
        """Create a button with pastel coloring and connect to method"""
        btn = QPushButton(label)
        btn.setMaximumHeight(22)
        btn.setMinimumHeight(20)

        """
        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        """

        # Apply pastel styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 8pt;
                font-weight: bold;
                color: #333333;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color, 0.85)};
                border: 1px solid #999999;
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color, 0.7)};
            }}
        """)

        # Set action type property
        btn.setProperty("action-type", action_type)

        # Connect to main window method
        try:
            if hasattr(self.main_window, method_name):
                method = getattr(self.main_window, method_name)
                btn.clicked.connect(method)
                print(f"✅ Connected '{label}' to {method_name}")
            else:
                # Create placeholder that logs the missing method
                btn.clicked.connect(lambda: self.main_window.log_message(f"Method '{method_name}' not implemented"))
                print(f"⚠️ Method '{method_name}' not found for '{label}'")
        except Exception as e:
            print(f"❌ Error connecting button '{label}': {e}")
            btn.clicked.connect(lambda: self.main_window.log_message(f"Button '{label}' connection error"))

        return btn
    
    def _get_short_text(self, label):
        """Get short text for button"""
        short_map = {
            "New": "New",
            "Open": "Open",
            "Close": "Close",
            "Close All": "Close A",
            "Reload": "Reload",
            " ": " ",
            "Rebuild": "Rebld",
            "Rebuild As": "Rebld As",
            "Rebuild All": "Rebld Al",
            "Merge": "Merge",
            "Split": "Split",
            "Convert": "Conv",
            "Import": "Imp",
            "Import via": "Imp via",
            "Refresh": "Refresh",
            "Export": "Exp",
            "Export via": "Exp via",
            "Quick Export": "Q Exp",
            "Remove": "Rem",
            "Remove via": "Rem via",
            "Dump": "Dump",
            "Pin selected": "Pin",
            "Rename": "Rename",
            "Replace": "Replace",
            "Select All": "Select",
            "Sel Inverse": "Inverse",
            "Sort": "Sort",
            # Editing Options
            "Col Edit": "Col Edit",
            "Txd Edit": "Txd Edit",
            "Dff Edit": "Dff Edit",
            "Ipf Edit": "Ipf Edit",
            "IDE Edit": "IDE Edit",
            "IPL Edit": "IPL Edit",
            "Dat Edit": "Dat Edit",
            "Zons Cull Ed": "Zons Cull",
            "Weap Edit": "Weap Edit",
            "Vehi Edit": "Vehi Edit",
            "Peds Edit": "Peds Edit",
            "Radar Map": "Radar Map",
            "Paths Map": "Paths Map",
            "Waterpro": "Waterpro",
            "Weather": "Weather",
            "Handling": "Handling",
            "Objects": "Objects",
            "SCM Code": "SCM Code",
            "GXT Edit": "GXT Edit",
            "Menu Edit": "Menu Ed",

        }

        return short_map.get(label, label)

    def _handle_button_click(self, button_label, method_name):
        """Handle button clicks for methods that don't exist yet"""
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"🔘 {button_label} clicked (method: {method_name})")
        else:
            print(f"Button clicked: {button_label} -> {method_name}")
    
    def _darken_color(self, color, factor=0.8):
        """Darken a color by a factor"""
        try:
            # Simple darkening - multiply RGB values
            if color.startswith('#'):
                hex_color = color[1:]
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)

                    # Darken each component
                    r = int(r * factor)
                    g = int(g * factor)
                    b = int(b * factor)

                    return f"#{r:02x}{g:02x}{b:02x}"
            return color
        except:
            return color
    
    def _lighten_color(self, color, factor):
        """Lighten a hex color by factor (0.0 to 1.0)"""
        try:
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))

            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color


    def _apply_log_theme_styling(self):
        """Apply theme styling to the log widget"""
        theme_colors = self._get_theme_colors("default")
        
        bg_color = theme_colors.get('log_background', 'ffffff')
        text_color = theme_colors.get('log_text', '333333')
        
        self.log.setStyleSheet(f"""
            QTextEdit {{
                background-color: #{bg_color};
                color: #{text_color};
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }}
        """)
    
    def _apply_table_theme_styling(self):
        """Apply theme styling to the table widget"""
        theme_colors = self._get_theme_colors("default")
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 3px;
                gridline-color: #e0e0e0;
                font-size: 9pt;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #cccccc;
                font-weight: bold;
                font-size: 9pt;
            }
        """)
    
    def _apply_info_bar_theme_styling(self, info_bar):
        """Apply theme styling to the info bar"""
        info_bar.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }
            QLabel {
                border: none;
                font-size: 9pt;
            }
        """)
    
    def _apply_vertical_splitter_theme(self):
        """Apply theme styling to the vertical splitter"""
        theme_colors = self._get_theme_colors("default")
        splitter_bg = theme_colors.get('splitter_color_background', 'default')
        
        self.left_vertical_splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background-color: #{splitter_bg};
                border: 1px solid #cccccc;
                height: 4px;
                margin: 1px 2px;
                border-radius: 2px;
            }}
            QSplitter::handle:vertical:hover {{
                background-color: #999999;
            }}
        """)

    def _get_theme_colors(self, theme_name):
        """Get theme colors - fallback for missing theme system"""
        try:
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'themes'):
                theme_data = self.main_window.app_settings.themes.get(theme_name, {})
                return theme_data.get('colors', {})
        except:
            pass
        return {
            'log_background': 'ffffff',
            'log_text': '333333',
            'splitter_color_background': 'default',
            'splitter_color_shine': 'default',
            'splitter_color_shadow': 'default'
        }
    
    def apply_table_theme(self):
        """Apply theme styling to the table - called from main window when theme changes"""
        if hasattr(self, 'table') and self.table:
            self._apply_table_theme_styling()
        if hasattr(self, 'log') and self.log:
            self._apply_log_theme_styling()

    def handle_resize_event(self, event):
        """Handle window resize to adapt button text"""
        # Use GUI layout's adaptive method
        if self.main_splitter:
            sizes = self.main_splitter.sizes()
            if len(sizes) > 1:
                right_panel_width = sizes[1]
                self.adapt_buttons_to_width(right_panel_width)

    def adapt_buttons_to_width(self, width):
        """Adapt button text based on available width"""
        all_buttons = []
        if hasattr(self, 'img_buttons'):
            all_buttons.extend(self.img_buttons)
        if hasattr(self, 'entry_buttons'):
            all_buttons.extend(self.entry_buttons)
        if hasattr(self, 'options_buttons'):
            all_buttons.extend(self.options_buttons)
        
        for button in all_buttons:
            if hasattr(button, 'full_text'):
                if width > 280:
                    button.setText(button.full_text)
                elif width > 200:
                    # Medium text - remove some words
                    text = button.full_text.replace(' via', '>').replace(' lst', '')
                    button.setText(text)
                elif width > 150:
                    button.setText(button.short_text)
                else:
                    # Icon only mode
                    button.setText("")

    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)
        
        # Get right panel width
        if hasattr(self, 'main_splitter'):
            sizes = self.main_splitter.sizes()
            if len(sizes) > 1:
                right_panel_width = sizes[1]
                self._adapt_buttons_to_width(right_panel_width)

    def _adapt_buttons_to_width(self, width):
        """Adapt button text based on available width"""
        all_buttons = []
        if hasattr(self, 'img_buttons'):
            all_buttons.extend(self.img_buttons)
        if hasattr(self, 'entry_buttons'):
            all_buttons.extend(self.entry_buttons)
        if hasattr(self, 'options_buttons'):
            all_buttons.extend(self.options_buttons)
        
        for button in all_buttons:
            if hasattr(button, 'full_text'):
                if width > 280:
                    button.setText(button.full_text)
                elif width > 200:
                    # Medium text - remove some words
                    text = button.full_text.replace(' via', '>').replace(' lst', '')
                    button.setText(text)
                elif width > 150:
                    button.setText(button.short_text)
                else:
                    # Icon only mode
                    button.setText("")

    # logging
    def log_message(self, message):
        """Add message to activity log"""
        if self.log:
            from PyQt6.QtCore import QDateTime
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            self.log.append(f"[{timestamp}] {message}")
            # Auto-scroll to bottom
            self.log.verticalScrollBar().setValue(
                self.log.verticalScrollBar().maximum()
            )
    
    def show_gui_layout_settings(self):
        """Show comprehensive GUI Layout settings dialog - called from Settings menu"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
                                     QPushButton, QGroupBox, QCheckBox, QComboBox, QTabWidget, 
                                     QWidget, QSlider, QFormLayout)
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("🖥️ GUI Layout Settings")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Create tab widget for different settings categories
        tabs = QTabWidget()
        
        # === TAB 1: Panel Layout ===
        panel_tab = QWidget()
        panel_layout = QVBoxLayout(panel_tab)
        
        # Right Panel Width
        width_group = QGroupBox("📏 Right Panel Width")
        width_layout = QVBoxLayout(width_group)
        
        current_width = self.main_splitter.sizes()[1] if len(self.main_splitter.sizes()) > 1 else 280
        
        # Width spinner
        width_form = QFormLayout()
        width_spin = QSpinBox()
        width_spin.setRange(180, 400)
        width_spin.setValue(current_width)
        width_spin.setSuffix(" px")
        width_form.addRow("Panel Width:", width_spin)
        
        # Preview label
        preview_label = QLabel(f"Current: {current_width}px")
        preview_label.setStyleSheet("color: #666; font-style: italic;")
        width_form.addRow("Preview:", preview_label)
        width_layout.addLayout(width_form)
        
        def update_preview():
            new_width = width_spin.value()
            preview_label.setText(f"Preview: {new_width}px")
            # Live preview
            self._apply_right_panel_width(new_width)
        
        width_spin.valueChanged.connect(update_preview)
        
        panel_layout.addWidget(width_group)
        
        # Button Layout Settings
        button_group = QGroupBox("🔘 Button Layout")
        button_layout = QVBoxLayout(button_group)
        
        button_form = QFormLayout()
        
        # Section spacing
        section_spacing_spin = QSpinBox()
        section_spacing_spin.setRange(2, 20)
        section_spacing_spin.setValue(6)
        section_spacing_spin.setSuffix(" px")
        button_form.addRow("Section Spacing:", section_spacing_spin)
        
        # Button spacing
        button_spacing_spin = QSpinBox()
        button_spacing_spin.setRange(1, 10)
        button_spacing_spin.setValue(2)
        button_spacing_spin.setSuffix(" px")
        button_form.addRow("Button Spacing:", button_spacing_spin)
        
        # Panel margins
        panel_margins_spin = QSpinBox()
        panel_margins_spin.setRange(0, 15)
        panel_margins_spin.setValue(4)
        panel_margins_spin.setSuffix(" px")
        button_form.addRow("Panel Margins:", panel_margins_spin)
        
        button_layout.addLayout(button_form)
        panel_layout.addWidget(button_group)
        
        tabs.addTab(panel_tab, "📐 Panel Layout")
        
        # === TAB 2: Button Appearance ===
        button_tab = QWidget()
        button_tab_layout = QVBoxLayout(button_tab)
        
        # Button Height
        height_group = QGroupBox("📏 Button Dimensions")
        height_layout = QVBoxLayout(height_group)
        
        height_form = QFormLayout()
        
        button_height_spin = QSpinBox()
        button_height_spin.setRange(18, 40)
        button_height_spin.setValue(22)
        button_height_spin.setSuffix(" px")
        height_form.addRow("Button Height:", button_height_spin)
        
        button_font_size_spin = QSpinBox()
        button_font_size_spin.setRange(6, 12)
        button_font_size_spin.setValue(8)
        button_font_size_spin.setSuffix(" pt")
        height_form.addRow("Font Size:", button_font_size_spin)
        
        height_layout.addLayout(height_form)
        button_tab_layout.addWidget(height_group)
        
        # Button Font
        font_group = QGroupBox("🔤 Button Font")
        font_layout = QVBoxLayout(font_group)
        
        font_form = QFormLayout()
        
        font_combo = QComboBox()
        font_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Tahoma", "Verdana"])
        font_form.addRow("Font Family:", font_combo)
        
        font_layout.addLayout(font_form)
        button_tab_layout.addWidget(font_group)
        
        # Button Behavior
        behavior_group = QGroupBox("⚙️ Button Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        show_icons_check = QCheckBox("Show button icons")
        show_icons_check.setChecked(False)
        behavior_layout.addWidget(show_icons_check)
        
        adaptive_text_check = QCheckBox("Adaptive text (resize with panel)")
        adaptive_text_check.setChecked(True)
        behavior_layout.addWidget(adaptive_text_check)
        
        show_tooltips_check = QCheckBox("Show tooltips")
        show_tooltips_check.setChecked(True)
        behavior_layout.addWidget(show_tooltips_check)
        
        button_tab_layout.addWidget(behavior_group)
        
        tabs.addTab(button_tab, "🔘 Button Style")
        
        # === TAB 3: Color Scheme ===
        color_tab = QWidget()
        color_tab_layout = QVBoxLayout(color_tab)
        
        color_group = QGroupBox("🎨 Color Scheme")
        color_layout = QVBoxLayout(color_group)
        
        color_form = QFormLayout()
        
        color_scheme_combo = QComboBox()
        color_scheme_combo.addItems(["Default Pastel", "High Contrast", "Dark Theme", "Light Theme"])
        color_form.addRow("Color Scheme:", color_scheme_combo)
        
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(70, 100)
        opacity_slider.setValue(95)
        opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        opacity_slider.setTickInterval(10)
        color_form.addRow("Panel Opacity:", opacity_slider)
        
        color_layout.addLayout(color_form)
        color_tab_layout.addWidget(color_group)
        
        tabs.addTab(color_tab, "🎨 Colors")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Apply Changes")
        def apply_changes():
            # Apply settings
            width = width_spin.value()
            self._apply_right_panel_width(width)
            
            # Save settings
            if hasattr(self.main_window, 'app_settings'):
                self.main_window.app_settings.current_settings.update({
                    "right_panel_width": width,
                    "section_spacing": section_spacing_spin.value(),
                    "button_spacing": button_spacing_spin.value(),
                    "panel_margins": panel_margins_spin.value(),
                    "button_height": button_height_spin.value(),
                    "button_font_size": button_font_size_spin.value(),
                    "button_font_family": font_combo.currentText(),
                    #"show_icons": show_icons_check.isChecked(),
                    "adaptive_button_text": adaptive_text_check.isChecked(),
                    "show_tooltips": show_tooltips_check.isChecked(),
                    "color_scheme": color_scheme_combo.currentText(),
                    "panel_opacity": opacity_slider.value()
                })
                self.main_window.app_settings.save_settings()
            
            self.log_message(f"GUI settings applied: {width}px panel, {font_combo.currentText()} font")
            dialog.accept()
        
        #apply_btn.clicked.connect(apply_changes)
        button_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        def reset_defaults():
            width_spin.setValue(280)
            section_spacing_spin.setValue(6)
            button_spacing_spin.setValue(2)
            panel_margins_spin.setValue(4)
            button_height_spin.setValue(22)
            button_font_size_spin.setValue(8)
            font_combo.setCurrentText("Segoe UI")
            #show_icons_check.setChecked(False)
            adaptive_text_check.setChecked(True)
            show_tooltips_check.setChecked(True)
            color_scheme_combo.setCurrentText("Default Pastel")
            opacity_slider.setValue(95)
            update_preview()
        
        reset_btn.clicked.connect(reset_defaults)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _apply_right_panel_width(self, width):
        """Apply right panel width immediately"""
        # Update splitter sizes
        sizes = self.main_splitter.sizes()
        if len(sizes) >= 2:
            left_size = sizes[0]
            self.main_splitter.setSizes([left_size, width])
        
        # Update right panel widget constraints
        right_widget = self.main_splitter.widget(1)
        if right_widget:
            right_widget.setMaximumWidth(width + 60)  # Allow some flexibility
            right_widget.setMinimumWidth(max(180, width - 40))
    
    def create_status_bar(self):
        """Create status bar - called from imgfactory.py _create_ui method"""
        try:
            from gui.status_bar import create_status_bar
            create_status_bar(self.main_window)
            self.log_message("Status bar created successfully")
        except ImportError:
            # Fallback - create basic status bar
            self.main_window.setStatusBar(QStatusBar())
            self.main_window.statusBar().showMessage("Ready")
            self.log_message("Basic status bar created (gui.status_bar not available)")
        except Exception as e:
            self.log_message(f"Status bar creation error: {str(e)}")
    
    def show_progress(self, value, text="Working..."):
        """Show progress - compatibility method"""
        if hasattr(self.main_window, 'show_progress'):
            self.main_window.show_progress(text, 0, 100)
            self.main_window.update_progress(value)
        elif hasattr(self.main_window, 'progress_bar'):
            self.main_window.progress_bar.setValue(value)
            self.main_window.progress_bar.setVisible(value >= 0)
        else:
            # Fallback to status bar
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"{text} ({value}%)")
    
    def update_file_info(self, info_text):
        """Update file info - compatibility method"""
        if hasattr(self.main_window, 'update_img_status'):
            # Extract info from text if possible
            if "entries" in info_text:
                try:
                    count = int(info_text.split()[0])
                    self.main_window.update_img_status(entry_count=count)
                except:
                    pass
        
        # Also update info labels if available
        if hasattr(self, 'file_name_label'):
            self.update_info_labels(entry_count=info_text)
    
    def update_img_info(self, info_text):
        """Update IMG info - compatibility method (alias for update_file_info)"""
        self.update_file_info(info_text)
