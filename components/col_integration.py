#!/usr/bin/env python3
"""
#this belongs in components/col_integration.py - version 10
X-Seti - July07 2025 - COL Integration for Img Factory 1.5
Complete COL functionality integration - clean version without fallbacks
"""

import os
import tempfile
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QGroupBox, QSplitter, QHeaderView,
    QAbstractItemView, QMessageBox, QFileDialog, QProgressDialog,
    QMenu, QMenuBar, QCheckBox, QSpinBox, QTextEdit, QDialog,
    QFrame, QLineEdit, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QContextMenuEvent, QShortcut, QKeySequence

# Import COL components
from components.col_core_classes import COLFile, COLModel, COLVersion
from components.col_editor import COLEditorDialog, open_col_editor
from components.col_utilities import open_col_batch_processor, analyze_col_file_dialog

class COLFileLoadThread(QThread):
    """Background thread for loading COL files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # COLFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit(10)
            col_file = COLFile(self.file_path)
            
            self.progress.emit(50)
            if not col_file.load():
                self.error.emit(f"Failed to load COL file: {self.file_path}")
                return
            
            self.progress.emit(100)
            self.finished.emit(col_file)
            
        except Exception as e:
            self.error.emit(f"Error loading COL file: {str(e)}")

class COLListWidget(QWidget):
    """Widget for displaying COL files"""
    
    col_selected = pyqtSignal(COLFile)
    col_double_clicked = pyqtSignal(COLFile)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.col_files: List[COLFile] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🔧 COL Files"))
        
        # Load button
        self.load_btn = QPushButton("📂 Load COL")
        self.load_btn.clicked.connect(self.load_col_file)
        header_layout.addWidget(self.load_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # COL files table
        self.col_table = QTableWidget()
        self.col_table.setColumnCount(4)
        self.col_table.setHorizontalHeaderLabels(["Name", "Models", "Version", "Size"])
        self.col_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.col_table.setAlternatingRowColors(True)
        self.col_table.horizontalHeader().setStretchLastSection(True)
        
        # Connect signals
        self.col_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.col_table.itemDoubleClicked.connect(self.on_double_clicked)
        self.col_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.col_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.col_table)
        
        # Status
        self.status_label = QLabel("No COL files loaded")
        layout.addWidget(self.status_label)
    
    def load_col_file(self):
        """Load COL file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_from_path(file_path)
    
    def load_col_from_path(self, file_path: str):
        """Load COL file from path"""
        try:
            col_file = COLFile(file_path)
            if col_file.load():
                self.col_files.append(col_file)
                self.refresh_table()
                self.status_label.setText(f"Loaded: {len(self.col_files)} COL files")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load COL file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading COL file: {str(e)}")
    
    def refresh_table(self):
        """Refresh the COL files table"""
        self.col_table.setRowCount(len(self.col_files))
        
        for row, col_file in enumerate(self.col_files):
            # Name
            name = os.path.basename(col_file.file_path) if col_file.file_path else "Unknown"
            name_item = QTableWidgetItem(name)
            name_item.setToolTip(col_file.file_path or "No file path")
            self.col_table.setItem(row, 0, name_item)
            
            # Models count
            models_item = QTableWidgetItem(str(len(col_file.models)) if hasattr(col_file, 'models') else "0")
            self.col_table.setItem(row, 1, models_item)
            
            # Version
            version_text = "Unknown"
            if hasattr(col_file, 'models') and col_file.models:
                try:
                    version_text = f"v{col_file.models[0].version.value}"
                    if len(set(m.version for m in col_file.models)) > 1:
                        version_text += " (mixed)"
                except:
                    version_text = "Unknown"
            version_item = QTableWidgetItem(version_text)
            self.col_table.setItem(row, 2, version_item)
            
            # Size
            try:
                size = os.path.getsize(col_file.file_path) if col_file.file_path else 0
                size_text = f"{size:,} bytes"
            except:
                size_text = "Unknown"
            size_item = QTableWidgetItem(size_text)
            self.col_table.setItem(row, 3, size_item)
    
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            self.col_selected.emit(self.col_files[current_row])
    
    def on_double_clicked(self, item):
        """Handle double click"""
        row = item.row()
        if 0 <= row < len(self.col_files):
            self.col_double_clicked.emit(self.col_files[row])
    
    def show_context_menu(self, position):
        """Show context menu"""
        if self.col_table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Edit COL", self)
        edit_action.triggered.connect(self.edit_selected_col)
        menu.addAction(edit_action)
        
        analyze_action = QAction("🔍 Analyze COL", self)
        analyze_action.triggered.connect(self.analyze_selected_col)
        menu.addAction(analyze_action)
        
        menu.exec(self.col_table.mapToGlobal(position))
    
    def edit_selected_col(self):
        """Edit selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            open_col_editor(self, col_file.file_path)
    
    def analyze_selected_col(self):
        """Analyze selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            analyze_col_file_dialog(self)

class COLModelDetailsWidget(QWidget):
    """Widget for displaying COL model details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_col_file: Optional[COLFile] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        self.header_label = QLabel("📊 COL Model Details")
        self.header_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.header_label)
        
        # Model info
        info_group = QGroupBox("Model Information")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_current_model)
        actions_layout.addWidget(self.edit_btn)
        
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.analyze_current_model)
        actions_layout.addWidget(self.analyze_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_group)
        
        layout.addStretch()
    
    def set_col_file(self, col_file: COLFile):
        """Set the COL file to display"""
        self.current_col_file = col_file
        self.update_display()
    
    def update_display(self):
        """Update the display"""
        if not self.current_col_file:
            self.info_text.setPlainText("No COL file selected")
            self.stats_text.setPlainText("No statistics available")
            self.edit_btn.setEnabled(False)
            self.analyze_btn.setEnabled(False)
            return
        
        self.edit_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        
        # Update info
        try:
            info_lines = []
            info_lines.append(f"File: {os.path.basename(self.current_col_file.file_path)}")
            
            if hasattr(self.current_col_file, 'models'):
                info_lines.append(f"Models: {len(self.current_col_file.models)}")
                
                if self.current_col_file.models:
                    versions = set(m.version for m in self.current_col_file.models)
                    if len(versions) == 1:
                        info_lines.append(f"Version: {list(versions)[0].value}")
                    else:
                        info_lines.append(f"Versions: {', '.join(str(v.value) for v in versions)}")
            
            self.info_text.setPlainText("\n".join(info_lines))
        except Exception as e:
            self.info_text.setPlainText(f"Error loading info: {str(e)}")
        
        # Update statistics
        try:
            if hasattr(self.current_col_file, 'get_total_stats'):
                stats = self.current_col_file.get_total_stats()
                stats_text = []
                
                for key, value in stats.items():
                    stats_text.append(f"{key.title()}: {value}")
                
                # Calculate additional statistics
                total_elements = stats.get('spheres', 0) + stats.get('boxes', 0) + stats.get('meshes', 0)
                stats_text.append(f"Total Elements: {total_elements}")
                
                if stats.get('vertices', 0) > 0 and stats.get('faces', 0) > 0:
                    vertex_face_ratio = stats['vertices'] / stats['faces']
                    stats_text.append(f"Vertex/Face Ratio: {vertex_face_ratio:.2f}")
                
                if total_elements > 0:
                    complexity = "Low" if total_elements < 100 else "Medium" if total_elements < 500 else "High"
                    stats_text.append(f"Complexity: {complexity}")
                
                self.stats_text.setPlainText("\n".join(stats_text))
            else:
                self.stats_text.setPlainText("Statistics not available")
        except Exception as e:
            self.stats_text.setPlainText(f"Error loading statistics: {str(e)}")
    
    def edit_current_model(self):
        """Edit current model"""
        if not self.current_col_file:
            return
        
        try:
            editor = COLEditorDialog(self)
            editor.load_col_file(self.current_col_file.file_path)
            editor.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open COL editor: {str(e)}")
    
    def analyze_current_model(self):
        """Analyze current model"""
        if not self.current_col_file:
            return
        
        try:
            analyze_col_file_dialog(self)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")

# Main Integration Functions

def setup_col_integration_full(main_window):
    """Main COL integration entry point"""
    try:
        print("Starting COL integration for IMG interface...")

        # Add COL tools menu to existing menu bar
        if hasattr(main_window, 'menuBar') and main_window.menuBar():
            add_col_tools_menu(main_window)
            print("✓ COL tools menu added")

        # Add COL context menu items to existing entries table
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            add_col_context_menu_to_entries_table(main_window)
            print("✓ COL context menu added to entries table")

        # Mark integration as completed
        main_window._col_integration_active = True
        
        print("✅ COL integration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ COL integration failed: {e}")
        return False

def add_col_tools_menu(main_window):
    """Add COL tools menu to main window"""
    try:
        menubar = main_window.menuBar()
        
        # Find Tools menu or create it
        tools_menu = None
        for action in menubar.actions():
            if action.text() == "Tools":
                tools_menu = action.menu()
                break
        
        if not tools_menu:
            tools_menu = menubar.addMenu("Tools")
        
        # Add COL submenu
        col_submenu = tools_menu.addMenu("🔧 COL Tools")
        
        # Batch processor
        batch_action = QAction("📦 Batch Processor", main_window)
        batch_action.setStatusTip("Process multiple COL files at once")
        batch_action.triggered.connect(lambda: open_col_batch_processor(main_window))
        col_submenu.addAction(batch_action)
        
        # Analyzer
        analyze_action = QAction("🔍 Analyze COL File", main_window)
        analyze_action.setStatusTip("Analyze a COL file for issues")
        analyze_action.triggered.connect(lambda: analyze_col_file_dialog(main_window))
        col_submenu.addAction(analyze_action)
        
        col_submenu.addSeparator()
        
        # IMG integration tools
        import_col_action = QAction("📥 Import COL to IMG", main_window)
        import_col_action.triggered.connect(lambda: import_col_to_current_img(main_window))
        col_submenu.addAction(import_col_action)
        
        export_all_action = QAction("📤 Export All COL from IMG", main_window)
        export_all_action.triggered.connect(lambda: export_all_col_from_img(main_window))
        col_submenu.addAction(export_all_action)
        
        col_submenu.addSeparator()
        
        # Help
        help_action = QAction("❓ COL Help", main_window)
        help_action.triggered.connect(lambda: show_col_help_dialog(main_window))
        col_submenu.addAction(help_action)
        
        return True
        
    except Exception as e:
        print(f"Error adding COL tools menu: {e}")
        return False

def add_col_context_menu_to_entries_table(main_window):
    """Add COL context menu items to the existing IMG entries table"""
    try:
        entries_table = main_window.gui_layout.table
        
        # Store original context menu method
        original_context_menu = getattr(entries_table, 'contextMenuEvent', None)
        
        def enhanced_context_menu_event(event):
            # Get the item under cursor
            item = entries_table.itemAt(event.pos())
            if not item:
                return
            
            row = item.row()
            if row < 0:
                return
            
            # Get entry name from first column
            name_item = entries_table.item(row, 0)
            if not name_item:
                return
            
            entry_name = name_item.text()
            is_col_file = entry_name.lower().endswith('.col')
            
            # Create context menu
            menu = QMenu(entries_table)
            
            # Add COL-specific actions if this is a COL file
            if is_col_file:
                # Edit COL
                edit_action = QAction("✏️ Edit COL", entries_table)
                edit_action.triggered.connect(lambda: edit_col_from_img_entry(main_window, row))
                menu.addAction(edit_action)
                
                # Analyze COL
                analyze_action = QAction("🔍 Analyze COL", entries_table)
                analyze_action.triggered.connect(lambda: analyze_col_from_img_entry(main_window, row))
                menu.addAction(analyze_action)
                
                menu.addSeparator()
            
            # Add standard actions
            export_action = QAction("📤 Export", entries_table)
            export_action.triggered.connect(lambda: main_window.export_selected())
            menu.addAction(export_action)
            
            remove_action = QAction("🗑️ Remove", entries_table)
            remove_action.triggered.connect(lambda: main_window.remove_selected())
            menu.addAction(remove_action)
            
            # Show menu
            if menu.actions():
                menu.exec(event.globalPos())
        
        # Replace the context menu event
        entries_table.contextMenuEvent = enhanced_context_menu_event
        
        return True
        
    except Exception as e:
        print(f"Error adding COL context menu: {e}")
        return False

# COL Operations

def import_col_to_current_img(main_window):
    """Import COL file to current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "Please open an IMG file first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            main_window, "Import COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            with open(file_path, 'rb') as f:
                col_data = f.read()
            
            entry_name = os.path.basename(file_path)
            main_window.current_img.add_entry(entry_name, col_data)
            
            QMessageBox.information(main_window, "Success", f"COL imported as {entry_name}")
            
            # Refresh the entries table
            if hasattr(main_window, 'populate_entries_table'):
                main_window.populate_entries_table()
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to import COL: {str(e)}")

def export_all_col_from_img(main_window):
    """Export all COL files from current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "Please open an IMG file first")
            return
        
        # Find COL entries
        col_entries = [entry for entry in main_window.current_img.entries 
                      if entry.name.lower().endswith('.col')]
        
        if not col_entries:
            QMessageBox.information(main_window, "No COL Files", "No COL files found in current IMG")
            return
        
        # Select output directory
        output_dir = QFileDialog.getExistingDirectory(main_window, "Select Output Directory")
        if not output_dir:
            return
        
        # Export each COL file
        exported_count = 0
        for entry in col_entries:
            try:
                col_data = entry.get_data()
                output_path = os.path.join(output_dir, entry.name)
                
                with open(output_path, 'wb') as f:
                    f.write(col_data)
                
                exported_count += 1
                main_window.log_message(f"Exported: {entry.name}")
                
            except Exception as e:
                main_window.log_message(f"Failed to export {entry.name}: {str(e)}")
        
        QMessageBox.information(
            main_window, "Export Complete",
            f"Exported {exported_count}/{len(col_entries)} COL files to:\n{output_dir}"
        )
        main_window.log_message(f"Exported {exported_count} COL files to {output_dir}")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to export COL files: {str(e)}")

def edit_col_from_img_entry(main_window, row: int):
    """Edit COL file from IMG entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "No IMG file is currently open")
            return

        if row < 0 or row >= len(main_window.current_img.entries):
            return

        entry = main_window.current_img.entries[row]
        col_data = entry.get_data()

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name

        # Open editor
        try:
            editor = COLEditorDialog(main_window)
            editor.load_col_file(temp_path)
            result = editor.exec()

            if result == QDialog.DialogCode.Accepted:
                main_window.log_message(f"COL file '{entry.name}' edited successfully")

        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to edit COL: {str(e)}")

def analyze_col_from_img_entry(main_window, row: int):
    """Analyze COL file from IMG entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return

        if row < 0 or row >= len(main_window.current_img.entries):
            return

        entry = main_window.current_img.entries[row]
        col_data = entry.get_data()

        # Create temporary COL file for analysis
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name

        try:
            # Analyze using COL utilities
            col_file = COLFile(temp_path)
            if col_file.load():
                from components.col_utilities import COLAnalyzer
                analysis = COLAnalyzer.analyze_col_file(col_file)
                report = COLAnalyzer.generate_report(analysis)

                # Show analysis dialog
                dialog = QDialog(main_window)
                dialog.setWindowTitle(f"COL Analysis - {entry.name}")
                dialog.setMinimumSize(600, 400)

                layout = QVBoxLayout(dialog)

                text_edit = QTextEdit()
                text_edit.setPlainText(report)
                text_edit.setReadOnly(True)
                layout.addWidget(text_edit)

                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.close)
                layout.addWidget(close_btn)

                dialog.exec()
            else:
                QMessageBox.warning(main_window, "Error", "Failed to load COL data for analysis")

        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL: {str(e)}")

def show_col_help_dialog(parent):
    """Show COL help dialog"""
    help_text = """
<h2>🔧 COL Functionality Help</h2>

<h3>What are COL files?</h3>
<p>COL files contain collision data for GTA games. They define invisible boundaries that prevent players and vehicles from passing through solid objects.</p>

<h3>Available Operations:</h3>
<ul>
<li><b>📦 Batch Processor</b> - Process multiple COL files at once</li>
<li><b>🔍 Analyze COL File</b> - Analyze collision geometry for issues</li>
<li><b>📥 Import COL to IMG</b> - Add COL files to IMG archives</li>
<li><b>📤 Export All COL from IMG</b> - Extract all COL files from IMG</li>
</ul>

<h3>Context Menu (Right-click COL entries):</h3>
<ul>
<li><b>✏️ Edit COL</b> - Open COL file in editor</li>
<li><b>🔍 Analyze COL</b> - Analyze individual COL from IMG</li>
</ul>

<h3>Supported Operations:</h3>
<ul>
<li>Loading and viewing COL files</li>
<li>Extracting COL data from IMG archives</li>
<li>Basic collision analysis</li>
<li>Batch processing workflows</li>
</ul>
    """
    
    dialog = QDialog(parent)
    dialog.setWindowTitle("COL Help")
    dialog.setMinimumSize(500, 400)
    
    layout = QVBoxLayout(dialog)
    
    text_edit = QTextEdit()
    text_edit.setHtml(help_text)
    text_edit.setReadOnly(True)
    layout.addWidget(text_edit)
    
    close_btn = QPushButton("Close")
    close_btn.clicked.connect(dialog.accept)
    layout.addWidget(close_btn)
    
    dialog.exec()

# Legacy compatibility functions
def load_col_from_img_entry(img_entry, parent=None):
    """Load COL file from IMG entry"""
    try:
        col_data = img_entry.get_data()
        
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name
        
        try:
            editor = COLEditorDialog(parent)
            editor.load_col_file(temp_path)
            result = editor.exec()
        finally:
            os.unlink(temp_path)
        
        return result
        
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load COL from IMG entry: {str(e)}")
        return False

def export_col_to_img(col_file: COLFile, img_file, entry_name: str) -> bool:
    """Export COL file to IMG entry"""
    try:
        if hasattr(col_file, '_build_col_data'):
            col_data = col_file._build_col_data()
        elif hasattr(col_file, 'save'):
            with tempfile.NamedTemporaryFile(suffix='.col') as temp_file:
                if col_file.save(temp_file.name):
                    with open(temp_file.name, 'rb') as f:
                        col_data = f.read()
                else:
                    return False
        else:
            return False

        # Add to IMG file
        if hasattr(img_file, 'add_entry'):
            img_file.add_entry(entry_name, col_data)
            return True
        else:
            return False

    except Exception as e:
        print(f"Error exporting COL to IMG: {e}")
        return False
