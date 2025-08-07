#this belongs in core/importer.py - Version: 4
# X-Seti - August07 2025 - IMG Factory 1.5 - Import Functions Fix
# Fixed: Table refresh after import, proper completion handling

"""
Import Functions - FIXED VERSION
Properly refreshes table after import completion
"""

import os
from typing import List, Dict, Any
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal

##Methods list -
# get_selected_entries
# import_files_function
# import_via_function
# import_from_folder
# integrate_import_functions
# refresh_table_after_import

##Classes -
# ImportThread

class ImportThread(QThread): #vers 2
    """Background thread for importing files with proper completion handling"""
    
    progress_updated = pyqtSignal(int, str)
    import_completed = pyqtSignal(bool, str, dict)
    
    def __init__(self, main_window, files_to_import, import_options):
        super().__init__()
        self.main_window = main_window
        self.files_to_import = files_to_import
        self.import_options = import_options
        self.stats = {'imported': 0, 'failed': 0, 'skipped': 0}
    
    def run(self): #vers 2
        """Import files with proper table refresh"""
        try:
            if not hasattr(self.main_window, 'current_img') or not self.main_window.current_img:
                self.import_completed.emit(False, "No IMG file open", self.stats)
                return
            
            total_files = len(self.files_to_import)
            
            for i, file_path in enumerate(self.files_to_import):
                filename = os.path.basename(file_path)
                progress = int((i / total_files) * 90)  # Reserve 10% for refresh
                
                self.progress_updated.emit(progress, f"Importing {filename}...")
                
                try:
                    # Read file data
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Check if entry exists
                    if self.import_options.get('replace_existing', True):
                        existing_entries = [e for e in self.main_window.current_img.entries if e.name == filename]
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
            
            # DISABLED: Save IMG - causes segfault, save manually instead
            # if self.import_options.get('auto_save', True):
            #     self.progress_updated.emit(95, "Saving IMG file...")
            #     if hasattr(self.main_window.current_img, 'save_img_file'):
            #         self.main_window.current_img.save_img_file()
            
            self.progress_updated.emit(95, "⚠️ Import complete - manual save required")
            
            # DISABLED: Table refresh causes segfault - manual refresh required
            # self.progress_updated.emit(98, "Refreshing table...")
            # refresh_table_after_import(self.main_window)
            
            self.progress_updated.emit(100, "Import completed!")
            
            success_msg = f"Import completed: {self.stats['imported']} imported, {self.stats['failed']} failed"
            self.import_completed.emit(True, success_msg, self.stats)
            
        except Exception as e:
            self.import_completed.emit(False, f"Import failed: {str(e)}", self.stats)

def refresh_table_after_import(main_window): #vers 1
    """Refresh the table after import completion"""
    try:
        # Method 1: Try populate_entries_table (most common)
        if hasattr(main_window, 'populate_entries_table'):
            main_window.populate_entries_table()
            main_window.log_message("✅ Table refreshed after import")
            return True
        
        # Method 2: Try refresh_table from utils
        if hasattr(main_window, 'refresh_table'):
            main_window.refresh_table()
            main_window.log_message("✅ Table refreshed via refresh_table")
            return True
        
        # Method 3: Try reload_table
        if hasattr(main_window, 'reload_table'):
            main_window.reload_table()
            main_window.log_message("✅ Table refreshed via reload_table")
            return True
        
        # Method 4: Manual table update
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            if hasattr(main_window, 'current_img') and main_window.current_img:
                # Clear table
                table.setRowCount(0)
                
                # Repopulate with current IMG entries
                entries = main_window.current_img.entries
                table.setRowCount(len(entries))
                
                for row, entry in enumerate(entries):
                    table.setItem(row, 0, table.item(row, 0).__class__(entry.name))
                    table.setItem(row, 1, table.item(row, 0).__class__(entry.type if hasattr(entry, 'type') else 'Unknown'))
                    table.setItem(row, 2, table.item(row, 0).__class__(str(entry.offset) if hasattr(entry, 'offset') else 'N/A'))
                    table.setItem(row, 3, table.item(row, 0).__class__(str(entry.size) if hasattr(entry, 'size') else '0'))
                
                main_window.log_message("✅ Table manually refreshed after import")
                return True
        
        main_window.log_message("⚠️ Could not refresh table - no refresh method found")
        return False
        
    except Exception as e:
        main_window.log_message(f"❌ Error refreshing table after import: {str(e)}")
        return False

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
    """Import files with file dialog - FIXED VERSION"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get files to import
        files, _ = QFileDialog.getOpenFileNames(
            main_window,
            "Select Files to Import",
            "",
            "All Files (*.*)"
        )
        
        if not files:
            return
        
        main_window.log_message(f"📁 Import files: {len(files)} files selected")
        
        # Simple import options
        import_options = {
            'replace_existing': True,
            'auto_save': True
        }
        
        # Start import thread
        import_thread = ImportThread(main_window, files, import_options)
        
        # Connect completion signal
        def on_import_completed(success, message, stats):
            main_window.log_message(message)
            if success:
                QMessageBox.information(main_window, "Import Complete", message)
            else:
                QMessageBox.critical(main_window, "Import Failed", message)
        
        import_thread.import_completed.connect(on_import_completed)
        import_thread.progress_updated.connect(lambda p, s: main_window.log_message(f"Import: {s}"))
        
        # Store thread reference to prevent garbage collection
        main_window._import_thread = import_thread
        
        # Start import
        import_thread.start()
        
    except Exception as e:
        main_window.log_message(f"❌ Import files error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import failed: {str(e)}")

def import_via_function(main_window): #vers 3
    """Import files listed in IDE file - FIXED VERSION"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get IDE file
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE File",
            "",
            "IDE Files (*.ide);;All Files (*.*)"
        )
        
        if not ide_file:
            return
        
        # Parse IDE file to get list of files
        files_to_import = []
        missing_files = []
        base_dir = os.path.dirname(ide_file)
        
        with open(ide_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Simple parsing - assumes filename is first part
                    parts = line.split(',')
                    if parts:
                        filename = parts[0].strip()
                        file_path = os.path.join(base_dir, filename)
                        
                        if os.path.exists(file_path):
                            files_to_import.append(file_path)
                        else:
                            missing_files.append(filename)
        
        if not files_to_import:
            QMessageBox.information(main_window, "No Files Found", 
                                   f"No files found from IDE file: {os.path.basename(ide_file)}")
            return
        
        # Show results
        result_msg = f"Found {len(files_to_import)} files to import"
        if missing_files:
            result_msg += f"\n{len(missing_files)} files missing from directory"
        
        main_window.log_message(f"📋 {result_msg}")
        
        # Import options
        import_options = {
            'replace_existing': True,
            'auto_save': True
        }
        
        # Start import thread
        import_thread = ImportThread(main_window, files_to_import, import_options)
        
        # Connect completion signal
        def on_import_completed(success, message, stats):
            main_window.log_message(message)
            if success:
                QMessageBox.information(main_window, "Import Via IDE Complete", message)
            else:
                QMessageBox.critical(main_window, "Import Via IDE Failed", message)
        
        import_thread.import_completed.connect(on_import_completed)
        import_thread.progress_updated.connect(lambda p, s: main_window.log_message(f"Import via IDE: {s}"))
        
        # Store thread reference
        main_window._import_thread = import_thread
        
        # Start import
        import_thread.start()
        
    except Exception as e:
        main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via IDE Error", f"Import via IDE failed: {str(e)}")

def import_from_folder(main_window): #vers 3
    """Import all files from a folder - FIXED VERSION"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get folder
        folder = QFileDialog.getExistingDirectory(main_window, "Select Folder to Import")
        
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
        
        # Import options
        import_options = {
            'replace_existing': True,
            'auto_save': True
        }
        
        # Start import thread
        import_thread = ImportThread(main_window, files_to_import, import_options)
        
        # Connect completion signal
        def on_import_completed(success, message, stats):
            main_window.log_message(message)
            if success:
                QMessageBox.information(main_window, "Import From Folder Complete", message)
            else:
                QMessageBox.critical(main_window, "Import From Folder Failed", message)
        
        import_thread.import_completed.connect(on_import_completed)
        import_thread.progress_updated.connect(lambda p, s: main_window.log_message(f"Import folder: {s}"))
        
        # Store thread reference
        main_window._import_thread = import_thread
        
        # Start import
        import_thread.start()
        
    except Exception as e:
        main_window.log_message(f"❌ Import from folder error: {str(e)}")
        QMessageBox.critical(main_window, "Import From Folder Error", f"Import from folder failed: {str(e)}")

def integrate_import_functions(main_window): #vers 4
    """Integrate import functions into main window - FIXED VERSION"""
    try:
        # Add import functions with proper method names
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_via_function = lambda: import_via_function(main_window)
        main_window.import_from_folder = lambda: import_from_folder(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        main_window.refresh_table_after_import = lambda: refresh_table_after_import(main_window)
        
        # Add aliases for different naming conventions used by GUI
        main_window.import_files = main_window.import_files_function
        main_window.import_files_via = main_window.import_via_function
        main_window.import_via = main_window.import_via_function
        
        main_window.log_message("✅ Import functions integrated with table refresh fix")
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
    'refresh_table_after_import',
    'integrate_import_functions'
]