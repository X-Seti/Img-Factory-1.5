#this belongs in components/Img_Factory/img_factory_file_operations.py - Version: 1
# X-Seti - Oct27 2025 - IMG Factory 1.5 - File Operations Methods

"""
File Operations Methods
Handles file opening, loading, progress tracking, and error handling
"""

from typing import Optional
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from apps.methods.svg_shared_icons import get_open_icon, get_img_file_icon, get_error_icon
from apps.methods.img_core_classes import IMGFile
from apps.methods.col_core_classes import COLFile

import os

##Methods list -
# _clean_on_img_loaded
# _load_img_file_in_new_tab
# _load_txd_file_in_new_tab
# _on_img_load_error
# _on_img_load_progress
# _update_ui_for_no_img
# integrate_unified_progress_system
# load_file_unified
# open_file_dialog
# open_img_file
# reload_table


def open_img_file(self): #vers 2
    """Open file dialog - FIXED: Call imported function correctly"""
    try:
        open_file_dialog(self)  # Call function with self parameter
    except Exception as e:
        self.log_message(f"Error opening file dialog: {str(e)}")

def open_file_dialog(self): #vers 1
    """Unified file dialog - imported from core"""
    from core.open_img import open_file_dialog
    return open_file_dialog(self)

def _clean_on_img_loaded(self, img_file: IMGFile): #vers 6
    """Handle IMG loading - USES ISOLATED FILE WINDOW"""
    try:
        # Store the loaded IMG file
        current_index = self.main_tab_widget.currentIndex()
        if current_index in self.open_files:
            self.open_files[current_index]['file_object'] = img_file

        # Set current IMG reference
        self.current_img = img_file
        # CRITICAL: Store file object in tab tracking for tab switching
        current_index = self.main_tab_widget.currentIndex()
        if current_index in self.open_files:
            self.open_files[current_index]['file_object'] = img_file
            self.log_message(f"IMG file object stored in tab {current_index}")

        # Use isolated file window update
        success = self.gui_layout.update_file_window_only(img_file)

        # Properly hide progress and ensure GUI visibility
        self.gui_layout.hide_progress_properly()

        if success:
            self.log_message(f"Loaded (isolated): {os.path.basename(img_file.file_path)} ({len(img_file.entries)} entries)")

    except Exception as e:
        self.log_message(f"Loading error: {str(e)}")


def reload_table(self): #vers 1
    """Reload current file - called by reload button"""
    return self.reload_current_file()


def load_file_unified(self, file_path: str): #vers 8
    """Unified file loader for IMG and COL files"""
    try:
        if not file_path or not os.path.exists(file_path):
            self.log_message("File not found")
            return False

        file_ext = file_path.lower().split('.')[-1]
        file_name = os.path.basename(file_path)

        if file_ext == 'img':
            self._load_img_file_in_new_tab(file_path)  # ← Starts threading
            return True  # ← Return immediately, let threading finish
            try:
                # Import IMG loading components directly
                from methods.img_core_classes import IMGFile
                from methods.populate_img_table import populate_img_table

                # Create IMG file object
                img_file = IMGFile(file_path)

                if not img_file.open():
                    self.log_message(f"Failed to open IMG file: {img_file.get_error()}")
                    return False

                # Set as current IMG file #hangs after second img added?
                #self.current_img = img_file

                # CRITICAL: Setup IMG table structure (6 columns)
                if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
                    table = self.gui_layout.table
                    # Reset to IMG structure
                    table.setColumnCount(6)
                    table.setHorizontalHeaderLabels([
                        "Name", "Type", "Size", "Offset", "RW Version", "Info"
                    ])
                    # Set IMG column widths
                    table.setColumnWidth(0, 200)  # Name
                    table.setColumnWidth(1, 80)   # Type
                    table.setColumnWidth(2, 100)  # Size
                    table.setColumnWidth(3, 100)  # Offset
                    table.setColumnWidth(4, 120)  # RW Version
                    table.setColumnWidth(5, 150)  # Info

                # Populate table with IMG data using proper method

                populate_img_table(table, img_file)

                # Update window title
                self.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

                # Update info panel/status
                entry_count = len(img_file.entries) if img_file.entries else 0
                file_size = os.path.getsize(file_path)

                self.log_message(f"IMG file loaded: {entry_count} entries")
                return True

            except Exception as img_error:
                self.log_message(f"Error loading IMG file: {str(img_error)}")
                return False

        elif file_ext == 'col':
            # COL file loading (unchanged - working correctly)
            if hasattr_open_txd_workshop(self, 'load_col_file_safely'):
                self.log_message(f"Loading COL file: {file_name}")
                success = self.load_col_file_safely(file_path)
                if success:
                    self.log_message("COL file loaded successfully")
                else:
                    self.log_message("Failed to load COL file")
                return success
            else:
                self.log_message("COL integration not available")
                return False

        else:
            self.log_message(f"Unsupported file type: {file_ext}")
            return False

    except Exception as e:
        self.log_message(f"Error loading file: {str(e)}")
        import traceback
        traceback.print_exc()  # Debug info
        return False


def _load_img_file_in_new_tab(self, file_path): #vers [your_version + 1]
    """Load IMG file in new tab"""
    try:
        import os
        self.log_message(f"Loading IMG in new tab: {os.path.basename(file_path)}")

        # Create new tab first
        #tab_index = self.create_tab(file_path, 'IMG', None)

        # Then load IMG using your existing thread loader
        if self.load_thread and self.load_thread.isRunning():
            return

        self.load_thread = IMGLoadThread(file_path)
        self.load_thread.progress_updated.connect(self._on_img_load_progress)
        self.load_thread.loading_finished.connect(self._on_img_loaded)
        self.load_thread.loading_error.connect(self._on_img_load_error)
        self.load_thread.start()

    except Exception as e:
        self.log_message(f"Error loading IMG in new tab: {str(e)}")


def _load_txd_file_in_new_tab(self, file_path): #vers 1
    """Load TXD file in new tab"""
    try:
        import os

        # Create new tab for TXD
        #tab_index = self.create_tab(file_path, 'TXD', None)

        # Update tab to show it's a TXD
        file_name = os.path.basename(file_path)[:-4]  # Remove .txd
        self.main_tab_widget.setTabText(tab_index, f"{file_name}") #TODO SVG icon

        # Open TXD Workshop for this file
        from components.Txd_Editor.txd_workshop import open_txd_workshop
        self.txd_workshop = open_txd_workshop(self, file_path)

        if workshop:
            self.log_message(f"TXD loaded in tab {tab_index}: {file_name}")

    except Exception as e:
        self.log_message(f"Error loading TXD in tab:_open_txd_workshop {str(e)}")

def _load_col_file_in_new_tab(self, file_path): #vers [your_version + 1]
    """Load COL file in new tab"""
    try:
        import os
        self.log_message(f"Loading COL in new tab: {os.path.basename(file_path)}")

        # Don't create tab here if load_col_file_safely creates one
        # Just call the loader directly
        if hasattr(self, 'load_col_file_safely'):
            self.load_col_file_safely(file_path)
        else:
            self.log_message("Error: No COL loading method found")

    except Exception as e:
        self.log_message(f"Error loading COL in new tab: {str(e)}")


def _open_txd_workshop(self, file_path=None): #vers 2
    """Open TXD Workshop - connects to tab switching"""
    from apps.components.Txd_Editor.txd_workshop import open_txd_workshop

    if not file_path:
        if hasattr(self, 'current_img') and self.current_img:
            file_path = self.current_img.file_path

    workshop = open_txd_workshop(self, file_path)

    if workshop:
        if not hasattr(self, 'txd_workshops'):
            self.txd_workshops = []

        self.txd_workshops.append(workshop)

        # Connect workshop to tab changes
        self.main_tab_widget.currentChanged.connect(
            lambda idx: self._update_workshop_on_tab_change(workshop, idx)
        )

        workshop.workshop_closed.connect(lambda: self._on_workshop_closed(workshop))
        self.log_message(f"Workshop opened and connected ({len(self.txd_workshops)} total)")

    return workshop


def _update_workshop_on_tab_change(self, workshop, tab_index): #vers 1
    """Update specific workshop when tab changes"""
    if not workshop or not workshop.isVisible():
        return

    tab_widget = self.main_tab_widget.widget(tab_index)
    if not tab_widget:
        return

    file_path = getattr(tab_widget, 'file_path', None)
    if file_path:
        if file_path.lower().endswith('.txd'):
            workshop.open_txd_file(file_path)
        elif file_path.lower().endswith('.img'):
            workshop.load_from_img_archive(file_path)

def _on_workshop_closed(self, workshop): #vers 1
    """Remove closed workshop from tracking list"""
    if hasattr(self, 'txd_workshops') and workshop in self.txd_workshops:
        self.txd_workshops.remove(workshop)
        self.log_message(f"Workshop closed ({len(self.txd_workshops)} remaining)")


def open_file_dialog(main_window): #vers 8
    """Unified file dialog for IMG, COL, and TXD files"""
    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Open Archive",
        "",
        "All Supported (*.img *.col *.txd);;IMG Archives (*.img);;COL Archives (*.col);;TXD Textures (*.txd);;All Files (*)"
    )

    if file_path:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.txd':
            load_txd_file(main_window, file_path)
        elif file_ext == '.col':
            # Create new tab for COL
            if hasattr(main_window, '_load_col_file_in_new_tab'):
                main_window._load_col_file_in_new_tab(file_path)
            else:
                main_window.load_col_file_safely(file_path)
        else:  # .img
            # Create new tab for IMG
            if hasattr(main_window, '_load_img_file_in_new_tab'):
                main_window._load_img_file_in_new_tab(file_path)
            else:
                main_window.load_img_file(file_path)


def _on_img_load_progress(self, progress: int, status: str): #vers 5
    """Handle IMG loading progress updates - UPDATED: Uses unified progress system"""
    try:
        from methods.progressbar_functions import update_progress
        update_progress(self, progress, status)
    except ImportError:
        # Fallback for systems without unified progress
        self.log_message(f"Progress: {progress}% - {status}")


def _update_ui_for_no_img(self): #vers 6
    """Update UI when no IMG file is loaded - UPDATED: Uses unified progress system"""
    # Clear current data
    self.current_img = None
    self.current_col = None
    self.current_txd = None

    # Update window title
    self.setWindowTitle("IMG Factory 1.5")

    # Clear table if it exists
    if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'table'):
        self.gui_layout.table.setRowCount(0)

    # Reset progress using unified system
    try:
        from methods.progressbar_functions import hide_progress
        hide_progress(self, "Ready")
    except ImportError:
        # Fallback for old systems
        if hasattr(self, 'gui_layout') and hasattr(self.gui_layout, 'show_progress'):
            self.gui_layout.show_progress(-1, "Ready")

    # Update file info
    if hasattr(self.gui_layout, 'update_img_info'):
        self.gui_layout.update_img_info("No IMG loaded")

    # Reset any status labels
    if hasattr(self, 'file_path_label'):
        self.file_path_label.setText("No file loaded")
    if hasattr(self, 'version_label'):
        self.version_label.setText("---")
    if hasattr(self, 'entry_count_label'):
        self.entry_count_label.setText("0")
    if hasattr(self, 'img_status_label'):
        self.img_status_label.setText("No IMG loaded")

    # Disable buttons that require an IMG to be loaded
    buttons_to_disable = [
        'close_img_btn', 'rebuild_btn', 'rebuild_as_btn', 'validate_btn',
        'import_btn', 'export_all_btn', 'export_selected_btn'
    ]

    for btn_name in buttons_to_disable:
        if hasattr(self.gui_layout, btn_name):
            button = getattr(self.gui_layout, btn_name)
            if hasattr(button, 'setEnabled'):
                button.setEnabled(False)

def _on_img_load_error(self, error_message: str): #vers 4
    """Handle IMG loading error - UPDATED: Uses unified progress system"""
    self.log_message(f" {error_message}")

    # Hide progress using unified system
    try:
        from methods.progressbar_functions import hide_progress
        hide_progress(self, "Load failed")
    except ImportError:
        # Fallback for old systems
        if hasattr(self.gui_layout, 'hide_progress'):
            self.gui_layout.hide_progress()

    QMessageBox.critical(self, "IMG Load Error", error_message)

# Add this to __init__ method after GUI creation:
def integrate_unified_progress_system(self): #vers 1
    """Integrate unified progress system - call in __init__"""
    try:
        from methods.progressbar_functions import integrate_progress_system
        integrate_progress_system(self)
        self.log_message("Unified progress system integrated")
    except ImportError:
        self.log_message("Unified progress system not available - using fallback")
    except Exception as e:
        self.log_message(f"Progress system integration failed: {str(e)}")


__all__ = [
    'open_img_file',
    'open_file_dialog',
    '_clean_on_img_loaded',
    'reload_table',
    'load_file_unified',
    '_load_img_file_in_new_tab',
    '_load_col_file_in_new_tab',
    '_load_txd_file_in_new_tab',
    '_open_txd_workshop',
    '_update_workshop_on_tab_change',
    '_on_workshop_closed',
    'open_file_dialog',
    '_on_img_load_progress',
    '_update_ui_for_no_img',
    '_on_img_load_error',
    'integrate_unified_progress_system'

]
