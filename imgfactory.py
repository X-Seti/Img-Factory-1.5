#!/usr/bin/env python3
"""
IMG Factory 2.0 - Main Application Entry Point
Clean Qt6-based implementation for IMG archive management
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QMenuBar, QStatusBar,
    QProgressBar, QHeaderView, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView, QTreeWidget, QTreeWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap

# Import components
try:
    from components.img_core_classes import IMGFile, IMGEntry, IMGVersion, format_file_size
    from components.img_creator import NewIMGDialog
    from components.img_templates import IMGTemplateManager, TemplateManagerDialog
    from components.img_manager import IMGFile, IMGVersion, Platform
    from components.img_validator import IMGValidator
    print("Pastel Theme imported successfully")
    from gui.pastel_button_theme import apply_pastel_theme_to_buttons
except ImportError as e:
    print(f"Failed to import components: {e}")
    print("Make sure all component files are in the components/ directory")
    sys.exit(1)


class IMGLoadThread(QThread):
    """Background thread for loading IMG files"""
    progress_updated = pyqtSignal(int, str)  # progress, status
    loading_finished = pyqtSignal(object)    # IMGFile object
    loading_error = pyqtSignal(str)          # error message
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress_updated.emit(10, "Opening file...")
            
            # Create IMG file instance
            img_file = IMGFile(self.file_path)
            
            self.progress_updated.emit(30, "Detecting format...")
            
            # Open and parse file
            if not img_file.open():
                self.loading_error.emit(f"Failed to open IMG file: {self.file_path}")
                return
            
            self.progress_updated.emit(80, "Loading entries...")
            
            # Validate the loaded file
            validation = IMGValidator.validate_img_file(img_file)
            if not validation.is_valid:
                self.loading_error.emit(f"IMG file validation failed: {validation.get_summary()}")
                return
            
            self.progress_updated.emit(100, "Complete")
            self.loading_finished.emit(img_file)
            
        except Exception as e:
            self.loading_error.emit(f"Error loading IMG file: {str(e)}")


class ExportThread(QThread):
    """Background thread for exporting files"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    export_finished = pyqtSignal(int, int)        # success_count, error_count
    export_error = pyqtSignal(str)                # error message
    
    def __init__(self, img_file: IMGFile, entries: List[IMGEntry], export_dir: str):
        super().__init__()
        self.img_file = img_file
        self.entries = entries
        self.export_dir = export_dir
        self.should_stop = False
    
    def stop_export(self):
        self.should_stop = True
    
    def run(self):
        success_count = 0
        error_count = 0
        total_files = len(self.entries)
        
        try:
            for i, entry in enumerate(self.entries):
                if self.should_stop:
                    break
                
                try:
                    self.progress_updated.emit(i, total_files, entry.name)
                    
                    # Get entry data
                    data = entry.get_data()
                    
                    # Write to file
                    output_path = os.path.join(self.export_dir, entry.name)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Export error for {entry.name}: {e}")
            
            self.progress_updated.emit(total_files, total_files, "Complete")
            self.export_finished.emit(success_count, error_count)
            
        except Exception as e:
            self.export_error.emit(f"Export failed: {str(e)}")


class IMGFactory(QMainWindow):
    """Main IMG Factory application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMG Factory 2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Application settings
        self.settings = QSettings("IMGFactory", "IMGFactory2")
        
        # Core data
        self.current_img: Optional[IMGFile] = None
        self.template_manager = IMGTemplateManager()
        
        # Background threads
        self.load_thread: Optional[IMGLoadThread] = None
        self.export_thread: Optional[ExportThread] = None
        
        # Initialize UI
        self._create_ui()
        self._connect_signals()
        self._restore_settings()
        
        # Log startup
        self.log_message("IMG Factory 2.0 initialized")
    
    def _create_ui(self):
        """Create the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - IMG content
        left_panel = self._create_content_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Controls
        right_panel = self._create_control_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([800, 400])
        
        main_layout.addWidget(content_splitter)
        
        # Create menu and status bars
        self._create_menu_bar()
        self._create_status_bar()
    
    def _create_content_panel(self) -> QWidget:
        """Create left content panel with IMG info and entries"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # IMG file information
        info_group = QGroupBox("📁 IMG File Information")
        info_layout = QHBoxLayout(info_group)
        
        # File path
        info_layout.addWidget(QLabel("File:"))
        self.file_path_label = QLabel("No file loaded")
        self.file_path_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        info_layout.addWidget(self.file_path_label)
        info_layout.addStretch()
        
        # Version info
        info_layout.addWidget(QLabel("Version:"))
        self.version_label = QLabel("Unknown")
        info_layout.addWidget(self.version_label)
        
        # Entry count
        info_layout.addWidget(QLabel("Entries:"))
        self.entry_count_label = QLabel("0")
        info_layout.addWidget(self.entry_count_label)
        
        layout.addWidget(info_group)
        
        # Content splitter for entries and log
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Entries table
        self._create_entries_table()
        content_splitter.addWidget(self.entries_table)
        
        # Log area
        log_group = QGroupBox("📜 Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(120)
        self.log_output.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
            }
        """)
        log_layout.addWidget(self.log_output)
        
        content_splitter.addWidget(log_group)
        
        # Set content splitter proportions
        content_splitter.setSizes([600, 120])
        
        layout.addWidget(content_splitter)
        
        return panel
    
    def _create_entries_table(self):
        """Create and configure the entries table"""
        self.entries_table = QTableWidget(0, 6)
        self.entries_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Offset", "Version", "Status"
        ])
        
        # Configure table
        self.entries_table.verticalHeader().setVisible(False)
        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)
        
        # Configure column widths
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)    # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Offset
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
    
    def _create_control_panel(self) -> QWidget:
        """Create right control panel"""
        panel = QWidget()
        panel.setMinimumWidth(300)
        layout = QVBoxLayout(panel)
        
        # IMG Operations
        img_group = QGroupBox("🎮 IMG Operations")
        img_layout = QVBoxLayout(img_group)
        
        self.new_img_btn = QPushButton("🆕 New IMG Archive")
        self.new_img_btn.clicked.connect(self.create_new_img)
        img_layout.addWidget(self.new_img_btn)
        
        self.open_img_btn = QPushButton("📂 Open IMG Archive")
        self.open_img_btn.clicked.connect(self.open_img_file)
        img_layout.addWidget(self.open_img_btn)
        
        self.close_img_btn = QPushButton("❌ Close Archive")
        self.close_img_btn.clicked.connect(self.close_img_file)
        self.close_img_btn.setEnabled(False)
        img_layout.addWidget(self.close_img_btn)
        
        img_layout.addWidget(QLabel("—" * 20))
        
        self.rebuild_btn = QPushButton("🔄 Rebuild Archive")
        self.rebuild_btn.clicked.connect(self.rebuild_img)
        self.rebuild_btn.setEnabled(False)
        img_layout.addWidget(self.rebuild_btn)
        
        self.validate_btn = QPushButton("✅ Validate Archive")
        self.validate_btn.clicked.connect(self.validate_img)
        self.validate_btn.setEnabled(False)
        img_layout.addWidget(self.validate_btn)
        
        layout.addWidget(img_group)
        
        # Entry Operations
        entry_group = QGroupBox("📦 Entry Operations")
        entry_layout = QVBoxLayout(entry_group)
        
        self.import_btn = QPushButton("📥 Import Files")
        self.import_btn.clicked.connect(self.import_files)
        self.import_btn.setEnabled(False)
        entry_layout.addWidget(self.import_btn)
        
        self.export_selected_btn = QPushButton("📤 Export Selected")
        self.export_selected_btn.clicked.connect(self.export_selected)
        self.export_selected_btn.setEnabled(False)
        entry_layout.addWidget(self.export_selected_btn)
        
        self.export_all_btn = QPushButton("📤 Export All")
        self.export_all_btn.clicked.connect(self.export_all)
        self.export_all_btn.setEnabled(False)
        entry_layout.addWidget(self.export_all_btn)
        
        entry_layout.addWidget(QLabel("—" * 20))
        
        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.remove_btn.setEnabled(False)
        entry_layout.addWidget(self.remove_btn)
        
        layout.addWidget(entry_group)
        
        # Filter & Search
        filter_group = QGroupBox("🔍 Filter & Search")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Files", "Models (DFF)", "Textures (TXD)", 
            "Collision (COL)", "Animation (IFP)", "Audio", "Scripts"
        ])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.search_input)
        
        layout.addWidget(filter_group)
        
        # Template Management
        template_group = QGroupBox("📋 Templates")
        template_layout = QVBoxLayout(template_group)
        
        self.manage_templates_btn = QPushButton("⚙️ Manage Templates")
        self.manage_templates_btn.clicked.connect(self.manage_templates)
        template_layout.addWidget(self.manage_templates_btn)
        
        layout.addWidget(template_group)
        
        layout.addStretch()
        
        return panel
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("🆕 New IMG Archive...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_img)
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Open IMG Archive...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_img_file)
        file_menu.addAction(open_action)
        
        close_action = QAction("❌ Close Archive", self)
        close_action.triggered.connect(self.close_img_file)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        
        validate_action = QAction("✅ Validate Archive", self)
        validate_action.triggered.connect(self.validate_img)
        tools_menu.addAction(validate_action)
        
        templates_action = QAction("📋 Manage Templates", self)
        templates_action.triggered.connect(self.manage_templates)
        tools_menu.addAction(templates_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("ℹ️ About IMG Factory", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # IMG info
        self.img_status_label = QLabel("No IMG loaded")
        self.status_bar.addPermanentWidget(self.img_status_label)
    
    def _connect_signals(self):
        """Connect UI signals"""
        self.entries_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.entries_table.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _restore_settings(self):
        """Restore application settings"""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore recent files (placeholder)
        # recent_files = self.settings.value("recent_files", [])
    
    def _save_settings(self):
        """Save application settings"""
        self.settings.setValue("geometry", self.saveGeometry())
    
    # Event handlers
    def _on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = len(self.entries_table.selectionModel().selectedRows())
        has_selection = selected_rows > 0
        has_img = self.current_img is not None
        
        # Update button states
        self.export_selected_btn.setEnabled(has_selection and has_img)
        self.remove_btn.setEnabled(has_selection and has_img)
        
        # Update status
        if selected_rows > 0:
            self.status_label.setText(f"{selected_rows} entries selected")
        else:
            self.status_label.setText("Ready")
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on table item"""
        row = item.row()
        name_item = self.entries_table.item(row, 0)
        if name_item and self.current_img:
            entry_name = name_item.text()
            entry = self.current_img.get_entry_by_name(entry_name)
            if entry:
                self.log_message(f"Entry info: {entry.name} ({format_file_size(entry.size)})")
    
    # Core functionality
    def create_new_img(self):
        """Show new IMG creation dialog"""
        dialog = NewIMGDialog(self)
        if hasattr(dialog, 'template_manager'):
            dialog.template_manager = self.template_manager
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Dialog should emit img_created signal with file path
            pass
    
    def open_img_file(self):
        """Open IMG file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open IMG Archive",
            "",
            "IMG Files (*.img *.dir);;All Files (*)"
        )
        
        if file_path:
            self.load_img_file(file_path)
    
    def load_img_file(self, file_path: str):
        """Load IMG file in background thread"""
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.show_progress(True)
        self.status_label.setText("Loading IMG file...")
        
        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._update_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_img_load_error)
        self.load_thread.start()
    
    def _update_load_progress(self, progress: int, status: str):
        """Update loading progress"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def _on_img_loaded(self, img_file: IMGFile):
        """Handle successful IMG loading"""
        self.current_img = img_file
        self.show_progress(False)
        
        # Update UI
        filename = os.path.basename(img_file.file_path)
        self.file_path_label.setText(filename)
        self.version_label.setText(f"IMG {img_file.version.value}")
        self.entry_count_label.setText(str(len(img_file.entries)))
        self.img_status_label.setText(f"IMG {img_file.version.value} - {len(img_file.entries)} entries")
        
        # Enable controls
        self.close_img_btn.setEnabled(True)
        self.rebuild_btn.setEnabled(True)
        self.validate_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_all_btn.setEnabled(True)
        
        # Populate table
        self._populate_entries_table()
        
        self.status_label.setText("IMG file loaded successfully")
        self.log_message(f"Loaded: {filename} ({len(img_file.entries)} entries)")
    
    def _on_img_load_error(self, error_message: str):
        """Handle IMG loading error"""
        self.show_progress(False)
        self.status_label.setText("Failed to load IMG file")
        self.log_error(error_message)
        
        QMessageBox.critical(self, "Error", f"Failed to load IMG file:\n{error_message}")
    
    def _populate_entries_table(self):
        """Populate entries table with IMG data"""
        if not self.current_img:
            return
        
        entries = self.current_img.entries
        self.entries_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Name
            self.entries_table.setItem(row, 0, QTableWidgetItem(entry.name))
            
            # Type
            type_text = entry.extension if entry.extension else "Unknown"
            self.entries_table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # Size
            size_text = format_file_size(entry.size)
            self.entries_table.setItem(row, 2, QTableWidgetItem(size_text))
            
            # Offset
            offset_text = f"0x{entry.offset:X}"
            self.entries_table.setItem(row, 3, QTableWidgetItem(offset_text))
            
            # Version
            version_text = entry.get_version_text()
            self.entries_table.setItem(row, 4, QTableWidgetItem(version_text))
            
            # Status
            status_text = "New" if entry.is_new_entry else "Ready"
            if hasattr(entry, 'is_replaced') and entry.is_replaced:
                status_text = "Modified"
            self.entries_table.setItem(row, 5, QTableWidgetItem(status_text))
            
            # Make all items read-only
            for col in range(6):
                item = self.entries_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        # Reset filters
        self.filter_combo.setCurrentIndex(0)
        self.search_input.clear()
    
    def close_img_file(self):
        """Close current IMG file"""
        if self.current_img:
            self.current_img.close()
            self.current_img = None
            
            # Clear table
            self.entries_table.setRowCount(0)
            
            # Update UI
            self.file_path_label.setText("No file loaded")
            self.version_label.setText("Unknown")
            self.entry_count_label.setText("0")
            self.img_status_label.setText("No IMG loaded")
            
            # Disable controls
            self.close_img_btn.setEnabled(False)
            self.rebuild_btn.setEnabled(False)
            self.validate_btn.setEnabled(False)
            self.import_btn.setEnabled(False)
            self.export_selected_btn.setEnabled(False)
            self.export_all_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            
            self.log_message("IMG file closed")
    
    def rebuild_img(self):
        """Rebuild current IMG file"""
        if not self.current_img:
            return
        
        reply = QMessageBox.question(
            self, "Rebuild IMG",
            "Rebuild the current IMG archive?\n\nThis will save all changes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.status_label.setText("Rebuilding IMG archive...")
                # Placeholder for rebuild functionality
                self.log_message("IMG rebuild not yet implemented")
                QMessageBox.information(self, "Info", "Rebuild functionality coming soon!")
            except Exception as e:
                self.log_error(f"Rebuild error: {str(e)}")
            finally:
                self.status_label.setText("Ready")
    
    def validate_img(self):
        """Validate current IMG file"""
        if not self.current_img:
            QMessageBox.information(self, "Validate", "No IMG file loaded")
            return
        
        try:
            self.status_label.setText("Validating IMG archive...")
            
            # Run validation
            validation = IMGValidator.validate_img_file(self.current_img)
            
            # Show results
            result_text = f"Validation Result: {validation.get_summary()}\n\n"
            result_text += validation.get_details()
            
            if validation.is_valid:
                QMessageBox.information(self, "Validation Result", result_text)
            else:
                QMessageBox.warning(self, "Validation Result", result_text)
            
            self.log_message(f"Validation: {validation.get_summary()}")
            
        except Exception as e:
            self.log_error(f"Validation error: {str(e)}")
        finally:
            self.status_label.setText("Ready")
    
    def import_files(self):
        """Import files into IMG"""
        if not self.current_img:
            return
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            "",
            "All Supported (*.dff *.txd *.col *.ifp *.wav *.scm);;All Files (*)"
        )
        
        if file_paths:
            # Placeholder for import functionality
            self.log_message(f"Import requested for {len(file_paths)} files")
            QMessageBox.information(self, "Info", "Import functionality coming soon!")
    
    def export_selected(self):
        """Export selected entries"""
        if not self.current_img:
            return
        
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Export", "No entries selected")
            return
        
        self._export_entries([row.row() for row in selected_rows])
    
    def export_all(self):
        """Export all entries"""
        if not self.current_img:
            return
        
        entry_count = len(self.current_img.entries)
        if entry_count == 0:
            QMessageBox.information(self, "Export", "No entries to export")
            return
        
        self._export_entries(list(range(entry_count)))
    
    def _export_entries(self, row_indices: List[int]):
        """Export entries by row indices"""
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
        
        # Get entries to export
        entries_to_export = []
        for row in row_indices:
            if row < len(self.current_img.entries):
                entries_to_export.append(self.current_img.entries[row])
        
        if not entries_to_export:
            return
        
        self.show_progress(True)
        self.status_label.setText("Exporting files...")
        
        self.export_thread = ExportThread(self.current_img, entries_to_export, export_dir)
        self.export_thread.progress_updated.connect(self._update_export_progress)
        self.export_thread.export_finished.connect(self._on_export_finished)
        self.export_thread.export_error.connect(self._on_export_error)
        self.export_thread.start()
    
    def _update_export_progress(self, current: int, total: int, filename: str):
        """Update export progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Exporting {current}/{total}: {filename}")
    
    def _on_export_finished(self, success_count: int, error_count: int):
        """Handle export completion"""
        self.show_progress(False)
        self.status_label.setText("Ready")
        
        if error_count == 0:
            message = f"Successfully exported {success_count} files!"
            QMessageBox.information(self, "Export Complete", message)
        else:
            message = f"Export completed with {error_count} errors.\nSuccessfully exported: {success_count} files"
            QMessageBox.warning(self, "Export Complete", message)
        
        self.log_message(f"Export completed: {success_count} files, {error_count} errors")
    
    def _on_export_error(self, error_message: str):
        """Handle export error"""
        self.show_progress(False)
        self.status_label.setText("Ready")
        self.log_error(f"Export failed: {error_message}")
        QMessageBox.critical(self, "Export Error", f"Export failed:\n{error_message}")
    
    def remove_selected(self):
        """Remove selected entries"""
        if not self.current_img:
            return
        
        selected_rows = self.entries_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Remove", "No entries selected")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Remove {len(selected_rows)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Placeholder for remove functionality
            self.log_message(f"Remove requested for {len(selected_rows)} entries")
            QMessageBox.information(self, "Info", "Remove functionality coming soon!")
    
    def apply_filter(self):
        """Apply filter and search to entries table"""
        if not self.current_img:
            return
        
        filter_type = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        for row in range(self.entries_table.rowCount()):
            show_row = True
            
            # Apply type filter
            if filter_type != "All Files":
                type_item = self.entries_table.item(row, 1)
                if type_item:
                    file_type = type_item.text()
                    if filter_type == "Models (DFF)" and file_type != "DFF":
                        show_row = False
                    elif filter_type == "Textures (TXD)" and file_type != "TXD":
                        show_row = False
                    elif filter_type == "Collision (COL)" and file_type != "COL":
                        show_row = False
                    elif filter_type == "Animation (IFP)" and file_type != "IFP":
                        show_row = False
                    elif filter_type == "Audio" and file_type not in ["WAV", "MP3"]:
                        show_row = False
                    elif filter_type == "Scripts" and file_type not in ["SCM", "CS"]:
                        show_row = False
            
            # Apply search filter
            if show_row and search_text:
                name_item = self.entries_table.item(row, 0)
                if name_item and search_text not in name_item.text().lower():
                    show_row = False
            
            self.entries_table.setRowHidden(row, not show_row)
    
    def manage_templates(self):
        """Show template manager dialog"""
        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>IMG Factory 2.0</h2>
<p>Modern IMG archive manager for GTA and related games</p>

<h3>Features:</h3>
<ul>
<li>Support for IMG versions 1, 2, 3, and Fastman92</li>
<li>Template system for quick archive creation</li>
<li>Import/Export functionality</li>
<li>Archive validation and repair</li>
<li>Cross-platform Qt6-based interface</li>
</ul>

<h3>Supported Games:</h3>
<ul>
<li>Grand Theft Auto III</li>
<li>Grand Theft Auto Vice City</li>
<li>Grand Theft Auto San Andreas</li>
<li>Grand Theft Auto IV</li>
<li>Bully</li>
</ul>

<p><b>Based on the original IMG Factory by MexUK</b><br>
Python Qt6 implementation</p>
        """
        
        QMessageBox.about(self, "About IMG Factory", about_text)
    
    # Utility methods
    def show_progress(self, visible: bool = True):
        """Show or hide progress bar"""
        self.progress_bar.setVisible(visible)
        if not visible:
            self.progress_bar.setValue(0)
    
    def log_message(self, message: str):
        """Add message to log output"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        self.log_output.ensureCursorVisible()
    
    def log_error(self, message: str):
        """Add error message to log output"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] <span style='color: red;'>ERROR:</span> {message}")
        self.log_output.ensureCursorVisible()
    
    # Application lifecycle
    def closeEvent(self, event):
        """Handle application close event"""
        self._save_settings()
        
        # Stop any running threads
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.terminate()
            self.load_thread.wait(3000)
        
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.stop_export()
            self.export_thread.wait(3000)
        
        # Close IMG file
        if self.current_img:
            self.current_img.close()
        
        super().closeEvent(event)


def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("IMG Factory")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("IMG Factory")
    
    # Set modern style
    app.setStyle("Fusion")
    
    # Apply dark theme (optional)
    apply_dark_theme(app)
    
    # Create and show main window
    try:
        window = IMGFactory()
        window.show()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path) and file_path.lower().endswith(('.img', '.dir')):
                QTimer.singleShot(100, lambda: window.load_img_file(file_path))
        
        # Run application
        return app.exec()
        
    except Exception as e:
        QMessageBox.critical(None, "Startup Error", f"Failed to start IMG Factory:\n{str(e)}")
        return 1


def apply_dark_theme(app):
    """Apply a modern dark theme to the application"""
    dark_stylesheet = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #555555;
        border-radius: 5px;
        margin-top: 1ex;
        padding-top: 5px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    
    QPushButton {
        background-color: #404040;
        border: 2px solid #555555;
        border-radius: 6px;
        padding: 6px 12px;
        min-height: 20px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #505050;
        border-color: #777777;
    }
    
    QPushButton:pressed {
        background-color: #303030;
    }
    
    QPushButton:disabled {
        background-color: #2b2b2b;
        border-color: #333333;
        color: #666666;
    }
    
    QTableWidget {
        background-color: #353535;
        alternate-background-color: #404040;
        gridline-color: #555555;
        border: 1px solid #555555;
    }
    
    QHeaderView::section {
        background-color: #404040;
        padding: 4px;
        border: 1px solid #555555;
        font-weight: bold;
    }
    
    QComboBox {
        background-color: #404040;
        border: 2px solid #555555;
        border-radius: 4px;
        padding: 4px;
        min-width: 6em;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }
    
    QLineEdit {
        background-color: #404040;
        border: 2px solid #555555;
        border-radius: 4px;
        padding: 4px;
    }
    
    QLineEdit:focus {
        border-color: #0078d4;
    }
    
    QTextEdit {
        background-color: #353535;
        border: 1px solid #555555;
    }
    
    QMenuBar {
        background-color: #404040;
        border-bottom: 1px solid #555555;
    }
    
    QMenuBar::item {
        padding: 4px 8px;
    }
    
    QMenuBar::item:selected {
        background-color: #505050;
    }
    
    QMenu {
        background-color: #404040;
        border: 1px solid #555555;
    }
    
    QMenu::item {
        padding: 4px 20px;
    }
    
    QMenu::item:selected {
        background-color: #505050;
    }
    
    QStatusBar {
        background-color: #404040;
        border-top: 1px solid #555555;
    }
    
    QProgressBar {
        border: 2px solid #555555;
        border-radius: 4px;
        background-color: #353535;
    }
    
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 2px;
    }
    
    QSplitter::handle {
        background-color: #555555;
    }
    
    QSplitter::handle:horizontal {
        width: 3px;
    }
    
    QSplitter::handle:vertical {
        height: 3px;
    }
    """
    
    app.setStyleSheet(dark_stylesheet)


if __name__ == "__main__":
    sys.exit(main())
