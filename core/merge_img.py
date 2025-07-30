#this belongs in core/ merge_img.py - Version: 1
# X-Seti - July06 2025 - Img Factory 1.5 - Merge img Functions

#!/usr/bin/env python3
"""
IMG Factory Merge Functions
"""

def merge_img(self): #vers 1
    """Merge multiple IMG files"""
    try:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select IMG files to merge", "", "IMG Files (*.img)"
        )
        if len(files) < 2:
            QMessageBox.warning(self, "Warning", "Select at least 2 IMG files")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save merged IMG as", "", "IMG Files (*.img)"
        )
        if output_file:
            self.log_message(f"Merging {len(files)} IMG files...")
            QMessageBox.information(self, "Info", "Merge functionality coming soon")
    except Exception as e:
        self.log_message(f"❌ Error in merge_img: {str(e)}")
