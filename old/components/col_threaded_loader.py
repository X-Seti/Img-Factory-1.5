#this belongs in components/col_background_loader.py - version 1
# X-Seti - July10 2025 - Img Factory 1.5
# Background COL loader to prevent UI freezing during long loads

import os
import time
from typing import Optional, Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

try:
    from components.col_core_classes import COLFile, COLModel
except ImportError:
    pass

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
            self.progress_update.emit(0, "Initializing COL loader...")
            QApplication.processEvents()
            
            # Check file exists
            if not os.path.exists(self.file_path):
                self.load_error.emit(f"File not found: {self.file_path}")
                return
                
            file_size = os.path.getsize(self.file_path)
            self.progress_update.emit(5, f"Loading COL file ({file_size:,} bytes)...")
            
            # Create COL file object
            self.col_file = COLFile(self.file_path)
            
            self.progress_update.emit(10, "Reading COL header...")
            
            # Start the actual loading with progress monitoring
            if not self._load_with_progress():
                self.load_error.emit("Failed to load COL file - see log for details")
                return
                
            self.progress_update.emit(100, "COL loading complete")
            self.load_complete.emit(self.col_file)
            
        except Exception as e:
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
            from components.col_tab_integration import populate_table_with_col_data_debug
            populate_table_with_col_data_debug(main_window, col_file)
            
            # Update info bar
            from components.col_tab_integration import update_info_bar_for_col
            update_info_bar_for_col(main_window, col_file, file_path)
            
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
        from PyQt6.QtWidgets import QMessageBox
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