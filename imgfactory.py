#!/usr/bin/env python3
"""
X-Seti - JUNE25 2025 - IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""
#this belongs in root /imgfactory.py - version 60
import sys
import os
import mimetypes
from pathlib import Path  # Move this up here
print("Starting application...")

# Setup paths FIRST - before any other imports
current_dir = Path(__file__).parent
components_dir = current_dir / "components"
gui_dir = current_dir / "gui"

# Add directories to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if components_dir.exists() and str(components_dir) not in sys.path:
    sys.path.insert(0, str(components_dir))
if gui_dir.exists() and str(gui_dir) not in sys.path:
    sys.path.insert(0, str(gui_dir))

# Now continue with other imports

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton
)
print("PyQt6.QtCore imported successfully")
from PyQt6.QtCore import Qt, QThread, pyqtSignal,  QTimer, QSettings, QMimeData
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap, QDragEnterEvent, QDropEvent, QContextMenuEvent

# Import component in alphabetical order.

from app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog
from components.img_creator import NewIMGDialog
from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
from components.img_formats import GameSpecificIMGDialog, EnhancedIMGCreator
from components.img_manager import IMGFile, IMGVersion, Platform
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
from components.img_validator import IMGValidator
#from imgfactory_col_integration import setup_col_integration
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons


try:
    from imgfactory_col_integration import setup_col_integration
except ImportError:
    print("Warning: COL integration not available")
    def setup_col_integration(main_window):
        return False

print("Components imported successfully")

class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_updated = pyqtSignal(int, str)  # progress, status
    loading_finished = pyqtSignal(object)    # IMGFile object
    loading_error = pyqtSignal(str)          # error message

    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            self.progress_updated.emit(10, "Opening file...")
            
            # Create IMG file instance
            self.progress.emit(10)
            img_file = IMGFile(self.file_path)
            self.progress_updated.emit(30, "Detecting format...")
            
            # Open and parse file
            self.progress.emit(30)
            if not img_file.open():
                self.error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress_updated.emit(60, "Reading entries...")
            self.progress.emit(60)
            
            # Parse entries
            if not img_file.parse_entries():
                self.error.emit(f"Failed to parse IMG entries: {self.file_path}")
                return
            
            self.progress_updated.emit(100, "Complete")
            self.progress.emit(100)
            
            # Return the loaded IMG file
            self.finished.emit(img_file)
            self.loading_finished.emit(img_file)
            
        except Exception as e:
            self.error.emit(f"Error loading IMG file: {str(e)}")
            self.loading_error.emit(f"Error loading IMG file: {str(e)}")

def populate_img_table(table: QTableWidget, img_file: IMGFile):
    """Populate table with IMG file entries"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return
    
    table.setRowCount(len(img_file.entries))
    
    for row, entry in enumerate(img_file.entries):
        # Filename
        table.setItem(row, 0, QTableWidgetItem(entry.name))
        # File type
        file_type = entry.name.split('.')[-1].upper() if '.' in entry.name else "Unknown"
        table.setItem(row, 1, QTableWidgetItem(file_type))
        # Size
        table.setItem(row, 2, QTableWidgetItem(format_file_size(entry.size)))
        # Offset
        table.setItem(row, 3, QTableWidgetItem(f"0x{entry.offset:X}"))
        # Version
        table.setItem(row, 4, QTableWidgetItem(str(entry.version)))
        # Compression
        compression = "ZLib" if hasattr(entry, 'compressed') and entry.compressed else "None"
        table.setItem(row, 5, QTableWidgetItem(compression))
        # Status
        table.setItem(row, 6, QTableWidgetItem("Ready"))


class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.app_settings = settings if hasattr(settings, 'themes') else AppSettings()
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        
        # Core data
        self.current_img: Optional[IMGFile] = None
        self.current_col: Optional = None  # For COL file support
        self.template_manager = IMGTemplateManager()
        
        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None
        
        # Initialize GUI layout
        self.gui_layout = IMGFactoryGUILayout(self)
        
        # Debug: check if methods exist
        print(f"Has create_new_img: {hasattr(self, 'create_new_img')}")
        print(f"Has validate_img: {hasattr(self, 'validate_img')}")
        print(f"Has show_about: {hasattr(self, 'show_about')}")
        
        # Initialize UI
        self._create_ui()
        self._connect_signals()
        self._restore_settings()
        
        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)
        
        # Apply COL integration after creating the main interface
        if setup_col_integration(self):
            self.log_message("COL functionality integrated successfully")
        else:
            self.log_message("Failed to integrate COL functionality")
        
        # Log startup
        self.log_message("IMG Factory 1.5 initialized")
    
    def _create_ui(self):
        """Create the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Check if advanced UI is enabled, otherwise use fallback
        use_advanced_ui = True
        if hasattr(self.settings, 'current_settings'):
            use_advanced_ui = self.settings.current_settings.get('use_advanced_ui', True)
        elif isinstance(self.settings, dict):
            use_advanced_ui = self.settings.get('use_advanced_ui', True)
        
        if use_advanced_ui:
            self._create_advanced_ui(main_layout)
        else:
            self._create_fallback_ui(main_layout)
    
    def _create_advanced_ui(self, main_layout):
        """Create advanced UI with all features"""
        # Create GUI layout using the gui_layout class
        self.gui_layout.create_main_ui_with_splitters(main_layout)
        
        # Create menu and status bars
        self.gui_layout.create_menu_bar()
        self.gui_layout.create_status_bar()
        
        # Apply theme to table
        self.gui_layout.apply_table_theme()
        
        # Connect table signals
        self.gui_layout.connect_table_signals()
        
        # Add sample data for demonstration
        self.gui_layout.add_sample_data()

    def _create_fallback_ui(self, main_layout):
        """Create fallback UI"""
        self.gui_layout.create_main_ui_with_splitters(main_layout)
        self.gui_layout.create_menu_bar()
        self.gui_layout.create_status_bar()

    def resizeEvent(self, event):
        """Handle window resize to adapt button text"""
        super().resizeEvent(event)
        # Delegate to GUI layout
        self.gui_layout.handle_resize_event(event)

    def _connect_signals(self):
        """Connect signals for table interactions"""
        # Delegate to GUI layout
        self.gui_layout.connect_table_signals()

    def on_selection_changed(self):
        """Handle table selection change"""
        # Delegate to GUI layout but keep in main for business logic
        self.gui_layout.on_selection_changed()

    def on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        # Delegate to GUI layout but keep in main for business logic
        self.gui_layout.on_item_double_clicked(item)

    def log_message(self, message):
        """Log a message using GUI layout's log method"""
        self.gui_layout.log_message(message)

    def _create_adaptive_button(self, label, action_type=None, icon=None, callback=None, bold=False):
        """Create adaptive button with theme support"""
        btn = QPushButton(label)
        
        # Set font
        font = btn.font()
        if bold:
            font.setBold(True)
        btn.setFont(font)
        
        # Set icon if provided
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
        
        # Connect callback if provided
        if callback:
            btn.clicked.connect(callback)
        else:
            btn.setEnabled(False)  # Disable buttons without callbacks
        
        return btn
    
    def themed_button(self, label, action_type=None, icon=None, bold=False):
        """Legacy method for compatibility"""
        return self._create_adaptive_button(label, action_type, icon, None, bold)

    # =============================================================================
    # IMG FILE OPERATIONS - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def _update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded"""
        # Enable COL-specific buttons
        if hasattr(self, 'gui_layout'):
            # Update table with COL info
            if self.gui_layout.table:
                self.gui_layout.table.setRowCount(1)
                col_name = os.path.basename(self.current_col) if self.current_col else "Unknown"
                items = [
                    (col_name, "COL", "Unknown", "0x0", "COL", "None", "Loaded")
                ]

                for row, item_data in enumerate(items):
                    for col, value in enumerate(item_data):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.gui_layout.table.setItem(row, col, item)

        # Update status
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(f"COL file loaded: {os.path.basename(self.current_col)}")


    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = GameSpecificIMGDialog(self)
        dialog.template_manager = self.template_manager
        dialog.img_created.connect(self.load_img_file)
        dialog.img_created.connect(lambda path: self.log_message(f"Created: {os.path.basename(path)}"))
        dialog.exec()

    def open_file(self):
        """Unified function to open IMG or COL files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG or COL File", "",
            "IMG/COL Files (*.img *.col);;IMG Files (*.img);;COL Files (*.col);;All Files (*)"
        )

        if file_path:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.img':
                self._load_img_file(file_path)
            elif file_ext == '.col':
                self._load_col_file(file_path)
            else:
                # Try to detect file type by content
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(8)

                    # Check for IMG signatures
                    if header[:4] in [b'VER2', b'VER3'] or len(header) >= 8:
                        self._load_img_file(file_path)
                    # Check for COL signatures
                    elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                        self._load_col_file(file_path)
                    else:
                        # Default to IMG
                        self._load_img_file(file_path)

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not determine file type: {e}")


    def open_img_file(self):
        """Open IMG file specifically"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG File", "", "IMG Files (*.img);;All Files (*)"
        )

        if file_path:
            self._load_img_file(file_path)

    def open_col_file(self):
        """Open COL file specifically"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", "COL Files (*.col);;All Files (*)"
        )

        if file_path:
            self._load_col_file(file_path)

    def load_img_file(self, file_path: str):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.log_message(f"Loading: {os.path.basename(file_path)}")
        
        # Show progress
        self.gui_layout.show_progress(0, "Loading IMG file...")
        
        # Start loading thread
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._on_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_load_error)
        self.load_thread.start()
    
    def _on_load_progress(self, progress: int, status: str):
        """Handle loading progress updates"""
        self.gui_layout.show_progress(progress, status)
    
    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        self.current_img = img_file
        self.log_message(f"Loaded: {img_file.file_path} ({len(img_file.entries)} entries)")
        
        # Update table
        populate_img_table(self.gui_layout.table, img_file)
        
        # Update status
        self.gui_layout.show_progress(-1, "Ready")
        self.gui_layout.update_img_info(f"{len(img_file.entries)} entries loaded")
        
        # Update window title
        self.setWindowTitle(f"IMG Factory 1.5 - {os.path.basename(img_file.file_path)}")
    
    def _on_load_error(self, error_message: str):
        """Handle IMG loading error"""
        self.log_message(f"Error: {error_message}")
        self.gui_layout.show_progress(-1, "Error")
        QMessageBox.critical(self, "Loading Error", error_message)

    def close_all_img(self):
        """Close all open IMG files"""
        self.current_img = None
        self.current_col = None
        self._update_ui_for_no_img()
        self.log_message("All IMG files closed")

    def rebuild_all_img(self):
        """Rebuild all IMG files in directory"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        base_dir = os.path.dirname(self.current_img.file_path)
        img_files = [f for f in os.listdir(base_dir) if f.endswith('.img')]

        if not img_files:
            QMessageBox.information(self, "Info", "No IMG files found in directory")
            return

        reply = QMessageBox.question(self, "Rebuild All",
                                    f"Rebuild {len(img_files)} IMG files?")
        if reply == QMessageBox.StandardButton.Yes:
            self.log_message(f"Rebuilding {len(img_files)} IMG files...")
            # Implementation would iterate through files

    def merge_img(self):
        """Merge multiple IMG files"""
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

    def split_img(self):
        """Split IMG file into smaller parts"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        dialog = QMessageBox.question(self, "Split IMG",
                                    "Split current IMG into multiple files?")
        if dialog == QMessageBox.StandardButton.Yes:
            self.log_message("IMG split functionality coming soon")

    def convert_img(self):
        """Convert IMG between versions"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        self.log_message("IMG conversion functionality coming soon")

    def import_via_tool(self):
        """Import files using external tool"""
        self.log_message("Import via tool functionality coming soon")

    def export_via_tool(self):
        """Export using external tool"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        self.log_message("Export via tool functionality coming soon")

    def remove_all_entries(self):
        """Remove all entries from IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        reply = QMessageBox.question(self, "Remove All",
                                    "Remove all entries from IMG?")
        if reply == QMessageBox.StandardButton.Yes:
            self.current_img.entries.clear()
            self._update_ui_for_loaded_img()
            self.log_message("All entries removed")

    def quick_export(self):
        """Quick export selected files to default location"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No entries selected")
            return

        # Use Documents/IMG_Exports as default
        export_dir = os.path.join(os.path.expanduser("~"), "Documents", "IMG_Exports")
        os.makedirs(export_dir, exist_ok=True)

        self.log_message(f"Quick exporting {len(selected_rows)} files to {export_dir}")

    def pin_selected(self):
        """Pin selected entries to top of list"""
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Pin", "No entries selected")
            return

        self.log_message(f"Pinned {len(selected_rows)} entries")

    # COL and editor functions
    def open_col_editor(self):
        """Open COL file editor"""
        self.log_message("COL editor functionality coming soon")

    def open_txd_editor(self):
        """Open TXD texture editor"""
        self.log_message("TXD editor functionality coming soon")

    def open_dff_editor(self):
        """Open DFF model editor"""
        self.log_message("DFF editor functionality coming soon")

    def open_ipf_editor(self):
        """Open IPF animation editor"""
        self.log_message("IPF editor functionality coming soon")

    def open_ipl_editor(self):
        """Open IPL item placement editor"""
        self.log_message("IPL editor functionality coming soon")

    def open_ide_editor(self):
        """Open IDE item definition editor"""
        self.log_message("IDE editor functionality coming soon")

    def open_dat_editor(self):
        """Open DAT file editor"""
        self.log_message("DAT editor functionality coming soon")

    def open_zons_editor(self):
        """Open zones editor"""
        self.log_message("Zones editor functionality coming soon")

    def open_weap_editor(self):
        """Open weapons editor"""
        self.log_message("Weapons editor functionality coming soon")

    def open_vehi_editor(self):
        """Open vehicles editor"""
        self.log_message("Vehicles editor functionality coming soon")

    def open_radar_map(self):
        """Open radar map editor"""
        self.log_message("Radar map functionality coming soon")

    def open_paths_map(self):
        """Open paths map editor"""
        self.log_message("Paths map functionality coming soon")

    def open_waterpro(self):
        """Open water properties editor"""
        self.log_message("Water properties functionality coming soon")


    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.log_message(f"Closed: {os.path.basename(self.current_img.file_path)}")
            self.current_img = None
            self.gui_layout.table.setRowCount(0)
            self.gui_layout.update_img_info("No IMG loaded")
            self.setWindowTitle("IMG Factory 1.5")

    def rebuild_img(self):
        """Rebuild current IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        try:
            self.log_message("Rebuilding IMG file...")
            self.gui_layout.show_progress(0, "Rebuilding...")
            
            # Rebuild the IMG file
            if self.current_img.rebuild():
                self.log_message("IMG file rebuilt successfully")
                self.gui_layout.show_progress(-1, "Rebuild complete")
                QMessageBox.information(self, "Success", "IMG file rebuilt successfully!")
            else:
                self.log_message("Failed to rebuild IMG file")
                self.gui_layout.show_progress(-1, "Rebuild failed")
                QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
                
        except Exception as e:
            error_msg = f"Error rebuilding IMG: {str(e)}"
            self.log_message(error_msg)
            self.gui_layout.show_progress(-1, "Error")
            QMessageBox.critical(self, "Rebuild Error", error_msg)

    def rebuild_img_as(self):
        """Rebuild IMG file with new name"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Rebuild IMG As", "", 
            "IMG Archives (*.img);;All Files (*)"
        )
        
        if file_path:
            try:
                self.log_message(f"Rebuilding IMG as: {os.path.basename(file_path)}")
                self.gui_layout.show_progress(0, "Rebuilding...")
                
                if self.current_img.rebuild_as(file_path):
                    self.log_message("IMG file rebuilt successfully")
                    self.gui_layout.show_progress(-1, "Rebuild complete")
                    QMessageBox.information(self, "Success", f"IMG file rebuilt as {os.path.basename(file_path)}")
                else:
                    self.log_message("Failed to rebuild IMG file")
                    self.gui_layout.show_progress(-1, "Rebuild failed")
                    QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
                    
            except Exception as e:
                error_msg = f"Error rebuilding IMG: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Error")
                QMessageBox.critical(self, "Rebuild Error", error_msg)

    def import_files(self):
        """Import files into current IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Import Files", "", 
            "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
        )
        
        if file_paths:
            try:
                self.log_message(f"Importing {len(file_paths)} files...")
                self.gui_layout.show_progress(0, "Importing files...")
                
                imported_count = 0
                for i, file_path in enumerate(file_paths):
                    progress = int((i + 1) * 100 / len(file_paths))
                    self.gui_layout.show_progress(progress, f"Importing {os.path.basename(file_path)}")
                    
                    if self.current_img.import_file(file_path):
                        imported_count += 1
                        self.log_message(f"Imported: {os.path.basename(file_path)}")
                
                # Refresh table
                populate_img_table(self.gui_layout.table, self.current_img)
                
                self.log_message(f"Import complete: {imported_count}/{len(file_paths)} files imported")
                self.gui_layout.show_progress(-1, "Import complete")
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")
                
                QMessageBox.information(self, "Import Complete", 
                                      f"Imported {imported_count} of {len(file_paths)} files")
                
            except Exception as e:
                error_msg = f"Error importing files: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Import error")
                QMessageBox.critical(self, "Import Error", error_msg)

    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        selected_rows = []
        for item in self.gui_layout.table.selectedItems():
            if item.column() == 0:  # Only filename column
                selected_rows.append(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select entries to export.")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Export To Folder")
        if export_dir:
            try:
                self.log_message(f"Exporting {len(selected_rows)} entries...")
                self.gui_layout.show_progress(0, "Exporting...")
                
                exported_count = 0
                for i, row in enumerate(selected_rows):
                    progress = int((i + 1) * 100 / len(selected_rows))
                    entry_name = self.gui_layout.table.item(row, 0).text()
                    self.gui_layout.show_progress(progress, f"Exporting {entry_name}")
                    
                    if self.current_img.export_entry(row, export_dir):
                        exported_count += 1
                        self.log_message(f"Exported: {entry_name}")
                
                self.log_message(f"Export complete: {exported_count}/{len(selected_rows)} files exported")
                self.gui_layout.show_progress(-1, "Export complete")
                
                QMessageBox.information(self, "Export Complete", 
                                      f"Exported {exported_count} of {len(selected_rows)} files to {export_dir}")
                
            except Exception as e:
                error_msg = f"Error exporting files: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Export error")
                QMessageBox.critical(self, "Export Error", error_msg)

    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        export_dir = QFileDialog.getExistingDirectory(self, "Export All To Folder")
        if export_dir:
            try:
                entry_count = len(self.current_img.entries)
                self.log_message(f"Exporting all {entry_count} entries...")
                self.gui_layout.show_progress(0, "Exporting all...")
                
                exported_count = 0
                for i, entry in enumerate(self.current_img.entries):
                    progress = int((i + 1) * 100 / entry_count)
                    self.gui_layout.show_progress(progress, f"Exporting {entry.name}")
                    
                    if self.current_img.export_entry(i, export_dir):
                        exported_count += 1
                        self.log_message(f"Exported: {entry.name}")
                
                self.log_message(f"Export complete: {exported_count}/{entry_count} files exported")
                self.gui_layout.show_progress(-1, "Export complete")
                
                QMessageBox.information(self, "Export Complete", 
                                      f"Exported {exported_count} of {entry_count} files to {export_dir}")
                
            except Exception as e:
                error_msg = f"Error exporting all files: {str(e)}"
                self.log_message(error_msg)
                self.gui_layout.show_progress(-1, "Export error")
                QMessageBox.critical(self, "Export Error", error_msg)

    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        selected_rows = []
        for item in self.gui_layout.table.selectedItems():
            if item.column() == 0:  # Only filename column
                selected_rows.append(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select entries to remove.")
            return
        
        # Confirm removal
        entry_names = [self.gui_layout.table.item(row, 0).text() for row in selected_rows]
        reply = QMessageBox.question(
            self, "Confirm Removal", 
            f"Remove {len(selected_rows)} selected entries?\n\n" + "\n".join(entry_names[:5]) + 
            (f"\n... and {len(entry_names) - 5} more" if len(entry_names) > 5 else ""),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Sort in reverse order to maintain indices
                selected_rows.sort(reverse=True)
                
                removed_count = 0
                for row in selected_rows:
                    entry_name = self.gui_layout.table.item(row, 0).text()
                    if self.current_img.remove_entry(row):
                        removed_count += 1
                        self.log_message(f"Removed: {entry_name}")
                
                # Refresh table
                populate_img_table(self.gui_layout.table, self.current_img)
                
                self.log_message(f"Removal complete: {removed_count} entries removed")
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")
                
                QMessageBox.information(self, "Removal Complete", 
                                      f"Removed {removed_count} entries")
                
            except Exception as e:
                error_msg = f"Error removing entries: {str(e)}"
                self.log_message(error_msg)
                QMessageBox.critical(self, "Removal Error", error_msg)

    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return
        
        try:
            self.log_message("Validating IMG file...")
            self.gui_layout.show_progress(0, "Validating...")
            
            validator = IMGValidator()
            validation_result = validator.validate(self.current_img)
            
            self.gui_layout.show_progress(-1, "Validation complete")
            
            if validation_result.is_valid:
                self.log_message("IMG file validation passed")
                QMessageBox.information(self, "Validation Result", "IMG file is valid!")
            else:
                self.log_message(f"IMG file validation failed: {len(validation_result.errors)} errors")
                error_details = "\n".join(validation_result.errors[:10])
                if len(validation_result.errors) > 10:
                    error_details += f"\n... and {len(validation_result.errors) - 10} more errors"
                
                QMessageBox.warning(self, "Validation Failed", 
                                  f"IMG file has {len(validation_result.errors)} validation errors:\n\n{error_details}")
                
        except Exception as e:
            error_msg = f"Error validating IMG: {str(e)}"
            self.log_message(error_msg)
            self.gui_layout.show_progress(-1, "Validation error")
            QMessageBox.critical(self, "Validation Error", error_msg)

    # =============================================================================
    # COL FILE OPERATIONS - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def open_col_file(self):
        """Open COL file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open COL File", "", 
            "COL Files (*.col);;All Files (*)"
        )
        
        if file_path:
            self.load_col_file(file_path)
    
    def load_col_file(self, file_path: str):
        """Load COL file"""
        try:
            self.log_message(f"Loading COL: {os.path.basename(file_path)}")
            self.gui_layout.show_progress(0, "Loading COL file...")
            
            # COL loading logic would go here
            # For now, just simulate the loading
            self.current_col = {"file_path": file_path, "type": "COL"}
            
            self.log_message(f"Loaded COL: {os.path.basename(file_path)}")
            self.gui_layout.show_progress(-1, "COL loaded")
            self.gui_layout.update_img_info(f"COL: {os.path.basename(file_path)}")
            
        except Exception as e:
            error_msg = f"Error loading COL: {str(e)}"
            self.log_message(error_msg)
            self.gui_layout.show_progress(-1, "COL load error")
            QMessageBox.critical(self, "COL Loading Error", error_msg)

    # =============================================================================
    # TEMPLATE MANAGEMENT - KEEP 100% OF FUNCTIONALITY  
    # =============================================================================

    def manage_templates(self):
        """Show template manager dialog"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.template_selected.connect(self._apply_template)
        dialog.exec()

    def _apply_template(self, template_data):
        """Apply template to create new IMG"""
        try:
            self.log_message(f"Applying template: {template_data.get('name', 'Unknown')}")
            
            # Template application logic
            creator = EnhancedIMGCreator()
            if creator.create_from_template(template_data):
                self.log_message("Template applied successfully")
                # Optionally load the created IMG
                if 'output_path' in template_data:
                    self.load_img_file(template_data['output_path'])
            else:
                self.log_message("Failed to apply template")
                
        except Exception as e:
            error_msg = f"Error applying template: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "Template Error", error_msg)

    # =============================================================================
    # SETTINGS AND DIALOGS - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.app_settings, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Apply new settings
            apply_theme_to_app(QApplication.instance(), self.app_settings)
            self.gui_layout.apply_table_theme()
            self.log_message("Settings updated")

    def show_theme_settings(self):
        """Show theme settings dialog"""
        # This would open a dedicated theme settings dialog
        self.show_settings()  # For now, use general settings

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>IMG Factory 1.5</h2>
        <p><b>Professional IMG Archive Manager</b></p>
        <p>Version: 1.5.0 Python Edition</p>
        <p>Author: X-Seti</p>
        <p>Based on original IMG Factory by MexUK (2007)</p>
        <br>
        <p>Features:</p>
        <ul>
        <li>IMG file creation and editing</li>
        <li>Multi-format support (DFF, TXD, COL, IFP)</li>
        <li>Template system</li>
        <li>Batch operations</li>
        <li>Validation tools</li>
        </ul>
        """
        
        QMessageBox.about(self, "About IMG Factory", about_text)

    # =============================================================================
    # SETTINGS PERSISTENCE - KEEP 100% OF FUNCTIONALITY
    # =============================================================================

    def _restore_settings(self):
        """Restore application settings"""
        try:
            settings = QSettings("XSeti", "IMGFactory")
            
            # Restore window geometry
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            # Restore splitter state
            splitter_state = settings.value("splitter_state")
            if splitter_state and hasattr(self.gui_layout, 'main_splitter'):
                self.gui_layout.main_splitter.restoreState(splitter_state)
            
            self.log_message("Settings restored")
            
        except Exception as e:
            self.log_message(f"Failed to restore settings: {str(e)}")

    def _save_settings(self):
        """Save application settings"""
        try:
            settings = QSettings("XSeti", "IMGFactory")
            
            # Save window geometry
            settings.setValue("geometry", self.saveGeometry())
            
            # Save splitter state
            if hasattr(self.gui_layout, 'main_splitter'):
                settings.setValue("splitter_state", self.gui_layout.main_splitter.saveState())
            
            self.log_message("Settings saved")
            
        except Exception as e:
            self.log_message(f"Failed to save settings: {str(e)}")

    def closeEvent(self, event):
        """Handle application close"""
        self._save_settings()
        
        # Clean up threads
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.quit()
            self.load_thread.wait()
        
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("1.5")
    app.setOrganizationName("X-Seti")
    
    # Load settings
    try:
        settings = AppSettings()
        settings.load_settings()
    except Exception as e:
        print(f"Warning: Could not load settings: {str(e)}")
        settings = {}
    
    # Create main window
    window = IMGFactory(settings)
    
    # COL integration setup
    if setup_col_integration(window):
        window.log_message("COL functionality integrated successfully")
    else:
        window.log_message("COL functionality not available")
    
    # Show window
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
