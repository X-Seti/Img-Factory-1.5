#!/usr/bin/env python3
# X-Seti - Nov04 2025 - IMG Factory 1.5 - Main Entry Point
# this belongs in root /imgfactory.py - Version: 75

"""
IMG Factory 1.5 - Main Application Entry Point
Fixed method assignment order - log_message available immediately
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import pyqtSignal, Qt, QThread

print("Starting application...")

# Setup paths FIRST
current_dir = Path(__file__).parent
for path in [current_dir, current_dir / "components", current_dir / "gui",  current_dir / "themes", current_dir / "utils"]:
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QMainWindow

# Components - Import all split modules
from components.Img_Factory.img_factory_init import imgfactory_init
from components.Img_Factory.img_factory_thread import IMGLoadThread
from utils.app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog

# Import all method modules using 'from' to make functions accessible
from components.Img_Factory import img_factory_logging as logging_methods
from components.Img_Factory import img_factory_corruption as corruption_methods
from components.Img_Factory import img_factory_txd_workshop as txd_methods
from components.Img_Factory import img_factory_tab_system as tab_methods
from components.Img_Factory import img_factory_col_integration as col_methods
from components.Img_Factory import img_factory_file_operations as file_methods
from components.Img_Factory import img_factory_img_operations as img_methods
from components.Img_Factory import img_factory_entry_operations as entry_methods
from components.Img_Factory import img_factory_ui_dialogs as ui_methods
from components.Img_Factory import img_factory_utility as utility_methods


App_name = "Img Factory 1.5"

class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""

    def __init__(self, settings): #vers 80
        """Initialize IMG Factory with proper method assignment order"""
        super().__init__()

        # CRITICAL: Create working log_message IMMEDIATELY as fallback
        # This ensures logging works during initialization even if module imports fail
        def _safe_log(msg):
            """Safe logging that always works"""
            try:
                if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'log'):
                    self.gui_layout.log.append(msg)
                else:
                    print(f"LOG: {msg}")
            except:
                print(f"LOG: {msg}")

        self.log_message = _safe_log
        self._append_log_message = _safe_log

        # CRITICAL: Assign methods needed during initialization BEFORE calling init
        self.show_about = lambda: ui_methods.show_about(self)
        self.show_gui_settings = lambda: ui_methods.show_gui_settings(self)
        self.open_file_dialog = lambda: file_methods.open_file_dialog(self)
        self.open_img_file = lambda: file_methods.open_img_file(self)
        self.create_new_img = lambda: ui_methods.create_new_img(self)
        self.validate_img = lambda: ui_methods.validate_img(self)
        self.closeEvent = lambda event: ui_methods.closeEvent(self, event)
        self._restore_settings = lambda: ui_methods._restore_settings(self)
        self._save_settings = lambda: ui_methods._save_settings(self)
        self.setup_missing_utility_functions = lambda: utility_methods.setup_missing_utility_functions(self)
        self._create_ui = lambda: tab_methods._create_ui(self)  # Creates tab widget and calls gui_layout setup
        self.reload_current_file = lambda: file_methods.reload_table(self)

        # Now safe to call initialization which uses log_message
        imgfactory_init(self, settings)

        # Assign all other methods after initialization
        self._assign_all_methods()

    def _assign_all_methods(self): #vers 1
        """Assign all methods from imported modules to instance"""

        # Logging methods (already assigned, but complete the set)
        self.debug_img_before_loading = lambda fp: logging_methods.debug_img_before_loading(self, fp)
        self.show_debug_settings = lambda: logging_methods.show_debug_settings(self)

        # Corruption methods
        self.analyze_corruption = lambda: corruption_methods.analyze_corruption(self)
        self.analyze_img_corruption = lambda: corruption_methods.analyze_img_corruption(self)
        self.quick_fix_corruption = lambda: corruption_methods.quick_fix_corruption(self)
        self.clean_filenames_only = lambda: corruption_methods.clean_filenames_only(self)
        self.export_corruption_report = lambda: corruption_methods.export_corruption_report(self)

        # TXD methods
        self.open_txd_workshop_docked = lambda: txd_methods.open_txd_workshop_docked(self)
        self._handle_txd_overlay_tab_switch = lambda w, i: txd_methods._handle_txd_overlay_tab_switch(self, w, i)
        self.setup_unified_signals = lambda: txd_methods.setup_unified_signals(self)
        self._open_txd_workshop = lambda: txd_methods._open_txd_workshop(self)
        self._update_workshop_on_tab_change = lambda i: txd_methods._update_workshop_on_tab_change(self, i)
        self._on_workshop_closed = lambda: txd_methods._on_workshop_closed(self)

        # Tab system methods
        self._create_ui = lambda: tab_methods._create_ui(self)
        self._create_initial_tab = lambda: tab_methods._create_initial_tab(self)
        self._find_table_in_tab = lambda w: tab_methods._find_table_in_tab(self, w)
        self._log_current_tab_state = lambda: tab_methods._log_current_tab_state(self)
        self.ensure_current_tab_references_valid = lambda: tab_methods.ensure_current_tab_references_valid(self)
        self._update_info_bar_for_current_file = lambda: tab_methods._update_info_bar_for_current_file(self)
        self.setup_robust_tab_system = lambda: tab_methods.setup_robust_tab_system(self)
        self._reindex_open_files_robust = lambda: tab_methods._reindex_open_files_robust(self)

        # COL integration methods
        self.setup_col_integration = lambda: col_methods.setup_col_integration(self)
        self._update_ui_for_loaded_col = lambda: col_methods._update_ui_for_loaded_col(self)
        self.handle_col_file_open = lambda fp: col_methods.handle_col_file_open(self, fp)
        self.load_col_file_safely = lambda fp: col_methods.load_col_file_safely(self, fp)
        self._load_col_file_in_new_tab = lambda fp: col_methods._load_col_file_in_new_tab(self, fp)
        self._populate_col_table_img_format = lambda cf: col_methods._populate_col_table_img_format(self, cf)
        self._on_col_loaded = lambda cf: col_methods._on_col_loaded(self, cf)
        self.enable_col_debug = lambda: col_methods.enable_col_debug(self)
        self.disable_col_debug = lambda: col_methods.disable_col_debug(self)

        # File operations methods
        self.open_file_dialog = lambda: file_methods.open_file_dialog(self)
        self.open_img_file = lambda: file_methods.open_img_file(self)
        self.load_file_unified = lambda fp: file_methods.load_file_unified(self, fp)
        self._clean_on_img_loaded = lambda img: file_methods._clean_on_img_loaded(self, img)
        self.reload_table = lambda: file_methods.reload_table(self)

        # IMG operations methods
        self._on_img_loaded = lambda img: img_methods._on_img_loaded(self, img)
        self._on_load_error = lambda err: img_methods._on_load_error(self, err)
        self._on_load_progress = lambda p, s: img_methods._on_load_progress(self, p, s)

        # Entry operations methods
        self._unified_double_click_handler = lambda row: entry_methods._unified_double_click_handler(self, row)
        self._unified_selection_handler = lambda: entry_methods._unified_selection_handler(self)
        self._update_status_from_signal = lambda msg: entry_methods._update_status_from_signal(self, msg)

        # UI dialog methods
        self.create_new_img = lambda: ui_methods.create_new_img(self)
        self.select_all_entries = lambda: ui_methods.select_all_entries(self)
        self.validate_img = lambda: ui_methods.validate_img(self)
        self.show_gui_settings = lambda: ui_methods.show_gui_settings(self)
        self.show_about = lambda: ui_methods.show_about(self)

        # Utility methods
        self._update_ui_for_current_file = lambda: utility_methods._update_ui_for_current_file(self)
        self.update_button_states = lambda: utility_methods.update_button_states(self)
        self.get_current_file_type = lambda: utility_methods.get_current_file_type(self)
        self.has_col_file_loaded = lambda: utility_methods.has_col_file_loaded(self)
        self.has_img_file_loaded = lambda: utility_methods.has_img_file_loaded(self)

        # Settings persistence methods
        self._restore_settings = lambda: ui_methods._restore_settings(self)
        self._save_settings = lambda: ui_methods._save_settings(self)
        self.closeEvent = lambda event: ui_methods.closeEvent(self, event)




#Important - do not remove these methods below.

def setup_rebuild_system(self): #vers 2
    """Setup hybrid rebuild system with mode selection"""
    try:
        from core.hybrid_rebuild import setup_hybrid_rebuild_methods
        success = setup_hybrid_rebuild_methods(self)

        if success:
            self.log_message("Hybrid rebuild system enabled")
            # Now you have these methods available:

            # self.rebuild_all_img() - Shows batch mode dialog
            # self.quick_rebuild() - Fast mode only
            # self.fast_rebuild() - Direct fast mode
            # self.safe_rebuild() - Direct safe mode
        else:
            self.log_message("Hybrid rebuild setup failed")

        return success

    except ImportError:
        self.log_message("Hybrid rebuild not available")
        return False

def create_rebuild_menu(self): #vers 1
    """Create rebuild menu with mode options"""
    try:
        # Add to your existing menu bar
        rebuild_menu = self.menuBar().addMenu("🔧 Rebuild")

        # Regular rebuild (shows dialog)
        rebuild_action = QAction("Rebuild IMG...", self)
        rebuild_action.setShortcut("Ctrl+R")
        rebuild_action.setStatusTip("Rebuild current IMG file with mode selection")
        rebuild_action.triggered.connect(self.rebuild_img)
        rebuild_menu.addAction(rebuild_action)

        # Quick rebuild (fast mode only)
        quick_action = QAction("Quick Rebuild", self)
        quick_action.setShortcut("Ctrl+Shift+R")
        quick_action.setStatusTip("Quick rebuild using fast mode")
        quick_action.triggered.connect(self.quick_rebuild)
        rebuild_menu.addAction(quick_action)

        rebuild_menu.addSeparator()

        # Direct mode access
        fast_action = QAction("Fast Rebuild", self)
        fast_action.setStatusTip("Direct fast rebuild without dialog")
        fast_action.triggered.connect(self.fast_rebuild)
        rebuild_menu.addAct
        self.file_path = file_pathion(fast_action)

        safe_action = QAction("Safe Rebuild", self)
        safe_action.setStatusTip("Direct safe rebuild with full checking")
        safe_action.triggered.connect(self.safe_rebuild)
        rebuild_menu.addAction(safe_action)

        rebuild_menu.addSeparator()

        # Batch rebuild
        batch_action = QAction("Rebuild All...", self)
        batch_action.setStatusTip("Batch rebuild multiple IMG files")
        batch_action.triggered.connect(self.rebuild_all_img)
        rebuild_menu.addAction(batch_action)

        return True

    except Exception as e:
        self.log_message(f"Rebuild menu creation failed: {str(e)}")
        return False

def setup_debug_mode(self): #vers 2
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


def debug_trace(func): #ver 1
    """Simple debug decorator to trace function calls."""
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] Calling: {func.__name__} with args={args} kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[DEBUG] Finished: {func.__name__}")
        return result
    return wrapper


def toggle_debug_mode(self): #vers 2
    """Toggle debug mode with user feedback"""
    enabled = self.debug.toggle_debug_mode()
    status = "enabled" if enabled else "disabled"
    self.log_message(f"🐛 Debug mode {status}")

    if enabled:
        self.log_message("Debug categories: " + ", ".join(self.debug.debug_categories))
        # Run immediate debug check
        self.debug_img_entries()


def debug_img_entries(self): #vers 2
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

    def run(self): #vers 1
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


def main(): #vers 1
    """Main application entry point"""
    try:
        print("PyQt6.QtCore imported successfully")

        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName(App_name)

        # Load settings
        try:
            from utils.app_settings_system import load_settings
            settings = load_settings()
            print("Settings loaded successfully")
        except Exception as e:
            print(f"Settings load error: {e}, using defaults")
            settings = {}

        # Create and show main window
        print("Creating main window...")
        window = IMGFactory(settings)
        window.show()

        print("Application ready")

        # Start event loop
        return app.exec()

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
