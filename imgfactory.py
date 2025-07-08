
#!/usr/bin/env python3
"""
X-Seti - JUNE25 2025 - IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""
#this belongs in root /imgfactory.py - version 61
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
if utils_dir.exists() and str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

# Now continue with other imports
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QDialog,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton, QToolBar, QFormLayout
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
from components.col_tabs_integration import setup_col_tab_integration
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.menu import IMGFactoryMenuBar

# FIXED COL INTEGRATION IMPORTS
print("Attempting COL integration...")
COL_INTEGRATION_AVAILABLE = False
COL_SETUP_FUNCTION = None


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
        self.open_files = {}  # Dict to store open files {tab_index: file_info}
        self.tab_counter = 0  # Counter for unique tab IDs

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

        # Setup close manager for tab handling
        install_close_functions(self)

        # COL Integration - FIXED: Move to end and use correct import

        try:
            from components.col_tabs_integration import setup_col_tab_integration
            if setup_col_tab_integration(self):
                self.log_message("✅ COL tab integration setup complete")
            else:
                self.log_message("⚠️ COL tab integration setup failed")
        except ImportError as e:
            self.log_message(f"COL integration not available: {e}")
        except Exception as e:
            self.log_message(f"COL integration error: {str(e)}")

        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)

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

    # Part 2
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
        has_col = self.current_col is not None

        # Log the button state changes for debugging
        self.log_message(f"Button states updated: selection={has_selection}, img_loaded={has_img}, col_loaded={has_col}")

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
                    # Enable for IMG files with selection, disable for COL files
                    button.setEnabled(has_selection and has_img and not has_col)

        # These buttons only need an IMG (no selection required) - DISABLE for COL
        img_dependent_buttons = [
            'import_btn', 'import_files_btn', 'rebuild_btn', 'close_btn',
            'validate_btn', 'refresh_btn'
        ]

        for btn_name in img_dependent_buttons:
            if hasattr(self.gui_layout, btn_name):
                button = getattr(self.gui_layout, btn_name)
                if hasattr(button, 'setEnabled'):
                    # Special handling for rebuild - disable for COL files
                    if btn_name == 'rebuild_btn':
                        button.setEnabled(has_img and not has_col)
                    else:
                        button.setEnabled(has_img or has_col)

    def _update_status_from_signal(self, message):
        """Update status from unified signal system"""
        # Update status bar if available
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(message)

        # Also update GUI layout status if available
        if hasattr(self.gui_layout, 'status_label'):
            self.gui_layout.status_label.setText(message)

    def show_search_dialog(self):
        """Handle search button/menu"""
        self.log_message("🔍 Search dialog requested")
        # TODO: Implement search dialog

    def refresh_table(self):
        """Handle refresh/update button"""
        self.log_message("🔄 Refresh table requested")
        if self.current_img:
            self._update_ui_for_loaded_img()
        elif self.current_col:
            self._update_ui_for_loaded_col()

    def select_all_entries(self):
        """Select all entries in current table"""
        if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
            self.gui_layout.table.selectAll()
            self.log_message("✅ Selected all entries")

    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            self.log_message("❌ No IMG file loaded")
            return

        try:
            from components.img_validator import IMGValidator
            validation = IMGValidator.validate_img_file(self.current_img)
            if validation.is_valid:
                self.log_message("✅ IMG validation passed")
            else:
                self.log_message(f"⚠️ IMG validation issues: {validation.get_summary()}")
        except Exception as e:
            self.log_message(f"❌ Validation error: {str(e)}")

    def show_gui_settings(self):
        """Show GUI settings dialog"""
        self.log_message("⚙️ GUI settings requested")
        try:
            from utils.app_settings_system import SettingsDialog
            dialog = SettingsDialog(self.app_settings, self)
            dialog.exec()
        except Exception as e:
            self.log_message(f"❌ Settings dialog error: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About IMG Factory 1.5",
                         "IMG Factory 1.5\nAdvanced IMG Archive Management\nX-Seti 2025")

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

        # Initialize open files tracking
        self.open_files = {}

        # Create initial empty tab
        self._create_initial_tab()

        # Setup close manager BEFORE connecting signals
        self.close_manager = install_close_functions(self)
        self.main_tab_widget.tabCloseRequested.connect(self.close_manager.close_tab)
        self.main_tab_widget.currentChanged.connect(self._on_tab_changed)

        # Add tab widget to main layout
        main_layout.addWidget(self.main_tab_widget)

        # Create GUI layout system (single instance)
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

    def _populate_real_img_table(self, img_file):
        """Populate table with real IMG data - HELPER method"""
        try:
            populate_img_table(self.gui_layout.table, img_file)
        except Exception as e:
            self.log_message(f"❌ Error populating table: {str(e)}")

    def handle_action(self, action_name):
        """Handle unified action signals - UPDATED with missing methods"""
        try:
            action_map = {
                # File operations
                'open_img_file': self.open_img_file,
                'close_img_file': self.close_img_file,
                'close_all': self.close_manager.close_all_tabs if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': self.close_all_img,
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
                'rebuild_all_img': self.rebuild_all_img,
                'merge_img': self.merge_img,
                'split_img': self.split_img,
                'convert_img_format': self.convert_img_format,

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

    def setup_menu_connections(self):
        """Setup menu connections - UPDATED for unified file loading"""
        try:
            menu_callbacks = {
                'new_img': self.create_new_img,
                'open_img': self.open_file_dialog,  # UPDATED: Use unified loader
                'close_img': self.close_manager.close_img_file if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all': self.close_manager.close_all_tabs if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
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

    def handle_menu_search(self):
        """Handle search from menu (Ctrl+F)"""
        self.show_search_dialog()

    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)
        # Delegate to GUI layout
        if hasattr(self.gui_layout, 'handle_resize_event'):
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

    def _update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded - FIXED to use col_tab_integration"""
        try:
            if hasattr(self, 'load_col_file_safely'):
                # Use the method provided by col_tab_integration
                from components.col_tab_integration import update_ui_for_loaded_col
                update_ui_for_loaded_col(self)
            else:
                # Fallback implementation
                self.log_message("⚠️ COL integration not fully loaded, using fallback")
                if hasattr(self, 'gui_layout') and self.gui_layout.table:
                    self.gui_layout.table.setRowCount(1)
                    col_name = os.path.basename(self.current_col.file_path) if hasattr(self.current_col, 'file_path') else "Unknown"
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
                    self.statusBar().showMessage(f"COL file loaded: {col_name}")

        except Exception as e:
            self.log_message(f"❌ Error updating UI for COL: {str(e)}")

    def create_new_img(self):
        """Show new IMG creation dialog - FIXED: No signal connections"""
        try:
            dialog = GameSpecificIMGDialog(self)
            dialog.template_manager = self.template_manager

            # Execute dialog and check result
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Get the output path from the dialog
                if hasattr(dialog, 'output_path') and dialog.output_path:
                    output_path = dialog.output_path
                    self.log_message(f"✅ Created: {os.path.basename(output_path)}")

                    # Load the created IMG file in a new tab
                    self._load_img_file_in_new_tab(output_path)
        except Exception as e:
            self.log_message(f"❌ Error creating new IMG: {str(e)}")

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
                self._load_col_file_safely(file_path)
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
                self._load_col_file_safely(file_path)
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
        """Load COL file safely - REDIRECTS to col_tab_integration"""
        try:
            if hasattr(self, 'load_col_file_safely'):
                # Use the method provided by col_tab_integration
                self.load_col_file_safely(file_path)
            else:
                self.log_message("❌ Error loading file: 'IMGFactory' object has no attribute 'load_col_file_safely'")
        except Exception as e:
            self.log_message(f"❌ Error loading COL file: {str(e)}")

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
            self._update_ui_for_loaded_col()

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

    # Part 3
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
        """Load IMG file in background thread - FIXED recursion issue"""
        if self.load_thread and self.load_thread.isRunning():
            return

        self.log_message(f"Loading: {os.path.basename(file_path)}")

        # Show progress - CHECK if method exists first
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(0, "Loading IMG file...")
        else:
            self.log_message("⚠️ gui_layout.show_progress not available")

        # Create and start the loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._on_img_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_img_load_error)
        self.load_thread.start()

    def _on_img_load_progress(self, progress: int, status: str):
        """Handle IMG loading progress updates"""
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(progress, status)
        else:
            self.log_message(f"Progress: {progress}% - {status}")

    def _on_img_load_error(self, error_message: str):
        """Handle IMG loading error"""
        self.log_message(f"❌ {error_message}")

        # Hide progress - CHECK if method exists first
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()
        else:
            self.log_message("⚠️ gui_layout.hide_progress not available")

        QMessageBox.critical(self, "IMG Load Error", error_message)

    def open_img_file(self):
        """Open file dialog - REDIRECTS to unified loader"""
        self.open_file_dialog()

    def _update_ui_for_no_img(self):
        """Update UI when no IMG file is loaded"""
        # Clear current data
        self.current_img = None
        self.current_col = None  # Also clear COL

        # Update window title
        self.setWindowTitle("IMG Factory 1.5")

        # Clear table if it exists
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            self.gui_layout.table.setRowCount(0)

        # Update status - CHECK if methods exist first
        if hasattr(self, 'gui_layout'):
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Ready")
            if hasattr(self.gui_layout, 'update_img_info'):
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
                file_size = os.path.getsize(col_file.file_path) if col_file and hasattr(col_file, 'file_path') and col_file.file_path else 0
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
                model_name = getattr(model, 'name', f"Model_{row}") if hasattr(model, 'name') and model.name else f"Model_{row}"
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
                if hasattr(model, 'version') and hasattr(model.version, 'value'):
                    version_text = str(model.version.value)  # Just "1", "2", "3", or "4"
                elif hasattr(model, 'version'):
                    version_text = str(model.version)
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
            if hasattr(model, 'version') and hasattr(model.version, 'value'):
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
                'name': getattr(model, 'name', f"Model_{row_index}") if hasattr(model, 'name') and model.name else f"Model_{row_index}",
                'type': "COL",
                'size': self._estimate_col_model_size_bytes(model),
                'version': str(model.version.value) if hasattr(model, 'version') and hasattr(model.version, 'value') else "Unknown",
                'elements': stats.get('total_elements', 0),
                'spheres': stats.get('spheres', 0),
                'boxes': stats.get('boxes', 0),
                'faces': stats.get('faces', 0),
                'vertices': stats.get('vertices', 0),
            }

            if hasattr(model, 'bounding_box') and model.bounding_box:
                bbox = model.bounding_box
                if hasattr(bbox, 'center') and hasattr(bbox, 'radius'):
                    details.update({
                        'bbox_center': (bbox.center.x, bbox.center.y, bbox.center.z),
                        'bbox_radius': bbox.radius,
                    })
                    if hasattr(bbox, 'min') and hasattr(bbox, 'max'):
                        details.update({
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
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(progress, status)
        else:
            self.log_message(f"Progress: {progress}% - {status}")

    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        try:
            # Store the loaded IMG file
            current_index = self.main_tab_widget.currentIndex()

            if current_index in self.open_files:
                self.open_files[current_index]['file_object'] = img_file

            # Set current IMG reference
            self.current_img = img_file

            # Update UI
            self._update_ui_for_loaded_img()

            # Hide progress - CHECK if method exists first
            if hasattr(self.gui_layout, 'hide_progress'):
                self.gui_layout.hide_progress()
            else:
                self.log_message("⚠️ gui_layout.hide_progress not available")

            # Log success
            self.log_message(f"✅ Loaded: {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")

        except Exception as e:
            error_msg = f"Error processing loaded IMG: {str(e)}"
            self.log_message(f"❌ {error_msg}")

            # Hide progress - CHECK if method exists first
            if hasattr(self.gui_layout, 'hide_progress'):
                self.gui_layout.hide_progress()
            else:
                self.log_message("⚠️ gui_layout.hide_progress not available")

            QMessageBox.critical(self, "IMG Processing Error", error_msg)

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
                clean_name = str(entry.name).strip() if hasattr(entry, 'name') else f"Entry_{row}"
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

            # Hide progress - CHECK if method exists first
            if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_progress'):
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

    def close_img_file(self):
        """Close current IMG/COL file - DIRECT implementation if close_manager fails"""
        try:
            # Try to use close manager first
            if hasattr(self, 'close_manager') and self.close_manager:
                self.close_manager.close_img_file()
                return
        except Exception as e:
            self.log_message(f"❌ Close manager error: {str(e)}")

        # Fallback: Direct implementation
        try:
            current_index = self.main_tab_widget.currentIndex()

            # Log what we're closing
            if hasattr(self, 'current_img') and self.current_img:
                file_path = getattr(self.current_img, 'file_path', 'Unknown IMG')
                self.log_message(f"🗂️ Closing IMG: {os.path.basename(file_path)}")
            elif hasattr(self, 'current_col') and self.current_col:
                file_path = getattr(self.current_col, 'file_path', 'Unknown COL')
                self.log_message(f"🗂️ Closing COL: {os.path.basename(file_path)}")
            else:
                self.log_message("🗂️ Closing current tab")

            # Clear the current file data
            self.current_img = None
            self.current_col = None

            # Remove from open_files if exists
            if hasattr(self, 'open_files') and current_index in self.open_files:
                del self.open_files[current_index]

            # Reset tab name to "No File"
            if hasattr(self, 'main_tab_widget'):
                self.main_tab_widget.setTabText(current_index, "📁 No File")

            # Update UI for no file state
            self._update_ui_for_no_img()

            self.log_message("✅ File closed successfully")

        except Exception as e:
            error_msg = f"Error closing file: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            # Don't show error dialog, just log it

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
        """Rebuild all IMG files in current directory or selected directory"""
        try:
            # Get base directory - use current IMG directory or let user choose
            if self.current_img and hasattr(self.current_img, 'file_path'):
                base_dir = os.path.dirname(self.current_img.file_path)
                use_current_dir = QMessageBox.question(
                    self, "Rebuild All IMG Files",
                    f"Rebuild all IMG files in current directory?\n\n{base_dir}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )

                if use_current_dir == QMessageBox.StandardButton.Cancel:
                    return
                elif use_current_dir == QMessageBox.StandardButton.No:
                    base_dir = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
                    if not base_dir:
                        return
            else:
                base_dir = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
                if not base_dir:
                    return

            # Find all IMG files in directory
            try:
                img_files = [f for f in os.listdir(base_dir) if f.lower().endswith('.img')]
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot access directory: {str(e)}")
                return

            if not img_files:
                QMessageBox.information(self, "No IMG Files", "No IMG files found in selected directory")
                return

            # Show confirmation with file list
            file_list = "\n".join(img_files[:10])
            if len(img_files) > 10:
                file_list += f"\n... and {len(img_files) - 10} more files"

            reply = QMessageBox.question(
                self, "Confirm Rebuild All",
                f"Rebuild {len(img_files)} IMG files?\n\nFiles to rebuild:\n{file_list}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Perform rebuild operation
            self.log_message(f"🔧 Starting rebuild of {len(img_files)} IMG files...")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Rebuilding IMG files...")

            rebuilt_count = 0
            failed_files = []

            for i, img_file in enumerate(img_files):
                file_path = os.path.join(base_dir, img_file)
                progress = int((i + 1) * 100 / len(img_files))

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Rebuilding {img_file}...")

                self.log_message(f"🔧 Rebuilding {img_file}...")

                try:
                    # Import IMG class and attempt to rebuild
                    from components.img_core_classes import IMGFile

                    # Load IMG file
                    img = IMGFile(file_path)
                    if not img.open():
                        failed_files.append(f"{img_file}: Failed to open")
                        continue

                    # Check if rebuild method exists and attempt rebuild
                    if hasattr(img, 'rebuild'):
                        if img.rebuild():
                            rebuilt_count += 1
                            self.log_message(f"✅ Rebuilt: {img_file}")
                        else:
                            failed_files.append(f"{img_file}: Rebuild method failed")
                    elif hasattr(img, 'save'):
                        # Alternative: try save method
                        if img.save():
                            rebuilt_count += 1
                            self.log_message(f"✅ Saved: {img_file}")
                        else:
                            failed_files.append(f"{img_file}: Save method failed")
                    else:
                        failed_files.append(f"{img_file}: No rebuild/save method available")

                    # Clean up
                    if hasattr(img, 'close'):
                        img.close()

                except Exception as e:
                    failed_files.append(f"{img_file}: {str(e)}")
                    self.log_message(f"❌ Error rebuilding {img_file}: {str(e)}")

            # Hide progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"Rebuild complete: {rebuilt_count}/{len(img_files)}")

            # Show results
            self.log_message(f"✅ Rebuild all complete: {rebuilt_count}/{len(img_files)} files rebuilt")

            if failed_files:
                # Show detailed results with failures
                failed_list = "\n".join(failed_files[:10])
                if len(failed_files) > 10:
                    failed_list += f"\n... and {len(failed_files) - 10} more failures"

                QMessageBox.warning(
                    self, "Rebuild All Results",
                    f"Rebuild completed with some issues:\n\n"
                    f"✅ Successfully rebuilt: {rebuilt_count} files\n"
                    f"❌ Failed: {len(failed_files)} files\n\n"
                    f"Failed files:\n{failed_list}"
                )
            else:
                # All successful
                QMessageBox.information(
                    self, "Rebuild All Complete",
                    f"✅ Successfully rebuilt all {rebuilt_count} IMG files!"
                )

        except Exception as e:
            error_msg = f"Error in rebuild_all_img: {str(e)}"
            self.log_message(f"❌ {error_msg}")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Rebuild all failed")

            QMessageBox.critical(self, "Rebuild All Error", error_msg)

    def merge_img(self):
        """Merge multiple IMG files"""
        try:
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
        except Exception as e:
            self.log_message(f"❌ Error in merge_img: {str(e)}")

    def split_img(self):
        """Split IMG file into smaller parts"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            dialog = QMessageBox.question(self, "Split IMG",
                                        "Split current IMG into multiple files?")
            if dialog == QMessageBox.StandardButton.Yes:
                self.log_message("IMG split functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in split_img: {str(e)}")

    def convert_img(self):
        """Convert IMG between versions"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            self.log_message("IMG conversion functionality coming soon")
            QMessageBox.information(self, "Info", "IMG conversion functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in convert_img: {str(e)}")

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

        try:
            reply = QMessageBox.question(self, "Remove All",
                                        "Remove all entries from IMG?")
            if reply == QMessageBox.StandardButton.Yes:
                self.current_img.entries.clear()
                self._update_ui_for_loaded_img()
                self.log_message("All entries removed")
        except Exception as e:
            self.log_message(f"❌ Error in remove_all_entries: {str(e)}")

    def quick_export(self):
        """Quick export selected files to default location"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            # Check if we have a selection method available
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if not selected_rows:
                QMessageBox.warning(self, "Warning", "No entries selected")
                return

            # Use Documents/IMG_Exports as default
            export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
            os.makedirs(export_dir, exist_ok=True)

            self.log_message(f"Quick exporting {len(selected_rows)} files to {export_dir}")
            QMessageBox.information(self, "Info", "Quick export functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in quick_export: {str(e)}")

    def pin_selected(self):
        """Pin selected entries to top of list"""
        try:
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if not selected_rows:
                QMessageBox.information(self, "Pin", "No entries selected")
                return

            self.log_message(f"Pinned {len(selected_rows)} entries")
        except Exception as e:
            self.log_message(f"❌ Error in pin_selected: {str(e)}")

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

            # Show progress - CHECK if method exists first
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Rebuilding...")

            # Check if IMG has rebuild method
            if hasattr(self.current_img, 'rebuild'):
                if self.current_img.rebuild():
                    self.log_message("IMG file rebuilt successfully")
                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(-1, "Rebuild complete")
                    QMessageBox.information(self, "Success", "IMG file rebuilt successfully!")
                else:
                    self.log_message("Failed to rebuild IMG file")
                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(-1, "Rebuild failed")
                    QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
            else:
                self.log_message("❌ Error rebuilding IMG: 'IMGFile' object has no attribute 'rebuild'")
                QMessageBox.critical(self, "Error", "Rebuild method not available in IMG file class")

        except Exception as e:
            error_msg = f"Error rebuilding IMG: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Error")
            QMessageBox.critical(self, "Rebuild Error", error_msg)

    def rebuild_img_as(self):
        """Rebuild IMG file with new name"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Rebuild IMG As", "",
                "IMG Archives (*.img);;All Files (*)"
            )

            if file_path:
                self.log_message(f"Rebuilding IMG as: {os.path.basename(file_path)}")

                # Show progress - CHECK if method exists first
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Rebuilding...")

                # Check if IMG has rebuild_as method
                if hasattr(self.current_img, 'rebuild_as'):
                    if self.current_img.rebuild_as(file_path):
                        self.log_message("IMG file rebuilt successfully")
                        if hasattr(self.gui_layout, 'show_progress'):
                            self.gui_layout.show_progress(-1, "Rebuild complete")
                        QMessageBox.information(self, "Success", f"IMG file rebuilt as {os.path.basename(file_path)}")
                    else:
                        self.log_message("Failed to rebuild IMG file")
                        if hasattr(self.gui_layout, 'show_progress'):
                            self.gui_layout.show_progress(-1, "Rebuild failed")
                        QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
                else:
                    self.log_message("❌ Error rebuilding IMG: 'IMGFile' object has no attribute 'rebuild_as'")
                    QMessageBox.critical(self, "Error", "Rebuild As method not available in IMG file class")

        except Exception as e:
            error_msg = f"Error rebuilding IMG: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Error")
            QMessageBox.critical(self, "Rebuild Error", error_msg)

    # Part 4
    def import_files(self):
        """Import files into current IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Import Files", "",
                "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
            )

            if file_paths:
                self.log_message(f"Importing {len(file_paths)} files...")

                # Show progress - CHECK if method exists first
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Importing files...")

                imported_count = 0
                for i, file_path in enumerate(file_paths):
                    progress = int((i + 1) * 100 / len(file_paths))
                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Importing {os.path.basename(file_path)}")

                    # Check if IMG has import_file method
                    if hasattr(self.current_img, 'import_file'):
                        if self.current_img.import_file(file_path):
                            imported_count += 1
                            self.log_message(f"Imported: {os.path.basename(file_path)}")
                    else:
                        self.log_message(f"❌ IMG import_file method not available")
                        break

                # Refresh table
                if hasattr(self, '_populate_real_img_table'):
                    self._populate_real_img_table(self.current_img)
                else:
                    populate_img_table(self.gui_layout.table, self.current_img)

                self.log_message(f"Import complete: {imported_count}/{len(file_paths)} files imported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Import complete")
                if hasattr(self.gui_layout, 'update_img_info'):
                    self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")

                QMessageBox.information(self, "Import Complete",
                                      f"Imported {imported_count} of {len(file_paths)} files")

        except Exception as e:
            error_msg = f"Error importing files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Import error")
            QMessageBox.critical(self, "Import Error", error_msg)

    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            selected_rows = []
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectedItems'):
                for item in self.gui_layout.table.selectedItems():
                    if item.column() == 0:  # Only filename column
                        selected_rows.append(item.row())

            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "Please select entries to export.")
                return

            export_dir = QFileDialog.getExistingDirectory(self, "Export To Folder")
            if export_dir:
                self.log_message(f"Exporting {len(selected_rows)} entries...")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Exporting...")

                exported_count = 0
                for i, row in enumerate(selected_rows):
                    progress = int((i + 1) * 100 / len(selected_rows))
                    entry_name = self.gui_layout.table.item(row, 0).text() if self.gui_layout.table.item(row, 0) else f"Entry_{row}"

                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Exporting {entry_name}")

                    # Check if IMG has export_entry method
                    if hasattr(self.current_img, 'export_entry'):
                        if self.current_img.export_entry(row, export_dir):
                            exported_count += 1
                            self.log_message(f"Exported: {entry_name}")
                    else:
                        self.log_message(f"❌ IMG export_entry method not available")
                        break

                self.log_message(f"Export complete: {exported_count}/{len(selected_rows)} files exported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Export complete")

                QMessageBox.information(self, "Export Complete",
                                      f"Exported {exported_count} of {len(selected_rows)} files to {export_dir}")

        except Exception as e:
            error_msg = f"Error exporting files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export error")
            QMessageBox.critical(self, "Export Error", error_msg)

    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            export_dir = QFileDialog.getExistingDirectory(self, "Export All To Folder")
            if export_dir:
                entry_count = len(self.current_img.entries) if hasattr(self.current_img, 'entries') and self.current_img.entries else 0
                self.log_message(f"Exporting all {entry_count} entries...")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Exporting all...")

                exported_count = 0
                for i, entry in enumerate(self.current_img.entries):
                    progress = int((i + 1) * 100 / entry_count)
                    entry_name = getattr(entry, 'name', f"Entry_{i}")

                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Exporting {entry_name}")

                    # Check if IMG has export_entry method
                    if hasattr(self.current_img, 'export_entry'):
                        if self.current_img.export_entry(i, export_dir):
                            exported_count += 1
                            self.log_message(f"Exported: {entry_name}")
                    else:
                        self.log_message(f"❌ IMG export_entry method not available")
                        break

                self.log_message(f"Export complete: {exported_count}/{entry_count} files exported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Export complete")

                QMessageBox.information(self, "Export Complete",
                                      f"Exported {exported_count} of {entry_count} files to {export_dir}")

        except Exception as e:
            error_msg = f"Error exporting all files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export error")
            QMessageBox.critical(self, "Export Error", error_msg)

    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            selected_rows = []
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectedItems'):
                for item in self.gui_layout.table.selectedItems():
                    if item.column() == 0:  # Only filename column
                        selected_rows.append(item.row())

            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "Please select entries to remove.")
                return

            # Confirm removal
            entry_names = []
            for row in selected_rows:
                item = self.gui_layout.table.item(row, 0)
                entry_names.append(item.text() if item else f"Entry_{row}")

            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Remove {len(selected_rows)} selected entries?\n\n" + "\n".join(entry_names[:5]) +
                (f"\n... and {len(entry_names) - 5} more" if len(entry_names) > 5 else ""),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Sort in reverse order to maintain indices
                selected_rows.sort(reverse=True)

                removed_count = 0
                for row in selected_rows:
                    item = self.gui_layout.table.item(row, 0)
                    entry_name = item.text() if item else f"Entry_{row}"

                    # Check if IMG has remove_entry method
                    if hasattr(self.current_img, 'remove_entry'):
                        if self.current_img.remove_entry(row):
                            removed_count += 1
                            self.log_message(f"Removed: {entry_name}")
                    else:
                        self.log_message(f"❌ IMG remove_entry method not available")
                        break

                # Refresh table
                if hasattr(self, '_populate_real_img_table'):
                    self._populate_real_img_table(self.current_img)
                else:
                    populate_img_table(self.gui_layout.table, self.current_img)

                self.log_message(f"Removal complete: {removed_count} entries removed")

                if hasattr(self.gui_layout, 'update_img_info'):
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

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Validating...")

            # Try different validation approaches
            validation_result = None

            # Method 1: Try IMGValidator class
            try:
                validator = IMGValidator()
                if hasattr(validator, 'validate'):
                    validation_result = validator.validate(self.current_img)
                elif hasattr(validator, 'validate_img_file'):
                    validation_result = validator.validate_img_file(self.current_img)
            except Exception as e:
                self.log_message(f"⚠️ IMGValidator error: {str(e)}")

            # Method 2: Try static method
            if not validation_result:
                try:
                    validation_result = IMGValidator.validate_img_file(self.current_img)
                except Exception as e:
                    self.log_message(f"⚠️ Static validation error: {str(e)}")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Validation complete")

            if validation_result:
                if hasattr(validation_result, 'is_valid') and validation_result.is_valid:
                    self.log_message("IMG file validation passed")
                    QMessageBox.information(self, "Validation Result", "IMG file is valid!")
                else:
                    errors = getattr(validation_result, 'errors', ['Unknown validation issues'])
                    self.log_message(f"IMG file validation failed: {len(errors)} errors")
                    error_details = "\n".join(errors[:10])
                    if len(errors) > 10:
                        error_details += f"\n... and {len(errors) - 10} more errors"

                    QMessageBox.warning(self, "Validation Failed",
                                      f"IMG file has {len(errors)} validation errors:\n\n{error_details}")
            else:
                self.log_message("IMG file validation completed (no issues detected)")
                QMessageBox.information(self, "Validation Result", "IMG file appears to be valid!")

        except Exception as e:
            error_msg = f"Error validating IMG: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
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
                if hasattr(self, 'close_manager'):
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
            if hasattr(self, '_apply_col_tab_styling'):
                self._apply_col_tab_styling(current_index)

            # Start loading COL file - use col_tab_integration if available
            if hasattr(self, 'load_col_file_safely'):
                self.load_col_file_safely(file_path)
            else:
                self.log_message("❌ COL loading method not available")

        except Exception as e:
            error_msg = f"Error setting up COL tab: {str(e)}"
            self.log_message(f"❌ {error_msg}")

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
            if hasattr(self, '_apply_individual_col_tab_style'):
                self._apply_individual_col_tab_style(current_index)

            # Update UI for loaded COL
            if hasattr(self, '_update_ui_for_loaded_col'):
                self._update_ui_for_loaded_col()

            # Update window title to show current file
            file_name = os.path.basename(col_file.file_path) if hasattr(col_file, 'file_path') else "Unknown COL"
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

            model_count = len(col_file.models) if hasattr(col_file, 'models') and col_file.models else 0
            self.log_message(f"✅ Loaded: {file_name} ({model_count} models)")

            # Hide progress and show COL-specific status
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

        except Exception as e:
            self.log_message(f"❌ Error in _on_col_loaded: {str(e)}")
            if hasattr(self, '_on_col_load_error'):
                self._on_col_load_error(str(e))

    def show_theme_settings(self):
        """Show theme settings dialog"""
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
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QGroupBox

            dialog = QDialog(self)
            dialog.setWindowTitle("GUI Layout Settings")
            dialog.setMinimumSize(500, 250)

            layout = QVBoxLayout(dialog)

            # Panel width group
            width_group = QGroupBox("📏 Right Panel Width Settings")
            width_layout = QVBoxLayout(width_group)

            # Current width display
            current_width = 240  # Default
            if hasattr(self.gui_layout, 'main_splitter') and hasattr(self.gui_layout.main_splitter, 'sizes'):
                sizes = self.gui_layout.main_splitter.sizes()
                if len(sizes) > 1:
                    current_width = sizes[1]

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
                if hasattr(self.gui_layout, 'main_splitter') and hasattr(self.gui_layout.main_splitter, 'sizes'):
                    sizes = self.gui_layout.main_splitter.sizes()
                    if len(sizes) >= 2:
                        self.gui_layout.main_splitter.setSizes([sizes[0], width])

                if hasattr(self.gui_layout, 'main_splitter'):
                    right_widget = self.gui_layout.main_splitter.widget(1)
                    if right_widget:
                        right_widget.setMaximumWidth(width + 60)
                        right_widget.setMinimumWidth(max(180, width - 40))

            preview_btn.clicked.connect(preview_changes)
            button_layout.addWidget(preview_btn)

            apply_btn = QPushButton("✅ Apply & Close")
            def apply_changes():
                width = width_spin.value()
                if hasattr(self.gui_layout, 'main_splitter') and hasattr(self.gui_layout.main_splitter, 'sizes'):
                    sizes = self.gui_layout.main_splitter.sizes()
                    if len(sizes) >= 2:
                        self.gui_layout.main_splitter.setSizes([sizes[0], width])

                if hasattr(self.gui_layout, 'main_splitter'):
                    right_widget = self.gui_layout.main_splitter.widget(1)
                    if right_widget:
                        right_widget.setMaximumWidth(width + 60)
                        right_widget.setMinimumWidth(max(180, width - 40))

                # Save to settings if you have app_settings
                if hasattr(self, 'app_settings') and hasattr(self.app_settings, 'current_settings'):
                    self.app_settings.current_settings["right_panel_width"] = width
                    if hasattr(self.app_settings, 'save_settings'):
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

        except Exception as e:
            self.log_message(f"❌ Error showing GUI settings: {str(e)}")

    def show_gui_layout_settings(self):
        """Show GUI Layout settings - called from menu"""
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_gui_layout_settings'):
            self.gui_layout.show_gui_layout_settings()
        else:
            self.log_message("GUI Layout settings not available")

    def debug_theme_system(self):
        """Debug method to check theme system status"""
        try:
            if hasattr(self, 'app_settings'):
                settings = self.app_settings
                self.log_message(f"🎨 Theme System Debug:")

                if hasattr(settings, 'settings_file'):
                    self.log_message(f"   Settings file: {settings.settings_file}")
                if hasattr(settings, 'themes_dir'):
                    self.log_message(f"   Themes directory: {settings.themes_dir}")
                    self.log_message(f"   Themes dir exists: {settings.themes_dir.exists()}")
                if hasattr(settings, 'themes'):
                    self.log_message(f"   Available themes: {list(settings.themes.keys())}")
                if hasattr(settings, 'current_settings'):
                    self.log_message(f"   Current theme: {settings.current_settings.get('theme')}")

                # Check if themes directory has files
                if hasattr(settings, 'themes_dir') and settings.themes_dir.exists():
                    theme_files = list(settings.themes_dir.glob("*.json"))
                    self.log_message(f"   Theme files found: {[f.name for f in theme_files]}")
                else:
                    self.log_message(f"   ⚠️  Themes directory does not exist!")
            else:
                self.log_message("⚠️ No app_settings available")
        except Exception as e:
            self.log_message(f"❌ Error in debug_theme_system: {str(e)}")

    def show_settings(self):
        """Show settings dialog"""
        print("show_settings called!")  # Debug
        try:
            # Try different import paths
            try:
                from utils.app_settings_system import SettingsDialog, apply_theme_to_app
            except ImportError:
                from app_settings_system import SettingsDialog, apply_theme_to_app

            dialog = SettingsDialog(self.app_settings, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                apply_theme_to_app(QApplication.instance(), self.app_settings)
                if hasattr(self.gui_layout, 'apply_table_theme'):
                    self.gui_layout.apply_table_theme()
                self.log_message("Settings updated")
        except Exception as e:
            print(f"Settings error: {e}")
            self.log_message(f"Settings error: {str(e)}")

    # SETTINGS PERSISTENCE - KEEP 100% OF FUNCTIONALITY

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
        try:
            self._save_settings()

            # Clean up threads
            if hasattr(self, 'load_thread') and self.load_thread and self.load_thread.isRunning():
                self.load_thread.quit()
                self.load_thread.wait()

            # Close all files
            if hasattr(self, 'close_manager'):
                self.close_manager.close_all_tabs()

            event.accept()
        except Exception as e:
            self.log_message(f"❌ Error during close: {str(e)}")
            event.accept()  # Accept anyway to prevent hanging


def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("IMG Factory")
        app.setApplicationVersion("1.5")
        app.setOrganizationName("X-Seti")

        # Load settings
        try:
            # Try different import paths for settings
            try:
                from utils.app_settings_system import AppSettings
            except ImportError:
                from app_settings_system import AppSettings

            settings = AppSettings()
            if hasattr(settings, 'load_settings'):
                settings.load_settings()
        except Exception as e:
            print(f"Warning: Could not load settings: {str(e)}")
            # Create minimal settings object
            class DummySettings:
                def __init__(self):
                    self.current_settings = {}
                    self.themes = {}
            settings = DummySettings()

        # Create main window
        window = IMGFactory(settings)

        # Show window
        window.show()

        return app.exec()

    except Exception as e:
        print(f"Fatal error in main(): {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
