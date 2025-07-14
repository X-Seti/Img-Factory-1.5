#this belongs in gui/ __init__.py - Version: 18
# X-Seti - July12 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory GUI Module
Modular GUI components for IMG Factory 1.5
"""

# Import main GUI components
from .main_window import IMGFactoryMainWindow, create_main_window
from .panel_controls import (
    create_control_panel, 
    create_right_panel_with_pastel_buttons,
    update_button_states,
    DraggableButton,
    ButtonPreset,
    ButtonFactory,
    ButtonPresetManager,
    ButtonPanel
)
from .panel_manager import PanelManager
from .tear_off import (
    TearOffPanel,
    TearOffPanelManager,
    add_panel_menu_to_menubar
)
from .log_panel import create_log_panel, setup_logging_for_main_window
from .status_bar import create_status_bar, create_enhanced_status_bar
from core.dialogs import (
    show_about_dialog, show_export_options_dialog,
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
    
    # Panel controls (consolidated from buttons.py, control_panels.py, button_panel.py, panels.py)
    'create_control_panel',
    'create_right_panel_with_pastel_buttons',  # Main GUI layout function
    'update_button_states',
    
    # Advanced button system
    'DraggableButton',
    'ButtonPreset', 
    'ButtonFactory',
    'ButtonPresetManager',
    
    # Panel classes
    'FilterSearchPanel',
    'ButtonPanel',
    'PanelManager',
    
    # Tear-off system
    'TearOffPanel',
    'TearOffPanelManager', 
    'add_panel_menu_to_menubar',
    
    # GUI components
    'create_log_panel',
    'create_status_bar',
    'create_enhanced_status_bar',
    
    # Utility functions
    'setup_logging_for_main_window',
    
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
    'description': 'Consolidated GUI components for IMG Factory',
    'components': [
        'main_window - Main application window',
        'panel_controls - Consolidated button and panel system',
        'tear_off - Tear-off panel functionality', 
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


def setup_panel_system(main_window):
    """Setup complete panel system with tear-off functionality"""
    try:
        # Create tear-off panel manager
        tearoff_manager = TearOffPanelManager(main_window)
        main_window.tearoff_manager = tearoff_manager
        
        # Create main control panel
        control_panel = create_right_panel_with_pastel_buttons(main_window)
        main_window.control_panel = control_panel
        
        # Add panel menu to menu bar if available
        if hasattr(main_window, 'menuBar'):
            add_panel_menu_to_menubar(main_window.menuBar(), tearoff_manager)
        
        main_window.log_message("✅ Panel system setup complete")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error setting up panel system: {str(e)}")
        return False


# Integration helpers
def integrate_with_existing_main_window(main_window):
    """Integrate GUI components with existing main window"""
    try:
        # Setup panel system
        setup_panel_system(main_window)
        
        # Setup logging if not already done
        if not hasattr(main_window, 'log_message'):
            setup_logging_for_main_window(main_window)
        
        main_window.log_message("✅ GUI integration complete")
        
    except Exception as e:
        print(f"Error integrating GUI components: {e}")


# Backward compatibility functions
def create_control_panel_legacy(main_window):
    """Legacy function for backward compatibility"""
    return create_control_panel(main_window)


def create_button_panel_legacy(main_window):
    """Legacy function for backward compatibility"""
    return create_right_panel_with_pastel_buttons(main_window)
