#this belongs in core/importer.py - Version: 5
# X-Seti - August07 2025 - IMG Factory 1.5 - Import Functions Fixed

"""
Import Functions - FIXED based on original windows_source IMGF patterns
Preserves autosave functionality and proper IMG integration
Replaces broken version 4 with working implementation
"""

import os
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt6.QtCore import QThread, pyqtSignal, Qt

##Methods list -
# add_file_to_img
# check_autosave_enabled
# get_selected_entries
# import_files_function
# import_via_function  
# integrate_import_functions_fixed
# refresh_img_table
# validate_import_file

##Classes -
# ImportWorker

class ImportWorker(QThread): #vers 1
    """Background import worker based on windows_source patterns"""
    
    progress_update = pyqtSignal(str)
    file_imported = pyqtSignal(str, bool)
    import_complete = pyqtSignal(int, int)  # imported_count, total_count
    
    def __init__(self, main_window, files_to_import: List[str], options: Dict):
        super().__init__()
        self.main_window = main_window
        self.files_to_import = files_to_import
        self.options = options
        self.imported_count = 0
        self.imported_files = []  # Track successfully imported files
        self.replaced_files = []  # Track files that were replaced
        
    def run(self): #vers 1
        """Import files using IMG core functionality"""
        try:
            total_files = len(self.files_to_import)
            
            for i, file_path in enumerate(self.files_to_import):
                filename = os.path.basename(file_path)
                self.progress_update.emit(f"Importing {filename}...")
                
                # Import single file
                success = self._import_single_file(file_path)
                
                if success:
                    self.imported_count += 1
                    self.imported_files.append(file_path)
                    
                    # Check if this was a replacement
                    filename = os.path.basename(file_path)
                    if self._was_file_replaced(filename):
                        self.replaced_files.append(file_path)
                    
                self.file_imported.emit(filename, success)
                
            self.import_complete.emit(self.imported_count, total_files)
            
        except Exception as e:
            self.main_window.log_message(f"❌ Import worker error: {str(e)}")
    
    def save_img_after_batch_import(self): #vers 1
        """Save IMG file after all imports are complete"""
        try:
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                # Use the save method from the IMG file
                if hasattr(self.main_window.current_img, 'save_img_file'):
                    return self.main_window.current_img.save_img_file()
                else:
                    # Fallback to save entry function
                    from core.save_img_entry import save_img_file_with_backup
                    return save_img_file_with_backup(self.main_window.current_img)
            return False
        except Exception as e:
            print(f"Error saving IMG after batch import: {e}")
            return False
            
    def _was_file_replaced(self, filename: str) -> bool: #vers 1
        """Check if file was replaced (existed before import)"""
        try:
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                # Check if entry already existed before import
                return any(entry.name == filename for entry in self.main_window.current_img.entries)
            return False
        except Exception:
            return False
            
    def _import_single_file(self, file_path: str) -> bool: #vers 1
        """Import single file using IMG core methods"""
        try:
            if not hasattr(self.main_window, 'current_img') or not self.main_window.current_img:
                return False
                
            filename = os.path.basename(file_path)
            
            # Check if file exists and is valid
            if not validate_import_file(file_path):
                return False
                
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # Use IMG core add_entry method
            success = add_file_to_img(self.main_window.current_img, filename, file_data, self.options)
            
            return success
            
        except Exception as e:
            print(f"Error importing {file_path}: {e}")
            return False

def validate_import_file(file_path: str) -> bool: #vers 1
    """Validate file before import"""
    try:
        if not os.path.exists(file_path):
            return False
            
        if not os.path.isfile(file_path):
            return False
            
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False
            
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            return False
            
        return True
        
    except Exception:
        return False

def add_file_to_img(img_file, filename: str, file_data: bytes, options: Dict) -> bool: #vers 1
    """Add file to IMG using core functionality with batch mode support"""
    try:
        # Check for existing entry
        if options.get('replace_existing', True):
            # Remove existing entry with same name
            if hasattr(img_file, 'entries'):
                img_file.entries = [e for e in img_file.entries if e.name != filename]
        
        # Add to IMG using core method with auto_save=False for batch mode
        if hasattr(img_file, 'add_entry'):
            return img_file.add_entry(filename, file_data, auto_save=False)
        elif hasattr(img_file, 'entries'):
            # Manual entry creation if add_entry doesn't exist
            from components.img_core_classes import IMGEntry
            
            entry = IMGEntry()
            entry.name = filename
            entry._cached_data = file_data
            entry.size = len(file_data)
            entry.offset = 0  # Will be calculated during save
            
            img_file.entries.append(entry)
            return True
            
        return False
        
    except Exception as e:
        print(f"Error adding file to IMG: {e}")
        return False

def refresh_img_table(main_window) -> bool: #vers 1
    """Refresh IMG table after import"""
    try:
        # Method 1: Use populate_entries_table if available
        if hasattr(main_window, 'populate_entries_table') and callable(main_window.populate_entries_table):
            main_window.populate_entries_table()
            return True
            
        # Method 2: Use table manager if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'populate_entries_table'):
            main_window.gui_layout.populate_entries_table()
            return True
            
        # Method 3: Manual table refresh
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            
            if hasattr(main_window, 'current_img') and main_window.current_img and hasattr(main_window.current_img, 'entries'):
                entries = main_window.current_img.entries
                
                # Clear and repopulate table
                table.setRowCount(len(entries))
                
                for row, entry in enumerate(entries):
                    from PyQt6.QtWidgets import QTableWidgetItem
                    
                    # Name column
                    name_item = QTableWidgetItem(entry.name)
                    table.setItem(row, 0, name_item)
                    
                    # Type column
                    file_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else 'Unknown'
                    type_item = QTableWidgetItem(file_ext)
                    table.setItem(row, 1, type_item)
                    
                    # Offset column
                    offset_item = QTableWidgetItem(str(getattr(entry, 'offset', 'N/A')))
                    table.setItem(row, 2, offset_item)
                    
                    # Size column
                    size_item = QTableWidgetItem(str(getattr(entry, 'size', len(getattr(entry, 'data', b'')))))
                    table.setItem(row, 3, size_item)
                    
                    # RW Version column (if exists)
                    if table.columnCount() > 4:
                        rw_item = QTableWidgetItem(getattr(entry, 'rw_version', 'Unknown'))
                        table.setItem(row, 4, rw_item)
                
                return True
                
        return False
        
    except Exception as e:
        print(f"Error refreshing table: {e}")
        return False

def check_autosave_enabled(main_window) -> bool: #vers 1
    """Check if autosave is enabled from autosave menu"""
    try:
        # Import autosave functionality
        from gui.autosave_menu import is_autosave_enabled
        return is_autosave_enabled(main_window)
    except ImportError:
        # Fallback to attribute check
        return getattr(main_window, 'autosave_enabled', False)

def get_selected_entries(main_window) -> List: #vers 1
    """Get selected entries from table"""
    selected_entries = []
    
    try:
        table = None
        
        # Find the table
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
        if hasattr(main_window, 'current_img') and main_window.current_img and hasattr(main_window.current_img, 'entries'):
            for row in selected_rows:
                if row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])
                    
    except Exception as e:
        print(f"Error getting selected entries: {e}")
        
    return selected_entries

def import_files_function(main_window): #vers 1
    """Import files with file dialog"""
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
        
        # Import options
        import_options = {
            'replace_existing': True,
            'validate_files': True
        }
        
        # Create progress dialog
        progress = QProgressDialog("Importing files...", "Cancel", 0, 0, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        # Create worker thread
        worker = ImportWorker(main_window, files, import_options)
        
        def on_progress_update(message):
            progress.setLabelText(message)
            
        def on_import_complete(imported_count, total_count):
            progress.close()
            
            # Collect imported filenames for highlighting
            imported_filenames = [os.path.basename(f) for f in files if f in worker.imported_files]
            replaced_filenames = [os.path.basename(f) for f in files if f in worker.replaced_files]
            
            # BATCH SAVE: Save IMG file once after all imports
            save_successful = False
            if imported_count > 0 and check_autosave_enabled(main_window):
                main_window.log_message(f"💾 Auto-saving IMG file after batch import ({imported_count} files)...")
                try:
                    save_successful = worker.save_img_after_batch_import()
                    if save_successful:
                        main_window.log_message("✅ IMG file auto-saved successfully")
                    else:
                        main_window.log_message("⚠️ Auto-save failed - manual save required")
                except Exception as e:
                    main_window.log_message(f"⚠️ Auto-save failed: {str(e)}")
            elif imported_count > 0:
                main_window.log_message("💾 Remember to save your IMG file manually (auto-save disabled)")
            
            # Refresh table with highlighting
            try:
                from methods.import_highlight_system import highlight_imported_files
                if highlight_imported_files(main_window, imported_filenames, replaced_filenames):
                    main_window.log_message("✅ Table refreshed with import highlights")
                else:
                    # Fallback to standard refresh
                    if refresh_img_table(main_window):
                        main_window.log_message("✅ Table refreshed after import")
            except ImportError:
                # Fallback if highlighting system not available
                if refresh_img_table(main_window):
                    main_window.log_message("✅ Table refreshed after import")
                
            # Show completion message
            success_msg = f"Import completed: {imported_count}/{total_count} files imported"
            if save_successful:
                success_msg += "\n💾 IMG file saved automatically"
            elif imported_count > 0:
                success_msg += "\n💾 Remember to save your IMG file manually"
            if imported_filenames:
                success_msg += f"\n✨ {len(imported_filenames)} files highlighted in green"
            if replaced_filenames:
                success_msg += f"\n🔄 {len(replaced_filenames)} files replaced (highlighted in yellow)"
            main_window.log_message(f"✅ {success_msg}")
            QMessageBox.information(main_window, "Import Complete", success_msg)
            
        def on_file_imported(filename, success):
            status = "✅" if success else "❌"
            main_window.log_message(f"{status} {filename}")
            
        # Connect signals
        worker.progress_update.connect(on_progress_update)
        worker.file_imported.connect(on_file_imported)
        worker.import_complete.connect(on_import_complete)
        
        # Connect cancel
        progress.canceled.connect(worker.terminate)
        
        # Store worker reference
        main_window._import_worker = worker
        
        # Start import
        worker.start()
        
    except Exception as e:
        main_window.log_message(f"❌ Import files error: {str(e)}")
        QMessageBox.critical(main_window, "Import Error", f"Import failed: {str(e)}")

def import_via_function(main_window): #vers 1
    """Import files listed in IDE file"""
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
        
        try:
            with open(ide_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and ',' in line:
                        # Parse IDE line - filename is typically first part
                        parts = [p.strip() for p in line.split(',')]
                        if parts:
                            filename = parts[0]
                            file_path = os.path.join(base_dir, filename)
                            
                            if os.path.exists(file_path):
                                files_to_import.append(file_path)
                            else:
                                missing_files.append(f"{filename} (line {line_num})")
                                
        except Exception as e:
            QMessageBox.critical(main_window, "IDE Parse Error", f"Failed to parse IDE file: {str(e)}")
            return
            
        if not files_to_import:
            if missing_files:
                missing_list = '\n'.join(missing_files[:10])  # Show first 10
                if len(missing_files) > 10:
                    missing_list += f"\n... and {len(missing_files) - 10} more"
                QMessageBox.information(main_window, "No Files Found", 
                                       f"No files found from IDE file.\n\nMissing files:\n{missing_list}")
            else:
                QMessageBox.information(main_window, "No Files Found", 
                                       f"No valid file entries found in IDE file: {os.path.basename(ide_file)}")
            return
            
        # Show results
        result_msg = f"Found {len(files_to_import)} files to import from IDE"
        if missing_files:
            result_msg += f"\n{len(missing_files)} files missing from directory"
            
        main_window.log_message(f"📋 {result_msg}")
        
        # Import options
        import_options = {
            'replace_existing': True,
            'validate_files': True
        }
        
        # Create progress dialog
        progress = QProgressDialog("Importing from IDE...", "Cancel", 0, 0, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        # Create worker thread
        worker = ImportWorker(main_window, files_to_import, import_options)
        
        def on_progress_update(message):
            progress.setLabelText(message)
            
        def on_import_complete(imported_count, total_count):
            progress.close()
            
            # Collect imported filenames for highlighting
            imported_filenames = [os.path.basename(f) for f in files_to_import if f in worker.imported_files]
            replaced_filenames = [os.path.basename(f) for f in files_to_import if f in worker.replaced_files]
            
            # BATCH SAVE: Save IMG file once after all imports
            save_successful = False
            if imported_count > 0 and check_autosave_enabled(main_window):
                main_window.log_message(f"💾 Auto-saving IMG file after batch import ({imported_count} files)...")
                try:
                    save_successful = worker.save_img_after_batch_import()
                    if save_successful:
                        main_window.log_message("✅ IMG file auto-saved successfully")
                    else:
                        main_window.log_message("⚠️ Auto-save failed - manual save required")
                except Exception as e:
                    main_window.log_message(f"⚠️ Auto-save failed: {str(e)}")
            elif imported_count > 0:
                main_window.log_message("💾 Remember to save your IMG file manually (auto-save disabled)")
            
            # Refresh table with highlighting
            try:
                from methods.import_highlight_system import highlight_imported_files
                if highlight_imported_files(main_window, imported_filenames, replaced_filenames):
                    main_window.log_message("✅ Table refreshed with import highlights")
                else:
                    # Fallback to standard refresh
                    if refresh_img_table(main_window):
                        main_window.log_message("✅ Table refreshed after IDE import")
            except ImportError:
                # Fallback if highlighting system not available
                if refresh_img_table(main_window):
                    main_window.log_message("✅ Table refreshed after IDE import")
                
            # Show completion message
            success_msg = f"Import via IDE completed: {imported_count}/{total_count} files imported"
            if missing_files:
                success_msg += f"\n{len(missing_files)} files were missing"
            if save_successful:
                success_msg += "\n💾 IMG file saved automatically"
            elif imported_count > 0:
                success_msg += "\n💾 Remember to save your IMG file manually"
            if imported_filenames:
                success_msg += f"\n✨ {len(imported_filenames)} files highlighted in green"
            if replaced_filenames:
                success_msg += f"\n🔄 {len(replaced_filenames)} files replaced (highlighted in yellow)"
            main_window.log_message(f"✅ {success_msg}")
            QMessageBox.information(main_window, "Import Via IDE Complete", success_msg)
            
        def on_file_imported(filename, success):
            status = "✅" if success else "❌"
            main_window.log_message(f"{status} {filename}")
            
        # Connect signals
        worker.progress_update.connect(on_progress_update)
        worker.file_imported.connect(on_file_imported)
        worker.import_complete.connect(on_import_complete)
        
        # Connect cancel
        progress.canceled.connect(worker.terminate)
        
        # Store worker reference
        main_window._import_worker = worker
        
        # Start import
        worker.start()
        
    except Exception as e:
        main_window.log_message(f"❌ Import via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Import Via IDE Error", f"Import via IDE failed: {str(e)}")

def integrate_import_functions(main_window): #vers 5
    """Integrate fixed import functions into main window - REPLACEMENT for broken version 4"""
    try:
        # Add import functions with proper method names
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_via_function = lambda: import_via_function(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        
        # Add aliases for different naming conventions used by GUI
        main_window.import_files = main_window.import_files_function
        main_window.import_files_via = main_window.import_via_function
        main_window.import_via = main_window.import_via_function
        
        # Ensure autosave menu is integrated
        try:
            from gui.autosave_menu import integrate_autosave_menu
            integrate_autosave_menu(main_window)
        except ImportError:
            main_window.log_message("⚠️ Autosave menu not found - manual save required")
            
        # Ensure highlighting system is integrated
        try:
            from methods.import_highlight_system import integrate_import_highlighting
            integrate_import_highlighting(main_window)
        except ImportError:
            main_window.log_message("⚠️ Import highlighting system not found - standard refresh only")
            
        main_window.log_message("✅ Fixed import functions integrated with highlighting support")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate fixed import functions: {str(e)}")
        return False
    """Integrate fixed import functions into main window"""
    try:
        # Add import functions with proper method names
        main_window.import_files_function = lambda: import_files_function(main_window)
        main_window.import_via_function = lambda: import_via_function(main_window)
        main_window.get_selected_entries = lambda: get_selected_entries(main_window)
        
        # Add aliases for different naming conventions used by GUI
        main_window.import_files = main_window.import_files_function
        main_window.import_files_via = main_window.import_via_function
        main_window.import_via = main_window.import_via_function
        
        # Ensure highlighting system is integrated
        try:
            from methods.import_highlight_system import integrate_import_highlighting
            integrate_import_highlighting(main_window)
        except ImportError:
            main_window.log_message("⚠️ Import highlighting system not found - standard refresh only")
            
        main_window.log_message("✅ Fixed import functions integrated with highlighting support")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate fixed import functions: {str(e)}")
        return False

# Export functions
__all__ = [
    'ImportWorker',
    'add_file_to_img',
    'check_autosave_enabled',
    'get_selected_entries',
    'import_files_function',
    'import_via_function',
    'integrate_import_functions',      # Main integration function (standard name)
    'refresh_img_table',
    'validate_import_file'
]