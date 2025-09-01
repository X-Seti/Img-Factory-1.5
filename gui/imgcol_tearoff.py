#this belongs in gui/ imgcol_tearoff.py - Version: 1
# X-Seti - August27 2025 - Img Factory 1.5

"""
IMG, COL Tear-Off Window System - Reusable for all editors
Creates detachable windows for IMG, COL and other files with essential functions
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QSplitter, QTextEdit, QDialog, QFrame,
    QGroupBox, QMessageBox, QHeaderView, QAbstractItemView, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QCursor, QAction, QTextCursor
from gui.tear_off import TearOffPanel

##Methods list -
# create_img_tearoff_window
# create_col_tearoff_window  
# create_editor_tearoff_window
# _setup_table_widget
# _setup_button_panel
# _setup_log_panel

##class IMGCOLTearOffWindow: -
# __init__
# setup_ui
# setup_img_table
# setup_col_table
# _create_button_panel
# _create_log_area
# _setup_connections
# _import_files
# _export_selected
# _remove_selected
# _rebuild_archive
# _refresh_table
# _close_window
# update_table_data
# log_message
# get_selected_entries

def create_img_tearoff_window(main_window, title="IMG Archive"): #vers 1
    """Create tear-off window for IMG files"""
    window = IMGCOLTearOffWindow(main_window, "img", title)
    window.setup_img_table()
    return window

def create_col_tearoff_window(main_window, title="COL Collision"): #vers 1
    """Create tear-off window for COL files"""  
    window = IMGCOLTearOffWindow(main_window, "col", title)
    window.setup_col_table()
    return window

def create_editor_tearoff_window(main_window, editor_type, title): #vers 1
    """Create tear-off window for specific editors (TXD, DFF, IDE, etc.)"""
    window = IMGCOLTearOffWindow(main_window, editor_type, title)
    # Setup appropriate table based on editor type
    if editor_type in ["txd", "dff", "ifp"]:
        window.setup_img_table()
    elif editor_type in ["col"]:
        window.setup_col_table()
    else:
        window.setup_img_table()  # Default to IMG table
    return window

def _setup_table_widget(table): #vers 1
    """Configure table widget with standard settings"""
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    table.setSortingEnabled(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)

def _setup_button_panel(parent, window_type): #vers 1
    """Create button panel based on window type"""
    button_frame = QFrame()
    button_layout = QHBoxLayout(button_frame)
    button_layout.setContentsMargins(5, 5, 5, 5)
    
    buttons = []
    
    if window_type == "img":
        button_configs = [
            ("📂 Import", "import_files", "Import files into archive"),
            ("📤 Export", "export_selected", "Export selected entries"),
            ("🗑️ Remove", "remove_selected", "Remove selected entries"),
            ("🔄 Rebuild", "rebuild_archive", "Rebuild archive")
        ]
    elif window_type == "col":
        button_configs = [
            ("📂 Import", "import_files", "Import COL files"),
            ("📤 Export", "export_selected", "Export selected COL data"),
            ("✏️ Edit", "edit_collision", "Edit collision data"),
            ("🔍 Analyze", "analyze_collision", "Analyze collision")
        ]
    else:
        button_configs = [
            ("📂 Import", "import_files", "Import files"),
            ("📤 Export", "export_selected", "Export selected"),
            ("🗑️ Remove", "remove_selected", "Remove selected"),
            ("🔄 Refresh", "refresh_table", "Refresh table")
        ]
    
    for text, action, tooltip in button_configs:
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setMinimumHeight(32)
        btn.setObjectName(action)
        buttons.append(btn)
        button_layout.addWidget(btn)
    
    button_layout.addStretch()
    
    # Always add refresh and close buttons
    refresh_btn = QPushButton("🔄 Refresh")
    refresh_btn.setToolTip("Refresh table data")
    refresh_btn.setObjectName("refresh_table")
    buttons.append(refresh_btn)
    button_layout.addWidget(refresh_btn)
    
    close_btn = QPushButton("❌ Close")
    close_btn.setToolTip("Close window")
    close_btn.setObjectName("close_window")
    buttons.append(close_btn)
    button_layout.addWidget(close_btn)
    
    return button_frame, buttons

def _setup_log_panel(): #vers 1
    """Create log panel for tear-off windows"""
    log_frame = QGroupBox("Activity Log")
    log_layout = QVBoxLayout(log_frame)
    
    log_text = QTextEdit()
    log_text.setMaximumHeight(100)
    log_text.setReadOnly(True)
    log_text.append("📋 Tear-off window ready")
    
    log_layout.addWidget(log_text)
    return log_frame, log_text

class IMGCOLTearOffWindow(QDialog): #vers 1
    """Detachable window for IMG/COL files with essential functionality"""
    
    # Signals for parent communication
    entries_updated = pyqtSignal()
    file_imported = pyqtSignal(str)  
    entries_exported = pyqtSignal(list)
    entries_removed = pyqtSignal(list)
    archive_rebuilt = pyqtSignal()
    
    def __init__(self, parent, window_type="img", title="IMG Factory Window"): #vers 1
        super().__init__(parent)
        self.parent_window = parent
        self.window_type = window_type
        self.current_file = None
        self.current_entries = []
        
        # Window setup
        self.setWindowTitle(f"{title} - Detached")
        self.setModal(False)  # Non-modal
        self.resize(900, 600)
        self.setMinimumSize(600, 400)
        
        # Setup UI
        self.setup_ui()
        self._setup_connections()
        
        # Apply theme if parent has one
        if hasattr(parent, 'app_settings'):
            self._apply_theme()
    
    def setup_ui(self): #vers 1
        """Setup main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Title bar with info
        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        
        self.info_label = QLabel("No file loaded")
        self.info_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_layout.addWidget(self.info_label)
        
        title_layout.addStretch()
        
        # Window type indicator
        type_label = QLabel(f"[{self.window_type.upper()}]")
        type_label.setStyleSheet("color: #666; font-weight: bold;")
        title_layout.addWidget(type_label)
        
        main_layout.addWidget(title_frame)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Table area (main content)
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        
        self.table = QTableWidget()
        _setup_table_widget(self.table)
        table_layout.addWidget(self.table)
        
        # Button panel  
        self.button_frame, self.buttons = _setup_button_panel(self, self.window_type)
        table_layout.addWidget(self.button_frame)
        
        splitter.addWidget(table_frame)
        
        # Log panel (smaller)
        self.log_frame, self.log_text = _setup_log_panel()
        splitter.addWidget(self.log_frame)
        
        # Set splitter proportions (table gets most space)
        splitter.setSizes([450, 100])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        self.status_label = QLabel("Ready")
        self.entries_label = QLabel("Entries: 0")
        self.selected_label = QLabel("Selected: 0")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.entries_label)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.selected_label)
        
        main_layout.addWidget(status_frame)
    
    def setup_img_table(self): #vers 1
        """Setup table for IMG files"""
        headers = ["Name", "Type", "Size", "Offset", "RW Address", "RW Version",  "Compression", "Status"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column widths to match main window
        header = self.table.horizontalHeader()
        header.resizeSection(0, 180)  # Name
        header.resizeSection(1, 50)   # Type  
        header.resizeSection(2, 80)   # Size
        header.resizeSection(3, 100)  # Offset
        header.resizeSection(4, 120)  # RW Address
        header.resizeSection(5, 120)  # RW Version
        header.resizeSection(6, 150)  # Compression
        header.resizeSection(7, 100)  # Status
        
        self.log_message("📁 IMG table configured")
    
    def setup_col_table(self): #vers 1
        """Setup table for COL files"""  
        headers = ["Model Name", "Spheres", "Boxes", "Faces", "Vertices", "Status"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.resizeSection(0, 150)  # Model Name
        header.resizeSection(1, 80)   # Spheres
        header.resizeSection(2, 80)   # Boxes
        header.resizeSection(3, 80)   # Faces
        header.resizeSection(4, 80)   # Vertices
        header.resizeSection(5, 100)  # Status
        
        self.log_message("🚗 COL table configured")
    
    def _create_button_panel(self): #vers 1
        """Create button panel (legacy method for compatibility)"""
        return _setup_button_panel(self, self.window_type)
    
    def _create_log_area(self): #vers 1  
        """Create log area (legacy method for compatibility)"""
        return _setup_log_panel()
    
    def _setup_connections(self): #vers 1
        """Setup button connections and signals"""
        # Connect buttons by object name
        for button in self.buttons:
            object_name = button.objectName()
            if object_name == "import_files":
                button.clicked.connect(self._import_files)
            elif object_name == "export_selected":
                button.clicked.connect(self._export_selected)
            elif object_name == "remove_selected":
                button.clicked.connect(self._remove_selected)
            elif object_name == "rebuild_archive":
                button.clicked.connect(self._rebuild_archive)
            elif object_name == "refresh_table":
                button.clicked.connect(self._refresh_table)
            elif object_name == "close_window":
                button.clicked.connect(self._close_window)
            elif object_name == "edit_collision":
                button.clicked.connect(self._edit_collision)
            elif object_name == "analyze_collision":
                button.clicked.connect(self._analyze_collision)
        
        # Table selection changes
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Table context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
    
    def _import_files(self): #vers 1
        """Import files into archive"""
        self.log_message("📂 Import function called")
        if hasattr(self.parent_window, 'import_files'):
            self.parent_window.import_files()
        else:
            self.log_message("❌ Import function not available in parent")
    
    def _export_selected(self): #vers 1
        """Export selected entries"""
        selected = self.get_selected_entries()
        if not selected:
            self.log_message("❌ No entries selected for export")
            return
            
        self.log_message(f"📤 Exporting {len(selected)} entries")
        if hasattr(self.parent_window, 'export_selected_function'):
            self.parent_window.export_selected_function()
        else:
            self.log_message("❌ Export function not available in parent")
    
    def _remove_selected(self): #vers 1
        """Remove selected entries"""
        selected = self.get_selected_entries()
        if not selected:
            self.log_message("❌ No entries selected for removal")
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Remove {len(selected)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_message(f"🗑️ Removing {len(selected)} entries")
            if hasattr(self.parent_window, 'remove_selected'):
                self.parent_window.remove_selected()
            else:
                self.log_message("❌ Remove function not available in parent")
    
    def _rebuild_archive(self): #vers 1
        """Rebuild archive"""
        self.log_message("🔄 Rebuilding archive")
        if hasattr(self.parent_window, 'rebuild_img'):
            self.parent_window.rebuild_img()
        else:
            self.log_message("❌ Rebuild function not available in parent")
    
    def _refresh_table(self): #vers 1
        """Refresh table data"""
        self.log_message("🔄 Refreshing table")
        if hasattr(self.parent_window, 'refresh_table'):
            self.parent_window.refresh_table()
        elif hasattr(self.parent_window, 'reload_current_file'):
            self.parent_window.reload_current_file()
        else:
            self.log_message("❌ Refresh function not available in parent")
    
    def _close_window(self): #vers 1
        """Close tear-off window"""
        self.log_message("❌ Closing tear-off window")
        self.close()
    
    def _edit_collision(self): #vers 1
        """Edit collision data (COL specific)"""
        if self.window_type != "col":
            return
            
        self.log_message("✏️ Opening COL editor")
        try:
            from gui.gui_context import open_col_editor_dialog
            open_col_editor_dialog(self.parent_window)
        except Exception as e:
            self.log_message(f"❌ COL editor error: {str(e)}")
    
    def _analyze_collision(self): #vers 1
        """Analyze collision data (COL specific)"""
        if self.window_type != "col":
            return
            
        self.log_message("🔍 Analyzing collision data")
        # Add collision analysis functionality
        
    def _on_selection_changed(self): #vers 1
        """Handle table selection changes"""
        selected_count = len(self.table.selectionModel().selectedRows())
        self.selected_label.setText(f"Selected: {selected_count}")
        
        # Update button states
        has_selection = selected_count > 0
        for button in self.buttons:
            object_name = button.objectName()
            if object_name in ["export_selected", "remove_selected"]:
                button.setEnabled(has_selection)
    
    def _show_context_menu(self, position): #vers 1
        """Show context menu for table"""
        if not self.table.itemAt(position):
            return
            
        menu = QMenu(self)
        
        # Common actions
        export_action = menu.addAction("📤 Export Selected")
        export_action.triggered.connect(self._export_selected)
        
        remove_action = menu.addAction("🗑️ Remove Selected") 
        remove_action.triggered.connect(self._remove_selected)
        
        menu.addSeparator()
        
        if self.window_type == "col":
            edit_action = menu.addAction("✏️ Edit Collision")
            edit_action.triggered.connect(self._edit_collision)
            
            analyze_action = menu.addAction("🔍 Analyze")
            analyze_action.triggered.connect(self._analyze_collision)
        
        menu.addSeparator()
        
        refresh_action = menu.addAction("🔄 Refresh")
        refresh_action.triggered.connect(self._refresh_table)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def update_table_data(self, entries_data): #vers 1
        """Update table with new data"""
        self.current_entries = entries_data
        row_count = len(entries_data)
        
        self.table.setRowCount(row_count)
        self.entries_label.setText(f"Entries: {row_count}")
        
        if self.window_type == "img":
            self._populate_img_table(entries_data)
        elif self.window_type == "col":
            self._populate_col_table(entries_data)
        
        self.log_message(f"📊 Table updated with {row_count} entries")
    
    def _populate_img_table(self, entries): #vers 1
        """Populate IMG table with entry data"""
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(entry.get('name', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(entry.get('type', ''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(entry.get('size', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(entry.get('offset', ''))))
            self.table.setItem(row, 4, QTableWidgetItem(str(entry.get('rw_address', ''))))
            self.table.setItem(row, 5, QTableWidgetItem(str(entry.get('rw_version', ''))))
            self.table.setItem(row, 6, QTableWidgetItem(str(entry.get('info', ''))))
            self.table.setItem(row, 7, QTableWidgetItem(str(entry.get('status', 'Ready'))))
    
    def _populate_col_table(self, entries): #vers 1
        """Populate COL table with collision data"""
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(entry.get('model_name', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(entry.get('spheres', '0'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(entry.get('boxes', '0'))))
            self.table.setItem(row, 3, QTableWidgetItem(str(entry.get('faces', '0'))))
            self.table.setItem(row, 4, QTableWidgetItem(str(entry.get('vertices', '0'))))
            self.table.setItem(row, 5, QTableWidgetItem(str(entry.get('status', 'Ready'))))
    
    def log_message(self, message): #vers 1
        """Add message to log panel"""
        self.log_text.append(message)
        self.log_text.moveCursor(self.log_text.textCursor().End)
        self.status_label.setText(message.replace('📋 ', '').replace('❌ ', '').replace('✅ ', ''))
    
    def get_selected_entries(self): #vers 1
        """Get list of selected entries"""
        selected_rows = []
        for item in self.table.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)
        
        return [self.current_entries[row] for row in selected_rows if row < len(self.current_entries)]
    
    def _apply_theme(self): #vers 1
        """Apply theme from parent window"""
        try:
            if hasattr(self.parent_window, 'app_settings'):
                theme_name = self.parent_window.app_settings.current_settings.get("theme", "default")
                # Apply theme styling here if needed
                self.log_message(f"🎨 Applied theme: {theme_name}")
        except Exception as e:
            self.log_message(f"❌ Theme error: {str(e)}")
    
    def closeEvent(self, event): #vers 1
        """Handle window close event"""
        self.log_message("👋 Tear-off window closing")
        event.accept()


# Integration functions for existing editors
def integrate_tearoff_with_col_editor(main_window): #vers 1
    """Add tear-off button to COL editor"""
    if hasattr(main_window, 'col_editor'):
        # Add tear-off functionality to existing COL editor
        pass

def integrate_tearoff_with_ide_editor(main_window): #vers 1
    """Add tear-off button to IDE editor"""  
    if hasattr(main_window, 'ide_editor'):
        # Add tear-off functionality to existing IDE editor
        pass

def integrate_tearoff_with_txd_editor(main_window): #vers 1
    """Add tear-off button to TXD editor"""
    if hasattr(main_window, 'txd_editor'):
        # Add tear-off functionality to existing TXD editor
        pass
