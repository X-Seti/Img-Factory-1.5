# this belongs in methods/populate_img_table.py - Version: 5
# X-Seti - August07 2025 - IMG Factory 1.5 - Updated IMG Table Population with RW Hex Column

"""
IMG Table Population
"""

import os
from typing import Any, List
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

try:
    from utils.img_debug_logger import img_debugger
except ImportError:
    class DummyDebugger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    img_debugger = DummyDebugger()

##Methods list -
# create_img_table_item
# format_img_entry_size
# get_hex_preview
# get_img_entry_type
# get_rw_version_hex
# get_rw_version_string
# populate_table_row
# populate_table_with_img_data
# refresh_img_table
# update_img_table_selection_info

class IMGTablePopulator:
    """Handles IMG table population with proper column structure"""
    
    def __init__(self, main_window):
        self.main_window = main_window

    def populate_table_with_img_data(self, img_file: Any) -> bool: #vers 5
        """Populate table with IMG entry data - UPDATED with RW Hex column"""
        try:
            if not img_file or not hasattr(img_file, 'entries'):
                img_debugger.error("Invalid IMG file for table population")
                return False

            # Get table reference
            table = self.get_table_reference()
            if not table:
                img_debugger.error("No table found for IMG population")
                return False

            # Configure table structure - UPDATED: 7 columns including RW Hex
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([
                "Name", "Type", "Size", "Offset", "RW Address", "RW Version", "Info", "Status"
            ])

            # Set proper column widths - UPDATED for RW Hex column
            table.setColumnWidth(0, 190)  # Name
            table.setColumnWidth(1, 60)   # Type
            table.setColumnWidth(2, 90)  # Size
            table.setColumnWidth(3, 100)  # Offset
            table.setColumnWidth(5, 100)  # RW Version
            table.setColumnWidth(4, 100)  # RW Hex - NEW COLUMN
            table.setColumnWidth(6, 110)  # Info
            table.setColumnWidth(7, 110)   # Status
            #TODO - add resizing on columns, file window span to fill 100% window.

            # Enable proper selection, sorting, and column resizing
            from PyQt6.QtWidgets import QHeaderView, QAbstractItemView
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSortingEnabled(True)
            
            # Enable column resizing
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(False)
            header.setSectionsMovable(True)
            
            # Set row count
            table.setRowCount(len(img_file.entries))

            img_debugger.debug(f"Populating table with {len(img_file.entries)} entries")

            # Populate all rows
            for i, entry in enumerate(img_file.entries):
                try:
                    self.populate_table_row(table, i, entry)
                except Exception as e:
                    img_debugger.error(f"Error populating row {i}: {str(e)}")
                    # Continue with other rows

            img_debugger.info(f"✅ IMG table populated with {len(img_file.entries)} entries")
            return True

        except Exception as e:
            img_debugger.error(f"IMG table population failed: {str(e)}")
            return False

    def populate_table_row(self, table, row: int, entry: Any): #vers 5
        """Populate a single table row with entry data - UPDATED with RW Hex"""
        try:
            # Column 0: Name
            name_item = self.create_img_table_item(entry.name)
            table.setItem(row, 0, name_item)

            # Column 1: Type 
            entry_type = self.get_img_entry_type(entry)
            type_item = self.create_img_table_item(entry_type)
            table.setItem(row, 1, type_item)

            # Column 2: Size
            size_text = self.format_img_entry_size(entry)
            size_item = self.create_img_table_item(size_text)
            table.setItem(row, 2, size_item)

            # Column 3: Offset
            offset_text = f"0x{entry.offset:08X}" if hasattr(entry, 'offset') else "N/A"
            offset_item = self.create_img_table_item(offset_text)
            table.setItem(row, 3, offset_item)

            # Column 4: RW Version
            rw_version = self.get_rw_version_string(entry)
            version_item = self.create_img_table_item(rw_version)
            table.setItem(row, 5, version_item)

            # Column 5: RW Hex - NEW COLUMN
            rw_hex = self.get_rw_version_hex(entry)
            hex_item = self.create_img_table_item(rw_hex)
            table.setItem(row, 4, hex_item)

            # Column 6: Info
            info_text = self.get_entry_info(entry)
            info_item = self.create_img_table_item(info_text)
            table.setItem(row, 6, info_item)

            # Column 7: Status
            status_text = self.get_entry_status(entry)
            table.setItem(row, 7, self.create_img_table_item(status_text))

        except Exception as e:
            img_debugger.error(f"Error populating table row {row}: {str(e)}")

    def get_entry_status(self, entry: Any) -> str: #vers 1
        """Get entry status for Status column"""
        try:
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                return "Imported"
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                return "Replaced"
            else:
                return "Original"
        except Exception:
            return "Original"


    def get_table_reference(self):
        """Get table widget reference"""
        try:
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                return self.main_window.gui_layout.table
            elif hasattr(self.main_window, 'table'):
                return self.main_window.table
            else:
                return None
        except Exception:
            return None

    def create_img_table_item(self, text: str) -> QTableWidgetItem: #vers 1
        """Create table item with proper formatting"""
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
        return item

    def format_img_entry_size(self, entry: Any) -> str: #vers 1
        """Format entry size in human readable format"""
        try:
            if not hasattr(entry, 'size'):
                return "N/A"
            
            size = entry.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except Exception:
            return "N/A"

    def get_img_entry_type(self, entry: Any) -> str: #vers 1
        """Get entry file type"""
        try:
            if hasattr(entry, 'extension') and entry.extension:
                return entry.extension.upper()
            elif hasattr(entry, 'name') and '.' in entry.name:
                return entry.name.split('.')[-1].upper()
            else:
                return "Unknown"
        except Exception:
            return "Unknown"

    def get_rw_version_string(self, entry: Any) -> str: #vers 1
        """Get RW version string"""
        try:
            if hasattr(entry, 'rw_version_name') and entry.rw_version_name:
                if entry.rw_version_name in ["Unknown", ""]:
                    return "N/A"
                return entry.rw_version_name
            elif hasattr(entry, 'rw_version') and entry.rw_version > 0:
                # Fallback version lookup
                version_map = {
                    0x1003FFFF: "3.1.0.1",
                    0x1803FFFF: "3.6.0.3", 
                    0x34003: "3.4.0.3",
                    0x35000: "3.5.0.0",
                    0x35002: "3.5.0.2"
                }
                return version_map.get(entry.rw_version, f"0x{entry.rw_version:X}")
            else:
                return "N/A"
        except Exception:
            return "N/A"

    def get_rw_version_hex(self, entry: Any) -> str: #vers 1
        """Get RW version hex value - NEW METHOD"""
        try:
            if hasattr(entry, 'rw_version') and entry.rw_version > 0:
                return f"0x{entry.rw_version:08X}"
            else:
                return "N/A"
        except Exception:
            return "N/A"

    def get_entry_info(self, entry: Any) -> str: #vers 3
        """Get entry info string - FIXED redundancy and compression types"""
        try:
            info_parts = []

            # DON'T add file type here - it's already shown in the Type column
            # File type info - REMOVED to avoid redundancy

            # Status info
            if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                info_parts.append("Imported")
            elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                info_parts.append("Replaced")

            # Compression info - Enhanced
            if hasattr(entry, 'compression_type') and hasattr(entry.compression_type, 'value'):
                if entry.compression_type.value > 1:  # Actually compressed
                    # Try to detect compression type
                    comp_type = "zlib"  # Default assumption for RW files
                    if hasattr(entry, 'compression_method'):
                        comp_type = entry.compression_method
                    info_parts.append(f"Compressed ({comp_type})")
                else:
                    # Not compressed
                    info_parts.append("Uncompressed")
            else:
                # No compression info available
                info_parts.append("Uncompressed")

            return " • ".join(info_parts) if info_parts else "Uncompressed"

        except Exception:
            return "Uncompressed"

    def get_hex_preview(self, entry: Any) -> str: #vers 1
        """Get hex preview of entry data - PRESERVED for compatibility"""
        try:
            if hasattr(entry, '_cached_data') and entry._cached_data:
                data = entry._cached_data[:8]  # First 8 bytes
            elif hasattr(entry, 'get_data'):
                try:
                    data = entry.get_data()[:8]
                except Exception:
                    return "..."
            else:
                return "..."
            
            if data:
                hex_str = ' '.join([f'{b:02X}' for b in data])
                return hex_str
            else:
                return "..."
        except Exception:
            return "..."

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

def install_img_table_populator(main_window) -> bool: #vers 1
    """Install IMG table populator methods into main window"""
    try:
        # Create populator instance
        img_populator = IMGTablePopulator(main_window)
        
        # Add methods to main window for backward compatibility
        main_window.populate_table_with_img_data = img_populator.populate_table_with_img_data
        main_window.create_img_table_item = img_populator.create_img_table_item
        main_window.format_img_entry_size = img_populator.format_img_entry_size
        main_window.get_img_entry_type = img_populator.get_img_entry_type
        main_window.get_hex_preview = img_populator.get_hex_preview
        main_window.get_rw_version_hex = img_populator.get_rw_version_hex
        main_window.get_rw_version_string = img_populator.get_rw_version_string

        
        # Store populator reference
        main_window.img_table_populator = img_populator
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG table populator with RW Hex column installed")
        else:
            print("✅ IMG table populator with RW Hex column installed")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error installing IMG table populator: {str(e)}")
        else:
            print(f"❌ Error installing IMG table populator: {str(e)}")
        return False

def populate_img_table(table, img_file: Any) -> bool: #vers 5
    """Standalone function for backward compatibility"""
    try:
        from PyQt6.QtWidgets import QWidget
        
        # Create dummy main window for standalone usage
        class DummyMainWindow(QWidget):
            def __init__(self):
                super().__init__()
                self.gui_layout = type('obj', (object,), {'table': table})
                
            def log_message(self, message):
                print(f"[TABLE] {message}")
        
        dummy_window = DummyMainWindow()
        populator = IMGTablePopulator(dummy_window)
        return populator.populate_table_with_img_data(img_file)
        
    except Exception as e:
        print(f"[ERROR] Error in standalone populate_img_table: {e}")
        if table:
            table.setRowCount(0)
        return False

def refresh_img_table(main_window) -> bool: #vers 6
    """Refresh the IMG table with current data - PRESERVED FUNCTION"""
    try:
        if hasattr(main_window, 'current_img') and main_window.current_img:
            populator = IMGTablePopulator(main_window)
            return populator.populate_table_with_img_data(main_window.current_img)
        else:
            clear_img_table(main_window)
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ No IMG file loaded to refresh")
            return False
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error refreshing IMG table: {str(e)}")
        return False

def update_img_table_selection_info(main_window) -> bool: #vers 6
    """Update selection info for IMG table - PRESERVED FUNCTION"""
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
