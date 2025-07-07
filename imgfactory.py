#!/usr/bin/env python3
"""
X-Seti - JUNE25 2025 - IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""
#this belongs in root /imgfactory.py - version 60
import sys
import os
import mimetypes
from typing import Optional, List, Dict, Any
from pathlib import Path
print("Starting application...")

# Setup paths FIRST - before any other imports
current_dir = Path(__file__).parent
components_dir = current_dir / "components"
gui_dir = current_dir / "gui"
utils_dir = current_dir / "utils"

# Add directories to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if components_dir.exists() and str(components_dir) not in sys.path:
    sys.path.insert(0, str(components_dir))
if gui_dir.exists() and str(gui_dir) not in sys.path:
    sys.path.insert(0, str(gui_dir))
if utils_dir.exists() and str(utils_dir) not in sys.path:  # ADD THESE LINES
    sys.path.insert(0, str(utils_dir))

# Now continue with other imports

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QDialog,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton, QToolBar

)
print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut

# OR use the full path:
from utils.app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog

from components.img_creator import NewIMGDialog
from components.img_core_classes import (
    IMGFile, IMGEntry, IMGVersion, Platform, format_file_size,
    IMGEntriesTable, FilterPanel, IMGFileInfoPanel,
    TabFilterWidget, integrate_filtering, create_entries_table_panel
)
from components.img_close_functions import install_close_functions, setup_close_manager
from components.img_creator import GameType, NewIMGDialog, IMGCreationThread
from components.img_formats import GameSpecificIMGDialog, IMGCreator
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
#from components.img_threads import IMGLoadThread, IMGSaveThread
from components.img_validator import IMGValidator
#from components.tab_manager import TabManager
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.menu import IMGFactoryMenuBar


print("Components imported successfully")
COL_INTEGRATION_AVAILABLE = False
COL_SETUP_FUNCTION = None

# FIXED COL INTEGRATION IMPORTS
print("Attempting COL integration...")
COL_INTEGRATION_AVAILABLE = False
COL_SETUP_FUNCTION = None

try:
    # Check if the COL integration module exists
    from components.col_integration import setup_col_integration_full
    COL_INTEGRATION_AVAILABLE = True
    COL_SETUP_FUNCTION = setup_col_integration_full
    print("✅ COL integration loaded successfully")
except ImportError as e:
    print(f"⚠️ COL integration not available: {e}")
    # Create a dummy function to prevent errors
    def setup_col_integration_full(main_window):
        print("COL integration not available")
        return False
    COL_SETUP_FUNCTION = setup_col_integration_full
    COL_INTEGRATION_AVAILABLE = False
except Exception as e:
    print(f"❌ COL integration error: {e}")
    # Create a dummy function to prevent errors
    def setup_col_integration_full(main_window):
        print("COL integration failed to load")
        return False
    COL_SETUP_FUNCTION = setup_col_integration_full
    COL_INTEGRATION_AVAILABLE = False


# Replace the populate_img_table function in imgfactory.py with this improved version:

def populate_img_table(table: QTableWidget, img_file: IMGFile):
    """Populate table with IMG file entries - FIXED VERSION"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return

    entries = img_file.entries
    print(f"DEBUG: Populating table with {len(entries)} entries")

    # Clear existing data first
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        # Name
        table.setItem(row, 0, QTableWidgetItem(entry.name))

        # Type (file extension) - FIXED: Always use name-based detection
        if '.' in entry.name:
            file_type = entry.name.split('.')[-1].upper()
        else:
            file_type = "NO_EXT"

        print(f"DEBUG: Row {row}: {entry.name} -> Type: {file_type}")
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
            elif hasattr(entry, 'version') and entry.version:
                version = str(entry.version)
            else:
                # Provide sensible defaults based on file type
                if file_type in ['DFF', 'TXD']:
                    version = "RenderWare"
                elif file_type == 'COL':
                    version = "COL"
                elif file_type == 'IFP':
                    version = "IFP"
                elif file_type == 'WAV':
                    version = "Audio"
                elif file_type == 'SCM':
                    version = "Script"
                else:
                    version = "Unknown"
        except Exception as e:
            print(f"DEBUG: Version detection error for {entry.name}: {e}")
            version = "Unknown"

        table.setItem(row, 4, QTableWidgetItem(version))

        # Compression
        compression = "None"
        try:
            if hasattr(entry, 'compression_type') and entry.compression_type:
                compression = str(entry.compression_type)
            elif hasattr(entry, 'compressed') and entry.compressed:
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

    print(f"DEBUG: Table population complete. Table now has {table.rowCount()} rows")

    # IMPORTANT: Clear any filters that might be hiding rows
    for row in range(table.rowCount()):
        table.setRowHidden(row, False)

    print(f"DEBUG: All rows made visible")

def setup_debug_mode(self):
    """Setup debug mode integration"""
    self.debug = DebugSettings(self.app_settings)

    # Add debug menu item
    if hasattr(self, 'menu_bar_system'):
        debug_action = QAction("🐛 Debug Mode", self)
        debug_action.setCheckable(True)
        debug_action.setChecked(self.debug.debug_enabled)
        debug_action.triggered.connect(self.toggle_debug_mode)

        # Add to Settings menu
        if hasattr(self.menu_bar_system, 'settings_menu'):
            self.menu_bar_system.settings_menu.addSeparator()
            self.menu_bar_system.settings_menu.addAction(debug_action)

def toggle_debug_mode(self):
    """Toggle debug mode with user feedback"""
    enabled = self.debug.toggle_debug_mode()
    status = "enabled" if enabled else "disabled"
    self.log_message(f"🐛 Debug mode {status}")

    if enabled:
        self.log_message("Debug categories: " + ", ".join(self.debug.debug_categories))
        # Run immediate debug check
        self.debug_img_entries()

def debug_img_entries(self):
    """Enhanced debug function with categories"""
    if not self.debug.is_debug_enabled('TABLE_POPULATION'):
        return

    if not self.current_img or not self.current_img.entries:
        self.debug.debug_log("No IMG loaded or no entries found", 'TABLE_POPULATION', 'WARNING')
        return

    self.debug.debug_log(f"IMG file has {len(self.current_img.entries)} entries", 'TABLE_POPULATION')

    # Count file types
    file_types = {}
    all_extensions = set()
    extension_mismatches = []

    for i, entry in enumerate(self.current_img.entries):
        # Extract extension both ways
        name_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
        attr_ext = getattr(entry, 'extension', 'NO_ATTR').upper() if hasattr(entry, 'extension') and entry.extension else "NO_ATTR"

        all_extensions.add(name_ext)
        file_types[name_ext] = file_types.get(name_ext, 0) + 1

        # Check for extension mismatches
        if name_ext != attr_ext and attr_ext != "NO_ATTR":
            extension_mismatches.append(f"{entry.name}: name='{name_ext}' vs attr='{attr_ext}'")

        # Detailed debug for first 5 entries
        if i < 5:
            self.debug.debug_log(f"Entry {i}: {entry.name} -> {name_ext}", 'TABLE_POPULATION')

    # Summary
    self.debug.debug_log("File type summary:", 'TABLE_POPULATION')
    for ext, count in sorted(file_types.items()):
        self.debug.debug_log(f"  {ext}: {count} files", 'TABLE_POPULATION')

    self.debug.debug_log(f"All extensions found: {sorted(all_extensions)}", 'TABLE_POPULATION')

    # Extension mismatches
    if extension_mismatches:
        self.debug.debug_log(f"Extension mismatches found: {len(extension_mismatches)}", 'TABLE_POPULATION', 'WARNING')
        for mismatch in extension_mismatches[:10]:  # Show first 10
            self.debug.debug_log(f"  {mismatch}", 'TABLE_POPULATION', 'WARNING')

    # Table analysis
    table_rows = self.gui_layout.table.rowCount()
    hidden_count = sum(1 for row in range(table_rows) if self.gui_layout.table.isRowHidden(row))

    self.debug.debug_log(f"Table: {table_rows} rows, {hidden_count} hidden", 'TABLE_POPULATION')

    if hidden_count > 0:
        self.debug.debug_log("Some rows are hidden! Checking filter settings...", 'TABLE_POPULATION', 'WARNING')

        # Check filter combo if it exists
        try:
            # Look for filter combo in right panel
            filter_combo = self.findChild(QComboBox)
            if filter_combo:
                current_filter = filter_combo.currentText()
                self.debug.debug_log(f"Current filter: '{current_filter}'", 'TABLE_POPULATION')
        except:
            pass


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_updated = pyqtSignal(int, str)  # progress, status
    loading_finished = pyqtSignal(object)    # IMGFile object
    loading_error = pyqtSignal(str)          # error message

    """Background thread for loading IMG files"""
    #progress = pyqtSignal(int)
    #finished = pyqtSignal(object)  # IMGFile object
    #error = pyqtSignal(str)

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
        # Initialize template manager - FIXED INDENTATION
        try:
            from components.img_templates import IMGTemplateManager
            self.template_manager = IMGTemplateManager()
            print("✅ Template manager initialized")
        except Exception as e:
            print(f"❌ Template manager initialization failed: {str(e)}")
            # Create dummy template manager as fallback
            class DummyTemplateManager:
                def get_all_templates(self): return []
                def get_default_templates(self): return []
                def get_user_templates(self): return []
            self.template_manager = DummyTemplateManager()

        # Core data
        self.current_img: Optional[IMGFile] = None
        self.current_col: Optional = None  # For COL file support
        self.setup_col_tab_styling()
        self.open_files = {}  # Dict to store open files {tab_index: file_info}
        self.tab_counter = 0  # Counter for unique tab IDs
        self.template_manager = IMGTemplateManager()

        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None

        # Initialize GUI layout
        self.gui_layout = IMGFactoryGUILayout(self)

        # Setup menu bar system
        self.menu_bar_system = IMGFactoryMenuBar(self)

        # Setup menu callbacks - FIXED TO USE WORKING METHOD
        callbacks = {
            "about": self.show_about,
            "open_img": self.open_img_file,  # FIXED: Use method that actually works
            "new_img": self.create_new_img,
            "exit": self.close,
            "img_validate": self.validate_img,
            "customize_interface": self.show_gui_settings,
        }
        self.menu_bar_system.set_callbacks(callbacks)

        # Initialize UI (but without menu creation in gui_layout)
        self._create_ui()
        self._restore_settings()

        try:
            from components.col_integration import setup_col_integration_full
            col_integration_result = setup_col_integration_full(self)
            if col_integration_result:
                self.log_message("✅ COL functionality integrated successfully")
            else:
                self.log_message("⚠️ COL functionality setup failed")
        except ImportError as e:
            self.log_message(f"COL integration not available: {e}")

        # Log startup
        self.log_message("IMG Factory 1.5 initialized")


        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)

        # Apply COL integration after creating the main interface
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

    def debug_img_entries(self):
        """Debug function to check what entries are actually loaded"""
        if not self.current_img or not self.current_img.entries:
            self.log_message("❌ No IMG loaded or no entries found")
            return

        self.log_message(f"🔍 DEBUG: IMG file has {len(self.current_img.entries)} entries")

        # Count file types
        file_types = {}
        all_extensions = set()

        for i, entry in enumerate(self.current_img.entries):
            # Debug each entry
            self.log_message(f"Entry {i}: {entry.name}")

            # Extract extension both ways
            name_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else "NO_EXT"
            attr_ext = getattr(entry, 'extension', 'NO_ATTR').upper() if hasattr(entry, 'extension') and entry.extension else "NO_ATTR"

            all_extensions.add(name_ext)

            # Count by name-based extension
            file_types[name_ext] = file_types.get(name_ext, 0) + 1

            # Log extension differences
            if name_ext != attr_ext:
                self.log_message(f"  ⚠️ Extension mismatch: name='{name_ext}' vs attr='{attr_ext}'")

        # Summary
        self.log_message(f"📊 File type summary:")
        for ext, count in sorted(file_types.items()):
            self.log_message(f"  {ext}: {count} files")

        self.log_message(f"🎯 All extensions found: {sorted(all_extensions)}")

        # Check table row count vs entries count
        table_rows = self.gui_layout.table.rowCount()
        self.log_message(f"📋 Table has {table_rows} rows, IMG has {len(self.current_img.entries)} entries")

        # Check if any rows are hidden
        hidden_count = 0
        for row in range(table_rows):
            if self.gui_layout.table.isRowHidden(row):
                hidden_count += 1

        self.log_message(f"👻 Hidden rows: {hidden_count}")

        if hidden_count > 0:
            self.log_message("⚠️ Some rows are hidden! Check the filter settings.")

    def _unified_double_click_handler(self, row, filename, item):
        """Handle double-click through unified system"""
        # Get the actual filename from the first column (index 0)
        if row < self.gui_layout.table.rowCount():
            name_item = self.gui_layout.table.item(row, 0)
            if name_item:
                actual_filename = name_item.text()
                self.log_message(f"Double-clicked: {actual_filename}")

                # Show file info if IMG is loaded
                if self.current_img and row < len(self.current_img.entries):
                    entry = self.current_img.entries[row]
                    from components.img_core_classes import format_file_size
                    self.log_message(f"File info: {entry.name} ({format_file_size(entry.size)})")
            else:
                self.log_message(f"Double-clicked row {row} (no filename found)")
        else:
            self.log_message(f"Double-clicked: {filename}")

    def _unified_double_click_handler(self, row, filename, item):
        """Handle double-click through unified system"""
        self.log_message(f"Double-clicked: {filename}")

        # TODO: Add double-click functionality (preview, extract, etc.)
        # For now, show info about the item if IMG is loaded
        if self.current_img and row < len(self.current_img.entries):
            entry = self.current_img.entries[row]
            from components.img_core_classes import format_file_size
            self.log_message(f"File info: {entry.name} ({format_file_size(entry.size)})")

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

    def _update_button_states(self, has_selection):
        """Update button enabled/disabled states based on selection"""
        # Enable/disable buttons based on selection and loaded IMG
        has_img = self.current_img is not None

        # Log the button state changes for debugging
        self.log_message(f"Button states updated: selection={has_selection}, img_loaded={has_img}")

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
        """Handle search button/menu"""
        self.log_message("🔍 Search dialog requested")
        # TODO: Implement search dialog

    def import_files(self):
        """Handle import button"""
        self.log_message("📥 Import files requested")

    def export_selected(self):
        """Handle export button"""
        self.log_message("📤 Export selected requested")

    def remove_selected(self):
        """Handle remove button"""
        self.log_message("🗑️ Remove selected requested")

    def refresh_table(self):
        """Handle refresh/update button"""
        self.log_message("🔄 Refresh table requested")

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

    # MODIFIED the _create_ui() method to call setup_unified_signals():

    def _create_ui(self):
        """Create the main user interface - WITH TABS FIXED"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create main tab widget for file handling
        self.main_tab_widget = QTabWidget()
        self.main_tab_widget.setTabsClosable(True)
        #self.main_tab_widget.tabCloseRequested.connect(self._close_tab)
        #self.main_tab_widget.currentChanged.connect(self._on_tab_changed)

        # Initialize open files tracking
        self.open_files = {}

        # Create initial empty tab
        self._create_initial_tab()

        self.close_manager = install_close_functions(self)
        self.main_tab_widget.tabCloseRequested.connect(self.close_manager.close_tab)
        # Add tab widget to main layout
        main_layout.addWidget(self.main_tab_widget)

        # Create GUI layout system (single instance)
        #self.gui_layout.create_main_ui_with_splitters()
        self.gui_layout.create_status_bar()
        self.gui_layout.apply_table_theme()

        # Setup unified signal system
        self.setup_unified_signals()

    def _create_initial_tab(self):
        """Create initial empty tab"""
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create GUI layout for this tab
        self.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Add tab with "No file" label
        self.main_tab_widget.addTab(tab_widget, "📁 No File")

    def _on_tab_changed(self, index):
        """Handle tab change - FIXED"""
        if index == -1:
            return

        self.log_message(f"🔄 Tab changed to: {index}")

        # Update current file based on tab
        if index in self.open_files:
            file_info = self.open_files[index]
            self.log_message(f"📂 Tab {index} has file: {file_info.get('file_path', 'Unknown')}")

            if file_info['type'] == 'IMG':
                self.current_img = file_info['file_object']
                self.current_col = None
            elif file_info['type'] == 'COL':
                self.current_col = file_info['file_object']
                self.current_img = None

            # Update UI for current file
            self._update_ui_for_current_file()
        else:
            # No file in this tab
            self.log_message(f"📭 Tab {index} is empty")
            self.current_img = None
            self.current_col = None
            self._update_ui_for_no_img()

    def _update_ui_for_current_file(self):
        """Update UI for currently selected file - FIXED"""
        if self.current_img:
            self.log_message("🔄 Updating UI for IMG file")
            self._update_ui_for_loaded_img()
        elif self.current_col:
            self.log_message("🔄 Updating UI for COL file")
            self._update_ui_for_loaded_col()
        else:
            self.log_message("🔄 Updating UI for no file")
            self._update_ui_for_no_img()

    def _update_ui_for_loaded_img(self):
        """Update UI when IMG file is loaded - FIXED: Complete implementation"""
        if not self.current_img:
            self.log_message("⚠️ _update_ui_for_loaded_img called but no current_img")
            return

        # Update window title
        file_name = os.path.basename(self.current_img.file_path)
        self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Populate table with IMG entries
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            self._populate_real_img_table(self.current_img)
            self.log_message(f"📋 Table populated with {len(self.current_img.entries)} entries")
        else:
            self.log_message("⚠️ GUI layout or table not available")

        # Update status
        if hasattr(self, 'gui_layout'):
            entry_count = len(self.current_img.entries) if self.current_img.entries else 0
            self.gui_layout.show_progress(-1, f"Loaded: {entry_count} entries")

            if hasattr(self.gui_layout, 'update_img_info'):
                self.gui_layout.update_img_info(f"IMG: {file_name}")

        self.log_message("✅ IMG UI updated successfully")

    def handle_action(self, action_name):
        """Handle unified action signals - UPDATED with missing methods"""
        try:
            action_map = {
                # File operations
                'open_img_file': self.open_img_file,
                'close_img_file': self.close_manager.close_img_file if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all': self.close_manager.close_all_tabs if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': self.close_all_img,  # Added
                'create_new_img': self.create_new_img,
                'refresh_table': self.refresh_table,

                # Entry operations
                'import_files': self.import_files,
                'export_selected': self.export_selected,
                'remove_selected': self.remove_selected,
                'select_all_entries': self.select_all_entries,

                # IMG operations
                'rebuild_img': self.rebuild_img,
                'rebuild_img_as': self.rebuild_img_as,
                'rebuild_all_img': self.rebuild_all_img,  # Added
                'merge_img': self.merge_img,              # Added
                'split_img': self.split_img,              # Added
                'convert_img_format': self.convert_img_format,  # Added

                # System
                'show_search_dialog': self.show_search_dialog,
            }

            if action_name in action_map:
                self.log_message(f"🎯 Action: {action_name}")
                action_map[action_name]()
            else:
                self.log_message(f"⚠️ Method '{action_name}' not implemented")

        except Exception as e:
            self.log_message(f"❌ Action error ({action_name}): {str(e)}")


    # Update the setup_menu_connections method:

    def setup_menu_connections(self):
        """Setup menu connections - UPDATED for unified file loading"""
        try:
            menu_callbacks = {
                'new_img': self.create_new_img,
                'open_img': self.open_file_dialog,  # UPDATED: Use unified loader
                'close_img': self.close_manager.close_img_file,
                'close_all': self.close_manager.close_all_tabs,
                'exit': self.close,
                'select_all': self.select_all_entries,
                'find': self.show_search_dialog,
                'entry_import': self.import_files,
                'entry_export': self.export_selected,
                'entry_remove': self.remove_selected,
                'img_rebuild': self.rebuild_img,
                'img_rebuild_as': self.rebuild_img_as,
            }

            if hasattr(self, 'menu_bar_system') and hasattr(self.menu_bar_system, 'set_callbacks'):
                self.menu_bar_system.set_callbacks(menu_callbacks)

            self.log_message("✅ Menu connections established (unified file loading)")

        except Exception as e:
            self.log_message(f"❌ Menu connection error: {str(e)}")

    def _update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded - FIXED"""
        if not self.current_col:
            return

        try:
            # Update window title
            file_name = os.path.basename(self.current_col.file_path)
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

            # Update table with COL models info
            if hasattr(self, 'gui_layout') and self.gui_layout.table:
                models = self.current_col.models if hasattr(self.current_col, 'models') else []
                self.gui_layout.table.setRowCount(len(models))

                for row, model in enumerate(models):
                    items = [
                        (model.name if hasattr(model, 'name') else f"Model_{row}",
                        "COL",
                        f"v{model.version.value}" if hasattr(model, 'version') else "Unknown",
                        f"{len(model.spheres) if hasattr(model, 'spheres') else 0}S/"
                        f"{len(model.boxes) if hasattr(model, 'boxes') else 0}B/"
                        f"{len(model.meshes) if hasattr(model, 'meshes') else 0}M",
                        "COL",
                        "None",
                        "Loaded")
                    ]

                    for col, value in enumerate(items[0]):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.gui_layout.table.setItem(row, col, item)

            # Update status
            if hasattr(self, 'gui_layout'):
                model_count = len(self.current_col.models) if hasattr(self.current_col, 'models') else 0
                self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

                if hasattr(self.gui_layout, 'update_img_info'):
                    self.gui_layout.update_img_info(f"COL: {file_name}")

            self.log_message("✅ COL UI updated successfully")

        except Exception as e:
            self.log_message(f"❌ Error updating COL UI: {str(e)}")

    def _create_initial_tab(self):
        """Create initial empty tab"""
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # FIXED: Use the correct method name
        self.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Add tab with "No file" label
        self.main_tab_widget.addTab(tab_widget, "📁 No File")

    def handle_menu_search(self):
        """Handle search from menu (Ctrl+F)"""
        self.show_search_dialog()


    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)
        # Delegate to GUI layout
        self.gui_layout.handle_resize_event(event)

    def log_message(self, message):
        """Log a message to the activity log"""
        print(f"LOG: {message}")  # Temporary - shows in console

        # Try different log methods
        if hasattr(self.gui_layout, 'log_message'):
            self.gui_layout.log_message(message)
        elif hasattr(self.gui_layout, 'log') and hasattr(self.gui_layout.log, 'append'):
            from PyQt6.QtCore import QDateTime
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            self.gui_layout.log.append(f"[{timestamp}] {message}")
        else:
            # Fallback - create a simple log in status bar
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(message)

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
        """Show new IMG creation dialog - FIXED: No signal connections"""
        dialog = GameSpecificIMGDialog(self)
        dialog.template_manager = self.template_manager
        # Set template manager if dialog supports it
        if hasattr(dialog, 'template_manager'):
            dialog.template_manager = self.template_manager

            # Execute dialog and check result
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Get the output path from the dialog
                if hasattr(dialog, 'output_path') and dialog.output_path:
                    output_path = dialog.output_path
                    self.log_message(f"✅ Created: {os.path.basename(output_path)}")

                    # Load the created IMG file in a new tab
                    self._load_img_file_in_new_tab(output_path)

    def open_img_file(self):
        """Open file dialog - REDIRECTS to unified loader"""
        self.open_file_dialog()

    def _detect_and_open_file(self, file_path: str) -> bool:
        """Detect file type and open with appropriate handler"""
        try:
            # First check by extension
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.img':
                self.load_img_file(file_path)
                return True
            elif file_ext == '.col':
                self._load_col_file(file_path)
                return True

            # If extension is ambiguous, check file content
            with open(file_path, 'rb') as f:
                header = f.read(16)

            if len(header) < 4:
                return False

            # Check for IMG signatures
            if header[:4] in [b'VER2', b'VER3']:
                self.log_message(f"🔍 Detected IMG file by signature")
                self.load_img_file(file_path)
                return True

            # Check for COL signatures
            elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                self.log_message(f"🔍 Detected COL file by signature")
                self._load_col_file(file_path)
                return True

            # Try reading as IMG version 1 (no header signature)
            elif len(header) >= 8:
                # Could be IMG v1 or unknown format
                self.log_message(f"🔍 Attempting to open as IMG file")
                self.load_img_file(file_path)
                return True

            return False

        except Exception as e:
            self.log_message(f"❌ Error detecting file type: {str(e)}")
            return False

    def open_file_dialog(self):
        """Unified file dialog for IMG and COL files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG/COL Archive", "",
            "All Supported (*.img *.col);;IMG Archives (*.img);;COL Archives (*.col);;All Files (*)")

        if file_path:
            self.load_file_unified(file_path)

    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type by extension and content"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.img':
                return "IMG"
            elif file_ext == '.col':
                return "COL"

            # Check file content if extension is ambiguous
            with open(file_path, 'rb') as f:
                header = f.read(16)

            if len(header) < 4:
                return "UNKNOWN"

            # Check for IMG signatures
            if header[:4] in [b'VER2', b'VER3']:
                return "IMG"

            # Check for COL signatures
            elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return "COL"

            # Default to IMG for unknown formats
            return "IMG"

        except Exception as e:
            self.log_message(f"❌ Error detecting file type: {str(e)}")
            return "UNKNOWN"

    def _load_col_file_safely(self, file_path):
        """Load COL file safely without breaking if COL classes don't exist"""
        try:
            # Try to import COL classes
            from components.col_core_classes import COLFile

            # Create COL file object
            col_file = COLFile(file_path)
            if not col_file.load():
                raise Exception(f"Failed to load COL file: {file_path}")

            # Set current COL
            self.current_col = col_file

            # Update UI for COL file
            self._update_ui_for_loaded_col_safe()

            self.log_message(f"✅ Loaded COL: {os.path.basename(file_path)}")

        except ImportError:
            self.log_message("❌ COL classes not available - loading as generic file")
            # Fallback to basic handling
            self._load_col_as_generic_file(file_path)
        except Exception as e:
            error_msg = f"Error loading COL file: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "COL Load Error", error_msg)

    def _load_col_as_generic_file(self, file_path):
        """Load COL as generic file when COL classes aren't available"""
        try:
            # Create simple COL representation
            self.current_col = {
                "file_path": file_path,
                "type": "COL",
                "size": os.path.getsize(file_path)
            }

            # Update UI
            self._update_ui_for_loaded_col_safe()

            self.log_message(f"✅ Loaded COL (generic): {os.path.basename(file_path)}")

        except Exception as e:
            self.log_message(f"❌ Error loading COL as generic: {str(e)}")


    def load_file_unified(self, file_path: str):
        """Unified file loader with proper type detection"""
        try:
            file_type = self._detect_file_type(file_path)

            if file_type == "IMG":
                self.log_message(f"📁 Loading IMG: {os.path.basename(file_path)}")
                self._load_img_file_in_new_tab(file_path)
            elif file_type == "COL":
                self.log_message(f"🔧 Loading COL: {os.path.basename(file_path)}")
                self._load_col_file_safely(file_path)
            else:
                self.log_message(f"❌ Unsupported file type: {file_path}")
                QMessageBox.warning(self, "Unsupported File",
                                  f"File type not supported: {os.path.basename(file_path)}")

        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "File Load Error", error_msg)

    def _load_col_file_in_new_tab(self, file_path):
        """Load COL file in new tab - FIXED to use proper COL objects"""
        try:
            # Import COL classes
            from components.col_core_classes import COLFile

            # Create new tab if current tab has a file
            current_index = self.main_tab_widget.currentIndex()
            if current_index in self.open_files:
                self.close_manager.create_new_tab()
                current_index = self.main_tab_widget.currentIndex()

            # Create proper COL file object
            col_file = COLFile(file_path)
            if not col_file.load():
                raise Exception(f"Failed to load COL file: {file_path}")

            # Set current COL
            self.current_col = col_file

            # Store file info with proper structure
            file_name = os.path.basename(file_path)
            tab_name = f"🔧 {file_name}"

            self.open_files[current_index] = {
                'type': 'COL',
                'file_path': file_path,
                'file_object': col_file,
                'tab_name': tab_name
            }

            # Update tab name
            self.main_tab_widget.setTabText(current_index, tab_name)

            # Update UI
            self._update_ui_for_loaded_col()

            self.log_message(f"✅ Loaded COL: {file_name} ({len(col_file.models)} models)")

        except Exception as e:
            error_msg = f"Error loading COL file: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "COL Load Error", error_msg)


    def _load_img_file_in_new_tab(self, file_path):
        """Load IMG file in new tab - logic using close manager"""
        current_index = self.main_tab_widget.currentIndex()

        # Check if current tab is empty (no file loaded)
        if current_index not in self.open_files:
            # Current tab is empty, use it
            self.log_message(f"Using current empty tab for: {os.path.basename(file_path)}")
        else:
            # Current tab has a file, create new tab using close manager
            self.log_message(f"Creating new tab for: {os.path.basename(file_path)}")
            self.close_manager.create_new_tab()  # Updated to use close manager
            current_index = self.main_tab_widget.currentIndex()

        # Store file info BEFORE loading
        file_name = os.path.basename(file_path)
        # Remove .img extension for cleaner tab names
        if file_name.lower().endswith('.img'):
            file_name_clean = file_name[:-4]  # Remove last 4 characters (.img)
        else:
            file_name_clean = file_name
        tab_name = f"📁 {file_name_clean}"

        self.open_files[current_index] = {
            'type': 'IMG',
            'file_path': file_path,
            'file_object': None,  # Will be set when loaded
            'tab_name': tab_name
        }

        # Update tab name immediately
        self.main_tab_widget.setTabText(current_index, tab_name)

        # Start loading
        self.load_img_file(file_path)

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

    # REPLACE THE EXISTING open_img_file method
    def open_img_file(self):
        """Open file dialog - REDIRECTS to unified loader"""
        self.open_file_dialog()

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

    def _update_ui_for_loaded_col_safe(self):
        """Update UI when COL file is loaded - USES SAME FORMAT AS IMG"""
        if not self.current_col:
            return

        try:
            # Handle both COL object and dictionary formats
            if hasattr(self.current_col, 'file_path'):
                file_path = self.current_col.file_path
                col_file = self.current_col
            elif isinstance(self.current_col, dict):
                file_path = self.current_col.get('file_path', 'Unknown')
                # Try to load as proper COL file
                try:
                    from components.col_core_classes import COLFile
                    col_file = COLFile(file_path)
                    if col_file.load():
                        self.current_col = col_file
                    else:
                        col_file = None
                except:
                    col_file = None
            else:
                file_path = str(self.current_col)
                col_file = None

            file_name = os.path.basename(file_path)

            # Update window title
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

            # Populate table with COL models using IMG format
            if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
                self._populate_col_table_img_format(col_file, file_name)

            # Update status
            if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_progress'):
                model_count = len(col_file.models) if col_file and hasattr(col_file, 'models') else 0
                self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

            self.log_message("✅ COL UI updated successfully")

        except Exception as e:
            self.log_message(f"❌ Error updating COL UI: {str(e)}")

    def _populate_col_table_img_format(self, col_file, file_name):
        """Populate table with COL models using same format as IMG entries"""
        from PyQt6.QtWidgets import QTableWidgetItem
        from PyQt6.QtCore import Qt

        table = self.gui_layout.table

        # Keep the same 7-column format as IMG files
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Version", "Compression", "Status"
        ])

        if not col_file or not hasattr(col_file, 'models') or not col_file.models:
            # Show the file itself if no models
            table.setRowCount(1)

            try:
                file_size = os.path.getsize(col_file.file_path) if col_file and col_file.file_path else 0
                size_text = self._format_file_size(file_size)
            except:
                size_text = "Unknown"

            items = [
                (file_name, "COL", size_text, "0x0", "Unknown", "None", "No Models")
            ]

            for row, item_data in enumerate(items):
                for col, value in enumerate(item_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row, col, item)

            self.log_message(f"📋 COL file loaded but no models found")
            return

        # Show individual models in IMG entry format
        models = col_file.models
        table.setRowCount(len(models))

        self.log_message(f"📋 Populating table with {len(models)} COL models")

        virtual_offset = 0x0  # Virtual offset for COL models

        for row, model in enumerate(models):
            try:
                # Name - use model name or generate one
                model_name = model.name if model.name else f"Model_{row}"
                table.setItem(row, 0, QTableWidgetItem(model_name))

                # Type - just "COL" (like IMG shows "DFF", "TXD", etc.)
                table.setItem(row, 1, QTableWidgetItem("COL"))

                # Size - estimate model size in same format as IMG
                estimated_size = self._estimate_col_model_size_bytes(model)
                size_text = self._format_file_size(estimated_size)
                table.setItem(row, 2, QTableWidgetItem(size_text))

                # Offset - virtual hex offset (like IMG entries)
                offset_text = f"0x{virtual_offset:X}"
                table.setItem(row, 3, QTableWidgetItem(offset_text))
                virtual_offset += estimated_size  # Increment for next model

                # Version - show just the COL version number (1, 2, 3, or 4)
                if hasattr(model, 'version'):
                    version_text = str(model.version.value)  # Just "1", "2", "3", or "4"
                else:
                    version_text = "Unknown"
                table.setItem(row, 4, QTableWidgetItem(version_text))

                # Compression - always None for COL models
                table.setItem(row, 5, QTableWidgetItem("None"))

                # Status - based on model content (like IMG status)
                stats = model.get_stats() if hasattr(model, 'get_stats') else {}
                total_elements = stats.get('total_elements', 0)

                if total_elements == 0:
                    status = "Empty"
                elif total_elements > 500:
                    status = "Complex"
                elif total_elements > 100:
                    status = "Medium"
                else:
                    status = "Ready"
                table.setItem(row, 6, QTableWidgetItem(status))

                # Make all items read-only (same as IMG)
                for col in range(7):
                    item = table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            except Exception as e:
                self.log_message(f"❌ Error populating COL model {row}: {str(e)}")
                # Create fallback row (same as IMG error handling)
                table.setItem(row, 0, QTableWidgetItem(f"Model_{row}"))
                table.setItem(row, 1, QTableWidgetItem("COL"))
                table.setItem(row, 2, QTableWidgetItem("0 B"))
                table.setItem(row, 3, QTableWidgetItem("0x0"))
                table.setItem(row, 4, QTableWidgetItem("Unknown"))
                table.setItem(row, 5, QTableWidgetItem("None"))
                table.setItem(row, 6, QTableWidgetItem("Error"))

        # Auto-resize columns (optional, IMG doesn't do this but it's helpful)
        # table.resizeColumnsToContents()

        self.log_message(f"✅ Table populated with {len(models)} COL models (IMG format)")

    def _estimate_col_model_size_bytes(self, model):
        """Estimate COL model size in bytes (similar to IMG entry sizes)"""
        try:
            if not hasattr(model, 'get_stats'):
                return 1024  # Default 1KB

            stats = model.get_stats()

            # Rough estimation based on collision elements
            size = 100  # Base model overhead (header, name, etc.)
            size += stats.get('spheres', 0) * 16     # 16 bytes per sphere
            size += stats.get('boxes', 0) * 24       # 24 bytes per box
            size += stats.get('vertices', 0) * 12    # 12 bytes per vertex
            size += stats.get('faces', 0) * 8        # 8 bytes per face
            size += stats.get('face_groups', 0) * 8  # 8 bytes per face group

            # Add version-specific overhead
            if hasattr(model, 'version'):
                if model.version.value >= 3:
                    size += stats.get('shadow_vertices', 0) * 12
                    size += stats.get('shadow_faces', 0) * 8
                    size += 64  # COL3+ additional headers
                elif model.version.value >= 2:
                    size += 48  # COL2 headers

            return max(size, 64)  # Minimum 64 bytes

        except Exception:
            return 1024  # Default 1KB on error

    def _format_file_size(self, size_bytes):
        """Format file size same as IMG entries"""
        try:
            # Use the same formatting as IMG entries
            if hasattr(self, 'current_img'):  # Check if format_file_size is available
                try:
                    from components.img_core_classes import format_file_size
                    return format_file_size(size_bytes)
                except:
                    pass

            # Fallback formatting (same logic as IMG)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes // 1024} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes // (1024 * 1024)} MB"
            else:
                return f"{size_bytes // (1024 * 1024 * 1024)} GB"

        except Exception:
            return f"{size_bytes} bytes"

    def get_col_model_details_for_display(self, model, row_index):
        """Get COL model details in same format as IMG entry details"""
        try:
            stats = model.get_stats() if hasattr(model, 'get_stats') else {}

            details = {
                'name': model.name or f"Model_{row_index}",
                'type': "COL",
                'size': self._estimate_col_model_size_bytes(model),
                'version': str(model.version.value) if hasattr(model, 'version') else "Unknown",
                'elements': stats.get('total_elements', 0),
                'spheres': stats.get('spheres', 0),
                'boxes': stats.get('boxes', 0),
                'faces': stats.get('faces', 0),
                'vertices': stats.get('vertices', 0),
            }

            if hasattr(model, 'bounding_box') and model.bounding_box:
                bbox = model.bounding_box
                details.update({
                    'bbox_center': (bbox.center.x, bbox.center.y, bbox.center.z),
                    'bbox_radius': bbox.radius,
                    'bbox_min': (bbox.min.x, bbox.min.y, bbox.min.z),
                    'bbox_max': (bbox.max.x, bbox.max.y, bbox.max.z),
                })

            return details

        except Exception as e:
            self.log_message(f"❌ Error getting COL model details: {str(e)}")
            return {
                'name': f"Model_{row_index}",
                'type': "COL",
                'size': 0,
                'version': "Unknown",
                'elements': 0,
            }

    def show_col_model_details_img_style(self, model_index):
        """Show COL model details in same style as IMG entry details"""
        try:
            if (not hasattr(self, 'current_col') or
                not hasattr(self.current_col, 'models') or
                model_index >= len(self.current_col.models)):
                return

            model = self.current_col.models[model_index]
            details = self.get_col_model_details_for_display(model, model_index)

            from PyQt6.QtWidgets import QMessageBox

            info_lines = []
            info_lines.append(f"Name: {details['name']}")
            info_lines.append(f"Type: {details['type']}")
            info_lines.append(f"Size: {self._format_file_size(details['size'])}")
            info_lines.append(f"Version: {details['version']}")
            info_lines.append("")
            info_lines.append("Collision Data:")
            info_lines.append(f"  Total Elements: {details['elements']}")
            info_lines.append(f"  Spheres: {details['spheres']}")
            info_lines.append(f"  Boxes: {details['boxes']}")
            info_lines.append(f"  Faces: {details['faces']}")
            info_lines.append(f"  Vertices: {details['vertices']}")

            if 'bbox_center' in details:
                info_lines.append("")
                info_lines.append("Bounding Box:")
                center = details['bbox_center']
                info_lines.append(f"  Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
                info_lines.append(f"  Radius: {details['bbox_radius']:.2f}")

            QMessageBox.information(
                self,
                f"COL Model Details - {details['name']}",
                "\n".join(info_lines)
            )

        except Exception as e:
            self.log_message(f"❌ Error showing COL model details: {str(e)}")

    # Update the double-click handler to use the new style
    def _on_col_table_double_click(self, item):
        """Handle double-click on COL table item - IMG style"""
        try:
            if hasattr(self, 'current_col') and hasattr(self.current_col, 'models'):
                row = item.row()
                self.show_col_model_details_img_style(row)
            else:
                self.log_message("No COL models available for details")
        except Exception as e:
            self.log_message(f"❌ Error handling COL table double-click: {str(e)}")

    def _setup_col_integration_safely(self):
        """Setup COL integration safely"""
        try:
            if COL_SETUP_FUNCTION:
                result = COL_SETUP_FUNCTION(self)
                if result:
                    self.log_message("✅ COL functionality integrated")
                else:
                    self.log_message("⚠️ COL integration returned False")
            else:
                self.log_message("⚠️ COL integration function not available")
        except Exception as e:
            self.log_message(f"❌ COL integration error: {str(e)}")

    def _on_load_progress(self, progress: int, status: str):
        """Handle loading progress updates"""
        self.gui_layout.show_progress(progress, status)
    

    def _on_img_loaded(self, img_file):
        """Handle IMG file loaded - FIXED for tabs"""
        try:
            self.current_img = img_file
            current_index = self.main_tab_widget.currentIndex()

            # Update file info in open_files
            if current_index in self.open_files:
                self.open_files[current_index]['file_object'] = img_file
                self.log_message(f"✅ Updated tab {current_index} with loaded IMG")
            else:
                self.log_message(f"⚠️ Tab {current_index} not found in open_files")

            # Update UI for loaded IMG
            self._update_ui_for_loaded_img()

            # Update window title to show current file
            file_name = os.path.basename(img_file.file_path)
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

            self.log_message(f"✅ Loaded: {file_name} ({len(img_file.entries)} entries)")

        except Exception as e:
            self.log_message(f"❌ Error in _on_img_loaded: {str(e)}")
            if hasattr(self, 'gui_layout'):
                self.gui_layout.show_progress(-1, "Error loading IMG")


    def _populate_real_img_table(self, img_file: IMGFile):
        """Populate table with real IMG file entries - FIXED for SA format display"""
        if not img_file or not img_file.entries:
            self.gui_layout.table.setRowCount(0)
            return

        table = self.gui_layout.table
        entries = img_file.entries

        # Clear existing data (including sample entries)
        table.setRowCount(0)
        table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            try:
                # Name - should now be clean from fixed parsing
                clean_name = str(entry.name).strip()
                table.setItem(row, 0, QTableWidgetItem(clean_name))

                # Extension - Use the cleaned extension from populate_entry_details
                if hasattr(entry, 'extension') and entry.extension:
                    extension = entry.extension
                else:
                    # Fallback extraction
                    if '.' in clean_name:
                        extension = clean_name.split('.')[-1].upper()
                        extension = ''.join(c for c in extension if c.isalpha())
                    else:
                        extension = "NO_EXT"
                table.setItem(row, 1, QTableWidgetItem(extension))

                # Size - Format properly
                try:
                    if hasattr(entry, 'size') and entry.size:
                        size_bytes = int(entry.size)
                        if size_bytes < 1024:
                            size_text = f"{size_bytes} B"
                        elif size_bytes < 1024 * 1024:
                            size_text = f"{size_bytes / 1024:.1f} KB"
                        else:
                            size_text = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_text = "0 B"
                except:
                    size_text = "Unknown"
                table.setItem(row, 2, QTableWidgetItem(size_text))

                # Hash/Offset - Show as hex
                try:
                    if hasattr(entry, 'offset') and entry.offset is not None:
                        offset_text = f"0x{int(entry.offset):X}"
                    else:
                        offset_text = "0x0"
                except:
                    offset_text = "0x0"
                table.setItem(row, 3, QTableWidgetItem(offset_text))

                # Version - Use proper RW version parsing
                try:
                    if extension in ['DFF', 'TXD']:
                        if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                            version_text = entry.get_version_text()
                        elif hasattr(entry, 'rw_version') and entry.rw_version > 0:
                            # FIXED: Use proper RW version mapping
                            rw_versions = {
                                0x0800FFFF: "3.0.0.0",
                                0x1003FFFF: "3.1.0.1",
                                0x1005FFFF: "3.2.0.0",
                                0x1400FFFF: "3.4.0.3",
                                0x1803FFFF: "3.6.0.3",
                                0x1C020037: "3.7.0.2",
                                # Additional common SA versions
                                0x34003: "3.4.0.3",
                                0x35002: "3.5.0.2",
                                0x36003: "3.6.0.3",
                                0x37002: "3.7.0.2",
                                0x1801: "3.6.0.3",  # Common SA version
                                0x1400: "3.4.0.3",  # Common SA version
                            }

                            if entry.rw_version in rw_versions:
                                version_text = f"RW {rw_versions[entry.rw_version]}"
                            else:
                                # Show hex for unknown versions
                                version_text = f"RW 0x{entry.rw_version:X}"
                        else:
                            version_text = "Unknown"
                    elif extension == 'COL':
                        version_text = "COL"
                    elif extension == 'IFP':
                        version_text = "IFP"
                    else:
                        version_text = "Unknown"
                except:
                    version_text = "Unknown"
                table.setItem(row, 4, QTableWidgetItem(version_text))

                # Compression
                try:
                    if hasattr(entry, 'compression_type') and entry.compression_type:
                        if str(entry.compression_type).upper() != 'NONE':
                            compression_text = str(entry.compression_type)
                        else:
                            compression_text = "None"
                    else:
                        compression_text = "None"
                except:
                    compression_text = "None"
                table.setItem(row, 5, QTableWidgetItem(compression_text))

                # Status
                try:
                    if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                        status_text = "New"
                    elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                        status_text = "Modified"
                    else:
                        status_text = "Ready"
                except:
                    status_text = "Ready"
                table.setItem(row, 6, QTableWidgetItem(status_text))

                # Make all items read-only
                for col in range(7):
                    item = table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            except Exception as e:
                self.log_message(f"❌ Error populating row {row}: {str(e)}")
                # Create minimal fallback row
                table.setItem(row, 0, QTableWidgetItem(f"Entry_{row}"))
                table.setItem(row, 1, QTableWidgetItem("UNKNOWN"))
                table.setItem(row, 2, QTableWidgetItem("0 B"))
                table.setItem(row, 3, QTableWidgetItem("0x0"))
                table.setItem(row, 4, QTableWidgetItem("Unknown"))
                table.setItem(row, 5, QTableWidgetItem("None"))
                table.setItem(row, 6, QTableWidgetItem("Error"))

        self.log_message(f"📋 Table populated with {len(entries)} entries (SA format parser fixed)")

    def _on_load_error(self, error_message):
        """Handle loading error from background thread"""
        try:
            self.log_message(f"❌ Loading error: {error_message}")

            # Hide progress
            if hasattr(self, 'gui_layout'):
                self.gui_layout.show_progress(-1, "Error loading file")

            # Reset UI to no-file state
            self._update_ui_for_no_img()

            # Show error dialog
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Loading Error",
                f"Failed to load IMG file:\n\n{error_message}"
            )

        except Exception as e:
            self.log_message(f"❌ Error in _on_load_error: {str(e)}")


    def close_all_img(self):
        """Close all IMG files - Wrapper for close_all_tabs"""
        try:
            if hasattr(self, 'close_manager') and self.close_manager:
                self.close_manager.close_all_tabs()
            else:
                self.log_message("❌ Close manager not available")
        except Exception as e:
            self.log_message(f"❌ Error in close_all_img: {str(e)}")


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

    def convert_img_format(self):
        """Convert IMG format - Placeholder"""
        self.log_message("🔄 Convert IMG format requested")
        # TODO: Implement format conversion

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

    # COL FILE OPERATIONS - KEEP 100% OF FUNCTIONALITY

    def _load_col_file_in_new_tab(self, file_path):
        """Load COL file in new tab with proper styling - UPDATED"""
        try:
            current_index = self.main_tab_widget.currentIndex()

            # Check if current tab is empty (no file loaded)
            if current_index not in self.open_files:
                # Current tab is empty, use it
                self.log_message(f"Using current empty tab for: {os.path.basename(file_path)}")
            else:
                # Current tab has a file, create new tab using close manager
                self.log_message(f"Creating new tab for: {os.path.basename(file_path)}")
                self.close_manager.create_new_tab()
                current_index = self.main_tab_widget.currentIndex()

            # Store file info BEFORE loading (same as IMG)
            file_name = os.path.basename(file_path)
            # Remove .col extension for cleaner tab name
            if file_name.lower().endswith('.col'):
                file_name_clean = file_name[:-4]
            else:
                file_name_clean = file_name

            # Use collision/shield icon for COL files
            tab_name = f"🛡️ {file_name_clean}"

            self.open_files[current_index] = {
                'type': 'COL',
                'file_path': file_path,
                'file_object': None,  # Will be set when loaded
                'tab_name': tab_name
            }

            # Update tab name with icon
            self.main_tab_widget.setTabText(current_index, tab_name)

            # Apply light blue styling to this COL tab
            self._apply_col_tab_styling(current_index)

            # Start loading COL file
            self.load_col_file(file_path)

        except Exception as e:
            error_msg = f"Error setting up COL tab: {str(e)}"
            self.log_message(f"❌ {error_msg}")

def _apply_col_tab_styling(self, tab_index):
    """Apply light blue styling to COL tab"""
    try:
        # Get the tab bar
        tab_bar = self.main_tab_widget.tabBar()

        # Apply light blue background to this specific tab
        tab_bar.setTabTextColor(tab_index, self._get_col_text_color())

        # Apply CSS styling for light blue theme
        self._update_tab_stylesheet_for_col()

        self.log_message(f"✅ Applied light blue styling to COL tab {tab_index}")

    except Exception as e:
        self.log_message(f"❌ Error applying COL tab styling: {str(e)}")

    def _get_col_text_color(self):
        """Get text color for COL tabs"""
        from PyQt6.QtGui import QColor
        return QColor(25, 118, 210)  # Nice blue color

    def _get_col_background_color(self):
        """Get background color for COL tabs"""
        from PyQt6.QtGui import QColor
        return QColor(227, 242, 253)  # Light blue background

    def _update_tab_stylesheet_for_col(self):
        """Update tab stylesheet to support COL tab styling"""
        try:
            # Enhanced stylesheet that differentiates COL tabs
            enhanced_style = """
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: #ffffff;
                    margin-top: 0px;
                }

                QTabBar {
                    qproperty-drawBase: 0;
                }

                /* Default tab styling (IMG files) */
                QTabBar::tab {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    padding: 6px 12px;
                    margin-right: 2px;
                    border-radius: 3px 3px 0px 0px;
                    min-width: 80px;
                    max-height: 28px;
                    font-size: 9pt;
                    color: #333333;
                }

                /* Selected tab */
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 1px solid #ffffff;
                    color: #000000;
                    font-weight: bold;
                }

                /* Hover effect */
                QTabBar::tab:hover {
                    background-color: #e8e8e8;
                }

                /* COL tab styling - light blue theme */
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
            """

            # Apply the enhanced stylesheet
            self.main_tab_widget.setStyleSheet(enhanced_style)

        except Exception as e:
            self.log_message(f"❌ Error updating tab stylesheet: {str(e)}")

    def _apply_individual_col_tab_style(self, tab_index):
        """Apply individual styling to a specific COL tab"""
        try:
            # This is a workaround since PyQt6 doesn't easily allow per-tab styling
            # We'll modify the tab text to include color coding
            tab_bar = self.main_tab_widget.tabBar()
            current_text = tab_bar.tabText(tab_index)

            # Ensure COL tabs have the shield icon and are visually distinct
            if not current_text.startswith("🛡️"):
                if current_text.startswith("🔧"):
                    # Replace the wrench with shield
                    new_text = current_text.replace("🔧", "🛡️")
                else:
                    new_text = f"🛡️ {current_text}"

                tab_bar.setTabText(tab_index, new_text)

            # Set tooltip to indicate it's a COL file
            tab_bar.setTabToolTip(tab_index, "Collision File (COL) - Contains 3D collision data")

        except Exception as e:
            self.log_message(f"❌ Error applying individual COL tab style: {str(e)}")

    def _on_col_loaded(self, col_file):
        """Handle COL file loaded - UPDATED with styling"""
        try:
            self.current_col = col_file
            current_index = self.main_tab_widget.currentIndex()

            # Update file info in open_files (same as IMG)
            if current_index in self.open_files:
                self.open_files[current_index]['file_object'] = col_file
                self.log_message(f"✅ Updated tab {current_index} with loaded COL")
            else:
                self.log_message(f"⚠️ Tab {current_index} not found in open_files")

            # Apply enhanced COL tab styling after loading
            self._apply_individual_col_tab_style(current_index)

            # Update UI for loaded COL
            self._update_ui_for_loaded_col_safe()

            # Update window title to show current file
            file_name = os.path.basename(col_file.file_path)
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            self.log_message(f"✅ Loaded: {file_name} ({model_count} models)")

            # Hide progress and show COL-specific status
            if hasattr(self, 'gui_layout'):
                self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

        except Exception as e:
            self.log_message(f"❌ Error in _on_col_loaded: {str(e)}")
            self._on_col_load_error(str(e))

    def setup_col_tab_styling(self):
        """Setup enhanced tab styling system for COL differentiation"""
        try:
            # Apply base tab styling that supports COL themes
            self._update_tab_stylesheet_for_col()

            # Connect tab change to update styling
            if hasattr(self.main_tab_widget, 'currentChanged'):
                # Store original connection
                original_tab_changed = getattr(self, '_on_tab_changed', None)

                def enhanced_tab_changed(index):
                    # Call original handler
                    if original_tab_changed:
                        original_tab_changed(index)

                    # Apply COL-specific styling if needed
                    if index in self.open_files:
                        file_info = self.open_files[index]
                        if file_info.get('type') == 'COL':
                            self._apply_individual_col_tab_style(index)

                # Replace the handler
                self._on_tab_changed = enhanced_tab_changed

            self.log_message("✅ COL tab styling system setup complete")

        except Exception as e:
            self.log_message(f"❌ Error setting up COL tab styling: {str(e)}")

    def get_col_tab_info(self):
        """Get information about all COL tabs"""
        col_tabs = []

        for tab_index, file_info in self.open_files.items():
            if file_info.get('type') == 'COL':
                tab_text = self.main_tab_widget.tabText(tab_index)
                file_path = file_info.get('file_path', 'Unknown')

                col_tabs.append({
                    'index': tab_index,
                    'name': tab_text,
                    'path': file_path,
                    'is_active': tab_index == self.main_tab_widget.currentIndex()
                })

        return col_tabs

    # Enhanced COL tab icons - different options
    def get_col_tab_icons(self):
        """Get different icon options for COL tabs"""
        return {
            'shield': '🛡️',      # Current - protection/collision
            'collision': '💥',    # Impact/collision
            'cube': '🧊',         # 3D collision box
            'diamond': '💎',      # Collision geometry
            'gear': '⚙️',         # Technical/mechanical
            'warning': '⚠️',      # Collision warning
            'target': '🎯',       # Collision detection
            'atom': '⚛️',         # Physics/collision
        }

    def change_col_tab_icon(self, icon_key='shield'):
        """Change the icon for all COL tabs"""
        try:
            icons = self.get_col_tab_icons()
            new_icon = icons.get(icon_key, '🛡️')

            changed_count = 0
            for tab_index, file_info in self.open_files.items():
                if file_info.get('type') == 'COL':
                    current_text = self.main_tab_widget.tabText(tab_index)

                    # Replace any existing icon with new one
                    for old_icon in icons.values():
                        if current_text.startswith(old_icon):
                            current_text = current_text[2:]  # Remove icon and space
                            break

                    new_text = f"{new_icon} {current_text}"
                    self.main_tab_widget.setTabText(tab_index, new_text)
                    changed_count += 1

            if changed_count > 0:
                self.log_message(f"✅ Changed icon for {changed_count} COL tabs to {new_icon}")

        except Exception as e:
            self.log_message(f"❌ Error changing COL tab icons: {str(e)}")

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

    def debug_theme_system(self):
        """Debug method to check theme system status"""
        if hasattr(self, 'app_settings'):
            settings = self.app_settings
            self.log_message(f"🎨 Theme System Debug:")
            self.log_message(f"   Settings file: {settings.settings_file}")
            self.log_message(f"   Themes directory: {settings.themes_dir}")
            self.log_message(f"   Themes dir exists: {settings.themes_dir.exists()}")
            self.log_message(f"   Available themes: {list(settings.themes.keys())}")
            self.log_message(f"   Current theme: {settings.current_settings.get('theme')}")

            # Check if themes directory has files
            if settings.themes_dir.exists():
                theme_files = list(settings.themes_dir.glob("*.json"))
                self.log_message(f"   Theme files found: {[f.name for f in theme_files]}")
            else:
                self.log_message(f"   ⚠️  Themes directory does not exist!")

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
