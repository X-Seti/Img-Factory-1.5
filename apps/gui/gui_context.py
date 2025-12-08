#this belongs in gui/gui_context.py - Version: 9
# X-Seti - August13 2025 - IMG Factory 1.5 - Context Menu Functions - WORKING COL IMPLEMENTATION

"""
Context Menu Functions - Handles right-click context menus
UPDATED: Replace stubs with working COL functionality using existing components
"""

import sys
import os
import tempfile
import mimetypes
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QMenu, QMessageBox, QFileDialog
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut
from apps.methods.img_core_classes import format_file_size

##Methods list -
# add_col_context_menu_to_entries_table
# add_img_context_menu_to_entries_table
# analyze_col_file_dialog
# analyze_col_from_img_entry
# edit_col_collision
# edit_col_from_img_entry
# edit_dff_model
# edit_txd_textures
# enhanced_context_menu_event
# get_selected_entry_info
# open_col_batch_proc_dialog
# open_col_editor_dialog
# open_col_file_dialog
# replace_selected_entry
# show_entry_properties
# view_col_collision
# view_dff_model
# view_txd_textures



def edit_col_from_img_entry(main_window, row): #vers 2
    """Edit COL file from IMG entry - WORKING VERSION"""
    try:
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info or not entry_info['is_col']:
            main_window.log_message("❌ Selected entry is not a COL file")
            return False
        
        entry = entry_info['entry']
        main_window.log_message(f"🔧 Opening COL editor for: {entry.name}")
        
        # Use methods from col_operations
        from apps.methods.col_operations import extract_col_from_img_entry, create_temporary_col_file, cleanup_temporary_file
        
        # Extract COL data
        extraction_result = extract_col_from_img_entry(main_window, row)
        if not extraction_result:
            main_window.log_message("❌ Failed to extract COL data")
            return False
        
        col_data, entry_name = extraction_result
        
        # Create temporary COL file
        temp_path = create_temporary_col_file(col_data, entry_name)
        if not temp_path:
            main_window.log_message("❌ Failed to create temporary COL file")
            return False
        
        try:
            # Import and open COL editor
            from apps.components.Col_Editor.col_editor import COLEditorDialog
            editor = COLEditorDialog(main_window)
            
            # Load the temporary COL file
            if editor.load_col_file(temp_path):
                editor.setWindowTitle(f"COL Editor - {entry.name}")
                editor.show()  # Use show() instead of exec() for non-modal
                main_window.log_message(f"✅ COL editor opened for: {entry.name}")
                return True
            else:
                main_window.log_message("❌ Failed to load COL file in editor")
                return False
                
        finally:
            # Clean up temporary file
            cleanup_temporary_file(temp_path)
        
    except ImportError:
        QMessageBox.information(main_window, "COL Editor", 
            "COL editor component not available. Please check components.Col_Editor.col_editor.py")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error editing COL file: {str(e)}")
        QMessageBox.critical(main_window, "Error", f"Failed to edit COL file: {str(e)}")
        return False

def view_col_collision(main_window, row): #vers 2
    """View COL collision - WORKING VERSION"""
    try:
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info or not entry_info['is_col']:
            main_window.log_message("❌ Selected entry is not a COL file")
            return False
        
        entry = entry_info['entry']
        main_window.log_message(f"🔍 Viewing COL collision for: {entry.name}")
        
        # Use methods from col_operations
        from apps.methods.col_operations import extract_col_from_img_entry, get_col_basic_info
        
        # Extract COL data
        extraction_result = extract_col_from_img_entry(main_window, row)
        if not extraction_result:
            main_window.log_message("❌ Failed to extract COL data")
            return False
        
        col_data, entry_name = extraction_result
        
        # Get basic info
        basic_info = get_col_basic_info(col_data)
        
        if 'error' in basic_info:
            main_window.log_message(f"❌ COL analysis error: {basic_info['error']}")
            return False
        
        # Build info display
        info_text = f"COL File: {entry.name}\n"
        info_text += f"Size: {format_file_size(len(col_data))}\n"
        info_text += f"Version: {basic_info.get('version', 'Unknown')}\n"
        info_text += f"Models: {basic_info.get('model_count', 0)}\n"
        info_text += f"Signature: {basic_info.get('signature', b'Unknown')}\n"
        
        # Show info dialog
        from gui.col_dialogs import show_col_info_dialog
        show_col_info_dialog(main_window, info_text, f"COL Collision Info - {entry.name}")
        
        main_window.log_message(f"✅ COL collision viewed for: {entry.name}")
        return True
        
    except ImportError:
        main_window.log_message("❌ COL operations not available")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error viewing COL collision: {str(e)}")
        return False

def analyze_col_from_img_entry(main_window, row): #vers 2
    """Analyze COL file from IMG entry - WORKING VERSION"""
    try:
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info or not entry_info['is_col']:
            main_window.log_message("❌ Selected entry is not a COL file")
            return False
        
        entry = entry_info['entry']
        main_window.log_message(f"🔍 Analyzing COL file: {entry.name}")
        
        # Use methods from col_operations
        from apps.methods.col_operations import extract_col_from_img_entry, validate_col_data, create_temporary_col_file, cleanup_temporary_file, get_col_detailed_analysis
        
        # Extract COL data
        extraction_result = extract_col_from_img_entry(main_window, row)
        if not extraction_result:
            main_window.log_message("❌ Failed to extract COL data")
            return False
        
        col_data, entry_name = extraction_result
        
        # Validate COL data
        validation_result = validate_col_data(col_data)
        
        # Get detailed analysis if possible
        temp_path = create_temporary_col_file(col_data, entry_name)
        analysis_data = {}
        
        if temp_path:
            try:
                detailed_analysis = get_col_detailed_analysis(temp_path)
                if 'error' not in detailed_analysis:
                    analysis_data.update(detailed_analysis)
            finally:
                cleanup_temporary_file(temp_path)
        
        # Combine validation and analysis data
        final_analysis = {
            'size': len(col_data),
            **analysis_data,
            **validation_result
        }
        
        # Show analysis dialog
        from gui.col_dialogs import show_col_analysis_dialog
        show_col_analysis_dialog(main_window, final_analysis, entry.name)
        
        main_window.log_message(f"✅ COL analysis completed for: {entry.name}")
        return True
        
    except ImportError:
        main_window.log_message("❌ COL analysis components not available")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error analyzing COL file: {str(e)}")
        return False

def edit_col_collision(main_window, row): #vers 2
    """Edit COL collision - WORKING VERSION (alias for edit_col_from_img_entry)"""
    return edit_col_from_img_entry(main_window, row)

def open_col_editor_dialog(main_window): #vers 3
    """Open COL editor - WORKING VERSION"""
    try:
        # Try to import and open COL editor
        from apps.components.Col_Editor.col_editor import COLEditorDialog
        
        main_window.log_message("🔧 Opening COL editor...")
        editor = COLEditorDialog(main_window)
        editor.setWindowTitle("COL Editor - IMG Factory 1.5")
        
        # Show the editor
        editor.show()  # Use show() for non-modal
        main_window.log_message("✅ COL editor opened successfully")
        return True
        
    except ImportError:
        QMessageBox.information(main_window, "COL Editor", 
            "COL editor component not available.\n\nPlease ensure components.Col_Editor.col_editor.py is properly installed.")
        main_window.log_message("❌ COL editor component not found")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error opening COL editor: {str(e)}")
        QMessageBox.critical(main_window, "Error", f"Failed to open COL editor:\n{str(e)}")
        return False

def open_col_batch_proc_dialog(main_window): #vers 3
    """Open COL batch processor - WORKING VERSION"""
    try:
        # Try to import and open batch processor
        from apps.methods.col_utilities import COLBatchProcessor
        
        main_window.log_message("⚙️ Opening COL batch processor...")
        processor = COLBatchProcessor(main_window)
        processor.setWindowTitle("COL Batch Processor - IMG Factory 1.5")
        
        # Show the processor
        result = processor.exec()
        if result == 1:
            main_window.log_message("✅ COL batch processor completed")
        else:
            main_window.log_message("🔄 COL batch processor closed")
        
        return result == 1
        
    except ImportError:
        QMessageBox.information(main_window, "Batch Processor", 
            "COL batch processor component not available.\n\nPlease ensure methods.col_utilities.py is properly installed.")
        main_window.log_message("❌ COL batch processor component not found")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Error opening batch processor: {str(e)}")
        QMessageBox.critical(main_window, "Error", f"Failed to open batch processor:\n{str(e)}")
        return False

def open_col_file_dialog(main_window): #vers 3
    """Open COL file dialog - WORKING VERSION"""
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Open COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )

        if file_path:
            main_window.log_message(f"Opening COL file: {os.path.basename(file_path)}")
            
            # Check if main window has a COL loading method
            if hasattr(main_window, 'load_col_file_safely'):
                return main_window.load_col_file_safely(file_path)
            else:
                # Try to load using COL parsing functions
                try:
                    from apps.methods.populate_col_table import load_col_file_safely
                    return load_col_file_safely(main_window, file_path)
                except ImportError:
                    # Fallback: open in COL editor
                    try:
                        from apps.components.Col_Editor.col_editor import open_col_editor
                        editor = open_col_editor(main_window, file_path)
                        return editor is not None
                    except ImportError:
                        QMessageBox.warning(main_window, "COL Support", 
                            "COL file loading not available.\n\nPlease ensure COL integration is properly installed.")
                        return False
        
        return False

    except Exception as e:
        main_window.log_message(f"❌ Error opening COL file: {str(e)}")
        QMessageBox.critical(main_window, "Error", f"Failed to open COL file:\n{str(e)}")
        return False

def analyze_col_file_dialog(main_window): #vers 3
    """Analyze COL file dialog - WORKING VERSION"""
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Analyze COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )

        if file_path:
            main_window.log_message(f"🔍 Analyzing COL file: {os.path.basename(file_path)}")
            
            try:
                from apps.methods.col_operations import get_col_detailed_analysis, validate_col_data
                
                # Read file data
                with open(file_path, 'rb') as f:
                    col_data = f.read()
                
                # Get detailed analysis
                analysis_data = get_col_detailed_analysis(file_path)
                if 'error' in analysis_data:
                    QMessageBox.warning(main_window, "Analysis Error", f"Analysis failed: {analysis_data['error']}")
                    return False
                
                # Get validation data
                validation_data = validate_col_data(col_data)
                
                # Combine data
                final_analysis = {
                    'size': len(col_data),
                    **analysis_data,
                    **validation_data
                }
                
                # Show analysis dialog
                from gui.col_dialogs import show_col_analysis_dialog
                show_col_analysis_dialog(main_window, final_analysis, os.path.basename(file_path))
                
                main_window.log_message(f"✅ COL analysis completed for: {os.path.basename(file_path)}")
                return True
                
            except ImportError:
                QMessageBox.warning(main_window, "COL Analysis", 
                    "COL analysis components not available.\n\nPlease ensure COL integration is properly installed.")
                return False
        
        return False

    except Exception as e:
        main_window.log_message(f"❌ Error analyzing COL file: {str(e)}")
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL file:\n{str(e)}")
        return False

# Other file type functions (keeping existing stubs for now)
def edit_dff_model(main_window, row): #vers 1
    """Edit DFF model"""
    main_window.log_message(f"✏️ Edit DFF model from row {row} - not yet implemented")

def edit_txd_textures(main_window, row): #vers 1
    """Edit TXD textures"""
    main_window.log_message(f"🎨 Edit TXD textures from row {row} - not yet implemented")

def view_dff_model(main_window, row): #vers 1
    """View DFF model"""
    main_window.log_message(f"👁️ View DFF model from row {row} - not yet implemented")

def view_txd_textures(main_window, row): #vers 1
    """View TXD textures"""
    main_window.log_message(f"View TXD textures from row {row} - not yet implemented")

def replace_selected_entry(main_window, row): #vers 1
    """Replace selected entry"""
    main_window.log_message(f"🔄 Replace entry from row {row} - not yet implemented")

def show_entry_properties(main_window, row): #vers 1
    """Show entry properties"""
    entry_info = get_selected_entry_info(main_window, row)
    if entry_info:
        props_text = f"Entry Properties:\n\n"
        props_text += f"Name: {entry_info['name']}\n"
        props_text += f"Size: {format_file_size(entry_info['size'])}\n"
        props_text += f"Offset: 0x{entry_info['offset']:08X}\n"
        props_text += f"Type: {'COL' if entry_info['is_col'] else 'DFF' if entry_info['is_dff'] else 'TXD' if entry_info['is_txd'] else 'Other'}\n"
        
        QMessageBox.information(main_window, "Entry Properties", props_text)
        main_window.log_message(f"📋 Properties shown for: {entry_info['name']}")
    else:
        main_window.log_message(f"❌ Unable to get properties for row {row}")

# Context menu setup functions (enhanced versions)
def enhanced_context_menu_event(main_window, event): #vers 2
    """Enhanced context menu with working COL functions"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return

        table = main_window.gui_layout.table
        # Get the item at the position where the right-click occurred
        item = table.itemAt(event.pos())
        if not item:
            return

        row = item.row()
        entry_info = get_selected_entry_info(main_window, row)
        if not entry_info:
            return

        # Create context menu
        menu = QMenu(table)
        
        # Add file-type specific actions
        if entry_info['is_col']:
            # COL file actions
            view_action = QAction("🔍 View Collision", table)
            view_action.triggered.connect(lambda: view_col_collision(main_window, row))
            menu.addAction(view_action)
            
            edit_action = QAction("🔧 Edit COL File", table)
            edit_action.triggered.connect(lambda: edit_col_from_img_entry(main_window, row))
            menu.addAction(edit_action)
            
            analyze_action = QAction("📊 Analyze COL", table)
            analyze_action.triggered.connect(lambda: analyze_col_from_img_entry(main_window, row))
            menu.addAction(analyze_action)
            
            menu.addSeparator()
            
        elif entry_info['is_dff']:
            # DFF model actions
            view_action = QAction("👁️ View Model", table)
            view_action.triggered.connect(lambda: view_dff_model(main_window, row))
            menu.addAction(view_action)
            
            edit_action = QAction("✏️ Edit Model", table)
            edit_action.triggered.connect(lambda: edit_dff_model(main_window, row))
            menu.addAction(edit_action)
            
            menu.addSeparator()
            
        elif entry_info['is_txd']:
            # TXD texture actions
            view_action = QAction("View Textures", table)
            view_action.triggered.connect(lambda: view_txd_textures(main_window, row))
            menu.addAction(view_action)
            
            edit_action = QAction("🎨 Edit Textures", table)
            edit_action.triggered.connect(lambda: edit_txd_textures(main_window, row))
            menu.addAction(edit_action)
            
            menu.addSeparator()
        
        # Common actions
        props_action = QAction("📋 Properties", table)
        props_action.triggered.connect(lambda: show_entry_properties(main_window, row))
        menu.addAction(props_action)
        
        replace_action = QAction("🔄 Replace Entry", table)
        replace_action.triggered.connect(lambda: replace_selected_entry(main_window, row))
        menu.addAction(replace_action)
        
        # Show menu at the global position of the event
        menu.exec(event.globalPos())

    except Exception as e:
        main_window.log_message(f"❌ Error showing context menu: {str(e)}")

def add_col_context_menu_to_entries_table(main_window): #vers 4
    """Add enhanced COL context menu to entries table"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return False

        entries_table = main_window.gui_layout.table

        # Set up custom context menu
        entries_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        entries_table.customContextMenuRequested.connect(
            lambda pos: enhanced_context_menu_event(main_window, 
                type('MockEvent', (), {'pos': lambda: pos, 'globalPos': lambda: entries_table.mapToGlobal(pos)})())
        )

        main_window.log_message("✅ Enhanced COL context menu added to entries table")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error adding COL context menu: {str(e)}")
        return False

def add_img_context_menu_to_entries_table(main_window): #vers 5
    """Add IMG-specific context menu items to entries table"""
    # Use the enhanced COL context menu which handles all file types
    return add_col_context_menu_to_entries_table(main_window)

# Export functions
__all__ = [
    'add_col_context_menu_to_entries_table',
    'add_img_context_menu_to_entries_table', 
    'analyze_col_file_dialog',
    'analyze_col_from_img_entry',
    'edit_col_collision',
    'edit_col_from_img_entry',
    'enhanced_context_menu_event',
    'get_selected_entry_info',
    'open_col_batch_proc_dialog',
    'open_col_editor_dialog',
    'open_col_file_dialog',
    'show_entry_properties',
    'view_col_collision',
    'view_dff_model',
    'view_txd_textures',
    'edit_dff_model',
    'edit_txd_textures',
    'replace_selected_entry'
]