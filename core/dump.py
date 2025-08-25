#this belongs in core/ dump.py - Version: 8
# X-Seti - August24 2025 - IMG Factory 1.5 - Dump Functions


import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system (this works!)
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# dump_all_function
# dump_selected_function
# _dump_using_img_editor_core
# _get_selected_entries_safe
# _create_dump_progress_dialog
# _create_dump_directory
# _get_assists_folder
# _open_folder_in_explorer
# integrate_dump_functions

def dump_all_function(main_window): #vers 8
    """Dump all entries using IMG_Editor core - TAB AWARE"""
    try:
        # Use same tab validation as other core functions
        if not validate_tab_before_operation(main_window, "Dump All"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Get all entries
        all_entries = getattr(file_object, 'entries', [])
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "IMG file contains no entries to dump")
            return False
        
        # Create dump directory
        dump_folder = _create_dump_directory(main_window, "IMG_DUMP_ALL")
        if not dump_folder:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📦 Dumping ALL {len(all_entries)} entries to: {dump_folder}")
        
        # Use IMG_Editor core for dump
        success = _dump_using_img_editor_core(file_object, all_entries, dump_folder, main_window)
        
        if success:
            QMessageBox.information(main_window, "Dump Complete", 
                f"Successfully dumped {len(all_entries)} files to:\n{dump_folder}")
            
            # Open dump folder
            _open_folder_in_explorer(dump_folder)
        else:
            QMessageBox.critical(main_window, "Dump Failed", 
                "Failed to dump files. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump all error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump error: {str(e)}")
        return False


def dump_selected_function(main_window): #vers 8
    """Dump selected entries using IMG_Editor core - TAB AWARE"""
    try:
        # Use same tab validation as other core functions
        if not validate_tab_before_operation(main_window, "Dump Selected"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Get selected entries
        selected_entries = _get_selected_entries_safe(main_window, file_object)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "No entries selected for dump")
            return False
        
        # Create dump directory
        dump_folder = _create_dump_directory(main_window, "IMG_DUMP_SELECTED")
        if not dump_folder:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📦 Dumping {len(selected_entries)} selected entries to: {dump_folder}")
        
        # Use IMG_Editor core for dump
        success = _dump_using_img_editor_core(file_object, selected_entries, dump_folder, main_window)
        
        if success:
            QMessageBox.information(main_window, "Dump Complete", 
                f"Successfully dumped {len(selected_entries)} files to:\n{dump_folder}")
            
            # Open dump folder
            _open_folder_in_explorer(dump_folder)
        else:
            QMessageBox.critical(main_window, "Dump Failed", 
                "Failed to dump selected files. Check debug log for details.")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump selected error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump error: {str(e)}")
        return False


def _dump_using_img_editor_core(file_object, entries_to_dump, dump_folder, main_window) -> bool: #vers 8
    """CORE FUNCTION: Dump using working IMG_Editor Import_Export class"""
    try:
        # Import the working IMG_Editor core classes
        try:
            from IMG_Editor.core.Core import IMGArchive, IMGEntry
            from IMG_Editor.core.Import_Export import Import_Export
        except ImportError:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG_Editor core not available - cannot dump")
            return False
        
        # Convert to IMG_Editor archive format if needed
        if not isinstance(file_object, IMGArchive):
            # Load the IMG file using IMG_Editor
            file_path = getattr(file_object, 'file_path', None)
            if not file_path or not os.path.exists(file_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ No valid file path for dump")
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
            main_window.log_message("🔧 Using IMG_Editor Import_Export.export_entry for dump")
        
        # Create progress dialog - NO THREADING to avoid crashes
        progress_dialog = _create_dump_progress_dialog(main_window, len(entries_to_dump))
        
        dumped_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(entries_to_dump):
                # Update progress - process events to keep UI responsive
                progress_dialog.setValue(i)
                progress_dialog.setLabelText(f"Dumping: {getattr(entry, 'name', 'Unknown')}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("Dump cancelled by user")
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
                output_path = os.path.join(dump_folder, entry_name)
                
                # Use IMG_Editor Import_Export.export_entry - NO THREADING
                try:
                    success = Import_Export.export_entry(img_archive, img_editor_entry, output_path)
                    
                    if success:
                        dumped_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"✅ Dumped: {entry_name}")
                    else:
                        failed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Failed to dump: {entry_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Dump error for {entry_name}: {str(e)}")
            
        finally:
            progress_dialog.close()
        
        # Report results
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📊 Dump complete: {dumped_count} success, {failed_count} failed")
        
        return dumped_count > 0
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core dump error: {str(e)}")
        return False


def _get_selected_entries_safe(main_window, file_object) -> list: #vers 8
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
        
        # Method 3: If no selection, return empty list
        return []
        
    except Exception:
        return []


def _create_dump_progress_dialog(main_window, total_entries) -> QProgressDialog: #vers 8
    """Create progress dialog for dump operation"""
    try:
        progress_dialog = QProgressDialog(
            "Preparing dump...",
            "Cancel",
            0,
            total_entries,
            main_window
        )
        
        progress_dialog.setWindowTitle("Dumping Files")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        return progress_dialog
        
    except Exception:
        # Fallback: create minimal progress dialog
        progress_dialog = QProgressDialog(main_window)
        progress_dialog.setRange(0, total_entries)
        return progress_dialog


def _create_dump_directory(main_window, dump_type: str) -> Optional[str]: #vers 8
    """Create organized dump directory"""
    try:
        # Get base assists folder
        assists_folder = _get_assists_folder()
        
        # Create timestamp-based folder name
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get current file name for folder naming
        try:
            file_object, _ = get_current_file_from_active_tab(main_window)
            file_path = getattr(file_object, 'file_path', '')
            file_name = Path(file_path).stem if file_path else 'unknown'
        except Exception:
            file_name = 'unknown'
        
        # Create organized folder structure
        dump_folder_name = f"{dump_type}_{file_name}_{timestamp}"
        dump_folder = os.path.join(assists_folder, dump_folder_name)
        
        # Create directory
        os.makedirs(dump_folder, exist_ok=True)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📁 Created dump directory: {dump_folder}")
        
        return dump_folder
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to create dump directory: {str(e)}")
        return None


def _get_assists_folder() -> str: #vers 8
    """Get Assists folder path"""
    try:
        current_dir = os.getcwd()
        assists_folder = os.path.join(current_dir, "Assists")
        
        if not os.path.exists(assists_folder):
            os.makedirs(assists_folder, exist_ok=True)
        
        return assists_folder
    except Exception:
        return os.getcwd()


def _open_folder_in_explorer(folder_path: str): #vers 8
    """Open folder in system file explorer"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["xdg-open", folder_path])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", folder_path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
    except Exception:
        pass  # Don't fail if can't open folder


def integrate_dump_functions(main_window) -> bool: #vers 8
    """Integrate IMG_Editor core dump functions - FIXED"""
    try:
        # Main dump functions with IMG_Editor core - NO THREADING
        main_window.dump_all_function = lambda: dump_all_function(main_window)
        main_window.dump_selected_function = lambda: dump_selected_function(main_window)
        
        # Add all the aliases that GUI might use
        main_window.dump_all = main_window.dump_all_function
        main_window.dump_selected = main_window.dump_selected_function
        main_window.dump_all_entries = main_window.dump_all_function
        main_window.dump_selected_entries = main_window.dump_selected_function
        main_window.dump_entries = main_window.dump_selected_function  # Legacy
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG_Editor core dump functions integrated - CRASH-FREE")
            main_window.log_message("   • Uses Import_Export.export_entry for reliable extraction")
            main_window.log_message("   • NO THREADING - eliminates app crashes")
            main_window.log_message("   • Creates organized timestamped dump folders")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Dump integration failed: {str(e)}")
        return False


# Export only the essential functions
__all__ = [
    'dump_all_function',
    'dump_selected_function',
    'integrate_dump_functions'
]
