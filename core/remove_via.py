#this belongs in core/ remove_via.py - Version: 3
# X-Seti - September08 2025 - IMG Factory 1.5 - Remove Via Functions with Proper Refresh

"""
Remove Via Functions - Remove entries via IDE/text files with comprehensive refresh
"""

import os
from pathlib import Path
from typing import List, Optional, Set
from PyQt6.QtWidgets import QMessageBox, QFileDialog

# Tab awareness system
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# remove_via_function
# remove_via_ide_function
# remove_via_text_function
# _remove_entries_via_ide
# _remove_entries_via_text
# _parse_text_file_list
# _find_entries_for_removal_ide
# _find_entries_for_removal_text
# _refresh_after_removal_via
# integrate_remove_via_functions

def remove_via_function(main_window): #vers 3
    """Remove via dialog - choose IDE or text file"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Remove Via"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Ask user what type of removal
        reply = QMessageBox.question(
            main_window,
            "Remove Via",
            "Choose removal method:\n\n"
            "• Yes = Remove via IDE file\n"
            "• No = Remove via text file list\n"
            "• Cancel = Cancel removal",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            return remove_via_ide_function(main_window)
        elif reply == QMessageBox.StandardButton.No:
            return remove_via_text_function(main_window)
        else:
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via Error", f"Remove via error: {str(e)}")
        return False


def remove_via_ide_function(main_window) -> bool: #vers 3
    """Remove entries based on IDE definitions with proper refresh"""
    try:
        # File dialog for IDE file
        ide_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File",
            "",
            "IDE Files (*.ide);;All Files (*.*)"
        )
        
        if not ide_path:
            return False
        
        # Remove entries via IDE
        success = _remove_entries_via_ide(main_window, ide_path)
        
        if success:
            QMessageBox.information(main_window, "Remove Via Complete",
                "Entries removed via IDE successfully!\n\n"
                "💾 Use the 'Save Entry' button to save changes to disk.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via IDE error: {str(e)}")
        return False


def remove_via_text_function(main_window) -> bool: #vers 3
    """Remove entries from text file list with proper refresh"""
    try:
        # File dialog for text file
        text_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select Text File List",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not text_path:
            return False
        
        # Remove entries via text list
        success = _remove_entries_via_text(main_window, text_path)
        
        if success:
            QMessageBox.information(main_window, "Remove Via Complete",
                "Entries removed via text list successfully!\n\n"
                "💾 Use the 'Save Entry' button to save changes to disk.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via text error: {str(e)}")
        return False


def _remove_entries_via_ide(main_window, ide_path: str) -> bool: #vers 3
    """Remove entries based on IDE definitions with proper refresh"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        # Parse IDE file
        try:
            from methods.ide_parser_functions import parse_ide_file
            ide_parser = parse_ide_file(ide_path)
            if ide_parser:
                ide_models = ide_parser.models
            else:
                ide_models = None
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IDE parser not available")
            return False
        
        if not ide_models:
            QMessageBox.information(main_window, "No Models", "No model definitions found in IDE file")
            return False
        
        # Find entries to remove based on IDE models
        entries_to_remove = _find_entries_for_removal_ide(file_object, ide_models)
        
        if not entries_to_remove:
            QMessageBox.information(main_window, "No Matches Found", 
                "No entries found in IMG that match IDE definitions")
            return False
        
        # Confirm removal
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            f"Remove {len(entries_to_remove)} entries matching IDE definitions?\n\n"
            f"⚠️ Use 'Save Entry' afterwards to save changes to disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Remove via IDE cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries via IDE definitions")
        
        # Remove entries
        removed_count = 0
        for entry in entries_to_remove:
            try:
                if hasattr(file_object, 'remove_entry') and callable(file_object.remove_entry):
                    if file_object.remove_entry(entry.name):
                        removed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🗑️ Removed via IDE: {entry.name}")
                else:
                    # Direct removal from entries list
                    if entry in file_object.entries:
                        file_object.entries.remove(entry)
                        removed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🗑️ Removed via IDE: {entry.name}")
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to remove {entry.name}: {str(e)}")
        
        if removed_count > 0:
            # Mark file as modified
            if hasattr(file_object, 'modified'):
                file_object.modified = True
            
            # Comprehensive refresh after removal
            _refresh_after_removal_via(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Removed {removed_count} entries via IDE - use 'Save Entry' to save changes")
            
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No entries were removed via IDE")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via IDE error: {str(e)}")
        return False


def _remove_entries_via_text(main_window, text_path: str) -> bool: #vers 3
    """Remove entries from text file list with proper refresh"""
    try:
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        # Parse text file for file list
        file_list = _parse_text_file_list(text_path)
        
        if not file_list:
            QMessageBox.information(main_window, "No Files", "No valid file names found in text file")
            return False
        
        # Find entries to remove based on text list
        entries_to_remove = _find_entries_for_removal_text(file_object, file_list)
        
        if not entries_to_remove:
            QMessageBox.information(main_window, "No Matches Found", 
                f"No entries found in IMG matching text file list.\n\n"
                f"Looked for {len(file_list)} filenames but none were found in the current IMG file.")
            return False
        
        # Confirm removal
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            f"Remove {len(entries_to_remove)} entries matching text file list?\n\n"
            f"⚠️ Use 'Save Entry' afterwards to save changes to disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Remove via text cancelled by user")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries via text list")
        
        # Remove entries
        removed_count = 0
        for entry in entries_to_remove:
            try:
                if hasattr(file_object, 'remove_entry') and callable(file_object.remove_entry):
                    if file_object.remove_entry(entry.name):
                        removed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🗑️ Removed via text: {entry.name}")
                else:
                    # Direct removal from entries list
                    if entry in file_object.entries:
                        file_object.entries.remove(entry)
                        removed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"🗑️ Removed via text: {entry.name}")
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Failed to remove {entry.name}: {str(e)}")
        
        if removed_count > 0:
            # Mark file as modified
            if hasattr(file_object, 'modified'):
                file_object.modified = True
            
            # Comprehensive refresh after removal
            _refresh_after_removal_via(main_window)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Removed {removed_count} entries via text - use 'Save Entry' to save changes")
            
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No entries were removed via text")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via text error: {str(e)}")
        return False


def _parse_text_file_list(text_path: str) -> List[str]: #vers 3
    """Parse text file for list of filenames"""
    try:
        file_list = []
        
        with open(text_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    # Smart parsing - extract filename if it's a path
                    if '/' in line or '\\' in line:
                        filename = os.path.basename(line)
                    else:
                        filename = line
                    
                    # Validate filename
                    if filename and '.' in filename:
                        file_list.append(filename)
        
        return file_list
        
    except Exception:
        return []


def _find_entries_for_removal_ide(file_object, ide_models: dict) -> List: #vers 3
    """Find entries to remove based on IDE model definitions"""
    try:
        entries_to_remove = []
        
        if not hasattr(file_object, 'entries'):
            return entries_to_remove
        
        # Build list of filenames to look for based on IDE models
        filenames_to_remove = set()
        
        for model_id, model_data in ide_models.items():
            model_name = model_data.get('name', model_id)
            
            # Common file patterns for GTA models
            potential_files = [
                f"{model_name}.dff",
                f"{model_name}.txd",
                f"{model_name}.col"
            ]
            
            filenames_to_remove.update(potential_files)
        
        # Find matching entries in IMG
        for entry in file_object.entries:
            if entry.name in filenames_to_remove:
                entries_to_remove.append(entry)
        
        return entries_to_remove
        
    except Exception:
        return []


def _find_entries_for_removal_text(file_object, file_list: List[str]) -> List: #vers 3
    """Find entries to remove based on text file list"""
    try:
        entries_to_remove = []
        
        if not hasattr(file_object, 'entries'):
            return entries_to_remove
        
        # Convert file list to set for faster lookup
        filenames_to_remove = set(file_list)
        
        # Find matching entries in IMG
        for entry in file_object.entries:
            if entry.name in filenames_to_remove:
                entries_to_remove.append(entry)
        
        return entries_to_remove
        
    except Exception:
        return []


def _refresh_after_removal_via(main_window): #vers 2
    """Comprehensive refresh after removal via - FIXED: No blocking RW detection"""
    try:
        # 1. Skip RW re-parsing to avoid UI freeze - table refresh will show existing RW data
        # Note: RW versions are preserved from when entries were first loaded
        
        # 2. Refresh table with highlights if available
        if hasattr(main_window, 'refresh_table_with_highlights'):
            main_window.refresh_table_with_highlights()
        elif hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        
        # 3. Refresh file list window
        if hasattr(main_window, 'refresh_file_list'):
            main_window.refresh_file_list()
        
        # 4. Update filewindow display via GUI layout
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'refresh_file_list'):
            main_window.gui_layout.refresh_file_list()
        
        # 5. Update UI for current IMG
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()
        
        # 6. Update current tab data
        if hasattr(main_window, 'refresh_current_tab_data'):
            main_window.refresh_current_tab_data()
        
        # 7. Clear any stale highlights (removed files should not be highlighted)
        if hasattr(main_window, '_import_highlight_manager'):
            # Refresh highlights to remove deleted entries
            if hasattr(main_window, 'refresh_table_with_highlights'):
                main_window.refresh_table_with_highlights()
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 UI refreshed after removal via (RW data preserved)")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Error in removal via refresh: {str(e)}")


def integrate_remove_via_functions(main_window) -> bool: #vers 4
    """Integrate remove via functions into main window - COMPLETE ALIASES"""
    try:
        # Add remove via methods to main window
        main_window.remove_via_function = lambda: remove_via_function(main_window)
        main_window.remove_via_ide_function = lambda: remove_via_ide_function(main_window)
        main_window.remove_via_text_function = lambda: remove_via_text_function(main_window)
        
        # Add aliases that GUI might use
        main_window.remove_via = main_window.remove_via_function
        main_window.remove_via_ide = main_window.remove_via_ide_function
        main_window.remove_via_text = main_window.remove_via_text_function
        main_window.remove_via_entries = main_window.remove_via_function  # GUI uses this name!
        main_window.remove_via_entries_function = main_window.remove_via_function  # Alternative GUI name
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Remove Via functions integrated")
            main_window.log_message("   • IDE file removal support")
            main_window.log_message("   • Text file list removal support")
            main_window.log_message("   • Simple UI refresh after removal")
            main_window.log_message("   • No unnecessary RW detection")
            main_window.log_message("   • All GUI aliases added")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove Via integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'remove_via_function',
    'remove_via_ide_function', 
    'remove_via_text_function',
    'integrate_remove_via_functions'
]