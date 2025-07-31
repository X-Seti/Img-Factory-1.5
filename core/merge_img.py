#!/usr/bin/env python3

#this belongs in core/merge_img.py - Version: 2
# X-Seti - July30 2025 - IMG Factory 1.5 - Merge IMG Functions
# Extracted from components/img_manager.py and imgfactory_old.py

"""
IMG Factory Merge Functions
Combined from working implementations
"""

from PyQt6.QtWidgets import QMessageBox, QFileDialog
from components.img_core_classes import IMGFile, IMGVersion

##Methods list -
# merge_img_function
# merge_img_files

def merge_img_function(main_window): #vers 1
    """Merge multiple IMG files - UI version for buttons"""
    try:
        files, _ = QFileDialog.getOpenFileNames(
            main_window, "Select IMG files to merge", "", "IMG Files (*.img)"
        )
        if len(files) < 2:
            QMessageBox.warning(main_window, "Warning", "Select at least 2 IMG files")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            main_window, "Save merged IMG as", "", "IMG Files (*.img)"
        )
        if output_file:
            main_window.log_message(f"Merging {len(files)} IMG files...")

            # Use the core merge function
            success = merge_img_files(files, output_file)

            if success:
                main_window.log_message(f"✅ Successfully merged {len(files)} IMG files")
                QMessageBox.information(main_window, "Success", f"IMG files merged successfully!\n\nOutput: {output_file}")
            else:
                main_window.log_message("❌ Failed to merge IMG files")
                QMessageBox.critical(main_window, "Error", "Failed to merge IMG files")

    except Exception as e:
        main_window.log_message(f"❌ Error in merge_img: {str(e)}")
        QMessageBox.critical(main_window, "Merge Error", f"Error merging IMG files:\n{str(e)}")


def merge_img_files(img_paths, output_path, version=IMGVersion.VERSION_2): #vers 1
    """Merge multiple IMG files into one - Core implementation from img_manager.py"""
    try:
        merged_img = IMGFile()
        if not merged_img.create_new(output_path, version):
            return False

        total_entries = 0
        successful_merges = 0

        for img_path in img_paths:
            source_img = IMGFile(img_path)
            if source_img.open():
                for entry in source_img.entries:
                    # Check for duplicates - rename if exists
                    existing_names = [e.name for e in merged_img.entries]
                    entry_name = entry.name

                    if entry_name in existing_names:
                        # Add suffix to avoid duplicates
                        base_name, ext = entry_name.rsplit('.', 1) if '.' in entry_name else (entry_name, '')
                        counter = 1
                        while f"{base_name}_{counter}.{ext}" in existing_names:
                            counter += 1
                        entry_name = f"{base_name}_{counter}.{ext}" if ext else f"{base_name}_{counter}"

                    # Get entry data and add to merged IMG
                    try:
                        entry_data = entry.get_data()
                        if merged_img.add_entry(entry_name, entry_data):
                            successful_merges += 1
                        total_entries += 1
                    except Exception as e:
                        print(f"Error adding entry {entry.name}: {e}")
                        continue

                source_img.close()
            else:
                print(f"Failed to open source IMG: {img_path}")

        # Rebuild the merged IMG
        if successful_merges > 0:
            rebuild_success = merged_img.rebuild()
            merged_img.close()

            print(f"Merge complete: {successful_merges}/{total_entries} entries merged")
            return rebuild_success
        else:
            merged_img.close()
            return False

    except Exception as e:
        print(f"Error merging IMG files: {e}")
        return False


def merge_img_ld(self): #vers 1
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

# Export functions
__all__ = [
    'merge_img_function',
    'merge_img_files'
]
