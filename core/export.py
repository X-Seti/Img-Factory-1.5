#this belongs in core/export.py - Version: 3
# X-Seti - August23 2025 - IMG Factory 1.5 - Clean Export Functions with Tab Awareness

"""
Clean Export Functions - Simplified and uses tab awareness like export_via.py
Supports both IMG and COL file export with proper multi-tab detection
"""

import os
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from PyQt6.QtCore import QThread, pyqtSignal

# Use same tab awareness imports as export_via.py (this works!)
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab, get_current_file_type_from_tab

##Methods list -
# export_selected_function
# export_all_function
# _export_img_selected
# _export_img_all
# _export_col_selected
# _export_col_all
# _get_selected_entries_from_tab
# integrate_export_functions

def export_selected_function(main_window): #vers 3
    """Export selected entries - CLEAN: Uses tab awareness like export_via.py"""
    try:
        # Copy exact pattern from working export_via.py
        if not validate_tab_before_operation(main_window, "Export Selected"):
            return
        
        file_type = get_current_file_type_from_tab(main_window)
        
        if file_type == 'IMG':
            _export_img_selected(main_window)
        elif file_type == 'COL':
            _export_col_selected(main_window)
        else:
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export selected error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")


def export_all_function(main_window): #vers 3
    """Export all entries - CLEAN: Uses tab awareness like export_via.py"""
    try:
        if not validate_tab_before_operation(main_window, "Export All"):
            return
        
        file_type = get_current_file_type_from_tab(main_window)
        
        if file_type == 'IMG':
            _export_img_all(main_window)
        elif file_type == 'COL':
            _export_col_all(main_window)
        else:
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export all error: {str(e)}")


def _export_img_selected(main_window): #vers 1
    """Export selected IMG entries"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'IMG':
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # Get selected entries from current tab
        selected_entries = _get_selected_entries_from_tab(main_window)
        
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export")
            return
        
        # Choose export directory
        export_dir = QFileDialog.getExistingDirectory(
            main_window, f"Export {len(selected_entries)} Selected Entries")
        
        if not export_dir:
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Exporting {len(selected_entries)} IMG entries to: {export_dir}")
        
        # Export each selected entry as separate file
        success_count = 0
        for entry in selected_entries:
            try:
                # Get entry data
                if hasattr(entry, 'get_data'):
                    data = entry.get_data()
                elif hasattr(entry, '_cached_data') and entry._cached_data:
                    data = entry._cached_data
                else:
                    # Read from IMG file
                    data = file_object.read_entry_data(entry)
                
                if data:
                    output_path = os.path.join(export_dir, entry.name)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    success_count += 1
                    
            except Exception as entry_error:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to export {entry.name}: {entry_error}")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Successfully exported {success_count}/{len(selected_entries)} entries")
        
        QMessageBox.information(main_window, "Export Complete", 
            f"Successfully exported {success_count} of {len(selected_entries)} entries")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG export error: {str(e)}")


def _export_img_all(main_window): #vers 1
    """Export all IMG entries"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'IMG':
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        if not hasattr(file_object, 'entries') or not file_object.entries:
            QMessageBox.information(main_window, "No Entries", "IMG file has no entries to export")
            return
        
        all_entries = file_object.entries
        
        # Choose export directory
        export_dir = QFileDialog.getExistingDirectory(
            main_window, f"Export All {len(all_entries)} Entries")
        
        if not export_dir:
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Exporting ALL {len(all_entries)} IMG entries to: {export_dir}")
        
        # Show progress dialog for all entries
        progress = QProgressDialog(f"Exporting {len(all_entries)} entries...", "Cancel", 0, len(all_entries), main_window)
        progress.setModal(True)
        
        success_count = 0
        for i, entry in enumerate(all_entries):
            if progress.wasCanceled():
                break
                
            progress.setValue(i)
            progress.setLabelText(f"Exporting {entry.name}...")
            
            try:
                # Get entry data
                if hasattr(entry, 'get_data'):
                    data = entry.get_data()
                elif hasattr(entry, '_cached_data') and entry._cached_data:
                    data = entry._cached_data
                else:
                    data = file_object.read_entry_data(entry)
                
                if data:
                    output_path = os.path.join(export_dir, entry.name)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    success_count += 1
                    
            except Exception as entry_error:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to export {entry.name}: {entry_error}")
        
        progress.close()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Successfully exported {success_count}/{len(all_entries)} entries")
        
        QMessageBox.information(main_window, "Export Complete", 
            f"Successfully exported {success_count} of {len(all_entries)} entries")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG export all error: {str(e)}")


def _export_col_selected(main_window): #vers 1
    """Export selected COL models"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'COL':
            QMessageBox.warning(main_window, "No COL File", "Current tab does not contain a COL file")
            return
        
        # Get selected COL models from current tab
        selected_models = _get_selected_col_models_from_tab(main_window, file_object)
        
        if not selected_models:
            QMessageBox.information(main_window, "No Selection", "Please select collision models to export")
            return
        
        # Ask: separate files or combined COL file?
        reply = QMessageBox.question(main_window, "COL Export Options",
            f"Export {len(selected_models)} collision models as:\n\n"
            "• Separate COL files (one per model)\n"
            "• Single combined COL file\n\n"
            "Choose 'Yes' for separate files, 'No' for combined file",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        
        if reply == QMessageBox.StandardButton.Yes:
            # Export as separate files
            export_dir = QFileDialog.getExistingDirectory(main_window, "Export COL Models")
            if export_dir:
                _export_col_models_separate(main_window, selected_models, export_dir)
        else:
            # Export as combined file
            output_path, _ = QFileDialog.getSaveFileName(
                main_window, "Save Combined COL File", "combined_models.col", "COL Files (*.col);;All Files (*)")
            if output_path:
                _export_col_models_combined(main_window, selected_models, output_path)
                
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL export error: {str(e)}")


def _export_col_all(main_window): #vers 1
    """Export all COL models"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if not file_object or file_type != 'COL':
            QMessageBox.warning(main_window, "No COL File", "Current tab does not contain a COL file")
            return
        
        if not hasattr(file_object, 'models') or not file_object.models:
            QMessageBox.information(main_window, "No Models", "COL file has no models to export")
            return
        
        all_models = file_object.models
        
        # Ask: separate files or combined COL file?
        reply = QMessageBox.question(main_window, "COL Export All Options",
            f"Export ALL {len(all_models)} collision models as:\n\n"
            "• Separate COL files (one per model)\n"
            "• Single combined COL file\n\n"
            "Choose 'Yes' for separate files, 'No' for combined file",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        
        if reply == QMessageBox.StandardButton.Yes:
            # Export as separate files
            export_dir = QFileDialog.getExistingDirectory(main_window, "Export All COL Models")
            if export_dir:
                _export_col_models_separate(main_window, all_models, export_dir)
        else:
            # Export as combined file
            output_path, _ = QFileDialog.getSaveFileName(
                main_window, "Save Combined COL File", "all_models.col", "COL Files (*.col);;All Files (*)")
            if output_path:
                _export_col_models_combined(main_window, all_models, output_path)
                
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL export all error: {str(e)}")


def _get_selected_entries_from_tab(main_window): #vers 1
    """Get selected entries from current active tab"""
    try:
        # Use existing tab awareness function if available
        if hasattr(main_window, 'get_selected_entries_from_active_tab'):
            return main_window.get_selected_entries_from_active_tab()
        
        # Fallback: try to get from current table
        if hasattr(main_window, 'table'):
            table = main_window.table
            selected_rows = table.selectionModel().selectedRows()
            
            if not selected_rows:
                return []
            
            # Get file object
            file_object, _ = get_current_file_from_active_tab(main_window)
            if not file_object or not hasattr(file_object, 'entries'):
                return []
            
            selected_entries = []
            for index in selected_rows:
                row = index.row()
                if 0 <= row < len(file_object.entries):
                    selected_entries.append(file_object.entries[row])
            
            return selected_entries
        
        return []
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting selected entries: {str(e)}")
        return []


def _get_selected_col_models_from_tab(main_window, col_file): #vers 1
    """Get selected COL models from current active tab"""
    try:
        selected_entries = _get_selected_entries_from_tab(main_window)
        
        if not selected_entries:
            return []
        
        # Convert entry indices to COL models
        selected_models = []
        for entry in selected_entries:
            if hasattr(entry, 'model'):
                selected_models.append(entry.model)
            elif isinstance(entry, int) and 0 <= entry < len(col_file.models):
                selected_models.append(col_file.models[entry])
        
        return selected_models
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting selected COL models: {str(e)}")
        return []


def _export_col_models_separate(main_window, models, export_dir): #vers 1
    """Export COL models as separate files"""
    try:
        from methods.export_col_shared import create_single_col_file
        
        success_count = 0
        for i, model in enumerate(models):
            try:
                model_name = getattr(model, 'name', f'model_{i}')
                output_path = os.path.join(export_dir, f"{model_name}.col")
                
                if create_single_col_file(model, output_path):
                    success_count += 1
                    
            except Exception as model_error:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to export model {i}: {model_error}")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Exported {success_count}/{len(models)} COL models as separate files")
        
        QMessageBox.information(main_window, "COL Export Complete",
            f"Successfully exported {success_count} of {len(models)} models as separate files")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL separate export error: {str(e)}")


def _export_col_models_combined(main_window, models, output_path): #vers 1
    """Export COL models as single combined file"""
    try:
        from methods.export_col_shared import create_combined_col_file
        
        if create_combined_col_file(models, output_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Exported {len(models)} COL models to combined file: {output_path}")
            
            QMessageBox.information(main_window, "COL Export Complete",
                f"Successfully exported {len(models)} models to combined file")
        else:
            QMessageBox.warning(main_window, "Export Failed",
                "Failed to create combined COL file")
                
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL combined export error: {str(e)}")


def integrate_export_functions(main_window): #vers 3
    """Integrate clean export functions - SIMPLIFIED"""
    try:
        # Main export functions
        main_window.export_selected_function = lambda: export_selected_function(main_window)
        main_window.export_all_function = lambda: export_all_function(main_window)
        
        # Add all the aliases that GUI might use
        main_window.export_selected = main_window.export_selected_function
        main_window.export_selected_entries = main_window.export_selected_function
        main_window.export_all_entries = main_window.export_all_function
        main_window.export_all = main_window.export_all_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Clean export functions integrated with tab awareness")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export integration failed: {str(e)}")
        return False


# Export only the essential functions
__all__ = [
    'export_selected_function',
    'export_all_function',
    'integrate_export_functions'
]
