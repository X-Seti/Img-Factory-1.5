#!/usr/bin/env python3
"""
#this belongs in root /imgfactory_col_integration.py
X-Seti - June27 2025 - COL Integration for IMG Factory 1.5
Integrates all COL functionality into the main IMG Factory interface
"""

import os
import sys
from typing import Optional, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QMessageBox, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QHeaderView, QAbstractItemView, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QShortcut, QKeySequence, QFont

# Import COL components
from components.col_core_classes import COLFile, COLModel, COLVersion
from components.col_editor import COLEditorDialog, open_col_editor
from components.col_integration import COLListWidget, COLModelDetailsWidget, load_col_from_img_entry, export_col_to_img
from components.col_utilities import open_col_batch_processor, analyze_col_file_dialog

def integrate_col_functionality(img_factory_instance):
    """
    Main function to integrate all COL functionality into IMG Factory
    """
    
    # Add COL menu to menu bar
    add_col_menu(img_factory_instance)
    
    # Add COL tab to main interface
    add_col_tab(img_factory_instance)
    
    # Add COL context menu items to IMG entries
    add_col_context_menu_items(img_factory_instance)
    
    # Add COL file type detection
    add_col_file_detection(img_factory_instance)
    
    print("COL functionality integrated successfully!")

def add_col_menu(img_factory_instance):
    """Add COL menu to the main menu bar"""
    
    menubar = img_factory_instance.menuBar()
    
    # Create COL menu
    col_menu = menubar.addMenu("🔧 COL")
    
    # File operations
    open_col_action = QAction("📂 Open COL File", img_factory_instance)
    open_col_action.setShortcut("Ctrl+Shift+O")
    open_col_action.triggered.connect(lambda: open_col_file_dialog(img_factory_instance))
    col_menu.addAction(open_col_action)
    
    new_col_action = QAction("🆕 New COL File", img_factory_instance)
    new_col_action.triggered.connect(lambda: create_new_col_file(img_factory_instance))
    col_menu.addAction(new_col_action)
    
    col_menu.addSeparator()
    
    # COL Editor
    editor_action = QAction("✏️ COL Editor", img_factory_instance)
    editor_action.setShortcut("Ctrl+E")
    editor_action.triggered.connect(lambda: open_col_editor(img_factory_instance))
    col_menu.addAction(editor_action)
    
    col_menu.addSeparator()
    
    # Batch operations
    batch_process_action = QAction("⚙️ Batch Processor", img_factory_instance)
    batch_process_action.triggered.connect(lambda: open_col_batch_processor(img_factory_instance))
    col_menu.addAction(batch_process_action)
    
    analyze_action = QAction("📊 Analyze COL", img_factory_instance)
    analyze_action.triggered.connect(lambda: analyze_col_file_dialog(img_factory_instance))
    col_menu.addAction(analyze_action)
    
    col_menu.addSeparator()
    
    # Import/Export
    import_to_img_action = QAction("📥 Import to IMG", img_factory_instance)
    import_to_img_action.triggered.connect(lambda: import_col_to_img(img_factory_instance))
    col_menu.addAction(import_to_img_action)
    
    export_from_img_action = QAction("📤 Export from IMG", img_factory_instance)
    export_from_img_action.triggered.connect(lambda: export_col_from_img(img_factory_instance))
    col_menu.addAction(export_from_img_action)
    
    # Store reference to COL menu
    img_factory_instance.col_menu = col_menu

def add_col_tab(img_factory_instance):
    """Add COL tab to the main interface"""
    
    # Check if main interface has a tab widget
    if not hasattr(img_factory_instance, 'main_tab_widget'):
        # Create tab widget if it doesn't exist
        central_widget = img_factory_instance.centralWidget()
        if central_widget:
            # Replace central widget with tab widget
            old_layout = central_widget.layout()
            
            img_factory_instance.main_tab_widget = QTabWidget()
            
            # Move existing content to first tab
            if old_layout:
                img_tab = QWidget()
                img_tab.setLayout(old_layout)
                img_factory_instance.main_tab_widget.addTab(img_tab, "📁 IMG Files")
            
            # Set new layout
            new_layout = QVBoxLayout(central_widget)
            new_layout.addWidget(img_factory_instance.main_tab_widget)
    
    # Create COL tab
    col_tab = QWidget()
    col_layout = QVBoxLayout(col_tab)
    
    # Create COL interface
    col_splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Left panel - COL file list
    col_list_widget = COLListWidget()
    col_splitter.addWidget(col_list_widget)
    
    # Right panel - COL model details
    col_details_widget = COLModelDetailsWidget()
    col_splitter.addWidget(col_details_widget)
    
    # Connect signals
    col_list_widget.col_selected.connect(col_details_widget.set_col_file)
    col_list_widget.col_double_clicked.connect(lambda col_file: open_col_editor_with_file(img_factory_instance, col_file))
    
    # Set splitter sizes
    col_splitter.setSizes([400, 300])
    
    col_layout.addWidget(col_splitter)
    
    # Add COL tab
    img_factory_instance.main_tab_widget.addTab(col_tab, "🔧 COL Files")
    
    # Store references
    img_factory_instance.col_list_widget = col_list_widget
    img_factory_instance.col_details_widget = col_details_widget

def add_col_context_menu_items(img_factory_instance):
    """Add COL-specific context menu items to IMG entries"""
    
    # Store original context menu method
    if hasattr(img_factory_instance, 'entries_table'):
        original_context_menu = getattr(img_factory_instance.entries_table, 'contextMenuEvent', None)
        
        def enhanced_context_menu(event):
            # Call original context menu first
            if original_context_menu:
                original_context_menu(event)
            
            # Get selected item
            item = img_factory_instance.entries_table.itemAt(event.pos())
            if not item:
                return
            
            row = item.row()
            if row < 0:
                return
            
            # Check if it's a COL file
            name_item = img_factory_instance.entries_table.item(row, 0)
            if not name_item:
                return
            
            filename = name_item.text()
            if not filename.lower().endswith('.col'):
                return
            
            # Create COL-specific context menu
            from PyQt6.QtWidgets import QMenu
            menu = QMenu(img_factory_instance.entries_table)
            
            # COL-specific actions
            edit_col_action = menu.addAction("✏️ Edit COL")
            edit_col_action.triggered.connect(lambda: edit_col_from_img(img_factory_instance, row))
            
            analyze_col_action = menu.addAction("📊 Analyze COL")
            analyze_col_action.triggered.connect(lambda: analyze_col_from_img(img_factory_instance, row))
            
            menu.addSeparator()
            
            export_col_action = menu.addAction("📤 Export COL")
            export_col_action.triggered.connect(lambda: export_col_entry(img_factory_instance, row))
            
            replace_col_action = menu.addAction("🔄 Replace COL")
            replace_col_action.triggered.connect(lambda: replace_col_entry(img_factory_instance, row))
            
            menu.exec(event.globalPos())
        
        # Replace context menu method
        img_factory_instance.entries_table.contextMenuEvent = enhanced_context_menu

def add_col_file_detection(img_factory_instance):
    """Add COL file type detection to IMG entries"""
    
    # Enhance the file type detection in the entries table
    if hasattr(img_factory_instance, 'populate_entries_table'):
        original_populate = img_factory_instance.populate_entries_table
        
        def enhanced_populate_entries_table():
            # Call original method
            original_populate()
            
            # Enhance COL entries
            if hasattr(img_factory_instance, 'current_img') and img_factory_instance.current_img:
                table = img_factory_instance.entries_table
                
                for row in range(table.rowCount()):
                    name_item = table.item(row, 0)
                    type_item = table.item(row, 1)
                    
                    if name_item and type_item:
                        filename = name_item.text()
                        
                        if filename.lower().endswith('.col'):
                            # Enhanced COL file info
                            try:
                                entry = img_factory_instance.current_img.entries[row]
                                col_info = detect_col_version_from_data(entry.get_data())
                                
                                if col_info:
                                    type_item.setText(f"COL v{col_info['version']}")
                                    
                                    # Add tooltip with details
                                    tooltip = f"COL Version {col_info['version']}\n"
                                    tooltip += f"Models: {col_info['models']}\n"
                                    tooltip += f"Size: {col_info['size']} bytes"
                                    name_item.setToolTip(tooltip)
                                    
                                    # Color code by version
                                    if col_info['version'] == 1:
                                        type_item.setBackground(Qt.GlobalColor.lightGray)
                                    elif col_info['version'] == 2:
                                        type_item.setBackground(Qt.GlobalColor.yellow)
                                    elif col_info['version'] == 3:
                                        type_item.setBackground(Qt.GlobalColor.lightGreen)
                                        
                            except Exception as e:
                                print(f"Error detecting COL info: {e}")
        
        # Replace the method
        img_factory_instance.populate_entries_table = enhanced_populate_entries_table

def detect_col_version_from_data(data: bytes) -> Optional[dict]:
    """Detect COL version and basic info from raw data"""
    if len(data) < 8:
        return None
    
    try:
        # Check signature
        signature = data[:4]
        version = 0
        models = 0
        
        if signature == b'COLL':
            version = 1
        elif signature == b'COL\x02':
            version = 2
        elif signature == b'COL\x03':
            version = 3
        elif signature == b'COL\x04':
            version = 4
        else:
            return None
        
        # Count models (simplified)
        offset = 0
        while offset < len(data) - 8:
            if data[offset:offset+4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                models += 1
                # Skip to next potential model
                try:
                    import struct
                    size = struct.unpack('<I', data[offset+4:offset+8])[0]
                    offset += size + 8
                except:
                    break
            else:
                break
        
        return {
            'version': version,
            'models': max(1, models),  # At least 1 model
            'size': len(data)
        }
        
    except Exception:
        return None

# COL operation functions

def open_col_file_dialog(img_factory_instance):
    """Open COL file dialog"""
    file_path, _ = QFileDialog.getOpenFileName(
        img_factory_instance, "Open COL File", "", "COL Files (*.col);;All Files (*)"
    )
    
    if file_path:
        if hasattr(img_factory_instance, 'col_list_widget'):
            img_factory_instance.col_list_widget.load_col_from_path(file_path)
            # Switch to COL tab
            if hasattr(img_factory_instance, 'main_tab_widget'):
                img_factory_instance.main_tab_widget.setCurrentIndex(1)  # COL tab
        else:
            # Fallback to standalone editor
            open_col_editor(img_factory_instance, file_path)

def create_new_col_file(img_factory_instance):
    """Create new COL file"""
    QMessageBox.information(img_factory_instance, "New COL", "New COL file creation coming soon!")

def open_col_editor_with_file(img_factory_instance, col_file: COLFile):
    """Open COL editor with specific file"""
    editor = COLEditorDialog(img_factory_instance)
    if col_file.file_path:
        editor.load_col_file(col_file.file_path)
    editor.exec()

def edit_col_from_img(img_factory_instance, row: int):
    """Edit COL file from IMG entry"""
    try:
        if not hasattr(img_factory_instance, 'current_img') or not img_factory_instance.current_img:
            return
        
        if row < 0 or row >= len(img_factory_instance.current_img.entries):
            return
        
        entry = img_factory_instance.current_img.entries[row]
        load_col_from_img_entry(entry, img_factory_instance)
        
    except Exception as e:
        QMessageBox.critical(img_factory_instance, "Error", f"Failed to edit COL: {str(e)}")

def analyze_col_from_img(img_factory_instance, row: int):
    """Analyze COL file from IMG entry"""
    try:
        if not hasattr(img_factory_instance, 'current_img') or not img_factory_instance.current_img:
            return
        
        if row < 0 or row >= len(img_factory_instance.current_img.entries):
            return
        
        entry = img_factory_instance.current_img.entries[row]
        col_data = entry.get_data()
        
        # Create temporary COL file for analysis
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name
        
        # Analyze
        from components.col_utilities import COLAnalyzer
        col_file = COLFile(temp_path)
        if col_file.load():
            analysis = COLAnalyzer.analyze_col_file(col_file)
            report = COLAnalyzer.generate_report(analysis)
            
            # Show analysis dialog
            from PyQt6.QtWidgets import QDialog, QTextEdit
            from PyQt6.QtGui import QFont
            
            dialog = QDialog(img_factory_instance)
            dialog.setWindowTitle(f"COL Analysis - {entry.name}")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(report)
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Courier", 9))
            layout.addWidget(text_edit)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec()
        
        # Clean up
        import os
        os.unlink(temp_path)
        
    except Exception as e:
        QMessageBox.critical(img_factory_instance, "Error", f"Failed to analyze COL: {str(e)}")

def export_col_entry(img_factory_instance, row: int):
    """Export COL entry from IMG"""
    try:
        if not hasattr(img_factory_instance, 'current_img') or not img_factory_instance.current_img:
            return
        
        if row < 0 or row >= len(img_factory_instance.current_img.entries):
            return
        
        entry = img_factory_instance.current_img.entries[row]
        
        # Get export path
        default_name = entry.name if entry.name.lower().endswith('.col') else entry.name + '.col'
        file_path, _ = QFileDialog.getSaveFileName(
            img_factory_instance, "Export COL File", default_name, "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            col_data = entry.get_data()
            with open(file_path, 'wb') as f:
                f.write(col_data)
            
            QMessageBox.information(img_factory_instance, "Success", f"COL exported to {file_path}")
            
    except Exception as e:
        QMessageBox.critical(img_factory_instance, "Error", f"Failed to export COL: {str(e)}")

def replace_col_entry(img_factory_instance, row: int):
    """Replace COL entry in IMG"""
    try:
        if not hasattr(img_factory_instance, 'current_img') or not img_factory_instance.current_img:
            return
        
        if row < 0 or row >= len(img_factory_instance.current_img.entries):
            return
        
        entry = img_factory_instance.current_img.entries[row]
        
        # Get replacement file
        file_path, _ = QFileDialog.getOpenFileName(
            img_factory_instance, "Replace COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            with open(file_path, 'rb') as f:
                new_data = f.read()
            
            entry.set_data(new_data)
            
            QMessageBox.information(img_factory_instance, "Success", "COL entry replaced successfully")
            
            # Refresh the entries table
            if hasattr(img_factory_instance, 'populate_entries_table'):
                img_factory_instance.populate_entries_table()
            
    except Exception as e:
        QMessageBox.critical(img_factory_instance, "Error", f"Failed to replace COL: {str(e)}")

def import_col_to_img(img_factory_instance):
    """Import COL file to current IMG"""
    try:
        if not hasattr(img_factory_instance, 'current_img') or not img_factory_instance.current_img:
            QMessageBox.warning(img_factory_instance, "No IMG", "Please open an IMG file first")
            return
        
        # Get COL file to import
        file_path, _ = QFileDialog.getOpenFileName(
            img_factory_instance, "Import COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            with open(file_path, 'rb') as f:
                col_data = f.read()
            
            entry_name = os.path.basename(file_path)
            img_factory_instance.current_img.add_entry(entry_name, col_data)
            
            QMessageBox.information(img_factory_instance, "Success", f"COL imported as {entry_name}")
            
            # Refresh the entries table
            if hasattr(img_factory_instance, 'populate_entries_table'):
                img_factory_instance.populate_entries_table()
            
    except Exception as e:
        QMessageBox.critical(img_factory_instance, "Error", f"Failed to import COL: {str(e)}")

def export_col_from_img(img_factory_instance):
    """Export COL files from current IMG"""
    try:
        if not hasattr(img_factory_instance, 'current_img') or not img_factory_instance.current_img:
            QMessageBox.warning(img_factory_instance, "No IMG", "Please open an IMG file first")
            return
        
        # Find COL entries
        col_entries = []
        for entry in img_factory_instance.current_img.entries:
            if entry.name.lower().endswith('.col'):
                col_entries.append(entry)
        
        if not col_entries:
            QMessageBox.information(img_factory_instance, "No COL Files", "No COL files found in current IMG")
            return
        
        # Get export directory
        export_dir = QFileDialog.getExistingDirectory(
            img_factory_instance, "Export COL Files"
        )
        
        if export_dir:
            exported_count = 0
            
            for entry in col_entries:
                try:
                    file_path = os.path.join(export_dir, entry.name)
                    col_data = entry.get_data()
                    
                    with open(file_path, 'wb') as f:
                        f.write(col_data)
                    
                    exported_count += 1
                    
                except Exception as e:
                    print(f"Failed to export {entry.name}: {e}")
            
            QMessageBox.information(
                img_factory_instance, "Export Complete", 
                f"Exported {exported_count} COL files to {export_dir}"
            )
            
    except Exception as e:
        QMessageBox.critical(img_factory_instance, "Error", f"Failed to export COL files: {str(e)}")

def add_col_status_info(img_factory_instance):
    """Add COL-specific status information"""
    
    # Store original status update method
    if hasattr(img_factory_instance, 'update_status_bar'):
        original_update_status = img_factory_instance.update_status_bar
        
        def enhanced_update_status_bar():
            # Call original method
            original_update_status()
            
            # Add COL-specific info
            if hasattr(img_factory_instance, 'current_img') and img_factory_instance.current_img:
                col_count = 0
                for entry in img_factory_instance.current_img.entries:
                    if entry.name.lower().endswith('.col'):
                        col_count += 1
                
                if col_count > 0:
                    current_status = img_factory_instance.statusBar().currentMessage()
                    enhanced_status = f"{current_status} | COL Files: {col_count}"
                    img_factory_instance.statusBar().showMessage(enhanced_status)
        
        # Replace the method
        img_factory_instance.update_status_bar = enhanced_update_status_bar

# Main integration function to be called from IMG Factory
def setup_col_integration(img_factory_instance):
    """Setup complete COL integration"""
    
    try:
        # Integrate all COL functionality
        integrate_col_functionality(img_factory_instance)
        
        # Add status bar enhancement
        add_col_status_info(img_factory_instance)
        
        # Add keyboard shortcuts
        add_col_shortcuts(img_factory_instance)
        
        return True
        
    except Exception as e:
        print(f"Error setting up COL integration: {e}")
        return False

def add_col_shortcuts(img_factory_instance):
    """Add keyboard shortcuts for COL operations"""
    
    from PyQt6.QtGui import QShortcut, QKeySequence
    
    # Ctrl+Shift+C for COL Editor
    col_editor_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), img_factory_instance)
    col_editor_shortcut.activated.connect(lambda: open_col_editor(img_factory_instance))
    
    # Ctrl+Shift+B for Batch Processor
    batch_shortcut = QShortcut(QKeySequence("Ctrl+Shift+B"), img_factory_instance)
    batch_shortcut.activated.connect(lambda: open_col_batch_processor(img_factory_instance))
    
    # Ctrl+Shift+A for Analyze
    analyze_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), img_factory_instance)
    analyze_shortcut.activated.connect(lambda: analyze_col_file_dialog(img_factory_instance))

# Example usage in main IMG Factory file:
"""
# Add this to your main IMG Factory __init__ method:

from imgfactory_col_integration import setup_col_integration

# After creating the main interface:
if setup_col_integration(self):
    self.log_message("COL functionality integrated successfully")
else:
    self.log_message("Failed to integrate COL functionality")
"""