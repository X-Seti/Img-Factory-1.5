#this belongs in core/ remove_via.py - Version: 1
# X-Seti - August24 2025 - IMG Factory 1.5 - Remove Via Functions


import os
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QMessageBox, QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt

# Use EXACT same methods and dialogs as export_via.py and import_via.py
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab
from methods.ide_parser import IDEParser
from gui.ide_dialog import show_ide_dialog

# IMG_Editor core integration support
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
# _convert_to_img_archive
# integrate_remove_via_functions

def remove_via_function(main_window): #vers 1
    """Main remove via function using EXACT same dialogs as export_via.py"""
    try:
        # EXACT same tab awareness validation as export_via.py
        if not validate_tab_before_operation(main_window, "Remove Via"):
            return
        
        # Get current file type (same as export_via.py)
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


def remove_via_entries_function(main_window): #vers 1
    """Remove via entries function - alias for main function"""
    return remove_via_function(main_window)


def _remove_img_via_ide(main_window): #vers 1
    """Remove IMG entries via IDE definitions using EXACT same dialog as export_via.py"""
    try:
        # EXACT same tab validation as export_via.py
        if not validate_tab_before_operation(main_window, "Remove IMG via IDE"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # EXACT same IDE dialog as export_via.py and import_via.py (100% identical)
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
        
        # EXACT same IDE models extraction as export_via.py
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
        
        # Show removal confirmation dialog
        if not _show_remove_confirmation_dialog(main_window, entries_to_remove, files_missing):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries based on IDE definitions")
        
        # Remove entries with IMG_Editor core support
        success = _remove_with_img_core(main_window, file_object, entries_to_remove)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            QMessageBox.information(main_window, "Remove Complete", 
                f"Successfully removed {len(entries_to_remove)} entries via IDE definitions!")
        else:
            QMessageBox.critical(main_window, "Remove Failed", 
                "Failed to remove entries. Check debug log for details.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via IDE Error", f"Remove via IDE failed: {str(e)}")


def _find_entries_for_removal(file_object, ide_models: Dict, main_window) -> Tuple[List, List[str], List[str]]: #vers 1
    """Find entries to remove based on IDE definitions - EXACT same format as export_via.py"""
    try:
        entries_to_remove = []
        files_found = []
        files_missing = []
        
        # Extract filenames from IDE models dictionary (EXACT methods/ide_parser.py format)
        files_to_find = []
        for model_id, model_data in ide_models.items():
            model_name = model_data.get('name', '')
            if model_name:
                files_to_find.extend([
                    f"{model_name}.dff",
                    f"{model_data.get('txd', model_name)}.txd"
                ])
        
        # Get IMG entries
        img_entries = getattr(file_object, 'entries', [])
        
        # Find matching entries for removal
        for entry in img_entries:
            entry_name = getattr(entry, 'name', '').lower()
            
            for file_to_find in files_to_find:
                if entry_name == file_to_find.lower():
                    entries_to_remove.append(entry)
                    files_found.append(file_to_find)
                    break
        
        # Find missing files (ones in IDE but not in IMG)
        for file_to_find in files_to_find:
            if file_to_find not in files_found:
                files_missing.append(file_to_find)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 Found {len(files_found)} entries to remove, {len(files_missing)} not found in IMG")
        
        return entries_to_remove, files_found, files_missing
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error finding entries for removal: {str(e)}")
        return [], [], []


def _show_remove_confirmation_dialog(main_window, entries_to_remove: List, files_missing: List[str]) -> bool: #vers 1
    """Show remove confirmation dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Confirm Removal")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_text = f"Remove {len(entries_to_remove)} entries?"
        if files_missing:
            header_text += f" ({len(files_missing)} files from IDE not found in IMG)"
        
        header = QLabel(header_text)
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px; color: red;")
        layout.addWidget(header)
        
        # Warning
        warning = QLabel("⚠️ WARNING: This action cannot be undone!")
        warning.setStyleSheet("color: red; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(warning)
        
        # Entry list
        entry_list = QTextEdit()
        entry_list.setReadOnly(True)
        entry_list.setMaximumHeight(200)
        
        entry_text = "Entries to remove:\n"
        for i, entry in enumerate(entries_to_remove[:20]):  # Show first 20
            entry_name = getattr(entry, 'name', f'entry_{i}')
            entry_text += f"🗑️ {entry_name}\n"
        
        if len(entries_to_remove) > 20:
            entry_text += f"... and {len(entries_to_remove) - 20} more entries\n"
        
        if files_missing:
            entry_text += f"\nFiles from IDE not found in IMG:\n"
            for missing_file in files_missing[:10]:  # Show first 10
                entry_text += f"❓ {missing_file}\n"
            if len(files_missing) > 10:
                entry_text += f"... and {len(files_missing) - 10} more missing\n"
        
        entry_list.setPlainText(entry_text)
        layout.addWidget(entry_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_btn = QPushButton("🗑️ Remove Entries")
        remove_btn.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setDefault(True)  # Make cancel the default to prevent accidental removal
        
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        remove_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        return dialog.exec() == QDialog.DialogCode.Accepted
        
    except Exception:
        return False


def _remove_with_img_core(main_window, file_object, entries_to_remove: List) -> bool: #vers 1
    """Remove entries using IMG_Editor core for reliability"""
    try:
        # Convert to IMG_Editor archive if available
        if IMG_INTEGRATION_AVAILABLE:
            img_archive = _convert_to_img_archive(file_object, main_window)
            if img_archive:
                return _remove_with_img_archive(main_window, img_archive, entries_to_remove)
        
        # Fallback to basic removal
        return _remove_with_basic_method(main_window, file_object, entries_to_remove)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Remove with core error: {str(e)}")
        return False


def _remove_with_img_archive(main_window, img_archive, entries_to_remove: List) -> bool: #vers 1
    """Remove using IMG_Editor archive"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Using IMG_Editor core for reliable removal")
        
        # Create progress dialog - NO THREADING to avoid crashes
        progress_dialog = QProgressDialog(
            "Preparing removal...",
            "Cancel",
            0,
            len(entries_to_remove),
            main_window
        )
        progress_dialog.setWindowTitle("Removing Entries")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        removed_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(entries_to_remove):
                # Update progress
                progress_dialog.setValue(i)
                entry_name = getattr(entry, 'name', f'entry_{i}')
                progress_dialog.setLabelText(f"Removing: {entry_name}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("Removal cancelled by user")
                    break
                
                # Find entry in IMG_Editor archive
                img_editor_entry = None
                for archive_entry in img_archive.entries:
                    if getattr(archive_entry, 'name', '') == entry_name:
                        img_editor_entry = archive_entry
                        break
                
                if not img_editor_entry:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ Entry not found in archive: {entry_name}")
                    failed_count += 1
                    continue
                
                # Remove entry from archive
                try:
                    img_archive.entries.remove(img_editor_entry)
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
            main_window.log_message(f"📊 Removal complete: {removed_count} success, {failed_count} failed")
            if removed_count > 0:
                main_window.log_message("💾 Remember to rebuild IMG to save changes")
        
        return removed_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG archive removal error: {str(e)}")
        return False


def _remove_with_basic_method(main_window, file_object, entries_to_remove: List) -> bool: #vers 1
    """Fallback removal method"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("⚠️ Using fallback removal method")
        
        # Use the existing remove method from core/remove.py
        try:
            from core.remove import remove_multiple_entries
            return remove_multiple_entries(main_window, entries_to_remove)
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No removal method available")
            return False
        
    except Exception:
        return False


def _convert_to_img_archive(file_object, main_window):
    """Convert file object to IMG_Editor archive format"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            return None
        
        # If already IMG_Editor format, return as-is
        if isinstance(file_object, IMGArchive):
            return file_object
        
        # Load IMG file using IMG_Editor
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Create and load IMG_Editor archive
        archive = IMGArchive()
        if archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                entry_count = len(archive.entries) if archive.entries else 0
                main_window.log_message(f"✅ Converted to IMG archive format: {entry_count} entries")
            return archive
        
        return None
        
    except Exception:
        return None


def integrate_remove_via_functions(main_window) -> bool: #vers 1
    """Integrate remove via functions into main window"""
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
            integration_msg = "✅ Remove via functions integrated with tab awareness"
            if IMG_INTEGRATION_AVAILABLE:
                integration_msg += " + IMG_Editor core"
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
        
