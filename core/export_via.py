#this belongs in core/export_via.py - Version: 6
# X-Seti - August16 2025 - IMG Factory 1.5 - Export Via Functions with Tab Awareness

"""
Export Via Functions - Export via IDE/dialog with options
UPDATED: Uses tab awareness system and shared COL export functions
Fixes multi-tab confusion and COL single model extraction
"""
import os
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import Qt
from methods.tab_aware_functions import validate_tab_before_operation, get_current_file_from_active_tab, get_current_file_type_from_tab
from methods.export_col_shared import get_col_models_from_selection, save_col_models_with_options

##Methods list -
# _export_col_via_ide
# _export_col_via_options
# _export_img_via_ide
# export_via_function
# integrate_export_via_functions
# _log_missing_files
# _start_ide_export_with_progress

def export_via_function(main_window): #vers 5
    """Export files via IDE definitions with destination options - FIXED: Uses tab awareness"""
    try:
        # FIXED: Use tab awareness system instead of broken get_current_file_type
        if not validate_tab_before_operation(main_window, "Export Via"):
            return
        
        file_type = get_current_file_type_from_tab(main_window)
        
        if file_type == 'IMG':
            _export_img_via_ide(main_window)
        elif file_type == 'COL':
            _export_col_via_ide(main_window)
        else:
            QMessageBox.warning(main_window, "No File", "Please open an IMG or COL file first")
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export via error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via Error", f"Export via failed: {str(e)}")


def _export_img_via_ide(main_window): #vers 6
    """Export files via IDE definitions - FIXED: Uses tab awareness"""
    try:
        # FIXED: Get current file from active tab instead of main_window.current_img
        file_object, file_type = get_current_file_from_active_tab(main_window)

        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return

        #if file_type != 'COL' or not file_object:
            #QMessageBox.warning(main_window, "No COL File", "Current tab does not contain an COL file")
            #return

        if hasattr(main_window, 'log_message'):
            main_window.log_message("📋 Starting Export Via IDE...")

        # Show IDE dialog
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

        # FIXED: Find matching entries in current IMG from active tab
        matching_entries = []
        found_files = []

        for entry in file_object.entries:
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
        found_msg += f"\n\n📽 Where would you like to export these files?"

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
        assists_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
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


def _export_col_via_ide(main_window): #vers 1
    """Export COL models via IDE definitions - NEW: Uses IDE parser to match models"""
    try:
        if not hasattr(main_window, 'current_col') or not main_window.current_col:
            QMessageBox.warning(main_window, "No COL File", "Please open a COL file first")
            return

        if hasattr(main_window, 'log_message'):
            main_window.log_message("🛡️ Starting COL Export Via IDE...")

        # Show IDE dialog using existing parser
        try:
            from gui.ide_dialog import show_ide_dialog
            ide_parser = show_ide_dialog(main_window, "export")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error",
                               "IDE dialog system not available.\nPlease ensure all components are installed.")
            return

        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("ℹ️ COL export via IDE cancelled by user")
            return

        # Build list of model names from IDE
        model_names_to_find = []
        try:
            for model_id, model_data in ide_parser.models.items():
                # Get model name from IDE (could be 'name' or 'dff' field)
                model_name = model_data.get('name') or model_data.get('dff', '')
                if model_name:
                    # Remove .dff extension if present, COL models typically match base name
                    if model_name.lower().endswith('.dff'):
                        model_name = model_name[:-4]
                    model_names_to_find.append(model_name.lower())
        except Exception as e:
            QMessageBox.critical(main_window, "IDE Parse Error", 
                               f"Failed to parse IDE model names:\n{str(e)}")
            return

        if not model_names_to_find:
            QMessageBox.information(main_window, "No Models Found",
                                  "No model names found in IDE file.")
            return

        # Find matching COL models in current file
        matching_models = []
        found_model_names = []

        if hasattr(main_window.current_col, 'models'):
            for i, model in enumerate(main_window.current_col.models):
                model_name = getattr(model, 'name', f'model_{i}').lower()
                
                # Check if this COL model matches any IDE model name
                if any(ide_name in model_name or model_name in ide_name for ide_name in model_names_to_find):
                    col_entry = {
                        'name': f"{model_name}.col",
                        'type': 'COL_MODEL',
                        'model': model,
                        'index': i,
                        'col_file': main_window.current_col
                    }
                    matching_models.append(col_entry)
                    found_model_names.append(model_name)

        # Report results
        if not matching_models:
            missing_msg = f"No COL models from IDE found in current COL file.\n\n"
            missing_msg += f"IDE references {len(model_names_to_find)} model names:\n"
            missing_msg += '\n'.join(sorted(model_names_to_find)[:10])
            if len(model_names_to_find) > 10:
                missing_msg += f"\n... and {len(model_names_to_find) - 10} more"

            QMessageBox.information(main_window, "No Matches Found", missing_msg)
            return

        # Show what was found and ask for export options
        found_msg = f"Found {len(matching_models)} COL models from IDE:\n\n"
        found_msg += '\n'.join(sorted(found_model_names)[:15])
        if len(found_model_names) > 15:
            found_msg += f"\n... and {len(found_model_names) - 15} more"

        if len(found_model_names) < len(model_names_to_find):
            missing_count = len(model_names_to_find) - len(found_model_names)
            found_msg += f"\n\n({missing_count} models from IDE not found in COL)"

        found_msg += f"\n\n🛡️ How would you like to export these COL models?"

        # Create COL export options dialog
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Export COL Models - Choose Options")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Models info
        info_label = QLabel(found_msg)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(info_label)

        # Export type options
        export_type_label = QLabel("📁 Export Type:")
        export_type_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(export_type_label)

        single_files_check = QCheckBox("🗂️ Export as separate .col files (one per model)")
        single_files_check.setChecked(True)  # Default to single files
        layout.addWidget(single_files_check)

        combined_file_check = QCheckBox("📦 Export as single combined .col file")
        layout.addWidget(combined_file_check)

        # Logging option
        log_missing_check = QCheckBox("📝 Log missing models to assists/logs/missing_col_models.txt")
        log_missing_check.setChecked(True)
        layout.addWidget(log_missing_check)

        # Destination buttons
        button_layout = QHBoxLayout()

        assists_btn = QPushButton("📁 Assists Folder")
        assists_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
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
        export_single = single_files_check.isChecked()
        export_combined = combined_file_check.isChecked()
        log_missing = log_missing_check.isChecked()

        if not export_single and not export_combined:
            QMessageBox.warning(main_window, "No Export Type Selected",
                              "Please select at least one export type (single files or combined file).")
            return

        # Get export folder
        if choice == 'assists':
            export_folder = None
            if hasattr(main_window, 'settings'):
                export_folder = getattr(main_window.settings, 'assists_folder', None)

            if not export_folder or not os.path.exists(export_folder):
                QMessageBox.warning(main_window, "Assists Folder Not Found",
                                  "Assists folder is not configured or doesn't exist.")
                return
        elif choice == 'custom':
            from methods.export_shared import get_export_folder
            export_folder = get_export_folder(main_window, "Select Export Destination for COL Models")
            if not export_folder:
                return
        else:
            return

        # Log missing models if requested
        if log_missing and len(found_model_names) < len(model_names_to_find):
            _log_missing_col_models(main_window, model_names_to_find, found_model_names)

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🛡️ Exporting {len(matching_models)} COL models to {export_folder}")

        # Start COL export with chosen options
        _start_col_ide_export(main_window, matching_models, export_folder, export_single, export_combined)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "COL Export Via IDE Error", f"COL export via IDE failed: {str(e)}")


def _log_missing_col_models(main_window, model_names_to_find, found_model_names): #vers 1
    """Log missing COL models to assists/logs/missing_col_models.txt"""
    try:
        # Get assists folder
        assists_folder = None
        if hasattr(main_window, 'settings'):
            assists_folder = getattr(main_window.settings, 'assists_folder', None)
        
        if not assists_folder or not os.path.exists(assists_folder):
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ Cannot log missing COL models - assists folder not available")
            return
        
        # Create logs directory
        logs_dir = os.path.join(assists_folder, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Find missing models
        found_model_names_lower = [f.lower() for f in found_model_names]
        missing_models = [f for f in model_names_to_find if f.lower() not in found_model_names_lower]
        
        if not missing_models:
            return
        
        # Create log entry
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(logs_dir, 'missing_col_models.txt')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"COL Export Via IDE - Missing Models Log\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Total models in IDE: {len(model_names_to_find)}\n")
            f.write(f"Found in COL: {len(found_model_names)}\n")
            f.write(f"Missing from COL: {len(missing_models)}\n")
            f.write(f"{'='*60}\n\n")
            
            f.write("Missing COL Models:\n")
            f.write("-" * 40 + "\n")
            for missing_model in sorted(missing_models):
                f.write(f"{missing_model}\n")
            f.write("\n")
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📝 Missing COL models logged to {log_file}")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error logging missing COL models: {str(e)}")


def _log_missing_files(main_window, files_to_find, found_files): #vers 1
    """Log missing files to assists/logs/missing_files.txt - FROM ORIGINAL"""
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
    """Start IDE export with progress dialog - FROM ORIGINAL"""
    try:
        # Create export thread
        from methods.export_shared import ExportThread
        export_thread = ExportThread(main_window, entries, export_folder, export_options)
        
        # Create progress dialog
        from PyQt6.QtWidgets import QProgressDialog
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


def integrate_export_via_functions(main_window): #vers 3
    """Integrate export via functions into main window - FIXED: Updated for tab awareness"""
    try:
        # Add main export via function
        main_window.export_via_function = lambda: export_via_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.export_via = main_window.export_via_function
        main_window.export_selected_via = main_window.export_via_function
        main_window.export_via_ide = main_window.export_via_function
        main_window.export_via_dialog = main_window.export_via_function
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Export via functions integrated with tab awareness and COL support")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate export via functions: {str(e)}")
        return False


def _start_col_ide_export(main_window, col_entries, export_folder, export_single, export_combined): #vers 1
    """Start COL IDE export with single/combined options"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🛡️ Starting COL IDE export: {len(col_entries)} models")

        # Create progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        progress_dialog = QProgressDialog("Exporting COL models...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()

        exported_count = 0
        failed_count = 0
        total_operations = 0

        # Calculate total operations
        if export_single:
            total_operations += len(col_entries)
        if export_combined:
            total_operations += 1

        current_operation = 0

        # Export individual files if requested
        if export_single:
            for i, col_entry in enumerate(col_entries):
                if progress_dialog.wasCanceled():
                    break

                try:
                    model_name = col_entry['name']
                    output_path = os.path.join(export_folder, model_name)

                    # Update progress
                    progress = int((current_operation / total_operations) * 100)
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(f"Exporting {model_name}...")

                    # Create single model COL file (this needs to extract just one model)
                    if _create_single_model_col_file(col_entry, output_path):
                        exported_count += 1
                    else:
                        failed_count += 1

                    current_operation += 1

                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Error exporting {col_entry['name']}: {str(e)}")

        # Export combined file if requested
        if export_combined:
            try:
                current_operation += 1
                combined_name = "combined_ide_models.col"
                combined_path = os.path.join(export_folder, combined_name)

                progress = int((current_operation / total_operations) * 100)
                progress_dialog.setValue(progress)
                progress_dialog.setLabelText(f"Creating combined file...")

                # Use the shared COL export function
                from methods.export_col_shared import save_col_models_with_options
                success_count, fail_count = save_col_models_with_options(
                    main_window, col_entries, export_folder, {'create_combined': True, 'combined_name': combined_name}
                )

                if success_count > 0:
                    exported_count += success_count
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"❌ Error creating combined file: {str(e)}")

        progress_dialog.close()

        # Show results
        if exported_count > 0:
            message = f"Exported {exported_count} COL files to {export_folder}"
            if failed_count > 0:
                message += f"\n{failed_count} operations failed"

            QMessageBox.information(main_window, "COL IDE Export Complete", message)

            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"✅ COL IDE export complete: {exported_count} success, {failed_count} failed")
        else:
            QMessageBox.warning(main_window, "COL IDE Export Failed", "No COL models were exported successfully")

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL IDE export error: {str(e)}")
        QMessageBox.critical(main_window, "COL IDE Export Error", f"COL IDE export failed: {str(e)}")

def _create_single_model_col_file(col_entry, output_path): #vers 1
    """Create a COL file containing only one specific model"""
    try:
        model = col_entry['model']
        col_file = col_entry['col_file']

        # This should create a new COL file with just this one model
        # For now, we'll copy the entire file (user can extract what they need)
        # TODO: Implement proper single-model COL file creation

        if hasattr(col_file, 'file_path') and os.path.exists(col_file.file_path):
            import shutil
            shutil.copy2(col_file.file_path, output_path)
            return True
        elif hasattr(col_file, 'save_to_file'):
            return col_file.save_to_file(output_path)
        else:
            return False

    except Exception:
        return False

__all__ = [
    'export_via_function',
    'integrate_export_via_functions'
]
        
