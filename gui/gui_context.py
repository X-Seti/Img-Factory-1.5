# #this belongs in gui/ gui_context.py - Version: 8
# X-Seti - July16 2025 - IMG Factory 1.5 - Context Menu Functions

"""
Context Menu Functions - Handles right-click context menus
"""
import sys
import os
import mimetypes
from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut
from components.img_core_classes import format_file_size

#print(f"[DEBUG] gui_context calling: with args={Path}")

## Methods list
# add_col_context_menu_to_entries_table
# add_img_context_menu_to_entries_table
# analyze_col_file_dialog
# analyze_col_from_img_entry
# edit_col_collision
# edit_col_from_img_entry
# edit_dff_model
# edit_txd_textures
# replace_selected_entry
# open_col_batch_proc_dialog
# open_col_editor_dialog
# open_col_file_dialog
# show_entry_properties
# view_col_collision
# view_txd_textures
# view_dff_model


def add_col_context_menu_to_entries_table(main_window): #vers 4
    """Add COL context menu to entries table - FIXED"""
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

        main_window.log_message("✅ COL context menu added to entries table")
        return True

    except Exception as e:
        main_window.log_message(f"❌ Error adding COL context menu: {str(e)}")
        return False


def add_img_context_menu_to_entries_table(main_window): #vers 5
    """Add IMG-specific context menu items to entries table"""
    try:
        if not hasattr(main_window.gui_layout, 'table'):
            return False
        
        entries_table = main_window.gui_layout.table
        
        def img_context_menu_event(event: QContextMenuEvent):
            """IMG context menu with standard operations"""
            # Get selected row
            item = entries_table.itemAt(event.pos())
            if not item:
                return
            
            row = item.row()
            
            # Create context menu
            menu = QMenu(entries_table)
            
            # Get entry info
            try:
                name_item = entries_table.item(row, 0)
                if name_item:
                    entry_name = name_item.text().lower()
                    
                    # Add file-type specific actions
                    if entry_name.endswith('.dff'):
                        # DFF model actions
                        view_action = QAction("👁️ View Model", entries_table)
                        view_action.triggered.connect(lambda: view_dff_model(main_window, row))
                        menu.addAction(view_action)
                        
                        edit_action = QAction("✏️ Edit Model", entries_table)
                        edit_action.triggered.connect(lambda: edit_dff_model(main_window, row))
                        menu.addAction(edit_action)
                        
                        menu.addSeparator()
                        
                    elif entry_name.endswith('.txd'):
                        # TXD texture actions
                        view_action = QAction("🖼️ View Textures", entries_table)
                        view_action.triggered.connect(lambda: view_txd_textures(main_window, row))
                        menu.addAction(view_action)
                        
                        edit_action = QAction("🎨 Edit Textures", entries_table)
                        edit_action.triggered.connect(lambda: edit_txd_textures(main_window, row))
                        menu.addAction(edit_action)
                        
                        menu.addSeparator()
                        
                    elif entry_name.endswith('.col'):
                        # COL collision actions
                        view_action = QAction("🔍 View Collision", entries_table)
                        view_action.triggered.connect(lambda: view_col_collision(main_window, row))
                        menu.addAction(view_action)
                        
                        edit_action = QAction("✏️ Edit Collision", entries_table)
                        edit_action.triggered.connect(lambda: edit_col_collision(main_window, row))
                        menu.addAction(edit_action)
                        
                        menu.addSeparator()
            except:
                pass
            
            # Standard actions for all files
            export_action = QAction("📤 Export", entries_table)
            export_action.triggered.connect(lambda: main_window.export_selected())
            menu.addAction(export_action)
            
            replace_action = QAction("🔄 Replace", entries_table)
            replace_action.triggered.connect(lambda: replace_selected_entry(main_window, row))
            menu.addAction(replace_action)
            
            menu.addSeparator()
            
            remove_action = QAction("🗑️ Remove", entries_table)
            remove_action.triggered.connect(lambda: main_window.remove_selected())
            menu.addAction(remove_action)
            
            # Properties
            properties_action = QAction("📋 Properties", entries_table)
            properties_action.triggered.connect(lambda: show_entry_properties(main_window, row))
            menu.addAction(properties_action)
            
            # Show menu
            menu.exec(event.globalPos())
        
        # Set the context menu handler
        entries_table.contextMenuEvent = img_context_menu_event
        
        main_window.log_message("✅ IMG context menu added to entries table")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error adding IMG context menu: {str(e)}")
        return False


def analyze_col_file_dialog(main_window): #vers 4
    """Show COL file analysis dialog"""
    try:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os

        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Analyze COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )

        if file_path:
            # Parse and analyze the file
            try:
                from components.col_parsing_functions import COLParser
                parser = COLParser(debug=False)
                models = parser.parse_col_file_structure(file_path)

                # Create analysis report
                analysis = []
                analysis.append("COL File Analysis Report")
                analysis.append("=" * 30)
                analysis.append(f"File: {os.path.basename(file_path)}")
                analysis.append(f"Size: {os.path.getsize(file_path):,} bytes")
                analysis.append(f"Models Found: {len(models)}")

                total_elements = 0
                for i, model in enumerate(models):
                    analysis.append(f"\nModel {i+1}:")
                    analysis.append(f"  Name: {model.get('name', 'Unknown')}")
                    analysis.append(f"  Version: {model.get('version', 'Unknown')}")
                    analysis.append(f"  Size: {model.get('size', 0):,} bytes")
                    analysis.append(f"  Elements: {model.get('total_elements', 0)}")
                    total_elements += model.get('total_elements', 0)

                analysis.append(f"\nTotal Elements: {total_elements}")

                # Show analysis
                QMessageBox.information(main_window, "COL Analysis", "\n".join(analysis))

            except ImportError:
                QMessageBox.information(main_window, "COL Analysis",
                    "COL analysis will be available in a future version.")

    except Exception as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL file: {str(e)}")


def analyze_col_from_img_entry(main_window, row): #vers 1
    """Analyze COL file from IMG entry"""
    main_window.log_message(f"🔍 Analyze COL from row {row} - not yet implemented")


def edit_col_collision(main_window, row): #vers 1
    """Edit COL collision"""
    main_window.log_message(f"✏️ Edit COL collision from row {row} - not yet implemented")

# Placeholder functions for file operations (to be implemented)
def edit_col_from_img_entry(main_window, row): #vers 1
    """Edit COL file from IMG entry"""
    main_window.log_message(f"🔧 Edit COL from row {row} - not yet implemented")


def edit_dff_model(main_window, row): #vers 1
    """Edit DFF model"""
    main_window.log_message(f"✏️ Edit DFF model from row {row} - not yet implemented")


def edit_txd_textures(main_window, row): #vers 1
    """Edit TXD textures"""
    main_window.log_message(f"🎨 Edit TXD textures from row {row} - not yet implemented")



def replace_selected_entry(main_window, row): #vers 1
    """Replace selected entry"""
    main_window.log_message(f"🔄 Replace entry from row {row} - not yet implemented")


def open_col_batch_proc_dialog(main_window): #vers 2
    """Open COL batch processor"""
    try:
        # Try to open batch processor if available
        try:
            from components.col_utilities import COLBatchProcessor
            processor = COLBatchProcessor(main_window)
            processor.exec()
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "Batch Processor", 
                "COL batch processor will be available in a future version.")
                
    except Exception as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Error", f"Failed to open batch processor: {str(e)}")


def open_col_editor_dialog(main_window): #vers 2
    """Open COL editor"""
    try:
        # Try to open COL editor if available
        try:
            from components.col_editor import COLEditorDialog
            editor = COLEditorDialog(main_window)
            editor.exec()
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(main_window, "COL Editor", 
                "COL editor will be available in a future version.")
                
    except Exception as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Error", f"Failed to open COL editor: {str(e)}")


def open_col_file_dialog(main_window): #vers 2
    """Open COL file dialog"""
    try:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Open COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )

        if file_path:
            main_window.load_col_file(file_path)

    except Exception as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Error", f"Failed to open COL file: {str(e)}")

"""
def open_col_file_dialog(self): #vers 1
    #Open COL file dialog
    try:
        if hasattr(self, 'load_col_file_safely'):
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
            )

            if file_path:
                return self.handle_col_file_open(file_path)
        else:
            QMessageBox.warning(self, "COL Support", "COL integration not available")

        return False

    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to open COL file: {str(e)}")
        return False
"""

def show_entry_properties(main_window, row): #vers 1
    """Show entry properties"""
    main_window.log_message(f"📋 Show properties for row {row} - not yet implemented")


def view_col_collision(main_window, row): #vers 1
    """View COL collision"""
    main_window.log_message(f"🔍 View COL collision from row {row} - not yet implemented")


def view_dff_model(main_window, row): #vers 1
    """View DFF model"""
    main_window.log_message(f"👁️ View DFF model from row {row} - not yet implemented")


def view_txd_textures(main_window, row): #vers 1
    """View TXD textures"""
    main_window.log_message(f"🖼️ View TXD textures from row {row} - not yet implemented")


# Export functions
__all__ = [
    'add_col_context_menu_to_entries_table',
    'add_img_context_menu_to_entries_table',
    'analyze_col_file_dialog',
    'open_col_batch_proc_dialog',
    'open_col_editor_dialog',
    'open_col_file_dialog'
]
