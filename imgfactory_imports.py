#this belongs in root /imgfactory.py - version 61
# X-Seti - June29 2025 - Img Factory 1.5
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""

import sys
import os
import mimetypes
from pathlib import Path
from typing import Optional, List, Dict, Any

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

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QMimeData
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap, QDragEnterEvent, QDropEvent, QContextMenuEvent

# Import components - consolidated to avoid duplicates
from app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog
from components.img_creator import NewIMGDialog
from components.img_core_classes import (
    IMGFile, IMGEntry, IMGVersion, format_file_size,
    IMGEntriesTable, FilterPanel, IMGFileInfoPanel, create_entries_table_panel,
    TabFilterWidget, integrate_filtering
)
from components.img_formats import GameSpecificIMGDialog, EnhancedIMGCreator
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
from components.img_validator import IMGValidator
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.menu import IMGFactoryMenuBar

# Optional COL integration
try:
    from imgfactory_col_integration import setup_col_integration
except ImportError:
    print("Warning: COL integration not available")
    def setup_col_integration(main_window):
        return False

print("Components imported successfully")


def populate_img_table(table: QTableWidget, img_file: IMGFile):
    """Populate table with IMG file entries - module level function"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return

    entries = img_file.entries

    # Clear existing data first
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        # Name
        table.setItem(row, 0, QTableWidgetItem(entry.name))

        # Type (file extension)
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


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # IMGFile object
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit(10)
            img_file = IMGFile(self.file_path)
            
            self.progress.emit(30)
            if not img_file.open():
                self.error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress.emit(100)
            self.finished.emit(img_file)
            
        except Exception as e:
            self.error.emit(f"Error loading IMG file: {str(e)}")


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
        self.menu_bar_system = IMGFactoryMenuBar(self)

        callbacks = {
            "about": self.show_about,
            "open_img": self.open_img_file,
            "new_img": self.create_new_img,
            "exit": self.close,
            "img_validate": self.validate_img,
            "customize_interface": self.show_gui_settings,
        }
        self.menu_bar_system.set_callbacks(callbacks)

        # Initialize UI
        self._create_ui()
        self._connect_signals()
        self._restore_settings()
        
        # Apply theme
        if hasattr(self.app_settings, 'themes'):
            apply_theme_to_app(QApplication.instance(), self.app_settings)
        
        # Apply COL integration after creating the main interface
        setup_col_integration(self)
        
        self.log_message("IMG Factory 1.5 initialized")

    def _create_ui(self):
        """Create the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - table and file info (using consolidated components)
        left_panel = create_entries_table_panel(self)
        splitter.addWidget(left_panel)
        
        # Right panel - buttons and controls
        right_panel = self.gui_layout.create_button_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([800, 400])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self):
        """Connect UI signals to methods"""
        # Table signals are connected in create_entries_table_panel
        pass

    def _restore_settings(self):
        """Restore application settings"""
        if hasattr(self.app_settings, 'restore_window_state'):
            self.app_settings.restore_window_state(self)

    def log_message(self, message: str):
        """Log message to status bar and console"""
        print(f"[IMG Factory] {message}")
        self.status_bar.showMessage(message)

    def log_error(self, message: str):
        """Log error message"""
        print(f"[ERROR] {message}")
        self.status_bar.showMessage(f"Error: {message}")

    def open_img_file(self):
        """Open IMG file dialog"""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Open IMG Archive",
            "",
            "IMG Archives (*.img);;All Files (*)"
        )
        
        if file_path:
            self._load_img_file(file_path)

    def _load_img_file(self, file_path: str):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.quit()
            self.load_thread.wait()
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress.connect(self._on_load_progress)
        self.load_thread.finished.connect(self._on_img_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.start()

    def _on_load_progress(self, progress: int):
        """Handle loading progress updates"""
        self.status_bar.showMessage(f"Loading... {progress}%")

    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        self.current_img = img_file
        self.log_message(f"Loaded: {img_file.file_path} ({len(img_file.entries)} entries)")

        # Update table using consolidated component
        if hasattr(self, 'entries_table'):
            self.entries_table.populate_entries(img_file.entries)

        # Update file info panel
        if hasattr(self, 'file_info_panel'):
            self.file_info_panel.update_info(img_file)

        # Update window title
        self.setWindowTitle(f"IMG Factory 1.5 - {os.path.basename(img_file.file_path)}")

    def _on_load_error(self, error_message: str):
        """Handle loading errors"""
        self.log_error(error_message)
        QMessageBox.critical(self, "Loading Error", error_message)

    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.log_message("New IMG creation requested")

    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            QMessageBox.information(self, "Info", "No IMG file loaded to validate")
            return
        
        validator = IMGValidator()
        result = validator.validate_img_file(self.current_img)
        
        if result.is_valid:
            QMessageBox.information(self, "Validation", "IMG file is valid!")
        else:
            error_text = "\n".join(result.errors)
            QMessageBox.warning(self, "Validation Errors", f"Validation failed:\n{error_text}")

    def show_gui_settings(self):
        """Show GUI settings dialog"""
        dialog = SettingsDialog(self.app_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            apply_theme_to_app(QApplication.instance(), self.app_settings)

    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>IMG Factory 1.5</h2>
<p>Modern IMG archive manager for GTA and related games</p>

<h3>Features:</h3>
<ul>
<li>Support for IMG v1, v2, and v3 formats</li>
<li>Advanced file filtering and search</li>
<li>COL collision file integration</li>
<li>Multiple theme support</li>
<li>Template system for quick creation</li>
</ul>

<p><b>Version:</b> 1.5<br>
<b>Build:</b> June 29, 2025<br>
<b>Original:</b> MexUK 2007 IMG Factory 1.2</p>
        """
        
        QMessageBox.about(self, "About IMG Factory", about_text)

    def on_entries_selected(self, selected_indices: List[int]):
        """Handle table selection changes"""
        count = len(selected_indices)
        if count > 0:
            self.status_bar.showMessage(f"{count} entries selected")
        else:
            self.status_bar.showMessage("Ready")

    def on_entry_double_clicked(self, row_index: int):
        """Handle entry double-click"""
        if hasattr(self, 'entries_table') and self.current_img:
            name_item = self.entries_table.item(row_index, 0)
            if name_item:
                entry_name = name_item.text()
                self.log_message(f"Double-clicked entry: {entry_name}")

    def closeEvent(self, event):
        """Handle application close"""
        if hasattr(self.app_settings, 'save_window_state'):
            self.app_settings.save_window_state(self)
        
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
    settings = AppSettings()
    
    # Create main window
    window = IMGFactory(settings)
    window.show()
    
    # Apply theme
    apply_theme_to_app(app, settings)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
    