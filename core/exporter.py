#this belongs in core/exporter.py - Version: 3
# X-Seti - July31 2025 - IMG Factory 1.5 - Export Functions with Shared IDE System

"""
IMG Export Functions - Rewritten to use shared IDE parser and dialog
Provides consistent export functionality across all export operations
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from core.dialogs import ExportOptionsDialog
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut

##Methods list -
# dump_all_function
# export_all_function
# export_selected_function
# export_via_function
# get_selected_entries
# integrate_export_functions
# quick_export_function

##Classes -
# ExportThread

class ExportThread(QThread):
    """Background thread for exporting files"""
    
    progress_updated = pyqtSignal(int, str)  # progress %, message
    export_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    
    def __init__(self, main_window, entries_to_export: List, export_dir: str, export_options: dict):
        super().__init__()
        self.main_window = main_window
        self.entries_to_export = entries_to_export
        self.export_dir = export_dir
        self.export_options = export_options
        self.stats = {'exported': 0, 'skipped': 0, 'failed': 0}
        
    def run(self):
        """Run export operation in background"""
        try:
            total_entries = len(self.entries_to_export)
            
            for i, entry in enumerate(self.entries_to_export):
                entry_name = getattr(entry, 'name', f'entry_{i}')
                progress = int((i / total_entries) * 100)
                
                self.progress_updated.emit(progress, f"Exporting {entry_name}...")
                
                try:
                    # Determine output path
                    if self.export_options.get('organize_by_type', True):
                        subdir = self._get_type_subdir(entry_name)
                        output_dir = os.path.join(self.export_dir, subdir)
                    else:
                        output_dir = self.export_dir
                    
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, entry_name)
                    
                    # Skip if exists and not overwriting
                    if os.path.exists(output_path) and not self.export_options.get('overwrite', True):
                        self.stats['skipped'] += 1
                        continue
                    
                    # Get entry data
                    if hasattr(entry, 'get_data'):
                        entry_data = entry.get_data()
                    elif hasattr(entry, '_cached_data') and entry._cached_data:
                        entry_data = entry._cached_data
                    elif hasattr(self.main_window.current_img, 'read_entry_data'):
                        entry_data = self.main_window.current_img.read_entry_data(entry)
                    else:
                        self.stats['failed'] += 1
                        continue
                    
                    # Write file
                    with open(output_path, 'wb') as f:
                        f.write(entry_data)
                    
                    self.stats['exported'] += 1
                    
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"Error exporting {entry_name}: {e}")
            
            self.progress_updated.emit(100, "Export completed!")
            
            success_msg = f"Export completed: {self.stats['exported']} exported, {self.stats['skipped']} skipped, {self.stats['failed']} failed"
            self.export_completed.emit(True, success_msg, self.stats)
            
        except Exception as e:
            self.export_completed.emit(False, f"Export failed: {str(e)}", self.stats)
    
    def _get_type_subdir(self, filename: str) -> str: #vers 1
        """Get subdirectory based on file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        type_mapping = {
            '.dff': 'models',
            '.txd': 'textures', 
            '.col': 'collision',
            '.ifp': 'animations',
            '.wav': 'audio',
            '.scm': 'scripts',
            '.ipl': 'placement',
            '.dat': 'data'
        }
        
        return type_mapping.get(ext, 'other')

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

def export_selected_function(main_window): #vers 3
    """Export selected entries with options dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export")
            return
        
        main_window.log_message(f"📤 Exporting {len(selected_entries)} selected entries")
        
        # Show export options dialog
        dialog = ExportOptionsDialog(main_window, len(selected_entries))
        dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Export selected error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")

def export_via_function(main_window): #vers 3
    """Export files via IDE definitions - REWRITTEN with shared IDE system"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Use shared IDE dialog
        from gui.ide_dialog import show_ide_dialog
        
        ide_parser = show_ide_dialog(main_window, "export")
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
        matching_entries = []
        found_files = []
        
        for entry in main_window.current_img.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name.lower() in [f.lower() for f in files_to_find]:
                matching_entries.append(entry)
                found_files.append(entry_name)
        
        if not matching_entries:
            missing_msg = f"No files from IDE found in current IMG.\n\n"
            missing_msg += f"IDE references {len(files_to_find)} files:\n"
            missing_msg += '\n'.join(sorted(files_to_find)[:10])
            if len(files_to_find) > 10:
                missing_msg += f"\n... and {len(files_to_find) - 10} more files"
            
            QMessageBox.information(main_window, "No Matches", missing_msg)
            return
        
        # Show results
        result_msg = f"Found {len(matching_entries)} matching files in IMG"
        if len(matching_entries) < len(files_to_find):
            missing_count = len(files_to_find) - len(matching_entries)
            result_msg += f"\n{missing_count} files from IDE not found in IMG"
        
        main_window.log_message(f"📋 {result_msg}")
        
        # Show export options dialog
        dialog = ExportOptionsDialog(main_window, len(matching_entries))
        
        # Set default export directory based on IDE filename
        if hasattr(ide_parser, 'file_path') and ide_parser.file_path:
            ide_name = os.path.splitext(os.path.basename(ide_parser.file_path))[0]
            default_dir = os.path.join(os.path.expanduser("~/Desktop"), f"{ide_name}_export")
            dialog.folder_input.setText(default_dir)
        
        dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via IDE Error", f"Export via IDE failed: {str(e)}")

def quick_export_function(main_window): #vers 3
    """Quick export to project folder with automatic organization"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export")
            return
        
        # Get project folder from settings
        project_folder = None
        if hasattr(main_window, 'settings'):
            project_folder = getattr(main_window.settings, 'assists_folder', None)
            if not project_folder:
                project_folder = main_window.settings.get('project_folder')
        
        if not project_folder or not os.path.exists(project_folder):
            QMessageBox.warning(
                main_window, 
                "No Project Folder", 
                "Please set a project folder in settings first"
            )
            return
        
        main_window.log_message(f"⚡ Quick export: {len(selected_entries)} entries to project folder")
        
        # Create export options for quick export
        export_options = {
            'organize_by_type': True,
            'overwrite': True,
            'create_log': True
        }
        
        # Start export thread
        export_thread = ExportThread(main_window, selected_entries, project_folder, export_options)
        
        # Show progress dialog
        progress_dialog = QProgressDialog("Quick Export in progress...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(message)
        
        def export_finished(success, message, stats):
            progress_dialog.close()
            if success:
                QMessageBox.information(main_window, "Quick Export Complete", message)
            else:
                QMessageBox.critical(main_window, "Quick Export Failed", message)
            main_window.log_message(f"⚡ {message}")
        
        export_thread.progress_updated.connect(update_progress)
        export_thread.export_completed.connect(export_finished)
        export_thread.start()
        
        progress_dialog.show()
        
    except Exception as e:
        main_window.log_message(f"❌ Quick export error: {str(e)}")
        QMessageBox.critical(main_window, "Quick Export Error", f"Quick export failed: {str(e)}")

def export_all_function(main_window): #vers 3
    """Export all entries with options dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        all_entries = main_window.current_img.entries
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "No entries to export")
            return
        
        main_window.log_message(f"📤 Exporting all {len(all_entries)} entries")
        
        # Show export options dialog
        dialog = ExportOptionsDialog(main_window, len(all_entries))
        dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Export all error: {str(e)}")
        QMessageBox.critical(main_window, "Export All Error", f"Export all failed: {str(e)}")

def dump_all_function(main_window): #vers 3
    """Dump all entries to single folder without organization"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        all_entries = main_window.current_img.entries
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "No entries to dump")
            return
        
        # Get dump folder
        dump_folder = QFileDialog.getExistingDirectory(main_window, "Select Dump Folder")
        if not dump_folder:
            return
        
        main_window.log_message(f"📂 Dumping all {len(all_entries)} entries to folder")
        
        # Create export options for dump (no organization)
        export_options = {
            'organize_by_type': False,
            'overwrite': True,
            'create_log': True
        }
        
        # Start export thread
        export_thread = ExportThread(main_window, all_entries, dump_folder, export_options)
        
        # Show progress dialog
        progress_dialog = QProgressDialog("Dump in progress...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(message)
        
        def dump_finished(success, message, stats):
            progress_dialog.close()
            if success:
                QMessageBox.information(main_window, "Dump Complete", message)
            else:
                QMessageBox.critical(main_window, "Dump Failed", message)
            main_window.log_message(f"📂 {message}")
        
        export_thread.progress_updated.connect(update_progress)
        export_thread.export_completed.connect(dump_finished)
        export_thread.start()
        
        progress_dialog.show()
        
    except Exception as e:
        main_window.log_message(f"❌ Dump error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump failed: {str(e)}")

def integrate_export_functions(main_window): #vers 3
    """Integrate export functions into main window"""
    try:
        # Integrate shared IDE system first
        from methods.ide_parser import integrate_ide_parser
        from gui.ide_dialog import integrate_ide_dialog
        
        integrate_ide_parser(main_window)
        integrate_ide_dialog(main_window)
        
        # Add export functions
        main_window.export_selected_function = lambda: export_selected_function(main_window)
        main_window.export_via_function = lambda: export_via_function(main_window)
        main_window.quick_export_function = lambda: quick_export_function(main_window)
        main_window.export_all_function = lambda: export_all_function(main_window)
        main_window.dump_all_function = lambda: dump_all_function(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        
        # Add aliases for different naming conventions
        main_window.export_selected = main_window.export_selected_function
        main_window.export_selected_via = main_window.export_via_function
        main_window.quick_export_selected = main_window.quick_export_function
        main_window.export_all_entries = main_window.export_all_function
        main_window.dump_all_entries = main_window.dump_all_function
        
        main_window.log_message("✅ Export functions integrated with shared IDE system")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate export functions: {str(e)}")
        return False

__all__ = [
    'ExportThread',
    'get_selected_entries',
    'export_selected_function',
    'export_via_function', 
    'quick_export_function',
    'export_all_function',
    'dump_all_function',
    'integrate_export_functions'
]
