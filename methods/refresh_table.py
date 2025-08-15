#this belongs in methods/refresh_table.py - Version: 1
# X-Seti - Aug15 2025 - IMG Factory 1.5 - Refresh Table Function

"""
Refresh Table Function - Simple refresh functionality for IMG and COL tables
Refreshes the current table display when IMG or COL files are loaded
"""

##Methods list -
# refresh_table

def refresh_table(main_window): #vers 1
    """Refresh the current table - works for IMG or COL files"""
    try:
        # Check what type of file is currently loaded
        if hasattr(main_window, 'current_img') and main_window.current_img:
            # IMG file is loaded - refresh IMG table
            return _refresh_img_table(main_window)
        elif hasattr(main_window, 'current_col') and main_window.current_col:
            # COL file is loaded - refresh COL table
            return _refresh_col_table(main_window)
        else:
            # No file loaded - clear table
            return _clear_table(main_window)
            
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error refreshing table: {str(e)}")
        return False

def _refresh_img_table(main_window) -> bool: #vers 1
    """Refresh IMG table with current IMG data"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Refreshing IMG table...")
        
        # Method 1: Use existing refresh_img_table from populate_img_table
        try:
            from methods.populate_img_table import refresh_img_table
            success = refresh_img_table(main_window)
            if success:
                if hasattr(main_window, 'log_message'):
                    main_window.log_message("✅ IMG table refreshed")
                return True
        except ImportError:
            pass
        
        # Method 2: Use populate_entries_table if available
        if hasattr(main_window, 'populate_entries_table') and callable(main_window.populate_entries_table):
            main_window.populate_entries_table()
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ IMG table refreshed via populate_entries_table")
            return True
        
        # Method 3: Manual refresh using table and current_img
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            img_file = main_window.current_img
            
            if hasattr(img_file, 'entries'):
                from PyQt6.QtWidgets import QTableWidgetItem
                
                # Clear and set row count
                table.setRowCount(len(img_file.entries))
                
                # Populate rows
                for row, entry in enumerate(img_file.entries):
                    # Name column (0)
                    name_item = QTableWidgetItem(getattr(entry, 'name', f'entry_{row}'))
                    table.setItem(row, 0, name_item)
                    
                    # Type column (1)
                    name = getattr(entry, 'name', '')
                    file_ext = name.split('.')[-1].upper() if '.' in name else 'UNK'
                    type_item = QTableWidgetItem(file_ext)
                    table.setItem(row, 1, type_item)
                    
                    # Size column (2)
                    size = getattr(entry, 'size', 0)
                    size_text = f"{size:,} bytes" if size > 0 else "0 bytes"
                    size_item = QTableWidgetItem(size_text)
                    table.setItem(row, 2, size_item)
                    
                    # Offset column (3)
                    offset = getattr(entry, 'offset', 0)
                    offset_text = f"0x{offset:08X}" if offset > 0 else "0x00000000"
                    offset_item = QTableWidgetItem(offset_text)
                    table.setItem(row, 3, offset_item)
                
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ IMG table refreshed - {len(img_file.entries)} entries")
                return True
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("⚠️ Could not refresh IMG table - no available methods")
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error refreshing IMG table: {str(e)}")
        return False

def _refresh_col_table(main_window) -> bool: #vers 1
    """Refresh COL table with current COL data"""
    try:
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Refreshing COL table...")
        
        # Try to use COL table refresh methods
        if hasattr(main_window, 'refresh_col_table') and callable(main_window.refresh_col_table):
            main_window.refresh_col_table()
            if hasattr(main_window, 'log_message'):
                main_window.log_message("✅ COL table refreshed")
            return True
        
        # Basic COL table refresh if available
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            col_file = main_window.current_col
            
            if hasattr(col_file, 'models') or hasattr(col_file, 'entries'):
                from PyQt6.QtWidgets import QTableWidgetItem
                
                # Get COL data
                if hasattr(col_file, 'models'):
                    items = col_file.models
                    table.setRowCount(len(items))
                    
                    for row, model in enumerate(items):
                        # Name
                        name = getattr(model, 'name', f'model_{row}')
                        table.setItem(row, 0, QTableWidgetItem(name))
                        
                        # Type
                        table.setItem(row, 1, QTableWidgetItem('COL'))
                        
                        # Info
                        info = f"Spheres: {len(getattr(model, 'spheres', []))}, Boxes: {len(getattr(model, 'boxes', []))}"
                        table.setItem(row, 2, QTableWidgetItem(info))
                
                if hasattr(main_window, 'log_message'):
                    main_window.log_message(f"✅ COL table refreshed - {len(items)} models")
                return True
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("⚠️ Could not refresh COL table - no available methods")
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error refreshing COL table: {str(e)}")
        return False

def _clear_table(main_window) -> bool: #vers 1
    """Clear the table when no file is loaded"""
    try:
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            table = main_window.gui_layout.table
            table.setRowCount(0)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message("🗑️ Table cleared - no file loaded")
            return True
            
        return False
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error clearing table: {str(e)}")
        return False

def integrate_refresh_table(main_window): #vers 1
    """Integrate refresh table function into main window"""
    try:
        # Add refresh_table method to main window
        main_window.refresh_table = lambda: refresh_table(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("🔄 Refresh table function integrated")
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error integrating refresh table: {str(e)}")
        return False

__all__ = [
    'refresh_table',
    'integrate_refresh_table'
]