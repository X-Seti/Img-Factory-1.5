#this belongs in core/dump.py - Version: 1
# X-Seti - Aug15 2025 - IMG Factory 1.5 - Dump Functions

"""
Dump Functions - Simple dump all entries to folder with crash bug fixes
Fixed version of dump functionality that was causing application crashes
"""

import os
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from methods.export_shared import ExportThread, get_export_folder

##Methods list -
# dump_all_function
# dump_selected_function

def dump_all_function(main_window): #vers 2
    """Dump all entries to Assists/Dump folder - FIXED crash bug"""
    try:
        # CRITICAL: Validate main window state first to prevent crashes
        if not hasattr(main_window, 'current_img'):
            QMessageBox.warning(main_window, "No IMG File", "No IMG file loaded")
            return
            
        if not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # CRITICAL: Validate entries exist and are accessible
        try:
            all_entries = main_window.current_img.entries
            if not all_entries:
                QMessageBox.information(main_window, "No Entries", "No entries to dump")
                return
        except Exception as e:
            QMessageBox.critical(main_window, "Access Error", f"Cannot access IMG entries: {str(e)}")
            return
        
        # CRITICAL: Validate entry count is reasonable to prevent memory issues
        entry_count = len(all_entries)
        if entry_count > 10000:
            reply = QMessageBox.question(
                main_window,
                "Large IMG File",
                f"This IMG contains {entry_count} entries.\n"
                f"Dumping all entries may take significant time and disk space.\n\n"
                f"Continue with dump?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Get Assists folder and create Dump subfolder
        assists_folder = None
        if hasattr(main_window, 'settings'):
            assists_folder = getattr(main_window.settings, 'assists_folder', None)
        
        if not assists_folder or not os.path.exists(assists_folder):
            # Fallback to manual selection
            QMessageBox.warning(
                main_window, 
                "Assists Folder Not Found", 
                "Assists folder not configured.\nPlease select dump destination manually."
            )
            dump_folder = get_export_folder(main_window, "Select Dump Folder")
            if not dump_folder:
                return
        else:
            # Create Dump subfolder in Assists
            dump_folder = os.path.join(assists_folder, "Dump")
            try:
                os.makedirs(dump_folder, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(
                    main_window, 
                    "Folder Creation Error", 
                    f"Cannot create dump folder:\n{dump_folder}\n\nError: {str(e)}"
                )
                return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Dumping {entry_count} entries to {dump_folder}")
        
        # CRITICAL: Validate dump folder is writable to prevent crashes
        try:
            test_file = os.path.join(dump_folder, '.imgfactory_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            QMessageBox.critical(main_window, "Folder Error", 
                               f"Cannot write to dump folder:\n{str(e)}")
            return
        
        # FIXED: Safe dump options that won't cause crashes
        dump_options = {
            'organize_by_type': False,    # Flat structure for dumps
            'use_assists_structure': False,  # Simple dump, no organization
            'overwrite': True,           # Assume overwrite OK for dumps
            'create_log': True,          # Create log for large operations
            'open_folder_after': True    # Open dump folder when done
        }
        
        # Start dump with crash prevention
        _start_safe_dump_with_progress(main_window, all_entries, dump_folder, dump_options)
        
    except Exception as e:
        # CRITICAL: Catch any remaining errors to prevent app crash
        error_msg = f"Dump operation failed: {str(e)}"
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "Dump Error", error_msg)

def dump_selected_function(main_window): #vers 1
    """Dump selected entries to single folder"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get selected entries
        from methods.export_shared import get_selected_entries, validate_export_entries
        selected_entries = get_selected_entries(main_window)
        if not validate_export_entries(selected_entries, main_window):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Preparing to dump {len(selected_entries)} selected entries")
        
        # Get dump folder
        dump_folder = get_export_folder(main_window, "Select Dump Folder for Selected Entries")
        if not dump_folder:
            return
        
        # Dump options for selected entries
        dump_options = {
            'organize_by_type': False,
            'overwrite': True,
            'create_log': False  # Less verbose for smaller dumps
        }
        
        # Start dump
        _start_safe_dump_with_progress(main_window, selected_entries, dump_folder, dump_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump selected error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump selected failed: {str(e)}")

def _start_safe_dump_with_progress(main_window, entries, dump_folder, dump_options): #vers 1
    """Start dump with crash prevention and safe progress handling"""
    try:
        # CRITICAL: Additional validation before starting thread
        if not entries:
            QMessageBox.warning(main_window, "No Entries", "No entries to dump")
            return
        
        # CRITICAL: Validate each entry has required attributes
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
        
        # Create export thread with validated entries
        export_thread = ExportThread(main_window, valid_entries, dump_folder, dump_options)
        
        # CRITICAL: Create progress dialog with proper error handling
        progress_dialog = QProgressDialog("Dump in progress...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        
        # CRITICAL: Safe progress update that won't crash on bad data
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
                    success_msg = f"Dump Complete!\n\nDumped to: Assists/Dump folder\n{message}"
                    QMessageBox.information(main_window, "Dump Complete", success_msg)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ Dump: {message}")
                    
                    # Open dump folder
                    if dump_options.get('open_folder_after', True) and 'dump_folder' in locals():
                        try:
                            import subprocess
                            import platform
                            if platform.system() == "Linux":
                                subprocess.run(["xdg-open", dump_folder])
                            elif platform.system() == "Windows":
                                subprocess.run(["explorer", dump_folder])
                            elif platform.system() == "Darwin":  # macOS
                                subprocess.run(["open", dump_folder])
                        except Exception:
                            pass  # Don't fail if can't open folder
                else:
                    QMessageBox.critical(main_window, "Dump Failed", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Dump: {message}")
            except Exception as e:
                # Last resort error handling
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Dump completion error: {str(e)}")
        
        def safe_handle_cancel():
            try:
                if export_thread and export_thread.isRunning():
                    export_thread.terminate()
                    export_thread.wait(3000)  # Wait max 3 seconds
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("🚫 Dump cancelled by user")
            except Exception:
                pass  # Don't crash on cancel
        
        # CRITICAL: Connect signals with error handling
        try:
            export_thread.progress_updated.connect(safe_update_progress)
            export_thread.export_completed.connect(safe_dump_finished)
            progress_dialog.canceled.connect(safe_handle_cancel)
        except Exception as e:
            QMessageBox.critical(main_window, "Setup Error", f"Failed to setup dump operation: {str(e)}")
            return
        
        # Start dump
        export_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        # CRITICAL: Final error handler to prevent app crash
        error_msg = f"Failed to start dump operation: {str(e)}"
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "Dump Error", error_msg)

__all__ = [
    'dump_all_function',
    'dump_selected_function'
]
