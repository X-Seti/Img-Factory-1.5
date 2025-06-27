#this belongs in gui/ gui_layout.py
# X-Seti - JUNE27 2025 - Img Factory 1.5 - GUI Layout Module

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class IMGFactoryGUILayout:
    """Handles the complete GUI layout for IMG Factory 1.5"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.table = None
        self.log = None
        self.main_splitter = None
        self.img_buttons = []
        self.entry_buttons = []
    
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
    
        """
    def _create_ui(self):
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
        #Create advanced UI with all features
        # Create menu and status bars FIRST
        self._create_menu_bar()
        self._create_status_bar()

        # Then create main UI
        self._create_main_ui_with_splitters(main_layout)

        """


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

    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)

        # Use GUI layout's adaptive method
        if hasattr(self.gui_layout, 'main_splitter'):
            sizes = self.gui_layout.main_splitter.sizes()
            if len(sizes) > 1:
                right_panel_width = sizes[1]
                self.gui_layout.adapt_buttons_to_width(right_panel_width)

    def _connect_signals(self):
        """Connect signals for table interactions"""
        if self.gui_layout.table:
            self.gui_layout.table.itemSelectionChanged.connect(self.on_selection_changed)
            self.gui_layout.table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.gui_layout.table.selectedItems()
        if selected_items:
            self.log_message(f"Selected: {selected_items[0].text()}")

    def on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        filename = self.gui_layout.table.item(item.row(), 0).text()
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
