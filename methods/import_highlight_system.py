#this belongs in methods/import_highlight_system.py - Version: 1
# X-Seti - August07 2025 - IMG Factory 1.5 - Import File Highlighting System

"""
Import File Highlighting System - File Explorer Style
Highlights imported/replaced files with visual indicators and animations
"""

import time
from typing import List, Dict, Set
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QBrush, QFont

##Methods list -
# apply_import_highlighting
# clear_import_highlights
# create_highlighted_item
# highlight_imported_files
# integrate_import_highlighting
# refresh_table_with_highlights
# set_import_highlight_style
# track_imported_files

##Classes -
# ImportHighlightManager

class ImportHighlightManager: #vers 1
    """Manages highlighting of imported files in the table"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.imported_files: Set[str] = set()
        self.replaced_files: Set[str] = set()
        self.highlight_timer: QTimer = None
        self.highlight_duration = 10000  # 10 seconds
        
    def track_imported_file(self, filename: str, was_replaced: bool = False): #vers 1
        """Track a file that was imported"""
        if was_replaced:
            self.replaced_files.add(filename)
        else:
            self.imported_files.add(filename)
            
        # Start highlight timer
        self._start_highlight_timer()
        
    def track_multiple_files(self, filenames: List[str], replaced_files: List[str] = None): #vers 1
        """Track multiple imported files"""
        if replaced_files is None:
            replaced_files = []
            
        for filename in filenames:
            self.imported_files.add(filename)
            
        for filename in replaced_files:
            self.replaced_files.add(filename)
            
        self._start_highlight_timer()
        
    def _start_highlight_timer(self): #vers 1
        """Start timer to clear highlights after duration"""
        if self.highlight_timer:
            self.highlight_timer.stop()
            
        self.highlight_timer = QTimer()
        self.highlight_timer.timeout.connect(self.clear_highlights)
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.start(self.highlight_duration)
        
    def clear_highlights(self): #vers 1
        """Clear all import highlights"""
        self.imported_files.clear()
        self.replaced_files.clear()
        
        # Refresh table to remove highlights
        refresh_table_with_highlights(self.main_window)
        
    def is_file_highlighted(self, filename: str) -> tuple: #vers 1
        """Check if file should be highlighted and return (is_highlighted, is_replaced)"""
        is_imported = filename in self.imported_files
        is_replaced = filename in self.replaced_files
        return (is_imported or is_replaced, is_replaced)

def create_highlighted_item(text: str, highlight_type: str = "imported") -> QTableWidgetItem: #vers 1
    """Create table item with import highlighting"""
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

def apply_import_highlighting(table: QTableWidget, highlight_manager: ImportHighlightManager): #vers 1
    """Apply highlighting to existing table items"""
    try:
        for row in range(table.rowCount()):
            # Get filename from first column
            name_item = table.item(row, 0)
            if not name_item:
                continue
                
            filename = name_item.text()
            is_highlighted, is_replaced = highlight_manager.is_file_highlighted(filename)
            
            if is_highlighted:
                highlight_type = "replaced" if is_replaced else "imported"
                
                # Apply highlighting to all columns in this row
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        # Copy current text and recreate with highlighting
                        text = item.text()
                        highlighted_item = create_highlighted_item(text, highlight_type)
                        table.setItem(row, col, highlighted_item)
                        
    except Exception as e:
        print(f"Error applying import highlighting: {e}")

def refresh_table_with_highlights(main_window) -> bool: #vers 1
    """Refresh table and maintain import highlights"""
    try:
        # Get highlight manager
        highlight_manager = getattr(main_window, '_import_highlight_manager', None)
        if not highlight_manager:
            # Fallback to regular refresh
            return refresh_img_table_standard(main_window)
            
        # Get table
        table = None
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
        elif hasattr(main_window, 'entries_table'):
            table = main_window.entries_table
            
        if not table:
            return False
            
        # Standard table population first
        success = refresh_img_table_standard(main_window)
        
        if success:
            # Apply highlighting after population
            apply_import_highlighting(table, highlight_manager)
            
        return success
        
    except Exception as e:
        print(f"Error refreshing table with highlights: {e}")
        return False

def refresh_img_table_standard(main_window) -> bool: #vers 1
    """Standard IMG table refresh without highlights"""
    try:
        # Method 1: Use populate_entries_table if available
        if hasattr(main_window, 'populate_entries_table') and callable(main_window.populate_entries_table):
            main_window.populate_entries_table()
            return True
            
        # Method 2: Use IMG table manager
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'img_table_manager'):
            manager = main_window.gui_layout.img_table_manager
            if hasattr(manager, 'populate_img_table') and hasattr(main_window, 'current_img'):
                manager.populate_img_table(main_window.current_img)
                return True
                
        # Method 3: Manual table refresh
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            
            if hasattr(main_window, 'current_img') and main_window.current_img and hasattr(main_window.current_img, 'entries'):
                entries = main_window.current_img.entries
                
                # Clear and repopulate table
                table.setRowCount(len(entries))
                
                for row, entry in enumerate(entries):
                    from PyQt6.QtWidgets import QTableWidgetItem
                    
                    # Name column
                    name_item = QTableWidgetItem(entry.name)
                    table.setItem(row, 0, name_item)
                    
                    # Type column
                    file_ext = entry.name.split('.')[-1].upper() if '.' in entry.name else 'Unknown'
                    type_item = QTableWidgetItem(file_ext)
                    table.setItem(row, 1, type_item)
                    
                    # Offset column
                    offset_text = f"0x{getattr(entry, 'offset', 0):08X}" if hasattr(entry, 'offset') else "N/A"
                    offset_item = QTableWidgetItem(offset_text)
                    table.setItem(row, 2, offset_item)
                    
                    # Size column
                    size = getattr(entry, 'size', len(getattr(entry, 'data', b'')))
                    size_item = QTableWidgetItem(str(size))
                    table.setItem(row, 3, size_item)
                    
                    # Hex preview column (if exists)
                    if table.columnCount() > 4:
                        hex_preview = "..."
                        if hasattr(entry, 'data') and entry.data:
                            hex_bytes = entry.data[:8].hex().upper()
                            hex_preview = ' '.join(hex_bytes[i:i+2] for i in range(0, len(hex_bytes), 2))
                        hex_item = QTableWidgetItem(hex_preview)
                        table.setItem(row, 4, hex_item)
                    
                    # RW Version column (if exists)
                    if table.columnCount() > 5:
                        rw_version = getattr(entry, 'rw_version', 'Unknown')
                        rw_item = QTableWidgetItem(rw_version)
                        table.setItem(row, 5, rw_item)
                
                return True
                
        return False
        
    except Exception as e:
        print(f"Error in standard table refresh: {e}")
        return False

def highlight_imported_files(main_window, imported_filenames: List[str], replaced_filenames: List[str] = None): #vers 1
    """Highlight recently imported files in the table"""
    try:
        if replaced_filenames is None:
            replaced_filenames = []
            
        # Get or create highlight manager
        if not hasattr(main_window, '_import_highlight_manager'):
            main_window._import_highlight_manager = ImportHighlightManager(main_window)
            
        highlight_manager = main_window._import_highlight_manager
        
        # Track the imported files
        highlight_manager.track_multiple_files(imported_filenames, replaced_filenames)
        
        # Refresh table with highlights
        success = refresh_table_with_highlights(main_window)
        
        if success:
            # Log the highlighting
            total_highlighted = len(imported_filenames) + len(replaced_filenames)
            main_window.log_message(f"✨ Highlighted {total_highlighted} imported files (10s duration)")
            
            # Show status message
            if hasattr(main_window, 'statusBar'):
                status_msg = f"✨ {len(imported_filenames)} imported"
                if replaced_filenames:
                    status_msg += f", {len(replaced_filenames)} replaced"
                main_window.statusBar().showMessage(status_msg, 5000)
        
        return success
        
    except Exception as e:
        main_window.log_message(f"❌ Error highlighting imported files: {str(e)}")
        return False

def clear_import_highlights(main_window): #vers 1
    """Clear all import highlights"""
    try:
        if hasattr(main_window, '_import_highlight_manager'):
            main_window._import_highlight_manager.clear_highlights()
            
        main_window.log_message("🧹 Import highlights cleared")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error clearing highlights: {str(e)}")
        return False

def set_import_highlight_style(main_window, highlight_duration: int = 10000): #vers 1
    """Configure import highlighting settings"""
    try:
        if not hasattr(main_window, '_import_highlight_manager'):
            main_window._import_highlight_manager = ImportHighlightManager(main_window)
            
        main_window._import_highlight_manager.highlight_duration = highlight_duration
        
        main_window.log_message(f"⚙️ Import highlight duration set to {highlight_duration/1000}s")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Error setting highlight style: {str(e)}")
        return False

def track_imported_files(main_window, filenames: List[str], replaced_files: List[str] = None): #vers 1
    """Track imported files for highlighting (used by import functions)"""
    try:
        if not filenames:
            return False
            
        if replaced_files is None:
            replaced_files = []
            
        # Get or create highlight manager
        if not hasattr(main_window, '_import_highlight_manager'):
            main_window._import_highlight_manager = ImportHighlightManager(main_window)
            
        highlight_manager = main_window._import_highlight_manager
        highlight_manager.track_multiple_files(filenames, replaced_files)
        
        return True
        
    except Exception as e:
        print(f"Error tracking imported files: {e}")
        return False

def integrate_import_highlighting(main_window): #vers 1
    """Integrate import highlighting system into main window"""
    try:
        # Create highlight manager
        main_window._import_highlight_manager = ImportHighlightManager(main_window)
        
        # Add highlighting functions to main window
        main_window.highlight_imported_files = lambda files, replaced=None: highlight_imported_files(main_window, files, replaced)
        main_window.clear_import_highlights = lambda: clear_import_highlights(main_window)
        main_window.track_imported_files = lambda files, replaced=None: track_imported_files(main_window, files, replaced)
        main_window.set_import_highlight_style = lambda duration=10000: set_import_highlight_style(main_window, duration)
        
        # Override refresh function to include highlights
        main_window.refresh_table_with_highlights = lambda: refresh_table_with_highlights(main_window)
        
        main_window.log_message("✨ Import highlighting system integrated")
        return True
        
    except Exception as e:
        main_window.log_message(f"❌ Failed to integrate import highlighting: {str(e)}")
        return False

# Export functions
__all__ = [
    'ImportHighlightManager',
    'apply_import_highlighting',
    'clear_import_highlights', 
    'create_highlighted_item',
    'highlight_imported_files',
    'integrate_import_highlighting',
    'refresh_table_with_highlights',
    'set_import_highlight_style',
    'track_imported_files'
]