#this belongs in gui/ gui_layout.py - Version: 12
# X-Seti - JULY03 2025 - Img Factory 1.5 - GUI Layout Module - Fixed Button Connections

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QMenuBar, QStatusBar, QProgressBar, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon

class IMGFactoryGUILayout:
    """Handles the complete GUI layout for IMG Factory 1.5"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.table = None
        self.log = None
        self.main_splitter = None
        self.img_buttons = []
        self.entry_buttons = []
        self.options_buttons = []  # Add options buttons list
        # Status bar components
        self.status_bar = None
        self.status_label = None
        self.progress_bar = None
        self.img_info_label = None
    
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
        splitter_bg = theme_colors.get('splitter_color_background', '777777')
        splitter_shine = theme_colors.get('splitter_color_shine', '787878')
        splitter_shadow = theme_colors.get('splitter_color_shadow', '757575')
        
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
        """Create left panel with 3 sections: Info Bar, File Window, Status Window"""
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(3, 3, 3, 3)
        left_layout.setSpacing(0)  # No spacing - splitter handles this
        
        # Create vertical splitter for the 3 sections
        self.left_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 1. TOP: Information Bar (file details)
        info_bar = self._create_information_bar()
        self.left_vertical_splitter.addWidget(info_bar)
        
        # 2. MIDDLE: File Window (table with tabs)
        file_window = self._create_file_window()
        self.left_vertical_splitter.addWidget(file_window)
        
        # 3. BOTTOM: Status Window (log and status)
        status_window = self._create_status_window()
        self.left_vertical_splitter.addWidget(status_window)
        
        # Set section proportions: Info(80px), File(700px), Status(200px)
        self.left_vertical_splitter.setSizes([80, 700, 200])
        
        # Prevent sections from collapsing completely
        self.left_vertical_splitter.setCollapsible(0, False)  # Info bar
        self.left_vertical_splitter.setCollapsible(1, False)  # File window
        self.left_vertical_splitter.setCollapsible(2, False)  # Status window
        
        # Apply theme styling to vertical splitter
        self._apply_vertical_splitter_theme()
        
        left_layout.addWidget(self.left_vertical_splitter)
        
        return left_container
    
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
            ("New", "new", "document-new", "#EEFAFA", "create_new_img"),
            ("Open", "open", "document-open", "#E3F2FD", "open_img_file"),
            ("Close", "close", "window-close", "#FFF3E0", "close_img_file"),
            ("Close All", "close_all", "edit-clear", "#FFF3E0", "close_all_img"),
            ("Rebuild", "rebuild", "view-refresh", "#E8F5E8", "rebuild_img"),
            ("Rebuild As", "rebuild_as", "document-save-as", "#E8F5E8", "rebuild_img_as"),
            ("Rebuild All", "rebuild_all", "document-save", "#E8F5E8", "rebuild_all_img"),
            ("Merge", "merge", "document-merge", "#F3E5F5", "merge_img"),
            ("Split", "split", "edit-cut", "#F3E5F5", "split_img"),
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
            ("Update list", "update", "view-refresh", "#F9FBE7", "refresh_table"),
            ("Export", "export", "document-export", "#E8F5E8", "export_selected"),
            ("Export via", "export_via", "document-export", "#E8F5E8", "export_selected_via"),
            ("Quick Export", "quick_export", "document-send", "#E8F5E8", "quick_export_selected"),
            ("Remove", "remove", "edit-delete", "#FFEBEE", "remove_selected"),
            ("Remove All", "remove_all", "edit-delete", "#FFEBEE", "remove_all_entries"),
            ("Dump", "dump", "document-save", "#F3E5F5", "dump_entries"),
            ("Rename", "rename", "edit-rename", "#FFF8E1", "rename_selected"),
            ("Replace", "replace", "edit-copy", "#FFF8E1", "replace_selected"),
            ("Select All", "select_all", "edit-select-all", "#F1F8E9", "select_all_entries"),
            ("Sel Inverse", "sel_inverse", "edit-select", "#F1F8E9", "select_inverse"),
            ("Sort", "sort", "view-sort", "#F1F8E9", "sort_entries"),
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

        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))

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
    
    def _get_short_text(self, text):
        """Get shortened text for responsive buttons"""
        short_map = {
            "Import": "Imp",
            "Export": "Exp", 
            "Remove": "Rem",
            "Update list": "Upd",
            "Select All": "Sel A",
            "Sel Inverse": "Sel I",
            "Quick Export": "Q.Exp",
            "Rebuild As": "Reb A",
            "Rebuild All": "Reb A",
            "Remove All": "Rem A",
            "Close All": "Cls A",
            "Pin selected": "Pin",
            "Zons Cull Ed": "Zons",
            "Radar Map": "Radar",
            "Paths Map": "Paths",
            "Col Edit": "Col",
            "Txd Edit": "Txd",
            "Dff Edit": "Dff",
            "Ipf Edit": "Ipf",
            "IDE Edit": "IDE",
            "IPL Edit": "IPL",
            "Dat Edit": "Dat",
            "Weap Edit": "Weap",
            "Vehi Edit": "Vehi",
            "Peds Edit": "Peds",
            "Waterpro": "Water",
            "Weather": "Weath",
            "Handling": "Hand",
            "Objects": "Objs"
        }
        return short_map.get(text, text[:6])
    
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
        splitter_bg = theme_colors.get('splitter_color_background', '777777')
        
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
            'splitter_color_background': '777777',
            'splitter_color_shine': '787878',
            'splitter_color_shadow': '757575'
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

    def _add_sample_data(self):
        """Add sample data to show the interface"""
        sample_entries = [
            ("test.dff", "DFF", "245 KB", "0x2000", "3.4.0.2", "None", ""),
            ("test.txd", "TXD", "512 KB", "0x42000", "3.4.0.2", "None", ""),
            ("test.col", "COL", "128 KB", "0x84000", "COL 2", "None", ""),
            ("test.txd", "txd", "1.2 MB", "0xA4000", "3.4.0.2", "None", ""),
        ]
        
        self.table.setRowCount(len(sample_entries))
        for row, entry_data in enumerate(sample_entries):
            for col, value in enumerate(entry_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        
        self.log_message("Interface loaded with sample data. Open an IMG file to see real content.")

    def add_sample_data(self):
        """Public method to add sample data - calls private method"""
        self._add_sample_data()

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
                    "show_icons": show_icons_check.isChecked(),
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
            show_icons_check.setChecked(False)
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
    
    def update_info_labels(self, file_name="No file loaded", entry_count=0, file_size=0, format_version="Unknown"):
        """Update information bar labels"""
        if hasattr(self, 'file_name_label'):
            self.file_name_label.setText(f"File: {file_name}")
        if hasattr(self, 'entry_count_label'):
            self.entry_count_label.setText(f"Entries: {entry_count}")
        if hasattr(self, 'file_size_label'):
            self.file_size_label.setText(f"Size: {file_size} bytes")
        if hasattr(self, 'format_version_label'):
            self.format_version_label.setText(f"Format: {format_version}")
    
    def enable_buttons_by_context(self, img_loaded=False, entries_selected=False):
        """Enable/disable buttons based on context"""
        # IMG buttons that need an IMG loaded
        img_dependent_buttons = ["close", "rebuild", "rebuild_as", "rebuild_all", "merge", "split", "convert"]
        
        # Entry buttons that need entries selected
        selection_dependent_buttons = ["export", "export_via", "quick_export", "remove", "rename", "replace", "pin_selected"]
        
        # Update IMG buttons
        for btn in self.img_buttons:
            if hasattr(btn, 'full_text'):
                button_action = btn.full_text.lower().replace(" ", "_")
                if button_action in img_dependent_buttons:
                    btn.setEnabled(img_loaded)
        
        # Update Entry buttons
        for btn in self.entry_buttons:
            if hasattr(btn, 'full_text'):
                button_action = btn.full_text.lower().replace(" ", "_")
                if button_action in selection_dependent_buttons:
                    btn.setEnabled(entries_selected and img_loaded)
                elif button_action in ["import", "import_via", "update_list", "select_all", "sel_inverse", "sort"]:
                    btn.setEnabled(img_loaded)
    
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
