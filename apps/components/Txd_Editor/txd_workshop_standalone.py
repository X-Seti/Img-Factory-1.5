#!/usr/bin/env python3
#this belongs in root /run_txd_workshop.py - Version: 1
# X-Seti - October13 2025 - IMG Factory 1.5 - TXD Workshop Standalone Launcher

"""
TXD Workshop Standalone Launcher
Fixes import paths and launches TXD Workshop as a standalone application
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now imports will work correctly
from components.Txd_Editor.txd_workshop import open_txd_workshop, TXDWorkshop
from PyQt6.QtWidgets import QApplication

def main():
    """Launch TXD Workshop standalone"""
    app = QApplication(sys.argv)
    
    # Create standalone workshop (no main_window)
    workshop = TXDWorkshop(parent=None, main_window=None)
    workshop.show()
    
    # Check if file path provided as argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            if file_path.lower().endswith('.txd'):
                workshop.open_txd_file(file_path)
            elif file_path.lower().endswith('.img'):
                workshop.load_from_img_archive(file_path)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
