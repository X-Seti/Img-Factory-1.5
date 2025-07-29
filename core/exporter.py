#this belongs in core/export.py - Version: 8
# X-Seti - July15 2025 - Img Factory 1.5
# Export functions for IMG Factory

import os
import shutil
from typing import List, Dict, Set
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QProgressBar, QMessageBox, QFileDialog, QGroupBox, QGridLayout, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont

#from components.img_core_classes import IMGFile, IMGEntry

def get_selected_entries(main_window): #vers 2
    """Get currently selected entries from the table"""
    try:
        selected_entries = []

        if hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            selected_rows = set()

            for item in table.selectedItems():
                selected_rows.add(item.row())

            for row in selected_rows:
                if row < len(main_window.current_img.entries):
                    selected_entries.append(main_window.current_img.entries[row])

        return selected_entries

    except Exception:
        return []


class IDEParser:
    """Parses GTA IDE files for different game versions"""

    def __init__(self): #vers 1
        self.current_section = None
        self.files_to_extract = set()

    def parse_ide_file(self, ide_path: str) -> Set[str]: #vers 1
        """Parse IDE file and return set of files to extract"""
        try:
            with open(ide_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            self.files_to_extract.clear()
            self.current_section = None

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith('//'):
                    continue

                # Check for section headers
                if line.lower() in ['objs', 'tobj', 'aext', 'anim', 'txdp', 'hier', 'cars', 'peds', '2dfx', 'path', 'weap']:
                    self.current_section = line.lower()
                    continue

                # Check for section end
                if line.lower() == 'end':
                    self.current_section = None
                    continue

                # Parse section content
                if self.current_section:
                    self._parse_section_line(line, line_num)

            return self.files_to_extract

        except Exception as e:
            print(f"[ERROR] Failed to parse IDE file {ide_path}: {e}")
            return set()

    def _parse_section_line(self, line: str, line_num: int): #vers 1
        """Parse individual line based on current section"""
        try:
            # Skip 2dfx section entirely
            if self.current_section == '2dfx':
                return

            parts = [part.strip() for part in line.split(',')]
            if len(parts) < 2:
                return

            if self.current_section == 'objs':
                # OBJS: ID, ModelName, TxdName, MeshCount, DrawDist, Flags
                if len(parts) >= 3:
                    model_name = parts[1].strip()
                    txd_name = parts[2].strip()

                    if model_name:
                        # Add all possible file types with this base name
                        self._add_all_file_types(model_name)

                    if txd_name and txd_name != model_name:
                        self._add_all_file_types(txd_name)

            elif self.current_section == 'tobj':
                # TOBJ: ID, ModelName, TxdName, MeshCount, DrawDist, Flags, TimeOn, TimeOff
                if len(parts) >= 3:
                    model_name = parts[1].strip()
                    txd_name = parts[2].strip()

                    if model_name:
                        self._add_all_file_types(model_name)

                    if txd_name and txd_name != model_name:
                        self._add_all_file_types(txd_name)
            elif self.current_section == 'aext':
                        # AEXT: ID, ModelName, TxdName, [timing variables: secs, mins, hours, day, month, year]
                        if len(parts) >= 3:
                            model_name = parts[1].strip()
                            txd_name = parts[2].strip()

                            if model_name:
                                self._add_all_file_types(model_name)

                            if txd_name and txd_name != model_name:
                                self._add_all_file_types(txd_name)
            elif self.current_section == 'anim':
                # ANIM: AnimName, IfpFile, AnimType, BlendTime
                if len(parts) >= 2:
                    anim_name = parts[0].strip()
                    ifp_name = parts[1].strip()

                    if anim_name:
                        self._add_all_file_types(anim_name)
                    if ifp_name and ifp_name != anim_name:
                        self._add_all_file_types(ifp_name)

            elif self.current_section == 'txdp':
                # TXDP: TxdName, ParentTxd
                if len(parts) >= 1:
                    txd_name = parts[0].strip()
                    if txd_name:
                        self._add_all_file_types(txd_name)

            elif self.current_section == 'cars':
                # CARS: ID, ModelName, TxdName, Type, HandlingId, GameName, AnimFile, Class, Freq, Level, CompRules, WheelModelId, WheelScale
                if len(parts) >= 3:
                    model_name = parts[1].strip()
                    txd_name = parts[2].strip()

                    if model_name:
                        self._add_all_file_types(model_name)

                    if txd_name and txd_name != model_name:
                        self._add_all_file_types(txd_name)

            elif self.current_section == 'peds':
                # PEDS: ID, ModelName, TxdName, Type, Stat, AnimGroup, CarsCanDrive, Flags, AnimFile, Radio1, Radio2
                if len(parts) >= 3:
                    model_name = parts[1].strip()
                    txd_name = parts[2].strip()

                    if model_name:
                        self._add_all_file_types(model_name)

                    if txd_name and txd_name != model_name:
                        self._add_all_file_types(txd_name)

            elif self.current_section == 'weap':
                # WEAP: ID, ModelName, TxdName, AnimName, MeshCount, DrawDist, Flags
                if len(parts) >= 3:
                    model_name = parts[1].strip()
                    txd_name = parts[2].strip()

                    if model_name:
                        self._add_all_file_types(model_name)

                    if txd_name and txd_name != model_name:
                        self._add_all_file_types(txd_name)

        except Exception as e:
            print(f"[WARNING] Error parsing IDE line {line_num}: {line} - {e}")

    def _add_all_file_types(self, base_name: str): #vers 1
        """Add all possible file extensions for a base name"""
        if not base_name:
            return

        # Common GTA file extensions (excluding .ide files)
        extensions = [
            '.dff',    # 3D Models
            '.txd',    # Texture Dictionary
            '.col',    # Collision
            '.ifp',    # Animation
            '.ipl',    # Item Placement List
            '.rrr',    # Audio/Radio
            '.dat',    # Data files
            '.cfg',    # Configuration
            '.scm',    # Script
            '.img',    # Archive (nested)
            '.wav',    # Audio
            '.mp3',    # Audio
            '.bmp',    # Bitmap
            '.tga',    # Texture
            '.png',    # Image
            '.jpg',    # Image
            '.jpeg',   # Image
            '.3ds',    # 3D Model
            '.obj',    # 3D Model
            '.mdl',    # Model
            '.anim',   # Animation
            '.cut',    # Cutscene
            '.raw',    # Raw data
            '.bin'     # Binary data
        ]

        for ext in extensions:
            self.files_to_extract.add(f"{base_name}{ext}")


def export_via_function(main_window): #vers 3
    """Export files matching IDE file to chosen folder - COMPLETE REWRITE"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Get IDE file
        ide_file, _ = QFileDialog.getOpenFileName(
            main_window,
            "Select IDE file",
            "",
            "IDE Files (*.ide);;All Files (*)"
        )

        if not ide_file:
            return

        # Get export folder
        export_dir = QFileDialog.getExistingDirectory(main_window, "Select Export Folder")
        if not export_dir:
            return

        # Create subfolder based on IDE filename
        ide_name = os.path.splitext(os.path.basename(ide_file))[0]
        final_export_dir = os.path.join(export_dir, ide_name)
        os.makedirs(final_export_dir, exist_ok=True)

        main_window.log_message(f"📤 Export Via IDE: {os.path.basename(ide_file)}")

        # Parse IDE file using proper parser
        ide_parser = IDEParser()
        files_to_export = ide_parser.parse_ide_file(ide_file)

        if not files_to_export:
            QMessageBox.information(main_window, "No Files Found",
                                  f"No files found in IDE file {os.path.basename(ide_file)}")
            return

        main_window.log_message(f"📋 IDE file contains {len(files_to_export)} file references")

        # Find matching entries in IMG
        img_entries = []
        found_files = []

        for file_to_export in files_to_export:
            for img_entry in main_window.current_img.entries:
                img_entry_name = getattr(img_entry, 'name', '')
                if img_entry_name.lower() == file_to_export.lower():
                    img_entries.append(img_entry)
                    found_files.append(file_to_export)
                    break

        if not img_entries:
            QMessageBox.information(main_window, "No Matches",
                                  f"No files from IDE found in current IMG archive.\n\n"
                                  f"IDE references {len(files_to_export)} files:\n" +
                                  '\n'.join(sorted(list(files_to_export))[:10]) +
                                  ('\n...' if len(files_to_export) > 10 else ''))
            return

        main_window.log_message(f"✅ Found {len(img_entries)} matching files in IMG")

        # Export matching entries
        exported_count = 0
        for i, entry in enumerate(img_entries):
            try:
                output_path = os.path.join(final_export_dir, entry.name)

                if main_window.current_img.export_entry(entry, output_path):
                    exported_count += 1
                    main_window.log_message(f"📤 Exported: {entry.name}")
                else:
                    main_window.log_message(f"❌ Failed: {entry.name}")

            except Exception as e:
                main_window.log_message(f"❌ Error exporting {entry.name}: {str(e)}")

        # Show results
        QMessageBox.information(main_window, "Export Via IDE Complete",
                              f"IDE Analysis:\n"
                              f"• IDE file: {os.path.basename(ide_file)}\n"
                              f"• Files referenced: {len(files_to_export)}\n"
                              f"• Files found in IMG: {len(img_entries)}\n"
                              f"• Files exported: {exported_count}\n\n"
                              f"Exported to: {final_export_dir}")

        main_window.log_message(f"🎯 Export Via IDE complete: {exported_count}/{len(img_entries)} files exported")

    except Exception as e:
        main_window.log_message(f"❌ Export Via IDE error: {str(e)}")
        QMessageBox.critical(main_window, "Export Via IDE Error", f"Export Via IDE failed:\n{str(e)}")

class IMGExportMethods:
    """Adds missing export functionality to IMGFile class"""

    @staticmethod
    def add_export_methods_to_imgfile(): #vers 1
        """Add missing export methods to IMGFile class"""
        try:
            from components.img_core_classes import IMGFile

            def export_entry(self, entry, output_path): #vers 1
                """Export a single entry to file"""
                try:
                    # Use existing read_entry_data method
                    entry_data = self.read_entry_data(entry)
                    if entry_data:
                        # Ensure output directory exists
                        import os
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)

                        # Write data to file
                        with open(output_path, 'wb') as f:
                            f.write(entry_data)
                        return True
                    return False

                except Exception as e:
                    print(f"[ERROR] Failed to export entry {getattr(entry, 'name', 'unknown')}: {e}")
                    return False

            def export_entries(self, entries, output_dir, organize_by_type=True): #vers 1
                """Export multiple entries to directory"""
                import os
                exported_count = 0

                for entry in entries:
                    try:
                        # Determine output path
                        if organize_by_type:
                            ext = os.path.splitext(entry.name)[1].lower()
                            if ext in ['.dff', '.3ds', '.obj']:
                                subfolder = 'models'
                            elif ext in ['.txd', '.png', '.jpg', '.bmp']:
                                subfolder = 'textures'
                            elif ext in ['.col']:
                                subfolder = 'collision'
                            elif ext in ['.ifp']:
                                subfolder = 'animations'
                            else:
                                subfolder = 'other'

                            output_path = os.path.join(output_dir, subfolder, entry.name)
                        else:
                            output_path = os.path.join(output_dir, entry.name)

                        # Export entry
                        if self.export_entry(entry, output_path):
                            exported_count += 1

                    except Exception as e:
                        print(f"[ERROR] Failed to export {entry.name}: {e}")
                        continue

                return exported_count

            # Add methods to IMGFile class
            IMGFile.export_entry = export_entry
            IMGFile.export_entries = export_entries

            print("✅ Added export methods to IMGFile class")
            return True

        except Exception as e:
            print(f"❌ Failed to add export methods to IMGFile class: {e}")
            return False

class ExportOptionsDialog(QDialog):
    """Export options dialog"""
    
    def __init__(self, main_window, entries, export_type="selected"): #vers 2
        super().__init__(main_window)
        self.main_window = main_window
        self.entries = entries
        self.export_type = export_type
        self.setup_ui()
        
    def setup_ui(self): #vers 4
        self.setWindowTitle(f"Export {self.export_type.title()} Files")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Export folder selection
        folder_group = QGroupBox("Export Destination")
        folder_layout = QHBoxLayout()
        
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Select export folder...")
        folder_layout.addWidget(self.folder_path)
        
        folder_btn = QPushButton("Browse")
        folder_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_btn)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout()
        
        self.organize_by_type = QCheckBox("Organize by file type (models/, textures/, etc.)")
        self.organize_by_type.setChecked(True)
        options_layout.addWidget(self.organize_by_type)
        
        self.overwrite_existing = QCheckBox("Overwrite existing files")
        self.overwrite_existing.setChecked(True)
        options_layout.addWidget(self.overwrite_existing)
        
        self.create_log = QCheckBox("Create export log file")
        self.create_log.setChecked(False)
        options_layout.addWidget(self.create_log)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # File count info
        info_label = QLabel(f"Files to export: {len(self.entries)}")
        layout.addWidget(info_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.start_export)
        button_layout.addWidget(export_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def browse_folder(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self.folder_path.setText(folder)
    
    def start_export(self): #vers 2
        if not self.folder_path.text():
            QMessageBox.warning(self, "No Folder", "Please select an export folder.")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.entries))
        
        # Start export thread
        self.export_thread = ExportThread(
            self.main_window,
            self.entries,
            self.folder_path.text(),
            self.organize_by_type.isChecked(),
            self.overwrite_existing.isChecked(),
            self.create_log.isChecked()
        )
        
        self.export_thread.progress.connect(self.progress_bar.setValue)
        self.export_thread.finished.connect(self.export_finished)
        self.export_thread.start()
        
    def export_finished(self, success, message): #vers 2
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Export Complete", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Export Failed", message)



class ExportThread(QThread):
    """Background export thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, main_window, entries, export_dir, organize_by_type, overwrite, create_log): #vers 2
        super().__init__()
        self.main_window = main_window
        self.entries = entries
        self.export_dir = export_dir
        self.organize_by_type = organize_by_type
        self.overwrite = overwrite
        self.create_log = create_log
        
    def run(self):
        try:
            exported_count = 0
            log_entries = []
            
            for i, entry in enumerate(self.entries):
                entry_name = getattr(entry, 'name', f'entry_{i}')
                
                # Determine subfolder
                if self.organize_by_type:
                    ext = os.path.splitext(entry_name)[1].lower()
                    if ext in ['.dff', '.3ds', '.obj']:
                        subfolder = 'models'
                    elif ext in ['.txd', '.png', '.jpg', '.bmp', '.tga']:
                        subfolder = 'textures'
                    elif ext in ['.col']:
                        subfolder = 'collision'
                    elif ext in ['.rrr']:
                        subfolder = 'rrr'
                    elif ext in ['.ipf']:
                        subfolder = 'ipf'
                    else:
                        subfolder = 'other'
                    
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
            if self.create_log:
                log_path = os.path.join(self.export_dir, 'export_log.txt')
                with open(log_path, 'w') as f:
                    f.write('\n'.join(log_entries))
            
            self.finished.emit(True, f"Exported {exported_count}/{len(self.entries)} files successfully.")
            
        except Exception as e:
            self.finished.emit(False, f"Export error: {str(e)}")
    
    def export_entry(self, entry, output_path): #vers 2
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

    def export_selected(self): #vers 6
        """Export selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            selected_rows = []
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectedItems'):
                for item in self.gui_layout.table.selectedItems():
                    if item.column() == 0:  # Only filename column
                        selected_rows.append(item.row())

            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "Please select entries to export.")
                return

            export_dir = QFileDialog.getExistingDirectory(self, "Export To Folder")
            if export_dir:
                self.log_message(f"Exporting {len(selected_rows)} entries...")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Exporting...")

                exported_count = 0
                for i, row in enumerate(selected_rows):
                    progress = int((i + 1) * 100 / len(selected_rows))
                    entry_name = self.gui_layout.table.item(row, 0).text() if self.gui_layout.table.item(row, 0) else f"Entry_{row}"

                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Exporting {entry_name}")

                    # Check if IMG has export_entry method
                    if hasattr(self.current_img, 'export_entry'):
                        #if self.current_img.export_entry(row, export_dir):
                        entry = self.current_img.entries[row]
                        output_path = os.path.join(export_dir, entry.name)
                        if self.current_img.export_entry(entry, output_path):
                            exported_count += 1
                            self.log_message(f"Exported: {entry_name}")
                    else:
                        self.log_message(f"❌ IMG export_entry method not available")
                        break

                self.log_message(f"Export complete: {exported_count}/{len(selected_rows)} files exported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Export complete")

                QMessageBox.information(self, "Export Complete",
                                      f"Exported {exported_count} of {len(selected_rows)} files to {export_dir}")

        except Exception as e:
            error_msg = f"Error exporting files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export error")
            QMessageBox.critical(self, "Export Error", error_msg)

    def export_all(self): #vers 2
        """Export all entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            export_dir = QFileDialog.getExistingDirectory(self, "Export All To Folder")
            if export_dir:
                entry_count = len(self.current_img.entries) if hasattr(self.current_img, 'entries') and self.current_img.entries else 0
                self.log_message(f"Exporting all {entry_count} entries...")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Exporting all...")

                exported_count = 0
                for i, entry in enumerate(self.current_img.entries):
                    progress = int((i + 1) * 100 / entry_count)
                    entry_name = getattr(entry, 'name', f"Entry_{i}")

                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Exporting {entry_name}")

                    # Check if IMG has export_entry method
                    if hasattr(self.current_img, 'export_entry'):
                        #if self.current_img.export_entry(i, export_dir):
                        entry = self.current_img.entries[i]
                        output_path = os.path.join(export_dir, entry.name)
                        if self.current_img.export_entry(entry, output_path):
                            exported_count += 1
                            self.log_message(f"Exported: {entry_name}")
                    else:
                        self.log_message(f"❌ IMG export_entry method not available")
                        break

                self.log_message(f"Export complete: {exported_count}/{entry_count} files exported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Export complete")

                QMessageBox.information(self, "Export Complete",
                                      f"Exported {exported_count} of {entry_count} files to {export_dir}")

        except Exception as e:
            error_msg = f"Error exporting all files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export error")
            QMessageBox.critical(self, "Export Error", error_msg)


    def remove_all_entries(self): #vers 2
        """Remove all entries from IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            reply = QMessageBox.question(self, "Remove All",
                                        "Remove all entries from IMG?")
            if reply == QMessageBox.StandardButton.Yes:
                self.current_img.entries.clear()
                self._update_ui_for_loaded_img()
                self.log_message("All entries removed")
        except Exception as e:
            self.log_message(f"❌ Error in remove_all_entries: {str(e)}")


    def quick_export(self): #vers 2
        """Quick export selected files to default location"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            # Check if we have a selection method available
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if not selected_rows:
                QMessageBox.warning(self, "Warning", "No entries selected")
                return

            # Use Documents/IMG_Exports as default
            export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
            os.makedirs(export_dir, exist_ok=True)

            self.log_message(f"Quick exporting {len(selected_rows)} files to {export_dir}")
            QMessageBox.information(self, "Info", "Quick export functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in quick_export: {str(e)}")

def export_selected_function(main_window): #vers 3
    """Export selected entries"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
            return

        dialog = ExportOptionsDialog(main_window, selected_entries, "selected")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Export error: {str(e)}")
        QMessageBox.critical(main_window, "Export Error", f"Export failed: {str(e)}")


def quick_export_function(main_window): #vers 3
    """Quick export to project folder with organized structure"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        # Check if project folder is set
        if not hasattr(main_window, 'settings') or not main_window.settings.get('project_folder'):
            QMessageBox.warning(main_window, "No Project Folder", "Please set a project folder in settings first.")
            return

        selected_entries = get_selected_entries(main_window)
        if not selected_entries:
            QMessageBox.information(main_window, "No Selection", "Please select entries to export.")
            return

        project_folder = main_window.settings.get('project_folder')
        
        # Create organized export
        dialog = ExportOptionsDialog(main_window, selected_entries, "quick")
        dialog.folder_path.setText(project_folder)
        dialog.organize_by_type.setChecked(True)
        dialog.organize_by_type.setEnabled(False)  # Force organize by type
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Quick Export error: {str(e)}")
        QMessageBox.critical(main_window, "Quick Export Error", f"Quick Export failed: {str(e)}")


def export_all_function(main_window): #vers 2
    """Export all entries with dialog"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        all_entries = main_window.current_img.entries
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "No entries to export.")
            return

        dialog = ExportOptionsDialog(main_window, all_entries, "all")
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Export All error: {str(e)}")
        QMessageBox.critical(main_window, "Export All Error", f"Export All failed: {str(e)}")


def dump_all_function(main_window): #vers 3
    """Dump all entries to single folder - no organization"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            QMessageBox.warning(main_window, "No IMG File", "Please open an IMG file first.")
            return

        all_entries = main_window.current_img.entries
        if not all_entries:
            QMessageBox.information(main_window, "No Entries", "No entries to dump.")
            return

        # Get dump folder
        dump_folder = QFileDialog.getExistingDirectory(main_window, "Select Dump Folder")
        if not dump_folder:
            return

        # Create dump dialog (no organization)
        dialog = ExportOptionsDialog(main_window, all_entries, "dump")
        dialog.folder_path.setText(dump_folder)
        dialog.organize_by_type.setChecked(False)
        dialog.organize_by_type.setEnabled(False)  # Force no organization
        dialog.exec()

    except Exception as e:
        main_window.log_message(f"❌ Dump error: {str(e)}")
        QMessageBox.critical(main_window, "Dump Error", f"Dump failed: {str(e)}")


def integrate_export_functions(main_window): #vers 2
    """Integrate export functions into main window"""
    try:
        main_window.export_selected = lambda: export_selected_function(main_window)
        main_window.export_selected_via = lambda: export_via_function(main_window)
        main_window.quick_export_selected = lambda: quick_export_function(main_window)
        main_window.export_all_entries = lambda: export_all_function(main_window)
        main_window.dump_all_entries = lambda: dump_all_function(main_window)
        
        # Add aliases
        main_window.export_selected_function = main_window.export_selected
        main_window.export_via_function = main_window.export_selected_via
        main_window.quick_export_function = main_window.quick_export_selected
        main_window.export_all_function = main_window.export_all_entries
        main_window.dump_all_function = main_window.dump_all_entries
        
        main_window.log_message("✅ Export functions integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate export functions: {str(e)}")
        return False

def integrate_img_export_methods(main_window): #vers 1
    """Integrate IMG export methods into main window"""
    try:
        # Add the missing methods to IMGFile class
        if IMGExportMethods.add_export_methods_to_imgfile():
            main_window.log_message("✅ IMG export/import methods added - functions should now work")
            return True
        else:
            main_window.log_message("❌ Failed to add IMG export/import methods")
            return False

    except Exception as e:
        main_window.log_message(f"❌ IMG export integration failed: {str(e)}")
        return False

# Export functions
__all__ = [
    'export_selected',
    'remove_all_entries',
    'quick_export',
    'export_all',
    'export_selected_function',
    'export_via_function',
    'quick_export_function',
    'export_all_function',
    'dump_all_function',
    'get_selected_entries',
    'integrate_export_functions'
]
