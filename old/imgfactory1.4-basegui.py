# $vers" X-Seti - March 22,2022 - Img Fastory 1.4"
# $hist" Credit MexUK 2007 Img Factory 1.2"
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QTextEdit, QTableWidget, QGroupBox,
    QGridLayout, QTableWidgetItem, QMenuBar, QMenu, QStatusBar, QLabel,
    QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QFont
from app_settings_system import AppSettings, apply_theme_to_app


class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.4 [GUI layout Demo]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings

        self._create_menu()
        self._create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout will contain the main horizontal splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self._create_main_ui_with_splitters(main_layout)

    def themed_button(self, label, action_type=None, icon=None, bold=False):
        btn = QPushButton(label)
        if action_type:
            btn.setProperty("action-type", action_type)
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        if bold:
            font = btn.font()
            font.setBold(True)
            btn.setFont(font)
        return btn

    def _create_menu(self):
        menubar = self.menuBar()

        menu_names = [
            "File", "Edit", "Dat", "IMG", "Model",
            "Texture", "Collision", "Item Definition",
            "Item Placement", "Entry", "Settings", "Help"
        ]

        for name in menu_names:
            menu = menubar.addMenu(name)
            if name == "File":
                menu.addAction(QIcon.fromTheme("document-open"), "Open")
                menu.addAction(QIcon.fromTheme("window-close"), "Close")
                menu.addSeparator()
                menu.addAction(QIcon.fromTheme("application-exit"), "Exit", self.close)
            elif name == "IMG":
                menu.addAction(QIcon.fromTheme("document-save"), "Rebuild")
                menu.addAction(QIcon.fromTheme("document-merge"), "Merge")
                menu.addAction(QIcon.fromTheme("edit-cut"), "Split")
            elif name == "Settings":
                menu.addAction(QIcon.fromTheme("preferences-other"), "Preferences")
            elif name == "Help":
                menu.addAction(QIcon.fromTheme("help-about"), "About")
            else:
                placeholder = QAction("(No items yet)", self)
                placeholder.setEnabled(False)
                menu.addAction(placeholder)

    def _create_status_bar(self):
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

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
        self.main_splitter.setSizes([700, 300])
        
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
        """Create the left panel with table and log, separated by a vertical splitter"""
        
        # Vertical splitter for table vs log
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Table widget
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Offset", "Size", "Version"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self._apply_table_theme()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Set minimum size for table
        self.table.setMinimumSize(400, 200)
        
        # Log widget
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Log Output")
        self._apply_log_theme()
        
        # Set minimum size for log
        self.log.setMinimumSize(400, 100)
        
        # Add some sample content to make the splitter behavior more visible
        self._populate_sample_data()
        
        # Add widgets to left splitter
        self.left_splitter.addWidget(self.table)
        self.left_splitter.addWidget(self.log)
        
        # Set initial sizes (table takes 70%, log takes 30%)
        self.left_splitter.setSizes([400, 200])
        
        # Style the vertical splitter
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
        
        return self.left_splitter

    def _create_right_panel(self):
        """Create the right panel with controls"""
        
        # Container widget for the right panel
        right_widget = QWidget()
        right_widget.setMinimumWidth(250)
        right_layout = QVBoxLayout(right_widget)

        # IMG Section
        img_box = QGroupBox("IMG")
        img_layout = QGridLayout()
        img_buttons = [
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
        for i, (label, action_type, icon) in enumerate(img_buttons):
            btn = self.themed_button(label, action_type, icon, bold=True)
            img_layout.addWidget(btn, i // 3, i % 3)
        img_box.setLayout(img_layout)
        right_layout.addWidget(img_box)

        # Entries Section
        entries_box = QGroupBox("Entries")
        entries_layout = QGridLayout()
        entry_buttons = [
            ("Import", "import"), ("Import via", "import"), ("Update list", "update"),
            ("Export", "export"), ("Export via", "export"), ("Quick Export", "export"),
            ("Remove", "remove"), ("Remove via", "remove"), ("Dump", "update"),
            ("Rename", "convert"), ("Replace", "convert"),
            ("Select All", None), ("Select Inverse", None), ("Sort", None)
        ]
        for i, (label, action_type) in enumerate(entry_buttons):
            icon_name = "edit-copy" if "Import" in label else "edit-delete" if "Remove" in label else None
            btn = self.themed_button(label, action_type, icon_name, bold="Import" in label or "Export" in label or "Remove" in label)
            entries_layout.addWidget(btn, i // 3, i % 3)
        entries_box.setLayout(entries_layout)
        right_layout.addWidget(entries_box)

        # Filter/Search Panel
        filter_box = QGroupBox("Filter & Search")
        filter_layout = QHBoxLayout()
        filter_combo = QComboBox()
        filter_combo.addItems(["All Files", "*.txt", "*.dat", "*.img", "*.model"])
        filter_layout.addWidget(filter_combo)
        filter_input = QLineEdit("Find")
        filter_btn = QPushButton("Search")
        filter_btn.setIcon(QIcon.fromTheme("edit-find"))
        filter_layout.addWidget(filter_input)
        filter_layout.addWidget(filter_btn)
        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)
        
        # Add stretch to push controls to top
        right_layout.addStretch()

        return right_widget

    def _apply_table_theme(self):
        """Apply theme-aware styling to the table with soft pastel highlights"""
        theme = self.app_settings.get_theme()
        colors = theme["colors"]
        
        # Determine if we're using a dark or light theme
        is_dark_theme = self._is_dark_theme(colors["bg_primary"])
        
        if is_dark_theme:
            # Dark theme colors - soft pastels on dark background
            table_bg = colors["bg_secondary"]
            table_text = colors["text_primary"]
            alternate_bg = self._lighten_color(colors["bg_tertiary"], 0.1)
            selection_bg = self._add_alpha(colors["accent_primary"], 0.3)
            header_bg = colors["panel_bg"]
            header_text = colors["text_accent"]
            grid_color = self._lighten_color(colors["border"], 0.2)
        else:
            # Light theme colors - soft pastels on light background
            table_bg = colors["bg_primary"]
            table_text = colors["text_primary"]
            alternate_bg = self._darken_color(colors["bg_secondary"], 0.05)
            selection_bg = self._add_alpha(colors["accent_primary"], 0.2)
            header_bg = colors["panel_bg"]
            header_text = colors["text_accent"]
            grid_color = colors["border"]
        
        table_style = f"""
            QTableWidget {{
                background-color: {table_bg};
                color: {table_text};
                gridline-color: {grid_color};
                selection-background-color: {selection_bg};
                alternate-background-color: {alternate_bg};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                font-weight: normal;
            }}
            
            QTableWidget::item {{
                padding: 4px 8px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {selection_bg};
                color: {colors["text_primary"]};
            }}
            
            QTableWidget::item:hover {{
                background-color: {self._add_alpha(colors["accent_secondary"], 0.1)};
            }}
            
            QHeaderView::section {{
                background-color: {header_bg};
                color: {header_text};
                padding: 6px 8px;
                border: 1px solid {colors["border"]};
                border-radius: 0px;
                font-weight: bold;
                text-align: left;
            }}
            
            QHeaderView::section:hover {{
                background-color: {self._lighten_color(header_bg, 0.1)};
            }}
        """
        
        self.table.setStyleSheet(table_style)

    def _apply_log_theme(self):
        """Apply theme-aware styling to the log widget"""
        theme = self.app_settings.get_theme()
        colors = theme["colors"]
        
        # Use a slightly different background for the log to distinguish it
        is_dark_theme = self._is_dark_theme(colors["bg_primary"])
        
        if is_dark_theme:
            log_bg = self._darken_color(colors["bg_secondary"], 0.1)
            log_text = colors["text_secondary"]
        else:
            log_bg = self._lighten_color(colors["bg_secondary"], 0.05)
            log_text = colors["text_primary"]
        
        log_style = f"""
            QTextEdit {{
                background-color: {log_bg};
                color: {log_text};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                line-height: 1.2;
            }}
            
            QTextEdit:focus {{
                border-color: {colors["accent_primary"]};
            }}
        """
        
        self.log.setStyleSheet(log_style)

    def _is_dark_theme(self, color_hex):
        """Determine if a color is dark (for theme detection)"""
        # Remove # and convert to RGB
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def _lighten_color(self, color_hex, factor):
        """Lighten a hex color by a factor (0.0 to 1.0)"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, color_hex, factor):
        """Darken a hex color by a factor (0.0 to 1.0)"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _add_alpha(self, color_hex, alpha):
        """Add alpha transparency to a hex color"""
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"

    def _populate_sample_data(self):
        """Add sample data to the table and log for demonstration"""
        
        # Sample table data
        sample_data = [
            ["001", "Texture", "background.jpg", "0x1000", "2048 KB", "1.0"],
            ["002", "Model", "character.3ds", "0x2000", "512 KB", "1.2"],
            ["003", "Sound", "music.wav", "0x3000", "1024 KB", "1.1"],
            ["004", "Data", "config.dat", "0x4000", "64 KB", "1.0"],
            ["005", "Script", "init.lua", "0x5000", "16 KB", "1.3"],
            ["006", "Texture", "ground.png", "0x6000", "1536 KB", "1.0"],
            ["007", "Model", "building.obj", "0x7000", "768 KB", "1.1"],
            ["008", "Animation", "walk.ani", "0x8000", "256 KB", "1.2"],
        ]
        
        self.table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                self.table.setItem(row, col, item)
        
        # Sample log content
        log_content = """IMG Factory 1.4 - Log Output
=============================

[10:30:15] Application started
[10:30:16] Loading IMG file: sample.img
[10:30:17] Found 8 entries in archive
[10:30:18] Parsing texture files...
[10:30:19] Parsing model files...
[10:30:20] Parsing sound files...
[10:30:21] Archive loaded successfully
[10:30:22] Ready for operations

Status: Loaded 8 files (4.2 MB total)
Memory usage: 45 MB
"""
        self.log.setPlainText(log_content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = AppSettings()
    apply_theme_to_app(app, settings)
    window = ImgFactoryDemo(settings)
    window.show()
    sys.exit(app.exec())
