#this belongs in components/ img_import_export.py - Version: 2
# X-Seti - July13 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Import/Export Support - Legacy compatibility and special functions
Contains only unique functionality not duplicated in img_import_export_functions.py
"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

def integrate_import_export_system(main_window):
    """Legacy compatibility function - redirects to new system"""
    try:
        # Import the new consolidated function
        from components.img_import_export_functions import integrate_clean_import_export
        
        # Use the new consolidated system
        success = integrate_clean_import_export(main_window)
        
        if success:
            main_window.log_message("✅ Import/Export system integrated (legacy compatibility)")
        else:
            main_window.log_message("❌ Failed to integrate import/export system")
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Legacy integration error: {str(e)}")
        return False


# ============================================================================
# SPECIALIZED IMPORT/EXPORT FUNCTIONS
# ============================================================================

def import_files_threaded(main_window, file_paths: List[str], options: dict = None):
    """Legacy threaded import function - redirects to new system"""
    try:
        if options is None:
            options = {
                'files': file_paths,
                'overwrite_existing': False,
                'validate_files': True,
                'organize_by_type': False
            }
        else:
            options['files'] = file_paths
        
        # Use the new threaded import
        from components.img_import_export_functions import _import_files_threaded
        _import_files_threaded(main_window, options)
        
    except Exception as e:
        main_window.log_message(f"❌ Legacy threaded import error: {str(e)}")


def export_files_threaded(main_window, entries: List, output_dir: str, options: dict = None):
    """Legacy threaded export function - redirects to new system"""
    try:
        if options is None:
            options = {
                'selected_entries': entries,
                'output_directory': output_dir,
                'organize_by_type': False,
                'create_ide_file': False,
                'overwrite_existing': True
            }
        else:
            options['selected_entries'] = entries
            options['output_directory'] = output_dir
        
        # Use the new threaded export
        from components.img_import_export_functions import _export_files_threaded
        _export_files_threaded(main_window, options)
        
    except Exception as e:
        main_window.log_message(f"❌ Legacy threaded export error: {str(e)}")


def show_import_dialog(main_window):
    """Legacy import dialog function - redirects to new system"""
    try:
        from components.img_import_export_functions import import_files_function
        import_files_function(main_window)
    except Exception as e:
        main_window.log_message(f"❌ Legacy import dialog error: {str(e)}")


def show_export_dialog(main_window, entries: List = None):
    """Legacy export dialog function - redirects to new system"""
    try:
        if entries:
            # Export specific entries
            from components.img_import_export_functions import export_selected_function
            # Temporarily set the entries as selected (this is a workaround)
            original_get_selected = getattr(main_window, 'get_selected_entries', None)
            main_window.get_selected_entries = lambda: entries
            
            export_selected_function(main_window)
            
            # Restore original function
            if original_get_selected:
                main_window.get_selected_entries = original_get_selected
        else:
            # Export all entries
            from components.img_import_export_functions import export_all_function
            export_all_function(main_window)
            
    except Exception as e:
        main_window.log_message(f"❌ Legacy export dialog error: {str(e)}")


# ============================================================================
# SPECIALIZED UTILITY FUNCTIONS
# ============================================================================

def dump_all_entries(main_window, output_directory: str = None):
    """Legacy dump function - redirects to new system"""
    try:
        if output_directory:
            # Direct dump to specified directory
            if not hasattr(main_window, 'current_img') or not main_window.current_img:
                QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
                return
            
            all_entries = main_window.current_img.entries if hasattr(main_window.current_img, 'entries') else []
            if not all_entries:
                QMessageBox.information(main_window, "Dump All", "No entries found in current IMG file.")
                return
            
            # Use new system for actual dumping
            options = {
                'selected_entries': all_entries,
                'output_directory': output_directory,
                'organize_by_type': False,
                'create_ide_file': True,
                'overwrite_existing': True
            }
            
            from components.img_import_export_functions import _export_files_threaded
            _export_files_threaded(main_window, options)
        else:
            # Use dialog-based dump
            from components.img_import_export_functions import dump_all_function
            dump_all_function(main_window)
            
    except Exception as e:
        main_window.log_message(f"❌ Legacy dump error: {str(e)}")


def import_from_ide_file(main_window, ide_file_path: str = None):
    """Legacy IDE import function - redirects to new system"""
    try:
        if ide_file_path:
            # Direct IDE import
            files_to_import = []
            base_dir = os.path.dirname(ide_file_path)
            
            with open(ide_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            filename = parts[0]
                            relative_path = parts[1]
                            full_path = os.path.join(base_dir, relative_path)
                            
                            if os.path.exists(full_path):
                                files_to_import.append(full_path)
            
            if files_to_import:
                options = {
                    'files': files_to_import,
                    'overwrite_existing': False,
                    'validate_files': True,
                    'organize_by_type': False
                }
                from components.img_import_export_functions import _import_files_threaded
                _import_files_threaded(main_window, options)
            else:
                QMessageBox.information(main_window, "IDE Import", "No valid files found in IDE file.")
        else:
            # Use dialog-based IDE import
            from components.img_import_export_functions import import_from_ide_file as new_ide_import
            new_ide_import(main_window)
            
    except Exception as e:
        main_window.log_message(f"❌ Legacy IDE import error: {str(e)}")


# ============================================================================
# SPECIAL COMPATIBILITY FUNCTIONS
# ============================================================================

def get_selected_entries(main_window):
    """Legacy function - redirects to new system"""
    try:
        from components.img_import_export_functions import get_selected_entries as new_get_selected
        return new_get_selected(main_window)
    except Exception:
        return []


def validate_import_files(file_paths: List[str]) -> tuple:
    """Validate files before import - specialized function"""
    try:
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Check file size
                size = os.path.getsize(file_path)
                if size > 0:
                    # Check extension
                    filename = os.path.basename(file_path)
                    if '.' in filename:
                        ext = filename.split('.')[-1].lower()
                        if ext in ['dff', 'txd', 'col', 'ifp', 'wav', 'scm', 'ide', 'ipl', 'dat']:
                            valid_files.append(file_path)
                        else:
                            invalid_files.append(file_path)
                    else:
                        # No extension, but might still be valid
                        valid_files.append(file_path)
                else:
                    invalid_files.append(file_path)
            else:
                invalid_files.append(file_path)
        
        return valid_files, invalid_files
        
    except Exception:
        return [], file_paths


def create_backup_before_import(main_window) -> bool:
    """Create backup of IMG before import operations"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            return False
        
        if not hasattr(main_window.current_img, 'file_path') or not main_window.current_img.file_path:
            return False
        
        source_path = main_window.current_img.file_path
        backup_path = f"{source_path}.backup"
        
        # Only create backup if it doesn't exist
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(source_path, backup_path)
            main_window.log_message(f"✅ Backup created: {backup_path}")
            return True
        else:
            main_window.log_message(f"ℹ️ Backup already exists: {backup_path}")
            return True
            
    except Exception as e:
        main_window.log_message(f"❌ Backup creation failed: {str(e)}")
        return False


def get_import_statistics(file_paths: List[str]) -> dict:
    """Get statistics about files to be imported"""
    try:
        stats = {
            'total_files': len(file_paths),
            'total_size': 0,
            'file_types': {},
            'largest_file': None,
            'smallest_file': None
        }
        
        largest_size = 0
        smallest_size = float('inf')
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                
                # Total size
                stats['total_size'] += size
                
                # File types
                if '.' in filename:
                    ext = filename.split('.')[-1].upper()
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                # Largest file
                if size > largest_size:
                    largest_size = size
                    stats['largest_file'] = {
                        'path': file_path,
                        'size': size
                    }
                
                # Smallest file
                if size < smallest_size and size > 0:
                    smallest_size = size
                    stats['smallest_file'] = {
                        'path': file_path,
                        'size': size
                    }
        
        return stats
        
    except Exception:
        return {'error': 'Failed to calculate statistics'}


# ============================================================================
# LEGACY DIALOG CLASSES (Kept for compatibility)
# ============================================================================

class ImportOptionsDialog:
    """Legacy compatibility - redirects to new dialog"""
    def __init__(self, parent=None):
        from components.img_import_export_functions import ImportOptionsDialog as NewDialog
        self._dialog = NewDialog(parent)
    
    def exec(self):
        return self._dialog.exec()
    
    def get_import_options(self):
        return self._dialog.get_import_options()


class ExportOptionsDialog:
    """Legacy compatibility - redirects to new dialog"""
    def __init__(self, entries, parent=None):
        from components.img_import_export_functions import ExportOptionsDialog as NewDialog
        self._dialog = NewDialog(entries, parent)
    
    def exec(self):
        return self._dialog.exec()
    
    def get_export_options(self):
        return self._dialog.get_export_options()


# ============================================================================
# THREAD CLASSES (Legacy compatibility)
# ============================================================================

class ImportThread:
    """Legacy compatibility - redirects to new thread"""
    def __init__(self, img_file, import_options):
        from components.img_import_export_functions import ImportThread as NewThread
        self._thread = NewThread(img_file, import_options)
    
    def start(self):
        return self._thread.start()
    
    def isRunning(self):
        return self._thread.isRunning()
    
    def terminate(self):
        return self._thread.terminate()
    
    def wait(self):
        return self._thread.wait()


class ExportThread:
    """Legacy compatibility - redirects to new thread"""
    def __init__(self, img_file, export_options):
        from components.img_import_export_functions import ExportThread as NewThread
        self._thread = NewThread(img_file, export_options)
    
    def start(self):
        return self._thread.start()
    
    def isRunning(self):
        return self._thread.isRunning()
    
    def terminate(self):
        return self._thread.terminate()
    
    def wait(self):
        return self._thread.wait()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Legacy compatibility functions
    'integrate_import_export_system',
    'show_import_dialog', 
    'show_export_dialog',
    'import_files_threaded', 
    'export_files_threaded',
    'import_from_ide_file', 
    'dump_all_entries',
    'get_selected_entries',
    
    # Specialized utility functions
    'validate_import_files',
    'create_backup_before_import',
    'get_import_statistics',
    
    # Legacy dialog classes
    'ImportOptionsDialog', 
    'ExportOptionsDialog',
    'ImportThread', 
    'ExportThread'
]