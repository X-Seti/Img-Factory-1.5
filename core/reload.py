#this belongs in core/reload.py - Version: 6
# X-Seti - August05 2025 - IMG Factory 1.5 - Reload Functions

"""
IMG Factory Reload Functions - TAB-AWARE VERSION
Handles reloading IMG and COL files with proper tab system integration
"""

import os
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal, Qt

##Methods list -
# get_current_tab_file_info
# integrate_reload_functions
# quick_reload
# reload_col_file
# reload_current_file
# reload_img_file
# reload_selected_tab
# _handle_reload_completion
# _update_reload_progress

##Classes -
# ReloadThread

class ReloadThread(QThread):
    """Background thread for reloading files"""
    
    progress_updated = pyqtSignal(int, str)
    reload_completed = pyqtSignal(bool, str)
    
    def __init__(self, main_window, file_path: str, file_type: str):
        super().__init__()
        self.main_window = main_window
        self.file_path = file_path
        self.file_type = file_type
        
    def run(self):
        """Run reload in background"""
        try:
            self.progress_updated.emit(10, "Starting reload...")
            
            if self.file_type == 'IMG':
                success = self._reload_img_file()
            elif self.file_type == 'COL':
                success = self._reload_col_file()
            else:
                success = False
            
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
            new_img = IMGFile(self.file_path)
            if not new_img.open():
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
            new_col = COLFile(self.file_path)
            if not new_col.load():
                return False
            
            self.progress_updated.emit(80, "Updating interface...")
            
            # Store new COL reference
            self.main_window.current_col = new_col
            
            return True
            
        except Exception as e:
            print(f"COL reload error: {e}")
            return False


def get_current_tab_file_info(main_window) -> Optional[Dict[str, Any]]:
    """Get file info for currently selected tab"""
    try:
        if not hasattr(main_window, 'main_tab_widget') or not hasattr(main_window, 'open_files'):
            return None
        
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return None
        
        file_info = main_window.open_files.get(current_index)
        if not file_info:
            return None
        
        return {
            'tab_index': current_index,
            'file_type': file_info.get('type'),
            'file_path': file_info.get('file_path'),
            'file_object': file_info.get('file_object'),
            'tab_name': file_info.get('tab_name', f'Tab {current_index}')
        }
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting current tab info: {str(e)}")
        return None


def reload_selected_tab(main_window) -> bool:
    """Reload the file in the currently selected tab - TAB-AWARE VERSION"""
    try:
        # Get current tab file info
        tab_info = get_current_tab_file_info(main_window)
        if not tab_info:
            main_window.log_message("❌ No file loaded in current tab")
            return False
        
        file_path = tab_info['file_path']
        file_type = tab_info['file_type']
        tab_index = tab_info['tab_index']
        
        if not file_path or not os.path.exists(file_path):
            main_window.log_message("❌ Current tab file path is invalid or file doesn't exist")
            return False
        
        # Get current stats for confirmation dialog
        if file_type == 'IMG' and tab_info['file_object']:
            current_entries = len(tab_info['file_object'].entries) if tab_info['file_object'].entries else 0
            stats_text = f"{current_entries} entries"
        elif file_type == 'COL' and tab_info['file_object']:
            current_models = len(tab_info['file_object'].models) if hasattr(tab_info['file_object'], 'models') and tab_info['file_object'].models else 0
            stats_text = f"{current_models} models"
        else:
            stats_text = "Unknown"
        
        # Confirm reload
        filename = os.path.basename(file_path)
        reply = QMessageBox.question(
            main_window, 
            "Reload File",
            f"Reload {filename}?\n\nCurrent: {stats_text}\nThis will refresh the file from disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            main_window.log_message("🔄 Reload cancelled by user")
            return False
        
        main_window.log_message(f"🔄 Reloading {file_type} file in tab {tab_index}: {filename}")
        
        # Start reload thread
        reload_thread = ReloadThread(main_window, file_path, file_type)
        
        # Connect signals with tab-aware completion handler
        reload_thread.progress_updated.connect(
            lambda progress, message: _update_reload_progress(main_window, progress, message)
        )
        reload_thread.reload_completed.connect(
            lambda success, message: _handle_tab_reload_completion(
                main_window, success, message, file_type, tab_index
            )
        )
        
        # Store thread reference to prevent garbage collection
        main_window._reload_thread = reload_thread
        reload_thread.start()
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Tab reload failed: {str(e)}")
        return False


def reload_current_file(main_window) -> bool:
    """Reload current file - UPDATED: Uses tab-aware reload"""
    return reload_selected_tab(main_window)


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
        new_img = IMGFile(file_path)
        
        if new_img.open():
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
        new_col = COLFile(file_path)
        
        if new_col.load():
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
    """Quick reload without confirmation dialog - TAB-AWARE VERSION"""
    try:
        # Get current tab file info
        tab_info = get_current_tab_file_info(main_window)
        if not tab_info:
            main_window.log_message("❌ No file loaded in current tab for quick reload")
            return False
        
        file_path = tab_info['file_path']
        file_type = tab_info['file_type']
        
        if file_type == 'IMG':
            return reload_img_file(main_window, file_path)
        elif file_type == 'COL':
            return reload_col_file(main_window, file_path)
        else:
            main_window.log_message(f"❌ Unsupported file type for reload: {file_type}")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Quick reload error: {str(e)}")
        return False


def _update_reload_progress(main_window, progress: int, message: str):
    """Update reload progress using unified system"""
    try:
        from methods.progressbar_functions import update_progress
        update_progress(main_window, progress, message)
        main_window.log_message(f"🔄 {message}")
    except ImportError:
        # Fallback if unified progress not available
        main_window.log_message(f"🔄 {message}")
    except Exception as e:
        print(f"Progress update error: {e}")


def _handle_tab_reload_completion(main_window, success: bool, message: str, file_type: str, tab_index: int):
    """Handle reload completion with tab system updates"""
    try:
        # Hide progress using unified system
        from methods.progressbar_functions import hide_progress
        if success:
            hide_progress(main_window, "Reload complete")
        else:
            hide_progress(main_window, "Reload failed")
        
        if success:
            main_window.log_message(f"✅ {message}")
            
            # Update the tab's file object with the new loaded object
            if hasattr(main_window, 'open_files') and tab_index in main_window.open_files:
                if file_type == 'IMG' and hasattr(main_window, 'current_img'):
                    main_window.open_files[tab_index]['file_object'] = main_window.current_img
                elif file_type == 'COL' and hasattr(main_window, 'current_col'):
                    main_window.open_files[tab_index]['file_object'] = main_window.current_col
            
            # Update UI based on file type
            if file_type == 'IMG' and hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            elif file_type == 'COL' and hasattr(main_window, '_update_ui_for_loaded_col'):
                main_window._update_ui_for_loaded_col()
                
        else:
            main_window.log_message(f"❌ {message}")
            
            # Show error dialog
            QMessageBox.critical(main_window, "Reload Failed", f"Failed to reload file:\n{message}")
        
        # Clean up thread reference
        if hasattr(main_window, '_reload_thread'):
            delattr(main_window, '_reload_thread')
            
    except Exception as e:
        main_window.log_message(f"❌ Reload completion error: {str(e)}")


def _handle_reload_completion(main_window, success: bool, message: str, file_type: str):
    """Handle reload completion - LEGACY VERSION"""
    try:
        if success:
            main_window.log_message(f"✅ {message}")
            
            # Update UI based on file type
            if file_type == 'IMG' and hasattr(main_window, '_update_ui_for_loaded_img'):
                main_window._update_ui_for_loaded_img()
            elif file_type == 'COL' and hasattr(main_window, '_update_ui_for_loaded_col'):
                main_window._update_ui_for_loaded_col()
                
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
        # Add tab-aware reload methods
        main_window.reload_current_file = lambda: reload_selected_tab(main_window)
        main_window.reload_selected_tab = lambda: reload_selected_tab(main_window)
        main_window.reload_img_file = lambda path: reload_img_file(main_window, path)
        main_window.reload_col_file = lambda path: reload_col_file(main_window, path)
        main_window.quick_reload = lambda: quick_reload(main_window)
        
        # Legacy compatibility
        main_window.reload_table = main_window.reload_current_file
        main_window.refresh_current_file = main_window.reload_current_file
        
        main_window.log_message("✅ Tab-aware reload functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Reload integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'reload_current_file',
    'reload_selected_tab',
    'reload_img_file', 
    'reload_col_file',
    'quick_reload',
    'get_current_tab_file_info',
    'integrate_reload_functions',
    'ReloadThread'
]
