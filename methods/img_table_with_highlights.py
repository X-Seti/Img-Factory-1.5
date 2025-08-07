# This belongs in methods/img_table_with_highlights.py - Version: 6
# X-Seti - August07 2025 - IMG Factory 1.5 - Enhanced with Import Highlighting

"""
Enhanced IMG Table Population with Import Highlighting Support
Adds highlighting functionality to existing table population
"""

import os
from typing import Any, List
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt


def create_highlighted_img_table_item(text: str, highlight_type: str = None) -> Any: #vers 1
    """Create table item with optional import highlighting"""
    from PyQt6.QtWidgets import QTableWidgetItem
    from PyQt6.QtGui import QColor, QBrush, QFont
    
    item = QTableWidgetItem(text)
    
    if highlight_type == "imported":
        # Light green background for newly imported files
        item.setBackground(QBrush(QColor(200, 255, 200)))  # Light green
        item.setForeground(QBrush(QColor(0, 100, 0)))      # Dark green text
        
        # Make text bold
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        
        # Add tooltip
        item.setToolTip("📥 Recently imported file")
        
    elif highlight_type == "replaced":
        # Light yellow background for replaced files
        item.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
        item.setForeground(QBrush(QColor(150, 100, 0)))    # Dark orange text
        
        # Make text bold
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        
        # Add tooltip
        item.setToolTip("🔄 Recently replaced file")
        
    return item

def get_highlight_type_for_entry(main_window, entry_name: str) -> str: #vers 1
    """Check if entry should be highlighted"""
    try:
        if hasattr(main_window, '_import_highlight_manager'):
            highlight_manager = main_window._import_highlight_manager
            is_highlighted, is_replaced = highlight_manager.is_file_highlighted(entry_name)
            
            if is_highlighted:
                return "replaced" if is_replaced else "imported"
        
        return None
        
    except Exception:
        return None

# Enhanced IMGTablePopulator class - ADD THIS TO YOUR EXISTING CLASS
def populate_table_row_with_highlights(self, table, row: int, entry: Any): #vers 1
    """Enhanced populate_table_row with highlighting support"""
    try:
        # Check if this entry should be highlighted
        highlight_type = get_highlight_type_for_entry(self.main_window, entry.name)
        
        # Column 0: Name (with highlighting)
        if highlight_type:
            name_item = create_highlighted_img_table_item(entry.name, highlight_type)
        else:
            name_item = self.create_img_table_item(entry.name)
        table.setItem(row, 0, name_item)

        # Column 1: Type (with highlighting)
        entry_type = self.get_img_entry_type(entry)
        if highlight_type:
            type_item = create_highlighted_img_table_item(entry_type, highlight_type)
        else:
            type_item = self.create_img_table_item(entry_type)
        table.setItem(row, 1, type_item)

        # Column 2: Offset (with highlighting)
        offset_text = f"0x{entry.offset:08X}" if hasattr(entry, 'offset') else "N/A"
        if highlight_type:
            offset_item = create_highlighted_img_table_item(offset_text, highlight_type)
        else:
            offset_item = self.create_img_table_item(offset_text)
        table.setItem(row, 2, offset_item)

        # Column 3: Size (with highlighting)
        size_text = self.format_img_entry_size(entry)
        if highlight_type:
            size_item = create_highlighted_img_table_item(size_text, highlight_type)
        else:
            size_item = self.create_img_table_item(size_text)
        table.setItem(row, 3, size_item)

        # Column 4: Hex Preview (with highlighting)
        hex_preview = self.get_hex_preview(entry) if hasattr(self, 'get_hex_preview') else "..."
        if highlight_type:
            hex_item = create_highlighted_img_table_item(hex_preview, highlight_type)
        else:
            hex_item = self.create_img_table_item(hex_preview)
        table.setItem(row, 4, hex_item)

        # Column 5: RW Version (with highlighting)
        rw_version = self.get_rw_version_string(entry) if hasattr(self, 'get_rw_version_string') else "Unknown"
        if highlight_type:
            rw_item = create_highlighted_img_table_item(rw_version, highlight_type)
        else:
            rw_item = self.create_img_table_item(rw_version)
        table.setItem(row, 5, rw_item)

        # Column 6: Status (if exists, with highlighting)
        if table.columnCount() > 6:
            status = self.get_entry_status(entry) if hasattr(self, 'get_entry_status') else "OK"
            if highlight_type:
                status_item = create_highlighted_img_table_item(status, highlight_type)
            else:
                status_item = self.create_img_table_item(status)
            table.setItem(row, 6, status_item)

    except Exception as e:
        if hasattr(self.main_window, 'log_message'):
            self.main_window.log_message(f"Error populating highlighted row {row}: {str(e)}")
        else:
            print(f"Error populating highlighted row {row}: {str(e)}")

def populate_table_with_img_data_highlighted(self, img_file: Any) -> bool: #vers 1
    """Enhanced populate table with highlighting support"""
    try:
        if not img_file or not hasattr(img_file, 'entries'):
            img_debugger.error("Invalid IMG file for table population")
            return False

        # Get table reference
        table = self.get_table_reference()
        if not table:
            img_debugger.error("No table found for IMG population")
            return False

        # Configure table structure - same as before
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Offset", "Size", "Hex", "RW Version", "Status"
        ])

        # Set proper column widths
        table.setColumnWidth(0, 120)  # Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Offset
        table.setColumnWidth(3, 100)  # Size
        table.setColumnWidth(4, 100)  # Hex
        table.setColumnWidth(5, 120)  # RW Version
        table.setColumnWidth(6, 80)   # Status

        # Set row count
        table.setRowCount(len(img_file.entries))

        # Populate each row with highlighting support
        for i, entry in enumerate(img_file.entries):
            try:
                self.populate_table_row_with_highlights(table, i, entry)
            except Exception as e:
                img_debugger.error(f"Error populating highlighted row {i}: {str(e)}")
                # Fall back to standard population for this row
                if hasattr(self, 'populate_table_row'):
                    self.populate_table_row(table, i, entry)

        img_debugger.info(f"✅ IMG table populated with {len(img_file.entries)} entries (highlighting enabled)")
        return True

    except Exception as e:
        img_debugger.error(f"Enhanced IMG table population failed: {str(e)}")
        return False

# Integration function to add to your existing file
def integrate_highlighting_with_img_table(main_window): #vers 1
    """Integrate highlighting support with existing IMG table populator"""
    try:
        # Add enhanced methods to existing populator
        if hasattr(main_window, '_img_table_populator'):
            populator = main_window._img_table_populator
            
            # Add highlighting methods
            populator.populate_table_row_with_highlights = lambda table, row, entry: populate_table_row_with_highlights(populator, table, row, entry)
            populator.populate_table_with_img_data_highlighted = lambda img_file: populate_table_with_img_data_highlighted(populator, img_file)
            
            # Override the standard populate method to use highlighting
            populator.populate_table_with_img_data = populator.populate_table_with_img_data_highlighted
            
            main_window.log_message("✅ IMG table highlighting integrated")
            return True
        else:
            main_window.log_message("⚠️ IMG table populator not found")
            return False
            
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate table highlighting: {str(e)}")
        return False

# Add this to the end of your existing populate_img_table.py file
def enable_import_highlighting(main_window): #vers 1
    """Enable import highlighting for the IMG table - MAIN INTEGRATION FUNCTION"""
    try:
        # First create the highlighting system
        from methods.import_highlight_system import integrate_import_highlighting
        integrate_import_highlighting(main_window)
        
        # Then integrate with the table populator
        integrate_highlighting_with_img_table(main_window)
        
        main_window.log_message("✨ Import highlighting system fully enabled")
        return True
        
    except ImportError as e:
        main_window.log_message(f"⚠️ Import highlighting system not found: {str(e)}")
        main_window.log_message("💡 Create methods/import_highlight_system.py to enable highlighting")
        return False
    except Exception as e:
        main_window.log_message(f"❌ Failed to enable import highlighting: {str(e)}")
        return False
