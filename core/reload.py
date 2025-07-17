#this belongs in core/ reload.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - Reload Function

"""
IMG Factory Reload Function
Handles reloading IMG/COL files without losing current state
"""

import os
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal


class ReloadThread(QThread):
    """Background thread for reloading files"""
    
    progress_updated = pyqtSignal(int, str)
    reload_completed = pyqtSignal(bool, str)
    
    def __init__(self, main_window, file_path: str, file_type: str):
        super().__init__()
        self.main_window = main_window
        self.file_path = file_path
        self.file_type = file_type.upper()
        
    def run(self):
        """Run reload in background"""
        try:
            self.progress_updated.emit(10, "Validating file...")
            
            # Check if file still exists
            if not os.path.exists(self.file_path):
                self.reload_completed.emit(False, f"File not found: {self.file_path}")
                return
            
            self.progress_updated.emit(30, "Reading file...")
            
            # Reload based on file type
            if self.file_type == 'IMG':
                success = self._reload_img_file()
            elif self.file_type == 'COL':
                success = self._reload_col_file()
            else:
                self.reload_completed.emit(False, f"Unsupported file type: {self.file_type}")
                return
            
            if success:
                self.progress_updated.emit(100, "Reload complete")
                self.reload_completed.emit(True, "File reloaded successfully")
            else:
                self.reload_completed.emit(False, "Reload failed")
                
        except Exception as e:
            self.reload_completed.emit(False, f"Reload error: {str(e)}")
    
    def _reload_img_file(self) -> bool:
        """Reload IMG file"""
        try:
            from components.img_core_classes import IMGFile
            
            self.progress_updated.emit(50, "Loading IMG data...")
            
            # Create new IMG instance
            new_img = IMGFile()
            if not new_img.load_from_file(self.file_path):
                return False
            
            self.progress_updated.emit(80, "Updating interface...")
            
            # Store new IMG reference
            self.main_window.current_img = new_img
            
            return True
            
        except Exception as e:
            print(f"IMG reload error: {e}")
            return False
    
    def _reload_col_file(self) -> bool:
        """Reload COL file"""
        try:
            from components.col_core_classes import COLFile
            
            self.progress_updated.emit(50, "Loading COL data...")
            
            # Create new COL instance
            new_col = COLFile()
            if not new_col.load_from_file(self.file_path):
                return False
            
            self.progress_updated.emit(80, "Updating interface...")
            
            # Store new COL reference
            self.main_window.current_col = new_col
            
            return True
            
        except Exception as e:
            print(f"COL reload error: {e}")
            return False


def reload_current_file(main_window) -> bool:
    """Reload the currently loaded IMG or COL file"""
    try:
        # Determine current file type and path
        if hasattr(main_window, 'current_img') and main_window.current_img:
            file_path = main_window.current_img.file_path
            file_type = 'IMG'
            current_entries = len(main_window.current_img.entries) if main_window.current_img.entries else 0
        elif hasattr(main_window, 'current_col') and main_window.current_col:
            file_path = main_window.current_col.file_path
            file_type = 'COL'
            current_entries = len(main_window.current_col.models) if hasattr(main_window.current_col, 'models') and main_window.current_col.models else 0
        else:
            main_window.log_message("❌ No file loaded to reload")
            return False
        
        if not file_path or not os.path.exists(file_path):
            main_window.log_message("❌ Current file path is invalid or file doesn't exist")
            return False
        
        # Confirm reload
        filename = os.path.basename(file_path)
        reply = QMessageBox.question(
            main_window, 
            "Reload File",
            f"Reload {filename}?\n\nCurrent: {current_entries} entries\nThis will refresh the file from disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            main_window.log_message("🔄 Reload cancelled by user")
            return False
        
        main_window.log_message(f"🔄 Reloading {file_type} file: {filename}")
        
        # Start reload thread
        reload_thread = ReloadThread(main_window, file_path, file_type)
        
        # Connect signals
        reload_thread.progress_updated.connect(
            lambda progress, message: _update_reload_progress(main_window, progress, message)
        )
        reload_thread.reload_completed.connect(
            lambda success, message: _handle_reload_completion(main_window, success, message, file_type)
        )
        
        # Store thread reference to prevent garbage collection
        main_window._reload_thread = reload_thread
        reload_thread.start()
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Reload initiation failed: {str(e)}")
        return False


def reload_img_file(main_window, file_path: str) -> bool:
    """Reload specific IMG file by path"""
    try:
        if not os.path.exists(file_path):
            main_window.log_message(f"❌ IMG file not found: {file_path}")
            return False
        
        filename = os.path.basename(file_path)
        main_window.log_message(f"🔄 Reloading IMG file: {filename}")
        
        # Close current file if different
        if (hasattr(main_window, 'current_img') and main_window.current_img and 
            main_window.current_img.file_path != file_path):
            main_window.current_img.close()
        
        # Load the file
        from components.img_core_classes import IMGFile
        new_img = IMGFile()
        
        if new_img.load_from_file(file_path):
            main_window.current_img = new_img
            
            # Update UI
            if hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            
            entry_count = len(new_img.entries) if new_img.entries else 0
            main_window.log_message(f"✅ IMG reloaded: {filename} ({entry_count} entries)")
            return True
        else:
            main_window.log_message(f"❌ Failed to reload IMG: {filename}")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ IMG reload error: {str(e)}")
        return False


def reload_col_file(main_window, file_path: str) -> bool:
    """Reload specific COL file by path"""
    try:
        if not os.path.exists(file_path):
            main_window.log_message(f"❌ COL file not found: {file_path}")
            return False
        
        filename = os.path.basename(file_path)
        main_window.log_message(f"🔄 Reloading COL file: {filename}")
        
        # Close current file if different
        if (hasattr(main_window, 'current_col') and main_window.current_col and 
            main_window.current_col.file_path != file_path):
            main_window.current_col.close()
        
        # Load the file
        from components.col_core_classes import COLFile
        new_col = COLFile()
        
        if new_col.load_from_file(file_path):
            main_window.current_col = new_col
            
            # Update UI
            if hasattr(main_window, '_update_ui_for_loaded_col'):
                main_window._update_ui_for_loaded_col()
            
            model_count = len(new_col.models) if hasattr(new_col, 'models') and new_col.models else 0
            main_window.log_message(f"✅ COL reloaded: {filename} ({model_count} models)")
            return True
        else:
            main_window.log_message(f"❌ Failed to reload COL: {filename}")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ COL reload error: {str(e)}")
        return False


def quick_reload(main_window) -> bool:
    """Quick reload without confirmation dialog"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            file_path = main_window.current_img.file_path
            return reload_img_file(main_window, file_path)
        elif hasattr(main_window, 'current_col') and main_window.current_col:
            file_path = main_window.current_col.file_path
            return reload_col_file(main_window, file_path)
        else:
            main_window.log_message("❌ No file loaded for quick reload")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Quick reload error: {str(e)}")
        return False


def _update_reload_progress(main_window, progress: int, message: str):
    """Update reload progress in UI"""
    try:
        main_window.log_message(f"🔄 {message}")
        
        # Update progress bar if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(progress, message)
            
    except Exception as e:
        print(f"Progress update error: {e}")


def _handle_reload_completion(main_window, success: bool, message: str, file_type: str):
    """Handle reload completion"""
    try:
        if success:
            main_window.log_message(f"✅ {message}")
            
            # Update UI based on file type
            if file_type == 'IMG' and hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            elif file_type == 'COL' and hasattr(main_window, '_update_ui_for_loaded_col'):
                main_window._update_ui_for_loaded_col()
            
            # Clear progress
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
                main_window.gui_layout.show_progress(-1, "Ready")
                
        else:
            main_window.log_message(f"❌ {message}")
            
            # Show error dialog
            QMessageBox.critical(main_window, "Reload Failed", f"Failed to reload file:\n{message}")
        
        # Clean up thread reference
        if hasattr(main_window, '_reload_thread'):
            delattr(main_window, '_reload_thread')
            
    except Exception as e:
        main_window.log_message(f"❌ Reload completion error: {str(e)}")


def integrate_reload_functions(main_window) -> bool:
    """Integrate reload functions into main window"""
    try:
        # Add reload methods
        main_window.reload_current_file = lambda: reload_current_file(main_window)
        main_window.reload_img_file = lambda path: reload_img_file(main_window, path)
        main_window.reload_col_file = lambda path: reload_col_file(main_window, path)
        main_window.quick_reload = lambda: quick_reload(main_window)
        
        # Legacy compatibility
        main_window.reload_table = main_window.reload_current_file
        main_window.refresh_current_file = main_window.reload_current_file
        
        main_window.log_message("✅ Reload functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Reload integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'reload_current_file',
    'reload_img_file', 
    'reload_col_file',
    'quick_reload',
    'integrate_reload_functions',
    'ReloadThread'
]