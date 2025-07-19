#this belongs in methods/populate_img_table.py - Version: 3
# X-Seti - July19 2025 - IMG Factory 1.5 - IMG Table Population Methods
# REPLACES the existing messy file with 3 duplicate functions

"""
IMG Table Population Methods
Contains all IMG-specific table population functions moved from imgfactory.py
Uses IMG debug system throughout
"""

import os
from typing import Optional
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

# Import IMG debug system
from components.img_debug_functions import img_debugger
from components.img_core_classes import IMGFile, IMGEntry
#from gui.gui_layout import IMGFactoryGUILayout

##Methods list -
# populate_img_table
# create_img_table_item
# format_img_entry_size
# get_img_entry_type

class IMGTablePopulator:
    """Handle IMG table population for IMG Factory"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        

    def _populate_img_table(self, img_file: IMGFile):
        """Populate table with IMG file entries - display"""
        if not img_file or not img_file.entries:
            self.gui_layout.table.setRowCount(0)
            return

        table = self.gui_layout.table
        entries = img_file.entries

        # Clear existing data (including sample entries)
        table.setRowCount(0)
        table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            try:
                # Name - should now be clean from fixed parsing
                clean_name = str(entry.name).strip() if hasattr(entry, 'name') else f"Entry_{row}"
                table.setItem(row, 0, QTableWidgetItem(clean_name))

                # Extension - Use the cleaned extension from populate_entry_details
                if hasattr(entry, 'extension') and entry.extension:
                    extension = entry.extension
                else:
                    # Fallback extraction
                    if '.' in clean_name:
                        extension = clean_name.split('.')[-1].upper()
                        extension = ''.join(c for c in extension if c.isalpha())
                    else:
                        extension = "NO_EXT"
                table.setItem(row, 1, QTableWidgetItem(extension))

                # Size - Format properly
                try:
                    if hasattr(entry, 'size') and entry.size:
                        size_bytes = int(entry.size)
                        if size_bytes < 1024:
                            size_text = f"{size_bytes} B"
                        elif size_bytes < 1024 * 1024:
                            size_text = f"{size_bytes / 1024:.1f} KB"
                        else:
                            size_text = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_text = "0 B"
                except:
                    size_text = "Unknown"
                table.setItem(row, 2, QTableWidgetItem(size_text))

                # Hash/Offset - Show as hex
                try:
                    if hasattr(entry, 'offset') and entry.offset is not None:
                        offset_text = f"0x{int(entry.offset):X}"
                    else:
                        offset_text = "0x0"
                except:
                    offset_text = "0x0"
                table.setItem(row, 3, QTableWidgetItem(offset_text))

                # Version - FIXED: Use new method
                try:
                    if extension in ['DFF', 'TXD']:
                        version_text = self.get_entry_rw_version(entry, extension)
                    elif extension == 'COL':
                        version_text = "COL"
                    elif extension == 'IFP':
                        version_text = "IFP"
                    else:
                        version_text = "Unknown"
                except Exception as e:
                    print(f"🔍 DEBUG: Version detection error for {clean_name}: {e}")
                    version_text = "Unknown"

                table.setItem(row, 4, QTableWidgetItem(version_text))

                # Compression
                try:
                    if hasattr(entry, 'compression_type') and entry.compression_type:
                        if str(entry.compression_type).upper() != 'NONE':
                            compression_text = str(entry.compression_type)
                        else:
                            compression_text = "None"
                    else:
                        compression_text = "None"
                except:
                    compression_text = "None"
                table.setItem(row, 5, QTableWidgetItem(compression_text))

                # Status
                try:
                    if hasattr(entry, 'is_new_entry') and entry.is_new_entry:
                        status_text = "New"
                    elif hasattr(entry, 'is_replaced') and entry.is_replaced:
                        status_text = "Modified"
                    else:
                        status_text = "Ready"
                except:
                    status_text = "Ready"
                table.setItem(row, 6, QTableWidgetItem(status_text))

                # Make all items read-only
                for col in range(7):
                    item = table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            except Exception as e:
                self.log_message(f"❌ Error populating row {row}: {str(e)}")
                # Create minimal fallback row
                table.setItem(row, 0, QTableWidgetItem(f"Entry_{row}"))
                table.setItem(row, 1, QTableWidgetItem("UNKNOWN"))
                table.setItem(row, 2, QTableWidgetItem("0 B"))
                table.setItem(row, 3, QTableWidgetItem("0x0"))
                table.setItem(row, 4, QTableWidgetItem("Unknown"))
                table.setItem(row, 5, QTableWidgetItem("None"))
                table.setItem(row, 6, QTableWidgetItem("Error"))

        self.log_message(f"📋 Table populated with {len(entries)} entries (using RW version detection method)")


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

    def update_img_table_selection_info(self, selected_rows: list) -> None: #vers 2
        """Update selection info for IMG table"""
        try:
            if not selected_rows:
                self.main_window.log_message("No entries selected")
                return
            
            if len(selected_rows) == 1:
                # Single selection - show detailed info
                row = selected_rows[0]
                if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                    if row < len(self.main_window.current_img.entries):
                        entry = self.main_window.current_img.entries[row]
                        size_text = self.format_img_entry_size(entry.size)
                        self.main_window.log_message(f"Selected: {entry.name} ({size_text})")
            else:
                # Multiple selection - show count and total size
                total_size = 0
                if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                    for row in selected_rows:
                        if row < len(self.main_window.current_img.entries):
                            total_size += self.main_window.current_img.entries[row].size
                
                total_size_text = self.format_img_entry_size(total_size)
                self.main_window.log_message(f"Selected: {len(selected_rows)} entries ({total_size_text})")
                
        except Exception as e:
            if img_debugger.debug_enabled:
                img_debugger.error(f"Error updating IMG selection info: {e}")

    def clear_img_table(self) -> None: #vers 2
        """Clear the IMG table"""
        try:
            if hasattr(self.main_window, 'gui_layout') and hasattr(self.main_window.gui_layout, 'table'):
                table = self.main_window.gui_layout.table
                table.setRowCount(0)
                table.clearSelection()
                self.main_window.log_message("✅ IMG table cleared")
            
        except Exception as e:
            self.main_window.log_message(f"❌ Error clearing IMG table: {str(e)}")

    def refresh_img_table(self) -> bool: #vers 2
        """Refresh the IMG table with current data"""
        try:
            if hasattr(self.main_window, 'current_img') and self.main_window.current_img:
                return self._populate_img_table(self.main_window.current_img)
            else:
                self.clear_img_table()
                self.main_window.log_message("⚠️ No IMG file loaded to refresh")
                return False
                
        except Exception as e:
            self.main_window.log_message(f"❌ Error refreshing IMG table: {str(e)}")
            return False


def install_img_table_populator(main_window):
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
        
        main_window.log_message("✅ IMG table populator installed")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error installing IMG table populator: {str(e)}")
        return False


# Export main classes and functions
__all__ = [
    'IMGTablePopulator',
    'populate_img_table',
    'install_img_table_populator'
]
