#this belongs in core/ open_img.py - Version: 2
# X-Seti - September27 2025 - IMG Factory 1.5 - Open Functions with TXD Support

"""
IMG Factory Open Functions - Now supports IMG, COL, and TXD files
"""

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

def _detect_and_open_file(self, file_path: str) -> bool: #vers 6
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
        elif file_ext == '.txd':
            self._load_txd_file(file_path)
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

        # Check for TXD signature
        elif header[:4] == b'\x16\x00\x00\x00':
            self.log_message(f"🔍 Detected TXD file by signature")
            self._load_txd_file(file_path)
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


def open_file_dialog(self): #vers 5
    """Unified file dialog for IMG, COL, and TXD files"""
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Open Archive", "",
        "All Supported (*.img *.col *.txd);;IMG Archives (*.img);;COL Archives (*.col);;TXD Textures (*.txd);;All Files (*)")

    if file_path:
        self.load_file_unified(file_path)


def _detect_file_type(self, file_path: str) -> str: #vers 4
    """Detect file type by extension and content"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.img':
            return "IMG"
        elif file_ext == '.col':
            return "COL"
        elif file_ext == '.txd':
            return "TXD"

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

        # Check for TXD signature
        elif header[:4] == b'\x16\x00\x00\x00':
            return "TXD"

        # Default to IMG for unknown formats
        return "IMG"

    except Exception as e:
        self.log_message(f"❌ Error detecting file type: {str(e)}")
        return "UNKNOWN"


def _load_txd_file(self, file_path: str): #vers 1
    """Load TXD file and open in TXD Workshop"""
    try:
        self.log_message(f"🖼️ Loading TXD file: {os.path.basename(file_path)}")

        # Open TXD Workshop with this file
        from components.Txd_Editor.txd_workshop import open_txd_workshop
        workshop = open_txd_workshop(self, file_path)

        if workshop:
            self.log_message(f"✅ TXD Workshop opened: {os.path.basename(file_path)}")
        else:
            self.log_message(f"❌ Failed to open TXD Workshop")

    except ImportError:
        self.log_message(f"❌ TXD Workshop not found")
        QMessageBox.warning(self, "TXD Support",
            "TXD Workshop not available. Please ensure components/Txd_Editor/ exists.")
    except Exception as e:
        self.log_message(f"❌ Error loading TXD: {str(e)}")
        QMessageBox.critical(self, "Error", f"Failed to load TXD file: {str(e)}")
