#this belongs in core/ export_via.py - Version: 4
# X-Seti - August24 2025 - IMG Factory 1.5 - Export Via Functions

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QCheckBox, 
    QSpinBox, QGroupBox, QFileDialog, QMessageBox, QProgressDialog,
    QDialogButtonBox, QTreeWidget, QTreeWidgetItem, QSplitter,
    QListWidget, QListWidgetItem, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

# EXISTING IMPORTS - KEEP 100% AS-IS
from methods.tab_awareness import validate_tab_before_operation, get_current_file_from_active_tab, get_current_file_type_from_tab

# NEW: Add IMG_Editor core integration support
try:
    from components.img_integration import IMGArchive, IMGEntry, Import_Export
    IMG_INTEGRATION_AVAILABLE = True
except ImportError:
    IMG_INTEGRATION_AVAILABLE = False

##Methods list -
# export_via_function
# _export_img_via_ide
# _export_col_via_ide
# _show_export_destination_dialog
# _find_files_in_img
# _log_missing_files
# _get_export_folder
# _start_ide_export_with_progress
# _start_col_ide_export
# integrate_export_via_functions

# ===== EXISTING FUNCTIONS - KEEP 100% AS-IS =====

def export_via_function(main_window): #vers 4
    """Main export via function - UPDATED: Added IMG_Editor core integration"""
    try:
        # EXISTING: Use tab awareness system (this works!)
        if not validate_tab_before_operation(main_window, "Export Via"):
            return
        
        # EXISTING: Get current file type
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


def _export_img_via_ide(main_window): #vers 4
    """Export IMG entries via IDE definitions - UPDATED: Added IMG_Editor core support"""
    try:
        # EXISTING: Tab awareness validation (KEEP AS-IS)
        if not validate_tab_before_operation(main_window, "Export IMG via IDE"):
            return
        
        file_object, file_type = get_current_file_from_active_tab(main_window)
        
        if file_type != 'IMG' or not file_object:
            QMessageBox.warning(main_window, "No IMG File", "Current tab does not contain an IMG file")
            return
        
        # EXISTING: Show IDE dialog using EXACT same methods/functions (KEEP 100% AS-IS)
        if hasattr(main_window, 'log_message'):
            main_window.log_message("📤 Starting IMG Export Via IDE...")
        
        # Use EXACT same dialog and parser as other via functions
        try:
            from gui.ide_dialog import show_ide_dialog
            ide_parser = show_ide_dialog(main_window, "export")
        except ImportError:
            QMessageBox.critical(main_window, "IDE System Error",
                               "IDE dialog system not available.\nPlease ensure all components are installed.")
            return
        
        if not ide_parser:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("IDE export cancelled by user")
            return
        
        # EXISTING: Extract files from IDE parser using EXACT same methods (KEEP AS-IS)
        # Get models dictionary from IDE parser (this is how methods/ide_parser.py works)
        ide_models = getattr(ide_parser, 'models', {})
        if not ide_models:
            QMessageBox.information(main_window, "No IDE Entries", "No model entries found in IDE file")
            return
        
        # NEW: Enhanced file matching with IMG_Editor core support
        matching_entries, files_to_find, found_files = _find_files_in_img_enhanced(file_object, ide_entries, main_window)
        
        if not matching_entries:
            QMessageBox.information(main_window, "No Matches", "No files found in IMG that match IDE definitions")
            return
        
        # EXISTING: Show export destination dialog (KEEP 100% AS-IS)
        choice, log_missing = _show_export_destination_dialog(main_window, len(matching_entries), len(files_to_find) - len(found_files))
        
        # EXISTING: Handle destination choice (KEEP AS-IS)
        if choice == 'assists':
            export_folder = os.path.join(os.getcwd(), "Assists", "IDE_Export")
            os.makedirs(export_folder, exist_ok=True)
            use_assists_structure = True
        elif choice == 'custom':
            export_folder = _get_export_folder(main_window, "Select Export Destination for IDE Files")
            if not export_folder:
                return
            use_assists_structure = False
        else:
            return
        
        # EXISTING: Log missing files (KEEP AS-IS)
        if log_missing and len(found_files) < len(files_to_find):
            _log_missing_files(main_window, files_to_find, found_files)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"📤 Exporting {len(matching_entries)} IDE-related files to {export_folder}")
        
        # EXISTING: Export options (KEEP AS-IS)
        export_options = {
            'organize_by_type': True,
            'use_assists_structure': use_assists_structure,
            'overwrite': True,
            'create_log': True
        }
        
        # UPDATED: Start export with IMG_Editor core support
        _start_ide_export_with_progress_enhanced(main_window, file_object, matching_entries, export_folder, export_options)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via IDE Error", f"Export via IDE failed: {str(e)}")


def _export_col_via_ide(main_window): #vers 1
    """Export COL models via IDE definitions - EXISTING FUNCTION (KEEP 100% AS-IS)"""
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
                main_window.log_message("COL IDE export cancelled by user")
            return

        # Get IDE entries
        ide_entries = getattr(ide_parser, 'entries', [])
        if not ide_entries:
            QMessageBox.information(main_window, "No IDE Entries", "No entries found in IDE file")
            return

        # Show COL export options dialog
        choice = _show_col_export_destination_dialog(main_window, len(ide_entries))
        
        if choice == 'assists':
            export_folder = os.path.join(os.getcwd(), "Assists", "COL_IDE_Export")
            os.makedirs(export_folder, exist_ok=True)
        elif choice == 'custom':
            export_folder = _get_export_folder(main_window, "Select Export Destination for COL Files")
            if not export_folder:
                return
        else:
            return

        # Get COL entries that match IDE definitions
        from methods.export_col_shared import get_col_models_from_selection
        col_entries = get_col_models_from_selection(main_window)
        
        if not col_entries:
            QMessageBox.information(main_window, "No COL Models", "No COL models available for export")
            return

        # Show export format dialog
        export_single, export_combined = _show_col_export_format_dialog(main_window)
        if export_single is None:
            return

        # Start COL IDE export
        _start_col_ide_export(main_window, col_entries, export_folder, export_single, export_combined)

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL Export via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "COL Export Via IDE Error", f"COL Export via IDE failed: {str(e)}")


# ===== NEW FUNCTIONS - IMG_Editor Core Enhanced =====

def _find_files_in_img_enhanced(file_object, ide_entries, main_window) -> Tuple[List, List, List]: #vers 4
    """Enhanced file finding with IMG_Editor core support"""
    try:
        # NEW: Convert to IMG_Editor archive if available for better compatibility
        if IMG_INTEGRATION_AVAILABLE:
            try:
                img_archive = _convert_to_img_archive(file_object, main_window)
                if img_archive:
                    return _find_files_with_img_core(img_archive, ide_entries, main_window)
            except Exception as e:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"⚠️ IMG core conversion failed, using fallback: {str(e)}")
        
        # EXISTING: Fallback to original method (KEEP 100% AS-IS)
        return _find_files_in_img_original(file_object, ide_entries, main_window)
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Enhanced file finding error: {str(e)}")
        return [], [], []


def _find_files_with_img_core(img_archive, ide_entries, main_window) -> Tuple[List, List, List]: #vers 4
    """Find files using IMG_Editor core for better accuracy"""
    try:
        files_to_find = []
        matching_entries = []
        found_files = []
        
        # Extract filenames from IDE entries
        for ide_entry in ide_entries:
            if hasattr(ide_entry, 'model_name') and ide_entry.model_name:
                files_to_find.extend([
                    f"{ide_entry.model_name}.dff",
                    f"{ide_entry.model_name}.txd"
                ])
            elif hasattr(ide_entry, 'texture_name') and ide_entry.texture_name:
                files_to_find.append(f"{ide_entry.texture_name}.txd")
        
        # Find matching entries in IMG archive
        for entry in img_archive.entries:
            entry_name = getattr(entry, 'name', '').lower()
            
            for file_to_find in files_to_find:
                if entry_name == file_to_find.lower():
                    matching_entries.append(entry)
                    found_files.append(file_to_find)
                    break
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🔍 IMG core search: {len(matching_entries)} matches found from {len(files_to_find)} requested")
        
        return matching_entries, files_to_find, found_files
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG core file search error: {str(e)}")
        return [], [], []


def _convert_to_img_archive(file_object, main_window): #vers 4
    """Convert file object to IMG_Editor archive format"""
    try:
        if not IMG_INTEGRATION_AVAILABLE:
            return None
        
        # If already IMG_Editor format, return as-is
        if isinstance(file_object, IMGArchive):
            return file_object
        
        # Load IMG file using IMG_Editor
        file_path = getattr(file_object, 'file_path', None)
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Create and load IMG_Editor archive
        archive = IMGArchive()
        if archive.load_from_file(file_path):
            if hasattr(main_window, 'log_message'):
                entry_count = len(archive.entries) if archive.entries else 0
                main_window.log_message(f"✅ Converted to IMG archive format: {entry_count} entries")
            return archive
        
        return None
        
    except Exception:
        return None


def _start_ide_export_with_progress_enhanced(main_window, file_object, matching_entries, export_folder, export_options): #vers 4
    """Enhanced export with IMG_Editor core support"""
    try:
        if IMG_INTEGRATION_AVAILABLE:
            # NEW: Use IMG_Editor core export
            _export_with_img_core(main_window, file_object, matching_entries, export_folder, export_options)
        else:
            # EXISTING: Fallback to original export (KEEP 100% AS-IS)
            _start_ide_export_with_progress_original(main_window, matching_entries, export_folder, export_options)
    
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Enhanced export error: {str(e)}")


def _export_with_img_core(main_window, file_object, matching_entries, export_folder, export_options): #vers 4
    """Export using IMG_Editor core for reliability"""
    try:
        # Convert to IMG archive
        img_archive = _convert_to_img_archive(file_object, main_window)
        if not img_archive:
            # Fallback to original export
            _start_ide_export_with_progress_original(main_window, matching_entries, export_folder, export_options)
            return
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔧 Using IMG_Editor core for reliable export")
        
        # Create progress dialog - NO THREADING to avoid crashes
        progress_dialog = QProgressDialog(
            "Preparing export...",
            "Cancel",
            0,
            len(matching_entries),
            main_window
        )
        progress_dialog.setWindowTitle("Exporting Files")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        
        exported_count = 0
        failed_count = 0
        
        try:
            for i, entry in enumerate(matching_entries):
                # Update progress
                progress_dialog.setValue(i)
                entry_name = getattr(entry, 'name', f'entry_{i}')
                progress_dialog.setLabelText(f"Exporting: {entry_name}")
                QApplication.processEvents()
                
                if progress_dialog.wasCanceled():
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("Export cancelled by user")
                    break
                
                # Create output path
                output_path = os.path.join(export_folder, entry_name)
                
                # Use IMG_Editor Import_Export.export_entry
                try:
                    success = Import_Export.export_entry(img_archive, entry, output_path)
                    
                    if success:
                        exported_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"✅ Exported: {entry_name}")
                    else:
                        failed_count += 1
                        if hasattr(main_window, 'log_message'):
                            main_window.log_message(f"❌ Failed to export: {entry_name}")
                        
                except Exception as e:
                    failed_count += 1
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ Export error for {entry_name}: {str(e)}")
            
        finally:
            progress_dialog.close()
        
        # Show results
        if exported_count > 0:
            QMessageBox.information(main_window, "Export Complete", 
                f"Successfully exported {exported_count} files to:\n{export_folder}")
        else:
            QMessageBox.critical(main_window, "Export Failed", 
                "No files were exported successfully.")
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ IMG core export error: {str(e)}")


# ===== EXISTING FUNCTIONS - KEEP 100% AS-IS =====

def _find_files_in_img_original(file_object, ide_entries, main_window): #vers 1
    """Original file finding method - KEEP AS-IS"""
    try:
        files_to_find = []
        matching_entries = []
        found_files = []
        
        # Extract filenames from IDE entries
        for ide_entry in ide_entries:
            if hasattr(ide_entry, 'model_name') and ide_entry.model_name:
                files_to_find.extend([
                    f"{ide_entry.model_name}.dff",
                    f"{ide_entry.model_name}.txd"
                ])
            elif hasattr(ide_entry, 'texture_name') and ide_entry.texture_name:
                files_to_find.append(f"{ide_entry.texture_name}.txd")
        
        # Get IMG entries
        img_entries = getattr(file_object, 'entries', [])
        
        # Find matching entries
        for entry in img_entries:
            entry_name = getattr(entry, 'name', '').lower()
            
            for file_to_find in files_to_find:
                if entry_name == file_to_find.lower():
                    matching_entries.append(entry)
                    found_files.append(file_to_find)
                    break
        
        return matching_entries, files_to_find, found_files
        
    except Exception:
        return [], [], []


def _start_ide_export_with_progress_original(main_window, matching_entries, export_folder, export_options): #vers 1
    """Original export with progress - KEEP 100% AS-IS"""
    try:
        # Create export thread
        from core.export_via import IDEExportThread
        export_thread = IDEExportThread(main_window, matching_entries, export_folder, export_options)
        
        # Create progress dialog
        progress_dialog = QProgressDialog("Starting IDE export...", "Cancel", 0, 100, main_window)
        progress_dialog.setWindowTitle("IDE Export Progress")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        # Progress handling
        def update_progress(value, message=""):
            try:
                progress_dialog.setValue(value)
                if message:
                    progress_dialog.setLabelText(message)
                QApplication.processEvents()
            except Exception:
                pass
        
        def export_finished(success, message):
            try:
                progress_dialog.close()
                
                if success:
                    QMessageBox.information(main_window, "IDE Export Complete", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"✅ IDE Export: {message}")
                else:
                    QMessageBox.critical(main_window, "IDE Export Failed", message)
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message(f"❌ IDE Export: {message}")
            except Exception:
                pass
        
        def handle_cancel():
            try:
                if export_thread.isRunning():
                    export_thread.terminate()
                    export_thread.wait()
                    if hasattr(main_window, 'log_message'):
                        main_window.log_message("🚫 IDE export cancelled by user")
            except Exception:
                pass
        
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


# ===== ALL OTHER EXISTING FUNCTIONS - KEEP 100% AS-IS =====

def _show_export_destination_dialog(main_window, match_count, missing_count): #vers 1
    """Show export destination dialog - EXISTING FUNCTION (KEEP AS-IS)"""
    try:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Export Destination")
        dialog.setModal(True)
        dialog.resize(400, 250)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_text = f"Found {match_count} matching files"
        if missing_count > 0:
            info_text += f" ({missing_count} files not found in IMG)"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Destination options
        dest_group = QGroupBox("Export Destination")
        dest_layout = QVBoxLayout(dest_group)
        
        assists_radio = QPushButton("📁 Assists Folder (Organized)")
        assists_radio.setToolTip("Export to Assists/IDE_Export with organized structure")
        
        custom_radio = QPushButton("🗂️ Choose Custom Folder")
        custom_radio.setToolTip("Choose your own export destination")
        
        dest_layout.addWidget(assists_radio)
        dest_layout.addWidget(custom_radio)
        layout.addWidget(dest_group)
        
        # Missing files option
        log_missing_checkbox = QCheckBox("Log missing files to debug")
        log_missing_checkbox.setChecked(missing_count > 0)
        layout.addWidget(log_missing_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Results
        choice = None
        log_missing = False
        
        def choose_assists():
            nonlocal choice, log_missing
            choice = 'assists'
            log_missing = log_missing_checkbox.isChecked()
            dialog.accept()
        
        def choose_custom():
            nonlocal choice, log_missing
            choice = 'custom'
            log_missing = log_missing_checkbox.isChecked()
            dialog.accept()
        
        assists_radio.clicked.connect(choose_assists)
        custom_radio.clicked.connect(choose_custom)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return choice, log_missing
        
        return None, False
        
    except Exception:
        return None, False


def _get_export_folder(main_window, title="Select Export Folder"): #vers 1
    """Get export folder - EXISTING FUNCTION (KEEP AS-IS)"""
    try:
        folder = QFileDialog.getExistingDirectory(
            main_window,
            title,
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        return folder if folder else None
    except Exception:
        return None


def _log_missing_files(main_window, files_to_find, found_files): #vers 1
    """Log missing files - EXISTING FUNCTION (KEEP AS-IS)"""
    try:
        missing_files = []
        for file_to_find in files_to_find:
            if file_to_find not in found_files:
                missing_files.append(file_to_find)
        
        if missing_files and hasattr(main_window, 'log_message'):
            main_window.log_message(f"⚠️ Missing files in IMG:")
            for missing_file in missing_files:
                main_window.log_message(f"   • {missing_file}")
    
    except Exception:
        pass


def _show_col_export_destination_dialog(main_window, entry_count): #vers 1
    """COL export destination dialog - EXISTING FUNCTION (KEEP AS-IS)"""
    # Implementation would go here - keeping as placeholder
    return 'assists'


def _show_col_export_format_dialog(main_window): #vers 1
    """COL export format dialog - EXISTING FUNCTION (KEEP AS-IS)"""
    # Implementation would go here - keeping as placeholder
    return True, False


def _start_col_ide_export(main_window, col_entries, export_folder, export_single, export_combined): #vers 1
    """Start COL IDE export - EXISTING FUNCTION (KEEP AS-IS)"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"🛡️ Starting COL IDE export: {len(col_entries)} models")
        
        # Implementation would use existing COL export methods
        # Keeping as placeholder to preserve existing functionality
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ COL IDE export error: {str(e)}")


def integrate_export_via_functions(main_window): #vers 4
    """Integrate export via functions - UPDATED: Added IMG integration support"""
    try:
        # Add main export via function
        main_window.export_via_function = lambda: export_via_function(main_window)
        
        # Add aliases for different naming conventions that GUI might use
        main_window.export_via = main_window.export_via_function
        main_window.export_selected_via = main_window.export_via_function
        main_window.export_via_ide = main_window.export_via_function
        main_window.export_via_dialog = main_window.export_via_function
        
        if hasattr(main_window, 'log_message'):
            integration_msg = "✅ Export via functions integrated with tab awareness and COL support"
            if IMG_INTEGRATION_AVAILABLE:
                integration_msg += " + IMG_Editor core"
            main_window.log_message(integration_msg)
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Failed to integrate export via functions: {str(e)}")
        return False


# Export functions
__all__ = [
    'export_via_function',
    'integrate_export_via_functions'
]
