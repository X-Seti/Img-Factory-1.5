#this belongs in methods/populate_img_table.py - Version: 8
# X-Seti - October15 2025 - IMG Factory 1.5

"""
IMG Table Population - MINIMAL VERSION
Shows basic entry info without heavy RW version detection to prevent freezing
UPDATED: Clean column resize modes with multiple examples
"""

import os
from typing import Any, List, Optional
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView
from PyQt6.QtCore import Qt

from debug.img_debug_functions import img_debugger

try:
    from utils.img_debug_logger import img_debugger
except ImportError:
    class DummyDebugger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    img_debugger = DummyDebugger()

##Methods list - imported from tables_structure
# reset_table_styling
# setup_table_for_img_data
# setup_table_structure

##Methods list -
# create_img_table_item
# format_img_entry_size
# get_img_entry_type
# populate_table_row_minimal
# populate_table_with_img_data_minimal
# refresh_img_table
# update_img_table_selection_info

def reset_table_styling(main_window): #vers 1
    """Completely reset table styling to default using IMG debug system"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.warning("No table widget available for styling reset")
            return False

        table = main_window.gui_layout.table
        header = table.horizontalHeader()

        # Clear all styling
        table.setStyleSheet("")
        header.setStyleSheet("")
        table.setObjectName("")

        # Reset to basic alternating colors
        table.setAlternatingRowColors(True)

        # Reset selection behavior
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        # Reset header properties
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSectionsMovable(False)

        main_window.log_message("🔧 Table styling completely reset")
        img_debugger.debug("Table styling reset to default")
        return True

    except Exception as e:
        error_msg = f"Error resetting table styling: {str(e)}"
        main_window.log_message(f"⚠️ {error_msg}")
        img_debugger.error(error_msg)
        return False

def setup_table_structure(main_window, file_type: str = "IMG"): #vers 1
    """Setup table structure based on file type using IMG debug system"""
    try:
        if not hasattr(main_window, 'gui_layout') or not hasattr(main_window.gui_layout, 'table'):
            img_debugger.error("No table widget available for structure setup")
            return False

        table = main_window.gui_layout.table

        if file_type.upper() == "COL":
            return setup_table_for_col_data(table)
        else:
            return setup_table_for_img_data(table)

    except Exception as e:
        img_debugger.error(f"Error setting up table structure: {e}")
        return False

def setup_table_for_img_data(table: QTableWidget) -> bool: #vers 2
    """Setup table structure for IMG file data"""
    try:
        # IMG file columns
        img_headers = ["Name", "Type", "Size", "Offset", "RW Address", "RW Version", "Compression", "Status"]
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(img_headers)

        # Set initial column widths
        table.setColumnWidth(0, 190)  # Name
        table.setColumnWidth(1, 60)   # Type
        table.setColumnWidth(2, 90)   # Size
        table.setColumnWidth(3, 100)  # Offset
        table.setColumnWidth(4, 100)  # RW Address
        table.setColumnWidth(5, 100)  # RW Version
        table.setColumnWidth(6, 110)  # Compression
        table.setColumnWidth(7, 110)  # Status

        # Configure header - ACTIVE MODE (uncomment one option)
        header = table.horizontalHeader()
        header.setSectionsMovable(True)

        # OPTION 1: Name column stretches, others manual (CURRENTLY ACTIVE)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name stretches
        for col in range(1, 8):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        # OPTION 2: All columns proportional (equal resize)
        # for col in range(8):
        #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        # header.setStretchLastSection(True)

        # OPTION 3: Multiple stretch columns
        # header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        # header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        # header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        # header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        # header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        # header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        # header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Compression
        # header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Status

        # OPTION 4: Fixed columns (no resizing allowed)
        # for col in range(8):
        #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

        # OPTION 5: Resize to contents (auto-fit data)
        # for col in range(8):
        #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        # OPTION 6: Force all columns visible (prevent horizontal scroll)
        # table.horizontalHeader().setStretchLastSection(False)
        # for col in range(7):  # All except last
        #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        # header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        # Enable sorting
        table.setSortingEnabled(True)

        img_debugger.debug("Table structure setup for IMG data")
        return True

    except Exception as e:
        img_debugger.error(f"Error setting up IMG table structure: {e}")
        return False

class IMGTablePopulator:
    """Handles IMG table population with minimal processing to prevent freezing"""

    def __init__(self, main_window):
        self.main_window = main_window

    def populate_table_with_img_data(self, img_file: Any) -> bool: #vers 8
        """Populate table with IMG entry data - MINIMAL VERSION to prevent freezing"""
        try:
            if not img_file or not hasattr(img_file, 'entries'):
                img_debugger.error("Invalid IMG file for table population")
                return False

            # Get table reference
            table = self.get_table_reference()
            if not table:
                img_debugger.error("No table found for IMG population")
                return False

            # Keep original 8-column structure
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([
                "Name", "Type", "Size", "Offset", "RW Address", "RW Version", "Compression", "Status"
            ])

            # Set initial column widths
            table.setColumnWidth(0, 190)  # Name
            table.setColumnWidth(1, 60)   # Type
            table.setColumnWidth(2, 90)   # Size
            table.setColumnWidth(3, 100)  # Offset
            table.setColumnWidth(4, 100)  # RW Address
            table.setColumnWidth(5, 100)  # RW Version
            table.setColumnWidth(6, 110)  # Compression
            table.setColumnWidth(7, 110)  # Status

            # Configure header - ACTIVE MODE (uncomment one option)
            header = table.horizontalHeader()
            header.setSectionsMovable(True)

            # OPTION 1: Name column stretches, others manual (CURRENTLY ACTIVE)
            #header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name stretches
            #for col in range(1, 8):
            #    header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

            # OPTION 2: All columns equal proportional resize
            # for col in range(8):
            #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            # header.setStretchLastSection(True)

            # OPTION 3: First and last columns stretch
            # header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
            # for col in range(1, 7):
            #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            # header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Status

            # OPTION 4: Force all columns always visible (no horizontal scroll)
            header.setStretchLastSection(False)
            for col in range(8):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

            # OPTION 5: Fit to contents (auto-adjust to data)
            # for col in range(8):
            #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

            # OPTION 6: Fixed size columns (no manual resize)
            # for col in range(8):
            #     header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

            entries = img_file.entries
            if not entries:
                img_debugger.info("No entries found in IMG file")
                return True

            # Set row count once
            table.setRowCount(len(entries))
            img_debugger.debug(f"Populating table with {len(entries)} entries")

            # Populate table rows with minimal processing
            for row, entry in enumerate(entries):
                self.populate_table_row_minimal(table, row, entry)

            img_debugger.info(f"✅ Table populated with {len(entries)} entries")
            return True

        except Exception as e:
            img_debugger.error(f"Error populating IMG table: {str(e)}")
            return False


    def populate_table_row_minimal(self, table: Any, row: int, entry: Any): #vers 1
        """Populate single table row with MINIMAL processing - keep all 8 columns"""
        try:
            # Column 0: Name - just the filename, no processing
            name_text = str(entry.name) if hasattr(entry, 'name') else f"Entry_{row}"
            name_item = self.create_img_table_item(name_text)
            table.setItem(row, 0, name_item)

            # Column 1: Type - simple extension extraction
            entry_type = self.get_img_entry_type_simple(entry)
            type_item = self.create_img_table_item(entry_type)
            table.setItem(row, 1, type_item)

            # Column 2: Size - simple formatting
            size_text = self.format_img_entry_size_simple(entry)
            size_item = self.create_img_table_item(size_text)
            table.setItem(row, 2, size_item)

            # Column 3: Offset - simple hex formatting
            offset_text = f"0x{entry.offset:08X}" if hasattr(entry, 'offset') else "N/A"
            offset_item = self.create_img_table_item(offset_text)
            table.setItem(row, 3, offset_item)

            # Column 4: RW Address - LIGHT processing, no file reading
            rw_address_text = self.get_rw_address_light(entry)
            rw_address_item = self.create_img_table_item(rw_address_text)
            table.setItem(row, 4, rw_address_item)

            # Column 5: RW Version - LIGHT processing, no file reading
            version_text = self.get_rw_version_light(entry)
            version_item = self.create_img_table_item(version_text)
            table.setItem(row, 5, version_item)

            # Column 6: compression_type
            info_text = self.get_compression_info(entry)
            info_item = self.create_img_table_item(info_text)
            table.setItem(row, 6, info_item)

            # Column 7: Status - get_info
            status_text = self.get_info_light(entry)
            status_item = self.create_img_table_item(status_text)
            table.setItem(row, 7, status_item)

        except Exception as e:
            img_debugger.error(f"Error populating table row {row}: {str(e)}")
            # Set basic error info
            table.setItem(row, 0, self.create_img_table_item(f"Error_{row}"))

    def get_img_entry_type_simple(self, entry: Any) -> str: #vers 1
        """Get entry type - SIMPLE extension extraction, no heavy processing"""
        try:
            if hasattr(entry, 'name') and '.' in entry.name:
                return entry.name.split('.')[-1].upper()
            else:
                return "UNKNOWN"
        except Exception:
            return "UNKNOWN"

    def format_img_entry_size_simple(self, entry: Any) -> str: #vers 1
        """Format entry size - SIMPLE formatting, no processing"""
        try:
            if hasattr(entry, 'size') and entry.size > 0:
                size = entry.size
            elif hasattr(entry, 'actual_size') and entry.actual_size > 0:
                size = entry.actual_size
            else:
                return "0 B"

            # Simple size formatting
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size/(1024*1024):.1f} MB"
            else:
                return f"{size/(1024*1024*1024):.1f} GB"
        except Exception:
            return "0 B"

    def get_rw_address_light(self, entry: Any) -> str: #vers 1
        """Get RW address - LIGHT processing, no file reading"""
        try:
            # Check if RW version already cached
            if hasattr(entry, 'rw_version') and entry.rw_version > 0:
                return f"0x{entry.rw_version:08X}"
            else:
                # Don't read file, just show placeholder
                entry_type = self.get_img_entry_type_simple(entry)
                if entry_type in ['DFF', 'TXD']:
                    return "RW File"
                else:
                    return "N/A"
        except Exception:
            return "N/A"

    def get_rw_version_light(self, entry: Any) -> str: #vers 1
        """Get RW version - LIGHT processing, no file reading"""
        try:
            # Check if version already cached
            if hasattr(entry, 'rw_version_name') and entry.rw_version_name:
                if entry.rw_version_name not in ["Unknown", "", "N/A"]:
                    return entry.rw_version_name

            # Don't read file, just show basic info
            entry_type = self.get_img_entry_type_simple(entry)
            if entry_type in ['DFF', 'TXD']:
                return "RW File"
            elif entry_type == 'COL':
                return "COL File"
            elif entry_type in ['IPL', 'IDE', 'DAT']:
                return f"{entry_type} File"
            else:
                return "Unknown"
        except Exception:
            return "Unknown"

    def get_compression_info(self, entry: Any) -> str: #vers 1
        """Get compression info only"""
        try:
            if hasattr(entry, 'compression_type') and entry.compression_type:
                if str(entry.compression_type).upper() != 'NONE':
                    return str(entry.compression_type)
            return "None"
        except Exception:
            return "None"

    def get_status_info(self, entry: Any) -> str: #vers 1
        """Get status info only"""
        try:
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                return "Imported"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                return "Replaced"
            else:
                return "Original"
        except Exception:
            return "Original"

    def get_info_light(self, entry: Any) -> str: #vers 1
        """Get entry info - LIGHT processing, no heavy detection"""
        try:
            info_parts = []

            # Basic status info only - no compression detection
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                info_parts.append("Imported")
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                info_parts.append("Replaced")
            else:
                info_parts.append("Original")

            # Add file type info
            entry_type = self.get_img_entry_type_simple(entry)
            if entry_type in ['DFF']:
                info_parts.append("Model")
            elif entry_type in ['TXD']:
                info_parts.append("Texture")
            elif entry_type in ['COL']:
                info_parts.append("Collision")

            return " • ".join(info_parts) if info_parts else "Original"

        except Exception:
            return "Original"

    def get_version_simple(self, entry: Any) -> str: #vers 1
        """Get version info - SIMPLE, no file reading or heavy processing"""
        try:
            # Check if version already detected and cached
            if hasattr(entry, 'rw_version_name') and entry.rw_version_name:
                if entry.rw_version_name not in ["Unknown", "", "N/A"]:
                    return entry.rw_version_name

            # For non-RW files, just show file type
            entry_type = self.get_img_entry_type_simple(entry)
            if entry_type in ['COL', 'IPL', 'IDE', 'DAT', 'WAV', 'SCM']:
                return f"{entry_type} File"
            elif entry_type in ['DFF', 'TXD']:
                return "RW File"  # Don't try to detect version
            else:
                return "Unknown"
        except Exception:
            return "Unknown"

    def get_status_simple(self, entry: Any) -> str: #vers 1
        """Get entry status - SIMPLE, no processing"""
        try:
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                return "New"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                return "Modified"
            else:
                return "Original"
        except Exception:
            return "Original"

    def create_img_table_item(self, text: str) -> QTableWidgetItem: #vers 1
        """Create table item - SIMPLE"""
        try:
            item = QTableWidgetItem(str(text))
            return item
        except Exception:
            return QTableWidgetItem("Error")

    def get_table_reference(self): #vers 1
        """Get table reference from main window"""
        try:
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                return self.main_window.gui_layout.table
            elif hasattr(self.main_window, 'table'):
                return self.main_window.table
            else:
                img_debugger.error("No table found in main window")
                return None
        except Exception as e:
            img_debugger.error(f"Error getting table reference: {str(e)}")
            return None

# Standalone functions for compatibility
def populate_img_table(table, img_file) -> bool: #vers 2
    """Standalone function for IMG table population - MINIMAL VERSION"""
    try:
        # Create dummy window for populator
        class DummyWindow:
            def __init__(self, table):
                self.gui_layout = type('obj', (object,), {'table': table})

        dummy_window = DummyWindow(table)
        populator = IMGTablePopulator(dummy_window)
        return populator.populate_table_with_img_data(img_file)

    except Exception as e:
        img_debugger.error(f"Error in standalone populate_img_table: {e}")
        if table:
            table.setRowCount(0)
        return False

def clear_img_table(main_window) -> bool: #vers 1
    """Clear IMG table contents"""
    try:
        populator = IMGTablePopulator(main_window)
        table = populator.get_table_reference()

        if table:
            table.setRowCount(0)
            table.clearContents()
            return True
        else:
            return False

    except Exception as e:
        img_debugger.error(f"Error clearing IMG table: {str(e)}")
        return False

def refresh_img_table(main_window) -> bool: #vers 1
    """Refresh the IMG table with current data"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            populator = IMGTablePopulator(main_window)
            return populator.populate_table_with_img_data(main_window.current_img)
        else:
            clear_img_table(main_window)
            return False

    except Exception as e:
        img_debugger.error(f"Error refreshing IMG table: {str(e)}")
        return False

def install_img_table_populator(main_window): #vers 1
    """Install IMG table populator into main window"""
    try:
        # Install methods into main window
        main_window.populate_img_table = lambda img_file: populate_img_table(
            main_window.gui_layout.table if hasattr(main_window, 'gui_layout') else None,
            img_file
        )
        main_window.clear_img_table = lambda: clear_img_table(main_window)
        main_window.refresh_img_table = lambda: refresh_img_table(main_window)

        img_debugger.info("✅ Minimal IMG table populator installed")
        return True

    except Exception as e:
        img_debugger.error(f"Error installing IMG table populator: {str(e)}")
        return False

def update_img_table_selection_info(main_window) -> bool: #vers 1
    """Update selection info for IMG table"""
    try:
        populator = IMGTablePopulator(main_window)
        table = populator.get_table_reference()

        if not table:
            return False

        selected_rows = len(table.selectionModel().selectedRows())
        total_rows = table.rowCount()

        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"Selected {selected_rows} of {total_rows} entries")

        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error updating selection info: {str(e)}")
        return False

# Export functions
__all__ = [
    'IMGTablePopulator',
    'populate_img_table',
    'refresh_img_table',
    'clear_img_table',
    'install_img_table_populator',
    'update_img_table_selection_info'
]
