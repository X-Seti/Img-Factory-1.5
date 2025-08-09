#this belongs in core/simple_rebuild.py - Version: 1
# X-Seti - Aug09 2025 - IMG Factory 1.5 - SIMPLE Rebuild (No Recursion)

"""
SIMPLE Rebuild System - Completely avoids integration conflicts
Direct functions that work without complex integration
"""

import os
import struct
import shutil
from typing import List, Dict
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication, QFileDialog
from PyQt6.QtCore import Qt

##Methods list -
# simple_rebuild_current
# simple_rebuild_all
# simple_quick_rebuild
# setup_simple_rebuild_methods

def simple_rebuild_current(main_window) -> bool: #vers 1
    """Simple rebuild current IMG - NO INTEGRATION CONFLICTS"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG", "No IMG file is currently loaded.")
            return False
            
        if not main_window.current_img.entries:
            QMessageBox.warning(main_window, "Empty IMG", "IMG file has no entries to rebuild")
            return False
        
        img_file = main_window.current_img
        main_window.log_message(f"🔧 Simple rebuild: {os.path.basename(img_file.file_path)}")
        
        # Create backup
        backup_path = f"{img_file.file_path}.backup"
        if not os.path.exists(backup_path):
            shutil.copy2(img_file.file_path, backup_path)
            main_window.log_message(f"✅ Backup created: {os.path.basename(backup_path)}")
        
        # Show simple progress
        progress = QProgressDialog("Rebuilding IMG...", "Cancel", 0, 100, main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Do the rebuild
        success = _simple_rebuild_process(img_file, progress, main_window)
        
        progress.close()
        
        if success:
            main_window.log_message("✅ Simple rebuild complete")
            QMessageBox.information(main_window, "Success", "IMG file rebuilt successfully!")
            
            # Refresh table if possible
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            return True
        else:
            main_window.log_message("❌ Simple rebuild failed")
            QMessageBox.critical(main_window, "Error", "Failed to rebuild IMG file")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Simple rebuild error: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild Error", f"Rebuild failed: {str(e)}")
        return False

def simple_rebuild_all(main_window) -> bool: #vers 1
    """Simple rebuild all IMGs in directory - NO INTEGRATION CONFLICTS"""
    try:
        # Get directory
        directory = QFileDialog.getExistingDirectory(main_window, "Select Directory with IMG Files")
        if not directory:
            return False

        # Find IMG files
        import glob
        img_files = []
        
        # Find .img files (Version 2)
        img_files.extend(glob.glob(os.path.join(directory, "*.img")))
        # Find .dir files (Version 1)
        img_files.extend(glob.glob(os.path.join(directory, "*.dir")))
        
        if not img_files:
            QMessageBox.information(main_window, "No IMG Files", "No IMG files found in directory")
            return False

        # Confirm
        reply = QMessageBox.question(
            main_window, "Confirm Rebuild All",
            f"Rebuild {len(img_files)} IMG files?\n\nThis will modify the original files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return False

        main_window.log_message(f"🔧 Simple batch rebuild: {len(img_files)} files")

        # Progress dialog
        batch_progress = QProgressDialog("Batch rebuilding IMG files...", "Cancel", 0, len(img_files), main_window)
        batch_progress.setWindowModality(Qt.WindowModality.WindowModal)
        batch_progress.show()

        rebuilt_count = 0
        failed_files = []

        # Process each file
        for i, img_file_path in enumerate(img_files):
            if batch_progress.wasCanceled():
                break
                
            filename = os.path.basename(img_file_path)
            batch_progress.setValue(i)
            batch_progress.setLabelText(f"Rebuilding {filename}...")
            QApplication.processEvents()

            main_window.log_message(f"🔧 Processing: {filename}")

            try:
                # Load IMG file
                from components.img_core_classes import IMGFile
                img = IMGFile()
                
                if img.load_from_file(img_file_path):
                    # Try simple rebuild
                    if _simple_rebuild_process(img, None, main_window):
                        rebuilt_count += 1
                        main_window.log_message(f"✅ Rebuilt: {filename}")
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

        # Show results
        if rebuilt_count == len(img_files):
            success_msg = f"Successfully rebuilt all {rebuilt_count} IMG files!"
            main_window.log_message(f"✅ {success_msg}")
            QMessageBox.information(main_window, "Batch Rebuild Complete", success_msg)
            return True
        else:
            result_msg = f"Rebuilt {rebuilt_count} of {len(img_files)} files."
            if failed_files:
                result_msg += f"\n\nFailed files:\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5:
                    result_msg += f"\n... and {len(failed_files) - 5} more"
            
            main_window.log_message(f"⚠️ {result_msg}")
            QMessageBox.warning(main_window, "Partial Success", result_msg)
            return rebuilt_count > 0

    except Exception as e:
        main_window.log_message(f"❌ Batch rebuild error: {str(e)}")
        QMessageBox.critical(main_window, "Batch Rebuild Error", f"Batch rebuild failed: {str(e)}")
        return False

def simple_quick_rebuild(main_window) -> bool: #vers 1
    """Simple quick rebuild - NO INTEGRATION CONFLICTS"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            main_window.log_message("⚠️ Quick rebuild: No IMG file open")
            return False
        
        main_window.log_message("⚡ Simple quick rebuild")
        return simple_rebuild_current(main_window)
        
    except Exception as e:
        main_window.log_message(f"❌ Quick rebuild error: {str(e)}")
        return False

def _simple_rebuild_process(img_file, progress_dialog, main_window) -> bool: #vers 1
    """Simple rebuild process - NO COMPLEX THREADING"""
    try:
        if progress_dialog:
            progress_dialog.setValue(10)
            progress_dialog.setLabelText("Reading entries...")
            QApplication.processEvents()
        
        # Step 1: Read all entry data
        entry_data_list = []
        total_entries = len(img_file.entries)
        
        for i, entry in enumerate(img_file.entries):
            try:
                # Try to get data
                data = entry.get_data()
                if data is None:
                    # Fallback read
                    data = _read_entry_directly(img_file, entry)
                
                if data:
                    entry_data_list.append({
                        'name': entry.name,
                        'data': data,
                        'size': len(data)
                    })
                else:
                    main_window.log_message(f"⚠️ Could not read: {entry.name}")
                    
            except Exception as e:
                main_window.log_message(f"❌ Read error: {entry.name} - {str(e)}")
                continue
                
            if progress_dialog:
                progress = 10 + (i * 50 // total_entries)
                progress_dialog.setValue(progress)
                QApplication.processEvents()
        
        if not entry_data_list:
            main_window.log_message("❌ No entries could be read")
            return False
        
        if progress_dialog:
            progress_dialog.setValue(70)
            progress_dialog.setLabelText("Calculating new structure...")
            QApplication.processEvents()
        
        # Step 2: Calculate new offsets
        new_offsets = _calculate_simple_offsets(entry_data_list)
        
        if progress_dialog:
            progress_dialog.setValue(80)
            progress_dialog.setLabelText("Writing rebuilt IMG...")
            QApplication.processEvents()
        
        # Step 3: Write rebuilt IMG
        success = _write_simple_rebuild(img_file, entry_data_list, new_offsets)
        
        if progress_dialog:
            progress_dialog.setValue(90)
            progress_dialog.setLabelText("Updating entries...")
            QApplication.processEvents()
        
        # Step 4: Update entries
        if success:
            for i, entry in enumerate(img_file.entries):
                if i < len(new_offsets):
                    entry.offset = new_offsets[i]['offset']
                    entry.size = new_offsets[i]['size']
        
        if progress_dialog:
            progress_dialog.setValue(100)
            QApplication.processEvents()
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Rebuild process error: {str(e)}")
        return False

def _read_entry_directly(img_file, entry) -> bytes: #vers 1
    """Read entry data directly from file"""
    try:
        file_path = img_file.file_path
        
        # Handle version 1 IMG files
        if hasattr(img_file, 'version') and img_file.version == 1:
            if file_path.endswith('.dir'):
                file_path = file_path.replace('.dir', '.img')
        
        with open(file_path, 'rb') as f:
            f.seek(entry.offset)
            return f.read(entry.size)
            
    except Exception as e:
        print(f"Direct read error for {entry.name}: {e}")
        return None

def _calculate_simple_offsets(entry_data_list) -> List[Dict]: #vers 1
    """Calculate simple optimized offsets"""
    try:
        offsets = []
        
        # Header size: 32 bytes per entry (24 name + 4 offset + 4 size)
        header_size = len(entry_data_list) * 32
        
        # Start data after header, aligned to 2048-byte sectors
        current_offset = ((header_size + 2047) // 2048) * 2048
        
        for entry_data in entry_data_list:
            size_bytes = entry_data['size']
            size_sectors = (size_bytes + 2047) // 2048
            
            offsets.append({
                'name': entry_data['name'],
                'offset': current_offset,
                'size': size_bytes,
                'size_sectors': size_sectors
            })
            
            # Next entry starts after this one (sector-aligned)
            current_offset += size_sectors * 2048
        
        return offsets
        
    except Exception as e:
        print(f"Offset calculation error: {e}")
        return []

def _write_simple_rebuild(img_file, entry_data_list, new_offsets) -> bool: #vers 1
    """Write the rebuilt IMG file"""
    try:
        is_version1 = hasattr(img_file, 'version') and img_file.version == 1
        
        if is_version1:
            return _write_version1_simple(img_file, entry_data_list, new_offsets)
        else:
            return _write_version2_simple(img_file, entry_data_list, new_offsets)
            
    except Exception as e:
        print(f"Write error: {e}")
        return False

def _write_version2_simple(img_file, entry_data_list, new_offsets) -> bool: #vers 1
    """Write Version 2 IMG file - SIMPLE"""
    try:
        with open(img_file.file_path, 'wb') as f:
            # Write directory entries
            for i, offset_info in enumerate(new_offsets):
                entry_data = entry_data_list[i]
                
                # Entry format: [NAME(24)] [OFFSET(4)] [SIZE(4)]
                name_bytes = entry_data['name'].encode('ascii')[:24].ljust(24, b'\x00')
                f.write(name_bytes)
                f.write(struct.pack('<I', offset_info['offset']))
                f.write(struct.pack('<I', offset_info['size']))
            
            # Pad to sector boundary
            header_end = f.tell()
            sector_boundary = ((header_end + 2047) // 2048) * 2048
            padding = sector_boundary - header_end
            if padding > 0:
                f.write(b'\x00' * padding)
            
            # Write file data
            for i, offset_info in enumerate(new_offsets):
                entry_data = entry_data_list[i]
                
                f.seek(offset_info['offset'])
                f.write(entry_data['data'])
                
                # Pad to sector boundary
                current_pos = f.tell()
                sector_end = ((current_pos + 2047) // 2048) * 2048
                padding = sector_end - current_pos
                if padding > 0:
                    f.write(b'\x00' * padding)
        
        return True
        
    except Exception as e:
        print(f"Version 2 write error: {e}")
        return False

def _write_version1_simple(img_file, entry_data_list, new_offsets) -> bool: #vers 1
    """Write Version 1 IMG files (.dir and .img) - SIMPLE"""
    try:
        dir_path = img_file.file_path
        img_path = dir_path.replace('.dir', '.img')
        
        # Write .dir file
        with open(dir_path, 'wb') as f:
            for offset_info in new_offsets:
                entry_data = next(e for e in entry_data_list if e['name'] == offset_info['name'])
                
                # Entry format: [NAME(24)] [OFFSET(4)] [SIZE(4)]
                name_bytes = entry_data['name'].encode('ascii')[:24].ljust(24, b'\x00')
                f.write(name_bytes)
                f.write(struct.pack('<I', offset_info['offset']))
                f.write(struct.pack('<I', offset_info['size']))
        
        # Write .img file
        with open(img_path, 'wb') as f:
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
        
        return True
        
    except Exception as e:
        print(f"Version 1 write error: {e}")
        return False

def setup_simple_rebuild_methods(main_window): #vers 1
    """Setup simple rebuild methods - NO INTEGRATION CONFLICTS"""
    try:
        # Add simple rebuild methods directly
        main_window.rebuild_img = lambda: simple_rebuild_current(main_window)
        main_window.rebuild_all_img = lambda: simple_rebuild_all(main_window)
        main_window.quick_rebuild = lambda: simple_quick_rebuild(main_window)
        
        # Legacy aliases
        main_window.rebuild_current_img = main_window.rebuild_img
        main_window.optimize_img = main_window.rebuild_img
        main_window.batch_rebuild = main_window.rebuild_all_img
        
        main_window.log_message("✅ Simple rebuild methods setup complete")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Simple rebuild setup failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'simple_rebuild_current',
    'simple_rebuild_all', 
    'simple_quick_rebuild',
    'setup_simple_rebuild_methods'
]