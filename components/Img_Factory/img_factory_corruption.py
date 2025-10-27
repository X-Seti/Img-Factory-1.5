#this belongs in components/Img_Factory/img_factory_corruption.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - Corruption Analysis Methods

"""
Corruption Analysis Methods
Handles IMG file corruption detection, analysis, and repair
"""

from typing import Optional
from PyQt6.QtWidgets import QMessageBox
from methods.svg_shared_icons import get_search_icon, get_warning_icon, get_success_icon

##Methods list -
# analyze_corruption
# analyze_img_corruption
# clean_filenames_only
# export_corruption_report
# quick_fix_corruption

def analyze_corruption(self):
    """Analyze and fix IMG corruption"""
    return self.analyze_img_corruption()

def analyze_img_corruption(self): #vers 1
    """Analyze IMG file for corruption - Menu callback"""
    try:
        if not hasattr(self, 'current_img') or not self.current_img:
            QMessageBox.warning(self, "No IMG File", "Please open an IMG file first to analyze corruption")
            return

        self.log_message("Starting IMG corruption analysis...")

        # Show corruption analysis dialog
        from core.img_corruption_analyzer import show_corruption_analysis_dialog
        result = show_corruption_analysis_dialog(self)

        if result:
            # User wants to apply fixes
            report = result['report']
            fix_options = result['fix_options']

            from core.img_corruption_analyzer import fix_corrupted_img
            success = fix_corrupted_img(self.current_img, report, fix_options, self)

            if success:
                self.log_message("IMG corruption fixed successfully")
            else:
                self.log_message("IMG corruption fix failed")
        else:
            self.log_message("Corruption analysis completed (no fixes applied)")

    except Exception as e:
        self.log_message(f"Corruption analysis error: {str(e)}")
        QMessageBox.critical(self, "Analysis Error", f"Corruption analysis failed:\n{str(e)}")

def quick_fix_corruption(self): #vers 1
    """Quick fix common corruption issues - Menu callback"""
    try:
        if not hasattr(self, 'current_img') or not self.current_img:
            QMessageBox.warning(self, "No IMG File", "Please open an IMG file first")
            return

        self.log_message("Quick fixing IMG corruption...")

        # Analyze first
        from core.img_corruption_analyzer import analyze_img_corruption
        report = analyze_img_corruption(self.current_img, self)

        if 'error' in report:
            QMessageBox.critical(self, "Analysis Failed",
                                f"Could not analyze file:\n{report['error']}")
            return

        corrupted_count = len(report.get('corrupted_entries', []))

        if corrupted_count == 0:
            QMessageBox.information(self, "No Corruption",
                                    "No corruption detected in this IMG file!")
            return

        # Confirm quick fix
        reply = QMessageBox.question(self, "Quick Fix Corruption",
                                    f"Found {corrupted_count} corrupted entries.\n\n"
                                    f"Quick fix will:\n"
                                    f"• Clean all filenames\n"
                                    f"• Remove null bytes\n"
                                    f"• Fix control characters\n"
                                    f"• Create backup\n\n"
                                    f"Continue with quick fix?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Apply quick fix options
            quick_fix_options = {
                'fix_filenames': True,
                'remove_invalid': False,  # Don't remove entries in quick fix
                'fix_null_bytes': True,
                'fix_long_names': True,
                'create_backup': True
            }

            from core.img_corruption_analyzer import fix_corrupted_img
            success = fix_corrupted_img(self.current_img, report, quick_fix_options, self)

            if success:
                QMessageBox.information(self, "Quick Fix Complete", f"Successfully fixed {corrupted_count} corrupted entries!\n\nThe IMG file has been cleaned and rebuilt.")
            else:
                self.log_message("Quick corruption fix failed")

    except Exception as e:
        self.log_message(f"Quick fix error: {str(e)}")
        QMessageBox.critical(self, "Quick Fix Error", f"Quick fix failed:\n{str(e)}")

def clean_filenames_only(self): #vers 1
    """Clean only filenames, keep all entries - Menu callback"""
    try:
        if not hasattr(self, 'current_img') or not self.current_img:
            QMessageBox.warning(self, "No IMG File", "Please open an IMG file first")
            return

        self.log_message("Cleaning filenames only...")

        # Analyze corruption
        from core.img_corruption_analyzer import analyze_img_corruption
        report = analyze_img_corruption(self.current_img, self)

        if 'error' in report:
            QMessageBox.critical(self, "Analysis Failed", f"Could not analyze file:\n{report['error']}")
            return

        corrupted_count = len(report.get('corrupted_entries', []))

        if corrupted_count == 0:
            QMessageBox.information(self, "No Corruption", "No filename corruption detected!")
            return

        # Apply filename-only cleaning
        filename_fix_options = {
            'fix_filenames': True,
            'remove_invalid': False,  # Never remove entries
            'fix_null_bytes': True,
            'fix_long_names': True,
            'create_backup': True
        }

        from core.img_corruption_analyzer import fix_corrupted_img
        success = fix_corrupted_img(self.current_img, report, filename_fix_options, self)

        if success:
            self.log_message("Filename cleaning completed")
            QMessageBox.information(self, "Filenames Cleaned", f"Successfully cleaned {corrupted_count} filenames!\n\n", f"All entries preserved, only filenames fixed.")
        else:
            self.log_message("Filename cleaning failed")

    except Exception as e:
        self.log_message(f"Filename cleaning error: {str(e)}")
        QMessageBox.critical(self, "Cleaning Error", f"Filename cleaning failed:\n{str(e)}")

def export_corruption_report(self): #vers 1
    """Export corruption report to file - Menu callback"""
    try:
        if not hasattr(self, 'current_img') or not self.current_img:
            QMessageBox.warning(self, "No IMG File", "Please open an IMG file first")
            return

        self.log_message("Generating corruption report...")

        # Analyze corruption
        from core.img_corruption_analyzer import analyze_img_corruption
        report = analyze_img_corruption(self.current_img, self)

        if 'error' in report:
            QMessageBox.critical(self, "Analysis Failed", f"Could not analyze file:\n{report['error']}")
            return

        # Get save filename
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Corruption Report",
            f"{os.path.splitext(os.path.basename(self.current_img.file_path))[0]}_corruption_report.txt", "Text Files (*.txt);;All Files (*)")

        if filename:
            # Export detailed report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"IMG Corruption Analysis Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"File: {self.current_img.file_path}\n")
                f.write("=" * 60 + "\n\n")

                # Summary
                total_entries = report.get('total_entries', 0)
                corrupted_count = len(report.get('corrupted_entries', []))
                f.write(f"Summary:\n")
                f.write(f"  Total Entries: {total_entries:,}\n")
                f.write(f"  Corrupted Entries: {corrupted_count:,}\n")
                f.write(f"  Corruption Level: {(corrupted_count/total_entries*100) if total_entries > 0 else 0:.1f}%\n")
                f.write(f"  Severity: {report.get('severity', 'Unknown')}\n\n")

                # Issue breakdown
                f.write(f"Issue Breakdown:\n")
                for issue_type, count in report.get('issue_summary', {}).items():
                    f.write(f"  {issue_type}: {count} entries\n")
                f.write("\n")

                # Detailed corrupted entries
                f.write(f"Detailed Corrupted Entries:\n")
                f.write("-" * 60 + "\n")

                for entry in report.get('corrupted_entries', []):
                    f.write(f"\nEntry #{entry.get('index', 0)}:\n")
                    f.write(f"  Original Name: {repr(entry.get('original_name', ''))}\n")
                    f.write(f"  Issues: {', '.join(entry.get('issues', []))}\n")
                    f.write(f"  Suggested Fix: {entry.get('suggested_fix', '')}\n")
                    f.write(f"  Size: {entry.get('size', 0):,} bytes\n")
                    f.write(f"  Offset: 0x{entry.get('offset', 0):08X}\n")

            self.log_message(f"Corruption report exported to: {filename}")
            QMessageBox.information(self, "Report Exported",
                                    f"Corruption report exported to:\n{filename}")

    except Exception as e:
        self.log_message(f"Report export error: {str(e)}")
        QMessageBox.critical(self, "Export Error", f"Report export failed:\n{str(e)}")


__all__ = [
    'analyze_corruption',
    'analyze_img_corruption',
    'quick_fix_corruption',
    'clean_filenames_only',
    'export_corruption_report'
]
