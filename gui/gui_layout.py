#this belongs in gui/ gui_layout.py - Version: 11
# X-Seti - JUNE28 2025 - Img Factory 1.5 - GUI Layout Module

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
                border: 1px solid #{splitter_shadow};
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
        
        # 3. BOTTOM: Status Window (log)
        status_window = self._create_status_window()
        self.left_vertical_splitter.addWidget(status_window)
        
        # Set size ratios: Info(small), File(large), Status(medium)
        # Heights: Info=80px, File=400px, Status=120px (total=600px)
        self.left_vertical_splitter.setSizes([90, 420, 90])
        
        # Style the vertical splitter handles with theme colors
        theme_colors = self._get_theme_colors("default")
        splitter_bg = theme_colors.get('splitter_color_background', '777777')
        splitter_shine = theme_colors.get('splitter_color_shine', '787878') 
        splitter_shadow = theme_colors.get('splitter_color_shadow', '757575')
        
        self.left_vertical_splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background-color: #{splitter_bg};
                border: 1px solid #{splitter_shadow};
                height: 6px;
                margin: 1px 2px;
                border-radius: 2px;
            }}
            
            QSplitter::handle:vertical:hover {{
                background-color: #{splitter_shine};
                border-color: #{splitter_shadow};
            }}
            
            QSplitter::handle:vertical:pressed {{
                background-color: #{splitter_shadow};
            }}
        """)
        
        # Prevent sections from collapsing completely
        self.left_vertical_splitter.setCollapsible(0, False)  # Info bar
        self.left_vertical_splitter.setCollapsible(1, False)  # File window
        self.left_vertical_splitter.setCollapsible(2, False)  # Status window
        
        # Add the vertical splitter to the container
        left_layout.addWidget(self.left_vertical_splitter)
        
        return left_container
    
    def _create_information_bar(self):
        """Create top information bar with file details"""
        info_bar = QGroupBox("📋 File Information")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(10, 5, 10, 5)
        
        # Current file info
        info_layout.addWidget(QLabel("File:"))
        self.current_file_label = QLabel("sample_archive.img")
        self.current_file_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        info_layout.addWidget(self.current_file_label)
        
        info_layout.addWidget(QLabel("|"))
        
        # File type
        info_layout.addWidget(QLabel("Type:"))
        self.file_type_label = QLabel("IMG Archive")
        info_layout.addWidget(self.file_type_label)
        
        info_layout.addWidget(QLabel("|"))
        
        # Entry count
        info_layout.addWidget(QLabel("Items:"))
        self.item_count_label = QLabel("4")
        info_layout.addWidget(self.item_count_label)
        
        info_layout.addWidget(QLabel("|"))
        
        # File size
        info_layout.addWidget(QLabel("Size:"))
        self.file_size_label = QLabel("512.0 KB")
        info_layout.addWidget(self.file_size_label)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
        info_layout.addWidget(self.status_indicator)
        
        # Add stretch to push everything to the left
        info_layout.addStretch()
        
        return info_bar
    
    def _create_file_window(self):
        """Create middle file window with tabs and table"""
        file_window = QWidget()
        file_layout = QVBoxLayout(file_window)
        file_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(QWidget(), "DFF")
        self.tab_widget.addTab(QWidget(), "COL")
        both_tab = QWidget()
        self.tab_widget.addTab(both_tab, "Both")
        self.tab_widget.addTab(QWidget(), "TXD")
        self.tab_widget.addTab(QWidget(), "Other")
        
        # Set "Both" as active tab
        self.tab_widget.setCurrentIndex(2)
        
        # Create main table in the "Both" tab
        both_layout = QVBoxLayout(both_tab)
        both_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "", "Filename", "Type", "Size", "Offset", "Version", "Compression", "Status"
        ])
        
        # Configure table appearance
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # Apply theme styling
        self._apply_table_theme_styling()
        
        both_layout.addWidget(self.table)
        file_layout.addWidget(self.tab_widget)
        
        # Add sample data
        self._add_sample_data()
        
        return file_window
    
    def _create_status_window(self):
        """Create bottom status/log window"""
        status_window = QGroupBox("📊 Status & Activity Log")
        status_layout = QVBoxLayout(status_window)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
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
        """Create right panel with pastel colored buttons - ONLY CHANGED SPACING"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)  # FIXED: Reduced margins slightly
        right_layout.setSpacing(6)  # FIXED: Even spacing between sections

        # IMG Section with pastel colors
        img_box = QGroupBox("IMG, COL Files")
        img_layout = QGridLayout()
        img_layout.setSpacing(2)  # FIXED: Tighter button spacing
        img_buttons_data = [
            ("New", "new", "document-new", "#EEFAFA"),      # Light Something
            ("Open", "open", "document-open", "#E3F2FD"),      # Light Blue
            ("Close", "close", "window-close", "#FFF3E0"),     # Light Orange
            ("Close All", "close_all", "edit-clear", "#FFF3E0"),
            ("Rebuild", "rebuild", "view-refresh", "#E8F5E8"),  # Light Green
            ("Rebuild As", "rebuild_as", "document-save-as", "#E8F5E8"),
            ("Rebuild All", "rebuild_all", "document-save", "#E8F5E8"),
            ("Merge", "merge", "document-merge", "#F3E5F5"),    # Light Purple
            ("Split", "split", "edit-cut", "#F3E5F5"),
            ("Convert", "convert", "transform", "#FFF8E1"),     # Light Yellow
        ]
        
        for i, (label, action_type, icon, color) in enumerate(img_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entries Section with pastel colors
        entries_box = QGroupBox("File Entries")
        entries_layout = QGridLayout()
        entries_layout.setSpacing(2)  # FIXED: Tighter button spacing
        entry_buttons_data = [
            ("Import", "import", "document-import", "#E1F5FE"),                 # Light Cyan
            ("Import via", "import_via", "document-import", "#E1F5FE"),
            ("Update list", "update", "view-refresh", "#F9FBE7"),               # Light Lime
            ("Export", "export", "document-export", "#E8F5E8"),                 # Light Green
            ("Export via", "export_via", "document-export", "#E8F5E8"),
            ("Quick Export", "quick_export", "document-send", "#E8F5E8"),
            ("Remove", "remove", "edit-delete", "#FFEBEE"),                     # Light Red
            ("Remove All", "remove_all", "edit-delete", "#FFEBEE"),
            ("Dump", "dump", "document-save", "#F3E5F5"),                       # Light Purple
            ("Rename", "rename", "edit-rename", "#FFF8E1"),                     # Light Yellow
            ("Replace", "replace", "edit-copy", "#FFF8E1"),
            ("Select All", "select_all", "edit-select-all", "#F1F8E9"),         # Light Light Green
            ("Sel Inverse", "sel_inverse", "edit-select", "#F1F8E9"),
            ("Sort", "sort", "view-sort", "#F1F8E9"),
            ("Pin selected", "pin_selected", "pin", "#E8EAF6"),                 # Light Indigo
        ]
        
        for i, (label, action_type, icon, color) in enumerate(entry_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Options Section with pastel colors
        options_box = QGroupBox("Editing Options")
        options_layout = QGridLayout()
        options_layout.setSpacing(2)  # FIXED: Tighter button spacing
        options_buttons_data = [
            ("Col Edit", "col_edit", "col-edit", "#E3F2FD"),         # Light Blue
            ("Txd Edit", "txd_edit", "txd-edit", "#F8BBD9"),         # Light Pink
            ("Dff Edit", "dff_edit", "dff-edit", "#E1F5FE"),         # Light Cyan
            ("Ipf Edit", "ipf_edit", "ipf-edit", "#FFF3E0"),         # Light Orange
            ("IDE Edit", "ide_edit", "ide-edit", "#F8BBD9"),         # Light Pink
            ("IPL Edit", "ipl_edit", "ipl-edit", "#E1F5FE"),         # Light Cyan
            ("Dat Edit", "dat_edit", "dat-edit", "#E3F2FD"),         # Light Blue
            ("Zons Cull Ed", "zones_cull", "zones-cull", "#E8F5E8"), # Light Green
            ("Weap Edit", "weap_edit", "weap-edit", "#E1F5FE"),      # Light Cyan
            ("Vehi Edit", "vehi_edit", "vehi-edit", "#E3F2FD"),      # Light Blue
            ("Radar Map", "radar_map", "radar-map", "#F8BBD9"),      # Light Pink
            ("Paths Map", "paths_map", "paths-map", "#E1F5FE"),      # Light Cyan
            ("Waterpro", "timecyc", "timecyc", "#E3F2FD"),         # Light Blue
            ("Weather", "timecyc", "timecyc", "#E0F2F1"),            # Light Teal
            ("Handling", "handling", "handling", "#E4E3ED"),         # Light Blue
            ("Objects", "ojs_breakble", "ojs-breakble", "#FFE0B2"),  # Light Deep Orange
        ]
        
        for i, (label, action_type, icon, color) in enumerate(options_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.options_buttons.append(btn)
            options_layout.addWidget(btn, i // 3, i % 3)
        
        options_box.setLayout(options_layout)
        right_layout.addWidget(options_box)

        # Filter Section
        filter_box = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(4)  # FIXED: Consistent spacing
        
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
    
    def _create_pastel_button(self, label, action_type, icon, bg_color):
        """Create a button with pastel coloring - ONLY CHANGED HEIGHT"""
        btn = QPushButton(label)
        btn.setMaximumHeight(22)  # FIXED: Compact button height
        btn.setMinimumHeight(20)  # FIXED: Minimum button height
        
        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        
        # Apply pastel styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 8pt;
                color: #333333;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color)};
                border: 1px solid #999999;
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color, 0.2)};
                border: 1px solid #666666;
            }}
            QPushButton:disabled {{
                background-color: #f0f0f0;
                color: #999999;
                border: 1px solid #dddddd;
            }}
        """)
        
        # Set button properties
        btn.setMinimumHeight(20)
        btn.setProperty("action-type", action_type)
        
        return btn
    
    def _darken_color(self, hex_color, factor=0.1):
        """Darken a hex color by a factor"""
        # Simple color darkening - remove # and convert to RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken each component
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_menu_bar(self):
        """Create the comprehensive menu bar"""
        menubar = self.main_window.menuBar()

        # All menu names from the original design
        menu_names = [
            "File", "Edit", "Dat", "IMG", "Model",
            "Texture", "Collision", "Item Definition",
            "Item Placement", "Zons/ Cull", "Entry", "Settings", "Help"
        ]

        for name in menu_names:
            menu = menubar.addMenu(name)
            
            if name == "File":
                # Create actions properly with main_window reference
                new_action = QAction("New IMG...", self.main_window)
                new_action.setIcon(QIcon.fromTheme("document-new"))
                new_action.triggered.connect(self.main_window.create_new_img)
                menu.addAction(new_action)
                
                open_action = QAction("Open IMG...", self.main_window)
                open_action.setIcon(QIcon.fromTheme("document-open"))
                open_action.triggered.connect(self.main_window.open_img_file)
                menu.addAction(open_action)
                
                col_action = QAction("Open COL...", self.main_window)
                col_action.setIcon(QIcon.fromTheme("document-open"))
                col_action.triggered.connect(self.main_window.open_file)
                menu.addAction(col_action)

                menu.addSeparator()
                
                close_action = QAction("Close", self.main_window)
                close_action.setIcon(QIcon.fromTheme("window-close"))
                close_action.triggered.connect(self.main_window.close_img_file)
                menu.addAction(close_action)
                
                menu.addSeparator()
                
                exit_action = QAction("Exit", self.main_window)
                exit_action.setIcon(QIcon.fromTheme("application-exit"))
                exit_action.triggered.connect(self.main_window.close)
                menu.addAction(exit_action)
                
            else:
                # Add placeholder for other menus
                placeholder = QAction("(No items yet)", self.main_window)
                placeholder.setEnabled(False)
                menu.addAction(placeholder)

    def create_status_bar(self):
        """Create status bar with progress indicator"""
        self.status_bar = QStatusBar()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # IMG info label
        self.img_info_label = QLabel("No IMG loaded")
        self.status_bar.addPermanentWidget(self.img_info_label)
        
        self.main_window.setStatusBar(self.status_bar)



    def connect_button_signals(self):
        """Public method to connect all button signals - call this after UI creation"""
        try:
            self._connect_all_button_signals()
            self.log_message("Button signals connected successfully")
        except Exception as e:
            self.log_message(f"Error connecting button signals: {str(e)}")

    def _connect_all_button_signals(self):
        """Connect all button signals to their respective functions"""
        # Connect IMG buttons
        self._connect_img_buttons()
        # Connect entry buttons
        self._connect_entry_buttons()
        # Connect options buttons if they exist
        if hasattr(self, 'options_buttons'):
            self._connect_options_buttons()

    def _connect_img_buttons(self):
        """Connect IMG operation buttons to their functions"""
        button_map = {
            "New": self.main_window.create_new_img,
            "Open": self.main_window.open_img_file,
            "Close": self.main_window.close_img_file,
            "Close All": self.main_window.close_all_img,
            "Rebuild": self.main_window.rebuild_img,
            "Rebuild As": self.main_window.rebuild_img_as,
            "Rebuild All": self.main_window.rebuild_all_img,
            "Merge": self.main_window.merge_img,
            "Split": self.main_window.split_img,
            "Convert": self.main_window.convert_img
        }

        connected_count = 0
        for button in self.img_buttons:
            if hasattr(button, 'full_text'):
                func = button_map.get(button.full_text)
                if func:
                    button.clicked.connect(func)
                    connected_count += 1
                    print(f"Connected IMG button: {button.full_text} -> {func.__name__}")

        self.log_message(f"Connected {connected_count} IMG buttons")

    def _connect_entry_buttons(self):
        """Connect entry operation buttons to their functions"""
        button_map = {
            "Import": self.main_window.import_files,
            "Import via": self.main_window.import_via_tool,
            "Export": self.main_window.export_selected,
            "Export via": self.main_window.export_via_tool,
            "Remove": self.main_window.remove_selected,
            "Remove All": self.main_window.remove_all_entries,
            "Update list": self.main_window.refresh_table,
            "Quick Export": self.main_window.quick_export,
            "Pin selected": self.main_window.pin_selected
        }

        connected_count = 0
        for button in self.entry_buttons:
            if hasattr(button, 'full_text'):
                func = button_map.get(button.full_text)
                if func:
                    button.clicked.connect(func)
                    connected_count += 1
                    print(f"Connected Entry button: {button.full_text} -> {func.__name__}")

        self.log_message(f"Connected {connected_count} entry buttons")

    def update_file_info(self, filename=None, file_type=None, item_count=0, file_size=0):
        """Update the file information display"""
        if filename:
            self.current_file_label.setText(filename)
            self.current_file_label.setStyleSheet("font-weight: bold; color: #2E7D32;")  # Green = loaded
            self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")  # Green dot
        else:
            self.current_file_label.setText("No file loaded")
            self.current_file_label.setStyleSheet("font-weight: bold; color: #757575;")  # Gray = no file
            self.status_indicator.setStyleSheet("color: #ff4444; font-size: 16px;")  # Red dot
        
        if file_type:
            self.file_type_label.setText(file_type)
        else:
            self.file_type_label.setText("Unknown")
            
        self.item_count_label.setText(str(item_count))
        
        if file_size > 0:
            if file_size > 1024 * 1024:
                size_text = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size > 1024:
                size_text = f"{file_size / 1024:.1f} KB"
            else:
                size_text = f"{file_size} B"
            self.file_size_label.setText(size_text)
        else:
            self.file_size_label.setText("0 KB")
    
    def show_progress(self, value, message=""):
        """Show progress in status bar"""
        if self.progress_bar:
            if value >= 0:
                self.progress_bar.setValue(value)
                self.progress_bar.setVisible(True)
            else:
                self.progress_bar.setVisible(False)
        
        if message and self.status_label:
            self.status_label.setText(message)

    def _apply_table_theme_styling(self):
        """Apply theme-aware styling to the table"""
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #e8e8e8;
                padding: 8px;
                border: 1px solid #c0c0c0;
                font-weight: bold;
            }
        """)

    def _apply_log_theme_styling(self):
        """Apply theme-aware styling to the log"""
        self.log.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
        """)

    def _get_theme_colors(self, theme_name):
        """Get theme colors from JSON theme file"""
        try:
            if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'themes'):
                theme_data = self.main_window.app_settings.themes.get(theme_name, {})
                return theme_data.get('colors', {})
        except:
            pass
        return {}

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

    def connect_table_signals(self):
        """Connect signals for table interactions"""
        if self.table:
            self.table.itemSelectionChanged.connect(self.main_window.on_selection_changed)
            self.table.itemDoubleClicked.connect(self.main_window.on_item_double_clicked)

    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.table.selectedItems()
        if selected_items:
            self.log_message(f"Selected: {selected_items[0].text()}")

    def on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        filename = self.table.item(item.row(), 0).text()
        self.log_message(f"Double-clicked: {filename}")
    
    def _get_short_text(self, full_text):
        """Get abbreviated text for buttons when space is limited"""
        abbreviations = {
            'Import': 'Imp',
            'Import via': 'Imp>',
            'Export': 'Exp',
            'Export via': 'Exp>',
            'Remove': 'Rem',
            'Remove All': 'Rem All',
            'Update list': 'Update',
            'Quick Export': 'Q-Exp',
            'Pin selected': 'Pin',
            'Rebuild': 'Build',
            'Rebuild As': 'Build>',
            'Rebuild All': 'Build All',
            'Close All': 'Close All',
            'Convert': 'Conv',
            'Col Edit': 'Col',
            'Txd Edit': 'Txd',
            'Dff Edit': 'Dff',
            'Ipf Edit': 'Ipf',
            'IDE Edit': 'IDE',
            'IPL Edit': 'IPL',
            'Dat Edit': 'Dat',
            'Zons Cull Ed': 'Zons',
            'Weap Edit': 'Weap',
            'Vehi Edit': 'Vehi',
            'Radar Map': 'Radar',
            'Paths Map': 'Paths',
            'Waterpro': 'Water',
            'Weather': 'Weath',
            'Handling': 'Hand',
            'Objects': 'Objs'
        }
        
        return abbreviations.get(full_text, full_text[:5])

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

    def _connect_signals(self):
        """Connect signals for table interactions"""
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def _add_sample_data(self):
        """Add sample data to show the interface"""
        sample_entries = [
            ("1", "player.dff", "DFF", "245 KB", "0x2000", "3.6.0.3", "None", "Ready"),
            ("2", "player.txd", "TXD", "512 KB", "0x42000", "3.6.0.3", "None", "Ready"),
            ("3", "vehicle.col", "COL", "128 KB", "0x84000", "COL 2", "None", "Ready"),
            ("4", "dance.ifp", "IFP", "1.2 MB", "0xA4000", "IFP 1", "ZLib", "Ready"),
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

    def _connect_all_button_signals(self):
        """Connect all button signals to their respective functions - ADD TO create_main_ui_with_splitters"""
        # Connect IMG buttons
        self._connect_img_buttons()
        # Connect entry buttons
        self._connect_entry_buttons()
        # Connect options buttons if they exist
        if hasattr(self, 'options_buttons'):
            self._connect_options_buttons()

    def _connect_img_buttons(self):
        """Connect IMG operation buttons to their functions"""
        button_map = {
            "New": self.main_window.create_new_img,
            "Open": self.main_window.open_img_file,
            "Close": self.main_window.close_img_file,
            "Close All": self.main_window.close_all_img,
            "Rebuild": self.main_window.rebuild_img,
            "Rebuild As": self.main_window.rebuild_img_as,
            "Rebuild All": self.main_window.rebuild_all_img,
            "Merge": self.main_window.merge_img,
            "Split": self.main_window.split_img,
            "Convert": self.main_window.convert_img
        }

        for button in self.img_buttons:
            if hasattr(button, 'full_text'):
                func = button_map.get(button.full_text)
                if func:
                    button.clicked.connect(func)

    def _connect_entry_buttons(self):
        """Connect entry operation buttons to their functions"""
        button_map = {
            "Import": self.main_window.import_files,
            "Import via": self.main_window.import_via_tool,
            "Export": self.main_window.export_selected,
            "Export via": self.main_window.export_via_tool,
            "Remove": self.main_window.remove_selected,
            "Remove All": self.main_window.remove_all_entries,
            "Update list": self.main_window.refresh_table,
            "Quick Export": self.main_window.quick_export,
            "Pin selected": self.main_window.pin_selected
        }

        for button in self.entry_buttons:
            if hasattr(button, 'full_text'):
                func = button_map.get(button.full_text)
                if func:
                    button.clicked.connect(func)

    def _connect_options_buttons(self):
        """Connect COL and editor buttons"""
        button_map = {
            "Col Edit": self.main_window.open_col_editor,
            "Txd Edit": self.main_window.open_txd_editor,
            "Dff Edit": self.main_window.open_dff_editor,
            "Ipf Edit": self.main_window.open_ipf_editor,
            "IPL Edit": self.main_window.open_ipl_editor,
            "IDE Edit": self.main_window.open_ide_editor,
            "Dat Edit": self.main_window.open_dat_editor,
            "Zons Cull Ed": self.main_window.open_zons_editor,
            "Weap Edit": self.main_window.open_weap_editor,
            "Vehi Edit": self.main_window.open_vehi_editor,
            "Radar Map": self.main_window.open_radar_map,
            "Paths Map": self.main_window.open_paths_map,
            "Waterpro": self.main_window.open_waterpro
        }

        for button in self.options_buttons:
            if hasattr(button, 'full_text'):
                func = button_map.get(button.full_text)
                if func:
                    button.clicked.connect(func)

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
        
        # Update preview when width changes
        def update_preview():
            width = width_spin.value()
            percentage = round((width / 1240) * 100)
            preview_label.setText(f"Current: {width}px ({percentage}% of window)")
        
        width_spin.valueChanged.connect(update_preview)
        update_preview()
        
        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Quick Presets:"))
        presets = [("Narrow", 200), ("Default", 240), ("Wide", 280), ("Extra Wide", 320)]
        for name, value in presets:
            btn = QPushButton(f"{name}\n({value}px)")
            btn.clicked.connect(lambda checked, v=value: (width_spin.setValue(v), update_preview()))
            presets_layout.addWidget(btn)
        presets_layout.addStretch()
        width_layout.addLayout(presets_layout)
        
        panel_layout.addWidget(width_group)
        
        # Section Spacing
        spacing_group = QGroupBox("📐 Spacing Settings")
        spacing_form = QFormLayout(spacing_group)
        
        section_spacing_spin = QSpinBox()
        section_spacing_spin.setRange(2, 20)
        section_spacing_spin.setValue(6)
        section_spacing_spin.setSuffix(" px")
        spacing_form.addRow("Section Spacing:", section_spacing_spin)
        
        button_spacing_spin = QSpinBox()
        button_spacing_spin.setRange(1, 10)
        button_spacing_spin.setValue(2)
        button_spacing_spin.setSuffix(" px")
        spacing_form.addRow("Button Spacing:", button_spacing_spin)
        
        panel_margins_spin = QSpinBox()
        panel_margins_spin.setRange(2, 15)
        panel_margins_spin.setValue(4)
        panel_margins_spin.setSuffix(" px")
        spacing_form.addRow("Panel Margins:", panel_margins_spin)
        
        panel_layout.addWidget(spacing_group)
        panel_layout.addStretch()
        
        tabs.addTab(panel_tab, "📐 Panel Layout")
        
        # === TAB 2: Button Settings ===
        button_tab = QWidget()
        button_layout = QVBoxLayout(button_tab)
        
        # Button Appearance
        button_group = QGroupBox("🔲 Button Appearance")
        button_form = QFormLayout(button_group)
        
        button_height_spin = QSpinBox()
        button_height_spin.setRange(18, 35)
        button_height_spin.setValue(22)
        button_height_spin.setSuffix(" px")
        button_form.addRow("Button Height:", button_height_spin)
        
        button_font_size_spin = QSpinBox()
        button_font_size_spin.setRange(6, 14)
        button_font_size_spin.setValue(8)
        button_font_size_spin.setSuffix(" pt")
        button_form.addRow("Font Size:", button_font_size_spin)
        
        # Font family
        font_combo = QComboBox()
        font_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Verdana", "Tahoma", "Consolas"])
        font_combo.setCurrentText("Segoe UI")
        button_form.addRow("Font Family:", font_combo)
        
        button_layout.addWidget(button_group)
        
        # Button Features
        features_group = QGroupBox("✨ Button Features")
        features_layout = QVBoxLayout(features_group)
        
        show_icons_check = QCheckBox("Show button icons")
        show_icons_check.setChecked(False)
        features_layout.addWidget(show_icons_check)
        
        adaptive_text_check = QCheckBox("Use adaptive button text (shorter text on narrow panels)")
        adaptive_text_check.setChecked(True)
        features_layout.addWidget(adaptive_text_check)
        
        show_tooltips_check = QCheckBox("Show button tooltips")
        show_tooltips_check.setChecked(True)
        features_layout.addWidget(show_tooltips_check)
        
        button_layout.addWidget(features_group)
        button_layout.addStretch()
        
        tabs.addTab(button_tab, "🔲 Buttons")
        
        # === TAB 3: Colors & Theme ===
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)
        
        # Theme selection
        theme_group = QGroupBox("🎨 Button Color Theme")
        theme_form = QFormLayout(theme_group)
        
        color_scheme_combo = QComboBox()
        color_scheme_combo.addItems(["Default Pastel", "High Contrast", "Dark Mode", "Custom"])
        theme_form.addRow("Color Scheme:", color_scheme_combo)
        
        # Opacity slider
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(50, 100)
        opacity_slider.setValue(95)
        opacity_label = QLabel("95%")
        def update_opacity(value):
            opacity_label.setText(f"{value}%")
        opacity_slider.valueChanged.connect(update_opacity)
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(opacity_slider)
        opacity_layout.addWidget(opacity_label)
        theme_form.addRow("Panel Opacity:", opacity_layout)
        
        theme_layout.addWidget(theme_group)
        theme_layout.addStretch()
        
        tabs.addTab(theme_tab, "🎨 Colors")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("👁️ Preview Changes")
        def preview_changes():
            width = width_spin.value()
            self._apply_right_panel_width(width)
            # Could apply other settings here for preview
        
        preview_btn.clicked.connect(preview_changes)
        button_layout.addWidget(preview_btn)
        
        apply_btn = QPushButton("✅ Apply & Save")
        def apply_changes():
            # Apply all settings
            width = width_spin.value()
            self._apply_right_panel_width(width)
            
            # Save all settings to app_settings
            if hasattr(self.main_window, 'app_settings'):
                settings = self.main_window.app_settings.current_settings
                settings.update({
                    "right_panel_width": width,
                    "section_spacing": section_spacing_spin.value(),
                    "button_spacing": button_spacing_spin.value(),
                    "panel_margins": panel_margins_spin.value(),
                    "button_height": button_height_spin.value(),
                    "button_font_size": button_font_size_spin.value(),
                    "button_font_family": font_combo.currentText(),
                    "show_button_icons": show_icons_check.isChecked(),
                    "adaptive_button_text": adaptive_text_check.isChecked(),
                    "show_tooltips": show_tooltips_check.isChecked(),
                    "color_scheme": color_scheme_combo.currentText(),
                    "panel_opacity": opacity_slider.value()
                })
                self.main_window.app_settings.save_settings()
            
            self.log_message(f"GUI settings applied: {width}px panel, {font_combo.currentText()} font")
            dialog.accept()
        
        apply_btn.clicked.connect(apply_changes)
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
