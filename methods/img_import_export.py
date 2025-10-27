#this belongs in methods/img_import_export.py - Version: 1
# X-Seti - September11 2025 - IMG Factory 1.5 - IMG Import Export - Ported from Modern System

"""
IMG Import Export - Ported working functions from modern IMG Editor system
Handles importing files into and exporting entries from IMG archives with proper error handling
"""

import os
import struct
import math
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from methods.img_entry_operations import add_entry_safe, add_multiple_entries

##Methods list -
# import_file
# import_multiple_files
# import_folder
# import_via_ide
# export_entry
# export_all
# export_by_type
# validate_import_file
# get_import_preview
# integrate_import_export_functions

# Constants
SECTOR_SIZE = 2048
MAX_FILENAME_LENGTH = 24

def import_file(img_archive, file_path: str, entry_name: Optional[str] = None) -> bool: #vers 1
    """Import a file into an IMG archive - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not os.path.exists(file_path):
            if img_debugger:
                img_debugger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine entry name
        if not entry_name:
            entry_name = os.path.basename(file_path)
        
        if img_debugger:
            img_debugger.debug(f"Importing file: {file_path} as {entry_name}")
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        if img_debugger:
            img_debugger.debug(f"Read {len(file_data)} bytes from {file_path}")
        
        # Use the add_entry method from the archive or fallback to add_entry_safe
        if hasattr(img_archive, 'add_entry') and callable(img_archive.add_entry):
            success = img_archive.add_entry(entry_name, file_data)
        else:
            success = add_entry_safe(img_archive, entry_name, file_data)
        
        if success:
            if img_debugger:
                img_debugger.success(f"Successfully imported: {entry_name}")
            return True
        else:
            if img_debugger:
                img_debugger.error(f"Failed to add entry to archive: {entry_name}")
            return False
                
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to import file {file_path}: {str(e)}")
        else:
            print(f"[ERROR] import_file failed: {e}")
        return False

def import_multiple_files(img_archive, file_paths: List[str], entry_names: Optional[List[str]] = None) -> Tuple[List, List]: #vers 1
    """Import multiple files into an IMG archive - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not file_paths:
            return [], []
        
        # Validate entry_names list if provided
        if entry_names and len(entry_names) != len(file_paths):
            raise ValueError("entry_names list must be same length as file_paths list")
        
        imported_entries = []
        failed_files = []
        
        if img_debugger:
            img_debugger.info(f"Starting batch import of {len(file_paths)} files")
        
        for i, file_path in enumerate(file_paths):
            try:
                # Determine entry name
                if entry_names:
                    entry_name = entry_names[i]
                else:
                    entry_name = os.path.basename(file_path)
                
                if img_debugger:
                    img_debugger.debug(f"Importing file {i+1}/{len(file_paths)}: {file_path} as {entry_name}")
                
                success = import_file(img_archive, file_path, entry_name)
                if success:
                    imported_entries.append(entry_name)
                    if img_debugger:
                        img_debugger.info(f"Successfully imported {i+1}/{len(file_paths)}: {entry_name}")
                else:
                    failed_files.append(file_path)
                    if img_debugger:
                        img_debugger.error(f"Failed to import {i+1}/{len(file_paths)}: {file_path}")
                        
            except Exception as e:
                failed_files.append(file_path)
                if img_debugger:
                    img_debugger.error(f"Exception importing {file_path}: {str(e)}")
        
        if img_debugger:
            img_debugger.success(f"Batch import completed: {len(imported_entries)} success, {len(failed_files)} failed")
        
        return imported_entries, failed_files
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Batch import failed: {e}")
        else:
            print(f"[ERROR] import_multiple_files failed: {e}")
        return [], file_paths

def import_folder(img_archive, folder_path: str, recursive: bool = False, filter_extensions: Optional[List[str]] = None) -> Tuple[List, List]: #vers 1
    """Import all files from a folder into an IMG archive - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Folder not found: {folder_path}")
        
        imported_entries = []
        failed_files = []
        
        if img_debugger:
            img_debugger.info(f"Starting folder import: {folder_path} (recursive={recursive})")
        
        # Walk through directory
        for root, dirs, files in os.walk(folder_path):
            if img_debugger:
                img_debugger.debug(f"Processing directory: {root}")
            
            for file in files:
                # Check extension if filter is provided
                if filter_extensions:
                    ext = os.path.splitext(file)[1].lower().lstrip('.')
                    if ext not in [e.lower().lstrip('.') for e in filter_extensions]:
                        if img_debugger:
                            img_debugger.debug(f"Skipping file due to extension filter: {file} (ext: {ext})")
                        continue
                
                file_path = os.path.join(root, file)
                
                # For entries from subdirectories, maintain relative path if recursive is True
                if recursive and root != folder_path:
                    rel_path = os.path.relpath(root, folder_path)
                    entry_name = os.path.join(rel_path, file).replace('\\', '/')
                else:
                    entry_name = file
                
                try:
                    if img_debugger:
                        img_debugger.debug(f"Attempting to import: {file_path} as {entry_name}")
                    
                    success = import_file(img_archive, file_path, entry_name)
                    if success:
                        imported_entries.append(entry_name)
                        if img_debugger:
                            img_debugger.info(f"Successfully imported: {entry_name}")
                    else:
                        failed_files.append(file_path)
                        if img_debugger:
                            img_debugger.error(f"Failed to import: {file_path}")
                            
                except Exception as e:
                    failed_files.append(file_path)
                    if img_debugger:
                        img_debugger.error(f"Exception importing {file_path}: {str(e)}")
            
            # If not recursive, don't process subdirectories
            if not recursive:
                break
        
        if img_debugger:
            img_debugger.success(f"Folder import completed: {len(imported_entries)} success, {len(failed_files)} failed")
        
        return imported_entries, failed_files
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Folder import failed: {e}")
        else:
            print(f"[ERROR] import_folder failed: {e}")
        return [], []

def import_via_ide(img_archive, ide_file_path: str, models_directory: str) -> Tuple[List, List, Dict]: #vers 1
    """Import DFF models and TXD textures from an IDE file - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not os.path.exists(ide_file_path):
            raise FileNotFoundError(f"IDE file not found: {ide_file_path}")
        
        imported_entries = []
        failed_files = []
        parsed_info = {
            'objs_count': 0,
            'tobj_count': 0,
            'unique_models': set(),
            'unique_textures': set(),
            'found_models': [],
            'found_textures': [],
            'missing_models': [],
            'missing_textures': []
        }
        
        if img_debugger:
            img_debugger.info(f"Starting IDE import: {ide_file_path}")
        
        # Parse IDE file
        models, textures = _parse_ide_file(ide_file_path, parsed_info)
        
        if not models and not textures:
            if img_debugger:
                img_debugger.warning(f"No models or textures found in IDE file: {ide_file_path}")
            return imported_entries, failed_files, parsed_info
        
        # Find and import DFF files
        for model_name in models:
            dff_path = _find_file_in_directory(models_directory, f"{model_name}.dff")
            if dff_path:
                parsed_info['found_models'].append(model_name)
                try:
                    success = import_file(img_archive, dff_path)
                    if success:
                        imported_entries.append(f"{model_name}.dff")
                        if img_debugger:
                            img_debugger.info(f"Imported model: {model_name}.dff")
                    else:
                        failed_files.append(dff_path)
                        if img_debugger:
                            img_debugger.error(f"Failed to import model: {dff_path}")
                except Exception as e:
                    failed_files.append(dff_path)
                    if img_debugger:
                        img_debugger.error(f"Exception importing model {dff_path}: {str(e)}")
            else:
                parsed_info['missing_models'].append(model_name)
                if img_debugger:
                    img_debugger.warning(f"Model file not found: {model_name}.dff")
        
        # Find and import TXD files
        for texture_name in textures:
            txd_path = _find_file_in_directory(models_directory, f"{texture_name}.txd")
            if txd_path:
                parsed_info['found_textures'].append(texture_name)
                try:
                    success = import_file(img_archive, txd_path)
                    if success:
                        imported_entries.append(f"{texture_name}.txd")
                        if img_debugger:
                            img_debugger.info(f"Imported texture: {texture_name}.txd")
                    else:
                        failed_files.append(txd_path)
                        if img_debugger:
                            img_debugger.error(f"Failed to import texture: {txd_path}")
                except Exception as e:
                    failed_files.append(txd_path)
                    if img_debugger:
                        img_debugger.error(f"Exception importing texture {txd_path}: {str(e)}")
            else:
                parsed_info['missing_textures'].append(texture_name)
                if img_debugger:
                    img_debugger.warning(f"Texture file not found: {texture_name}.txd")
        
        if img_debugger:
            img_debugger.success(f"IDE import completed: {len(imported_entries)} imported, {len(failed_files)} failed")
        
        return imported_entries, failed_files, parsed_info
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"IDE import failed: {e}")
        else:
            print(f"[ERROR] import_via_ide failed: {e}")
        return [], [], {}

def _parse_ide_file(ide_file_path: str, parsed_info: Dict) -> Tuple[set, set]: #vers 1
    """Parse IDE file to extract model and texture names - HELPER FUNCTION"""
    models = set()
    textures = set()
    current_section = None
    
    try:
        with open(ide_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith(';'):
                    continue
                
                # Check for section headers
                if line.lower() == 'objs':
                    current_section = 'objs'
                    continue
                elif line.lower() == 'tobj':
                    current_section = 'tobj'
                    continue
                elif line.lower() == 'end':
                    current_section = None
                    continue
                
                # Parse entries based on current section
                if current_section in ['objs', 'tobj']:
                    try:
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 3:  # Need at least ID, ModelName, TextureName
                            model_name = parts[1].strip()
                            texture_name = parts[2].strip()
                            
                            # Validate names (should not be empty or numeric IDs)
                            if model_name and not model_name.isdigit() and model_name != '-1':
                                models.add(model_name)
                                parsed_info['unique_models'].add(model_name)
                            
                            if texture_name and not texture_name.isdigit() and texture_name != '-1':
                                textures.add(texture_name)
                                parsed_info['unique_textures'].add(texture_name)
                            
                            if current_section == 'objs':
                                parsed_info['objs_count'] += 1
                            else:
                                parsed_info['tobj_count'] += 1
                                
                    except Exception as e:
                        continue  # Skip malformed lines
    
    except Exception as e:
        raise Exception(f"Failed to read IDE file: {str(e)}")
    
    return models, textures

def _find_file_in_directory(directory: str, filename: str, recursive: bool = True) -> Optional[str]: #vers 1
    """Find a file in a directory (case-insensitive search) - HELPER FUNCTION"""
    filename_lower = filename.lower()
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == filename_lower:
                    return os.path.join(root, file)
    else:
        try:
            for file in os.listdir(directory):
                if file.lower() == filename_lower:
                    return os.path.join(directory, file)
        except OSError:
            pass
    
    return None

def export_entry(img_archive, entry, output_path: Optional[str] = None, output_dir: Optional[str] = None) -> str: #vers 1
    """Export an entry from an IMG archive to a file - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        if not output_path and not output_dir:
            raise ValueError("Either output_path or output_dir must be provided")
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, entry.name)
        
        # Check if entry has in-memory data (new/modified entries)
        if hasattr(entry, 'is_new_entry') and entry.is_new_entry and hasattr(entry, 'data') and entry.data:
            if img_debugger:
                img_debugger.debug(f"Exporting new/modified entry from memory: {entry.name}")
            data_to_write = entry.data
        else:
            # Read entry data from file if not already loaded
            if not hasattr(entry, 'data') or not entry.data:
                if img_debugger:
                    img_debugger.debug(f"Reading entry data from file: {entry.name}")
                with open(img_archive.file_path, 'rb') as f:
                    f.seek(entry.actual_offset)
                    data_to_write = f.read(entry.actual_size)
            else:
                data_to_write = entry.data
        
        # Write data to output file
        with open(output_path, 'wb') as f:
            f.write(data_to_write)
        
        if img_debugger:
            img_debugger.success(f"Exported entry: {entry.name} to {output_path} ({len(data_to_write)} bytes)")
        
        return output_path
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Failed to export entry {entry.name}: {str(e)}")
        else:
            print(f"[ERROR] export_entry failed: {e}")
        raise

def export_all(img_archive, output_dir: str, filter_type: Optional[str] = None) -> Tuple[List[str], List]: #vers 1
    """Export all entries from an IMG archive - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = []
        failed_entries = []
        
        if img_debugger:
            img_debugger.info(f"Starting export all: {len(img_archive.entries)} entries")
        
        for entry in img_archive.entries:
            # Apply type filter if provided
            if filter_type and hasattr(entry, 'type') and entry.type != filter_type:
                continue
            
            try:
                output_path = export_entry(img_archive, entry, output_dir=output_dir)
                exported_files.append(output_path)
            except Exception as e:
                failed_entries.append(entry)
                if img_debugger:
                    img_debugger.error(f"Error exporting {entry.name}: {str(e)}")
        
        if img_debugger:
            img_debugger.success(f"Export all completed: {len(exported_files)} success, {len(failed_entries)} failed")
        
        return exported_files, failed_entries
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Export all failed: {e}")
        else:
            print(f"[ERROR] export_all failed: {e}")
        return [], []

def export_by_type(img_archive, output_dir: str, types: List[str]) -> Dict: #vers 1
    """Export entries of specific types from an IMG archive - PORTED FROM MODERN SYSTEM"""
    try:
        # Import debug system
        try:
            from debug.img_debug_functions import img_debugger
        except ImportError:
            img_debugger = None
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        for t in types:
            results[t] = ([], [])  # (exported_files, failed_entries)
        
        if img_debugger:
            img_debugger.info(f"Starting export by type: {types}")
        
        for entry in img_archive.entries:
            # Check if entry type is in requested types
            if hasattr(entry, 'type') and entry.type in types:
                try:
                    # Create type-specific subdirectory
                    type_dir = os.path.join(output_dir, entry.type)
                    os.makedirs(type_dir, exist_ok=True)
                    
                    output_path = export_entry(img_archive, entry, output_dir=type_dir)
                    results[entry.type][0].append(output_path)  # Add to exported_files
                except Exception as e:
                    results[entry.type][1].append(entry)  # Add to failed_entries
                    if img_debugger:
                        img_debugger.error(f"Error exporting {entry.name}: {str(e)}")
        
        # Print summary
        for file_type, (exported, failed) in results.items():
            if img_debugger:
                img_debugger.info(f"Export by type summary - {file_type}: {len(exported)} exported, {len(failed)} failed")
        
        return results
        
    except Exception as e:
        if img_debugger:
            img_debugger.error(f"Export by type failed: {e}")
        else:
            print(f"[ERROR] export_by_type failed: {e}")
        return {}

def validate_import_file(file_path: str, max_size_mb: Optional[int] = None) -> Tuple[bool, str]: #vers 1
    """Validate a file before importing - PORTED FROM MODERN SYSTEM"""
    try:
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, f"File is empty: {file_path}"
        
        if max_size_mb and file_size > (max_size_mb * 1024 * 1024):
            return False, f"File too large ({file_size / (1024*1024):.1f}MB > {max_size_mb}MB): {file_path}"
        
        # Check filename
        filename = os.path.basename(file_path)
        if len(filename.encode('ascii', errors='replace')) >= MAX_FILENAME_LENGTH:
            return False, f"Filename too long (>{MAX_FILENAME_LENGTH-1} chars): {filename}"
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)  # Try to read at least 1 byte
        except PermissionError:
            return False, f"Permission denied reading file: {file_path}"
        except Exception as e:
            return False, f"Cannot read file: {file_path} - {str(e)}"
        
        return True, "File is valid for import"
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def get_import_preview(img_archive, file_paths: List[str]) -> Dict: #vers 1
    """Get a preview of what would happen if files were imported - PORTED FROM MODERN SYSTEM"""
    try:
        preview = {
            'total_files': len(file_paths),
            'valid_files': [],
            'invalid_files': [],
            'would_replace': [],
            'would_add': [],
            'total_size_bytes': 0,
            'total_size_sectors': 0
        }
        
        for file_path in file_paths:
            # Validate file
            is_valid, error_msg = validate_import_file(file_path)
            
            if not is_valid:
                preview['invalid_files'].append({
                    'file_path': file_path,
                    'error': error_msg
                })
                continue
            
            # File is valid
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            preview['valid_files'].append(file_path)
            preview['total_size_bytes'] += file_size
            preview['total_size_sectors'] += math.ceil(file_size / SECTOR_SIZE)
            
            # Check if would replace existing entry
            existing_entry = None
            if hasattr(img_archive, 'get_entry_by_name'):
                existing_entry = img_archive.get_entry_by_name(filename)
            
            if existing_entry:
                preview['would_replace'].append({
                    'file_path': file_path,
                    'entry_name': filename,
                    'existing_entry': existing_entry
                })
            else:
                preview['would_add'].append({
                    'file_path': file_path,
                    'entry_name': filename
                })
        
        return preview
        
    except Exception as e:
        print(f"[ERROR] get_import_preview failed: {e}")
        return {'total_files': len(file_paths), 'valid_files': [], 'invalid_files': [], 'would_replace': [], 'would_add': [], 'total_size_bytes': 0, 'total_size_sectors': 0}

def integrate_import_export_functions(main_window) -> bool: #vers 1
    """Integrate import/export functions with main window - PORTED FROM MODERN SYSTEM"""
    try:
        # Add import/export methods to main window
        main_window.import_file = lambda img_archive, file_path, entry_name=None: import_file(img_archive, file_path, entry_name)
        main_window.import_multiple_files = lambda img_archive, file_paths, entry_names=None: import_multiple_files(img_archive, file_paths, entry_names)
        main_window.import_folder = lambda img_archive, folder_path, recursive=False, filter_extensions=None: import_folder(img_archive, folder_path, recursive, filter_extensions)
        main_window.import_via_ide = lambda img_archive, ide_file_path, models_directory: import_via_ide(img_archive, ide_file_path, models_directory)
        main_window.export_entry = lambda img_archive, entry, output_path=None, output_dir=None: export_entry(img_archive, entry, output_path, output_dir)
        main_window.export_all = lambda img_archive, output_dir, filter_type=None: export_all(img_archive, output_dir, filter_type)
        main_window.export_by_type = lambda img_archive, output_dir, types: export_by_type(img_archive, output_dir, types)
        main_window.validate_import_file = lambda file_path, max_size_mb=None: validate_import_file(file_path, max_size_mb)
        main_window.get_import_preview = lambda img_archive, file_paths: get_import_preview(img_archive, file_paths)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("Import/Export functions integrated - PORTED from modern system")
            main_window.log_message("   • File import with proper validation")
            main_window.log_message("   • Batch operations for multiple files")
            main_window.log_message("   • IDE-based import with model/texture detection")
            main_window.log_message("   • Export with type filtering")
            main_window.log_message("   • Import preview and validation")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Import/Export integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'import_file',
    'import_multiple_files',
    'import_folder', 
    'import_via_ide',
    'export_entry',
    'export_all',
    'export_by_type',
    'validate_import_file',
    'get_import_preview',
    'integrate_import_export_functions'
]
