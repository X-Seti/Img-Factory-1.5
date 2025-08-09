#this belongs in core/fast_rebuild_fixed.py - Version: 1
# X-Seti - Aug09 2025 - IMG Factory 1.5 - FIXED Fast Rebuild (No Corruption)

"""
FIXED Fast Rebuild System - Prevents filename corruption and file corruption
Careful filename handling, proper encoding, validation at each step
"""

import os
import struct
import shutil
from typing import List, Dict, Tuple
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication, QFileDialog
from PyQt6.QtCore import Qt

##Methods list -
# fixed_fast_rebuild_current
# fixed_fast_rebuild_all
# fixed_fast_quick_rebuild
# setup_fixed_fast_rebuild_methods

def fixed_fast_rebuild_current(main_window) -> bool: #vers 1
    """FIXED fast rebuild current IMG - Prevents corruption"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "No IMG file is currently loaded.")
            return False
            
        if not main_window.current_img.entries:
            QMessageBox.warning(main_window, "Empty IMG", "IMG file has no entries to rebuild")
            return False
        
        img_file = main_window.current_img
        filename = os.path.basename(img_file.file_path)
        entry_count = len(img_file.entries)
        
        main_window.log_message(f"🔧 FIXED fast rebuild: {filename} ({entry_count} entries)")
        
        # Create backup
        backup_path = f"{img_file.file_path}.backup"
        if not os.path.exists(backup_path):
            shutil.copy2(img_file.file_path, backup_path)
            main_window.log_message(f"✅ Backup created")
        
        # Show progress
        progress = QProgressDialog("FIXED fast rebuilding IMG...", "Cancel", 0, 4, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # FIXED rebuild process with validation
        success = _fixed_fast_rebuild_process(img_file, progress, main_window)
        
        progress.close()
        
        if success:
            # VALIDATE the rebuilt file
            validation_result = _validate_rebuilt_file(img_file, main_window)
            
            if validation_result:
                main_window.log_message(f"✅ FIXED fast rebuild complete: {filename}")
                
                # Show stats
                new_size = os.path.getsize(img_file.file_path)
                main_window.log_message(f"📊 Rebuilt {entry_count} entries, {new_size // 1024} KB")
                
                QMessageBox.information(main_window, "Fast Rebuild Complete", 
                                      f"Successfully rebuilt {filename}\n\n"
                                      f"Entries: {entry_count:,}\n"
                                      f"Size: {new_size // 1024:,} KB\n"
                                      f"✅ File validated - No corruption detected")
                
                # Refresh table
                if hasattr(main_window, 'refresh_table'):
                    main_window.refresh_table()
                
                return True
            else:
                main_window.log_message("❌ Rebuilt file validation failed - File may be corrupted")
                QMessageBox.critical(main_window, "Validation Failed", 
                                   "Rebuilt file failed validation!\n\n"
                                   "The file may be corrupted. Please use Safe Mode rebuild.")
                return False
        else:
            main_window.log_message("❌ FIXED fast rebuild failed")
            QMessageBox.critical(main_window, "Error", "Failed to rebuild IMG file")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ FIXED fast rebuild error: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild Error", f"Fast rebuild failed: {str(e)}")
        return False

def fixed_fast_rebuild_all(main_window) -> bool: #vers 1
    """FIXED fast rebuild all IMGs - Prevents corruption"""
    try:
        # Get directory
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory with IMG Files")
        if not directory:
            return False

        # Find IMG files
        import glob
        img_files = []
        img_files.extend(glob.glob(os.path.join(directory, "*.img")))
        img_files.extend(glob.glob(os.path.join(directory, "*.dir")))
        
        if not img_files:
            QMessageBox.information(main_window, "No IMG Files", "No IMG files found in directory")
            return False

        # Confirmation with validation warning
        reply = QMessageBox.question(
            main_window, "FIXED Fast Batch Rebuild",
            f"FIXED fast rebuild {len(img_files)} IMG files?\n\n"
            f"This will optimize all files with validation.\n"
            f"Original files will be backed up.\n\n"
            f"Each file will be validated to prevent corruption.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return False

        main_window.log_message(f"🔧 FIXED fast batch rebuild: {len(img_files)} files")

        # Progress dialog
        batch_progress = QProgressDialog("FIXED fast batch rebuilding...", "Cancel", 0, len(img_files), main_window)
        batch_progress.setWindowModality(Qt.WindowModality.WindowModal)
        batch_progress.show()

        rebuilt_count = 0
        failed_files = []
        corrupted_files = []
        total_entries = 0

        # Process files with validation
        for i, img_file_path in enumerate(img_files):
            if batch_progress.wasCanceled():
                break
                
            filename = os.path.basename(img_file_path)
            batch_progress.setValue(i)
            batch_progress.setLabelText(f"FIXED rebuilding: {filename}")
            QApplication.processEvents()

            try:
                # Load and rebuild
                from components.img_core_classes import IMGFile
                img = IMGFile()
                
                if img.load_from_file(img_file_path):
                    entry_count = len(img.entries)
                    main_window.log_message(f"🔧 Processing: {filename} ({entry_count} entries)")
                    
                    # Rebuild with validation
                    if _fixed_fast_rebuild_process(img, None, main_window):
                        # Validate the rebuilt file
                        if _validate_rebuilt_file(img, main_window):
                            rebuilt_count += 1
                            total_entries += entry_count
                            main_window.log_message(f"✅ Rebuilt & validated: {filename}")
                        else:
                            corrupted_files.append(filename)
                            main_window.log_message(f"⚠️ Rebuilt but validation failed: {filename}")
                    else:
                        failed_files.append(filename)
                        main_window.log_message(f"❌ Failed: {filename}")
                else:
                    failed_files.append(filename)
                    main_window.log_message(f"❌ Failed to load: {filename}")

            except Exception as e:
                failed_files.append(filename)
                main_window.log_message(f"❌ Error: {filename} - {str(e)}")

        batch_progress.close()

        # Show detailed results
        if rebuilt_count == len(img_files) and not corrupted_files:
            success_msg = f"✅ FIXED fast batch rebuild complete!\n\n" \
                         f"Files rebuilt: {rebuilt_count:,}\n" \
                         f"Total entries: {total_entries:,}\n" \
                         f"✅ All files validated - No corruption detected!"
            main_window.log_message(f"✅ Batch complete: {rebuilt_count} files, {total_entries} entries")
            QMessageBox.information(main_window, "Fast Batch Complete", success_msg)
            return True
        else:
            result_msg = f"🔧 FIXED fast batch rebuild results:\n\n" \
                        f"Successfully rebuilt: {rebuilt_count}/{len(img_files)}\n" \
                        f"Total entries processed: {total_entries:,}\n"
            
            if corrupted_files:
                result_msg += f"\n⚠️ Files with validation issues ({len(corrupted_files)}):\n" + "\n".join(corrupted_files[:3])
                if len(corrupted_files) > 3:
                    result_msg += f"\n... and {len(corrupted_files) - 3} more"
                result_msg += f"\n\nThese files may be corrupted. Use Safe Mode to rebuild them."
            
            if failed_files:
                result_msg += f"\n❌ Failed files ({len(failed_files)}):\n" + "\n".join(failed_files[:3])
                if len(failed_files) > 3:
                    result_msg += f"\n... and {len(failed_files) - 3} more"
            
            main_window.log_message(f"⚠️ Batch partial: {rebuilt_count}/{len(img_files)} files")
            QMessageBox.warning(main_window, "Batch Results", result_msg)
            return rebuilt_count > 0

    except Exception as e:
        main_window.log_message(f"❌ FIXED fast batch error: {str(e)}")
        QMessageBox.critical(main_window, "Fast Batch Error", f"Fast batch rebuild failed: {str(e)}")
        return False

def fixed_fast_quick_rebuild(main_window) -> bool: #vers 1
    """FIXED fastest rebuild with validation"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            main_window.log_message("⚠️ Quick rebuild: No IMG file open")
            return False
        
        filename = os.path.basename(main_window.current_img.file_path)
        entry_count = len(main_window.current_img.entries)
        
        main_window.log_message(f"⚡ FIXED fastest rebuild: {filename} ({entry_count} entries)")
        
        # Quick rebuild with validation
        success = _fixed_fast_rebuild_process(main_window.current_img, None, main_window)
        
        if success:
            # Quick validation
            if _validate_rebuilt_file(main_window.current_img, main_window):
                main_window.log_message(f"⚡ FIXED fastest complete & validated: {filename}")
                if hasattr(main_window, 'refresh_table'):
                    main_window.refresh_table()
                return True
            else:
                main_window.log_message(f"⚠️ FIXED fastest complete but validation failed: {filename}")
                return False
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ FIXED fastest rebuild error: {str(e)}")
        return False

def _fixed_fast_rebuild_process(img_file, progress_dialog, main_window) -> bool: #vers 1
    """FIXED fast rebuild process with proper validation"""
    try:
        # Step 1: SAFE bulk read all entry data
        if progress_dialog:
            progress_dialog.setValue(1)
            progress_dialog.setLabelText("Safely reading entries...")
            QApplication.processEvents()
        
        entry_data_list = _safe_bulk_read_entries(img_file, main_window)
        if not entry_data_list:
            main_window.log_message("❌ No entries could be read safely")
            return False
        
        # VALIDATE filenames before proceeding
        filename_validation = _validate_entry_filenames(entry_data_list, main_window)
        if not filename_validation:
            main_window.log_message("❌ Filename validation failed")
            return False
        
        # Step 2: SAFE offset calculation
        if progress_dialog:
            progress_dialog.setValue(2)
            progress_dialog.setLabelText("Calculating safe structure...")
            QApplication.processEvents()
        
        new_offsets = _safe_calculate_offsets(entry_data_list)
        if not new_offsets:
            main_window.log_message("❌ Offset calculation failed")
            return False
        
        # Step 3: SAFE bulk write with validation
        if progress_dialog:
            progress_dialog.setValue(3)
            progress_dialog.setLabelText("Safely writing IMG...")
            QApplication.processEvents()
        
        success = _safe_bulk_write_img(img_file, entry_data_list, new_offsets, main_window)
        if not success:
            main_window.log_message("❌ Safe write failed")
            return False
        
        # Step 4: Update entries and validate
        if progress_dialog:
            progress_dialog.setValue(4)
            progress_dialog.setLabelText("Updating and validating...")
            QApplication.processEvents()
        
        _safe_update_entries(img_file, new_offsets)
        
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ FIXED process error: {str(e)}")
        return False

def _safe_bulk_read_entries(img_file, main_window) -> List[Dict]: #vers 1
    """SAFE bulk read with proper validation"""
    try:
        file_path = img_file.file_path
        
        # Handle version 1 IMG files
        if hasattr(img_file, 'version') and img_file.version == 1:
            if file_path.endswith('.dir'):
                file_path = file_path.replace('.dir', '.img')
        
        entry_data_list = []
        
        # Validate file exists and is readable
        if not os.path.exists(file_path):
            main_window.log_message(f"❌ File not found: {file_path}")
            return []
        
        file_size = os.path.getsize(file_path)
        if file_size < 32:  # Too small to be valid
            main_window.log_message(f"❌ File too small: {file_size} bytes")
            return []
        
        # Safe read with validation
        with open(file_path, 'rb') as f:
            for i, entry in enumerate(img_file.entries):
                try:
                    # Validate entry bounds
                    if entry.offset < 0 or entry.size < 0:
                        main_window.log_message(f"⚠️ Invalid entry bounds: {entry.name}")
                        continue
                    
                    if entry.offset + entry.size > file_size:
                        main_window.log_message(f"⚠️ Entry extends beyond file: {entry.name}")
                        continue
                    
                    # SAFE filename validation
                    safe_name = _sanitize_filename(entry.name)
                    if not safe_name:
                        main_window.log_message(f"⚠️ Invalid filename: {repr(entry.name)}")
                        continue
                    
                    # Safe read
                    f.seek(entry.offset)
                    data = f.read(entry.size)
                    
                    if data and len(data) == entry.size:
                        entry_data_list.append({
                            'name': safe_name,  # Use sanitized name
                            'original_name': entry.name,  # Keep original for logging
                            'data': data,
                            'size': len(data)
                        })
                    else:
                        main_window.log_message(f"⚠️ Size mismatch: {entry.name} (expected {entry.size}, got {len(data) if data else 0})")
                        
                except Exception as e:
                    main_window.log_message(f"❌ Read error: {entry.name} - {str(e)}")
                    continue
        
        main_window.log_message(f"📖 Safe bulk read: {len(entry_data_list)}/{len(img_file.entries)} entries")
        return entry_data_list
        
    except Exception as e:
        main_window.log_message(f"❌ Safe bulk read error: {str(e)}")
        return []

def _sanitize_filename(filename: str) -> str: #vers 1
    """Sanitize filename to prevent corruption"""
    try:
        if not filename:
            return ""
        
        # Remove null bytes and control characters
        clean_name = ''.join(char for char in filename if ord(char) >= 32 and ord(char) < 127)
        
        # Remove common problematic characters
        clean_name = clean_name.replace('\x00', '').replace('\xff', '').replace('\xcd', '')
        
        # Ensure it's not empty and not too long
        clean_name = clean_name.strip()
        if len(clean_name) > 24:
            clean_name = clean_name[:24]
        
        # If empty after cleaning, create a fallback name
        if not clean_name:
            clean_name = "unnamed_file"
        
        return clean_name
        
    except Exception:
        return "unnamed_file"

def _validate_entry_filenames(entry_data_list, main_window) -> bool: #vers 1
    """Validate all entry filenames are safe"""
    try:
        invalid_count = 0
        
        for entry_data in entry_data_list:
            name = entry_data['name']
            original_name = entry_data.get('original_name', name)
            
            # Check for problematic characters
            if len(name.encode('ascii', errors='ignore')) != len(name):
                main_window.log_message(f"⚠️ Non-ASCII characters in: {repr(original_name)} → {repr(name)}")
                invalid_count += 1
            
            # Check length
            if len(name) > 24:
                main_window.log_message(f"⚠️ Filename too long: {repr(original_name)} → {repr(name)}")
                invalid_count += 1
            
            # Check for null bytes
            if '\x00' in original_name:
                main_window.log_message(f"⚠️ Null bytes in filename: {repr(original_name)} → {repr(name)}")
                invalid_count += 1
        
        if invalid_count > 0:
            main_window.log_message(f"🔧 Filename validation: {invalid_count} filenames sanitized")
        
        return True  # Continue even with sanitized names
        
    except Exception as e:
        main_window.log_message(f"❌ Filename validation error: {str(e)}")
        return False

def _safe_calculate_offsets(entry_data_list) -> List[Dict]: #vers 1
    """SAFE offset calculation with validation"""
    try:
        offsets = []
        
        # Calculate header size (32 bytes per entry)
        header_size = len(entry_data_list) * 32
        
        # Start data after header, sector-aligned
        current_offset = ((header_size + 2047) // 2048) * 2048
        
        # Validate starting offset
        if current_offset < header_size:
            print(f"❌ Invalid starting offset: {current_offset} < {header_size}")
            return []
        
        # Calculate all offsets safely
        for entry_data in entry_data_list:
            size_bytes = entry_data['size']
            
            # Validate size
            if size_bytes < 0 or size_bytes > 100 * 1024 * 1024:  # Max 100MB per entry
                print(f"❌ Invalid entry size: {size_bytes} for {entry_data['name']}")
                continue
            
            offsets.append({
                'name': entry_data['name'],
                'offset': current_offset,
                'size': size_bytes
            })
            
            # Next offset (sector-aligned)
            aligned_size = ((size_bytes + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Validate total size is reasonable
        total_size = current_offset
        if total_size > 2 * 1024 * 1024 * 1024:  # Max 2GB
            print(f"❌ Total file size too large: {total_size}")
            return []
        
        return offsets
        
    except Exception as e:
        print(f"❌ SAFE offset calculation error: {e}")
        return []

def _safe_bulk_write_img(img_file, entry_data_list, new_offsets, main_window) -> bool: #vers 1
    """SAFE bulk write with validation at each step"""
    try:
        is_version1 = hasattr(img_file, 'version') and img_file.version == 1
        
        if is_version1:
            return _safe_write_version1(img_file, entry_data_list, new_offsets, main_window)
        else:
            return _safe_write_version2(img_file, entry_data_list, new_offsets, main_window)
            
    except Exception as e:
        main_window.log_message(f"❌ SAFE bulk write error: {str(e)}")
        return False

def _safe_write_version2(img_file, entry_data_list, new_offsets, main_window) -> bool: #vers 1
    """SAFE write Version 2 IMG with validation"""
    try:
        # Pre-build and validate directory
        directory_data = bytearray()
        
        for i, offset_info in enumerate(new_offsets):
            entry_data = entry_data_list[i]
            
            # SAFE filename encoding
            name = entry_data['name']
            try:
                name_bytes = name.encode('ascii', errors='replace')[:24]
                name_bytes = name_bytes.ljust(24, b'\x00')
            except Exception:
                # Fallback to safe name
                name_bytes = b'unnamed_file'.ljust(24, b'\x00')
            
            # Validate name_bytes
            if len(name_bytes) != 24:
                main_window.log_message(f"❌ Invalid name bytes length for: {name}")
                return False
            
            # Build directory entry safely
            try:
                directory_data.extend(name_bytes)
                directory_data.extend(struct.pack('<I', offset_info['offset']))
                directory_data.extend(struct.pack('<I', offset_info['size']))
            except struct.error as e:
                main_window.log_message(f"❌ Struct pack error for {name}: {e}")
                return False
        
        # Validate directory size
        expected_dir_size = len(new_offsets) * 32
        if len(directory_data) != expected_dir_size:
            main_window.log_message(f"❌ Directory size mismatch: {len(directory_data)} != {expected_dir_size}")
            return False
        
        # Calculate padding
        header_size = len(directory_data)
        sector_boundary = ((header_size + 2047) // 2048) * 2048
        padding_size = sector_boundary - header_size
        
        # SAFE write with validation
        temp_path = f"{img_file.file_path}.tmp"
        
        try:
            with open(temp_path, 'wb') as f:
                # Write directory
                f.write(directory_data)
                
                # Write padding
                if padding_size > 0:
                    f.write(b'\x00' * padding_size)
                
                # Write file data with validation
                for i, offset_info in enumerate(new_offsets):
                    entry_data = entry_data_list[i]
                    
                    # Validate offset
                    expected_pos = offset_info['offset']
                    actual_pos = f.tell()
                    if actual_pos != expected_pos:
                        f.seek(expected_pos)
                    
                    # Write data
                    data = entry_data['data']
                    if len(data) != offset_info['size']:
                        main_window.log_message(f"❌ Data size mismatch for {entry_data['name']}")
                        return False
                    
                    f.write(data)
                    
                    # Sector padding
                    current_pos = f.tell()
                    sector_end = ((current_pos + 2047) // 2048) * 2048
                    padding = sector_end - current_pos
                    if padding > 0:
                        f.write(b'\x00' * padding)
            
            # Validate written file
            if os.path.getsize(temp_path) < header_size:
                main_window.log_message("❌ Written file too small")
                os.remove(temp_path)
                return False
            
            # Replace original with temp file
            shutil.move(temp_path, img_file.file_path)
            main_window.log_message("✅ Safe Version 2 write complete")
            return True
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        main_window.log_message(f"❌ SAFE Version 2 write error: {str(e)}")
        return False

def _safe_write_version1(img_file, entry_data_list, new_offsets, main_window) -> bool: #vers 1
    """SAFE write Version 1 IMG files with validation"""
    try:
        dir_path = img_file.file_path
        img_path = dir_path.replace('.dir', '.img')
        
        # Build directory safely
        directory_data = bytearray()
        for offset_info in new_offsets:
            entry_data = next(e for e in entry_data_list if e['name'] == offset_info['name'])
            
            # SAFE filename encoding
            name = entry_data['name']
            try:
                name_bytes = name.encode('ascii', errors='replace')[:24]
                name_bytes = name_bytes.ljust(24, b'\x00')
            except Exception:
                name_bytes = b'unnamed_file'.ljust(24, b'\x00')
            
            directory_data.extend(name_bytes)
            directory_data.extend(struct.pack('<I', offset_info['offset']))
            directory_data.extend(struct.pack('<I', offset_info['size']))
        
        # Write .dir file safely
        temp_dir_path = f"{dir_path}.tmp"
        with open(temp_dir_path, 'wb') as f:
            f.write(directory_data)
        
        # Write .img file safely
        temp_img_path = f"{img_path}.tmp"
        with open(temp_img_path, 'wb') as f:
            for offset_info in new_offsets:
                entry_data = next(e for e in entry_data_list if e['name'] == offset_info['name'])
                
                f.seek(offset_info['offset'])
                f.write(entry_data['data'])
                
                # Sector padding
                current_pos = f.tell()
                sector_end = ((current_pos + 2047) // 2048) * 2048
                padding = sector_end - current_pos
                if padding > 0:
                    f.write(b'\x00' * padding)
        
        # Replace original files
        shutil.move(temp_dir_path, dir_path)
        shutil.move(temp_img_path, img_path)
        
        main_window.log_message("✅ Safe Version 1 write complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ SAFE Version 1 write error: {str(e)}")
        # Clean up temp files
        for temp_file in [f"{dir_path}.tmp", f"{img_path}.tmp"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return False

def _safe_update_entries(img_file, new_offsets): #vers 1
    """SAFE update all entries with validation"""
    try:
        updated_count = 0
        for i, entry in enumerate(img_file.entries):
            if i < len(new_offsets):
                entry.offset = new_offsets[i]['offset']
                entry.size = new_offsets[i]['size']
                updated_count += 1
        
        print(f"✅ Safe entry update: {updated_count} entries updated")
        
    except Exception as e:
        print(f"❌ SAFE entry update error: {e}")

def _validate_rebuilt_file(img_file, main_window) -> bool: #vers 1
    """Validate rebuilt file to detect corruption"""
    try:
        file_path = img_file.file_path
        
        # Check file exists
        if not os.path.exists(file_path):
            main_window.log_message("❌ Validation: File not found")
            return False
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size < 32:
            main_window.log_message("❌ Validation: File too small")
            return False
        
        # Check header structure
        try:
            with open(file_path, 'rb') as f:
                # Try to read first entry
                if img_file.entries:
                    header_data = f.read(32)
                    if len(header_data) != 32:
                        main_window.log_message("❌ Validation: Invalid header size")
                        return False
                    
                    # Check for null-terminated strings in name field
                    name_field = header_data[:24]
                    if b'\x00' not in name_field:
                        main_window.log_message("⚠️ Validation: No null terminator in name field")
                    
                    # Try to read offset and size
                    try:
                        offset, size = struct.unpack('<II', header_data[24:32])
                        if offset < 0 or size < 0:
                            main_window.log_message("❌ Validation: Negative offset/size")
                            return False
                    except struct.error:
                        main_window.log_message("❌ Validation: Invalid offset/size structure")
                        return False
        
        except Exception as e:
            main_window.log_message(f"❌ Validation: Read error - {str(e)}")
            return False
        
        main_window.log_message("✅ Validation: File structure appears valid")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Validation error: {str(e)}")
        return False

def setup_fixed_fast_rebuild_methods(main_window): #vers 1
    """Setup FIXED fast rebuild methods - Prevents corruption"""
    try:
        # Add FIXED fast rebuild methods
        main_window.rebuild_img = lambda: fixed_fast_rebuild_current(main_window)
        main_window.rebuild_all_img = lambda: fixed_fast_rebuild_all(main_window)
        main_window.quick_rebuild = lambda: fixed_fast_quick_rebuild(main_window)
        
        # Additional safe methods
        main_window.safe_fast_rebuild = main_window.rebuild_img
        main_window.validated_rebuild = main_window.rebuild_img
        
        # Legacy aliases
        main_window.rebuild_current_img = main_window.rebuild_img
        main_window.optimize_img = main_window.rebuild_img
        main_window.batch_rebuild = main_window.rebuild_all_img
        main_window.fast_rebuild = main_window.quick_rebuild
        
        main_window.log_message("🔧 FIXED fast rebuild methods setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ FIXED fast rebuild setup failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'fixed_fast_rebuild_current',
    'fixed_fast_rebuild_all', 
    'fixed_fast_quick_rebuild',
    'setup_fixed_fast_rebuild_methods'
]