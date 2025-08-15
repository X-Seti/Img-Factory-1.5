#this belongs in core/quick_export.py - Version: 1
# X-Seti - Aug15 2025 - IMG Factory 1.5 - Quick Export Functions

"""
Quick Export Functions - Streamlined export with minimal dialogs
Fast export operations with sensible defaults and reduced user interaction
"""

import os
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt, QSettings, QTimer
from methods.export_shared import (
    ExportThread, get_selected_entries, get_export_folder, validate_export_entries
)

##Methods list -
# quick_export_function

def quick_export_function(main_window): #vers 2
    """Fast export directly to Assists folder with automatic organization"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        # Get selected entries
        selected_entries = get_selected_entries(main_window)
        if not validate_export_entries(selected_entries, main_window):
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚡ Quick export: {len(selected_entries)} entries to Assists folder")
        
        # Get Assists folder from settings
        assists_folder = None
        if hasattr(main_window, 'settings'):
            assists_folder = getattr(main_window.settings, 'assists_folder', None)
        
        if not assists_folder or not os.path.exists(assists_folder):
            # Fallback to manual selection if no assists folder
            QMessageBox.warning(
                main_window, 
                "Assists Folder Not Found", 
                "Assists folder not configured or doesn't exist.\nPlease select export destination manually."
            )
            assists_folder = get_export_folder(main_window, "Quick Export - Select Destination")
            if not assists_folder:
                return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📁 Quick export destination: {assists_folder}")
        
        # Quick export options - auto-organize to Assists structure
        export_options = {
            'organize_by_type': True,
            'use_assists_structure': True,  # Use Assists folder structure
            'overwrite': True,              # Quick export assumes overwrite OK
            'create_log': False,            # Skip log for speed
            'open_folder_after': True       # Open folder when done
        }
        
        # Start quick export
        _start_quick_export_with_progress(main_window, selected_entries, assists_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Quick export error: {str(e)}")
        QMessageBox.critical(main_window, "Quick Export Error", f"Quick export failed: {str(e)}")

def _get_quick_export_folder(main_window) -> str: #vers 1
    """Get export folder with smart defaults"""
    try:
        # Try to load last used folder from settings
        settings = QSettings('IMGFactory', 'QuickExport')
        last_folder = settings.value('last_export_folder', '')
        
        # If we have a recent folder and it exists, offer to use it
        if last_folder and os.path.exists(last_folder):
            reply = QMessageBox.question(
                main_window,
                "Quick Export",
                f"Export to last used folder?\n\n{last_folder}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                return last_folder
        
        # Otherwise, get new folder but start from a smart location
        start_dir = ""
        
        # Try to start from last folder's parent, or current IMG location, or desktop
        if last_folder and os.path.exists(os.path.dirname(last_folder)):
            start_dir = os.path.dirname(last_folder)
        elif hasattr(main_window, 'current_img') and hasattr(main_window.current_img, 'file_path'):
            img_dir = os.path.dirname(main_window.current_img.file_path)
            if os.path.exists(img_dir):
                start_dir = img_dir
        else:
            start_dir = os.path.expanduser("~/Desktop")
        
        # Show folder dialog
        from PyQt6.QtWidgets import QFileDialog
        
        if start_dir:
            folder = QFileDialog.getExistingDirectory(
                main_window, 
                "Quick Export - Select Destination", 
                start_dir
            )
        else:
            folder = get_export_folder(main_window, "Quick Export - Select Destination")
        
        return folder if folder else None
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error getting quick export folder: {e}")
        return get_export_folder(main_window, "Quick Export - Select Destination")

def _save_quick_export_folder(folder: str): #vers 1
    """Save export folder for next quick export"""
    try:
        settings = QSettings('IMGFactory', 'QuickExport')
        settings.setValue('last_export_folder', folder)
    except Exception:
        pass  # Non-critical if save fails

def _start_quick_export_with_progress(main_window, entries, export_folder, export_options): #vers 1
    """Start quick export with minimal progress feedback"""
    try:
        # Create export thread
        export_thread = ExportThread(main_window, entries, export_folder, export_options)
        
        # Create minimal progress dialog
        progress_dialog = QProgressDialog("Quick export in progress...", None, 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(500)  # Only show if takes more than 0.5s
        progress_dialog.setCancelButton(None)     # No cancel for quick export
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            # Minimal message updates for speed
            if progress % 20 == 0:  # Only update every 20%
                progress_dialog.setLabelText(f"Quick export: {progress}%")
            
        def export_finished(success, message, stats):
            progress_dialog.close()
            
            if success:
                # Quick notification with folder info
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚡ Quick export complete: {stats['exported']} files to Assists folder")
                
                # Show brief success message
                brief_msg = f"Quick Export Complete!\n\n{stats['exported']} files exported to Assists folder"
                if export_options.get('organize_by_type', True):
                    brief_msg += "\nFiles organized by type (Models, Textures, etc.)"
                
                QMessageBox.information(main_window, "Quick Export Complete", brief_msg)
                
                # Open assists folder if requested
                if export_options.get('open_folder_after', True):
                    try:
                        import subprocess
                        import platform
                        if platform.system() == "Linux":
                            subprocess.run(["xdg-open", assists_folder])
                        elif platform.system() == "Windows":
                            subprocess.run(["explorer", assists_folder])
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.run(["open", assists_folder])
                    except Exception:
                        pass  # Don't fail if can't open folder
            else:
                # Still show errors
                QMessageBox.critical(main_window, "Quick Export Failed", message)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Quick export failed: {message}")
        
        # Connect signals
        export_thread.progress_updated.connect(update_progress)
        export_thread.export_completed.connect(export_finished)
        
        # Start export
        export_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Quick export thread error: {str(e)}")
        QMessageBox.critical(main_window, "Quick Export Error", f"Failed to start quick export: {str(e)}")

__all__ = [
    'quick_export_function'
]