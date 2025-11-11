#this belongs in core/ open.py - Version: 8
# X-Seti - November10 2025 - IMG Factory 1.5 - Open Functions with Tab System

"""
IMG Factory Open Functions - Now supports IMG, COL, and TXD files
Uses unified tab system from methods/tab_system.py
"""

import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox

##Methods list -
# _detect_and_open_file
# _detect_file_type
# _load_col_file
# _load_img_file
# _load_txd_file
# open_file_dialog

def open_file_dialog(main_window): #vers 12
    """Unified file dialog for IMG, COL, and TXD files"""
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Open Archive",
        "",
        "All Supported (*.img *.col *.txd);;IMG Archives (*.img);;COL Archives (*.col);;TXD Textures (*.txd);;All Files (*)"
    )

    if file_path:
        file_ext = os.path.splitext(file_path)[1].lower()
        options=QFileDialog.Option.DontUseNativeDialog
        if file_ext == '.txd':
            _load_txd_file(main_window, file_path)
        elif file_ext == '.col':
            _load_col_file(main_window, file_path)
        else:
            _load_img_file(main_window, file_path)


def _load_img_file(main_window, file_path): #vers 3
    """Load IMG file in new tab using unified tab system"""
    try:
        if hasattr(main_window, '_load_img_file_in_new_tab'):
            main_window._load_img_file_in_new_tab(file_path)
        elif hasattr(main_window, 'load_img_file_in_new_tab'):
            main_window.load_img_file_in_new_tab(file_path)
        else:
            main_window.log_message("Error: No IMG loading method found")
    except Exception as e:
        main_window.log_message(f"Error loading IMG: {str(e)}")


def _load_col_file(main_window, file_path): #vers 3
    """Load COL file in new tab using unified tab system"""
    try:
        if hasattr(main_window, '_load_col_file_in_new_tab'):
            main_window._load_col_file_in_new_tab(file_path)
        elif hasattr(main_window, 'load_col_file_in_new_tab'):
            main_window.load_col_file_in_new_tab(file_path)
        elif hasattr(main_window, 'load_col_file_safely'):
            main_window.load_col_file_safely(file_path)
        else:
            main_window.log_message("Error: No COL loading method found")
    except Exception as e:
        main_window.log_message(f"Error loading COL: {str(e)}")


def _load_txd_file(main_window, file_path): #vers 2
    """Load TXD file in new tab using unified tab system"""
    try:
        main_window.log_message(f"Loading TXD file: {os.path.basename(file_path)}")

        # Check if main window has a TXD tab loading method
        if hasattr(main_window, '_load_txd_file_in_new_tab'):
            main_window._load_txd_file_in_new_tab(file_path)
            return
        elif hasattr(main_window, 'load_txd_file_in_new_tab'):
            main_window.load_txd_file_in_new_tab(file_path)
            return

        # Fallback: Open TXD Workshop window
        from apps.components.Txd_Editor.txd_workshop import open_txd_workshop
        workshop = open_txd_workshop(main_window, file_path)

        if workshop:
            if not hasattr(main_window, 'txd_workshops'):
                main_window.txd_workshops = []
            main_window.txd_workshops.append(workshop)
            main_window.log_message(f"TXD Workshop opened: {os.path.basename(file_path)}")

    except Exception as e:
        main_window.log_message(f"Error loading TXD: {str(e)}")


def _detect_and_open_file(main_window, file_path): #vers 9
    """Detect file type and open with appropriate handler"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.img':
            _load_img_file(main_window, file_path)
            return True
        elif file_ext == '.col':
            _load_col_file(main_window, file_path)
            return True
        elif file_ext == '.txd':
            _load_txd_file(main_window, file_path)
            return True

        with open(file_path, 'rb') as f:
            header = f.read(16)

        if len(header) < 4:
            return False

        if header[:4] in [b'VER2', b'VER3']:
            main_window.log_message("Detected IMG file by signature")
            _load_img_file(main_window, file_path)
            return True
        elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
            main_window.log_message("Detected COL file by signature")
            _load_col_file(main_window, file_path)
            return True
        elif header[:4] == b'\x16\x00\x00\x00':
            main_window.log_message("Detected TXD file by signature")
            _load_txd_file(main_window, file_path)
            return True
        elif len(header) >= 8:
            main_window.log_message("Attempting to open as IMG file")
            _load_img_file(main_window, file_path)
            return True

        return False

    except Exception as e:
        main_window.log_message(f"Error detecting file type: {str(e)}")
        return False


def _detect_file_type(main_window, file_path): #vers 7
    """Detect file type by extension and content"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.img':
            return "IMG"
        elif file_ext == '.col':
            return "COL"
        elif file_ext == '.txd':
            return "TXD"

        with open(file_path, 'rb') as f:
            header = f.read(16)

        if len(header) < 4:
            return "UNKNOWN"

        if header[:4] in [b'VER2', b'VER3']:
            return "IMG"
        elif header[:4] in [b'COLL', b'COL\x02', b'COL\x03', b'COL\x04']:
            return "COL"
        elif header[:4] == b'\x16\x00\x00\x00':
            return "TXD"

        return "IMG"

    except Exception as e:
        main_window.log_message(f"Error detecting file type: {str(e)}")
        return "UNKNOWN"


__all__ = [
    '_detect_and_open_file',
    '_detect_file_type',
    '_load_col_file',
    '_load_img_file',
    '_load_txd_file',
    'open_file_dialog'
]
