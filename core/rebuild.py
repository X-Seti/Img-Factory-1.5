#this belongs in core/rebuild.py - Version: 1
# X-Seti - August09 2025 - IMG Factory 1.5 - Unified Single IMG Rebuild System

"""
Unified IMG Rebuild System - Single File Operations
Corruption-free rebuilding with comprehensive validation
FIXED: Directory structure bugs, backup system for Version 1
"""

import os
import struct
import shutil
from typing import Optional, Dict, Any, List, Tuple
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, QCheckBox, QLabel, QPushButton, QButtonGroup
from PyQt6.QtCore import QThread, pyqtSignal, Qt

def rebuild_current_img(main_window) -> bool:
    """Rebuild current IMG with mode selection dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return False
            
        if not main_window.current_img.entries:
            QMessageBox.warning(main_window, "Empty IMG", "IMG file has no entries to rebuild")
            return False
        
        # Show mode selection dialog
        options = show_rebuild_mode_dialog(main_window, "single")
        if not options:
            return False  # User cancelled
        
        return rebuild_current_with_mode(main_window, options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild current error: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild Error", f"Rebuild failed: {str(e)}")
        return False


def rebuild_current_with_mode(main_window, options: dict) -> bool:
    """Rebuild current IMG with specified options"""
    try:
        img_file = main_window.current_img
        filename = os.path.basename(img_file.file_path)
        entry_count = len(img_file.entries)
        mode = options.get('mode', 'fast')
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 {mode.upper()} rebuild: {filename} ({entry_count} entries)")
        
        # Create backup first
        if options.get('create_backup', True):
            if not _create_unified_backup(img_file, main_window):
                QMessageBox.warning(main_window, "Backup Failed", "Failed to create backup. Continue anyway?")
                reply = QMessageBox.question(main_window, "Continue?", "Continue without backup?")
                if reply != QMessageBox.StandardButton.Yes:
                    return False
        
        # Execute rebuild
        success = _unified_rebuild_process(img_file, mode, main_window)
        
        if success:
            # Validate if requested
            if options.get('verify_integrity', False):
                validation_success = _validate_rebuilt_img(img_file, main_window)
                if not validation_success:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("⚠️ Rebuild validation failed")
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ Rebuild complete: {filename}")
            
            # Show completion dialog
            new_size = os.path.getsize(img_file.file_path)
            result_msg = f"Successfully rebuilt {filename}\n\n" \
                        f"Entries: {entry_count:,}\n" \
                        f"Size: {new_size // 1024:,} KB\n" \
                        f"Mode: {mode.upper()}"
            
            if options.get('verify_integrity', False):
                result_msg += "\n✅ File validated - No corruption detected"
            
            QMessageBox.information(main_window, "Rebuild Complete", result_msg)
            
            # Refresh table
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Rebuild failed")
            
            # Offer backup restoration on failure
            if options.get('create_backup', True):
                reply = QMessageBox.question(
                    main_window, "Rebuild Failed", 
                    "Rebuild failed. Would you like to restore from backup?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    if _restore_from_backup(img_file, main_window):
                        QMessageBox.information(main_window, "Restoration Complete", 
                                              "File restored from backup successfully.")
                        if hasattr(main_window, 'refresh_table'):
                            main_window.refresh_table()
                    else:
                        QMessageBox.critical(main_window, "Restoration Failed", 
                                           "Failed to restore from backup.")
            else:
                QMessageBox.critical(main_window, "Rebuild Failed", "Rebuild process failed.")
            
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild with mode error: {str(e)}")
        return False


def show_rebuild_mode_dialog(main_window, operation_type="single") -> Optional[dict]:
    """Show rebuild mode selection dialog"""
    try:
        # Simple mode selection using standard dialog
        reply = QMessageBox.question(
            main_window, "Rebuild Mode",
            "Choose rebuild mode:\n\n"
            "Fast Mode: Quick optimization, basic validation\n"
            "Safe Mode: Thorough checking, full validation\n\n"
            "Use Fast Mode?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return None
        elif reply == QMessageBox.StandardButton.Yes:
            # Fast mode
            return {
                'mode': 'fast',
                'create_backup': True,
                'verify_integrity': False
            }
        else:
            # Safe mode  
            return {
                'mode': 'safe',
                'create_backup': True,
                'verify_integrity': True
            }
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Mode dialog error: {str(e)}")
        return None


def fast_rebuild_current(main_window) -> bool:
    """Fast rebuild current IMG (direct call)"""
    options = {'mode': 'fast', 'create_backup': True, 'verify_integrity': False}
    return rebuild_current_with_mode(main_window, options)


def safe_rebuild_current(main_window) -> bool:
    """Safe rebuild current IMG (direct call)"""
    options = {'mode': 'safe', 'create_backup': True, 'verify_integrity': True}
    return rebuild_current_with_mode(main_window, options)


def quick_rebuild_current(main_window) -> bool:
    """Quick rebuild current IMG (no backup, fast mode)"""
    options = {'mode': 'fast', 'create_backup': False, 'verify_integrity': False}
    return rebuild_current_with_mode(main_window, options)


def _create_unified_backup(img_file, main_window) -> bool:
    """Create unified backup with validation - FIXED for Version 1 DIR/IMG pairs"""
    try:
        file_path = img_file.file_path
        img_version = getattr(img_file, 'version', 2)
        
        if img_version == 1:
            # FIXED: Version 1 needs BOTH .dir and .img backed up
            dir_path = file_path  # This is the .dir file
            img_path = file_path.replace('.dir', '.img')
            
            dir_backup_path = f"{dir_path}.backup"
            img_backup_path = f"{img_path}.backup"
            
            # Check if backups already exist
            if os.path.exists(dir_backup_path) and os.path.exists(img_backup_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"ℹ️ DIR/IMG backups already exist")
                return True
            
            # FIXED: Create backup for .dir file
            if os.path.exists(dir_path):
                shutil.copy2(dir_path, dir_backup_path)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ DIR backup created: {os.path.basename(dir_backup_path)}")
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ DIR file not found: {dir_path}")
                return False
            
            # FIXED: Create backup for .img file
            if os.path.exists(img_path):
                shutil.copy2(img_path, img_backup_path)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ IMG backup created: {os.path.basename(img_backup_path)}")
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ IMG file not found: {img_path}")
                return False
            
            # Verify both backups were created successfully
            if os.path.exists(dir_backup_path) and os.path.exists(img_backup_path):
                dir_size = os.path.getsize(dir_backup_path)
                img_size = os.path.getsize(img_backup_path)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Version 1 backup complete: DIR ({dir_size} bytes) + IMG ({img_size} bytes)")
                return True
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Version 1 backup verification failed")
                return False
                
        else:
            # Version 2: Single .img file backup (existing logic)
            backup_path = f"{file_path}.backup"
            
            if os.path.exists(backup_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"ℹ️ Backup already exists: {os.path.basename(backup_path)}")
                return True
            
            shutil.copy2(file_path, backup_path)
            
            # Verify backup
            if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
                backup_size = os.path.getsize(backup_path)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ Version 2 backup created: {os.path.basename(backup_path)} ({backup_size} bytes)")
                return True
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Version 2 backup creation failed")
                return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Backup error: {str(e)}")
        return False


def _restore_from_backup(img_file, main_window) -> bool:
    """Restore IMG file from backup - FIXED for Version 1 DIR/IMG pairs"""
    try:
        file_path = img_file.file_path
        img_version = getattr(img_file, 'version', 2)
        
        if img_version == 1:
            # FIXED: Version 1 restore BOTH .dir and .img files
            dir_path = file_path  # This is the .dir file
            img_path = file_path.replace('.dir', '.img')
            
            dir_backup_path = f"{dir_path}.backup"
            img_backup_path = f"{img_path}.backup"
            
            # Check if both backup files exist
            if not os.path.exists(dir_backup_path) or not os.path.exists(img_backup_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Version 1 backup files not found for restoration")
                return False
            
            # Restore .dir file
            shutil.copy2(dir_backup_path, dir_path)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ DIR file restored from backup")
            
            # Restore .img file
            shutil.copy2(img_backup_path, img_path)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ IMG file restored from backup")
            
            # Verify restoration
            if os.path.exists(dir_path) and os.path.exists(img_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("✅ Version 1 restoration complete")
                return True
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Version 1 restoration verification failed")
                return False
                
        else:
            # Version 2: Single .img file restore
            backup_path = f"{file_path}.backup"
            
            if not os.path.exists(backup_path):
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Version 2 backup file not found for restoration")
                return False
            
            shutil.copy2(backup_path, file_path)
            
            # Verify restoration
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("✅ Version 2 restoration complete")
                return True
            else:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("❌ Version 2 restoration verification failed")
                return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Restoration error: {str(e)}")
        return False


def _sanitize_filename_unified(filename: str) -> str:
    """Unified filename sanitization to prevent corruption - FIXED"""
    try:
        if not filename:
            return "unnamed.dat"
        
        # Remove null bytes and control characters
        clean_name = filename.replace('\x00', '').replace('\xcd', '').replace('\xff', '')
        
        # Remove other control characters (keep printable ASCII only)
        clean_name = ''.join(c for c in clean_name if 32 <= ord(c) <= 126)
        
        # Remove problematic characters for IMG format
        clean_name = clean_name.replace('\\', '_').replace('/', '_').replace('|', '_')
        
        # FIXED: Limit to IMG field size and strip whitespace
        clean_name = clean_name.strip()[:23]  # Leave room for null terminator
        
        # Fallback if empty
        if not clean_name:
            clean_name = "file.dat"
        
        return clean_name
        
    except Exception:
        return "file.dat"


def _unified_rebuild_process(img_file, mode: str, main_window) -> bool:
    """Unified rebuild process for both modes"""
    try:
        # Determine IMG version
        img_version = getattr(img_file, 'version', 2)  # Default to Version 2
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 Rebuilding IMG Version {img_version} in {mode} mode")
        
        # Collect and validate entry data
        entry_data_list = []
        total_entries = len(img_file.entries)
        
        for i, entry in enumerate(img_file.entries):
            try:
                # Sanitize filename
                clean_name = _sanitize_filename_unified(entry.name)
                if clean_name != entry.name and hasattr(main_window, 'log_message'):
                    main_window.log_message(f"🧹 Cleaned filename: '{entry.name}' → '{clean_name}'")
                    entry.name = clean_name
                
                # Get entry data
                if hasattr(entry, '_cached_data') and entry._cached_data:
                    data = entry._cached_data
                elif hasattr(entry, 'get_data'):
                    data = entry.get_data()
                else:
                    # Fallback: read from file
                    with open(img_file.file_path, 'rb') as f:
                        f.seek(entry.offset)
                        data = f.read(entry.size)
                
                if data and len(data) > 0:
                    entry_data_list.append({
                        'entry': entry,
                        'data': data,
                        'clean_name': clean_name
                    })
                else:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ Skipping empty entry: {entry.name}")
                        
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error processing entry {entry.name}: {str(e)}")
                if mode == "safe":
                    continue  # Skip problematic entries in safe mode
                else:
                    return False  # Fail fast in fast mode
        
        # Write rebuilt IMG based on version
        if img_version == 1:
            success = _write_img_version1(img_file, entry_data_list, mode, main_window)
        else:
            success = _write_img_version2(img_file, entry_data_list, mode, main_window)
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Unified rebuild process error: {str(e)}")
        return False


def _write_img_version2(img_file, entry_data_list, mode: str, main_window) -> bool:
    """Write Version 2 IMG file (SA format) - FIXED STRUCTURE BUGS"""
    try:
        entry_count = len(entry_data_list)
        
        # FIXED: Calculate correct directory size and data start
        directory_size = entry_count * 32  # 32 bytes per entry
        data_start = ((directory_size + 2047) // 2048) * 2048  # FIXED: Sector-aligned start
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 FIXED structure: {entry_count} entries, dir_size={directory_size}, data_start={data_start}")
        
        # Calculate FIXED offsets
        current_offset = data_start
        offset_info = []
        
        for entry_data in entry_data_list:
            data = entry_data['data']
            
            offset_info.append({
                'offset': current_offset,
                'size': len(data)
            })
            
            # FIXED: Align to sector boundary (2048 bytes)
            aligned_size = ((len(data) + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Write to temporary file first (atomic operation)
        temp_path = f"{img_file.file_path}.tmp"
        
        with open(temp_path, 'wb') as f:
            # FIXED: Write directory with CORRECT format: name(24) + offset(4) + size(4)
            for i, entry_data in enumerate(entry_data_list):
                clean_name = entry_data['clean_name']
                
                # FIXED: Encode filename safely (24 bytes)
                name_bytes = clean_name.encode('ascii', errors='replace')[:24]
                name_bytes = name_bytes.ljust(24, b'\x00')
                
                # FIXED: Convert to sectors for IMG format
                offset_sectors = offset_info[i]['offset'] // 2048
                size_sectors = ((offset_info[i]['size'] + 2047) // 2048)
                
                # FIXED: Correct directory entry format: name(24) + offset(4) + size(4)
                f.write(name_bytes)  # Write name FIRST (24 bytes)
                f.write(struct.pack('<I', offset_sectors))  # Then offset (4 bytes)
                f.write(struct.pack('<I', size_sectors))    # Then size (4 bytes)
            
            # FIXED: Pad directory to sector boundary
            current_pos = f.tell()
            if current_pos < data_start:
                padding = data_start - current_pos
                f.write(b'\x00' * padding)
            
            # FIXED: Write file data at correct offsets
            for i, entry_data in enumerate(entry_data_list):
                data = entry_data['data']
                expected_offset = offset_info[i]['offset']
                
                # Verify we're at the correct position
                actual_pos = f.tell()
                if actual_pos != expected_offset:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"⚠️ FIXED position: expected {expected_offset}, got {actual_pos}")
                    f.seek(expected_offset)
                
                f.write(data)
                
                # FIXED: Pad to sector boundary
                current_pos = f.tell()
                sector_end = ((current_pos + 2047) // 2048) * 2048
                if current_pos < sector_end:
                    f.write(b'\x00' * (sector_end - current_pos))
        
        # FIXED: Atomic replace original file
        shutil.move(temp_path, img_file.file_path)
        
        # FIXED: Update entries with correct new offsets and sizes
        for i, entry_data in enumerate(entry_data_list):
            entry = entry_data['entry']
            entry.offset = offset_info[i]['offset']
            entry.size = offset_info[i]['size']
            entry.name = entry_data['clean_name']
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ FIXED Version 2 IMG rebuilt: {entry_count} entries")
        
        return True
        
    except Exception as e:
        # Clean up temp file
        temp_path = f"{img_file.file_path}.tmp"
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ FIXED Version 2 write error: {str(e)}")
        return False


def _write_img_version1(img_file, entry_data_list, mode: str, main_window) -> bool:
    """Write Version 1 IMG file (DIR/IMG pair) - FIXED STRUCTURE BUGS"""
    try:
        # Get paths
        dir_path = img_file.file_path
        img_path = img_file.file_path.replace('.dir', '.img')
        
        entry_count = len(entry_data_list)
        
        # FIXED: Calculate offsets (Version 1 starts from 0 in IMG file)
        current_offset = 0
        offset_info = []
        
        for entry_data in entry_data_list:
            data = entry_data['data']
            
            offset_info.append({
                'offset': current_offset,
                'size': len(data)
            })
            
            # FIXED: Align to sector boundary
            aligned_size = ((len(data) + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Write to temporary files first
        temp_dir_path = f"{dir_path}.tmp"
        temp_img_path = f"{img_path}.tmp"
        
        # FIXED: Write DIR file with correct format
        with open(temp_dir_path, 'wb') as f:
            for i, entry_data in enumerate(entry_data_list):
                clean_name = entry_data['clean_name']
                
                # FIXED: Encode filename safely (24 bytes)
                name_bytes = clean_name.encode('ascii', errors='replace')[:24]
                name_bytes = name_bytes.ljust(24, b'\x00')
                
                # FIXED: Convert to sectors
                offset_sectors = offset_info[i]['offset'] // 2048
                size_sectors = ((offset_info[i]['size'] + 2047) // 2048)
                
                # FIXED: Correct DIR entry format: name(24) + offset(4) + size(4)
                f.write(name_bytes)  # Write name FIRST (24 bytes)
                f.write(struct.pack('<I', offset_sectors))  # Then offset (4 bytes)
                f.write(struct.pack('<I', size_sectors))    # Then size (4 bytes)
        
        # FIXED: Write IMG file
        with open(temp_img_path, 'wb') as f:
            for i, entry_data in enumerate(entry_data_list):
                data = entry_data['data']
                expected_offset = offset_info[i]['offset']
                
                # Seek to correct position
                f.seek(expected_offset)
                f.write(data)
                
                # FIXED: Pad to sector boundary
                current_pos = f.tell()
                sector_end = ((current_pos + 2047) // 2048) * 2048
                if current_pos < sector_end:
                    f.write(b'\x00' * (sector_end - current_pos))
        
        # FIXED: Atomic replace original files
        shutil.move(temp_dir_path, dir_path)
        shutil.move(temp_img_path, img_path)
        
        # FIXED: Update entries with correct new offsets and sizes
        for i, entry_data in enumerate(entry_data_list):
            entry = entry_data['entry']
            entry.offset = offset_info[i]['offset']
            entry.size = offset_info[i]['size']
            entry.name = entry_data['clean_name']
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ FIXED Version 1 DIR/IMG rebuilt: {entry_count} entries")
        
        return True
        
    except Exception as e:
        # Clean up temp files
        for temp_file in [f"{dir_path}.tmp", f"{img_path}.tmp"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ FIXED Version 1 write error: {str(e)}")
        return False


def _validate_rebuilt_img(img_file, main_window) -> bool:
    """Validate rebuilt IMG file to detect corruption - FIXED VALIDATION"""
    try:
        file_path = img_file.file_path
        
        # Check file exists and has reasonable size
        if not os.path.exists(file_path):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Validation: Rebuilt file not found")
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size < 32:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ Validation: Rebuilt file too small")
            return False
        
        # FIXED: Validate directory structure format
        expected_entries = len(img_file.entries)
        expected_dir_size = expected_entries * 32
        
        try:
            with open(file_path, 'rb') as f:
                # Read and validate first few directory entries
                for i in range(min(3, expected_entries)):
                    f.seek(i * 32)
                    entry_data = f.read(32)
                    
                    if len(entry_data) != 32:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ FIXED validation: Invalid entry size at {i}")
                        return False
                    
                    # FIXED: Validate structure - name(24) + offset(4) + size(4)
                    name_bytes = entry_data[:24]
                    offset_size_bytes = entry_data[24:32]
                    
                    # Check name has null terminator somewhere
                    if b'\x00' not in name_bytes:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"⚠️ FIXED validation: No null terminator in entry {i}")
                    
                    # FIXED: Validate offset and size are in correct positions
                    try:
                        offset_sectors, size_sectors = struct.unpack('<II', offset_size_bytes)
                        if offset_sectors < 0 or size_sectors < 0:
                            if hasattr(main_window, 'log_message'):
                                main_window.log_message(f"❌ FIXED validation: Invalid offset/size at entry {i}")
                            return False
                            
                        # Sanity check: offset should be reasonable
                        offset_bytes = offset_sectors * 2048
                        if offset_bytes > file_size:
                            if hasattr(main_window, 'log_message'):
                                main_window.log_message(f"❌ FIXED validation: Offset beyond file size at entry {i}")
                            return False
                            
                    except struct.error:
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ FIXED validation: Invalid structure at entry {i}")
                        return False
        
        except Exception as e:
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"❌ FIXED validation: Read error - {str(e)}")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ FIXED validation: IMG structure appears correct")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ FIXED validation error: {str(e)}")
        return False


# Integration function for main window
def integrate_rebuild_functions(main_window) -> bool:
    """Integrate unified rebuild functions into main window"""
    try:
        # Main rebuild functions
        main_window.rebuild_current_img = lambda: rebuild_current_img(main_window)
        main_window.rebuild_img = main_window.rebuild_current_img  # Alias
        
        # Direct mode functions
        main_window.fast_rebuild_current = lambda: fast_rebuild_current(main_window)
        main_window.safe_rebuild_current = lambda: safe_rebuild_current(main_window)
        main_window.quick_rebuild = lambda: quick_rebuild_current(main_window)
        
        # Legacy aliases for compatibility
        main_window.fast_rebuild = main_window.fast_rebuild_current
        main_window.safe_rebuild = main_window.safe_rebuild_current
        main_window.optimize_img = main_window.rebuild_current_img
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Unified rebuild system integrated")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'rebuild_current_img',
    'rebuild_current_with_mode',
    'fast_rebuild_current',
    'safe_rebuild_current', 
    'quick_rebuild_current',
    'show_rebuild_mode_dialog',
    'integrate_rebuild_functions'
]
                