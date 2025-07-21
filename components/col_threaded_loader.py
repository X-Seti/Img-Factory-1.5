#this belongs in components/col_threaded_loader.py - Version: 5
# X-Seti - July20 2025 - IMG Factory 1.5 - COL Threaded Loader
# Background COL file loading with progress feedback using IMG debug system

"""
COL Threaded Loader - Asynchronous COL file loading
Provides background loading with progress updates and status reporting
"""

import os
import time
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox

# Import IMG debug system and COL classes
from components.img_debug_functions import img_debugger
from components.col_core_classes import COLFile

##Methods list -
# load_col_file_async

##Classes -
# COLBackgroundLoader

class COLBackgroundLoader(QThread):
    """Background COL file loader with progress signals"""
    
    # Signals for progress updates
    progress_update = pyqtSignal(int, str)  # progress, status
    model_loaded = pyqtSignal(int, str)     # count, name
    load_complete = pyqtSignal(object)      # col_file
    load_error = pyqtSignal(str)            # error_message
    
    def __init__(self, file_path: str = None, main_window=None):
        super().__init__()
        self.file_path = file_path
        self.main_window = main_window
        self.col_file = None
        self._should_stop = False
    
    def set_file_path(self, file_path: str): #vers 1
        """Set the file path to load"""
        self.file_path = file_path
    
    def stop_loading(self): #vers 1
        """Stop the loading process"""
        self._should_stop = True
        img_debugger.debug("COL loading stop requested")
    
    def run(self): #vers 1
        """Main thread execution - load COL file with progress"""
        try:
            if not self.file_path:
                self.load_error.emit("No file path specified")
                return
            
            if not os.path.exists(self.file_path):
                self.load_error.emit(f"File not found: {self.file_path}")
                return
            
            img_debugger.debug(f"Starting background COL load: {os.path.basename(self.file_path)}")
            
            # Initialize progress
            self.progress_update.emit(0, "Starting COL file load...")
            
            # Create COL file object
            self.col_file = COLFile(self.file_path)
            
            # Check if we should stop
            if self._should_stop:
                return
            
            # Load with progress monitoring
            self.progress_update.emit(25, "Reading file data...")
            
            success = self._load_with_progress()
            
            if self._should_stop:
                return
            
            if success:
                self.progress_update.emit(100, "Load complete!")
                self.load_complete.emit(self.col_file)
                img_debugger.success(f"COL file loaded successfully: {os.path.basename(self.file_path)}")
            else:
                error_msg = self.col_file.load_error or "Unknown loading error"
                self.load_error.emit(error_msg)
                img_debugger.error(f"COL file loading failed: {error_msg}")
                
        except Exception as e:
            error_msg = f"COL loading exception: {str(e)}"
            self.load_error.emit(error_msg)
            img_debugger.error(error_msg)
    
    def _load_with_progress(self) -> bool: #vers 1
        """Load COL file with progress monitoring"""
        try:
            # Wrap the COL file's load method to provide progress feedback
            def progress_load():
                self.progress_update.emit(50, "Parsing COL structure...")
                
                result = self.col_file.load()
                
                if result and self.col_file.models:
                    self.progress_update.emit(75, f"Processing {len(self.col_file.models)} models...")
                    
                    # Report individual models
                    for i, model in enumerate(self.col_file.models):
                        if self._should_stop:
                            return False
                        
                        model_name = model.name or f"Model_{i+1}"
                        progress = 75 + (20 * (i + 1) // len(self.col_file.models))
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

def load_col_file_async(main_window, file_path: str): #vers 1
    """Load COL file asynchronously with progress feedback"""
    
    # Create progress dialog
    progress_dialog = None
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
            from methods.populate_col_table import populate_table_with_col_data_debug
            populate_table_with_col_data_debug(main_window, col_file)
            
            # Update info bar
            from gui.gui_infobar import update_col_info_bar_enhanced
            update_col_info_bar_enhanced(main_window, col_file, file_path)
            
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