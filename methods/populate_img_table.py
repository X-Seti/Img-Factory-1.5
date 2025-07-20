#this belongs in methods/populate_img_table.py - Version: 4
# X-Seti - July20 2025 - IMG Factory 1.5 - IMG Table Population Methods
# FIXED: Uses ONLY existing functions from core/rw_versions.py - COMPLETE VERSION

"""
IMG Table Population Methods - COMPLETE FIXED VERSION
Contains all IMG-specific table population functions with RW version detection
Uses ONLY existing functions from core/rw_versions.py - NO fallback code
"""

import os
from typing import Optional, List
from PyQt6.QtWidgets import QTableWidgetItem
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

    def _populate_img_table(self, img_file: IMGFile): #vers 4
        """Populate table with IMG file entries - MAIN FUNCTION"""
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
        
        if not table:
            print("[ERROR] No table found for population")
            return

        entries = img_file.entries
        print(f"[DEBUG] Populating table with {len(entries)} entries")

        # Clear existing data (including sample entries)
        table.setRowCount(0)
        table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            try:
                # Name - should now be clean from fixed parsing
                clean_name = str(entry.name).strip() if hasattr(entry, 'name') else f"Entry_{row}"
                table.setItem(row, 0, self.create_img_table_item(clean_name))

                # Extension - Use the cleaned extension from detect_file_type_and_version
                if hasattr(entry, 'extension') and entry.extension:
                    extension = entry.extension
                else:
                    # Extract using existing logic
                    if '.' in clean_name:
                        extension = clean_name.split('.')[-1].upper()
                        extension = ''.join(c for c in extension if c.isalpha())
                    else:
                        extension = "NO_EXT"
                table.setItem(row, 1, self.create_img_table_item(extension))

                # Size - Use existing format function
                size_text = self.format_img_entry_size(entry.size) if hasattr(entry, 'size') else "0 B"
                table.setItem(row, 2, self.create_img_table_item(size_text))

                # Offset - Show as hex
                if hasattr(entry, 'offset') and entry.offset is not None:
                    offset_text = f"0x{int(entry.offset):X}"
                else:
                    offset_text = "0x0"
                table.setItem(row, 3, self.create_img_table_item(offset_text))

                # Version - USE ONLY EXISTING FUNCTIONS
                version_text = "Unknown"
                try:
                    # Method 1: Use existing get_version_text() from fixed IMGEntry
                    if hasattr(entry, 'get_version_text') and callable(entry.get_version_text):
                        version_text = entry.get_version_text()
                    else:
                        # Method 2: Use existing rw_version + get_rw_version_name() from core/
                        if hasattr(entry, 'extension') and entry.extension in ['DFF', 'TXD']:
                            if hasattr(entry, 'rw_version') and entry.rw_version > 0:
                                # USE EXISTING get_rw_version_name() function
                                version_name = get_rw_version_name(entry.rw_version)
                                version_text = f"RW {version_name}"
                        elif hasattr(entry, 'extension'):
                            if entry.extension == 'COL':
                                version_text = "COL"
                            elif entry.extension == 'IFP':
                                version_text = "IFP"
                            elif entry.extension == 'IPL':
                                version_text = "IPL"
                            elif entry.extension in ['WAV', 'MP3']:
                                version_text = "Audio"
                except Exception as e:
                    print(f"[WARNING] Error getting version for {entry.name}: {e}")
                
                table.setItem(row, 4, self.create_img_table_item(version_text))

                # Compression - use existing entry.compression_type
                compression_text = "None"
                if hasattr(entry, 'compression_type') and entry.compression_type:
                    if str(entry.compression_type).upper() != 'NONE':
                        compression_text = str(entry.compression_type)
                table.setItem(row, 5, self.create_img_table_item(compression_text))

                # Status - use existing entry flags
                status_text = "Ready"
                if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                    status_text = "New"
                elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                    status_text = "Modified"
                table.setItem(row, 6, self.create_img_table_item(status_text))

                # Make all items read-only
                for col in range(7):
                    item = table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            except Exception as e:
                print(f"[ERROR] Error populating row {row}: {e}")
                # Create minimal row
                table.setItem(row, 0, self.create_img_table_item(f"Entry_{row}"))
                table.setItem(row, 1, self.create_img_table_item("UNKNOWN"))
                table.setItem(row, 2, self.create_img_table_item("0 B"))
                table.setItem(row, 3, self.create_img_table_item("0x0"))
                table.setItem(row, 4, self.create_img_table_item("Unknown"))
                table.setItem(row, 5, self.create_img_table_item("None"))
                table.setItem(row, 6, self.create_img_table_item("Error"))

        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"📋 Table populated with {len(entries)} entries")
        print(f"[SUCCESS] Successfully populated table with {len(entries)} entries")

        from core.right_click_actions import setup_table_context_menu
        setup_table_context_menu(self.main_window)


    def create_img_table_item(self, text: str, data=None) -> QTableWidgetItem: #vers 2
        """Create standardized IMG table widget item"""
        item = QTableWidgetItem(str(text))
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        if data is not None:
            item.setData(Qt.ItemDataRole.UserRole, data)
        return item

    def format_img_entry_size(self, size_bytes: int) -> str: #vers 2
        """Format IMG entry size for display"""
        try:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024*1024:
                return f"{size_bytes/1024:.1f} KB"
            else:
                return f"{size_bytes/(1024*1024):.1f} MB"
        except (TypeError, ValueError):
            return "0 B"

    def get_img_entry_type(self, filename: str) -> str: #vers 2
        """Get IMG entry type from filename extension"""
        try:
            if '.' not in filename:
                return "Unknown"

            extension = filename.split('.')[-1].upper()

            # Common GTA file types
            type_mapping = {
                'DFF': 'Model',
                'TXD': 'Texture',
                'COL': 'Collision',
                'IFP': 'Animation',
                'WAV': 'Audio',
                'SCM': 'Script',
                'IPL': 'Placement',
                'IDE': 'Definition',
                'DAT': 'Data',
                'CFG': 'Config',
                'FXT': 'Text',
                'GXT': 'Text'
            }

            return type_mapping.get(extension, extension)

        except Exception:
            return "Unknown"

    def update_img_table_selection_info(self, selected_rows: List[int]) -> None: #vers 2
        """Update selection info for IMG table"""
        try:
            if not selected_rows:
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("No entries selected")
                return
            
            if len(selected_rows) == 1:
                # Single selection - show detailed info
                row = selected_rows[0]
                if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                    if row < len(self.main_window.current_img.entries):
                        entry = self.main_window.current_img.entries[row]
                        size_text = self.format_img_entry_size(entry.size)
                        if hasattr(self.main_window, 'log_message'):
                            self.main_window.log_message(f"Selected: {entry.name} ({size_text})")
            else:
                # Multiple selection - show count and total size
                total_size = 0
                if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                    for row in selected_rows:
                        if row < len(self.main_window.current_img.entries):
                            total_size += self.main_window.current_img.entries[row].size
                
                total_size_text = self.format_img_entry_size(total_size)
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(f"Selected: {len(selected_rows)} entries ({total_size_text})")
                
        except Exception as e:
            print(f"[ERROR] Error updating IMG selection info: {e}")

    def clear_img_table(self) -> None: #vers 2
        """Clear the IMG table"""
        try:
            table = None
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                table = self.main_window.gui_layout.table
            elif hasattr(self.main_window, 'entries_table'):
                table = self.main_window.entries_table
                
            if table:
                table.setRowCount(0)
                table.clearSelection()
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message("✅ IMG table cleared")
            
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
def populate_img_table(table, img_file: IMGFile): #vers 1
    """Standalone function - uses IMGTablePopulator for backward compatibility"""
    try:
        # Create dummy main window object for compatibility
        class DummyMainWindow:
            def __init__(self):
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
