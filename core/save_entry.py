#this belongs in core/ save_entry.py - Version: 1
# X-Seti - September04 2025 - IMG Factory 1.5 - Save Entry Function

import os
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# Tab awareness system
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab

##Methods list -
# save_img_entry
# _check_for_changes
# _rebuild_img_file
# integrate_save_entry_function

def save_img_entry(main_window): #vers 1
    """Save IMG entry changes by rebuilding the IMG file"""
    try:
        # Validate tab
        if not validate_tab_before_operation(main_window, "Save Entry"):
            return False
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return False
        
        # Check if there are changes to save
        has_changes = _check_for_changes(file_object, main_window)
        
        if not has_changes:
            QMessageBox.information(main_window, "No Changes", "No changes detected. IMG file is up to date.")
            return True
        
        # Ask user to confirm save
        reply = QMessageBox.question(
            main_window,
            "Save Changes",
            "This will rebuild the IMG file to save all changes to disk.\n\n"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # Rebuild IMG file to save changes
        success = _rebuild_img_file(file_object, main_window)
        
        if success:
            QMessageBox.information(main_window, "Save Complete", "IMG file saved successfully!")
            
            # Refresh table to show updated state
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
        else:
            QMessageBox.critical(main_window, "Save Failed", "Failed to save IMG file changes")
        
        return success
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Save entry error: {str(e)}")
        QMessageBox.critical(main_window, "Save Error", f"Save error: {str(e)}")
        return False


def _check_for_changes(file_object, main_window) -> bool: #vers 1
    """Check if IMG file has unsaved changes"""
    try:
        # Method 1: Check modified flag
        if hasattr(file_object, 'modified') and file_object.modified:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("💾 Changes detected: IMG marked as modified")
            return True
        
        # Method 2: Check for new entries
        if hasattr(file_object, 'has_new_or_modified_entries'):
            if file_object.has_new_or_modified_entries():
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("💾 Changes detected: New/modified entries found")
                return True
        
        # Method 3: Check for new entries manually
        if hasattr(file_object, 'entries'):
            new_count = 0
            for entry in file_object.entries:
                if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                    new_count += 1
            
            if new_count > 0:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"💾 Changes detected: {new_count} new entries")
                return True
        
        # Method 4: Check deleted entries
        if hasattr(file_object, 'deleted_entries') and file_object.deleted_entries:
            deleted_count = len(file_object.deleted_entries)
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"💾 Changes detected: {deleted_count} deleted entries")
            return True
        
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Check changes error: {str(e)}")
        return False


def _rebuild_img_file(file_object, main_window) -> bool: #vers 1
    """Rebuild IMG file to save changes to disk"""
    try:
        # Get file path
        file_path = getattr(file_object, 'file_path', None)
        if not file_path:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("❌ No file path available for rebuild")
            return False
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"💾 Rebuilding IMG file: {file_path}")
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Saving IMG file...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowTitle("Saving Changes")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setValue(0)
        progress_dialog.show()
        
        try:
            # Method 1: Use existing rebuild method
            if hasattr(file_object, 'rebuild_img_file'):
                progress_dialog.setLabelText("Rebuilding IMG file...")
                progress_dialog.setValue(25)
                QApplication.processEvents()
                
                success = file_object.rebuild_img_file()
                
                progress_dialog.setValue(100)
                QApplication.processEvents()
                
                if success:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("✅ IMG file rebuilt successfully")
                    return True
            
            # Method 2: Use save method
            elif hasattr(file_object, 'save'):
                progress_dialog.setLabelText("Saving IMG file...")
                progress_dialog.setValue(25)
                QApplication.processEvents()
                
                success = file_object.save()
                
                progress_dialog.setValue(100)
                QApplication.processEvents()
                
                if success:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("✅ IMG file saved successfully")
                    return True
            
            # Method 3: Use main window rebuild function
            elif hasattr(main_window, 'rebuild_img_function'):
                progress_dialog.setLabelText("Using rebuild function...")
                progress_dialog.setValue(25)
                QApplication.processEvents()
                
                success = main_window.rebuild_img_function()
                
                progress_dialog.setValue(100)
                QApplication.processEvents()
                
                return success
            
            # Method 4: Try external rebuild from core/rebuild.py
            else:
                try:
                    from core.rebuild import rebuild_img_file
                    
                    progress_dialog.setLabelText("Using core rebuild...")
                    progress_dialog.setValue(25)
                    QApplication.processEvents()
                    
                    success = rebuild_img_file(main_window)
                    
                    progress_dialog.setValue(100)
                    QApplication.processEvents()
                    
                    return success
                    
                except ImportError:
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("❌ No rebuild method available")
                    return False
        
        finally:
            progress_dialog.close()
        
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Rebuild IMG error: {str(e)}")
        return False


def integrate_save_entry_function(main_window) -> bool: #vers 1
    """Integrate save entry function into main window"""
    try:
        # Add save entry method to main window
        main_window.save_img_entry = lambda: save_img_entry(main_window)
        
        # Add aliases that GUI might use
        main_window.save_entry = main_window.save_img_entry
        main_window.save_img_entry_function = main_window.save_img_entry
        main_window.save_changes = main_window.save_img_entry
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Save entry function integrated")
            main_window.log_message("   • Rebuilds IMG file to save changes")
            main_window.log_message("   • Detects unsaved changes automatically")
            main_window.log_message("   • Works with existing IMG classes")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Save entry integration failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'save_img_entry',
    'show_save_options_dialog',
    'integrate_save_entry_function',
    'SaveOptions'
]