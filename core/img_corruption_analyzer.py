#this belongs in core/img_corruption_analyzer.py - Version: 1
# X-Seti - Aug09 2025 - IMG Factory 1.5 - IMG Corruption Analyzer

"""
IMG Corruption Analyzer and Fixer
Detects corrupted filenames, invalid entries, and provides cleaning options
"""

import os
import struct
import re
from typing import List, Dict, Tuple, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QGroupBox, QCheckBox,
                            QProgressDialog, QMessageBox, QTabWidget, QWidget,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

##Methods list -
# analyze_img_corruption
# show_corruption_analysis_dialog
# fix_corrupted_img
# setup_corruption_analyzer

##Classes -
# CorruptionAnalysisDialog

class CorruptionAnalysisDialog(QDialog):
    """Dialog showing corruption analysis and fix options"""
    
    def __init__(self, parent=None, corruption_report=None):
        super().__init__(parent)
        self.setWindowTitle("IMG Corruption Analysis")
        self.setModal(True)
        self.setFixedSize(700, 600)
        self.corruption_report = corruption_report or {}
        
        self.setup_ui()
        self.populate_data()
        
    def setup_ui(self):
        """Setup the analysis dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("🔍 IMG Corruption Analysis")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        
        # Summary tab
        self.create_summary_tab()
        
        # Corrupted entries tab
        self.create_corrupted_entries_tab()
        
        # Fix options tab
        self.create_fix_options_tab()
        
        layout.addWidget(self.tabs)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(self.export_btn)
        
        self.fix_btn = QPushButton("Fix Corruption")
        self.fix_btn.clicked.connect(self.fix_corruption)
        button_layout.addWidget(self.fix_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def create_summary_tab(self):
        """Create corruption summary tab"""
        summary_widget = QWidget()
        layout = QVBoxLayout(summary_widget)
        
        # Summary info
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
        self.tabs.addTab(summary_widget, "📊 Summary")
        
    def create_corrupted_entries_tab(self):
        """Create corrupted entries table tab"""
        entries_widget = QWidget()
        layout = QVBoxLayout(entries_widget)
        
        # Corrupted entries table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(5)
        self.entries_table.setHorizontalHeaderLabels([
            "Entry #", "Original Name", "Issues", "Suggested Fix", "Size"
        ])
        
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.entries_table)
        
        self.tabs.addTab(entries_widget, "🔧 Corrupted Entries")
        
    def create_fix_options_tab(self):
        """Create fix options tab"""
        fix_widget = QWidget()
        layout = QVBoxLayout(fix_widget)
        
        # Fix options
        options_group = QGroupBox("Corruption Fix Options:")
        options_layout = QVBoxLayout(options_group)
        
        self.fix_filenames_check = QCheckBox("Fix corrupted filenames")
        self.fix_filenames_check.setChecked(True)
        options_layout.addWidget(self.fix_filenames_check)
        
        self.remove_invalid_entries_check = QCheckBox("Remove completely invalid entries")
        self.remove_invalid_entries_check.setChecked(False)
        options_layout.addWidget(self.remove_invalid_entries_check)
        
        self.fix_null_bytes_check = QCheckBox("Remove null bytes from filenames")
        self.fix_null_bytes_check.setChecked(True)
        options_layout.addWidget(self.fix_null_bytes_check)
        
        self.fix_long_names_check = QCheckBox("Truncate overly long filenames")
        self.fix_long_names_check.setChecked(True)
        options_layout.addWidget(self.fix_long_names_check)
        
        self.create_backup_check = QCheckBox("Create backup before fixing")
        self.create_backup_check.setChecked(True)
        options_layout.addWidget(self.create_backup_check)
        
        layout.addWidget(options_group)
        
        # Preview of fixes
        preview_group = QGroupBox("Fix Preview:")
        preview_layout = QVBoxLayout(preview_group)
        
        self.fix_preview = QTextEdit()
        self.fix_preview.setReadOnly(True)
        self.fix_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.fix_preview)
        
        layout.addWidget(preview_group)
        
        self.tabs.addTab(fix_widget, "🛠️ Fix Options")
        
    def populate_data(self):
        """Populate dialog with corruption data"""
        report = self.corruption_report
        
        # Populate summary
        total_entries = report.get('total_entries', 0)
        corrupted_count = len(report.get('corrupted_entries', []))
        corruption_percentage = (corrupted_count / total_entries * 100) if total_entries > 0 else 0
        
        summary = f"""IMG Corruption Analysis Report
=====================================

Total Entries: {total_entries:,}
Corrupted Entries: {corrupted_count:,}
Corruption Level: {corruption_percentage:.1f}%

Issue Breakdown:
"""
        
        issues = report.get('issue_summary', {})
        for issue_type, count in issues.items():
            summary += f"• {issue_type}: {count} entries\n"
        
        summary += f"""
File Information:
• File Size: {report.get('file_size', 0):,} bytes
• IMG Version: {report.get('img_version', 'Unknown')}
• Platform: {report.get('platform', 'Unknown')}

Corruption Severity: {report.get('severity', 'Unknown')}
"""
        
        self.summary_text.setPlainText(summary)
        
        # Populate corrupted entries table
        corrupted_entries = report.get('corrupted_entries', [])
        self.entries_table.setRowCount(len(corrupted_entries))
        
        for row, entry in enumerate(corrupted_entries):
            self.entries_table.setItem(row, 0, QTableWidgetItem(str(entry.get('index', row))))
            self.entries_table.setItem(row, 1, QTableWidgetItem(repr(entry.get('original_name', ''))))
            self.entries_table.setItem(row, 2, QTableWidgetItem(', '.join(entry.get('issues', []))))
            self.entries_table.setItem(row, 3, QTableWidgetItem(entry.get('suggested_fix', '')))
            self.entries_table.setItem(row, 4, QTableWidgetItem(f"{entry.get('size', 0):,} bytes"))
        
        # Update fix preview
        self.update_fix_preview()
        
    def update_fix_preview(self):
        """Update fix preview text"""
        corrupted_entries = self.corruption_report.get('corrupted_entries', [])
        
        preview = "Fix Preview:\n============\n\n"
        
        for entry in corrupted_entries[:10]:  # Show first 10
            original = entry.get('original_name', '')
            fixed = entry.get('suggested_fix', '')
            preview += f"'{original}' → '{fixed}'\n"
        
        if len(corrupted_entries) > 10:
            preview += f"... and {len(corrupted_entries) - 10} more entries\n"
        
        self.fix_preview.setPlainText(preview)
        
    def get_fix_options(self) -> Dict:
        """Get selected fix options"""
        return {
            'fix_filenames': self.fix_filenames_check.isChecked(),
            'remove_invalid': self.remove_invalid_entries_check.isChecked(),
            'fix_null_bytes': self.fix_null_bytes_check.isChecked(),
            'fix_long_names': self.fix_long_names_check.isChecked(),
            'create_backup': self.create_backup_check.isChecked()
        }
        
    def export_report(self):
        """Export corruption report to file"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Corruption Report", 
                "corruption_report.txt", "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.summary_text.toPlainText())
                    f.write("\n\nDetailed Corrupted Entries:\n")
                    f.write("=" * 50 + "\n")
                    
                    for entry in self.corruption_report.get('corrupted_entries', []):
                        f.write(f"\nEntry #{entry.get('index', 0)}:\n")
                        f.write(f"  Original: {repr(entry.get('original_name', ''))}\n")
                        f.write(f"  Issues: {', '.join(entry.get('issues', []))}\n")
                        f.write(f"  Fix: {entry.get('suggested_fix', '')}\n")
                        f.write(f"  Size: {entry.get('size', 0)} bytes\n")
                
                QMessageBox.information(self, "Export Complete", f"Report exported to:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export report:\n{str(e)}")
            
    def fix_corruption(self):
        """Apply corruption fixes"""
        self.accept()


def analyze_img_corruption(img_file, main_window) -> Dict: #vers 1
    """Analyze IMG file for corruption issues"""
    try:
        main_window.log_message("🔍 Analyzing IMG file for corruption...")
        
        report = {
            'total_entries': len(img_file.entries),
            'corrupted_entries': [],
            'issue_summary': {},
            'file_size': os.path.getsize(img_file.file_path) if img_file.file_path else 0,
            'img_version': getattr(img_file, 'version', 'Unknown'),
            'platform': 'Unknown',
            'severity': 'Unknown'
        }
        
        corrupted_entries = []
        issue_counts = {}
        
        # Analyze each entry
        for i, entry in enumerate(img_file.entries):
            issues = []
            original_name = entry.name
            suggested_fix = original_name
            
            # Check for null bytes
            if '\x00' in original_name[:-1]:  # Allow null at end
                issues.append("Embedded null bytes")
                suggested_fix = original_name.replace('\x00', '')
                issue_counts['null_bytes'] = issue_counts.get('null_bytes', 0) + 1
            
            # Check for control characters
            control_chars = [char for char in original_name if ord(char) < 32 and char != '\x00']
            if control_chars:
                issues.append(f"Control characters: {[hex(ord(c)) for c in control_chars]}")
                suggested_fix = ''.join(char for char in suggested_fix if ord(char) >= 32 or char == '\x00')
                issue_counts['control_chars'] = issue_counts.get('control_chars', 0) + 1
            
            # Check for extended ASCII
            extended_chars = [char for char in original_name if ord(char) > 127]
            if extended_chars:
                issues.append(f"Extended ASCII: {[hex(ord(c)) for c in extended_chars]}")
                suggested_fix = suggested_fix.encode('ascii', errors='replace').decode('ascii')
                issue_counts['extended_ascii'] = issue_counts.get('extended_ascii', 0) + 1
            
            # Check filename length
            if len(original_name) > 24:
                issues.append(f"Filename too long ({len(original_name)} chars)")
                suggested_fix = suggested_fix[:24]
                issue_counts['long_names'] = issue_counts.get('long_names', 0) + 1
            
            # Check for invalid characters
            invalid_chars = [char for char in original_name if char in '<>:"|?*\\']
            if invalid_chars:
                issues.append(f"Invalid characters: {invalid_chars}")
                for char in invalid_chars:
                    suggested_fix = suggested_fix.replace(char, '_')
                issue_counts['invalid_chars'] = issue_counts.get('invalid_chars', 0) + 1
            
            # Check for completely corrupted names
            printable_chars = sum(1 for char in original_name if 32 <= ord(char) <= 126)
            if len(original_name) > 0 and printable_chars / len(original_name) < 0.5:
                issues.append("Severely corrupted filename")
                suggested_fix = f"file_{i:04d}.dat"
                issue_counts['severely_corrupted'] = issue_counts.get('severely_corrupted', 0) + 1
            
            # Check for empty names
            if not original_name.strip('\x00'):
                issues.append("Empty filename")
                suggested_fix = f"unnamed_{i:04d}.dat"
                issue_counts['empty_names'] = issue_counts.get('empty_names', 0) + 1
            
            # Check entry data validity
            if entry.size < 0 or entry.offset < 0:
                issues.append("Invalid size/offset")
                issue_counts['invalid_data'] = issue_counts.get('invalid_data', 0) + 1
            
            # If any issues found, add to corrupted list
            if issues:
                corrupted_entries.append({
                    'index': i,
                    'original_name': original_name,
                    'suggested_fix': suggested_fix,
                    'issues': issues,
                    'size': entry.size,
                    'offset': entry.offset
                })
        
        # Update report
        report['corrupted_entries'] = corrupted_entries
        report['issue_summary'] = issue_counts
        
        # Determine severity
        corruption_percentage = len(corrupted_entries) / len(img_file.entries) * 100 if img_file.entries else 0
        
        if corruption_percentage == 0:
            report['severity'] = "No corruption detected"
        elif corruption_percentage < 5:
            report['severity'] = "Minor corruption"
        elif corruption_percentage < 25:
            report['severity'] = "Moderate corruption"
        else:
            report['severity'] = "Severe corruption"
        
        main_window.log_message(f"🔍 Analysis complete: {len(corrupted_entries)} corrupted entries found ({corruption_percentage:.1f}%)")
        
        return report
        
    except Exception as e:
        main_window.log_message(f"❌ Corruption analysis failed: {str(e)}")
        return {'error': str(e)}


def show_corruption_analysis_dialog(main_window) -> Optional[Dict]: #vers 1
    """Show corruption analysis dialog for current IMG"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first")
            return None
        
        # Analyze corruption
        report = analyze_img_corruption(main_window.current_img, main_window)
        
        if 'error' in report:
            QMessageBox.critical(main_window, "Analysis Failed", f"Corruption analysis failed:\n{report['error']}")
            return None
        
        # Show dialog
        dialog = CorruptionAnalysisDialog(main_window, report)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # User wants to fix corruption
            fix_options = dialog.get_fix_options()
            return {'report': report, 'fix_options': fix_options}
        
        return None
        
    except Exception as e:
        main_window.log_message(f"❌ Corruption dialog error: {str(e)}")
        return None


def fix_corrupted_img(img_file, report, fix_options, main_window) -> bool: #vers 1
    """Fix corrupted IMG file based on analysis and options"""
    try:
        corrupted_entries = report.get('corrupted_entries', [])
        
        if not corrupted_entries:
            main_window.log_message("✅ No corruption to fix")
            return True
        
        main_window.log_message(f"🔧 Fixing {len(corrupted_entries)} corrupted entries...")
        
        # Create backup if requested
        if fix_options.get('create_backup', True):
            backup_path = f"{img_file.file_path}.backup"
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(img_file.file_path, backup_path)
                main_window.log_message(f"✅ Backup created: {os.path.basename(backup_path)}")
        
        # Progress dialog
        progress = QProgressDialog("Fixing corrupted entries...", "Cancel", 0, len(corrupted_entries), main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        fixed_count = 0
        removed_count = 0
        
        # Process each corrupted entry
        for i, corrupt_entry in enumerate(corrupted_entries):
            if progress.wasCanceled():
                break
                
            progress.setValue(i)
            progress.setLabelText(f"Fixing: {corrupt_entry['original_name'][:20]}...")
            
            entry_index = corrupt_entry['index']
            if entry_index < len(img_file.entries):
                entry = img_file.entries[entry_index]
                
                # Apply fixes based on options
                if fix_options.get('remove_invalid', False):
                    # Check if entry should be removed completely
                    if 'severely_corrupted' in corrupt_entry['issues'] or 'invalid_data' in corrupt_entry['issues']:
                        img_file.entries.remove(entry)
                        removed_count += 1
                        main_window.log_message(f"🗑️ Removed severely corrupted entry: {repr(corrupt_entry['original_name'])}")
                        continue
                
                # Fix filename
                if fix_options.get('fix_filenames', True):
                    new_name = corrupt_entry['suggested_fix']
                    
                    if fix_options.get('fix_null_bytes', True):
                        new_name = new_name.replace('\x00', '')
                    
                    if fix_options.get('fix_long_names', True):
                        new_name = new_name[:24]
                    
                    # Ensure name ends with null byte if needed
                    if len(new_name) < 24:
                        new_name = new_name.ljust(24, '\x00')
                    
                    entry.name = new_name
                    fixed_count += 1
                    main_window.log_message(f"🔧 Fixed: {repr(corrupt_entry['original_name'])} → {repr(new_name)}")
        
        progress.close()
        
        # Rebuild IMG with fixed entries
        main_window.log_message("🔧 Rebuilding IMG with fixed entries...")
        
        # Use the fixed fast rebuild to apply changes
        from core.fast_rebuild_fixed import _fixed_fast_rebuild_process
        rebuild_success = _fixed_fast_rebuild_process(img_file, None, main_window)
        
        if rebuild_success:
            result_msg = f"✅ Corruption fix complete!\n\n" \
                        f"Entries fixed: {fixed_count}\n" \
                        f"Entries removed: {removed_count}\n" \
                        f"IMG file rebuilt successfully"
            
            main_window.log_message(f"✅ Corruption fix: {fixed_count} fixed, {removed_count} removed")
            QMessageBox.information(main_window, "Fix Complete", result_msg)
            
            # Refresh table to show cleaned data
            if hasattr(main_window, 'refresh_table'):
                main_window.refresh_table()
            
            return True
        else:
            main_window.log_message("❌ Failed to rebuild IMG after corruption fix")
            QMessageBox.critical(main_window, "Fix Failed", "Failed to rebuild IMG after fixing corruption")
            return False
        
    except Exception as e:
        main_window.log_message(f"❌ Corruption fix error: {str(e)}")
        QMessageBox.critical(main_window, "Fix Error", f"Corruption fix failed: {str(e)}")
        return False


def setup_corruption_analyzer(main_window): #vers 1
    """Setup corruption analyzer methods"""
    try:
        # Add corruption analysis methods
        main_window.analyze_img_corruption = lambda: show_corruption_analysis_dialog(main_window)
        main_window.fix_img_corruption = lambda: show_corruption_analysis_dialog(main_window)
        main_window.clean_img_file = lambda: show_corruption_analysis_dialog(main_window)
        
        main_window.log_message("🔍 IMG corruption analyzer ready")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Corruption analyzer setup failed: {str(e)}")
        return False


# Export functions
__all__ = [
    'analyze_img_corruption',
    'show_corruption_analysis_dialog', 
    'fix_corrupted_img',
    'setup_corruption_analyzer',
    'CorruptionAnalysisDialog'
]