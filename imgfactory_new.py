#!/usr/bin/env python3
"""
X-Seti - July22 2025 - IMG Factory 1.5 - AtariST version :D
#this belongs in root /imgfactory.py - version 71
"""
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
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut, QTextCursor

# OR use the full path:
from utils.app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog

#components
from components.Img_Creator.img_creator import NewIMGDialog, IMGCreationThread
#from components.Txd_Editor.txd_workshop import TXDEditor

# Components - Import all split modules
from components.Img_Factory.img_factory_init import imgfactory_init

#debug
from debug.col_debug_functions import set_col_debug_enabled
from debug.unified_debug_functions import integrate_all_improvements, install_debug_control_system

#Core functions.
from core.img_formats import GameSpecificIMGDialog, IMGCreator
from core.file_extraction import setup_complete_extraction_integration
from core.file_type_filter import integrate_file_filtering
from core.rw_versions import get_rw_version_name
from core.right_click_actions import integrate_right_click_actions, setup_table_context_menu
from core.shortcuts import setup_all_shortcuts, create_debug_keyboard_shortcuts
from core.convert import convert_img, convert_img_format
from core.img_split import integrate_split_functions
from core.theme_integration import integrate_theme_system
from core.create import create_new_img
from core.open import _detect_and_open_file, open_file_dialog, _detect_file_type
from core.clean import integrate_clean_utilities
from core.close import install_close_functions, setup_close_manager
from core.export import integrate_export_functions
from core.impotr import integrate_import_functions #import impotr
from core.remove import integrate_remove_functions
from core.export import export_selected_function, export_all_function, integrate_export_functions
from core.dump import dump_all_function, dump_selected_function, integrate_dump_functions
from core.import_via import integrate_import_via_functions
from core.remove_via import integrate_remove_via_functions
from core.export_via import export_via_function
from core.rebuild import integrate_rebuild_functions
from core.rebuild_all import integrate_batch_rebuild_functions
from core.imgcol_rename import integrate_imgcol_rename_functions
from core.imgcol_replace import integrate_imgcol_replace_functions
from core.imgcol_convert import integrate_imgcol_convert_functions
from core.save_entry import integrate_save_entry_function
from core.rw_unk_snapshot import integrate_unknown_rw_detection
from core.col_viewer_integration import integrate_col_viewer

#gui-layout
from gui.ide_dialog import integrate_ide_dialog
from gui.gui_backend import ButtonDisplayMode, GUIBackend
from gui.main_window import IMGFactoryMainWindow
from gui.col_display import update_col_info_bar_enhanced
from gui.gui_layout import IMGFactoryGUILayout
from gui.unified_button_theme import apply_unified_button_theme
from gui.gui_menu import IMGFactoryMenuBar
from gui.autosave_menu import integrate_autosave_menu
from gui.file_menu_integration import add_project_menu_items
from gui.directory_tree_system import integrate_directory_tree_system
from gui.tearoff_integration import integrate_tearoff_system

# After GUI setup:
from gui.gui_context import (add_col_context_menu_to_entries_table, open_col_file_dialog, open_col_batch_proc_dialog, open_col_editor_dialog, analyze_col_file_dialog)

#Shared Methods - Shared Functions.
from methods.img_core_classes import (IMGFile, IMGEntry, IMGVersion, Platform, IMGEntriesTable, FilterPanel, IMGFileInfoPanel, TabFilterWidget, integrate_filtering, create_entries_table_panel, format_file_size)
from methods.col_core_classes import (COLFile, COLModel, COLVersion, COLMaterial, COLFaceGroup, COLSphere, COLBox, COLVertex, COLFace, Vector3, BoundingBox, diagnose_col_file, set_col_debug_enabled, is_col_debug_enabled)

from methods.col_integration import integrate_complete_col_system
from methods.col_functions import setup_complete_col_integration
from methods.col_parsing_functions import load_col_file_safely
from methods.col_structure_manager import COLStructureManager
from methods.img_analyze import analyze_img_corruption, show_analysis_dialog
from methods.img_integration import integrate_img_functions, img_core_functions
from methods.img_routing_operations import install_operation_routing
from methods.img_validation import IMGValidator


from methods.populate_img_table import reset_table_styling, install_img_table_populator
from methods.progressbar_functions import integrate_progress_system
from methods.update_ui_for_loaded_img import update_ui_for_loaded_img, integrate_update_ui_for_loaded_img
from methods.import_highlight_system import enable_import_highlighting
from methods.refresh_table_functions import integrate_refresh_table
from methods.img_entry_operations import integrate_entry_operations
from methods.img_import_export import integrate_import_export_functions
from methods.col_export_shared import integrate_col_export_shared
#from methods.mirror_tab_shared import show_mirror_tab_selection
from methods.ide_parser_functions import integrate_ide_parser
from methods.find_dups_functions import find_duplicates_by_hash, show_duplicates_dialog
from methods.dragdrop_functions import integrate_drag_drop_system
from methods.img_templates import IMGTemplateManager, TemplateManagerDialog

from components.Img_Factory.img_factory_thread import IMGLoadThread

# Import all method modules - Img Factory split
from components.Img_Factory.img_factory_logging import logging_methods
from components.Img_Factory.img_factory_corruption import corruption_methods
from components.Img_Factory.img_factory_txd_workshop import txd_methods
from components.Img_Factory.img_factory_tab_system import tab_methods
from components.Img_Factory.img_factory_col_integration import col_methods
from components.Img_Factory.img_factory_file_operations import file_methods
from components.Img_Factory.img_factory_img_operations import img_methods
from components.Img_Factory.img_factory_entry_operations import entry_methods
from components.Img_Factory.img_factory_ui_dialogs import ui_methods
from components.Img_Factory.img_factory_utility import utility_methods

App_name = "Img Factory 1.5"

def setup_rebuild_system(self): #vers 1
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


class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""
    def __init__(self, settings): #vers 62
        """Initialize IMG Factory with optimized loading order"""
        super().__init__()

        # === PHASE 1: CORE SETUP (Fast) ===
        self.settings = settings
        self.app_settings = settings if hasattr(settings, 'themes') else AppSettings()

        # Window setup
        self.setWindowTitle("IMG Factory 1.5 - X-Seti Aug09-2025")
        self.setGeometry(100, 100, 1200, 800)

        # Core data initialization
        self.current_img: Optional[IMGFile] = None
        self.current_col: Optional[COLFile] = None

        #self.current_txd = None
        #self.txd_workshops = []
        self.open_files = {}
        self.tab_counter = 0
        self.load_thread: Optional[IMGLoadThread] = None

        # === PHASE 2: ESSENTIAL COMPONENTS (Fast) ===

        # Template manager (with better error handling)
        try:
            from methods.img_templates import IMGTemplateManager
            self.template_manager = IMGTemplateManager()
            print("Template manager initialized")
        except Exception as e:
            print(f"Template manager failed: {str(e)}")
            class DummyTemplateManager:
                def get_all_templates(self): return []
                def get_default_templates(self): return []
                def get_user_templates(self): return []
            self.template_manager = DummyTemplateManager()

        # === PHASE 3: GUI CREATION (Medium) ===

        # Create GUI layout
        self.gui_layout = IMGFactoryGUILayout(self)
        integrate_directory_tree_system(self)

        # Menu system
        self.menubar = self.menuBar()
        self.menu_bar_system = IMGFactoryMenuBar(self)

        # Menu callbacks
        callbacks = {
            "about": self.show_about,
            "open_img": self.open_img_file,
            "new_img": self.create_new_img,
            "exit": self.close,
            "img_validate": self.validate_img,
            "customize_interface": self.show_gui_settings,
        }
        self.menu_bar_system.set_callbacks(callbacks)
        integrate_drag_drop_system(self)

        # Create main UI (includes tab system setup)
        self._create_ui()

        # Additional UI integrations
        add_project_menu_items(self)
        #integrate_tab_awareness_system(self)
        integrate_tearoff_system(self)

        # === PHASE 4: ESSENTIAL INTEGRATIONS (Medium) ===

        # Core parsers (now safe to use log_message)
        integrate_col_export_shared(self)
        integrate_ide_parser(self)
        integrate_ide_dialog(self)
        install_operation_routing(self)
        integrate_dump_functions(self)
        integrate_img_functions(self)
        integrate_export_functions(self)
        integrate_import_functions(self)
        integrate_remove_functions(self)
        integrate_save_entry_function(self)
        integrate_batch_rebuild_functions(self)
        integrate_rebuild_functions(self)

        integrate_imgcol_rename_functions(self)
        integrate_imgcol_replace_functions(self)
        integrate_imgcol_convert_functions(self)

        self.export_via = lambda: export_via_function(self)
        integrate_import_via_functions(self)
        integrate_remove_via_functions(self)
        integrate_entry_operations(self)
        integrate_import_export_functions(self)

        # File operations
        install_close_functions(self)

        # Table population (needed for IMG display)
        install_img_table_populator(self)

        # Update UI system
        integrate_update_ui_for_loaded_img(self)

        # === PHASE 5: CORE FUNCTIONALITY (Medium) ===
        self.export_selected = lambda: export_selected_function(self)
        self.export_all = lambda: export_all_function(self)
        self.dump_all = lambda: dump_all_function(self)
        self.dump_selected = lambda: dump_selected_function(self)
        integrate_refresh_table(self)

        # TXD Editor Integration
        try:
            self.txd_editor = None
            self.log_message("TXD Editor available")
        except Exception as e:
            self.log_message(f"TXD Editor failed: {str(e)}")

        # File extraction
        try:
            from core.file_extraction import setup_complete_extraction_integration
            setup_complete_extraction_integration(self)
            self.log_message("File extraction integrated")
        except Exception as e:
            self.log_message(f"Extraction integration failed: {str(e)}")

        # COL System Integration
        try:
            from methods.populate_col_table import load_col_file_safely
            self.load_col_file_safely = lambda file_path: load_col_file_safely(self, file_path)
            self.log_message("COL file loading enabled")
        except Exception as e:
            self.log_message(f"COL loading setup failed: {str(e)}")

        # File filtering
        integrate_file_filtering(self)


        # === PHASE 6: GUI BACKEND & SHORTCUTS (Medium) ===

        # GUI backend
        self.gui_backend = GUIBackend(self)

        # Keyboard shortcuts
        setup_all_shortcuts(self)

        # Context menus
        setup_table_context_menu(self)

        # === PHASE 7: OPTIONAL FEATURES (Heavy - Can be delayed) ===

        # Auto-save menu
        integrate_autosave_menu(self)

        # Theme system
        integrate_theme_system(self)
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)

        # Progress system
        integrate_progress_system(self)

        # Split functions
        integrate_split_functions(self)

        # RW detection
        integrate_unknown_rw_detection(self)

        try:
            integrate_rebuild_functions(self)
            integrate_batch_rebuild_functions(self)
            integrate_clean_utilities(self)
            self.log_message("All systems integrated")
        except Exception as e:
            self.log_message(f"Integration failed: {e}")

        """
        try:
            from core.img_corruption_analyzer import setup_corruption_analyzer
            setup_corruption_analyzer(self)
            self.log_message("IMG corruption analyzer integrated")
        except Exception as e:
            self.log_message(f"Corruption analyzer integration failed: {e}")

        # Debug features
        try:
            integrate_debug_patch(self)
            apply_visibility_fix(self)
            create_debug_keyboard_shortcuts(self)
            install_debug_control_system(self)
            # self.log_message("Debug features loaded")
        except Exception as e:
            self.log_message(f"Debug features failed: {str(e)}")

        """
        # === PHASE 9: HIGHLIGHTING & FINAL SETUP ===

        # Import highlighting
        enable_import_highlighting(self)

        # Restore settings
        self._restore_settings()

        # Utility functions
        self.setup_missing_utility_functions()

        # Final reload alias
        self.reload_table = self.reload_current_file

        # === STARTUP COMPLETE ===
        self.log_message("IMG Factory 1.5 initialized - Ready!")

        # Show window (non-blocking)
        self.show()

        self.logging_methods()


def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(App_name)

        from utils.app_settings_system import AppSettings
        settings = AppSettings()
        settings.load_settings()

        window = IMGFactory(settings)
        window.show()

        return app.exec()

    except Exception as e:
        print(f"Fatal error in main(): {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
