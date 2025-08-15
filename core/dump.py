#this belongs in core/dump.py - Version: 3
# X-Seti - Aug15 2025 - IMG Factory 1.5 - Dump Functions with COL Support

"""
Dump Functions - Simple dump all entries to folder with crash bug fixes
Based on original implementation with COL file support added
Fixed version that was causing application crashes
"""

import os
import platform
import subprocess
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from methods.export_shared import ExportThread, get_export_folder, get_selected_entries, validate_export_entries
from core.export import get_current_file_type

##Methods list -
# dump_all_function
# dump_selected_function
# integrate_dump_functions

def dump_all_function(main_window): #vers 3
    """Dump all entries to Assists/Dump folder - FIXED crash bug with COL support"""
    try:
        file_type = get_current_file_type(main_window)
        
        if file_type == 'NONE':
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return
        
        # CRITICAL: Validate file state first to prevent crashes
        if file_type == 'IMG':
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
                return
            
            try:
                all_entries = main_window.current_img.entries
                if not all_entries:
                    QMessageBox.information(main_window, "No Entries", "No entries to dump")
                    return
            except Exception as e:
                QMessageBox.critical(main_window, "Access Error", f"Cannot access IMG entries: {str(e)}")
                return
                
        elif file_type == 'COL':
            if not hasattr(main_window, 'current_col') or not main_window.current_col:
                QMessageBox.warning(main_window, "No COL File", "Please open a COL file first")
                return
            
            try:
                # Convert COL models to dump entries
                all_entries = []
                if hasattr(main_window.current_col, 'models'):
                    for i, model in enumerate(main_window.current_col.models):
                        col_entry = {
                            'name': f"{model.name}.col" if hasattr(model, 'name') and model.name else f"model_{i}.col",
                            'type': 'COL_MODEL',
                            'model': model,
                            'index': i,
                            'col_file': main_window.current_col
                        }
                        all_entries.append(col_entry)
                
                if not all_entries:
                    QMessageBox.information(main_window, "No COL Models", "No COL models to dump")
                    return
            except Exception as e:
                QMessageBox.critical(main_window, "COL Access Error", f"Cannot access COL models: {str(e)}")
                return
        
        # CRITICAL: Validate entry count is reasonable to prevent memory issues
        entry_count = len(all_entries)
        if entry_count > 10000:
            reply = QMessageBox.question(
                main_window,
                f"Large {file_type} File",
                f"This {file_type} contains {entry_count} entries.\n"
                f"Dumping all entries may take significant time and disk space.\n\n"
                f"Continue with dump?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Get Assists folder and create Dump subfolder - FROM ORIGINAL
        assists_folder = None
        if hasattr(main_window, 'settings'):
            assists_folder = getattr(main_window.settings, 'assists_folder', None)
        
        if not assists_folder or not os.path.exists(assists_folder):
            # Fallback to manual selection - FROM ORIGINAL
            QMessageBox.warning(
                main_window, 
                "Assists Folder Not Found", 
                "Assists folder not configured.\nPlease select dump destination manually."
            )
            dump_folder = get_export_folder(main_window, f"Select Dump Folder for {file_type}")
            if not dump_folder:
                return
        else:
            # Create Dump subfolder in Assists - FROM ORIGINAL
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
            main_window.log_message(f"📂 Dumping {entry_count} {file_type} entries to {dump_folder}")
        
        # CRITICAL: Validate dump folder is writable to prevent crashes - FROM ORIGINAL
        try:
            test_file = os.path.join(dump_folder, '.imgfactory_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            QMessageBox.critical(main_window, "Folder Error", 
                               f"Cannot write to dump folder:\n{str(e)}")
            return
        
        # FIXED: Safe dump options that won't cause crashes - FROM ORIGINAL
        dump_options = {
            'organize_by_type': False,    # Flat structure for dumps
            'use_assists_structure': False,  # Simple dump, no organization
            'overwrite': True,           # Assume overwrite OK for dumps
            'create_log': True,          # Create log for large operations
            'open_folder_after': True    # Open dump folder when done
        }
        
        # Start dump with crash prevention based on file type
        if file_type == 'IMG':
            _start_safe_dump_with_progress(main_window, all_entries, dump_folder, dump_options, file_type)
        elif file_type == 'COL':
            _start_col_dump_with_progress(main_window, all_entries, dump_folder, dump_options)
        
    except Exception as e:
        # CRITICAL: Catch any remaining errors to prevent app crash - FROM ORIGINAL
        error_msg = f"Dump operation failed: {str(e)}"
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "Dump Error", error_msg)

def dump_selected_function(main_window): #vers 2
    """Dump selected entries to single folder - works with IMG or COL"""
    try:
        file_type = get_current_file_type(main_window)
        
        if file_type == 'NONE':
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return
        
        # Get selected entries - FROM ORIGINAL
        selected_entries = get_selected_entries(main_window)
        if not validate_export_entries(selected_entries, main_window):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Preparing to dump {len(selected_entries)} selected {file_type} entries")
        
        # Get dump folder - FROM ORIGINAL
        dump_folder = get_export_folder(main_window, f"Select Dump Folder for Selected {file_type} Entries")
        if not dump_folder:
            return
        
        # Dump options for selected entries - FROM ORIGINAL
        dump_options = {
            'organize_by_type': False,
            'overwrite': True,
            'create_log': False  # Less verbose for smaller dumps
        }
        
        # Start dump based on file type
        if file_type == 'IMG':
            _start_safe_dump_with_progress(main_window, selected_entries, dump_folder, dump_options, file_type)
        elif file_type == 'COL':
            _start_col_dump_with_progress(main_window, selected_entries, dump_folder, dump_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump selected error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump selected failed: {str(e)}")

def _start_safe_dump_with_progress(main_window, entries, dump_folder, dump_options, file_type): #vers 2
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
        export_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        # CRITICAL: Final error handler to prevent app crash - FROM ORIGINAL
        error_msg = f"Failed to start {file_type} dump operation: {str(e)}"
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ {error_msg}")
        QMessageBox.critical(main_window, "Dump Error", error_msg)

def _start_col_dump_with_progress(main_window, col_entries, dump_folder, dump_options): #vers 2
    """Start COL dump with progress handling - OPTIMIZED for speed"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🛡️ Starting COL dump: {len(col_entries)} models")
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Dumping COL models...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()
        
        exported_count = 0
        failed_count = 0
        total_entries = len(col_entries)
        
        # OPTIMIZED: Batch process with reduced UI updates
        for i, col_entry in enumerate(col_entries):
            if progress_dialog.wasCanceled():
                break
                
            try:
                model_name = col_entry['name']
                output_path = os.path.join(dump_folder, model_name)
                
                # Update progress every 10 items or for small batches - OPTIMIZED
                if i % 10 == 0 or total_entries < 50:
                    progress = int((i / total_entries) * 100)
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(f"Dumping {model_name}...")
                
                # Create individual COL file for this model - OPTIMIZED
                from core.export import _create_single_model_col_file_optimized
                if _create_single_model_col_file_optimized(col_entry, output_path):
                    exported_count += 1
                    # Reduced logging frequency - OPTIMIZED
                    if hasattr(main_window, 'log_message') and i % 50 == 0:
                        main_window.log_message(f"🛡️ Dump progress: {exported_count}/{total_entries}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error dumping {col_entry['name']}: {str(e)}")
        
        progress_dialog.close()
        
        # Show results - FROM ORIGINAL STYLE
        if exported_count > 0:
            message = f"Dumped {exported_count} COL models to {dump_folder}"
            if failed_count > 0:
                message += f"\n{failed_count} models failed to dump"
            
            QMessageBox.information(main_window, "COL Dump Complete", message)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ COL dump complete: {exported_count} success, {failed_count} failed")
            
            # Try to open dump folder - FROM ORIGINAL
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
            QMessageBox.warning(main_window, "COL Dump Failed", "No COL models were dumped successfully")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL dump error: {str(e)}")
        QMessageBox.critical(main_window, "COL Dump Error", f"COL dump failed: {str(e)}")

def integrate_dump_functions(main_window): #vers 1
    """Integrate dump functions into main window with all aliases"""
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
            main_window.log_message("✅ Dump functions integrated with COL support")
        
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