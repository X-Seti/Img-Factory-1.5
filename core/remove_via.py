#this belongs in core/remove_via.py - Version: 2
# X-Seti - September07 2025 - IMG Factory 1.5 - Remove Via Functions FIXED

"""
Remove Via Functions - FIXED VERSION
Remove entries via IDE files using working remove system
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QMessageBox, QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt

# Import working methods
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab
from methods.ide_parser_functions import IDEParser
from gui.ide_dialog import show_ide_dialog
from core.remove import remove_entries_by_name

##Methods list -
# remove_via_function
# remove_via_entries_function
# _remove_img_via_ide
# _find_entries_for_removal
# _show_remove_confirmation_dialog
# integrate_remove_via_functions

def remove_via_function(main_window): #vers 2
    """Main remove via function - FIXED VERSION"""
    try:
        # Tab awareness validation
        if not validate_tab_before_operation(main_window, "Remove Via"):
            return
        
        # Get current file type
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG':
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first for remove operations")
            return
        
        # Direct to IDE removal
        _remove_img_via_ide(main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via Error", f"Remove via failed: {str(e)}")


def remove_via_entries_function(main_window): #vers 2
    """Remove via entries function - alias for main function"""
    return remove_via_function(main_window)


def _remove_img_via_ide(main_window): #vers 2
    """Remove IMG entries via IDE definitions - FIXED"""
    try:
        # Tab validation
        if not validate_tab_before_operation(main_window, "Remove IMG via IDE"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # Show IDE dialog
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🗑️ Starting IMG Remove Via IDE...")
        
        try:
            ide_parser = show_ide_dialog(main_window, "remove")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error",
                               "IDE dialog system not available.\nPlease ensure all components are installed.")
            return
        
        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("IDE remove cancelled by user")
            return
        
        # Extract IDE models
        ide_models = getattr(ide_parser, 'models', {})
        if not ide_models:
            QMessageBox.information(main_window, "No IDE Entries", "No model entries found in IDE file")
            return
        
        # Find entries to remove based on IDE definitions
        entries_to_remove, files_found, files_missing = _find_entries_for_removal(file_object, ide_models, main_window)
        
        if not entries_to_remove:
            QMessageBox.information(main_window, "No Matches Found", 
                f"No entries found in IMG that match IDE definitions.\n\n"
                f"Looked for files based on IDE models but none were found in the current IMG file.")
            return
        
        # Show confirmation dialog
        if not _show_remove_confirmation_dialog(main_window, entries_to_remove, files_missing):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries based on IDE definitions")
        
        # Remove entries using fixed remove system
        success = remove_entries_by_name(main_window, entries_to_remove)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_table') and callable(main_window.refresh_table):
                main_window.refresh_table()
            elif hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'populate_entries_table'):
                main_window.populate_entries_table()
            
            # Inform user about saving changes
            QMessageBox.information(
                main_window, 
                "Remove Via Complete", 
                f"Successfully removed {len(entries_to_remove)} entries via IDE definitions from memory.\n\n"
                f"💾 Use the 'Save Entry' button to save changes to disk.\n"
                f"⚠️ Changes will be lost if you reload without saving."
            )
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Removed {len(entries_to_remove)} entries via IDE - use 'Save Entry' to save changes")
        else:
            QMessageBox.critical(main_window, "Remove Failed", 
                "Failed to remove entries. Check debug log for details.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via IDE Error", f"Error: {str(e)}")


def _find_entries_for_removal(file_object, ide_models: dict, main_window) -> Tuple[List[str], List[str], List[str]]: #vers 2
    """Find entries in IMG that match IDE model definitions"""
    try:
        entries_to_remove = []
        files_found = []
        files_missing = []
        
        # Get current IMG entries
        img_entries = []
        if hasattr(file_object, 'entries') and file_object.entries:
            img_entries = [getattr(entry, 'name', '').lower() for entry in file_object.entries]
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📋 Checking {len(ide_models)} IDE models against {len(img_entries)} IMG entries")
        
        # Check each IDE model for matching files
        for model_id, model_data in ide_models.items():
            model_name = model_data.get('name', model_id)
            
            # Look for DFF and TXD files for this model
            dff_file = f"{model_name}.dff"
            txd_file = f"{model_name}.txd"
            
            # Check if files exist in IMG
            if dff_file.lower() in img_entries:
                entries_to_remove.append(dff_file)
                files_found.append(dff_file)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Found for removal: {dff_file}")
            else:
                files_missing.append(dff_file)
            
            if txd_file.lower() in img_entries:
                entries_to_remove.append(txd_file)
                files_found.append(txd_file)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Found for removal: {txd_file}")
            else:
                files_missing.append(txd_file)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Found {len(files_found)} files to remove, {len(files_missing)} missing")
        
        return entries_to_remove, files_found, files_missing
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error finding entries for removal: {str(e)}")
        return [], [], []


def _show_remove_confirmation_dialog(main_window, entries_to_remove: List[str], files_missing: List[str]) -> bool: #vers 2
    """Show confirmation dialog for remove via operation"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Confirm Remove Via IDE")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Summary
        summary_group = QGroupBox("Remove Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        summary_layout.addWidget(QLabel(f"Files to remove: {len(entries_to_remove)}"))
        if files_missing:
            summary_layout.addWidget(QLabel(f"Files not found in IMG: {len(files_missing)}"))
        
        layout.addWidget(summary_group)
        
        # Files to remove
        if entries_to_remove:
            remove_group = QGroupBox("Files to Remove")
            remove_layout = QVBoxLayout(remove_group)
            
            remove_text = QTextEdit()
            remove_text.setMaximumHeight(120)
            remove_text.setPlainText('\n'.join(entries_to_remove))
            remove_text.setReadOnly(True)
            remove_layout.addWidget(remove_text)
            
            layout.addWidget(remove_group)
        
        # Missing files (if any)
        if files_missing:
            missing_group = QGroupBox("Files Not Found in IMG")
            missing_layout = QVBoxLayout(missing_group)
            
            missing_text = QTextEdit()
            missing_text.setMaximumHeight(100)
            missing_text.setPlainText('\n'.join(files_missing[:20]))  # Show first 20
            if len(files_missing) > 20:
                missing_text.append(f"\n... and {len(files_missing) - 20} more")
            missing_text.setReadOnly(True)
            missing_layout.addWidget(missing_text)
            
            layout.addWidget(missing_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove Files")
        remove_button.clicked.connect(dialog.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
        
        return dialog.exec() == QDialog.DialogCode.Accepted
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error showing confirmation dialog: {str(e)}")
        # Fallback to simple message box
        reply = QMessageBox.question(
            main_window,
            "Confirm Remove Via IDE",
            f"Remove {len(entries_to_remove)} entries based on IDE definitions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


def integrate_remove_via_functions(main_window) -> bool: #vers 2
    """Integrate fixed remove via functions into main window"""
    try:
        # Add main remove via functions
        main_window.remove_via_function = lambda: remove_via_function(main_window)
        main_window.remove_via_entries_function = lambda: remove_via_entries_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.remove_via = main_window.remove_via_function
        main_window.remove_via_ide = main_window.remove_via_function
        main_window.remove_via_entries = main_window.remove_via_entries_function
        main_window.remove_entries_via = main_window.remove_via_entries_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Fixed remove via functions integrated with tab awareness")
            main_window.log_message("   • Uses working remove_entries_by_name method")
            main_window.log_message("   • Supports IDE-based entry removal")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate remove via functions: {str(e)}")
        return False


# Export functions
__all__ = [
    'remove_via_function',
    'remove_via_entries_function',
    'integrate_remove_via_functions'
]