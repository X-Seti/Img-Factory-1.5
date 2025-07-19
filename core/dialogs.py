#this belongs in core/dialogs.py - Version: 12
# X-Seti - July15 2025 - Img Factory 1.5
# Complete dialog classes and threading for IMG Factory

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCheckBox, QComboBox, QProgressBar, QMessageBox, 
                             QFileDialog, QGroupBox, QGridLayout, QTextEdit, QDialogButtonBox,
                             QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

## Methods list -
# ExportOptionsDialog._create_ui
# ExportThread.export_entry
# ExportThread.run
# ImportOptionsDialog._create_ui  
# ImportThread.import_file
# ImportThread.run
# IMGPropertiesDialog._create_ui
# IMGPropertiesDialog._format_size
# IMGPropertiesDialog._get_file_size
# IMGPropertiesDialog._get_file_type_stats
# IMGPropertiesDialog._get_modification_time
# ValidationResultsDialog._create_ui
# get_export_directory
# get_img_file_filter
# get_import_files
# get_open_img_filename
# get_save_img_filename
# show_about_dialog
# show_error_dialog
# show_export_options_dialog
# show_img_properties_dialog
# show_import_options_dialog
# show_info_dialog
# show_progress_dialog
# show_question_dialog
# show_validation_results_dialog
# show_warning_dialog

##Classes -
# ExportOptionsDialog
# ExportThread
# ImportOptionsDialog
# ImportThread
# IMGPropertiesDialog
# ValidationResultsDialog


class IMGPropertiesDialog(QDialog):
    """Dialog showing IMG file properties"""
    
    def __init__(self, img_file, parent=None):
        super().__init__(parent)
        self.img_file = img_file
        self.setWindowTitle("IMG Properties")
        self.setMinimumWidth(400)
        self._create_ui()
    
    def _create_ui(self): #vers 11
        """Create properties UI"""
        layout = QVBoxLayout(self)
        
        # File properties
        file_group = QGroupBox("File Information")
        file_layout = QVBoxLayout(file_group)
        
        properties = [
            ("File Path", getattr(self.img_file, 'file_path', 'Unknown')),
            ("File Size", self._get_file_size()),
            ("Version", getattr(self.img_file, 'version', 'Unknown')),
            ("Platform", getattr(self.img_file, 'platform', 'Unknown')),  
            ("Encrypted", "Yes" if getattr(self.img_file, 'is_encrypted', False) else "No"),
            ("Entry Count", str(len(getattr(self.img_file, 'entries', [])))),
            ("Modified", self._get_modification_time()),
        ]
        
        for label, value in properties:
            prop_layout = QHBoxLayout()
            prop_layout.addWidget(QLabel(f"{label}:"))
            prop_layout.addStretch()
            value_label = QLabel(str(value))
            value_label.setStyleSheet("font-weight: bold;")
            prop_layout.addWidget(value_label)
            file_layout.addLayout(prop_layout)
        
        layout.addWidget(file_group)
        
        # Entry statistics
        stats_group = QGroupBox("Entry Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        # File type breakdown
        file_types = self._get_file_type_stats()
        for file_type, count in file_types.items():
            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel(f"{file_type}:"))
            type_layout.addStretch()
            count_label = QLabel(str(count))
            count_label.setStyleSheet("font-weight: bold;")
            type_layout.addWidget(count_label)
            stats_layout.addLayout(type_layout)
        
        layout.addWidget(stats_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _get_file_size(self): #vers 10
        """Get formatted file size"""
        try:
            if hasattr(self.img_file, 'file_path'):
                size = os.path.getsize(self.img_file.file_path)
                return self._format_size(size)
        except:
            pass
        return "Unknown"
    
    def _format_size(self, size): #vers 8
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _get_modification_time(self):
        """Get file modification time"""
        try:
            if hasattr(self.img_file, 'file_path'):
                import datetime
                mtime = os.path.getmtime(self.img_file.file_path)
                return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
        return "Unknown"
    
    def _get_file_type_stats(self): #vers 8
        """Get file type statistics"""
        stats = {}
        for entry in self.img_file.entries:
            ext = getattr(entry, 'extension', 'Unknown')
            stats[ext] = stats.get(ext, 0) + 1
        return stats


class ExportOptionsDialog(QDialog):
    """Export options dialog"""
    
    def __init__(self, parent=None, entry_count=0): #vers 5
        super().__init__(parent)
        self.entry_count = entry_count
        self.setWindowTitle("Export Options")
        self.setMinimumWidth(400)
        self._create_ui()
    
    def _create_ui(self): #vers 10
        """Create export options UI"""
        layout = QVBoxLayout(self)
        
        # Export destination
        dest_group = QGroupBox("Export Destination")
        dest_layout = QVBoxLayout(dest_group)
        
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select export folder...")
        folder_layout.addWidget(self.folder_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(browse_btn)
        
        dest_layout.addLayout(folder_layout)
        layout.addWidget(dest_group)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)
        
        self.organize_check = QCheckBox("Organize by file type")
        self.organize_check.setChecked(True)
        options_layout.addWidget(self.organize_check)
        
        self.overwrite_check = QCheckBox("Overwrite existing files")
        self.overwrite_check.setChecked(True)
        options_layout.addWidget(self.overwrite_check)
        
        self.create_log_check = QCheckBox("Create export log")
        options_layout.addWidget(self.create_log_check)
        
        layout.addWidget(options_group)
        
        # Info
        info_label = QLabel(f"Ready to export {self.entry_count} entries")
        info_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_folder(self): #vers 3
        """Browse for export folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self.folder_input.setText(folder)
    
    def get_options(self): #vers 4
        """Get export options"""
        return {
            'export_folder': self.folder_input.text(),
            'organize_by_type': self.organize_check.isChecked(),
            'overwrite_existing': self.overwrite_check.isChecked(),
            'create_log': self.create_log_check.isChecked()
        }


class ImportOptionsDialog(QDialog):
    """Import options dialog"""
    
    def __init__(self, parent=None, file_count=0): #vers 5
        super().__init__(parent)
        self.file_count = file_count
        self.setWindowTitle("Import Options")
        self.setMinimumWidth(400)
        self._create_ui()
    
    def _create_ui(self): #vers 10
        """Create import options UI"""
        layout = QVBoxLayout(self)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        self.replace_check = QCheckBox("Replace existing entries")
        self.replace_check.setChecked(True)
        options_layout.addWidget(self.replace_check)
        
        self.validate_check = QCheckBox("Validate files before import")
        self.validate_check.setChecked(True)
        options_layout.addWidget(self.validate_check)
        
        self.backup_check = QCheckBox("Create backup before import")
        options_layout.addWidget(self.backup_check)
        
        self.create_log_check = QCheckBox("Create import log")
        options_layout.addWidget(self.create_log_check)
        
        layout.addWidget(options_group)
        
        # Info
        info_label = QLabel(f"Ready to import {self.file_count} files")
        info_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_options(self): #vers 4
        """Get import options"""
        return {
            'replace_existing': self.replace_check.isChecked(),
            'validate_files': self.validate_check.isChecked(),
            'create_backup': self.backup_check.isChecked(),
            'create_log': self.create_log_check.isChecked()
        }


class ValidationResultsDialog(QDialog):
    """Dialog showing IMG validation results"""
    
    def __init__(self, validation_result, parent=None): #vers 6
        super().__init__(parent)
        self.validation_result = validation_result
        self.setWindowTitle("IMG Validation Results")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self._create_ui()
    
    def _create_ui(self): #vers 10
        """Create validation results UI"""
        layout = QVBoxLayout(self)
        
        # Results text
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        results_text.setFont(QFont("Courier", 9))
        
        # Format results
        result_text = "IMG Validation Results\n" + "="*50 + "\n\n"
        
        if self.validation_result.get('is_valid', False):
            result_text += "✅ Validation PASSED\n\n"
        else:
            result_text += "❌ Validation FAILED\n\n"
        
        # Show errors
        errors = self.validation_result.get('errors', [])
        if errors:
            result_text += f"Errors ({len(errors)}):\n"
            for error in errors:
                result_text += f"  • {error}\n"
            result_text += "\n"
        
        # Show warnings
        warnings = self.validation_result.get('warnings', [])
        if warnings:
            result_text += f"Warnings ({len(warnings)}):\n"
            for warning in warnings:
                result_text += f"  • {warning}\n"
            result_text += "\n"
        
        # Show statistics
        stats = self.validation_result.get('statistics', {})
        if stats:
            result_text += "Statistics:\n"
            for key, value in stats.items():
                result_text += f"  {key}: {value}\n"
        
        results_text.setText(result_text)
        layout.addWidget(results_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)


class ImportThread(QThread):
    """Background import thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, main_window, files_to_import, replace_existing=True, validate_files=True, create_backup=False, create_log=False): #vers 7
        super().__init__()
        self.main_window = main_window
        self.files_to_import = files_to_import
        self.replace_existing = replace_existing
        self.validate_files = validate_files
        self.create_backup = create_backup
        self.create_log = create_log
        
    def run(self): #vers 11
        try:
            from core.utils import validate_import_files, create_backup_before_import, entry_exists_in_img
            
            imported_count = 0
            log_entries = []
            
            # Create backup if requested
            if self.create_backup:
                create_backup_before_import(self.main_window)
            
            # Validate files if requested
            if self.validate_files:
                self.files_to_import = validate_import_files(self.files_to_import)
            
            for i, file_path in enumerate(self.files_to_import):
                filename = os.path.basename(file_path)
                
                # Check if entry already exists
                if not self.replace_existing:
                    if entry_exists_in_img(self.main_window, filename):
                        log_entries.append(f"Skipped: {filename} (already exists)")
                        continue
                
                # Import file
                imported = self.import_file(file_path)
                
                if imported:
                    imported_count += 1
                    log_entries.append(f"Imported: {filename}")
                else:
                    log_entries.append(f"Failed: {filename}")
                
                self.progress.emit(i + 1)
            
            # Create log file if requested
            if self.create_log and log_entries:
                log_path = os.path.join(os.path.dirname(self.files_to_import[0]), 'import_log.txt')
                with open(log_path, 'w') as f:
                    f.write('\n'.join(log_entries))
            
            # Update UI
            from core.utils import refresh_table
            refresh_table(self.main_window)
            
            self.finished.emit(True, f"Imported {imported_count}/{len(self.files_to_import)} files successfully.")
            
        except Exception as e:
            self.finished.emit(False, f"Import error: {str(e)}")
    
    def import_file(self, file_path): #vers 4
        """Import a single file"""
        try:
            filename = os.path.basename(file_path)
            
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Method 1: Use IMG's add_entry method
            if hasattr(self.main_window.current_img, 'add_entry'):
                try:
                    if self.main_window.current_img.add_entry(filename, file_data):
                        return True
                except Exception:
                    pass
            
            # Method 2: Use IMG's import_file method
            if hasattr(self.main_window.current_img, 'import_file'):
                try:
                    if self.main_window.current_img.import_file(file_path):
                        return True
                except Exception:
                    pass
            
            # Method 3: Create entry directly
            if hasattr(self.main_window.current_img, 'entries'):
                try:
                    # Create new entry
                    new_entry = type('Entry', (), {
                        'name': filename,
                        'data': file_data,
                        'size': len(file_data),
                        'get_data': lambda: file_data
                    })()
                    
                    # Remove existing entry if replacing
                    if self.replace_existing:
                        self.main_window.current_img.entries = [
                            e for e in self.main_window.current_img.entries 
                            if getattr(e, 'name', '').lower() != filename.lower()
                        ]
                    
                    self.main_window.current_img.entries.append(new_entry)
                    return True
                except Exception:
                    pass
            
            return False
            
        except Exception:
            return False


class ExportThread(QThread):
    """Background export thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, main_window, entries, export_dir, organize_by_type=True, overwrite=True, create_log=False): #vers 6
        super().__init__()
        self.main_window = main_window
        self.entries = entries
        self.export_dir = export_dir
        self.organize_by_type = organize_by_type
        self.overwrite = overwrite
        self.create_log = create_log
        
    def run(self): #vers 4
        try:
            from core.utils import get_file_type_subfolder
            
            exported_count = 0
            log_entries = []
            
            for i, entry in enumerate(self.entries):
                entry_name = getattr(entry, 'name', f'entry_{i}')
                
                # Determine subfolder
                if self.organize_by_type:
                    subfolder = get_file_type_subfolder(entry_name)
                    output_dir = os.path.join(self.export_dir, subfolder)
                else:
                    output_dir = self.export_dir
                
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, entry_name)
                
                # Skip if file exists and not overwriting
                if os.path.exists(output_path) and not self.overwrite:
                    log_entries.append(f"Skipped: {entry_name} (already exists)")
                    continue
                
                # Export file
                exported = self.export_entry(entry, output_path)
                
                if exported:
                    exported_count += 1
                    log_entries.append(f"Exported: {entry_name}")
                else:
                    log_entries.append(f"Failed: {entry_name}")
                
                self.progress.emit(i + 1)
            
            # Create log file if requested
            if self.create_log and log_entries:
                log_path = os.path.join(self.export_dir, 'export_log.txt')
                with open(log_path, 'w') as f:
                    f.write('\n'.join(log_entries))
            
            self.finished.emit(True, f"Exported {exported_count}/{len(self.entries)} files successfully.")
            
        except Exception as e:
            self.finished.emit(False, f"Export error: {str(e)}")
    
    def export_entry(self, entry, output_path): #vers 6
        """Export a single entry using multiple methods"""
        try:
            # Method 1: Use IMG file's export_entry method
            if hasattr(self.main_window.current_img, 'export_entry'):
                try:
                    if self.main_window.current_img.export_entry(entry, output_path):
                        return True
                except Exception:
                    pass
            
            # Method 2: Use entry's get_data method
            if hasattr(entry, 'get_data'):
                try:
                    entry_data = entry.get_data()
                    if entry_data:
                        with open(output_path, 'wb') as f:
                            f.write(entry_data)
                        return True
                except Exception:
                    pass
            
            # Method 3: Direct data access
            if hasattr(entry, 'data'):
                try:
                    with open(output_path, 'wb') as f:
                        f.write(entry.data)
                    return True
                except Exception:
                    pass
            
            return False
            
        except Exception:
            return False


# Dialog utility functions
def show_img_properties_dialog(img_file, parent=None): #vers 1
    """Show IMG properties dialog"""
    dialog = IMGPropertiesDialog(img_file, parent)
    dialog.exec()


def show_export_options_dialog(parent=None, entry_count=0): #vers 1
    """Show export options dialog"""
    dialog = ExportOptionsDialog(parent, entry_count)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_options()
    return None


def show_import_options_dialog(parent=None, file_count=0): #vers 2
    """Show import options dialog"""
    dialog = ImportOptionsDialog(parent, file_count)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_options()
    return None


def show_validation_results_dialog(validation_result, parent=None): #vers 2
    """Show validation results dialog"""
    dialog = ValidationResultsDialog(validation_result, parent)
    dialog.exec()


def show_error_dialog(parent, title, message, details=None): #vers 2
    """Show error dialog with optional details"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_warning_dialog(parent, title, message): #vers 2
    """Show warning dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return msg_box.exec()


def show_question_dialog(parent, title, message): #vers 2
    """Show question dialog with Yes/No buttons"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
    
    result = msg_box.exec()
    return result == QMessageBox.StandardButton.Yes


def show_info_dialog(parent, title, message): #vers 2
    """Show information dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_progress_dialog(parent, title, text, maximum=100): #vers 2
    """Show progress dialog"""
    progress = QProgressDialog(text, "Cancel", 0, maximum, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)
    progress.show()
    return progress


def show_about_dialog(parent=None): #vers 2
    """Show about dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle("About IMG Factory")
    msg_box.setText("IMG Factory 1.5")
    msg_box.setInformativeText("A comprehensive IMG file editor for GTA games")
    msg_box.setDetailedText(
        "Features:\n"
        "• Import/Export IMG entries\n"
        "• COL file editing\n"
        "• TXD conversion\n"
        "• Project management\n"
        "• Multiple theme support\n\n"
        "X-Seti - 2025"
    )
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


# File dialog utilities
def get_img_file_filter(): #vers 2
    """Get file filter for IMG files"""
    return "IMG Archives (*.img);;All Files (*)"


def get_export_directory(parent=None, title="Select Export Directory"): #vers 1
    """Get export directory from user"""
    return QFileDialog.getExistingDirectory(parent, title)


def get_import_files(parent=None, title="Select Files to Import"): #vers 3
    """Get files to import from user"""
    files, _ = QFileDialog.getOpenFileNames(
        parent,
        title,
        "",
        "All Files (*);;Models (*.dff);;Textures (*.txd);;Collision (*.col);;Animation (*.ifp);;Audio (*.wav);;Scripts (*.scm)"
    )
    return files


def get_save_img_filename(parent=None, title="Save IMG Archive"): #vers 2
    """Get filename for saving IMG archive"""
    filename, _ = QFileDialog.getSaveFileName(
        parent,
        title,
        "",
        get_img_file_filter()
    )
    return filename


def get_open_img_filename(parent=None, title="Open IMG Archive"): #vers 2
    """Get filename for opening IMG archive"""
    filename, _ = QFileDialog.getOpenFileName(
        parent,
        title,
        "",
        get_img_file_filter()
    )
    return filename


# Export all functions
__all__ = [
    'IMGPropertiesDialog',
    'ExportOptionsDialog', 
    'ImportOptionsDialog',
    'ValidationResultsDialog',
    'ImportThread',
    'ExportThread',
    'show_img_properties_dialog',
    'show_export_options_dialog',
    'show_import_options_dialog',
    'show_validation_results_dialog',
    'show_error_dialog',
    'show_warning_dialog',
    'show_question_dialog',
    'show_info_dialog',
    'show_progress_dialog',
    'show_about_dialog',
    'get_img_file_filter',
    'get_export_directory',
    'get_import_files',
    'get_save_img_filename',
    'get_open_img_filename'
]