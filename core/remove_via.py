#this belongs in core/ remove_via.py - Version: 2
# X-Seti - September06 2025 - IMG Factory 1.5 - Remove Via Functions

"""
Remove Via Functions - Uses EXACT same pattern as fixed import_via.py
FIXED: Tab awareness, IDE dialog integration, progress handling
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QMessageBox, QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt

# Use EXACT same methods and dialogs as fixed import_via.py
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab
from methods.ide_parser_functions import IDEParser
from gui.ide_dialog import show_ide_dialog

# IMG core integration support
try:
    from components.img_integration import IMGArchive, IMGEntry, Import_Export
    IMG_INTEGRATION_AVAILABLE = True
except ImportError:
    IMG_INTEGRATION_AVAILABLE = False

##Methods list -
# remove_via_function
# remove_via_entries_function
# _remove_img_via_ide
# _find_entries_for_removal
# _show_remove_confirmation_dialog
# _remove_with_img_core
# _convert_to_imgfactory_object
# integrate_remove_via_functions

def remove_via_function(main_window): #vers 2
    """Main remove via function using EXACT same dialogs as import_via.py"""
    try:
        # EXACT same tab awareness validation as import_via.py
        if not validate_tab_before_operation(main_window, "Remove Via"):
            return
        
        # Get current file type (same as import_via.py)
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG':
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first for remove operations")
            return
        
        # Direct to IDE removal (primary method)
        _remove_img_via_ide(main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via Error", f"Remove via failed: {str(e)}")


def remove_via_entries_function(main_window): #vers 2
    """Remove via entries function - alias for main function"""
    return remove_via_function(main_window)


def _remove_img_via_ide(main_window): #vers 2
    """Remove IMG entries via IDE definitions - same pattern as import_via.py"""
    try:
        # EXACT same tab awareness validation as import_via.py
        if not validate_tab_before_operation(main_window, "Remove IMG via IDE"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # EXACT same IDE dialog as import_via.py
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🗑️ Starting IMG Remove Via IDE...")
        
        # Use EXACT same dialog and parser as import_via.py
        try:
            ide_parser = show_ide_dialog(main_window, "remove")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error",
                               "IDE dialog system not available.\nPlease ensure all components are installed.")
            return
        
        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("Remove via IDE cancelled by user")
            return
        
        # Find entries to remove based on IDE
        entries_to_remove = _find_entries_for_removal(file_object, ide_parser, main_window)
        
        if not entries_to_remove:
            QMessageBox.information(main_window, "No Matches", 
                "No entries found in IMG file that match the IDE definitions")
            return
        
        # Show confirmation dialog
        if not _show_remove_confirmation_dialog(main_window, entries_to_remove, ide_parser):
            return
        
        success = _remove_entries(file_object, entries_to_remove, main_window)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Remove Via Complete", 
                f"Successfully removed {len(entries_to_remove)} entries via IDE")
        else:
            QMessageBox.critical(main_window, "Remove Via Failed", 
                "Failed to remove entries via IDE. Check debug log for details.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove IMG via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via IDE Error", f"Remove via IDE failed: {str(e)}")


def _find_entries_for_removal(file_object, ide_parser: IDEParser, main_window) -> List: #vers 2
    """Find entries in IMG that match IDE definitions - same logic as import_via.py"""
    try:
        entries_to_remove = []
        
        if not hasattr(file_object, 'entries'):
            return entries_to_remove
        
        # Get model names from IDE parser (same as import_via.py)
        ide_models = set()
        for model in ide_parser.models:
            model_name = model.get('model_name', '').lower()
            if model_name:
                ide_models.add(model_name)
                # Also add with .dff extension
                ide_models.add(f"{model_name}.dff")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Looking for {len(ide_models)} models from IDE in IMG entries")
        
        # Find matching entries in IMG
        for entry in file_object.entries:
            entry_name = getattr(entry, 'name', '').lower()
            
            if entry_name in ide_models:
                entries_to_remove.append(entry)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Found for removal: {entry_name}")
            else:
                # Check without extension
                base_name = entry_name.replace('.dff', '').replace('.txd', '')
                if base_name in ide_models:
                    entries_to_remove.append(entry)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ Found for removal: {entry_name}")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Found {len(entries_to_remove)} entries to remove")
        
        return entries_to_remove
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error finding entries for removal: {str(e)}")
        return []


def _show_remove_confirmation_dialog(main_window, entries_to_remove: List, ide_parser: IDEParser) -> bool: #vers 2
    """Show confirmation dialog for removal - similar to import_via.py confirmation"""
    try:
        # Create confirmation dialog
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Confirm Remove Via IDE")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_label = QLabel(f"Remove {len(entries_to_remove)} entries found in IDE file?")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # IDE info
        ide_info = QGroupBox("IDE File Information")
        ide_layout = QVBoxLayout(ide_info)
        
        ide_path_label = QLabel(f"File: {ide_parser.file_path}")
        ide_path_label.setWordWrap(True)
        ide_layout.addWidget(ide_path_label)
        
        ide_stats_label = QLabel(ide_parser.get_status_text())
        ide_layout.addWidget(ide_stats_label)
        
        layout.addWidget(ide_info)
        
        # Entries list
        entries_group = QGroupBox("Entries to Remove")
        entries_layout = QVBoxLayout(entries_group)
        
        entries_text = QTextEdit()
        entries_text.setReadOnly(True)
        entries_text.setMaximumHeight(150)
        
        entry_names = [getattr(entry, 'name', 'Unknown') for entry in entries_to_remove]
        entries_text.setPlainText('\n'.join(entry_names))
        
        entries_layout.addWidget(entries_text)
        layout.addWidget(entries_group)
        
        # Warning label
        warning_label = QLabel("⚠️ Warning: This will permanently remove entries from the IMG file!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove Entries")
        remove_button.clicked.connect(dialog.accept)
        remove_button.setStyleSheet("background-color: #d32f2f; color: white;")
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(remove_button)
        layout.addLayout(button_layout)
        
        # Show dialog
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error showing confirmation dialog: {str(e)}")
        
        # Fallback to simple confirmation
        reply = QMessageBox.question(
            main_window,
            "Confirm Remove Via IDE",
            f"Remove {len(entries_to_remove)} entries from IDE file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


def _remove_entries(file_object, entries_to_remove: List, main_window) -> bool: #vers 2
    """Remove entries"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG core not available for removal")
            return False
        
        # Convert to IMG archive format (same as import_via.py)
        img_archive = _convert_to_img_archive(file_object, main_window)
        if not img_archive:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Could not convert to IMG archive format")
            return False
        
        # Create progress dialog (same pattern as import_via.py)
        progress_dialog = QProgressDialog(
            "Preparing removal...",
            "Cancel",
            0,
            len(entries_to_remove),
            main_window
        )
        progress_dialog.setWindowTitle("Removing Entries via IDE")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(500)
        progress_dialog.show()
        QApplication.processEvents()
        
        removed_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(entries_to_remove):
                if progress_dialog.wasCanceled():
                    break
                
                entry_name = getattr(entry, 'name', f'Entry_{i}')
                progress_dialog.setLabelText(f"Removing: {entry_name}")
                progress_dialog.setValue(i)
                QApplication.processEvents()
                
                # Find entry in IMG archive
                img_archedit_entry = None
                for archive_entry in img_archive.entries:
                    if getattr(archive_entry, 'name', '') == entry_name:
                        img_archedit_entry = archive_entry
                        break
                
                if not img_archedit_entry:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ Entry not found in archive: {entry_name}")
                    failed_count += 1
                    continue
                
                # Remove entry from archive
                try:
                    img_archive.entries.remove(img_archedit_entry)
                    removed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ Removed: {entry_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Remove error for {entry_name}: {str(e)}")
            
        finally:
            progress_dialog.close()
        
        # Report results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Remove via IDE complete: {removed_count} success, {failed_count} failed")
            if removed_count > 0:
                main_window.log_message("💾 Remember to rebuild IMG to save changes")
        
        return removed_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG archive removal error: {str(e)}")
        return False


def _convert_to_img_archive(file_object, main_window): #vers 2
    """Convert file object - same as import_via.py"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            return None
        
        if isinstance(file_object, IMGArchive):
            return file_object
        
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            return None
        
        archive = IMGArchive()
        if archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                entry_count = len(archive.entries) if archive.entries else 0
                main_window.log_message(f"✅ Converted to IMG archive format: {entry_count} entries")
            return archive
        
        return None
        
    except Exception:
        return None


def integrate_remove_via_functions(main_window) -> bool: #vers 2
    """Integrate remove via functions into main window - same pattern as import_via.py"""
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
            integration_msg = "✅ Remove via functions integrated with tab awareness + imgfactory methods"
            main_window.log_message(integration_msg)
        
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
