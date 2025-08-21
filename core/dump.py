#this belongs in core/dump.py - Version: 6
# X-Seti - August19 2025 - IMG Factory 1.5 - Dump Functions with Working Tab Detection

"""
Dump Functions - Simple dump all entries to folder
UPDATED: Uses the exact same working tab detection from export_via.py  
No imports from methods.tab_awareness - self-contained working functions
"""

import os
import platform
import subprocess
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import Qt
from methods.export_shared import ExportThread, get_export_folder, get_selected_entries, validate_export_entries

##Methods list -
# dump_all_function
# dump_selected_function
# get_current_file_from_active_tab
# get_current_file_type_from_tab
# integrate_dump_functions

def get_current_file_from_active_tab(main_window): #vers 1
    """Get current file from active tab - COPIED from working export_via.py"""
    try:
        if not hasattr(main_window, 'main_tab_widget'):
            return None, 'NONE'
            
        current_index = main_window.main_tab_widget.currentIndex()
        if current_index == -1:
            return None, 'NONE'
            
        current_tab = main_window.main_tab_widget.widget(current_index)
        if not current_tab:
            return None, 'NONE'
        
        # Check for IMG file in tab
        if hasattr(current_tab, 'img_file') and current_tab.img_file:
            return current_tab.img_file, 'IMG'
            
        # Check for COL file in tab
        elif hasattr(current_tab, 'col_file') and current_tab.col_file:
            return current_tab.col_file, 'COL'
            
        # Check for file_object attribute (your actual tab structure)
        elif hasattr(current_tab, 'file_object') and current_tab.file_object:
            file_obj = current_tab.file_object
            if hasattr(file_obj, 'entries'):
                return file_obj, 'IMG'
            elif hasattr(file_obj, 'models'):
                return file_obj, 'COL'
                
        # Alternative: check file_data attribute
        elif hasattr(current_tab, 'file_data') and current_tab.file_data:
            file_data = current_tab.file_data
            if hasattr(file_data, 'entries'):
                return file_data, 'IMG'
            elif hasattr(file_data, 'models'):
                return file_data, 'COL'
                
        return None, 'NONE'
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Tab detection error: {str(e)}")
        return None, 'NONE'

def get_current_file_type_from_tab(main_window): #vers 1
    """Get current file type from tab - COPIED from working export_via.py"""
    file_object, file_type = get_current_file_from_active_tab(main_window)
    return file_type

def dump_all_function(main_window): #vers 1
    """Dump all entries to folder - CLEAN: Based on export_via.py pattern"""
    try:
        # Get current tab like export_via.py does
        current_index = main_window.main_tab_widget.currentIndex()
        current_tab = main_window.main_tab_widget.widget(current_index)
        
        if not current_tab:
            QMessageBox.warning(main_window, "No Tab", "No active tab found.")
            return
        
        # DEBUG: Log what's actually in the tab
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 DEBUG Tab {current_index}: {type(current_tab).__name__}")
            
            # List all attributes
            if current_tab:
                attrs = [attr for attr in dir(current_tab) if not attr.startswith('_')]
                main_window.log_message(f"🔍 DEBUG Tab attrs: {attrs[:10]}")
                
                # Check specific attributes
                if hasattr(current_tab, 'file_object'):
                    file_obj = current_tab.file_object
                    main_window.log_message(f"🔍 DEBUG file_object: {type(file_obj).__name__ if file_obj else 'None'}")
                    if file_obj:
                        main_window.log_message(f"🔍 DEBUG has entries: {hasattr(file_obj, 'entries')}")
                        main_window.log_message(f"🔍 DEBUG has models: {hasattr(file_obj, 'models')}")
                        if hasattr(file_obj, 'models'):
                            main_window.log_message(f"🔍 DEBUG models count: {len(file_obj.models) if file_obj.models else 0}")
        
        # Detect file type and get all entries using file_object (like your tabs actually use)
        file_object = None
        file_type = 'NONE'
        all_entries = []
        
        if hasattr(current_tab, 'file_object') and current_tab.file_object:
            file_obj = current_tab.file_object
            if hasattr(file_obj, 'entries') and file_obj.entries:
                file_object = file_obj
                file_type = 'IMG'
                all_entries = file_obj.entries
            elif hasattr(file_obj, 'models') and file_obj.models:
                file_object = file_obj
                file_type = 'COL'
                # Convert all COL models to dump entries
                for i, model in enumerate(file_obj.models):
                    col_entry = {
                        'name': f"{model.name}.col" if hasattr(model, 'name') and model.name else f"model_{i}.col",
                        'type': 'COL_MODEL',
                        'model': model,
                        'index': i,
                        'col_file': file_obj
                    }
                    all_entries.append(col_entry)
        
        if file_type == 'NONE' or not all_entries:
            QMessageBox.warning(main_window, "No File", 
                "Current tab does not contain an IMG or COL file with entries to dump.")
            return
            
        if not validate_export_entries(all_entries, main_window):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Preparing to dump all {len(all_entries)} {file_type} entries")
        
        # Try to get default dump folder from assists folder
        try:
            if hasattr(main_window, 'settings') and main_window.settings:
                assists_folder = getattr(main_window.settings, 'assists_folder', '')
                if assists_folder and os.path.exists(assists_folder):
                    default_dump_folder = os.path.join(assists_folder, 'Dump')
                    os.makedirs(default_dump_folder, exist_ok=True)
                else:
                    default_dump_folder = None
            else:
                default_dump_folder = None
        except:
            default_dump_folder = None
        
        # Get dump folder
        if default_dump_folder:
            reply = QMessageBox.question(
                main_window,
                "Dump Location",
                f"Dump all {len(all_entries)} {file_type} entries to:\n{default_dump_folder}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                dump_folder = default_dump_folder
            elif reply == QMessageBox.StandardButton.No:
                dump_folder = get_export_folder(main_window, f"Select Dump Folder for All {file_type} Entries")
                if not dump_folder:
                    return
            else:
                return
        else:
            dump_folder = get_export_folder(main_window, f"Select Dump Folder for All {file_type} Entries")
            if not dump_folder:
                return
        
        # Dump options
        dump_options = {
            'organize_by_type': False,
            'overwrite': True,
            'create_log': True
        }
        
        # Start dump based on file type
        if file_type == 'IMG':
            _start_safe_dump_with_progress(main_window, all_entries, dump_folder, dump_options, file_type)
        elif file_type == 'COL':
            _start_col_dump_with_progress(main_window, all_entries, dump_folder, dump_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump all error: {str(e)}")
        error_msg = f"Dump operation failed: {str(e)}"
        QMessageBox.critical(main_window, "Dump Error", error_msg)

def dump_selected_function(main_window): #vers 1
    """Dump selected entries to single folder - CLEAN: Based on export_via.py pattern"""
    try:
        # Get current tab like export_via.py does
        current_index = main_window.main_tab_widget.currentIndex()
        current_tab = main_window.main_tab_widget.widget(current_index)
        
        if not current_tab:
            QMessageBox.warning(main_window, "No Tab", "No active tab found.")
            return
        
        # Detect file type and get selected entries using file_object
        file_object = None
        file_type = 'NONE'
        selected_entries = []
        
        if hasattr(current_tab, 'file_object') and current_tab.file_object:
            file_obj = current_tab.file_object
            if hasattr(file_obj, 'entries') and file_obj.entries:
                file_object = file_obj
                file_type = 'IMG'
                selected_entries = get_selected_entries(main_window)
            elif hasattr(file_obj, 'models') and file_obj.models:
                file_object = file_obj
                file_type = 'COL'
                # Get selected COL models
                try:
                    table = None
                    if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
                        table = main_window.gui_layout.table
                    
                    if table:
                        selected_rows = set()
                        for item in table.selectedItems():
                            selected_rows.add(item.row())
                        
                        if selected_rows and hasattr(file_obj, 'models'):
                            for row in selected_rows:
                                if row < len(file_obj.models):
                                    model = file_obj.models[row]
                                    col_entry = {
                                        'name': f"{model.name}.col" if hasattr(model, 'name') and model.name else f"model_{row}.col",
                                        'type': 'COL_MODEL',
                                        'model': model,
                                        'index': row,
                                        'col_file': file_obj
                                    }
                                    selected_entries.append(col_entry)
                except:
                    pass
        
        if file_type == 'NONE':
            QMessageBox.warning(main_window, "No File", "Current tab does not contain an IMG or COL file.")
            return
            
        if not selected_entries:
            QMessageBox.warning(main_window, "Nothing Selected", 
                f"Please select {file_type} entries to dump.")
            return
            
        if not validate_export_entries(selected_entries, main_window):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Preparing to dump {len(selected_entries)} selected {file_type} entries")
        
        # Get dump folder
        dump_folder = get_export_folder(main_window, f"Select Dump Folder for Selected {file_type} Entries")
        if not dump_folder:
            return
        
        # Dump options for selected entries
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

def _start_safe_dump_with_progress(main_window, entries, dump_folder, dump_options, file_type): #vers 1
    """Start IMG dump with crash prevention and safe progress handling"""
    try:
        # Validate entries
        if not entries:
            QMessageBox.warning(main_window, "No Entries", "No entries to dump")
            return
        
        # Validate each entry has required attributes
        valid_entries = []
        for entry in entries:
            if hasattr(entry, 'name') and getattr(entry, 'name', ''):
                valid_entries.append(entry)
        
        if not valid_entries:
            QMessageBox.warning(main_window, "Invalid Entries", "No valid entries found to dump")
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📂 Starting safe dump: {len(valid_entries)} valid {file_type} entries")
        
        # Create progress dialog
        progress_dialog = QProgressDialog(f"Dumping {file_type} entries...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        
        # Create dump thread
        dump_thread = ExportThread(main_window, valid_entries, dump_folder, dump_options)
        
        def update_progress(progress, message):
            try:
                if progress_dialog and not progress_dialog.wasCanceled():
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(message)
            except Exception:
                pass
            
        def dump_finished(success, message, stats):
            try:
                # Close progress dialog first
                if progress_dialog:
                    progress_dialog.close()
                    progress_dialog.deleteLater()
                
                # Ensure thread is properly stopped
                if dump_thread and dump_thread.isRunning():
                    dump_thread.quit()
                    dump_thread.wait(1000)
                
                # Show result dialog
                if success:
                    # Show completion message with folder open option
                    reply = QMessageBox.question(
                        main_window,
                        "Dump Complete",
                        f"{message}\n\nOpen dump folder?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        _open_folder_in_explorer(dump_folder)
                    
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ {message}")
                else:
                    QMessageBox.critical(main_window, "Dump Failed", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ {message}")
                        
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error in dump completion: {e}")
        
        def handle_cancel():
            try:
                if dump_thread and dump_thread.isRunning():
                    dump_thread.stop_export()
                    dump_thread.quit()
                    dump_thread.wait(2000)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("🚫 Dump cancelled by user")
            except Exception:
                pass
        
        # Connect signals
        try:
            dump_thread.progress_updated.connect(update_progress)
            dump_thread.export_completed.connect(dump_finished)
            progress_dialog.canceled.connect(handle_cancel)
        except Exception as e:
            QMessageBox.critical(main_window, "Setup Error", f"Failed to setup dump operation: {str(e)}")
            return
        
        # Start dump
        dump_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump thread error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Failed to start dump: {str(e)}")

def _start_col_dump_with_progress(main_window, col_entries, dump_folder, dump_options): #vers 1
    """Start COL dump with progress"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🛡️ Starting COL dump: {len(col_entries)} models")
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Dumping COL models...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()
        
        dumped_count = 0
        failed_count = 0
        total_entries = len(col_entries)
        
        for i, col_entry in enumerate(col_entries):
            if progress_dialog.wasCanceled():
                break
                
            try:
                model_name = col_entry['name']
                output_path = os.path.join(dump_folder, model_name)
                
                # Update progress
                progress = int((i / total_entries) * 100)
                progress_dialog.setValue(progress)
                progress_dialog.setLabelText(f"Dumping {model_name}...")
                
                # Create COL file
                if _create_col_file_for_dump(col_entry, output_path):
                    dumped_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error dumping {col_entry['name']}: {str(e)}")
        
        progress_dialog.close()
        
        # Show results
        if dumped_count > 0:
            message = f"Dumped {dumped_count} COL models to {dump_folder}"
            if failed_count > 0:
                message += f"\n{failed_count} models failed to dump"
            
            # Show completion with folder open option
            reply = QMessageBox.question(
                main_window,
                "COL Dump Complete", 
                f"{message}\n\nOpen dump folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                _open_folder_in_explorer(dump_folder)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ COL dump complete: {dumped_count} success, {failed_count} failed")
        else:
            QMessageBox.warning(main_window, "COL Dump Failed", "No COL models were dumped successfully")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL dump error: {str(e)}")
        QMessageBox.critical(main_window, "COL Dump Error", f"COL dump failed: {str(e)}")

def _create_col_file_for_dump(col_entry, output_path): #vers 1
    """Create a COL file for dump operation"""
    try:
        col_file = col_entry['col_file']
        
        # Copy the entire original file (fastest method)
        if hasattr(col_file, 'file_path') and os.path.exists(col_file.file_path):
            import shutil
            shutil.copy2(col_file.file_path, output_path)
            return True
        
        # Save entire COL file data
        elif hasattr(col_file, '_build_col_data'):
            col_data = col_file._build_col_data()
            with open(output_path, 'wb') as f:
                f.write(col_data)
            return True
        
        # Use save method
        elif hasattr(col_file, 'save_to_file'):
            return col_file.save_to_file(output_path)
            
        return False
        
    except Exception:
        return False

def _open_folder_in_explorer(folder_path): #vers 1
    """Open folder in system file explorer"""
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", folder_path])
        else:  # Linux and others
            subprocess.call(["xdg-open", folder_path])
    except Exception:
        pass  # Fail silently if can't open folder

def integrate_dump_functions(main_window): #vers 1
    """Integrate dump functions into main window"""
    try:
        # Add main dump functions
        main_window.dump_all_function = lambda: dump_all_function(main_window)
        main_window.dump_selected_function = lambda: dump_selected_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.dump_all = main_window.dump_all_function
        main_window.dump_all_entries = main_window.dump_all_function
        main_window.dump_selected = main_window.dump_selected_function
        main_window.dump_entries = main_window.dump_selected_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Dump functions integrated - clean version based on export_via.py")
        
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
