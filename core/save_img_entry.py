#this belongs in core/save_img_entry.py - Version: 3
# X-Seti - July28 2025 - IMG Factory 1.5 - IMG Save Entry Functions

"""
IMG Save Entry Functions - Handle saving/rebuilding IMG files after import
Separates save functionality from core classes for better organization
"""

import struct
import os
import shutil

##Methods list -
# add_save_methods_to_imgfile
# integrate_img_save_functions
# rebuild_img_file
# rebuild_version1_img
# rebuild_version2_img
# save_img_file_with_backup
# Save_Img_entry_function


def save_img_entry_function(main_window): #vers 1
    """Save current IMG entries - manual save button"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "No IMG file is currently loaded.")
            return

        if main_window.current_img.save_img_file():
            main_window.log_message("✅ IMG file saved successfully")
            QMessageBox.information(main_window, "Save Complete", "IMG file saved successfully.")
        else:
            main_window.log_message("❌ Failed to save IMG file")
            QMessageBox.critical(main_window, "Save Error", "Failed to save IMG file.")

    except Exception as e:
        main_window.log_message(f"❌ Save error: {str(e)}")
        QMessageBox.critical(main_window, "Save Error", f"Save failed: {str(e)}")


def save_img_file_with_backup(img_file) -> bool: #vers 1
    """Save IMG file with current entries - creates backup first"""
    try:
        if not img_file.file_path or not img_file.entries:
            print("[ERROR] No file path or entries to save")
            return False
        
        # Create backup first
        backup_path = img_file.file_path + '.backup'
        shutil.copy2(img_file.file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        
        # Rebuild the IMG file
        return rebuild_img_file(img_file)
        
    except Exception as e:
        print(f"[ERROR] Failed to save IMG file: {e}")
        return False

def rebuild_img_file(img_file) -> bool: #vers 1
    """Rebuild IMG file with current entries"""
    try:
        from components.img_core_classes import IMGVersion
        
        if img_file.version == IMGVersion.VERSION_1:
            return rebuild_version1_img(img_file)
        else:
            return rebuild_version2_img(img_file)
            
    except Exception as e:
        print(f"[ERROR] Failed to rebuild IMG file: {e}")
        return False

def rebuild_version2_img(img_file) -> bool: #vers 1
    """Rebuild Version 2 IMG file (SA format)"""
    try:
        # Calculate sizes
        entry_count = len(img_file.entries)
        directory_size = entry_count * 32  # 32 bytes per entry
        data_start = directory_size
        
        # Collect entry data
        entry_data_list = []
        current_offset = data_start
        
        for entry in img_file.entries:
            # Get entry data
            if hasattr(entry, '_cached_data') and entry._cached_data:
                data = entry._cached_data
            else:
                data = img_file.read_entry_data(entry)
            
            entry_data_list.append(data)
            
            # Update entry with new offset/size
            entry.offset = current_offset
            entry.size = len(data)
            
            # Align to sector boundary (2048 bytes)
            aligned_size = ((len(data) + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Write new IMG file
        with open(img_file.file_path, 'wb') as f:
            # Write directory
            for i, entry in enumerate(img_file.entries):
                # Convert to sectors
                offset_sectors = entry.offset // 2048
                size_sectors = ((entry.size + 2047) // 2048)
                
                # Pack entry: offset(4), size(4), name(24)
                entry_data = struct.pack('<II', offset_sectors, size_sectors)
                name_bytes = entry.name.encode('ascii')[:24].ljust(24, b'\x00')
                entry_data += name_bytes
                
                f.write(entry_data)
            
            # Write file data
            for i, data in enumerate(entry_data_list):
                f.seek(img_file.entries[i].offset)
                f.write(data)
                
                # Pad to sector boundary
                current_pos = f.tell()
                sector_end = ((current_pos + 2047) // 2048) * 2048
                if current_pos < sector_end:
                    f.write(b'\x00' * (sector_end - current_pos))
        
        print(f"✅ Rebuilt Version 2 IMG file: {entry_count} entries")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to rebuild Version 2 IMG: {e}")
        return False

def rebuild_version1_img(img_file) -> bool: #vers 1
    """Rebuild Version 1 IMG file (DIR/IMG pair)"""
    try:
        # Get DIR and IMG paths
        dir_path = img_file.file_path
        img_path = img_file.file_path.replace('.dir', '.img')
        
        entry_count = len(img_file.entries)
        
        # Collect entry data and calculate offsets
        entry_data_list = []
        current_offset = 0
        
        for entry in img_file.entries:
            # Get entry data
            if hasattr(entry, '_cached_data') and entry._cached_data:
                data = entry._cached_data
            else:
                data = img_file.read_entry_data(entry)
            
            entry_data_list.append(data)
            
            # Update entry with new offset/size
            entry.offset = current_offset
            entry.size = len(data)
            
            # Align to sector boundary
            aligned_size = ((len(data) + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Write DIR file
        with open(dir_path, 'wb') as f:
            for entry in img_file.entries:
                # Convert to sectors
                offset_sectors = entry.offset // 2048
                size_sectors = ((entry.size + 2047) // 2048)
                
                # Pack entry: offset(4), size(4), name(24)
                entry_data = struct.pack('<II', offset_sectors, size_sectors)
                name_bytes = entry.name.encode('ascii')[:24].ljust(24, b'\x00')
                entry_data += name_bytes
                
                f.write(entry_data)
        
        # Write IMG file
        with open(img_path, 'wb') as f:
            for i, data in enumerate(entry_data_list):
                f.seek(img_file.entries[i].offset)
                f.write(data)
                
                # Pad to sector boundary
                current_pos = f.tell()
                sector_end = ((current_pos + 2047) // 2048) * 2048
                if current_pos < sector_end:
                    f.write(b'\x00' * (sector_end - current_pos))
        
        print(f"✅ Rebuilt DIR/IMG pair: {entry_count} entries")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to rebuild Version 1 IMG: {e}")
        return False

def add_save_methods_to_imgfile(): #vers 1
    """Add save methods to IMGFile class"""
    try:
        from components.img_core_classes import IMGFile
        
        def save_img_file(self) -> bool: #vers 1
            """Save IMG file with current entries"""
            return save_img_file_with_backup(self)
        
        def rebuild_img_file_method(self) -> bool: #vers 1
            """Rebuild IMG file with current entries"""
            return rebuild_img_file(self)
        
        # Add methods to IMGFile class
        IMGFile.save_img_file = save_img_file
        IMGFile.rebuild_img_file = rebuild_img_file_method
        
        print("✅ Added save methods to IMGFile class")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add save methods to IMGFile class: {e}")
        return False


def integrate_img_save_functions(main_window): #vers 1
    """Integrate IMG save functions into main window"""
    try:
        # Add the save methods to IMGFile class
        if add_save_methods_to_imgfile():
            main_window.log_message("✅ IMG save functions added - imports will now persist")
            return True
        else:
            main_window.log_message("❌ Failed to add IMG save functions")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ IMG save integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'save_img_file_with_backup',
    'rebuild_img_file', 
    'rebuild_version1_img',
    'rebuild_version2_img',
    'add_save_methods_to_imgfile',
    'Save_Img_entry_function',
    'integrate_img_save_functions'
]
