#this belongs in core/remove.py - Version: 1
# X-Seti - July14 2025 - Img Factory 1.5
# Core removal functions for IMG entries

import os
from PyQt6.QtWidgets import QMessageBox, QFileDialog


def get_selected_entries(main_window):
    """Get selected entries from the current table"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            return []
        
        table = main_window.gui_layout.table
        selected_rows = []
        
        for item in table.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)
        
        if not selected_rows:
            return []
        
        # Get entries from current IMG
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return []
        
        selected_entries = []
        for row in selected_rows:
            if 0 <= row < len(main_window.current_img.entries):
                selected_entries.append(main_window.current_img.entries[row])
        
        return selected_entries
        
    except Exception as e:
        main_window.log_message(f"❌ Error getting selected entries: {str(e)}")
        return []


def remove_selected_function(main_window):
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
        entry_names = [getattr(entry, 'name', 'unknown') for entry in selected_entries]
        reply = QMessageBox.question(
            main_window,
            "Confirm Removal",
            f"Are you sure you want to remove {len(selected_entries)} entries?\n\n" + 
            "\n".join(entry_names[:5]) + 
            ("..." if len(entry_names) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
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
                        entry_name = getattr(entry, 'name', 'unknown')
                        main_window.log_message(f"🗑️ Removed: {entry_name}")
                
            except Exception as e:
                entry_name = getattr(entry, 'name', 'unknown')
                main_window.log_message(f"❌ Failed to remove {entry_name}: {str(e)}")
        
        # Update table
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()
        
        # Show results
        main_window.log_message(f"✅ Removal complete: {removed_count} entries removed")
        QMessageBox.information(
            main_window,
            "Removal Complete",
            f"Removed {removed_count} entries successfully."
        )
        
    except Exception as e:
        main_window.log_message(f"❌ Remove error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Error", f"Remove failed: {str(e)}")


def remove_via_entries_function(main_window):
    """Remove entries using IDE file reference"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get IDE file for removal reference
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE file for removal reference",
            "",
            "IDE Files (*.ide);;All Files (*)"
        )

        if not ide_file:
            return

        main_window.log_message(f"🚮 Remove Via IDE: {ide_file}")

        # Parse IDE file to get entry names to remove
        entries_to_remove = []
        try:
            with open(ide_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue

                    # Extract filename from IDE line
                    # Common IDE formats:
                    # filename.dff, texdict, 100, 0, 0, 0
                    # filename.txd, texdict, 100, 0, 0, 0
                    parts = line.split(',')
                    if parts:
                        filename = parts[0].strip()
                        # Remove quotes if present
                        filename = filename.strip('"\'')
                        if filename:
                            entries_to_remove.append(filename)

        except Exception as e:
            main_window.log_message(f"❌ Error reading IDE file: {str(e)}")
            QMessageBox.critical(main_window, "IDE Parse Error", f"Could not parse IDE file:\n{str(e)}")
            return

        if not entries_to_remove:
            QMessageBox.information(main_window, "No Entries Found", "No valid entries found in IDE file.")
            return

        main_window.log_message(f"📋 Found {len(entries_to_remove)} entries in IDE file")

        # Find matching entries in current IMG
        img_entries_to_remove = []
        for entry_name in entries_to_remove:
            # Try exact match first
            found_entry = None
            for img_entry in main_window.current_img.entries:
                img_entry_name = getattr(img_entry, 'name', '')
                if img_entry_name.lower() == entry_name.lower():
                    found_entry = img_entry
                    break

            if found_entry:
                img_entries_to_remove.append(found_entry)
                main_window.log_message(f"✅ Found match: {entry_name}")
            else:
                main_window.log_message(f"⚠️ Not found in IMG: {entry_name}")

        if not img_entries_to_remove:
            QMessageBox.information(main_window, "No Matches", "No entries from IDE file were found in the current IMG.")
            return

        # Confirm removal
        reply = QMessageBox.question(
            main_window,
            "Confirm Remove Via IDE",
            f"Remove {len(img_entries_to_remove)} entries found in IDE file?\n\n" +
            f"IDE file: {os.path.basename(ide_file)}\n" +
            f"Entries to remove: {len(img_entries_to_remove)}/{len(entries_to_remove)} found",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Remove the entries
        removed_count = 0
        for entry in img_entries_to_remove:
            try:
                if hasattr(main_window.current_img, 'remove_entry'):
                    if main_window.current_img.remove_entry(entry):
                        removed_count += 1
                        entry_name = getattr(entry, 'name', 'unknown')
                        main_window.log_message(f"🗑️ Removed: {entry_name}")

            except Exception as e:
                entry_name = getattr(entry, 'name', 'unknown')
                main_window.log_message(f"❌ Failed to remove {entry_name}: {str(e)}")

        # Update table
        if hasattr(main_window, '_update_ui_for_loaded_img'):
            main_window._update_ui_for_loaded_img()

        # Show results
        main_window.log_message(f"✅ Remove Via IDE complete: {removed_count} entries removed")
        QMessageBox.information(
            main_window,
            "Remove Via IDE Complete",
            f"Successfully removed {removed_count} entries based on IDE file."
        )

    except Exception as e:
        main_window.log_message(f"❌ Remove Via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Remove Via IDE Error", f"Remove Via IDE failed: {str(e)}")


def integrate_remove_functions(main_window):
    """Integrate remove functions into main window"""
    try:
        # Add remove functions
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


# Export functions
__all__ = [
    'remove_selected_function',
    'remove_via_entries_function',
    'get_selected_entries',
    'integrate_remove_functions'
]