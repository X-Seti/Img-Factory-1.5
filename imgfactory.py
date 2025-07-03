#!/usr/bin/env python3
"""
X-Seti - JUNE25 2025 - IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""
#this belongs in root /imgfactory.py - version 60
import sys
import os
import mimetypes
from pathlib import Path  # Move this up here
print("Starting application...")

# Setup paths FIRST - before any other imports
current_dir = Path(__file__).parent
components_dir = current_dir / "components"
gui_dir = current_dir / "gui"

# Add directories to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if components_dir.exists() and str(components_dir) not in sys.path:
    sys.path.insert(0, str(components_dir))
if gui_dir.exists() and str(gui_dir) not in sys.path:
    sys.path.insert(0, str(gui_dir))

# Now continue with other imports

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton
)
print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import Qt, QThread, pyqtSignal,  QTimer, QSettings, QMimeData
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap, QDragEnterEvent, QDropEvent, QContextMenuEvent

from app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog
from components.img_creator import NewIMGDialog
from components.img_core_classes import (
    IMGFile, IMGEntry, IMGVersion, Platform, format_file_size,
    IMGEntriesTable, FilterPanel, IMGFileInfoPanel,
    TabFilterWidget, integrate_filtering, create_entries_table_panel
)
from components.img_formats import GameSpecificIMGDialog, EnhancedIMGCreator
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
from components.img_validator import IMGValidator
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.menu import IMGFactoryMenuBar
#from components.col_main_integration import setup_col_integration

print("Components imported successfully")


def populate_img_table(table: QTableWidget, img_file: IMGFile):
    """Populate table with IMG file entries - module level function"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return

    entries = img_file.entries

    # Clear existing data first
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        # Name
        table.setItem(row, 0, QTableWidgetItem(entry.name))

        # Type (file extension)
        file_type = entry.name.split('.')[-1].upper() if '.' in entry.name else "Unknown"
        table.setItem(row, 1, QTableWidgetItem(file_type))

        # Size (formatted)
        try:
            from components.img_core_classes import format_file_size
            size_text = format_file_size(entry.size)
        except:
            size_text = f"{entry.size} bytes"
        table.setItem(row, 2, QTableWidgetItem(size_text))

        # Offset (hex format)
        table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))

        # Version - Improved detection
        version = "Unknown"
        try:
            if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                version = entry.get_version_text()
            elif hasattr(img_file, 'version'):
                # Use IMG file version to provide better info
                if img_file.version.name == 'IMG_1':
                    # For GTA III/VC files, try to detect from file types
                    if file_type in ['DFF', 'TXD']:
                        version = "RW 3.6.0.3"  # Common version for GTA III/VC
                    elif file_type == 'COL':
                        version = "COL 2"
                    elif file_type == 'IFP':
                        version = "IFP 1"
                    else:
                        version = "GTA III/VC"
                elif img_file.version.name == 'IMG_2':
                    version = "GTA SA"
                elif img_file.version.name == 'IMG_3':
                    version = "GTA IV"
                else:
                    version = img_file.version.name
        except:
            version = "Unknown"
        table.setItem(row, 4, QTableWidgetItem(version))

        # Compression
        compression = "None"
        try:
            if hasattr(entry, 'compression') and hasattr(entry.compression, 'name'):
                if entry.compression.name != 'NONE':
                    compression = entry.compression.name
            elif hasattr(entry, 'compressed') and entry.compressed:
                compression = "ZLib"
            elif hasattr(entry, 'is_compressed') and callable(entry.is_compressed) and entry.is_compressed():
                compression = "Compressed"
        except:
            compression = "None"
        table.setItem(row, 5, QTableWidgetItem(compression))

        # Status
        status = "Ready"
        try:
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                status = "New"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                status = "Modified"
        except:
            status = "Ready"
        table.setItem(row, 6, QTableWidgetItem(status))

        # Make items read-only
        for col in range(7):
            item = table.item(row, col)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)



class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_updated = pyqtSignal(int, str)  # progress, status
    loading_finished = pyqtSignal(object)    # IMGFile object
    loading_error = pyqtSignal(str)          # error message

    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            self.progress_updated.emit(10, "Opening file...")

            # Create IMG file instance
            img_file = IMGFile(self.file_path)

            self.progress_updated.emit(30, "Detecting format...")

            # Open and parse file (entries are loaded automatically by open())
            if not img_file.open():
                self.loading_error.emit(f"Failed to open IMG file: {self.file_path}")
                return

            self.progress_updated.emit(60, "Reading entries...")

            # Check if entries were loaded
            if not img_file.entries:
                self.loading_error.emit(f"No entries found in IMG file: {self.file_path}")
                return

            self.progress_updated.emit(80, "Validating...")

            # Validate the loaded file if validator exists
            try:
                validation = IMGValidator.validate_img_file(img_file)
                if not validation.is_valid:
                    # Just warn but don't fail - some IMG files might have minor issues
                    print(f"IMG validation warnings: {validation.get_summary()}")
            except:
                # If validator fails, just continue - validation is optional
                pass

            self.progress_updated.emit(100, "Complete")

            # Return the loaded IMG file
            self.loading_finished.emit(img_file)

        except Exception as e:
            self.loading_error.emit(f"Error loading IMG file: {str(e)}")

    def populate_img_table(table: QTableWidget, img_file: IMGFile):
        """Populate table with IMG file entries"""
        if not img_file or not img_file.entries:
            table.setRowCount(0)
            return

        table.setRowCount(len(img_file.entries))

        for row, entry in enumerate(img_file.entries):
            # Filename
            table.setItem(row, 0, QTableWidgetItem(entry.name))
            # File type
            file_type = entry.name.split('.')[-1].upper() if '.' in entry.name else "Unknown"
            table.setItem(row, 1, QTableWidgetItem(file_type))
            # Size
            table.setItem(row, 2, QTableWidgetItem(format_file_size(entry.size)))
            # Offset
            table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))
            # Version
            table.setItem(row, 4, QTableWidgetItem(str(entry.version)))
            # Compression
            compression = "ZLib" if hasattr(entry, 'compressed') and entry.compressed else "None"
            table.setItem(row, 5, QTableWidgetItem(compression))
            # Status
            table.setItem(row, 6, QTableWidgetItem("Ready"))


class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.app_settings = settings if hasattr(settings, 'themes') else AppSettings()
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        
        # Core data
        self.current_img: Optional[IMGFile] = None
        self.current_col: Optional = None  # For COL file support
        self.template_manager = IMGTemplateManager()
        
        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None
        
        # Initialize GUI layout
        self.gui_layout = IMGFactoryGUILayout(self)
        self.menu_bar_system = IMGFactoryMenuBar(self)

        callbacks = {
            "about": self.show_about,
            "open_img": self.open_img_file,
            "new_img": self.create_new_img,
            "exit": self.close,
            "img_validate": self.validate_img,
            "customize_interface": self.show_gui_settings,
            # Add more as your methods exist
            }
        self.menu_bar_system.set_callbacks(callbacks)

        # Initialize UI (but without menu creation in gui_layout)
        self._create_ui()
        self._restore_settings()
        
        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)
        
        # Apply COL integration after creating the main interface
        # COL integration setup - with error handling
        try:
            from main_col_integration import setup_col_integration
            if setup_col_integration(self):
                self.log_message("COL functionality integrated successfully")
            else:
                self.log_message("COL functionality not available")
        except ImportError:
            self.log_message("COL integration not available - continuing without COL support")
        except Exception as e:
            self.log_message(f"COL integration error: {str(e)} - continuing without COL support")
        
        # Log startup
        self.log_message("IMG Factory 1.5 initialized")
    

    def setup_unified_signals(self):
        """Setup unified signal handler for all table interactions"""
        from components.unified_signal_handler import connect_table_signals

        # Connect main entries table to unified system
        success = connect_table_signals(
            table_name="main_entries",
            table_widget=self.gui_layout.table,
            parent_instance=self,
            selection_callback=self._unified_selection_handler,
            double_click_callback=self._unified_double_click_handler
        )

        if success:
            self.log_message("✅ Unified signal system connected")
        else:
            self.log_message("❌ Failed to connect unified signals")

        # Connect unified signals to status bar updates
        from components.unified_signal_handler import signal_handler
        signal_handler.status_update_requested.connect(self._update_status_from_signal)

    def _unified_selection_handler(self, selected_rows, selection_count):
        """Handle selection changes through unified system"""
        # Update button states based on selection
        has_selection = selection_count > 0
        self._update_button_states(has_selection)

        # Log selection (unified approach - no spam)
        if selection_count == 0:
            # Don't log "Ready" for empty selection to reduce noise
            pass
        elif selection_count == 1:
            # Get filename of selected item
            if selected_rows and len(selected_rows) > 0:
                row = selected_rows[0]
                if row < self.gui_layout.table.rowCount():
                    name_item = self.gui_layout.table.item(row, 0)
                    if name_item:
                        self.log_message(f"Selected: {name_item.text()}")
        else:
            self.log_message(f"Selected {selection_count} entries")

    def _unified_double_click_handler(self, row, filename, item):
        """Handle double-click through unified system"""
        self.log_message(f"Double-clicked: {filename}")

        # TODO: Add double-click functionality (preview, extract, etc.)
        # For now, show info about the item if IMG is loaded
        if self.current_img and row < len(self.current_img.entries):
            entry = self.current_img.entries[row]
            from components.img_core_classes import format_file_size
            self.log_message(f"File info: {entry.name} ({format_file_size(entry.size)})")

    def _update_status_from_signal(self, message):
        """Update status from unified signal system"""
        # Update status bar if available
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(message)

        # Also update GUI layout status if available
        if hasattr(self.gui_layout, 'status_label'):
            self.gui_layout.status_label.setText(message)

    def _update_button_states(self, has_selection):
        """Update button enabled/disabled states based on selection"""
        # Enable/disable buttons based on selection and loaded IMG
        has_img = self.current_img is not None

        # Find buttons in GUI layout and update their states
        # These buttons need both an IMG and selection
        selection_dependent_buttons = [
            'export_btn', 'export_selected_btn', 'remove_btn', 'remove_selected_btn',
            'extract_btn', 'quick_export_btn'
        ]

        for btn_name in selection_dependent_buttons:
            if hasattr(self.gui_layout, btn_name):
                button = getattr(self.gui_layout, btn_name)
                if hasattr(button, 'setEnabled'):
                    button.setEnabled(has_selection and has_img)

        # These buttons only need an IMG (no selection required)
        img_dependent_buttons = [
            'import_btn', 'import_files_btn', 'rebuild_btn', 'close_btn',
            'validate_btn', 'refresh_btn'
        ]

        for btn_name in img_dependent_buttons:
            if hasattr(self.gui_layout, btn_name):
                button = getattr(self.gui_layout, btn_name)
                if hasattr(button, 'setEnabled'):
                    button.setEnabled(has_img)

    def show_search_dialog(self):
        """Show search dialog and connect to unified system"""
        from gui.dialogs import show_search_dialog

        # Create and show search dialog
        self.search_dialog = show_search_dialog(self)

        # Connect the search_requested signal to our search handler
        if hasattr(self.search_dialog, 'search_requested'):
            self.search_dialog.search_requested.connect(self.perform_search)
            self.log_message("Search dialog opened")
        else:
            self.log_message("Search dialog error - signal not found")

    def perform_search(self, search_text, options):
        """Perform search in current IMG entries using unified system"""
        try:
            if not self.current_img or not self.current_img.entries:
                self.log_message("No IMG file loaded or no entries to search")
                if hasattr(self, 'search_dialog'):
                    self.search_dialog.update_results(0, 0)
                return

            # Perform search
            matches = []
            total_entries = len(self.current_img.entries)

            for i, entry in enumerate(self.current_img.entries):
                entry_name = entry.name

                # Apply search options
                if not options.get('case_sensitive', False):
                    entry_name = entry_name.lower()
                    search_text = search_text.lower()

                # Check if matches
                if options.get('whole_word', False):
                    import re
                    pattern = r'\b' + re.escape(search_text) + r'\b'
                    if re.search(pattern, entry_name):
                        matches.append(i)
                elif options.get('regex', False):
                    import re
                    try:
                        if re.search(search_text, entry_name):
                            matches.append(i)
                    except re.error:
                        self.log_message("Invalid regular expression")
                        return
                else:
                    # Simple text search
                    if search_text in entry_name:
                        matches.append(i)

            # Update search dialog results
            if hasattr(self, 'search_dialog'):
                self.search_dialog.update_results(len(matches), total_entries)

            # Select matching entries in table using unified system
            if matches:
                from components.unified_signal_handler import signal_handler
                if signal_handler.select_rows("main_entries", matches):
                    self.log_message(f"Found {len(matches)} matches for '{search_text}'")
                else:
                    self.log_message(f"Found {len(matches)} matches but couldn't select them")
            else:
                self.log_message(f"No matches found for '{search_text}'")

        except Exception as e:
            self.log_message(f"Search error: {str(e)}")

    # MODIFY the _create_ui() method to call setup_unified_signals():

    def _create_ui(self):
        """Create the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.gui_layout.create_main_ui_with_splitters(main_layout)
        self.gui_layout.create_status_bar()
        self.gui_layout.apply_table_theme()
        self.gui_layout.add_sample_data()

        # REPLACE any old signal connection calls with:
        # Setup unified signal system
        self.setup_unified_signals()

    # ALSO ADD a method to handle menu search action:

    def handle_menu_search(self):
        """Handle search from menu (Ctrl+F)"""
        self.show_search_dialog()


    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)
        # Delegate to GUI layout
        self.gui_layout.handle_resize_event(event)


    def log_message(self, message):
        """Log a message using GUI layout's log method"""
        self.gui_layout.log_message(message)

    def create_adaptive_button(self, label, action_type=None, icon=None, callback=None, bold=False):
        """Create adaptive button with theme support"""
        btn = QPushButton(label)
        
        # Set font
        font = btn.font()
        if bold:
            font.setBold(True)
        btn.setFont(font)
        
        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))

        # Connect callback if provided
        if callback:
            btn.clicked.connect(callback)
        else:
            btn.setEnabled(False)  # Disable buttons without callbacks

        return btn
    
    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Legacy method for compatibility"""
        return self.create_adaptive_button(label, action_type, icon, None, bold)

    # =============================================================================
    # IMG FILE OPERATIONS - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded"""
        # Enable COL-specific buttons
        if hasattr(self, 'gui_layout'):
            # Update table with COL info
            if self.gui_layout.table:
                self.gui_layout.table.setRowCount(1)
                col_name = os.path.basename(self.current_col) if self.current_col else "Unknown"
                items = [
                    (col_name, "COL", "Unknown", "0x0", "COL", "None", "Loaded")
                ]

                for row, item_data in enumerate(items):
                    for col, value in enumerate(item_data):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.gui_layout.table.setItem(row, col, item)

        # Update status
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(f"COL file loaded: {os.path.basename(self.current_col)}")


    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = GameSpecificIMGDialog(self)
        dialog.template_manager = self.template_manager
        dialog.img_created.connect(self.load_img_file)
        dialog.img_created.connect(lambda path: self.log_message(f"Created: {os.path.basename(path)}"))
        dialog.exec()

    def open_file(self):
        """Unified function to open IMG or COL files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG or COL File", "",
            "IMG/COL Files (*.img *.col);;IMG Files (*.img);;COL Files (*.col);;All Files (*)"
        )

        if file_path:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.img':
                self._load_img_file(file_path)
            elif file_ext == '.col':
                self._load_col_file(file_path)
            else:
                # Try to detect file type by content
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(8)

                    # Check for IMG signatures
                    if header[:4] in [b'VER2', b'VER3'] or len(header) >= 8:
                        self._load_img_file(file_path)
                    # Check for COL signatures
                    elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                        self._load_col_file(file_path)
                    else:
                        # Default to IMG
                        self._load_img_file(file_path)

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not determine file type: {e}")


    def open_img_file(self):
        """Open IMG file specifically"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG File", "", "IMG Files (*.img);;All Files (*)"
        )

        if file_path:
            self._load_img_file(file_path)

    def open_col_file(self):
        """Open COL file specifically"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )

        if file_path:
            self._load_col_file(file_path)

    def load_img_file(self, file_path: str):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.log_message(f"Loading: {os.path.basename(file_path)}")
        
        # Show progress
        self.gui_layout.show_progress(0, "Loading IMG file...")
        
        # Start loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._on_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_load_error)
        self.load_thread.start()
    
    def _load_img_file(self, file_path: str):
        """Internal method that calls the public load_img_file method"""
        self.load_img_file(file_path)

    def _update_ui_for_no_img(self):
        """Update UI when no IMG file is loaded"""
        # Clear current data
        self.current_img = None

        # Update window title
        self.setWindowTitle("IMG Factory 1.5")

        # Clear table if it exists
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            self.gui_layout.table.setRowCount(0)

        # Update status
        if hasattr(self, 'gui_layout'):
            self.gui_layout.show_progress(-1, "Ready")
            self.gui_layout.update_img_info("No IMG loaded")

        # Reset any status labels
        if hasattr(self, 'file_path_label'):
            self.file_path_label.setText("No file loaded")
        if hasattr(self, 'version_label'):
            self.version_label.setText("---")
        if hasattr(self, 'entry_count_label'):
            self.entry_count_label.setText("0")
        if hasattr(self, 'img_status_label'):
            self.img_status_label.setText("No IMG loaded")

        # Disable buttons that require an IMG to be loaded
        buttons_to_disable = [
            'close_img_btn', 'rebuild_btn', 'rebuild_as_btn', 'validate_btn',
            'import_btn', 'export_all_btn', 'merge_btn', 'split_btn'
        ]

        for button_name in buttons_to_disable:
            if hasattr(self, button_name):
                getattr(self, button_name).setEnabled(False)

        self.log_message("IMG interface reset")

    def _on_load_progress(self, progress: int, status: str):
        """Handle loading progress updates"""
        self.gui_layout.show_progress(progress, status)
    
    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        self.current_img = img_file
        self.log_message(f"Loaded: {img_file.file_path} ({len(img_file.entries)} entries)")

        # Update table
        populate_img_table(self.gui_layout.table, img_file)

        # Update status
        self.gui_layout.show_progress(-1, "Ready")

        # Fix: Use correct method name
        if hasattr(self.gui_layout, 'update_file_info'):
            self.gui_layout.update_file_info(f"{len(img_file.entries)} entries loaded")
        elif hasattr(self.gui_layout, 'update_img_info'):
            self.gui_layout.update_img_info(f"{len(img_file.entries)} entries loaded")
        else:
            # Fallback - just log the info
            self.log_message(f"File info: {len(img_file.entries)} entries loaded")

        # Update window title
        self.setWindowTitle(f"IMG Factory 1.5 - {os.path.basename(img_file.file_path)}")


    def _populate_real_img_table(self, img_file: IMGFile):
        """Populate table with real IMG file entries"""
        if not img_file or not img_file.entries:
            self.gui_layout.table.setRowCount(0)
            return

        table = self.gui_layout.table
        entries = img_file.entries

        # Clear existing data (including sample entries)
        table.setRowCount(0)
        table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            # Name
            table.setItem(row, 0, QTableWidgetItem(entry.name))

            # Type (file extension)
            file_type = entry.extension if entry.extension else "Unknown"
            table.setItem(row, 1, QTableWidgetItem(file_type))

            # Size (formatted)
            from components.img_core_classes import format_file_size
            size_text = format_file_size(entry.size)
            table.setItem(row, 2, QTableWidgetItem(size_text))

            # Offset (hex format)
            offset_text = f"0x{entry.offset:X}"
            table.setItem(row, 3, QTableWidgetItem(offset_text))

            # Version
            version_text = entry.get_version_text() if hasattr(entry, 'get_version_text') else "Unknown"
            table.setItem(row, 4, QTableWidgetItem(version_text))

            # Compression
            if hasattr(entry, 'is_compressed') and callable(entry.is_compressed):
                comp_text = "Compressed" if entry.is_compressed() else "None"
            else:
                comp_text = "None"
            table.setItem(row, 5, QTableWidgetItem(comp_text))

            # Status
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                status_text = "New"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                status_text = "Modified"
            else:
                status_text = "Ready"
            table.setItem(row, 6, QTableWidgetItem(status_text))

            # Make all items read-only
            for col in range(7):
                item = table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)


    def _on_load_error(self, error_message: str):
        """Handle IMG loading error"""
        self.log_message(f"Error: {error_message}")
        self.gui_layout.show_progress(-1, "Error")
        QMessageBox.critical(self, "Loading Error", error_message)

    def close_all_img(self):
        """Close all open IMG files"""
        self.current_img = None
        self.current_col = None
        self._update_ui_for_no_img()
        self.log_message("All IMG files closed")

    def rebuild_all_img(self):
        """Rebuild all IMG files in directory"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        base_dir = os.path.dirname(self.current_img.file_path)
        img_files = [f for f in os.listdir(base_dir) if f.endswith('.img')]

        if not img_files:
            QMessageBox.information(self, "Info", "No IMG files found in directory")
            return

        reply = QMessageBox.question(self, "Rebuild All",
                                    f"Rebuild {len(img_files)} IMG files?")
        if reply == QMessageBox.StandardButton.Yes:
            self.log_message(f"Rebuilding {len(img_files)} IMG files...")
            # Implementation would iterate through files

    def merge_img(self):
        """Merge multiple IMG files"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select IMG files to merge", "", "IMG Files (*.img)"
        )
        if len(files) < 2:
            QMessageBox.warning(self, "Warning", "Select at least 2 IMG files")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save merged IMG as", "", "IMG Files (*.img)"
        )
        if output_file:
            self.log_message(f"Merging {len(files)} IMG files...")
            QMessageBox.information(self, "Info", "Merge functionality coming soon")

    def split_img(self):
        """Split IMG file into smaller parts"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        dialog = QMessageBox.question(self, "Split IMG",
                                    "Split current IMG into multiple files?")
        if dialog == QMessageBox.StandardButton.Yes:
            self.log_message("IMG split functionality coming soon")

    def convert_img(self):
        """Convert IMG between versions"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        self.log_message("IMG conversion functionality coming soon")

    def import_via_tool(self):
        """Import files using external tool"""
        self.log_message("Import via tool functionality coming soon")

    def export_via_tool(self):
        """Export using external tool"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        self.log_message("Export via tool functionality coming soon")

    def remove_all_entries(self):
        """Remove all entries from IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        reply = QMessageBox.question(self, "Remove All",
                                    "Remove all entries from IMG?")
        if reply == QMessageBox.StandardButton.Yes:
            self.current_img.entries.clear()
            self._update_ui_for_loaded_img()
            self.log_message("All entries removed")

    def quick_export(self):
        """Quick export selected files to default location"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No entries selected")
            return

        # Use Documents/IMG_Exports as default
        export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
        os.makedirs(export_dir, exist_ok=True)

        self.log_message(f"Quick exporting {len(selected_rows)} files to {export_dir}")

    def pin_selected(self):
        """Pin selected entries to top of list"""
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Pin", "No entries selected")
            return

        self.log_message(f"Pinned {len(selected_rows)} entries")

    # COL and editor functions
    def open_col_editor(self):
        """Open COL file editor"""
        self.log_message("COL editor functionality coming soon")

    def open_txd_editor(self):
        """Open TXD texture editor"""
        self.log_message("TXD editor functionality coming soon")

    def open_dff_editor(self):
        """Open DFF model editor"""
        self.log_message("DFF editor functionality coming soon")

    def open_ipf_editor(self):
        """Open IPF animation editor"""
        self.log_message("IPF editor functionality coming soon")

    def open_ipl_editor(self):
        """Open IPL item placement editor"""
        self.log_message("IPL editor functionality coming soon")

    def open_ide_editor(self):
        """Open IDE item definition editor"""
        self.log_message("IDE editor functionality coming soon")

    def open_dat_editor(self):
        """Open DAT file editor"""
        self.log_message("DAT editor functionality coming soon")

    def open_zons_editor(self):
        """Open zones editor"""
        self.log_message("Zones editor functionality coming soon")

    def open_weap_editor(self):
        """Open weapons editor"""
        self.log_message("Weapons editor functionality coming soon")

    def open_vehi_editor(self):
        """Open vehicles editor"""
        self.log_message("Vehicles editor functionality coming soon")

    def open_radar_map(self):
        """Open radar map editor"""
        self.log_message("Radar map functionality coming soon")

    def open_paths_map(self):
        """Open paths map editor"""
        self.log_message("Paths map functionality coming soon")

    def open_waterpro(self):
        """Open water properties editor"""
        self.log_message("Water properties functionality coming soon")


    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.log_message(f"Closed: {os.path.basename(self.current_img.file_path)}")
            self.current_img = None
            self.gui_layout.table.setRowCount(0)
            self.gui_layout.update_img_info("No IMG loaded")
            self.setWindowTitle("IMG Factory 1.5")

    def rebuild_img(self):
        """Rebuild current IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        try:
            self.log_message("Rebuilding IMG file...")
            self.gui_layout.show_progress(0, "Rebuilding...")
            
            # Rebuild the IMG file
            if self.current_img.rebuild():
                self.log_message("IMG file rebuilt successfully")
                self.gui_layout.show_progress(-1, "Rebuild complete")
                QMessageBox.information(self, "Success", "IMG file rebuilt successfully!")
            else:
                self.log_message("Failed to rebuild IMG file")
                self.gui_layout.show_progress(-1, "Rebuild failed")
                QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
                
        except Exception as e:
            error_msg = f"Error rebuilding IMG: {str(e)}"
            self.log_message(error_msg)
            self.gui_layout.show_progress(-1, "Error")
            QMessageBox.critical(self, "Rebuild Error", error_msg)

    def rebuild_img_as(self):
        """Rebuild IMG file with new name"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Rebuild IMG As", "", 
            "IMG Archives (*.img);;All Files (*)"
        )
        
        if file_path:
            try:
                self.log_message(f"Rebuilding IMG as: {os.path.basename(file_path)}")
                self.gui_layout.show_progress(0, "Rebuilding...")
                
                if self.current_img.rebuild_as(file_path):
                    self.log_message("IMG file rebuilt successfully")
                    self.gui_layout.show_progress(-1, "Rebuild complete")
                    QMessageBox.information(self, "Success", f"IMG file rebuilt as {os.path.basename(file_path)}")
                else:
                    self.log_message("Failed to rebuild IMG file")
                    self.gui_layout.show_progress(-1, "Rebuild failed")
                    QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
                    
            except Exception as e:
                error_msg = f"Error rebuilding IMG: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Error")
                QMessageBox.critical(self, "Rebuild Error", error_msg)

    def import_files(self):
        """Import files into current IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Import Files", "", 
            "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
        )
        
        if file_paths:
            try:
                self.log_message(f"Importing {len(file_paths)} files...")
                self.gui_layout.show_progress(0, "Importing files...")
                
                imported_count = 0
                for i, file_path in enumerate(file_paths):
                    progress = int((i + 1) * 100 / len(file_paths))
                    self.gui_layout.show_progress(progress, f"Importing {os.path.basename(file_path)}")
                    
                    if self.current_img.import_file(file_path):
                        imported_count += 1
                        self.log_message(f"Imported: {os.path.basename(file_path)}")
                
                # Refresh table
                populate_img_table(self.gui_layout.table, self.current_img)
                
                self.log_message(f"Import complete: {imported_count}/{len(file_paths)} files imported")
                self.gui_layout.show_progress(-1, "Import complete")
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")
                
                QMessageBox.information(self, "Import Complete", 
                                      f"Imported {imported_count} of {len(file_paths)} files")
                
            except Exception as e:
                error_msg = f"Error importing files: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Import error")
                QMessageBox.critical(self, "Import Error", error_msg)

    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        selected_rows = []
        for item in self.gui_layout.table.selectedItems():
            if item.column() == 0:  # Only filename column
                selected_rows.append(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select entries to export.")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Export To Folder")
        if export_dir:
            try:
                self.log_message(f"Exporting {len(selected_rows)} entries...")
                self.gui_layout.show_progress(0, "Exporting...")
                
                exported_count = 0
                for i, row in enumerate(selected_rows):
                    progress = int((i + 1) * 100 / len(selected_rows))
                    entry_name = self.gui_layout.table.item(row, 0).text()
                    self.gui_layout.show_progress(progress, f"Exporting {entry_name}")
                    
                    if self.current_img.export_entry(row, export_dir):
                        exported_count += 1
                        self.log_message(f"Exported: {entry_name}")
                
                self.log_message(f"Export complete: {exported_count}/{len(selected_rows)} files exported")
                self.gui_layout.show_progress(-1, "Export complete")
                
                QMessageBox.information(self, "Export Complete", 
                                      f"Exported {exported_count} of {len(selected_rows)} files to {export_dir}")
                
            except Exception as e:
                error_msg = f"Error exporting files: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Export error")
                QMessageBox.critical(self, "Export Error", error_msg)

    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Export All To Folder")
        if export_dir:
            try:
                entry_count = len(self.current_img.entries)
                self.log_message(f"Exporting all {entry_count} entries...")
                self.gui_layout.show_progress(0, "Exporting all...")
                
                exported_count = 0
                for i, entry in enumerate(self.current_img.entries):
                    progress = int((i + 1) * 100 / entry_count)
                    self.gui_layout.show_progress(progress, f"Exporting {entry.name}")
                    
                    if self.current_img.export_entry(i, export_dir):
                        exported_count += 1
                        self.log_message(f"Exported: {entry.name}")
                
                self.log_message(f"Export complete: {exported_count}/{entry_count} files exported")
                self.gui_layout.show_progress(-1, "Export complete")
                
                QMessageBox.information(self, "Export Complete", 
                                      f"Exported {exported_count} of {entry_count} files to {export_dir}")
                
            except Exception as e:
                error_msg = f"Error exporting all files: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Export error")
                QMessageBox.critical(self, "Export Error", error_msg)

    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        selected_rows = []
        for item in self.gui_layout.table.selectedItems():
            if item.column() == 0:  # Only filename column
                selected_rows.append(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select entries to remove.")
            return
        
        # Confirm removal
        entry_names = [self.gui_layout.table.item(row, 0).text() for row in selected_rows]
        reply = QMessageBox.question(
            self, "Confirm Removal", 
            f"Remove {len(selected_rows)} selected entries?\n\n" + "\n".join(entry_names[:5]) + 
            (f"\n... and {len(entry_names) - 5} more" if len(entry_names) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Sort in reverse order to maintain indices
                selected_rows.sort(reverse=True)
                
                removed_count = 0
                for row in selected_rows:
                    entry_name = self.gui_layout.table.item(row, 0).text()
                    if self.current_img.remove_entry(row):
                        removed_count += 1
                        self.log_message(f"Removed: {entry_name}")
                
                # Refresh table
                populate_img_table(self.gui_layout.table, self.current_img)
                
                self.log_message(f"Removal complete: {removed_count} entries removed")
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")
                
                QMessageBox.information(self, "Removal Complete", 
                                      f"Removed {removed_count} entries")
                
            except Exception as e:
                error_msg = f"Error removing entries: {str(e)}"
                self.log_message(error_msg)
                QMessageBox.critical(self, "Removal Error", error_msg)

    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        try:
            self.log_message("Validating IMG file...")
            self.gui_layout.show_progress(0, "Validating...")
            
            validator = IMGValidator()
            validation_result = validator.validate(self.current_img)
            
            self.gui_layout.show_progress(-1, "Validation complete")
            
            if validation_result.is_valid:
                self.log_message("IMG file validation passed")
                QMessageBox.information(self, "Validation Result", "IMG file is valid!")
            else:
                self.log_message(f"IMG file validation failed: {len(validation_result.errors)} errors")
                error_details = "\n".join(validation_result.errors[:10])
                if len(validation_result.errors) > 10:
                    error_details += f"\n... and {len(validation_result.errors) - 10} more errors"
                
                QMessageBox.warning(self, "Validation Failed", 
                                  f"IMG file has {len(validation_result.errors)} validation errors:\n\n{error_details}")
                
        except Exception as e:
            error_msg = f"Error validating IMG: {str(e)}"
            self.log_message(error_msg)
            self.gui_layout.show_progress(-1, "Validation error")
            QMessageBox.critical(self, "Validation Error", error_msg)

    # =============================================================================
    # COL FILE OPERATIONS - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def open_col_file(self):
        """Open COL file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", 
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_file(file_path)
    
    def load_col_file(self, file_path: str):
        """Load COL file"""
        try:
            self.log_message(f"Loading COL: {os.path.basename(file_path)}")
            self.gui_layout.show_progress(0, "Loading COL file...")
            
            # COL loading logic would go here
            # For now, just simulate the loading
            self.current_col = {"file_path": file_path, "type": "COL"}
            
            self.log_message(f"Loaded COL: {os.path.basename(file_path)}")
            self.gui_layout.show_progress(-1, "COL loaded")
            self.gui_layout.update_img_info(f"COL: {os.path.basename(file_path)}")
            
        except Exception as e:
            error_msg = f"Error loading COL: {str(e)}"
            self.log_message(error_msg)
            self.gui_layout.show_progress(-1, "COL load error")
            QMessageBox.critical(self, "COL Loading Error", error_msg)

    # =============================================================================
    # TEMPLATE MANAGEMENT - KEEP 100% OF FUNCTIONALITY  
    # =============================================================================

    def manage_templates(self):
        """Show template manager dialog"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.template_selected.connect(self._apply_template)
        dialog.exec()

    def _apply_template(self, template_data):
        """Apply template to create new IMG"""
        try:
            self.log_message(f"Applying template: {template_data.get('name', 'Unknown')}")
            
            # Template application logic
            creator = EnhancedIMGCreator()
            if creator.create_from_template(template_data):
                self.log_message("Template applied successfully")
                # Optionally load the created IMG
                if 'output_path' in template_data:
                    self.load_img_file(template_data['output_path'])
            else:
                self.log_message("Failed to apply template")
                
        except Exception as e:
            error_msg = f"Error applying template: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "Template Error", error_msg)

    # =============================================================================
    # SETTINGS AND DIALOGS - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def show_theme_settings(self):
        """Show theme settings dialog"""
        # This would open a dedicated theme settings dialog
        self.show_settings()  # For now, use general settings

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>IMG Factory 1.5</h2>
        <p><b>Professional IMG Archive Manager</b></p>
        <p>Version: 1.5.0 Python Edition</p>
        <p>Author: X-Seti</p>
        <p>Based on original IMG Factory by MexUK (2007)</p>
        <br>
        <p>Features:</p>
        <ul>
        <li>IMG file creation and editing</li>
        <li>Multi-format support (DFF, TXD, COL, IFP)</li>
        <li>Template system</li>
        <li>Batch operations</li>
        <li>Validation tools</li>
        </ul>
        """
        
        QMessageBox.about(self, "About IMG Factory", about_text)

    def show_gui_settings(self):
        """Show GUI settings dialog - ADD THIS METHOD TO YOUR MAIN WINDOW CLASS"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QGroupBox

        dialog = QDialog(self)
        dialog.setWindowTitle("GUI Layout Settings")
        dialog.setMinimumSize(500, 250)

        layout = QVBoxLayout(dialog)

        # Panel width group
        width_group = QGroupBox("📏 Right Panel Width Settings")
        width_layout = QVBoxLayout(width_group)

        # Current width display
        current_width = self.gui_layout.main_splitter.sizes()[1] if len(self.gui_layout.main_splitter.sizes()) > 1 else 240

        # Width spinner
        spinner_layout = QHBoxLayout()
        spinner_layout.addWidget(QLabel("Width:"))
        width_spin = QSpinBox()
        width_spin.setRange(180, 400)
        width_spin.setValue(current_width)
        width_spin.setSuffix(" px")
        spinner_layout.addWidget(width_spin)
        spinner_layout.addStretch()
        width_layout.addLayout(spinner_layout)

        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Presets:"))
        presets = [("Narrow", 200), ("Default", 240), ("Wide", 280), ("Extra Wide", 320)]
        for name, value in presets:
            btn = QPushButton(f"{name}\n({value}px)")
            btn.clicked.connect(lambda checked, v=value: width_spin.setValue(v))
            presets_layout.addWidget(btn)
        presets_layout.addStretch()
        width_layout.addLayout(presets_layout)

        layout.addWidget(width_group)

        # Buttons
        button_layout = QHBoxLayout()

        preview_btn = QPushButton("👁️ Preview")
        def preview_changes():
            width = width_spin.value()
            sizes = self.gui_layout.main_splitter.sizes()
            if len(sizes) >= 2:
                self.gui_layout.main_splitter.setSizes([sizes[0], width])

            right_widget = self.gui_layout.main_splitter.widget(1)
            if right_widget:
                right_widget.setMaximumWidth(width + 60)
                right_widget.setMinimumWidth(max(180, width - 40))

        preview_btn.clicked.connect(preview_changes)
        button_layout.addWidget(preview_btn)

        apply_btn = QPushButton("✅ Apply & Close")
        def apply_changes():
            width = width_spin.value()
            sizes = self.gui_layout.main_splitter.sizes()
            if len(sizes) >= 2:
                self.gui_layout.main_splitter.setSizes([sizes[0], width])

            right_widget = self.gui_layout.main_splitter.widget(1)
            if right_widget:
                right_widget.setMaximumWidth(width + 60)
                right_widget.setMinimumWidth(max(180, width - 40))

            # Save to settings if you have app_settings
            if hasattr(self, 'app_settings'):
                self.app_settings.current_settings["right_panel_width"] = width
                self.app_settings.save_settings()

            self.log_message(f"Right panel width set to {width}px")
            dialog.accept()

        apply_btn.clicked.connect(apply_changes)
        button_layout.addWidget(apply_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def show_gui_layout_settings(self):
        """Show GUI Layout settings - called from menu"""
        if hasattr(self, 'gui_layout'):
            self.gui_layout.show_gui_layout_settings()
        else:
            self.log_message("GUI Layout not available")

        # ADD THIS TO YOUR MENU CREATION (in your _create_menu or create_menu_bar method):
        # Find where you create the Settings menu and add:

    def show_settings(self):
        """Show settings dialog"""
        print("show_settings called!")  # Debug
        try:
            from app_settings_system import SettingsDialog
            dialog = SettingsDialog(self.app_settings, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                from app_settings_system import apply_theme_to_app
                apply_theme_to_app(QApplication.instance(), self.app_settings)
                self.gui_layout.apply_table_theme()
                self.log_message("Settings updated")
        except Exception as e:
            print(f"Settings error: {e}")
            self.log_message(f"Settings error: {str(e)}")

    def show_theme_settings(self):
        """Show theme settings dialog"""
        print("show_theme_settings called!")  # Debug
        self.show_settings()

    def manage_templates(self):
        """Show template manager dialog"""
        try:
            dialog = TemplateManagerDialog(self.template_manager, self)
            dialog.template_selected.connect(self._apply_template)
            dialog.exec()
        except Exception as e:
            self.log_message(f"Template manager not available: {str(e)}")

    def _apply_template(self, template_data):
        """Apply template to create new IMG"""
        self.log_message(f"Template applied: {template_data.get('name', 'Unknown')}")

    def show_gui_layout_settings(self):
        """Show GUI Layout settings - called from menu"""
        if hasattr(self, 'gui_layout'):
            self.gui_layout.show_gui_layout_settings()
        else:
            self.log_message("GUI Layout not available")

    # =============================================================================
    # SETTINGS PERSISTENCE - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def _restore_settings(self):
        """Restore application settings"""
        try:
            settings = QSettings("XSeti", "IMGFactory")
            
            # Restore window geometry
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            # Restore splitter state
            splitter_state = settings.value("splitter_state")
            if splitter_state and hasattr(self.gui_layout, 'main_splitter'):
                self.gui_layout.main_splitter.restoreState(splitter_state)
            
            self.log_message("Settings restored")
            
        except Exception as e:
            self.log_message(f"Failed to restore settings: {str(e)}")

    def _save_settings(self):
        """Save application settings"""
        try:
            settings = QSettings("XSeti", "IMGFactory")
            
            # Save window geometry
            settings.setValue("geometry", self.saveGeometry())
            
            # Save splitter state
            if hasattr(self.gui_layout, 'main_splitter'):
                settings.setValue("splitter_state", self.gui_layout.main_splitter.saveState())
            
            self.log_message("Settings saved")
            
        except Exception as e:
            self.log_message(f"Failed to save settings: {str(e)}")

    def closeEvent(self, event):
        """Handle application close"""
        self._save_settings()
        
        # Clean up threads
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.quit()
            self.load_thread.wait()
        
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    app.setOrganizationName("X-Seti")
    
    # Load settings
    try:
        settings = AppSettings()
        settings.load_settings()
    except Exception as e:
        print(f"Warning: Could not load settings: {str(e)}")
        settings = {}
    
    # Create main window
    window = IMGFactory(settings)
    
    # Show window
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
