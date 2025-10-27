#this belongs in core/export.py - Version: 6
# X-Seti - September09 2025 - IMG Factory 1.5 - Export Functions with Overwrite Check

"""
Export Functions - Updated with shared overwrite check system
- Export selected entries as individual files
- Export all entries as individual files  
- Shared overwrite checking for consistent user experience
- Tab awareness support
"""

import os
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# Import required functions
from methods.export_shared import get_export_folder, get_selected_entries
from methods.export_overwrite_check import handle_overwrite_check, get_output_path_for_entry

##Methods list -
# export_selected_function
# export_all_function
# _export_entries_with_overwrite_check
# _get_selected_entries_from_tab
# _export_col_selected
# _export_col_all
# integrate_export_functions

def export_selected_function(main_window): #vers 4
    """Export selected entries with overwrite check"""
    try:
        
        if not file_object:
            QMessageBox.warning(main_window, "No File", "No file is currently loaded")
            return False
        
        if file_type == 'IMG':
            return _export_img_selected(main_window, file_object)
        elif file_type == 'COL':
            return _export_col_selected(main_window, file_object)
        else:
            QMessageBox.warning(main_window, "Unsupported File Type", f"Export not supported for {file_type} files")
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export selected error: {str(e)}")
        return False

def export_all_function(main_window): #vers 4
    """Export all entries with overwrite check"""
    try:
        
        if not file_object:
            QMessageBox.warning(main_window, "No File", "No file is currently loaded")
            return False
        
        if file_type == 'IMG':
            return _export_img_all(main_window, file_object)
        elif file_type == 'COL':
            return _export_col_all(main_window, file_object)
        else:
            QMessageBox.warning(main_window, "Unsupported File Type", f"Export not supported for {file_type} files")
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export all error: {str(e)}")
        return False

def _export_img_selected(main_window, file_object): #vers 1
    """Export selected IMG entries with overwrite check"""
    try:
        # Get selected entries from current tab
        selected_entries = _get_selected_entries_from_tab(main_window)
        
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export")
            return False
        
        # Choose export directory
        export_dir = get_export_folder(main_window, f"Export {len(selected_entries)} Selected Entries")
        if not export_dir:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Exporting {len(selected_entries)} IMG entries to: {export_dir}")
        
        # Export options - individual files only (as per changelog request)
        export_options = {
            'organize_by_type': False,  # Keep files in main folder unless requested
            'overwrite': True,
            'create_log': False
        }
        
        # Use shared overwrite check and export
        return _export_entries_with_overwrite_check(main_window, file_object, selected_entries, export_dir, export_options, "selected")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export IMG selected error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")
        return False

def _export_img_all(main_window, file_object): #vers 1
    """Export all IMG entries with overwrite check"""
    try:
        all_entries = getattr(file_object, 'entries', [])
        
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "No entries found in current IMG file")
            return False
        
        # Choose export directory
        export_dir = get_export_folder(main_window, f"Export All {len(all_entries)} Entries")
        if not export_dir:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Exporting all {len(all_entries)} IMG entries to: {export_dir}")
        
        # Export options - individual files only (as per changelog request)
        export_options = {
            'organize_by_type': False,  # Keep files in main folder unless requested
            'overwrite': True,
            'create_log': False
        }
        
        # Use shared overwrite check and export
        return _export_entries_with_overwrite_check(main_window, file_object, all_entries, export_dir, export_options, "all")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export IMG all error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")
        return False

def _export_entries_with_overwrite_check(main_window, file_object, entries, export_dir, export_options, operation_name): #vers 1
    """Export entries with shared overwrite check system - NEW FUNCTION"""
    try:
        # Use shared overwrite check function
        filtered_entries, should_continue = handle_overwrite_check(
            main_window, entries, export_dir, export_options, f"export {operation_name}"
        )
        
        if not should_continue:
            return False  # User cancelled or no files to export
        
        # Update entries with filtered results
        entries = filtered_entries
        
        # Create progress dialog
        progress = QProgressDialog(f"Exporting {operation_name} entries...", "Cancel", 0, len(entries), main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()
        
        success_count = 0
        failed_count = 0
        
        for i, entry in enumerate(entries):
            if progress.wasCanceled():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("🚫 Export cancelled by user")
                break
                
            progress.setValue(i)
            entry_name = getattr(entry, 'name', f'entry_{i}')
            progress.setLabelText(f"Exporting: {entry_name}")
            QApplication.processEvents()
            
            try:
                # Get entry data with multiple methods
                entry_data = None
                
                # Method 1: Try get_data method
                if hasattr(entry, 'get_data'):
                    try:
                        entry_data = entry.get_data()
                    except Exception as e:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"get_data failed for {entry_name}: {str(e)}")
                
                # Method 2: Try cached data
                if entry_data is None and hasattr(entry, '_cached_data') and entry._cached_data:
                    entry_data = entry._cached_data
                
                # Method 3: Try file object read method
                if entry_data is None and hasattr(file_object, 'read_entry_data'):
                    try:
                        entry_data = file_object.read_entry_data(entry)
                    except Exception as e:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"read_entry_data failed for {entry_name}: {str(e)}")
                
                # Method 4: Try direct file reading using offset/size
                if entry_data is None and hasattr(file_object, 'file_path'):
                    try:
                        if hasattr(entry, 'offset') and hasattr(entry, 'size'):
                            with open(file_object.file_path, 'rb') as f:
                                f.seek(entry.offset)
                                entry_data = f.read(entry.size)
                    except Exception as e:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"File read failed for {entry_name}: {str(e)}")
                
                if entry_data is None:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"No data available for: {entry_name}")
                    continue
                
                # Use shared function to get output path (handles organization if needed)
                output_path = get_output_path_for_entry(entry_name, export_dir, export_options)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Write file
                with open(output_path, 'wb') as f:
                    f.write(entry_data)
                
                success_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Exported: {entry_name} ({len(entry_data)} bytes)")
                        
            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Export error for {entry_name}: {str(e)}")
        
        progress.setValue(len(entries))
        progress.close()
        
        # Show results
        if success_count > 0:
            result_msg = f"Successfully exported {success_count} files to:\n{export_dir}"
            if failed_count > 0:
                result_msg += f"\n\nFailed: {failed_count} files"
            
            QMessageBox.information(main_window, "Export Complete", result_msg)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Export complete: {success_count} exported, {failed_count} failed")
            return True
        else:
            QMessageBox.critical(main_window, "Export Failed", 
                f"No files were exported successfully.\nFailed: {failed_count} files")
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export with overwrite check error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")
        return False

def _get_selected_entries_from_tab(main_window): #vers 2
    """Get selected entries from current tab - ENHANCED"""
    try:
        selected_entries = []
        
        # Try multiple methods to get the table
        table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
        elif hasattr(main_window, 'entries_table'):
            table = main_window.entries_table
        elif hasattr(main_window, 'table'):
            table = main_window.table
        
        if not table:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("No table found for entry selection")
            return selected_entries
        
        # Get selected rows
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())
        
        # Get file object to access entries

        if not file_object or not hasattr(file_object, 'entries'):
            return selected_entries
        
        # Get entries for selected rows
        for row in selected_rows:
            if row < len(file_object.entries):
                selected_entries.append(file_object.entries[row])
                
        return selected_entries
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error getting selected entries: {str(e)}")
        return []

def _export_col_selected(main_window, file_object): #vers 2
    """Export selected COL models - PLACEHOLDER"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("COL selected export - Using placeholder implementation")
        
        QMessageBox.information(main_window, "COL Export", 
            "COL export functionality will use the existing COL export system.\n\n"
            "For now, this is a placeholder.")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL selected export error: {str(e)}")
        return False

def _export_col_all(main_window, file_object): #vers 2
    """Export all COL models - PLACEHOLDER"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("COL all export - Using placeholder implementation")
        
        QMessageBox.information(main_window, "COL Export", 
            "COL export functionality will use the existing COL export system.\n\n"
            "For now, this is a placeholder.")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL all export error: {str(e)}")
        return False

def integrate_export_functions(main_window): #vers 4
    """Integrate export functions with overwrite check support"""
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
            main_window.log_message("Export functions integrated with overwrite check support")
            main_window.log_message("   • Individual file export (no combining)")
            main_window.log_message("   • Shared overwrite checking")
            main_window.log_message("   • Multiple data access methods")
            main_window.log_message("   • Tab awareness support")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'export_selected_function',
    'export_all_function',
    'integrate_export_functions',
    '_export_entries_with_overwrite_check'
]
