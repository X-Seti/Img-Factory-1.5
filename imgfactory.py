#this belongs in root /imgfactory.py - Version: 62
# X-Seti - July13 2025 - Img Factory 1.5 - Main Application Entry Point
# Credit MexUK 2007 Img Factory 1.2

#!/usr/bin/env python3
"""
IMG Factory 1.5 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""

import sys
import os
import mimetypes
from typing import Optional, List, Dict, Any
from pathlib import Path

print("Starting IMG Factory 1.5...")

# Setup paths FIRST - before any other imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
components_dir = current_dir / "components"
gui_dir = current_dir / "gui"
utils_dir = current_dir / "utils"

# Add directories to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if components_dir.exists() and str(components_dir) not in sys.path:
    sys.path.insert(0, str(components_dir))
if gui_dir.exists() and str(gui_dir) not in sys.path:
    sys.path.insert(0, str(gui_dir))
if utils_dir.exists() and str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "components"))
sys.path.insert(0, str(current_dir / "gui"))
sys.path.insert(0, str(current_dir / "utils"))

print("Importing PyQt6 components...")
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QDialog,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGridLayout, QMenu, QButtonGroup, QRadioButton, QToolBar, QFormLayout
)
from PyQt6.QtCore import pyqtSignal, QMimeData, Qt, QThread, QTimer, QSettings
from PyQt6.QtGui import QAction, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFont, QIcon, QPixmap, QShortcut

print("Importing IMG Factory modules...")
# Core settings and theme system
from utils.app_settings_system import AppSettings, apply_theme_to_app, SettingsDialog

# Core IMG components
from components.img_core_classes import (
    IMGFile, IMGEntry, IMGVersion, Platform, format_file_size,
    IMGEntriesTable, FilterPanel, IMGFileInfoPanel,
    TabFilterWidget, integrate_filtering, create_entries_table_panel
)

# IMG functionality modules
from components.img_creator import GameType, NewIMGDialog, IMGCreationThread
from components.img_close_functions import install_close_functions, setup_close_manager
from components.img_formats import GameSpecificIMGDialog, IMGCreator
from components.img_templates import IMGTemplateManager, TemplateManagerDialog
from components.img_validator import IMGValidator
from components.img_import_export_functions import integrate_clean_import_export
from components.unified_debug_functions import integrate_all_improvements
from components.file_extraction_functions import setup_complete_extraction_integration

# GUI layout and theme
from gui.gui_layout import IMGFactoryGUILayout
from gui.pastel_button_theme import apply_pastel_theme_to_buttons
from gui.menu import IMGFactoryMenuBar

# COL integration setup
print("Setting up COL integration...")
COL_INTEGRATION_AVAILABLE = False
COL_SETUP_FUNCTION = None

try:
    from components.col_debug_control import COLDebugController
    from components.col_main_integration import setup_col_integration

    COL_INTEGRATION_AVAILABLE = True
    COL_SETUP_FUNCTION = setup_col_integration
    print("✅ COL integration available")
except ImportError as e:
    print(f"⚠️ COL integration not available: {e}")

_theme_loading_guard = False

def safe_apply_theme_to_app(app_settings, app_or_widget):
    """Safe theme application that prevents loops"""
    global _theme_loading_guard

    if _theme_loading_guard:
        print("⚠️ Theme loading loop detected - skipping")
        return

    try:
        _theme_loading_guard = True

        if hasattr(app_settings, 'get_stylesheet'):
            stylesheet = app_settings.get_stylesheet()
        else:
            stylesheet = "QMainWindow { background-color: #f0f0f0; color: #000000; }"

        if hasattr(app_or_widget, 'setStyleSheet'):
            app_or_widget.setStyleSheet(stylesheet)
            print("✅ Theme applied safely")

    except Exception as e:
        print(f"❌ Theme application error: {e}")
    finally:
        _theme_loading_guard = False


def populate_img_table(table: QTableWidget, img_file: IMGFile):
    """Populate table with IMG file entries - FIXED VERSION"""
    if not img_file or not img_file.entries:
        table.setRowCount(0)
        return

    entries = img_file.entries
    print(f"Populating table with {len(entries)} entries")

    # Clear existing data first
    table.setRowCount(0)
    table.setRowCount(len(entries))

    for row, entry in enumerate(entries):
        # Name
        table.setItem(row, 0, QTableWidgetItem(entry.name))

        # Type (file extension) - Use name-based detection
        if '.' in entry.name:
            file_type = entry.name.split('.')[-1].upper()
        else:
            file_type = "UNKNOWN"
        table.setItem(row, 1, QTableWidgetItem(file_type))

        # Size (formatted)
        size_str = format_file_size(entry.size)
        table.setItem(row, 2, QTableWidgetItem(size_str))

        # Offset (hex format)
        offset_str = f"0x{entry.offset:08X}"
        table.setItem(row, 3, QTableWidgetItem(offset_str))

    print(f"✅ Table populated with {len(entries)} entries")


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    load_complete = pyqtSignal(IMGFile)
    load_error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """Load IMG file in background"""
        try:
            self.status_update.emit(f"Loading {os.path.basename(self.file_path)}...")
            self.progress_update.emit(10)

            img_file = IMGFile()
            self.progress_update.emit(30)

            if img_file.load_from_file(self.file_path):
                self.progress_update.emit(100)
                self.status_update.emit("Loading complete")
                self.load_complete.emit(img_file)
            else:
                self.load_error.emit("Failed to load IMG file")

        except Exception as e:
            self.load_error.emit(f"Error loading IMG file: {str(e)}")


class IMGFactoryMainWindow(QMainWindow):
    """Main window class for IMG Factory 1.5"""

    def __init__(self):
        super().__init__()
        print("Initializing IMG Factory Main Window...")

        # Window setup
        self.setWindowTitle("IMG Factory 1.5")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Application settings
        self.app_settings = AppSettings()

        # Template manager setup
        try:
            self.template_manager = IMGTemplateManager()
        except Exception as e:
            print(f"Template manager error: {e}")
            # Fallback template manager
            class DummyTemplateManager:
                def get_user_templates(self): 
                    return []
            self.template_manager = DummyTemplateManager()

        # Core data
        self.current_img: Optional[IMGFile] = None
        self.current_col: Optional = None  # For COL file support
        self.open_files = {}  # Dict to store open files {tab_index: file_info}
        self.tab_counter = 0  # Counter for unique tab IDs

        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None

        # Initialize GUI layout
        print("Setting up GUI layout...")
        self.gui_layout = IMGFactoryGUILayout(self)

        # Setup menu bar system
        print("Setting up menu system...")
        self.menu_bar_system = IMGFactoryMenuBar(self)

        # Setup menu callbacks - Use working methods
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
        print("Creating UI components...")
        self._create_ui()
        
        # Restore settings
        print("Restoring settings...")
        self._restore_settings()

        # Setup integrations
        print("Setting up integrations...")
        self._setup_integrations()

        print("✅ IMG Factory initialization complete")

    def _setup_integrations(self):
        """Setup all system integrations"""
        try:
            # Close manager for tab handling
            install_close_functions(self)
            
            # Import/export integration
            integrate_clean_import_export(self)
            
            # Debug and improvements integration
            integrate_all_improvements(self)
            
            # File extraction integration
            setup_complete_extraction_integration(self)
            
            # COL integration (if available)
            if COL_INTEGRATION_AVAILABLE and COL_SETUP_FUNCTION:
                print("Setting up COL integration...")
                try:
                    COL_SETUP_FUNCTION(self)
                    print("✅ COL integration complete")
                except Exception as e:
                    print(f"⚠️ COL integration failed: {e}")
            
            print("✅ All integrations complete")
            
        except Exception as e:
            print(f"❌ Integration error: {e}")

    def _create_ui(self):
        """Create the main user interface"""
        # Set up the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main horizontal splitter
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # Create the main splitter (horizontal)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Left panel setup
        self._create_left_panel()

        # Right panel setup  
        self._create_right_panel()

        # Status bar
        self._create_status_bar()

        # Set splitter proportions
        self.main_splitter.setSizes([800, 400])  # Left panel wider

    def _create_left_panel(self):
        """Create the left panel with table and log"""
        # Create left widget with vertical splitter
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter for table and log
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_layout.addWidget(left_splitter)

        # Table section
        table_group = QGroupBox("IMG Contents")
        table_layout = QVBoxLayout(table_group)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Offset"])
        
        # Table configuration
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size  
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        
        table_layout.addWidget(self.table)
        left_splitter.addWidget(table_group)

        # Log section
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)

        self.log = QTextEdit()
        self.log.setMaximumHeight(200)
        self.log.setReadOnly(True)
        log_layout.addWidget(self.log)
        left_splitter.addWidget(log_group)

        # Set splitter proportions (table larger than log)
        left_splitter.setSizes([600, 200])

        # Add to main splitter
        self.main_splitter.addWidget(left_widget)

        # Connect table selection
        self.table.itemSelectionChanged.connect(self._on_table_selection_changed)

    def _create_right_panel(self):
        """Create the right panel with buttons"""
        # Import the button creation from gui_layout
        try:
            from gui.panel_controls import create_right_panel_with_pastel_buttons
            right_panel = create_right_panel_with_pastel_buttons(self)
            self.main_splitter.addWidget(right_panel)
        except ImportError:
            # Fallback simple button panel
            self._create_simple_right_panel()

    def _create_simple_right_panel(self):
        """Create a simple right panel if advanced one fails"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # IMG Operations group
        img_group = QGroupBox("IMG Operations")
        img_layout = QGridLayout(img_group)

        # Basic buttons
        buttons = [
            ("New", self.create_new_img),
            ("Open", self.open_img_file),
            ("Close", self.close_img_file),
            ("Rebuild", self.rebuild_img)
        ]

        for i, (text, callback) in enumerate(buttons):
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            img_layout.addWidget(btn, i // 2, i % 2)

        right_layout.addWidget(img_group)
        right_layout.addStretch()

        self.main_splitter.addWidget(right_widget)

    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.statusBar()
        
        # Main status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addWidget(self.progress_bar)

        # IMG info label
        self.img_info_label = QLabel()
        self.status_bar.addPermanentWidget(self.img_info_label)

    def _restore_settings(self):
        """Restore application settings"""
        try:
            # Apply theme
            apply_theme_to_app(self.app_settings, self)
            
            # Restore window geometry
            settings = QSettings("IMGFactory", "IMGFactory1.5")
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
                
            # Restore splitter state
            splitter_state = settings.value("splitter_state")
            if splitter_state and hasattr(self, 'main_splitter'):
                self.main_splitter.restoreState(splitter_state)
                
        except Exception as e:
            print(f"Settings restore error: {e}")

    def _save_settings(self):
        """Save application settings"""
        try:
            settings = QSettings("IMGFactory", "IMGFactory1.5")
            settings.setValue("geometry", self.saveGeometry())
            
            if hasattr(self, 'main_splitter'):
                settings.setValue("splitter_state", self.main_splitter.saveState())
                
        except Exception as e:
            print(f"Settings save error: {e}")

    def closeEvent(self, event):
        """Handle application close event"""
        self._save_settings()
        event.accept()

    # Drag and Drop Support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.img', '.col')):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.img'):
                    self.open_img_file(file_path)
                    break
                elif file_path.lower().endswith('.col'):
                    self.open_col_file(file_path)
                    break

    # Core IMG File Operations
    def open_img_file(self, file_path: str = None):
        """Open an IMG file"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open IMG File",
                "",
                "IMG Files (*.img);;All Files (*)"
            )
            
        if not file_path:
            return

        try:
            self.log_message(f"Opening IMG file: {os.path.basename(file_path)}")
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Load in background thread
            self.load_thread = IMGLoadThread(file_path)
            self.load_thread.progress_update.connect(self.progress_bar.setValue)
            self.load_thread.status_update.connect(self.status_label.setText)
            self.load_thread.load_complete.connect(self._on_img_loaded)
            self.load_thread.load_error.connect(self._on_img_load_error)
            self.load_thread.start()
            
        except Exception as e:
            self.log_message(f"Error opening IMG file: {str(e)}")
            self.progress_bar.setVisible(False)

    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG file loading"""
        try:
            self.current_img = img_file
            self.current_col = None  # Clear COL when IMG is loaded
            
            # Populate table
            populate_img_table(self.table, img_file)
            
            # Update status
            entry_count = len(img_file.entries) if img_file.entries else 0
            total_size = sum(entry.size for entry in img_file.entries) if img_file.entries else 0
            size_str = format_file_size(total_size)
            
            self.img_info_label.setText(f"IMG: {entry_count} entries, {size_str}")
            self.status_label.setText(f"Loaded {os.path.basename(img_file.file_path)}")
            
            # Update button states
            self._update_button_states(False)
            
            self.log_message(f"✅ IMG file loaded: {entry_count} entries, {size_str}")
            
        except Exception as e:
            self.log_message(f"Error processing loaded IMG: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def _on_img_load_error(self, error_message: str):
        """Handle IMG file loading errors"""
        self.log_message(f"❌ {error_message}")
        self.status_label.setText("Ready")
        self.progress_bar.setVisible(False)

    def close_img_file(self):
        """Close the current IMG file"""
        if self.current_img:
            self.current_img = None
            self.table.setRowCount(0)
            self.img_info_label.setText("")
            self.status_label.setText("Ready")
            self._update_button_states(False)
            self.log_message("IMG file closed")

    def create_new_img(self):
        """Create a new IMG file"""
        try:
            dialog = NewIMGDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Get dialog results
                results = dialog.get_results()
                self.log_message(f"Creating new IMG file: {results.get('name', 'unnamed')}")
                
                # TODO: Implement IMG creation logic
                self.log_message("IMG creation not yet implemented")
                
        except Exception as e:
            self.log_message(f"Error creating new IMG: {str(e)}")

    def rebuild_img(self):
        """Rebuild the current IMG file"""
        if not self.current_img:
            self.log_message("No IMG file loaded")
            return
            
        try:
            self.log_message("Rebuilding IMG file...")
            # TODO: Implement rebuild logic
            self.log_message("Rebuild not yet implemented")
            
        except Exception as e:
            self.log_message(f"Error rebuilding IMG: {str(e)}")

    def validate_img(self):
        """Validate the current IMG file"""
        if not self.current_img:
            self.log_message("No IMG file loaded")
            return
            
        try:
            validator = IMGValidator()
            result = validator.validate_img_file(self.current_img)
            
            if result.is_valid:
                self.log_message("✅ IMG file validation passed")
            else:
                self.log_message(f"❌ IMG file validation failed: {result.error_message}")
                
        except Exception as e:
            self.log_message(f"Error validating IMG: {str(e)}")

    # COL File Operations
    def open_col_file(self, file_path: str = None):
        """Open a COL file"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open COL File", 
                "",
                "COL Files (*.col);;All Files (*)"
            )
            
        if not file_path:
            return

        try:
            self.log_message(f"Opening COL file: {os.path.basename(file_path)}")
            
            if COL_INTEGRATION_AVAILABLE:
                # Use COL integration if available
                # TODO: Implement COL opening logic
                self.log_message("COL file opening not yet implemented")
            else:
                self.log_message("COL support not available")
                
        except Exception as e:
            self.log_message(f"Error opening COL file: {str(e)}")

    # Table Events
    def _on_table_selection_changed(self):
        """Handle table selection changes"""
        selected_items = self.table.selectedItems()
        selection_count = len(selected_items) // 4  # 4 columns per row
        
        if selection_count == 1:
            # Single selection - show entry details
            current_row = self.table.currentRow()
            if current_row >= 0:
                name_item = self.table.item(current_row, 0)
                if name_item:
                    self.log_message(f"Selected: {name_item.text()}")
        elif selection_count > 1:
            self.log_message(f"Selected {selection_count} entries")

        # Update button states
        has_selection = selection_count > 0
        self._update_button_states(has_selection)

    def _update_button_states(self, has_selection):
        """Update button enabled/disabled states based on selection"""
        # Enable/disable buttons based on selection and loaded IMG
        has_img = self.current_img is not None
        has_col = self.current_col is not None

        # Find buttons in GUI layout and update their states
        selection_dependent_buttons = [
            'export_btn', 'export_selected_btn', 'remove_btn', 'remove_selected_btn',
            'extract_btn', 'quick_export_btn'
        ]

        for btn_name in selection_dependent_buttons:
            if hasattr(self.gui_layout, btn_name):
                button = getattr(self.gui_layout, btn_name)
                if hasattr(button, 'setEnabled'):
                    # Enable for IMG files with selection, disable for COL files
                    button.setEnabled(has_selection and has_img and not has_col)

        # These buttons only need an IMG (no selection required) - DISABLE for COL
        img_dependent_buttons = [
            'import_btn', 'import_files_btn', 'rebuild_btn', 'close_btn',
            'validate_btn', 'refresh_btn'
        ]

        for btn_name in img_dependent_buttons:
            if hasattr(self.gui_layout, btn_name):
                button = getattr(self.gui_layout, btn_name)
                if hasattr(button, 'setEnabled'):
                    # Enable only for IMG files, not COL files
                    button.setEnabled(has_img and not has_col)

    # Utility Methods
    def log_message(self, message: str):
        """Add a message to the log panel"""
        if hasattr(self, 'log') and self.log:
            self.log.append(f"[{self._get_timestamp()}] {message}")
            # Auto-scroll to bottom
            scrollbar = self.log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _get_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    # Dialog Methods
    def show_about(self):
        """Show about dialog"""
        try:
            from gui.dialogs import show_about_dialog
            show_about_dialog(self)
        except ImportError:
            QMessageBox.about(self, "About IMG Factory", 
                            "IMG Factory 1.5\nIMG archive management tool")

    def show_gui_settings(self):
        """Show GUI settings dialog"""
        try:
            settings_dialog = SettingsDialog(self.app_settings, self)
            if settings_dialog.exec() == QDialog.DialogCode.Accepted:
                # Apply new theme
                apply_theme_to_app(self.app_settings, self)
                self.log_message("Settings applied")
        except Exception as e:
            self.log_message(f"Settings dialog error: {str(e)}")

    # Debug and Development Methods
    def enable_col_debug(self):
        """Enable COL debug output"""
        try:
            # Set debug flag on current COL file if loaded
            if hasattr(self, 'current_col') and self.current_col:
                self.current_col._debug_enabled = True

            # Set global flag for future COL files
            try:
                import components.col_core_classes as col_module
                col_module._global_debug_enabled = True
            except ImportError:
                pass  # COL module not available

            # Enable debug on COL debug controller if available
            if hasattr(self, 'col_debug_controller'):
                self.col_debug_controller.enable_debug()

            self.log_message("🔊 COL debug output enabled")

        except Exception as e:
            self.log_message(f"❌ COL debug enable error: {e}")

    def disable_col_debug(self):
        """Disable COL debug output"""
        try:
            # Set debug flag on current COL file if loaded
            if hasattr(self, 'current_col') and self.current_col:
                self.current_col._debug_enabled = False

            # Set global flag for future COL files
            try:
                import components.col_core_classes as col_module
                col_module._global_debug_enabled = False
            except ImportError:
                pass  # COL module not available

            # Disable debug on COL debug controller if available
            if hasattr(self, 'col_debug_controller'):
                self.col_debug_controller.disable_debug()

            self.log_message("🔇 COL debug output disabled")

        except Exception as e:
            self.log_message(f"❌ COL debug disable error: {e}")

    def toggle_col_debug(self):
        """Toggle COL debug output"""
        try:
            # Check current debug state
            debug_enabled = False
            try:
                import components.col_core_classes as col_module
                debug_enabled = getattr(col_module, '_global_debug_enabled', False)
            except ImportError:
                pass

            # Toggle debug state
            if debug_enabled:
                self.disable_col_debug()
            else:
                self.enable_col_debug()

        except Exception as e:
            self.log_message(f"❌ Debug toggle error: {e}")

    def setup_debug_controls(self):
        """Setup debug control shortcuts and initial state"""
        try:
            from PyQt6.QtGui import QShortcut, QKeySequence

            # Ctrl+Shift+D for debug toggle
            debug_shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
            debug_shortcut.activated.connect(self.toggle_col_debug)

            # Start with debug disabled for performance
            self.disable_col_debug()

            self.log_message("✅ Debug controls ready (Ctrl+Shift+D to toggle COL debug)")

        except Exception as e:
            self.log_message(f"❌ Debug controls setup error: {e}")

    def setup_search_functionality(self):
        """Setup search functionality for the table"""
        try:
            # Add search capabilities to the table if not already present
            if hasattr(self, 'table') and self.table:
                # Basic search functionality - could be enhanced later
                self.log_message("✅ Search functionality ready")
            
        except Exception as e:
            self.log_message(f"❌ Search setup error: {e}")

    def apply_search_and_performance_fixes(self):
        """Apply simple fixes without complex dependencies"""
        try:
            self.log_message("🔧 Applying performance and search fixes...")

            # 1. Simple COL debug control
            try:
                # Start with debug disabled for performance
                try:
                    import components.col_core_classes as col_module
                    col_module._global_debug_enabled = False
                except ImportError:
                    pass

                self.log_message("✅ COL performance mode enabled (debug disabled)")

            except Exception as e:
                self.log_message(f"⚠️ COL performance setup issue: {e}")

            # 2. Setup debug controls
            self.setup_debug_controls()

            # 3. Setup search functionality
            self.setup_search_functionality()

            self.log_message("✅ Performance and search fixes applied")

        except Exception as e:
            self.log_message(f"❌ Fixes application error: {e}")

    def setup_search_functionality(self):
        """Setup search box functionality"""
        try:
            # Find the search input widget
            search_input = None

            # Try different possible locations
            if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'search_input'):
                search_input = self.gui_layout.search_input
            elif hasattr(self, 'filter_input'):
                search_input = self.filter_input
            elif hasattr(self.gui_layout, 'filter_input'):
                search_input = self.gui_layout.filter_input

            if search_input:
                # Connect search functionality
                search_input.textChanged.connect(self.perform_search)
                self.log_message("✅ Search functionality connected")
            else:
                self.log_message("⚠️ Search input not found")

        except Exception as e:
            self.log_message(f"❌ Search setup error: {str(e)}")

    def perform_search(self, search_text=None, options=None):
        """Perform search on current IMG entries"""
        try:
            if not self.current_img or not self.current_img.entries:
                return

            # Get search parameters
            if search_text is None:
                if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'search_input'):
                    search_text = self.gui_layout.search_input.text()
                else:
                    return

            if not search_text.strip():
                return

            # Default search options
            if options is None:
                options = {
                    'case_sensitive': False,
                    'whole_word': False,
                    'regex': False,
                    'file_type': 'All Files'
                }

            # Convert to lowercase if not case sensitive
            if not options.get('case_sensitive', False):
                search_text = search_text.lower()

            # Find matches
            matches = []
            for i, entry in enumerate(self.current_img.entries):
                entry_name = entry.name
                if not options.get('case_sensitive', False):
                    entry_name = entry_name.lower()

                # File type filter
                file_type = options.get('file_type', 'All Files')
                if file_type != 'All Files':
                    entry_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else ''
                    type_mapping = {
                        'Models (DFF)': 'DFF',
                        'Textures (TXD)': 'TXD',
                        'Collision (COL)': 'COL',
                        'Animation (IFP)': 'IFP',
                        'Audio (WAV)': 'WAV',
                        'Scripts (SCM)': 'SCM'
                    }
                    if file_type in type_mapping and entry_ext != type_mapping[file_type]:
                        continue

                # Check if matches
                if options.get('whole_word', False):
                    import re
                    pattern = r'\b' + re.escape(search_text) + r'\b'
                    if re.search(pattern, entry_name):
                        matches.append(i)
                elif options.get('regex', False):
                    import re
                    try:
                        if re.search(search_text, entry_name):
                            matches.append(i)
                    except re.error:
                        self.log_message("Invalid regular expression")
                        return
                else:
                    # Simple text search
                    if search_text in entry_name:
                        matches.append(i)

            # Select matching entries in table
            if matches:
                table = self.gui_layout.table
                table.clearSelection()
                for row in matches:
                    if row < table.rowCount():
                        table.selectRow(row)

                # Scroll to first match
                table.scrollToItem(table.item(matches[0], 0))

                self.log_message(f"🔍 Found {len(matches)} matches for '{search_text}'")
            else:
                self.log_message(f"🔍 No matches found for '{search_text}'")

        except Exception as e:
            self.log_message(f"❌ Search error: {str(e)}")

    def _create_initial_tab(self):
        """Create initial empty tab"""
        # Create tab widget
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create GUI layout for this tab
        self.gui_layout.create_main_ui_with_splitters(tab_layout)

        # Add tab with "No file" label
        self.main_tab_widget.addTab(tab_widget, "📁 No File")

    def _on_tab_changed(self, index):
        """Handle tab change"""
        if index == -1:
            return

        self.log_message(f"🔄 Tab changed to: {index}")

        # Update current file based on tab
        if index in self.open_files:
            file_info = self.open_files[index]
            self.log_message(f"📂 Tab {index} has file: {file_info.get('file_path', 'Unknown')}")

            if file_info['type'] == 'IMG':
                self.current_img = file_info['file_object']
                self.current_col = None
            elif file_info['type'] == 'COL':
                self.current_col = file_info['file_object']
                self.current_img = None

            # Update UI for current file
            self._update_ui_for_current_file()
        else:
            # No file in this tab
            self.log_message(f"📭 Tab {index} is empty")
            self.current_img = None
            self.current_col = None
            self._update_ui_for_no_img()

    def _update_ui_for_current_file(self):
        """Update UI for currently selected file"""
        if self.current_img:
            self.log_message("🔄 Updating UI for IMG file")
            self._update_ui_for_loaded_img()
        elif self.current_col:
            self.log_message("🔄 Updating UI for COL file")
            self._update_ui_for_loaded_col()
        else:
            self.log_message("🔄 Updating UI for no file")
            self._update_ui_for_no_img()

    def _update_ui_for_loaded_img(self):
        """Update UI when IMG file is loaded"""
        if not self.current_img:
            self.log_message("⚠️ _update_ui_for_loaded_img called but no current_img")
            return

        # Update window title
        file_name = os.path.basename(self.current_img.file_path)
        self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Populate table with IMG entries
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            self._populate_real_img_table(self.current_img)
            self.log_message(f"📋 Table populated with {len(self.current_img.entries)} entries")
        else:
            self.log_message("⚠️ GUI layout or table not available")

        # Update status
        if hasattr(self, 'gui_layout'):
            entry_count = len(self.current_img.entries) if self.current_img.entries else 0
            self.gui_layout.show_progress(-1, f"Loaded: {entry_count} entries")

            if hasattr(self.gui_layout, 'update_img_info'):
                self.gui_layout.update_img_info(f"IMG: {file_name}")

        self.log_message("✅ IMG UI updated successfully")

    def _populate_real_img_table(self, img_file):
        """Populate table with real IMG data - HELPER method"""
        try:
            populate_img_table(self.gui_layout.table, img_file)
        except Exception as e:
            self.log_message(f"❌ Error populating table: {str(e)}")

    def _update_ui_for_loaded_col(self):
        """Update UI when COL file is loaded"""
        if not self.current_col:
            self.log_message("⚠️ _update_ui_for_loaded_col called but no current_col")
            return

        try:
            # Update window title
            file_name = os.path.basename(self.current_col.file_path)
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name} (COL)")

            # Apply COL-specific styling if available
            if hasattr(self, '_apply_individual_col_tab_style'):
                current_index = self.main_tab_widget.currentIndex()
                self._apply_individual_col_tab_style(current_index)

            # Update status for COL
            model_count = len(self.current_col.models) if hasattr(self.current_col, 'models') and self.current_col.models else 0
            if hasattr(self, 'gui_layout'):
                self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

            self.log_message(f"✅ COL UI updated: {file_name} ({model_count} models)")

        except Exception as e:
            self.log_message(f"❌ Error updating COL UI: {str(e)}")

    def _update_ui_for_no_img(self):
        """Update UI when no file is loaded"""
        # Clear table
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
            self.gui_layout.table.setRowCount(0)

        # Reset window title
        self.setWindowTitle("IMG Factory 1.5")

        # Clear status
        if hasattr(self, 'gui_layout'):
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "No file loaded")
            if hasattr(self.gui_layout, 'update_img_info'):
                self.gui_layout.update_img_info("")

        self.log_message("📭 UI cleared - no file loaded")

    def handle_action(self, action_name):
        """Handle unified action signals"""
        try:
            action_map = {
                # File operations
                'open_img_file': self.open_img_file,
                'close_img_file': self.close_img_file,
                'close_all': self.close_manager.close_all_tabs if hasattr(self, 'close_manager') else lambda: self.log_message("Close manager not available"),
                'close_all_img': self.close_all_img,
                'create_new_img': self.create_new_img,
                'refresh_table': self.refresh_table,

                # Entry operations
                'import_files': self.import_files,
                'export_selected': self.export_selected,
                'remove_selected': self.remove_selected,
                'select_all_entries': self.select_all_entries,

                # IMG operations
                'rebuild_img': self.rebuild_img,
                'rebuild_img_as': self.rebuild_img_as,
                'rebuild_all_img': self.rebuild_all_img,
                'merge_img': self.merge_img,
                'split_img': self.split_img,
                'convert_img_format': self.convert_img_format,

                # System
                'show_search_dialog': self.show_search_dialog,
            }

            if action_name in action_map:
                self.log_message(f"🎯 Action: {action_name}")
                action_map[action_name]()
            else:
                self.log_message(f"❌ Unknown action: {action_name}")

        except Exception as e:
            self.log_message(f"❌ Action error ({action_name}): {str(e)}")

    def setup_unified_signals(self):
        """Setup unified signal handler for all table interactions"""
        try:
            from components.unified_signal_handler import connect_table_signals

            # Connect main entries table to unified system
            success = connect_table_signals(
                table_name="main_entries",
                table_widget=self.gui_layout.table,
                parent_instance=self,
                selection_callback=self._unified_selection_handler,
                double_click_callback=self._unified_double_click_handler
            )

            if success:
                self.log_message("✅ Unified signal system connected")
            else:
                self.log_message("❌ Failed to connect unified signals")

            # Connect unified signals to status bar updates
            from components.unified_signal_handler import signal_handler
            signal_handler.status_update_requested.connect(self._update_status_from_signal)

        except Exception as e:
            self.log_message(f"❌ Unified signals setup error: {str(e)}")

    def _unified_selection_handler(self, selected_rows, selection_count):
        """Handle unified selection events"""
        try:
            if selection_count == 1:
                # Single selection - show details
                if selected_rows and len(selected_rows) > 0:
                    row = selected_rows[0]
                    if hasattr(self.gui_layout, 'table') and row < self.gui_layout.table.rowCount():
                        name_item = self.gui_layout.table.item(row, 0)
                        if name_item:
                            self.log_message(f"Selected: {name_item.text()}")
            elif selection_count > 1:
                self.log_message(f"Selected {selection_count} entries")

            # Update button states
            self._update_button_states(selection_count > 0)

        except Exception as e:
            self.log_message(f"❌ Selection handler error: {str(e)}")

    def _unified_double_click_handler(self, row, column):
        """Handle unified double-click events"""
        try:
            if self.current_img:
                # IMG file double-click handling
                if hasattr(self.gui_layout, 'table') and row < self.gui_layout.table.rowCount():
                    name_item = self.gui_layout.table.item(row, 0)
                    if name_item:
                        entry_name = name_item.text()
                        self.log_message(f"Double-clicked IMG entry: {entry_name}")
                        # TODO: Implement IMG entry preview/details
            elif self.current_col:
                # COL file double-click handling
                self._handle_col_table_double_click_img_style(row)

        except Exception as e:
            self.log_message(f"❌ Double-click handler error: {str(e)}")

    def _handle_col_table_double_click_img_style(self, row):
        """Handle double-click on COL table item - IMG style"""
        try:
            if hasattr(self, 'current_col') and hasattr(self.current_col, 'models'):
                self.show_col_model_details_img_style(row)
            else:
                self.log_message("No COL models available for details")
        except Exception as e:
            self.log_message(f"❌ Error handling COL table double-click: {str(e)}")

    def show_col_model_details_img_style(self, model_index):
        """Show COL model details in IMG Factory style"""
        try:
            if not hasattr(self, 'current_col') or not self.current_col:
                return

            if not hasattr(self.current_col, 'models') or model_index >= len(self.current_col.models):
                self.log_message(f"❌ Invalid COL model index: {model_index}")
                return

            model = self.current_col.models[model_index]
            model_name = getattr(model, 'name', f'Model {model_index}')

            # Create simple details message
            details = []
            details.append(f"COL Model: {model_name}")
            details.append(f"Index: {model_index}")

            # Get model statistics if available
            if hasattr(model, 'get_stats'):
                stats = model.get_stats()
                for key, value in stats.items():
                    details.append(f"{key}: {value}")

            # Show in message box for now
            QMessageBox.information(self, "COL Model Details", "\n".join(details))

        except Exception as e:
            self.log_message(f"❌ Error showing COL details: {str(e)}")

    def _update_status_from_signal(self, message):
        """Update status from unified signal system"""
        # Update status bar if available
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(message)

        # Also update GUI layout status if available
        if hasattr(self.gui_layout, 'status_label'):
            self.gui_layout.status_label.setText(message)

    def show_search_dialog(self):
        """Handle search button/menu"""
        self.log_message("🔍 Search dialog requested")
        # TODO: Implement advanced search dialog
        try:
            from gui.dialogs import show_search_dialog
            show_search_dialog(self)
        except ImportError:
            self.log_message("Advanced search dialog not available")

    def refresh_table(self):
        """Handle refresh/update button"""
        self.log_message("🔄 Refresh table requested")
        if self.current_img:
            self._update_ui_for_loaded_img()
        elif self.current_col:
            self._update_ui_for_loaded_col()
        else:
            self.log_message("No file to refresh")

    def select_all_entries(self):
        """Select all entries in current table"""
        try:
            if hasattr(self.gui_layout, 'table') and self.gui_layout.table:
                self.gui_layout.table.selectAll()
                selection_count = self.gui_layout.table.rowCount()
                self.log_message(f"✅ Selected all {selection_count} entries")
            else:
                self.log_message("❌ No table available for selection")
        except Exception as e:
            self.log_message(f"❌ Select all error: {str(e)}")

    def debug_img_entries(self):
        """Debug function to check what entries are actually loaded"""
        if not self.current_img or not self.current_img.entries:
            self.log_message("❌ No IMG loaded or no entries found")
            return

        self.log_message(f"🔍 DEBUG: IMG file has {len(self.current_img.entries)} entries")

        # Count file types
        file_types = {}
        all_extensions = set()

        for i, entry in enumerate(self.current_img.entries):
            # Debug each entry
            self.log_message(f"Entry {i}: {entry.name}")

            # Extract extension both ways
            name_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else 'NO_EXT'
            all_extensions.add(name_ext)

            # Count file types
            if name_ext not in file_types:
                file_types[name_ext] = 0
            file_types[name_ext] += 1

        # Summary
        self.log_message(f"🔍 File type summary: {file_types}")
        self.log_message(f"🔍 All extensions found: {sorted(all_extensions)}")

    def _setup_col_integration_safely(self):
        """Setup COL integration safely"""
        try:
            if COL_SETUP_FUNCTION:
                result = COL_SETUP_FUNCTION(self)
                if result:
                    self.log_message("✅ COL functionality integrated")
                else:
                    self.log_message("⚠️ COL integration returned False")
            else:
                self.log_message("⚠️ COL integration function not available")
        except Exception as e:
            self.log_message(f"❌ COL integration error: {str(e)}")

    def _on_load_progress(self, progress: int, status: str):
        """Handle loading progress updates"""
        if hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(progress, status)
        else:
            self.log_message(f"Progress: {progress}% - {status}")

    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        try:
            # Store the loaded IMG file
            current_index = self.main_tab_widget.currentIndex()

            if current_index in self.open_files:
                self.open_files[current_index]['file_object'] = img_file

            # Set current IMG reference
            self.current_img = img_file

            # Update UI
            self._update_ui_for_loaded_img()

            # Hide progress if method exists
            if hasattr(self.gui_layout, 'hide_progress'):
                self.gui_layout.hide_progress()

            self.log_message("✅ IMG file loaded and UI updated")

        except Exception as e:
            self.log_message(f"❌ Error in _on_img_loaded: {str(e)}")

    def _on_col_loaded(self, col_file):
        """Handle COL file loaded"""
        try:
            self.current_col = col_file
            current_index = self.main_tab_widget.currentIndex()

            # Update file info in open_files
            if current_index in self.open_files:
                self.open_files[current_index]['file_object'] = col_file
                self.log_message(f"✅ Updated tab {current_index} with loaded COL")
            else:
                self.log_message(f"⚠️ Tab {current_index} not found in open_files")

            # Apply enhanced COL tab styling after loading
            if hasattr(self, '_apply_individual_col_tab_style'):
                self._apply_individual_col_tab_style(current_index)

            # Update UI for loaded COL
            self._update_ui_for_loaded_col()

            # Update window title to show current file
            file_name = os.path.basename(col_file.file_path) if hasattr(col_file, 'file_path') else "Unknown COL"
            self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

            model_count = len(col_file.models) if hasattr(col_file, 'models') and col_file.models else 0
            self.log_message(f"✅ Loaded: {file_name} ({model_count} models)")

            # Hide progress and show COL-specific status
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"COL loaded: {model_count} models")

        except Exception as e:
            self.log_message(f"❌ Error in _on_col_loaded: {str(e)}")
            if hasattr(self, '_on_col_load_error'):
                self._on_col_load_error(str(e))

    def _on_col_load_error(self, error_message):
        """Handle COL file loading errors"""
        self.log_message(f"❌ COL load error: {error_message}")
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()

    def _on_img_load_error(self, error_message):
        """Handle IMG file loading errors"""
        self.log_message(f"❌ IMG load error: {error_message}")
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()

    def import_files(self):
        """Import files into current IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Import Files", "",
                "All Files (*);;DFF Models (*.dff);;TXD Textures (*.txd);;COL Collision (*.col)"
            )

            if file_paths:
                self.log_message(f"Importing {len(file_paths)} files...")

                # Show progress if method exists
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Importing files...")

                imported_count = 0
                for i, file_path in enumerate(file_paths):
                    progress = int((i + 1) * 100 / len(file_paths))
                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Importing {os.path.basename(file_path)}")

                    # Check if IMG has import_file method
                    if hasattr(self.current_img, 'import_file'):
                        if self.current_img.import_file(file_path):
                            imported_count += 1
                            self.log_message(f"Imported: {os.path.basename(file_path)}")
                    else:
                        self.log_message(f"❌ IMG import_file method not available")
                        break

                # Refresh table
                if hasattr(self, '_populate_real_img_table'):
                    self._populate_real_img_table(self.current_img)
                else:
                    populate_img_table(self.gui_layout.table, self.current_img)

                self.log_message(f"Import complete: {imported_count}/{len(file_paths)} files imported")

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Import complete")
                if hasattr(self.gui_layout, 'update_img_info'):
                    self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")

                QMessageBox.information(self, "Import Complete",
                                      f"Imported {imported_count} of {len(file_paths)} files")

        except Exception as e:
            error_msg = f"Error importing files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Import error")
            QMessageBox.critical(self, "Import Error", error_msg)

    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            # Get selected rows
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "No entries selected for export.")
                return

            # Get export directory
            export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
            if not export_dir:
                return

            # Show progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Exporting selected entries...")

            exported_count = 0
            for i, selected in enumerate(selected_rows):
                row = selected.row()
                progress = int((i + 1) * 100 / len(selected_rows))

                if row < len(self.current_img.entries):
                    entry = self.current_img.entries[row]
                    export_path = os.path.join(export_dir, entry.name)

                    if hasattr(self.gui_layout, 'show_progress'):
                        self.gui_layout.show_progress(progress, f"Exporting {entry.name}")

                    # Check if IMG has export_entry method
                    if hasattr(self.current_img, 'export_entry'):
                        if self.current_img.export_entry(entry, export_path):
                            exported_count += 1
                            self.log_message(f"Exported: {entry.name}")
                    elif hasattr(entry, 'get_data'):
                        # Alternative: use entry's get_data method
                        try:
                            data = entry.get_data()
                            with open(export_path, 'wb') as f:
                                f.write(data)
                            exported_count += 1
                            self.log_message(f"Exported: {entry.name}")
                        except Exception as e:
                            self.log_message(f"❌ Error exporting {entry.name}: {str(e)}")
                    else:
                        self.log_message(f"❌ No export method available for {entry.name}")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"Export complete: {exported_count}/{len(selected_rows)}")

            self.log_message(f"Export complete: {exported_count}/{len(selected_rows)} files exported")
            QMessageBox.information(self, "Export Complete",
                                  f"Exported {exported_count} of {len(selected_rows)} selected files")

        except Exception as e:
            error_msg = f"Error exporting files: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Export error")
            QMessageBox.critical(self, "Export Error", error_msg)

    def remove_selected(self):
        """Remove selected entries from IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            # Get selected rows
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "No entries selected for removal.")
                return

            # Confirm removal
            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Remove {len(selected_rows)} selected entries from IMG?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Remove entries (in reverse order to maintain indices)
            removed_count = 0
            for selected in reversed(selected_rows):
                row = selected.row()
                if row < len(self.current_img.entries):
                    entry_name = self.current_img.entries[row].name
                    del self.current_img.entries[row]
                    removed_count += 1
                    self.log_message(f"Removed: {entry_name}")

            # Refresh table
            if hasattr(self, '_populate_real_img_table'):
                self._populate_real_img_table(self.current_img)
            else:
                populate_img_table(self.gui_layout.table, self.current_img)

            # Update info
            if hasattr(self.gui_layout, 'update_img_info'):
                self.gui_layout.update_img_info(f"{len(self.current_img.entries)} entries")

            self.log_message(f"Removal complete: {removed_count} entries removed")
            QMessageBox.information(self, "Removal Complete",
                                  f"Removed {removed_count} entries from IMG")

        except Exception as e:
            error_msg = f"Error removing entries: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "Remove Error", error_msg)

    def close_all_img(self):
        """Close all open IMG files"""
        try:
            if hasattr(self, 'close_manager') and self.close_manager:
                # Use close manager if available
                self.close_manager.close_all_tabs()
                self.log_message("All IMG files closed")
            else:
                # Fallback: close current file
                self.current_img = None
                self.current_col = None
                self._update_ui_for_no_img()
                self.log_message("Current file closed")

        except Exception as e:
            self.log_message(f"❌ Error closing all files: {str(e)}")

    def rebuild_img_as(self):
        """Rebuild current IMG file with new name"""
        if not self.current_img:
            QMessageBox.warning(self, "No IMG", "No IMG file is currently loaded.")
            return

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Rebuild IMG As", "",
                "IMG Archives (*.img);;All Files (*)"
            )

            if file_path:
                self.log_message(f"Rebuilding IMG as: {os.path.basename(file_path)}")

                # Show progress if method exists
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(0, "Rebuilding...")

                # Check if IMG has rebuild_as method
                if hasattr(self.current_img, 'rebuild_as'):
                    if self.current_img.rebuild_as(file_path):
                        self.log_message("IMG file rebuilt successfully")
                        if hasattr(self.gui_layout, 'show_progress'):
                            self.gui_layout.show_progress(-1, "Rebuild complete")
                        QMessageBox.information(self, "Success", f"IMG file rebuilt as {os.path.basename(file_path)}")
                    else:
                        self.log_message("Failed to rebuild IMG file")
                        if hasattr(self.gui_layout, 'show_progress'):
                            self.gui_layout.show_progress(-1, "Rebuild failed")
                        QMessageBox.critical(self, "Error", "Failed to rebuild IMG file")
                elif hasattr(self.current_img, 'save_as'):
                    # Alternative: use save_as method
                    if self.current_img.save_as(file_path):
                        self.log_message("IMG file saved successfully")
                        if hasattr(self.gui_layout, 'show_progress'):
                            self.gui_layout.show_progress(-1, "Save complete")
                        QMessageBox.information(self, "Success", f"IMG file saved as {os.path.basename(file_path)}")
                    else:
                        self.log_message("Failed to save IMG file")
                        QMessageBox.critical(self, "Error", "Failed to save IMG file")
                else:
                    self.log_message("❌ No rebuild_as or save_as method available")
                    QMessageBox.critical(self, "Error", "Rebuild As method not available in IMG file class")

        except Exception as e:
            error_msg = f"Error rebuilding IMG: {str(e)}"
            self.log_message(error_msg)
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Error")
            QMessageBox.critical(self, "Rebuild Error", error_msg)

    def rebuild_all_img(self):
        """Rebuild all IMG files in directory"""
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
            if not directory:
                return

            # Find all IMG files in directory
            img_files = []
            for file in os.listdir(directory):
                if file.lower().endswith('.img'):
                    img_files.append(os.path.join(directory, file))

            if not img_files:
                QMessageBox.information(self, "No IMG Files", "No IMG files found in selected directory")
                return

            # Confirm operation
            reply = QMessageBox.question(
                self, "Rebuild All",
                f"Rebuild {len(img_files)} IMG files in directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            self.log_message(f"Rebuilding {len(img_files)} IMG files...")

            # Show progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Rebuilding all IMG files...")

            rebuilt_count = 0
            failed_files = []

            for i, img_file in enumerate(img_files):
                progress = int((i + 1) * 100 / len(img_files))
                file_name = os.path.basename(img_file)

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Rebuilding {file_name}")

                try:
                    # Load IMG file
                    img = IMGFile()
                    if not img.load_from_file(img_file):
                        failed_files.append(f"{img_file}: Failed to load")
                        continue

                    # Check if rebuild method exists and attempt rebuild
                    if hasattr(img, 'rebuild'):
                        if img.rebuild():
                            rebuilt_count += 1
                            self.log_message(f"✅ Rebuilt: {file_name}")
                        else:
                            failed_files.append(f"{file_name}: Rebuild method failed")
                    elif hasattr(img, 'save'):
                        # Alternative: try save method
                        if img.save():
                            rebuilt_count += 1
                            self.log_message(f"✅ Saved: {file_name}")
                        else:
                            failed_files.append(f"{file_name}: Save method failed")
                    else:
                        failed_files.append(f"{file_name}: No rebuild/save method available")

                    # Clean up
                    if hasattr(img, 'close'):
                        img.close()

                except Exception as e:
                    failed_files.append(f"{file_name}: {str(e)}")
                    self.log_message(f"❌ Error rebuilding {file_name}: {str(e)}")

            # Hide progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"Rebuild complete: {rebuilt_count}/{len(img_files)}")

            # Show results
            self.log_message(f"✅ Rebuild all complete: {rebuilt_count}/{len(img_files)} files rebuilt")

            if failed_files:
                # Show detailed results with failures
                failed_list = "\n".join(failed_files[:10])
                if len(failed_files) > 10:
                    failed_list += f"\n... and {len(failed_files) - 10} more failures"

                QMessageBox.warning(
                    self, "Rebuild All Results",
                    f"Rebuild completed with some issues:\n\n"
                    f"✅ Successfully rebuilt: {rebuilt_count} files\n"
                    f"❌ Failed: {len(failed_files)} files\n\n"
                    f"Failed files:\n{failed_list}"
                )
            else:
                # All successful
                QMessageBox.information(
                    self, "Rebuild All Complete",
                    f"✅ Successfully rebuilt all {rebuilt_count} IMG files!"
                )

        except Exception as e:
            error_msg = f"Error in rebuild_all_img: {str(e)}"
            self.log_message(f"❌ {error_msg}")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Rebuild all failed")

            QMessageBox.critical(self, "Rebuild All Error", error_msg)

    def merge_img(self):
        """Merge multiple IMG files"""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select IMG files to merge", "", "IMG Files (*.img)"
            )
            if len(files) < 2:
                QMessageBox.warning(self, "Warning", "Select at least 2 IMG files to merge")
                return

            output_file, _ = QFileDialog.getSaveFileName(
                self, "Save merged IMG as", "", "IMG Files (*.img)"
            )
            if output_file:
                self.log_message(f"Merging {len(files)} IMG files...")
                # TODO: Implement actual merge functionality
                QMessageBox.information(self, "Info", "Merge functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in merge_img: {str(e)}")

    def split_img(self):
        """Split IMG file into smaller parts"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            dialog = QMessageBox.question(self, "Split IMG",
                                        "Split current IMG into multiple files?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if dialog == QMessageBox.StandardButton.Yes:
                self.log_message("IMG split functionality coming soon")
                # TODO: Implement actual split functionality
                QMessageBox.information(self, "Info", "Split functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in split_img: {str(e)}")

    def convert_img_format(self):
        """Convert IMG between different formats/versions"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            self.log_message("🔄 Convert IMG format requested")
            # TODO: Implement format conversion
            QMessageBox.information(self, "Info", "IMG conversion functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in convert_img_format: {str(e)}")

    def import_files_via(self):
        """Import files using advanced options"""
        try:
            self.log_message("Import via tool functionality coming soon")
            # TODO: Implement advanced import dialog
            QMessageBox.information(self, "Info", "Advanced import functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in import_files_via: {str(e)}")

    def export_selected_via(self):
        """Export using advanced options"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return
        try:
            self.log_message("Export via tool functionality coming soon")
            # TODO: Implement advanced export dialog
            QMessageBox.information(self, "Info", "Advanced export functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in export_selected_via: {str(e)}")

    def quick_export_selected(self):
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
            # TODO: Implement actual quick export
            QMessageBox.information(self, "Info", "Quick export functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in quick_export_selected: {str(e)}")

    def remove_via_entries(self):
        """Remove entries using advanced criteria"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            self.log_message("Remove via functionality coming soon")
            # TODO: Implement advanced remove dialog
            QMessageBox.information(self, "Info", "Advanced remove functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in remove_via_entries: {str(e)}")

    def dump_entries(self):
        """Dump all entries to directory without organization"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            export_dir = QFileDialog.getExistingDirectory(self, "Select Dump Directory")
            if not export_dir:
                return

            self.log_message(f"Dumping all entries to {export_dir}")
            # TODO: Implement actual dump functionality
            QMessageBox.information(self, "Info", "Dump functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in dump_entries: {str(e)}")

    def rename_selected(self):
        """Rename selected entry"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            # Get selected rows
            if hasattr(self.gui_layout, 'table') and hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if len(selected_rows) != 1:
                QMessageBox.warning(self, "Warning", "Select exactly one entry to rename")
                return

            row = selected_rows[0].row()
            if row < len(self.current_img.entries):
                entry = self.current_img.entries[row]
                old_name = entry.name

                # Get new name from user
                from PyQt6.QtWidgets import QInputDialog
                new_name, ok = QInputDialog.getText(
                    self, "Rename Entry",
                    f"Enter new name for '{old_name}':",
                    text=old_name
                )

                if ok and new_name and new_name != old_name:
                    entry.name = new_name
                    self.log_message(f"Renamed '{old_name}' to '{new_name}'")

                    # Refresh table
                    if hasattr(self, '_populate_real_img_table'):
                        self._populate_real_img_table(self.current_img)
                    else:
                        populate_img_table(self.gui_layout.table, self.current_img)

        except Exception as e:
            self.log_message(f"❌ Error in rename_selected: {str(e)}")

    def replace_selected(self):
        """Replace selected entry with new file"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            self.log_message("Replace functionality coming soon")
            # TODO: Implement replace functionality
            QMessageBox.information(self, "Info", "Replace functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in replace_selected: {str(e)}")

    def show_settings(self):
        """Show application settings dialog"""
        try:
            self.show_gui_settings()
        except Exception as e:
            self.log_message(f"❌ Error showing settings: {str(e)}")

    def show_theme_settings(self):
        """Show theme settings dialog"""
        try:
            self.show_settings()  # For now, use general settings
        except Exception as e:
            self.log_message(f"❌ Error showing theme settings: {str(e)}")

    def manage_templates(self):
        """Show template management dialog"""
        try:
            if hasattr(self, 'template_manager'):
                # TODO: Implement template management dialog
                self.log_message("Template management coming soon")
                QMessageBox.information(self, "Info", "Template management coming soon")
            else:
                self.log_message("❌ Template manager not available")
        except Exception as e:
            self.log_message(f"❌ Error in manage_templates: {str(e)}")

    def export_all(self):
        """Export all entries from IMG"""
        if not self.current_img:
            QMessageBox.warning(self, "Warning", "No IMG file loaded")
            return

        try:
            export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
            if not export_dir:
                return

            entry_count = len(self.current_img.entries)
            if entry_count == 0:
                QMessageBox.information(self, "Info", "No entries to export")
                return

            self.log_message(f"Exporting all {entry_count} entries...")
            # TODO: Implement export all functionality
            QMessageBox.information(self, "Info", "Export all functionality coming soon")
        except Exception as e:
            self.log_message(f"❌ Error in export_all: {str(e)}")

    def open_file_dialog(self):
        """Unified file dialog for IMG and COL files"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open IMG/COL Archive", "",
            "All Supported (*.img *.col);;IMG Archives (*.img);;COL Archives (*.col);;All Files (*)")

        if file_path:
            self.load_file_unified(file_path)

    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type by extension and content"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.img':
                return "IMG"
            elif file_ext == '.col':
                return "COL"

            # Check file content if extension is ambiguous
            with open(file_path, 'rb') as f:
                header = f.read(16)

            if len(header) < 4:
                return "UNKNOWN"

            # Check for IMG signatures
            if header[:4] in [b'VER2', b'VER3']:
                return "IMG"

            # Check for COL signatures
            elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                return "COL"

            # Default to IMG for unknown formats
            return "IMG"

        except Exception as e:
            self.log_message(f"❌ Error detecting file type: {str(e)}")
            return "UNKNOWN"

    def load_file_unified(self, file_path: str):
        """Unified file loader with proper type detection"""
        try:
            file_type = self._detect_file_type(file_path)

            if file_type == "IMG":
                self.log_message(f"🔍 Loading as IMG file: {os.path.basename(file_path)}")
                self.load_img_file(file_path)
            elif file_type == "COL":
                self.log_message(f"🔍 Loading as COL file: {os.path.basename(file_path)}")
                self._load_col_file_safely(file_path)
            else:
                # Try as IMG by default
                self.log_message(f"🔍 Unknown format, trying as IMG: {os.path.basename(file_path)}")
                self.load_img_file(file_path)

        except Exception as e:
            self.log_message(f"❌ Error in unified file loader: {str(e)}")

    def _load_col_file_safely(self, file_path):
        """Load COL file safely - REDIRECTS to col_tab_integration"""
        try:
            if hasattr(self, 'load_col_file_safely'):
                # Use the method provided by col_tab_integration
                self.load_col_file_safely(file_path)
            else:
                self.log_message("❌ COL loading method not available")
                self._load_col_as_generic_file(file_path)
        except Exception as e:
            self.log_message(f"❌ Error loading COL file: {str(e)}")

    def _load_col_as_generic_file(self, file_path):
        """Load COL as generic file when COL classes aren't available"""
        try:
            # Create simple COL representation
            self.current_col = {
                "file_path": file_path,
                "type": "COL",
                "size": os.path.getsize(file_path)
            }

            # Update UI
            self._update_ui_for_loaded_col()

            self.log_message(f"✅ Loaded COL (generic): {os.path.basename(file_path)}")

        except Exception as e:
            self.log_message(f"❌ Error loading COL as generic: {str(e)}")

    def load_img_file(self, file_path: str):
        """Load IMG file with progress tracking"""
        try:
            self.log_message(f"Loading IMG file: {os.path.basename(file_path)}")

            # Show progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Loading IMG...")

            # Load in background thread
            self.load_thread = IMGLoadThread(file_path)
            self.load_thread.progress_update.connect(self._on_load_progress)
            self.load_thread.status_update.connect(self._update_status_from_signal)
            self.load_thread.load_complete.connect(self._on_img_loaded)
            self.load_thread.load_error.connect(self._on_img_load_error)
            self.load_thread.start()

        except Exception as e:
            self.log_message(f"Error loading IMG file: {str(e)}")
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Load error")

    def _load_img_file_in_new_tab(self, file_path: str):
        """Load IMG file in a new tab"""
        try:
            # Create new tab
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)

            # Setup GUI for this tab
            self.gui_layout.create_main_ui_with_splitters(tab_layout)

            # Add tab
            tab_index = self.main_tab_widget.addTab(tab_widget, f"📁 {os.path.basename(file_path)}")
            self.main_tab_widget.setCurrentIndex(tab_index)

            # Store file info
            self.open_files[tab_index] = {
                'file_path': file_path,
                'type': 'IMG',
                'file_object': None
            }

            # Load the file
            self.load_img_file(file_path)

        except Exception as e:
            self.log_message(f"❌ Error loading IMG in new tab: {str(e)}")

    def _detect_and_open_file(self, file_path: str) -> bool:
        """Detect file type and open with appropriate handler"""
        try:
            # First check by extension
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.img':
                self.load_img_file(file_path)
                return True
            elif file_ext == '.col':
                self._load_col_file_safely(file_path)
                return True

            # If extension is ambiguous, check file content
            with open(file_path, 'rb') as f:
                header = f.read(16)

            if len(header) < 4:
                return False

            # Check for IMG signatures
            if header[:4] in [b'VER2', b'VER3']:
                self.log_message(f"🔍 Detected IMG file by signature")
                self.load_img_file(file_path)
                return True

            # Check for COL signatures
            elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
                self.log_message(f"🔍 Detected COL file by signature")
                self._load_col_file_safely(file_path)
                return True

            # Try reading as IMG version 1 (no header signature)
            elif len(header) >= 8:
                # Could be IMG v1 or unknown format
                self.log_message(f"🔍 Attempting to open as IMG file")
                self.load_img_file(file_path)
                return True

            return False

        except Exception as e:
            self.log_message(f"❌ Error detecting file type: {str(e)}")
            return False

    def _populate_col_table_img_style(self, col_file):
        """Populate table with COL data in IMG entry style"""
        try:
            if not hasattr(col_file, 'models') or not col_file.models:
                self.log_message("⚠️ COL file has no models to display")
                return

            models = col_file.models
            table = self.gui_layout.table

            # Set table structure for COL (same columns as IMG)
            table.setColumnCount(7)  # Name, Type, Size, Offset, Version, Elements, Details
            table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Offset", "Version", "Elements", "Details"])
            table.setRowCount(len(models))

            for row, model in enumerate(models):
                try:
                    details = self.get_col_model_details_for_display(model, row)

                    # Name (same as IMG entry name)
                    name = details.get('name', f"Model_{row}")
                    table.setItem(row, 0, QTableWidgetItem(name))

                    # Type (always COL for consistency)
                    table.setItem(row, 1, QTableWidgetItem("COL"))

                    # Size (estimated, formatted like IMG entries)
                    size_bytes = details.get('size', 0)
                    size_str = self._format_file_size(size_bytes)
                    table.setItem(row, 2, QTableWidgetItem(size_str))

                    # Offset (use row index * estimated size for display)
                    offset = row * size_bytes
                    offset_str = f"0x{offset:08X}"
                    table.setItem(row, 3, QTableWidgetItem(offset_str))

                    # Version (COL version)
                    version = details.get('version', 'Unknown')
                    table.setItem(row, 4, QTableWidgetItem(f"COL{version}"))

                    # Elements (total collision elements)
                    elements = details.get('elements', 0)
                    table.setItem(row, 5, QTableWidgetItem(str(elements)))

                    # Details (brief summary)
                    details_summary = f"{details.get('spheres', 0)}s {details.get('boxes', 0)}b {details.get('faces', 0)}f"
                    table.setItem(row, 6, QTableWidgetItem(details_summary))

                except Exception as e:
                    self.log_message(f"❌ Error populating COL model {row}: {str(e)}")
                    # Create fallback row (same as IMG error handling)
                    table.setItem(row, 0, QTableWidgetItem(f"Model_{row}"))
                    table.setItem(row, 1, QTableWidgetItem("COL"))
                    table.setItem(row, 2, QTableWidgetItem("0 B"))
                    table.setItem(row, 3, QTableWidgetItem("0x0"))
                    table.setItem(row, 4, QTableWidgetItem("Unknown"))
                    table.setItem(row, 5, QTableWidgetItem("None"))
                    table.setItem(row, 6, QTableWidgetItem("Error"))

            self.log_message(f"✅ Table populated with {len(models)} COL models (IMG format)")

        except Exception as e:
            self.log_message(f"❌ Error populating COL table: {str(e)}")

    def _estimate_col_model_size_bytes(self, model):
        """Estimate COL model size in bytes (similar to IMG entry sizes)"""
        try:
            if not hasattr(model, 'get_stats'):
                return 1024  # Default 1KB

            stats = model.get_stats()

            # Rough estimation based on collision elements
            size = 100  # Base model overhead (header, name, etc.)
            size += stats.get('spheres', 0) * 16     # 16 bytes per sphere
            size += stats.get('boxes', 0) * 24       # 24 bytes per box
            size += stats.get('vertices', 0) * 12    # 12 bytes per vertex
            size += stats.get('faces', 0) * 8        # 8 bytes per face
            size += stats.get('face_groups', 0) * 8  # 8 bytes per face group

            # Add version-specific overhead
            if hasattr(model, 'version') and hasattr(model.version, 'value'):
                if model.version.value >= 3:
                    size += stats.get('shadow_vertices', 0) * 12
                    size += stats.get('shadow_faces', 0) * 8
                    size += 64  # COL3+ additional headers
                elif model.version.value >= 2:
                    size += 48  # COL2 headers

            return max(size, 64)  # Minimum 64 bytes

        except Exception:
            return 1024  # Default 1KB on error

    def _format_file_size(self, size_bytes):
        """Format file size same as IMG entries"""
        try:
            # Use the same formatting as IMG entries
            try:
                from components.img_core_classes import format_file_size
                return format_file_size(size_bytes)
            except:
                pass

            # Fallback formatting (same logic as IMG)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes // 1024} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes // (1024 * 1024)} MB"
            else:
                return f"{size_bytes // (1024 * 1024 * 1024)} GB"

        except Exception:
            return f"{size_bytes} bytes"

    def get_col_model_details_for_display(self, model, row_index):
        """Get COL model details in same format as IMG entry details"""
        try:
            stats = model.get_stats() if hasattr(model, 'get_stats') else {}

            details = {
                'name': getattr(model, 'name', f"Model_{row_index}") if hasattr(model, 'name') and model.name else f"Model_{row_index}",
                'type': "COL",
                'size': self._estimate_col_model_size_bytes(model),
                'version': str(model.version.value) if hasattr(model, 'version') and hasattr(model.version, 'value') else "Unknown",
                'elements': stats.get('total_elements', 0),
                'spheres': stats.get('spheres', 0),
                'boxes': stats.get('boxes', 0),
                'faces': stats.get('faces', 0),
                'vertices': stats.get('vertices', 0),
            }

            if hasattr(model, 'bounding_box') and model.bounding_box:
                bbox = model.bounding_box
                if hasattr(bbox, 'center') and hasattr(bbox, 'radius'):
                    details.update({
                        'bbox_center': (bbox.center.x, bbox.center.y, bbox.center.z),
                        'bbox_radius': bbox.radius,
                    })
                    if hasattr(bbox, 'min') and hasattr(bbox, 'max'):
                        details.update({
                            'bbox_min': (bbox.min.x, bbox.min.y, bbox.min.z),
                            'bbox_max': (bbox.max.x, bbox.max.y, bbox.max.z),
                        })

            return details

        except Exception as e:
            self.log_message(f"❌ Error getting COL model details: {str(e)}")
            return {
                'name': f"Model_{row_index}",
                'type': "COL",
                'size': 0,
                'version': "Unknown",
                'elements': 0,
            }

    def _apply_individual_col_tab_style(self, tab_index):
        """Apply COL-specific styling to individual tab"""
        try:
            if not hasattr(self, 'main_tab_widget'):
                return

            # Get tab widget
            tab_widget = self.main_tab_widget.widget(tab_index)
            if not tab_widget:
                return

            # Apply COL-specific styling
            tab_widget.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTableWidget {
                    background-color: #353535;
                    alternate-background-color: #404040;
                    gridline-color: #555555;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #444444;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
            """)

            self.log_message(f"✅ Applied COL styling to tab {tab_index}")

        except Exception as e:
            self.log_message(f"❌ Error applying COL tab styling: {str(e)}")

    def _setup_col_tab(self, file_path):
        """Setup new tab for COL file"""
        try:
            # Create new tab widget
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)

            # Create GUI layout for this tab
            self.gui_layout.create_main_ui_with_splitters(tab_layout)

            # Add tab with COL icon
            file_name = os.path.basename(file_path)
            tab_index = self.main_tab_widget.addTab(tab_widget, f"🛡️ {file_name}")
            self.main_tab_widget.setCurrentIndex(tab_index)

            # Store file info
            self.open_files[tab_index] = {
                'file_path': file_path,
                'type': 'COL',
                'file_object': None
            }

            self.log_message(f"✅ COL tab created: {file_name}")
            return tab_index

        except Exception as e:
            self.log_message(f"❌ Error setting up COL tab: {str(e)}")
            return None

    def open_file_generic(self):
        """Generic file opener - fallback method"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "All Files (*);;IMG Archives (*.img);;COL Archives (*.col)"
            )

            if file_path:
                self._detect_and_open_file(file_path)

        except Exception as e:
            self.log_message(f"❌ Error in generic file opener: {str(e)}")

    def validate_current_file(self):
        """Validate currently loaded file"""
        try:
            if self.current_img:
                self.validate_img()
            elif self.current_col:
                self.validate_col()
            else:
                self.log_message("❌ No file loaded to validate")

        except Exception as e:
            self.log_message(f"❌ Error validating file: {str(e)}")

    def validate_col(self):
        """Validate current COL file"""
        try:
            if not self.current_col:
                self.log_message("❌ No COL file loaded")
                return

            # Basic COL validation
            if hasattr(self.current_col, 'models'):
                model_count = len(self.current_col.models)
                self.log_message(f"✅ COL validation: {model_count} models found")

                # Check each model
                valid_models = 0
                for i, model in enumerate(self.current_col.models):
                    if hasattr(model, 'get_stats'):
                        stats = model.get_stats()
                        if stats.get('total_elements', 0) > 0:
                            valid_models += 1
                        else:
                            self.log_message(f"⚠️ Model {i} has no collision elements")
                    else:
                        self.log_message(f"⚠️ Model {i} cannot be validated")

                self.log_message(f"✅ COL validation complete: {valid_models}/{model_count} valid models")
            else:
                self.log_message("⚠️ COL file structure cannot be validated")

        except Exception as e:
            self.log_message(f"❌ COL validation error: {str(e)}")

    def get_current_file_info(self):
        """Get information about currently loaded file"""
        try:
            if self.current_img:
                entry_count = len(self.current_img.entries) if self.current_img.entries else 0
                file_path = getattr(self.current_img, 'file_path', 'Unknown')
                return {
                    'type': 'IMG',
                    'path': file_path,
                    'entries': entry_count,
                    'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
            elif self.current_col:
                if hasattr(self.current_col, 'models'):
                    model_count = len(self.current_col.models)
                    file_path = getattr(self.current_col, 'file_path', 'Unknown')
                else:
                    model_count = 0
                    file_path = self.current_col.get('file_path', 'Unknown') if isinstance(self.current_col, dict) else 'Unknown'

                return {
                    'type': 'COL',
                    'path': file_path,
                    'models': model_count,
                    'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
            else:
                return {
                    'type': 'None',
                    'path': 'No file loaded',
                    'entries': 0,
                    'size': 0
                }

        except Exception as e:
            self.log_message(f"❌ Error getting file info: {str(e)}")
            return {'type': 'Error', 'path': 'Unknown', 'entries': 0, 'size': 0}

    def get_selected_entries_info(self):
        """Get information about currently selected entries"""
        try:
            if not hasattr(self.gui_layout, 'table'):
                return {'count': 0, 'total_size': 0}

            # Get selected rows
            if hasattr(self.gui_layout.table, 'selectionModel'):
                selected_rows = self.gui_layout.table.selectionModel().selectedRows()
            else:
                selected_rows = []

            if not selected_rows:
                return {'count': 0, 'total_size': 0}

            total_size = 0
            valid_selections = 0

            for selected in selected_rows:
                row = selected.row()

                if self.current_img and row < len(self.current_img.entries):
                    # IMG file entry
                    entry = self.current_img.entries[row]
                    total_size += entry.size
                    valid_selections += 1
                elif self.current_col and hasattr(self.current_col, 'models') and row < len(self.current_col.models):
                    # COL file model
                    model = self.current_col.models[row]
                    model_size = self._estimate_col_model_size_bytes(model)
                    total_size += model_size
                    valid_selections += 1

            return {
                'count': valid_selections,
                'total_size': total_size,
                'size_formatted': self._format_file_size(total_size)
            }

        except Exception as e:
            self.log_message(f"❌ Error getting selection info: {str(e)}")
            return {'count': 0, 'total_size': 0}

    def clear_current_file(self):
        """Clear currently loaded file and reset UI"""
        try:
            # Clear file references
            self.current_img = None
            self.current_col = None

            # Reset UI
            self._update_ui_for_no_img()

            self.log_message("✅ Current file cleared")

        except Exception as e:
            self.log_message(f"❌ Error clearing file: {str(e)}")

    def reload_current_file(self):
        """Reload the currently loaded file"""
        try:
            current_info = self.get_current_file_info()
            file_path = current_info.get('path')

            if file_path and file_path != 'Unknown' and file_path != 'No file loaded':
                self.log_message(f"🔄 Reloading file: {os.path.basename(file_path)}")
                self.load_file_unified(file_path)
            else:
                self.log_message("❌ No file to reload")

        except Exception as e:
            self.log_message(f"❌ Error reloading file: {str(e)}")

    def show_file_properties(self):
        """Show properties dialog for current file"""
        try:
            file_info = self.get_current_file_info()
            selection_info = self.get_selected_entries_info()

            if file_info['type'] == 'None':
                QMessageBox.information(self, "File Properties", "No file is currently loaded.")
                return

            # Create properties message
            props = []
            props.append(f"File Type: {file_info['type']}")
            props.append(f"File Path: {file_info['path']}")
            props.append(f"File Size: {self._format_file_size(file_info['size'])}")

            if file_info['type'] == 'IMG':
                props.append(f"Entries: {file_info['entries']}")
            elif file_info['type'] == 'COL':
                props.append(f"Models: {file_info['models']}")

            if selection_info['count'] > 0:
                props.append("")
                props.append(f"Selected: {selection_info['count']} items")
                props.append(f"Selection Size: {selection_info['size_formatted']}")

            QMessageBox.information(self, "File Properties", "\n".join(props))

        except Exception as e:
            self.log_message(f"❌ Error showing file properties: {str(e)}")

    def copy_file_path(self):
        """Copy current file path to clipboard"""
        try:
            file_info = self.get_current_file_info()
            file_path = file_info.get('path')

            if file_path and file_path not in ['Unknown', 'No file loaded']:
                # Copy to clipboard
                from PyQt6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(file_path)
                self.log_message(f"📋 Copied to clipboard: {os.path.basename(file_path)}")
            else:
                self.log_message("❌ No file path to copy")

        except Exception as e:
            self.log_message(f"❌ Error copying file path: {str(e)}")

    def show_recent_files(self):
        """Show recent files menu"""
        try:
            # Import the recent files manager
            from components.img_core_classes import RecentFilesManager

            recent_manager = RecentFilesManager()
            recent_files = recent_manager.get_recent_files()

            if not recent_files:
                QMessageBox.information(self, "Recent Files", "No recent files found.")
                return

            # Create context menu with recent files
            from PyQt6.QtWidgets import QMenu
            menu = QMenu(self)

            for file_path in recent_files:
                file_name = os.path.basename(file_path)
                action = menu.addAction(f"📁 {file_name}")
                action.setData(file_path)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))

            # Show menu at cursor position
            menu.exec(self.mapFromGlobal(self.cursor().pos()))

        except Exception as e:
            self.log_message(f"❌ Error showing recent files: {str(e)}")

    def open_recent_file(self, file_path: str):
        """Open a recent file"""
        try:
            if os.path.exists(file_path):
                self.log_message(f"Opening recent file: {os.path.basename(file_path)}")
                self.load_file_unified(file_path)

                # Update recent files list
                from components.img_core_classes import RecentFilesManager
                recent_manager = RecentFilesManager()
                recent_manager.add_file(file_path)
            else:
                QMessageBox.warning(self, "File Not Found",
                                  f"The file '{file_path}' no longer exists.")
                # Remove from recent files
                from components.img_core_classes import RecentFilesManager
                recent_manager = RecentFilesManager()
                if file_path in recent_manager.recent_files:
                    recent_manager.recent_files.remove(file_path)
                    recent_manager._save_recent_files()

        except Exception as e:
            self.log_message(f"❌ Error opening recent file: {str(e)}")

    def add_to_recent_files(self, file_path: str):
        """Add file to recent files list"""
        try:
            from components.img_core_classes import RecentFilesManager
            recent_manager = RecentFilesManager()
            recent_manager.add_file(file_path)
            self.log_message(f"Added to recent files: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"❌ Error adding to recent files: {str(e)}")

    def clear_recent_files(self):
        """Clear recent files list"""
        try:
            reply = QMessageBox.question(
                self, "Clear Recent Files",
                "Clear all recent files from the list?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                from components.img_core_classes import RecentFilesManager
                recent_manager = RecentFilesManager()
                recent_manager.recent_files = []
                recent_manager._save_recent_files()
                self.log_message("✅ Recent files list cleared")

        except Exception as e:
            self.log_message(f"❌ Error clearing recent files: {str(e)}")

    def backup_current_file(self):
        """Create backup of current file"""
        try:
            current_info = self.get_current_file_info()
            file_path = current_info.get('path')

            if not file_path or file_path in ['Unknown', 'No file loaded']:
                QMessageBox.warning(self, "No File", "No file is currently loaded to backup.")
                return

            if not os.path.exists(file_path):
                QMessageBox.warning(self, "File Not Found", "Current file no longer exists.")
                return

            # Create backup filename
            backup_path = file_path + '.backup'

            # Check if backup already exists
            if os.path.exists(backup_path):
                reply = QMessageBox.question(
                    self, "Backup Exists",
                    f"Backup file already exists:\n{backup_path}\n\nOverwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            # Create backup
            import shutil
            shutil.copy2(file_path, backup_path)

            self.log_message(f"✅ Backup created: {os.path.basename(backup_path)}")
            QMessageBox.information(self, "Backup Created",
                                  f"Backup created successfully:\n{backup_path}")

        except Exception as e:
            error_msg = f"Error creating backup: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Backup Error", error_msg)

    def restore_from_backup(self):
        """Restore file from backup"""
        try:
            current_info = self.get_current_file_info()
            file_path = current_info.get('path')

            if not file_path or file_path in ['Unknown', 'No file loaded']:
                QMessageBox.warning(self, "No File", "No file is currently loaded.")
                return

            backup_path = file_path + '.backup'

            if not os.path.exists(backup_path):
                QMessageBox.warning(self, "No Backup",
                                  f"No backup file found for:\n{file_path}")
                return

            # Confirm restore
            reply = QMessageBox.question(
                self, "Restore Backup",
                f"Restore from backup?\n\nThis will overwrite:\n{file_path}\n\nWith backup:\n{backup_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                import shutil
                shutil.copy2(backup_path, file_path)

                self.log_message(f"✅ Restored from backup: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Restore Complete", "File restored from backup successfully.")

                # Reload the file
                self.reload_current_file()

        except Exception as e:
            error_msg = f"Error restoring from backup: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Restore Error", error_msg)

    def auto_save_settings(self):
        """Auto-save application settings"""
        try:
            if hasattr(self, 'app_settings') and self.app_settings:
                if self.app_settings.get_setting('auto_save', True):
                    self.app_settings.save_settings()
                    self.log_message("⚙️ Settings auto-saved")

        except Exception as e:
            self.log_message(f"❌ Auto-save error: {str(e)}")

    def export_settings(self):
        """Export application settings to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Settings", "imgfactory_settings.json",
                "JSON Files (*.json);;All Files (*)"
            )

            if file_path:
                if hasattr(self, 'app_settings') and self.app_settings:
                    # Export settings
                    import json
                    with open(file_path, 'w') as f:
                        json.dump(self.app_settings.current_settings, f, indent=2)

                    self.log_message(f"✅ Settings exported: {os.path.basename(file_path)}")
                    QMessageBox.information(self, "Export Complete",
                                          f"Settings exported to:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Settings not available for export.")

        except Exception as e:
            error_msg = f"Error exporting settings: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Export Error", error_msg)

    def import_settings(self):
        """Import application settings from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Settings", "",
                "JSON Files (*.json);;All Files (*)"
            )

            if file_path:
                if hasattr(self, 'app_settings') and self.app_settings:
                    # Import settings
                    import json
                    with open(file_path, 'r') as f:
                        imported_settings = json.load(f)

                    # Update current settings
                    self.app_settings.current_settings.update(imported_settings)
                    self.app_settings.save_settings()

                    # Apply new theme
                    from utils.app_settings_system import apply_theme_to_app
                    apply_theme_to_app(self.app_settings, self)

                    self.log_message(f"✅ Settings imported: {os.path.basename(file_path)}")
                    QMessageBox.information(self, "Import Complete",
                                          f"Settings imported from:\n{file_path}\n\nRestart may be required for all changes to take effect.")
                else:
                    QMessageBox.warning(self, "Error", "Settings system not available.")

        except Exception as e:
            error_msg = f"Error importing settings: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Import Error", error_msg)

    def reset_settings_to_defaults(self):
        """Reset all settings to default values"""
        try:
            reply = QMessageBox.question(
                self, "Reset Settings",
                "Reset all settings to default values?\n\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if hasattr(self, 'app_settings') and self.app_settings:
                    # Reset to defaults
                    self.app_settings.current_settings = self.app_settings._get_default_settings()
                    self.app_settings.save_settings()

                    # Apply default theme
                    from utils.app_settings_system import apply_theme_to_app
                    apply_theme_to_app(self.app_settings, self)

                    self.log_message("✅ Settings reset to defaults")
                    QMessageBox.information(self, "Reset Complete",
                                          "Settings have been reset to default values.\n\nRestart recommended.")
                else:
                    QMessageBox.warning(self, "Error", "Settings system not available.")

        except Exception as e:
            error_msg = f"Error resetting settings: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Reset Error", error_msg)

    def check_for_updates(self):
        """Check for application updates"""
        try:
            # Placeholder for update checking
            self.log_message("🔍 Checking for updates...")

            # In a real implementation, this would check online for updates
            QMessageBox.information(
                self, "Update Check",
                "Update checking not implemented yet.\n\nCurrent version: IMG Factory 1.5"
            )

        except Exception as e:
            self.log_message(f"❌ Update check error: {str(e)}")

    def show_changelog(self):
        """Show application changelog"""
        try:
            changelog_text = """
IMG Factory 1.5 - Changelog

Version 1.5.0:
• Complete rewrite using PyQt6
• Added COL file support
• Improved import/export system
• New theme system with multiple themes
• Enhanced search functionality
• Better error handling and logging
• Tab-based interface for multiple files
• Unified signal handling system
• Performance improvements
• Bug fixes and stability improvements

Version 1.2.0 (Original):
• Basic IMG file support
• File import/export
• Entry management
• Original GUI with PyQt4
            """

            # Show in message box
            msg = QMessageBox(self)
            msg.setWindowTitle("Changelog")
            msg.setText("IMG Factory Changelog")
            msg.setDetailedText(changelog_text.strip())
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        except Exception as e:
            self.log_message(f"❌ Error showing changelog: {str(e)}")

    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        try:
            shortcuts = [
                ("File Operations", [
                    ("Ctrl+N", "New IMG"),
                    ("Ctrl+O", "Open File"),
                    ("Ctrl+W", "Close File"),
                    ("Ctrl+S", "Save"),
                    ("Ctrl+Q", "Exit")
                ]),
                ("Edit Operations", [
                    ("Ctrl+A", "Select All"),
                    ("Ctrl+F", "Search"),
                    ("F3", "Find Next"),
                    ("Shift+F3", "Find Previous")
                ]),
                ("Debug", [
                    ("Ctrl+Shift+D", "Toggle COL Debug"),
                    ("F12", "Debug Console")
                ])
            ]

            # Create shortcuts text
            shortcuts_text = ""
            for category, items in shortcuts:
                shortcuts_text += f"{category}:\n"
                for shortcut, description in items:
                    shortcuts_text += f"  {shortcut:<15} {description}\n"
                shortcuts_text += "\n"

            # Show in message box
            msg = QMessageBox(self)
            msg.setWindowTitle("Keyboard Shortcuts")
            msg.setText("IMG Factory Keyboard Shortcuts")
            msg.setDetailedText(shortcuts_text.strip())
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        except Exception as e:
            self.log_message(f"❌ Error showing shortcuts: {str(e)}")

    def show_system_info(self):
        """Show system information dialog"""
        try:
            import platform
            import sys

            info = []
            info.append(f"IMG Factory Version: 1.5")
            info.append(f"Python Version: {sys.version}")
            info.append(f"PyQt6 Version: {self._get_pyqt_version()}")
            info.append(f"Platform: {platform.platform()}")
            info.append(f"Architecture: {platform.architecture()[0]}")
            info.append(f"Processor: {platform.processor()}")

            # Current file info
            current_info = self.get_current_file_info()
            info.append("")
            info.append(f"Current File Type: {current_info['type']}")
            if current_info['type'] != 'None':
                info.append(f"File Path: {current_info['path']}")
                info.append(f"File Size: {self._format_file_size(current_info['size'])}")

            info_text = "\n".join(info)

            QMessageBox.information(self, "System Information", info_text)

        except Exception as e:
            self.log_message(f"❌ Error showing system info: {str(e)}")

    def _get_pyqt_version(self):
        """Get PyQt version string"""
        try:
            from PyQt6.QtCore import QT_VERSION_STR
            return QT_VERSION_STR
        except:
            return "Unknown"

    def export_debug_log(self):
        """Export debug log to file"""
        try:
            if not hasattr(self, 'log') or not self.log:
                QMessageBox.warning(self, "No Log", "No log data available to export.")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Debug Log", f"imgfactory_log_{self._get_timestamp_for_file()}.txt",
                "Text Files (*.txt);;All Files (*)"
            )

            if file_path:
                log_text = self.log.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"IMG Factory 1.5 Debug Log\n")
                    f.write(f"Exported: {self._get_timestamp()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(log_text)

                self.log_message(f"✅ Debug log exported: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Export Complete",
                                      f"Debug log exported to:\n{file_path}")

        except Exception as e:
            error_msg = f"Error exporting debug log: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Export Error", error_msg)

    def _get_timestamp_for_file(self):
        """Get timestamp formatted for filenames"""
        try:
            from datetime import datetime
            return datetime.now().strftime("%Y%m%d_%H%M%S")
        except:
            return "unknown"

    def clear_debug_log(self):
        """Clear the debug log"""
        try:
            if hasattr(self, 'log') and self.log:
                reply = QMessageBox.question(
                    self, "Clear Log",
                    "Clear all debug log entries?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.log.clear()
                    self.log_message("✅ Debug log cleared")
            else:
                QMessageBox.warning(self, "No Log", "No log panel available.")

        except Exception as e:
            self.log_message(f"❌ Error clearing log: {str(e)}")

    def restart_application(self):
        """Restart the application"""
        try:
            reply = QMessageBox.question(
                self, "Restart Application",
                "Restart IMG Factory?\n\nAny unsaved changes will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.log_message("🔄 Restarting application...")

                # Save settings before restart
                if hasattr(self, 'app_settings'):
                    self.app_settings.save_settings()

                # Restart the application
                import sys
                from PyQt6.QtWidgets import QApplication
                QApplication.quit()
                QApplication.instance().exit(1000)  # Exit code for restart

        except Exception as e:
            self.log_message(f"❌ Restart error: {str(e)}")

    def exit_application(self):
        """Exit the application safely"""
        try:
            # Check for unsaved changes
            unsaved_changes = False  # TODO: Implement unsaved changes detection

            if unsaved_changes:
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "There are unsaved changes. Exit anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            self.log_message("👋 Exiting IMG Factory...")

            # Save settings
            if hasattr(self, 'app_settings'):
                self.app_settings.save_settings()

            # Close application
            self.close()

        except Exception as e:
            self.log_message(f"❌ Exit error: {str(e)}")
            self.close()  # Force close on error

    def show_memory_usage(self):
        """Show current memory usage"""
        try:
            import psutil
            import os

            # Get current process
            process = psutil.Process(os.getpid())

            # Memory info
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # System memory
            system_memory = psutil.virtual_memory()
            system_total_gb = system_memory.total / 1024 / 1024 / 1024
            system_used_percent = system_memory.percent

            info = []
            info.append(f"IMG Factory Memory Usage: {memory_mb:.1f} MB")
            info.append(f"System Memory: {system_used_percent:.1f}% of {system_total_gb:.1f} GB")
            info.append("")

            # File info
            current_info = self.get_current_file_info()
            if current_info['type'] != 'None':
                file_size_mb = current_info['size'] / 1024 / 1024
                info.append(f"Current File: {file_size_mb:.1f} MB")

            QMessageBox.information(self, "Memory Usage", "\n".join(info))

        except ImportError:
            QMessageBox.warning(self, "Memory Usage", "psutil not available.\nCannot show memory usage.")
        except Exception as e:
            self.log_message(f"❌ Error showing memory usage: {str(e)}")

    def show_debug_console(self):
        """Show debug console (placeholder)"""
        try:
            self.log_message("🔧 Debug console requested")
            # TODO: Implement actual debug console
            QMessageBox.information(self, "Debug Console", "Debug console not yet implemented.")
        except Exception as e:
            self.log_message(f"❌ Debug console error: {str(e)}")

    def toggle_performance_mode(self):
        """Toggle between performance and debug mode"""
        try:
            if hasattr(self, 'app_settings') and self.app_settings:
                current_debug = self.app_settings.get_setting('debug_mode', False)
                new_debug = not current_debug

                self.app_settings.set_setting('debug_mode', new_debug)

                if new_debug:
                    self.log_message("🔧 Debug mode enabled")
                else:
                    self.log_message("⚡ Performance mode enabled")

                QMessageBox.information(
                    self, "Mode Changed",
                    f"{'Debug' if new_debug else 'Performance'} mode enabled.\n\nRestart recommended for full effect."
                )
            else:
                self.log_message("❌ Settings not available for mode toggle")

        except Exception as e:
            self.log_message(f"❌ Mode toggle error: {str(e)}")

    def compact_database(self):
        """Compact application database/settings (placeholder)"""
        try:
            self.log_message("🗜️ Database compaction requested")
            # TODO: Implement database compaction if needed
            QMessageBox.information(self, "Database Compact", "Database compaction not yet implemented.")
        except Exception as e:
            self.log_message(f"❌ Database compact error: {str(e)}")

    def close_img_file(self):
        """Close current IMG/COL file"""
        try:
            current_index = self.main_tab_widget.currentIndex() if hasattr(self, 'main_tab_widget') else 0

            # Log what we're closing
            if hasattr(self, 'current_img') and self.current_img:
                file_path = getattr(self.current_img, 'file_path', 'Unknown IMG')
                self.log_message(f"🗂️ Closing IMG: {os.path.basename(file_path)}")
            elif hasattr(self, 'current_col') and self.current_col:
                file_path = getattr(self.current_col, 'file_path', 'Unknown COL')
                self.log_message(f"🗂️ Closing COL: {os.path.basename(file_path)}")
            else:
                self.log_message("🗂️ Closing current tab")

            # Clear the current file data
            self.current_img = None
            self.current_col = None

            # Remove from open_files if exists
            if hasattr(self, 'open_files') and current_index in self.open_files:
                del self.open_files[current_index]

            # Reset tab name to "No File"
            if hasattr(self, 'main_tab_widget'):
                self.main_tab_widget.setTabText(current_index, "📁 No File")

            # Update UI for no file state
            self._update_ui_for_no_img()

            self.log_message("✅ File closed successfully")

        except Exception as e:
            error_msg = f"Error closing file: {str(e)}"
            self.log_message(f"❌ {error_msg}")

    def rebuild_all_img_with_directory_selection(self):
        """Rebuild all IMG files with directory selection"""
        try:
            # Get base directory - use current IMG directory or let user choose
            if self.current_img and hasattr(self.current_img, 'file_path'):
                base_dir = os.path.dirname(self.current_img.file_path)
                use_current_dir = QMessageBox.question(
                    self, "Rebuild All IMG Files",
                    f"Rebuild all IMG files in current directory?\n\n{base_dir}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )

                if use_current_dir == QMessageBox.StandardButton.Cancel:
                    return
                elif use_current_dir == QMessageBox.StandardButton.No:
                    base_dir = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
                    if not base_dir:
                        return
            else:
                base_dir = QFileDialog.getExistingDirectory(self, "Select Directory with IMG Files")
                if not base_dir:
                    return

            # Call the main rebuild_all_img method with the selected directory
            self.rebuild_all_img_in_directory(base_dir)

        except Exception as e:
            error_msg = f"Error in rebuild all with directory selection: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Rebuild All Error", error_msg)

    def rebuild_all_img_in_directory(self, directory):
        """Rebuild all IMG files in specified directory"""
        try:
            # Find all IMG files in directory
            img_files = []
            for file in os.listdir(directory):
                if file.lower().endswith('.img'):
                    img_files.append(os.path.join(directory, file))

            if not img_files:
                QMessageBox.information(self, "No IMG Files", "No IMG files found in selected directory")
                return

            # Confirm operation
            reply = QMessageBox.question(
                self, "Rebuild All",
                f"Rebuild {len(img_files)} IMG files in directory?\n\n{directory}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            self.log_message(f"Rebuilding {len(img_files)} IMG files...")

            # Show progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(0, "Rebuilding all IMG files...")

            rebuilt_count = 0
            failed_files = []

            for i, img_file in enumerate(img_files):
                progress = int((i + 1) * 100 / len(img_files))
                file_name = os.path.basename(img_file)

                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(progress, f"Rebuilding {file_name}")

                try:
                    # Load IMG file
                    img = IMGFile()
                    if not img.load_from_file(img_file):
                        failed_files.append(f"{img_file}: Failed to load")
                        continue

                    # Check if rebuild method exists and attempt rebuild
                    if hasattr(img, 'rebuild'):
                        if img.rebuild():
                            rebuilt_count += 1
                            self.log_message(f"✅ Rebuilt: {file_name}")
                        else:
                            failed_files.append(f"{file_name}: Rebuild method failed")
                    elif hasattr(img, 'save'):
                        # Alternative: try save method
                        if img.save():
                            rebuilt_count += 1
                            self.log_message(f"✅ Saved: {file_name}")
                        else:
                            failed_files.append(f"{file_name}: Save method failed")
                    else:
                        failed_files.append(f"{file_name}: No rebuild/save method available")

                    # Clean up
                    if hasattr(img, 'close'):
                        img.close()

                except Exception as e:
                    failed_files.append(f"{file_name}: {str(e)}")
                    self.log_message(f"❌ Error rebuilding {file_name}: {str(e)}")

            # Hide progress
            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, f"Rebuild complete: {rebuilt_count}/{len(img_files)}")

            # Show results
            self.log_message(f"✅ Rebuild all complete: {rebuilt_count}/{len(img_files)} files rebuilt")

            if failed_files:
                # Show detailed results with failures
                failed_list = "\n".join(failed_files[:10])
                if len(failed_files) > 10:
                    failed_list += f"\n... and {len(failed_files) - 10} more failures"

                QMessageBox.warning(
                    self, "Rebuild All Results",
                    f"Rebuild completed with some issues:\n\n"
                    f"✅ Successfully rebuilt: {rebuilt_count} files\n"
                    f"❌ Failed: {len(failed_files)} files\n\n"
                    f"Failed files:\n{failed_list}"
                )
            else:
                # All successful
                QMessageBox.information(
                    self, "Rebuild All Complete",
                    f"✅ Successfully rebuilt all {rebuilt_count} IMG files!"
                )

        except Exception as e:
            error_msg = f"Error in rebuild_all_img_in_directory: {str(e)}"
            self.log_message(f"❌ {error_msg}")

            if hasattr(self.gui_layout, 'show_progress'):
                self.gui_layout.show_progress(-1, "Rebuild all failed")

            QMessageBox.critical(self, "Rebuild All Error", error_msg)

    def _update_ui_for_no_img(self):
        """Update UI when no IMG file is loaded"""
        try:
            # Clear current data
            self.current_img = None
            self.current_col = None

            # Update window title
            self.setWindowTitle("IMG Factory 1.5")

            # Clear table if it exists
            if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
                self.gui_layout.table.setRowCount(0)

            # Update status
            if hasattr(self, 'gui_layout'):
                if hasattr(self.gui_layout, 'show_progress'):
                    self.gui_layout.show_progress(-1, "Ready")
                if hasattr(self.gui_layout, 'update_img_info'):
                    self.gui_layout.update_img_info("No IMG loaded")

            # Reset any status labels
            if hasattr(self, 'file_path_label'):
                self.file_path_label.setText("No file loaded")
            if hasattr(self, 'version_label'):
                self.version_label.setText("---")
            if hasattr(self, 'entry_count_label'):
                self.entry_count_label.setText("0")

            self.log_message("📭 UI cleared - no file loaded")

        except Exception as e:
            self.log_message(f"❌ Error updating UI for no IMG: {str(e)}")

class MinimalSettings:
    def __init__(self):
        self.current_settings = {
            "theme": "img_factory",
            "font_family": "Arial",
            "font_size": 9,
            "debug_mode": False
        }
        self.themes = {
            "img_factory": {
                "name": "IMG Factory Default",
                "colors": {
                    "background": "#f0f0f0",
                    "text": "#000000"
                }
            }
        }
        self._loading = False

    def get_stylesheet(self):
        """Return basic stylesheet without recursion"""
        if self._loading:
            return "QWidget { background-color: #f0f0f0; }"

        try:
            self._loading = True
            theme_name = self.current_settings.get("theme", "img_factory")
            theme = self.themes.get(theme_name, self.themes["img_factory"])
            colors = theme.get("colors", {})

            bg = colors.get("background", "#f0f0f0")
            text = colors.get("text", "#000000")

            return f"""
            QMainWindow {{
                background-color: {bg};
                color: {text};
            }}
            QPushButton {{
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                padding: 4px;
                color: {text};
            }}
            QTableWidget {{
                background-color: {bg};
                color: {text};
                gridline-color: #c0c0c0;
            }}
            """
        finally:
            self._loading = False

    def load_settings(self):
        pass

    def save_settings(self):
        pass

    def get_setting(self, key, default=None):
        return self.current_settings.get(key, default)

    def set_setting(self, key, value):
        self.current_settings[key] = value

print("🛡️ Theme loop protection enabled")

# NOW import the rest normally...
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt

# Test that PyQt works
print("✅ PyQt6 import successful")

# Create a simple test to check for segfaults
def test_basic_qt():
    """Test basic Qt functionality"""
    try:
        # Create minimal app
        app = QApplication([])

        # Create minimal window
        window = QMainWindow()
        window.setWindowTitle("IMG Factory 1.5 - Safe Mode")
        window.setMinimumSize(400, 300)

        # Apply minimal theme
        window.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")

        print("✅ Basic Qt test passed")
        return True

    except Exception as e:
        print(f"❌ Basic Qt test failed: {e}")
        return False

# Run the test
if __name__ == "__main__":
    if test_basic_qt():
        print("🚀 Safe to proceed with full application")
    else:
        print("💥 Basic Qt test failed - check Qt installation")
        sys.exit(1)


# Application Entry Point and Main Function
def main():
    """Main application entry point"""
    try:
        print("🚀 Starting IMG Factory 1.5...")

        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("IMG Factory 1.5")
        app.setApplicationVersion("1.5.0")
        app.setOrganizationName("X-Seti")

        settings = MinimalSettings()

        # Set application icon if available
        try:
            app_icon = QIcon("icon.ico")
            app.setWindowIcon(app_icon)
        except:
            pass  # Icon not critical

        # Load settings with fallback
        try:
            print("📚 Loading application settings...")
            settings = AppSettings()
            settings.load_settings()

            if not hasattr(settings, 'get_stylesheet'):
                raise AttributeError("AppSettings missing get_stylesheet method")

        except Exception as e:
            print(f"⚠️ Could not load settings: {str(e)}")
            # Use minimal fallback settings
            class DummySettings:
                def __init__(self):
                    self.current_settings = {
                        "theme": "img_factory",
                        "font_family": "Arial",
                        "font_size": 9,
                        "show_tooltips": True,
                        "auto_save": True,
                        "debug_mode": False
                    }
                    self.themes = {
                        "img_factory": {
                            "colors": {
                                "background": "#f0f0f0",
                                "text": "#000000",
                                "button_text_color": "#000000"
                            }
                        }
                    }

                def get_stylesheet(self):
                    return "QMainWindow { background-color: #f0f0f0; }"

                def get_theme(self, theme_name=None):
                    return self.themes.get("img_factory", {"colors": {}})

                def get_setting(self, key, default=None):
                    return self.current_settings.get(key, default)

                def set_setting(self, key, value):
                    self.current_settings[key] = value

                def load_settings(self):
                    pass

                def save_settings(self):
                    pass

            settings = DummySettings()
            print("📝 Using fallback settings - theme system may be limited")

        # Create main window
        print("🏠 Creating main window...")
        window = IMGFactoryMainWindow()
        window.app_settings = settings

        # Apply theme
        try:
            apply_theme_to_app(settings, window)
        except Exception as e:
            print(f"⚠️ Theme application failed: {e}")

        # Show window
        print("🖥️ Showing main window...")
        window.show()

        # Log startup complete
        window.log_message("🎉 IMG Factory 1.5 started successfully!")
        window.log_message(f"📂 Working directory: {os.getcwd()}")

        print("✅ IMG Factory 1.5 startup complete")

        # Run application
        return app.exec()

    except Exception as e:
        print(f"💥 Fatal error in main(): {str(e)}")
        import traceback
        traceback.print_exc()

        # Try to show error dialog
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            QMessageBox.critical(
                None, "IMG Factory Startup Error",
                f"A fatal error occurred during startup:\n\n{str(e)}\n\nCheck console for details."
            )
        except:
            pass  # If even the error dialog fails, just exit

        return 1


def check_dependencies():
    """Check for required dependencies"""
    try:
        print("🔍 Checking dependencies...")

        # Check PyQt6
        try:
            from PyQt6.QtWidgets import QApplication
            print("  ✅ PyQt6 - OK")
        except ImportError:
            print("  ❌ PyQt6 - MISSING")
            return False

        # Check paths
        current_dir = Path(__file__).parent
        components_dir = current_dir / "components"
        gui_dir = current_dir / "gui"
        utils_dir = current_dir / "utils"

        dirs_to_check = [
            ("components", components_dir),
            ("gui", gui_dir),
            ("utils", utils_dir)
        ]

        for name, path in dirs_to_check:
            if path.exists():
                py_files = len(list(path.glob("*.py")))
                print(f"  ✅ {name}/ - {py_files} Python files")
            else:
                print(f"  ❌ {name}/ - MISSING")
                return False

        print("✅ All dependencies OK")
        return True

    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False


def show_startup_info():
    """Show startup information"""
    print("=" * 50)
    print("IMG Factory 1.5")
    print("GTA IMG Archive Management Tool")
    print("Credit: MexUK 2007 (Original)")
    print("Enhanced by: X-Seti 2025")
    print("=" * 50)


if __name__ == "__main__":
    # Show startup info
    show_startup_info()

    # Check dependencies
    if not check_dependencies():
        print("💥 Dependency check failed - cannot start")
        sys.exit(1)

if test_basic_qt():
    print("🚀 Safe to proceed with full application")
else:
    print("💥 Basic Qt test failed - check Qt installation")
    sys.exit(1)

    # Run main application
    sys.exit(main())
