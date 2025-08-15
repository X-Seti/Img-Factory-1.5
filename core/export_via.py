#this belongs in core/export_via.py - Version: 1
# X-Seti - Aug15 2025 - IMG Factory 1.5 - Export Via IDE Functions

"""
Export Via IDE Functions - Export based on IDE file relationships
Fixed destination folder selection UI and proper IDE integration
"""
import os
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from methods.export_shared import ExportThread, get_export_folder, validate_export_entries

##Methods list -
# export_via_function

def export_via_function(main_window): #vers 2
    """Export files via IDE definitions with single dialog and destination options"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("📋 Starting Export Via IDE...")
        
        # Show IDE dialog - KEEP THIS ONE
        try:
            from gui.ide_dialog import show_ide_dialog
            ide_parser = show_ide_dialog(main_window, "export")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error", 
                               "IDE dialog system not available.\nPlease ensure all components are installed.")
            return
        
        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("ℹ️ Export via IDE cancelled by user")
            return
        
        # Build list of filenames from IDE relationships
        files_to_find = []
        try:
            for model_id, model_data in ide_parser.models.items():
                # Add DFF file
                if 'dff' in model_data and model_data['dff']:
                    files_to_find.append(model_data['dff'])
                
                # Add TXD file (with extension)
                if 'txd' in model_data and model_data['txd']:
                    txd_name = model_data['txd']
                    if not txd_name.lower().endswith('.txd'):
                        txd_name += '.txd'
                    files_to_find.append(txd_name)
        except Exception as e:
            QMessageBox.critical(main_window, "IDE Parse Error", 
                               f"Failed to parse IDE relationships:\n{str(e)}")
            return
        
        if not files_to_find:
            QMessageBox.information(main_window, "No Files Found", 
                                  "No valid file relationships found in IDE file.")
            return
        
        # Find matching entries in current IMG
        matching_entries = []
        found_files = []
        
        for entry in main_window.current_img.entries:
            entry_name = getattr(entry, 'name', '')
            if entry_name and entry_name.lower() in [f.lower() for f in files_to_find]:
                matching_entries.append(entry)
                found_files.append(entry_name)
        
        # Report results
        if not matching_entries:
            missing_msg = f"No files from IDE found in current IMG.\n\n"
            missing_msg += f"IDE references {len(files_to_find)} files:\n"
            missing_msg += '\n'.join(sorted(files_to_find)[:10])
            if len(files_to_find) > 10:
                missing_msg += f"\n... and {len(files_to_find) - 10} more"
            
            QMessageBox.information(main_window, "No Matches Found", missing_msg)
            return
        
        # Show what was found and ask for destination - SINGLE DIALOG
        found_msg = f"Found {len(matching_entries)} files from IDE in current IMG:\n\n"
        found_msg += '\n'.join(sorted(found_files)[:15])
        if len(found_files) > 15:
            found_msg += f"\n... and {len(found_files) - 15} more"
        
        if len(found_files) < len(files_to_find):
            missing_count = len(files_to_find) - len(found_files)
            found_msg += f"\n\n({missing_count} files from IDE not found in IMG)"
        
        # Add destination options to the confirmation dialog
        found_msg += f"\n\n🔽 Where would you like to export these files?"
        
        # Create custom dialog with destination options and logging checkbox
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton
        
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Export IDE Files - Choose Options")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Files info
        info_label = QLabel(found_msg)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(info_label)
        
        # Logging option
        log_missing_check = QCheckBox("📝 Log missing files to assists/logs/missing_files.txt")
        log_missing_check.setChecked(True)  # Default to checked
        layout.addWidget(log_missing_check)
        
        # Destination buttons
        button_layout = QHBoxLayout()
        
        assists_btn = QPushButton("📁 Assists Folder")
        assists_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; background-color: #e8f5e8; }")
        button_layout.addWidget(assists_btn)
        
        custom_btn = QPushButton("📂 Choose Folder")
        button_layout.addWidget(custom_btn)
        
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect buttons
        dialog.result_choice = None
        assists_btn.clicked.connect(lambda: setattr(dialog, 'result_choice', 'assists') or dialog.accept())
        custom_btn.clicked.connect(lambda: setattr(dialog, 'result_choice', 'custom') or dialog.accept())
        cancel_btn.clicked.connect(dialog.reject)
        
        # Show dialog
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        
        # Get user choices
        choice = dialog.result_choice
        log_missing = log_missing_check.isChecked()
        
        if choice == 'assists':
            # Use Assists folder
            export_folder = None
            if hasattr(main_window, 'settings'):
                export_folder = getattr(main_window.settings, 'assists_folder', None)
            
            if not export_folder or not os.path.exists(export_folder):
                QMessageBox.warning(main_window, "Assists Folder Not Found", 
                                  "Assists folder is not configured or doesn't exist.")
                return
                
            use_assists_structure = True
            
        elif choice == 'custom':
            # Choose custom folder
            export_folder = get_export_folder(main_window, "Select Export Destination for IDE Files")
            if not export_folder:
                return
            use_assists_structure = False
        else:
            return
        
        # Log missing files if requested
        if log_missing and len(found_files) < len(files_to_find):
            _log_missing_files(main_window, files_to_find, found_files)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Exporting {len(matching_entries)} IDE-related files to {export_folder}")
        
        # Export options for IDE export
        export_options = {
            'organize_by_type': True,  # Always organize IDE exports
            'use_assists_structure': use_assists_structure,
            'overwrite': True,
            'create_log': True
        }
        
        # Start export with progress
        _start_ide_export_with_progress(main_window, matching_entries, export_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via IDE Error", f"Export via IDE failed: {str(e)}")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via IDE Error", f"Export via IDE failed: {str(e)}")

def _log_missing_files(main_window, files_to_find, found_files): #vers 1
    """Log missing files to assists/logs/missing_files.txt"""
    try:
        # Get assists folder
        assists_folder = None
        if hasattr(main_window, 'settings'):
            assists_folder = getattr(main_window.settings, 'assists_folder', None)
        
        if not assists_folder or not os.path.exists(assists_folder):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ Cannot log missing files - assists folder not available")
            return
        
        # Create logs directory
        logs_dir = os.path.join(assists_folder, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Find missing files
        found_files_lower = [f.lower() for f in found_files]
        missing_files = [f for f in files_to_find if f.lower() not in found_files_lower]
        
        if not missing_files:
            return
        
        # Create log entry
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(logs_dir, 'missing_files.txt')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Export Via IDE - Missing Files Log\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Total files in IDE: {len(files_to_find)}\n")
            f.write(f"Found in IMG: {len(found_files)}\n")
            f.write(f"Missing from IMG: {len(missing_files)}\n")
            f.write(f"{'='*60}\n\n")
            
            f.write("Missing Files:\n")
            f.write("-" * 40 + "\n")
            for missing_file in sorted(missing_files):
                f.write(f"{missing_file}\n")
            f.write("\n")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📝 Missing files logged to {log_file}")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error logging missing files: {str(e)}")

def _start_ide_export_with_progress(main_window, entries, export_folder, export_options): #vers 1
    """Start IDE export with progress dialog"""
    try:
        # Create export thread
        export_thread = ExportThread(main_window, entries, export_folder, export_options)
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Exporting IDE files...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        
        def update_progress(progress, message):
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(message)
            
        def export_finished(success, message, stats):
            progress_dialog.close()
            if success:
                success_detail = f"IDE Export Complete!\n\n{message}"
                if stats.get('failed', 0) > 0:
                    success_detail += f"\n\nNote: {stats['failed']} files failed to export"
                
                QMessageBox.information(main_window, "IDE Export Complete", success_detail)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ IDE Export: {message}")
            else:
                QMessageBox.critical(main_window, "IDE Export Failed", message)
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ IDE Export: {message}")
        
        def handle_cancel():
            if export_thread.isRunning():
                export_thread.terminate()
                export_thread.wait()
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("🚫 IDE export cancelled by user")
        
        # Connect signals
        export_thread.progress_updated.connect(update_progress)
        export_thread.export_completed.connect(export_finished)
        progress_dialog.canceled.connect(handle_cancel)
        
        # Start export
        export_thread.start()
        progress_dialog.show()
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IDE export thread error: {str(e)}")
        QMessageBox.critical(main_window, "IDE Export Error", f"Failed to start IDE export: {str(e)}")

__all__ = [
    'export_via_function'
]
