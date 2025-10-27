#this belongs in components/Img_Factory/img_factory_entry_operations.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - Entry Operations Methods

"""
Entry Operations Methods
Handles import, export, remove, and manipulation of IMG entries
"""

from typing import Optional, List
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from methods.svg_shared_icons import (
    get_import_icon, get_export_icon, get_remove_icon,
    get_save_icon, get_trash_icon
)
import os

##Methods list -
# close_all_file
# close_img_file
# dump_entries
# export_all
# export_selected
# export_selected_via
# export_via_tool
# import_files
# import_files_via
# import_via_tool
# pin_selected
# quick_export
# quick_export_selected
# reload_current_file
# reload_file
# remove_all_entries
# remove_selected
# remove_via_entries


def import_via_tool(self): #vers 1
    """Import files using external tool"""
    self.log_message("Import via tool functionality coming soon")


def export_via_tool(self): #vers 1
    """Export using external tool"""
    if not self.current_img:
        QMessageBox.warning(self, "Warning", "No IMG file loaded")
        return
    self.log_message("Export via tool functionality coming soon")


def import_files(self):
    """Import files into current IMG"""
    if not self.current_img:
        QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
        return

    try:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Import Files", "", "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)")

        if file_paths:
            self.log_message(f"Importing {len(file_paths)} files...")

            # Show progress - CHECK if method exists first
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Importing files...")

            imported_count = 0
            for i, file_path in enumerate(file_paths):
                progress = int((i + 1) * 100 / len(file_paths))
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Importing {os.path.basename(file_path)}")

                # Check if IMG has import_file method
                if hasattr(self.current_img, 'import_file'):
                    if self.current_img.import_file(file_path):
                        imported_count += 1
                        self.log_message(f"Imported: {os.path.basename(file_path)}")
                else:
                    self.log_message(f"IMG import_file method not available")
                    break

            # Refresh table
            if hasattr(self, '_populate_real_img_table'):
                self._populate_real_img_table(self.current_img)
            else:
                populate_img_table(self.gui_layout.table, self.current_img)

            self.log_message(f"Import complete: {imported_count}/{len(file_paths)} files imported")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Import complete")
            if hasattr(self.gui_layout, 'update_img_info'):
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")

            QMessageBox.information(self, "Import Complete",
                                    f"Imported {imported_count} of {len(file_paths)} files")

    except Exception as e:
        error_msg = f"Error importing files: {str(e)}"
        self.log_message(error_msg)
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Import error")
        QMessageBox.critical(self, "Import Error", error_msg)

def export_selected(self):
    """Export selected entries"""
    if not self.current_img:
        QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
        return

    try:
        selected_rows = []
        if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectedItems'):
            for item in self.gui_layout.table.selectedItems():
                if item.column() == 0:  # Only filename column
                    selected_rows.append(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select entries to export.")
            return

        export_dir = QFileDialog.getExistingDirectory(self, "Export To Folder")
        if export_dir:
            self.log_message(f"Exporting {len(selected_rows)} entries...")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Exporting...")

            exported_count = 0
            for i, row in enumerate(selected_rows):
                progress = int((i + 1) * 100 / len(selected_rows))
                entry_name = self.gui_layout.table.item(row, 0).text() if self.gui_layout.table.item(row, 0) else f"Entry_{row}"

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Exporting {entry_name}")

                # Check if IMG has export_entry method
                if hasattr(self.current_img, 'export_entry'):
                    #if self.current_img.export_entry(row, export_dir):
                    entry = self.current_img.entries[row]
                    output_path = os.path.join(export_dir, entry.name)
                    if self.current_img.export_entry(entry, output_path):
                        exported_count += 1
                        self.log_message(f"Exported: {entry_name}")
                else:
                    self.log_message(f"IMG export_entry method not available")
                    break

            self.log_message(f"Export complete: {exported_count}/{len(selected_rows)} files exported")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export complete")

            QMessageBox.information(self, "Export Complete", f"Exported {exported_count} of {len(selected_rows)} files to {export_dir}")

    except Exception as e:
        error_msg = f"Error exporting files: {str(e)}"
        self.log_message(error_msg)
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Export error")
        QMessageBox.critical(self, "Export Error", error_msg)


def export_all(self):
    """Export all entries"""
    if not self.current_img:
        QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
        return

    try:
        export_dir = QFileDialog.getExistingDirectory(self, "Export All To Folder")
        if export_dir:
            entry_count = len(self.current_img.entries) if hasattr(self.current_img, 'entries') and self.current_img.entries else 0
            self.log_message(f"Exporting all {entry_count} entries...")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Exporting all...")

            exported_count = 0
            for i, entry in enumerate(self.current_img.entries):
                progress = int((i + 1) * 100 / entry_count)
                entry_name = getattr(entry, 'name', f"Entry_{i}")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Exporting {entry_name}")

                # Check if IMG has export_entry method
                if hasattr(self.current_img, 'export_entry'):
                    #if self.current_img.export_entry(i, export_dir):
                    entry = self.current_img.entries[i]
                    output_path = os.path.join(export_dir, entry.name)
                    if self.current_img.export_entry(entry, output_path):
                        exported_count += 1
                        self.log_message(f"Exported: {entry_name}")
                else:
                    self.log_message(f"IMG export_entry method not available")
                    break

            self.log_message(f"Export complete: {exported_count}/{entry_count} files exported")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export complete")

            QMessageBox.information(self, "Export Complete", f"Exported {exported_count} of {entry_count} files to {export_dir}")

    except Exception as e:
        error_msg = f"Error exporting all files: {str(e)}"
        self.log_message(error_msg)
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Export error")
        QMessageBox.critical(self, "Export Error", error_msg)


def remove_selected(self):
    """Remove selected entries"""
    if not self.current_img:
        QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
        return

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
            self, "Confirm Removal", f"Remove {len(selected_rows)} selected entries?\n\n" + "\n".join(entry_names[:5]) +
            (f"\n... and {len(entry_names) - 5} more" if len(entry_names) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

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
                    self.log_message(f"IMG remove_entry method not available")
                    break

            # Refresh table
            if hasattr(self, '_populate_real_img_table'):
                self._populate_real_img_table(self.current_img)
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


def remove_all_entries(self):
    """Remove all entries from IMG"""
    if not self.current_img:
        QMessageBox.warning(self, "Warning", "No IMG file loaded")
        return

    try:
        reply = QMessageBox.question(self, "Remove All",
                                    "Remove all entries from IMG?")
        if reply == QMessageBox.StandardButton.Yes:
            self.current_img.entries.clear()
            self._update_ui_for_loaded_img()
            self.log_message("All entries removed")
    except Exception as e:
        self.log_message(f"Error in remove_all_entries: {str(e)}")


def quick_export(self):
    """Quick export selected files to default location"""
    if not self.current_img:
        QMessageBox.warning(self, "Warning", "No IMG file loaded")
        return

    try:
        # Check if we have a selection method available
        if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
            selected_rows = self.gui_layout.table.selectionModel().selectedRows()
        else:
            selected_rows = []

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No entries selected")
            return

        # Use Documents/IMG_Exports as default
        export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
        os.makedirs(export_dir, exist_ok=True)

        self.log_message(f"Quick exporting {len(selected_rows)} files to {export_dir}")
        QMessageBox.information(self, "Info", "Quick export functionality coming soon")
    except Exception as e:
        self.log_message(f"Error in quick_export: {str(e)}")

def close_img_file(self): #vers1
    """placeholder - close img debug"""

def close_all_file(self): #vers1
    """placeholder - close all debug"""

def reload_current_file(self): #vers 1
    """Reload current IMG or COL file (close and reopen)"""
    try:
        if self.current_img and self.current_img.file_path:
            # Store current IMG path
            img_path = self.current_img.file_path
            self.log_message(f"Reloading IMG file: {os.path.basename(img_path)}")

            # Close current file
            self.close_img_file()

            # Reopen the file
            self.load_img_file(img_path)
            self.log_message("IMG file reloaded")
            return True

        elif self.current_col and hasattr(self.current_col, 'file_path'):
            # Store current COL path
            col_path = self.current_col.file_path
            self.log_message(f"Reloading COL file: {os.path.basename(col_path)}")

            # Close current COL
            self.current_col = None

            # Reopen the COL file
            if hasattr(self, 'load_col_file_safely'):
                self.load_col_file_safely(col_path)
                self.log_message("COL file reloaded")
                return True

        else:
            self.log_message("No file to reload")
            return False

    except Exception as e:
        self.log_message(f"Reload failed: {str(e)}")
        return False


# Add aliases for button connections To-Do
def reload_file(self):
    return self.reload_current_file()

def export_selected_via(self): #vers 1
    """Export selected entries via IDE file"""
    from core.exporter import export_via_function
    export_via_function(self)

def quick_export_selected(self): #vers 1
    """Quick export selected entries"""
    from core.exporter import quick_export_function
    quick_export_function(self)

def dump_entries(self): #vers 1
    """Dump all entries"""
    try:
        from core.exporter import dump_all_function
        dump_all_function(self)
    except Exception as e:
        self.log_message(f"Dump error: {str(e)}")


def import_files_via(self): #vers 1
    """Import files via IDE file"""
    try:
        from core.importer import import_via_function
        import_via_function(self)
    except Exception as e:
        self.log_message(f"Import via error: {str(e)}")


def remove_via_entries(self):
    """Remove entries via IDE file"""
    try:
        from core.remove import remove_via_entries_function
        remove_via_entries_function(self)
    except Exception as e:
        self.log_message(f"Remove via error: {str(e)}")


def pin_selected(self): #vers 1
    """Pin selected entries to top of list"""
    try:
        if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
            selected_rows = self.gui_layout.table.selectionModel().selectedRows()
        else:
            selected_rows = []

        if not selected_rows:
            QMessageBox.information(self, "Pin", "No entries selected")
            return

        self.log_message(f"Pinned {len(selected_rows)} entries")
    except Exception as e:
        self.log_message(f"Error in pin_selected: {str(e)}")

__all__ = [
    'import_via_tool',
    'export_via_tool',
    'import_files',
    'export_selected',
    'export_all',
    'remove_selected',
    'remove_all_entries',
    'quick_export',
    'close_img_file',
    'close_all_file',
    'reload_current_file',
    'reload_file',
    'export_selected_via',
    'quick_export_selected',
    'dump_entries',
    'import_files_via',
    'remove_via_entries',
    'pin_selected'
]
