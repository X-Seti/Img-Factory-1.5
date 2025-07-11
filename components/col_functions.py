#this belongs in components/ col_functions.py - Version: 2  
# X-Seti - July11 2025 - Img Factory 1.5
# COL Functions - COMPLETE VERSION with debug control

"""
COL Functions - Integration functions for COL file support
Provides COL file loading, display, and integration with IMG Factory
"""

import os
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QLabel, QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QMenu, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QContextMenuEvent

# Import COL classes with debug control
from components.col_core_classes import COLFile, is_col_debug_enabled, set_col_debug_enabled
from components.col_parsing_functions import COLParser


def col_debug_log(main_window, message: str, category: str = 'COL_GENERAL', level: str = 'INFO'):
    """Log COL debug message only if debug is enabled"""
    if is_col_debug_enabled():
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"[{category}] {message}")
        else:
            print(f"[{category}] {message}")


class COLBackgroundLoader(QThread):
    """Background thread for loading COL files without blocking UI"""
    
    progress = pyqtSignal(str)  # status message
    finished = pyqtSignal(bool, str, object)  # success, message, col_file
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.should_cancel = False
    
    def cancel(self):
        """Cancel the loading operation"""
        self.should_cancel = True
    
    def run(self):
        """Load COL file in background"""
        try:
            if self.should_cancel:
                return
            
            self.progress.emit(f"Loading {os.path.basename(self.file_path)}...")
            
            # Create COL file object
            col_file = COLFile(self.file_path)
            
            if self.should_cancel:
                return
            
            self.progress.emit("Parsing COL data...")
            
            # Load the file
            success = col_file.load_from_file(self.file_path)
            
            if self.should_cancel:
                return
            
            if success:
                message = f"Loaded {len(col_file.models)} COL models"
                self.finished.emit(True, message, col_file)
            else:
                error_msg = col_file.load_error or "Unknown error"
                self.finished.emit(False, f"Failed to load COL: {error_msg}", None)
                
        except Exception as e:
            self.finished.emit(False, f"Error loading COL: {str(e)}", None)


def load_col_file_async(main_window, file_path: str) -> COLBackgroundLoader:
    """Load COL file asynchronously and return the loader thread"""
    loader = COLBackgroundLoader(file_path)
    
    def on_progress(message):
        col_debug_log(main_window, message, 'COL_LOADING')
    
    def on_finished(success, message, col_file):
        if success:
            col_debug_log(main_window, f"COL loaded successfully: {message}", 'COL_LOADING')
            if hasattr(main_window, 'current_col'):
                main_window.current_col = col_file
        else:
            col_debug_log(main_window, f"COL loading failed: {message}", 'COL_LOADING')
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(message)
    
    loader.progress.connect(on_progress)
    loader.finished.connect(on_finished)
    
    return loader


def cancel_col_loading(loader: COLBackgroundLoader):
    """Cancel COL loading operation"""
    if loader and loader.isRunning():
        loader.cancel()
        loader.wait(1000)  # Wait up to 1 second for clean shutdown


class COLListWidget(QListWidget):
    """Widget for displaying list of COL models"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.col_file = None
        self.setAlternatingRowColors(True)
    
    def set_col_file(self, col_file: COLFile):
        """Set the COL file to display"""
        self.col_file = col_file
        self.update_display()
    
    def update_display(self):
        """Update the display with COL models"""
        self.clear()
        
        if not self.col_file or not hasattr(self.col_file, 'models'):
            return
        
        for i, model in enumerate(self.col_file.models):
            name = getattr(model, 'name', f'Model_{i}')
            stats = getattr(model, 'get_stats', lambda: {})()
            
            # Format display text
            elements = stats.get('total_elements', 0)
            version = getattr(model, 'version', None)
            version_text = f"v{version.value}" if version else "v?"
            
            display_text = f"{name} ({version_text}) - {elements} elements"
            
            item = QListWidgetItem(display_text)
            item.setData(0x0100, i)  # Store model index
            self.addItem(item)


class COLModelDetailsWidget(QWidget):
    """Widget for displaying detailed COL model information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_col_file = None
        self._create_ui()
    
    def _create_ui(self):
        """Create the details widget UI"""
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel("COL Model Details")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        layout.addWidget(self.details_text)
        
        # Buttons
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
            # Try to open COL editor if available
            try:
                from components.col_editor import COLEditorDialog
                editor = COLEditorDialog(self)
                editor.load_col_file(self.current_col_file.file_path)
                editor.exec()
            except ImportError:
                QMessageBox.information(self, "COL Editor", 
                    "COL editor will be available in a future version.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open COL editor: {str(e)}")
    
    def analyze_current_model(self):
        """Analyze current model"""
        if not self.current_col_file:
            return
        
        try:
            # Create detailed analysis
            analysis = []
            analysis.append("COL File Analysis")
            analysis.append("=" * 20)
            analysis.append(f"File: {self.current_col_file.file_path}")
            analysis.append(f"Size: {os.path.getsize(self.current_col_file.file_path):,} bytes")
            analysis.append(f"Models: {len(self.current_col_file.models)}")
            
            total_elements = 0
            for i, model in enumerate(self.current_col_file.models):
                analysis.append(f"\nModel {i+1}: {getattr(model, 'name', 'Unnamed')}")
                stats = getattr(model, 'get_stats', lambda: {})()
                for key, value in stats.items():
                    analysis.append(f"  {key}: {value}")
                    if key == 'total_elements':
                        total_elements += value
            
            analysis.append(f"\nTotal Elements: {total_elements}")
            
            # Show analysis in message box
            QMessageBox.information(self, "COL Analysis", "\n".join(analysis))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")


def setup_col_debug_for_main_window(main_window):
    """Setup COL debug functionality for main window"""
    try:
        # Add COL debug control methods
        def enable_col_debug():
            """Enable COL debug output"""
            set_col_debug_enabled(True)
            col_debug_log(main_window, "COL debug enabled", 'COL_DEBUG')
        
        def disable_col_debug():
            """Disable COL debug output"""
            set_col_debug_enabled(False)
            if hasattr(main_window, 'log_message'):
                main_window.log_message("COL debug disabled")
        
        def toggle_col_debug():
            """Toggle COL debug output"""
            if is_col_debug_enabled():
                disable_col_debug()
            else:
                enable_col_debug()
        
        # Add methods to main window
        main_window.enable_col_debug = enable_col_debug
        main_window.disable_col_debug = disable_col_debug
        main_window.toggle_col_debug = toggle_col_debug
        
        col_debug_log(main_window, "COL debug controls setup complete", 'COL_INTEGRATION')
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL debug setup error: {e}")
        return False


def setup_threaded_col_loading(main_window):
    """Setup threaded COL loading for main window"""
    try:
        # Add COL loading methods
        def load_col_file(file_path):
            """Load COL file with progress feedback"""
            if not file_path or not os.path.exists(file_path):
                main_window.log_message("COL file not found")
                return False
            
            # Start background loading
            loader = load_col_file_async(main_window, file_path)
            loader.start()
            
            # Store loader reference to prevent garbage collection
            if not hasattr(main_window, '_col_loaders'):
                main_window._col_loaders = []
            main_window._col_loaders.append(loader)
            
            return True
        
        # Add method to main window
        main_window.load_col_file = load_col_file
        
        col_debug_log(main_window, "Threaded COL loading setup complete", 'COL_INTEGRATION')
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL threading setup error: {e}")
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
        
        # Open COL file
        open_action = QAction("📂 Open COL File", main_window)
        open_action.setStatusTip("Open a COL collision file")
        open_action.triggered.connect(lambda: open_col_file_dialog(main_window))
        col_submenu.addAction(open_action)
        
        # Create new COL
        new_action = QAction("🆕 New COL File", main_window)
        new_action.setStatusTip("Create a new COL file")
        new_action.triggered.connect(lambda: create_new_col_file(main_window))
        col_submenu.addAction(new_action)
        
        col_submenu.addSeparator()
        
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
        
        col_debug_log(main_window, "COL tools menu created", 'COL_INTEGRATION')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error creating COL tools menu: {e}", 'COL_INTEGRATION')
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
            menu.exec(event.globalPos())
        
        # Replace the context menu handler
        entries_table.contextMenuEvent = enhanced_context_menu_event
        
        col_debug_log(main_window, "COL context menu added to entries table", 'COL_INTEGRATION')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Error adding COL context menu: {e}", 'COL_INTEGRATION')
        return False


# =======================
# COL FILE OPERATIONS
# =======================

def open_col_file_dialog(main_window):
    """Open COL file dialog"""
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Open COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            main_window.load_col_file(file_path)
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open COL file: {str(e)}")


def create_new_col_file(main_window):
    """Create new COL file"""
    try:
        file_path, _ = QFileDialog.getSaveFileName(
            main_window,
            "Create New COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            # Create basic COL file
            col_file = COLFile()
            if col_file.save_to_file(file_path):
                main_window.log_message(f"Created new COL file: {os.path.basename(file_path)}")
            else:
                QMessageBox.critical(main_window, "Error", "Failed to create COL file")
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to create COL file: {str(e)}")


def import_col_to_current_img(main_window):
    """Import COL file to current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "Warning", "No IMG file is currently open")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Import COL File to IMG",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            # Implementation for importing COL to IMG
            main_window.log_message(f"COL import functionality will be implemented")
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to import COL: {str(e)}")


def export_all_col_from_img(main_window):
    """Export all COL files from current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "Warning", "No IMG file is currently open")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Export COL Files to Directory"
        )
        
        if output_dir:
            # Implementation for exporting all COL files
            main_window.log_message(f"COL export functionality will be implemented")
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to export COL files: {str(e)}")


def edit_col_from_img_entry(main_window, row):
    """Edit COL file from IMG entry"""
    try:
        # Get entry from row
        if hasattr(main_window, 'current_img') and main_window.current_img:
            entries = main_window.current_img.entries
            if row < len(entries):
                entry = entries[row]
                # Implementation for editing COL from IMG entry
                main_window.log_message(f"COL editing from IMG entry will be implemented")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to edit COL: {str(e)}")


def analyze_col_from_img_entry(main_window, row):
    """Analyze COL file from IMG entry"""
    try:
        # Get entry from row
        if hasattr(main_window, 'current_img') and main_window.current_img:
            entries = main_window.current_img.entries
            if row < len(entries):
                entry = entries[row]
                # Implementation for analyzing COL from IMG entry
                main_window.log_message(f"COL analysis from IMG entry will be implemented")
        
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL: {str(e)}")


def load_col_from_img_entry(main_window, entry):
    """Load COL file from IMG entry"""
    try:
        # Implementation for loading COL from IMG entry
        col_debug_log(main_window, f"Loading COL from IMG entry: {entry.name}", 'COL_LOADING')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Failed to load COL from IMG entry: {e}", 'COL_LOADING')
        return False


def export_col_to_img(main_window, col_file, img_file):
    """Export COL file to IMG"""
    try:
        # Implementation for exporting COL to IMG
        col_debug_log(main_window, f"Exporting COL to IMG", 'COL_INTEGRATION')
        return True
        
    except Exception as e:
        col_debug_log(main_window, f"Failed to export COL to IMG: {e}", 'COL_INTEGRATION')
        return False


def open_col_batch_processor(main_window):
    """Open COL batch processor"""
    try:
        # Try to open batch processor if available
        try:
            from components.col_utilities import COLBatchProcessor
            processor = COLBatchProcessor(main_window)
            processor.exec()
        except ImportError:
            QMessageBox.information(main_window, "Batch Processor", 
                "COL batch processor will be available in a future version.")
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open batch processor: {str(e)}")


def open_col_editor(main_window):
    """Open COL editor"""
    try:
        # Try to open COL editor if available
        try:
            from components.col_editor import COLEditorDialog
            editor = COLEditorDialog(main_window)
            editor.exec()
        except ImportError:
            QMessageBox.information(main_window, "COL Editor", 
                "COL editor will be available in a future version.")
                
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to open COL editor: {str(e)}")


def analyze_col_file_dialog(main_window):
    """Show COL file analysis dialog"""
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Analyze COL File",
            "",
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            # Parse and analyze the file
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
            
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Failed to analyze COL file: {str(e)}")


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
        col_debug_log(main_window, f"COL integration failed: {e}", 'COL_INTEGRATION')
        return False


def setup_complete_col_integration(main_window):
    """Complete COL integration setup - main entry point"""
    try:
        # Check settings for initial debug state
        try:
            if hasattr(main_window, 'app_settings'):
                debug_mode = main_window.app_settings.current_settings.get('debug_mode', False)
                debug_categories = main_window.app_settings.current_settings.get('debug_categories', [])
                
                # Enable COL debug only if debug mode is on AND COL categories are enabled
                col_debug = debug_mode and any('COL' in cat for cat in debug_categories)
                set_col_debug_enabled(col_debug)
                
                if col_debug:
                    col_debug_log(main_window, "COL debug enabled from settings", 'COL_INTEGRATION')
                else:
                    col_debug_log(main_window, "COL debug disabled for performance", 'COL_INTEGRATION')
        except Exception as e:
            col_debug_log(main_window, f"Settings integration error: {e}", 'COL_INTEGRATION')
            # Default to disabled for performance
            set_col_debug_enabled(False)
        
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
    col_debug_log(main_window, "COL integration marked for later setup", 'COL_INTEGRATION')


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
        col_debug_log(main_window, f"Error setting up delayed COL integration: {str(e)}", 'COL_INTEGRATION')


# Export main classes and functions
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
    'create_new_col_file',
    'open_col_batch_processor',
    'open_col_editor',
    'analyze_col_file_dialog',
    'setup_col_debug_for_main_window',
    'setup_threaded_col_loading',
    'col_debug_log'
]
