#!/usr/bin/env python3
"""
Test script for the new hex editor with three panels
"""

import sys
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from apps.components.Hex_Editor.Hex_Editor_Panel import HexEditorDialog

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Hex Editor")
        self.resize(800, 600)
        
        # Create a central widget with a button to open the hex editor
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        open_hex_btn = QPushButton("Open Hex Editor")
        open_hex_btn.clicked.connect(self.open_hex_editor)
        layout.addWidget(open_hex_btn)
        
        self.setCentralWidget(central_widget)
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
        # Write some test data
        test_data = b"Hello, World! This is a test file for the hex editor. ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.temp_file.write(test_data)
        self.temp_file.close()
        
    def open_hex_editor(self):
        # Create and show the hex editor dialog
        dialog = HexEditorDialog(self, self.temp_file.name)
        dialog.exec()
        
    def log_message(self, message):
        """Mock log message function"""
        print(f"LOG: {message}")
        
    def show_message_box(self, title, text, buttons, default_button):
        """Mock message box function"""
        print(f"Message Box: {title} - {text}")
        return default_button

def main():
    app = QApplication(sys.argv)
    
    main_window = TestMainWindow()
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()