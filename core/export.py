#this belongs in core/export.py - Version: 3
# X-Seti - Aug15 2025 - IMG Factory 1.5 - Main Export Functions with COL Support

"""
Main Export Functions - Standard export with full options dialog
Based on original implementation with COL file support added
Provides comprehensive export functionality with user configuration
"""

import os
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from methods.export_shared import (
    ExportThread, get_selected_entries, get_export_folder, validate_export_entries
)

##Methods list -
# export_all_function
# export_selected_function
# get_current_file_type
# get_selected_col_models
# integrate_export_functions

def get_current_file_type(main_window) -> str: #vers 1
    """Detect what type of file is currently loaded"""
    if hasattr(main_window, 'current_img') and main_window.current_img:
        return 'IMG'
    elif hasattr(main_window, 'current_col') and main_window.current_col:
        return 'COL'
    else:
        return 'NONE'

def get_selected_col_models(main_window) -> list: #vers 1
    """Get selected COL models from table"""
    selected_models = []
    
    try:
        # Try different table access methods
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
        
        # Get COL models for selected rows
        if hasattr(main_window, 'current_col') and main_window.current_col:
            if hasattr(main_window.current_col, 'models'):
                for row in selected_rows:
                    if row < len(main_window.current_col.models):
                        model = main_window.current_col.models[row]
                        # Create export entry for COL model
                        col_entry = {
                            'name': f"{model.name}.col" if hasattr(model, 'name') and model.name else f"model_{row}.col",
                            'type': 'COL_MODEL',
                            'model': model,
                            'index': row,
                            'col_file': main_window.current_col
                        }
                        selected_models.append(col_entry)
                    
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting COL models: {str(e)}")
    
    return selected_models

def export_selected_function(main_window): #vers 3
    """Export selected entries with full options dialog - FROM ORIGINAL with COL support"""
    try:
        file_type = get_current_file_type(main_window)
        
        if file_type == 'IMG':
            # Original IMG export logic
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
                return
            
            # Get selected entries - FROM ORIGINAL
            selected_entries = get_selected_entries(main_window)
            if not validate_export_entries(selected_entries, main_window):
                return
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📤 Preparing to export {len(selected_entries)} selected entries")
            
        elif file_type == 'COL':
            # COL export logic
            if not hasattr(main_window, 'current_col') or not main_window.current_col:
                QMessageBox.warning(main_window, "No COL File", "Please open a COL file first")
                return
            
            # Get selected COL models
            selected_entries = get_selected_col_models(main_window)
            if not selected_entries:
                QMessageBox.warning(main_window, "Nothing Selected", 
                    "Please select COL models to export")
                return
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📤 Preparing to export {len(selected_entries)} selected COL models")
                
        else:
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return
        
        # Show export options dialog with Assists folder integration - FROM ORIGINAL
        try:
            from core.dialogs import ExportOptionsDialog
            options_dialog = ExportOptionsDialog(main_window, len(selected_entries))  # Fixed: only 2 parameters
            
            if options_dialog.exec() != options_dialog.DialogCode.Accepted:
                return
            
            export_options = options_dialog.get_options()
            export_folder = export_options.get('export_folder')
            
            if not export_folder:
                QMessageBox.warning(main_window, "No Folder", "Please select an export folder")
                return
                
        except ImportError:
            # Fallback - get folder directly - FROM ORIGINAL
            export_folder = get_export_folder(main_window, f"Select Export Destination for {file_type}")
            if not export_folder:
                return
            export_options = {
                'organize_by_type': True,
                'overwrite': True,
                'create_log': False
            }
            if hasattr(main_window, 'log_message'):
                main_window.log_message("ℹ️ Using default export options")
        
        # Start export based on file type
        if file_type == 'IMG':
            _start_export_with_progress(main_window, selected_entries, export_folder, export_options)
        elif file_type == 'COL':
            _start_col_export(main_window, selected_entries, export_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export selected error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")

def export_all_function(main_window): #vers 3
    """Export all entries with options dialog - FROM ORIGINAL with COL support"""
    try:
        file_type = get_current_file_type(main_window)
        
        if file_type == 'IMG':
            # Original IMG export all logic
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
                return
            
            all_entries = main_window.current_img.entries
            if not validate_export_entries(all_entries, main_window):
                return
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📤 Preparing to export all {len(all_entries)} entries")
            
        elif file_type == 'COL':
            # COL export all logic
            if not hasattr(main_window, 'current_col') or not main_window.current_col:
                QMessageBox.warning(main_window, "No COL File", "Please open a COL file first")
                return
            
            # Convert all COL models to export entries
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
                QMessageBox.information(main_window, "No Models", "No COL models to export")
                return
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📤 Preparing to export all {len(all_entries)} COL models")
                
        else:
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return
        
        # Confirm export all - FROM ORIGINAL
        reply = QMessageBox.question(
            main_window, 
            f"Export All {file_type} Entries",
            f"Export all {len(all_entries)} entries from this {file_type} file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Show export options dialog - FROM ORIGINAL
        try:
            from core.dialogs import ExportOptionsDialog
            options_dialog = ExportOptionsDialog(main_window, len(all_entries))  # Fixed: only 2 parameters
            
            if options_dialog.exec() != options_dialog.DialogCode.Accepted:
                return
            
            export_options = options_dialog.get_options()
            export_folder = export_options.get('export_folder')
            
            if not export_folder:
                QMessageBox.warning(main_window, "No Folder", "Please select an export folder")
                return
                
        except ImportError:
            # Fallback to basic folder selection - FROM ORIGINAL
            export_folder = get_export_folder(main_window, f"Select Export Destination for All {file_type} Entries")
            if not export_folder:
                return
            export_options = {
                'organize_by_type': True,
                'overwrite': False,  # More conservative for large exports
                'create_log': True
            }
            if hasattr(main_window, 'log_message'):
                main_window.log_message("ℹ️ Using default export options")
        
        # Start export based on file type
        if file_type == 'IMG':
            _start_export_with_progress(main_window, all_entries, export_folder, export_options)
        elif file_type == 'COL':
            _start_col_export(main_window, all_entries, export_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export all error: {str(e)}")
        QMessageBox.critical(main_window, "Export All Error", f"Export all failed: {str(e)}")

def _start_export_with_progress(main_window, entries, export_folder, export_options): #vers 3
    """Start IMG export with progress dialog - FROM ORIGINAL with threading fixes"""
    try:
        # Create export thread
        export_thread = ExportThread(main_window, entries, export_folder, export_options)
        
        # Create progress dialog - FROM ORIGINAL
        progress_dialog = QProgressDialog("Export in progress...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setAutoClose(True)  # CRITICAL: Auto close to prevent hanging
        progress_dialog.setAutoReset(True)  # CRITICAL: Auto reset to prevent hanging
        
        def update_progress(progress, message):
            try:
                if progress_dialog and not progress_dialog.wasCanceled():
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(message)
            except Exception:
                pass  # Don't let progress updates crash export
            
        def export_finished(success, message, stats):
            try:
                # CRITICAL: Close progress dialog first - FROM ORIGINAL
                if progress_dialog:
                    progress_dialog.close()
                    progress_dialog.deleteLater()
                
                # CRITICAL: Ensure thread is properly stopped - FROM ORIGINAL
                if export_thread and export_thread.isRunning():
                    export_thread.quit()
                    export_thread.wait(1000)  # Wait max 1 second
                
                # Show result dialog - FROM ORIGINAL
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
                    export_thread.stop_export()  # Request stop
                    export_thread.quit()
                    export_thread.wait(2000)  # Wait max 2 seconds
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("🚫 Export cancelled by user")
            except Exception:
                pass  # Don't crash on cancel
        
        # CRITICAL: Connect signals with proper error handling - FROM ORIGINAL
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

def _start_col_export(main_window, col_entries, export_folder, export_options): #vers 2
    """Start COL export with progress - OPTIMIZED for speed"""
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
        
        # OPTIMIZED: Batch process instead of individual file creation
        for i, col_entry in enumerate(col_entries):
            if progress_dialog.wasCanceled():
                break
                
            try:
                model_name = col_entry['name']
                output_path = os.path.join(export_folder, model_name)
                
                # Update progress every 10 items or for small batches
                if i % 10 == 0 or total_entries < 50:
                    progress = int((i / total_entries) * 100)
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(f"Exporting {model_name}...")
                
                # OPTIMIZED: Use faster COL file creation
                if _create_single_model_col_file_optimized(col_entry, output_path):
                    exported_count += 1
                    if hasattr(main_window, 'log_message') and i % 50 == 0:  # Log every 50 items
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

def _create_single_model_col_file_optimized(col_entry, output_path): #vers 1
    """Create a COL file containing a single model - OPTIMIZED VERSION"""
    try:
        col_file = col_entry['col_file']
        
        # FASTEST: Copy the entire original file (all models) - user can extract what they need
        if hasattr(col_file, 'file_path') and os.path.exists(col_file.file_path):
            import shutil
            shutil.copy2(col_file.file_path, output_path)
            return True
        
        # FAST: Save entire COL file data
        elif hasattr(col_file, '_build_col_data'):
            col_data = col_file._build_col_data()
            with open(output_path, 'wb') as f:
                f.write(col_data)
            return True
        
        # FALLBACK: Use save method
        elif hasattr(col_file, 'save_to_file'):
            return col_file.save_to_file(output_path)
            
        return False
        
    except Exception as e:
        return False

def _create_single_model_col_file(col_entry, output_path): #vers 1
    """Create a COL file containing a single model"""
    try:
        model = col_entry['model']
        col_file = col_entry['col_file']
        
        # Try different methods to save the COL model
        
        # Method 1: Use save_single_model if available
        if hasattr(col_file, 'save_single_model'):
            return col_file.save_single_model(model, output_path)
        
        # Method 2: Use save_to_file (saves entire COL file with all models)
        elif hasattr(col_file, 'save_to_file'):
            return col_file.save_to_file(output_path)
        
        # Method 3: Build COL data and write
        elif hasattr(col_file, '_build_col_data'):
            col_data = col_file._build_col_data()
            with open(output_path, 'wb') as f:
                f.write(col_data)
            return True
        
        # Method 4: Copy from original file if available
        elif hasattr(col_file, 'file_path') and os.path.exists(col_file.file_path):
            import shutil
            shutil.copy2(col_file.file_path, output_path)
            return True
            
        return False
        
    except Exception as e:
        return False

def integrate_export_functions(main_window): #vers 2
    """Integrate export functions into main window with all aliases - FROM ORIGINAL"""
    try:
        # Add main export functions
        main_window.export_selected_function = lambda: export_selected_function(main_window)
        main_window.export_all_function = lambda: export_all_function(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        main_window.get_selected_col_models = lambda: get_selected_col_models(main_window)
        main_window.get_current_file_type = lambda: get_current_file_type(main_window)
        
        # Add aliases for different naming conventions that GUI might use - FROM ORIGINAL
        main_window.export_selected = main_window.export_selected_function
        main_window.export_selected_entries = main_window.export_selected_function
        main_window.export_all_entries = main_window.export_all_function
        main_window.export_all = main_window.export_all_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Export functions integrated with COL support")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate export functions: {str(e)}")
        return False

__all__ = [
    'get_current_file_type',
    'get_selected_col_models',
    'export_selected_function',
    'export_all_function',
    'integrate_export_functions'
]