#this belongs in gui/ gui_layout.py
# X-Seti - JUNE27 2025 - Img Factory 1.5 - GUI Layout Module

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QMenuBar, QStatusBar, QProgressBar
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
        # Status bar components
        self.status_bar = None
        self.status_label = None
        self.progress_bar = None
        self.img_info_label = None
    
    def create_main_ui_with_splitters(self, main_layout):
        """Create the main UI with splitter layout - 100% intact from original"""
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel (70% width)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Table widget for IMG contents
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        headers = ["Filename", "Type", "Size", "Offset", "Version", "Compression", "Status"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setStyleSheet("QTableWidget { background-color: #ffffff; gridline-color: #d0d0d0; font-weight: bold; }")
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        left_layout.addWidget(self.table)

        # Log output
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Log Output")
        self.log.setStyleSheet("QTextEdit { background-color: #f9f9f9; border: 1px solid #cccccc; padding: 4px; font-weight: bold; }")
        left_layout.addWidget(self.log)

        # Right panel (30% width)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # IMG Section
        img_box = QGroupBox("IMG")
        img_layout = QGridLayout()
        img_buttons_data = [
            ("Open", None, "document-open"),
            ("Close", None, "window-close"),
            ("Close All", None, "edit-clear"),
            ("Rebuild", None, "view-refresh"),
            ("Rebuild As", None, "document-save-as"),
            ("Rebuild All", None, "document-save"),
            ("Merge", None, "document-merge"),
            ("Split", None, "edit-cut"),
            ("Convert", "convert", "transform"),
        ]
        
        for i, (label, action_type, icon) in enumerate(img_buttons_data):
            btn = self.main_window.themed_button(label, action_type, icon, bold=True)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.img_buttons.append(btn)
            img_layout.addWidget(btn, i // 3, i % 3)
        
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entries Section
        entries_box = QGroupBox("Entries")
        entries_layout = QGridLayout()
        entry_buttons_data = [
            ("Import", "import", "document-import"),
            ("Import via", "import", "document-import"),
            ("Export", "export", "document-export"),
            ("Export via", "export", "document-export"),
            ("Remove", "remove", "edit-delete"),
            ("Remove All", "remove", "edit-clear"),
            ("Update list", "update", "view-refresh"),
            ("Quick Export", "export", "document-export"),
            ("Pin selected", None, "view-pin"),
        ]
        
        for i, (label, action_type, icon) in enumerate(entry_buttons_data):
            btn = self.main_window.themed_button(label, action_type, icon)
            btn.full_text = label
            btn.short_text = self._get_short_text(label)
            self.entry_buttons.append(btn)
            entries_layout.addWidget(btn, i // 3, i % 3)
        
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Filter Section
        filter_box = QGroupBox("Filter")
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

        # Add panels to splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (70% left, 30% right)
        self.main_splitter.setSizes([840, 360])
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)
    
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

    def apply_table_theme(self):
        """Apply theme styling to the table"""
        if hasattr(self.main_window.app_settings, 'current_settings'):
            theme_name = self.main_window.app_settings.current_settings.get('theme', 'IMG_Factory')
            
            if theme_name == "LCARS":
                self.table.setStyleSheet("""
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
                self.table.setStyleSheet("""
                    QTableWidget {
                        gridline-color: #dddddd;
                        background-color: #ffffff;
                        alternate-background-color: #f8f9fa;
                        selection-background-color: #e3f2fd;
                    }
                    QHeaderView::section {
                        background-color: #f5f5f5;
                        color: #333333;
                        font-weight: bold;
                        border: 1px solid #dddddd;
                    }
                """)

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
            'Convert': 'Conv'
        }
        
        return abbreviations.get(full_text, full_text[:5])
    
    def adapt_buttons_to_width(self, width):
        """Adapt button text based on available width"""
        all_buttons = self.img_buttons + self.entry_buttons
        
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
    
    def log_message(self, message):
        """Log a message to the log widget"""
        if self.log:
            self.log.append(message)

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
    
    def update_img_info(self, info_text):
        """Update IMG information in status bar"""
        if self.img_info_label:
            self.img_info_label.setText(info_text)
