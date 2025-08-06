#this belongs in methods/populate_img_table.py - Version: 5
# X-Seti - July21 2025 - IMG Factory 1.5 - IMG Table Population Methods - FIXED
# FIXED: DummyMainWindow inherits from QWidget to fix QMenu parent issue

"""
IMG Table Population Methods
"""

import os
from typing import Optional, List
from PyQt6.QtWidgets import QTableWidgetItem, QWidget
from PyQt6.QtCore import Qt

# Import existing classes and functions - NO NEW FUNCTIONS
from components.img_debug_functions import img_debugger
from components.img_core_classes import IMGFile, IMGEntry
from core.rw_versions import get_rw_version_name

##Methods list -
# _populate_img_table
# clear_img_table
# create_img_table_item
# format_img_entry_size
# get_img_entry_type
# install_img_table_populator
# populate_img_table
# refresh_img_table
# update_img_table_selection_info

class IMGTablePopulator:
    """Handle IMG table population for IMG Factory - COMPLETE VERSION"""
    
    def __init__(self, main_window):
        self.main_window = main_window

    def _populate_img_table(self, img_file: IMGFile): #vers 5
        """Populate table with IMG file entries - MAIN FUNCTION - FIXED"""
        if not img_file or not img_file.entries:
            # Try different table access methods
            table = None
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                table = self.main_window.gui_layout.table
            elif hasattr(self.main_window, 'entries_table'):
                table = self.main_window.entries_table
            
            if table:
                table.setRowCount(0)
            return

        # Get table reference
        table = None
        if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
            table = self.main_window.gui_layout.table
        elif hasattr(self.main_window, 'entries_table'):
            table = self.main_window.entries_table
        else:
            img_debugger.error("No table found for IMG population")
            return

        # Configure table
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Offset", "Size", "Hex", "RW Version", "Status"
        ])

        # Set column widths
        table.setColumnWidth(0, 120)  # Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Offset
        table.setColumnWidth(3, 100)  # Size
        table.setColumnWidth(4, 100)  # Hex
        table.setColumnWidth(5, 120)  # RW Version
        table.setColumnWidth(6, 80)   # Status

        # Populate rows
        table.setRowCount(len(img_file.entries))
        
        for i, entry in enumerate(img_file.entries):
            try:
                # Name
                name_item = self.create_img_table_item(entry.name)
                table.setItem(i, 0, name_item)

                # Type 
                entry_type = self.get_img_entry_type(entry)
                type_item = self.create_img_table_item(entry_type)
                table.setItem(i, 1, type_item)

                # Offset
                offset_text = f"0x{entry.offset:08X}" if hasattr(entry, 'offset') else "N/A"
                offset_item = self.create_img_table_item(offset_text)
                table.setItem(i, 2, offset_item)

                # Size
                size_text = self.format_img_entry_size(entry)
                size_item = self.create_img_table_item(size_text)
                table.setItem(i, 3, size_item)
                table.setItem(i, 4, hex_item)
                # RW Version - Use entry's own version detection
                if hasattr(entry, 'rw_version_name') and entry.rw_version_name:
                    # Entry already has version detected
                    rw_item = self.create_img_table_item(entry.rw_version_name)
                elif hasattr(entry, 'rw_version') and entry.rw_version > 0:
                    # Entry has version number, get name
                    try:
                        version_name = get_rw_version_name(entry.rw_version)
                        rw_item = self.create_img_table_item(version_name)
                    except Exception as e:
                        rw_item = self.create_img_table_item("Unknown")
                        img_debugger.debug(f"RW version name lookup failed for {entry.name}: {e}")
                elif entry.size > 0 and entry.extension in ['dff', 'txd']:
                    # Try to detect RW version for RenderWare files
                    try:
                        entry.detect_rw_version()  # Trigger version detection
                        if hasattr(entry, 'rw_version_name') and entry.rw_version_name:
                            rw_item = self.create_img_table_item(entry.rw_version_name)
                        else:
                            rw_item = self.create_img_table_item("Unknown")
                    except Exception as e:
                        rw_item = self.create_img_table_item("Unknown")
                        img_debugger.debug(f"RW version detection failed for {entry.name}: {e}")
                else:
                    rw_item = self.create_img_table_item("N/A")
                table.setItem(i, 5, rw_item)

                # Status
                status_item = self.create_img_table_item("✅ Ready")
                table.setItem(i, 6, status_item)

            except Exception as e:
                img_debugger.error(f"Error populating row {i}: {e}")
                # Fill with error data
                table.setItem(i, 0, self.create_img_table_item(f"Entry_{i}"))
                table.setItem(i, 1, self.create_img_table_item("ERROR"))
                table.setItem(i, 2, self.create_img_table_item("N/A"))
                table.setItem(i, 3, self.create_img_table_item("0 bytes"))
                table.setItem(i, 4, self.create_img_table_item("TODO"))
                table.setItem(i, 5, self.create_img_table_item("Unknown"))
                table.setItem(i, 6, self.create_img_table_item("❌ Error"))

        # Update selection info
        self.update_img_table_selection_info()
        
        img_debugger.success(f"IMG table populated: {len(img_file.entries)} entries")

    def create_img_table_item(self, text: str) -> QTableWidgetItem: #vers 2
        """Create table item with standard formatting"""
        item = QTableWidgetItem(str(text))
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        return item

    def format_img_entry_size(self, entry: IMGEntry) -> str: #vers 2
        """Format entry size for display"""
        try:
            if hasattr(entry, 'size'):
                size = entry.size
                if size >= 1024 * 1024:
                    return f"{size / (1024 * 1024):.1f} MB"
                elif size >= 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size} bytes"
            return "Unknown"
        except:
            return "Unknown"

    def get_img_entry_type(self, entry: IMGEntry) -> str: #vers 2
        """Get entry type from name extension"""
        try:
            if hasattr(entry, 'name') and '.' in entry.name:
                return entry.name.split('.')[-1].upper()
            return "Unknown"
        except:
            return "Unknown"

    def update_img_table_selection_info(self): #vers 2
        """Update selection information display"""
        try:
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                table = self.main_window.gui_layout.table
                selected_items = table.selectedItems()
                
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Selection: {len(selected_items)} items")
                    
        except Exception as e:
            img_debugger.error(f"Error updating selection info: {e}")

    def clear_img_table(self): #vers 2
        """Clear IMG table data"""
        try:
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                table = self.main_window.gui_layout.table
                table.setRowCount(0)
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("🧹 IMG table cleared")
            else:
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("⚠️ No table to clear")
                    
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error clearing IMG table: {str(e)}")

    def refresh_img_table(self) -> bool: #vers 2
        """Refresh the IMG table with current data"""
        try:
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                self._populate_img_table(self.main_window.current_img)
                return True
            else:
                self.clear_img_table()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("⚠️ No IMG file loaded to refresh")
                return False
                
        except Exception as e:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"❌ Error refreshing IMG table: {str(e)}")
            return False

# Standalone function for backward compatibility with existing code
def populate_img_table(table, img_file: IMGFile): #vers 2
    """Standalone function - uses IMGTablePopulator for backward compatibility - FIXED"""
    try:
        # FIXED: Create dummy main window object that inherits from QWidget
        table.clear()
        table.setRowCount(0)
        class DummyMainWindow(QWidget):
            def __init__(self):
                super().__init__()  # Initialize QWidget
                self.gui_layout = type('obj', (object,), {'table': table})
                
            def log_message(self, message):
                print(f"[TABLE] {message}")
        
        dummy_window = DummyMainWindow()
        populator = IMGTablePopulator(dummy_window)
        populator._populate_img_table(img_file)
        
    except Exception as e:
        print(f"[ERROR] Error in standalone populate_img_table: {e}")
        # Clear table if population fails - works or doesn't work
        if table:
            table.setRowCount(0)

def install_img_table_populator(main_window): #vers 1
    """Install IMG table populator into main window"""
    try:
        # Create populator instance
        img_populator = IMGTablePopulator(main_window)
        
        # Add methods to main window
        main_window._populate_img_table = img_populator._populate_img_table
        main_window.create_img_table_item = img_populator.create_img_table_item
        main_window.format_img_entry_size = img_populator.format_img_entry_size
        main_window.get_img_entry_type = img_populator.get_img_entry_type
        main_window.update_img_table_selection_info = img_populator.update_img_table_selection_info
        main_window.clear_img_table = img_populator.clear_img_table
        main_window.refresh_img_table = img_populator.refresh_img_table
        
        # Store populator reference
        main_window.img_table_populator = img_populator
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG table populator installed")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error installing IMG table populator: {str(e)}")
        return False

# Export main classes and functions
__all__ = [
    'IMGTablePopulator',
    'populate_img_table',
    'install_img_table_populator'
]
