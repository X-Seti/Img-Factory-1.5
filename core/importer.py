#this belongs in core/importer.py - Version: 3
# X-Seti - July31 2025 - IMG Factory 1.5 - Import Functions with Shared IDE System

"""
IMG Import Functions - Rewritten to use shared IDE parser and dialog
Provides consistent import functionality across all import operations
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
from core.dialogs import ImportOptionsDialog
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut

##Methods list -
# get_selected_entries
# import_files_function
# import_from_folder
# import_via_function
# integrate_import_functions

##Classes -
# ImportThread

class ImportThread(QThread):
    """Background thread for importing files"""
    
    progress_updated = pyqtSignal(int, str)  # progress %, message
    import_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    
    def __init__(self, main_window, files_to_import: List[str], import_options: dict):
        super().__init__()
        self.main_window = main_window
        self.files_to_import = files_to_import
        self.import_options = import_options
        self.stats = {'imported': 0, 'skipped': 0, 'failed': 0}
        
    def run(self):
        """Run import operation in background"""
        try:
            total_files = len(self.files_to_import)
            
            for i, file_path in enumerate(self.files_to_import):
                filename = os.path.basename(file_path)
                progress = int((i / total_files) * 100)
                
                self.progress_updated.emit(progress, f"Importing {filename}...")
                
                try:
                    # Read file data
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Check if should replace existing
                    if self.import_options.get('replace_existing', False):
                        # Remove existing entry if it exists
                        existing_entries = [e for e in self.main_window.current_img.entries 
                                          if e.name.lower() == filename.lower()]
                        for entry in existing_entries:
                            self.main_window.current_img.entries.remove(entry)
                    
                    # Add to IMG
                    if hasattr(self.main_window.current_img, 'add_entry'):
                        success = self.main_window.current_img.add_entry(filename, file_data, auto_save=False)
                        if success:
                            self.stats['imported'] += 1
                        else:
                            self.stats['failed'] += 1
                    else:
                        self.stats['failed'] += 1
                        
                except Exception as e:
                    self.stats['failed'] += 1
                    print(f"Error importing {filename}: {e}")
            
            # Save IMG if requested
            if self.import_options.get('auto_save', True):
                self.progress_updated.emit(95, "Saving IMG file...")
                if hasattr(self.main_window.current_img, 'save_img_file'):
                    self.main_window.current_img.save_img_file()
            
            self.progress_updated.emit(100, "Import completed!")
            
            success_msg = f"Import completed: {self.stats['imported']} imported, {self.stats['failed']} failed"
            self.import_completed.emit(True, success_msg, self.stats)
            
        except Exception as e:
            self.import_completed.emit(False, f"Import failed: {str(e)}", self.stats)

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

def import_files_function(main_window): #vers 3
    """Import files with file selection dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get files to import
        files, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            "",
            "All Files (*);;Models (*.dff);;Textures (*.txd);;Collision (*.col);;Animation (*.ifp);;Audio (*.wav)"
        )
        
        if not files:
            return
        
        main_window.log_message(f"📥 Selected {len(files)} files for import")
        
        # Show import options dialog
        dialog = ImportOptionsDialog(main_window, len(files))
        dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Import files error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import failed: {str(e)}")

def import_via_function(main_window): #vers 3
    """Import files via IDE definitions - REWRITTEN with shared IDE system"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Use shared IDE dialog
        from gui.ide_dialog import show_ide_dialog
        
        ide_parser = show_ide_dialog(main_window, "import")
        if not ide_parser:
            return  # User cancelled
        
        # Get base directory for file search
        import_dir = QFileDialog.getExistingDirectory(
            main_window,
            "Select Directory Containing Files to Import"
        )
        
        if not import_dir:
            return
        
        # Build list of files to import based on IDE relationships
        files_to_import = []
        missing_files = []
        
        for model_id, model_data in ide_parser.models.items():
            # Look for DFF file
            dff_file = os.path.join(import_dir, model_data['dff'])
            if os.path.exists(dff_file):
                files_to_import.append(dff_file)
            else:
                missing_files.append(model_data['dff'])
            
            # Look for TXD file  
            txd_file = os.path.join(import_dir, f"{model_data['txd']}.txd")
            if os.path.exists(txd_file):
                files_to_import.append(txd_file)
            else:
                missing_files.append(f"{model_data['txd']}.txd")
        
        if not files_to_import:
            QMessageBox.information(
                main_window, 
                "No Files Found",
                f"No files found in directory that match IDE definitions.\n\n"
                f"Looking for {len(ide_parser.models) * 2} files based on IDE data."
            )
            return
        
        # Show results
        result_msg = f"Found {len(files_to_import)} files to import"
        if missing_files:
            result_msg += f"\n{len(missing_files)} files missing from directory"
        
        main_window.log_message(f"📋 {result_msg}")
        
        # Show import options dialog
        dialog = ImportOptionsDialog(main_window, len(files_to_import))
        dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via IDE Error", f"Import via IDE failed: {str(e)}")

def import_from_folder(main_window): #vers 3
    """Import all files from a folder"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get folder
        folder = QFileDialog.getExistingDirectory(
            main_window,
            "Select Folder to Import"
        )
        
        if not folder:
            return
        
        # Get all files in folder (recursive option)
        files_to_import = []
        
        # Ask if should search recursively
        reply = QMessageBox.question(
            main_window,
            "Search Subfolders?",
            "Include files from subfolders?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Recursive search
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    if not filename.startswith('.'):  # Skip hidden files
                        file_path = os.path.join(root, filename)
                        files_to_import.append(file_path)
        else:
            # Just current folder
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    files_to_import.append(file_path)
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", "No files found in the selected folder")
            return
        
        main_window.log_message(f"📁 Import from folder: {len(files_to_import)} files found")
        
        # Show import options dialog
        dialog = ImportOptionsDialog(main_window, len(files_to_import))
        dialog.exec()
        
    except Exception as e:
        main_window.log_message(f"❌ Import from folder error: {str(e)}")
        QMessageBox.critical(main_window, "Import From Folder Error", f"Import from folder failed: {str(e)}")

def integrate_import_functions(main_window): #vers 3
    """Integrate import functions into main window"""
    try:
        # Integrate shared IDE system first
        from methods.ide_parser import integrate_ide_parser
        from gui.ide_dialog import integrate_ide_dialog
        
        integrate_ide_parser(main_window)
        integrate_ide_dialog(main_window)
        
        # Add import functions
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_via_function = lambda: import_via_function(main_window)
        main_window.import_from_folder = lambda: import_from_folder(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        
        # Add aliases for different naming conventions
        main_window.import_files = main_window.import_files_function
        main_window.import_files_via = main_window.import_via_function
        
        main_window.log_message("✅ Import functions integrated with shared IDE system")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate import functions: {str(e)}")
        return False

__all__ = [
    'ImportThread',
    'get_selected_entries',
    'import_files_function',
    'import_via_function',
    'import_from_folder',
    'integrate_import_functions'
]
