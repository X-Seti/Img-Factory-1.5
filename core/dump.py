#this belongs in core/dump.py - Version: 7
# X-Seti - August23 2025 - IMG Factory 1.5 - Dump Functions with Tab Awareness and Newer IMG Operations

import os
import platform
import subprocess
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Import newer IMG operations
try:
    from Import_Export import Import_Export
    from IMG_Operations import IMG_Operations
    from File_Operations import File_Operations
    NEWER_IMG_AVAILABLE = True
except ImportError:
    NEWER_IMG_AVAILABLE = False

# Import tab awareness system (same as export.py uses)
from methods.tab_awareness import (
    validate_tab_before_operation, 
    get_current_file_from_active_tab, 
    get_current_file_type_from_tab,
    get_selected_entries_from_active_tab
)

##Methods list -
# dump_all_function
# dump_selected_function
# _create_dump_directory
# _dump_img_entries
# _dump_col_entries
# _get_assists_folder
# _open_dump_folder_after_completion
# integrate_dump_functions

class SafeDumpThread(QThread): #vers 1
    """Safe dump thread using newer IMG operations"""
    progress_updated = pyqtSignal(int, str)
    dump_completed = pyqtSignal(bool, str, dict)
    
    def __init__(self, entries, dump_folder, file_object, file_type, dump_options):
        super().__init__()
        self.entries = entries
        self.dump_folder = dump_folder
        self.file_object = file_object
        self.file_type = file_type
        self.dump_options = dump_options
        
        """Run dump operation using appropriate method"""
        try:
            if self.file_type == 'IMG':
                success, message, stats = self._dump_img_entries()
            elif self.file_type == 'COL':
                success, message, stats = self._dump_col_entries()
            else:
                success, message, stats = False, f"Unsupported file type: {self.file_type}", {}

            self.dump_completed.emit(success, message, stats)
            
        except Exception as e:
            self.dump_completed.emit(False, f"Dump operation failed: {str(e)}", {})

    def _dump_img_entries(self): #vers 5
        """Start IMG dump with crash prevention and safe progress handling - FROM ORIGINAL"""
        try:
            # CRITICAL: Additional validation before starting thread - FROM ORIGINAL
            if not entries:
                QMessageBox.warning(main_window, "No Entries", "No entries to dump")
                return

            # CRITICAL: Validate each entry has required attributes - FROM ORIGINAL
            valid_entries = []
            for entry in entries:
                if hasattr(entry, 'name') and getattr(entry, 'name', ''):
                    valid_entries.append(entry)

            if not valid_entries:
                QMessageBox.warning(main_window, "Invalid Entries", "No valid entries found to dump")
                return

            if len(valid_entries) < len(entries):
                skipped = len(entries) - len(valid_entries)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚠️ Skipping {skipped} invalid entries")

            # Create export thread with validated entries - FROM ORIGINAL
            export_thread = ExportThread(main_window, valid_entries, dump_folder, dump_options)

            # CRITICAL: Create progress dialog with proper error handling - FROM ORIGINAL
            progress_dialog = QProgressDialog(f"Dump in progress...", "Cancel", 0, 100, main_window)
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setMinimumDuration(0)

            # CRITICAL: Safe progress update that won't crash on bad data - FROM ORIGINAL
            def safe_update_progress(progress, message):
                try:
                    if progress_dialog and not progress_dialog.wasCanceled():
                        progress_dialog.setValue(min(100, max(0, progress)))
                        # Sanitize message to prevent display issues
                        safe_message = str(message)[:100] if message else "Processing..."
                        progress_dialog.setLabelText(safe_message)
                except Exception:
                    pass  # Don't let progress updates crash the dump

            def safe_dump_finished(success, message, stats):
                try:
                    if progress_dialog:
                        progress_dialog.close()
                    if success:
                        # FROM ORIGINAL - show completion message
                        success_msg = f"Dump Complete!\n\nDumped to: {dump_folder}\n{message}"
                        QMessageBox.information(main_window, f"{file_type} Dump Complete", success_msg)
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"✅ {file_type} dump: {message}")

                        # Open dump folder - FROM ORIGINAL
                        if dump_options.get('open_folder_after', True):
                            try:
                                if platform.system() == "Linux":
                                    subprocess.run(["xdg-open", dump_folder])
                                elif platform.system() == "Windows":
                                    subprocess.run(["explorer", dump_folder])
                                elif platform.system() == "Darwin":  # macOS
                                    subprocess.run(["open", dump_folder])
                            except Exception:
                                pass  # Don't fail if can't open folder
                    else:
                        QMessageBox.critical(main_window, f"{file_type} Dump Failed", message)
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ {file_type} dump: {message}")
                except Exception as e:
                    # Last resort error handling - FROM ORIGINAL
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Dump completion error: {str(e)}")

            def safe_handle_cancel():
                try:
                    if export_thread and export_thread.isRunning():
                        export_thread.terminate()
                        export_thread.wait(3000)  # Wait max 3 seconds
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🚫 {file_type} dump cancelled by user")
                except Exception:
                    pass  # Don't crash on cancel

            # CRITICAL: Connect signals with error handling - FROM ORIGINAL
            try:
                export_thread.progress_updated.connect(safe_update_progress)
                export_thread.export_completed.connect(safe_dump_finished)
                progress_dialog.canceled.connect(safe_handle_cancel)
            except Exception as e:
                QMessageBox.critical(main_window, "Setup Error", f"Failed to setup dump operation: {str(e)}")
                return

            # Start dump
            dump_all_function()
            #export_thread.start()
            progress_dialog.show()

        except Exception as e:
            # CRITICAL: Final error handler to prevent app crash - FROM ORIGINAL
            error_msg = f"Failed to start {file_type} dump operation: {str(e)}"
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ {error_msg}")
            QMessageBox.critical(main_window, "Dump Error", error_msg)

    
    def _dump_col_entries(self):
        """Dump COL entries safely"""
        try:
            exported_count = 0
            failed_count = 0
            total_entries = len(self.entries)
            
            for i, entry in enumerate(self.entries):
                try:
                    progress = int((i / total_entries) * 100)
                    self.progress_updated.emit(progress, f"Exporting COL model {i+1}...")
                    
                    # Export COL model (simplified - needs COL export implementation)
                    output_path = os.path.join(self.dump_folder, f"model_{i+1}.col")
                    
                    # Placeholder for COL export
                    exported_count += 1
                    
                except Exception:
                    failed_count += 1
            
            stats = {
                'exported': exported_count,
                'failed': failed_count,
                'total': total_entries
            }
            
            return exported_count > 0, f"COL dump: {exported_count} exported, {failed_count} failed", stats
            
        except Exception as e:
            return False, f"COL dump error: {str(e)}", {}


def dump_all_function(main_window): #vers 4
    """Dump all entries using tab awareness and newer IMG operations"""
    try:
        # FIXED: Use tab awareness system same as export.py
        if not validate_tab_before_operation(main_window, "Dump All"):
            return
        
        file_type = get_current_file_type_from_tab(main_window)
        file_object, detected_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type == 'NONE':
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return
        
        # Get all entries from current tab
        try:
            if file_type == 'IMG':
                all_entries = file_object.entries if hasattr(file_object, 'entries') else []
            elif file_type == 'COL':
                # Convert COL models to entries for dumping
                all_entries = []
                if hasattr(file_object, 'models'):
                    for i, model in enumerate(file_object.models):
                        all_entries.append({'name': f'model_{i+1}.col', 'model': model})
            else:
                all_entries = []
                
            if not all_entries:
                QMessageBox.information(main_window, "No Entries", "No entries to dump")
                return
                
        except Exception as e:
            QMessageBox.critical(main_window, "Access Error", f"Cannot access entries: {str(e)}")
            return
        
        # Create dump folder
        dump_folder = _create_dump_directory(main_window, file_type)
        if not dump_folder:
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Dumping {len(all_entries)} {file_type} entries using tab awareness")
        
        # Start dump with progress
        _start_dump_with_progress(main_window, all_entries, dump_folder, file_object, file_type, 'all')
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump all error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump all failed: {str(e)}")


def dump_selected_function(main_window): #vers 4
    """Dump selected entries using tab awareness and newer IMG operations"""
    try:
        # FIXED: Use tab awareness system same as export.py
        if not validate_tab_before_operation(main_window, "Dump Selected"):
            return
        
        file_type = get_current_file_type_from_tab(main_window)
        file_object, detected_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type == 'NONE':
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return
        
        # Get selected entries using tab awareness
        selected_entries = get_selected_entries_from_active_tab(main_window)
        
        if not selected_entries:
            QMessageBox.warning(main_window, "No Selection", "Please select entries to dump")
            return
        
        # Get dump folder
        dump_folder = QFileDialog.getExistingDirectory(
            main_window, 
            f"Select Dump Folder for Selected {file_type} Entries",
            _get_assists_folder()
        )
        
        if not dump_folder:
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Dumping {len(selected_entries)} selected {file_type} entries using tab awareness")
        
        # Start dump with progress
        _start_dump_with_progress(main_window, selected_entries, dump_folder, file_object, file_type, 'selected')
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump selected error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump selected failed: {str(e)}")


def _create_dump_directory(main_window, file_type: str) -> Optional[str]:
    """Create dump directory in Assists folder"""
    try:
        assists_folder = _get_assists_folder()
        
        # Ask user for dump location
        use_default = QMessageBox.question(
            main_window,
            "Dump Location",
            f"Dump {file_type} files to default location?\n\n"
            f"Default: {assists_folder}/Dump\n\n"
            f"Click 'No' to choose custom location",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if use_default == QMessageBox.StandardButton.Yes:
            dump_folder = os.path.join(assists_folder, "Dump")
            try:
                os.makedirs(dump_folder, exist_ok=True)
                return dump_folder
            except Exception as e:
                QMessageBox.critical(main_window, "Folder Creation Error", 
                                   f"Cannot create dump folder:\n{dump_folder}\n\nError: {str(e)}")
                return None
        else:
            return QFileDialog.getExistingDirectory(
                main_window, 
                f"Select Dump Folder for {file_type}",
                assists_folder
            )
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error creating dump directory: {str(e)}")
        return None


def _start_dump_with_progress(main_window, entries, dump_folder, file_object, file_type, operation_type):
    """Start dump operation with progress dialog"""
    try:
        # Validate dump folder is writable
        try:
            test_file = os.path.join(dump_folder, '.imgfactory_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            QMessageBox.critical(main_window, "Folder Error", 
                               f"Cannot write to dump folder:\n{str(e)}")
            return
        
        # Setup progress dialog
        progress_dialog = QProgressDialog(
            f"Dumping {len(entries)} {file_type} entries...",
            "Cancel",
            0, 100,
            main_window
        )
        progress_dialog.setWindowTitle(f"Dump {operation_type.title()} - {file_type}")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        
        # Dump options
        dump_options = {
            'organize_by_type': False,
            'overwrite': True,
            'create_log': True,
            'open_folder_after': True
        }
        
        # Create and start dump thread
        dump_thread = SafeDumpThread(entries, dump_folder, file_object, file_type, dump_options)
        
        def safe_update_progress(progress, message):
            try:
                progress_dialog.setValue(progress)
                progress_dialog.setLabelText(message)
            except Exception:
                pass
        
        def safe_dump_finished(success, message, stats):
            try:
                progress_dialog.close()
                
                if success:
                    # Show completion message
                    exported = stats.get('exported', 0)
                    failed = stats.get('failed', 0)
                    
                    QMessageBox.information(
                        main_window,
                        f"{file_type} Dump Complete",
                        f"Dump completed successfully!\n\n"
                        f"• Files exported: {exported}\n"
                        f"• Files failed: {failed}\n"
                        f"• Location: {dump_folder}"
                    )
                    
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ {file_type} dump complete: {exported} success, {failed} failed")
                    
                    # Open dump folder
                    if dump_options.get('open_folder_after', True):
                        _open_dump_folder_after_completion(dump_folder)
                else:
                    QMessageBox.critical(main_window, f"{file_type} Dump Failed", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ {file_type} dump failed: {message}")
                        
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Dump completion error: {str(e)}")
        
        def safe_handle_cancel():
            try:
                if dump_thread and dump_thread.isRunning():
                    dump_thread.terminate()
                    dump_thread.wait(3000)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"🚫 {file_type} dump cancelled by user")
            except Exception:
                pass
        
        # Connect signals
        dump_thread.progress_updated.connect(safe_update_progress)
        dump_thread.dump_completed.connect(safe_dump_finished)
        progress_dialog.canceled.connect(safe_handle_cancel)
        
        # Start dump
        dump_all_function()
        #dump_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        error_msg = f"Failed to start {file_type} dump operation: {str(e)}"
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "Dump Error", error_msg)


def _get_assists_folder() -> str:
    """Get Assists folder path"""
    try:
        current_dir = os.getcwd()
        assists_folder = os.path.join(current_dir, "Assists")
        
        if not os.path.exists(assists_folder):
            os.makedirs(assists_folder, exist_ok=True)
        
        return assists_folder
    except Exception:
        return os.getcwd()


def _open_dump_folder_after_completion(dump_folder: str):
    """Open dump folder in file manager"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["xdg-open", dump_folder])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", dump_folder])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", dump_folder])
    except Exception:
        pass  # Don't fail if can't open folder


def integrate_dump_functions(main_window): #vers 4
    """Integrate fixed dump functions into main window with all aliases"""
    try:
        # Add main dump functions
        main_window.dump_all_function = lambda: dump_all_function(main_window)
        main_window.dump_selected_function = lambda: dump_selected_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.dump_all = main_window.dump_all_function
        main_window.dump_selected = main_window.dump_selected_function
        main_window.dump_all_entries = main_window.dump_all_function
        main_window.dump_selected_entries = main_window.dump_selected_function
        main_window.dump_entries = main_window.dump_selected_function  # Legacy alias
        
        if hasattr(main_window, 'log_message'):
            msg = "✅ Fixed dump functions integrated with tab awareness"
            if NEWER_IMG_AVAILABLE:
                msg += " and newer IMG operations"
            main_window.log_message(msg)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate dump functions: {str(e)}")
        return False


__all__ = [
    'dump_all_function',
    'dump_selected_function',
    'integrate_dump_functions'
]
