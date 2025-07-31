#this belongs in core/ rebuild.py - Version: 5
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


##Method list
# rebuild_current_img
# rebuild_img_as
# rebuild_all_img
# quick_rebuild
# integrate_rebuild_functions
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
        
    def run(self): #vers 2
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
    
    def _rebuild_img_file(self) -> bool: #vers 4
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


    def rebuild_all_img(self): #vers 2
        """Rebuild all IMG files in current directory or selected directory"""
        try:
            # Get base directory - use current IMG directory or let user choose
            if self.current_img and hasattr(self.current_img, 'file_path'):
                base_dir = os.path.dirname(self.current_img.file_path)
                use_current_dir = QMessageBox.question(
                    self, "Rebuild All IMG Files",
                    f"Rebuild all IMG files in current directory?\n\n{base_dir}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )

                if use_current_dir == QMessageBox.StandardButton.Cancel:
                    return
                elif use_current_dir == QMessageBox.StandardButton.No:
                    base_dir = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
                    if not base_dir:
                        return
            else:
                base_dir = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
                if not base_dir:
                    return

            # Find all IMG files in directory
            try:
                img_files = [f for f in os.listdir(base_dir) if f.lower().endswith('.img')]
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot access directory: {str(e)}")
                return

            if not img_files:
                QMessageBox.information(self, "No IMG Files", "No IMG files found in selected directory")
                return

            # Show confirmation with file list
            file_list = "\n".join(img_files[:10])
            if len(img_files) > 10:
                file_list += f"\n... and {len(img_files) - 10} more files"

            reply = QMessageBox.question(
                self, "Confirm Rebuild All",
                f"Rebuild {len(img_files)} IMG files?\n\nFiles to rebuild:\n{file_list}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Perform rebuild operation
            self.log_message(f"🔧 Starting rebuild of {len(img_files)} IMG files...")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Rebuilding IMG files...")

            rebuilt_count = 0
            failed_files = []

            for i, img_file in enumerate(img_files):
                file_path = os.path.join(base_dir, img_file)
                progress = int((i + 1) * 100 / len(img_files))

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Rebuilding {img_file}...")

                self.log_message(f"🔧 Rebuilding {img_file}...")

                try:
                    # Import IMG class and attempt to rebuild
                    from components.img_core_classes import IMGFile

                    # Load IMG file
                    img = IMGFile(file_path)
                    if not img.open():
                        failed_files.append(f"{img_file}: Failed to open")
                        continue

                    # Check if rebuild method exists and attempt rebuild
                    if hasattr(img, 'rebuild'):
                        if img.rebuild():
                            rebuilt_count += 1
                            self.log_message(f"✅ Rebuilt: {img_file}")
                        else:
                            failed_files.append(f"{img_file}: Rebuild method failed")
                    elif hasattr(img, 'save'):
                        # Alternative: try save method
                        if img.save():
                            rebuilt_count += 1
                            self.log_message(f"✅ Saved: {img_file}")
                        else:
                            failed_files.append(f"{img_file}: Save method failed")
                    else:
                        failed_files.append(f"{img_file}: No rebuild/save method available")

                    # Clean up
                    if hasattr(img, 'close'):
                        img.close()

                except Exception as e:
                    failed_files.append(f"{img_file}: {str(e)}")
                    self.log_message(f"❌ Error rebuilding {img_file}: {str(e)}")

            # Hide progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"Rebuild complete: {rebuilt_count}/{len(img_files)}")

            # Show results
            self.log_message(f"✅ Rebuild all complete: {rebuilt_count}/{len(img_files)} files rebuilt")

            if failed_files:
                # Show detailed results with failures
                failed_list = "\n".join(failed_files[:10])
                if len(failed_files) > 10:
                    failed_list += f"\n... and {len(failed_files) - 10} more failures"

                QMessageBox.warning(
                    self, "Rebuild All Results",
                    f"Rebuild completed with some issues:\n\n"
                    f"✅ Successfully rebuilt: {rebuilt_count} files\n"
                    f"❌ Failed: {len(failed_files)} files\n\n"
                    f"Failed files:\n{failed_list}"
                )
            else:
                # All successful
                QMessageBox.information(
                    self, "Rebuild All Complete",
                    f"✅ Successfully rebuilt all {rebuilt_count} IMG files!"
                )

        except Exception as e:
            error_msg = f"Error in rebuild_all_img: {str(e)}"
            self.log_message(f"❌ {error_msg}")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Rebuild all failed")

            QMessageBox.critical(self, "Rebuild All Error", error_msg)


def rebuild_current_img(main_window, save_as: bool = False) -> bool: #vers 4
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

def rebuild_all_img(main_window) -> bool: #vers 3
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


def _get_rebuild_options(main_window) -> Optional[Dict[str, Any]]: #vers 3
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


def _update_rebuild_progress(main_window, progress: int, message: str): #vers 3
    """Update rebuild progress in UI"""
    try:
        main_window.log_message(f"🔧 {message}")
        
        # Update progress bar if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            main_window.gui_layout.show_progress(progress, message)
            
    except Exception as e:
        print(f"Progress update error: {e}")


def rebuild_img_as(main_window) -> bool: #vers 1
    """Rebuild IMG file with new name (Save As functionality)"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "No IMG file is currently loaded.")
            return False

        # Get save path from user
        file_path, _ = QFileDialog.getSaveFileName(
            main_window, "Rebuild IMG As", "",
            "IMG Archives (*.img);;All Files (*)"
        )

        if not file_path:
            return False  # User cancelled

        main_window.log_message(f"Rebuilding IMG as: {os.path.basename(file_path)}")

        # Create rebuild options
        options = {
            'create_backup': False,  # Don't backup when saving as new file
            'optimize_structure': True,
            'remove_gaps': True
        }

        # Start rebuild thread
        rebuild_thread = RebuildThread(main_window, main_window.current_img, file_path, options)

        # Connect progress signals
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
            rebuild_thread.progress_updated.connect(
                lambda progress, status: main_window.gui_layout.show_progress(progress, status)
            )

        # Connect completion signal
        def on_rebuild_complete(success, message, stats): #vers 2
            if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'show_progress'):
                main_window.gui_layout.show_progress(-1, "Complete" if success else "Failed")

            if success:
                main_window.log_message(f"✅ IMG rebuilt successfully as: {os.path.basename(file_path)}")
                _show_rebuild_stats(main_window, stats)

                # Ask if user wants to open the new file
                reply = QMessageBox.question(
                    main_window, "Rebuild Complete",
                    f"IMG rebuilt successfully as {os.path.basename(file_path)}\n\nOpen the new file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Open the new file
                    main_window.open_img_file(file_path)
            else:
                main_window.log_message(f"❌ Rebuild failed: {message}")
                QMessageBox.critical(main_window, "Rebuild Failed", f"Failed to rebuild IMG:\n{message}")

        rebuild_thread.rebuild_completed.connect(on_rebuild_complete)

        # Start rebuild
        rebuild_thread.start()

        return True

    except Exception as e:
        main_window.log_message(f"❌ Error in rebuild as: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild Error", f"Error rebuilding IMG:\n{str(e)}")
        return False

def _handle_rebuild_completion(main_window, success: bool, message: str, stats: Dict[str, Any], 
                              output_path: str, original_path: str): #vers 2
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


def _show_rebuild_stats(main_window, stats: Dict[str, Any]): #vers 2
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


def integrate_rebuild_functions(main_window) -> bool: #vers 3
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
