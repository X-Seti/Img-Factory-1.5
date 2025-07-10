#!/usr/bin/env python3
"""
#this belongs in components/col_integration.py - version 11
# X-Seti - July10 2025 - Img Factory 1.5
# Complete COL functionality integration - Updated with threaded loading
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
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QAction, QIcon, QContextMenuEvent, QShortcut, QKeySequence

# Import COL components
from components.col_core_classes import COLFile, COLModel, COLVersion
from components.col_editor import COLEditorDialog, open_col_editor
from components.col_utilities import open_col_batch_processor, analyze_col_file_dialog
from components.col_debug_settings import col_debug_log, is_col_debug_enabled, setup_col_debug_for_main_window
from components.col_robust_parser import patch_col_parsing_for_robustness, estimate_gtasa_model, format_parsing_result

# =======================
# THREADED LOADING SYSTEM  
# =======================

class COLBackgroundLoader(QThread):
    """Background thread for loading COL files without freezing UI"""
    
    # Signals for UI updates
    progress_update = pyqtSignal(int, str)  # progress %, status text
    model_loaded = pyqtSignal(int, str)     # model count, model name
    load_complete = pyqtSignal(object)      # COLFile object
    load_error = pyqtSignal(str)            # error message
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.should_cancel = False
        self.col_file = None
        
    def cancel_load(self):
        """Cancel the loading operation"""
        self.should_cancel = True
        
    def run(self):
        """Run the background loading process"""
        try:
            col_debug_log(self.parent(), "Starting background COL loading", 'COL_THREADING')
            
            self.progress_update.emit(0, "Initializing COL loader...")
            QApplication.processEvents()
            
            # Check file exists
            if not os.path.exists(self.file_path):
                col_debug_log(self.parent(), f"File not found: {self.file_path}", 'COL_LOADING', 'ERROR')
                self.load_error.emit(f"File not found: {self.file_path}")
                return
                
            file_size = os.path.getsize(self.file_path)
            col_debug_log(self.parent(), f"Loading COL file: {file_size:,} bytes", 'COL_LOADING')
            self.progress_update.emit(5, f"Loading COL file ({file_size:,} bytes)...")
            
            # Create COL file object
            self.col_file = COLFile(self.file_path)
            
            self.progress_update.emit(10, "Reading COL header...")
            col_debug_log(self.parent(), "Created COL file object, starting parse", 'COL_PARSING')
            
            # Start the actual loading with progress monitoring
            if not self._load_with_progress():
                col_debug_log(self.parent(), "COL loading failed", 'COL_LOADING', 'ERROR')
                self.load_error.emit("Failed to load COL file - see log for details")
                return
                
            col_debug_log(self.parent(), "COL loading completed successfully", 'COL_LOADING')
            self.progress_update.emit(100, "COL loading complete")
            self.load_complete.emit(self.col_file)
            
        except Exception as e:
            col_debug_log(self.parent(), f"COL loading exception: {str(e)}", 'COL_LOADING', 'ERROR')
            self.load_error.emit(f"COL loading error: {str(e)}")
    
    def _load_with_progress(self) -> bool:
        """Load COL file with progress updates"""
        try:
            # Hook into the COL loading process
            original_load = self.col_file.load
            
            def progress_load():
                # Start loading
                self.progress_update.emit(20, "Parsing COL data...")
                
                # Let UI update
                self.msleep(10)
                if self.should_cancel:
                    return False
                
                # Call original load method
                result = original_load()
                
                if result and hasattr(self.col_file, 'models'):
                    # Report model loading progress
                    model_count = len(self.col_file.models)
                    self.progress_update.emit(80, f"Loaded {model_count} collision models")
                    
                    # Process each model for UI feedback
                    for i, model in enumerate(self.col_file.models):
                        if self.should_cancel:
                            return False
                            
                        progress = 80 + int((i / model_count) * 15)
                        model_name = getattr(model, 'name', f'Model {i+1}')
                        self.progress_update.emit(progress, f"Processing {model_name}...")
                        self.model_loaded.emit(i+1, model_name)
                        
                        # Small delay to prevent UI lockup
                        self.msleep(5)
                
                return result
            
            # Replace the load method temporarily
            self.col_file.load = progress_load
            return self.col_file.load()
            
        except Exception as e:
            self.progress_update.emit(0, f"Loading error: {str(e)}")
            return False

def load_col_file_async(main_window, file_path: str):
    """Load COL file asynchronously with progress feedback"""
    
    # Create progress dialog
    if hasattr(main_window.gui_layout, 'show_progress'):
        main_window.gui_layout.show_progress(0, "Loading COL file...")
    
    # Create background loader
    loader = COLBackgroundLoader(file_path, main_window)
    
    # Connect signals
    def on_progress(progress, status):
        """Update progress display"""
        if hasattr(main_window.gui_layout, 'update_progress'):
            main_window.gui_layout.update_progress(progress, status)
        main_window.log_message(f"COL Load: {status}")
    
    def on_model_loaded(count, name):
        """Report model loading"""
        main_window.log_message(f"📦 Loaded model {count}: {name}")
    
    def on_load_complete(col_file):
        """Handle successful load completion"""
        try:
            # Hide progress
            if hasattr(main_window.gui_layout, 'hide_progress'):
                main_window.gui_layout.hide_progress()
            
            # Update main window with loaded COL
            main_window.current_col = col_file
            
            # Populate table with COL data
            try:
                from components.col_tab_integration import populate_table_with_col_data_debug
                populate_table_with_col_data_debug(main_window, col_file)
            except ImportError:
                # Fallback to local population function
                populate_col_table_fallback(main_window, col_file)
            
            # Update info bar
            try:
                from components.col_tab_integration import update_info_bar_for_col
                update_info_bar_for_col(main_window, col_file, file_path)
            except ImportError:
                # Fallback to local info update
                update_col_info_fallback(main_window, col_file, file_path)
            
            # Update window title
            file_name = os.path.basename(file_path)
            main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")
            
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            main_window.log_message(f"✅ COL Load Complete: {file_name} ({model_count} models)")
            
        except Exception as e:
            main_window.log_message(f"❌ Error updating UI after COL load: {str(e)}")
    
    def on_load_error(error_msg):
        """Handle load errors"""
        # Hide progress
        if hasattr(main_window.gui_layout, 'hide_progress'):
            main_window.gui_layout.hide_progress()
        
        main_window.log_message(f"❌ COL Load Error: {error_msg}")
        
        # Show error dialog
        QMessageBox.critical(main_window, "COL Load Error", 
                           f"Failed to load COL file:\n{error_msg}")
    
    # Connect all signals
    loader.progress_update.connect(on_progress)
    loader.model_loaded.connect(on_model_loaded)
    loader.load_complete.connect(on_load_complete)
    loader.load_error.connect(on_load_error)
    
    # Store loader reference to prevent garbage collection
    main_window._col_loader = loader
    
    # Start loading
    loader.start()
    
    main_window.log_message(f"🔄 Started background COL loading: {os.path.basename(file_path)}")
    
    return loader

def cancel_col_loading(main_window):
    """Cancel any ongoing COL loading operation"""
    try:
        if hasattr(main_window, '_col_loader') and main_window._col_loader:
            if main_window._col_loader.isRunning():
                main_window._col_loader.cancel_load()
                main_window._col_loader.wait(3000)  # Wait up to 3 seconds
                main_window.log_message("🛑 COL loading cancelled")
                return True
        return False
    except Exception as e:
        main_window.log_message(f"⚠️ Error cancelling COL load: {str(e)}")
        return False

def populate_col_table_fallback(main_window, col_file):
    """Fallback function to populate table with COL data using robust parsing"""
    try:
        col_debug_log(main_window, f"Populating table with {len(col_file.models)} COL models", 'COL_DISPLAY')
        
        if not hasattr(main_window.gui_layout, 'table'):
            return
            
        table = main_window.gui_layout.table
        table.setRowCount(len(col_file.models))
        
        for i, model in enumerate(col_file.models):
            # Model name
            model_name = getattr(model, 'name', f'Model {i+1}')
            name_item = QTableWidgetItem(model_name)
            table.setItem(i, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem("COL Model")
            table.setItem(i, 1, type_item)
            
            # Get robust stats
            try:
                stats = model.get_stats() if hasattr(model, 'get_stats') else {}
                
                # If stats look corrupted, use GTA SA heuristics
                total_elements = stats.get('total_elements', 0)
                if total_elements == 0 or total_elements > 50000:
                    col_debug_log(main_window, f"Using heuristic estimation for model {model_name}", 'COL_ESTIMATION')
                    model_size = getattr(model, 'size', 0)
                    heuristic_stats = estimate_gtasa_model(model_name, model_size)
                    stats.update(heuristic_stats)
                    total_elements = sum(heuristic_stats.values())
                
                # Size estimate with validation
                size_estimate = max(total_elements * 20, 60)  # Minimum 60 bytes
                size_item = QTableWidgetItem(f"{size_estimate:,} bytes")
                table.setItem(i, 2, size_item)
                
                col_debug_log(main_window, format_parsing_result(stats, model_name), 'COL_DISPLAY')
                
            except Exception as e:
                col_debug_log(main_window, f"Error getting stats for model {model_name}: {str(e)}", 'COL_DISPLAY', 'WARNING')
                # Fallback size
                size_item = QTableWidgetItem("Unknown")
                table.setItem(i, 2, size_item)
            
    except Exception as e:
        col_debug_log(main_window, f"Error in fallback table population: {str(e)}", 'COL_DISPLAY', 'ERROR')
        main_window.log_message(f"⚠️ Error in fallback table population: {str(e)}")

def update_col_info_fallback(main_window, col_file, file_path):
    """Fallback function to update info bar"""
    try:
        if hasattr(main_window.gui_layout, 'file_name_label'):
            file_name = os.path.basename(file_path)
            main_window.gui_layout.file_name_label.setText(f"File: {file_name}")
        
        if hasattr(main_window.gui_layout, 'file_size_label'):
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024*1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            main_window.gui_layout.file_size_label.setText(f"Size: {size_str}")
        
    except Exception as e:
        main_window.log_message(f"⚠️ Error in fallback info update: {str(e)}")

# =======================
# EXISTING COL WIDGETS
# =======================

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
        
        layout.addLayout(header_layout)
        
        # COL files table
        self.col_table = QTableWidget()
        self.col_table.setColumnCount(4)
        self.col_table.setHorizontalHeaderLabels(["Name", "Models", "Version", "Size"])
        
        header = self.col_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.col_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.col_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.col_table.itemDoubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.col_table)
    
    def load_col_file(self):
        """Load COL file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_from_path(file_path)
    
    def load_col_from_path(self, file_path: str):
        """Load COL file from path"""
        try:
            col_file = COLFile(file_path)
            if col_file.load():
                self.add_col_file(col_file)
            else:
                QMessageBox.warning(self, "Load Error", f"Failed to load COL file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading COL file: {str(e)}")
    
    def add_col_file(self, col_file: COLFile):
        """Add COL file to the list"""
        self.col_files.append(col_file)
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the COL files table"""
        self.col_table.setRowCount(len(self.col_files))
        
        for row, col_file in enumerate(self.col_files):
            # Name
            name = os.path.basename(col_file.file_path) if col_file.file_path else "Unknown"
            self.col_table.setItem(row, 0, QTableWidgetItem(name))
            
            # Models count
            model_count = len(col_file.models) if hasattr(col_file, 'models') else 0
            self.col_table.setItem(row, 1, QTableWidgetItem(str(model_count)))
            
            # Version
            version = getattr(col_file, 'version', 'Unknown')
            self.col_table.setItem(row, 2, QTableWidgetItem(str(version)))
            
            # Size
            try:
                size = os.path.getsize(col_file.file_path) if col_file.file_path else 0
                size_str = self.format_file_size(size)
            except:
                size_str = "Unknown"
            self.col_table.setItem(row, 3, QTableWidgetItem(size_str))
    
    def format_file_size(self, size: int) -> str:
        """Format file size for display"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.col_table.currentRow()
        if 0 <= current_row < len(self.col_files):
            col_file = self.col_files[current_row]
            self.col_selected.emit(col_file)
    
    def on_double_click(self, item):
        """Handle double click"""
        row = item.row()
        if 0 <= row < len(self.col_files):
            col_file = self.col_files[row]
            self.col_double_clicked.emit(col_file)

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
        layout.addWidget(QLabel("📋 COL Model Details"))
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_current_model)
        buttons_layout.addWidget(self.edit_btn)
        
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.analyze_current_model)
        buttons_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(buttons_layout)
        
        self.update_display()
    
    def set_col_file(self, col_file: COLFile):
        """Set the current COL file"""
        self.current_col_file = col_file
        self.update_display()
    
    def update_display(self):
        """Update the details display"""
        if not self.current_col_file:
            self.details_text.setText("No COL file selected")
            self.edit_btn.setEnabled(False)
            self.analyze_btn.setEnabled(False)
            return
        
        details = []
        details.append(f"File: {os.path.basename(self.current_col_file.file_path)}")
        
        if hasattr(self.current_col_file, 'models'):
            details.append(f"Models: {len(self.current_col_file.models)}")
            
            for i, model in enumerate(self.current_col_file.models):
                details.append(f"\nModel {i+1}:")
                details.append(f"  Name: {getattr(model, 'name', 'Unnamed')}")
                
                if hasattr(model, 'get_stats'):
                    stats = model.get_stats()
                    for key, value in stats.items():
                        details.append(f"  {key.title()}: {value}")
        
        self.details_text.setText("\n".join(details))
        self.edit_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
    
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

# =======================
# INTEGRATION FUNCTIONS
# =======================

def setup_col_integration_full(main_window):
    """Main COL integration entry point with threaded loading"""
    try:
        col_debug_log(main_window, "Starting COL integration for IMG interface", 'COL_INTEGRATION')

        # Setup COL debug functionality first
        setup_col_debug_for_main_window(main_window)

        # Setup threaded loading first
        setup_threaded_col_loading(main_window)

        # Add COL tools menu to existing menu bar
        if hasattr(main_window, 'menuBar') and main_window.menuBar():
            add_col_tools_menu(main_window)
            col_debug_log(main_window, "COL tools menu added", 'COL_INTEGRATION')

        # Add COL context menu items to existing entries table
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            add_col_context_menu_to_entries_table(main_window)
            col_debug_log(main_window, "COL context menu added to entries table", 'COL_INTEGRATION')

        # Mark integration as completed
        main_window._col_integration_active = True
        
        col_debug_log(main_window, "COL integration completed successfully", 'COL_INTEGRATION')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"COL integration failed: {e}", 'COL_INTEGRATION', 'ERROR')
        return False

def setup_threaded_col_loading(main_window):
    """Setup threaded COL loading functionality"""
    try:
        # Apply robust parsing patches first
        patch_col_parsing_for_robustness()
        col_debug_log(main_window, "Applied robust COL parsing patches", 'COL_PARSING')
        
        # Add async loading method to main window
        main_window.load_col_file_async = lambda file_path: load_col_file_async(main_window, file_path)
        
        # Update existing COL loading to use async version
        if hasattr(main_window, 'load_col_file_safely'):
            # Replace synchronous loader with async version
            main_window.load_col_file_safely = main_window.load_col_file_async
        
        # Add cancel method
        main_window.cancel_col_loading = lambda: cancel_col_loading(main_window)
        
        main_window.log_message("✅ COL integration with threading enabled")
        col_debug_log(main_window, "Threaded COL loading setup complete", 'COL_THREADING')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error setting up threaded COL integration: {str(e)}", 'COL_INTEGRATION', 'ERROR')
        main_window.log_message(f"❌ Error setting up threaded COL integration: {str(e)}")
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
        
        # COL Editor
        editor_action = QAction("✏️ COL Editor", main_window)
        editor_action.setStatusTip("Open COL file editor")
        editor_action.triggered.connect(lambda: open_col_editor(main_window))
        col_submenu.addAction(editor_action)
        
        # Analyzer
        analyze_action = QAction("🔍 Analyze COL", main_window)
        analyze_action.setStatusTip("Analyze COL file structure")
        analyze_action.triggered.connect(lambda: analyze_col_file_dialog(main_window))
        col_submenu.addAction(analyze_action)
        
        print("✓ COL tools menu created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating COL tools menu: {e}")
        return False

def add_col_context_menu_to_entries_table(main_window):
    """Add COL-specific context menu items to entries table"""
    try:
        if not hasattr(main_window.gui_layout, 'table'):
            return False
        
        entries_table = main_window.gui_layout.table
        original_context_menu = entries_table.contextMenuEvent
        
        def enhanced_context_menu_event(event: QContextMenuEvent):
            """Enhanced context menu with COL support"""
            # Get selected row
            item = entries_table.itemAt(event.pos())
            if not item:
                return
            
            row = item.row()
            
            # Create context menu
            menu = QMenu(entries_table)
            
            # Check if selected entry might be a COL file
            try:
                name_item = entries_table.item(row, 0)
                if name_item:
                    entry_name = name_item.text().lower()
                    if entry_name.endswith('.col'):
                        # Add COL-specific actions
                        edit_action = QAction("✏️ Edit COL", entries_table)
                        edit_action.triggered.connect(lambda: edit_col_from_img_entry(main_window, row))
                        menu.addAction(edit_action)
                        
                        # Analyze COL
                        analyze_action = QAction("🔍 Analyze COL", entries_table)
                        analyze_action.triggered.connect(lambda: analyze_col_from_img_entry(main_window, row))
                        menu.addAction(analyze_action)
                        
                        menu.addSeparator()
            except:
                pass
            
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

# =======================
# COL OPERATIONS
# =======================

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
        
        output_dir = QFileDialog.getExistingDirectory(main_window, "Select Output Directory")
        if not output_dir:
            return
        
        exported_count = 0
        
        for entry in main_window.current_img.entries:
            if entry.name.lower().endswith('.col'):
                output_path = os.path.join(output_dir, entry.name)
                
                with open(output_path, 'wb') as f:
                    f.write(entry.data)
                
                exported_count += 1
        
        QMessageBox.information(main_window, "Export Complete", 
                              f"Exported {exported_count} COL files to {output_dir}")
                              
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to export COL files: {str(e)}")

def edit_col_from_img_entry(main_window, row: int):
    """Edit COL file from IMG entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "No IMG file loaded")
            return
        
        # Get entry from table
        name_item = main_window.gui_layout.table.item(row, 0)
        if not name_item:
            return
        
        entry_name = name_item.text()
        
        # Find entry in IMG
        entry = None
        for img_entry in main_window.current_img.entries:
            if img_entry.name == entry_name:
                entry = img_entry
                break
        
        if not entry:
            QMessageBox.warning(main_window, "Not Found", f"Entry {entry_name} not found")
            return
        
        # Extract COL data to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.col', delete=False)
        temp_file.write(entry.data)
        temp_file.close()
        
        # Open COL editor
        try:
            open_col_editor(main_window, temp_file.name)
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to edit COL: {str(e)}")

def analyze_col_from_img_entry(main_window, row: int):
    """Analyze COL file from IMG entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "No IMG file loaded")
            return
        
        # Get entry from table
        name_item = main_window.gui_layout.table.item(row, 0)
        if not name_item:
            return
        
        entry_name = name_item.text()
        
        # Find entry in IMG
        entry = None
        for img_entry in main_window.current_img.entries:
            if img_entry.name == entry_name:
                entry = img_entry
                break
        
        if not entry:
            QMessageBox.warning(main_window, "Not Found", f"Entry {entry_name} not found")
            return
        
        # Extract COL data to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.col', delete=False)
        temp_file.write(entry.data)
        temp_file.close()
        
        # Analyze COL file
        try:
            analyze_col_file_dialog(main_window, temp_file.name)
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL: {str(e)}")

def load_col_from_img_entry(main_window, entry_name: str) -> Optional[COLFile]:
    """Load COL file from IMG entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return None
        
        # Find entry in IMG
        entry = None
        for img_entry in main_window.current_img.entries:
            if img_entry.name == entry_name:
                entry = img_entry
                break
        
        if not entry:
            return None
        
        # Extract COL data to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.col', delete=False)
        temp_file.write(entry.data)
        temp_file.close()
        
        # Load COL file
        col_file = COLFile(temp_file.name)
        if col_file.load():
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return col_file
        else:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
            return None
            
    except Exception as e:
        print(f"Error loading COL from IMG entry: {e}")
        return None

def export_col_to_img(main_window, col_file: COLFile, entry_name: str) -> bool:
    """Export COL file back to IMG entry"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False
        
        # Save COL to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.col', delete=False)
        temp_file.close()
        
        if not col_file.save(temp_file.name):
            os.unlink(temp_file.name)
            return False
        
        # Read COL data
        with open(temp_file.name, 'rb') as f:
            col_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        # Find existing entry or create new one
        entry = None
        for img_entry in main_window.current_img.entries:
            if img_entry.name == entry_name:
                entry = img_entry
                break
        
        if entry:
            # Update existing entry
            entry.data = col_data
        else:
            # Create new entry
            main_window.current_img.add_entry(entry_name, col_data)
        
        return True
        
    except Exception as e:
        print(f"Error exporting COL to IMG: {e}")
        return False

# =======================
# HELPER FUNCTIONS
# =======================

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

def open_col_file_dialog(main_window):
    """Open COL file dialog with threaded loading"""
    file_path, _ = QFileDialog.getOpenFileName(
        main_window, "Open COL File", "", "COL Files (*.col);;All Files (*)"
    )
    
    if file_path:
        # Use threaded loading if available
        if hasattr(main_window, 'load_col_file_async'):
            main_window.load_col_file_async(file_path)
        else:
            # Fallback to synchronous loading
            try:
                col_file = COLFile(file_path)
                if col_file.load():
                    main_window.current_col = col_file
                    main_window.log_message(f"✅ COL file loaded: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(main_window, "Load Error", f"Failed to load COL file: {file_path}")
            except Exception as e:
                QMessageBox.critical(main_window, "Error", f"Error loading COL file: {str(e)}")

def create_new_col_file(main_window):
    """Create new COL file"""
    QMessageBox.information(main_window, "New COL", "New COL file creation coming soon!")

# =======================
# COMPATIBILITY FUNCTIONS
# =======================

def setup_complete_col_integration(main_window):
    """Complete COL integration setup - main entry point"""
    try:
        # Call the full integration function
        success = setup_col_integration_full(main_window)
        
        if success:
            main_window.log_message("✅ Complete COL integration setup finished")
        else:
            main_window.log_message("⚠️ COL integration setup had issues")
            
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ COL integration setup failed: {str(e)}")
        return False

# =======================
# DEPRECATED FUNCTIONS (kept for compatibility)
# =======================

def init_col_integration_placeholder(main_window):
    """Placeholder for COL integration during init - DEPRECATED"""
    # Just set a flag that COL integration is needed
    main_window._col_integration_needed = True
    print("COL integration marked for later setup - use setup_complete_col_integration instead")

def setup_delayed_col_integration(main_window):
    """Setup COL integration after GUI is fully ready"""
    try:
        # Use a timer to delay until GUI is ready
        def try_setup():
            if setup_col_integration_full(main_window):
                # Success - stop trying
                return
            else:
                # Retry in 100ms
                QTimer.singleShot(100, try_setup)
        
        # Start the retry process
        QTimer.singleShot(100, try_setup)
        
    except Exception as e:
        print(f"Error setting up delayed COL integration: {str(e)}")

# Module exports
__all__ = [
    'COLBackgroundLoader',
    'load_col_file_async',
    'cancel_col_loading',
    'COLListWidget', 
    'COLModelDetailsWidget',
    'setup_col_integration_full',
    'setup_complete_col_integration',
    'add_col_tools_menu',
    'add_col_context_menu_to_entries_table',
    'import_col_to_current_img',
    'export_all_col_from_img',
    'edit_col_from_img_entry',
    'analyze_col_from_img_entry',
    'load_col_from_img_entry',
    'export_col_to_img',
    'open_col_file_dialog',
    'create_new_col_file'
]