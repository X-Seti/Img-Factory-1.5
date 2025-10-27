#!/usr/bin/env python3
"""
X-Seti - Oct27 2025 - IMG Factory 1.5 - Main Entry Point
#this belongs in root /imgfactory.py - version 72
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
for path in [current_dir, current_dir / "components", current_dir / "gui", current_dir / "utils"]:
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QMainWindow

# Components - Import all split modules
from components.Img_Factory.img_factory_init import imgfactory_init
from components.Img_Factory.img_factory_thread import IMGLoadThread

# Import all method modules
import components.Img_Factory.img_factory_logging as logging_methods
import components.Img_Factory.img_factory_corruption as corruption_methods
import components.Img_Factory.img_factory_txd_workshop as txd_methods
import components.Img_Factory.img_factory_tab_system as tab_methods
import components.Img_Factory.img_factory_col_integration as col_methods
import components.Img_Factory.img_factory_file_operations as file_methods
import components.Img_Factory.img_factory_img_operations as img_methods
import components.Img_Factory.img_factory_entry_operations as entry_methods
import components.Img_Factory.img_factory_ui_dialogs as ui_methods
import components.Img_Factory.img_factory_utility as utility_methods

App_name = "Img Factory 1.5"


class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""

    def __init__(self, settings): #vers 1
        """Initialize IMG Factory with optimized loading order"""
        super().__init__()
        imgfactory_init(self, settings)

    # Inject all methods from modules
    log_message = logging_methods.log_message
    _append_log_message = logging_methods._append_log_message
    debug_img_before_loading = logging_methods.debug_img_before_loading
    show_debug_settings = logging_methods.show_debug_settings

    analyze_corruption = corruption_methods.analyze_corruption
    analyze_img_corruption = corruption_methods.analyze_img_corruption
    quick_fix_corruption = corruption_methods.quick_fix_corruption
    clean_filenames_only = corruption_methods.clean_filenames_only
    export_corruption_report = corruption_methods.export_corruption_report

    open_txd_workshop_docked = txd_methods.open_txd_workshop_docked
    _handle_txd_overlay_tab_switch = txd_methods._handle_txd_overlay_tab_switch
    setup_unified_signals = txd_methods.setup_unified_signals
    _open_txd_workshop = txd_methods._open_txd_workshop
    _update_workshop_on_tab_change = txd_methods._update_workshop_on_tab_change
    _on_workshop_closed = txd_methods._on_workshop_closed

    _create_ui = tab_methods._create_ui
    _create_initial_tab = tab_methods._create_initial_tab
    _find_table_in_tab = tab_methods._find_table_in_tab
    _log_current_tab_state = tab_methods._log_current_tab_state
    ensure_current_tab_references_valid = tab_methods.ensure_current_tab_references_valid
    _update_info_bar_for_current_file = tab_methods._update_info_bar_for_current_file
    setup_robust_tab_system = tab_methods.setup_robust_tab_system
    _reindex_open_files_robust = tab_methods._reindex_open_files_robust

    setup_col_integration = col_methods.setup_col_integration
    _update_ui_for_loaded_col = col_methods._update_ui_for_loaded_col
    handle_col_file_open = col_methods.handle_col_file_open
    load_col_file_safely = col_methods.load_col_file_safely
    _load_col_file_in_new_tab = col_methods._load_col_file_in_new_tab
    _populate_col_table_img_format = col_methods._populate_col_table_img_format
    _on_col_loaded = col_methods._on_col_loaded
    enable_col_debug = col_methods.enable_col_debug
    disable_col_debug = col_methods.disable_col_debug
    toggle_col_debug = col_methods.toggle_col_debug

    open_img_file = file_methods.open_img_file
    open_file_dialog = file_methods.open_file_dialog
    load_file_unified = file_methods.load_file_unified
    _load_img_file_in_new_tab = file_methods._load_img_file_in_new_tab
    _on_img_load_progress = file_methods._on_img_load_progress
    _on_img_load_error = file_methods._on_img_load_error

    _on_img_loaded = img_methods._on_img_loaded
    _populate_real_img_table = img_methods._populate_real_img_table
    _on_load_error = img_methods._on_load_error
    close_all_img = img_methods.close_all_img

    import_files = entry_methods.import_files
    export_selected = entry_methods.export_selected
    export_all = entry_methods.export_all
    remove_selected = entry_methods.remove_selected
    import_via_tool = entry_methods.import_via_tool
    export_via_tool = entry_methods.export_via_tool

    create_new_img = ui_methods.create_new_img
    validate_img = ui_methods.validate_img
    show_gui_settings = ui_methods.show_gui_settings
    show_about = ui_methods.show_about
    _restore_settings = ui_methods._restore_settings
    _save_settings = ui_methods._save_settings
    closeEvent = ui_methods.closeEvent

    setup_missing_utility_functions = utility_methods.setup_missing_utility_functions
    update_button_states = utility_methods.update_button_states


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
