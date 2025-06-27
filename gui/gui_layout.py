#this belongs in gui/ gui_layout.py - version 9
# X-Seti - JUNE27 2025 - Img Factory 1.5 - GUI Layout Module

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
        
        # Set splitter proportions (80% left, 20% right) - made right panel 20% narrower  
        self.main_splitter.setSizes([960, 240])  # Was 912,288 - now even narrower right panel
        
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
        left_layout.setContentsMargins(5, 5, 5, 5)
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
        self.left_vertical_splitter.setSizes([80, 400, 120])
        
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
        self.current_file_label = QLabel("No file loaded")
        self.current_file_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        info_layout.addWidget(self.current_file_label)
        
        info_layout.addWidget(QLabel("|"))
        
        # File type
        info_layout.addWidget(QLabel("Type:"))
        self.file_type_label = QLabel("Unknown")
        info_layout.addWidget(self.file_type_label)
        
        info_layout.addWidget(QLabel("|"))
        
        # Entry/model count
        info_layout.addWidget(QLabel("Items:"))
        self.item_count_label = QLabel("0")
        info_layout.addWidget(self.item_count_label)
        
        info_layout.addWidget(QLabel("|"))
        
        # File size
        info_layout.addWidget(QLabel("Size:"))
        self.file_size_label = QLabel("0 KB")
        info_layout.addWidget(self.file_size_label)
        
        info_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #ff4444; font-size: 16px;")  # Red = no file
        info_layout.addWidget(self.status_indicator)
        
        return info_bar
    
    def _create_file_window(self):
        """Create middle file window with tabs and table"""
        file_window = QWidget()
        file_layout = QVBoxLayout(file_window)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(2)
        
        # File type tabs (DFF | COL | Both)
        self.file_type_tabs = QTabWidget()
        self.file_type_tabs.setMaximumHeight(35)  # Compact tabs
        
        # Add tabs
        self.file_type_tabs.addTab(QWidget(), "DFF")
        self.file_type_tabs.addTab(QWidget(), "COL") 
        self.file_type_tabs.addTab(QWidget(), "Both")
        
        file_layout.addWidget(self.file_type_tabs)
        
        # Main table with scrollbars
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        headers = ["Filename", "Type", "Size", "Offset", "Version", "Compression", "Status"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # Enable scrollbars
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Apply theme styling to table
        self._apply_table_theme_styling()
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        file_layout.addWidget(self.table)
        
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
        """Create right panel with pastel colored buttons"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # IMG Section with pastel colors
        img_box = QGroupBox("IMG Files")
        img_layout = QGridLayout()
        img_buttons_data = [
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
        entry_buttons_data = [
            ("Import", "import", "document-import", "#E1F5FE"),     # Light Cyan
            ("Import via", "import_via", "document-import", "#E1F5FE"),
            ("Export", "export", "document-export", "#E0F2F1"),    # Light Teal
            ("Export via", "export_via", "document-export", "#E0F2F1"),
            ("Remove", "remove", "edit-delete", "#FFEBEE"),        # Light Red
            ("Remove All", "remove_all", "edit-clear", "#FFEBEE"),
            ("Update list", "update", "view-refresh", "#F9FBE7"),  # Light Lime
            ("Quick Export", "quick_export", "document-export", "#E0F2F1"),
            ("Pin selected", "pin", "view-pin", "#FCE4EC"),        # Light Pink
        ]
        
        for i, (label, action_type, icon, color) in enumerate(entry_buttons_data):
            btn = self._create_pastel_button(label, action_type, icon, color)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Options Section - Third button group
        options_box = QGroupBox("Editing Options")
        options_layout = QGridLayout()
        options_buttons_data = [
            ("Col Edit", "col_edit", "edit-col", "#FFE0B2"),        # Light Deep Orange
            ("Txd Edit", "txd_edit", "edit-txd", "#E8EAF6"),        # Light Indigo
            ("Dff Edit", "dff_edit", "edit-dff", "#F1F8E9"),        # Light Light Green
            ("Ipf Edit", "ipf_edit", "edit-ipf", "#FFF3E0"),        # Light Orange
            ("IPL Edit", "ipl_edit", "edit-ipl", "#FFEBEE"),        # Light Red
            ("IDE Edit", "ide_edit", "edit-ide", "#E0F2F1"),        # Light Teal
            ("Dat Edit", "dat_edit", "dat-editor", "#F3E5F5"),      # Light Purple
            ("Zons Edit", "zons_edit", "zon-editor", "#E1F5FE"),    # Light Cyan
            ("Weap Edit", "weap_edit", "weap-editor", "#FFF8E1"),   # Light Yellow
            ("Vehi Edit", "vehi_edit", "vehi-editor", "#E8F5E8"),   # Light Green
            ("Radar Map", "radar_map", "radar-map", "#FCE4EC"),     # Light Pink
            ("Paths Map", "paths_map", "paths-map", "#F9FBE7"),     # Light Lime
            ("Waterpro", "waterpro", "waterpro", "#E3F2FD"),        # Light Blue
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
        """Create a button with pastel coloring"""
        btn = QPushButton(label)
        
        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        
        # Apply pastel styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
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
        btn.setMinimumHeight(30)
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
            "Item Placement", "Entry", "Settings", "Help"
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
                col_action.triggered.connect(self.main_window.open_col_file)
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
                
            elif name == "Edit":
                undo_action = QAction("Undo", self.main_window)
                undo_action.setIcon(QIcon.fromTheme("edit-undo"))
                menu.addAction(undo_action)
                
                redo_action = QAction("Redo", self.main_window)
                redo_action.setIcon(QIcon.fromTheme("edit-redo"))
                menu.addAction(redo_action)
                
                menu.addSeparator()
                
                copy_action = QAction("Copy", self.main_window)
                copy_action.setIcon(QIcon.fromTheme("edit-copy"))
                menu.addAction(copy_action)
                
                paste_action = QAction("Paste", self.main_window)
                paste_action.setIcon(QIcon.fromTheme("edit-paste"))
                menu.addAction(paste_action)
                
            elif name == "IMG":
                rebuild_action = QAction("Rebuild", self.main_window)
                rebuild_action.setIcon(QIcon.fromTheme("document-save"))
                rebuild_action.triggered.connect(self.main_window.rebuild_img)
                menu.addAction(rebuild_action)
                
                rebuild_as_action = QAction("Rebuild As...", self.main_window)
                rebuild_as_action.setIcon(QIcon.fromTheme("document-save-as"))
                rebuild_as_action.triggered.connect(self.main_window.rebuild_img_as)
                menu.addAction(rebuild_as_action)
                
                menu.addSeparator()
                
                merge_action = QAction("Merge IMG Files", self.main_window)
                merge_action.setIcon(QIcon.fromTheme("document-merge"))
                menu.addAction(merge_action)
                
                split_action = QAction("Split IMG File", self.main_window)
                split_action.setIcon(QIcon.fromTheme("edit-cut"))
                menu.addAction(split_action)
                
                menu.addSeparator()
                
                properties_action = QAction("IMG Properties", self.main_window)
                properties_action.setIcon(QIcon.fromTheme("dialog-information"))
                menu.addAction(properties_action)
                
            elif name == "Entry":
                import_action = QAction("Import Files...", self.main_window)
                import_action.setIcon(QIcon.fromTheme("go-down"))
                import_action.triggered.connect(self.main_window.import_files)
                menu.addAction(import_action)
                
                export_selected_action = QAction("Export Selected...", self.main_window)
                export_selected_action.setIcon(QIcon.fromTheme("go-up"))
                export_selected_action.triggered.connect(self.main_window.export_selected)
                menu.addAction(export_selected_action)
                
                export_all_action = QAction("Export All...", self.main_window)
                export_all_action.setIcon(QIcon.fromTheme("go-up"))
                export_all_action.triggered.connect(self.main_window.export_all)
                menu.addAction(export_all_action)
                
                menu.addSeparator()
                
                remove_action = QAction("Remove Selected", self.main_window)
                remove_action.setIcon(QIcon.fromTheme("list-remove"))
                remove_action.triggered.connect(self.main_window.remove_selected)
                menu.addAction(remove_action)
                
                rename_action = QAction("Rename Entry", self.main_window)
                rename_action.setIcon(QIcon.fromTheme("edit"))
                menu.addAction(rename_action)
                
            elif name == "Settings":
                preferences_action = QAction("Preferences...", self.main_window)
                preferences_action.setIcon(QIcon.fromTheme("preferences-other"))
                preferences_action.triggered.connect(self.main_window.show_settings)
                menu.addAction(preferences_action)
                
                themes_action = QAction("Themes...", self.main_window)
                themes_action.setIcon(QIcon.fromTheme("applications-graphics"))
                themes_action.triggered.connect(self.main_window.show_theme_settings)
                menu.addAction(themes_action)
                
                menu.addSeparator()
                
                templates_action = QAction("Manage Templates...", self.main_window)
                templates_action.setIcon(QIcon.fromTheme("folder"))
                templates_action.triggered.connect(self.main_window.manage_templates)
                menu.addAction(templates_action)
                
            elif name == "Help":
                guide_action = QAction("User Guide", self.main_window)
                guide_action.setIcon(QIcon.fromTheme("help-contents"))
                menu.addAction(guide_action)
                
                about_action = QAction("About IMG Factory", self.main_window)
                about_action.setIcon(QIcon.fromTheme("help-about"))
                about_action.triggered.connect(self.main_window.show_about)
                menu.addAction(about_action)
                
            else:
                # Add placeholder for unimplemented menus
                placeholder = QAction("(Coming Soon)", self.main_window)
                placeholder.setEnabled(False)
                menu.addAction(placeholder)

    def create_status_bar(self):
        """Create the status bar with progress indicator"""
        # Use Qt's built-in statusBar() method
        self.status_bar = self.main_window.statusBar()
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        self.img_info_label = QLabel("No IMG loaded")
        self.status_bar.addPermanentWidget(self.img_info_label)

    def _apply_table_theme_styling(self):
        """Apply theme-aware styling to table"""
        # Check if we have theme settings
        theme_name = "default"
        if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'current_settings'):
            theme_name = self.main_window.app_settings.current_settings.get('theme', 'default')
        
        # Get theme colors from JSON if available
        theme_colors = self._get_theme_colors(theme_name)
        
        if theme_name == "LCARS":
            # LCARS theme styling
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #000000;
                    color: #ff9900;
                    gridline-color: #ff9900;
                    font-weight: bold;
                    border: 2px solid #ff9900;
                    selection-background-color: #ff6600;
                    selection-color: #000000;
                    alternate-background-color: #1a1a1a;
                }
                QHeaderView::section {
                    background-color: #ff9900;
                    color: #000000;
                    font-weight: bold;
                    border: 1px solid #ff6600;
                    padding: 6px;
                }
                QScrollBar:vertical {
                    background-color: #2a2a2a;
                    border: 1px solid #ff9900;
                    width: 16px;
                    border-radius: 8px;
                }
                QScrollBar::handle:vertical {
                    background-color: #ff9900;
                    border: 1px solid #ff6600;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #ffaa00;
                }
                QScrollBar:horizontal {
                    background-color: #2a2a2a;
                    border: 1px solid #ff9900;
                    height: 16px;
                    border-radius: 8px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #ff9900;
                    border: 1px solid #ff6600;
                    border-radius: 6px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #ffaa00;
                }
            """)
        elif theme_name == "dark":
            # Dark theme styling
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    gridline-color: #555555;
                    font-weight: bold;
                    border: 1px solid #555555;
                    selection-background-color: #0078d4;
                    selection-color: #ffffff;
                    alternate-background-color: #353535;
                }
                QHeaderView::section {
                    background-color: #404040;
                    color: #ffffff;
                    font-weight: bold;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                QScrollBar:vertical {
                    background-color: #404040;
                    border: 1px solid #555555;
                    width: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical {
                    background-color: #606060;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #707070;
                }
                QScrollBar:horizontal {
                    background-color: #404040;
                    border: 1px solid #555555;
                    height: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #606060;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #707070;
                }
            """)
        else:
            # Default/light theme styling with improved selection visibility
            splitter_bg = theme_colors.get('splitter_color_background', '777777')
            splitter_shine = theme_colors.get('splitter_color_shine', '787878')
            splitter_shadow = theme_colors.get('splitter_color_shadow', '757575')
            
            self.table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: #ffffff;
                    color: #333333;
                    gridline-color: #e0e0e0;
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    selection-background-color: #0078d4;
                    selection-color: #ffffff;
                    alternate-background-color: #f8f9fa;
                }}
                QHeaderView::section {{
                    background-color: #f5f5f5;
                    color: #333333;
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    padding: 4px;
                }}
                QScrollBar:vertical {{
                    background-color: #{splitter_bg};
                    border: 1px solid #{splitter_shadow};
                    width: 14px;
                    border-radius: 7px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #{splitter_shine};
                    border: 1px solid #{splitter_shadow};
                    border-radius: 5px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: #a0a0a0;
                }}
                QScrollBar::handle:vertical:pressed {{
                    background-color: #808080;
                }}
                QScrollBar:horizontal {{
                    background-color: #{splitter_bg};
                    border: 1px solid #{splitter_shadow};
                    height: 14px;
                    border-radius: 7px;
                }}
                QScrollBar::handle:horizontal {{
                    background-color: #{splitter_shine};
                    border: 1px solid #{splitter_shadow};
                    border-radius: 5px;
                    min-width: 20px;
                }}
                QScrollBar::handle:horizontal:hover {{
                    background-color: #a0a0a0;
                }}
                QScrollBar::handle:horizontal:pressed {{
                    background-color: #808080;
                }}
            """)
    
    def _apply_log_theme_styling(self):
        """Apply theme-aware styling to log widget"""
        # Check if we have theme settings
        theme_name = "default"
        if hasattr(self.main_window, 'app_settings') and hasattr(self.main_window.app_settings, 'current_settings'):
            theme_name = self.main_window.app_settings.current_settings.get('theme', 'default')
        
        if theme_name == "LCARS":
            # LCARS theme styling for log
            self.log.setStyleSheet("""
                QTextEdit {
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 9pt;
                    background-color: #000000;
                    color: #ff9900;
                    border: 2px solid #ff9900;
                }
                QScrollBar:vertical {
                    background-color: #2a2a2a;
                    border: 1px solid #ff9900;
                    width: 16px;
                    border-radius: 8px;
                }
                QScrollBar::handle:vertical {
                    background-color: #ff9900;
                    border: 1px solid #ff6600;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #ffaa00;
                }
                QScrollBar:horizontal {
                    background-color: #2a2a2a;
                    border: 1px solid #ff9900;
                    height: 16px;
                    border-radius: 8px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #ff9900;
                    border: 1px solid #ff6600;
                    border-radius: 6px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #ffaa00;
                }
            """)
        elif theme_name == "dark":
            # Dark theme styling for log
            self.log.setStyleSheet("""
                QTextEdit {
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 9pt;
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QScrollBar:vertical {
                    background-color: #404040;
                    border: 1px solid #555555;
                    width: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical {
                    background-color: #606060;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #707070;
                }
                QScrollBar:horizontal {
                    background-color: #404040;
                    border: 1px solid #555555;
                    height: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #606060;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #707070;
                }
            """)
        else:
            # Default/light theme styling for log
            self.log.setStyleSheet("""
                QTextEdit {
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 9pt;
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    color: #333333;
                }
                QScrollBar:vertical {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    width: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical {
                    background-color: #c0c0c0;
                    border: 1px solid #999999;
                    border-radius: 5px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #a0a0a0;
                }
                QScrollBar::handle:vertical:pressed {
                    background-color: #808080;
                }
                QScrollBar:horizontal {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    height: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #c0c0c0;
                    border: 1px solid #999999;
                    border-radius: 5px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #a0a0a0;
                }
                QScrollBar::handle:horizontal:pressed {
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
            # Options section abbreviations
            'Col Edit': 'COL',
            'Txd Edit': 'TXD',
            'Dff Edit': 'DFF',
            'Ipf Edit': 'IPF',
            'IPL Edit': 'IPL',
            'IDE Edit': 'IDE',
            'Dat Edit': 'DAT',
            'Zons Edit': 'ZON',
            'Weap Edit': 'WEAP',
            'Vehi Edit': 'VEHI',
            'Radar Map': 'RADAR',
            'Paths Map': 'PATH',
            'Waterpro': 'WATER'
        }
        
        return abbreviations.get(full_text, full_text[:5])
    
    def adapt_buttons_to_width(self, width):
        """Adapt button text based on available width"""
        all_buttons = self.img_buttons + self.entry_buttons + self.options_buttons
        
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
    
    def add_sample_data(self):
        """Add sample data to show the interface"""
        if not self.table:
            return
            
        sample_entries = [
            ("player.dff", "DFF", "245 KB", "0x2000", "3.6.0.3", "None", "Ready"),
            ("player.txd", "TXD", "512 KB", "0x42000", "3.6.0.3", "None", "Ready"),
            ("vehicle.col", "COL", "128 KB", "0x84000", "COL 2", "None", "Ready"),
            ("dance.ifp", "IFP", "1.2 MB", "0xA4000", "IFP 1", "ZLib", "Ready"),
        ]
        
        self.table.setRowCount(len(sample_entries))
        for row, entry_data in enumerate(sample_entries):
            for col, value in enumerate(entry_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
        
        # Update info bar with sample data
        self.update_file_info("sample_archive.img", "IMG Archive", 4, 1024*512)  # 512KB sample
    
    def update_file_info(self, file_path=None, file_type=None, item_count=0, file_size=0):
        """Update the information bar with current file details"""
        if file_path:
            import os
            filename = os.path.basename(file_path)
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
    
    def log_message(self, message):
        """Log a message to the log widget"""
        if self.log:
            import time
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log.append(formatted_message)
            # Auto-scroll to bottom
            self.log.ensureCursorVisible()

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
