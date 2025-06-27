#!/usr/bin/env python3
"""
#this belongs in components/col_integration.py
X-Seti - June27 2025 - COL Integration for Img Factory 1.5
Integrates COL functionality into the main IMG Factory interface
"""

from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QGroupBox, QSplitter, QHeaderView,
    QAbstractItemView, QMessageBox, QFileDialog, QProgressDialog,
    QMenu, QMenuBar, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QContextMenuEvent
from col_core_classes import COLFile, COLModel, COLVersion
from col_editor import COLEditorDialog, open_col_editor

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
    """Widget for displaying COL files in the main IMG Factory interface"""
    
    col_selected = pyqtSignal(COLFile)
    col_double_clicked = pyqtSignal(COLFile)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.col_files: List[COLFile] = []
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the COL list UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Collision Files (COL)"))
        
        # COL operations buttons
        self.load_col_btn = QPushButton("📂 Load COL")
        self.load_col_btn.setProperty("action-type", "import")
        self.edit_col_btn = QPushButton("✏️ Edit COL")
        self.edit_col_btn.setProperty("action-type", "update")
        self.save_col_btn = QPushButton("💾 Save COL")
        self.save_col_btn.setProperty("action-type", "export")
        self.remove_col_btn = QPushButton("🗑️ Remove")
        self.remove_col_btn.setProperty("action-type", "remove")
        
        header_layout.addWidget(self.load_col_btn)
        header_layout.addWidget(self.edit_col_btn)
        header_layout.addWidget(self.save_col_btn)
        header_layout.addWidget(self.remove_col_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # COL table
        self.col_table = QTableWidget()
        self.col_table.setColumnCount(7)
        self.col_table.setHorizontalHeaderLabels([
            "Name", "Version", "Models", "Spheres", "Boxes", "Faces", "Size"
        ])
        
        # Configure table
        header = self.col_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.col_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.col_table.setAlternatingRowColors(True)
        self.col_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        layout.addWidget(self.col_table)
        
        # Status
        self.status_label = QLabel("No COL files loaded")
        layout.addWidget(self.status_label)
    
    def connect_signals(self):
        """Connect UI signals"""
        self.load_col_btn.clicked.connect(self.load_col_file)
        self.edit_col_btn.clicked.connect(self.edit_selected_col)
        self.save_col_btn.clicked.connect(self.save_selected_col)
        self.remove_col_btn.clicked.connect(self.remove_selected_col)
        
        self.col_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.col_table.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.col_table.customContextMenuRequested.connect(self.show_context_menu)
    
    def load_col_file(self):
        """Load COL file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_from_path(file_path)
    
    def load_col_from_path(self, file_path: str):
        """Load COL file from path"""
        # Show progress dialog
        progress = QProgressDialog("Loading COL file...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Create and start loading thread
        self.load_thread = COLFileLoadThread(file_path)
        self.load_thread.progress.connect(progress.setValue)
        self.load_thread.finished.connect(self.on_col_loaded)
        self.load_thread.error.connect(self.on_col_load_error)
        self.load_thread.finished.connect(progress.close)
        self.load_thread.error.connect(progress.close)
        self.load_thread.start()
    
    def on_col_loaded(self, col_file: COLFile):
        """Handle COL file loaded"""
        self.col_files.append(col_file)
        self.refresh_table()
        self.status_label.setText(f"Loaded: {len(self.col_files)} COL files")
    
    def on_col_load_error(self, error_msg: str):
        """Handle COL loading error"""
        QMessageBox.critical(self, "COL Load Error", error_msg)
    
    def refresh_table(self):
        """Refresh the COL table"""
        self.col_table.setRowCount(len(self.col_files))
        
        for row, col_file in enumerate(self.col_files):
            # Get file stats
            stats = col_file.get_total_stats()
            file_name = col_file.file_path.split('/')[-1] if col_file.file_path else "Unknown"
            
            # Determine version (from first model)
            version_str = "Mixed"
            if col_file.models:
                first_version = col_file.models[0].version
                if all(model.version == first_version for model in col_file.models):
                    version_str = f"Version {first_version.value}"
            
            # File size
            file_size = "Unknown"
            if col_file.file_path:
                try:
                    import os
                    size_bytes = os.path.getsize(col_file.file_path)
                    if size_bytes < 1024:
                        file_size = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        file_size = f"{size_bytes / 1024:.1f} KB"
                    else:
                        file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
                except:
                    pass
            
            # Set table items
            items = [
                QTableWidgetItem(file_name),
                QTableWidgetItem(version_str),
                QTableWidgetItem(str(stats["models"])),
                QTableWidgetItem(str(stats["spheres"])),
                QTableWidgetItem(str(stats["boxes"])),
                QTableWidgetItem(str(stats["faces"])),
                QTableWidgetItem(file_size)
            ]
            
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.col_table.setItem(row, col, item)
    
    def get_selected_col(self) -> Optional[COLFile]:
        """Get currently selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            return self.col_files[current_row]
        return None
    
    def edit_selected_col(self):
        """Edit selected COL file"""
        col_file = self.get_selected_col()
        if col_file:
            editor = COLEditorDialog(self)
            editor.load_col_file(col_file.file_path)
            editor.exec()
    
    def save_selected_col(self):
        """Save selected COL file"""
        col_file = self.get_selected_col()
        if not col_file:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            try:
                if col_file.save(file_path):
                    QMessageBox.information(self, "Success", "COL file saved successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save COL file")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving COL file: {str(e)}")
    
    def remove_selected_col(self):
        """Remove selected COL file"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            file_name = col_file.file_path.split('/')[-1] if col_file.file_path else "Unknown"
            
            reply = QMessageBox.question(
                self, "Remove COL File",
                f"Remove COL file '{file_name}' from the list?\n\n"
                f"This will not delete the file from disk.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.col_files[current_row]
                self.refresh_table()
                self.status_label.setText(f"Loaded: {len(self.col_files)} COL files")
    
    def on_selection_changed(self):
        """Handle selection change"""
        col_file = self.get_selected_col()
        if col_file:
            self.col_selected.emit(col_file)
    
    def on_item_double_clicked(self, item):
        """Handle item double click"""
        col_file = self.get_selected_col()
        if col_file:
            self.col_double_clicked.emit(col_file)
            self.edit_selected_col()
    
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
        layout.addWidget(QLabel("COL Model Details"))
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        layout.addWidget(self.model_combo)
        
        # Details table
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(2)
        self.details_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.details_table.horizontalHeader().setStretchLastSection(True)
        self.details_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.details_table)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.edit_model_btn = QPushButton("✏️ Edit Model")
        self.edit_model_btn.setProperty("action-type", "update")
        self.edit_model_btn.clicked.connect(self.edit_current_model)
        
        self.optimize_btn = QPushButton("⚡ Optimize")
        self.optimize_btn.setProperty("action-type", "update")
        self.optimize_btn.clicked.connect(self.optimize_current_model)
        
        actions_layout.addWidget(self.edit_model_btn)
        actions_layout.addWidget(self.optimize_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
    
    def set_col_file(self, col_file: COLFile):
        """Set COL file to display"""
        self.current_col_file = col_file
        self.update_model_combo()
    
    def update_model_combo(self):
        """Update model combo box"""
        self.model_combo.clear()
        
        if not self.current_col_file:
            return
        
        for i, model in enumerate(self.current_col_file.models):
            display_name = model.name if model.name else f"Model {i}"
            self.model_combo.addItem(display_name)
        
        if self.current_col_file.models:
            self.on_model_changed(0)
    
    def on_model_changed(self, index: int):
        """Handle model selection change"""
        if not self.current_col_file or index < 0 or index >= len(self.current_col_file.models):
            self.details_table.setRowCount(0)
            return
        
        model = self.current_col_file.models[index]
        self.update_details_table(model)
    
    def update_details_table(self, model: COLModel):
        """Update details table for model"""
        details = [
            ("Name", model.name or "Unnamed"),
            ("Model ID", str(model.model_id)),
            ("Version", f"COL Version {model.version.value}"),
            ("Spheres", str(len(model.spheres))),
            ("Boxes", str(len(model.boxes))),
            ("Vertices", str(len(model.vertices))),
            ("Faces", str(len(model.faces))),
            ("Face Groups", str(len(model.face_groups))),
            ("Shadow Vertices", str(len(model.shadow_vertices))),
            ("Shadow Faces", str(len(model.shadow_faces))),
            ("Flags", f"0x{model.flags:08X}"),
        ]
        
        # Add bounding box info
        if model.bounding_box:
            bb = model.bounding_box
            details.extend([
                ("Bounding Min", f"({bb.min.x:.2f}, {bb.min.y:.2f}, {bb.min.z:.2f})"),
                ("Bounding Max", f"({bb.max.x:.2f}, {bb.max.y:.2f}, {bb.max.z:.2f})"),
                ("Bounding Center", f"({bb.center.x:.2f}, {bb.center.y:.2f}, {bb.center.z:.2f})"),
                ("Bounding Radius", f"{bb.radius:.2f}"),
            ])
        
        self.details_table.setRowCount(len(details))
        
        for row, (prop, value) in enumerate(details):
            prop_item = QTableWidgetItem(prop)
            value_item = QTableWidgetItem(value)
            
            prop_item.setFlags(prop_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.details_table.setItem(row, 0, prop_item)
            self.details_table.setItem(row, 1, value_item)
    
    def edit_current_model(self):
        """Edit current model"""
        if not self.current_col_file:
            return
        
        editor = COLEditorDialog(self)
        editor.load_col_file(self.current_col_file.file_path)
        editor.exec()
    
    def optimize_current_model(self):
        """Optimize current model"""
        QMessageBox.information(self, "Optimize", "Model optimization coming soon!")

def add_col_functionality_to_imgfactory(img_factory_instance):
    """Add COL functionality to IMG Factory main window"""
    
    # Add COL menu to menu bar
    if hasattr(img_factory_instance, 'menuBar'):
        col_menu = img_factory_instance.menuBar().addMenu("COL")
        
        open_col_action = QAction("📂 Open COL File", img_factory_instance)
        open_col_action.triggered.connect(lambda: open_col_file_dialog(img_factory_instance))
        col_menu.addAction(open_col_action)
        
        edit_col_action = QAction("✏️ COL Editor", img_factory_instance)
        edit_col_action.triggered.connect(lambda: open_col_editor(img_factory_instance))
        col_menu.addAction(edit_col_action)
        
        col_menu.addSeparator()
        
        batch_convert_action = QAction("🔄 Batch Convert", img_factory_instance)
        batch_convert_action.triggered.connect(lambda: batch_convert_cols(img_factory_instance))
        col_menu.addAction(batch_convert_action)
    
    # Add COL list widget to main interface
    if hasattr(img_factory_instance, 'main_splitter'):
        col_widget = COLListWidget()
        
        # Create a new splitter for COL files
        col_splitter = QSplitter(Qt.Orientation.Vertical)
        col_splitter.addWidget(col_widget)
        
        # Add COL model details
        col_details = COLModelDetailsWidget()
        col_widget.col_selected.connect(col_details.set_col_file)
        col_splitter.addWidget(col_details)
        
        # Add to main interface
        img_factory_instance.main_splitter.addWidget(col_splitter)
        
        # Store references
        img_factory_instance.col_widget = col_widget
        img_factory_instance.col_details = col_details

def open_col_file_dialog(parent):
    """Open COL file dialog"""
    file_path, _ = QFileDialog.getOpenFileName(
        parent, "Open COL File", "", "COL Files (*.col);;All Files (*)"
    )
    
    if file_path:
        if hasattr(parent, 'col_widget'):
            parent.col_widget.load_col_from_path(file_path)
        else:
            # Fallback - open in standalone editor
            open_col_editor(parent, file_path)

def batch_convert_cols(parent):
    """Batch convert COL files"""
    QMessageBox.information(parent, "Batch Convert", "Batch COL conversion coming soon!")

def load_col_from_img_entry(img_entry, parent=None):
    """Load COL file from IMG entry"""
    try:
        # Extract COL data from IMG entry
        col_data = img_entry.get_data()
        
        # Create temporary COL file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.col', delete=False) as temp_file:
            temp_file.write(col_data)
            temp_path = temp_file.name
        
        # Open in COL editor
        editor = COLEditorDialog(parent)
        editor.load_col_file(temp_path)
        result = editor.exec()
        
        # Clean up temp file
        import os
        os.unlink(temp_path)
        
        return result
        
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load COL from IMG entry: {str(e)}")
        return False

def export_col_to_img(col_file: COLFile, img_file, entry_name: str) -> bool:
    """Export COL file to IMG entry"""
    try:
        # Build COL data
        col_data = col_file._build_col_data()
        
        # Add to IMG file
        img_file.add_entry(entry_name, col_data)
        
        return True
        
    except Exception as e:
        print(f"Error exporting COL to IMG: {e}")
        return False