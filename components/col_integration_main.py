#this belongs in components/col_integration_main.py - Version: 1
# X-Seti - July17 2025 - IMG Factory 1.5 - COL Integration Main
# Uses IMG debug system for COL integration

"""
COL Integration Main
Integrates all COL functionality into the main IMG Factory interface using IMG debug system
"""

import os
import sys
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QMessageBox, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QHeaderView, QAbstractItemView, QDialog, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QIcon, QShortcut, QKeySequence, QFont

# Import COL classes with IMG debug system
from components.col_core_classes import COLFile, COLModel, COLVersion
from components.col_debug_functions import col_debug_log, is_col_debug_enabled, debug_col_loading_process
from components.col_parsing_functions import COLParser
from components.img_debug_functions import img_debugger

##Methods list -
# add_col_file_detection
# add_col_tools_menu
# analyze_col_from_img
# create_col_editor_action
# create_col_file_dialog
# export_col_to_img_format
# integrate_complete_col_system
# setup_col_debug_for_main_window
# setup_col_integration_full
# setup_threaded_col_loading

def add_col_file_detection(img_factory_instance): #vers 1
    """Add COL file type detection to IMG entries using IMG debug system"""
    try:
        col_debug_log(img_factory_instance, "Setting up COL file detection in IMG entries", 'COL_INTEGRATION')
        
        # Enhance the file type detection in the entries table
        if hasattr(img_factory_instance, 'populate_entries_table'):
            original_populate = img_factory_instance.populate_entries_table
            
            def enhanced_populate_entries_table():
                # Call original method
                result = original_populate()
                
                # Add COL detection to entries
                if hasattr(img_factory_instance, 'current_img') and img_factory_instance.current_img:
                    for entry in img_factory_instance.current_img.entries:
                        if entry.name.lower().endswith('.col'):
                            col_debug_log(img_factory_instance, f"Detected COL file: {entry.name}", 'COL_DETECTION')
                
                return result
            
            img_factory_instance.populate_entries_table = enhanced_populate_entries_table
            col_debug_log(img_factory_instance, "COL file detection integrated", 'COL_INTEGRATION', 'SUCCESS')
            return True
            
    except Exception as e:
        col_debug_log(img_factory_instance, f"Error setting up COL detection: {e}", 'COL_INTEGRATION', 'ERROR')
        return False

def analyze_col_from_img(main_window, entry_name: str): #vers 1
    """Analyze COL file from IMG entry using IMG debug system"""
    try:
        col_debug_log(main_window, f"Analyzing COL file: {entry_name}", 'COL_ANALYSIS')
        
        if not main_window.current_img:
            col_debug_log(main_window, "No IMG file loaded", 'COL_ANALYSIS', 'ERROR')
            return False
        
        # Find the COL entry
        col_entry = None
        for entry in main_window.current_img.entries:
            if entry.name == entry_name:
                col_entry = entry
                break
        
        if not col_entry:
            col_debug_log(main_window, f"COL entry not found: {entry_name}", 'COL_ANALYSIS', 'ERROR')
            return False
        
        # Extract and analyze COL data
        col_data = col_entry.get_data()
        if not col_data:
            col_debug_log(main_window, f"Could not extract COL data from {entry_name}", 'COL_ANALYSIS', 'ERROR')
            return False
        
        # Create temporary COL file for analysis
        col_parser = COLParser()
        col_parser.set_debug(is_col_debug_enabled())
        
        analysis_result = col_parser.parse_col_data(col_data)
        
        # Show analysis results
        if analysis_result:
            info_text = f"COL Analysis: {entry_name}\n"
            info_text += f"Size: {len(col_data):,} bytes\n"
            info_text += f"Models: {analysis_result.get('model_count', 0)}\n"
            info_text += f"Version: {analysis_result.get('version', 'Unknown')}\n"
            
            QMessageBox.information(main_window, "COL Analysis", info_text)
            col_debug_log(main_window, f"COL analysis completed for {entry_name}", 'COL_ANALYSIS', 'SUCCESS')
            return True
        else:
            col_debug_log(main_window, f"COL analysis failed for {entry_name}", 'COL_ANALYSIS', 'ERROR')
            return False
            
    except Exception as e:
        col_debug_log(main_window, f"Error analyzing COL: {e}", 'COL_ANALYSIS', 'ERROR')
        return False

def add_col_tools_menu(main_window): #vers 1
    """Add COL tools menu to main window using IMG debug system"""
    try:
        col_debug_log(main_window, "Adding COL tools menu", 'COL_INTEGRATION')
        
        # Find or create Tools menu
        menu_bar = main_window.menuBar()
        tools_menu = None
        
        # Look for existing Tools menu
        for action in menu_bar.actions():
            if action.text() == "Tools":
                tools_menu = action.menu()
                break
        
        if not tools_menu:
            tools_menu = menu_bar.addMenu("Tools")
            col_debug_log(main_window, "Created new Tools menu", 'COL_INTEGRATION')
        
        # Add COL submenu
        col_menu = tools_menu.addMenu("🛡️ COL Tools")
        
        # COL file actions
        open_col_action = col_menu.addAction("Open COL File...")
        open_col_action.triggered.connect(lambda: create_col_file_dialog(main_window))
        
        col_menu.addSeparator()
        
        # COL creation actions
        create_col_action = col_menu.addAction("Create New COL...")
        create_col_action.triggered.connect(lambda: create_col_editor_action(main_window))
        
        # COL batch processing
        batch_col_action = col_menu.addAction("Batch Process COL Files...")
        batch_col_action.triggered.connect(lambda: open_col_batch_processor(main_window))
        
        col_menu.addSeparator()
        
        # COL settings
        col_settings_action = col_menu.addAction("COL Settings...")
        col_settings_action.triggered.connect(lambda: main_window.toggle_col_debug())
        
        col_debug_log(main_window, "COL tools menu added successfully", 'COL_INTEGRATION', 'SUCCESS')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error adding COL tools menu: {e}", 'COL_INTEGRATION', 'ERROR')
        return False

def create_col_file_dialog(main_window): #vers 1
    """Create COL file open dialog using IMG debug system"""
    try:
        col_debug_log(main_window, "Opening COL file dialog", 'COL_DIALOG')
        
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Open COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            col_debug_log(main_window, f"Selected COL file: {file_path}", 'COL_DIALOG')
            
            # Load COL file using core loader
            from core.loadcol import load_col_file_safely
            success = load_col_file_safely(main_window, file_path)
            
            if success:
                col_debug_log(main_window, f"COL file loaded successfully: {file_path}", 'COL_DIALOG', 'SUCCESS')
            else:
                col_debug_log(main_window, f"Failed to load COL file: {file_path}", 'COL_DIALOG', 'ERROR')
            
            return success
        else:
            col_debug_log(main_window, "COL file dialog cancelled", 'COL_DIALOG')
            return False
            
    except Exception as e:
        col_debug_log(main_window, f"Error in COL file dialog: {e}", 'COL_DIALOG', 'ERROR')
        return False

def create_col_editor_action(main_window): #vers 1
    """Create COL editor action using IMG debug system"""
    try:
        col_debug_log(main_window, "Opening COL editor", 'COL_EDITOR')
        
        from components.col_editor import COLEditorDialog
        
        editor_dialog = COLEditorDialog(main_window)
        result = editor_dialog.exec()
        
        if result:
            col_debug_log(main_window, "COL editor completed successfully", 'COL_EDITOR', 'SUCCESS')
        else:
            col_debug_log(main_window, "COL editor cancelled", 'COL_EDITOR')
        
        return result
        
    except Exception as e:
        col_debug_log(main_window, f"Error opening COL editor: {e}", 'COL_EDITOR', 'ERROR')
        QMessageBox.critical(main_window, "Error", f"Failed to open COL editor: {str(e)}")
        return False

def open_col_batch_processor(main_window): #vers 1
    """Open COL batch processor using IMG debug system"""
    try:
        col_debug_log(main_window, "Opening COL batch processor", 'COL_BATCH')
        
        from components.col_utilities import open_col_batch_proc_dialog
        
        result = open_col_batch_proc_dialog(main_window)
        
        if result:
            col_debug_log(main_window, "COL batch processor completed", 'COL_BATCH', 'SUCCESS')
        else:
            col_debug_log(main_window, "COL batch processor cancelled", 'COL_BATCH')
        
        return result
        
    except Exception as e:
        col_debug_log(main_window, f"Error in COL batch processor: {e}", 'COL_BATCH', 'ERROR')
        return False

def setup_threaded_col_loading(main_window): #vers 1
    """Setup threaded COL loading using IMG debug system"""
    try:
        col_debug_log(main_window, "Setting up threaded COL loading", 'COL_THREADING')
        
        from components.col_threaded_loader import COLBackgroundLoader
        
        # Create background loader
        col_loader = COLBackgroundLoader()
        
        # Connect signals
        if hasattr(main_window, '_on_col_loaded'):
            col_loader.col_loaded.connect(main_window._on_col_loaded)
        
        if hasattr(main_window, '_on_load_progress'):
            col_loader.progress_updated.connect(main_window._on_load_progress)
        
        # Store reference
        main_window.col_background_loader = col_loader
        
        col_debug_log(main_window, "Threaded COL loading setup complete", 'COL_THREADING', 'SUCCESS')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error setting up threaded COL loading: {e}", 'COL_THREADING', 'ERROR')
        return False

def setup_col_debug_for_main_window(main_window): #vers 1
    """Setup COL debug functionality for main window using IMG debug system"""
    try:
        from components.col_debug_functions import integrate_col_debug_with_main_window
        
        success = integrate_col_debug_with_main_window(main_window)
        
        if success:
            col_debug_log(main_window, "COL debug system integrated with main window", 'COL_INTEGRATION', 'SUCCESS')
        else:
            col_debug_log(main_window, "COL debug integration failed", 'COL_INTEGRATION', 'ERROR')
        
        return success
        
    except Exception as e:
        col_debug_log(main_window, f"Error setting up COL debug: {e}", 'COL_INTEGRATION', 'ERROR')
        return False

def export_col_to_img_format(main_window, col_file_path: str, output_img_path: str): #vers 1
    """Export COL file to IMG format using IMG debug system"""
    try:
        col_debug_log(main_window, f"Exporting COL to IMG: {col_file_path} -> {output_img_path}", 'COL_EXPORT')
        
        # Load COL file
        col_file = COLFile(col_file_path)
        if not col_file.load():
            col_debug_log(main_window, f"Failed to load COL file: {col_file_path}", 'COL_EXPORT', 'ERROR')
            return False
        
        # Create new IMG file
        from components.img_core_classes import IMGFile, IMGVersion
        img_file = IMGFile()
        
        if not img_file.create_new(output_img_path, IMGVersion.VERSION_2):
            col_debug_log(main_window, f"Failed to create IMG file: {output_img_path}", 'COL_EXPORT', 'ERROR')
            return False
        
        # Export COL data to IMG
        col_data = col_file.get_raw_data()
        if col_data:
            col_filename = os.path.basename(col_file_path)
            img_file.add_entry(col_filename, col_data)
            
            if img_file.rebuild():
                col_debug_log(main_window, f"COL exported to IMG successfully", 'COL_EXPORT', 'SUCCESS')
                return True
            else:
                col_debug_log(main_window, f"Failed to rebuild IMG after COL export", 'COL_EXPORT', 'ERROR')
                return False
        else:
            col_debug_log(main_window, f"No COL data to export", 'COL_EXPORT', 'ERROR')
            return False
            
    except Exception as e:
        col_debug_log(main_window, f"Error exporting COL to IMG: {e}", 'COL_EXPORT', 'ERROR')
        return False

def setup_col_integration_full(main_window): #vers 1
    """Main COL integration entry point with threaded loading using IMG debug system"""
    try:
        col_debug_log(main_window, "Starting full COL integration for IMG interface", 'COL_INTEGRATION')

        # Setup COL debug functionality first
        setup_col_debug_for_main_window(main_window)

        # Setup threaded loading
        setup_threaded_col_loading(main_window)

        # Add COL tools menu to existing menu bar
        if hasattr(main_window, 'menuBar') and main_window.menuBar():
            add_col_tools_menu(main_window)
            col_debug_log(main_window, "COL tools menu added", 'COL_INTEGRATION')

        # Add COL context menu items to existing entries table
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            from gui.gui_context import add_col_context_menu_to_entries_table
            add_col_context_menu_to_entries_table(main_window)
            col_debug_log(main_window, "COL context menu added to entries table", 'COL_INTEGRATION')

        # Mark integration as completed
        main_window._col_integration_active = True

        col_debug_log(main_window, "Full COL integration completed successfully", 'COL_INTEGRATION', 'SUCCESS')
        return True

    except Exception as e:
        col_debug_log(main_window, f"Full COL integration failed: {e}", 'COL_INTEGRATION', 'ERROR')
        return False

def integrate_complete_col_system(main_window): #vers 1
    """Complete COL integration setup - main entry point using IMG debug system"""
    try:
        col_debug_log(main_window, "Starting complete COL system integration", 'COL_INTEGRATION')
        
        # Check settings for initial debug state
        try:
            if hasattr(main_window, 'app_settings'):
                debug_mode = main_window.app_settings.current_settings.get('debug_mode', False)
                debug_categories = main_window.app_settings.current_settings.get('debug_categories', [])

                # Enable COL debug only if debug mode is on AND COL categories are enabled
                col_debug = debug_mode and any('COL' in cat for cat in debug_categories)
                from components.col_debug_functions import set_col_debug_enabled
                set_col_debug_enabled(col_debug)

                if col_debug:
                    col_debug_log(main_window, "COL debug enabled from settings", 'COL_INTEGRATION')
                else:
                    col_debug_log(main_window, "COL debug disabled for performance", 'COL_INTEGRATION')
            else:
                # Default to disabled for performance
                from components.col_debug_functions import set_col_debug_enabled
                set_col_debug_enabled(False)
                col_debug_log(main_window, "COL debug disabled (no settings)", 'COL_INTEGRATION')
                
        except Exception as e:
            col_debug_log(main_window, f"Error checking settings: {e}", 'COL_INTEGRATION', 'WARNING')

        # Setup full integration
        success = setup_col_integration_full(main_window)
        
        if success:
            # Add COL file detection
            add_col_file_detection(main_window)
            
            # Add show COL info function
            def show_col_info_func():
                """Show COL file information"""
                if not main_window.current_col:
                    QMessageBox.information(main_window, "COL Info", "No COL file loaded")
                    return
                
                try:
                    file_name = getattr(main_window.current_col, 'file_path', 'Unknown')
                    file_name = os.path.basename(file_name) if file_name != 'Unknown' else 'Unknown'
                    
                    model_count = len(main_window.current_col.models) if hasattr(main_window.current_col, 'models') else 0
                    
                    file_size = getattr(main_window.current_col, 'file_size', 0)
                    file_size_str = f"{file_size:,} bytes ({file_size / (1024*1024):.2f} MB)" if file_size else "Unknown"
                    
                    version = getattr(main_window.current_col, 'version', 'Unknown')
                    version_str = str(version) if version else "Unknown"
                    
                    # Get detailed statistics if available
                    stats = {}
                    if hasattr(main_window.current_col, 'get_collision_statistics'):
                        try:
                            stats = main_window.current_col.get_collision_statistics()
                        except:
                            pass
                    
                    # Build info text
                    info_text = f"COL File: {file_name}\n"
                    info_text += f"Models: {model_count}\n"
                    info_text += f"Size: {file_size_str}\n"
                    info_text += f"Version: {version_str}\n"
                    
                    if stats:
                        info_text += "\nDetailed Statistics:\n"
                        for key, value in stats.items():
                            if isinstance(value, int) and key.lower() in ['vertices', 'faces', 'spheres', 'boxes']:
                                info_text += f"- {key}: {value:,}\n"
                            else:
                                info_text += f"- {key}: {str(value)}\n"
                    
                    QMessageBox.information(main_window, "COL File Information", info_text)
                    col_debug_log(main_window, "COL info displayed successfully", 'COL_INFO', 'SUCCESS')
                    
                except Exception as e:
                    col_debug_log(main_window, f"Error showing COL info: {str(e)}", 'COL_INFO', 'ERROR')
                    QMessageBox.critical(main_window, "Error", f"Error getting COL information: {str(e)}")
            
            main_window.show_col_info = show_col_info_func
            
            col_debug_log(main_window, "Complete COL system integrated successfully", 'COL_INTEGRATION', 'SUCCESS')
            return True
        else:
            col_debug_log(main_window, "Complete COL system integration failed", 'COL_INTEGRATION', 'ERROR')
            return False
        
    except Exception as e:
        col_debug_log(main_window, f"Error integrating complete COL system: {str(e)}", 'COL_INTEGRATION', 'ERROR')
        return False

# Export main functions
__all__ = [
    'add_col_file_detection',
    'add_col_tools_menu', 
    'analyze_col_from_img',
    'create_col_editor_action',
    'create_col_file_dialog',
    'export_col_to_img_format',
    'integrate_complete_col_system',
    'setup_col_debug_for_main_window',
    'setup_col_integration_full',
    'setup_threaded_col_loading'
]
