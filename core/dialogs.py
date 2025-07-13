#this belongs in gui/ dialogs.py - version 4
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory Dialogs - Common Dialog Windows
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QCheckBox, QComboBox, QGroupBox,
    QDialogButtonBox, QMessageBox, QFileDialog, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QIcon
import os


class AboutDialog(QDialog):
    """About IMG Factory dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About IMG Factory")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self._create_ui()
    
    def _create_ui(self):
        """Create about dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with logo/icon
        header_layout = QHBoxLayout()
        
        # Icon/Logo placeholder
        icon_label = QLabel("🏭")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title and version
        title_layout = QVBoxLayout()
        
        title_label = QLabel("IMG Factory 1.5")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Professional IMG Archive Manager")
        subtitle_label.setStyleSheet("color: #666666; font-size: 12pt;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(200)
        description.setHtml("""
        <h3>IMG Factory 1.5 - Python Edition</h3>
        <p>A modern, cross-platform IMG archive manager for GTA and related games.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>Support for IMG versions 1, 2, 3, and Fastman92</li>
        <li>Template system for quick IMG creation</li>
        <li>Import/Export functionality with batch processing</li>
        <li>Background processing and progress tracking</li>
        <li>Cross-platform compatibility</li>
        <li>Modern Qt6-based interface with themes</li>
        </ul>
        
        <p><b>Supported Games:</b></p>
        <ul>
        <li>Grand Theft Auto III, Vice City, San Andreas, IV</li>
        <li>Bully</li>
        </ul>
        """)
        layout.addWidget(description)
        
        # Credits
        credits_label = QLabel("Based on the original IMG Factory by MexUK\nPython edition by X-Seti")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(credits_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

class ExportOptionsDialog(QDialog):
    """Dialog for export options"""
    
    def __init__(self, parent=None, entry_count=0):
        super().__init__(parent)
        self.setWindowTitle("Export Options")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        self.entry_count = entry_count
        self._create_ui()
    
    def _create_ui(self):
        """Create export options UI"""
        layout = QVBoxLayout(self)
        
        # Export location
        location_group = QGroupBox("Export Location")
        location_layout = QVBoxLayout(location_group)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Directory:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Choose export directory...")
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)
        
        location_layout.addLayout(dir_layout)
        layout.addWidget(location_group)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)
        
        self.preserve_structure_check = QCheckBox("Preserve directory structure")
        self.preserve_structure_check.setChecked(True)
        options_layout.addWidget(self.preserve_structure_check)
        
        self.overwrite_check = QCheckBox("Overwrite existing files")
        options_layout.addWidget(self.overwrite_check)
        
        self.create_log_check = QCheckBox("Create export log")
        self.create_log_check.setChecked(True)
        options_layout.addWidget(self.create_log_check)
        
        layout.addWidget(options_group)
        
        # Progress options
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.show_progress_check = QCheckBox("Show progress dialog")
        self.show_progress_check.setChecked(True)
        progress_layout.addWidget(self.show_progress_check)
        
        self.open_folder_check = QCheckBox("Open export folder when complete")
        progress_layout.addWidget(self.open_folder_check)
        
        layout.addWidget(progress_group)
        
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
    
    def _browse_directory(self):
        """Browse for export directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.dir_input.text() or os.path.expanduser("~")
        )
        
        if directory:
            self.dir_input.setText(directory)
    
    def get_options(self):
        """Get export options"""
        return {
            'directory': self.dir_input.text(),
            'preserve_structure': self.preserve_structure_check.isChecked(),
            'overwrite': self.overwrite_check.isChecked(),
            'create_log': self.create_log_check.isChecked(),
            'show_progress': self.show_progress_check.isChecked(),
            'open_folder': self.open_folder_check.isChecked()
        }


class ImportOptionsDialog(QDialog):
    """Dialog for import options"""
    
    def __init__(self, parent=None, file_count=0):
        super().__init__(parent)
        self.setWindowTitle("Import Options")
        self.setMinimumSize(400, 250)
        self.setModal(True)
        self.file_count = file_count
        self._create_ui()
    
    def _create_ui(self):
        """Create import options UI"""
        layout = QVBoxLayout(self)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_rename_check = QCheckBox("Auto-rename conflicting files")
        self.auto_rename_check.setChecked(True)
        options_layout.addWidget(self.auto_rename_check)
        
        self.compress_check = QCheckBox("Compress files when possible")
        options_layout.addWidget(self.compress_check)
        
        self.validate_check = QCheckBox("Validate files after import")
        self.validate_check.setChecked(True)
        options_layout.addWidget(self.validate_check)
        
        layout.addWidget(options_group)
        
        # Conflict resolution
        conflict_group = QGroupBox("Conflict Resolution")
        conflict_layout = QVBoxLayout(conflict_group)
        
        self.conflict_combo = QComboBox()
        self.conflict_combo.addItems([
            "Ask for each conflict",
            "Auto-rename duplicates", 
            "Overwrite existing",
            "Skip existing"
        ])
        self.conflict_combo.setCurrentIndex(1)  # Auto-rename
        conflict_layout.addWidget(self.conflict_combo)
        
        layout.addWidget(conflict_group)
        
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
    
    def get_options(self):
        """Get import options"""
        return {
            'auto_rename': self.auto_rename_check.isChecked(),
            'compress': self.compress_check.isChecked(),
            'validate': self.validate_check.isChecked(),
            'conflict_resolution': self.conflict_combo.currentText()
        }

def show_about_dialog(parent=None):
    """Show about dialog"""
    dialog = AboutDialog(parent)
    dialog.exec()

def show_export_options_dialog(parent=None, entry_count=0):
    """Show export options dialog"""
    dialog = ExportOptionsDialog(parent, entry_count)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_options()
    return None

def show_import_options_dialog(parent=None, file_count=0):
    """Show import options dialog"""
    dialog = ImportOptionsDialog(parent, file_count)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_options()
    return None

def show_error_dialog(parent, title, message, details=None):
    """Show error dialog with optional details"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

def show_warning_dialog(parent, title, message):
    """Show warning dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return msg_box.exec()

def show_question_dialog(parent, title, message):
    """Show question dialog with Yes/No buttons"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
    
    result = msg_box.exec()
    return result == QMessageBox.StandardButton.Yes

def show_info_dialog(parent, title, message):
    """Show information dialog"""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

def show_progress_dialog(parent, title, text, maximum=100):
    """Show progress dialog"""
    progress = QProgressDialog(text, "Cancel", 0, maximum, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)
    progress.show()
    return progress

class ValidationResultsDialog(QDialog):
    """Dialog showing IMG validation results"""
    
    def __init__(self, validation_result, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IMG Validation Results")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self.validation_result = validation_result
        self._create_ui()
    
    def _create_ui(self):
        """Create validation results UI"""
        layout = QVBoxLayout(self)
        
        # Summary
        summary_group = QGroupBox("Validation Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # Overall status
        if self.validation_result.get('is_valid', False):
            status_text = "✅ IMG archive is valid"
            status_color = "#2E7D32"
        else:
            status_text = "❌ IMG archive has issues"
            status_color = "#D32F2F"
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 12pt;")
        summary_layout.addWidget(status_label)
        
        # Statistics
        stats = self.validation_result.get('statistics', {})
        stats_text = f"""
        Total Entries: {stats.get('total_entries', 0)}
        Valid Entries: {stats.get('valid_entries', 0)}
        Warnings: {stats.get('warnings', 0)}
        Errors: {stats.get('errors', 0)}
        """
        
        stats_label = QLabel(stats_text)
        summary_layout.addWidget(stats_label)
        
        layout.addWidget(summary_group)
        
        # Issues details
        if self.validation_result.get('issues'):
            issues_group = QGroupBox("Issues Found")
            issues_layout = QVBoxLayout(issues_group)
            
            issues_text = QTextEdit()
            issues_text.setReadOnly(True)
            issues_text.setMaximumHeight(200)
            
            issues_html = "<table border='1' cellpadding='4'>"
            issues_html += "<tr><th>Type</th><th>Entry</th><th>Description</th></tr>"
            
            for issue in self.validation_result['issues'][:50]:  # Limit to first 50
                issue_type = issue.get('type', 'Unknown')
                entry_name = issue.get('entry', 'N/A')
                description = issue.get('description', 'No description')
                
                color = "#FF6B6B" if issue_type == "Error" else "#FFD700"
                issues_html += f"<tr><td style='background-color: {color};'>{issue_type}</td>"
                issues_html += f"<td>{entry_name}</td><td>{description}</td></tr>"
            
            issues_html += "</table>"
            
            if len(self.validation_result['issues']) > 50:
                issues_html += f"<p><i>... and {len(self.validation_result['issues']) - 50} more issues</i></p>"
            
            issues_text.setHtml(issues_html)
            issues_layout.addWidget(issues_text)
            
            layout.addWidget(issues_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if not self.validation_result.get('is_valid', False):
            fix_btn = QPushButton("🔧 Try Auto-Fix")
            fix_btn.clicked.connect(self._try_auto_fix)
            button_layout.addWidget(fix_btn)
        
        save_report_btn = QPushButton("💾 Save Report")
        save_report_btn.clicked.connect(self._save_report)
        button_layout.addWidget(save_report_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _try_auto_fix(self):
        """Try to automatically fix issues"""
        # Placeholder for auto-fix functionality
        show_info_dialog(self, "Auto-Fix", "Auto-fix functionality not yet implemented")
    
    def _save_report(self):
        """Save validation report to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Validation Report",
            "validation_report.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("IMG Factory Validation Report\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Overall Status: {'Valid' if self.validation_result.get('is_valid') else 'Invalid'}\n\n")
                    
                    # Statistics
                    stats = self.validation_result.get('statistics', {})
                    f.write("Statistics:\n")
                    for key, value in stats.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                    
                    # Issues
                    if self.validation_result.get('issues'):
                        f.write("Issues Found:\n")
                        for i, issue in enumerate(self.validation_result['issues'], 1):
                            f.write(f"{i}. {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}\n")
                            if issue.get('entry'):
                                f.write(f"   Entry: {issue['entry']}\n")
                            f.write("\n")
                
                show_info_dialog(self, "Report Saved", f"Validation report saved to:\n{filename}")
                
            except Exception as e:
                show_error_dialog(self, "Save Error", f"Failed to save report:\n{str(e)}")


def show_validation_results_dialog(validation_result, parent=None):
    """Show validation results dialog"""
    dialog = ValidationResultsDialog(validation_result, parent)
    dialog.exec()


class IMGPropertiesDialog(QDialog):
    """Dialog showing IMG archive properties"""
    
    def __init__(self, img_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IMG Archive Properties")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.img_file = img_file
        self._create_ui()
    
    def _create_ui(self):
        """Create properties dialog UI"""
        layout = QVBoxLayout(self)
        
        # File information
        file_group = QGroupBox("File Information")
        file_layout = QVBoxLayout(file_group)
        
        # Create properties table
        properties = [
            ("File Name", os.path.basename(getattr(self.img_file, 'file_path', 'Unknown'))),
            ("File Size", self._format_file_size()),
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
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _format_file_size(self):
        """Format file size"""
        try:
            if hasattr(self.img_file, 'file_path') and os.path.exists(self.img_file.file_path):
                size = os.path.getsize(self.img_file.file_path)
                if size < 1024:
                    return f"{size} bytes"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                elif size < 1024 * 1024 * 1024:
                    return f"{size / (1024 * 1024):.1f} MB"
                else:
                    return f"{size / (1024 * 1024 * 1024):.1f} GB"
        except:
            pass
        return "Unknown"
    
    def _get_modification_time(self):
        """Get file modification time"""
        try:
            if hasattr(self.img_file, 'file_path') and os.path.exists(self.img_file.file_path):
                import time
                mtime = os.path.getmtime(self.img_file.file_path)
                return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        except:
            pass
        return "Unknown"
    
    def _get_file_type_stats(self):
        """Get file type statistics"""
        stats = {}
        if hasattr(self.img_file, 'entries'):
            for entry in self.img_file.entries:
                ext = getattr(entry, 'extension', 'Unknown')
                stats[ext] = stats.get(ext, 0) + 1
        return stats


def show_img_properties_dialog(img_file, parent=None):
    """Show IMG properties dialog"""
    dialog = IMGPropertiesDialog(img_file, parent)
    dialog.exec()


# Utility functions for file dialogs
def get_img_file_filter():
    """Get file filter for IMG files"""
    return "IMG Archives (*.img);;All Files (*)"


def get_export_directory(parent=None, title="Select Export Directory"):
    """Get export directory from user"""
    return QFileDialog.getExistingDirectory(parent, title)


def get_import_files(parent=None, title="Select Files to Import"):
    """Get files to import from user"""
    files, _ = QFileDialog.getOpenFileNames(
        parent,
        title,
        "",
        "All Files (*);;Models (*.dff);;Textures (*.txd);;Collision (*.col);;Animation (*.ifp);;Audio (*.wav);;Scripts (*.scm)"
    )
    return files


def get_save_img_filename(parent=None, title="Save IMG Archive"):
    """Get filename for saving IMG archive"""
    filename, _ = QFileDialog.getSaveFileName(
        parent,
        title,
        "",
        get_img_file_filter()
    )
    return filename


def get_open_img_filename(parent=None, title="Open IMG Archive"):
    """Get filename for opening IMG archive"""
    filename, _ = QFileDialog.getOpenFileName(
        parent,
        title,
        "",
        get_img_file_filter()
    )
    return filename
