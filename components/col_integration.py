#!/usr/bin/env python3
"""
#this belongs in components/col_integration.py - version 7
X-Seti - July06 2025 - COL Integration for Img Factory 1.5
Complete COL functionality integration focused on enhancing the existing IMG interface
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

# Handle imports with fallback
try:
    from components.col_core_classes import COLFile, COLModel, COLVersion
except ImportError:
    try:
        from col_core_classes import COLFile, COLModel, COLVersion
    except ImportError:
        # Fallback - create dummy classes
        class COLFile:
            def __init__(self, path=""): pass
        class COLModel: pass
        class COLVersion: pass

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
    """Widget for displaying COL files - simplified for IMG integration"""
    
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
            if col_file.file_path and os.path.exists(col_file.file_path):
                file_size = os.path.getsize(col_file.file_path)
                size_text = self.format_file_size(file_size)
            else:
                size_text = "Unknown"
            size_item = QTableWidgetItem(size_text)
            self.col_table.setItem(row, 3, size_item)
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            self.col_selected.emit(col_file)
    
    def on_double_clicked(self, item):
        """Handle double click"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            self.col_double_clicked.emit(col_file)
    
    def show_context_menu(self, position):
        """Show context menu"""
        if self.col_table.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Edit COL")
        edit_action.triggered.connect(self.edit_selected_col)
        
        save_action = menu.addAction("💾 Save As...")
        save_action.triggered.connect(self.save_selected_col)
        
        menu.addSeparator()
        
        remove_action = menu.addAction("🗑️ Remove from List")
        remove_action.triggered.connect(self.remove_selected_col)
        
        menu.exec(self.col_table.mapToGlobal(position))
    
    def edit_selected_col(self):
        """Edit selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            try:
                from components.col_editor import COLEditorDialog
                editor = COLEditorDialog(self)
                editor.load_col_file(col_file.file_path)
                editor.exec()
            except ImportError:
                QMessageBox.warning(self, "COL Editor", "COL Editor not available")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open COL editor: {str(e)}")
    
    def save_selected_col(self):
        """Save selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save COL File", "", "COL Files (*.col);;All Files (*)"
            )
            
            if file_path:
                try:
                    if hasattr(col_file, 'save') and col_file.save(file_path):
                        QMessageBox.information(self, "Success", "COL file saved successfully")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to save COL file")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error saving COL file: {str(e)}")
    
    def remove_selected_col(self):
        """Remove selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            reply = QMessageBox.question(
                self, "Remove COL File",
                "Remove COL file from the list?\n\nThis will not delete the file from disk.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.col_files[current_row]
                self.refresh_table()
                self.status_label.setText(f"Loaded: {len(self.col_files)} COL files")

class COLModelDetailsWidget(QWidget):
    """Widget for displaying COL model details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_col_file: Optional[COLFile] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the details UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🔧 COL Model Details"))
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        
        model_layout.addStretch()
        layout.addLayout(model_layout)
        
        # Details table
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(2)
        self.details_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.details_table.horizontalHeader().setStretchLastSection(True)
        self.details_table.setAlternatingRowColors(True)
        self.details_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.details_table)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Quick actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.edit_model_btn = QPushButton("✏️ Edit Model")
        self.edit_model_btn.clicked.connect(self.edit_current_model)
        
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.analyze_current_model)
        
        actions_layout.addWidget(self.edit_model_btn)
        actions_layout.addWidget(self.analyze_btn)
        actions_layout.addStretch()
        
        layout.addWidget(actions_group)
        
        # Initially disable all controls
        self.set_enabled(False)
    
    def set_enabled(self, enabled: bool):
        """Enable/disable all controls"""
        self.model_combo.setEnabled(enabled)
        self.edit_model_btn.setEnabled(enabled)
        self.analyze_btn.setEnabled(enabled)
    
    def set_col_file(self, col_file: COLFile):
        """Set COL file to display"""
        self.current_col_file = col_file
        self.update_model_combo()
        self.set_enabled(col_file is not None)
    
    def update_model_combo(self):
        """Update model combo box"""
        self.model_combo.clear()
        
        if not self.current_col_file:
            self.details_table.setRowCount(0)
            self.stats_text.clear()
            return
        
        if hasattr(self.current_col_file, 'models'):
            for i, model in enumerate(self.current_col_file.models):
                display_name = getattr(model, 'name', f"Model {i}") or f"Model {i}"
                self.model_combo.addItem(display_name)
            
            if self.current_col_file.models:
                self.on_model_changed(0)
    
    def on_model_changed(self, index: int):
        """Handle model selection change"""
        if not self.current_col_file or not hasattr(self.current_col_file, 'models'):
            self.details_table.setRowCount(0)
            self.stats_text.clear()
            return
        
        if index < 0 or index >= len(self.current_col_file.models):
            self.details_table.setRowCount(0)
            self.stats_text.clear()
            return
        
        model = self.current_col_file.models[index]
        self.update_details_table(model)
        self.update_statistics(model)
    
    def update_details_table(self, model):
        """Update details table for model"""
        details = [
            ("Name", getattr(model, 'name', 'Unknown') or "Unnamed"),
            ("Model ID", str(getattr(model, 'model_id', 'N/A'))),
            ("Version", f"COL Version {getattr(model.version, 'value', 'Unknown')}" if hasattr(model, 'version') else "Unknown"),
            ("Spheres", str(len(getattr(model, 'spheres', [])))),
            ("Boxes", str(len(getattr(model, 'boxes', [])))),
            ("Vertices", str(len(getattr(model, 'vertices', [])))),
            ("Faces", str(len(getattr(model, 'faces', [])))),
            ("Face Groups", str(len(getattr(model, 'face_groups', [])))),
            ("Shadow Vertices", str(len(getattr(model, 'shadow_vertices', [])))),
            ("Shadow Faces", str(len(getattr(model, 'shadow_faces', [])))),
        ]
        
        self.details_table.setRowCount(len(details))
        
        for row, (prop, value) in enumerate(details):
            prop_item = QTableWidgetItem(prop)
            value_item = QTableWidgetItem(value)
            
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.details_table.setItem(row, 0, prop_item)
            self.details_table.setItem(row, 1, value_item)
    
    def update_statistics(self, model):
        """Update statistics display"""
        try:
            if hasattr(model, 'get_stats'):
                stats = model.get_stats()
                stats_text = []
                
                total_elements = stats.get('total_elements', 0)
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
            from components.col_editor import COLEditorDialog
            editor = COLEditorDialog(self)
            editor.load_col_file(self.current_col_file.file_path)
            editor.exec()
        except ImportError:
            QMessageBox.warning(self, "COL Editor", "COL Editor not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open COL editor: {str(e)}")
    
    def analyze_current_model(self):
        """Analyze current model"""
        if not self.current_col_file:
            return
        
        try:
            from components.col_utilities import analyze_col_file_dialog
            analyze_col_file_dialog(self)
        except ImportError:
            QMessageBox.warning(self, "Analysis", "COL analyzer not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")

# Main Integration Functions for IMG Interface

    def setup_col_integration_full(main_window):
        """Main COL integration entry point - focused on IMG interface enhancement"""
        try:
            print("Starting COL integration for IMG interface...")

            # 1. Add COL tools menu to existing menu bar
            if hasattr(main_window, 'menuBar') and main_window.menuBar():
                add_col_tools_menu(main_window)
                print("✓ COL tools menu added")

            # 2. Add COL context menu items to existing entries table
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                add_col_context_menu_to_entries_table(main_window)
                print("✓ COL context menu added to entries table")

            # 3. Add COL keyboard shortcuts
            add_col_keyboard_shortcuts(main_window)
            print("✓ COL keyboard shortcuts added")

            main_window.log_message("✅ COL integration focused on IMG interface")
            return True

        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"Failed to analyze COL: {str(e)}")

    def extract_col_from_img_entry(main_window, row: int):
        """Extract COL file from IMG entry"""
        try:
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                return

            if row < 0 or row >= len(main_window.current_img.entries):
                return

            entry = main_window.current_img.entries[row]

            # Get save location
            file_path, _ = QFileDialog.getSaveFileName(
                main_window, "Extract COL File", entry.name, "COL Files (*.col);;All Files (*)"
            )

            if file_path:
                col_data = entry.get_data()
                with open(file_path, 'wb') as f:
                    f.write(col_data)

                QMessageBox.information(main_window, "Success", f"COL extracted to: {file_path}")
                main_window.log_message(f"Extracted COL '{entry.name}' to {file_path}")

        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"Failed to extract COL: {str(e)}")

    def replace_col_in_img_entry(main_window, row: int):
        """Replace COL file in IMG entry"""
        try:
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                return

            if row < 0 or row >= len(main_window.current_img.entries):
                return

            entry = main_window.current_img.entries[row]

            # Get replacement file
            file_path, _ = QFileDialog.getOpenFileName(
                main_window, "Replace COL File", "", "COL Files (*.col);;All Files (*)"
            )

            if file_path:
                with open(file_path, 'rb') as f:
                    new_data = f.read()

                entry.set_data(new_data)

                QMessageBox.information(main_window, "Success", "COL entry replaced successfully")
                main_window.log_message(f"Replaced COL '{entry.name}' with {file_path}")

                # Refresh the entries table if available
                if hasattr(main_window, 'populate_entries_table'):
                    main_window.populate_entries_table()

        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"Failed to replace COL: {str(e)}")

    def import_col_to_current_img(main_window):
        """Import COL file to current IMG"""
        try:
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG", "Please open an IMG file first")
                return

            # Get COL file to import
            file_path, _ = QFileDialog.getOpenFileName(
                main_window, "Import COL File", "", "COL Files (*.col);;All Files (*)"
            )

            if file_path:
                with open(file_path, 'rb') as f:
                    col_data = f.read()

                entry_name = os.path.basename(file_path)
                main_window.current_img.add_entry(entry_name, col_data)

                QMessageBox.information(main_window, "Success", f"COL imported as {entry_name}")
                main_window.log_message(f"Imported COL file: {entry_name}")

                # Refresh the entries table if available
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

            # Find all COL entries
            col_entries = [entry for entry in main_window.current_img.entries
                        if entry.name.lower().endswith('.col')]

            if not col_entries:
                QMessageBox.information(main_window, "No COL Files", "No COL files found in current IMG")
                return

            # Get output directory
            output_dir = QFileDialog.getExistingDirectory(
                main_window, "Select Output Directory for COL Files"
            )

            if output_dir:
                exported_count = 0
                for entry in col_entries:
                    try:
                        col_data = entry.get_data()
                        output_path = os.path.join(output_dir, entry.name)

                        with open(output_path, 'wb') as f:
                            f.write(col_data)

                        exported_count += 1

                    except Exception as e:
                        main_window.log_message(f"Failed to export {entry.name}: {str(e)}")

                QMessageBox.information(
                    main_window, "Export Complete",
                    f"Exported {exported_count}/{len(col_entries)} COL files to:\n{output_dir}"
                )
                main_window.log_message(f"Exported {exported_count} COL files to {output_dir}")

        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"Failed to export COL files: {str(e)}")

    # Utility Functions

    def open_col_batch_processor_safe(parent):
        """Safely open COL batch processor"""
        try:
            from components.col_utilities import open_col_batch_processor
            open_col_batch_processor(parent)
        except ImportError:
            QMessageBox.warning(parent, "COL Tools", "COL batch processor not available")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to open COL batch processor: {str(e)}")

    def analyze_col_file_safe(parent):
        """Safely open COL file analyzer"""
        try:
            from components.col_utilities import analyze_col_file_dialog
            analyze_col_file_dialog(parent)
        except ImportError:
            QMessageBox.warning(parent, "COL Tools", "COL analyzer not available")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to open COL analyzer: {str(e)}")

    def show_col_help_dialog(parent):
        """Show COL help dialog"""
        help_text = """
    <h2>🔧 COL Functionality Help</h2>

    <h3>What are COL files?</h3>
    <p>COL files contain collision data for GTA games. They define physical boundaries
    for objects in the game world.</p>

    <h3>Available Tools:</h3>
    <ul>
    <li><b>Batch Processor:</b> Process multiple COL files with optimization</li>
    <li><b>Analyzer:</b> Examine COL files for issues and statistics</li>
    <li><b>IMG Integration:</b> Import/export COL files to/from IMG archives</li>
    </ul>

    <h3>Context Menu Actions:</h3>
    <p>Right-click on .col files in IMG archives for:</p>
    <ul>
    <li><b>Edit COL File:</b> Open in COL editor for detailed editing</li>
    <li><b>Analyze COL:</b> Get detailed analysis and statistics</li>
    <li><b>Extract COL:</b> Save COL file to disk</li>
    <li><b>Replace COL:</b> Replace with a different COL file</li>
    </ul>

    <h3>Keyboard Shortcuts:</h3>
    <ul>
    <li><b>Ctrl+Shift+B:</b> Open Batch Processor</li>
    <li><b>Ctrl+Shift+A:</b> Open COL Analyzer</li>
    </ul>

    <h3>Supported COL Versions:</h3>
    <ul>
    <li>COL 1 (GTA III)</li>
    <li>COL 2 (GTA Vice City)</li>
    <li>COL 3 (GTA San Andreas)</li>
    </ul>

    <h3>Batch Processor Features:</h3>
    <ul>
    <li>Remove duplicate vertices</li>
    <li>Remove unused vertices</li>
    <li>Merge nearby vertices</li>
    <li>Convert between COL versions</li>
    <li>Fix material assignments</li>
    <li>Calculate face groups</li>
    <li>Optimize geometry</li>
    </ul>
    """

        dialog = QDialog(parent)
        dialog.setWindowTitle("COL Functionality Help")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setHtml(help_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    # Legacy Functions for Compatibility

    def load_col_from_img_entry(img_entry, parent=None):
        """Load COL file from IMG entry - legacy compatibility"""
        try:
            # Extract COL data from IMG entry
            col_data = img_entry.get_data()

            # Create temporary COL file
            with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
                temp_file.write(col_data)
                temp_path = temp_file.name

            # Open in COL editor
            try:
                from components.col_editor import COLEditorDialog
                editor = COLEditorDialog(parent)
                editor.load_col_file(temp_path)
                result = editor.exec()
            except Exception as e:
                QMessageBox.critical(parent, "Error", f"Failed to open COL editor: {str(e)}")
                result = False
            finally:
                # Clean up temp file
                os.unlink(temp_path)

            return result

        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to load COL from IMG entry: {str(e)}")
            return False

    def export_col_to_img(col_file: COLFile, img_file, entry_name: str) -> bool:
        """Export COL file to IMG entry - legacy compatibility"""
        try:
            # Build COL data
            if hasattr(col_file, '_build_col_data'):
                col_data = col_file._build_col_data()
            elif hasattr(col_file, 'save'):
                # Save to temporary file and read back
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

    def add_col_functionality_to_imgfactory(img_factory_instance):
        """Add COL functionality to IMG Factory main window - legacy compatibility"""
        return setup_col_integration_full(img_factory_instance)

    def open_col_file_dialog(parent):
        """Open COL file dialog - legacy compatibility"""
        QMessageBox.information(
            parent, "COL Integration",
            "COL files are now integrated into the IMG interface.\n\n"
            "Use Tools → COL Tools menu for COL operations."
        )

    def batch_convert_cols(parent):
        """Batch convert COL files - legacy compatibility"""
        open_col_batch_processor_safe(parent)

        # Main entry point aliases
        setup_col_integration = setup_col_integration_full
        integrate_col_functionality = setup_col_integration_full


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
            batch_action.triggered.connect(lambda: open_col_batch_processor_safe(main_window))
            col_submenu.addAction(batch_action)

            # Analyzer
            analyze_action = QAction("🔍 Analyze COL File", main_window)
            analyze_action.setStatusTip("Analyze a COL file for issues")
            analyze_action.triggered.connect(lambda: analyze_col_file_safe(main_window))
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

                # Add standard context menu items first
                if original_context_menu:
                    # Add standard actions here if needed
                    pass

                # Add COL-specific actions if this is a COL file
                if is_col_file:
                    if menu.actions():  # Add separator if menu has other actions
                        menu.addSeparator()

                    # Edit COL action
                    edit_action = menu.addAction("✏️ Edit COL File")
                    edit_action.triggered.connect(lambda: edit_col_from_img_entry(main_window, row))

                    # Analyze COL action
                    analyze_action = menu.addAction("🔍 Analyze COL")
                    analyze_action.triggered.connect(lambda: analyze_col_from_img_entry(main_window, row))

                    # Extract COL action
                    extract_action = menu.addAction("📤 Extract COL")
                    extract_action.triggered.connect(lambda: extract_col_from_img_entry(main_window, row))

                    # Replace COL action
                    replace_action = menu.addAction("🔄 Replace COL")
                    replace_action.triggered.connect(lambda: replace_col_in_img_entry(main_window, row))

                # Show menu if it has actions
                if menu.actions():
                    menu.exec(event.globalPos())

            # Replace the context menu event
            entries_table.contextMenuEvent = enhanced_context_menu_event

            return True

        except Exception as e:
            print(f"Error adding COL context menu: {e}")
            return False

    def add_col_keyboard_shortcuts(main_window):
        """Add COL keyboard shortcuts"""
        try:
            # Ctrl+Shift+B for Batch Processor
            batch_shortcut = QShortcut(QKeySequence("Ctrl+Shift+B"), main_window)
            batch_shortcut.activated.connect(lambda: open_col_batch_processor_safe(main_window))

            # Ctrl+Shift+A for Analyze
            analyze_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), main_window)
            analyze_shortcut.activated.connect(lambda: analyze_col_file_safe(main_window))

            return True

        except Exception as e:
            print(f"Error adding shortcuts: {e}")
            return False

    # COL Operations for IMG Entries

    def edit_col_from_img_entry(main_window, row: int):
        """Edit COL file from IMG entry"""
        try:
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG", "No IMG file is currently open")
                return

            if row < 0 or row >= len(main_window.current_img.entries):
                return

            entry = main_window.current_img.entries[row]

            # Extract COL data and open in editor
            col_data = entry.get_data()

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
                temp_file.write(col_data)
                temp_path = temp_file.name

            # Open editor
            try:
                from components.col_editor import COLEditorDialog
                editor = COLEditorDialog(main_window)
                editor.load_col_file(temp_path)
                result = editor.exec()

                if result == QDialog.DialogCode.Accepted:
                    main_window.log_message(f"COL file '{entry.name}' edited successfully")

            except Exception as e:
                QMessageBox.critical(main_window, "Error", f"Failed to open COL editor: {str(e)}")
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
                try:
                    from components.col_utilities import COLAnalyzer
                    col_file = COLFile(temp_path)
                    if col_file.load():
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

                except ImportError:
                    QMessageBox.information(
                        main_window, "COL Analysis",
                        f"Analysis for {entry.name} from IMG file.\n\n"
                        f"Size: {len(col_data)} bytes\n"
                        f"Use the COL Analyzer tool for detailed analysis.")

            finally:
                # Clean up temp file
                os.unlink(temp_path)

        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"Failed to edit COL: {str(e)}")
