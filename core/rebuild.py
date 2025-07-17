#this belongs in core/ rebuild.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - Rebuild Functions

"""
IMG Factory Rebuild Functions
Handles rebuilding IMG files to optimize structure and remove fragmentation
"""

import os
import shutil
from typing import Optional, Dict, Any, List, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import QThread, pyqtSignal, Qt


class RebuildThread(QThread):
    """Background thread for rebuilding IMG files"""
    
    progress_updated = pyqtSignal(int, str)
    rebuild_completed = pyqtSignal(bool, str, dict)
    
    def __init__(self, main_window, img_file, output_path: str, options: Dict[str, Any]):
        super().__init__()
        self.main_window = main_window
        self.img_file = img_file
        self.output_path = output_path
        self.options = options
        self.rebuild_stats = {}
        
    def run(self):
        """Run rebuild in background"""
        try:
            self.progress_updated.emit(5, "Preparing rebuild...")
            
            # Validate IMG file
            if not self.img_file or not self.img_file.entries:
                self.rebuild_completed.emit(False, "No IMG file or entries to rebuild", {})
                return
            
            self.progress_updated.emit(10, "Creating backup...")
            
            # Create backup if requested
            if self.options.get('create_backup', True):
                backup_path = f"{self.img_file.file_path}.backup"
                if not os.path.exists(backup_path):
                    shutil.copy2(self.img_file.file_path, backup_path)
            
            self.progress_updated.emit(20, "Analyzing entries...")
            
            # Analyze current IMG structure
            self._analyze_img_structure()
            
            self.progress_updated.emit(30, "Rebuilding IMG structure...")
            
            # Perform the rebuild
            success = self._rebuild_img_file()
            
            if success:
                self.progress_updated.emit(100, "Rebuild complete")
                self.rebuild_completed.emit(True, "IMG rebuilt successfully", self.rebuild_stats)
            else:
                self.rebuild_completed.emit(False, "Rebuild failed", self.rebuild_stats)
                
        except Exception as e:
            self.rebuild_completed.emit(False, f"Rebuild error: {str(e)}", {})
    
    def _analyze_img_structure(self):
        """Analyze current IMG structure for rebuild statistics"""
        try:
            total_entries = len(self.img_file.entries)
            total_size = sum(entry.size for entry in self.img_file.entries)
            
            # Calculate fragmentation
            sorted_entries = sorted(self.img_file.entries, key=lambda e: e.offset)
            gaps = 0
            gap_size = 0
            
            for i in range(len(sorted_entries) - 1):
                current_end = sorted_entries[i].offset + sorted_entries[i].size
                next_start = sorted_entries[i + 1].offset
                if next_start > current_end:
                    gaps += 1
                    gap_size += (next_start - current_end)
            
            self.rebuild_stats = {
                'original_entries': total_entries,
                'original_size': total_size,
                'gaps_found': gaps,
                'gap_size': gap_size,
                'fragmentation_percent': (gap_size / total_size * 100) if total_size > 0 else 0
            }
            
        except Exception as e:
            print(f"Analysis error: {e}")
            self.rebuild_stats = {'error': str(e)}
    
    def _rebuild_img_file(self) -> bool:
        """Rebuild the IMG file with optimized structure"""
        try:
            from components.img_core_classes import IMGFile, IMGVersion
            
            # Create new IMG file
            new_img = IMGFile()
            
            # Determine IMG version
            img_version = IMGVersion.VERSION_2  # Default
            if hasattr(self.img_file, 'version'):
                img_version = self.img_file.version
            
            # Create new IMG with optimized structure
            initial_size = max(self.rebuild_stats.get('original_size', 0) // (1024 * 1024) + 10, 10)
            
            if not new_img.create_new(self.output_path, img_version, initial_size):
                return False
            
            self.progress_updated.emit(40, "Adding entries...")
            
            # Add entries in optimized order
            total_entries = len(self.img_file.entries)
            
            for i, entry in enumerate(self.img_file.entries):
                try:
                    # Get entry data
                    entry_data = entry.get_data()
                    
                    # Add to new IMG
                    new_entry = new_img.add_entry(entry.name, entry_data)
                    
                    if new_entry:
                        # Preserve metadata if possible
                        if hasattr(entry, 'compression_type'):
                            new_entry.compression_type = entry.compression_type
                        if hasattr(entry, 'version'):
                            new_entry.version = entry.version
                    
                    # Update progress
                    progress = 40 + (i / total_entries) * 50
                    self.progress_updated.emit(int(progress), f"Adding entry {i+1}/{total_entries}: {entry.name}")
                    
                except Exception as e:
                    print(f"Error adding entry {entry.name}: {e}")
                    continue
            
            self.progress_updated.emit(90, "Finalizing rebuild...")
            
            # Save the new IMG
            if new_img.rebuild():
                # Update statistics
                self.rebuild_stats.update({
                    'rebuilt_entries': len(new_img.entries),
                    'rebuilt_size': new_img.get_file_size(),
                    'size_saved': self.rebuild_stats.get('original_size', 0) - new_img.get_file_size()
                })
                
                new_img.close()
                
                # Replace original if same path
                if self.output_path == self.img_file.file_path:
                    self.img_file.close()
                    # File already saved to same location
                
                return True
            else:
                new_img.close()
                return False
                
        except Exception as e:
            print(f"Rebuild error: {e}")
            return False


def rebuild_current_img(main_window, save_as: bool = False) -> bool:
    """Rebuild the currently loaded IMG file"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            main_window.log_message("❌ No IMG file loaded to rebuild")
            return False
        
        current_img = main_window.current_img
        original_path = current_img.file_path
        
        # Determine output path
        if save_as:
            output_path, _ = QFileDialog.getSaveFileName(
                main_window,
                "Rebuild IMG As",
                original_path,
                "IMG Files (*.img);;All Files (*)"
            )
            if not output_path:
                main_window.log_message("🔄 Rebuild cancelled by user")
                return False
        else:
            output_path = original_path
        
        # Get rebuild options
        options = _get_rebuild_options(main_window)
        if options is None:
            return False
        
        filename = os.path.basename(original_path)
        entry_count = len(current_img.entries) if current_img.entries else 0
        
        main_window.log_message(f"🔧 Starting rebuild of {filename} ({entry_count} entries)")
        
        # Start rebuild thread
        rebuild_thread = RebuildThread(main_window, current_img, output_path, options)
        
        # Connect signals
        rebuild_thread.progress_updated.connect(
            lambda progress, message: _update_rebuild_progress(main_window, progress, message)
        )
        rebuild_thread.rebuild_completed.connect(
            lambda success, message, stats: _handle_rebuild_completion(
                main_window, success, message, stats, output_path, original_path
            )
        )
        
        # Store thread reference
        main_window._rebuild_thread = rebuild_thread
        rebuild_thread.start()
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Rebuild initiation failed: {str(e)}")
        return False


def rebuild_img_as(main_window) -> bool:
    """Rebuild IMG with new filename"""
    return rebuild_current_img(main_window, save_as=True)


def rebuild_all_img(main_window) -> bool:
    """Rebuild all loaded IMG files"""
    try:
        # For now, just rebuild current IMG
        # TODO: Implement multiple IMG handling when tab system is ready
        if hasattr(main_window, 'current_img') and main_window.current_img:
            main_window.log_message("🔧 Rebuilding current IMG (rebuild all not yet implemented)")
            return rebuild_current_img(main_window)
        else:
            main_window.log_message("❌ No IMG files loaded to rebuild")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Rebuild all failed: {str(e)}")
        return False


def quick_rebuild(main_window) -> bool:
    """Quick rebuild without dialog confirmation"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            main_window.log_message("❌ No IMG file loaded for quick rebuild")
            return False
        
        # Use default options for quick rebuild
        options = {
            'create_backup': True,
            'optimize_structure': True,
            'remove_gaps': True,
            'compress_entries': False
        }
        
        current_img = main_window.current_img
        output_path = current_img.file_path
        
        filename = os.path.basename(output_path)
        main_window.log_message(f"⚡ Quick rebuilding {filename}")
        
        # Start rebuild thread
        rebuild_thread = RebuildThread(main_window, current_img, output_path, options)
        
        # Connect signals
        rebuild_thread.progress_updated.connect(
            lambda progress, message: _update_rebuild_progress(main_window, progress, message)
        )
        rebuild_thread.rebuild_completed.connect(
            lambda success, message, stats: _handle_rebuild_completion(
                main_window, success, message, stats, output_path, output_path
            )
        )
        
        # Store thread reference
        main_window._rebuild_thread = rebuild_thread
        rebuild_thread.start()
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Quick rebuild failed: {str(e)}")
        return False


def _get_rebuild_options(main_window) -> Optional[Dict[str, Any]]:
    """Get rebuild options from user"""
    try:
        # For now, use default options
        # TODO: Create rebuild options dialog
        
        reply = QMessageBox.question(
            main_window,
            "Rebuild IMG",
            "Rebuild IMG file?\n\nThis will:\n• Optimize file structure\n• Remove fragmentation\n• Create backup\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            main_window.log_message("🔄 Rebuild cancelled by user")
            return None
        
        return {
            'create_backup': True,
            'optimize_structure': True,
            'remove_gaps': True,
            'compress_entries': False,
            'preserve_order': False
        }
        
    except Exception as e:
        main_window.log_message(f"❌ Error getting rebuild options: {str(e)}")
        return None


def _update_rebuild_progress(main_window, progress: int, message: str):
    """Update rebuild progress in UI"""
    try:
        main_window.log_message(f"🔧 {message}")
        
        # Update progress bar if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(progress, message)
            
    except Exception as e:
        print(f"Progress update error: {e}")


def _handle_rebuild_completion(main_window, success: bool, message: str, stats: Dict[str, Any], 
                              output_path: str, original_path: str):
    """Handle rebuild completion"""
    try:
        if success:
            main_window.log_message(f"✅ {message}")
            
            # Show rebuild statistics
            if stats:
                _show_rebuild_stats(main_window, stats)
            
            # Reload the IMG if rebuilt in place
            if output_path == original_path:
                from core.reload import reload_current_file
                reload_current_file(main_window)
            
            # Clear progress
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
                main_window.gui_layout.show_progress(-1, "Ready")
                
        else:
            main_window.log_message(f"❌ {message}")
            
            # Show error dialog
            QMessageBox.critical(main_window, "Rebuild Failed", f"Failed to rebuild IMG:\n{message}")
        
        # Clean up thread reference
        if hasattr(main_window, '_rebuild_thread'):
            delattr(main_window, '_rebuild_thread')
            
    except Exception as e:
        main_window.log_message(f"❌ Rebuild completion error: {str(e)}")


def _show_rebuild_stats(main_window, stats: Dict[str, Any]):
    """Show rebuild statistics to user"""
    try:
        original_entries = stats.get('original_entries', 0)
        rebuilt_entries = stats.get('rebuilt_entries', 0)
        original_size = stats.get('original_size', 0)
        rebuilt_size = stats.get('rebuilt_size', 0)
        size_saved = stats.get('size_saved', 0)
        gaps_found = stats.get('gaps_found', 0)
        fragmentation = stats.get('fragmentation_percent', 0)
        
        # Format sizes
        def format_size(size_bytes):
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        
        stats_text = f"""Rebuild Statistics:

Original: {original_entries} entries, {format_size(original_size)}
Rebuilt:  {rebuilt_entries} entries, {format_size(rebuilt_size)}

Fragmentation removed: {gaps_found} gaps ({fragmentation:.1f}%)
Space saved: {format_size(abs(size_saved))}

IMG structure optimized successfully!"""
        
        QMessageBox.information(main_window, "Rebuild Complete", stats_text)
        
    except Exception as e:
        print(f"Stats display error: {e}")


def integrate_rebuild_functions(main_window) -> bool:
    """Integrate rebuild functions into main window"""
    try:
        # Add rebuild methods
        main_window.rebuild_img = lambda: rebuild_current_img(main_window)
        main_window.rebuild_img_as = lambda: rebuild_img_as(main_window)
        main_window.rebuild_all_img = lambda: rebuild_all_img(main_window)
        main_window.quick_rebuild = lambda: quick_rebuild(main_window)
        
        # Legacy compatibility
        main_window.rebuild_current_img = main_window.rebuild_img
        main_window.optimize_img = main_window.rebuild_img
        
        main_window.log_message("✅ Rebuild functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Rebuild integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'rebuild_current_img',
    'rebuild_img_as',
    'rebuild_all_img',
    'quick_rebuild',
    'integrate_rebuild_functions',
    'RebuildThread'
]