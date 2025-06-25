#this belongs in root /imgfactory.py

#!/usr/bin/env python3
"""
X-Seti - June25 2025 - IMG Factory 1.5
Complete IMG Factory application with modular GUI system
Features: Tear-off panels, customizable buttons, modular menus
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QProgressBar, QLabel, QPushButton, QFileDialog,
    QMessageBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenuBar, QMenu, QStatusBar, QSizePolicy, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QAction, QIcon, QFont, QDragEnterEvent, QDropEvent

print("Loading IMG Factory with modular GUI system...")

# Import required components - no fallbacks
from App_settings_system import AppSettings, apply_theme_to_app
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.buttons import ButtonPresetManager, ButtonFactory
from gui.panels import PanelManager, ButtonPanel, FilterSearchPanel
from gui.menu import IMGFactoryMenuBar, ContextMenuManager
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
from components.img_combined_open_dialog import show_combined_open_dialog, open_single_img_file

print("✓ All components imported successfully")


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit(10)
            img_file = IMGFile(self.file_path)
            
            self.progress.emit(30)
            if not img_file.open():
                self.error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress.emit(100)
            self.finished.emit(img_file)
            
        except Exception as e:
            self.error.emit(f"Error loading IMG file: {str(e)}")


class IMGFactory(QMainWindow):
    """Main IMG Factory application with modular GUI"""
    
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings
        
        # Current IMG file
        self.current_img: IMGFile = None
        self.load_thread: IMGLoadThread = None

        # Initialize modular GUI components
        self.preset_manager = ButtonPresetManager()
        self.panel_manager = None  # Will be created after UI
        
        self._create_ui()
        self._create_status_bar()
        
        # Create menu system
        self.menu_bar = IMGFactoryMenuBar(self, self.panel_manager)
        self.context_menu_manager = ContextMenuManager(self)
        self._setup_menu_callbacks()

    def _create_ui(self):
        """Create the main UI with modular panel system"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Main horizontal splitter (left content | right panels)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Table and Log with vertical splitter
        left_widget = self._create_left_panel()
        
        # Right side: Modular panels
        right_widget = self._create_modular_right_panel()
        
        # Add widgets to main splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        
        # Set initial sizes (left panel 70%, right panel 30%)
        self.main_splitter.setSizes([770, 330])
        
        # Prevent panels from collapsing
        self.main_splitter.setChildrenCollapsible(False)
        
        main_layout.addWidget(self.main_splitter)

    def _create_modular_right_panel(self):
        """Create right panel with modular tear-off panels"""
        # Create panel manager with callbacks
        callbacks = self._get_button_callbacks()
        self.panel_manager = PanelManager(self, self.preset_manager)
        
        # Create default panels
        panels = self.panel_manager.create_default_panels(callbacks)
        
        # Create container for panels
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(5)
        
        # Add panels to layout
        for panel_id in ["img_ops", "entries_ops", "filter_search"]:
            if panel_id in panels:
                right_layout.addWidget(panels[panel_id])
        
        right_layout.addStretch()
        
        # Connect filter panel signals
        if "filter_search" in panels:
            filter_panel = panels["filter_search"]
            filter_panel.filter_changed.connect(self._on_filter_changed)
            filter_panel.search_requested.connect(self._on_search_requested)
        
        return right_widget

    def _create_left_panel(self):
        """Create left panel with IMG table and log"""
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Vertical splitter for table and log
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # IMG entries table
        self._create_entries_table()
        self.left_splitter.addWidget(self.table)
        
        # Log section
        self.log = QTextEdit()
        self.log.setMaximumHeight(150)
        self.log.setPlaceholderText("Activity log will appear here...")
        self.left_splitter.addWidget(self.log)
        
        # Set sizes (table 80%, log 20%)
        self.left_splitter.setSizes([400, 100])
        
        left_layout.addWidget(self.left_splitter)
        
        return left_container

    def _create_entries_table(self):
        """Create the IMG entries table"""
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Offset", "Size"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _create_status_bar(self):
        """Create status bar"""
        status = QStatusBar()
        self.setStatusBar(status)
        
        # Left side status
        self.status_label = QLabel("Ready")
        status.addWidget(self.status_label)
        
        # Entries count
        self.entries_count_label = QLabel("Entries: 0")
        status.addWidget(self.entries_count_label)
        
        # Selected count
        self.selected_count_label = QLabel("Selected: 0")
        status.addWidget(self.selected_count_label)
        
        # Right side - IMG info
        self.img_status_label = QLabel("IMG: (no tabs open)")
        status.addPermanentWidget(self.img_status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status.addPermanentWidget(self.progress_bar)

    def _get_button_callbacks(self):
        """Get button callbacks for the modular system"""
        return {
            # IMG Operations
            "open": self.open_img_file,
            "close": self.close_img_file,
            "rebuild": self.rebuild_img,
            "merge": self.merge_img,
            "split": self.split_img,
            "convert": self.convert_img,
            
            # Entry Operations
            "import": self.import_files,
            "export": self.export_selected_entries,
            "remove": self.remove_selected_entries,
            "update_list": self.refresh_table,
            "select_all": self._select_all,
            "select_inverse": self._select_inverse,
            "sort": self._sort_entries,
            
            # Advanced
            "open_multiple": self.open_multiple_files,
            "new_img": self.create_new_img,
        }

    def _setup_menu_callbacks(self):
        """Setup menu callbacks"""
        callbacks = {
            # File menu
            "new_img": self.create_new_img,
            "open_img": self.open_img_file,
            "open_multiple": self.open_multiple_files,
            "close_img": self.close_img_file,
            "exit": self.close,
            
            # Edit menu
            "select_all": self._select_all,
            "select_inverse": self._select_inverse,
            "find": self._focus_search,
            
            # IMG menu
            "img_rebuild": self.rebuild_img,
            "img_validate": self.validate_img,
            
            # Entry menu
            "entry_import": self.import_files,
            "entry_export": self.export_selected_entries,
            "entry_remove": self.remove_selected_entries,
            
            # Settings menu
            "customize_buttons": self._show_button_customization,
            "customize_panels": self._show_panel_customization,
            
            # Help menu
            "about": self._show_about,
        }
        
        self.menu_bar.set_callbacks(callbacks)

    # Core functionality methods

    def open_img_file(self):
        """REVERTED: Original single IMG file open dialog (as requested)"""
        file_path = open_single_img_file(self)
        
        if file_path:
            self.load_img_file(file_path)

    def open_multiple_files(self):
        """NEW: Combined multiple file open dialog"""
        files, mode = show_combined_open_dialog(self)
        
        if files:
            if mode == "single" and len(files) == 1:
                # Single IMG file
                self.load_img_file(files[0])
            elif mode == "multiple":
                # Multiple files - handle appropriately
                self._handle_multiple_files(files)

    def _handle_multiple_files(self, files):
        """Handle opening multiple files"""
        img_files = [f for f in files if f.lower().endswith('.img')]
        other_files = [f for f in files if not f.lower().endswith('.img')]
        
        if img_files:
            # Load the first IMG file
            self.load_img_file(img_files[0])
            
            if len(img_files) > 1:
                self.log_message(f"Note: Only first IMG file loaded. Other IMG files ignored.")
        
        if other_files and self.current_img:
            # Import other files into the loaded IMG
            self.log_message(f"Importing {len(other_files)} additional files...")
            # Implementation would go here
        elif other_files:
            self.log_message("Cannot import files - no IMG archive loaded")

    def load_img_file(self, file_path):
        """Load IMG file"""
        if self.load_thread and self.load_thread.isRunning():
            return

        self.log_message(f"Loading IMG file: {os.path.basename(file_path)}")

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.status_label.setText("Loading IMG file...")

        # Start loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress.connect(self.progress_bar.setValue)
        self.load_thread.finished.connect(self._on_img_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.start()

    def _on_img_loaded(self, img_file):
        """Handle successful IMG loading"""
        self.current_img = img_file

        # Update UI
        self.populate_table()
        self._update_img_info()
        self._update_button_states()

        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

        self.log_message(f"Loaded IMG: {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")

    def _on_load_error(self, error_message):
        """Handle IMG loading error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

        self.log_message(f"Failed to load IMG: {error_message}")
        QMessageBox.critical(self, "Loading Error", f"Failed to load IMG file:\n{error_message}")

    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None

            # Clear UI
            self.table.setRowCount(0)
            self._update_img_info()
            self._update_button_states()

            self.log_message("IMG file closed")

    def populate_table(self):
        """Populate entries table"""
        if not self.current_img:
            return

        self.table.setRowCount(len(self.current_img.entries))

        for row, entry in enumerate(self.current_img.entries):
            # ID
            id_item = QTableWidgetItem(str(row + 1))
            self.table.setItem(row, 0, id_item)

            # Type
            ext = os.path.splitext(entry.name)[1].upper().lstrip('.')
            type_item = QTableWidgetItem(ext or "Unknown")
            self.table.setItem(row, 1, type_item)

            # Name
            name_item = QTableWidgetItem(entry.name)
            self.table.setItem(row, 2, name_item)

            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:08X}")
            self.table.setItem(row, 3, offset_item)

            # Size
            size_item = QTableWidgetItem(format_file_size(entry.size))
            self.table.setItem(row, 4, size_item)

        # Resize columns
        self.table.resizeColumnsToContents()

    def _update_img_info(self):
        """Update IMG information display"""
        if self.current_img:
            file_name = os.path.basename(self.current_img.file_path)
            self.img_status_label.setText(f"IMG: {file_name}")
            self.entries_count_label.setText(f"Entries: {len(self.current_img.entries)}")
        else:
            self.img_status_label.setText("IMG: (no tabs open)")
            self.entries_count_label.setText("Entries: 0")

    def _update_button_states(self):
        """Update button enabled states"""
        has_img = self.current_img is not None
        
        # Update menu actions
        self.menu_bar.enable_action("close_img", has_img)
        self.menu_bar.enable_action("img_rebuild", has_img)
        self.menu_bar.enable_action("entry_import", has_img)
        self.menu_bar.enable_action("entry_export", has_img)

    def _on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = len(self.table.selectionModel().selectedRows())
        self.selected_count_label.setText(f"Selected: {selected_rows}")

    def _on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        row = item.row()
        if self.current_img and row < len(self.current_img.entries):
            entry = self.current_img.entries[row]
            self.log_message(f"Entry info: {entry.name} ({format_file_size(entry.size)})")

    def _on_filter_changed(self, filter_type: str, value: str):
        """Handle filter changes"""
        self.log_message(f"Filter changed: {filter_type} = {value}")
        # Implementation would go here

    def _on_search_requested(self, search_text: str):
        """Handle search requests"""
        if not search_text:
            # Show all rows
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
        else:
            # Filter based on search text
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 2)  # Name column
                if name_item:
                    visible = search_text.lower() in name_item.text().lower()
                    self.table.setRowHidden(row, not visible)

    def _select_all(self):
        """Select all entries"""
        self.table.selectAll()

    def _select_inverse(self):
        """Select inverse"""
        # Implementation would go here
        self.log_message("Select inverse not yet implemented")

    def _sort_entries(self):
        """Sort entries"""
        self.table.sortItems(2)  # Sort by name column

    def _focus_search(self):
        """Focus search box in filter panel"""
        if self.panel_manager:
            filter_panel = self.panel_manager.get_panel("filter_search")
            if filter_panel and hasattr(filter_panel, 'search_box'):
                filter_panel.search_box.setFocus()

    def refresh_table(self):
        """Refresh the entries table"""
        if self.current_img:
            self.populate_table()
            self.log_message("Table refreshed")

    def create_new_img(self):
        """Show new IMG creation dialog"""
        from components.img_creator import NewIMGDialog
        dialog = NewIMGDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.log_message("New IMG creation completed")

    def _show_button_customization(self):
        """Show button customization dialog"""
        from gui.buttons import ButtonCustomizationDialog
        dialog = ButtonCustomizationDialog(self.preset_manager, self)
        dialog.preset_changed.connect(self._apply_button_preset)
        dialog.exec()

    def _show_panel_customization(self):
        """Show panel customization options"""
        self.log_message("Panel customization not yet implemented")

    def _apply_button_preset(self, preset_name: str):
        """Apply button preset to panels"""
        if self.panel_manager:
            for panel_id, panel in self.panel_manager.panels.items():
                if hasattr(panel, 'apply_preset'):
                    panel.apply_preset(preset_name)

    def _show_about(self):
        """Show about dialog"""
        about_text = """
<h3>IMG Factory 1.5</h3>
<p>Advanced IMG archive manager for GTA games</p>
<p><b>Features:</b></p>
<ul>
<li>Modular tear-off panels</li>
<li>Customizable button layouts</li>
<li>Support for GTA III, Vice City, San Andreas, and IV</li>
<li>Import/export files with validation</li>
</ul>
<p><b>Supported Files:</b> IMG, COL, TXD, DFF, IFP, WAV, SCM</p>
<p>X-Seti - June25 2025</p>
        """
        QMessageBox.about(self, "About IMG Factory 1.5", about_text)

    # Placeholder methods for functionality
    def import_files(self):
        """Import files into IMG"""
        self.log_message("Import functionality coming soon!")

    def export_selected_entries(self):
        """Export selected entries"""
        self.log_message("Export functionality coming soon!")

    def remove_selected_entries(self):
        """Remove selected entries"""
        self.log_message("Remove functionality coming soon!")

    def rebuild_img(self):
        """Rebuild IMG file"""
        self.log_message("Rebuild functionality coming soon!")

    def validate_img(self):
        """Validate IMG file"""
        self.log_message("Validate functionality coming soon!")

    def merge_img(self):
        """Merge IMG files"""
        self.log_message("Merge functionality coming soon!")

    def split_img(self):
        """Split IMG file"""
        self.log_message("Split functionality coming soon!")

    def convert_img(self):
        """Convert IMG format"""
        self.log_message("Convert functionality coming soon!")

    # Logging
    def log_message(self, message):
        """Add message to log"""
        self.log.append(f"[INFO] {message}")

    def log_error(self, message):
        """Add error message to log"""
        self.log.append(f"[ERROR] {message}")


def main():
    """Main application entry point"""
    import os
    import warnings
    
    # Suppress Qt warnings about unknown CSS properties
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    app = QApplication(sys.argv)
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    
    # Suppress console spam
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    
    # Create settings system
    settings = AppSettings()
    
    # Apply themes
    apply_theme_to_app(app, settings)
    apply_pastel_theme_to_buttons(app, settings)
    print("✓ Themes applied successfully")
    
    # Create main window
    window = IMGFactory(settings)
    window.show()
    
    # Log startup
    window.log_message("IMG Factory 1.5 started")
    window.log_message("Modular GUI system active")
    window.log_message("Ready to work with IMG archives")
    
    # Suppress any remaining console spam
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


class IMGLoadThread(QThread):
    """Background thread for loading IMG files (same as before)"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit(10)
            img_file = IMGFile(self.file_path)
            
            self.progress.emit(30)
            if not img_file.open():
                self.error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress.emit(100)
            self.finished.emit(img_file)
            
        except Exception as e:
            self.error.emit(f"Error loading IMG file: {str(e)}")


class IMGFactory(QMainWindow):
    """Main IMG Factory application with modular GUI"""
    
    def __init__(self, app_settings):
        super().__init__()
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1100, 700)
        self.app_settings = app_settings
        
        # Current IMG file
        self.current_img: IMGFile = None
        self.load_thread: IMGLoadThread = None

        # Initialize modular GUI components
        if MODULAR_GUI_AVAILABLE:
            self.preset_manager = ButtonPresetManager()
            self.panel_manager = None  # Will be created after UI
        
        self._create_ui()
        self._create_status_bar()
        
        # Create menu system
        if MODULAR_GUI_AVAILABLE:
            self.menu_bar = IMGFactoryMenuBar(self, self.panel_manager)
            self.context_menu_manager = ContextMenuManager(self)
            self._setup_menu_callbacks()
        else:
            self._create_fallback_menu()

    def _create_ui(self):
        """Create the main UI with modular panel system"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        if MODULAR_GUI_AVAILABLE:
            self._create_modular_ui(main_layout)
        else:
            self._create_fallback_ui(main_layout)

    def _create_modular_ui(self, main_layout):
        """Create UI with modular panel system"""
        # Main horizontal splitter (left content | right panels)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Table and Log with vertical splitter
        left_widget = self._create_left_panel()
        
        # Right side: Modular panels
        right_widget = self._create_modular_right_panel()
        
        # Add widgets to main splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        
        # Set initial sizes (left panel 70%, right panel 30%)
        self.main_splitter.setSizes([770, 330])
        
        # Prevent panels from collapsing
        self.main_splitter.setChildrenCollapsible(False)
        
        main_layout.addWidget(self.main_splitter)

    def _create_modular_right_panel(self):
        """Create right panel with modular tear-off panels"""
        # Create panel manager with callbacks
        callbacks = self._get_button_callbacks()
        self.panel_manager = PanelManager(self, self.preset_manager)
        
        # Create default panels
        panels = self.panel_manager.create_default_panels(callbacks)
        
        # Create container for panels
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(5)
        
        # Add panels to layout
        for panel_id in ["img_ops", "entries_ops", "filter_search"]:
            if panel_id in panels:
                right_layout.addWidget(panels[panel_id])
        
        right_layout.addStretch()
        
        # Connect filter panel signals
        if "filter_search" in panels:
            filter_panel = panels["filter_search"]
            filter_panel.filter_changed.connect(self._on_filter_changed)
            filter_panel.search_requested.connect(self._on_search_requested)
        
        return right_widget

    def _create_fallback_ui(self, main_layout):
        """Create fallback UI if modular system not available"""
        # Same as before - create the traditional layout
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = self._create_left_panel()
        right_widget = self._create_traditional_right_panel()
        
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        self.main_splitter.setSizes([770, 330])
        
        main_layout.addWidget(self.main_splitter)

    def _create_left_panel(self):
        """Create left panel with IMG table and log (same as before)"""
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Vertical splitter for table and log
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # IMG entries table
        self._create_entries_table()
        self.left_splitter.addWidget(self.table)
        
        # Log section
        self.log = QTextEdit()
        self.log.setMaximumHeight(150)
        self.log.setPlaceholderText("Activity log will appear here...")
        self.left_splitter.addWidget(self.log)
        
        # Set sizes (table 80%, log 20%)
        self.left_splitter.setSizes([400, 100])
        
        left_layout.addWidget(self.left_splitter)
        
        return left_container

    def _create_main_ui_with_splitters(self, main_layout):
        """Create the main UI matching original IMG Factory layout"""
        
        # Main horizontal splitter (left content | right controls)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Table and Log with vertical splitter
        left_widget = self._create_left_panel()
        
        # Right side: Control panels (matching original layout)
        right_widget = self._create_right_panel()
        
        # Add widgets to main splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        
        # Set initial sizes (left panel 70%, right panel 30%)
        self.main_splitter.setSizes([770, 330])
        
        # Prevent panels from collapsing
        self.main_splitter.setChildrenCollapsible(False)
        
        main_layout.addWidget(self.main_splitter)

    def _create_left_panel(self):
        """Create left panel with IMG table and log"""
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Vertical splitter for table and log
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # IMG entries table
        self._create_entries_table()
        self.left_splitter.addWidget(self.table)
        
        # Log section
        self.log = QTextEdit()
        self.log.setMaximumHeight(150)
        self.log.setPlaceholderText("Activity log will appear here...")
        self.left_splitter.addWidget(self.log)
        
        # Set sizes (table 80%, log 20%)
        self.left_splitter.setSizes([400, 100])
        
        left_layout.addWidget(self.left_splitter)
        
        return left_container

    def _create_entries_table(self):
        """Create the IMG entries table"""
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Name", "Offset", "Size"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _create_right_panel(self):
        """Create right control panel (original IMG Factory style)"""
        
        right_widget = QWidget()
        right_widget.setMinimumWidth(280)
        right_layout = QVBoxLayout(right_widget)
        
        # IMG Operations
        img_group = QGroupBox("IMG")
        img_layout = QGridLayout(img_group)
        img_layout.setSpacing(3)
        
        # Row 1
        self.open_btn = QPushButton("Open")
        self.open_btn.setProperty("action-type", "import")
        self.open_btn.clicked.connect(self.open_img_file)  # REVERTED: Single file
        img_layout.addWidget(self.open_btn, 0, 0)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close_img_file)
        self.close_btn.setEnabled(False)
        img_layout.addWidget(self.close_btn, 0, 1)
        
        self.close_all_btn = QPushButton("Close All")
        img_layout.addWidget(self.close_all_btn, 0, 2)
        
        # Row 2
        self.rebuild_btn = QPushButton("Rebuild")
        self.rebuild_btn.setProperty("action-type", "update")
        self.rebuild_btn.clicked.connect(self.rebuild_img)
        self.rebuild_btn.setEnabled(False)
        img_layout.addWidget(self.rebuild_btn, 1, 0)
        
        self.rebuild_as_btn = QPushButton("Rebuild As")
        self.rebuild_as_btn.setProperty("action-type", "update")
        img_layout.addWidget(self.rebuild_as_btn, 1, 1)
        
        self.rebuild_all_btn = QPushButton("Rebuild All")
        self.rebuild_all_btn.setProperty("action-type", "update")
        img_layout.addWidget(self.rebuild_all_btn, 1, 2)
        
        # Row 3
        self.merge_btn = QPushButton("Merge")
        self.merge_btn.setProperty("action-type", "convert")
        img_layout.addWidget(self.merge_btn, 2, 0)
        
        self.split_btn = QPushButton("Split")
        self.split_btn.setProperty("action-type", "convert")
        img_layout.addWidget(self.split_btn, 2, 1)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setProperty("action-type", "convert")
        img_layout.addWidget(self.convert_btn, 2, 2)
        
        right_layout.addWidget(img_group)
        
        # Entries Operations
        entries_group = QGroupBox("Entries")
        entries_layout = QGridLayout(entries_group)
        entries_layout.setSpacing(3)
        
        # Row 1
        self.import_btn = QPushButton("Import")
        self.import_btn.setProperty("action-type", "import")
        self.import_btn.clicked.connect(self.import_files)
        self.import_btn.setEnabled(False)
        entries_layout.addWidget(self.import_btn, 0, 0)
        
        self.import_via_btn = QPushButton("Import via")
        self.import_via_btn.setProperty("action-type", "import")
        entries_layout.addWidget(self.import_via_btn, 0, 1)
        
        self.update_list_btn = QPushButton("Update list")
        self.update_list_btn.setProperty("action-type", "update")
        self.update_list_btn.clicked.connect(self.refresh_table)
        entries_layout.addWidget(self.update_list_btn, 0, 2)
        
        # Row 2
        self.export_btn = QPushButton("Export")
        self.export_btn.setProperty("action-type", "export")
        self.export_btn.clicked.connect(self.export_selected_entries)
        self.export_btn.setEnabled(False)
        entries_layout.addWidget(self.export_btn, 1, 0)
        
        self.export_via_btn = QPushButton("Export via")
        self.export_via_btn.setProperty("action-type", "export")
        entries_layout.addWidget(self.export_via_btn, 1, 1)
        
        self.quick_export_btn = QPushButton("Quick Export")
        self.quick_export_btn.setProperty("action-type", "export")
        entries_layout.addWidget(self.quick_export_btn, 1, 2)
        
        # Row 3
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setProperty("action-type", "remove")
        self.remove_btn.clicked.connect(self.remove_selected_entries)
        self.remove_btn.setEnabled(False)
        entries_layout.addWidget(self.remove_btn, 2, 0)
        
        self.remove_via_btn = QPushButton("Remove via")
        self.remove_via_btn.setProperty("action-type", "remove")
        entries_layout.addWidget(self.remove_via_btn, 2, 1)
        
        self.dump_btn = QPushButton("Dump")
        self.dump_btn.setProperty("action-type", "update")
        entries_layout.addWidget(self.dump_btn, 2, 2)
        
        # Row 4
        self.rename_btn = QPushButton("Rename")
        entries_layout.addWidget(self.rename_btn, 3, 0)
        
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.setProperty("action-type", "convert")
        entries_layout.addWidget(self.replace_btn, 3, 1)
        
        # Row 5
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        entries_layout.addWidget(self.select_all_btn, 4, 0)
        
        self.select_inverse_btn = QPushButton("Select Inverse")
        entries_layout.addWidget(self.select_inverse_btn, 4, 1)
        
        self.sort_btn = QPushButton("Sort")
        entries_layout.addWidget(self.sort_btn, 4, 2)
        
        right_layout.addWidget(entries_group)
        
        # Filter & Search
        filter_group = QGroupBox("Filter & Search")
        filter_layout = QVBoxLayout(filter_group)
        
        # Filter dropdowns
        filter_row1 = QHBoxLayout()
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "DFF", "TXD", "COL", "IFP", "WAV"])
        filter_row1.addWidget(QLabel("Type:"))
        filter_row1.addWidget(self.type_filter)
        filter_layout.addLayout(filter_row1)
        
        filter_row2 = QHBoxLayout()
        self.version_filter = QComboBox()
        self.version_filter.addItems(["All Versions"])
        filter_row2.addWidget(QLabel("Version:"))
        filter_row2.addWidget(self.version_filter)
        filter_layout.addLayout(filter_row2)
        
        # Search box
        search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self._filter_entries)
        search_row.addWidget(self.search_box)
        
        self.find_btn = QPushButton("Find")
        search_row.addWidget(self.find_btn)
        filter_layout.addLayout(search_row)
        
        # Filter checkboxes
        self.hit_tabs_check = QCheckBox("Hit Tabs")
        filter_layout.addWidget(self.hit_tabs_check)
        
        right_layout.addWidget(filter_group)
        
        # NEW: Add combined open button
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.open_multiple_btn = QPushButton("📁 Open Multiple Files")
        self.open_multiple_btn.setProperty("action-type", "import")
        self.open_multiple_btn.clicked.connect(self.open_multiple_files)  # NEW: Combined dialog
        advanced_layout.addWidget(self.open_multiple_btn)
        
        self.new_img_btn = QPushButton("🆕 New IMG")
        self.new_img_btn.setProperty("action-type", "import")
        self.new_img_btn.clicked.connect(self.create_new_img)
        advanced_layout.addWidget(self.new_img_btn)
        
        right_layout.addWidget(advanced_group)
        
        right_layout.addStretch()
        
        return right_widget

    def _create_menu(self):
        """Create menu bar (original IMG Factory style)"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        
        # REVERTED: Original single IMG open
        open_action = QAction("Open IMG", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        # NEW: Combined multiple file open
        open_multi_action = QAction("Open Multiple Files", self)
        open_multi_action.setShortcut("Ctrl+Shift+O")
        open_multi_action.triggered.connect(self.open_multiple_files)
        file_menu.addAction(open_multi_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("Close", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Add other menus (placeholders)
        for menu_name in ["Edit", "Dat", "IMG", "Model", "Texture", "Collision", 
                         "Item Definition", "Item Placement", "Entry", "Settings", "Help"]:
            menu = menubar.addMenu(menu_name)
            placeholder = QAction(f"{menu_name} (Coming Soon)", self)
            placeholder.setEnabled(False)
            menu.addAction(placeholder)

    def _create_status_bar(self):
        """Create status bar"""
        status = QStatusBar()
        self.setStatusBar(status)
        
        # Left side status
        self.status_label = QLabel("Ready")
        status.addWidget(self.status_label)
        
        # Entries count
        self.entries_count_label = QLabel("Entries: 0")
        status.addWidget(self.entries_count_label)
        
        # Selected count
        self.selected_count_label = QLabel("Selected: 0")
        status.addWidget(self.selected_count_label)
        
        # Right side - IMG info
        self.img_status_label = QLabel("IMG: (no tabs open)")
        status.addPermanentWidget(self.img_status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status.addPermanentWidget(self.progress_bar)

    # Core functionality methods

    def open_img_file(self):
        """REVERTED: Original single IMG file open dialog (as requested)"""
        if COMBINED_DIALOG_AVAILABLE:
            file_path = open_single_img_file(self)
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open IMG Archive", "", "IMG Files (*.img);;All Files (*)"
            )
        
        if file_path:
            self.load_img_file(file_path)

    def open_multiple_files(self):
        """NEW: Combined multiple file open dialog"""
        if COMBINED_DIALOG_AVAILABLE:
            files, mode = show_combined_open_dialog(self)
        else:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files to Open", "",
                "All Supported (*.img *.col *.txd *.dff);;IMG Archives (*.img);;All Files (*)"
            )
            mode = "multiple"
        
        if files:
            if mode == "single" and len(files) == 1:
                # Single IMG file
                self.load_img_file(files[0])
            elif mode == "multiple":
                # Multiple files - handle appropriately
                self._handle_multiple_files(files)

    def _handle_multiple_files(self, files):
        """Handle opening multiple files"""
        img_files = [f for f in files if f.lower().endswith('.img')]
        other_files = [f for f in files if not f.lower().endswith('.img')]
        
        if img_files:
            # Load the first IMG file
            self.load_img_file(img_files[0])
            
            if len(img_files) > 1:
                self.log_message(f"Note: Only first IMG file loaded. Other IMG files ignored.")
        
        if other_files and self.current_img:
            # Import other files into the loaded IMG
            self.log_message(f"Importing {len(other_files)} additional files...")
            # Implementation would go here
        elif other_files:
            self.log_message("Cannot import files - no IMG archive loaded")

    def load_img_file(self, file_path):
        """Load IMG file"""
        if self.load_thread and self.load_thread.isRunning():
            return

        self.log_message(f"Loading IMG file: {os.path.basename(file_path)}")

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.status_label.setText("Loading IMG file...")

        # Start loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress.connect(self.progress_bar.setValue)
        self.load_thread.finished.connect(self._on_img_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.start()

    def _on_img_loaded(self, img_file):
        """Handle successful IMG loading"""
        self.current_img = img_file

        # Update UI
        self.populate_table()
        self._update_img_info()
        self._update_button_states()

        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

        self.log_message(f"Loaded IMG: {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")

    def _on_load_error(self, error_message):
        """Handle IMG loading error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

        self.log_message(f"Failed to load IMG: {error_message}")
        QMessageBox.critical(self, "Loading Error", f"Failed to load IMG file:\n{error_message}")

    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None

            # Clear UI
            self.table.setRowCount(0)
            self._update_img_info()
            self._update_button_states()

            self.log_message("IMG file closed")

    def populate_table(self):
        """Populate entries table"""
        if not self.current_img:
            return

        self.table.setRowCount(len(self.current_img.entries))

        for row, entry in enumerate(self.current_img.entries):
            # ID
            id_item = QTableWidgetItem(str(row + 1))
            self.table.setItem(row, 0, id_item)

            # Type
            ext = os.path.splitext(entry.name)[1].upper().lstrip('.')
            type_item = QTableWidgetItem(ext or "Unknown")
            self.table.setItem(row, 1, type_item)

            # Name
            name_item = QTableWidgetItem(entry.name)
            self.table.setItem(row, 2, name_item)

            # Offset
            offset_item = QTableWidgetItem(f"0x{entry.offset:08X}")
            self.table.setItem(row, 3, offset_item)

            # Size
            size_item = QTableWidgetItem(format_file_size(entry.size))
            self.table.setItem(row, 4, size_item)

        # Resize columns
        self.table.resizeColumnsToContents()

    def _update_img_info(self):
        """Update IMG information display"""
        if self.current_img:
            file_name = os.path.basename(self.current_img.file_path)
            self.img_status_label.setText(f"IMG: {file_name}")
            self.entries_count_label.setText(f"Entries: {len(self.current_img.entries)}")
        else:
            self.img_status_label.setText("IMG: (no tabs open)")
            self.entries_count_label.setText("Entries: 0")

    def _update_button_states(self):
        """Update button enabled states"""
        has_img = self.current_img is not None

        # IMG operations
        self.close_btn.setEnabled(has_img)
        self.rebuild_btn.setEnabled(has_img)

        # Entry operations
        self.import_btn.setEnabled(has_img)
        self.export_btn.setEnabled(has_img)
        self.remove_btn.setEnabled(has_img)

    def _on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = len(self.table.selectionModel().selectedRows())
        self.selected_count_label.setText(f"Selected: {selected_rows}")

    def _on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        row = item.row()
        if self.current_img and row < len(self.current_img.entries):
            entry = self.current_img.entries[row]
            self.log_message(f"Entry info: {entry.name} ({format_file_size(entry.size)})")

    def _filter_entries(self, text):
        """Filter entries table based on search text"""
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 2)  # Name column
            if name_item:
                visible = text.lower() in name_item.text().lower() if text else True
                self.table.setRowHidden(row, not visible)

    def _select_all(self):
        """Select all entries"""
        self.table.selectAll()

    def refresh_table(self):
        """Refresh the entries table"""
        if self.current_img:
            self.populate_table()
            self.log_message("Table refreshed")

    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.log_message("New IMG creation completed")

    # Placeholder methods for functionality
    def import_files(self):
        """Import files into IMG"""
        self.log_message("Import functionality coming soon!")
        QMessageBox.information(self, "Import", "Import functionality will be implemented")

    def export_selected_entries(self):
        """Export selected entries"""
        self.log_message("Export functionality coming soon!")
        QMessageBox.information(self, "Export", "Export functionality will be implemented")

    def remove_selected_entries(self):
        """Remove selected entries"""
        self.log_message("Remove functionality coming soon!")
        QMessageBox.information(self, "Remove", "Remove functionality will be implemented")

    def rebuild_img(self):
        """Rebuild IMG file"""
        reply = QMessageBox.question(
            self, "Rebuild IMG",
            "This will rebuild the IMG file and may take some time.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log_message("Rebuild functionality coming soon!")
            QMessageBox.information(self, "Rebuild", "Rebuild functionality will be implemented")

    # Logging
    def log_message(self, message):
        """Add message to log"""
        self.log.append(f"[INFO] {message}")

    def log_error(self, message):
        """Add error message to log"""
        self.log.append(f"[ERROR] {message}")


def main():
    """Main application entry point"""
    import os
    import warnings
    
    # Suppress Qt warnings about unknown CSS properties
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    app = QApplication(sys.argv)
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    
    # Suppress console spam
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    
    # Create settings system
    try:
        settings = AppSettings()
        
        # Apply base theme from App_settings_system
        apply_theme_to_app(app, settings)
        print("✓ Base theme applied")
        
        # Apply pastel button theme on top (with error handling)
        try:
            apply_pastel_theme_to_buttons(app, settings)
            print("✓ Pastel theme applied")
        except Exception as e:
            print(f"⚠ Pastel theme failed: {e}")
        
    except Exception as e:
        print(f"⚠ Theme system failed: {e}")
        settings = AppSettings()  # Use dummy
        
        # Apply minimal styling to prevent ugly default look
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QPushButton[action-type="import"] {
                background-color: #e3f2fd;
            }
            QPushButton[action-type="export"] {
                background-color: #e8f5e8;
            }
            QPushButton[action-type="remove"] {
                background-color: #ffebee;
            }
            QPushButton[action-type="update"] {
                background-color: #fff3e0;
            }
            QPushButton[action-type="convert"] {
                background-color: #f3e5f5;
            }
        """)
        print("✓ Fallback styling applied")
    
    # Create main window
    window = IMGFactory(settings)
    window.show()
    
    # Log startup
    window.log_message("IMG Factory 1.5 started")
    window.log_message("Ready to work with IMG archives")
    
    # Suppress any remaining console spam
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()