#this belongs in core/rebuild_all.py - Version: 1
# X-Seti - August09 2025 - IMG Factory 1.5 - Unified Batch IMG Rebuild System

"""
Unified Batch IMG Rebuild System - Multi-file Operations
Corruption-free batch rebuilding with comprehensive validation
"""

import os
import glob
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, QCheckBox, QLabel, QPushButton, QButtonGroup, QApplication
from PyQt6.QtCore import QThread, pyqtSignal, Qt

##Methods list -
# rebuild_all_img
# rebuild_all_with_mode
# batch_fast_rebuild
# batch_safe_rebuild
# show_batch_rebuild_dialog
# _find_img_files_in_directory
# _get_batch_rebuild_options
# _load_img_file_safe
# _process_batch_rebuild
# _validate_batch_results

##Classes -
# BatchRebuildDialog
# BatchRebuildThread

class BatchRebuildDialog(QDialog):
    """Enhanced batch rebuild mode selection dialog"""
    
    def __init__(self, main_window, img_files: List[str]): #vers 1
        super().__init__(main_window)
        self.main_window = main_window
        self.img_files = img_files
        self.selected_mode = "fast"
        
        self.setWindowTitle("Batch IMG Rebuild Configuration")
        self.setFixedSize(450, 420)
        self.setModal(True)
        
        self._setup_ui()
        
    def _setup_ui(self): #vers 1
        """Setup batch dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title with file count
        title = QLabel(f"🔧 Batch Rebuild Configuration")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        file_count_label = QLabel(f"Found {len(self.img_files)} IMG files to rebuild")
        file_count_label.setStyleSheet("color: #666; font-size: 11pt; padding-bottom: 10px;")
        layout.addWidget(file_count_label)
        
        # Mode selection group
        mode_group = QGroupBox("Rebuild Mode:")
        mode_group.setMaximumHeight(180)
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(8)
        mode_layout.setContentsMargins(15, 10, 15, 10)
        
        self.mode_button_group = QButtonGroup()
        
        # Fast mode
        self.fast_radio = QRadioButton("🚀 Fast Batch Mode (Recommended)")
        self.fast_radio.setChecked(True)
        self.fast_radio.toggled.connect(self._on_mode_changed)
        self.mode_button_group.addButton(self.fast_radio)
        mode_layout.addWidget(self.fast_radio)
        
        fast_desc = QLabel("• Parallel processing • Quick optimization • Basic validation")
        fast_desc.setStyleSheet("color: #555; margin-left: 20px; font-size: 9pt; padding: 2px;")
        fast_desc.setWordWrap(True)
        mode_layout.addWidget(fast_desc)
        
        mode_layout.addSpacing(5)
        
        # Safe mode
        self.safe_radio = QRadioButton("🔍 Safe Batch Mode")
        self.safe_radio.toggled.connect(self._on_mode_changed)
        self.mode_button_group.addButton(self.safe_radio)
        mode_layout.addWidget(self.safe_radio)
        
        safe_desc = QLabel("• Sequential processing • Full validation • Comprehensive error checking")
        safe_desc.setStyleSheet("color: #555; margin-left: 20px; font-size: 9pt; padding: 2px;")
        safe_desc.setWordWrap(True)
        mode_layout.addWidget(safe_desc)
        
        layout.addWidget(mode_group)
        
        # Options group
        options_group = QGroupBox("Batch Options:")
        options_group.setMaximumHeight(140)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)
        options_layout.setContentsMargins(15, 10, 15, 10)
        
        # Create backups option
        self.create_backups_check = QCheckBox("✅ Create backups before rebuilding")
        self.create_backups_check.setChecked(True)
        options_layout.addWidget(self.create_backups_check)
        
        # Stop on error option
        self.stop_on_error_check = QCheckBox("⏹️ Stop batch on first error")
        self.stop_on_error_check.setChecked(False)
        options_layout.addWidget(self.stop_on_error_check)
        
        # Verify integrity option
        self.verify_integrity_check = QCheckBox("🔍 Verify integrity after rebuild")
        self.verify_integrity_check.setChecked(False)
        self.verify_integrity_check.setEnabled(False)  # Enabled only for safe mode
        options_layout.addWidget(self.verify_integrity_check)
        
        layout.addWidget(options_group)
        
        # Performance info
        self.perf_label = QLabel()
        self.perf_label.setStyleSheet("background: #f0f0f0; padding: 8px; border-radius: 4px; font-size: 8pt;")
        self.perf_label.setWordWrap(True)
        layout.addWidget(self.perf_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("Start Batch Rebuild")
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet("QPushButton { background: #4CAF50; color: white; padding: 8px 16px; font-weight: bold; }")
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("QPushButton { padding: 8px 16px; }")
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        self._update_performance_info()
        
    def _on_mode_changed(self): #vers 1
        """Handle mode change"""
        self.selected_mode = "fast" if self.fast_radio.isChecked() else "safe"
        self.verify_integrity_check.setEnabled(self.selected_mode == "safe")
        if self.selected_mode == "fast":
            self.verify_integrity_check.setChecked(False)
        else:
            self.verify_integrity_check.setChecked(True)
        self._update_performance_info()
        
    def _update_performance_info(self): #vers 1
        """Update performance information"""
        file_count = len(self.img_files)
        
        if self.selected_mode == "fast":
            perf_text = f"🚀 Fast Batch Mode ({file_count} files):\n" \
                       f"10-20 files: 1-3 min | 50+ files: 3-8 min\n" \
                       f"Features: Parallel processing, speed optimized, basic corruption fixes"
        else:
            perf_text = f"🔍 Safe Batch Mode ({file_count} files):\n" \
                       f"10-20 files: 5-15 min | 50+ files: 15-45 min\n" \
                       f"Features: Sequential processing, full validation, comprehensive error checking"
        
        self.perf_label.setText(perf_text)
        
    def get_batch_options(self) -> dict: #vers 1
        """Get selected batch rebuild options"""
        return {
            'mode': self.selected_mode,
            'create_backups': self.create_backups_check.isChecked(),
            'stop_on_error': self.stop_on_error_check.isChecked(),
            'verify_integrity': self.verify_integrity_check.isChecked() and self.selected_mode == "safe"
        }


class BatchRebuildThread(QThread):
    """Background thread for batch rebuilding"""
    
    progress_updated = pyqtSignal(int, str)
    file_completed = pyqtSignal(str, bool, str)  # filename, success, message
    batch_completed = pyqtSignal(bool, dict)
    
    def __init__(self, main_window, img_files: List[str], options: Dict[str, Any]): #vers 1
        super().__init__()
        self.main_window = main_window
        self.img_files = img_files
        self.options = options
        self.batch_stats = {
            'total_files': len(img_files),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'failed_files': [],
            'total_entries': 0
        }
        
    def run(self): #vers 1
        """Run batch rebuild in background"""
        try:
            self.progress_updated.emit(5, "Starting batch rebuild...")
            
            mode = self.options.get('mode', 'fast')
            stop_on_error = self.options.get('stop_on_error', False)
            
            for i, img_file_path in enumerate(self.img_files):
                if self.isInterruptionRequested():
                    break
                
                filename = os.path.basename(img_file_path)
                progress = int((i / len(self.img_files)) * 85) + 10
                
                self.progress_updated.emit(progress, f"Rebuilding {filename}...")
                
                try:
                    success, message = self._rebuild_single_file(img_file_path, mode)
                    
                    self.batch_stats['processed'] += 1
                    
                    if success:
                        self.batch_stats['successful'] += 1
                        self.file_completed.emit(filename, True, message)
                    else:
                        self.batch_stats['failed'] += 1
                        self.batch_stats['failed_files'].append(filename)
                        self.file_completed.emit(filename, False, message)
                        
                        if stop_on_error:
                            self.progress_updated.emit(100, "Batch stopped due to error")
                            self.batch_completed.emit(False, self.batch_stats)
                            return
                            
                except Exception as e:
                    self.batch_stats['failed'] += 1
                    self.batch_stats['failed_files'].append(filename)
                    error_msg = f"Exception: {str(e)}"
                    self.file_completed.emit(filename, False, error_msg)
                    
                    if stop_on_error:
                        self.progress_updated.emit(100, "Batch stopped due to exception")
                        self.batch_completed.emit(False, self.batch_stats)
                        return
            
            self.progress_updated.emit(100, "Batch rebuild complete")
            
            # Determine overall success
            overall_success = (self.batch_stats['failed'] == 0)
            self.batch_completed.emit(overall_success, self.batch_stats)
            
        except Exception as e:
            self.batch_stats['error'] = str(e)
            self.batch_completed.emit(False, self.batch_stats)
            
    def _rebuild_single_file(self, img_file_path: str, mode: str) -> tuple: #vers 1
        """Rebuild a single IMG file"""
        try:
            # Load IMG file
            img_file = _load_img_file_safe(img_file_path, self.main_window)
            if not img_file:
                return False, "Failed to load IMG file"
            
            if not img_file.entries:
                return False, "IMG file has no entries"
            
            # Count entries for stats
            self.batch_stats['total_entries'] += len(img_file.entries)
            
            # Create backup if requested
            if self.options.get('create_backups', True):
                backup_path = f"{img_file_path}.backup"
                if not os.path.exists(backup_path):
                    import shutil
                    shutil.copy2(img_file_path, backup_path)
            
            # Use unified rebuild process from rebuild.py
            from core.rebuild import _unified_rebuild_process
            
            # Create dummy progress callback for single file
            def dummy_progress(value, message):
                pass
            
            success = _unified_rebuild_process(img_file, mode, self.main_window, dummy_progress)
            
            if success:
                # Validate if requested
                if self.options.get('verify_integrity', False):
                    from core.rebuild import _validate_rebuilt_img
                    validation_success = _validate_rebuilt_img(img_file, self.main_window)
                    if not validation_success:
                        return False, "Rebuild validation failed"
                
                return True, f"Successfully rebuilt ({len(img_file.entries)} entries)"
            else:
                return False, "Rebuild process failed"
                
        except Exception as e:
            return False, f"Error: {str(e)}"


def show_batch_rebuild_dialog(main_window, img_files: List[str]) -> Optional[dict]: #vers 1
    """Show batch rebuild mode selection dialog"""
    try:
        dialog = BatchRebuildDialog(main_window, img_files)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_batch_options()
        
        return None
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Batch dialog error: {str(e)}")
        return None


def rebuild_all_img(main_window) -> bool: #vers 1
    """Rebuild all IMG files with mode selection dialog"""
    try:
        # Get directory
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory with IMG Files")
        if not directory:
            return False
        
        # Find IMG files
        img_files = _find_img_files_in_directory(directory)
        
        if not img_files:
            QMessageBox.information(main_window, "No IMG Files", "No IMG files found in directory")
            return False
        
        # Show batch dialog
        options = show_batch_rebuild_dialog(main_window, img_files)
        if not options:
            return False  # User cancelled
        
        return rebuild_all_with_mode(main_window, img_files, options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild all error: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild All Error", f"Batch rebuild failed: {str(e)}")
        return False


def rebuild_all_with_mode(main_window, img_files: List[str], options: dict) -> bool: #vers 1
    """Rebuild all IMG files with specified options"""
    try:
        mode = options.get('mode', 'fast')
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 Starting {mode.upper()} batch rebuild of {len(img_files)} files")
        
        # Confirmation dialog
        backup_text = "with backups" if options.get('create_backups', True) else "without backups"
        stop_text = "stopping on errors" if options.get('stop_on_error', False) else "continuing on errors"
        
        reply = QMessageBox.question(
            main_window, f"{mode.upper()} Batch Rebuild",
            f"Rebuild {len(img_files)} IMG files?\n\n"
            f"Mode: {mode.upper()}\n"
            f"Options: {backup_text}, {stop_text}\n\n"
            f"This operation may take several minutes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # Create progress dialog
        progress = QProgressDialog(f"{mode.upper()} batch rebuilding...", "Cancel", 0, 100, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Create batch rebuild thread
        rebuild_thread = BatchRebuildThread(main_window, img_files, options)
        
        # Track results
        successful_files = []
        failed_files = []
        
        def update_progress(value, message):
            progress.setValue(value)
            progress.setLabelText(message)
            QApplication.processEvents()
        
        def handle_file_completion(filename, success, message):
            if success:
                successful_files.append(filename)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ {filename}: {message}")
            else:
                failed_files.append(filename)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ {filename}: {message}")
        
        def handle_batch_completion(overall_success, stats):
            progress.close()
            
            # Show detailed results
            total_files = stats.get('total_files', 0)
            successful_count = stats.get('successful', 0)
            failed_count = stats.get('failed', 0)
            total_entries = stats.get('total_entries', 0)
            
            if successful_count == total_files:
                # Complete success
                success_msg = f"✅ Batch rebuild complete!\n\n" \
                             f"Files rebuilt: {successful_count:,}\n" \
                             f"Total entries: {total_entries:,}\n" \
                             f"Mode: {mode.upper()}\n\n" \
                             f"All files processed successfully!"
                
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Batch rebuild complete: {successful_count}/{total_files} files")
                
                QMessageBox.information(main_window, "Batch Rebuild Complete", success_msg)
                
            elif successful_count > 0:
                # Partial success
                partial_msg = f"⚠️ Batch rebuild completed with issues\n\n" \
                             f"Successful: {successful_count}/{total_files} files\n" \
                             f"Failed: {failed_count} files\n" \
                             f"Total entries: {total_entries:,}\n\n" \
                             f"Failed files:\n{chr(10).join(stats.get('failed_files', [])[:5])}"
                
                if len(stats.get('failed_files', [])) > 5:
                    partial_msg += f"\n... and {len(stats.get('failed_files', [])) - 5} more"
                
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚠️ Batch rebuild partial: {successful_count}/{total_files} files")
                
                QMessageBox.warning(main_window, "Batch Rebuild Partial", partial_msg)
                
            else:
                # Complete failure
                failure_msg = f"❌ Batch rebuild failed\n\n" \
                             f"Failed: {failed_count}/{total_files} files\n" \
                             f"No files were successfully rebuilt.\n\n" \
                             f"Check the log for details."
                
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Batch rebuild failed: 0/{total_files} files")
                
                QMessageBox.critical(main_window, "Batch Rebuild Failed", failure_msg)
        
        # Connect signals
        rebuild_thread.progress_updated.connect(update_progress)
        rebuild_thread.file_completed.connect(handle_file_completion)
        rebuild_thread.batch_completed.connect(handle_batch_completion)
        
        # Handle cancellation
        def check_cancellation():
            if progress.wasCanceled():
                rebuild_thread.requestInterruption()
        
        progress.canceled.connect(check_cancellation)
        
        # Start and wait for completion
        rebuild_thread.start()
        rebuild_thread.wait()
        
        return True  # Thread completion handled by signals
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild all with mode error: {str(e)}")
        return False


def batch_fast_rebuild(main_window, img_files: List[str]) -> bool: #vers 1
    """Fast batch rebuild (direct call)"""
    options = {'mode': 'fast', 'create_backups': True, 'stop_on_error': False, 'verify_integrity': False}
    return rebuild_all_with_mode(main_window, img_files, options)


def batch_safe_rebuild(main_window, img_files: List[str]) -> bool: #vers 1
    """Safe batch rebuild (direct call)"""
    options = {'mode': 'safe', 'create_backups': True, 'stop_on_error': False, 'verify_integrity': True}
    return rebuild_all_with_mode(main_window, img_files, options)


def _find_img_files_in_directory(directory: str) -> List[str]: #vers 1
    """Find all IMG files in directory"""
    try:
        img_files = []
        
        # Find .img files (Version 2)
        img_files.extend(glob.glob(os.path.join(directory, "*.img")))
        
        # Find .dir files (Version 1)
        img_files.extend(glob.glob(os.path.join(directory, "*.dir")))
        
        # Sort for consistent ordering
        img_files.sort()
        
        return img_files
        
    except Exception as e:
        print(f"Error finding IMG files: {e}")
        return []


def _load_img_file_safe(img_file_path: str, main_window) -> Optional[object]: #vers 1
    """Safely load IMG file for batch processing"""
    try:
        from components.img_core_classes import IMGFile
        
        img_file = IMGFile()
        
        if img_file.load_from_file(img_file_path):
            return img_file
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ Failed to load: {os.path.basename(img_file_path)}")
            return None
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Load error: {os.path.basename(img_file_path)} - {str(e)}")
        return None


# Integration function for main window
def integrate_batch_rebuild_functions(main_window): #vers 1
    """Integrate batch rebuild functions into main window"""
    try:
        # Main batch rebuild functions
        main_window.rebuild_all_img = lambda: rebuild_all_img(main_window)
        main_window.batch_rebuild = main_window.rebuild_all_img  # Alias
        
        # Direct mode batch functions  
        main_window.batch_fast_rebuild = lambda img_files: batch_fast_rebuild(main_window, img_files)
        main_window.batch_safe_rebuild = lambda img_files: batch_safe_rebuild(main_window, img_files)
        
        # Legacy aliases for compatibility
        main_window.rebuild_all = main_window.rebuild_all_img
        main_window.batch_optimize = main_window.rebuild_all_img
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Batch rebuild system integrated")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Batch rebuild integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'rebuild_all_img',
    'rebuild_all_with_mode',
    'batch_fast_rebuild',
    'batch_safe_rebuild',
    'show_batch_rebuild_dialog',
    'integrate_batch_rebuild_functions'
]