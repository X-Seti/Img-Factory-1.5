def _show_rebuild_stats(main_window, stats: Dict[str, Any]): #vers 2#this belongs in core/rebuild.py - Version: 6
# X-Seti - August05 2025 - IMG Factory 1.5 - Rebuild Functions

"""
IMG Factory Rebuild Functions
Handles rebuilding IMG files to optimize structure and remove fragmentation
"""

import os
import shutil
from typing import Optional, Dict, Any, List, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import QThread, pyqtSignal, Qt

##Methods list -
# integrate_rebuild_functions
# quick_rebuild  
# rebuild_all_img
# rebuild_current_img
# _get_rebuild_options
# _handle_rebuild_completion
# _rebuild_single_file_sync
# _show_rebuild_stats
# _update_rebuild_progress

##Classes -
# RebuildThread

class RebuildThread(QThread):
    """Background thread for rebuilding IMG files"""
    
    progress_updated = pyqtSignal(int, str)
    rebuild_completed = pyqtSignal(bool, str, dict)
    
    def __init__(self, main_window, img_file, output_path: str, options: Dict[str, Any]): #vers 1
        super().__init__()
        self.main_window = main_window
        self.img_file = img_file
        self.output_path = output_path
        self.options = options
        self.rebuild_stats = {}
        
    def run(self): #vers 3
        """Run rebuild in background"""
        try:
            self.progress_updated.emit(5, "Preparing rebuild...")
            
            # Validate IMG file
            if not self.img_file or not self.img_file.entries:
                self.rebuild_completed.emit(False, "No IMG file or entries to rebuild", {})
                return
            
            self.progress_updated.emit(10, "Creating backup..." if self.options.get('create_backup', True) else "Skipping backup...")
            
            # Create backup if requested
            if self.options.get('create_backup', True):
                backup_path = f"{self.img_file.file_path}.backup"
                if not os.path.exists(backup_path):
                    shutil.copy2(self.img_file.file_path, backup_path)
                    self.main_window.log_message(f"✅ Backup created: {os.path.basename(backup_path)}")
                else:
                    self.main_window.log_message(f"ℹ️ Backup already exists: {os.path.basename(backup_path)}")
            else:
                self.main_window.log_message("⚠️ Proceeding without backup as requested")
            
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
    
    def _analyze_img_structure(self): #vers 2
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
    
    def _rebuild_img_file(self) -> bool: #vers 5
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
            
            # Fix: use **options for create_new() call
            creation_options = {
                'initial_size_mb': initial_size
            }
            
            if not new_img.create_new(self.output_path, img_version, **creation_options):
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
                    # Move new file over original
                    temp_path = f"{self.output_path}.temp"
                    shutil.move(self.output_path, temp_path)
                    shutil.move(temp_path, self.output_path)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Rebuild error: {e}")
            return False


def rebuild_current_img(main_window) -> bool: #vers 4
    """Rebuild current IMG file in place"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            main_window.log_message("❌ No IMG file loaded to rebuild")
            QMessageBox.warning(main_window, "No IMG File", "No IMG file is currently loaded.")
            return False
        
        # Get rebuild options from user
        options = _get_rebuild_options(main_window)
        if options is None:
            return False
        
        original_path = main_window.current_img.file_path
        output_path = original_path  # Rebuild in place
        
        # Start rebuild thread
        rebuild_thread = RebuildThread(main_window, main_window.current_img, output_path, options)
        
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

def rebuild_all_img(main_window) -> bool: #vers 4
    """Rebuild all loaded IMG files or current IMG if only one tab"""
    try:
        # Check if we have the tab system and open files
        if not hasattr(main_window, 'open_files') or not main_window.open_files:
            main_window.log_message("❌ No IMG files loaded to rebuild")
            return False
        
        # Get all IMG files from open tabs
        img_files = []
        for tab_index, file_info in main_window.open_files.items():
            if file_info.get('type') == 'IMG' and file_info.get('file_object'):
                img_files.append({
                    'tab_index': tab_index,
                    'file_object': file_info['file_object'],
                    'file_path': file_info.get('file_path', 'Unknown'),
                    'tab_name': file_info.get('tab_name', f'Tab {tab_index}')
                })
        
        if not img_files:
            main_window.log_message("❌ No IMG files found in open tabs")
            return False
        
        if len(img_files) == 1:
            # Only one IMG tab open - just rebuild current
            main_window.log_message("🔧 Only one IMG tab open, rebuilding current file")
            return rebuild_current_img(main_window)
        
        # Multiple IMG files - get user confirmation for batch rebuild
        from PyQt6.QtWidgets import QPushButton
        
        msg_box = QMessageBox(main_window)
        msg_box.setWindowTitle("Rebuild All IMG Files")
        msg_box.setText(f"Found {len(img_files)} IMG files open in tabs.")
        msg_box.setInformativeText("Choose rebuild option for all files:")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        # Add custom buttons
        backup_btn = msg_box.addButton("Rebuild All (With Backups)", QMessageBox.ButtonRole.YesRole)
        no_backup_btn = msg_box.addButton("Rebuild All (No Backups)", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.setDefaultButton(backup_btn)
        msg_box.exec()
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == cancel_btn:
            main_window.log_message("🔄 Rebuild all cancelled by user")
            return False
        
        # Determine backup option
        create_backups = (clicked_button == backup_btn)
        backup_text = "with backups" if create_backups else "without backups"
        main_window.log_message(f"🔧 Starting batch rebuild of {len(img_files)} files {backup_text}")
        
        # Rebuild each file
        success_count = 0
        failed_files = []
        
        for i, img_info in enumerate(img_files):
            try:
                main_window.log_message(f"🔧 Rebuilding {i+1}/{len(img_files)}: {os.path.basename(img_info['file_path'])}")
                
                # Update progress
                if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
                    progress = int((i / len(img_files)) * 100)
                    main_window.gui_layout.show_progress(progress, f"Rebuilding {i+1}/{len(img_files)}")
                
                # Set as current for rebuild
                original_img = main_window.current_img
                main_window.current_img = img_info['file_object']
                
                # Create rebuild options
                options = {
                    'create_backup': create_backups,
                    'optimize_structure': True,
                    'remove_gaps': True,
                    'compress_entries': False,
                    'preserve_order': False
                }
                
                # Rebuild this file (synchronously for batch operation)
                if _rebuild_single_file_sync(main_window, img_info['file_object'], options):
                    success_count += 1
                    main_window.log_message(f"✅ Rebuilt: {os.path.basename(img_info['file_path'])}")
                else:
                    failed_files.append(os.path.basename(img_info['file_path']))
                    main_window.log_message(f"❌ Failed: {os.path.basename(img_info['file_path'])}")
                
                # Restore original current img
                main_window.current_img = original_img
                
            except Exception as e:
                failed_files.append(f"{os.path.basename(img_info['file_path'])} ({str(e)})")
                main_window.log_message(f"❌ Error rebuilding {os.path.basename(img_info['file_path'])}: {str(e)}")
        
        # Clear progress
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(-1, "Ready")
        
        # Show results
        if success_count == len(img_files):
            main_window.log_message(f"✅ Successfully rebuilt all {success_count} IMG files!")
            QMessageBox.information(main_window, "Rebuild Complete", 
                                  f"Successfully rebuilt all {success_count} IMG files!")
        else:
            result_text = f"Rebuilt {success_count}/{len(img_files)} files successfully."
            if failed_files:
                result_text += f"\n\nFailed files:\n" + "\n".join(failed_files)
            
            main_window.log_message(f"⚠️ Batch rebuild completed: {success_count}/{len(img_files)} successful")
            QMessageBox.warning(main_window, "Rebuild Results", result_text)
        
        return success_count > 0
        
    except Exception as e:
        main_window.log_message(f"❌ Rebuild all failed: {str(e)}")
        return False


def quick_rebuild(main_window) -> bool: #vers 3
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
            'compress_entries': False,
            'preserve_order': False
        }
        
        original_path = main_window.current_img.file_path
        output_path = original_path
        
        # Start rebuild thread
        rebuild_thread = RebuildThread(main_window, main_window.current_img, output_path, options)
        
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
        main_window.log_message(f"❌ Quick rebuild failed: {str(e)}")
        return False


def _get_rebuild_options(main_window) -> Optional[Dict[str, Any]]: #vers 3
    """Get rebuild options from user with backup choice"""
    try:
        from PyQt6.QtWidgets import QPushButton
        
        # Create custom message box with three options
        msg_box = QMessageBox(main_window)
        msg_box.setWindowTitle("Rebuild IMG")
        msg_box.setText("This will rebuild the IMG file to optimize structure and remove fragmentation.")
        msg_box.setInformativeText("Choose how to proceed:")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        # Add custom buttons
        backup_btn = msg_box.addButton("Yes (With Backup)", QMessageBox.ButtonRole.YesRole)
        no_backup_btn = msg_box.addButton("No Backup", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        # Set default button
        msg_box.setDefaultButton(backup_btn)
        
        # Execute dialog
        msg_box.exec()
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == cancel_btn:
            main_window.log_message("🔄 Rebuild cancelled by user")
            return None
        elif clicked_button == backup_btn:
            main_window.log_message("🔄 Rebuild with backup selected")
            return {
                'create_backup': True,
                'optimize_structure': True,
                'remove_gaps': True,
                'compress_entries': False,
                'preserve_order': False
            }
        elif clicked_button == no_backup_btn:
            main_window.log_message("⚠️ Rebuild without backup selected")
            return {
                'create_backup': False,
                'optimize_structure': True,
                'remove_gaps': True,
                'compress_entries': False,
                'preserve_order': False
            }
        else:
            # Fallback - shouldn't happen
            main_window.log_message("🔄 Rebuild cancelled (unknown button)")
            return None
        
    except Exception as e:
        main_window.log_message(f"❌ Error getting rebuild options: {str(e)}")
        return None


def _update_rebuild_progress(main_window, progress: int, message: str): #vers 3
    """Update rebuild progress in UI"""
    try:
        main_window.log_message(f"🔧 {message}")
        
        # Update progress bar if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(progress, message)
            
    except Exception as e:
        print(f"Progress update error: {e}")


def _handle_rebuild_completion(main_window, success: bool, message: str, stats: Dict[str, Any], 
                              output_path: str, original_path: str): #vers 3
    """Handle rebuild completion"""
    try:
        # Clear progress bar first
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(-1, "Ready")
        
        if success:
            main_window.log_message(f"✅ {message}")
            
            # Show rebuild statistics
            if stats:
                _show_rebuild_stats(main_window, stats)
            
            # Reload the IMG if rebuilt in place
            if output_path == original_path:
                from core.reload import reload_current_file
                reload_current_file(main_window)
                
        else:
            main_window.log_message(f"❌ {message}")
            
            # Show error dialog
            QMessageBox.critical(main_window, "Rebuild Failed", f"Failed to rebuild IMG:\n{message}")
        
        # Clean up thread reference
        if hasattr(main_window, '_rebuild_thread'):
            delattr(main_window, '_rebuild_thread')
            
    except Exception as e:
        main_window.log_message(f"❌ Rebuild completion error: {str(e)}")


def _rebuild_single_file_sync(main_window, img_file, options: Dict[str, Any]) -> bool: #vers 1
    """Rebuild a single IMG file synchronously for batch operations"""
    try:
        # Create a simplified rebuild that doesn't use threading for batch operations
        # This avoids thread conflicts when rebuilding multiple files
        
        # Create backup if requested
        if options.get('create_backup', True):
            backup_path = f"{img_file.file_path}.backup"
            if not os.path.exists(backup_path):
                shutil.copy2(img_file.file_path, backup_path)
        
        # Use the core rebuild method from save_img_entry
        from core.save_img_entry import rebuild_img_file
        return rebuild_img_file(img_file)
        
    except Exception as e:
        main_window.log_message(f"❌ Sync rebuild error: {str(e)}")
        return False



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


def integrate_rebuild_functions(main_window) -> bool: #vers 4
    """Integrate rebuild functions into main window"""
    try:
        # Add rebuild methods (removed rebuild_img_as reference)
        main_window.rebuild_img = lambda: rebuild_current_img(main_window)
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
    'rebuild_all_img', 
    'quick_rebuild',
    'integrate_rebuild_functions',
    'RebuildThread'
]