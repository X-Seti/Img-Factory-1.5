#this belongs in core/rebuild.py - Version: 4
# X-Seti - August23 2025 - IMG Factory 1.5 - Clean Rebuild Functions with Tab Awareness and New Core

"""
Clean Rebuild Functions - Uses tab awareness like export_via.py + integrates new core system
UPDATED: Uses new IMG_Operations.rebuild_archive (creates new IMG from memory, deletes old)
Supports rebuilding current IMG in active tab with proper multi-tab detection
"""

import os
import shutil
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup

# Use same tab awareness imports as export_via.py (this works!)
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab, get_current_file_type_from_tab

##Methods list -
# rebuild_current_img
# fast_rebuild_current
# safe_rebuild_current
# show_rebuild_mode_dialog
# _unified_rebuild_process
# _try_new_core_rebuild
# _convert_to_new_core_format
# _legacy_rebuild_process
# _sanitize_filename
# integrate_rebuild_functions

def rebuild_current_img(main_window): #vers 4
    """Rebuild current IMG in active tab - CLEAN: Uses tab awareness like export_via.py"""
    try:
        # Copy exact pattern from working export_via.py
        if not validate_tab_before_operation(main_window, "Rebuild Current IMG"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file to rebuild")
            return False
        
        if hasattr(main_window, 'log_message'):
            file_name = os.path.basename(getattr(file_object, 'file_path', 'Unknown'))
            main_window.log_message(f"🔧 Rebuilding IMG in current tab: {file_name}")
        
        # Use unified rebuild with new core integration
        success = _unified_rebuild_process(file_object, "fast", main_window)
        
        if success:
            # Refresh current tab to show changes
            if hasattr(main_window, 'refresh_current_tab_data'):
                main_window.refresh_current_tab_data()
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ Current IMG rebuilt successfully")
            
            QMessageBox.information(main_window, "Rebuild Complete", 
                "IMG file rebuilt successfully!")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild current IMG error: {str(e)}")
        QMessageBox.critical(main_window, "Rebuild Error", f"Rebuild failed: {str(e)}")
        return False


def fast_rebuild_current(main_window): #vers 2
    """Fast rebuild current tab IMG - CLEAN: Uses tab awareness"""
    try:
        if not validate_tab_before_operation(main_window, "Fast Rebuild"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🚀 Fast rebuild mode - current tab")
        
        return _unified_rebuild_process(file_object, "fast", main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Fast rebuild error: {str(e)}")
        return False


def safe_rebuild_current(main_window): #vers 2
    """Safe rebuild current tab IMG - CLEAN: Uses tab awareness"""
    try:
        if not validate_tab_before_operation(main_window, "Safe Rebuild"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔒 Safe rebuild mode - current tab")
        
        return _unified_rebuild_process(file_object, "safe", main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Safe rebuild error: {str(e)}")
        return False


def show_rebuild_mode_dialog(main_window): #vers 1
    """Show dialog to choose rebuild mode for current tab"""
    try:
        if not validate_tab_before_operation(main_window, "Rebuild Mode Selection"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Rebuild Mode - Current Tab")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        # Info about current file
        file_name = os.path.basename(getattr(file_object, 'file_path', 'Unknown'))
        entry_count = len(file_object.entries) if hasattr(file_object, 'entries') else 0
        
        info_label = QLabel(f"Rebuild IMG in current tab:\n{file_name} ({entry_count} entries)")
        info_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # Mode selection
        mode_group = QButtonGroup()
        fast_radio = QRadioButton("🚀 Fast Mode - Quick rebuild (recommended)")
        safe_radio = QRadioButton("🔒 Safe Mode - Skip problematic entries")
        
        fast_radio.setChecked(True)  # Default to fast
        mode_group.addButton(fast_radio)
        mode_group.addButton(safe_radio)
        
        layout.addWidget(fast_radio)
        layout.addWidget(safe_radio)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Rebuild")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            mode = "fast" if fast_radio.isChecked() else "safe"
            success = _unified_rebuild_process(file_object, mode, main_window)
            
            if success:
                QMessageBox.information(main_window, "Rebuild Complete",
                    f"IMG file rebuilt successfully using {mode} mode!")
            
            return success
        
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild mode dialog error: {str(e)}")
        return False


def _unified_rebuild_process(img_file, mode: str, main_window) -> bool: #vers 4
    """UPDATED: Unified rebuild using new IMG_Operations.rebuild_archive (creates new from memory, deletes old)"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 Starting {mode} rebuild using memory-based system")
        
        # Try new core system first (creates new IMG from memory, deletes old)
        if _try_new_core_rebuild(img_file, mode, main_window):
            return True
        
        # Fallback to legacy rebuild system
        if hasattr(main_window, 'log_message'):
            main_window.log_message("⚠️ New core not available, using legacy rebuild")
        
        return _legacy_rebuild_process(img_file, mode, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Unified rebuild error: {str(e)}")
        return False


def _try_new_core_rebuild(img_file, mode: str, main_window) -> bool: #vers 1
    """Try to use new IMG_Operations.rebuild_archive system (creates new from memory, deletes old)"""
    try:
        # Import new core system
        from .IMG_Operations import IMG_Operations
        from .Core import IMGArchive
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🆕 Using NEW core rebuild system (creates new IMG from memory)")
        
        # Convert existing IMG to new core format if needed
        if not isinstance(img_file, IMGArchive):
            core_img = _convert_to_new_core_format(img_file, main_window)
            if not core_img:
                return False
        else:
            core_img = img_file
        
        # Progress callback
        def progress_callback(percent, message):
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"🔧 {message} ({percent}%)")
        
        # Use new core rebuild_archive (creates new IMG from memory, deletes old)
        rebuilt_archive = IMG_Operations.rebuild_archive(
            img_archive=core_img,
            output_path=None,  # Overwrites original
            version=None,      # Keep same version
            progress_callback=progress_callback
        )
        
        if rebuilt_archive:
            # Update main window references to new archive
            if hasattr(main_window, 'current_img') and main_window.current_img == img_file:
                main_window.current_img = rebuilt_archive
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ NEW core rebuild completed successfully")
            return True
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ NEW core rebuild failed")
            return False
        
    except ImportError:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("⚠️ New core system not available")
        return False
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ New core rebuild error: {str(e)}")
        return False


def _convert_to_new_core_format(old_img_file, main_window): #vers 1
    """Convert existing IMG to new core format while preserving memory pool data"""
    try:
        from .Core import IMGArchive, IMGEntry
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Converting IMG to new core format...")
        
        # Create new core archive
        core_archive = IMGArchive()
        core_archive.file_path = getattr(old_img_file, 'file_path', '')
        core_archive.version = 'V1' if getattr(old_img_file, 'version', 2) == 1 else 'V2'
        
        # Convert entries and PRESERVE MEMORY POOL DATA
        if hasattr(old_img_file, 'entries'):
            for old_entry in old_img_file.entries:
                core_entry = IMGEntry()
                core_entry.name = old_entry.name
                core_entry.actual_offset = getattr(old_entry, 'offset', 0)
                core_entry.actual_size = getattr(old_entry, 'size', 0)
                
                # CRITICAL: Preserve cached data from memory pool
                if hasattr(old_entry, '_cached_data') and old_entry._cached_data:
                    core_entry.data = old_entry._cached_data
                    core_entry.is_new_entry = True
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"🧠 Preserved memory data for: {old_entry.name}")
                elif hasattr(old_entry, 'get_data'):
                    # Try to get data using existing method
                    try:
                        core_entry.data = old_entry.get_data()
                    except:
                        pass  # Data will be read from file if needed
                
                core_archive.entries.append(core_entry)
        
        if hasattr(main_window, 'log_message'):
            entry_count = len(core_archive.entries) if core_archive.entries else 0
            main_window.log_message(f"✅ Converted {entry_count} entries to new core format")
        
        return core_archive
        
    except ImportError:
        return None  # New core not available
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Core format conversion error: {str(e)}")
        return None


def _legacy_rebuild_process(img_file, mode: str, main_window) -> bool: #vers 1
    """Fallback to existing working rebuild system"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔧 Using legacy rebuild system in {mode} mode")
        
        # Determine IMG version
        img_version = getattr(img_file, 'version', 2)
        
        if not hasattr(img_file, 'entries') or not img_file.entries:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ IMG file has no entries to rebuild")
            return False
        
        # Collect and sanitize entry data
        entry_data_list = []
        for entry in img_file.entries:
            try:
                # Sanitize filename to prevent corruption
                clean_name = _sanitize_filename(entry.name)
                if clean_name != entry.name and hasattr(main_window, 'log_message'):
                    main_window.log_message(f"🧹 Cleaned filename: '{entry.name}' → '{clean_name}'")
                    entry.name = clean_name
                
                # Get entry data (preserve memory pool data)
                if hasattr(entry, '_cached_data') and entry._cached_data:
                    data = entry._cached_data
                elif hasattr(entry, 'get_data'):
                    data = entry.get_data()
                else:
                    # Read from file
                    data = img_file.read_entry_data(entry)
                
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
        
        if not entry_data_list:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No valid entries found for rebuild")
            return False
        
        # Rebuild based on version
        if img_version == 1:
            success = _legacy_write_version1(img_file, entry_data_list, main_window)
        else:
            success = _legacy_write_version2(img_file, entry_data_list, main_window)
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Legacy rebuild error: {str(e)}")
        return False


def _legacy_write_version2(img_file, entry_data_list, main_window) -> bool: #vers 1
    """Legacy Version 2 IMG rebuild"""
    try:
        import struct
        
        file_path = img_file.file_path
        entry_count = len(entry_data_list)
        
        # Calculate structure
        directory_size = entry_count * 32
        data_start = ((directory_size + 2047) // 2048) * 2048
        
        # Create temporary file
        temp_path = f"{file_path}.tmp"
        
        # Calculate offsets
        current_offset = data_start
        offset_info = []
        
        for entry_data in entry_data_list:
            data = entry_data['data']
            offset_info.append({
                'offset': current_offset,
                'size': len(data)
            })
            aligned_size = ((len(data) + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Write temporary file
        with open(temp_path, 'wb') as f:
            # Write directory
            for i, entry_data in enumerate(entry_data_list):
                offset_sectors = offset_info[i]['offset'] // 2048
                size_sectors = ((offset_info[i]['size'] + 2047) // 2048)
                name_bytes = entry_data['clean_name'].encode('ascii', errors='replace')[:24].ljust(24, b'\x00')
                
                f.write(struct.pack('<II', offset_sectors, size_sectors))
                f.write(name_bytes)
            
            # Write data
            for i, entry_data in enumerate(entry_data_list):
                f.seek(offset_info[i]['offset'])
                f.write(entry_data['data'])
        
        # Atomic replace
        shutil.move(temp_path, file_path)
        
        # Update entries
        for i, entry_data in enumerate(entry_data_list):
            entry = entry_data['entry']
            entry.offset = offset_info[i]['offset']
            entry.size = offset_info[i]['size']
            entry.name = entry_data['clean_name']
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Legacy Version 2 rebuilt: {entry_count} entries")
        
        return True
        
    except Exception as e:
        # Clean up temp file
        temp_path = f"{img_file.file_path}.tmp"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Legacy Version 2 write error: {str(e)}")
        return False


def _legacy_write_version1(img_file, entry_data_list, main_window) -> bool: #vers 1
    """Legacy Version 1 IMG rebuild (DIR/IMG pair)"""
    try:
        import struct
        
        # Get paths
        dir_path = img_file.file_path
        img_path = dir_path.replace('.dir', '.img')
        entry_count = len(entry_data_list)
        
        # Calculate offsets
        current_offset = 0
        offset_info = []
        
        for entry_data in entry_data_list:
            data = entry_data['data']
            offset_info.append({
                'offset': current_offset,
                'size': len(data)
            })
            aligned_size = ((len(data) + 2047) // 2048) * 2048
            current_offset += aligned_size
        
        # Write to temporary files
        temp_dir_path = f"{dir_path}.tmp"
        temp_img_path = f"{img_path}.tmp"
        
        # Write DIR file
        with open(temp_dir_path, 'wb') as f:
            for i, entry_data in enumerate(entry_data_list):
                name_bytes = entry_data['clean_name'].encode('ascii', errors='replace')[:24].ljust(24, b'\x00')
                offset_sectors = offset_info[i]['offset'] // 2048
                size_sectors = ((offset_info[i]['size'] + 2047) // 2048)
                
                f.write(name_bytes)  # Name first
                f.write(struct.pack('<I', offset_sectors))  # Then offset
                f.write(struct.pack('<I', size_sectors))    # Then size
        
        # Write IMG file
        with open(temp_img_path, 'wb') as f:
            for i, entry_data in enumerate(entry_data_list):
                f.seek(offset_info[i]['offset'])
                f.write(entry_data['data'])
        
        # Atomic replace
        shutil.move(temp_dir_path, dir_path)
        shutil.move(temp_img_path, img_path)
        
        # Update entries
        for i, entry_data in enumerate(entry_data_list):
            entry = entry_data['entry']
            entry.offset = offset_info[i]['offset']
            entry.size = offset_info[i]['size']
            entry.name = entry_data['clean_name']
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"✅ Legacy Version 1 rebuilt: {entry_count} entries")
        
        return True
        
    except Exception as e:
        # Clean up temp files
        for temp_file in [f"{dir_path}.tmp", f"{img_path}.tmp"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Legacy Version 1 write error: {str(e)}")
        return False


def _sanitize_filename(filename: str) -> str: #vers 1
    """Sanitize filename to prevent corruption"""
    try:
        if not filename:
            return "unnamed.dat"
        
        # Remove null bytes and control characters
        clean_name = filename.replace('\x00', '').replace('\xcd', '').replace('\xff', '')
        clean_name = ''.join(c for c in clean_name if 32 <= ord(c) <= 126)
        clean_name = clean_name.replace('\\', '_').replace('/', '_').replace('|', '_')
        clean_name = clean_name.strip()[:23]  # Leave room for null terminator
        
        return clean_name if clean_name else "file.dat"
        
    except Exception:
        return "file.dat"


def integrate_rebuild_functions(main_window) -> bool: #vers 4
    """Integrate clean rebuild functions with tab awareness - SIMPLIFIED"""
    try:
        # Main rebuild functions - TAB AWARE
        main_window.rebuild_current_img = lambda: rebuild_current_img(main_window)
        main_window.rebuild_img = main_window.rebuild_current_img  # Alias
        
        # Mode-specific functions for current tab
        main_window.fast_rebuild_current = lambda: fast_rebuild_current(main_window)
        main_window.safe_rebuild_current = lambda: safe_rebuild_current(main_window)
        main_window.show_rebuild_dialog = lambda: show_rebuild_mode_dialog(main_window)
        
        # Legacy aliases for compatibility
        main_window.fast_rebuild = main_window.fast_rebuild_current
        main_window.safe_rebuild = main_window.safe_rebuild_current
        main_window.optimize_img = main_window.rebuild_current_img
        main_window.quick_rebuild = main_window.fast_rebuild_current
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Clean rebuild system integrated with TAB AWARENESS + NEW CORE")
            main_window.log_message("   • Uses new IMG_Operations.rebuild_archive (creates new from memory)")
            main_window.log_message("   • Falls back to legacy system if new core unavailable")
            main_window.log_message("   • Rebuilds current active tab only")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild integration failed: {str(e)}")
        return False


# Export only the essential functions
__all__ = [
    'rebuild_current_img',
    'fast_rebuild_current',
    'safe_rebuild_current', 
    'show_rebuild_mode_dialog',
    'integrate_rebuild_functions'
]