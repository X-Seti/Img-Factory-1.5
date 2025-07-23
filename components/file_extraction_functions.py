#this belongs in core/file_extraction_functions.py - Version: 1
# X-Seti - July23 2025 - IMG Factory 1.5 - File Extraction Functions - Complete Port
# Ported from file_extraction_functions.py-old with 100% functionality preservation
# ONLY debug system changed from old COL debug to img_debugger

"""
File Extraction Functions - COMPLETE PORT
Contains all file extraction functionality with context menus and filtering
Uses IMG debug system throughout - preserves 100% original functionality
"""

import os
import tempfile
import subprocess
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel,
    QGroupBox, QCheckBox, QSpinBox, QLineEdit, QComboBox, QApplication,
    QMenu, QAction, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Import IMG debug system - NO fallback code
from components.img_debug_functions import img_debugger

##Functions list -
# add_extraction_to_menu  
# analyze_col_from_table
# edit_col_from_table
# edit_ide_file
# extract_all_files
# extract_by_type
# extract_selected_files
# extraction_context_menu
# get_selected_entries_for_extraction
# integrate_extraction_system
# open_ide_in_text_editor
# patch_img_loading_for_extraction
# populate_with_extraction_update
# quick_extract_col_files
# quick_extract_dff_files
# quick_extract_ide_files
# quick_extract_txd_files
# setup_complete_extraction_integration
# setup_extraction_context_menu
# setup_extraction_methods
# show_dff_info
# update_extraction_filter_stats
# view_ide_definitions
# view_txd_textures

def integrate_extraction_system(main_window): #vers 1
    """Integrate complete file extraction system"""
    try:
        # Add extraction methods to main window
        setup_extraction_methods(main_window)
        
        # Setup extraction context menu
        setup_extraction_context_menu(main_window)
        
        # Add extraction to main menu
        add_extraction_to_menu(main_window)
        
        # Patch IMG loading for extraction statistics
        patch_img_loading_for_extraction(main_window)
        
        img_debugger.debug("✅ File extraction system integrated successfully")
        return True
        
    except Exception as e:
        img_debugger.error(f"❌ Failed to integrate extraction system: {str(e)}")
        return False

def setup_extraction_methods(main_window): #vers 1
    """Setup all extraction methods on main window"""
    
    def extract_selected_files():
        """Extract currently selected files"""
        try:
            entries = get_selected_entries_for_extraction(main_window)
            if not entries:
                QMessageBox.information(main_window, "No Selection", "Please select files to extract.")
                return
            
            output_dir = QFileDialog.getExistingDirectory(
                main_window, "Select Output Directory"
            )
            
            if output_dir:
                from core.file_type_filter import show_extraction_dialog
                show_extraction_dialog(main_window, entries, output_dir)
                
        except Exception as e:
            img_debugger.error(f"Extract selected files error: {str(e)}")
            QMessageBox.critical(main_window, "Error", f"Failed to extract files: {str(e)}")
    
    def extract_all_files():
        """Extract all files from current IMG"""
        try:
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG", "Please load an IMG file first.")
                return
            
            output_dir = QFileDialog.getExistingDirectory(
                main_window, "Select Output Directory"
            )
            
            if output_dir:
                entries = main_window.current_img.entries
                from core.file_type_filter import show_extraction_dialog
                show_extraction_dialog(main_window, entries, output_dir)
                
        except Exception as e:
            img_debugger.error(f"Extract all files error: {str(e)}")
            QMessageBox.critical(main_window, "Error", f"Failed to extract all files: {str(e)}")
    
    def extract_by_type(file_type: str):
        """Extract files of specific type"""
        try:
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG", "Please load an IMG file first.")
                return
            
            # Filter entries by type
            filtered_entries = []
            for entry in main_window.current_img.entries:
                entry_type = entry.name.split('.')[-1].upper() if '.' in entry.name else 'Unknown'
                if entry_type == file_type.upper():
                    filtered_entries.append(entry)
            
            if filtered_entries:
                output_dir = QFileDialog.getExistingDirectory(
                    main_window, f"Extract {file_type} Files"
                )
                if output_dir:
                    from core.file_type_filter import show_extraction_dialog
                    show_extraction_dialog(main_window, filtered_entries, output_dir)
            else:
                QMessageBox.information(main_window, "No Files", f"No {file_type} files found in current IMG.")
        
        except Exception as e:
            img_debugger.error(f"Extract by type error: {str(e)}")
    
    def quick_extract_ide_files():
        """Quick extract all IDE files"""
        extract_by_type('IDE')
    
    def quick_extract_col_files():
        """Quick extract all COL files"""
        extract_by_type('COL')
    
    def quick_extract_dff_files():
        """Quick extract all DFF files"""
        extract_by_type('DFF')
    
    def quick_extract_txd_files():
        """Quick extract all TXD files"""
        extract_by_type('TXD')
    
    def update_extraction_filter_stats():
        """Update filter statistics when IMG changes"""
        try:
            if hasattr(main_window, 'file_filter'):
                main_window.file_filter.update_filter_statistics()
        except Exception as e:
            img_debugger.warning(f"Filter stats update error: {str(e)}")
    
    # Add methods to main window
    main_window.extract_selected_files = extract_selected_files
    main_window.extract_all_files = extract_all_files
    main_window.extract_by_type = extract_by_type
    main_window.quick_extract_ide_files = quick_extract_ide_files
    main_window.quick_extract_col_files = quick_extract_col_files
    main_window.quick_extract_dff_files = quick_extract_dff_files
    main_window.quick_extract_txd_files = quick_extract_txd_files
    main_window.update_extraction_filter_stats = update_extraction_filter_stats

def setup_extraction_context_menu(main_window): #vers 1
    """Setup context menu for file extraction"""
    try:
        # Get the entries table
        entries_table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            entries_table = main_window.gui_layout.table
        elif hasattr(main_window, 'entries_table'):
            entries_table = main_window.entries_table
        
        if not entries_table:
            img_debugger.warning("Could not find entries table for extraction context menu")
            return False
        
        # Store original context menu method
        if hasattr(entries_table, 'contextMenuEvent'):
            original_context_menu = entries_table.contextMenuEvent
        else:
            original_context_menu = None
        
        def extraction_context_menu(event):
            """Enhanced context menu with extraction options"""
            try:
                menu = QMenu(entries_table)
                
                # Get current row
                row = entries_table.rowAt(event.pos().y())
                
                if row >= 0:
                    # Get file info
                    name_item = entries_table.item(row, 0)
                    if name_item:
                        filename = name_item.text().lower()
                        
                        # File-specific actions
                        if filename.endswith('.ide'):
                            edit_action = QAction("✏️ Edit IDE", entries_table)
                            edit_action.triggered.connect(lambda: edit_ide_file(main_window, row))
                            menu.addAction(edit_action)
                            
                            view_action = QAction("👁️ View Definitions", entries_table)
                            view_action.triggered.connect(lambda: view_ide_definitions(main_window, row))
                            menu.addAction(view_action)
                            
                        elif filename.endswith('.col'):
                            if hasattr(main_window, 'load_col_file_async'):
                                edit_col_action = QAction("✏️ Edit COL", entries_table)
                                edit_col_action.triggered.connect(lambda: edit_col_from_table(main_window, row))
                                menu.addAction(edit_col_action)
                            
                            analyze_col_action = QAction("🔍 Analyze COL", entries_table)
                            analyze_col_action.triggered.connect(lambda: analyze_col_from_table(main_window, row))
                            menu.addAction(analyze_col_action)
                            
                        elif filename.endswith('.dff'):
                            info_action = QAction("ℹ️ DFF Info", entries_table)
                            info_action.triggered.connect(lambda: show_dff_info(main_window, row))
                            menu.addAction(info_action)
                            
                        elif filename.endswith('.txd'):
                            view_action = QAction("🖼️ View Textures", entries_table)
                            view_action.triggered.connect(lambda: view_txd_textures(main_window, row))
                            menu.addAction(view_action)
                        
                        menu.addSeparator()
                
                # Standard extraction actions
                extract_selected_action = QAction("📤 Extract Selected", entries_table)
                extract_selected_action.triggered.connect(main_window.extract_selected_files)
                menu.addAction(extract_selected_action)
                
                extract_all_action = QAction("📦 Extract All", entries_table)
                extract_all_action.triggered.connect(main_window.extract_all_files) 
                menu.addAction(extract_all_action)
                
                # Quick extract submenu
                quick_menu = menu.addMenu("⚡ Quick Extract")
                
                quick_menu.addAction("IDE Files", main_window.quick_extract_ide_files)
                quick_menu.addAction("COL Files", main_window.quick_extract_col_files)
                quick_menu.addAction("DFF Files", main_window.quick_extract_dff_files)
                quick_menu.addAction("TXD Files", main_window.quick_extract_txd_files)
                
                # Show menu
                menu.exec(event.globalPos())
                
            except Exception as e:
                img_debugger.error(f"Context menu error: {str(e)}")
                # Fallback to original context menu if available
                if original_context_menu:
                    original_context_menu(event)
        
        # Replace context menu method
        entries_table.contextMenuEvent = extraction_context_menu
        
        img_debugger.debug("✅ Extraction context menu setup complete")
        return True
        
    except Exception as e:
        img_debugger.error(f"Failed to setup extraction context menu: {str(e)}")
        return False

def get_selected_entries_for_extraction(main_window) -> List: #vers 1
    """Get currently selected entries for extraction"""
    try:
        entries = []
        
        # Get the entries table
        table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
        elif hasattr(main_window, 'entries_table'):
            table = main_window.entries_table
        
        if not table or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return entries
        
        # Get selected rows
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())
        
        # Get corresponding entries
        for row in selected_rows:
            if row < len(main_window.current_img.entries):
                entries.append(main_window.current_img.entries[row])
        
        return entries
        
    except Exception as e:
        img_debugger.error(f"Error getting selected entries: {str(e)}")
        return []

def add_extraction_to_menu(main_window): #vers 1
    """Add extraction options to main menu"""
    try:
        if not hasattr(main_window, 'menuBar'):
            return False
        
        # Create or get Tools menu
        tools_menu = None
        for action in main_window.menuBar().actions():
            if action.text() == "Tools":
                tools_menu = action.menu()
                break
        
        if not tools_menu:
            tools_menu = main_window.menuBar().addMenu("Tools")
        
        # Add extraction submenu
        extraction_menu = tools_menu.addMenu("📤 Extract Files")
        
        # Add extraction actions
        extraction_menu.addAction("Extract Selected", main_window.extract_selected_files)
        extraction_menu.addAction("Extract All", main_window.extract_all_files)
        extraction_menu.addSeparator()
        extraction_menu.addAction("Extract IDE Files", main_window.quick_extract_ide_files)
        extraction_menu.addAction("Extract COL Files", main_window.quick_extract_col_files)
        extraction_menu.addAction("Extract DFF Files", main_window.quick_extract_dff_files)
        extraction_menu.addAction("Extract TXD Files", main_window.quick_extract_txd_files)
        
        img_debugger.debug("✅ Extraction menu added")
        return True
        
    except Exception as e:
        img_debugger.error(f"Failed to add extraction menu: {str(e)}")
        return False

def edit_col_from_table(main_window, row: int): #vers 1
    """Edit COL file from table row"""
    try:
        if row < 0 or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return
        
        if row >= len(main_window.current_img.entries):
            return
        
        from components.col_integration import edit_col_from_img_entry
        edit_col_from_img_entry(main_window, row)
        
    except Exception as e:
        img_debugger.error(f"Edit COL from table error: {str(e)}")

def analyze_col_from_table(main_window, row: int): #vers 1
    """Analyze COL file from table row"""
    try:
        if row < 0 or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return
        
        if row >= len(main_window.current_img.entries):
            return
        
        from components.col_integration import analyze_col_from_img_entry
        analyze_col_from_img_entry(main_window, row)
        
    except Exception as e:
        img_debugger.error(f"Analyze COL from table error: {str(e)}")

def edit_ide_file(main_window, row: int): #vers 1
    """Edit IDE file from table row"""
    try:
        if row < 0 or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return
        
        if row >= len(main_window.current_img.entries):
            return
        
        entry = main_window.current_img.entries[row]
        if not entry.name.lower().endswith('.ide'):
            return
        
        open_ide_in_text_editor(main_window, entry)
        
    except Exception as e:
        img_debugger.error(f"Edit IDE file error: {str(e)}")

def open_ide_in_text_editor(main_window, entry): #vers 1
    """Open IDE file in text editor"""
    try:
        # Extract to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.ide', delete=False)
        temp_file.write(entry.get_data())
        temp_file.close()
        
        # Try to open in system text editor
        try:
            if os.name == 'nt':  # Windows
                os.startfile(temp_file.name)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.call(['xdg-open', temp_file.name])
            
            img_debugger.debug(f"📝 Opened IDE file for editing: {entry.name}")
            
        except Exception as e:
            QMessageBox.warning(main_window, "Editor Error", 
                              f"Could not open text editor.\nFile extracted to: {temp_file.name}")
            img_debugger.warning(f"⚠️ Editor error for {entry.name}: {str(e)}")
            
    except Exception as e:
        img_debugger.error(f"Open IDE in text editor error: {str(e)}")

def view_ide_definitions(main_window, row: int): #vers 1
    """View IDE file definitions"""
    try:
        if row < 0 or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return
        
        if row >= len(main_window.current_img.entries):
            return
        
        entry = main_window.current_img.entries[row]
        if not entry.name.lower().endswith('.ide'):
            return
        
        # Parse IDE content
        ide_data = entry.get_data().decode('utf-8', errors='ignore')
        lines = ide_data.split('\n')
        
        definitions = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                definitions.append(line)
        
        # Show in dialog
        dialog = QDialog(main_window)
        dialog.setWindowTitle(f"IDE Definitions - {entry.name}")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        from PyQt6.QtWidgets import QTextEdit
        text_edit = QTextEdit()
        text_edit.setPlainText('\n'.join(definitions[:100]))  # Limit to first 100 lines
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
        
    except Exception as e:
        img_debugger.error(f"View IDE definitions error: {str(e)}")

def show_dff_info(main_window, row: int): #vers 1
    """Show DFF file information"""
    try:
        if row < 0 or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return
        
        if row >= len(main_window.current_img.entries):
            return
        
        entry = main_window.current_img.entries[row]
        if not entry.name.lower().endswith('.dff'):
            return
        
        # Get basic file info
        file_size = len(entry.get_data())
        
        # Try to get RW version
        rw_version = "Unknown"
        try:
            from core.rw_versions import get_rw_version_name
            data = entry.get_data()
            if len(data) >= 8:
                import struct
                version_raw = struct.unpack('<I', data[4:8])[0]
                rw_version = get_rw_version_name(version_raw)
        except:
            pass
        
        info_text = f"""DFF File Information
        
File: {entry.name}
Size: {file_size:,} bytes
RW Version: {rw_version}
Offset: {entry.offset}
"""
        
        QMessageBox.information(main_window, "DFF Info", info_text)
        
    except Exception as e:
        img_debugger.error(f"Show DFF info error: {str(e)}")

def view_txd_textures(main_window, row: int): #vers 1
    """View TXD texture information"""
    try:
        if row < 0 or not hasattr(main_window, 'current_img') or not main_window.current_img:
            return
        
        if row >= len(main_window.current_img.entries):
            return
        
        entry = main_window.current_img.entries[row]
        if not entry.name.lower().endswith('.txd'):
            return
        
        # Get basic file info
        file_size = len(entry.get_data())
        
        # Try to get RW version and texture count
        rw_version = "Unknown"
        texture_count = "Unknown"
        try:
            from core.rw_versions import get_rw_version_name
            data = entry.get_data()
            if len(data) >= 8:
                import struct
                version_raw = struct.unpack('<I', data[4:8])[0]
                rw_version = get_rw_version_name(version_raw)
                
                # Simple texture count estimation
                texture_count = str(data.count(b'TXTR'))
        except:
            pass
        
        info_text = f"""TXD File Information
        
File: {entry.name}
Size: {file_size:,} bytes
RW Version: {rw_version}
Estimated Textures: {texture_count}
Offset: {entry.offset}
"""
        
        QMessageBox.information(main_window, "TXD Info", info_text)
        
    except Exception as e:
        img_debugger.error(f"View TXD textures error: {str(e)}")

def patch_img_loading_for_extraction(main_window): #vers 1
    """Patch IMG loading to update extraction filter statistics"""
    try:
        # Store original method if it exists
        if hasattr(main_window, 'populate_entries_table'):
            original_populate = main_window.populate_entries_table
            
            def populate_with_extraction_update():
                """Enhanced populate method with extraction stats"""
                # Call original populate method
                result = original_populate()
                
                # Update extraction filter statistics
                if hasattr(main_window, 'update_extraction_filter_stats'):
                    main_window.update_extraction_filter_stats()
                
                return result
            
            main_window.populate_entries_table = populate_with_extraction_update
        
        return True
        
    except Exception as e:
        img_debugger.warning(f"⚠️ Error patching IMG loading for extraction: {str(e)}")
        return False

def update_extraction_filter_stats(main_window): #vers 1
    """Update extraction filter statistics"""
    try:
        if hasattr(main_window, 'file_filter') and hasattr(main_window.file_filter, 'update_filter_statistics'):
            main_window.file_filter.update_filter_statistics()
    except Exception as e:
        img_debugger.warning(f"Filter stats update error: {str(e)}")

def setup_complete_extraction_integration(main_window): #vers 1
    """Complete integration of extraction system"""
    try:
        # Integrate GTA file editors first
        from components.gta_file_editors import integrate_gta_file_editors
        integrate_gta_file_editors(main_window)
        
        # Integrate extraction system
        if integrate_extraction_system(main_window):
            # Patch IMG loading to update filter stats
            patch_img_loading_for_extraction(main_window)
            
            img_debugger.success("✅ Complete extraction system integration finished")
            return True
        
        return False
        
    except Exception as e:
        img_debugger.error(f"❌ Complete extraction integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'integrate_extraction_system',
    'setup_complete_extraction_integration', 
    'get_selected_entries_for_extraction',
    'setup_extraction_context_menu',
    'add_extraction_to_menu'
]