#this belongs in core/remove.py - Version: 4
# X-Seti - July31 2025 - IMG Factory 1.5 - Remove Functions with Shared IDE System

"""
IMG Remove Functions - Rewritten to use shared IDE parser and dialog
Provides consistent remove functionality across all remove operations
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut


##Methods list -
# get_selected_entries
# integrate_remove_functions
# remove_all_function
# remove_selected_function
# remove_via_entries_function

##Classes -
# RemoveThread

class RemoveThread(QThread):
    """Background thread for removing entries"""
    
    progress_updated = pyqtSignal(int, str)  # progress %, message
    remove_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    
    def __init__(self, main_window, entries_to_remove: List, remove_options: dict):
        super().__init__()
        self.main_window = main_window
        self.entries_to_remove = entries_to_remove
        self.remove_options = remove_options
        self.stats = {'removed': 0, 'skipped': 0, 'failed': 0}
        
    def run(self):
        """Run remove operation in background"""
        try:
            total_entries = len(self.entries_to_remove)
            
            for i, entry in enumerate(self.entries_to_remove):
                entry_name = getattr(entry, 'name', f'entry_{i}')
                progress = int((i / total_entries) * 100)
                
                self.progress_updated.emit(progress, f"Removing {entry_name}...")
                
                try:
                    # Remove using different methods
                    removed = False
                    
                    # Method 1: IMG remove_entry method
                    if hasattr(self.main_window.current_img, 'remove_entry'):
                        removed = self.main_window.current_img.remove_entry(entry)
                    
                    # Method 2: Direct entries list removal
                    elif hasattr(self.main_window.current_img, 'entries'):
                        if entry in self.main_window.current_img.entries:
                            self.main_window.current_img.entries.remove(entry)
                            removed = True
                    
                    if removed:
                        self.stats['removed'] += 1
                    else:
                        self.stats['failed'] += 1
                        
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"Error removing {entry_name}: {e}")
            
            # Save IMG if requested
            if self.remove_options.get('auto_save', True):
                self.progress_updated.emit(95, "Saving IMG file...")
                if hasattr(self.main_window.current_img, 'save_img_file'):
                    self.main_window.current_img.save_img_file()
            
            self.progress_updated.emit(100, "Remove completed!")
            
            success_msg = f"Remove completed: {self.stats['removed']} removed, {self.stats['failed']} failed"
            self.remove_completed.emit(True, success_msg, self.stats)
            
        except Exception as e:
            self.remove_completed.emit(False, f"Remove failed: {str(e)}", self.stats)

def get_selected_entries(main_window) -> List: #vers 2
    """Get currently selected entries from table"""
    selected_entries = []
    
    try:
        # Try different table access methods
        table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
        elif hasattr(main_window, 'entries_table'):
            table = main_window.entries_table
        
        if not table:
            return selected_entries
        
        # Get selected rows
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())
        
        # Get entries for selected rows
        if hasattr(main_window, 'current_img') and main_window.current_img:
            for row in selected_rows:
                if row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])
                    
    except Exception as e:
        print(f"Error getting selected entries: {e}")
    
    return selected_entries

def remove_selected_function(main_window): #vers 3
    """Remove selected entries with confirmation"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to remove")
            return
        
        # Show entry names for confirmation
        entry_names = [getattr(entry, 'name', f'Entry_{i}') for i, entry in enumerate(selected_entries)]
        
        # Create confirmation message
        confirm_msg = f"Are you sure you want to remove {len(selected_entries)} selected entries?"
        if len(entry_names) <= 10:
            confirm_msg += f"\n\nEntries to remove:\n" + "\n".join(entry_names)
        else:
            confirm_msg += f"\n\nFirst 10 entries:\n" + "\n".join(entry_names[:10])
            confirm_msg += f"\n... and {len(entry_names) - 10} more entries"
        
        # Confirm removal
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        main_window.log_message(f"🗑️ Removing {len(selected_entries)} selected entries")
        
        # Remove entries with progress dialog
        remove_options = {'auto_save': True}
        remove_thread = RemoveThread(main_window, selected_entries, remove_options)
        
        # Show progress dialog
        progress_dialog = QProgressDialog("Removing entries...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(message)
        
        def remove_finished(success, message, stats):
            progress_dialog.close()
            
            # Wait for thread to finish properly
            if remove_thread.isRunning():
                remove_thread.wait(1000)
            
            # Refresh table after removal
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            elif hasattr(main_window, '_populate_img_table'):
                main_window._populate_img_table(main_window.current_img)
            
            if success:
                QMessageBox.information(main_window, "Remove Complete", message)
            else:
                QMessageBox.critical(main_window, "Remove Failed", message)
            main_window.log_message(f"🗑️ {message}")
        
        remove_thread.progress_updated.connect(update_progress)
        remove_thread.remove_completed.connect(remove_finished)
        remove_thread.start()
        
        progress_dialog.show()
        
    except Exception as e:
        main_window.log_message(f"❌ Remove selected error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove failed: {str(e)}")

def remove_via_entries_function(main_window): #vers 4
    """Remove entries via IDE definitions - REWRITTEN with shared IDE system"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Use shared IDE dialog
        from gui.ide_dialog import show_ide_dialog

        ide_parser = show_ide_dialog(main_window, "remove")
        if not ide_parser:
            return  # User cancelled
        
        # Build list of filenames to find based on IDE relationships
        files_to_find = []
        for model_id, model_data in ide_parser.models.items():
            files_to_find.extend([
                model_data['dff'],
                f"{model_data['txd']}.txd"
            ])
        
        # Find matching entries in current IMG
        entries_to_remove = []
        found_files = []
        
        for entry in main_window.current_img.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name.lower() in [f.lower() for f in files_to_find]:
                entries_to_remove.append(entry)
                found_files.append(entry_name)
        
        if not entries_to_remove:
            missing_msg = f"No files from IDE found in current IMG to remove.\n\n"
            missing_msg += f"IDE references {len(files_to_find)} files:\n"
            missing_msg += '\n'.join(sorted(files_to_find)[:10])
            if len(files_to_find) > 10:
                missing_msg += f"\n... and {len(files_to_find) - 10} more files"
            
            QMessageBox.information(main_window, "No Matches", missing_msg)
            return
        
        # Show what will be removed
        confirm_msg = f"Found {len(entries_to_remove)} files from IDE in current IMG.\n\n"
        confirm_msg += f"Files to remove:\n" + "\n".join(sorted(found_files)[:10])
        if len(found_files) > 10:
            confirm_msg += f"\n... and {len(found_files) - 10} more files"
        
        if len(entries_to_remove) < len(files_to_find):
            missing_count = len(files_to_find) - len(entries_to_remove)
            confirm_msg += f"\n\n{missing_count} files from IDE not found in IMG"
        
        confirm_msg += f"\n\nProceed with removal?"
        
        # Confirm removal
        reply = QMessageBox.question(
            main_window,
            "Confirm IDE-based Removal",
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        main_window.log_message(f"🗑️ Removing {len(entries_to_remove)} entries via IDE")
        
        # Remove entries with progress dialog
        remove_options = {'auto_save': True}
        remove_thread = RemoveThread(main_window, entries_to_remove, remove_options)
        
        # Show progress dialog
        progress_dialog = QProgressDialog("Removing entries via IDE...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(message)
        
        def remove_finished(success, message, stats):
            progress_dialog.close()
            
            # Wait for thread to finish properly
            if remove_thread.isRunning():
                remove_thread.wait(1000)
            
            # Refresh table after removal
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            elif hasattr(main_window, '_populate_img_table'):
                main_window._populate_img_table(main_window.current_img)
            
            if success:
                QMessageBox.information(main_window, "Remove Via IDE Complete", message)
            else:
                QMessageBox.critical(main_window, "Remove Via IDE Failed", message)
            main_window.log_message(f"📋 {message}")
        
        remove_thread.progress_updated.connect(update_progress)
        remove_thread.remove_completed.connect(remove_finished)
        remove_thread.start()
        
        progress_dialog.show()
        
    except Exception as e:
        main_window.log_message(f"❌ Remove via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via IDE Error", f"Remove via IDE failed: {str(e)}")

def remove_all_function(main_window): #vers 2
    """Remove all entries with confirmation"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        all_entries = main_window.current_img.entries
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "No entries to remove")
            return
        
        # Confirm removal of all entries
        reply = QMessageBox.question(
            main_window,
            "Confirm Remove All",
            f"Are you sure you want to remove ALL {len(all_entries)} entries?\n\n"
            f"This will empty the IMG file completely!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        main_window.log_message(f"🗑️ Removing all {len(all_entries)} entries")
        
        # Remove all entries
        remove_options = {'auto_save': True}
        remove_thread = RemoveThread(main_window, all_entries, remove_options)
        
        # Show progress dialog
        progress_dialog = QProgressDialog("Removing all entries...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(message)
        
        def remove_finished(success, message, stats):
            progress_dialog.close()
            
            # Wait for thread to finish properly
            if remove_thread.isRunning():
                remove_thread.wait(1000)
            
            # Refresh table after removal
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            elif hasattr(main_window, '_populate_img_table'):
                main_window._populate_img_table(main_window.current_img)
            
            if success:
                QMessageBox.information(main_window, "Remove All Complete", message)
            else:
                QMessageBox.critical(main_window, "Remove All Failed", message)
            main_window.log_message(f"🗑️ {message}")
        
        remove_thread.progress_updated.connect(update_progress)
        remove_thread.remove_completed.connect(remove_finished)
        remove_thread.start()
        
        progress_dialog.show()
        
    except Exception as e:
        main_window.log_message(f"❌ Remove all error: {str(e)}")
        QMessageBox.critical(main_window, "Remove All Error", f"Remove all failed: {str(e)}")

def integrate_remove_functions(main_window): #vers 3
    """Integrate remove functions into main window"""
    try:
        # Integrate shared IDE system first
        from methods.ide_parser import integrate_ide_parser
        from gui.ide_dialog import integrate_ide_dialog
        
        integrate_ide_parser(main_window)
        integrate_ide_dialog(main_window)
        
        # Add remove functions
        main_window.remove_selected_function = lambda: remove_selected_function(main_window)
        main_window.remove_via_entries_function = lambda: remove_via_entries_function(main_window)
        main_window.remove_all_function = lambda: remove_all_function(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        
        # Add aliases for different naming conventions
        main_window.remove_selected = main_window.remove_selected_function
        main_window.remove_via_entries = main_window.remove_via_entries_function
        main_window.remove_all_entries = main_window.remove_all_function
        
        main_window.log_message("✅ Remove functions integrated with shared IDE system")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate remove functions: {str(e)}")
        return False

__all__ = [
    'RemoveThread',
    'get_selected_entries',
    'remove_selected_function',
    'remove_via_entries_function',
    'remove_all_function', 
    'integrate_remove_functions'
]