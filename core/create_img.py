#this belongs in core/ create_img.py - Version: 1
# X-Seti - July16 2025 - IMG Factory 1.5 - Img Create Functions

"""
IMG Factory Create Img Functions
"""
import os
import shutil
from typing import Optional, Dict, Any, List, Tuple
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog, QDialog
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from core.img_formats import GameSpecificIMGDialog, IMGCreator

#create_new_img
#detect_and_open_file
#open_file_dialog
#detect_file_type


def create_new_img(self): #vers 5
    """Show new IMG creation dialog - FIXED: No signal connections"""
    try:
        dialog = GameSpecificIMGDialog(self)
        dialog.template_manager = self.template_manager

        # Execute dialog and check result
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the output path from the dialog
            if hasattr(dialog, 'output_path') and dialog.output_path:
                output_path = dialog.output_path
                self.log_message(f"✅ Created: {os.path.basename(output_path)}")

                # Load the created IMG file in a new tab
                self._load_img_file_in_new_tab(output_path)
    except Exception as e:
        self.log_message(f"❌ Error creating new IMG: {str(e)}")

def detect_and_open_file(self, file_path: str) -> bool: #vers 5
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


def open_file_dialog(self): #vers 4
    """Unified file dialog for IMG and COL files"""
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Open IMG/COL Archive", "",
        "All Supported (*.img *.col);;IMG Archives (*.img);;COL Archives (*.col);;All Files (*)")

    if file_path:
        self.load_file_unified(file_path)


def detect_file_type(self, file_path: str) -> str: #vers 3
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


__all__ = [
    'create_new_img',
    'detect_and_open_file',
    'open_file_dialog',
    'detect_file_type'
]
