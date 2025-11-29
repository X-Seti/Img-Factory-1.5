#this belongs in core/ open.py - Version: 8
# X-Seti - November10 2025 - IMG Factory 1.5 - Open Functions with Tab System

"""
IMG Factory Open Functions - Now supports IMG, COL, and TXD files
Uses unified tab system from apps.methods.tab_system.py
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


def _load_img_file(main_window, file_path): #vers 4
    """Load IMG file in new tab using unified tab system"""
    try:
        if hasattr(main_window, '_load_img_file_in_new_tab'):
            main_window._load_img_file_in_new_tab(file_path)
        elif hasattr(main_window, 'load_img_file_in_new_tab'):
            main_window.load_img_file_in_new_tab(file_path)
        else:
            main_window.log_message("Error: No IMG loading method found")
        
        # Check for corresponding IDE file in the same directory
        check_and_prompt_for_ide_file(main_window, file_path)
        
    except Exception as e:
        main_window.log_message(f"Error loading IMG: {str(e)}")


def check_and_prompt_for_ide_file(main_window, img_file_path): #vers 1
    """Check if IDE file exists in same folder as IMG file and prompt user to load it"""
    try:
        import os
        from PyQt6.QtWidgets import QMessageBox
        
        # Get the directory and base name of the IMG file
        img_dir = os.path.dirname(img_file_path)
        img_basename = os.path.splitext(os.path.basename(img_file_path))[0]
        
        # Look for corresponding IDE file (same name as IMG file)
        ide_file_path = os.path.join(img_dir, img_basename + ".ide")
        
        # Check if IDE file exists
        if os.path.exists(ide_file_path):
            # Ask user if they want to load the IDE file
            reply = QMessageBox.question(
                main_window,
                "IDE File Found",
                f"IDE file found with IMG file:\n{os.path.basename(ide_file_path)}\n\n"
                f"Do you want to load this IDE file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Load the IDE file using the IDE editor
                from apps.components.Ide_Editor.ide_editor import open_ide_editor
                editor = open_ide_editor(main_window)
                if editor:
                    editor.load_ide_file(ide_file_path)
                    main_window.log_message(f"✅ Loaded IDE file: {os.path.basename(ide_file_path)}")
                else:
                    main_window.log_message(f"❌ Failed to open IDE editor for: {os.path.basename(ide_file_path)}")
            else:
                main_window.log_message(f"ℹ️ IDE file available but not loaded: {os.path.basename(ide_file_path)}")
        else:
            # Look for any IDE file in the same directory (case-insensitive)
            for file in os.listdir(img_dir):
                if file.lower().endswith('.ide'):
                    # Ask user if they want to load this IDE file
                    reply = QMessageBox.question(
                        main_window,
                        "IDE File Found",
                        f"IDE file found in same folder:\n{file}\n\n"
                        f"Do you want to load this IDE file?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        ide_path = os.path.join(img_dir, file)
                        from apps.components.Ide_Editor.ide_editor import open_ide_editor
                        editor = open_ide_editor(main_window)
                        if editor:
                            editor.load_ide_file(ide_path)
                            main_window.log_message(f"✅ Loaded IDE file: {file}")
                        else:
                            main_window.log_message(f"❌ Failed to open IDE editor for: {file}")
                    else:
                        main_window.log_message(f"ℹ️ IDE file available but not loaded: {file}")
                    break  # Only check for one IDE file
                    
    except Exception as e:
        main_window.log_message(f"⚠️ Error checking for IDE file: {str(e)}")


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
    'open_file_dialog',
    'check_and_prompt_for_ide_file'
]
