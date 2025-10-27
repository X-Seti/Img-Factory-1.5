#this belongs in components/Img_Factory/img_factory_init.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - Complete Initialization System

"""
IMG Factory Complete Initialization - All 9 PHASES
This file contains the entire __init__ method split into logical function calls
Keeps 100% of original functionality intact
"""

from typing import Optional
from PyQt6.QtWidgets import QApplication

def imgfactory_init(main_window, settings): #vers 1
    """Complete IMG Factory initialization - All phases in order"""
    
    # Call super().__init__() first
    # Note: This should be called before this function in the actual __init__
    
    # Execute all phases
    phase1_core_setup(main_window, settings)
    phase2_essential_components(main_window)
    phase3_gui_creation(main_window)
    phase4_essential_integrations(main_window)
    phase5_core_functionality(main_window)
    phase6_gui_backend_shortcuts(main_window)
    phase7_optional_features(main_window)
    # PHASE 8 was commented out in original
    phase9_final_setup(main_window)
    
    # Final steps
    main_window.log_message("IMG Factory 1.5 initialized - Ready!")
    main_window.show()


def phase1_core_setup(main_window, settings): #vers 1
    """PHASE 1: CORE SETUP (Fast)"""
    from utils.app_settings_system import AppSettings
    
    main_window.settings = settings
    main_window.app_settings = settings if hasattr(settings, 'themes') else AppSettings()

    # Window setup
    main_window.setWindowTitle("IMG Factory 1.5 - X-Seti Oct27-2025")
    main_window.setGeometry(100, 100, 1200, 800)

    # Core data initialization
    from components.Img_Factory.imgload_thread import IMGLoadThread
    main_window.current_img = None
    main_window.current_col = None
    main_window.open_files = {}
    main_window.tab_counter = 0
    main_window.load_thread = None


def phase2_essential_components(main_window): #vers 1
    """PHASE 2: ESSENTIAL COMPONENTS (Fast)"""
    # Template manager (with better error handling)
    try:
        from methods.img_templates import IMGTemplateManager
        main_window.template_manager = IMGTemplateManager()
        print("Template manager initialized")
    except Exception as e:
        print(f"Template manager failed: {str(e)}")
        class DummyTemplateManager:
            def get_all_templates(self): #vers 1
                return []
            def get_default_templates(self): #vers 1
                return []
            def get_user_templates(self): #vers 1
                return []
        main_window.template_manager = DummyTemplateManager()


def phase3_gui_creation(main_window): #vers 1
    """PHASE 3: GUI CREATION (Medium)"""
    from gui.gui_layout import IMGFactoryGUILayout
    from gui.directory_tree_system import integrate_directory_tree_system
    from gui.gui_menu import IMGFactoryMenuBar
    from gui.file_menu_integration import add_project_menu_items
    from gui.tearoff_integration import integrate_tearoff_system
    from methods.dragdrop_functions import integrate_drag_drop_system
    
    # Create GUI layout
    main_window.gui_layout = IMGFactoryGUILayout(main_window)
    integrate_directory_tree_system(main_window)

    # Menu system
    main_window.menubar = main_window.menuBar()
    main_window.menu_bar_system = IMGFactoryMenuBar(main_window)

    # Menu callbacks
    callbacks = {
        "about": main_window.show_about,
        "open_img": main_window.open_img_file,
        "new_img": main_window.create_new_img,
        "exit": main_window.close,
        "img_validate": main_window.validate_img,
        "customize_interface": main_window.show_gui_settings,
    }
    main_window.menu_bar_system.set_callbacks(callbacks)
    integrate_drag_drop_system(main_window)

    # Create main UI (includes tab system setup)
    main_window._create_ui()

    # Additional UI integrations
    add_project_menu_items(main_window)
    integrate_tearoff_system(main_window)


def phase4_essential_integrations(main_window): #vers 1
    """PHASE 4: ESSENTIAL INTEGRATIONS (Medium)"""
    from methods.col_export_shared import integrate_col_export_shared
    from methods.ide_parser_functions import integrate_ide_parser
    from gui.ide_dialog import integrate_ide_dialog
    from methods.img_routing_operations import install_operation_routing
    from core.dump import integrate_dump_functions
    from methods.img_integration import integrate_img_functions
    from core.export import integrate_export_functions
    from core.impotr import integrate_import_functions
    from core.remove import integrate_remove_functions
    from core.save_entry import integrate_save_entry_function
    from core.rebuild_all import integrate_batch_rebuild_functions
    from core.rebuild import integrate_rebuild_functions
    from core.imgcol_rename import integrate_imgcol_rename_functions
    from core.imgcol_replace import integrate_imgcol_replace_functions
    from core.imgcol_convert import integrate_imgcol_convert_functions
    from core.export_via import export_via_function
    from core.import_via import integrate_import_via_functions
    from core.remove_via import integrate_remove_via_functions
    from methods.img_entry_operations import integrate_entry_operations
    from methods.img_import_export import integrate_import_export_functions
    from core.close import install_close_functions
    from methods.populate_img_table import install_img_table_populator
    from methods.update_ui_for_loaded_img import integrate_update_ui_for_loaded_img
    
    # Core parsers (now safe to use log_message)
    integrate_col_export_shared(main_window)
    integrate_ide_parser(main_window)
    integrate_ide_dialog(main_window)
    install_operation_routing(main_window)
    integrate_dump_functions(main_window)
    integrate_img_functions(main_window)
    integrate_export_functions(main_window)
    integrate_import_functions(main_window)
    integrate_remove_functions(main_window)
    integrate_save_entry_function(main_window)
    integrate_batch_rebuild_functions(main_window)
    integrate_rebuild_functions(main_window)

    integrate_imgcol_rename_functions(main_window)
    integrate_imgcol_replace_functions(main_window)
    integrate_imgcol_convert_functions(main_window)

    main_window.export_via = lambda: export_via_function(main_window)
    integrate_import_via_functions(main_window)
    integrate_remove_via_functions(main_window)
    integrate_entry_operations(main_window)
    integrate_import_export_functions(main_window)

    # File operations
    install_close_functions(main_window)

    # Table population (needed for IMG display)
    install_img_table_populator(main_window)

    # Update UI system
    integrate_update_ui_for_loaded_img(main_window)


def phase5_core_functionality(main_window): #vers 1
    """PHASE 5: CORE FUNCTIONALITY (Medium)"""
    from core.export import export_selected_function, export_all_function
    from core.dump import dump_all_function, dump_selected_function
    from methods.refresh_table_functions import integrate_refresh_table
    from core.file_type_filter import integrate_file_filtering
    
    main_window.export_selected = lambda: export_selected_function(main_window)
    main_window.export_all = lambda: export_all_function(main_window)
    main_window.dump_all = lambda: dump_all_function(main_window)
    main_window.dump_selected = lambda: dump_selected_function(main_window)
    integrate_refresh_table(main_window)

    # TXD Editor Integration
    try:
        main_window.txd_editor = None
        main_window.log_message("TXD Editor available")
    except Exception as e:
        main_window.log_message(f"TXD Editor failed: {str(e)}")

    # File extraction
    try:
        from core.file_extraction import setup_complete_extraction_integration
        setup_complete_extraction_integration(main_window)
        main_window.log_message("File extraction integrated")
    except Exception as e:
        main_window.log_message(f"Extraction integration failed: {str(e)}")

    # COL System Integration
    try:
        from methods.populate_col_table import load_col_file_safely
        main_window.load_col_file_safely = lambda file_path: load_col_file_safely(main_window, file_path)
        main_window.log_message("COL file loading enabled")
    except Exception as e:
        main_window.log_message(f"COL loading setup failed: {str(e)}")

    # File filtering
    integrate_file_filtering(main_window)


def phase6_gui_backend_shortcuts(main_window): #vers 1
    """PHASE 6: GUI BACKEND & SHORTCUTS (Medium)"""
    from gui.gui_backend import GUIBackend
    from core.shortcuts import setup_all_shortcuts
    from core.right_click_actions import setup_table_context_menu
    
    # GUI backend
    main_window.gui_backend = GUIBackend(main_window)

    # Keyboard shortcuts
    setup_all_shortcuts(main_window)

    # Context menus
    setup_table_context_menu(main_window)


def phase7_optional_features(main_window): #vers 1
    """PHASE 7: OPTIONAL FEATURES (Heavy - Can be delayed)"""
    from gui.autosave_menu import integrate_autosave_menu
    from core.theme_integration import integrate_theme_system
    from utils.app_settings_system import apply_theme_to_app
    from methods.progressbar_functions import integrate_progress_system
    from core.img_split import integrate_split_functions
    from core.rw_unk_snapshot import integrate_unknown_rw_detection
    from core.rebuild import integrate_rebuild_functions
    from core.rebuild_all import integrate_batch_rebuild_functions
    from core.clean import integrate_clean_utilities
    
    # Auto-save menu
    integrate_autosave_menu(main_window)

    # Theme system
    integrate_theme_system(main_window)
    if hasattr(main_window.app_settings, 'themes'):
        apply_theme_to_app(QApplication.instance(), main_window.app_settings)

    # Progress system
    integrate_progress_system(main_window)

    # Split functions
    integrate_split_functions(main_window)

    # RW detection
    integrate_unknown_rw_detection(main_window)

    try:
        integrate_rebuild_functions(main_window)
        integrate_batch_rebuild_functions(main_window)
        integrate_clean_utilities(main_window)
        main_window.log_message("All systems integrated")
    except Exception as e:
        main_window.log_message(f"Integration failed: {e}")


def phase9_final_setup(main_window): #vers 1
    """PHASE 9: HIGHLIGHTING & FINAL SETUP"""
    from methods.import_highlight_system import enable_import_highlighting
    
    # Import highlighting
    enable_import_highlighting(main_window)

    # Restore settings
    main_window._restore_settings()

    # Utility functions
    main_window.setup_missing_utility_functions()

    # Final reload alias
    main_window.reload_table = main_window.reload_current_file


__all__ = [
    'imgfactory_init',
    'phase1_core_setup',
    'phase2_essential_components',
    'phase3_gui_creation',
    'phase4_essential_integrations',
    'phase5_core_functionality',
    'phase6_gui_backend_shortcuts',
    'phase7_optional_features',
    'phase9_final_setup'
]
