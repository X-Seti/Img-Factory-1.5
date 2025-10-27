#this belongs in components/Img_Factory/img_factory_logging.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - Logging and Debug Methods

"""
Logging and Debug Methods
Handles all logging, debug output, and debug settings functionality
"""

from typing import Optional
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
import os
import struct

##Methods list -
# _append_log_message
# debug_img_before_loading
# log_message
# show_debug_settings


def log_message(self, message: str): #vers 2
    """Optimized logging that works before GUI is ready"""
    try:
        # Check if GUI is ready
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'log') and self.gui_layout.log:
            # Use QTimer to defer log updates to prevent blocking
            QTimer.singleShot(0, lambda: self._append_log_message(message))
        else:
            # Fallback to console if GUI not ready
            print(f"LOG: {message}")
    except Exception:
        print(f"LOG: {message}")

def _append_log_message(self, message: str): #vers 1
    """Internal log message append"""
    try:
        if hasattr(self.gui_layout, 'log') and self.gui_layout.log:
            self.gui_layout.log.append(message)
            # Scroll to bottom
            scrollbar = self.gui_layout.log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    except Exception:
        pass

def debug_img_before_loading(self, file_path): #vers 1
    """Quick debug before loading IMG"""
    try:
        file_size = os.path.getsize(file_path)
        self.log_message(f"Debug: File size = {file_size:,} bytes")

        with open(file_path, 'rb') as f:
            first_8_bytes = f.read(8)
            self.log_message(f"Debug: First 8 bytes = {first_8_bytes.hex()}")

            if first_8_bytes.startswith(b'VER2'):
                entry_count = struct.unpack('<I', first_8_bytes[4:8])[0]
                self.log_message(f"Debug: V2 entry count = {entry_count:,}")
            else:
                potential_v1_entries = file_size // 32
                self.log_message(f"Debug: Potential V1 entries = {potential_v1_entries:,}")

    except Exception as e:
        self.log_message(f"Debug failed: {e}")

def show_debug_settings(self): #vers 1
    """Show debug settings dialog"""
    try:
        # Try to show proper debug settings if available
        from utils.app_settings_system import SettingsDialog
        if hasattr(self, 'app_settings'):
            dialog = SettingsDialog(self.app_settings, self)
            dialog.exec()
        else:
            QMessageBox.information(self, "Debug Settings", "Debug settings: Use F12 to toggle performance mode")
    except ImportError:
        QMessageBox.information(self, "Debug Settings", "Debug settings: Use F12 to toggle performance mode")


def _append_log_message(self, message: str): #vers 1
    """Internal log message append"""
    try:
        if hasattr(self.gui_layout, 'log') and self.gui_layout.log:
            self.gui_layout.log.append(message)
            # Scroll to bottom
            scrollbar = self.gui_layout.log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    except Exception:
        pass


__all__ = [
    'log_message',
    '_append_log_message',
    'debug_img_before_loading',
    'show_debug_settings'
]
