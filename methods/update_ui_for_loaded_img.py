#this belongs in methods/update_ui_for_loaded_img.py - Version: 1
# X-Seti - August01 2025 - IMG Factory 1.5 - UI Update for Loaded IMG

"""
IMG Factory UI Update for Loaded IMG
Standalone method to update UI when IMG file is loaded - FIXED VERSION
"""

import os
from PyQt6.QtWidgets import QTableWidgetItem

##Methods list -
# update_ui_for_loaded_img

def update_ui_for_loaded_img(main_window): #vers 5
    """Update UI when IMG file is loaded - STANDALONE FIXED VERSION"""
    try:
        if not hasattr(main_window, 'current_img') or not main_window.current_img:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ update_ui_for_loaded_img called but no current_img")
            return False

        # Update window title
        file_name = os.path.basename(main_window.current_img.file_path)
        main_window.setWindowTitle(f"IMG Factory 1.5 - {file_name}")

        # Populate table with IMG entries using STANDALONE method
        if hasattr(main_window, 'gui_layout') and hasattr(main_window.gui_layout, 'table'):
            # Import and use the standalone function from methods/
            from methods.populate_img_table import populate_img_table

            # Setup IMG table structure first
            table = main_window.gui_layout.table
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

            # Clear table before populating (preserve headers)
            table.setRowCount(0)

            # Populate table
            populate_img_table(main_window.gui_layout.table, main_window.current_img)
            
            if hasattr(main_window, 'log_message'):
                main_window.log_message(f"📋 Table populated with {len(main_window.current_img.entries)} entries")
        else:
            if hasattr(main_window, 'log_message'):
                main_window.log_message("⚠️ GUI layout or table not available")

        # Update status - FIXED: Properly hide progress and update status
        if hasattr(main_window, 'gui_layout'):
            entry_count = len(main_window.current_img.entries) if main_window.current_img.entries else 0
            
            # CRITICAL: Hide progress bar completely - multiple methods
            if hasattr(main_window.gui_layout, 'hide_progress'):
                main_window.gui_layout.hide_progress()
            
            if hasattr(main_window.gui_layout, 'progress_bar'):
                main_window.gui_layout.progress_bar.setVisible(False)
                main_window.gui_layout.progress_bar.setValue(0)
            
            # Force table to be visible
            if hasattr(main_window.gui_layout, 'table'):
                main_window.gui_layout.table.setVisible(True)
                main_window.gui_layout.table.show()
            
            # Update IMG info if method exists
            if hasattr(main_window.gui_layout, 'update_img_info'):
                main_window.gui_layout.update_img_info(f"IMG: {file_name}")

        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ IMG UI updated successfully")
        
        return True

    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error updating UI for loaded IMG: {str(e)}")
        return False


def integrate_update_ui_for_loaded_img(main_window): #vers 1
    """Integrate the standalone update_ui_for_loaded_img method into main window"""
    try:
        # Add method to main window
        main_window._update_ui_for_loaded_img = lambda: update_ui_for_loaded_img(main_window)
        
        if hasattr(main_window, 'log_message'):
            main_window.log_message("✅ Standalone update_ui_for_loaded_img integrated")
        
        return True
        
    except Exception as e:
        if hasattr(main_window, 'log_message'):
            main_window.log_message(f"❌ Error integrating update_ui_for_loaded_img: {str(e)}")
        return False


__all__ = [
    'update_ui_for_loaded_img',
    'integrate_update_ui_for_loaded_img'
]