#this belongs in gui/ status_bar.py
# $vers" X-Seti - June26, 2025 - Img Factory 1.5"
# $hist" Credit MexUK 2007 Img Factory 1.2"

#!/usr/bin/env python3
"""
IMG Factory Status Bar - Status Information and Progress Display
Handles status bar creation, progress bars, and status updates
"""

from PyQt6.QtWidgets import (
    QStatusBar, QLabel, QProgressBar, QPushButton, QWidget, 
    QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from datetime import datetime


class StatusBarManager:
    """Manages status bar components and updates"""
    
    def __init__(self, status_bar):
        self.status_bar = status_bar
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._clear_temporary_status)
        self._permanent_status = "Ready"
    
    def show_message(self, message, timeout=0):
        """Show a message in the status bar"""
        self.status_bar.showMessage(message, timeout)
        
        if timeout > 0:
            self._status_timer.start(timeout)
    
    def show_permanent_message(self, message):
        """Show a permanent message"""
        self._permanent_status = message
        self.status_bar.showMessage(message)
    
    def _clear_temporary_status(self):
        """Clear temporary status and restore permanent status"""
        self.status_bar.showMessage(self._permanent_status)


class IMGStatusWidget(QWidget):
    """Widget showing IMG file status information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
        self._reset_status()
    
    def _create_ui(self):
        """Create status widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # IMG file indicator
        self.img_icon = QLabel("📁")
        layout.addWidget(self.img_icon)
        
        # File name
        self.file_label = QLabel("No IMG loaded")
        self.file_label.setMinimumWidth(150)
        layout.addWidget(self.file_label)
        
        # Separator
        layout.addWidget(QLabel("|"))
        
        # Entry count
        self.entries_label = QLabel("Entries: 0")
        layout.addWidget(self.entries_label)
        
        # Separator  
        layout.addWidget(QLabel("|"))
        
        # File size
        self.size_label = QLabel("Size: 0 B")
        layout.addWidget(self.size_label)
        
        # Separator
        layout.addWidget(QLabel("|"))
        
        # Version
        self.version_label = QLabel("Version: Unknown")
        layout.addWidget(self.version_label)
    
    def _reset_status(self):
        """Reset to default status"""
        self.img_icon.setText("📁")
        self.file_label.setText("No IMG loaded")
        self.file_label.setStyleSheet("color: #666666;")
        self.entries_label.setText("Entries: 0")
        self.size_label.setText("Size: 0 B")
        self.version_label.setText("Version: Unknown")
    
    def update_img_status(self, img_file=None, filename="", entry_count=0, file_size=0, version="Unknown"):
        """Update IMG status information"""
        if img_file or filename:
            # File loaded
            self.img_icon.setText("📂")
            display_name = filename if filename else (img_file.file_path if img_file else "Unknown")
            
            # Show just filename, not full path
            import os
            if os.path.sep in display_name:
                display_name = os.path.basename(display_name)
            
            self.file_label.setText(display_name)
            self.file_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
            
            self.entries_label.setText(f"Entries: {entry_count}")
            self.size_label.setText(f"Size: {self._format_size(file_size)}")
            self.version_label.setText(f"Version: {version}")
        else:
            # No file loaded
            self._reset_status()
    
    def _format_size(self, size_bytes):
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


class ProgressWidget(QWidget):
    """Progress bar widget with cancel button"""
    
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
        self.setVisible(False)
    
    def _create_ui(self):
        """Create progress widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        
        # Progress label
        self.progress_label = QLabel("Working...")
        self.progress_label.setMinimumWidth(100)
        layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumWidth(200)
        self.progress_bar.setMaximumHeight(16)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setMaximumWidth(20)
        self.cancel_btn.setMaximumHeight(16)
        self.cancel_btn.setToolTip("Cancel operation")
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        layout.addWidget(self.cancel_btn)
    
    def show_progress(self, text="Working...", minimum=0, maximum=100):
        """Show progress bar with text"""
        self.progress_label.setText(text)
        self.progress_bar.setRange(minimum, maximum)
        self.progress_bar.setValue(minimum)
        self.setVisible(True)
    
    def update_progress(self, value, text=None):
        """Update progress value and optional text"""
        self.progress_bar.setValue(value)
        if text:
            self.progress_label.setText(text)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Working...")


def create_status_bar(main_window):
    """Create and setup the status bar"""
    status_bar = QStatusBar()
    main_window.setStatusBar(status_bar)
    
    # Status bar manager
    main_window.status_manager = StatusBarManager(status_bar)
    
    # Main status message (left side)
    main_window.status_label = QLabel("Ready")
    status_bar.addWidget(main_window.status_label)
    
    # Progress widget (center, hidden by default)
    main_window.progress_widget = ProgressWidget()
    status_bar.addWidget(main_window.progress_widget)
    
    # IMG status widget (right side)
    main_window.img_status_widget = IMGStatusWidget()
    status_bar.addPermanentWidget(main_window.img_status_widget)
    
    # Connect progress cancel signal
    if hasattr(main_window, 'cancel_current_operation'):
        main_window.progress_widget.cancel_requested.connect(main_window.cancel_current_operation)
    
    # Add convenience methods to main window
    _add_status_methods(main_window)
    
    return status_bar


def _add_status_methods(main_window):
    """Add status bar convenience methods to main window"""
    
    def show_status(message, timeout=0):
        """Show status message"""
        main_window.status_manager.show_message(message, timeout)
    
    def show_permanent_status(message):
        """Show permanent status message"""
        main_window.status_manager.show_permanent_message(message)
    
    def show_progress(text="Working...", minimum=0, maximum=100):
        """Show progress bar"""
        main_window.progress_widget.show_progress(text, minimum, maximum)
    
    def update_progress(value, text=None):
        """Update progress"""
        main_window.progress_widget.update_progress(value, text)
    
    def hide_progress():
        """Hide progress bar"""
        main_window.progress_widget.hide_progress()
    
    def update_img_status(img_file=None, filename="", entry_count=0, file_size=0, version="Unknown"):
        """Update IMG file status"""
        main_window.img_status_widget.update_img_status(img_file, filename, entry_count, file_size, version)
    
    def set_ready_status():
        """Set status to ready"""
        show_permanent_status("Ready")
        main_window.img_status_widget._reset_status()
    
    # Attach methods to main window
    main_window.show_status = show_status
    main_window.show_permanent_status = show_permanent_status
    main_window.show_progress = show_progress
    main_window.update_progress = update_progress
    main_window.hide_progress = hide_progress
    main_window.update_img_status = update_img_status
    main_window.set_ready_status = set_ready_status


class SelectionStatusWidget(QWidget):
    """Widget showing current selection information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
        self.update_selection(0, 0)
    
    def _create_ui(self):
        """Create selection status UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Selection icon
        layout.addWidget(QLabel("📋"))
        
        # Selection text
        self.selection_label = QLabel("0 of 0 selected")
        layout.addWidget(self.selection_label)
    
    def update_selection(self, selected_count, total_count):
        """Update selection information"""
        if selected_count == 0:
            self.selection_label.setText(f"0 of {total_count} selected")
            self.selection_label.setStyleSheet("color: #666666;")
        elif selected_count == total_count and total_count > 0:
            self.selection_label.setText(f"All {total_count} selected")
            self.selection_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
        else:
            self.selection_label.setText(f"{selected_count} of {total_count} selected")
            self.selection_label.setStyleSheet("color: #1976D2; font-weight: bold;")


class OperationStatusWidget(QWidget):
    """Widget showing current operation status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_ui()
        self.set_idle()
    
    def _create_ui(self):
        """Create operation status UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Status icon
        self.status_icon = QLabel("⚪")
        layout.addWidget(self.status_icon)
        
        # Status text
        self.status_text = QLabel("Idle")
        layout.addWidget(self.status_text)
    
    def set_idle(self):
        """Set status to idle"""
        self.status_icon.setText("⚪")
        self.status_text.setText("Idle")
        self.status_text.setStyleSheet("color: #666666;")
    
    def set_working(self, operation="Working"):
        """Set status to working"""
        self.status_icon.setText("🔄")
        self.status_text.setText(operation)
        self.status_text.setStyleSheet("color: #1976D2;")
    
    def set_success(self, message="Complete"):
        """Set status to success"""
        self.status_icon.setText("✅")
        self.status_text.setText(message)
        self.status_text.setStyleSheet("color: #2E7D32;")
        
        # Auto-clear after 3 seconds
        QTimer.singleShot(3000, self.set_idle)
    
    def set_error(self, message="Error"):
        """Set status to error"""
        self.status_icon.setText("❌")
        self.status_text.setText(message)
        self.status_text.setStyleSheet("color: #D32F2F;")
        
        # Auto-clear after 5 seconds
        QTimer.singleShot(5000, self.set_idle)


def create_enhanced_status_bar(main_window):
    """Create enhanced status bar with additional widgets"""
    status_bar = create_status_bar(main_window)
    
    # Add selection status widget
    main_window.selection_status_widget = SelectionStatusWidget()
    status_bar.addPermanentWidget(main_window.selection_status_widget)
    
    # Add operation status widget
    main_window.operation_status_widget = OperationStatusWidget()
    status_bar.addPermanentWidget(main_window.operation_status_widget)
    
    # Add enhanced methods
    def update_selection_status(selected_count, total_count):
        """Update selection status"""
        main_window.selection_status_widget.update_selection(selected_count, total_count)
    
    def set_operation_status(status, message=""):
        """Set operation status"""
        if status == "idle":
            main_window.operation_status_widget.set_idle()
        elif status == "working":
            main_window.operation_status_widget.set_working(message)
        elif status == "success":
            main_window.operation_status_widget.set_success(message)
        elif status == "error":
            main_window.operation_status_widget.set_error(message)
    
    # Attach enhanced methods
    main_window.update_selection_status = update_selection_status
    main_window.set_operation_status = set_operation_status
    
    return status_bar


class StatusBarTheme:
    """Theme manager for status bar styling"""
    
    @staticmethod
    def apply_theme(status_bar, theme_name="default"):
        """Apply theme to status bar"""
        themes = {
            "default": """
                QStatusBar {
                    background-color: #f0f0f0;
                    border-top: 1px solid #d0d0d0;
                    color: #333333;
                }
                QStatusBar::item {
                    border: none;
                }
            """,
            "dark": """
                QStatusBar {
                    background-color: #2d2d30;
                    border-top: 1px solid #3e3e42;
                    color: #ffffff;
                }
                QStatusBar::item {
                    border: none;
                }
            """,
            "img_factory": """
                QStatusBar {
                    background-color: #fafafa;
                    border-top: 1px solid #dee2e6;
                    color: #212529;
                }
                QStatusBar::item {
                    border: none;
                }
                QLabel {
                    color: #495057;
                }
            """
        }
        
        style = themes.get(theme_name, themes["default"])
        status_bar.setStyleSheet(style)


# Integration helpers
def integrate_with_existing_status_bar(main_window):
    """Integrate with existing status bar if present"""
    if hasattr(main_window, 'statusBar') and main_window.statusBar():
        # Use existing status bar
        existing_bar = main_window.statusBar()
        
        # Add our components to existing bar
        main_window.status_manager = StatusBarManager(existing_bar)
        
        # Add our widgets if space available
        main_window.progress_widget = ProgressWidget()
        existing_bar.addWidget(main_window.progress_widget)
        
        main_window.img_status_widget = IMGStatusWidget()
        existing_bar.addPermanentWidget(main_window.img_status_widget)
        
        # Add methods
        _add_status_methods(main_window)
        
        return existing_bar
    else:
        # Create new status bar
        return create_status_bar(main_window)


# Utility functions
def format_operation_time(seconds):
    """Format operation time for display"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def create_status_context_menu(main_window):
    """Create context menu for status bar"""
    from PyQt6.QtWidgets import QMenu
    
    def show_context_menu(position):
        menu = QMenu(main_window)
        
        # Copy status action
        copy_action = menu.addAction("📋 Copy Status")
        copy_action.triggered.connect(lambda: copy_status_to_clipboard(main_window))
        
        menu.addSeparator()
        
        # Clear status action
        clear_action = menu.addAction("🗑️ Clear Status")
        clear_action.triggered.connect(lambda: main_window.set_ready_status())
        
        # Show log action
        if hasattr(main_window, 'log_widget'):
            log_action = menu.addAction("📜 Show Log")
            log_action.triggered.connect(lambda: main_window.log_widget.show())
        
        menu.exec(main_window.statusBar().mapToGlobal(position))
    
    # Connect context menu
    main_window.statusBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    main_window.statusBar().customContextMenuRequested.connect(show_context_menu)


def copy_status_to_clipboard(main_window):
    """Copy current status information to clipboard"""
    from PyQt6.QtWidgets import QApplication
    
    status_info = []
    
    # Main status
    if hasattr(main_window, 'status_label'):
        status_info.append(f"Status: {main_window.status_label.text()}")
    
    # IMG status
    if hasattr(main_window, 'img_status_widget'):
        widget = main_window.img_status_widget
        status_info.extend([
            f"File: {widget.file_label.text()}",
            f"{widget.entries_label.text()}",
            f"{widget.size_label.text()}",
            f"{widget.version_label.text()}"
        ])
    
    # Selection status
    if hasattr(main_window, 'selection_status_widget'):
        status_info.append(f"Selection: {main_window.selection_status_widget.selection_label.text()}")
    
    clipboard_text = "\n".join(status_info)
    QApplication.clipboard().setText(clipboard_text)
    
    if hasattr(main_window, 'show_status'):
        main_window.show_status("Status copied to clipboard", 2000)