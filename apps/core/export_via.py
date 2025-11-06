#this belongs in core/export_via.py - Version: 8
# X-Seti - September09 2025 - IMG Factory 1.5 - Export Via Functions - Clean Complete Version

"""
Export Via Functions - Complete clean version with all fixes
- Uses correct assists folder from settings
- Shared overwrite check functions  
- Choose Export Folder button support
- Proper file export with multiple data access methods
- Theme-compatible buttons
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox

# Import required functions
from methods.export_shared import get_export_folder
from methods.export_overwrite_check import handle_overwrite_check, get_output_path_for_entry

##Methods list -
# export_via_function
# _export_img_via_ide
# _export_col_via_ide
# _handle_ide_dialog_result
# _get_assists_folder_from_settings
# _find_files_in_img_enhanced
# _start_ide_export_with_progress
# integrate_export_via_functions

def export_via_function(main_window): #vers 5
    """Main export via function with full tab awareness"""
    try:

        if file_type == 'IMG':
            return _export_img_via_ide(main_window)
        elif file_type == 'COL':
            return _export_col_via_ide(main_window)
        else:
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            return False

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export via error: {str(e)}")
        return False

def _export_img_via_ide(main_window): #vers 3
    """Export IMG via IDE with proper folder handling and file export"""
    try:
        # Validate current tab

        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False

        # Show IDE dialog
        try:
            from gui.ide_dialog import show_ide_dialog
            ide_parser = show_ide_dialog(main_window, "export")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error", "IDE dialog system not available.\nPlease ensure all components are installed.")
            return False

        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("IDE export cancelled by user")
            return False

        # Handle IDE dialog result and get export folder
        export_choice_result = _handle_ide_dialog_result(ide_parser, main_window)
        if not export_choice_result:
            return False
            
        export_folder, use_assists_structure = export_choice_result

        # Convert IDE parser models to entries format
        if hasattr(ide_parser, 'models') and ide_parser.models:
            ide_entries = []
            for model_id, model_data in ide_parser.models.items():
                class IDEEntry:
                    def __init__(self, model_data):
                        self.model_name = model_data.get('name', '')
                        self.name = model_data.get('name', '')
                        self.dff_name = model_data.get('dff', '')
                        self.texture_name = model_data.get('txd', '')
                        self.txd_name = model_data.get('txd', '')
                        self.txd = model_data.get('txd', '')
                
                ide_entries.append(IDEEntry(model_data))
        else:
            ide_entries = getattr(ide_parser, 'entries', [])

        if not ide_entries:
            models_count = len(getattr(ide_parser, 'models', {}))
            sections_count = len(getattr(ide_parser, 'sections', {}))
            
            error_msg = f"No entries found in IDE file.\n\nParsing results:\n"
            error_msg += f"• Models found: {models_count}\n"
            error_msg += f"• Sections found: {sections_count}\n"
            
            if hasattr(ide_parser, 'parse_stats') and ide_parser.parse_stats.get('errors'):
                error_msg += f"• Parse errors: {len(ide_parser.parse_stats['errors'])}\n"
                error_msg += f"• First error: {ide_parser.parse_stats['errors'][0]}"
            
            QMessageBox.information(main_window, "No IDE Entries", error_msg)
            return False

        # Find matching entries in IMG
        matching_entries, files_to_find, found_files = _find_files_in_img_enhanced(file_object, ide_entries, main_window)

        if not matching_entries:
            QMessageBox.information(main_window, "No Matches", "No files found in IMG that match IDE definitions")
            return False

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Exporting {len(matching_entries)} IDE-related files to {export_folder}")

        # Export options
        export_options = {
            'organize_by_type': True,
            'use_assists_structure': use_assists_structure,
            'overwrite': True,
            'create_log': True
        }

        # Start export with progress
        _start_ide_export_with_progress(main_window, matching_entries, export_folder, export_options)
        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via IDE Error", f"Export via IDE failed: {str(e)}")
        return False

def _handle_ide_dialog_result(ide_parser, main_window): #vers 3
    """Handle IDE dialog result and determine export folder"""
    try:
        # Check if user chose a folder in the IDE dialog
        if hasattr(ide_parser, 'selected_export_folder') and ide_parser.selected_export_folder:
            export_folder = ide_parser.selected_export_folder
            use_assists_structure = False
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Using chosen export folder: {export_folder}")
            
            return (export_folder, use_assists_structure)
        
        # No folder chosen in IDE dialog - use assists folder or ask
        assists_folder = _get_assists_folder_from_settings(main_window)
        if not assists_folder:
            # Ask user to choose folder
            export_folder = get_export_folder(main_window, "Select Export Destination for IDE Files")
            if not export_folder:
                return None
            use_assists_structure = False
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Using user-selected folder: {export_folder}")
        else:
            # Use assists folder
            export_folder = os.path.join(assists_folder, "IDE_Export")
            os.makedirs(export_folder, exist_ok=True)
            use_assists_structure = True
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Using assists folder: {export_folder}")
        
        return (export_folder, use_assists_structure)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error handling IDE dialog result: {str(e)}")
        return None

def _get_assists_folder_from_settings(main_window): #vers 3
    """Get assists folder from settings with comprehensive checking"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Searching for assists folder...")
        
        # Method 1: New settings system (utils/app_settings_system.py)
        if hasattr(main_window, 'settings'):
            assists_folder = getattr(main_window.settings, 'assists_folder', None)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Method 1 - settings.assists_folder: {assists_folder}")
            
            if assists_folder and os.path.exists(assists_folder):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Found assists folder: {assists_folder}")
                return assists_folder
        
        # Method 2: Direct main_window.project_folder attribute
        if hasattr(main_window, 'project_folder'):
            project_folder = main_window.project_folder
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Method 2 - main_window.project_folder: {project_folder}")
                
            if project_folder and os.path.exists(project_folder):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Found direct project folder: {project_folder}")
                return project_folder
        
        # Method 3: QSettings (gui/file_menu_integration.py system)
        from PyQt6.QtCore import QSettings
        settings = QSettings("IMG Factory", "Project Settings")
        project_folder = settings.value("project_folder")
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Method 3 - QSettings project_folder: {project_folder}")
            
        if project_folder and os.path.exists(project_folder):
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Found QSettings project folder: {project_folder}")
            return project_folder
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("No assists folder found - will ask user to choose")
        
        return None
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error getting assists folder: {str(e)}")
        return None

def _find_files_in_img_enhanced(file_object, ide_entries, main_window): #vers 2
    """Enhanced file finding with better IDE entry parsing"""
    try:
        matching_entries = []
        files_to_find = []
        found_files = []

        # Build list of files to find from IDE entries
        for ide_entry in ide_entries:
            # Try multiple attribute names for model data
            model_name = None
            if hasattr(ide_entry, 'model_name') and ide_entry.model_name:
                model_name = ide_entry.model_name
            elif hasattr(ide_entry, 'name') and ide_entry.name:
                model_name = ide_entry.name
            elif hasattr(ide_entry, 'dff_name') and ide_entry.dff_name:
                model_name = ide_entry.dff_name
            
            if model_name:
                files_to_find.extend([
                    f"{model_name}.dff",
                    f"{model_name}.col"
                ])
            
            # Try different texture attribute names
            texture_name = None
            if hasattr(ide_entry, 'texture_name') and ide_entry.texture_name:
                texture_name = ide_entry.texture_name
            elif hasattr(ide_entry, 'txd_name') and ide_entry.txd_name:
                texture_name = ide_entry.txd_name
            elif hasattr(ide_entry, 'txd') and ide_entry.txd:
                texture_name = ide_entry.txd
                
            if texture_name:
                files_to_find.append(f"{texture_name}.txd")

        # Find matching entries in IMG
        for entry in file_object.entries:
            entry_name = getattr(entry, 'name', '').lower()
            if any(file_to_find.lower() == entry_name for file_to_find in files_to_find):
                matching_entries.append(entry)
                found_files.append(entry_name)

        return matching_entries, files_to_find, found_files

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Error finding files in IMG: {str(e)}")
        return [], [], []

def _start_ide_export_with_progress(main_window, matching_entries, export_folder, export_options): #vers 7
    """Start IDE export with progress tracking and shared overwrite check - FIXED: QApplication import"""
    try:
        from PyQt6.QtWidgets import QProgressDialog, QApplication  # FIXED: Import QApplication from QtWidgets
        from PyQt6.QtCore import Qt  # Keep Qt from QtCore
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Creating export folder: {export_folder}")
        
        # Ensure export folder exists
        os.makedirs(export_folder, exist_ok=True)
        
        # Use shared overwrite check function
        filtered_entries, should_continue = handle_overwrite_check(
            main_window, matching_entries, export_folder, export_options, "export"
        )
        
        if not should_continue:
            return  # User cancelled or no files to export
        
        # Update matching_entries with filtered results
        matching_entries = filtered_entries
        
        # Create progress dialog
        progress = QProgressDialog("Starting export...", "Cancel", 0, len(matching_entries), main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()
        
        exported_count = 0
        failed_count = 0
        
        # Get the current file object to access entry data

        if not file_object:
            QMessageBox.critical(main_window, "Export Error", "No file object available for export")
            progress.close()
            return
        
        for i, entry in enumerate(matching_entries):
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
                            main_window.log_message(f"et_data failed for {entry_name}: {str(e)}")
                
                # Method 2: Try data attribute
                if entry_data is None and hasattr(entry, 'data'):
                    try:
                        entry_data = entry.data
                    except Exception as e:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"data attribute failed for {entry_name}: {str(e)}")
                
                # Method 3: Try to read from file using offset/size
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
                
                # Use shared function to get output path
                output_path = get_output_path_for_entry(entry_name, export_folder, export_options)
                
                # Create directory if needed (for organized exports)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Write file
                with open(output_path, 'wb') as f:
                    f.write(entry_data)
                
                exported_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Exported: {entry_name} ({len(entry_data)} bytes)")
                        
            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"Export error for {entry_name}: {str(e)}")
        
        progress.setValue(len(matching_entries))
        progress.close()
        
        # Show results
        if exported_count > 0:
            result_msg = f"Successfully exported {exported_count} files to:\n{export_folder}"
            if failed_count > 0:
                result_msg += f"\n\nFailed: {failed_count} files"
            
            QMessageBox.information(main_window, "Export Complete", result_msg)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"Export complete: {exported_count} exported, {failed_count} failed")
        else:
            QMessageBox.critical(main_window, "Export Failed", 
                f"No files were exported successfully.\nFailed: {failed_count} files")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Export progress error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")

def _export_col_via_ide(main_window): #vers 1
    """Export COL via IDE - placeholder implementation"""
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            QMessageBox.warning(main_window, "No COL File", "Please open a COL file first")
            return False

        if hasattr(main_window, 'log_message'):
            main_window.log_message("COL Export Via IDE not fully implemented yet")
        
        QMessageBox.information(main_window, "COL Export", "COL Export Via IDE functionality will be implemented in a future update.")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"COL export via IDE error: {str(e)}")
        return False

def integrate_export_via_functions(main_window) -> bool: #vers 3
    """Integrate export via functions into main window"""
    try:
        # Add main export via function
        main_window.export_via_function = lambda: export_via_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.export_via = main_window.export_via_function
        main_window.export_selected_via = main_window.export_via_function
        main_window.export_via_ide = main_window.export_via_function
        main_window.export_via_dialog = main_window.export_via_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Export via functions integrated - complete clean version")
            main_window.log_message("   • Fixed assists folder detection")
            main_window.log_message("   • Added shared overwrite checking")
            main_window.log_message("   • Added Choose Export Folder support")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Failed to integrate export via functions: {str(e)}")
        return False

# Export functions
__all__ = [
    'export_via_function',
    'integrate_export_via_functions',
    '_handle_ide_dialog_result',
    '_find_files_in_img_enhanced',
    '_get_assists_folder_from_settings'
]
