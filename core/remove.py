#this belongs in core/remove.py - Version: 4
# X-Seti - July15 2025 - Img Factory 1.5
# Remove functions for IMG Factory

import os
from PyQt6.QtWidgets import QMessageBox, QInputDialog
from PyQt6.QtCore import QThread, pyqtSignal

##Methods list
#remove_selected_function
# remove_via_entries_function
# get_selected_entries
# integrate_remove_functions


def get_selected_entries(main_window): #vers 2
    """Get currently selected entries from the table"""
    try:
        selected_entries = []
        
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()
            
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            for row in selected_rows:
                if hasattr(main_window, 'current_img') and main_window.current_img and row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])
        
        return selected_entries
        
    except Exception:
        return []


def remove_selected_function(main_window): #vers 2
    """Remove selected entries from IMG file"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to remove.")
            return

        # Confirm removal
        reply = QMessageBox.question(
            main_window, 
            "Confirm Removal", 
            f"Are you sure you want to remove {len(selected_entries)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Remove entries
        removed_count = 0
        for entry in selected_entries:
            try:
                if hasattr(main_window.current_img, 'remove_entry'):
                    if main_window.current_img.remove_entry(entry):
                        removed_count += 1
                elif hasattr(main_window.current_img, 'entries'):
                    if entry in main_window.current_img.entries:
                        main_window.current_img.entries.remove(entry)
                        removed_count += 1
            except Exception as e:
                main_window.log_message(f"❌ Failed to remove entry: {str(e)}")

        # Refresh table
        if hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
        
        main_window.log_message(f"✅ Removed {removed_count} entries")
        QMessageBox.information(main_window, "Removal Complete", f"Successfully removed {removed_count} entries.")

    except Exception as e:
        main_window.log_message(f"❌ Remove error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove failed: {str(e)}")


def remove_via_entries_function(main_window): #vers 2
    """Remove entries based on IDE file or pattern"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get IDE file or pattern
        from PyQt6.QtWidgets import QFileDialog
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File or Pattern File",
            "",
            "IDE Files (*.ide);;Text Files (*.txt);;All Files (*)"
        )
        
        if not ide_file:
            return

        try:
            # Read file and get entry names
            with open(ide_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse entry names (simple implementation)
            entry_names = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract filename from IDE line (basic parsing)
                    parts = line.split(',')
                    if len(parts) >= 2:
                        # Second part is usually the model/texture name
                        entry_name = parts[1].strip()
                        if entry_name:
                            entry_names.append(entry_name)
            
            if not entry_names:
                QMessageBox.information(main_window, "No Entries Found", "No valid entry names found in the selected file.")
                return

            # Find matching entries
            entries_to_remove = []
            for entry in main_window.current_img.entries:
                entry_name = getattr(entry, 'name', '')
                if entry_name in entry_names:
                    entries_to_remove.append(entry)

            if not entries_to_remove:
                QMessageBox.information(main_window, "No Matches", "No entries match the names in the selected file.")
                return

            # Confirm removal
            reply = QMessageBox.question(
                main_window,
                "Confirm Removal",
                f"Found {len(entries_to_remove)} entries matching the file. Remove them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return

            # Remove entries
            removed_count = 0
            for entry in entries_to_remove:
                try:
                    if hasattr(main_window.current_img, 'remove_entry'):
                        if main_window.current_img.remove_entry(entry):
                            removed_count += 1
                    elif hasattr(main_window.current_img, 'entries'):
                        if entry in main_window.current_img.entries:
                            main_window.current_img.entries.remove(entry)
                            removed_count += 1
                except Exception as e:
                    main_window.log_message(f"❌ Failed to remove entry: {str(e)}")

            # Refresh table
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            main_window.log_message(f"✅ Removed {removed_count} entries via IDE file")
            QMessageBox.information(main_window, "Removal Complete", f"Successfully removed {removed_count} entries.")

        except Exception as e:
            main_window.log_message(f"❌ Error reading IDE file: {str(e)}")
            QMessageBox.critical(main_window, "File Error", f"Error reading file: {str(e)}")

    except Exception as e:
        main_window.log_message(f"❌ Remove via error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via Error", f"Remove via failed: {str(e)}")


def integrate_remove_functions(main_window): #vers 2
    """Integrate remove functions into main window"""
    try:
        main_window.remove_selected_function = lambda: remove_selected_function(main_window)
        main_window.remove_via_entries_function = lambda: remove_via_entries_function(main_window)
        
        # Add aliases for different naming conventions
        main_window.remove_selected = main_window.remove_selected_function
        main_window.remove_via_entries = main_window.remove_via_entries_function
        
        main_window.log_message("✅ Remove functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate remove functions: {str(e)}")
        return False

def remove_selected(self):
    """Remove selected entries"""
    if not self.current_img:
        QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
        return
""""
    try:
        selected_rows = []
        if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectedItems'):
            for item in self.gui_layout.table.selectedItems():
                if item.column() == 0:  # Only filename column
                    selected_rows.append(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select entries to remove.")
            return

        # Confirm removal
        entry_names = []
        for row in selected_rows:
            item = self.gui_layout.table.item(row, 0)
            entry_names.append(item.text() if item else f"Entry_{row}")

            reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Remove {len(selected_rows)} selected entries?\n\n" + "\n".join(entry_names[:5]) +
            (f"\n... and {len(entry_names) - 5} more" if len(entry_names) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Sort in reverse order to maintain indices
            selected_rows.sort(reverse=True)

            removed_count = 0
            for row in selected_rows:
                item = self.gui_layout.table.item(row, 0)
                entry_name = item.text() if item else f"Entry_{row}"

                # Check if IMG has remove_entry method
                if hasattr(self.current_img, 'remove_entry'):
                    if self.current_img.remove_entry(row):
                        removed_count += 1
                        self.log_message(f"Removed: {entry_name}")
                else:
                    self.log_message(f"❌ IMG remove_entry method not available")
                    break

            # Refresh table
            if hasattr(self, '_populate_img_table'):
                self._populate_img_table(self.current_img)
            else:
                populate_img_table(self.gui_layout.table, self.current_img)

            self.log_message(f"Removal complete: {removed_count} entries removed")

            if hasattr(self.gui_layout, 'update_img_info'):
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")

            QMessageBox.information(self, "Removal Complete",
                                    f"Removed {removed_count} entries")

        except Exception as e:
            error_msg = f"Error removing entries: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "Removal Error", error_msg)

"""

# Export functions
__all__ = [
    'remove_selected_function',
    'remove_via_entries_function',
    'get_selected_entries',
    'integrate_remove_functions'
]
