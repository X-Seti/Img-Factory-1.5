#this belongs in core/ rebuild.py - Version: 5
# X-Seti - August24 2025 - IMG Factory 1.5 - Rebuild Functions

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Callable
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# Use same tab awareness imports as export_via.py (this works!)
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab, get_current_file_type_from_tab

##Methods list -
# rebuild_current_img
# fast_rebuild_current
# safe_rebuild_current
# show_rebuild_mode_dialog
# _rebuild_using_img_editor_core
# _create_progress_callback
# _convert_img_to_archive
# _sanitize_filename
# integrate_rebuild_functions

def rebuild_current_img(main_window): #vers 5
    """Rebuild current IMG in active tab - UPDATED: Uses working IMG_Editor core"""
    try:
        # Copy exact pattern from working export_via.py
        if not validate_tab_before_operation(main_window, "Rebuild Current IMG"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file to rebuild")
            return False
        
        if hasattr(main_window, 'log_message'):
            file_name = os.path.basename(getattr(file_object, 'file_path', 'Unknown'))
            main_window.log_message(f"🔧 Rebuilding IMG using IMG_Editor core: {file_name}")
        
        # Use IMG_Editor core rebuild system
        success = _rebuild_using_img_editor_core(file_object, "fast", main_window)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            elif hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ IMG rebuilt successfully using IMG_Editor core")
            
            QMessageBox.information(main_window, "Rebuild Complete", 
                "IMG file rebuilt successfully!")
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG rebuild failed")
            
            QMessageBox.critical(main_window, "Rebuild Failed", 
                "Failed to rebuild IMG file. Check debug log for details.")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild error: {str(e)}")
        
        QMessageBox.critical(main_window, "Rebuild Error", 
            f"Error during rebuild: {str(e)}")
        return False


def fast_rebuild_current(main_window): #vers 5
    """Fast rebuild of current IMG - optimized for speed"""
    try:
        if not validate_tab_before_operation(main_window, "Fast Rebuild"):
            return False
            
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
            
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🚀 Fast rebuild mode - optimized for speed")
        
        return _rebuild_using_img_editor_core(file_object, "fast", main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Fast rebuild error: {str(e)}")
        return False


def safe_rebuild_current(main_window): #vers 5
    """Safe rebuild of current IMG - includes validation"""
    try:
        if not validate_tab_before_operation(main_window, "Safe Rebuild"):
            return False
            
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
            
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🛡️ Safe rebuild mode - includes validation")
        
        return _rebuild_using_img_editor_core(file_object, "safe", main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Safe rebuild error: {str(e)}")
        return False


def show_rebuild_mode_dialog(main_window): #vers 5
    """Show rebuild mode selection dialog"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Rebuild Options")
        dialog.setModal(True)
        dialog.resize(350, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header = QLabel("Select Rebuild Mode:")
        header.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Radio buttons
        button_group = QButtonGroup(dialog)
        
        fast_radio = QRadioButton("🚀 Fast Rebuild")
        fast_radio.setToolTip("Quick rebuild - optimized for speed")
        fast_radio.setChecked(True)
        button_group.addButton(fast_radio, 0)
        layout.addWidget(fast_radio)
        
        safe_radio = QRadioButton("🛡️ Safe Rebuild")
        safe_radio.setToolTip("Thorough rebuild with validation")
        button_group.addButton(safe_radio, 1)
        layout.addWidget(safe_radio)
        
        layout.addWidget(QLabel())  # Spacer
        
        # Buttons
        button_layout = QHBoxLayout()
        
        rebuild_btn = QPushButton("Rebuild")
        rebuild_btn.setDefault(True)
        cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(rebuild_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        rebuild_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Execute dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_id = button_group.checkedId()
            
            if selected_id == 0:  # Fast rebuild
                return fast_rebuild_current(main_window)
            elif selected_id == 1:  # Safe rebuild
                return safe_rebuild_current(main_window)
        
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild mode dialog error: {str(e)}")
        return False


def _rebuild_using_img_editor_core(img_file_object, mode: str, main_window) -> bool: #vers 5
    """CORE FUNCTION: Rebuild using working IMG_Editor core system"""
    try:
        # Import the working IMG_Editor core classes
        try:
            from IMG_Editor.core.Core import IMGArchive, IMGEntry
            from IMG_Editor.core.IMG_Operations import IMG_Operations
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG_Editor core not available - cannot rebuild")
            return False
        
        # Get file path from img_file_object
        file_path = getattr(img_file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No valid file path found")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 Loading IMG file: {os.path.basename(file_path)}")
        
        # Convert current IMG object to IMG_Editor IMGArchive
        img_archive = _convert_img_to_archive(img_file_object, main_window)
        if not img_archive:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Failed to convert IMG to archive format")
            return False
        
        # Create progress callback
        progress_callback = _create_progress_callback(main_window)
        
        # Use IMG_Operations.rebuild_archive (creates new IMG from memory, deletes old)
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🆕 Using IMG_Operations.rebuild_archive (creates new from memory)")
        
        # Rebuild the archive
        rebuilt_archive = IMG_Operations.rebuild_archive(
            img_archive=img_archive,
            output_path=None,  # Overwrites original
            version=None,      # Keep same version
            progress_callback=progress_callback
        )
        
        if rebuilt_archive:
            if hasattr(main_window, 'log_message'):
                entry_count = len(rebuilt_archive.entries) if rebuilt_archive.entries else 0
                main_window.log_message(f"✅ Successfully rebuilt IMG with {entry_count} entries")
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG_Operations.rebuild_archive returned None")
            return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core rebuild error: {str(e)}")
        return False


def _create_progress_callback(main_window) -> Callable: #vers 5
    """Create progress callback for rebuild operation"""
    def progress_callback(percent: int, message: str = ""):
        try:
            if hasattr(main_window, 'log_message') and message:
                main_window.log_message(f"🔧 {message} ({percent}%)")
            
            # Update progress bar if available
            if hasattr(main_window, 'update_progress'):
                main_window.update_progress(percent)
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
        except Exception:
            pass  # Ignore progress callback errors
    
    return progress_callback


def _convert_img_to_archive(img_file_object, main_window) -> Optional[object]: #vers 5
    """Convert IMG file object to IMG_Editor IMGArchive format"""
    try:
        from IMG_Editor.core.Core import IMGArchive, IMGEntry
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Converting IMG to IMG_Editor archive format")
        
        # Create new IMG_Editor archive
        archive = IMGArchive()
        
        # Set basic properties
        archive.file_path = getattr(img_file_object, 'file_path', '')
        
        # Determine version
        img_version = getattr(img_file_object, 'version', 2)
        if img_version == 1:
            archive.version = 'V1'
        else:
            archive.version = 'V2'
        
        # Convert entries
        if hasattr(img_file_object, 'entries') and img_file_object.entries:
            for old_entry in img_file_object.entries:
                try:
                    # Create new IMG_Editor entry
                    new_entry = IMGEntry()
                    
                    # Copy basic properties
                    new_entry.name = _sanitize_filename(getattr(old_entry, 'name', ''))
                    new_entry.actual_offset = getattr(old_entry, 'offset', 0)
                    new_entry.actual_size = getattr(old_entry, 'size', 0)
                    
                    # Try to preserve cached data if available
                    if hasattr(old_entry, '_cached_data') and old_entry._cached_data:
                        new_entry.data = old_entry._cached_data
                        new_entry.is_new_entry = True
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"📝 Preserved cached data for: {new_entry.name}")
                    elif hasattr(old_entry, 'get_data'):
                        # Try to get data using existing method
                        try:
                            new_entry.data = old_entry.get_data()
                        except Exception:
                            # Data will be read from file when needed
                            pass
                    
                    archive.entries.append(new_entry)
                    
                except Exception as e:
                    if hasattr(main_window, 'log_message'):
                        entry_name = getattr(old_entry, 'name', 'Unknown')
                        main_window.log_message(f"⚠️ Warning converting entry {entry_name}: {str(e)}")
                    continue
        
        if hasattr(main_window, 'log_message'):
            entry_count = len(archive.entries) if archive.entries else 0
            main_window.log_message(f"✅ Converted {entry_count} entries to IMG_Editor format")
        
        return archive
        
    except ImportError:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("❌ IMG_Editor core not available")
        return None
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Conversion error: {str(e)}")
        return None


def _sanitize_filename(filename: str) -> str: #vers 5
    """Clean filename to prevent corruption"""
    try:
        if not filename:
            return "file.dat"
        
        # Remove null bytes and control characters
        clean_name = filename.replace('\x00', '').replace('\xcd', '').replace('\xff', '')
        clean_name = ''.join(c for c in clean_name if 32 <= ord(c) <= 126)
        clean_name = clean_name.replace('\\', '_').replace('/', '_').replace('|', '_')
        clean_name = clean_name.strip()[:23]  # Leave room for null terminator
        
        return clean_name if clean_name else "file.dat"
        
    except Exception:
        return "file.dat"


def integrate_rebuild_functions(main_window) -> bool: #vers 5
    """Integrate IMG_Editor core rebuild functions - UPDATED"""
    try:
        # Main rebuild functions - TAB AWARE with IMG_Editor core
        main_window.rebuild_current_img = lambda: rebuild_current_img(main_window)
        main_window.rebuild_img = main_window.rebuild_current_img  # Alias
        
        # Mode-specific functions for current tab
        main_window.fast_rebuild_current = lambda: fast_rebuild_current(main_window)
        main_window.safe_rebuild_current = lambda: safe_rebuild_current(main_window)
        main_window.show_rebuild_dialog = lambda: show_rebuild_mode_dialog(main_window)
        
        # Legacy aliases for compatibility
        main_window.fast_rebuild = main_window.fast_rebuild_current
        main_window.safe_rebuild = main_window.safe_rebuild_current
        main_window.optimize_img = main_window.rebuild_current_img
        main_window.quick_rebuild = main_window.fast_rebuild_current
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 IMG_Editor core rebuild system integrated with TAB AWARENESS")
            main_window.log_message("   • Uses IMG_Operations.rebuild_archive (creates new from memory)")
            main_window.log_message("   • Rebuilds current active tab only")
            main_window.log_message("   • Preserves cached data and memory pool")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild integration failed: {str(e)}")
        return False


# Export only the essential functions
__all__ = [
    'rebuild_current_img',
    'fast_rebuild_current',
    'safe_rebuild_current', 
    'show_rebuild_mode_dialog',
    'integrate_rebuild_functions'
]
