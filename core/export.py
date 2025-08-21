#this belongs in core/export.py - Version: 6
# X-Seti - August19 2025 - IMG Factory 1.5 - Main Export Functions with Working Tab Detection

"""
Main Export Functions - Standard export with full options dialog
UPDATED: Uses the exact same working tab detection from export_via.py
No imports from methods.tab_awareness - self-contained working functions
"""

import os
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import Qt
from methods.export_shared import ExportThread, get_selected_entries, get_export_folder, validate_export_entries

##Methods list -
# export_all_function
# export_selected_function
# get_current_file_from_active_tab
# get_current_file_type_from_tab
# integrate_export_functions

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

def export_selected_function(main_window): #vers 2
    """Export selected entries with full options dialog - USES working export_via.py logic"""
    try:
        # Use the exact same logic as working export_via.py
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type == 'NONE' or not file_object:
            QMessageBox.warning(main_window, "No File", "Current tab does not contain an IMG or COL file")
            return
        
        # Get selected entries based on file type
        if file_type == 'IMG':
            selected_entries = get_selected_entries(main_window)
            if not validate_export_entries(selected_entries, main_window):
                return
        elif file_type == 'COL':
            selected_entries = _get_selected_col_models_from_tab(main_window, file_object)
            if not selected_entries:
                QMessageBox.warning(main_window, "Nothing Selected", 
                    "Please select COL models to export")
                return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Preparing to export {len(selected_entries)} selected {file_type} entries")
        
        # Show export options dialog
        export_folder, export_options = _show_export_options_dialog(main_window, len(selected_entries), file_type)
        if not export_folder:
            return
        
        # Start export based on file type
        if file_type == 'IMG':
            _start_export_with_progress(main_window, selected_entries, export_folder, export_options)
        elif file_type == 'COL':
            _start_col_export_with_progress(main_window, selected_entries, export_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export selected error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")

def export_all_function(main_window): #vers 2
    """Export all entries with options dialog - USES working export_via.py logic"""
    try:
        # Use the exact same logic as working export_via.py
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type == 'NONE' or not file_object:
            QMessageBox.warning(main_window, "No File", "Current tab does not contain an IMG or COL file")
            return
        
        # Get all entries based on file type
        if file_type == 'IMG':
            if not hasattr(file_object, 'entries') or not file_object.entries:
                QMessageBox.warning(main_window, "No Entries", "IMG file has no entries to export")
                return
            all_entries = file_object.entries
        elif file_type == 'COL':
            if not hasattr(file_object, 'models') or not file_object.models:
                QMessageBox.warning(main_window, "No Models", "COL file has no models to export")
                return
            # Convert all COL models to export entries
            all_entries = []
            for i, model in enumerate(file_object.models):
                col_entry = {
                    'name': f"{model.name}.col" if hasattr(model, 'name') and model.name else f"model_{i}.col",
                    'type': 'COL_MODEL',
                    'model': model,
                    'index': i,
                    'col_file': file_object
                }
                all_entries.append(col_entry)
            
        if not validate_export_entries(all_entries, main_window):
            return
        
        # Confirm export all
        reply = QMessageBox.question(
            main_window, 
            f"Export All {file_type} Entries",
            f"Export all {len(all_entries)} entries from this {file_type} file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Preparing to export all {len(all_entries)} {file_type} entries")
        
        # Show export options dialog
        export_folder, export_options = _show_export_options_dialog(main_window, len(all_entries), file_type)
        if not export_folder:
            return
        
        # Start export based on file type
        if file_type == 'IMG':
            _start_export_with_progress(main_window, all_entries, export_folder, export_options)
        elif file_type == 'COL':
            _start_col_export_with_progress(main_window, all_entries, export_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export all error: {str(e)}")
        QMessageBox.critical(main_window, "Export All Error", f"Export all failed: {str(e)}")

def _get_selected_col_models_from_tab(main_window, col_file): #vers 1
    """Get selected COL models from current tab - helper function"""
    selected_models = []
    
    try:
        # Get selected rows from table
        table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
        elif hasattr(main_window, 'entries_table'):
            table = main_window.entries_table
        
        if not table:
            return selected_models
        
        # Get selected rows
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())
        
        # Create COL export entries for selected rows
        if hasattr(col_file, 'models') and col_file.models:
            for row in selected_rows:
                if row < len(col_file.models):
                    model = col_file.models[row]
                    col_entry = {
                        'name': f"{model.name}.col" if hasattr(model, 'name') and model.name else f"model_{row}.col",
                        'type': 'COL_MODEL',
                        'model': model,
                        'index': row,
                        'col_file': col_file
                    }
                    selected_models.append(col_entry)
                    
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting COL models: {str(e)}")
    
    return selected_models

def _show_export_options_dialog(main_window, entry_count, file_type): #vers 1
    """Show export options dialog like export_via.py does"""
    try:
        # Create export options dialog
        dialog = QDialog(main_window)
        dialog.setWindowTitle(f"Export {entry_count} {file_type} Entries - Choose Options")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Info label
        info_msg = f"📤 Ready to export {entry_count} {file_type} entries\n\nChoose your export destination and options:"
        info_label = QLabel(info_msg)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(info_label)

        # Export options
        options_label = QLabel("📁 Export Options:")
        options_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(options_label)

        organize_check = QCheckBox("🗂️ Organize files by type (Models/Textures/Collision folders)")
        organize_check.setChecked(True)
        layout.addWidget(organize_check)

        overwrite_check = QCheckBox("🔄 Overwrite existing files")
        overwrite_check.setChecked(True)
        layout.addWidget(overwrite_check)

        log_check = QCheckBox("📝 Create export log file")
        log_check.setChecked(True)
        layout.addWidget(log_check)

        # Destination buttons
        button_layout = QHBoxLayout()

        assists_btn = QPushButton("📁 Assists Folder")
        assists_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        button_layout.addWidget(assists_btn)

        custom_btn = QPushButton("📂 Choose Folder")
        button_layout.addWidget(custom_btn)

        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Connect buttons
        dialog.result_choice = None
        assists_btn.clicked.connect(lambda: setattr(dialog, 'result_choice', 'assists') or dialog.accept())
        custom_btn.clicked.connect(lambda: setattr(dialog, 'result_choice', 'custom') or dialog.accept())
        cancel_btn.clicked.connect(dialog.reject)

        # Show dialog
        if dialog.exec() != dialog.DialogCode.Accepted:
            return None, None

        # Get user choices
        choice = dialog.result_choice
        export_options = {
            'organize_by_type': organize_check.isChecked(),
            'overwrite': overwrite_check.isChecked(),
            'create_log': log_check.isChecked()
        }

        # Get export folder
        export_folder = None
        if choice == 'assists':
            if hasattr(main_window, 'settings'):
                export_folder = getattr(main_window.settings, 'assists_folder', None)
            if not export_folder or not os.path.exists(export_folder):
                QMessageBox.warning(main_window, "Assists Folder Not Found",
                                  "Assists folder is not configured or doesn't exist.")
                return None, None
            export_options['use_assists_structure'] = True
        elif choice == 'custom':
            export_folder = get_export_folder(main_window, f"Select Export Destination for {file_type} Files")
            if not export_folder:
                return None, None
            export_options['use_assists_structure'] = False

        return export_folder, export_options

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export options dialog error: {str(e)}")
        return None, None

def _start_export_with_progress(main_window, entries, export_folder, export_options): #vers 1
    """Start IMG export with progress dialog"""
    try:
        # Create export thread
        export_thread = ExportThread(main_window, entries, export_folder, export_options)
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Export in progress...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        
        def update_progress(progress, message):
            try:
                if progress_dialog and not progress_dialog.wasCanceled():
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(message)
            except Exception:
                pass
            
        def export_finished(success, message, stats):
            try:
                # Close progress dialog first
                if progress_dialog:
                    progress_dialog.close()
                    progress_dialog.deleteLater()
                
                # Ensure thread is properly stopped
                if export_thread and export_thread.isRunning():
                    export_thread.quit()
                    export_thread.wait(1000)
                
                # Show result dialog
                if success:
                    QMessageBox.information(main_window, "Export Complete", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ {message}")
                else:
                    QMessageBox.critical(main_window, "Export Failed", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ {message}")
                        
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error in export completion: {e}")
        
        def handle_cancel():
            try:
                if export_thread and export_thread.isRunning():
                    export_thread.stop_export()
                    export_thread.quit()
                    export_thread.wait(2000)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("🚫 Export cancelled by user")
            except Exception:
                pass
        
        # Connect signals
        try:
            export_thread.progress_updated.connect(update_progress)
            export_thread.export_completed.connect(export_finished)
            progress_dialog.canceled.connect(handle_cancel)
        except Exception as e:
            QMessageBox.critical(main_window, "Setup Error", f"Failed to setup export operation: {str(e)}")
            return
        
        # Start export
        export_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export thread error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Failed to start export: {str(e)}")

def _start_col_export_with_progress(main_window, col_entries, export_folder, export_options): #vers 1
    """Start COL export with progress"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🛡️ Starting COL export: {len(col_entries)} models")
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Exporting COL models...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()
        
        # Apply organization options for COL
        if export_options.get('organize_by_type', False):
            col_folder = os.path.join(export_folder, 'collision')
            os.makedirs(col_folder, exist_ok=True)
            export_folder = col_folder
        
        exported_count = 0
        failed_count = 0
        total_entries = len(col_entries)
        
        for i, col_entry in enumerate(col_entries):
            if progress_dialog.wasCanceled():
                break
                
            try:
                model_name = col_entry['name']
                output_path = os.path.join(export_folder, model_name)
                
                # Update progress
                progress = int((i / total_entries) * 100)
                progress_dialog.setValue(progress)
                progress_dialog.setLabelText(f"Exporting {model_name}...")
                
                # Create COL file
                if _create_col_file_for_export(col_entry, output_path):
                    exported_count += 1
                    if hasattr(main_window, 'log_message') and i % 50 == 0:
                        main_window.log_message(f"🛡️ Progress: {exported_count}/{total_entries}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error exporting {col_entry['name']}: {str(e)}")
        
        progress_dialog.close()
        
        # Show results
        if exported_count > 0:
            message = f"Exported {exported_count} COL models to {export_folder}"
            if failed_count > 0:
                message += f"\n{failed_count} models failed to export"
            
            QMessageBox.information(main_window, "COL Export Complete", message)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ COL export complete: {exported_count} success, {failed_count} failed")
        else:
            QMessageBox.warning(main_window, "COL Export Failed", "No COL models were exported successfully")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL export error: {str(e)}")
        QMessageBox.critical(main_window, "COL Export Error", f"COL export failed: {str(e)}")

def _create_col_file_for_export(col_entry, output_path): #vers 1
    """Create a COL file for export operation"""
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

def integrate_export_functions(main_window): #vers 1
    """Integrate export functions into main window with all aliases"""
    try:
        # Add main export functions
        main_window.export_selected_function = lambda: export_selected_function(main_window)
        main_window.export_all_function = lambda: export_all_function(main_window)
        main_window.get_current_file_from_active_tab = lambda: get_current_file_from_active_tab(main_window)
        main_window.get_current_file_type_from_tab = lambda: get_current_file_type_from_tab(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.export_selected = main_window.export_selected_function
        main_window.export_selected_entries = main_window.export_selected_function
        main_window.export_all_entries = main_window.export_all_function
        main_window.export_all = main_window.export_all_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Export functions integrated - using working export_via.py tab detection")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate export functions: {str(e)}")
        return False

__all__ = [
    'get_current_file_from_active_tab',
    'get_current_file_type_from_tab',
    'export_selected_function',
    'export_all_function',
    'integrate_export_functions'
]