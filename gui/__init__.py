#this belongs in gui/ __init__.py - version 17
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory GUI Module
Modular GUI components for IMG Factory 1.5
"""

# Import main GUI components
from .main_window import IMGFactoryMainWindow, create_main_window
#from .table_view import create_entries_table_panel, IMGEntriesTable, populate_table_with_sample_data
from .control_panels import create_control_panel, update_button_states
from .log_panel import create_log_panel, setup_logging_for_main_window
from .status_bar import create_status_bar, create_enhanced_status_bar
from .dialogs import (
    show_about_dialog, show_search_dialog, show_export_options_dialog,
    show_import_options_dialog, show_error_dialog, show_warning_dialog,
    show_question_dialog, show_info_dialog, show_progress_dialog
)

# Version info
__version__ = "1.5.0"
__author__ = "X-Seti"

# Export main classes and functions
__all__ = [
    # Main window
    'IMGFactoryMainWindow',
    'create_main_window',
    
    # GUI components
    'create_menu_bar',
    'create_entries_table_panel', 
    'create_control_panel',
    'create_log_panel',
    'create_status_bar',
    'create_enhanced_status_bar',
    
    # Table components
    'IMGEntriesTable',
    'populate_table_with_sample_data',
    
    # Utility functions
    'update_button_states',
    'setup_logging_for_main_window',
    'register_global_shortcuts',
    
    # Dialogs
    'show_about_dialog',
    'show_search_dialog', 
    'show_export_options_dialog',
    'show_import_options_dialog',
    'show_error_dialog',
    'show_warning_dialog',
    'show_question_dialog',
    'show_info_dialog',
    'show_progress_dialog',
]

# Module information
MODULE_INFO = {
    'name': 'IMG Factory GUI',
    'version': __version__,
    'author': __author__,
    'description': 'Modular GUI components for IMG Factory',
    'components': [
        'main_window - Main application window',
        'menu_system - Menu bar and keyboard shortcuts',
        'table_view - IMG entries table and file info',
        'control_panels - Control button panels',
        'log_panel - Activity log and message display',
        'status_bar - Status information and progress',
        'dialogs - Common dialog windows',
    ]
}


def get_module_info():
    """Get module information"""
    return MODULE_INFO


def create_complete_gui(app_settings=None):
    """Create complete GUI with all components"""
    # Create main window
    main_window = create_main_window(app_settings)
    
    # Setup logging
    setup_logging_for_main_window(main_window)
    
    # Register global shortcuts
    register_global_shortcuts(main_window)
    
    # Initial status
    main_window.log_message("GUI components initialized")
    main_window.show_status("Ready")
    
    return main_window


def apply_gui_theme(main_window, theme_name="default"):
    """Apply theme to GUI components"""
    try:
        # Apply theme to status bar
        from .status_bar import StatusBarTheme
        StatusBarTheme.apply_theme(main_window.statusBar(), theme_name)
        
        # Apply theme to other components as needed
        main_window.log_message(f"Applied theme: {theme_name}")
        
    except Exception as e:
        if hasattr(main_window, 'log_warning'):
            main_window.log_warning(f"Failed to apply theme: {str(e)}")


# Integration helpers
def integrate_with_existing_main_window(main_window):
    """Integrate GUI components with existing main window"""
    try:
        # Setup logging if not present
        if not hasattr(main_window, 'log_message'):
            setup_logging_for_main_window(main_window)
        
        # Add status bar methods if not present
        if not hasattr(main_window, 'show_status'):
            from .status_bar import integrate_with_existing_status_bar
            integrate_with_existing_status_bar(main_window)
        
        # Register shortcuts
        register_global_shortcuts(main_window)
        
        main_window.log_message("GUI components integrated")
        return True
        
    except Exception as e:
        print(f"Failed to integrate GUI components: {e}")
        return False


# Compatibility functions
def setup_legacy_compatibility(main_window):
    """Setup compatibility with legacy code"""
    # Add legacy method aliases
    if not hasattr(main_window, 'themed_button'):
        from .control_panels import create_action_button
        main_window.themed_button = lambda text, action_type=None, icon=None, bold=False: \
            create_action_button(text, action_type, main_window, "placeholder_method")
    
    # Ensure log methods exist
    if not hasattr(main_window, 'log_message'):
        main_window.log_message = lambda msg: print(f"LOG: {msg}")
        main_window.log_error = lambda msg: print(f"ERROR: {msg}")
        main_window.log_warning = lambda msg: print(f"WARNING: {msg}")


# Module initialization
def initialize_gui_module():
    """Initialize the GUI module"""
    print(f"IMG Factory GUI Module {__version__} loaded")
    print(f"Components: {len(MODULE_INFO['components'])} available")


# Auto-initialize when imported
initialize_gui_module()
