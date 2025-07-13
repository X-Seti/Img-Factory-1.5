#this belongs in gui/ __init__.py - Version: 19
# X-Seti - July13 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory GUI Module
Modular GUI components for IMG Factory 1.5
"""

# Import main GUI components with error handling
try:
    from .main_window import IMGFactoryMainWindow, create_main_window
except ImportError:
    # Fallback if main_window doesn't exist
    IMGFactoryMainWindow = None
    create_main_window = None

# Import panel controls with safe imports
try:
    from .panel_controls import (
        create_control_panel, 
        create_right_panel_with_pastel_buttons,
        update_button_states,
        create_pastel_button,
        get_short_text,
        lighten_color,
        darken_color
    )
except ImportError as e:
    print(f"Warning: Could not import some panel_controls: {e}")
    # Create fallback functions
    def create_control_panel(main_window):
        from PyQt6.QtWidgets import QWidget
        return QWidget()
    
    def create_right_panel_with_pastel_buttons(main_window):
        from PyQt6.QtWidgets import QWidget
        return QWidget()
    
    def update_button_states(main_window):
        pass

# Import advanced button system with fallbacks
try:
    from .panel_controls import DraggableButton, ButtonPreset, ButtonFactory, ButtonPresetManager
except ImportError:
    print("Warning: Advanced button classes not available")
    # Create fallback classes
    from PyQt6.QtWidgets import QPushButton
    
    class DraggableButton(QPushButton):
        def __init__(self, text, button_id=None, action_type=None):
            super().__init__(text)
            self.button_id = button_id
            self.action_type = action_type
    
    class ButtonPreset:
        def __init__(self, name, description=""):
            self.name = name
            self.description = description
    
    class ButtonFactory:
        @staticmethod
        def create_button(button_id, callbacks=None):
            return DraggableButton(button_id)
    
    class ButtonPresetManager:
        def __init__(self, settings_path=None):
            pass

# Import panel classes with fallbacks
try:
    from .panel_controls import FilterSearchPanel, ButtonPanel
except ImportError:
    print("Warning: Panel classes not available, using fallbacks")
    from PyQt6.QtWidgets import QWidget
    
    class FilterSearchPanel(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
    
    class ButtonPanel(QWidget):
        def __init__(self, parent=None, panel_type="default"):
            super().__init__(parent)

# Import panel manager
try:
    from .panel_manager import PanelManager
except ImportError:
    print("Warning: PanelManager not available")
    class PanelManager:
        def __init__(self, main_window):
            pass

# Import tear-off system
try:
    from .tear_off import (
        TearOffPanel,
        TearOffPanelManager,
        add_panel_menu_to_menubar
    )
except ImportError:
    print("Warning: Tear-off system not available")
    from PyQt6.QtWidgets import QWidget
    
    class TearOffPanel(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
    
    class TearOffPanelManager:
        def __init__(self, main_window):
            pass
    
    def add_panel_menu_to_menubar(menubar, panel_manager):
        pass

# Import log panel
try:
    from .log_panel import create_log_panel, setup_logging_for_main_window
except ImportError:
    print("Warning: Log panel not available")
    from PyQt6.QtWidgets import QTextEdit
    
    def create_log_panel(parent=None):
        return QTextEdit()
    
    def setup_logging_for_main_window(main_window):
        pass

# Import status bar
try:
    from .status_bar import create_status_bar, create_enhanced_status_bar
except ImportError:
    print("Warning: Status bar not available")
    from PyQt6.QtWidgets import QStatusBar
    
    def create_status_bar(parent=None):
        return QStatusBar()
    
    def create_enhanced_status_bar(parent=None):
        return QStatusBar()

# Import dialogs
try:
    from .dialogs import (
        show_about_dialog, show_search_dialog, show_export_options_dialog,
        show_import_options_dialog, show_error_dialog, show_warning_dialog,
        show_question_dialog, show_info_dialog, show_progress_dialog
    )
except ImportError:
    print("Warning: Dialog functions not available")
    from PyQt6.QtWidgets import QMessageBox
    
    def show_about_dialog(parent=None):
        QMessageBox.about(parent, "About", "IMG Factory 1.5")
    
    def show_search_dialog(parent=None):
        pass
    
    def show_export_options_dialog(parent=None):
        return False
    
    def show_import_options_dialog(parent=None):
        return False
    
    def show_error_dialog(parent=None, title="Error", message=""):
        QMessageBox.critical(parent, title, message)
    
    def show_warning_dialog(parent=None, title="Warning", message=""):
        QMessageBox.warning(parent, title, message)
    
    def show_question_dialog(parent=None, title="Question", message=""):
        return QMessageBox.question(parent, title, message)
    
    def show_info_dialog(parent=None, title="Info", message=""):
        QMessageBox.information(parent, title, message)
    
    def show_progress_dialog(parent=None):
        from PyQt6.QtWidgets import QProgressDialog
        return QProgressDialog(parent)

# Version info
__version__ = "1.5.0"
__author__ = "X-Seti"

# Export main classes and functions - Only export what actually exists
__all__ = [
    # Main window
    'IMGFactoryMainWindow',
    'create_main_window',
    
    # Panel controls - Core functions that should exist
    'create_control_panel',
    'create_right_panel_with_pastel_buttons',
    'update_button_states',
    
    # Advanced button system - With fallbacks
    'DraggableButton',
    'ButtonPreset', 
    'ButtonFactory',
    'ButtonPresetManager',
    
    # Panel classes - With fallbacks
    'FilterSearchPanel',
    'ButtonPanel',
    'PanelManager',
    
    # Tear-off system
    'TearOffPanel',
    'TearOffPanelManager', 
    'add_panel_menu_to_menubar',
    
    # GUI components
    'create_log_panel',
    'setup_logging_for_main_window',
    'create_status_bar',
    'create_enhanced_status_bar',
    
    # Dialog functions
    'show_about_dialog',
    'show_search_dialog', 
    'show_export_options_dialog',
    'show_import_options_dialog',
    'show_error_dialog',
    'show_warning_dialog',
    'show_question_dialog', 
    'show_info_dialog',
    'show_progress_dialog',
    
    # Utility functions from panel_controls
    'create_pastel_button',
    'get_short_text',
    'lighten_color',
    'darken_color',
    
    # Version info
    '__version__',
    '__author__'
]

# Optional: Log which components loaded successfully
try:
    _loaded_components = []
    if IMGFactoryMainWindow is not None:
        _loaded_components.append("main_window")
    if 'create_right_panel_with_pastel_buttons' in globals():
        _loaded_components.append("panel_controls")
    if 'PanelManager' in globals():
        _loaded_components.append("panel_manager")
    
    print(f"GUI module loaded successfully with components: {', '.join(_loaded_components)}")
except:
    pass
