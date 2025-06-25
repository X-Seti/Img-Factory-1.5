# $vers" X-Seti - June04,2025 - Img Fastory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QTextEdit, QTableWidget, QGroupBox,
    QGridLayout, QTableWidgetItem, QMenuBar, QMenu, QStatusBar, QLabel,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QFont
from app_settings_system import AppSettings, apply_theme_to_app


class ImgFactoryDemo(QMainWindow):
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5 [GUI Demo]")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings

        self._create_menu()
        self._create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout(central_widget)

        self._create_main_ui()

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

    def _create_main_ui(self):
        # Left panel: Table + Log
        left_layout = QVBoxLayout()

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Offset", "Size", "Version"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setStyleSheet("QTableWidget { background-color: #ffffff; gridline-color: #d0d0d0; font-weight: bold; }")
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        left_layout.addWidget(self.table)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Log Output")
        self.log.setStyleSheet("QTextEdit { background-color: #f9f9f9; border: 1px solid #cccccc; padding: 4px; font-weight: bold; }")
        left_layout.addWidget(self.log)

        # Right panel: Controls
        right_layout = QVBoxLayout()

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
        filter_layout.addWidget(QComboBox())
        filter_layout.addWidget(QComboBox())
        filter_input = QLineEdit("Find")
        filter_btn = QPushButton("Search")
        filter_btn.setIcon(QIcon.fromTheme("edit-find"))
        filter_layout.addWidget(filter_input)
        filter_layout.addWidget(filter_btn)
        filter_box.setLayout(filter_layout)
        right_layout.addWidget(filter_box)

        self.layout.addLayout(left_layout, 2)
        self.layout.addLayout(right_layout, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = AppSettings()
    apply_theme_to_app(app, settings)
    window = ImgFactoryDemo(settings)
    window.show()
    sys.exit(app.exec())
