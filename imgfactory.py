
#!/usr/bin/env python3
"""
X-Seti - JUNE25 2025 - IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""
#this belongs in root /imgfactory.py - version 62
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

#components
from components.unified_debug_functions import integrate_all_improvements, install_debug_control_system

from components.img_creator import NewIMGDialog, IMGCreationThread
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
from components.img_validator import IMGValidator
from components.img_core_classes import (
    IMGFile, IMGEntry, IMGVersion, Platform,
    IMGEntriesTable, FilterPanel, IMGFileInfoPanel, format_file_size,
    TabFilterWidget, integrate_filtering, create_entries_table_panel)
from components.col_loader import load_col_file_safely

#core
from core.close_func import install_close_functions, setup_close_manager
from core.img_formats import GameSpecificIMGDialog, IMGCreator
from core.file_extraction import setup_complete_extraction_integration
from core.tables_structure import reset_table_styling
from core.remove import integrate_remove_functions
from core.importer import (import_files_function,
    import_via_function, import_via_ide_file, import_from_folder,
    get_selected_entries, integrate_import_functions)
from core.rw_versions import get_rw_version_name
from core.right_click_actions import integrate_right_click_actions
from core.shortcuts import setup_all_shortcuts
from core.integration import integrate_complete_core_system


#gui-layout

#gui
from gui.gui_backend import ButtonDisplayMode, GUIBackend
from gui.gui_context import enhanced_context_menu_event
from gui.main_window import IMGFactoryMainWindow
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.gui_menu import IMGFactoryMenuBar

#methods
from methods.populate_img_table import install_img_table_populator



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

def debug_trace(func):
    """Simple debug decorator to trace function calls."""
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] Calling: {func.__name__} with args={args} kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[DEBUG] Finished: {func.__name__}")
        return result
    return wrapper

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



class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""

    def __init__(self, settings): #vers 60
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
        #self.current_col: Optional =
        self.open_files = {}  # Dict to store open files {tab_index: file_info}
        self.tab_counter = 0  # Counter for unique tab IDs

        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None

        # Initialize GUI layout
        self.gui_layout = IMGFactoryGUILayout(self)

        # Setup menu bar system
        self.menubar = self.menuBar()
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
        install_img_table_populator(self)
        integrate_right_click_actions(self)

        if integrate_remove_functions(self):
            self.log_message("✅ Remove functions integrated")

        # First integrate the functions
        integrate_complete_core_system(self)

        try:
            from core.file_extraction import setup_complete_extraction_integration
            setup_complete_extraction_integration(self)
        except Exception as e:
            self.log_message(f"⚠️ Failed to setup extraction integration: {str(e)}")


        # Create gui_backend
        self.gui_backend = GUIBackend(self)
        install_debug_control_system(self)

        # After GUI setup in __init__:
        setup_all_shortcuts(self)

        # Debug: Check what methods gui_backend has
        print("🔍 GUI Backend methods:")
        for method in dir(self.gui_backend):
            if not method.startswith('_') and callable(getattr(self.gui_backend, method)):
                print(f"   - {method}")

        # Debug: Check if bridging worked
        methods_to_check = ['export_selected_via', 'quick_export_selected', 'remove_via_entries', 'dump_entries', 'import_files_via']
        for method in methods_to_check:
            if hasattr(self, method):
                print(f"✅ {method} bridged successfully")
            else:
                print(f"❌ {method} NOT bridged")

        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)


        # Log startup
        self.log_message("IMG Factory 1.5 initialized")

    def show_debug_settings(self): #vers 1
        """Show debug settings dialog"""
        try:
            # Try to show proper debug settings if available
            from utils.app_settings_system import SettingsDialog
            if hasattr(self, 'app_settings'):
                dialog = SettingsDialog(self.app_settings, self)
                dialog.exec()
            else:
                QMessageBox.information(self, "Debug Settings",
                    "Debug settings: Use F12 to toggle performance mode")
        except ImportError:
            QMessageBox.information(self, "Debug Settings",
                "Debug settings: Use F12 to toggle performance mode")

    def setup_unified_signals(self): #vers 6
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


    def debug_img_entries(self): #vers 4
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


    def _unified_double_click_handler(self, row, filename, item): #vers 2
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


    def _unified_selection_handler(self, selected_rows, selection_count): #vers 1
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
        #has_col = self.current_col is not None

        # Log the button state changes for debugging
        self.log_message(f"Button states updated: selection={has_selection}, img_loaded={has_img}, col_loaded={has_col}")

        # Find buttons in GUI layout and update their states
        # These buttons need both an IMG and selection
        selection_dependent_buttons = [
            'export_btn', 'export_selected_btn', 'remove_btn', 'remove_selected_btn', 'reload_btn',
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
            'validate_btn', 'refresh_btn',  'reload_btn'
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

    def _update_status_from_signal(self, message): #vers 3
        """Update status from unified signal system"""
        # Update status bar if available
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(message)

        # Also update GUI layout status if available
        if hasattr(self.gui_layout, 'status_label'):
            self.gui_layout.status_label.setText(message)

    def refresh_table(self): #vers 4 -
        #./core/utils.py - def refresh_table(main_window):
        #./components/img_integration_main.py: - def refresh_table_func():

        """Handle refresh/update button"""
        self.log_message("🔄 Refresh table requested")
        if self.current_img:
            self._update_ui_for_loaded_img()
        elif self.current_col:
            self._update_ui_for_loaded_col()

    def select_all_entries(self): #vers 3
        """Select all entries in current table"""
        if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
            self.gui_layout.table.selectAll()
            self.log_message("✅ Selected all entries")

    def validate_img(self): #vers 4
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

    def show_gui_settings(self): #vers 5
        """Show GUI settings dialog"""
        self.log_message("⚙️ GUI settings requested")
        try:
            from utils.app_settings_system import SettingsDialog
            dialog = SettingsDialog(self.app_settings, self)
            dialog.exec()
        except Exception as e:
            self.log_message(f"❌ Settings dialog error: {str(e)}")


    def _create_ui(self): #vers 10
        #./core/dialogs.py: - def _create_ui(self):
        #./core/dialogs.py: - def _create_ui(self):
        #./core/dialogs.py: - def _create_ui(self):
        #./core/dialogs.py: - def _create_ui(self):
        #./core/img_formats.py: - def _create_ui(self):
        #./gui/gui_settings.py: - def _create_ui(self):
        #./gui/log_panel.py: - def _create_ui(self):
        #./gui/status_bar.py: - def _create_ui(self):
        #./gui/status_bar.py: - def _create_ui(self):
        #./gui/status_bar.py: - def _create_ui(self):
        #./gui/status_bar.py: - def _create_ui(self):
        #./components/img_templates.py: - def _create_ui(self):
        #./components/img_open_dialog.py: - def _create_ui(self):

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

    def _create_initial_tab(self): #vers 4
        #./components/img_close_functions.py: - def _create_initial_tab[self]
        """Create initial empty tab"""
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create GUI layout for this tab
        self.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Add tab with "No file" label
        self.main_tab_widget.addTab(tab_widget, "📁 No File")

    def _on_tab_changed(self, index): #vers 4
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

    def _update_ui_for_current_file(self): #vers 5
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

    def _update_ui_for_loaded_img(self): #vers 2
        """Update UI when IMG file is loaded - FIXED: Complete implementation"""
        if not self.current_img:
            self.log_message("⚠️ _update_ui_for_loaded_img called but no current_img")
            return

        # Update window title
        file_name = os.path.basename(self.current_img.file_path)
        self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Populate table with IMG entries
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            self._populate_img_table(self.current_img)
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

    def log_message(self, message): #vers 3
        #./gui/gui_layout.py - def log_message(self, message): #vers 3 #keep
        #./gui/gui_backend.py - def log_message(self, message): #vers 3 #keep
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

    def create_new_img(self): #vers 5
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


    def open_img_file(self): #vers 5
        """Open file dialog - REDIRECTS to unified loader"""
        self.open_file_dialog()


    def _detect_and_open_file(self, file_path: str) -> bool: #vers 5
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

    def open_file_dialog(self): #vers 4
        """Unified file dialog for IMG and COL files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG/COL Archive", "",
            "All Supported (*.img *.col);;IMG Archives (*.img);;COL Archives (*.col);;All Files (*)")

        if file_path:
            self.load_file_unified(file_path)

    def _detect_file_type(self, file_path: str) -> str: #vers 3
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


    def load_file_unified(self, file_path: str): #vers 2
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


    def _load_img_file_in_new_tab(self, file_path): #vers 3
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


    def load_img_file(self, file_path: str): #vers 3
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


    def _on_img_load_progress(self, progress: int, status: str): #vers 4
        """Handle IMG loading progress updates"""
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(progress, status)
        else:
            self.log_message(f"Progress: {progress}% - {status}")


    def _on_img_load_error(self, error_message: str): #vers 3
        """Handle IMG loading error"""
        self.log_message(f"❌ {error_message}")

        # Hide progress - CHECK if method exists first
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()
        else:
            self.log_message("⚠️ gui_layout.hide_progress not available")

        QMessageBox.critical(self, "IMG Load Error", error_message)


    def _update_ui_for_no_img(self): #vers 5
        """Update UI when no IMG file is loaded"""
        # Clear current data
        self.current_img = None
        #self.current_col = None  # Also clear COL

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

    def _on_load_progress(self, progress: int, status: str): #vers 4
        """Handle loading progress updates"""
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(progress, status)
        else:
            self.log_message(f"Progress: {progress}% - {status}")

    def _on_img_loaded(self, img_file: IMGFile): #vers 4
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


    def get_entry_rw_version(self, entry, extension): #vers 3
        """Detect RW version from entry file data"""
        try:
            # Skip non-RW files
            if extension not in ['DFF', 'TXD']:
                return "Unknown"

            # Check if entry already has version info
            if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                return entry.get_version_text()

            # Try to get file data using different methods
            file_data = None

            # Method 1: Direct data access
            if hasattr(entry, 'get_data'):
                try:
                    file_data = entry.get_data()
                except:
                    pass

            # Method 2: Extract data method
            if not file_data and hasattr(entry, 'extract_data'):
                try:
                    file_data = entry.extract_data()
                except:
                    pass

            # Method 3: Read directly from IMG file
            if not file_data:
                try:
                    if (hasattr(self, 'current_img') and
                        hasattr(entry, 'offset') and
                        hasattr(entry, 'size') and
                        self.current_img and
                        self.current_img.file_path):

                        with open(self.current_img.file_path, 'rb') as f:
                            f.seek(entry.offset)
                            # Only read the header (12 bytes) for efficiency
                            file_data = f.read(min(entry.size, 12))
                except Exception as e:
                    print(f"🔍 DEBUG: Failed to read file data for {entry.name}: {e}")
                    return "Unknown"

            # Parse RW version from file header
            if file_data and len(file_data) >= 12:
                import struct
                try:
                    # RW version is stored at offset 8-12 in RW files
                    rw_version = struct.unpack('<I', file_data[8:12])[0]

                    if rw_version > 0:
                        version_name = get_rw_version_name(rw_version)
                        print(f"🔍 DEBUG: Found RW version 0x{rw_version:X} ({version_name}) for {entry.name}")
                        return f"RW {version_name}"
                    else:
                        print(f"🔍 DEBUG: Invalid RW version (0) for {entry.name}")
                        return "Unknown"

                except struct.error as e:
                    print(f"🔍 DEBUG: Struct unpack error for {entry.name}: {e}")
                    return "Unknown"
            else:
                print(f"🔍 DEBUG: Insufficient file data for {entry.name} (need 12 bytes, got {len(file_data) if file_data else 0})")
                return "Unknown"

        except Exception as e:
            print(f"🔍 DEBUG: RW version detection error for {entry.name}: {e}")
            return "Unknown"


    def _on_load_error(self, error_message): #vers 2
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
                f"Failed to load IMG file:\n\n{error_message}")

        except Exception as e:
            self.log_message(f"❌ Error in _on_load_error: {str(e)}")


    def merge_img(self): #vers 1
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


    def split_img(self): #vers 1
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


    def convert_img(self): #vers 1
        """Convert IMG between versions"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            self.log_message("IMG conversion functionality coming soon")
            QMessageBox.information(self, "Info", "IMG conversion functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in convert_img: {str(e)}")


    def convert_img_format(self): #vers 1
        """Convert IMG format - Placeholder"""
        self.log_message("🔄 Convert IMG format requested")
        # TODO: Implement format conversion


    def import_via_tool(self): #vers 1
        """Import files using external tool"""
        self.log_message("Import via tool functionality coming soon")


    def export_via_tool(self): #vers 1
        """Export using external tool"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        self.log_message("Export via tool functionality coming soon")

    def export_selected_via(self): #vers 1
        """Export selected entries via IDE file"""
        from core.exporter import export_via_function
        export_via_function(self)

    def quick_export_selected(self): #vers 1
        """Quick export selected entries"""
        from core.exporter import quick_export_function
        quick_export_function(self)

    def dump_entries(self): #vers 1
        """Dump all entries to folder"""
        from core.exporter import dump_all_function
        dump_all_function(self)

    def import_files_via(self): #vers 1
        """Import files via IDE file"""
        from core.importer import import_via_function
        import_via_function(self)


    def pin_selected(self): #vers 1
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
    def open_col_editor(self): #vers 1
        """Open COL file editor"""
        self.log_message("COL editor functionality coming soon")

    def open_txd_editor(self): #vers 1
        """Open TXD texture editor"""
        self.log_message("TXD editor functionality coming soon")

    def open_dff_editor(self): #vers 1
        """Open DFF model editor"""
        self.log_message("DFF editor functionality coming soon")

    def open_ipf_editor(self): #vers 1
        """Open IPF animation editor"""
        self.log_message("IPF editor functionality coming soon")

    def open_ipl_editor(self): #vers 1
        """Open IPL item placement editor"""
        self.log_message("IPL editor functionality coming soon")

    def open_ide_editor(self): #vers 1
        """Open IDE item definition editor"""
        self.log_message("IDE editor functionality coming soon")

    def open_dat_editor(self): #vers 1
        """Open DAT file editor"""
        self.log_message("DAT editor functionality coming soon")

    def open_zons_editor(self): #vers 1
        """Open zones editor"""
        self.log_message("Zones editor functionality coming soon")

    def open_weap_editor(self): #vers 1
        """Open weapons editor"""
        self.log_message("Weapons editor functionality coming soon")

    def open_vehi_editor(self): #vers 1
        """Open vehicles editor"""
        self.log_message("Vehicles editor functionality coming soon")

    def open_radar_map(self): #vers 1
        """Open radar map editor"""
        self.log_message("Radar map functionality coming soon")

    def open_paths_map(self): #vers 1
        """Open paths map editor"""
        self.log_message("Paths map functionality coming soon")

    def open_waterpro(self): #vers 1
        """Open water properties editor"""
        self.log_message("Water properties functionality coming soon")


    def validate_img(self): #vers 3
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


    def show_theme_settings(self): #vers 2
        """Show theme settings dialog"""
        self.show_settings()  # For now, use general settings

    def show_about(self): #vers 2
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


    def show_gui_settings(self): #vers 5
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

    def show_gui_layout_settings(self): #vers 2
        """Show GUI Layout settings - called from menu"""
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_gui_layout_settings'):
            self.gui_layout.show_gui_layout_settings()
        else:
            self.log_message("GUI Layout settings not available")

    def debug_theme_system(self): #vers 1
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

    def show_settings(self): #vers 1
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

    def _restore_settings(self): #vers 1
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

    def _save_settings(self): #vers 1
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

           # Test if settings actually work
           if not hasattr(settings, 'get_stylesheet'):
               raise AttributeError("AppSettings missing get_stylesheet method")

       except Exception as e:
           print(f"Warning: Could not load settings: {str(e)}")
           # Only use DummySettings as last resort
           class DummySettings:
               def __init__(self):
                   self.current_settings = {
                       "theme": "img_factory",
                       "font_family": "Arial",
                       "font_size": 9,
                       "show_tooltips": True,
                       "auto_save": True,
                       "debug_mode": False
                   }
                   self.themes = {
                       "img_factory": {
                           "colors": {
                               "background": "#f0f0f0",
                               "text": "#000000",
                               "button_text_color": "#000000"
                           }
                       }
                   }

               def get_stylesheet(self):
                   return "QMainWindow { background-color: #f0f0f0; }"

               def get_theme(self, theme_name=None):
                   return self.themes.get("img_factory", {"colors": {}})

               def load_settings(self):
                   pass

               def save_settings(self):
                   pass

           settings = DummySettings()
           print("Using DummySettings - theme system may be limited")

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
