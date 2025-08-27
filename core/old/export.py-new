#this belongs in core/ export.py - Version: 4
# X-Seti - August24 2025 - IMG Factory 1.5 - Export Functions


import os
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system (this works!)
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# export_selected_function
# export_all_function
# _export_using_img_editor_core
# _get_selected_entries_safe
# _create_export_progress_dialog
# _export_entries_to_folder
# integrate_export_functions

def export_selected_function(main_window): #vers 4
    """Export selected entries using IMG_Editor core - TAB AWARE"""
    try:
        # Use same tab validation as rebuild.py
        if not validate_tab_before_operation(main_window, "Export Selected"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Get selected entries
        selected_entries = _get_selected_entries_safe(main_window, file_object)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "No entries selected for export")
            return False
        
        # Choose export folder
        export_folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Export Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_folder:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Export cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Exporting {len(selected_entries)} selected entries to: {export_folder}")
        
        # Use IMG_Editor core for export
        success = _export_using_img_editor_core(file_object, selected_entries, export_folder, main_window)
        
        if success:
            QMessageBox.information(main_window, "Export Complete", 
                f"Successfully exported {len(selected_entries)} files to:\n{export_folder}")
        else:
            QMessageBox.critical(main_window, "Export Failed", 
                "Failed to export selected files. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export selected error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export error: {str(e)}")
        return False


def export_all_function(main_window): #vers 4
    """Export all entries using IMG_Editor core - TAB AWARE"""
    try:
        # Use same tab validation as rebuild.py
        if not validate_tab_before_operation(main_window, "Export All"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Get all entries
        all_entries = getattr(file_object, 'entries', [])
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "IMG file contains no entries to export")
            return False
        
        # Choose export folder
        export_folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Export Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_folder:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Export all cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Exporting ALL {len(all_entries)} entries to: {export_folder}")
        
        # Use IMG_Editor core for export
        success = _export_using_img_editor_core(file_object, all_entries, export_folder, main_window)
        
        if success:
            QMessageBox.information(main_window, "Export Complete", 
                f"Successfully exported {len(all_entries)} files to:\n{export_folder}")
        else:
            QMessageBox.critical(main_window, "Export Failed", 
                "Failed to export files. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export all error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export error: {str(e)}")
        return False


def _export_using_img_editor_core(file_object, entries_to_export, export_folder, main_window) -> bool: #vers 4
    """CORE FUNCTION: Export using working IMG_Editor Import_Export class"""
    try:
        # Import the working IMG_Editor core classes
        try:
            from IMG_Editor.core.Core import IMGArchive, IMGEntry
            from IMG_Editor.core.Import_Export import Import_Export
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG_Editor core not available - cannot export")
            return False
        
        # Convert to IMG_Editor archive format if needed
        if not isinstance(file_object, IMGArchive):
            # Load the IMG file using IMG_Editor
            file_path = getattr(file_object, 'file_path', None)
            if not file_path or not os.path.exists(file_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ No valid file path for export")
                return False
            
            # Load IMG using IMG_Editor
            img_archive = IMGArchive()
            if not img_archive.load_from_file(file_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Failed to load IMG file with IMG_Editor")
                return False
        else:
            img_archive = file_object
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Using IMG_Editor Import_Export.export_entry")
        
        # Create progress dialog
        progress_dialog = _create_export_progress_dialog(main_window, len(entries_to_export))
        
        exported_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(entries_to_export):
                # Update progress
                progress_dialog.setValue(i)
                progress_dialog.setLabelText(f"Exporting: {getattr(entry, 'name', 'Unknown')}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("Export cancelled by user")
                    break
                
                # Get entry name
                entry_name = getattr(entry, 'name', f'entry_{i}')
                
                # Find entry in IMG_Editor archive
                img_editor_entry = None
                for archive_entry in img_archive.entries:
                    if archive_entry.name == entry_name:
                        img_editor_entry = archive_entry
                        break
                
                if not img_editor_entry:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ Entry not found in archive: {entry_name}")
                    failed_count += 1
                    continue
                
                # Create output path
                output_path = os.path.join(export_folder, entry_name)
                
                # Use IMG_Editor Import_Export.export_entry
                try:
                    success = Import_Export.export_entry(img_archive, img_editor_entry, output_path)
                    
                    if success:
                        exported_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"✅ Exported: {entry_name}")
                    else:
                        failed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Failed to export: {entry_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Export error for {entry_name}: {str(e)}")
            
        finally:
            progress_dialog.close()
        
        # Report results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Export complete: {exported_count} success, {failed_count} failed")
        
        return exported_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core export error: {str(e)}")
        return False


def _get_selected_entries_safe(main_window, file_object) -> list: #vers 4
    """Safely get selected entries from main window"""
    try:
        # Try different methods to get selected entries
        selected_entries = []
        
        # Method 1: Use main window's get_selected_entries
        if hasattr(main_window, 'get_selected_entries'):
            try:
                selected_entries = main_window.get_selected_entries()
                if selected_entries:
                    return selected_entries
            except Exception:
                pass
        
        # Method 2: Check if there's a table widget
        if hasattr(main_window, 'entries_table'):
            try:
                table = main_window.entries_table
                selected_rows = set()
                
                for item in table.selectedItems():
                    selected_rows.add(item.row())
                
                if selected_rows and hasattr(file_object, 'entries'):
                    for row in selected_rows:
                        if row < len(file_object.entries):
                            selected_entries.append(file_object.entries[row])
                
                if selected_entries:
                    return selected_entries
                    
            except Exception:
                pass
        
        # Method 3: If no selection, return empty list (user will get "no selection" message)
        return []
        
    except Exception:
        return []


def _create_export_progress_dialog(main_window, total_entries) -> QProgressDialog: #vers 4
    """Create progress dialog for export operation"""
    try:
        progress_dialog = QProgressDialog(
            "Preparing export...",
            "Cancel",
            0,
            total_entries,
            main_window
        )
        
        progress_dialog.setWindowTitle("Exporting Files")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        return progress_dialog
        
    except Exception:
        # Fallback: create minimal progress dialog
        progress_dialog = QProgressDialog(main_window)
        progress_dialog.setRange(0, total_entries)
        return progress_dialog


def integrate_export_functions(main_window): #vers 4
    """Integrate IMG_Editor core export functions - UPDATED"""
    try:
        # Main export functions with IMG_Editor core
        main_window.export_selected_function = lambda: export_selected_function(main_window)
        main_window.export_all_function = lambda: export_all_function(main_window)
        
        # Add all the aliases that GUI might use
        main_window.export_selected = main_window.export_selected_function
        main_window.export_selected_entries = main_window.export_selected_function
        main_window.export_all_entries = main_window.export_all_function
        main_window.export_all = main_window.export_all_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG_Editor core export functions integrated with TAB AWARENESS")
            main_window.log_message("   • Uses Import_Export.export_entry for reliable extraction")
            main_window.log_message("   • Supports both selected and all entry export")
        
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
